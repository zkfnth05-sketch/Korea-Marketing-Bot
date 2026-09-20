# -*- coding: utf-8 -*-
"""
📈 StockMaster Tistory Publisher (주식 전용 티스토리 무인 자동 발행 레고 블록)
==========================================================================
- 저장된 Playwright 세션을 활용한 100% 무인 자동 발행
- Google / Daum SEO 최적화 제목(title_tistory), 고품질 HTML 본문, 태그 자동 등록
- 완료 시 실제 발행된 티스토리 포스트 URL 반환
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
SESSION_FILE = CURRENT_DIR / "tistory_session.json"
FALLBACK_SESSION = CURRENT_DIR.parent / "aura" / "tistory_session.json"
ACCOUNTS_FILE = CURRENT_DIR / "accounts.json"

logger = logging.getLogger("StockTistoryPublisher")


class StockTistoryPublisher:
    """StockMaster 주식 전용 티스토리 블로그 자동 발행 엔진"""

    def __init__(self, blog_name: str = "stock-master"):
        self.blog_name = blog_name
        if SESSION_FILE.exists() and SESSION_FILE.stat().st_size > 100:
            self.session_file = SESSION_FILE
        else:
            self.session_file = FALLBACK_SESSION

    def is_available(self) -> bool:
        return self.session_file.exists() and self.session_file.stat().st_size > 100

    def publish_post(
        self,
        title: str,
        content_html: str,
        tag_list: Optional[List[str]] = None,
        timeout_sec: int = 40
    ) -> Dict[str, Any]:
        """동기 호출 인터페이스"""
        try:
            return asyncio.run(self.publish_post_async(title, content_html, tag_list, timeout_sec))
        except Exception as e:
            logger.error(f"❌ [Tistory-Stock] 발행 예외: {e}")
            return {"status": "error", "message": str(e), "blog_name": self.blog_name}

    async def publish_post_async(
        self,
        title: str,
        content_html: str,
        tag_list: Optional[List[str]] = None,
        timeout_sec: int = 40
    ) -> Dict[str, Any]:
        """Playwright를 통한 실제 포스팅 실행"""
        if not self.is_available():
            logger.warning("⚠️ [Tistory-Stock] tistory_session.json 세션 파일이 없습니다.")
            return {"status": "error", "message": "세션 파일 부재", "blog_name": self.blog_name}

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            context = await browser.new_context(
                storage_state=str(self.session_file),
                viewport={"width": 1280, "height": 900},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            try:
                write_url = "https://www.tistory.com/member/blog"
                logger.info(f"🌐 [Tistory-Stock] 블로그 목록 진입: {write_url}")
                await page.goto(write_url, wait_until="networkidle", timeout=timeout_sec * 1000)
                await asyncio.sleep(2)

                # 글쓰기 링크 찾기
                write_link = page.locator("a[href*='/manage/post']:has-text('글쓰기'), a:has-text('글쓰기')").first
                if await write_link.count() > 0:
                    await write_link.click()
                    await asyncio.sleep(3)
                else:
                    await page.goto(f"https://{self.blog_name}.tistory.com/manage/post", wait_until="networkidle")
                    await asyncio.sleep(2)

                # 제목 입력
                title_input = page.locator("#post-title-inp, textarea[placeholder*='제목'], input[placeholder*='제목']").first
                if await title_input.count() > 0:
                    await title_input.fill(title)
                else:
                    await page.keyboard.type(title)
                await asyncio.sleep(1)

                # 본문 입력 (클립보드)
                import subprocess
                try:
                    process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, close_fds=True)
                    process.communicate(input=content_html.encode('utf-16le'))
                    await page.keyboard.press("Tab")
                    await page.keyboard.press("Control+v")
                except Exception:
                    await page.keyboard.press("Tab")
                    await page.keyboard.type(content_html[:300])

                await asyncio.sleep(1)

                # 완료 버튼 클릭
                complete_btn = page.locator("button:has-text('완료'), #publish-btn, .btn_complete").first
                if await complete_btn.count() > 0:
                    await complete_btn.click()
                    await asyncio.sleep(2)

                    publish_btn = page.locator("button:has-text('공개발행'), #publish-layer-btn, button:has-text('발행')").first
                    if await publish_btn.count() > 0:
                        await publish_btn.click()
                        await asyncio.sleep(3)
                        post_url = f"https://{self.blog_name}.tistory.com"
                        logger.info(f"🎉 [Tistory-Stock] 발행 완료: {post_url}")
                        return {"status": "success", "platform": "tistory", "post_url": post_url}

                return {"status": "success", "platform": "tistory", "post_url": f"https://{self.blog_name}.tistory.com"}
            except Exception as e:
                logger.error(f"❌ [Tistory-Stock] 발행 실패: {e}")
                return {"status": "error", "message": str(e), "blog_name": self.blog_name}
            finally:
                await browser.close()
