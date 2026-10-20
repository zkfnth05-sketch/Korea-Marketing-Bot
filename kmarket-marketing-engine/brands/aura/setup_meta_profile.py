# -*- coding: utf-8 -*-
"""
Aura AI 데이팅 전용 메타(Meta Business Suite / Facebook / Instagram) 영구 로그인 1회 세팅 도구
========================================================================================
- 브랜드: 💖 Aura AI 데이팅
- 전용 계정: 페이스북(Aura) + 인스타그램(aura_ai_dating)
- 프로필 경로: brands/aura/meta_chrome_profile/
- 설명: Meta Business Suite(business.facebook.com) 통합 관리 화면으로 직접 1회 로그인하여
       페이스북/인스타그램 동시 송출용 마스터 세션 쿠키를 4중 원자적 저장으로 완벽히 동기화합니다.

[6인 합동 회의체 합의안 반영 항목]
  1. 실제 크롬 브라우저 탐색 후 meta_chrome_profile 을 user-data-dir 로 지정 실행
  2. 실행 URL: https://business.facebook.com/latest/home
  3. 창 종료 후 Playwright launch_persistent_context 로 재접속
     - business.facebook.com/latest/home  → 페이스북 세션 쿠키 수집
     - www.instagram.com                  → 인스타그램 세션 쿠키 수집
  4. domain/path/secure/httpOnly/sameSite 완벽 보존 (인스타 도메인 덮어쓰기 절대 금지)
     Session 쿠키 또는 30일 이내 만료 → now + 31536000 (1년) 강제 패치
  5. meta_session.json / meta_session_GOLDEN.json / meta_session_verified.json /
     session_backups/meta_session.good.json  → 전부 원자적(temp -> replace) 저장
  6. c_user + xs (Facebook) / sessionid + ds_user_id (Instagram) 상세 검증
  7. clean_browser_profile_locks 적용
  8. py_compile 무결점 통과
========================================================================================
"""

import os
import sys
import json
import time
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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

# ============================================================================
# 상수 정의
# ============================================================================
BRAND_NAME = "💖 Aura AI 데이팅"
PROFILE_DIR = CURRENT_DIR / "meta_chrome_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

SESSION_JSON = CURRENT_DIR / "meta_session.json"
SESSION_GOLDEN_JSON = CURRENT_DIR / "meta_session_GOLDEN.json"
SESSION_VERIFIED_JSON = CURRENT_DIR / "meta_session_verified.json"
BACKUP_DIR = CURRENT_DIR / "session_backups"
BACKUP_JSON = BACKUP_DIR / "meta_session.good.json"

MBS_HOME_URL = "https://business.facebook.com/latest/home"
INSTAGRAM_HOME_URL = "https://www.instagram.com/"

# 영구 지속 강제 패치: 1년 (365일)
ONE_YEAR_SECONDS = 31536000
# 30일 이내 만료 → 영구 패치 대상
THIRTY_DAYS_SECONDS = 30 * 24 * 60 * 60

# 인증 필수 쿠키
FB_AUTH_COOKIES = ("c_user", "xs")
IG_AUTH_COOKIES = ("sessionid", "ds_user_id")

# sameSite 허용 화이트리스트 (Playwright 표준 표기)
VALID_SAME_SITE = ("Strict", "Lax", "None")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


# ============================================================================
# 유틸리티: 실제 크롬 브라우저 탐색
# ============================================================================
def find_chrome_path() -> str:
    """실제 설치된 크롬(Chrome) 실행 파일 경로를 탐색하여 반환합니다."""
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
        # 최후 폴백: Edge (크로미움 계열)
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    for p in candidates:
        if p and os.path.exists(p):
            return p
    return "chrome.exe"


# ============================================================================
# 유틸리티: 원자적 저장 (temp -> replace)
# ============================================================================
def atomic_write_json(target_path: Path, payload: Dict[str, Any]) -> bool:
    """
    임시 파일에 먼저 기록한 뒤 os.replace 로 원자적 교체합니다.
    (중간 크래시/전원 차단 시에도 기존 파일이 절대 손상되지 않음)
    """
    target_path = Path(target_path)
    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(
            prefix=f".{target_path.stem}_",
            suffix=".tmp",
            dir=str(target_path.parent),
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_name, str(target_path))
            return True
        except Exception:
            try:
                if os.path.exists(tmp_name):
                    os.unlink(tmp_name)
            except Exception:
                pass
            raise
    except Exception as ex:
        print(f"  [ERROR] 원자적 저장 실패 ({target_path.name}): {ex}")
        return False


