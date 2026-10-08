# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

output_dir = Path(r"c:\Users\zkfnt\Desktop\한국 마케팅봇\kmarket-marketing-engine\brands\stock\assets")
output_dir.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 430, "height": 932},
        device_scale_factor=2.0,
        is_mobile=True,
        has_touch=True
    )
    page = context.new_page()
    page.goto("https://stockmaster-ai.vercel.app/", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2500)

    # 광고 제거
    page.evaluate("""() => {
        const style = document.createElement('style');
        style.innerHTML = 'iframe, [class*="ads"], div[id*="google"] { display: none !important; }';
        document.head.appendChild(style);
        document.querySelectorAll('iframe, [id*="google"]').forEach(el => el.remove());
    }""")
    page.wait_for_timeout(500)

    # 1. AI 1위 종목 카드 & 분석 근거
    page.evaluate("""() => {
        const el = Array.from(document.querySelectorAll('*')).find(e => e.textContent && e.textContent.includes('테마 예측') && e.children.length === 0);
        if (el) {
            const card = el.closest('div');
            const rect = card.getBoundingClientRect();
            window.scrollBy(0, rect.top - 50);
        } else {
            window.scrollTo(0, 300);
        }
    }""")
    page.wait_for_timeout(600)
    page.screenshot(path=str(output_dir / "live_sec1_ai_pick.png"))

    # 2. 시장 스트레스 지표 (리스크 센터)
    page.evaluate("""() => {
        const el = Array.from(document.querySelectorAll('*')).find(e => e.textContent && e.textContent.includes('시장 스트레스 지표별') && e.children.length === 0);
        if (el) {
            const rect = el.getBoundingClientRect();
            window.scrollBy(0, rect.top - 50);
        } else {
            window.scrollTo(0, 750);
        }
    }""")
    page.wait_for_timeout(600)
    page.screenshot(path=str(output_dir / "live_sec2_risk_center.png"))

    # 3. 계량 전광판 1위 아코디언 오픈
    page.evaluate("""() => {
        const items = Array.from(document.querySelectorAll('*')).filter(el => el.textContent && el.textContent.includes('계량 종합') && el.children.length === 0);
        let targetCard = null;
        for (let el of items) {
            let card = el.closest('[class*="border"]');
            if (card) {
                targetCard = card;
                break;
            }
        }
        if (targetCard) {
            if (!targetCard.textContent.includes('DETAIL SCORES')) {
                targetCard.click();
            }
            const rect = targetCard.getBoundingClientRect();
            window.scrollBy(0, rect.top - 50);
        } else {
            window.scrollTo(0, 1400);
        }
    }""")
    page.wait_for_timeout(800)
    page.screenshot(path=str(output_dir / "live_sec3_quant_board.png"))

    browser.close()
    print("All 3 main sections captured successfully!")
