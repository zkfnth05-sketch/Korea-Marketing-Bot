# -*- coding: utf-8 -*-
"""
Insurance Meta Login Helper (🛡️ 보험 리밸런스 메타 1회 영구 로그인 연동기 - 정품 크롬 전용)
=============================================================================
- 브랜드: 🛡️ 보험 리밸런스 (InsureBalance)
- 전용 계정: 보험 리밸런스 인스타/페북
- 프로필 디렉터리: brands/insurance/meta_chrome_profile/
- 역할:
  1. 실제 정품 구글 크롬(Chrome)을 전용 프로필 모드로 실행 (봇 탐지 0%, 팝업 0%)
  2. 대표님께서 인스타그램/페이스북에 평소처럼 정상 로그인 수행
  3. 크롬 창을 닫으면 Playwright가 자동으로 쿠키를 meta_session.json으로 추출·저장
"""

import os
import sys
import shutil
import asyncio
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
PROFILE_DIR = CURRENT_DIR / "meta_chrome_profile"
SESSION_FILE = CURRENT_DIR / "meta_session.json"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


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


async def _extract_and_save_session():
    """
    크롬 창이 닫힌 뒤 Playwright로 프로필을 열어
    인증 쿠키를 meta_session.json 으로 자동 추출·저장.
    """
    from playwright.async_api import async_playwright
    from core.engine.session_integrity import has_auth, _backup_path

    for fname in ["SingletonLock"]:
        lp = PROFILE_DIR / fname
        if lp.exists():
            try:
                lp.unlink()
            except Exception:
                pass

    print("\n[자동 추출] Playwright 로 쿠키 추출 중...")
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check",
            ],
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36"
            )
        )

        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        try:
            await page.goto(
                "https://www.instagram.com/",
                wait_until="domcontentloaded",
                timeout=20000
            )
            await asyncio.sleep(3)
        except Exception:
            pass

        cookies = await ctx.cookies()
        names = {c["name"] for c in cookies}

        print(f"  총 쿠키: {len(cookies)}개")
        print(f"  sessionid : {'[OK]' if 'sessionid' in names else '[없음]'}")
        print(f"  csrftoken : {'[OK]' if 'csrftoken' in names else '[없음]'}")
        print(f"  ds_user_id: {'[OK]' if 'ds_user_id' in names else '[없음]'}")

        auth_ok = has_auth("meta", cookies) or has_auth("instagram", cookies) or (
            "sessionid" in names and "ds_user_id" in names
        )

        if not auth_ok:
            print("\n[FAIL] 인증 쿠키가 없습니다.")
            print("  -> 다시 bat 파일 실행 후 인스타그램 로그인 완료 후 창을 닫아주세요.")
            await ctx.close()
            return False

        await ctx.storage_state(path=str(SESSION_FILE))
        await ctx.close()

    bp = _backup_path(SESSION_FILE)
    bp.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SESSION_FILE, bp)

    print(f"\n[BACKUP] 정상 백업 저장: {bp.name}")
    print("=" * 70)
    print("🎉 [성공] 인스타 로그인 세션이 meta_session.json 에 자동 저장되었습니다!")
    print("   봇이 다음 발행 시 이 세션을 사용합니다. 재로그인 불필요.")
    print("=" * 70)
    return True


def main():
    print("\n" + "=" * 70)
    print("🔑 [🛡️ 보험 리밸런스] 메타(인스타그램·페이스북) 영구 로그인 1회 연동기")
    print("=" * 70)
    print(f"👉 프로필 저장 위치: {PROFILE_DIR}")
    print("-" * 70)
    print("1. 화면에 진짜 정품 구글 크롬(Chrome) 브라우저가 열립니다.")
    print("2. 인스타그램에 정상 로그인(아이디/비번 또는 페이스북 연동)해 주세요.")
    print("3. 피드 메인 화면이 뜨면, 브라우저 창 우측 상단의 [X]를 눌러 닫아주세요.")
    print("4. 창을 닫으면 쿠키가 자동으로 봇 세션 파일에 저장됩니다. (Enter 불필요)")
    print("=" * 70 + "\n")

    chrome_exe = find_chrome_path()
    print(f"🚀 정품 크롬 실행 중... ({chrome_exe})")

    cmd = [
        chrome_exe,
        f"--user-data-dir={PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        "https://www.instagram.com/accounts/login/"
    ]

    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"\n❌ 실행 오류: {e}")
        return

    print("\n[INFO] 크롬 창이 닫혔습니다. 쿠키를 자동으로 추출합니다...")
    asyncio.run(_extract_and_save_session())


if __name__ == "__main__":
    main()
