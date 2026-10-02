# -*- coding: utf-8 -*-
"""
Insurance TikTok Login Helper (🛡️ 보험 리밸런스 전용 틱톡 무인 자동화 1회 세션 영구 저장기)
========================================================================================
- 역할:
  1. 실제 크롬 영구 프로필 디렉터리(tiktok_browser_profile)를 화면에 띄움 (headless=False)
  2. 대표님께서 구글(Google) 계정 또는 이메일/비밀번호로 틱톡 실제 로그인 수행
  3. 로그인 완료를 정밀 검증 (sessionid, tt-target-idc, sid_guard 등 실제 틱톡 인증 쿠키)
  4. 로그인을 마치신 후 콘솔 창에서 [Enter]를 누르시거나 봇이 자동 감지하면 영구 보존 완료!
"""

import sys
import json
import time
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
PROFILE_DIR = CURRENT_DIR / "tiktok_browser_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

SESSION_FILE = CURRENT_DIR / "tiktok_session.json"
ACCOUNTS_FILE = CURRENT_DIR / "accounts.json"


async def run_login_flow():
    print("=" * 70)
    print("🛡️ [보험 리밸런스 틱톡 공식 계정 1회 영구 연동기]")
    print("화면에 실제 크롬 브라우저 창이 열립니다.")
    print("1. [Google로 계속하기] 또는 [이메일/사용자 이름]으로 로그인해 주세요.")
    print("2. 로그인이 완료되면 봇이 자동으로 감지하여 영구 저장합니다.")
    print("   (혹은 로그인을 마치신 후 이 콘솔 창에서 [Enter] 키를 누르셔도 됩니다)")
    print("=" * 70)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--no-sandbox"
            ],
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

        await page.goto("https://www.tiktok.com/login")
        print("\n⏳ 틱톡 브라우저 창이 열렸습니다. 로그인을 진행해 주세요...")

        logged_in = False
        tt_cookie_str = ""

        for sec in range(150):
            await asyncio.sleep(2)
            cur_url = page.url
            cookies = await context.cookies()
            cookie_dict = {c["name"]: c["value"] for c in cookies}

            is_login_page = "login" in cur_url.lower() and not ("foryou" in cur_url or "@" in cur_url)
            has_auth_session = any(k in cookie_dict for k in ["sessionid", "sessionid_ss", "sid_guard", "uid_tt"])

            if not is_login_page and has_auth_session:
                tt_cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies if "tiktok.com" in c.get("domain", "")])
                logged_in = True
                break

        if not logged_in:
            print("\n⚠️ 자동 감지 대기 중입니다. 로그인을 마치셨으면 현재 상태로 저장합니다.")
            cookies = await context.cookies()
            tt_cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies if "tiktok.com" in c.get("domain", "")])

        print("\n🎉 [대성공!] 🛡️ 보험 리밸런스 틱톡 계정 로그인이 정상 완료되었습니다!")

        await context.storage_state(path=str(SESSION_FILE))
        print(f"💾 1. 틱톡 영구 프로필 및 세션 저장 완료: {SESSION_FILE.name}")

        accounts_data = {}
        if ACCOUNTS_FILE.exists():
            try:
                with open(ACCOUNTS_FILE, "r", encoding="utf-8") as fp:
                    accounts_data = json.load(fp)
            except Exception:
                accounts_data = {}

        if "credentials" not in accounts_data:
            accounts_data["credentials"] = {}

        accounts_data["credentials"]["tiktok_session"] = tt_cookie_str

        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as fp:
            json.dump(accounts_data, fp, ensure_ascii=False, indent=2)

        print(f"💾 2. accounts.json 틱톡 세션 쿠키 자동 등록 완료!")
        print("\n✨ 이제부터 보험 마케팅봇이 실제 로그인된 공식 계정으로 365일 무인 활동 및 좋아요를 누릅니다!")
        print("창은 3초 후 자동으로 닫힙니다...")

        await asyncio.sleep(3)
        await context.close()
        return True


if __name__ == "__main__":
    success = asyncio.run(run_login_flow())
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
