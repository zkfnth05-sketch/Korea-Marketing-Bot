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

    # 수급 현황 탭 클릭
    tab_supply = page.query_selector('text="수급 현황"')
    tab_supply.click()
    page.wait_for_timeout(1000)

    # 모달 내부에서 상단 주가 그래프를 숨기고, 3대 주체 수급 블록과 당일 거래대금 / 신용잔고가 시원하게 채워지도록 레이아웃 정렬
    page.evaluate("""() => {
        // 주가/지수 추이 텍스트 및 그 아래 차트 영역 찾아서 display none 처리하여 수급 상세가 위로 쫙 올라오게 함
        const allEls = Array.from(document.querySelectorAll('*'));
        for (let el of allEls) {
            if (el.textContent === '주가/지수 추이' && el.children.length === 0) {
                const chartBlock = el.closest('div.mb-6') || el.closest('div.space-y-4') || el.parentElement.parentElement;
                if (chartBlock) {
                    chartBlock.style.display = 'none';
                }
            }
        }
    }""")
    page.wait_for_timeout(500)
    page.screenshot(path="brands/stock/assets/test_s4_pure_supply.png")
    print("Saved test_s4_pure_supply.png")
    browser.close()
