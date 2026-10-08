# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 430, "height": 932}, device_scale_factor=2.0)
    page = context.new_page()
    page.goto("https://stockmaster-ai.vercel.app/", wait_until="networkidle")
    page.wait_for_timeout(2000)

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

    tab_supply = page.query_selector('text="수급 현황"')
    tab_supply.click()
    page.wait_for_timeout(1000)

    # 모달 내부에서 그래프 영역만 정확히 제거하여 탭 바 + 3대 주체 수급 + 거래대금/신용잔고가 상단으로 착 올라오게 함
    page.evaluate("""() => {
        // 주가/지수 추이 텍스트를 가진 컨테이너 찾기
        const pTags = Array.from(document.querySelectorAll('*')).filter(el => 
            el.textContent && el.textContent.includes('주가/지수 추이') && el.children.length === 0
        );
        for (let p of pTags) {
            // 주가/지수 추이 및 차트 영역의 직계 래퍼 찾기
            let parent = p.parentElement;
            while (parent && !parent.className.includes('bg-white')) {
                if (parent.querySelector('canvas') || parent.querySelector('svg') || parent.innerText.includes('347,500')) {
                    parent.style.display = 'none';
                    break;
                }
                parent = parent.parentElement;
            }
        }
    }""")
    page.wait_for_timeout(500)

    modal_box = page.query_selector('.bg-white.rounded-xl') or page.query_selector('.bg-white.rounded-3xl') or page.query_selector('.fixed.inset-0 > div')
    if modal_box:
        modal_box.screenshot(path="brands/stock/assets/test_s4_pure_supply_perfect.png")
        print("Saved test_s4_pure_supply_perfect.png")
    browser.close()
