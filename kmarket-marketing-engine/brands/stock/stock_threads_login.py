# -*- coding: utf-8 -*-
"""
Stock Threads Login Helper (📈 StockMaster AI 스레드 1회 영구 로그인 연동기 - Playwright 완벽 감지)
=============================================================================================
- 브랜드: 📈 StockMaster AI (주식 AI)
- 전용 계정: @stockmaster_ai
- 프로필 디렉터리: brands/stock/threads_chrome_profile/  (🔒 meta_chrome_profile 과 물리적 완전 격리)
- 세션 파일: brands/stock/threads_session.json
- 골든 세션: brands/stock/threads_session_GOLDEN.json (불변 스냅샷 · 자가치유 원본)
- 역할:
  1. 실제 독립 브라우저 창을 화면에 띄움 (headless=False)
  2. 스레드(threads.net/login) 로그인 페이지로 연결
  3. 사용자가 아이디/비번 또는 Continue with Instagram으로 로그인 수행
  4. 메인 피드 진입이 완벽히 확인될 때까지 대기
  5. 로그인 성공 시 threads_chrome_profile 및 threads_session.json + threads_session_GOLDEN.json
     동시 원자적 저장(temp→fsync→os.replace) 후 자동 종료
"""

import os
import sys
import json
import shutil
import asyncio
import logging
import tempfile
from pathlib import Path
from playwright.async_api import async_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("StockThreadsLogin")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
# 🔒 프로필 물리 격리: meta_chrome_profile 과 완전 분리된 스레드 전용 프로필
PROFILE_DIR = CURRENT_DIR / "threads_chrome_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)
SESSION_FILE = CURRENT_DIR / "threads_session.json"
# 🧬 불변 골든 세션 스냅샷 (자가치유 원본)
GOLDEN_SESSION_FILE = CURRENT_DIR / "threads_session_GOLDEN.json"
ACCOUNTS_FILE = CURRENT_DIR / "accounts.json"
# 🔑 스레드 로그인 증명 핵심 쿠키
THREADS_AUTH_COOKIE_NAMES = {"sessionid", "ds_user_id"}


# =====================================================================
# 🧬 원자적 파일 유틸 (temp → fsync → os.replace)
# =====================================================================
def _atomic_copy(src: Path, dst: Path) -> bool:
    """원본 → 대상 원자적 복사 (불변 스냅샷 생성/복원용)

    ⚠️ Windows 주의: 읽기전용("rb") 핸들에 os.fsync() 를 호출하면
       [Errno 9] Bad file descriptor 가 발생한다.
       반드시 쓰기 가능 핸들("r+b")에서 fsync 를 수행해야 한다.
    """
    try:
        if not src.exists() or src.stat().st_size < 20:
            return False
        dst.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix=f".{dst.stem}_", suffix=".tmp", dir=str(dst.parent))
        os.close(fd)
        try:
            shutil.copyfile(src, tmp_name)
            # ✅ Windows 안전: 쓰기 가능 핸들에서 fsync
            with open(tmp_name, "r+b") as f:
                os.fsync(f.fileno())
            os.replace(tmp_name, dst)
            return True
        except Exception:
            try:
                if os.path.exists(tmp_name):
                    os.unlink(tmp_name)
            except Exception:
                pass
            raise
    except Exception as e:
        logger.warning(f"⚠️ 원자적 복사 실패({src.name} → {dst.name}): {e}")
        return False


def _has_threads_auth(path: Path) -> bool:
    """세션 파일에 스레드 인증 쿠키(sessionid / ds_user_id)가 실제로 존재하는가"""
    try:
        if not path.exists() or path.stat().st_size < 20:
            return False
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            ck = data.get("cookies")
            cookies = [c for c in ck if isinstance(c, dict)] if isinstance(ck, list) else []
        elif isinstance(data, list):
            cookies = [c for c in data if isinstance(c, dict)]
        else:
            cookies = []
        names = {str(c.get("name", "")).lower() for c in cookies}
        return bool(names & THREADS_AUTH_COOKIE_NAMES)
    except Exception:
        return False


