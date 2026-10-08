# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 430, "height": 932}, device_scale_factor=2.0)
    page = context.new_page()
    page.goto("https://stockmaster-ai.vercel.app/", wait_until="networkidle")
    page.wait_for_timeout(2000)

    # 광고 제거
    page.evaluate("""() => {
        const style = document.createElement('style');
        style.innerHTML = `
            iframe, [class*="ads"], div[id*="google"] { display: none !important; opacity: 0 !important; }
        `;
        document.head.appendChild(style);
        document.querySelectorAll('iframe, [id*="google"]').forEach(el => el.remove());
    }""")

    inp = page.query_selector('input')
    inp.fill("LG에너지솔루션")
    page.wait_for_timeout(1000)

    item = page.query_selector('text="LG에너지솔루션"') or page.query_selector('div.cursor-pointer')
    item.click()
    page.wait_for_timeout(2000)

    tab_supply = page.query_selector('text="수급 현황"')
    tab_supply.click()
    page.wait_for_timeout(1000)

    # 모달 내부 팝업 박스 자체를 찾아서 캡처
    modal_box = page.query_selector('.bg-white.rounded-3xl') or page.query_selector('.fixed.inset-0 > div')
    if modal_box:
        modal_box.screenshot(path="brands/stock/assets/full_modal_box.png")
        print("Saved full_modal_box.png")

    # 모달 내부 HTML 구조 분석
    structure = page.evaluate("""() => {
        const modal = document.querySelector('.bg-white.rounded-3xl') || document.querySelector('.fixed.inset-0');
        if (!modal) return "No modal";
        return Array.from(modal.children).map((c, i) => ({
            index: i,
            tagName: c.tagName,
            className: c.className,
            textSnippet: c.innerText ? c.innerText.substring(0, 50).replace(/\\n/g, ' ') : ''
        }));
    }""")
    print("Modal structure:", structure)
    browser.close()
