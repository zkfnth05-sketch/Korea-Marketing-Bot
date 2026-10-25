# -*- coding: utf-8 -*-
"""
Drama Cut Budget
================
Wan S2V 81프레임 상한 기반 컷 대사 글자수 예산 검증기 (CutBudgetValidator).

확정 사실:
    - Wan S2V 컷당 최대 81프레임, 16fps -> S2V_MAX_SEC = 81/16 = 5.0625초
    - 대사 오디오가 5.0625초를 넘으면 영상이 대사를 따라가지 못한다.
    - 숏폼 배속 SHORTS_SPEECH_SPEED = 1.20 (atempo)
    - edge-tts: ko-KR-HyunsuNeural(여) / ko-KR-InJoonNeural(남)
    - ffmpeg: imageio_ffmpeg.get_ffmpeg_exe()

실측 문제(이 모듈이 해결하는 대상):
    - 기존 글자수 규격 cut3 30~42자는 약 5~7초 -> 5.0625초 상한과 모순
    - 폴백 56컷 중 16컷 규격이탈 / 33컷 81프레임 초과 추정

설계 원칙:
    - 추정치로 조용히 대체 금지. edge-tts 실패 시 logger.error(exc_info=True) 후 재발생.
    - 절단 금지. 위반은 보고만 한다.
    - 캐시는 원자적 쓰기(tempfile -> fsync -> os.replace).
    - try-except pass 금지.
"""

from __future__ import annotations

import asyncio
import json
import logging
import math
import os
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import edge_tts
import imageio_ffmpeg

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 루트 산출 (하드코딩 금지)
#   <root>/modules/drama_engine/drama_cut_budget.py
#   parents[0]=drama_engine, parents[1]=modules, parents[2]=<root>
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
DATA_DIR: Path = PROJECT_ROOT / "data"
DEFAULT_CACHE_PATH: Path = DATA_DIR / "drama_cps_calibration.json"

# ---------------------------------------------------------------------------
# 확정 상수
# ---------------------------------------------------------------------------
S2V_MAX_FRAMES: int = 81
S2V_FPS: int = 16
S2V_MAX_SEC: float = S2V_MAX_FRAMES / S2V_FPS  # 5.0625

# 캘리브레이션(실측 cps 산출) 시 합성 오디오에 적용한 atempo 값.
# 이 값이 cps 의 단일 원천이며, 다른 배속은 이 기준으로 선형 스케일한다.
CALIBRATION_SPEED: float = 1.20
# 하위 호환 별칭 (기존 코드/문서가 SHORTS_SPEECH_SPEED 를 참조)
SHORTS_SPEECH_SPEED: float = CALIBRATION_SPEED

# 대표님 확정: 기본 배속 1.25, 변주 1.20~1.30
DEFAULT_VOICE_SPEED: float = 1.25
VOICE_SPEED_MIN: float = 1.20
VOICE_SPEED_MAX: float = 1.30
# scale_cps 허용 절대 범위 (atempo 안전 구간)
SPEED_SCALE_MIN: float = 1.0
SPEED_SCALE_MAX: float = 2.0

VOICE_FEMALE: str = "ko-KR-HyunsuNeural"
VOICE_MALE: str = "ko-KR-InJoonNeural"

# 역할별 min 비율 (max 대비)
ROLE_MIN_RATIO: Dict[str, float] = {
    "cut1": 0.42,  # hook
    "cut2": 0.62,  # dialogue
    "cut3": 0.72,  # solution
    "cut4": 0.50,  # cta
}
ROLE_LABEL: Dict[str, str] = {
    "cut1": "hook",
    "cut2": "dialogue",
    "cut3": "solution",
    "cut4": "cta",
}
# role 문자열 -> cut_id 역매핑 (FALLBACK_TEMPLATES 는 role 만 갖는다)
ROLE_TO_CUT_ID: Dict[str, str] = {v: k for k, v in ROLE_LABEL.items()}

