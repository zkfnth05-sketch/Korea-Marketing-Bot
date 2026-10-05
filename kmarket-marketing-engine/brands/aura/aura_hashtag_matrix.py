# -*- coding: utf-8 -*-
"""
AuraHashtagMatrix - 🏷️ [Aura 데이팅 전용 4단 티어 실시간 바이럴 해시태그 엔진]
=============================================================================
• 역할:
  - 인스타그램(탐색탭), 릴스/쇼츠, 스레드, 페이스북 알고리즘 노출을 극대화하는 4단 티어 해시태그 풀 생성
  - Tier 1: 메가 키워드 (검색량 10만+ 대형 트래픽)
  - Tier 2: 미들 트렌드 키워드 (2030 핫플, 연애 심리, 상황 몰입)
  - Tier 3: 롱테일 타깃 키워드 (주제별 킬러 소구점, 전환율 극대화)
  - Tier 4: 브랜드 공식 검색어 (#아우라AI데이팅 붙여쓰기 불변 철칙)
• 8대 킬러 주제별 전용 롱테일 매트릭스 탑재
"""

import sys
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("AuraHashtagMatrix")


class AuraHashtagMatrix:
    """💖 Aura 데이팅 전용 4단 티어 해시태그 엔진"""

    OFFICIAL_KEYWORD = "아우라AI데이팅"
    BRAND_TAGS = ["#아우라AI데이팅", "#AURA", "#아우라데이팅", "#50대50성비"]

    # Tier 1: 2030 메가 키워드 (검색량 10만+ 상위 트래픽)
    MEGA_TAGS = [
        "#소개팅", "#연애", "#연애스타그램", "#직장인", "#직장인연애",
        "#20대", "#30대", "#솔로탈출", "#데이트", "#일상",
        "#카드뉴스", "#꿀팁", "#심리테스트", "#연애고민"
    ]

    # Tier 2: 미들 트렌드 키워드 (핫플, 라이프스타일, 상황)
    MID_TREND_TAGS = {
        "hotplaces": ["#성수동데이트", "#연남동소개팅", "#을지로와인바", "#강남역소개팅", "#한남동맛집", "#신용산핫플", "#주말데이트"],
        "lifestyle": ["#퇴근길", "#주말엔뭐하지", "#불금", "#데이트룩", "#소개팅룩", "#오오티디", "#직장인취미"],
        "psychology": ["#카톡심리", "#읽씹", "#MBTI연애", "#연애심리", "#썸", "#밀당", "#티키타카"]
    }

    # Tier 3: 8대 주제별 킬러 롱테일 키워드
    TOPIC_LONGTAIL_TAGS: Dict[int, List[str]] = {
        1: [  # 소개팅 긴급 탈출 전화
            "#소개팅탈출", "#소개팅긴급탈출", "#소개팅매너", "#소개팅빌런",
            "#소개팅후기", "#소개팅2차", "#어색한자리탈출", "#소개팅거절법",
            "#소개팅실물", "#안심소개팅", "#매너탈출"
        ],
        2: [  # 실시간 AI 자막 통화
            "#글로벌썸", "#외국인친구", "#일본인친구", "#언어교환",
            "#AI자막통화", "#실시간번역", "#글로벌데이팅", "#국제연애",
            "#일본여행친구", "#외국어회화", "#언어장벽제로"
        ],
        3: [  # 50:50 남녀 황금 성비 라운지
            "#50대50황금성비", "#성비50대50", "#소개팅앱추천", "#데이팅앱추천",
            "#남초탈출", "#유령회원제로", "#실명인증데이팅", "#클린라운지",
            "#검증된만남", "#진성회원", "#직장인소개팅앱"
        ],
        4: [  # 청담동 화보 프로필 스튜디오
            "#소개팅프로필", "#AI프로필", "#청담동스튜디오", "#인생샷",
            "#프로필사진", "#소개팅사진", "#첫인상치트키", "#화보프로필",
            "#셀카보정", "#매칭률폭발", "#자연스러운보정"
        ],
        5: [  # 2030 가치관 밸런스 게임
            "#가치관매칭", "#소개팅더치페이", "#데이트비용", "#연락빈도",
            "#연애밸런스게임", "#소개팅가치관", "#연애가치관", "#결혼관",
            "#소비습관", "#낭비없는연애", "#성향맞춤소개팅"
        ],
        6: [  # AI 첫대화 비서 / 스마트 오프너
            "#소개팅첫마디", "#읽씹탈출", "#AI대화비서", "#센스있는첫인사",
            "#스몰토크", "#답장률98프로", "#카톡첫마디", "#대화치트키",
            "#어색함탈출", "#소개팅대화주제", "#티키타카"
        ],
        7: [  # AI 매력상 & 관상/궁합 진단
            "#AI매력상", "#얼굴상진단", "#여우상vs강아지상", "#연애궁합",
            "#AI관상", "#찰떡궁합", "#매력리포트", "#소개팅궁합",
            "#내얼굴분위기", "#외모진단", "#퍼스널컬러"
        ],
        8: [  # 500m 안심 레이더 & 안심 번개 퀘스트
            "#500m안심레이더", "#동네친구", "#성수동번개", "#퇴근길번개",
            "#안심데이팅", "#위치보안", "#24시간자동폭파", "#스토킹걱정제로",
            "#동네메이트", "#가벼운와인한잔", "#동네소개팅"
        ]
    }

    @classmethod
    def fetch_live_trend_keywords(cls) -> List[str]:
        """🌐 구글 실시간 급상승(Google Trends) + 🟢 네이버 실시간 검색 트렌드(Naver Trend) 듀얼 교차 수집"""
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

        # 2. 🟢 네이버 실시간 핫이슈 & 2030 데이트/트렌드 실시간 검색어 (Naver AC API)
        naver_seeds = ["오늘 핫이슈", "2030 트렌드", "성수동 핫플", "주말 데이트"]
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

        fallback = ["#실시간트렌드", "#2030트렌드", "#주말데이트", "#핫플레이스"]
        for fb in fallback:
            if fb not in trends and len(trends) < 4:
                trends.append(fb)
        return trends[:4]

    @classmethod
    def get_rich_viral_hashtags(cls, topic_id: int = 1, count: int = 18) -> List[str]:
        """무광고 오가닉 바이럴 극대화: 브랜드 공식 태그 + 구글/네이버 실시간 급상승(최우선) + 주제별 롱테일 + 핫플/메가 태그 결합"""
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

        # 4. ☕ 2030 핫플 / 심리 / 라이프스타일 미들 태그 (3개)
        tags.extend(cls.MID_TREND_TAGS["hotplaces"][:2])
        tags.extend(cls.MID_TREND_TAGS["psychology"][:1])

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
        tag_list = [f"#{cls.OFFICIAL_KEYWORD}"] + topic_tags[:5] + ["#소개팅어플", "#데이팅앱추천", "#2030직장인", "#실시간트렌드"]
        return " ".join(tag_list)


if __name__ == "__main__":
    matrix = AuraHashtagMatrix()
    print("=== 인스타그램 4단 해시태그 풀 (주제 #1, 18개) ===")
    print(" ".join(matrix.get_instagram_hashtags(1, 18)))
    print("\n=== 스레드 실시간 트렌드 해시태그 (주제 #1, 15개) ===")
    print(" ".join(matrix.get_threads_hashtags(1, 15)))
