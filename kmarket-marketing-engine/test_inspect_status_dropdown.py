# -*- coding: utf-8 -*-
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def inspect_status_dropdown():
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=True)
    ctx = await browser.new_context(storage_state='brands/aura/naver_session.json', viewport={'width': 1400, 'height': 1000})
    page = await ctx.new_page()
    await page.goto('https://clipcreators.naver.com/web/contents/clips', wait_until='networkidle')
    await asyncio.sleep(2)

    # 카테고리가 '플레이스'로 선택된 행의 '초안' 버튼 클릭
    row = page.locator("tr", has_text="플레이스").first
    status_btn = row.locator("button:has-text('초안')").first
    await status_btn.click()
    await asyncio.sleep(1.5)
    await page.screenshot(path='outputs/proofs/clip_status_dropdown_opened.png')

    opts = await page.evaluate("""() => Array.from(document.querySelectorAll('button, li, div[role="option"]')).map(e => ({
        tag: e.tagName, cls: e.className, text: (e.innerText||'').trim()
    }))""")

    import json
    with open('outputs/proofs/clip_status_opts.json', 'w', encoding='utf-8') as f:
        json.dump(opts, f, ensure_ascii=False, indent=2)

    print("DUMPED STATUS OPTIONS:", len(opts))
    await browser.close()
    await p.stop()

if __name__ == "__main__":
    asyncio.run(inspect_status_dropdown())
