# -*- coding: utf-8 -*-
"""
test_risk_modal_capture.py
- StockMaster AI 모바일 뷰에서 3번 주제용 실시간 리스크 화면들 정밀 캡처 테스트:
  1) 상단 글로벌 매크로 & 시장 종합 스트레스 지수 / VETO 필터
  2) 종목 상세 모달의 [AI 리스크 평가] 탭 (기계적 손절매 가이드 & 변동성 리스크)
  3) 10분 계량 전광판의 '🔴 배제(VETO)' 필터 클릭 화면
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    iphone = p.devices['iPhone 14 Pro']
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(**iphone)
    page = context.new_page()

    page.goto('https://stockmaster-ai.vercel.app/', wait_until='networkidle')
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

    # 2-1. [2번 슬라이드용] 전광판의 VETO 배제 종목 & 리스크 필터 화면
    page.evaluate("() => window.scrollTo(0, 1500)")
    page.wait_for_timeout(500)
    
    # '🔴 배제(VETO)' 버튼 클릭
    veto_btn = page.locator('button:has-text("배제(VETO)")')
    if veto_btn.count() > 0:
        veto_btn.first.click()
        page.wait_for_timeout(600)
        print("Clicked VETO button")
    
    page.screenshot(path=str(ASSETS_DIR / "stock_topic3_s2_veto_filter.png"))
    print("Captured slide 2 VETO filter")

    # 2-2. [3번/4번 슬라이드용] 종목 클릭 후 모달 열기 -> [AI 리스크평가] 탭 클릭
    ai_btn = page.locator('button:has-text("AI ANALYSIS")').first
    if ai_btn.count() > 0:
        ai_btn.click()
        page.wait_for_timeout(1000)
        print("Opened AI Analysis Modal")

        # 모달 탭 확인 (수급현황, 기술지표, AI 리스크평가, 기본정보)
        risk_tab = page.locator('button:has-text("AI 리스크"), button:has-text("리스크")')
        if risk_tab.count() > 0:
            risk_tab.first.click()
            page.wait_for_timeout(800)
            print("Clicked AI Risk tab in modal")
            page.screenshot(path=str(ASSETS_DIR / "stock_topic3_s3_risk_tab.png"))
            print("Captured slide 3 Risk Tab")

        # 모달 내부 스크롤해서 손절선/상세 리스크 캡처
        page.evaluate("""() => {
            const modal = document.querySelector('[role="dialog"]') || document.querySelector('[class*="fixed"]');
            if (modal) {
                const scrollable = modal.querySelector('[class*="overflow-y-auto"]') || modal;
                scrollable.scrollBy(0, 350);
            }
        }""")
        page.wait_for_timeout(600)
        page.screenshot(path=str(ASSETS_DIR / "stock_topic3_s4_stoploss_guide.png"))
        print("Captured slide 4 Stoploss Guide")

    browser.close()
    print("All captures completed successfully!")
