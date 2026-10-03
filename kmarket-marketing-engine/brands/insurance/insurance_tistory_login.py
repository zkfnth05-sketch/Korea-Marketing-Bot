# -*- coding: utf-8 -*-
"""
InsureBalance Tistory Login Helper (실제 크롬 브라우저 1회 영구 로그인 도구)
=============================================================================
- 브랜드: 🛡️ 보험 리밸런스 (InsureBalance)
- 프로필 경로: brands/insurance/tistory_chrome_profile/
- 역할: 실제 크롬 브라우저 창을 띄워 티스토리 카카오 로그인을 수행하고 영구 보존합니다.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
PROFILE_DIR = CURRENT_DIR / "tistory_chrome_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)
SESSION_FILE = CURRENT_DIR / "tistory_session.json"
ACCOUNTS_FILE = CURRENT_DIR / "accounts.json"


def find_chrome_path():
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return "chrome.exe"


def main():
    print("\n" + "=" * 70)
    print("🔑 [🛡️ 보험 리밸런스] 티스토리 블로그 영구 브라우저 1회 로그인 도구")
    print("=" * 70)
    print(f"👉 프로필 저장 위치: {PROFILE_DIR}")
    print("-" * 70)
    print("1. 실제 크롬 브라우저가 화면에 바로 실행됩니다.")
    print("2. 카카오 계정으로 티스토리에 로그인해 주세요.")
    print("   ★ [로그인 상태 유지] 및 [이 기기에서 2단계 인증 건너뛰기]를 꼭 체크하세요!")
    print("3. 로그인이 완료되어 티스토리 메인/블로그 화면이 정상적으로 뜨면,")
    print("4. 브라우저 창 우측 상단의 [X]를 눌러 닫아주시면 영구 세션이 자동 저장됩니다.")
    print("=" * 70 + "\n")

    chrome_exe = find_chrome_path()
    print(f"🚀 실제 크롬 브라우저 실행 중... ({chrome_exe})")

    # Clean locks
    for f in ["SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile"]:
        p = PROFILE_DIR / f
        if p.exists():
            try:
                p.unlink()
            except Exception:
                pass

    cmd = [
        chrome_exe,
        f"--user-data-dir={PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        "--start-maximized",
        "https://www.tistory.com/auth/login"
    ]

    subprocess.run(cmd)

    print("\n✅ 브라우저가 닫혔습니다. 영구 쿠키 및 세션 동기화 중...")

    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=True,
                args=["--disable-blink-features=AutomationControlled"]
            )
            cookies = context.cookies()
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump({"cookies": cookies}, f, ensure_ascii=False, indent=2)

            t_cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies if "tistory.com" in c.get("domain", "")])
            
            # 블로그 관리자 접근 테스트
            page = context.new_page()
            detected_blog_name = "insure-balance"
            try:
                page.goto("https://www.tistory.com/member/blog", timeout=10000)
                bl_elem = page.query_selector("a.link_blog, a.link_tit, .item_blog a")
                if bl_elem:
                    href = bl_elem.get_attribute("href")
                    if href and ".tistory.com" in href:
                        import re
                        m = re.search(r"https?://([^.]+)\.tistory\.com", href)
                        if m:
                            detected_blog_name = m.group(1)
            except Exception:
                pass

            context.close()

        print(f"🎉 [성공] 총 {len(cookies)}개의 최신 티스토리 쿠키가 영구 보관함에 완벽하게 동기화되었습니다!")
        
        # accounts.json 갱신
        accounts_data = {}
        if ACCOUNTS_FILE.exists():
            try:
                with open(ACCOUNTS_FILE, "r", encoding="utf-8") as fp:
                    accounts_data = json.load(fp)
            except Exception:
                accounts_data = {}

        if "credentials" not in accounts_data:
            accounts_data["credentials"] = {}

        accounts_data["credentials"]["tistory_blog_name"] = detected_blog_name
        accounts_data["credentials"]["tistory_session_cookie"] = t_cookie_str

        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as fp:
            json.dump(accounts_data, fp, ensure_ascii=False, indent=2)

        print(f"💾 accounts.json 티스토리 블로그 정보({detected_blog_name}) 등록 완료!\n")
    except Exception as ex:
        print(f"⚠️ 세션 동기화 안내: {ex} (프로필 디스크 저장은 완료되었습니다)")


if __name__ == "__main__":
    main()
