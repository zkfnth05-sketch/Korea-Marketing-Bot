# -*- coding: utf-8 -*-
"""
Aura Kin Scheduler (⏰ Aura 전용 24시간 4대 슬롯 일일 10개 분산 스케줄러)
========================================================================================
- 브랜드: Aura (2030 AI 데이팅 & 서울 핫플 매칭)
- 구조:
  1. 🌅 슬롯 1 (오전 08:30~11:30): 2개
  2. ☀️ 슬롯 2 (오후 13:30~17:30): 3개
  3. 🌙 슬롯 3 (저녁 19:30~23:30): 4개 (골든 타임)
  4. 🌌 슬롯 4 (심야 00:00~02:00): 1개
  👉 일일 총합: 정확히 10개 엄선 (스마트 이월 관리)
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# UTF-8 콘솔 지원
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("AuraKinScheduler")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "data"
STATE_FILE = DATA_DIR / "aura_kin_daily_state.json"

try:
    from brands.aura.aura_kin_pipeline import AuraKinPipeline
except ImportError:
    from aura_kin_pipeline import AuraKinPipeline


class AuraKinScheduler:
    """💖 Aura 지식iN 24시간 4대 슬롯 일일 10개 스케줄러"""

    DAILY_TARGET = 10

    SLOTS = {
        "morning": {"start": 8, "end": 12, "target": 2, "name": "🌅 오전 슬롯"},
        "afternoon": {"start": 13, "end": 18, "target": 3, "name": "☀️ 오후 슬롯"},
        "evening": {"start": 19, "end": 24, "target": 4, "name": "🌙 저녁 피크 슬롯"},
        "night": {"start": 0, "end": 3, "target": 1, "name": "🌌 심야 슬롯"}
    }

    def __init__(self):
        self.pipeline = AuraKinPipeline()

    def get_current_slot(self) -> Dict[str, Any]:
        """현재 시간에 해당하는 슬롯 반환"""
        hour = datetime.now().hour
        if 8 <= hour < 12:
            return {"key": "morning", **self.SLOTS["morning"]}
        elif 13 <= hour < 18:
            return {"key": "afternoon", **self.SLOTS["afternoon"]}
        elif 19 <= hour <= 23:
            return {"key": "evening", **self.SLOTS["evening"]}
        elif 0 <= hour < 3:
            return {"key": "night", **self.SLOTS["night"]}
        else:
            return {"key": "idle", "name": "☕ 휴식 시간대", "target": 0}

    def _load_state(self) -> Dict[str, Any]:
        today_str = datetime.now().strftime("%Y-%m-%d")
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("date") == today_str:
                        return data
            except Exception:
                pass
        return {
            "date": today_str,
            "daily_total": 0,
            "slots": {"morning": 0, "afternoon": 0, "evening": 0, "night": 0},
            "last_run_at": ""
        }

    def _save_state(self, state: Dict[str, Any]):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def trigger_scheduled_catch(self) -> Dict[str, Any]:
        """데몬 또는 스케줄러가 주기적으로 호출하는 함수"""
        state = self._load_state()
        slot = self.get_current_slot()

        logger.info(f"⏰ [Aura 지식iN 스케줄러] 현재 슬롯: {slot['name']} (금일 총 {state['daily_total']}/{self.DAILY_TARGET}개 완료)")

        # 일일 상한선 10개 체크
        if state["daily_total"] >= self.DAILY_TARGET:
            logger.info("✅ 오늘 목표 10개 낚아채기 완료! 내일까지 대기합니다.")
            return {"success": False, "status": "daily_quota_full", "message": "금일 10개 완료"}

        # 파이프라인 1회 실행
        res = self.pipeline.run_catch_cycle(max_catch=1)
        if res.get("success"):
            state["daily_total"] += 1
            slot_key = slot.get("key", "other")
            if slot_key in state["slots"]:
                state["slots"][slot_key] += 1
            state["last_run_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._save_state(state)
            logger.info(f"🎉 [성공 기록] 오늘 누적: {state['daily_total']} / {self.DAILY_TARGET}개")

        return res


if __name__ == "__main__":
    scheduler = AuraKinScheduler()
    res = scheduler.trigger_scheduled_catch()
    print("Scheduler Run Result:", res)
