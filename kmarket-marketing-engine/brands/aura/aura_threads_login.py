# -*- coding: utf-8 -*-
"""
Aura Threads Login Helper (💖 Aura 스레드 1회 영구 로그인 연동기 - Playwright 완벽 감지)
=====================================================================================
- 브랜드: 💖 Aura (AI 데이팅)
- 전용 계정: @aura_ai_dating
- 프로필 디렉터리: brands/aura/meta_chrome_profile/
- 세션 파일: brands/aura/threads_session.json
- 역할:
  1. 실제 독립 브라우저 창을 화면에 띄움 (headless=False)
  2. 스레드(threads.net/login) 로그인 페이지로 연결
  3. 사용자가 아이디/비번 또는 Continue with Instagram으로 로그인 수행
  4. 메인 피드 진입이 완벽히 확인될 때까지 대기
  5. 로그인 성공 시 meta_chrome_profile 및 threads_session.json 영구 보존 후 자동 종료
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from playwright.async_api import async_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("AuraThreadsLogin")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
PROFILE_DIR = CURRENT_DIR / "meta_chrome_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)
SESSION_FILE = CURRENT_DIR / "threads_session.json"
ACCOUNTS_FILE = CURRENT_DIR / "accounts.json"


async def run_threads_login_flow():
    print("\n" + "=" * 70)
    print("🔑 [💖 Aura AI 데이팅] 스레드(Threads) 영구 로그인 1회 연동기")
    print(f"👉 전용 계정: [ @aura_ai_dating ]")
    print(f"👉 영구 프로필: {PROFILE_DIR.name}")
    print("=" * 70)
    print("1. 화면에 스레드 전용 브라우저 창이 열립니다.")
    print("2. 인스타그램 @aura_ai_dating 계정으로 로그인을 완료해 주세요.")
    print("   (아이디/비번 직접 입력 또는 아래 'Continue with Instagram' 클릭)")
    print("3. 메인 피드(홈 화면)가 정상 표시되면 봇이 자동 감지하여 영구 저장 후 창을 닫습니다.")
    print("=" * 70 + "\n")

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check"
            ],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900}
        )
        page = context.pages[0] if context.pages else await context.new_page()

        # 스레드 로그인 페이지로 이동
        await page.goto("https://www.threads.net/login", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)
        
        # 'Continue with Instagram' 버튼이 있으면 자동으로 클릭하여 로그인 화면으로 유도
        try:
            continue_btn = await page.query_selector("div:has-text('Continue with Instagram'), button:has-text('Continue with Instagram')")
            if continue_btn:
                print("👉 'Continue with Instagram' 버튼 자동 클릭...")
                await continue_btn.click()
        except Exception:
            pass

        print("⏳ 스레드 로그인 대기 중... (열린 창에서 로그인을 진행해 주세요)")

        logged_in = False
        for i in range(120):  # 120 * 2초 = 240초 (4분 대기)
            await asyncio.sleep(2)
            
            curr_url = page.url.lower()
            
            # 1. 로그인 폼이나 모달이 여전히 떠있는지 확인
            login_form = await page.query_selector("input[type='password'], button:has-text('Log in'), div:has-text('Say more with Threads')")
            
            # 2. 피드 및 네비게이션 요소 확인
            nav_element = await page.query_selector("svg[aria-label='Create'], svg[aria-label='새 스레드'], svg[aria-label='Home'], svg[aria-label='홈'], a[href*='/@'], div[role='button'][aria-label*='새']")
            
            # 3. 로그인 성공 판정 (URL이 login이 아니고, 비밀번호 폼이 없으며, 네비게이션이 활성화됨)
            if "login" not in curr_url and not login_form and nav_element:
                logged_in = True
                break

        if not logged_in:
            print("\n⚠️ 4분 동안 로그인이 완료되지 않았거나 창이 닫혔습니다. 다시 시도해 주세요.")
            try:
                await context.close()
            except Exception:
                pass
            return False

        print("\n🎉 [대성공!] Aura 스레드 피드 진입 및 로그인이 정상 확인되었습니다!")

        # 1. storage_state 영구 저장
        await context.storage_state(path=str(SESSION_FILE))
        print(f"💾 1. 영구 프로필 및 {SESSION_FILE.name} 세션 동기화 완료")

        # 1-1. 검증 플래그 영구 생성 및 에러 스크린샷 정리
        vfile = CURRENT_DIR / "threads_session_verified.json"
        with open(vfile, "w", encoding="utf-8") as vf:
            json.dump({"verified_at": "2026-10-09", "brand": "aura", "status": "authenticated"}, vf, indent=2)
        err_shot = CURRENT_DIR / "threads_error_screenshot.png"
        if err_shot.exists():
            try:
                err_shot.unlink()
            except Exception:
                pass
        print(f"💾 1-1. 실시간 관제판 연동 플래그(threads_session_verified.json) 활성화 완료")

        # 2. accounts.json 업데이트
        if ACCOUNTS_FILE.exists():
            try:
                with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                    acc = json.load(f)
                acc.setdefault("credentials", {})["threads_session_connected"] = True
                acc["credentials"]["threads_username"] = "aura_ai_dating"
                with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
                    json.dump(acc, f, ensure_ascii=False, indent=2)
                print(f"💾 2. accounts.json 연동 상태 업데이트 완료")
            except Exception as ex:
                logger.warning(f"accounts.json 업데이트 실패: {ex}")

        print("\n✨ 이제부터 Aura 마케팅봇이 스레드에 완전 무인으로 영구 자동 송출합니다!")
        print("창은 3초 후 자동으로 닫힙니다...\n")

        await asyncio.sleep(3)
        await context.close()
        return True


if __name__ == "__main__":
    success = asyncio.run(run_threads_login_flow())
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
