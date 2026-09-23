# -*- coding: utf-8 -*-
"""
Stock Kin Python Filter (🐍 Stock Master 전용 지식iN 파이썬 고도화 질문 필터)
==============================================================================
- 브랜드: Stock Master (2030 AI 주식 퀀트 & 종목 진단)
- 목적: Gemini API 낭비(evaluate_relevance)를 100% 방지하고 로컬 파이썬에서 즉각(0ms) 채점
- 로직:
  1. 🚫 블랙리스트 즉시 탈락 (0점, False)
  2. 🎯 화이트리스트 가중치 합산 (키워드당 최대 2회 가산)
  3. 📌 제목 키워드 가산점 (+10점)
  4. 📝 본문 충실도 가산점 (100자 이상 +5점, 300자 이상 +5점)
  5. ⚖️ 50점 이상 시 합격 (True)
"""

import re
import sys
import logging
from typing import Tuple, List, Dict

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("StockPythonFilter")

# 화이트리스트 (주식/투자 관련 가중치 사전)
STOCK_WHITELIST: Dict[str, int] = {
    # 핵심 주식/증권 용어 (+15점)
    "주식": 15, "주가": 15, "증권": 15, "코스피": 15, "코스닥": 15,
    # 투자 행동 (+12점)
    "매매": 12, "매수": 12, "매도": 12, "투자": 12, "장기투자": 12, "공매도": 12, "물타기": 12, "단타": 12, "스윙": 12,
    # 금융 상품 (+10점)
    "etf": 10, "펀드": 10, "공모주": 10, "배당": 10, "배당금": 10, "isa": 10, "국내주식": 10, "해외주식": 10,
    # 계좌/시스템 (+10점)
    "계좌": 10, "증권사": 10, "mts": 10, "hts": 10, "예수금": 10,
    # 분석 지표 (+8점)
    "per": 8, "pbr": 8, "roe": 8, "이동평균": 8, "골든크로스": 8,
    "수급": 8, "외국인": 8, "기관": 8, "시가총액": 8, "실적": 8, "영업이익": 8,
    "차트": 8, "지지선": 8, "저항선": 8, "거래량": 8, "테마주": 8, "대장주": 8,
    # 주요 대표 종목명 (+10점)
    "삼성전자": 10, "하이닉스": 10, "sk하이닉스": 10, "현대차": 10, "카카오": 10,
    "네이버": 10, "셀트리온": 10, "lg에너지솔루션": 10, "포스코": 10, "에코프로": 10,
    "엘앤에프": 10, "알테오젠": 10, "한미반도체": 10, "엔켐": 10,
    # 시황/글로벌 (+7점)
    "나스닥": 7, "환율": 7, "금리": 7, "미국 증시": 7, "s&p": 7, "다우": 7,
}

# 블랙리스트 (주식과 무관한 부동산, 중고거래, 게임, 가상화폐, 직업, 수능, 취업, 불법 스팸 등)
STOCK_BLACKLIST: List[str] = [
    # 부동산 / 주거
    "부동산", "아파트", "청약", "빌라", "오피스텔", "원룸", "투룸", "전세", "월세", "보증금", "임대차", "lh", "sh", "주택청약",
    # 중고거래 / 게임
    "중고차", "중고거래", "당근", "당근마켓", "번개장터", "게임", "아이템", "계정거래", "메이플", "로아", "피파", "롤",
    # 가상화폐 / 사행성 / 불법
    "비트코인", "이더리움", "가상화폐", "코인", "해외선물", "선물거래", "fx마진", "바카라", "토토", "사채", "대출", "불법도박", "개인회생", "파산", "불법리딩방", "보이스피싱",
    # 예적금 / 정부지원통장 / 단순 환전 / 개인간 금융
    "청년도약계좌", "청년희망적금", "군적금", "장병내일준비적금", "내일배움카드",
    "환전수수료", "외화통장", "엔화환전", "달러환전", "여행자수표",
    "정기예금", "정기적금", "파킹통장", "차용증", "빌려준돈",
    # 진로 / 취업 / 자격증 / 학업
    "취업", "진로", "공기업", "공무원", "수능", "편입", "군대", "알바", "아르바이트",
    "노무사", "공인중개사", "사회복지사", "임용", "사법시험", "요리사", "조리", "영양사", "치위생", "물리치료",
    "간호사", "간호학", "의대", "약대", "미용사", "미용", "자격증", "숙제", "과제",
]

