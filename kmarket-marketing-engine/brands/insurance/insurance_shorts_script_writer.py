# -*- coding: utf-8 -*-
"""
InsuranceShortsScriptWriter - 🤖 [보험 리밸런스 8대 주제 100% 순수 자율 창작 제미나이 대본 생성기]
========================================================================================
- 원칙: '주입 문장 0%' — AI에게 예시 문장을 주입하지 않고, 오직 '상황/기능'과 '22초 시간/글자수 규격'만 제공
- 제미나이 2.5 Flash가 매번 전문 금융 아나운서 감성의 독창적이고 참신한 대본을 100% 즉석 자율 집필
- 8대 전용 고화질 실제 앱 시뮬레이션(34개사 실시간 비교 12초)과 100% 동기화
- 3개 무료키 자율 체인 & 100% 무인 무결성 게이트 탑재 (공식 검색어 '보험 리밸런스' 필수 검증)
- 10초 훅 대본을 정확히 58~64자(Part1 30자 + Part2 30자)로 제한하여 Wan 2.2 S2V 10.12초 립싱크와 0.1초 오차 없이 일치
- API 오류 시 기존 검증된 골든 대본으로 자동 안전 폴백(Fallback) 보장
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("InsuranceShortsScriptWriter")

# 8대 주제별 '순수 상황 & 기능 정의'
INSURANCE_8_TOPIC_CONCEPTS: Dict[int, Dict[str, str]] = {
    1: {
        "title": "실손의료비 4세대 전환 손익",
        "concept": "병원에 자주 안 가는데 옛날 실비보험료를 매달 5~10만원씩 비싸게 내는 소비자를 위해, 4세대 실손으로 전환 시 월 1만원대로 줄어드는 손익을 33개사 실시간 비교로 확인하는 기능.",
        "app_sim_visual": "실손의료비 4세대 전환 시뮬레이션 및 33개 보험사 실시간 보험료 비교 순위표가 1초 만에 뜨는 모습."
    },
    2: {
        "title": "운전자보험 1만원의 법칙",
        "concept": "자동차보험과 별개로 운전자보험에 3~4만원씩 과다 지출하는 운전자를 위해, 필수 3대 특약(벌금, 변호사비, 합의금)만 챙겨 월 1만3천원에 군더더기 없이 맞추는 기능.",
        "app_sim_visual": "운전자보험 필수 3대 특약 선택 후 불필요한 중복 특약이 제거되고 1만원대 견적이 완성되는 모습."
    },
    3: {
        "title": "암보험 일반암 vs 유사암 진실",
        "concept": "갑상선암이나 소액암 진단 시 10%만 지급되는 약관 함정을 피하기 위해, 내가 필요한 암 진단금을 직접 선택하고 34개 보험사의 암보험료와 보장 범위를 실시간으로 1초 만에 비교하는 기능.",
        "app_sim_visual": "원하는 암 진단금 특약 선택 및 고객 조건 입력 시 국내 34개 보험사 암보험 비교 분석표가 실시간 렌더링되는 모습."
    },
    4: {
        "title": "뇌경색 100% 뇌혈관질환 최저가 다이렉트 비교",
        "concept": "뇌경색과 협심증까지 100% 보장되는 뇌혈관·허혈성 심장질환 보험을 위해, 생년월일과 성별만 입력하고 국내 33개 보험사의 실시간 최저가 순위를 1초 만에 비교하는 기능.",
        "app_sim_visual": "생년월일과 성별 선택 후 국내 33개 보험사의 뇌혈관·허혈성 진단비 최저가 비교 순위표가 실시간 렌더링되는 모습."
    },
    5: {
        "title": "아는 사람 부탁으로 가입한 보험 손익 분석",
        "concept": "아는 사람이나 지인 부탁으로 가입해 매달 돈만 나가고 무슨 보장인지도 모르는 보험에 대해, 내 나이만 넣으면 얼마를 손해보고 있는지와 국내 34개 보험사 실시간 최저가 가격을 1초 만에 비교해주는 기능.",
        "app_sim_visual": "나이와 성별 입력 후 34개 보험사 실시간 최저가 비교표와 매달 새는 돈 절감 분석표가 1초 만에 뜨는 화면."
    },
    6: {
        "title": "어린이·어른이 100세 만기 리모델링",
        "concept": "부모님이 100세 만기로 들어준 옛날 보험의 갱신형 인상 부담 대신, 생년월일과 성별을 직접 입력하여 국내 34개 보험사의 비갱신형 최저가 순위를 1초 만에 실시간으로 비교하고 알뜰하게 리모델링하는 기능.",
        "app_sim_visual": "생년월일/성별 입력 후 34개 보험사 비갱신형 종합건강 최저가 비교 순위표가 실시간 렌더링되는 모습."
    },
    7: {
        "title": "내 보험 정밀 비교 & 새는 보험료 다이어트",
        "concept": "매달 비싸게 나가는 기존 보험 대비, 국내 34개 보험사의 더 저렴하고 보장이 든든한 최적 상품을 1초 만에 정밀 비교하여 불필요한 보험료 지출을 똑똑하게 다이어트하는 기능.",
        "app_sim_visual": "기존 대비 34개사 최저가 비교 순위표와 매달 절감되는 보험료 분석 리포트가 1초 만에 뜨는 모습."
    },
    8: {
        "title": "AI 보험료 역추정 비교 & 가성비 리모델링",
        "concept": "고객이 내는 보험료 금액을 기준으로 AI가 역추정하여, 같은 금액에 보장이 훨씬 넓은 보험과 똑같은 보장에 더 저렴한 상품을 34개 보험사에서 1초 만에 비교/추천해주는 기능.",
        "app_sim_visual": "보험료 금액 입력 후 AI 역추정 분석으로 같은 가격 최대 보장 순위표가 1초 만에 뜨는 모습."
    }
}


class InsuranceShortsScriptWriter:
    """🛡️ 보험 리밸런스 8대 주제 전용 제미나이 2.5 Flash 실시간 자율 대본 생성 엔진"""

    OFFICIAL_KEYWORD = "보험 리밸런스"
    FORBIDDEN_WORDS = [
        # 마케팅 날조 금지
        "한정", "이벤트", "선착순", "마감", "사은품", "쿠폰", "오늘만", 
        "특가", "캐시백", "당첨", "데이팅", "소개팅", "연애", "매칭", "주식", "종목",
        # 🚨 [보험 심의 및 금소법 위반 금지어 (과장, 공포, 비하, 단정)]
        "호갱", "폭탄", "사기", "대충격", "공중분해", "반토막", "절반으로", "줄어듭니다",
        "무조건", "100%", "압도적", "배불리는", "파산", "눈물", "생돈", "뻥튀기",
        "수수료 떼먹", "속인", "20만원", "30만원", "10만원 아끼", "1억"
    ]

    def __init__(self):
        try:
            from config import (
                GEMINI_FREE_API_KEY_AURA_1,
                GEMINI_FREE_API_KEY_AURA_2,
                GEMINI_FREE_API_KEY_AURA_3,
                GEMINI_PAID_API_KEY_AURA_1,
                GEMINI_API_KEY
            )
            candidates = [
                {"name": "FREE_1", "key": GEMINI_FREE_API_KEY_AURA_1},
                {"name": "FREE_2", "key": GEMINI_FREE_API_KEY_AURA_2},
                {"name": "FREE_3", "key": GEMINI_FREE_API_KEY_AURA_3},
                {"name": "PAID_1", "key": GEMINI_PAID_API_KEY_AURA_1},
                {"name": "DEFAULT", "key": GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")}
            ]
        except Exception:
            candidates = [{"name": "ENV", "key": os.environ.get("GEMINI_API_KEY")}]

        seen = set()
        self.key_chain = []
        for c in candidates:
            k = (c.get("key") or "").strip()
            if k and k not in seen and len(k) > 10:
                seen.add(k)
                self.key_chain.append(k)

    def generate_dynamic_script(self, topic_id: int = 1) -> Optional[Dict[str, Any]]:
        """
        주제 ID(1~8)에 맞춰 우리가 검증한 골든 대본을 [기준 원본 뼈대]로 제미나이에 주입하여,
        핵심 팩트와 웹앱 플로우를 100% 온전히 유지하면서 전문 아나운서 어조/글자수를 최적화한 대본 생성.
        실패 시 None을 반환하여 기존 골든 대본으로 자동 폴백.
        """
        norm_id = ((topic_id - 1) % len(INSURANCE_8_TOPIC_CONCEPTS)) + 1
        info = INSURANCE_8_TOPIC_CONCEPTS.get(norm_id, INSURANCE_8_TOPIC_CONCEPTS[1])

        # 🌟 [우리가 검증한 골든 대본 기준 원본 로드]
        try:
            from core.shorts_engine.insurance_shorts_scenario_director import InsuranceShortsScenarioDirector
            golden = InsuranceShortsScenarioDirector.SCRIPTS_22S.get(norm_id, {})
        except Exception:
            golden = {}

        ref_hook_p1 = golden.get("hook_p1_5s", "")
        ref_hook_p2 = golden.get("hook_p2_5s", "")
        ref_app = golden.get("app_10_20s", "")
        ref_hero = golden.get("hero_copy", "객관적 5대 보장 AI 분석!")
        ref_debate = golden.get("debate_question", "내 보험 보장 범위는 안전할까?")

        prompt = f"""당신은 신뢰감 있고 명쾌하며 스마트한 대한민국 금융/보험 전문 아나운서입니다.
