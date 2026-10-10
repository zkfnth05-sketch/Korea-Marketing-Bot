# -*- coding: utf-8 -*-
"""
[신규 모듈 업그레이드] GeminiDomesticSNSCopywriter (core/gemini_domestic_sns_copywriter.py)
=============================================================================
• 역할: 국내 3대 브랜드(💖 Aura 데이팅, 🛡️ 보험 리밸런스, 📈 StockMaster AI)의
        숏폼 및 카드뉴스 송출 시, 4대 SNS 채널(유튜브 쇼츠, 틱톡, 네이버 클립, 메타 릴스)의
        알고리즘 도달률과 전환율을 극대화하는 [초고관여 바이럴 스토리텔링 캡션 + 제목 + 해시태그 + 고정댓글] 패키지 생성 엔진
• 핵심 개혁:
  1. [GeminiSmartClient 연동]: 무료키 6개 + 유료키 2개 + 기본키 1개 (총 9개 키 체인 자동 롤오버)
  2. [최신 gemini-2.5-flash / gemini-2.0-flash 정식 모델 호출]
  3. [풍부한 고밀도 스토리텔링 본문 생성]:
     - 유튜브 쇼츠: 상황 공감 서사 + 3대 팩트체크 리스트 + 네이버 검색어 유도 + 바이럴 고정댓글
     - 틱톡: 1.5초 시선 강탈 훅 + 핵심 3줄 요약 + 공식 검색어
     - 네이버 클립: 글자 수 최적화(280자 내외) 고밀도 실전 정보 압축 카피
     - 인스타그램 릴스/피드: 깊이 있는 감성/정보 서사 + 체크포인트 + 프로필 링크 유도
     - 페이스북 릴스/피드: 긴 호흡의 칼럼형 정보 본문 + 첫 댓글 유도
  4. [공식 검색어 각인 + 전환 유도 CTA + 4단 하이브리드 해시태그 완벽 패키징]
"""

import os
import re
import json
import random
import logging
import urllib.request
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from core.gemini_smart_client import GeminiSmartClient

logger = logging.getLogger("GeminiDomesticSNSCopywriter")

FORBIDDEN_WORDS = [
    "한정 이벤트", "선착순 마감", "파격 할인", "수강생 모집",
    "VIP 리딩방", "원금 보장", "수익률 100% 보장", "사은품 증정",
    "오늘만 이 가격", "마감 임박", "선착순 100명", "선착순 50명"
]

