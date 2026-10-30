# -*- coding: utf-8 -*-
"""
[독립 레고 블록] Session Integrity (영구 로그인 무결성 보호막) v2
=====================================================================
v2 개정 (감사 피드백 반영):
  - AUTH_RULES에 deny(추적 쿠키 구조적 배제) 계층 추가 → TSID/_T_ID 등 오탐 원천 차단
  - has_auth를 증거 등급(strict/weak) 판정으로 분리, 저장/복원 정책과 결합 해소
  - safe_save: strict 증거만 저장 / ensure_auth_cookies: weak라도 백업 우선 시도
  - 24h 무인 가동 안전장치: 타임아웃 상한, 재시도 상한, 백업 실패 폴백, 락, 행 감지

원칙: 이 모듈은 어떤 브랜드/플랫폼 코드에도 의존하지 않는다 (각 퍼블리셔가 호출만 한다).
"""

import asyncio
import json
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

# ---------------------------------------------------------------------------
# 인증 규칙: require(강한 증거) / weak(약한 증거) / deny(구조적 배제)
#  - deny에 걸린 이름은 require/weak와 겹쳐도 무조건 불인정
#  - 추적 쿠키(TSID, _T_ID 등)는 deny로 이중 차단
# ---------------------------------------------------------------------------
AUTH_RULES: Dict[str, Dict[str, Any]] = {
    "meta": {"complex": True, "deny": ["_T_ID", "TSID"]},
    "tiktok": {"any_of": ["sessionid", "sessionid_ss", "sid_tt"], "deny": ["ttwid", "msToken"]},
    "youtube": {"any_of": ["SID", "__Secure-1PSID", "__Secure-3PSID"], "deny": ["VISITOR_INFO1_LIVE"]},
    "google": {"any_of": ["SID", "__Secure-1PSID", "__Secure-3PSID"], "deny": ["NID"]},
    "naver": {"all_of": ["NID_AUT", "NID_SES"], "deny": ["NID_JST"]},
    "tistory": {"any_of": ["TSSESSION", "_kawlt"], "deny": ["TSID", "_T_ID", "_T_ANO"]},
    "brunch": {"any_of": ["bid", "b_s_a_l", "_maldive_oauth_webapp_session_key"], "deny": ["TSID", "_T_ID", "_T_ANO"]},
    "threads": {"any_of": ["sessionid"], "deny": ["_T_ID"]},
    "instagram": {"any_of": ["sessionid"], "deny": ["_T_ID"]},
}

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

# 24h 무인 가동 안전 상수
RESTORE_TIMEOUT_SEC = 15.0     # 백업 복원 전체 상한
INJECT_TIMEOUT_SEC = 3.0       # 쿠키 1개 주입 상한
MAX_INJECT_RETRY = 2           # 쿠키 1개당 재시도 상한
LOCK_STALE_SEC = 300           # 락 파일 좀비 판정(5분)


def _names(cookies: Iterable[Dict[str, Any]]) -> set:
    return {str(c.get("name")) for c in (cookies or []) if isinstance(c, dict)}


def _deny_names(platform: str) -> set:
    rule = AUTH_RULES.get(platform) or {}
    return set(rule.get("deny", []) or [])


def has_auth(platform: str, cookies: Iterable[Dict[str, Any]]) -> bool:
    """하위 호환: strict 증거 존재 여부"""
    return auth_grade(platform, cookies) == "strict"


def auth_grade(platform: str, cookies: Iterable[Dict[str, Any]]) -> str:
    """
    증거 등급 반환: 'strict' | 'weak' | 'none'
      - deny에 걸린 이름만 있으면 무조건 'none' (구조적 배제)
      - require 규칙 충족 시 'strict'
      - deny 아닌 쿠키가 존재하나 require 미충족이면 'weak'
    """
    cookies = list(cookies or [])
    if not cookies:
        return "none"
    names = _names(cookies)
    deny = _deny_names(platform)
    # deny만 있는 경우 → 인증 증거 아님
    if deny and names and names.issubset(deny):
        return "none"

    rule = AUTH_RULES.get(platform)
    if not rule:
        return "strict" if cookies else "none"

    if platform == "meta":
        has_fb = ("c_user" in names and "xs" in names)
        has_ig = ("sessionid" in names)
        return "strict" if (has_fb or has_ig) else "weak"

    if "all_of" in rule:
        if all(n in names for n in rule["all_of"]):
            return "strict"
    if "any_of" in rule:
        if any(n in names for n in rule["any_of"]):
            return "strict"
    return "weak"


def is_logged_out_url(platform: str, url: str) -> bool:
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


def _lock_path(session_file: Path) -> Path:
    return session_file.parent / f".{session_file.stem}.lock"


