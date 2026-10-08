# -*- coding: utf-8 -*-
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

def inspect_modal():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 430, "height": 932},
            device_scale_factor=2.0
        )
        page = context.new_page()
        page.goto("https://stockmaster-ai.vercel.app/", wait_until="networkidle")
        page.wait_for_timeout(2000)

        # 1. 1위 종목 검색
        inp = page.query_selector('input')
        if inp:
            inp.click()
            inp.fill("LG에너지솔루션")
            page.wait_for_timeout(1000)

            item = page.query_selector('text="LG에너지솔루션"') or page.query_selector('div.cursor-pointer')
            if item:
                item.click()
                page.wait_for_timeout(2000)

                # 모달 내부 텍스트 확인
                modal_text = page.evaluate("() => document.body.innerText")
                print("=== MODAL TEXT ===")
                print(modal_text[:500])

                # 2. [기술 지표] 탭 클릭 및 스크롤 다운 테스트
                tab_tech = page.query_selector('text="기술 지표"')
                if tab_tech:
                    tab_tech.click()
                    page.wait_for_timeout(1000)
                    
                    # 모달 내부의 스크롤 컨테이너를 찾아서 맨 아래 또는 기술 지표가 보이는 곳으로 스크롤
                    page.evaluate("""() => {
                        const divs = Array.from(document.querySelectorAll('div'));
                        for (let d of divs) {
                            if (d.scrollHeight > d.clientHeight && d.clientHeight > 200) {
                                d.scrollTop = 450; // 기술 지표 상세가 보이도록 아래로 스크롤
                            }
                        }
                    }""")
                    page.wait_for_timeout(1000)
                    page.screenshot(path="brands/stock/assets/test_tech_scrolled.png")
                    print("✅ Saved test_tech_scrolled.png")

                # 3. [수급 현황] 탭 클릭 및 스크롤 다운 테스트
                tab_supply = page.query_selector('text="수급 현황"')
                if tab_supply:
                    tab_supply.click()
                    page.wait_for_timeout(1000)
                    
                    page.evaluate("""() => {
                        const divs = Array.from(document.querySelectorAll('div'));
                        for (let d of divs) {
                            if (d.scrollHeight > d.clientHeight && d.clientHeight > 200) {
                                d.scrollTop = 450; // 수급 상세가 보이도록 아래로 스크롤
                            }
                        }
                    }""")
                    page.wait_for_timeout(1000)
                    page.screenshot(path="brands/stock/assets/test_supply_scrolled.png")
                    print("✅ Saved test_supply_scrolled.png")

        browser.close()

if __name__ == "__main__":
    inspect_modal()
