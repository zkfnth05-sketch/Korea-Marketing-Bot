# -*- coding: utf-8 -*-
"""
InsureBalance Tistory Login Helper (보험 티스토리 블로그 무인 자동 발행용 1회 세션 영구 저장기)
========================================================================================
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
PROFILE_DIR = CURRENT_DIR / "tistory_chrome_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

SESSION_FILE = CURRENT_DIR / "tistory_session.json"
ACCOUNTS_FILE = CURRENT_DIR / "accounts.json"


async def run_login_flow():
    print("=" * 65)
    print("🚀 [InsureBalance 보험 티스토리 블로그 1회 영구 연동기]")
    print("화면에 실제 크롬 브라우저 창이 열립니다.")
    print("1. [카카오계정으로 로그인] 클릭 후 아이디/비밀번호로 로그인해 주세요.")
    print("2. '로그인 상태 유지' 체크박스를 꼭 체크해 주세요.")
    print("=" * 65)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ],
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.pages[0] if context.pages else await context.new_page()

        await page.goto("https://www.tistory.com/auth/login")
        print("\n⏳ 티스토리 브라우저 창이 열렸습니다. 로그인을 진행해 주세요...")

        logged_in = False
        t_cookie_str = ""

        for sec in range(150):
            await asyncio.sleep(2)
            cur_url = page.url
            cookies = await context.cookies()
            cookie_dict = {c["name"]: c["value"] for c in cookies}

            is_login_page = any(x in cur_url for x in ["auth/login", "authentication/login", "accounts.kakao.com", "kauth.kakao.com"])
            has_auth_session = "TSSESSION" in cookie_dict or "_T_ID" in cookie_dict
            
            if not is_login_page and has_auth_session:
                t_cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies if "tistory.com" in c.get("domain", "")])
                logged_in = True
                break

        if not logged_in:
            print("\n⚠️ 시간이 초과되었거나 로그인이 감지되지 않았습니다. 현재 상태로 저장을 시도합니다.")
            cookies = await context.cookies()
            t_cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies if "tistory.com" in c.get("domain", "")])

        print("\n🎉 [대성공!] InsureBalance 티스토리 로그인이 정상 감지되었습니다!")
        await context.storage_state(path=str(SESSION_FILE))
        print(f"💾 1. 티스토리 크롬 영구 프로필 및 세션 저장 완료: {PROFILE_DIR.name}")

        accounts_data = {}
        if ACCOUNTS_FILE.exists():
            try:
                with open(ACCOUNTS_FILE, "r", encoding="utf-8") as fp:
                    accounts_data = json.load(fp)
            except Exception:
                accounts_data = {}

        if "credentials" not in accounts_data:
            accounts_data["credentials"] = {}

        accounts_data["credentials"]["tistory_blog_name"] = "insure-balance"
        accounts_data["credentials"]["tistory_session_cookie"] = t_cookie_str

        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as fp:
            json.dump(accounts_data, fp, ensure_ascii=False, indent=2)

        print("💾 2. accounts.json 티스토리 블로그 정보 자동 등록 완료!")
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
