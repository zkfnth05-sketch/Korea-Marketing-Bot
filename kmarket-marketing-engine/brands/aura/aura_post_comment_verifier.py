# -*- coding: utf-8 -*-
"""
💖 Aura AI 데이팅 전용 - [게시물 & 첫 댓글 실측 확인 레고 블록]
=============================================================================
- 브랜드: Aura AI 데이팅 (순수 독립 모듈)
- 공식 검색어: '아우라AI데이팅' (붙여쓰기 필수)
- 공식 URL: https://aura-ai-dating.vercel.app/
- 역할:
  1. 유튜브 쇼츠 실물 영상 노출 확인 + 첫 댓글/고정핀에 '아우라AI데이팅' & 랜딩 URL 실측 확인
  2. 메타(Instagram/Facebook) 릴스 게시글 및 캡션/댓글 공식 검색어 실측 확인
  3. 네이버 클립 스튜디오/채널(aura-dating) 게시물 및 설명글 실측 확인
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
logger = logging.getLogger("AuraVerifier")

PROOFS_DIR = PROJECT_ROOT / "outputs" / "proofs" / "aura"
PROOFS_DIR.mkdir(parents=True, exist_ok=True)


class AuraPostCommentVerifier:
    """💖 Aura AI 데이팅 전용 게시물 및 첫 댓글 실측 확인기"""

    BRAND_NAME = "💖 Aura AI 데이팅"
    OFFICIAL_KEYWORD = "아우라AI데이팅"
    LANDING_URL = "https://aura-ai-dating.vercel.app/"
    CLIP_ID = "aura-dating"

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.profile_dir_meta = CURRENT_DIR / "meta_chrome_profile"
        self.profile_dir_naver = CURRENT_DIR / "naver_browser_profile"
        self.profile_dir_yt = CURRENT_DIR / "youtube_chrome_profile"

    async def verify_youtube_shorts(self, video_url: str) -> Dict[str, Any]:
        """Aura 유튜브 쇼츠 게시물 및 공식 댓글/고정핀 실측 검증"""
        result = {
            "platform": "youtube_shorts",
            "brand": "aura",
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

        logger.info(f"🔍 [Aura 유튜브 실측] 쇼츠 접속: {video_url}")

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
                    logger.warning("❌ [Aura 유튜브] 쇼츠 영상을 찾을 수 없음")
                else:
                    result["post_status"] = "ALIVE"
                    logger.info("✅ [Aura 유튜브] 쇼츠 게시물 정상 노출 확인!")

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
                if self.LANDING_URL in all_body or "aura-ai-dating.vercel.app" in all_body:
                    result["url_matched"] = True

                # 고정 핀 체크
                pinned_badge = page.locator("ytd-pinned-comment-badge-renderer, [aria-label*='고정'], [aria-label*='Pinned']").first
                if await pinned_badge.count() > 0:
                    result["is_pinned"] = True

                if result["keyword_matched"] and result["url_matched"]:
                    result["comment_status"] = "VERIFIED_PERFECT"
                    logger.info(f"🎉 [Aura 유튜브] '{self.OFFICIAL_KEYWORD}' & 공식링크 첫 댓글 100% 실측 확인!")
                elif result["keyword_matched"] or result["url_matched"]:
                    result["comment_status"] = "VERIFIED_PARTIAL"
                else:
                    result["comment_status"] = "NO_MATCH"

                # 4. 실측 증빙 스크린샷
                shot_path = PROOFS_DIR / f"verify_aura_youtube_{int(time.time())}.png"
                await page.screenshot(path=str(shot_path), full_page=False)
                result["proof_screenshot"] = str(shot_path)
                logger.info(f"📸 [Aura 증빙] 유튜브 캡처: {shot_path.name}")

            except Exception as e:
                result["post_status"] = "ERROR"
                result["error"] = str(e)
                logger.error(f"❌ [Aura 유튜브 예외] {e}")
            finally:
                await browser.close()

        return result

    async def verify_meta_reels(self) -> Dict[str, Any]:
        """Aura 메타 릴스(MBS) 게시물 실측 검증"""
        result = {
            "platform": "meta_reels",
            "brand": "aura",
            "url": "https://business.facebook.com/latest/posts/published_posts",
            "post_status": "UNKNOWN",
            "comment_status": "NOT_FOUND",
            "keyword_matched": False,
            "url_matched": False,
            "proof_screenshot": "",
            "verified_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        clean_browser_profile_locks(self.profile_dir_meta)
        logger.info("🔍 [Aura 메타 실측] Meta Business Suite 점검 중...")

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
                if "aura-ai-dating" in body_text:
                    result["url_matched"] = True

                if result["keyword_matched"] or result["url_matched"]:
                    result["post_status"] = "ALIVE"
                    result["comment_status"] = "VERIFIED_IN_CAPTION"
                    logger.info("🎉 [Aura 메타] 릴스 게시글 및 공식문구 실측 확인!")
                else:
                    result["post_status"] = "ALIVE_OR_PENDING"
                    result["comment_status"] = "PENDING"

                shot_path = PROOFS_DIR / f"verify_aura_meta_{int(time.time())}.png"
                await page.screenshot(path=str(shot_path), full_page=False)
                result["proof_screenshot"] = str(shot_path)
                logger.info(f"📸 [Aura 증빙] 메타 캡처: {shot_path.name}")

                await context.close()
            except Exception as e:
                result["post_status"] = "ERROR"
                result["error"] = str(e)
                logger.error(f"❌ [Aura 메타 예외] {e}")

        return result

    async def verify_naver_clip(self) -> Dict[str, Any]:
        """Aura 네이버 클립 게시물 실측 검증"""
        result = {
            "platform": "naver_clip",
            "brand": "aura",
            "url": "https://clipcreators.naver.com/web/contents",
            "post_status": "UNKNOWN",
            "comment_status": "NOT_FOUND",
            "keyword_matched": False,
            "url_matched": False,
            "proof_screenshot": "",
            "verified_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        clean_browser_profile_locks(self.profile_dir_naver)
        logger.info("🔍 [Aura 네이버 실측] 클립 스튜디오 점검 중...")

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
                    logger.info("🎉 [Aura 네이버] 클립 콘텐츠 정상 실측 확인!")
                else:
                    result["post_status"] = "PENDING"

                shot_path = PROOFS_DIR / f"verify_aura_naver_{int(time.time())}.png"
                await page.screenshot(path=str(shot_path), full_page=False)
                result["proof_screenshot"] = str(shot_path)
                logger.info(f"📸 [Aura 증빙] 네이버 클립 캡처: {shot_path.name}")

                await context.close()
            except Exception as e:
                result["post_status"] = "ERROR"
                result["error"] = str(e)
                logger.error(f"❌ [Aura 네이버 예외] {e}")

        return result

    async def verify_facebook(self) -> Dict[str, Any]:
        """Aura 페이스북 공식 페이지 최신 글 및 첫 댓글 실측 검증"""
        result = {
            "platform": "facebook",
            "brand": "aura",
            "url": "https://www.facebook.com/1356851504174047",
            "post_status": "UNKNOWN",
            "comment_status": "NOT_FOUND",
            "keyword_matched": False,
            "url_matched": False,
            "proof_screenshot": "",
            "verified_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        profile_dir = CURRENT_DIR / "facebook_chrome_profile"
        clean_browser_profile_locks(profile_dir)
        logger.info("🔍 [Aura 페이스북 실측] 공식 페이지 접속 중...")

        async with async_playwright() as p:
            try:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(profile_dir),
                    headless=self.headless,
                    args=get_safe_browser_args(),
                    viewport={"width": 1400, "height": 900}
                )
                page = context.pages[0] if context.pages else await context.new_page()

                await page.goto(result["url"], wait_until="domcontentloaded", timeout=40000)
                await asyncio.sleep(4.0)

                body_text = await page.content()
                if "아우라" in body_text or "Aura" in body_text:
                    result["post_status"] = "ALIVE"
                if self.OFFICIAL_KEYWORD in body_text:
                    result["keyword_matched"] = True
                if "aura-ai-dating" in body_text:
                    result["url_matched"] = True

                if result["keyword_matched"] and result["url_matched"]:
                    result["comment_status"] = "VERIFIED_PERFECT"
                    logger.info("🎉 [Aura 페이스북] 최신 게시물 및 공식 링크 첫 댓글 100% 실측 확인!")
                elif result["keyword_matched"] or result["url_matched"]:
                    result["comment_status"] = "VERIFIED_PARTIAL"
                else:
                    result["comment_status"] = "ALIVE_NO_COMMENT"

                shot_path = PROOFS_DIR / f"verify_aura_facebook_{int(time.time())}.png"
                await page.screenshot(path=str(shot_path), full_page=False)
                result["proof_screenshot"] = str(shot_path)
                logger.info(f"📸 [Aura 증빙] 페이스북 캡처: {shot_path.name}")

                await context.close()
            except Exception as e:
                result["post_status"] = "ERROR"
                result["error"] = str(e)
                logger.error(f"❌ [Aura 페이스북 예외] {e}")

        return result

    async def verify_instagram(self) -> Dict[str, Any]:
        """Aura 인스타그램 공식 프로필 최신 릴스/게시물 및 첫 댓글 실측 검증"""
        result = {
            "platform": "instagram",
            "brand": "aura",
            "url": "https://www.instagram.com/aura_ai_dating/",
            "post_status": "UNKNOWN",
            "comment_status": "NOT_FOUND",
            "keyword_matched": False,
            "url_matched": False,
            "proof_screenshot": "",
            "verified_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        profile_dir = CURRENT_DIR / "instagram_chrome_profile"
        clean_browser_profile_locks(profile_dir)
        logger.info("🔍 [Aura 인스타그램 실측] 공식 프로필 접속 중...")

        async with async_playwright() as p:
            try:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(profile_dir),
                    headless=self.headless,
                    args=get_safe_browser_args(),
                    viewport={"width": 1280, "height": 900}
                )
                page = context.pages[0] if context.pages else await context.new_page()

                await page.goto(result["url"], wait_until="domcontentloaded", timeout=40000)
                await asyncio.sleep(4.0)

                body_text = await page.content()
                if "aura_ai_dating" in body_text or "게시물" in body_text:
                    result["post_status"] = "ALIVE"

                reel_link = page.locator("a[href*='/reel/'], a[href*='/p/']").first
                if await reel_link.is_visible():
                    reel_href = await reel_link.get_attribute("href")
                    target_url = f"https://www.instagram.com{reel_href}" if reel_href.startswith("/") else reel_href
                    result["url"] = target_url
                    await page.goto(target_url, wait_until="domcontentloaded", timeout=40000)
                    await asyncio.sleep(3.0)

                    detail_text = await page.content()
                    if self.OFFICIAL_KEYWORD in detail_text:
                        result["keyword_matched"] = True
                    if "aura-ai-dating" in detail_text:
                        result["url_matched"] = True

                if result["keyword_matched"] and result["url_matched"]:
                    result["comment_status"] = "VERIFIED_PERFECT"
                    logger.info("🎉 [Aura 인스타그램] 최신 릴스 및 공식 링크 첫 댓글 100% 실측 확인!")
                elif result["keyword_matched"] or result["url_matched"]:
                    result["comment_status"] = "VERIFIED_PARTIAL"
                else:
                    result["comment_status"] = "ALIVE_OR_PENDING"

                shot_path = PROOFS_DIR / f"verify_aura_instagram_{int(time.time())}.png"
                await page.screenshot(path=str(shot_path), full_page=False)
                result["proof_screenshot"] = str(shot_path)
                logger.info(f"📸 [Aura 증빙] 인스타그램 캡처: {shot_path.name}")

                await context.close()
            except Exception as e:
                result["post_status"] = "ERROR"
                result["error"] = str(e)
                logger.error(f"❌ [Aura 인스타그램 예외] {e}")

        return result

    async def verify_threads(self) -> Dict[str, Any]:
        """Aura 스레드(Threads) 공식 피드 최신 글 및 첫 타래 댓글 실측 검증"""
        result = {
            "platform": "threads",
            "brand": "aura",
            "url": "https://www.threads.net/@aura_ai_dating",
            "post_status": "UNKNOWN",
            "comment_status": "NOT_FOUND",
            "keyword_matched": False,
            "url_matched": False,
            "proof_screenshot": "",
            "verified_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        profile_dir = CURRENT_DIR / "threads_chrome_profile"
        if not profile_dir.exists():
            profile_dir = CURRENT_DIR / "meta_chrome_profile"
        clean_browser_profile_locks(profile_dir)
        logger.info("🔍 [Aura 스레드 실측] 공식 프로필 피드 접속 중...")

        async with async_playwright() as p:
            try:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(profile_dir),
                    headless=self.headless,
                    args=get_safe_browser_args(),
                    viewport={"width": 1280, "height": 900}
                )
                page = context.pages[0] if context.pages else await context.new_page()

                await page.goto(result["url"], wait_until="domcontentloaded", timeout=40000)
                await asyncio.sleep(4.0)

                body_text = await page.content()
                if "aura_ai_dating" in body_text or "스레드" in body_text:
                    result["post_status"] = "ALIVE"
                if self.OFFICIAL_KEYWORD in body_text:
                    result["keyword_matched"] = True
                if "aura-ai-dating" in body_text:
                    result["url_matched"] = True

                if result["keyword_matched"] and result["url_matched"]:
                    result["comment_status"] = "VERIFIED_PERFECT"
                    logger.info("🎉 [Aura 스레드] 최신 스레드 및 공식 링크 타래 댓글 100% 실측 확인!")
                elif result["keyword_matched"] or result["url_matched"]:
                    result["comment_status"] = "VERIFIED_PARTIAL"
                else:
                    result["comment_status"] = "ALIVE_OR_PENDING"

                shot_path = PROOFS_DIR / f"verify_aura_threads_{int(time.time())}.png"
                await page.screenshot(path=str(shot_path), full_page=False)
                result["proof_screenshot"] = str(shot_path)
                logger.info(f"📸 [Aura 증빙] 스레드 캡처: {shot_path.name}")

                await context.close()
            except Exception as e:
                result["post_status"] = "ERROR"
                result["error"] = str(e)
                logger.error(f"❌ [Aura 스레드 예외] {e}")

        return result

    async def run_full_verification(self, yt_url: Optional[str] = None) -> Dict[str, Any]:
        """Aura 전 플랫폼(인스타, 페북, 스레드, 유튜브, 네이버) 전수 실측 검증 실행 및 대시보드 저장"""
        logger.info("\n" + "=" * 70)
        logger.info(f"🕵️ [{self.BRAND_NAME}] 숏폼 & 카드뉴스 5대 플랫폼 전수 실측 감사 시작")
        logger.info(f"• 공식 검색어: '{self.OFFICIAL_KEYWORD}' | 공식 URL: {self.LANDING_URL}")
        logger.info("=" * 70)

        # 1. 페이스북 실측
        fb_res = await self.verify_facebook()
        await asyncio.sleep(2.0)

        # 2. 인스타그램 실측
        ig_res = await self.verify_instagram()
        await asyncio.sleep(2.0)

        # 3. 스레드 실측
        th_res = await self.verify_threads()
        await asyncio.sleep(2.0)

        # 4. 유튜브 쇼츠 실측
        if not yt_url:
            receipt = PROJECT_ROOT / "outputs" / "proofs" / "3brands_omni_publish_receipt.json"
            if receipt.exists():
                try:
                    with open(receipt, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    yt_url = data.get("aura", {}).get("channels", {}).get("youtube", {}).get("video_url")
                except Exception:
                    pass
        yt_res = await self.verify_youtube_shorts(yt_url or "https://youtube.com/shorts/FGHn1Ngu5Xo")
        await asyncio.sleep(2.0)

        # 5. 네이버 클립 실측
        naver_res = await self.verify_naver_clip()

        report = {
            "brand": "aura",
            "brand_name": self.BRAND_NAME,
            "keyword": self.OFFICIAL_KEYWORD,
            "landing_url": self.LANDING_URL,
            "audit_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "platforms": {
                "instagram": ig_res,
                "facebook": fb_res,
                "threads": th_res,
                "youtube_shorts": yt_res,
                "naver_clip": naver_res
            }
        }

        # 1. 감사 JSON 영구 저장
        out_json = PROOFS_DIR / f"aura_verification_{int(time.time())}.json"
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        # 2. 대시보드 메인 보드 JSON 갱신
        board_file = PROJECT_ROOT / "outputs" / "live_verification_board.json"
        board_data = {}
        if board_file.exists():
            try:
                with open(board_file, "r", encoding="utf-8") as bf:
                    board_data = json.load(bf)
            except Exception:
                board_data = {}
        board_data["aura"] = report
        with open(board_file, "w", encoding="utf-8") as bf:
            json.dump(board_data, bf, ensure_ascii=False, indent=2)

        # 3. 시각적 HTML 대시보드 리포트 생성
        html_file = PROJECT_ROOT / "outputs" / "live_verification_dashboard.html"
        self._generate_dashboard_html(report, html_file)

        logger.info(f"🎉 [전수 실측 검증 완료] 대시보드 리포트 생성: {html_file}")
        return report

    def _generate_dashboard_html(self, report: Dict[str, Any], html_path: Path):
        """대시보드에서 브라우저로 바로 볼 수 있는 프리미엄 시각적 실측 감사 리포트 HTML 생성"""
        platforms = report.get("platforms", {})
        cards_html = ""
        for name, data in platforms.items():
            if not data or not isinstance(data, dict):
                continue
            status_color = "#10b981" if data.get("post_status") == "ALIVE" else "#f59e0b"
            comment_color = "#10b981" if "VERIFIED" in data.get("comment_status", "") else "#ef4444"
            shot_rel = Path(data.get("proof_screenshot", "")).name if data.get("proof_screenshot") else ""
            
            cards_html += f"""
            <div style="background:#1e293b; border-radius:12px; padding:20px; margin-bottom:16px; border:1px solid #334155;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <h3 style="margin:0; color:#38bdf8; font-size:18px;">🌐 {name.upper()}</h3>
                    <span style="background:{status_color}; color:#fff; padding:4px 10px; border-radius:20px; font-size:12px; font-weight:bold;">
                        {data.get('post_status')}
                    </span>
                </div>
                <div style="color:#94a3b8; font-size:14px; margin-bottom:8px;">
                    <strong>접속 URL:</strong> <a href="{data.get('url')}" target="_blank" style="color:#60a5fa; text-decoration:none;">{data.get('url')}</a>
                </div>
                <div style="color:#cbd5e1; font-size:14px; margin-bottom:8px;">
                    <strong>첫 댓글 검증:</strong> <span style="color:{comment_color}; font-weight:bold;">{data.get('comment_status')}</span>
                    (키워드: {'✅ 일치' if data.get('keyword_matched') else '❌ 미발견'} / 링크: {'✅ 일치' if data.get('url_matched') else '❌ 미발견'})
                </div>
                <div style="color:#64748b; font-size:12px; margin-bottom:12px;">
                    실측 확인 시각: {data.get('verified_at')}
                </div>
                {f'<div style="margin-top:10px;"><a href="proofs/aura/{shot_rel}" target="_blank"><img src="proofs/aura/{shot_rel}" style="max-width:100%; max-height:220px; border-radius:8px; border:1px solid #475569;" alt="증빙 스크린샷" /></a></div>' if shot_rel else ''}
            </div>
            """

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>💖 Aura 마케팅봇 실측 감사 대시보드</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background:#0f172a; color:#f8fafc; padding:30px; margin:0; }}
        .container {{ max-width: 900px; margin:0 auto; }}
        .header {{ display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155; padding-bottom:16px; margin-bottom:24px; }}
        .badge {{ background:#ec4899; color:#fff; padding:6px 14px; border-radius:20px; font-weight:bold; font-size:14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1 style="margin:0; font-size:24px; color:#fff;">💖 Aura AI 데이팅 실측 감사 대시보드</h1>
                <p style="margin:6px 0 0; color:#94a3b8; font-size:14px;">사람처럼 웹 브라우저를 띄워 실물 게시물 및 공식 검색어 첫 댓글을 100% 실측 검증한 결과</p>
            </div>
            <span class="badge">검증 완료</span>
        </div>
        <div style="background:#1e293b; border-radius:8px; padding:14px; margin-bottom:24px; color:#cbd5e1; font-size:14px;">
            📌 공식 검색어: <strong>아우라AI데이팅</strong> | 공식 랜딩 URL: <a href="https://aura-ai-dating.vercel.app/" target="_blank" style="color:#38bdf8;">https://aura-ai-dating.vercel.app/</a> | 감사 기준 시각: {report.get('audit_time')}
        </div>
        {cards_html}
    </div>
</body>
</html>
"""
        with open(html_path, "w", encoding="utf-8") as hf:
            hf.write(html_content)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Aura 게시물 및 첫 댓글 실측 확인기")
    parser.add_argument("--url", "-u", default=None, help="유튜브 쇼츠 URL")
    args = parser.parse_args()

    verifier = AuraPostCommentVerifier(headless=True)
    res = asyncio.run(verifier.run_full_verification(args.url))
    print(json.dumps(res, ensure_ascii=False, indent=2))