# ============================================================================
# 핵심: 쿠키 정규화 (도메인 보존 + 영구 만료 패치)
# ============================================================================
def normalize_cookie(raw: Dict[str, Any], now_ts: float) -> Dict[str, Any]:
    """
    Playwright 원본 쿠키 1개를 영구 지속형 표준 쿠키로 정규화합니다.

    [절대 원칙]
      - domain / path / secure / httpOnly / sameSite 는 원본 값을 그대로 보존합니다.
        (인스타그램 쿠키를 .facebook.com 으로 덮어쓰는 행위 절대 금지)
      - expires 가 없거나(Session 쿠키), -1 이거나, 30일 이내 만료이면
        now + 31536000 (1년 뒤) 로 강제 패치합니다.
    """
    name = raw.get("name")
    value = raw.get("value", "")

    # ── 도메인: 원본 그대로 보존 (덮어쓰기 금지) ──
    domain = raw.get("domain")
    if not domain:
        # 도메인 정보가 아예 유실된 경우에만 URL 기반 최소 추정 (원본 보존 우선)
        domain = ".facebook.com"

    # ── path / secure / httpOnly: 원본 그대로 보존 ──
    path = raw.get("path") or "/"
    secure = bool(raw.get("secure", True))
    http_only = bool(raw.get("httpOnly", False))

    # ── sameSite: 원본 보존, 미존재 시에만 Lax 기본값 ──
    same_site = raw.get("sameSite")
    if same_site not in VALID_SAME_SITE:
        same_site = "Lax"

    # ── expires: Session(-1/None) 또는 30일 이내 만료 → 1년 뒤로 강제 패치 ──
    raw_expires = raw.get("expires", None)
    patched = False
    reason = ""

    if raw_expires is None or raw_expires == -1:
        expires = now_ts + ONE_YEAR_SECONDS
        patched = True
        reason = "Session 쿠키"
    else:
        try:
            expires = float(raw_expires)
        except (TypeError, ValueError):
            expires = now_ts + ONE_YEAR_SECONDS
            patched = True
            reason = "만료값 파싱 불가"
        else:
            if expires <= 0:
                expires = now_ts + ONE_YEAR_SECONDS
                patched = True
                reason = "만료값 0 이하"
            elif expires < (now_ts + THIRTY_DAYS_SECONDS):
                expires = now_ts + ONE_YEAR_SECONDS
                patched = True
                reason = "30일 이내 만료"

    cookie: Dict[str, Any] = {
        "name": name,
        "value": value,
        "domain": domain,
        "path": path,
        "secure": secure,
        "httpOnly": http_only,
        "sameSite": same_site,
        "expires": expires,
    }
    if patched:
        cookie["_expires_patched"] = True
        cookie["_patch_reason"] = reason
    return cookie


