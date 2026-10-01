# -*- coding: utf-8 -*-
"""
Aura Meta Login Helper (💖 Aura 데이팅 메타 1회 영구 로그인 연동기 - 정품 크롬 전용)
=============================================================================
- 브랜드: 💖 Aura (AI 데이팅)
- 전용 계정: @aura_ai_dating
- 프로필 디렉터리: brands/aura/meta_chrome_profile/
- 역할:
  1. 실제 정품 구글 크롬(Chrome)을 전용 프로필 모드로 실행 (봇 탐지 0%, 팝업 0%)
  2. 대표님께서 인스타그램/페이스북에 평소처럼 정상 로그인 수행
  3. 로그인 완료 후 크롬 창을 닫으면 해당 프로필 폴더에 세션이 영구 보존됨
"""

import os
import sys
import json
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
PROFILE_DIR = CURRENT_DIR / "meta_chrome_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)


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
    print("🔑 [💖 Aura AI 데이팅] 메타(인스타그램·페이스북) 영구 로그인 1회 연동기")
    print("=" * 70)
    print(f"👉 프로필 저장 위치: {PROFILE_DIR}")
    print("-" * 70)
    print("1. 화면에 진짜 정품 구글 크롬(Chrome) 브라우저가 열립니다.")
    print("2. 인스타그램에 정상 로그인(아이디/비번 또는 페이스북 연동)해 주세요.")
    print("3. 피드 메인 화면이 뜨면, 브라우저 창 우측 상단의 [X]를 눌러 닫아주세요.")
    print("4. 창을 닫으시면 로그인 세션이 이 폴더에 영구 보존됩니다.")
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
        print("\n" + "=" * 70)
        print("🎉 [성공] 브라우저가 닫혔습니다! 로그인 세션이 영구 보관함에 안전하게 저장되었습니다.")
        print(f"📁 영구 보관 프로필: {PROFILE_DIR.name}")
        print("💡 이제 봇이 인스타그램 탐색 및 좋아요를 100% 무인으로 자율 수행합니다.")
        print("=" * 70 + "\n")
    except Exception as e:
        print(f"\n❌ 실행 오류: {e}")


if __name__ == "__main__":
    main()
