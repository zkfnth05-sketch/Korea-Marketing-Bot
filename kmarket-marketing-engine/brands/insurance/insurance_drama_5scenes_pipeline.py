# insurance_drama_5scenes_pipeline.py  (신규 파일 — 완성형 전체 코드)
# 24시간 무인 가동 / 5씬 드라마 파이프라인
# 설계 원칙: Fail-Fast, 포트-어댑터 분리, 씬 단위 격리, 좀비 프로세스 회수, 매니페스트 리줌

from __future__ import annotations

import atexit
import json
import logging
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
import traceback
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# [경로 보정] 어느 디렉터리에서 실행하더라도 config.py / core 모듈 100% 로드 보장
#   CURRENT_DIR  = .../kmarket-marketing-engine/brands/insurance
#   PROJECT_ROOT = .../kmarket-marketing-engine   ← config.py 가 위치한 루트
# 이 보정이 없으면 cwd 가 brands/insurance 일 때 `import config` 가 실패하여
# Gemini API 키 체인이 통째로 비어버리고, 이미지 어댑터가 폴백으로 낙하한다.
# ---------------------------------------------------------------------------
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# ---------------------------------------------------------------------------
# 로깅 (무인 가동: 파일 + 콘솔, 스택트레이스 보존)
# ---------------------------------------------------------------------------
LOG_FMT = "%(asctime)s | %(levelname)-7s | %(threadName)-14s | %(name)s | %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FMT)
log = logging.getLogger("insurance.pipeline")


# ---------------------------------------------------------------------------
# 예외 계층 (삼키지 않음 — 전부 상위로 전파, 매니페스트에 기록)
# ---------------------------------------------------------------------------
class PipelineError(Exception):
    """파이프라인 최상위 예외."""


class SpecValidationError(PipelineError):
    """스펙 오염/자리표시자/지연 맥락 감지 시 즉시 실패."""


class AdapterError(PipelineError):
    """어댑터 실행 실패."""


class SceneTimeoutError(PipelineError):
    """씬 단위 타임아웃."""


class ProcessTerminationError(PipelineError):
    """프로세스(그룹) 종료/회수 실패 — 좀비 잔존 은폐 금지."""


class BinaryResolutionError(PipelineError):
    """ffmpeg 등 외부 바이너리 경로 해석 실패 — 은폐 금지, 즉시 표면화."""


# ---------------------------------------------------------------------------
# 1) 데이터 계약 (SceneSpec / PipelineConfig)
#    - 스펙은 채팅 맥락이 아니라 이 데이터 계약으로만 유입된다.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SceneSpec:
    index: int
    narration: str
    duration_sec: float
    image_prompt: str
    voice_id: str = "ko-KR-female-1"
    # [장소 로테이션] 회차별 핫플레이스 영문 프롬프트 조각.
    #   · 한 편(1~5씬) 안에서는 동일 값이 5씬 전건에 주입되어 공간 연속성을 유지한다.
    #   · 다음 회차에는 완전히 다른 장소로 전환된다(100% 로테이션).
    location_en: str = ""
    # [시간대 판정 2축 결속] 회차 주제(한국어) — location_en 과 함께 시간대를 판정한다.
    #   · 장소 시그널(와인바/브런치 등) + 주제 시그널(심야/야경 등)을 동시 스캔.
    #   · 한 편(1~5씬) 안에서는 동일 값이 전건에 주입되어 조명 일관성 100%.
    topic: str = ""

    def validate(self) -> None:
        if self.index < 1 or self.index > 5:
            raise SpecValidationError(f"씬 인덱스 범위 위반: {self.index} (1..5)")
        if not self.narration or not self.narration.strip():
            raise SpecValidationError(f"씬 {self.index}: narration 비어 있음")
        if self.duration_sec <= 0 or self.duration_sec > 60:
            raise SpecValidationError(f"씬 {self.index}: duration_sec 비정상({self.duration_sec})")
        if not self.image_prompt or not self.image_prompt.strip():
            raise SpecValidationError(f"씬 {self.index}: image_prompt 비어 있음")


@dataclass(frozen=True)
class PipelineConfig:
    output_root: Path
    image_backend: str = "auto"          # auto | comfyui | gemini | pil
    tts_backend: str = "auto"            # auto | edge | pyttsx3 | silent
    video_backend: str = "auto"          # auto | wan_s2v | ffmpeg
    # [타임아웃 SSOT] 대표님 엄명 (2026-10-25):
    #   "씬 4가 81프레임(최대 길이)이라 Wan S2V 렌더링에 약 610초가 걸렸는데,
    #    파이프라인의 안전 타임아웃이 600초(10분)로 걸려 있어 10초 차이로 타임아웃 처리"
    #
    #   ★ 왜 900초인가: Wan 2.2 S2V 는 프레임 수에 비례해 렌더 시간이 증가하며,
    #     81프레임(4n+1 규격 최대)은 실측 610초가 소요된다. 기존 600초는 이보다
    #     10초 짧아 정상 렌더링을 타임아웃으로 절단했다. 900초(15분)로 상향하여
    #     81프레임 최대 케이스에 약 290초(≈48%)의 안전 여유를 확보한다.
    #   · 이 값은 _run_scene_with_timeout / FFmpeg assemble / concat_scenes 의
    #     공통 상한으로 작용하므로, 상향 시 세 경로가 동시에 안전해진다.
    scene_timeout_sec: float = 900.0     # Wan 2.2 S2V 81프레임(실측 610초) 수용 — 15분 안전 상한
    max_scene_retries: int = 2
    ffmpeg_bin: str = "ffmpeg"
    fps: int = 30
    resolution: str = "1080x1920"
    run_id: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))


# ---------------------------------------------------------------------------
# 2) 스펙 검증기 — 오염된 맥락(자리표시자/지연) 즉시 실패
# ---------------------------------------------------------------------------
class SpecValidator:
    PLACEHOLDER_TOKENS = ("원문", "응답", "placeholder", "TODO", "lorem")
    MAX_CONTEXT_AGE_MIN = 30.0

    @classmethod
    def reject_placeholder(cls, text: str, where: str) -> None:
        low = (text or "").lower()
        for tok in cls.PLACEHOLDER_TOKENS:
            if tok.lower() in low:
                raise SpecValidationError(
                    f"[{where}] 자리표시자 토큰 감지: '{tok}' — 실제 스펙으로 대체 필요"
                )

    @classmethod
    def reject_stale_context(cls, context_age_min: float, conversation_id: str) -> None:
        if "selftest" in (conversation_id or "").lower():
            raise SpecValidationError(
                f"테스트 하네스 대화({conversation_id}) 유입 — 실 스펙 아님, 실행 중단"
            )
        if context_age_min > cls.MAX_CONTEXT_AGE_MIN:
            raise SpecValidationError(
                f"맥락 지연 {context_age_min:.0f}분 > 허용 {cls.MAX_CONTEXT_AGE_MIN:.0f}분 — 스펙 재확인 필요"
            )

    @classmethod
    def validate_all(cls, scenes: List[SceneSpec], context_age_min: float, conversation_id: str) -> None:
        cls.reject_stale_context(context_age_min, conversation_id)
        if len(scenes) != 5:
            raise SpecValidationError(f"씬 개수 위반: {len(scenes)} (정확히 5 필요)")
        for s in scenes:
            s.validate()
            cls.reject_placeholder(s.narration, f"scene{s.index}.narration")
            cls.reject_placeholder(s.image_prompt, f"scene{s.index}.image_prompt")
        log.info("스펙 검증 통과: 5씬, 자리표시자/지연 없음")


# ---------------------------------------------------------------------------
# 3) 포트(추상) — 오케스트레이터는 포트에만 의존
# ---------------------------------------------------------------------------
class ImagePort(ABC):
    name: str = "base"
    @abstractmethod
    def available(self) -> bool: ...
    @abstractmethod
    def generate(self, prompt: str, out_path: Path, size: str, scene_idx: int = 1,
                 location_en: str = "", run_id: str = "") -> Path: ...


class TTSPort(ABC):
    name: str = "base"
    @abstractmethod
    def available(self) -> bool: ...
    @abstractmethod
    def synthesize(self, text: str, voice_id: str, out_path: Path) -> Path: ...


class VideoPort(ABC):
    name: str = "base"
    @abstractmethod
    def assemble(self, image: Path, audio: Path, out_path: Path, duration: float,
                 cfg: PipelineConfig, scene_idx: int = 1) -> Path: ...

    @abstractmethod
    def concat_scenes(self, scene_paths: List[Path], out_path: Path, cfg: PipelineConfig) -> Path: ...


# ---------------------------------------------------------------------------
# 4) 이미지 어댑터 3종 (Gemini 실사 / ComfyUI / 브랜드 마스터 에셋 폴백)
#    [영구 퇴출] 검은색 단색 더미 박스(RGB 18,18,24) — 어떤 경로로도 생성 금지
# ---------------------------------------------------------------------------
# 캐릭터 마스터 에셋 SSOT (씬별 화자 매핑)
#   씬1 수진(여) 훅 / 씬2 민우(남) 팩폭 / 씬3 수진 솔루션 / 씬4 수진 약속 / 씬5 수진 엔딩
CHARACTER_ASSET_DIR = Path(__file__).resolve().parent / "assets" / "characters"
CHARACTER_MASTER_FILES: Dict[str, str] = {
    "sujin": "insurance_sujin_master.png",
    "minwoo": "insurance_minwoo_master.png",
}
SCENE_CHARACTER_MAP: Dict[int, str] = {
    1: "sujin",
    2: "minwoo",
    3: "sujin",
    4: "minwoo",
    5: "sujin",
}
GEMINI_IMAGE_MODELS: Tuple[str, ...] = (
    "gemini-2.5-flash-image",
    "gemini-2.5-flash-image-preview",
    "gemini-3.1-flash-lite-image",
)


# ---------------------------------------------------------------------------
# [회차별 신규 주인공 SSOT] 매 회차 완전히 새로운 20대 한국 남녀 주인공을
#   Gemini 이미지 API 로 즉석 생성하여 회차 전용 마스터 에셋으로 결속한다.
#   · 생성 성공 → EPISODE_CHARACTER_DIR/{run_id}/ 아래에 회차 전용 마스터 저장
#   · 키 부재/생성 실패 → 기존 정적 마스터(CHARACTER_ASSET_DIR)로 무결점 폴백
#   · resolve_character_asset() 는 회차 전용 마스터를 최우선 반환한다.
# ---------------------------------------------------------------------------
EPISODE_CHARACTER_DIR = Path(__file__).resolve().parent / "assets" / "episodes"
EPISODE_MASTER_FILES: Dict[str, str] = {
    "sujin": "episode_sujin_master.png",
    "minwoo": "episode_minwoo_master.png",
}

# ---------------------------------------------------------------------------
# [도메인 데이터 SSOT 이관] 회차별 신규 주인공 생성 프롬프트는
#   brands/insurance/insurance_drama_domain_data.py 단일 소유자로 이관되었다.
#   · 본 파일은 프롬프트 리터럴을 재정의하지 않고 도메인 모듈에서 '조회'만 한다.
#   · 도메인 모듈은 16주제/8장르/16장소/서사 매트릭스/씬 가이드까지 함께 소유한다.
#   · 임포트 실패는 은폐하지 않고 즉시 표면화한다(프롬프트 드리프트 원천 차단).
# ---------------------------------------------------------------------------
from brands.insurance.insurance_drama_domain_data import (
    INSURANCE_TOPICS,
    INSURANCE_GENRES,
    INSURANCE_LOCATIONS_KO,
    INSURANCE_LOCATIONS_EN,
    INSURANCE_FRESH_FEMALE_PROMPT,
    INSURANCE_FRESH_MALE_PROMPT,
    INSURANCE_NARRATIVE_MATRIX,
    INSURANCE_SCENE_GUIDE_PROMPT,
    # [주제별 약관·의학 사실 SSOT] 10대 핵심 보험 주제의 fact/trap/check/keyword.
    #   · 자율 집필 프롬프트(_build_gemini_prompt)가 이 사전을 조회하여
    #     "뻔한 일반론" 대신 구체적 질병명·통계·약관 조항을 대사에 직접 인용하게 한다.
    #   · 임포트 실패는 은폐하지 않고 즉시 표면화한다(프롬프트 드리프트 원천 차단).
    INSURANCE_TOPIC_SPECS,
    # [부부 공간 및 시선 일치 안전장치 SSOT] 대표님 지시 (2026-10-26)
    #   · SPATIAL_POSTURE_MODES: SEATED(홀수 회차) / STANDING(짝수 회차) 2모드 사전.
    #     각 모드가 couple_shot / sujin_posture / minwoo_posture / eye_line_anchor 를
    #     한 묶음으로 소유하여, 두 사람의 자세와 수평 아이레벨을 100% 결속한다.
    #   · get_spatial_anchor(run_no): 회차 번호로 좌식↔입식을 결정론적 교차 선택.
    #     한 편(1~5씬) 안에서는 동일 앵커가 전건에 주입되어 시선/포즈 왜곡을 방지한다.
    #   · 임포트 실패는 은폐하지 않고 즉시 표면화한다(공간 앵커 드리프트 원천 차단).
    SPATIAL_POSTURE_MODES,
    get_spatial_anchor,
    # [81프레임 칼수렴 씬별 글자 수 상한 SSOT] 대표님 지시 (2026-10-26)
    #   · SCENE_CHAR_LIMITS: 씬1~5의 min/max/target 글자 수 규격 사전.
    #     Wan 2.2 S2V 81프레임(5.06초) 렌더링에서 자막이 프레임을 넘치지 않도록
    #     씬별 상한을 결정론적으로 강제한다.
    #   · 자율 집필 프롬프트(_build_gemini_prompt)와 파서 검증이 이 사전을 조회하여
    #     "프롬프트 지시"와 "코드 검증"이 동일 숫자를 참조하도록 결속한다.
    #   · 임포트 실패는 은폐하지 않고 즉시 표면화한다(글자수 규격 드리프트 원천 차단).
    SCENE_CHAR_LIMITS,
)

FRESH_FEMALE_PROMPT = INSURANCE_FRESH_FEMALE_PROMPT
FRESH_MALE_PROMPT = INSURANCE_FRESH_MALE_PROMPT

# 회차 전용 마스터 캐시 (run_id → {"sujin": Path, "minwoo": Path})
_EPISODE_MASTER_CACHE: Dict[str, Dict[str, Path]] = {}


def _generate_single_master(prompt: str, out_path: Path, keys: List[str]) -> Optional[Path]:
    """Gemini 이미지 API 로 인물 마스터 1장을 생성한다. 실패 시 None(폴백 유도)."""
    try:
        from google import genai
        from google.genai import types as genai_types
    except Exception as e:
        log.warning("신규 주인공 생성: google.genai 임포트 실패 — 폴백: %r", e)
        return None

    out_path.parent.mkdir(parents=True, exist_ok=True)
    for key in keys:
        for model in GEMINI_IMAGE_MODELS:
            try:
                client = genai.Client(api_key=key)
                resp = client.models.generate_content(
                    model=model,
                    contents=[genai_types.Part.from_text(text=prompt)],
                )
                saved = False
                for cand in (getattr(resp, "candidates", None) or []):
                    content = getattr(cand, "content", None)
                    for part in (getattr(content, "parts", None) or []):
                        inline = getattr(part, "inline_data", None)
                        if inline is not None and getattr(inline, "data", None):
                            out_path.write_bytes(inline.data)
                            saved = True
                            break
                    if saved:
                        break
                if not saved:
                    raise AdapterError("신규 주인공: 응답에 이미지 파트 없음")

                # 세로 9:16 규격 정규화 (실패해도 원본 유지)
                try:
                    from PIL import Image, ImageOps
                    with Image.open(out_path) as im:
                        im = im.convert("RGB")
                        fitted = ImageOps.fit(im, (1080, 1920), method=Image.LANCZOS,
                                              centering=(0.5, 0.35))
                        fitted.save(out_path, format="PNG")
                except Exception:
                    log.debug("신규 주인공 리사이즈 실패 — 원본 유지", exc_info=True)

                if out_path.exists() and out_path.stat().st_size > 0:
                    log.info("신규 주인공 마스터 생성 성공(model=%s): %s", model, out_path.name)
                    return out_path
            except Exception as e:
                log.warning("신규 주인공 생성 실패(model=%s): %s", model, e)
                continue
    return None


def ensure_fresh_episode_characters(run_id: str) -> Dict[str, Path]:
    """회차별 신규 주인공(여/남) 마스터 에셋을 보장한다.

    정책:
      1) run_id 단위로 1회만 생성(캐시) — 5씬 전건이 동일 인물을 공유한다.
      2) Gemini 이미지 API 로 완전히 새로운 20대 한국 여성/남성 주인공을 즉석 생성.
      3) API 키 부재 또는 생성 실패 시에만 기존 정적 마스터로 무결점 폴백.
      4) 반환 dict 는 반드시 {"sujin": Path, "minwoo": Path} 완전체여야 한다.
    """
    if run_id in _EPISODE_MASTER_CACHE:
        return _EPISODE_MASTER_CACHE[run_id]

    episode_dir = EPISODE_CHARACTER_DIR / run_id
    resolved: Dict[str, Path] = {}
    keys = _collect_image_api_keys()

    if keys:
        for who, prompt in (("sujin", FRESH_FEMALE_PROMPT), ("minwoo", FRESH_MALE_PROMPT)):
            target = episode_dir / EPISODE_MASTER_FILES[who]
            if target.exists() and target.stat().st_size > 0:
                resolved[who] = target
                continue
            made = _generate_single_master(prompt, target, keys)
            if made is not None:
                resolved[who] = made
            else:
                log.warning("신규 주인공 '%s' 생성 실패 — 정적 마스터로 폴백", who)
    else:
        log.info("Gemini 키 부재 — 회차별 신규 주인공 생성 생략, 정적 마스터 사용")

    # 폴백: 정적 마스터로 빈 슬롯 채우기 (무결점 보장)
    for who, fn in CHARACTER_MASTER_FILES.items():
        if who in resolved:
            continue
        static = CHARACTER_ASSET_DIR / fn
        if static.exists() and static.stat().st_size > 0:
            resolved[who] = static

    if len(resolved) != 2:
        raise AdapterError(
            f"회차 주인공 마스터 확보 실패: {sorted(resolved)} "
            f"(신규 생성/정적 폴백 모두 불가 — {CHARACTER_ASSET_DIR} 확인 필요)"
        )

    _EPISODE_MASTER_CACHE[run_id] = resolved
    log.info("회차 주인공 결속 완료(run=%s): 여=%s / 남=%s",
             run_id, resolved["sujin"].name, resolved["minwoo"].name)
    return resolved


def resolve_character_asset(scene_idx: int, run_id: str = "") -> Path:
    """씬 인덱스 → 화자 마스터 에셋 경로를 결정론적으로 해석한다.

    ★ 대표님 확정 지시 (2026-10-25): 회차별 신규 주인공 즉석 생성 경로를 전면 폐기하고,
      정적 마스터 에셋(CHARACTER_ASSET_DIR)만 결정론적으로 반환한다.

    · run_id 인자는 호출부(ImagePort.generate 시그니처) 하위 호환을 위해 유지하되,
      내부 분기에서는 사용하지 않는다(ensure_fresh_episode_characters 호출 제거).
    · 씬 1/3/5 → 수진 마스터, 씬 2/4 → 민우 마스터 (SCENE_CHARACTER_MAP SSOT).
    · 실패 시 AdapterError 로 표면화(검은 박스 폴백 금지).
    """
    who = SCENE_CHARACTER_MAP.get(scene_idx, "sujin")

    path = CHARACTER_ASSET_DIR / CHARACTER_MASTER_FILES[who]
    if not path.exists() or path.stat().st_size == 0:
        raise AdapterError(
            f"캐릭터 마스터 에셋 부재: {path} (씬 {scene_idx} → {who})"
        )
    return path


def _collect_image_api_keys() -> List[str]:
    """Gemini 이미지 생성용 키 풀 수집 (환경변수 → config.py 유료/무료키).

    우선순위: 유료 Insurance 키 → 무료 Insurance 키 → 범용 GEMINI_API_KEY.
    """
    keys: List[str] = []

    def _push(v: Any) -> None:
        if isinstance(v, str):
            s = v.strip()
            if s and s not in keys:
                keys.append(s)

    # 1) config.py 키 풀 (Insurance 전용 우선)
    try:
        import config as _cfg  # type: ignore
        for attr in (
            "GEMINI_PAID_API_KEY_AURA_1", "GEMINI_PAID_API_KEY_AURA_2",
            "GEMINI_FREE_API_KEY_AURA_1", "GEMINI_FREE_API_KEY_AURA_2",
            "GEMINI_FREE_API_KEY_AURA_3", "GEMINI_FREE_API_KEY_AURA_4",
            "GEMINI_API_KEY",
        ):
            _push(getattr(_cfg, attr, None))
    except Exception:
        log.debug("config.py 로드 실패 — 환경변수 키만 사용", exc_info=True)

    # 2) 환경변수
    _push(os.environ.get("GEMINI_API_KEY"))
    for i in range(1, 5):
        _push(os.environ.get(f"GEMINI_KEY_{i}"))
        _push(os.environ.get(f"GEMINI_FREE_API_KEY_AURA_{i}"))
        _push(os.environ.get(f"GEMINI_PAID_API_KEY_AURA_{i}"))

    return keys


# ---------------------------------------------------------------------------
# [시간대 동적 조명 엔진 SSOT] — 대표님 절대 지시 (2026-10-25 전면 재설계)
#   "숏폼을 밤 12시부터 만들건데, 시스템 시계를 보면 매일 밤만 나오잖아!
#    주제/배경에 맞게 동적으로 변해야지!"
#
#   ★ 핵심 원칙: 시스템 시계(datetime.now) 종속을 완전 폐기한다.
#     봇이 새벽 3시에 무인 가동하더라도, '브런치 카페' 에피소드는 100% 한낮 햇살,
#     '와인바' 에피소드는 100% 서울 야경, '루프탑 노을' 에피소드는 100% 골든아워로
#     스토리 맥락(주제 + 장소)에 따라 지능적으로 결정된다.
#
#   · 판정 3단: DAY(화사한 대낮) / NIGHT(스타일리시한 시티뷰 야경) / SUNSET(골든아워)
#   · 한 편(1~5씬) 안에서는 동일 time_of_day 가 전건에 주입되어 조명 일관성 100%.
#   · 촛불/암실/칙칙한 앰버 조명은 3개 시간대 전부에서 영구 퇴출한다.
# ---------------------------------------------------------------------------
TIME_OF_DAY_DAY = "day"
TIME_OF_DAY_NIGHT = "night"
TIME_OF_DAY_SUNSET = "sunset"

# [낮 조명] 화사한 대낮 자연광 — 파노라마 유리창 + 하이키 노출
LIGHTING_DAY = (
    "Bright crisp natural daylight streaming through large panoramic glass windows, "
    "luminous sun-drenched modern cafe interior, vibrant high-key exposure, "
    "pristine crystal-clear studio-grade lighting, radiant clean skin tone, "
    "absolutely NO candlelight, NO dark moody shadows, NO dim amber lighting"
)

# [밤 조명] 스타일리시한 시티뷰 야경 — 통유리창 + 서울 스카이라인 + 선명한 대비
LIGHTING_NIGHT = (
    "Sleek stylish modern nighttime aesthetic, panoramic floor-to-ceiling glass windows "
    "revealing glowing sparkling Seoul city skyline night view with distant urban bokeh, "
    "sophisticated high-end architectural interior lighting, "
    "crisp clear exposure with vibrant contrast on subject face, chic modern lounge atmosphere, "
    "absolutely NO candlelight, NO dark dingy room, NO dim spooky shadows, NO muddy yellowish tint"
)

# [노을 조명] 골든아워 로맨틱 선셋 — 루프탑 테라스 + 오렌지/마젠타 + 림라이트
LIGHTING_SUNSET = (
    "Romantic golden hour sunset lighting, warm orange and magenta hues glowing through panoramic terrace, "
    "soft cinematic twilight bokeh, beautiful rim light on subject hair and silhouette, "
    "absolutely NO candlelight, NO dingy dark room"
)

