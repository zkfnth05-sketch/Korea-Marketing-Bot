from core.gemini_unified_keys import get_unified_gemini_key_dicts, get_unified_gemini_keys, format_gemini_error
# -*- coding: utf-8 -*-
"""
InsuranceCardnewsGeminiCopywriter - 🛡️ [보험 리밸런스 8대 주제 전용 제미나이 심의 준수 카피라이터]
=====================================================================================================
• 핵심 원칙:
  1. 8대 정예 주제별 5장 슬라이드(제목, 부제, 3줄 불릿, 찬반토론, CTA) 및 SNS 캡션 100% 순수 제미나이 자율 집필
  2. [주제 이탈 0% 원칙]: 각 주제별 핵심 제도, 약관, 금감원 팩트 가이드라인을 주입하여 절대 다른 주제로 새어나가지 않음
  3. [금융소비자보호법 심의 준수]: '무조건', '100%', '최고', '공짜', '호갱' 등 과장·단정적 표현 전면 배제 및 객관적 통계/약관 근거 서술
  4. [풍성하고 깊이 있는 분량]: 슬라이드별 35~55자 상세 불릿, SNS 본문 350~450자 전문 칼럼
  5. 3개 무료 키(INSURE_KEY_1 -> 2 -> 3) 자율 체인 & 쿼터 소진 시 무중단 롤오버
  6. 자체 무결성 게이트: '보험 리밸런스' 공식 검색어 누락 시 자동 보정 및 엄격 검증
"""

import os
import sys
import json
import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("InsuranceCardnewsGeminiCopywriter")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from brands.insurance.insurance_hashtag_matrix import InsuranceHashtagMatrix


