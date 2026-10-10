# -*- coding: utf-8 -*-
"""
📈 StockMaster 전용 블로그 SEO & 실시간 앱 캡처 엔진 (StockBlogEngine)
========================================================================
- 브랜드: StockMaster AI (주식 AI 분석 & 10분 계량 전광판 & 뇌동매매 방지 VETO)
- 철칙:
  1. 📚 100% 대한민국 국내 증시 100대 주제 풀에서 7대 카테고리 인터리빙 교차 순환
  2. 📸 가짜 AI 사진 생성 전면 배제 ➔ 실제 웹앱(stockmaster-ai.vercel.app)에서 [✨ 변곡점], [🟢 진입유효], [🔴 VETO] 버튼을 직접 클릭한 실시간 전광판 캡처 증거 화면 100% 사용
  3. 🤖 Gemini 3,000자 실전 계량 투자 칼럼 작성 (실제 캡처 데이터 1:1 인용)
  4. 🏷️ 100대 주제 1:1 고유 태그 + 구글/네이버 실시간 급상승 트렌드 15개 해시태그 결합
  5. 🌐 3대 블로그(네이버, 티스토리, 브런치) 동시/순차 무인 자동 배포
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

# UTF-8 콘솔 출력 지원
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("StockBlogEngine")

from brands.stock.stock_100_topics import (
    STOCK_100_TOPICS,
    get_all_topics,
    get_topic_by_id,
    get_topics_by_category,
    get_interleaved_topic_order
)
from brands.stock.stock_keyword_matrix import StockKeywordMatrix
from brands.stock.stock_hashtag_matrix import StockHashtagMatrix


class StockBlogEngine:
    """
    📈 100% 국내 주식 100대 주제 + 실제 앱 실시간 버튼 클릭 캡처 블로그 엔진
    """
    BRAND = "stock"
    NAME = "StockMaster Blog Engine"
    LANDING_URL = "https://stockmaster-ai.vercel.app/"

    def __init__(self):
        self.keyword_matrix = StockKeywordMatrix()
        self.topics = STOCK_100_TOPICS
        self.rotation_index = 0
        self._writer = None
        self._capturer = None
        self._publisher = None

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

    def _get_publisher(self):
        if self._publisher is None:
            from brands.stock.stock_multi_publisher import StockMultiPublisher
            self._publisher = StockMultiPublisher()
        return self._publisher

    def get_next_topic(self) -> Dict[str, Any]:
        """7대 카테고리 교차 순환(인터리빙) 방식으로 1개씩 순환 반환 (특정 분야 쏠림 100% 차단)"""
        state_file = PROJECT_ROOT / "data" / "stock_blog_rotation_state.json"
        state = {}
        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
            except Exception:
                state = {}

        interleaved_order = get_interleaved_topic_order()
        idx = state.get("current_topic_index", 0)
        target_id = interleaved_order[idx % len(interleaved_order)]
        topic = get_topic_by_id(target_id)

        state["current_topic_index"] = (idx + 1) % len(interleaved_order)
        state["last_topic_id"] = topic["id"]
        state["last_title"] = topic["title"]
        try:
            state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"상태 저장 실패: {e}")

        return topic

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
            if not l:
                cleaned.append("")
                continue
            cleaned.append(l)

        res = "\n".join(cleaned)
        res = re.sub(r'\n{3,}', '\n\n', res).strip()
        return res

    @staticmethod
    def render_clean_html_body(clean_md: str, landing_url: str, image_path: Optional[str] = None) -> str:
        """티스토리/웹 전용 고품질 여백 및 비주얼 박스 카드 HTML 렌더링 (실제 앱 캡처 이미지 상단 직결)"""
        import re
        import base64

        img_html = ""
        if image_path and Path(image_path).exists():
            try:
                with open(image_path, "rb") as img_f:
                    b64_str = base64.b64encode(img_f.read()).decode("utf-8")
                img_html = f"""
