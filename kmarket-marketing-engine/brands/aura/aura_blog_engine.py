"""
💖 Aura 2030 전용 블로그 SEO & 실시간 키워드 합성 엔진 (AuraBlogEngine)
=======================================================================
- 브랜드: Aura (2030 AI 데이팅 / 소개팅 코칭 / 매력 리포트 / 데이트 코스)
- 역할:
  1. 📚 100대 마스터 주제 풀에서 순환 또는 지정 추출
  2. 🛡️ [가드레일 1] 주제별 6대 카테고리 전용 시드어(Scoped Seed)로만 실시간 키워드 수집 (엉뚱한 키워드 원천 차단)
  3. 🛡️ [가드레일 2] 불용어 및 무관한 잡음 키워드 정밀 필터링
  4. 🛡️ [가드레일 3] 제미나이(Gemini) AI 3중 문맥 검증 프롬프트 주입
  5. 🌐 네이버 스마트블록 1위 제목 + 구글 SEO H2/H3 소제목 + Aura 앱 전환 CTA + 4대 플랫폼 태그 완성
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
import random
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger("AuraBlogEngine")

# 모듈 내부 의존성 (완전 독립 레고 블록)
from brands.aura.aura_100_topics import AURA_100_TOPICS, get_all_topics, get_topic_by_id, get_topics_by_category
from brands.aura.aura_keyword_matrix import AuraKeywordMatrix


class AuraBlogEngine:
    """
    💖 100대 주제 + 3중 가드레일 실시간 키워드 결합 2030 데이팅 블로그 엔진
    """
    BRAND = "aura"
    NAME = "Aura 2030 Dating Blog Engine"

    def __init__(self):
        self.keyword_matrix = AuraKeywordMatrix()
        self.topics = AURA_100_TOPICS
        self.rotation_index = 0

    def get_next_topic(self) -> Dict[str, Any]:
        """100대 주제를 순차적으로 1개씩 순환 반환"""
        topic = self.topics[self.rotation_index % len(self.topics)]
        self.rotation_index = (self.rotation_index + 1) % len(self.topics)
        return topic

    def get_random_topic(self, category: Optional[str] = None) -> Dict[str, Any]:
        """특정 카테고리 또는 전체에서 랜덤하게 주제 1개 반환"""
        if category:
            pool = get_topics_by_category(category)
            if pool:
                return random.choice(pool)
        return random.choice(self.topics)

    def build_article_package(self, topic_id: Optional[int] = None) -> Dict[str, Any]:
        """
        100대 주제 중 1개를 선택하여 3중 가드레일을 통과한 실시간 네이버/구글 키워드를 결합,
        완벽한 SEO 포스팅 패키지를 생성합니다.
        """
        # 1. 주제 선택
        if topic_id is not None:
            topic = get_topic_by_id(topic_id)
        else:
            topic = self.get_next_topic()

        cat_key = topic["category"]
        seed_topic = topic["title"]
        aura_feature = topic.get("aura_feature", "Aura AI 매력 리포트")
        intent = topic.get("intent", "2030 연애 꿀팁")

        # 2. [가드레일 1 & 2] 해당 카테고리 전용 실시간 키워드 국소 추출
        # (엉뚱한 키워드가 절대 들어가지 않도록 카테고리 방에서만 인출)
        seo_brief = self.keyword_matrix.build_seo_article_brief(
            seed_topic=seed_topic,
            category=cat_key
        )

        naver_keys = seo_brief.get("seo_title_keywords", [])
        google_keys = seo_brief.get("h2_h3_subheading_keywords", [])
        hashtags = seo_brief.get("viral_hashtags", [])

        # 3. [가드레일 3] 자연스러운 제목 및 소제목 합성
        main_naver_kw = naver_keys[0] if naver_keys else "소개팅 성공법"
        sub_naver_kw = naver_keys[1] if len(naver_keys) > 1 else ""

        # 네이버 스마트블록 1위용 자연스러운 고클릭률 제목 생성
        if sub_naver_kw:
            title = f"2026 {seed_topic} | {main_naver_kw} & {sub_naver_kw} 실전 가이드"
        else:
            title = f"2026 {seed_topic} | {main_naver_kw} 핵심 공략법"

        h2_title = google_keys[0] if len(google_keys) > 0 else f"{main_naver_kw} 실전 팁"
        h3_title_1 = google_keys[1] if len(google_keys) > 1 else "자연스러운 티키타카 대화법"
        h3_title_2 = google_keys[2] if len(google_keys) > 2 else "호감도를 높이는 실전 노하우"

        # 4. 고품질 HTML 본문 템플릿 렌더링 (제미나이 AI가 채우거나 기본 엔진이 즉시 배포)
        content_html = f"""
        <div class="aura-magazine-article" style="font-family:'Pretendard', sans-serif; line-height:1.8; color:#1E293B;">
            <header style="margin-bottom:24px; border-bottom:2px solid #F1F5F9; padding-bottom:16px;">
                <span style="background:#FDF2F8; color:#DB2777; font-size:12px; font-weight:700; padding:4px 10px; border-radius:20px;">
                    💖 Aura 2030 연애 매거진 · {seo_brief['category_name']}
                </span>
                <h1 style="font-size:22px; font-weight:800; color:#0F172A; margin:14px 0 8px 0; line-height:1.4;">
                    {title}
                </h1>
                <p style="font-size:14px; color:#64748B; margin:0;">
                    기획 의도: {intent}
                </p>
            </header>

            <section style="margin-bottom:28px;">
                <h2 style="font-size:18px; font-weight:700; color:#EC4899; margin-bottom:12px; display:flex; align-items:center; gap:8px;">
                    ✨ 1. {h2_title}
                </h2>
                <p style="font-size:15px; color:#334155;">
                    소개팅과 연애에서 가장 중요한 순간은 바로 상대방의 미묘한 시그널과 대화의 핑퐁을 캐치하는 것입니다. 
                    많은 2030 싱글들이 <strong>{main_naver_kw}</strong>에 대해 고민하지만, 핵심은 
                    상대방의 입장에서 편안함을 느끼게 만드는 작은 배려와 공감에서 시작됩니다.
                </p>
            </section>

            <section style="margin-bottom:28px;">
                <h3 style="font-size:16px; font-weight:700; color:#0F172A; margin-bottom:10px;">
                    💡 2. {h3_title_1}
                </h3>
                <p style="font-size:15px; color:#334155;">
                    대화가 끊기거나 어색한 침묵이 흐를 때는 무리하게 새로운 주제를 던지기보다, 
                    방금 상대방이 했던 말의 마지막 단어에 '공감' 한 마디를 얹고 가벼운 질문을 이어가는 것이 좋습니다.
                    이는 상대방에게 "내 이야기에 진심으로 귀 기울이고 있구나"라는 깊은 신뢰감을 줍니다.
                </p>
            </section>

            <section style="margin-bottom:28px;">
                <h3 style="font-size:16px; font-weight:700; color:#0F172A; margin-bottom:10px;">
                    🔮 3. {h3_title_2}
                </h3>
                <p style="font-size:15px; color:#334155;">
                    나의 대화 스타일과 첫인상 매력 포인트를 객관적으로 파악하고 있다면 훨씬 더 자신감 있게 상대방을 대할 수 있습니다. 
                    단점을 억지로 숨기려 하기보다는, 나만의 독보적인 성향과 분위기를 솔직하게 표현하는 것이 가장 큰 무기입니다.
                </p>
            </section>

            <!-- 🎁 Aura 앱 공식 전환 CTA 배너 (Call to Action) -->
            <div style="background:linear-gradient(135deg, #FFF1F2 0%, #FDF2F8 100%); border:1px solid #FECDD3; border-radius:14px; padding:20px; margin:32px 0; text-align:center;">
                <span style="font-size:24px;">💖</span>
                <h4 style="margin:8px 0 6px 0; font-size:16px; font-weight:800; color:#BE123C;">
                    내 연애 매력도와 카톡 스타일, 객관적으로 몇 점일까?
                </h4>
                <p style="font-size:13.5px; color:#4C0519; margin:0 0 14px 0; line-height:1.5;">
                    지금 <strong>[{aura_feature}]</strong>에서 AI가 정밀 분석해 주는 
                    나만의 첫인상 매력 리포트와 티키타카 코칭을 무료로 확인해 보세요!
                </p>
                <a href="https://aura-dating.app" target="_blank" style="display:inline-block; background:#EC4899; color:#FFFFFF; font-weight:700; font-size:13.5px; padding:10px 22px; border-radius:25px; text-decoration:none; box-shadow:0 4px 12px rgba(236,72,153,0.3);">
                    👉 Aura 공식 앱에서 내 매력 진단받기
                </a>
            </div>

            <footer style="margin-top:20px; padding-top:16px; border-top:1px dashed #E2E8F0;">
                <div style="display:flex; flex-wrap:wrap; gap:6px;">
                    {' '.join([f'<span style="background:#F1F5F9; color:#475569; padding:3px 8px; border-radius:6px; font-size:12px;">{t}</span>' for t in hashtags])}
                </div>
            </footer>
        </div>
        """

        clean_tags = [t.replace("#", "") for t in hashtags]

        return {
            "topic_id": topic["id"],
            "category": cat_key,
            "category_name": seo_brief["category_name"],
            "seed_topic": seed_topic,
            "title": title,
            "content_html": content_html,
            "tags": clean_tags,
            "hashtags_str": " ".join(hashtags),
            "aura_feature": aura_feature,
            "seo_brief": seo_brief
        }


if __name__ == "__main__":
    engine = AuraBlogEngine()
    
    print("\n=======================================================")
    print("💖 [Aura] 100대 주제 + 3중 가드레일 실시간 결합 블로그 생성 테스트")
    print("=======================================================")
    
    # 1. 카톡 주제 테스트 (ID: 2)
    sample1 = engine.build_article_package(topic_id=2)
    print(f"\n[주제 #2 ({sample1['category_name']})]")
    print(f"  - 생성 제목: {sample1['title']}")
    print(f"  - 네이버 실시간: {sample1['seo_brief']['seo_title_keywords']}")
    print(f"  - 구글 실시간:   {sample1['seo_brief']['h2_h3_subheading_keywords']}")
    print(f"  - 해시태그:     {sample1['hashtags_str'][:60]}...")
    
    # 2. 맛집/데이트 코스 주제 테스트 (ID: 19)
    sample2 = engine.build_article_package(topic_id=19)
    print(f"\n[주제 #19 ({sample2['category_name']})]")
    print(f"  - 생성 제목: {sample2['title']}")
    print(f"  - 네이버 실시간: {sample2['seo_brief']['seo_title_keywords']}")
    print(f"  - 구글 실시간:   {sample2['seo_brief']['h2_h3_subheading_keywords']}")
    print(f"  - 해시태그:     {sample2['hashtags_str'][:60]}...")
