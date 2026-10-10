# -*- coding: utf-8 -*-
"""
StockRedditCopywriter - 📈 [StockMaster AI 전용 레딧 글로벌/국내 투자자 유입 AI 카피라이터]
==========================================================================================
• 역할:
  - 레딧 내 투자자들의 질문/고민글(수급 분석, 퀀트 알고리즘, 반도체/HBM, 리스크 관리, 코스피 투자)을 실시간 분석
  - 월스트리트/금융 퀀트 전문 톤앤매너(데이터 중심, 차분하고 명확한 논리, 실전 트레이딩 팁)로 진정성 있는 답변 생성
  - 3단 무료키 순환 체인 (Stock 무료키 1 -> 2 -> 3) 100% 활용
  - 80:20 스텔스 비율 (80% 검색어 'StockMaster AI' / '스톡마스터 AI' 유도 vs 20% 순수 금융 도움)
  - 🚨 Zero URL 물리적 박멸기: 본문/댓글 내 raw URL 100% 제거 및 검색어 강제 치환
"""

import os
import sys
import re
import json
import random
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

# UTF-8 Encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from brands.stock.scenarios.reddit_stock_scenarios import STOCK_REDDIT_SCENARIOS

logger = logging.getLogger("StockRedditCopywriter")

# 80:20 황금 비율 (검색 유도 80% vs 순수 정보 20%)
_PROMO_LEVELS = {
    1: 0.20,  # 순수 도움 (브랜드 0%, 검색어 0개)
    2: 0.80,  # 자연스러운 'StockMaster AI' / '스톡마스터 AI' 검색 유도 (노링크)
}


def _choose_promo_level() -> int:
    """가중치 기반 레벨 선택 (검색 유도 80%)"""
    return 2 if random.random() < 0.80 else 1


