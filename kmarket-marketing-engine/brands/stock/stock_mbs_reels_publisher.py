# -*- coding: utf-8 -*-
"""
📈 [주식 전용] Meta Business Suite 웹 릴스 발행 엔진 (순수 브라우저 스텔스 레고 블록)
========================================================================================
- 대표님 지침 준수: 
  1. 100% 순수 브라우저 스텔스 봇 (0 API)
  2. 글자 레시피 내비게이션: [동영상 추가] -> [텍스트] -> [다음] -> [다음] -> [공유하기] -> [완료]
  3. 완료 시 게시물 관리 화면(published_posts)으로 이동하여 1등 실물 등록 확인
  4. 실제 라이브 URL 영수증 추출
  5. 미발견 시 브라우저 풀리셋 후 최대 3회 자가 치유 재시도 (Self-Healing Retry)
  6. 릴스 발행 성공 직후 인스타그램 & 페이스북 첫 댓글 자율 파이프라인 비동기 직결
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


async def browser_ctx_close_safe(context) -> None:
    """브라우저 컨텍스트 안전 회수 헬퍼 (좀비 프로세스 방지)."""
    try:
        if context is not None:
            await context.close()
    except Exception:
        pass

PROFILE_DIR = CURRENT_DIR / "meta_chrome_profile"
SESSION_FILE = CURRENT_DIR / "meta_session.json"
ACCOUNTS_FILE = CURRENT_DIR / "accounts.json"

logger = logging.getLogger("StockMBSReelsPublisher")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class StockMBSReelsPublisher:
    """📈 주식 전용 Meta Business Suite 웹 릴스 발행기 (독립 레고 블록)"""

    def __init__(self):
        self.brand = "stock"
        self.profile_dir = PROFILE_DIR
        self.session_file = SESSION_FILE
        self.accounts_file = ACCOUNTS_FILE
        self.page_id = self._load_page_id()
        self.business_id = self._load_business_id()
        self.composer_url = f"https://business.facebook.com/latest/reels_composer?business_id={self.business_id}&asset_id={self.page_id}"
        self.posts_url = f"https://business.facebook.com/latest/posts/published_posts?business_id={self.business_id}&asset_id={self.page_id}"

    def _load_business_id(self) -> str:
        if self.accounts_file.exists():
            try:
                with open(self.accounts_file, "r", encoding="utf-8") as f:
                    acc = json.load(f)
                bid = acc.get("credentials", {}).get("facebook_business_id")
                if bid:
                    return str(bid)
            except Exception as e:
                logger.warning(f"accounts.json business_id 로드 경고: {e}")
        return "1524234062837117" # 주식 스톡마스터 비즈니스 기본값

    def _load_page_id(self) -> str:
        if self.accounts_file.exists():
            try:
                with open(self.accounts_file, "r", encoding="utf-8") as f:
                    acc = json.load(f)
                pid = acc.get("credentials", {}).get("facebook_page_id")
                if pid:
                    return str(pid)
            except Exception as e:
                logger.warning(f"accounts.json 로드 경고: {e}")
        return "1341778472350233" # 주식 기본값

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
        try:
            return asyncio.run(self.publish_reel_async(video_path, caption, max_retries))
        except Exception as e:
            logger.error(f"❌ [주식 MBS Reel] 발행 최종 예외: {e}")
            return {"status": "error", "message": str(e), "brand": self.brand}

    async def publish_reel_async(
        self,
        video_path: str,
        caption: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        if not os.path.exists(video_path):
            return {"status": "error", "message": f"비디오 파일 없음: {video_path}", "brand": self.brand}

        video_name = os.path.basename(video_path)
        # 🛡️ 본문 내 URL 전면 소독 (알고리즘 다운랭킹 방지 및 네이버 공식 검색어 유도)
        clean_caption = caption or ""
        clean_caption = re.sub(r'https?://\S+', '👉 네이버 검색: [스톡마스터 AI]', clean_caption)
        logger.info(f"🚀 [주식 MBS Reel] 순수 브라우저 글자 레시피 발행 가동: {video_name}")

        for attempt in range(1, max_retries + 1):
            logger.info(f"--- [시도 {attempt}/{max_retries}] 주식 메타 릴스 발행 시작 ---")
            clean_browser_profile_locks(self.profile_dir)

            try:
                async with async_browser_lock(f"주식 Meta 릴스 웹 발행 (시도 {attempt})", timeout_sec=600):
                    result = await self._execute_recipe_once(video_path, clean_caption)
                    if result.get("status") == "success":
                        logger.info(f"🎉 [주식 MBS Reel] 시도 {attempt}에서 100% 실물 발행 성공!")
                        # 💬 [자율 파이프라인] 릴스 발행 직후 인스타그램 & 페이스북 단독 첫 댓글 자율 집행 (비동기 직결)
                        try:
                            from brands.stock.stock_meta_comment_pipeline import run_stock_meta_comments_async
                            logger.info("💬 [주식] 인스타그램 & 페이스북 공식 첫 댓글 자율 파이프라인 출동...")
                            result["comments"] = await run_stock_meta_comments_async()
                        except Exception as ce:
                            logger.warning(f"⚠️ 주식 댓글 파이프라인 실행 중 경고: {ce}")
                        return result
                    else:
                        logger.warning(f"⚠️ [주식 MBS Reel] 시도 {attempt} 미완료: {result.get('message')}")
            except Exception as e:
                logger.error(f"❌ [주식 MBS Reel] 시도 {attempt} 예외 발생: {e}")

            if attempt < max_retries:
                logger.info("⏳ 5초 후 브라우저 풀리셋 및 재시도 진행...")
                await asyncio.sleep(5.0)

        return {
            "status": "error",
            "brand": self.brand,
            "message": f"{max_retries}회 재시도 모두 소진, 실물 등록 미확인"
        }

    async def _execute_recipe_once(self, video_path: str, caption: str) -> Dict[str, Any]:
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

                # 0. 전면 안내 팝업 자동 닫기
                try:
                    popup_close = page.locator("button:has-text('닫기'), div[aria-label='닫기'], button:has-text('시작하기'), [aria-label='Close']").first
                    if await popup_close.count() > 0 and await popup_close.is_visible():
                        await popup_close.click(force=True)
                        await asyncio.sleep(1.5)
                        logger.info("👉 메타 안내 팝업 닫기 완료")
                except Exception:
                    pass

                # 📌 2단계: '동영상 추가' / 'Add Video' 미디어 주입
                logger.info("2. '동영상 추가' 미디어 주입 중...")
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
                    logger.info("✍️ 캡션 기입 완료")

                await asyncio.sleep(2.0)

                # 📌 4단계: 1차 '다음 / Next' 글자 버튼 클릭
                next_btn_1 = page.locator("div[role='button'], button").filter(has_text=re.compile(r"^Next$|^다음$", re.I)).last
                if await next_btn_1.count() > 0 and await next_btn_1.is_visible():
                    await next_btn_1.scroll_into_view_if_needed()
                    await asyncio.sleep(1.0)
                    await next_btn_1.click(force=True)
                    logger.info("👉 1차 [다음/Next] 클릭 완료")
                await asyncio.sleep(4.0)

                # 📌 5단계: 2차 '다음 / Next' 글자 버튼 클릭
                next_btn_2 = page.locator("div[role='button'], button").filter(has_text=re.compile(r"^Next$|^다음$", re.I)).last
                if await next_btn_2.count() > 0 and await next_btn_2.is_visible():
                    await next_btn_2.scroll_into_view_if_needed()
                    await asyncio.sleep(1.0)
                    await next_btn_2.click(force=True)
                    logger.info("👉 2차 [다음/Next] 클릭 완료")
                await asyncio.sleep(4.0)

                # 📌 6단계: '공유하기 / Share' 글자 버튼 클릭
                share_btn = page.locator("div[role='button'], button").filter(has_text=re.compile(r"^Share$|^공유하기$|^공유$|^Publish$", re.I)).last
                if await share_btn.count() > 0 and await share_btn.is_visible():
                    await share_btn.scroll_into_view_if_needed()
                    await asyncio.sleep(1.0)
                    await share_btn.click(force=True)
                    logger.info("💥 [공유하기/Share] 클릭 집행 완료!")
                else:
                    raise RuntimeError("화면에서 [공유하기/Share] 버튼을 찾지 못했습니다.")

                # '릴스 처리 중 [완료/Done]' 팝업 대응
                await asyncio.sleep(5.0)
                done_btn = page.locator("div[role='button'], button").filter(has_text=re.compile(r"^Done$|^완료$", re.I)).first
                if await done_btn.count() > 0 and await done_btn.is_visible():
                    await done_btn.click(force=True)
                    logger.info("👉 '릴스 처리 중 [완료/Done]' 팝업 클릭")

                # 📌 7단계: [무인 파이프라인] 게시물 관리 화면으로 이동 후 조건 기반 폴링 검증
                # (고정 60초 sleep 폐기 → 렌더 상태 관측 기반 폴링 + 전체 상한 타임아웃)
                logger.info(f"7. 게시물 관리 화면({self.posts_url})으로 이동하여 실물 검증 폴링 시작...")
                await page.goto(self.posts_url, wait_until="domcontentloaded", timeout=40000)

                # 오버레이 소거 (구조화: 잔존 집합 불변 종료 + 상한 라운드 + 예외 로그 승격)
                overlay_ok = await self._dismiss_overlays(page, max_rounds=5)
                if not overlay_ok:
                    logger.warning("⚠️ 오버레이 잔존 감지 — 검증 신뢰도 저하 가능성 있음(로그 승격)")

                proof_path = CURRENT_DIR / "stock_mbs_verified_proof.png"

                # 조건 기반 폴링: 최상단 카드 스코프 검증 (위양성 원인 제거)
                verify_deadline = asyncio.get_event_loop().time() + 90.0   # 전체 상한 90초
                poll_interval = 3.0
                last_verdict: Dict[str, Any] = {"verdict": "unknown", "reason": "not_started"}

                while asyncio.get_event_loop().time() < verify_deadline:
                    try:
                        last_verdict = await self._verify_top_card(page, caption)
                    except Exception as ve:
                        # 예외 삼키지 않고 로그 승격
                        logger.warning(f"⚠️ 최상단 카드 검증 중 예외: {ve}")
                        last_verdict = {"verdict": "unknown", "reason": f"exception:{ve}"}

                    if last_verdict.get("verdict") == "match":
                        break
                    await asyncio.sleep(poll_interval)

                # 검증 결과 스크린샷 (성공/실패 무관 증빙)
                try:
                    await page.screenshot(path=str(proof_path))
                except Exception as se:
                    logger.warning(f"⚠️ 검증 스크린샷 실패: {se}")

                if last_verdict.get("verdict") == "match":
                    logger.info(f"🎉🎉 [주식 메타 릴스 실물 검증 100% 합격!] 사유={last_verdict.get('reason')}")
                    return {
                        "status": "success",
                        "brand": self.brand,
                        "platform": "meta_business_suite",
                        "message": "Meta Business Suite를 통한 📈 주식 릴스 순수 브라우저 실물 발행 완료",
                        "video": os.path.basename(video_path),
                        "verified_proof": str(proof_path),
                        "verify_detail": last_verdict,
                    }
                else:
                    logger.warning(f"⚠️ 최상단 카드 실물 미확인: {last_verdict}")
                    return {
                        "status": "pending_or_missing",
                        "message": "목록 최상단 카드에서 실물 미확인",
                        "verify_detail": last_verdict,
                    }

            finally:
                # 로그인 상태일 때만 저장 (로그아웃 쿠키로 정상 세션 덮어쓰기 금지)
                try:
                    await save_if_logged_in("meta", context, self.session_file, reason="stock_mbs_end")
                except Exception as se:
                    logger.warning(f"⚠️ 세션 저장 실패(무시하고 컨텍스트 회수 진행): {se}")
                # 🛡️ 세션/컨텍스트 회수 보장 (좀비 프로세스 방지)
                try:
                    await context.close()
                except Exception as ce:
                    logger.warning(f"⚠️ 컨텍스트 close 예외: {ce}")
                try:
                    await browser_ctx_close_safe(context)
                except Exception:
                    pass

    # ============================================================
    # 🧩 관측 계층: 오버레이 소거 / 최상단 카드 스코프 검증
    # ============================================================
    async def _dismiss_overlays(self, page, max_rounds: int = 5) -> bool:
        """
        오버레이/투어 모달 소거.
        - 종료 조건: 잔존 오버레이 집합이 라운드 간 불변(변화 없음) → 종료
        - 상한 라운드: max_rounds
        - 예외는 삼키지 않고 로그 승격
        반환: True(잔존 없음) / False(잔존 있음)
        """
        close_selectors = [
            "button:has-text('닫기')",
            "div[role='button']:has-text('닫기')",
            "button:has-text('Close')",
            "div[role='button']:has-text('Close')",
            "[aria-label='Close']",
            "[aria-label='닫기']",
        ]
        overlay_probe = "div[role='dialog'], div[aria-modal='true']"

        prev_signature: Optional[str] = None
        for round_idx in range(1, max_rounds + 1):
            try:
                dialogs = await page.query_selector_all(overlay_probe)
                visible_dialogs = []
                for d in dialogs:
                    try:
                        if await d.is_visible():
                            visible_dialogs.append(d)
                    except Exception:
                        continue

                # 잔존 집합 시그니처 (개수 + 첫 다이얼로그 텍스트 앞 40자)
                sig_parts = [str(len(visible_dialogs))]
                if visible_dialogs:
                    try:
                        txt = (await visible_dialogs[0].inner_text())[:40]
                        sig_parts.append(txt)
                    except Exception:
                        sig_parts.append("?")
                signature = "|".join(sig_parts)

                if not visible_dialogs:
                    logger.info(f"👉 오버레이 소거 완료(라운드 {round_idx}, 잔존 0)")
                    return True

                if prev_signature is not None and signature == prev_signature:
                    logger.warning(f"⚠️ 오버레이 잔존 집합 불변(라운드 {round_idx}, sig={signature}) — 소거 실패 판정")
                    return False
                prev_signature = signature

                clicked_any = False
                for sel in close_selectors:
                    try:
                        loc = page.locator(sel).first
                        if await loc.count() > 0 and await loc.is_visible():
                            await loc.click(force=True, timeout=2000)
                            clicked_any = True
                            await asyncio.sleep(0.6)
                            break
                    except Exception as ce:
                        logger.debug(f"오버레이 셀렉터 시도 실패({sel}): {ce}")
                if not clicked_any:
                    logger.warning(f"⚠️ 오버레이 감지됐으나 닫기 버튼 미발견(라운드 {round_idx})")
                    return False
            except Exception as e:
                logger.warning(f"⚠️ 오버레이 소거 라운드 {round_idx} 예외: {e}")
                return False

        # 상한 라운드 소진
        try:
            remaining = await page.query_selector_all(overlay_probe)
            still_visible = 0
            for d in remaining:
                try:
                    if await d.is_visible():
                        still_visible += 1
                except Exception:
                    continue
            if still_visible == 0:
                return True
        except Exception:
            pass
        logger.warning(f"⚠️ 오버레이 소거 상한 라운드({max_rounds}) 소진 — 잔존 가능성")
        return False

    @staticmethod
    def _normalize_text(s: str) -> str:
        """캡션/카드 텍스트 정규화: 제로폭 제거, 공백/개행 통합, 소문자화."""
        if not s:
            return ""
        # 제로폭 문자 제거
        s = re.sub(r"[\u200b-\u200f\u202a-\u202e\ufeff]", "", s)
        # 개행/탭/다중 공백 → 단일 공백
        s = re.sub(r"\s+", " ", s)
        return s.strip().lower()

    # ============================================================
    # 🧭 관측 계층 단일 계약 (Single Source of Truth)
    # ------------------------------------------------------------
    # - Insurance/Stock 공용: 브랜드 어댑터는 이 계약만 주입한다.
    # - MBS published_posts 는 role='row' 테이블 행 구조가 1차 계약.
    # - 피드용 셀렉터(div[role='article'], data-pagelet*='Post')는
    #   MBS 목록에서 다중 행/전체 리스트를 잡는 오스코프 원인이므로
    #   최후 폴백으로만 사용하고, 반드시 데이터 행 필터를 통과해야 한다.
    # ============================================================
    ROW_SELECTORS: tuple = (
        "div[role='row']",
        "div[role='listitem']",
        "div[role='article']",
        "div[data-pagelet*='Post']",
    )
    # 헤더/컬럼 라벨 행 배제용 (데이터 행 아님)
    HEADER_ROW_HINTS: tuple = (
        "게시물", "post", "도달", "reach", "참여", "engagement",
        "유형", "type", "날짜", "date", "상태", "status",
    )

    @staticmethod
    def _parse_time_badge(text: str) -> Optional[str]:
        """
        카드 내부 '게시 시각' 뱃지 파싱 (신선도 전용).
        반환: 'seconds' | 'minutes' | 'hours' | 'days' | None(파싱 실패)
        ⚠️ 영상 길이(0:32 등)는 절대 신선도로 해석하지 않는다.
        """
        if not text:
            return None
        t = text.lower()
        # 방금 전 / just now / 초 전
        if re.search(r"(방금|just now|\d+\s*초 전|\d+\s*s ago)", t):
            return "seconds"
        # 분 전
        if re.search(r"(\d+\s*분 전|\d+\s*m ago|\d+\s*min)", t):
            return "minutes"
        # 시간 전
        if re.search(r"(\d+\s*시간 전|\d+\s*h ago|\d+\s*hour)", t):
            return "hours"
        # 일 전
        if re.search(r"(\d+\s*일 전|\d+\s*d ago|\d+\s*day|어제|yesterday)", t):
            return "days"
        return None

    @staticmethod
    def _parse_duration_badge(text: str) -> Optional[str]:
        """
        카드 내부 '영상 길이' 뱃지 파싱 (신선도와 무관, 증거 기록용).
        반환: 'duration' | None
        """
        if not text:
            return None
        if re.search(r"\b\d{1,2}:\d{2}\b", text):
            return "duration"
        return None

    async def _collect_data_rows(self, page) -> list:
        """
        데이터 행 후보 수집 (헤더/컬럼 라벨 행 배제).
        - 가시성 + 텍스트 존재 + 헤더 힌트 미포함 조건 통과 행만 반환
        - DOM 순서 유지 (최상단 우선)
        """
        rows = []
        for sel in self.ROW_SELECTORS:
            try:
                loc = page.locator(sel)
                count = await loc.count()
            except Exception:
                continue
            for i in range(count):
                try:
                    el = loc.nth(i)
                    if not await el.is_visible():
                        continue
                    txt = await el.inner_text()
                    if not txt or not txt.strip():
                        continue
                    low = txt.strip().lower()
                    # 헤더 행 배제: 텍스트가 헤더 힌트로만 구성된 경우
                    if len(low) <= 40 and any(h in low for h in self.HEADER_ROW_HINTS):
                        # 데이터 신호(시간 뱃지/캡션 유사 텍스트)가 없으면 헤더로 판정
                        if self._parse_time_badge(txt) is None:
                            continue
                    rows.append({"selector": sel, "index": i, "text": txt, "locator": el})
                except Exception:
                    continue
            # 1차 계약(role='row')에서 데이터 행을 찾았으면 상위 계약 우선
            if rows:
                break
        return rows

    async def _verify_top_card(self, page, caption: str) -> Dict[str, Any]:
        """
        게시물 목록 최상단 '데이터 행'으로 스코프를 한정한 실물 검증.
        - 관측 계층 단일 계약(ROW_SELECTORS) 사용
        - 헤더 행 배제 필터 통과 행만 후보
        - 캡션 스니펫 매칭 + 게시 시각 뱃지 신선도만 신뢰
        - 영상 길이 뱃지는 증거로만 기록 (신선도 판정 금지)
        반환: 증거 기반 3상태
          {"verdict": "match"|"mismatch"|"unknown",
           "reason": str,
           "card_text_head": str,
           "badge_source": str,      # 'posted_time' | 'none'
           "duration_badge": str,    # 'duration' | 'none'
           "snippet": str,
           "row_selector": str}
        """
        rows = await self._collect_data_rows(page)
        if not rows:
            return {
                "verdict": "unknown",
                "reason": "data_row_not_found",
                "card_text_head": "",
                "badge_source": "none",
                "duration_badge": "none",
                "snippet": "",
                "row_selector": "",
            }

        top = rows[0]
        card_text = top["text"]
        norm_card = self._normalize_text(card_text)
        norm_caption = self._normalize_text(caption)
        head = norm_card[:80]
        snippet = norm_caption[:20] if norm_caption else ""
        caption_hit = bool(snippet) and (snippet in norm_card)

        posted_badge = self._parse_time_badge(card_text)   # 신선도 전용
        duration_badge = self._parse_duration_badge(card_text) or "none"
        badge_source = "posted_time" if posted_badge else "none"

        base = {
            "card_text_head": head,
            "badge_source": badge_source,
            "duration_badge": duration_badge,
            "snippet": snippet,
            "row_selector": top["selector"],
        }

        if caption_hit and posted_badge in ("seconds", "minutes"):
            return {"verdict": "match", "reason": f"caption+posted_badge({posted_badge})", **base}
        if caption_hit and posted_badge is None:
            return {"verdict": "unknown", "reason": "caption_hit_posted_badge_unknown", **base}
        if caption_hit and posted_badge in ("hours", "days"):
            return {"verdict": "mismatch", "reason": f"caption_hit_but_old({posted_badge})", **base}
        if not caption_hit and posted_badge in ("seconds", "minutes"):
            return {"verdict": "unknown", "reason": f"posted_badge_fresh_but_caption_miss({posted_badge})", **base}
        return {"verdict": "mismatch", "reason": "caption_miss_and_posted_badge_not_fresh", **base}


if __name__ == "__main__":
    pub = StockMBSReelsPublisher()
    print("Page ID:", pub.page_id)
    print("Is available:", pub.is_available())
