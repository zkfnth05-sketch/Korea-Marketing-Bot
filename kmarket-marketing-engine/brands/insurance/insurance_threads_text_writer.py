# -*- coding: utf-8 -*-
"""
Insurance Threads Text Writer (🛡️ 보험 리밸런스 전용 스레드 순수 텍스트 제미나이 집필기 독립 레고 블록)
===================================================================================================
- 브랜드: 🛡️ 보험 리밸런스 (InsureBalance)
- 공식 검색어: 보험 리밸런스 (띄어쓰기 필수)
- 공식 랜딩 URL: https://insure-rebalance.vercel.app/
- 역할:
  1. 사진 0장! 100% 텍스트 단독 글 생성 (스레드 For You 알고리즘 바이럴 최적화)
  2. 2030 직장인/가족 보험료 절약, 4세대 실손 팩트, 숨은 환급금 250~380자 팩트 폭격 자율 집필
  3. 본문 내 링크(URL) 100% 배제 (알고리즘 페널티 방지)
  4. 첫 번째 타래 댓글(Add to thread)에 공식 검색어('보험 리밸런스') 및 랜딩 URL 자동 체인
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
from google import genai
from google.genai import types
from core.gemini_unified_keys import get_unified_gemini_key_dicts, format_gemini_error, get_gemini_content_config


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("InsuranceThreadsTextWriter")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent

# 🛡️ 보험 리밸런스 스레드 텍스트 글감 테마 풀 (하루 2회 순환)
_INSURANCE_MORNING_THEMES = [
    {"topic": "2030 직장인 10명 중 8명이 매달 10만원씩 버리는 불필요한 특약", "hook": "매달 나가는 보험료 15만원, 까보면 7만원은 진짜 쓸데없는 특약입니다."},
    {"topic": "4세대 실손보험 갈아타면 무조건 손해 보는 사람 특징", "hook": "4세대 실손보험 싸다고 덜컥 갈아탔다가 병원비 폭탄 맞는 3가지 유형."},
    {"topic": "치과 치료 받기 전에 반드시 확인해야 할 숨은 실손 보장", "hook": "치과 가서 100만원 깨지기 전에 내 보험에서 돌려받을 수 있는 항목 체크리스트."},
    {"topic": "부모님 암보험 갱신 폭탄 피하는 리모델링 3원칙", "hook": "부모님 보험료가 3년마다 2배씩 뛴다면 당장 이 항목부터 확인하세요."}
]

_INSURANCE_AFTERNOON_THEMES = [
    {"topic": "주부 알뜰 살림 꿀팁: 매달 새어나가는 고정지출 3분 점검", "hook": "장보기 2만원 아끼는 것보다 보험료 10만원 다이어트가 5배 빠릅니다."},
    {"topic": "어린이보험/태아보험 성인 될 때까지 보험료 안 오르게 맞추는 법", "hook": "자녀 보험 10만원 넘게 내고 계신다면 꼭 확인해야 할 만기 설정 팁."},
    {"topic": "병원비 영수증 버리지 마세요! 통원치료 실손 청구 노하우", "hook": "1~2만원짜리 약값, 통원비도 모으면 1년에 수십만원 환급받습니다."},
    {"topic": "단독 실손 vs 종합보험, 나에게 진짜 필요한 보장 구별법", "hook": "보험설계사가 추천하는 종합보험에 덜컥 가입하기 전 체크리스트."}
]

_INSURANCE_EVENING_THEMES = [
    {"topic": "잠자고 있는 숨은 보험금 3분 만에 계좌로 돌려받는 법", "hook": "대한민국 국민 1인당 평균 18만원씩 잠자고 있는 숨은 환급금 찾는 법."},
    {"topic": "운전자보험 가입할 때 호구 안 당하는 필수 3대 특약", "hook": "운전자보험 3만원짜리 들지 마세요. 딱 1만원이면 충분한 이유."},
    {"topic": "가족력 있는 사람이 3대 질병 진단비 가성비로 맞추는 법", "hook": "암·뇌·심장 3대 질병 진단비, 비싼 종합보험 대신 핵심만 골라 담기."},
    {"topic": "사회초년생 월급 250만원 기준 가장 이상적인 보험료 비율", "hook": "사회초년생 첫 월급 받고 지인한테 보험 가입했다가 후회하는 이유."}
]

from brands.insurance.insurance_hashtag_matrix import InsuranceHashtagMatrix

# 비상용 고품질 폴백 원고 뱅크 (15개 풍성한 해시태그 풀 탑재)
_INSURANCE_FALLBACK_BANK = [
    {
        "caption": "사회초년생 때 지인 부탁으로 월 15만원짜리 종신보험 든 분들 진짜 많으시죠...\n\n솔직히 2030 싱글한테 종신보험은 낭비에 가깝습니다. 실손 + 3대 질병(암/뇌/심장) 진단비만 딱 챙겨도 월 5~7만원이면 차고 넘치거든요.\n\n매달 새어나가는 보험료 8만원만 아껴도 1년에 100만원 저축합니다. 지금 바로 증권 열어서 불필요한 특약 다이어트해보세요!\n\n#보험리밸런스 #InsureBalance #보험료줄이기 #재테크 #사회초년생 #보험리모델링 #실손보험 #보험다이어트 #숨은보험금 #고정지출절약 #실비보험비교 #2030재테크 #실시간트렌드 #가계부점검 #월급관리",
        "first_reply": "🛡️ 내 보험료 과다청구 1분 무료 분석\n네이버에 '보험 리밸런스' 한번 검색해보세요!\n👉 https://insure-rebalance.vercel.app/"
    },
    {
        "caption": "4세대 실손보험 보험료 싸다고 무조건 갈아타면 안 되는 이유 💡\n\n1~2세대 실손(2017년 이전 가입)은 병원 자주 가거나 도수치료, 비급여 주사 많이 맞으시는 분들에게는 무조건 유지하는 게 이득입니다.\n\n반대로 1년에 병원 한 번 갈까 말까 하신 분들은 4세대로 넘어가서 보험료 70% 아끼는 게 정답이에요. 내 병원 이용 패턴부터 객관적으로 분석해보세요!\n\n#보험리밸런스 #InsureBalance #실손보험 #4세대실손 #보험꿀팁 #병원비절약 #보험비교 #착한실손 #실비보험료 #도수치료실비 #보험비교사이트 #34개보험사비교 #실시간트렌드 #돈모으기 #재테크고민",
        "first_reply": "🛡️ 내 숨은 보험금 & 최적 보장 무료 진단\n네이버에 '보험 리밸런스' 한번 검색해보세요!\n👉 https://insure-rebalance.vercel.app/"
    }
]


class InsuranceThreadsTextWriter:
    """🛡️ 보험 리밸런스 전용 스레드 텍스트 단독 집필기 (100% 독립 레고 블록)"""

    BRAND = "insurance"
    BRAND_NAME = "보험 리밸런스"
    OFFICIAL_SEARCH_KEYWORD = "보험 리밸런스"
    LANDING_URL = "https://insure-rebalance.vercel.app/"

    def __init__(self):
        self.key_chain = get_unified_gemini_key_dicts()
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
                client = genai.Client(api_key=kinfo["key"])

                resp = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.85)
                )
                if resp and resp.text and len(resp.text.strip()) > 80:
                    self._active_key_index = idx
                    return resp.text.strip()
            except Exception as e:
                last_err = e
                logger.warning(f"⚠️ [InsuranceTextWriter] {kinfo['name']} 실패 ➔ 롤오버: {format_gemini_error(e)}")

        raise RuntimeError(f"모든 Gemini 키 호출 실패: {last_err}")

    def generate_thread_post(self, slot: str = "morning", custom_theme: Optional[str] = None) -> Dict[str, Any]:
        """스레드 전용 사진 0장 순수 텍스트 포스팅 + 실시간 15개 해시태그 + 첫 댓글 자동 생성"""
        if slot == "morning":
            theme_pool = _INSURANCE_MORNING_THEMES
        elif slot == "afternoon":
            theme_pool = _INSURANCE_AFTERNOON_THEMES
        else:
            theme_pool = _INSURANCE_EVENING_THEMES
        chosen_theme = random.choice(theme_pool)
        topic = custom_theme or chosen_theme["topic"]
        hook = chosen_theme["hook"]

        # 실시간 15개 4-Tier 트렌드 해시태그 풀 생성
        hashtag_list = InsuranceHashtagMatrix.get_threads_hashtags(topic_id=random.randint(1, 8), count=15)
        hashtag_str = " ".join(hashtag_list)

        full_prompt = f"""당신은 10년 차 공인 보험 분석가이자 가성비 재테크 스레드(Threads) 전문 에디터입니다.
