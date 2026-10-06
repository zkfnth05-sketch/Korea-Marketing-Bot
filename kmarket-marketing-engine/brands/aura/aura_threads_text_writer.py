# -*- coding: utf-8 -*-
"""
Aura Threads Text Writer (💖 Aura 전용 스레드 순수 텍스트 제미나이 집필기 독립 레고 블록)
====================================================================================
- 브랜드: 💖 Aura (AI 데이팅)
- 공식 검색어: 아우라AI데이팅
- 공식 랜딩 URL: https://aura-ai-dating.vercel.app/
- 역할:
  1. 사진 0장! 100% 텍스트 단독 글 생성 (스레드 For You 알고리즘 바이럴 최적화)
  2. 2030 소개팅 삼프터/카톡 밀당/연애 심리 250~380자 공감 썰 & 촌철살인 팁 자율 집필
  3. 본문 내 링크(URL) 100% 배제 (알고리즘 페널티 방지)
  4. 첫 번째 타래 댓글(Add to thread)에 공식 검색어('아우라AI데이팅') 및 랜딩 URL 자동 체인
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

logger = logging.getLogger("AuraThreadsTextWriter")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent

# 💖 Aura 스레드 텍스트 글감 테마 풀 (하루 2회 순환)
_AURA_MORNING_THEMES = [
    {"topic": "소개팅 첫 카톡에서 90%가 하는 읽씹 유발 실수", "hook": "소개팅 끝나고 집 갈 때 카톡 이렇게 보내면 99% 읽씹당합니다."},
    {"topic": "썸녀/썸남 답장 텀으로 알아보는 찐 호감 시그널 3가지", "hook": "카톡 답장 텀 1시간? 5분? 답장 속도보다 중요한 '진짜 호감 시그널' 3가지."},
    {"topic": "첫 소개팅 어색한 침묵 3초 만에 깨는 마법의 스몰토크", "hook": "소개팅에서 밥 먹다가 숨 막히는 정적 올 때 쓰는 3초 치트키 대화법."},
    {"topic": "2030 직장인 소개팅 삼프터 성공률 300% 올리는 법", "hook": "애프터까지 잘 가놓고 삼프터에서 까이는 사람들의 공통적인 특징."}
]

_AURA_AFTERNOON_THEMES = [
    {"topic": "오후 나른할 때 생각나는 직장인 사내연애 & 썸 현실", "hook": "사내에서 은근히 호감 표시할 때 쓰는 부담 없는 시그널 3가지."},
    {"topic": "MBTI F와 T가 연애할 때 가장 크게 부딪히는 지점", "hook": "공감 바라는 F와 해결책 내놓는 T가 평화롭게 연애하는 법."},
    {"topic": "주말 데이트 코스 짤 때 센스 만점 소리 듣는 법", "hook": "웨이팅 지옥 피하고 분위기 챙기는 2030 성수/연남 데이트 꿀팁."},
    {"topic": "카톡 프로필 사진 하나로 호감도 200% 올리기", "hook": "소개팅 전 카톡 프사만 바꿔도 첫인상 점수 떡상하는 치트키."}
]

_AURA_EVENING_THEMES = [
    {"topic": "퇴근길 혼술할 때 유독 생각나는 전애인 카톡 심리", "hook": "퇴근하고 밤 11시에 오는 '자니?' 카톡의 진짜 심리학적 의미."},
    {"topic": "남녀가 생각하는 '연락 빈도'의 치명적인 차이점", "hook": "연인 사이에 연락 문제로 싸우기 전에 알아야 할 남녀 심리 팩트."},
    {"topic": "나랑 진짜 잘 맞는 인연을 5초 만에 알아보는 대화법", "hook": "아무리 외모가 이상형이어도 이 '한 가지' 안 맞으면 무조건 파국입니다."},
    {"topic": "요즘 2030이 남초 어플 거르고 안심 매칭 찾는 이유", "hook": "남초 데이팅앱에서 허위 프로필과 유령 회원에 지친 솔로들의 현실."}
]

from brands.aura.aura_hashtag_matrix import AuraHashtagMatrix

# 비상용 고품질 폴백 원고 뱅크 (15개 풍성한 해시태그 풀 탑재)
_AURA_FALLBACK_BANK = [
    {
        "caption": "소개팅 끝나고 집 갈 때 '오늘 즐거웠어요 조심히 들어가세요!'만 딱 보내면 90%는 그냥 예의상 인사로 끝납니다 ㅠㅠ\n\n진짜 센스 있는 사람은 오늘 밥 먹으면서 나눴던 사소한 대화 하나를 콕 집어서 언급해요.\n\n'오늘 파스타집 진짜 맛있었어요! 추천해주신 디저트 카페도 담에 꼭 가봐요 ㅎㅎ'\n\n이렇게 다음 만남의 핑계를 자연스럽게 만들어주는 게 애프터 성사율 300% 치트키입니다 ✨\n\n#아우라AI데이팅 #AURA #소개팅 #연애꿀팁 #소개팅카톡 #애프터신청 #연애심리 #2030연애 #직장인소개팅 #성수동데이트 #연남동소개팅 #카톡스몰토크 #실시간트렌드 #티키타카 #솔로탈출",
        "first_reply": "💖 2030 매력 진단 & AI 매칭 1분 무료 리포트\n네이버에 '아우라AI데이팅' 한번 검색해보세요!\n👉 https://aura-ai-dating.vercel.app/"
    },
    {
        "caption": "썸탈 때 상대방 답장 텀 길어진다고 '바쁘세요?' '오늘 뭐해요?' 재촉하는 건 호감도를 깎아먹는 지름길입니다...\n\n사람 심리는 '왜 연락 안 해?'가 아니라 '내 사소한 말을 기억해 줬네'에서 설레는 법이거든요.\n\n상대방이 며칠 전 지나가듯 말했던 취향이나 맛집 사진을 툭 보내보세요. 99% 바로 칼답 옵니다 ㅋㅋㅋ\n\n#아우라AI데이팅 #AURA #연애심리 #썸 #밀당 #카톡답장 #소개팅대화 #2030직장인 #연애고민 #읽씹탈출 #대화치트키 #강남역소개팅 #을지로데이트 #실시간트렌드 #심리테스트",
        "first_reply": "💖 나와 딱 맞는 500m 안심 인연 1분 무료 진단\n네이버에 '아우라AI데이팅' 한번 검색해보세요!\n👉 https://aura-ai-dating.vercel.app/"
    }
]


class AuraThreadsTextWriter:
    """💖 Aura 전용 스레드 텍스트 단독 집필기 (100% 독립 레고 블록)"""

    BRAND = "aura"
    BRAND_NAME = "Aura AI 데이팅"
    OFFICIAL_SEARCH_KEYWORD = "아우라AI데이팅"
    LANDING_URL = "https://aura-ai-dating.vercel.app/"

    def __init__(self):
        from config import (
            GEMINI_FREE_API_KEY_AURA_1,
            GEMINI_FREE_API_KEY_AURA_2,
            GEMINI_FREE_API_KEY_AURA_3,
        )
        candidates = [
            {"name": "AURA_FREE_1", "key": GEMINI_FREE_API_KEY_AURA_1},
            {"name": "AURA_FREE_2", "key": GEMINI_FREE_API_KEY_AURA_2},
            {"name": "AURA_FREE_3", "key": GEMINI_FREE_API_KEY_AURA_3},
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
                logger.warning(f"⚠️ [AuraTextWriter] {kinfo['name']} 실패 ➔ 롤오버: {e}")

        raise RuntimeError(f"모든 Gemini 키 호출 실패: {last_err}")

    def generate_thread_post(self, slot: str = "morning", custom_theme: Optional[str] = None) -> Dict[str, Any]:
        """스레드 전용 사진 0장 순수 텍스트 포스팅 + 실시간 15개 해시태그 + 첫 댓글 자동 생성"""
        if slot == "morning":
            theme_pool = _AURA_MORNING_THEMES
        elif slot == "afternoon":
            theme_pool = _AURA_AFTERNOON_THEMES
        else:
            theme_pool = _AURA_EVENING_THEMES
        chosen_theme = random.choice(theme_pool)
        topic = custom_theme or chosen_theme["topic"]
        hook = chosen_theme["hook"]

        # 실시간 15개 4-Tier 트렌드 해시태그 풀 생성
        hashtag_list = AuraHashtagMatrix.get_threads_hashtags(topic_id=random.randint(1, 8), count=15)
        hashtag_str = " ".join(hashtag_list)

        full_prompt = f"""당신은 2030 세대에게 폭발적인 공감을 얻는 감성/트렌드 연애 에디터이자 스레드(Threads) 전문 인플루언서입니다.
