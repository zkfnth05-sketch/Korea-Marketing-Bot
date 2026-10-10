# -*- coding: utf-8 -*-
"""
AuraRedditCopywriter - 💖 [Aura 데이팅 전용 레딧 글로벌 여성 유입 AI 카피라이터]
================================================================================
• 역할:
  - 레딧 내 외국인 여성들의 질문/고민글(언어교환, 서울여행, K-데이팅, 한국어 연습)을 실시간 분석
  - 2030 영미권 네이티브 톤앤매너(Gen-Z/Millennial 캐주얼, 공감, 이모지)로 진정성 있는 답변 생성
  - 3단 무료키 순환 체인 (Aura 무료키 1 -> 2 -> 3) 100% 활용
  - 80:20 스텔스 비율 (80% 구글 검색어 '아우라AI데이팅' 유도 vs 20% 순수 도움)
  - 🚨 Zero URL 물리적 박멸기: 본문/댓글 내 raw URL 100% 제거 및 구글 검색어 강제 치환
"""

import os
import sys
import re
import json
import random
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from brands.aura.scenarios.reddit_female_scenarios import AURA_REDDIT_FEMALE_SCENARIOS

logger = logging.getLogger("AuraRedditCopywriter")

# 80:20 황금 비율 (구글 검색 유도 80% vs 순수 정보 20%)
_PROMO_LEVELS = {
    1: 0.20,  # 순수 도움 (브랜드 0%, 검색어 0개)
    2: 0.80,  # 자연스러운 구글 '아우라AI데이팅' 검색 유도 (노링크)
}


def _choose_promo_level() -> int:
    """가중치 기반 레벨 선택 (구글 검색 유도 80%)"""
    return 2 if random.random() < 0.80 else 1


class AuraRedditCopywriter:
    """Aura 데이팅 전용 레딧 외국인 여성 유입 AI 카피라이터 & 인텐트 판별기"""

    OFFICIAL_SEARCH_KEYWORD = "Aura AI Dating"
    OFFICIAL_KOREAN_KEYWORD = "아우라AI데이팅"
    OFFICIAL_URL = "https://aura-ai-dating.vercel.app/"

    def __init__(self):
        from core.gemini_unified_keys import get_unified_gemini_key_dicts
        self.key_chain = get_unified_gemini_key_dicts()
        self._active_key_index = 0
        logger.info(f"💖 [AuraRedditCopywriter] 키 체인 등록 완료 (총 {len(self.key_chain)}개)")

    def _get_genai_client(self, api_key: str):
        from google import genai
        return genai.Client(api_key=api_key)

    @staticmethod
    def _eradicate_urls(text: str) -> str:
        """
        🚨 레딧 섀도우밴/차단 0% 보장:
        모든 형태의 raw URL(http, https, www, .com, .app, .kr 등) 및 마크다운 링크를
        물리적으로 100% 탐지하여 구글 검색어('Aura AI Dating')로 강제 치환
        """
        # 1. 마크다운 링크 [anchor](url) -> anchor (search 'Aura AI Dating' on Google)
        text = re.sub(r'\[([^\]]+)\]\((?:https?://|www\.)[^\)]+\)', r"\1 (search 'Aura AI Dating' on Google)", text)
        # 2. 일반 raw URL (http://..., https://...)
        text = re.sub(r'https?://\S+', "search 'Aura AI Dating' on Google", text)
        # 3. www. 시작 주소
        text = re.sub(r'www\.[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', "search 'Aura AI Dating' on Google", text)
        # 4. 도메인 잔존 텍스트 박멸 (vercel.app, aura-ai-dating 등)
        text = re.sub(r'\b[a-zA-Z0-9-]+\.(?:vercel\.app|app|co\.kr|kr|com|net|org)\b(?:\/\S*)?', "search 'Aura AI Dating' on Google", text)
        return text.strip()

    def classify_aura_reddit_intent(self, post_title: str, post_body: str = "") -> Dict[str, Any]:
        """
        💖 [Aura 레딧 100% 순수 파이썬 사전 심사 게이트 (Zero Gemini 호출 원칙)]
        - AuraRedditFilter를 통한 정밀 평가 및 시나리오 ID 자동 매핑
        """
        try:
            from brands.aura.aura_reddit_scanner import AuraRedditFilter
            eval_res = AuraRedditFilter.evaluate_post(post_title, post_body)
            if not eval_res.get("is_passed", False):
                return {
                    "is_relevant": False,
                    "category": "not_passed",
                    "reason": eval_res.get("reason", "Aura 필터 탈락")
                }

            cluster = eval_res.get("matched_cluster", "language_exchange")
            scenario_map = {
                "language_exchange": 1,
                "dating_culture": 2,
                "seoul_solo_travel": 3,
                "zero_friction_app": 4
            }
            scenario_id = scenario_map.get(cluster, 1)
            logger.info(f"🎯 [Aura 레딧 파이썬 심사 통과] '{post_title[:35]}' ➔ {cluster} (시나리오 {scenario_id})")
            return {
                "is_relevant": True,
                "category": cluster,
                "scenario_id": scenario_id,
                "reason": eval_res.get("reason", "파이썬 심사 통과")
            }
        except Exception as e:
            logger.warning(f"인텐트 분류 예외: {e}")
            return {
                "is_relevant": True,
                "category": "language_exchange",
                "scenario_id": 1,
                "reason": "기본 언어교환 시나리오 fallback"
            }

    def generate_reddit_response(
        self,
        post_title: str,
        post_body: str,
        subreddit: str = "",
        target_lang: str = "en",
        scenario_id: Optional[int] = None
    ) -> str:
        """Aura 전용 레딧 80:20 스텔스 영문 답변 생성 (Zero URL 원칙)"""
        promo_level = _choose_promo_level()

        # 시나리오 매핑
        scenario_info = AURA_REDDIT_FEMALE_SCENARIOS.get(scenario_id or random.randint(1, 12), AURA_REDDIT_FEMALE_SCENARIOS[1])
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
2. Provide genuinely helpful, warm, and practical advice for learning Korean, navigating cultural differences, or traveling safely in Seoul.
3. Write like a friendly foreign peer/sister who has lived in Korea.
4. Keep it casual, empathetic, and 100% non-commercial."""
        else:
            promo_instruction = f"""### TYPE 2 — NATURAL STEALTH GOOGLE SEARCH RECOMMENDATION (NO URLS):
