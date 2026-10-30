# -*- coding: utf-8 -*-
"""
🛡️ [보험 리밸런스 전용] 인스타그램 릴스 최신글 단독 1개 첫 댓글 등록 모듈 (독립 레고 블록)
========================================================================================
- 브랜드: 🛡️ 보험 리밸런스
- 인스타 계정: @goldmomofficial
- 공식 키워드: 보험 리밸런스
- 공식 랜딩 URL: https://insure-rebalance.vercel.app/
- 안전 원칙: 중복 도배 방지 (0개 확인 후 단 1개만 작성), 전용 프로필 격리
- 구조 원칙: 상태머신 4단계 분리 (drawer_open → locate → input → verify)
========================================================================================
"""
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Page, TimeoutError as PWTimeoutError

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logger = logging.getLogger("InsuranceInstaCommenter")
if not logger.handlers:
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("[%(asctime)s] [InsuranceInstaCommenter] %(message)s"))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine.browser_guard import clean_browser_profile_locks

PROFILE_DIR = CURRENT_DIR / "instagram_chrome_profile"
SESSION_FILE = CURRENT_DIR / "instagram_session.json"
PROOF_IMG = CURRENT_DIR / "insurance_instagram_comment_proof.png"

INSTA_USERNAME = "goldmomofficial"
PROFILE_URL = f"https://www.instagram.com/{INSTA_USERNAME}/"
LANDING_URL = "https://insure-rebalance.vercel.app/"
OFFICIAL_KEYWORD = "보험 리밸런스"

COMMENT_TEXT = (
    f"🛡️ [보험 리밸런스] 과다 청구 보험료 & 숨은 환급금 3초 정밀 진단:\n"
    f"👉 {LANDING_URL}\n\n"
    f"🔍 네이버 검색창에 [{OFFICIAL_KEYWORD}]를 검색해보세요!\n"
    f"✨ 불필요한 특약은 줄이고 보장은 든든하게 무료 리밸런싱 받아보세요!"
)

# ── 상태머신 상수 ──────────────────────────────────────────────────────────
STAGE_DRAWER = "ensure_drawer_open"
STAGE_LOCATE = "locate_editor"
STAGE_INPUT = "input_comment"
STAGE_VERIFY = "verify_submission"

# 상태 열거형 (문자열 상수로 유지 — 로그/결과 직렬화 용이)
DRAWER_OPEN = "OPEN"
DRAWER_CLOSED = "CLOSED"
DRAWER_UNKNOWN = "UNKNOWN"

DRAWER_OPEN_TIMEOUT_MS = 8000
EDITOR_WAIT_TIMEOUT_MS = 6000
VERIFY_WAIT_TIMEOUT_MS = 6000
GLOBAL_FLOW_TIMEOUT_SEC = 120

# ── 무인 가동 안전장치 상수 ────────────────────────────────────────────────
MAX_DRAWER_ATTEMPTS = 2          # 서랍 열기 시도 총량 상한 (토글 진동 차단)
STATE_POLL_INTERVAL_SEC = 0.3    # 상태 폴링 주기
STATE_STABLE_REPEAT_LIMIT = 3    # 동일 상태 N회 반복 시 진동으로 간주
BACKOFF_BASE_SEC = 0.5           # 재시도 지수 백오프 기준
BACKOFF_MAX_SEC = 4.0            # 재시도 지수 백오프 상한

# 댓글 서랍 열기 트리거 (부모 인터랙티브 요소 우선 — svg 직접 클릭 미스 방지)
DRAWER_TRIGGER_SELECTORS = [
    "div[role='button']:has(svg[aria-label='댓글'])",
    "div[role='button']:has(svg[aria-label='Comment'])",
    "button[aria-label*='댓글']",
    "button[aria-label*='Comment']",
    "svg[aria-label='댓글']",
    "svg[aria-label='Comment']",
]

# 댓글 서랍 컨테이너 (열림 판정용 — 모달 + 릴스 인라인 컬럼 모두 포함)
DRAWER_CONTAINER_SELECTORS = [
    "div[role='dialog']",
    "div[aria-label*='댓글']",
    "div[aria-label*='Comment']",
    # 릴스 데스크톱 인라인 댓글 컬럼 (모달 아님)
    "div[role='complementary']",
    "section:has(div[role='textbox'][contenteditable='true'])",
]

