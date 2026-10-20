# -*- coding: utf-8 -*-
"""
================================================================================
 semantic_resolver.py  ─  Aura 모바일 UI 계층 2: 의미 기반 앵커 탐색 독립 모듈
================================================================================
 [헌장 제1조] 모듈 분리 원칙 준수
   - 단일 책임: "화면 XML → 의미 있는 앵커 노드 → 유효 탭 좌표" 변환만 담당.
   - ADB 실행/덤프/재시도는 계층 1(ScreenReader)에 완전 위임한다.
   - 게시/업로드/판단 로직은 일절 포함하지 않는다.

 [핵심 설계]
   1) 3단 우선순위 매칭 : exact_text → regex_pattern → text_contains
      · regex 는 fullmatch 로 강제하여 '이 게시물을 볼 수 있는 사람' 오탐 100% 차단
   2) bounds 유효성 필터 : [0,0][0,0] 배제 + 화면 영역(0<=x<=1080, 0<=y<=2280) 내만 유효
   3) clickable 우선 채택  : clickable="true" AND enabled="true" 노드 우선
   4) 부모 역추적(최대 3단) : 자식 bounds 무효 시 부모로 상승, 면적 70%↑ 거대 컨테이너 배제
   5) 🛑 하드코딩 폴백 좌표 전면 금지 : 탐색 실패 시 AnchorNotFoundError 즉시 발생
   6) tap_by_anchor        : dump_ui() 폴링 → 앵커 발견 즉시 tap
================================================================================
"""

from __future__ import annotations

import re
import time
import xml.etree.ElementTree as ET
from typing import Callable, Dict, List, Optional, Tuple

# ──────────────────────────────────────────────────────────────────────────────
# 상수
# ──────────────────────────────────────────────────────────────────────────────
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 2280
SCREEN_AREA = SCREEN_WIDTH * SCREEN_HEIGHT

# 거대 컨테이너 배제 임계값 (화면 면적 대비)
GIANT_CONTAINER_RATIO = 0.70

# 부모 역추적 최대 깊이
MAX_PARENT_CLIMB_DEPTH = 3

Bounds = Tuple[int, int, int, int]


class AnchorNotFoundError(RuntimeError):
    """앵커를 찾지 못했을 때 발생. 하드코딩 좌표 폴백은 절대 금지한다."""


