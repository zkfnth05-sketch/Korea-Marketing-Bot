# -*- coding: utf-8 -*-
"""
capture_topic4_live_screens.py
- StockMaster AI [주제 4번: 체결 가속도(+%p) 급증 시그널] 실제 라이브 웹앱 실시간 정밀 캡처기
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
logger = logging.getLogger("CaptureTopic4LiveScreens")

BASE_URL = "https://stockmaster-ai.vercel.app/"


def capture_all_topic4_screens(output_dir: Path = None):
    if output_dir is None:
        output_dir = Path(__file__).resolve().parent / "assets"
    output_dir.mkdir(parents=True, exist_ok=True)

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
            viewport={"width": 430, "height": 920},
            device_scale_factor=2.0,
            is_mobile=True,
            has_touch=True
        )

        page = context.new_page()
        logger.info(f"🌐 [StockMaster AI] 실시간 라이브 웹앱 접속: {BASE_URL}")
        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

        # 1. 광고 제거
        page.evaluate("""() => {
            const style = document.createElement('style');
            style.innerHTML = `
                iframe, [class*="ads"], div[id*="google"] { display: none !important; opacity: 0 !important; }
            `;
            document.head.appendChild(style);
            document.querySelectorAll('iframe, [id*="google"]').forEach(el => el.remove());
        }""")
        page.wait_for_timeout(500)

        # 2. [2번 슬라이드용] 10분 체결 가속도 전광판 캡처
        logger.info("📊 [2번 슬라이드용] 10분 계량 전광판 영역으로 스크롤 & 캡처...")
        page.evaluate("() => window.scrollTo(0, 750)")
        page.wait_for_timeout(800)

        path_s2 = output_dir / "stock_topic4_s2_accel_board.png"
        page.screenshot(path=str(path_s2))
        logger.info(f"📸 [2번 카드 캡처 완료] 체결가속도 전광판 -> {path_s2.name}")

        # 3. [3번/4번 슬라이드용] 검색창에서 주도주(SK하이닉스/삼성전자 등) 검색하여 모달 열기
        logger.info("🔍 검색창에 종목 검색하여 모달 열기...")
        page.evaluate("() => window.scrollTo(0, 0)")
        page.wait_for_timeout(400)

        inp = page.query_selector('input')
        if inp:
            inp.click()
            inp.fill("")
            for char in "SK하이닉스":
                inp.type(char, delay=50)
            page.wait_for_timeout(800)

        item = page.query_selector('text=000660') or page.query_selector('text="SK하이닉스"')
        if not item:
            if inp:
                inp.click()
                inp.fill("")
                for char in "삼성전자":
                    inp.type(char, delay=50)
                page.wait_for_timeout(800)
            item = page.query_selector('text=005930') or page.query_selector('text="삼성전자"')

        if item:
            item.click()
            page.wait_for_timeout(2000)
            logger.info("✨ 종목 상세 모달 팝업 오픈 완료!")

            # 3-1. [3번 카드] [수급 분석] 또는 기본 체결강도 탭 캡처
            tab_supply = page.query_selector('text="수급 분석"') or page.query_selector('text="수급"')
            if tab_supply:
                tab_supply.click()
                page.wait_for_timeout(800)

            path_s3 = output_dir / "stock_topic4_s3_top1_supply_accel.png"
            page.screenshot(path=str(path_s3))
            logger.info(f"📸 [3번 카드 캡처 완료] 실시간 수급 & 체결강도 -> {path_s3.name}")

            # 3-2. [4번 카드] 모달 스크롤 또는 대량 체결 / 퀀트 점수 탭 캡처
            tab_quant = page.query_selector('text="퀀트 분석"') or page.query_selector('text="AI 퀀트"') or page.query_selector('text="AI 리스크"')
            if tab_quant:
                tab_quant.click()
                page.wait_for_timeout(800)

            page.evaluate("""() => {
                const scrollables = Array.from(document.querySelectorAll('div')).filter(el => {
                    const style = window.getComputedStyle(el);
                    return (style.overflowY === 'auto' || style.overflowY === 'scroll') && el.scrollHeight > el.clientHeight;
                });
                if (scrollables.length > 0) {
                    scrollables[0].scrollTop = 180;
                }
            }""")
            page.wait_for_timeout(800)
            path_s4 = output_dir / "stock_topic4_s4_block_orders.png"
            page.screenshot(path=str(path_s4))
            logger.info(f"📸 [4번 카드 캡처 완료] 세력 대량 체결 & 퀀트 분석 -> {path_s4.name}")

        browser.close()
        logger.info("🎉 [CaptureTopic4LiveScreens] 4번 주제 전용 실시간 캡처 완료!")


if __name__ == "__main__":
    capture_all_topic4_screens()
