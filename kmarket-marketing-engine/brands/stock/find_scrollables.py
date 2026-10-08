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

    # 모든 자식 요소들 중 스크롤 가능한 요소 찾기
    scroll_res = page.evaluate("""() => {
        const divs = Array.from(document.querySelectorAll('div, section, main'));
        const results = [];
        divs.forEach((d, i) => {
            if (d.scrollHeight > d.clientHeight) {
                results.push({
                    index: i,
                    tagName: d.tagName,
                    className: d.className,
                    scrollHeight: d.scrollHeight,
                    clientHeight: d.clientHeight,
                    scrollTop: d.scrollTop
                });
            }
        });
        return results;
    }""")
    print("Scrollable candidates:", scroll_res)
    browser.close()
