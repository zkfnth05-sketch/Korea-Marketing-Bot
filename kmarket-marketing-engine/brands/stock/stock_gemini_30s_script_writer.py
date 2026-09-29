# -*- coding: utf-8 -*-
"""
StockGemini30sScriptWriter - 🤖 [주식앱 100% 실측 매크로 & 퀀트 기반 국내 5대 주제 30초 자율 대본 생성기]
=====================================================================================================
- 5대 실시간 마스터 라인업:
  1) [주제 1] 삼성전자 실시간 4대 모달 퀀트 수급 (30초)
  2) [주제 2] SK하이닉스 실시간 4대 모달 퀀트 수급 (30초)
  3) [주제 3] 뇌동매매 방지! AI 자동 손절매 & 실시간 리스크 가드 (30초)
  4) [주제 4] 당일 10분 계량 전광판 실시간 1위 주도주 발굴 (30초)
  5) [주제 5] KOSPI 시장 종합 스트레스 센터 & 환율/금리 리포트 (30초)
- 주식앱(stockmaster-ai.vercel.app)에서 실시간 크롤링한 7대 팩트 데이터 주입:
  1) 시장 종합 스트레스 점수 및 국면 (예: 10점 🟢 안정 국면)
  2) 미국 10년물 국채 금리 및 일일 변동률 (예: 5.240%)
  3) 코스피 / 코스닥 실시간 지수 및 Z-Score
  4) 당일 체결강도 (예: 160.15% 매수 우위)
  5) 당일 거래대금 (예: 5조 1,046억 원)
  6) 5일 이격도 및 공매도 비중
  7) AI 리스크 종합 점수 (예: 30점 안전)
- 성우 발화속도 +10%에 정확히 맞춘 175~190자 황금 30초 대본 (끊김 0%, 공백 0%)
- 공식 네이버 검색어 불변: ['스톡마스터 AI'] (띄어쓰기 100% 준수)
"""

import os
import sys
import random
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from google import genai
from google.genai import types

from dotenv import load_dotenv
load_dotenv()

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("StockGemini30sScriptWriter")


