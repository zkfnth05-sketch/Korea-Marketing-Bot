from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    iphone = p.devices['iPhone 14 Pro Max']
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(**iphone)
    page = context.new_page()
    page.goto("https://insure-rebalance.vercel.app/", wait_until="networkidle")

    # Click 의료실비
    page.locator("button:has-text('의료실비'), div:has-text('의료실비')").first.click()
    page.wait_for_timeout(1000)

    # Click 4세대 실손
    btn = page.locator("button:has-text('4세대 실손')")
    print("Found 4세대 btn count:", btn.count())
    if btn.count() > 0:
        btn.first.click()
        page.wait_for_timeout(2000)

    # Hide header logos and floating counselor popup
    page.evaluate('''() => {
        const toHide = document.querySelectorAll('header, nav, img[src*="incar"], img[src*="logo"], [class*="planner"], [class*="Planner"], [class*="counsel"], [class*="floating"]');
        toHide.forEach(h => h.style.display = 'none');
    }''')

    page.screenshot(path="brands/insurance/real_4th_clicked.png")
    print("Saved real_4th_clicked.png")
    browser.close()
