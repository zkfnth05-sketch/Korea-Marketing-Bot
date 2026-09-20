"""
💖 Aura 2030 전용 블로그 SEO & 실시간 키워드 합성 엔진 (AuraBlogEngine)
=======================================================================
- 브랜드: Aura (2030 AI 데이팅 / 소개팅 코칭 / 매력 리포트 / 데이트 코스)
- 역할:
  1. 📚 100대 마스터 주제 풀에서 순환 또는 지정 추출
  2. 🛡️ [가드레일 1 & 2] 주제별 6대 카테고리 전용 시드어(Scoped Seed) 실시간 키워드 수집 및 노이즈 필터링
  3. 🤖 [Gemini 2,000자 칼럼] 무료키 우선 체인으로 고품질 실전 칼럼 작성 (비용 0원)
  4. 🎨 [맞춤 사진 1장] 글 스토리 맥락에 100% 어울리는 16:9 감성 사진 실시간 생성 (유료키 2단 롤오버)
  5. 🌐 네이버 스마트블록 1위 제목 + 대표 커버 사진 + H2/H3 소제목 + Aura 앱 전환 CTA + 4대 플랫폼 태그 완성
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
import markdown
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
    - Gemini 2,000자 칼럼 자동 작성
    - 주제 맥락 맞춤 16:9 사진 1장 실시간 생성
    """
    BRAND = "aura"
    NAME = "Aura 2030 Magazine Blog Engine"
    LANDING_URL = "https://aura-ai-dating.vercel.app/"

    def __init__(self):
        self.keyword_matrix = AuraKeywordMatrix()
        self.topics = AURA_100_TOPICS
        self.rotation_index = 0
        self._writer = None
        self._image_gen = None

    def _get_writer(self):
        if self._writer is None:
            from brands.aura.aura_gemini_writer import AuraGeminiWriter
            self._writer = AuraGeminiWriter()
        return self._writer

    def _get_image_gen(self):
        if self._image_gen is None:
            from brands.aura.aura_image_generator import AuraImageGenerator
            self._image_gen = AuraImageGenerator()
        return self._image_gen

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

    def build_article_package(
        self,
        topic_id: Optional[int] = None,
        use_gemini: bool = True,
        generate_photo: bool = True
    ) -> Dict[str, Any]:
        """
        100대 주제 중 1개를 선택하여 실시간 키워드 결합 ➔ Gemini 2,000자 칼럼 ➔ 맞춤 사진 1장 생성
        완벽한 SEO 포스팅 풀 패키지를 생성합니다.
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
        seo_brief = self.keyword_matrix.build_seo_article_brief(
            seed_topic=seed_topic,
            category=cat_key
        )

        naver_keys = seo_brief.get("seo_title_keywords", [])
        google_keys = seo_brief.get("h2_h3_subheading_keywords", [])
        hashtags = seo_brief.get("viral_hashtags", [])
        clean_tags = [t.replace("#", "") for t in hashtags]

        # 3. Gemini 실시간 본문 작성 (무료키 1순위)
        gemini_result = None
        if use_gemini:
            try:
                writer = self._get_writer()
                gemini_result = writer.write_magazine_article(topic, seo_brief)
                logger.info(f"✅ [AuraBlog] Gemini 2,000자 칼럼 작성 완료: '{gemini_result['title']}'")
            except Exception as e:
                logger.warning(f"⚠️ [AuraBlog] Gemini 작성 실패 (폴백 템플릿 사용): {e}")

        # 4. 주제 맞춤 실사 사진 1장 실시간 생성 (유료키 1순위)
        photo_info = {
            "image_path": "",
            "web_url": "https://images.unsplash.com/photo-1517256064527-09c73fc73e38?w=1200&auto=format&fit=crop&q=80",
            "is_fallback": True,
            "prompt_used": ""
        }
        if generate_photo:
            try:
                img_gen = self._get_image_gen()
                custom_p = gemini_result.get("visual_prompt") if gemini_result else None
                photo_info = img_gen.generate_article_photo(
                    topic_id=topic["id"],
                    category=cat_key,
                    topic_title=seed_topic,
                    custom_visual_prompt=custom_p
                )
                logger.info(f"✅ [AuraBlog] 맞춤 사진 1장 생성 완료 (경로: {photo_info['web_url']})")
            except Exception as e:
                logger.warning(f"⚠️ [AuraBlog] 사진 생성 실패 (폴백 사용): {e}")

        # 5. 완성형 HTML 본문 조립
        cover_img_url = photo_info["web_url"]

        title = gemini_result.get("title", gemini_result.get("title_naver", f"2026 {seed_topic}")) if gemini_result else f"2026 {seed_topic}"
        title_naver = gemini_result.get("title_naver", title) if gemini_result else title
        title_tistory = gemini_result.get("title_tistory", title) if gemini_result else title
        title_kakao = gemini_result.get("title_kakao", title) if gemini_result else title
        excerpt = gemini_result.get("excerpt", f"2030 {seed_topic} 실전 가이드") if gemini_result else f"2030 {seed_topic} 실전 가이드"

        if gemini_result and gemini_result.get("content_md"):
            content_md = gemini_result["content_md"]
            # 본문에 남아있을 수 있는 불필요한 마크다운 이미지 코드 및 중복 대제목 정제
            import re
            content_md = re.sub(r'!\[.*?\]\(.*?\)', '', content_md).strip()
            if content_md.startswith("# "):
                content_md = content_md.split("\n", 1)[-1].strip()

            body_html = markdown.markdown(content_md, extensions=['extra', 'tables', 'nl2br'])

            content_html = f"""
        <div class="aura-magazine-article" style="font-family:'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif; line-height:1.85; color:#1E293B; max-width:680px; margin:0 auto; padding:10px 4px;">
            <!-- 🌟 [맨 처음이 사진] 16:9 고화질 감성 대표 비주얼 -->
            <figure class="aura-magazine-cover" style="margin:0 0 24px 0; border-radius:14px; overflow:hidden; box-shadow:0 6px 24px rgba(0,0,0,0.08);">
                <img src="{cover_img_url}" alt="{title}" style="width:100%; height:auto; display:block; object-fit:cover; aspect-ratio:16/9;" />
                <figcaption style="font-size:12px; color:#94A3B8; text-align:center; padding:8px 12px; background:#F8FAFC;">
                    💖 Aura 2030 에디토리얼 비주얼 · {seo_brief['category_name']}
                </figcaption>
            </figure>

            <!-- 📝 [그 밑이 글] 카테고리 뱃지 & 대제목 & 요약 -->
            <header style="margin-bottom:24px; border-bottom:2px solid #F1F5F9; padding-bottom:16px;">
                <span style="background:#FDF2F8; color:#DB2777; font-size:12px; font-weight:700; padding:4px 12px; border-radius:20px; display:inline-block; margin-bottom:8px;">
                    💖 Aura 2030 매거진 · {seo_brief['category_name']}
                </span>
                <h1 style="font-size:23px; font-weight:800; color:#0F172A; margin:10px 0 8px 0; line-height:1.4;">
                    {title}
                </h1>
                <p style="font-size:14.5px; color:#64748B; margin:6px 0 0 0; line-height:1.6;">
                    {excerpt}
                </p>
            </header>

            <!-- 2,000자 풍성한 본문 마크다운 렌더링 -->
            <div class="aura-magazine-body" style="font-size:15.5px; color:#334155; line-height:1.9;">
                {body_html}
            </div>

            <!-- 🎁 Aura 앱 공식 전환 CTA 배너 (Call to Action) -->
            <div style="background:linear-gradient(135deg, #FFF1F2 0%, #FDF2F8 100%); border:1px solid #FECDD3; border-radius:16px; padding:22px; margin:32px 0; text-align:center; box-shadow:0 6px 20px rgba(236,72,153,0.08);">
                <span style="font-size:26px;">💖</span>
                <h4 style="margin:8px 0 6px 0; font-size:16px; font-weight:800; color:#BE123C;">
                    내 연애 매력도와 카톡 스타일, 객관적으로 몇 점일까?
                </h4>
                <p style="font-size:13.5px; color:#4C0519; margin:0 0 16px 0; line-height:1.5;">
                    지금 <strong>[{aura_feature}]</strong>에서 AI가 정밀 분석해 주는 
                    나만의 첫인상 매력 리포트와 실시간 대화 코칭을 확인해 보세요!
                </p>
                <a href="{self.LANDING_URL}" target="_blank" style="display:inline-block; background:linear-gradient(135deg, #EC4899 0%, #DB2777 100%); color:#FFFFFF; font-weight:700; font-size:13.5px; padding:11px 26px; border-radius:30px; text-decoration:none; box-shadow:0 4px 14px rgba(236,72,153,0.35);">
                    👉 Aura 공식 앱에서 내 매력 진단받기
                </a>
            </div>

            <!-- Footer Tags -->
            <footer style="margin-top:20px; padding-top:16px; border-top:1px dashed #E2E8F0;">
                <div style="display:flex; flex-wrap:wrap; gap:6px;">
                    {' '.join([f'<span style="background:#F1F5F9; color:#475569; padding:4px 9px; border-radius:6px; font-size:12px;">{t}</span>' for t in hashtags])}
                </div>
            </footer>
        </div>
        """
        else:
            # Fallback 템플릿
            main_naver_kw = naver_keys[0] if naver_keys else "소개팅 성공법"
            sub_naver_kw = naver_keys[1] if len(naver_keys) > 1 else ""
            title = f"2026 {seed_topic} | {main_naver_kw} & {sub_naver_kw} 실전 가이드" if sub_naver_kw else f"2026 {seed_topic} | {main_naver_kw} 핵심 공략법"
            intro = f"소개팅과 연애에서 가장 중요한 순간은 바로 상대방의 미묘한 시그널과 대화의 핑퐁을 캐치하는 것입니다. {main_naver_kw}에 대해 고민하는 2030 싱글들을 위한 실전 꿀팁을 전해드립니다."
            sections = [
                {
                    "heading": f"✨ 1. {google_keys[0] if len(google_keys) > 0 else f'{main_naver_kw} 실전 팁'}",
                    "body": "상대방의 입장에서 편안함을 느끼게 만드는 작은 배려와 공감에서 진짜 대화가 시작됩니다. 과도한 질문보다는 상대방의 톤과 템포에 맞춰 호흡을 가다듬으세요."
                },
                {
                    "heading": f"💡 2. {google_keys[1] if len(google_keys) > 1 else '자연스러운 티키타카 대화법'}",
                    "body": "대화가 끊기거나 어색한 침묵이 흐를 때는 무리하게 새로운 주제를 던지기보다, 방금 상대방이 했던 말의 마지막 단어에 공감 한 마디를 얹고 가벼운 질문을 이어가세요."
                },
                {
                    "heading": f"🔮 3. {google_keys[2] if len(google_keys) > 2 else '호감도를 높이는 실전 노하우'}",
                    "body": "나의 대화 스타일과 첫인상 매력 포인트를 객관적으로 파악하고 있다면 훨씬 더 자신감 있게 상대방을 대할 수 있습니다. 단점을 숨기기보다 나만의 분위기를 솔직하게 표현하세요."
                }
            ]
            tip_box = "대화의 핵심은 화려한 말솜씨가 아니라, 상대방이 말하기 편안하도록 리액션을 열어주는 배려입니다."

            content_md = f"""# {title}

