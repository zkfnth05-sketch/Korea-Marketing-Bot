import json
import logging
import datetime
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger("StockKeywordMatrix")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CACHE_FILE = DATA_DIR / "stock_keywords_cache.json"


class StockKeywordMatrix:
    """StockMaster 주식 AI & 투자 전용 실시간 네이버+구글 키워드 매트릭스"""
    BRAND = "stock"
    NAME = "StockMaster AI"

    CATEGORY_METAS = {
        "korea_market": {
            "name": "국내 증시 & 코스피 우량주",
            "icon": "🇰🇷",
            "description": "삼성전자, SK하이닉스 HBM, 밸류업 프로그램, 2차전지 반등 수급",
            "seeds": ["삼성전자 주가", "SK하이닉스 주가", "코스피 전망", "밸류업 수혜주", "2차전지 관련주"]
        },
        "us_dividend_tech": {
            "name": "미국 배당주 & 빅테크",
            "icon": "🇺🇸",
            "description": "엔비디아 실적, SCHD 배당 ETF, 테슬라 로보택시, 미국주식 양도세 절세",
            "seeds": ["엔비디아 주가", "SCHD ETF", "미국주식 절세", "테슬라 주가", "미국 배당주 추천"]
        },
        "etf_index": {
            "name": "S&P500 & 나스닥 지수 ETF",
            "icon": "📈",
            "description": "S&P500 적립식 복리, QQQ 나스닥100, 미국 장기채 TLT 금리인하 수혜",
            "seeds": ["S&P500 ETF", "나스닥100 QQQ", "미국채권 ETF", "적립식 ETF", "TQQQ 레버리지"]
        },
        "macro_economy": {
            "name": "거시경제 & 금리·환율",
            "icon": "🌐",
            "description": "미국 연준 FOMC 금리인하, 원달러 환율 전망, 미국 CPI 소비자물가지수",
            "seeds": ["FOMC 금리인하", "환율 전망", "미국 CPI 발표", "공포탐욕지수", "국제유가 전망"]
        },
        "chart_financials": {
            "name": "재무제표 & 차트 매매기법",
            "icon": "📊",
            "description": "PER PBR 재무제표 보는법, 이동평균선 골든크로스, DART 전자공시",
            "seeds": ["주식 차트 보는법", "재무제표 보는법", "골든크로스 매매법", "DART 공시", "RSI 지표"]
        },
        "quant_risk": {
            "name": "AI 퀀트 & 뇌동매매 방지",
            "icon": "🛡️",
            "description": "손절매 스탑로스, 분할매수 원칙, AI 퀀트 알고리즘 전광판, 멘탈 관리",
            "seeds": ["주식 분할매수", "주식 손절매 기준", "주식 뇌동매매", "AI 퀀트 투자", "주식 매매일지"]
        }
    }

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

    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.matrix_cache = self._load_or_refresh_cache()

    def fetch_naver_keywords(self, query: str) -> List[str]:
        keywords = []
        try:
            encoded_q = urllib.parse.quote(query)
            url = f"https://ac.search.naver.com/nx/ac?q={encoded_q}&st=100&frm=nv&ans=2&r_format=json"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0 Safari/537.36"}
            )
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                items = data.get("items", [[]])[0]
                for item in items:
                    if isinstance(item, list) and len(item) > 0:
                        word = item[0].strip()
                        if word and word not in keywords:
                            keywords.append(word)
        except Exception:
            pass
        return keywords[:8]

    def fetch_google_suggest(self, query: str) -> List[str]:
        keywords = []
        try:
            encoded_q = urllib.parse.quote(query)
            url = f"https://suggestqueries.google.com/complete/search?client=chrome&hl=ko&gl=kr&q={encoded_q}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                if len(data) > 1 and isinstance(data[1], list):
                    for word in data[1]:
                        word_str = str(word).strip()
                        if word_str and word_str != query and word_str not in keywords:
                            keywords.append(word_str)
        except Exception:
            pass
        return keywords[:8]

    def _load_or_refresh_cache(self) -> Dict[str, Any]:
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("categories") and len(data["categories"]) >= 6:
                        return data
            except Exception:
                pass
        return self.refresh_all_categories()

    def refresh_all_categories(self) -> Dict[str, Any]:
        logger.info("📈 [StockMaster] 네이버 & 구글 실시간 주식 키워드 수집 시작...")
        from core.trend_scraper import ViralTrendScraper
        scraper = ViralTrendScraper()
        kr_trends = scraper.fetch_korea_live_trends()

        categories_data = {}
        for cat_key, cat_meta in self.CATEGORY_METAS.items():
            naver_collected = []
            google_collected = []
            for seed in cat_meta["seeds"][:3]:
                naver_collected.extend(self.fetch_naver_keywords(seed))
                google_collected.extend(self.fetch_google_suggest(seed))

            unique_naver = list(dict.fromkeys(naver_collected))
            unique_google = list(dict.fromkeys(google_collected))
            tags = self.VIRAL_TAG_POOL.get(cat_key, ["#주식투자", "#StockMaster"])
            combined_tags = [f"#{w.replace(' ', '')}" for w in (unique_naver[:3] + unique_google[:2])] + tags

            categories_data[cat_key] = {
                "name": cat_meta["name"],
                "icon": cat_meta["icon"],
                "description": cat_meta["description"],
                "naver_top_keywords": unique_naver[:8],
                "google_top_keywords": unique_google[:8],
                "viral_hashtags": list(dict.fromkeys(combined_tags))[:8]
            }

        matrix_result = {
            "brand": self.BRAND,
            "name": self.NAME,
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "google_kr_live_trends": kr_trends,
            "total_categories": len(categories_data),
            "categories": categories_data
        }

        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(matrix_result, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        self.matrix_cache = matrix_result
        return matrix_result

    def get_dashboard_summary(self) -> Dict[str, Any]:
        return self.matrix_cache

    def get_live_hashtags(self, category: str = "korea_market", base_tags: Optional[List[str]] = None, count: int = 10) -> List[str]:
        cat_info = self.matrix_cache.get("categories", {}).get(category, {})
        cat_viral = cat_info.get("viral_hashtags", [])[:4]
        kr_trends = self.matrix_cache.get("google_kr_live_trends", [])[:2]
        kr_trend_tags = [f"#{t.replace(' ', '')}" if not t.startswith('#') else t for t in kr_trends]

        combined = []
        if base_tags:
            combined.extend(base_tags)
        combined.extend(cat_viral)
        combined.extend(kr_trend_tags)
        combined.extend(["#스톡마스터AI", "#StockMaster", "#주식AI", "#shorts"])

        unique_tags = []
        for t in combined:
            tag = t.strip()
            if not tag.startswith("#"):
                tag = f"#{tag}"
            if tag not in unique_tags and len(tag) > 1:
                unique_tags.append(tag)
        return unique_tags[:count]

    def build_seo_article_brief(self, seed_topic: str, category: str) -> Dict[str, Any]:
        seeds = self.SCOPED_SEEDS.get(category, self.SCOPED_SEEDS["korea_market"])
        import random
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

        tags = self.get_live_hashtags(category=category)

        return {
            "category": category,
            "seed_topic": seed_topic,
            "seo_title_keywords": title_keywords,
            "h2_h3_subheading_keywords": subheading_keywords,
            "viral_hashtags": tags,
            "scoped_seeds": chosen_seeds
        }

    def build_live_trend_brief(self) -> Dict[str, Any]:
        try:
            from brands.stock.stock_live_trend_scanner import StockLiveTrendScanner
            scanner = StockLiveTrendScanner()
            live_stock = scanner.get_curated_live_stock_trend()
        except Exception:
            live_stock = {
                "name": "삼성전자",
                "code": "005930",
                "sector": "반도체/HBM",
                "price": "실시간 수급 집중",
                "change_rate": "+2.5%",
                "keywords": ["HBM3E", "외국인순매수", "목표주가", "20일선지지선"],
                "is_live_hit": False
            }

        name = live_stock["name"]
        sector = live_stock["sector"]
        keywords = live_stock.get("keywords", [])
        seeds = [f"{name} {kw}" for kw in keywords[:3]]

        title_keywords = [
            f"오늘 실검 1위 [{name}] 급등, 10분 계량 전광판의 진단은?",
            f"외국인·기관 연속 순매수 [{name}] {keywords[0] if keywords else '수급'} 긴급 분석",
            f"[{name}] 목표주가와 20일선 지지선 손익비 팩트체크"
        ]

        subheading_keywords = [
            f"1. 오늘 실시간 수급 핫이슈: {name} ({sector}) 자금 쏠림 배경",
            f"2. 펀더멘털과 20일 이동평균선 차트 지지/저항 데이터 정밀 진단",
            f"3. 뇌동매매 방지: StockMaster 10분 계량 전광판 & -5% 리스크 관리 대응"
        ]

        tags = [f"#{name}", f"#{name}주가", f"#{sector}", "#외국인순매수", "#StockMaster", "#스톡마스터AI", "#주식AI", "#10분계량전광판"]

        return {
            "is_live_trend": True,
            "live_stock": live_stock,
            "category": "korea_market",
            "seed_topic": f"오늘 실시간 검색어 1위 [{name}] ({sector}) 퀀트 수급 분석",
            "seo_title_keywords": title_keywords,
            "h2_h3_subheading_keywords": subheading_keywords,
            "viral_hashtags": tags,
            "scoped_seeds": seeds
        }


