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
    def get_instagram_hashtags(cls, topic_id: int = 1, count: int = 18) -> List[str]:
        """인스타그램 알고리즘 탐색탭 노출용 18~20개 정밀 4단 해시태그 리스트 반환"""
        norm_id = ((topic_id - 1) % 8) + 1
        tags: List[str] = []

        # 1. 브랜드 공식 태그 (Tier 4)
        tags.extend(cls.BRAND_TAGS)

        # 2. 주제별 롱테일 태그 6~8개 (Tier 3)
        topic_tags = cls.TOPIC_LONGTAIL_TAGS.get(norm_id, cls.TOPIC_LONGTAIL_TAGS[1])
        tags.extend(topic_tags[:7])

        # 3. 미들 트렌드 태그 4~5개 (Tier 2)
        tags.extend(cls.MID_TREND_TAGS["savings"][:3])
        tags.extend(cls.MID_TREND_TAGS["main_insurance"][:2])

        # 4. 대형 메가 태그 3~4개 (Tier 1)
        tags.extend(cls.MEGA_TAGS[:4])

        seen = set()
        unique_tags = []
        for t in tags:
            if t not in seen:
                seen.add(t)
                unique_tags.append(t)
            if len(unique_tags) >= count:
                break

        return unique_tags

    @classmethod
    def get_threads_hashtags(cls, topic_id: int = 1, count: int = 4) -> List[str]:
        """스레드(Threads) 텍스트 바이럴용 핵심 3~4개 해시태그 반환"""
        norm_id = ((topic_id - 1) % 8) + 1
        topic_tags = cls.TOPIC_LONGTAIL_TAGS.get(norm_id, cls.TOPIC_LONGTAIL_TAGS[1])
        tags = ["#보험리밸런스"] + topic_tags[:2] + ["#재테크고민"]
        return tags[:count]

    @classmethod
    def get_facebook_hashtags(cls, topic_id: int = 1, count: int = 6) -> List[str]:
        """페이스북(Facebook) 피드용 5~6개 해시태그 반환"""
        norm_id = ((topic_id - 1) % 8) + 1
        topic_tags = cls.TOPIC_LONGTAIL_TAGS.get(norm_id, cls.TOPIC_LONGTAIL_TAGS[1])
        tags = ["#보험리밸런스", "#InsureBalance", "#보험료줄이기"] + topic_tags[:3]
        return tags[:count]

    @classmethod
    def get_shorts_hashtags(cls, topic_id: int = 1) -> str:
        """유튜브 쇼츠 / 틱톡 / 릴스용 통합 해시태그 문자열 반환"""
        norm_id = ((topic_id - 1) % 8) + 1
        topic_tags = cls.TOPIC_LONGTAIL_TAGS.get(norm_id, cls.TOPIC_LONGTAIL_TAGS[1])
        tag_list = ["#보험리밸런스"] + topic_tags[:4] + ["#재테크꿀팁", "#Shorts", "#Reels", "#TikTok"]
        return " ".join(tag_list)

    @classmethod
    def get_youtube_shorts_hashtags(cls, topic_id: int = 1, count: int = 7) -> List[str]:
        """유튜브 쇼츠 전용 해시태그 리스트 반환 (호환 래퍼)"""
        norm_id = ((topic_id - 1) % 8) + 1
        topic_tags = cls.TOPIC_LONGTAIL_TAGS.get(norm_id, cls.TOPIC_LONGTAIL_TAGS[1])
        tags = ["#보험리밸런스"] + topic_tags[:4] + ["#Shorts", "#Reels"]
        return tags[:count]

    @classmethod
    def get_naver_tags(cls, topic_id: int = 1) -> str:
        """네이버 블로그 / 포스트 / 카페용 검색 태그 문자열 반환"""
        norm_id = ((topic_id - 1) % 8) + 1
        topic_tags = cls.TOPIC_LONGTAIL_TAGS.get(norm_id, cls.TOPIC_LONGTAIL_TAGS[1])
        tag_list = ["#보험리밸런스"] + topic_tags[:5] + ["#보험비교사이트", "#보험료다이어트", "#직장인재테크"]
        return " ".join(tag_list)


if __name__ == "__main__":
    matrix = InsuranceHashtagMatrix()
    print("=== 인스타그램 4단 해시태그 풀 (주제 #1) ===")
    print(" ".join(matrix.get_instagram_hashtags(1, 18)))
