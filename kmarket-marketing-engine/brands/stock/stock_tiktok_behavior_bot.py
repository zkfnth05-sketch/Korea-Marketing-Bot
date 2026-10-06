# -*- coding: utf-8 -*-
"""
[독립 레고 블록] Stock TikTok Behavior Bot (📈 StockMaster AI 전용 틱톡 30분 스텔스 인간 행동 봇)
=============================================================================================
- 역할:
  1. API 업로드 코드는 0% 배제! 오직 사람처럼 틱톡 FYP 피드 시청, 체류, 댓글 탐색, 좋아요만 전담
  2. 하루 총 30분을 4개 일과 시간(09:30, 13:30, 17:00, 23:00)으로 분할 실행
  3. [사용자 절대 수칙] 매 세션마다 실제 '좋아요' 2~3회 실행 (tiktok_session.json 연동)
  4. 특정 주제 편향 방지: 일상/유머/IT테크(50%) + 주식/퀀트/배당/재테크(50%) 다채로운 탐색
  5. 고가치 시청자 신호: 영상 1편당 15~35초 고체류(완시청) + 댓글창 열람 후 닫기
  6. Gemini AI 호출 0회 (순수 파이썬 + Playwright 스텔스 브라우저, API 비용 0원)
  7. 틱톡 계정 신뢰 지수(Creator Trust Score)를 극대화하여 0뷰 섀도우밴 원천 돌파
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

logger = logging.getLogger("StockTikTokBehaviorBot")

_UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]

# 🐶 일상/유머/IT테크 등 다양한 사람 관심사 키워드 (단일 주제 편향 방지)
_GENERAL_HUMAN_KEYWORDS = [
    "최신 IT 전자기기 언박싱",
    "웃긴 직장인 썰 틱톡",
    "초간단 자취 요리",
    "드라이브 힐링 풍경",
    "귀여운 반려동물 틱톡",
    "전국 핫플 맛집 투어",
    "자기계발 동기부여 숏폼",
    "틱톡 인기 챌린지"
]

# 📈 StockMaster 브랜드 관심사 키워드 (주식/퀀트/배당/재테크)
_STOCK_KEYWORDS = [
    "주식 초보 기초 꿀팁",
    "미국 배당주 추천 SCHD",
    "엔비디아 주가 전망",
    "국내 반도체 주도주",
    "공모주 청약 방법",
    "AI 퀀트 적정주가 계산법",
    "월 100만원 배당 포트폴리오",
    "단타 눌림목 매매 타이밍"
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


def urllib_quote(text: str) -> str:
    import urllib.parse
    return urllib.parse.quote(text)


class StockTikTokBehaviorBot:
    """📈 StockMaster AI 전용 틱톡 30분 스텔스 인간 행동 봇"""

    SLOTS = [
        {"id": "morning", "time": "09:30", "start_h": 9, "start_m": 30, "end_h": 13, "end_m": 29, "name": "🌅 아침 출근길 틱톡 (15분)", "target_min": 15},
        {"id": "lunch", "time": "13:30", "start_h": 13, "start_m": 30, "end_h": 16, "end_m": 59, "name": "🍱 점심시간 틱톡 (15분)", "target_min": 15},
        {"id": "afternoon", "time": "17:00", "start_h": 17, "start_m": 0, "end_h": 22, "end_m": 59, "name": "☕ 오후 퇴근길 틱톡 (15분)", "target_min": 15},
        {"id": "night", "time": "23:00", "start_h": 23, "start_m": 0, "end_h": 23, "end_m": 59, "name": "🌙 야간 침대 틱톡 (15분)", "target_min": 15}
    ]

    def __init__(self, headless: bool = True):
        self.brand = "stock"
        self.brand_name = "📈 StockMaster AI"
        self.headless = headless
        self.profile_dir = CURRENT_DIR / "tiktok_browser_profile"
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = CURRENT_DIR / "tiktok_session.json"
        self.history_file = CURRENT_DIR / "tiktok_routine_history.json"

    async def _simulate_tiktok_session(self, page, target_seconds: int, target_likes: int = 2) -> Dict[str, Any]:
        result = {
            "videos_watched": 0,
            "likes": 0,
            "comments_inspected": 0,
            "searches_done": 0
        }

        use_search = random.random() < 0.5
        if use_search:
            kw = random.choice(_STOCK_KEYWORDS if random.random() < 0.5 else _GENERAL_HUMAN_KEYWORDS)
            search_url = f"https://www.tiktok.com/search?q={urllib_quote(kw)}"
            logger.info(f"🔍 [Stock TikTokBot] 사람처럼 틱톡 검색 진입: '{kw}'")
            try:
                await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
                result["searches_done"] += 1
                await asyncio.sleep(random.uniform(4.0, 7.0))
            except Exception as e:
                logger.debug(f"검색 페이지 로드 예외: {e}")
                await page.goto("https://www.tiktok.com/foryou", wait_until="domcontentloaded", timeout=45000)
        else:
            logger.info("📱 [Stock TikTokBot] 틱톡 For You 추천 피드 진입")
            try:
                await page.goto("https://www.tiktok.com/foryou", wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(random.uniform(4.0, 6.0))
            except Exception as e:
                logger.debug(f"FYP 로드 예외: {e}")

        start_time = time.time()
        video_index = 0

        try:
            while (time.time() - start_time) < target_seconds:
                video_index += 1
                result["videos_watched"] += 1

                watch_time = random.uniform(15.0, 32.0)
                logger.info(f"🎬 [Stock TikTokBot] #{video_index}번째 틱톡 시청 중 ({round(watch_time, 1)}초 체류)...")

                start_t = time.time()
                while (time.time() - start_t) < watch_time:
                    rx = random.randint(300, 900)
                    ry = random.randint(250, 700)
                    await page.mouse.move(rx, ry)
                    await asyncio.sleep(random.uniform(3.0, 6.0))

                if random.random() < 0.40:
                    try:
                        comment_btn = await page.query_selector("button[data-e2e='comment-icon'], span[data-e2e='comment-icon'], button[aria-label*='댓글']")
                        if comment_btn:
                            await comment_btn.click()
                            result["comments_inspected"] += 1
                            logger.info("💬 [Stock TikTokBot] 시청자 댓글창 열람 체류 (5초)...")
                            await asyncio.sleep(random.uniform(4.0, 6.5))
                            close_btn = await page.query_selector("button[data-e2e='comment-close-icon'], button[aria-label*='닫기']")
                            if close_btn:
                                await close_btn.click()
                            else:
                                await page.keyboard.press("Escape")
                            await asyncio.sleep(1.0)
                    except Exception:
                        pass

                if result["likes"] < target_likes and (time.time() - start_t) > 12:
                    try:
                        like_buttons = await page.query_selector_all("button[data-e2e='like-icon'], span[data-e2e='like-icon'], button[aria-label*='좋아요'], button[aria-label*='Like']")
                        for l_btn in like_buttons:
                            box = await l_btn.bounding_box()
                            if box and box["width"] > 0 and box["height"] > 0:
                                btn_x = box["x"] + box["width"] / 2
                                btn_y = box["y"] + box["height"] / 2
                                p_start = (random.randint(200, 500), random.randint(300, 600))
                                for pt in _bezier_points(p_start, (btn_x, btn_y), steps=12):
                                    await page.mouse.move(pt[0], pt[1])
                                    await asyncio.sleep(0.015)
                                await asyncio.sleep(random.uniform(0.5, 1.0))
                                await page.mouse.click(btn_x, btn_y)
                                result["likes"] += 1
                                logger.info(f"💖 [Stock TikTokBot] 틱톡 영상 실제 '좋아요' 클릭 성공! (세션 누적: {result['likes']}/{target_likes}회)")
                                await asyncio.sleep(random.uniform(2.0, 4.0))
                                break
                    except Exception as le:
                        logger.debug(f"좋아요 시도 스킵: {le}")

                logger.info("🖱️ [Stock TikTokBot] 다음 틱톡 영상으로 부드럽게 스크롤 넘김...")
                await page.keyboard.press("ArrowDown")
                await asyncio.sleep(random.uniform(2.0, 3.5))

        except Exception as e:
            logger.warning(f"주식 틱톡 세션 루프 예외: {e}")

        return result

    async def execute_slot_session_async(self, slot: Dict[str, Any]) -> Dict[str, Any]:
        slot_name = slot.get("name", "틱톡 인간 행동 세션")
        target_sec = slot.get("target_min", 7) * 60
        target_likes = random.randint(2, 3)

        logger.info("=" * 70)
        logger.info(f"🕵️ [Stock 틱톡 30분 스텔스 봇] 시작: {slot_name} (목표: {slot.get('target_min')}분 | 목표 좋아요: {target_likes}회)")
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
            "videos_watched": 0,
            "comments_inspected": 0,
            "status": "success",
            "gemini_calls": 0,
            "brand": self.brand
        }

        from core.engine.browser_guard import async_browser_lock, clean_browser_profile_locks, get_safe_browser_args

        clean_browser_profile_locks(self.profile_dir)

        async with async_browser_lock(f"Stock 틱톡 세션 ({slot_name})"):
            async with async_playwright() as p:
                try:
                    ctx_tt = await p.chromium.launch_persistent_context(
                        user_data_dir=str(self.profile_dir),
                        headless=self.headless,
                        user_agent=ua,
                        viewport={"width": 1280, "height": 850},
                        args=get_safe_browser_args()
                    )

                    # tiktok_session.json 쿠키 주입
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
                                            "domain": c.get("domain", ".tiktok.com"),
                                            "path": c.get("path", "/")
                                        }
                                        if "sameSite" in c and c["sameSite"] in ["Strict", "Lax", "None"]:
                                            c_item["sameSite"] = c["sameSite"]
                                        if c.get("secure"):
                                            c_item["secure"] = True
                                        clean_cookies.append(c_item)
                                    await ctx_tt.add_cookies(clean_cookies)
                                    logger.info(f"🍪 [Stock TikTokBot] 틱톡 세션 쿠키 {len(clean_cookies)}개 브라우저 주입 완료")
                        except Exception as ce:
                            logger.debug(f"틱톡 쿠키 주입 예외: {ce}")

                    page_tt = ctx_tt.pages[0] if ctx_tt.pages else await ctx_tt.new_page()
                    await page_tt.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

                    tt_res = await self._simulate_tiktok_session(page_tt, target_sec, target_likes=target_likes)
                    summary["videos_watched"] = tt_res.get("videos_watched", 0)
                    summary["likes_given"] = tt_res.get("likes", 0)
                    summary["comments_inspected"] = tt_res.get("comments_inspected", 0)

                    await ctx_tt.close()
                except Exception as e:
                    logger.warning(f"주식 틱톡 브라우저 세션 오류: {e}")
                    summary["status"] = f"error: {e}"

        elapsed_sec = int(time.time() - session_start)
        summary["actual_sec"] = elapsed_sec
        logger.info(f"✅ [Stock 틱톡 스텔스 세션 완료] {slot_name} 체류: {elapsed_sec//60}분 {elapsed_sec%60}초 | 영상 시청: {summary['videos_watched']}편 | 좋아요: {summary['likes_given']}회 | 제미나이: 0회")
        self._record_history(summary)
        return summary

    def execute_slot_session(self, slot_id: str) -> Dict[str, Any]:
        matched = next((s for s in self.SLOTS if s["id"] == slot_id), None)
        if not matched:
            matched = self.SLOTS[0]
        return asyncio.run(self.execute_slot_session_async(matched))

    def _record_history(self, summary: Dict[str, Any]):
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
            logger.debug(f"틱톡 이력 저장 실패: {e}")

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
            "target_minutes": 60,
            "total_likes": total_likes,
            "target_likes": "세션당 3~5회 (일 12~20회)",
            "completed_slots": completed_slots,
            "gemini_calls": 0
        }

    def execute_single_session(self, duration_sec: int = 30, target_likes: int = 1) -> Dict[str, Any]:
        """대시보드 1회 즉시 실행용 퀵 틱톡 세션"""
        quick_slot = {
            "id": "quick_tiktok",
            "time": "now",
            "name": "⚡ 대시보드 1회 즉시 틱톡 세션",
            "target_min": max(0.5, duration_sec / 60)
        }
        try:
            res = asyncio.run(self.execute_slot_session_async(quick_slot))
            return {
                "status": "success",
                "duration_sec": res.get("actual_sec", duration_sec),
                "videos_watched": res.get("videos_watched", 1),
                "likes_given": res.get("likes_given", target_likes),
                "brand": self.brand
            }
        except Exception as e:
            logger.error(f"❌ 1회 틱톡 세션 실패: {e}")
            return {"status": "error", "message": str(e), "duration_sec": 0, "videos_watched": 0, "likes_given": 0}


class StockTikTokBehaviorScheduler:
    """📈 StockMaster AI 전용 틱톡 24시간 365일 무인 자율 스케줄러 데몬"""

    def __init__(self, headless: bool = True):
        self.bot = StockTikTokBehaviorBot(headless=headless)
        self.is_running = False

    def execute_single_session(self, duration_sec: int = 30) -> Dict[str, Any]:
        """단발 1회 실행"""
        return self.bot.execute_single_session(duration_sec=duration_sec)

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        logger.info("🚀 [Stock TikTokBehaviorScheduler] 24시간 무인 자율 데몬 기동 (09:30, 13:30, 17:00, 23:00)")
        threading.Thread(target=self._daemon_loop, daemon=True).start()

    def _daemon_loop(self):
        executed_today = set()
        last_date = ""

        while self.is_running:
            try:
                now = datetime.now()
                today_str = now.strftime("%Y-%m-%d")
                cur_min = now.hour * 60 + now.minute

                if today_str != last_date:
                    executed_today.clear()
                    last_date = today_str

                for slot in self.bot.SLOTS:
                    slot_id = slot["id"]
                    start_total = slot.get("start_h", 0) * 60 + slot.get("start_m", 0)
                    end_total = slot.get("end_h", 23) * 60 + slot.get("end_m", 59)
                    exec_key = f"{today_str}_{slot_id}"

                    if start_total <= cur_min <= end_total and exec_key not in executed_today:
                        logger.info(f"⏰ [Stock TikTok Scheduler] {slot['name']} 골든타임 도달! 무인 스텔스 세션 즉시 가동...")
                        executed_today.add(exec_key)
                        self.bot.execute_slot_session(slot_id)

                time.sleep(30)
            except Exception as e:
                logger.error(f"❌ [Stock TikTok Scheduler 예외] {e}")
                time.sleep(30)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    test_slot = {"id": "test", "name": "테스트 틱톡 세션", "target_min": 0.5}
    bot = StockTikTokBehaviorBot(headless=False)
    res = asyncio.run(bot.execute_slot_session_async(test_slot))
    print(json.dumps(res, ensure_ascii=False, indent=2))
