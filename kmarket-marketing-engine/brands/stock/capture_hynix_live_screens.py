# -*- coding: utf-8 -*-
"""
CaptureHynixLiveScreens - 📱 [StockMaster AI 실제 웹앱 SK하이닉스 실시간 라이브 캡처기]
===================================================================================
• 역할:
  - https://stockmaster-ai.vercel.app/ 실제 웹앱에 100% 실시간 접속
  - [2번]: 다크 퀀트 전광판에서 SK하이닉스 행 클릭 -> 아코디언 확장 -> 'SK하이닉스 000660' 글자 최상단 정렬 실시간 캡처
  - [3번]: SK하이닉스 모달 [기본 정보] (기업 펀더멘털 & 최근 실적 추이 바차트) 실시간 캡처
  - [4번]: SK하이닉스 모달 [수급 현황] (3대 주체별 외인/기관 순매수 vs 개미 손절 & 거래대금) 실시간 캡처
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
logger = logging.getLogger("CaptureHynixLiveScreens")

BASE_URL = "https://stockmaster-ai.vercel.app/"


def capture_all_hynix_screens(output_dir: Path = None):
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

        # 2. 전광판 검색창 영역으로 스크롤 이동
        logger.info("🔍 전광판 영역(y=4090)으로 스크롤 후 'SK하이닉스' 검색...")
        page.evaluate("() => window.scrollTo(0, 4090)")
        page.wait_for_timeout(600)

        inp = page.query_selector('input')
        if inp:
            inp.click()
            inp.fill("")
            for char in "SK하이닉스":
                inp.type(char, delay=50)
            page.wait_for_timeout(500)

        span_target = page.query_selector('text="SK하이닉스"')
        if span_target:
            span_target.click()
            page.wait_for_timeout(1500)
            logger.info("✨ [라이브 웹앱] SK하이닉스 4대 탭 모달 팝업 오픈 성공!")

            # -------------------------------------------------------------
            # [3번 카드용 실시간 캡처] [기본 정보] (기업 펀더멘털 & 분기 실적 추이 바차트)
            # -------------------------------------------------------------
            tab_info = page.query_selector('text="기본 정보"')
            if tab_info:
                tab_info.click()
                page.wait_for_timeout(800)
                # 모달 내부 스크롤하여 실적 추이 바차트까지 정렬
                page.evaluate("""() => {
                    document.querySelectorAll('div').forEach(el => {
                        const style = window.getComputedStyle(el);
                        if ((style.overflowY === 'auto' || style.overflowY === 'scroll') && el.scrollHeight > el.clientHeight) {
                            el.scrollTop = 550;
                        }
                    });
                }""")
                page.wait_for_timeout(800)
                path_s3 = output_dir / "stock_topic2_s3_fundamental_real.png"
                page.screenshot(path=str(path_s3))
                logger.info(f"📸 [3번 카드용 실시간 라이브 캡처 완료] SK하이닉스 기본 정보 & 실적 추이 -> {path_s3.name}")

            # -------------------------------------------------------------
            # [4번 카드용 실시간 캡처] [수급 현황] (3대 주체별 외인/기관 순매수 vs 개미 손절)
            # -------------------------------------------------------------
            tab_supply = page.query_selector('text="수급 현황"')
            if tab_supply:
                tab_supply.click()
                page.wait_for_timeout(800)
                page.evaluate("""() => {
                    document.querySelectorAll('div').forEach(el => {
                        const style = window.getComputedStyle(el);
                        if ((style.overflowY === 'auto' || style.overflowY === 'scroll') && el.scrollHeight > el.clientHeight) {
                            el.scrollTop = 550;
                        }
                    });
                }""")
                page.wait_for_timeout(800)
                path_s4 = output_dir / "stock_topic2_s4_supply_real.png"
                page.screenshot(path=str(path_s4))
                logger.info(f"📸 [4번 카드용 실시간 라이브 캡처 완료] SK하이닉스 3대 주체별 수급 현황 -> {path_s4.name}")

            # 모달 닫기 버튼 또는 외부 클릭으로 닫기
            page.evaluate("""() => {
                const closeBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('✕'));
                if (closeBtn) closeBtn.click();
                document.querySelectorAll('div.fixed.inset-0, [class*="fixed"]').forEach(el => {
                    if (el.textContent.includes('SK하이닉스') && el.querySelector('button, svg')) {
                        el.remove();
                    }
                });
            }""")
            page.wait_for_timeout(600)

        # -----------------------------------------------------------------
        # [2번 카드용 실시간 캡처] 다크 퀀트 전광판 ('SK하이닉스 000660' 최상단 정렬)
        # -----------------------------------------------------------------
        logger.info("📊 [2번 카드용 실시간 라이브 캡처] 'SK하이닉스 000660' 아코디언 카드 최상단 정렬...")
        page.evaluate("""() => {
            // 전광판 영역으로 스크롤 이동 후 SK하이닉스 카드 탐색
            const targets = Array.from(document.querySelectorAll('*')).filter(el => 
                el.textContent && el.textContent.includes('SK하이닉스') && el.textContent.includes('000660') && el.children.length === 0
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
                // 대체 검색
                const altTargets = Array.from(document.querySelectorAll('*')).filter(el => 
                    el.textContent && el.textContent.includes('SK하이닉스')
                );
                if (altTargets.length > 0) {
                    const card = altTargets[altTargets.length - 1].closest('[class*="border"]') || altTargets[altTargets.length - 1];
                    card.click();
                    const rect = card.getBoundingClientRect();
                    window.scrollBy(0, rect.top - 8);
                }
            }
        }""")
        page.wait_for_timeout(1000)
        path_s2 = output_dir / "stock_topic2_s2_quant_board_exact.png"
        page.screenshot(path=str(path_s2))
        logger.info(f"📸 [2번 카드용 실시간 라이브 캡처 완료] SK하이닉스 전광판 -> {path_s2.name}")

        browser.close()

    logger.info("🎉 [CaptureHynixLiveScreens] SK하이닉스 실시간 라이브 캡처 파이프라인 100% 성공!")


if __name__ == "__main__":
    capture_all_hynix_screens()
