# -*- coding: utf-8 -*-
"""
Aura 전용 네이버 영구 브라우저 프로필 1회 생성 도구
========================================================================================
- 브랜드: 💖 Aura (AI 데이팅)
- 전용 계정: zkfnth01
- 프로필 경로: brands/aura/naver_browser_profile/
- 설명: 단 1회 로그인하면 브라우저 쿠키/인증토큰/스토리지가 디스크에 영구 저장되어
       이후 24시간 무인 가동 시 영구히 자동 로그인 상태를 유지합니다.
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
PROFILE_DIR = CURRENT_DIR / "naver_browser_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)
SESSION_JSON = CURRENT_DIR / "naver_session.json"


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
    print("🔑 [💖 Aura 데이팅] 네이버 영구 브라우저 프로필 1회 세팅 도구")
    print("=" * 70)
    print(f"👉 Aura 전용 계정: [ zkfnth01 ]")
    print(f"👉 저장 위치: {PROFILE_DIR}")
    print("-" * 70)
    print("1. 실제 크롬 브라우저가 전용 영구 프로필 모드로 실행됩니다.")
    print("2. 네이버 로그인 화면에서 [zkfnth01] 계정으로 로그인해 주세요.")
    print("3. 로그인 후 네이버 메인 또는 지식iN 페이지가 정상적으로 뜨면,")
    print("4. 브라우저 창 우측 상단의 [X]를 눌러 닫아주시면 영구 저장이 완료됩니다.")
    print("=" * 70 + "\n")

    chrome_exe = find_chrome_path()
    print(f"🚀 실제 브라우저 실행 중... ({chrome_exe})")

    cmd = [
        chrome_exe,
        f"--user-data-dir={PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        "https://nid.naver.com/nidlogin.login?url=https%3A%2F%2Fkin.naver.com"
    ]

    subprocess.run(cmd)

    print("\n✅ 브라우저가 닫혔습니다. 영구 쿠키 동기화 중...")

    # Playwright로 쿠키 추출하여 naver_session.json 동기화
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=True
            )
            cookies = context.cookies()
            with open(SESSION_JSON, "w", encoding="utf-8") as f:
                json.dump({"cookies": cookies}, f, ensure_ascii=False, indent=2)
            context.close()
        print(f"🎉 [성공] 총 {len(cookies)}개의 최신 롤링 쿠키가 영구 보관함에 완벽하게 동기화되었습니다!")
        print("💡 이제 봇이 지식iN 질문을 낚아채고 실제 답변을 100% 무인으로 등록합니다.\n")
    except Exception as ex:
        print(f"⚠️ 쿠키 동기화 안내: {ex} (프로필 디스크 저장은 완료되었습니다)")


if __name__ == "__main__":
    main()
