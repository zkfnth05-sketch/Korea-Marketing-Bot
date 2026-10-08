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

    # [수급 현황] 탭 클릭
    tab_supply = page.query_selector('text="수급 현황"')
    tab_supply.click()
    page.wait_for_timeout(1000)

    # '3대 주체별 수급 현황' 또는 수급 바차트 헤더 위치 확인 및 window / modal scroll
    page.evaluate("""() => {
        // 모든 scrollable 엘리먼트와 window를 아래로 스크롤
        const target = Array.from(document.querySelectorAll('*')).find(el => 
            el.innerText && el.innerText.includes('3대 주체별 수급 현황')
        );
        if (target) {
            const rect = target.getBoundingClientRect();
            // 화면 상단에서 60px 아래에 오도록 스크롤
            window.scrollBy(0, rect.top - 60);
            
            // 모든 부모 컨테이너도 함께 스크롤
            let p = target.parentElement;
            while (p && p !== document.body) {
                if (p.scrollHeight > p.clientHeight) {
                    p.scrollTop += (rect.top - 60);
                }
                p = p.parentElement;
            }
        }
    }""")
    page.wait_for_timeout(1000)
    page.screenshot(path="brands/stock/assets/test_s4_aligned_header.png")
    print("Saved test_s4_aligned_header.png")
    browser.close()
