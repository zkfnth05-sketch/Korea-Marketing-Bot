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
    LANDING_URL = "https://stockmaster-ai.vercel.app/"

    def __init__(self):
        self.keyword_matrix = StockKeywordMatrix()
        self.topics = STOCK_100_TOPICS
        self.rotation_index = 0
        self._writer = None
        self._image_gen = None
        self._publisher = None
        self._capturer = None

    def _get_capturer(self):
        if self._capturer is None:
            from brands.stock.stock_dashboard_capturer import StockDashboardCapturer
            self._capturer = StockDashboardCapturer()
        return self._capturer

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
        generate_photo: bool = True,
        use_live_trend: bool = True
    ) -> Dict[str, Any]:
        """
        🔥 [3박자 퀀트 결합] 당일 실시간 핫 우량주 트렌드 + 100대 주제 ➔ Gemini 2,000자 칼럼 ➔ 맞춤 사진 1장 생성
        """
        # 1. 주제 선택
        if topic_id is not None:
            topic = get_topic_by_id(topic_id)
        else:
            topic = self.get_next_topic()

        cat_key = topic["category"]
        seed_topic = topic["title"]
        app_feature = topic.get("app_feature", "StockMaster AI 10분 계량 전광판")

        # 2. 실시간 증시 수급 트렌드 또는 고검색량 키워드 추출
        if use_live_trend:
            seo_brief = self.keyword_matrix.build_live_trend_brief()
            logger.info(f"🔥 [StockBlog] 실시간 핫 종목 매트릭스 결합: {seo_brief.get('live_stock', {}).get('name', '우량주')}")
        else:
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
                logger.info(f"✅ [StockBlog] Gemini 2,000자 칼럼 작성 완료: '{gemini_result.get('title_naver', gemini_result.get('title'))}'")
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
  <p style="font-weight: bold; font-size: 16px; margin-bottom: 8px; color: #10b981;">📈 뇌동매매 끝! 10분마다 350개 주도주를 스캔하는 AI 퀀트 시스템</p>
  <p style="font-size: 14px; color: #a1a1aa; margin-bottom: 12px;">외국인·기관 수급, 체결강도, 블록오더, 그리고 -5% 실시간 문자 손절 알림을 100% 무료로 확인하세요.</p>
  <a href="{self.LANDING_URL}" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #10b981; color: #000000; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 14px;">StockMaster AI 10분 전광판 바로가기 👉</a>
</div>

<!-- 🌟 티스토리/웹 공식 규격 10분 350개 주도주 오픈그래프 카드 -->
<figure data-ke-type="opengraph" data-ke-align="alignCenter" data-og-type="website" data-og-title="Stock Master AI - 10분 퀀트 스캔 &amp; 실시간 -5% 손절 알림" data-og-description="10분마다 국내 350개 주도주를 스캔하는 AI 퀀트 시스템. 체결강도, 블록오더, 수급 분석을 무료로 경험하세요." data-og-host="stockmaster-ai.vercel.app" data-og-source-url="https://stockmaster-ai.vercel.app/" data-og-url="https://stockmaster-ai.vercel.app/" data-og-image="https://stockmaster-ai.vercel.app/og-image.png" style="margin: 20px 0; border: 1px solid #27272a; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 14px rgba(0,0,0,0.25); text-align: left;">
  <a href="{self.LANDING_URL}" target="_blank" rel="noopener" style="text-decoration: none; display: flex; align-items: center; background: #18181b; color: inherit;">
    <div class="og-image" style="width: 140px; height: 100px; flex-shrink: 0; background: url('https://stockmaster-ai.vercel.app/og-image.png') no-repeat center center / cover; border-right: 1px solid #27272a;"></div>
    <div class="og-text" style="padding: 14px 18px; flex-grow: 1;">
      <p class="og-title" style="margin: 0 0 6px 0; font-size: 15px; font-weight: bold; color: #ffffff; line-height: 1.4;">Stock Master AI - 10분 퀀트 스캔 &amp; 실시간 -5% 손절 알림</p>
      <p class="og-desc" style="margin: 0 0 6px 0; font-size: 12.5px; color: #a1a1aa; line-height: 1.5;">10분마다 350개 국내 주도주를 스캔하는 실시간 AI 퀀트 전광판</p>
      <p class="og-host" style="margin: 0; font-size: 11.5px; color: #10b981; font-weight: 600;">stockmaster-ai.vercel.app</p>
    </div>
  </a>
