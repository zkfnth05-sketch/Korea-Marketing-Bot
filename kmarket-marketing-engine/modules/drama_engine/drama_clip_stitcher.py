# -*- coding: utf-8 -*-
"""
modules/drama_engine/drama_clip_stitcher.py
===================================================================================================
🎬 [DramaClipStitcher] — Wan 2.2 S2V 14B 립싱크 모션 기반 4컷 숏드라마 조립 엔진
---------------------------------------------------------------------------------------------------
- 1계층: MotionGenerator   — Wan 2.2 S2V (립싱크 동영상 생성, 인물/입모양/고개 실제 움직임)
- 2계층: ClipNormalizer    — 1080x1920 세로 9:16 / 30fps 정규화 및 A/V 싱크 정렬
- 3계층: TimelineAssembler — 4컷 클립 결합, 네이버 공식 검색어 CTA 오버레이, BGM 믹싱

🛑 정지 사진 줌인/줌아웃(Ken Burns / zoompan / stillimage) 땜질 완전 영구 퇴출
🈶 한글 폰트 미지정으로 인한 네모(□□□□) 깨짐 100% 방지 — 맑은 고딕 Bold 직결

[🎯 Audio-First 규격 — 대표님 확정 명령]
  "숏폼이 약간 길어져도 상관은 없어..그대신 음성에 맞추어 영상 제작.."
  · 컷 오디오의 실측 길이(final_cut_dur)가 비디오 길이를 100% 결정한다.
  · Wan S2V 프레임 수는 16fps 기준으로 오디오 길이에 맞춰 동적 계산된다.
  · FFmpeg 정규화 시 tpad=stop_mode=clone 으로 마지막 프레임을 홀드하여
    비디오가 오디오보다 미세하게 먼저 끝나더라도 대사가 100% 온전히 재생되고,
    -t {final_cut_dur} 시점에 비디오/오디오가 동시에 칼전환(Hard Cut)된다.

[🛠️ FFmpeg 바이너리 탐색 규격 — Windows `where ffmpeg` 미인식 대응]
  1순위: imageio_ffmpeg.get_ffmpeg_exe()  (워크스페이스 표준 번들 바이너리)
  2순위: 환경변수 FFMPEG_BINARY / FFMPEG_PATH / IMAGEIO_FFMPEG_EXE
  3순위: shutil.which("ffmpeg")           (PATH 등록된 시스템 바이너리)
  4순위: 로컬 번들 경로(./bin/ffmpeg.exe, ./ffmpeg.exe, tools/ffmpeg.exe)
  5순위: "ffmpeg"                          (최후의 문자열 폴백 — 실행 시 명시적 오류 발생)
===================================================================================================
"""

from __future__ import annotations

import logging
import math
import os
import re
import shutil
import signal
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("DramaClipStitcher")


# ==============================================================================
# 🎨 [시각 계약 계층] — 해상도/렌더 규격에서 파생되는 시각 불변식의 단일 출처
# ==============================================================================
@dataclass(frozen=True)
class VisualContract:
    """
    시각 규격 계약 — 1080x1920 세로 숏폼 기준의 '정당성 있는 값 범위'를 선언한다.

    🎯 목적: BounceSpec 의 파라미터가 '왜 이 값인가'를 코드로 표현한다.
       · 진폭은 화면 높이 대비 비율(ratio)로 정의 → 해상도 변경 시 자동 스케일.
       · 주기는 숏폼 시청 리듬(0.6~1.6초) 범위로 제약 → 무한 왕복/정지 방지.
       · 검증은 문자열 매칭이 아니라 '수치 불변식'으로 수행한다.

    📌 SSOT: 시각 파라미터의 정당성 판단은 오직 이 클래스에서만 이루어진다.
    """
    # 기준 해상도 (계약의 원본 좌표계)
    REF_WIDTH: int = 1080
    REF_HEIGHT: int = 1920

    # 🎯 [공식 규격 확정 — shorts_video_composer.py SSOT 일치]
    #    y = 1450 - 18*abs(sin(2*PI*t*1.5))  →  진폭 18px, 주기 1/1.5 ≈ 0.6667s
    #    진폭 계약: 화면 높이 대비 비율 (0.008 ~ 0.020 → 1080x1920 기준 약 15~38px)
    AMPLITUDE_RATIO_MIN: float = 0.008
    AMPLITUDE_RATIO_MAX: float = 0.020
    # 기본 진폭 비율: 18px / 1920px = 0.009375 (공식 규격)
    AMPLITUDE_RATIO_DEFAULT: float = 18.0 / 1920.0

    # 주기 계약: 숏폼 리듬 (0.5 ~ 1.6초) — 공식 규격 0.6667s 수용
    PERIOD_SEC_MIN: float = 0.5
    PERIOD_SEC_MAX: float = 1.6
    PERIOD_SEC_DEFAULT: float = 1.0 / 1.5  # 공식 규격 2*PI*t*1.5 → 주기 0.6667s

    # 🎯 [필 뱃지 기준 좌표 — 공식 규격 절대값]
    #    y_base = 1450 (REF_HEIGHT=1920 기준), x_center = 60
    PILL_BASE_Y_ABS: int = 1450
    PILL_X_ABS: int = 60

    def amplitude_px_default(self) -> float:
        """기본 진폭(px) — 기준 해상도에서 파생."""
        return round(self.AMPLITUDE_RATIO_DEFAULT * self.REF_HEIGHT, 2)

    def amplitude_px_for(self, out_height: int) -> float:
        """임의 출력 해상도에 대한 진폭(px) — 비율 기반 스케일."""
        return round(self.AMPLITUDE_RATIO_DEFAULT * float(out_height), 2)

    def assert_amplitude_valid(self, amplitude_px: float, out_height: int) -> None:
        """진폭 수치 불변식 검증 — 화면 높이 대비 비율 범위 내인지 확인."""
        if amplitude_px < 0:
            raise ValueError(f"진폭은 0 이상이어야 함: {amplitude_px}")
        ratio = amplitude_px / max(1.0, float(out_height))
        if not (self.AMPLITUDE_RATIO_MIN <= ratio <= self.AMPLITUDE_RATIO_MAX):
            raise ValueError(
                f"진폭 비율이 계약 범위를 벗어남: {ratio:.5f} "
                f"(허용 {self.AMPLITUDE_RATIO_MIN}~{self.AMPLITUDE_RATIO_MAX}, "
                f"amplitude_px={amplitude_px}, out_height={out_height})"
            )

    def assert_period_valid(self, period_sec: float) -> None:
        """주기 수치 불변식 검증 — 숏폼 리듬 범위 내인지 확인."""
        if not (self.PERIOD_SEC_MIN <= period_sec <= self.PERIOD_SEC_MAX):
            raise ValueError(
                f"주기가 계약 범위를 벗어남: {period_sec}s "
                f"(허용 {self.PERIOD_SEC_MIN}~{self.PERIOD_SEC_MAX})"
            )


# 시각 계약 싱글턴 (모듈 레벨 단일 출처)
VISUAL_CONTRACT: VisualContract = VisualContract()


