# -*- coding: utf-8 -*-
"""
Omni Session Heartbeat Keeper (5대 SNS + 블로그 365일 무인 영구 생명 연장 코어 엔진)
=============================================================================
- 역할:
  3개 브랜드(insurance, stock, aura) × 6대 플랫폼(YouTube, Meta MBS, TikTok, Naver Clip, Threads, Tistory)
  각 디스크 프로필 및 세션을 3시간마다 스텔스로 핑(Ping)하여
  플랫폼 보안 서버의 유휴(Inactivity) 만료 타이머를 원천 리셋하고 365일 영구 유지합니다.
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine.session_integrity import (
    has_auth, is_logged_out_url, ensure_auth_cookies, save_if_logged_in, log_event
)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("OmniSessionHeartbeat")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


PLATFORM_CONFIG = {
    "youtube": {
        "profile_dir_name": "youtube_chrome_profile",
        "ping_url": "https://studio.youtube.com/",
        "description": "YouTube Shorts (Google DBSC 토큰)"
    },
    "meta": {
        "profile_dir_name": "meta_chrome_profile",
        "ping_url": "https://business.facebook.com/latest/home",
        "description": "Meta MBS Reels (Meta 세션)"
    },
    "tiktok": {
        "profile_dir_name": "tiktok_chrome_profile",
        "ping_url": "https://www.tiktok.com/tiktokstudio/content",
        "description": "TikTok Studio (sid_tt 토큰)"
    },
    "naver": {
        "profile_dir_name": "naver_browser_profile",
        "ping_url": "https://creator.naver.com/",
        "description": "Naver Clip Creator (NID_AUT 쿠키)"
    },
    "threads": {
        "profile_dir_name": "meta_chrome_profile",
        "session_file_name": "threads_session.json",
        "ping_url": "https://www.threads.net/",
        "description": "Threads (Instagram 연동 세션)"
    }
}


class OmniSessionHeartbeatKeeper:
    """전 플랫폼 3시간 스텔스 생명 연장 코어 엔진"""

    def __init__(self, brand: str):
        self.brand = brand.lower()
        self.brand_dir = PROJECT_ROOT / "brands" / self.brand
        self.log_file = self.brand_dir / "session_heartbeat_history.json"

    def _cleanup_locks(self, profile_dir: Path):
        """SingletonLock만 제거 (SingletonCookie/Socket은 실제 Chrome 데이터라 건드리지 않음)"""
        # 실행 중인 Chrome이 있을 때 잘못 지우면 세션이 깨지므로 lockfile 만 타깃
        for fname in ["SingletonLock"]:
            lp = profile_dir / fname
            if lp.exists():
                try:
                    lp.unlink()
                except Exception:
                    pass

    def _log_heartbeat(self, platform: str, status: str, message: str):
        records = []
        if self.log_file.exists():
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    records = json.load(f)
            except Exception:
                records = []
        records.append({
            "timestamp": datetime.now().isoformat(),
            "brand": self.brand,
            "platform": platform,
            "status": status,
            "message": message
        })
        records = records[-100:]
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    async def ping_profile_platform(self, platform_key: str) -> Dict[str, Any]:
        cfg = PLATFORM_CONFIG.get(platform_key)
        if not cfg:
            return {"status": "error", "message": f"알 수 없는 플랫폼: {platform_key}"}

        prof_dir = self.brand_dir / cfg["profile_dir_name"]
        if not prof_dir.exists() or not any(prof_dir.iterdir()):
            msg = f"{cfg['description']} 프로필 부재 (1회 연동 필요)"
            self._log_heartbeat(platform_key, "skipped", msg)
            return {"status": "skipped", "message": msg}

        self._cleanup_locks(prof_dir)
        logger.info(f"[{self.brand.upper()}] {cfg['description']} 스텔스 핑 전송 시작...")

        # 플랫폼별 세션 파일 경로
        session_file = self.brand_dir / f"{platform_key}_session.json"

        try:
            async with async_playwright() as p:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(prof_dir),
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-first-run",
                        "--no-default-browser-check"
                    ],
                    viewport={"width": 1280, "height": 900},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
                )

                # 🛡️ 인증 쿠키 없을 때만 정상 백업에서 복원 (있으면 건드리지 않음)
                await ensure_auth_cookies(platform_key, context, session_file)

                page = context.pages[0] if context.pages else await context.new_page()

                await page.route(
                    "**/*.{png,jpg,jpeg,webp,gif,svg,woff,woff2,ttf,mp4,webm}",
                    lambda route: route.abort()
                )

                target_ping_url = cfg["ping_url"]
                # 🛡️ 보험비교는 인스타그램 단독 연동 계정이므로 instagram.com으로 스텔스 핑
                if platform_key == "meta" and self.brand == "insurance":
                    target_ping_url = "https://www.instagram.com/"

                try:
                    await page.goto(target_ping_url, wait_until="domcontentloaded", timeout=15000)
                    await asyncio.sleep(3.0)
                except Exception:
                    pass

                cur_url = page.url
                cookies = await context.cookies()
                # 🔑 URL이 로그인 화면이 아니고 인증 쿠키도 실제로 존재하는지 확인
                logged_in = (not is_logged_out_url(platform_key, cur_url)) and has_auth(platform_key, cookies)

                if logged_in:
                    # 정상 세션 갱신 저장
                    await save_if_logged_in(platform_key, context, session_file, reason="heartbeat_ping")
                    msg = f"세션 생명 연장 성공 (URL: {cur_url[:55]})"
                    logger.info(f"   [성공] [{self.brand.upper()}] {cfg['description']}: {msg}")
                    self._log_heartbeat(platform_key, "active", msg)
                    await context.close()
                    return {"status": "active", "message": msg}
                else:
                    # 만료 시 forensic log에도 기록
                    log_event(session_file, platform_key, "heartbeat_expired", url=cur_url[:80])
                    msg = f"세션 만료 감지 (재연동 필요, URL: {cur_url})"
                    logger.warning(f"   ⚠️ [{self.brand.upper()}] {cfg['description']}: {msg}")
                    self._log_heartbeat(platform_key, "expired", msg)
                    await context.close()
                    return {"status": "expired", "message": msg}

        except Exception as e:
            msg = f"핑 예외: {e}"
            logger.warning(f"   [에러] [{self.brand.upper()}] {cfg['description']}: {msg}")
            self._log_heartbeat(platform_key, "error", msg)
            return {"status": "error", "message": msg}

    async def ping_threads(self) -> Dict[str, Any]:
        session_file = self.brand_dir / "threads_session.json"
        prof_dir = self.brand_dir / "meta_chrome_profile"

        if not session_file.exists() and not prof_dir.exists():
            msg = "Threads 세션/프로필 부재 (1회 연동 필요)"
            self._log_heartbeat("threads", "skipped", msg)
            return {"status": "skipped", "message": msg}

        logger.info(f"[{self.brand.upper()}] Threads(스레드) 스텔스 핑 전송 시작...")

        try:
            async with async_playwright() as p:
                if prof_dir.exists() and any(prof_dir.iterdir()):
                    self._cleanup_locks(prof_dir)
                    context = await p.chromium.launch_persistent_context(
                        user_data_dir=str(prof_dir),
                        headless=True,
                        args=["--disable-blink-features=AutomationControlled"]
                    )
                elif session_file.exists():
                    browser = await p.chromium.launch(headless=True)
                    context = await browser.new_context(storage_state=str(session_file))
                else:
                    return {"status": "skipped", "message": "세션 없음"}

                page = context.pages[0] if context.pages else await context.new_page()

                await page.route(
                    "**/*.{png,jpg,jpeg,webp,gif,svg,woff,woff2,ttf,mp4,webm}",
                    lambda route: route.abort()
                )

                try:
                    await page.goto("https://www.threads.net/", wait_until="domcontentloaded", timeout=12000)
                    await asyncio.sleep(2.0)
                except Exception:
                    pass

                cur_url = page.url.lower()
                is_logged_in = "login" not in cur_url and "accounts" not in cur_url

                if is_logged_in:
                    await context.storage_state(path=str(session_file))
                    msg = "Threads 세션 생명 연장 및 storage_state 갱신 완료"
                    logger.info(f"   [성공] [{self.brand.upper()}] Threads: {msg}")
                    self._log_heartbeat("threads", "active", msg)
                    await context.close()
                    return {"status": "active", "message": msg}
                else:
                    msg = f"Threads 세션 만료 감지 (URL: {cur_url})"
                    logger.warning(f"   [주의] [{self.brand.upper()}] Threads: {msg}")
                    self._log_heartbeat("threads", "expired", msg)
                    await context.close()
                    return {"status": "expired", "message": msg}

        except Exception as e:
            msg = f"Threads 핑 예외: {e}"
            logger.warning(f"   [에러] [{self.brand.upper()}] Threads: {msg}")
            self._log_heartbeat("threads", "error", msg)
            return {"status": "error", "message": msg}

    async def ping_tistory(self) -> Dict[str, Any]:
        logger.info(f"[{self.brand.upper()}] Tistory(카카오 SSO) 스텔스 생명 연장 가동...")
        try:
            if self.brand == "insurance":
                from brands.insurance.insurance_tistory_publisher import InsuranceTistoryPublisher
                pub = InsuranceTistoryPublisher()
            elif self.brand == "stock":
                from brands.stock.stock_tistory_publisher import StockTistoryPublisher
                pub = StockTistoryPublisher()
            elif self.brand == "aura":
                from brands.aura.aura_tistory_publisher import AuraTistoryPublisher
                pub = AuraTistoryPublisher()
            else:
                return {"status": "skipped", "message": "알 수 없는 브랜드"}

            # 비동기 함수 직접 await 호출 (이벤트 루프 충돌 방지)
            if hasattr(pub, "_keep_alive_async"):
                res = await pub._keep_alive_async()
            else:
                res = pub.keep_alive_session()

            status = res.get("status", "unknown")
            msg = res.get("message", "")

            if status == "active":
                logger.info(f"   [성공] [{self.brand.upper()}] Tistory: {msg}")
                self._log_heartbeat("tistory", "active", msg)
            else:
                logger.warning(f"   [주의] [{self.brand.upper()}] Tistory: {msg}")
                self._log_heartbeat("tistory", status, msg)
            return res
        except Exception as e:
            msg = f"Tistory 생명 연장 예외: {e}"
            logger.warning(f"   [에러] [{self.brand.upper()}] Tistory: {msg}")
            self._log_heartbeat("tistory", "error", msg)
            return {"status": "error", "message": msg}

    async def run_brand_cycle(self) -> Dict[str, Any]:
        logger.info(f"\n=======================================================")
        logger.info(f"[{self.brand.upper()}] 6대 플랫폼 세션 생명 연장 파이프라인 가동")
        logger.info(f"=======================================================")

        results = {}
        results["youtube"] = await self.ping_profile_platform("youtube")
        results["meta"] = await self.ping_profile_platform("meta")
        results["tiktok"] = await self.ping_profile_platform("tiktok")
        results["naver"] = await self.ping_profile_platform("naver")
        results["threads"] = await self.ping_threads()
        results["tistory"] = await self.ping_tistory()

        active_cnt = sum(1 for r in results.values() if r.get("status") == "active")
        logger.info(f"[{self.brand.upper()}] 완료: 총 {len(results)}개 플랫폼 중 {active_cnt}개 활성 유지 성공\n")
        return {"brand": self.brand, "results": results, "active_count": active_cnt}


async def run_all_brands_cycle() -> Dict[str, Any]:
    all_res = {}
    for b in ["insurance", "stock", "aura"]:
        keeper = OmniSessionHeartbeatKeeper(brand=b)
        all_res[b] = await keeper.run_brand_cycle()
    return all_res


async def start_heartbeat_daemon(interval_hours: float = 3.0):
    interval_sec = int(interval_hours * 3600)
    logger.info(f"[OmniSessionHeartbeat] 365일 무인 영구 생명 연장 데몬 시작 (주기: {interval_hours}시간 / {interval_sec}초)")

    cycle_num = 1
    while True:
        logger.info(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 제 #{cycle_num}회차 전 플랫폼 세션 갱신 사이클 시작")
        try:
            await run_all_brands_cycle()
        except Exception as e:
            logger.error(f"사이클 실행 중 예외: {e}")

        logger.info(f"다음 사이클까지 {interval_hours}시간({interval_sec}초) 동안 백그라운드 대기합니다...\n")
        cycle_num += 1
        await asyncio.sleep(interval_sec)


if __name__ == "__main__":
    if "--daemon" in sys.argv:
        asyncio.run(start_heartbeat_daemon(interval_hours=3.0))
    elif "--brand" in sys.argv:
        idx = sys.argv.index("--brand")
        target_b = sys.argv[idx + 1] if len(sys.argv) > idx + 1 else "insurance"
        keeper = OmniSessionHeartbeatKeeper(brand=target_b)
        asyncio.run(keeper.run_brand_cycle())
    else:
        asyncio.run(run_all_brands_cycle())
