# -*- coding: utf-8 -*-
"""
키보드 네비게이션(ArrowDown + Enter)으로 리액트 상태를 100% 트리거하여 [저장] 활성화 검증
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def test_keyboard_select():
    session_file = Path("brands/aura/naver_session.json")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(storage_state=str(session_file), viewport={"width": 1400, "height": 1000})
        page = await ctx.new_page()

        print("1. 네이버 클립 clips 접속...")
        await page.goto("https://clipcreators.naver.com/web/contents/clips", wait_until="networkidle", timeout=60000)
        await asyncio.sleep(3.0)

        cat_btn = await page.query_selector("button:has-text('카테고리 선택')")
        if not cat_btn:
            print("카테고리 선택 버튼 없음")
            await browser.close()
            return

        print("2. 카테고리 선택 클릭...")
        await cat_btn.click()
        await asyncio.sleep(2.0)

        # 모달 내부 1차 카테고리 버튼 클릭
        dialog = page.locator("[role='dialog']")
        c1 = dialog.locator("button:has-text('1차 카테고리')").first
        await c1.click()
        await asyncio.sleep(1.0)

        # 🌟 키보드로 아래 화살표 누르고 엔터! (리액트 100% 정석 이벤트)
        print("3. 키보드 ArrowDown + Enter 전송...")
        await page.keyboard.press("ArrowDown")
        await asyncio.sleep(0.5)
        await page.keyboard.press("Enter")
        await asyncio.sleep(1.5)

        # 스크린샷 1: 선택 직후 모달 상태
        await page.screenshot(path="outputs/proofs/clip_modal_after_keyboard.png")

        # 저장 버튼 상태 확인
        save_btn = dialog.locator("button:has-text('저장')").first
        is_dis = await save_btn.is_disabled()
        print(f"4. [저장] 버튼 disabled 여부: {is_dis}")

        if not is_dis:
            print("🎉 [저장] 버튼 활성화 성공! 클릭 진행...")
            await save_btn.click()
            await asyncio.sleep(2.0)
            await page.screenshot(path="outputs/proofs/clip_after_save_success.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_keyboard_select())
