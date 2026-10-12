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
    mbs_login_url = "https://business.facebook.com/latest/home?business_id=1106559705427284&asset_id=1358924267302888"
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
        import shutil, time
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=True,
                args=["--disable-blink-features=AutomationControlled",
                      "--no-first-run", "--no-default-browser-check"],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            )
            # 인스타그램 피드 접속으로 sessionid 쿠키 활성화
            page = context.pages[0] if context.pages else context.new_page()
            try:
                page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=20000)
                time.sleep(3)
            except Exception:
                pass

            cookies = context.cookies()
            for c in cookies:
                c_item = {
                    "name": c.get("name"),
                    "value": c.get("value"),
                    "domain": c.get("domain", ".instagram.com"),
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

        print(f"[INFO] 총 {len(clean_cookies)}개 쿠키 추출 완료")
        names = {c.get("name") for c in clean_cookies}
        has_ig_auth = "sessionid" in names and "ds_user_id" in names
        has_fb_auth = "c_user" in names and "xs" in names

        if has_ig_auth or has_fb_auth:
            print("[OK] 인증 쿠키 검증 통과 (sessionid/ds_user_id 또는 c_user/xs 정상 감지)")
            backup_dir = SESSION_JSON.parent / "session_backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / "meta_session.good.json"
            shutil.copyfile(SESSION_JSON, backup_path)
            print(f"[BACKUP] 정상 백업 저장: {backup_path.name}")
            print("[SUCCESS] 이제 봇이 이 세션으로 24시간 무인 송출합니다. 재로그인 불필요!\n")
        else:
            print("[WARNING] 인증 쿠키(sessionid/c_user)가 없습니다.")
            print("  -> 인스타그램에 로그인 완료 후 피드가 뜰 때 창을 닫아주세요.\n")
    except Exception as ex:
        print(f"[ERROR] 쿠키 동기화 오류: {ex}\n")


if __name__ == "__main__":
    main()
