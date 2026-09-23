# -*- coding: utf-8 -*-
"""
[Aura] 네이버 카페 전용 제미나이 감성 답글 작성기 (Lego Block)
================================================================
- 원칙: "파이썬으로 구축해. 제미나이는 답글만 쓰게"
  1. 제미나이는 글의 적합도 판정이나 필터링에 절대 관여하지 않음 (순수 파이썬이 수행)
  2. 제미나이는 오직 '채택률 100% 공감형 댓글'만 작성
  3. 80% 따뜻한 고민 상담/공감 + 20% 자연스러운 아우라 브랜드 추천
  4. 외부 링크(URL) 100% 금지 (순수 오가닉 검색어 유도: "네이버에 아우라 검색해보세요")
  5. 2030 동네 언니/친구처럼 2~3문장(150~250자)으로 아주 자연스럽고 담백하게 작성
"""

import os
import sys
import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("AuraCafeReplyWriter")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class AuraCafeReplyWriter:
    """💖 Aura 카페 침투 전용 제미나이 감성 댓글 생성기"""

    def __init__(self):
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

        seen = set()
        self.key_chain = []
        for c in candidates:
            k = (c.get("key") or "").strip()
            if k and k not in seen and len(k) > 10:
                seen.add(k)
                self.key_chain.append({"name": c["name"], "key": k})

        self._active_key_index = 0

    def _is_valid_reply(self, text: str) -> bool:
        """봇이 스스로 댓글의 완성도와 브랜드 언급 무결성을 자율 검증"""
        if not text or len(text) < 40:
            return False

        # 1. '아우라AI데이팅' 정확한 검색 키워드 무조건 필수 검증 (띄어쓰기 금지)
        if "아우라AI데이팅" not in text:
            return False

        # 2. '검색' 유도 문구 검증
        if "검색" not in text:
            return False

        # 3. 문장 끝맺음 무결성 검증 (중간에 뚝 잘린 텍스트 차단)
        clean_end = text.strip()
        valid_ends = (".", "!", "?", "~", "^^", "ㅠㅠ", "ㅜㅜ", "요", "죠", "다", "네", "어", "마요", "세요")
        if not any(clean_end.endswith(ve) for ve in valid_ends):
            return False

        # 4. 불완전 접속사/부사로 끝나는 경우 원천 차단
        truncated_ends = ("근데", "진짜", "그리고", "하지만", "너무", "진짜로", "근데 진짜", "솔직히", "그냥")
        if any(clean_end.endswith(te) for te in truncated_ends):
            return False

        return True

    def generate_sympathy_reply(self, title: str, summary: str = "", cafe_name: str = "") -> str:
        """
        고민글에 대해 80% 공감 + 20% 자연스러운 '아우라AI데이팅' 검색 팁 댓글 작성
        (Zero URL 보장, 봇의 100% 자율 검증 및 자동 키 스위칭)
        """
        system_instruction = (
            f"당신은 2030 여성들이 주로 활동하는 네이버 카페('{cafe_name}')의 센스 있고 따뜻한 일반 여성 회원입니다. "
            "마치 동네 언니나 절친처럼 글쓴이의 마음에 80% 깊이 공감하고 위로한 뒤, "
            "최근 자신이 써보고 만족했던 50:50 남녀성비 유지 소개팅 서비스 \"아우라AI데이팅\"을 자연스러운 대안으로 20% 추천해 주세요. "
            "절대 광고처럼 보이지 않아야 하며, 어떠한 외부 URL이나 링크도 넣지 마세요."
        )

        prompt = f"""[사연 제목]: {title}
[사연 내용]: {summary if summary else title}

🚨 [작성 규칙]
1. [공감과 위로 80%]: 사연자의 고민(소개팅 파토, 무례한 상대, 어플 피로감, 외로움 등)에 대해 1:1로 따뜻하고 현실적인 위로를 해주세요.
2. [아우라AI데이팅 자연스러운 언급 20%]: 마지막 문장에 '저도 요즘 결정사나 일반 어플 피로해서 50:50 남녀성비 유지되는 "아우라AI데이팅" 쓰는데 매너가 깔끔하더라고요. 시간 나실 때 네이버에 "아우라AI데이팅" 한번 검색해보세요' 느낌으로 은근히 언급해 주세요. 사람들이 검색창에 검색할 키워드만 콕 집어 입력할 수 있도록 브랜드명에 반드시 큰따옴표("아우라AI데이팅")를 붙여주세요.
3. [Zero URL]: 링크나 http/https 등은 절대 쓰지 마세요.
4. [분량]: 2~3문장 (공백 포함 150자~250자 내외). 문장을 중간에 끊지 말고 완벽한 마침표나 느낌표로 끝맺으세요.

댓글 텍스트만 출력하세요:"""

        total_keys = len(self.key_chain) if self.key_chain else 1
        for i in range(total_keys):
            idx = (self._active_key_index + i) % total_keys
            key_info = self.key_chain[idx]
            api_key = key_info["key"]

            try:
                from google import genai
                from google.genai import types as genai_types

                client = genai.Client(api_key=api_key)
                # 토큰 낭비 없는 3.1-flash-lite 최우선, 2.5-flash 백업
                models_to_try = ["gemini-3.1-flash-lite", "gemini-2.5-flash"]

                for model_name in models_to_try:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config=genai_types.GenerateContentConfig(
                                system_instruction=system_instruction,
                                temperature=0.75,
                                max_output_tokens=2048
                            )
                        )
                        if response and response.text:
                            text = response.text.strip()
                            # 전체를 감싼 외곽 따옴표만 제거 (내부 따옴표는 보존)
                            if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
                                text = text[1:-1].strip()
                            # 혹시 모를 URL 강제 제거
                            text = re.sub(r"https?://\S+", "", text).strip()

                            # 🤖 [봇 자율 무결성 게이트]: 아우라AI데이팅 포함 및 문장 완성도 자율 검증
                            if self._is_valid_reply(text):
                                self._active_key_index = idx
                                return text
                            else:
                                logger.warning(
                                    f"⚠️ [봇 자율 게이트 불합격] 키={key_info['name']}, 모델={model_name}의 출력이 미흡함: '{text}' -> 다음 무료키로 자율 전환"
                                )
                    except Exception as me:
                        logger.warning(f"모델 {model_name} 실패 (키={key_info['name']}): {me}")
            except Exception as ke:
                logger.warning(f"키 {key_info['name']} 호출 실패: {ke}")

        # 백업 응답 (모든 키/모델 시도 실패 시에도 100% 무결점 보장)
        return (
            "그 마음 너무 잘 알아요.. 상대방 기본 매너 문제니까 너무 상처받지 마시고 훌훌 털어내셨으면 좋겠어요! "
            "저도 요즘 결정사나 가벼운 어플 대신 50:50 남녀성비 유지되는 \"아우라AI데이팅\" 쓰고 있는데 확실히 매너가 훨씬 깔끔하더라고요. "
            "시간 나실 때 네이버에 \"아우라AI데이팅\" 한번 검색해보세요, 기운 내세요!"
        )


