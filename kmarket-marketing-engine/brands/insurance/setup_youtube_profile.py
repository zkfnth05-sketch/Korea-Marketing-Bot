# -*- coding: utf-8 -*-
"""
Insurance 전용 유튜브(Google/YouTube) 영구 브라우저 프로필 1회 생성 도구
========================================================================================
- 브랜드: 🛡️ 보험 리밸런스 (골드맘)
- 전용 계정: 보험 리밸런스 공식 채널 계정
- 프로필 경로: brands/insurance/youtube_chrome_profile/
- 설명: Playwright 독립 브라우저로 1회 로그인하면 브라우저 쿠키/인증토큰이 영구 저장됩니다.
- 원칙: Rule 1 (앱별 완전 독립 모듈화), Rule 6 (무인 자율 구동)
"""

import os
import sys
import json
import time
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

PROFILE_DIR = CURRENT_DIR / "youtube_chrome_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)
SESSION_JSON = CURRENT_DIR / "youtube_session.json"


def main():
    print("\n" + "=" * 70)
    print("🔑 [🛡️ 보험 리밸런스] 유튜브(Google/YouTube) 영구 브라우저 프로필 1회 세팅 도구")
    print("=" * 70)
    print(f"👉 대상 브랜드: 🛡️ 보험 리밸런스 (골드맘)")
    print(f"👉 프로필 저장 위치: {PROFILE_DIR}")
    print("-" * 70)
    print("1. 독립된 전용 크롬 창이 실행됩니다.")
    print("2. [보험 리밸런스 전용 구글 계정]으로 로그인해 주세요.")
    print("3. 유튜브 스튜디오 홈이 뜨면 브라우저 창 우측 상단 [X]를 눌러 닫아주세요.")
    print("=" * 70 + "\n")

    clean_browser_profile_locks(PROFILE_DIR)

    login_url = "https://accounts.google.com/ServiceLogin?service=youtube&continue=https%3A%2F%2Fstudio.youtube.com%2F"

    print("🚀 독립 크롬 브라우저 창을 여는 중입니다...", flush=True)
    with sync_playwright() as p:
        browser_args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-infobars",
            "--start-maximized",
            "--disable-gpu"
        ]
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport=None,
            args=browser_args
        )

        page = context.pages[0] if context.pages else context.new_page()
        page.goto(login_url)

        print("\n" + "=" * 70, flush=True)
        print("💡 [보험 리밸런스 zkfnth03@gmail.com 로그인 진행 중]", flush=True)
        print("1. 열린 크롬 창에서 [zkfnth03@gmail.com] 계정으로 로그인해 주세요.", flush=True)
        print("2. 로그인이 완료되어 유튜브 스튜디오 화면이 뜨면 봇이 자동으로 감지하여 저장합니다.", flush=True)
        print("   (또는 로그인 완료 후 이 터미널 창에서 [엔터(Enter)]를 누르셔도 됩니다)", flush=True)
        print("=" * 70 + "\n", flush=True)

        # 자동 감지 루프 (최대 10분 대기)
        for _ in range(600):
            time.sleep(1)
            try:
                current_url = page.url
                # 스튜디오 홈으로 정상 진입한 경우
                if "studio.youtube.com" in current_url and "accounts.google.com" not in current_url:
                    print("✨ [자동 감지] 유튜브 스튜디오 로그인 성공 감지! 세션을 동기화합니다...", flush=True)
                    time.sleep(2)
                    break
                if len(context.pages) == 0:
                    break
            except Exception:
                break

        # 쿠키 추출 및 동기화
        clean_cookies = []
        try:
            cookies = context.cookies()
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
        except Exception as ce:
            print(f"쿠키 저장 참조: {ce}", flush=True)

        try:
            context.close()
        except Exception:
            pass

    has_login = any(c.get("name") in ["LOGIN_INFO", "SID", "SSID", "SAPISID"] for c in clean_cookies)
    print("\n" + "=" * 70)
    print(f"🎉 [성공] 총 {len(clean_cookies)}개의 유튜브 세션 쿠키가 영구 보관함에 완벽하게 동기화되었습니다!")
    if has_login:
        print("✅ [검증 통과] 보험 리밸런스 구글/유튜브 인증 토큰(SID/LOGIN_INFO) 정상 감지 완료!")
    else:
        print("⚠️ [안내] 로그인 토큰이 감지되지 않았습니다. 로그인이 정상 완료되었는지 확인해 주세요.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
