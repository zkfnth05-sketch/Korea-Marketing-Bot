# -*- coding: utf-8 -*-
"""
[Insurance 전용 독립 모듈] InsuranceDomesticSNSCopywriter (brands/insurance/insurance_domestic_sns_copywriter.py)
=============================================================================
• 역할: 🛡️ 보험 리밸런스 (TheFirst Life) 전용 4대 SNS(유튜브 쇼츠, 틱톡, 네이버 클립, 메타 릴스)
        알고리즘 도달률 및 가계부 절약 상담 유입 극대화 [초고관여 금융/보험 카피라이팅] 엔진
• 전문 분야: 34개 보험사 실시간 요율 비교, 실비/운전자/암/뇌심혈관 리모델링, 중복 특약 다이어트
• 핵심 특징:
  1. Insurance 전담 9단 키 체인(GeminiSmartClient) 연동 및 실시간 롤오버
  2. 최신 gemini-2.5-flash / gemini-2.0-flash 정식 모델 호출
  3. 플랫폼별 초고밀도 금융 분석/다이어트 팁 및 시선 강탈 훅 100% AI 작문
  4. 네이버 공식 검색어 [보험비교] 각인 + 34개사 무료 견적 CTA + 4단 해시태그 패키지
"""

import re
import json
import logging
import urllib.request
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from core.gemini_smart_client import GeminiSmartClient

logger = logging.getLogger("InsuranceDomesticSNSCopywriter")

FORBIDDEN_WORDS = [
    "한정 이벤트", "선착순 마감", "파격 할인", "수강생 모집",
    "VIP 리딩방", "원금 보장", "수익률 100% 보장", "사은품 증정",
    "오늘만 이 가격", "마감 임박", "선착순 100명", "선착순 50명"
]

INSURANCE_TOPIC_HOOKS = {
    1: "병원도 안 가는데 매달 11만원 내던 실비 1만2천원으로 줄인 비결! 💡",
    2: "강남 출근길 직장인 1만3천원 운전자보험 가성비 꿀팁! 🚗",
    3: "건강검진 전 필수 확인! 일반암 vs 유사암 보장 범위 팩트체크 🏥",
    4: "40대 가장 필수 점검! 뇌출혈 vs 뇌혈관질환 보장 차이 총정리 🧠",
    5: "지인 부탁으로 가입한 보험 손익 분석 & 1억 보장 맞춤 리모델링 📋",
    6: "30살 넘어 열어본 부모님 가입 100세 만기 보험 알뜰 리모델링 👶",
    7: "매달 30만원 새던 가족 보험 34개사 비교 다이어트 비결 🔍",
    8: "전화번호 요구 없이 AI 역추정으로 찾는 최저가 가성비 보험 🤖"
}