</figure>
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

    def build_captured_article_package(self, article_type: str = "rank1") -> Dict[str, Any]:
        """
        주식 웹앱 실시간 화면(1600x1600 고화질) 캡처 + 대표님 성공 바이블 기반 2,000자 칼럼 패키지 생성
        article_type: 'rank1' (전광판 1위 주도주 편) 또는 'semiconductor' (반도체 주도주 편)
        """
        logger.info(f"🚀 [StockBlog] 실시간 캡처 기반 패키지 생성 시작 (유형: {article_type})")

        # 1. 실시간 주식 앱 캡처 및 메트릭스 추출
        capturer = self._get_capturer()
        capture_res = capturer.capture_dashboard(mode=article_type)
        image_path = capture_res.get("image_path", "")
        metrics = capture_res.get("metrics", {})

        # 2. Gemini 황금 바이블 칼럼 생성
        writer = self._get_writer()
        article = writer.write_captured_article(capture_res, article_type=article_type)

        title_naver = article.get("title_naver", article.get("title", ""))
        title_tistory = article.get("title_tistory", title_naver)
        title_brunch = article.get("title_brunch", title_naver)
        body_md = article.get("body_markdown", "")
        body_html = markdown.markdown(body_md)

        # 3. 고품격 CTA 카드 바인딩
        cta_html = f"""
<div style="margin-top: 30px; padding: 20px; background-color: #09090b; border-left: 4px solid #10b981; border-radius: 8px; color: #ffffff;">
  <p style="font-weight: bold; font-size: 16px; margin-bottom: 8px; color: #10b981;">📈 뇌동매매 끝! 10분마다 350개 주도주를 스캔하는 AI 퀀트 시스템</p>
  <p style="font-size: 14px; color: #a1a1aa; margin-bottom: 12px;">실시간 계량 전광판, 체결강도, 블록오더, 그리고 -5% 실시간 문자 손절 알림을 100% 무료로 경험해보세요.</p>
  <a href="{self.LANDING_URL}" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #10b981; color: #000000; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 14px;">StockMaster AI 실시간 전광판 바로가기 👉</a>
</div>

<!-- 🌟 티스토리/웹 공식 규격 10분 350개 주도주 오픈그래프 카드 -->
<figure data-ke-type="opengraph" data-ke-align="alignCenter" data-og-type="website" data-og-title="Stock Master AI - 10분 퀀트 스캔 &amp; 실시간 -5% 손절 알림" data-og-description="10분마다 국내 350개 주도주를 스캔하는 AI 퀀트 시스템. 체결강도, 블록오더, 수급 분석을 무료로 경험하세요." data-og-host="stockmaster-ai.vercel.app" data-og-source-url="https://stockmaster-ai.vercel.app/" data-og-url="https://stockmaster-ai.vercel.app/" data-og-image="https://stockmaster-ai.vercel.app/og-image.png" style="margin: 20px 0; border: 1px solid #27272a; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 14px rgba(0,0,0,0.25); text-align: left;">
  <a href="{self.LANDING_URL}" target="_blank" rel="noopener" style="text-decoration: none; display: flex; align-items: center; background: #18181b; color: inherit;">
    <div class="og-image" style="width: 140px; height: 100px; flex-shrink: 0; background: url('https://stockmaster-ai.vercel.app/og-image.png') no-repeat center center / cover; border-right: 1px solid #27272a;"></div>
    <div class="og-text" style="padding: 14px 18px; flex-grow: 1;">
      <p class="og-title" style="margin: 0 0 6px 0; font-size: 15px; font-weight: bold; color: #ffffff; line-height: 1.4;">Stock Master AI - 10분 퀀트 스캔 &amp; 실시간 -5% 손절 알림</p>
      <p class="og-desc" style="margin: 0 0 6px 0; font-size: 12.5px; color: #a1a1aa; line-height: 1.5;">10분마다 350개 국내 주도주를 스캔하는 실시간 AI 퀀트 전광판</p>
      <p class="og-host" style="margin: 0; font-size: 11.5px; color: #10b981; font-weight: 600;">stockmaster-ai.vercel.app</p>
    </div>
  </a>
</figure>
"""
        full_html = body_html + cta_html

        return {
            "topic_id": 999 if article_type == "rank1" else 998,
            "title": title_naver,
            "title_naver": title_naver,
            "title_tistory": title_tistory,
            "title_brunch": title_brunch,
            "category": "live_quant" if article_type == "rank1" else "semiconductor",
            "body_markdown": body_md,
            "content_text": body_md,
            "content_html": full_html,
            "summary": article.get("summary", ""),
            "tags": article.get("tags", ["주식투자", "체결강도", "블록오더", "스톡마스터AI"]),
            "image_path": image_path,
            "image_url": "",
            "metrics": metrics,
            "article_type": article_type,
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
