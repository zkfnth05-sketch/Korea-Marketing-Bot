# -*- coding: utf-8 -*-
"""
네이버 3대 브랜드 세션 고속 점검 및 미로그인 브랜드 자동 연동 팝업 런처
========================================================================================
- Aura, 보험비교, StockMaster AI의 네이버 영구 로그인 상태를 순차 점검
- 이미 로그인된 브랜드는 패스(OK)
- 만료되거나 미연동된 브랜드만 실제 브라우저 창을 띄워 QR/아이디 로그인 수행 및 영구 저장
========================================================================================
"""
import sys
import os
import asyncio
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
BRANDS_DIR = BASE_DIR / "brands"

BRANDS = [
    {
        "key": "insurance",
        "name": "🛡️ 보험 리밸런스 (InsureBalance)",
        "script": BRANDS_DIR / "insurance" / "insurance_naver_login.py",
        "profile": BRANDS_DIR / "insurance" / "naver_browser_profile",
    },
    {
        "key": "aura",
        "name": "💖 Aura AI 데이팅",
        "script": BRANDS_DIR / "aura" / "aura_naver_login.py",
        "profile": BRANDS_DIR / "aura" / "naver_browser_profile",
    },
    {
        "key": "stock",
        "name": "📈 StockMaster 주식 AI",
        "script": BRANDS_DIR / "stock" / "stock_naver_login.py",
        "profile": BRANDS_DIR / "stock" / "naver_browser_profile",
    }
]

async def check_session_valid(profile_dir: Path) -> bool:
    if not profile_dir.exists():
        return False
    for lock in ["SingletonLock", "SingletonCookie", "SingletonSocket"]:
        lp = profile_dir / lock
        if lp.exists():
            try: lp.unlink()
            except: pass

    try:
        async with async_playwright() as p:
            ctx = await p.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                headless=True,
                viewport={"width": 1280, "height": 800}
            )
            page = ctx.pages[0] if ctx.pages else await ctx.new_page()
            await page.goto("https://nid.naver.com/user2/help/myInfo?lang=ko_KR", timeout=20000)
            await asyncio.sleep(2.0)
            url = page.url
            await ctx.close()
            if "nidlogin" in url or "login" in url:
                return False
            return True
    except Exception:
        return False


def main():
    print("=" * 70)
    print("🔍 [한국 마케팅봇] 3대 브랜드 네이버 영구 로그인 자동 진단 시작...")
    print("=" * 70)

    need_login = []
    for b in BRANDS:
        print(f"👉 [{b['name']}] 세션 검증 중...", end="", flush=True)
        is_ok = asyncio.run(check_session_valid(b["profile"]))
        if is_ok:
            print(" -> ✅ [정상 유지 중]")
        else:
            print(" -> ❌ [로그인 필요 (만료 또는 미연동)]")
            need_login.append(b)

    print("-" * 70)
    if not need_login:
        print("\n🎉 축하합니다! 3대 전 브랜드 네이버 영구 로그인이 100% 완벽하게 유지되고 있습니다.")
        print("별도의 로그인이 필요하지 않습니다.\n")
        return

    print(f"\n⚠️ 총 {len(need_login)}개 브랜드의 네이버 로그인이 필요합니다.")
    print("지금부터 해당 브랜드의 로그인 창을 순서대로 화면에 띄웁니다.")
    print("스마트폰 네이버 앱의 [QR코드]로 1회 로그인해 주시면 영구 보존됩니다.\n")
    print("=" * 70)

    for idx, b in enumerate(need_login, 1):
        print(f"\n[{idx}/{len(need_login)}] {b['name']} 네이버 로그인 창 실행 중...")
        subprocess.run([sys.executable, "-u", str(b["script"])])
        print(f"✅ {b['name']} 로그인 프로세스 완료!")

    print("\n" + "=" * 70)
    print("🎉 모든 미로그인 브랜드의 네이버 영구 로그인 연동이 완료되었습니다!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
