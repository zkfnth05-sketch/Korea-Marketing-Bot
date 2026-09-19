"""
💖 Aura 2030 실시간 바이럴 키워드 수집 & SEO 매트릭스 독립 레고 블록 (AuraKeywordMatrix)
================================================================================
- 브랜드: Aura (2030 AI 데이팅 / 소개팅 코칭 / 매력 리포트 / 데이트 코스)
- 역할:
  1. 🔍 [네이버] 실시간 자동완성 & 연관검색어 (스마트블록 1위 상위노출용) 자동 수집
  2. 🌐 [구글] 구글 트렌드 KR + 구글 Suggest 롱테일 질문형 키워드 자동 수집
  3. 🎯 2030 6대 핵심 카테고리(카톡심리/핫플코스/대화스킬/MBTI심리/룩북/애프터) 정밀 매트릭스
  4. 🤖 제미나이(Gemini) SEO 원고/숏폼/텔레그램 주입용 고노출 프롬프트 패키징
"""

import os
import sys

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json
import logging
import datetime
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger("AuraKeywordMatrix")

# 기본 경로 및 캐시 파일
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CACHE_FILE = DATA_DIR / "aura_keywords_cache.json"


class AuraKeywordMatrix:
    """
    💖 2030 싱글 타깃 Aura 전용 실시간 네이버 + 구글 키워드 하이브리드 엔진
    """
    BRAND = "aura"
    NAME = "Aura 2030 AI Dating"

    # 🎯 2030 6대 황금 카테고리 & 시드(Seed) 키워드
    CATEGORY_SEEDS = {
        "kakaotalk_signals": {
            "name": "카톡 밀당 & 시그널 해석",
            "icon": "💬",
            "description": "2030 소개팅 전후 카톡 심리, 답장 텀, 읽씹/안읽씹, 선톡 분석",
            "seeds": ["소개팅 카톡", "소개팅 읽씹", "소개팅 카톡 텀", "소개팅 안읽씹", "소개팅 선톡", "소개팅 답장"],
            "aura_feature": "Aura AI 카톡 답장 코칭 & 티키타카 분석기"
        },
        "date_spots": {
            "name": "실전 소개팅 핫플 & 데이트 코스",
            "icon": "🍷",
            "description": "네이버 스마트블록 장악용 연남/성수/한남/강남 소개팅 핫플 및 와인바",
            "seeds": ["연남동 소개팅", "성수동 소개팅", "소개팅 와인바", "소개팅 룸식당", "소개팅 2차", "서울 실내데이트"],
            "aura_feature": "Aura 성향 맞춤 AI 주말 데이트 코스 큐레이션"
        },
        "conversation_skills": {
            "name": "대화 꿀팁 & 어색함 탈출",
            "icon": "🧠",
            "description": "첫 만남 침묵 방지, 스몰토크, 밸런스게임, 더치페이 매너",
            "seeds": ["소개팅 대화주제", "소개팅 스몰토크", "소개팅 밸런스게임", "소개팅 더치페이", "소개팅 칭찬", "소개팅 첫인사"],
            "aura_feature": "Aura AI 실시간 밸런스 게임 & 대화 치트키"
        },
        "psychology_mbti": {
            "name": "연애 심리 & 자가진단 & MBTI",
            "icon": "🔮",
            "description": "바이럴 공유 1위 연애 MBTI 궁합, 매력도 점수, 호감 시그널",
            "seeds": ["연애 MBTI", "소개팅 호감 시그널", "연애 매력도 테스트", "회피형 연애", "남자가 반했을 때", "여자가 호감"],
            "aura_feature": "Aura AI 얼굴/성격 매력도 진단 리포트"
        },
        "lookbook_style": {
            "name": "소개팅 룩북 & 스타일링",
            "icon": "👗",
            "description": "소개팅 전날 무조건 검색하는 꾸안꾸 남친룩/여친룩, 향수, 메이크업",
            "seeds": ["소개팅 남자 룩", "소개팅 여자 코디", "소개팅 향수", "꾸안꾸 남친룩", "소개팅 첫인상"],
            "aura_feature": "Aura AI 프로필 비주얼 스타일 가이드"
        },
        "after_dating": {
            "name": "애프터 & 삼프터 고백 타이밍",
            "icon": "💘",
            "description": "실제 만남 성사 및 연애 발전 단계의 고백/애프터 신청법",
            "seeds": ["소개팅 애프터", "소개팅 삼프터 고백", "소개팅 귀가 카톡", "애프터 거절 시그널", "소개팅 다음날"],
            "aura_feature": "Aura AI 애프터 성공률 예측 모델"
        }
    }

    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.matrix_cache = self._load_or_refresh_cache()

    # =========================================================================
    # 🔍 1. 네이버(Naver) 실시간 검색어 & 자동완성 수집기
    # =========================================================================
    def fetch_naver_keywords(self, query: str) -> List[str]:
        """
        네이버 실시간 검색 자동완성 API를 호출하여 2030 실시간 확장 검색어를 수집합니다.
        """
        keywords = []
        try:
            encoded_q = urllib.parse.quote(query)
            url = f"https://ac.search.naver.com/nx/ac?q={encoded_q}&st=100&frm=nv&ans=2&r_format=json"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
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
            logger.debug(f"네이버 자동완성 수집 일시 오류 ({query}): {e}")

        return keywords[:8]

    # =========================================================================
    # 🌐 2. 구글(Google) Suggest & 트렌드 수집기
    # =========================================================================
    def fetch_google_suggest(self, query: str) -> List[str]:
        """
        구글 한국 검색 Suggest API를 호출하여 구글 SEO 1위용 롱테일 질문 키워드를 수집합니다.
        """
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
            logger.debug(f"구글 Suggest 수집 일시 오류 ({query}): {e}")

        return keywords[:8]

    def fetch_google_kr_trends(self) -> List[str]:
        """
        대한민국 영토 내(Geo: KR) 실시간 급상승 검색어 피드 수집
        """
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
            logger.debug(f"구글 트렌드 KR 수집 일시 오류: {e}")

        if not trends:
            trends = ["2026연애트렌드", "소개팅후기", "주말핫플", "첫인상테스트"]
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
                logger.warning(f"Aura 키워드 캐시 읽기 실패: {e}")

        return self.refresh_all_categories()

    def refresh_all_categories(self) -> Dict[str, Any]:
        """
        네이버 + 구글 실시간 교차 수집을 실행하여 6대 카테고리 전체 키워드 매트릭스를 갱신합니다.
        """
        logger.info("💖 [Aura] 2030 네이버 & 구글 실시간 바이럴 키워드 전수 수집 시작...")
        kr_trends = self.fetch_google_kr_trends()
        categories_data = {}

        for cat_key, cat_meta in self.CATEGORY_SEEDS.items():
            naver_collected = []
            google_collected = []

            for seed in cat_meta["seeds"][:3]:  # 핵심 시드 3개씩 교차 수집
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

            categories_data[cat_key] = {
                "name": cat_meta["name"],
                "icon": cat_meta["icon"],
                "description": cat_meta["description"],
                "aura_feature": cat_meta["aura_feature"],
                "naver_top_keywords": unique_naver[:8],
                "google_top_keywords": unique_google[:8],
                "ranked_keywords": combined_ranked[:12],
                "viral_hashtags": [f"#{w.replace(' ', '')}" for w in combined_ranked[:8]]
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
            logger.info("💖 [Aura] 2030 실시간 키워드 매트릭스 캐시 저장 완료!")
        except Exception as e:
            logger.warning(f"캐시 저장 실패: {e}")

        self.matrix_cache = matrix_result
        return matrix_result

    # =========================================================================
    # 🤖 4. 제미나이(Gemini) SEO 원고 & 숏폼 프롬프트 패키징 브릿지
    # =========================================================================
    def get_realtime_keywords(self, category: Optional[str] = None, count: int = 10) -> List[str]:
        """특정 카테고리 또는 전체에서 최상위 실시간 키워드 n개 추출"""
        categories = self.matrix_cache.get("categories", {})
        if category and category in categories:
            return categories[category].get("ranked_keywords", [])[:count]
        
        # 전체 카테고리에서 균등 추출
        all_keywords = []
        for cat in categories.values():
            all_keywords.extend(cat.get("ranked_keywords", [])[:2])
        return list(dict.fromkeys(all_keywords))[:count]

    def build_seo_article_brief(self, seed_topic: str, category: str = "kakaotalk_signals") -> Dict[str, Any]:
        """
        시드 주제 + 네이버 스마트블록 키워드 + 구글 질문 키워드 + Aura 전환 CTA를
        완벽하게 융합한 SEO 작성 브리프를 생성합니다.
        """
        cat_info = self.matrix_cache.get("categories", {}).get(category, {})
        naver_keys = cat_info.get("naver_top_keywords", ["소개팅 대화", "카톡 답장"])[:4]
        google_keys = cat_info.get("google_top_keywords", ["소개팅 성공법", "첫만남 호감"])[:4]
        hashtags = cat_info.get("viral_hashtags", ["#Aura", "#소개팅", "#연애팁"])[:8]
        aura_feature = cat_info.get("aura_feature", "Aura AI 매력 리포트")

        return {
            "seed_topic": seed_topic,
            "category_name": cat_info.get("name", "2030 연애 트렌드"),
            "target_audience": "2030 미혼/싱글 남녀 (소개팅 및 썸 진행 중인 고관여 독자)",
            "seo_title_keywords": naver_keys[:2],
            "h2_h3_subheading_keywords": google_keys[:3],
            "viral_hashtags": hashtags,
            "aura_cta_bridge": f"💡 이 글을 읽은 독자가 '내 상황은 어떨까?' 궁금해할 때 자연스럽게 [{aura_feature}]를 체험하도록 연결할 것.",
            "prompt_instructions": (
                f"당신은 2030 트렌드에 가장 민감한 전문 에디터입니다.\n"
                f"주제: '{seed_topic}'\n"
                f"1. 제목에는 네이버 스마트블록 핵심어 ({', '.join(naver_keys[:2])})를 자연스럽게 포함하세요.\n"
                f"2. 소제목(H2, H3)에는 구글 롱테일 질문 키워드 ({', '.join(google_keys[:3])})를 배치하세요.\n"
                f"3. 결론부에는 [{aura_feature}]로 연결되는 공감형 CTA를 한 단락 작성하세요.\n"
                f"4. 글 끝에는 해시태그 ({' '.join(hashtags)})를 기재하세요."
            )
        }

    # =========================================================================
    # 📊 5. 웹 대시보드 연동용 JSON 요약기
    # =========================================================================
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """대시보드 '실시간 바이럴 키워드' 탭에 렌더링할 2030 전용 데이터 반환"""
        return self.matrix_cache


if __name__ == "__main__":
    matrix = AuraKeywordMatrix()
    summary = matrix.refresh_all_categories()
    print("\n==========================================")
    print("💖 [Aura] 2030 실시간 키워드 매트릭스 수집 결과")
    print("==========================================")
    for cat_id, cat_data in summary["categories"].items():
        print(f"\n{cat_data['icon']} [{cat_data['name']}]")
        print(f"  - 네이버 실시간: {cat_data['naver_top_keywords'][:4]}")
        print(f"  - 구글 실시간:   {cat_data['google_top_keywords'][:4]}")
        print(f"  - 바이럴 태그:   {' '.join(cat_data['viral_hashtags'][:5])}")
    
    brief = matrix.build_seo_article_brief("소개팅 카톡 답장 텀과 선톡의 의미", "kakaotalk_signals")
    print("\n📝 [제미나이 주입용 SEO 브리프 샘플]")
    print(json.dumps(brief, ensure_ascii=False, indent=2))
