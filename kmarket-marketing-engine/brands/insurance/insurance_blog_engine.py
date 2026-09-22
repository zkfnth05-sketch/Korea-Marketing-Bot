# -*- coding: utf-8 -*-
"""
🛡️ InsureBalance 전용 블로그 SEO & 실시간 키워드 합성 엔진 (InsuranceBlogEngine)
=============================================================================
- 브랜드: InsureBalance (보험 비교 & 보장 분석 & 리모델링 & 보험금 청구)
- 역할:
  1. 📚 100대 마스터 주제 풀에서 순환 또는 지정 추출
  2. 🛡️ 6대 카테고리 전용 시드어 실시간 키워드 수집 및 노이즈 필터링
  3. 🤖 Gemini 2,000자 전문 칼럼 작성 (비용 0원 무료키 1순위)
  4. 🎨 글 스토리 맥락에 100% 어울리는 16:9 감성 사진 실시간 생성
  5. 🌐 3대 블로그(네이버, 티스토리, 브런치) 동시/순차 자동 발행
"""

import os
import sys
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

logger = logging.getLogger("InsuranceBlogEngine")

from brands.insurance.insurance_100_topics import (
    INSURANCE_100_TOPICS,
    get_all_topics,
    get_topic_by_id,
    get_topics_by_category
)
from brands.insurance.insurance_keyword_matrix import InsuranceKeywordMatrix


