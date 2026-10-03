# -*- coding: utf-8 -*-
"""
Stock Threads Human Behavior Bot (📈 StockMaster AI 전용 스레드 하루 45분 인간 행동 봇 독립 레고 블록)
=================================================================================================
- 브랜드: 📈 StockMaster AI (주식 AI)
- 전용 계정: @stockmaster_ai
- 역할:
  1. API/자동발행 코드는 일체 배제! 오직 사람처럼 피드 탐색, 정독, 체류, 좋아요만 전담
  2. 하루 총 45분을 4개 일과 시간(08:45, 12:45, 16:00, 22:00)으로 분할 실행
  3. 스레드(Threads.net) For You 피드 및 검색 탭 자연스러운 탐색
  4. 특정 주제 편향 방지: 일상/유머/맛집/자취(50%) + 주식/테마주/수급/재테크(50%) 다채로운 탐색
  5. 매 세션당 자연스러운 좋아요(Heart) 2~3회 실행 (과도한 액션 방지, 안전 텀 유지)
  6. 베지어 곡선 마우스 이동 및 실제 인간 휠 스크롤 시뮬레이션
  7. 계정 신뢰도(Trust Score)를 극대화하여 섀도우밴 원천 차단 및 For You 추천 노출 부스팅
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

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("StockThreadsHumanBot")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
PROFILE_DIR = CURRENT_DIR / "meta_chrome_profile"
COOKIE_FILE = CURRENT_DIR / "threads_cookies.json"
SESSION_FILE = CURRENT_DIR / "threads_session.json"
HISTORY_FILE = CURRENT_DIR / "threads_human_routine_history.json"

# 🐶 일상/유머/맛집/힐링 등 다양한 사람 관심사 키워드 (50% 비중)
_GENERAL_HUMAN_KEYWORDS = [
    "귀여운 강아지 고양이",
    "오늘의 꿀잼 썰",
    "전국 숨은 맛집 투어",
    "직장인 퇴근 일상",
    "요즘 뜨는 감성 카페",
    "초간단 자취 요리 레시피",
    "힐링 여행 일상",
    "주말 브런치 맛집"
]

# 📈 StockMaster AI 연관 관심사 키워드 (50% 비중)
_STOCK_TARGET_KEYWORDS = [
    "실시간 외국인 기관 수급",
    "오늘의 주도 테마주",
    "주식 초보 매매 팁",
    "급등주 눌림목 매매",
    "코스피 코스닥 시황",
    "2차전지 반도체 전망",
    "단타 스윙 매매 기법",
    "AI 관련주 분석"
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


class StockThreadsHumanBot:
    """📈 StockMaster AI 스레드 전용 하루 45분 인간 행동 시뮬레이터"""

    BRAND = "stock"
    BRAND_NAME = "StockMaster AI"

    SLOTS = [
        {"id": "morning", "time": "08:45", "start_h": 8, "start_m": 45, "end_h": 12, "end_m": 0, "name": "🌅 아침 출근길 스레드 탐색 (11분)", "target_min": 11, "target_likes": 3},
        {"id": "lunch", "time": "12:45", "start_h": 12, "start_m": 45, "end_h": 15, "end_m": 30, "name": "🍱 점심시간 스레드 둘러보기 (12분)", "target_min": 12, "target_likes": 3},
        {"id": "afternoon", "time": "16:00", "start_h": 16, "start_m": 0, "end_h": 21, "end_m": 0, "name": "☕ 오후 티타임 스레드 피드 (11분)", "target_min": 11, "target_likes": 2},
        {"id": "night", "time": "22:00", "start_h": 22, "start_m": 0, "end_h": 23, "end_m": 59, "name": "🌙 야간 침대 속 스레드 정독 (11분)", "target_min": 11, "target_likes": 3}
    ]

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.profile_dir = PROFILE_DIR
        self.profile_dir.mkdir(parents=True, exist_ok=True)

    def _prepare_cookies(self) -> List[Dict[str, Any]]:
        if not COOKIE_FILE.exists():
            return []
        try:
            with open(COOKIE_FILE, "r", encoding="utf-8") as f:
                raw_cookies = json.load(f)
            pw_cookies = []
            for c in raw_cookies:
                pw_c = {
                    "name": c["name"],
                    "value": c["value"],
                    "domain": c["domain"],
                    "path": c.get("path", "/"),
                    "secure": c.get("secure", True),
                    "httpOnly": c.get("httpOnly", False),
                }
                if c.get("sameSite") in ["Strict", "Lax", "None"]:
                    pw_c["sameSite"] = c["sameSite"]
                elif c.get("sameSite") == "no_restriction":
                    pw_c["sameSite"] = "None"
                elif c.get("sameSite") == "lax":
                    pw_c["sameSite"] = "Lax"
                pw_cookies.append(pw_c)
                for d in [".threads.net", ".instagram.com"]:
                    dc = dict(pw_c)
                    dc["domain"] = d
                    pw_cookies.append(dc)
            return pw_cookies
        except Exception:
            return []

    async def run_session(self, duration_sec: int = 660, target_likes: int = 3) -> Dict[str, Any]:
        """스레드 인간 체류 & 피드 탐색 세션 실행"""
        logger.info(f"🚀 [{self.BRAND_NAME}] 스레드 인간 행동 봇 가동 (목표 체류: {duration_sec}초 / {duration_sec//60}분, 목표 좋아요: {target_likes}개)")
        
        result = {
            "brand": self.BRAND,
            "started_at": datetime.now().isoformat(),
            "posts_read": 0,
            "likes_given": 0,
            "searches_performed": 0,
            "duration_sec": 0,
            "status": "IN_PROGRESS"
        }
        
        start_time = time.time()

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 900}
            )
            
            cookies = self._prepare_cookies()
            if cookies:
                await context.add_cookies(cookies)

            page = context.pages[0] if context.pages else await context.new_page()

            try:
                # 1. 스레드 메인 피드 접속
                logger.info("1. 스레드 For You 홈 피드 접속 중...")
                await page.goto("https://www.threads.net/", wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(random.uniform(4.0, 6.0))

                # 피드 탐색 루프
                while (time.time() - start_time) < duration_sec:
                    elapsed = int(time.time() - start_time)
                    
                    if random.random() < 0.25 and result["searches_performed"] < 3:
                        search_kw = random.choice(_GENERAL_HUMAN_KEYWORDS if random.random() < 0.5 else _STOCK_TARGET_KEYWORDS)
                        logger.info(f"🔍 [자연스러운 검색 탐색] 키워드: '{search_kw}'")
                        try:
                            search_url = f"https://www.threads.net/search?q={search_kw}"
                            await page.goto(search_url, wait_until="domcontentloaded", timeout=25000)
                            result["searches_performed"] += 1
                            await asyncio.sleep(random.uniform(4.0, 7.0))
                        except Exception as e:
                            logger.warning(f"검색 이동 경고: {e}")

                    # 1. 자연스러운 불규칙 휠 스크롤
                    scroll_px = random.randint(280, 650)
                    await page.mouse.wheel(0, scroll_px)
                    result["posts_read"] += 1

                    # 2. 베지어 마우스 이동 (인간성 시뮬레이션)
                    p1 = (random.randint(150, 450), random.randint(200, 450))
                    p2 = (random.randint(450, 850), random.randint(350, 700))
                    for pt in _bezier_points(p1, p2, steps=10):
                        await page.mouse.move(pt[0], pt[1])
                        await asyncio.sleep(0.012)

                    # 3. 실제 글 정독 체류 시간 (5 ~ 14초)
                    dwell = random.uniform(5.0, 14.0)
                    await asyncio.sleep(dwell)

                    # 4. 자연스러운 좋아요(Like) 액션 (안전 간격 준수)
                    if result["likes_given"] < target_likes and (time.time() - start_time) > 20:
                        if random.random() < 0.35:
                            try:
                                like_btns = await page.query_selector_all("svg[aria-label='Like'], svg[aria-label='좋아요']")
                                if like_btns:
                                    idx = min(result["likes_given"], len(like_btns) - 1)
                                    target_btn = like_btns[idx]
                                    box = await target_btn.bounding_box()
                                    if box:
                                        await page.mouse.move(box["x"] + box["width"]/2, box["y"] + box["height"]/2)
                                        await asyncio.sleep(random.uniform(0.3, 0.7))
                                        await target_btn.click(force=True)
                                        result["likes_given"] += 1
                                        logger.info(f"❤️ [공감 좋아요] 피드 글에 자연스러운 하트 클릭 완료! (누적 {result['likes_given']}/{target_likes})")
                                        await asyncio.sleep(random.uniform(8.0, 16.0))
                            except Exception as ex_like:
                                logger.warning(f"좋아요 시도 건너뜀: {ex_like}")

                    if page.url != "https://www.threads.net/" and random.random() < 0.3:
                        logger.info("🏠 홈 피드로 복귀...")
                        await page.goto("https://www.threads.net/", wait_until="domcontentloaded", timeout=25000)
                        await asyncio.sleep(random.uniform(3.0, 5.0))

                result["duration_sec"] = int(time.time() - start_time)
                result["status"] = "COMPLETED"
                result["ended_at"] = datetime.now().isoformat()
                
                await context.storage_state(path=str(SESSION_FILE))
                self._save_history(result)

                logger.info(f"🎉 [{self.BRAND_NAME}] 스레드 인간 행동 세션 완료! (체류: {result['duration_sec']}초, 정독: {result['posts_read']}개, 좋아요: {result['likes_given']}개)")
                await context.close()
                return result

            except Exception as e:
                logger.error(f"❌ [{self.BRAND_NAME}] 스레드 인간 행동 오류: {e}")
                result["status"] = f"ERROR: {str(e)}"
                result["duration_sec"] = int(time.time() - start_time)
                await context.close()
                return result

    def _save_history(self, record: Dict[str, Any]):
        history = []
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []
        history.append(record)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    async def run_daemon_loop(self):
        """24시간 365일 무인 자율 스케줄러 루프"""
        logger.info(f"🤖 [{self.BRAND_NAME}] 스레드 45분 데몬 스케줄러 가동 시작 (총 4개 슬롯 분할)")
        executed_today = set()
        
        while True:
            now = datetime.now()
            today_str = now.strftime("%Y-%m-%d")
            curr_h = now.hour
            curr_m = now.minute

            if curr_h == 0 and curr_m < 5:
                executed_today.clear()

            for slot in self.SLOTS:
                slot_key = f"{today_str}_{slot['id']}"
                if slot_key not in executed_today:
                    if slot["start_h"] <= curr_h and (curr_h > slot["start_h"] or curr_m >= slot["start_m"]):
                        if curr_h < slot["end_h"] or (curr_h == slot["end_h"] and curr_m <= slot["end_m"]):
                            logger.info(f"⏰ [스케줄 기상] {slot['name']} 시작!")
                            duration = slot["target_min"] * 60
                            likes = slot["target_likes"]
                            await self.run_session(duration_sec=duration, target_likes=likes)
                            executed_today.add(slot_key)
                            logger.info(f"💤 [슬롯 완료] {slot['name']} 완료 후 대기 모드 진입")

            await asyncio.sleep(60)


async def main():
    bot = StockThreadsHumanBot(headless=True)
    res = await bot.run_session(duration_sec=30, target_likes=1)
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
