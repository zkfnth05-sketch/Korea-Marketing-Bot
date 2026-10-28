# -*- coding: utf-8 -*-
"""
[Aura 전용 독립 모듈] AuraDomesticSNSCopywriter (brands/aura/aura_domestic_sns_copywriter.py)
=============================================================================
• 역할: 💖 Aura AI 데이팅 전용 4대 SNS(유튜브 쇼츠, 틱톡, 네이버 클립, 메타 릴스)
        알고리즘 도달률 및 라운지 유입 극대화 [초고관여 바이럴 스토리텔링 카피라이팅] 엔진
• 전문 분야: 2030 데이팅, 소개팅 꿀팁, 카톡 대화법, 연애 심리, MBTI 궁합, 핫플 데이트
• 핵심 특징:
  1. Aura 전담 9단 키 체인(GeminiSmartClient) 연동 및 실시간 롤오버
  2. 최신 gemini-2.5-flash / gemini-2.0-flash 정식 모델 호출
  3. 플랫폼별 초고밀도 연애 스토리텔링 및 시선 강탈 훅 100% AI 작문
  4. 네이버 공식 검색어 [아우라AI데이팅] 각인 + 프로필 링크 CTA + 4단 해시태그 패키지
"""

import re
import json
import logging
import urllib.request
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from core.gemini_smart_client import GeminiSmartClient

logger = logging.getLogger("AuraDomesticSNSCopywriter")

FORBIDDEN_WORDS = [
    "한정 이벤트", "선착순 마감", "파격 할인", "수강생 모집",
    "VIP 리딩방", "원금 보장", "수익률 100% 보장", "사은품 증정",
    "오늘만 이 가격", "마감 임박", "선착순 100명", "선착순 50명"
]

AURA_TOPIC_HOOKS = {
    1: "소개팅 나갔는데 분위기 싸할 때 1초 만에 합법 탈출하는 법 ㄷㄷ",
    2: "카톡 답장 느린 사람 100% 심리 분석 (읽씹 대처법)",
    3: "남초 제로, 성비 50:50 데이팅 라운지 실화냐?",
    4: "첫 만남에서 호감도 3배 올리는 스몰토크 치트키",
    5: "2030 남녀가 뽑은 최악의 소개팅 착장 1위는?",
    6: "소개팅 애프터 신청 골든타임 & 카톡 멘트 추천",
    7: "성수동/연남동 분위기 터지는 소개팅 핫플 추천",
    8: "MBTI 유형별 절대 실패 없는 연애 공략법"
}