def save_session_and_golden() -> bool:
    """
    🧬 로그인 완료 직후 세션 + GOLDEN 동시 원자적 저장

    - threads_session.json 이 유효 인증 쿠키를 담고 있을 때만 GOLDEN 스냅샷 생성
    - GOLDEN 은 temp → fsync → os.replace 로 원자적 교체 (부분 기록 원천 차단)
    """
    if not _has_threads_auth(SESSION_FILE):
        logger.warning("⚠️ GOLDEN 저장 스킵: threads_session.json 에 인증 쿠키가 없습니다.")
        return False
    ok = _atomic_copy(SESSION_FILE, GOLDEN_SESSION_FILE)
    if ok:
        print(f"💾 2. {GOLDEN_SESSION_FILE.name} 불변 골든 세션 동시 원자적 저장 완료")
    else:
        logger.warning("⚠️ GOLDEN 세션 원자적 저장 실패")
    return ok


async def run_threads_login_flow():
    print("\n" + "=" * 70)
    print("🔑 [📈 StockMaster AI] 스레드(Threads) 영구 로그인 1회 연동기")
    print(f"👉 전용 계정: [ @stockmaster_ai ]")
    print(f"👉 영구 프로필: {PROFILE_DIR.name}")
    print("=" * 70)
    print("1. 화면에 스레드 전용 브라우저 창이 열립니다.")
    print("2. 인스타그램 @stockmaster_ai 계정으로 로그인을 완료해 주세요.")
    print("   (아이디/비번 직접 입력 또는 아래 'Continue with Instagram' 클릭)")
    print("3. 메인 피드(홈 화면)가 정상 표시되면 봇이 자동 감지하여 영구 저장 후 창을 닫습니다.")
    print("=" * 70 + "\n")

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
                "--no-default-browser-check"
            ],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900}
        )
        page = context.pages[0] if context.pages else await context.new_page()

        await page.goto("https://www.threads.net/login", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        # 'Continue with Instagram' 버튼이 있으면 자동으로 클릭하여 로그인 화면으로 유도
        try:
            continue_btn = await page.query_selector("div:has-text('Continue with Instagram'), button:has-text('Continue with Instagram')")
            if continue_btn:
                print("👉 'Continue with Instagram' 버튼 자동 클릭...")
                await continue_btn.click()
        except Exception:
            pass

        print("⏳ 스레드 로그인 대기 중... (열린 창에서 로그인을 진행해 주세요)")

        logged_in = False
        for i in range(450):  # 450 * 2초 = 15분 대기
            await asyncio.sleep(2)

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
                        login_form = await p_check.query_selector("input[type='password'], button:has-text('Log in'), div:has-text('Say more with Threads')")
                        nav_element = await p_check.query_selector("svg[aria-label='Create'], svg[aria-label='새 스레드'], svg[aria-label='Home'], svg[aria-label='홈'], a[href*='/@'], div[role='button'][aria-label*='새']")
                        clean_url = curr_url.rstrip("/")
                        if (not login_form and nav_element) or clean_url in ["https://www.threads.net", "https://threads.net", "https://www.threads.com", "https://threads.com"]:
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

        print("\n🎉 [대성공!] StockMaster AI 스레드 피드 진입 및 로그인이 정상 확인되었습니다!")

        await context.storage_state(path=str(SESSION_FILE))
        print(f"💾 1. 영구 프로필 및 {SESSION_FILE.name} 세션 동기화 완료")

        # 🧬 GOLDEN 세션 동시 원자적 저장 (자가치유 원본)
        save_session_and_golden()

        vfile = CURRENT_DIR / "threads_session_verified.json"
        with open(vfile, "w", encoding="utf-8") as vf:
            json.dump({"verified_at": "2026-10-11", "brand": "stock", "status": "authenticated"}, vf, indent=2)

        try:
            cookies = await context.cookies()
            with open(CURRENT_DIR / "threads_cookies.json", "w", encoding="utf-8") as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            print("💾 3. threads_cookies.json 영구 쿠키 파일 저장 완료")
        except Exception as ce:
            logger.warning(f"쿠키 파일 저장 경고: {ce}")

        if ACCOUNTS_FILE.exists():
            try:
                with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                    acc = json.load(f)
                acc.setdefault("credentials", {})["threads_session_connected"] = True
                acc["credentials"]["threads_username"] = "stockmaster_ai"
                with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
                    json.dump(acc, f, ensure_ascii=False, indent=2)
                print("💾 4. accounts.json 연동 상태 업데이트 완료")
            except Exception as ex:
                logger.warning(f"accounts.json 업데이트 실패: {ex}")

        print("\n✨ 이제부터 StockMaster AI 마케팅봇이 스레드에 완전 무인으로 영구 자동 송출합니다!")
        print("창은 3초 후 자동으로 닫힙니다...\n")

        await asyncio.sleep(3)
        await context.close()
        return True


if __name__ == "__main__":
    success = asyncio.run(run_threads_login_flow())
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
