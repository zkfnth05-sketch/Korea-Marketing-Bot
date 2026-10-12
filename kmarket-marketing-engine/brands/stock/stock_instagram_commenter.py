# -*- coding: utf-8 -*-
"""
📈 [StockMaster AI 전용] 인스타그램 릴스 최신글 단독 1개 첫 댓글 등록 모듈 (독립 레고 블록)
========================================================================================
- 브랜드: 📈 StockMaster AI
- 인스타 계정: @stockmaster_ai
- 공식 키워드: 스톡마스터 AI
- 공식 랜딩 URL: https://stockmaster-ai.vercel.app/
- 안전 원칙: 중복 도배 방지 (0개 확인 후 단 1개만 작성), 전용 프로필 격리
========================================================================================
"""
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any
from playwright.async_api import async_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logger = logging.getLogger("StockInstaCommenter")
if not logger.handlers:
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("[%(asctime)s] [StockInstaCommenter] %(message)s"))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine.browser_guard import clean_browser_profile_locks

PROFILE_DIR = CURRENT_DIR / "instagram_chrome_profile"
SESSION_FILE = CURRENT_DIR / "instagram_session.json"
PROOF_IMG = CURRENT_DIR / "stock_instagram_comment_proof.png"

INSTA_USERNAME = "stockmaster_ai"
PROFILE_URL = f"https://www.instagram.com/{INSTA_USERNAME}/"
LANDING_URL = "https://stockmaster-ai.vercel.app/"
OFFICIAL_KEYWORD = "스톡마스터 AI"

COMMENT_TEXT = (
    f"📈 [StockMaster AI] 실시간 AI 퀀트 분석 & 급등 테마주 포트폴리오 무료 진단:\n"
    f"👉 {LANDING_URL}\n\n"
    f"🔍 네이버 검색창에 [{OFFICIAL_KEYWORD}]를 검색해보세요!\n"
    f"✨ 프리미엄 AI 알고리즘의 실시간 시장 분석을 지금 즉시 확인해보세요!"
)


class StockInstagramCommenter:
    """📈 스톡마스터 AI 전용 인스타그램 단독 댓글러 (독립 레고 블록)"""

    def __init__(self):
        self.profile_dir = PROFILE_DIR
        self.session_file = SESSION_FILE
        self.proof_img = PROOF_IMG

    async def post_comment_on_latest_reel_async(self) -> Dict[str, Any]:
        clean_browser_profile_locks(self.profile_dir)

        async with async_playwright() as p:
            ctx = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
                viewport={"width": 1280, "height": 900}
            )
            page = ctx.pages[0] if ctx.pages else await ctx.new_page()

            try:
                logger.info(f"1. 인스타그램 프로필 접속: {PROFILE_URL}")
                await page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=40000)
                await asyncio.sleep(4.0)

                # 최신 릴스 탐색
                reel_link = page.locator("a[href*='/reel/'], a[href*='/p/']").first
                if not await reel_link.is_visible():
                    logger.warning("릴스/게시물 링크를 찾지 못했습니다.")
                    return {"status": "skipped", "message": "게시물 없음"}

                reel_href = await reel_link.get_attribute("href")
                reel_url = f"https://www.instagram.com{reel_href}" if reel_href.startswith("/") else reel_href
                logger.info(f"2. 최신 릴스 상세 접속: {reel_url}")
                await page.goto(reel_url, wait_until="domcontentloaded", timeout=40000)
                await asyncio.sleep(4.0)

                # 중복 댓글 방지 검사 (Strict Deduplication Guard)
                existing_check = await page.evaluate("""(url) => {
                    const articles = Array.from(document.querySelectorAll("div[role='article'], ul ul"));
                    for (const art of articles) {
                        if (art.innerText.includes(url) || art.innerText.includes('스톡마스터 AI')) {
                            return true;
                        }
                    }
                    return false;
                }""", LANDING_URL)

                if existing_check:
                    logger.info("⚠️ 이미 주식 공식 댓글이 존재합니다. 중복 방지 스킵.")
                    await page.screenshot(path=str(self.proof_img))
                    return {"status": "success", "message": "이미 등록됨 (중복 방지)"}

                # 댓글 입력창 찾기
                comment_box = page.locator("textarea[aria-label*='댓글'], textarea[placeholder*='댓글'], div[role='textbox']").first
                if not await comment_box.is_visible():
                    logger.warning("댓글 입력창이 비활성화되어 있거나 찾을 수 없습니다.")
                    return {"status": "failed", "message": "댓글창 미발견"}

                await comment_box.click()
                await asyncio.sleep(0.5)

                # 단 1개 댓글로 줄바꿈 전송
                lines = COMMENT_TEXT.split("\n")
                for i, line in enumerate(lines):
                    if line:
                        await page.keyboard.type(line, delay=15)
                    if i < len(lines) - 1:
                        await page.keyboard.down("Shift")
                        await page.keyboard.press("Enter")
                        await page.keyboard.up("Shift")
                        await asyncio.sleep(0.05)

                await asyncio.sleep(1.0)
                await page.keyboard.press("Enter")
                await asyncio.sleep(5.0)

                await page.screenshot(path=str(self.proof_img))
                logger.info(f"🎉 [성공] 스톡마스터 AI 인스타그램 단독 1개 댓글 등록 완료: {self.proof_img}")
                return {"status": "success", "proof": str(self.proof_img)}

            except Exception as e:
                logger.error(f"❌ 스톡마스터 AI 인스타 댓글 오류: {e}")
                return {"status": "error", "message": str(e)}
            finally:
                await ctx.close()

    def post_comment_on_latest_reel(self) -> Dict[str, Any]:
        return asyncio.run(self.post_comment_on_latest_reel_async())


if __name__ == "__main__":
    c = StockInstagramCommenter()
    res = c.post_comment_on_latest_reel()
    print("결과:", res)
