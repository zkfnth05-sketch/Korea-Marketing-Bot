# -*- coding: utf-8 -*-
"""
================================================================================
 state_guards.py  ─  Aura 모바일 UI 계층 3: 상태 전이 보증 / 가드 독립 모듈
================================================================================
 [헌장 제1조] 모듈 분리 원칙 준수
   - 단일 책임: "화면이 목표 상태로 실제 전이되었는가"를 보증(Guard)한다.
   - 판독은 계층 1(ScreenReader), 앵커 해석은 계층 2(SemanticResolver)에 위임.
   - 게시/업로드 판단 로직은 일절 포함하지 않는다.

 [핵심 설계]
   1) wait_for_condition   : 고정 sleep 체인 전면 폐기 → dump_ui() 폴링 기반 조건 대기
   2) CaptionGate          : AdbIME 활성화 → 입력창 탭 → base64 주입 → 🔍 EditText text
                             재판독 실측 검증(미주입 시 재시도) → ESC(111)+BACK(4) 키보드
                             완전 닫기 → 하단 [게시] 버튼 노출 확인
   3) PopupGate            : 방해 모달("나중에"/"다음에"/"닫기") 소탕 +
                             🛡️ 블랙리스트 보호 가드(취소/게시/임시저장 절대 오터치 금지)
   4) KeyboardGuard        : AdbIME ↔ 삼성 HoneyBoardService 원복 + Context Manager
                             (예외 발생 시에도 무조건 삼성 키보드 자동 원복 보장)
================================================================================
"""

from __future__ import annotations

import base64
import time
import xml.etree.ElementTree as ET
from typing import Callable, Dict, List, Optional, Tuple

# ──────────────────────────────────────────────────────────────────────────────
# 상수
# ──────────────────────────────────────────────────────────────────────────────
ADB_IME_ID = "com.android.adbkeyboard/.AdbIME"
SAMSUNG_IME_ID = "com.samsung.android.honeyboard/.service.HoneyBoardService"

# 키보드 완전 닫기 키이벤트
KEYCODE_ESCAPE = "111"
KEYCODE_BACK = "4"

# 방해 모달 닫기 후보 (정확 일치 우선)
POPUP_DISMISS_TEXTS: Tuple[str, ...] = ("나중에", "다음에", "닫기", "나중에 하기", "다음에 하기")

# 🛡️ 블랙리스트: 업로드 파이프라인 핵심 버튼 — 절대 닫기 타깃으로 오인 터치 금지
PROTECTED_BLACKLIST: Tuple[str, ...] = (
    "취소", "게시", "게시하기", "임시저장", "임시 저장", "저장", "다음", "확인",
    "Post", "Publish", "Cancel", "Save", "Next", "OK",
)

# 캡션 주입 검증 재시도 횟수
CAPTION_INJECT_ATTEMPTS = 3


class StateTransitionTimeoutError(RuntimeError):
    """목표 상태로 전이되지 않았을 때 발생. 어느 단계에서 왜 실패했는지 명시한다."""


class GuardViolationError(RuntimeError):
    """가드 규칙 위반(블랙리스트 오터치 시도 등) 시 발생."""


# ══════════════════════════════════════════════════════════════════════════════
# 1) 조건 대기 (고정 sleep 폐기)
# ══════════════════════════════════════════════════════════════════════════════
def wait_for_condition(
    screen_reader,
    predicate: Callable[[ET.Element], bool],
    timeout: float = 15.0,
    interval: float = 1.0,
    description: str = "",
) -> ET.Element:
    """
    screen_reader.dump_ui() 를 interval 간격으로 폴링하여 predicate(root) 가 True 가 될 때까지 대기.
    성공 시 해당 root Element 반환. 타임아웃 시 StateTransitionTimeoutError.
    """
    label = description or getattr(predicate, "__name__", "predicate")
    deadline = time.time() + float(timeout)
    last_error: Optional[Exception] = None
    polls = 0

    while time.time() < deadline:
        polls += 1
        try:
            root = screen_reader.dump_ui()
            if predicate(root):
                return root
        except Exception as exc:  # ScreenReadError 등 — 폴링 지속
            last_error = exc
        time.sleep(float(interval))

    raise StateTransitionTimeoutError(
        f"[{label}] 상태 전이 실패: {timeout}s 내 조건 미충족 "
        f"(폴링 {polls}회, interval={interval}s, 마지막 오류={last_error})"
    )


