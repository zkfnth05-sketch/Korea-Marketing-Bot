# -*- coding: utf-8 -*-
"""
Insurance Threads Cookie Importer (🛡️ 보험 리밸런스 스레드 Cookie-Editor 연동기)
=============================================================================
- 브랜드: 🛡️ 보험 리밸런스 (InsureBalance)
- 전용 계정: @goldmomofficial
- 쿠키 파일: brands/insurance/threads_cookies.json
- 프로필 디렉터리: brands/insurance/meta_chrome_profile/
- 세션 파일: brands/insurance/threads_session.json
- 역할:
  1. Cookie-Editor 확장 프로그램에서 익스포트한 JSON 쿠키를 읽어 세척 및 도메인 정규화
  2. meta_chrome_profile 브라우저 컨텍스트에 주입
  3. 스레드(threads.net) 접속 후 @goldmomofficial 로그인 세션 검증
  4. threads_session.json 및 accounts.json 상태를 영구 저장
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

logger = logging.getLogger("InsuranceThreadsCookieImporter")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_DIR = Path(__file__).resolve().parent
COOKIE_FILE = BASE_DIR / "threads_cookies.json"
PROFILE_DIR = BASE_DIR / "meta_chrome_profile"
SESSION_FILE = BASE_DIR / "threads_session.json"
ACCOUNTS_FILE = BASE_DIR / "accounts.json"
PROOF_SCREENSHOT = BASE_DIR / "threads_live_logged_in.png"


async def inject_and_verify():
    print("\n" + "=" * 70)
    print("🍪 [🛡️ 보험 리밸런스] 스레드(Threads) Cookie-Editor 자동 연동기")
    print(f"👉 전용 계정: [ @goldmomofficial ]")
    print(f"👉 대상 쿠키: {COOKIE_FILE.name}")
    print("=" * 70)

    if not COOKIE_FILE.exists():
        print(f"\n❌ [오류] 쿠키 파일을 찾을 수 없습니다: {COOKIE_FILE}")
        print("👉 threads_cookies.json 파일에 Cookie-Editor JSON 내용을 붙여넣어 주세요.")
        return False

    try:
        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            raw_cookies = json.load(f)
    except Exception as e:
        print(f"\n❌ [오류] 쿠키 파일 JSON 파싱 실패: {e}")
        return False

    if not isinstance(raw_cookies, list) or len(raw_cookies) == 0:
        print("\n❌ [오류] 쿠키 데이터가 비어있거나 올바른 리스트 형식이 아닙니다.")
        return False

    pw_cookies = []
    for c in raw_cookies:
        pw_c1 = {
            "name": c["name"],
            "value": c["value"],
            "domain": c.get("domain", ".threads.net"),
            "path": c.get("path", "/"),
            "secure": c.get("secure", True),
            "httpOnly": c.get("httpOnly", False),
        }
        same_site = c.get("sameSite")
        if same_site in ["Strict", "Lax", "None"]:
            pw_c1["sameSite"] = same_site
        elif same_site == "no_restriction":
            pw_c1["sameSite"] = "None"
        elif same_site == "lax":
            pw_c1["sameSite"] = "Lax"

        pw_cookies.append(pw_c1)

        # Duplicate for .threads.net and .instagram.com if not already
        if not pw_c1["domain"].endswith("threads.net"):
            pw_c2 = dict(pw_c1)
            pw_c2["domain"] = ".threads.net"
            pw_cookies.append(pw_c2)

        if not pw_c1["domain"].endswith("instagram.com"):
            pw_c3 = dict(pw_c1)
            pw_c3["domain"] = ".instagram.com"
            pw_cookies.append(pw_c3)

    print(f"1. 총 {len(pw_cookies)}개의 쿠키 정규화 준비 완료.")

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check"
            ],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )

        await context.add_cookies(pw_cookies)
        print("2. 브라우저 컨텍스트에 쿠키 주입 완료.")

        page = context.pages[0] if context.pages else await context.new_page()

        print("3. 스레드(https://www.threads.com/) 접속 및 세션 검증 중...")
        await page.goto("https://www.threads.com/", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(4)

        # 하단 배너 제거 및 Continue with Instagram 클릭
        try:
            await page.evaluate("""() => {
                const fixedOverlays = Array.from(document.querySelectorAll("div")).filter(d => {
                    const style = window.getComputedStyle(d);
                    return (style.position === 'fixed' || style.position === 'sticky') && style.bottom === '0px' && d.innerText && d.innerText.includes('Terms');
                });
                fixedOverlays.forEach(b => b.remove());
            }""")
            await asyncio.sleep(1)

            clicked = await page.evaluate("""() => {
                const all = Array.from(document.querySelectorAll("button, div[role='button'], a, div"));
                const cont = all.find(el => el.innerText && (el.innerText.trim().includes('Continue with Instagram') || el.innerText.trim().includes('goldmomofficial')));
                if (cont) {
                    const clickable = cont.closest("button, div[role='button'], a") || cont;
                    clickable.click();
                    return true;
                }
                return false;
            }""")
            if clicked:
                print("👉 'Continue with Instagram' 버튼 클릭, 세션 연결 대기...")
                await asyncio.sleep(8)
        except Exception as me:
            print(f"모달 클릭 예외: {me}")

        curr_url = page.url
        print(f"   현재 페이지 URL: {curr_url}")

        await page.screenshot(path=str(PROOF_SCREENSHOT))
        print(f"4. 로그인 검증 스크린샷 저장 완료: {PROOF_SCREENSHOT.name}")

        create_btn = await page.query_selector("svg[aria-label='Create'], svg[aria-label='새 스레드'], div[role='button'][aria-label*='새'], a[href*='/@goldmomofficial'], a[href*='/@me'], svg[aria-label='Home'], svg[aria-label='홈']")
        login_modal = await page.query_selector("div:has-text('Continue with Instagram'), button:has-text('Log in with Instagram')")

        if create_btn or ("login" not in curr_url.lower() and not login_modal):
            print("\n🎉 [대성공!] 🛡️ 보험 리밸런스 (@goldmomofficial) 스레드 로그인 세션 연동 완료!")
            await context.storage_state(path=str(SESSION_FILE))
            print(f"💾 1. 영구 세션 파일 저장 완료: {SESSION_FILE.name}")

            if ACCOUNTS_FILE.exists():
                try:
                    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                        acc = json.load(f)
                    acc.setdefault("credentials", {})["threads_session_connected"] = True
                    acc["credentials"]["threads_username"] = "goldmomofficial"
                    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
                        json.dump(acc, f, ensure_ascii=False, indent=2)
                    print("💾 2. accounts.json 연동 상태 업데이트 완료")
                except Exception as ex:
                    logger.warning(f"accounts.json 업데이트 실패: {ex}")

            await context.close()
            return True
        else:
            print("\n⚠️ 스레드 로그인 상태가 확인되지 않았습니다. 쿠키가 만료되었거나 올바르지 않은지 확인해 주세요.")
            await context.close()
            return False


if __name__ == "__main__":
    success = asyncio.run(inject_and_verify())
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