![{title}]({cover_img_url})

{intro}

## {sections[0]['heading']}
{sections[0]['body']}

## {sections[1]['heading']}
{sections[1]['body']}

## {sections[2]['heading']}
{sections[2]['body']}

### 💡 Aura 에디터 실전 치트키
{tip_box}

👉 [{self.LANDING_URL}]({self.LANDING_URL})

{' '.join(hashtags)}
"""
            sections_html = ""
            for sec in sections:
                sections_html += f"""
                <section style="margin-bottom:28px;">
                    <h2 style="font-size:17.5px; font-weight:700; color:#BE123C; margin-bottom:12px; display:flex; align-items:center; gap:8px;">
                        {sec.get('heading', '')}
                    </h2>
                    <p style="font-size:15px; color:#334155; line-height:1.85; margin:0 0 10px 0;">
                        {sec.get('body', '')}
                    </p>
                </section>
                """

            content_html = f"""
            <div class="aura-magazine-article" style="font-family:'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif; line-height:1.8; color:#1E293B; max-width:680px; margin:0 auto;">
                <header style="margin-bottom:20px; border-bottom:2px solid #F1F5F9; padding-bottom:16px;">
                    <span style="background:#FDF2F8; color:#DB2777; font-size:12px; font-weight:700; padding:4px 12px; border-radius:20px; display:inline-block; margin-bottom:8px;">
                        💖 Aura 2030 매거진 · {seo_brief['category_name']}
                    </span>
                    <h1 style="font-size:22px; font-weight:800; color:#0F172A; margin:10px 0 8px 0; line-height:1.4;">
                        {title}
                    </h1>
                    <p style="font-size:13.5px; color:#64748B; margin:0;">
                        기획 의도: {intent}
                    </p>
                </header>

                <figure class="aura-magazine-cover" style="margin:24px 0; border-radius:18px; overflow:hidden; border:1px solid #E2E8F0; box-shadow:0 6px 20px rgba(0,0,0,0.06);">
                    <img src="{cover_img_url}" alt="{title}" style="width:100%; height:auto; display:block; object-fit:cover; aspect-ratio:16/9;" />
                    <figcaption style="font-size:11.5px; color:#94A3B8; text-align:center; padding:8px 12px; background:#F8FAFC;">
                        💖 Aura 2030 에디토리얼 비주얼 · {seo_brief['category_name']}
                    </figcaption>
                </figure>

                <div style="background:#FFF1F2; border-left:4px solid #EC4899; padding:16px 18px; border-radius:0 12px 12px 0; margin-bottom:28px;">
                    <p style="font-size:14.5px; color:#4C0519; font-weight:500; margin:0; line-height:1.75;">
                        {intro}
                    </p>
                </div>

                {sections_html}

                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:14px; padding:16px 18px; margin:28px 0;">
                    <div style="font-weight:700; font-size:13.5px; color:#0F172A; margin-bottom:6px; display:flex; align-items:center; gap:6px;">
                        <span>💡</span> <span>Aura 에디터 한 줄 치트키</span>
                    </div>
                    <p style="font-size:13.5px; color:#475569; margin:0; line-height:1.6;">
                        {tip_box}
                    </p>
                </div>

                <div style="background:linear-gradient(135deg, #FFF1F2 0%, #FDF2F8 100%); border:1px solid #FECDD3; border-radius:16px; padding:22px; margin:32px 0; text-align:center; box-shadow:0 6px 20px rgba(236,72,153,0.08);">
                    <span style="font-size:26px;">💖</span>
                    <h4 style="margin:8px 0 6px 0; font-size:16px; font-weight:800; color:#BE123C;">
                        내 연애 매력도와 카톡 스타일, 객관적으로 몇 점일까?
                    </h4>
                    <p style="font-size:13.5px; color:#4C0519; margin:0 0 16px 0; line-height:1.5;">
                        지금 <strong>[{aura_feature}]</strong>에서 AI가 정밀 분석해 주는 
                        나만의 첫인상 매력 리포트와 실시간 대화 코칭을 확인해 보세요!
                    </p>
                    <a href="{self.LANDING_URL}" target="_blank" style="display:inline-block; background:linear-gradient(135deg, #EC4899 0%, #DB2777 100%); color:#FFFFFF; font-weight:700; font-size:13.5px; padding:11px 26px; border-radius:30px; text-decoration:none; box-shadow:0 4px 14px rgba(236,72,153,0.35);">
                        👉 Aura 공식 앱에서 내 매력 진단받기
                    </a>
                </div>

                <footer style="margin-top:20px; padding-top:16px; border-top:1px dashed #E2E8F0;">
                    <div style="display:flex; flex-wrap:wrap; gap:6px;">
                        {' '.join([f'<span style="background:#F1F5F9; color:#475569; padding:4px 9px; border-radius:6px; font-size:12px;">{t}</span>' for t in hashtags])}
                    </div>
                </footer>
            </div>
            """

        # 🌐 4개 국어(KO, EN, JA, ES) 자동 번역 생성 (아우라 전용 무료 키 라운드로빈 활용)
        translations = {}
        try:
            from .aura_translator import AuraTranslator
            translator = AuraTranslator()
            lounge_summary = (
                f"💖 [Aura 2030 매거진 공식 칼럼]\n\n"
                f"📌 {title_kakao or title_naver or title}\n\n"
                f"{excerpt}\n\n"
                f"에디터의 꿀팁이 담긴 칼럼 전문을 지금 바로 라운지에서 확인해 보세요!\n\n"
                f"👉 공식 라운지 바로가기: {self.LANDING_URL}"
            )
            translations = translator.translate_full_package({
                "title": title,
                "title_kakao": title_kakao,
                "title_naver": title_naver,
                "excerpt": excerpt,
                "lounge_content": lounge_summary,
                "content_md": content_md
            })
            logger.info("✅ [AuraBlogEngine] 4개 국어(KO, EN, JA, ES) 패키지 번역 완료")
        except Exception as e:
            logger.warning(f"⚠️ [AuraBlogEngine] 번역 패키징 예외: {e}")

        return {
            "topic_id": topic["id"],
            "category": cat_key,
            "category_name": seo_brief["category_name"],
            "seed_topic": seed_topic,
            "title": title,
            "title_naver": title_naver,
            "title_tistory": title_tistory,
            "title_kakao": title_kakao,
            "excerpt": excerpt,
            "content_md": content_md,
            "content_html": content_html,
            "image_path": photo_info.get("image_path", ""),
            "image_url": photo_info.get("web_url", ""),
            "is_image_fallback": photo_info.get("is_fallback", False),
            "visual_prompt": photo_info.get("prompt_used", ""),
            "tags": clean_tags,
            "hashtags_str": " ".join(hashtags),
            "aura_feature": aura_feature,
            "landing_url": self.LANDING_URL,
            "discussion_prompt": gemini_result.get("discussion_prompt", "Aura 싱글 여러분의 생각은 어떠신가요? 아래 댓글로 여러분만의 솔직한 생각과 꿀팁을 들려주세요!") if gemini_result else "Aura 싱글 여러분의 생각은 어떠신가요? 아래 댓글로 여러분만의 솔직한 생각과 꿀팁을 들려주세요!",
            "translations": translations,
            "seo_brief": seo_brief
        }


if __name__ == "__main__":
    engine = AuraBlogEngine()
    print("💖 [AuraBlogEngine] 글 + 사진 결합 1회 생성 테스트 시작...")
    res = engine.build_article_package(topic_id=1, use_gemini=True, generate_photo=True)
    print("\n[생성 결과]")
    print(f"  - 제목: {res['title']}")
    print(f"  - 사진 URL: {res['image_url']}")
    print(f"  - 로컬 파일: {res['image_path']}")
    print(f"  - 본문 길이: {len(res['content_html']):,} 글자")
    print(f"  - 태그: {res['hashtags_str']}")
