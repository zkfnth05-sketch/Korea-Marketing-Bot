# -*- coding: utf-8 -*-
"""
InsuranceAppMobileCapture - 📱 [보험 리밸런스 모바일 실물 화면 자동 캡처기]
- 모바일 뷰포트(390x844, scale=3.0 -> 1170x2532 고해상도)로 실제 웹앱에 접속
- 3번 슬라이드용: 4세대 실손 조건 진단 폼 모바일 뷰 캡처
- 4번 슬라이드용: 34개 보험사 실시간 가격비교 순위표 모바일 뷰 캡처
"""

import time
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("InsuranceAppMobileCapture")

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def capture_mobile_screens():
    url = "https://insure-rebalance.vercel.app/"
    logger.info(f"🌐 [Playwright] 모바일 뷰포트로 웹앱 접속: {url}")

    with sync_playwright() as p:
        # iPhone 14 Pro 뷰포트 에뮬레이션
        iphone = p.devices['iPhone 14 Pro']
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(**iphone)
        page = context.new_page()

        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)

        # 1. 3번 슬라이드용 캡처 (생년월일 및 4세대 실손 조건 영역)
        logger.info("📸 3번 슬라이드 모바일 화면 캡처 중...")
        # 생년월일 입력창에 '19770101' 입력 및 조건 클릭 시뮬레이션
        try:
            inputs = page.locator("input")
            if inputs.count() > 0:
                inputs.first.fill("19770101")
        except Exception:
            pass
        page.wait_for_timeout(500)

        s3_path = ASSETS_DIR / "slide3_silbi_condition.png"
        page.screenshot(path=str(s3_path))
        logger.info(f"✅ 3번 모바일 화면 저장: {s3_path}")

        # 2. 4번 슬라이드용 캡처 (가격비교 순위표 영역)
        logger.info("📸 4번 슬라이드 모바일 화면 캡처 중...")
        # 아래 가격표 섹션으로 스크롤
        try:
            # 순위표나 가격 텍스트가 있는 요소 찾기
            page.evaluate("window.scrollTo(0, 750)")
        except Exception:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.4)")
        page.wait_for_timeout(1000)

        s4_path = ASSETS_DIR / "slide4_price_comparison.png"
        page.screenshot(path=str(s4_path))
        logger.info(f"✅ 4번 모바일 화면 저장: {s4_path}")

        browser.close()


if __name__ == "__main__":
    capture_mobile_screens()
