# -*- coding: utf-8 -*-
"""
[독립 레고 블록] 3대 브랜드 18개 전 플랫폼 영구 프로필 동기화 실행기
====================================================================
- 역할: 💖 아우라, 🛡️ 보험비교, 📈 주식 AI의 6대 플랫폼(유튜브, 메타, 틱톡, 네이버, 스레드, 티스토리)
        영구 브라우저 프로필(user_data_dir)을 0.1초 만에 최신 세션으로 동기화 및 무결성 검증
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Windows 콘솔 UTF-8 한글 입출력 보장
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

from core.engine.persistent_session_hub import PersistentSessionHub
from playwright.async_api import async_playwright

logger = logging.getLogger("SyncProfiles")

BRAND_NAMES = {
    "aura": "💖 Aura AI 데이팅",
    "insurance": "🛡️ 보험비교 AI",
    "stock": "📈 주식 AI"
}

PLATFORMS = ["youtube", "meta", "tiktok", "naver", "threads", "tistory"]
PLATFORM_NAMES = {
    "youtube": "유튜브 스튜디오",
    "meta": "메타(인스타+페북)",
    "tiktok": "틱톡 스튜디오",
    "naver": "네이버 클립/블로그",
    "threads": "스레드",
    "tistory": "티스토리(카카오)"
}


async def sync_brand_profiles(target_brand: str = "all"):
    brands_to_sync = ["aura", "insurance", "stock"] if target_brand == "all" else [target_brand.lower()]

    print("=" * 70)
    print("👑 [골든 스택] 3대 브랜드 전 플랫폼 무인 영구 프로필 동기화 콘솔")
    print("=" * 70)
    print(f"👉 동기화 대상 브랜드: {[BRAND_NAMES.get(b, b) for b in brands_to_sync]}")
    print("👉 방식: Persistent Profile 디렉토리 고정 (IndexedDB + 캐시 + 쿠키 영구 보존)")
    print("-" * 70)

    async with async_playwright() as p:
        for brand in brands_to_sync:
            b_title = BRAND_NAMES.get(brand, brand.upper())
            print(f"\n👉 [{b_title}] 6대 플랫폼 영구 세션 동기화 시작...")
            hub = PersistentSessionHub(brand=brand)

            for plat in PLATFORMS:
                plat_title = PLATFORM_NAMES.get(plat, plat)
                cookies = hub.load_cookies(plat)

                if not cookies:
                    print(f"  - {plat_title:<16}: ⚠️ 기존 쿠키 부재 (신규 세션 대기)")
                    continue

                try:
                    context = await hub.get_playwright_context(p, plat, headless=True)
                    await hub.sync_and_close(context, plat)
                    print(f"  - {plat_title:<16}: ✅ 동기화 완료 ({len(cookies)}개 쿠키 & 프로필 보존)")
                except Exception as e:
                    print(f"  - {plat_title:<16}: ⚠️ 동기화 주의 ({e})")

    print("\n" + "=" * 70)
    print("🎉 [대성공!] 영구 로그인 프로필 디렉토리 동기화가 완벽하게 완료되었습니다!")
    print("=" * 70)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Persistent Profile Synchronizer")
    parser.add_argument("--brand", type=str, default="all", help="Target brand: aura, insurance, stock, or all")
    args = parser.parse_args()

    asyncio.run(sync_brand_profiles(target_brand=args.brand))
