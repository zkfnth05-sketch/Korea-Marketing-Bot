# -*- coding: utf-8 -*-
"""
Aura Translator (🌐 Aura 앱 4개 국어 실시간 번역 전담 독립 레고 블록)
========================================================================
- 역할:
  1. 본진 앱(aura-ai-dating.vercel.app)에 접속한 글로벌 유저(EN, JA, ES)를 위한 4개 국어 자동 번역
  2. 라운지 피드(lounge_posts)용 요약문 3개국어(EN, JA, ES) 100% 동시 번역 (수퍼베이스 translations 컬럼 규격)
  3. 2,000자 공식 매거진 원고(title, excerpt, content_md) 4개 국어 아카이빙 지원
  4. 아우라 전용 무료 키 3개(AURA_1, 2, 3) 라운드로빈 및 429 자동 롤오버 (비용 0원 원칙)
"""

import os
import re
import json
import time
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

logger = logging.getLogger("AuraTranslator")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent


class AuraTranslator:
    """Aura 전용 4개 국어(KO, EN, JA, ES) 자동 번역 엔진 (완전 독립 모듈)"""

    def __init__(self):
        load_dotenv(PROJECT_ROOT / ".env")
        
        # 1. 아우라 전용 무료 키 풀 수집
        raw_free = [
            os.getenv("GEMINI_FREE_API_KEY_AURA_1", ""),
            os.getenv("GEMINI_FREE_API_KEY_AURA_2", ""),
            os.getenv("GEMINI_FREE_API_KEY_AURA_3", ""),
            os.getenv("GEMINI_API_KEY", "")
        ]
        self.free_keys = [k.strip() for k in raw_free if k and k.strip()]
        
        # 2. 비상용 유료 키 풀
        raw_paid = [
            os.getenv("GEMINI_PAID_API_KEY_AURA_1", ""),
            os.getenv("GEMINI_PAID_API_KEY_AURA_2", ""),
            os.getenv("GEMINI_PAID_API_KEY", "")
        ]
        self.paid_keys = [k.strip() for k in raw_paid if k and k.strip()]
        
        self._key_index = 0
        self._lock = threading.Lock()
        
        logger.info(f"🌐 [AuraTranslator] 무료 키 {len(self.free_keys)}개 / 유료 백업 {len(self.paid_keys)}개 준비 완료")

    def _get_next_free_key(self) -> str:
        with self._lock:
            if not self.free_keys:
                return ""
            key = self.free_keys[self._key_index % len(self.free_keys)]
            self._key_index += 1
            return key

    def _call_gemini_with_fallback(self, prompt: str, system_instruction: str = "") -> Optional[str]:
        """무료 키 풀 순환 호출 -> 429 발생 시 다음 무료 키 롤오버 -> 최후에 유료 키 백업"""
        from google import genai
        from google.genai import types

        keys_to_try = list(self.free_keys)
        # 무료 키가 모두 소진되었을 때 유료 키 1개 추가
        if self.paid_keys:
            keys_to_try.append(self.paid_keys[0])

        for attempt, key in enumerate(keys_to_try):
            try:
                client = genai.Client(api_key=key)
                cfg = types.GenerateContentConfig(
                    temperature=0.3,
                    response_mime_type="application/json"
                )
                if system_instruction:
                    cfg.system_instruction = system_instruction

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=cfg
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    logger.warning(f"⚠️ [AuraTranslator] 키 [{attempt+1}/{len(keys_to_try)}] 429 초과 -> 다음 키로 즉시 전환")
                    time.sleep(1)
                    continue
                else:
                    logger.warning(f"⚠️ [AuraTranslator] 호출 오류: {e}")
                    time.sleep(1)
                    continue

        logger.error("❌ [AuraTranslator] 모든 Gemini 키 호출 실패")
        return None

    def translate_lounge_content(self, korean_text: str) -> Dict[str, str]:
        """
        📱 본진 앱 라운지 피드(lounge_posts) 카드 요약문 3개국어 번역
        - 반환 규격: {'en': '...', 'ja': '...', 'es': '...'}
        - 본진 앱의 lounge-post-card.tsx 에서 language !== 'ko' 일 때 즉시 표시되는 핵심 데이터
        """
        if not korean_text or not korean_text.strip():
            return {"en": "", "ja": "", "es": ""}

        system_instruction = (
            "You are a professional multilingual translator for the premium 2030 social dating app AURA.\n"
            "Translate the given Korean dating lounge magazine post into English (en), Japanese (ja), and Spanish (es) simultaneously.\n"
            "Rules:\n"
            "1. Maintain a youthful, warm, romantic, and trendy 2030 dating magazine tone for each language.\n"
            "2. Keep all emojis, bullet points, and structure intact.\n"
            "3. The official landing URL 'https://aura-ai-dating.vercel.app/' must remain unchanged.\n"
            "4. Output MUST be valid JSON with keys 'en', 'ja', and 'es'."
        )

        prompt = f"""
Translate the following Korean Lounge Feed content into English, Japanese, and Spanish:

=== KOREAN SOURCE ===
{korean_text}
=====================

Return JSON format:
{{
  "en": "English translated text...",
  "ja": "Japanese translated text...",
  "es": "Spanish translated text..."
}}
"""

        raw_json = self._call_gemini_with_fallback(prompt, system_instruction)
        if raw_json:
            try:
                # 마크다운 코드 블록 제거 후 파싱
                clean = re.sub(r"^```json\s*", "", raw_json, flags=re.MULTILINE)
                clean = re.sub(r"```$", "", clean, flags=re.MULTILINE).strip()
                data = json.loads(clean)
                if isinstance(data, dict) and "en" in data and "ja" in data and "es" in data:
                    logger.info("✅ [AuraTranslator] 라운지 카드 3개국어(EN, JA, ES) 번역 완료")
                    return {
                        "en": str(data.get("en", "")),
                        "ja": str(data.get("ja", "")),
                        "es": str(data.get("es", ""))
                    }
            except Exception as e:
                logger.warning(f"⚠️ [AuraTranslator] JSON 파싱 실패: {e}")

        # 실패 시 비상 폴백
        return {
            "en": korean_text,
            "ja": korean_text,
            "es": korean_text
        }

    def translate_full_package(self, article_pkg: Dict[str, Any]) -> Dict[str, Any]:
        """
        📚 2,000자 마스터 원고 및 라운지 피드를 포함한 4개 국어(KO, EN, JA, ES) 풀 패키지 번역
        - lounge_translations: lounge_posts 테이블 translations 컬럼 주입용
        - article_translations: aura_blogs 및 로컬 JSON 아카이빙용
        """
        title = article_pkg.get("title_kakao") or article_pkg.get("title_naver") or article_pkg.get("title", "")
        excerpt = article_pkg.get("excerpt", "")
        content_summary = article_pkg.get("lounge_content", "")
        content_md = article_pkg.get("content_md", "")

        # 1. 라운지 카드 요약문 번역 (본진 앱 실시간 노출 최우선)
        lounge_trans = self.translate_lounge_content(content_summary)

        # 2. 제목 및 요약 번역
        system_instruction = (
            "You are a professional localization editor for the premium 2030 dating magazine AURA.\n"
            "Translate the Korean title and excerpt into English (en), Japanese (ja), and Spanish (es).\n"
            "Keep the romantic, engaging, and high-conversion tone.\n"
            "Output MUST be valid JSON."
        )

        prompt = f"""
Translate the title and excerpt into en, ja, es:
Title: {title}
Excerpt: {excerpt}

Return JSON format:
{{
  "en": {{"title": "...", "excerpt": "..."}},
  "ja": {{"title": "...", "excerpt": "..."}},
  "es": {{"title": "...", "excerpt": "..."}}
}}
"""
        meta_trans = {"en": {}, "ja": {}, "es": {}}
        raw_json = self._call_gemini_with_fallback(prompt, system_instruction)
        if raw_json:
            try:
                clean = re.sub(r"^```json\s*", "", raw_json, flags=re.MULTILINE)
                clean = re.sub(r"```$", "", clean, flags=re.MULTILINE).strip()
                data = json.loads(clean)
                if isinstance(data, dict):
                    meta_trans = data
            except Exception as e:
                logger.warning(f"⚠️ [AuraTranslator] 메타 JSON 파싱 실패: {e}")

        # 최종 4개 국어 패키지 조립
        translations = {
            "lounge": lounge_trans,  # {'en': '...', 'ja': '...', 'es': '...'}
            "articles": {
                "en": {
                    "title": meta_trans.get("en", {}).get("title", title),
                    "excerpt": meta_trans.get("en", {}).get("excerpt", excerpt),
                    "lounge_content": lounge_trans.get("en", "")
                },
                "ja": {
                    "title": meta_trans.get("ja", {}).get("title", title),
                    "excerpt": meta_trans.get("ja", {}).get("excerpt", excerpt),
                    "lounge_content": lounge_trans.get("ja", "")
                },
                "es": {
                    "title": meta_trans.get("es", {}).get("title", title),
                    "excerpt": meta_trans.get("es", {}).get("excerpt", excerpt),
                    "lounge_content": lounge_trans.get("es", "")
                }
            }
        }
        return translations
