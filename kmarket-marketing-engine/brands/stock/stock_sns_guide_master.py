# -*- coding: utf-8 -*-
"""
StockSNSGuideMaster - 📢 [StockMaster AI 전용 카드뉴스 & 숏폼 SNS 포스팅 가이드 통합 마스터]
==========================================================================================
• 역할:
  1. 1080x1350 카드뉴스 (인스타 캐러셀, 스레드, 페이스북, 네이버 포스트/블로그/카페, 텔레그램 7대 채널)
  2. 1080x1920 숏폼 영상 (유튜브 쇼츠, 틱톡, 릴스, 스레드, 페이스북, 네이버클립 6대 채널)
  3. 실시간 4단 티어 해시태그 엔진(StockHashtagMatrix) 100% 자동 결합
  4. 관리자가 복사(Ctrl+C)하여 즉시 붙여넣을 수 있는 완벽한 원스톱 템플릿 제공
• 공식 규격:
  - 공식 검색어: '스톡마스터 AI' (띄어쓰기 필수!)
  - 공식 랜딩 URL: https://stockmaster-ai.vercel.app/
  - 카페 침투: Zero-URL 원칙 ("네이버에 스톡마스터 AI 한번 검색해보세요")
  - 자본시장법 준수 클린 면책고지 일체형
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from .stock_hashtag_matrix import StockHashtagMatrix

logger = logging.getLogger("StockSNSGuideMaster")


class StockSNSGuideMaster:
    """📈 StockMaster AI 카드뉴스 & 숏폼 SNS 포스팅 가이드 완결 마스터"""

    OFFICIAL_KEYWORD = "스톡마스터 AI"
    OFFICIAL_URL = "https://stockmaster-ai.vercel.app/"
    BRAND_TITLE = "StockMaster AI (실시간 외국인 수급 & 퀀트 적정주가 진단)"

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
        """
        matrix = StockHashtagMatrix()
        insta_tags = " ".join(matrix.get_instagram_hashtags(topic_id=topic_id, count=18))
        threads_tags = " ".join(matrix.get_threads_hashtags(topic_id=topic_id))
        fb_tags = " ".join(matrix.get_facebook_hashtags(topic_id=topic_id))
        naver_tags = matrix.get_naver_tags(topic_id=topic_id)

        s1 = copy_data.get("slide1", {})
        s2 = copy_data.get("slide2", {})
        s3 = copy_data.get("slide3", {})
        s4 = copy_data.get("slide4", {})
        s5 = copy_data.get("slide5", {})

        s1_title = f"{s1.get('headline_line1', '')} {s1.get('headline_line2', '')}".strip() or f"{theme_name} 퀀트 팩트체크"
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

        debate_q = s5.get("debate_question") or "지금 이 종목, 매수 타이밍일까요?"
        opt1_t = s5.get("debate_opt1_title") or "1번: 수급 유입으로 추가 상승 기대"
        opt2_t = s5.get("debate_opt2_title") or "2번: 밸류에이션 부담으로 조정 대비"

        sns_caption = copy_data.get("sns_caption", "").strip()
        if not sns_caption:
            sns_caption = (
                f"{s1_title}\n\n"
                f"{s1_sub}\n\n"
                f"감으로 매매하다 물리고 후회했던 적 있으신가요? 📉\n"
                f"StockMaster AI는 특정 종목 권유 없이, 실시간 외국인·기관 수급과 퀀트 밸류에이션으로 적정주가를 1초 만에 진단해 드립니다. 📈\n\n"
                f"⚖️ 오늘의 투자 토론!\n"
                f"\"{debate_q}\"\n"
                f"👉 1번: {opt1_t}\n"
                f"👉 2번: {opt2_t}\n\n"
                f"댓글에 [1번] vs [2번] 여러분의 솔직한 투자 뷰를 남겨주세요! 👇"
            )

        guide = f"""================================================================================
📈 [스톡마스터 AI] 1080x1350 카드뉴스 7대 SNS 원스톱 포스팅 가이드
================================================================================
📌 테마: #{topic_id} {theme_name} ({theme_code})
📌 공식 브랜드: {cls.BRAND_TITLE}
🔍 공식 포털 검색어: [{cls.OFFICIAL_KEYWORD}] (띄어쓰기 필수!)
🔗 공식 사이트 URL: {cls.OFFICIAL_URL}
📐 규격: 1080x1350 (4:5 풀블리드 카드뉴스 총 5장 완결)
================================================================================

[1] 📸 인스타그램 (Instagram) 피드 & 캐러셀 가이드
--------------------------------------------------------------------------------
📌 [인스타 캡션 (복사해서 바로 사용)]
{sns_caption}

🔍 네이버 검색창에 [{cls.OFFICIAL_KEYWORD}] 검색하고
실시간 외국인 수급과 퀀트 적정주가를 1초 만에 확인해보세요! 🚀
🔗 프로필 링크(@stockmaster_ai) 또는 공식 사이트: {cls.OFFICIAL_URL}

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

다들 이 종목 어떻게 보고 계심? 댓글로 의견 남겨보셈 👇

{threads_tags}

💬 [첫 번째 댓글 (알고리즘 보호 전환 링크)]
👉 실시간 AI 퀀트 적정주가 계산기: {cls.OFFICIAL_URL}
(또는 네이버에 '{cls.OFFICIAL_KEYWORD}' 검색)


[3] 📘 페이스북 (Facebook) 피드 가이드
--------------------------------------------------------------------------------
📌 [페북 피드 본문 (카드뉴스 5장 앨범 첨부)]
{s1_title} 📊

{s1_sub}

깜깜이 뇌동매매는 그만! 퀀트 지표로 확인하는 실전 투자 인사이트.
카드뉴스를 옆으로 넘겨서 5장으로 확인해보세요. 👉

{fb_tags}

💬 [첫 번째 댓글 (스텔스 전환 링크)]
👉 공식 사이트에서 무료 진단: {cls.OFFICIAL_URL}
👉 네이버 검색창에 [{cls.OFFICIAL_KEYWORD}] 검색!


[4] 📰 네이버 포스트 (Naver Post) - [카드형] 에디터 가이드
--------------------------------------------------------------------------------
📌 [추천 제목]: {s1_title}
🏷️ [추천 시리즈]: 스마트 개미를 위한 AI 퀀트 투자 백과

🖼️ [슬라이드 업로드 매핑]:
• [표지 1/5]: slide_1.png ➔ {s1_title} ({s1_sub})
• [공감 2/5]: slide_2.png ➔ {s2_title}
• [수급 3/5]: slide_3.png ➔ {s3_title}
• [퀀트 4/5]: slide_4.png ➔ {s4_title}
• [엔딩 5/5]: slide_5.png ➔ 주식 찬반 토론 & 네이버 검색 [{cls.OFFICIAL_KEYWORD}] CTA

🏷️ [네이버 포스트 태그]:
{naver_tags}


[5] 📗 네이버 블로그 (Naver Blog) - 카드뉴스 연속 스크롤 가이드
--------------------------------------------------------------------------------
📌 [블로그 추천 제목]: {s1_title} | {theme_name} 퀀트 분석

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
💡 오늘의 투자 토론: {debate_q}
지금 네이버 검색창에 [{cls.OFFICIAL_KEYWORD}]을 검색하시고 객관적인 퀀트 지표를 무료로 확인하세요.

🏷️ [네이버 블로그 태그]:
{naver_tags}


[6] ☕ 네이버 카페 (Naver Cafe) - 바이럴 침투 가이드
--------------------------------------------------------------------------------
⚠️ [카페 침투 절대 철칙 - Zero-URL 원칙]
링크(URL) 삽입 절대 금지! 오직 "네이버에 {cls.OFFICIAL_KEYWORD} 한번 검색해보세요"로만 유도합니다.

📌 [추천 게시글 제목]: {s1_title} 다들 어떻게 대응하시나요?
📝 [추천 본문]:
{s2_sub}
요즘 변동성이 커서 분할매수 타이밍 잡기가 쉽지 않네요 ㅠㅠ
선배님들은 이 구간 어떻게 보시는지 조언 부탁드립니다!

💬 [댓글 침투 스크립트]:
"저도 뇌동매매 줄이려고 {s3_title} 지표 참고하고 있어요 ㅋㅋㅋ 네이버에 '{cls.OFFICIAL_KEYWORD}' 검색하면 외인 수급이랑 적정주가 바로 나와서 편하더라고요"


[7] ✈️ 텔레그램 (Telegram) - 5장 앨범 가이드
--------------------------------------------------------------------------------
📌 [텔레그램 캡션]:
📈 {s1_title}

{s1_sub}
• 외국인/기관 실시간 쌍끌이 순매수 레이더
• 객관적 AI 퀀트 적정주가 & 밸류에이션

🔗 공식 사이트 바로가기: {cls.OFFICIAL_URL}
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
        fb_text: str,
        naver_clip_text: Optional[str] = None
    ) -> str:
        """
        1080x1920 숏폼 영상 전용 6대 SNS 통합 포스팅 가이드 생성
        """
        matrix = StockHashtagMatrix()
        insta_tags = " ".join(matrix.get_instagram_hashtags(topic_id=topic_id, count=18))
        threads_tags = " ".join(matrix.get_threads_hashtags(topic_id=topic_id))
        fb_tags = " ".join(matrix.get_facebook_hashtags(topic_id=topic_id))
        shorts_tags = matrix.get_shorts_hashtags(topic_id=topic_id)

        clip_text = naver_clip_text or fb_text

        guide = f"""================================================================================
