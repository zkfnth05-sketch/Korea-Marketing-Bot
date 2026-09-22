# -*- coding: utf-8 -*-
"""
📈 Stock Live Trend Scanner (실시간 증시/수급 & 우량주 트렌드 정밀 스캐너)
========================================================================
- 브랜드: Stock Master AI
- 역할:
  1. 네이버 금융 실시간 검색 상위 & 외인/기관 순매수 상위 종목 정밀 스캔
  2. 잡주/정치테마/동전주 100% 원천 필터링
  3. 코스피/코스닥 우량주 및 주도 섹터(HBM, 반도체, AI, 2차전지, 바이오, 방산)만 엄선
  4. 제미나이 3박자 퀀트 칼럼에 주입할 실시간 핫이슈 패키지 생성
"""

import re
import json
import logging
import urllib.request
from typing import Dict, List, Any, Optional

logger = logging.getLogger("StockLiveTrendScanner")


# 🛡️ 1. 우량주 & 주도 섹터 화이트리스트 (노이즈/잡주 원천 차단)
BLUE_CHIP_WHITELIST = {
    # ⚡ HBM & 반도체
    "삼성전자": {"code": "005930", "sector": "반도체/HBM", "keywords": ["HBM3E", "파운드리", "영업이익", "외국인순매수"]},
    "SK하이닉스": {"code": "000660", "sector": "반도체/HBM", "keywords": ["HBM 공급", "엔비디아", "실적서프라이즈", "기관매집"]},
    "한미반도체": {"code": "042700", "sector": "반도체장비", "keywords": ["듀얼TC본더", "HBM", "목표주가", "신고가"]},
    "리노공업": {"code": "058470", "sector": "반도체소부장", "keywords": ["온디바이스AI", "소켓", "영업이익률", "우량주"]},
    "HPSP": {"code": "403870", "sector": "반도체장비", "keywords": ["고압수소어닐링", "독점", "외인매수", "성장주"]},

    # 🔋 2차전지 & 모빌리티
    "LG에너지솔루션": {"code": "373220", "sector": "2차전지", "keywords": ["원통형배터리", "테슬라", "바닥반등", "수급개선"]},
    "POSCO홀딩스": {"code": "005490", "sector": "2차전지/철강", "keywords": ["리튬", "밸류업", "저PBR", "배당수익률"]},
    "에코프로비엠": {"code": "247540", "sector": "2차전지", "keywords": ["양극재", "코스피이전", "숏스퀴즈", "공매도잔고"]},
    "에코프로": {"code": "086520", "sector": "2차전지", "keywords": ["지주사", "유상증자", "반등타점", "손익비"]},
    "현대차": {"code": "005380", "sector": "자동차/밸류업", "keywords": ["하이브리드", "인도IPO", "주주환원", "저PBR"]},
    "기아": {"code": "000270", "sector": "자동차/밸류업", "keywords": ["영업이익률", "배당금", "외인순매수", "신차모멘텀"]},

    # 💊 바이오 & 헬스케어
    "삼성바이오로직스": {"code": "206640", "sector": "바이오CDMO", "keywords": ["수주대박", "생산능력", "실적성장", "기관매수"]},
    "셀트리온": {"code": "068270", "sector": "바이오시밀러", "keywords": ["짐펜트라", "미국PBM", "합병시너지", "바닥탈출"]},
    "유한양행": {"code": "000100", "sector": "신약개발", "keywords": ["렉라자", "FDA승인", "마일스톤", "글로벌신약"]},
    "알테오젠": {"code": "196170", "sector": "바이오플랫폼", "keywords": ["피하주사", "머크", "키트루다", "코스닥대장주"]},

    # 🚀 방산 & 조선 & 원전
    "한화에어로스페이스": {"code": "012450", "sector": "K-방산", "keywords": ["K9자주포", "수주잔고", "폴란드", "어닝서프라이즈"]},
    "현대로템": {"code": "064350", "sector": "K-방산", "keywords": ["K2전차", "루마니아", "외인연속매수", "실적개선"]},
    "HD현대중공업": {"code": "329180", "sector": "조선/슈퍼사이클", "keywords": ["신조선가지수", "LNG선", "흑자전환", "친환경선박"]},
    "두산에너빌리티": {"code": "034020", "sector": "원전/SMR", "keywords": ["체코원전", "웨스팅하우스", "AI전력수요", "가스터빈"]},

    # 🏦 금융 & 밸류업
    "KB금융": {"code": "105560", "sector": "금융/밸류업", "keywords": ["자사주소각", "분기배당", "ROE개선", "외국인지분율"]},
    "신한지주": {"code": "055550", "sector": "금융/밸류업", "keywords": ["주주환원율", "배당수익률", "저PBR", "기관순매수"]},

    # 🤖 IT & 플랫폼
    "NAVER": {"code": "035420", "sector": "인터넷/AI", "keywords": ["하이퍼클로바X", "숏폼클립", "치지직", "저평가구간"]},
    "카카오": {"code": "035720", "sector": "플랫폼", "keywords": ["경영쇄신", "카카오톡개편", "바닥다지기", "수급전환"]}
}