class SemanticResolver:
    """UIAutomator XML 트리에서 의미 기반으로 앵커 노드/좌표를 해석한다."""

    # ──────────────────────────────────────────────────────────────────────
    # bounds 파싱 / 유효성 검증
    # ──────────────────────────────────────────────────────────────────────
    @staticmethod
    def parse_bounds(bounds_str: Optional[str]) -> Optional[Bounds]:
        """'[x1,y1][x2,y2]' → (x1, y1, x2, y2). 형식 불일치 시 None."""
        if not bounds_str:
            return None
        nums = re.findall(r"-?\d+", bounds_str)
        if len(nums) != 4:
            return None
        try:
            x1, y1, x2, y2 = (int(n) for n in nums)
        except Exception:
            return None
        return (x1, y1, x2, y2)

    @classmethod
    def is_valid_bounds(cls, rect: Optional[Bounds]) -> bool:
        """[0,0][0,0] 배제 + 화면 영역 내 + 최소 10px 크기 검증."""
        if not rect:
            return False
        x1, y1, x2, y2 = rect
        if x2 <= x1 or y2 <= y1:
            return False
        if (x2 - x1) <= 10 or (y2 - y1) <= 10:
            return False
        # 화면 영역 밖이면 무효
        if x1 < 0 or y1 < 0 or x2 > SCREEN_WIDTH or y2 > SCREEN_HEIGHT:
            return False
        return True

    @classmethod
    def is_giant_container(cls, rect: Optional[Bounds]) -> bool:
        """화면 면적 70% 이상인 거대 컨테이너 여부 (탭 오작동 방지)."""
        if not rect:
            return False
        x1, y1, x2, y2 = rect
        area = max(0, x2 - x1) * max(0, y2 - y1)
        return area >= SCREEN_AREA * GIANT_CONTAINER_RATIO

    @staticmethod
    def center_of(rect: Bounds) -> Tuple[int, int]:
        """bounds → 중심 좌표."""
        x1, y1, x2, y2 = rect
        return ((x1 + x2) // 2, (y1 + y2) // 2)

    # ──────────────────────────────────────────────────────────────────────
    # 노드 텍스트 추출
    # ──────────────────────────────────────────────────────────────────────
    @staticmethod
    def _node_texts(node: ET.Element) -> List[str]:
        """text 와 content-desc 를 모두 후보 텍스트로 반환."""
        out: List[str] = []
        t = (node.get("text") or "").strip()
        d = (node.get("content-desc") or "").strip()
        if t:
            out.append(t)
        if d:
            out.append(d)
        return out

    @staticmethod
    def _is_clickable(node: ET.Element) -> bool:
        return (node.get("clickable") or "").lower() == "true"

    @staticmethod
    def _is_enabled(node: ET.Element) -> bool:
        return (node.get("enabled") or "").lower() == "true"

    # ──────────────────────────────────────────────────────────────────────
    # 3단 우선순위 매칭
    # ──────────────────────────────────────────────────────────────────────
    def find_node(
        self,
        root: ET.Element,
        exact_text: Optional[str] = None,
        regex_pattern: Optional[str] = None,
        text_contains: Optional[str] = None,
        resource_id: Optional[str] = None,
        prefer_clickable: bool = True,
    ) -> Optional[ET.Element]:
        """
        3단 우선순위로 앵커 노드를 탐색한다.
          1순위: exact_text 완전일치 (text 또는 content-desc)
          2순위: regex_pattern fullmatch (오탐 원천 차단)
          3순위: text_contains 부분일치
        bounds 무효 노드는 후보에서 제외. prefer_clickable=True 시 clickable+enabled 우선.
        """
        if not any([exact_text, regex_pattern, text_contains, resource_id]):
            raise ValueError("exact_text / regex_pattern / text_contains 중 최소 1개는 필요합니다.")

        compiled: Optional[re.Pattern] = None
        if regex_pattern:
            compiled = re.compile(regex_pattern)

        # 후보 수집: (우선순위, clickable_ok, node)
        candidates: List[Tuple[int, int, ET.Element]] = []

        parent_map: Dict[ET.Element, ET.Element] = {child: parent for parent in root.iter() for child in parent}

        for node in root.iter("node"):
            texts = self._node_texts(node)
            if not texts and not resource_id:
                continue

            priority = 0
            if exact_text is not None and any(t == exact_text for t in texts):
                priority = 1
            elif compiled is not None and any(compiled.fullmatch(t) for t in texts):
                priority = 2
            elif text_contains is not None and any(text_contains in t for t in texts):
                priority = 3
            elif resource_id is not None and resource_id in (node.get('resource-id') or ''):
                priority = 2

            if priority == 0:
                continue

            # bounds 유효성 검사 (자신이 [0,0][0,0]이라도 부모가 유효 bounds를 가지면 채택)
            rect = self.parse_bounds(node.get("bounds"))
            has_valid = self.is_valid_bounds(rect)
            if not has_valid:
                curr = parent_map.get(node)
                p_depth = 0
                while curr is not None and p_depth < MAX_PARENT_CLIMB_DEPTH:
                    p_rect = self.parse_bounds(curr.get("bounds"))
                    if self.is_valid_bounds(p_rect) and not self.is_giant_container(p_rect):
                        has_valid = True
                        break
                    curr = parent_map.get(curr)
                    p_depth += 1

            if not has_valid:
                continue

            clickable_ok = 1 if (self._is_clickable(node) and self._is_enabled(node)) else 0
            candidates.append((priority, clickable_ok, node))

        if not candidates:
            return None

        # 정렬: 우선순위 낮을수록(1순위) 우선, prefer_clickable 시 clickable_ok 높을수록 우선
        if prefer_clickable:
            candidates.sort(key=lambda c: (c[0], -c[1]))
        else:
            candidates.sort(key=lambda c: c[0])

        return candidates[0][2]

    # ──────────────────────────────────────────────────────────────────────
    # 부모 역추적 좌표 계산
    # ──────────────────────────────────────────────────────────────────────
    def find_clickable_center_with_parent_climb(
        self,
        root: ET.Element,
        match_fn: Callable[[ET.Element], bool],
        max_depth: int = MAX_PARENT_CLIMB_DEPTH,
    ) -> Tuple[int, int]:
        """
        match_fn 을 만족하는 노드를 찾고, bounds 가 무효하면 부모를 최대 max_depth 단계 역추적.
        거대 컨테이너(면적 70%↑)는 탭 오작동 방지를 위해 배제.
        유효 중심 좌표 (cx, cy) 반환. 실패 시 AnchorNotFoundError.
        """
        parent_map: Dict[ET.Element, ET.Element] = {child: parent for parent in root.iter() for child in parent}

        target: Optional[ET.Element] = None
        for node in root.iter("node"):
            try:
                if match_fn(node):
                    target = node
                    break
            except Exception:
                continue

        if target is None:
            raise AnchorNotFoundError("match_fn 을 만족하는 앵커 노드를 찾지 못했습니다.")

        # 자신 → 부모 순으로 최대 max_depth 단계까지 상승
        current: Optional[ET.Element] = target
        depth = 0
        while current is not None and depth <= max_depth:
            rect = self.parse_bounds(current.get("bounds"))
            if self.is_valid_bounds(rect) and not self.is_giant_container(rect):
                return self.center_of(rect)  # type: ignore[arg-type]
            current = parent_map.get(current)
            depth += 1

        raise AnchorNotFoundError(
            f"앵커 '{self._describe(target)}' 의 유효 좌표를 {max_depth}단계 부모 역추적 내에서 확정하지 못했습니다. "
            "(하드코딩 폴백 좌표 사용 금지)"
        )

    # ──────────────────────────────────────────────────────────────────────
    # 앵커 스펙 → 좌표 해석 (통합 진입점)
    # ──────────────────────────────────────────────────────────────────────
    def resolve_center(
        self,
        root: ET.Element,
        exact_text: Optional[str] = None,
        regex_pattern: Optional[str] = None,
        text_contains: Optional[str] = None,
        resource_id: Optional[str] = None,
        prefer_clickable: bool = True,
        max_depth: int = MAX_PARENT_CLIMB_DEPTH,
    ) -> Tuple[int, int]:
        """find_node + 부모 역추적을 결합하여 최종 탭 좌표를 반환."""
        node = self.find_node(
            root,
            exact_text=exact_text,
            regex_pattern=regex_pattern,
            text_contains=text_contains,
            resource_id=resource_id,
            prefer_clickable=prefer_clickable,
        )
        if node is None:
            spec = exact_text or regex_pattern or text_contains or resource_id
            raise AnchorNotFoundError(f"앵커 스펙 '{spec}' 에 해당하는 노드가 화면에 없습니다.")

        parent_map: Dict[ET.Element, ET.Element] = {child: parent for parent in root.iter() for child in parent}
        current: Optional[ET.Element] = node
        depth = 0
        while current is not None and depth <= max_depth:
            rect = self.parse_bounds(current.get("bounds"))
            if self.is_valid_bounds(rect) and not self.is_giant_container(rect):
                return self.center_of(rect)  # type: ignore[arg-type]
            current = parent_map.get(current)
            depth += 1

        raise AnchorNotFoundError(
            f"앵커 '{self._describe(node)}' 의 유효 좌표 확정 실패 (부모 {max_depth}단계 역추적 소진)."
        )

    # ──────────────────────────────────────────────────────────────────────
    # tap_by_anchor : dump_ui 폴링 후 탭
    # ──────────────────────────────────────────────────────────────────────
    def tap_by_anchor(
        self,
        screen_reader,
        match_spec: Dict[str, object],
        timeout: float = 10.0,
        retry_interval: float = 1.0,
        pause_video: bool = False,
    ) -> Tuple[int, int]:
        """
        screen_reader.dump_ui() 를 retry_interval 간격으로 폴링하며 앵커를 찾아 tap.
        match_spec 예: {"exact_text": "게시", "prefer_clickable": True}
        성공 시 (cx, cy) 반환. timeout 초과 시 AnchorNotFoundError.
        """
        deadline = time.time() + float(timeout)
        last_error: Optional[Exception] = None

        while time.time() < deadline:
            try:
                root = screen_reader.dump_ui(pause_video=pause_video)
                cx, cy = self.resolve_center(
                    root,
                    exact_text=match_spec.get("exact_text"),          # type: ignore[arg-type]
                    regex_pattern=match_spec.get("regex_pattern"),    # type: ignore[arg-type]
                    text_contains=match_spec.get("text_contains"),    # type: ignore[arg-type]
                    resource_id=match_spec.get("resource_id"),        # type: ignore[arg-type]
                    prefer_clickable=bool(match_spec.get("prefer_clickable", True)),
                    max_depth=int(match_spec.get("max_depth", MAX_PARENT_CLIMB_DEPTH)),  # type: ignore[arg-type]
                )
                screen_reader.run_adb("shell", "input", "tap", str(cx), str(cy))
                return (cx, cy)
            except AnchorNotFoundError as exc:
                last_error = exc
            except Exception as exc:  # ScreenReadError 등
                last_error = exc

            time.sleep(float(retry_interval))

        raise AnchorNotFoundError(
            f"tap_by_anchor 실패: {timeout}s 내 앵커 {match_spec} 를 찾지 못했습니다. (마지막 오류: {last_error})"
        )

    # ──────────────────────────────────────────────────────────────────────
    # 디버그 유틸
    # ──────────────────────────────────────────────────────────────────────
    @staticmethod
    def _describe(node: ET.Element) -> str:
        t = (node.get("text") or "").strip()
        d = (node.get("content-desc") or "").strip()
        b = node.get("bounds") or ""
        return f"text='{t}' desc='{d}' bounds={b}"


# ──────────────────────────────────────────────────────────────────────────────
# 단독 실행 스모크 테스트 (실기기 + 오프라인 검증)
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    from screen_reader import ScreenReader, ScreenReadError

    print("[SMOKE] SemanticResolver 스모크 테스트 시작")
    resolver = SemanticResolver()

    # ── 오프라인 단위 검증: 오탐 차단 regex ──
    fake_xml = """<hierarchy>
      <node text="이 게시물을 볼 수 있는 사람" bounds="[40,300][1040,400]" clickable="true" enabled="true"/>
      <node text="게시" bounds="[900,2100][1060,2200]" clickable="true" enabled="true"/>
      <node text="게시하기" bounds="[0,0][0,0]" clickable="true" enabled="true"/>
    </hierarchy>"""
    fake_root = ET.fromstring(fake_xml)

    node = resolver.find_node(fake_root, regex_pattern=r"^(게시|게시하기|Post|Publish)$")
    print(f"[SMOKE] regex 오탐차단 결과: {SemanticResolver._describe(node) if node is not None else 'None'}")
    assert node is not None and node.get("text") == "게시", "regex fullmatch 오탐 차단 실패"

    cx, cy = resolver.resolve_center(fake_root, regex_pattern=r"^(게시|게시하기|Post|Publish)$")
    print(f"[SMOKE] ✅ resolve_center 좌표: ({cx}, {cy})")
    assert (cx, cy) == (980, 2150), "좌표 계산 오류"

    # ── 하드코딩 폴백 금지 검증 ──
    try:
        resolver.resolve_center(fake_root, exact_text="존재하지않는앵커")
        print("[SMOKE] ❌ AnchorNotFoundError 미발생 (치명적)")
        sys.exit(1)
    except AnchorNotFoundError as exc:
        print(f"[SMOKE] ✅ AnchorNotFoundError 정상 발생: {str(exc)[:80]}")

    # ── 실기기 연동 검증 ──
    reader = ScreenReader()
    try:
        root = reader.dump_ui()
        nodes = list(root.iter("node"))
        print(f"[SMOKE] ✅ 실기기 dump 성공: node_count={len(nodes)}")
        try:
            cx, cy = resolver.resolve_center(root, text_contains="프로필")
            print(f"[SMOKE] ✅ 실기기 앵커 '프로필' 좌표: ({cx}, {cy})")
        except AnchorNotFoundError as exc:
            print(f"[SMOKE] ⚠️ 실기기 앵커 미발견(정상 동작): {str(exc)[:80]}")
    except ScreenReadError as exc:
        print(f"[SMOKE] ⚠️ 실기기 판독 불가(환경 의존): {exc}")

    print("[SMOKE] ✅ 전체 스모크 테스트 통과")
