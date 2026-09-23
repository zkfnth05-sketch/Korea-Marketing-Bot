# -*- coding: utf-8 -*-
"""
[보험 리밸런스] 네이버 카페 전용 보험 공감 댓글 작성기 (Lego Block)
====================================================================
- 원칙: "파이썬으로 구축해. 제미나이는 답글만 쓰게"
  1. 80% 매달 나가는 고정 보험료/부실 특약 공감 + 20% 자연스러운 보험 리밸런스 추천
  2. 외부 링크(URL) 100% 금지 (순수 오가닉 검색어 유도)
  3. 공식 문구: "네이버에 국내보험 전수 비교 보험 리밸런스 한번 검색해보세요"
  4. 3개 무료키 자율 체인 & 봇 자체 무결성 게이트 탑재
"""

import os
import sys
import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("InsuranceCafeReplyWriter")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class InsuranceCafeReplyWriter:
    """🛡️ 보험 리밸런스 카페 침투 전용 제미나이 감성 댓글 생성기"""

    def __init__(self):
        from config import (
            GEMINI_FREE_API_KEY_AURA_1,
            GEMINI_FREE_API_KEY_AURA_2,
            GEMINI_FREE_API_KEY_AURA_3,
            GEMINI_PAID_API_KEY_AURA_1,
            GEMINI_API_KEY
        )
        candidates = [
            {"name": "INSURE_KEY_1", "key": GEMINI_FREE_API_KEY_AURA_1},
            {"name": "INSURE_KEY_2", "key": GEMINI_FREE_API_KEY_AURA_2},
            {"name": "INSURE_KEY_3", "key": GEMINI_FREE_API_KEY_AURA_3},
            {"name": "INSURE_PAID_1", "key": GEMINI_PAID_API_KEY_AURA_1},
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

        # 1. '보험 리밸런스' 공식 키워드 필수 검증 (띄어쓰기 철저 준수)
        if "보험 리밸런스" not in text:
            return False

        # 2. '검색' 유도 문구 검증
        if "검색" not in text:
            return False

        # 3. 소구점 '전수 비교' 또는 '국내보험' 포함 검증
        if "전수 비교" not in text and "전수비교" not in text:
            return False

        # 4. 문장 끝맺음 무결성 검증 (중간에 뚝 잘린 텍스트 차단)
        clean_end = text.strip()
        valid_ends = (".", "!", "?", "~", "^^", "ㅠㅠ", "ㅜㅜ", "요", "죠", "다", "네", "어", "마요", "세요")
        if not any(clean_end.endswith(ve) for ve in valid_ends):
            return False

        # 5. 불완전 접속사/부사로 끝나는 경우 원천 차단
        truncated_ends = ("근데", "진짜", "그리고", "하지만", "너무", "진짜로", "근데 진짜", "솔직히", "그냥")
        if any(clean_end.endswith(te) for te in truncated_ends):
            return False

        return True

    def generate_sympathy_reply(self, title: str, summary: str = "", cafe_name: str = "") -> str:
        """
        보험 고민글에 대해 80% 공감 + 20% 자연스러운 '보험 리밸런스' 검색 팁 댓글 작성
        (Zero URL 보장, 봇의 100% 자율 검증 및 자동 키 스위칭)
        """
        system_instruction = (
            f"당신은 맘/가계부/재테크 카페('{cafe_name}')에서 활동하는 3040 알뜰한 이웃입니다. "
            "매달 나가는 고정 보험료 부담이나 갱신형/부실 특약으로 속상해하는 글쓴이의 마음에 80% 깊이 공감하고 위로해 주세요. "
            "그리고 자신이 불필요한 특약을 덜어내고 보험료를 크게 줄였던 \"보험 리밸런스\"를 20% 자연스러운 대안으로 언급해 주세요. "
            "절대 특정 설계사 영업처럼 보이지 않아야 하며, 어떠한 외부 URL이나 링크도 넣지 마세요."
        )

        prompt = f"""[사연 제목]: {title}
[사연 내용]: {summary if summary else title}

🚨 [작성 규칙]
1. [공감과 위로 80%]: 사연자의 보험 고민(매달 나가는 보험료 부담, 지인 권유로 가입한 갱신형 후회, 중복 보장 등)에 대해 이웃처럼 따뜻하고 현실적인 위로를 해주세요.
2. [보험 리밸런스 자연스러운 언급 20%]: 마지막 문장에 '저도 쓸데없는 특약 줄이려고 국내보험 전수 비교해주는 "보험 리밸런스"로 리모델링했는데 속이 다 시원하더라고요. 시간 나실 때 네이버에 국내보험 전수 비교 "보험 리밸런스" 한번 검색해보세요' 느낌으로 은근히 언급해 주세요. 사람들이 검색창에 브랜드명을 정확히 콕 집어 입력할 수 있도록 브랜드명에 반드시 큰따옴표("보험 리밸런스")를 붙여주세요.
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
                            text = re.sub(r"https?://\S+", "", text).strip()

                            # 🤖 [봇 자율 무결성 게이트]: 보험 리밸런스 포함 및 완성도 검증
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

        # 백업 응답 (100% 무결점 보장)
        return (
            "매달 나가는 고정 보험료가 은근히 큰 부담인데, 막상 증권 뜯어보면 쓸데없는 특약만 가득해서 속상하셨겠어요. "
            "저도 지인 통해 들었던 거 다 정리하고 국내보험 전수 비교해주는 \"보험 리밸런스\"로 리모델링했더니 월 보험료가 많이 줄어들더라고요. "
            "시간 나실 때 네이버에 국내보험 전수 비교 \"보험 리밸런스\" 한번 검색해보세요, 기운 내세요!"
        )
