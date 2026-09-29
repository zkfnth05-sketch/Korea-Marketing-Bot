# -*- coding: utf-8 -*-
"""
StockShortsScriptWriter - 🤖 [StockMaster AI 8대 주제 100% 순수 자율 창작 제미나이 대본 생성기]
========================================================================================
- 원칙: 'Ground Truth 주입 & 실시간 최적화'
  - 우리가 검증한 8대 골든 대본을 [기준 원본]으로 제미나이 2.5 Flash에 주입
  - 핵심 팩트(실시간 외인/기관 수급, 적정주가, 배당 계산기, 저PBR 스크리너 등)와 실제 기능 플로우 100% 보존
  - 전문 주식/금융 아나운서 어조 및 22초 시간/글자수 규격(10초 립싱크 55~65자 / 12초 앱 시연 75~100자) 정밀 조율
- 3개 무료키 자율 체인 & 100% 무인 무결성 게이트 탑재 (공식 검색어 '스톡마스터 AI' 필수 검증)
- API 오류 시 기존 검증된 골든 대본으로 자동 안전 폴백(Fallback) 보장
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("StockShortsScriptWriter")

# 8대 주제별 '순수 상황 & 기능 정의'
STOCK_8_TOPIC_CONCEPTS: Dict[int, Dict[str, str]] = {
    1: {
        "title": "삼성전자 vs SK하이닉스 HBM 수급 대결",
        "concept": "삼성전자와 SK하이닉스 중 무엇을 매수할지 고민하는 투자자를 위해, 엔비디아 공급망 수급과 외인/기관 순매수 추이 및 퀀트 적정주가를 1초 만에 객관적으로 비교해주는 기능.",
        "app_sim_visual": "삼성전자 및 SK하이닉스 실시간 수급 비교 및 AI 퀀트 적정주가 분석표가 1초 만에 뜨는 화면."
    },
    2: {
        "title": "미국 배당성장 ETF(SCHD·JEPQ) 월 100만원 배당",
        "concept": "매달 통장에 배당금을 받는 제2의 월급을 원하는 투자자를 위해, SCHD와 JEPQ 최적의 배당 비율과 예상 월 수령액을 투자금 입력만으로 1초 만에 시뮬레이션해주는 기능.",
        "app_sim_visual": "배당 계산기에서 투자금 입력 후 SCHD/JEPQ 월별 배당 예상 수령액 그래프가 1초 만에 시뮬레이션되는 화면."
    },
    3: {
        "title": "엔비디아(NVDA) AI 빅테크 실시간 밸류에이션",
        "concept": "엔비디아 및 M7 빅테크 기업의 고점 여부와 밸류에이션이 불안한 투자자를 위해, PER/실적 기반 적정주가와 월가 애널리스트 컨센서스를 1초 만에 분석해주는 기능.",
        "app_sim_visual": "엔비디아 실시간 PER 밸류에이션 및 적정 목표주가 분석 차트가 1초 만에 렌더링되는 화면."
    },
    4: {
        "title": "저PBR 밸류업 & 고배당 금융주 스크리너",
        "concept": "정부 밸류업 정책에 맞춰 어떤 저평가 종목을 사야 할지 모르는 투자자를 위해, PBR 1배 미만 알짜 기업과 주주환원율/배당수익률 순위를 1초 만에 필터링해주는 기능.",
        "app_sim_visual": "저PBR 밸류업 스크리너에서 PBR 1배 미만 알짜 금융/지주사 순위표가 1초 만에 정렬되는 화면."
    },
    5: {
        "title": "뇌동매매 방지! AI 자동 손절매 & 리스크 가드",
        "concept": "급등주 추격매수로 고점에 물리거나 손절 타이밍을 놓치는 개인 투자자를 위해, 변동성을 감지하여 최적의 손절 라인과 익절 목표가를 기계적으로 1초 만에 계산해주는 기능.",
        "app_sim_visual": "종목 변동성 기반 AI 손절선(-3%/-5%) 및 익절 목표가 리스크 매트릭스가 1초 만에 계산되는 화면."
    },
    6: {
        "title": "S&P 500 vs 나스닥 100: 직장인 20년 월적립식 복리",
        "concept": "월급으로 미국 지수 ETF에 적립식 투자하려는 직장인을 위해, 월 적립액 입력만으로 S&P 500과 나스닥 100의 20년 복리 수익 곡선과 미래 예상 자산을 1초 만에 비교해주는 기능.",
        "app_sim_visual": "월 적립식 복리 시뮬레이터에서 20년 자산 성장 곡선 그래프가 1초 만에 비교 렌더링되는 화면."
    },
    7: {
        "title": "외국인·기관 쌍끌이 순매수 실시간 레이더",
        "concept": "개미들만 사고 메이저 세력은 매도하는 종목에 물리지 않도록, 장중 외국인과 기관이 3일 연속 동시 순매수하는 진짜 주도주를 1초 만에 포착해주는 기능.",
        "app_sim_visual": "외국인·기관 쌍끌이 실시간 순매수 상위 종목 레이더 전광판이 1초 만에 실시간 렌더링되는 화면."
    },
    8: {
        "title": "초보 탈출! 원클릭 AI 종목 재무 건전성 진단",
        "concept": "어려운 재무제표를 보기 힘든 초보 투자자를 위해, 영업이익, 부채비율, 현금흐름 3대 지표를 분석해 상폐 위험을 거르고 100점 만점 점수로 1초 만에 진단해주는 기능.",
        "app_sim_visual": "종목명 검색 후 재무 건전성 100점 만점 레이더 차트와 위험도 평가표가 1초 만에 분석되는 화면."
    }
}


class StockShortsScriptWriter:
    """📈 StockMaster AI 8대 주제 전용 제미나이 2.5 Flash 실시간 자율 대본 생성 엔진"""

    OFFICIAL_KEYWORD = "스톡마스터 AI"

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
        핵심 팩트와 웹앱 플로우를 100% 온전히 유지하면서 전문 주식 금융 아나운서 어조/글자수를 최적화한 대본 생성.
        실패 시 None을 반환하여 기존 골든 대본으로 자동 폴백.
        """
        norm_id = ((topic_id - 1) % len(STOCK_8_TOPIC_CONCEPTS)) + 1
        info = STOCK_8_TOPIC_CONCEPTS.get(norm_id, STOCK_8_TOPIC_CONCEPTS[1])

        # 🌟 [우리가 검증한 골든 대본 기준 원본 로드]
        try:
            from core.shorts_engine.stock_shorts_scenario_director import StockShortsScenarioDirector
            golden = StockShortsScenarioDirector.SCRIPTS_22S.get(norm_id, {})
        except Exception:
            golden = {}

        ref_hook_p1 = golden.get("hook_p1_5s", "")
        ref_hook_p2 = golden.get("hook_p2_5s", "")
        ref_app = golden.get("app_10_20s", "")
        ref_hero = golden.get("hero_copy", "실시간 퀀트 데이터 객관적 분석!")
        ref_debate = golden.get("debate_question", "지금 시장의 진짜 주도주는?")

        prompt = f"""당신은 신뢰감 있고 명쾌하며 스마트한 대한민국 주식/금융 퀀트 전문 아나운서입니다.
아래 제공된 [기준 원본 골든 대본]과 앱 기능 정보를 바탕으로, 대한민국 스마트 개미 투자자들이 깊이 공감하고 즉시 행동할 수 있는 22초 숏폼 아나운서 대본을 완성해주세요.

[★ 핵심 원칙 (절대 불변)]
1. 아래 [기준 원본 골든 대본]에 담긴 **스토리 라인, 핵심 팩트(외인/기관 수급 분석, 적정주가, 배당 계산, 저PBR 스크리너 등), 실제 기능 플로우를 100% 온전히 계승**하세요.
2. 특정 종목 매수/매도 권유나 미확인 정보 등 팩트를 왜곡하지 마세요. (심의 100% 프리패스 객관적 퀀트 데이터 강조)
3. [기준 원본 골든 대본]의 뼈대를 바탕으로, 전문 주식 아나운서 어조와 정확한 글자수 규격(10초 훅 / 12초 앱 시연)에 맞춰 가장 매끄럽고 명쾌한 발화문으로 정밀 다듬기하세요.

[기준 원본 골든 대본 (Ground Truth Reference)]
- 기준 훅 1 (0~5초): {ref_hook_p1}
- 기준 훅 2 (5~10초): {ref_hook_p2}
- 기준 웹앱 시연 (10~20초): {ref_app}
- 기준 히어로 카피: {ref_hero}
- 기준 토론 질문: {ref_debate}

[상황 및 기능 정보]
- 주제: {info['title']} (StockMaster AI 기능 #{norm_id})
- 핵심 상황: {info['concept']}
- 실제 앱 시연 화면(10~20초): {info['app_sim_visual']}
- 공식 포털 검색어: {self.OFFICIAL_KEYWORD}

[대본 글자수 절대 규칙 (Wan 2.2 S2V 10초 립싱크 완벽 동기화)]
1. hook_p1 (0~5초): 시선을 사로잡는 현실 주식 투자 공감 질문 [공백 포함 정확히 25~32자]
2. hook_p2 (5~10초): 핵심 팩트와 해결책 제시 [공백 포함 정확히 25~32자]
   ★ 중요: hook_p1과 hook_p2를 합친 전체 훅(0~10초)은 반드시 [공백 포함 55~65자] 내외여야 합니다.
3. app_speech (10~20초): 실제 앱 화면에서 퀀트 데이터 분석/시뮬레이션이 일어나는 상황 설명 [공백 포함 75~100자 (약 8~9초 발화 분량으로 침묵 없이 꽉 차게)]
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

        if not self.key_chain:
            logger.warning("🔑 [Stock 자율 대본] 유효한 Gemini API 키가 없습니다. 골든 대본으로 폴백합니다.")
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

                    # 2) 앱 시연 글자수 검증: 65자 ~ 115자 (12초 앱 시연 음성 공백 방지)
                    if len(app_speech) < 65 or len(app_speech) > 115:
                        logger.warning(f"⚠️ 앱 시연 글자수 범위 벗어남({len(app_speech)}자, 목표: 75~100자), 다음 시도")
                        continue

                    # 3) 전체 글자수 검증: 135자 ~ 195자
                    if len(full_speech) < 135 or len(full_speech) > 195:
                        logger.warning(f"⚠️ 전체 글자수 범위 벗어남({len(full_speech)}자, 목표: 150~185자), 다음 시도")
                        continue

                    logger.info(f"✨ [Gemini 주식 자율 대본 성공] 주제 #{norm_id} (훅:{len(hook_full)}자, 전체:{len(full_speech)}자, model={model})")
                    return {
                        "hook_p1_5s": hook_p1,
                        "hook_p2_5s": hook_p2,
                        "hook_0_10s": hook_full,
                        "app_10_20s": app_speech,
                        "cta_18_22s": cta_speech,
                        "hero_copy": hero_copy or "실시간 퀀트 데이터 객관적 분석!",
                        "debate_question": debate_q or "지금 시장의 진짜 주도주는?",
                        "full_speech": full_speech,
                        "is_ai_generated": True
                    }
                except Exception as e:
                    logger.debug(f"Gemini 호출 실패 ({model}): {e}")
                    continue

        logger.warning(f"⚠️ [주식 대본] 제미나이 호출 모두 실패 ➔ 기존 검증된 골든 대본으로 자동 폴백")
        return None
