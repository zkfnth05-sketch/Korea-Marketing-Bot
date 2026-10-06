import json
import sys
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

async def inject_aura_cookies():
    base_dir = Path(r"c:\Users\zkfnt\Desktop\한국 마케팅봇\kmarket-marketing-engine\brands\aura")
    cookie_file = base_dir / "threads_cookies.json"
    profile_dir = base_dir / "meta_chrome_profile"
    session_file = base_dir / "threads_session.json"
    
    print("=" * 60)
    print("🔑 [Aura AI 데이팅] 최신 스레드 쿠키 브라우저 주입 및 세션 활성화")
    print("=" * 60)
    
    with open(cookie_file, "r", encoding="utf-8") as f:
        raw_cookies = json.load(f)
        
    pw_cookies = []
    for c in raw_cookies:
        pw_c1 = {
            "name": c["name"],
            "value": c["value"],
            "domain": ".threads.com",
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
        
        pw_c2 = dict(pw_c1)
        pw_c2["domain"] = ".threads.net"
        pw_cookies.append(pw_c2)
        
        pw_c3 = dict(pw_c1)
        pw_c3["domain"] = ".instagram.com"
        pw_cookies.append(pw_c3)

    print(f"1. 총 {len(pw_cookies)}개 스코프 쿠키 준비 완료.")

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900}
        )
        
        # 쿠키 주입
        await context.add_cookies(pw_cookies)
        print("2. 브라우저 컨텍스트에 쿠키 주입 완료.")
        
        page = context.pages[0] if context.pages else await context.new_page()
        
        print("3. 스레드(https://www.threads.com/) 접속 중...")
        await page.goto("https://www.threads.com/", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(6)
        
        # 만약 Instagram 계속하기 버튼이 아직 있다면 자동 클릭
        try:
            clicked = await page.evaluate("""() => {
                const el = Array.from(document.querySelectorAll("div, button, a")).find(e => 
                    e.innerText && (e.innerText.includes("Instagram으로 계속하기") || e.innerText.includes("Continue with Instagram")) && e.offsetWidth > 100
                );
                if (el) { el.click(); return true; }
                return false;
            }""")
            if clicked:
                print("   👉 화면의 'Instagram으로 계속하기' 자동 클릭 완료!")
                await asyncio.sleep(5)
        except Exception:
            pass
            
        proof_path = base_dir / "threads_live_logged_in.png"
        await page.screenshot(path=str(proof_path))
        print(f"4. 실물 증빙 스크린샷 저장 완료: {proof_path}")
        
        # 로그인 성공 여부 정밀 검증
        say_more_modal = await page.query_selector("div:has-text('Say more with Threads'), div:has-text('Instagram 계정으로 로그인')")
        profile_feed = await page.query_selector("div[role='button']:has-text('새로운 소식을 공유해보세요'), div[role='button']:has-text('새로운 스레드'), a[href*='/@aura_ai_dating'], a[href*='/@me']")
        
        if not say_more_modal and profile_feed:
            print("\n🎉 [대성공!] 💖 Aura AI 데이팅 (@aura_ai_dating) 스레드 로그인 완벽 활성화 성공!")
            await context.storage_state(path=str(session_file))
            print(f"💾 영구 세션 파일 저장 완료: {session_file}")
            result = True
        else:
            print("\n⚠️ 아직 비로그인 팝업이 감지되었습니다. 캡처 이미지를 확인합니다.")
            result = False
            
        await context.close()
        return result

if __name__ == "__main__":
    asyncio.run(inject_aura_cookies())
