# -*- coding: utf-8 -*-
"""
🛡️ InsureBalance Multi Publisher (3대 블로그 플랫폼 동시 발행 오케스트레이터)
============================================================================
- 역할: Naver, Tistory, Brunch 3개 플랫폼에 최적화된 형태로 동시/순차 발행
- 반환: 각 플랫폼별 발행 성공 여부 및 URL 리포트
"""

import sys
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger("InsuranceMultiPublisher")

from brands.insurance.insurance_naver_publisher import InsuranceNaverPublisher
from brands.insurance.insurance_tistory_publisher import InsuranceTistoryPublisher
from brands.insurance.insurance_brunch_publisher import InsuranceBrunchPublisher


class InsuranceMultiPublisher:
    """InsureBalance 3대 블로그 동시 발행 컨트롤러"""

    def __init__(self):
        self.naver = InsuranceNaverPublisher()
        self.tistory = InsuranceTistoryPublisher()
        self.brunch = InsuranceBrunchPublisher()

    def publish_all(
        self,
        article_pkg: Dict[str, Any],
        landing_url: str = "https://insurebalance.co.kr"
    ) -> Dict[str, Any]:
        """
        네이버, 티스토리, 브런치에 각 플랫폼별 최적화 제목 및 본문으로 발행
        """
        title_naver = article_pkg.get("title_naver", article_pkg.get("title", ""))
        title_tistory = article_pkg.get("title_tistory", title_naver)
        title_brunch = article_pkg.get("title_brunch", title_naver)

        body_text = article_pkg.get("content_text", article_pkg.get("body_markdown", ""))
        body_html = article_pkg.get("content_html", f"<p>{body_text}</p>")
        tags = article_pkg.get("tags", ["보험비교", "보험리모델링", "InsureBalance"])
        image_paths = [article_pkg["image_path"]] if article_pkg.get("image_path") else []

        results = {}

        # 1. 네이버 블로그
        try:
            logger.info("🚀 [MultiPub-Insurance] 네이버 블로그 발행 시작...")
            res_n = self.naver.publish_article(
                title=title_naver,
                content_text=body_text,
                tag_list=tags,
                image_paths=image_paths,
                landing_url=landing_url
            )
            results["naver"] = res_n
        except Exception as e:
            logger.error(f"❌ [MultiPub-Insurance] 네이버 실패: {e}")
            results["naver"] = {"status": "error", "message": str(e)}

        # 2. 티스토리
        try:
            logger.info("🚀 [MultiPub-Insurance] 티스토리 블로그 발행 시작...")
            res_t = self.tistory.publish_post(
                title=title_tistory,
                content_html=body_html,
                tag_list=tags
            )
            results["tistory"] = res_t
        except Exception as e:
            logger.error(f"❌ [MultiPub-Insurance] 티스토리 실패: {e}")
            results["tistory"] = {"status": "error", "message": str(e)}

        # 3. 브런치스토리
        try:
            logger.info("🚀 [MultiPub-Insurance] 브런치스토리 발행 시작...")
            res_b = self.brunch.publish_story(
                title=title_brunch,
                content_text=body_text,
                tag_list=tags
            )
            results["brunch"] = res_b
        except Exception as e:
            logger.error(f"❌ [MultiPub-Insurance] 브런치 실패: {e}")
            results["brunch"] = {"status": "error", "message": str(e)}

        return results
