# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    iphone = p.devices['iPhone 14 Pro']
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(**iphone)
    page = context.new_page()
    page.goto('https://stockmaster-ai.vercel.app/', wait_until='domcontentloaded')
    page.wait_for_timeout(2000)

    # 1. 광고 제거
    page.evaluate("""() => {
        const style = document.createElement('style');
        style.innerHTML = `
            iframe, [class*="ads"], div[id*="google"] { display: none !important; opacity: 0 !important; }
        `;
        document.head.appendChild(style);
        document.querySelectorAll('iframe, [id*="google"]').forEach(el => el.remove());
    }""")

    # 2. 전광판 위치로 스크롤
    page.evaluate("() => window.scrollTo(0, 4090)")
    page.wait_for_timeout(500)

    # 3. Playwright locator로 005930 요소를 찾아서 클릭!
    target_locator = page.locator('text=005930').first
    if target_locator.count() > 0:
        target_locator.click()
        print("Playwright target_locator clicked!")
    else:
        page.get_by_text("삼성전자").nth(1).click()
        print("Fallback click!")

    page.wait_for_timeout(1000)

    # 4. 카드가 화면 최상단(y=0)에 딱 맞닿도록 스크롤
    page.evaluate("""() => {
        const all = Array.from(document.querySelectorAll('*'));
        const el = all.find(e => e.children.length === 0 && e.textContent.trim() === '005930');
        if (el) {
            let card = el.closest('[class*="border"]') || el.parentElement.parentElement;
            if (card) {
                const rect = card.getBoundingClientRect();
                window.scrollBy(0, rect.top - 8);
            }
        }
    }""")
    page.wait_for_timeout(500)

    page.screenshot(path='brands/stock/assets/test_s2_locator_click.png')
    print("Saved test_s2_locator_click.png")
    browser.close()