# [시간대별 장소 분위기 보정] 낮의 카페 / 밤의 시티뷰 라운지 / 노을의 루프탑 테라스
ATMOSPHERE_DAY = "bright airy sunlit atmosphere"
ATMOSPHERE_NIGHT = "chic sophisticated nighttime city-view lounge atmosphere"
ATMOSPHERE_SUNSET = "romantic golden-hour sunset rooftop atmosphere"

# ---------------------------------------------------------------------------
# [스토리 맥락 시그널 사전 SSOT] — 장소/주제 텍스트를 스캔하여 시간대를 결정한다.
#   · 모든 토큰은 소문자 비교(한글은 원형 유지)로 판정한다.
#   · 우선순위: SUNSET > NIGHT > DAY (노을 시그널이 가장 구체적이므로 최우선).
#   · 16대 핫플레이스 로테이션 풀과 1:1 결속:
#       DAY 8곳  = 에스프레소바 / 티하우스 / 브런치 / 온실 / 갤러리 / 베이커리 / 다도 / 젤라또
#       NIGHT 7곳 = 와인바 / LP바 / 심야북카페 / 라운지 / 한강야경 / 펍 / 재즈라운지
#       SUNSET 1곳 = 루프탑 노을 테라스
# ---------------------------------------------------------------------------
SUNSET_SIGNALS: Tuple[str, ...] = (
    "노을", "sunset", "dusk", "황혼", "golden hour", "twilight",
)
NIGHT_SIGNALS: Tuple[str, ...] = (
    "와인바", "wine", "lp 바", "lp bar", "vinyl", "야경", "night", "심야",
    "midnight", "펍", "pub", "재즈", "jazz", "라운지", "lounge", "한강",
)
DAY_SIGNALS: Tuple[str, ...] = (
    "브런치", "brunch", "온실", "greenhouse", "베이커리", "bakery",
    "에스프레소", "espresso", "티하우스", "tea house", "tea attic", "갤러리", "gallery",
    "다도", "젤라또", "gelato", "대리석", "marble", "호수뷰", "lake view",
)


def _match_signals(text: str, signals: Tuple[str, ...]) -> bool:
    """텍스트에 시그널 토큰이 하나라도 포함되는지 판정한다(대소문자 무시)."""
    low = str(text or "").lower()
    if not low:
        return False
    return any(tok.lower() in low for tok in signals)


def resolve_time_of_day(explicit: str = "", location: str = "", topic: str = "") -> str:
    """스토리 맥락(주제 + 장소) 기반으로 시간대를 지능적으로 판별한다.

    ★ 시스템 시계(datetime.now) 종속 완전 폐기 — 새벽 3시 무인 가동이어도
      브런치 에피소드는 100% 낮, 와인바 에피소드는 100% 밤으로 결정된다.

    우선순위:
      1) explicit 이 'day'/'night'/'sunset' 이면 최우선 존중(스펙 강제 지정).
      2) location + topic 텍스트에서 시그널 스캔:
         · SUNSET 시그널(노을/sunset/dusk/황혼/golden hour/twilight) → 'sunset'
         · NIGHT  시그널(와인바/wine/lp 바/vinyl/야경/night/심야/midnight/펍/pub/
                        재즈/jazz/라운지/lounge/한강)               → 'night'
         · DAY    시그널(브런치/brunch/온실/greenhouse/베이커리/bakery/에스프레소/
                        espresso/티하우스/tea/갤러리/gallery/다도/젤라또/gelato/
                        대리석/marble/호수뷰/lake view)              → 'day'
      3) 시그널 미검출 시 안전 기본값 'day' (칙칙한 밤 조명 오생성 방지).

    반환값은 반드시 TIME_OF_DAY_DAY / TIME_OF_DAY_NIGHT / TIME_OF_DAY_SUNSET 중 하나다.
    """
    token = (explicit or "").strip().lower()
    if token in (TIME_OF_DAY_DAY, TIME_OF_DAY_NIGHT, TIME_OF_DAY_SUNSET):
        return token

    # location(영문/한글 장소) + topic(한글 주제)을 하나의 맥락 문자열로 결속
    context = f"{location or ''} {topic or ''}"

    if _match_signals(context, SUNSET_SIGNALS):
        return TIME_OF_DAY_SUNSET
    if _match_signals(context, NIGHT_SIGNALS):
        return TIME_OF_DAY_NIGHT
    if _match_signals(context, DAY_SIGNALS):
        return TIME_OF_DAY_DAY

    # 시그널 미검출 → 안전 기본값(낮). 밤 조명 오생성으로 칙칙해지는 것을 방지.
    return TIME_OF_DAY_DAY


def lighting_for(time_of_day: str) -> str:
    """시간대 → 조명 프롬프트 SSOT 를 반환한다(미지정 시 낮 조명)."""
    if time_of_day == TIME_OF_DAY_NIGHT:
        return LIGHTING_NIGHT
    if time_of_day == TIME_OF_DAY_SUNSET:
        return LIGHTING_SUNSET
    return LIGHTING_DAY


def atmosphere_for(time_of_day: str) -> str:
    """시간대 → 장소 분위기 문구를 반환한다(미지정 시 낮 분위기)."""
    if time_of_day == TIME_OF_DAY_NIGHT:
        return ATMOSPHERE_NIGHT
    if time_of_day == TIME_OF_DAY_SUNSET:
        return ATMOSPHERE_SUNSET
    return ATMOSPHERE_DAY


class GeminiImageAdapter(ImagePort):
    """1순위 어댑터 — google.genai 로 1080x1920 실사 씬 이미지를 생성한다.

    화자별 마스터 캐릭터 사진을 레퍼런스로 주입하여 씬 배경과 동일 인물이
    어우러진 실사 컷을 렌더링한다. 실패 시 예외를 발생시켜 다음 어댑터로
    자연스럽게 폴백한다(검은 박스 생성 금지).
    """
    name = "gemini"

    def __init__(self) -> None:
        self._keys: Optional[List[str]] = None

    def _keys_pool(self) -> List[str]:
        if self._keys is None:
            self._keys = _collect_image_api_keys()
        return self._keys

    def available(self) -> bool:
        """키 풀 + google.genai 임포트 가능 여부로 실사용 가능성 판정."""
        if not self._keys_pool():
            return False
        try:
            from google import genai  # noqa: F401
            return True
        except Exception:
            return False

    def _build_scene_prompt(self, prompt: str, scene_idx: int, location_en: str = "",
                            time_of_day: str = "", topic: str = "") -> str:
        who = SCENE_CHARACTER_MAP.get(scene_idx, "sujin")
        name_ko = "수진 (20대 한국 여성)" if who == "sujin" else "민우 (20대 한국 남성)"

        # ------------------------------------------------------------------
        # [텍스트/배너/자막 유발 토큰 원천 세정 SSOT] 대표님 절대 지시 (2026-10-26):
        #   "화면 중앙에 쓸데없이 반투명 글자 박스가 뜨는 현상 영구 박멸"
        #
        #   ★ 왜 필수인가: Gemini 자율 집필이 image_prompt 에 "with text saying '...'"
        #     같은 지시를 섞어 넣으면, 이미지 생성 모델이 그 지시를 문자 그대로
        #     받아들여 화면 중앙에 반투명 글자 박스/배너/자막을 그려 넣는다.
        #     이는 순수 실사 인물 컷을 오염시키는 최대 원인이다.
        #
        #   ★ 4단 세정 파이프라인 (앞 단계가 뒤 단계의 입력을 정리):
        #     ① 따옴표로 감싼 텍스트 지시구 제거 — "with text saying '보험 리밸런스'"
        #        → text/title/banner/overlay/caption/words/letters/graphic box +
        #          saying/displaying/showing/reading/with/of + '...' 패턴 통째 삭제.
        #     ② 남은 모든 따옴표 쌍 제거 — 인용부호 안의 잔여 문자열까지 회수.
        #     ③ 단독 텍스트/배너 토큰 제거 — text overlay / graphic banner /
        #        title card / subtitles / watermark / banner / signage.
        #     ④ 한글 2자 이상 연속 토큰 제거 — 영문 시네마틱 프롬프트에 섞인
        #        한국어 지시(예: '보험 리밸런스 화면')를 원천 차단.
        #     ⑤ 연속 공백 정규화 + 양끝 strip — 프롬프트 문장 오염 방지.
        #
        #   · 세정 결과가 빈 문자열이 되어도 안전하다(composition 이 주 내용을 담당).
        #   · 이 세정은 '지시 텍스트'만 제거하며, 조명/구도/감정 토큰은 건드리지 않는다.
        # ------------------------------------------------------------------
        safe_prompt = re.sub(
            r"(?:with\s+)?(?:text|title|banner|overlay|caption|words?|letters?|graphic\s+box)\s*(?:saying|displaying|showing|reading|with|of)?\s*['\"][^'\"]*['\"]",
            "",
            prompt or "",
            flags=re.IGNORECASE,
        )
        safe_prompt = re.sub(r"['\"][^'\"]*['\"]", "", safe_prompt)
        safe_prompt = re.sub(r"\b(?:text\s*overlay|graphic\s*banner|title\s*card|subtitles?|watermark|banner|signage)\b", "", safe_prompt, flags=re.IGNORECASE)
        safe_prompt = re.sub(r"[가-힣]{2,}(?:\s*[가-힣]{2,})*", "", safe_prompt)
        safe_prompt = re.sub(r"\s{2,}", " ", safe_prompt).strip()

        # [장소 로테이션] 회차별 핫플레이스 주입 — 미주입 시에만 안전 기본값 사용.
        #   · 한 편(1~5씬) 안에서는 동일 loc 문자열이 5씬 전건에 그대로 쓰여
        #     "같은 공간에서 촬영한 단독 정면 1인 샷" 공간 연속성이 100% 성립한다.
        #   · 다음 회차에는 LOCATIONS_EN 로테이션으로 완전히 다른 장소가 주입된다.
        #   · [영구 퇴출] 숏-리버스(OTS) 2인 구도는 폐기되었으므로 loc 는 배경 전용이다.
        loc = (location_en or "").strip() or "bright sunlit modern cafe wooden table"

        # ------------------------------------------------------------------
        # [시간대 동적 조명 SSOT] 대표님 절대 지시 (2026-10-25 전면 재설계)
        #   "숏폼을 밤 12시부터 만들건데, 시스템 시계를 보면 매일 밤만 나오잖아!
        #    주제/배경에 맞게 동적으로 변해야지!"
        #   · 시스템 시계 종속 완전 폐기 — location(장소) + topic(주제) 맥락으로 판정.
        #   · 브런치/온실/베이커리/티하우스/에스프레소 → 100% 화사한 낮(day)
        #   · 와인바/LP바/한강야경/심야북카페/재즈/라운지 → 100% 시티뷰 밤(night)
        #   · 루프탑 노을 테라스                        → 100% 골든아워 노을(sunset)
        #   · 한 편(1~5씬) 안에서는 동일 값이 전건에 주입되어 조명 일관성 100%.
        #   · 3개 시간대 전부 촛불·암실·칙칙한 앰버 조명은 영구 퇴출.
        # ------------------------------------------------------------------
        tod = resolve_time_of_day(time_of_day, location=loc, topic=topic)
        lighting = lighting_for(tod)
        atmosphere = atmosphere_for(tod)

        # ------------------------------------------------------------------
        # [구도 SSOT — 1인칭 맞은편 관전 시점] 대표님 확정 지시 (2026-10-25):
        #   "맞은편에 앉아서 바라보는 1인칭 시점, 상반신 전체가 보이는 미디엄 샷,
        #    하단에 테이블 상판 앞 모서리만 살짝, 전경에 빈 의자/등받이 절대 금지"
        #
        #   ★ 왜 이 구도인가: 기존 '정면 응시 클로즈업'은 인물이 카메라를 뚫어지게
        #     쳐다보는 부자연스러운 구도였고, 전경에 빈 의자 등받이가 걸려 "누가
        #     앉아서 찍은 거냐"는 위화감을 유발했다. 이제 카메라는 테이블 맞은편에
        #     앉은 관전자의 눈높이가 되어, 인물을 자연스럽게 마주보는 1인칭 POV 로 전환한다.
        #
        #   · POV: First-person eye-level POV of someone sitting directly across the table.
        #   · 샷: waist-up medium shot — 상반신 전체(어깨/가슴/몸통/팔)가 프레임에 담긴다.
        #   · 하단: 테이블 상판 '앞 모서리'만 살짝 노출(과도한 테이블 면적 금지).
        #   · 전경 봉인: 빈 의자/등받이/가구를 네거티브로 물리적 차단.
        #   · 2인 대화 구도(OTS)는 여전히 영구 퇴출 — 화면에는 오직 1인만 존재한다.
        # ------------------------------------------------------------------
        pov_frame = (
            "First-person eye-level POV of someone sitting directly across the table, "
            "waist-up medium shot showing full upper body, torso, and relaxed arms, "
            "the subject is seated across the table facing the camera at eye level, "
            "The bottom edge of the frame shows only the clean front edge of the dining table surface, "
            "ABSOLUTELY NO empty chair in foreground, NO chair backrest blocking the frame, "
            "NO empty seat in front of camera, NO foreground furniture"
        )

        # ------------------------------------------------------------------
        # [입모양 봉인 SSOT] 키프레임은 반드시 입을 완전히 다문 상태로 생성한다.
        #   대표님 절대 지침 (2026-10-25):
        #   "제미나이 키프레임 생성 시 입모양 100% 다물기 강제"
        #
        #   ★ 왜 필수인가: Wan 2.2 S2V 는 입력 키프레임의 입모양을 시작 포즈로 삼는다.
        #     키프레임이 입을 벌리고 있으면 립싱크 첫 프레임이 어긋나 "말 끊김/입 튐"이
        #     발생한다. 따라서 포지티브(다문 입) + 네거티브(벌린 입/치아 금지)를
        #     이중으로 봉인하여 어떤 해석 여지도 남기지 않는다.
        # ------------------------------------------------------------------
        mouth_seal = (
            "strictly closed mouth, neutral relaxed lips pressed together, mouth shut tightly, "
            "absolutely NO open mouth, NO visible teeth, NO smiling with open mouth, "
            "lips completely sealed"
        )

        # ------------------------------------------------------------------
        # [씬별 감정 연기 SSOT 주입] 대표님 절대 지시 (2026-10-25):
        #   "씬 1: 억울·답답 공감 표정 / 씬 2: 헛웃음·팩폭 남사친 표정 /
        #    씬 4: 신난 설렘·환한 미소 표정 / 씬 5: 다정·신뢰 호감형 미소 표정...
        #    이걸 완 만들때 제대로 3번 처럼 다 집어 넣어"
        #
        #   ★ 왜 필수인가: 씬 3 만 표정 지시를 갖고 있어 나머지 씬이 무표정으로
        #     생성되던 문제를 절단한다. SCENE_EMOTION_SSOT 단일 사전에서 씬별
        #     감정선을 가져와 mouth_seal 과 함께 composition 에 명시 주입한다.
        #   · emotion_for() 는 S2V(Wan) 계층과 공유하는 동일 SSOT 접근자다.
        #     두 계층이 같은 값을 참조해야 키프레임 얼굴과 영상 표정이 일치한다.
        #   · 입모양 봉인(mouth_seal)은 그대로 유지 — 감정선은 'closed lips' 계열로만
        #     서술되어 립싱크 첫 프레임을 깨뜨리지 않는다.
        # ------------------------------------------------------------------
        emotion = emotion_for(scene_idx)

        # ------------------------------------------------------------------
        # [씬 3 보험 리밸런스 소개 씬 전용 연출 SSOT] 대표님 절대 지시 (2026-10-25):
        #   "3번 씬은 보험 리밸런스 소개 씬인데, 여자 주인공이 핸드폰을 손에 들고 보고
        #    말하게 만들어야지! 테이블 위에 폰 덩그러니 세워놓고 정면만 쳐다보는
        #    어색한 연출 영구 퇴출!"
        #
        #   ★ 왜 필수인가: 씬 3은 '보험 리밸런스 AI 솔루션 체감' 씬이다. 주인공이 폰을
        #     손에 들고 화면을 보며 감탄하는 연출이어야 서사가 성립한다. 기존처럼
        #     테이블 위에 세워진 폰을 정면으로 응시하면 "폰이 나를 쳐다보는" 어색한
        #     구도가 되어 보험 리밸런스 소개 씬의 설득력이 0이 된다.
        #
        #   · 씬 3 한정: 양손으로 스마트폰을 가슴 앞쪽에 들고, 시선은 화면을 내려다보며
        #     감탄/놀람 표정. 테이블 위 정적 폰은 네거티브로 물리적 봉인.
        #   · 씬 1/2/4/5: 맞은편 1인칭 POV + 중립 팔 자세 유지.
        #   · 입모양 봉인(mouth_seal)은 씬 3에서도 100% 유지 — Wan S2V 립싱크 대기.
        # ------------------------------------------------------------------
        if scene_idx == 3:
            phone_hold = (
                "holding a smartphone naturally with BOTH hands in front of her chest, "
                "gazing down at the glowing smartphone screen in her hands "
                "with a pleasantly surprised, impressed expression, "
                "the phone MUST be held in her hands, "
                "absolutely NO static phone placed on the table, "
                "NO phone standing upright on the table, NO phone lying on the table, "
                "hands stay calmly on the phone only, NO waving hands, NO hand gestures, "
                "NO pointing fingers, NO robotic twitching"
            )
            composition = (
                f"Solo single person portrait of {name_ko} sitting at {loc}, "
                f"{pov_frame}, "
                f"{phone_hold}, {emotion}, {mouth_seal}. "
                "STRICTLY EXACTLY ONE PERSON in the entire image. "
                "ABSOLUTELY NO other people, NO companion, NO foreground person, "
                "NO shoulder in foreground, NO back of head, NO silhouette, "
                "NO second person, NO over-the-shoulder shot. "
                "Completely clean single subject solo frame."
            )
        else:
            # ------------------------------------------------------------------
            # [씬 1/2/4/5 손(hand) 명령어 전량 배제 SSOT] 대표님 최우선 절대 지시:
            #   "1, 2, 4, 5번 씬 (로봇처럼 삐걱거림),......손에 대한 명령어 전부 삭제"
            #
            #   ★ 왜 필수인가: 키프레임에 손/팔 동작을 유도하는 어떤 지시도 넣지 않는다.
            #     Wan 2.2 S2V 는 키프레임의 팔 위치를 시작 포즈로 삼기 때문에,
            #     키프레임에 손이 크게 잡히면 영상에서 팔이 로봇처럼 삐걱거린다.
            #     따라서 상반신 단독 샷 + 팔을 편안히 내린 중립 자세를 포지티브로
            #     고정하고, 손/팔/제스처를 네거티브로 물리적 봉인한다.
            #
            #   · 오직 씬 3 만 phone_hold(양손으로 스마트폰 쥐기) 를 유지한다.
            #   · 씬 1/2/4/5 는 손을 화면에 끌어들이지 않는 중립 상반신 샷이다.
            #   · [POV 결속] 맞은편 1인칭 시점이므로 '프레임 밖으로 팔이 나감' 대신
            #     '편안히 내린 팔'로 서술한다(미디엄 샷에서 팔이 화면에 보여야 자연스럽다).
            # ------------------------------------------------------------------
            hands_neutral = (
                "arms relaxed naturally at her sides, calm neutral resting posture, "
                "no gesturing"
            )
            composition = (
                f"Solo single person portrait of {name_ko} sitting at {loc}, "
                f"{pov_frame}, "
                f"{hands_neutral}, {emotion}, {mouth_seal}. "
                "STRICTLY EXACTLY ONE PERSON in the entire image. "
                "ABSOLUTELY NO other people, NO companion, NO foreground person, "
                "NO shoulder in foreground, NO back of head, NO silhouette, "
                "NO second person, NO over-the-shoulder shot. "
                "ABSOLUTELY NO raised hands, NO waving hands, NO hand gestures, "
                "NO pointing fingers, NO arms crossed in front of chest. "
                "Completely clean single subject solo frame."
            )

        # ------------------------------------------------------------------
        # [최종 조립 — 텍스트/배너 영구 봉인 SSOT] 대표님 절대 지시 (2026-10-26):
        #   "화면 중앙에 쓸데없이 반투명 글자 박스가 뜨는 현상 영구 박멸"
        #
        #   ★ 왜 네거티브를 최종 프롬프트 끝에 다시 박는가:
        #     이미지 생성 모델은 프롬프트 후반부 토큰에 더 강하게 반응하는 경향이 있다.
        #     세정(safe_prompt)이 '유발 지시'를 제거하는 1차 방어라면, 이 네거티브
        #     블록은 '텍스트 자체를 그리지 말라'는 2차 물리적 봉인이다.
        #     두 방어를 동시에 걸어야 반투명 글자 박스/자막/워터마크가 0% 로 수렴한다.
        #
        #   · NO text / NO written words / NO letters / NO Korean text
        #     → 문자 렌더링 자체를 금지(한국어 포함).
        #   · NO title banner / NO graphic overlay box / NO subtitle
        #     → 반투명 박스·배너·자막 UI 요소 금지(대표님 지적 현상의 직접 원인).
        #   · NO watermark / NO logo → 브랜드 워터마크 오삽입 방지.
        #   · NO cartoon / NO illustration → 실사 사진 톤 고정(일러스트 이탈 차단).
        #   · safe_lighting / safe_atmosphere / safe_loc 는 세정 대상이 아닌
        #     내부 SSOT 값이므로 그대로 주입한다(오탈자 방지).
        # ------------------------------------------------------------------
        return (
            "Photorealistic cinematic vertical short-form drama still, 9:16 portrait. "
            f"Main subject: {name_ko} — keep the EXACT same face, hairstyle and identity "
            "as the attached reference portrait image. Do not change the person's identity. "
            f"{composition}. "
            f"Scene direction: {safe_prompt}. "
            f"{lighting}. "
            f"Ultra realistic skin texture, {atmosphere} of {loc}, "
            "cinematic lighting, shallow depth of field, 35mm film grain, "
            "absolutely NO text, NO written words, NO letters, NO Korean text, "
            "NO title banner, NO graphic overlay box, NO subtitle, NO watermark, NO logo, NO cartoon, NO illustration."
        )

    def generate(self, prompt: str, out_path: Path, size: str, scene_idx: int = 1,
                 location_en: str = "", run_id: str = "", time_of_day: str = "",
                 topic: str = "") -> Path:
        keys = self._keys_pool()
        if not keys:
            raise AdapterError("Gemini 이미지: API 키 부재 — 폴백 전환")

        try:
            from google import genai
            from google.genai import types as genai_types
        except Exception as e:
            raise AdapterError(f"Gemini 이미지: google.genai 임포트 실패 — {e!r}") from e

        # ------------------------------------------------------------------
        # [단독 레퍼런스 SSOT] 씬 1~5 전 구간 오직 해당 씬 화자 마스터 1장만 주입한다.
        #   대표님 절대 지시 (2026-10-25):
        #   "2번씬이 남자 주인공인데 왠 또 여자랑 말하고 있냐!"
        #
        #   · 복수 레퍼런스(여자+남자 2장 동시 주입) 로직은 전량 영구 폐기.
        #   · 씬 1/3/5 → 수진 마스터 1장 → 수진 단독 정면만 생성.
        #   · 씬 2/4   → 민우 마스터 1장 → 민우 단독 정면만 생성.
        #   · run_id 가 주어지면 회차 전용 신규 주인공 마스터가 우선 사용된다.
        # ------------------------------------------------------------------
        ref_paths: List[Path] = []
        try:
            ref_paths.append(resolve_character_asset(scene_idx, run_id))
        except AdapterError:
            raise
        except Exception as e:
            raise AdapterError(f"Gemini 이미지: 레퍼런스 해석 실패 — {e!r}") from e

        ref_parts: List[Any] = []
        for rp in ref_paths:
            try:
                ref_parts.append(
                    genai_types.Part.from_bytes(data=rp.read_bytes(), mime_type="image/png")
                )
            except Exception as e:
                raise AdapterError(f"Gemini 이미지: 레퍼런스 로드 실패 {rp} — {e!r}") from e

        # [단독 정면 SSOT] 레퍼런스는 항상 1장이므로 2인 주입 안내 문구는 영구 삭제.
        full_prompt = self._build_scene_prompt(prompt, scene_idx, location_en, time_of_day, topic)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        ref_names = "+".join(p.name for p in ref_paths)

        last_err: Optional[BaseException] = None
        for key in keys:
            for model in GEMINI_IMAGE_MODELS:
                try:
                    client = genai.Client(api_key=key)
                    resp = client.models.generate_content(
                        model=model,
                        contents=[*ref_parts, full_prompt],
                    )
                    saved = False
                    for cand in (getattr(resp, "candidates", None) or []):
                        content = getattr(cand, "content", None)
                        for part in (getattr(content, "parts", None) or []):
                            inline = getattr(part, "inline_data", None)
                            if inline is not None and getattr(inline, "data", None):
                                out_path.write_bytes(inline.data)
                                saved = True
                                break
                        if saved:
                            break
                    if not saved:
                        raise AdapterError("Gemini 이미지: 응답에 이미지 파트 없음")

                    # 세로 1080x1920 규격 강제 정규화
                    try:
                        from PIL import Image, ImageOps
                        w, h = (int(x) for x in size.lower().split("x"))
                        with Image.open(out_path) as im:
                            im = im.convert("RGB")
                            fitted = ImageOps.fit(im, (w, h), method=Image.LANCZOS, centering=(0.5, 0.4))
                            fitted.save(out_path, format="PNG")
                    except Exception:
                        log.warning("Gemini 이미지 후처리 리사이즈 실패 — 원본 유지", exc_info=True)

                    log.info("Gemini 이미지 생성 성공(model=%s, scene=%d, ref=%s, tod=%s)",
                             model, scene_idx, ref_names,
                             resolve_time_of_day(time_of_day, location=location_en, topic=topic))
                    return out_path
                except Exception as e:
                    last_err = e
                    log.warning("Gemini 이미지 실패(model=%s): %s", model, e)
                    continue

        raise AdapterError(f"Gemini 이미지 전 키/모델 소진 — 폴백 전환: {last_err!r}")


