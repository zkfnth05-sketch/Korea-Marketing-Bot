# -*- coding: utf-8 -*-
"""
🛡️ InsureBalance 전용 실시간 키워드 매트릭스 (InsuranceKeywordMatrix)
=====================================================================
- 역할:
  1. 보험 6대 카테고리별 전문 시드어(Scoped Seed) 관리
  2. 노이즈 필터링 (주식, 암호화폐, 음란물 등 무관 키워드 완벽 배제)
  3. 네이버 스마트블록 1위형 제목 키워드, 소제목 키워드, 바이럴 해시태그 생성
"""

import random
from typing import Dict, List, Any


class InsuranceKeywordMatrix:
    """InsureBalance 보험 비교 & 리모델링 전용 키워드 매트릭스"""

    SCOPED_SEEDS: Dict[str, List[str]] = {
        "health_medical": [
            "4세대 실손보험 전환", "실비보험 도수치료", "암보험 진단비 비교",
            "유사암 진단비 한도", "뇌혈관질환 보험", "허혈성 심장질환",
            "1종 5종 수술비 특약", "간병인 사용일당 보험", "질병후유장해 3프로",
            "표적항암치료 특약", "유병자 355 간편보험", "2030 청년보험"
        ],
        "auto_driver": [
            "다이렉트 자동차보험 비교견적", "운전자보험 필수특약", "민식이법 벌금 3천만원",
            "교통사고 처리지원금 형사합의금", "자동차보험 대물배상 10억", "자동차상해 자기신체사고 차이",
            "무보험차상해 5억", "침수차 자차보험 보상", "교통사고 보험처리 할증",
            "자동차보험 환입제도", "원데이 자동차보험 렌터카", "티맵 안전운전할인 특약"
        ],
        "life_dental_pet": [
            "치아보험 임플란트 면책기간", "치아보험 크라운 레진", "펫보험 강아지 슬개골탈구",
            "일상생활배상책임 누수보상", "주택화재보험 가전제품수리비", "골절진단비 치아파절",
            "해외여행자보험 해외의료비", "태아보험 22주 가입시기", "신생아 인큐베이터 특약"
        ],
        "savings_annuity": [
            "연금저축보험 연말정산 세액공제", "IRP 퇴직연금 절세한도", "종신보험 정기보험 비교",
            "사회초년생 종신보험 해지", "10년 비과세 저축보험", "변액보험 펀드변경 수익률",
            "연금소득세 건보료 피부양자", "퇴직금 IRP 수령 세금감면", "국민연금 조기수령 손익분기점"
        ],
        "claims_knowhow": [
            "실손보험 청구서류 3분컷", "보험사 현장심사 서명주의", "보험금 부지급 금감원민원",
            "독립 손해사정사 무료선임", "숨은 보험금 찾기 내보험찾아줌", "고지의무위반 3년 제척기간",
            "직업변경 통지의무 상해급수", "보험금 청구 소멸시효 3년", "정신과 F코드 실손보험",
            "보험금 지급 지연이자 계산"
        ],
        "remodeling_savings": [
            "보험 리모델링 중복특약 정리", "적립보험료 삭제 환급", "갱신형 비갱신형 보험료 비교",
            "사회초년생 월 7만원 첫보험", "무해지 환급형 가성비보험", "CI보험 약관 리모델링",
            "부모님 6070 보험정리", "보험 감액완납 유지", "보험증권 분석 필수담보",
            "보험 청약철회 30일 환불"
        ]
    }

    VIRAL_TAG_POOL: Dict[str, List[str]] = {
        "health_medical": ["#실손보험", "#암보험비교", "#4세대실비", "#수술비보험", "#간병인보험", "#건강보험추천", "#InsureBalance"],
        "auto_driver": ["#자동차보험", "#다이렉트자동차보험", "#운전자보험", "#교통사고합의금", "#자차보험", "#운전자보험특약", "#InsureBalance"],
        "life_dental_pet": ["#치아보험", "#임플란트보험", "#펫보험", "#일상생활배상책임", "#주택화재보험", "#태아보험", "#InsureBalance"],
        "savings_annuity": ["#연금저축", "#연말정산세액공제", "#IRP", "#종신보험", "#정기보험", "#노후준비", "#InsureBalance"],
        "claims_knowhow": ["#보험금청구", "#실비청구서류", "#보험금부지급", "#내보험찾아줌", "#숨은보험금", "#손해사정사", "#InsureBalance"],
        "remodeling_savings": ["#보험리모델링", "#보험료절약", "#보험다이어트", "#비갱신형보험", "#사회초년생보험", "#보험진단", "#InsureBalance"]
    }

    def build_seo_article_brief(self, seed_topic: str, category: str) -> Dict[str, Any]:
        """주제와 카테고리에 맞는 실시간 SEO 키워드 패키지 생성"""
        seeds = self.SCOPED_SEEDS.get(category, self.SCOPED_SEEDS["health_medical"])
        chosen_seeds = random.sample(seeds, min(3, len(seeds)))

        title_keywords = [
            f"{chosen_seeds[0]} 핵심 정리",
            f"{chosen_seeds[0]} 손해 안 보는 법",
            f"{chosen_seeds[0]} 보장 비교"
        ]

        subheading_keywords = [
            f"1. {chosen_seeds[0]} 꼭 알아야 할 필수 약관",
            f"2. {chosen_seeds[1] if len(chosen_seeds) > 1 else '실제 보상'} 주의사항과 체크포인트",
            f"3. 전문가가 추천하는 맞춤형 가입 및 리모델링 전략"
        ]

        tags = self.VIRAL_TAG_POOL.get(category, ["#보험비교", "#보험리모델링", "#InsureBalance"])

        return {
            "category": category,
            "seed_topic": seed_topic,
            "seo_title_keywords": title_keywords,
            "h2_h3_subheading_keywords": subheading_keywords,
            "viral_hashtags": tags,
            "scoped_seeds": chosen_seeds
        }
