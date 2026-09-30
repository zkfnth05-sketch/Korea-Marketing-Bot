# -*- coding: utf-8 -*-
"""
StockDebateBooster - 📈 [StockMaster AI 전용 댓글창 찬반 논쟁 유발 고정 댓글 엔진]
==================================================================================
• 앱별 완전 독립 레고 블록 원칙 준수 (brands/stock/ 전담)
• 주식 6대 주제별 실시간 투자 토론/찬반 투표 질문 및 5대 SNS 고정 댓글 생성
• 시청 지속 시간(AVD 150%~200% 루프) 및 댓글 인게이지먼트 극대화
• 공식 검색어: '스톡마스터 AI' (띄어쓰기 필수)
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("StockDebateBooster")

STOCK_6_DEBATES: Dict[int, str] = {
    1: "지금 반도체 대장주 매수한다면? 1번 삼성전자 vs 2번 SK하이닉스",
    2: "매달 배당 100만원 포트폴리오, 1번 배당성장 SCHD vs 2번 고배당 JEPQ",
    3: "주식 계좌 -5% 손실 터치 시, AI 원칙 손절한다 vs 반등 믿고 존버한다?",
    4: "당일 체결강도 150% 수급 1위 주도주 매매, 따라붙는다 vs 관망한다?",
    5: "코스피 현 시장 국면, 바닥 반등 랠리다 vs 추가 조정 하락장이다?",
    6: "주식 매매할 때 AI 퀀트 지표로 객관적 판단, 필수다 vs 내 직관과 차트가 낫다?"
}


class StockDebateBooster:
    """📈 StockMaster AI 전용 찬반 논쟁 고정 댓글 생성기"""

    OFFICIAL_KEYWORD = "스톡마스터 AI"
    OFFICIAL_URL = "https://stockmaster-ai.vercel.app/"

    @classmethod
    def get_debate_question(cls, topic_id: int = 1, custom_question: Optional[str] = None) -> str:
        """주식 주제별 찬반 논쟁 질문 반환"""
        if custom_question and len(custom_question.strip()) > 5:
            return custom_question.strip()
        norm_id = ((topic_id - 1) % len(STOCK_6_DEBATES)) + 1
        return STOCK_6_DEBATES.get(norm_id, "여러분의 투자 선택은? 1번 vs 2번")

    @classmethod
    def generate_pinned_comments(
        cls,
        topic_id: int = 1,
        custom_question: Optional[str] = None
    ) -> Dict[str, str]:
        """주식 5대 SNS 플랫폼 전용 찬반 논쟁 고정 댓글 패키지 생성"""
        norm_id = ((topic_id - 1) % len(STOCK_6_DEBATES)) + 1
        question = cls.get_debate_question(norm_id, custom_question)

        yt_pinned = (
            f"💬 [실시간 투자 토론] {question}\n"
            f"👉 1번 매수/찬성 vs 2번 관망/반대\n"
            f"여러분의 투자 판단을 댓글로 남겨주세요! 👇\n\n"
            f"✨ 10분 계량 전광판은 네이버에 '{cls.OFFICIAL_KEYWORD}' 검색!"
        )

        reels_comment = (
            f"여러분의 투자 선택은? 💬 {question}\n"
            f"댓글로 1번 vs 2번 남겨주세요! 👇\n"
            f"🔗 10분 계량 전광판은 네이버에 [{cls.OFFICIAL_KEYWORD}] 검색!"
        )

        tiktok_comment = (
            f"💬 {question}\n"
            f"투표는 댓글로! 👇 (링크는 프로필 Bio 클릭)"
        )

        fb_comment = (
            f"💬 {question}\n"
            f"여러분의 투자 의견을 댓글로 들려주세요! 👇\n"
            f"👉 네이버 검색 [{cls.OFFICIAL_KEYWORD}] 또는 바로가기: {cls.OFFICIAL_URL}"
        )

        naver_clip_comment = (
            f"💬 [투자 토론] {question}\n"
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
