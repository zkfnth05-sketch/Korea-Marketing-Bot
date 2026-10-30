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
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
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

# ---------- 중앙화된 시간/재시도 정책 (단일 진실원) ----------
TIMEOUTS = {
    "page_nav_ms": 40000,
    "reel_link_ms": 10000,
    "drawer_open_poll_ms": 8000,     # 열림 확정 폴링 상한
    "drawer_poll_interval_ms": 250,
    "comment_box_ms": 8000,
    "trigger_visible_ms": 5000,
    "post_submit_settle_ms": 5000,
    "global_hard_cap_s": 180,        # 전체 실행 전역 상한 (서킷브레이커)
}
RETRY_LIMITS = {
    "open_strategies": 3,            # 열기 전략 재시도 한도
    "find_box_attempts": 2,
}
HEARTBEAT_INTERVAL_S = 15.0

# ---------- 예외 분류 스키마 ----------
class FailureKind:
    ELEMENT_MISSING = "element_missing"
    OBSCURED = "obscured"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"

def _classify_exc(e: Exception) -> str:
    msg = str(e).lower()
    if "timeout" in msg:
        return FailureKind.TIMEOUT
    if "intercept" in msg or "obscur" in msg or "not visible" in msg:
        return FailureKind.OBSCURED
    if "no element" in msg or "not found" in msg or "no node" in msg:
        return FailureKind.ELEMENT_MISSING
    return FailureKind.UNKNOWN