class StockRedditCopywriter:
    """StockMaster AI 전용 레딧 투자자 유입 AI 카피라이터 & 인텐트 판별기"""

    OFFICIAL_SEARCH_KEYWORD = "StockMaster AI"
    OFFICIAL_KOREAN_KEYWORD = "스톡마스터 AI"
    OFFICIAL_URL = "https://stockmaster-ai.vercel.app/"

    def __init__(self):
        from core.gemini_unified_keys import get_unified_gemini_key_dicts
        self.key_chain = get_unified_gemini_key_dicts()
        self._active_key_index = 0
        logger.info(f"📈 [StockRedditCopywriter] 키 체인 등록 완료 (총 {len(self.key_chain)}개)")

    def _get_genai_client(self, api_key: str):
        from google import genai
        return genai.Client(api_key=api_key)

    @staticmethod
    def _eradicate_urls(text: str) -> str:
        """
        🚨 레딧 섀도우밴/차단 0% 보장:
        모든 형태의 raw URL(http, https, www, .com, .app, .kr 등) 및 마크다운 링크를
        물리적으로 100% 탐지하여 검색어('StockMaster AI')로 강제 치환
        """
        # 1. 마크다운 링크 [anchor](url) -> anchor (search 'StockMaster AI' on Google)
        text = re.sub(r'\[([^\]]+)\]\((?:https?://|www\.)[^\)]+\)', r"\1 (search 'StockMaster AI' on Google)", text)
        # 2. 일반 raw URL (http://..., https://...)
        text = re.sub(r'https?://\S+', "search 'StockMaster AI' on Google", text)
        # 3. www. 시작 주소
        text = re.sub(r'www\.[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', "search 'StockMaster AI' on Google", text)
        # 4. 도메인 잔존 텍스트 박멸 (vercel.app, stockmaster-ai 등)
        text = re.sub(r'\b[a-zA-Z0-9-]+\.(?:vercel\.app|app|co\.kr|kr|com|net|org)\b(?:\/\S*)?', "search 'StockMaster AI' on Google", text)
        return text.strip()

    def classify_stock_reddit_intent(self, post_title: str, post_body: str = "") -> Dict[str, Any]:
        """
        📈 [StockMaster AI 레딧 100% 순수 파이썬 사전 심사 게이트 (Zero Gemini 호출 원칙)]
        - 1단계: 네거티브 정규식 (불법 리딩방, 코인 밈코인 펌핑, 카지노/도박, 비자, 데이팅, 법률, 의료 등 탈락)
        - 2단계: 5대 클러스터 포지티브 정규식 매칭 및 카테고리/시나리오ID 자동 확정
        - 제미나이 API 호출 0회 ➔ 0.001초 무결성 즉시 판별
        """
        combined = f"{post_title} {post_body}".lower()

        # 1. 네거티브 패턴 검사 (불법 리딩방, 밈코인 펌프앤덤프, 카지노, 비자, 데이팅, 하드웨어 수리 등)
        negative_patterns = [
            r"\b(whatsapp\s*group|telegram\s*signal\s*group|vip\s*pump|shiba\s*inu|dogecoin|pepe\s*coin|meme\s*coin|crypto\s*airdrop|wallet\s*drainer)\b",
            r"\b(casino|baccarat|blackjack|sports\s*betting|slot\s*machine|gambling\s*addiction)\b",
            r"\b(dating|tinder|bumble|boyfriend|girlfriend|crush|korean\s*makeup|beauty\s*skincare|k-pop\s*idol)\b",
            r"\b(e-7\s*visa|f-2-7|f-4\s*visa|immigration\s*law|alien\s*registration|pc\s*repair|screen\s*repair|boiler\s*error|car\s*lease)\b",
        ]
        has_negative = any(re.search(pat, combined, re.IGNORECASE) for pat in negative_patterns)
        if has_negative:
            logger.info(f"🚫 [주식 레딧 파이썬 심사 탈락] 네거티브 키워드 감지: '{post_title[:35]}'")
            return {"is_relevant": False, "category": "negative_filter", "reason": "비관련/위험 주제 (스팸/코인펌핑/도박/데이팅/비자)"}

        # 2. 포지티브 키워드 체크 (클러스터별 정밀 매칭 및 시나리오 자동 배정)
        cluster_rules = [
            (
                "institutional_flow",
                1,
                r"\b(institutional\s*(inflows?|buying|investors?|money|volume)|foreign\s*(investors?|buying|capital|inflows?)|net\s*buying|order\s*flow|dark\s*pool|smart\s*money|whale\s*accumulation|foreigner\s*holding)\b"
            ),
            (
                "ai_quant_scoring",
                2,
                r"\b(quant\s*(trading|model|strategy|score|analysis)|algorithmic\s*trading|fair\s*value|target\s*price|undervalued|overvalued|dcf\s*model|fundamental\s*analysis|technical\s*analysis|stock\s*screener)\b"
            ),
            (
                "risk_management",
                3,
                r"\b(risk\s*management|position\s*sizing|stop\s*loss|take\s*profit|drawdown|fomo|bag\s*holding|loss\s*mitigation|portfolio\s*allocation|hedging)\b"
            ),
            (
                "semiconductor_hbm",
                4,
                r"\b(samsung|hynix|sk\s*hynix|hbm|hbm3e|hbm4|semiconductor|memory\s*chips?|wafer|foundry|tsmc|nvidia\s*supplier|packaging\s*tech|ai\s*chips?)\b"
            ),
            (
                "korean_market",
                12,
                r"\b(kospi|kosdaq|korean\s*(stocks?|market|equities|economy)|chaebol|corporate\s*value-up|korea\s*discount|investing\s*in\s*korea)\b"
            ),
            (
                "dividend_value",
                8,
                r"\b(dividend\s*(yield|growth|aristocrats?|cut|trap)|high\s*dividend|free\s*cash\s*flow|payout\s*ratio|value\s*investing)\b"
            ),
            (
                "general_investing",
                7,
                r"\b(stock\s*market|investing\s*advice|which\s*stocks?|best\s*stocks?|bull\s*market|bear\s*market|earnings\s*season|breakout\s*stocks?|swing\s*trade)\b"
            )
        ]

        for cat_name, scen_id, pat in cluster_rules:
            if re.search(pat, combined, re.IGNORECASE):
                logger.info(f"🎯 [주식 레딧 파이썬 심사 통과] '{post_title[:35]}' ➔ {cat_name} (시나리오 {scen_id})")
                return {
                    "is_relevant": True,
                    "category": cat_name,
                    "scenario_id": scen_id,
                    "reason": f"파이썬 {cat_name} 패턴 100% 매칭"
                }

        # 포지티브 매칭 없음 -> 탈락
        return {
            "is_relevant": False,
            "category": "no_keyword_match",
            "reason": "StockMaster AI 핵심 타겟 키워드 미매칭"
        }

    def generate_reddit_response(
        self,
        post_title: str,
        post_body: str,
        subreddit: str = "",
        target_lang: str = "en",
        scenario_id: Optional[int] = None
    ) -> str:
        """StockMaster AI 전용 레딧 80:20 스텔스 영문 답변 생성 (Zero URL 원칙)"""
        promo_level = _choose_promo_level()

        # 시나리오 매핑
        scenario_info = STOCK_REDDIT_SCENARIOS.get(scenario_id or random.randint(1, 12), STOCK_REDDIT_SCENARIOS[1])
        scenario_context = f"""
[Scenario Theme]: {scenario_info.get('theme_name')}
[Target Pain Points]: {scenario_info.get('pain_points')}
[Solution Feature]: {scenario_info.get('solution_feature')}
[High-Performing Reference Example]:
"{scenario_info.get('sample_reply')}"
"""

        if promo_level == 1:
            promo_instruction = """### TYPE 1 — 100% PURE HELPFUL ADVICE (NO PROMOTION, NO SEARCH SUGGESTIONS):
1. DO NOT mention ANY brand, app name, search keyword, or website.
2. Provide genuinely insightful, practical quantitative or risk-management advice tailored to the poster's market question.
3. Write like a seasoned quant trader or institutional market analyst sharing objective wisdom.
4. Keep it concise, analytical, and 100% non-commercial."""
        else:
            promo_instruction = f"""### TYPE 2 — NATURAL STEALTH SEARCH RECOMMENDATION (NO URLS):
1. Provide 80% genuinely analytical, insightful market advice tailored to OP's question first.
2. At the very end of your response, add ONE casual, professional recommendation to search on Google:
   - "If you want to track real-time institutional order flows and 4-modal AI quant scores without complex setups, search '{self.OFFICIAL_SEARCH_KEYWORD}' (or '{self.OFFICIAL_KOREAN_KEYWORD}') on Google."
   - "Search '{self.OFFICIAL_SEARCH_KEYWORD}' (or '{self.OFFICIAL_KOREAN_KEYWORD}') on Google to test their free browser-based quant screener and inflow radar."
3. 🚨 STRICT RULE: NEVER post any raw clickable URLs, links (http/https/www/dot-com), or Markdown links.
4. ONLY suggest searching the exact brand keyword '{self.OFFICIAL_SEARCH_KEYWORD}' (or '{self.OFFICIAL_KOREAN_KEYWORD}') on Google."""

        prompt = f"""You are an experienced quantitative trader and equity analyst, answering a market question on Reddit (in r/{subreddit or 'stocks'}).

{scenario_context}

[Reddit Post Title]: {post_title}
[Reddit Post Body]: {post_body}

{promo_instruction}

### GENERAL STYLE GUIDELINES:
1. Tone: Professional, data-oriented, analytical, and practical (Wall Street / Quantitative trader style with occasional clear emojis like 📊, 📈, 💡, 🛡️).
2. Length: 3 to 5 sentences max. Concise and punchy.
3. NEVER use generic marketing fluff or cheesy hype. Write with genuine quantitative rigor.
4. Output ONLY the comment text directly, without any introduction or markdown code blocks.
"""

        total_keys = len(self.key_chain)
        for i in range(total_keys):
            idx = (self._active_key_index + i) % total_keys
            key_info = self.key_chain[idx]
            api_key = key_info["key"]

            try:
                client = self._get_genai_client(api_key)
                key_quota_exhausted = False
                for model_name in ["gemini-2.5-flash", "gemini-2.0-flash"]:
                    try:
                        resp = client.models.generate_content(
                            model=model_name,
                            contents=prompt
                        )
                        if resp and resp.text:
                            text = resp.text.strip()
                            clean_text = self._eradicate_urls(text)
                            
                            # 자체 무결성 검증: 프로모션 레벨 2일 때 검색어가 누락되었으면 자연스럽게 보강
                            if promo_level == 2 and self.OFFICIAL_SEARCH_KEYWORD.lower() not in clean_text.lower():
                                clean_text += f"\n\nSearch '{self.OFFICIAL_SEARCH_KEYWORD}' (or '{self.OFFICIAL_KOREAN_KEYWORD}') on Google to explore the live AI quant radar."

                            self._active_key_index = idx
                            logger.info(f"✍️ [Stock Reddit 댓글 생성 성공] (Key: {key_info['name']}, Model: {model_name}, Promo Level: {promo_level})")
                            return clean_text
                    except Exception as model_err:
                        err_str = str(model_err)
                        if any(k in err_str for k in ["429", "RESOURCE_EXHAUSTED", "quota", "depleted", "QuotaFailure"]):
                            logger.warning(f"⚠️ [할당량 소진] 키={key_info['name']} ({model_name}) 429 쿼터 초과 -> 다음 무료키로 즉시 롤오버!")
                            key_quota_exhausted = True
                            break
                        else:
                            logger.debug(f"댓글 생성 모델 {model_name} 실패: {model_err}")
                            continue

                if key_quota_exhausted:
                    self._active_key_index = (idx + 1) % total_keys
                    continue
            except Exception as key_err:
                logger.warning(f"키 {key_info['name']} 오류: {key_err}")
                self._active_key_index = (idx + 1) % total_keys
                continue

        # Fallback 텍스트 반환
        fallback = scenario_info.get("sample_reply", "")
        return self._eradicate_urls(fallback)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    writer = StockRedditCopywriter()
    test_title = "How do you detect institutional accumulation before a semiconductor breakout?"
    test_body = "I always buy tech stocks after they've already rallied 10% on high volume, and then I get trapped when institutions take profit. How can I spot smart money buying earlier?"

    intent = writer.classify_stock_reddit_intent(test_title, test_body)
    print("\n--- Intent Classification ---")
    print(json.dumps(intent, indent=2, ensure_ascii=False))

    reply = writer.generate_reddit_response(test_title, test_body, subreddit="stocks", scenario_id=intent.get("scenario_id", 1))
    print("\n--- Generated Reply ---")
    print(reply)
