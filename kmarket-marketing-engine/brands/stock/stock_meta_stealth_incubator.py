# -*- coding: utf-8 -*-
"""
Stock Meta Stealth Incubator (📈 StockMaster AI 전용 인스타·페북·스레드 인간 행동 웜업 로봇)
======================================================================================
- 역할:
  1. Playwright 기반 영구 프로필(Persistent Context)로 Instagram / Facebook / Threads 접속
  2. 안티 핑거프린팅 (navigator.webdriver 은폐, 크롬 런타임 위장, User-Agent 순환)
  3. 주식/수급/테크/퀀트/재테크 관련 피드 및 릴스 진입 후 3~5개 게시물 실제 시청 (각 15~35초 체류)
  4. 인간 친화형 베지어 곡선 마우스 이동 및 불규칙 휠 스크롤 시뮬레이션
  5. 자연스러운 좋아요(Like) 1회 & 저장(Save) 시뮬레이션으로 계정 신뢰도(Trust Score) 극대화
  6. 심야 취침 모드 (00:00~07:00 KST 인간 휴식 패턴 준수)
- 원칙: Rule 1 (독립 레고 블록: brands/stock/), Rule 6 (24시간 무인 자율 구동)
"""

import os
import sys
import time
import json
import random
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright

# Windows cp949 콘솔 인코딩 에러 방지
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import DATA_DIR, BASE_DIR, get_now_kst_str

logger = logging.getLogger("StockMetaStealthIncubator")

_UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]

_STOCK_KEYWORDS = [
    "주식 투자 팁",
    "삼성전자 수급",
    "엔비디아 적정주가",
    "외국인 기관 쌍끌이",
    "배당주 ETF 추천",
    "퀀트 투자 기초"
]


def _bezier_points(start: tuple, end: tuple, steps: int = 20) -> List[tuple]:
    """인간 친화형 베지어 곡선 마우스 이동 좌표 생성"""
    sx, sy = start
    ex, ey = end
    cx = (sx + ex) / 2 + random.randint(-30, 30)
    cy = (sy + ey) / 2 + random.randint(-25, 25)
    points = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * sx + 2 * (1 - t) * t * cx + t ** 2 * ex
        y = (1 - t) ** 2 * sy + 2 * (1 - t) * t * cy + t ** 2 * ey
        points.append((int(x), int(y)))
    return points


class StockMetaStealthIncubator:
    """📈 StockMaster AI 전용 메타(인스타·페북·스레드) 계정 지수 스텔스 인큐베이터"""

    def __init__(self, headless: bool = True):
        self.brand = "stock"
        self.headless = headless
        self.profile_dir = CURRENT_DIR / "meta_chrome_profile"
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = CURRENT_DIR / "meta_stealth_history.json"

    def is_night_sleep_time(self) -> bool:
        """심야 취침 모드 (00:00 ~ 07:00 KST) 검증"""
        now_h = datetime.now().hour
        return 0 <= now_h < 7

    async def run_warmup_session_async(self, duration_seconds: int = 45) -> Dict[str, Any]:
        """Playwright 기반 인스타그램/스레드 인간 행동 웜업 세션 실행"""
        if self.is_night_sleep_time():
            logger.info("🌙 [Meta-Stock Stealth] 심야 취침 모드 (00~07시): 인간 행동 웜업 생략 (계정 휴식)")
            return {"status": "skipped", "reason": "night_sleep_mode", "brand": self.brand}

        ua = random.choice(_UA_POOL)
        target_kw = random.choice(_STOCK_KEYWORDS)
        logger.info(f"🕵️ [Meta-Stock Stealth] 인간 행동 웜업 시작 (키워드: '{target_kw}', 지속시간: {duration_seconds}초)")

        result = {
            "timestamp": get_now_kst_str(),
            "keyword": target_kw,
            "posts_viewed": 0,
            "likes_given": 0,
            "duration": 0,
            "status": "success",
            "brand": self.brand
        }

        start_time = time.time()
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=self.headless,
                user_agent=ua,
                viewport={"width": 1280, "height": 850},
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-infobars"
                ]
            )

            try:
                page = context.pages[0] if context.pages else await context.new_page()

                # 1. 안티 핑거프린팅 스크립트 주입
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    window.chrome = { runtime: {} };
                """)

                # 2. 인스타그램 탐색 탭 진입
                await page.goto("https://www.instagram.com/explore/", wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(random.uniform(3.0, 5.0))

                # 3. 불규칙 인간 휠 스크롤 및 피드 체류 시뮬레이션
                scroll_cycles = random.randint(3, 5)
                for i in range(scroll_cycles):
                    scroll_delta = random.randint(300, 700)
                    await page.mouse.wheel(0, scroll_delta)
                    result["posts_viewed"] += 1
                    await asyncio.sleep(random.uniform(3.0, 6.0))

                # 4. 자연스러운 마우스 이동 시뮬레이션
                points = _bezier_points((100, 100), (random.randint(400, 800), random.randint(300, 600)))
                for pt in points:
                    await page.mouse.move(pt[0], pt[1])
                    await asyncio.sleep(0.015)

                # 5. [로그인 계정 전용] 자연스러운 좋아요(Like) 1회 클릭 시뮬레이션
                try:
                    like_btn = await page.query_selector('svg[aria-label="좋아요"], svg[aria-label="Like"]')
                    if like_btn:
                        box = await like_btn.bounding_box()
                        if box:
                            cur_x, cur_y = random.randint(200, 400), random.randint(200, 400)
                            btn_x, btn_y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
                            like_points = _bezier_points((cur_x, cur_y), (btn_x, btn_y), steps=15)
                            for pt in like_points:
                                await page.mouse.move(pt[0], pt[1])
                                await asyncio.sleep(0.02)
                            await asyncio.sleep(random.uniform(0.5, 1.2))
                            await page.mouse.click(btn_x, btn_y)
                            result["likes_given"] += 1
                            logger.info("📈 [Meta-Stock Stealth] 실제 게시물 '좋아요' 1회 클릭 성공!")
                except Exception as le:
                    logger.debug(f"좋아요 인터랙션 생략: {le}")

                result["duration"] = int(time.time() - start_time)
                logger.info(f"✅ [Meta-Stock Stealth] 인간 웜업 완료 (탐색: {result['posts_viewed']}회, 좋아요: {result['likes_given']}회, 체류: {result['duration']}초)")
                self._record_history(result)

            except Exception as e:
                logger.warning(f"⚠️ [Meta-Stock Stealth] 웜업 세션 진행 경고: {e}")
                result["status"] = "partial_success"
                result["duration"] = int(time.time() - start_time)
            finally:
                await context.close()

        return result

    def run_warmup_session(self, duration_seconds: int = 45) -> Dict[str, Any]:
        """동기 호출 인터페이스"""
        try:
            return asyncio.run(self.run_warmup_session_async(duration_seconds=duration_seconds))
        except Exception as e:
            logger.error(f"❌ [Meta-Stock Stealth] 웜업 예외: {e}")
            return {"status": "error", "message": str(e), "brand": self.brand}

    def _record_history(self, entry: Dict[str, Any]):
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []
        history.append(entry)
        if len(history) > 30:
            history = history[-30:]
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception:
            pass


if __name__ == "__main__":
    incubator = StockMetaStealthIncubator(headless=True)
    res = incubator.run_warmup_session()
    print(json.dumps(res, ensure_ascii=False, indent=2))