class InsuranceBlogEngine:
    """
    🛡️ 100대 주제 + 실시간 키워드 결합 보험 비교 블로그 엔진
    - Gemini 2,000자 전문 칼럼 자동 작성
    - 16:9 맞춤 실사 사진 1장 실시간 생성
    - 네이버, 티스토리, 브런치 무인 자동 발행
    """
    BRAND = "insurance"
    NAME = "InsureBalance Blog Engine"
    LANDING_URL = "https://insure-rebalance.vercel.app/"

    def __init__(self):
        self.keyword_matrix = InsuranceKeywordMatrix()
        self.topics = INSURANCE_100_TOPICS
        self.rotation_index = 0
        self._writer = None
        self._image_gen = None
        self._publisher = None

    def _get_writer(self):
        if self._writer is None:
            from brands.insurance.insurance_gemini_writer import InsuranceGeminiWriter
            self._writer = InsuranceGeminiWriter()
        return self._writer

    def _get_image_gen(self):
        if self._image_gen is None:
            from brands.insurance.insurance_image_generator import InsuranceImageGenerator
            self._image_gen = InsuranceImageGenerator()
        return self._image_gen

    def _get_publisher(self):
        if self._publisher is None:
            from brands.insurance.insurance_multi_publisher import InsuranceMultiPublisher
            self._publisher = InsuranceMultiPublisher()
        return self._publisher

    def get_next_topic(self) -> Dict[str, Any]:
        """100대 주제를 파일 기반으로 1개씩 순환 반환 (중복 발행 100% 원천 차단)"""
        state_file = PROJECT_ROOT / "data" / "insurance_blog_rotation_state.json"
        state = {}
        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
            except Exception:
                state = {}

        idx = state.get("current_topic_index", 0)
        topic = self.topics[idx % len(self.topics)]

        state["current_topic_index"] = (idx + 1) % len(self.topics)
        state["last_topic_id"] = topic["id"]
        state["last_title"] = topic["title"]
        try:
            state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"상태 저장 실패: {e}")

        return topic

    def get_random_topic(self, category: Optional[str] = None) -> Dict[str, Any]:
        """랜덤 주제 반환"""
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
        """
        # 1. 주제 선택
        if topic_id is not None:
            topic = get_topic_by_id(topic_id)
        else:
            topic = self.get_next_topic()

        cat_key = topic["category"]
        seed_topic = topic["title"]
        app_feature = topic.get("app_feature", "보험리밸런스 AI 보장 분석")

        # 2. 실시간 키워드 추출
        seo_brief = self.keyword_matrix.build_seo_article_brief(
            seed_topic=seed_topic,
            category=cat_key
        )

        # 3. Gemini 실시간 본문 작성
        gemini_result = None
        if use_gemini:
            try:
                writer = self._get_writer()
                gemini_result = writer.write_magazine_article(topic, seo_brief)
                logger.info(f"✅ [InsuranceBlog] Gemini 2,000자 칼럼 작성 완료: '{gemini_result['title']}'")
            except Exception as e:
                logger.warning(f"⚠️ [InsuranceBlog] Gemini 작성 실패: {e}")

        # 4. 맞춤 실사 사진 1장 생성
        photo_info = {
            "image_path": "",
            "web_url": "https://images.unsplash.com/photo-1450133064473-71024230f91b?w=1200&auto=format&fit=crop&q=80",
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
                logger.info(f"✅ [InsuranceBlog] 맞춤 사진 1장 생성 완료 ({photo_info['web_url']})")
            except Exception as e:
                logger.warning(f"⚠️ [InsuranceBlog] 사진 생성 실패: {e}")

    @staticmethod
    def clean_markdown_body(raw_md: str) -> str:
        """본문에서 [이미지:...], [사진:...], 불필요한 특수문자 선을 100% 제거하고 깔끔한 줄바꿈 유지"""
        import re
        text = re.sub(r'\[.*?이미지.*?\]', '', raw_md)
        text = re.sub(r'\[.*?사진.*?\]', '', text)
        text = re.sub(r'\[.*?16:9.*?\]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'🖼️\s*\[.*?\]', '', text)
        text = re.sub(r'━{3,}', '', text)
        text = re.sub(r'-{4,}', '', text)
        text = re.sub(r'={4,}', '', text)

        lines = text.split("\n")
        cleaned = []
        for line in lines:
            l = line.strip()
            # 빈 줄 유지
            if not l:
                cleaned.append("")
                continue
            cleaned.append(l)

        res = "\n".join(cleaned)
        res = re.sub(r'\n{3,}', '\n\n', res).strip()
        return res

    @staticmethod
    def render_clean_html_body(clean_md: str, landing_url: str) -> str:
        """티스토리/웹 전용 고품질 여백(margin/line-height) 및 비주얼 박스 카드 HTML 렌더링"""
        import re
        blocks = clean_md.split("\n\n")
        html_parts = []

        for block in blocks:
            b = block.strip()
            if not b:
                continue

            # 인용구 (비주얼 훅 박스)
            if b.startswith(">"):
                b_lines = [line.lstrip(">").strip() for line in b.split("\n")]
                inner_text = "<br/>".join([l for l in b_lines if l])
                inner_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', inner_text)
                card_html = f"""<blockquote style="margin: 26px 0; padding: 18px 22px; background-color: #f1f5f9; border-left: 4px solid #0284c7; border-radius: 8px; font-size: 15px; color: #1e293b; line-height: 1.8;">{inner_text}</blockquote>"""
                html_parts.append(card_html)
            elif b.startswith("# "):
                title_text = b[2:].strip()
                html_parts.append(f"""<h2 style="font-size: 22px; font-weight: bold; margin: 30px 0 16px 0; color: #0f172a;">{title_text}</h2>""")
            elif b.startswith("## ") or b.startswith("### "):
                sub_text = re.sub(r'^#+\s*', '', b).strip()
                html_parts.append(f"""<h3 style="font-size: 18px; font-weight: bold; margin: 26px 0 12px 0; color: #0f172a;">{sub_text}</h3>""")
            else:
                p_text = b.replace("\n", "<br/>")
                p_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', p_text)
                html_parts.append(f"""<p style="margin-bottom: 22px; line-height: 1.85; font-size: 16px; color: #334155;">{p_text}</p>""")

        # 하단 공식 CTA 카드 첨부
        cta_html = f"""
<div style="margin-top: 36px; padding: 22px; background-color: #f8fafc; border-left: 5px solid #0284c7; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
  <p style="font-weight: bold; font-size: 17px; margin: 0 0 8px 0; color: #0f172a;">🛡️ 내 보험 보장 점수, 3분 만에 확인해보세요</p>
  <p style="font-size: 14px; color: #475569; margin: 0 0 16px 0; line-height: 1.6;">복잡한 보험 약관과 부족한 보장, 보험리밸런스가 객관적으로 진단해 드립니다.</p>
  <p style="margin: 0;"><a href="{landing_url}" target="_blank" style="display: inline-block; padding: 12px 24px; background-color: #0284c7; color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 15px;">보험리밸런스 무료 진단 시작하기 👉</a></p>