<div style="text-align: center; margin: 24px 0 32px 0;">
  <img src="data:image/png;base64,{b64_str}" alt="StockMaster AI 실시간 퀀트 전광판" style="max-width: 100%; height: auto; border-radius: 10px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.15), 0 4px 6px -2px rgba(0,0,0,0.05); border: 1px solid #cbd5e1;" />
  <p style="color: #64748b; font-size: 13px; margin-top: 10px; font-weight: 500;">▲ StockMaster AI 실시간 10분 계량 전광판 및 수급 레이더 캡처 화면</p>
</div>
"""
            except Exception as e:
                logger.warning(f"이미지 HTML 변환 통과: {e}")

        blocks = clean_md.split("\n\n")
        html_parts = [img_html] if img_html else []

        for block in blocks:
            b = block.strip()
            if not b:
                continue

            if b.startswith(">"):
                b_lines = [line.lstrip(">").strip() for line in b.split("\n")]
                inner_text = "<br/>".join([l for l in b_lines if l])
                inner_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', inner_text)
                card_html = f"""<blockquote style="margin: 26px 0; padding: 18px 22px; background-color: #0f172a; border-left: 4px solid #10b981; border-radius: 8px; font-size: 15px; color: #f8fafc; line-height: 1.8;">{inner_text}</blockquote>"""
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

        cta_html = f"""
<div style="margin-top: 36px; padding: 22px; background-color: #0f172a; border-left: 5px solid #10b981; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
  <p style="font-weight: bold; font-size: 17px; margin: 0 0 8px 0; color: #ffffff;">📈 내 보유 종목 실시간 퀀트 점수 확인하기</p>
  <p style="font-size: 14px; color: #94a3b8; margin: 0 0 16px 0; line-height: 1.6;">10분마다 350개 주도주 체결강도 스캔 & -5% 실시간 손절 알림 (100% 무료)</p>
  <p style="margin: 0;"><a href="{landing_url}" target="_blank" style="display: inline-block; padding: 12px 24px; background-color: #10b981; color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 15px;">StockMaster AI 실시간 전광판 바로가기 👉</a></p>
