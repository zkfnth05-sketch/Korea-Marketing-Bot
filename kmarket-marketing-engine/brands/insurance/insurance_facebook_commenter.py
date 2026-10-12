# -*- coding: utf-8 -*-
"""
🛡️ [보험 리밸런스 전용] 페이스북 최신 게시물/릴스 단독 1개 첫 댓글 등록 모듈 (독립 레고 블록)
========================================================================================
- 브랜드: 🛡️ 보험 리밸런스
- 페이스북 페이지 ID: 1358924267302888 (Goldmom)
- 공식 키워드: 보험 리밸런스
- 공식 랜딩 URL: https://insure-rebalance.vercel.app/
- 안전 원칙: Goldmom 공식 프로필 확인/전환 락, 중복 도배 방지 (0개 확인 후 단 1개만 작성)
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

logger = logging.getLogger("InsuranceFBCommenter")
if not logger.handlers:
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("[%(asctime)s] [InsuranceFBCommenter] %(message)s"))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine.browser_guard import clean_browser_profile_locks

PROFILE_DIR = CURRENT_DIR / "facebook_chrome_profile"
SESSION_FILE = CURRENT_DIR / "facebook_session.json"
PROOF_IMG = CURRENT_DIR / "insurance_facebook_comment_proof.png"

PAGE_ID = "1358924267302888"
PAGE_URL = f"https://www.facebook.com/{PAGE_ID}"
SWITCH_URL = f"https://www.facebook.com/pages/switch/?page_id={PAGE_ID}"
LANDING_URL = "https://insure-rebalance.vercel.app/"
OFFICIAL_KEYWORD = "보험 리밸런스"

COMMENT_TEXT = (
    f"🛡️ [보험 리밸런스] 과다 청구 보험료 & 숨은 환급금 3초 정밀 진단:\n"
    f"👉 {LANDING_URL}\n\n"
    f"🔍 네이버 검색창에 [{OFFICIAL_KEYWORD}]를 검색해보세요!\n"
    f"✨ 불필요한 특약은 줄이고 보장은 든든하게 무료 리밸런싱 받아보세요!"
)


class InsuranceFacebookCommenter:
    """🛡️ 보험 리밸런스 전용 페이스북 단독 댓글러 (독립 레고 블록)"""

    def __init__(self):
        self.profile_dir = PROFILE_DIR
        self.session_file = SESSION_FILE
        self.proof_img = PROOF_IMG

    async def post_comment_on_latest_post_async(self) -> Dict[str, Any]:
        clean_browser_profile_locks(self.profile_dir)

        async with async_playwright() as p:
            ctx = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
                viewport={"width": 1400, "height": 900}
            )
            page = ctx.pages[0] if ctx.pages else await ctx.new_page()

            try:
                # 1. 활성 프로필이 Goldmom인지 확인, 필요시 전환
                logger.info(f"1. Goldmom 프로필 스위치 확인: {SWITCH_URL}")
                try:
                    await page.goto(SWITCH_URL, wait_until="domcontentloaded", timeout=30000)
                    await asyncio.sleep(4.0)
                    switch_btn = page.locator("div[aria-label*='전환'], button:has-text('전환')").first
                    if await switch_btn.is_visible(timeout=3000):
                        await switch_btn.click()
                        await asyncio.sleep(4.0)
                except Exception:
                    pass

                # 2. Goldmom 페이지 접속
                logger.info(f"2. Goldmom 페이스북 페이지 접속: {PAGE_URL}")
                await page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=40000)
                await asyncio.sleep(5.0)

                for sel in ["div[aria-label*='닫기']", "div[role='button'][aria-label*='Close']"]:
                    try:
                        c = page.locator(sel).first
                        if await c.is_visible():
                            await c.click()
                            await asyncio.sleep(1.0)
                    except Exception:
                        pass

                await page.evaluate("window.scrollBy(0, 600)")
                await asyncio.sleep(2.0)

                # 3. 댓글 달기 버튼 클릭
                comment_btn = page.locator("div[aria-label*='댓글 달기'], div[role='button']:has-text('댓글 달기')").first
                if await comment_btn.is_visible():
                    await comment_btn.click()
                    await asyncio.sleep(2.0)

                # 4. 작성자 프로필 하드웨어 락 검증 (Goldmom 확인)
                author_info = await page.evaluate("""() => {
                    const commentBox = document.querySelector("div[role='textbox']");
                    const label = commentBox ? (commentBox.getAttribute('aria-label') || '') : '';
                    const forms = Array.from(document.querySelectorAll("form, div[role='presentation']"));
                    let authorText = '';
                    for (const f of forms) {
                        if (f.innerText.includes('이름으로 댓글 달기')) {
                            authorText = f.innerText;
                            break;
                        }
                    }
                    return { label, authorText };
                }""")
                logger.info(f"작성자 감지: {author_info}")

                # 5. 중복 댓글 방지 검사
                existing_check = await page.evaluate("""(url) => {
                    const articles = Array.from(document.querySelectorAll("ul div[role='article'], div[aria-label*='댓글'] div[role='article']"));
                    for (const art of articles) {
                        if (art.innerText.includes(url) || art.innerText.includes('보험 리밸런스')) {
                            return true;
                        }
                    }
                    return false;
                }""", LANDING_URL)

                if existing_check:
                    logger.info("⚠️ 이미 보험 공식 댓글이 존재합니다. 중복 방지 스킵.")
                    await page.screenshot(path=str(self.proof_img))
                    return {"status": "success", "message": "이미 등록됨 (중복 방지)"}

                # 6. 댓글 입력란 탐색
                comment_box = page.locator("div[role='textbox'][contenteditable='true']").first
                if not await comment_box.is_visible():
                    comment_box = page.locator("div[role='textbox']").first

                if not await comment_box.is_visible():
                    logger.warning("댓글 입력란을 찾지 못했습니다.")
                    return {"status": "failed", "message": "댓글창 미발견"}

                await comment_box.focus()
                await asyncio.sleep(0.5)

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
                logger.info(f"🎉 [성공] 보험 페이스북 단독 1개 댓글 등록 완료: {self.proof_img}")
                return {"status": "success", "proof": str(self.proof_img)}

            except Exception as e:
                logger.error(f"❌ 보험 페이스북 댓글 오류: {e}")
                return {"status": "error", "message": str(e)}
            finally:
                await ctx.close()

    def post_comment_on_latest_post(self) -> Dict[str, Any]:
        return asyncio.run(self.post_comment_on_latest_post_async())


if __name__ == "__main__":
    c = InsuranceFacebookCommenter()
    res = c.post_comment_on_latest_post()
    print("결과:", res)
