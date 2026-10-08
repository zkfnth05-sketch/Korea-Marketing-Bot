# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 430, "height": 932})
    page.goto("https://stockmaster-ai.vercel.app/", wait_until="networkidle")
    page.wait_for_timeout(2000)

    # 10분 계량 전광판 텍스트 찾기
    info = page.evaluate("""() => {
        const els = Array.from(document.querySelectorAll('*')).filter(el => 
            el.textContent && el.textContent.includes('10분 계량 전광판') && el.children.length === 0
        );
        return els.map(el => {
            const rect = el.getBoundingClientRect();
            return {
                text: el.textContent,
                top: rect.top,
                y: window.scrollY + rect.top
            };
        });
    }""")
    print("Quant board title positions:", info)
    browser.close()