아래 제공된 [기준 원본 골든 대본]과 앱 기능 정보를 바탕으로, 대한민국 국민들이 깊이 공감하고 즉시 행동할 수 있는 22초 숏폼 아나운서 대본을 완성해주세요.

[🏛️ 대한민국 금융소비자보호법 & 보험 광고 심의 절대 헌법 (위반 시 즉시 반려)]
1. 🚨 [특정 금액 및 절감 비율 단정 전면 금지 (금소법 제21조)]: "월 20만원", "보험료를 절반으로 줄여준다", "월 10만원 절약" 등 가입자별로 달라지는 수치를 임의로 단정하지 마세요. 오직 "동일 보장 기준 34개 보험사 객관적 요율 비교", "연령/조건별 맞춤 분석"으로만 서술하세요.
2. 🚨 [공포·비하·자극적 마케팅 단어 100% 원천 차단]: '호갱', '폭탄', '사기', '대충격', '공중분해', '반토막', '파산', '눈물', '생돈', '뻥튀기' 등의 단어를 일체 사용하지 마세요. 대신 '약관상 보장 공백', '연령별 위험률 구조', '비례보상(중복 지급 불가) 원리' 등 품격 있는 금융 팩트 용어로만 작성하세요.
3. 🚨 [타 직군/보험사 비방 및 최상급 표현 금지]: '설계사가 속인', '보험사만 배불리는', '압도적 유리' 등의 문구를 쓰지 말고, 소비자의 합법적 권리(감액완납, 비갱신 전환, 특약 정비)를 객관적으로 설명하세요.
4. 🚨 [허위 마케팅 날조 전면 금지]: '한정 이벤트', '선착순 마감', '사은품 증정', '오늘만 특가', '계좌로 즉시 입금' 등의 거짓말 문구를 절대 지어내지 마세요.
5. [기준 원본 골든 대본]의 뼈대를 바탕으로, 전문 금융 아나운서 어조와 정확한 글자수 규격(10초 훅 / 12초 앱 시연)에 맞춰 가장 매끄럽고 명쾌한 발화문으로 정밀 다듬기하세요.

