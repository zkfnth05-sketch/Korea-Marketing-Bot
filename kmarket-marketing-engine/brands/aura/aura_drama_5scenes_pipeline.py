# aura_drama_5scenes_pipeline.py  (신규 파일 — 완성형 전체 코드)
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
#   CURRENT_DIR  = .../kmarket-marketing-engine/brands/aura
#   PROJECT_ROOT = .../kmarket-marketing-engine   ← config.py 가 위치한 루트
# 이 보정이 없으면 cwd 가 brands/aura 일 때 `import config` 가 실패하여
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
log = logging.getLogger("aura.pipeline")


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
#   씬1 서연(여) 훅 / 씬2 민준(남) 팩폭 / 씬3 서연 솔루션 / 씬4 서연 약속 / 씬5 서연 엔딩
CHARACTER_ASSET_DIR = Path(__file__).resolve().parent / "assets" / "characters"
CHARACTER_MASTER_FILES: Dict[str, str] = {
    "seoyeon": "aura_seoyeon_master.png",
    "minjun": "aura_minjun_master.png",
}
SCENE_CHARACTER_MAP: Dict[int, str] = {
    1: "seoyeon",
    2: "minjun",
    3: "seoyeon",
    4: "minjun",
    5: "seoyeon",
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
    "seoyeon": "episode_seoyeon_master.png",
    "minjun": "episode_minjun_master.png",
}

# 회차별 신규 주인공 생성 프롬프트 (화사한 자연광 / 긴 생머리 / 맑고 투명한 피부)
FRESH_FEMALE_PROMPT = (
    "Photorealistic studio portrait of a beautiful Korean woman in her mid-20s, "
    "long silky straight black hair flowing past her shoulders, luminous clear translucent skin, "
    "refined elegant facial features, soft natural makeup, gentle warm smile, "
    "bright crisp natural daylight, high-key luminous exposure, pristine crystal-clear studio lighting, "
    "radiant healthy skin tone, plain soft neutral background, "
    "vertical 9:16 portrait, upper body, looking at camera, "
    "ultra realistic skin texture, 85mm portrait lens, shallow depth of field, "
    "absolutely NO candlelight, NO dark moody shadows, NO dim amber lighting, "
    "no text, no watermark, no logo, no cartoon, no illustration"
)
FRESH_MALE_PROMPT = (
    "Photorealistic studio portrait of a handsome Korean man in his mid-20s, "
    "neat short black hair, clean-shaven, clear healthy skin, refined friendly facial features, "
    "bright crisp natural daylight, high-key luminous exposure, pristine crystal-clear studio lighting, "
    "radiant healthy skin tone, plain soft neutral background, "
    "vertical 9:16 portrait, upper body, looking at camera, "
    "ultra realistic skin texture, 85mm portrait lens, shallow depth of field, "
    "absolutely NO candlelight, NO dark moody shadows, NO dim amber lighting, "
    "no text, no watermark, no logo, no cartoon, no illustration"
)

