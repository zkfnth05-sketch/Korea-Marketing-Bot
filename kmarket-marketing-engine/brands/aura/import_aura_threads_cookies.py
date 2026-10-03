# -*- coding: utf-8 -*-
import json
import sys
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

async def inject_and_verify():
    base_dir = Path(r"c:\Users\zkfnt\Desktop\한국 마케팅봇\kmarket-marketing-engine\brands\aura")
    cookie_file = base_dir / "threads_cookies.json"
    profile_dir = base_dir / "meta_chrome_profile"
    session_file = base_dir / "threads_session.json"
    
    if not cookie_file.exists():
        print(f"❌ {cookie_file} not found!")
        return
        
    with open(cookie_file, "r", encoding="utf-8") as f:
        raw_cookies = json.load(f)
        
    pw_cookies = []
    for c in raw_cookies:
        # Create cookie for .threads.com
        pw_c1 = {
            "name": c["name"],
            "value": c["value"],
            "domain": c["domain"],
            "path": c.get("path", "/"),
            "secure": c.get("secure", True),
            "httpOnly": c.get("httpOnly", False),
        }
        if c.get("sameSite") in ["Strict", "Lax", "None"]:
            pw_c1["sameSite"] = c["sameSite"]
        elif c.get("sameSite") == "no_restriction":
            pw_c1["sameSite"] = "None"
        elif c.get("sameSite") == "lax":
            pw_c1["sameSite"] = "Lax"
        pw_cookies.append(pw_c1)
        
        # Also duplicate for .threads.net and .instagram.com
        pw_c2 = dict(pw_c1)
        pw_c2["domain"] = ".threads.net"
        pw_cookies.append(pw_c2)
        
        pw_c3 = dict(pw_c1)
        pw_c3["domain"] = ".instagram.com"
        pw_cookies.append(pw_c3)

    print(f"1. Prepared {len(pw_cookies)} cookies for injection.")

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        
        # Inject cookies
        await context.add_cookies(pw_cookies)
        print("2. Injected cookies into context.")
        
        page = context.pages[0] if context.pages else await context.new_page()
        
        # Navigate to Threads
        print("3. Navigating to Threads...")
        await page.goto("https://www.threads.net/", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(5)
        
        print(f"   Page URL: {page.url}")
        proof_path = base_dir / "threads_live_logged_in.png"
        await page.screenshot(path=str(proof_path))
        print(f"4. Proof screenshot saved: {proof_path}")
        
        # Check login
        create_btn = await page.query_selector("svg[aria-label='Create'], svg[aria-label='새 스레드'], div[role='button'][aria-label*='새'], a[href*='/@aura_ai_dating'], a[href*='/@me']")
        login_modal = await page.query_selector("div:has-text('Continue with Instagram'), button:has-text('Log in with Instagram')")
        
        if create_btn or not login_modal:
            print("🎉 [대성공!] Aura Threads 로그인 세션 완벽 활성화 완료!")
            # Save storage state
            await context.storage_state(path=str(session_file))
            print(f"💾 storage_state 저장 완료: {session_file}")
        else:
            print("⚠️ 아직 추가 확인이 필요합니다.")
            
        await context.close()

if __name__ == "__main__":
    asyncio.run(inject_and_verify())
