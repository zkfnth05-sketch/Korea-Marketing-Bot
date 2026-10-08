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

    inp = page.query_selector('input')
    inp.fill("LG에너지솔루션")
    page.wait_for_timeout(1000)

    item = page.query_selector('text="LG에너지솔루션"') or page.query_selector('div.cursor-pointer')
    item.click()
    page.wait_for_timeout(2000)

    # 1. 수급 현황 탭 클릭
    tab_supply = page.query_selector('text="수급 현황"')
    tab_supply.click()
    page.wait_for_timeout(1000)

    # 모달 배경 컨테이너(index 567 또는 .fixed.inset-0.overflow-y-auto)의 scrollTop을 350px 내리기
    page.evaluate("""() => {
        const modalContainer = document.querySelector('.fixed.inset-0.overflow-y-auto') || document.querySelector('[class*="fixed"][class*="overflow-y-auto"]');
        if (modalContainer) {
            modalContainer.scrollTop = 320; // 3대 주체 수급 현황과 당일 거래대금이 완벽히 보이도록 스크롤
        }
    }""")
    page.wait_for_timeout(1000)
    page.screenshot(path="brands/stock/assets/test_s4_exact_bottom.png")
    print("Saved test_s4_exact_bottom.png")
    browser.close()
