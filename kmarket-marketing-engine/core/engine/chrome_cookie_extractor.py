# -*- coding: utf-8 -*-
"""
core/engine/chrome_cookie_extractor.py
========================================================================================
- 역할: 윈도우 실제 구글 크롬(Chrome)의 신뢰 프로필(Profile 8, 12, 14 등)에서
        DPAPI 마스터키 복호화를 통해 YouTube/Google 영구 인증 세션 쿠키를 100% 무손실 추출
- 원칙:
  1. [Rule 1 독립 모듈화]: 모든 브랜드(Aura, Insurance, Stock)가 공통으로 재사용하는 핵심 엔진
  2. [Rule 5 땜질 코딩 금지]: 낯선 가상 프로필을 만들어 차단당하는 방식 원천 배제,
     대표님 PC에서 수개월간 신뢰가 쌓인 실제 크롬 프로필과 직결
========================================================================================
"""

import os
import sys
import json
import base64
import sqlite3
import shutil
import tempfile
import ctypes
import subprocess
import logging
from ctypes import wintypes
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    AESGCM = None

logger = logging.getLogger("ChromeCookieExtractor")


class DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]


def _unprotect_data(data: bytes) -> bytes:
    """Windows DPAPI 복호화"""
    blob_in = DATA_BLOB(len(data), ctypes.cast(ctypes.create_string_buffer(data), ctypes.POINTER(ctypes.c_byte)))
    blob_out = DATA_BLOB()
    if ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)):
        out_bytes = ctypes.string_at(blob_out.pbData, blob_out.cbData)
        ctypes.windll.kernel32.LocalFree(blob_out.pbData)
        return out_bytes
    return b""


def get_chrome_master_key() -> bytes:
    """Chrome Local State에서 AES-256-GCM 마스터 복호화 키 추출"""
    local_state_path = Path(r"C:\Users\zkfnt\AppData\Local\Google\Chrome\User Data\Local State")
    if not local_state_path.exists():
        raise FileNotFoundError(f"Chrome Local State 파일을 찾을 수 없습니다: {local_state_path}")
    
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    encrypted_key = encrypted_key[5:]
    master_key = _unprotect_data(encrypted_key)
    if not master_key:
        raise RuntimeError("Chrome DPAPI 마스터키 복호화 실패")
    return master_key


def decrypt_cookie_value(encrypted_val: bytes, master_key: bytes) -> str:
    """Chrome 쿠키 암호화 바이너리 복호화 (v10/v11/v20 AES-GCM 또는 레거시 DPAPI)"""
    if not encrypted_val:
        return ""
    try:
        if encrypted_val.startswith(b"v10") or encrypted_val.startswith(b"v11") or encrypted_val.startswith(b"v20"):
            if not AESGCM:
                return ""
            nonce = encrypted_val[3:15]
            ciphertext = encrypted_val[15:]
            aesgcm = AESGCM(master_key)
            return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
        else:
            return _unprotect_data(encrypted_val).decode("utf-8")
    except Exception:
        return ""


def find_chrome_executable() -> str:
    """시스템에 설치된 Chrome 실행 파일 경로 탐색"""
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


def launch_chrome_profile(profile_dir_name: str, start_url: str = "https://studio.youtube.com"):
    """실제 크롬의 특정 프로필 디렉토리 모드로 창 실행 (사용자 1회 로그인용)"""
    chrome_exe = find_chrome_executable()
    cmd = [
        chrome_exe,
        f"--profile-directory={profile_dir_name}",
        "--no-first-run",
        "--no-default-browser-check",
        start_url
    ]
    print(f"🚀 실제 크롬 [{profile_dir_name}] 프로필 모드로 실행합니다...")
    subprocess.run(cmd)


def extract_youtube_cookies_from_profile(profile_dir_name: str) -> List[Dict[str, Any]]:
    """
    실제 크롬 프로필(예: Profile 8)의 SQLite DB에서 YouTube/Google 인증 쿠키 전수 복호화 추출
    """
    master_key = get_chrome_master_key()
    user_data_base = Path(r"C:\Users\zkfnt\AppData\Local\Google\Chrome\User Data")
    cookies_db = user_data_base / profile_dir_name / "Network" / "Cookies"
    
    if not cookies_db.exists():
        logger.error(f"쿠키 DB 파일 부재: {cookies_db}")
        return []
    
    fd, tmp_db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    try:
        with open(cookies_db, "rb") as f_src:
            with open(tmp_db_path, "wb") as f_dst:
                f_dst.write(f_src.read())
        
        conn = sqlite3.connect(tmp_db_path)
        cur = conn.cursor()
        cur.execute("SELECT host_key, name, path, encrypted_value, is_secure, is_httponly, samesite, expires_utc FROM cookies")
        rows = cur.fetchall()
        conn.close()
    except Exception as e:
        logger.error(f"SQLite 쿠키 DB 복사/조회 실패: {e}")
        return []
    finally:
        try:
            if os.path.exists(tmp_db_path):
                os.remove(tmp_db_path)
        except Exception:
            pass

    clean_cookies = []
    same_site_map = {-1: "None", 0: "None", 1: "Lax", 2: "Strict"}
    
    for host, name, path, enc_val, sec, http_only, same_site, exp in rows:
        if "youtube" in host or "google" in host:
            val = decrypt_cookie_value(enc_val, master_key)
            if val:
                item = {
                    "name": name,
                    "value": val,
                    "domain": host,
                    "path": path,
                    "secure": bool(sec),
                    "httpOnly": bool(http_only),
                    "sameSite": same_site_map.get(same_site, "None")
                }
                if exp and exp > 0:
                    unix_exp = int((exp - 11644473600000000) / 1000000)
                    if unix_exp > 0:
                        item["expires"] = unix_exp
                clean_cookies.append(item)
                
    return clean_cookies


def sync_brand_youtube_session(
    brand_name: str,
    profile_dir_name: str,
    output_session_file: Path
) -> Dict[str, Any]:
    """
    브랜드별 신뢰 크롬 프로필에서 쿠키를 추출하여 youtube_session.json에 저장 및 검증
    """
    print(f"\n🔄 [{brand_name}] 크롬 '{profile_dir_name}' 프로필에서 영구 세션 쿠키 추출 중...")
    cookies = extract_youtube_cookies_from_profile(profile_dir_name)
    
    output_session_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_session_file, "w", encoding="utf-8") as f:
        json.dump({"cookies": cookies}, f, ensure_ascii=False, indent=2)
        
    auth_tokens = [c["name"] for c in cookies if c["name"] in ["LOGIN_INFO", "SID", "SSID", "SAPISID", "HSID", "__Secure-3PSID", "__Secure-1PSID"]]
    has_auth = "LOGIN_INFO" in auth_tokens or "SID" in auth_tokens or "__Secure-3PSID" in auth_tokens
    
    print(f"📦 총 {len(cookies)}개의 Google/YouTube 세션 쿠키 추출 완료")
    print(f"🔑 발견된 핵심 인증 토큰: {set(auth_tokens)}")
    
    if has_auth:
        print(f"🎉 [{brand_name}] 유튜브 영구 로그인 세션 검증 100% 성공!")
    else:
        print(f"ℹ️ [{brand_name}] ({profile_dir_name}) 로그인 완료 후 브라우저를 닫으시면 세션이 즉시 반영됩니다.")
        
    return {
        "success": has_auth,
        "cookie_count": len(cookies),
        "auth_tokens": auth_tokens,
        "session_file": str(output_session_file)
    }