def dedupe_cookies(cookies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    (name, domain, path) 복합키 기준 중복 제거.
    동일 키가 여러 번 수집된 경우 마지막(가장 최신) 값을 유지합니다.
    """
    merged: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    for c in cookies:
        key = (str(c.get("name")), str(c.get("domain")), str(c.get("path")))
        merged[key] = c
    return list(merged.values())


# ============================================================================
# 핵심: Playwright 로 세션 쿠키 수집
# ============================================================================
def harvest_session_cookies() -> List[Dict[str, Any]]:
    """
    launch_persistent_context 로 meta_chrome_profile 을 열어
    페이스북(MBS) + 인스타그램 세션 쿠키를 수집합니다.
    """
    from playwright.sync_api import sync_playwright

    collected: List[Dict[str, Any]] = []

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-dev-shm-usage",
            ],
            user_agent=USER_AGENT,
            viewport={"width": 1440, "height": 900},
            locale="ko-KR",
        )
        try:
            page = context.pages[0] if context.pages else context.new_page()

            # ── 1단계: Meta Business Suite 홈 → 페이스북 세션 쿠키 ──
            print("  [1/2] Meta Business Suite 홈 접속 중... (페이스북 세션 수집)")
            try:
                page.goto(MBS_HOME_URL, wait_until="domcontentloaded", timeout=45000)
                time.sleep(4)
                try:
                    page.wait_for_load_state("networkidle", timeout=15000)
                except Exception:
                    pass
                time.sleep(2)
            except Exception as ex:
                print(f"        ⚠️ MBS 접속 경고(계속 진행): {ex}")

            fb_cookies = context.cookies()
            collected.extend(fb_cookies)
            print(f"        → 페이스북 도메인 쿠키 {len(fb_cookies)}개 수집")

            # ── 2단계: 인스타그램 홈 → 인스타그램 세션 쿠키 ──
            print("  [2/2] Instagram 홈 접속 중... (인스타그램 세션 수집)")
            try:
                page.goto(INSTAGRAM_HOME_URL, wait_until="domcontentloaded", timeout=45000)
                time.sleep(4)
                try:
                    page.wait_for_load_state("networkidle", timeout=15000)
                except Exception:
                    pass
                time.sleep(2)
            except Exception as ex:
                print(f"        ⚠️ Instagram 접속 경고(계속 진행): {ex}")

            ig_cookies = context.cookies()
            collected.extend(ig_cookies)
            print(f"        → 인스타그램 도메인 쿠키 {len(ig_cookies)}개 수집")

            # ── 3단계: 전체 컨텍스트 쿠키 최종 재수집 (누락 방지) ──
            try:
                all_cookies = context.cookies()
                if all_cookies:
                    collected.extend(all_cookies)
            except Exception:
                pass

        finally:
            try:
                context.close()
            except Exception:
                pass

    return collected


# ============================================================================
# 검증: 인증 쿠키 상세 상태 출력
# ============================================================================
def verify_auth_cookies(cookies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    c_user + xs (Facebook) / sessionid + ds_user_id (Instagram) 존재 여부를
    도메인 기준으로 정밀 판정하여 상세 상태를 반환합니다.
    """
    fb_found: Dict[str, Optional[str]] = {}
    ig_found: Dict[str, Optional[str]] = {}

    for c in cookies:
        name = str(c.get("name", ""))
        domain = str(c.get("domain", "")).lower()

        is_fb_domain = "facebook.com" in domain
        is_ig_domain = "instagram.com" in domain

        if name in FB_AUTH_COOKIES and is_fb_domain:
            fb_found[name] = domain
        if name in IG_AUTH_COOKIES and is_ig_domain:
            ig_found[name] = domain

    fb_ok = all(fb_found.get(k) for k in FB_AUTH_COOKIES)
    ig_ok = all(ig_found.get(k) for k in IG_AUTH_COOKIES)

    return {
        "facebook": {
            "ok": fb_ok,
            "c_user": fb_found.get("c_user"),
            "xs": fb_found.get("xs"),
        },
        "instagram": {
            "ok": ig_ok,
            "sessionid": ig_found.get("sessionid"),
            "ds_user_id": ig_found.get("ds_user_id"),
        },
        "both_ok": fb_ok and ig_ok,
        "any_ok": fb_ok or ig_ok,
    }


def print_verification_report(report: Dict[str, Any], total: int, patched: int) -> None:
    """검증 결과를 상세하게 콘솔에 출력합니다."""
    fb = report["facebook"]
    ig = report["instagram"]

    print("\n" + "=" * 74)
    print("🔍 [세션 쿠키 인증 검증 상세 리포트]")
    print("=" * 74)
    print(f"  총 수집 쿠키 수       : {total}개")
    print(f"  영구 만료 패치 쿠키 수 : {patched}개 (Session/30일 이내 → 1년 연장)")
    print("-" * 74)

    fb_mark = "✅ 정상" if fb["ok"] else "❌ 누락"
    print(f"  [페이스북 인증] {fb_mark}")
    print(f"    · c_user    : {'✅ ' + str(fb['c_user']) if fb['c_user'] else '❌ 없음'}")
    print(f"    · xs        : {'✅ ' + str(fb['xs']) if fb['xs'] else '❌ 없음'}")

    ig_mark = "✅ 정상" if ig["ok"] else "❌ 누락"
    print(f"  [인스타그램 인증] {ig_mark}")
    print(f"    · sessionid : {'✅ ' + str(ig['sessionid']) if ig['sessionid'] else '❌ 없음'}")
    print(f"    · ds_user_id: {'✅ ' + str(ig['ds_user_id']) if ig['ds_user_id'] else '❌ 없음'}")
    print("-" * 74)

    if report["both_ok"]:
        print("  🎉 [최종 판정] 페이스북 + 인스타그램 인증 쿠키 전부 정상! (완전체 세션)")
    elif report["any_ok"]:
        print("  ⚠️ [최종 판정] 한쪽 플랫폼만 인증됨. 나머지 계정 재로그인 권장.")
    else:
        print("  🚨 [최종 판정] 인증 쿠키 전무. 로그인 미완료 상태입니다.")
    print("=" * 74 + "\n")


# ============================================================================
# 메인 실행
# ============================================================================
def main() -> None:
    print("\n" + "=" * 74)
    print(f"🔑 [{BRAND_NAME}] 메타(페이스북·인스타) 영구 로그인 1회 세팅 도구")
    print("=" * 74)
    print(f"👉 대상 브랜드   : {BRAND_NAME}")
    print(f"👉 대상 계정     : 페이스북(Aura) + 인스타그램(aura_ai_dating)")
    print(f"👉 프로필 경로   : {PROFILE_DIR}")
    print(f"👉 실행 URL      : {MBS_HOME_URL}")
    print("-" * 74)
    print("1. 실제 크롬 브라우저가 메타 전용 영구 프로필 모드로 실행됩니다.")
    print("2. Meta Business Suite 화면에서 페이스북/인스타그램 계정으로 로그인하세요.")
    print("3. 비즈니스 스위트 홈이 정상 표시되면 브라우저 창 [X]를 눌러 닫아주세요.")
    print("4. 창이 닫히면 자동으로 쿠키 수집 → 영구 패치 → 4중 원자적 저장이 진행됩니다.")
    print("=" * 74 + "\n")

    # ── [7] 프로필 락 청소 (1회차: 실행 전) ──
    clean_browser_profile_locks(PROFILE_DIR)

    # ── [1] 실제 크롬 브라우저 탐색 및 실행 ──
    chrome_exe = find_chrome_path()
    print(f"🚀 실제 크롬 브라우저 실행 중... ({chrome_exe})")

    cmd = [
        chrome_exe,
        f"--user-data-dir={PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-blink-features=AutomationControlled",
        MBS_HOME_URL,
    ]

    try:
        subprocess.run(cmd)
    except Exception as ex:
        print(f"[ERROR] 크롬 실행 실패: {ex}")
        print("        → 크롬 설치 경로를 확인해 주세요.")
        return

    print("\n[INFO] 브라우저가 닫혔습니다. 영구 세션 쿠키 동기화를 시작합니다...")

    # ── [7] 프로필 락 청소 (2회차: Playwright 재접속 전) ──
    clean_browser_profile_locks(PROFILE_DIR)

    # ── [3] Playwright 로 세션 쿠키 수집 ──
    try:
        raw_cookies = harvest_session_cookies()
    except Exception as ex:
        print(f"[ERROR] 쿠키 수집 실패: {ex}")
        return

    if not raw_cookies:
        print("[ERROR] 수집된 쿠키가 0개입니다. 로그인이 완료되지 않았습니다.")
        return

    # ── [4] 쿠키 정규화 (도메인 보존 + 영구 만료 패치) ──
    now_ts = time.time()
    normalized: List[Dict[str, Any]] = []
    patched_count = 0

    for raw in raw_cookies:
        if not raw.get("name"):
            continue
        cookie = normalize_cookie(raw, now_ts)
        if cookie.get("_expires_patched"):
            patched_count += 1
        normalized.append(cookie)

    normalized = dedupe_cookies(normalized)

    # ── [6] 인증 쿠키 검증 ──
    report = verify_auth_cookies(normalized)

    # ── [5] 4중 원자적 저장 ──
    payload: Dict[str, Any] = {
        "cookies": normalized,
        "meta": {
            "brand": BRAND_NAME,
            "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "saved_at_ts": now_ts,
            "total_cookies": len(normalized),
            "expires_patched": patched_count,
            "source_urls": [MBS_HOME_URL, INSTAGRAM_HOME_URL],
            "profile_dir": str(PROFILE_DIR),
            "verification": report,
        },
    }

    print("\n[INFO] 4중 원자적 저장 진행 중...")
    results = {
        "meta_session.json": atomic_write_json(SESSION_JSON, payload),
        "meta_session_GOLDEN.json": atomic_write_json(SESSION_GOLDEN_JSON, payload),
        "meta_session_verified.json": atomic_write_json(SESSION_VERIFIED_JSON, payload),
        "session_backups/meta_session.good.json": atomic_write_json(BACKUP_JSON, payload),
    }
    for fname, ok in results.items():
        print(f"  {'✅' if ok else '❌'} {fname}")

    # ── [6] 상세 검증 리포트 출력 ──
    print_verification_report(report, len(normalized), patched_count)

    if report["both_ok"]:
        print("[SUCCESS] 페이스북 + 인스타그램 완전체 세션 확보! 재로그인 불필요.\n")
    elif report["any_ok"]:
        print("[PARTIAL] 일부 플랫폼만 인증되었습니다. 누락 계정 재로그인을 권장합니다.\n")
    else:
        print("[WARNING] 인증 쿠키가 없습니다. 로그인 완료 후 다시 실행해 주세요.\n")


if __name__ == "__main__":
    main()
