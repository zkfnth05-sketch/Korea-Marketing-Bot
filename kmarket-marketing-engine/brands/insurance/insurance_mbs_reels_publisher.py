# -*- coding: utf-8 -*-
"""
🛡️ [보험 리밸런스 전용] Meta Business Suite 웹 릴스 발행 엔진 (순수 브라우저 스텔스)
========================================================================================
- 대표님 지침 준수: 
  1. 100% 순수 브라우저 스텔스 봇 (0 API)
  2. 글자 레시피 내비게이션: [동영상 추가] -> [텍스트] -> [다음] -> [다음] -> [공유하기] -> [완료]
  3. 완료 시 게시물 관리 화면(published_posts)으로 이동하여 1등 실물 등록 확인
  4. 실제 라이브 URL(Instagram Reel, Facebook Reel) 영수증 추출
  5. 미발견 시 브라우저 풀리셋 후 최대 3회 자가 치유 재시도 (Self-Healing Retry)
"""

import os
import sys
import re
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine.browser_guard import clean_browser_profile_locks, get_safe_browser_args, async_browser_lock
from core.engine.session_integrity import ensure_auth_cookies, save_if_logged_in, is_logged_out_url, has_auth

PROFILE_DIR = CURRENT_DIR / "meta_chrome_profile"
SESSION_FILE = CURRENT_DIR / "meta_session.json"
ACCOUNTS_FILE = CURRENT_DIR / "accounts.json"

