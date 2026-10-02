# -*- coding: utf-8 -*-
"""
[독립 레고 블록] Stock YouTube Behavior Bot (📈 StockMaster AI 전용 유튜브 쇼츠 30분 스텔스 인간 행동 봇)
===================================================================================================
- 역할:
  1. API 업로드 코드는 0% 배제! 오직 사람처럼 유튜브 쇼츠 시청, 체류, 댓글 탐색, 좋아요만 전담
  2. 하루 총 30분을 4개 일과 시간(09:00, 13:00, 16:30, 22:30)으로 분할 실행
  3. [사용자 절대 수칙] 매 세션마다 실제 '좋아요' 2~3회 실행 (youtube_session.json 로그인 세션 연동)
  4. 특정 주제 편향 방지: 일상/유머/반려동물(50%) + 주식/증시/ETF/퀀트(50%) 다채로운 탐색
  5. 고가치 시청자 신호: 쇼츠 1편당 16~35초 고체류(완시청) + 댓글창 열람 후 닫기
  6. Gemini AI 호출 0회 (순수 파이썬 + Playwright 스텔스 브라우저, API 비용 0원)
  7. 구글 계정 신뢰 지수(Creator Trust Score)를 극대화하여 유튜브 쇼츠 피드 노출 0회 원천 돌파
- 원칙: Rule 1 (앱별 완전 독립 모듈화), Rule 6 (24시간 무인 자율 구동)
"""

import os
import sys
import time
import json
import random
import logging
import asyncio
import threading
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

logger = logging.getLogger("StockYouTubeBehaviorBot")

_UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]

_GENERAL_HUMAN_KEYWORDS = [
    "귀여운 강아지 고양이 숏폼",
    "오늘의 꿀잼 릴스 숏폼",
    "전국 숨은 맛집 투어 쇼츠",
    "힐링 여행 풍경 쇼츠",
    "직장인 공감 썰 숏폼",
    "요즘 뜨는 감성 카페 쇼츠",
    "초간단 자취 요리 레시피 쇼츠"
]

