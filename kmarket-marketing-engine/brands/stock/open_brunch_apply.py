# -*- coding: utf-8 -*-
"""
📈 Open Brunch Creator Application Page
=========================================
저장된 브런치 프로필/세션으로 실제 브라우저를 열어 카카오 브런치 작가 신청 페이지로 바로 진입합니다.
"""

import sys
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

CURRENT_DIR = Path(__file__).resolve().parent
PROFILE_DIR = CURRENT_DIR / "brunch_chrome_profile"
SESSION_FILE = CURRENT_DIR / "brunch_session.json"


async def open_apply_page():
    print("=" * 60)
    print("🚀 [카카오 브런치 작가 신청 페이지를 화면에 엽니다]")
    print("저장된 세션으로 로그인 상태가 유지된 채 브런치 작가 신청 페이지로 이동합니다.")
    print("=" * 60)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ],
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.pages[0] if context.pages else await context.new_page()

        # 브런치 작가 신청 페이지 이동
        await page.goto("https://brunch.co.kr/creator/create")
        print("\n✅ 브런치 작가 신청 페이지가 열렸습니다!")
        print("준비해 드린 합격 답변(작가소개, 활동계획, 글샘플)을 복사해서 붙여넣으신 후 [신청하기]를 눌러주세요.")
        print("창을 닫으실 때까지 브라우저는 계속 유지됩니다.")

        # 사용자가 창을 닫을 때까지 대기
        try:
            while len(context.pages) > 0:
                await asyncio.sleep(2)
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(open_apply_page())
