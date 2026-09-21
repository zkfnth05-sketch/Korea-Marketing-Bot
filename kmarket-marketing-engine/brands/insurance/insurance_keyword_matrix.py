# -*- coding: utf-8 -*-
"""
🛡️ InsureBalance 실시간 바이럴 키워드 수집 & 트렌드 해시태그 매트릭스 (InsuranceKeywordMatrix)
========================================================================================
- 브랜드: InsureBalance (34개 보험사 실시간 비교 & 보험 리밸런싱)
- 역할:
  1. 🔍 [네이버] 실시간 자동완성 & 연관검색어 (스마트블록 1위 상위노출용) 자동 수집
  2. 🌐 [구글] 구글 트렌드 KR + 구글 Suggest 롱테일 질문형 키워드 자동 수집
  3. 🎯 보험 6대 핵심 카테고리(실손/운전자/3대질환/치아태아/연금저축/가계부리밸런싱) 정밀 매트릭스
  4. 🏷️ 실시간 검색 트렌드 기반 고노출 바이럴 해시태그 자동 결합 및 패키징
"""

import os
import sys
import json
import logging
import datetime
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger("InsuranceKeywordMatrix")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CACHE_FILE = DATA_DIR / "insurance_keywords_cache.json"


class InsuranceKeywordMatrix:
    """
    🛡️ InsureBalance 전용 실시간 네이버 + 구글 검색 트렌드 & 바이럴 해시태그 결합 엔진
    """
    BRAND = "insurance"
    NAME = "InsureBalance Smart Insurance"

    # 🎯 보험 6대 황금 카테고리 & 시드(Seed) 키워드
    CATEGORY_SEEDS = {
        "health_medical": {
            "name": "4세대 실손 & 3대 질환 진단비",
            "icon": "🏥",
            "description": "실손보험 전환, 도수치료 보상, 암·뇌·심장 3대 진단비 비교",
            "seeds": ["실손보험 전환", "4세대 실비", "암보험 비교", "뇌혈관질환 보험", "허혈성 심장질환", "수술비 특약"],
            "feature": "InsureBalance AI 실시간 보장 분석 & 34개 보험사 비교"
        },
        "auto_driver": {
            "name": "운전자 & 자동차 다이렉트",
            "icon": "🚗",
            "description": "운전자보험 필수특약, 스쿨존 벌금 3천만, 변호사 선임비용, 다이렉트 비교",
            "seeds": ["운전자보험 필수특약", "자동차보험 다이렉트 비교", "교통사고 형사합의금", "자차보험 자기부담금", "운전자보험 만원"],
            "feature": "InsureBalance 1분 운전자 필수특약 점검기"
        },
        "life_dental_pet": {
            "name": "치아 · 태아 · 펫보험",
            "icon": "🦷",
            "description": "임플란트 면책기간, 태아보험 22주 가입시기, 강아지 슬개골 탈구",
            "seeds": ["치아보험 임플란트", "태아보험 가입시기", "펫보험 강아지 슬개골", "일상생활배상책임 누수", "주택화재보험"],
            "feature": "InsureBalance 라이프케어 맞춤 견적기"
        },
        "savings_annuity": {
            "name": "연금저축 & 세액공제 절세",
            "icon": "💰",
            "description": "연말정산 66만원 환급, IRP 퇴직연금, 비과세 저축보험, 종신 vs 정기",
            "seeds": ["연금저축 연말정산 세액공제", "IRP 퇴직연금 절세", "종신보험 정기보험 차이", "10년 비과세 저축보험"],
            "feature": "InsureBalance 절세 시뮬레이터"
        },
        "claims_knowhow": {
            "name": "보험금 3초 청구 & 숨은 돈 찾기",
            "icon": "📄",
            "description": "내보험찾아줌 숨은 보험금, 실손 청구서류 3분컷, 부지급 민원",
            "seeds": ["내보험찾아줌 숨은보험금", "실손보험 청구서류", "보험금 부지급 민원", "독립 손해사정사", "보험금 청구 소멸시효"],
            "feature": "InsureBalance 3초 숨은 보험금 조회기"
        },
        "remodeling_savings": {
            "name": "가계부 보험 다이어트 & 리밸런싱",
            "icon": "✂️",
            "description": "중복 특약 삭제, 적립보험료 환급, 갱신형 ➔ 비갱신형 조정, 월 3만원 절약",
            "seeds": ["보험 리모델링", "보험 다이어트", "적립보험료 삭제 환급", "비갱신형 보험료 비교", "보험증권 분석"],
            "feature": "InsureBalance 3초 무료 보험 리밸런싱"
        }
    }

    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.matrix_cache = self._load_or_refresh_cache()

    # =========================================================================
    # 🔍 1. 네이버(Naver) 실시간 검색어 & 자동완성 수집기
    # =========================================================================
    def fetch_naver_keywords(self, query: str) -> List[str]:
        """네이버 실시간 검색 자동완성 API를 호출하여 최신 실시간 검색어를 수집합니다."""
        keywords = []
        try:
            encoded_q = urllib.parse.quote(query)
            url = f"https://ac.search.naver.com/nx/ac?q={encoded_q}&st=100&frm=nv&ans=2&r_format=json"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
            )
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                items = data.get("items", [[]])[0]
                for item in items:
                    if isinstance(item, list) and len(item) > 0:
                        word = item[0].strip()
                        if word and word not in keywords:
                            keywords.append(word)
        except Exception as e:
            logger.debug(f"네이버 자동완성 수집 오류 ({query}): {e}")

        return keywords[:8]

    # =========================================================================
    # 🌐 2. 구글(Google) Suggest & 트렌드 수집기
    # =========================================================================
    def fetch_google_suggest(self, query: str) -> List[str]:
        """구글 한국 검색 Suggest API를 호출하여 구글 SEO 1위용 롱테일 검색어를 수집합니다."""
        keywords = []
        try:
            encoded_q = urllib.parse.quote(query)
            url = f"https://suggestqueries.google.com/complete/search?client=chrome&hl=ko&gl=kr&q={encoded_q}"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                if len(data) > 1 and isinstance(data[1], list):
                    for word in data[1]:
                        word_str = str(word).strip()
                        if word_str and word_str != query and word_str not in keywords:
                            keywords.append(word_str)
        except Exception as e:
            logger.debug(f"구글 Suggest 수집 오류 ({query}): {e}")

        return keywords[:8]

    def fetch_google_kr_trends(self) -> List[str]:
        """대한민국 영토 내(Geo: KR) 실시간 급상승 검색어 피드 수집"""
        trends = []
        try:
            url = "https://trends.google.com/trending/rss?geo=KR"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                root = ET.fromstring(resp.read().decode("utf-8", errors="ignore"))
                for item in root.findall("./channel/item"):
                    title = item.find("title")
                    if title is not None and title.text:
                        word = title.text.strip().replace("#", "")
                        if word and len(word) < 15:
                            trends.append(word)
                    if len(trends) >= 6:
                        break
        except Exception as e:
            logger.debug(f"구글 트렌드 KR 수집 오류: {e}")

        if not trends:
            trends = ["보험다이어트", "실손보험전환", "가계부절약", "숨은보험금"]
        return trends

    # =========================================================================
    # 🗄️ 3. 캐시 로드 및 일괄 실시간 갱신 파이프라인
    # =========================================================================
    def _load_or_refresh_cache(self) -> Dict[str, Any]:
        """캐시가 유효하면 로드하고, 없거나 만료되면 즉시 수집"""
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("categories") and len(data["categories"]) >= 6:
                        return data
            except Exception as e:
                logger.warning(f"보험 키워드 캐시 읽기 실패: {e}")

        return self.refresh_all_categories()

    def refresh_all_categories(self) -> Dict[str, Any]:
        """
        네이버 + 구글 실시간 교차 수집을 실행하여 6대 카테고리 전체 키워드 매트릭스를 갱신합니다.
        """
        logger.info("🛡️ [InsureBalance] 네이버 & 구글 실시간 바이럴 키워드 전수 수집 시작...")
        kr_trends = self.fetch_google_kr_trends()
        categories_data = {}

        for cat_key, cat_meta in self.CATEGORY_SEEDS.items():
            naver_collected = []
            google_collected = []

            for seed in cat_meta["seeds"][:3]:  # 핵심 시드 3개씩 실시간 수집
                n_res = self.fetch_naver_keywords(seed)
                naver_collected.extend(n_res)

                g_res = self.fetch_google_suggest(seed)
                google_collected.extend(g_res)

            # 중복 제거 및 랭킹 정제
            unique_naver = list(dict.fromkeys(naver_collected))
            unique_google = list(dict.fromkeys(google_collected))

            # 황금 조합: 네이버 상위 6개 + 구글 상위 6개 + 기본 시드
            combined_ranked = list(dict.fromkeys(
                unique_naver[:6] + unique_google[:6] + cat_meta["seeds"]
            ))

            # 🏷️ 실시간 트렌드 해시태그 결합 (공백 제거 및 바이럴 태그화)
            viral_tags = [f"#{w.replace(' ', '')}" for w in combined_ranked[:6]]
            # 브랜드 및 절약 공통 태그 결합
            viral_tags.extend(["#보험리밸런스", "#보험비교", "#가계부절약"])
            viral_tags = list(dict.fromkeys(viral_tags))[:10]

            categories_data[cat_key] = {
                "name": cat_meta["name"],
                "icon": cat_meta["icon"],
                "description": cat_meta["description"],
                "feature": cat_meta["feature"],
                "naver_top_keywords": unique_naver[:8],
                "google_top_keywords": unique_google[:8],
                "ranked_keywords": combined_ranked[:12],
                "viral_hashtags": viral_tags
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
            logger.info("🛡️ [InsureBalance] 실시간 키워드 매트릭스 캐시 저장 완료!")
        except Exception as e:
            logger.warning(f"캐시 저장 실패: {e}")

        self.matrix_cache = matrix_result
        return matrix_result

    # =========================================================================
    # 🤖 4. 제미나이(Gemini) SEO 원고 프롬프트 패키징 브릿지
    # =========================================================================
    def build_seo_article_brief(self, seed_topic: str, category: str = "health_medical") -> Dict[str, Any]:
        """
        시드 주제 + 실시간 네이버 스마트블록 키워드 + 실시간 트렌드 해시태그를 완벽하게 결합한 브리프 생성
        """
        cat_info = self.matrix_cache.get("categories", {}).get(category, {})
        if not cat_info:
            cat_info = list(self.matrix_cache.get("categories", {}).values())[0] if self.matrix_cache.get("categories") else {}

        naver_keys = cat_info.get("naver_top_keywords", ["실손보험 비교", "4세대 실비"])[:4]
        google_keys = cat_info.get("google_top_keywords", ["실손보험 갱신", "보험료 다이어트"])[:4]
        hashtags = cat_info.get("viral_hashtags", ["#보험리밸런스", "#보험비교", "#실손보험", "#가계부절약"])[:10]
        feature = cat_info.get("feature", "InsureBalance AI 실시간 보장 분석")

        # 네이버 스마트블록용 제목 키워드
        title_keywords = [
            f"{naver_keys[0] if naver_keys else seed_topic} 핵심 정리",
            f"{naver_keys[0] if naver_keys else seed_topic} 손해 안 보는 법",
            f"{naver_keys[0] if naver_keys else seed_topic} 보장 비교"
        ]

        subheading_keywords = [
            f"1. {naver_keys[0] if naver_keys else seed_topic} 꼭 알아야 할 핵심 포인트",
            f"2. {google_keys[0] if google_keys else '실제 가입'} 주의사항과 체크리스트",
            f"3. 불필요한 고정비 다이어트와 리밸런싱 전략"
        ]

        return {
            "category": category,
            "seed_topic": seed_topic,
            "seo_title_keywords": title_keywords,
            "h2_h3_subheading_keywords": subheading_keywords,
            "viral_hashtags": hashtags,
            "scoped_seeds": naver_keys + google_keys[:2]
        }


if __name__ == "__main__":
    matrix = InsuranceKeywordMatrix()
    summary = matrix.refresh_all_categories()
    print("\n=== 실시간 키워드 & 트렌드 해시태그 수집 결과 ===")
    for cat_id, cat_data in summary["categories"].items():
        print(f"\n{cat_data['icon']} [{cat_data['name']}]")
        print(f"  - 네이버 실시간: {cat_data['naver_top_keywords'][:4]}")
        print(f"  - 구글 실시간:   {cat_data['google_top_keywords'][:4]}")
        print(f"  - 실시간 해시태그: {' '.join(cat_data['viral_hashtags'][:7])}")
