# -*- coding: utf-8 -*-
"""
Stock Threads Text Writer (📈 StockMaster AI 전용 스레드 순수 텍스트 제미나이 집필기 독립 레고 블록)
=================================================================================================
- 브랜드: 📈 StockMaster AI (주식 AI)
- 공식 검색어: 스톡마스터 AI (띄어쓰기 필수)
- 공식 랜딩 URL: https://stockmaster-ai.vercel.app/
- 역할:
  1. 사진 0장! 100% 텍스트 단독 글 생성 (스레드 For You 알고리즘 바이럴 최적화)
  2. 주도 테마주, 외인/기관 수급 분석, 뇌동매매 방지 250~380자 실전 퀀트 인사이트 자율 집필
  3. 본문 내 링크(URL) 100% 배제 (알고리즘 페널티 방지)
  4. 첫 번째 타래 댓글(Add to thread)에 공식 검색어('스톡마스터 AI') 및 랜딩 URL 자동 체인
  5. 무료키 3개 자동 체인 + 안전 폴백 뱅크 탑재
"""

import os
import sys
import json
import random
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("StockThreadsTextWriter")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent

# 📈 StockMaster AI 스레드 텍스트 글감 테마 풀 (하루 2회 순환)
_STOCK_MORNING_THEMES = [
    {"topic": "장 시작 전 반드시 체크해야 할 외인/기관 수급 쏠림 섹터", "hook": "개장 30분 전, 미 증시 마감 보고 오늘 국장 주도 테마 3줄 요약."},
    {"topic": "주식 초보들이 장초반 9시~9시30분에 제일 많이 물리는 패턴", "hook": "장 시작하자마자 갭상승 종목 쫓아갔다가 고점 물리는 개미들의 공통점."},
    {"topic": "단타 칠 때 거래량 터지는 양봉 캔들 제대로 해석하는 법", "hook": "거래대금 1,000억 터졌다고 무조건 진입하면 안 되는 이유."},
    {"topic": "오늘 주목해야 할 반도체 & 2차전지 밸류체인 핵심 맥락", "hook": "삼성전자/SK하이닉스 수급 들어올 때 조용히 같이 오르는 소부장 공략법."}
]

_STOCK_EVENING_THEMES = [
    {"topic": "장마감 후 외인·기관이 몰래 쌍끌이 매수한 종목 분석법", "hook": "오늘 시장 하락장에서도 기관이 3일 연속 쓸어담은 종목들의 특징."},
    {"topic": "수익률 30% 갉아먹는 '손절 타이밍' 놓치는 심리학적 원인", "hook": "-3% 손절은 쉬운데 -15% 넘어가면 계좌 방치하게 되는 이유."},
    {"topic": "뇌동매매와 추격매수 끊어내는 AI 퀀트 분할 매매 원칙", "hook": "주식으로 꾸준히 수익 내는 상위 1%가 철저히 지키는 분할 매수 룰."},
    {"topic": "실시간 뉴스 뜨기 전에 차트와 수급에서 먼저 나오는 시그널", "hook": "호재 공시 뜨고 사면 왜 항상 고점일까? 스마트 머니의 매집 흔적 찾는 법."}
]

# 비상용 고품질 폴백 원고 뱅크
_STOCK_FALLBACK_BANK = [
    {
        "caption": "주식 초보분들이 가장 많이 하는 실수가 '장 시작하자마자 9시 5분에 급등주 추격 매수'하는 겁니다 ㅠㅠ\n\n장초반 30분은 변동성이 가장 심하고 세력들의 물량 털기가 자주 나오는 시간대예요.\n\n진짜 고수들은 9시 30분 이후 거래대금이 꾸준히 유지되면서 지지선 확인하는 종목을 공략합니다. 조급함을 버리는 게 수익의 첫걸음이에요 📈\n\n#주식투자 #주식초보 #매매기법 #단타 #스톡마스터AI",
        "first_reply": "📈 AI 실시간 수급 & 급등 테마 분석기\n네이버에 '스톡마스터 AI' 한번 검색해보세요!\n👉 https://stockmaster-ai.vercel.app/"
    },
    {
        "caption": "하락장에서 계좌 지키는 최고의 무기는 '수급 연속성' 체크입니다 💡\n\n코스피 코스닥이 밀려도 외국인과 기관이 3일 이상 연속으로 순매수하는 종목은 시장 반등할 때 1순위로 튀어 오르거든요.\n\n감이나 소문으로 매매하지 말고, 매일 장마감 후 메이저 수급이 어디로 쏠렸는지 데이터로 확인해보세요!\n\n#주식시황 #외인수급 #기관수급 #주식공부 #StockMaster",
        "first_reply": "📈 실시간 테마 & 기관 수급 레이더 무료 진단\n네이버에 '스톡마스터 AI' 한번 검색해보세요!\n👉 https://stockmaster-ai.vercel.app/"
    }
]


