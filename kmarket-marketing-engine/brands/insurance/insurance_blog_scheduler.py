# -*- coding: utf-8 -*-
"""
🛡️ InsureBalance Blog Scheduler (보험 전용 정기 자동 발행 스케줄러)
====================================================================
- 매일 3회 (09:00, 13:00, 19:00 KST) 정기 자동 발행
- 100대 마스터 주제 풀을 단 1개의 중복 없이 순차 회전 (data/insurance_blog_rotation_state.json)
- Gemini 2,000자 칼럼 + 16:9 맞춤 사진 1장 ➔ 3대 블로그(네이버, 티스토리, 브런치) 동시 무인 배포
- 단독 테스트(--now / --blog-now) 및 대시보드 연동 완벽 지원
"""

import sys
import time
import json
import logging
import threading
import datetime
from datetime import datetime as dt, timezone, timedelta
from typing import Dict, Any, Optional
from pathlib import Path

# UTF-8 콘솔 출력 지원
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("InsuranceBlogScheduler")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = DATA_DIR / "insurance_blog_rotation_state.json"

KST = timezone(timedelta(hours=9))


class InsuranceBlogScheduler:
    """InsureBalance 정기 자동 발행 스케줄러 레고 블록 (영구 순환 상태 지원)"""

    SCHEDULE_HOURS = [12, 21]  # 하루 딱 2회 (12:00, 21:00 KST)
    SCHEDULE_MINUTE = 0

    def __init__(self):
        self._is_running = False
        self._thread: Optional[threading.Thread] = None
        self._last_published_hour: Optional[int] = None
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """순환 상태 파일 로드 또는 초기화"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️ 상태 파일 파싱 실패, 초기화합니다: {e}")

        initial_state = {
            "current_topic_index": 0,
            "last_topic_id": 0,
            "last_run_time": None,
            "last_title": None,
            "published_count": 0,
            "history": []
        }
        self._save_state(initial_state)
        return initial_state

    def _save_state(self, state: Dict[str, Any]):
        """상태 파일 디스크에 안전하게 영구 저장"""
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ 상태 파일 저장 실패: {e}")

    def can_publish_today(self, max_daily_posts: int = 2) -> tuple[bool, str]:
        """하루 최대 2건 제한 및 최소 4시간 발행 간격 엄격 검증"""
        today_str = dt.now().strftime("%Y-%m-%d")
        history = self.state.get("history", [])
        
        today_posts = [h for h in history if (h.get("published_at") or "").startswith(today_str)]
        if len(today_posts) >= max_daily_posts:
            return False, f"🛑 [안전 차단] 오늘 이미 일일 최대 발행 한도({len(today_posts)}/{max_daily_posts}회)를 모두 완료했습니다. 저품질 방지를 위해 추가 발행을 차단합니다."
            
        if today_posts:
            last_pub_str = today_posts[0].get("published_at", "")
            try:
                last_dt = dt.strptime(last_pub_str, "%Y-%m-%d %H:%M:%S")
                diff_hours = (dt.now() - last_dt).total_seconds() / 3600.0
                if diff_hours < 4.0:
                    return False, f"⚠️ [안전 쿨타임] 직전 발행 후 최소 4시간이 지나지 않았습니다 (경과: {diff_hours:.1f}시간). 블로그 도배 방지를 위해 대기합니다."
            except Exception:
                pass
                
        return True, "발행 가능"

    def run_one_cycle(self, force_topic_id: Optional[int] = None) -> Dict[str, Any]:
        """
        주제 1개에 대해 안전 검증 후 수동 1회 발행
        (하루 최대 2건 엄격 제한 & 도배 원천 차단)
        """
        can_pub, reason = self.can_publish_today(max_daily_posts=2)
        if not can_pub and force_topic_id is None:
            logger.warning(reason)
            return {"status": "BLOCKED_DAILY_CAP", "message": reason}

        from brands.insurance.insurance_blog_engine import InsuranceBlogEngine
        from brands.insurance.insurance_100_topics import INSURANCE_100_TOPICS
        from brands.insurance.insurance_multi_publisher import InsuranceMultiPublisher

        engine = InsuranceBlogEngine()
        total_topics = len(INSURANCE_100_TOPICS)

        # 다음 순환 주제 결정
        if force_topic_id is not None:
            topic_id = force_topic_id
        else:
            cur_idx = self.state.get("current_topic_index", 0)
            topic_id = (cur_idx % total_topics) + 1

        logger.info(f"🚀 [InsuranceScheduler] 주제 #{topic_id} 정기 포스팅 사이클 시작...")
        package = engine.build_article_package(topic_id=topic_id, use_gemini=True, generate_photo=True)

        # 3대 채널(네이버, 티스토리, 브런치) 동시 무인 자동 배포!
        publisher = InsuranceMultiPublisher()
        publish_results = publisher.publish_all(package, landing_url=engine.LANDING_URL)

        now_str = dt.now().strftime("%Y-%m-%d %H:%M:%S")

        # 상태 갱신
        next_idx = (self.state.get("current_topic_index", 0) + 1) % total_topics
        history_entry = {
            "topic_id": topic_id,
            "title": package["title"],
            "title_naver": package.get("title_naver"),
            "title_tistory": package.get("title_tistory"),
            "title_brunch": package.get("title_brunch"),
            "category": package["category"],
            "image_url": package.get("image_url", ""),
            "published_at": now_str,
            "publish_results": publish_results
        }

        self.state["current_topic_index"] = next_idx
        self.state["last_topic_id"] = topic_id
        self.state["last_run_time"] = now_str
        self.state["last_title"] = package["title"]
        self.state["published_count"] = self.state.get("published_count", 0) + 1

        hist = self.state.get("history", [])
        hist.insert(0, history_entry)
        self.state["history"] = hist[:100]

        self._save_state(self.state)

        return {
            "topic_id": topic_id,
            "title": package["title"],
            "title_naver": package.get("title_naver"),
            "title_tistory": package.get("title_tistory"),
            "title_brunch": package.get("title_brunch"),
            "image_url": package.get("image_url", ""),
            "published_at": now_str,
            "next_topic_id": (next_idx % total_topics) + 1,
            "publish_results": publish_results
        }

    run_once_now = run_one_cycle

    def is_running(self) -> bool:
        return self._is_running

    def start(self):
        """스케줄러 백그라운드 스레드 시작"""
        if self._is_running:
            logger.info("ℹ️ [InsuranceScheduler] 이미 실행 중입니다.")
            return

        self._is_running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="InsuranceBlogSchedulerThread")
        self._thread.start()
        logger.info(f"🚀 [InsuranceScheduler] 정기 스케줄러 가동 시작 (발행 시각: {self.SCHEDULE_HOURS}시 KST)")

    def stop(self):
        """스케줄러 정지"""
        if not self._is_running:
            return
        self._is_running = False
        logger.info("🛑 [InsuranceScheduler] 정기 스케줄러 정지 요청 완료")

    def _loop(self):
        while self._is_running:
            try:
                now_kst = dt.now(KST)
                current_hour = now_kst.hour
                current_min = now_kst.minute

                if current_hour in self.SCHEDULE_HOURS and current_min == self.SCHEDULE_MINUTE:
                    if self._last_published_hour != current_hour:
                        logger.info(f"⏰ [InsuranceScheduler] 정기 발행 시각 도달: {current_hour:02d}:{current_min:02d} KST")
                        self._last_published_hour = current_hour
                        self.run_one_cycle()

                if current_min != self.SCHEDULE_MINUTE:
                    self._last_published_hour = None

            except Exception as e:
                logger.error(f"❌ [InsuranceScheduler] 루프 에러: {e}")

            time.sleep(10)


# 글로벌 싱글톤 인스턴스
insurance_blog_scheduler = InsuranceBlogScheduler()