# ══════════════════════════════════════════════════════════════════════════════
# 2) 캡션 입력 게이트
# ══════════════════════════════════════════════════════════════════════════════
class CaptionGate:
    """설명(캡션) 입력 → 실측 검증 → 키보드 닫기 → 게시 버튼 노출 확인."""

    def __init__(self, keyboard_guard: Optional["KeyboardGuard"] = None) -> None:
        self.keyboard_guard = keyboard_guard or KeyboardGuard()

    # ── EditText 노드 수집 ──
    @staticmethod
    def _collect_edittexts(root: ET.Element) -> List[ET.Element]:
        out: List[ET.Element] = []
        for node in root.iter("node"):
            cls = (node.get("class") or "")
            if "EditText" in cls:
                out.append(node)
        return out

    # ── 실제 주입 여부 실측 검증 ──
    def verify_caption_injected(
        self,
        screen_reader,
        caption_text: str,
        sample_len: int = 12,
    ) -> bool:
        """
        dump_ui() 로 EditText 노드의 text 속성을 재판독하여 실제 캡션이 주입되었는지 확인.
        공백/개행 정규화 후 앞 sample_len 글자 일치 여부로 판정.
        """
        def _norm(s: str) -> str:
            return "".join((s or "").split())

        target = _norm(caption_text)[:sample_len]
        if not target:
            return False

        try:
            root = screen_reader.dump_ui()
        except Exception:
            return False

        for node in self._collect_edittexts(root):
            actual = _norm(node.get("text") or "")
            if target in actual:
                return True
        # EditText 클래스가 없는 커스텀 입력창 대비: 전체 노드 text 스캔
        for node in root.iter("node"):
            actual = _norm(node.get("text") or "")
            if target and target in actual:
                return True
        return False

    # ── 메인: 캡션 입력 + 검증 ──
    def input_caption_verified(
        self,
        screen_reader,
        resolver,
        adb_path,
        caption_text: str,
        edit_spec: Dict[str, object],
        verify_timeout: float = 6.0,
        verify_interval: float = 1.0,
    ) -> bool:
        """
        AdbIME 활성화 → 설명 입력창 탭 → base64 브로드캐스트 주입 →
        EditText text 재판독 실측 검증(미주입 시 재시도) → ESC+BACK 키보드 완전 닫기 →
        하단 [게시] 버튼 노출 확인.
        """
        # 1) AdbIME 활성화
        self.keyboard_guard.activate_adb_keyboard()

        # 2) 설명 입력창 탭 (계층 2 앵커 해석)
        try:
            cx, cy = resolver.resolve_center(
                screen_reader.dump_ui(),
                exact_text=edit_spec.get("exact_text"),          # type: ignore[arg-type]
                regex_pattern=edit_spec.get("regex_pattern"),    # type: ignore[arg-type]
                text_contains=edit_spec.get("text_contains"),    # type: ignore[arg-type]
                prefer_clickable=bool(edit_spec.get("prefer_clickable", True)),
            )
            screen_reader.run_adb("shell", "input", "tap", str(cx), str(cy))
        except Exception as exc:
            raise StateTransitionTimeoutError(
                f"[CaptionGate] 설명 입력창 탭 실패: 앵커 {edit_spec} 미발견 ({exc})"
            ) from exc

        time.sleep(0.8)

        # 3) base64 주입 + 실측 검증 (미주입 시 재시도)
        b64_msg = base64.b64encode(caption_text.encode("utf-8")).decode("utf-8")
        injected = False
        for attempt in range(1, CAPTION_INJECT_ATTEMPTS + 1):
            screen_reader.run_adb(
                "shell", "am", "broadcast", "-a", "ADB_INPUT_B64", "--es", "msg", b64_msg
            )
            time.sleep(1.2)

            # 🔍 실측 검증: dump_ui 재판독
            deadline = time.time() + float(verify_timeout)
            while time.time() < deadline:
                if self.verify_caption_injected(screen_reader, caption_text):
                    injected = True
                    break
                time.sleep(float(verify_interval))
            if injected:
                break
            # 재시도 전 입력창 재탭
            try:
                screen_reader.run_adb("shell", "input", "tap", str(cx), str(cy))
                time.sleep(0.5)
            except Exception:
                pass

        if not injected:
            raise StateTransitionTimeoutError(
                f"[CaptionGate] 캡션 주입 실측 검증 실패: {CAPTION_INJECT_ATTEMPTS}회 재시도 후에도 "
                f"EditText text 에 캡션이 반영되지 않았습니다. (앞 20자: {caption_text[:20]!r})"
            )

        # 4) 키보드 닫기: ESC(111) 호출 (화면 이탈 방지를 위해 mInputShown=true 일 때만 BACK 호출)
        screen_reader.run_adb("shell", "input", "keyevent", KEYCODE_ESCAPE)
        time.sleep(0.8)
        try:
            ime_dump = screen_reader.run_adb("shell", "dumpsys", "input_method")
            if "mInputShown=true" in ime_dump:
                screen_reader.run_adb("shell", "input", "keyevent", KEYCODE_BACK)
                time.sleep(0.8)
        except Exception:
            pass

        # 5) 하단 [게시] 버튼 노출 확인
        try:
            wait_for_condition(
                screen_reader,
                lambda root: resolver.find_node(
                    root,
                    regex_pattern=r"^(게시|게시하기|Post|Publish)$",
                    prefer_clickable=True,
                ) is not None,
                timeout=8.0,
                interval=1.0,
                description="CaptionGate: 하단 [게시] 버튼 노출",
            )
        except StateTransitionTimeoutError as exc:
            raise StateTransitionTimeoutError(
                f"[CaptionGate] 키보드 닫기 후 [게시] 버튼이 노출되지 않았습니다. ({exc})"
            ) from exc

        return True


