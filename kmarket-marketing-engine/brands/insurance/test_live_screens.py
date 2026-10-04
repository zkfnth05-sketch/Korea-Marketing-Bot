from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    iphone = p.devices['iPhone 14 Pro Max']
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(**iphone)
    page = context.new_page()
    page.goto("https://insure-rebalance.vercel.app/", wait_until="networkidle")

    # Hide header logos and floating counselor popup
    page.evaluate('''() => {
        const toHide = document.querySelectorAll('header, nav, img[src*="incar"], img[src*="logo"], [class*="planner"], [class*="Planner"], [class*="counsel"], [class*="floating"]');
        toHide.forEach(h => h.style.display = 'none');
    }''')

    # Click 의료실비 button
    buttons = page.locator("button, div[role='button']").all()
    for b in buttons:
        t = b.inner_text().strip()
        if "실비" in t or "실손" in t or "의료실비" in t:
            print("Clicking:", t)
            b.click()
            page.wait_for_timeout(2000)
            break

    # Screenshot right after clicking
    page.screenshot(path="brands/insurance/live_after_click_silbi.png")
    print("Saved live_after_click_silbi.png")

    # Scroll down 600px
    page.evaluate("window.scrollBy(0, 600)")
    page.wait_for_timeout(1000)
    page.screenshot(path="brands/insurance/live_after_click_scroll1.png")
    print("Saved live_after_click_scroll1.png")

    # Scroll down another 600px
    page.evaluate("window.scrollBy(0, 600)")
    page.wait_for_timeout(1000)
    page.screenshot(path="brands/insurance/live_after_click_scroll2.png")
    print("Saved live_after_click_scroll2.png")

    browser.close()
