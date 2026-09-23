# -*- coding: utf-8 -*-
"""
Insurance Kin Python Filter (🐍 InsureBalance 전용 지식iN 파이썬 고도화 질문 필터)
==================================================================================
- 브랜드: InsureBalance (보험 다이렉트 비교 & AI 리모델링)
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

logger = logging.getLogger("InsurancePythonFilter")

# 화이트리스트 (보험/보장/리모델링 관련 가중치 사전)
INSURANCE_WHITELIST: Dict[str, int] = {
    # 핵심 용어 (+15점)
    "보험": 15, "보험료": 15, "보험금": 15, "보험사": 15, "실손보험": 15, "실비보험": 15,
    # 상품군 (+12점)
    "실손": 12, "실비": 12, "종신": 12, "암보험": 12, "연금보험": 12, "치아보험": 12,
    "자동차보험": 12, "화재보험": 12, "생명보험": 12, "손해보험": 12, "태아보험": 12, "어린이보험": 12,
    # 행위/절차 (+10점)
    "해지": 10, "청구": 10, "갱신": 10, "비갱신": 10, "가입": 10,
    "비교": 10, "환급": 10, "환급금": 10, "납입": 10, "리모델링": 10, "증권분석": 10,
    # 개념/보장 (+8점)
    "면책": 8, "보장": 8, "특약": 8, "다이렉트": 8, "진단비": 8, "수술비": 8, "입원비": 8,
    "고지의무": 8, "부담보": 8, "적립보험료": 8, "자기부담금": 8,
}

# 블랙리스트 (통신/구독, 세무/부동산/투자, 취업/학업, 불법 등)
INSURANCE_BLACKLIST: List[str] = [
    # 통신 / 구독 / 일상 서비스
    "인터넷가입", "알뜰폰", "통신사", "요금제", "넷플릭스", "유튜브", "멤버십", "구독", "헬스장",
    # 세무 / 부동산 / 투자
    "연말정산", "종합소득세", "주식", "코인", "부동산", "청약", "아파트", "전세", "월세",
    # 은행 / 간편결제 / 전자금융 / 전산
    "펌뱅킹", "오픈뱅킹", "인터넷뱅킹", "계좌이체", "타행이체", "무통장입금", "자동이체등록",
    "정기예금", "예금", "적금", "마이너스통장", "입출금", "통장개설", "신한뱅킹", "국민뱅킹", "우리뱅킹", "하나뱅킹",
    "신용카드한도", "체크카드발급", "카드결제일", "리볼빙", "카드론", "현금서비스",
    "토스송금", "카카오페이머니", "네이버페이포인트", "간편결제", "페이코",
    # 진로 / 취업 / 학업
    "취업", "진로", "공기업", "공무원", "수능", "편입", "군대", "알바", "아르바이트",
    # 연애 / 성인 / 불법 사행성
    "연애", "소개팅", "조건만남", "대출", "사채", "도박", "토토", "사기", "보이스피싱",
]

# 보험 핵심 앵커 키워드 (단순 '해지', '가입', '환급' 등으로 인한 타 분야 오탐 원천 차단)
INSURANCE_CORE_ANCHORS: List[str] = [
    "보험", "실손", "실비", "특약", "보장", "암보험", "운전자보험",
    "자동차보험", "종신보험", "치아보험", "태아보험", "보험금", "보험료"
]

PASS_THRESHOLD = 50


class InsurancePythonFilter:
    """🛡️ InsureBalance 보험 질문 고도화 파이썬 필터"""

    def __init__(self, pass_threshold: int = PASS_THRESHOLD):
        self.pass_threshold = pass_threshold
        self.whitelist = INSURANCE_WHITELIST
        self.blacklist = INSURANCE_BLACKLIST
        self.anchors = INSURANCE_CORE_ANCHORS

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

        # 2단계: 보험 핵심 앵커 키워드 필수 검증 (단순 구독 해지/환급 등 오탐 원천 차단)
        has_anchor = any(anchor.lower() in text_lower for anchor in self.anchors)
        if not has_anchor:
            return 0, False, "보험 핵심 앵커 키워드 부재"

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
    pf = InsurancePythonFilter()
    test_cases = [
        ("4세대 실손보험 전환해야 할까요?", "지금 2세대 실비인데 보험료가 너무 많이 올라서 갱신 때마다 부담스럽습니다. 다이렉트로 비교해보려구요."),
        ("주식 코인 단타로 돈 벌어서 집 사고 싶습니다", "투자 추천 부탁드려요"),
        ("암보험 진단비 비갱신형 추천 및 특약 정리", "가족력이 있어서 암보험 수술비와 입원비 특약 넣고 월 보험료 줄이고 싶어요"),
        ("넷플릭스 멤버십 요금제 해지 방법", "유튜브 프리미엄이랑 넷플릭스 구독 취소하고 환급받고 싶어요"),
        ("알뜰폰 요금제 통신사 비교", "인터넷가입 사은품 많이 주는 곳 추천 부탁드립니다"),
        ("단순 문의", "안녕하세요"),
    ]
    for t, c in test_cases:
        s, p, r = pf.score_question(t, c)
        print(f"[{'합격' if p else '탈락'}] {s}점 | {t} ➔ {r}")