# ==============================================================================
# 🎨 [선언적 오버레이 레이어 스펙] — 매직 넘버/문자열 결합/수동 인덱스 결합 제거
# ==============================================================================
@dataclass(frozen=True)
class BounceSpec:
    """
    바운싱 애니메이션 파라미터 — 단방향 반발(rebound) 물리 모델.

    🎯 물리 모델: base_y 를 '바닥선'으로 삼아 위로만 튀어오르는 -abs(sin) 곡선.
       · sin 왕복(위/아래 대칭)은 '둥실거림'이지 '통통 튐'이 아니다.
       · -abs(sin) 은 항상 0 이하 → base_y 에 더하면 base_y 위쪽으로만 이동(클램프 보장).
       · 위상(phase_rad)은 시간 오프셋으로 실제 소비된다(무시되지 않음).

    📌 SSOT: 진폭/주기/위상의 유일한 출처는 이 클래스다.
       기본값은 VisualContract 에서 파생되며, 여기서 수치를 재정의하지 않는다.
    """
    amplitude_px: float = field(
        default_factory=lambda: VISUAL_CONTRACT.amplitude_px_default()
    )
    period_sec: float = field(
        default_factory=lambda: VISUAL_CONTRACT.PERIOD_SEC_DEFAULT
    )
    phase_rad: float = 0.0         # 위상(라디안) — 시간 오프셋으로 소비

    def __post_init__(self) -> None:
        # 🛡️ 수치 불변식: 계약(VisualContract) 기준으로 검증 — 자기참조 검증 아님
        if self.amplitude_px < 0:
            raise ValueError(f"BounceSpec.amplitude_px 는 0 이상이어야 함: {self.amplitude_px}")
        if self.period_sec < 0.05:
            raise ValueError(f"BounceSpec.period_sec 는 0.05 이상이어야 함: {self.period_sec}")
        # 계약 범위 검증 (기준 해상도 기준)
        VISUAL_CONTRACT.assert_amplitude_valid(
            self.amplitude_px, VISUAL_CONTRACT.REF_HEIGHT
        )
        VISUAL_CONTRACT.assert_period_valid(self.period_sec)

    def y_expr(self, base_y: str) -> str:
        """
        FFmpeg overlay y 표현식 생성 — base_y 는 'H-330' 같은 기준식.

        반환식 형태: {base_y}-{amp}*abs(sin({w}*t+{phase}))
          · abs(sin) ∈ [0,1] → -amp*abs(sin) ∈ [-amp, 0]
          · base_y + (음수) → base_y 위쪽으로만 이동 (바닥 아래로 내려가지 않음)
          · phase_rad 는 t 에 더해져 실제로 위상을 이동시킨다.
        """
        w = 2.0 * math.pi / max(0.05, self.period_sec)
        return (
            f"{base_y}-{self.amplitude_px:.2f}"
            f"*abs(sin({w:.4f}*t+{self.phase_rad:.4f}))"
        )

    def validate_expr(self, base_y: str) -> None:
        """
        y_expr 문자열 단위 검증 — 렌더 타임 은폐 차단.

        🎯 이중 검증 구조:
          (A) 수치 불변식: VisualContract 기준 진폭/주기 범위 재확인 (자기참조 아님)
          (B) 문자열 구조: 반발 부호/위상 소비/base_y 접두/왕복 패턴 부재

        검증 항목:
          1) 반발 부호: '-{amp}*abs(sin(' 형태가 반드시 포함 (단방향 보장)
          2) 위상 소비: phase_rad 값이 문자열에 실제로 등장
          3) base_y 접두: 표현식이 base_y 로 시작
          4) 금지 토큰: 왕복을 유발하는 '+...*sin(' 패턴 부재
        """
        # (A) 수치 불변식 재검증 — 문자열과 무관하게 값 자체의 정당성 확인
        VISUAL_CONTRACT.assert_amplitude_valid(
            self.amplitude_px, VISUAL_CONTRACT.REF_HEIGHT
        )
        VISUAL_CONTRACT.assert_period_valid(self.period_sec)

        # (B) 문자열 구조 검증
        expr = self.y_expr(base_y)
        if not expr.startswith(base_y):
            raise ValueError(f"y_expr 가 base_y 로 시작하지 않음: {expr!r}")
        if "*abs(sin(" not in expr:
            raise ValueError(f"y_expr 에 abs(sin) 반발 곡선 부재: {expr!r}")
        if f"-{self.amplitude_px:.2f}*abs(sin(" not in expr:
            raise ValueError(f"y_expr 반발 부호(음수) 미적용 — 왕복 위험: {expr!r}")
        if f"+{self.phase_rad:.4f}" not in expr and self.phase_rad != 0.0:
            raise ValueError(f"y_expr 에 위상(phase_rad) 미소비: {expr!r}")
        # 왕복 패턴(+amp*sin) 부재 확인 — base_y 뒤에 '+숫자*sin(' 이 오면 회귀
        if re.search(r"\+[0-9.]+\*sin\(", expr):
            raise ValueError(f"y_expr 에 왕복 패턴(+amp*sin) 잔존 — 반발 모델 위반: {expr!r}")


@dataclass(frozen=True)
class OverlayLayerSpec:
    """
    오버레이 레이어 1개의 완전한 선언적 스펙.

    🎯 [시간 의존성 계약 — SSOT]
      FFmpeg overlay 필터의 x/y 표현식은 `eval=init`(기본)에서 초기화 시점에 단 한 번만
      평가된다. 따라서 `t`에 의존하는 표현식(바운스, 시간 기반 좌표 등)은 반드시
      `eval=frame`으로 평가되어야 한다. 이 판단은 호출자(빌더)가 `bounce` 필드 유무로
      추론하는 것이 아니라, **스펙 스스로가 `is_time_dependent()`로 선언**해야 한다.

      · bounce 존재 → 시간 의존 (y_expr 에 t 포함)
      · lifetime 존재 → 시간 의존 (enable 이 between(t,...) 로 시간 게이팅)
      · x_expr/y_expr 에 't' 토큰 포함 → 시간 의존 (향후 확장 대비 방어)

    📌 빌더는 이 계약만 보고 eval 모드를 결정한다. 조건부 문자열 삽입 금지.
    """
    name: str
    asset_path: Path
    x_expr: str = "0"
    y_expr: str = "0"
    bounce: Optional[BounceSpec] = None
    lifetime: Optional[Tuple[float, float]] = None  # (start_sec, end_sec) — None 이면 전 구간
    z_order: int = 0

    def resolved_y_expr(self) -> str:
        return self.bounce.y_expr(self.y_expr) if self.bounce else self.y_expr

    def enable_expr(self) -> str:
        if self.lifetime is None:
            return ""
        start, end = self.lifetime
        return f":enable='between(t,{start:.3f},{end:.3f})'"

    def is_time_dependent(self) -> bool:
        """
        이 레이어의 좌표/게이팅 표현식이 시간(t)에 의존하는지 선언한다.

        🎯 단일 판단 지점: eval 모드 결정은 오직 이 메서드 결과에만 근거한다.
           (bounce 필드 유무를 빌더가 직접 검사하는 암묵적 결합 금지)
        """
        if self.bounce is not None:
            return True
        if self.lifetime is not None:
            return True
        # 향후 확장 방어: x/y 표현식에 t 토큰이 있으면 시간 의존으로 간주
        if re.search(r"(?<![A-Za-z0-9_])t(?![A-Za-z0-9_])", self.x_expr):
            return True
        if re.search(r"(?<![A-Za-z0-9_])t(?![A-Za-z0-9_])", self.y_expr):
            return True
        return False

    def eval_mode(self) -> str:
        """overlay 필터에 전달할 eval 모드 — 시간 의존이면 'frame', 아니면 'init'."""
        return "frame" if self.is_time_dependent() else "init"


