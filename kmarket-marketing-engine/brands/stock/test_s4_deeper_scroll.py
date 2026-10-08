# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def test_s4_deeper_scroll():
    target_stock = "LG에너지솔루션"
    target_code = "373220"
    base_url = "https://stockmaster-ai.vercel.app/"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--hide-scrollbars",
                "--mute-audio"
            ]
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

        # 검색창에서 종목 검색 & 모달 오픈
        inp = page.query_selector('input')
        if inp:
            inp.click()
            inp.fill("")
            for char in target_stock:
                inp.type(char, delay=50)
            page.wait_for_timeout(1000)

            search_item = page.query_selector(f'text="{target_stock}"') or page.query_selector(f'text="{target_code}"') or page.query_selector('div.cursor-pointer')
            if search_item:
                search_item.click()
                page.wait_for_timeout(2000)

                # [수급 현황] 탭 클릭
                tab_supply = page.query_selector('text="수급 현황"')
                if tab_supply:
                    tab_supply.click()
                    page.wait_for_timeout(1000)

                # '3대 주체별 수급 현황' 또는 수급 바차트 헤더가 모달 최상단에 딱 오도록 scrollIntoView
                page.evaluate("""() => {
                    const targetEl = Array.from(document.querySelectorAll('*')).find(el => 
                        el.textContent && el.textContent.includes('3대 주체별 수급 현황') && el.children.length === 0
                    );
                    if (targetEl) {
                        targetEl.scrollIntoView({ behavior: 'instant', block: 'start' });
                    } else {
                        const divs = Array.from(document.querySelectorAll('div'));
                        for (let d of divs) {
                            if (d.scrollHeight > d.clientHeight && d.clientHeight > 300) {
                                d.scrollTop = 520;
                            }
                        }
                    }
                }""")
                page.wait_for_timeout(1000)
                
                path_s4 = Path("brands/stock/assets/stock_topic6_s4_supply_modal.png")
                page.screenshot(path=str(path_s4), full_page=False)
                print(f"Deeper S4 Supply Modal saved: {path_s4}")

        browser.close()

if __name__ == "__main__":
    test_s4_deeper_scroll()
