# -*- coding: utf-8 -*-
"""
[독립 레고 블록] Session Integrity (영구 로그인 무결성 보호막)
=====================================================================
풀리는 근본 원인 3가지를 원천 차단한다.
  1. 로그아웃 상태 쿠키가 정상 세션 파일(*_session.json)을 덮어쓰는 문제
     -> 인증 쿠키가 '실제로 존재'할 때만 저장(safe_save), 정상본은 별도 백업 유지
  2. '프로필이 비어있을 때만' 복구하던 조건(익명 쿠키 때문에 복구가 영영 건너뛰어짐)
     -> 플랫폼별 '인증 쿠키 유무'로 판단(ensure_auth_cookies)
  3. 로그아웃 화면을 못 알아채던 판정
     -> 플랫폼별 로그아웃 URL 판정(is_logged_out_url)
추가: 쿠키 상태 시간별 포렌식 로그(session_integrity_log.jsonl)로 언제 풀렸는지 추적한다.

원칙: 이 모듈은 어떤 브랜드/플랫폼 코드에도 의존하지 않는다 (각 퍼블리셔가 호출만 한다).
"""

import json
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

# 플랫폼별 '로그인 됐다'를 증명하는 인증 쿠키 규칙
#  - all_of: 전부 있어야 함 / any_of: 하나라도 있으면 됨
AUTH_RULES: Dict[str, Dict[str, Any]] = {
    "meta": {"complex": True},  # FB: c_user+xs, IG-only: sessionid (has_auth에서 복합 처리)
    "tiktok": {"any_of": ["sessionid", "sessionid_ss", "sid_tt"]},
    "youtube": {"any_of": ["SID", "__Secure-1PSID", "__Secure-3PSID"]},
    "google": {"any_of": ["SID", "__Secure-1PSID", "__Secure-3PSID"]},
    "naver": {"all_of": ["NID_AUT", "NID_SES"]},
    "tistory": {"any_of": ["_kawlt", "TSSESSION", "_T_ID", "TSID"]},
    "brunch": {"any_of": ["_kawlt", "TSID", "bid", "b_s_a_l", "_maldive_oauth_webapp_session_key"]},
    "threads": {"any_of": ["sessionid"]},
    "instagram": {"any_of": ["sessionid"]},
}

# 로그아웃(로그인 화면) URL 조각
LOGGED_OUT_URL_HINTS: Dict[str, List[str]] = {
    "meta": ["facebook.com/login", "/loginpage", "/login/", "checkpoint", "/login.php"],
    "tiktok": ["tiktok.com/login", "/login?", "passport/web/login"],
    "youtube": ["accounts.google.com", "/signin", "ServiceLogin"],
    "google": ["accounts.google.com", "/signin", "ServiceLogin"],
    "naver": ["nid.naver.com/nidlogin", "nid.naver.com/user2", "nidlogin.login"],
    "tistory": ["auth/login", "accounts.kakao.com", "kauth.kakao.com"],
    "brunch": ["signin", "accounts.kakao.com", "kauth.kakao.com", "login"],
    "threads": ["/login", "accounts/login"],
    "instagram": ["accounts/login", "/login"],
}


def _names(cookies: Iterable[Dict[str, Any]]) -> set:
    return {str(c.get("name")) for c in (cookies or []) if isinstance(c, dict)}


def has_auth(platform: str, cookies: Iterable[Dict[str, Any]]) -> bool:
    """쿠키 목록에 해당 플랫폼의 로그인 인증 쿠키가 실제로 존재하는가"""
    rule = AUTH_RULES.get(platform)
    if not rule:
        return bool(cookies)
    names = _names(cookies)
    if platform == "meta":
        # 페이스북(c_user AND xs) 또는 인스타그램 단독(sessionid) 복합 인증 허용
        has_fb = ("c_user" in names and "xs" in names)
        has_ig = ("sessionid" in names)
        return has_fb or has_ig
    if "all_of" in rule and not all(n in names for n in rule["all_of"]):
        return False
    if "any_of" in rule and not any(n in names for n in rule["any_of"]):
        return False
    return True


def is_logged_out_url(platform: str, url: str) -> bool:
    """현재 URL이 로그인 요구 화면인가 (빈 화면/이동 실패도 로그아웃으로 간주)"""
    if not url or url.startswith("about:") or url.startswith("chrome-error"):
        return True
    low = url.lower()
    return any(h.lower() in low for h in LOGGED_OUT_URL_HINTS.get(platform, ["login"]))


def _extract_cookies(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, dict):
        return list(data.get("cookies", []) or [])
    if isinstance(data, list):
        return data
    return []


def _read_cookie_file(path: Path) -> List[Dict[str, Any]]:
    try:
        if path.exists() and path.stat().st_size > 20:
            with open(path, "r", encoding="utf-8") as f:
                return _extract_cookies(json.load(f))
    except Exception:
        pass
    return []


def _backup_path(session_file: Path) -> Path:
    return session_file.parent / "session_backups" / f"{session_file.stem}.good.json"


def _log_path(session_file: Path) -> Path:
    return session_file.parent / "session_integrity_log.jsonl"