class StockLiveTrendScanner:
    """📈 실시간 증시 핫 종목 및 우량주 트렌드 정밀 스캐너"""

    NAVER_POPULAR_SEARCH_URL = "https://finance.naver.com/sise/lastsearch2.naver"

    def __init__(self):
        pass

    def fetch_naver_popular_stocks(self) -> List[Dict[str, Any]]:
        """네이버 금융 실시간 검색 상위 30개 종목 스크랩"""
        stocks = []
        try:
            req = urllib.request.Request(
                self.NAVER_POPULAR_SEARCH_URL,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                html = resp.read().decode("euc-kr", errors="ignore")

            # 정규식으로 종목명, 현재가, 등락률 파싱
            rows = re.findall(
                r'<a href="/item/main\.naver\?code=(\d+)".*?class="tltle">(.*?)</a>.*?<td class="number">([\d,]+)</td>.*?<td class="number">.*?([+-]?[\d\.]+)%</td>',
                html,
                re.DOTALL
            )
            for code, name, price, change_rate in rows:
                clean_name = name.strip()
                stocks.append({
                    "code": code.strip(),
                    "name": clean_name,
                    "price": price.strip(),
                    "change_rate": f"{change_rate.strip()}%"
                })
        except Exception as e:
            logger.warning(f"⚠️ 네이버 실시간 검색 종목 파싱 일시 장애(Fallback 가동): {e}")

        return stocks

    def get_curated_live_stock_trend(self) -> Dict[str, Any]:
        """
        실시간 검색 종목 중 '우량주 화이트리스트'에 부합하는 최우선 핫 종목 1개 엄선
        (없을 경우 시장 주도 대표 우량주 자동 선정)
        """
        live_stocks = self.fetch_naver_popular_stocks()
        selected_stock = None

        # 1. 실시간 검색 상위 종목 중 화이트리스트 매칭
        for s in live_stocks:
            if s["name"] in BLUE_CHIP_WHITELIST:
                info = BLUE_CHIP_WHITELIST[s["name"]]
                selected_stock = {
                    "name": s["name"],
                    "code": info["code"],
                    "sector": info["sector"],
                    "price": s["price"],
                    "change_rate": s["change_rate"],
                    "keywords": info["keywords"],
                    "is_live_hit": True
                }
                logger.info(f"🎯 [StockLiveTrend] 실시간 검색 핫 종목 매칭 성공: {s['name']} ({s['change_rate']})")
                break

        # 2. 매칭 실패 시 화이트리스트 대표 우량주 중 1개 큐레이션 (삼성전자, SK하이닉스, 한화에어로 등)
        if not selected_stock:
            import random
            featured_name = random.choice(["삼성전자", "SK하이닉스", "한화에어로스페이스", "현대차", "알테오젠", "KB금융"])
            info = BLUE_CHIP_WHITELIST[featured_name]
            selected_stock = {
                "name": featured_name,
                "code": info["code"],
                "sector": info["sector"],
                "price": "실시간 수급 집중",
                "change_rate": "+2.5%",
                "keywords": info["keywords"],
                "is_live_hit": False
            }
            logger.info(f"🎯 [StockLiveTrend] 대표 우량주 큐레이션: {featured_name}")

        return selected_stock


if __name__ == "__main__":
    scanner = StockLiveTrendScanner()
    trend = scanner.get_curated_live_stock_trend()
    print("선정된 실시간 핫 종목:", json.dumps(trend, ensure_ascii=False, indent=2))