아래 조건에 맞춰 사진 없는 순수 텍스트 스레드 글을 작성해 주세요.

[주제] {topic}
[핵심 후킹 포인트] {hook}

[작성 규칙]
1. 사진/이미지는 없습니다. 오직 텍스트만으로 강력한 정보성과 가치를 전달해야 합니다.
2. 본문 글자 수는 공백 포함 200자 ~ 280자 이내로 2~3개 문단으로 줄바꿈을 넣어 간결하고 흡입력 있게 작성하십시오.
3. 🚨 [본문 URL 금지]: 본문 안에 링크(http/https)나 '링크 확인' 같은 노골적인 홍보 문구를 절대 넣지 마십시오.
4. 문체: 신뢰감 있으면서도 쉬운 설명체 (~입니다, ~하세요, ~거든요, 💡 활용).
5. 첫 줄은 보험료 낭비를 찌르는 1줄 후킹, 중간은 알기 쉬운 원인 분석 + 1줄 실전 팁을 담아주세요.
6. 문장이 중간에 잘리지 않게 완전한 한국어 문장으로 마무리하십시오."""

        caption = ""
        try:
            raw_text = self._call_gemini_chain(full_prompt)
            caption_body = raw_text.replace("```json", "").replace("```", "").strip()
            lines = [l for l in caption_body.split("\n") if l.strip() and not l.strip().startswith("#")]
            clean_body = "\n\n".join(lines)
            if len(clean_body) > 320:
                clean_body = clean_body[:300] + "..."
            caption = f"{clean_body}\n\n{hashtag_str}"
            logger.info(f"✨ [InsuranceTextWriter] Gemini 신규 텍스트 집필 완료 ({len(caption)}자, 해시태그 {len(hashtag_list)}개)")
        except Exception as ex:
            logger.warning(f"⚠️ [InsuranceTextWriter] Gemini 생성 실패로 비상 폴백 가동: {ex}")
            fallback = random.choice(_INSURANCE_FALLBACK_BANK)
            caption = fallback["caption"]

        first_reply = (
            f"🛡️ 내 보험료 과다청구 1분 무료 분석\n"
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
            "hashtags": hashtag_list,
            "created_at": datetime.now().isoformat(),
            "character_count": len(caption),
            "has_images": False
        }


if __name__ == "__main__":
    writer = InsuranceThreadsTextWriter()
    res = writer.generate_thread_post(slot="morning")
    print(json.dumps(res, ensure_ascii=False, indent=2))
