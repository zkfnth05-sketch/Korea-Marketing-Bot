# -*- coding: utf-8 -*-
"""
AuraDebateBooster - 💖 [Aura 데이팅 전용 댓글창 찬반 논쟁 유발 고정 댓글 엔진]
================================================================================
• 앱별 완전 독립 레고 블록 원칙 준수 (brands/aura/ 전담)
• 8대 킬러 주제별 2030 심리 저격 찬반 논쟁 질문 및 5대 SNS 고정 댓글 생성
• 시청 지속 시간(AVD 150%~200% 루프) 및 댓글 인게이지먼트 극대화
• 공식 검색어: '아우라AI데이팅' (붙여쓰기 필수)
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("AuraDebateBooster")

AURA_8_DEBATES: Dict[int, str] = {
    1: "소개팅 자리에서 가짜 업무 전화로 탈출하는 것, 센스다 vs 예의없다?",
    2: "언어 안 통해도 AI 자막 통화로 외국인 연애 가능? 가능하다 vs 무리다",
    3: "소개팅 앱 남녀 성비 50:50 안 맞으면 입장 제한하는 정원제, 찬성 vs 반대?",
    4: "소개팅 프로필 사진 AI 스튜디오 화보 보정, 자기관리다 vs 사진 사기다?",
    5: "연애할 때 연락 빈도 & 데이트 비용 가치관, 얼굴보다 중요하다 vs 얼굴이 먼저다?",
    6: "소개팅 앱 첫마디 AI 추천 멘트 사용하는 것, 스마트하다 vs 진정성 없다?",
    7: "AI가 분석해주는 내 매력상 & 얼굴형 진단, 신뢰한다 vs 재미로만 본다?",
    8: "동네 친구 만날 때 500m 위치 랜덤 안심 보안, 필수다 vs 굳이?"
}


class AuraDebateBooster:
    """💖 Aura AI 데이팅 전용 찬반 논쟁 고정 댓글 생성기"""

    OFFICIAL_KEYWORD = "아우라AI데이팅"
    OFFICIAL_URL = "https://aura-ai-dating.vercel.app/"

    @classmethod
    def get_debate_question(cls, topic_id: int = 1, custom_question: Optional[str] = None) -> str:
        """Aura 주제별 찬반 논쟁 질문 반환"""
        if custom_question and len(custom_question.strip()) > 5:
            return custom_question.strip()
        norm_id = ((topic_id - 1) % len(AURA_8_DEBATES)) + 1
        return AURA_8_DEBATES.get(norm_id, "여러분의 연애 가치관은? 찬성 vs 반대")

    @classmethod
    def generate_pinned_comments(
        cls,
        topic_id: int = 1,
        custom_question: Optional[str] = None
    ) -> Dict[str, str]:
        """Aura 5대 SNS 플랫폼 전용 찬반 논쟁 고정 댓글 패키지 생성"""
        norm_id = ((topic_id - 1) % len(AURA_8_DEBATES)) + 1
        question = cls.get_debate_question(norm_id, custom_question)

        yt_pinned = (
            f"💬 [긴급 찬반 투표] {question}\n"
            f"👉 1번 찬성 (이유는?) vs 2번 반대 (이유는?)\n"
            f"여러분의 솔직한 생각을 댓글로 남겨주세요! 👇\n\n"
            f"✨ 현재 100% 무료! 네이버에 네이버에 '{cls.OFFICIAL_KEYWORD}' 검색!"
        )

        reels_comment = (
            f"여러분의 선택은? 💬 {question}\n"
            f"댓글로 1번 vs 2번 남겨주세요! 👇\n"
            f"🔗 프로필 링크(@aura_official)에서 무료 확인 가능!"
        )

        tiktok_comment = (
            f"💬 {question}\n"
            f"투표는 댓글로! 👇 (링크는 프로필 Bio 클릭)"
        )

        threads_comment = (
            f"다들 어떻게 생각하시나요? 🤔\n"
            f"{question}\n\n"
            f"솔직한 의견 댓글로 토론해봐요! 👇\n"
            f"👉 바로가기: {cls.OFFICIAL_URL}"
        )

        fb_comment = (
            f"💬 {question}\n"
            f"여러분의 의견을 댓글로 들려주세요! 👇\n"
            f"👉 네이버 검색 [{cls.OFFICIAL_KEYWORD}] 또는 바로가기: {cls.OFFICIAL_URL}"
        )

        return {
            "debate_question": question,
            "youtube_pinned": yt_pinned,
            "reels_comment": reels_comment,
            "tiktok_comment": tiktok_comment,
            "threads_comment": threads_comment,
            "facebook_comment": fb_comment,
            "official_keyword": cls.OFFICIAL_KEYWORD,
            "landing_url": cls.OFFICIAL_URL
        }