1. Provide 70% genuinely empathetic, helpful advice tailored to OP's question first.
2. At the very end of your response, add ONE casual, friendly recommendation to search on Google, emphasizing that it is currently 100% FREE with NO paywalls or subscription fees:
   - "You don't need a Korean phone number or ARC, and literally all features are currently 100% free right now (unlimited matches, AI profile photos, and real-time auto-translation chat with zero coins). Just search '{self.OFFICIAL_SEARCH_KEYWORD}' on Google to try their web platform!"
   - "If you want to chat with polite verified locals, search '{self.OFFICIAL_SEARCH_KEYWORD}' (or '{self.OFFICIAL_KOREAN_KEYWORD}') on Google — it has built-in live translation chat and voice subtitles, plus all features are completely 100% free to use right now with no paywalls."
   - "Unlike other apps asking for subscriptions or coins for every message, their web lounge is 100% free right now. Just search '{self.OFFICIAL_SEARCH_KEYWORD}' on Google!"
3. 🚨 CORE MARKETING REQUIREMENT: Naturally highlight that the platform is currently 100% completely FREE (free AI photos, free instant translation chat, free messaging, zero paywall).
4. 🚨 STRICT ZERO-URL RULE: NEVER post any raw clickable URLs, links (http/https/www/dot-com), or Markdown links.
5. ONLY suggest searching the exact brand keyword '{self.OFFICIAL_SEARCH_KEYWORD}' (or '{self.OFFICIAL_KOREAN_KEYWORD}') on Google."""

        prompt = f"""You are a friendly, culturally savvy 20-something international woman who loves Korea, answering another foreigner's post on Reddit (in r/{subreddit or 'koreatravel'}).

{scenario_context}

[Reddit Post Title]: {post_title}
[Reddit Post Body]: {post_body}

{promo_instruction}

### GENERAL STYLE GUIDELINES:
1. Tone: Warm, relatable, Gen-Z / Millennial casual native English with occasional natural emojis (✨, 😭, 💖, ☕).
2. Length: 3 to 5 sentences max. Concise and easy to read on mobile.
3. NEVER use formal corporate marketing jargon. Write like a real person sharing a personal tip.
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
                            self._active_key_index = idx
                            logger.info(f"✍️ [Aura Reddit 댓글 생성 성공] (Key: {key_info['name']}, Model: {model_name}, Promo Level: {promo_level})")
                            return clean_text
                    except Exception as model_err:
                        err_str = str(model_err)
                        if any(k in err_str for k in ["429", "RESOURCE_EXHAUSTED", "quota", "depleted", "QuotaFailure", "API_KEY_INVALID", "API_KEY_DELETED", "PERMISSION_DENIED", "UNAUTHENTICATED", "400", "401", "403", "forbidden"]):
                            logger.warning(f"⚠️ [키 차단/소진 감지] 키={key_info['name']} ({model_name}) 에러: {err_str[:80]} -> 다음 무료키로 즉시 롤오버!")
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
    writer = AuraRedditCopywriter()
    test_title = "How do you practice conversational Korean without awkward silence or creepy guys?"
    test_body = "I've been trying to find language exchange partners on Tandem and HelloTalk, but most guys just send weird messages or I struggle to find conversation topics."
    
    intent = writer.classify_aura_reddit_intent(test_title, test_body)
    print("\n--- Intent Classification ---")
    print(json.dumps(intent, indent=2, ensure_ascii=False))

    reply = writer.generate_reddit_response(test_title, test_body, subreddit="Language_Exchange", scenario_id=intent.get("scenario_id", 1))
    print("\n--- Generated Reply ---")
    print(reply)