# 주식 핵심 앵커 키워드 (단순 '매매', '투자' 오탐 방지를 위해 아래 키워드 중 최소 1개 필수 포함)
STOCK_CORE_ANCHORS: List[str] = [
    "주식", "주가", "코스피", "코스닥", "증권", "etf", "상장", "배당", "공모주", "종목",
    "isa", "hts", "mts", "예수금", "공매도", "장기투자", "단타", "스윙", "외국인수급", "기관수급",
    "삼성전자", "하이닉스", "sk하이닉스", "현대차", "카카오",
    "네이버", "셀트리온", "에코프로", "포스코", "lg에너지솔루션", "엘앤에프", "알테오젠", "한미반도체", "나스닥", "미국주식", "s&p", "증시"
]

PASS_THRESHOLD = 50


class StockPythonFilter:
    """📈 Stock Master 질문 고도화 파이썬 필터"""

    def __init__(self, pass_threshold: int = PASS_THRESHOLD):
        self.pass_threshold = pass_threshold
        self.whitelist = STOCK_WHITELIST
        self.blacklist = STOCK_BLACKLIST
        self.anchors = STOCK_CORE_ANCHORS

    def score_question(self, title: str, content: str = "") -> Tuple[int, bool, str]:
        """
        질문 제목과 본문을 분석하여 0~100점 점수 및 합격 여부 반환
        반환: (score: int, is_passed: bool, reason: str)
        """
        title = title or ""
        content = content or ""
        text = f"{title} {content}"
        text_lower = text.lower()

        # 1단계: 블랙리스트 즉시 탈락
        for bl in self.blacklist:
            if bl.lower() in text_lower:
                return 0, False, f"블랙리스트 차단: '{bl}'"

        # 2단계: 주식 핵심 앵커 키워드 필수 검증 (단순 '매매', '투자'로 인한 오탐 원천 차단)
        has_anchor = any(anchor.lower() in text_lower for anchor in self.anchors)
        if not has_anchor:
            return 0, False, "주식 핵심 앵커 키워드 부재"

        # 3단계: 화이트리스트 가중치 점수 합산
        score = 0
        matched = []
        for kw, weight in self.whitelist.items():
            count = text_lower.count(kw.lower())
            if count > 0:
                score += weight * min(count, 2)
                matched.append(f"{kw}(+{weight * min(count, 2)})")

        # 4단계: 제목에 화이트리스트 키워드가 있으면 가산점 (+10점)
        title_bonus = False
        title_lower = title.lower()
        for kw in self.whitelist:
            if kw.lower() in title_lower:
                score += 10
                title_bonus = True
                break

        # 5단계: 본문 길이 가산점 (성의 있는 질문)
        content_len = len(content.strip())
        if content_len > 100:
            score += 5
        if content_len > 300:
            score += 5

        # 100점 상한 제한
        score = min(score, 100)
        is_passed = score >= self.pass_threshold

        reason_parts = []
        if matched:
            reason_parts.append(f"매칭: {', '.join(matched[:5])}")
        if title_bonus:
            reason_parts.append("제목 가산점(+10)")
        if content_len > 100:
            reason_parts.append(f"본문 길이({content_len}자)")

        reason = " | ".join(reason_parts) if reason_parts else "키워드 매칭 없음"
        return score, is_passed, reason


if __name__ == "__main__":
    pf = StockPythonFilter()
    test_cases = [
        ("삼성전자 주가 전망 매수해도 될까요?", "지금 7만원대인데 장기투자로 분할매수 어떻게 해야 할지 궁금합니다."),
        ("미용과 졸업 후 취업 진로 상담 부탁드립니다", "미용사 자격증 따고 취업하려는데 조언 부탁드려요"),
        ("강남 아파트 매매 타이밍 문의", "지금 아파트 매매 투자로 들어가는 게 맞을까요?"),
        ("메이플 계정 매매합니다", "매매 관심 있으신 분 연락주세요."),
        ("코스피 배당주 추천 및 ISA 계좌 활용법", "초보 주린이인데 배당 높은 주식 ETF 모아가고 싶습니다."),
        ("단순 질문입니다", "안녕하세요 투자하고 싶어요"),
    ]
    for t, c in test_cases:
        s, p, r = pf.score_question(t, c)
        print(f"[{'합격' if p else '탈락'}] {s}점 | {t} ➔ {r}")
