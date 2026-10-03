# -*- coding: utf-8 -*-
"""
Aura Meta Business Suite (MBS) Reels Publisher (💖 Aura 전용 메타 비즈니스 웹 릴스 발행 레고 블록)
======================================================================================
- 역할: Meta Graph API 대신 Meta Business Suite 웹(business.facebook.com)을 직접 제어하여
        서드파티 API 페널티를 원천 회피하고 인스타그램 + 페이스북 릴스를 100% 무인 동시 발행
- 지원: 15.5초 슬라이드쇼 릴스 및 22초 오리지널 숏폼 비디오 무인 자동 업로드 & 게시
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
PROFILE_DIR = CURRENT_DIR / "meta_chrome_profile"
ACCOUNTS_FILE = CURRENT_DIR / "accounts.json"

logger = logging.getLogger("AuraMBSReelsPublisher")


class AuraMBSReelsPublisher:
    """Aura 데이팅 전용 Meta Business Suite 웹 릴스 발행 엔진"""

    def __init__(self, page_id: str = "1356851504174047"):
        self.page_id = page_id
        self.profile_dir = PROFILE_DIR
        self.composer_url = f"https://business.facebook.com/latest/reels_composer?asset_id={self.page_id}"

    def is_available(self) -> bool:
        return self.profile_dir.exists() and any(self.profile_dir.iterdir())

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
            logger.error(f"❌ [Aura MBS Reel] 발행 예외: {e}")
            return {"status": "error", "message": str(e)}

    async def publish_reel_async(
        self,
        video_path: str,
        caption: str,
        timeout_sec: int = 60
    ) -> Dict[str, Any]:
        """비동기 Meta Business Suite 웹 자동 릴스 발행"""
        if not os.path.exists(video_path):
            return {"status": "error", "message": f"비디오 파일 없음: {video_path}"}

        logger.info(f"🚀 [Aura MBS Reel] 발행 시작: {video_path}")

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-first-run",
                    "--no-default-browser-check"
                ],
                viewport={"width": 1366, "height": 900}
            )
            page = context.pages[0] if context.pages else await context.new_page()

            try:
                # 1. 릴스 작성기 진입
                logger.info(f"🌐 [MBS] Aura 릴스 작성기 접속 중: {self.composer_url}")
                await page.goto(self.composer_url, wait_until="networkidle", timeout=35000)
                await asyncio.sleep(4)

                # 2. 비디오 파일 첨부
                btn = page.locator("div[role='button']").filter(has_text="동영상 추가").first
                if await btn.count() == 0:
                    raise RuntimeError("MBS Reels Composer에서 [동영상 추가] 버튼을 찾을 수 없습니다.")

                async with page.expect_file_chooser(timeout=10000) as fc_info:
                    await btn.click()
                fc = await fc_info.value
                await fc.set_files(video_path)
                logger.info("📁 비디오 파일 첨부 완료, 업로드 렌더링 대기...")

                # 100% 업로드 대기
                await asyncio.sleep(14)

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
                    await page.screenshot(path=str(CURRENT_DIR / "aura_mbs_published.png"))

                    logger.info("🎉 [Aura MBS Reel] 페이스북(Aura) + 인스타그램(@aura_ai_dating) 동시 발행 완료!")
                    return {
                        "status": "success",
                        "message": "Meta Business Suite를 통한 Aura 릴스 동시 발행 성공",
                        "platform": "meta_business_suite",
                        "video": os.path.basename(video_path)
                    }
                else:
                    raise RuntimeError("[공유하기] 최종 버튼을 찾을 수 없습니다.")

            except Exception as ex:
                logger.error(f"❌ [Aura MBS Reel 발행 실패] {ex}")
                return {"status": "error", "message": str(ex)}
            finally:
                await context.close()
