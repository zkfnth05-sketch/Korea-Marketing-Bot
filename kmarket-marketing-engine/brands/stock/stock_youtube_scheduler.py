# -*- coding: utf-8 -*-
"""
StockMaster YouTube Scheduler (⏰ StockMaster AI 유튜브 쇼츠 하루 3회 무인 자동 송출 스케줄러)
==========================================================================================
- 역할:
  1. 📈 StockMaster AI 전용 유튜브 쇼츠 [하루 3회 정시 무인 배포] 관제
  2. 3대 주식 황금 송출 시간대:
     - 🌅 1차 (장전 골든타임): 08:30 (개장 직전 오늘 급등 예상 테마)
     - 🌇 2차 (장마감 골든타임): 15:40 (당일 외국인/기관 쌍끌이 수급 결산)
     - 🌙 3차 (야간 내일장 대비 피크): 21:30 (내일 코스피/코스닥 주도주 & 수급 분석)
  3. 송출 직전 [StockYouTubeStealthIncubator] 웜업 ➔ [StockYouTubeAPIPublisher] 0.1초 업로드 + 고정댓글
  4. 8대 주식 퀀트 주제(1~8번) 자율 순환(Rotation) 영구 기록
- 원칙: Rule 1 (독립 레고 블록), Rule 6 (24시간 무인 자율 구동), Rule 7 (공식 검색어 '스톡마스터 AI')
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

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

from config import BASE_DIR, get_now_kst_str
from brands.stock.stock_youtube_hybrid_pilot import StockYouTubeHybridPilot

logger = logging.getLogger("StockYouTubeScheduler")


class StockYouTubeScheduler:
    """⏰ StockMaster AI 유튜브 쇼츠 하루 3회 무인 정시 관제 스케줄러"""

    SCHEDULE_SLOTS = [
        {"slot": 1, "time": "08:30", "name": "장전 급등 브리핑"},
        {"slot": 2, "time": "15:40", "name": "장마감 수급 결산"},
        {"slot": 3, "time": "21:30", "name": "야간 미증시 피크"}
    ]

    def __init__(self, headless: bool = True):
        self.pilot = StockYouTubeHybridPilot(headless=headless)
        self.state_file = CURRENT_DIR / "youtube_schedule_state.json"

    def _load_state(self) -> Dict[str, Any]:
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"last_topic_id": 0, "published_today": []}

    def _save_state(self, state: Dict[str, Any]):
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"상태 파일 저장 실패: {e}")

    def get_next_topic_id(self) -> int:
        """1~8번 주제 자율 순환"""
        state = self._load_state()
        last_id = state.get("last_topic_id", 0)
        next_id = (last_id % 8) + 1
        state["last_topic_id"] = next_id
        self._save_state(state)
        return next_id

    def trigger_single_broadcast(self, slot_name: str = "수동 실행", topic_id: Optional[int] = None) -> Dict[str, Any]:
        """지정된 슬롯에 맞춰 [웜업 + 0.1초 API 업로드 + 고정댓글] 1회 송출"""
        target_topic = topic_id or self.get_next_topic_id()
        logger.info("=" * 70)
        logger.info(f"⏰ [StockMaster AI 유튜브 1일 3회 정시 송출] 슬롯: {slot_name} | 주제: #{target_topic}")
        logger.info("=" * 70)

        res = self.pilot.execute_hybrid_deployment(
            topic_id=target_topic,
            skip_warmup=False,
            privacy_status="public"
        )

        # 오늘 발행 기록 누적
        state = self._load_state()
        today_str = datetime.now().strftime("%Y-%m-%d")
        pub_list = state.get("published_today", [])
        pub_list.append({
            "date": today_str,
            "slot": slot_name,
            "topic_id": target_topic,
            "time": get_now_kst_str(),
            "status": res.get("status")
        })
        state["published_today"] = pub_list[-30:]
        self._save_state(state)

        return res

    def run_daemon_loop(self):
        """24시간 365일 백그라운드 상주 루프 (08:30, 15:40, 21:30에 스스로 기상 및 송출)"""
        logger.info("=" * 70)
        logger.info("🤖 [StockMaster AI 유튜브 하루 3회 무인 상주 데몬 가동]")
        logger.info("  • 1차 송출: 08:30 (장전 급등 브리핑)")
        logger.info("  • 2차 송출: 15:40 (장마감 수급 결산)")
        logger.info("  • 3차 송출: 21:30 (야간 미증시 피크)")
        logger.info("=" * 70)

        triggered_today = set()
        current_date = datetime.now().strftime("%Y-%m-%d")

        while True:
            now = datetime.now()
            today_str = now.strftime("%Y-%m-%d")
            time_hm = now.strftime("%H:%M")

            # 날짜 바뀌면 트리거 셋 초기화
            if today_str != current_date:
                triggered_today.clear()
                current_date = today_str

            # 슬롯 시간 점검
            for slot in self.SCHEDULE_SLOTS:
                target_time = slot["time"]
                slot_id = f"{today_str}_{target_time}"

                if time_hm == target_time and slot_id not in triggered_today:
                    logger.info(f"🔔 [정시 알람] {target_time} {slot['name']} 도래 -> 무인 송출 시작!")
                    triggered_today.add(slot_id)
                    try:
                        self.trigger_single_broadcast(slot_name=slot["name"])
                    except Exception as e:
                        logger.error(f"❌ 정시 송출 에러: {e}")

            time.sleep(30)


if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    parser = argparse.ArgumentParser(description="StockMaster YouTube Daily 3x Scheduler")
    parser.add_argument("--daemon", action="store_true", help="24시간 백그라운드 데몬 상주 모드")
    parser.add_argument("--once", action="store_true", help="즉시 1회 시험 송출")
    parser.add_argument("--topic", type=int, default=None, help="지정 주제 번호")
    args = parser.parse_args()

    scheduler = StockYouTubeScheduler(headless=True)
    if args.daemon:
        scheduler.run_daemon_loop()
    elif args.once:
        scheduler.trigger_single_broadcast(slot_name="원클릭 시험 송출", topic_id=args.topic)
    else:
        parser.print_help()