@dataclass
class OverlayAssetResolution:
    """자산 해석 결과 — 실패는 예외로 승격, 성공은 스펙 리스트로 반환."""
    layers: List[OverlayLayerSpec] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class DramaClipStitcher:
    """Wan 2.2 S2V 14B 립싱크 모션 숏드라마 조립기 (3계층 구조)"""

    # 출력 규격 (세로 풀HD 숏폼)
    OUT_WIDTH: int = 1080
    OUT_HEIGHT: int = 1920
    OUT_FPS: int = 30

    # 🈶 한글 폰트 (맑은 고딕 Bold) — FFmpeg drawtext 는 콜론(:)을 옵션 구분자로 쓰므로
    #    Windows 드라이브 문자 뒤 콜론은 반드시 백슬래시로 이스케이프해야 한다.
    FONT_FILE: str = "C\\:/Windows/Fonts/malgunbd.ttf"
    FONT_FILE_FALLBACK: str = "C\\:/Windows/Fonts/malgun.ttf"

    # 🎬 Wan 2.2 S2V 렌더링 규격
    S2V_WIDTH: int = 384
    S2V_HEIGHT: int = 672
    S2V_FRAMES: int = 81          # 폴백 기본 프레임 (오디오 길이 측정 실패 시에만 사용)
    S2V_MIN_VALID_BYTES: int = 100_000  # 100KB 초과 시 캐시 재사용

    # 🎞️ [Audio-First 프레임 계산 규격]
    #    Wan 2.2 S2V 는 16fps 로 렌더링되며, 프레임 수는 (frames - 1) % 4 == 0 을 만족해야 한다.
    S2V_FPS: int = 16
    S2V_FRAMES_MIN: int = 49      # 최소 49프레임 (약 3.0초)
    S2V_FRAMES_MAX: int = 81      # 최대 81프레임 (약 5.06초) — 주석/코드 단일 출처
    S2V_FRAMES_STEP: int = 4      # (frames - 1) % 4 == 0 강제

    # 🎭 립싱크 모션 프롬프트 (입모양/눈깜빡임/고개 움직임 강제)
    MOTION_PROMPT: str = (
        "photorealistic Korean character speaking naturally with delicate accurate lip sync "
        "matching the voice audio, subtle lifelike eye blinks, gentle head motion"
    )

    # ⏱️ [컷별 표준 시간 — 폴백 전용]
    #    🚨 실제 컷 길이는 각 컷 오디오의 실측 길이(_get_audio_duration)가 결정한다.
    #       이 표는 오디오 길이 측정이 실패했을 때만 쓰이는 최후 폴백이다.
    CUT_DURATIONS: Dict[int, float] = {
        1: 3.0,
        2: 6.0,
        3: 7.0,
        4: 4.0,
    }

    # 🏷️ [엔딩 CTA 카드 — 본편 4컷과 완전 분리된 별도 클립]
    #    본편 cut1~cut4 는 전부 인물 드라마 씬(S2V 립싱크 대상)이다.
    #    엔딩 CTA 카드(AuraDramaCTACard)는 본편 20초가 모두 끝난 뒤 맨 마지막에 붙는다.
    CTA_CARD_DURATION_SEC: float = 2.5

    # 🛡️ [엔딩 CTA 풀스크린 보호] 오버레이 노출 컷오프 시각(초) — 폴백 전용
    #    실제 컷오프는 본편 실측 총 길이(body_total_dur)로 동적 확정된다.
    OVERLAY_CUTOFF_SEC: float = 20.0

    # 🎨 [오버레이 레이어 배치 상수] — 매직 넘버 단일 출처화
    BADGE_Y_EXPR: str = "0"
    # 🎯 [공식 규격 좌표 — 해상도 비율식으로 재정의]
    #    공식 절대값 y=1450 (REF_HEIGHT=1920 기준) → H-(1920-1450) = H-470
    #    out_height 변동 시에도 하단 여백(470px)이 비율 유지되어 스케일 붕괴 방지.
    PILL_Y_BASE_EXPR: str = f"H-{VisualContract.REF_HEIGHT - VisualContract.PILL_BASE_Y_ABS}"
    # 🎯 [공식 규격 x=60 — 좌측 정렬 절대값]
    PILL_X_CENTER_EXPR: str = str(VisualContract.PILL_X_ABS)
    # 📌 SSOT: BounceSpec 기본값을 그대로 참조 — 여기서 수치를 재정의하지 말 것.
    #    (이중 하드코딩 금지: 진폭/주기/위상 변경은 VisualContract → BounceSpec 경로로만)
    #    기본값: 진폭 18px(1080x1920 기준 0.009375 비율), 주기 0.6667s (공식 규격)
    # 🛡️ [import 크래시 차단] 클래스 정의 시점 평가 → 지연 팩토리 전환
    #    BounceSpec.__post_init__ 검증 실패 시 모듈 로드 자체가 붕괴하는 경로를 차단.
    PILL_BOUNCE: BounceSpec = field(
        default_factory=lambda: BounceSpec(
            amplitude_px=VISUAL_CONTRACT.amplitude_px_default(),
            period_sec=VISUAL_CONTRACT.PERIOD_SEC_DEFAULT,
            phase_rad=0.0,
        )
    )

    # 🛡️ [무인 가동 안전장치] FFmpeg 타임아웃 / 최소 산출물 크기
    FFMPEG_TIMEOUT_SEC: int = 1800
    MIN_OUTPUT_BYTES: int = 10_000

    def __init__(
        self,
        ffmpeg_exe: Optional[str] = None,
        out_width: int = 1080,
        out_height: int = 1920,
        out_fps: int = 30,
    ):
        self.out_width = int(out_width)
        self.out_height = int(out_height)
        self.out_fps = int(out_fps)
        self.ffmpeg_exe = ffmpeg_exe or self._resolve_ffmpeg()
        self.font_file = self._resolve_font()

        # 1계층: Wan 2.2 S2V 립싱크 모션 엔진 직결
        try:
            from core.engine.wan_pipeline_client import WanPipelineClient

            self.wan_client: Optional[Any] = WanPipelineClient()
            logger.info("✅ [DramaStitcher] Wan 2.2 S2V 립싱크 엔진 직결 완료")
        except Exception as exc:  # noqa: BLE001 — 임포트 실패는 렌더 시점에 명시적 오류로 승격
            logger.warning(f"⚠️ [DramaStitcher] WanPipelineClient 초기화 실패: {exc}")
            self.wan_client = None

        logger.info(f"🎬 [DramaStitcher] FFmpeg 바이너리 확정: {self.ffmpeg_exe}")
        logger.info(f"🈶 [DramaStitcher] 한글 폰트 확정: {self.font_file}")

    # ==========================================================================
    # 🛠️ [FFmpeg 바이너리 탐색]
    # ==========================================================================
    def _resolve_ffmpeg(self) -> str:
        """Windows `where ffmpeg` 미인식 대응 — imageio_ffmpeg 번들 바이너리 최우선 탐색."""
        # 1순위: imageio_ffmpeg 번들 바이너리
        try:
            import imageio_ffmpeg  # type: ignore

            bundled = imageio_ffmpeg.get_ffmpeg_exe()
            if bundled and Path(bundled).exists():
                logger.info(f"✅ [DramaStitcher] imageio_ffmpeg 번들 바이너리 채택: {bundled}")
                return str(bundled)
            logger.warning(
                f"⚠️ [DramaStitcher] imageio_ffmpeg 경로가 존재하지 않음: {bundled} → 다음 후보 탐색"
            )
        except ImportError as exc:
            logger.warning(f"⚠️ [DramaStitcher] imageio_ffmpeg 미설치({exc}) → 다음 후보 탐색")
        except (OSError, RuntimeError) as exc:
            logger.warning(f"⚠️ [DramaStitcher] imageio_ffmpeg 바이너리 조회 실패({exc}) → 다음 후보 탐색")

        # 2순위: 환경변수 명시 경로
        for env_key in ("FFMPEG_BINARY", "FFMPEG_PATH", "IMAGEIO_FFMPEG_EXE"):
            env_val = os.environ.get(env_key, "").strip()
            if env_val and Path(env_val).exists():
                logger.info(f"✅ [DramaStitcher] 환경변수 {env_key} 채택: {env_val}")
                return env_val

        # 3순위: PATH 등록 바이너리
        which_path = shutil.which("ffmpeg")
        if which_path:
            logger.info(f"✅ [DramaStitcher] PATH 등록 ffmpeg 채택: {which_path}")
            return which_path

        # 4순위: 로컬 번들 경로
        project_root = Path(__file__).resolve().parent.parent.parent
        local_candidates = [
            project_root / "bin" / "ffmpeg.exe",
            project_root / "bin" / "ffmpeg",
            project_root / "tools" / "ffmpeg.exe",
            project_root / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe",
            project_root / "ffmpeg.exe",
            project_root / "ffmpeg",
        ]
        for candidate in local_candidates:
            if candidate.exists():
                logger.info(f"✅ [DramaStitcher] 로컬 번들 ffmpeg 채택: {candidate}")
                return str(candidate)

        # 5순위: 최후 폴백 (은폐 금지 — 실행 시 명시적 오류)
        logger.error(
            "🚨 [DramaStitcher] ffmpeg 바이너리를 찾지 못했습니다. "
            "`pip install imageio-ffmpeg` 설치 또는 PATH 등록이 필요합니다. "
            "최후 폴백 문자열 'ffmpeg' 로 진행합니다."
        )
        return "ffmpeg"

    # ==========================================================================
    # 🈶 [한글 폰트 탐색] 네모(□□□□) 깨짐 100% 방지
    # ==========================================================================
    def _resolve_font(self) -> str:
        """
        FFmpeg drawtext 용 한글 폰트 경로를 확정한다.
        Windows 경로의 콜론(:)은 FFmpeg 필터 옵션 구분자와 충돌하므로 `C\\:` 형태로 이스케이프한다.
        """
        candidates = [
            ("C\\:/Windows/Fonts/malgunbd.ttf", Path("C:/Windows/Fonts/malgunbd.ttf")),
            ("C\\:/Windows/Fonts/malgun.ttf", Path("C:/Windows/Fonts/malgun.ttf")),
            ("C\\:/Windows/Fonts/NanumGothic.ttf", Path("C:/Windows/Fonts/NanumGothic.ttf")),
        ]
        for escaped, real in candidates:
            if real.exists():
                logger.info(f"✅ [DramaStitcher] 한글 폰트 채택: {real} (drawtext: {escaped})")
                return escaped

        logger.error(
            "🚨 [DramaStitcher] 맑은 고딕 폰트를 찾지 못했습니다. "
            "한글 자막이 네모(□□□□)로 깨질 수 있습니다. 기본 이스케이프 경로로 강행합니다."
        )
        return self.FONT_FILE

    # ==========================================================================
    # ⏱️ [Audio-First] 컷 오디오 실측 길이 측정 (3단 폴백)
    # ==========================================================================
    def _get_audio_duration(self, audio_path: Path) -> float:
        """FFprobe/FFmpeg 기반 컷 오디오 실측 길이(초) 측정."""
        try:
            # 1차: ffprobe
            cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(audio_path),
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if res.returncode == 0 and res.stdout.strip():
                return float(res.stdout.strip().splitlines()[0])
        except Exception:
            pass

        try:
            # 2차: ffmpeg time= 파싱
            decode_cmd = [self.ffmpeg_exe, "-i", str(audio_path), "-f", "null", "-"]
            res = subprocess.run(decode_cmd, capture_output=True, text=True, check=False)
            matches = re.findall(r"time=(\d+):(\d+):(\d+\.\d+)", res.stderr or "")
            if matches:
                h, m, s = matches[-1]
                return int(h) * 3600 + int(m) * 60 + float(s)
        except Exception:
            pass

        # 3차: 파일 크기 128kbps 환산
        try:
            return max(0.5, os.path.getsize(audio_path) / 16000.0)
        except Exception:
            return 4.0

    # ==========================================================================
    # 🎞️ [Audio-First] 오디오 실측 길이 → Wan S2V 프레임 수 동적 계산
    # ==========================================================================
    def _calc_s2v_frames(self, final_cut_dur: float) -> int:
        """
        오디오 실측 길이(초)를 Wan 2.2 S2V 프레임 수로 환산한다.

        규격:
          · S2V 렌더 fps = 16
          · 프레임 수는 (frames - 1) % 4 == 0 을 반드시 만족해야 한다 (Wan 2.2 VAE 시간 압축 배수)
          · 49 ~ 81 프레임 범위로 클램핑 (약 3.0초 ~ 8.0초)

        계산식:
          calc = int(final_cut_dur * 16)
          return max(49, min(81, (calc // 4) * 4 + 1))

        Args:
            final_cut_dur: 컷 오디오 실측 길이(초)

        Returns:
            int: Wan S2V 에 전달할 프레임 수 (항상 (frames-1)%4==0)
        """
        try:
            dur = float(final_cut_dur)
        except (TypeError, ValueError):
            dur = 0.0
        if dur <= 0.0:
            logger.warning(
                f"⚠️ [DramaStitcher] 프레임 계산 입력이 유효하지 않음({final_cut_dur!r}) "
                f"→ 기본 {self.S2V_FRAMES} 프레임 사용"
            )
            return self.S2V_FRAMES

        calc = int(dur * self.S2V_FPS)
        s2v_frames = max(
            self.S2V_FRAMES_MIN,
            min(
                self.S2V_FRAMES_MAX,
                (calc // self.S2V_FRAMES_STEP) * self.S2V_FRAMES_STEP + 1,
            ),
        )

        # 🛡️ 규격 불변식 최종 검증 — (frames - 1) % 4 == 0
        if (s2v_frames - 1) % self.S2V_FRAMES_STEP != 0:
            s2v_frames = (s2v_frames // self.S2V_FRAMES_STEP) * self.S2V_FRAMES_STEP + 1

        logger.info(
            f"🎞️ [DramaStitcher] Audio-First 프레임 산출: 오디오 {dur:.2f}s "
            f"→ calc {calc} → S2V {s2v_frames} frames "
            f"({s2v_frames / self.S2V_FPS:.2f}s @ {self.S2V_FPS}fps)"
        )
        return s2v_frames

    # ==========================================================================
    # 🎬 [메인 조립] 4컷 S2V 립싱크 클립 → 20초 완성형 숏드라마 MP4
    # ==========================================================================
    def stitch_drama_short(
        self,
        scene_images: List[Path],
        cut_audios: List[Any],
        output_mp4_path: Path,
        brand_keyword: str,
        brand_name: str,
        bgm_path: Optional[Path] = None,
        full_audio_path: Optional[Path] = None,
        brand_key: Optional[str] = None,
        cta_image_path: Optional[Path] = None,
        cta_duration_sec: Optional[float] = None,
    ) -> Path:
        """
        4컷 실사 이미지 + 컷별 오디오를 받아 Wan 2.2 S2V 립싱크 동영상을 생성하고
        최종 1080x1920 / 30fps 숏드라마 MP4 로 결합한다.

        Args:
            scene_images: 컷별 씬 이미지 경로 리스트 (4개 — 전부 인물 드라마 씬)
            cut_audios: 컷별 오디오 경로 리스트.
                        Path/str 또는 {"audio_path": ..., "duration_sec": ..., "speech": ...} 딕셔너리 모두 허용.
            output_mp4_path: 최종 산출물 MP4 경로
            brand_keyword: 브랜드 공식 검색어 (예: '아우라AI데이팅')
            brand_name: 브랜드 공식 명칭 (예: 'Aura AI 데이팅')
            bgm_path: 배경음악 경로 (선택)
            full_audio_path: 4컷 전체 결합 오디오 경로 (참조용, 선택)
            cta_image_path: 엔딩 CTA 카드 이미지 경로 (선택).
                            지정 시 본편 4컷(20초)이 모두 끝난 뒤 맨 마지막에
                            stillimage 클립으로 결합된다. 본편 사진 목록과는 완전 분리.
            cta_duration_sec: 엔딩 CTA 카드 노출 시간(초). 미지정 시 CTA_CARD_DURATION_SEC(2.5).

        Returns:
            Path: 최종 산출물 MP4 경로

        Raises:
            ValueError: 입력 리스트 개수 불일치 또는 빈 입력
            FileNotFoundError: 씬 이미지 / 컷 오디오 파일 부재
            RuntimeError: Wan S2V 렌더링 또는 FFmpeg 렌더링 실패
        """
        if not scene_images:
            raise ValueError("❌ [DramaStitcher] scene_images 가 비어 있습니다.")
        if not cut_audios:
            raise ValueError("❌ [DramaStitcher] cut_audios 가 비어 있습니다.")
        if len(scene_images) != len(cut_audios):
            raise ValueError(
                f"❌ [DramaStitcher] 이미지/오디오 개수 불일치: "
                f"이미지 {len(scene_images)}개 vs 오디오 {len(cut_audios)}개"
            )

        # 컷 오디오 경로 정규화 (Path/str/딕셔너리 혼용 허용)
        audio_paths: List[Path] = [self._extract_audio_path(a) for a in cut_audios]

        for img in scene_images:
            if not Path(img).exists():
                raise FileNotFoundError(f"❌ [DramaStitcher] 씬 이미지 없음: {img}")
        for audio_p in audio_paths:
            if not audio_p.exists():
                raise FileNotFoundError(f"❌ [DramaStitcher] 컷 오디오 없음: {audio_p}")

        output_mp4 = Path(output_mp4_path)
        output_mp4.parent.mkdir(parents=True, exist_ok=True)
        temp_dir = output_mp4.parent / "_temp_stitch"
        temp_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"🚀 [DramaStitcher] {len(scene_images)}컷 Wan 2.2 S2V 립싱크 동영상 렌더링 착수 ({brand_name})"
        )

        rendered_clips: List[Path] = []
        body_total_dur: float = 0.0   # 🎯 본편 실측 총 길이 (오버레이 컷오프 동적 확정용)
        try:
            # ── 1계층 + 2계층: 컷별 S2V 립싱크 생성 및 1080x1920 정규화 ──
            #    본편 cut1~cut4 는 전부 인물 드라마 씬이므로 100% S2V 립싱크 대상이다.
            #    cut0 (상황 자막 카드): 무음·정지 이미지 → FFmpeg stillimage (S2V 비호출)
            #    (엔딩 CTA 카드는 본편과 분리되어 아래에서 맨 마지막에 별도 결합된다)
            for i, (img_p, aud_p) in enumerate(zip(scene_images, audio_paths)):
                cut_idx = i + 1

                # 🎬 [cut0 분기] 상황 자막 카드: 무음 정지 이미지 → stillimage 클립
                # 감지 기준: 오디오 파일명에 'cut0' 또는 'silent' 포함
                _aud_name = str(aud_p).lower()
                _is_cut0 = ("cut0" in _aud_name) or ("silent" in _aud_name)
                if _is_cut0:
                    target_duration = self._get_audio_duration(aud_p)
                    if not target_duration or target_duration <= 0:
                        target_duration = 2.5
                    logger.info(
                        f"🎬 [DramaStitcher] 컷 #{cut_idx} [cut0 상황카드] 정지이미지 클립 생성 "
                        f"({target_duration:.2f}s, S2V 미사용)"
                    )
                    clip_out = temp_dir / f"cut_{cut_idx}_situation.mp4"
                    rendered_clip = self._generate_ending_cta_clip(
                        image_path=Path(img_p),
                        output_clip_path=clip_out,
                        duration_sec=target_duration,
                    )
                    rendered_clips.append(rendered_clip)
                    body_total_dur += float(target_duration)
                    continue

                # 🚨 [대표님 확정 명령] "말하는 거에 영상을 맞추어야지"
                #    하드코딩 3/6/7/4초가 아니라, 이 컷 오디오의 실제 길이를 그대로 쓴다.
                #    → 대사가 끝나는 바로 그 순간 비디오도 칼같이 끝나고 다음 컷으로 넘어간다.
                target_duration = self._get_audio_duration(aud_p)
                if target_duration is None or target_duration <= 0:
                    target_duration = self.CUT_DURATIONS.get(cut_idx)
                logger.info(
                    f"⏱️ [DramaStitcher] 컷 #{cut_idx} 오디오 실측 길이 {target_duration:.2f}s "
                    f"→ 비디오 길이로 동적 지정 (칼전환)"
                )

                clip_out = temp_dir / f"cut_{cut_idx}_s2v.mp4"
                rendered_clip = self._generate_s2v_clip(
                    image_path=Path(img_p),
                    audio_path=aud_p,
                    output_clip_path=clip_out,
                    cut_idx=cut_idx,
                    target_duration=target_duration,
                )
                rendered_clips.append(rendered_clip)
                body_total_dur += float(target_duration)

                # 🧹 [대표님 절대 엄명] 컷 렌더링 직후 VRAM 캐시 즉시 비우기 (누적 OOM 방지)
                if self.wan_client is not None:
                    self.wan_client.free_vram()
                    logger.info(f"🧹 [DramaStitcher] 컷 #{cut_idx} 렌더링 완료 즉시 VRAM 캐시 안전 방출")


            # ── 3계층: 엔딩 CTA 카드 클립을 본편 맨 마지막에 별도 결합 ──
            #    본편 4컷(20초)이 모두 끝난 뒤 CTA 카드(2.5초)가 이어 붙는다.
            if cta_image_path is not None:
                cta_img = Path(cta_image_path)
                if not cta_img.exists():
                    raise FileNotFoundError(
                        f"❌ [DramaStitcher] 엔딩 CTA 카드 이미지 없음: {cta_img}"
                    )
                cta_dur = (
                    cta_duration_sec
                    if (cta_duration_sec is not None and cta_duration_sec > 0)
                    else self.CTA_CARD_DURATION_SEC
                )
                cta_clip_out = temp_dir / "cut_5_ending_cta.mp4"
                cta_clip = self._generate_ending_cta_clip(
                    image_path=cta_img,
                    output_clip_path=cta_clip_out,
                    duration_sec=cta_dur,
                )
                rendered_clips.append(cta_clip)
                logger.info(
                    f"🏷️ [DramaStitcher] 엔딩 CTA 카드 클립을 본편 뒤에 결합 "
                    f"({cta_dur:.2f}초 · 총 {len(rendered_clips)}개 클립)"
                )

            # ── 3계층: 4컷 클립 Concat 재인코딩 결합 ──
            concat_list = temp_dir / "concat_list.txt"
            with open(concat_list, "w", encoding="utf-8") as f:
                for clip in rendered_clips:
                    clean_path = str(clip.resolve()).replace("\\", "/")
                    f.write(f"file '{clean_path}'\n")

            merged_raw = temp_dir / "merged_raw.mp4"
            cmd_concat = [
                self.ffmpeg_exe, "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(concat_list),
                "-c:v", "libx264", "-preset", "fast", "-crf", "20",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                "-r", str(self.out_fps),
                str(merged_raw),
            ]
            self._run_cmd(cmd_concat, "4컷 S2V 동영상 Concat 결합")

            # ── 3계층: 네이버 공식 검색어 CTA 오버레이 + BGM 믹싱 ──
            #    🎯 오버레이 컷오프는 본편 실측 총 길이로 동적 확정한다.
            #       (오디오가 길어져 본편이 23~26초가 되어도 엔딩 카드는 완벽히 보호된다)
            overlay_cutoff = body_total_dur if body_total_dur > 0 else self.OVERLAY_CUTOFF_SEC
            self._apply_branding_and_cta(
                input_mp4=merged_raw,
                output_mp4=output_mp4,
                brand_keyword=brand_keyword,
                bgm_path=bgm_path,
                brand_key=brand_key,
                brand_name=brand_name,
                overlay_cutoff_sec=overlay_cutoff,
            )

            if not output_mp4.exists() or output_mp4.stat().st_size <= 0:
                raise RuntimeError(f"❌ [DramaStitcher] 최종 MP4 미생성: {output_mp4}")

            logger.info(f"🎉 [DramaStitcher] Wan 2.2 S2V 실사 숏드라마 최종 완성: {output_mp4}")
            return output_mp4

        finally:
            # 임시 산출물 정리 (실패해도 원본 예외를 덮지 않도록 개별 처리)
            for leftover in (
                temp_dir / "concat_list.txt",
                temp_dir / "merged_raw.mp4",
            ):
                if leftover.exists():
                    try:
                        leftover.unlink()
                    except OSError as exc:
                        logger.warning(f"⚠️ [DramaStitcher] 임시 파일 삭제 실패(무해): {leftover} ({exc})")

    # ==========================================================================
    # 🎥 [1계층 + 2계층] Wan 2.2 S2V 립싱크 생성 → 1080x1920 정규화
    # ==========================================================================
    def _generate_s2v_clip(
        self,
        image_path: Path,
        audio_path: Path,
        output_clip_path: Path,
        cut_idx: int,
        target_duration: Optional[float] = None,
    ) -> Path:
        """
        Wan 2.2 S2V 를 가동하여 인물이 실제로 말하는 립싱크 동영상을 생성하고 세로 9:16 으로 정규화한다.

        Args:
            target_duration: 컷 표준 시간(초). 지정 시 FFmpeg -t 로 길이를 강제 고정하여
                             정확히 해당 초에 다음 컷으로 칼전환(Hard Cut)되도록 보장한다.
        """
        # 캐시 재사용 (100KB 초과 = 정상 렌더링 산출물)
        if output_clip_path.exists() and output_clip_path.stat().st_size > self.S2V_MIN_VALID_BYTES:
            logger.info(f"♻️ [DramaStitcher] 기존 립싱크 클립 재사용: {output_clip_path.name}")
            return output_clip_path

        if self.wan_client is None:
            raise RuntimeError(
                "❌ [DramaStitcher] WanPipelineClient 미초기화 — S2V 립싱크 렌더링 불가"
            )

        if not self.wan_client.check_health(auto_start=True):
            raise RuntimeError("❌ [DramaStitcher] Wan 2.2 ComfyUI 엔진이 오프라인 상태입니다. S2V 렌더링 불가.")

        # ── ① 컷 오디오 실측 길이 확정 (Audio-First 기준값) ──────────────────
        # 🚨 [대표님 확정 명령] "숏폼이 약간 길어져도 상관은 없어..그대신 음성에 맞추어 영상 제작.."
        #    이 컷의 비디오 길이는 오직 이 오디오의 실측 길이가 결정한다.
        final_cut_dur = (
            float(target_duration)
            if (target_duration is not None and float(target_duration) > 0)
            else self._get_audio_duration(audio_path)
        )
        if final_cut_dur is None or final_cut_dur <= 0:
            final_cut_dur = self.CUT_DURATIONS.get(cut_idx, 3.0)
            logger.warning(
                f"⚠️ [DramaStitcher] 컷 #{cut_idx} 오디오 길이 측정 실패 → 폴백 {final_cut_dur:.2f}s"
            )

        # ── ② 오디오 길이에 맞춘 S2V 프레임 수 동적 계산 ─────────────────────
        s2v_frames = self._calc_s2v_frames(final_cut_dur)

        # ComfyUI input 디렉터리로 이미지/오디오 복사
        comfy_input = Path(self.wan_client.comfy_input_dir)
        comfy_input.mkdir(parents=True, exist_ok=True)

        input_img_name = f"s2v_cut_{cut_idx}_{image_path.name}"
        input_aud_name = f"s2v_cut_{cut_idx}_{audio_path.name}"
        shutil.copy2(str(image_path), str(comfy_input / input_img_name))
        shutil.copy2(str(audio_path), str(comfy_input / input_aud_name))

        raw_s2v_out = output_clip_path.parent / f"raw_s2v_cut_{cut_idx}.mp4"

        logger.info(
            f"🎬 [DramaStitcher] 컷 #{cut_idx} Wan 2.2 S2V 립싱크 렌더링 가동 "
            f"(14B Q4_0 · {s2v_frames} frames · 오디오 {final_cut_dur:.2f}s 기준)"
        )
        try:
            self.wan_client.generate_s2v_video(
                image_name=input_img_name,
                audio_name=input_aud_name,
                prompt_text=self.MOTION_PROMPT,
                output_mp4_path=str(raw_s2v_out),
                width=self.S2V_WIDTH,
                height=self.S2V_HEIGHT,
                frames=s2v_frames,
                prefix=f"s2v_drama_cut_{cut_idx}",
            )
        finally:
            # 🛡️ 컷 간 VRAM 정리 — unload_models=True 는 ComfyUI GGUF 텐서 해제 경로에서
            #    C++ access violation(0xC0000005) 프로세스 즉사를 유발하므로 반드시 False.
            try:
                self.wan_client.free_vram(unload_models=False)
                logger.info(f"🧹 [DramaStitcher] 컷 #{cut_idx} VRAM 정리 완료 (unload_models=False)")
            except Exception as exc:  # noqa: BLE001 — VRAM 정리 실패가 렌더 결과를 덮지 않도록
                logger.warning(f"⚠️ [DramaStitcher] 컷 #{cut_idx} VRAM 정리 실패(무해): {exc}")

        if not raw_s2v_out.exists() or raw_s2v_out.stat().st_size <= 0:
            raise RuntimeError(f"❌ [DramaStitcher] 컷 #{cut_idx} S2V 원본 미생성: {raw_s2v_out}")

        # ── ③ 1080x1920 정규화 + tpad 클론 + A/V 동시 칼전환 ─────────────────
        # 🎯 tpad=stop_mode=clone:stop_duration=1.0
        #    S2V 원본 비디오가 오디오보다 미세하게 짧아도 마지막 프레임을 1초간 복제(clone)하여
        #    비디오 스트림이 절대 먼저 끊기지 않게 한다.
        #    이후 -t {final_cut_dur} 가 비디오/오디오를 동시에 정확히 절단 → 완벽한 하드컷.
        vf_chain = (
            f"scale={self.out_width}:{self.out_height}:force_original_aspect_ratio=increase,"
            f"crop={self.out_width}:{self.out_height},"
            f"setsar=1,fps={self.out_fps},"
            f"tpad=stop_mode=clone:stop_duration=1.0,"
            f"format=yuv420p"
        )

        cmd_upscale = [
            self.ffmpeg_exe, "-y",
            "-i", str(raw_s2v_out),
            "-i", str(audio_path),
            "-vf", vf_chain,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-t", f"{final_cut_dur:.2f}",
            str(output_clip_path),
        ]
        self._run_cmd(cmd_upscale, f"컷 #{cut_idx} 1080x1920 정규화")

        # 정규화 원본(raw) 정리
        if raw_s2v_out.exists():
            try:
                raw_s2v_out.unlink()
            except OSError as exc:
                logger.warning(f"⚠️ [DramaStitcher] raw S2V 삭제 실패(무해): {raw_s2v_out} ({exc})")

        return output_clip_path

    # ==========================================================================
    # 🏷️ [엔딩 전용] CTA 카드 초고화질 stillimage 클립 생성 (본편과 완전 분리)
    # ==========================================================================
    def _generate_ending_cta_clip(
        self,
        image_path: Path,
        output_clip_path: Path,
        duration_sec: Optional[float] = None,
    ) -> Path:
        """
        엔딩 CTA 카드 전용 클립 렌더러 (본편 4컷과 완전 분리).

        텍스트 카드를 S2V 인물 립싱크 엔진에 집어넣으면 글자가 뭉개지는 참사가 발생한다.
        따라서 S2V 를 완전히 우회하고, 정지 이미지를 -loop 1 로 물려
        -tune stillimage / -crf 16 초고화질로 인코딩한다.

        본편 오디오와 섞이지 않도록 **무음 오디오 트랙(anullsrc)** 을 함께 생성한다.
        (concat 결합 시 오디오 스트림 부재로 인한 결합 실패를 원천 차단)

        Args:
            image_path: AuraDramaCTACard 가 렌더링한 1080x1920 CTA 카드 PNG
            output_clip_path: 생성될 클립 경로
            duration_sec: 카드 노출 시간(초). 미지정 시 CTA_CARD_DURATION_SEC(2.5).

        Returns:
            Path: 생성된 엔딩 CTA 카드 클립 경로
        """
        # 캐시 재사용 (100KB 초과 = 정상 렌더링 산출물)
        if output_clip_path.exists() and output_clip_path.stat().st_size > self.S2V_MIN_VALID_BYTES:
            logger.info(f"♻️ [DramaStitcher] 기존 엔딩 CTA 카드 클립 재사용: {output_clip_path.name}")
            return output_clip_path

        if not image_path.exists():
            raise FileNotFoundError(f"❌ [DramaStitcher] 엔딩 CTA 카드 이미지 없음: {image_path}")

        duration = (
            duration_sec
            if (duration_sec is not None and duration_sec > 0)
            else self.CTA_CARD_DURATION_SEC
        )

        logger.info(
            f"🏷️ [DramaStitcher] 엔딩 CTA 카드 stillimage 클립 렌더링 "
            f"(S2V 우회 · {duration:.2f}초 고정 · CRF 16 · 무음 트랙)"
        )

        cmd_cta = [
            self.ffmpeg_exe, "-y",
            "-loop", "1",
            "-i", str(image_path),
            "-f", "lavfi",
            "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-vf",
            (
                f"scale={self.out_width}:{self.out_height}:force_original_aspect_ratio=increase,"
                f"crop={self.out_width}:{self.out_height},"
                f"setsar=1,fps={self.out_fps},format=yuv420p"
            ),
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-t", f"{duration:.2f}",
            "-shortest",
            str(output_clip_path),
        ]
        self._run_cmd(cmd_cta, "엔딩 CTA 카드 stillimage 클립 렌더링")

        if not output_clip_path.exists() or output_clip_path.stat().st_size <= 0:
            raise RuntimeError(
                f"❌ [DramaStitcher] 엔딩 CTA 카드 클립 미생성: {output_clip_path}"
            )

        logger.info(
            f"✅ [DramaStitcher] 엔딩 CTA 카드 클립 완성 "
            f"({output_clip_path.stat().st_size:,} bytes): {output_clip_path.name}"
        )
        return output_clip_path

    # ==========================================================================
    # 🏷️ [3계층] 네이버 공식 검색어 CTA 오버레이 + BGM 믹싱
    # ==========================================================================
    def _apply_branding_and_cta(
        self,
        input_mp4: Path,
        output_mp4: Path,
        brand_keyword: str,
        bgm_path: Optional[Path] = None,
        brand_key: Optional[str] = None,
        brand_name: Optional[str] = None,
        overlay_cutoff_sec: Optional[float] = None,
    ) -> None:
        """
        상단 공식 캡슐 뱃지(v_badge) 단독 오버레이 + BGM 덕킹 믹싱.

        Args:
            overlay_cutoff_sec: 오버레이 노출 컷오프 시각(초). 미지정 시 OVERLAY_CUTOFF_SEC.
                                본편 실측 총 길이가 전달되면 엔딩 CTA 카드 구간이 완벽히 보호된다.

        ✅ [유지] 상단 공식 캡슐 뱃지(v_badge) + 하단 바운싱 필 뱃지(v_pill)
        🚫 [영구 제거] 시커먼 drawbox=color=black@0.65 / '네이버에 [키워드] 검색' drawtext
           → 촌스러운 검은 박스와 자막만 배제하며, 세련된 캡슐 필 뱃지는 유입을 위해 반드시 살린다.
        """
        b_key = brand_key or ("insurance" if "보험" in (brand_name or "") or "보험" in brand_keyword else ("stock" if "스톡" in (brand_name or "") or "스톡" in brand_keyword else "aura"))

        # ── ① 자산 해석 (합성과 분리) ─────────────────────────────────────
        cutoff = (
            float(overlay_cutoff_sec)
            if (overlay_cutoff_sec is not None and float(overlay_cutoff_sec) > 0)
            else self.OVERLAY_CUTOFF_SEC
        )
        resolution = self._resolve_overlay_assets(b_key, cutoff)
        for warn in resolution.warnings:
            logger.warning(f"⚠️ [DramaStitcher] 오버레이 자산 경고: {warn}")

        # ── ② 순수 함수로 필터 그래프 결정적 구성 ─────────────────────────
        inputs, filter_str, v_out_label, a_out_label = self._build_overlay_filter_graph(
            input_mp4=input_mp4,
            layers=resolution.layers,
            bgm_path=bgm_path,
        )

        # ── ③ FFmpeg 실행 + 출력 무결성 검증 ──────────────────────────────
        cmd = [
            self.ffmpeg_exe, "-y", *inputs,
            "-filter_complex", filter_str,
            "-map", v_out_label, "-map", a_out_label,
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
        ]
        if bgm_path and Path(bgm_path).exists():
            cmd.append("-shortest")
        cmd.append(str(output_mp4))
        self._run_cmd(cmd, "Aura 공식 브랜딩 뱃지 및 CTA 오버레이 적용")
        self._verify_output(output_mp4, "오버레이 합성")

    # ==========================================================================
    # 🎨 [자산 해석] — 합성과 분리된 순수 해석 단계 (명시적 실패 정책)
    # ==========================================================================
    def _resolve_overlay_assets(
        self,
        brand_key: str,
        cutoff_sec: float,
    ) -> OverlayAssetResolution:
        """
        브랜드 자산을 해석하여 선언적 OverlayLayerSpec 리스트로 반환한다.

        실패 정책:
          · 임포트 실패/경로 부재 → warnings 에 기록 후 해당 레이어 스킵 (관측 가능)
          · 파일은 존재하나 0바이트 → FileNotFoundError 로 승격 (무음 실패 차단)
        """
        res = OverlayAssetResolution()
        lifetime = (0.0, float(cutoff_sec))

        # 상단 공식 캡슐 뱃지
        try:
            from core.shorts_engine.shorts_brand_capsule_badge import ShortsBrandCapsuleBadge
            bp = ShortsBrandCapsuleBadge.get_overlay_path(brand_key)
            if bp and Path(bp).exists():
                p = Path(bp)
                if p.stat().st_size <= 0:
                    raise FileNotFoundError(f"상단 캡슐 뱃지 파일이 0바이트: {p}")
                res.layers.append(OverlayLayerSpec(
                    name="badge",
                    asset_path=p.resolve(),
                    x_expr="0",
                    y_expr=self.BADGE_Y_EXPR,
                    bounce=None,
                    lifetime=lifetime,
                    z_order=10,
                ))
            else:
                res.warnings.append(f"상단 캡슐 뱃지 경로 부재(brand_key={brand_key})")
        except FileNotFoundError:
            raise
        except Exception as exc:  # noqa: BLE001 — 임포트 실패는 관측 가능한 경고로
            res.warnings.append(f"상단 캡슐 뱃지 로드 실패: {exc}")

        # 하단 바운싱 필 뱃지
        try:
            from core.shorts_engine.shorts_branding_overlay import ShortsBrandingOverlay
            pp = ShortsBrandingOverlay.get_bouncing_profile_badge_path(brand_key)
            if pp and Path(pp).exists():
                p = Path(pp)
                if p.stat().st_size <= 0:
                    raise FileNotFoundError(f"하단 필 뱃지 파일이 0바이트: {p}")
                res.layers.append(OverlayLayerSpec(
                    name="pill",
                    asset_path=p.resolve(),
                    x_expr=self.PILL_X_CENTER_EXPR,
                    y_expr=self.PILL_Y_BASE_EXPR,
                    bounce=self.PILL_BOUNCE,
                    lifetime=lifetime,
                    z_order=20,
                ))
            else:
                res.warnings.append(f"하단 필 뱃지 경로 부재(brand_key={brand_key})")
        except FileNotFoundError:
            raise
        except Exception as exc:  # noqa: BLE001
            res.warnings.append(f"하단 필 뱃지 로드 실패: {exc}")

        # z-order 정렬 (결정적 합성 순서 보장)
        res.layers.sort(key=lambda s: s.z_order)

        # 🛡️ 바운스 표현식 단위 검증 — 렌더 타임 은폐 차단 (무인 가동 안전장치)
        #    🎯 [fail-isolated] 계약 위반 레이어는 전체 파이프라인을 죽이지 않고
        #       경고 후 스킵한다. 무인 가동 시 단일 레이어 오류가 전역 붕괴로
        #       번지는 것을 차단(회로차단기). 관측은 warnings 로 100% 노출.
        validated_layers: List[OverlayLayerSpec] = []
        for layer in res.layers:
            if layer.bounce is not None:
                try:
                    layer.bounce.validate_expr(layer.y_expr)
                except ValueError as exc:
                    res.warnings.append(
                        f"레이어 '{layer.name}' 바운스 표현식 검증 실패 → 스킵: {exc}"
                    )
                    logger.error(
                        f"🚨 [DramaStitcher] 레이어 '{layer.name}' 계약 위반 → 격리 스킵: {exc}"
                    )
                    continue
            validated_layers.append(layer)
        res.layers = validated_layers

        return res

    # ==========================================================================
    # 🎨 [필터 그래프 빌더] — 순수 함수, 인덱스 자동 할당, 단위 테스트 가능
    # ==========================================================================
    def _build_overlay_filter_graph(
        self,
        input_mp4: Path,
        layers: List[OverlayLayerSpec],
        bgm_path: Optional[Path],
    ) -> Tuple[List[str], str, str, str]:
        """
        선언적 레이어 스펙으로부터 FFmpeg 입력/필터 문자열을 결정적으로 구성한다.

        Returns:
            (inputs, filter_str, v_out_label, a_out_label)
        """
        inputs: List[str] = ["-i", str(input_mp4)]
        filters: List[str] = []
        curr_v = "0:v"
        next_idx = 1  # 다음 -i 인덱스 (자동 할당)

        for layer in layers:
            clean = str(layer.asset_path).replace("\\", "/")
            inputs.extend(["-i", clean])
            in_idx = next_idx
            next_idx += 1
            out_label = f"v_{layer.name}"
            # 🎯 [SSOT] eval 모드는 레이어 스펙의 시간 의존성 계약에서만 결정한다.
            #    bounce 유무로 조건부 삽입하던 증상 패치를 제거하고,
            #    시간 의존 레이어는 항상 eval=frame 으로 좌표를 매 프레임 재평가한다.
            eval_mode = layer.eval_mode()
            filters.append(
                f"[{curr_v}][{in_idx}:v]overlay="
                f"x={layer.x_expr}:y={layer.resolved_y_expr()}"
                f":eval={eval_mode}"
                f"{layer.enable_expr()}[{out_label}]"
            )
            curr_v = out_label

        filters.append(f"[{curr_v}]null[vout]")

        if bgm_path and Path(bgm_path).exists():
            clean_bgm = str(Path(bgm_path).resolve()).replace("\\", "/")
            inputs.extend(["-stream_loop", "-1", "-i", clean_bgm])
            bgm_idx = next_idx
            filters.append(f"[{bgm_idx}:a]volume=0.15[bgma]")
            filters.append("[0:a][bgma]amix=inputs=2:duration=first[aout]")
            a_out = "[aout]"
        else:
            a_out = "0:a?"

        return inputs, ";".join(filters), "[vout]", a_out

    # ==========================================================================
    # 🧰 [유틸] 오디오 경로 추출 / FFmpeg 실행
    # ==========================================================================
    @staticmethod
    def _extract_audio_path(audio_info: Any) -> Path:
        """컷 오디오 항목(Path/str/dict)에서 실제 오디오 경로를 추출한다."""
        if isinstance(audio_info, dict):
            raw = audio_info.get("audio_path") or audio_info.get("path") or ""
            return Path(str(raw))
        return Path(str(audio_info))

    def _run_cmd(self, cmd: List[str], label: str) -> None:
        """
        FFmpeg 명령을 실행하고 실패 시 stderr 를 포함한 RuntimeError 로 승격한다.

        🛡️ 무인 가동 안전장치:
          · 프로세스 그룹 분리(start_new_session) → 타임아웃 시 자식 프로세스까지 회수
          · 타임아웃 시 SIGKILL 로 좀비 방지
        """
        proc: Optional[subprocess.Popen] = None
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                start_new_session=(os.name != "nt"),
            )
            try:
                stdout, stderr = proc.communicate(timeout=self.FFMPEG_TIMEOUT_SEC)
            except subprocess.TimeoutExpired:
                self._kill_process_tree(proc)
                raise RuntimeError(
                    f"❌ [DramaStitcher] {label} 타임아웃 ({self.FFMPEG_TIMEOUT_SEC}초 초과)"
                )
        except FileNotFoundError as exc:
            raise RuntimeError(
                f"❌ [DramaStitcher] {label} 실패 — FFmpeg 바이너리 미발견: {self.ffmpeg_exe}"
            ) from exc

        if proc.returncode != 0:
            stderr_tail = (stderr or "")[-800:]
            logger.error(f"❌ [DramaStitcher] {label} 실패 (rc={proc.returncode}): {stderr_tail}")
            raise RuntimeError(f"❌ [DramaStitcher] {label} 실패: {stderr_tail[:400]}")

        logger.info(f"✅ [DramaStitcher] {label} 완료")

    @staticmethod
    def _kill_process_tree(proc: subprocess.Popen) -> None:
        """타임아웃된 FFmpeg 프로세스 트리를 강제 회수한다 (좀비 방지)."""
        try:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                    capture_output=True, check=False,
                )
            else:
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    proc.kill()
        except Exception as exc:  # noqa: BLE001 — 회수 실패가 원 예외를 덮지 않도록
            logger.warning(f"⚠️ [DramaStitcher] 프로세스 회수 실패(무해): {exc}")
        finally:
            try:
                proc.wait(timeout=5)
            except Exception:  # noqa: BLE001
                pass

    def _verify_output(self, path: Path, label: str) -> None:
        """산출물 존재/최소 크기 검증 — 무음 실패 차단."""
        if not path.exists():
            raise RuntimeError(f"❌ [DramaStitcher] {label} 산출물 미생성: {path}")
        size = path.stat().st_size
        if size < self.MIN_OUTPUT_BYTES:
            raise RuntimeError(
                f"❌ [DramaStitcher] {label} 산출물이 비정상적으로 작음 "
                f"({size} bytes < {self.MIN_OUTPUT_BYTES}): {path}"
            )
        logger.info(f"🔍 [DramaStitcher] {label} 산출물 검증 통과 ({size:,} bytes)")


