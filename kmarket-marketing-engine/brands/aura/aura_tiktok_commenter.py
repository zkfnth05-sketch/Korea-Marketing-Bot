# -*- coding: utf-8 -*-
"""
💖 [Aura 전용] 틱톡 쇼츠 최신 영상 공식 URL 첫 댓글 등록기 (독립 레고 블록)
========================================================================
- 브랜드: 💖 Aura AI 데이팅
- 공식 검색어: 아우라AI데이팅
- 공식 랜딩 URL: https://aura-ai-dating.vercel.app/
- 역할: 틱톡 쇼츠 발행 직후 내 최신 영상으로 이동하여 공식 랜딩 URL 및 검색 유도 첫 댓글을 100% 무인 자동 작성
- 안전 원칙: 중복 도배 방지 (이미 댓글 존재 시 스킵), 전용 프로필 격리
"""
import sys
import asyncio
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logger = logging.getLogger("AuraTikTokCommenter")
if not logger.handlers:
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("[%(asctime)s] [AuraTikTokCommenter] %(message)s"))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine.browser_guard import clean_browser_profile_locks, get_safe_browser_args, async_browser_lock
from core.engine.session_integrity import ensure_auth_cookies

PROFILE_DIR = CURRENT_DIR / "tiktok_chrome_profile"
SESSION_FILE = CURRENT_DIR / "tiktok_session.json"
PROOF_IMG = CURRENT_DIR / "aura_tiktok_comment_proof.png"

TIKTOK_USER = "aura_ai_official"
PROFILE_URL = f"https://www.tiktok.com/@{TIKTOK_USER}"
LANDING_URL = "https://aura-ai-dating.vercel.app/"
OFFICIAL_KEYWORD = "아우라AI데이팅"

COMMENT_TEXT = (
    f"💖 [Aura AI 데이팅] 50:50 황금 성비 청정 라운지:\n"
    f"👉 {LANDING_URL}\n\n"
    f"🔍 네이버 검색창에 [{OFFICIAL_KEYWORD}]을 검색해보세요!\n"
    f"✨ 지금 접속하시면 무료 AI 매칭 리포트를 즉시 받아보실 수 있습니다!"
)


class AuraTikTokCommenter:
    """💖 아우라 전용 틱톡 단독 댓글러 (독립 레고 블록)"""

    def __init__(self):
        self.profile_dir = PROFILE_DIR
        self.session_file = SESSION_FILE
        self.proof_img = PROOF_IMG

    def post_comment_on_latest_video(self, video_url: Optional[str] = None) -> Dict[str, Any]:
        """동기 호출 인터페이스"""
        try:
            return asyncio.run(self.post_comment_async(video_url))
        except Exception as e:
            logger.error(f"❌ 아우라 틱톡 댓글 최종 예외: {e}")
            return {"status": "error", "message": str(e), "brand": "aura"}

    async def post_comment_async(self, video_url: Optional[str] = None) -> Dict[str, Any]:
        """비동기 틱톡 최신 영상 첫 댓글 자동 작성"""
        clean_browser_profile_locks(self.profile_dir)

        async with async_browser_lock("Aura 틱톡 첫 댓글 작성", timeout_sec=300):
            async with async_playwright() as p:
                browser_args = get_safe_browser_args([
                    "--disable-blink-features=AutomationControlled",
                    "--no-first-run",
                    "--no-default-browser-check"
                ])
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(self.profile_dir),
                    headless=True,
                    args=browser_args,
                    viewport={"width": 1366, "height": 900},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
                )
                await ensure_auth_cookies("tiktok", context, self.session_file)
                page = context.pages[0] if context.pages else await context.new_page()

                try:
                    target_url = video_url
                    if not target_url:
                        logger.info(f"1. 틱톡 내 프로필 접속: {PROFILE_URL}")
                        await page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=40000)
                        await asyncio.sleep(4.0)

                        # 최신 동영상 1등 탐색
                        video_link = page.locator("div[data-e2e='user-post-item'] a, a[href*='/video/']").first
                        if not await video_link.is_visible():
                            logger.warning("틱톡 프로필에서 동영상 링크를 찾지 못했습니다.")
                            return {"status": "skipped", "message": "게시물 없음"}

                        href = await video_link.get_attribute("href")
                        target_url = href if href.startswith("http") else f"https://www.tiktok.com{href}"

                    logger.info(f"2. 틱톡 영상 상세 접속: {target_url}")
                    await page.goto(target_url, wait_until="domcontentloaded", timeout=40000)
                    await asyncio.sleep(4.0)

                    # 중복 댓글 방지 검사
                    body_text = await page.inner_text("body")
                    if LANDING_URL in body_text or OFFICIAL_KEYWORD in body_text:
                        logger.info("ℹ️ 이미 공식 URL 또는 검색어 댓글이 등록되어 있습니다. (도배 방지 스킵)")
                        return {"status": "already_commented", "message": "중복 댓글 방지 스킵"}

                    # 댓글 입력창 탐색
                    logger.info("3. 틱톡 댓글 입력창 활성화 중...")
                    comment_box = page.locator("div[data-e2e='comment-input'], div.public-DraftEditor-content, div[contenteditable='true']").first
                    if not await comment_box.is_visible():
                        # 모바일 뷰어일 경우 댓글 서랍 열기
                        open_btn = page.locator("button[data-e2e='comment-icon'], [aria-label*='댓글']").first
                        if await open_btn.is_visible():
                            await open_btn.click()
                            await asyncio.sleep(2.0)
                        comment_box = page.locator("div[data-e2e='comment-input'], div.public-DraftEditor-content, div[contenteditable='true']").first

                    if await comment_box.is_visible():
                        await comment_box.click()
                        await asyncio.sleep(1.0)

                        # 댓글 본문 타이핑
                        for char in COMMENT_TEXT:
                            if char == "\n":
                                await page.keyboard.press("Shift+Enter")
                            else:
                                await page.keyboard.type(char)
                            await asyncio.sleep(0.01)

                        await asyncio.sleep(1.5)

                        # [게시] 버튼 클릭
                        post_btn = page.locator("div[data-e2e='comment-post'], button:has-text('게시'), button:has-text('Post')").first
                        if await post_btn.is_visible():
                            await post_btn.click()
                            logger.info("🎉 [Aura 틱톡] 공식 URL 첫 댓글 게시 버튼 클릭 완료!")
                            await asyncio.sleep(3.0)

                            await page.screenshot(path=str(self.proof_img))
                            return {
                                "status": "success",
                                "brand": "aura",
                                "platform": "tiktok",
                                "comment_text": COMMENT_TEXT,
                                "video_url": target_url,
                                "proof_screenshot": str(self.proof_img)
                            }
                        else:
                            # 엔터 키 폴백
                            await page.keyboard.press("Enter")
                            await asyncio.sleep(2.0)
                            return {"status": "success", "message": "엔터 전송 완료", "video_url": target_url}
                    else:
                        logger.warning("틱톡 댓글 입력창을 찾지 못했습니다.")
                        return {"status": "error", "message": "댓글 입력창 미발견"}

                finally:
                    await context.close()


if __name__ == "__main__":
    commenter = AuraTikTokCommenter()
    print("Commenter initialized:", commenter)