아래 조건에 맞춰 사진 없는 순수 텍스트 스레드 글을 작성해 주세요.

[주제] {topic}
[핵심 후킹 포인트] {hook}

[작성 규칙]
1. 사진/이미지는 없습니다. 오직 텍스트만으로 강렬한 공감과 재미를 주어야 합니다.
2. 본문 글자 수는 공백 포함 200자 ~ 280자 이내로 2~3개 문단으로 줄바꿈을 넣어 간결하고 흡입력 있게 작성하십시오.
3. 🚨 [본문 URL 금지]: 본문 안에 링크(http/https)나 '링크는 댓글에' 같은 노골적인 홍보 문구를 절대 넣지 마십시오.
4. 문체: 친근한 대화체 (~해요, ~거든요, ~더라고요, ㅋㅋㅋ, ㅠㅠ 적절히 활용).
5. 첫 줄은 시선을 끄는 1줄 후킹, 중간은 현실적인 공감 상황 + 1줄 실전 팁을 담아주세요.
6. 문장이 중간에 잘리지 않게 완전한 한국어 문장으로 마무리하십시오."""

        caption = ""
        try:
            raw_text = self._call_gemini_chain(full_prompt)
            caption_body = raw_text.replace("```json", "").replace("```", "").strip()
            # 기존 해시태그 제거 후 정밀 결합
            lines = [l for l in caption_body.split("\n") if l.strip() and not l.strip().startswith("#")]
            clean_body = "\n\n".join(lines)
            if len(clean_body) > 320:
                clean_body = clean_body[:300] + "..."
            caption = f"{clean_body}\n\n{hashtag_str}"
            logger.info(f"✨ [AuraTextWriter] Gemini 신규 텍스트 집필 완료 ({len(caption)}자, 해시태그 {len(hashtag_list)}개)")
        except Exception as ex:
            logger.warning(f"⚠️ [AuraTextWriter] Gemini 생성 실패로 비상 폴백 가동: {ex}")
            fallback = random.choice(_AURA_FALLBACK_BANK)
            caption = fallback["caption"]

        first_reply = (
            f"💖 2030 매력 진단 & AI 매칭 1분 무료 리포트\n"
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
    writer = AuraThreadsTextWriter()
    res = writer.generate_thread_post(slot="morning")
    print(json.dumps(res, ensure_ascii=False, indent=2))