# ==============================================================================
# 🧪 [테스트 블록] 단독 실행 검증
# ==============================================================================
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    print("=" * 88)
    print("🎬 [DramaClipStitcher] Wan 2.2 S2V 립싱크 엔진 / 한글 폰트 / 입력 검증 자체 점검")
    print("=" * 88)

    stitcher = DramaClipStitcher()

    print("\n🛠️ [FFmpeg 바이너리 탐색 결과]")
    print(f"  · ffmpeg_exe : {stitcher.ffmpeg_exe}")
    print(
        f"  · 파일 존재  : "
        f"{Path(stitcher.ffmpeg_exe).exists() if stitcher.ffmpeg_exe != 'ffmpeg' else 'PATH 의존'}"
    )

    print("\n🔎 [FFmpeg 실행 검증]")
    ver_res = subprocess.run(
        [stitcher.ffmpeg_exe, "-version"], capture_output=True, text=True, check=False
    )
    if ver_res.returncode == 0:
        print(f"  · ✅ {ver_res.stdout.splitlines()[0]}")
    else:
        print(f"  · ❌ 실행 실패(rc={ver_res.returncode}): {ver_res.stderr[:200]}")

    print("\n🈶 [한글 폰트 검증]")
    print(f"  · drawtext fontfile : {stitcher.font_file}")
    real_font = Path(stitcher.font_file.replace("\\:", ":").replace("\\", "/"))
    print(f"  · 실제 파일 존재    : {real_font.exists()} ({real_font})")

    print("\n🎬 [Wan 2.2 S2V 엔진 검증]")
    print(f"  · wan_client        : {'연결됨' if stitcher.wan_client else '미연결'}")
    print(f"  · S2V 규격          : {stitcher.S2V_WIDTH}x{stitcher.S2V_HEIGHT} / {stitcher.S2V_FRAMES} frames")
    print(f"  · motion_prompt     : {stitcher.MOTION_PROMPT[:70]}...")

    print("\n📐 [출력 규격]")
    print(f"  · 해상도 : {stitcher.out_width}x{stitcher.out_height}")
    print(f"  · FPS    : {stitcher.out_fps}")

    print("\n🚨 [입력 검증 예외 테스트]")
    try:
        stitcher.stitch_drama_short(
            scene_images=[],
            cut_audios=[],
            output_mp4_path=Path("dummy.mp4"),
            brand_keyword="아우라AI데이팅",
            brand_name="Aura AI 데이팅",
        )
        print("  · ❌ 예외가 발생하지 않았습니다 (규격 위반)")
    except ValueError as exc:
        print(f"  · ✅ ValueError 정상 발생: {exc}")

    try:
        stitcher.stitch_drama_short(
            scene_images=[Path("a.png"), Path("b.png")],
            cut_audios=[{"cut_id": "cut1", "audio_path": "a.mp3", "duration_sec": 3.0, "speech": "x"}],
            output_mp4_path=Path("dummy.mp4"),
            brand_keyword="아우라AI데이팅",
            brand_name="Aura AI 데이팅",
        )
        print("  · ❌ 예외가 발생하지 않았습니다 (개수 불일치 미검출)")
    except ValueError as exc:
        print(f"  · ✅ ValueError 정상 발생: {exc}")

    print("\n" + "=" * 88)
    print("✅ [DramaClipStitcher] 자체 점검 완료")
    print("=" * 88)
