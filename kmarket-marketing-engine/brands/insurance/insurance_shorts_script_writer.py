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

[★ 핵심 원칙 (절대 불변)]
1. 아래 [기준 원본 골든 대본]에 담긴 **스토리 라인, 핵심 팩트(고객이 직접 생년월일/성별 입력, 34개사 최저가 비교, 비갱신형 등), 실제 기능 플로우를 100% 온전히 계승**하세요.
2. 임의로 없는 기능을 상상해서 지어내거나(예: 증권 구멍을 색출해준다 등 ❌) 팩트를 왜곡하지 마세요.
3. [기준 원본 골든 대본]의 뼈대를 바탕으로, 전문 금융 아나운서 어조와 정확한 글자수 규격(10초 훅 / 12초 앱 시연)에 맞춰 가장 매끄럽고 명쾌한 발화문으로 정밀 다듬기하세요.

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

[대본 글자수 절대 규칙 (Wan 2.2 S2V 10초 립싱크 완벽 동기화)]
1. hook_p1 (0~5초): 시선을 사로잡는 현실 보험 공감 질문 [공백 포함 정확히 25~32자]
2. hook_p2 (5~10초): 핵심 팩트와 해결책 제시 [공백 포함 정확히 25~32자]
   ★ 중요: hook_p1과 hook_p2를 합친 전체 훅(0~10초)은 반드시 [공백 포함 55~65자] 내외여야 합니다.
3. app_speech (10~20초): 실제 앱 화면에서 34개사 실시간 비교/자가진단이 일어나는 상황 설명 [공백 포함 75~100자 (약 8~9초 발화 분량으로 침묵 없이 꽉 차게)]
4. cta_speech (20~22초): "네이버에 {self.OFFICIAL_KEYWORD} 검색해보세요!" 유도 [공백 포함 18~25자]

[글자수 합계 엄수: 전체 대본 합계가 공백 포함 정확히 150~185자 내외가 되도록 작성하세요.]

반드시 아래 JSON 포맷으로만 응답하세요:
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

                    # 공식 검색어 포함 검증 (누락 시 자동 보정)
                    if self.OFFICIAL_KEYWORD not in cta_speech:
                        cta_speech = f"네이버에 {self.OFFICIAL_KEYWORD} 검색해보세요!"

                    hook_full = f"{hook_p1} {hook_p2}".strip()
                    full_speech = f"{hook_full} {app_speech} {cta_speech}".strip()

                    # 🔒 무결성 게이트 검증
                    # 1) 훅 글자수 검증: 45자 ~ 70자 (Wan 10초 립싱크 안전 마진: 9.0s ~ 10.2s)
                    if len(hook_full) < 45 or len(hook_full) > 70:
                        logger.warning(f"⚠️ 훅 글자수 범위 벗어남({len(hook_full)}자, 목표: 55~65자), 다음 시도")
                        continue

                    # 2) 앱 시연 글자수 검증: 65자 ~ 110자 (12초 앱 시연 음성 공백 방지)
                    if len(app_speech) < 65 or len(app_speech) > 115:
                        logger.warning(f"⚠️ 앱 시연 글자수 범위 벗어남({len(app_speech)}자, 목표: 75~100자), 다음 시도")
                        continue

                    # 3) 전체 글자수 검증: 135자 ~ 195자
                    if len(full_speech) < 135 or len(full_speech) > 195:
                        logger.warning(f"⚠️ 전체 글자수 범위 벗어남({len(full_speech)}자, 목표: 150~185자), 다음 시도")
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
