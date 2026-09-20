# -*- coding: utf-8 -*-
"""
Aura Naver Login Helper (네이버 블로그 무인 자동 발행용 1회 세션 영구 저장기)
=============================================================================
- 역할:
  1. 실제 크롬 브라우저 창을 화면에 띄움 (headless=False)
  2. 대표님께서 QR코드 또는 아이디/비번으로 1회 정상 로그인 수행
  3. 로그인 완료 감지 시 NID_AUT, NID_SES 및 브라우저 세션을 naver_session.json 및 accounts.json에 자동 영구 저장
  4. 이후 일상 자동 발행 시 재로그인 불필요 (무인 자동화)
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
SESSION_FILE = CURRENT_DIR / "naver_session.json"
ACCOUNTS_FILE = CURRENT_DIR / "accounts.json"


async def run_login_flow():
    print("=" * 60)
    print("🚀 [Aura 네이버 블로그 간편 연동기]")
    print("화면에 네이버 로그인 창이 열립니다.")
    print("스마트폰 네이버 앱의 [QR코드 로그인] 또는 [아이디/비번]으로 로그인해 주세요.")
    print("=" * 60)

    async with async_playwright() as p:
        # 화면에 보이는 브라우저 실행
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )
        context = await browser.new_context(
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # 네이버 로그인 페이지 접속
        await page.goto("https://nid.naver.com/nidlogin.login")
        print("\n⏳ 네이버 로그인 대기 중... (로그인을 완료하시면 봇이 자동으로 감지합니다)")

        # 로그인 완료 감지 루프 (최대 3분 대기)
        logged_in = False
        nid_aut = ""
        nid_ses = ""

        for _ in range(90):  # 90 * 2초 = 180초
            await asyncio.sleep(2)
            cookies = await context.cookies()
            cookie_dict = {c["name"]: c["value"] for c in cookies}

            if "NID_AUT" in cookie_dict and "NID_SES" in cookie_dict:
                # 로그인 완료 감지
                nid_aut = cookie_dict["NID_AUT"]
                nid_ses = cookie_dict["NID_SES"]
                logged_in = True
                break

        if not logged_in:
            print("\n⚠️ 3분 동안 로그인이 완료되지 않아 연결이 취소되었습니다. 다시 실행해 주세요.")
            await browser.close()
            return False

        print("\n🎉 [대성공!] 네이버 로그인이 정상 감지되었습니다!")

        # 1. 브라우저 스토리지 상태(세션) 파일 영구 저장
        await context.storage_state(path=str(SESSION_FILE))
        print(f"💾 1. 브라우저 세션 영구 저장 완료: {SESSION_FILE.name}")

        # 2. accounts.json 업데이트
        accounts_data = {}
        if ACCOUNTS_FILE.exists():
            try:
                with open(ACCOUNTS_FILE, "r", encoding="utf-8") as fp:
                    accounts_data = json.load(fp)
            except Exception:
                accounts_data = {}

        if "credentials" not in accounts_data:
            accounts_data["credentials"] = {}

        accounts_data["credentials"]["naver_blog_id"] = "zkfnth01"
        accounts_data["credentials"]["naver_session_cookie"] = f"NID_AUT={nid_aut}; NID_SES={nid_ses};"

        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as fp:
            json.dump(accounts_data, fp, ensure_ascii=False, indent=2)

        print(f"💾 2. accounts.json 네이버 계정(zkfnth01) 및 세션 쿠키 자동 등록 완료!")
        print("\n✨ 이제부터 마케팅봇이 네이버 블로그에 완전 무인으로 글을 자동 발행합니다!")
        print("창은 3초 후 자동으로 닫힙니다...")

        await asyncio.sleep(3)
        await browser.close()
        return True


if __name__ == "__main__":
    success = asyncio.run(run_login_flow())
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