class InsuranceDomesticSNSCopywriter:
    """🛡️ 보험 리밸런스 전용 4대 SNS 초고관여 바이럴 카피라이터"""

    def __init__(self):
        self.brand_name = "🛡️ 보험 리밸런스 (TheFirst Life)"
        self.official_keyword = "보험비교"
        self.url = "https://thefirst-life.vercel.app/"
        self.naver_blog_url = "https://blog.naver.com/thefirst-life"
        self.search_phrase = "네이버 검색창에 [보험비교]를 검색해보세요!"
        self.core_value = "전화번호 요구 없이 34개 보험사 실시간 요율 즉시 역추정 비교, 중복 특약 정리로 월 15만원 다이어트"
        self.target = "2040 직장인 및 가계부 고정지출 절약이 필요한 금융 소비자"
        self.client = None
        self._init_client()

    def _init_client(self):
        try:
            self.client = GeminiSmartClient(service_id="insurance")
        except Exception as e:
            logger.warning(f"Insurance GeminiSmartClient 초기화 실패: {e}")
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
        """Insurance 전용 해시태그 + 실시간 트렌드 융합"""
        tags = [
            "#보험비교", "#실손보험", "#보험다이어트", "#보험리모델링",
            "#운전자보험", "#암보험", "#가계부절약", "#재테크꿀팁", "#Shorts", "#TikTok", "#Reels"
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
                    logger.info(f"✨ [Insurance Copywriter] {m} 카피라이팅 생성 성공!")
                    return resp.text.strip()
            except Exception as e:
                logger.warning(f"Insurance 모델 {m} 호출 실패: {e}")
                continue
        return None

    def generate_full_package(
        self,
        topic_id: int = 1,
        topic_title: Optional[str] = None,
        media_type: str = "shorts"
    ) -> Dict[str, Any]:
        """🛡️ Insurance 전용 4대 SNS 초고관여 바이럴 패키징"""
        hook_title = topic_title or INSURANCE_TOPIC_HOOKS.get(topic_id, f"보험 리밸런스 가이드 #{topic_id}")
        hashtags = self.build_hybrid_hashtags(topic_id=topic_id, count=15)
        short_tags = " ".join(hashtags[:8])
        full_tags = " ".join(hashtags)

        prompt = f"""
당신은 대한민국 1위 금융/보험 리밸런싱 바이럴 마케팅 총괄 디렉터입니다.
아래 브랜드와 주제 정보를 바탕으로 매달 새어나가는 고정지출에 고민하는 소비자들의 이목을 사로잡는 [4대 SNS 플랫폼별 초고밀도 금융 카피 패키지]를 작성하세요.

[브랜드 정보]
- 브랜드명: {self.brand_name}
- 네이버 공식 검색어: [{self.official_keyword}]
- 핵심 가치: {self.core_value}
- 타깃층: {self.target}
- 검색 유도 문구: {self.search_phrase}

[콘텐츠 정보]
- 유형: 금융/보험 정보성 숏폼 영상
- 주제 #{topic_id}: {hook_title}

[플랫폼별 작성 지침 - 분량을 풍부하고 전문적인 팩트 중심으로 작성할 것]
1. viral_title: 가계부 고정지출을 절약하고 싶은 시선을 1초 만에 사로잡는 강력한 훅 제목 (이모지 포함, 35자 내외)
2. youtube_desc: 유튜브 쇼츠 상세 설명문 (풍부한 줄바꿈 포함)
   - [상황 공감 인트로 2~3줄: "매달 나가는 보험료, 제대로 보장받고 계신가요?"]
   - [💡 실전 보험 다이어트 3대 팩트체크] (번호 매겨서 상세 서술)
   - [전화번호 없는 34개사 무료 비교 안내]
3. youtube_pinned: 시청자 참여를 유도하는 고정 댓글 (질문 던지기 + 네이버 검색어 안내)
4. tiktok_caption: 틱톡 알고리즘 최적화 본문 (강렬한 절약 훅 2줄 + 핵심 요약 2줄 + 검색어)
5. naver_clip_desc: 네이버 클립용 280자 내외 고밀도 실전 금융 정보 압축 카피
6. instagram_caption: 인스타그램 릴스/피드용 감각적인 재테크 스토리텔링 본문 (공감 서사 + 체크포인트 + 프로필 링크 유도)
7. facebook_caption: 페이스북용 깊이 있는 금융 칼럼 본문 (가계부 절약 서사 + 실전 가이드 + 첫 댓글 안내)

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

        # YouTube
        yt_d = self._clean_text(parsed.get("youtube_desc"))
        if not yt_d:
            yt_d = (
                f"📌 {v_title}\n\n"
                f"매달 통장에서 빠져나가는 보험료, 혹시 중복 가입되어 새고 있진 않으신가요?\n"
                f"34개 보험사 요율을 데이터로 비교해 불필요한 특약만 쏙 뺀 실전 꿀팁을 전해드립니다.\n\n"
                f"💡 실전 보험 다이어트 3대 팩트체크:\n"
                f"1. {self.core_value}\n"
                f"2. 지인 부탁으로 가입한 중복 특약 및 불필요 담보 즉시 정리\n"
                f"3. 전화번호 노출 없이 AI 역추정으로 찾는 최저가 가성비 견적\n\n"
                f"👉 {self.search_phrase}"
            )
        yt_desc_full = f"{yt_d}\n\n🔍 {self.search_phrase}\n🌐 34개사 무료 견적: {self.url}\n\n{short_tags}"

        yt_p = self._clean_text(parsed.get("youtube_pinned"))
        if not yt_p:
            yt_p = (
                f"📌 여러분의 매달 지출되는 보험료는 얼마인가요? 댓글로 공유해주세요!\n\n"
                f"전화번호 입력 없는 34개사 실시간 요율 비교는 네이버에 👉 [ {self.official_keyword} ] 검색하시면 바로 확인 가능합니다! 🛡️"
            )

        # TikTok
        tk_c = self._clean_text(parsed.get("tiktok_caption"))
        if not tk_c:
            tk_c = (
                f"{v_title}\n\n"
                f"매달 15만원 새던 보험료 1분 만에 다이어트하는 법! 💡\n"
                f"👉 {self.search_phrase}\n"
                f"전화번호 없이 34개사 실시간 비교 📲"
            )
        tk_caption_full = f"{tk_c}\n\n{short_tags}"

        # Naver Clip
        nv_d = self._clean_text(parsed.get("naver_clip_desc"))
        if not nv_d:
            nv_d = (
                f"{v_title}\n\n"
                f"TheFirst Life에서 전해드리는 실전 가계부 절약 브리핑!\n"
                f"전화번호 요구 없이 34개사 요율을 한눈에 비교하고 중복 특약을 정리하세요.\n\n"
                f"🔍 네이버 검색: [{self.official_keyword}]"
            )
        nv_desc_full = f"{nv_d}\n\n{short_tags}"

        # Meta Reels
        ig_c = self._clean_text(parsed.get("instagram_caption"))
        if not ig_c:
            ig_c = (
                f"✨ {v_title}\n\n"
                f"\"보험료는 줄이고 보장은 2배로 넓히는 황금 법칙!\" 📋\n\n"
                f"✔️ 34개 보험사 실시간 요율 즉시 역추정\n"
                f"✔️ 전화번호 입력 없는 안심 무료 견적\n"
                f"✔️ 불필요한 중복 특약 정리로 가계부 고정지출 절약\n\n"
                f"🔗 지금 프로필 상단 링크를 누르시거나\n"
                f"👉 {self.search_phrase}"
            )
        ig_caption_full = f"{ig_c}\n\n{full_tags}"

        # Facebook
        fb_c = self._clean_text(parsed.get("facebook_caption"))
        if not fb_c:
            fb_c = (
                f"📢 {v_title}\n\n"
                f"스마트한 금융 소비자를 위한 가계부 고정지출 다이어트 리포트입니다.\n"
                f"{self.core_value}\n\n"
                f"💡 지금 네이버에서 [{self.official_keyword}]을 검색해보세요!"
            )
        fb_caption_full = f"{fb_c}\n\n👇 [첫 번째 댓글]의 34개사 무료 비교 링크를 확인하세요!\n\n{short_tags}"

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
