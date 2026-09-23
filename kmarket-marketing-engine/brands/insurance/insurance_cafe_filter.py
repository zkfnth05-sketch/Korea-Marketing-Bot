# -*- coding: utf-8 -*-
"""
[보험 리밸런스] 네이버 카페 전용 지식iN 헌터급 완벽 파이썬 필터 (Lego Block)
================================================================================
- 브랜드: 🛡️ 보험 리밸런스 (34개 국내보험사 실시간 전수비교)
- 원칙: "파이썬으로 완벽 구축. 제미나이는 답글만 쓰게"
  1. 제목(Title)과 본문(Content) 전수 정밀 심사
  2. 지식iN 헌터 규격 7대 카테고리 화이트리스트 & 6대 카테고리 블랙리스트 전면 탑재
  3. 설계사 구인/노골적 GA 영업글, 금융 잡글, 일상 스팸 100% 원천 차단
  4. 보험 핵심 앵커 키워드 필수 검증 + 제목 가산점 + 본문 충실도 평가 (0~100점)
"""

import re
import sys
import logging
from typing import Tuple, List, Dict, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("InsuranceCafeFilter")

# 🟢 1. 화이트리스트 (7대 카테고리 정밀 가중치 사전)
INSURANCE_CAFE_WHITELIST: Dict[str, int] = {
    # [1. 핵심 보험 / 리모델링 / 증권분석 용어 (+20점)]
    "보험": 20, "보험료": 20, "보험금": 20, "보험사": 18, "실손보험": 20, "실비보험": 20,
    "보험리모델링": 20, "증권분석": 20, "보험고민": 20, "보험다이어트": 20,
    
    # [2. 주요 보장 상품군 (+18점)]
    "실손": 18, "실비": 18, "암보험": 18, "종신보험": 18, "건강보험": 18,
    "정기보험": 15, "치아보험": 15, "간병보험": 18, "치매보험": 18, "유병자보험": 18,
    "어린이보험": 15, "태아보험": 15, "생명보험": 15, "손해보험": 15, "운전자보험": 15,
    
    # [3. 행위 / 절차 / 현실 고충 (+18점)]
    "해지": 18, "리모델링": 18, "중복가입": 18, "갱신": 18, "비갱신": 18,
    "실손전환": 18, "갈아타기": 18, "납입": 15, "고정지출": 15, "과다청구": 15,
    "보험료부담": 18, "보험해지": 18, "환급금": 15, "해약환급금": 15,
    
    # [4. 핵심 특약 및 수술 / 진단 담보 (+15점)]
    "특약": 15, "불필요한특약": 18, "진단비": 15, "수술비": 15, "입원일당": 15,
    "뇌혈관": 15, "허혈성": 15, "심혈관": 15, "표적항암": 15, "질병수술비": 15,
    "상해수술비": 15, "보장내역": 15, "보장분석": 18,
    
    # [5. 보험 계약 구조 / 설계 용어 (+12점)]
    "납입기간": 12, "순수보장형": 12, "만기환급형": 12, "적립보험료": 15,
    "20년납": 12, "100세만기": 12, "자기부담금": 12, "면책기간": 12,
    "감액기간": 12, "부담보": 12, "고지의무": 12, "가입설계서": 12,
    
    # [6. 가입 채널 및 전수비교 (+12점)]
    "다이렉트": 12, "보험비교": 15, "비교사이트": 15, "전수비교": 18,
    "국내보험사": 15, "보험대리점": 10, "설계사": 10,
    
    # [7. 절약 / 비용 체감 (+12점)]
    "보험료절약": 15, "쓸데없는특약": 15, "중복보장": 15, "보험료줄이기": 15, "눈먼돈": 12
}

