# -*- coding: utf-8 -*-
"""
Insurance(보험 리밸런스) 전용 인스타그램(Instagram) 영구 브라우저 프로필 1회 세팅 도구
========================================================================================
- 브랜드: 🛡️ 보험 리밸런스
- 전용 계정: @goldmomofficial
- 프로필 경로: brands/insurance/instagram_chrome_profile/
- 세션 파일: brands/insurance/instagram_session.json
========================================================================================
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine.browser_guard import clean_browser_profile_locks

PROFILE_DIR = CURRENT_DIR / "instagram_chrome_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)
SESSION_JSON = CURRENT_DIR / "instagram_session.json"


def find_chrome_executable() -> str:
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
    print("🔑 [🛡️ 보험 리밸런스] 인스타그램 1회 영구 로그인 셋업")
    print("=" * 70)
    print("👉 대상 브랜드: 🛡️ 보험 리밸런스")
    print("👉 대상 계정: @goldmomofficial")
    print(f"👉 프로필 저장 위치: {PROFILE_DIR}")
    print("-" * 70)
    print("1. 순수 크롬 브라우저가 화면에 열립니다 (의심 플래그 0%).")
    print("2. [goldmomofficial] 인스타그램 계정으로 로그인을 완료해 주세요.")
    print("3. 인스타그램 피드/홈 화면이 정상적으로 뜨면,")
    print("4. 크롬 창 우측 상단 [X]를 눌러 닫아주세요.")
    print("5. 닫히는 즉시 봇이 sessionid 등 영구 인증 토큰을 자동 추출하여 저장합니다.")
    print("=" * 70 + "\n")

    clean_browser_profile_locks(PROFILE_DIR)
    chrome_path = find_chrome_executable()
    login_url = "https://www.instagram.com/accounts/login/"

    print(f"🚀 순수 크롬 브라우저 실행 중... ({chrome_path})", flush=True)

    cmd = [
        chrome_path,
        f"--user-data-dir={PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        login_url
    ]

    subprocess.run(cmd)

    print("\n🌐 브라우저가 닫혔습니다. 인스타그램 영구 세션 쿠키 동기화 중...", flush=True)
    clean_browser_profile_locks(PROFILE_DIR)

    clean_cookies = []
    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=True
            )
            cookies = context.cookies()
            for c in cookies:
                item = {
                    "name": c.get("name"),
                    "value": c.get("value"),
                    "domain": c.get("domain", ".instagram.com"),
                    "path": c.get("path", "/")
                }
                if "sameSite" in c and c["sameSite"] in ["Strict", "Lax", "None"]:
                    item["sameSite"] = c["sameSite"]
                if c.get("name", "").startswith(("__Secure-", "__Host-")) or c.get("secure"):
                    item["secure"] = True
                if c.get("httpOnly"):
                    item["httpOnly"] = True
                clean_cookies.append(item)

            with open(SESSION_JSON, "w", encoding="utf-8") as f:
                json.dump({"cookies": clean_cookies}, f, ensure_ascii=False, indent=2)
            context.close()
    except Exception as ex:
        print(f"⚠️ 쿠키 동기화 안내: {ex} (프로필 디스크 저장은 완료되었습니다)")

    auth_tokens = [c["name"] for c in clean_cookies if c["name"] in ["sessionid", "ds_user_id", "csrftoken", "mid", "rur"]]
    print(f"\n📦 총 {len(clean_cookies)}개의 인스타그램 세션 쿠키 저장 완료!")
    print(f"🔑 발견된 핵심 인증 토큰: {set(auth_tokens)}")

    if any(k in auth_tokens for k in ["sessionid", "ds_user_id"]):
        print("\n🎉 [검증 통과] 보험 리밸런스 인스타그램 영구 인증 토큰 저장 성공!")
        print("👉 이제 릴스 게시 후 첫 댓글(랜딩 URL) 무인 등록이 100% 가능합니다.\n")
    else:
        print("\n⚠️ [안내] sessionid 토큰이 감지되지 않았습니다. 로그인이 정상 완료되었는지 확인 후 다시 실행해 주세요.\n")


if __name__ == "__main__":
    main()