</div>
"""
        return "".join(html_parts) + cta_html

    def build_article_package(
        self,
        topic_id: Optional[int] = None,
        use_gemini: bool = True,
        force_recapture: bool = True
    ) -> Dict[str, Any]:
        """
        주제 선택 ➔ 실제 앱 버튼 클릭 고화질 캡처 ➔ 실시간 캡처 데이터 주입 Gemini 3,000자 칼럼 ➔ 15개 해시태그 결합
        """
        # 1. 주제 선택
        if topic_id is not None:
            topic = get_topic_by_id(topic_id)
        else:
            topic = self.get_next_topic()

        cat_key = topic["category"]
        seed_topic = topic["title"]
        app_action_mode = topic.get("app_action_mode", "rank1")

        logger.info(f"🚀 [StockBlog] 주제 #{topic['id']} 패키지 빌드 시작: '{seed_topic}' (액션 모드: {app_action_mode})")

        # 2. 📸 [핵심] 실제 StockMaster AI 웹앱에서 버튼 직접 클릭하여 실시간 전광판 캡처!
        capturer = self._get_capturer()
        capture_result = capturer.capture_dashboard(mode=app_action_mode)
        image_path = capture_result.get("image_path", "")
        metrics = capture_result.get("metrics", {})

        logger.info(f"📸 [StockBlog] 실제 앱 버튼 클릭 캡처 완료: {Path(image_path).name if image_path else '없음'}")
        logger.info(f"📊 [StockBlog] 실시간 1위 종목 파싱: {metrics.get('stock_name')} ({metrics.get('chegyul_strength')}, 손절:{metrics.get('exit_sl')}, 목표:{metrics.get('swing_tp')})")

        # 3. 🤖 Gemini 실시간 본문 작성 (100대 주제 고유 3,000자 칼럼 집필)
        seo_brief = self.keyword_matrix.build_seo_article_brief(
            seed_topic=seed_topic,
            category=cat_key
        )
        gemini_result = None
        writer = self._get_writer()
        if use_gemini:
            try:
                # 100대 주제별 고유 퀀트 칼럼 작성 (중복 재탕 원천 차단)
                gemini_result = writer.write_magazine_article(topic, seo_brief)
                logger.info(f"✅ [StockBlog] Gemini 3,000자 실전 칼럼 작성 완료: '{gemini_result.get('title_naver', seed_topic)}'")
            except Exception as e:
                logger.warning(f"⚠️ [StockBlog] Gemini 100대 주제 원고 작성 예외: {e}")

        # 🚨 [절대 무결성 게이트: 껍데기/더미 글 100% 차단 및 완성형 원고 강제 보장]
        if not gemini_result or not gemini_result.get("body_markdown") or len(gemini_result.get("body_markdown", "").strip()) < 1500 or "내용 준비 중" in gemini_result.get("body_markdown", ""):
            logger.warning("🛡️ [StockBlog 무결성 게이트] 고품질 3,000자 완성형 퀀트 칼럼으로 안전 복원합니다.")
            gemini_result = writer._generate_fallback(topic, seo_brief)

        # 4. 본문 조립 및 마크다운/HTML 정제
        title_naver = gemini_result.get("title_naver", seed_topic)
        title_tistory = gemini_result.get("title_tistory", title_naver)
        title_brunch = gemini_result.get("title_brunch", title_naver)
        main_title = title_naver

        raw_body_md = gemini_result.get("body_markdown", "")
        clean_body_md = self.clean_markdown_body(raw_body_md)
        full_html = self.render_clean_html_body(clean_body_md, self.LANDING_URL, image_path=image_path)

        # 5. 🏷️ 100대 주제 1:1 고유 태그 + 구글/네이버 실시간 급상승 15개 해시태그 결합
        live_tags = StockHashtagMatrix.get_rich_viral_hashtags(topic_id=topic["id"], count=15)
        clean_tags = [t.replace("#", "").strip() for t in live_tags]

        return {
            "topic_id": topic["id"],
            "title": main_title,
            "title_naver": title_naver,
            "title_tistory": title_tistory,
            "title_brunch": title_brunch,
            "category": cat_key,
            "app_action_mode": app_action_mode,
            "body_markdown": clean_body_md,
            "content_text": clean_body_md,
            "content_html": full_html,
            "summary": gemini_result.get("summary", "") if gemini_result else "",
            "tags": clean_tags,
            "image_path": image_path,
            "image_url": image_path,
            "metrics": metrics,
            "landing_url": self.LANDING_URL
        }

    def publish_now(self, topic_id: Optional[int] = None) -> Dict[str, Any]:
        """실제 앱 캡처 ➔ 4대 채널(네이버, 티스토리, 브런치 등) 동시 배포"""
        logger.info("🎬 [StockBlog] 실제 앱 캡처 결합 ➔ 3대 채널 옴니 배포 가동")
        pkg = self.build_article_package(topic_id=topic_id)
        publisher = self._get_publisher()
        pub_results = publisher.publish_all(pkg, landing_url=self.LANDING_URL)

        return {
            "status": "success",
            "article_title": pkg["title"],
            "topic_id": pkg["topic_id"],
            "image_used": pkg["image_path"],
            "publishing_results": pub_results
        }


if __name__ == "__main__":
    engine = StockBlogEngine()
    print("🚀 [StockBlogEngine] #046 (변곡점 탭 연동 주제) 패키지 빌드 테스트 시작...")
    pkg = engine.build_article_package(topic_id=46)
    print("\n=========================================")
    print(f"📌 주제 ID: {pkg['topic_id']}")
    print(f"📌 네이버 제목: {pkg['title_naver']}")
    print(f"📌 티스토리 제목: {pkg['title_tistory']}")
    print(f"📌 사용된 실제 앱 캡처 이미지: {pkg['image_path']}")
    print(f"📌 캡처된 1위 종목: {pkg['metrics'].get('stock_name')} ({pkg['metrics'].get('current_price')})")
    print(f"📌 해시태그 ({len(pkg['tags'])}개): {' '.join(['#' + t for t in pkg['tags']])}")
    print(f"📌 본문 길이: {len(pkg['body_markdown'])}자")
    print("=========================================\n")