def _acquire_lock(session_file: Path) -> bool:
    """좀비 락 회수 포함 락 획득 (24h 무인 가동 안전장치)"""
    lp = _lock_path(session_file)
    try:
        lp.parent.mkdir(parents=True, exist_ok=True)
        if lp.exists():
            age = time.time() - lp.stat().st_mtime
            if age > LOCK_STALE_SEC:
                try:
                    lp.unlink()
                except Exception:
                    pass
            else:
                return False
        lp.write_text(str(os.getpid()), encoding="utf-8")
        return True
    except Exception:
        return False


def _release_lock(session_file: Path) -> None:
    try:
        _lock_path(session_file).unlink()
    except Exception:
        pass


def log_event(session_file: Path, platform: str, event: str, **extra: Any) -> None:
    try:
        rec = {"ts": datetime.now().isoformat(timespec="seconds"), "platform": platform, "event": event}
        rec.update(extra)
        lp = _log_path(session_file)
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
    strict 증거가 있을 때만 저장 + 골든 백업. weak/none은 절대 원본·백업 불변.
    """
    session_file = Path(session_file)
    grade = auth_grade(platform, cookies)
    if grade != "strict":
        log_event(session_file, platform, "save_skipped_no_strict_auth",
                  reason=reason, grade=grade, n=len(cookies or []))
        return False
    if not _acquire_lock(session_file):
        log_event(session_file, platform, "save_skipped_locked", reason=reason)
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
    finally:
        _release_lock(session_file)


def sanitize_for_playwright(cookies: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    now = time.time()
    out: List[Dict[str, Any]] = []
    for c in cookies or []:
        if not isinstance(c, dict) or not c.get("name") or c.get("value") is None:
            continue
        exp = c.get("expires", c.get("expirationDate"))
        if isinstance(exp, (int, float)) and exp > 0 and exp < now:
            continue
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
    """strict 우선, 없으면 weak 백업도 반환 (복원 정책은 상위에서 결정)"""
    session_file = Path(session_file)
    cur = _read_cookie_file(session_file)
    if auth_grade(platform, cur) == "strict":
        return cur
    bak = _read_cookie_file(_backup_path(session_file))
    if auth_grade(platform, bak) in ("strict", "weak"):
        return bak
    return []


async def _inject_one(context: Any, c: Dict[str, Any]) -> bool:
    for _ in range(MAX_INJECT_RETRY):
        try:
            await asyncio.wait_for(context.add_cookies([c]), timeout=INJECT_TIMEOUT_SEC)
            return True
        except asyncio.TimeoutError:
            continue
        except Exception:
            return False
    return False


async def ensure_auth_cookies(platform: str, context: Any, session_file: Path) -> Dict[str, Any]:
    """
    strict 증거가 라이브에 있으면 그대로 유지.
    없으면 백업 우선 시도(weak라도), 타임아웃·재시도 상한·폴백으로 무인 안전 확보.
    반환: {"had_auth": bool, "restored": bool, "n_injected": int, "grade": str}
    """
    session_file = Path(session_file)
    try:
        live = await asyncio.wait_for(context.cookies(), timeout=RESTORE_TIMEOUT_SEC)
    except Exception:
        live = []
    grade_live = auth_grade(platform, live)
    if grade_live == "strict":
        log_event(session_file, platform, "profile_auth_ok", n=len(live))
        return {"had_auth": True, "restored": False, "n_injected": 0, "grade": "strict"}

    saved = load_best_cookies(platform, session_file)
    if not saved:
        log_event(session_file, platform, "no_auth_anywhere", n_live=len(live))
        return {"had_auth": False, "restored": False, "n_injected": 0, "grade": grade_live}

    async def _do_restore() -> int:
        injected = 0
        for c in sanitize_for_playwright(saved):
            if await _inject_one(context, c):
                injected += 1
        return injected

    try:
        injected = await asyncio.wait_for(_do_restore(), timeout=RESTORE_TIMEOUT_SEC)
    except asyncio.TimeoutError:
        log_event(session_file, platform, "restore_timeout")
        return {"had_auth": False, "restored": False, "n_injected": 0, "grade": grade_live}
    except Exception as e:
        log_event(session_file, platform, "restore_error", error=str(e))
        return {"had_auth": False, "restored": False, "n_injected": 0, "grade": grade_live}

    try:
        after = await asyncio.wait_for(context.cookies(), timeout=RESTORE_TIMEOUT_SEC)
    except Exception:
        after = []
    grade_after = auth_grade(platform, after)
    restored = grade_after == "strict"
    log_event(session_file, platform, "restored" if restored else "restore_failed",
              n_injected=injected, grade=grade_after)
    return {"had_auth": False, "restored": restored, "n_injected": injected, "grade": grade_after}


async def save_if_logged_in(platform: str, context: Any, session_file: Path, reason: str = "") -> bool:
    try:
        cookies = await asyncio.wait_for(context.cookies(), timeout=RESTORE_TIMEOUT_SEC)
    except Exception:
        return False
    return safe_save(platform, Path(session_file), cookies, reason=reason)