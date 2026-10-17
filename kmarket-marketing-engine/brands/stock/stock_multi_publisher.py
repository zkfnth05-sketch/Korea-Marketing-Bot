# -*- coding: utf-8 -*-
"""
📈 StockMaster Multi Publisher (📈 3대 채널 옴니 블로그 무인 자동 배포 매니저)
===========================================================================
- 역할:
  1. 🟢 [네이버 블로그]: 'title_naver' (스마트블록 1위 최적화 제목) + 자동 발행
  2. 🟠 [티스토리]: 'title_tistory' (구글 SEO 최적화 정보형 제목) + HTML 완전 서식 발행 (영구 프로필 지원)
  3. 🟡 [카카오 브런치]: 'title_brunch' (심층 칼럼형 제목) + 브런치스토리 전용 발행 (영구 프로필 지원)
- 반환: 3대 블로그 플랫폼별 발행 성공 여부 및 URL 리포트
"""

import sys
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger("StockMultiPublisher")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from brands.stock.stock_naver_publisher import StockNaverPublisher
from brands.stock.stock_tistory_publisher import StockTistoryPublisher
from brands.stock.stock_brunch_publisher import StockBrunchPublisher
from brands.stock.stock_supabase_publisher import StockSupabasePublisher


class StockMultiPublisher:
    """StockMaster 4대 채널 옴니 블로그 & 본진 웹앱 동시 배포 컨트롤러 (완전 독립 레고 블록)"""

    def __init__(self):
        self.naver = StockNaverPublisher()
        self.tistory = StockTistoryPublisher()
        self.brunch = StockBrunchPublisher()
        self.supabase = StockSupabasePublisher()

    def publish_all(
        self,
        article_pkg: Dict[str, Any],
        landing_url: str = "https://stockmaster-ai.vercel.app/"
    ) -> Dict[str, Any]:
        """
        3대 블로그 채널 동시 무인 배포 실행:
        1. 네이버 블로그
        2. 티스토리 블로그
        3. 카카오 브런치스토리
        """
        topic_id = article_pkg.get("topic_id", 1)
        title_naver = article_pkg.get("title_naver", article_pkg.get("title", ""))
        title_tistory = article_pkg.get("title_tistory", title_naver)
        title_brunch = article_pkg.get("title_brunch", title_naver)

        body_text = article_pkg.get("content_text", article_pkg.get("body_markdown", ""))
        body_html = article_pkg.get("content_html", f"<p>{body_text}</p>")
        tags = article_pkg.get("tags", ["주식투자", "AI종목분석", "StockMaster"])
        image_paths = [article_pkg["image_path"]] if article_pkg.get("image_path") else []

        logger.info(f"\n" + "=" * 60)
        logger.info(f"🚀 [StockMaster 3대 채널 옴니 배포 가동] 주제 #{topic_id}")
        logger.info(f"  🟢 네이버 제목: {title_naver}")
        logger.info(f"  🟠 티스토리 제목: {title_tistory}")
        logger.info(f"  🟡 브런치 제목: {title_brunch}")
        logger.info("=" * 60)

        results = {
            "topic_id": topic_id,
            "channels": {}
        }

        # 1. 🟢 네이버 블로그
        try:
            logger.info("🚀 [1/3] 🟢 네이버 블로그 발행 시작...")
            res_n = self.naver.publish_article(
                title=title_naver,
                content_text=body_text,
                tag_list=tags,
                image_paths=image_paths,
                landing_url=landing_url
            )
            results["channels"]["naver_blog"] = res_n
            logger.info(f"✅ [1/3] 🟢 네이버 블로그 발행 완료: {res_n.get('url', '')}")
        except Exception as e:
            logger.error(f"❌ [1/3] 🟢 네이버 블로그 실패: {e}")
            results["channels"]["naver_blog"] = {"status": "error", "message": str(e)}

        # 2. 🟠 티스토리 — 최대 3회 재시도
        import time as _time
        res_t = {"status": "error", "message": "재시도 소진"}
        for _attempt in range(1, 4):
            try:
                logger.info(f"🚀 [2/3] 🟠 티스토리 발행 시도 {_attempt}/3...")
                res_t = self.tistory.publish_post(
                    title=title_tistory,
                    content_html=body_html,
                    tag_list=tags,
                    image_paths=image_paths
                )
                t_status = res_t.get("status", "")
                if t_status in ("success", "active", "restored"):
                    logger.info(f"✅ [2/3] 🟠 티스토리 발행 성공 (시도 {_attempt}): {res_t.get('post_url', res_t.get('url', ''))}")
                    break
                elif t_status == "session_expired":
                    logger.warning(f"⚠️ [2/3] 티스토리 세션 만료 (시도 {_attempt}/3), 10초 후 재시도...")
                    _time.sleep(10)
                else:
                    logger.warning(f"⚠️ [2/3] 티스토리 실패 (시도 {_attempt}/3): {res_t.get('message')}, 10초 후 재시도...")
                    _time.sleep(10)
            except Exception as e:
                logger.error(f"❌ [2/3] 티스토리 예외 (시도 {_attempt}/3): {e}")
                res_t = {"status": "error", "message": str(e)}
                _time.sleep(10)
        results["channels"]["tistory"] = res_t


        # 3. 🟡 브런치스토리
        try:
            logger.info("🚀 [3/4] 🟡 브런치스토리 발행 시작...")
            res_b = self.brunch.publish_story(
                title=title_brunch,
                content_text=body_text,
                tag_list=tags,
                landing_url=landing_url
            )
            results["channels"]["brunch"] = res_b
            logger.info(f"✅ [3/4] 🟡 브런치 발행 완료: {res_b.get('post_url', res_b.get('url', ''))}")
        except Exception as e:
            logger.error(f"❌ [3/4] 🟡 브런치 실패: {e}")
            results["channels"]["brunch"] = {"status": "error", "message": str(e)}

        # 4. 📊 본진 웹앱 Supabase [퀀트 리서치] 자동 연동
        try:
            logger.info("🚀 [4/4] 📊 본진 웹앱 Supabase 퀀트 리서치 자동 등록 시작...")
            article_type = article_pkg.get("article_type", "rank1")
            category_code = "SEMICONDUCTOR" if article_type == "semiconductor" else "RANK1"

            # 🎯 [100% 실측 동적 연동] 하드코딩 제거 및 실제 캡처된 종목/코드 자동 매핑
            target_stock = article_pkg.get("target_stock")
            if not target_stock:
                metrics = article_pkg.get("metrics", {})
                if metrics.get("stock_name"):
                    s_code = metrics.get("stock_code", "")
                    s_name = metrics.get("stock_name", "")
                    target_stock = f"{s_code} {s_name}".strip()
                elif "samsung" in metrics and "hynix" in metrics:
                    target_stock = "005930 삼성전자, 000660 SK하이닉스"
                elif article_pkg.get("title"):
                    target_stock = "국내 주도 우량주"
                else:
                    target_stock = "10분 계량 전광판 1위"

            res_s = self.supabase.publish_research(
                category=category_code,
                title=title_naver,
                summary=article_pkg.get("summary", ""),
                target_stock=target_stock,
                quant_data=article_pkg.get("metrics", {}),
                content_markdown=body_text,
                image_path=article_pkg.get("image_path", ""),
                tags=tags
            )
            results["channels"]["supabase_research"] = res_s
            logger.info(f"✅ [4/4] 📊 본진 Supabase 퀀트 리서치 등록 완료! ID: {res_s.get('post_id')}")
        except Exception as e:
            logger.error(f"❌ [4/4] 📊 본진 Supabase 등록 실패: {e}")
            results["channels"]["supabase_research"] = {"status": "error", "message": str(e)}

        # 🔍 [사후 무결성 실사 검증 레고 블록] 실제 공개 블로그 등록 여부 '눈으로 확인'
        try:
            from brands.stock.stock_blog_verifier import StockBlogVerifier
            verifier = StockBlogVerifier()
            v_res = verifier.verify_all(expected_title=title_naver, capture=True)
            results["verification"] = v_res

            # 네이버 실사 검증 반영
            if not v_res.get("naver", {}).get("verified"):
                if results["channels"].get("naver_blog", {}).get("status") == "success":
                    results["channels"]["naver_blog"]["status"] = "error"
                    results["channels"]["naver_blog"]["message"] = f"사후 실사 검증 실패 (RSS/블로그 미등록: {v_res.get('naver', {}).get('error', '제목 불일치')})"
            else:
                real_url = v_res["naver"].get("real_url")
                if real_url:
                    results["channels"]["naver_blog"]["url"] = real_url
                    results["channels"]["naver_blog"]["post_url"] = real_url

            # 티스토리 실사 검증 반영
            if not v_res.get("tistory", {}).get("verified"):
                if results["channels"].get("tistory", {}).get("status") in ("success", "active", "restored"):
                    results["channels"]["tistory"]["status"] = "error"
                    results["channels"]["tistory"]["message"] = f"사후 실사 검증 실패 (티스토리 미등록: {v_res.get('tistory', {}).get('error', '제목 불일치')})"
            else:
                real_t_url = v_res["tistory"].get("real_url")
                if real_t_url:
                    results["channels"]["tistory"]["url"] = real_t_url
                    results["channels"]["tistory"]["post_url"] = real_t_url
        except Exception as ve:
            logger.warning(f"⚠️ [Stock] 사후 실사 검증 예외: {ve}")

        return results
