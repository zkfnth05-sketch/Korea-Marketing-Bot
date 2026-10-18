# -*- coding: utf-8 -*-
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def dump_modal_html():
    session_file = Path("brands/aura/naver_session.json")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(storage_state=str(session_file), viewport={"width": 1400, "height": 1000})
        page = await ctx.new_page()

        await page.goto("https://clipcreators.naver.com/web/contents/clips", wait_until="networkidle", timeout=60000)
        await asyncio.sleep(3.0)

        cat_btn = await page.wait_for_selector("button:has-text('카테고리 선택')")
        await cat_btn.click()
        await asyncio.sleep(2.0)

        dialog_html = await page.evaluate("""() => {
            const d = document.querySelector("[role='dialog']");
            return d ? d.outerHTML : "NO DIALOG";
        }""")

        with open("outputs/proofs/modal_html_dump.html", "w", encoding="utf-8") as f:
            f.write(dialog_html)

        print("DUMPED MODAL HTML LENGTH:", len(dialog_html))
        await browser.close()

if __name__ == "__main__":
    asyncio.run(dump_modal_html())
