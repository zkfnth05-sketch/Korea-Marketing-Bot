# -*- coding: utf-8 -*-
"""
Aura Tistory Publisher (Aura 전용 티스토리 무인 자동 발행 레고 블록)
====================================================================
- 크롬 영구 프로필 디렉터리(tistory_chrome_profile)를 활용한 100% 무인 자동 발행 (로그인 영구 보존)
- Google / Daum SEO 최적화 제목(title_tistory), 고품질 HTML 본문, 태그 자동 등록
- 완료 시 실제 발행된 티스토리 포스트 URL 반환
"""

import sys
import time
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from core.engine.session_integrity import load_best_cookies, sanitize_for_playwright, has_auth, safe_save, ensure_auth_cookies

PROFILE_DIR = CURRENT_DIR / "tistory_chrome_profile"
SESSION_FILE = CURRENT_DIR / "tistory_session.json"
ACCOUNTS_FILE = CURRENT_DIR / "accounts.json"

logger = logging.getLogger("AuraTistoryPublisher")


class AuraTistoryPublisher:
    """Aura 전용 티스토리 블로그 자동 발행 엔진 (영구 크롬 프로필 지원)"""

    def __init__(self, blog_name: Optional[str] = None):
        if blog_name:
            self.blog_name = blog_name
        elif ACCOUNTS_FILE.exists():
            try:
                with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                    acc = json.load(f)
                    self.blog_name = acc.get("credentials", {}).get("tistory_blog_name") or "aura-magazine"
            except Exception:
                self.blog_name = "aura-magazine"
        else:
            self.blog_name = "aura-magazine"

        self.profile_dir = PROFILE_DIR
        self.session_file = SESSION_FILE
        self.brand = "aura"

    def is_available(self) -> bool:
        has_profile = self.profile_dir.exists() and any(self.profile_dir.iterdir())
        has_session = self.session_file.exists() and self.session_file.stat().st_size > 100
        return has_profile or has_session

    def _cleanup_profile_locks(self):
        """Chromium 충돌 및 락 방지 클린업"""
        for fname in ["SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile"]:
            lp = self.profile_dir / fname
            if lp.exists():
                try:
                    lp.unlink()
                except Exception:
                    pass

    async def _inject_saved_cookies(self, context):
        """🛡️ [티스토리 영구 세션 보호]: 티스토리 인증 쿠키 부재 시 .good.json 백업 쿠키 즉각 주입"""
        existing_cookies = await context.cookies()
        if not has_auth("tistory", existing_cookies):
            best = load_best_cookies("tistory", self.session_file)
            if best:
                for c in sanitize_for_playwright(best):
                    try:
                        await context.add_cookies([c])
                    except Exception:
                        pass
                logger.info(f"   🍪 [Tistory-{self.brand}] 인증 쿠키 부재 감지 -> .good.json 백업 쿠키 {len(best)}개 즉시 주입 복원 완료")
            elif self.session_file.exists() and self.session_file.stat().st_size > 100:
                try:
                    with open(self.session_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        cookies = data.get("cookies", [])
                        if cookies:
                            await context.add_cookies(cookies)
                            logger.info(f"   🍪 [Tistory-{self.brand}] 세션 쿠키 {len(cookies)}개 폴백 주입 완료")
                except Exception as e:
                    logger.debug(f"[Tistory-{self.brand}] 쿠키 주입 스킵: {e}")
        else:
            logger.info(f"   🔐 [Tistory-{self.brand} 영구 세션 보호] 티스토리 SSO 세션 유지")

    def keep_alive_session(self) -> Dict[str, Any]:
        """
        🔄 [24시간 무활동 만료 방지 킵얼라이브]
        티스토리 메인/관리자 홈에 접속하여 카카오 SSO 세션 수명을 상시 연장
        """
        if not self.is_available():
            return {"status": "skipped", "message": "티스토리 세션 미연동 상태"}

        try:
            return asyncio.run(self._keep_alive_async())
        except Exception as e:
            logger.warning(f"⚠️ [Tistory Keep-Alive 예외] {e}")
            return {"status": "error", "message": str(e)}

    async def _auto_recover_sso(self, page, context, target_write_url: str) -> bool:
        """카카오 SSO 및 간편로그인 화면에서 원클릭으로 세션을 실시간 자동 복구"""
        try:
            logger.info("🔄 [Tistory-aura SSO 복구] 카카오 간편로그인 브릿지 가동...")
            cur_url = page.url
            if "auth/login" in cur_url or "login" in cur_url:
                kakao_btn = await page.query_selector("a.btn_login.link_kakao_id, .link_kakao, a[href*='accounts.kakao.com']")
                if kakao_btn:
                    await kakao_btn.click(force=True)
                    await asyncio.sleep(2.5)

            # 간편로그인 등록 계정 버튼 탐색 (.wrap_profile, a.link_profile, .item_account a, .link_name)
            prof_links = await page.query_selector_all("a.wrap_profile, a.link_profile, .item_account a, .link_name, [data-type='account']")
            prof_btn = None
            for pl in prof_links:
                txt = await pl.inner_text()
                if "새로운 계정" not in txt:
                    prof_btn = pl
                    break
            if not prof_btn and prof_links:
                prof_btn = prof_links[0]

            if prof_btn:
                logger.info("👉 [Tistory-aura SSO 복구] 등록된 간편 카카오 프로필 원클릭 선택...")
                await prof_btn.click(force=True)
                
                # 카카오 OAuth 리다이렉트 대기 (tistory.com 복귀 대기)
                try:
                    await page.wait_for_url(
                        lambda u: "tistory.com" in u and "accounts.kakao.com" not in u and "kauth.kakao.com" not in u,
                        timeout=12000
                    )
                except Exception:
                    await asyncio.sleep(3.0)

            # 글쓰기 페이지로 재진입
            await page.goto(target_write_url, wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(2.0)

            cur_url = page.url
            if "manage/newpost" in cur_url and "auth/login" not in cur_url and "accounts.kakao.com" not in cur_url:
                logger.info("🎉 [Tistory-aura SSO 복구 성공] 티스토리 글쓰기 페이지에 정상 복구 진입했습니다!")
                try:
                    await context.storage_state(path=str(self.session_file))
                except Exception:
                    pass
                return True
            else:
                logger.warning(f"⚠️ [Tistory-aura SSO 복구 미완료] 현재 URL: {cur_url}")
                return False
        except Exception as e:
            logger.warning(f"⚠️ [Tistory-aura SSO 복구 예외] {e}")
            return False

    async def _keep_alive_async(self) -> Dict[str, Any]:
        self._cleanup_profile_locks()
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-first-run",
                    "--no-default-browser-check"
                ],
                viewport={"width": 1280, "height": 900},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            )
            await self._inject_saved_cookies(context)
            page = context.pages[0] if context.pages else await context.new_page()
            try:
                # 관리자 또는 메인 페이지 접속으로 세션 활성 유지
                target_url = f"https://{self.blog_name}.tistory.com/manage"
                await page.goto(target_url, wait_until="domcontentloaded", timeout=15000)
                await asyncio.sleep(1.5)
                cur_url = page.url

                if "auth/login" in cur_url or "accounts.kakao.com" in cur_url:
                    write_url = f"https://{self.blog_name}.tistory.com/manage/newpost/?type=post"
                    recovered = await self._auto_recover_sso(page, context, write_url)
                    if recovered:
                        cur_url = page.url

                cookies = await context.cookies()
                cookie_dict = {c["name"]: c["value"] for c in cookies}
                has_auth = any(k in cookie_dict for k in ["TSSESSION", "_T_ID", "TSID", "_kawlt", "_T_ANO", "_kawask"]) or ("/manage" in cur_url and "login" not in cur_url and "auth" not in cur_url)

                if has_auth and "auth/login" not in cur_url and "accounts.kakao.com" not in cur_url:
                    await context.storage_state(path=str(self.session_file))
                    logger.info("🎉 [Tistory Keep-Alive 성공] 카카오 티스토리 세션 수명이 24시간 자동 연장되었습니다.")
                    return {"status": "active", "message": "세션 정상 유지 및 자동 갱신 완료"}
                else:
                    logger.warning(f"⚠️ [Tistory Keep-Alive] 세션 만료 감지, 백업 복원 시도 (URL: {cur_url})")
                    best = load_best_cookies("tistory", self.session_file)
                    if best:
                        for c in sanitize_for_playwright(best):
                            try:
                                await context.add_cookies([c])
                            except Exception:
                                pass
                        await page.goto(target_url, wait_until="domcontentloaded", timeout=15000)
                        await asyncio.sleep(1.5)
                        cur_url2 = page.url
                        if "auth/login" not in cur_url2 and "accounts.kakao.com" not in cur_url2:
                            logger.info("[RESTORE] 백업 쿠키 주입으로 티스토리 세션 자동 복원 성공!")
                            return {"status": "restored", "message": "백업에서 세션 복원 완료"}
                    return {"status": "session_expired", "message": "카카오 세션 만료"}
            finally:
                await context.close()

    def publish_post(
        self,
        title: str,
        content_html: str,
        tag_list: Optional[List[str]] = None,
        timeout_sec: int = 40
    ) -> Dict[str, Any]:
        """동기 호출 인터페이스 (세션 만료 시 백업 복원 및 최대 3회 자동 재시도 내장)"""
        last_res = {"status": "error", "message": "발행 실패"}
        for attempt in range(1, 4):
            try:
                res = asyncio.run(self.publish_post_async(title, content_html, tag_list, timeout_sec))
                if res.get("status") in ("success", "active", "restored"):
                    return res
                last_res = res
                logger.warning(f"⚠️ [Tistory-{self.brand}] 발행 시도 {attempt}/3 실패: {res.get('status')} ({res.get('message')}) - 5초 후 재시도...")
                time.sleep(5)
            except Exception as e:
                logger.error(f"❌ [Tistory-{self.brand}] 발행 시도 {attempt}/3 예외: {e}")
                last_res = {"status": "error", "message": str(e), "blog_name": self.blog_name}
                time.sleep(5)
        return last_res

    async def publish_post_async(
        self,
        title: str,
        content_html: str,
        tag_list: Optional[List[str]] = None,
        timeout_sec: int = 40
    ) -> Dict[str, Any]:
        """Playwright를 통한 실제 포스팅 실행 (영구 프로필 우선)"""
        if not self.is_available():
            logger.warning("⚠️ [Tistory] 티스토리 세션 또는 프로필이 없습니다.")
            return {"status": "error", "message": "세션 파일 부재", "blog_name": self.blog_name}

        self._cleanup_profile_locks()
        write_url = f"https://{self.blog_name}.tistory.com/manage/newpost/?type=post&returnURL=%2Fmanage%2Fposts%2F"
        tags = tag_list or ["Aura", "소개팅", "연애심리", "2030매거진"]

        logger.info(f"🚀 [Tistory] 무인 자동 발행 시작: '{title}'")

        async with async_playwright() as p:
            has_session_file = self.session_file.exists() and self.session_file.stat().st_size > 100
            is_persistent = self.profile_dir.exists() and any(self.profile_dir.iterdir())
            browser = None
            context = None

            if is_persistent:
                # 🌟 [1순위: 크롬 영구 프로필 모드 - 카카오 세션 자동 연장 & 영구 유지]
                logger.info(f"📂 [Tistory-aura] 크롬 영구 프로필 모드로 실행: {self.profile_dir.name}")
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(self.profile_dir),
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-first-run",
                        "--no-default-browser-check"
                    ],
                    viewport={"width": 1280, "height": 900},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
                )
                await self._inject_saved_cookies(context)
                page = context.pages[0] if context.pages else await context.new_page()
            elif has_session_file:
                # 🌟 [2순위: 세션 파일 폴백]
                logger.info("📄 [Tistory-aura] 저장된 세션 파일(storage_state)로 접속")
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
            else:
                # 세션 파일 없음 → 백업에서 비상 복원 시도
                best = load_best_cookies("tistory", self.session_file)
                if best:
                    logger.info("[RESTORE] 티스토리 세션 없음 → .good.json 백업에서 비상 주입 시도")
                    browser = await p.chromium.launch(
                        headless=True,
                        args=["--disable-blink-features=AutomationControlled"]
                    )
                    context = await browser.new_context(
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                        viewport={"width": 1280, "height": 900}
                    )
                    for c in sanitize_for_playwright(best):
                        try:
                            await context.add_cookies([c])
                        except Exception:
                            pass
                    page = await context.new_page()
                else:
                    return {"status": "error", "message": "티스토리 세션 부재 ([1회연동] bat 실행 필요)", "blog_name": self.blog_name}

            try:
                # 1. 글쓰기 페이지 진입
                await page.goto(write_url, wait_until="domcontentloaded", timeout=timeout_sec * 1000)
                await asyncio.sleep(1.5)

                # 🛡️ 세션 만료 즉각 감지 및 실시간 SSO 자동 복구
                cur_url = page.url
                if "auth" in cur_url or "login" in cur_url or "accounts.kakao.com" in cur_url:
                    logger.info("🔄 [Tistory-aura] 로그인/인증 페이지 감지 -> 카카오 간편 SSO 실시간 자동 복구 시도...")
                    recovered = await self._auto_recover_sso(page, context, write_url)
                    if not recovered:
                        logger.warning("⚠️ [Tistory] 세션 만료, 백업 쿠키 주입 시도...")
                        best = load_best_cookies("tistory", self.session_file)
                        if best:
                            for c in sanitize_for_playwright(best):
                                try:
                                    await context.add_cookies([c])
                                except Exception:
                                    pass
                            await page.goto(write_url, wait_until="domcontentloaded", timeout=30000)
                            await asyncio.sleep(2)
                            cur_url2 = page.url
                            if "auth" not in cur_url2 and "login" not in cur_url2:
                                logger.info("[RESTORE] 백업 쿠키 주입으로 세션 복원 성공 → 발행 계속")
                            else:
                                return {
                                    "status": "session_expired",
                                    "message": f"티스토리 카카오 세션 만료. [백업도 실패] 루트의 [1회연동]_aura_티스토리_영구로그인.bat 1회 실행 필요",
                                    "blog_name": self.blog_name
                                }
                        else:
                            return {
                                "status": "session_expired",
                                "message": f"티스토리 카카오 세션 만료. 루트의 [1회연동]_aura_티스토리_영구로그인.bat 1회 실행 필요",
                                "blog_name": self.blog_name
                            }

                # 2. 제목 입력기 대기 (유연한 선택자 지원)
                title_el = None
                try:
                    title_el = await page.wait_for_selector("#post-title-inp, textarea[id*='title'], input[name='title']", timeout=15000)
                except Exception:
                    pass

                if not title_el:
                    cur_url = page.url
                    if "auth" in cur_url or "login" in cur_url or "accounts.kakao.com" in cur_url:
                        recovered = await self._auto_recover_sso(page, context, write_url)
                        if recovered:
                            title_el = await page.wait_for_selector("#post-title-inp, textarea[id*='title'], input[name='title']", timeout=15000)
                    if not title_el:
                        raise RuntimeError("티스토리 제목 입력 필드를 찾을 수 없습니다.")

                # 2. 제목 입력
                await title_el.fill(title)

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

                # 관리자 주소가 남아있을 경우 RSS 피드를 통해 실제 공개 글 링크 즉시 획득
                if "manage" in post_url:
                    try:
                        import urllib.request
                        import xml.etree.ElementTree as ET
                        rss_url = f"https://{self.blog_name}.tistory.com/rss"
                        req = urllib.request.Request(rss_url, headers={"User-Agent": "Mozilla/5.0"})
                        with urllib.request.urlopen(req, timeout=5) as resp:
                            root = ET.fromstring(resp.read().decode("utf-8"))
                            items = root.findall("./channel/item")
                            if items and items[0].find("link") is not None:
                                post_url = items[0].find("link").text.strip()
                    except Exception as rss_err:
                        logger.debug(f"RSS 링크 조회 통과: {rss_err}")

                if "manage" in post_url:
                    post_url = f"https://{self.blog_name}.tistory.com/"

                # 🌟 [세션 자동 수명 연장] 살아있는 최신 세션 상태를 디스크 및 .good.json 백업에 즉시 자동 저장
                try:
                    await context.storage_state(path=str(self.session_file))
                    await safe_save("tistory", context, self.session_file, reason="publish_success")
                    logger.info("🔄 [Tistory-aura] 세션 쿠키 수명 자동 연장 및 .good.json 백업 갱신 완료")
                except Exception as save_err:
                    logger.debug(f"세션 연장 통과: {save_err}")

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
                if is_persistent:
                    await context.close()
                else:
                    await context.close()
                    if browser:
                        await browser.close()


if __name__ == "__main__":
    pub = AuraTistoryPublisher()
    print("Is available:", pub.is_available())
