# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 430, "height": 932}, device_scale_factor=2.0)
    page = context.new_page()
    page.goto("https://stockmaster-ai.vercel.app/", wait_until="networkidle")
    page.wait_for_timeout(2000)

    # 0. 광고 제거
    page.evaluate("""() => {
        const style = document.createElement('style');
        style.innerHTML = `
            iframe, [class*="ads"], div[id*="google"] { display: none !important; opacity: 0 !important; }
        `;
        document.head.appendChild(style);
        document.querySelectorAll('iframe, [id*="google"]').forEach(el => el.remove());
    }""")

    # 종목 검색 & 모달 오픈
    inp = page.query_selector('input')
    inp.fill("373220")
    page.wait_for_timeout(1000)

    dropdown_item = page.locator('text="LG에너지솔루션"').first
    dropdown_item.click()
    page.wait_for_timeout(2000)

    # 1. 기술 지표 탭 클릭 & 4번 주제 방식 스크롤(390px)
    tab_tech = page.query_selector('text="기술 지표"')
    tab_tech.click()
    page.wait_for_timeout(800)

    page.evaluate("""() => {
        const modal = document.querySelector('.fixed.inset-0.overflow-y-auto') || document.querySelector('.fixed.inset-0');
        if (modal) {
            modal.scrollTop = 390;
        }
    }""")
    page.wait_for_timeout(800)
    page.screenshot(path="brands/stock/assets/test_s3_fixed.png")
    print("Saved test_s3_fixed.png")

    # 2. 수급 현황 탭 클릭 & 4번 주제 방식 스크롤(320px)
    tab_supply = page.query_selector('text="수급 현황"')
    tab_supply.click()
    page.wait_for_timeout(800)

    page.evaluate("""() => {
        const modal = document.querySelector('.fixed.inset-0.overflow-y-auto') || document.querySelector('.fixed.inset-0');
        if (modal) {
            modal.scrollTop = 320;
        }
    }""")
    page.wait_for_timeout(800)
    page.screenshot(path="brands/stock/assets/test_s4_fixed.png")
    print("Saved test_s4_fixed.png")

    browser.close()