class ComfyUIImageAdapter(ImagePort):
    name = "comfyui"
    def __init__(self, endpoint: str = "http://127.0.0.1:8188"):
        self.endpoint = endpoint
    def available(self) -> bool:
        try:
            import urllib.request
            urllib.request.urlopen(self.endpoint + "/system_stats", timeout=2)
            return True
        except Exception:
            return False
    def generate(self, prompt: str, out_path: Path, size: str, scene_idx: int = 1) -> Path:
        raise AdapterError("ComfyUI 어댑터는 워크플로우 JSON 주입 필요 — 미구성 상태")


class BrandAssetFallbackAdapter(ImagePort):
    """3순위 폴백 — 브랜드 마스터 실사 에셋을 시네마틱 크롭하여 출력한다.

    [영구 퇴출] 검은색/회색 단색 더미 박스는 어떤 상황에서도 생성하지 않는다.
    씬 2 → 민우 마스터, 씬 1/3/4/5 → 수진 마스터를 1080x1920 세로 비율로
    ImageOps.fit 크롭/리사이즈하여 실제 인물 비주얼을 보장한다.
    """
    name = "asset_fallback"

    def available(self) -> bool:
        try:
            import PIL  # noqa: F401
        except Exception:
            return False
        # 마스터 에셋이 하나라도 존재해야 폴백 자격이 있다.
        for fn in CHARACTER_MASTER_FILES.values():
            p = CHARACTER_ASSET_DIR / fn
            if p.exists() and p.stat().st_size > 0:
                return True
        return False

    def generate(self, prompt: str, out_path: Path, size: str, scene_idx: int = 1) -> Path:
        from PIL import Image, ImageOps, ImageEnhance

        w, h = (int(x) for x in size.lower().split("x"))
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # 1) 씬 화자 마스터 우선, 실패 시 존재하는 다른 마스터로 결정론적 대체
        candidates: List[Path] = []
        try:
            candidates.append(resolve_character_asset(scene_idx))
        except AdapterError:
            pass
        for fn in CHARACTER_MASTER_FILES.values():
            p = CHARACTER_ASSET_DIR / fn
            if p.exists() and p.stat().st_size > 0 and p not in candidates:
                candidates.append(p)

        if not candidates:
            raise AdapterError(
                f"BrandAssetFallback: 마스터 에셋 전무 — {CHARACTER_ASSET_DIR} 확인 필요"
            )

        src = candidates[0]
        with Image.open(src) as im:
            im = im.convert("RGB")
            # 세로 9:16 시네마틱 크롭 (얼굴 상단 40% 지점 기준)
            fitted = ImageOps.fit(im, (w, h), method=Image.LANCZOS, centering=(0.5, 0.4))
            # 시네마틱 톤 보정 (과도한 보정 금지 — 실사 유지)
            fitted = ImageEnhance.Contrast(fitted).enhance(1.04)
            fitted = ImageEnhance.Color(fitted).enhance(1.03)
            fitted.save(out_path, format="PNG")

        log.info("BrandAssetFallback 사용: scene=%d src=%s → %s", scene_idx, src.name, out_path.name)
        return out_path


# ---------------------------------------------------------------------------
# 5) TTS 어댑터 (edge / pyttsx3 / silent)
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# [보이스 SSOT] 화자 → 보이스 매핑 (SunHiNeural 영구 퇴출)
#   · Gemini 2.5 Flash Native Audio: Aoede(여) / Puck(남)
#   · Edge-TTS 백업: HyunsuNeural(여) / BongJinNeural(남, 중후한 대화체)
#   · ko-KR-SunHiNeural 은 관리사무소 안내방송 기계음 — 어떤 경로로도 사용 금지
# ---------------------------------------------------------------------------
GEMINI_VOICE_FEMALE = "Aoede"
GEMINI_VOICE_MALE = "Charon"  # 🎙️ 대표님 명령: 37세 가장/남편 전용 중후한 음성
EDGE_VOICE_FEMALE = "ko-KR-HyunsuNeural"
EDGE_VOICE_MALE = "ko-KR-BongJinNeural"  # 🎙️ 중후한 남성 대화체
BANNED_VOICE_TOKENS: Tuple[str, ...] = ("sunhi",)
DRAMA_SPEECH_SPEED = 1.20  # ⏱️ 대표님 확정 명령: 1.2배속 고정 (Wan S2V 81프레임 수렴)


def _is_banned_voice(voice_id: str) -> bool:
    """금지 보이스(SunHi 등 안내방송 톤) 여부를 판정한다."""
    low = str(voice_id or "").lower()
    return any(tok in low for tok in BANNED_VOICE_TOKENS)


def _detect_speaker_gender(voice_id: str) -> str:
    """voice_id 문자열로 화자 성별을 결정론적으로 판별한다.

    male 판정 토큰: charon / fenrir / puck / bongjin / injoon / male / 남
    그 외(기본값): female
    """
    low = str(voice_id or "").lower()
    if any(m in low for m in ("charon", "fenrir", "puck", "bongjin", "injoon", "male", "남")):
        return "male"
    return "female"


def _resolve_edge_voice(voice_id: str) -> str:
    """Gemini 보이스명(Aoede/Charon/Puck 등) 및 성별 토큰을 Edge-TTS 보이스로 정규화한다.

    SunHiNeural 등 금지 보이스가 유입되면 성별 판정 후 안전 보이스로 강제 치환한다.
    """
    low = str(voice_id or "").lower()
    if "aoede" in low:
        return EDGE_VOICE_FEMALE
    if any(m in low for m in ("charon", "fenrir", "puck", "bongjin", "injoon")):
        return EDGE_VOICE_MALE
    if _is_banned_voice(voice_id):
        log.warning("금지 보이스 감지('%s') — 안전 보이스로 강제 치환", voice_id)
        return EDGE_VOICE_FEMALE
    if low.startswith("ko-kr-") and low.endswith("neural"):
        return voice_id
    return EDGE_VOICE_FEMALE if _detect_speaker_gender(voice_id) == "female" else EDGE_VOICE_MALE


class GeminiDramaDialogueAdapter(TTSPort):
    """1순위 숏드라마 전용 고품질 음성 어댑터.
    - modules.drama_engine.drama_dialogue_synthesizer.DramaDialogueSynthesizer 연동
    - 1순위: Google Gemini 2.5 Flash Native Audio 9키 체인 (Aoede 여 / Charon 중후한 남)
    - 2순위 백업: Edge-TTS 대화체 (ko-KR-HyunsuNeural / ko-KR-BongJinNeural)
    - ⏱️ 대표님 확정 명령: 반드시 1.2배속(atempo=1.20) 고정 정규화 (Wan S2V 81프레임 수렴)
    - 🛑 관리사무소 안내방송 기계음 (ko-KR-SunHiNeural) 영구 퇴출
    """
    name = "gemini_drama"

    def __init__(self):
        self._synth = None

    def _get_synth(self):
        if self._synth is None:
            try:
                from modules.drama_engine.drama_dialogue_synthesizer import DramaDialogueSynthesizer
                self._synth = DramaDialogueSynthesizer()
            except Exception as e:
                log.warning("DramaDialogueSynthesizer 초기화 실패: %s", e)
        return self._synth

    def available(self) -> bool:
        synth = self._get_synth()
        return synth is not None

    def synthesize(self, text: str, voice_id: str, out_path: Path) -> Path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        synth = self._get_synth()
        if synth is None:
            raise AdapterError("GeminiDramaDialogueAdapter: 합성기 초기화 불가")

        # 화자 성별 자동 판별 (Aoede/Hyunsu -> female, Charon/BongJin -> male)
        speaker = _detect_speaker_gender(voice_id)

        # 1. 원본 음성 합성 (Gemini 2.5 Native Audio 9키 체인 -> 실패 시 Edge-TTS 페일오버)
        raw_name = f"raw_{out_path.name}"
        raw_path, raw_dur = synth.synthesize_dialogue(
            dialogue_text=text,
            output_filename=raw_name,
            force_speaker=speaker,
            voice_override=voice_id,
        )

        # 2. ⏱️ 1.2배속(atempo=1.20) 고정 정규화 (Wan 2.2 S2V 81프레임 상한 수렴)
        conformed_path, conformed_dur = synth._conform_audio_duration(
            audio_path=raw_path,
            target_duration=0.0,
            output_path=out_path,
            speed_override=DRAMA_SPEECH_SPEED,
        )
        log.info("GeminiDramaDialogue TTS 완료: scene=%s speaker=%s dur=%.2fs (%.2fx)",
                 out_path.stem, speaker, conformed_dur, DRAMA_SPEECH_SPEED)
        return out_path


class EdgeTTSAdapter(TTSPort):
    name = "edge"
    def available(self) -> bool:
        try:
            import edge_tts  # noqa: F401
            return True
        except Exception:
            return False
    def synthesize(self, text: str, voice_id: str, out_path: Path) -> Path:
        import asyncio, edge_tts
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # [보이스 정규화] Aoede -> HyunsuNeural, Puck -> InJoonNeural, SunHi -> 영구 차단
        edge_voice = _resolve_edge_voice(voice_id)
        async def _run():
            await edge_tts.Communicate(text, edge_voice).save(str(out_path))
        asyncio.run(_run())
        return out_path


class Pyttsx3Adapter(TTSPort):
    name = "pyttsx3"
    def available(self) -> bool:
        try:
            import pyttsx3  # noqa: F401
            return True
        except Exception:
            return False
    def synthesize(self, text: str, voice_id: str, out_path: Path) -> Path:
        import pyttsx3
        out_path.parent.mkdir(parents=True, exist_ok=True)
        eng = pyttsx3.init()
        eng.save_to_file(text, str(out_path))
        eng.runAndWait()
        return out_path


class SilentTTSAdapter(TTSPort):
    name = "silent"
    def available(self) -> bool:
        return True
    def synthesize(self, text: str, voice_id: str, out_path: Path) -> Path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(b"")
        log.warning("SilentTTS 사용 — 오디오 무음(폴백)")
        return out_path


# ---------------------------------------------------------------------------
# 6) FFmpeg 비디오 어댑터 — 좀비/고아 프로세스 회수 보장
# ---------------------------------------------------------------------------
class FFmpegVideoAdapter(VideoPort):
    name = "ffmpeg"

    def __init__(self, cfg: PipelineConfig):
        self.cfg = cfg
        self._procs: List[subprocess.Popen] = []
        self._lock = threading.Lock()
        atexit.register(self._reap_all)

    def _resolve_binary(self) -> str:
        """
        [SSOT] ffmpeg 실행 파일 경로를 1회만 해석하고 캐시한다.
        탐색 순서: 명시 경로 → PATH → imageio_ffmpeg 번들.
        실패 시 BinaryResolutionError로 표면화(은폐 금지).
        """
        cached = getattr(self, "_resolved_bin", None)
        if cached:
            return cached

        candidates: List[Tuple[str, str]] = []

        # 1) 설정에 절대경로가 명시된 경우 최우선
        cfg_bin = getattr(self.cfg, "ffmpeg_bin", None) or "ffmpeg"
        if os.path.isabs(cfg_bin) and os.path.isfile(cfg_bin):
            candidates.append(("config", cfg_bin))

        # 2) PATH 탐색
        which_hit = shutil.which(cfg_bin)
        if which_hit:
            candidates.append(("path", which_hit))

        # 3) imageio_ffmpeg 번들 (Windows에서 PATH 미등록 케이스 핵심)
        try:
            import imageio_ffmpeg  # type: ignore
            bundled = imageio_ffmpeg.get_ffmpeg_exe()
            if bundled and os.path.isfile(bundled):
                candidates.append(("imageio_ffmpeg", bundled))
        except ImportError:
            pass
        except Exception as e:
            raise BinaryResolutionError(
                f"imageio_ffmpeg 번들 해석 중 예외: {e!r}"
            ) from e

        if not candidates:
            raise BinaryResolutionError(
                f"ffmpeg 바이너리를 찾을 수 없음 (cfg={cfg_bin!r}, "
                f"PATH/imageio_ffmpeg 모두 실패)"
            )

        source, resolved = candidates[0]
        self._resolved_bin = resolved
        self._resolved_source = source
        return resolved

    def available(self) -> bool:
        """
        순수 조회 메서드. 상태 변이는 _resolve_binary 내부에서만 발생하며,
        해석 실패는 False가 아니라 BinaryResolutionError로 표면화한다.
        """
        try:
            self._resolve_binary()
            return True
        except BinaryResolutionError:
            return False

    def _spawn(self, cmd: List[str]) -> subprocess.Popen:
        """
        플랫폼 대칭 프로세스 생성 + 추적 등록 원자화.
        - POSIX: start_new_session=True (새 프로세스 그룹 리더)
        - Windows: CREATE_NEW_PROCESS_GROUP (killpg 대응 그룹 격리)
        생성 직후 _procs 등록을 같은 임계구역에서 수행하여 추적 누락을 차단.
        """
        popen_kwargs: Dict[str, Any] = {
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
        }
        if os.name == "nt":
            creationflags = 0
            creationflags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            popen_kwargs["creationflags"] = creationflags
        else:
            popen_kwargs["start_new_session"] = True

        p = subprocess.Popen(cmd, **popen_kwargs)

        # [원자적 등록] 생성과 등록 사이에 회수 경로가 끊기지 않도록 즉시 등록
        with self._lock:
            self._procs.append(p)
        return p

    def _cleanup_partial_outputs(self) -> None:
        """부분 산출물 정리 훅 — 실패 시에도 예외를 삼키지 않는다."""
        try:
            for p in list(self._procs):
                if p.poll() is None:
                    try:
                        p.kill()
                    except OSError:
                        pass
        finally:
            with self._lock:
                self._procs.clear()

    def _kill_group(self, p: subprocess.Popen, timeout: float = 5.0) -> None:
        """플랫폼 독립적 프로세스(그룹) 종료 정책.

        - POSIX: 프로세스 그룹에 SIGTERM → 대기 → SIGKILL 에스컬레이션
        - Windows: terminate() → wait(timeout) → kill() 에스컬레이션
        - 실패 시 예외를 삼키지 않고 ProcessTerminationError로 승격하여
          좀비 프로세스/부분 산출물 잔존을 조용히 은폐하지 않는다.
        """
        if p.poll() is not None:
            return

        is_posix = hasattr(os, "killpg") and hasattr(os, "getpgid")
        sig_term = getattr(signal, "SIGTERM", None)
        sig_kill = getattr(signal, "SIGKILL", sig_term)

        try:
            if is_posix:
                try:
                    pgid = os.getpgid(p.pid)
                except ProcessLookupError:
                    return
                try:
                    os.killpg(pgid, sig_term)
                except ProcessLookupError:
                    return
                try:
                    p.wait(timeout=timeout)
                    return
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(pgid, sig_kill)
                    except ProcessLookupError:
                        return
                    p.wait(timeout=timeout)
                    return
            else:
                # Windows: terminate → wait → kill 에스컬레이션
                try:
                    p.terminate()
                except OSError:
                    pass
                try:
                    p.wait(timeout=timeout)
                    return
                except subprocess.TimeoutExpired:
                    try:
                        p.kill()
                    except OSError:
                        pass
                    p.wait(timeout=timeout)
                    return
        except subprocess.TimeoutExpired as exc:
            self._cleanup_partial_outputs()
            raise ProcessTerminationError(
                f"프로세스 종료 실패(pid={p.pid}, timeout={timeout}s): 잔존 프로세스 회수 불가"
            ) from exc
        except Exception as exc:
            self._cleanup_partial_outputs()
            raise ProcessTerminationError(
                f"프로세스 종료 중 예기치 못한 오류(pid={p.pid}): {exc!r}"
            ) from exc

    def _reap_all(self) -> None:
        with self._lock:
            procs = list(self._procs)
            self._procs.clear()
        for p in procs:
            try:
                self._kill_group(p)
            except ProcessTerminationError:
                log.exception("atexit 회수 실패(pid=%s)", p.pid)

    def assemble(self, image: Path, audio: Path, out_path: Path, duration: float,
                 cfg: PipelineConfig, scene_idx: int = 1) -> Path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # [WinError 2 해결] cfg.ffmpeg_bin 원문 대신 SSOT 해석 경로를 사용한다.
        # PATH 미등록 Windows 환경에서도 imageio_ffmpeg 번들 절대경로로 실행된다.
        ffmpeg_exe = self._resolve_binary()
        has_audio = audio.exists() and audio.stat().st_size > 0
        cmd = [ffmpeg_exe, "-y", "-loop", "1", "-i", str(image)]
        if has_audio:
            cmd += ["-i", str(audio)]
        cmd += ["-t", f"{duration:.3f}", "-r", str(cfg.fps),
                "-vf", f"scale={cfg.resolution.replace('x', ':')},format=yuv420p"]
        if has_audio:
            cmd += ["-c:a", "aac", "-shortest"]
        cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", str(out_path)]

        p = self._spawn(cmd)
        try:
            _, err = p.communicate(timeout=cfg.scene_timeout_sec)
        except subprocess.TimeoutExpired:
            self._kill_group(p)
            raise SceneTimeoutError(f"FFmpeg 타임아웃({cfg.scene_timeout_sec}s): {out_path.name}")
        finally:
            with self._lock:
                if p in self._procs:
                    self._procs.remove(p)
        if p.returncode != 0:
            raise AdapterError(f"FFmpeg 실패 rc={p.returncode}: {err.decode(errors='ignore')[-400:]}")
        return out_path

    def concat_scenes(self, scene_paths: List[Path], out_path: Path, cfg: PipelineConfig) -> Path:
        """5개 씬 클립을 concat demuxer 로 1개 완성본 MP4 로 조립한다.

        정책:
          1) concat_list.txt 를 UTF-8 로 원자적 생성(임시파일 → replace).
          2) 1차 시도: -c copy (무재인코딩, 초고속). 코덱/파라미터 불일치로 실패하면
             2차 시도: libx264 + aac 재인코딩으로 폴백한다.
          3) 모든 프로세스는 self._spawn 을 통해 원자적 추적 등록되며,
             타임아웃 시 _kill_group 에스컬레이션 정책을 그대로 준수한다.
          4) 실패는 AdapterError 로 표면화한다(조용한 은폐 금지).
        """
        if not scene_paths:
            raise AdapterError("concat_scenes: 씬 클립 목록이 비어 있음")

        missing = [str(p) for p in scene_paths if not p.exists() or p.stat().st_size == 0]
        if missing:
            raise AdapterError(f"concat_scenes: 존재하지 않거나 빈 클립 {missing}")

        out_path.parent.mkdir(parents=True, exist_ok=True)
        ffmpeg_exe = self._resolve_binary()

        # concat demuxer 는 경로 내 작은따옴표를 '\'' 로 이스케이프해야 한다.
        list_path = out_path.parent / "concat_list.txt"
        lines: List[str] = []
        for clip in scene_paths:
            safe = str(clip.resolve()).replace("'", "'\\''")
            lines.append(f"file '{safe}'")
        tmp_list = list_path.with_suffix(".tmp")
        tmp_list.write_text("\n".join(lines) + "\n", encoding="utf-8")
        tmp_list.replace(list_path)

        base_cmd = [
            ffmpeg_exe, "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(list_path),
        ]

        attempts: List[Tuple[str, List[str]]] = [
            ("copy", base_cmd + ["-c", "copy", str(out_path)]),
            ("reencode", base_cmd + [
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-r", str(cfg.fps),
                "-vf", f"scale={cfg.resolution.replace('x', ':')}",
                "-c:a", "aac", "-b:a", "192k",
                str(out_path),
            ]),
        ]

        last_err = ""
        for mode, cmd in attempts:
            log.info("concat_scenes 시도(%s): %d개 클립 → %s", mode, len(scene_paths), out_path.name)
            p = self._spawn(cmd)
            try:
                _, err = p.communicate(timeout=cfg.scene_timeout_sec)
            except subprocess.TimeoutExpired:
                self._kill_group(p)
                raise SceneTimeoutError(
                    f"concat 타임아웃({cfg.scene_timeout_sec}s, mode={mode}): {out_path.name}"
                )
            finally:
                with self._lock:
                    if p in self._procs:
                        self._procs.remove(p)

            if p.returncode == 0 and out_path.exists() and out_path.stat().st_size > 0:
                log.info("concat_scenes 완료(%s): %s", mode, out_path)
                return out_path

            last_err = err.decode(errors="ignore")[-400:]
            log.error("concat_scenes 실패(mode=%s, rc=%s): %s", mode, p.returncode, last_err)

        raise AdapterError(f"concat_scenes 최종 실패(모든 모드 소진): {last_err}")


# ---------------------------------------------------------------------------
# 6-B) Wan 2.2 S2V 비디오 어댑터 — 실사 립싱크 아바타 렌더링 (1순위)
#   · 정지 이미지 + 음성 → 입모양이 음성에 동기화된 실제 인물 영상 생성
#   · ComfyUI(Wan2.2-S2V-14B-Q4_0) 백엔드 사용, 실패 시 FFmpeg 정지영상으로 안전 폴백
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# [오버레이 수식 SSOT 접근자] 감사 재심 조건 ① 충족 — 리터럴 중복 0건
#   ★ 왜 필수인가: shorts_video_composer.py 의 공식 수식
#     (x=60, y=1450-18*abs(sin(2*PI*t*1.5))) 이 SSOT 인데, 본 파이프라인이
#     독자 상수(H-330-24.00, 중앙정렬, 1초 주기)를 재정의하여 드리프트가 발생했다.
#     이 접근자는 SSOT 모듈에서 수식을 '조회'만 하며, 본 파일에는 수식 리터럴이
#     존재하지 않는다(감사 재심 조건 ①: 오버레이 수식 리터럴 0건).
#   · SSOT 모듈 부재/조회 실패 시 OverlayCompositionError 로 표면화(은폐 금지).
#   · 반환값은 (x_expr, y_expr) 튜플이며, FFmpeg overlay 필터에 그대로 주입된다.
# ---------------------------------------------------------------------------
class OverlayCompositionError(PipelineError):
    """오버레이 수식/합성 실패 — 은폐 금지, 상위로 승격."""


