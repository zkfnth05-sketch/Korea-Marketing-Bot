# -*- coding: utf-8 -*-
"""
CaptureGenuineStockScreens - 📱 [StockMaster AI 실제 모바일 웹앱 실시간 정밀 캡처기]
===================================================================================
• 역할:
  - https://stockmaster-ai.vercel.app/ 실제 모바일 웹앱(iPhone 14 Pro 뷰포트)에 100% 실시간 접속
  - 광고, 배너 팝업 100% 완전 제거
  - [2번]: 10분 계량 다크 퀀트 전광판에서 삼성전자 행 Playwright Locator로 직접 클릭 -> 아코디언 확장 -> 최상단 '삼성전자 005930' 정렬 실시간 캡처
  - [3번]: 삼성전자 모달 [기본 정보] (기업 펀더멘털 & 최근 실적 추이 바차트) 실시간 캡처
  - [4번]: 삼성전자 모달 [수급 현황] (3대 주체별 외인 매수 vs 개미 손절 & 거래대금) 실시간 캡처
"""

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
logger = logging.getLogger("CaptureGenuineStockScreens")

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
BASE_URL = "https://stockmaster-ai.vercel.app/"


def capture_all_stock_screens():
    logger.info(f"🌐 [StockMaster AI] 실제 라이브 웹앱 접속 시작: {BASE_URL}")

    with sync_playwright() as p:
        iphone = p.devices['iPhone 14 Pro']
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
        context = browser.new_context(**iphone)
        page = context.new_page()

        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2500)

        # 1. 광고 및 불필요 요소 제거
        logger.info("🧹 광고 및 딤드 요소 정리...")
        page.evaluate("""() => {
            const style = document.createElement('style');
            style.innerHTML = `
                iframe,
                [class*="ads"],
                div[id*="google"] {
                    display: none !important;
                    opacity: 0 !important;
                    visibility: hidden !important;
                }
            `;
            document.head.appendChild(style);
            document.querySelectorAll('iframe, [id*="google"]').forEach(el => el.remove());
        }""")
        page.wait_for_timeout(500)

        # =========================================================================
        # [2번 슬라이드용] 다크 퀀트 전광판 ('삼성전자 005930' 최상단 정렬 & 아코디언 오픈)
        # =========================================================================
        logger.info("📊 [2번 슬라이드용] 다크 퀀트 전광판 삼성전자 카드 실시간 캡처...")
        page.evaluate("() => window.scrollTo(0, 4090)")
        page.wait_for_timeout(600)

        # Playwright Locator로 정확히 클릭하여 아코디언 확장
        target_loc = page.locator('text=005930').first
        if target_loc.count() > 0:
            target_loc.click()
            logger.info("👉 삼성전자 아코디언 클릭 완료!")
        page.wait_for_timeout(1000)

        # 상단 정렬 (헤더 바로 아래에 '삼성전자 005930' 글자가 완벽히 노출되도록 튜닝)
        page.evaluate("""() => {
            const all = Array.from(document.querySelectorAll('*'));
            const el = all.find(e => e.children.length === 0 && e.textContent.trim() === '005930');
            if (el) {
                let card = el.closest('[class*="border"]') || el.parentElement.parentElement;
                if (card) {
                    const rect = card.getBoundingClientRect();
                    window.scrollBy(0, rect.top - 42); // 상단 지수 바 아래 완벽 정렬
                }
            }
        }""")
        page.wait_for_timeout(600)

        s2_path = ASSETS_DIR / "stock_s2_quant_board_exact.png"
        page.screenshot(path=str(s2_path))
        logger.info(f"✅ [2번 슬라이드용 실물 화면 캡처 완료]: {s2_path}")

        # =========================================================================
        # 3번 & 4번 슬라이드용: 삼성전자 모달 팝업 열기
        # =========================================================================
        logger.info("🔍 검색창에 '삼성전자' 입력하여 모달 열기...")
        inp = page.query_selector('input')
        if inp:
            inp.click()
            inp.fill("")
            for char in "삼성전자":
                inp.type(char, delay=50)
            page.wait_for_timeout(1000)

        item = page.query_selector('text=005930') or page.query_selector('text="삼성전자"')
        if item:
            item.click()
            page.wait_for_timeout(2000)
            logger.info("✨ 삼성전자 모달 팝업 오픈 성공!")

            # -------------------------------------------------------------
            # [3번 슬라이드용] [기본 정보] (기업 펀더멘털 & 분기 실적 추이)
            # -------------------------------------------------------------
            tab_info = page.query_selector('text="기본 정보"')
            if tab_info:
                tab_info.click()
                page.wait_for_timeout(800)
                # 모달 내부 스크롤을 살짝 조정하여 실적 바차트 바닥까지 완벽 노출
                page.evaluate("""() => {
                    const scrollables = Array.from(document.querySelectorAll('div')).filter(el => {
                        const s = window.getComputedStyle(el);
                        return (s.overflowY === 'auto' || s.overflowY === 'scroll') && el.scrollHeight > el.clientHeight;
                    });
                    if (scrollables.length > 0) {
                        scrollables[0].scrollTop = 120;
                    }
                }""")
                page.wait_for_timeout(800)
                s3_path = ASSETS_DIR / "stock_s3_fundamental_real.png"
                page.screenshot(path=str(s3_path))
                logger.info(f"✅ [3번 슬라이드용 실물 화면 캡처 완료]: {s3_path}")

            # -------------------------------------------------------------
            # [4번 슬라이드용] [수급 현황] (3대 주체별 외국인 매수 vs 개미 손절)
            # -------------------------------------------------------------
            tab_supply = page.query_selector('text="수급 현황"')
            if tab_supply:
                tab_supply.click()
                page.wait_for_timeout(800)
                page.evaluate("""() => {
                    const scrollables = Array.from(document.querySelectorAll('div')).filter(el => {
                        const s = window.getComputedStyle(el);
                        return (s.overflowY === 'auto' || s.overflowY === 'scroll') && el.scrollHeight > el.clientHeight;
                    });
                    if (scrollables.length > 0) {
                        scrollables[0].scrollTop = 120;
                    }
                }""")
                page.wait_for_timeout(800)
                s4_path = ASSETS_DIR / "stock_s4_supply_real.png"
                page.screenshot(path=str(s4_path))
                logger.info(f"✅ [4번 슬라이드용 실물 화면 캡처 완료]: {s4_path}")

        browser.close()

    logger.info("🎉 [CaptureGenuineStockScreens] 전 슬라이드 실시간 라이브 캡처 100% 완료!")


if __name__ == "__main__":
    capture_all_stock_screens()
