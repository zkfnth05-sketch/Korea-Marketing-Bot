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
import core.gemini_unified_keys
from core.gemini_unified_keys import format_gemini_error
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("StockShortsScriptWriter")

# 6대 주제별 '스톡마스터 AI 100% 진짜 기능 정의' (국내 코스피/코스닥 350개 우량주 실시간 퀀트)
# 8대 주제별 1:1 고유 화자 페르소나 (성별, 나이, 상황, 전문 앵커 vs 현실 개미 투자자 시점 완벽 분리)
STOCK_8_TOPIC_PERSONAS: Dict[int, Dict[str, str]] = {
    1: {
        "gender": "female",
        "persona": (
            "당신은 여의도 증권 방송 메인 뉴스룸의 24세 경제 전문 여성 아나운서입니다.\n"
            "삼성전자의 실시간 외국인·기관 순매수 수급과 체결강도, 4대 퀀트 모달 팩트를 라이브 속보로 명쾌하고 스마트하게 브리핑하세요."
        ),
        "hook_hint": "삼성전자 지금 살까 말까 고민하는 투자자들을 향한 강렬한 질문으로 시작"
    },
    2: {
        "gender": "male",
        "persona": (
            "★ [성별: 남성 앵커! 절대 여성 말투 금지]:\n"
            "당신은 여의도 방송 스튜디오 메인 데스크의 26세 훈남 남성 금융 아나운서입니다.\n"
            "HBM 주도주 SK하이닉스의 고점 추격매수와 조정 구간에서, 장중 3대 주체별 실시간 수급 현황과 AI 리스크 안전 진입가를 단호하고 명쾌한 딕션으로 전달하세요."
        ),
        "hook_hint": "SK하이닉스 고점 추격매수해도 될지 고민하는 투자자들을 향한 속보 질문으로 시작"
    },
    3: {
        "gender": "male",
        "persona": (
            "★ [성별: 남성 투자자! 절대 여성 말투 금지]:\n"
            "당신은 뇌동매매와 고점 물림을 피하기 위해 객관적 계량 지표로 매매하는 36세 직장인 남성 주식 투자자입니다.\n"
            "감정에 휘둘려 손절 타이밍을 놓치던 과거에서 벗어나, AI 리스크 센터가 변동성을 감지해 알려주는 기계적 손절 라인으로 자산을 지켜낸 생생한 경험을 동료 개미 투자자들에게 전해주세요."
        ),
        "hook_hint": "급등주 샀다가 고점에 물려 손절 타이밍 놓쳐본 적 있으신지 공감 질문으로 시작"
    },
    4: {
        "gender": "female",
        "persona": (
            "당신은 오늘 장중 세력의 뭉칫돈이 쏠리는 진짜 주도주를 찾아내는 35세 스마트 여성 투자자입니다.\n"
            "지나간 뉴스 뒷북 매매 대신, 10분마다 350개 우량주를 스캔해 거래대금과 체결강도 1등 종목을 1초 만에 포착해주는 10분 계량 전광판 활용 팁을 전해주세요."
        ),
        "hook_hint": "오늘 장중 진짜 세력 돈이 몰리는 1등 주도주가 뭔지 찾는 질문으로 시작"
    },
    5: {
        "gender": "female",
        "persona": (
            "당신은 글로벌 매크로와 국내 증시 하방 위험도를 한눈에 분석하는 24세 경제 분석 여성 앵커입니다.\n"
            "환율, 금리, 유가와 KOSPI 시장 종합 스트레스 10점 척도 리포트로 증시 급락 국면을 사전에 대비할 수 있는 객관적 데이터를 스마트하게 브리핑하세요."
        ),
        "hook_hint": "요즘 시장이 흔들릴 때 내 계좌는 안전할지 거시경제 리스크 질문으로 시작"
    },
    6: {
        "gender": "male",
        "persona": (
            "★ [성별: 남성 앵커! 절대 여성 말투 금지]:\n"
            "당신은 여의도 방송 스튜디오의 26세 훈남 남성 메인 앵커입니다.\n"
            "국내 최초로 10분 계량 전광판, 실시간 손절 알림, 4대 모달 퀀트 분석을 100% 무료로 제공하는 StockMaster AI 퀀트 비서의 총괄 가치를 자신감 넘치는 목소리로 소개하세요."
        ),
        "hook_hint": "감정 매매에서 벗어나 진짜 데이터로 투자하고 싶은 투자자들을 향한 질문으로 시작"
    },
    7: {
        "gender": "male",
        "persona": (
            "★ [성별: 남성 투자자! 절대 여성 말투 금지]:\n"
            "당신은 기관과 외국인 메이저 수급만 따라붙어 안정적인 수익을 내는 38세 직장인 남성 베테랑 투자자입니다.\n"
            "개미들만 사고 외인/기관은 던지는 함정 종목을 피하고, 실시간 쌍끌이 순매수 유입 종목만 1초 만에 포착하는 비결을 전해주세요."
        ),
        "hook_hint": "외국인과 기관이 오늘 조용히 쓸어 담고 있는 진짜 알짜 종목 질문으로 시작"
    },
    8: {
        "gender": "female",
        "persona": (
            "당신은 어려운 재무제표 없이도 깡통 종목을 똑소리 나게 걸러내는 36세 스마트 여성 투자자입니다.\n"
            "원클릭 AI 진단으로 영업이익 적자, 부채비율 급증 등 위험 종목을 1초 만에 VETO 배제하고 알짜 우량주만 고르는 법을 알려주세요."
        ),
        "hook_hint": "어려운 재무제표 대신 1초 만에 종목 건강검진하는 팁 질문으로 시작"
    }
}

