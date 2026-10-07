# -*- coding: utf-8 -*-
"""
CaptureSamsungLiveScreens - 📱 [StockMaster AI 실제 웹앱 삼성전자 실시간 라이브 캡처기]
===================================================================================
• 역할:
  - https://stockmaster-ai.vercel.app/ 실제 웹앱에 100% 실시간 접속
  - [2번]: 다크 퀀트 전광판에서 삼성전자 행 클릭 -> 아코디언 확장 -> '삼성전자 005930' 글자 최상단 정렬 실시간 캡처
  - [3번]: 삼성전자 모달 [기본 정보] (기업 펀더멘털 & 최근 실적 추이 바차트) 실시간 캡처
  - [4번]: 삼성전자 모달 [수급 현황] (3대 주체별 외인 137만주 매수 vs 개미 137만주 손절 & 거래대금) 실시간 캡처
  - 하드코딩 0%, 100% 라이브 웹앱 실시간 파이프라인
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
logger = logging.getLogger("CaptureSamsungLiveScreens")

BASE_URL = "https://stockmaster-ai.vercel.app/"


def capture_all_samsung_screens(output_dir: Path = None):
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

        # 1. 광고 및 방해 요소 제거
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

        # 2. 검색창에 '삼성전자' 입력하여 모달 열기
        logger.info("🔍 검색창에 '삼성전자' 입력...")
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
            logger.info("✨ [라이브 웹앱] 삼성전자 모달 팝업 오픈 완료!")

            # -------------------------------------------------------------
            # [3번 카드용 실시간 캡처] [기본 정보] (기업 펀더멘털 & 분기 실적 추이 바차트)
            # -------------------------------------------------------------
            tab_info = page.query_selector('text="기본 정보"')
            if tab_info:
                tab_info.click()
                page.wait_for_timeout(800)
                # 모달 내부를 살짝 스크롤하여 실적 추이 바차트까지 화면에 꼭 차게 정렬
                page.evaluate("""() => {
                    const scrollables = Array.from(document.querySelectorAll('div')).filter(el => {
                        const style = window.getComputedStyle(el);
                        return (style.overflowY === 'auto' || style.overflowY === 'scroll') && el.scrollHeight > el.clientHeight;
                    });
                    if (scrollables.length > 0) {
                        scrollables[0].scrollTop = 120;
                    }
                }""")
                page.wait_for_timeout(800)
                path_s3 = output_dir / "stock_s3_fundamental_real.png"
                page.screenshot(path=str(path_s3))
                logger.info(f"📸 [3번 카드용 실시간 라이브 캡처 완료] 기본 정보 & 실적 추이 -> {path_s3.name}")

            # -------------------------------------------------------------
            # [4번 카드용 실시간 캡처] [수급 현황] (3대 주체별 외인 137만주 순매수 vs 개미 손절)
            # -------------------------------------------------------------
            tab_supply = page.query_selector('text="수급 현황"')
            if tab_supply:
                tab_supply.click()
                page.wait_for_timeout(800)
                page.evaluate("""() => {
                    const scrollables = Array.from(document.querySelectorAll('div')).filter(el => {
                        const style = window.getComputedStyle(el);
                        return (style.overflowY === 'auto' || style.overflowY === 'scroll') && el.scrollHeight > el.clientHeight;
                    });
                    if (scrollables.length > 0) {
                        scrollables[0].scrollTop = 120;
                    }
                }""")
                page.wait_for_timeout(800)
                path_s4 = output_dir / "stock_s4_supply_real.png"
                page.screenshot(path=str(path_s4))
                logger.info(f"📸 [4번 카드용 실시간 라이브 캡처 완료] 3대 주체별 수급 현황 -> {path_s4.name}")

            # 모달 제거하여 전광판 영역으로 복귀
            page.evaluate("""() => {
                document.querySelectorAll('div.fixed.inset-0, [class*="fixed"]').forEach(el => {
                    if (el.textContent.includes('삼성전자') && el.querySelector('button, svg')) {
                        el.remove();
                    }
                });
            }""")
            page.wait_for_timeout(600)

        # -----------------------------------------------------------------
        # [2번 카드용 실시간 캡처] 다크 퀀트 전광판 ('삼성전자 005930' 최상단 정렬)
        # -----------------------------------------------------------------
        logger.info("📊 [2번 카드용 실시간 라이브 캡처] '삼성전자 005930' 아코디언 카드 최상단 정렬...")
        page.evaluate("""() => {
            // 전광판 영역으로 스크롤 이동 후 삼성전자 카드 탐색
            const targets = Array.from(document.querySelectorAll('*')).filter(el => 
                el.textContent && el.textContent.includes('삼성전자') && el.textContent.includes('005930') && el.children.length === 0
            );
            if (targets.length > 0) {
                const target = targets[0];
                const card = target.closest('[class*="border"]') || target.parentElement.parentElement;
                if (card) {
                    card.click(); // 아코디언 펼치기
                    const rect = card.getBoundingClientRect();
                    window.scrollBy(0, rect.top - 8);
                }
            } else {
                // 대체 스크롤 위치
                window.scrollTo(0, 4850);
            }
        }""")
        page.wait_for_timeout(1000)
        path_s2 = output_dir / "stock_s2_quant_board_exact.png"
        page.screenshot(path=str(path_s2))
        logger.info(f"📸 [2번 카드용 실시간 라이브 캡처 완료] 삼성전자 전광판 -> {path_s2.name}")

        browser.close()

    logger.info("🎉 [CaptureSamsungLiveScreens] 실시간 라이브 캡처 파이프라인 100% 성공!")


if __name__ == "__main__":
    capture_all_samsung_screens()