🎬 [스톡마스터 AI] 1080x1920 숏폼 6대 SNS 원클릭 포스팅 가이드
================================================================================
주제 번호: #{topic_id} [{theme_name}]
테마 코드: {theme_code}
영상 규격: 1080x1920 (9:16 세로 풀HD 숏폼, 22초)
공식 네이버 검색어: [{cls.OFFICIAL_KEYWORD}] (띄어쓰기 필수!)
공식 랜딩 URL: {cls.OFFICIAL_URL}
================================================================================

[1] 🔴 유튜브 쇼츠 (YouTube Shorts) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [쇼츠 제목 (Title)]
{yt_title}

📌 [쇼츠 설명 (Description)]
{yt_desc}

📌 [고정 댓글 (Pinned Comment)]
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

🔗 Bio Link: @stockmaster_ai -> {cls.OFFICIAL_URL}
🔍 네이버에 [{cls.OFFICIAL_KEYWORD}] 검색!

📌 [릴스 알고리즘 노출 폭발 18~20개 4단 해시태그 풀]
{insta_tags}


[4] 🧵 스레드 (Threads) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [스레드 본문 (텍스트 바이럴 & 공감 질문형)]
{threads_text}

{threads_tags}

💬 [첫 번째 댓글 (전환 링크)]
👉 실시간 외국인 수급 & 퀀트 적정주가 확인하기: {cls.OFFICIAL_URL}


[5] 📘 페이스북 릴스 (Facebook Reels) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [피드 본문 (알고리즘 도달 극대화)]
{fb_text}

{fb_tags}

💬 [첫 번째 댓글 (스텔스 전환 링크)]
👉 네이버에 [{cls.OFFICIAL_KEYWORD}] 검색 또는 바로가기: {cls.OFFICIAL_URL}


[6] 🟢 네이버 클립 (Naver Clip) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [클립 본문 및 검색어 유도]
{clip_text}

🔍 네이버 검색창에 [{cls.OFFICIAL_KEYWORD}] 검색!
================================================================================
"""
        return guide
