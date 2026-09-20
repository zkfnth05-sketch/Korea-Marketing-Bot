# -*- coding: utf-8 -*-
"""
📈 StockMaster 전용 블로그 SEO & 실시간 키워드 합성 엔진 (StockBlogEngine)
========================================================================
- 브랜드: StockMaster AI (주식 AI 분석 & 퀀트 & 뇌동매매 방지)
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

logger = logging.getLogger("StockBlogEngine")

from brands.stock.stock_100_topics import (
    STOCK_100_TOPICS,
    get_all_topics,
    get_topic_by_id,
    get_topics_by_category
)
from brands.stock.stock_keyword_matrix import StockKeywordMatrix


class StockBlogEngine:
    """
    📈 100대 주제 + 실시간 키워드 결합 주식 AI 블로그 엔진
    - Gemini 2,000자 전문 투자 칼럼 자동 작성
    - 16:9 맞춤 실사 사진 1장 실시간 생성
    - 네이버, 티스토리, 브런치 무인 자동 발행
    """
    BRAND = "stock"
    NAME = "StockMaster Blog Engine"
    LANDING_URL = "https://stockmaster.ai"

    def __init__(self):
        self.keyword_matrix = StockKeywordMatrix()
        self.topics = STOCK_100_TOPICS
        self.rotation_index = 0
        self._writer = None
        self._image_gen = None
        self._publisher = None

    def _get_writer(self):
        if self._writer is None:
            from brands.stock.stock_gemini_writer import StockGeminiWriter
            self._writer = StockGeminiWriter()
        return self._writer

    def _get_image_gen(self):
        if self._image_gen is None:
            from brands.stock.stock_image_generator import StockImageGenerator
            self._image_gen = StockImageGenerator()
        return self._image_gen

    def _get_publisher(self):
        if self._publisher is None:
            from brands.stock.stock_multi_publisher import StockMultiPublisher
            self._publisher = StockMultiPublisher()
        return self._publisher

    def get_next_topic(self) -> Dict[str, Any]:
        """100대 주제를 파일 기반으로 1개씩 순환 반환 (중복 발행 100% 원천 차단)"""
        state_file = PROJECT_ROOT / "data" / "stock_blog_rotation_state.json"
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
        app_feature = topic.get("app_feature", "StockMaster AI 수급 레이더")

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
                logger.info(f"✅ [StockBlog] Gemini 2,000자 칼럼 작성 완료: '{gemini_result['title']}'")
            except Exception as e:
                logger.warning(f"⚠️ [StockBlog] Gemini 작성 실패: {e}")

        # 4. 맞춤 실사 사진 1장 생성
        photo_info = {
            "image_path": "",
            "web_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&auto=format&fit=crop&q=80",
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
                logger.info(f"✅ [StockBlog] 맞춤 사진 1장 생성 완료 ({photo_info['web_url']})")
            except Exception as e:
                logger.warning(f"⚠️ [StockBlog] 사진 생성 실패: {e}")

        # 5. 완성형 본문 조립
        title = gemini_result.get("title", seed_topic) if gemini_result else seed_topic
        title_naver = gemini_result.get("title_naver", title) if gemini_result else title
        title_tistory = gemini_result.get("title_tistory", title) if gemini_result else title
        title_brunch = gemini_result.get("title_brunch", title) if gemini_result else title

        body_md = gemini_result.get("body_markdown", "") if gemini_result else f"## {seed_topic}\n\n내용 준비 중..."
        body_html = markdown.markdown(body_md)

        # CTA 추가
        cta_html = f"""
<div style="margin-top: 30px; padding: 20px; background-color: #09090b; border-left: 4px solid #10b981; border-radius: 8px; color: #ffffff;">
  <p style="font-weight: bold; font-size: 16px; margin-bottom: 8px; color: #10b981;">📈 뇌동매매 끝! AI 데이터로 검증된 투자 신호</p>
  <p style="font-size: 14px; color: #a1a1aa; margin-bottom: 12px;">외국인·기관 수급, 재무 건전성, AI 퀀트 모멘텀을 실시간으로 확인하세요.</p>
  <a href="{self.LANDING_URL}" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #10b981; color: #000000; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 14px;">StockMaster AI 무료 시그널 확인하기 👉</a>
</div>
"""
        full_html = body_html + cta_html

        return {
            "topic_id": topic["id"],
            "title": title,
            "title_naver": title_naver,
            "title_tistory": title_tistory,
            "title_brunch": title_brunch,
            "category": cat_key,
            "body_markdown": body_md,
            "content_text": body_md,
            "content_html": full_html,
            "summary": gemini_result.get("summary", "") if gemini_result else "",
            "tags": gemini_result.get("tags", topic.get("tags", ["주식투자", "StockMaster"])) if gemini_result else topic.get("tags", []),
            "image_path": photo_info.get("image_path", ""),
            "image_url": photo_info.get("web_url", ""),
            "landing_url": self.LANDING_URL
        }

    def publish_now(self, topic_id: Optional[int] = None) -> Dict[str, Any]:
        """제미나이 1회 호출 + 이미지 1회 생성 ➔ 4대 채널(본진, 네이버, 티스토리, 브런치) 동시 배포"""
        logger.info("🎬 [StockBlog] 1회 원고/이미지 생성 ➔ 4대 채널 동시 옴니 배포 시작")
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