# 기본 내장 샘플 (길이 다양한 한국어 대화체 8개)
DEFAULT_SAMPLES: List[str] = [
    "안녕하세요.",
    "오늘 진짜 좋은 일이 있었어요.",
    "그 사람이 먼저 말을 걸어왔는데, 생각보다 훨씬 다정했어요.",
    "저는 그냥 웃고 있었는데, 어느 순간 대화가 끊기지 않고 계속 이어지더라고요.",
    "솔직히 처음엔 별 기대 안 했는데, 두 번째 만남에서 완전히 생각이 바뀌었습니다.",
    "연락이 늦어도 불안하지 않고, 그 사람의 하루가 궁금해지는 관계가 좋더라고요.",
    "결국 중요한 건 조건이 아니라, 내 말을 끝까지 들어주는 사람이라는 걸 알았어요.",
    "지금 바로 검색해보시면, 생각보다 가까운 곳에 답이 있을지도 모릅니다.",
]

_DURATION_RE = re.compile(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)")


class CutBudgetValidator:
    """컷 대사 글자수 예산 검증기."""

    def __init__(self, cache_path: Optional[Path] = None) -> None:
        self.cache_path: Path = (
            Path(cache_path) if cache_path is not None else DEFAULT_CACHE_PATH
        )
        self.ffmpeg_exe: str = imageio_ffmpeg.get_ffmpeg_exe()
        if not os.path.isfile(self.ffmpeg_exe):
            raise FileNotFoundError(f"ffmpeg 실행 파일 없음: {self.ffmpeg_exe}")

    # -- 캐시 --------------------------------------------------------------
    def _load_cache(self) -> Optional[Dict[str, Any]]:
        if not self.cache_path.exists():
            return None
        try:
            with open(self.cache_path, "r", encoding="utf-8") as fp:
                raw = json.load(fp)
        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.error("cps 캐시 손상: %s -> 재측정", self.cache_path, exc_info=True)
            return None
        except OSError:
            logger.error("cps 캐시 읽기 실패: %s", self.cache_path, exc_info=True)
            raise
        if not isinstance(raw, dict):
            logger.error("cps 캐시 구조 이상(dict 아님): %s -> 재측정", self.cache_path)
            return None
        for key in ("female", "male"):
            val = raw.get(key)
            if not isinstance(val, (int, float)) or val <= 0:
                logger.error("cps 캐시 값 이상(%s=%r) -> 재측정", key, val)
                return None
        return raw

    def _save_cache(self, payload: Dict[str, Any]) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(
            prefix=f".{self.cache_path.stem}_",
            suffix=".tmp",
            dir=str(self.cache_path.parent),
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fp:
                json.dump(payload, fp, ensure_ascii=False, indent=2)
                fp.flush()
                os.fsync(fp.fileno())
            os.replace(tmp_name, self.cache_path)
        except OSError:
            logger.error("cps 캐시 원자적 쓰기 실패: %s", self.cache_path, exc_info=True)
            if os.path.exists(tmp_name):
                try:
                    os.remove(tmp_name)
                except OSError:
                    logger.error("임시 파일 정리 실패: %s", tmp_name, exc_info=True)
            raise

    # -- 합성 / 측정 -------------------------------------------------------
    @staticmethod
    def _count_chars(text: str) -> int:
        """공백 포함 글자수."""
        return len(text)

    async def _synthesize(self, text: str, voice: str, out_path: Path) -> None:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(out_path))

    def _apply_atempo(self, src: Path, dst: Path, speed: float) -> None:
        cmd = [
            self.ffmpeg_exe,
            "-y",
            "-i",
            str(src),
            "-filter:a",
            f"atempo={speed}",
            str(dst),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if proc.returncode != 0:
            logger.error("ffmpeg atempo 실패(rc=%s): %s", proc.returncode, proc.stderr[-800:])
            raise RuntimeError(f"ffmpeg atempo 실패 rc={proc.returncode}")

    def _probe_duration(self, path: Path) -> float:
        """ffmpeg -i 출력의 Duration 파싱 (ffprobe 미의존 안정 방식)."""
        cmd = [self.ffmpeg_exe, "-i", str(path)]
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        stderr = proc.stderr or ""
        match = _DURATION_RE.search(stderr)
        if not match:
            logger.error("Duration 파싱 실패: %s", path)
            raise RuntimeError(f"Duration 파싱 실패: {path}")
        h, m, s = match.groups()
        return int(h) * 3600 + int(m) * 60 + float(s)

    def _measure_gender(
        self, samples: Sequence[str], voice: str, work_dir: Path, tag: str
    ) -> Tuple[float, int, float]:
        """여/남 한쪽 실측 -> (cps, 총 글자수, 총 초)."""
        total_chars = 0
        total_sec = 0.0
        for i, text in enumerate(samples):
            raw = work_dir / f"{tag}_{i:02d}_raw.mp3"
            fast = work_dir / f"{tag}_{i:02d}_fast.mp3"
            try:
                asyncio.run(self._synthesize(text, voice, raw))
            except Exception:
                logger.error(
                    "edge-tts 합성 실패(voice=%s, idx=%d) -> 추정치 대체 금지, 재발생",
                    voice,
                    i,
                    exc_info=True,
                )
                raise
            self._apply_atempo(raw, fast, SHORTS_SPEECH_SPEED)
            sec = self._probe_duration(fast)
            total_chars += self._count_chars(text)
            total_sec += sec
        if total_sec <= 0:
            raise RuntimeError(f"{tag} 실측 총 초가 0 이하입니다.")
        return total_chars / total_sec, total_chars, total_sec

    def calibrate_chars_per_sec(
        self, samples: Optional[List[str]] = None, force: bool = False
    ) -> Dict[str, Any]:
        """여/남 초당 글자수(cps) 실측. 캐시 우선, force=True 면 재측정."""
        if not force:
            cached = self._load_cache()
            if cached is not None:
                logger.info("cps 캐시 재사용: %s", self.cache_path)
                return cached

        use_samples: List[str] = list(samples) if samples else list(DEFAULT_SAMPLES)
        if len(use_samples) < 6:
            raise ValueError(f"샘플은 6개 이상이어야 합니다. (입력: {len(use_samples)}개)")

        with tempfile.TemporaryDirectory(prefix="drama_cps_") as tmp:
            work_dir = Path(tmp)
            female_cps, f_chars, f_sec = self._measure_gender(
                use_samples, VOICE_FEMALE, work_dir, "f"
            )
            male_cps, m_chars, m_sec = self._measure_gender(
                use_samples, VOICE_MALE, work_dir, "m"
            )

        payload: Dict[str, Any] = {
            "female": round(female_cps, 4),
            "male": round(male_cps, 4),
            "measured_at": datetime.now().isoformat(timespec="seconds"),
            "samples": len(use_samples),
            "detail": {
                "female": {
                    "voice": VOICE_FEMALE,
                    "chars": f_chars,
                    "sec": round(f_sec, 4),
                },
                "male": {
                    "voice": VOICE_MALE,
                    "chars": m_chars,
                    "sec": round(m_sec, 4),
                },
                "atempo": SHORTS_SPEECH_SPEED,
                "s2v_max_sec": S2V_MAX_SEC,
            },
        }
        self._save_cache(payload)
        return payload

    # -- 배속 스케일 -------------------------------------------------------
    @staticmethod
    def scale_cps(cps_by_gender: Dict[str, float], speed: float) -> Dict[str, float]:
        """캘리브레이션 cps 를 실제 적용 배속 기준으로 선형 스케일한다.

        cps_scaled = cps * (speed / CALIBRATION_SPEED)

        배속이 빨라지면 같은 시간에 더 많은 글자를 말할 수 있으므로
        초당 글자수는 배속에 정비례한다. 여/남 모두 동일 비율로 스케일한다.

        Args:
            cps_by_gender: {"female": float, "male": float} (CALIBRATION_SPEED 기준)
            speed: 실제 적용할 atempo 배속 (1.0 ~ 2.0)

        Returns:
            {"female": float, "male": float} 스케일된 cps

        Raises:
            ValueError: speed 가 1.0~2.0 밖이거나 cps 값이 비정상일 때
        """
        if not isinstance(speed, (int, float)) or isinstance(speed, bool):
            raise ValueError(f"speed 는 숫자여야 합니다: {speed!r}")
        speed_f = float(speed)
        if not (SPEED_SCALE_MIN <= speed_f <= SPEED_SCALE_MAX):
            raise ValueError(
                f"speed 는 {SPEED_SCALE_MIN} ~ {SPEED_SCALE_MAX} 범위여야 합니다: {speed_f!r}"
            )
        if not isinstance(cps_by_gender, dict):
            raise TypeError("cps_by_gender 는 dict 여야 합니다.")

        ratio = speed_f / CALIBRATION_SPEED
        scaled: Dict[str, float] = {}
        for key in ("female", "male"):
            if key not in cps_by_gender:
                raise ValueError(f"cps_by_gender 에 '{key}' 가 없습니다.")
            val = cps_by_gender[key]
            if not isinstance(val, (int, float)) or isinstance(val, bool) or val <= 0:
                raise ValueError(f"cps_by_gender['{key}'] 는 양수여야 합니다: {val!r}")
            scaled[key] = round(float(val) * ratio, 4)
        return scaled

    # -- 예산 --------------------------------------------------------------
    def compute_char_budget(
        self,
        cut_id: str,
        cps: float,
        margin: float = 0.92,
        speed: float = DEFAULT_VOICE_SPEED,
    ) -> Tuple[int, int]:
        """(min_chars, max_chars). max 는 81프레임 상한을 절대 넘지 않는다.

        cps 는 CALIBRATION_SPEED 기준 실측값이며, 내부에서 speed 로 스케일한다.
        """
        if cut_id not in ROLE_MIN_RATIO:
            raise ValueError(
                f"알 수 없는 cut_id: {cut_id!r} (허용: {sorted(ROLE_MIN_RATIO)})"
            )
        if not isinstance(cps, (int, float)) or cps <= 0:
            raise ValueError(f"cps 는 양수여야 합니다: {cps!r}")
        if not (0 < margin <= 1.0):
            raise ValueError(f"margin 은 0 초과 1 이하여야 합니다: {margin!r}")

        # 당일 배속 반영: 캘리브레이션 cps -> 실제 적용 배속 cps
        scaled = self.scale_cps({"female": float(cps), "male": float(cps)}, speed)
        cps_eff = scaled["female"]

        max_chars = int(math.floor(S2V_MAX_SEC * cps_eff * float(margin)))
        if max_chars < 1:
            raise ValueError(
                f"max_chars 가 1 미만입니다(cps={cps}, speed={speed}, margin={margin})"
            )
        min_chars = int(math.floor(max_chars * ROLE_MIN_RATIO[cut_id]))
        if min_chars < 1:
            min_chars = 1
        return min_chars, max_chars

    def validate_cuts(
        self,
        cuts: List[Dict[str, Any]],
        cps_by_gender: Dict[str, float],
        speed: float = DEFAULT_VOICE_SPEED,
    ) -> List[Dict[str, Any]]:
        """컷별 예산 검증. 절단 금지, 위반 보고만.

        cps_by_gender 는 CALIBRATION_SPEED 기준 실측값이며,
        내부에서 speed 로 스케일한 값을 사용한다.
        """
        if not isinstance(cuts, list):
            raise TypeError("cuts 는 list 여야 합니다.")
        for key in ("female", "male"):
            if key not in cps_by_gender:
                raise ValueError(f"cps_by_gender 에 '{key}' 가 없습니다.")

        # 당일 배속 반영
        cps_scaled = self.scale_cps(cps_by_gender, speed)

        results: List[Dict[str, Any]] = []
        for idx, cut in enumerate(cuts):
            if not isinstance(cut, dict):
                raise TypeError(f"cuts[{idx}] 는 dict 여야 합니다.")

            cut_id = cut.get("cut_id")
            if not cut_id:
                role = str(cut.get("role", "")).strip()
                cut_id = ROLE_TO_CUT_ID.get(role)
            if cut_id not in ROLE_MIN_RATIO:
                raise ValueError(
                    f"cuts[{idx}] cut_id/role 판별 불가: "
                    f"cut_id={cut.get('cut_id')!r}, role={cut.get('role')!r}"
                )

            gender = str(cut.get("speaker_gender", "")).strip().lower()
            if gender not in ("female", "male"):
                raise ValueError(
                    f"cuts[{idx}] speaker_gender 는 female/male 이어야 합니다: {gender!r}"
                )

            speech = cut.get("speech", "")
            if not isinstance(speech, str):
                raise TypeError(f"cuts[{idx}] speech 는 str 여야 합니다.")
            chars = self._count_chars(speech)

            cps = float(cps_scaled[gender])
            min_chars, max_chars = self.compute_char_budget(
                cut_id, cps, speed=speed
            )
            estimated_sec = round(chars / cps, 4) if cps > 0 else 0.0

            reasons: List[str] = []
            if chars < min_chars:
                reasons.append(f"min 미달({chars}<{min_chars})")
            if chars > max_chars:
                reasons.append(f"max 초과({chars}>{max_chars})")
            if estimated_sec > S2V_MAX_SEC:
                reasons.append(
                    f"81프레임 초과({estimated_sec}s>{S2V_MAX_SEC}s)"
                )

            results.append(
                {
                    "cut_id": cut_id,
                    "chars": chars,
                    "min": min_chars,
                    "max": max_chars,
                    "ok": not reasons,
                    "estimated_sec": estimated_sec,
                    "reason": "OK" if not reasons else " / ".join(reasons),
                }
            )
        return results

    # -- 프롬프트 주입 -----------------------------------------------------
    def build_prompt_budget_text(
        self,
        cps_by_gender: Dict[str, float],
        speed: float = DEFAULT_VOICE_SPEED,
    ) -> str:
        """Gemini 대본 프롬프트 주입용 컷별 글자수 범위 문구(롤 한글).

        cps_by_gender 는 CALIBRATION_SPEED 기준 실측값이며,
        내부에서 speed 로 스케일한 값을 사용한다.
        """
        for key in ("female", "male"):
            if key not in cps_by_gender:
                raise ValueError(f"cps_by_gender 에 '{key}' 가 없습니다.")

        # 당일 배속 반영
        cps_scaled = self.scale_cps(cps_by_gender, speed)

        lines: List[str] = []
        lines.append(
            f"[컷 대사 글자수 규격 — 실측 기반] "
            f"Wan S2V 상한 {S2V_MAX_FRAMES}프레임/{S2V_FPS}fps = {S2V_MAX_SEC}초, "
            f"배속 atempo={float(speed):.2f}"
        )
        lines.append(
            f"실측 초당 글자수(공백 포함, 배속 atempo={float(speed):.2f} 기준): "
            f"여성 {cps_scaled['female']:.2f}자/초, "
            f"남성 {cps_scaled['male']:.2f}자/초"
        )
        lines.append("아래 범위를 반드시 지켜라. 초과하면 영상이 대사를 따라가지 못한다.")
        for cut_id in ("cut1", "cut2", "cut3", "cut4"):
            f_min, f_max = self.compute_char_budget(
                cut_id, cps_by_gender["female"], speed=speed
            )
            m_min, m_max = self.compute_char_budget(
                cut_id, cps_by_gender["male"], speed=speed
            )
            lines.append(
                f"- {cut_id} ({ROLE_LABEL[cut_id]}): "
                f"여성 {f_min}~{f_max}자 / 남성 {m_min}~{m_max}자 "
                f"(공백 포함, 최대 {S2V_MAX_SEC}초)"
            )
        lines.append(
            "- 한 컷에 한 화자만 말한다. 문장을 자르지 말고, 범위 안에서 완결된 문장으로 쓴다."
        )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 자체 점검
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="[%(levelname)s] %(name)s: %(message)s"
    )

    print("=" * 74)
    print("CutBudgetValidator 자체 점검")
    print("=" * 74)
    print(f"PROJECT_ROOT   : {PROJECT_ROOT}")
    print(f"S2V_MAX_SEC    : {S2V_MAX_SEC} ({S2V_MAX_FRAMES}f / {S2V_FPS}fps)")
    print(f"SPEECH_SPEED   : {SHORTS_SPEECH_SPEED}")

    validator = CutBudgetValidator()
    print(f"CACHE_PATH     : {validator.cache_path}")
    print(f"FFMPEG         : {validator.ffmpeg_exe}")

    # [1] 실측 캘리브레이션
    print("\n[1] edge-tts 실측 캘리브레이션 (force=True)")
    calib = validator.calibrate_chars_per_sec(force=True)
    print(f"    female cps = {calib['female']}  ({calib['detail']['female']})")
    print(f"    male   cps = {calib['male']}  ({calib['detail']['male']})")
    print(f"    samples    = {calib['samples']}")
    print(f"    measured_at= {calib['measured_at']}")

    cps_by_gender = {"female": calib["female"], "male": calib["male"]}

    # [2] 컷별 예산 표
    print("\n[2] 컷별 글자수 예산 표 (margin=0.92)")
    print(f"    {'cut_id':<7}{'role':<10}{'여 min~max':<14}{'남 min~max':<14}{'여 최대초':<10}{'남 최대초'}")
    for cut_id in ("cut1", "cut2", "cut3", "cut4"):
        f_min, f_max = validator.compute_char_budget(cut_id, cps_by_gender["female"])
        m_min, m_max = validator.compute_char_budget(cut_id, cps_by_gender["male"])
        f_sec = round(f_max / cps_by_gender["female"], 3)
        m_sec = round(m_max / cps_by_gender["male"], 3)
        print(
            f"    {cut_id:<7}{ROLE_LABEL[cut_id]:<10}"
            f"{f'{f_min}~{f_max}':<14}{f'{m_min}~{m_max}':<14}"
            f"{f_sec:<10}{m_sec}"
        )

    # [2-1] 배속별 컷 예산 표 (1.20 / 1.25 / 1.30)
    print("\n[2-1] 배속별 컷 예산 표 (CALIBRATION_SPEED 기준 cps 를 배속으로 스케일)")
    print(f"    CALIBRATION_SPEED = {CALIBRATION_SPEED}")
    print(f"    DEFAULT_VOICE_SPEED = {DEFAULT_VOICE_SPEED}")
    print(f"    허용 배속 범위 = {VOICE_SPEED_MIN} ~ {VOICE_SPEED_MAX}")
    for sp in (1.20, 1.25, 1.30):
        scaled = validator.scale_cps(cps_by_gender, sp)
        print(
            f"\n    [배속 atempo={sp:.2f}] "
            f"여 {scaled['female']:.2f}자/초 / 남 {scaled['male']:.2f}자/초"
        )
        print(
            f"    {'cut_id':<7}{'role':<10}{'여 min~max':<14}"
            f"{'남 min~max':<14}{'여 최대초':<10}{'남 최대초'}"
        )
        for cut_id in ("cut1", "cut2", "cut3", "cut4"):
            f_min, f_max = validator.compute_char_budget(
                cut_id, cps_by_gender["female"], speed=sp
            )
            m_min, m_max = validator.compute_char_budget(
                cut_id, cps_by_gender["male"], speed=sp
            )
            f_sec = round(f_max / scaled["female"], 3)
            m_sec = round(m_max / scaled["male"], 3)
            print(
                f"    {cut_id:<7}{ROLE_LABEL[cut_id]:<10}"
                f"{f'{f_min}~{f_max}':<14}{f'{m_min}~{m_max}':<14}"
                f"{f_sec:<10}{m_sec}"
            )

    # [2-2] scale_cps 범위 검증
    print("\n[2-2] scale_cps 범위 검증")
    for bad in (0.99, 2.01):
        try:
            validator.scale_cps(cps_by_gender, bad)
        except ValueError as exc:
            print(f"    speed={bad} -> ValueError 정상 발생: {exc}")
        else:
            print(f"    speed={bad} -> !! ValueError 미발생 (오류)")
    print(
        f"    speed=1.25 스케일 비율 = "
        f"{1.25 / CALIBRATION_SPEED:.6f} "
        f"(여 {cps_by_gender['female']:.4f} -> "
        f"{validator.scale_cps(cps_by_gender, 1.25)['female']:.4f})"
    )

    # [3] FALLBACK_TEMPLATES 14종 56컷 검증
    print("\n[3] FALLBACK_TEMPLATES 14종(56컷) 검증")
    from modules.drama_engine.drama_scenario_director import FALLBACK_TEMPLATES

    all_cuts: List[Dict[str, Any]] = []
    for tpl in FALLBACK_TEMPLATES:
        for cut in tpl.get("cuts", []):
            all_cuts.append(
                {
                    "cut_id": ROLE_TO_CUT_ID.get(str(cut.get("role", "")).strip()),
                    "role": cut.get("role"),
                    "speaker_gender": cut.get("speaker_gender"),
                    "speech": cut.get("speech", ""),
                    "char_count": len(cut.get("speech", "")),
                    "template_id": tpl.get("id"),
                }
            )
    print(f"    템플릿 수 = {len(FALLBACK_TEMPLATES)}, 총 컷 수 = {len(all_cuts)}")

    results = validator.validate_cuts(
        all_cuts, cps_by_gender, speed=DEFAULT_VOICE_SPEED
    )
    print(f"    적용 배속 = {DEFAULT_VOICE_SPEED}")
    violations = [r for r in results if not r["ok"]]
    over_81 = [r for r in results if r["estimated_sec"] > S2V_MAX_SEC]
    under_min = [r for r in results if r["chars"] < r["min"]]
    over_max = [r for r in results if r["chars"] > r["max"]]

    print(f"    위반 컷 수        = {len(violations)} / {len(results)}")
    print(f"    81프레임 초과 컷  = {len(over_81)}")
    print(f"    min 미달 컷       = {len(under_min)}")
    print(f"    max 초과 컷       = {len(over_max)}")

    print("\n    [위반 상세]")
    for r in violations:
        print(
            f"    {r['cut_id']:<6} chars={r['chars']:<3} "
            f"range={r['min']}~{r['max']:<3} est={r['estimated_sec']:<7} {r['reason']}"
        )

    # [4] 프롬프트 주입 문구
    print("\n[4] build_prompt_budget_text 출력")
    for line in validator.build_prompt_budget_text(
        cps_by_gender, speed=DEFAULT_VOICE_SPEED
    ).splitlines():
        print(f"    {line}")

    # [5] 캐시 재사용 확인
    print("\n[5] 캐시 재사용 확인 (force=False)")
    reused = validator.calibrate_chars_per_sec(force=False)
    print(f"    캐시 파일 존재 = {validator.cache_path.exists()}")
    print(f"    재사용 값 일치 = {reused['female'] == calib['female'] and reused['male'] == calib['male']}")

    print("\n" + "=" * 74)
    print("자체 점검 완료")
    print("=" * 74)
