# -*- coding: utf-8 -*-
import sys
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 430, "height": 932})
    page.goto("https://stockmaster-ai.vercel.app/", wait_until="networkidle")
    page.wait_for_timeout(2000)

    # 1위 종목(LG에너지솔루션) 전광판 카드 찾기
    info = page.evaluate("""() => {
        const allCards = Array.from(document.querySelectorAll('*')).filter(el => {
            return el.innerText && el.innerText.includes('계량 종합') && (el.innerText.includes('LG에너지솔루션') || el.innerText.includes('373220') || el.innerText.includes('1위') || el.innerText.includes('1'));
        });
        return allCards.map(c => ({
            tag: c.tagName,
            className: c.className,
            textSnippet: c.innerText.replace(/\\n/g, ' ').substring(0, 80),
            top: window.scrollY + c.getBoundingClientRect().top
        }));
    }""")
    for item in info:
        print(f"y={item['top']} : {item['textSnippet']}")
    browser.close()
