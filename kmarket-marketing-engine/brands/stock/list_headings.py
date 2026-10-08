# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 430, "height": 932})
    page.goto("https://stockmaster-ai.vercel.app/", wait_until="networkidle")
    page.wait_for_timeout(2000)

    # 모든 h2, h3, h4 태그의 텍스트와 위치 확인
    headings = page.evaluate("""() => {
        const hs = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, [class*="title"], [class*="header"]'));
        return hs.map(h => ({
            tag: h.tagName,
            text: h.innerText.replace(/\\n/g, ' '),
            top: window.scrollY + h.getBoundingClientRect().top
        }));
    }""")
    for h in headings:
        print(f"[{h['tag']}] y={h['top']} : {h['text'][:60]}")
    browser.close()
