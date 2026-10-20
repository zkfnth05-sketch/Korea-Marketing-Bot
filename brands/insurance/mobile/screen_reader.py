# -*- coding: utf-8 -*-
"""
================================================================================
 screen_reader.py  ─  Aura 모바일 UI 계층 1: 화면 판독 전담 독립 모듈
================================================================================
 [헌장 제1조] 모듈 분리 원칙 준수
   - 단일 책임: 오직 "화면(UI) XML 판독"만 담당한다.
   - 판단/해석/좌표 계산/게시 로직은 일절 포함하지 않는다.
   - SemanticResolver(계층 2)가 본 모듈의 ElementTree 를 소비한다.

 [핵심 설계]
   1) stale dump 선삭제  : 이전 회차 XML 이 남아 '성공'으로 오판되는 것을 원천 차단
   2) --compressed 우선  : uiautomator dump --compressed 로 전송량/시간 절감
   3) 실패 시 자동 복구  : 화면 중앙(540,1100) 탭 → 영상 일시정지 → 지수 백오프
                           (1s → 2s → 4s) 3회 재시도
   4) 신선도 검증        : pull 후 파일 크기 > 0 AND mtime < 5초 를 모두 만족해야 반환
   5) 실패는 예외로      : 조용한 None 반환 금지 → ScreenReadError 로 즉시 중단
================================================================================
"""

from __future__ import annotations

import subprocess
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Sequence

# ──────────────────────────────────────────────────────────────────────────────
# 경로 상수 (기존 업로더와 동일한 규약 유지)
# ──────────────────────────────────────────────────────────────────────────────
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent.parent
ENGINE_DIR = PROJECT_ROOT / "kmarket-marketing-engine"
ADB_PATH = ENGINE_DIR / "tools" / "platform-tools" / "adb.exe"

DEVICE_DUMP_PATH = "/sdcard/flow_dump.xml"
LOCAL_DUMP_PATH = CURRENT_DIR / "temp_flow_dump.xml"

# 영상 일시정지용 화면 중앙 좌표 (실측: 1080x2050 해상도 기준)
SCREEN_CENTER = (540, 1100)

# 신선도 임계값 (초)
FRESHNESS_LIMIT_SEC = 5.0

# 지수 백오프 대기열 (1s → 2s → 4s)
BACKOFF_DELAYS: Sequence[float] = (1.0, 2.0, 4.0)


class ScreenReadError(RuntimeError):
    """화면 판독이 최종 실패했을 때 발생. 상위 계층은 즉시 중단해야 한다."""


