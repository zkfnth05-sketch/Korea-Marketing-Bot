# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 430, "height": 932})
    page.goto("https://stockmaster-ai.vercel.app/", wait_until="networkidle")
    page.wait_for_timeout(2000)

    inp = page.query_selector('input')
    inp.fill("LG에너지솔루션")
    page.wait_for_timeout(1000)

    item = page.query_selector('text="LG에너지솔루션"') or page.query_selector('div.cursor-pointer')
    item.click()
    page.wait_for_timeout(2000)

    tab_supply = page.query_selector('text="수급 현황"')
    tab_supply.click()
    page.wait_for_timeout(1000)

    # 모달 박스 내부의 모든 직계 및 2단계 자식 엘리먼트 덤프
    html = page.evaluate("""() => {
        const modal = document.querySelector('.bg-white.rounded-xl') || document.querySelector('.fixed.inset-0 > div');
        if (!modal) return "No modal";
        return modal.innerHTML;
    }""")
    with open("modal_dump.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Dumped modal_dump.html (length:", len(html), ")")
    browser.close()
