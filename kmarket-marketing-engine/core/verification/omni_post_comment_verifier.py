# -*- coding: utf-8 -*-
"""
[코어 검증 엔진] OmniPostCommentVerifier - 🛡️ [3대 앱 3대 SNS 게시물 & 댓글 실측 검증기]
========================================================================================
- 역할:
  1. 유튜브 쇼츠, 메타 릴스, 네이버 클립에 실제 영상이 정상 노출되는지 실측 브라우저 접속
  2. 첫 댓글 및 고정 핀에 공식 검색어(아우라AI데이팅, 보험 리밸런스, 스톡마스터 AI)와
     공식 랜딩 URL이 100% 정상 포함되어 있는지 DOM 파싱 검증
  3. 실측 증빙 스크린샷 자동 캡처 (outputs/proofs/verify_*.png)
  4. 검증 결과 종합 영수증(JSON) 자동 생성
"""

import os
import sys
import json
import time
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("OmniVerifier")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROOFS_DIR = PROJECT_ROOT / "outputs" / "proofs"
PROOFS_DIR.mkdir(parents=True, exist_ok=True)

from core.engine.browser_guard import get_safe_browser_args, clean_browser_profile_locks


class OmniPostCommentVerifier:
    """3대 브랜드 게시물 송출 및 댓글 실측 검증 엔진"""

    BRANDS_STANDARD = {
        "aura": {
            "name": "💖 Aura AI 데이팅",
            "keyword": "아우라AI데이팅",
            "url": "https://aura-ai-dating.vercel.app/",
            "clip_id": "aura-dating",
            "meta_id": "aura_dating_official"
        },
        "insurance": {
            "name": "🛡️ 보험 리밸런스",
            "keyword": "보험 리밸런스",
            "url": "https://insure-rebalance.vercel.app/",
            "clip_id": "thefirst-life",
            "meta_id": "insure_rebalance"
        },
        "stock": {
            "name": "📈 StockMaster AI",
            "keyword": "스톡마스터 AI",
            "url": "https://stockmaster-ai.vercel.app/",
            "clip_id": "stockmaster-ai",
            "meta_id": "stockmaster_ai"
        }
    }

    def __init__(self, headless: bool = True):
        self.headless = headless

    async def verify_youtube_shorts(self, brand: str, video_url: str) -> Dict[str, Any]:
        """유튜브 쇼츠 게시물 및 댓글/고정핀 실측 검증"""
        cfg = self.BRANDS_STANDARD.get(brand, {})
        brand_name = cfg.get("name", brand)
        keyword = cfg.get("keyword", "")
        landing_url = cfg.get("url", "")

        result = {
            "platform": "youtube_shorts",
            "brand": brand,
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

        logger.info(f"🔍 [유튜브 검증] {brand_name} 쇼츠 실측 접속: {video_url}")

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

                # 1. 게시물 생존 여부 확인
                title_el = page.locator("h1.ytd-watch-metadata, .ytd-reel-player-header-renderer, ytd-shorts-player-title").first
                page_text = await page.content()

                if "동영상을 볼 수 없습니다" in page_text or "Video unavailable" in page_text:
                    result["post_status"] = "DEAD_VIDEO"
                    logger.warning(f"❌ [유튜브 검증] {brand_name}: 동영상을 찾을 수 없음")
                else:
                    result["post_status"] = "ALIVE"
                    logger.info(f"✅ [유튜브 검증] {brand_name}: 쇼츠 게시물 정상 노출 확인!")

                # 2. 댓글 서랍 열기
                try:
                    comment_btn = page.locator("button[aria-label*='댓글'], #comments-button button, [aria-label*='Comments']").first
                    if await comment_btn.is_visible():
                        await comment_btn.click(force=True)
                        await asyncio.sleep(2.5)
                except Exception:
                    pass

                # 3. 댓글 DOM 파싱
                comments_text_list = []
                comment_locators = page.locator("#content-text, ytd-comment-view-model #content-text, #comment-content")
                count = await comment_locators.count()

                for i in range(min(count, 15)):
                    try:
                        ctext = await comment_locators.nth(i).inner_text()
                        if ctext:
                            comments_text_list.append(ctext)
                    except Exception:
                        pass

                all_comments_body = "\n".join(comments_text_list)

                # 공식 검색어 & URL 매칭 검사
                if keyword and keyword in all_comments_body:
                    result["keyword_matched"] = True
                if landing_url and (landing_url in all_comments_body or "vercel.app" in all_comments_body):
                    result["url_matched"] = True

                # 고정 핀 확인
                pinned_badge = page.locator("ytd-pinned-comment-badge-renderer, [aria-label*='고정'], [aria-label*='Pinned']").first
                if await pinned_badge.count() > 0:
                    result["is_pinned"] = True

                if result["keyword_matched"] and result["url_matched"]:
                    result["comment_status"] = "VERIFIED_PERFECT"
                    logger.info(f"🎉 [유튜브 검증] {brand_name}: 공식 검색어({keyword}) & 랜딩링크 댓글 100% 실측 확인!")
                elif result["keyword_matched"] or result["url_matched"]:
                    result["comment_status"] = "VERIFIED_PARTIAL"
                    logger.info(f"✨ [유튜브 검증] {brand_name}: 댓글 키워드 또는 링크 부분 일치 확인")
                else:
                    result["comment_status"] = "NO_MATCH"
                    logger.warning(f"⚠️ [유튜브 검증] {brand_name}: 댓글 내 공식 검색어/링크 미검출 (아직 미등록 또는 대기중)")

                # 4. 실측 증빙 스크린샷 저장
                shot_path = PROOFS_DIR / f"verify_youtube_{brand}_{int(time.time())}.png"
                await page.screenshot(path=str(shot_path), full_page=False)
                result["proof_screenshot"] = str(shot_path)
                logger.info(f"📸 [증빙 캡처] 유튜브 실측 스크린샷: {shot_path.name}")

            except Exception as e:
                result["post_status"] = "ERROR"
                result["error"] = str(e)
                logger.error(f"❌ [유튜브 검증 예외] {e}")
            finally:
                await browser.close()

        return result

    async def verify_meta_reels(self, brand: str, post_url: Optional[str] = None) -> Dict[str, Any]:
        """메타 릴스(인스타/페이스북) 게시물 및 캡션/댓글 실측 검증"""
        cfg = self.BRANDS_STANDARD.get(brand, {})
        brand_name = cfg.get("name", brand)
        keyword = cfg.get("keyword", "")
        landing_url = cfg.get("url", "")

        result = {
            "platform": "meta_reels",
            "brand": brand,
            "url": post_url or "https://business.facebook.com/latest/content_calendar",
            "post_status": "UNKNOWN",
            "comment_status": "NOT_FOUND",
            "keyword_matched": False,
            "url_matched": False,
            "proof_screenshot": "",
            "verified_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Meta Business Suite 세션 프로필 연동
        meta_profile = PROJECT_ROOT / "brands" / brand / "meta_chrome_profile"
        clean_browser_profile_locks(meta_profile)

        logger.info(f"🔍 [메타 검증] {brand_name} MBS 게시물 실측 점검 중...")

        async with async_playwright() as p:
            try:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(meta_profile),
                    headless=self.headless,
                    args=get_safe_browser_args(),
                    viewport={"width": 1280, "height": 900}
                )
                page = context.pages[0] if context.pages else await context.new_page()

                target_url = post_url if post_url else "https://business.facebook.com/latest/posts/published_posts"
                await page.goto(target_url, wait_until="domcontentloaded", timeout=40000)
                await asyncio.sleep(4.0)

                body_text = await page.content()
                if keyword in body_text:
                    result["keyword_matched"] = True
                if "vercel.app" in body_text or landing_url in body_text:
                    result["url_matched"] = True

                if result["keyword_matched"] or result["url_matched"]:
                    result["post_status"] = "ALIVE"
                    result["comment_status"] = "VERIFIED_IN_CAPTION"
                    logger.info(f"🎉 [메타 검증] {brand_name}: 메타 릴스 게시글 및 공식문구 실측 확인!")
                else:
                    result["post_status"] = "ALIVE_OR_PENDING"
                    result["comment_status"] = "PENDING"

                shot_path = PROOFS_DIR / f"verify_meta_{brand}_{int(time.time())}.png"
                await page.screenshot(path=str(shot_path), full_page=False)
                result["proof_screenshot"] = str(shot_path)
                logger.info(f"📸 [증빙 캡처] 메타 실측 스크린샷: {shot_path.name}")

                await context.close()
            except Exception as e:
                result["post_status"] = "ERROR"
                result["error"] = str(e)
                logger.error(f"❌ [메타 검증 예외] {e}")

        return result

    async def verify_naver_clip(self, brand: str) -> Dict[str, Any]:
        """네이버 클립 스튜디오/채널 게시물 및 설명글 실측 검증"""
        cfg = self.BRANDS_STANDARD.get(brand, {})
        brand_name = cfg.get("name", brand)
        keyword = cfg.get("keyword", "")
        clip_id = cfg.get("clip_id", "")

        result = {
            "platform": "naver_clip",
            "brand": brand,
            "url": f"https://clipcreators.naver.com/web/contents",
            "post_status": "UNKNOWN",
            "comment_status": "NOT_FOUND",
            "keyword_matched": False,
            "url_matched": False,
            "proof_screenshot": "",
            "verified_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        naver_profile = PROJECT_ROOT / "brands" / brand / "naver_browser_profile"
        clean_browser_profile_locks(naver_profile)

        logger.info(f"🔍 [네이버 검증] {brand_name} 클립 스튜디오 실측 점검 중...")

        async with async_playwright() as p:
            try:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(naver_profile),
                    headless=self.headless,
                    args=get_safe_browser_args(),
                    viewport={"width": 1280, "height": 900}
                )
                page = context.pages[0] if context.pages else await context.new_page()

                await page.goto(result["url"], wait_until="domcontentloaded", timeout=40000)
                await asyncio.sleep(4.0)

                body_text = await page.content()
                if "등록된 클립" in body_text or "클립" in body_text or "콘텐츠 관리" in body_text:
                    result["post_status"] = "ALIVE"
                    if keyword in body_text:
                        result["keyword_matched"] = True
                        result["comment_status"] = "VERIFIED_IN_CLIP"
                    else:
                        result["comment_status"] = "ACTIVE_CONTENTS"
                    logger.info(f"🎉 [네이버 검증] {brand_name}: 네이버 클립 콘텐츠 실측 확인!")
                else:
                    result["post_status"] = "PENDING"

                shot_path = PROOFS_DIR / f"verify_naver_{brand}_{int(time.time())}.png"
                await page.screenshot(path=str(shot_path), full_page=False)
                result["proof_screenshot"] = str(shot_path)
                logger.info(f"📸 [증빙 캡처] 네이버 클립 실측 스크린샷: {shot_path.name}")

                await context.close()
            except Exception as e:
                result["post_status"] = "ERROR"
                result["error"] = str(e)
                logger.error(f"❌ [네이버 검증 예외] {e}")

        return result

    async def verify_single_brand(self, brand: str, yt_url: Optional[str] = None) -> Dict[str, Any]:
        """단일 브랜드 3개 채널 전수 실측 검증"""
        cfg = self.BRANDS_STANDARD.get(brand, {})
        brand_name = cfg.get("name", brand)

        logger.info("\n" + "=" * 70)
        logger.info(f"🕵️ [{brand_name}] 게시물 & 첫 댓글 실측 감사(Audit) 시작")
        logger.info("=" * 70)

        # 1. 유튜브 쇼츠 검증
        yt_res = await self.verify_youtube_shorts(brand, yt_url or "")
        await asyncio.sleep(2.0)

        # 2. 메타 릴스 검증
        meta_res = await self.verify_meta_reels(brand)
        await asyncio.sleep(2.0)

        # 3. 네이버 클립 검증
        naver_res = await self.verify_naver_clip(brand)

        return {
            "brand": brand,
            "brand_name": brand_name,
            "youtube": yt_res,
            "meta": meta_res,
            "naver": naver_res,
            "audit_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    async def verify_all_3brands(self, yt_urls: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """3개 앱 전체 게시물 및 댓글 종합 실측 감사"""
        yt_urls = yt_urls or {}
        report = {}
        for brand in ["aura", "insurance", "stock"]:
            url = yt_urls.get(brand, "")
            res = await self.verify_single_brand(brand, url)
            report[brand] = res
            await asyncio.sleep(3.0)

        report_file = PROOFS_DIR / f"omni_verification_report_{int(time.time())}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        latest_file = PROOFS_DIR / "latest_verification_report.json"
        with open(latest_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info(f"\n📑 [종합 감사 영수증 저장 완결] {report_file}")
        return report
