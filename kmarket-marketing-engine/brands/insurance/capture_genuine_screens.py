# -*- coding: utf-8 -*-
"""
InsuranceAppGenuineCapture - 📱 [보험 리밸런스 모바일 실물 웹앱 정밀 캡처기]
- 실제 배포된 웹앱(https://insure-rebalance.vercel.app/)에 모바일 뷰포트로 접속
- 의료실비 -> 4세대 실손 클릭 -> 생년월일 19770101 자동 입력
- 헤더 로고 및 플로팅 상담 팝업 100% 제거
- 3번 슬라이드용: 4세대 실손 조건/고지사항 진단 폼 실물 화면 캡처
- 4번 슬라이드용: 34개 보험사 실시간 가격비교 15,081원 순위표 실물 화면 캡처
"""

import time
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("InsuranceAppGenuineCapture")

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def capture_all_screens():
    url = "https://insure-rebalance.vercel.app/"
    logger.info(f"🌐 [Playwright] 실제 웹앱 접속: {url}")

    with sync_playwright() as p:
        iphone = p.devices['iPhone 14 Pro']
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(**iphone)
        page = context.new_page()

        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)

        # 1. 의료실비 클릭
        logger.info("👉 '의료실비' 카테고리 클릭...")
        page.get_by_text("의료실비").first.click()
        page.wait_for_timeout(1000)

        # 2. 4세대 실손 클릭
        logger.info("👉 '4세대 실손' 클릭...")
        page.evaluate('''() => {
            const els = Array.from(document.querySelectorAll('*'));
            for (const el of els) {
                if (el.textContent.trim() === '4세대 실손' && el.children.length === 0) {
                    el.click();
                    if (el.parentElement) el.parentElement.click();
                    break;
                }
            }
        }''')
        page.wait_for_timeout(2000)

        # 3. 헤더 로고 및 하단 상담 팝업 완전 제거 (CSS Injection)
        logger.info("🧹 헤더 로고 및 플로팅 상담 팝업 제거...")
        page.evaluate('''() => {
            const removeSelectors = [
                'header', 'nav', 
                'img[src*="incar"]', 'img[src*="logo"]', 
                '[class*="planner"]', '[class*="Planner"]', 
                '[class*="counsel"]', '[class*="floating"]', '[class*="Floating"]'
            ];
            removeSelectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(el => el.remove());
            });
        }''')
        page.wait_for_timeout(500)

        # 4. 생년월일 입력
        try:
            inp = page.locator("input[placeholder*='1977'], input").first
            inp.fill("19770101")
            page.wait_for_timeout(1000)
        except Exception as ie:
            logger.warning(f"입력창 필드 처리: {ie}")

        # 5. 3번 슬라이드: 4세대 실손 조건/고지사항 영역 스크롤 및 캡처
        logger.info("📸 3번 슬라이드 실물 모바일 화면 캡처 중...")
        page.evaluate('''() => {
            const target = Array.from(document.querySelectorAll('*')).find(e => e.textContent.includes('4세대 실손 가입 전 고지사항'));
            if (target) {
                target.scrollIntoView({ behavior: 'instant', block: 'start' });
                window.scrollBy(0, -120);
            } else {
                window.scrollTo(0, 1800);
            }
        }''')
        page.wait_for_timeout(1000)

        s3_path = ASSETS_DIR / "slide3_silbi_condition.png"
        page.screenshot(path=str(s3_path))
        logger.info(f"✅ 3번 모바일 실물 화면 저장 완료: {s3_path}")

        # 6. 4번 슬라이드: 34개 보험사 순위표 영역 스크롤 및 캡처
        logger.info("📸 4번 슬라이드 실물 모바일 순위표 캡처 중...")
        page.evaluate('''() => {
            const table = document.querySelector('table') || Array.from(document.querySelectorAll('*')).find(e => e.textContent.includes('J손보') || e.textContent.includes('15,081'));
            if (table) {
                table.scrollIntoView({ behavior: 'instant', block: 'start' });
                window.scrollBy(0, -50);
            } else {
                window.scrollBy(0, 750);
            }
        }''')
        page.wait_for_timeout(1000)

        s4_path = ASSETS_DIR / "slide4_price_comparison.png"
        page.screenshot(path=str(s4_path))
        logger.info(f"✅ 4번 모바일 실물 화면 저장 완료: {s4_path}")

        browser.close()


if __name__ == "__main__":
    capture_all_screens()
