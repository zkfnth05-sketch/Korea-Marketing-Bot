from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    iphone = p.devices['iPhone 14 Pro Max']
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(**iphone)
    page = context.new_page()
    page.goto("https://insure-rebalance.vercel.app/", wait_until="networkidle")

    # Click 의료실비
    page.get_by_text("의료실비").first.click()
    page.wait_for_timeout(1000)

    # Click 4세대 실손
    page.get_by_text("4세대 실손").first.click()
    page.wait_for_timeout(2000)

    # Hide header logos and floating counselor popup
    page.evaluate('''() => {
        const toHide = document.querySelectorAll('header, nav, img[src*="incar"], img[src*="logo"], [class*="planner"], [class*="Planner"], [class*="counsel"], [class*="floating"]');
        toHide.forEach(h => h.style.display = 'none');
    }''')

    # Fill 19770101
    try:
        page.locator("input").first.fill("19770101")
        page.wait_for_timeout(1000)
    except Exception as e:
        print("Input error:", e)

    page.screenshot(path="brands/insurance/real_live_form_success.png")
    print("Saved real_live_form_success.png")

    # Scroll to table
    page.evaluate("window.scrollBy(0, 800)")
    page.wait_for_timeout(1000)
    page.screenshot(path="brands/insurance/real_live_table_success.png")
    print("Saved real_live_table_success.png")

    browser.close()