# 🔴 2. 블랙리스트 (지식iN 헌터급 6대 차단 카테고리)
INSURANCE_CAFE_BLACKLIST: List[str] = [
    # 🚫 [1. 설계사 구인 / 노골적 GA 영업 / DB 수집 스팸 100% 차단]
    "설계사모집", "입사문의", "팀원모집", "ga모집", "무료상담신청", "db모집",
    "사은품증정", "경품이벤트", "상담신청링크", "카톡상담링크", "명함첨부",
    "설문조사참여", "스타벅스기프티콘", "선착순이벤트", "영업사원모집", "위촉계약",
    
    # 📱 [2. 통신 / 요금제 / 인터넷 / 알뜰폰 / OTT 구독 차단]
    "인터넷가입", "알뜰폰", "통신사", "요금제", "넷플릭스", "유튜브", "멤버십", "구독", "헬스장",
    "스마트폰개통", "약정할인", "공시지원금", "자급제",
    
    # 💳 [3. 은행 예적금 / 간편결제 / 대출 / 카드 차단]
    "펌뱅킹", "오픈뱅킹", "인터넷뱅킹", "계좌이체", "타행이체", "무통장입금", "자동이체등록",
    "정기예금", "예금", "적금", "마이너스통장", "통장개설", "신한뱅킹", "국민뱅킹", "우리뱅킹",
    "신용카드한도", "체크카드발급", "카드결제일", "리볼빙", "카드론", "현금서비스",
    "토스송금", "카카오페이머니", "네이버페이포인트", "간편결제", "신용대출", "주담대",
    
    # 🏠 [4. 세무 / 부동산 / 청약 / 주식 / 코인 차단]
    "연말정산", "종합소득세", "주식", "코인", "비트코인", "부동산", "청약", "아파트", "전세", "월세",
    
    # 🎓 [5. 취업 / 진로 / 학업 / 자격증 차단]
    "취업", "진로", "공기업", "공무원", "수능", "편입", "군대", "알바", "아르바이트", "자격증",
    
    # 💄 [6. 뷰티 / 성형 / 명품 / 쇼핑 / 일상 잡글 차단]
    "피부과", "성형", "맛집", "여행", "다이어트약", "다이어트한약", "체중감량", "식욕억제제", "화장품", "샤넬", "루이비통", "오픈런",
    "중고차", "당근마켓", "번개장터"
]

# 🎯 3. 필수 앵커 키워드 (제목이나 본문에 최소 1개 이상 필수 포함)
INSURANCE_CAFE_ANCHORS: List[str] = [
    "보험", "보험료", "보험금", "실손", "실비", "특약", "보장", "암보험", "운전자보험",
    "자동차보험", "종신보험", "치아보험", "태아보험", "증권", "증권분석", "리모델링",
    "갱신형", "비갱신", "해지", "순수보장형", "적립보험료", "과다청구"
]

PASS_THRESHOLD = 40  # 카페 글 기준 40점 이상 합격


class InsuranceCafeFilter:
    """🛡️ 보험 리밸런스 전용 지식iN 헌터급 파이썬 고도화 필터"""

    def __init__(self, pass_threshold: int = PASS_THRESHOLD):
        self.pass_threshold = pass_threshold
        self.whitelist = INSURANCE_CAFE_WHITELIST
        self.blacklist = INSURANCE_CAFE_BLACKLIST
        self.anchors = INSURANCE_CAFE_ANCHORS

    def evaluate_post(
        self,
        title: str,
        content: str = "",
        cafe_name: str = ""
    ) -> Tuple[int, bool, str, List[str], List[str]]:
        """
        제목(Title)과 본문(Content) 전수 정밀 심사
        :return: (score, is_passed, reason, matched_white, matched_black)
        """
        title = title or ""
        content = content or ""
        full_text = f"{title} {content}"
        text_lower = full_text.lower()
        title_lower = title.lower()

        # 1. 🚫 블랙리스트 즉시 탈락 (제목/본문 어디든 감지 시 0점 탈락)
        matched_black = [bl for bl in self.blacklist if bl.lower() in text_lower]
        if matched_black:
            return 0, False, f"블랙리스트 차단: {', '.join(matched_black[:3])}", [], matched_black

        # 2. 🎯 필수 앵커 키워드 검증 (제목이나 본문에 최소 1개 이상 필수)
        matched_anchors = [ac for ac in self.anchors if ac.lower() in text_lower]
        if not matched_anchors:
            return 0, False, "보험 리모델링/보장 핵심 앵커 키워드 부재", [], []

        # 3. ⚖️ 화이트리스트 가중치 점수 합산 (키워드당 최대 2회 가산)
        score = 0
        matched_white = []
        for kw, weight in self.whitelist.items():
            cnt = len(re.findall(re.escape(kw.lower()), text_lower))
            if cnt > 0:
                matched_white.append(kw)
                score += weight * min(cnt, 2)

        # 4. 📌 제목(Title) 앵커 키워드 포함 특별 가산점 (+15점)
        title_has_anchor = any(ac.lower() in title_lower for ac in self.anchors)
        if title_has_anchor:
            score += 15

        # 5. 📝 본문 충실도 가산점
        if len(content) >= 50:
            score += 5
        if len(content) >= 150:
            score += 5
        if len(content) >= 300:
            score += 5

        # 점수 100점 상한
        score = min(score, 100)
        is_passed = score >= self.pass_threshold
        reason = f"적합도 {score}점 (합격)" if is_passed else f"적합도 {score}점 (기준점 {self.pass_threshold}점 미달)"

        return score, is_passed, reason, matched_white, []
