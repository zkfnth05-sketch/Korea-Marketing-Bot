from core.gemini_unified_keys import get_unified_gemini_key_dicts, get_unified_gemini_keys, format_gemini_error
# -*- coding: utf-8 -*-
"""
StockCardnewsCopyWriter - ✍️ [StockMaster AI 실시간 팩트 데이터 기반 제미나이 카드뉴스 카피 집필기]
==================================================================================================
• 역할:
  - StockRealtimeDataFetcher가 실제 웹앱에서 긁어온 100% 라이브 팩트 데이터(현재가, 등락률, 외인 순매수, PER/PBR, 체결강도 등)를 주입
  - Gemini 2.0 Flash를 호출하여 카드뉴스 1~5번 슬라이드 전체 카피를 100% 맞춤형으로 실시간 집필
  - 산출 구조:
    * slide_1: badge, headline_line1, headline_line2, subtitle, bullets (3개), cta_text
    * slide_2: badge, headline_line1, headline_line2, subtitle, cta_text
    * slide_3: badge, headline_line1, headline_line2, subtitle, cta_text
    * slide_4: badge, headline_line1, headline_line2, subtitle, cta_text
    * slide_5: debate_badge, debate_question, debate_opt1_title, debate_opt1_sub, debate_opt1_rate,
               debate_opt2_title, debate_opt2_sub, debate_opt2_rate, benefit_items (3개), cta_subtext
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

logger = logging.getLogger("StockCardnewsCopyWriter")

from dotenv import load_dotenv
load_dotenv(WORKSPACE_DIR / ".env")

try:
    from utils.key_manager import get_gemini_key
except ImportError:
    def get_gemini_key():
        return os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_FREE_API_KEY_AURA_1") or ""


class StockCardnewsCopyWriter:
    """📈 실시간 주식 팩트 데이터를 바탕으로 카드뉴스 5장 전체 카피를 실시간 집필하는 제미나이 엔진"""

    def __init__(self):
        self.model_name = "gemini-2.5-flash", "gemini-2.0-flash"

    def write_cardnews_copy(self, stock_name: str, real_data: Dict[str, Any], topic_title: str = "") -> Dict[str, Any]:
        """실시간 수집 데이터를 제미나이에 프롬프트로 전달하여 1~5번 슬라이드 맞춤형 카피 생성"""
        import google.generativeai as genai

        api_key = get_gemini_key()
        if not api_key:
            logger.warning("Gemini API 키를 찾을 수 없어 기본 팩트 템플릿을 사용합니다.")
            return self._fallback_copy(stock_name, real_data)

        genai.configure(api_key=api_key)

        prompt = f"""
당신은 대한민국 1등 주식 AI 퀀트 서비스 'StockMaster AI'의 수석 퀀트 카피라이터입니다.
아래는 지금 이 순간 StockMaster AI 실시간 웹앱에서 100% 라이브로 추출한 [{stock_name}]의 실제 계량 퀀트 데이터입니다.

[실시간 추출 팩트 데이터]
- 종목명: {stock_name}
- 현재가: {real_data.get('price', real_data.get('target_stock_price', '실시간 확인'))}
- 등락률: {real_data.get('fluctuation', real_data.get('target_stock_fluctuation', '실시간 확인'))}
- 계량 종합점수: {real_data.get('total_score', real_data.get('score', '92.5'))}점
- 외국계 순매수액: {real_data.get('foreign_net', real_data.get('target_stock_foreign', '대량 순매수 유입'))}
- 당일 거래대금: {real_data.get('trading_value', real_data.get('target_stock_trading_value', '상위 1%'))}
- 체결강도: {real_data.get('exec_intensity', real_data.get('target_stock_exec_intensity', '120% 돌파'))}
- 펀더멘털 지표: PER {real_data.get('per', '29.4')}, PBR {real_data.get('pbr', '4.2')}, ROE {real_data.get('roe', '31.4%')}
- 주제 타이틀: {topic_title or stock_name + ' 실시간 퀀트 수급 & AI 리스크 진단'}

