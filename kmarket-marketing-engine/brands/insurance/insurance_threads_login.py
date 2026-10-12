# -*- coding: utf-8 -*-
"""
Insurance Threads Login Helper (보험 리밸런스 스레드 1회 영구 로그인 연동기 - 인스타그램 연동 지원)
=============================================================================================
- 브랜드: 보험 리밸런스 (InsureBalance)
- 전용 계정: @goldmomofficial
- 프로필 디렉토리: brands/insurance/meta_chrome_profile/
- 세션 파일: brands/insurance/threads_session.json
- 주요 개선점:
  1. 인스타그램 연동 로그인 특화 (Instagram Web SSO 지원)
  2. 넉넉한 15분(900초) 대기 시간 (스마트폰 2FA / 앱 승인 여유 보장)
  3. 로그인 완료 즉시 threads_session.json + 디스크 프로필 동시 영구 각인
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from playwright.async_api import async_playwright

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("InsuranceThreadsLogin")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
PROFILE_DIR = CURRENT_DIR / "meta_chrome_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)
SESSION_FILE = CURRENT_DIR / "threads_session.json"
ACCOUNTS_FILE = CURRENT_DIR / "accounts.json"


async def run_threads_login_flow():
    print("\n" + "=" * 75)
    print("🧵 [보험 리밸런스] 스레드(Threads) 1회 영구 로그인 연동기")
    print(f"📌 전용 계정: [ @goldmomofficial ]")
    print(f"📌 디스크 프로필: {PROFILE_DIR.name}")
    print("=" * 75)
    print("1. 화면에 스레드 전용 브라우저 창이 열립니다.")
    print("2. 스레드는 인스타그램(@goldmomofficial) 연동 계정이므로:")
    print("   - 화면의 'Continue with Instagram' (Instagram으로 계속)을 클릭하시거나,")
    print("   - 인스타그램 로그인 창에서 아이디/비번 또는 페이스북 연동으로 로그인해 주세요.")
    print("   - 스마트폰 인스타 앱 승인(2단계 인증)이 뜨면 폰에서 [승인]을 눌러주세요.")
    print("3. 스레드 메인 피드(홈 화면)가 열리면 봇이 자동으로 감지하여 영구 저장합니다.")
    print("   (최대 15분 동안 대기하므로 천천히 여유 있게 진행하시면 됩니다)")
    print("=" * 75 + "\n")

    # 브라우저 충돌 방지 락 정리
    for fname in ["SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile"]:
        lp = PROFILE_DIR / fname
        if lp.exists():
            try:
                lp.unlink()
            except Exception:
                pass

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check",
                "--start-maximized"
            ],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900}
        )
        page = context.pages[0] if context.pages else await context.new_page()

        # 스레드 로그인 페이지 진입
        await page.goto("https://www.threads.net/login", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(2.0)

        # 'Continue with Instagram' 버튼 자동 클릭 시도 (사용자 편의)
        try:
            continue_btn = await page.query_selector(
                "div:has-text('Continue with Instagram'), button:has-text('Continue with Instagram'), div:has-text('Instagram으로 계속'), button:has-text('Instagram으로 계속')"
            )
            if continue_btn:
                print("🔘 'Continue with Instagram' 버튼 감지 -> 자동 클릭 실행...")
                await continue_btn.click()
        except Exception:
            pass

        print("⏳ 스레드 / 인스타그램 로그인 대기 중... (열린 창에서 로그인을 완료해 주세요)")

        logged_in = False
        # 최대 450회 * 2초 = 900초 (15분)
        for i in range(450):
            await asyncio.sleep(2.0)

            # 1. 🍪 스레드 도메인 전용 쿠키 판별 (인스타그램 쿠키만 있을 때는 절대 조기 종료하지 않음!)
            try:
                cookies = await context.cookies()
                threads_cookies = [
                    c for c in cookies 
                    if ("threads.net" in c.get("domain", "") or "threads.com" in c.get("domain", ""))
                ]
                t_names = {c.get("name") for c in threads_cookies}
                if "sessionid" in t_names and ("ds_user_id" in t_names or "mid" in t_names or "csrftoken" in t_names):
                    print("🎉 [스레드 쿠키 감지 성공] 스레드 전용 세션 토큰(threads sessionid)이 정상 발급되었습니다!")
                    logged_in = True
                    break
            except Exception:
                pass

            # 2. 🪟 사용자가 브라우저 창을 직접 닫았을 때 감지 (스레드 쿠키가 있을 때만 성공)
            pages_to_check = context.pages
            if not pages_to_check:
                print("ℹ️ 브라우저 창 닫힘 감지. 저장된 쿠키 및 세션을 정밀 검증합니다...")
                try:
                    cookies = await context.cookies()
                    threads_cookies = [
                        c for c in cookies 
                        if ("threads.net" in c.get("domain", "") or "threads.com" in c.get("domain", ""))
                    ]
                    t_names = {c.get("name") for c in threads_cookies}
                    if "sessionid" in t_names or "ds_user_id" in t_names:
                        print("🎉 [스레드 세션 보존 확인] 스레드 인증 쿠키가 정상 저장되어 연동을 완료합니다!")
                        logged_in = True
                        break
                    else:
                        print("⚠️ 스레드 메인 피드 도달 전에 창이 닫혔습니다. (인스타 로그인 완료 -> 스레드 전환 중단 감지)")
                except Exception:
                    pass
                break

            # 3. 🌐 화면 및 URL 기반 보조 감지 & 자동 브릿지 클릭
            for p_check in pages_to_check:
                try:
                    curr_url = p_check.url.lower()

                    # 인스타그램 로그인 완료 후 'Continue as ...' 또는 '계속' 버튼 자동 클릭 지원
                    if "threads.net" in curr_url or "threads.com" in curr_url:
                        btn_continue = await p_check.query_selector(
                            "button:has-text('Continue as'), button:has-text('계속'), div[role='button']:has-text('Continue'), div[role='button']:has-text('계속')"
                        )
                        if btn_continue:
                            try:
                                print("👉 스레드 연결 버튼('Continue / 계속') 자동 클릭 감지...")
                                await btn_continue.click()
                                await asyncio.sleep(2.0)
                            except Exception:
                                pass

                    # 메인 피드 진입 여부 검증
                    if ("threads.net" in curr_url or "threads.com" in curr_url) and "login" not in curr_url and "accounts" not in curr_url:
                        nav_el = await p_check.query_selector(
                            "svg[aria-label='Create'], svg[aria-label='새 스레드'], svg[aria-label='Home'], svg[aria-label='홈'], a[href*='/@'], div[role='button'][aria-label*='홈']"
                        )
                        feed_post = await p_check.query_selector("div[data-pressable-container='true'], article, div[data-testid='post-container']")

                        clean_url = curr_url.rstrip("/")
                        if nav_el or feed_post or clean_url in ["https://www.threads.net", "https://threads.net", "https://www.threads.com", "https://threads.com"]:
                            # 쿠키가 완전히 발급되도록 2초 여유 대기
                            await asyncio.sleep(2.0)
                            logged_in = True
                            page = p_check
                            break
                except Exception:
                    continue

            if logged_in:
                break

            if (i + 1) % 15 == 0:
                elapsed_min = (i + 1) * 2 // 60
                print(f"   ... 로그인 진행 중 ({elapsed_min}분 경과 / 15분 대기)")

        if not logged_in:
            print("\n⚠️ 15분 동안 로그인이 완료되지 않았거나 창이 닫혔습니다. 다시 시도해 주세요.")
            try:
                await context.close()
            except Exception:
                pass
            return False

        print("\n🎉 [대성공!] 보험 리밸런스 스레드(@goldmomofficial) 메인 피드 진입 및 로그인 확인 완료!")

        # storage_state 영구 저장
        await context.storage_state(path=str(SESSION_FILE))
        print(f"💾 1. 영구 프로필 및 {SESSION_FILE.name} 세션 동기화 완료")

        # 인증 플래그 생성
        vfile = CURRENT_DIR / "threads_session_verified.json"
        with open(vfile, "w", encoding="utf-8") as vf:
            json.dump({"verified_at": "2026-10-11", "brand": "insurance", "status": "authenticated"}, vf, indent=2)

        # 쿠키 파일 저장
        try:
            cookies = await context.cookies()
            with open(CURRENT_DIR / "threads_cookies.json", "w", encoding="utf-8") as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            print("💾 2. threads_cookies.json 영구 쿠키 파일 저장 완료")
        except Exception as ce:
            logger.warning(f"쿠키 파일 저장 경고: {ce}")

        # accounts.json 업데이트
        if ACCOUNTS_FILE.exists():
            try:
                with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                    acc = json.load(f)
                acc.setdefault("credentials", {})["threads_session_connected"] = True
                acc["credentials"]["threads_username"] = "goldmomofficial"
                with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
                    json.dump(acc, f, ensure_ascii=False, indent=2)
                print("💾 3. accounts.json 연동 상태 업데이트 완료")
            except Exception as ex:
                logger.warning(f"accounts.json 업데이트 경고: {ex}")

        print("\n🚀 이제부터 보험 리밸런스 마케팅봇이 스레드에 100% 완전 무인으로 영구 자동 송출합니다.")
        print("창은 3초 후 자동으로 닫힙니다...\n")

        await asyncio.sleep(3.0)
        await context.close()
        return True


if __name__ == "__main__":
    success = asyncio.run(run_threads_login_flow())
    if not success:
        sys.exit(1)
