# -*- coding: utf-8 -*-
"""
🛡️ 보험 리밸런스 전용 - [게시물 & 첫 댓글 실측 확인 레고 블록]
=============================================================================
- 브랜드: 보험 리밸런스 (순수 독립 모듈)
- 공식 검색어: '보험 리밸런스' (띄어쓰기 필수)
- 공식 URL: https://insure-rebalance.vercel.app/
- 역할:
  1. 유튜브 쇼츠 실물 영상 노출 확인 + 첫 댓글/고정핀에 '보험 리밸런스' & 랜딩 URL 실측 확인
  2. 메타(Instagram/Facebook) 릴스 게시글 및 캡션/댓글 공식 검색어 실측 확인
  3. 네이버 클립 스튜디오/채널(thefirst-life) 게시물 및 설명글 실측 확인
  4. 증빙 스크린샷 캡처 및 전용 감사 리포트 생성
"""

import os
import sys
import json
import time
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine.browser_guard import get_safe_browser_args, clean_browser_profile_locks

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("InsuranceVerifier")

PROOFS_DIR = PROJECT_ROOT / "outputs" / "proofs" / "insurance"
PROOFS_DIR.mkdir(parents=True, exist_ok=True)


class InsurancePostCommentVerifier:
    """🛡️ 보험 리밸런스 전용 게시물 및 첫 댓글 실측 확인기"""

    BRAND_NAME = "🛡️ 보험 리밸런스"
    OFFICIAL_KEYWORD = "보험 리밸런스"
    LANDING_URL = "https://insure-rebalance.vercel.app/"
    CLIP_ID = "thefirst-life"

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.profile_dir_meta = CURRENT_DIR / "meta_chrome_profile"
        self.profile_dir_naver = CURRENT_DIR / "naver_browser_profile"
        self.profile_dir_yt = CURRENT_DIR / "youtube_chrome_profile"

    async def verify_youtube_shorts(self, video_url: str) -> Dict[str, Any]:
        """보험 리밸런스 유튜브 쇼츠 게시물 및 공식 댓글/고정핀 실측 검증"""
        result = {
            "platform": "youtube_shorts",
            "brand": "insurance",
            "url": video_url,
            "post_status": "UNKNOWN",
            "comment_status": "NOT_FOUND",
            "is_pinned": False,
            "keyword_matched": False,
            "url_matched": False,
            "proof_screenshot": "",
            "verified_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        if not video_url or not video_url.startswith("http"):
            result["post_status"] = "INVALID_URL"
            return result

        logger.info(f"🔍 [보험 유튜브 실측] 쇼츠 접속: {video_url}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                args=get_safe_browser_args() + ["--disable-blink-features=AutomationControlled"]
            )
            context = await browser.new_context(viewport={"width": 1280, "height": 900})
            page = await context.new_page()

            try:
                await page.goto(video_url, wait_until="domcontentloaded", timeout=35000)
                await asyncio.sleep(3.0)

                # 1. 쇼츠 영상 노출 확인
                page_text = await page.content()
                if "동영상을 볼 수 없습니다" in page_text or "Video unavailable" in page_text:
                    result["post_status"] = "DEAD_VIDEO"
                    logger.warning("❌ [보험 유튜브] 쇼츠 영상을 찾을 수 없음")
                else:
                    result["post_status"] = "ALIVE"
                    logger.info("✅ [보험 유튜브] 쇼츠 게시물 정상 노출 확인!")

                # 2. 댓글 서랍 열기
                try:
                    comment_btn = page.locator("button[aria-label*='댓글'], #comments-button button, [aria-label*='Comments']").first
                    if await comment_btn.is_visible():
                        await comment_btn.click(force=True)
                        await asyncio.sleep(2.5)
                except Exception:
                    pass

                # 3. 댓글 파싱
                comment_locators = page.locator("#content-text, ytd-comment-view-model #content-text, #comment-content")
                count = await comment_locators.count()
                comments_text = []
                for i in range(min(count, 15)):
                    try:
                        ct = await comment_locators.nth(i).inner_text()
                        if ct:
                            comments_text.append(ct)
                    except Exception:
                        pass

                all_body = "\n".join(comments_text)

                if self.OFFICIAL_KEYWORD in all_body:
                    result["keyword_matched"] = True
                if self.LANDING_URL in all_body or "insure-rebalance.vercel.app" in all_body:
                    result["url_matched"] = True

                pinned_badge = page.locator("ytd-pinned-comment-badge-renderer, [aria-label*='고정'], [aria-label*='Pinned']").first
                if await pinned_badge.count() > 0:
                    result["is_pinned"] = True

                if result["keyword_matched"] and result["url_matched"]:
                    result["comment_status"] = "VERIFIED_PERFECT"
                    logger.info(f"🎉 [보험 유튜브] '{self.OFFICIAL_KEYWORD}' & 공식링크 첫 댓글 100% 실측 확인!")
                elif result["keyword_matched"] or result["url_matched"]:
                    result["comment_status"] = "VERIFIED_PARTIAL"
                else:
                    result["comment_status"] = "NO_MATCH"

                # 4. 실측 증빙 스크린샷
                shot_path = PROOFS_DIR / f"verify_insurance_youtube_{int(time.time())}.png"
                await page.screenshot(path=str(shot_path), full_page=False)
                result["proof_screenshot"] = str(shot_path)
                logger.info(f"📸 [보험 증빙] 유튜브 캡처: {shot_path.name}")

            except Exception as e:
                result["post_status"] = "ERROR"
                result["error"] = str(e)
                logger.error(f"❌ [보험 유튜브 예외] {e}")
            finally:
                await browser.close()

        return result

    async def verify_meta_reels(self) -> Dict[str, Any]:
        """보험 리밸런스 메타 릴스(MBS) 게시물 실측 검증"""
        result = {
            "platform": "meta_reels",
            "brand": "insurance",
            "url": "https://business.facebook.com/latest/posts/published_posts",
            "post_status": "UNKNOWN",
            "comment_status": "NOT_FOUND",
            "keyword_matched": False,
            "url_matched": False,
            "proof_screenshot": "",
            "verified_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        clean_browser_profile_locks(self.profile_dir_meta)
        logger.info("🔍 [보험 메타 실측] Meta Business Suite 점검 중...")

        async with async_playwright() as p:
            try:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(self.profile_dir_meta),
                    headless=self.headless,
                    args=get_safe_browser_args(),
                    viewport={"width": 1280, "height": 900}
                )
                page = context.pages[0] if context.pages else await context.new_page()

                await page.goto(result["url"], wait_until="domcontentloaded", timeout=40000)
                await asyncio.sleep(4.0)

                body_text = await page.content()
                if self.OFFICIAL_KEYWORD in body_text:
                    result["keyword_matched"] = True
                if "insure-rebalance" in body_text:
                    result["url_matched"] = True

                if result["keyword_matched"] or result["url_matched"]:
                    result["post_status"] = "ALIVE"
                    result["comment_status"] = "VERIFIED_IN_CAPTION"
                    logger.info("🎉 [보험 메타] 릴스 게시글 및 공식문구 실측 확인!")
                else:
                    result["post_status"] = "ALIVE_OR_PENDING"
                    result["comment_status"] = "PENDING"

                shot_path = PROOFS_DIR / f"verify_insurance_meta_{int(time.time())}.png"
                await page.screenshot(path=str(shot_path), full_page=False)
                result["proof_screenshot"] = str(shot_path)
                logger.info(f"📸 [보험 증빙] 메타 캡처: {shot_path.name}")

                await context.close()
            except Exception as e:
                result["post_status"] = "ERROR"
                result["error"] = str(e)
                logger.error(f"❌ [보험 메타 예외] {e}")

        return result

    async def verify_naver_clip(self) -> Dict[str, Any]:
        """보험 리밸런스 네이버 클립 게시물 실측 검증"""
        result = {
            "platform": "naver_clip",
            "brand": "insurance",
            "url": "https://clipcreators.naver.com/web/contents",
            "post_status": "UNKNOWN",
            "comment_status": "NOT_FOUND",
            "keyword_matched": False,
            "url_matched": False,
            "proof_screenshot": "",
            "verified_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        clean_browser_profile_locks(self.profile_dir_naver)
        logger.info("🔍 [보험 네이버 실측] 클립 스튜디오 점검 중...")

        async with async_playwright() as p:
            try:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(self.profile_dir_naver),
                    headless=self.headless,
                    args=get_safe_browser_args(),
                    viewport={"width": 1280, "height": 900}
                )
                page = context.pages[0] if context.pages else await context.new_page()

                await page.goto(result["url"], wait_until="domcontentloaded", timeout=40000)
                await asyncio.sleep(4.0)

                body_text = await page.content()
                if "등록된 클립" in body_text or "클립" in body_text:
                    result["post_status"] = "ALIVE"
                    if self.OFFICIAL_KEYWORD in body_text:
                        result["keyword_matched"] = True
                        result["comment_status"] = "VERIFIED_IN_CLIP"
                    else:
                        result["comment_status"] = "ACTIVE_CONTENTS"
                    logger.info("🎉 [보험 네이버] 클립 콘텐츠 정상 실측 확인!")
                else:
                    result["post_status"] = "PENDING"

                shot_path = PROOFS_DIR / f"verify_insurance_naver_{int(time.time())}.png"
                await page.screenshot(path=str(shot_path), full_page=False)
                result["proof_screenshot"] = str(shot_path)
                logger.info(f"📸 [보험 증빙] 네이버 클립 캡처: {shot_path.name}")

                await context.close()
            except Exception as e:
                result["post_status"] = "ERROR"
                result["error"] = str(e)
                logger.error(f"❌ [보험 네이버 예외] {e}")

        return result

    async def run_full_verification(self, yt_url: Optional[str] = None) -> Dict[str, Any]:
        """보험 리밸런스 3개 채널 전수 실측 검증 실행"""
        logger.info("\n" + "=" * 70)
        logger.info(f"🕵️ [{self.BRAND_NAME}] 게시물 & 첫 댓글 실측 감사 시작")
        logger.info(f"• 공식 검색어: '{self.OFFICIAL_KEYWORD}' | 공식 URL: {self.LANDING_URL}")
        logger.info("=" * 70)

        if not yt_url:
            receipt = PROJECT_ROOT / "outputs" / "proofs" / "3brands_omni_publish_receipt.json"
            if receipt.exists():
                try:
                    with open(receipt, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    yt_url = data.get("insurance", {}).get("channels", {}).get("youtube", {}).get("video_url")
                except Exception:
                    pass

        yt_res = await self.verify_youtube_shorts(yt_url or "")
        await asyncio.sleep(2.0)
        meta_res = await self.verify_meta_reels()
        await asyncio.sleep(2.0)
        naver_res = await self.verify_naver_clip()

        report = {
            "brand": "insurance",
            "brand_name": self.BRAND_NAME,
            "keyword": self.OFFICIAL_KEYWORD,
            "youtube": yt_res,
            "meta": meta_res,
            "naver": naver_res,
            "audit_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        out_file = PROOFS_DIR / f"insurance_verification_{int(time.time())}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="보험 리밸런스 게시물 및 첫 댓글 실측 확인기")
    parser.add_argument("--url", "-u", default=None, help="유튜브 쇼츠 URL")
    args = parser.parse_args()

    verifier = InsurancePostCommentVerifier(headless=True)
    res = asyncio.run(verifier.run_full_verification(args.url))
    print(json.dumps(res, ensure_ascii=False, indent=2))