</div>
"""
        return "".join(html_parts) + cta_html

    def build_article_package(
        self,
        topic_id: Optional[int] = None,
        use_gemini: bool = True,
        generate_photo: bool = True
    ) -> Dict[str, Any]:
        """
        100대 주제 중 1개를 선택하여 실시간 키워드 결합 ➔ Gemini 2,000자 칼럼 ➔ 맞춤 사진 1장 생성
        """
        # 1. 주제 선택
        if topic_id is not None:
            topic = get_topic_by_id(topic_id)
        else:
            topic = self.get_next_topic()

        cat_key = topic["category"]
        seed_topic = topic["title"]
        app_feature = topic.get("app_feature", "보험리밸런스 AI 보장 분석")

        # 2. 실시간 키워드 추출
        seo_brief = self.keyword_matrix.build_seo_article_brief(
            seed_topic=seed_topic,
            category=cat_key
        )

        # 3. Gemini 실시간 본문 작성
        gemini_result = None
        if use_gemini:
            try:
                writer = self._get_writer()
                gemini_result = writer.write_magazine_article(topic, seo_brief)
                logger.info(f"✅ [InsuranceBlog] Gemini 2,000자 칼럼 작성 완료: '{gemini_result['title']}'")
            except Exception as e:
                logger.warning(f"⚠️ [InsuranceBlog] Gemini 작성 실패: {e}")

        # 4. 맞춤 실사 사진 1장 생성
        photo_info = {
            "image_path": "",
            "web_url": "https://images.unsplash.com/photo-1450133064473-71024230f91b?w=1200&auto=format&fit=crop&q=80",
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
                logger.info(f"✅ [InsuranceBlog] 맞춤 사진 1장 생성 완료 ({photo_info['web_url']})")
            except Exception as e:
                logger.warning(f"⚠️ [InsuranceBlog] 사진 생성 실패: {e}")

        # 5. 완성형 본문 조립 및 마크다운/HTML 정제
        title = gemini_result.get("title", seed_topic) if gemini_result else seed_topic
        title_naver = gemini_result.get("title_naver", title) if gemini_result else title
        title_tistory = gemini_result.get("title_tistory", title) if gemini_result else title
        title_brunch = gemini_result.get("title_brunch", title) if gemini_result else title

        raw_body_md = gemini_result.get("body_markdown", "") if gemini_result else f"## {seed_topic}\n\n내용 준비 중..."
        clean_body_md = self.clean_markdown_body(raw_body_md)
        full_html = self.render_clean_html_body(clean_body_md, self.LANDING_URL)

        return {
            "topic_id": topic["id"],
            "title": title,
            "title_naver": title_naver,
            "title_tistory": title_tistory,
            "title_brunch": title_brunch,
            "category": cat_key,
            "body_markdown": clean_body_md,
            "content_text": clean_body_md,
            "content_html": full_html,
            "summary": gemini_result.get("summary", "") if gemini_result else "",
            "tags": gemini_result.get("tags", topic.get("tags", ["보험비교", "InsureBalance"])) if gemini_result else topic.get("tags", []),
            "image_path": photo_info.get("image_path", ""),
            "image_url": photo_info.get("web_url", ""),
            "landing_url": self.LANDING_URL
        }

    def publish_now(self, topic_id: Optional[int] = None) -> Dict[str, Any]:
        """제미나이 1회 호출 + 이미지 1회 생성 ➔ 4대 채널(본진, 네이버, 티스토리, 브런치) 동시 배포"""
        logger.info("🎬 [InsuranceBlog] 1회 원고/이미지 생성 ➔ 4대 채널 동시 옴니 배포 시작")
        pkg = self.build_article_package(topic_id=topic_id)
        publisher = self._get_publisher()
        pub_results = publisher.publish_all(pkg, landing_url=self.LANDING_URL)

        return {
            "status": "success",
            "article_title": pkg["title"],
            "topic_id": pkg["topic_id"],
            "publishing_results": pub_results
        }

    def publish_omni(self, topic_id: Optional[int] = None) -> Dict[str, Any]:
        """4대 채널 옴니 배포 별칭"""
        return self.publish_now(topic_id=topic_id)