_STOCK_KEYWORDS = [
    "오늘의 코스피 급등주 쇼츠",
    "국내 배당주 추천 쇼츠",
    "삼성전자 SK하이닉스 수급 분석",
    "코스피 코스닥 체결강도 꿀팁",
    "초보 주식 차트 보는 법",
    "국내 고배당주 포트폴리오",
    "한국은행 금리 수혜주 숏폼",
    "주식 외인 기관 수급 타점"
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


class StockYouTubeBehaviorBot:
    """📈 StockMaster AI 전용 유튜브 쇼츠 30분 스텔스 인간 행동 봇"""

    SLOTS = [
        {"id": "morning", "time": "09:00", "name": "🌅 아침 출근길 쇼츠 (7분)", "target_min": 7},
        {"id": "lunch", "time": "13:00", "name": "🍱 점심시간 쇼츠 (8분)", "target_min": 8},
        {"id": "afternoon", "time": "16:30", "name": "☕ 오후 휴식 쇼츠 (7분)", "target_min": 7},
        {"id": "night", "time": "22:30", "name": "🌙 야간 침대 쇼츠 (8분)", "target_min": 8}
    ]

    def __init__(self, headless: bool = True):
        self.brand = "stock"
        self.brand_name = "📈 StockMaster AI"
        self.headless = headless
        self.youtube_profile_dir = CURRENT_DIR / "youtube_chrome_profile"
        self.youtube_profile_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = CURRENT_DIR / "youtube_session.json"
        self.history_file = CURRENT_DIR / "youtube_human_routine_history.json"

    def is_sleep_time(self) -> bool:
        """심야 취침 모드 (00:00 ~ 07:30 KST 계정 안전 휴식)"""
        now = datetime.now()
        return (now.hour == 0 and now.minute < 30) or (0 <= now.hour < 7) or (now.hour == 7 and now.minute < 30)

    async def _simulate_youtube_shorts_session(self, page, duration_sec: int, target_likes: int = 2) -> Dict[str, Any]:
        """유튜브 쇼츠 탐색, 완시청, 댓글 열람 및 좋아요 (일상 50% + 브랜드 50% 혼합)"""
        result = {"shorts_watched": 0, "likes": 0, "comments_inspected": 0, "platform": "youtube_shorts"}
        start_t = time.time()
        pool = _GENERAL_HUMAN_KEYWORDS if random.random() < 0.5 else _STOCK_KEYWORDS
        kw = random.choice(pool)

        try:
            logger.info(f"🎬 [Stock YouTubeBot] 유튜브 쇼츠 피드 진입 중... (관심 키워드: '{kw}')")

            # 1. 자연스러운 키워드 검색 또는 쇼츠 직행
            if random.random() < 0.4:
                search_url = f"https://www.youtube.com/results?search_query={kw}&sp=CAISAhAB"
                await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(random.uniform(3.0, 5.0))
                shorts_entry = await page.query_selector("ytd-reel-item-renderer, a[href*='/shorts/']")
                if shorts_entry:
                    await shorts_entry.click()
                    await asyncio.sleep(random.uniform(2.5, 4.0))
                else:
                    await page.goto("https://www.youtube.com/shorts", wait_until="domcontentloaded", timeout=45000)
            else:
                await page.goto("https://www.youtube.com/shorts", wait_until="domcontentloaded", timeout=45000)

            await asyncio.sleep(random.uniform(2.5, 4.5))

            while (time.time() - start_t) < duration_sec:
                # 2. 쇼츠 완시청 체류 (16 ~ 35초)
                watch_time = random.uniform(16.0, 35.0)
                logger.info(f"👀 [Stock YouTubeBot] 쇼츠 #{result['shorts_watched'] + 1} 완시청 중... ({watch_time:.1f}초 체류)")
                await asyncio.sleep(watch_time)
                result["shorts_watched"] += 1

                # 3. 댓글창 열람 시뮬레이션
                if random.random() < 0.25:
                    try:
                        comment_btn = await page.query_selector("button#comments-button, button[aria-label*='댓글'], ytd-comments-entry-point-header-renderer")
                        if comment_btn:
                            await comment_btn.click()
                            result["comments_inspected"] += 1
                            logger.info("💬 [Stock YouTubeBot] 시청자 댓글창 열람 체류 (5초)...")
                            await asyncio.sleep(random.uniform(4.0, 7.0))
                            close_comment = await page.query_selector("button#close-button, ytd-engagement-panel-section-list-renderer button[aria-label*='닫기']")
                            if close_comment:
                                await close_comment.click()
                            else:
                                await page.keyboard.press("Escape")
                            await asyncio.sleep(1.0)
                    except Exception:
                        pass

                # 4. 자연스러운 좋아요 클릭
                if result["likes"] < target_likes and (time.time() - start_t) > 15:
                    try:
                        like_buttons = await page.query_selector_all("button[aria-label*='좋아요'], button[aria-label*='like this'], ytd-like-button-renderer button")
                        for l_btn in like_buttons:
                            box = await l_btn.bounding_box()
                            if box and box["width"] > 0 and box["height"] > 0:
                                btn_x = box["x"] + box["width"] / 2
                                btn_y = box["y"] + box["height"] / 2
                                p_start = (random.randint(200, 500), random.randint(300, 600))
                                for pt in _bezier_points(p_start, (btn_x, btn_y), steps=12):
                                    await page.mouse.move(pt[0], pt[1])
                                    await asyncio.sleep(0.015)
                                await asyncio.sleep(random.uniform(0.6, 1.2))
                                await page.mouse.click(btn_x, btn_y)
                                result["likes"] += 1
                                logger.info(f"💖 [Stock YouTubeBot] 유튜브 쇼츠 실제 '좋아요' 클릭 성공! (세션 누적: {result['likes']}/{target_likes}회)")
                                await asyncio.sleep(random.uniform(2.5, 4.5))
                                break
                    except Exception as le:
                        logger.debug(f"좋아요 시도 스킵: {le}")

                await page.keyboard.press("PageDown")
                await asyncio.sleep(random.uniform(2.0, 3.8))

        except Exception as e:
            logger.warning(f"스톡 유튜브 쇼츠 세션 예외: {e}")

        return result

    async def execute_slot_session_async(self, slot: Dict[str, Any]) -> Dict[str, Any]:
        """지정된 세션 실행 (쿠키 100% 주입 + 목표 좋아요 2~3회)"""
        slot_name = slot.get("name", "유튜브 인간 행동 세션")
        target_sec = slot.get("target_min", 7) * 60
        target_likes = random.randint(2, 3)

        logger.info("=" * 70)
        logger.info(f"🕵️ [Stock 유튜브 30분 스텔스 봇] 시작: {slot_name} (목표: {slot.get('target_min')}분 | 목표 좋아요: {target_likes}회)")
        logger.info("=" * 70)

        session_start = time.time()
        ua = random.choice(_UA_POOL)
        summary = {
            "timestamp": get_now_kst_str(),
            "slot_id": slot.get("id"),
            "slot_name": slot_name,
            "target_min": slot.get("target_min"),
            "target_likes": target_likes,
            "actual_sec": 0,
            "likes_given": 0,
            "shorts_watched": 0,
            "comments_inspected": 0,
            "status": "success",
            "gemini_calls": 0,
            "brand": self.brand
        }

        async with async_playwright() as p:
            try:
                ctx_yt = await p.chromium.launch_persistent_context(
                    user_data_dir=str(self.youtube_profile_dir),
                    headless=self.headless,
                    user_agent=ua,
                    viewport={"width": 1280, "height": 850},
                    args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-infobars"]
                )

                if self.session_file.exists():
                    try:
                        with open(self.session_file, "r", encoding="utf-8") as sf:
                            sdata = json.load(sf)
                            cookies = sdata if isinstance(sdata, list) else sdata.get("cookies", [])
                            if cookies:
                                clean_cookies = []
                                for c in cookies:
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
                                    clean_cookies.append(c_item)
                                await ctx_yt.add_cookies(clean_cookies)
                                logger.info(f"🍪 [Stock YouTubeBot] 유튜브 세션 쿠키 {len(clean_cookies)}개 브라우저 주입 완료")
                    except Exception as ce:
                        logger.debug(f"유튜브 쿠키 주입 예외: {ce}")

                page_yt = ctx_yt.pages[0] if ctx_yt.pages else await ctx_yt.new_page()
                await page_yt.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

                yt_res = await self._simulate_youtube_shorts_session(page_yt, target_sec, target_likes=target_likes)
                summary["shorts_watched"] = yt_res.get("shorts_watched", 0)
                summary["likes_given"] = yt_res.get("likes", 0)
                summary["comments_inspected"] = yt_res.get("comments_inspected", 0)

                await ctx_yt.close()
            except Exception as e:
                logger.warning(f"스톡 유튜브 브라우저 세션 오류: {e}")
                summary["status"] = f"error: {e}"

        elapsed_sec = int(time.time() - session_start)
        summary["actual_sec"] = elapsed_sec
        logger.info(f"✅ [Stock 유튜브 스텔스 세션 완료] {slot_name} 체류: {elapsed_sec//60}분 {elapsed_sec%60}초 | 쇼츠 시청: {summary['shorts_watched']}편 | 좋아요: {summary['likes_given']}회 | 제미나이: 0회")
        self._record_history(summary)
        return summary

    def execute_slot_session(self, slot_id: str) -> Dict[str, Any]:
        """동기 호출 래퍼"""
        matched = next((s for s in self.SLOTS if s["id"] == slot_id), None)
        if not matched:
            matched = self.SLOTS[0]
        return asyncio.run(self.execute_slot_session_async(matched))

    def _record_history(self, summary: Dict[str, Any]):
        """일일 유튜브 인간 루틴 이력 디스크 저장"""
        try:
            records = []
            if self.history_file.exists():
                with open(self.history_file, "r", encoding="utf-8") as f:
                    records = json.load(f)
            records.append(summary)
            records = records[-100:]
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.debug(f"유튜브 루틴 이력 저장 실패: {e}")

    def get_today_stats(self) -> Dict[str, Any]:
        """오늘자 유튜브 스텔스 누적 통계"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        total_sec = 0
        total_likes = 0
        total_watched = 0
        sessions_done = 0

        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    records = json.load(f)
                for r in records:
                    if r.get("timestamp", "").startswith(today_str):
                        total_sec += r.get("actual_sec", 0)
                        total_likes += r.get("likes_given", 0)
                        total_watched += r.get("shorts_watched", 0)
                        sessions_done += 1
            except Exception:
                pass

        return {
            "date": today_str,
            "sessions_done": sessions_done,
            "total_min": round(total_sec / 60, 1),
            "total_likes": total_likes,
            "total_watched": total_watched,
            "gemini_calls": 0,
            "target_daily_min": 30
        }


class StockYouTubeBehaviorScheduler:
    """📈 StockMaster AI 유튜브 24/7 백그라운드 무인 스케줄러 데몬"""

    def __init__(self):
        self.bot = StockYouTubeBehaviorBot(headless=True)
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._executed_today = set()

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="StockYouTubeBehaviorScheduler")
        self._thread.start()
        logger.info("🚀 [Stock YouTubeBehaviorScheduler] 24시간 무인 자율 데몬 기동 완료 (09:00, 13:00, 16:30, 22:30)")

    def _run_loop(self):
        while self.is_running:
            try:
                now = datetime.now()
                now_str = now.strftime("%H:%M")
                today_date = now.strftime("%Y-%m-%d")

                if now_str == "00:00":
                    self._executed_today.clear()

                for slot in self.bot.SLOTS:
                    slot_id = slot["id"]
                    slot_time = slot["time"]
                    key = f"{today_date}_{slot_id}"

                    if now_str == slot_time and key not in self._executed_today:
                        logger.info(f"⏰ [Stock YouTube 스케줄 알람] {slot['name']} 정시 감지 ➔ 스텔스 세션 즉각 착수!")
                        self._executed_today.add(key)
                        self.bot.execute_slot_session(slot_id)

            except Exception as e:
                logger.warning(f"스톡 유튜브 스케줄러 루프 오류: {e}")

            time.sleep(25)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    print("\n" + "=" * 70)
    print("🎬 [📈 StockMaster AI] 유튜브 쇼츠 30분 스텔스 인간 행동 봇 단독 테스트")
    print("=" * 70)
    bot = StockYouTubeBehaviorBot(headless=True)
    test_slot = {"id": "test", "time": "now", "name": "🚀 1분 퀵 검증 세션", "target_min": 1}
    res = asyncio.run(bot.execute_slot_session_async(test_slot))
    print(f"\n결과: {json.dumps(res, ensure_ascii=False, indent=2)}")
    print(f"오늘 통계: {bot.get_today_stats()}")
