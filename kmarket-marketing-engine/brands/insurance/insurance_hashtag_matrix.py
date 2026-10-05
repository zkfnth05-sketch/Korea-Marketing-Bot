# -*- coding: utf-8 -*-
"""
InsuranceHashtagMatrix - 🏷️ [보험 리밸런스 전용 4단 티어 실시간 바이럴 해시태그 엔진]
=====================================================================================
• 역할:
  - 인스타그램(탐색탭), 릴스/쇼츠, 스레드, 페이스북 알고리즘 노출을 극대화하는 4단 티어 해시태그 풀 생성
  - Tier 1: 메가 키워드 (검색량 10만+ 재테크/절약/직장인 트래픽)
  - Tier 2: 미들 트렌드 키워드 (실손, 운전자, 암, 치아, 보험다이어트)
  - Tier 3: 롱테일 타깃 키워드 (주제별 킬러 소구점: 4세대실손손익, 1만원운전자, 유사암 등)
  - Tier 4: 브랜드 공식 검색어 (#보험리밸런스 띄어쓰기 불변 철칙)
• 공식 규격:
  - 공식 검색어: '보험 리밸런스' (띄어쓰기 필수!)
  - 공식 URL: https://insure-rebalance.vercel.app/
"""

import sys
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("InsuranceHashtagMatrix")


