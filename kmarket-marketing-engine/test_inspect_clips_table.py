# -*- coding: utf-8 -*-
"""
콘텐츠 목록 페이지(contents/clips)에서 카테고리 및 상태를 직접 [공개]로 전환 가능한지 검증
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def inspect_clips_table():
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=True)
    ctx = await browser.new_context(storage_state='brands/aura/naver_session.json', viewport={"width": 1400, "height": 1000})
    page = await ctx.new_page()
    await page.goto('https://clipcreators.naver.com/web/contents/clips', wait_until='networkidle')
    await asyncio.sleep(3)

    # 1. 목록 화면의 첫 번째 행 카테고리 버튼 탐색
    first_row_cat = await page.query_selector("button:has-text('카테고리 선택'), [class*='category'] button")
    print("Found first row cat button:", first_row_cat is not None)

    # 2. 첫 번째 행 상태(초안) 버튼 탐색
    first_row_status = await page.query_selector("button:has-text('초안'), [class*='status'] button")
    print("Found first row status button:", first_row_status is not None)

    # 카테고리 버튼 클릭 시도
    if first_row_cat:
        await first_row_cat.click()
        await asyncio.sleep(1.5)
        await page.screenshot(path="outputs/proofs/clips_table_cat_dropdown.png")
        print("Clicked first row cat, screenshot saved")

        # 옵션 목록 탐색
        opts = await page.evaluate("""() => Array.from(document.querySelectorAll('button, li, div[role="option"]')).map(e => (e.innerText||'').trim())""")
        print("Category options in table:", [o for o in opts if o])

    await browser.close()
    await p.stop()

if __name__ == "__main__":
    asyncio.run(inspect_clips_table())
