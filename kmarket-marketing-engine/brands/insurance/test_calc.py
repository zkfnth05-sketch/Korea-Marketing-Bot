from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 430, "height": 932})
    page.goto("https://insure-rebalance.vercel.app/", wait_until="networkidle")

    # Scroll directly to #calculator-section
    calc = page.locator("#calculator-section")
    calc.scroll_into_view_if_needed()
    page.wait_for_timeout(1000)

    # Inspect all buttons/categories inside #calculator-section
    buttons = calc.locator("button, div[role='button']").all()
    print("Found buttons in calc:", len(buttons))
    for b in buttons:
        t = b.inner_text().strip()
        if len(t) > 0 and len(t) < 40:
            print("Button:", t)

    # Let's take screenshot of calculator section on mobile
    page.screenshot(path="brands/insurance/real_calc_mobile.png")
    print("Saved real_calc_mobile.png")
    browser.close()