class InsuranceHashtagMatrix:
    """🛡️ 보험 리밸런스 전용 4단 티어 해시태그 엔진"""

    OFFICIAL_KEYWORD = "보험 리밸런스"
    BRAND_TAGS = ["#보험리밸런스", "#InsureBalance", "#34개보험사비교", "#보험자가진단"]

    # Tier 1: 금융/재테크 메가 키워드 (검색량 10만+ 상위 트래픽)
    MEGA_TAGS = [
        "#보험", "#재테크", "#직장인", "#월급관리", "#고정지출줄이기",
        "#가계부", "#절약", "#돈모으기", "#생활비줄이기", "#카드뉴스",
        "#꿀팁", "#금융정보", "#직장인재테크", "#2030재테크"
    ]

    # Tier 2: 미들 트렌드 키워드 (카테고리별 핵심 보험)
    MID_TREND_TAGS = {
        "savings": ["#보험다이어트", "#보험료줄이기", "#보험리모델링", "#숨은보험금", "#고정지출절약"],
        "main_insurance": ["#실비보험", "#운전자보험", "#암보험", "#건강보험", "#치아보험", "#종신보험"],
        "comparison": ["#다이렉트보험", "#보험비교", "#보험비교사이트", "#보험사순위", "#보험금청구"]
    }

    # Tier 3: 8대 주요 주제별 킬러 롱테일 키워드
    TOPIC_LONGTAIL_TAGS: Dict[int, List[str]] = {
        1: [  # 4세대 실손의료비 전환
            "#4세대실손", "#4세대실비", "#실손보험전환", "#실비보험비교",
            "#도수치료실비", "#비급여특약", "#실손의료비", "#실비보험료",
            "#착한실손", "#병원비절약", "#실손보험청구"
        ],
        2: [  # 운전자보험 1만원의 법칙
            "#운전자보험1만원", "#운전자보험필수특약", "#스쿨존벌금", "#교통사고처리지원금",
            "#변호사선임비용", "#운전자보험비교", "#자동차보험비교", "#다이렉트운전자보험",
            "#민식이법벌금", "#1만원운전자보험", "#교통사고합의금"
        ],
        3: [  # 암보험 일반암 vs 유사암
            "#암보험진단비", "#일반암유사암", "#갑상선암보험", "#소액암진단비",
            "#암보험비교추천", "#표적항암치료", "#암보험가입요령", "#비갱신형암보험",
            "#암치료비", "#3대질병보험", "#암진단비5천만원"
        ],
        4: [  # 뇌혈관 & 허혈성 심장질환
            "#뇌혈관질환보험", "#허혈성심장질환", "#뇌출혈뇌경색", "#심근경색보험",
            "#2대질환진단비", "#산정특례특약", "#혈관보험", "#부모님보험점검",
            "#3대진단비", "#질병수술비", "#순환기질환보험"
        ],
        5: [  # 치아보험 임플란트 꿀팁
            "#치아보험임플란트", "#치과보험비교", "#임플란트보장", "#크라운치료보험",
            "#치아보험면책기간", "#충치치료비용", "#스케일링보험", "#틀니보험",
            "#치아보험가입시기", "#치과비용절약", "#치아보험해지"
        ],
        6: [  # 2030 사회초년생 필수 3종 보험
            "#사회초년생보험", "#20대보험추천", "#첫월급보험", "#필수보험3가지",
            "#가성비보험", "#보험다이어트팁", "#월5만원보험", "#단독실비",
            "#청년보험", "#어린이보험성인", "#2030보험설계"
        ],
        7: [  # 태아 & 어린이보험 22주
            "#태아보험가입시기", "#어린이보험비교", "#태아보험22주", "#신생아특약",
            "#선천성이상수술비", "#저체중아출산", "#어린이실비", "#육아스타그램",
            "#임산부필수", "#태아보험견적", "#어린이종합보험"
        ],
        8: [  # 가계부 보험료 다이어트 (월 30만원 ➔ 10만원)
            "#보험료다이어트", "#보험과다지출", "#중복보험정리", "#보험리모델링후기",
            "#해지환급금", "#월급루팡보험", "#가계부점검", "#보험갈아타기",
            "#불필요한특약삭제", "#보험자가진단", "#34개사비교견적"
        ]
    }

    @classmethod
    def fetch_live_trend_keywords(cls) -> List[str]:
        """🌐 구글 실시간 급상승(Google Trends) + 🟢 네이버 실시간 절약/재테크 검색 트렌드(Naver Trend) 듀얼 교차 수집"""
        trends = []
        import urllib.request
        import urllib.parse
        import json
        import xml.etree.ElementTree as ET

        # 1. 🌐 구글 실시간 급상승 검색어 (Google Trends KR RSS)
        try:
            url_google = "https://trends.google.com/trending/rss?geo=KR"
            req_g = urllib.request.Request(url_google, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req_g, timeout=2.5) as resp:
                xml_text = resp.read().decode("utf-8", errors="ignore")
                root = ET.fromstring(xml_text)
                for item in root.findall("./channel/item"):
                    title = item.find("title")
                    if title is not None and title.text:
                        w = title.text.strip().replace(" ", "").replace("#", "")
                        if w and len(w) < 12 and f"#{w}" not in trends:
                            trends.append(f"#{w}")
                    if len(trends) >= 2:
                        break
        except Exception as eg:
            logger.debug(f"Google Trends 수집 건너뜀: {eg}")

        # 2. 🟢 네이버 실시간 핫이슈 & 가계부/절약/재테크 실시간 검색어 (Naver AC API)
        naver_seeds = ["오늘 핫이슈", "생활비 절약", "가계부 다이어트", "고정지출 줄이기"]
        for seed in naver_seeds:
            try:
                encoded_q = urllib.parse.quote(seed)
                url_nv = f"https://ac.search.naver.com/nx/ac?q={encoded_q}&st=100&frm=nv&ans=2&r_format=json"
                req_nv = urllib.request.Request(url_nv, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                with urllib.request.urlopen(req_nv, timeout=2.0) as resp:
                    data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                    items = data.get("items", [[]])[0]
                    for it in items:
                        if isinstance(it, list) and len(it) > 0:
                            w = it[0].strip().replace(" ", "").replace("#", "")
                            if w and len(w) < 12 and f"#{w}" not in trends:
                                trends.append(f"#{w}")
                        if len(trends) >= 4:
                            break
            except Exception:
                pass
            if len(trends) >= 4:
                break

        fallback = ["#실시간트렌드", "#고정지출절약", "#재테크꿀팁", "#생활비절약"]
        for fb in fallback:
            if fb not in trends and len(trends) < 4:
                trends.append(fb)
        return trends[:4]

    @classmethod
    def get_rich_viral_hashtags(cls, topic_id: int = 1, count: int = 18) -> List[str]:
        """무광고 오가닉 바이럴 극대화: 브랜드 공식 태그 + 구글/네이버 실시간 급상승(최우선) + 주제별 롱테일 + 가계부/메가 태그 결합"""
        norm_id = ((topic_id - 1) % 8) + 1
        tags: List[str] = []

        # 1. 🏷️ 브랜드 공식 핵심 태그 (2개)
        tags.extend(cls.BRAND_TAGS[:2])

        # 2. 🌐 구글 + 🟢 네이버 실시간 급상승 트렌드 키워드 (4개, 최우선 100% 보장!)
        live_trends = cls.fetch_live_trend_keywords()
        tags.extend(live_trends)

        # 3. 🎯 주제별 킬러 롱테일 소구점 태그 (5~6개)
        topic_tags = cls.TOPIC_LONGTAIL_TAGS.get(norm_id, cls.TOPIC_LONGTAIL_TAGS[1])
        tags.extend(topic_tags[:6])

        # 4. ☕ 가계부 / 절약 / 주부 살림 미들 태그 (3개)
        tags.extend(cls.MID_TREND_TAGS["savings"][:2])
        tags.extend(cls.MID_TREND_TAGS["main_insurance"][:1])

        # 5. 🚀 10만+ 대형 메가 키워드 (3개)
        tags.extend(cls.MEGA_TAGS[:3])

        # 중복 제거 및 최대 개수 슬라이싱
        seen = set()
        unique_tags = []
        for t in tags:
            clean_t = t.strip()
            if not clean_t.startswith("#"):
                clean_t = f"#{clean_t}"
            if clean_t not in seen:
                seen.add(clean_t)
                unique_tags.append(clean_t)
            if len(unique_tags) >= count:
                break

        return unique_tags

    @classmethod
    def get_instagram_hashtags(cls, topic_id: int = 1, count: int = 18) -> List[str]:
        """인스타그램 알고리즘 탐색탭 노출용 18~20개 정밀 4단 해시태그 리스트 반환"""
        return cls.get_rich_viral_hashtags(topic_id=topic_id, count=count)

    @classmethod
    def get_threads_hashtags(cls, topic_id: int = 1, count: int = 15) -> List[str]:
        """스레드(Threads) 알고리즘 노출 폭발 15~18개 실시간 트렌드 융합 해시태그 반환"""
        return cls.get_rich_viral_hashtags(topic_id=topic_id, count=count)

    @classmethod
    def get_facebook_hashtags(cls, topic_id: int = 1, count: int = 12) -> List[str]:
        """페이스북(Facebook) 피드용 10~12개 해시태그 반환"""
        return cls.get_rich_viral_hashtags(topic_id=topic_id, count=count)

    @classmethod
    def get_shorts_hashtags(cls, topic_id: int = 1, count: int = 15) -> str:
        """유튜브 쇼츠 / 틱톡 / 릴스용 15개 실시간 트렌드 통합 해시태그 문자열 반환"""
        tags = cls.get_rich_viral_hashtags(topic_id=topic_id, count=count)
        return " ".join(tags)

    @classmethod
    def get_youtube_shorts_hashtags(cls, topic_id: int = 1, count: int = 12) -> List[str]:
        """유튜브 쇼츠 전용 해시태그 리스트 반환"""
        return cls.get_rich_viral_hashtags(topic_id=topic_id, count=count)

    @classmethod
    def get_naver_tags(cls, topic_id: int = 1) -> str:
        """네이버 블로그 / 포스트 / 카페용 검색 태그 문자열 반환"""
        norm_id = ((topic_id - 1) % 8) + 1
        topic_tags = cls.TOPIC_LONGTAIL_TAGS.get(norm_id, cls.TOPIC_LONGTAIL_TAGS[1])
        tag_list = ["#보험리밸런스"] + topic_tags[:5] + ["#보험비교사이트", "#보험료다이어트", "#직장인재테크", "#실시간트렌드"]
        return " ".join(tag_list)


if __name__ == "__main__":
    matrix = InsuranceHashtagMatrix()
    print("=== 인스타그램 4단 해시태그 풀 (주제 #1, 18개) ===")
    print(" ".join(matrix.get_instagram_hashtags(1, 18)))
    print("\n=== 스레드 실시간 트렌드 해시태그 (주제 #1, 15개) ===")
    print(" ".join(matrix.get_threads_hashtags(1, 15)))
