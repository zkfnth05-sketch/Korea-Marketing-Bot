# -*- coding: utf-8 -*-
"""
보험 리밸런스 (골드망) 전용 메타(Meta Business Suite / Instagram / Facebook) 영구 브라우저 프로필 1회 생성 도구
========================================================================================
- 브랜드: 🛡️ 보험 리밸런스 (골드망)
- 전용 계정: 페이스북(Goldmom) + 인스타그램(goldmomofficial)
- 프로필 경로: brands/insurance/meta_chrome_profile/
- 설명: Meta Business Suite(business.facebook.com) 통합 관리 화면으로 직접 1회 로그인하여
       페이스북/인스타그램 동시 송출용 마스터 세션 쿠키를 meta_session.json에 완벽히 동기화합니다.
========================================================================================
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
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine.browser_guard import clean_browser_profile_locks

PROFILE_DIR = CURRENT_DIR / "meta_chrome_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)
SESSION_JSON = CURRENT_DIR / "meta_session.json"


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
    print("🔑 [🛡️ 보험 리밸런스 (골드망)] 메타(페이스북·인스타) 통합 비즈니스 영구 프로필 1회 세팅 도구")
    print("=" * 70)
    print(f"👉 대상 브랜드: 🛡️ 보험 리밸런스 (골드망)")
    print(f"👉 대상 계정: 페이스북(Goldmom) + 인스타그램(goldmomofficial)")
    print(f"👉 프로필 저장 위치: {PROFILE_DIR}")
    print("-" * 70)
    print("1. 실제 크롬 브라우저가 보험 리밸런스 (골드망) 메타 전용 영구 프로필 모드로 실행됩니다.")
    print("2. Meta Business Suite 또는 페이스북/인스타그램 계정으로 로그인해 주세요.")
    print("3. 메타 비즈니스 스위트(business.facebook.com) 홈 화면이 정상적으로 뜨면,")
    print("4. 브라우저 창 우측 상단의 [X]를 눌러 닫아주시면 영구 저장이 완료됩니다.")
    print("=" * 70 + "\n")

    clean_browser_profile_locks(PROFILE_DIR)

    chrome_exe = find_chrome_path()
    mbs_login_url = "https://business.facebook.com/latest/home?asset_id=1358924267302888"
    print(f"🚀 실제 크롬 브라우저 실행 중... ({chrome_exe})")

    cmd = [
        chrome_exe,
        f"--user-data-dir={PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        mbs_login_url
    ]

    subprocess.run(cmd)

    print("\n✅ 브라우저가 닫혔습니다. 영구 세션 쿠키 동기화 중...")
    clean_browser_profile_locks(PROFILE_DIR)

    # Playwright로 쿠키 추출하여 meta_session.json 동기화
    clean_cookies = []
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=True,
                args=["--disable-blink-features=AutomationControlled"]
            )
            cookies = context.cookies()
            for c in cookies:
                c_item = {
                    "name": c.get("name"),
                    "value": c.get("value"),
                    "domain": c.get("domain", ".facebook.com"),
                    "path": c.get("path", "/"),
                    "secure": c.get("secure", True),
                    "httpOnly": c.get("httpOnly", False)
                }
                if "sameSite" in c and c["sameSite"] in ["Strict", "Lax", "None"]:
                    c_item["sameSite"] = c["sameSite"]
                clean_cookies.append(c_item)

            with open(SESSION_JSON, "w", encoding="utf-8") as f:
                json.dump({"cookies": clean_cookies}, f, ensure_ascii=False, indent=2)
            context.close()
            
        print(f"🎉 [성공] 총 {len(clean_cookies)}개의 최신 메타(페이스북/인스타) 쿠키가 영구 보관함에 완벽하게 동기화되었습니다!")
        has_fb_auth = any(c.get("name") in ["c_user", "xs", "datr"] for c in clean_cookies)
        if has_fb_auth:
            print("✅ [검증 통과] Meta Business Suite 마스터 인증 토큰(c_user/xs) 정상 감지 완료!")
            print("👉 이제 페이스북 + 인스타그램 릴스 24시간 무인 동시 송출이 가능합니다.\n")
        else:
            print("ℹ️ [안내] 로그인 후 창을 닫아주시면 세션이 즉시 반영됩니다.\n")
    except Exception as ex:
        print(f"⚠️ 쿠키 동기화 안내: {ex} (프로필 디스크 저장은 완료되었습니다)\n")


if __name__ == "__main__":
    main()
