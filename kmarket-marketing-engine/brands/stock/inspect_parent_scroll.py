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

    # 3대 주체별 수급 현황 엘리먼트의 정확한 상위 조상 체인과 스크롤 가능 컨테이너 확인
    info = page.evaluate("""() => {
        const target = Array.from(document.querySelectorAll('*')).find(el => 
            el.textContent && el.textContent.includes('3대 주체별 수급 현황') && el.children.length === 0
        );
        let curr = target;
        const parents = [];
        while (curr && curr !== document.body) {
            parents.push({
                tag: curr.tagName,
                className: curr.className,
                scrollHeight: curr.scrollHeight,
                clientHeight: curr.clientHeight,
                scrollTop: curr.scrollTop,
                overflowY: window.getComputedStyle(curr).overflowY
            });
            curr = curr.parentElement;
        }
        return { parents, windowScrollY: window.scrollY };
    }""")
    print("Ancestors of target:", info)
    browser.close()