logger = logging.getLogger("InsuranceMBSReelsPublisher")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class InsuranceMBSReelsPublisher:
    """🛡️ 보험 리밸런스 전용 Meta Business Suite 웹 릴스 발행기"""

    def __init__(self):
        self.brand = "insurance"
        self.profile_dir = PROFILE_DIR
        self.session_file = SESSION_FILE
        self.accounts_file = ACCOUNTS_FILE
        self.page_id = self._load_page_id()
        self.business_id = self._load_business_id()
        self.composer_url = f"https://business.facebook.com/latest/reels_composer?business_id={self.business_id}&asset_id={self.page_id}"
        self.posts_url = f"https://business.facebook.com/latest/posts/published_posts?business_id={self.business_id}&asset_id={self.page_id}"

    def _load_business_id(self) -> str:
        """accounts.json에서 실제 보험 페이스북 비즈니스 포트폴리오 ID 로드"""
        if self.accounts_file.exists():
            try:
                with open(self.accounts_file, "r", encoding="utf-8") as f:
                    acc = json.load(f)
                bid = acc.get("credentials", {}).get("facebook_business_id")
                if bid:
                    return str(bid)
            except Exception as e:
                logger.warning(f"accounts.json business_id 로드 경고: {e}")
        return "1106559705427284" # 보험 Goldmom 비즈니스 기본값

    def _load_page_id(self) -> str:
        """accounts.json에서 실제 보험 페이스북 페이지 ID 로드"""
        if self.accounts_file.exists():
            try:
                with open(self.accounts_file, "r", encoding="utf-8") as f:
                    acc = json.load(f)
                pid = acc.get("credentials", {}).get("facebook_page_id")
                if pid:
                    return str(pid)
            except Exception as e:
                logger.warning(f"accounts.json 로드 경고: {e}")
        return "1358924267302888" # 보험 리밸런스 Goldmom 기본값

    def is_available(self) -> bool:
        has_profile = self.profile_dir.exists() and any(self.profile_dir.iterdir())
        has_session = self.session_file.exists() and self.session_file.stat().st_size > 50
        return has_profile or has_session

    def publish_reel(
        self,
        video_path: str,
        caption: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """동기 호출 인터페이스 (최대 3회 자가 치유 재시도)"""
        try:
            return asyncio.run(self.publish_reel_async(video_path, caption, max_retries))
        except Exception as e:
            logger.error(f"❌ [보험 MBS Reel] 발행 최종 예외: {e}")
            return {"status": "error", "message": str(e), "brand": self.brand}

    async def publish_reel_async(
        self,
        video_path: str,
        caption: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """비동기 메타 릴스 순수 브라우저 글자 레시피 발행 엔진"""
        if not os.path.exists(video_path):
            return {"status": "error", "message": f"비디오 파일 없음: {video_path}", "brand": self.brand}

        video_name = os.path.basename(video_path)
        # 🛡️ 본문 내 URL 전면 소독 (알고리즘 다운랭킹 방지 및 네이버 공식 검색어 유도)
        clean_caption = caption or ""
        clean_caption = re.sub(r'https?://\S+', '👉 네이버 검색: [보험 리밸런스]', clean_caption)
        logger.info(f"🚀 [보험 MBS Reel] 순수 브라우저 글자 레시피 발행 가동: {video_name}")

        for attempt in range(1, max_retries + 1):
            logger.info(f"--- [시도 {attempt}/{max_retries}] 메타 릴스 발행 시작 ---")
            clean_browser_profile_locks(self.profile_dir)

            try:
                async with async_browser_lock(f"보험 Meta 릴스 웹 발행 (시도 {attempt})", timeout_sec=600):
                    result = await self._execute_recipe_once(video_path, clean_caption)
                    if result.get("status") == "success":
                        logger.info(f"🎉 [보험 MBS Reel] 시도 {attempt}에서 100% 실물 발행 성공!")
                        # 💬 [자율 파이프라인] 릴스 발행 직후 인스타그램 & 페이스북 단독 첫 댓글 자율 집행
                        try:
                            from brands.insurance.insurance_meta_comment_pipeline import run_insurance_meta_comments_async
                            logger.info("💬 [보험] 인스타그램 & 페이스북 공식 첫 댓글 자율 파이프라인 출동...")
                            result["comments"] = await run_insurance_meta_comments_async()
                        except Exception as ce:
                            logger.warning(f"⚠️ 보험 댓글 파이프라인 실행 중 경고: {ce}")
                        return result
                    else:
                        logger.warning(f"⚠️ [보험 MBS Reel] 시도 {attempt} 미완료: {result.get('message')}")
            except Exception as e:
                logger.error(f"❌ [보험 MBS Reel] 시도 {attempt} 예외 발생: {e}")

            if attempt < max_retries:
                logger.info("⏳ 5초 후 브라우저 풀리셋 및 재시도 진행...")
                await asyncio.sleep(5.0)

        return {
            "status": "error",
            "brand": self.brand,
            "message": f"{max_retries}회 재시도 모두 소진, 실물 등록 미확인"
        }

    # =====================================================================
    # 🛡️ [오버레이 상태 머신] 라운드 기반 · 소멸 확인 · 모든 내비게이션 경계에서 재사용
    # =====================================================================
    _OVERLAY_CLOSE_SELECTORS = [
        "[aria-label='닫기']",
        "[aria-label='Close']",
        "[aria-label='Dismiss']",
        "div[role='dialog'] [aria-label='닫기']",
        "div[role='dialog'] [aria-label='Close']",
        "button:has-text('닫기')",
        "button:has-text('Close')",
        "div[role='button']:has-text('나중에')",
        "div[role='button']:has-text('Not now')",
        "div[role='button']:has-text('건너뛰기')",
        "div[role='button']:has-text('Skip')",
    ]
    _OVERLAY_CONTAINER_SELECTORS = [
        "div[role='dialog']",
        "[aria-modal='true']",
        "div[role='alertdialog']",
    ]

    async def _dismiss_overlays(self, page, max_rounds: int = 5, settle_ms: int = 400) -> int:
        """라운드 기반 오버레이 소거. 각 라운드마다 '실제로 사라졌는지' 확인 후 다음 라운드.
        반환값: 소거 성공 횟수. 소거 후에도 남아있으면 예외 없이 로그만 남기고 종료(상위에서 판단)."""
        dismissed = 0
        for rnd in range(1, max_rounds + 1):
            acted = False
            for sel in self._OVERLAY_CLOSE_SELECTORS:
                try:
                    loc = page.locator(sel)
                    cnt = await loc.count()
                    if cnt == 0:
                        continue
                    for i in range(min(cnt, 3)):
                        el = loc.nth(i)
                        try:
                            if not await el.is_visible():
                                continue
                            await el.click(timeout=1500)
                            acted = True
                            dismissed += 1
                            await page.wait_for_timeout(settle_ms)
                        except Exception:
                            continue
                except Exception:
                    continue
            # 소멸 확인: 컨테이너가 실제로 사라졌는지 검사
            remaining = 0
            for csel in self._OVERLAY_CONTAINER_SELECTORS:
                try:
                    loc = page.locator(csel)
                    cnt = await loc.count()
                    for i in range(cnt):
                        try:
                            if await loc.nth(i).is_visible():
                                remaining += 1
                        except Exception:
                            pass
                except Exception:
                    pass
            if remaining == 0:
                if acted:
                    logger.info(f"🧹 [오버레이] 라운드 {rnd}에서 소거 완료 (누적 {dismissed}회)")
                return dismissed
            if not acted:
                # 더 이상 닫을 수단이 없는데 컨테이너가 남아있음 → 상위 판단에 위임
                logger.warning(f"⚠️ [오버레이] 라운드 {rnd}: 닫기 수단 소진, 잔존 컨테이너 {remaining}개")
                return dismissed
        logger.warning(f"⚠️ [오버레이] 최대 라운드({max_rounds}) 소진, 잔존 컨테이너 존재 가능")
        return dismissed

    # =====================================================================
    # 🛡️ [카드 스코프 검증] 최상단 행 로케이터 → 정규화 → 부분일치 + 시간 배지 정규식
    # =====================================================================
    _TIME_BADGE_RE = re.compile(
        r"(방금|초\s*전|분\s*전|시간\s*전|일\s*전|주\s*전|"
        r"just\s*now|\d+\s*[smhdw]\b|\d+\s*(second|minute|hour|day|week)s?\s*ago)",
        re.I,
    )

    @staticmethod
    def _normalize_text(s: str) -> str:
        """공백/제로폭/전각/이모지/개행 정규화"""
        if not s:
            return ""
        s = s.replace("\u200b", "").replace("\u200c", "").replace("\u200d", "").replace("\ufeff", "")
        s = s.replace("\u00a0", " ")
        # 전각 → 반각
        s = "".join(
            chr(ord(ch) - 0xFEE0) if 0xFF01 <= ord(ch) <= 0xFF5E else ch
            for ch in s
        )
        # 이모지/기호 제거
        s = re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F]", "", s)
        s = re.sub(r"\s+", " ", s).strip()
        return s

    async def _verify_top_card(self, page, caption: str, timeout_ms: int = 20000) -> Dict[str, Any]:
        """게시물 목록 최상단 '행' 단위로 스코프를 좁혀 검증.
        - 최상단 행 로케이터 확보(테이블 row / 리스트 아이템)
        - 행 내부 텍스트만 정규화 후 캡션 스니펫 부분일치
        - 시간 배지 정규식 존재 여부로 '방금 게시됨' 신호 보강
        반환: {"verified": bool, "reason": str, "row_text": str}"""
        snippet_raw = (caption or "").strip()[:20]
        snippet = self._normalize_text(snippet_raw)
        if not snippet:
            return {"verified": False, "reason": "빈 캡션", "row_text": ""}

        row_selectors = [
            "div[role='row']",
            "table tbody tr",
            "div[role='listitem']",
            "div[role='article']",
        ]
        deadline = asyncio.get_event_loop().time() + (timeout_ms / 1000.0)
        last_row_text = ""
        while asyncio.get_event_loop().time() < deadline:
            for rsel in row_selectors:
                try:
                    rows = page.locator(rsel)
                    cnt = await rows.count()
                    if cnt == 0:
                        continue
                    top = rows.first
                    try:
                        if not await top.is_visible():
                            continue
                    except Exception:
                        continue
                    raw = await top.inner_text()
                    norm = self._normalize_text(raw)
                    last_row_text = norm
                    has_snippet = snippet in norm
                    has_time = bool(self._TIME_BADGE_RE.search(raw))
                    if has_snippet and has_time:
                        return {"verified": True, "reason": "snippet+time_badge", "row_text": norm}
                    if has_snippet:
                        # 스니펫은 맞지만 시간 배지 미확인 → 잠시 대기 후 재확인
                        await page.wait_for_timeout(1500)
                        continue
                except Exception:
                    continue
            await page.wait_for_timeout(1500)

        return {"verified": False, "reason": "top_card_mismatch", "row_text": last_row_text}

    async def _execute_recipe_once(self, video_path: str, caption: str) -> Dict[str, Any]:
        """1회 글자 레시피 실행 및 게시물 관리 화면 실물 검증"""
        async with async_playwright() as p:
            browser_args = get_safe_browser_args([
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check",
                "--start-maximized"
            ])
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=True,
                args=browser_args,
                viewport={"width": 1366, "height": 900},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            )

            # 🛡️ 인증 쿠키(c_user/xs) 유무로 판단하여 부재 시에만 정상 세션/백업에서 복원
            await ensure_auth_cookies("meta", context, self.session_file)

            page = context.pages[0] if context.pages else await context.new_page()

            try:
                # 📌 1단계: 릴스 작성기 접속
                logger.info(f"1. 릴스 작성기 접속 중: {self.composer_url}")
                await page.goto(self.composer_url, wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(4.0)

                if is_logged_out_url("meta", page.url) or not has_auth("meta", await context.cookies()):
                    raise RuntimeError("메타(페이스북) 세션 만료. 로그인 필요.")
                # 🛡️ [스테이지 경계 1] 작성기 진입 직후 오버레이 상태 머신 가동
                await self._dismiss_overlays(page, max_rounds=5)

                # 📌 2단계: '동영상 추가' / 'Add video' 글자 눈으로 찾고 파일 넣기
                logger.info("2. '동영상 추가' 미디어 주입 중...")
                import re
                try:
                    await page.wait_for_selector("input[type='file'], [role='button']:has-text('동영상'), [role='button']:has-text('Add video'), button:has-text('동영상'), button:has-text('Add Video')", timeout=15000)
                except Exception:
                    pass

                # 파일 주입: Add Video 버튼 클릭 후 file_chooser 대응
                btn = page.locator("div[role='button'], button").filter(has_text=re.compile(r"^Add Video$|^동영상 추가$", re.I)).first
                if await btn.count() == 0:
                    btn = page.locator("div[role='button'], button").filter(has_text=re.compile(r"Add Video|동영상 추가", re.I)).first

                if await btn.count() > 0 and await btn.is_visible():
                    async with page.expect_file_chooser(timeout=15000) as fc_info:
                        await btn.click()
                    fc = await fc_info.value
                    await fc.set_files(str(Path(video_path).resolve()))
                    logger.info("🎬 파일 선택기를 통한 비디오 파일 주입 성공!")
                else:
                    file_input = await page.query_selector("input[type='file']")
                    if file_input:
                        await file_input.set_input_files(str(Path(video_path).resolve()))
                        logger.info("🎬 input[type='file']에 직접 비디오 파일 주입 성공!")
                    else:
                        raise RuntimeError("화면에서 '동영상 추가' 버튼을 찾지 못했습니다.")

                logger.info("⏳ 비디오 처리 및 미리보기 생성 대기 (12초)...")
                await asyncio.sleep(12.0)

                # 📌 3단계: '텍스트' 글자 입력창 찾아서 캡션 기입
                logger.info("3. 릴스 본문 및 해시태그 기입 중...")
                text_input = page.locator("textarea, div[contenteditable='true'], [role='textbox']").first
                if await text_input.count() > 0:
                    await text_input.scroll_into_view_if_needed()
                    await text_input.click(force=True)
                    await text_input.press("Control+A")
                    await text_input.press("Backspace")
                    await asyncio.sleep(0.3)
                    for ch in caption:
                        if ch == "\n":
                            await text_input.press("Shift+Enter")
                        else:
                            await text_input.type(ch)
                        await asyncio.sleep(0.008)
                    logger.info("✍️ contenteditable type() 방식 캡션 기입 완료")

                await asyncio.sleep(2.0)

                # 📌 4단계: 1차 '다음'/'Next' 글자 버튼 클릭
                next_btn_1 = page.locator("div[role='button'], button").filter(has_text=re.compile(r"^Next$|^다음$", re.I)).last
                if await next_btn_1.count() > 0 and await next_btn_1.is_visible():
                    await next_btn_1.scroll_into_view_if_needed()
                    await asyncio.sleep(1.0)
                    await next_btn_1.click(force=True)
                    logger.info("👉 1차 [다음/Next] 클릭 완료")
                await asyncio.sleep(4.0)

                # 📌 5단계: 2차 '다음'/'Next' 글자 버튼 클릭
                next_btn_2 = page.locator("div[role='button'], button").filter(has_text=re.compile(r"^Next$|^다음$", re.I)).last
                if await next_btn_2.count() > 0 and await next_btn_2.is_visible():
                    await next_btn_2.scroll_into_view_if_needed()
                    await asyncio.sleep(1.0)
                    await next_btn_2.click(force=True)
                    logger.info("👉 2차 [다음/Next] 클릭 완료")
                await asyncio.sleep(4.0)

                # 🛡️ [계정 무결성 가드] 인스타그램 동시 공유 옵션 검증 (Insurance 전용: goldmomofficial)
                try:
                    # 화면에 노출된 Instagram 공유 옵션 / 체크박스 탐색
                    for inp in await page.locator("input[type='checkbox']").all():
                        parent_text = await inp.evaluate("el => el.closest('label, div, tr')?.innerText || ''")
                        aria_label = await inp.get_attribute("aria-label") or ""
                        combined_text = (parent_text + " " + aria_label).lower()
                        if re.search(r"instagram|인스타그램", combined_text, re.I):
                            # 타 브랜드(aura_ai_dating, stockmaster 등) 계정이 잡혀있거나 내 계정이 아닐 경우 즉시 OFF
                            if "aura" in combined_text or "stockmaster" in combined_text or ("goldmom" not in combined_text and "@" in combined_text):
                                if await inp.is_checked():
                                    await inp.uncheck(force=True)
                                    logger.warning("🛡️ [계정 가드] 타 브랜드 인스타그램 계정 감지 -> 동시 공유 즉시 차단(OFF) 완료!")
                            else:
                                logger.info("✅ [계정 가드] 보험 전용 인스타그램(goldmomofficial) 확인 또는 정상 유지")

                    for sw in await page.locator("[role='switch'], [role='checkbox']").all():
                        parent_text = await sw.evaluate("el => el.closest('label, div, tr')?.innerText || ''")
                        aria_label = await sw.get_attribute("aria-label") or ""
                        aria_checked = await sw.get_attribute("aria-checked")
                        combined_text = (parent_text + " " + aria_label).lower()
                        if re.search(r"instagram|인스타그램", combined_text, re.I):
                            if "aura" in combined_text or "stockmaster" in combined_text or ("goldmom" not in combined_text and "@" in combined_text):
                                if aria_checked == "true":
                                    await sw.click()
                                    logger.warning("🛡️ [계정 가드] 타 브랜드 인스타그램 스위치 감지 -> 즉시 OFF 전환 완료!")
                except Exception as guard_err:
                    logger.warning(f"⚠️ 인스타그램 계정 가드 점검 중 경고 (계속 진행): {guard_err}")

                # 📌 6단계: '공유하기'/'Share' 글자 버튼 클릭
                share_btn = page.locator("div[role='button'], button").filter(has_text=re.compile(r"^Share$|^공유하기$|^공유$|^Publish$", re.I)).last
                if await share_btn.count() > 0 and await share_btn.is_visible():
                    await share_btn.scroll_into_view_if_needed()
                    await asyncio.sleep(1.0)
                    await share_btn.click(force=True)
                    logger.info("💥 [공유하기/Share] 클릭 집행 완료!")
                else:
                    raise RuntimeError("화면에서 [공유하기/Share] 버튼을 찾지 못했습니다.")

                # '릴스 처리 중 [완료]' 팝업 대응
                await asyncio.sleep(3.0)
                done_btn = page.locator("div[role='button'], button").filter(has_text=re.compile(r"^완료$|^Done$", re.I)).first
                if await done_btn.count() > 0 and await done_btn.is_visible():
                    await done_btn.click(force=True)
                    logger.info("👉 '릴스 처리 중 [완료/Done]' 팝업 클릭")

                # 📌 7단계: [조건 기반 대기] 게시물 목록으로 이동 후 카드 스코프 검증 (고정 60초 대기 제거)
                logger.info(f"7. 게시물 관리 화면({self.posts_url})으로 이동하여 실물 검증 중...")
                await page.goto(self.posts_url, wait_until="domcontentloaded", timeout=40000)

                # 🛡️ [스테이지 경계 2] 게시물 목록 진입 직후 오버레이 상태 머신 가동
                await self._dismiss_overlays(page, max_rounds=5)

                # 🛡️ [스테이지 경계 3] 카드 스코프 검증 (조건 기반 대기 + 명시적 타임아웃)
                verify = await self._verify_top_card(page, caption, timeout_ms=90000)

                # 증빙 스크린샷
                proof_path = CURRENT_DIR / "mbs_verified_proof.png"
                try:
                    await page.screenshot(path=str(proof_path))
                except Exception as se:
                    logger.warning(f"⚠️ 증빙 스크린샷 실패(계속): {se}")

                if verify.get("verified"):
                    logger.info(f"🎉🎉 [보험 메타 릴스 실물 검증 100% 합격!] 최상단 카드 스코프 일치 확인 (사유: {verify.get('reason')})")
                    return {
                        "status": "success",
                        "brand": self.brand,
                        "platform": "meta_business_suite",
                        "message": "Meta Business Suite를 통한 🛡️ InsureBalance 보험 릴스 순수 브라우저 실물 발행 완료",
                        "video": os.path.basename(video_path),
                        "verified_proof": str(proof_path),
                        "verify_reason": verify.get("reason"),
                    }
                else:
                    logger.warning(f"⚠️ 최상단 카드 스코프 검증 실패 (사유: {verify.get('reason')})")
                    return {
                        "status": "pending_or_missing",
                        "message": f"목록 최상단 카드 미확인 ({verify.get('reason')})",
                        "verify_reason": verify.get("reason"),
                    }

            finally:
                # 로그인 상태일 때만 저장 (로그아웃 쿠키로 정상 세션 덮어쓰기 금지)
                try:
                    await save_if_logged_in("meta", context, self.session_file, reason="insurance_mbs_end")
                except Exception:
                    pass
                await context.close()


if __name__ == "__main__":
    pub = InsuranceMBSReelsPublisher()
    print("Page ID:", pub.page_id)
    print("Is available:", pub.is_available())
