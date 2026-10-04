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

    # Click the orange 4세대 실손 button via Javascript
    page.evaluate('''() => {
        const els = Array.from(document.querySelectorAll('*'));
        for (const el of els) {
            if (el.textContent.trim() === '4세대 실손' && el.children.length === 0) {
                el.click();
                if (el.parentElement) el.parentElement.click();
                break;
            }
        }
    }''')
    page.wait_for_timeout(2000)

    # Hide header logos and floating counselor popup
    page.evaluate('''() => {
        const toHide = document.querySelectorAll('header, nav, img[src*="incar"], img[src*="logo"], [class*="planner"], [class*="Planner"], [class*="counsel"], [class*="floating"]');
        toHide.forEach(h => h.style.display = 'none');
    }''')

    page.screenshot(path="brands/insurance/real_4th_after_js_click.png")
    print("Saved real_4th_after_js_click.png")

    # Scroll down 600px
    page.evaluate("window.scrollBy(0, 600)")
    page.wait_for_timeout(1000)
    page.screenshot(path="brands/insurance/real_4th_scroll1.png")

    # Scroll down another 600px
    page.evaluate("window.scrollBy(0, 600)")
    page.wait_for_timeout(1000)
    page.screenshot(path="brands/insurance/real_4th_scroll2.png")

    browser.close()
