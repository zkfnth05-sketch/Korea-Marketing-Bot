# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 430, "height": 932}, device_scale_factor=2.0)
    page = context.new_page()
    page.goto("https://stockmaster-ai.vercel.app/", wait_until="networkidle")
    page.wait_for_timeout(2000)

    page.evaluate("""() => {
        const style = document.createElement('style');
        style.innerHTML = `
            iframe, [class*="ads"], div[id*="google"] { display: none !important; opacity: 0 !important; }
        `;
        document.head.appendChild(style);
        document.querySelectorAll('iframe, [id*="google"]').forEach(el => el.remove());
    }""")

    inp = page.query_selector('input')
    inp.fill("LG에너지솔루션")
    page.wait_for_timeout(1000)

    item = page.query_selector('text="LG에너지솔루션"') or page.query_selector('div.cursor-pointer')
    item.click()
    page.wait_for_timeout(2000)

    tab_supply = page.query_selector('text="수급 현황"')
    tab_supply.click()
    page.wait_for_timeout(1000)

    # scrollTop 600으로 완전히 밑으로 스크롤
    page.evaluate("""() => {
        const modalContainer = document.querySelector('.fixed.inset-0.overflow-y-auto') || document.querySelector('[class*="fixed"][class*="overflow-y-auto"]');
        if (modalContainer) {
            modalContainer.scrollTop = 580; // 그래프 완전히 치우고 수급 본문만 집중
        }
    }""")
    page.wait_for_timeout(1000)
    page.screenshot(path="brands/stock/assets/test_s4_deeper_600.png")
    print("Saved test_s4_deeper_600.png")
    browser.close()
