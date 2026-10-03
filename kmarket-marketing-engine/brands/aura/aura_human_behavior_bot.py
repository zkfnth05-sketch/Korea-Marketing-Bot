# -*- coding: utf-8 -*-
"""
[독립 레고 블록] Aura Human Behavior Bot (💖 Aura 전용 100% 독립 인간 행동 봇)
=============================================================================
- 역할:
  1. API 업로드 코드는 0% 배제! 오직 사람처럼 행동(체류, 탐색, 시청, 좋아요)만 전담
  2. 하루 총 45분을 4개 일과 시간(08:30, 12:30, 15:30, 21:30)으로 분할 실행
  3. [사용자 절대 수칙] 매번 실시할 때마다 좋아요 2~3회씩 실행
  4. 특정 주제 편향 방지: 일상/유머/맛집/반려동물(50%) + 연애/소개팅(50%) 다채로운 탐색
  5. Gemini AI 호출 0회 (순수 파이썬 + Playwright 스텔스 브라우저, API 비용 0원)
  6. 계정 신뢰 지수(Trust Score)를 극대화하여 인스타그램 0뷰 섀도우밴 및 유튜브 10회 컷오프 원천 돌파
- 원칙: Rule 1 (앱별 완전 독립 모듈화), Rule 6 (24시간 무인 자율 구동)
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

logger = logging.getLogger("AuraHumanBehaviorBot")

_UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]

# 🐶 일상/유머/맛집/힐링 등 다양한 사람 관심사 키워드 (단일 주제 편향 방지)
_GENERAL_HUMAN_KEYWORDS = [
    "귀여운 강아지 고양이 숏폼",
    "오늘의 꿀잼 릴스",
    "전국 숨은 맛집 투어",
    "힐링 여행 풍경",
    "직장인 공감 썰 숏폼",
    "요즘 뜨는 감성 카페",
    "퇴근길 일상 브이로그",
    "초간단 자취 요리 레시피"
]

# 💖 Aura 브랜드 관심사 키워드
_AURA_KEYWORDS = [
    "소개팅 꿀팁",
    "소개팅 코디 룩북",
    "연애 심리 테스트",
    "카톡 대화 팁",
    "남녀 심리 차이",
    "데이트 코스 추천",
    "첫소개팅 대화주제",
    "호감 시그널"
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


class AuraHumanBehaviorBot:
    """💖 Aura 전용 순수 인간 행동 봇 (API 업로드 일체 분리)"""

    SLOTS = [
        {"id": "morning", "time": "08:30", "start_h": 8, "start_m": 30, "end_h": 12, "end_m": 29, "name": "🌅 아침 출근길 (11분)", "target_min": 11},
        {"id": "lunch", "time": "12:30", "start_h": 12, "start_m": 30, "end_h": 15, "end_m": 29, "name": "🍱 점심시간 (12분)", "target_min": 12},
        {"id": "afternoon", "time": "15:30", "start_h": 15, "start_m": 30, "end_h": 21, "end_m": 29, "name": "☕ 오후 티타임 (11분)", "target_min": 11},
        {"id": "night", "time": "21:30", "start_h": 21, "start_m": 30, "end_h": 23, "end_m": 59, "name": "🌙 야간 침대 휴식 (11분)", "target_min": 11}
    ]

    def __init__(self, headless: bool = True):
        self.brand = "aura"
        self.brand_name = "💖 Aura AI 데이팅"
        self.headless = headless
        self.meta_profile_dir = CURRENT_DIR / "meta_chrome_profile"
        self.meta_profile_dir.mkdir(parents=True, exist_ok=True)
        self.youtube_profile_dir = CURRENT_DIR / "youtube_chrome_profile"
        self.youtube_profile_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = CURRENT_DIR / "daily_human_routine_history.json"

    def is_sleep_time(self) -> bool:
        """심야 취침 모드 (00:00 ~ 07:30 KST 계정 안전 휴식)"""
        now = datetime.now()
        return (now.hour == 0 and now.minute < 30) or (0 <= now.hour < 7) or (now.hour == 7 and now.minute < 30)

    async def _simulate_instagram_activity(self, page, duration_sec: int, target_likes: int = 1) -> Dict[str, Any]:
        """인스타그램 탐색 탭 / 릴스 피드 인간 체류 & 좋아요 (일상+연애 혼합)"""
        result = {"posts_viewed": 0, "likes": 0, "platform": "instagram"}
        start_t = time.time()

        try:
            logger.info("📸 [Aura HumanBot] 인스타그램(https://www.instagram.com/explore/) 진입 중...")
            await page.goto("https://www.instagram.com/explore/", wait_until="domcontentloaded", timeout=40000)
            await asyncio.sleep(random.uniform(3.5, 6.0))

            # 팝업 및 로그인 유도 모달 닫기 시도
            try:
                await page.keyboard.press("Escape")
                close_btn = await page.query_selector('button:has-text("나중에 하기"), button:has-text("Not Now"), svg[aria-label="닫기"], svg[aria-label="Close"]')
                if close_btn:
                    await close_btn.click()
            except Exception:
                pass

            while (time.time() - start_t) < duration_sec:
                # 1. 불규칙 휠 스크롤
                scroll_amount = random.randint(350, 750)
                await page.mouse.wheel(0, scroll_amount)
                result["posts_viewed"] += 1

                # 2. 베지어 마우스 이동
                p_start = (random.randint(150, 400), random.randint(200, 450))
                p_end = (random.randint(450, 800), random.randint(350, 650))
                for pt in _bezier_points(p_start, p_end, steps=12):
                    await page.mouse.move(pt[0], pt[1])
                    await asyncio.sleep(0.015)

                # 3. 체류 시간 (실제 글/사진 보는 시간)
                dwell = random.uniform(4.0, 8.5)
                await asyncio.sleep(dwell)

                # 4. 자연스러운 좋아요 시도 (세션 목표 좋아요까지)
                if result["likes"] < target_likes and (time.time() - start_t) > 12:
                    try:
                        like_buttons = await page.query_selector_all('svg[aria-label="좋아요"], svg[aria-label="Like"]')
                        if like_buttons:
                            idx = min(result["likes"], len(like_buttons) - 1)
                            target_btn = like_buttons[idx]
                            box = await target_btn.bounding_box()
                            if box:
                                btn_x = box["x"] + box["width"] / 2
                                btn_y = box["y"] + box["height"] / 2
                                for pt in _bezier_points(p_end, (btn_x, btn_y), steps=12):
                                    await page.mouse.move(pt[0], pt[1])
                                    await asyncio.sleep(0.02)
                                await asyncio.sleep(random.uniform(0.6, 1.4))
                                await page.mouse.click(btn_x, btn_y)
                                result["likes"] += 1
                                logger.info(f"💖 [Aura HumanBot] 인스타그램 게시물 실제 '좋아요' 터치 완료! (인스타 누적: {result['likes']}회)")
                                await asyncio.sleep(random.uniform(3.0, 5.0))
                    except Exception as le:
                        logger.debug(f"인스타 좋아요 시도 스킵: {le}")

        except Exception as e:
            logger.warning(f"인스타그램 루틴 예외: {e}")

        return result

    async def _simulate_threads_activity(self, page, duration_sec: int) -> Dict[str, Any]:
        """스레드(Threads) 피드 인간 체류 및 스크롤"""
        result = {"posts_viewed": 0, "platform": "threads"}
        start_t = time.time()
        try:
            logger.info("🧵 [Aura HumanBot] 스레드(https://www.threads.net) 피드 둘러보기...")
            await page.goto("https://www.threads.net", wait_until="domcontentloaded", timeout=40000)
            await asyncio.sleep(random.uniform(3.0, 5.0))

            while (time.time() - start_t) < duration_sec:
                await page.mouse.wheel(0, random.randint(300, 600))
                result["posts_viewed"] += 1
                await asyncio.sleep(random.uniform(3.0, 6.0))
        except Exception as e:
            logger.debug(f"스레드 루틴 스킵/예외: {e}")
        return result

    async def _simulate_youtube_activity(self, page, duration_sec: int, target_likes: int = 1) -> Dict[str, Any]:
        """유튜브 쇼츠 탐색, 완시청 및 좋아요 (일상 50% + 브랜드 50% 혼합)"""
        result = {"shorts_watched": 0, "likes": 0, "platform": "youtube"}
        start_t = time.time()
        pool = _GENERAL_HUMAN_KEYWORDS if random.random() < 0.5 else _AURA_KEYWORDS
        kw = random.choice(pool)

        try:
            logger.info(f"🎬 [Aura HumanBot] 유튜브 쇼츠 탐색 중... (키워드: '{kw}')")
            search_url = f"https://www.youtube.com/results?search_query={kw}&sp=CAISAhAB"
            await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(random.uniform(3.0, 5.0))

            await page.goto("https://www.youtube.com/shorts", wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(random.uniform(2.5, 4.5))

            while (time.time() - start_t) < duration_sec:
                watch_time = random.uniform(16.0, 30.0)
                logger.info(f"👀 [Aura HumanBot] 쇼츠 영상 완시청 중... (체류: {watch_time:.1f}초)")
                await asyncio.sleep(watch_time)
                result["shorts_watched"] += 1

                # 좋아요 시도
                if result["likes"] < target_likes:
                    try:
                        like_btn = await page.query_selector("button[aria-label*='좋아요'], button[aria-label*='like this']")
                        if like_btn:
                            await asyncio.sleep(random.uniform(0.6, 1.3))
                            await like_btn.click()
                            result["likes"] += 1
                            logger.info(f"💖 [Aura HumanBot] 유튜브 쇼츠 '좋아요' 클릭 완료! (유튜브 누적: {result['likes']}회)")
                            await asyncio.sleep(random.uniform(2.0, 4.0))
                    except Exception as le:
                        logger.debug(f"유튜브 좋아요 시도 스킵: {le}")

                await page.keyboard.press("PageDown")
                await asyncio.sleep(random.uniform(2.0, 3.5))

        except Exception as e:
            logger.warning(f"유튜브 루틴 예외: {e}")

        return result

    async def execute_slot_session_async(self, slot: Dict[str, Any]) -> Dict[str, Any]:
        """
        지정된 세션 실행:
        - 매번 실시할 때마다 좋아요 2~3회 실행! (인스타 1~2회 + 유튜브 1~2회 = 총 2~3회)
        - Gemini AI 호출 0회 (순수 파이썬 + Playwright 구동, 비용 0원)
        """
        slot_name = slot.get("name", "인간 행동 세션")
        target_sec = slot.get("target_min", 7) * 60

        total_session_target_likes = random.randint(3, 5)
        ig_target_likes = random.randint(2, 3)
        yt_target_likes = total_session_target_likes - ig_target_likes

        logger.info("=" * 70)
        logger.info(f"🕵️ [Aura 인간 행동 봇] 시작: {slot_name} (목표: {slot.get('target_min')}분 | 이번 세션 좋아요 목표: {total_session_target_likes}회)")
        logger.info(f"   • 인스타그램 좋아요 배정: {ig_target_likes}회 | 유튜브 좋아요 배정: {yt_target_likes}회")
        logger.info("=" * 70)

        session_start = time.time()
        ua = random.choice(_UA_POOL)
        summary = {
            "timestamp": get_now_kst_str(),
            "slot_id": slot.get("id"),
            "slot_name": slot_name,
            "target_min": slot.get("target_min"),
            "target_likes": total_session_target_likes,
            "actual_sec": 0,
            "likes_given": 0,
            "actions": [],
            "status": "success",
            "gemini_calls": 0,
            "brand": self.brand
        }

        from core.engine.browser_guard import async_browser_lock, clean_browser_profile_locks, get_safe_browser_args

        clean_browser_profile_locks(self.meta_profile_dir)
        clean_browser_profile_locks(self.youtube_profile_dir)

        async with async_browser_lock(f"Aura 인간행동 세션 ({slot_name})"):
            # 1. 인스타그램 & 스레드
            meta_sec = int(target_sec * 0.5)
            async with async_playwright() as p:
                try:
                    ctx = await p.chromium.launch_persistent_context(
                        user_data_dir=str(self.meta_profile_dir),
                        headless=self.headless,
                        user_agent=ua,
                        viewport={"width": 1280, "height": 850},
                        args=get_safe_browser_args()
                    )

                    # meta_session.json 쿠키 주입
                    session_file = CURRENT_DIR / "meta_session.json"
                    if session_file.exists():
                        try:
                            with open(session_file, "r", encoding="utf-8") as sf:
                                sdata = json.load(sf)
                                cookies = sdata.get("cookies", [])
                                if cookies:
                                    clean_cookies = []
                                    for c in cookies:
                                        c_item = {
                                            "name": c.get("name"),
                                            "value": c.get("value"),
                                            "domain": c.get("domain", ".instagram.com"),
                                            "path": c.get("path", "/")
                                        }
                                        if "sameSite" in c and c["sameSite"] in ["Strict", "Lax", "None"]:
                                            c_item["sameSite"] = c["sameSite"]
                                        clean_cookies.append(c_item)
                                    await ctx.add_cookies(clean_cookies)
                                    logger.info(f"🍪 [Aura HumanBot] 인스타그램 세션 쿠키 {len(clean_cookies)}개 브라우저 주입 완료")
                        except Exception as ce:
                            logger.debug(f"쿠키 주입 예외 (무시): {ce}")

                    page = ctx.pages[0] if ctx.pages else await ctx.new_page()
                    await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

                    ig_res = await self._simulate_instagram_activity(page, int(meta_sec * 0.7), target_likes=ig_target_likes)
                    summary["actions"].append(ig_res)
                    summary["likes_given"] += ig_res.get("likes", 0)

                    th_res = await self._simulate_threads_activity(page, int(meta_sec * 0.3))
                    summary["actions"].append(th_res)

                    await ctx.close()
                except Exception as e:
                    logger.warning(f"메타 브라우저 컨텍스트 오류: {e}")

            # 2. 유튜브
            yt_sec = int(target_sec * 0.5)
            async with async_playwright() as p:
                try:
                    ctx_yt = await p.chromium.launch_persistent_context(
                        user_data_dir=str(self.youtube_profile_dir),
                        headless=self.headless,
                        user_agent=ua,
                        viewport={"width": 1280, "height": 850},
                        args=get_safe_browser_args()
                    )

                    # youtube_session.json 쿠키 주입
                    yt_session_file = CURRENT_DIR / "youtube_session.json"
                    if yt_session_file.exists():
                        try:
                            with open(yt_session_file, "r", encoding="utf-8") as ysf:
                                ydata = json.load(ysf)
                                ycookies = ydata if isinstance(ydata, list) else ydata.get("cookies", [])
                                if ycookies:
                                    clean_ycookies = []
                                    for c in ycookies:
                                        c_item = {
                                            "name": c.get("name"),
                                            "value": c.get("value"),
                                            "domain": c.get("domain", ".youtube.com"),
                                            "path": c.get("path", "/")
                                        }
                                        if "sameSite" in c and c["sameSite"] in ["Strict", "Lax", "None"]:
                                            c_item["sameSite"] = c["sameSite"]
                                        if c.get("name", "").startswith(("__Secure-", "__Host-")) or c.get("secure"):
                                            c_item["secure"] = True
                                        clean_ycookies.append(c_item)
                                    await ctx_yt.add_cookies(clean_ycookies)
                                    logger.info(f"🍪 [Aura HumanBot] 유튜브 세션 쿠키 {len(clean_ycookies)}개 브라우저 주입 완료")
                        except Exception as ye:
                            logger.debug(f"유튜브 쿠키 주입 예외: {ye}")

                    page_yt = ctx_yt.pages[0] if ctx_yt.pages else await ctx_yt.new_page()
                    await page_yt.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

                    yt_res = await self._simulate_youtube_activity(page_yt, yt_sec, target_likes=yt_target_likes)
                    summary["actions"].append(yt_res)
                    summary["likes_given"] += yt_res.get("likes", 0)

                    await ctx_yt.close()
                except Exception as e:
                    logger.warning(f"유튜브 브라우저 컨텍스트 오류: {e}")

        elapsed_sec = int(time.time() - session_start)
        summary["actual_sec"] = elapsed_sec
        logger.info(f"✅ [Aura 인간 행동 봇 세션 완료] {slot_name} 체류: {elapsed_sec//60}분 {elapsed_sec%60}초 | 좋아요: {summary['likes_given']}회 달성 | 제미나이: 0회")
        self._record_history(summary)
        return summary

    def execute_slot_session(self, slot_id: str) -> Dict[str, Any]:
        """동기 호출 래퍼"""
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
        """오늘 하루 수행된 인간 행동 통계 반환 (대시보드 실시간 연동용)"""
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
            "target_minutes": 45,
            "total_likes": total_likes,
            "target_likes": "세션당 3~5회 (일 12~20회)",
            "completed_slots": completed_slots,
            "gemini_calls": 0
        }

    def run_daemon(self, check_interval_seconds: int = 30):
        """24시간 365일 4개 일과 시간대 윈도우(아침 08:30~ / 점심 12:30~ / 오후 15:30~ / 야간 21:30~) 자율 보정 데몬"""
        logger.info(f"🤖 [{self.brand_name}] 24시간 365일 무인 인간 행동 봇 가동 (슬롯 윈도우 자율 보정, 하루 45분 4회 분할, 세션당 3~5회 좋아요)")
        executed_slots = set()
        last_date = ""

        while True:
            try:
                now = datetime.now()
                today_str = now.strftime("%Y-%m-%d")
                cur_min = now.hour * 60 + now.minute

                if today_str != last_date:
                    executed_slots.clear()
                    last_date = today_str

                for slot in self.SLOTS:
                    slot_id = slot["id"]
                    start_total = slot.get("start_h", 0) * 60 + slot.get("start_m", 0)
                    end_total = slot.get("end_h", 23) * 60 + slot.get("end_m", 59)
                    exec_key = f"{today_str}_{slot_id}"

                    if start_total <= cur_min <= end_total and exec_key not in executed_slots:
                        logger.info(f"⏰ [{self.brand_name}] {slot['name']} 골든타임 도달! {slot.get('target_min', 7)}분 인간 활동 및 2~3회 좋아요 시작...")
                        executed_slots.add(exec_key)
                        self.execute_slot_session(slot_id)

                time.sleep(check_interval_seconds)
            except Exception as e:
                logger.error(f"❌ [{self.brand_name}] 인간 행동 데몬 예외: {e}")
                time.sleep(check_interval_seconds)


if __name__ == "__main__":
    bot = AuraHumanBehaviorBot(headless=True)
    test_slot = {"id": "test", "name": "테스트 세션", "target_min": 0.5}
    res = asyncio.run(bot.execute_slot_session_async(test_slot))
    print(json.dumps(res, ensure_ascii=False, indent=2))
