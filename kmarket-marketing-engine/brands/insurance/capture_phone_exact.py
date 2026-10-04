from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 1080})
    page.goto("https://insure-rebalance.vercel.app/", wait_until="networkidle")

    # Click 의료실비 -> 4세대 실손
    page.get_by_text("의료실비").first.click()
    page.wait_for_timeout(1000)
    page.get_by_text("4세대 실손").first.click()
    page.wait_for_timeout(1000)

    # Hide floating counselor button
    page.evaluate('''() => {
        document.querySelectorAll('[class*="planner"], [class*="Planner"], [class*="counsel"]').forEach(e => e.remove());
    }''')

    # Capture the phone mockup on the live web app
    phone_container = page.locator("div.select-none:has-text('14:33')").first
    phone_container.scroll_into_view_if_needed()
    page.wait_for_timeout(1000)

    phone_container.screenshot(path="brands/insurance/assets/real_live_phone_mockup.png")
    print("Saved real_live_phone_mockup.png")
    browser.close()
