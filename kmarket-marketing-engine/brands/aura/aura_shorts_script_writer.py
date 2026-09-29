# -*- coding: utf-8 -*-
"""
AuraShortsScriptWriter - 🤖 [Aura 8대 주제 100% 순수 자율 창작 제미나이 대본 생성기]
================================================================================
- 원칙: '주입 문장 0%' — AI에게 예시 문장을 주입하지 않고, 오직 '상황/기능'과 '22초 시간 규격'만 제공
- 제미나이 2.5 Flash가 매번 2030 감성의 독창적이고 참신한 대본을 100% 즉석 자율 집필
- 8대 전용 고화질 실제 앱 시뮬레이션(아이프레임 8초)과 100% 동기화
- 3개 무료키 자율 체인 & 100% 무인 무결성 게이트 탑재 (검색어 '아우라AI데이팅' 필수 검증)
- API 오류 시 기존 검증된 골든 대본으로 자동 안전 폴백(Fallback) 보장
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("AuraShortsScriptWriter")

# 8대 주제별 '순수 상황 & 기능 정의' (예시 문장 전혀 없이 개념/상황만 정의)
AURA_8_TOPIC_CONCEPTS: Dict[int, Dict[str, str]] = {
    1: {
        "title": "소개팅 긴급 탈출 전화",
        "concept": "어색하거나 불쾌한 소개팅 자리에서 벗어나고 싶을 때, 앱에서 가짜 긴급 업무 호출 전화를 걸어주어 매너 있게 자리를 탈출할 수 있도록 돕는 기능.",
        "app_sim_visual": "스마트폰 화면에 진짜 팀장님 전화가 울리며 탈출 핑계 시나리오 대본이 화면에 뜸."
    },
    2: {
        "title": "실시간 AI 자막 통화",
        "concept": "외국어나 일본어를 전혀 못해도 영상 통화 시 화면 아래 넷플릭스처럼 실시간 번역 자막이 떠서 한일/글로벌 친구와 밤새 편하게 대화하는 기능.",
        "app_sim_visual": "영상 통화 중 화면 하단에 실시간 양방향 번역 자막이 타이핑되는 모습."
    },
    3: {
        "title": "50:50 VIP 게이트",
        "concept": "소개팅 앱들의 남초 90% 현상과 유령회원에 질린 2030을 위해, 남녀 성비가 50:50으로 완벽히 유지될 때만 신규 입장을 허용하는 정원제 VIP 라운지.",
        "app_sim_visual": "남성 가입 대기열 카운트다운 및 여성 VIP 프리패스 입장 애니메이션."
    },
    4: {
        "title": "청담동 화보 보정",
        "concept": "비싼 스튜디오에 가지 않아도 일상 폰카 사진 1장을 30만원짜리 청담동 스튜디오 화보급 프로필로 AI가 자연스럽게 변신시켜주는 기능.",
        "app_sim_visual": "평범한 일상 사진이 청담동 조명 화보 프로필로 슬라이드 전환되는 모습."
    },
    5: {
        "title": "가치관 밸런스 매칭",
        "concept": "연락 빈도, 데이트 비용, 소비 습관, 결혼관 등 12가지 연애 밸런스 게임을 통해 나와 가치관이 100% 찰떡궁합인 인연만 골라 매칭해주는 기능.",
        "app_sim_visual": "4장의 컬러풀한 파스텔 밸런스 선택 카드가 인터랙티브하게 선택되는 모습."
    },
    6: {
        "title": "AI 첫대화 비서",
        "concept": "매칭 후 첫마디 고민이나 읽씹 걱정 없이, 상대방 프로필과 취미를 분석해 답장률 99% 심쿵 첫마디와 대화 주제를 추천해주는 기능.",
        "app_sim_visual": "채팅창에서 AI 추천 답장 칩을 탭하자 센스 있는 멘트가 자동 전송되는 모습."
    },
    7: {
        "title": "AI 아우라 진단",
        "concept": "내 얼굴형과 이목구비를 AI가 정밀 분석하여 나의 독보적인 매력 키워드와 상위 % 아우라 지수(청순상, 여우상 등)를 1초 만에 진단해주는 기능.",
        "app_sim_visual": "AI 스캔 레이더가 얼굴을 분석하고 상위 3.8% 매력 리포트가 완성되는 모습."
    },
    8: {
        "title": "500m 안심 레이더",
        "concept": "동네 친구나 가벼운 카페/러닝 번개를 원하지만 집 주소 노출이나 스토킹이 불안한 사람을 위해, 실제 집 위치를 500m 랜덤 보안(지터링)으로 철통 방어하며 안전하게 당일 번개를 만나는 기능.",
        "app_sim_visual": "지도 위에서 500m 안심 보안 반경과 당일 번개 퀘스트 등록 모달이 시연되는 모습."
    }
}


class AuraShortsScriptWriter:
    """💖 Aura 8대 주제 전용 제미나이 2.5 Flash 실시간 자율 대본 생성 엔진"""

    OFFICIAL_KEYWORD = "아우라AI데이팅"

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
                {"name": "AURA_FREE_1", "key": GEMINI_FREE_API_KEY_AURA_1},
                {"name": "AURA_FREE_2", "key": GEMINI_FREE_API_KEY_AURA_2},
                {"name": "AURA_FREE_3", "key": GEMINI_FREE_API_KEY_AURA_3},
                {"name": "AURA_PAID_1", "key": GEMINI_PAID_API_KEY_AURA_1},
                {"name": "DEFAULT", "key": GEMINI_API_KEY}
            ]
        except Exception:
            candidates = []

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
        핵심 팩트와 웹앱 플로우를 100% 온전히 유지하면서 세련된 2030 어조/글자수를 최적화한 대본 생성.
        실패 시 None을 반환하여 기존 골든 대본으로 자동 폴백.
        """
        norm_id = ((topic_id - 1) % len(AURA_8_TOPIC_CONCEPTS)) + 1
        info = AURA_8_TOPIC_CONCEPTS.get(norm_id, AURA_8_TOPIC_CONCEPTS[1])

        # 🌟 [우리가 검증한 골든 대본 기준 원본 로드]
        try:
            from core.shorts_engine.aura_shorts_scenario_director import AuraShortsScenarioDirector
            golden = AuraShortsScenarioDirector.SCRIPTS_22S.get(norm_id, {})
        except Exception:
            golden = {}

        ref_hook_p1 = golden.get("hook_p1_5s", "")
        ref_hook_p2 = golden.get("hook_p2_5s", "")
        ref_app = golden.get("app_10_18s", "")
        ref_cta = golden.get("cta_18_22s", "")
        ref_debate = golden.get("debate_question", "이 기능, 센스다 vs 너무하다?")

        prompt = f"""당신은 청담/성수동 감성의 세련되고 지적이며 매력적인 2030 여성 앵커(인플루언서)입니다.
아래 제공된 [기준 원본 골든 대본]과 Aura 앱 기능 정보를 바탕으로, 2030 세대가 깊이 공감할 수 있는 22초 숏폼 발화 대본을 완성해주세요.

[★ 핵심 원칙 (절대 불변)]
1. 아래 [기준 원본 골든 대본]에 담긴 **스토리 라인, 핵심 팩트(가짜 긴급 호출, 실시간 번역 자막, 50:50 정원제 등), 실제 Aura 앱 작동 방식을 100% 온전히 계승**하세요.
2. 임의로 없는 기능을 상상해서 지어내거나 팩트를 왜곡하지 마세요.
3. [기준 원본 골든 대본]의 뼈대를 바탕으로, 성수/청담동 감성의 세련되고 품격 있는 2030 대화체와 정확한 글자수 규격에 맞춰 가장 매끄럽고 자연스러운 발화문으로 정밀 다듬기하세요.

[기준 원본 골든 대본 (Ground Truth Reference)]
- 기준 훅 1 (0~5초): {ref_hook_p1}
- 기준 훅 2 (5~10초): {ref_hook_p2}
- 기준 웹앱 시연 (10~18초): {ref_app}
- 기준 CTA (18~22초): {ref_cta}
- 기준 토론 질문: {ref_debate}

[어조 및 톤앤매너 (절대 준수)]
- 성수/청담동 감성의 세련되고 깔끔한 2030 직장인 대화체 (~하셨던 분들 계시죠?, ~하면 정말 편해요, ~해보셨나요?, ~만나보세요)
- ❌ 10대 인터넷 유행어, 급식체, 과한 은어(스멜, 망삘, 만렙, 튀어, 찐, 삘, 레전드, 개꿀 등) 사용 절대 금지!
- 과장되지 않고 담백하며, 공감 가고 스마트한 딕션 유지

[상황 및 기능 정보]
- 주제: {info['title']} (Aura 앱 기능 #{norm_id})
- 핵심 상황: {info['concept']}
- 실제 앱 시연 화면(10~18초): {info['app_sim_visual']}
- 공식 포털 검색어: {self.OFFICIAL_KEYWORD}

[대본 글자수 절대 규칙 (공백 포함 전체 140~145자 내외 엄수)]
- hook_p1 (0~5초): 세련되게 시선을 사로잡는 2030 현실 소개팅/연애 공감 질문
- hook_p2 (5~10초): 아우라 기능으로 매끄럽게 이어지는 스마트한 해결책 소개
- app_speech (10~18초): 실제 스마트폰 화면에서 벌어지는 상황을 세련되게 설명하는 멘트
- cta_speech (18~22초): 시청자 댓글 참여 질문과 "네이버에 {self.OFFICIAL_KEYWORD} 검색해보세요" 유도
- debate_question: 댓글 창에서 토론을 유도할 센스 있는 10자 내외 질문

★ 핵심 준수 사항: 전체 발화문 합계(hook_p1 + hook_p2 + app_speech + cta_speech)가 반드시 [공백 포함 정확히 140~145자] 내외가 되도록 글자수를 칼같이 맞춰서 작성하세요.

반드시 아래 JSON 포맷으로만 응답하세요:
{{
  "hook_p1": "...",
  "hook_p2": "...",
  "app_speech": "...",
  "cta_speech": "...",
  "debate_question": "..."
}}"""

        if not self.key_chain:
            logger.warning("🔑 [Aura 자율 대본] 유효한 Gemini API 키가 없습니다. 골든 대본으로 폴백합니다.")
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
                            temperature=0.8
                        )
                    )
                    if not resp or not resp.text:
                        continue

                    data = json.loads(resp.text)
                    hook_p1 = data.get("hook_p1", "").strip()
                    hook_p2 = data.get("hook_p2", "").strip()
                    app_speech = data.get("app_speech", "").strip()
                    cta_speech = data.get("cta_speech", "").strip()
                    debate_q = data.get("debate_question", "").strip()

                    # 공식 검색어 포함 검증 (누락 시 자동 보정)
                    if self.OFFICIAL_KEYWORD not in cta_speech:
                        cta_speech = f"{cta_speech} 네이버에 {self.OFFICIAL_KEYWORD} 검색해보세요!"

                    full_speech = f"{hook_p1} {hook_p2} {app_speech} {cta_speech}"

                    # 🔒 무결성 게이트 검증 (목표 140~145자, 안전 허용 범위: 115자 ~ 165자)
                    if len(full_speech) < 115 or len(full_speech) > 165:
                        logger.warning(f"⚠️ 글자 수 범위 벗어남({len(full_speech)}자, 목표: 140~145자), 다음 시도")
                        continue

                    logger.info(f"✨ [Gemini 자율 대본 성공] 주제 #{norm_id} ({len(full_speech)}자, model={model})")
                    return {
                        "hook_p1_5s": hook_p1,
                        "hook_p2_5s": hook_p2,
                        "hook_0_10s": f"{hook_p1} {hook_p2}",
                        "app_10_18s": app_speech,
                        "cta_18_22s": cta_speech,
                        "debate_question": debate_q or "여러분의 생각은 어떠신가요?",
                        "full_speech": full_speech,
                        "is_ai_generated": True
                    }
                except Exception as e:
                    logger.debug(f"Gemini 호출 실패 ({model}): {e}")
                    continue

        logger.warning(f"⚠️ [Aura 대본] 제미나이 호출 모두 실패 ➔ 기존 검증된 골든 대본으로 자동 폴백")
        return None