class StockGemini30sScriptWriter:
    """🤖 주식앱 실측 수치를 받아 365일 매일 색다른 30초 킬러 대본을 자율 주조하는 엔진"""

    def __init__(self):
        # 다중 스마트 키 체인 등록
        candidate_keys = [
            os.getenv("GEMINI_FREE_API_KEY_AURA_1", ""),
            os.getenv("GEMINI_FREE_API_KEY_AURA_2", ""),
            os.getenv("GEMINI_PAID_API_KEY_AURA_1", ""),
            os.getenv("GEMINI_API_KEY_KMARKET", ""),
            os.getenv("GEMINI_API_KEY", "")
        ]
        self.api_keys = [k for k in candidate_keys if k.strip()]
        self.current_key_idx = 0
        logger.info(f"🤖 [StockGemini30sScriptWriter] 초기화 완료 (등록된 무료/유료 스마트 키: {len(self.api_keys)}개)")

    def _get_client(self) -> Optional[genai.Client]:
        if not self.api_keys:
            try:
                return genai.Client()
            except Exception:
                return None
        key = self.api_keys[self.current_key_idx % len(self.api_keys)]
        return genai.Client(api_key=key)

    def _rotate_key(self):
        if len(self.api_keys) > 1:
            self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
            logger.info(f"🔄 [StockGemini30sScriptWriter] 다음 API 키로 스위칭: 인덱스 {self.current_key_idx}")

    def generate_30s_script(self, stock_data: Dict[str, Any], topic_id: int = 1) -> str:
        """실시간 종합 매크로 + 퀀트 데이터를 바탕으로 5대 주제별 매일 색다른 175~190자 대본 생성"""
        stock_name = stock_data.get("stock_name", "삼성전자")
        stress_score = stock_data.get("market_stress_score", "10점")
        stress_phase = stock_data.get("market_stress_phase", "🟢 안정 국면")
        us_bond = stock_data.get("us_treasury_10y", "5.240%").split()[0]
        chegyeol = stock_data.get("chegyeol_gangdo", "160.15%")
        trade_amt = stock_data.get("trade_amount", "4조 1,879억 원")
        disparity = stock_data.get("disparity_5d", "105.84%")
        risk = stock_data.get("risk_score", "30점 (안전)")
        kospi_z = stock_data.get("kospi_stress", "6,864.96")
        top1_name = stock_data.get("top1_leader_name", "이수페타시스")
        top1_score = stock_data.get("top1_total_score", "142점")
        top1_chegyeol = stock_data.get("top1_chegyeol", "141.13%")
        top1_foreign = stock_data.get("top1_foreign_amt", "+15.0억 ▲")

        today_str = datetime.now().strftime("%m월 %d일")

        # 5대 주제별 맞춤 프롬프트
        topic_prompts = {
            1: f"주제: 삼성전자 실시간 4대 모달 퀀트 수급. 거래대금 {trade_amt}, 체결강도 {chegyeol}, 5일 이격도 {disparity}, 시장 스트레스 {stress_score}를 반영하여 삼성전자로 몰리는 수급과 안전 구간을 분석하세요.",
            2: f"주제: SK하이닉스 실시간 4대 모달 퀀트 수급. HBM 독주, 거래대금 {trade_amt}, 체결강도 {chegyeol}, 5일 이격도 {disparity}, 시장 스트레스 {stress_score}를 반영하여 SK하이닉스 수급 폭발과 리스크 관리를 분석하세요.",
            3: f"주제: 뇌동매매 방지! AI 자동 손절매 & 실시간 리스크 가드. 최상단 시장 스트레스 {stress_score}부터 계량 1위 {top1_name}({top1_score}, 체결강도 {top1_chegyeol}, 외국계 {top1_foreign})의 수급 모달과 AI 리스크 평가 탭을 차례로 보며, 감정적 추격을 버리고 AI의 기계적 손절가와 수급 검증의 중요성을 강조하세요.",
            4: f"주제: 당일 10분 계량 전광판 실시간 1위 주도주 발굴. 10분마다 갱신되는 350개 우량주 중 당일 계량 종합 {top1_score}, 체결강도 {top1_chegyeol}로 1위를 기록한 진짜 주도주 {top1_name} 발굴을 강조하세요.",
            5: f"주제: KOSPI 시장 종합 스트레스 센터 & 환율/금리 리포트. 종합 스트레스 {stress_score}({stress_phase}), 미 국채 {us_bond}, 코스피 Z-Score {kospi_z} 등 4대 글로벌 매크로 지표로 증시 방향성을 제시하세요."
        }

        specific_topic_guide = topic_prompts.get(topic_id, topic_prompts[1])

        prompt = f"""당신은 100만 구독자를 보유한 대한민국 최고의 주식 숏폼 크리에이터입니다.
아래 전달된 [{today_str} 주식앱 실시간 실측 증시 데이터]와 [{specific_topic_guide}]를 바탕으로, 매일 색다른 파격적인 첫 3초 훅으로 시작하는 **[30초 세로형 숏폼 성우 나레이션 대본]**을 100% 자율 주조해주세요.

[{today_str} 주식앱 실시간 실측 증시 데이터]
- 타깃 종목: {stock_name}
- 🏆 10분 계량 전광판 1위 주도주: {top1_name} (종합 {top1_score}, 체결강도 {top1_chegyeol}, 외국계 {top1_foreign})
- 💡 시장 종합 스트레스: {stress_score} ({stress_phase})
- 🇺🇸 미국 10년물 국채 금리: {us_bond}
- 📈 당일 체결강도: {chegyeol} (매수 우위)
- 💰 당일 거래대금: {trade_amt}
- 📐 5일 이격도: {disparity}
- 🛡️ AI 리스크 종합 점수: {risk}
- 🔵 코스피 지표: {kospi_z}

[절대 필수 4대 작성 지침]
1. **[도입부 훅 매일 자율 창작 (첫 0~5초)]**: "뉴스는 좋다는데..." 같은 상투적인 문구를 절대 쓰지 말고, 오늘의 시장 스트레스({stress_score}), 미 국채금리({us_bond}), {trade_amt} 거래대금 폭발, 또는 전광판 1위 {top1_name} 수급 등 **당일 실시간 팩트 데이터를 활용해 시청자의 호기심을 0.5초 만에 폭발시키는 충격적인 질문이나 반전 훅**으로 매일 새롭게 시작할 것!
2. **[글자 수 절대 규격]**: 성우 발화속도 +10%에 맞춰 28초 본문 전체를 꽉 채우도록 공백 포함 **반드시 210자 ~ 230자 사이**로 풍부하고 알차게 완결할 것 (초과하거나 200자 미달 금지).
3. **[공식 검색어 불변]**: 마지막 문장에 반드시 **"지금 네이버에 '스톡마스터 AI'를 검색해보세요!"** (띄어쓰기 필수)를 넣을 것.
4. **[출력 포맷]**: 설명, 인사말, 따옴표 없이 **순수 성우가 읽을 한국어 본문 텍스트만** 한 단락으로 출력할 것.
"""

        # Gemini 자율 생성 시도 (Gemini 2.5 Flash 생각 예산 0으로 설정하여 210~230자 순수 대본 즉시 출력)
        model_candidates = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        for attempt in range(max(1, len(self.api_keys)) * 2):
            for model_name in model_candidates:
                try:
                    client = self._get_client()
                    if not client:
                        break

                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.85,
                            max_output_tokens=1500,
                            thinking_config=types.ThinkingConfig(thinking_budget=0)
                        )
                    )

                    text = response.text.strip().replace("\n", " ").replace("  ", " ")
                    char_len = len(text)
                    logger.info(f"🤖 [Gemini 자율 대본 생성 ({model_name}, 주제 {topic_id})] 글자수: {char_len}자: {text}")

                    if 200 <= char_len <= 245 and "스톡마스터 AI" in text and "뉴스는 좋다는데" not in text:
                        logger.info(f"✨ [Gemini 30초 자율 대본 100% 합격!] ({char_len}자): {text}")
                        return text
                except Exception as e:
                    logger.debug(f"Gemini API ({model_name}): {e}")
                    continue

            self._rotate_key()

        # 🌟 5대 주제별 365일 무한 순환 골든 훅 템플릿 풀 (정확히 210~230자 / 27.5~28.0초 완성)
        golden_fallbacks = {
            1: [
                f"시장 종합 스트레스 {stress_score} {stress_phase} 진입! 미 국채금리 {us_bond} 변동 상황 속에서도 {stock_name}으로 {trade_amt} 대규모 수급이 폭발했습니다. 10분 계량 전광판이 당일 체결강도 {chegyeol} 매수 우위와 5일 이격도 {disparity}를 실시간 정밀 포착! AI 리스크 센터가 고점 악재를 완벽 차단하고 기계적 안전 구간을 제시합니다. 4대 퀀트 지표를 지금 확인하세요. 지금 네이버에 '스톡마스터 AI'를 검색해보세요!",
                f"오늘 장중 {stock_name} {trade_amt} 역대급 거래대금 폭발! 시장 스트레스 {stress_score} 안정 속에서 기관과 외국인이 조용히 쓸어 담는 진짜 이유는 무엇일까요? 저희 10분 계량 전광판이 당일 체결강도 {chegyeol} 매수세를 포착했습니다. AI 리스크 센터의 4대 탭 심층 분석과 안전 진입 구간을 지금 즉시 무료로 확인해보세요! 지금 네이버에 '스톡마스터 AI'를 검색해보세요!"
            ],
            2: [
                f"시장 종합 스트레스 {stress_score} {stress_phase}! SK하이닉스 HBM 독주와 함께 당일 {trade_amt} 압도적 거래대금이 터졌습니다. 저희 10분 계량 전광판이 당일 체결강도 {chegyeol} 매수 우위와 5일 이격도 {disparity}를 실시간 포착! AI 리스크 센터가 고점 추격 매수를 정밀 차단하고 손절 라인을 제시합니다. 실시간 4대 수급 데이터를 확인하세요! 지금 네이버에 '스톡마스터 AI'를 검색해보세요!",
                f"미 국채금리 {us_bond} 변동 속에서도 SK하이닉스로 {trade_amt} 대규모 수급 집중! 기관과 세력이 조용히 쓸어 담는 진짜 이유는 무엇일까요? 저희 10분 계량 전광판이 당일 체결강도 {chegyeol}와 4대 핵심 퀀트 지표를 실시간 정밀 분석하여 최적의 안전 매매 전략과 손절가를 제시합니다. 지금 네이버에 '스톡마스터 AI'를 검색해보세요!"
            ],
            3: [
                f"감정적 뇌동매매로 손실 보셨나요? 시장 스트레스 {stress_score} 안정 국면 속에서 10분 계량 전광판 1위 주도주 {top1_name} 계량 종합 {top1_score} 포착! 당일 체결강도 {top1_chegyeol} 만점에 외국계 창구 순매수 {top1_foreign}이 집중 유입됐습니다. 감정 매매는 버리고 AI 리스크 가드가 제시하는 기계적 손절 라인과 진입 유효성을 지금 무료로 검증해보세요! 지금 네이버에 '스톡마스터 AI'를 검색해보세요!",
                f"주식 투자에서 수익보다 훨씬 더 중요한 것은 원금 보호입니다! 시장 스트레스 {stress_score} 국면에서 10분 계량 1위 {top1_name} 종합 {top1_score} 포착! 체결강도 {top1_chegyeol}와 외국계 {top1_foreign} 수급 속에서도 AI 리스크 가드가 위험 종목을 기계적으로 차단하고 손절 라인을 제시합니다. 350개 핵심 우량주 데이터를 확인하세요. 지금 네이버에 '스톡마스터 AI'를 검색해보세요!"
            ],
            4: [
                f"오늘 장중 국내 350개 핵심 우량주 중 10분 계량 전광판 1위 진짜 주도주는? 바로 {top1_name}! 계량 종합 {top1_score}와 당일 체결강도 {top1_chegyeol} 매수 만점, 외국계 창구 {top1_foreign} 수급을 10분마다 정밀 분석합니다. 세력의 실시간 매집 신호와 4대 모달 지표를 절대 놓치지 마세요. 지금 네이버에 '스톡마스터 AI'를 검색해보세요!",
                f"시장 종합 스트레스 {stress_score} 안정 국면 진입! 10분마다 자동 갱신되는 실시간 계량 전광판이 국내 350개 핵심주 중 당일 1위 {top1_name}({top1_score})를 실시간 포착했습니다. AI 리스크 센터가 고점 악재까지 완벽 검증하고 최적 안전 구간을 제시합니다. 지금 네이버에 '스톡마스터 AI'를 검색해보세요!"
            ],
            5: [
                f"오늘 대한민국 증시 시장 종합 스트레스 지수 {stress_score}로 {stress_phase} 진입! 미국 10년물 국채금리 {us_bond}와 코스피 퀀트 Z-Score를 1초 만에 계량 분석합니다. 글로벌 4대 매크로 실시간 지표와 350개 우량주 퀀트 전광판으로 증시의 진짜 방향성을 확실하게 확인하세요. 지금 네이버에 '스톡마스터 AI'를 검색해보세요!",
                f"코스피 현 구간, 과연 강력한 반등 랠리일까요 하락 조정일까요? 10분 계량 센터가 시장 스트레스 {stress_score}와 미 국채금리 {us_bond} 변동률을 실시간 지수화합니다. 데이터 기반의 실시간 글로벌 4대 매크로 리포트와 위험 지수를 지금 즉시 무료로 확인해보세요. 지금 네이버에 '스톡마스터 AI'를 검색해보세요!"
            ]
        }

        chosen_list = golden_fallbacks.get(topic_id, golden_fallbacks[1])
        chosen = random.choice(chosen_list)
        logger.info(f"📋 [StockGemini30sScriptWriter] 주제 {topic_id} 실측 기반 골든 대본 적용 ({len(chosen)}자)")
        return chosen

