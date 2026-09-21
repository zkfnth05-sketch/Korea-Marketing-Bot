# -*- coding: utf-8 -*-
"""
📈 StockMaster Tistory Publisher (주식 전용 티스토리 무인 자동 발행 레고 블록)
========================================================================
- 크롬 영구 프로필 디렉터리(tistory_chrome_profile) 및 세션 파일(tistory_session.json)을 활용한 100% 무인 자동 발행
- Google / Daum SEO 최적화 제목(title_tistory), TinyMCE 공식 API 서식+사진+CTA HTML 주입
- '공개' 라디오 버튼 강제 체크 및 최종 발행 완료 URL 파싱
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
PROFILE_DIR = CURRENT_DIR / "tistory_chrome_profile"
FALLBACK_PROFILE = CURRENT_DIR.parent / "aura" / "tistory_chrome_profile"

SESSION_FILE = CURRENT_DIR / "tistory_session.json"
FALLBACK_SESSION = CURRENT_DIR.parent / "aura" / "tistory_session.json"
ACCOUNTS_FILE = CURRENT_DIR / "accounts.json"

logger = logging.getLogger("StockTistoryPublisher")


class StockTistoryPublisher:
    """StockMaster 주식 전용 티스토리 블로그 자동 발행 엔진 (영구 크롬 프로필/세션 지원)"""

    def __init__(self, blog_name: Optional[str] = None):
        loaded_name = "stockmaster-ai"
        if ACCOUNTS_FILE.exists():
            try:
                with open(ACCOUNTS_FILE, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    loaded_name = data.get("credentials", {}).get("tistory_blog_name") or "stockmaster-ai"
            except Exception:
                pass
        self.blog_name = blog_name or loaded_name
        # 프로필 디렉터리 결정 (자체 우선, 없으면 fallback)
        if PROFILE_DIR.exists() and any(PROFILE_DIR.iterdir()):
            self.profile_dir = PROFILE_DIR
        elif FALLBACK_PROFILE.exists() and any(FALLBACK_PROFILE.iterdir()):
            self.profile_dir = FALLBACK_PROFILE
        else:
            self.profile_dir = PROFILE_DIR

        # 세션 파일 결정
        if SESSION_FILE.exists() and SESSION_FILE.stat().st_size > 100:
            self.session_file = SESSION_FILE
        else:
            self.session_file = FALLBACK_SESSION

    def is_available(self) -> bool:
        has_profile = self.profile_dir.exists() and any(self.profile_dir.iterdir())
        has_session = self.session_file.exists() and self.session_file.stat().st_size > 100
        return has_profile or has_session

    def publish_post(
        self,
        title: str,
        content_html: str,
        tag_list: Optional[List[str]] = None,
        image_paths: Optional[List[str]] = None,
        timeout_sec: int = 40
    ) -> Dict[str, Any]:
        """동기 호출 인터페이스"""
        try:
            return asyncio.run(self.publish_post_async(title, content_html, tag_list, image_paths, timeout_sec))
        except Exception as e:
            logger.error(f"❌ [Tistory-Stock] 발행 예외: {e}")
            return {"status": "error", "message": str(e), "blog_name": self.blog_name}

    async def publish_post_async(
        self,
        title: str,
        content_html: str,
        tag_list: Optional[List[str]] = None,
        image_paths: Optional[List[str]] = None,
        timeout_sec: int = 40
    ) -> Dict[str, Any]:
        """Playwright를 통한 실제 포스팅 실행 (영구 프로필 / 세션 우선)"""
        if not self.is_available():
            logger.warning("⚠️ [Tistory-Stock] 티스토리 영구 프로필 또는 세션 파일이 없습니다.")
            return {"status": "error", "message": "세션 파일 부재", "blog_name": self.blog_name}

        write_url = f"https://{self.blog_name}.tistory.com/manage/newpost/?type=post&returnURL=%2Fmanage%2Fposts%2F"
        tags = tag_list or ["주식투자", "주식AI", "StockMaster", "종목분석", "퀀트투자"]

        logger.info(f"🚀 [Tistory-Stock] 무인 자동 발행 시작: '{title}'")

        async with async_playwright() as p:
            has_session_file = self.session_file.exists() and self.session_file.stat().st_size > 100
            is_persistent = self.profile_dir.exists() and any(self.profile_dir.iterdir())
            browser = None
            context = None

            if has_session_file:
                # 🌟 [1순위: 검증된 저장 세션 파일 모드]
                logger.info("📄 [Tistory-Stock] 저장된 세션 파일(storage_state)로 접속")
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
            elif is_persistent:
                # 🌟 [2순위: 영구 프로필 모드]
                logger.info(f"📂 [Tistory-Stock] 크롬 영구 프로필 모드로 실행: {self.profile_dir.name}")
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(self.profile_dir),
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"],
                    viewport={"width": 1280, "height": 900},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
                )
                page = context.pages[0] if context.pages else await context.new_page()
            else:
                return {"status": "error", "message": "티스토리 세션 부재 (1회연동 bat 실행 필요)", "blog_name": self.blog_name}

            try:
                # 1. 글쓰기 페이지 진입
                await page.goto(write_url, wait_until="domcontentloaded", timeout=timeout_sec * 1000)
                await asyncio.sleep(1)

                # 🛡️ 세션 만료 즉각 감지 (로그인 페이지 리다이렉트 확인)
                cur_url = page.url
                if "auth" in cur_url or "login" in cur_url or "accounts.kakao.com" in cur_url:
                    logger.warning("⚠️ [Tistory-Stock] 티스토리 세션 만료 감지 (1회 연동 로그인 필요)")
                    return {
                        "status": "session_expired",
                        "message": "티스토리 카카오 세션 만료. [1회연동]_주식AI_티스토리_영구로그인.bat 실행 필요",
                        "blog_name": self.blog_name
                    }

                # 2. 제목 입력기 대기 (유연한 선택자 지원)
                title_el = await page.wait_for_selector("#post-title-inp, textarea[id*='title'], input[name='title']", timeout=15000)
                if not title_el:
                    raise RuntimeError("티스토리 제목 입력 필드를 찾을 수 없습니다.")

                # 2. 제목 입력
                await title_el.fill(title)

                # 3. 🌟 16:9 / 와이드 고화질 대표 캡처 사진 먼저 업로드
                if image_paths and len(image_paths) > 0 and Path(image_paths[0]).exists():
                    img_file = Path(image_paths[0]).resolve()
                    try:
                        attach_btn = await page.query_selector("#mceu_0-open, [id*='mceu_0']")
                        if attach_btn:
                            await attach_btn.click()
                            await asyncio.sleep(0.8)
                            photo_item = await page.wait_for_selector("#attach-image, .mce-tistory-attach-item:has-text('사진')", timeout=5000)
                            if photo_item:
                                async with page.expect_file_chooser(timeout=8000) as fc_info:
                                    await photo_item.click()
                                fc = await fc_info.value
                                await fc.set_files(str(img_file))
                                logger.info(f"📸 [Tistory-Stock] 대표 이미지 업로드 완료: {img_file.name}")
                                await asyncio.sleep(4.0)
                    except Exception as e:
                        logger.warning(f"⚠️ [Tistory-Stock] 사진 업로드 통과: {e}")

                # 4. 본문 HTML 주입 (사진 뒤에 이어서 본문 동기화)
                injected = await page.evaluate("""(html) => {
                    if (window.tinymce && window.tinymce.activeEditor) {
                        const cur = window.tinymce.activeEditor.getContent();
                        window.tinymce.activeEditor.setContent(cur ? cur + "<br/><br/>" + html : html);
                        if (window.tinymce.triggerSave) window.tinymce.triggerSave();
                        if (window.tinymce.activeEditor.save) window.tinymce.activeEditor.save();
                        window.tinymce.activeEditor.fire('change');
                        return true;
                    }
                    return false;
                }""", content_html)

                if injected:
                    logger.info("✅ [Tistory-Stock] TinyMCE 공식 엔진 및 버퍼 동기화(사진+서식+CTA) 완료")
                else:
                    logger.warning("⚠️ [Tistory-Stock] TinyMCE 객체 미감지, iframe DOM 직접 주입 시도")
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
                    const targets = Array.from(document.querySelectorAll('span.checkbox-text, label, .form-field'));
                    const openTarget = targets.find(l => l.innerText && l.innerText.trim() === '공개');
                    if (openTarget) openTarget.click();
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
                logger.info(f"✅ [Tistory-Stock] 발행 후 리다이렉트 URL: {final_url}")

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

                # 🌟 [세션 자동 수명 연장] 살아있는 최신 세션 상태를 디스크에 즉시 자동 저장
                try:
                    await context.storage_state(path=str(self.session_file))
                    logger.info("🔄 [Tistory-Stock] 세션 쿠키 수명 자동 연장 완료 (Auto-Renewed)")
                except Exception as save_err:
                    logger.debug(f"세션 연장 통과: {save_err}")

                logger.info(f"🎉 [Tistory-Stock] 최종 공개 발행 성공! {post_url}")
                return {
                    "status": "success",
                    "blog_name": self.blog_name,
                    "title": title,
                    "url": post_url,
                    "post_url": post_url,
                    "tags": tags
                }

            except Exception as e:
                logger.error(f"❌ [Tistory-Stock] 포스팅 실패: {e}")
                return {
                    "status": "error",
                    "blog_name": self.blog_name,
                    "message": str(e)
                }
            finally:
                if is_persistent:
                    await context.close()
                else:
                    await context.close()
                    if browser:
                        await browser.close()


if __name__ == "__main__":
    pub = StockTistoryPublisher()
    print("Is available:", pub.is_available())
