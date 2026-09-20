# -*- coding: utf-8 -*-
"""
📈 StockMaster Blog Scheduler (주식 전용 정기 자동 발행 스케줄러)
=================================================================
- 매일 3회 (08:00, 12:00, 18:00 KST) 정기 자동 발행
- 100대 마스터 주제 순환 추출 ➔ Gemini 2,000자 칼럼 ➔ 16:9 맞춤 사진 ➔ 3대 블로그 동시 발행
- 대시보드(server.py)와 100% 연동되는 스레드 세이프 시작/정지 제어
"""

import sys
import time
import logging
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger("StockBlogScheduler")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

KST = timezone(timedelta(hours=9))


class StockBlogScheduler:
    """StockMaster 정기 자동 발행 스케줄러 레고 블록"""

    SCHEDULE_HOURS = [8, 12, 18]  # 08:00, 12:00, 18:00 KST
    SCHEDULE_MINUTE = 0

    def __init__(self):
        self._is_running = False
        self._thread: Optional[threading.Thread] = None
        self._last_published_hour: Optional[int] = None
        self._engine = None

    def _get_engine(self):
        if self._engine is None:
            from brands.stock.stock_blog_engine import StockBlogEngine
            self._engine = StockBlogEngine()
        return self._engine

    def is_running(self) -> bool:
        return self._is_running

    def start(self):
        """스케줄러 백그라운드 스레드 시작"""
        if self._is_running:
            logger.info("ℹ️ [StockScheduler] 이미 실행 중입니다.")
            return

        self._is_running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="StockBlogSchedulerThread")
        self._thread.start()
        logger.info(f"🚀 [StockScheduler] 정기 스케줄러 가동 시작 (발행 시각: {self.SCHEDULE_HOURS}시 KST)")

    def stop(self):
        """스케줄러 정지"""
        if not self._is_running:
            return
        self._is_running = False
        logger.info("🛑 [StockScheduler] 정기 스케줄러 정지 요청 완료")

    def _loop(self):
        """10초마다 현재 시각을 체크하여 지정 시각에 자동 발행"""
        while self._is_running:
            try:
                now_kst = datetime.now(KST)
                current_hour = now_kst.hour
                current_min = now_kst.minute

                if current_hour in self.SCHEDULE_HOURS and current_min == self.SCHEDULE_MINUTE:
                    if self._last_published_hour != current_hour:
                        logger.info(f"⏰ [StockScheduler] 정기 발행 시각 도달: {current_hour:02d}:{current_min:02d} KST")
                        self._last_published_hour = current_hour
                        self._trigger_publish()

                if current_min != self.SCHEDULE_MINUTE:
                    self._last_published_hour = None

            except Exception as e:
                logger.error(f"❌ [StockScheduler] 루프 에러: {e}")

            time.sleep(10)

    def _trigger_publish(self):
        """실제 발행 실행"""
        try:
            engine = self._get_engine()
            res = engine.publish_now()
            logger.info(f"🎉 [StockScheduler] 정기 자동 발행 성공: {res.get('article_title')}")
        except Exception as e:
            logger.error(f"❌ [StockScheduler] 정기 자동 발행 실패: {e}")

    def run_once_now(self) -> Dict[str, Any]:
        """수동 1회 즉시 실행 (대시보드 테스트용)"""
        logger.info("⚡ [StockScheduler] 수동 1회 즉시 발행 트리거")
        engine = self._get_engine()
        return engine.publish_now()

    run_one_cycle = run_once_now


# 글로벌 싱글톤 인스턴스
stock_blog_scheduler = StockBlogScheduler()
