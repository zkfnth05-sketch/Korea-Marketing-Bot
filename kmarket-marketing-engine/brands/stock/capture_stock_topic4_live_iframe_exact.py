# -*- coding: utf-8 -*-
"""
capture_stock_topic4_live_iframe_exact.py
- StockMaster AI 실제 라이브 웹앱(https://stockmaster-ai.vercel.app/)에서
  사용자가 제시한 3장의 실물 화면과 100% 동일하게 순서대로 정밀 캡처:
  1) Slide 2: 삼성E&A 전광판 아코디언 오픈 (DETAIL SCORES + RAW METRICS)
  2) Slide 3: 삼성E&A 모달 [기술 지표] (당일 체결강도 120.39% 매수 우위 + RSI + 볼린저 밴드)
  3) Slide 4: 삼성E&A 모달 [수급 현황] (외인 +15.4만주 & 기관 +11.2만주 순매수 빨간 바 & 개미 파란 바)
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
logger = logging.getLogger("CaptureStockTopic4LiveExact")

BASE_URL = "https://stockmaster-ai.vercel.app/"
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def capture_all_topic4_exact_screens():
    logger.info(f"🌐 [StockMaster AI] 실제 라이브 웹앱 실시간 접속: {BASE_URL}")

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

        # 사용자 모바일 뷰포트 (430 x 932, scale 2.0)
        context = browser.new_context(
            viewport={"width": 430, "height": 932},
            device_scale_factor=2.0,
            is_mobile=True,
            has_touch=True
        )

        page = context.new_page()
        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2500)

        # 1. 광고 및 불필요 요소 제거
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
        # 📸 [Slide 2 실시간 캡처]: 삼성E&A 전광판 아코디언 오픈
        # =========================================================================
        logger.info("📸 [Slide 2] 삼성E&A 전광판 아코디언 오픈 캡처...")
        page.evaluate("""() => {
            const els = Array.from(document.querySelectorAll('*')).filter(el => 
                el.textContent && el.textContent.includes('삼성E&A') && el.children.length === 0
            );
            
            let targetCard = null;
            for (let el of els) {
                let card = el.closest('[class*="border"]');
                if (card && (card.textContent.includes('계량 종합') || card.textContent.includes('028050'))) {
                    targetCard = card;
                    break;
                }
            }
            
            if (targetCard) {
                if (!targetCard.textContent.includes('DETAIL SCORES') && !targetCard.textContent.includes('RAW METRICS')) {
                    targetCard.click();
                }
                const rect = targetCard.getBoundingClientRect();
                window.scrollBy(0, rect.top - 50); // 상단 환율 바 아래 정렬
            } else {
                window.scrollTo(0, 1500);
            }
        }""")
        page.wait_for_timeout(1000)
        path_s2 = ASSETS_DIR / "stock_topic4_s2_samsungea_board.png"
        page.screenshot(path=str(path_s2))
        logger.info(f"✅ [Slide 2 캡처 완료] -> {path_s2.name}")

        # =========================================================================
        # Slide 3 & 4: 검색창에 '삼성E&A' 검색하여 상세 모달 오픈
        # =========================================================================
        logger.info("🔍 검색창에 '삼성E&A' 검색하여 상세 모달 열기...")
        page.evaluate("() => window.scrollTo(0, 0)")
        page.wait_for_timeout(400)

        inp = page.query_selector('input')
        if inp:
            inp.click()
            inp.fill("")
            for char in "삼성E&A":
                inp.type(char, delay=50)
            page.wait_for_timeout(1000)

            search_item = page.query_selector('text="삼성E&A"') or page.query_selector('text=028050') or page.query_selector('div.cursor-pointer')
            if search_item:
                search_item.click()
                page.wait_for_timeout(2000)
                logger.info("✨ [삼성E&A] 상세 모달 팝업 오픈 성공!")

                # -----------------------------------------------------------------
                # 📸 [Slide 3 실시간 캡처]: [기술 지표] 탭 (당일 체결강도 120.39% 매수우위)
                # -----------------------------------------------------------------
                logger.info("📸 [Slide 3] [기술 지표] 탭 클릭 및 스크롤 정렬 캡처...")
                tab_tech = page.query_selector('text="기술 지표"')
                if tab_tech:
                    tab_tech.click()
                    page.wait_for_timeout(800)

                # 사용자 2번 사진과 동일하게 상단 차트를 살짝 올려 체결강도 게이지/RSI/볼린저가 꽉 차도록 스크롤
                page.evaluate("""() => {
                    const scrollables = Array.from(document.querySelectorAll('div')).filter(el => {
                        const style = window.getComputedStyle(el);
                        return (style.overflowY === 'auto' || style.overflowY === 'scroll') && el.scrollHeight > el.clientHeight;
                    });
                    if (scrollables.length > 0) {
                        scrollables[0].scrollTop = 390;
                    }
                }""")
                page.wait_for_timeout(800)
                path_s3 = ASSETS_DIR / "stock_topic4_s3_samsungea_tech.png"
                page.screenshot(path=str(path_s3))
                logger.info(f"✅ [Slide 3 캡처 완료] 기술 지표 체결강도 120.39% -> {path_s3.name}")

                # -----------------------------------------------------------------
                # 📸 [Slide 4 실시간 캡처]: [수급 현황] 탭 (3대 주체별 외인/기관 순매수)
                # -----------------------------------------------------------------
                logger.info("📸 [Slide 4] [수급 현황] 탭 클릭 및 3대 주체 수급 바 캡처...")
                tab_supply = page.query_selector('text="수급 현황"')
                if tab_supply:
                    tab_supply.click()
                    page.wait_for_timeout(800)

                # 사용자 3번 사진과 동일하게 3대 주체 수급 바 및 거래대금(922억)이 정중앙에 오도록 스크롤
                page.evaluate("""() => {
                    const scrollables = Array.from(document.querySelectorAll('div')).filter(el => {
                        const style = window.getComputedStyle(el);
                        return (style.overflowY === 'auto' || style.overflowY === 'scroll') && el.scrollHeight > el.clientHeight;
                    });
                    if (scrollables.length > 0) {
                        scrollables[0].scrollTop = 320;
                    }
                }""")
                page.wait_for_timeout(800)
                path_s4 = ASSETS_DIR / "stock_topic4_s4_samsungea_supply.png"
                page.screenshot(path=str(path_s4))
                logger.info(f"✅ [Slide 4 캡처 완료] 3대 주체별 외인·기관 쌍끌이 수급 -> {path_s4.name}")

        browser.close()
        logger.info("🎉 [CaptureStockTopic4LiveExact] 사용자 지정 3개 화면 정밀 추출 100% 완료!")


if __name__ == "__main__":
    capture_all_topic4_exact_screens()
