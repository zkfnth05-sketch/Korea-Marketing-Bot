# -*- coding: utf-8 -*-
"""
AuraSNSGuideMaster - 📢 [Aura 데이팅 전용 카드뉴스 & 숏폼 SNS 포스팅 가이드 통합 마스터]
======================================================================================
• 역할:
  1. 1080x1350 카드뉴스 (인스타 캐러셀, 스레드, 페이스북, 네이버 포스트/블로그/카페, 텔레그램 7대 채널)
  2. 1080x1920 숏폼 영상 (유튜브 쇼츠, 틱톡, 릴스, 스레드, 페이스북 5대 채널)
  3. 실시간 4단 티어 해시태그 엔진(AuraHashtagMatrix) 100% 자동 결합
  4. 관리자가 복사(Ctrl+C)하여 즉시 붙여넣을 수 있는 완벽한 원스톱 포맷 제공
• 공식 규격:
  - 포털 검색어: '아우라AI데이팅' (붙여쓰기 철칙)
  - 공식 랜딩 URL: https://aura-ai-dating.vercel.app/lounge
  - 카페 침투: Zero-URL 원칙 ("네이버에 아우라AI데이팅 한번 검색해보세요")
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from .aura_hashtag_matrix import AuraHashtagMatrix

logger = logging.getLogger("AuraSNSGuideMaster")


class AuraSNSGuideMaster:
    """💖 Aura 데이팅 카드뉴스 & 숏폼 SNS 포스팅 가이드 완결 마스터"""

    OFFICIAL_KEYWORD = "아우라AI데이팅"
    OFFICIAL_URL = "https://aura-ai-dating.vercel.app/lounge"
    BRAND_TITLE = "Aura AI 데이팅 (50:50 남녀 황금 성비 라운지)"

    @classmethod
    def build_cardnews_guide(
        cls,
        topic_id: int,
        theme_name: str,
        theme_code: str,
        copy_data: Dict[str, Any]
    ) -> str:
        """
        1080x1350 카드뉴스 전용 7대 플랫폼 통합 가이드 생성
        - 제미나이 실시간 창작 카피(copy_data)와 실시간 4단 해시태그 매트릭스 결합
        """
        matrix = AuraHashtagMatrix()
        insta_tags = " ".join(matrix.get_instagram_hashtags(topic_id=topic_id, count=18))
        threads_tags = " ".join(matrix.get_threads_hashtags(topic_id=topic_id))
        fb_tags = " ".join(matrix.get_facebook_hashtags(topic_id=topic_id))
        naver_tags = matrix.get_naver_tags(topic_id=topic_id)

        # 슬라이드별 카피 추출
        s1 = copy_data.get("slide1", {})
        s2 = copy_data.get("slide2", {})
        s3 = copy_data.get("slide3", {})
        s4 = copy_data.get("slide4", {})
        s5 = copy_data.get("slide5", {})

        s1_title = f"{s1.get('headline_line1', '')} {s1.get('headline_line2', '')}".strip()
        s1_sub = s1.get("subtitle", "")
        s1_bullets = "\n".join([f"• {b}" for b in s1.get("bullets", [])])

        s2_title = f"{s2.get('headline_line1', '')} {s2.get('headline_line2', '')}".strip()
        s2_sub = s2.get("subtitle", "")
        s2_bullets = "\n".join([f"• {b}" for b in s2.get("bullets", [])])

        s3_title = f"{s3.get('headline_line1', '')} {s3.get('headline_line2', '')}".strip()
        s3_sub = s3.get("subtitle", "")
        s3_bullets = "\n".join([f"• {b}" for b in s3.get("bullets", [])])

        s4_title = f"{s4.get('headline_line1', '')} {s4.get('headline_line2', '')}".strip()
        s4_sub = s4.get("subtitle", "")
        s4_bullets = "\n".join([f"• {b}" for b in s4.get("bullets", [])])

        debate_q = s5.get("debate_question") or s5.get("ending_debate", {}).get("question", "소개팅에서 당신의 선택은?")
        opt1_t = s5.get("debate_opt1_title") or s5.get("ending_debate", {}).get("opt1_text", "선택 1")
        opt2_t = s5.get("debate_opt2_title") or s5.get("ending_debate", {}).get("opt2_text", "선택 2")

        sns_caption = copy_data.get("sns_caption", "").strip()
        if not sns_caption:
            sns_caption = (
                f"{s1_title}\n\n"
                f"{s1_sub}\n\n"
                f"소개팅이나 새로운 만남에서 어색하거나 스트레스 받았던 경험, 다들 있으시죠? 💬\n"
                f"Aura는 50:50 남녀 황금 성비와 검증된 2030 싱글만을 위한 클린 라운지를 제공합니다. ✨\n\n"
                f"⚖️ 오늘의 찬반 토론!\n"
                f"\"{debate_q}\"\n"
                f"👉 1번: {opt1_t}\n"
                f"👉 2번: {opt2_t}\n\n"
                f"댓글에 [1번] vs [2번] 여러분의 솔직한 생각을 남겨주세요! 👇"
            )

        guide = f"""================================================================================
