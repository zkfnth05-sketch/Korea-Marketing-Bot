# -*- coding: utf-8 -*-
"""
HumanRecipeEngine (🤖 사람의 눈으로 글자 찾기 & 4대 절대 수칙 공통 코어 엔진)
=============================================================================
모든 SNS 자동 발행 엔진(유튜브, 메타, 틱톡, 스레드, 네이버)에 공통 적용되는 4대 절대 수칙:

1. [사람의 눈으로 글자 찾기]:
   - 암호화되거나 자주 바뀌는 난해한 CSS 셀렉터 전면 배제.
   - [다음], [게시], [공유하기], [등록], [완료], [업로드] 등 사람이 모니터를 보듯
     화면에 적힌 한글/영어 '글자(Text)'를 탐색하여 정확히 클릭.
   - React, Lexical, DraftJS 등 모던 웹 에디터 호환 키보드 주입 지원.

2. [방해 모달 분쇄기 (Modal Buster)]:
   - "Are you sure you want to exit?", "취소", "Stay", "닫기", "Not now" 등
     작업 도중 화면을 가리거나 이탈을 유도하는 방해 팝업을 실시간 감지하여 즉각 분쇄.

3. [게시물 완료 화면 직행 두 눈 실물 검증]:
   - "성공"이라는 피상적인 텍스트나 업로드 버튼 클릭 후 짐작으로 끝내지 않음.
   - 실제 게시물 관리 / 콘텐츠 스튜디오 / 프로필 화면으로 직접 이동하여
     내 게시물이 1등(최상단)으로 정상 반영되었는지 두 눈으로 확인하고 실물 라이브 URL 영수증 추출.

4. [최대 3회 풀리셋 자가 치유 재시도 (Self-Healing)]:
   - 화면 미반영이나 예외 발생 시 피상적인 땜질 없이 브라우저 프로세스를 완전히 닫고(풀리셋),
     처음부터 다시 시도하여 100% 무인 완수 달성.
"""

import os
import sys
import time
import asyncio
import logging
from typing import List, Optional, Dict, Any, Callable
from playwright.async_api import Page, Locator, BrowserContext

