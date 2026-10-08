# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 430, "height": 932}, device_scale_factor=2.0)
    page = context.new_page()
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

    # 팝업 내부의 스크롤 컨테이너 정보 및 자식 요소들의 높이 측정
    info = page.evaluate("""() => {
        const modal = document.querySelector('.fixed.inset-0');
        const scrollables = Array.from(document.querySelectorAll('div')).filter(d => d.scrollHeight > d.clientHeight);
        return scrollables.map(s => ({
            className: s.className,
            scrollHeight: s.scrollHeight,
            clientHeight: s.clientHeight,
            maxScrollTop: s.scrollHeight - s.clientHeight
        }));
    }""")
    print("Scrollables in Supply tab:", info)
    browser.close()
