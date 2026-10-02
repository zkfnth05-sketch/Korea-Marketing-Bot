# -*- coding: utf-8 -*-
"""
Insurance Daily Human Routine (🛡️ 보험 리밸런스 전용 하루 30분 인간 행동 & 3회 좋아요 자동화 모듈)
======================================================================================
- 역할:
  1. 업로드 직전 15초 땜질 대신, 하루 총 30분을 4개 일과 시간(08:30, 12:30, 15:30, 21:30)으로 분할
  2. 인스타그램 · 스레드 · 페이스북 · 유튜브 4대 플랫폼에서 실제 사람처럼 체류 및 시청
  3. 플랫폼별 자연스러운 좋아요 총 3회 (아침 인스타 1회, 점심 유튜브 1회, 야간 인스타/스레드 1회)
  4. Gemini AI 호출 0회 (순수 파이썬 + Playwright 스텔스 브라우저 구동, API 비용 0원)
  5. 계정 신뢰 지수(Trust Score)를 극대화하여 0뷰 섀도우밴 및 10회 컷오프를 원천 돌파
- 원칙: Rule 1 (독립 레고 블록: brands/insurance/), Rule 6 (24시간 무인 자율 구동)
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

from config import BASE_DIR, get_now_kst_str

logger = logging.getLogger("InsuranceDailyHumanRoutine")

_UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]

_INSURANCE_KEYWORDS = [
    "실손보험 전환 팁",
    "4세대 실손 장단점",
    "보험료 다이어트",
    "암보험 가입 요령",
    "3대 질병 진단비",
    "치아보험 가성비 비교",
    "운전자보험 필수 특약",
    "과다보험료 줄이는 법"
]


def _bezier_points(start: tuple, end: tuple, steps: int = 15) -> List[tuple]:
    """자연스러운 인간 마우스 베지어 이동 곡선"""
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


class InsuranceDailyHumanRoutine:
    """🛡️ 보험 리밸런스 하루 30분 일상 행동(4회 분할 & 좋아요 3회) 관제 엔진"""

    SLOTS = [
        {"id": "morning", "time": "08:30", "name": "🌅 아침 출근길 (7분)", "target_min": 7, "give_like": True, "like_platform": "instagram"},
        {"id": "lunch", "time": "12:30", "name": "🍱 점심시간 (8분)", "target_min": 8, "give_like": True, "like_platform": "youtube"},
        {"id": "afternoon", "time": "15:30", "name": "☕ 오후 티타임 (7분)", "target_min": 7, "give_like": False, "like_platform": None},
        {"id": "night", "time": "21:30", "name": "🌙 야간 침대 휴식 (8분)", "target_min": 8, "give_like": True, "like_platform": "instagram"}
    ]

    def __init__(self, headless: bool = True):
        self.brand = "insurance"
        self.brand_name = "🛡️ 보험 리밸런스"
        self.headless = headless
        self.meta_profile_dir = CURRENT_DIR / "meta_chrome_profile"
        self.meta_profile_dir.mkdir(parents=True, exist_ok=True)
        self.youtube_profile_dir = CURRENT_DIR / "youtube_chrome_profile"
        self.youtube_profile_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = CURRENT_DIR / "daily_human_routine_history.json"

    def is_sleep_time(self) -> bool:
        now = datetime.now()
        return (now.hour == 0 and now.minute < 30) or (0 <= now.hour < 7) or (now.hour == 7 and now.minute < 30)

    async def _simulate_instagram_activity(self, page, duration_sec: int, give_like: bool) -> Dict[str, Any]:
        result = {"posts_viewed": 0, "likes": 0, "platform": "instagram"}
        start_t = time.time()

        try:
            logger.info("📸 [Insurance Routine] 인스타그램(https://www.instagram.com/explore/) 진입 중...")
            await page.goto("https://www.instagram.com/explore/", wait_until="domcontentloaded", timeout=40000)
            await asyncio.sleep(random.uniform(3.5, 6.0))

            while (time.time() - start_t) < duration_sec:
                scroll_amount = random.randint(350, 750)
                await page.mouse.wheel(0, scroll_amount)
                result["posts_viewed"] += 1

                p_start = (random.randint(150, 400), random.randint(200, 450))
                p_end = (random.randint(450, 800), random.randint(350, 650))
                for pt in _bezier_points(p_start, p_end, steps=12):
                    await page.mouse.move(pt[0], pt[1])
                    await asyncio.sleep(0.015)

                dwell = random.uniform(4.0, 9.0)
                await asyncio.sleep(dwell)

                if give_like and result["likes"] == 0 and (time.time() - start_t) > 20:
                    try:
                        like_btn = await page.query_selector('svg[aria-label="좋아요"], svg[aria-label="Like"]')
                        if like_btn:
                            box = await like_btn.bounding_box()
                            if box:
                                btn_x = box["x"] + box["width"] / 2
                                btn_y = box["y"] + box["height"] / 2
                                for pt in _bezier_points(p_end, (btn_x, btn_y), steps=12):
                                    await page.mouse.move(pt[0], pt[1])
                                    await asyncio.sleep(0.02)
                                await asyncio.sleep(random.uniform(0.6, 1.4))
                                await page.mouse.click(btn_x, btn_y)
                                result["likes"] += 1
                                logger.info("🛡️ [Insurance Routine] 재테크/보험 정보 게시물 실제 '좋아요' 1회 성공!")
                                await asyncio.sleep(random.uniform(2.0, 4.0))
                    except Exception as le:
                        logger.debug(f"인스타 좋아요 시도 스킵: {le}")

        except Exception as e:
            logger.warning(f"인스타그램 루틴 예외: {e}")

        return result

    async def _simulate_threads_activity(self, page, duration_sec: int) -> Dict[str, Any]:
        result = {"posts_viewed": 0, "platform": "threads"}
        start_t = time.time()
        try:
            logger.info("🧵 [Insurance Routine] 스레드(https://www.threads.net) 재테크 정보 둘러보기...")
            await page.goto("https://www.threads.net", wait_until="domcontentloaded", timeout=40000)
            await asyncio.sleep(random.uniform(3.0, 5.0))

            while (time.time() - start_t) < duration_sec:
                await page.mouse.wheel(0, random.randint(300, 600))
                result["posts_viewed"] += 1
                await asyncio.sleep(random.uniform(3.0, 7.0))
        except Exception as e:
            logger.debug(f"스레드 루틴 스킵/예외: {e}")
        return result

    async def _simulate_youtube_activity(self, page, duration_sec: int, give_like: bool) -> Dict[str, Any]:
        result = {"shorts_watched": 0, "likes": 0, "platform": "youtube"}
        start_t = time.time()
        kw = random.choice(_INSURANCE_KEYWORDS)

        try:
            logger.info(f"🎬 [Insurance Routine] 유튜브 쇼츠 탐색 중... (키워드: '{kw}')")
            search_url = f"https://www.youtube.com/results?search_query={kw}&sp=CAISAhAB"
            await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(random.uniform(3.0, 5.0))

            await page.goto("https://www.youtube.com/shorts", wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(random.uniform(2.5, 4.5))

            while (time.time() - start_t) < duration_sec:
                watch_time = random.uniform(18.0, 32.0)
                logger.info(f"👀 [Insurance Routine] 쇼츠 영상 완시청 중... (체류: {watch_time:.1f}초)")
                await asyncio.sleep(watch_time)
                result["shorts_watched"] += 1

                if give_like and result["likes"] == 0:
                    try:
                        like_btn = await page.query_selector("button[aria-label*='좋아요'], button[aria-label*='like this']")
                        if like_btn:
                            await asyncio.sleep(random.uniform(0.5, 1.2))
                            await like_btn.click()
                            result["likes"] += 1
                            logger.info("🛡️ [Insurance Routine] 유튜브 재테크 쇼츠 '좋아요' 1회 클릭 완료!")
                            await asyncio.sleep(random.uniform(1.5, 3.0))
                    except Exception as le:
                        logger.debug(f"유튜브 좋아요 시도 스킵: {le}")

                await page.keyboard.press("PageDown")
                await asyncio.sleep(random.uniform(2.0, 4.0))

        except Exception as e:
            logger.warning(f"유튜브 루틴 예외: {e}")

        return result

    async def execute_slot_session_async(self, slot: Dict[str, Any]) -> Dict[str, Any]:
        slot_name = slot.get("name", "인간 행동 세션")
        target_sec = slot.get("target_min", 7) * 60
        give_like = slot.get("give_like", False)
        like_plat = slot.get("like_platform")

        logger.info("=" * 70)
        logger.info(f"🕵️ [Insurance 1일 30분 인간 루틴] 시작: {slot_name} (목표: {slot.get('target_min')}분 | 좋아요: {'1회 예정' if give_like else '없음'})")
        logger.info("=" * 70)

        session_start = time.time()
        ua = random.choice(_UA_POOL)
        summary = {
            "timestamp": get_now_kst_str(),
            "slot_id": slot.get("id"),
            "slot_name": slot_name,
            "target_min": slot.get("target_min"),
            "actual_sec": 0,
            "likes_given": 0,
            "actions": [],
            "status": "success",
            "gemini_calls": 0,
            "brand": self.brand
        }

        # 1. 인스타그램 & 스레드
        meta_sec = int(target_sec * 0.5)
        async with async_playwright() as p:
            try:
                ctx = await p.chromium.launch_persistent_context(
                    user_data_dir=str(self.meta_profile_dir),
                    headless=self.headless,
                    user_agent=ua,
                    viewport={"width": 1280, "height": 850},
                    args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-infobars"]
                )
                page = ctx.pages[0] if ctx.pages else await ctx.new_page()
                await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

                ig_like = (give_like and like_plat == "instagram")
                ig_res = await self._simulate_instagram_activity(page, int(meta_sec * 0.7), ig_like)
                summary["actions"].append(ig_res)
                if ig_res.get("likes", 0) > 0:
                    summary["likes_given"] += ig_res["likes"]

                th_res = await self._simulate_threads_activity(page, int(meta_sec * 0.3))
                summary["actions"].append(th_res)

                await ctx.close()
            except Exception as e:
                logger.warning(f"메타 브라우저 오류: {e}")

        # 2. 유튜브
        yt_sec = int(target_sec * 0.5)
        async with async_playwright() as p:
            try:
                ctx_yt = await p.chromium.launch_persistent_context(
                    user_data_dir=str(self.youtube_profile_dir),
                    headless=self.headless,
                    user_agent=ua,
                    viewport={"width": 1280, "height": 850},
                    args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-infobars"]
                )
                page_yt = ctx_yt.pages[0] if ctx_yt.pages else await ctx_yt.new_page()
                await page_yt.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

                yt_like = (give_like and like_plat == "youtube")
                yt_res = await self._simulate_youtube_activity(page_yt, yt_sec, yt_like)
                summary["actions"].append(yt_res)
                if yt_res.get("likes", 0) > 0:
                    summary["likes_given"] += yt_res["likes"]

                await ctx_yt.close()
            except Exception as e:
                logger.warning(f"유튜브 브라우저 오류: {e}")

        elapsed_sec = int(time.time() - session_start)
        summary["actual_sec"] = elapsed_sec
        logger.info(f"✅ [Insurance 인간 루틴 완료] {slot_name} 체류: {elapsed_sec//60}분 {elapsed_sec%60}초 | 좋아요: {summary['likes_given']}회 | 제미나이: 0회")
        self._record_history(summary)
        return summary

    def execute_slot_session(self, slot_id: str) -> Dict[str, Any]:
        slot = next((s for s in self.SLOTS if s["id"] == slot_id), self.SLOTS[0])
        try:
            return asyncio.run(self.execute_slot_session_async(slot))
        except Exception as e:
            logger.error(f"❌ 루틴 실행 실패: {e}")
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
        if len(history) > 50:
            history = history[-50:]
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def get_today_routine_summary(self) -> Dict[str, Any]:
        today_str = datetime.now().strftime("%Y-%m-%d")
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                pass

        today_entries = [h for h in history if h.get("timestamp", "").startswith(today_str)]
        total_sec = sum(h.get("actual_sec", 0) for h in today_entries)
        total_likes = sum(h.get("likes_given", 0) for h in today_entries)
        completed_slots = [h.get("slot_id") for h in today_entries]

        return {
            "brand": self.brand,
            "brand_name": self.brand_name,
            "date": today_str,
            "total_minutes": round(total_sec / 60, 1),
            "target_minutes": 30,
            "total_likes": total_likes,
            "target_likes": 3,
            "completed_slots": completed_slots,
            "gemini_calls": 0,
            "is_healthy": (total_minutes >= 20 if (total_minutes := round(total_sec / 60, 1)) else False)
        }


if __name__ == "__main__":
    routine = InsuranceDailyHumanRoutine(headless=True)
    test_slot = {"id": "test", "name": "테스트 세션", "target_min": 0.5, "give_like": True, "like_platform": "instagram"}
    res = asyncio.run(routine.execute_slot_session_async(test_slot))
    print(json.dumps(res, ensure_ascii=False, indent=2))