BRAND_SPECS = {
    "aura": {
        "name": "💖 Aura AI 데이팅",
        "official_keyword": "아우라AI데이팅",
        "url": "https://aura-ai-dating.vercel.app/",
        "naver_blog_url": "https://blog.naver.com/zkfnth01",
        "cta_label": "공식 라운지 입장",
        "ig_handle": "@aura_ai_dating",
        "core_value": "유령회원 제로 50:50 황금 성비 청정 데이팅 라운지, AI 이상형 매칭 & 1:1 비밀 쪽지 100% 무료",
        "target": "2030 직장인 및 대학생 싱글 남녀",
        "search_phrase": "네이버 검색창에 [아우라AI데이팅]을 검색해보세요!",
        "hook_titles": {
            1: "소개팅 나갔는데 분위기 싸할 때 1초 만에 합법 탈출하는 법 ㄷㄷ",
            2: "카톡 답장 느린 사람 100% 심리 분석 (읽씹 대처법)",
            3: "남초 제로, 성비 50:50 데이팅 라운지 실화냐?",
            4: "첫 만남에서 호감도 3배 올리는 스몰토크 치트키",
            5: "2030 남녀가 뽑은 최악의 소개팅 착장 1위는?",
            6: "소개팅 애프터 신청 골든타임 & 카톡 멘트 추천",
            7: "성수동/연남동 분위기 터지는 소개팅 핫플 추천",
            8: "MBTI 유형별 절대 실패 없는 연애 공략법"
        }
    },
    "insurance": {
        "name": "🛡️ 보험 리밸런스 (TheFirst Life)",
        "official_keyword": "보험비교",
        "url": "https://thefirst-life.vercel.app/",
        "naver_blog_url": "https://blog.naver.com/thefirst-life",
        "cta_label": "34개사 무료 견적",
        "ig_handle": "@goldmomofficial",
        "core_value": "전화번호 요구 없이 34개 보험사 실시간 요율 즉시 역추정 비교, 중복 특약 정리로 월 15만원 다이어트",
        "target": "2040 직장인 및 가계부 고정지출 절약이 필요한 금융 소비자",
        "search_phrase": "네이버 검색창에 [보험비교]를 검색해보세요!",
        "hook_titles": {
            1: "병원도 안 가는데 매달 11만원 내던 실비 1만2천원으로 줄인 비결! 💡",
            2: "강남 출근길 직장인 1만3천원 운전자보험 가성비 꿀팁! 🚗",
            3: "건강검진 전 필수 확인! 일반암 vs 유사암 보장 범위 팩트체크 🏥",
            4: "40대 가장 필수 점검! 뇌출혈 vs 뇌혈관질환 보장 차이 총정리 🧠",
            5: "지인 부탁으로 가입한 보험 손익 분석 & 1억 보장 맞춤 리모델링 📋",
            6: "30살 넘어 열어본 부모님 가입 100세 만기 보험 알뜰 리모델링 👶",
            7: "매달 30만원 새던 가족 보험 34개사 비교 다이어트 비결 🔍",
            8: "전화번호 요구 없이 AI 역추정으로 찾는 최저가 가성비 보험 🤖"
        }
    },
    "stock": {
        "name": "📈 StockMaster AI",
        "official_keyword": "주식AI",
        "url": "https://stockmaster-ai.vercel.app/",
        "naver_blog_url": "https://blog.naver.com/stockmaster_ai",
        "cta_label": "실시간 퀀트 분석 확인",
        "ig_handle": "@stockmaster_ai",
        "core_value": "감정 배제 100% 퀀트 데이터 기반 국내외 증시 실시간 수급 및 외국인/기관 매집 패턴 분석",
        "target": "2050 개인 스마트 주식 투자자 및 ETF 트레이더",
        "search_phrase": "네이버 검색창에 [주식AI]를 검색해보세요!",
        "hook_titles": {
            1: "외국인이 3일 연속 쓸어 담은 삼성전자/SK하이닉스 수급 비밀 📈",
            2: "기관이 100억 매집 중인 2차전지/로봇 숨은 주도주 팩트체크 🔋",
            3: "하락장에서도 살아남는 고배당 방어주 TOP 3 포트폴리오 🛡️",
            4: "미국 빅테크 vs 국내 반도체, 지금 당장 비중 늘려야 할 곳은? 🌐",
            5: "개미들 다 털릴 때 기관이 몰래 담는 과열 종목 위험 신호 포착 🚨",
            6: "단타 실패 줄이는 퀀트 알고리즘 골든크로스 매매 타이밍 📊"
        }
    }
}


