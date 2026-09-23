# -*- coding: utf-8 -*-
"""
🛡️ InsureBalance Naver Login Helper (보험 전용 네이버 블로그 무인 자동 발행용 1회 세션 저장기)
========================================================================================
- 브랜드: 🛡️ InsureBalance (보험비교)
- 전용 계정: thefirst-life
- 프로필 디렉터리: brands/insurance/naver_browser_profile/
- 역할:
  1. 실제 크롬 브라우저 창을 화면에 띄움 (영구 프로필 모드)
  2. 대표님께서 QR코드 또는 아이디/비번으로 1회 정상 로그인 수행
  3. 로그인 완료 감지 시 naver_browser_profile, naver_session.json 및 accounts.json에 자동 영구 저장
  4. 이후 일상 보험 칼럼/지식iN 자동 발행 시 재로그인 불필요 (100% 무인 자동화)
"""

import os
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
PROFILE_DIR = CURRENT_DIR / "naver_browser_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)
SESSION_FILE = CURRENT_DIR / "naver_session.json"
ACCOUNTS_FILE = CURRENT_DIR / "accounts.json"


async def run_login_flow():
    print("=" * 70)
    print("🛡️ [InsureBalance 보험비교] 네이버 영구 로그인 1회 연동기")
    print(f"👉 전용 계정: [ thefirst-life ]")
    print(f"👉 영구 프로필: {PROFILE_DIR.name}")
    print("=" * 70)
    print("1. 화면에 네이버 로그인 창이 열립니다.")
    print("2. 스마트폰 네이버 앱의 [QR코드 로그인] 또는 [아이디/비번]으로 로그인해 주세요.")
    print("3. 로그인이 완료되면 봇이 자동으로 감지하여 영구 저장 후 3초 뒤 창을 닫습니다.")
    print("=" * 70)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--no-first-run",
                "--no-default-browser-check"
            ]
        )
        page = await context.new_page()

        await page.goto("https://nid.naver.com/nidlogin.login?url=https%3A%2F%2Fblog.naver.com")
        
        # 🔒 [영구 로그인 보존 설정] 로그인 상태 유지 자동 체크 및 IP보안 자동 해제
        try:
            stay_cb = await page.wait_for_selector("#loginStay", timeout=5000)
            if stay_cb and not await stay_cb.is_checked():
                label_stay = await page.query_selector("label[for='loginStay']")
                if label_stay:
                    await label_stay.click()
                else:
                    await stay_cb.check()
                print("🔒 [영구 설정] '로그인 상태 유지'(nvlong) 자동 체크 완료 (영구 토큰 발급)")

            ip_cb = await page.query_selector("#switchIP")
            if ip_cb and await ip_cb.is_checked():
                label_ip = await page.query_selector("label[for='switchIP']")
                if label_ip:
                    await label_ip.click()
                else:
                    await ip_cb.uncheck()
                print("🌐 [영구 설정] 'IP보안' 자동 해제 완료 (유동 IP 환경 세션 파기 원천 차단)")
        except Exception as e:
            print(f"⚠️ 영구 옵션 자동 세팅 안내: {e}")

        print("\n⏳ 네이버 로그인 대기 중... (로그인을 완료하시면 봇이 자동으로 감지합니다)")

        logged_in = False
        nid_aut = ""
        nid_ses = ""

        for _ in range(90):  # 180초 대기
            await asyncio.sleep(2)
            cookies = await context.cookies()
            cookie_dict = {c["name"]: c["value"] for c in cookies}

            if "NID_AUT" in cookie_dict and "NID_SES" in cookie_dict:
                nid_aut = cookie_dict["NID_AUT"]
                nid_ses = cookie_dict["NID_SES"]
                logged_in = True
                break

        if not logged_in:
            print("\n⚠️ 3분 동안 로그인이 완료되지 않아 연결이 취소되었습니다. 다시 실행해 주세요.")
            await context.close()
            return False

        print("\n🎉 [대성공!] InsureBalance 네이버 로그인이 정상 감지되었습니다!")

        # 1. 브라우저 스토리지 상태 및 세션 파일 영구 저장
        await context.storage_state(path=str(SESSION_FILE))
        print(f"💾 1. 영구 프로필 디렉터리 및 {SESSION_FILE.name} 동기화 완료")

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

        accounts_data["credentials"]["naver_blog_id"] = "thefirst-life"
        accounts_data["credentials"]["naver_session_cookie"] = f"NID_AUT={nid_aut}; NID_SES={nid_ses};"

        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as fp:
            json.dump(accounts_data, fp, ensure_ascii=False, indent=2)

        print(f"💾 2. accounts.json 네이버 계정(thefirst-life) 영구 등록 완료!")
        print("\n✨ 이제부터 InsureBalance 마케팅봇이 보험 절약 칼럼 및 지식iN에 완전 무인으로 영구 자동 활동합니다!")
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