💖 [Aura AI 데이팅] 1080x1350 카드뉴스 7대 SNS 원스톱 포스팅 가이드
================================================================================
📌 테마: #{topic_id} {theme_name} ({theme_code})
📌 공식 브랜드: {cls.BRAND_TITLE}
🔍 공식 포털 검색어: {cls.OFFICIAL_KEYWORD} (붙여쓰기 필수!)
🔗 공식 라운지 URL: {cls.OFFICIAL_URL}
📐 규격: 1080x1350 (4:5 풀블리드 카드뉴스 총 5장 완결)
================================================================================

[1] 📸 인스타그램 (Instagram) 피드 & 캐러셀 가이드
--------------------------------------------------------------------------------
📌 [인스타 캡션 (복사해서 바로 사용)]
{sns_caption}

🔍 네이버 검색창에 [{cls.OFFICIAL_KEYWORD}] 검색하고
나랑 100% 맞는 인연을 지금 바로 만나보세요! ✨
🔗 프로필 링크(@aura_official) 또는 공식 웹: {cls.OFFICIAL_URL}

📌 [인스타 탐색탭 알고리즘 노출 폭발 18~20개 4단 해시태그 풀]
{insta_tags}


[2] 🧵 스레드 (Threads) 텍스트 바이럴 가이드
--------------------------------------------------------------------------------
📌 [스레드 본문 (200자 압축 후킹 + 공감 질문)]
{s1_title}

{s1_sub}

💬 여러분의 생각은?
{debate_q}
1️⃣ {opt1_t}
2️⃣ {opt2_t}

다들 솔직한 의견 댓글로 달아보셈 👇

{threads_tags}

💬 [첫 번째 댓글 (알고리즘 보호 전환 링크)]
👉 50:50 황금 성비 클린 라운지 입장하기: {cls.OFFICIAL_URL}
(또는 네이버에 '{cls.OFFICIAL_KEYWORD}' 검색)


[3] 📘 페이스북 (Facebook) 피드 가이드
--------------------------------------------------------------------------------
📌 [페북 피드 본문 (카드뉴스 5장 앨범 첨부)]
{s1_title} 🚨

{s1_sub}

어색하고 불편한 소개팅에 지친 2030을 위한 특급 솔루션!
카드뉴스를 옆으로 넘겨서 5장으로 확인해보세요. 👉

{fb_tags}

💬 [첫 번째 댓글 (스텔스 전환 링크)]
👉 공식 웹사이트에서 무료 확인: {cls.OFFICIAL_URL}
👉 네이버 검색창에 [{cls.OFFICIAL_KEYWORD}] 검색!


[4] 📰 네이버 포스트 (Naver Post) - [카드형] 에디터 가이드
--------------------------------------------------------------------------------
📌 [추천 제목]: {s1_title}
🏷️ [추천 시리즈]: Aura 2030 실전 소개팅 백과

🖼️ [슬라이드 업로드 매핑]:
• [표지 1/5]: slide_1.png ➔ {s1_title} ({s1_sub})
• [공감 2/5]: slide_2.png ➔ {s2_title}
• [해결 3/5]: slide_3.png ➔ {s3_title}
• [기능 4/5]: slide_4.png ➔ {s4_title}
• [엔딩 5/5]: slide_5.png ➔ 찬반 토론 & 네이버 검색 [{cls.OFFICIAL_KEYWORD}] CTA

🏷️ [네이버 포스트 태그]:
{naver_tags}


[5] 📗 네이버 블로그 (Naver Blog) - 카드뉴스 연속 스크롤 가이드
--------------------------------------------------------------------------------
📌 [블로그 추천 제목]: {s1_title} | {theme_name} 총정리

📝 [본문 배치]:
(사진 첨부: slide_1.png)
{s1_title}
{s1_sub}
{s1_bullets}

---
(사진 첨부: slide_2.png)
{s2_title}
{s2_sub}
{s2_bullets}

---
(사진 첨부: slide_3.png)
{s3_title}
{s3_sub}
{s3_bullets}

---
(사진 첨부: slide_4.png)
{s4_title}
{s4_sub}
{s4_bullets}

---
(사진 첨부: slide_5.png)
💡 오늘의 찬반 토론: {debate_q}
지금 네이버 검색창에 [{cls.OFFICIAL_KEYWORD}]을 검색하시고 나만의 인연을 만나보세요.

