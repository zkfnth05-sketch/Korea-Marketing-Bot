# -*- coding: utf-8 -*-
"""
💖 [Aura 전용] 인스타그램 릴스 최신글 단독 1개 첫 댓글 등록 모듈 (독립 레고 블록)
========================================================================================
- 브랜드: 💖 Aura AI 데이팅
- 인스타 계정: @aura_ai_dating
- 공식 키워드: 아우라AI데이팅
- 공식 랜딩 URL: https://aura-ai-dating.vercel.app/
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

logger = logging.getLogger("AuraInstaCommenter")
if not logger.handlers:
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("[%(asctime)s] [AuraInstaCommenter] %(message)s"))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine.browser_guard import clean_browser_profile_locks

PROFILE_DIR = CURRENT_DIR / "instagram_chrome_profile"
SESSION_FILE = CURRENT_DIR / "instagram_session.json"
PROOF_IMG = CURRENT_DIR / "aura_instagram_comment_proof.png"

INSTA_USERNAME = "aura_ai_dating"
PROFILE_URL = f"https://www.instagram.com/{INSTA_USERNAME}/"
LANDING_URL = "https://aura-ai-dating.vercel.app/"
OFFICIAL_KEYWORD = "아우라AI데이팅"

COMMENT_TEXT = (
    f"💖 [Aura AI 데이팅] 3초 만에 찾는 나만의 이상형 매칭:\n"
    f"👉 {LANDING_URL}\n\n"
    f"🔍 네이버 검색창에 [{OFFICIAL_KEYWORD}]를 검색해보세요!\n"
    f"✨ 지금 접속하시면 무료 AI 매칭 리포트를 즉시 받아보실 수 있습니다!"
)


class AuraInstagramCommenter:
    """💖 아우라 전용 인스타그램 단독 댓글러 (독립 레고 블록)"""

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

            COMMENT_BOX_SEL = (
                "div[role='textbox'][contenteditable='true'], textarea[aria-label*='댓글'], "
                "textarea[placeholder*='댓글'], textarea[aria-label*='Add a comment'], "
                "textarea[placeholder*='Add a comment'], textarea"
            )
            COMMENT_ICON_SEL = (
                "svg[aria-label*='댓글'], svg[aria-label*='Comment'], "
                "button:has(svg[aria-label*='댓글']), [role='button']:has(svg[aria-label*='댓글']), "
                "button:has(svg[aria-label*='Comment']), [role='button']:has(svg[aria-label*='Comment'])"
            )
            COMMENT_LIST_SEL = "div[role='article'], ul ul"

            async def _find_comment_box():
                """댓글 입력창을 (Playwright 로케이터 ➔ JS querySelector) 2중으로 탐색한다."""
                box = page.locator(COMMENT_BOX_SEL).first
                try:
                    if await box.count() > 0 and await box.is_visible():
                        return box
                except Exception:
                    pass
                try:
                    handle = await page.evaluate_handle("""(sel) => {
                        const el = document.querySelector(sel);
                        return el || null;
                    }""", COMMENT_BOX_SEL)
                    element = handle.as_element()
                    if element is not None:
                        return element
                except Exception:
                    pass
                return None

            async def _open_comment_drawer() -> bool:
                """릴스 화면에서 댓글 서랍이 닫혀 있으면 댓글 아이콘을 클릭해 개방한다."""
                try:
                    icon = page.locator(COMMENT_ICON_SEL).first
                    if await icon.count() > 0 and await icon.is_visible():
                        await icon.click()
                        logger.info("💬 [아우라 인스타] 댓글 아이콘 클릭 ➔ 우측 댓글 서랍 개방")
                        return True
                    clicked = await page.evaluate("""() => {
                        const svg = Array.from(document.querySelectorAll('svg'))
                            .find(s => {
                                const a = (s.getAttribute('aria-label') || '');
                                return a.includes('댓글') || a.includes('Comment');
                            });
                        if (svg) {
                            const target = svg.closest("button, [role='button']") || svg;
                            target.click();
                            return true;
                        }
                        return false;
                    }""")
                    if clicked:
                        logger.info("💬 [아우라 인스타] 댓글 아이콘 클릭(JS 폴백) ➔ 우측 댓글 서랍 개방")
                    return bool(clicked)
                except Exception as oe:
                    logger.warning(f"⚠️ [아우라 인스타] 댓글 아이콘 클릭 예외: {oe}")
                    return False

            async def _verify_comment_rendered() -> bool:
                """DOM 실물 검증: 댓글 목록 영역에 공식 검색어가 실제로 렌더링되었는지 확인한다."""
                try:
                    found = await page.evaluate("""(args) => {
                        const [listSel, keyword] = args;
                        const nodes = Array.from(document.querySelectorAll(listSel));
                        for (const n of nodes) {
                            if ((n.innerText || '').includes(keyword)) { return true; }
                        }
                        return false;
                    }""", [COMMENT_LIST_SEL, OFFICIAL_KEYWORD])
                    if found:
                        return True
                    # 2차: 댓글 리스트 컨테이너 전체 텍스트 검사
                    found2 = await page.evaluate("""(keyword) => {
                        const containers = Array.from(document.querySelectorAll(
                            "ul[class*='Comment'], div[class*='CommentList'], div[class*='X78zum5'] ul"
                        ));
                        for (const c of containers) {
                            if ((c.innerText || '').includes(keyword)) { return true; }
                        }
                        return false;
                    }""", OFFICIAL_KEYWORD)
                    return bool(found2)
                except Exception as ve:
                    logger.warning(f"⚠️ [아우라 인스타] 댓글 렌더링 검증 예외: {ve}")
                    return False

            try:
                logger.info(f"1. 인스타그램 프로필 접속: {PROFILE_URL}")
                await page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=40000)
                await asyncio.sleep(4.0)

                # 최신 릴스 탐색 (4초 단정 금지 — 최대 4회 폴링: 15초 대기 + 새로고침)
                reel_href = None
                for attempt in range(1, 5):
                    reel_link = page.locator("a[href*='/reel/'], a[href*='/p/']").first
                    try:
                        if await reel_link.count() > 0 and await reel_link.is_visible():
                            reel_href = await reel_link.get_attribute("href")
                            if reel_href:
                                logger.info(f"✅ [아우라 인스타] 최신 릴스 노출 확인 (시도 {attempt}/4): {reel_href}")
                                break
                    except Exception as le:
                        logger.debug(f"릴스 링크 탐색 예외(시도 {attempt}/4): {le}")

                    if attempt < 4:
                        logger.info(
                            f"⏳ [아우라 인스타] 최신 릴스 미노출 — 서버 배포 대기 후 재시도 "
                            f"({attempt}/4, 15초 대기 + 새로고침)"
                        )
                        await asyncio.sleep(15.0)
                        try:
                            await page.reload(wait_until="domcontentloaded", timeout=40000)
                        except Exception as re_err:
                            logger.debug(f"프로필 새로고침 예외: {re_err}")
                        await asyncio.sleep(4.0)

                if not reel_href:
                    logger.warning("릴스/게시물 링크를 4회 폴링 후에도 찾지 못했습니다.")
                    return {"status": "skipped", "message": "게시물 없음 (4회 폴링 실패)"}

                reel_url = f"https://www.instagram.com{reel_href}" if reel_href.startswith("/") else reel_href
                logger.info(f"2. 최신 릴스 상세 접속: {reel_url}")
                await page.goto(reel_url, wait_until="domcontentloaded", timeout=40000)
                await asyncio.sleep(4.0)

                # 중복 댓글 방지 검사 (Strict Deduplication Guard)
                existing_check = await page.evaluate("""(url) => {
                    const articles = Array.from(document.querySelectorAll("div[role='article'], ul ul"));
                    for (const art of articles) {
                        if (art.innerText.includes(url) || art.innerText.includes('아우라AI데이팅')) {
                            return true;
                        }
                    }
                    return false;
                }""", LANDING_URL)

                if existing_check:
                    logger.info("⚠️ 이미 아우라 공식 댓글이 존재합니다. 중복 방지 스킵.")
                    await page.screenshot(path=str(self.proof_img))
                    return {"status": "success", "message": "이미 등록됨 (중복 방지)", "verified": True}

                # 댓글 서랍 개방 ➔ 입력창 2중 탐색
                logger.info("3. 인스타그램 댓글 입력창 활성화 중...")
                comment_box = await _find_comment_box()
                if comment_box is None:
                    await _open_comment_drawer()
                    await asyncio.sleep(2.5)
                    comment_box = await _find_comment_box()

                if comment_box is None:
                    logger.warning("댓글 입력창이 비활성화되어 있거나 찾을 수 없습니다.")
                    return {"status": "failed", "message": "댓글창 미발견"}

                # 포커스/클릭
                try:
                    await comment_box.click()
                except Exception:
                    try:
                        await comment_box.evaluate("el => el.focus()")
                    except Exception:
                        pass
                await asyncio.sleep(0.8)

                # press_sequentially 로 줄바꿈(Shift+Enter) 포함 실제 키보드 이벤트 입력
                try:
                    await comment_box.press_sequentially(COMMENT_TEXT, delay=15)
                except Exception as te:
                    logger.warning(f"⚠️ [아우라 인스타] press_sequentially 실패 — 키보드 타이핑 폴백: {te}")
                    lines = COMMENT_TEXT.split("\n")
                    for i, line in enumerate(lines):
                        if line:
                            await page.keyboard.type(line, delay=15)
                        if i < len(lines) - 1:
                            await page.keyboard.down("Shift")
                            await page.keyboard.press("Enter")
                            await page.keyboard.up("Shift")
                            await asyncio.sleep(0.05)

                await asyncio.sleep(1.2)

                # [게시] 버튼 클릭 (3중 시도 ➔ Enter 폴백)
                posted = False
                post_btn = page.locator(
                    "div[role='button']:has-text('게시'), button:has-text('게시'), "
                    "div[role='button']:has-text('Post'), button:has-text('Post')"
                ).first
                try:
                    if await post_btn.count() > 0 and await post_btn.is_visible():
                        await post_btn.click()
                        posted = True
                        logger.info("🎉 [아우라 인스타] 공식 댓글 게시 버튼 클릭 완료!")
                except Exception as pe:
                    logger.warning(f"⚠️ [아우라 인스타] 게시 버튼 클릭 예외: {pe}")

                if not posted:
                    try:
                        posted = bool(await page.evaluate("""() => {
                            const btn = Array.from(document.querySelectorAll("div[role='button'], button"))
                                .find(el => {
                                    const t = (el.innerText || '').trim();
                                    return t === '게시' || t === 'Post';
                                });
                            if (btn) { btn.click(); return true; }
                            return false;
                        }"""))
                    except Exception:
                        posted = False

                if not posted:
                    await page.keyboard.press("Enter")
                    logger.info("↩️ [아우라 인스타] 게시 버튼 미발견 — Enter 키 전송 폴백 실행")

                # 4초 대기 후 DOM 실물 검증 (성공 위조 금지)
                await asyncio.sleep(4.0)
                verified = await _verify_comment_rendered()
                if not verified:
                    logger.info("⏳ [아우라 인스타] 댓글 미확인 — 2초 추가 대기 후 재검증...")
                    await asyncio.sleep(2.0)
                    verified = await _verify_comment_rendered()

                try:
                    await page.screenshot(path=str(self.proof_img))
                except Exception as se:
                    logger.warning(f"⚠️ [아우라 인스타] 증빙 스크린샷 저장 예외: {se}")

                if verified:
                    logger.info(f"✅ [성공] 아우라 인스타그램 단독 1개 댓글 등록 + DOM 실물 검증 통과: {self.proof_img}")
                    return {
                        "status": "success",
                        "brand": "aura",
                        "platform": "instagram",
                        "comment_text": COMMENT_TEXT,
                        "reel_url": reel_url,
                        "verified": True,
                        "proof": str(self.proof_img)
                    }

                logger.error("❌ [아우라 인스타] 게시 후에도 댓글이 DOM에 렌더링되지 않았습니다. (성공 위조 금지)")
                return {
                    "status": "unverified",
                    "brand": "aura",
                    "platform": "instagram",
                    "comment_text": COMMENT_TEXT,
                    "reel_url": reel_url,
                    "verified": False,
                    "message": "게시 후 댓글 DOM 렌더링 미확인 (6초 재검증 실패)",
                    "proof": str(self.proof_img)
                }

            except Exception as e:
                logger.error(f"❌ 아우라 인스타 댓글 오류: {e}")
                return {"status": "error", "message": str(e)}
            finally:
                await ctx.close()

    def post_comment_on_latest_reel(self) -> Dict[str, Any]:
        return asyncio.run(self.post_comment_on_latest_reel_async())


if __name__ == "__main__":
    c = AuraInstagramCommenter()
    res = c.post_comment_on_latest_reel()
    print("결과:", res)