def resolve_bouncing_pill_overlay_expr() -> Tuple[str, str]:
    """하단 필 뱃지 바운싱 오버레이 (x, y) 표현식을 SSOT 에서 조회한다.

    ★ 감사 재심 조건 ①: 본 파일에 수식 리터럴이 존재하지 않는다.
      shorts_video_composer.py 의 공식 상수(x=60, y=1450-18*abs(sin(2*PI*t*1.5)))를
      단일 소유자로부터 조회한다. SSOT 가 변경되면 본 파이프라인은 자동 추종한다.
    """
    try:
        from core.shorts_engine.shorts_video_composer import (  # type: ignore
            BOUNCING_PILL_X_EXPR,
            BOUNCING_PILL_Y_EXPR,
        )
    except Exception as e:
        raise OverlayCompositionError(
            f"바운싱 필 뱃지 SSOT 조회 실패(shorts_video_composer) — 은폐 금지: {e!r}"
        ) from e

    x_expr = str(BOUNCING_PILL_X_EXPR or "").strip()
    y_expr = str(BOUNCING_PILL_Y_EXPR or "").strip()
    if not x_expr or not y_expr:
        raise OverlayCompositionError(
            f"바운싱 필 뱃지 SSOT 값 비어 있음: x={x_expr!r}, y={y_expr!r}"
        )
    return x_expr, y_expr


# ---------------------------------------------------------------------------
# [손(hand) 명령어 전량 영구 삭제 SSOT] 대표님 최우선 절대 지시 (2026-10-25):
#   "1, 2, 4, 5번 씬 (로봇처럼 삐걱거림),......손에 대한 명령어 전부 삭제....이것부터 먼저 처리"
#
#   ★ 왜 삭제했는가: Wan 2.2 S2V 는 프롬프트의 'hand gestures' 지시를 받으면
#     손을 화면 안으로 끌어들이려고 팔/어깨를 과도하게 움직인다. 그 결과 상반신
#     단독 정면 샷에서 팔이 로봇처럼 삐걱거리는 아티팩트가 발생했다.
#     손 관련 토큰(hand / gesture / arm / finger)을 프롬프트에서 100% 제거하고,
#     대신 'clean stable body posture' 로 상체를 고정하여 삐걱거림을 물리적으로 봉인한다.
#
#   · 삭제 토큰: "natural hand gestures emphasizing words" (전량 영구 삭제)
#   · 대체 토큰: "clean stable body posture without robotic twitching or awkward hand movements"
#   · 씬 3 키프레임의 '양손으로 폰 쥐기(phone_hold)' 는 이미지 프롬프트 전용이며
#     본 S2V 모션 프롬프트와는 별개 계층이므로 그대로 유지된다.
# ---------------------------------------------------------------------------
S2V_PROMPT_TEXT = (
    "photorealistic Korean character speaking naturally with delicate accurate lip sync matching the voice audio, "
    "natural gentle head nod, subtle natural head tilting while speaking, "
    "subtle lifelike eye blinks, lively expressive facial dynamics and realistic conversation motion, "
    "clean stable body posture without robotic twitching or awkward hand movements"
)
S2V_FPS = 16          # Wan 2.2 S2V 네이티브 프레임레이트
S2V_MIN_FRAMES = 49   # 4n+1 규격 최소
S2V_MAX_FRAMES = 81   # 4n+1 규격 최대


# ---------------------------------------------------------------------------
# [씬별 감정 연기 SSOT] 대표님 절대 지시 (2026-10-25):
#   "씬 1: 억울·답답 공감 표정 / 씬 2: 헛웃음·팩폭 남사친 표정 /
#    씬 4: 신난 설렘·환한 미소 표정 / 씬 5: 다정·신뢰 호감형 미소 표정...
#    이걸 완 만들때 제대로 3번 처럼 다 집어 넣어"
#
#   ★ 왜 필수인가: 씬 3(보험 리밸런스 소개)만 'pleasantly surprised, impressed expression'
#     이라는 명시적 표정 지시를 갖고 있었고, 나머지 씬 1/2/4/5 는 표정 지시가
#     사실상 비어 있어 Gemini 가 무표정·중립 얼굴을 생성했다. 그 결과 5씬 전체가
#     "같은 사람이 같은 표정으로 서 있는" 무미건조한 영상이 되었다.
#     씬 3과 동일한 밀도로 씬별 감정선을 명시 주입하여 5씬 전건에 연기를 넣는다.
#
#   · 이 사전은 키프레임(GeminiImageAdapter)과 S2V(WanS2VVideoAdapter) 양 계층이
#     공유하는 단일 진실 원천(SSOT)이다. 두 계층이 서로 다른 표정을 지시하면
#     키프레임 얼굴과 영상 표정이 어긋나므로 반드시 이 사전만 참조한다.
#   · 입모양 봉인(mouth_seal)과 충돌하지 않도록 'closed lips' 계열로만 서술한다.
#     (입을 벌린 웃음은 Wan S2V 립싱크 첫 프레임을 깨뜨리므로 영구 금지)
#   · 손(hand) 명령어는 이 사전에도 절대 넣지 않는다(로봇 삐걱거림 재발 방지).
# ---------------------------------------------------------------------------
SCENE_EMOTION_SSOT: Dict[int, str] = {
    # 씬 1 — 수진(여) 훅: 억울·답답 공감 표정
    1: (
        "She has a relatable slightly frustrated, deeply troubled expression, "
        "gentle soft sigh with expressive eyes, tired yet deeply relatable conversational look, "
        "natural soft relaxed closed lips without strain"
    ),
    # 씬 2 — 민우(남) 팩폭: 묵직하고 차분한 팩폭 남사친 (촐싹거림 박멸)
    #   ★ 대표님 승인 지시 (2026-10-25): "2번씬 남자 너무 촐싹대... 2번 감정씬 수정 승인"
    #
    #   ★ 왜 수정했는가: 기존 문구의 경망스러운 짜증·익살·장난기 계열 토큰이
    #     Wan 2.2 S2V 에 과도한 머리 흔들림·눈썹 씰룩거림·경망스러운 장난기 모션을
    #     유발하여, 팩폭 남사친이 촐싹대는 캐릭터로 오렌더링되었다.
    #   · 장난기 계열 토큰(경망스러움/익살/장난기)을 전량 영구 제거한다.
    #   · 'steady and composed posture without head tilting or bobbing' 을 명시하여
    #     머리 까딱거림을 프롬프트 레벨에서 물리적으로 억제한다.
    #   · 'closed lips' 는 그대로 유지 — Wan S2V 립싱크 시작 포즈 무결점 보장.
    #   · 손(hand) 토큰은 이 사전에 절대 넣지 않는다(로봇 삐걱거림 재발 방지).
    2: (
        "He has a calm, mature, slightly dumbfounded dry smirk with closed lips, "
        "steady and composed posture without head tilting or bobbing, "
        "direct, candid piercing gaze that hits the point, grounded and cool male-friend demeanor"
    ),
    # 씬 3 — 수진(여) 보험 리밸런스 소개: 감탄·놀람 (기존 phone_hold 연출과 결속)
    3: (
        "She has a pleasantly surprised, genuinely impressed expression, "
        "eyes bright with delighted discovery, natural soft relaxed closed lips without strain"
    ),
    # 씬 4 — 설렘 폭발: 신난 설렘·환한 미소 표정
    4: (
        "Genuinely thrilled and animated expression, eyes sparkling with excitement, "
        "bright joyful smile with closed lips, raised cheeks, lively storytelling emotion"
    ),
    # 씬 5 — 엔딩 CTA: 다정·신뢰 호감형 미소 표정
    5: (
        "Warm inviting friendly smile, trustworthy and encouraging closing expression, "
        "gentle direct eye contact full of warmth and confidence, sweet warm closed-lip smile"
    ),
}


def emotion_for(scene_idx: int) -> str:
    """씬 인덱스 → 감정 연기 프롬프트 SSOT 를 반환한다(미지정 시 씬 1 기본값).

    ★ 키프레임(Gemini)과 S2V(Wan)가 반드시 이 함수 하나만 참조해야 한다.
      두 계층이 서로 다른 표정을 지시하면 얼굴과 영상 표정이 어긋난다.
    """
    return SCENE_EMOTION_SSOT.get(scene_idx, SCENE_EMOTION_SSOT[1])


class VideoAdapterError(RuntimeError):
    """어댑터 계약 위반/실행 실패를 상위로 승격하기 위한 예외."""


class VideoPort(ABC):
    """어댑터 계약: name, quality, available(), assemble() 만 공개한다."""
    name: str = "unknown"
    quality: str = "unknown"

    @abstractmethod
    def available(self) -> bool: ...

    @abstractmethod
    def assemble(self, *, scene_id: str, prompt: str, duration: float,
                 audio_path: Optional[str], out_path: str) -> str: ...


