# -*- coding: utf-8 -*-
"""
HookArchetypeRotator - 🎣 [7가지 훅 심리 아키타입 매일 자동 로테이션]
====================================================================
- 결론먼저 / 숫자팩트 / 반전대비 / 스토리텔링 / 권위뉴스 / 도발질문 / 긴급시한
- 날짜 + 브랜드 + 주제 기반 결정론적 로테이션 (같은 날 같은 주제 → 항상 같은 훅)
- 기존 코드 0% 훼손 — 독립 레고 블록
"""

import hashlib
from datetime import date
from typing import Dict, Any, List

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7가지 훅 아키타입 정의
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOOK_ARCHETYPES: Dict[str, Dict[str, Any]] = {

    "conclusion_first": {
        "name": "결론_먼저형",
        "structure": "첫 문장에 결론/핵심 수치 → 왜 그런지 → 해결책",
        "gemini_instruction": (
            "반드시 첫 문장(hook_p1)에서 결론이나 핵심 수치를 먼저 말해. "
            "'~하신 적 있으시죠?'같은 질문으로 시작하지 마. "
            "예: '보험료 10만원이면 5만원 버리는 겁니다' 처럼 결론부터 때려."
        ),
    },

    "number_fact": {
        "name": "숫자_팩트형",
        "structure": "구체적 %/금액 수치로 시작 → 문제 설명 → 해결책",
        "gemini_instruction": (
            "반드시 첫 문장(hook_p1)에 구체적인 숫자(%나 금액)를 넣어서 "
            "팩트로 시작해. 막연한 표현 금지. "
            "예: '직장인 67%가 보험료를 과납하고 있습니다' 처럼."
        ),
    },

    "contrast_reversal": {
        "name": "반전_대비형",
        "structure": "같은 조건인데 결과가 극과극인 A vs B 제시 → 왜 다른지 → 해결책",
        "gemini_instruction": (
            "같은 조건에서 결과가 극과극인 두 사례를 대비시켜서 시작해. "
            "예: '같은 보험인데 A는 월 12만원, B는 월 5만원입니다' 처럼."
        ),
    },

    "story": {
        "name": "스토리텔링형",
        "structure": "한 사람의 실제 경험 → 무슨 일이 일어났는지 → 해결책",
        "gemini_instruction": (
            "실제 있을 법한 한 사람의 짧은 스토리로 시작해. "
            "'저도 그랬는데' 라고 공감할 수 있게. "
            "예: '3년간 매달 20만원 넣던 직장인이 어느 날...' 처럼."
        ),
    },

    "authority_news": {
        "name": "권위_뉴스형",
        "structure": "공식 기관 발표/뉴스 → 나한테 왜 중요한지 → 해결책",
        "gemini_instruction": (
            "금감원, 한국은행, 통계청 등 공신력 있는 기관 발표나 "
            "뉴스 팩트로 시작해. 정확한 수치와 함께. "
            "예: '금감원 발표, 과잉보험 비율 67%' 처럼."
        ),
    },

    "provocative_question": {
        "name": "도발_질문형",
        "structure": "자존심이나 불안을 건드리는 질문 1줄 → 답변 → 해결책",
        "gemini_instruction": (
            "시청자의 자존심이나 불안을 건드리는 도발적 질문 한 줄로 시작하되, "
            "기존의 '~하신 적 있으시죠?'같은 부드러운 질문이 아니라 "
            "예: '지금 내는 보험료, 진짜 그 가치가 있을까요?' 처럼 찔러."
        ),
    },

    "urgency": {
        "name": "긴급_시한형",
        "structure": "지금 안 하면 손해 보는 시한 → 왜 급한지 → 해결책",
        "gemini_instruction": (
            "지금 바로 확인하거나 행동하지 않으면 손해 보는 시한이 있는 "
            "상황으로 시작해. 마감/인상/한정 등 긴급성을 강조. "
            "예: '7월 보험료 인상 전, 지금이 마지막 기회' 처럼."
        ),
    }
}

ARCHETYPE_KEYS: List[str] = list(HOOK_ARCHETYPES.keys())


class HookArchetypeRotator:
    """날짜 + 브랜드 + 주제 기반으로 7가지 훅 아키타입을 결정론적 로테이션

    사용법:
        archetype = HookArchetypeRotator.get_today_archetype("aura", 1)
        print(archetype["name"])  # → "결론_먼저형" (날짜에 따라 다름)
    """

    @classmethod
    def get_today_archetype(cls, brand: str, topic_id: int) -> Dict[str, Any]:
        """
        같은 날 + 같은 브랜드 + 같은 주제 → 항상 같은 훅 반환 (결정론적)
        다른 날 → 다른 훅 반환
        같은 날이라도 브랜드/주제가 다르면 → 다른 훅 반환

        Args:
            brand: "aura" | "insurance" | "stock"
            topic_id: 주제 번호 (1~8)

        Returns:
            {"key": "conclusion_first", "name": "결론_먼저형", "structure": ..., "gemini_instruction": ...}
        """
        seed = f"{date.today().isoformat()}_{brand}_{topic_id}"
        idx = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(ARCHETYPE_KEYS)
        key = ARCHETYPE_KEYS[idx]
        return {
            "key": key,
            **HOOK_ARCHETYPES[key]
        }

    @classmethod
    def get_all_archetypes(cls) -> Dict[str, Dict]:
        """전체 7가지 아키타입 반환 (디버깅/프리뷰용)"""
        return HOOK_ARCHETYPES

    @classmethod
    def preview_week(cls, brand: str, topic_id: int) -> List[Dict[str, str]]:
        """향후 7일간의 훅 로테이션 미리보기 (디버깅용)

        Returns:
            [{"date": "2026-09-29", "archetype": "결론_먼저형"}, ...]
        """
        from datetime import timedelta
        results = []
        today = date.today()
        for i in range(7):
            d = today + timedelta(days=i)
            seed = f"{d.isoformat()}_{brand}_{topic_id}"
            idx = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(ARCHETYPE_KEYS)
            key = ARCHETYPE_KEYS[idx]
            results.append({
                "date": d.isoformat(),
                "archetype": HOOK_ARCHETYPES[key]["name"]
            })
        return results
