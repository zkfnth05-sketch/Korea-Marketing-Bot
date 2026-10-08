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

    # 10분 계량 전광판 1위 LG에너지솔루션 아코디언 열기 및 스크롤
    page.evaluate("""() => {
        const items = Array.from(document.querySelectorAll('*')).filter(el => 
            el.textContent && (el.textContent.includes('373220') || (el.textContent.includes('LG에너지솔루션') && el.textContent.includes('계량 종합'))) && el.children.length === 0
        );
        let targetCard = null;
        for (let el of items) {
            let card = el.closest('[class*="border"]');
            if (card && card.textContent.includes('계량 종합')) {
                targetCard = card;
                break;
            }
        }
        if (targetCard) {
            // 아코디언이 열려있지 않으면 클릭
            if (!targetCard.textContent.includes('DETAIL SCORES') && !targetCard.textContent.includes('계량 가중치')) {
                targetCard.click();
            }
            const rect = targetCard.getBoundingClientRect();
            window.scrollBy(0, rect.top - 40);
        }
    }""")
    page.wait_for_timeout(1000)
    page.screenshot(path=str(output_dir / "live_sec3_quant_board_opened.png"))
    browser.close()
    print("Accordion capture finished!")
