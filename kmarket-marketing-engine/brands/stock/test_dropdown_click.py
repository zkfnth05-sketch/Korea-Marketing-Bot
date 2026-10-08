# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
from pathlib import Path

def test_search_dropdown_click():
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

        # 1. 검색창에 종목코드 입력 (가장 유일하고 정확함)
        inp = page.query_selector('input')
        if inp:
            inp.click()
            inp.fill("")
            inp.type(target_code, delay=50)
            page.wait_for_timeout(1200)

            # 드롭다운에서 정확히 첫 번째 종목 클릭
            dropdown_item = page.locator(f'text="{target_stock}"').first
            if dropdown_item:
                dropdown_item.click()
                page.wait_for_timeout(2000)

            # 모달 확인
            modal = page.query_selector('.bg-white.rounded-xl') or page.query_selector('.fixed.inset-0')
            print("Modal successfully opened:", bool(modal))

            if modal:
                # -----------------------------------------------------------------
                # 3번: [기술 지표] 탭 클릭 & 상단 차트 숨김
                # -----------------------------------------------------------------
                tab_tech = page.query_selector('text="기술 지표"')
                if tab_tech:
                    tab_tech.click()
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

                modal_box = page.query_selector('.bg-white.rounded-xl')
                path_s3 = Path("brands/stock/assets/stock_topic6_s3_tech_modal.png")
                modal_box.screenshot(path=str(path_s3))
                print("Saved s3 tech modal:", path_s3)

                # -----------------------------------------------------------------
                # 4번: [수급 현황] 탭 클릭 & 상단 차트 숨김
                # -----------------------------------------------------------------
                tab_supply = page.query_selector('text="수급 현황"')
                if tab_supply:
                    tab_supply.click()
                    page.wait_for_timeout(800)

                path_s4 = Path("brands/stock/assets/stock_topic6_s4_supply_modal.png")
                modal_box.screenshot(path=str(path_s4))
                print("Saved s4 supply modal:", path_s4)

        browser.close()

if __name__ == "__main__":
    test_search_dropdown_click()
