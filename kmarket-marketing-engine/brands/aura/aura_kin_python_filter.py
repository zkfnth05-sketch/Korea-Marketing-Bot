# -*- coding: utf-8 -*-
"""
Aura Kin Python Filter (🐍 Aura 전용 지식iN 파이썬 고도화 질문 필터)
======================================================================
- 브랜드: Aura (2030 AI 데이팅 & 서울 핫플 매칭)
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

logger = logging.getLogger("AuraPythonFilter")

# 화이트리스트 (데이팅/소개팅/연애 관련 가중치 사전)
AURA_WHITELIST: Dict[str, int] = {
    # 핵심 용어 (+15점)
    "소개팅": 15, "연애": 15, "남자친구": 15, "여자친구": 15, "남친": 15, "여친": 15,
    "썸": 15, "이성": 15, "만남": 15,
    # 관계 상황 (+12점)
    "커플": 12, "고백": 12, "데이트": 12, "헤어짐": 12, "이별": 12,
    "짝사랑": 12, "첫만남": 12, "미팅": 12, "애프터": 12,
    # 방법/플랫폼 (+10점)
    "어플": 10, "앱": 10, "결혼": 10, "맞선": 10, "결정사": 10, "소개팅어플": 10, "데이팅앱": 10,
    # 감정/행동 (+8점)
    "호감": 8, "연락": 8, "카톡": 8, "설레": 8, "차였": 8, "거절": 8, "심리": 8,
    # 장소/코스 (+7점)
    "홍대": 7, "강남": 7, "성수": 7, "핫플": 7, "카페": 7, "맛집": 7, "데이트코스": 7,
}

# 블랙리스트 (성인/유흥/불법, 반려동물/중고, 가정/육아 갈등, 시험/군대/취업 등)
AURA_BLACKLIST: List[str] = [
    # 성인 / 유흥 / 불법
    "조건만남", "성매매", "스폰", "유흥", "업소", "출장마사지", "원나잇", "오피",
    "성인용품", "불륜", "상간녀", "상간남", "아청법", "고소", "소송", "경찰서", "경찰",
    # 반려동물 / 중고거래 / 취업
    "강아지", "고양이", "입양", "분양", "중고거래", "직거래", "당근", "번개장터",
    "면접", "취업스터디", "취업", "공무원", "시험", "수능", "의대", "군대", "아르바이트", "알바구함", "알바모집",
    # 직장 내 사회생활 / 비연애 인간관계
    "직장상사", "팀장님", "동기", "이직", "퇴사", "사내정치", "거래처", "업무스트레스",
    "동성친구", "절친", "친구사이", "손절", "왕따", "단짝", "친구랑싸움", "우정",
    # 뷰티 / 미용 / 다이어트
    "화장법", "쿨톤", "웜톤", "쌍수", "코수술", "다이어트식단", "피부과시술", "여드름",
    # 가정 / 육아 갈등
    "이혼", "양육비", "육아", "임신", "출산", "어린이집", "초등학교", "시어머니", "시댁",
    # 금융 / 투자 / 사행성
    "부동산", "주식", "코인", "세금", "법원", "대출", "사채", "도박", "토토",
]

PASS_THRESHOLD = 50

# 데이팅 핵심 앵커 키워드 (단순 '홍대', '카페', '맛집' 등으로 인한 오탐 원천 차단)
AURA_CORE_ANCHORS: List[str] = [
    "소개팅", "연애", "남친", "여친", "남자친구", "여자친구", "썸", "데이트", "고백", "짝사랑",
    "첫만남", "애프터", "데이팅", "이상형", "인연", "이성", "맞선", "결정사", "커플"
]


class AuraPythonFilter:
    """💖 Aura 데이팅 질문 고도화 파이썬 필터"""

    def __init__(self, pass_threshold: int = PASS_THRESHOLD):
        self.pass_threshold = pass_threshold
        self.whitelist = AURA_WHITELIST
        self.blacklist = AURA_BLACKLIST
        self.anchors = AURA_CORE_ANCHORS

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

        # 2단계: 데이팅 핵심 앵커 키워드 필수 검증 (단순 맛집/카페 오탐 원천 차단)
        has_anchor = any(anchor.lower() in text_lower for anchor in self.anchors)
        if not has_anchor:
            return 0, False, "데이팅 핵심 앵커 키워드 부재"

        # 2단계: 화이트리스트 가중치 점수 합산
        score = 0
        matched = []
        for kw, weight in self.whitelist.items():
            count = text_lower.count(kw.lower())
            if count > 0:
                score += weight * min(count, 2)
                matched.append(f"{kw}(+{weight * min(count, 2)})")

        # 3단계: 제목에 화이트리스트 키워드가 있으면 가산점 (+10점)
        title_bonus = False
        title_lower = title.lower()
        for kw in self.whitelist:
            if kw.lower() in title_lower:
                score += 10
                title_bonus = True
                break

        # 4단계: 본문 길이 가산점 (성의 있는 질문)
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
    pf = AuraPythonFilter()
    test_cases = [
        ("소개팅 어플 추천좀 해주세요", "20대 후반 직장인인데 알바 없고 진지한 만남 가능한 곳 있을까요? 홍대나 성수 쪽에서 데이트하고 싶습니다."),
        ("조건만남 하실 분 구합니다", "지역 상관없이 쪽지 주세요"),
        ("강아지 첫만남 간식 추천", "유기견 분양 받은 강아지와 첫만남 어떻게 대처해야 할까요?"),
        ("남편과 이혼 소송 및 양육비 청구", "시어머니 갈등으로 이혼하기로 했습니다."),
        ("썸녀 카톡 연락 텀과 애프터 신청 타이밍", "첫만남 이후 카톡 분위기는 좋은데 이번 주말 데이트 신청 언제가 좋을까요?"),
        ("단순 일기", "오늘 날씨가 참 좋네요"),
    ]
    for t, c in test_cases:
        s, p, r = pf.score_question(t, c)
        print(f"[{'합격' if p else '탈락'}] {s}점 | {t} ➔ {r}")