class GeminiDomesticSNSCopywriter:
    """국내 3대 브랜드 전용 4대 SNS 초고관여 캡션 & 제목 & 해시태그 카피라이터"""

    def __init__(self, brand: str = "aura"):
        self.brand = brand.lower()
        self.spec = BRAND_SPECS.get(self.brand, BRAND_SPECS["aura"])
        self.client = None
        self._init_client()

    def _init_client(self):
        try:
            self.client = GeminiSmartClient(service_id=self.brand)
        except Exception as e:
            logger.warning(f"GeminiSmartClient 초기화 실패: {e}")
            self.client = None

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        for fw in FORBIDDEN_WORDS:
            text = text.replace(fw, "")
        return text.strip()

    def fetch_live_trend_keywords(self) -> List[str]:
        """Google Trends KR 실시간 인기 키워드 수집 (빠른 타임아웃 3초)"""
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
        """브랜드 고유 해시태그 + 매트릭스 롱테일 + 실시간 트렌드 융합"""
        tags = []
        if self.brand == "aura":
            tags.extend(["#아우라AI데이팅", "#소개팅", "#연애꿀팁", "#2030소개팅", "#데이트명소", "#Shorts", "#TikTok", "#Reels"])
        elif self.brand == "insurance":
            tags.extend(["#보험비교", "#실손보험", "#보험다이어트", "#보험리모델링", "#운전자보험", "#암보험", "#재테크꿀팁", "#Shorts", "#TikTok", "#Reels"])
        else:
            tags.extend(["#주식AI", "#스톡마스터", "#주식투자", "#퀀트투자", "#국내주식", "#삼성전자", "#SK하이닉스", "#재테크", "#Shorts", "#TikTok", "#Reels"])

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

    def _call_gemini_smart(self, prompt: str) -> Optional[str]:
        """GeminiSmartClient 9개 키 체인 연동 호출"""
        if not self.client:
            return None
        models = ["gemini-2.5-flash", "gemini-2.0-flash"]
        for m in models:
            try:
                resp = self.client.generate_content(
                    model=m,
                    contents=prompt
                )
                if resp and resp.text and len(resp.text.strip()) > 50:
                    logger.info(f"✨ [Gemini Copywriter] {m} 카피라이팅 생성 성공!")
                    return resp.text.strip()
            except Exception as e:
                logger.warning(f"모델 {m} 호출 실패: {e}")
                continue
        return None

    def generate_full_package(
        self,
        topic_id: int = 1,
        topic_title: Optional[str] = None,
        media_type: str = "shorts"
    ) -> Dict[str, Any]:
        """
        🚀 4대 SNS 채널(유튜브, 틱톡, 네이버 클립, 메타 릴스) 전용 초고관여 바이럴 패키징
        """
        hook_title = topic_title or self.spec["hook_titles"].get(topic_id, f"{self.spec['name']} 핵심 리포트 #{topic_id}")
        hashtags = self.build_hybrid_hashtags(topic_id=topic_id, count=15)
        short_tags = " ".join(hashtags[:8])
        full_tags = " ".join(hashtags)

        prompt = f"""
당신은 대한민국 1위 바이럴 SNS 마케팅 총괄 디렉터입니다.
아래 브랜드와 주제 정보를 바탕으로 독자의 호기심과 감정적 공감을 극대화하여 폭발적인 조회수, 댓글, 공유를 유도하는 [4대 SNS 플랫폼별 초고밀도 스토리텔링 카피 패키지]를 작성하세요.

[브랜드 정보]
- 브랜드명: {self.spec['name']}
- 네이버 공식 검색어: [{self.spec['official_keyword']}]
- 핵심 가치: {self.spec['core_value']}
- 타깃층: {self.spec['target']}
- 검색 유도 문구: {self.spec['search_phrase']}

[콘텐츠 정보]
- 미디어 유형: 숏폼 영상 (Shorts)
- 주제 #{topic_id}: {hook_title}

[플랫폼별 작성 지침 - 절대 부실하게 작성하지 말고 풍부하고 전문적으로 작성할 것]
1. viral_title: 시선을 단 1초 만에 사로잡는 강력한 훅 제목 (이모지 포함, 35자 내외)
2. youtube_desc: 유튜브 쇼츠 상세 설명문 (줄바꿈 포함 풍부하게)
   - [상황 공감 인트로 2~3줄]
   - [💡 실전 핵심 팩트체크 3대 포인트] (번호 매겨서 상세 서술)
   - [검색 유도 및 공식 안내]
3. youtube_pinned: 시청자 참여를 유도하는 고정 댓글 (질문 던지기 + 네이버 검색어 안내)
4. tiktok_caption: 틱톡 알고리즘 최적화 본문 (강렬한 훅 2줄 + 핵심 요약 2줄 + 검색어)
5. naver_clip_desc: 네이버 클립 규격 최적화 (250~300자 분량의 고밀도 실전 정보 요약)
6. instagram_caption: 인스타그램 릴스/피드용 감각적인 스토리텔링 본문 (공감 서사 + 체크리스트 + 프로필 링크 유도)
7. facebook_caption: 페이스북용 깊이 있는 정보성 칼럼 본문 (공감 스토리 + 실전 가이드 + 첫 댓글 안내)

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
        gemini_text = self._call_gemini_smart(prompt)
        parsed = {}
        if gemini_text:
            try:
                json_match = re.search(r'\{.*\}', gemini_text, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
            except Exception:
                pass

        v_title = self._clean_text(parsed.get("viral_title")) or hook_title

        # 1. YouTube
        yt_d = self._clean_text(parsed.get("youtube_desc"))
        if not yt_d:
            yt_d = (
                f"📌 {v_title}\n\n"
                f"매일 쏟아지는 정보 속에서 진짜 실전 핵심만 완벽하게 짚어드립니다!\n\n"
                f"💡 실전 핵심 팩트체크:\n"
                f"1. {self.spec['core_value']}\n"
                f"2. 불필요한 비용 낭비 및 시행착오 없이 팩트 데이터로 즉시 확인\n"
                f"3. 2030 스마트 소비자를 위한 100% 무료 분석 혜택\n\n"
                f"👉 {self.spec['search_phrase']}"
            )
        yt_desc_full = f"{yt_d}\n\n🔍 {self.spec['search_phrase']}\n🌐 공식 웹: {self.spec['url']}\n\n{short_tags}"

        yt_p = self._clean_text(parsed.get("youtube_pinned"))
        if not yt_p:
            yt_p = (
                f"📌 여러분의 생각은 어떠신가요? 댓글로 자유롭게 의견을 남겨주세요!\n\n"
                f"실시간 데이터 기반 팩트 확인은 네이버에 👉 [ {self.spec['official_keyword']} ] 검색하시면 바로 연결됩니다! 📲"
            )

        # 2. TikTok
        tk_c = self._clean_text(parsed.get("tiktok_caption"))
        if not tk_c:
            tk_c = (
                f"{v_title}\n\n"
                f"매일 고민되던 문제, 데이터로 1초 만에 해결하는 법! 💡\n"
                f"👉 {self.spec['search_phrase']}\n"
                f"실시간 분석 & 무료 혜택 📲"
            )
        tk_caption_full = f"{tk_c}\n\n{short_tags}"

        # 3. Naver Clip
        nv_d = self._clean_text(parsed.get("naver_clip_desc"))
        if not nv_d:
            nv_d = (
                f"{v_title}\n\n"
                f"{self.spec['name']}에서 알려드리는 실전 핵심 브리핑!\n"
                f"복잡한 과정 없이 팩트 데이터로 한 번에 확인하세요.\n\n"
                f"🔍 네이버 검색: [{self.spec['official_keyword']}]"
            )
        nv_desc_full = f"{nv_d}\n\n{short_tags}"

        # 4. Meta Reels & Instagram
        ig_c = self._clean_text(parsed.get("instagram_caption"))
        if not ig_c:
            ig_c = (
                f"✨ {v_title}\n\n"
                f"\"왜 나만 몰랐을까?\" 싶은 실전 꿀팁 대방출! 🔥\n\n"
                f"✔️ {self.spec['core_value']}\n"
                f"✔️ 팩트 기반 실시간 스마트 분석\n"
                f"✔️ 간편하게 누리는 100% 무료 혜택\n\n"
                f"🔗 자세한 내용은 프로필 상단 링크 또는\n"
                f"👉 {self.spec['search_phrase']}"
            )
        ig_caption_full = f"{ig_c}\n\n{full_tags}"

        # 5. Facebook
        fb_c = self._clean_text(parsed.get("facebook_caption"))
        if not fb_c:
            fb_c = (
                f"📢 {v_title}\n\n"
                f"{self.spec['name']} 실전 리포트입니다.\n"
                f"{self.spec['core_value']}\n\n"
                f"💡 지금 바로 네이버 검색창에 [{self.spec['official_keyword']}]을 검색하여 상세 내용을 확인해보세요!"
            )
        fb_caption_full = f"{fb_c}\n\n👇 [첫 번째 댓글]의 공식 링크를 확인하세요!\n\n{short_tags}"

        return {
            "title": v_title,
            "youtube": {
                "title": f"{v_title} #{self.spec['official_keyword']} #Shorts",
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