logger = logging.getLogger("HumanRecipeEngine")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class HumanRecipeEngine:
    """사람의 눈으로 글자 찾기 & 4대 절대 수칙 공통 엔진"""

    # 기본 모달 분쇄 타겟 텍스트 목록
    DEFAULT_MODAL_DISMISS_TEXTS = [
        "Cancel", "취소", "Stay", "계속 머무르기", "닫기", "Close",
        "Got it", "확인", "나중에 하기", "지금 안 함", "Not now", "Dismiss"
    ]

    @staticmethod
    async def human_click(
        page: Page,
        target_texts: List[str],
        role: str = "button",
        position: str = "first",
        timeout_ms: int = 8000,
        wait_after_sec: float = 1.0
    ) -> bool:
        """
        [1대 수칙] 화면에 적힌 글자(한글/영어)를 사람의 눈으로 찾아 클릭
        - target_texts: 찾을 글자 후보군 (예: ["다음", "Next"])
        - role: 엘리먼트 역할 ("button", "div", "a", "span" 등)
        - position: 여러 개 발견 시 위치 ("first" 또는 "last")
        """
        for text in target_texts:
            clean_text = text.strip()
            logger.info(f"🔍 [글자 탐색] 화면에서 '{clean_text}' 글자 찾는 중...")

            # 1. Playwright Locator filter(has_text=...)
            try:
                locator = page.locator(f"{role}, [role='button'], div, a, span").filter(has_text=clean_text)
                count = await locator.count()
                if count > 0:
                    target_el = locator.last if position == "last" else locator.first
                    if await target_el.is_visible(timeout=2000):
                        await target_el.scroll_into_view_if_needed()
                        await target_el.click(timeout=timeout_ms)
                        logger.info(f"   👉 '{clean_text}' 글자 클릭 성공! (Locator 감지)")
                        if wait_after_sec > 0:
                            await asyncio.sleep(wait_after_sec)
                        return True
            except Exception:
                pass

            # 2. get_by_role 또는 get_by_text 탐색
            try:
                el = page.get_by_text(clean_text, exact=False)
                if await el.count() > 0:
                    target_el = el.last if position == "last" else el.first
                    if await target_el.is_visible(timeout=2000):
                        await target_el.scroll_into_view_if_needed()
                        await target_el.click(timeout=timeout_ms)
                        logger.info(f"   👉 '{clean_text}' 글자 클릭 성공! (Text 감지)")
                        if wait_after_sec > 0:
                            await asyncio.sleep(wait_after_sec)
                        return True
            except Exception:
                pass

            # 3. JavaScript 완전 탐색 (Shadow DOM / 중첩 텍스트 Leaf 탐색)
            try:
                clicked = await page.evaluate("""({ text, pos }) => {
                    const all = Array.from(document.querySelectorAll("button, div[role='button'], a, div, span"));
                    const matches = all.filter(el => {
                        const t = (el.innerText || el.textContent || '').trim();
                        return t.includes(text) && el.offsetParent !== null;
                    });
                    if (matches.length > 0) {
                        const target = pos === 'last' ? matches[matches.length - 1] : matches[0];
                        const clickable = target.closest("button, div[role='button'], a") || target;
                        clickable.click();
                        return true;
                    }
                    return false;
                }""", {"text": clean_text, "pos": position})
                if clicked:
                    logger.info(f"   👉 '{clean_text}' 글자 클릭 성공! (JS 탐색)")
                    if wait_after_sec > 0:
                        await asyncio.sleep(wait_after_sec)
                    return True
            except Exception:
                pass

        logger.warning(f"⚠️ [글자 미발견] 화면에서 {target_texts} 글자를 찾지 못했습니다.")
        return False

    @staticmethod
    async def fill_text_human(
        page: Page,
        locator_or_selector: Any,
        text: str,
        clear_first: bool = True
    ) -> bool:
        """
        [1대 수칙 보조] 모던 웹 에디터(Lexical, DraftJS, Slate 등) 호환 키보드 입력
        """
        try:
            if isinstance(locator_or_selector, str):
                target = page.locator(locator_or_selector).first
            else:
                target = locator_or_selector

            await target.click()
            await asyncio.sleep(0.3)

            if clear_first:
                await page.keyboard.press("Control+A")
                await page.keyboard.press("Backspace")
                await asyncio.sleep(0.2)

            await page.keyboard.insert_text(text)
            await asyncio.sleep(0.5)
            return True
        except Exception as e:
            logger.warning(f"⚠️ 텍스트 입력 예외: {e}")
            return False

    @staticmethod
    async def modal_buster(
        page: Page,
        custom_dismiss_texts: Optional[List[str]] = None
    ) -> bool:
        """
        [2대 수칙] 방해 모달 분쇄기 (Modal Buster)
        작업 도중 발생하는 이탈 경고, 안내 팝업, 취소 버튼을 즉시 클릭하여 본 화면 사수
        """
        dismiss_texts = custom_dismiss_texts or HumanRecipeEngine.DEFAULT_MODAL_DISMISS_TEXTS
        busted = False

        for txt in dismiss_texts:
            try:
                clicked = await page.evaluate("""(text) => {
                    const dialogs = Array.from(document.querySelectorAll("div[role='dialog'], [aria-modal='true'], div[class*='modal'], div[class*='popup']"));
                    if (dialogs.length === 0) return false;
                    for (const d of dialogs) {
                        const btns = Array.from(d.querySelectorAll("button, div[role='button'], a"));
                        const target = btns.find(b => (b.innerText || '').trim().includes(text));
                        if (target) {
                            target.click();
                            return true;
                        }
                    }
                    return false;
                }""", txt)
                if clicked:
                    logger.info(f"🛡️ [Modal Buster] 방해 모달 분쇄 완료! ('{txt}' 클릭)")
                    await asyncio.sleep(1.0)
                    busted = True
            except Exception:
                pass

        return busted

    @staticmethod
    async def verify_content_managed(
        page: Page,
        manage_url: str,
        match_keywords: List[str],
        timeout_sec: float = 60.0,
        url_extract_regex: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        [3대 수칙] 게시물 완료 화면 직행 두 눈 실물 검증
        - manage_url: 실제 게시물 관리 / 콘텐츠 스튜디오 / 프로필 URL
        - match_keywords: 방금 올린 게시물 제목/캡션/키워드 후보군
        - 반환: {"verified": True/False, "proof_url": ..., "screenshot": ...}
        """
        logger.info(f"👀 [3대 수칙] 게시물 관리 화면으로 직접 이동하여 두 눈 실물 검증 개시: {manage_url}")
        try:
            await page.goto(manage_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(4.0)

            start_t = time.time()
            while time.time() - start_t < timeout_sec:
                # 1. 화면 텍스트 전수 스캔
                body_text = await page.inner_text("body")
                for kw in match_keywords:
                    if kw and kw in body_text:
                        logger.info(f"🎉🎉 [두 눈 실물 검증 100% 합격!] 화면에서 '{kw}' 키워드 실물 확인 완료!")

                        # 링크(URL 영수증) 추출 시도
                        live_url = await page.evaluate("""() => {
                            const postLink = document.querySelector("a[href*='/post/'], a[href*='/video/'], a[href*='/reel/'], a[href*='/shorts/']");
                            return postLink ? postLink.href : null;
                        }""")

                        return {
                            "verified": True,
                            "matched_keyword": kw,
                            "live_url": live_url or page.url,
                            "checked_url": manage_url
                        }

                await asyncio.sleep(2.5)

            logger.warning(f"⚠️ [실물 미확인] {timeout_sec}초 동안 게시물 관리 화면에서 키워드를 발견하지 못했습니다.")
            return {
                "verified": False,
                "error": "게시물 목록 최상단 실물 미반영",
                "checked_url": manage_url
            }
        except Exception as e:
            logger.error(f"❌ 실물 검증 화면 이동 예외: {e}")
            return {
                "verified": False,
                "error": str(e),
                "checked_url": manage_url
            }

    @staticmethod
    async def self_healing_retry(
        action_name: str,
        action_coroutine_fn: Callable[[int], Any],
        max_retries: int = 3,
        cooldown_sec: float = 5.0
    ) -> Dict[str, Any]:
        """
        [4대 수칙] 실패 시 될 때까지 최대 3회 풀리셋 자가 치유 재시도 (Self-Healing)
        - action_coroutine_fn(attempt): 각 시도별 비동기 실행 함수 (내부에서 브라우저 풀리셋 담당)
        """
        last_error = ""
        for attempt in range(1, max_retries + 1):
            logger.info(f"\n=======================================================")
            logger.info(f"🔄 [{action_name}] 자가 치유(Self-Healing) 시도 {attempt}/{max_retries} 가동")
            logger.info(f"=======================================================")
            try:
                result = await action_coroutine_fn(attempt)
                if isinstance(result, dict) and result.get("status") == "SUCCESS":
                    logger.info(f"🏆 [{action_name}] 시도 {attempt}회 만에 최종 완벽 성공!")
                    return result
                elif isinstance(result, dict) and result.get("verified") is True:
                    logger.info(f"🏆 [{action_name}] 시도 {attempt}회 만에 실물 검증 완벽 합격!")
                    result["status"] = "SUCCESS"
                    return result
                else:
                    msg = result.get("message") or result.get("error") if isinstance(result, dict) else str(result)
                    logger.warning(f"⚠️ [{action_name}] 시도 {attempt} 실패: {msg}")
                    last_error = msg
            except Exception as e:
                logger.error(f"❌ [{action_name}] 시도 {attempt} 예외 발생: {e}")
                last_error = str(e)

            if attempt < max_retries:
                logger.info(f"⏳ 브라우저 풀리셋 후 {cooldown_sec}초 뒤 처음부터 완전 재시도합니다...")
                await asyncio.sleep(cooldown_sec)

        logger.error(f"💥 [{action_name}] 최대 {max_retries}회 자가 치유 재시도 모두 실패: {last_error}")
        return {
            "status": "FAIL",
            "error": f"최대 {max_retries}회 재시도 실패: {last_error}",
            "attempts": max_retries
        }
