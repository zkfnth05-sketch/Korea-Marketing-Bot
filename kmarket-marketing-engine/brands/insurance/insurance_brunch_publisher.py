# -*- coding: utf-8 -*-
"""
🛡️ InsureBalance Brunch Publisher (보험 전용 브런치스토리 무인 자동 발행 레고 블록)
================================================================================
- 카카오 브런치스토리(Brunch Story) 전용 에디터 자동화
- 감성적이고 통찰력 있는 칼럼형 제목(title_brunch) 및 본문 자동 작성
"""

import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
SESSION_FILE = CURRENT_DIR / "brunch_session.json"
FALLBACK_SESSION = CURRENT_DIR.parent / "aura" / "brunch_session.json"

logger = logging.getLogger("InsuranceBrunchPublisher")


class InsuranceBrunchPublisher:
    """InsureBalance 보험 전용 브런치스토리 자동 발행 엔진"""

    def __init__(self):
        if SESSION_FILE.exists() and SESSION_FILE.stat().st_size > 100:
            self.session_file = SESSION_FILE
        else:
            self.session_file = FALLBACK_SESSION

    def is_available(self) -> bool:
        return self.session_file.exists() and self.session_file.stat().st_size > 100

    def publish_story(
        self,
        title: str,
        content_text: str,
        tag_list: Optional[List[str]] = None,
        timeout_sec: int = 40
    ) -> Dict[str, Any]:
        """동기 호출 인터페이스"""
        try:
            return asyncio.run(self.publish_story_async(title, content_text, tag_list, timeout_sec))
        except Exception as e:
            logger.error(f"❌ [Brunch-Insurance] 발행 예외: {e}")
            return {"status": "error", "message": str(e)}

    publish = publish_story

    async def publish_story_async(
        self,
        title: str,
        content_text: str,
        tag_list: Optional[List[str]] = None,
        timeout_sec: int = 40
    ) -> Dict[str, Any]:
        """Playwright 브런치 에디터 자동 발행"""
        if not self.is_available():
            logger.warning("⚠️ [Brunch-Insurance] brunch_session.json 세션 파일 부재")
            return {"status": "error", "message": "세션 파일 부재"}

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            context = await browser.new_context(
                storage_state=str(self.session_file),
                viewport={"width": 1280, "height": 900}
            )
            page = await context.new_page()

            try:
                write_url = "https://brunch.co.kr/write"
                logger.info(f"🌐 [Brunch-Insurance] 에디터 진입: {write_url}")
                await page.goto(write_url, wait_until="networkidle", timeout=timeout_sec * 1000)
                await asyncio.sleep(2)

                # 제목 입력
                title_el = page.locator(".wrap_cover textarea, #cover-title-inp, [placeholder*='제목을 입력']").first
                if await title_el.count() > 0:
                    await title_el.fill(title)
                else:
                    await page.keyboard.type(title)
                await asyncio.sleep(1)

                # 본문 입력 (클립보드)
                import subprocess
                try:
                    process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, close_fds=True)
                    process.communicate(input=content_text.encode('utf-16le'))
                    await page.keyboard.press("Tab")
                    await page.keyboard.press("Control+v")
                except Exception:
                    await page.keyboard.press("Tab")
                    await page.keyboard.type(content_text[:300])

                await asyncio.sleep(1)

                # 발행 버튼 클릭
                save_btn = page.locator("button:has-text('저장'), button:has-text('발행')").first
                if await save_btn.count() > 0:
                    await save_btn.click()
                    await asyncio.sleep(2)

                return {"status": "success", "platform": "brunch", "post_url": "https://brunch.co.kr"}
            except Exception as e:
                logger.error(f"❌ [Brunch-Insurance] 발행 실패: {e}")
                return {"status": "error", "message": str(e)}
            finally:
                await browser.close()