# ══════════════════════════════════════════════════════════════════════════════
# 3) 팝업 소탕 게이트 (블랙리스트 보호 가드)
# ══════════════════════════════════════════════════════════════════════════════
class PopupGate:
    """방해 모달을 닫되, 업로드 파이프라인 핵심 버튼은 절대 건드리지 않는다."""

    def __init__(self, blacklist: Tuple[str, ...] = PROTECTED_BLACKLIST) -> None:
        self.blacklist = tuple(blacklist)

    def is_protected(self, text: str) -> bool:
        """블랙리스트 보호 대상 여부 (정확 일치 기준)."""
        t = (text or "").strip()
        if not t:
            return False
        return any(t == b for b in self.blacklist)

    def _find_dismiss_target(self, root: ET.Element) -> Optional[Tuple[str, int, int]]:
        """닫기 타깃 (텍스트, cx, cy) 탐색. 블랙리스트는 절대 반환하지 않는다."""
        for node in root.iter("node"):
            texts = []
            t = (node.get("text") or "").strip()
            d = (node.get("content-desc") or "").strip()
            if t:
                texts.append(t)
            if d:
                texts.append(d)
            if not texts:
                continue

            for label in texts:
                # 🛡️ 블랙리스트 보호 가드: 업로드 파이프라인 버튼은 즉시 배제
                if self.is_protected(label):
                    continue
                if label not in POPUP_DISMISS_TEXTS:
                    continue

                bounds = node.get("bounds") or ""
                nums = [int(n) for n in __import__("re").findall(r"-?\d+", bounds)]
                if len(nums) != 4:
                    continue
                x1, y1, x2, y2 = nums
                if x2 <= x1 or y2 <= y1:
                    continue
                return (label, (x1 + x2) // 2, (y1 + y2) // 2)
        return None

    def dismiss_popups(self, screen_reader, resolver, max_attempts: int = 3) -> int:
        """
        방해 모달("나중에"/"다음에"/"닫기") 감지 시 닫기 탭.
        블랙리스트(취소/게시/임시저장 등)는 절대 오터치하지 않는다.
        실제로 닫은 횟수 반환.
        """
        dismissed = 0
        for _ in range(int(max_attempts)):
            try:
                root = screen_reader.dump_ui()
            except Exception:
                break

            target = self._find_dismiss_target(root)
            if target is None:
                break

            label, cx, cy = target
            # 이중 안전장치: 블랙리스트 재검증
            if self.is_protected(label):
                raise GuardViolationError(
                    f"[PopupGate] 블랙리스트 보호 버튼 '{label}' 오터치 시도 차단"
                )

            screen_reader.run_adb("shell", "input", "tap", str(cx), str(cy))
            dismissed += 1
            time.sleep(1.2)

        return dismissed


# ══════════════════════════════════════════════════════════════════════════════
# 4) 키보드 가드 (Context Manager 지원)
# ══════════════════════════════════════════════════════════════════════════════
class KeyboardGuard:
    """AdbIME 활성화 / 삼성 키보드 원복 + 예외 안전 Context Manager."""

    def __init__(self, screen_reader=None, adb_path=None) -> None:
        self.screen_reader = screen_reader
        self.adb_path = adb_path
        self._restored = False

    # ── ADB 실행 (screen_reader 우선, 없으면 subprocess) ──
    def _run_adb(self, *args: str) -> str:
        if self.screen_reader is not None:
            return self.screen_reader.run_adb(*args)
        import subprocess
        from pathlib import Path

        adb = Path(self.adb_path) if self.adb_path else None
        if adb is None:
            return ""
        try:
            res = subprocess.run(
                [str(adb)] + [str(a) for a in args],
                capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=20.0,
            )
            return (res.stdout or "").strip()
        except Exception:
            return ""

    def activate_adb_keyboard(self) -> None:
        """한글/해시태그 주입을 위한 AdbIME 활성화."""
        self._run_adb("shell", "ime", "set", ADB_IME_ID)
        time.sleep(0.5)
        self._restored = False

    def restore_samsung_keyboard(self) -> None:
        """삼성 기본 키보드(HoneyBoardService)로 원복."""
        self._run_adb("shell", "ime", "set", SAMSUNG_IME_ID)
        time.sleep(0.3)
        self._restored = True

    # ── Context Manager ──
    def __enter__(self) -> "KeyboardGuard":
        self.activate_adb_keyboard()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        # 예외 발생 여부와 무관하게 무조건 삼성 키보드 원복
        try:
            self.restore_samsung_keyboard()
        except Exception:
            pass
        return False  # 예외 전파 유지


# ══════════════════════════════════════════════════════════════════════════════
# 단독 실행 스모크 테스트
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    print("[SMOKE] state_guards 스모크 테스트 시작")

    # ── ① PopupGate 블랙리스트 보호 가드 (오프라인) ──
    gate = PopupGate()
    assert gate.is_protected("취소") is True, "블랙리스트 '취소' 보호 실패"
    assert gate.is_protected("게시") is True, "블랙리스트 '게시' 보호 실패"
    assert gate.is_protected("임시저장") is True, "블랙리스트 '임시저장' 보호 실패"
    assert gate.is_protected("나중에") is False, "닫기 후보 오분류"
    print("[SMOKE] ✅ PopupGate 블랙리스트 보호 가드 정상")

    fake_xml = """<hierarchy>
      <node text="취소" bounds="[40,2100][300,2200]" clickable="true" enabled="true"/>
      <node text="게시" bounds="[800,2100][1060,2200]" clickable="true" enabled="true"/>
      <node text="나중에" bounds="[600,1200][900,1300]" clickable="true" enabled="true"/>
    </hierarchy>"""
    fake_root = ET.fromstring(fake_xml)
    target = gate._find_dismiss_target(fake_root)
    assert target is not None and target[0] == "나중에", f"닫기 타깃 오선택: {target}"
    print(f"[SMOKE] ✅ 닫기 타깃 정확 선택: {target} (취소/게시 회피)")

    # ── ② wait_for_condition 타임아웃 ──
    class _FakeReader:
        def dump_ui(self, pause_video: bool = False):
            return ET.fromstring("<hierarchy><node text='x' bounds='[0,0][100,100]'/></hierarchy>")

        def run_adb(self, *a, **k):
            return ""

    try:
        wait_for_condition(_FakeReader(), lambda r: False, timeout=1.5, interval=0.5, description="테스트조건")
        print("[SMOKE] ❌ StateTransitionTimeoutError 미발생")
        sys.exit(1)
    except StateTransitionTimeoutError as exc:
        print(f"[SMOKE] ✅ StateTransitionTimeoutError 정상: {str(exc)[:90]}")

    # ── ③ KeyboardGuard Context Manager (예외 시 원복) ──
    calls: List[str] = []

    class _FakeReader2:
        def run_adb(self, *a, **k):
            calls.append(" ".join(str(x) for x in a))
            return ""

    kg = KeyboardGuard(screen_reader=_FakeReader2())
    try:
        with kg:
            raise ValueError("의도적 예외")
    except ValueError:
        pass
    assert any("AdbIME" in c for c in calls), "AdbIME 활성화 미호출"
    assert any("HoneyBoardService" in c for c in calls), "삼성 키보드 원복 미호출"
    print(f"[SMOKE] ✅ KeyboardGuard 예외 시에도 삼성 키보드 원복 보장 (호출 {len(calls)}회)")

    # ── ④ 실기기 연동 ──
    try:
        from screen_reader import ScreenReader, ScreenReadError
        from semantic_resolver import SemanticResolver

        reader = ScreenReader()
        resolver = SemanticResolver()
        root = reader.dump_ui()
        print(f"[SMOKE] ✅ 실기기 dump 성공: node_count={len(list(root.iter('node')))}")

        cg = CaptionGate()
        edit_nodes = cg._collect_edittexts(root)
        print(f"[SMOKE] ✅ EditText 노드 수집: {len(edit_nodes)}개")

        dismissed = PopupGate().dismiss_popups(reader, resolver, max_attempts=1)
        print(f"[SMOKE] ✅ PopupGate 실기기 스캔 완료: 닫은 팝업 {dismissed}개")
    except ScreenReadError as exc:
        print(f"[SMOKE] ⚠️ 실기기 판독 불가(환경 의존): {exc}")

    print("[SMOKE] ✅ 전체 스모크 테스트 통과")
