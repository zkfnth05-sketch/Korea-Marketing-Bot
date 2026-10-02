# -*- coding: utf-8 -*-
"""
Insurance 전용 유튜브(Google/YouTube) 영구 브라우저 프로필 1회 생성 도구
========================================================================================
- 브랜드: 🛡️ 보험 리밸런스 (골드맘)
- 전용 계정: 보험 리밸런스 공식 채널 계정
- 프로필 경로: brands/insurance/youtube_chrome_profile/
- 설명: 단 1회 로그인하면 브라우저 쿠키/인증토큰/스토리지가 디스크에 영구 저장되어
       이후 24시간 무인 가동 시 유튜브 쇼츠 피드 탐색 및 실제 '좋아요(Like)'를 자동 실행합니다.
- 원칙: Rule 1 (앱별 완전 독립 모듈화), Rule 6 (무인 자율 구동)
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
PROFILE_DIR = CURRENT_DIR / "youtube_chrome_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)
SESSION_JSON = CURRENT_DIR / "youtube_session.json"


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
    print("🔑 [🛡️ 보험 리밸런스] 유튜브(Google/YouTube) 영구 브라우저 프로필 1회 세팅 도구")
    print("=" * 70)
    print(f"👉 보험 리밸런스 전용 유튜브 채널(Google 계정) 로그인")
    print(f"👉 프로필 저장 위치: {PROFILE_DIR}")
    print("-" * 70)
    print("1. 실제 크롬 브라우저가 전용 영구 프로필 모드로 실행됩니다.")
    print("2. 구글 계정으로 로그인해 주시고, 유튜브 홈 화면이 뜨는지 확인해 주세요.")
    print("3. 로그인이 완료되면 브라우저 창 우측 상단의 [X]를 눌러 닫아주시면 영구 저장이 완료됩니다.")
    print("=" * 70 + "\n")

    chrome_exe = find_chrome_path()
    print(f"🚀 실제 브라우저 실행 중... ({chrome_exe})")

    login_url = "https://accounts.google.com/ServiceLogin?service=youtube&continue=https%3A%2F%2Fwww.youtube.com%2F"

    cmd = [
        chrome_exe,
        f"--user-data-dir={PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        login_url
    ]

    subprocess.run(cmd)

    print("\n✅ 브라우저가 닫혔습니다. 영구 유튜브 쿠키 동기화 중...")

    # Playwright로 쿠키 추출하여 youtube_session.json 동기화
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=True
            )
            cookies = context.cookies()
            clean_cookies = []
            for c in cookies:
                c_item = {
                    "name": c.get("name"),
                    "value": c.get("value"),
                    "domain": c.get("domain", ".youtube.com"),
                    "path": c.get("path", "/")
                }
                if "sameSite" in c and c["sameSite"] in ["Strict", "Lax", "None"]:
                    c_item["sameSite"] = c["sameSite"]
                if c.get("name", "").startswith(("__Secure-", "__Host-")) or c.get("secure"):
                    c_item["secure"] = True
                clean_cookies.append(c_item)

            with open(SESSION_JSON, "w", encoding="utf-8") as f:
                json.dump({"cookies": clean_cookies}, f, ensure_ascii=False, indent=2)
            context.close()

        has_login = any(c.get("name") in ["LOGIN_INFO", "SID", "SSID", "SAPISID"] for c in clean_cookies)
        print(f"🎉 [성공] 총 {len(clean_cookies)}개의 유튜브 쿠키가 영구 보관함에 완벽하게 동기화되었습니다!")
        if has_login:
            print("✅ [검증 통과] 구글/유튜브 인증 토큰(SID/LOGIN_INFO)이 정상 감지되었습니다.")
        else:
            print("⚠️ [안내] 로그인 토큰이 감지되지 않았습니다. 로그인이 정상 완료되었는지 확인해 주세요.")
        print("💡 이제 봇이 유튜브 쇼츠 탐색 중 실제 내 계정으로 피드 시청 및 '좋아요'를 누르며 계정 지수를 올립니다.\n")
    except Exception as ex:
        print(f"⚠️ 쿠키 동기화 안내: {ex} (프로필 디스크 저장은 완료되었습니다)")


if __name__ == "__main__":
    main()
