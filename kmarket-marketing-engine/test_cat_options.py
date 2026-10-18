# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright

async def test_cat():
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=True)
    ctx = await browser.new_context(storage_state='brands/aura/naver_session.json')
    page = await ctx.new_page()
    await page.goto('https://clipcreators.naver.com/web/upload', wait_until='networkidle')
    inp = await page.wait_for_selector("input[type='file']")
    await inp.set_input_files(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Aura\Aura_08_safe_radar_20261011_180012\Aura_22초숏폼_주제08_safe_radar_20261011_180012.mp4")
    await asyncio.sleep(4)
    btn = await page.wait_for_selector(".ClipDetailForm_dropdownPrimary__6ZbSU")
    await btn.click()
    await asyncio.sleep(2)
    opts = await page.evaluate("""() => Array.from(document.querySelectorAll('button, li, div[role="option"], ul')).map(e => ({
        tag: e.tagName, text: (e.innerText||'').trim(), cls: e.className
    }))""")
    print("Found options count:", len(opts))
    for o in opts:
        if o['text'] and any(k in o['text'] for k in ['일상', '라이프', '플레이스', '맛집', '엔터', '패션', '스포츠']):
            print("MATCHED OPTION:", o)
    await browser.close()
    await p.stop()

if __name__ == "__main__":
    asyncio.run(test_cat())
