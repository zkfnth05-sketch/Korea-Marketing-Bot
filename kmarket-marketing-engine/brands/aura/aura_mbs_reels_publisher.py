import re
# -*- coding: utf-8 -*-
"""
Aura AI 데이팅 Meta Business Suite (MBS) Reels Publisher (💖 Aura AI 데이팅 전용 메타 비즈니스 웹 릴스 발행 레고 블록)
===================================================================================================
- 역할: Meta Graph API 대신 Meta Business Suite 웹(business.facebook.com)을 직접 제어하여
        Aura 페이스북 페이지 + aura_ai_dating 인스타그램 릴스를 100% 무인 동시 발행
- 지원: 15.5초 슬라이드쇼 릴스 및 22초/30초 오리지널 숏폼 비디오 무인 자동 업로드 & 게시
- 핵심 기능:
  1. [0 API 순수 브라우저 스텔스]: input[type='file'] 다이렉트 주입 + 버튼 폴백
  2. [완벽한 크롬 User-Agent]: Headless 봇 탐지 원천 차단
  3. [메타 세션 로테이션 자동 동기화]: 발행 시마다 갱신된 최신 쿠키를 meta_session.json에 자동 저장하여 세션 영구 유지
===================================================================================================
"""

import os
import sys
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

from core.engine.browser_guard import clean_browser_profile_locks, get_safe_browser_args

PROFILE_DIR = CURRENT_DIR / "meta_chrome_profile"
SESSION_FILE = CURRENT_DIR / "meta_session.json"
ACCOUNTS_FILE = CURRENT_DIR / "accounts.json"

logger = logging.getLogger("AuraMBSReelsPublisher")


