from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 1080})
    page.goto("https://insure-rebalance.vercel.app/", wait_until="networkidle")

    # Find the phone element in calculator section
    # Let's find element with 14:33 or phone chassis
    phone_locator = page.locator("div:has-text('14:33')").last
    print("Found phone locator:", phone_locator.count())

    # Let's find all category buttons around or inside the phone
    cats = page.locator("button, div[role='button']").all()
    for c in cats:
        t = c.inner_text().strip()
        if "실비" in t or "실손" in t:
            print("Found category:", t)
            c.click()
            page.wait_for_timeout(1000)

    # Let's find the phone container element
    phone_el = page.evaluate('''() => {
        // Find the element containing the phone mockup
        const els = Array.from(document.querySelectorAll('div'));
        for (const el of els) {
            if (el.innerText.includes('14:33') && el.innerText.includes('5G') && el.clientWidth > 300 && el.clientWidth < 600) {
                return {
                    class: el.className,
                    width: el.clientWidth,
                    height: el.clientHeight,
                    rect: el.getBoundingClientRect()
                };
            }
        }
        return null;
    }''')
    print("Phone element:", phone_el)

    # Hide floating planner popup
    page.evaluate('''() => {
        document.querySelectorAll('[class*="planner"], [class*="Planner"], [class*="counsel"]').forEach(e => e.remove());
    }''')

    # Take high-res screenshot of the phone element
    phone = page.locator("div:has-text('14:33')").last
    # Save direct phone screenshot
    phone.screenshot(path="brands/insurance/assets/real_phone_widget.png")
    print("Saved real_phone_widget.png")

    browser.close()