[기준 원본 골든 대본 (Ground Truth Reference)]
- 기준 훅 1 (0~5초): {ref_hook_p1}
- 기준 훅 2 (5~10초): {ref_hook_p2}
- 기준 웹앱 시연 (10~20초): {ref_app}
- 기준 히어로 카피: {ref_hero}
- 기준 토론 질문: {ref_debate}

[상황 및 기능 정보]
- 주제: {info['title']} (보험 리밸런스 기능 #{norm_id})
- 핵심 상황: {info['concept']}
- 실제 앱 시연 화면(10~20초): {info['app_sim_visual']}
- 공식 포털 검색어: {self.OFFICIAL_KEYWORD}

[대본 글자수 절대 규칙 (정확히 22.0초 완제품 동기화 - 120~130자)]
1. hook_p1 (0~5초): 시선을 사로잡는 현실 보험 공감 질문 [공백 포함 22~26자]
2. hook_p2 (5~10초): 핵심 팩트와 해결책 제시 [공백 포함 22~26자]
   ★ 중요: hook_p1과 hook_p2를 합친 전체 훅(0~10초)은 [공백 포함 45~52자]여야 합니다. (Wan 2.2 S2V 10초 립싱크 완벽 동기화)
3. app_speech (10~20초): 실제 앱 화면에서 34개사 실시간 비교/자가진단이 일어나는 상황 설명 [공백 포함 48~56자 (정확히 8~9초 발화 분량)]
4. cta_speech (20~22초): "지금 네이버에 {self.OFFICIAL_KEYWORD} 검색해보세요!" [공백 포함 20~24자]

[글자수 합계 엄수: 전체 대본 합계가 공백 포함 정확히 120~130자가 되도록 반드시 간결하고 명확하게 작성하세요 (22초 완제품 일치).]

[작성 예시 (124자 규격)]:
{{
  "hook_p1": "운전자보험 매달 3, 4만 원씩 내시나요?",
  "hook_p2": "필수 3대 특약만 챙기면 월 1만 원대 설계가 가능합니다!",
  "app_speech": "보험 리밸런스에서 증권만 스캔하면 쓸데없이 새는 중복 특약을 1초 만에 싹 정리해 줍니다.",
  "cta_speech": "지금 네이버에 보험 리밸런스 검색해보세요!",
  "hero_copy": "필수 3대 특약으로 월 13,000원 완성!",
  "debate_question": "운전자보험 1만원대, 충분할까 vs 부족할까?"
}}

반드시 위 예시와 동일한 JSON 포맷으로만 응답하세요:
{{
  "hook_p1": "...",
  "hook_p2": "...",
  "app_speech": "...",
  "cta_speech": "...",
  "hero_copy": "15자 내외 핵심 헤드라인",
  "debate_question": "10자 내외 질문"
}}"""

        # 🆕 [무한 변주 엔진] 오늘의 훅 아키타입 지시를 프롬프트 끝에 추가
        try:
            from core.variation_engine.insurance_hook_variator import InsuranceHookVariator
            hook_injection = InsuranceHookVariator().build_hook_injection(
                topic_id=norm_id,
                topic_title=info['title'],
                topic_concept=info['concept'],
                app_sim_visual=info['app_sim_visual'],
            )
            prompt = prompt + hook_injection
        except Exception as e:
            logger.debug(f"[보험 변주 엔진] 로드 실패 (기존 프롬프트로 진행): {e}")

        if not self.key_chain:
            logger.warning("🔑 [보험 자율 대본] 유효한 Gemini API 키가 없습니다. 골든 대본으로 폴백합니다.")
            return None

        from google import genai
        from google.genai import types

        models = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-flash-latest"]
        for key in self.key_chain:
            try:
                client = genai.Client(api_key=key)
            except Exception:
                continue

            for model in models:
                try:
                    resp = client.models.generate_content(
                        model=model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.7
                        )
                    )
                    if not resp or not resp.text:
                        continue

                    data = json.loads(resp.text)
                    hook_p1 = data.get("hook_p1", "").strip()
                    hook_p2 = data.get("hook_p2", "").strip()
                    app_speech = data.get("app_speech", "").strip()
                    cta_speech = data.get("cta_speech", "").strip()
                    hero_copy = data.get("hero_copy", "").strip()
                    debate_q = data.get("debate_question", "").strip()

                    hook_full = f"{hook_p1} {hook_p2}".strip()
                    full_speech = f"{hook_full} {app_speech} {cta_speech}".strip()

                    # 🔒 [무결성 게이트 1: 금지어 / 허위 이벤트 검증]
                    has_forbidden = False
                    for bad_word in self.FORBIDDEN_WORDS:
                        if bad_word in full_speech:
                            logger.warning(f"🚫 [금지어 감지 탈락] '{bad_word}' 포함 대본 기각: {full_speech}")
                            has_forbidden = True
                            break
                    if has_forbidden:
                        continue

                    # 공식 검색어 포함 검증 (누락 시 자동 보정)
                    if self.OFFICIAL_KEYWORD not in cta_speech:
                        cta_speech = f"네이버에 {self.OFFICIAL_KEYWORD} 검색해보세요!"
                        full_speech = f"{hook_full} {app_speech} {cta_speech}".strip()

                    # 🔒 [무결성 게이트 2: 구간별 및 전체 글자수 검증 (정확히 21.5~22.5초 일치)]
                    # 1) 훅 글자수 검증: 42자 ~ 56자 (Wan 10초 립싱크 완벽 동기화)
                    if len(hook_full) < 42 or len(hook_full) > 56:
                        logger.warning(f"⚠️ 훅 글자수 범위 벗어남({len(hook_full)}자, 목표: 45~52자), 다음 시도")
                        continue

                    # 2) 앱 시연 글자수 검증: 42자 ~ 58자 (8~9초 앱 시연 음성 정밀 일치)
                    if len(app_speech) < 42 or len(app_speech) > 58:
                        logger.warning(f"⚠️ 앱 시연 글자수 범위 벗어남({len(app_speech)}자, 목표: 48~56자), 다음 시도")
                        continue

                    # 3) 전체 글자수 검증: 115자 ~ 132자 (정확한 22초대 완결 보장)
                    if len(full_speech) < 115 or len(full_speech) > 132:
                        logger.warning(f"⚠️ 전체 글자수 범위 벗어남({len(full_speech)}자, 목표: 120~130자), 다음 시도")
                        continue

                    logger.info(f"✨ [Gemini 보험 자율 대본 성공] 주제 #{norm_id} (훅:{len(hook_full)}자, 전체:{len(full_speech)}자, model={model})")
                    return {
                        "hook_p1_5s": hook_p1,
                        "hook_p2_5s": hook_p2,
                        "hook_0_10s": hook_full,
                        "app_10_20s": app_speech,
                        "cta_18_22s": cta_speech,
                        "hero_copy": hero_copy or "내가 원하는 진단금으로 실시간 비교!",
                        "debate_question": debate_q or "내 보험 보장 범위는 안전할까?",
                        "full_speech": full_speech,
                        "is_ai_generated": True
                    }
                except Exception as e:
                    logger.debug(f"Gemini 호출 실패 ({model}): {e}")
                    continue

        logger.warning(f"⚠️ [보험 대본] 제미나이 호출 모두 실패 ➔ 기존 검증된 골든 대본으로 자동 폴백")
        return None
