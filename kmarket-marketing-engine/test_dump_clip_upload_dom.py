# -*- coding: utf-8 -*-
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def dump_upload_page():
    session_file = Path("brands/aura/naver_session.json")
    video_path = r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Aura\Aura_08_safe_radar_20261011_180012\Aura_22초숏폼_주제08_safe_radar_20261011_180012.mp4"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=str(session_file), viewport={"width": 1400, "height": 1000})
        page = await context.new_page()
        
        await page.goto("https://clipcreators.naver.com/web/upload", wait_until="networkidle", timeout=60000)
        await asyncio.sleep(2.0)
        
        file_input = await page.wait_for_selector("input[type='file']")
        await file_input.set_input_files(video_path)
        await asyncio.sleep(4.0)

        # 업로드 화면 스크린샷 1: 초기 상태
        await page.screenshot(path="outputs/proofs/clip_upload_form_initial.png", full_page=True)
        
        # 버튼들 전수 덤프
        btns = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll("button, div[role='button'], [role='combobox'], select, input")).map(el => ({
                tag: el.tagName,
                type: el.getAttribute('type'),
                role: el.getAttribute('role'),
                className: el.className,
                innerText: (el.innerText || '').trim(),
                ariaLabel: el.getAttribute('aria-label'),
                name: el.getAttribute('name'),
                id: el.id
            }));
        }""")
        
        with open("outputs/proofs/clip_buttons_dump.json", "w", encoding="utf-8") as f:
            import json
            json.dump(btns, f, ensure_ascii=False, indent=2)

        # 카테고리 영역 클릭 시도
        cat_trigger = await page.query_selector("button:has-text('카테고리'), [class*='dropdown'], [class*='category'], [class*='Select']")
        if cat_trigger:
            await cat_trigger.click()
            await asyncio.sleep(2.0)
            await page.screenshot(path="outputs/proofs/clip_upload_form_after_cat_click.png", full_page=True)

        await browser.close()
        print("DONE DUMPING")

asyncio.run(dump_upload_page())