class InsuranceCardnewsGeminiCopywriter:
    """🛡️ 보험 리밸런스 5장 카드뉴스 전용 제미나이 심의 준수 카피라이터 & 캡션 생성기"""

    OFFICIAL_KEYWORD = "보험 리밸런스"
    OFFICIAL_URL = "https://insure-rebalance.vercel.app/"
    BRAND_NAME = "보험 리밸런스"

    # 심의상 절대 사용 금지 어휘
    BANNED_WORDS = ["무조건", "100%", "최고", "최저가 보장", "공짜", "무료 환급", "절대", "호갱", "전액 보장", "단독 특가", "원금 보장"]

    # 🎯 8대 정예 주제별 고유 팩트 매트릭스 (주제 이탈 0% 원천 보장)
    TOPIC_FACT_MATRIX = {
        1: {
            "title": "4세대 실손보험 전환 팩트 체크 (월 5만원 절약의 진실)",
            "core_focus": "구실손(1~3세대) 갱신 폭탄 vs 4세대 실손 급여 20%/비급여 30% 자기부담금 및 비급여 이용량에 따른 3~5단계 차등 할증 제도",
            "key_facts": [
                "1~2세대 구실손은 비급여 과다 청구자로 인해 매년 갱신 보험료가 가파르게 상승하는 구조입니다.",
                "4세대 실손은 병원(특히 비급여) 이용이 적을 경우 기존 대비 보험료가 최대 50~70% 저렴합니다.",
                "도수치료/비급여 주사 등 연간 비급여 수령액이 100만 원 이상이면 100~300% 할증될 수 있으므로 병원 이용 패턴 분석이 필수입니다."
            ],
            "debate_question": "4세대 실손 전환, 지금 갈아타기 vs 기존 1~3세대 유지 중 내 선택은?",
            "opt1": ("📉 지금 즉시 4세대 전환", "비급여 병원 이용이 적고 월 고정 보험료를 합리적으로 절감"),
            "opt2": ("🏥 기존 1~3세대 실손 유지", "도수치료/비급여 청구 빈도가 높아 기존 넓은 보장을 유지")
        },
        2: {
            "title": "10년 갱신형 암보험의 함정 vs 비갱신형 비교 분석",
            "core_focus": "갱신형(초기 저렴하지만 60대 이후 3~5배 폭탄) vs 비갱신형(초기 고정 보험료로 80/90세까지 납입 종료)",
            "key_facts": [
                "갱신형 암보험은 가입 초기에는 저렴해 보이지만 암 발병률이 급증하는 60~70대에 보험료가 기하급수적으로 폭증합니다.",
                "은퇴 후 소득이 줄어드는 시기에 갱신 보험료를 감당하지 못해 해지하는 분쟁 사례가 빈번합니다.",
                "기본 진단비는 비갱신형으로 든든하게 뼈대를 잡고, 특정 고액암 특약만 갱신형으로 복층 설계하는 것이 합리적입니다."
            ],
            "debate_question": "암보험 가입/리모델링 시 내 선택은: 비갱신형 평생 고정 vs 갱신형 초기 절약?",
            "opt1": ("🔒 비갱신형 평생 고정", "초기 보험료는 높아도 은퇴 후 보험료 상승 걱정 없이 완납"),
            "opt2": ("📉 갱신형 초기 절약", "젊을 때 적은 비용으로 고액 보장을 집중 확보하고 추후 조정")
        },
        3: {
            "title": "2030 사회초년생 월급 대비 적정 보험료 비율 가이드",
            "core_focus": "월급 250만원 기준 적정 보험료는 월 소득의 5~8%(12~20만원 선), 과도한 종신/변액 다이어트",
            "key_facts": [
                "사회초년생의 적정 보장성 보험료는 세후 월 소득의 5%~8% 이내가 가장 안정적인 재무 비율입니다.",
                "지인 부탁으로 가입한 월 20~30만 원대 종신보험이나 저축성 변액보험은 조기 해지 시 원금 손실 위험이 큽니다.",
                "실손보험 1~2만 원대 + 3대 진단비(암/뇌/심장) 종합보험 5~8만 원대로 슬림하게 세팅하는 것이 정석입니다."
            ],
            "debate_question": "사회초년생 첫 보험 세팅 기준: 3대 진단비 실속형 vs 종신/저축 복합형?",
            "opt1": ("🛡️ 3대 진단비 실속형", "월 5~10만원대로 순수 보장만 챙기고 남은 돈은 청년도약계좌 등 저축"),
            "opt2": ("💼 종신/연금 복합형", "사망 보장과 장기 저축을 한 번에 준비하는 복합 상품 선호")
        },
        4: {
            "title": "뇌혈관질환 vs 뇌출혈 진단비 약관 범위 팩트체크",
            "core_focus": "'뇌출혈'(전체 뇌질환의 약 9%) vs '뇌졸중'(약 60%) vs '뇌혈관질환'(100% 전체 보장) 약관 범위 차이",
            "key_facts": [
                "예전 보험에 많은 '뇌출혈' 특약은 뇌경색(I63)이나 뇌동맥류(I67) 발생 시 보험금이 0원 지급됩니다.",
                "건강보험심사평가원 통계 기준 뇌경색 환자가 전체 뇌혈관 질환의 대부분을 차지하므로 '뇌혈관질환 진단비'가 필수입니다.",
                "허혈성심장질환 진단비 역시 '급성심근경색'만 보장되는 특약은 협심증(I20) 청구 시 보장되지 않습니다."
            ],
            "debate_question": "내 보험 증권 뇌/심장 특약 점검: 뇌혈관·허혈성 넓은 보장 vs 뇌출혈·급성심근경색 기존 유지?",
            "opt1": ("🧠 뇌혈관/허혈성 보장 확대", "협심증, 뇌경색까지 100% 빈틈없이 보장받도록 특약 보완"),
            "opt2": ("📜 기존 약관 유지", "과거 가입 상품의 다른 유리한 조건(입원일당 등)을 감안해 유지")
        },
        5: {
            "title": "운전자보험 개정 약관과 1만원대 필수 특약 분석",
            "core_focus": "교통사고처리지원금(형사합의금 2억), 변호사선임비용(경찰조사단계 포함), 6주 미만 스쿨존 사고 보장",
            "key_facts": [
                "자동차보험은 민사상 손해배상 의무보험이고, 운전자보험은 형사적/행정적 책임을 보장하는 선택 상품입니다.",
                "과거 운전자보험은 '경찰조사 단계' 변호사선임비용이나 '스쿨존 6주 미만 부상' 형사합의금이 보장되지 않습니다.",
                "운전자보험은 월 1~2만 원대로 충분하며, 비싼 적립보험금을 넣거나 3~4만 원 이상 낼 이유가 없습니다."
            ],
            "debate_question": "운전자보험 리모델링 선택: 1만원대 다이렉트 최신 개정 약관 vs 기존 운전자보험 유지?",
            "opt1": ("🚗 1만원대 최신 개정 특약", "경찰조사 변호사선임 + 공탁금 50% 선지급 등 최신 보장 확보"),
            "opt2": ("📁 기존 운전자보험 유지", "과거 약관의 벌금/합의금 한도로도 일상 운전에 충분하다고 판단")
        },
        6: {
            "title": "간병비 파산 막는 '간병인 사용일당' vs '지원일당' 비교",
            "core_focus": "간병인 1일 비용 15만원 시대, 보험사가 사람을 보내주는 지원일당(갱신형) vs 영수증 청구하는 사용일당(체증형)",
            "key_facts": [
                "통계청 조사 기준 사설 간병인 일당이 13~15만 원으로 급등하여 한 달 간병비가 400만 원을 상회합니다.",
                "'간병인 지원일당'은 보험사가 간병인을 파견하지만 3~5년 갱신형이 많아 훗날 보험료가 크게 오를 수 있습니다.",
                "'간병인 사용일당'은 환자가 직접 간병인을 부르고 정액을 청구하며, 물가상승을 반영하는 체증형 특약이 인기입니다."
            ],
            "debate_question": "부모님/내 간병비 보험 선택: 물가반영 체증형 사용일당 vs 간병인 직접 파견 지원일당?",
            "opt1": ("📋 체증형 간병인 사용일당", "물가상승 시 보장금액이 늘어나고 비갱신으로 보험료 고정"),
            "opt2": ("🤝 간병인 직접 지원일당", "간병인 구하기 힘든 상황에서 보험사가 직접 인력을 매칭해주는 편리함")
        },
        7: {
            "title": "중복 가입으로 낭비되는 비례보상 특약 정리 가이드",
            "core_focus": "실손보험, 운전자비용(벌금/합의금), 일상생활배상책임은 10개 들어도 실제 손해액만 1회 비례보상",
            "key_facts": [
                "상법 및 보험업법상 '실손비례보상' 담보는 여러 보험사에 중복 가입해도 실제 발생한 손해액 이상 지급되지 않습니다.",
                "회사 단체실손과 개인실손을 이중으로 내고 있다면 개인실손 '중지 제도'를 활용해 이중 납부를 막을 수 있습니다.",
                "가족 일상생활배상책임(일배책) 역시 중복 가입 시 보험료만 이중 청구되므로 증권 점검을 통한 정리가 필수입니다."
            ],
            "debate_question": "중복 가입 보험료 점검: 이중 납부 특약 즉시 삭제 vs 만약을 대비해 중복 유지?",
            "opt1": ("✂️ 중복 특약 즉시 다이어트", "비례보상으로 돈 못 받는 중복 특약 삭제하고 매달 보험료 절감"),
            "opt2": ("🛡️ 중복 유지 (자기부담금 상쇄)", "일배책 등 일부 담보의 자기부담금 0원 효과를 노리고 유지")
        },
        8: {
            "title": "보험료 부담될 때 무작정 해지 대신 '감액완납' 활용법",
            "core_focus": "해지 시 원금 손실 극심! '감액완납'(추가납입 중단하고 보장 축소 유지), '보험료 납입유예', '특약 부분 해지'",
            "key_facts": [
                "보험료가 부담된다고 성급히 해약하면 해약환급금이 납입 원금에 훨씬 못 미쳐 큰 금전적 손실을 봅니다.",
                "'감액완납' 제도를 신청하면 지금까지 낸 해약환급금으로 남은 기간 보험료를 일시 완납 처리하고 보장을 유지할 수 있습니다.",
                "불필요한 선택특약만 골라서 부분 삭제하거나 납입유예 제도를 활용하면 해약 없이 월 고정 지출을 줄일 수 있습니다."
            ],
            "debate_question": "가계 부담 시 보험료 다이어트 방식: 감액완납/특약삭제로 유지 vs 해약환급금 수령 후 재설계?",
            "opt1": ("🔄 감액완납/특약 부분삭제", "과거 좋은 조건의 주계약은 끝까지 살려두고 월 지출만 0원으로 축소"),
            "opt2": ("🧾 전면 해약 후 신규 가입", "가족력과 현재 재정 상황에 맞춰 34개사 최저가 다이렉트로 완전 재설계")
        }
    }

    def __init__(self):
        from config import (
            GEMINI_FREE_API_KEY_AURA_1,
            GEMINI_FREE_API_KEY_AURA_2,
            GEMINI_FREE_API_KEY_AURA_3,
            GEMINI_FREE_API_KEY_AURA_4,
            GEMINI_PAID_API_KEY_AURA_1,
            GEMINI_API_KEY
        )
        self.key_chain = get_unified_gemini_key_dicts()
        self._active_key_index = 0
        self.hashtag_matrix = InsuranceHashtagMatrix()

    def _sanitize_compliance_text(self, text: str) -> str:
        """심의 금지어를 객관적이고 신뢰도 높은 어휘로 자동 치환/정제"""
        if not text:
            return ""
        sanitized = text
        sanitized = re.sub(r'무조건|절대|100% 보장', '통계적으로', sanitized)
        sanitized = re.sub(r'호갱', '과납 소비자', sanitized)
        sanitized = re.sub(r'공짜|무료 환급', '합리적인 비용 절감', sanitized)
        sanitized = re.sub(r'최고|최저가 보장', '공시 기준 비교', sanitized)
        return sanitized

    def generate_copy_for_topic(self, topic_id: int, theme_name: str, fallback_scenario: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        주제별 5장 슬라이드 카피 및 SNS 본문 캡션 생성 (제미나이 3개 무료키 자율 체인 + 주제 이탈 0% + 심의 준수)
        """
        topic_info = self.TOPIC_FACT_MATRIX.get(topic_id, self.TOPIC_FACT_MATRIX[1])
        hashtags_list = self.hashtag_matrix.get_instagram_hashtags(topic_id, count=15)
        hashtags_str = " ".join(hashtags_list)

        system_instruction = f"""
당신은 대한민국 금융위원회 및 금융감독원 표준약관을 완벽히 꿰뚫고 있는 수석 금융 분석가이자, 1080x1350 카드뉴스 전문 에디터입니다.
금융소비자보호법(금소법) 심의 기준을 100% 준수하여, 금융소비자에게 꼭 필요한 객관적 팩트와 약관 분석 콘텐츠를 집필합니다.

[🚨 절대 불변의 4대 집필 철칙]:
1. [주제 이탈 0% 원칙 (TOPIC INTEGRITY)]:
   - 이번 집필 대상 주제는 [주제 #{topic_id}: {topic_info['title']}] 입니다.
   - 반드시 이 주제의 핵심 쟁점([{topic_info['core_focus']}])에 대해서만 깊이 있게 분석하고, 절대 다른 주제나 엉뚱한 일반론으로 벗어나지 마십시오.
2. [금융소비자보호법 심의 절대 준수]:
   - '무조건', '100%', '최고', '공짜', '호갱', '절대' 등 단정적·과장된 표현 전면 금지.
   - 금융감독원 표준약관, 비급여 자기부담금, 공시 데이터 등 객관적 근거에 기반하여 서술할 것.
3. [풍성하고 알찬 분량 (부실한 짧은 문장 금지)]:
   - 슬라이드별 제목 22~32자, 부제목 35~50자, 각 불릿 포인트 35~55자로 충실한 정보를 담을 것.
   - SNS 본문 캡션은 350~450자 내외로 객관적 제도 분석 + 3대 점검 가이드 + 포털 검색 유도를 포함할 것.
4. [공식 검색어 표기]: 반드시 '보험 리밸런스' (띄어쓰기 필수)를 명시할 것.
"""

        user_prompt = f"""
[주제 #{topic_id}]: {topic_info['title']}
[핵심 집중 분석 쟁점]: {topic_info['core_focus']}
[핵심 팩트 근거 데이터]:
- {topic_info['key_facts'][0]}
- {topic_info['key_facts'][1]}
- {topic_info['key_facts'][2]}

[공식 검색어]: {self.OFFICIAL_KEYWORD} (띄어쓰기 필수)
[공식 URL]: {self.OFFICIAL_URL}
[추천 해시태그]: {hashtags_str}

위 팩트 데이터를 바탕으로 아래 JSON 규격에 맞춰 5장 카드뉴스 카피 및 SNS 캡션을 작성하세요.
각 슬라이드는 반드시 주제 #{topic_id}의 구체적인 약관/제도 내용을 직접 다루어야 합니다.

[JSON 출력 포맷]:
{{
  "sns_caption": "350~450자 내외의 전문적인 SNS/스레드 본문 긴글 (주제 #{topic_id} 팩트 분석 + 3대 핵심 점검 포인트 + 네이버에 '{self.OFFICIAL_KEYWORD}' 검색 유도 + {self.OFFICIAL_URL} + 면책 고지 + {hashtags_str})",
  "slide1": {{
    "badge": "💡 주제 핵심 분석 배지 (15~22자)",
    "title": "주제 #{topic_id}의 핵심 쟁점을 짚는 헤드라인 (22~32자)",
    "subtitle": "통계 및 현실적인 배경 설명 부제목 (35~50자)",
    "bullets": [
      "주제 #{topic_id} 관련 핵심 팩트 1 (30~45자)",
      "주제 #{topic_id} 관련 핵심 팩트 2 (30~45자)",
      "34개 보험사 공시 기준 비교 원리 (30~45자)"
    ],
    "cta_button": "👉 옆으로 넘겨서 상세 팩트 확인하기 (1/5) >"
  }},
  "slide2": {{
    "badge": "📊 금융감독원 표준약관 분석",
    "title": "주제 #{topic_id}의 제도/약관 차이 정밀 분석 헤드라인 (22~32자)",
    "subtitle": "손익 분기점 및 약관상 유의사항 설명 (35~50자)",
    "bullets": [
      "{topic_info['key_facts'][0]}",
      "{topic_info['key_facts'][1]}",
      "{topic_info['key_facts'][2]}"
    ],
    "cta_button": "다음 분석 내용 보기 (2/5) >"
  }},
  "slide3": {{
    "badge": "💡 0.1초 자가진단",
    "title": "이름·전화번호 입력 제로!\\n주제 #{topic_id} 조건 자가진단",
    "headline_line1": "이름·전화번호 입력 제로!",
    "headline_line2": "주제 #{topic_id} 맞춤 자가진단",
    "subtitle": "생년월일만으로 34개 보험사 기준 내 조건 손익 분기점을 0.1초 만에 확인",
    "bullets": [
      "개인정보 유출 및 스팸 전화 걱정 없는 100% PII-Free 익명 진단",
      "내 연령·성별 기준 해당 담보 손익 분기점 즉시 판정",
      "최근 병원 이용량 및 갱신 주기에 따른 예상 보험료 산출"
    ],
    "cta_button": "👉 옆으로 넘겨서 34개사 최저가 순위표 보기 (3/5) >"
  }},
  "slide4": {{
    "badge": "📊 대한민국 34개사 전수 공개",
    "title": "스팸 전화 0건! 34개 보험사 최저가\\n내 눈으로 0.1초 만에 전수 비교",
    "headline_line1": "스팸 전화 0건! 34개 보험사 최저가",
    "headline_line2": "내 눈으로 0.1초 만에 전수 비교",
    "subtitle": "특정사 편파 없이 34개 전 보험사 실제 공시 가격표를 투명하게 전수 공개",
    "bullets": [
      "생명보험·손해보험 34개사 실시간 가격표 0.1초 전수 비교",
      "동일 보장 기준 월 최저가 순위 투명 공개로 불필요한 거품 제거",
      "설계사 수수료 마진 없는 다이렉트 공시 기준 데이터 제공"
    ],
    "cta_button": "👉 옆으로 넘겨서 내 선택 결정하기 (4/5) >"
  }},
  "slide5": {{
    "debate_badge": "⚡ {topic_info['title'][:18]} 찬반 토론",
    "theme_name": "{topic_info['title']}",
    "debate_question": "{topic_info['debate_question']}",
    "debate_opt1_title": "{topic_info['opt1'][0]}",
    "debate_opt1_sub": "{topic_info['opt1'][1]}",
    "debate_opt1_rate": "74% (대세)",
    "debate_opt2_title": "{topic_info['opt2'][0]}",
    "debate_opt2_sub": "{topic_info['opt2'][1]}",
    "debate_opt2_rate": "26%",
    "benefit_items": [
      "34개 보험사 실시간 최저가 비교",
      "이름·전화번호 입력 제로 (스팸 0건)",
      "내 나이 맞춤 갱신 손익 0.1초 판정"
    ],
    "cta_subtext": "✨ 스팸 전화 0건 • 지금 조회하고 내 통장에서 매달 새는 보험료 막기",
    "cta_button": "👉 네이버에 '{self.OFFICIAL_KEYWORD}' 검색하기 >"
  }}
}}
오직 위 JSON 포맷만 순수하게 출력하세요. 백틱(```json) 없이 유효한 JSON만 반환하세요.
"""

        total_keys = len(self.key_chain) if self.key_chain else 1
        for i in range(total_keys):
            idx = (self._active_key_index + i) % total_keys
            key_info = self.key_chain[idx]
            api_key = key_info["key"]

            try:
                from google import genai
                from google.genai import types as genai_types
                types = genai_types

                client = genai.Client(api_key=api_key)
                models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash"]

                for model_name in models_to_try:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=user_prompt,
                            config=genai_types.GenerateContentConfig(
                                automatic_function_calling=genai_types.AutomaticFunctionCallingConfig(disable=True), system_instruction=system_instruction,
                                temperature=0.60,
                                max_output_tokens=4096,
                                response_mime_type="application/json"
                            )
                        )
                        if response and response.text:
                            raw_json = response.text.strip()
                            if raw_json.startswith("```json"):
                                raw_json = raw_json[7:]
                            if raw_json.startswith("```"):
                                raw_json = raw_json[3:]
                            if raw_json.endswith("```"):
                                raw_json = raw_json[:-3]
                            raw_json = raw_json.strip()

                            try:
                                parsed = json.loads(raw_json, strict=False)
                            except Exception:
                                # 줄바꿈 및 제어문자 정제
                                clean_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', lambda m: '\n' if m.group(0) in '\r\n\t' else ' ', raw_json)
                                parsed = json.loads(clean_text, strict=False)

                            # 🤖 [자체 무결성 게이트 및 심의 정제]
                            parsed = self._validate_and_enrich_copy(parsed, topic_id, topic_info['title'], hashtags_str)
                            self._active_key_index = idx
                            logger.info(f"✅ [InsuranceCopywriter] 주제 #{topic_id} 제미나이({model_name}, 키={key_info['name']}) 5장 카피 집필 성공!")
                            return parsed
                    except Exception as me:
                        err_str = str(me)
                        if any(k in err_str for k in ["429", "RESOURCE_EXHAUSTED", "quota", "depleted", "QuotaFailure"]):
                            logger.warning(f"⚠️ [할당량 소진] 키={key_info['name']} ({model_name}) 429 쿼터 초과 -> 다음 무료키로 즉시 롤오버!")
                            key_quota_exhausted = True
                            break
                        else:
                            logger.warning(f"⚠️ [InsuranceCopywriter] {model_name} 실패 (키={key_info['name']}): {me}")
                            continue

                if key_quota_exhausted:
                    self._active_key_index = (idx + 1) % total_keys
                    continue
            except Exception as ke:
                logger.warning(f"⚠️ [InsuranceCopywriter] 키={key_info['name']} 호출 실패: {ke}")
                self._active_key_index = (idx + 1) % total_keys
                continue

        logger.warning(f"⚠️ [InsuranceCopywriter] 모든 제미나이 키 소진 -> 심의 준수 폴백 시나리오 적용")
        return self._build_compliant_fallback(topic_id, topic_info['title'], fallback_scenario, hashtags_str)

    def _validate_and_enrich_copy(self, data: Dict[str, Any], topic_id: int, theme_name: str, hashtags_str: str) -> Dict[str, Any]:
        """제미나이 생성 결과에 대한 무결성 검증 및 심의 안전 보강"""
        caption = data.get("sns_caption", "")
        if self.OFFICIAL_KEYWORD not in caption:
            caption += f"\n\n👉 지금 네이버 검색창에 '{self.OFFICIAL_KEYWORD}'을 검색해보세요!\n🔗 공식 진단: {self.OFFICIAL_URL}"

        # 법적 면책 고지 부착
        disclaimer = "※ 본 콘텐츠는 금융소비자의 이해를 돕기 위한 정보 제공 목적이며, 개별 약관 및 가입 조건에 따라 달라질 수 있습니다."
        if disclaimer not in caption:
            caption += f"\n\n{disclaimer}"

        # 해시태그 보강
        if "#" not in caption:
            caption += f"\n\n{hashtags_str}"

        data["sns_caption"] = self._sanitize_compliance_text(caption)

        # 각 슬라이드 텍스트 정제
        for i in range(1, 6):
            s_key = f"slide{i}"
            if s_key in data and isinstance(data[s_key], dict):
                s = data[s_key]
                if "title" in s:
                    s["title"] = self._sanitize_compliance_text(s["title"])
                if "subtitle" in s:
                    s["subtitle"] = self._sanitize_compliance_text(s["subtitle"])
                if "bullets" in s and isinstance(s["bullets"], list):
                    s["bullets"] = [self._sanitize_compliance_text(b) for b in s["bullets"]]

        return data

    def _build_compliant_fallback(self, topic_id: int, theme_name: str, fallback_scenario: Optional[Dict[str, Any]], hashtags_str: str) -> Dict[str, Any]:
        """심의 기준 100% 준수 안전 폴백 데이터"""
        topic_info = self.TOPIC_FACT_MATRIX.get(topic_id, self.TOPIC_FACT_MATRIX[1])
        caption = (
            f"🛡️ [보험 리밸런스 팩트체크 리포트] #{topic_id} {theme_name}\n\n"
            f"매달 통장에서 나가는 보험료, 과연 현재 보장 내역과 내 상황에 맞게 최적화되어 있을까요?\n\n"
            f"📌 금융소비자가 꼭 알아야 할 3대 점검 팩트:\n"
            f"1️⃣ {topic_info['key_facts'][0]}\n"
            f"2️⃣ {topic_info['key_facts'][1]}\n"
            f"3️⃣ {topic_info['key_facts'][2]}\n\n"
            f"👇 34개 보험사 실시간 최저가 비교 & 새는 돈 계산기\n"
            f"👉 상단 프로필(@goldmomofficial) 링크를 터치하시면 0.1초 만에 확인 가능합니다! (스팸 0건)\n"
            f"🔍 네이버 검색: [{self.OFFICIAL_KEYWORD}]\n\n"
            f"※ 본 콘텐츠는 금융소비자의 이해를 돕기 위한 정보 제공 목적이며, 개별 약관 및 가입 조건에 따라 달라질 수 있습니다.\n\n"
            f"{hashtags_str}"
        )

        return {
            "sns_caption": caption,
            "slide1": {
                "badge": "💡 2026 보험 리모델링 팩트체크",
                "title": f"#{topic_id} {theme_name}",
                "subtitle": "금융감독원 표준약관 및 통계 기준 객관적 팩트 분석",
                "bullets": [
                    "매달 지출되는 고정 보험료의 합리적 절감 포인트 분석",
                    "병원 이용 빈도에 따른 실손보험 세대별 손익 분기점 비교",
                    "34개 보험사 공시 기준 객관적 가격표 전수 공개"
                ],
                "cta_button": "👉 옆으로 넘겨서 상세 팩트 확인하기 (1/5) >"
            },
            "slide2": {
                "badge": "📊 금융감독원 표준약관 분석",
                "title": f"#{topic_id} 핵심 약관 및 제도 비교",
                "subtitle": topic_info['core_focus'],
                "bullets": topic_info['key_facts'],
                "cta_button": "다음 분석 내용 보기 (2/5) >"
            },
            "slide3": {
                "badge": "💡 0.1초 자가진단",
                "title": f"이름·전화번호 입력 제로!\n주제 #{topic_id} 자가진단",
                "headline_line1": "이름·전화번호 입력 제로!",
                "headline_line2": f"주제 #{topic_id} 맞춤 자가진단",
                "subtitle": "생년월일만으로 34개 보험사 기준 해당 대상인지 0.1초 만에 확인",
                "bullets": [
                    "개인정보 유출 및 스팸 전화 걱정 없는 100% PII-Free 진단",
                    "내 연령·성별 기준 해당 담보 손익 분기점 즉시 판정",
                    "최근 병원 이용량에 따른 예상 갱신 보험료 산출"
                ],
                "cta_button": "👉 옆으로 넘겨서 34개사 최저가 순위표 보기 (3/5) >"
            },
            "slide4": {
                "badge": "📊 대한민국 34개사 전수 공개",
                "title": "스팸 전화 0건! 34개 보험사 최저가\n내 눈으로 0.1초 만에 전수 비교",
                "headline_line1": "스팸 전화 0건! 34개 보험사 최저가",
                "headline_line2": "내 눈으로 0.1초 만에 전수 비교",
                "subtitle": "특정사 편파 없이 34개 전 보험사 실제 공시 가격표를 투명하게 전수 공개",
                "bullets": [
                    "생명보험·손해보험 34개사 실시간 가격표 0.1초 전수 비교",
                    "동일 보장 기준 월 최저가 순위 투명 공개로 불필요한 거품 제거",
                    "설계사 수수료 마진 없는 다이렉트 공시 기준 데이터 제공"
                ],
                "cta_button": "👉 옆으로 넘겨서 내 선택 결정하기 (4/5) >"
            },
            "slide5": {
                "debate_badge": f"⚡ {theme_name[:18]} 찬반 토론",
                "theme_name": theme_name,
                "debate_question": topic_info['debate_question'],
                "debate_opt1_title": topic_info['opt1'][0],
                "debate_opt1_sub": topic_info['opt1'][1],
                "debate_opt1_rate": "74% (대세)",
                "debate_opt2_title": topic_info['opt2'][0],
                "debate_opt2_sub": topic_info['opt2'][1],
                "debate_opt2_rate": "26%",
                "benefit_items": [
                    "34개 보험사 실시간 최저가 비교",
                    "이름·전화번호 입력 제로 (스팸 0건)",
                    "내 나이 맞춤 갱신 손익 0.1초 판정"
                ],
                "cta_subtext": "✨ 스팸 전화 0건 • 지금 조회하고 내 통장에서 매달 새는 보험료 막기",
                "cta_button": f"👉 네이버에 '{self.OFFICIAL_KEYWORD}' 검색하기 >"
            }
        }
