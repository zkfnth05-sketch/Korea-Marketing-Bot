# -*- coding: utf-8 -*-
"""
StockHashtagMatrix - 🏷️ [StockMaster AI 전용 4단 티어 실시간 바이럴 해시태그 엔진]
==================================================================================
• 역할:
  - 인스타그램(탐색탭), 릴스/쇼츠, 스레드, 페이스북 알고리즘 노출을 극대화하는 4단 티어 해시태그 풀 생성
  - Tier 1: 메가 키워드 (검색량 10만+ 주식/재테크/미국주식 트래픽)
  - Tier 2: 미들 트렌드 키워드 (삼전, 하이닉스, 엔비디아, SCHD, S&P500 등 대형주/ETF)
  - Tier 3: 롱테일 타깃 키워드 (주제별 킬러 소구점: 퀀트적정주가, 외인수급, 월배당100만, 손절선 등)
  - Tier 4: 브랜드 공식 검색어 (#스톡마스터AI 띄어쓰기 불변 철칙)
• 공식 규격:
  - 공식 검색어: '스톡마스터 AI' (띄어쓰기 필수!)
  - 공식 URL: https://stockmaster-ai.vercel.app/
"""

import sys
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("StockHashtagMatrix")


class StockHashtagMatrix:
    """📈 StockMaster AI 전용 4단 티어 해시태그 엔진"""

    OFFICIAL_KEYWORD = "스톡마스터 AI"
    BRAND_TAGS = ["#스톡마스터AI", "#StockMasterAI", "#AI퀀트투자", "#주식자가진단"]

    # Tier 1: 금융/주식 메가 키워드 (검색량 10만+ 상위 트래픽)
    MEGA_TAGS = [
        "#주식", "#주식투자", "#재테크", "#미국주식", "#국내주식",
        "#직장인투자", "#주린이", "#경제공부", "#주식공부", "#카드뉴스",
        "#투자꿀팁", "#부자되기", "#돈모으기", "#파이어족"
    ]

    # Tier 2: 미들 트렌드 키워드 (빅테크, 대장주, ETF)
    MID_TREND_TAGS = {
        "korea_stocks": ["#삼성전자", "#SK하이닉스", "#HBM", "#반도체주식", "#코스피", "#밸류업"],
        "us_stocks": ["#엔비디아", "#테슬라", "#애플", "#마이크로소프트", "#빅테크", "#나스닥"],
        "etf_dividend": ["#SCHD", "#JEPQ", "#월배당", "#배당주", "#미국배당주", "#SP500", "#QQQ"]
    }

    # Tier 3: 8대 주요 주제별 킬러 롱테일 키워드
    TOPIC_LONGTAIL_TAGS: Dict[int, List[str]] = {
        1: [  # 삼성전자 vs SK하이닉스 HBM 수급 대결
            "#삼성전자주가", "#SK하이닉스주가", "#HBM관련주", "#외국인순매수",
            "#기관수급", "#반도체적정주가", "#반도체대장주", "#엔비디아공급망",
            "#코스피대장주", "#퀀트수급분석", "#반도체목표주가"
        ],
        2: [  # 미국 배당성장 ETF(SCHD·JEPQ) 월 100만원 배당
            "#SCHD배당금", "#JEPQ월배당", "#월100만원배당", "#배당포트폴리오",
            "#배당성장ETF", "#미국배당ETF", "#배당금시뮬레이션", "#월배당파이프라인",
            "#배당재투자", "#노후준비ETF", "#고배당주"
        ],
        3: [  # 엔비디아(NVDA) AI 밸류에이션
            "#엔비디아주가전망", "#NVDA적정주가", "#AI빅테크", "#M7주식",
            "#엔비디아실적", "#PER밸류에이션", "#월가목표주가", "#빅테크투자",
            "#AI반도체", "#엔비디아고점논란", "#나스닥우량주"
        ],
        4: [  # S&P500 vs 나스닥100 적립식 복리
            "#SP500적립식", "#나스닥100적립식", "#적립식복리효과", "#미국지수ETF",
            "#워런버핏추천", "#연금저축SP500", "#ISA계좌추천", "#장기투자성공법",
            "#VOO", "#IVV", "#QQQ장기투자"
        ],
        5: [  # 테슬라(TSLA) 로보택시 & FSD 퀀트
            "#테슬라주가전망", "#TSLA로보택시", "#FSD자율주행", "#일론머스크",
            "#전기차관련주", "#테슬라목표주가", "#로보택시수혜주", "#테슬라매수타이밍",
            "#성장주투자", "#미국성장주", "#테슬라실적"
        ],
        6: [  # 직장인 뇌동매매 방지 손절매 원칙
            "#주식손절매원칙", "#스탑로스설정", "#뇌동매매방지", "#주식분할매수",
            "#손실제한원칙", "#주식멘탈관리", "#투자원칙", "#주식매매일지",
            "#리스크관리", "#물타기금지", "#원칙매매"
        ],
        7: [  # 밸류업 프로그램 저PBR 고배당 금융주
            "#기업밸류업", "#저PBR주식", "#금융지주배당", "#은행주배당",
            "#주주환원율", "#배당수익률", "#자사주소각", "#코리아디스카운트",
            "#가치투자", "#우량배당주", "#밸류업수혜주"
        ],
        8: [  # AI 퀀트 적정주가 & 외국인 쌍끌이 레이더
            "#AI적정주가", "#외국인쌍끌이", "#퀀트알고리즘", "#종목자가진단",
            "#실시간수급레이더", "#골든크로스포착", "#재무제표분석", "#스마트개미",
            "#적정밸류에이션", "#주식치트키", "#퀀트투자전략"
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
        tags.extend(cls.MID_TREND_TAGS["us_stocks"][:2])
        tags.extend(cls.MID_TREND_TAGS["etf_dividend"][:3])

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
        tags = ["#스톡마스터AI"] + topic_tags[:2] + ["#주식고민"]
        return tags[:count]

    @classmethod
    def get_facebook_hashtags(cls, topic_id: int = 1, count: int = 6) -> List[str]:
        """페이스북(Facebook) 피드용 5~6개 해시태그 반환"""
        norm_id = ((topic_id - 1) % 8) + 1
        topic_tags = cls.TOPIC_LONGTAIL_TAGS.get(norm_id, cls.TOPIC_LONGTAIL_TAGS[1])
        tags = ["#스톡마스터AI", "#StockMasterAI", "#주식투자"] + topic_tags[:3]
        return tags[:count]

    @classmethod
    def get_shorts_hashtags(cls, topic_id: int = 1) -> str:
        """유튜브 쇼츠 / 틱톡 / 릴스용 통합 해시태그 문자열 반환"""
        norm_id = ((topic_id - 1) % 8) + 1
        topic_tags = cls.TOPIC_LONGTAIL_TAGS.get(norm_id, cls.TOPIC_LONGTAIL_TAGS[1])
        tag_list = ["#스톡마스터AI"] + topic_tags[:4] + ["#주식꿀팁", "#Shorts", "#Reels", "#TikTok"]
        return " ".join(tag_list)

    @classmethod
    def get_naver_tags(cls, topic_id: int = 1) -> str:
        """네이버 블로그 / 포스트 / 카페용 검색 태그 문자열 반환"""
        norm_id = ((topic_id - 1) % 8) + 1
        topic_tags = cls.TOPIC_LONGTAIL_TAGS.get(norm_id, cls.TOPIC_LONGTAIL_TAGS[1])
        tag_list = ["#스톡마스터AI"] + topic_tags[:5] + ["#주식비교", "#퀀트투자", "#미국주식추천"]
        return " ".join(tag_list)


if __name__ == "__main__":
    matrix = StockHashtagMatrix()
    print("=== 인스타그램 4단 해시태그 풀 (주제 #1) ===")
    print(" ".join(matrix.get_instagram_hashtags(1, 18)))
