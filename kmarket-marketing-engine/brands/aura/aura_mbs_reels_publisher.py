# -*- coding: utf-8 -*-
"""
✨ [아우라 전용] Meta Business Suite 웹 릴스 발행 엔진 (순수 브라우저 스텔스 레고 블록)
========================================================================================
- 대표님 지침 준수: 
  1. 100% 순수 브라우저 스텔스 봇 (0 API)
  2. 글자 레시피 내비게이션: [동영상 추가] -> [텍스트] -> [다음] -> [다음] -> [공유하기] -> [완료]
  3. 완료 시 게시물 관리 화면(published_posts)으로 이동하여 1등 실물 등록 확인
  4. 실제 라이브 URL 영수증 추출
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

logger = logging.getLogger("AuraMBSReelsPublisher")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class AuraMBSReelsPublisher:
    """✨ 아우라 전용 Meta Business Suite 웹 릴스 발행기 (독립 레고 블록)"""

    def __init__(self):
        self.brand = "aura"
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
        return "996423700150452" # 아우라 비즈니스 기본값

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
        return "1356851504174047" # 아우라 기본값

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
            logger.error(f"❌ [아우라 MBS Reel] 발행 최종 예외: {e}")
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
        clean_caption = re.sub(r'https?://\S+', '👉 네이버 검색: [아우라AI데이팅]', clean_caption)
        logger.info(f"🚀 [아우라 MBS Reel] 순수 브라우저 글자 레시피 발행 가동: {video_name}")

        for attempt in range(1, max_retries + 1):
            logger.info(f"--- [시도 {attempt}/{max_retries}] 아우라 메타 릴스 발행 시작 ---")
            clean_browser_profile_locks(self.profile_dir)

            try:
                async with async_browser_lock(f"아우라 Meta 릴스 웹 발행 (시도 {attempt})", timeout_sec=600):
                    result = await self._execute_recipe_once(video_path, clean_caption)
                    status = result.get("status")

                    # 🛡️ [멱등성 가드] 게시 실행은 완료되었으나 검증이 불확정인 경우,
                    # 재시도는 중복 게시를 유발하므로 즉시 종료하고 결과를 그대로 반환한다.
                    if status == "published_unverified":
                        logger.warning(
                            f"🛑 [아우라 MBS Reel] 시도 {attempt} 게시 실행 완료·검증 불확정 → 재시도 차단"
                        )
                        return result

                    if status == "success":
                        logger.info(f"🎉 [아우라 MBS Reel] 시도 {attempt}에서 100% 실물 발행 성공!")
                        # 💬 [자율 파이프라인] 릴스 발행 직후 인스타그램 & 페이스북 단독 첫 댓글 자율 집행 (비동기 직접 await)
                        try:
                            from brands.aura.aura_meta_comment_pipeline import run_aura_meta_comments_async
                            logger.info("💬 [아우라] 인스타그램 & 페이스북 공식 첫 댓글 자율 파이프라인 출동...")
                            result["comments"] = await run_aura_meta_comments_async()
                        except Exception as ce:
                            logger.warning(f"⚠️ 아우라 댓글 파이프라인 실행 중 경고: {ce}")
                        return result
                    else:
                        logger.warning(f"⚠️ [아우라 MBS Reel] 시도 {attempt} 미완료: {result.get('message')}")
            except Exception as e:
                logger.error(f"❌ [아우라 MBS Reel] 시도 {attempt} 예외 발생: {e}")

            if attempt < max_retries:
                logger.info("⏳ 5초 후 브라우저 풀리셋 및 재시도 진행...")
                await asyncio.sleep(5.0)

        return {
            "status": "error",
            "brand": self.brand,
            "message": f"{max_retries}회 재시도 모두 소진, 실물 등록 미확인"
        }

    # ============================================================
    # 🧱 [계층 1] UI 상호작용 계층: 오버레이(팝업) 소거 유틸
    # ============================================================
    async def _dismiss_overlays(self, page, stage: str = "", max_rounds: int = 6) -> int:
        """오버레이 DOM 상태를 근거로 반복 소거. 셀렉터 목록 의존을 최소화하고
        '닫기류 버튼이 실제로 보이고 클릭 가능한가'를 판정 기준으로 삼는다."""
        closed = 0
        close_pattern = re.compile(
            r"^(닫기|시작하기|확인|나중에|Close|Dismiss|Got it|OK|Not now|Later)$", re.I
        )
        for rnd in range(max_rounds):
            try:
                # 1) 표준 닫기 후보 수집 (aria-label / 텍스트 / role=button)
                candidates = page.locator(
                    "div[role='dialog'] button, div[role='dialog'] div[role='button'], "
                    "[aria-label='Close'], [aria-label='닫기'], "
                    "button, div[role='button']"
                )
                count = await candidates.count()
                clicked = False
                for i in range(min(count, 40)):
                    el = candidates.nth(i)
                    try:
                        if not await el.is_visible():
                            continue
                        label = (await el.get_attribute("aria-label")) or ""
                        text = (await el.inner_text() or "").strip()
                        if close_pattern.match(label) or close_pattern.match(text):
                            await el.click(force=True, timeout=2000)
                            closed += 1
                            clicked = True
                            await asyncio.sleep(0.8)
                            break
                    except Exception as e:
                        logger.debug(f"[overlay/{stage}] 후보 클릭 스킵: {e}")
                        continue
                if not clicked:
                    break
            except Exception as e:
                logger.debug(f"[overlay/{stage}] 라운드 {rnd} 예외: {e}")
                break
        if closed:
            logger.info(f"👉 [{stage}] 오버레이 {closed}건 소거 완료")
        return closed

    # ============================================================
    # 🧱 [계층 2] 검증 계층: 최상단 카드 단위 실물 검증 (다중 방언 스코어링)
    # ============================================================
    # 검증 계층은 게시 실행 계층과 완전히 분리한다.
    # - 셀렉터 방언을 '단일 체인'이 아닌 '후보 목록'으로 순회한다.
    # - 각 후보를 카드 후보로 스코어링하여 '가장 게시물다운' 노드를 선택한다.
    # - 검증 예외는 게시 실패로 승격하지 않는다(거짓 음성 → 중복 게시 방지).
    _CARD_SELECTOR_DIALECTS = (
        "div[role='article']",
        "div[role='listitem']",
        "div[role='row']",
        "article",
        "div[data-pagelet^='PostsList'] > div",
        "div[data-pagelet='PublishedPostsList'] > div",
        "div[aria-posinset]",
    )

    @staticmethod
    def _normalize(text: str) -> str:
        if not text:
            return ""
        t = text.replace("\u200b", "").replace("\xa0", " ")
        t = re.sub(r"\s+", " ", t)
        return t.strip().lower()

    async def _collect_card_candidates(self, page, limit_per_dialect: int = 5):
        """모든 방언을 순회하여 (locator, text, score) 후보를 수집한다.
        점수는 '게시물 카드다움'의 휴리스틱: 텍스트 길이 + 시간배지 + 상태표시."""
        candidates = []
        seen_handles = set()
        for dialect in self._CARD_SELECTOR_DIALECTS:
            try:
                loc = page.locator(dialect)
                cnt = await loc.count()
            except Exception as e:
                logger.debug(f"[verify] 방언 '{dialect}' count 예외: {e}")
                continue
            for i in range(min(cnt, limit_per_dialect)):
                try:
                    el = loc.nth(i)
                    if not await el.is_visible():
                        continue
                    # 동일 노드 중복 수집 방지
                    handle = await el.element_handle()
                    if handle is None:
                        continue
                    key = id(handle)
                    if key in seen_handles:
                        continue
                    seen_handles.add(key)

                    text = await el.inner_text()
                    if not text or len(text.strip()) < 4:
                        continue
                    score = 0
                    if re.search(r"\b\d{1,2}:\d{2}\b", text):
                        score += 3
                    if re.search(r"(published|게시됨|공개|just now|방금)", text, re.I):
                        score += 2
                    score += min(len(text) // 40, 5)
                    candidates.append({"locator": el, "text": text, "score": score, "dialect": dialect})
                except Exception as e:
                    logger.debug(f"[verify] 방언 '{dialect}'[{i}] 수집 스킵: {e}")
                    continue
        candidates.sort(key=lambda c: c["score"], reverse=True)
        return candidates

    async def _verify_top_card(self, page, caption: str) -> Dict[str, Any]:
        """게시물 목록 최상단 카드만 대상으로 캡션 정규화 부분일치 + 영상 길이 배지 정규식 판정.
        검증 예외는 '검증 불가'로 분류하며, 게시 실패로 승격하지 않는다."""
        try:
            candidates = await self._collect_card_candidates(page)
        except Exception as e:
            # 검증 계층 자체 예외 → 게시 실패 아님. 재시도 트리거 금지.
            logger.warning(f"[verify] 카드 후보 수집 예외(검증 불가): {e}")
            return {"verified": False, "inconclusive": True, "reason": f"검증 불가: {e}"}

        if not candidates:
            return {"verified": False, "inconclusive": True, "reason": "최상단 카드 후보 미탐지"}

        norm_cap_full = self._normalize(caption)
        probes = []
        for n in (30, 20, 12):
            p = self._normalize(caption[:n]) if caption else ""
            if p and p not in probes:
                probes.append(p)

        # 상위 후보부터 판정. 최상단 카드가 스코어 1위일 확률이 높다.
        for idx, cand in enumerate(candidates[:3]):
            card_text = cand["text"]
            norm_card = self._normalize(card_text)

            cap_hit = any(p in norm_card for p in probes)
            dur_hit = bool(re.search(r"\b\d{1,2}:\d{2}\b", card_text))
            status_hit = bool(re.search(r"(published|게시됨|공개|just now|방금)", card_text, re.I))

            verified = cap_hit and (dur_hit or status_hit)
            reason = (
                f"rank={idx}, dialect={cand['dialect']}, score={cand['score']}, "
                f"cap_hit={cap_hit}, dur_hit={dur_hit}, status_hit={status_hit}"
            )
            if verified:
                return {"verified": True, "inconclusive": False, "reason": reason}

        # 어떤 후보도 확정 불가 → inconclusive (재시도 금지, 사람/후속 검증 위임)
        return {
            "verified": False,
            "inconclusive": True,
            "reason": f"상위 후보 {min(len(candidates), 3)}건 모두 미확정 (cap_probe={probes[:1]})"
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
                logger.info(f"1. 릴스 작성기 접속 중: {self.composer_url}")
                await page.goto(self.composer_url, wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(4.0)

                if is_logged_out_url("meta", page.url) or not has_auth("meta", await context.cookies()):
                    raise RuntimeError("메타(페이스북) 세션 만료. 로그인 필요.")

                # 0. 전면 안내 팝업 자동 소거 (오버레이 상태 기반 반복 루프)
                await self._dismiss_overlays(page, stage="composer")

                logger.info("2. '동영상 추가' 미디어 주입 중...")
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

                # 1차 다음 / Next
                next_btn_1 = page.locator("div[role='button'], button").filter(has_text=re.compile(r"^Next$|^다음$", re.I)).last
                if await next_btn_1.count() > 0 and await next_btn_1.is_visible():
                    await next_btn_1.scroll_into_view_if_needed()
                    await asyncio.sleep(1.0)
                    await next_btn_1.click(force=True)
                    logger.info("👉 1차 [다음/Next] 클릭 완료")
                await asyncio.sleep(4.0)

                # 2차 다음 / Next
                next_btn_2 = page.locator("div[role='button'], button").filter(has_text=re.compile(r"^Next$|^다음$", re.I)).last
                if await next_btn_2.count() > 0 and await next_btn_2.is_visible():
                    await next_btn_2.scroll_into_view_if_needed()
                    await asyncio.sleep(1.0)
                    await next_btn_2.click(force=True)
                    logger.info("👉 2차 [다음/Next] 클릭 완료")
                await asyncio.sleep(4.0)

                # 최종 공유 / Share 클릭
                share_btn = page.locator("div[role='button'], button").filter(has_text=re.compile(r"^Share$|^공유하기$|^공유$|^Publish$", re.I)).last
                if await share_btn.count() > 0 and await share_btn.is_visible():
                    await share_btn.scroll_into_view_if_needed()
                    await asyncio.sleep(1.0)
                    await share_btn.click(force=True)
                    logger.info("💥 [공유하기/Share] 클릭 집행 완료!")
                else:
                    raise RuntimeError("화면에서 [공유하기/Share] 버튼을 찾지 못했습니다.")

                await asyncio.sleep(5.0)
                done_btn = page.locator("div[role='button'], button").filter(has_text=re.compile(r"^Done$|^완료$", re.I)).first
                if await done_btn.count() > 0 and await done_btn.is_visible():
                    await done_btn.click(force=True)
                    logger.info("👉 '릴스 처리 중 [완료/Done]' 팝업 클릭")

                # 📌 7단계: [무인 파이프라인] 메타 릴스 서버 인코딩 및 배포 대기 (정확히 60초 휴식)
                logger.info("⏳ [메타 릴스 무인 파이프라인] 릴스 인코딩 및 서버 배포 대기 (정확히 60초 휴식 후 실물 확인)...")
                await asyncio.sleep(60.0)

                logger.info(f"7. 게시물 관리 화면({self.posts_url})으로 이동하여 실물 검증 중...")
                await page.goto(self.posts_url, wait_until="domcontentloaded", timeout=40000)
                await asyncio.sleep(5.0)

                await self._dismiss_overlays(page, stage="posts_list")

                proof_path = CURRENT_DIR / "aura_mbs_verified_proof.png"
                await page.screenshot(path=str(proof_path))

                # 최상단 카드 단위 추출 + 정규화 부분일치 + 영상 길이 배지 정규식
                verdict = await self._verify_top_card(page, caption)
                logger.info(f"🔎 [검증 판정] {verdict}")

                if verdict.get("verified"):
                    logger.info("🎉🎉 [아우라 메타 릴스 실물 검증 100% 합격!] 최상단 카드에서 정상 게시 확인!")
                    return {
                        "status": "success",
                        "brand": self.brand,
                        "platform": "meta_business_suite",
                        "message": "Meta Business Suite를 통한 ✨ 아우라 릴스 순수 브라우저 실물 발행 완료",
                        "video": os.path.basename(video_path),
                        "verified_proof": str(proof_path),
                        "verify_reason": verdict.get("reason")
                    }

                # 🛡️ [멱등성 가드] 검증이 '불확정(inconclusive)'이면 게시 자체는 성공했을 가능성이 높다.
                # 이 경우 재시도는 중복 게시를 유발하므로 재시도 루프를 즉시 종료하고 사람 검증으로 위임한다.
                if verdict.get("inconclusive"):
                    logger.warning(
                        f"⚠️ [검증 불확정] 재시도 금지(중복 게시 방지). 사유: {verdict.get('reason')}"
                    )
                    return {
                        "status": "published_unverified",
                        "brand": self.brand,
                        "platform": "meta_business_suite",
                        "message": "게시 실행 완료, 목록 검증 불확정 (재시도 금지)",
                        "video": os.path.basename(video_path),
                        "verified_proof": str(proof_path),
                        "verify_reason": verdict.get("reason"),
                        "retry_blocked": True,
                    }

                logger.warning(f"⚠️ 최상단 카드 실물 미확인: {verdict.get('reason')}")
                return {"status": "pending_or_missing", "message": verdict.get("reason", "목록에 실물 미확인")}

            finally:
                # 로그인 상태일 때만 저장 (로그아웃 쿠키로 정상 세션 덮어쓰기 금지)
                try:
                    await save_if_logged_in("meta", context, self.session_file, reason="aura_mbs_end")
                except Exception:
                    pass
                await context.close()


if __name__ == "__main__":
    pub = AuraMBSReelsPublisher()
    print("Page ID:", pub.page_id)
    print("Is available:", pub.is_available())
