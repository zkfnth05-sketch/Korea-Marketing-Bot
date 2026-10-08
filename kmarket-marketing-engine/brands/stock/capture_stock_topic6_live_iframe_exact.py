# -*- coding: utf-8 -*-
"""
capture_stock_topic6_live_iframe_exact.py
- 4번 주제 카드뉴스 공식 메커니즘 100% 동일 복제:
  1) Slide 2: [10분 계량 전광판 1위 종목(LG에너지솔루션) 아코디언 오픈] (DETAIL SCORES + RAW METRICS)
  2) Slide 3: [1위 종목 상세 모달 ➔ 기술 지표 탭] (체결강도 145.02% + RSI + 볼린저 밴드)
  3) Slide 4: [1위 종목 상세 모달 ➔ 수급 현황 탭] (3대 주체별 외인·기관·개인 순매수 바 & 거래대금 3,743억원)
"""

import os
import sys
import time
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CaptureStockTopic6LiveExact")

BASE_URL = "https://stockmaster-ai.vercel.app/"
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def capture_all_topic6_exact_screens(target_stock: str = "LG에너지솔루션", target_code: str = "373220"):
    logger.info(f"🌐 [StockMaster AI 6번 주제] 실제 라이브 웹앱 실시간 접속 시작: {BASE_URL}")

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
        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2500)

        # 0. 광고 제거
        page.evaluate("""() => {
            const style = document.createElement('style');
            style.innerHTML = `
                iframe, [class*="ads"], div[id*="google"] { display: none !important; opacity: 0 !important; }
            `;
            document.head.appendChild(style);
            document.querySelectorAll('iframe, [id*="google"]').forEach(el => el.remove());
        }""")
        page.wait_for_timeout(500)

        # =========================================================================
        # 📸 [Slide 2 실시간 캡처]: 전광판 1위 종목(LG에너지솔루션) 아코디언 오픈 (4번 주제 방식 100% 동일)
        # =========================================================================
        logger.info(f"📸 [Slide 2] 전광판 1위 종목({target_stock}) 아코디언 오픈 캡처 중...")
        page.evaluate(f"""() => {{
            const allEls = Array.from(document.querySelectorAll('*'));
            let targetCard = null;
            for (let el of allEls) {{
                if (el.textContent && el.textContent.includes('{target_code}') && el.children.length === 0) {{
                    let card = el.closest('[class*="border"]');
                    if (card && card.textContent.includes('계량 종합')) {{
                        targetCard = card;
                        break;
                    }}
                }}
            }}
            
            if (targetCard) {{
                if (!targetCard.textContent.includes('DETAIL SCORES') && !targetCard.textContent.includes('RAW METRICS')) {{
                    targetCard.click();
                }}
                const rect = targetCard.getBoundingClientRect();
                window.scrollBy(0, rect.top - 50); // 상단 환율 바 아래 정렬
            }}
        }}""")
        page.wait_for_timeout(1200)
        path_s2 = ASSETS_DIR / "stock_topic6_s2_quant_board.png"
        page.screenshot(path=str(path_s2))
        logger.info(f"✅ [Slide 2 캡처 완료]: {path_s2.name}")

        # =========================================================================
        # Slide 3 & 4: 검색창에서 1위 종목 검색하여 4대 모달 팝업 오픈 (4번 주제 방식 100% 동일)
        # =========================================================================
        logger.info(f"🔍 검색창에 '{target_code}' 검색하여 상세 모달 열기...")
        page.evaluate("() => window.scrollTo(0, 0)")
        page.wait_for_timeout(400)

        inp = page.query_selector('input')
        if inp:
            inp.click()
            inp.fill("")
            inp.type(target_code, delay=50)
            page.wait_for_timeout(1000)

            dropdown_item = page.locator(f'text="{target_stock}"').first
            if dropdown_item:
                dropdown_item.click()
                page.wait_for_timeout(2000)
                logger.info(f"✨ [{target_stock}] 상세 모달 팝업 오픈 성공!")

                # -----------------------------------------------------------------
                # 📸 [Slide 3 실시간 캡처]: [기술 지표] 탭 (4번 주제 스크롤 390px)
                # -----------------------------------------------------------------
                logger.info("📸 [Slide 3] [기술 지표] 탭 클릭 및 스크롤 390px 캡처...")
                tab_tech = page.query_selector('text="기술 지표"')
                if tab_tech:
                    tab_tech.click()
                    page.wait_for_timeout(800)

                page.evaluate("""() => {
                    const modal = document.querySelector('.fixed.inset-0.overflow-y-auto') || document.querySelector('.fixed.inset-0');
                    if (modal) {
                        modal.scrollTop = 390;
                    }
                }""")
                page.wait_for_timeout(800)
                path_s3 = ASSETS_DIR / "stock_topic6_s3_tech_modal.png"
                page.screenshot(path=str(path_s3))
                logger.info(f"✅ [Slide 3 캡처 완료] 기술 지표 -> {path_s3.name}")

                # -----------------------------------------------------------------
                # 📸 [Slide 4 실시간 캡처]: [수급 현황] 탭 (4번 주제 스크롤 320px)
                # -----------------------------------------------------------------
                logger.info("📸 [Slide 4] [수급 현황] 탭 클릭 및 스크롤 320px 캡처...")
                tab_supply = page.query_selector('text="수급 현황"')
                if tab_supply:
                    tab_supply.click()
                    page.wait_for_timeout(800)

                page.evaluate("""() => {
                    const modal = document.querySelector('.fixed.inset-0.overflow-y-auto') || document.querySelector('.fixed.inset-0');
                    if (modal) {
                        modal.scrollTop = 320;
                    }
                }""")
                page.wait_for_timeout(800)
                path_s4 = ASSETS_DIR / "stock_topic6_s4_supply_modal.png"
                page.screenshot(path=str(path_s4))
                logger.info(f"✅ [Slide 4 캡처 완료] 수급 현황 -> {path_s4.name}")

        browser.close()
        logger.info("🎉 [Topic 6] 4번 주제 공식 규격 3대 화면 정밀 캡처 100% 완료")
        return [str(path_s2), str(path_s3), str(path_s4)]


if __name__ == "__main__":
    capture_all_topic6_exact_screens()