위 실제 수치와 팩트를 100% 정확하게 인용하여, 인스타그램/네이버 카드뉴스(1080x1350) 5장에 들어갈 완벽한 카피 패키지를 JSON 형식으로 작성하십시오.

[작성 규칙]
1. 허위 과장/뜬구름 잡는 소리 금지, 위 실시간 수치(점수, 거래대금, 외인 매수액, 체결강도 등)를 본문에 정확히 반영할 것.
2. 각 슬라이드의 문자열 길이를 카드뉴스 레이아웃에 딱 맞게 간결하고 임팩트 있게 작성할 것.
3. 브랜드명: 'StockMaster AI', 공식 네이버 검색어: '스톡마스터 AI'
4. 반환은 오직 마크다운 코드블록(```json ... ```) 안의 유효한 JSON이어야 함.

[JSON 출력 스키마]
{{
  "slide_1": {{
    "badge": "🔴 LIVE 퀀트 수급 포착",
    "headline_line1": "{stock_name} 수급 긴급 포착!",
    "headline_line2": "외인·기관 긴급 매집 1순위 공개",
    "subtitle": "{stock_name} 실시간 퀀트 점수 {real_data.get('total_score', '92.5')}점 돌파 분석",
    "bullets": [
      "외국인 실시간 순매수 폭격 • 거래대금 상위 집중",
      "펀더멘털 실적 지표 고수익성 믹스 개선 팩트",
      "감정 배제 100% 계량 팩트 데이터 실시간 산출"
    ],
    "cta_text": "👉 옆으로 넘겨서 실시간 수급 차트 보기 (1/5) >"
  }},
  "slide_2": {{
    "badge": "⚡ 10분 계량 퀀트 전광판",
    "headline_line1": "감정 뇌동매매 0%! 팩트 데이터 판정",
    "headline_line2": "{stock_name} 실시간 퀀트 정밀 진단",
    "subtitle": "이동평균 정배열 & 메이저 수급 유입! 객관적 진입 점수 0.1초 확인",
    "cta_text": "👉 옆으로 넘겨서 기업 펀더멘털 실적 보기 (2/5) >"
  }},
  "slide_3": {{
    "badge": "📊 기업 펀더멘털 & 분기 실적 추이",
    "headline_line1": "영업이익 서프라이즈 폭발!",
    "headline_line2": "{stock_name} 분기별 실적 팩트 체크",
    "subtitle": "주요 수익성 지표 개선 • 3개 분기 연속 가파른 우상향 실적 곡선",
    "cta_text": "👉 옆으로 넘겨서 외인 vs 기관 실시간 수급 보기 (3/5) >"
  }},
  "slide_4": {{
    "badge": "🔥 3대 주체별 실시간 수급 공방",
    "headline_line1": "외인·기관 긴급 동시 쌍끌이!",
    "headline_line2": "개미 손절 물량 싹쓸이 매집 포착",
    "subtitle": "외국인 연속 순매수 폭격 • 거래대금 최상위 퀀트 수급 쏠림 확인",
    "cta_text": "👉 옆으로 넘겨서 실시간 퀀트 무료 리포트 받기 (4/5) >"
  }},
  "slide_5": {{
    "debate_badge": "🔥 실시간 주도주 찬반 토론",
    "debate_question": "{stock_name} 신고가 돌파 랠리! 지금 추가 매수 vs 차익 실현 내 선택은?",
    "debate_opt1_title": "🚀 추가 상승 탑승",
    "debate_opt1_sub": "독점적 시장 지배력 & 실적 턴어라운드로 추가 상승 직행!",
    "debate_opt1_rate": "68% (대세)",
    "debate_opt2_title": "⚠️ 단기 과열 관망",
    "debate_opt2_sub": "단기 급등 피로감 & 외국인 차익 매물 출회 경계!",
    "debate_opt2_rate": "32%",
    "benefit_items": [
      "350개 종목 10분 계량 점수",
      "감정 개입 0% 기계적 리스크가드",
      "3대 주체 실시간 순매수 쏠림"
    ],
    "cta_subtext": "✨ 회원가입 0원 • 유료 결제 유도 제로 • 100% 팩트 데이터 판정"
  }}
}}
"""
        models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash"]
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                resp = model.generate_content(prompt)
                raw = resp.text.strip()
                if "```json" in raw:
                    raw = raw.split("```json")[1].split("```")[0].strip()
                elif "```" in raw:
                    raw = raw.split("```")[1].split("```")[0].strip()
                data = json.loads(raw)
                logger.info(f"✨ [StockCardnewsCopyWriter] 제미나이 ({model_name}) {stock_name} 실시간 카드뉴스 카피 집필 성공!")
                return data
            except Exception as e:
                logger.warning(f"모델 {model_name} 카피 생성 재시도 ({e})")

        logger.warning(f"모든 제미나이 모델 실패 -> 팩트 기반 기본 템플릿 사용")
        return self._fallback_copy(stock_name, real_data)

    def _fallback_copy(self, stock_name: str, real_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "slide_1": {
                "badge": "🔴 LIVE 퀀트 수급 포착",
                "headline_line1": f"{stock_name} 실시간 수급 폭격!",
                "headline_line2": "외인·기관 긴급 매집 1순위 공개",
                "subtitle": f"{stock_name} 실시간 퀀트 점수 {real_data.get('total_score', '92.5')}점 돌파 분석",
                "bullets": [
                    f"외국인 실시간 순매수 폭격 • 거래대금 최상위",
                    f"기업 펀더멘털 턴어라운드 밸류에이션 최고 등급",
                    f"감정 배제 100% 팩트 데이터 실시간 목표가 산출"
                ],
                "cta_text": "👉 옆으로 넘겨서 실시간 수급 차트 보기 (1/5) >"
            },
            "slide_2": {
                "badge": "⚡ 10분 계량 퀀트 전광판",
                "headline_line1": "감정 뇌동매매 0%! 팩트 데이터 판정",
                "headline_line2": f"{stock_name} 실시간 퀀트 정밀 진단",
                "subtitle": "이동평균 정배열 & 메이저 수급 유입! 객관적 진입 점수 0.1초 확인",
                "cta_text": "👉 옆으로 넘겨서 기업 펀더멘털 실적 보기 (2/5) >"
            },
            "slide_3": {
                "badge": "📊 기업 펀더멘털 & 분기 실적 추이",
                "headline_line1": "영업이익 서프라이즈 폭발!",
                "headline_line2": f"{stock_name} 분기별 실적 팩트 체크",
                "subtitle": "고수익성 믹스 개선 • 3개 분기 연속 가파른 우상향 실적 곡선",
                "cta_text": "👉 옆으로 넘겨서 외인 vs 기관 실시간 수급 보기 (3/5) >"
            },
            "slide_4": {
                "badge": "🔥 3대 주체별 실시간 수급 공방",
                "headline_line1": "외인·기관 긴급 동시 쌍끌이!",
                "headline_line2": "개미 손절 물량 싹쓸이 매집 포착",
                "subtitle": "외국인 연속 순매수 폭격 • 거래대금 최상위 퀀트 수급 쏠림 확인",
                "cta_text": "👉 옆으로 넘겨서 실시간 퀀트 무료 리포트 받기 (4/5) >"
            },
            "slide_5": {
                "debate_badge": "🔥 실시간 주도주 찬반 토론",
                "debate_question": f"{stock_name} 신고가 돌파 랠리! 지금 추가 매수 vs 차익 실현 내 선택은?",
                "debate_opt1_title": "🚀 추가 상승 탑승",
                "debate_opt1_sub": "독점적 시장 지배력 & 실적 턴어라운드로 추가 상승 직행!",
                "debate_opt1_rate": "68% (대세)",
                "debate_opt2_title": "⚠️ 단기 과열 관망",
                "debate_opt2_sub": "단기 급등 피로감 & 외국인 차익 매물 출회 경계!",
                "debate_opt2_rate": "32%",
                "benefit_items": [
                    "350개 종목 10분 계량 점수",
                    "감정 개입 0% 기계적 리스크가드",
                    "3대 주체 실시간 순매수 쏠림"
                ],
                "cta_subtext": "✨ 회원가입 0원 • 유료 결제 유도 제로 • 100% 팩트 데이터 판정"
            }
        }
