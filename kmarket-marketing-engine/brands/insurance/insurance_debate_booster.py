# -*- coding: utf-8 -*-
"""
InsuranceDebateBooster - 🛡️ [보험 리밸런스 전용 댓글창 찬반 논쟁 유발 고정 댓글 엔진]
========================================================================================
• 앱별 완전 독립 레고 블록 원칙 준수 (brands/insurance/ 전담)
• 보험 8대 주제별 팩트 기반 찬반 논쟁 질문 및 5대 SNS 고정 댓글 생성
• 시청 지속 시간(AVD 150%~200% 루프) 및 댓글 인게이지먼트 극대화
• 공식 검색어: '보험 리밸런스' (띄어쓰기 필수)
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("InsuranceDebateBooster")

INSURANCE_8_DEBATES: Dict[int, str] = {
    1: "병원 1년에 한두 번 가는데, 4세대 실비로 갈아탄다 vs 옛날 1·2세대 유지한다?",
    2: "운전자보험은 월 1만 3천 원이면 충분하다 vs 비싸도 상해 특약 다 넣어야 한다?",
    3: "암보험 들 때 유사암(갑상선 등) 진단비 비율, 꼭 따져봐야 한다 vs 일반암만 많으면 된다?",
    4: "뇌출혈만 보장되는 옛날 보험, 뇌혈관질환 전체 보장으로 리밸런싱 해야 한다 vs 그냥 둔다?",
    5: "임플란트/크라운 치료 계획 없으면 치아보험 해지한다 vs 혹시 모르니 유지한다?",
    6: "약 먹고 있어도 335 간편 심사로 갈아타야 한다 vs 거절될까 봐 기존 것 유지한다?",
    7: "부모님 간병비 일당 15만원 간병인 보험, 필수다 vs 나중에 생각한다?",
    8: "보험 가입 전 33개사 무료 비교 자가진단, 필수 코스다 vs 아는 설계사한테 그냥 든다?"
}


class InsuranceDebateBooster:
    """🛡️ 보험 리밸런스 전용 찬반 논쟁 고정 댓글 생성기"""

    OFFICIAL_KEYWORD = "보험 리밸런스"
    OFFICIAL_URL = "https://insure-rebalance.vercel.app/"

    @classmethod
    def get_debate_question(cls, topic_id: int = 1, custom_question: Optional[str] = None) -> str:
        """보험 주제별 찬반 논쟁 질문 반환"""
        if custom_question and len(custom_question.strip()) > 5:
            return custom_question.strip()
        norm_id = ((topic_id - 1) % len(INSURANCE_8_DEBATES)) + 1
        return INSURANCE_8_DEBATES.get(norm_id, "내 보험 보장 범위는 안전할까? 리밸런싱 찬성 vs 유지")

    @classmethod
    def generate_pinned_comments(
        cls,
        topic_id: int = 1,
        custom_question: Optional[str] = None
    ) -> Dict[str, str]:
        """보험 5대 SNS 플랫폼 전용 찬반 논쟁 고정 댓글 패키지 생성"""
        norm_id = ((topic_id - 1) % len(INSURANCE_8_DEBATES)) + 1
        question = cls.get_debate_question(norm_id, custom_question)

        yt_pinned = (
            f"💬 [보험 팩트 논쟁] {question}\n"
            f"👉 1번 갈아탄다(찬성) vs 2번 유지한다(반대)\n"
            f"여러분의 선택과 경험을 댓글로 알려주세요! 👇\n\n"
            f"✨ 33개사 실시간 비교는 네이버에 '{cls.OFFICIAL_KEYWORD}' 검색!"
        )

        reels_comment = (
            f"여러분의 선택은? 💬 {question}\n"
            f"댓글로 1번 vs 2번 남겨주세요! 👇\n"
            f"🔗 33개사 비교는 네이버에 [{cls.OFFICIAL_KEYWORD}] 검색!"
        )

        tiktok_comment = (
            f"💬 {question}\n"
            f"투표는 댓글로! 👇 (링크는 프로필 Bio 클릭)"
        )

        fb_comment = (
            f"💬 {question}\n"
            f"여러분의 의견을 댓글로 들려주세요! 👇\n"
            f"👉 네이버 검색 [{cls.OFFICIAL_KEYWORD}] 또는 바로가기: {cls.OFFICIAL_URL}"
        )

        naver_clip_comment = (
            f"💬 [찬반 토론] {question}\n"
            f"네이버 검색창에 [{cls.OFFICIAL_KEYWORD}]를 검색해보세요."
        )

        return {
            "debate_question": question,
            "youtube_pinned": yt_pinned,
            "reels_comment": reels_comment,
            "tiktok_comment": tiktok_comment,
            "facebook_comment": fb_comment,
            "naver_clip_comment": naver_clip_comment,
            "official_keyword": cls.OFFICIAL_KEYWORD,
            "landing_url": cls.OFFICIAL_URL
        }
