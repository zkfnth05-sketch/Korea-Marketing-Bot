# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
from pathlib import Path

def test_open_modal_and_capture_both():
    base_url = "https://stockmaster-ai.vercel.app/"
    target_stock = "LG에너지솔루션"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 430, "height": 932}, device_scale_factor=2.0)
        page = context.new_page()
        page.goto(base_url, wait_until="networkidle")
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

        # 1. 전광판 1위 종목명 클릭하여 모달 확실하게 오픈
        page.evaluate("""() => {
            // 전광판 카드 안의 종목명 h3 또는 div 클릭
            const allH = Array.from(document.querySelectorAll('*'));
            for (let el of allH) {
                if (el.textContent && el.textContent.includes('LG에너지솔루션') && el.closest('[class*="border"]')) {
                    el.click();
                    break;
                }
            }
        }""")
        page.wait_for_timeout(2000)

        # 모달이 열렸는지 확인 (bg-white.rounded-xl 확인)
        modal_opened = page.evaluate("""() => {
            const modal = document.querySelector('.bg-white.rounded-xl') || document.querySelector('[role="dialog"]');
            return !!modal;
        }""")
        print("Modal opened successfully:", modal_opened)

        if not modal_opened:
            # 검색창으로 다시 시도
            inp = page.query_selector('input')
            inp.fill("LG에너지솔루션")
            page.wait_for_timeout(1000)
            page.keyboard.press("Enter")
            page.wait_for_timeout(1500)

        # =============================================================
        # 3번: [기술 지표] 탭 클릭 & 상단 그래프 숨김 & 모달 박스 캡처
        # =============================================================
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

        modal_box = page.query_selector('.bg-white.rounded-xl') or page.query_selector('.fixed.inset-0 > div')
        path_s3 = Path("brands/stock/assets/stock_topic6_s3_tech_modal.png")
        if modal_box:
            modal_box.screenshot(path=str(path_s3))
            print("Saved Slide 3 Tech Modal:", path_s3)

        # =============================================================
        # 4번: [수급 현황] 탭 클릭 & 상단 그래프 숨김 & 모달 박스 캡처
        # =============================================================
        tab_supply = page.query_selector('text="수급 현황"')
        if tab_supply:
            tab_supply.click()
            page.wait_for_timeout(800)

        path_s4 = Path("brands/stock/assets/stock_topic6_s4_supply_modal.png")
        if modal_box:
            modal_box.screenshot(path=str(path_s4))
            print("Saved Slide 4 Supply Modal:", path_s4)

        browser.close()

if __name__ == "__main__":
    test_open_modal_and_capture_both()
