# -*- coding: utf-8 -*-
"""
capture_topic3_live_screens.py
- StockMaster AI [주제 3번: 뇌동매매 방지 AI 리스크가드] 실제 라이브 웹앱 실시간 정밀 캡처기
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
logger = logging.getLogger("CaptureTopic3LiveScreens")

BASE_URL = "https://stockmaster-ai.vercel.app/"


def capture_all_topic3_screens(output_dir: Path = None):
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

        # 2. [2번 슬라이드용] 전광판의 '🔴 배제(VETO)' 필터 클릭 후 과열 위험 종목 캡처
        logger.info("📊 [2번 슬라이드용] 🔴 배제(VETO) 필터 클릭 및 전광판 정렬...")
        page.evaluate("() => window.scrollTo(0, 1500)")
        page.wait_for_timeout(500)

        veto_clicked = page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const b = btns.find(el => el.textContent.includes('배제') || el.textContent.includes('VETO'));
            if (b) {
                b.click();
                return true;
            }
            return false;
        }""")
        page.wait_for_timeout(800)

        path_s2 = output_dir / "stock_topic3_s2_veto_board.png"
        page.screenshot(path=str(path_s2))
        logger.info(f"📸 [2번 카드 캡처 완료] VETO 과열 전광판 -> {path_s2.name}")

        # 3. [3번/4번 슬라이드용] 검색창에서 우량주 검색하여 모달 열기
        logger.info("🔍 검색창에 종목 검색하여 모달 열기...")
        page.evaluate("() => window.scrollTo(0, 0)")
        page.wait_for_timeout(400)
        
        inp = page.query_selector('input')
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
            logger.info("✨ 모달 팝업 오픈 완료!")

            # 3-1. [3번 카드] [AI 리스크 평가] 탭 클릭
            tab_risk = page.query_selector('text="AI 리스크 평가"') or page.query_selector('text="리스크"') or page.query_selector('text="AI 리스크"')
            if tab_risk:
                tab_risk.click()
                page.wait_for_timeout(800)
                path_s3 = output_dir / "stock_topic3_s3_risk_eval.png"
                page.screenshot(path=str(path_s3))
                logger.info(f"📸 [3번 카드 캡처 완료] AI 리스크 평가 탭 -> {path_s3.name}")
            else:
                # 탭 텍스트 전체 탐색 후 클릭
                page.evaluate("""() => {
                    const tabs = Array.from(document.querySelectorAll('button, div, span'));
                    const t = tabs.find(el => el.textContent.includes('리스크'));
                    if (t) t.click();
                }""")
                page.wait_for_timeout(800)
                path_s3 = output_dir / "stock_topic3_s3_risk_eval.png"
                page.screenshot(path=str(path_s3))
                logger.info(f"📸 [3번 카드 캡처 완료] AI 리스크 평가 탭 -> {path_s3.name}")

            # 3-2. [4번 카드] 모달 내부 스크롤하여 기계적 손절매 & 지지선/과열 구간 캡처
            page.evaluate("""() => {
                const scrollables = Array.from(document.querySelectorAll('div')).filter(el => {
                    const style = window.getComputedStyle(el);
                    return (style.overflowY === 'auto' || style.overflowY === 'scroll') && el.scrollHeight > el.clientHeight;
                });
                if (scrollables.length > 0) {
                    scrollables[0].scrollTop = 220;
                }
            }""")
            page.wait_for_timeout(800)
            path_s4 = output_dir / "stock_topic3_s4_stoploss_guide.png"
            page.screenshot(path=str(path_s4))
            logger.info(f"📸 [4번 카드 캡처 완료] 기계적 손절매 & 지지선 -> {path_s4.name}")

        browser.close()
        logger.info("🎉 [CaptureTopic3LiveScreens] 3번 주제 전용 실시간 캡처 100% 완료!")


if __name__ == "__main__":
    capture_all_topic3_screens()
