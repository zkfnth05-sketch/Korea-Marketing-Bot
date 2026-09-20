# -*- coding: utf-8 -*-
"""
Aura Tistory Publisher (💖 Aura 전용 티스토리 무인 자동 발행 레고 블록)
====================================================================
- 저장된 Playwright 세션(tistory_session.json)을 활용한 100% 무인 자동 발행
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
ACCOUNTS_FILE = CURRENT_DIR / "accounts.json"

logger = logging.getLogger("AuraTistoryPublisher")


class AuraTistoryPublisher:
    """Aura 데이팅 전용 티스토리 블로그 자동 발행 엔진"""

    def __init__(self, blog_name: str = "aura-magazine"):
        self.blog_name = blog_name
        self.session_file = SESSION_FILE

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
            logger.error(f"❌ [Tistory] 발행 예외: {e}")
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
            logger.warning("⚠️ [Tistory] tistory_session.json 세션 파일이 없습니다.")
            return {"status": "error", "message": "세션 파일 부재", "blog_name": self.blog_name}

        write_url = f"https://{self.blog_name}.tistory.com/manage/newpost/?type=post&returnURL=%2Fmanage%2Fposts%2F"
        tags = tag_list or ["Aura", "소개팅", "연애심리", "2030매거진"]

        logger.info(f"🚀 [Tistory] 무인 자동 발행 시작: '{title}'")

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"]
            )
            context = await browser.new_context(
                storage_state=str(self.session_file),
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 900}
            )
            page = await context.new_page()

            try:
                # 1. 글쓰기 페이지 진입
                await page.goto(write_url, wait_until="domcontentloaded", timeout=timeout_sec * 1000)
                await page.wait_for_selector("#post-title-inp", timeout=15000)

                # 2. 제목 입력
                await page.fill("#post-title-inp", title)

                # 3. 본문 HTML 주입 (TinyMCE 공식 엔진 버퍼 및 폼 텍스트에어리어 동기화)
                injected = await page.evaluate("""(html) => {
                    if (window.tinymce && window.tinymce.activeEditor) {
                        window.tinymce.activeEditor.setContent(html);
                        if (window.tinymce.triggerSave) window.tinymce.triggerSave();
                        if (window.tinymce.activeEditor.save) window.tinymce.activeEditor.save();
                        window.tinymce.activeEditor.fire('change');
                        return true;
                    }
                    return false;
                }""", content_html)

                if injected:
                    logger.info("✅ [Tistory] TinyMCE 공식 엔진 및 버퍼 동기화(사진+서식+CTA) 완료")
                else:
                    logger.warning("⚠️ [Tistory] TinyMCE 객체 미감지, iframe DOM 직접 주입 시도")
                    frame = page.frame(name="editor-tistory_ifr")
                    if frame:
                        await frame.evaluate("(html) => { document.body.innerHTML = html; }", content_html)

                await asyncio.sleep(1.5)

                # 4. 태그 등록
                tag_inp = await page.query_selector("#tagText")
                if tag_inp:
                    for t in tags[:10]:
                        clean_t = t.replace("#", "").strip()
                        if clean_t:
                            await tag_inp.fill(clean_t)
                            await page.keyboard.press("Enter")
                            await asyncio.sleep(0.2)

                # 5. [완료] 레이어 버튼 클릭
                layer_btn = await page.wait_for_selector("#publish-layer-btn", timeout=10000)
                await layer_btn.click()
                await asyncio.sleep(1)

                # 6. '공개' 라디오 버튼 강제 체크
                await page.evaluate("""() => {
                    const labels = Array.from(document.querySelectorAll('label'));
                    const openLabel = labels.find(l => l.textContent.trim() === '공개');
                    if (openLabel) openLabel.click();
                    const openInput = document.querySelector('input[id*="open"]');
                    if (openInput) openInput.checked = true;
                }""")
                await asyncio.sleep(1)

                # 7. [공개발행 / 발행] 버튼 클릭
                pub_btn = await page.wait_for_selector("#publish-btn", timeout=10000)
                await pub_btn.click()

                # 8. 발행 완료 대기 (URL 변경 또는 리스트 이동 감지)
                try:
                    await page.wait_for_url(lambda u: "newpost" not in u, timeout=20000)
                except Exception:
                    await asyncio.sleep(4)

                final_url = page.url
                logger.info(f"✅ [Tistory] 발행 후 리다이렉트 URL: {final_url}")

                # 최신 포스트 URL 파싱 (리스트 페이지에 있을 경우 최상단 글 링크 획득)
                post_url = final_url
                if "manage/posts" in final_url or "manage" in final_url:
                    first_link = await page.query_selector(".table_post tbody tr:first-child a.link_title, a[class*='link_title'], a.link_post")
                    if first_link:
                        href = await first_link.get_attribute("href")
                        if href:
                            if href.startswith("http"):
                                post_url = href
                            else:
                                post_url = f"https://{self.blog_name}.tistory.com{href}"

                logger.info(f"🎉 [Tistory] 최종 공개 발행 성공! {post_url}")
                return {
                    "status": "success",
                    "blog_name": self.blog_name,
                    "title": title,
                    "url": post_url,
                    "tags": tags
                }

            except Exception as e:
                logger.error(f"❌ [Tistory] 포스팅 실패: {e}")
                return {
                    "status": "error",
                    "blog_name": self.blog_name,
                    "message": str(e)
                }
            finally:
                await browser.close()


if __name__ == "__main__":
    pub = AuraTistoryPublisher()
    print("Is available:", pub.is_available())