class StockThreadsTextWriter:
    """📈 StockMaster AI 전용 스레드 텍스트 단독 집필기 (100% 독립 레고 블록)"""

    BRAND = "stock"
    BRAND_NAME = "StockMaster AI"
    OFFICIAL_SEARCH_KEYWORD = "스톡마스터 AI"
    LANDING_URL = "https://stockmaster-ai.vercel.app/"

    def __init__(self):
        from config import (
            GEMINI_FREE_API_KEY_AURA_1,
            GEMINI_FREE_API_KEY_AURA_2,
            GEMINI_FREE_API_KEY_AURA_3,
        )
        candidates = [
            {"name": "STOCK_FREE_1", "key": GEMINI_FREE_API_KEY_AURA_1},
            {"name": "STOCK_FREE_2", "key": GEMINI_FREE_API_KEY_AURA_2},
            {"name": "STOCK_FREE_3", "key": GEMINI_FREE_API_KEY_AURA_3},
        ]
        seen = set()
        self.key_chain = []
        for c in candidates:
            k = (c.get("key") or "").strip()
            if k and k not in seen and len(k) > 10:
                seen.add(k)
                self.key_chain.append({"name": c["name"], "key": k})
        self._active_key_index = 0

    def _call_gemini_chain(self, prompt: str) -> str:
        if not self.key_chain:
            raise RuntimeError("사용 가능한 Gemini API 키가 없습니다.")
        total_keys = len(self.key_chain)
        last_err = None

        for i in range(total_keys):
            idx = (self._active_key_index + i) % total_keys
            kinfo = self.key_chain[idx]
            try:
                from google import genai
                client = genai.Client(api_key=kinfo["key"])

                resp = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                if resp and resp.text and len(resp.text.strip()) > 80:
                    self._active_key_index = idx
                    return resp.text.strip()
            except Exception as e:
                last_err = e
                logger.warning(f"⚠️ [StockTextWriter] {kinfo['name']} 실패 ➔ 롤오버: {e}")

        raise RuntimeError(f"모든 Gemini 키 호출 실패: {last_err}")

    def generate_thread_post(self, slot: str = "morning", custom_theme: Optional[str] = None) -> Dict[str, Any]:
        """스레드 전용 사진 0장 순수 텍스트 포스팅 + 첫 댓글 자동 생성"""
        theme_pool = _STOCK_MORNING_THEMES if slot == "morning" else _STOCK_EVENING_THEMES
        chosen_theme = random.choice(theme_pool)
        topic = custom_theme or chosen_theme["topic"]
        hook = chosen_theme["hook"]

        full_prompt = f"""당신은 실전 퀀트 트레이더이자 주식 AI 투자 전략 스레드(Threads) 전문 인플루언서입니다.
아래 조건에 맞춰 사진 없는 순수 텍스트 스레드 글을 작성해 주세요.

[주제] {topic}
[핵심 후킹 포인트] {hook}

[작성 규칙]
1. 사진/이미지는 없습니다. 오직 텍스트만으로 강력한 인사이트와 실전성을 주어야 합니다.
2. 글자 수는 공백 포함 250자 ~ 380자 이내로 3~4개 문단으로 줄바꿈을 꼭 넣어 작성하십시오.
3. 🚨 [본문 URL 금지]: 본문 안에 링크(http/https)나 '종목 추천 링크' 같은 노골적인 홍보 문구를 절대 넣지 마십시오.
4. 문체: 전문적이면서도 알기 쉬운 어조 (~합니다, ~해보세요, ~거든요, 📈, 💡 적절히 활용).
5. 첫 줄은 시장 상황/투자자 실수를 찌르는 1줄 후킹, 중간은 데이터 기반 원인 분석 + 1줄 실전 매매 원칙, 끝에는 해시태그 3~4개(#주식투자 #주식시황 #수급분석 #스톡마스터AI)를 부착해 주세요.
6. 문장이 중간에 잘리지 않게 완전한 한국어 문장으로 마무리하십시오."""

        caption = ""
        try:
            raw_text = self._call_gemini_chain(full_prompt)
            caption = raw_text.replace("```json", "").replace("```", "").strip()
            if len(caption) < 100:
                raise ValueError(f"생성된 텍스트가 너무 짧음 ({len(caption)}자)")
            if len(caption) > 420:
                lines = [l for l in caption.split("\n") if l.strip()]
                caption = "\n\n".join(lines[:6])
                if len(caption) > 400:
                    caption = caption[:380] + "..."
            logger.info(f"✨ [StockTextWriter] Gemini 신규 텍스트 집필 완료 ({len(caption)}자)")
        except Exception as ex:
            logger.warning(f"⚠️ [StockTextWriter] Gemini 생성 실패로 비상 폴백 가동: {ex}")
            fallback = random.choice(_STOCK_FALLBACK_BANK)
            caption = fallback["caption"]

        first_reply = (
            f"📈 AI 실시간 수급 & 급등 테마 분석기\n"
            f"네이버에 '{self.OFFICIAL_SEARCH_KEYWORD}' 한번 검색해보세요!\n"
            f"👉 {self.LANDING_URL}"
        )

        return {
            "brand": self.BRAND,
            "brand_name": self.BRAND_NAME,
            "slot": slot,
            "topic": topic,
            "caption": caption,
            "first_reply": first_reply,
            "created_at": datetime.now().isoformat(),
            "character_count": len(caption),
            "has_images": False
        }


if __name__ == "__main__":
    writer = StockThreadsTextWriter()
    res = writer.generate_thread_post(slot="morning")
    print(json.dumps(res, ensure_ascii=False, indent=2))
