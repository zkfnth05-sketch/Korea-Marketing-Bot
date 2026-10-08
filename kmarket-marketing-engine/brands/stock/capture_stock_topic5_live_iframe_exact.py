# -*- coding: utf-8 -*-
"""
capture_stock_topic5_live_iframe_exact.py
- StockMaster AI 실제 라이브 웹앱(https://stockmaster-ai.vercel.app/)에서
  실시간으로 3장의 실물 화면을 100% 동적 크롤링 & 캡처:
  1) Slide 2: [AI 추천 종목 / 모멘텀 공략주] (테마 예측 & OFF-MARKET CACHED TOP PICK & 실시간 AI 분석 근거)
  2) Slide 3: [💡 시장 스트레스 지표별 투자 행동 지침 (RISK GUIDELINES)] & [실시간 계량 리스크 4대 지표]
  3) Slide 4: [10분 계량 전광판 1위 종목 아코디언 오픈] (DETAIL SCORES + RAW METRICS 완벽 매립)
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
logger = logging.getLogger("CaptureStockTopic5LiveExact")

BASE_URL = "https://stockmaster-ai.vercel.app/"
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def capture_all_topic5_exact_screens():
    logger.info(f"🌐 [StockMaster AI] 실제 라이브 웹앱 실시간 접속 시작: {BASE_URL}")

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
        page.goto(BASE_URL, wait_until="networkidle", timeout=35000)
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
        # 📸 [Slide 2 실시간 캡처]: AI 추천 종목 / 모멘텀 공략주 섹션 (상단 여백 80px)
        # =========================================================================
        logger.info("📸 [Slide 2] AI 추천 종목 / 모멘텀 공략주 실시간 캡처 중...")
        page.evaluate("""() => {
            const els = Array.from(document.querySelectorAll('*')).filter(el => 
                el.textContent && el.textContent.includes('테마 예측') && el.children.length === 0
            );
            if (els.length > 0) {
                const card = els[0].closest('[class*="border"]') || els[0].parentElement;
                if (card) {
                    const rect = card.getBoundingClientRect();
                    window.scrollBy(0, rect.top - 80);
                }
            }
        }""")
        page.wait_for_timeout(1000)
        s2_path = ASSETS_DIR / "stock_topic5_s2_ai_recommended.png"
        page.screenshot(path=str(s2_path), full_page=False)
        logger.info(f"✅ [Slide 2 캡처 완료]: {s2_path}")

        # =========================================================================
        # 📸 [Slide 3 실시간 캡처]: 시장 스트레스 지표별 투자 행동 지침 (상단 여백 85px)
        # =========================================================================
        logger.info("📸 [Slide 3] 시장 스트레스 지표별 투자 행동 지침 실시간 캡처 중...")
        page.evaluate("""() => {
            const els = Array.from(document.querySelectorAll('*')).filter(el => 
                el.textContent && (el.textContent.includes('RISK GUIDELINES') || el.textContent.includes('투자 행동 지침')) && el.children.length === 0
            );
            if (els.length > 0) {
                const card = els[0].closest('[class*="border"]') || els[0].parentElement;
                if (card) {
                    const rect = card.getBoundingClientRect();
                    window.scrollBy(0, rect.top - 85);
                }
            }
        }""")
        page.wait_for_timeout(1000)
        s3_path = ASSETS_DIR / "stock_topic5_s3_risk_guidelines.png"
        page.screenshot(path=str(s3_path), full_page=False)
        logger.info(f"✅ [Slide 3 캡처 완료]: {s3_path}")

        # =========================================================================
        # 📸 [Slide 4 실시간 캡처]: 10분 계량 전광판 1위 종목 아코디언 오픈 (373220 등)
        # =========================================================================
        logger.info("📸 [Slide 4] 10분 계량 전광판 1위 종목 아코디언 오픈 실시간 캡처 중...")
        page.evaluate("""() => {
            const els = Array.from(document.querySelectorAll('*')).filter(el => 
                el.textContent && (el.textContent.includes('373220') || el.textContent.includes('LG에너지솔루션') || el.textContent.includes('005930')) && el.children.length === 0
            );
            let targetCard = null;
            for (let el of els) {
                let card = el.closest('[class*="border"]');
                if (card && card.textContent.includes('계량 종합') && card.textContent.includes('진입 가능')) {
                    targetCard = card;
                    break;
                }
            }
            if (targetCard) {
                if (!targetCard.textContent.includes('DETAIL SCORES') && !targetCard.textContent.includes('RAW METRICS')) {
                    targetCard.click();
                }
            }
        }""")
        page.wait_for_timeout(1500)
        page.evaluate("""() => {
            const els = Array.from(document.querySelectorAll('*')).filter(el => 
                el.textContent && (el.textContent.includes('373220') || el.textContent.includes('LG에너지솔루션') || el.textContent.includes('005930')) && el.children.length === 0
            );
            for (let el of els) {
                let card = el.closest('[class*="border"]');
                if (card && card.textContent.includes('계량 종합')) {
                    const rect = card.getBoundingClientRect();
                    window.scrollBy(0, rect.top - 60);
                    break;
                }
            }
        }""")
        page.wait_for_timeout(1000)
        s4_path = ASSETS_DIR / "stock_topic5_s4_quant_rank1_board.png"
        page.screenshot(path=str(s4_path), full_page=False)
        logger.info(f"✅ [Slide 4 캡처 완료]: {s4_path}")

        browser.close()
        logger.info("🎉 [Topic 5] 실시간 라이브 웹앱 3개 화면 정밀 캡처 100% 완료")
        return [str(s2_path), str(s3_path), str(s4_path)]


if __name__ == "__main__":
    results = capture_all_topic5_exact_screens()
    for idx, r in enumerate(results, start=2):
        print(f"Slide {idx} Asset: {r}")