# 회차 전용 마스터 캐시 (run_id → {"seoyeon": Path, "minjun": Path})
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
      4) 반환 dict 는 반드시 {"seoyeon": Path, "minjun": Path} 완전체여야 한다.
    """
    if run_id in _EPISODE_MASTER_CACHE:
        return _EPISODE_MASTER_CACHE[run_id]

    episode_dir = EPISODE_CHARACTER_DIR / run_id
    resolved: Dict[str, Path] = {}
    keys = _collect_image_api_keys()

    if keys:
        for who, prompt in (("seoyeon", FRESH_FEMALE_PROMPT), ("minjun", FRESH_MALE_PROMPT)):
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
             run_id, resolved["seoyeon"].name, resolved["minjun"].name)
    return resolved


def resolve_character_asset(scene_idx: int, run_id: str = "") -> Path:
    """씬 인덱스 → 화자 마스터 에셋 경로를 결정론적으로 해석한다.

    ★ 대표님 확정 지시 (2026-10-25): 회차별 신규 주인공 즉석 생성 경로를 전면 폐기하고,
      정적 마스터 에셋(CHARACTER_ASSET_DIR)만 결정론적으로 반환한다.

    · run_id 인자는 호출부(ImagePort.generate 시그니처) 하위 호환을 위해 유지하되,
      내부 분기에서는 사용하지 않는다(ensure_fresh_episode_characters 호출 제거).
    · 씬 1/3/5 → 서연 마스터, 씬 2/4 → 민준 마스터 (SCENE_CHARACTER_MAP SSOT).
    · 실패 시 AdapterError 로 표면화(검은 박스 폴백 금지).
    """
    who = SCENE_CHARACTER_MAP.get(scene_idx, "seoyeon")

    path = CHARACTER_ASSET_DIR / CHARACTER_MASTER_FILES[who]
    if not path.exists() or path.stat().st_size == 0:
        raise AdapterError(
            f"캐릭터 마스터 에셋 부재: {path} (씬 {scene_idx} → {who})"
        )
    return path


def _collect_image_api_keys() -> List[str]:
    """Gemini 이미지 생성용 키 풀 수집 (환경변수 → config.py 유료/무료키).

    우선순위: 유료 Aura 키 → 무료 Aura 키 → 범용 GEMINI_API_KEY.
    """
    keys: List[str] = []

    def _push(v: Any) -> None:
        if isinstance(v, str):
            s = v.strip()
            if s and s not in keys:
                keys.append(s)

    # 1) config.py 키 풀 (Aura 전용 우선)
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
        who = SCENE_CHARACTER_MAP.get(scene_idx, "seoyeon")
        name_ko = "서연 (20대 한국 여성)" if who == "seoyeon" else "민준 (20대 한국 남성)"

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
        # [씬 3 아우라 소개 씬 전용 연출 SSOT] 대표님 절대 지시 (2026-10-25):
        #   "3번 씬은 아우라 소개 씬인데, 여자 주인공이 핸드폰을 손에 들고 보고
        #    말하게 만들어야지! 테이블 위에 폰 덩그러니 세워놓고 정면만 쳐다보는
        #    어색한 연출 영구 퇴출!"
        #
        #   ★ 왜 필수인가: 씬 3은 '아우라 AI 솔루션 체감' 씬이다. 주인공이 폰을
        #     손에 들고 화면을 보며 감탄하는 연출이어야 서사가 성립한다. 기존처럼
        #     테이블 위에 세워진 폰을 정면으로 응시하면 "폰이 나를 쳐다보는" 어색한
        #     구도가 되어 아우라 소개 씬의 설득력이 0이 된다.
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

        return (
            "Photorealistic cinematic vertical short-form drama still, 9:16 portrait. "
            f"Main subject: {name_ko} — keep the EXACT same face, hairstyle and identity "
            "as the attached reference portrait image. Do not change the person's identity. "
            f"{composition}. "
            f"Scene direction: {prompt}. "
            f"{lighting}. "
            f"Ultra realistic skin texture, {atmosphere} of {loc}, "
            "cinematic lighting, shallow depth of field, 35mm film grain, "
            "no text, no watermark, no logo, no cartoon, no illustration."
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
        #   · 씬 1/3/5 → 서연 마스터 1장 → 서연 단독 정면만 생성.
        #   · 씬 2/4   → 민준 마스터 1장 → 민준 단독 정면만 생성.
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
    씬 2 → 민준 마스터, 씬 1/3/4/5 → 서연 마스터를 1080x1920 세로 비율로
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
#   · Edge-TTS 백업: HyunsuNeural(여) / InJoonNeural(남)
#   · ko-KR-SunHiNeural 은 관리사무소 안내방송 기계음 — 어떤 경로로도 사용 금지
# ---------------------------------------------------------------------------
GEMINI_VOICE_FEMALE = "Aoede"
GEMINI_VOICE_MALE = "Puck"
EDGE_VOICE_FEMALE = "ko-KR-HyunsuNeural"
EDGE_VOICE_MALE = "ko-KR-InJoonNeural"
BANNED_VOICE_TOKENS: Tuple[str, ...] = ("sunhi",)
DRAMA_SPEECH_SPEED = 1.20  # ⏱️ 대표님 확정 명령: 1.2배속 고정 (Wan S2V 81프레임 수렴)


def _is_banned_voice(voice_id: str) -> bool:
    """금지 보이스(SunHi 등 안내방송 톤) 여부를 판정한다."""
    low = str(voice_id or "").lower()
    return any(tok in low for tok in BANNED_VOICE_TOKENS)


def _detect_speaker_gender(voice_id: str) -> str:
    """voice_id 문자열로 화자 성별을 결정론적으로 판별한다.

    male 판정 토큰: puck / injoon / male / 남
    그 외(기본값): female
    """
    low = str(voice_id or "").lower()
    if any(m in low for m in ("puck", "injoon", "male", "남")):
        return "male"
    return "female"


def _resolve_edge_voice(voice_id: str) -> str:
    """Gemini 보이스명(Aoede/Puck) 및 성별 토큰을 Edge-TTS 보이스로 정규화한다.

    SunHiNeural 등 금지 보이스가 유입되면 성별 판정 후 안전 보이스로 강제 치환한다.
    """
    low = str(voice_id or "").lower()
    if "aoede" in low:
        return EDGE_VOICE_FEMALE
    if "puck" in low:
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
    - 1순위: Google Gemini 2.5 Flash Native Audio 9키 체인 (Aoede 여 / Puck 남)
    - 2순위 백업: Edge-TTS 대화체 (ko-KR-HyunsuNeural / ko-KR-InJoonNeural)
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

        # 화자 성별 자동 판별 (Aoede/Hyunsu -> female, Puck/InJoon -> male)
        speaker = _detect_speaker_gender(voice_id)

        # 1. 원본 음성 합성 (Gemini 2.5 Native Audio 9키 체인 -> 실패 시 Edge-TTS 페일오버)
        raw_name = f"raw_{out_path.name}"
        raw_path, raw_dur = synth.synthesize_dialogue(
            dialogue_text=text,
            output_filename=raw_name,
            force_speaker=speaker,
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
#   ★ 왜 필수인가: 씬 3(아우라 소개)만 'pleasantly surprised, impressed expression'
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
    # 씬 1 — 서연(여) 훅: 억울·답답 공감 표정
    1: (
        "She has a relatable slightly frustrated, deeply troubled expression, "
        "gentle soft sigh with expressive eyes, tired yet deeply relatable conversational look, "
        "natural soft relaxed closed lips without strain"
    ),
    # 씬 2 — 민준(남) 팩폭: 묵직하고 차분한 팩폭 남사친 (촐싹거림 박멸)
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
    # 씬 3 — 서연(여) 아우라 소개: 감탄·놀람 (기존 phone_hold 연출과 결속)
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
    #     브랜드 검색 유도(아우라AI데이팅)를 시각적으로 각인시키는 3초 엔딩 카드가
    #     반드시 마지막에 붙어야 숏폼 CTA 전환이 성립한다.
    #
    #   · AuraDramaCTACard.render_cta_image(output_path) 는 PIL Image 를 반환하며,
    #     output_path 를 주면 파일로도 저장한다(실측 확인 완료).
    #   · 무음 트랙(anullsrc)을 반드시 결합해야 concat demuxer 가 오디오 스트림
    #     유무 불일치로 실패하지 않는다(본편 5씬은 전건 오디오 보유).
    #   · 실패 시 None 반환 — 본편 5씬은 그대로 보존한다(전체 실패 금지).
    # ------------------------------------------------------------------
    def _render_ending_cta_clip(self, output_dir: Path) -> Optional[Path]:
        try:
            from brands.aura.ui_templates.aura_drama_cta_card import AuraDramaCTACard
            cta_img_path = output_dir / "cta_card.png"
            cta_clip_path = output_dir / "scene_06_ending_cta.mp4"
            if cta_clip_path.exists() and cta_clip_path.stat().st_size > 50000:
                log.info("기존 엔딩 CTA 카드 클립 재사용: %s", cta_clip_path.name)
                return cta_clip_path

            card = AuraDramaCTACard()
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
    #     CTA 카드 위에 뱃지가 겹쳐 카드 문구(아우라AI데이팅)를 가린다.
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
            bp = ShortsBrandCapsuleBadge.get_overlay_path("aura")
            if bp and Path(bp).exists():
                badge_path = str(Path(bp).resolve()).replace("\\", "/")
        except Exception as e:
            log.debug("상단 캡슐 뱃지 로드 실패: %s", e)

        pill_path = None
        try:
            from core.shorts_engine.shorts_branding_overlay import ShortsBrandingOverlay
            pp = ShortsBrandingOverlay.get_bouncing_profile_badge_path("aura")
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
DEFAULT_CONVERSATION_ID = "aura_auto_test"
DEFAULT_CONTEXT_AGE_MIN = 0.0
DEFAULT_OUTPUT_PREFIX = "Aura_drama_5s"
SUBPROCESS_TIMEOUT_SEC = 600
MAX_OUTPUT_DIR_RETRY = 50

# 브랜드/로테이션 상수 (하드코딩 대본 금지 — 상태 파일 기반 자율 로테이션)
BRAND_NAME = "아우라AI데이팅"
ROTATION_STATE_FILENAME = ".aura_rotation_state.json"
TOPICS: Tuple[str, ...] = (
    "소개팅 호구조사 빌런", "카톡 읽씹 5시간의 멘붕", "자만추 꿈꾸는 방구석 솔로",
    "더치페이 100원 단위 계산 빌런", "어색한 침묵 30초 뚝딱거림", "MBTI 과몰입 소개팅",
    "삼프터인데 고백 안 하는 썸남", "프로필 사진 사기 당한 날", "첫마디 질문 대화 공포증",
    "주말에 혼밥하는 솔로 3년차", "친구들은 다 연애중", "소개팅 애프터 신청 타이밍",
    "전여친 무용담 떠드는 빌런", "연애 세포 바짝 마른 청춘", "이상형 눈만 높은 프로 불만러",
    "소개팅 파토 나고 멘붕 온 날",
)
GENRES: Tuple[str, ...] = (
    "로맨틱 코미디", "멜로드라마", "청춘 성장", "판타지 로맨스",
    "스릴러 로맨스", "일상 힐링", "시대극", "SF 로맨스",
)
# ---------------------------------------------------------------------------
# [장소 로테이션 SSOT] 2030 청춘 데이팅 16대 핫플레이스
#   · LOCATIONS_KO : 로그/매니페스트/리포트용 한국어 표기
#   · LOCATIONS_EN : Gemini 이미지 프롬프트 주입용 영문 표기
#   · 두 튜플은 반드시 같은 인덱스로 1:1 대응한다(길이 불일치 시 즉시 실패).
#   · 매 회차 location 인덱스를 +1 전진시켜 16회 주기로 100% 다른 장소를 보장한다.
# ---------------------------------------------------------------------------
LOCATIONS_KO: Tuple[str, ...] = (
    "성수동 에스프레소 바 원목 카운터",
    "한남동 내추럴 와인바 시티뷰 창가석",
    "익선동 한옥 티하우스 원목 좌식 테이블",
    "연남동 루프탑 카페 노을 야외 테라스",
    "도산공원 미니멀 브런치 카페 대리석 테이블",
    "을지로 LP 바 빈티지 원목 테이블",
    "양재 플랜테리어 온실 카페 유리 테이블",
    "망원동 독립서점 심야 북카페 창가석",
    "청담동 럭셔리 라운지 가죽 소파 테이블",
    "반포 한강공원 잠수교 야경 테라스",
    "삼청동 돌담길 갤러리 카페 중정 테이블",
    "문래동 감성 철공소 개조 펍 테이블",
    "송리단길 호수뷰 베이커리 카페 창가석",
    "서촌 골목 심야 재즈 카페 원형 테이블",
    "압구정 로데오 힙한 젤라또 카페 파스텔 테이블",
    "북촌 한옥마을 다도 다락방 원목 테이블",
)

LOCATIONS_EN: Tuple[str, ...] = (
    "cozy Seongsu-dong espresso bar wooden counter table",
    "stylish Hannam-dong natural wine bar window table with Seoul city night view",
    "traditional Ikseon-dong Hanok tea house wooden table",
    "sunset Yeonnam-dong rooftop cafe outdoor terrace table",
    "chic Dosan Park minimalist brunch cafe marble table",
    "vibrant Euljiro vinyl record lounge vintage wooden table with warm neon accents",
    "sunlit Yangjae greenhouse cafe glass table surrounded by lush plants",
    "quiet Mangwon-dong bookstore cafe cozy window nook table",
    "luxurious Cheongdam-dong lounge leather sofa table",
    "Banpo Han River night view riverside terrace table",
    "Samcheong-dong gallery cafe courtyard wooden table",
    "Mullae-dong industrial vintage pub steel-wood table",
    "Songridan-gil lake view bakery cafe sunlit window table",
    "Seochon alley stylish midnight jazz lounge sleek round table",
    "trendy Apgujeong Rodeo gelato cafe pastel colorful table",
    "Bukchon Hanok village traditional tea attic wooden low table",
)

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


def _rotation_state_path() -> Path:
    return Path.home() / ROTATION_STATE_FILENAME


def _load_rotation_state() -> Dict[str, int]:
    p = _rotation_state_path()
    if not p.exists():
        return {"topic": 0, "genre": 0, "location": 0, "run": 0}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return {
            "topic": int(data.get("topic", 0)) % len(TOPICS),
            "genre": int(data.get("genre", 0)) % len(GENRES),
            "location": int(data.get("location", 0)) % len(LOCATIONS_EN),
            "run": int(data.get("run", 0)),
        }
    except Exception:
        log.exception("로테이션 상태 파일 손상 — 초기화")
        return {"topic": 0, "genre": 0, "location": 0, "run": 0}


def _save_rotation_state(state: Dict[str, int]) -> None:
    p = _rotation_state_path()
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)


# ---------------------------------------------------------------------------
# [자율 서사 매트릭스] 16개 연애 주제별 실제 드라마 대사/감정선/시네마틱 프롬프트
# - 하드코딩 '완성 대본'이 아니라, 주제별 서사 재료(대사·감정·화면)의 원천 데이터다.
# - 조합·변주·문장 결합은 엔진이 수행한다(고정 5줄 템플릿 폐기).
# - 씬5 엔딩은 반드시 공식 검색어 '아우라AI데이팅' + 네이버 검색 유도 문구를 포함한다.
# ---------------------------------------------------------------------------
NARRATIVE_MATRIX: Dict[str, Tuple[Tuple[str, str], ...]] = {
    "소개팅 호구조사 빌런": (
        ("소개팅 첫마디가 '연봉 얼마예요?'… 탈출각 맞지?",
         "cinematic close up, woman sighing at cafe table, awkward blind date, cold tone, 35mm film grain"),
        ("야 미쳤냐? 당장 화장실 간다고 하고 튀어! 호구조사 나왔어?",
         "close up of Minjun sitting opposite at the cafe table, sincere and direct expression, warm indoor cafe background bokeh, 50mm lens"),
        ("친구 추천으로 '아우라' 켰는데, AI가 내 취향 딱 맞는 사람만 골라주네?",
         "close up of dating app screen glowing, warm bokeh, 50mm lens"),
        ("취향 완전 찰떡이라 새벽까지 카톡함! 이번 주말에 성수동에서 만나기로 함 ㅋㅋㅋ",
         "woman laughing at phone in bed, warm lamp light, shallow depth of field"),
        ("소개팅 빌런 그만 만나고, 네이버에 아우라AI데이팅 한번 검색해보세요!",
         "wide shot of seongsu-dong street at dusk, couple walking, cold blue tone"),
    ),
    "카톡 읽씹 5시간의 멘붕": (
        ("카톡 보낸 지 5시간째 읽씹… 나 또 차인 거야?",
         "cinematic close up, phone screen with single read receipt, dark bedroom, cold blue tone, 35mm film grain"),
        ("5시간? 그건 그냥 잠수 탄 거야. 답장 기다리지 말고 다른 사람 만나.",
         "close up of Minjun sitting opposite at the cafe table, sincere and direct expression, warm indoor cafe background bokeh, 50mm lens"),
        ("아우라 AI 비서가 첫마디 추천해줬는데 3분 만에 칼답 옴 대박!",
         "close up of chat notification popping up, warm bokeh, 50mm lens"),
        ("대화 코드 진짜 잘 맞아! 어색함 1도 없이 주말 데이트 잡았다.",
         "woman smiling at phone, cafe window light, shallow depth of field"),
        ("읽씹에 인생 낭비하지 말고, 네이버에 아우라AI데이팅 한번 검색해보세요!",
         "wide shot of night street, woman walking confident, cold blue tone"),
    ),
    "자만추 꿈꾸는 방구석 솔로": (
        ("자연스러운 만남만 기다린 지 3년… 현실은 편의점 혼밥이야.",
         "cinematic wide shot, dark room with laptop glow, single person eating alone, 35mm film grain"),
        ("자만추? 그거 그냥 집에 있으면서 로또 기다리는 거야. 나가!",
         "close up of Minjun sitting opposite at the cafe table, sincere and direct expression, warm indoor cafe background bokeh, 50mm lens"),
        ("아우라 켜니까 AI가 내 동네 취향 맞는 사람 매칭해줌… 이게 되네?",
         "close up of app matching animation, warm bokeh, 50mm lens"),
        ("집 앞 카페에서 자연스럽게 만났는데 대화가 술술 풀림 ㅋㅋㅋ",
         "two people talking at small cafe, warm daylight, shallow depth of field"),
        ("방구석 탈출하고, 네이버에 아우라AI데이팅 한번 검색해보세요!",
         "wide shot of neighborhood cafe at dusk, cold blue tone"),
    ),
    "더치페이 100원 단위 계산 빌런": (
        ("더치페이 계산기에 100원 단위까지… 이게 데이트야 가계부야?",
         "cinematic close up, calculator app on phone, restaurant table, cold tone, 35mm film grain"),
        ("100원? 저건 계산이 아니라 인성 검사야. 다음 없어.",
         "close up of Minjun sitting opposite at the cafe table, sincere and direct expression, warm indoor cafe background bokeh, 50mm lens"),
        ("아우라 AI가 대화 흐름 보고 결제 타이밍까지 알려줌… 이게 되네?",
         "close up of app payment tip screen, warm bokeh, 50mm lens"),
        ("이번엔 서로 먼저 사겠다고 난리 ㅋㅋㅋ 이런 게 진짜 데이트지.",
         "two people laughing over receipt, warm daylight, shallow depth of field"),
        ("100원 계산하는 사람 말고, 네이버에 아우라AI데이팅 한번 검색해보세요!",
         "wide shot of restaurant exterior at night, cold blue tone"),
    ),
    "어색한 침묵 30초 뚝딱거림": (
        ("30초째 침묵… 물 마시는 척하는데 컵이 벌써 비었어.",
         "cinematic close up, empty water glass, awkward silence, cold tone, 35mm film grain"),
        ("너 말투가 너무 딱딱하잖아! '진지 드셨어요'가 뭐냐!",
         "close up of Minjun sitting opposite at the cafe table, sincere and direct expression, warm indoor cafe background bokeh, 50mm lens"),
        ("아우라 AI가 대화 주제 실시간으로 던져줌… 침묵 0초 됐어.",
         "close up of app suggesting conversation topic, warm bokeh, 50mm lens"),
        ("웃음 터지고 대화 끊길 틈이 없음! 주말 데이트 바로 잡음 ㅋㅋ",
         "two people laughing hard at cafe, warm daylight, shallow depth of field"),
        ("어색한 침묵 끝내고, 네이버에 아우라AI데이팅 한번 검색해보세요!",
         "wide shot of cafe at dusk, cold blue tone"),
    ),
    "MBTI 과몰입 소개팅": (
        ("소개팅 시작 3분 만에 MBTI 검사지 나옴… 이게 맞아?",
         "cinematic close up, printed MBTI sheet on cafe table, cold tone, 35mm film grain"),
        ("MBTI로 사람 판별한다고? 걔는 너랑 안 맞아. 도망쳐.",
         "close up of Minjun sitting opposite at the cafe table, sincere and direct expression, warm indoor cafe background bokeh, 50mm lens"),
        ("아우라 AI는 MBTI 말고 실제 대화 코드로 매칭해줌… 이게 진짜야.",
         "close up of app matching profile cards, warm bokeh, 50mm lens"),
        ("말 다 통하고 웃음 코드도 맞아서 주말에 또 보기로 함 ㅋㅋ",
         "two people talking animatedly, warm daylight, shallow depth of field"),
        ("MBTI 검사지 들고 오는 사람 말고, 네이버에 아우라AI데이팅 한번 검색해보세요!",
         "wide shot of cafe street at dusk, cold blue tone"),
    ),
    "삼프터인데 고백 안 하는 썸남": (
        ("삼프터 끝났는데 고백 한마디 없음… 나만 썸 탄 거야?",
         "cinematic close up, woman checking phone at night, cold blue tone, 35mm film grain"),
        ("세 번 만나고 말 없으면 그건 썸이 아니라 시간 낭비야. 정리해.",
         "close up of Minjun sitting opposite at the cafe table, sincere and direct expression, warm indoor cafe background bokeh, 50mm lens"),
        ("아우라 AI가 상대 관심도 분석해줌… 애매한 썸은 이제 끝.",
         "close up of app interest analysis screen, warm bokeh, 50mm lens"),
        ("관심 있다고 먼저 말해줬더니 바로 주말 데이트 확정 ㅋㅋㅋ",
         "two people holding hands at cafe, warm daylight, shallow depth of field"),
        ("썸만 타는 사람 붙잡지 말고, 네이버에 아우라AI데이팅 한번 검색해보세요!",
         "wide shot of night street, couple walking, cold blue tone"),
    ),
    "프로필 사진 사기 당한 날": (
        ("프로필이랑 실물이… 이게 같은 사람이라고? 사기 아니야?",
         "cinematic close up, phone profile photo vs real person, cold tone, 35mm film grain"),
        ("야 그건 프로필이 아니라 판타지야! 얼른 나와!",
         "close up of Minjun sitting opposite at the cafe table, sincere and direct expression, warm indoor cafe background bokeh, 50mm lens"),
        ("아우라 AI는 사진 인증된 프로필만 보여줌… 이게 안전하지.",
         "close up of verified profile badge on app, warm bokeh, 50mm lens"),
        ("실물이 더 나은 사람 만남! 대화도 잘 통해서 주말 데이트 ㅋㅋ",
         "two people laughing at cafe table, warm daylight, shallow depth of field"),
        ("사진 사기 그만 당하고, 네이버에 아우라AI데이팅 한번 검색해보세요!",
         "wide shot of cafe street at night, cold blue tone"),
    ),
    "첫마디 질문 대화 공포증": (
        ("첫마디 뭐라고 해야 되지… '안녕하세요'만 열 번 지웠어.",
         "cinematic close up, phone screen with deleted draft messages, dark room, 35mm film grain"),
        ("첫마디 고민하다가 타이밍 다 놓쳐! 그냥 던져, 뭐라도!",
         "close up of Minjun sitting opposite at the cafe table, sincere and direct expression, warm indoor cafe background bokeh, 50mm lens"),
        ("아우라 AI가 첫마디 딱 맞춰서 추천해줌… 복붙했는데 반응 옴!",
         "close up of app first-message suggestion, warm bokeh, 50mm lens"),
        ("첫마디부터 대화가 막힘없이 이어짐! 주말에 보기로 함 ㅋㅋ",
         "two people chatting happily at cafe, warm daylight, shallow depth of field"),
        ("첫마디 공포증 끝내고, 네이버에 아우라AI데이팅 한번 검색해보세요!",
         "wide shot of cafe window at dusk, cold blue tone"),
    ),
    "주말에 혼밥하는 솔로 3년차": (
        ("주말 점심에 혼밥 3년차… 옆 테이블은 다 커플이네.",
         "cinematic wide shot, single person eating alone at restaurant, couples in background, cold tone, 35mm film grain"),
        ("혼밥 3년이면 전문가네. 근데 그거 자랑 아니야. 나와.",
         "close up of Minjun sitting opposite at the cafe table, sincere and direct expression, warm indoor cafe background bokeh, 50mm lens"),
        ("아우라 켜니까 AI가 주말 브런치 같이 갈 사람 매칭해줌… 이게 되네?",
         "close up of app weekend matching screen, warm bokeh, 50mm lens"),
        ("이번 주말엔 혼밥 아니고 둘이 밥 먹음 ㅋㅋㅋ 대화도 잘 통함!",
         "two people eating together laughing, warm daylight, shallow depth of field"),
        ("혼밥 3년차 졸업하고, 네이버에 아우라AI데이팅 한번 검색해보세요!",
         "wide shot of restaurant window at dusk, two people, cold blue tone"),
    ),
    "친구들은 다 연애중": (
        ("단톡방에 커플 사진만 올라옴… 나만 혼자인 거야?",
         "cinematic close up, group chat full of couple photos, dark room, cold blue tone, 35mm film grain"),
        ("너만 혼자야. 근데 그거 핑계 아니고. 지금 당장 뭐라도 해.",
         "close up of Minjun sitting opposite at the cafe table, sincere and direct expression, warm indoor cafe background bokeh, 50mm lens"),
        ("아우라 켜니까 AI가 내 성향 맞는 사람부터 순서대로 보여줌… 이게 되네?",
         "close up of app profile list scrolling, warm bokeh, 50mm lens"),
        ("이번 주말 단톡방에 내 커플 사진 올린다 ㅋㅋㅋ 순서 바뀜!",
         "woman taking couple selfie, warm daylight, shallow depth of field"),
        ("친구들 커플 사진만 보지 말고, 네이버에 아우라AI데이팅 한번 검색해보세요!",
         "wide shot of night street, couple walking hand in hand, cold blue tone"),
    ),
    "소개팅 애프터 신청 타이밍": (
        ("소개팅 끝나고 3시간째… 애프터 신청 언제 해야 돼?",
         "cinematic close up, phone screen with unsent message, cafe exit at night, cold tone, 35mm film grain"),
        ("3시간? 그거 지금 해. 늦으면 걔가 먼저 정리해.",
         "close up of Minjun sitting opposite at the cafe table, sincere and direct expression, warm indoor cafe background bokeh, 50mm lens"),
        ("아우라 AI가 상대 반응 분석해서 애프터 타이밍 딱 잡아줌… 이게 되네?",
         "close up of app timing recommendation screen, warm bokeh, 50mm lens"),
        ("바로 보냈더니 1분 만에 '좋아요' 답장 옴 ㅋㅋㅋ 주말 약속 잡힘!",
         "woman jumping with phone, warm daylight, shallow depth of field"),
        ("애프터 타이밍 놓치지 말고, 네이버에 아우라AI데이팅 한번 검색해보세요!",
         "wide shot of cafe street at night, couple walking, cold blue tone"),
    ),
    "전여친 무용담 떠드는 빌런": (
        ("소개팅인데 전여친 얘기 30분째… 이게 데이트야 상담이야?",
         "cinematic close up, woman forcing smile at cafe table, cold tone, 35mm film grain"),
        ("전여친 무용담? 그건 그냥 미련 남은 거야. 당장 나와.",
         "close up of Minjun sitting opposite at the cafe table, sincere and direct expression, warm indoor cafe background bokeh, 50mm lens"),
        ("아우라 AI는 대화 이력 분석해서 위험 신호 미리 알려줌… 이게 안전하지.",
         "close up of app red flag warning screen, warm bokeh, 50mm lens"),
        ("이번엔 서로 얘기만 해도 시간 가는 줄 모름 ㅋㅋ 주말 데이트 확정!",
         "two people talking deeply at cafe, warm daylight, shallow depth of field"),
        ("전여친 얘기하는 사람 만나지 말고, 네이버에 아우라AI데이팅 한번 검색해보세요!",
         "wide shot of cafe exterior at dusk, cold blue tone"),
    ),
    "연애 세포 바짝 마른 청춘": (
        ("연애 세포 다 죽었나… 누가 고백해도 심장이 안 뛰어.",
         "cinematic close up, woman staring blankly at phone, dark room, cold blue tone, 35mm film grain"),
        ("연애 세포? 그거 안 죽었어. 그냥 안 써서 굳은 거야. 움직여.",
         "close up of Minjun sitting opposite at the cafe table, sincere and direct expression, warm indoor cafe background bokeh, 50mm lens"),
        ("아우라 켜니까 AI가 대화 이어주니까 심장이 다시 뛰기 시작함… 이게 되네?",
         "close up of app chat screen with heartbeat animation, warm bokeh, 50mm lens"),
        ("설렘이라는 게 이거였구나 ㅋㅋㅋ 주말에 만나기로 함!",
         "woman smiling shyly at phone, warm daylight, shallow depth of field"),
        ("연애 세포 살리고 싶으면, 네이버에 아우라AI데이팅 한번 검색해보세요!",
         "wide shot of night street, woman walking with a smile, cold blue tone"),
    ),
    "이상형 눈만 높은 프로 불만러": (
        ("이상형 조건 27개인데… 그거 맞는 사람 지구에 없어.",
         "cinematic close up, long checklist on phone notes, dark room, cold tone, 35mm film grain"),
        ("27개? 그건 이상형이 아니라 견적서야. 조건 다 지워.",
         "close up of Minjun sitting opposite at the cafe table, sincere and direct expression, warm indoor cafe background bokeh, 50mm lens"),
        ("아우라 AI가 내 실제 대화 취향 분석해서 진짜 맞는 사람 찾아줌… 이게 되네?",
         "close up of app compatibility analysis screen, warm bokeh, 50mm lens"),
        ("조건 27개 다 필요 없었음 ㅋㅋ 대화만 통하면 된다는 걸 알았어!",
         "two people laughing together at cafe, warm daylight, shallow depth of field"),
        ("이상형 조건표 버리고, 네이버에 아우라AI데이팅 한번 검색해보세요!",
         "wide shot of cafe street at dusk, couple walking, cold blue tone"),
    ),
    "소개팅 파토 나고 멘붕 온 날": (
        ("소개팅 30분 전에 파토 카톡… 화장 다 하고 나왔는데.",
         "cinematic close up, woman standing alone in front of cafe, cold tone, 35mm film grain"),
        ("파토? 그건 그냥 인연 아니라는 뜻이야. 지금 당장 다른 사람 찾아.",
         "close up of Minjun sitting opposite at the cafe table, sincere and direct expression, warm indoor cafe background bokeh, 50mm lens"),
        ("아우라 켜니까 AI가 바로 근처 매칭 잡아줌… 이게 되네?",
         "close up of app instant matching screen, warm bokeh, 50mm lens"),
        ("파토 난 날에 더 잘 맞는 사람 만남 ㅋㅋㅋ 오히려 잘된 거지!",
         "two people laughing at cafe table, warm daylight, shallow depth of field"),
        ("소개팅 파토에 멘붕 오지 말고, 네이버에 아우라AI데이팅 한번 검색해보세요!",
         "wide shot of cafe street at night, couple walking, cold blue tone"),
    ),
}

# 씬5 엔딩 공식 규격 (붙여쓰기 100% 필수 — 브랜드 검색 유도)
BRAND_SEARCH_KEYWORD = "아우라AI데이팅"
BRAND_CTA = "네이버에 아우라AI데이팅 한번 검색해보세요"
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
GEMINI_TIMEOUT_SEC = 45.0


def _collect_gemini_keys() -> List[str]:
    """환경변수에서 Gemini 키를 수집한다(GEMINI_API_KEY, GEMINI_KEY_1~3)."""
    keys: List[str] = []
    primary = os.environ.get("GEMINI_API_KEY", "").strip()
    if primary:
        keys.append(primary)
    for i in range(1, 4):
        k = os.environ.get(f"GEMINI_KEY_{i}", "").strip()
        if k and k not in keys:
            keys.append(k)
    return keys


def _build_gemini_prompt(topic: str, genre: str, run_no: int) -> str:
    return (
        f"너는 한국 2030 데이팅 앱 '{BRAND_NAME}'의 숏폼 드라마 작가다. "
        f"주제='{topic}', 장르='{genre}', 회차={run_no}. "
        "5씬 시나리오를 JSON으로만 출력하라. 설명/마크다운 금지.\n"
        "★ 절대 금지: 오페라, 소설, 인생 명언, 3인칭 나레이션, 시적 비유, 문어체. "
        "2030 유튜브 쇼츠 감성의 날것 그대로의 극사실주의 구어체 대화로만 작성하라. "
        "실제 카톡/전화 통화에서 할 법한 말투(반말/존댓말 혼용, ㅋㅋ, ㅠㅠ, 헐, 대박)를 써라.\n"
        "씬 구성(고정):\n"
        "  씬1 = 서연(여) 한숨 훅 — 현실 소개팅/연애의 황당한 상황 (3초)\n"
        "  씬2 = 민준(남) 팩폭 티키타카 — 남사친의 경악/탈출 권유 (4초)\n"
        "  씬3 = 서연(여) 아우라 솔루션 체감 — AI 취향 매칭/대화 비서 감탄 (4초)\n"
        "  씬4 = 서연(여) 데이트 약속 성사 — 티키타카 폭발, 주말 약속 (5초)\n"
        "  씬5 = 서연(여) 검색유도 엔딩 — 사이다 클로징 (4초)\n"
        "각 씬 narration은 한국어 실제 대사 1~2문장(25~80자). "
        "image_prompt는 영어 시네마틱 프롬프트(카메라/조명/렌즈 포함).\n"
        f"씬5 narration에는 반드시 '{BRAND_SEARCH_KEYWORD}'와 '{BRAND_CTA}' 문구를 포함하라.\n"
        '출력 스키마: {"scenes":[{"index":1,"narration":"...","image_prompt":"..."}, ... 5개]}'
    )


def _call_gemini_scenario(topic: str, genre: str, run_no: int) -> Optional[List[Dict[str, str]]]:
    """Gemini Flash 호출로 5씬 시나리오를 자율 집필한다. 실패 시 None(폴백 유도)."""
    keys = _collect_gemini_keys()
    if not keys:
        log.info("Gemini 키 부재 — 자율 서사 매트릭스 폴백 사용")
        return None

    import urllib.error
    import urllib.request

    payload = json.dumps({
        "contents": [{"parts": [{"text": _build_gemini_prompt(topic, genre, run_no)}]}],
        "generationConfig": {"temperature": 1.0, "maxOutputTokens": 2048, "responseMimeType": "application/json"},
    }).encode("utf-8")

    for idx, key in enumerate(keys, start=1):
        url = GEMINI_ENDPOINT.format(model=GEMINI_MODEL, key=key)
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=GEMINI_TIMEOUT_SEC) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            text = body["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(text)
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
            log.info("Gemini 자율 집필 성공(key#%d, topic='%s')", idx, topic)
            return out
        except Exception as e:
            log.warning("Gemini 호출 실패(key#%d): %s", idx, e)
            continue
    log.warning("Gemini 전 키 실패 — 자율 서사 매트릭스 폴백")
    return None


def _compose_from_matrix(topic: str, genre: str, run_no: int) -> List[Dict[str, str]]:
    """16주제 극사실주의 매트릭스 1:1 조회 — 문장 이어붙이기 레거시 완전 폐기.

    불변식:
      1) NARRATIVE_MATRIX[topic] 은 정확히 5개의 (대사, 프롬프트) 튜플이다.
      2) 조합/변주/문장 결합을 하지 않는다. 튜플을 그대로 1:1 매핑한다.
      3) 미등록 주제는 로테이션 인덱스로 결정론적 대체(자리표시자 금지).
    """
    scenes = NARRATIVE_MATRIX.get(topic)
    if scenes is None:
        scenes = NARRATIVE_MATRIX[TOPICS[run_no % len(TOPICS)]]
        log.warning("주제 '%s' 매트릭스 미등록 — 대체 주제 사용", topic)

    if len(scenes) != 5:
        raise SpecValidationError(
            f"매트릭스 씬 개수 위반: topic='{topic}' → {len(scenes)}개 (정확히 5 필요)"
        )

    return [
        {"narration": narr, "image_prompt": prm}
        for narr, prm in scenes
    ]


def _build_autonomous_scenes(topic: str, genre: str, run_no: int,
                             location_en: str = "") -> List[SceneSpec]:
    """자율 시나리오 생성 엔진 — Gemini 우선, 실패 시 16주제 서사 매트릭스 폴백.

    불변식:
      1) SCENE_PLAN(3/4/4/5/4, Aoede-Puck-Aoede-Puck-Aoede) 규격 엄수.
      2) 씬5 narration에 '아우라AI데이팅' + 네이버 검색 유도 문구 강제 주입.
      3) 자리표시자/더미 텍스트 생성 금지.
      4) location_en 은 5씬 전건에 동일 주입 — 한 편 안의 공간 연속성 100% 보장.
    """
    drafted = _call_gemini_scenario(topic, genre, run_no)
    if drafted is None:
        drafted = _compose_from_matrix(topic, genre, run_no)

    scenes: List[SceneSpec] = []
    for i, ((dur, voice), item) in enumerate(zip(SCENE_PLAN, drafted), start=1):
        narr = item["narration"].strip()
        prm = item["image_prompt"].strip()
        if i == 5:
            # 엔딩 규격 강제: 공식 검색어 + 네이버 검색 유도 문구 100% 포함
            if BRAND_SEARCH_KEYWORD not in narr:
                narr = f"{narr} {BRAND_SEARCH_KEYWORD}."
            if "네이버" not in narr or BRAND_SEARCH_KEYWORD not in narr:
                narr = f"{narr} {BRAND_CTA}."
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


def build_default_5scenes_spec() -> List[SceneSpec]:
    """상태 파일 기반 자율 로테이션 5씬 스펙 팩토리 (SSOT 진입점).

    불변식:
      1) 반환 타입은 반드시 List[SceneSpec].
      2) 반환 전 SpecValidator.validate_all 통과 (fail-fast).
      3) 하드코딩 정적 대본 금지 — 16주제/8장르/16장소 3축 로테이션.
      4) 상태 파일 갱신은 성공 반환 직전에만 수행.
      5) location_en 은 5씬 전건 동일 주입 → 한 편 내 공간 연속성 100%.
    """
    state = _load_rotation_state()
    topic = TOPICS[state["topic"]]
    genre = GENRES[state["genre"]]
    location_idx = state.get("location", 0) % len(LOCATIONS_EN)
    location_ko = LOCATIONS_KO[location_idx]
    location_en = LOCATIONS_EN[location_idx]
    run_no = state["run"] + 1

    scenes = _build_autonomous_scenes(topic, genre, run_no, location_en=location_en)
    SpecValidator.validate_all(scenes, 0.0, "default_5scenes")

    _save_rotation_state({
        "topic": (state["topic"] + 1) % len(TOPICS),
        "genre": (state["genre"] + 1) % len(GENRES),
        "location": (location_idx + 1) % len(LOCATIONS_EN),
        "run": run_no,
    })
    log.info("자율 로테이션: run=%d topic='%s' genre='%s' location='%s'",
             run_no, topic, genre, location_ko)
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
OUTPUT_BRAND_DIR = "Aura"


def allocate_output_dir(prefix: str = DEFAULT_OUTPUT_PREFIX) -> Path:
    """타임스탬프 기반 산출물 폴더를 원자적으로 할당한다.

    표준 경로: {바탕화면}/한국 숏폼_산출물/Aura/{prefix}_{YYYYMMDD}_{HHMMSS}{suffix}
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