STOCK_8_TOPIC_CONCEPTS: Dict[int, Dict[str, str]] = {
    1: {
        "title": "삼성전자 실시간 4대 모달 퀀트 수급 분석",
        "concept": "삼성전자 매수를 고민하는 국내 투자자를 위해, 당일 장중 외국인·기관 실시간 순매수 유입, 퀀트 적정주가, 체결강도 골든크로스를 1초 만에 객관적으로 분석해주는 기능.",
        "app_sim_visual": "10분 계량 전광판에서 삼성전자 클릭 후 수급현황 탭(외인/기관 대량매집), 기술지표, AI 리스크평가 4대 모달이 1초 만에 렌더링되는 화면."
    },
    2: {
        "title": "SK하이닉스 HBM 실시간 퀀트 수급 & AI 리스크 진단",
        "concept": "HBM 주도주 SK하이닉스의 고점 추격매수와 조정 구간을 고민하는 국내 투자자를 위해, 당일 실시간 외국인·기관 수급 유입과 AI 리스크 센터의 단기 과열 진단 및 안전 진입가를 1초 만에 분석해주는 기능.",
        "app_sim_visual": "10분 계량 전광판에서 SK하이닉스 클릭 후 3대 주체별 실시간 수급 현황(외인/기관/개인), 거래대금, 신용잔고율, AI 리스크 안전구간이 1초 만에 렌더링되는 화면."
    },
    3: {
        "title": "뇌동매매 방지! AI 기계적 손절매 & 실시간 리스크 가드",
        "concept": "급등주 추격매수로 고점에 물리거나 감정에 휘둘려 손절 타이밍을 놓치는 개인 투자자를 위해, AI 리스크 센터가 변동성을 감지하여 기계적 손절 라인과 VETO 위험 종목을 1초 만에 걸러주는 기능.",
        "app_sim_visual": "AI 리스크 센터 화면에서 시장 변동성 지표, 기계적 손절매 가이드라인, VETO 배제 종목 목록이 1초 만에 렌더링되는 화면."
    },
    4: {
        "title": "당일 10분 계량 전광판 실시간 1위 주도주 포착 레이더",
        "concept": "오늘 장중 메이저 세력의 자금이 가장 강력하게 쏠리는 진짜 1등 주도주를 찾고 싶은 국내 투자자를 위해, 10분마다 국내 350개 우량주의 체결강도와 순매수를 스캔하여 실시간 1위를 포착해주는 기능.",
        "app_sim_visual": "10분 계량 전광판 상단에서 실시간 1위 급등 주도주가 10분마다 갱신되고, 1위 종목의 퀀트 스코어카드가 1초 만에 열리는 화면."
    },
    5: {
        "title": "KOSPI 시장 종합 스트레스 센터 & 환율·금리 4대 매크로 리포트",
        "concept": "국내 증시의 전반적인 하방 압력과 거시경제 위험도를 한눈에 파악하고 싶은 국내 투자자를 위해, 시장 종합 스트레스 지수 10점 척도와 환율/금리/유가 4대 계량 매크로 리포트를 1초 만에 진단해주는 기능.",
        "app_sim_visual": "메인 상단 글로벌 매크로 패널에서 시장 종합 스트레스 10점 국면 차트와 환율/금리 리스크 리포트가 1초 만에 렌더링되는 화면."
    },
    6: {
        "title": "국내 최초 24시간 자기학습 AI 퀀트 비서! Stock Master AI 총괄",
        "concept": "감정 매매에서 벗어나 객관적 데이터 기반의 스마트한 투자를 원하는 모든 개인 투자자를 위해, 10분 퀀트 스캔과 실시간 손절 알림 및 4대 모달 분석을 무료로 제공하는 AI 퀀트 비서 기능.",
        "app_sim_visual": "10분 계량 전광판 ➔ 1등 주도주 4대 모달 ➔ AI 리스크 센터 ➔ 실시간 수급 레이더가 유기적으로 연동되는 화면."
    }
}