class StockInstagramCommenter:
    """📈 스톡마스터 AI 전용 인스타그램 단독 댓글러 (독립 레고 블록)"""

    def __init__(self):
        self.profile_dir = PROFILE_DIR
        self.session_file = SESSION_FILE
        self.proof_img = PROOF_IMG
        self._started_at: float = 0.0
        self._last_heartbeat: float = 0.0
        self._failure_log: List[Dict[str, Any]] = []

    # ---------- 상태 판정 (단일 술어, 액션과 분리) ----------

    async def _is_drawer_open(self, page) -> bool:
        """서랍 열림 확정: 편집기 가시성 OR 댓글 목록 컨테이너 존재 (복합 신호)."""
        try:
            return await page.evaluate(
                """() => {
                    const edit = document.querySelector(
                        "textarea[aria-label*='댓글'], textarea[aria-label*='comment' i], " +
                        "textarea[placeholder*='댓글'], textarea[placeholder*='comment' i], " +
                        "div[role='textbox'][contenteditable='true']"
                    );
                    if (edit && edit.offsetParent !== null) return true;
                    const list = document.querySelector("ul ul, div[role='article']");
                    return !!(list && list.offsetParent !== null);
                }"""
            )
        except Exception as e:
            self._record_failure("is_drawer_open", _classify_exc(e), str(e))
            return False

    async def _poll_drawer_open(self, page, timeout_ms: int) -> bool:
        """열림 확정을 폴링. 단일 술어만 사용."""
        deadline = time.monotonic() + (timeout_ms / 1000.0)
        while time.monotonic() < deadline:
            if await self._is_drawer_open(page):
                return True
            await asyncio.sleep(TIMEOUTS["drawer_poll_interval_ms"] / 1000.0)
        return False

    def _record_failure(self, stage: str, kind: str, detail: str) -> None:
        self._failure_log.append({"stage": stage, "kind": kind, "detail": detail[:200]})
        logger.warning(f"   - [실패분류] stage={stage} kind={kind} detail={detail[:120]}")

    def _heartbeat(self, tag: str) -> None:
        now = time.monotonic()
        if now - self._last_heartbeat >= HEARTBEAT_INTERVAL_S:
            self._last_heartbeat = now
            logger.info(f"   ♥ heartbeat [{tag}] elapsed={now - self._started_at:.1f}s")

    def _check_global_cap(self) -> bool:
        """서킷브레이커: 전역 상한 초과 시 중단."""
        if time.monotonic() - self._started_at > TIMEOUTS["global_hard_cap_s"]:
            logger.error("   ⛔ 전역 상한 초과 - 서킷브레이커 작동")
            return False
        return True

    # ---------- 액션 전략 계층 (데이터화) ----------

    def _open_strategies(self) -> List[Dict[str, Any]]:
        """트리거 해석 전략 목록 (데이터). 상위 클릭 우선 → 좌표 폴백."""
        return [
            {"name": "role_button_comment", "kind": "role_click", "label": "Comment"},
            {"name": "role_button_korean", "kind": "role_click", "label": "댓글"},
            {"name": "svg_parent_click", "kind": "svg_parent_click"},
            {"name": "coord_fallback", "kind": "coord_click"},
        ]

    async def _apply_strategy(self, page, strategy: Dict[str, Any]) -> bool:
        """단일 전략 실행. 예외는 분류해 기록하고 False 반환."""
        try:
            kind = strategy["kind"]
            if kind == "role_click":
                loc = page.get_by_role("button", name=strategy["label"]).first
                await loc.wait_for(state="visible", timeout=TIMEOUTS["trigger_visible_ms"])
                await loc.click(timeout=TIMEOUTS["trigger_visible_ms"])
                return True
            if kind == "svg_parent_click":
                svg = page.locator("svg[aria-label*='Comment'], svg[aria-label*='댓글']").first
                await svg.wait_for(state="visible", timeout=TIMEOUTS["trigger_visible_ms"])
                handle = await svg.element_handle()
                if handle is None:
                    self._record_failure(strategy["name"], FailureKind.ELEMENT_MISSING, "svg handle null")
                    return False
                parent = await handle.evaluate_handle("el => el.closest('button, [role=\"button\"], div')")
                el = parent.as_element()
                if el is None:
                    self._record_failure(strategy["name"], FailureKind.ELEMENT_MISSING, "parent null")
                    return False
                await el.click(timeout=TIMEOUTS["trigger_visible_ms"])
                return True
            if kind == "coord_click":
                svg = page.locator("svg[aria-label*='Comment'], svg[aria-label*='댓글']").first
                await svg.wait_for(state="visible", timeout=TIMEOUTS["trigger_visible_ms"])
                box = await svg.bounding_box()
                if not box:
                    self._record_failure(strategy["name"], FailureKind.ELEMENT_MISSING, "bbox null")
                    return False
                await page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                return True
            self._record_failure(strategy["name"], FailureKind.UNKNOWN, f"unknown kind={kind}")
            return False
        except Exception as e:
            self._record_failure(strategy["name"], _classify_exc(e), str(e))
            return False

    async def _open_comment_drawer(self, page) -> bool:
        """오케스트레이션: 스냅샷 → 전략 실행 → 폴링 재검증. 오탐 시 False."""
        if await self._is_drawer_open(page):
            logger.info("   - 댓글 서랍이 이미 열려 있음 (판정 확정)")
            return True

        strategies = self._open_strategies()
        attempts = 0
        for strategy in strategies:
            if attempts >= RETRY_LIMITS["open_strategies"]:
                logger.warning("   - 열기 전략 재시도 한도 도달")
                break
            if not self._check_global_cap():
                return False
            attempts += 1
            self._heartbeat("open_drawer")
            logger.info(f"   - 열기 전략 시도: {strategy['name']}")
            clicked = await self._apply_strategy(page, strategy)
            if not clicked:
                continue
            # 클릭 후 폴링 재검증 (오탐 방지 게이트)
            if await self._poll_drawer_open(page, TIMEOUTS["drawer_open_poll_ms"]):
                logger.info(f"   - 서랍 열림 확정: {strategy['name']}")
                return True
            logger.warning(f"   - 클릭 후 열림 미확정: {strategy['name']}")

        logger.warning("   - 모든 열기 전략 실패 (열림 미확정)")
        return False

    async def _find_comment_box(self, page, timeout_ms: int = 8000):
        """입력창 해석. 예외는 분류 기록. 핸들 반환."""
        candidates = [
            "textarea[aria-label*='댓글']",
            "textarea[aria-label*='comment' i]",
            "textarea[placeholder*='댓글']",
            "textarea[placeholder*='comment' i]",
            "div[role='textbox'][contenteditable='true']",
            "textarea",
        ]
        for sel in candidates:
            try:
                loc = page.locator(sel).first
                await loc.wait_for(state="visible", timeout=timeout_ms)
                handle = await loc.element_handle()
                if handle is not None:
                    logger.info(f"   - 입력창 확보: {sel}")
                    return handle
            except Exception as e:
                self._record_failure(f"find_box:{sel}", _classify_exc(e), str(e))

        try:
            handle = await page.evaluate_handle(
                """() => {
                    const sels = ["textarea[aria-label*='댓글']","textarea[aria-label*='comment' i]",
                                  "textarea[placeholder*='댓글']","textarea[placeholder*='comment' i]",
                                  "div[role='textbox'][contenteditable='true']","textarea"];
                    for (const s of sels) {
                        const el = document.querySelector(s);
                        if (el && el.offsetParent !== null) return el;
                    }
                    return null;
                }"""
            )
            el = handle.as_element()
            if el is not None:
                logger.info("   - 입력창 확보: evaluate_handle 폴백")
                return el
        except Exception as e:
            self._record_failure("find_box:evaluate", _classify_exc(e), str(e))
        return None

    async def _is_already_commented(self, page) -> bool:
        """서랍이 열린 상태에서만 호출. 기존 댓글 존재 여부 검사."""
        try:
            return await page.evaluate(
                """(url) => {
                    const articles = Array.from(document.querySelectorAll("div[role='article'], ul ul"));
                    for (const art of articles) {
                        const t = art.innerText || "";
                        if (t.includes(url) || t.includes('스톡마스터 AI')) return true;
                    }
                    return false;
                }""",
                LANDING_URL,
            )
        except Exception as e:
            self._record_failure("dedup", _classify_exc(e), str(e))
            logger.warning(f"   - dedup 검사 예외(보수적 true 반환): {e}")
            return True  # 검사 실패 시 중복 방지 우선

    async def _type_and_submit(self, page, box_handle) -> bool:
        """입력창에 댓글 작성 후 Enter 제출."""
        try:
            await box_handle.click()
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
            await asyncio.sleep(TIMEOUTS["post_submit_settle_ms"] / 1000.0)
            return True
        except Exception as e:
            self._record_failure("type_submit", _classify_exc(e), str(e))
            logger.error(f"   - 입력/제출 실패: {e}")
            return False

    # ---------- 오케스트레이션 (상태 머신) ----------

    async def post_comment_on_latest_reel_async(self) -> Dict[str, Any]:
        clean_browser_profile_locks(self.profile_dir)
        self._started_at = time.monotonic()
        self._last_heartbeat = self._started_at
        self._failure_log = []

        async with async_playwright() as p:
            ctx = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
                viewport={"width": 1280, "height": 900}
            )
            page = ctx.pages[0] if ctx.pages else await ctx.new_page()

            try:
                if not self._check_global_cap():
                    return {"status": "aborted", "message": "전역 상한 초과", "failures": self._failure_log}

                logger.info(f"1. 인스타그램 프로필 접속: {PROFILE_URL}")
                await page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=TIMEOUTS["page_nav_ms"])
                await asyncio.sleep(4.0)
                self._heartbeat("profile_loaded")

                reel_link = page.locator("a[href*='/reel/'], a[href*='/p/']").first
                try:
                    await reel_link.wait_for(state="visible", timeout=TIMEOUTS["reel_link_ms"])
                except Exception as e:
                    self._record_failure("reel_link", _classify_exc(e), str(e))
                    logger.warning("릴스/게시물 링크를 찾지 못했습니다.")
                    return {"status": "skipped", "message": "게시물 없음", "failures": self._failure_log}

                reel_href = await reel_link.get_attribute("href")
                reel_url = f"https://www.instagram.com{reel_href}" if reel_href.startswith("/") else reel_href
                logger.info(f"2. 최신 릴스 상세 접속: {reel_url}")
                await page.goto(reel_url, wait_until="domcontentloaded", timeout=TIMEOUTS["page_nav_ms"])
                await asyncio.sleep(4.0)
                self._heartbeat("reel_loaded")

                # [상태 1] 댓글 서랍 열기 (열림 확정 게이트)
                logger.info("3. 댓글 서랍 열기 시도")
                if not await self._open_comment_drawer(page):
                    await page.screenshot(path=str(self.proof_img))
                    return {"status": "failed", "message": "댓글 서랍 열기 실패(열림 미확정)",
                            "failures": self._failure_log}

                # [상태 2] 열림 확정 후에만 dedup 검사 (오탐 게이트)
                logger.info("4. 중복 댓글 검사 (서랍 열린 상태)")
                if await self._is_already_commented(page):
                    logger.info("⚠️ 이미 공식 댓글이 존재합니다. 중복 방지 스킵.")
                    await page.screenshot(path=str(self.proof_img))
                    return {"status": "success", "message": "이미 등록됨 (중복 방지)",
                            "failures": self._failure_log}

                # [상태 3] 입력창 확보 (재시도 한도)
                logger.info("5. 댓글 입력창 확보")
                box_handle = None
                for attempt in range(RETRY_LIMITS["find_box_attempts"]):
                    if not self._check_global_cap():
                        return {"status": "aborted", "message": "전역 상한 초과",
                                "failures": self._failure_log}
                    box_handle = await self._find_comment_box(page, timeout_ms=TIMEOUTS["comment_box_ms"])
                    if box_handle is not None:
                        break
                    logger.warning(f"   - 입력창 재시도 {attempt + 1}/{RETRY_LIMITS['find_box_attempts']}")
                if box_handle is None:
                    await page.screenshot(path=str(self.proof_img))
                    return {"status": "failed", "message": "댓글창 미발견", "failures": self._failure_log}

                # [상태 4] 작성 및 제출
                logger.info("6. 댓글 작성 및 제출")
                if not await self._type_and_submit(page, box_handle):
                    await page.screenshot(path=str(self.proof_img))
                    return {"status": "failed", "message": "댓글 작성/제출 실패",
                            "failures": self._failure_log}

                await page.screenshot(path=str(self.proof_img))
                logger.info(f"🎉 [성공] 스톡마스터 AI 인스타그램 단독 1개 댓글 등록 완료: {self.proof_img}")
                return {"status": "success", "proof": str(self.proof_img), "failures": self._failure_log}

            except Exception as e:
                self._record_failure("orchestration", _classify_exc(e), str(e))
                logger.error(f"❌ 스톡마스터 AI 인스타 댓글 오류: {e}")
                return {"status": "error", "message": str(e), "failures": self._failure_log}
            finally:
                # 좀비 방지: 페이지/컨텍스트 명시적 정리
                try:
                    await page.close()
                except Exception as ce:
                    logger.warning(f"   - 페이지 정리 경고: {ce}")
                try:
                    await ctx.close()
                except Exception as ce:
                    logger.warning(f"   - 컨텍스트 정리 경고: {ce}")

    def post_comment_on_latest_reel(self) -> Dict[str, Any]:
        return asyncio.run(self.post_comment_on_latest_reel_async())


if __name__ == "__main__":
    c = StockInstagramCommenter()
    res = c.post_comment_on_latest_reel()
    print("결과:", res)
