# -*- coding: utf-8 -*-
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def test_click_and_dump_menu():
    session_file = Path("brands/aura/naver_session.json")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(storage_state=str(session_file), viewport={"width": 1400, "height": 1000})
        page = await ctx.new_page()

        await page.goto("https://clipcreators.naver.com/web/contents/clips", wait_until="networkidle", timeout=60000)
        await asyncio.sleep(2.0)

        # 1. '카테고리 선택' 클릭
        cat_btn = await page.wait_for_selector("button:has-text('카테고리 선택')")
        await cat_btn.click()
        await asyncio.sleep(1.5)

        # 2. 1차 카테고리 버튼 정확히 클릭
        c1 = page.locator("button.DropdownButton_trigger__75cvp:has-text('1차 카테고리')").first
        await c1.click()
        await asyncio.sleep(1.5)

        # 스크린샷: 드롭다운이 열렸는지 확인
        await page.screenshot(path="outputs/proofs/clip_dropdown_open_check.png")

        # 열린 메뉴 덤프
        menu_items = await page.evaluate("""() => {
            const all = Array.from(document.querySelectorAll("*"));
            return all.filter(el => {
                const t = (el.innerText || '').trim();
                return ['맛집', '일상기록', '라이프스타일', '플레이스', '푸드'].includes(t);
            }).map(el => ({
                tag: el.tagName,
                cls: el.className,
                text: el.innerText.trim(),
                role: el.getAttribute('role'),
                parentTag: el.parentElement ? el.parentElement.tagName : null,
                parentCls: el.parentElement ? el.parentElement.className : null
            }));
        }""")

        with open("outputs/proofs/clip_menu_items_dump.json", "w", encoding="utf-8") as f:
            import json
            json.dump(menu_items, f, ensure_ascii=False, indent=2)

        print("FOUND MATCHING MENU ITEMS:", len(menu_items))
        if menu_items:
            print("FIRST MATCH:", menu_items[0])

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_click_and_dump_menu())
