# -*- coding: utf-8 -*-
"""
🛡️ InsureBalance Brunch Publisher (보험 전용 브런치스토리 무인 자동 발행 레고 블록)
================================================================================
- 크롬 영구 프로필 디렉터리(brunch_chrome_profile) 및 세션(brunch_session.json)을 활용한 100% 무인 자동 발행
- 1. 로컬 안전 백업 보관 (outputs/insurance/brunch/brunch_draft_topic_xxx.json)
- 2. 카카오 브런치스토리 에디터(/write) 진입 및 세션 만료 조기 감지
- 3. 제목 + 본문 자동 입력 후 작가의 서랍 / 온라인 발행
"""

import sys
import json
import logging
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
PROFILE_DIR = CURRENT_DIR / "brunch_chrome_profile"
FALLBACK_PROFILE = CURRENT_DIR.parent / "aura" / "brunch_chrome_profile"

SESSION_FILE = CURRENT_DIR / "brunch_session.json"
FALLBACK_SESSION = CURRENT_DIR.parent / "aura" / "brunch_session.json"
BRUNCH_OUT_DIR = PROJECT_ROOT / "outputs" / "insurance" / "brunch"

logger = logging.getLogger("InsuranceBrunchPublisher")


class InsuranceBrunchPublisher:
    """InsureBalance 보험 전용 브런치스토리 자동 발행 엔진 (영구 크롬 프로필/세션 지원)"""

    def __init__(self):
        if PROFILE_DIR.exists() and any(PROFILE_DIR.iterdir()):
            self.profile_dir = PROFILE_DIR
        elif FALLBACK_PROFILE.exists() and any(FALLBACK_PROFILE.iterdir()):
            self.profile_dir = FALLBACK_PROFILE
        else:
            self.profile_dir = PROFILE_DIR

        if SESSION_FILE.exists() and SESSION_FILE.stat().st_size > 100:
            self.session_file = SESSION_FILE
        else:
            self.session_file = FALLBACK_SESSION

        BRUNCH_OUT_DIR.mkdir(parents=True, exist_ok=True)

    def is_available(self) -> bool:
        has_profile = self.profile_dir.exists() and any(self.profile_dir.iterdir())
        has_session = self.session_file.exists() and self.session_file.stat().st_size > 100
        return has_profile or has_session

    def publish_story(
        self,
        title: str,
        content_text: str,
        tag_list: Optional[List[str]] = None,
        topic_id: int = 1,
        landing_url: str = "https://insurebalance.co.kr",
        timeout_sec: int = 40
    ) -> Dict[str, Any]:
        """동기 호출 인터페이스"""
        try:
            return asyncio.run(self.publish_story_async(title, content_text, tag_list, topic_id, landing_url, timeout_sec))
        except Exception as e:
            logger.error(f"❌ [Brunch-Insurance] 발행 예외: {e}")
            return {"status": "error", "message": str(e)}

    publish = publish_story

    def publish_column(
        self,
        title: str,
        subtitle: str = "",
        body_text: str = "",
        topic_id: int = 1,
        landing_url: str = "https://insurebalance.co.kr",
        tag_list: Optional[List[str]] = None,
        timeout_sec: int = 40
    ) -> Dict[str, Any]:
        """기존 칼럼 인터페이스 호환용"""
        return self.publish_story(
            title=title,
            content_text=body_text,
            tag_list=tag_list,
            topic_id=topic_id,
            landing_url=landing_url,
            timeout_sec=timeout_sec
        )

    async def publish_story_async(
        self,
        title: str,
        content_text: str,
        tag_list: Optional[List[str]] = None,
        topic_id: int = 1,
        landing_url: str = "https://insurebalance.co.kr",
        timeout_sec: int = 40
    ) -> Dict[str, Any]:
        """Playwright 브런치 에디터 자동 발행 / 저장 (영구 크롬 프로필/세션 탑재)"""
        # 1. 로컬 안전 백업 (작가의 서랍 파일)
        file_name = f"brunch_draft_topic_{topic_id:03d}.json"
        draft_pkg = {
            "title": title,
            "body": content_text,
            "landing_url": landing_url,
            "topic_id": topic_id
        }
        save_path = BRUNCH_OUT_DIR / file_name
        try:
            with open(save_path, "w", encoding="utf-8") as fp:
                json.dump(draft_pkg, fp, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"⚠️ [Brunch-Insurance] 로컬 보관 예외: {e}")

        if not self.is_available():
            logger.warning("⚠️ [Brunch-Insurance] 브런치 영구 프로필 또는 세션 파일이 없습니다. 로컬 보관 모드로 유지됩니다.")
            return {
                "status": "archived_locally",
                "message": "브런치 세션 부재 - 로컬 원고 보관 완료 ([1회연동] bat 실행 필요)",
                "archive_file": str(save_path.name)
            }

        async with async_playwright() as p:
            is_persistent = self.profile_dir.exists() and any(self.profile_dir.iterdir())
            has_session_file = self.session_file.exists() and self.session_file.stat().st_size > 100
            browser = None
            context = None

            if has_session_file:
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
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(self.profile_dir),
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"],
                    viewport={"width": 1280, "height": 900},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
                )
                page = context.pages[0] if context.pages else await context.new_page()

            try:
                write_url = "https://brunch.co.kr/write"
                logger.info(f"🌐 [Brunch-Insurance] 에디터 진입: {write_url}")
                await page.goto(write_url, wait_until="networkidle", timeout=timeout_sec * 1000)
                await asyncio.sleep(2)

                cur_url = page.url
                if "signin" in cur_url or "accounts.kakao.com" in cur_url:
                    logger.info("🔄 [Brunch-Insurance] 브런치 세션 재인증 시도 (/auth/kakao SSO 자동 연동)...")
                    await page.goto("https://brunch.co.kr/auth/kakao?url=%2Fwrite", wait_until="networkidle", timeout=15000)
                    await asyncio.sleep(2)
                    cur_url = page.url
                    if "signin" in cur_url or "accounts.kakao.com" in cur_url:
                        logger.warning("⚠️ [Brunch-Insurance] 브런치 세션 만료 감지 (1회 연동 필요)")
                        return {"status": "error", "message": "로그인 만료 ([1회연동]_보험비교_브런치_영구로그인.bat 실행 필요)"}
                    else:
                        await context.storage_state(path=str(self.session_file))
                        logger.info("🎉 [Brunch-Insurance] 카카오 SSO 자동 재인증 및 영구 세션 갱신 완료!")

                # 제목 입력
                title_el = page.locator(".wrap_cover textarea, #cover-title-inp, [placeholder*='제목을 입력']").first
                if await title_el.count() > 0:
                    await title_el.fill(title)
                else:
                    await page.keyboard.type(title)
                await asyncio.sleep(1)

                # 본문 입력 (클립보드 방식)
                try:
                    process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, close_fds=True)
                    process.communicate(input=content_text.encode('utf-16le'))
                    await page.keyboard.press("Tab")
                    await page.keyboard.press("Control+v")
                except Exception:
                    await page.keyboard.press("Tab")
                    await page.keyboard.type(content_text[:300])

                await asyncio.sleep(1)

                # 저장 또는 발행 버튼 클릭
                save_btn = page.locator("button:has-text('발행'), button:has-text('저장')").first
                if await save_btn.count() > 0:
                    await save_btn.click()
                    await asyncio.sleep(2)

                return {
                    "status": "success",
                    "platform": "brunch",
                    "title": title,
                    "post_url": "https://brunch.co.kr",
                    "archive_file": str(save_path.name)
                }
            except Exception as e:
                logger.error(f"❌ [Brunch-Insurance] 자동 발행 예외: {e}")
                return {"status": "error", "message": str(e), "archive_file": str(save_path.name)}
            finally:
                if is_persistent:
                    await context.close()
                else:
                    if browser:
                        await browser.close()


if __name__ == "__main__":
    pub = InsuranceBrunchPublisher()
    print("Is available:", pub.is_available())