class AuraDomesticSNSCopywriter:
    """💖 Aura AI 데이팅 전용 4대 SNS 초고관여 바이럴 카피라이터"""

    def __init__(self):
        self.brand_name = "💖 Aura AI 데이팅"
        self.official_keyword = "아우라AI데이팅"
        self.url = "https://aura-ai-dating.vercel.app/"
        self.naver_blog_url = "https://blog.naver.com/zkfnth01"
        self.search_phrase = "네이버 검색창에 [아우라AI데이팅]을 검색해보세요!"
        self.core_value = "유령회원 제로 50:50 황금 성비 청정 데이팅 라운지, AI 이상형 매칭 & 1:1 비밀 쪽지 100% 무료"
        self.target = "2030 직장인 및 대학생 싱글 남녀"
        self.client = None
        self._init_client()

    def _init_client(self):
        try:
            self.client = GeminiSmartClient(service_id="aura")
        except Exception as e:
            logger.warning(f"Aura GeminiSmartClient 초기화 실패: {e}")
            self.client = None

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        for fw in FORBIDDEN_WORDS:
            text = text.replace(fw, "")
        return text.strip()

    def fetch_live_trend_keywords(self) -> List[str]:
        """Google Trends KR 실시간 인기 키워드 수집"""
        trends = []
        try:
            url = "https://trends.google.com/trending/rss?geo=KR"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                xml_data = resp.read()
                root = ET.fromstring(xml_data)
                for item in root.findall(".//item"):
                    title = item.find("title")
                    if title is not None and title.text:
                        clean = re.sub(r'[^가-힣0-9a-zA-Z]', '', title.text.strip())
                        if 2 <= len(clean) <= 12:
                            trends.append(f"#{clean}")
                    if len(trends) >= 6:
                        break
        except Exception:
            pass
        return trends

    def build_hybrid_hashtags(self, topic_id: int = 1, count: int = 15) -> List[str]:
        """Aura 전용 해시태그 + 실시간 트렌드 융합"""
        tags = [
            "#아우라AI데이팅", "#소개팅", "#연애꿀팁", "#2030소개팅",
            "#데이트명소", "#연애심리", "#카톡대화법", "#Shorts", "#TikTok", "#Reels"
        ]
        live = self.fetch_live_trend_keywords()
        tags.extend(live)

        seen = set()
        unique = []
        for t in tags:
            ct = t.strip() if t.startswith("#") else f"#{t.strip()}"
            if ct not in seen:
                seen.add(ct)
                unique.append(ct)
            if len(unique) >= count:
                break
        return unique

    def _call_gemini(self, prompt: str) -> Optional[str]:
        if not self.client:
            return None
        models = ["gemini-2.5-flash", "gemini-2.0-flash"]
        for m in models:
            try:
                resp = self.client.generate_content(model=m, contents=prompt)
                if resp and resp.text and len(resp.text.strip()) > 50:
                    logger.info(f"✨ [Aura Copywriter] {m} 카피라이팅 생성 성공!")
                    return resp.text.strip()
            except Exception as e:
                logger.warning(f"Aura 모델 {m} 호출 실패: {e}")
                continue
        return None

    def generate_full_package(
        self,
        topic_id: int = 1,
        topic_title: Optional[str] = None,
        media_type: str = "shorts"
    ) -> Dict[str, Any]:
        """💖 Aura 전용 4대 SNS 초고관여 바이럴 패키징"""
        hook_title = topic_title or AURA_TOPIC_HOOKS.get(topic_id, f"Aura 데이팅 연애 비법 #{topic_id}")
        hashtags = self.build_hybrid_hashtags(topic_id=topic_id, count=15)
        short_tags = " ".join(hashtags[:8])
        full_tags = " ".join(hashtags)

        prompt = f"""
당신은 대한민국 1위 2030 연애/데이팅 바이럴 마케팅 총괄 디렉터입니다.
아래 브랜드와 주제 정보를 바탕으로 2030 솔로 남녀의 폭풍 공감과 댓글 토론을 이끌어내는 [4대 SNS 플랫폼별 초고밀도 스토리텔링 카피 패키지]를 작성하세요.

[브랜드 정보]
- 브랜드명: {self.brand_name}
- 네이버 공식 검색어: [{self.official_keyword}]
- 핵심 가치: {self.core_value}
- 타깃층: {self.target}
- 검색 유도 문구: {self.search_phrase}

[콘텐츠 정보]
- 유형: 2030 연애/소개팅 숏폼 영상
- 주제 #{topic_id}: {hook_title}

[플랫폼별 작성 지침 - 분량을 풍부하고 감성적으로 작성할 것]
1. viral_title: 2030 시선을 단 1초 만에 사로잡는 강력한 훅 제목 (이모지 포함, 35자 내외)
2. youtube_desc: 유튜브 쇼츠 상세 설명문 (풍부한 줄바꿈 포함, 본문 내 외부 URL 절대 삽입 금지)
   - [공감 폭발 인트로 2~3줄: "소개팅 나가서 이런 경험 다들 한 번쯤 있으시죠?"]
   - [💡 실전 연애 치트키 3대 포인트] (번호 매겨서 구체적 서술)
   - [공식 라운지는 첫 번째 댓글 참조 유도]
3. youtube_pinned: 시청자 댓글 참여 유도 고정 댓글 (공식 바로가기 링크 단독 배치)
4. tiktok_caption: 틱톡 알고리즘 최적화 본문 (강렬한 훅 2줄 + 핵심 요약 2줄 + 첫 댓글 참조 안내 + 검색어)
5. naver_clip_desc: 네이버 클립용 280자 내외 고밀도 실전 연애 정보 압축 카피 (첫 댓글 참조 안내 포함)
6. instagram_caption: 인스타그램 릴스/피드용 감성 스토리텔링 본문 (공감 서사 + 체크리스트 + 첫 댓글 링크 참조 안내)
7. facebook_caption: 페이스북용 깊이 있는 연애 칼럼 본문 (공감 서사 + 실전 가이드 + 첫 번째 댓글 링크 안내)
※ [절대 원칙] 모든 본문(캡션/설명문)에는 외부 링크(http/https)를 절대 넣지 말고 '첫 번째 댓글 참조'를 안내하세요!

반드시 아래 JSON 형식으로만 응답하세요:
{{
  "viral_title": "...",
  "youtube_desc": "...",
  "youtube_pinned": "...",
  "tiktok_caption": "...",
  "naver_clip_desc": "...",
  "instagram_caption": "...",
  "facebook_caption": "..."
}}
"""
        gemini_text = self._call_gemini(prompt)
        parsed = {}
        if gemini_text:
            try:
                json_match = re.search(r'\{.*\}', gemini_text, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
            except Exception:
                pass

        v_title = self._clean_text(parsed.get("viral_title")) or hook_title

        # YouTube (본문 URL 0% - 알고리즘 다운랭킹 방지 & 첫 댓글 참조 필수)
        yt_d = self._clean_text(parsed.get("youtube_desc"))
        if not yt_d:
            yt_d = (
                f"📌 {v_title}\n\n"
                f"소개팅이나 썸 탈 때 '왜 항상 이렇게 흘러갈까?' 고민되셨다면 주목!\n"
                f"2030 남녀가 직접 검증한 실전 꿀팁을 지금 바로 공개합니다.\n\n"
                f"💡 실전 연애 치트키 3대 포인트:\n"
                f"1. {self.core_value}\n"
                f"2. 상대방의 무의식적 호감을 이끌어내는 대화 텐션 유지법\n"
                f"3. 부담 없는 자연스러운 애프터 신청 타이밍 잡기\n\n"
                f"👉 {self.search_phrase}"
            )
        yt_desc_full = (
            f"{yt_d}\n\n"
            f"👉 {self.search_phrase}\n\n"
            f"{short_tags}"
        )

        yt_p = (
            f"💖 [Aura AI 데이팅] 모든 기능 무료 사용하기 (3초 무료 입장):\n"
            f"👉 {self.url}\n\n"
            f"🔍 네이버 검색창에 [{self.official_keyword}]을 검색해보세요!\n\n"
            f"✨ 50:50 황금 성비 라운지를 3초 만에 무료로 이용해 보세요!\n"
            f"(네이버 검색: {self.official_keyword})"
        )

        # TikTok (본문 URL 0% & 네이버 검색 유도)
        tk_c = self._clean_text(parsed.get("tiktok_caption"))
        if not tk_c:
            tk_c = (
                f"{v_title}\n\n"
                f"소개팅 성공 확률 3배 올려주는 실전 치트키! 🔥\n"
                f"👉 {self.search_phrase}\n"
                f"50:50 성비 청정 라운지 무료 입장 💖"
            )
        tk_caption_full = (
            f"{tk_c}\n\n"
            f"👉 {self.search_phrase}\n\n"
            f"{short_tags}"
        )

        # Naver Clip (본문 URL 0% & 네이버 검색 유도)
        nv_d = self._clean_text(parsed.get("naver_clip_desc"))
        if not nv_d:
            nv_d = (
                f"{v_title}\n\n"
                f"Aura 데이팅에서 제안하는 2030 실전 연애 브리핑!\n"
                f"유령회원 없는 50:50 청정 라운지에서 AI 이상형 매칭을 시작해보세요.\n\n"
                f"🔍 네이버 검색: [{self.official_keyword}]"
            )
        nv_desc_full = (
            f"{nv_d}\n\n"
            f"👉 {self.search_phrase}\n\n"
            f"{short_tags}"
        )

        # Meta Reels (본문 URL 0% & 네이버 검색 유도)
        ig_c = self._clean_text(parsed.get("instagram_caption"))
        if not ig_c:
            ig_c = (
                f"✨ {v_title}\n\n"
                f"\"이것만 알아도 소개팅 애프터 확률 90% 돌파!\" 💕\n\n"
                f"✔️ 50:50 황금 성비 청정 라운지\n"
                f"✔️ AI 맞춤 이상형 매칭 & 1:1 비밀 쪽지 100% 무료\n"
                f"✔️ 알바/유령회원 없는 100% 실명 인증 회원\n\n"
                f"👉 {self.search_phrase}"
            )
        ig_caption_full = (
            f"{ig_c}\n\n"
            f"👉 {self.search_phrase}\n\n"
            f"{full_tags}"
        )

        # Facebook (본문 URL 0% & 네이버 검색 유도)
        fb_c = self._clean_text(parsed.get("facebook_caption"))
        if not fb_c:
            fb_c = (
                f"📢 {v_title}\n\n"
                f"2030 직장인과 대학생을 위한 스마트 데이팅 솔루션!\n"
                f"{self.core_value}\n\n"
                f"💡 지금 네이버에서 [{self.official_keyword}]을 검색해보세요!"
            )
        fb_caption_full = (
            f"{fb_c}\n\n"
            f"👉 {self.search_phrase}\n\n"
            f"{short_tags}"
        )

        # 🛡️ 본문 내 모든 URL 전면 소독 (알고리즘 다운랭킹 방지 및 네이버 공식 검색어로 치환)
        search_sub = f"👉 네이버 검색: [{self.official_keyword}]"
        yt_desc_full = re.sub(r'https?://\S+', search_sub, yt_desc_full)
        tk_caption_full = re.sub(r'https?://\S+', search_sub, tk_caption_full)
        nv_desc_full = re.sub(r'https?://\S+', search_sub, nv_desc_full)
        ig_caption_full = re.sub(r'https?://\S+', search_sub, ig_caption_full)
        fb_caption_full = re.sub(r'https?://\S+', search_sub, fb_caption_full)

        return {
            "title": v_title,
            "youtube": {
                "title": f"{v_title} #{self.official_keyword} #Shorts",
                "description": yt_desc_full,
                "pinned_comment": yt_p,
                "tags": hashtags
            },
            "tiktok": {
                "caption": tk_caption_full,
                "tags": hashtags[:8]
            },
            "naver_clip": {
                "title": v_title[:45],
                "description": nv_desc_full,
                "tags": hashtags[:8]
            },
            "meta_reels": {
                "caption": ig_caption_full,
                "tags": hashtags
            },
            "facebook": {
                "caption": fb_caption_full,
                "tags": hashtags[:8]
            },
            "hashtags": hashtags
        }