def log_event(session_file: Path, platform: str, event: str, **extra: Any) -> None:
    """쿠키/로그인 상태 변화를 시간별로 기록 (언제 풀렸는지 추적용)"""
    try:
        rec = {"ts": datetime.now().isoformat(timespec="seconds"), "platform": platform, "event": event}
        rec.update(extra)
        lp = _log_path(session_file)
        # 로그 비대 방지: 2MB 넘으면 절반으로 절단
        if lp.exists() and lp.stat().st_size > 2 * 1024 * 1024:
            lines = lp.read_text(encoding="utf-8").splitlines()
            lp.write_text("\n".join(lines[len(lines) // 2:]) + "\n", encoding="utf-8")
        with open(lp, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _atomic_write(path: Path, cookies: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"cookies": cookies}, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def safe_save(platform: str, session_file: Path, cookies: List[Dict[str, Any]], reason: str = "") -> bool:
    """
    인증 쿠키가 실제로 있을 때만 세션 파일을 저장하고 '마지막 정상본'을 백업한다.
    로그아웃 상태 쿠키로는 절대 덮어쓰지 않는다. 저장했으면 True.
    """
    session_file = Path(session_file)
    if not has_auth(platform, cookies):
        log_event(session_file, platform, "save_skipped_no_auth", reason=reason, n=len(cookies or []))
        return False
    try:
        _atomic_write(session_file, cookies)
        bp = _backup_path(session_file)
        bp.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(session_file, bp)
        log_event(session_file, platform, "saved_ok", reason=reason, n=len(cookies))
        return True
    except Exception as e:
        log_event(session_file, platform, "save_error", error=str(e))
        return False


def sanitize_for_playwright(cookies: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Playwright add_cookies 규격 정제 (__Host-/__Secure- 규칙, 만료 쿠키 제거)"""
    now = time.time()
    out: List[Dict[str, Any]] = []
    for c in cookies or []:
        if not isinstance(c, dict) or not c.get("name") or c.get("value") is None:
            continue
        exp = c.get("expires", c.get("expirationDate"))
        if isinstance(exp, (int, float)) and exp > 0 and exp < now:
            continue  # 이미 만료된 쿠키는 주입하지 않음
        name = str(c["name"])
        domain = c.get("domain") or ""
        item: Dict[str, Any] = {"name": name, "value": str(c["value"])}
        if name.startswith("__Host-"):
            host = domain.lstrip(".") or "www.google.com"
            item["url"] = f"https://{host}/"
            item["secure"] = True
        else:
            item["domain"] = domain
            item["path"] = c.get("path") or "/"
            item["secure"] = bool(c.get("secure", name.startswith("__Secure-")))
            if name.startswith("__Secure-"):
                item["secure"] = True
            if not domain:
                continue
        if "httpOnly" in c:
            item["httpOnly"] = bool(c["httpOnly"])
        ss = str(c.get("sameSite", "")).strip().lower()
        if ss == "strict":
            item["sameSite"] = "Strict"
        elif ss in ("lax", "unspecified"):
            item["sameSite"] = "Lax"
        elif ss in ("none", "no_restriction"):
            item["sameSite"] = "None"
            item["secure"] = True
        if isinstance(exp, (int, float)) and exp > 0:
            item["expires"] = float(exp)
        out.append(item)
    return out


def load_best_cookies(platform: str, session_file: Path) -> List[Dict[str, Any]]:
    """세션 파일 -> (인증쿠키 없으면) 마지막 정상 백업 순으로 쓸 만한 쿠키를 반환"""
    session_file = Path(session_file)
    cur = _read_cookie_file(session_file)
    if has_auth(platform, cur):
        return cur
    bak = _read_cookie_file(_backup_path(session_file))
    if has_auth(platform, bak):
        return bak
    return []


async def ensure_auth_cookies(platform: str, context: Any, session_file: Path) -> Dict[str, Any]:
    """
    프로필(context)에 인증 쿠키가 있으면 그대로 두고(회전된 최신 쿠키 보호),
    없을 때만 저장본/정상 백업에서 정제해 주입한다.
    반환: {"had_auth": bool, "restored": bool, "n_injected": int}
    """
    session_file = Path(session_file)
    try:
        live = await context.cookies()
    except Exception:
        live = []
    if has_auth(platform, live):
        log_event(session_file, platform, "profile_auth_ok", n=len(live))
        return {"had_auth": True, "restored": False, "n_injected": 0}

    saved = load_best_cookies(platform, session_file)
    if not saved:
        log_event(session_file, platform, "no_auth_anywhere", n_live=len(live))
        return {"had_auth": False, "restored": False, "n_injected": 0}

    injected = 0
    for c in sanitize_for_playwright(saved):
        try:
            await context.add_cookies([c])  # 하나씩 주입: 한 개 실패가 전체를 막지 않도록
            injected += 1
        except Exception:
            pass
    try:
        after = await context.cookies()
    except Exception:
        after = []
    restored = has_auth(platform, after)
    log_event(session_file, platform, "restored" if restored else "restore_failed", n_injected=injected)
    return {"had_auth": False, "restored": restored, "n_injected": injected}


async def save_if_logged_in(platform: str, context: Any, session_file: Path, reason: str = "") -> bool:
    """브라우저 종료 직전 호출: 로그인된 상태일 때만 저장"""
    try:
        cookies = await context.cookies()
    except Exception:
        return False
    return safe_save(platform, Path(session_file), cookies, reason=reason)
