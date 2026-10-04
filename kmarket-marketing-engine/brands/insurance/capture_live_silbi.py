import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    iphone = p.devices['iPhone 14 Pro Max']
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(**iphone)
    page = context.new_page()
    page.goto("https://insure-rebalance.vercel.app/", wait_until="networkidle")

    # Find and click 의료실비 category button
    calc = page.locator("#calculator-section")
    calc.scroll_into_view_if_needed()
    page.wait_for_timeout(1000)

    # Click button containing 의료실비 or 실비 or 실손
    buttons = page.locator("button, div[role='button']").all()
    for b in buttons:
        t = b.inner_text().strip()
        if "실비" in t or "실손" in t or "의료실비" in t:
            print("Clicking:", t)
            b.click()
            page.wait_for_timeout(1500)
            break

    # Hide header logos and floating counselor popup
    page.evaluate('''() => {
        const toHide = document.querySelectorAll('header, nav, img[src*="incar"], img[src*="logo"], [class*="planner"], [class*="Planner"], [class*="counsel"], [class*="floating"]');
        toHide.forEach(h => h.style.display = 'none');
    }''')

    # Fill birthdate if input exists
    inputs = page.locator("input").all()
    if inputs:
        inputs[0].fill("19770101")
        page.wait_for_timeout(1000)

    # Scroll to the form section for Slide 3
    page.screenshot(path="brands/insurance/real_live_slide3_mobile.png")
    print("Saved real_live_slide3_mobile.png")

    # Scroll down to ranking table for Slide 4
    page.evaluate("window.scrollBy(0, 700)")
    page.wait_for_timeout(1000)
    page.screenshot(path="brands/insurance/real_live_slide4_mobile.png")
    print("Saved real_live_slide4_mobile.png")

    browser.close()
