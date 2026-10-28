# -*- coding: utf-8 -*-
"""
📈 [StockMaster AI 전용] 틱톡 쇼츠 최신 영상 공식 URL 첫 댓글 등록기 (독립 레고 블록)
========================================================================
- 브랜드: 📈 StockMaster AI
- 공식 검색어: 스톡마스터 AI (띄어쓰기 불변)
- 공식 랜딩 URL: https://stockmaster-ai.vercel.app/
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

logger = logging.getLogger("StockTikTokCommenter")
if not logger.handlers:
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("[%(asctime)s] [StockTikTokCommenter] %(message)s"))
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
PROOF_IMG = CURRENT_DIR / "stock_tiktok_comment_proof.png"

TIKTOK_USER = "stockmaster_ai"
PROFILE_URL = f"https://www.tiktok.com/@{TIKTOK_USER}"
LANDING_URL = "https://stockmaster-ai.vercel.app/"
OFFICIAL_KEYWORD = "스톡마스터 AI"

COMMENT_TEXT = (
    f"📈 [StockMaster AI] 국내 우량주 350개 실시간 퀀트점수 무료 확인:\n"
    f"👉 {LANDING_URL}\n\n"
    f"🔍 네이버 검색창에 [{OFFICIAL_KEYWORD}]를 검색해보세요!\n"
    f"✨ 10분마다 갱신되는 국내 350개 종목의 AI 퀀트 점수와 세력 수급을 즉시 확인해 보세요!"
)


class StockTikTokCommenter:
    """📈 StockMaster AI 전용 틱톡 단독 댓글러 (독립 레고 블록)"""

    def __init__(self):
        self.brand = "stock"
        self.profile_dir = PROFILE_DIR
        self.session_file = SESSION_FILE
        self.proof_img = PROOF_IMG
        self.profile_url = PROFILE_URL
        self.landing_url = LANDING_URL
        self.official_keyword = OFFICIAL_KEYWORD
        self.comment_text = COMMENT_TEXT

    def post_comment_on_latest_video(self, video_url: Optional[str] = None) -> Dict[str, Any]:
        """동기 호출 인터페이스"""
        try:
            return asyncio.run(self.post_comment_async(video_url))
        except Exception as e:
            logger.error(f"❌ 스톡마스터 AI 틱톡 댓글 최종 예외: {e}")
            return {"status": "error", "message": str(e), "brand": self.brand}

    async def post_comment_on_page(self, page, video_url: Optional[str] = None) -> Dict[str, Any]:
        """
        [신규 분리] 이미 열려 있고 인증된 Playwright page 객체를 그대로 받아
        틱톡 최신 영상 첫 댓글 작성 시퀀스만 수행하는 재사용 레고 블록.

        - 브라우저 기동/컨텍스트 생성/락 획득/종료는 호출자(post_comment_async 등)가 담당
        - PROFILE_URL 방문 -> 최신 1등 영상 클릭 -> 중복 댓글 검사
          -> COMMENT_TEXT 타이핑(Shift+Enter 줄바꿈) -> [게시/Post] 클릭
          -> self.proof_img 스크린샷 캡처 후 결과 딕셔너리 반환
        """
        COMMENT_BOX_SEL = (
            "div[data-e2e='comment-input'], div.public-DraftEditor-content, "
            "div[contenteditable='true'], div[data-e2e='comment-input-area'] div[contenteditable='true']"
        )
        COMMENT_ITEM_SEL = (
            "div[data-e2e='comment-item'], div[data-e2e='comment-level-1'], "
            "p[data-e2e='comment-level-1'], div[class*='DivCommentItemContainer'], "
            "div[class*='DivCommentContentContainer']"
        )

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
            """댓글 서랍이 닫혀 있으면 댓글 아이콘을 클릭해 개방한다."""
            try:
                open_btn = page.locator(
                    "button[data-e2e='comment-icon'], [data-e2e='comment-icon'], "
                    "[aria-label*='댓글'], [aria-label*='Comment']"
                ).first
                if await open_btn.count() > 0 and await open_btn.is_visible():
                    await open_btn.click()
                    logger.info("💬 [스톡마스터 AI 틱톡] 댓글 아이콘 클릭 ➔ 댓글 서랍 개방")
                    return True
                clicked = await page.evaluate("""() => {
                    const btn = document.querySelector("button[data-e2e='comment-icon']") ||
                                document.querySelector("[data-e2e='comment-icon']") ||
                                Array.from(document.querySelectorAll('button, [role="button"]'))
                                    .find(el => {
                                        const a = (el.getAttribute('aria-label') || '');
                                        return a.includes('댓글') || a.includes('Comment');
                                    });
                    if (btn) { btn.click(); return true; }
                    return false;
                }""")
                if clicked:
                    logger.info("💬 [스톡마스터 AI 틱톡] 댓글 아이콘 클릭(JS 폴백) ➔ 댓글 서랍 개방")
                return bool(clicked)
            except Exception as oe:
                logger.warning(f"⚠️ [스톡마스터 AI 틱톡] 댓글 아이콘 클릭 예외: {oe}")
                return False

        async def _verify_comment_rendered() -> bool:
            """DOM 실물 검증: 댓글 목록에 공식 검색어가 실제로 렌더링되었는지 확인한다."""
            try:
                # 1차: 댓글 아이템 노드 내부 텍스트만 정밀 검사 (본문/설명란 오탐 차단)
                found = await page.evaluate("""(args) => {
                    const [itemSel, keyword] = args;
                    const nodes = Array.from(document.querySelectorAll(itemSel));
                    for (const n of nodes) {
                        const t = (n.innerText || '');
                        if (t.includes(keyword)) { return true; }
                    }
                    return false;
                }""", [COMMENT_ITEM_SEL, self.official_keyword])
                if found:
                    return True
                # 2차: 댓글 리스트 컨테이너 전체 텍스트 검사
                found2 = await page.evaluate("""(keyword) => {
                    const containers = Array.from(document.querySelectorAll(
                        "div[data-e2e='comment-list'], div[class*='DivCommentListContainer'], div[class*='CommentList']"
                    ));
                    for (const c of containers) {
                        if ((c.innerText || '').includes(keyword)) { return true; }
                    }
                    return false;
                }""", self.official_keyword)
                return bool(found2)
            except Exception as ve:
                logger.warning(f"⚠️ [스톡마스터 AI 틱톡] 댓글 렌더링 검증 예외: {ve}")
                return False

        try:
            target_url = video_url
            if not target_url:
                # ★ 섣부른 4초 단정 결함 절단:
                #   업로드 직후 틱톡 서버는 영상을 인코딩/배포하는 동안 프로필 그리드에
                #   해당 영상을 노출하지 않는다. 4초 한 번 보고 "게시물 없음"으로 단정하면
                #   무인 파이프라인이 100% 실패한다. 최대 4회(회당 15초 대기 + 새로고침)
                #   폴링으로 최신 영상이 실제 그리드에 뜰 때까지 끈기 있게 대기한다.
                logger.info(f"1. 틱톡 내 프로필 접속: {self.profile_url}")
                await page.goto(self.profile_url, wait_until="domcontentloaded", timeout=40000)
                await asyncio.sleep(4.0)

                href = None
                for attempt in range(1, 5):
                    video_link = page.locator("div[data-e2e='user-post-item'] a, a[href*='/video/']").first
                    try:
                        if await video_link.count() > 0 and await video_link.is_visible():
                            href = await video_link.get_attribute("href")
                            if href:
                                logger.info(f"✅ [스톡마스터 AI 틱톡] 최신 영상 노출 확인 (시도 {attempt}/4): {href}")
                                break
                    except Exception as le:
                        logger.debug(f"영상 링크 탐색 예외(시도 {attempt}/4): {le}")

                    if attempt < 4:
                        logger.info(
                            f"⏳ [스톡마스터 AI 틱톡] 최신 영상 미노출 — 서버 인코딩/배포 대기 후 재시도 "
                            f"({attempt}/4, 15초 대기 + 새로고침)"
                        )
                        await asyncio.sleep(15.0)
                        try:
                            await page.reload(wait_until="domcontentloaded", timeout=40000)
                        except Exception as re_err:
                            logger.debug(f"프로필 새로고침 예외: {re_err}")
                        await asyncio.sleep(4.0)

                if not href:
                    logger.warning("틱톡 프로필에서 4회 폴링 후에도 동영상 링크를 찾지 못했습니다.")
                    return {"status": "skipped", "message": "게시물 없음 (4회 폴링 실패)", "brand": self.brand}

                target_url = href if href.startswith("http") else f"https://www.tiktok.com{href}"

            logger.info(f"2. 틱톡 영상 상세 접속: {target_url}")
            await page.goto(target_url, wait_until="domcontentloaded", timeout=40000)
            await asyncio.sleep(4.0)

            # 중복 댓글 방지 검사
            body_text = await page.inner_text("body")
            if self.landing_url in body_text or self.official_keyword in body_text:
                logger.info("ℹ️ 이미 공식 URL 또는 검색어 댓글이 등록되어 있습니다. (도배 방지 스킵)")
                return {"status": "already_commented", "message": "중복 댓글 방지 스킵", "brand": self.brand}

            # 댓글 입력창 탐색 (닫혀 있으면 댓글 아이콘 클릭하여 서랍 개방)
            logger.info("3. 틱톡 댓글 입력창 활성화 중...")
            comment_box = await _find_comment_box()
            if comment_box is None:
                await _open_comment_drawer()
                await asyncio.sleep(2.5)
                comment_box = await _find_comment_box()

            if comment_box is None:
                logger.warning("틱톡 댓글 입력창을 찾지 못했습니다.")
                return {"status": "error", "message": "댓글 입력창 미발견", "brand": self.brand, "platform": "tiktok"}

            # 댓글 본문 타이핑 (press_sequentially + Shift+Enter 줄바꿈)
            try:
                await comment_box.click()
            except Exception:
                try:
                    await comment_box.evaluate("el => el.focus()")
                except Exception:
                    pass
            await asyncio.sleep(1.0)

            try:
                await comment_box.press_sequentially(self.comment_text, delay=12)
            except Exception as te:
                logger.warning(f"⚠️ [스톡마스터 AI 틱톡] press_sequentially 실패 — 키보드 타이핑 폴백: {te}")
                for char in self.comment_text:
                    if char == "\n":
                        await page.keyboard.press("Shift+Enter")
                    else:
                        await page.keyboard.type(char)
                    await asyncio.sleep(0.01)

            await asyncio.sleep(1.5)

            # [게시/Post] 버튼 확실히 클릭
            posted = False
            post_btn = page.locator(
                "div[data-e2e='comment-post'], button[data-e2e='comment-post'], "
                "button:has-text('게시'), button:has-text('Post')"
            ).first
            try:
                if await post_btn.count() > 0 and await post_btn.is_visible():
                    await post_btn.click()
                    posted = True
                    logger.info("🎉 [스톡마스터 AI 틱톡] 공식 URL 첫 댓글 게시 버튼 클릭 완료!")
            except Exception as pe:
                logger.warning(f"⚠️ [스톡마스터 AI 틱톡] 게시 버튼 클릭 예외: {pe}")

            if not posted:
                try:
                    posted = bool(await page.evaluate("""() => {
                        const btn = document.querySelector("div[data-e2e='comment-post']") ||
                                    document.querySelector("button[data-e2e='comment-post']") ||
                                    Array.from(document.querySelectorAll('button, div[role="button"]'))
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
                # 엔터 키 폴백
                await page.keyboard.press("Enter")
                logger.info("↩️ [스톡마스터 AI 틱톡] 게시 버튼 미발견 — 엔터 키 전송 폴백 실행")

            # 4초 대기 후 DOM 실물 검증 (성공 위조 금지)
            await asyncio.sleep(4.0)
            verified = await _verify_comment_rendered()
            if not verified:
                logger.info("⏳ [스톡마스터 AI 틱톡] 댓글 미확인 — 2초 추가 대기 후 재검증...")
                await asyncio.sleep(2.0)
                verified = await _verify_comment_rendered()

            try:
                await page.screenshot(path=str(self.proof_img))
            except Exception as se:
                logger.warning(f"⚠️ [스톡마스터 AI 틱톡] 증빙 스크린샷 저장 예외: {se}")

            if verified:
                logger.info("✅ [스톡마스터 AI 틱톡] 댓글 DOM 실물 검증 통과 — 공식 검색어 렌더링 확인!")
                return {
                    "status": "success",
                    "brand": self.brand,
                    "platform": "tiktok",
                    "comment_text": self.comment_text,
                    "video_url": target_url,
                    "verified": True,
                    "proof_screenshot": str(self.proof_img)
                }

            logger.error("❌ [스톡마스터 AI 틱톡] 게시 클릭 후에도 댓글이 DOM에 렌더링되지 않았습니다. (성공 위조 금지)")
            return {
                "status": "unverified",
                "brand": self.brand,
                "platform": "tiktok",
                "comment_text": self.comment_text,
                "video_url": target_url,
                "verified": False,
                "message": "게시 클릭 후 댓글 DOM 렌더링 미확인 (6초 재검증 실패)",
                "proof_screenshot": str(self.proof_img)
            }

        except Exception as e:
            logger.error(f"❌ [스톡마스터 AI 틱톡] page 기반 댓글 작성 중 예외: {e}")
            return {"status": "error", "message": str(e), "brand": self.brand, "platform": "tiktok"}

    async def post_comment_async(self, video_url: Optional[str] = None) -> Dict[str, Any]:
        """비동기 틱톡 최신 영상 첫 댓글 자동 작성 (브라우저 기동 후 page 시퀀스에 위임)"""
        clean_browser_profile_locks(self.profile_dir)

        async with async_browser_lock("스톡마스터 AI 틱톡 첫 댓글 작성", timeout_sec=300):
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
                    # 실제 댓글 작성 시퀀스는 page 기반 레고 블록에 100% 위임 (중복 제거)
                    return await self.post_comment_on_page(page, video_url)
                finally:
                    await context.close()


if __name__ == "__main__":
    commenter = StockTikTokCommenter()
    print("Brand:", commenter.brand)
    print("Profile URL:", commenter.profile_url)
    print("Landing URL:", commenter.landing_url)
    print("Official Keyword:", commenter.official_keyword)
    print("Proof:", commenter.proof_img)
    print("Commenter initialized:", commenter)