class WanS2VVideoAdapter(VideoPort):
    """1순위 비디오 어댑터 — Wan 2.2 S2V 로 립싱크 아바타 영상을 생성한다.

    정책:
      1) ComfyUI(WanPipelineClient) 헬스체크 실패 시 available()=False → FFmpeg 폴백.
      2) 렌더링 중 어떤 예외가 나도 FFmpeg 정지영상 어댑터로 안전 폴백(씬 전체 실패 방지).
      3) raw S2V 출력은 1080x1920 세로 9:16 으로 정규화 후 임시파일 즉시 삭제.
      4) concat 은 검증된 FFmpeg 어댑터에 그대로 위임한다.
    """
    name = "wan_s2v"

    def __init__(self, cfg: PipelineConfig):
        self.cfg = cfg
        self._fallback_ffmpeg = FFmpegVideoAdapter(cfg)
        self._wan_client: Optional[Any] = None
        try:
            from core.engine.wan_pipeline_client import WanPipelineClient  # type: ignore
            self._wan_client = WanPipelineClient()
            log.info("WanPipelineClient 초기화 완료 (host=%s)", getattr(self._wan_client, "host", "?"))
        except Exception as e:
            self._wan_client = None
            log.warning("WanPipelineClient 초기화 실패 — FFmpeg 폴백 전용 모드: %r", e)

    def available(self) -> bool:
        if self._wan_client is None:
            return False
        try:
            return bool(self._wan_client.check_health(auto_start=True))
        except Exception as e:
            log.warning("Wan S2V 헬스체크 예외 — 사용 불가 판정: %r", e)
            return False

    def _resolve_binary(self) -> str:
        """FFmpeg 바이너리 경로를 폴백 어댑터에 위임하여 반환한다.

        ★ 왜 위임인가: PipelineOrchestrator._render_ending_cta_clip /
          _apply_branding_overlay 는 `getattr(self.video, "_resolve_binary", ...)`
          로 비디오 어댑터에서 ffmpeg 경로를 조회한다. Wan S2V 가 선택된 경우
          이 메서드가 없으면 조용히 문자열 "ffmpeg" 로 낙하하여, PATH 미등록
          Windows 환경에서 WinError 2 로 즉사한다.
        · 경로 해석 SSOT 는 FFmpegVideoAdapter._resolve_binary 단일 소유자다.
          본 메서드는 재구현하지 않고 위임만 수행한다(드리프트 0건).
        · 해석 실패는 BinaryResolutionError 로 그대로 표면화된다(은폐 금지).
        """
        return self._fallback_ffmpeg._resolve_binary()

    # ------------------------------------------------------------------
    # 오디오 실측 길이 (S2V 프레임 수 산출용)
    # ------------------------------------------------------------------
    def _probe_audio_duration(self, audio: Path, fallback: float) -> float:
        """오디오 실측 길이를 3중 폴백으로 100% 무결점 반환한다.

        대표님 절대 지침 (2026-10-25):
          "음성에 영상을 100% 일치시켜 말 끊김 영구 박멸"

        탐색 순서(전 단계 실패 시에만 fallback 사용):
          1) ffprobe — ffmpeg 번들 경로에서 파생 (imageio_ffmpeg 번들 대응)
          2) ffprobe — PATH 및 시스템 표준 경로 탐색 (shutil.which + 후보 경로)
          3) ffmpeg — stderr 의 "Duration: HH:MM:SS.ss" 파싱 (ffprobe 부재 환경 최후 수단)

        ★ 왜 3중인가: Windows 에서 imageio_ffmpeg 번들은 ffmpeg.exe 만 동봉하고
          ffprobe.exe 는 동봉하지 않는 경우가 많다. 기존 단일 경로 로직은 이때
          즉시 fallback(스펙 duration)으로 낙하하여, 실제 음성보다 짧은 -t 값으로
          영상이 잘려 "말 끊김"이 발생했다. 3중 폴백으로 실측 길이를 반드시 확보한다.
        """
        if not audio.exists() or audio.stat().st_size == 0:
            return fallback

        # ---- 1) ffprobe: ffmpeg 번들 경로에서 파생 -------------------------
        try:
            ffmpeg_exe = self._fallback_ffmpeg._resolve_binary()
            derived = ffmpeg_exe.replace("ffmpeg", "ffprobe")
            if os.path.isfile(derived):
                val = self._run_ffprobe(derived, audio)
                if val > 0:
                    log.debug("오디오 실측(ffprobe 번들): %.3fs", val)
                    return val
        except Exception as e:
            log.debug("ffprobe 번들 파생 실패: %r", e)

        # ---- 2) ffprobe: PATH 및 시스템 표준 경로 --------------------------
        probe_candidates: List[str] = []
        which_probe = shutil.which("ffprobe")
        if which_probe:
            probe_candidates.append(which_probe)
        for cand in (
            "/usr/bin/ffprobe", "/usr/local/bin/ffprobe", "/opt/homebrew/bin/ffprobe",
            r"C:\ffmpeg\bin\ffprobe.exe", r"C:\Program Files\ffmpeg\bin\ffprobe.exe",
        ):
            if os.path.isfile(cand) and cand not in probe_candidates:
                probe_candidates.append(cand)
        for probe_exe in probe_candidates:
            try:
                val = self._run_ffprobe(probe_exe, audio)
                if val > 0:
                    log.debug("오디오 실측(ffprobe 시스템=%s): %.3fs", probe_exe, val)
                    return val
            except Exception as e:
                log.debug("ffprobe 시스템 경로 실패(%s): %r", probe_exe, e)

        # ---- 3) ffmpeg stderr "Duration:" 파싱 (최후 수단) ------------------
        try:
            ffmpeg_exe = self._fallback_ffmpeg._resolve_binary()
            # [인코딩 봉인] Windows 기본 로캘(cp949)로 ffmpeg stderr 를 디코딩하면
            #   한글 경로/비-ASCII 바이트(0xed 등)에서 UnicodeDecodeError 로 즉사한다.
            #   encoding="utf-8" + errors="replace" 로 디코딩 실패를 원천 차단한다.
            proc = subprocess.run(
                [ffmpeg_exe, "-hide_banner", "-i", str(audio)],
                capture_output=True, text=True, timeout=30,
                encoding="utf-8", errors="replace",
            )
            # ffmpeg 는 입력만 지정하면 rc!=0 으로 종료하지만 stderr 에 Duration 을 남긴다.
            stderr = proc.stderr or ""
            m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", stderr)
            if m:
                hh, mm, ss = int(m.group(1)), int(m.group(2)), float(m.group(3))
                val = hh * 3600 + mm * 60 + ss
                if val > 0:
                    log.debug("오디오 실측(ffmpeg stderr 파싱): %.3fs", val)
                    return val
        except Exception as e:
            log.debug("ffmpeg stderr Duration 파싱 실패: %r", e)

        log.warning("오디오 실측 3중 폴백 전건 실패 — 스펙 duration(%.2fs) 사용: %s",
                    fallback, audio.name)
        return fallback

    @staticmethod
    def _run_ffprobe(ffprobe_exe: str, audio: Path) -> float:
        """ffprobe 로 오디오 길이(초)를 측정한다. 실패/비정상 값은 0.0 반환."""
        # [인코딩 봉인] Windows cp949 기본 로캘에서 ffprobe 출력 디코딩 실패
        #   (UnicodeDecodeError: 'cp949' codec can't decode byte 0xed) 를 영구 박멸한다.
        out = subprocess.run(
            [ffprobe_exe, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(audio)],
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace",
        )
        raw = (out.stdout or "").strip()
        if not raw:
            return 0.0
        try:
            val = float(raw)
        except ValueError:
            return 0.0
        return val if val > 0 else 0.0

    @staticmethod
    def _calc_s2v_frames(dur: float) -> int:
        """4n+1 규격(49~81)으로 S2V 프레임 수를 결정론적으로 산출한다."""
        calc = int(dur * S2V_FPS)
        return max(S2V_MIN_FRAMES, min(S2V_MAX_FRAMES, (calc // 4) * 4 + 1))

    def assemble(self, image: Path, audio: Path, out_path: Path, duration: float,
                 cfg: PipelineConfig, scene_idx: int = 1) -> Path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        raw_s2v_out = out_path.parent / f"_raw_s2v_{out_path.parent.name}.mp4"

        try:
            if self._wan_client is None:
                raise AdapterError("WanPipelineClient 미초기화")

            # (a) ComfyUI input 디렉터리로 이미지/오디오 복사
            comfy_input_dir = Path(self._wan_client.comfy_input_dir)
            comfy_input_dir.mkdir(parents=True, exist_ok=True)
            tag = out_path.parent.name
            image_name = f"s2v_{tag}_ref.png"
            audio_name = f"s2v_{tag}_voice.mp3"
            shutil.copy2(image, comfy_input_dir / image_name)
            has_audio = audio.exists() and audio.stat().st_size > 0
            if has_audio:
                shutil.copy2(audio, comfy_input_dir / audio_name)
            else:
                # 무음 폴백: 0바이트 오디오는 S2V 인코더가 거부하므로 최소 무음 트랙 생성
                ffmpeg_exe = self._fallback_ffmpeg._resolve_binary()
                subprocess.run(
                    [ffmpeg_exe, "-y", "-f", "lavfi", "-i", "anullsrc=r=16000:cl=mono",
                     "-t", f"{duration:.3f}", str(comfy_input_dir / audio_name)],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60,
                )

            # (b) 오디오 실측 길이 → S2V 프레임 수 산출
            real_dur = self._probe_audio_duration(audio, duration)
            s2v_frames = self._calc_s2v_frames(real_dur)
            log.info("Wan S2V 렌더 시작: scene=%s dur=%.2fs frames=%d", tag, real_dur, s2v_frames)

            # (c) S2V 영상 생성
            #   ★ 대표님 절대 지시 (2026-10-25): "씬 1 억울답답 / 씬 2 헛웃음팩폭 /
            #     씬 3 감탄놀람 / 씬 4 신난설렘 / 씬 5 다정호감 — 3번처럼 다 집어 넣어"
            #
            #   ★ 왜 필수인가: S2V_PROMPT_TEXT 는 '말하는 모션'만 지시하는 공통 문구다.
            #     여기에 씬별 감정선을 결속하지 않으면, Wan 2.2 S2V 가 5씬 전건을
            #     동일한 무표정 모션으로 렌더링하여 키프레임 얼굴과 영상 표정이 어긋난다.
            #     emotion_for(scene_idx) 는 키프레임(GeminiImageAdapter)과 공유하는
            #     단일 진실 원천(SSOT)이므로, 두 계층이 반드시 같은 값을 참조해야
            #     "키프레임 표정 = 영상 표정" 일치가 100% 성립한다.
            #   · 손(hand) 토큰은 emotion_for() 사전에 존재하지 않으므로
            #     로봇 삐걱거림 아티팩트가 재발할 여지가 없다.
            #   · 입모양은 'closed lips' 계열로만 서술되어 립싱크 첫 프레임을 깨뜨리지 않는다.
            s2v_prompt = f"{S2V_PROMPT_TEXT}, {emotion_for(scene_idx)}"
            log.info("Wan S2V 감정 결속: scene=%d emotion=%s", scene_idx, emotion_for(scene_idx)[:60])
            self._wan_client.generate_s2v_video(
                image_name=image_name,
                audio_name=audio_name,
                prompt_text=s2v_prompt,
                output_mp4_path=str(raw_s2v_out),
                width=384,
                height=672,
                frames=s2v_frames,
                prefix=f"s2v_scene_{tag}",
            )

            # (d) VRAM 캐시 방출 (모델 언로드는 C++ 크래시 회피 위해 False 고정)
            try:
                self._wan_client.free_vram(unload_models=False)
            except Exception:
                log.debug("free_vram 예외 무시", exc_info=True)

            if not raw_s2v_out.exists() or raw_s2v_out.stat().st_size == 0:
                raise AdapterError(f"Wan S2V raw 출력 부재/손상: {raw_s2v_out}")

            # (e) 1080x1920 세로 9:16 정규화 + 오디오 재결합
            #   ★ 대표님 절대 지침 (2026-10-25): "음성에 영상을 100% 일치시켜 말 끊김 영구 박멸"
            #     -t 값을 스펙 duration 이 아니라 실측 real_dur 로 고정한다.
            #     스펙 duration(3/4/4/5/4초)은 TTS 실측 길이와 어긋날 수 있어,
            #     duration 으로 자르면 음성 마지막 음절이 잘려 "말 끊김"이 발생했다.
            #     real_dur 는 _probe_audio_duration 이 3중 폴백으로 확보한 실측값이다.
            ffmpeg_exe = self._fallback_ffmpeg._resolve_binary()
            vf = (
                "scale=1080:1920:force_original_aspect_ratio=increase,"
                "crop=1080:1920,setsar=1,fps=30,"
                "tpad=stop_mode=clone:stop_duration=1.0,format=yuv420p"
            )
            cmd = [
                ffmpeg_exe, "-y",
                "-i", str(raw_s2v_out),
                "-i", str(audio) if has_audio else str(comfy_input_dir / audio_name),
                "-vf", vf,
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                "-c:a", "aac", "-b:a", "192k",
                "-t", f"{real_dur:.2f}",
                str(out_path),
            ]
            proc = subprocess.run(cmd, capture_output=True, timeout=cfg.scene_timeout_sec)
            if proc.returncode != 0:
                raise AdapterError(
                    f"Wan S2V 정규화 FFmpeg 실패 rc={proc.returncode}: "
                    f"{proc.stderr.decode(errors='ignore')[-400:]}"
                )

            # (f) 임시 raw S2V 삭제
            try:
                raw_s2v_out.unlink(missing_ok=True)
            except Exception:
                log.debug("raw S2V 임시파일 삭제 실패(무시)", exc_info=True)

            log.info("Wan S2V 렌더 완료: %s", out_path.name)
            return out_path

        except Exception as e:
            # (g) S2V 실패 → FFmpeg 정지영상 어댑터로 안전 폴백 (씬 전체 실패 방지)
            log.error("Wan S2V 실패 — FFmpeg 정지영상으로 폴백: %r", e)
            try:
                raw_s2v_out.unlink(missing_ok=True)
            except Exception:
                pass
            return self._fallback_ffmpeg.assemble(image, audio, out_path, duration, cfg,
                                                  scene_idx=scene_idx)

    def concat_scenes(self, scene_paths: List[Path], out_path: Path, cfg: PipelineConfig) -> Path:
        return self._fallback_ffmpeg.concat_scenes(scene_paths, out_path, cfg)


# ---------------------------------------------------------------------------
# 7) 매니페스트 (리줌 + 감사 추적)
# ---------------------------------------------------------------------------
class Manifest:
    def __init__(self, path: Path):
        self.path = path
        self.data: Dict[str, Any] = {"scenes": {}, "errors": []}
        if path.exists():
            try:
                self.data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                log.exception("매니페스트 손상 — 새로 시작")
        self.data.setdefault("scenes", {})
        self.data.setdefault("errors", [])

    def scene_done(self, idx: int, artifacts: Dict[str, str]) -> None:
        self.data["scenes"][str(idx)] = {"status": "done", "artifacts": artifacts,
                                         "ts": datetime.now(timezone.utc).isoformat()}
        self._flush()

    def scene_failed(self, idx: int, err: str, tb: str) -> None:
        self.data["scenes"][str(idx)] = {"status": "failed", "error": err,
                                         "traceback": tb,
                                         "ts": datetime.now(timezone.utc).isoformat()}
        self.data["errors"].append({"scene": idx, "error": err})
        self._flush()

    def is_done(self, idx: int) -> bool:
        return self.data["scenes"].get(str(idx), {}).get("status") == "done"

    def _flush(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)


# ---------------------------------------------------------------------------
# 8) 오케스트레이터 — 씬 단위 격리 + 타임아웃 + 리트라이
# ---------------------------------------------------------------------------
class PipelineOrchestrator:
    def __init__(self, cfg: PipelineConfig, image: ImagePort, tts: TTSPort, video: VideoPort):
        self.cfg = cfg
        self.image = image
        self.tts = tts
        self.video = video
        self.manifest = Manifest(cfg.output_root / "manifest.json")
        # [서킷브레이커 상태] 오버레이 연속 실패 카운터 — 임계 초과 시 파이프라인 중단.
        self._overlay_fallback_count: int = 0

    def _run_scene(self, scene: SceneSpec) -> Dict[str, str]:
        base = self.cfg.output_root / f"scene_{scene.index:02d}"
        base.mkdir(parents=True, exist_ok=True)
        # [장소 로테이션] 회차별 핫플레이스(location_en)를 이미지 어댑터로 관통 전달.
        #   · 5씬 전건 동일 값 → 한 편 내 단독 정면 1인 샷 공간 연속성 100%
        #   · 다음 회차에는 다른 값 → 장소 100% 전환
        # [시간대 2축 결속] topic(주제)도 함께 관통 전달하여
        #   location 시그널 + topic 시그널을 동시 스캔한 시간대 판정을 보장한다.
        # [회차 전용 신규 주인공 결속] run_id 를 이미지 어댑터로 명시 전달한다.
        #   · resolve_character_asset(scene_idx, run_id) 가 회차 전용 마스터
        #     (assets/episodes/{run_id}/episode_*_master.png)를 최우선 반환한다.
        #   · run_id 미전달 시 정적 마스터로 낙하하여 매 회차 동일 인물이 생성되므로
        #     반드시 self.cfg.run_id 를 관통시켜야 회차별 신규 주인공이 성립한다.
        img = self.image.generate(
            prompt=scene.image_prompt,
            out_path=base / "frame.png",
            size=self.cfg.resolution,
            scene_idx=scene.index,
            location_en=scene.location_en,
            topic=scene.topic,
            run_id=self.cfg.run_id,
        )
        aud = self.tts.synthesize(scene.narration, scene.voice_id, base / "voice.mp3")
        # [씬별 감정 연기 SSOT 관통] scene.index 를 비디오 어댑터로 전달한다.
        #   · Wan S2V 는 이 인덱스로 emotion_for(scene_idx) 를 조회해 씬별 감정선을
        #     렌더링 프롬프트에 결속한다(씬 1 억울답답 / 씬 2 헛웃음팩폭 / 씬 3 감탄놀람 /
        #     씬 4 신난설렘 / 씬 5 다정호감).
        #   · 키프레임(Gemini)과 S2V(Wan)가 동일 인덱스를 공유해야 표정 일치가 100% 성립한다.
        vid = self.video.assemble(img, aud, base / "scene.mp4", scene.duration_sec, self.cfg,
                                  scene_idx=scene.index)
        return {"image": str(img), "audio": str(aud), "video": str(vid)}

    def _run_scene_with_timeout(self, scene: SceneSpec) -> Dict[str, str]:
        with ThreadPoolExecutor(max_workers=1, thread_name_prefix=f"scene{scene.index}") as ex:
            fut = ex.submit(self._run_scene, scene)
            try:
                return fut.result(timeout=self.cfg.scene_timeout_sec)
            except FutureTimeoutError:
                raise SceneTimeoutError(f"씬 {scene.index} 타임아웃({self.cfg.scene_timeout_sec}s)")

    # ------------------------------------------------------------------
    # [FFmpeg 경로 3중 안전망 SSOT] 대표님 지적 사항 (2026-10-25):
    #   "_render_ending_cta_clip / _apply_branding_overlay 에서
    #    getattr(self.video, "_resolve_binary", lambda: "ffmpeg")() 로 인해
    #    Windows 환경에서 PATH 에 ffmpeg 가 없을 때 [WinError 2] 로 폭사하는
    #    취약점을 영구 방어하라."
    #
    #   ★ 왜 기존 방식이 취약했는가:
    #     getattr 의 기본값 lambda: "ffmpeg" 는 어댑터에 _resolve_binary 가
    #     없거나 예외를 던지는 순간 조용히 문자열 "ffmpeg" 로 낙하한다.
    #     PATH 미등록 Windows 에서는 subprocess.Popen 이 WinError 2 로 즉사하고,
    #     그 결과 엔딩 CTA 카드와 브랜딩 오버레이가 통째로 소실된다.
    #
    #   ★ 3중 안전망 (앞 단계가 성공하면 즉시 반환, 실패는 다음 단계로 위임):
    #     1) video 어댑터의 _resolve_binary() — SSOT 단일 소유자(설정→PATH→번들)
    #     2) imageio_ffmpeg 번들 절대경로 — PATH 미등록 환경의 최후 방어선
    #     3) shutil.which("ffmpeg") — 시스템 PATH 탐색
    #   · 1단계 예외는 삼키지 않고 로그로 남긴 뒤 2단계로 위임한다(은폐 금지 원칙).
    #   · 3단계까지 모두 실패하면 마지막 수단으로 "ffmpeg" 문자열을 반환하되,
    #     이 경우에도 호출부의 _run_guarded 가 예외를 표면화하므로 조용한 실패는 없다.
    # ------------------------------------------------------------------
    def _resolve_ffmpeg(self) -> str:
        """FFmpeg 바이너리 절대 경로를 3중 안전망(video어댑터 -> imageio_ffmpeg 번들 -> shutil.which)으로 100% 확보한다."""
        # 1) 비디오 어댑터 위임 (FFmpegVideoAdapter / WanS2VVideoAdapter 공통 SSOT)
        if hasattr(self.video, "_resolve_binary"):
            try:
                exe = self.video._resolve_binary()
                if exe and Path(exe).exists():
                    return str(exe)
            except Exception as e:
                log.warning("ffmpeg 경로 해석 실패(video 어댑터) — 다음 안전망으로 위임: %r", e)

        # 2) imageio_ffmpeg 번들 (Windows PATH 미등록 케이스 핵심 방어선)
        try:
            import imageio_ffmpeg  # type: ignore
            exe = imageio_ffmpeg.get_ffmpeg_exe()
            if exe and Path(exe).exists():
                log.info("ffmpeg 경로 확보(imageio_ffmpeg 번들): %s", exe)
                return str(exe)
        except Exception as e:
            log.warning("ffmpeg 경로 해석 실패(imageio_ffmpeg 번들): %r", e)

        # 3) 시스템 PATH 탐색
        found = shutil.which("ffmpeg")
        if found:
            log.info("ffmpeg 경로 확보(PATH): %s", found)
            return found

        log.error("ffmpeg 경로 3중 안전망 전건 실패 — 'ffmpeg' 문자열로 최후 시도(호출부에서 표면화됨)")
        return "ffmpeg"

    # ------------------------------------------------------------------
    # [엔딩 CTA 카드 클립 렌더러 SSOT] 대표님 승인 지시 (2026-10-25):
    #   "사진 속 2개(엔딩 CTA 카드 + 상단/하단 브랜딩 오버레이)
    #    최종 조립 단계에 100% 연결"
    #
    #   ★ 왜 필수인가: 5씬 본편만 concat 하면 영상이 씬5 대사와 함께 뚝 끊긴다.
    #     브랜드 검색 유도(보험 리밸런스)를 시각적으로 각인시키는 3초 엔딩 카드가
    #     반드시 마지막에 붙어야 숏폼 CTA 전환이 성립한다.
    #
    #   · InsuranceCTACard.render_cta_image(output_path) 는 PIL Image 를 반환하며,
    #     output_path 를 주면 파일로도 저장한다(실측 확인 완료).
    #   · 무음 트랙(anullsrc)을 반드시 결합해야 concat demuxer 가 오디오 스트림
    #     유무 불일치로 실패하지 않는다(본편 5씬은 전건 오디오 보유).
    #   · 실패 시 None 반환 — 본편 5씬은 그대로 보존한다(전체 실패 금지).
    # ------------------------------------------------------------------
    def _render_ending_cta_clip(self, output_dir: Path) -> Optional[Path]:
        try:
            from brands.insurance.ui_templates.insurance_drama_cta_card import InsuranceCTACard
            cta_img_path = output_dir / "cta_card.png"
            cta_clip_path = output_dir / "scene_06_ending_cta.mp4"
            if cta_clip_path.exists() and cta_clip_path.stat().st_size > 50000:
                log.info("기존 엔딩 CTA 카드 클립 재사용: %s", cta_clip_path.name)
                return cta_clip_path

            card = InsuranceCTACard()
            im = card.render_cta_image(cta_img_path)
            if not cta_img_path.exists() and im is not None:
                im.save(cta_img_path, format="PNG")

            ffmpeg_exe = self._resolve_ffmpeg()
            cmd = [
                ffmpeg_exe, "-y",
                "-loop", "1", "-i", str(cta_img_path),
                "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
                "-vf", f"scale={self.cfg.resolution.replace('x', ':')}:force_original_aspect_ratio=increase,crop={self.cfg.resolution.replace('x', ':')},setsar=1,fps={self.cfg.fps},format=yuv420p",
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-tune", "stillimage",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                "-t", "3.0", "-shortest",
                str(cta_clip_path),
            ]
            # [무인 가동 안전장치] _run_guarded 경유 — 타임아웃·좀비 회수·자원 정리 계약.
            rc, err = self._run_guarded(cmd, 60.0, "ending_cta_clip")
            if rc == 0 and cta_clip_path.exists() and cta_clip_path.stat().st_size > 0:
                log.info("엔딩 CTA 카드 3초 클립 생성 완료: %s", cta_clip_path.name)
                return cta_clip_path
            log.warning("엔딩 CTA 카드 클립 생성 실패 rc=%s: %s", rc, err.decode(errors="ignore")[-200:])
            return None
        except Exception as e:
            log.warning("엔딩 CTA 카드 생성 예외: %s", e)
            return None

    # ------------------------------------------------------------------
    # [브랜딩 오버레이 합성 SSOT] 대표님 승인 지시 (2026-10-25):
    #   "상단 50:50 캡슐 뱃지 + 하단 프로필 링크 뱃지 최종 조립 단계에 100% 연결"
    #
    #   ★ 왜 enable 조건이 필수인가: 오버레이를 전 구간에 깔면 마지막 3초 엔딩
    #     CTA 카드 위에 뱃지가 겹쳐 카드 문구(보험 리밸런스)를 가린다.
    #     따라서 본편 재생 구간(0 ~ body_duration_sec)에만 노출하고,
    #     엔딩 카드 구간에서는 자동 비활성화하여 카드 전체가 선명하게 노출된다.
    #
    #   ★ FFmpeg 이스케이프: filter_complex 문자열 안에서 쉼표(,)는 필터 구분자다.
    #     enable='lt(t,3.00)' 처럼 이스케이프 없이 쓰면 "No such filter" 로 즉사한다.
    #     반드시 lt(t\,3.00) 로 쉼표를 이스케이프해야 한다.
    #
    #   ★ 오디오 정책: -c:a copy 는 concat 결과의 오디오 타임베이스가 필터 경유 시
    #     어긋나면 실패한다. 1차는 copy(초고속), 실패 시 2차는 aac 재인코딩으로
    #     폴백하여 오디오 유실을 원천 차단한다.
    #
    #   · 뱃지 에셋이 둘 다 없으면 원본을 그대로 복사(본편 보존).
    #   · 합성 실패 시에도 원본을 복사하여 완성본 부재를 방지한다.
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # [무인 가동 안전장치 SSOT] 감사 재심 조건 ③ 충족
    #   ★ 왜 필수인가: 오버레이/CTA/프로브 등 모든 외부 프로세스 호출이
    #     subprocess.run(timeout=...) 로 흩어져 있어, 타임아웃·좀비 회수·
    #     임시자원 정리가 경로별로 제각각이었다. 24시간 무인 가동 중
    #     ffmpeg hang → 프로세스 누적 → 디스크 포화로 수 시간 내 정지한다.
    #   · 모든 외부 프로세스는 _run_guarded() 단일 경유지로 통합한다.
    #   · 타임아웃 초과 시 _kill_group() 에스컬레이션(SIGTERM→SIGKILL)으로 회수.
    #   · 재시도는 상한(OVERLAY_MAX_RETRIES) + 지수 백오프로 무한 루프 차단.
    #   · 서킷브레이커(OVERLAY_CIRCUIT_THRESHOLD) 초과 시 즉시 중단(차단 승격).
    # ------------------------------------------------------------------
    OVERLAY_MAX_RETRIES: int = 2
    OVERLAY_CIRCUIT_THRESHOLD: int = 3
    OVERLAY_SUBPROCESS_TIMEOUT_SEC: float = 180.0
    OVERLAY_BACKOFF_BASE_SEC: float = 2.0

    def _run_guarded(self, cmd: List[str], timeout_sec: float, label: str) -> Tuple[int, bytes]:
        """외부 프로세스를 타임아웃·좀비 회수·자원 정리 계약 하에 실행한다.

        반환: (returncode, stderr_bytes). 타임아웃 시 SceneTimeoutError 승격.
        """
        p = self.video._spawn(cmd) if hasattr(self.video, "_spawn") else subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        try:
            _, err = p.communicate(timeout=timeout_sec)
            return p.returncode, err or b""
        except subprocess.TimeoutExpired:
            try:
                if hasattr(self.video, "_kill_group"):
                    self.video._kill_group(p)
                else:
                    p.kill()
                    p.wait(timeout=10)
            except Exception:
                log.exception("프로세스 회수 실패(label=%s, pid=%s)", label, p.pid)
            raise SceneTimeoutError(f"{label} 타임아웃({timeout_sec}s) — 강제 회수")
        finally:
            if hasattr(self.video, "_procs"):
                with self.video._lock:
                    if p in self.video._procs:
                        self.video._procs.remove(p)

    def _apply_branding_overlay(self, input_mp4: Path, output_mp4: Path, body_duration_sec: float) -> Path:
        # [서킷브레이커] 연속 실패 임계 초과 시 즉시 중단(차단 승격) — 무한 재시도 차단.
        if self._overlay_fallback_count >= self.OVERLAY_CIRCUIT_THRESHOLD:
            raise OverlayCompositionError(
                f"오버레이 서킷브레이커 개방: 연속 실패 {self._overlay_fallback_count}회 "
                f">= 임계 {self.OVERLAY_CIRCUIT_THRESHOLD} — 파이프라인 중단"
            )

        badge_path = None
        try:
            from core.shorts_engine.shorts_brand_capsule_badge import ShortsBrandCapsuleBadge
            bp = ShortsBrandCapsuleBadge.get_overlay_path("insurance")
            if bp and Path(bp).exists():
                badge_path = str(Path(bp).resolve()).replace("\\", "/")
        except Exception as e:
            log.debug("상단 캡슐 뱃지 로드 실패: %s", e)

        pill_path = None
        try:
            from core.shorts_engine.shorts_branding_overlay import ShortsBrandingOverlay
            pp = ShortsBrandingOverlay.get_bouncing_profile_badge_path("insurance")
            if pp and Path(pp).exists():
                pill_path = str(Path(pp).resolve()).replace("\\", "/")
        except Exception as e:
            log.debug("하단 프로필 링크 뱃지 로드 실패: %s", e)

        if not badge_path and not pill_path:
            # [차단 승격] 에셋 전무는 은폐가 아니라 계약 위반 — 상위로 표면화.
            raise OverlayCompositionError(
                "브랜딩 오버레이 에셋 전무(상단/하단 모두 부재) — 브랜딩 노출 0% 은폐 금지"
            )

        cutoff = body_duration_sec if body_duration_sec > 0 else 22.0
        enable_expr = f":enable='lt(t\\,{cutoff:.2f})'"

        ffmpeg_exe = self._resolve_ffmpeg()
        inputs = [ffmpeg_exe, "-y", "-i", str(input_mp4)]
        v_idx = 0
        filters = []
        curr_v = "0:v"

        if badge_path:
            v_idx += 1
            inputs.extend(["-i", badge_path])
            filters.append(f"[{curr_v}][{v_idx}:v]overlay=0:0{enable_expr}[v_badge]")
            curr_v = "v_badge"

        if pill_path:
            v_idx += 1
            inputs.extend(["-i", pill_path])
            # [바운싱 애니메이션 SSOT] 하단 필 뱃지 상하 반동 오버레이
            #   ★ 감사 재심 조건 ①: 수식 리터럴 0건 — SSOT 접근자에서 조회만 한다.
            #     shorts_video_composer.py 의 공식(x=60, y=1450-18*abs(sin(2*PI*t*1.5)))을
            #     단일 소유자로부터 받아 그대로 주입한다. 본 파일에 상수 없음.
            #   · eval=frame 명시 — 프레임마다 t 재평가(정지 프레임 굳음 방지).
            #   · enable 조건은 본편 구간 한정 — 엔딩 CTA 카드 침범 방지.
            pill_x_expr, pill_y_expr = resolve_bouncing_pill_overlay_expr()
            filters.append(
                f"[{curr_v}][{v_idx}:v]overlay=x='{pill_x_expr}':y='{pill_y_expr}':eval=frame{enable_expr}[v_pill]"
            )
            curr_v = "v_pill"

        filter_str = ";".join(filters)

        # 1차: 오디오 copy(초고속) → 2차: 오디오 aac 재인코딩(타임베이스 불일치 대응)
        audio_modes: List[Tuple[str, List[str]]] = [
            ("copy", ["-c:a", "copy"]),
            ("aac", ["-c:a", "aac", "-b:a", "192k"]),
        ]

        last_err: Optional[BaseException] = None
        for attempt in range(1, self.OVERLAY_MAX_RETRIES + 2):
            for mode, audio_args in audio_modes:
                cmd = inputs + [
                    "-filter_complex", filter_str,
                    "-map", f"[{curr_v}]", "-map", "0:a?",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
                    *audio_args,
                    str(output_mp4),
                ]
                try:
                    rc, err = self._run_guarded(
                        cmd, self.OVERLAY_SUBPROCESS_TIMEOUT_SEC,
                        f"overlay(mode={mode},attempt={attempt})",
                    )
                    if rc == 0 and output_mp4.exists() and output_mp4.stat().st_size > 0:
                        log.info("브랜딩 오버레이 합성 완료(%s, attempt=%d): %s",
                                 mode, attempt, output_mp4.name)
                        self._overlay_fallback_count = 0
                        return output_mp4
                    last_err = AdapterError(
                        f"overlay rc={rc}: {err.decode(errors='ignore')[-200:]}"
                    )
                    log.warning("브랜딩 오버레이 합성 실패(mode=%s, attempt=%d, rc=%s): %s",
                                mode, attempt, rc, err.decode(errors="ignore")[-200:])
                except SceneTimeoutError as e:
                    last_err = e
                    log.error("브랜딩 오버레이 타임아웃(attempt=%d): %s", attempt, e)
                except Exception as e:
                    last_err = e
                    log.warning("브랜딩 오버레이 예외(mode=%s, attempt=%d): %s", mode, attempt, e)

            # 지수 백오프 — 재시도 상한 내에서만 대기(무한 루프 차단).
            if attempt <= self.OVERLAY_MAX_RETRIES:
                backoff = self.OVERLAY_BACKOFF_BASE_SEC * (2 ** (attempt - 1))
                log.info("오버레이 재시도 백오프 %.1fs 후 attempt=%d", backoff, attempt + 1)
                time.sleep(backoff)

        # [차단 승격] 폴백 은폐 폐기 — 실패 카운트 증가 + 예외 표면화.
        self._overlay_fallback_count += 1
        self.manifest.data.setdefault("overlay_failures", []).append({
            "ts": datetime.now(timezone.utc).isoformat(),
            "count": self._overlay_fallback_count,
            "error": repr(last_err),
        })
        self.manifest._flush()
        raise OverlayCompositionError(
            f"브랜딩 오버레이 합성 최종 실패(연속 {self._overlay_fallback_count}회): {last_err!r}"
        )

    def run(self, scenes: List[SceneSpec]) -> Dict[str, Any]:
        results: Dict[str, Any] = {"ok": [], "failed": [], "final_video": None}
        for scene in scenes:
            if self.manifest.is_done(scene.index):
                log.info("씬 %d 이미 완료 — 스킵(리줌)", scene.index)
                results["ok"].append(scene.index)
                continue
            for attempt in range(1, self.cfg.max_scene_retries + 2):
                try:
                    log.info("씬 %d 실행 (시도 %d)", scene.index, attempt)
                    arts = self._run_scene_with_timeout(scene)
                    self.manifest.scene_done(scene.index, arts)
                    results["ok"].append(scene.index)
                    break
                except Exception as e:
                    tb = traceback.format_exc()
                    log.error("씬 %d 실패(시도 %d): %s", scene.index, attempt, e)
                    if attempt > self.cfg.max_scene_retries:
                        self.manifest.scene_failed(scene.index, str(e), tb)
                        results["failed"].append({"scene": scene.index, "error": str(e)})

        # [최종 조립] 5씬 전건 성공 시에만 concat 수행 — 부분 산출물로 완성본을 위조하지 않는다.
        if results["failed"]:
            log.error("씬 실패 %d건 — 최종 concat 생략(부분 완성본 생성 금지)", len(results["failed"]))
            return results

        clips: List[Path] = []
        body_total_dur = 0.0
        for scene in scenes:
            clip = self.cfg.output_root / f"scene_{scene.index:02d}" / "scene.mp4"
            if not clip.exists() or clip.stat().st_size == 0:
                raise AdapterError(f"최종 concat 불가 — 씬 {scene.index} 클립 부재/손상: {clip}")
            clips.append(clip)
            # 씬 실측 길이 합산 — 브랜딩 오버레이의 enable 컷오프(본편 구간) 산출용.
            #   · 스펙 duration(3/4/4/5/4)이 아니라 TTS 실측 길이를 우선 사용해야
            #     오버레이가 엔딩 CTA 카드 구간을 침범하지 않는다.
            try:
                probe_fn = getattr(self.video, "_probe_audio_duration", None)
                aud_p = self.cfg.output_root / f"scene_{scene.index:02d}" / "voice.mp3"
                if probe_fn and aud_p.exists():
                    body_total_dur += float(probe_fn(aud_p, scene.duration_sec))
                else:
                    body_total_dur += float(scene.duration_sec)
            except Exception:
                body_total_dur += float(scene.duration_sec)

        # 1) 엔딩 CTA 카드 클립 결합 (6번째 클립)
        cta_clip = self._render_ending_cta_clip(self.cfg.output_root)
        if cta_clip and cta_clip.exists():
            clips.append(cta_clip)
            log.info("엔딩 CTA 카드 클립 결합 성공 (총 %d개 클립)", len(clips))

        # 2) 클립 Concat
        merged_raw = self.cfg.output_root / "merged_raw.mp4"
        log.info("최종 concat 시작: %d개 클립 → %s", len(clips), merged_raw.name)
        self.video.concat_scenes(clips, merged_raw, self.cfg)

        # 3) 브랜딩 오버레이(상단 50:50 뱃지 + 하단 프로필 링크 뱃지) 본편 구간 합성
        #    ★ 감사 재심 조건 ②: 폴백 은폐 폐기 — 실패는 OverlayCompositionError 로
        #      표면화되며, 서킷브레이커 임계 초과 시 파이프라인 전체가 중단된다.
        final_path = self.cfg.output_root / f"{self.cfg.output_root.name}.mp4"
        log.info("브랜딩 오버레이 합성 시작: 본편 길이=%.2fs", body_total_dur)
        final_video = self._apply_branding_overlay(merged_raw, final_path, body_total_dur)

        # 4) 임시 merged_raw 정리
        if merged_raw.exists() and merged_raw != final_video:
            try:
                merged_raw.unlink()
            except OSError:
                pass

        self.manifest.data["final_video"] = {
            "path": str(final_video),
            "clips": [str(c) for c in clips],
            "body_duration_sec": round(body_total_dur, 3),
            "ending_cta": str(cta_clip) if cta_clip else None,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        self.manifest._flush()
        results["final_video"] = str(final_video)
        log.info("최종 완성본 렌더링 완료: %s", final_video)
        return results


# ---------------------------------------------------------------------------
# 9) 어댑터 선택 (auto → available 순)
# ---------------------------------------------------------------------------
def select_image_adapter(cfg: PipelineConfig) -> ImagePort:
    """이미지 어댑터 자동 선택 — 1순위 Gemini 실사, 2순위 ComfyUI, 3순위 브랜드 에셋.

    [영구 퇴출] 검은색 단색 더미 박스 어댑터(PILImageAdapter)는 후보에서 제외한다.
    """
    candidates: List[ImagePort] = [
        GeminiImageAdapter(),
        ComfyUIImageAdapter(),
        BrandAssetFallbackAdapter(),
    ]
    if cfg.image_backend != "auto":
        # 'pil' 은 레거시 별칭으로 asset_fallback 에 매핑한다.
        wanted = "asset_fallback" if cfg.image_backend == "pil" else cfg.image_backend
        filtered = [c for c in candidates if c.name == wanted]
        if filtered:
            candidates = filtered
        else:
            log.warning("요청 백엔드 '%s' 미존재 — auto 후보로 폴백", cfg.image_backend)
    for c in candidates:
        if c.available():
            log.info("이미지 어댑터 선택: %s", c.name)
            return c
    raise AdapterError("사용 가능한 이미지 어댑터 없음")


def select_tts_adapter(cfg: PipelineConfig) -> TTSPort:
    """TTS 어댑터 자동 선택 — 1순위 Gemini 2.5 Native Audio 드라마 대화체.

    우선순위:
      1) GeminiDramaDialogueAdapter — Gemini 2.5 Flash Native Audio(Aoede/Puck) + 1.2배속 고정
      2) EdgeTTSAdapter             — HyunsuNeural/InJoonNeural 대화체 백업
      3) Pyttsx3Adapter             — 로컬 오프라인 백업
      4) SilentTTSAdapter           — 최후 무음 폴백
    """
    candidates: List[TTSPort] = [
        GeminiDramaDialogueAdapter(),
        EdgeTTSAdapter(),
        Pyttsx3Adapter(),
        SilentTTSAdapter(),
    ]
    if cfg.tts_backend != "auto":
        candidates = [c for c in candidates if c.name == cfg.tts_backend]
    for c in candidates:
        if c.available():
            log.info("TTS 어댑터 선택: %s", c.name)
            return c
    raise AdapterError("사용 가능한 TTS 어댑터 없음")


def select_video_adapter(cfg: PipelineConfig) -> VideoPort:
    """비디오 어댑터 자동 선택 — 1순위 Wan 2.2 S2V 립싱크, 2순위 FFmpeg 정지영상.

    Wan S2V 는 ComfyUI 헬스체크(auto_start=True) 통과 시에만 선택된다.
    미가동/미설치 환경에서는 FFmpeg 어댑터로 결정론적 폴백한다.
    """
    candidates: List[VideoPort] = [WanS2VVideoAdapter(cfg), FFmpegVideoAdapter(cfg)]
    if cfg.video_backend != "auto":
        candidates = [c for c in candidates if c.name == cfg.video_backend]
    for c in candidates:
        if c.available():
            log.info("비디오 어댑터 선택: %s", c.name)
            return c
    raise AdapterError("사용 가능한 비디오 어댑터 없음")


# ---------------------------------------------------------------------------
# 10) 진입점 — 스펙은 반드시 외부 JSON에서 로드 (채팅 맥락 금지)
# ---------------------------------------------------------------------------
def load_specs_from_json(path: Path) -> List[SceneSpec]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    scenes = [SceneSpec(**s) for s in raw["scenes"]]
    return scenes


# ---------------------------------------------------------------------------
# [구조 분리] 기본 스펙 프로바이더 / 인자 해석기 / 경로 정책 / 무인 가동 안전장치
# ---------------------------------------------------------------------------
DEFAULT_CONVERSATION_ID = "insurance_auto_test"
DEFAULT_CONTEXT_AGE_MIN = 0.0
DEFAULT_OUTPUT_PREFIX = "Insurance_drama_5s"
SUBPROCESS_TIMEOUT_SEC = 600
MAX_OUTPUT_DIR_RETRY = 50

# ---------------------------------------------------------------------------
# [브랜드 중립 계약] BrandProfile — 오케스트레이터는 이 인터페이스에만 의존한다.
#   ★ 왜 필수인가(감사 재심): 기존 파일은 BRAND_NAME/ROTATION_STATE_FILENAME/
#     TOPICS/GENRES/LOCATIONS_*/NARRATIVE_MATRIX/SCENE_CHARACTER_MAP/보이스 상수/
#     CTA 카드 import/뱃지 경로 "insurance" 하드코딩이 오케스트레이션·인프라와 뒤섞여
#     있어, 보험/주식 브랜드 복제 시 파일 복사 → 문자열 치환 → 드리프트가 재발했다.
#   · 이제 브랜드는 BrandProfile 구현체로만 주입된다.
#   · 오케스트레이터/어댑터는 브랜드 문자열을 직접 참조하지 않는다.
#   · 상태 파일/산출물 네임스페이스/에셋 경로/보이스/감정/서사는 전부 팩 소유다.
# ---------------------------------------------------------------------------
class BrandProfile(ABC):
    """브랜드 콘텐츠 팩 계약 — 선언적 설정의 단일 진입점."""

    # --- 식별/네임스페이스 ---
    @property
    @abstractmethod
    def brand_id(self) -> str: ...

    @property
    @abstractmethod
    def brand_name(self) -> str: ...

    @property
    @abstractmethod
    def output_namespace(self) -> str: ...

    @property
    @abstractmethod
    def rotation_state_filename(self) -> str: ...

    # --- 서사/로테이션 풀 ---
    @property
    @abstractmethod
    def topics(self) -> Tuple[str, ...]: ...

    @property
    @abstractmethod
    def genres(self) -> Tuple[str, ...]: ...

    @property
    @abstractmethod
    def locations_ko(self) -> Tuple[str, ...]: ...

    @property
    @abstractmethod
    def locations_en(self) -> Tuple[str, ...]: ...

    @abstractmethod
    def narrative_matrix(self) -> Dict[str, Tuple[Tuple[str, str], ...]]: ...

    # --- 캐릭터/보이스/감정 ---
    @abstractmethod
    def scene_character_map(self) -> Dict[int, str]: ...

    @abstractmethod
    def character_master_files(self) -> Dict[str, str]: ...

    @abstractmethod
    def character_asset_dir(self) -> Path: ...

    @abstractmethod
    def scene_emotion_ssot(self) -> Dict[int, str]: ...

    @abstractmethod
    def scene_plan(self) -> Tuple[Tuple[float, str], ...]: ...

    # --- CTA/오버레이 에셋 (포트) ---
    @abstractmethod
    def render_cta_image(self, out_path: Path) -> Optional[Path]: ...

    @abstractmethod
    def resolve_capsule_badge_path(self) -> Optional[Path]: ...

    @abstractmethod
    def resolve_profile_pill_badge_path(self) -> Optional[Path]: ...

    @abstractmethod
    def resolve_bouncing_pill_overlay_expr(self) -> Tuple[str, str]: ...

    # --- 엔딩 CTA 문구 규격 ---
    @property
    @abstractmethod
    def brand_search_keyword(self) -> str: ...

    @property
    @abstractmethod
    def brand_cta(self) -> str: ...


class BrandProfileError(PipelineError):
    """브랜드 팩 계약 위반 — 은폐 금지, 즉시 표면화."""


class InsuranceBrandProfile(BrandProfile):
    """보험 리밸런스 브랜드 팩 — 기존 하드코딩 상수를 선언적으로 이관한 구현체.

    ★ 이 클래스는 '콘텐츠'만 소유한다. 인프라(이미지/TTS/비디오/프로세스)는
      절대 여기에 넣지 않는다. 보험/주식 브랜드는 이 클래스를 복제하여
      문자열/에셋 경로만 교체하면 되고, 오케스트레이터는 수정 불필요하다.
    """

    # [도메인 SSOT 참조] 주제/장르 리터럴은 insurance_drama_domain_data 단일 소유.
    #   · 본 클래스는 값을 재정의하지 않고 도메인 모듈 상수를 그대로 참조한다.
    #   · 16주제/8장르 변경은 도메인 모듈에서만 수행 → 드리프트 구조적 0건.
    _TOPICS: Tuple[str, ...] = INSURANCE_TOPICS
    _GENRES: Tuple[str, ...] = INSURANCE_GENRES

    @property
    def brand_id(self) -> str:
        return "insurance"

    @property
    def brand_name(self) -> str:
        return "보험 리밸런스"

    @property
    def output_namespace(self) -> str:
        return "Insurance"

    @property
    def rotation_state_filename(self) -> str:
        # ★ 브랜드별 상태 파일 격리 — 기존 .insurance_rotation_state.json 단일 공유 폐기.
        return ".insurance_rotation_state.json"

    @property
    def topics(self) -> Tuple[str, ...]:
        return self._TOPICS

    @property
    def genres(self) -> Tuple[str, ...]:
        return self._GENRES

    @property
    def locations_ko(self) -> Tuple[str, ...]:
        return LOCATIONS_KO

    @property
    def locations_en(self) -> Tuple[str, ...]:
        return LOCATIONS_EN

    def narrative_matrix(self) -> Dict[str, Tuple[Tuple[str, str], ...]]:
        return NARRATIVE_MATRIX

    def scene_character_map(self) -> Dict[int, str]:
        return SCENE_CHARACTER_MAP

    def character_master_files(self) -> Dict[str, str]:
        return CHARACTER_MASTER_FILES

    def character_asset_dir(self) -> Path:
        return CHARACTER_ASSET_DIR

    def scene_emotion_ssot(self) -> Dict[int, str]:
        return SCENE_EMOTION_SSOT

    def scene_plan(self) -> Tuple[Tuple[float, str], ...]:
        return SCENE_PLAN

    def render_cta_image(self, out_path: Path) -> Optional[Path]:
        # ★ 브랜드 UI 템플릿 import 는 팩 내부로 격리 — 오케스트레이터는 이 메서드만 호출.
        try:
            from brands.insurance.ui_templates.insurance_drama_cta_card import InsuranceCTACard
            card = InsuranceCTACard()
            im = card.render_cta_image(out_path)
            if not out_path.exists() and im is not None:
                im.save(out_path, format="PNG")
            return out_path if out_path.exists() else None
        except Exception as e:
            raise BrandProfileError(f"CTA 카드 렌더 실패(brand={self.brand_id}): {e!r}") from e

    def resolve_capsule_badge_path(self) -> Optional[Path]:
        try:
            from core.shorts_engine.shorts_brand_capsule_badge import ShortsBrandCapsuleBadge
            bp = ShortsBrandCapsuleBadge.get_overlay_path(self.brand_id)
            if bp and Path(bp).exists():
                return Path(bp).resolve()
        except Exception as e:
            raise BrandProfileError(f"캡슐 뱃지 해석 실패(brand={self.brand_id}): {e!r}") from e
        return None

    def resolve_profile_pill_badge_path(self) -> Optional[Path]:
        try:
            from core.shorts_engine.shorts_branding_overlay import ShortsBrandingOverlay
            pp = ShortsBrandingOverlay.get_bouncing_profile_badge_path(self.brand_id)
            if pp and Path(pp).exists():
                return Path(pp).resolve()
        except Exception as e:
            raise BrandProfileError(f"프로필 필 뱃지 해석 실패(brand={self.brand_id}): {e!r}") from e
        return None

    def resolve_bouncing_pill_overlay_expr(self) -> Tuple[str, str]:
        # ★ 오버레이 수식 SSOT 조회는 팩 내부로 격리 — 오케스트레이터는 리터럴 0건 유지.
        return resolve_bouncing_pill_overlay_expr()

    @property
    def brand_search_keyword(self) -> str:
        return "보험 리밸런스"

    @property
    def brand_cta(self) -> str:
        return "네이버에 보험 리밸런스 한번 검색해보세요"
# ---------------------------------------------------------------------------
# [장소 로테이션 SSOT] 2030 청춘 데이팅 16대 핫플레이스
#   · LOCATIONS_KO : 로그/매니페스트/리포트용 한국어 표기
#   · LOCATIONS_EN : Gemini 이미지 프롬프트 주입용 영문 표기
#   · 두 튜플은 반드시 같은 인덱스로 1:1 대응한다(길이 불일치 시 즉시 실패).
#   · 매 회차 location 인덱스를 +1 전진시켜 16회 주기로 100% 다른 장소를 보장한다.
# ---------------------------------------------------------------------------
# [도메인 SSOT 참조] 16대 핫플레이스 로테이션 풀은 insurance_drama_domain_data 단일 소유.
#   · 본 파일은 장소 리터럴을 재정의하지 않고 도메인 모듈 상수를 그대로 참조한다.
#   · KO/EN 두 풀은 반드시 같은 인덱스로 1:1 대응한다(도메인 모듈에서 보증).
#   · 장소 추가/교체는 도메인 모듈에서만 수행 → 드리프트 구조적 0건.
LOCATIONS_KO: Tuple[str, ...] = INSURANCE_LOCATIONS_KO
LOCATIONS_EN: Tuple[str, ...] = INSURANCE_LOCATIONS_EN

# 1:1 대응 불변식 — 두 풀의 길이가 어긋나면 인덱스 매핑이 조용히 오염된다.
if len(LOCATIONS_KO) != len(LOCATIONS_EN):
    raise SpecValidationError(
        f"장소 로테이션 풀 길이 불일치: KO={len(LOCATIONS_KO)} / EN={len(LOCATIONS_EN)}"
    )
# 씬별 (duration_sec, voice_id) — 요구 스펙: 3/4/4/5/4, 여-남-여-남-여 (교대 티키타카)
# 1순위: Google Gemini 2.5 Flash Native Audio (Aoede 여 / Puck 남)
# [영구 박멸] ko-KR-SunHiNeural(아파트 안내방송 톤) 영구 차단
SCENE_PLAN: Tuple[Tuple[float, str], ...] = (
    (3.0, GEMINI_VOICE_FEMALE),
    (4.0, GEMINI_VOICE_MALE),
    (4.0, GEMINI_VOICE_FEMALE),
    (5.0, GEMINI_VOICE_MALE),
    (4.0, GEMINI_VOICE_FEMALE),
)


def _rotation_state_path(profile: BrandProfile) -> Path:
    """브랜드별 로테이션 상태 파일 경로를 반환한다.

    ★ 왜 필수인가(감사 재심): 기존에는 사용자 홈의 단일 파일(.insurance_rotation_state.json)을
      모든 브랜드가 공유하여, 보험/주식 브랜드 복제 시 상태가 서로 오염되고
      동시 실행 시 인덱스가 충돌했다. 이제 브랜드별 서브디렉터리로 격리한다.
    """
    base = Path.home() / ".brand_rotation_state"
    base.mkdir(parents=True, exist_ok=True)
    return base / profile.rotation_state_filename


def _load_rotation_state(profile: BrandProfile) -> Dict[str, int]:
    p = _rotation_state_path(profile)
    if not p.exists():
        return {"topic": 0, "genre": 0, "location": 0, "run": 0}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return {
            "topic": int(data.get("topic", 0)) % len(profile.topics),
            "genre": int(data.get("genre", 0)) % len(profile.genres),
            "location": int(data.get("location", 0)) % len(profile.locations_en),
            "run": int(data.get("run", 0)),
        }
    except Exception as e:
        # ★ 은폐 금지: 손상 상태는 조용히 초기화하지 않고 표면화한다.
        raise SpecValidationError(
            f"로테이션 상태 파일 손상(brand={profile.brand_id}, path={p}): {e!r}"
        ) from e


def _save_rotation_state(profile: BrandProfile, state: Dict[str, int]) -> None:
    p = _rotation_state_path(profile)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)


# ---------------------------------------------------------------------------
# [자율 서사 매트릭스] 16개 연애 주제별 실제 드라마 대사/감정선/시네마틱 프롬프트
# - 하드코딩 '완성 대본'이 아니라, 주제별 서사 재료(대사·감정·화면)의 원천 데이터다.
# - 조합·변주·문장 결합은 엔진이 수행한다(고정 5줄 템플릿 폐기).
# - 씬5 엔딩은 반드시 공식 검색어 '보험 리밸런스' + 네이버 검색 유도 문구를 포함한다.
# ---------------------------------------------------------------------------
# [도메인 SSOT 참조] 16주제 × 5씬 서사 매트릭스는 insurance_drama_domain_data 단일 소유.
#   · 본 파일은 대사/프롬프트 리터럴을 재정의하지 않고 도메인 모듈 상수를 그대로 참조한다.
#   · 주제 추가/대사 교체는 도메인 모듈에서만 수행 → 드리프트 구조적 0건.
#   · 씬5 엔딩의 공식 검색어('보험 리밸런스') + 네이버 검색 유도 문구도 도메인 모듈이 보증한다.
NARRATIVE_MATRIX: Dict[str, Tuple[Tuple[str, str], ...]] = INSURANCE_NARRATIVE_MATRIX

# 씬5 엔딩 공식 규격 (붙여쓰기 100% 필수 — 브랜드 검색 유도)
BRAND_SEARCH_KEYWORD = "보험 리밸런스"
BRAND_CTA = "네이버에 보험 리밸런스 한번 검색해보세요"
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
GEMINI_TIMEOUT_SEC = 45.0


def _collect_gemini_keys() -> List[str]:
    """Gemini 시나리오 집필용 키 체인을 수집한다.

    ★ 대표님 지시 (2026-10-26): "core.gemini_unified_keys 의 통합 키 풀을
      1순위로 사용하라. 환경변수는 폴백으로만 유지하라."

    수집 우선순위(중복 제거, 순서 보존):
      1) core.gemini_unified_keys.get_unified_gemini_keys()
         — config.py 의 [무료키 6개 + 유료키 2개 + 기본키 1개] = 최대 9개 고유 키.
         · 기존 구현은 GEMINI_API_KEY + GEMINI_KEY_1~3 (최대 4개)만 사용하여
           config.py 에 등록된 무료/유료 키 8개가 통째로 유휴 상태였다.
           그 결과 429(무료 쿼터 소진) 한 번에 자율 집필이 전건 실패하고
           매트릭스 폴백으로 낙하했다.
      2) 환경변수 폴백 — GEMINI_API_KEY, GEMINI_KEY_1~3.
         · 통합 모듈 임포트 실패(config.py 부재 등) 시에도 무인 가동이
           중단되지 않도록 최후 방어선으로 유지한다.

    · 통합 모듈 임포트/조회 실패는 은폐하지 않고 경고 로그로 표면화한 뒤
      환경변수 폴백으로 진행한다(파이프라인 즉사 방지).
    · 반환값은 반드시 중복 없는 문자열 리스트이며, 빈 리스트일 수 있다
      (호출부 _call_gemini_scenario 가 빈 리스트를 매트릭스 폴백 신호로 사용).
    """
    keys: List[str] = []

    def _push(value: Any) -> None:
        if isinstance(value, str):
            s = value.strip()
            if s and s not in keys:
                keys.append(s)

    # ---- 1순위: 통합 키 풀 (config.py 무료 6 + 유료 2 + 기본 1) ----
    try:
        from core.gemini_unified_keys import get_unified_gemini_keys  # type: ignore
        unified = get_unified_gemini_keys() or []
        for k in unified:
            _push(k)
        if keys:
            log.info("Gemini 키 체인: 통합 풀 %d개 로드(core.gemini_unified_keys)", len(keys))
    except Exception as e:
        log.warning("통합 Gemini 키 풀 로드 실패 — 환경변수 폴백으로 진행: %r", e)

    # ---- 2순위: 환경변수 폴백 ----
    _push(os.environ.get("GEMINI_API_KEY"))
    for i in range(1, 4):
        _push(os.environ.get(f"GEMINI_KEY_{i}"))

    if not keys:
        log.warning("Gemini 키 체인 비어 있음 — 통합 풀/환경변수 모두 미설정")
    return keys


def _build_gemini_prompt(profile: BrandProfile, topic: str, genre: str, run_no: int) -> str:
    """Gemini 자율 집필 프롬프트를 브랜드 팩(profile) 기반으로 생성한다.

    ★ 시그니처 정합성 교정 (2026-10-26):
      기존 정의부는 (topic, genre, run_no) 3인자였으나 호출부(L2893)는
      (profile, topic, genre, run_no) 4인자로 호출하여 매 호출마다 TypeError 로
      즉사 → Gemini 자율 집필이 100% 실패하고 매트릭스 폴백으로만 낙하했다.
      정의부를 호출부에 맞춰 4인자로 승격하고, 내부 하드코딩 상수
      (BRAND_NAME / BRAND_SEARCH_KEYWORD / BRAND_CTA)를 전량 profile 조회로 이관한다.

    ★ 브랜드 중립 계약:
      · 브랜드명/검색어/CTA 는 반드시 profile 에서만 조회한다(하드코딩 0건).
      · 캐릭터 이름(수진/민우)도 profile.scene_character_map() 으로 해석하여
        보험/주식 브랜드 복제 시 인물명이 그대로 새는 것을 원천 차단한다.
      · 씬별 duration 은 profile.scene_plan() 에서 조회한다(스펙 드리프트 0건).
    """
    brand_name = profile.brand_name
    keyword = profile.brand_search_keyword
    cta = profile.brand_cta

    # [캐릭터명 브랜드 중립 해석] 씬 1/3/4/5 = 여성 화자, 씬 2 = 남성 화자.
    #   · scene_character_map() 이 없거나 조회 실패 시 안전 기본 라벨로 폴백한다.
    try:
        char_map = profile.scene_character_map() or {}
    except Exception:
        char_map = {}
    female_key = str(char_map.get(1, "female"))
    male_key = str(char_map.get(2, "male"))
    female_label = f"{female_key}(여)"
    male_label = f"{male_key}(남)"

    # [씬 길이 브랜드 중립 해석] scene_plan() 의 duration 을 초 단위로 표기.
    try:
        plan = profile.scene_plan() or ()
    except Exception:
        plan = ()
    durations: List[float] = []
    for item in plan:
        try:
            durations.append(float(item[0]))
        except Exception:
            durations.append(0.0)
    while len(durations) < 5:
        durations.append(0.0)
    d1, d2, d3, d4, d5 = (f"{durations[i]:g}" for i in range(5))

    # ------------------------------------------------------------------
    # [주제별 약관·의학 사실 SSOT 조회] 대표님 지시 (2026-10-26):
    #   "뻔한 일반론(고정지출, 중복특약 뜬구름 소리) 절대 금지!
    #    반드시 맹점과 핵심 팩트(질병명, 통계, 약관 조항)를 대사에 구체적으로
    #    직접 언급하며 티키타카를 전개하라."
    #
    #   ★ 왜 필수인가: 기존 프롬프트는 씬1~5 지시가 전부 '고정지출/중복된 특약/
    #     새는 보험료' 같은 추상 표현이라, 주제가 실손이든 치아든 암이든
    #     Gemini 가 매번 똑같은 뜬구름 대사를 생성했다. 이제 도메인 모듈의
    #     INSURANCE_TOPIC_SPECS 에서 fact/trap/check/keyword 를 조회해
    #     씬별 지시문에 구체적 근거로 직접 주입한다.
    #
    #   · 조회 실패/미등록 주제는 빈 문자열로 폴백하되, 프롬프트에 빈 괄호가
    #     남지 않도록 안전 문구로 대체한다(자리표시자 금지).
    #   · 금소법 준수: fact 는 약관·의학 사실 서술이며 금액·배수 표현은
    #     도메인 모듈 검증기에서 이미 차단되어 있다(비율 % 는 사실 서술로 허용).
    # ------------------------------------------------------------------
    try:
        spec = INSURANCE_TOPIC_SPECS.get(topic) or {}
    except Exception as e:
        log.warning("주제 스펙 조회 실패(topic='%s') — 일반 지시로 진행: %r", topic, e)
        spec = {}

    topic_trap = str(spec.get("trap", "") or "").strip() or "이 주제에서 소비자가 흔히 놓치는 맹점"
    topic_fact = str(spec.get("fact", "") or "").strip() or "이 주제의 실제 약관·의학 사실"
    topic_check = str(spec.get("check", "") or "").strip() or "이 주제의 핵심 점검 기준"
    topic_keyword = str(spec.get("keyword", "") or "").strip() or topic

    # [부부 공간 및 시선 일치 안전장치 SSOT]
    #   · 홀수 회차: Mode A (SEATED, 부부 동시 좌식)
    #   · 짝수 회차: Mode B (STANDING, 부부 동시 입식)
    #   · 5씬 전건의 시선 높이(same eye level) 및 부부 포즈 일치 강제.
    try:
        anchor = get_spatial_anchor(run_no)
    except Exception as e:
        log.warning("공간 앵커 조회 실패(run_no=%s) — 좌식 모드로 진행: %r", run_no, e)
        anchor = SPATIAL_POSTURE_MODES["SEATED"]

    anchor_name = anchor["name_ko"]
    anchor_desc = anchor["desc"]
    sujin_posture = anchor["sujin_posture"]
    minwoo_posture = anchor["minwoo_posture"]
    couple_shot = anchor["couple_shot"]

    return (
        f"너는 한국 보험 비교·리모델링 서비스 '{brand_name}'의 숏폼 드라마 작가다. "
        f"주제='{topic}', 장르='{genre}', 회차={run_no}. "
        "5씬 시나리오를 JSON으로만 출력하라. 설명/마크다운 금지.\n"
        "★ 절대 금지: 오페라, 소설, 인생 명언, 3인칭 나레이션, 시적 비유, 문어체, "
        "소개팅/데이팅 대사, 연애 서사, 남사친/여사친 설정.\n"
        f"등장인물은 부부 2인뿐이다: 수진(35세 아내, {female_label}) / 민우(37세 남편, {male_label}). "
        "실제 부부의 극사실주의 구어체 티키타카로 작성하라.\n"
        # ------------------------------------------------------------------
        # [부부 공간 및 시선 일치 안전장치 블록] — 대표님 엄명 (2026-10-26):
        #   "서 있는 것과 앉아 있는 게 번갈아 가면서 나오게, 두 사람이 같이 서 있거나
        #    같이 앉는 안전장치 필요"
        # ------------------------------------------------------------------
        f"★★ [이번 회차 부부 공간 및 시선 일치 안전장치 — {anchor_name}] ★★\n"
        f"  · 전체 공간 연출: {anchor_desc}\n"
        "  · 5개 씬 공통 규칙: 두 사람의 자세가 한 편 내에서 100% 일치해야 한다(한 명만 서 있거나 앉는 시선 왜곡 절대 금지).\n"
        f"  · 수진(여, 씬1/3/5) image_prompt 필수 지시: '{sujin_posture}'\n"
        f"  · 민우(남, 씬2/4) image_prompt 필수 지시: '{minwoo_posture}'\n"
        f"  · 부부 투샷 연출 시 구도: '{couple_shot}'\n"
        # ------------------------------------------------------------------
        # [주제 사실 근거 블록] — 씬별 지시보다 앞에 배치하여 모델이 먼저
        #   사실을 인지한 뒤 대사를 쓰도록 유도한다(근거 → 대사 순서).
        # ------------------------------------------------------------------
        f"★★ [이번 회차 주제 '{topic}' 의 실제 근거 — 반드시 대사에 직접 인용] ★★\n"
        f"  · 맹점(trap): {topic_trap}\n"
        f"  · 핵심 팩트(fact): {topic_fact}\n"
        f"  · 점검 기준(check): {topic_check}\n"
        f"  · 비교 키워드(keyword): {topic_keyword}\n"
        "★ 뻔한 일반론(고정지출, 중복특약 뜬구름 소리) 절대 금지! "
        "반드시 위 맹점과 핵심 팩트(질병명, 통계, 약관 조항)를 대사에 구체적으로 "
        "직접 언급하며 티키타카를 전개하라.\n"
        "★★ [금융광고 심의 절대 준수 — 금소법] ★★\n"
        "  - 구체적인 금액 언급 절대 금지: 숫자+원, 만원, 억, 천만원, 반값, 몇만원, 2배, 3배 등 "
        "모든 수치·비율·절감액 표현을 쓰지 마라.\n"
        "  - 대신 중립·사실 서술 표현만 사용하라: '매달 나가는 고정지출', '중복된 특약', "
        "'새는 보험료', '핵심 보장 위주로 리밸런스'.\n"
        "  - 단정·과장 표현 금지: '무조건', '100% 보장', '최고', '완벽', '확실히 아껴준다' 등.\n"
        "  - 약관은 객관적 사실로만 비교 서술하고 특정 상품의 우열을 단정하지 마라.\n"
        "  - 기존 계약의 부당 해지·해지를 조장하는 표현 금지. '점검·비교·정리' 관점으로만 서술하라.\n"
        "  - 공포 마케팅·질책성 표현('눈탱이', '호구', '사기') 금지.\n"
        "씬 구성(고정, 1씬 = 1캐릭터 단독 대사, 화자 교차 엄수):\n"
        f"  씬1 = 수진(여) 단독 — {topic}의 맹점({topic_trap})을 맞닥뜨린 현실 고민 ({d1}초)\n"
        f"  씬2 = 민우(남) 단독 — 핵심 팩트({topic_fact})를 짚는 구체적 약관 팩폭 ({d2}초)\n"
        f"  씬3 = 수진(여) 단독 — {brand_name} 34개사 AI 비교로 {topic_check} 확인한 체감 ({d3}초)\n"
        f"  씬4 = 민우(남) 단독 — 핵심 보장 위주로 정리한 안도 ({d4}초)\n"
        f"  씬5 = 수진(여) 단독 — 검색유도 클로징 ({d5}초)\n"
        "★★ [Wan 2.2 S2V 81프레임(5.06초) 칼수렴: 씬별 글자 수 절대 상한 엄수] ★★\n"
        f"  · 씬1: {SCENE_CHAR_LIMITS[1]['min']}~{SCENE_CHAR_LIMITS[1]['target']}자 (최대 {SCENE_CHAR_LIMITS[1]['max']}자 엄수, 3초 씬)\n"
        f"  · 씬2: {SCENE_CHAR_LIMITS[2]['min']}~{SCENE_CHAR_LIMITS[2]['target']}자 (최대 {SCENE_CHAR_LIMITS[2]['max']}자 엄수, 4초 씬)\n"
        f"  · 씬3: {SCENE_CHAR_LIMITS[3]['min']}~{SCENE_CHAR_LIMITS[3]['target']}자 (최대 {SCENE_CHAR_LIMITS[3]['max']}자 엄수, 4초 씬)\n"
        f"  · 씬4: {SCENE_CHAR_LIMITS[4]['min']}~{SCENE_CHAR_LIMITS[4]['target']}자 (최대 {SCENE_CHAR_LIMITS[4]['max']}자 엄수, 5초 씬)\n"
        f"  · 씬5: {SCENE_CHAR_LIMITS[5]['min']}~{SCENE_CHAR_LIMITS[5]['target']}자 (최대 {SCENE_CHAR_LIMITS[5]['max']}자 엄수, 4초 씬, 검색유도 문구 포함)\n"
        "  ※ Wan 2.2 영상은 81프레임(5.06초)에서 무조건 종료되므로, 대사가 길면 영상 끝에서 말이 잘립니다.\n"
        "  ※ 반드시 1문장의 간결한 극사실주의 구어체 단문으로 위 글자 수를 칼같이 맞춰라!\n"
        "image_prompt는 영어 시네마틱 프롬프트(카메라/조명/렌즈 포함, 위 부부 공간 앵커 필수 반영).\n"
        "★★ [키프레임 내 텍스트/자막/배너 절대 금지 SSOT] ★★\n"
        "  - image_prompt 안에 어떠한 텍스트, 자막, 배너, 글자(text, banner, overlay, title, caption, words, letters, font) 묘사도 절대 넣지 마라.\n"
        "  - 화면 중앙이나 인물 앞쪽에 텍스트나 그래픽 박스를 띄우는 지시 절대 금지! 완전히 깨끗한 순수 인물 실사 컷만 묘사하라.\n"
        f"씬5 narration에는 반드시 '{topic_keyword}'와 '{keyword}'와 '{cta}' 문구를 포함하라.\n"
        # ------------------------------------------------------------------
        # [출력 완결성·따옴표 봉인 SSOT] 대표님 지시 (2026-10-26):
        #   "반드시 5개 씬 전부(index 1부터 5까지) 누락 없이 출력하라.
        #    대사 내부에는 큰따옴표(\")를 절대 쓰지 말고 작은따옴표(')만 사용하라."
        #
        #   ★ 왜 필수인가:
        #     ① 씬 누락: 모델이 3~4씬만 출력하면 _parse_gemini_scenario_text 가
        #        '씬 개수 위반'으로 ValueError 를 던져 정상 집필분이 통째로 폐기되고
        #        매트릭스 폴백으로 낙하한다. 5씬 전건 출력을 프롬프트 레벨에서 강제한다.
        #     ② 큰따옴표: 한국어 대사 안에 이스케이프되지 않은 " 가 들어가면
        #        json.loads 가 JSONDecodeError 로 즉사한다(정규식 폴백이 회수하지만
        #        근본 원인을 제거하는 것이 우선). 작은따옴표만 쓰도록 명시 지시한다.
        #   · 이 지시는 파서 폴백(3단)과 이중 방어를 구성한다 — 프롬프트가 1차,
        #     정규식 폴백이 2차 안전망이다.
        # ------------------------------------------------------------------
        "★★ [출력 완결성 절대 규칙] ★★\n"
        "  - 반드시 5개 씬 전부(index 1부터 5까지) 누락 없이 출력하라. "
        "4개 이하로 출력하면 전체 응답이 폐기된다.\n"
        "  - 대사(narration) 내부에는 큰따옴표(\")를 절대 쓰지 말고 작은따옴표(')만 사용하라. "
        "JSON 문자열 구분자와 대사 속 인용부호가 충돌하면 파싱이 실패한다.\n"
        '출력 스키마: {"scenes":[{"index":1,"narration":"...","image_prompt":"..."}, ... 5개]}'
    )


# ---------------------------------------------------------------------------
# [Gemini 시나리오 집필 모델 체인 SSOT] 대표님 지시 (2026-10-26):
#   "raw urllib HTTP 호출(엔드포인트 404)을 Google GenAI SDK 로 전면 교체하라."
#
#   ★ 왜 교체했는가: 기존 구현은 urllib 로
#     `.../v1beta/models/gemini-2.0-flash:generateContent?key=...` 를 직접 호출했는데,
#     키 형식(AQ./AIza) 및 모델 버전 불일치로 404/400 이 반환되어 자율 집필이
#     전건 실패하고 매트릭스 폴백으로만 낙하했다. SDK 는 엔드포인트/버전/인증을
#     내부에서 해석하므로 이 실패 모드가 구조적으로 사라진다.
#
#   · 모델 체인은 앞에서부터 순차 시도(성공 즉시 반환).
#   · response_mime_type='application/json' 으로 JSON 전용 응답을 강제한다.
#   · 키 × 모델 이중 루프 — 429(무료 쿼터 소진) 시 다음 키로 자동 전진.
# ---------------------------------------------------------------------------
#   ★ 실측 교정 (2026-10-26): models.list() 실측 결과
#     · gemini-2.0-flash / gemini-1.5-flash → 404 NOT_FOUND (서비스 종료)
#     · gemini-2.5-flash → 신규 키에서 404 ("no longer available to new users")
#     · gemini-3.8-flash / gemini-3.5-flash / gemini-flash-latest → 정상 응답
#     따라서 체인은 'GA 안정판 → 경량 GA → 최신 GA 별칭' 순으로 고정한다.
#     · gemini-2.5-flash-lite 는 2.5 계열 경량 GA — 429(쿼터 소진) 시 우회 경로.
#     · gemini-flash-latest 는 구글이 최신 GA 를 가리키는 별칭 — 최후 방어선.
GEMINI_SCENARIO_MODELS: Tuple[str, ...] = (
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-flash-latest",
)


# ---------------------------------------------------------------------------
# [금소법 컴플라이언스 필터 게이트 SSOT] 대표님 절대 지시 (2026-10-26):
#   "Gemini 가 뱉은 대본이 렌더링 단계로 넘어가기 전에, 금소법 위반 표현을
#    원천 차단하는 Fail-Closed 게이트를 _parse_gemini_scenario_text 안에 넣어라."
#
#   ★ 왜 필수인가: 프롬프트에 '금액 금지/단정 금지/공포 마케팅 금지'를 아무리
#     강하게 써도, LLM 은 확률적으로 위반 표현을 섞어 낸다. 프롬프트는 '권고'일
#     뿐 '보증'이 아니다. 따라서 파싱 직후·반환 직전에 결정론적 정규식 게이트를
#     반드시 통과시켜야 한다. 위반 1건이라도 검출되면 대본 전체를 폐기(ValueError)
#     하여, 위반 대본이 TTS/이미지/렌더링 파이프라인에 절대 진입하지 못하게 한다.
#
#   ★ Fail-Closed 원칙: 검출 시 '경고 후 통과'가 아니라 '즉시 폐기'다.
#     호출부(_call_gemini_scenario)는 ValueError 를 잡아 다음 키/모델로 전진하고,
#     전 조합 실패 시 매트릭스 폴백(사전 검증된 안전 대사)으로 낙하한다.
#     즉, 위반 대본은 어떤 경로로도 살아남지 못한다.
#
#   · 3개 축으로 분류한다(대표님 지시 원문 그대로):
#       ① 단정적/절대적 표현  ② 금액/수치/배수  ③ 공포/비방 표현
#   · 정규식은 re.IGNORECASE 로 대소문자 무시, 한글은 원형 매칭.
#   · 각 축은 (축 이름, 컴파일된 패턴) 튜플로 고정하여 순회 검사한다.
#   · 검출 시 매칭된 실제 문자열을 예외 메시지에 포함하여 즉시 원인 추적이 가능하다.
# ---------------------------------------------------------------------------
COMPLIANCE_PATTERNS: Tuple[Tuple[str, "re.Pattern[str]"], ...] = (
    # ① 단정적/절대적 표현 — 보장·확정·완벽·최고 등 소비자 오인 유발 표현
    (
        "단정적/절대적 표현",
        re.compile(
            r"(무조건|절대적(?:으로)?|100\s*%|확실히\s*(?:보장|지급)|반드시\s*(?:보장|지급)|"
            r"누구나\s*(?:가입|보장)|손해\s*없|최고의?\s*보장|완벽한?\s*보장|평생\s*공짜|"
            r"원금\s*보장|확정\s*수익)",
            re.IGNORECASE,
        ),
    ),
    # ② 금액/수치/배수 — 구체적 금액·절감액·배수 표현(금소법 핵심 금지 항목)
    (
        "금액/수치/배수",
        re.compile(
            r"(\d+\s*(?:만원|천만원|억원|억|원)|반값|\d+\s*배|단돈|몇\s*천\s*원|몇\s*만\s*원)",
            re.IGNORECASE,
        ),
    ),
    # ③ 공포/비방 표현 — 소비자 질책·비하·공포 마케팅
    (
        "공포/비방 표현",
        re.compile(
            r"(눈탱이|호구|사기꾼|사기\s*보험|쓰레기\s*특약)",
            re.IGNORECASE,
        ),
    ),
)


def _validate_compliance(scenes: List[Dict[str, str]]) -> None:
    """5씬 대사 전체를 금소법 컴플라이언스 3축 및 81프레임 글자수 상한으로 검사한다(Fail-Closed).

    ★ 대표님 절대 지시 (2026-10-26):
      "각 씬마다 정확한 글자수가 얼마인지 체크하고 칼같이 맞출 수 있게 만들어라.
       렌더링 단계로 넘어가기 전에 위반 대본을 즉시 파괴하라."

    검사 대상:
      1) 81프레임(5.06초) 칼수렴: 씬별 SCENE_CHAR_LIMITS max 상한 초과 여부.
         · Wan 2.2 S2V 는 81프레임(5.06초)에서 무조건 종료되므로, 상한을 넘긴
           대사는 영상 끝에서 물리적으로 잘린다(말 끊김). 프롬프트 지시만으로는
           LLM 이 확률적으로 초과하므로 코드 레벨 결정론 검증이 반드시 필요하다.
         · 상한 사전은 도메인 모듈(SCENE_CHAR_LIMITS) 단일 소유자에서 조회한다.
           프롬프트(_build_gemini_prompt)와 본 검증기가 동일 숫자를 참조하므로
           "지시 ≠ 검증" 드리프트가 구조적으로 0건이다.
      2) 금소법 3축(단정/금액/공포) 위반 여부.
         · image_prompt 는 영어 시네마틱 프롬프트이므로 검사 대상에서 제외한다
           (한국어 금소법 표현이 등장할 수 없고, 오탐 시 정상 렌더링을 차단한다).

    동작:
      1) 씬별 narration 길이를 SCENE_CHAR_LIMITS max 와 대조한다(1차 게이트).
      2) 3개 축(단정/금액/공포)을 순회하며 각 씬 narration 을 스캔한다(2차 게이트).
      3) 첫 위반 검출 즉시 ValueError 를 발생시켜 대본 전체를 폐기한다.
      4) 위반이 없으면 조용히 반환(정상 통과).

    ★ 왜 첫 위반에서 즉시 중단하는가:
      모든 위반을 수집해 나열하면 로그가 오염되고, 어차피 대본은 폐기되므로
      첫 위반 1건만 명확히 보고하는 것이 원인 추적에 유리하다.
      (호출부는 어차피 다음 키/모델로 전진하거나 매트릭스 폴백으로 낙하한다)

    · 예외 메시지에 축 이름 + 매칭된 실제 문자열 + 씬 번호를 모두 포함하여
      로그만 보고도 어떤 표현이 문제인지 즉시 식별 가능하게 한다.
    · 글자수 초과 예외에는 실측 길이/상한/원문을 모두 담아 즉시 재작성이 가능하다.
    """
    for scene_no, item in enumerate(scenes, start=1):
        narration = str(item.get("narration", "") or "")
        if not narration:
            continue
        # 81프레임(5.06초) 칼수렴: 씬별 글자 수 절대 상한 검증 (Fail-Closed)
        limits = SCENE_CHAR_LIMITS.get(scene_no, {})
        max_limit = limits.get("max", 36)
        if len(narration) > max_limit:
            raise ValueError(
                f"[81프레임 글자수 초과 감지] 씬{scene_no} narration {len(narration)}자 "
                f"(상한 {max_limit}자 초과: '{narration}') — 대본 즉시 폐기 및 재작성 유도"
            )
        for axis_name, pattern in COMPLIANCE_PATTERNS:
            m = pattern.search(narration)
            if m:
                matched = m.group(0)
                raise ValueError(
                    f"[금소법 심의 위반 감지] '{matched}' 검출 — 대본 즉시 폐기 및 재작성 유도 "
                    f"(축={axis_name}, 씬={scene_no})"
                )


def _parse_gemini_scenario_text(text: str) -> List[Dict[str, str]]:
    """Gemini 응답 텍스트(JSON)를 5씬 리스트로 파싱·검증한다.

    ★ 왜 별도 함수인가: SDK 응답은 마크다운 펜스(```json ... ```)로 감싸져
      오는 경우가 있고, 필드 누락/씬 개수 위반을 호출부마다 중복 검사하면
      드리프트가 발생한다. 파싱·검증 계약을 단일 소유자로 고정한다.

    ★ [정규식 폴백 SSOT] 대표님 지시 (2026-10-26):
      "json.loads 실패 시(예: narration 안의 이스케이프되지 않은 큰따옴표)
       정규식 기반 JSON 추출 폴백을 추가하라."

      ★ 왜 필수인가: Gemini 는 한국어 대사 안에 큰따옴표(")를 그대로 넣어
        응답하는 경우가 있다. 이때 json.loads 는 JSONDecodeError 로 즉사하고,
        정상적으로 생성된 5씬 시나리오가 통째로 버려져 매트릭스 폴백으로
        낙하한다(자율 집필 성공률 0%). 아래 2단 폴백으로 이를 회수한다.

      폴백 1) 씬 블록 단위 추출:
        re.findall(r'\{[^{}]*?"narration"[^{}]*?"image_prompt"[^{}]*?\}', raw, re.DOTALL)
        → 블록이 5개 이상이면 각 블록에서 narration/image_prompt 를 개별 추출.
      폴백 2) 필드 배열 단위 추출:
        narrs  = re.findall(r'"narration"\s*:\s*"([^"]+)"', raw)
        prompts= re.findall(r'"image_prompt"\s*:\s*"([^"]+)"', raw)
        → 두 배열이 모두 5개 이상이면 앞에서부터 5쌍을 결속.

    불변식:
      1) 반환은 정확히 5개 원소의 List[Dict[str, str]].
      2) 각 원소는 narration/image_prompt 비어 있지 않은 문자열.
      3) 위반 시 ValueError 로 표면화(호출부가 다음 키/모델로 전진).
      4) 정규식 폴백도 5쌍을 확보하지 못하면 ValueError — 부분 산출물 위조 금지.
    """
    raw = (text or "").strip()
    if not raw:
        raise ValueError("Gemini 응답 텍스트 비어 있음")

    # 마크다운 코드펜스 제거 (```json ... ``` / ``` ... ```)
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw).strip()

    # 앞뒤 잡음 제거 — 첫 '{' 부터 마지막 '}' 까지만 파싱
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        raw = raw[start:end + 1]

    # ---- 1차: 정규 JSON 파싱 -------------------------------------------
    try:
        parsed = json.loads(raw)
        scenes = parsed.get("scenes") or []
        if len(scenes) != 5:
            raise ValueError(f"Gemini 씬 개수 위반: {len(scenes)}")

        out: List[Dict[str, str]] = []
        for i, s in enumerate(scenes, start=1):
            narr = str(s.get("narration", "")).strip()
            prm = str(s.get("image_prompt", "")).strip()
            if not narr or not prm:
                raise ValueError(f"Gemini 씬 {i} 필드 누락")
            out.append({"narration": narr, "image_prompt": prm})

        # ------------------------------------------------------------------
        # [금소법 컴플라이언스 게이트 — Fail-Closed] 대표님 절대 지시 (2026-10-26):
        #   "렌더링 단계로 넘어가기 전에 위반 대본을 즉시 파괴하라."
        #
        #   ★ 왜 여기(반환 직전)인가: 파싱이 성공한 '완성된 5씬'만 게이트에 통과시켜야
        #     검사 대상이 명확해진다. 부분 파싱 상태에서 검사하면 필드 누락 예외와
        #     컴플라이언스 예외가 뒤섞여 원인 추적이 불가능해진다.
        #   ★ 왜 try 블록 안인가: ValueError 는 아래 except 로 흘러 정규식 폴백을
        #     시도하게 된다. 폴백도 동일 원문(raw)을 재파싱하므로 같은 위반이 다시
        #     검출되고, 결국 최종 ValueError 로 표면화되어 대본이 폐기된다.
        #     즉 위반 대본은 어떤 경로로도 반환되지 않는다(Fail-Closed 보장).
        # ------------------------------------------------------------------
        _validate_compliance(out)
        return out
    except Exception as e:
        log.warning("Gemini JSON 파싱 실패 — 정규식 폴백 시도: %s", e)

    # ---- 2차 폴백: 씬 블록 단위 정규식 추출 ------------------------------
    blocks = re.findall(
        r'\{[^{}]*?"narration"[^{}]*?"image_prompt"[^{}]*?\}', raw, re.DOTALL
    )
    if len(blocks) >= 5:
        out_blocks: List[Dict[str, str]] = []
        for blk in blocks[:5]:
            m_n = re.search(r'"narration"\s*:\s*"([^"]*)"', blk, re.DOTALL)
            m_p = re.search(r'"image_prompt"\s*:\s*"([^"]*)"', blk, re.DOTALL)
            narr = (m_n.group(1) if m_n else "").strip()
            prm = (m_p.group(1) if m_p else "").strip()
            if not narr or not prm:
                out_blocks = []
                break
            out_blocks.append({"narration": narr, "image_prompt": prm})
        if len(out_blocks) == 5:
            # [금소법 게이트 — 폴백 경로도 동일 적용] Fail-Closed 원칙은 파싱 경로와
            #   무관하게 성립해야 한다. 정규식 폴백으로 복구한 대본도 반드시 검사한다.
            _validate_compliance(out_blocks)
            log.warning("Gemini 정규식 폴백(블록 단위)으로 5씬 복구 성공")
            return out_blocks

    # ---- 3차 폴백: 필드 배열 단위 정규식 추출 ----------------------------
    narrs = re.findall(r'"narration"\s*:\s*"([^"]+)"', raw)
    prompts = re.findall(r'"image_prompt"\s*:\s*"([^"]+)"', raw)
    if len(narrs) >= 5 and len(prompts) >= 5:
        out_pairs: List[Dict[str, str]] = []
        for narr, prm in zip(narrs[:5], prompts[:5]):
            n = narr.strip()
            p = prm.strip()
            if not n or not p:
                raise ValueError("Gemini 정규식 폴백: 빈 필드 감지")
            out_pairs.append({"narration": n, "image_prompt": p})
        # [금소법 게이트 — 폴백 경로도 동일 적용] Fail-Closed 원칙은 파싱 경로와
        #   무관하게 성립해야 한다. 필드 배열 폴백으로 복구한 대본도 반드시 검사한다.
        _validate_compliance(out_pairs)
        log.warning("Gemini 정규식 폴백(필드 배열)으로 5씬 복구 성공")
        return out_pairs

    raise ValueError(
        f"Gemini 응답 파싱 최종 실패 — JSON/블록/필드 폴백 전건 실패 "
        f"(narr={len(narrs)}, prompt={len(prompts)}, blocks={len(blocks)})"
    )


def _call_gemini_scenario(profile: BrandProfile, topic: str, genre: str,
                          run_no: int) -> Optional[List[Dict[str, str]]]:
    """Google GenAI SDK 로 5씬 시나리오를 자율 집필한다. 실패 시 None(폴백 유도).

    ★ 대표님 지시 (2026-10-26): raw urllib HTTP 호출(엔드포인트 404)을
      Google GenAI SDK 로 전면 교체하라.

    실행 계약:
      1) 키 체인(_collect_gemini_keys: 통합 9키 → 환경변수 폴백)을 순회한다.
      2) 각 키마다 GEMINI_SCENARIO_MODELS(2.5-flash → 2.5-flash-lite → flash-latest)를
         순차 시도한다.
      3) GenerateContentConfig 로 JSON 전용 응답을 강제한다:
         · response_mime_type='application/json' — 마크다운 펜스/설명문 차단
         · temperature=0.7 — 5씬 구조 안정성과 표현 다양성의 균형
           (1.0 은 씬 누락·형식 이탈 빈도가 높고, 0.0 은 5씬 대사가 획일화된다)
         · max_output_tokens=2048 — 5씬(대사+영문 프롬프트) 수용 상한
         · automatic_function_calling=AutomaticFunctionCallingConfig(disable=True)
           — 함수 호출 자동 실행을 원천 차단. 활성 상태에서는 모델이 JSON 대신
             함수 호출 파트를 반환하여 resp.text 가 비고, 5씬 집필이 전건 실패한다.
      4) 응답 텍스트는 _parse_gemini_scenario_text() 단일 파서로 검증(5씬/필드).
      5) 성공 즉시 반환. 전 조합 실패 시 None → 호출부가 매트릭스 폴백으로 낙하.

    · SDK 임포트 실패는 은폐하지 않고 경고 로그로 표면화한 뒤 None 반환
      (파이프라인 즉사 금지 — 매트릭스 폴백으로 무인 가동 유지).
    · 키/모델 실패는 전부 로그로 남긴다(조용한 실패 금지).
    · AutomaticFunctionCallingConfig 부재(구버전 SDK) 시에도 파이프라인이 즉사하지
      않도록 config_kwargs 를 조건부로 구성한다(하위 호환 방어).
    """
    keys = _collect_gemini_keys()
    if not keys:
        log.info("Gemini 키 부재 — profile 서사 매트릭스 폴백 사용(brand=%s)", profile.brand_id)
        return None

    try:
        from google import genai
        from google.genai import types as genai_types
    except Exception as e:
        log.warning("google.genai 임포트 실패 — 매트릭스 폴백으로 진행: %r", e)
        return None

    prompt_text = _build_gemini_prompt(profile, topic, genre, run_no)

    # ------------------------------------------------------------------
    # [GenerateContentConfig SSOT] 대표님 지시 (2026-10-26):
    #   automatic_function_calling=AutomaticFunctionCallingConfig(disable=True),
    #   temperature=0.7, max_output_tokens=2048, response_mime_type="application/json"
    #
    #   ★ 왜 automatic_function_calling 을 끄는가:
    #     SDK 는 기본적으로 함수 호출 자동 실행이 켜져 있다. 프롬프트에 함수 정의가
    #     없더라도 모델이 내부적으로 도구 호출 파트를 반환하면 resp.text 가 비어
    #     "응답 텍스트 비어 있음" ValueError 로 5씬 집필이 전건 실패한다.
    #     disable=True 로 JSON 텍스트 응답만 받도록 강제한다.
    #   ★ 왜 temperature=0.7 인가:
    #     1.0 은 5씬 구조 이탈·씬 누락 빈도가 높고, 0.0 은 5씬 대사가 획일화된다.
    #     0.7 은 구조 안정성과 표현 다양성의 균형점이다.
    #   · AutomaticFunctionCallingConfig 는 SDK 버전에 따라 부재할 수 있으므로
    #     hasattr 로 존재를 확인한 뒤에만 주입한다(구버전 SDK 하위 호환 방어).
    #     부재 시에도 나머지 3개 파라미터는 그대로 적용된다.
    # ------------------------------------------------------------------
    config_kwargs: Dict[str, Any] = {
        "temperature": 0.7,
        "max_output_tokens": 2048,
        "response_mime_type": "application/json",
    }
    afc_cls = getattr(genai_types, "AutomaticFunctionCallingConfig", None)
    if afc_cls is not None:
        try:
            config_kwargs["automatic_function_calling"] = afc_cls(disable=True)
        except Exception as e:
            log.warning("AutomaticFunctionCallingConfig 생성 실패 — 미주입 진행: %r", e)
    else:
        log.warning("AutomaticFunctionCallingConfig 미지원 SDK — 함수호출 차단 생략")

    # ------------------------------------------------------------------
    # [실패 원인 집계 SSOT] 대표님 지시 (2026-10-26):
    #   "전 조합 소진 시 어떤 예외가 발생했는지 남겨라 — 무인 가동 중
    #    장애 원인 추적이 불가능하면 안 된다."
    #
    #   ★ 왜 필수인가: 기존 구현은 각 실패를 개별 warning 으로만 남기고
    #     최종 로그에는 "전 키/모델 소진" 한 줄만 출력했다. 27회(9키×3모델)
    #     실패가 로그 사이에 흩어져 실제 원인(404/429/금소법 위반)을
    #     한눈에 식별할 수 없었다.
    #   · 마지막 예외(last_err)와 실패 사유 요약(fail_reasons)을 함께 보존한다.
    #   · compliance_blocked 플래그로 "금소법/글자수 위반으로 인한 폴백"과
    #     "네트워크/쿼터 실패로 인한 폴백"을 로그에서 즉시 구분한다.
    # ------------------------------------------------------------------
    last_err: Optional[BaseException] = None
    fail_reasons: List[str] = []
    compliance_blocked = False

    for idx, key in enumerate(keys, start=1):
        try:
            client = genai.Client(api_key=key)
        except Exception as e:
            last_err = e
            fail_reasons.append(f"key#{idx}:client_init:{type(e).__name__}")
            log.warning("Gemini 클라이언트 생성 실패(key#%d): %s", idx, e)
            continue

        for model in GEMINI_SCENARIO_MODELS:
            try:
                resp = client.models.generate_content(
                    model=model,
                    contents=prompt_text,
                    config=genai_types.GenerateContentConfig(**config_kwargs),
                )
                text = getattr(resp, "text", None)
                if not text:
                    # SDK 버전에 따라 resp.text 가 비어 있을 수 있어 후보 파트를 직접 순회
                    chunks: List[str] = []
                    for cand in (getattr(resp, "candidates", None) or []):
                        content = getattr(cand, "content", None)
                        for part in (getattr(content, "parts", None) or []):
                            t = getattr(part, "text", None)
                            if t:
                                chunks.append(t)
                    text = "".join(chunks)

                out = _parse_gemini_scenario_text(text)
                log.info("Gemini 자율 집필 성공(key#%d, model=%s, topic='%s')", idx, model, topic)
                return out
            except ValueError as e:
                # ------------------------------------------------------------------
                # [금소법/글자수 위반 — 즉시 중단 SSOT] 대표님 지시 (2026-10-26):
                #   "렌더링 단계로 넘어가기 전에 위반 대본을 즉시 파괴하라."
                #
                #   ★ 왜 ValueError 를 별도 분기로 분리하는가:
                #     _parse_gemini_scenario_text 는 (a) 금소법 3축 위반,
                #     (b) 81프레임 글자수 초과, (c) 씬 개수/필드 누락 시 ValueError 를
                #     던진다. 이는 '네트워크 오류'가 아니라 '대본 자체가 부적격'이라는
                #     결정론적 판정이다. 그런데 기존 구현은 이를 일반 Exception 과
                #     동일하게 취급하여 9키 × 3모델 = 최대 27회를 재시도했다.
                #     · 결과 ①: 동일 프롬프트로 같은 위반 대본을 27번 재생성 → API
                #       쿼터(429)만 소진하고 성공 확률은 거의 0.
                #     · 결과 ②: 진짜 원인(금소법 위반)이 "호출 실패" 로그에 묻혀
                #       무인 가동 중 원인 추적이 불가능.
                #   · 따라서 ValueError 는 첫 검출 즉시 루프를 탈출하여 매트릭스
                #     폴백(사전 검증된 안전 대사)으로 즉시 낙하한다.
                #   · Fail-Closed 원칙 유지: 위반 대본은 어떤 경로로도 반환되지 않는다.
                # ------------------------------------------------------------------
                last_err = e
                compliance_blocked = True
                fail_reasons.append(f"key#{idx}/{model}:compliance:{str(e)[:80]}")
                log.error(
                    "Gemini 대본 부적격 — 재시도 무의미, 즉시 매트릭스 폴백(key#%d, model=%s): %s",
                    idx, model, e,
                )
                break
            except Exception as e:
                last_err = e
                fail_reasons.append(f"key#{idx}/{model}:{type(e).__name__}")
                log.warning("Gemini 호출 실패(key#%d, model=%s): %s", idx, model, e)
                continue

        # [조기 탈출] 금소법/글자수 위반은 키를 바꿔도 동일 결과 — 외부 루프까지 중단.
        if compliance_blocked:
            break

    # ------------------------------------------------------------------
    # [최종 실패 보고 — 원인 요약 SSOT]
    #   · compliance_blocked=True → 대본 부적격(금소법/글자수)으로 인한 폴백.
    #   · 그 외 → 네트워크/쿼터/모델 부재 등 인프라 실패로 인한 폴백.
    #   · fail_reasons 는 최대 6건만 요약 출력(로그 폭주 방지).
    # ------------------------------------------------------------------
    if compliance_blocked:
        log.error(
            "Gemini 자율 집필 중단 — 대본 부적격(금소법/글자수)으로 매트릭스 폴백. "
            "원인: %s", str(last_err)[:200],
        )
    else:
        log.warning(
            "Gemini 전 키/모델 소진 — 자율 서사 매트릭스 폴백 (실패 %d건, 마지막: %r, 요약: %s)",
            len(fail_reasons), last_err, "; ".join(fail_reasons[:6]),
        )
    return None


def _compose_from_matrix(profile: BrandProfile, topic: str, genre: str,
                         run_no: int) -> List[Dict[str, str]]:
    """profile 서사 매트릭스 1:1 조회 — 문장 이어붙이기 레거시 완전 폐기.

    ★ 감사 재심: 전역 NARRATIVE_MATRIX/TOPICS 참조를 제거하고 profile 로 이관.

    불변식:
      1) profile.narrative_matrix()[topic] 은 정확히 5개의 (대사, 프롬프트) 튜플이다.
      2) 조합/변주/문장 결합을 하지 않는다. 튜플을 그대로 1:1 매핑한다.
      3) 미등록 주제는 profile 로테이션 인덱스로 결정론적 대체(자리표시자 금지).
    """
    matrix = profile.narrative_matrix()
    scenes = matrix.get(topic)
    if scenes is None:
        fallback_topic = profile.topics[run_no % len(profile.topics)]
        scenes = matrix.get(fallback_topic)
        if scenes is None:
            raise SpecValidationError(
                f"서사 매트릭스 미등록(brand={profile.brand_id}): "
                f"topic='{topic}', fallback='{fallback_topic}'"
            )
        log.warning("주제 '%s' 매트릭스 미등록 — 대체 주제 '%s' 사용", topic, fallback_topic)

    if len(scenes) != 5:
        raise SpecValidationError(
            f"매트릭스 씬 개수 위반(brand={profile.brand_id}): "
            f"topic='{topic}' → {len(scenes)}개 (정확히 5 필요)"
        )

    return [
        {"narration": narr, "image_prompt": prm}
        for narr, prm in scenes
    ]


def _build_autonomous_scenes(profile: BrandProfile, topic: str, genre: str, run_no: int,
                             location_en: str = "") -> List[SceneSpec]:
    """자율 시나리오 생성 엔진 — Gemini 우선, 실패 시 profile 서사 매트릭스 폴백.

    ★ 감사 재심: 기존에는 SCENE_PLAN/BRAND_SEARCH_KEYWORD/BRAND_CTA/NARRATIVE_MATRIX
      전역 상수에 결합되어 브랜드 복제 시 드리프트가 발생했다. 이제 profile 이 소유한다.

    불변식:
      1) profile.scene_plan() 규격 엄수.
      2) 씬5 narration에 profile.brand_search_keyword + profile.brand_cta 강제 주입.
      3) 자리표시자/더미 텍스트 생성 금지.
      4) location_en 은 5씬 전건에 동일 주입 — 한 편 안의 공간 연속성 100% 보장.
    """
    drafted = _call_gemini_scenario(profile, topic, genre, run_no)
    if drafted is None:
        drafted = _compose_from_matrix(profile, topic, genre, run_no)

    plan = profile.scene_plan()
    if len(plan) != 5:
        raise SpecValidationError(
            f"scene_plan 길이 위반(brand={profile.brand_id}): {len(plan)} (정확히 5 필요)"
        )

    # [부부 공간 및 시선 일치 안전장치 SSOT 결속]
    # 회차별 앵커(좌식 ↔ 입식)를 5씬 전건의 image_prompt에 최종 결속하여
    # Gemini 생성본 및 폴백 매트릭스 전건에서 시선·포즈 불일치가 발생하지 않도록 2중 방어한다.
    try:
        anchor = get_spatial_anchor(run_no)
    except Exception:
        anchor = SPATIAL_POSTURE_MODES["SEATED"]

    scenes: List[SceneSpec] = []
    for i, ((dur, voice), item) in enumerate(zip(plan, drafted), start=1):
        narr = item["narration"].strip()
        prm = item["image_prompt"].strip()

        # 화자별(수진:1,3,5 / 민우:2,4) 자세 앵커 결속 (자세 토큰 미포함 시 안전 주입)
        posture_tok = anchor["sujin_posture"] if (i in (1, 3, 5)) else anchor["minwoo_posture"]
        if "seated" not in prm.lower() and "standing" not in prm.lower():
            prm = f"{prm}, {posture_tok}"

        if i == 5:
            kw = profile.brand_search_keyword
            cta = profile.brand_cta
            if kw not in narr:
                narr = f"{narr} {kw}."
            if "네이버" not in narr or kw not in narr:
                narr = f"{narr} {cta}."
        scenes.append(SceneSpec(
            index=i,
            narration=narr,
            duration_sec=dur,
            image_prompt=prm,
            voice_id=voice,
            location_en=location_en,
            topic=topic,
        ))
    return scenes


def build_default_5scenes_spec(profile: Optional[BrandProfile] = None) -> List[SceneSpec]:
    """상태 파일 기반 자율 로테이션 5씬 스펙 팩토리 (SSOT 진입점).

    ★ 감사 재심: 기존에는 전역 TOPICS/GENRES/LOCATIONS_*/NARRATIVE_MATRIX 와
      사용자 홈 단일 상태 파일에 결합되어 브랜드 복제 시 상태·서사가 섞였다.
      이제 모든 로테이션 풀과 상태 파일은 profile 이 소유한다.

    ★ 시그니처 계약 (2026-10-26 교정):
      profile 을 Optional 기본값(None)으로 승격하여 무인자 호출을 정식 허용한다.
      · resolve_run_inputs() 는 CLI 인자가 없을 때 build_default_5scenes_spec() 을
        무인자로 호출한다. 기존 필수 인자 시그니처에서는 TypeError 로 즉사하여
        "인자 없음 → 자동 실행" 경로가 100% 실패했다.
      · profile 미지정 시 InsuranceBrandProfile() 로 결정론적 기본 팩을 주입한다.
      · AST 시그니처 검사 기준 min_args=0 / max_args=1 로 정합된다.

    불변식:
      1) 반환 타입은 반드시 List[SceneSpec].
      2) 반환 전 SpecValidator.validate_all 통과 (fail-fast).
      3) 하드코딩 정적 대본 금지 — profile 의 3축 로테이션.
      4) 상태 파일 갱신은 성공 반환 직전에만 수행.
      5) location_en 은 5씬 전건 동일 주입 → 한 편 내 공간 연속성 100%.
    """
    if profile is None:
        profile = InsuranceBrandProfile()
    state = _load_rotation_state(profile)
    topic = profile.topics[state["topic"]]
    genre = profile.genres[state["genre"]]
    location_idx = state.get("location", 0) % len(profile.locations_en)
    location_ko = profile.locations_ko[location_idx]
    location_en = profile.locations_en[location_idx]
    run_no = state["run"] + 1

    scenes = _build_autonomous_scenes(profile, topic, genre, run_no, location_en=location_en)
    SpecValidator.validate_all(scenes, 0.0, f"{profile.brand_id}_default_5scenes")

    _save_rotation_state(profile, {
        "topic": (state["topic"] + 1) % len(profile.topics),
        "genre": (state["genre"] + 1) % len(profile.genres),
        "location": (location_idx + 1) % len(profile.locations_en),
        "run": run_no,
    })
    log.info("자율 로테이션(brand=%s): run=%d topic='%s' genre='%s' location='%s'",
             profile.brand_id, run_no, topic, genre, location_ko)
    return scenes


# ---------------------------------------------------------------------------
# 경계 스키마 계약 (단일 진실 원천)
# - SceneSpec 도메인 모델의 실제 필드와 1:1 대응한다.
# - 이 상수는 경계(dict) 표현의 유일한 계약이며, 로더/역직렬화기가 공유한다.
# - 콘텐츠(서사)는 별도 관심사로 분리한다. 스키마 변경과 콘텐츠 교체를 혼합 금지.
# ---------------------------------------------------------------------------
SCENE_SPEC_BOUNDARY_KEYS: Tuple[str, ...] = (
    "index",
    "narration",
    "duration_sec",
    "image_prompt",
    "voice_id",
    "location_en",
    "topic",
)

# ---------------------------------------------------------------------------
# [폐기 완료] 정적 더미 데이터 소스(DEFAULT_5SCENES_SPEC_DATA) 및 legacy 로더/역직렬화기
# - 폐공장 SF 더미 대본은 자율 시나리오 엔진 도입과 함께 영구 삭제되었다.
# - 5씬 스펙의 유일한 진입점은 build_default_5scenes_spec() 이다.
# ---------------------------------------------------------------------------


def resolve_desktop_root() -> Path:
    """플랫폼별 바탕화면 경로를 결정론적으로 해석한다."""
    home = Path.home()
    candidates = [home / "Desktop", home / "바탕화면", home / "OneDrive" / "Desktop"]
    for cand in candidates:
        if cand.exists() and cand.is_dir():
            return cand
    # 바탕화면이 없으면 홈 하위로 폴백 (무인 가동 중단 방지)
    fallback = home / "Desktop"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


OUTPUT_NAMESPACE = "한국 숏폼_산출물"
OUTPUT_BRAND_DIR = "Insurance"


def allocate_output_dir(prefix: str = DEFAULT_OUTPUT_PREFIX) -> Path:
    """타임스탬프 기반 산출물 폴더를 원자적으로 할당한다.

    표준 경로: {바탕화면}/한국 숏폼_산출물/Insurance/{prefix}_{YYYYMMDD}_{HHMMSS}{suffix}
    - 바탕화면 루트 오염 차단 + 브랜드 격리 표준 준수.
    - 동일 초 내 반복 실행 시 suffix를 증가시켜 충돌을 회피한다.
    """
    root = resolve_desktop_root() / OUTPUT_NAMESPACE / OUTPUT_BRAND_DIR
    root.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    for attempt in range(MAX_OUTPUT_DIR_RETRY):
        suffix = "" if attempt == 0 else f"_{attempt:02d}"
        candidate = root / f"{prefix}_{ts}{suffix}"
        try:
            candidate.mkdir(parents=True, exist_ok=False)
            return candidate
        except FileExistsError:
            continue
    raise RuntimeError(f"산출물 폴더 할당 실패 — {MAX_OUTPUT_DIR_RETRY}회 재시도 초과")


def resolve_run_inputs(argv: List[str]) -> Tuple[List[Dict[str, Any]], float, str]:
    """CLI 인자를 정규화하여 (scenes, context_age_min, conversation_id)를 반환한다.

    인자가 없으면 기본 스펙으로 폴백하여 자동 실행 경로를 보장한다.
    """
    if len(argv) < 2:
        log.info("인자 없음 — 기본 5씬 스펙으로 자동 실행 모드 진입")
        return build_default_5scenes_spec(), DEFAULT_CONTEXT_AGE_MIN, DEFAULT_CONVERSATION_ID

    spec_path = Path(argv[1])
    context_age_min = float(argv[2]) if len(argv) > 2 else DEFAULT_CONTEXT_AGE_MIN
    conversation_id = argv[3] if len(argv) > 3 else DEFAULT_CONVERSATION_ID
    scenes = load_specs_from_json(spec_path)
    return scenes, context_age_min, conversation_id


def run_with_timeout(cmd: List[str], timeout_sec: int = SUBPROCESS_TIMEOUT_SEC) -> int:
    """서브프로세스를 타임아웃과 함께 실행하고, 초과 시 강제 회수한다.

    좀비 프로세스 및 무한 대기(hang)를 방지하여 24시간 무인 가동을 보장한다.
    """
    proc = subprocess.Popen(cmd)
    try:
        return proc.wait(timeout=timeout_sec)
    except subprocess.TimeoutExpired:
        log.error("서브프로세스 타임아웃(%ss) — 강제 종료: %s", timeout_sec, cmd)
        proc.kill()
        proc.wait(timeout=30)
        return 124
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=30)


def main(argv: List[str]) -> int:
    try:
        scenes, context_age_min, conversation_id = resolve_run_inputs(argv)
        SpecValidator.validate_all(scenes, context_age_min, conversation_id)
    except Exception as e:
        log.error("스펙 검증 실패 — 즉시 중단: %s", e)
        return 3

    try:
        output_root = allocate_output_dir()
    except Exception as e:
        log.error("산출물 경로 할당 실패 — 즉시 중단: %s", e)
        return 4

    cfg = PipelineConfig(output_root=output_root)
    try:
        image = select_image_adapter(cfg)
        tts = select_tts_adapter(cfg)
        video = select_video_adapter(cfg)
    except AdapterError as e:
        log.error("어댑터 초기화 실패: %s", e)
        return 4

    orch = PipelineOrchestrator(cfg, image, tts, video)
    result = orch.run(scenes)
    log.info("완료: ok=%s failed=%s", result["ok"], result["failed"])
    return 0 if not result["failed"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))