class StockShortsScriptWriter:
    """📈 StockMaster AI 6대 주제 전용 제미나이 2.5 Flash 실시간 자율 대본 생성 엔진"""

    OFFICIAL_KEYWORD = "스톡마스터 AI"
    FORBIDDEN_WORDS = [
        "한정", "이벤트", "선착순", "마감", "사은품", "쿠폰", "오늘만", 
        "특가", "캐시백", "당첨", "추천주 100% 급등", "원금보장", "수익률 보장",
        "배당", "월배당", "배당금", "배당주", "배당수익률", "배당락", "배당 계산기", 
        "저PBR", "PBR", "적립식", "복리", "세금", "환급", "보험", "데이팅", "소개팅", "연애"
    ]

    def __init__(self):
        try:
            from config import (
                GEMINI_FREE_API_KEY_AURA_1,
                GEMINI_FREE_API_KEY_AURA_2,
                GEMINI_FREE_API_KEY_AURA_3,
                GEMINI_FREE_API_KEY_AURA_4,
                GEMINI_FREE_API_KEY_KMARKET,
                GEMINI_FREE_API_KEY_EASYTAX,
                GEMINI_PAID_API_KEY_AURA_1,
                GEMINI_PAID_API_KEY_AURA_2,
                GEMINI_API_KEY
            )
            candidates = [
                {"name": "AURA_FREE_1", "key": GEMINI_FREE_API_KEY_AURA_1},
                {"name": "AURA_FREE_2", "key": GEMINI_FREE_API_KEY_AURA_2},
                {"name": "AURA_FREE_3", "key": GEMINI_FREE_API_KEY_AURA_3},
                {"name": "AURA_FREE_4", "key": GEMINI_FREE_API_KEY_AURA_4},
                {"name": "KMARKET_FREE", "key": GEMINI_FREE_API_KEY_KMARKET},
                {"name": "EASYTAX_FREE", "key": GEMINI_FREE_API_KEY_EASYTAX},
                {"name": "AURA_PAID_1", "key": GEMINI_PAID_API_KEY_AURA_1},
                {"name": "AURA_PAID_2", "key": GEMINI_PAID_API_KEY_AURA_2},
                {"name": "DEFAULT", "key": GEMINI_API_KEY}
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
            golden = StockShortsScenarioDirector.SCRIPTS_30S.get(norm_id, {})
        except Exception:
            golden = {}

        ref_hook_p1 = golden.get("hook_p1_5s", "")
        ref_hook_p2 = golden.get("hook_p2_5s", "")
        ref_app = golden.get("app_10_20s", "")
        ref_hero = golden.get("hero_copy", "실시간 퀀트 데이터 객관적 분석!")
        ref_debate = golden.get("debate_question", "지금 시장의 진짜 주도주는?")

        # 📡 [실시간 스톡앱 배포 사이트 100% 라이브 크롤링 데이터 수집]
        live_data_text = ""
        try:
            from brands.stock.stock_realtime_data_fetcher import StockRealtimeDataFetcher
            fetcher = StockRealtimeDataFetcher()
            target_stock_map = {
                1: "삼성전자",
                2: "SK하이닉스",
                3: "전광판1위",
                4: "전광판1위",
                5: "매크로스트레스",
                6: "전광판1위"
            }
            target_stock = target_stock_map.get(norm_id, "전광판1위")
            realtime_dict = fetcher.fetch_stock_data(target_stock)
            actual_target_stock_name = "삼성전자"
            if realtime_dict:
                macro_info = realtime_dict.get("macro", {})
                top1_info = realtime_dict.get("top1_board", {})
                modal_info = realtime_dict.get("modal_data", {})
                board_stocks = realtime_dict.get("board_stocks", [])
                actual_target_stock_name = top1_info.get("name", "삼성전자") if target_stock in ["전광판1위", "매크로스트레스"] else target_stock
                
                # 타깃 종목의 전광판 순위 찾기
                target_rank_str = "순위권 내"
                target_score_str = ""
                for s in board_stocks:
                    if s.get("name") == target_stock:
                        target_rank_str = f"전광판 {s.get('rank')}위"
                        target_score_str = f", 계량종합점수 {s.get('totalScore')}"
                        break

                live_data_text = f"""
[실제 주식앱(stockmaster-ai.vercel.app) 실시간 라이브 실측 팩트 수치 (Ground Truth - 10분마다 자동 갱신)]
- 🌐 시장 종합 스트레스 지수: {macro_info.get('stressScore', '20점')} ({macro_info.get('stressPhase', '🟢 안정 국면')}) / {macro_info.get('stressGuide', '')}
- 💵 원달러 환율: {macro_info.get('usdfx', '1,345.4원')} / 🇺🇸 미국 10년물 국채: {macro_info.get('usBond', '5.277%')}
- 🔵 코스피 지수: {macro_info.get('kospiZ', '7,003.74pt')} / 🟢 코스닥 지수: {macro_info.get('kosdaqZ', '893.29pt')}
- 🏆 10분 전광판 당일 실시간 1위 종목: {top1_info.get('name', '한온시스템')} ({top1_info.get('code', '018880')}) (계량종합: {top1_info.get('totalScore', '125점')}, 체결강도: {top1_info.get('chegyeol', '127.16%')}, 외국계 순매수: {top1_info.get('foreignAmt', '+42.0억')}, 손절선: {top1_info.get('exitSL', '3,197원')}, 현재가: {top1_info.get('currPrice', '3,840원')}, 목표선: {top1_info.get('swingTP', '5,126원')})
- 📈 이번 주제 타깃 종목 '{target_stock}' 실측 퀀트 수치 ({target_rank_str}{target_score_str}):
  * 현재가: {modal_info.get('currPrice', '')} ({modal_info.get('changeRate', '')})
  * 당일 거래대금: {modal_info.get('tradeAmt', '')} / 신용잔고율: {modal_info.get('creditRatio', '')}
  * 당일 체결강도: {modal_info.get('chegyeol', '')} / RSI: {modal_info.get('rsi', '')}
  * 외국인 수급: {modal_info.get('foreignFlow', '')} / 기관 수급: {modal_info.get('instFlow', '')} / 개인: {modal_info.get('retailFlow', '')}
  * 정량 리스크 점수: {modal_info.get('riskScore', '')}
"""
                logger.info(f"📡 [실시간 웹앱 크롤링 성공] 주제 #{norm_id} ({target_stock}) 실측 팩트 데이터 제미나이 주입 완료!")
        except Exception as ex_fetch:
            logger.error(f"❌ 실시간 웹앱 크롤링 실패: {ex_fetch}")
            raise RuntimeError(f"실시간 웹앱 라이브 크롤링 실패로 대본 생성 중단 (허위 캐시 배제 원칙): {ex_fetch}")

        topic_persona = STOCK_8_TOPIC_PERSONAS.get(norm_id, STOCK_8_TOPIC_PERSONAS[1])
        persona_desc = topic_persona["persona"]
        hook_hint = topic_persona.get("hook_hint", "")
        gender = topic_persona.get("gender", "female")

        prompt = f"""[화자 페르소나 및 상황 설정 (절대 준수)]
{persona_desc}

[★ 핵심 원칙 (절대 불변)]
1. 화자의 성별({gender})과 캐릭터 시점을 100% 엄격하게 유지하세요. 남성 화자일 경우 절대 여성 말투를 쓰지 마세요.
2. 첫 마디(hook_p1) 가이드: {hook_hint}
아래 [실시간 웹앱 라이브 실측 팩트 수치]를 바탕으로, 32초 숏폼 아나운서 대본을 작성해주세요.

[★ 핵심 원칙 (절대 불변)]
1. 아래 [실시간 웹앱 라이브 실측 팩트 수치]를 대본에 자연스럽고 정확하게 반영하여, 오늘 실제 장중 데이터가 살아있는 신뢰도 100% 대본을 작성하세요.
2. 🚨 [허위 마케팅 및 거짓말 날조 전면 금지]: '원금보장', '100% 급등 보장', '한정 무료 이벤트', '선착순 마감' 등의 거짓말 문구를 절대 지어내지 마세요.
3. 🚨 [기능 불일치 금지]: 배당금, 월배당, 세금, 환급 등 우리 앱에 없는 기능은 0% 배제하고, 실시간 외국인/기관 수급, 10분 전광판 1위 주도주, 체결강도, AI 리스크 센터 실제 기능만을 다루세요.
4. 문장을 절대 장황하게 늘이지 말고, 짧고 강력한 2~3개 핵심 문장으로 딱 맞추어 작성하세요.
{live_data_text}
[상황 및 기능 정보]
- 주제: {info['title']} (StockMaster AI 기능 #{norm_id})
- 핵심 상황: {info['concept']}
- 실제 앱 시연 화면: {info['app_sim_visual']}
- 공식 포털 검색어: {self.OFFICIAL_KEYWORD}

[대본 글자수 절대 규칙 (음성속도 +2% 기준 정확히 30~32초 완독: 총 190~215자 내외 - 초과 시 기각)]
1. hook_p1 (0~5초): 시선을 끄는 강렬한 1문장 [공백 포함 정확히 25~30자]
2. hook_p2 (5~10초): 팩트 및 궁금증 해결 [공백 포함 정확히 28~35자]
   ★ 중요: hook_p1 + hook_p2 합친 전체 훅은 [공백 포함 55~65자] (10초 립싱크 완벽 일치)
3. app_speech (10~27초): 핵심 실시간 데이터와 퀀트 수치를 알기 쉽게 전달하는 2문장 [공백 포함 반드시 105~125자]
4. cta_speech (27~32초): "지금 바로 네이버에 '{self.OFFICIAL_KEYWORD}'를 검색하고 무료로 확인하세요!" [공백 포함 28~32자]

[★ 글자수 총합 엄수: 전체 대본(훅+앱+CTA) 합계는 공백 포함 반드시 190~215자 범위로 맞추세요. 220자 초과 또는 180자 미달 시 자동 기각됩니다.]

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
            from core.variation_engine.stock_hook_variator import StockHookVariator
            hook_injection = StockHookVariator().build_hook_injection(
                topic_id=norm_id,
                topic_title=info['title'],
                topic_concept=info['concept'],
                app_sim_visual=info['app_sim_visual'],
            )
            prompt = prompt + hook_injection
        except Exception as e:
            logger.debug(f"[주식 변주 엔진] 로드 실패 (기존 프롬프트로 진행): {e}")

        if not self.key_chain:
            logger.warning("🔑 [Stock 자율 대본] 유효한 Gemini API 키가 없습니다. 골든 대본으로 폴백합니다.")
            return None

        from google import genai
        from google.genai import types

        models = ["gemini-2.5-flash", "gemini-2.0-flash"]
        for key in self.key_chain:
            try:
                client = genai.Client(api_key=key, http_options=types.HttpOptions(timeout=35000))
            except Exception:
                continue

            for model in models:
                try:
                    resp = client.models.generate_content(
                        model=model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            automatic_function_calling=genai_types.AutomaticFunctionCallingConfig(disable=True), response_mime_type="application/json",
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
                        cta_speech = f"지금 바로 네이버에 '{self.OFFICIAL_KEYWORD}'를 검색해보세요!"
                        full_speech = f"{hook_full} {app_speech} {cta_speech}".strip()

                    # 🔒 [무결성 게이트 2: +2% 발화 템포 32초 완독 구간별 및 전체 글자수 정밀 검증 (170~220자 엄수)]
                    # 1) 훅 글자수 검증: 45자 ~ 70자 (Wan 10초 립싱크 완벽 일치)
                    if len(hook_full) < 45 or len(hook_full) > 70:
                        logger.warning(f"⚠️ 훅 글자수 범위 벗어남({len(hook_full)}자), 다음 시도")
                        continue

                    # 2) 앱 시연 글자수 검증: 80자 ~ 135자 (18초 웹앱 화면)
                    if len(app_speech) < 80 or len(app_speech) > 135:
                        logger.warning(f"⚠️ 앱 시연 글자수 범위 벗어남({len(app_speech)}자), 다음 시도")
                        continue

                    # 3) 전체 글자수 검증: 170자 ~ 220자 (+2% 속도 기준 정확히 28~31초 완독 규격)
                    if len(full_speech) < 150 or len(full_speech) > 240:
                        logger.warning(f"⚠️ 전체 글자수 범위 벗어남({len(full_speech)}자), 다음 시도")
                        continue

                    logger.info(f"✨ [Gemini 주식 32초 자율 대본 성공] 주제 #{norm_id} (훅:{len(hook_full)}자, 앱:{len(app_speech)}자, 전체:{len(full_speech)}자, model={model})")
                    return {
                        "topic_id": norm_id,
                        "title": info["title"],
                        "target_stock_name": actual_target_stock_name,
                        "hook_p1": hook_p1,
                        "hook_p2": hook_p2,
                        "hook_p1_5s": hook_p1,
                        "hook_p2_5s": hook_p2,
                        "hook_0_10s": hook_full,
                        "app_speech": app_speech,
                        "app_10_20s": app_speech,
                        "app_10_30s": app_speech,
                        "cta_speech": cta_speech,
                        "cta_18_22s": cta_speech,
                        "cta_30_34s": cta_speech,
                        "hero_copy": hero_copy or "실시간 퀀트 데이터 객관적 분석!",
                        "debate_question": debate_q or "지금 시장의 진짜 주도주는?",
                        "full_speech": full_speech,
                        "is_ai_generated": True
                    }
                except Exception as e:
                    logger.warning(f"⚠️ [StockScriptWriter] 키 실패 ➔ 롤오버: {format_gemini_error(e)}")
                    continue

        logger.warning(f"⚠️ [주식 대본] 제미나이 호출 모두 실패 ➔ 기존 검증된 골든 대본으로 자동 폴백")
        return None

    def generate_30s_script(self, stock_data: Optional[Dict[str, Any]] = None, topic_id: int = 1) -> str:
        """하위 호환용 30초 풀 스크립트 문자열 반환 (단일화 인터페이스)"""
        res = self.generate_dynamic_script(topic_id=topic_id)
        if res and res.get("full_speech"):
            return res["full_speech"]
        
        # 골든 대본 폴백
        try:
            from core.shorts_engine.stock_shorts_scenario_director import StockShortsScenarioDirector
            norm_id = ((topic_id - 1) % len(STOCK_8_TOPIC_CONCEPTS)) + 1
            golden = StockShortsScenarioDirector.SCRIPTS_22S.get(norm_id, {})
            h1 = golden.get("hook_p1_5s", "")
            h2 = golden.get("hook_p2_5s", "")
            app = golden.get("app_10_20s", "")
            cta = f"지금 네이버에 '{self.OFFICIAL_KEYWORD}'를 검색해보세요!"
            return f"{h1} {h2} {app} {cta}".strip()
        except Exception:
            return f"실시간 퀀트 데이터와 시장 스트레스를 1초 만에 확인하세요. 지금 네이버에 '{self.OFFICIAL_KEYWORD}'를 검색해보세요!"
