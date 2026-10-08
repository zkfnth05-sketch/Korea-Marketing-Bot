# -*- coding: utf-8 -*-
"""
Test perfectly focused modal bottom captures for Slide 3 (Tech indicators) and Slide 4 (Supply status)
"""
from playwright.sync_api import sync_playwright
from pathlib import Path

def test_perfect_modal_captures():
    base_url = "https://stockmaster-ai.vercel.app/"
    target_stock = "LG에너지솔루션"
    target_code = "373220"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--mute-audio"]
        )
        context = browser.new_context(
            viewport={"width": 430, "height": 932},
            device_scale_factor=2.0,
            is_mobile=True,
            has_touch=True
        )
        page = context.new_page()
        page.goto(base_url, wait_until="networkidle", timeout=35000)
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

        # 종목 검색 & 모달 오픈
        inp = page.query_selector('input')
        inp.fill("")
        for char in target_stock:
            inp.type(char, delay=40)
        page.wait_for_timeout(1000)

        item = page.query_selector(f'text="{target_stock}"') or page.query_selector('div.cursor-pointer')
        item.click()
        page.wait_for_timeout(2000)

        # =====================================================================
        # 1. Slide 3: [기술 지표] 탭 하단 핵심 지표 (체결강도, RSI, 볼린저, ATR)
        # =====================================================================
        tab_tech = page.query_selector('text="기술 지표"')
        if tab_tech:
            tab_tech.click()
            page.wait_for_timeout(800)

        # 상단 차트 숨김 처리하여 기술 지표가 모달 상단에 꽉 차게 정렬
        page.evaluate("""() => {
            const chartTitles = Array.from(document.querySelectorAll('*')).filter(el => 
                el.textContent === '주가/지수 추이' && el.children.length === 0
            );
            for (let t of chartTitles) {
                const titleRow = t.parentElement;
                if (titleRow) titleRow.style.display = 'none';
                const chartWrapper = titleRow ? titleRow.nextElementSibling : null;
                if (chartWrapper) chartWrapper.style.display = 'none';
            }
        }""")
        page.wait_for_timeout(500)

        modal_box = page.query_selector('.bg-white.rounded-xl') or page.query_selector('.fixed.inset-0 > div')
        path_s3 = Path("brands/stock/assets/stock_topic6_s3_tech_modal.png")
        modal_box.screenshot(path=str(path_s3))
        print(f"✅ Slide 3 Tech Modal saved: {path_s3}")

        # =====================================================================
        # 2. Slide 4: [수급 현황] 탭 하단 핵심 수급 (외인/기관/개인 수급 바 + 거래대금 + 신용잔고)
        # =====================================================================
        tab_supply = page.query_selector('text="수급 현황"')
        if tab_supply:
            tab_supply.click()
            page.wait_for_timeout(800)

        page.evaluate("""() => {
            const chartTitles = Array.from(document.querySelectorAll('*')).filter(el => 
                el.textContent === '주가/지수 추이' && el.children.length === 0
            );
            for (let t of chartTitles) {
                const titleRow = t.parentElement;
                if (titleRow) titleRow.style.display = 'none';
                const chartWrapper = titleRow ? titleRow.nextElementSibling : null;
                if (chartWrapper) chartWrapper.style.display = 'none';
            }
        }""")
        page.wait_for_timeout(500)

        path_s4 = Path("brands/stock/assets/stock_topic6_s4_supply_modal.png")
        modal_box.screenshot(path=str(path_s4))
        print(f"✅ Slide 4 Supply Modal saved: {path_s4}")

        browser.close()

if __name__ == "__main__":
    test_perfect_modal_captures()