🏷️ [네이버 블로그 태그]:
{naver_tags}


[6] ☕ 네이버 카페 (Naver Cafe) - 바이럴 침투 가이드
--------------------------------------------------------------------------------
⚠️ [카페 침투 절대 철칙 - Zero-URL 원칙]
링크(URL) 삽입 절대 금지! 오직 "네이버에 {cls.OFFICIAL_KEYWORD} 한번 검색해보세요"로만 유도합니다.

📌 [추천 게시글 제목]: {s1_title} 다들 어떻게 생각하시나요?
📝 [추천 본문]:
{s2_sub}
소개팅이나 데이팅 앱 쓰면서 이런 경험 있으신 분들 많으시죠?
다들 이럴 때 어떻게 대처하시는지 팁 좀 공유해주세요! ㅠㅠ

💬 [댓글 침투 스크립트]:
"요즘 아우라 앱 쓰는데 {s3_title} 기능 진짜 유용해요 ㅋㅋㅋ 네이버에 '{cls.OFFICIAL_KEYWORD}' 한번 검색해보세요 신세계임"


[7] ✈️ 텔레그램 (Telegram) - 5장 앨범 가이드
--------------------------------------------------------------------------------
📌 [텔레그램 캡션]:
💖 {s1_title}

{s1_sub}
• 50:50 남녀 황금 성비율 보장
• 실명 인증 2030 클린 라운지

🔗 공식 웹 바로가기: {cls.OFFICIAL_URL}
================================================================================
"""
        return guide

    @classmethod
    def build_shorts_guide(
        cls,
        topic_id: int,
        theme_name: str,
        theme_code: str,
        yt_title: str,
        yt_desc: str,
        pinned_comment: str,
        reels_caption: str,
        tiktok_caption: str,
        threads_text: str,
        fb_text: str
    ) -> str:
        """
        1080x1920 숏폼 영상 전용 5대 SNS 통합 포스팅 가이드 생성
        """
        matrix = AuraHashtagMatrix()
        insta_tags = " ".join(matrix.get_instagram_hashtags(topic_id=topic_id, count=18))
        threads_tags = " ".join(matrix.get_threads_hashtags(topic_id=topic_id))
        fb_tags = " ".join(matrix.get_facebook_hashtags(topic_id=topic_id))
        shorts_tags = matrix.get_shorts_hashtags(topic_id=topic_id)

        guide = f"""================================================================================
🎬 [AURA AI 데이팅] 1080x1920 숏폼 5대 SNS 원클릭 포스팅 가이드
================================================================================
주제 번호: #{topic_id} [{theme_name}]
테마 코드: {theme_code}
영상 규격: 1080x1920 (9:16 세로 풀HD 숏폼, 22초)
공식 네이버 검색어: {cls.OFFICIAL_KEYWORD} (붙여쓰기 고정)
공식 랜딩 URL: {cls.OFFICIAL_URL}
================================================================================

[1] 🔴 유튜브 쇼츠 (YouTube Shorts) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [쇼츠 제목 (Title)]
{yt_title}

📌 [쇼츠 설명 (Description)]
{yt_desc}

📌 [고정 댓글 (Pinned Comment - 댓글창 찬반 논쟁 유발)]
{pinned_comment}

🏷️ [추천 태그]:
{shorts_tags}


[2] 🎵 틱톡 (TikTok) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [추천 캡션 (복사용 원문)]
{tiktok_caption}

{shorts_tags}

📌 [프로필 바이오 / 댓글 안내]
👉 Link in Bio: {cls.OFFICIAL_URL}
👉 네이버 검색창에 [{cls.OFFICIAL_KEYWORD}] 검색!


[3] 📸 인스타그램 릴스 (Instagram Reels) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [릴스 추천 캡션]
{reels_caption}

🔗 Bio Link: @aura_official -> {cls.OFFICIAL_URL}
🔍 네이버에 [{cls.OFFICIAL_KEYWORD}] 검색!

📌 [릴스 알고리즘 노출 폭발 18~20개 4단 해시태그 풀]
{insta_tags}


[4] 🧵 스레드 (Threads) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [스레드 본문 (텍스트 바이럴 & 공감 질문형)]
{threads_text}

{threads_tags}

💬 [첫 번째 댓글 (전환 링크)]
👉 안전한 동네 친구 & 50:50 데이팅 바로가기: {cls.OFFICIAL_URL}


[5] 📘 페이스북 릴스 (Facebook Reels) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [피드 본문 (알고리즘 도달 극대화)]
{fb_text}

{fb_tags}

💬 [첫 번째 댓글 (스텔스 전환 링크)]
👉 네이버에 [{cls.OFFICIAL_KEYWORD}] 검색 또는 바로가기: {cls.OFFICIAL_URL}
================================================================================
"""
        return guide
