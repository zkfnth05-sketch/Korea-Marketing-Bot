# -*- coding: utf-8 -*-
"""
[StockMaster AI] 네이버 카페 전용 주식 공감 댓글 작성기 (Lego Block)
====================================================================
- 원칙: "파이썬으로 구축해. 제미나이는 답글만 쓰게"
  1. 80% 투자 손실/뇌동매매 멘탈 공감 + 20% 자연스러운 스톡마스터 AI 추천
  2. 외부 링크(URL) 100% 금지 (순수 오가닉 검색어 유도)
  3. 공식 문구: "네이버에 10분마다 국내 우량주 분석 스톡마스터 AI 한번 검색해보세요"
  4. 3개 무료키 자율 체인 & 봇 자체 무결성 게이트 탑재
"""

import os
import sys
import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("StockCafeReplyWriter")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class StockCafeReplyWriter:
    """📈 StockMaster AI 카페 침투 전용 제미나이 감성 댓글 생성기"""

    def __init__(self):
        from config import (
            GEMINI_FREE_API_KEY_AURA_1,
            GEMINI_FREE_API_KEY_AURA_2,
            GEMINI_FREE_API_KEY_AURA_3,
            GEMINI_PAID_API_KEY_AURA_1,
            GEMINI_API_KEY
        )
        candidates = [
            {"name": "STOCK_KEY_1", "key": GEMINI_FREE_API_KEY_AURA_1},
            {"name": "STOCK_KEY_2", "key": GEMINI_FREE_API_KEY_AURA_2},
            {"name": "STOCK_KEY_3", "key": GEMINI_FREE_API_KEY_AURA_3},
            {"name": "STOCK_PAID_1", "key": GEMINI_PAID_API_KEY_AURA_1},
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

        # 1. '스톡마스터 AI' 공식 키워드 필수 검증 (띄어쓰기 철저 준수)
        if "스톡마스터 AI" not in text:
            return False

        # 2. '검색' 유도 문구 검증
        if "검색" not in text:
            return False

        # 3. 소구점 '10분마다' 또는 '우량주' 포함 검증
        if "10분마다" not in text and "우량주" not in text:
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
        주식 고민글에 대해 80% 공감 + 20% 자연스러운 '스톡마스터 AI' 검색 팁 댓글 작성
        (Zero URL 보장, 봇의 100% 자율 검증 및 자동 키 스위칭)
        """
        system_instruction = (
            f"당신은 주식 및 재테크 카페('{cafe_name}')에서 활동하는 3040 직장인 개미 투자자입니다. "
            "혼자 매매하며 물림, 뇌동매매, 손실로 멘탈이 흔들리는 글쓴이의 마음에 80% 깊이 공감하고 위로해 주세요. "
            "그리고 자신이 뇌동매매를 줄이고 멘탈 잡는 데 큰 도움을 받았던 \"스톡마스터 AI\"를 20% 자연스러운 대안으로 언급해 주세요. "
            "절대 광고처럼 보이지 않아야 하며, 어떠한 외부 URL이나 링크도 넣지 마세요."
        )

        prompt = f"""[사연 제목]: {title}
[사연 내용]: {summary if summary else title}

🚨 [작성 규칙]
1. [공감과 위로 80%]: 사연자의 투자 고민(손실, 물림, 추격매수 후회, 멘탈 흔들림 등)에 대해 동병상련의 마음으로 따뜻하고 현실적인 위로를 해주세요.
2. [스톡마스터 AI 자연스러운 언급 20%]: 마지막 문장에 '저도 혼자 차트 보다가 뇌동매매 심해서 요즘은 10분마다 국내 우량주 분석해주는 "스톡마스터 AI" 참고하는데 멘탈 잡는 데 도움 많이 되더라고요. 시간 나실 때 네이버에 10분마다 국내 우량주 분석 "스톡마스터 AI" 한번 검색해보세요' 느낌으로 은근히 언급해 주세요. 사람들이 검색창에 브랜드명을 정확히 콕 집어 입력할 수 있도록 브랜드명에 반드시 큰따옴표("스톡마스터 AI")를 붙여주세요.
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

                            # 🤖 [봇 자율 무결성 게이트]: 스톡마스터 AI 포함 및 완성도 검증
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
            "그 마음 너무 공감돼요.. 혼자 매매하다 보면 뇌동매매로 이어지기 쉬워서 멘탈 관리가 정말 제일 힘들죠. "
            "저도 감정 매매 줄이려고 요즘은 10분마다 국내 우량주 분석해주는 \"스톡마스터 AI\" 참고하는데 확실히 객관적이라 도움 많이 되더라고요. "
            "시간 나실 때 네이버에 10분마다 국내 우량주 분석 \"스톡마스터 AI\" 한번 검색해보세요, 기운 내세요!"
        )