# 댓글 에디터 후보 (역할/aria 우선)
EDITOR_SELECTORS = [
    "div[role='textbox'][contenteditable='true']",
    "textarea[aria-label*='댓글']",
    "textarea[aria-label*='Comment']",
    "textarea[placeholder*='댓글']",
    "textarea[placeholder*='Comment']",
]


class InsuranceInstagramCommenter:
    """🛡️ 보험 리밸런스 전용 인스타그램 단독 댓글러 (독립 레고 블록)"""

    def __init__(self):
        self.profile_dir = PROFILE_DIR
        self.session_file = SESSION_FILE
        self.proof_img = PROOF_IMG

    # ── 결과 객체 헬퍼 ────────────────────────────────────────────────────
    @staticmethod
    def _result(status: str, stage: str, message: str = "", **extra) -> Dict[str, Any]:
        payload = {"status": status, "stage": stage, "message": message}
        payload.update(extra)
        return payload

    # ── 관찰(Observation) — 상태 판정 전용, 부작용 없음 ────────────────────
    async def _observe_drawer_state(self, page: Page) -> str:
        """서랍 상태를 관찰만 한다. 클릭/입력 등 부작용 없음.

        OPEN 신호: 컨테이너 셀렉터 매칭 OR 에디터 가시.
        CLOSED 신호: 컨테이너 미매칭 AND 에디터 미가시 AND 트리거 가시.
        그 외: UNKNOWN.
        """
        # 1) 컨테이너 신호
        for sel in DRAWER_CONTAINER_SELECTORS:
            try:
                if await page.locator(sel).first.is_visible():
                    return DRAWER_OPEN
            except Exception:
                continue

        # 2) 에디터 신호 (모달이 아닌 인라인 컬럼 대응)
        for sel in EDITOR_SELECTORS:
            try:
                if await page.locator(sel).first.is_visible():
                    return DRAWER_OPEN
            except Exception:
                continue

        # 3) 트리거 가시 → 닫힘으로 간주
        for sel in DRAWER_TRIGGER_SELECTORS:
            try:
                if await page.locator(sel).first.is_visible():
                    return DRAWER_CLOSED
            except Exception:
                continue

        return DRAWER_UNKNOWN

    async def _wait_drawer_state(self, page: Page, target: str, timeout_ms: int) -> bool:
        """target 상태가 될 때까지 폴링. 진동 감지 시 조기 종료."""
        deadline = asyncio.get_event_loop().time() + (timeout_ms / 1000)
        last_state: Optional[str] = None
        repeat = 0
        while asyncio.get_event_loop().time() < deadline:
            state = await self._observe_drawer_state(page)
            if state == target:
                return True
            if state == last_state:
                repeat += 1
                if repeat >= STATE_STABLE_REPEAT_LIMIT and state == DRAWER_UNKNOWN:
                    logger.warning(f"[{STAGE_DRAWER}] 상태 진동/미확정({state}) → 조기 종료")
                    return False
            else:
                last_state = state
                repeat = 0
            await asyncio.sleep(STATE_POLL_INTERVAL_SEC)
        return False

    # ── 동작(Action) — 멱등 트리거 ────────────────────────────────────────
    async def _click_drawer_trigger_once(self, page: Page) -> bool:
        """트리거를 정확히 1회만 클릭. 성공 시 True."""
        for sel in DRAWER_TRIGGER_SELECTORS:
            try:
                trigger = page.locator(sel).first
                if await trigger.is_visible():
                    await trigger.click(timeout=3000)
                    logger.info(f"[{STAGE_DRAWER}] 트리거 클릭(1회): {sel}")
                    return True
            except Exception as e:
                logger.debug(f"[{STAGE_DRAWER}] 트리거 시도 실패 {sel}: {e}")
                continue
        logger.warning(f"[{STAGE_DRAWER}] 트리거 후보 전부 미가시")
        return False

    # ── STAGE 1: 댓글 서랍 열기 (관찰→전이→재관찰, 멱등) ──────────────────
    async def _ensure_drawer_open(self, page: Page) -> bool:
        # 1) 초기 관찰
        state = await self._observe_drawer_state(page)
        logger.info(f"[{STAGE_DRAWER}] 초기 상태: {state}")
        if state == DRAWER_OPEN:
            return True
        if state == DRAWER_UNKNOWN:
            # 관찰 유예 후 재판정 (페이지 렌더 지연 흡수)
            if await self._wait_drawer_state(page, DRAWER_OPEN, timeout_ms=2000):
                return True
            state = await self._observe_drawer_state(page)
            if state == DRAWER_UNKNOWN:
                logger.warning(f"[{STAGE_DRAWER}] 초기 상태 미확정 → 중단(블라인드 클릭 금지)")
                return False

        # 2) CLOSED 확정 → 제한된 재시도로 멱등 전이
        for attempt in range(1, MAX_DRAWER_ATTEMPTS + 1):
            if not await self._click_drawer_trigger_once(page):
                return False
            if await self._wait_drawer_state(page, DRAWER_OPEN, DRAWER_OPEN_TIMEOUT_MS):
                logger.info(f"[{STAGE_DRAWER}] 서랍 열림 확인 (attempt={attempt})")
                return True
            # 열리지 않음 → 상태 재관찰 후 재시도 여부 결정
            state = await self._observe_drawer_state(page)
            logger.warning(f"[{STAGE_DRAWER}] 열림 미확인 (attempt={attempt}, state={state})")
            if state == DRAWER_OPEN:
                return True
            if attempt < MAX_DRAWER_ATTEMPTS:
                backoff = min(BACKOFF_BASE_SEC * (2 ** (attempt - 1)), BACKOFF_MAX_SEC)
                await asyncio.sleep(backoff)

        logger.warning(f"[{STAGE_DRAWER}] 재시도 총량({MAX_DRAWER_ATTEMPTS}) 소진 → 실패")
        return False

    # ── STAGE 2: 에디터 탐색 ──────────────────────────────────────────────
    async def _locate_editor(self, page: Page):
        for sel in EDITOR_SELECTORS:
            try:
                loc = page.locator(sel).first
                await loc.wait_for(state="visible", timeout=EDITOR_WAIT_TIMEOUT_MS)
                logger.info(f"[{STAGE_LOCATE}] 에디터 발견: {sel}")
                return loc
            except PWTimeoutError:
                continue
            except Exception:
                continue
        logger.warning(f"[{STAGE_LOCATE}] 에디터 후보 전부 실패")
        return None

    # ── STAGE 3: 입력 ─────────────────────────────────────────────────────
    async def _input_comment(self, page: Page, editor) -> bool:
        try:
            await editor.click(timeout=3000)
            await asyncio.sleep(0.3)
            # 엘리먼트 스코프 입력 (전역 키보드 의존 제거)
            try:
                await editor.fill(COMMENT_TEXT, timeout=5000)
            except Exception:
                # contenteditable 폴백: 개행 유지 위해 insert_text
                await editor.press_sequentially(COMMENT_TEXT, delay=10, timeout=10000)
            await asyncio.sleep(0.5)
            await editor.press("Enter")
            logger.info(f"[{STAGE_INPUT}] 입력 및 전송 완료")
            return True
        except Exception as e:
            logger.error(f"[{STAGE_INPUT}] 입력 실패: {e}")
            return False

    # ── STAGE 4: 검증 ─────────────────────────────────────────────────────
    async def _verify_submission(self, page: Page) -> bool:
        deadline = asyncio.get_event_loop().time() + (VERIFY_WAIT_TIMEOUT_MS / 1000)
        while asyncio.get_event_loop().time() < deadline:
            try:
                found = await page.evaluate(
                    """(kw) => {
                        const arts = Array.from(document.querySelectorAll("div[role='article'], ul ul"));
                        return arts.some(a => a.innerText && a.innerText.includes(kw));
                    }""",
                    OFFICIAL_KEYWORD,
                )
                if found:
                    logger.info(f"[{STAGE_VERIFY}] 게시 확인: '{OFFICIAL_KEYWORD}'")
                    return True
            except Exception:
                pass
            await asyncio.sleep(0.5)
        logger.warning(f"[{STAGE_VERIFY}] 게시 검증 실패")
        return False

    # ── 중복 가드 (서랍 열린 뒤 실행) ─────────────────────────────────────
    async def _has_existing_comment(self, page: Page) -> bool:
        try:
            return await page.evaluate(
                """(url) => {
                    const arts = Array.from(document.querySelectorAll("div[role='article'], ul ul"));
                    return arts.some(a => a.innerText && (a.innerText.includes(url) || a.innerText.includes('보험 리밸런스')));
                }""",
                LANDING_URL,
            )
        except Exception:
            return False

    # ── 메인 플로우 ───────────────────────────────────────────────────────
    async def _run_flow(self) -> Dict[str, Any]:
        clean_browser_profile_locks(self.profile_dir)

        async with async_playwright() as p:
            ctx = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
                viewport={"width": 1280, "height": 900},
            )
            page = ctx.pages[0] if ctx.pages else await ctx.new_page()

            try:
                logger.info(f"1. 프로필 접속: {PROFILE_URL}")
                await page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=40000)
                await asyncio.sleep(3.0)

                reel_link = page.locator("a[href*='/reel/'], a[href*='/p/']").first
                if not await reel_link.is_visible():
                    return self._result("skipped", "discover_reel", "게시물 없음")

                reel_href = await reel_link.get_attribute("href")
                reel_url = f"https://www.instagram.com{reel_href}" if reel_href.startswith("/") else reel_href
                logger.info(f"2. 릴스 접속: {reel_url}")
                await page.goto(reel_url, wait_until="domcontentloaded", timeout=40000)
                await asyncio.sleep(3.0)

                # STAGE 1
                if not await self._ensure_drawer_open(page):
                    await page.screenshot(path=str(self.proof_img))
                    return self._result("failed", STAGE_DRAWER, "댓글 서랍 열기 실패")

                # 중복 가드 (서랍 열린 뒤)
                if await self._has_existing_comment(page):
                    logger.info("⚠️ 기존 댓글 존재 → 중복 방지 스킵")
                    await page.screenshot(path=str(self.proof_img))
                    return self._result("success", "dedup_guard", "이미 등록됨", proof=str(self.proof_img))

                # STAGE 2
                editor = await self._locate_editor(page)
                if editor is None:
                    await page.screenshot(path=str(self.proof_img))
                    return self._result("failed", STAGE_LOCATE, "에디터 미발견")

                # STAGE 3
                if not await self._input_comment(page, editor):
                    await page.screenshot(path=str(self.proof_img))
                    return self._result("failed", STAGE_INPUT, "입력 실패")

                # STAGE 4
                await asyncio.sleep(2.0)
                verified = await self._verify_submission(page)
                await page.screenshot(path=str(self.proof_img))

                if verified:
                    logger.info(f"🎉 [성공] 댓글 등록 검증 완료: {self.proof_img}")
                    return self._result("success", STAGE_VERIFY, "게시 확인", proof=str(self.proof_img))
                return self._result("failed", STAGE_VERIFY, "게시 미확인", proof=str(self.proof_img))

            except Exception as e:
                logger.error(f"❌ 플로우 예외: {e}")
                try:
                    await page.screenshot(path=str(self.proof_img))
                except Exception:
                    pass
                return self._result("error", "exception", str(e))
            finally:
                # 좀비 컨텍스트/페이지 회수 — 무인 가동 안전장치
                try:
                    await asyncio.wait_for(ctx.close(), timeout=10)
                except Exception as e:
                    logger.warning(f"컨텍스트 close 실패(무시): {e}")

    async def post_comment_on_latest_reel_async(self) -> Dict[str, Any]:
        # 워치독: 전역 타임아웃 초과 시 태스크 취소 + 좀비 회수
        flow_task = asyncio.create_task(self._run_flow())
        try:
            return await asyncio.wait_for(asyncio.shield(flow_task), timeout=GLOBAL_FLOW_TIMEOUT_SEC)
        except asyncio.TimeoutError:
            logger.error(f"❌ 전역 타임아웃({GLOBAL_FLOW_TIMEOUT_SEC}s) 초과 → 워치독 회수")
            flow_task.cancel()
            try:
                await asyncio.wait_for(flow_task, timeout=5)
            except (asyncio.CancelledError, asyncio.TimeoutError, Exception):
                pass
            return self._result("error", "watchdog", "전역 타임아웃")

    def post_comment_on_latest_reel(self) -> Dict[str, Any]:
        return asyncio.run(self.post_comment_on_latest_reel_async())


if __name__ == "__main__":
    c = InsuranceInstagramCommenter()
    res = c.post_comment_on_latest_reel()
    print("결과:", res)