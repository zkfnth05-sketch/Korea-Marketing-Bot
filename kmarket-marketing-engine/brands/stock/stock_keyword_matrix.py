# -*- coding: utf-8 -*-
"""
📈 StockMaster 전용 실시간 키워드 매트릭스 (StockKeywordMatrix)
===============================================================
- 역할:
  1. 주식/투자 6대 카테고리별 전문 시드어(Scoped Seed) 관리
  2. 노이즈 필터링 (불법 리딩방, 도박, 무관 키워드 배제)
  3. 네이버 스마트블록 1위형 제목 키워드, 소제목 키워드, 바이럴 해시태그 생성
"""

import random
from typing import Dict, List, Any


class StockKeywordMatrix:
    """StockMaster 주식 AI & 투자 전용 키워드 매트릭스"""

    SCOPED_SEEDS: Dict[str, List[str]] = {
        "korea_market": [
            "삼성전자 SK하이닉스 HBM", "정부 밸류업 저PBR 수혜주", "2차전지 양극재 반등",
            "K방산 한화에어로스페이스", "유한양행 레이저티닙 바이오", "조선주 슈퍼사이클 신조선가",
            "현대차 기아 하이브리드 실적", "공모주 청약 상장일 매도", "외국인 기관 순매수 수급"
        ],
        "us_dividend_tech": [
            "SCHD JEPI 배당 ETF 비교", "엔비디아 블랙웰 실적 전망", "미국주식 양도소득세 250만 절세",
            "마이크로소프트 애저 코파일럿", "애플 인텔리전스 온디바이스", "리얼티인컴 월배당 리츠",
            "테슬라 로보택시 FSD 자율주행", "일라이릴리 비만치료제 마운자로", "워런버핏 포트폴리오 현금보유"
        ],
        "etf_index": [
            "S&P 500 ETF VOO SPY 비교", "나스닥 100 QQQ QQM 차이", "월 50만원 S&P500 복리수익",
            "미국 장기채 TLT 금리인하", "TQQQ SOXL 레버리지 음의복리", "TIGER 미국S&P500 절세계좌",
            "한국판 SCHD 배당다우존스", "금 은 원자재 ETF 헤지", "비트코인 현물 ETF IBIT"
        ],
        "macro_economy": [
            "미국 연준 FOMC 기준금리 인하", "원달러 환율 전망 1350원", "미국 CPI 소비자물가지수",
            "장단기 금리차 역전 해소 침체", "엔 캐리 트레이드 청산 파장", "공포와 탐욕 지수 바닥매수",
            "VIX 변동성 공포지수", "달러 인덱스 DXY 강달러", "국제 유가 WTI 정유주 영향"
        ],
        "chart_financials": [
            "PER PBR ROE 재무제표 보는법", "이동평균선 골든크로스 매매법", "지지선 저항선 매물대 차트",
            "DART 전자공시 유상증자 전환사채", "대량 거래량 장대양봉 세력매집", "RSI 과매수 과매도 다이버전스",
            "볼린저밴드 스퀴즈 돌파매매", "공매도 숏스퀴즈 원리", "어닝서프라이즈 컨센서스 괴리율"
        ],
        "quant_risk": [
            "뇌동매매 FOMO 극복 멘탈", "기계적 손절매 스탑로스 설정", "3분할 매수 분할매도 공식",
            "AI 퀀트 알고리즘 팩터투자", "포트폴리오 MDD 최대낙폭 관리", "잡주 물타기 금지 불타기원칙",
            "켈리공식 최적투자비중", "주식 매매일지 작성 복기", "현금비중 30프로 유지 원칙"
        ]
    }

    VIRAL_TAG_POOL: Dict[str, List[str]] = {
        "korea_market": ["#국내주식", "#삼성전자주가", "#SK하이닉스", "#밸류업프로그램", "#2차전지", "#코스피전망", "#StockMaster"],
        "us_dividend_tech": ["#미국주식", "#엔비디아", "#SCHD", "#미국배당주", "#테슬라", "#서학개미", "#StockMaster"],
        "etf_index": ["#ETF추천", "#SP500", "#나스닥100", "#적립식투자", "#복리수익", "#채권ETF", "#StockMaster"],
        "macro_economy": ["#거시경제", "#FOMC금리인하", "#환율전망", "#CPI발표", "#공포탐욕지수", "#미국증시전망", "#StockMaster"],
        "chart_financials": ["#주식차트보는법", "#재무제표보는법", "#골든크로스", "#DART공시", "#거래량매매", "#RSI지표", "#StockMaster"],
        "quant_risk": ["#주식투자원칙", "#뇌동매매방지", "#손절매기준", "#분할매수", "#AI퀀트", "#주식멘탈관리", "#StockMaster"]
    }

    def build_seo_article_brief(self, seed_topic: str, category: str) -> Dict[str, Any]:
        """주제와 카테고리에 맞는 실시간 SEO 키워드 패키지 생성"""
        seeds = self.SCOPED_SEEDS.get(category, self.SCOPED_SEEDS["korea_market"])
        chosen_seeds = random.sample(seeds, min(3, len(seeds)))

        title_keywords = [
            f"{chosen_seeds[0]} 완벽 분석",
            f"{chosen_seeds[0]} 실전 매매 전략",
            f"{chosen_seeds[0]} 주가 전망"
        ]

        subheading_keywords = [
            f"1. {chosen_seeds[0]} 시장 배경과 펀더멘털 분석",
            f"2. {chosen_seeds[1] if len(chosen_seeds) > 1 else '실시간 수급'} 데이터와 차트 체크포인트",
            f"3. 리스크 요인과 스마트 포트폴리오 대응 전략"
        ]

        tags = self.VIRAL_TAG_POOL.get(category, ["#주식투자", "#주식AI", "#StockMaster"])

        return {
            "category": category,
            "seed_topic": seed_topic,
            "seo_title_keywords": title_keywords,
            "h2_h3_subheading_keywords": subheading_keywords,
            "viral_hashtags": tags,
            "scoped_seeds": chosen_seeds
        }
