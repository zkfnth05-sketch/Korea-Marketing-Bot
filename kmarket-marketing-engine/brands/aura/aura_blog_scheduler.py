# -*- coding: utf-8 -*-
"""
Aura Blog Scheduler (💖 Aura 2030 매거진 하루 2회 자율 순환 스케줄러)
===================================================================
- 브랜드: Aura (2030 AI 데이팅 / 매칭 라운지)
- 역할:
  1. 하루 2회 골든타임 (낮 12:00, 밤 21:00) 정기 자동 발행
  2. 100대 주제 풀을 50일간 단 1개의 중복 없이 순차 회전 (data/aura_blog_rotation_state.json)
  3. Gemini 2,000자 칼럼 + 주제 맞춤 16:9 사진 1장 동시 생성 및 배포
  4. 단독 테스트(--now) 및 24시간 백그라운드 상주(--daemon) 완벽 지원
"""

import os
import sys
import time
import json
import logging
import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# UTF-8 콘솔 출력 지원
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("AuraBlogScheduler")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = DATA_DIR / "aura_blog_rotation_state.json"

# 골든타임 정의 (KST 기준)
GOLDEN_HOURS = [12, 21]  # 낮 12:00, 밤 21:00


class AuraBlogScheduler:
    """💖 Aura 2030 매거진 하루 2회 자율 순환 스케줄러"""

    def __init__(self):
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
            "last_run_time": "",
            "last_title": "",
            "published_count": 0,
            "history": []
        }
        self._save_state(initial_state)
        return initial_state

    def _save_state(self, state: Dict[str, Any]):
        """상태 파일 저장"""
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ 상태 저장 실패: {e}")

    def get_status(self) -> Dict[str, Any]:
        """현재 발행 및 순환 상태 반환"""
        return {
            "brand": "aura",
            "magazine_name": "💖 Aura 2030 매거진",
            "total_topics": 100,
            "current_topic_index": self.state.get("current_topic_index", 0),
            "next_topic_id": (self.state.get("current_topic_index", 0) % 100) + 1,
            "last_run_time": self.state.get("last_run_time", "발행 이력 없음"),
            "last_title": self.state.get("last_title", "-"),
            "published_count": self.state.get("published_count", 0),
            "daily_schedule": "하루 2회 (12:00 / 21:00 KST)",
            "cycle_days": "50일 무중복 순환 (100개 / 2)"
        }

    def run_one_cycle(self, force_topic_id: Optional[int] = None) -> Dict[str, Any]:
        """
        주제 1개에 대해 Gemini 칼럼 작성 + 맞춤 사진 1장 생성 + 상태 갱신
        """
        from brands.aura.aura_blog_engine import AuraBlogEngine
        from brands.aura.aura_100_topics import AURA_100_TOPICS

        engine = AuraBlogEngine()
        total_topics = len(AURA_100_TOPICS)

        # 다음 순환 주제 결정
        if force_topic_id is not None:
            topic_id = force_topic_id
        else:
            cur_idx = self.state.get("current_topic_index", 0)
            topic_id = (cur_idx % total_topics) + 1

        logger.info(f"🚀 [AuraScheduler] 주제 #{topic_id} 정기 포스팅 사이클 시작...")
        package = engine.build_article_package(topic_id=topic_id, use_gemini=True, generate_photo=True)

        # 4대 채널(Aura Supabase, 네이버, 티스토리, 카카오) 동시 무인 자동 배포!
        from brands.aura.aura_multi_publisher import AuraMultiPublisher
        publisher = AuraMultiPublisher()
        publish_results = publisher.publish_all(package)

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 상태 갱신
        next_idx = (self.state.get("current_topic_index", 0) + 1) % total_topics
        history_entry = {
            "topic_id": topic_id,
            "title": package["title"],
            "title_naver": package.get("title_naver"),
            "title_tistory": package.get("title_tistory"),
            "title_kakao": package.get("title_kakao"),
            "category": package["category"],
            "image_url": package["image_url"],
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
        self.state["history"] = hist[:50]  # 최근 50건 유지

        self._save_state(self.state)

        logger.info(f"✨ [AuraScheduler] 4대 채널 배포 완성! 다음 주제 번호: #{next_idx + 1}")
        return {
            "status": "success",
            "topic_id": topic_id,
            "next_topic_id": next_idx + 1,
            "title": package["title"],
            "title_naver": package.get("title_naver"),
            "title_tistory": package.get("title_tistory"),
            "title_kakao": package.get("title_kakao"),
            "image_url": package["image_url"],
            "image_path": package["image_path"],
            "published_at": now_str,
            "publish_results": publish_results,
            "package": package
        }

    def start_daemon(self, is_running_checker=None, on_log=None):
        """하루 2회 (12:00, 21:00 KST) 자율 상주 스케줄러"""
        start_msg = "💖 [AuraScheduler] 하루 2회 (12:00 / 21:00 KST) 자율 순환 데몬 가동 시작!"
        logger.info(start_msg)
        if on_log:
            on_log(start_msg, "success")
        last_executed_slot = None

        while True:
            if is_running_checker and not is_running_checker():
                stop_msg = "⏹️ [AuraScheduler] 대시보드 정지 신호 수신으로 데몬이 종료되었습니다."
                logger.info(stop_msg)
                if on_log:
                    on_log(stop_msg, "warning")
                break

            try:
                now = datetime.datetime.now()
                hour = now.hour
                date_str = now.strftime("%Y-%m-%d")

                # 골든타임 검사 (12시 슬롯, 21시 슬롯)
                for g_hour in GOLDEN_HOURS:
                    slot_key = f"{date_str}_{g_hour}"
                    if hour == g_hour and last_executed_slot != slot_key:
                        alert_msg = f"⏰ [AuraScheduler] 골든타임 감지: {g_hour}:00 KST ➔ 4대 채널 자동 발행 시작!"
                        logger.info(alert_msg)
                        if on_log:
                            on_log(alert_msg, "info")
                        res = self.run_one_cycle()
                        fin_msg = f"🎉 [AuraScheduler] {g_hour}:00 정시 발행 완료! 주제: '{res.get('title')}' (네이버: {res.get('publish_results', {}).get('channels', {}).get('naver_blog', {}).get('url', '-')})"
                        logger.info(fin_msg)
                        if on_log:
                            on_log(fin_msg, "success")
                        last_executed_slot = slot_key
                        break

                # 10초 대기 (빠른 정지 반응)
                for _ in range(3):
                    if is_running_checker and not is_running_checker():
                        break
                    time.sleep(10)

            except KeyboardInterrupt:
                logger.info("🛑 [AuraScheduler] 사용자에 의해 데몬이 정지되었습니다.")
                break
            except Exception as e:
                err_msg = f"⚠️ [AuraScheduler] 데몬 루프 오류: {e}"
                logger.error(err_msg)
                if on_log:
                    on_log(err_msg, "error")
                time.sleep(10)


if __name__ == "__main__":
    scheduler = AuraBlogScheduler()

    if "--now" in sys.argv or "-n" in sys.argv:
        print("\n=======================================================")
        print("💖 [Aura] 2,000자 칼럼 + 맞춤 사진 1장 즉시 생성 1회 테스트")
        print("=======================================================")
        res = scheduler.run_one_cycle()
        print("\n✅ [테스트 완료 보고]")
        print(f"  - 제목: {res['title']}")
        print(f"  - 사진 URL: {res['image_url']}")
        print(f"  - 사진 파일: {res['image_path']}")
        print(f"  - 다음 발행 예정 주제 ID: #{res['next_topic_id']}")
    elif "--status" in sys.argv or "-s" in sys.argv:
        st = scheduler.get_status()
        print(json.dumps(st, ensure_ascii=False, indent=2))
    elif "--daemon" in sys.argv or "-d" in sys.argv:
        scheduler.start_daemon()
    else:
        print("사용법:")
        print("  python aura_blog_scheduler.py --now     (지금 즉시 1편 생성 및 상태 갱신)")
        print("  python aura_blog_scheduler.py --status  (현재 순환 및 발행 현황 조회)")
        print("  python aura_blog_scheduler.py --daemon  (하루 2회 12:00/21:00 자동 발행 데몬 가동)")
