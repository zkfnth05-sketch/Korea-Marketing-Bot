# -*- coding: utf-8 -*-
"""
Insurance YouTube Stealth Incubator (🛡️ 보험 리밸런스 전용 유튜브 인간 행동 웜업 로봇)
====================================================================================
- 역할:
  1. Playwright 기반 영구 프로필(Persistent Context)로 유튜브 접속
  2. 안티 핑거프린팅 (navigator.webdriver 은폐, 크롬 런타임 위장, User-Agent 풀)
  3. 보험/실손/재테크/절약 관련 쇼츠 피드 진입 및 3~4개 영상 실제 시청 (각 15~35초 체류)
  4. 인간 친화형 베지어 곡선 마우스 이동 및 마우스 휠 스크롤 시뮬레이션
  5. 자연스러운 좋아요(Like) 1회 클릭 시뮬레이션으로 계정 신뢰도(Trust Score) 풀충전
- 원칙: Rule 1 (독립 레고 블록), Rule 5 (땜질 코딩 금지) 준수
"""

import os
import sys
import time
import json
import random
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

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

logger = logging.getLogger("InsuranceYouTubeIncubator")

_UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]

# 보험/재테크/실손 웜업 탐색 키워드 풀
_INSURANCE_KEYWORDS = [
    "실비보험 청구 팁",
    "운전자보험 1만원 꿀팁",
    "암보험 가입 전 필수 확인",
    "숨은 보험금 찾기",
    "보험료 다이어트 비법",
    "2030 직장인 가성비 보험",
    "치아보험 임플란트 팁"
]


def _bezier_points(start: tuple, end: tuple, steps: int = 20) -> List[tuple]:
    """인간 친화형 베지어 곡선 마우스 이동 좌표 생성"""
    sx, sy = start
    ex, ey = end
    cx = (sx + ex) / 2 + random.randint(-40, 40)
    cy = (sy + ey) / 2 + random.randint(-30, 30)
    points = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * sx + 2 * (1 - t) * t * cx + t ** 2 * ex
        y = (1 - t) ** 2 * sy + 2 * (1 - t) * t * cy + t ** 2 * ey
        points.append((int(x), int(y)))
    return points


class InsuranceYouTubeStealthIncubator:
    """🛡️ 보험 리밸런스 전담 유튜브 0뷰 탈출 인간 웜업 로봇"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.profile_dir = CURRENT_DIR / "youtube_chrome_profile"
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.session_log_path = CURRENT_DIR / "youtube_warmup_history.json"

    def _get_anti_detect_script(self) -> str:
        """Playwright 핑거프린트 은폐 스크립트"""
        return """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.navigator.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', { get: () => ['ko-KR', 'ko', 'en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
                    { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' }
                ]
            });
        """

    def run_warmup_session(self, watch_count: int = 3, target_keyword: Optional[str] = None) -> Dict[str, Any]:
        """
        유튜브 웜업 세션 실행 (보험 쇼츠 3~4개 시청 + 체류 + 좋아요 1회 시뮬레이션)
        """
        from playwright.sync_api import sync_playwright

        selected_keyword = target_keyword or random.choice(_INSURANCE_KEYWORDS)
        session_ua = random.choice(_UA_POOL)
        logger.info("=" * 60)
        logger.info(f"🛡️ [보험 리밸런스 유튜브 웜업 시작] 탐색 키워드: '{selected_keyword}' | 목표 시청: {watch_count}편")
        logger.info("=" * 60)

        watched_videos = []
        likes_given = 0
        start_time = time.time()

        try:
            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.profile_dir),
                    headless=self.headless,
                    user_agent=session_ua,
                    viewport={"width": 1280 + random.randint(-30, 30), "height": 850 + random.randint(-20, 20)},
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-infobars",
                    ]
                )
                page = context.new_page()
                page.add_init_script(self._get_anti_detect_script())

                # 1. 유튜브 홈 접속
                logger.info("🌐 [1단계] 유튜브 홈 접속 중...")
                page.goto("https://www.youtube.com", wait_until="domcontentloaded", timeout=45000)
                time.sleep(random.uniform(2.5, 4.0))

                # 2. 보험/재테크 쇼츠 검색창 이동
                search_url = f"https://www.youtube.com/results?search_query={selected_keyword}&sp=CAISAhAB"
                logger.info(f"🔍 [2단계] 쇼츠 필터 검색 이동: {selected_keyword}")
                page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
                time.sleep(random.uniform(3.0, 5.0))

                # 3. 쇼츠 썸네일 탐색
                shorts_links = page.locator("a#thumbnail[href*='/shorts/']").all()
                if not shorts_links:
                    page.goto("https://www.youtube.com/shorts", wait_until="domcontentloaded", timeout=45000)
                    time.sleep(3.0)

                # 4. 순차 쇼츠 시청
                for idx in range(1, watch_count + 1):
                    watch_sec = random.uniform(15.0, 28.0)
                    logger.info(f"👀 [{idx}/{watch_count}] 쇼츠 영상 인간 시청 중... (체류: {watch_sec:.1f}초)")

                    try:
                        p_start = (random.randint(200, 400), random.randint(300, 500))
                        p_end = (random.randint(500, 700), random.randint(400, 600))
                        for x, y in _bezier_points(p_start, p_end, steps=10):
                            page.mouse.move(x, y)
                            time.sleep(0.02)
                    except Exception:
                        pass

                    time.sleep(watch_sec)

                    # 좋아요 1회 시뮬레이션
                    if idx == 1 and likes_given == 0:
                        try:
                            like_btn = page.locator("button[aria-label*='좋아요']").first
                            if like_btn and like_btn.is_visible():
                                like_btn.click()
                                likes_given += 1
                                logger.info("❤️ [인간 행동] 영상 좋아요 1회 클릭 완료")
                        except Exception:
                            pass

                    # 다음 영상 스크롤
                    page.keyboard.press("ArrowDown")
                    time.sleep(random.uniform(2.0, 3.5))

                context.close()

            elapsed = round(time.time() - start_time, 1)
            report = {
                "status": "success",
                "brand": "insurance",
                "keyword": selected_keyword,
                "watch_count": watch_count,
                "likes_given": likes_given,
                "elapsed_sec": elapsed,
                "timestamp": get_now_kst_str()
            }
            self._save_log(report)
            logger.info(f"✅ [보험 리밸런스 유튜브 웜업 완료] 소요: {elapsed}초 | 신뢰도 충전 완료")
            return report

        except Exception as e:
            logger.warning(f"⚠️ [보험 리밸런스 유튜브 웜업 예외] {e}")
            return {"status": "error", "error": str(e), "brand": "insurance"}

    def _save_log(self, data: Dict[str, Any]):
        logs = []
        if self.session_log_path.exists():
            try:
                with open(self.session_log_path, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                logs = []
        logs.append(data)
        try:
            with open(self.session_log_path, "w", encoding="utf-8") as f:
                json.dump(logs[-30:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    inc = InsuranceYouTubeStealthIncubator(headless=False)
    res = inc.run_warmup_session(watch_count=2)
    print("웜업 결과:", res)
