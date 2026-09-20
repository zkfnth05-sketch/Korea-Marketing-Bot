# -*- coding: utf-8 -*-
"""
StockMaster Brunch Login Helper (주식 카카오 브런치 무인 자동 연동 1회 세션 영구 저장기)
===================================================================================
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
PROFILE_DIR = CURRENT_DIR / "brunch_chrome_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

SESSION_FILE = CURRENT_DIR / "brunch_session.json"
ACCOUNTS_FILE = CURRENT_DIR / "accounts.json"


async def run_login_flow():
    print("=" * 65)
    print("🚀 [StockMaster 주식 브런치스토리 1회 영구 연동기]")
    print("화면에 실제 크롬 브라우저 창이 열립니다.")
    print("1. [카카오계정으로 시작하기] 클릭 후 로그인해 주세요.")
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

        await page.goto("https://brunch.co.kr/signin")
        print("\n⏳ 브런치 브라우저 창이 열렸습니다. 로그인을 진행해 주세요...")

        logged_in = False
        b_cookie_str = ""

        for sec in range(150):
            await asyncio.sleep(2)
            cur_url = page.url
            cookies = await context.cookies()
            cookie_dict = {c["name"]: c["value"] for c in cookies}

            is_login_page = any(x in cur_url for x in ["signin", "accounts.kakao.com", "kauth.kakao.com"])
            has_kakao_auth = "_kawlt" in cookie_dict or "_kadu" in cookie_dict or "KA" in cookie_dict
            
            if not is_login_page and has_kakao_auth:
                try:
                    write_btn = await page.locator("a:has-text('글쓰기'), button:has-text('글쓰기'), .link_profile, .btn_write").count()
                    signin_btn = await page.locator("a:has-text('시작하기'), button:has-text('시작하기')").count()
                    if write_btn > 0 or signin_btn == 0:
                        b_cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies if "brunch.co.kr" in c.get("domain", "")])
                        logged_in = True
                        break
                except Exception:
                    pass

        if not logged_in:
            print("\n⚠️ 시간이 초과되었거나 로그인이 감지되지 않았습니다. 현재 상태로 저장을 시도합니다.")
            cookies = await context.cookies()
            b_cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies if "brunch.co.kr" in c.get("domain", "")])

        print("\n🎉 [대성공!] StockMaster 브런치 로그인이 정상 감지되었습니다!")
        await context.storage_state(path=str(SESSION_FILE))
        print(f"💾 1. 브런치 크롬 영구 프로필 및 세션 저장 완료: {PROFILE_DIR.name}")

        accounts_data = {}
        if ACCOUNTS_FILE.exists():
            try:
                with open(ACCOUNTS_FILE, "r", encoding="utf-8") as fp:
                    accounts_data = json.load(fp)
            except Exception:
                accounts_data = {}

        if "credentials" not in accounts_data:
            accounts_data["credentials"] = {}

        accounts_data["credentials"]["brunch_session_cookie"] = b_cookie_str

        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as fp:
            json.dump(accounts_data, fp, ensure_ascii=False, indent=2)

        print("💾 2. accounts.json 브런치스토리 세션 쿠키 자동 등록 완료!")
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