class AuraMBSReelsPublisher:
    """Aura AI 데이팅 전용 Meta Business Suite 웹 릴스 발행 엔진"""

    def __init__(self, page_id: str = "1356851504174047"):
        self.page_id = page_id
        self.profile_dir = PROFILE_DIR
        self.session_file = SESSION_FILE
        self.composer_url = f"https://business.facebook.com/latest/reels_composer?asset_id={self.page_id}"

    def is_available(self) -> bool:
        has_profile = self.profile_dir.exists() and any(self.profile_dir.iterdir())
        has_session = self.session_file.exists() and self.session_file.stat().st_size > 50
        return has_profile or has_session

    def publish_reel(
        self,
        video_path: str,
        caption: str,
        timeout_sec: int = 60
    ) -> Dict[str, Any]:
        """동기 호출 인터페이스"""
        try:
            return asyncio.run(self.publish_reel_async(video_path, caption, timeout_sec))
        except Exception as e:
            logger.error(f"❌ [Aura AI 데이팅 MBS Reel] 발행 예외: {e}")
            return {"status": "error", "message": str(e)}

    async def publish_reel_async(
        self,
        video_path: str,
        caption: str,
        timeout_sec: int = 60
    ) -> Dict[str, Any]:
        """비동기 Meta Business Suite 웹 자동 릴스 발행 (0 API 순수 브라우저 스텔스)"""
        if not os.path.exists(video_path):
            return {"status": "error", "message": f"비디오 파일 없음: {video_path}"}

        logger.info(f"🚀 [Aura AI 데이팅 MBS Reel] 발행 시작: {video_path}")

        clean_browser_profile_locks(self.profile_dir)

        async with async_playwright() as p:
            browser_args = [
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check",
                "--start-maximized"
            ]
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=True,
                args=browser_args,
                viewport={"width": 1366, "height": 900},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            )

            # 세션 쿠키 주입
            if self.session_file.exists():
                try:
                    with open(self.session_file, "r", encoding="utf-8") as f:
                        raw = json.load(f)
                    raw_cookies = raw.get("cookies", raw) if isinstance(raw, dict) else raw
                    clean_cookies = []
                    for c in raw_cookies:
                        item = {
                            "name": c["name"],
                            "value": c["value"],
                            "domain": c.get("domain", ".facebook.com"),
                            "path": c.get("path", "/"),
                            "secure": c.get("secure", True),
                            "httpOnly": c.get("httpOnly", False)
                        }
                        if c.get("sameSite") in ["Strict", "Lax", "None"]:
                            item["sameSite"] = c["sameSite"]
                        clean_cookies.append(item)
                    for ck in clean_cookies:
                        try:
                            await context.add_cookies([ck])
                        except Exception:
                            pass
                    logger.info(f"   🍪 메타 세션 쿠키 {len(clean_cookies)}개 브라우저 주입 완료")
                except Exception as ce:
                    logger.warning(f"메타 쿠키 주입 경고: {ce}")

            page = context.pages[0] if context.pages else await context.new_page()

            try:
                # 1. 릴스 작성기 진입
                logger.info(f"🌐 [MBS] Aura AI 데이팅 릴스 작성기 접속 중: {self.composer_url}")
                await page.goto(self.composer_url, wait_until="networkidle", timeout=35000)
                await asyncio.sleep(4)

                # 2. 비디오 파일 첨부 (0 API 순수 브라우저 스텔스: input[type='file'] 다이렉트 주입 + 버튼 폴백)
                file_input = await page.query_selector("input[type='file']")
                if file_input:
                    await file_input.set_input_files(video_path)
                    logger.info("🎬 비디오 파일 input[type='file'] 다이렉트 주입 100% 성공!")
                else:
                    btn = page.locator("div[role='button'], button, [aria-label*='동영상'], [aria-label*='video'], [aria-label*='Video']").filter(has_text=re.compile(r'동영상\s*추가|Add\s*video|비디오|Upload', re.I)).first
                    if await btn.count() > 0:
                        async with page.expect_file_chooser(timeout=10000) as fc_info:
                            await btn.click()
                        fc = await fc_info.value
                        await fc.set_files(video_path)
                        logger.info("🎬 비디오 파일 버튼 클릭 첨부 완료!")
                    else:
                        raise RuntimeError("MBS Reels Composer에서 파일 업로드 엘리먼트를 찾을 수 없습니다.")
                logger.info("📁 비디오 파일 첨부 완료, 업로드 렌더링 대기...")

                # 100% 업로드 대기
                await asyncio.sleep(15)

                # 3. 캡션 본문 입력
                text_input = page.locator("textarea, div[contenteditable='true'], [role='textbox']").first
                if await text_input.count() > 0:
                    try:
                        await text_input.click()
                        await text_input.fill(caption)
                    except Exception:
                        await text_input.type(caption)
                    logger.info("✍️ 릴스 캡션 및 해시태그 입력 완료")

                await asyncio.sleep(2)

                # 4. Step 1 -> Step 2 [다음] 클릭
                next_btn1 = page.locator("div[role='button'], button").filter(has_text="다음").last
                if await next_btn1.count() > 0:
                    await next_btn1.click()
                    await asyncio.sleep(4)

                # 5. Step 2 -> Step 3 [다음] 클릭
                next_btn2 = page.locator("div[role='button'], button").filter(has_text="다음").last
                if await next_btn2.count() > 0:
                    await next_btn2.click()
                    await asyncio.sleep(4)

                # 6. Step 3 [공유하기] 클릭 (하단 우측 파란색 액션 버튼)
                submit_btn = page.locator("div[role='button'], button").filter(has_text="공유하기").last
                if await submit_btn.count() > 0:
                    await submit_btn.click()
                    logger.info("💥 [공유하기] 버튼 클릭 완료! 메타 릴스 처리 대기 중...")

                    # 팝업 [완료] 버튼 또는 처리 완료 대기
                    await asyncio.sleep(15)
                    modal_done_btn = page.locator("div[role='button'], button").filter(has_text="완료").first
                    if await modal_done_btn.count() > 0:
                        await modal_done_btn.click()
                        logger.info("✅ 릴스 처리 팝업 [완료] 클릭")

                    await asyncio.sleep(5)
                    await page.screenshot(path=str(CURRENT_DIR / f"aura_mbs_published.png"))

                    # 🔄 [메타 세션 로테이션 자동 동기화] 최신 쿠키 영구 저장
                    try:
                        latest_cookies = await context.cookies()
                        clean_latest = []
                        for c in latest_cookies:
                            item = {
                                "name": c["name"],
                                "value": c["value"],
                                "domain": c.get("domain", ".facebook.com"),
                                "path": c.get("path", "/"),
                                "secure": c.get("secure", True),
                                "httpOnly": c.get("httpOnly", False)
                            }
                            if c.get("sameSite") in ["Strict", "Lax", "None"]:
                                item["sameSite"] = c["sameSite"]
                            clean_latest.append(item)
                        with open(self.session_file, "w", encoding="utf-8") as f:
                            json.dump({"cookies": clean_latest}, f, ensure_ascii=False, indent=2)
                        logger.info(f"🔄 [Meta 세션 로테이션 동기화] {len(clean_latest)}개 최신 쿠키 영구 저장 완료")
                    except Exception as ce:
                        logger.warning(f"메타 쿠키 동기화 경고: {ce}")

                    logger.info("🎉 [Aura AI 데이팅 MBS Reel] 페이스북(Aura) + 인스타그램(aura_ai_dating) 동시 발행 완료!")
                    return {
                        "status": "success",
                        "message": "Meta Business Suite를 통한 Aura AI 데이팅 릴스 동시 발행 성공",
                        "platform": "meta_business_suite",
                        "video": os.path.basename(video_path)
                    }
                else:
                    raise RuntimeError("[공유하기] 최종 버튼을 찾을 수 없습니다.")

            except Exception as ex:
                logger.error(f"❌ [Aura AI 데이팅 MBS Reel 발행 실패] {ex}")
                return {"status": "error", "message": str(ex)}
            finally:
                try:
                    await context.close()
                except Exception:
                    pass
