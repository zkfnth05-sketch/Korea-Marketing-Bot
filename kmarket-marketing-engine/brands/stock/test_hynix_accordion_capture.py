# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

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
    page.goto('https://stockmaster-ai.vercel.app/', wait_until='domcontentloaded')
    page.wait_for_timeout(2000)
    
    # 1. 광고 제거
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
    
    # 2. 전광판 영역으로 먼저 스크롤 이동
    page.evaluate("() => window.scrollTo(0, 4850)")
    page.wait_for_timeout(1000)

    # 3. 전광판 영역에서 SK하이닉스 000660 카드 찾아서 클릭 및 최상단 정렬
    res = page.evaluate("""() => {
        // 전광판 내의 SK하이닉스 요소 찾기
        const targets = Array.from(document.querySelectorAll('*')).filter(el => 
            el.textContent && el.textContent.includes('SK하이닉스') && el.textContent.includes('000660') && el.children.length === 0
        );
        if (targets.length > 0) {
            // 전광판 내의 첫 번째(또는 해당) 타깃
            const target = targets[0];
            let card = target;
            while (card && card !== document.body) {
                if (card.classList.contains('border') || (card.className && card.className.includes('border'))) {
                    break;
                }
                card = card.parentElement;
            }
            if (card) {
                card.click(); // 아코디언 펼치기
                const rect = card.getBoundingClientRect();
                window.scrollBy(0, rect.top - 8);
                return { success: true, top: rect.top, tag: card.tagName };
            }
        }
        return { success: false, targetsCount: targets.length };
    }""")
    print("Accordion click result:", res)
    page.wait_for_timeout(1500)
    
    # 추가로 정확한 상단 정렬
    page.evaluate("""() => {
        const targets = Array.from(document.querySelectorAll('*')).filter(el => 
            el.textContent && el.textContent.includes('SK하이닉스') && el.textContent.includes('000660') && el.children.length === 0
        );
        if (targets.length > 0) {
            const card = targets[0].closest('[class*="border"]') || targets[0].parentElement.parentElement;
            if (card) {
                const rect = card.getBoundingClientRect();
                window.scrollBy(0, rect.top - 8);
            }
        }
    }""")
    page.wait_for_timeout(800)
    
    out_path = Path("brands/stock/assets/stock_topic2_s2_quant_board_exact.png")
    page.screenshot(path=str(out_path))
    print(f"Captured: {out_path} ({out_path.stat().st_size} bytes)")
    browser.close()