class ScreenReader:
    """ADB 를 통해 현재 화면의 UIAutomator XML 을 신뢰성 있게 판독한다."""

    def __init__(
        self,
        adb_path: Optional[Path] = None,
        device_dump_path: str = DEVICE_DUMP_PATH,
        local_dump_path: Optional[Path] = None,
        freshness_limit: float = FRESHNESS_LIMIT_SEC,
        backoff_delays: Sequence[float] = BACKOFF_DELAYS,
    ) -> None:
        self.adb = Path(adb_path) if adb_path else ADB_PATH
        self.device_dump_path = device_dump_path
        self.local_dump_path = Path(local_dump_path) if local_dump_path else LOCAL_DUMP_PATH
        self.freshness_limit = float(freshness_limit)
        self.backoff_delays = tuple(backoff_delays)

    # ──────────────────────────────────────────────────────────────────────
    # ADB 저수준 실행
    # ──────────────────────────────────────────────────────────────────────
    def run_adb(self, *args: str, timeout: float = 20.0) -> str:
        """ADB 명령 실행 후 stdout 반환. 실패해도 예외를 던지지 않는다."""
        cmd = [str(self.adb)] + [str(a) for a in args]
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=timeout,
            )
            return (res.stdout or "").strip()
        except Exception:
            return ""

    # ──────────────────────────────────────────────────────────────────────
    # stale dump 선삭제
    # ──────────────────────────────────────────────────────────────────────
    def _purge_stale_dump(self) -> None:
        """로컬/디바이스 양쪽의 이전 회차 XML 을 먼저 제거한다."""
        try:
            if self.local_dump_path.exists():
                self.local_dump_path.unlink()
        except Exception:
            pass
        # 디바이스 측 잔여 파일도 제거 (실패 무시)
        self.run_adb("shell", "rm", "-f", self.device_dump_path)

    # ──────────────────────────────────────────────────────────────────────
    # 신선도 검증
    # ──────────────────────────────────────────────────────────────────────
    def _is_fresh(self) -> bool:
        """파일 크기 > 0 이고 mtime 이 임계값 이내일 때만 True."""
        try:
            if not self.local_dump_path.exists():
                return False
            stat = self.local_dump_path.stat()
            if stat.st_size <= 0:
                return False
            age = time.time() - stat.st_mtime
            return age < self.freshness_limit
        except Exception:
            return False

    # ──────────────────────────────────────────────────────────────────────
    # 영상 일시정지 (좌표 탭)
    # ──────────────────────────────────────────────────────────────────────
    def _pause_video_by_tap(self) -> None:
        """화면 중앙을 탭하여 영상 재생을 일시정지시킨다."""
        x, y = SCREEN_CENTER
        self.run_adb("shell", "input", "tap", str(x), str(y))

    # ──────────────────────────────────────────────────────────────────────
    # 단일 dump 시도
    # ──────────────────────────────────────────────────────────────────────
    def _try_dump_once(self, compressed: bool) -> bool:
        """dump 1회 시도. 성공적으로 pull 되어 신선도 검증을 통과하면 True."""
        if compressed:
            self.run_adb("shell", "uiautomator", "dump", "--compressed", self.device_dump_path)
        else:
            self.run_adb("shell", "uiautomator", "dump", self.device_dump_path)

        self.run_adb("pull", self.device_dump_path, str(self.local_dump_path))
        return self._is_fresh()

    # ──────────────────────────────────────────────────────────────────────
    # 공개 API: dump_ui
    # ──────────────────────────────────────────────────────────────────────
    def dump_ui(self, pause_video: bool = False) -> ET.Element:
        """
        현재 화면의 UIAutomator XML 루트 Element 를 반환한다.

        절차:
          1) stale dump 선삭제
          2) --compressed 우선 dump 시도
          3) 실패 시: 화면 중앙 탭(영상 일시정지) → 지수 백오프(1s/2s/4s) 3회 재시도
          4) 매 시도마다 크기>0 & mtime<5s 검증
          5) 최종 실패 시 ScreenReadError 발생 (조용한 None 금지)
        """
        self._purge_stale_dump()

        if pause_video:
            self._pause_video_by_tap()
            time.sleep(0.4)

        # 1차: --compressed 우선
        if self._try_dump_once(compressed=True):
            return self._parse_or_raise()

        # 2차: 압축 없이 1회 재시도
        if self._try_dump_once(compressed=False):
            return self._parse_or_raise()

        # 3차: 영상 일시정지 + 지수 백오프 재시도
        for delay in self.backoff_delays:
            self._pause_video_by_tap()
            time.sleep(delay)
            if self._try_dump_once(compressed=True):
                return self._parse_or_raise()

        raise ScreenReadError(
            "화면 판독 최종 실패: dump 파일이 생성되지 않았거나 신선도 검증을 통과하지 못했습니다. "
            f"(path={self.local_dump_path}, freshness<{self.freshness_limit}s)"
        )

    # ──────────────────────────────────────────────────────────────────────
    # 내부: XML 파싱
    # ──────────────────────────────────────────────────────────────────────
    def _parse_or_raise(self) -> ET.Element:
        """신선도 검증을 통과한 XML 을 파싱하여 루트 Element 반환."""
        try:
            tree = ET.parse(str(self.local_dump_path))
            return tree.getroot()
        except Exception as exc:
            raise ScreenReadError(f"XML 파싱 실패: {exc}") from exc

    # ──────────────────────────────────────────────────────────────────────
    # 편의: 텍스트 스냅샷 (디버그/로그용)
    # ──────────────────────────────────────────────────────────────────────
    def dump_text_snapshot(self, pause_video: bool = False) -> str:
        """화면 내 모든 텍스트를 ' | ' 로 결합해 반환 (로그/디버그 전용)."""
        root = self.dump_ui(pause_video=pause_video)
        texts = []
        for node in root.iter("node"):
            t = (node.get("text") or "").strip()
            d = (node.get("content-desc") or "").strip()
            if t:
                texts.append(t)
            if d:
                texts.append(f"[desc]{d}")
        return " | ".join(texts)


# ──────────────────────────────────────────────────────────────────────────────
# 단독 실행 스모크 테스트
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    print("[SMOKE] ScreenReader 스모크 테스트 시작")
    reader = ScreenReader()
    print(f"[SMOKE] ADB 경로: {reader.adb} (exists={reader.adb.exists()})")

    try:
        root = reader.dump_ui()
        nodes = list(root.iter("node"))
        print(f"[SMOKE] ✅ dump_ui 성공: root={root.tag}, node_count={len(nodes)}")
        snapshot = reader.dump_text_snapshot()
        print(f"[SMOKE] 텍스트 스냅샷(앞 300자): {snapshot[:300]}")
    except ScreenReadError as exc:
        print(f"[SMOKE] ❌ ScreenReadError: {exc}")
        sys.exit(1)
