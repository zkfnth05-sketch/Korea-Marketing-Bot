# -*- coding: utf-8 -*-
"""
[StockMaster AI] 30초 퀀트 숏폼 자율 스케줄러 (Lego Block)
========================================================================
- 평일 (월~금 정규 장 운영일):
  * 1차 (09:30 KST): 장 초반 수급 폭발 & 당일 1위 주도주 발굴
  * 2차 (12:00 KST): 점심 시황 & 계량 리스크 가드
  * 3차 (15:00 KST): 장 마감 전 종가 결산 & 총괄 소개
  * 6개 주제(1~6) 순차 롤링 (2일 1회 완주)
- 주말 / 공휴일 (휴장일):
  * 1차 (11:00 KST): [주제 03] AI 리스크 가드 (원금보호 & 주말 계좌 점검)
  * 2차 (18:00 KST): [주제 06] 스톡마스터 AI 총괄 소개 (월요일 개장 대비)
- 24시간 365일 무인 자율 구동 & 대시보드 제어 지원
"""

import json
import logging
import threading
import time
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("StockShortsScheduler")
logger.setLevel(logging.INFO)

ROOT = Path(__file__).resolve().parent.parent.parent
STATE_FILE = ROOT / "scratch" / "stock_shorts_schedule_state.json"

# 2026~2027 대한민국 주요 법정 공휴일 (KRX 휴장일)
KRX_HOLIDAYS_2026_2027 = {
    # 2026년
    "2026-01-01",  # 신정
    "2026-02-16", "2026-02-17", "2026-02-18",  # 설날 연휴
    "2026-03-01", "2026-03-02",  # 3·1절 및 대체공휴일
    "2026-05-01",  # 근로자의 날 (KRX 휴장)
    "2026-05-05",  # 어린이날
    "2026-05-24", "2026-05-25",  # 부처님오신날 및 대체공휴일
    "2026-06-06",  # 현충일
    "2026-08-15", "2026-08-17",  # 광복절 및 대체공휴일
    "2026-09-24", "2026-09-25", "2026-09-26",  # 추석 연휴
    "2026-10-03", "2026-10-05",  # 개천절 및 대체공휴일
    "2026-10-09",  # 한글날
    "2026-12-25",  # 성탄절
    "2026-12-31",  # 연말 휴장일
    # 2027년
    "2027-01-01", "2027-02-05", "2027-02-06", "2027-02-07",
    "2027-03-01", "2027-05-01", "2027-05-05", "2027-05-13",
    "2027-06-06", "2027-08-15", "2027-09-14", "2027-09-15",
    "2027-09-16", "2027-10-03", "2027-10-09", "2027-12-25", "2027-12-31"
}


class StockShortsScheduler:
    """📈 StockMaster AI 30초 숏폼 전담 자율 스케줄러"""

    def __init__(self, state_path: Path = STATE_FILE):
        self.state_path = state_path
        self._lock = threading.Lock()
        self._ensure_state_file()

    def _ensure_state_file(self):
        """스케줄러 상태 파일 초기화"""
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.state_path.exists():
            initial_state = {
                "daemon_enabled": True,
                "current_topic_index": 1,  # 1 ~ 6
                "weekday_slots": {
                    "slot_0930": {"time": "09:30", "enabled": True, "label": "장 초반 수급·주도주"},
                    "slot_1200": {"time": "12:00", "enabled": True, "label": "점심 시황·리스크"},
                    "slot_1500": {"time": "15:00", "enabled": True, "label": "장 마감 결산·총괄"}
                },
                "weekend_slots": {
                    "slot_1100": {"time": "11:00", "enabled": True, "topic_id": 3, "label": "주말 계좌 리스크 점검"},
                    "slot_1800": {"time": "18:00", "enabled": True, "topic_id": 6, "label": "월요일 개장 대비 총괄 소개"}
                },
                "executed_slots_today": [],
                "last_run_date": "",
                "last_run_info": {},
                "total_shorts_created": 0,
                "history": []
            }
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(initial_state, f, ensure_ascii=False, indent=2)

    def _load_state(self) -> Dict[str, Any]:
        with self._lock:
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {
                    "daemon_enabled": True,
                    "current_topic_index": 1,
                    "weekday_slots": {
                        "slot_0930": {"time": "09:30", "enabled": True, "label": "장 초반 수급·주도주"},
                        "slot_1200": {"time": "12:00", "enabled": True, "label": "점심 시황·리스크"},
                        "slot_1500": {"time": "15:00", "enabled": True, "label": "장 마감 결산·총괄"}
                    },
                    "weekend_slots": {
                        "slot_1100": {"time": "11:00", "enabled": True, "topic_id": 3, "label": "주말 계좌 리스크 점검"},
                        "slot_1800": {"time": "18:00", "enabled": True, "topic_id": 6, "label": "월요일 개장 대비 총괄 소개"}
                    },
                    "executed_slots_today": [],
                    "last_run_date": "",
                    "last_run_info": {},
                    "total_shorts_created": 0,
                    "history": []
                }

    def _save_state(self, state: Dict[str, Any]):
        with self._lock:
            try:
                with open(self.state_path, "w", encoding="utf-8") as f:
                    json.dump(state, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.error(f"상태 저장 실패: {e}")

    @staticmethod
    def is_krx_open_day(target_date: Optional[date] = None) -> bool:
        """오늘이 한국 주식시장(KRX) 정규 개장일인지 확인 (토/일/공휴일 제외)"""
        if target_date is None:
            target_date = datetime.now().date()
        # 토요일(5), 일요일(6) 제외
        if target_date.weekday() >= 5:
            return False
        # 공휴일 제외
        date_str = target_date.strftime("%Y-%m-%d")
        if date_str in KRX_HOLIDAYS_2026_2027:
            return False
        return True

    def get_status(self) -> Dict[str, Any]:
        """대시보드 실시간 현황 API용 상태 조회"""
        state = self._load_state()
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        is_open = self.is_krx_open_day(now.date())
        current_time_str = now.strftime("%H:%M")

        # 오늘의 슬롯 리스트 결정
        active_slots = {}
        if is_open:
            active_slots = state.get("weekday_slots", {})
            mode_label = "🟢 평일 정규장 모드 (1일 3회 순차 롤링)"
            mode_type = "weekday"
        else:
            active_slots = state.get("weekend_slots", {})
            mode_label = "🔵 주말·휴장일 브랜딩 모드 (1일 2회 특화)"
            mode_type = "weekend"

        # 다음 예정 슬롯 탐색
        next_slot = None
        executed_today = state.get("executed_slots_today", []) if state.get("last_run_date") == today_str else []

        for slot_key, slot_data in active_slots.items():
            if not slot_data.get("enabled", True):
                continue
            slot_time = slot_data.get("time", "00:00")
            if slot_time > current_time_str and slot_key not in executed_today:
                next_slot = {
                    "slot_key": slot_key,
                    "time": slot_time,
                    "label": slot_data.get("label", ""),
                    "expected_topic": slot_data.get("topic_id", state.get("current_topic_index", 1))
                }
                break

        if not next_slot and active_slots:
            # 오늘의 모든 슬롯이 지났으면 내일 첫 슬롯 표시
            first_key = list(active_slots.keys())[0]
            first_data = active_slots[first_key]
            next_slot = {
                "slot_key": first_key,
                "time": f"내일 {first_data.get('time', '09:30')}",
                "label": first_data.get("label", ""),
                "expected_topic": first_data.get("topic_id", state.get("current_topic_index", 1))
            }

        return {
            "success": True,
            "daemon_enabled": state.get("daemon_enabled", True),
            "is_krx_open_day": is_open,
            "mode_type": mode_type,
            "mode_label": mode_label,
            "current_time": current_time_str,
            "current_topic_index": state.get("current_topic_index", 1),
            "next_slot": next_slot,
            "weekday_slots": state.get("weekday_slots", {}),
            "weekend_slots": state.get("weekend_slots", {}),
            "executed_slots_today": executed_today,
            "total_shorts_created": state.get("total_shorts_created", 0),
            "last_run_info": state.get("last_run_info", {}),
            "history": state.get("history", [])[-10:]
        }

    def trigger_now(self, topic_id: Optional[int] = None, force_fresh_record: bool = True) -> Dict[str, Any]:
        """원클릭 즉시 숏폼 생성 (수동 또는 스케줄러 공통)"""
        from brands.stock.stock_quant_shorts_builder import StockQuantShortsBuilder

        state = self._load_state()
        if topic_id is None:
            topic_id = state.get("current_topic_index", 1)

        logger.info(f"🎬 [StockShortsScheduler] 숏폼 빌드 시작! (주제 #{topic_id})")
        builder = StockQuantShortsBuilder()
        build_result = builder.build_shorts_by_topic(topic_id=topic_id, force_fresh_record=force_fresh_record)

        # 상태 업데이트 및 다음 주제 인덱스 롤링 (1->2->3->4->5->6->1)
        next_topic = (topic_id % 6) + 1
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        run_record = {
            "timestamp": now_str,
            "topic_id": topic_id,
            "topic_title": build_result.get("topic_title", f"주제 #{topic_id}"),
            "output_mp4": build_result.get("output_mp4", ""),
            "duration": build_result.get("total_duration", 30.0),
            "file_size_mb": round(Path(build_result.get("output_mp4", "")).stat().st_size / (1024 * 1024), 2) if build_result.get("output_mp4") and Path(build_result.get("output_mp4")).exists() else 0.0,
            "status": "성공" if build_result.get("output_mp4") else "실패"
        }

        state["current_topic_index"] = next_topic
        state["last_run_date"] = datetime.now().strftime("%Y-%m-%d")
        state["last_run_info"] = run_record
        state["total_shorts_created"] = state.get("total_shorts_created", 0) + 1

        history = state.get("history", [])
        history.append(run_record)
        state["history"] = history[-50:]  # 최근 50건 유지

        self._save_state(state)
        logger.info(f"🎉 [StockShortsScheduler] 주제 #{topic_id} 숏폼 제작 완료 -> 다음 롤링 주제: #{next_topic}")
        return {
            "success": True,
            "run_record": run_record,
            "next_topic_id": next_topic
        }

    def check_and_run_slot(self) -> Optional[Dict[str, Any]]:
        """정시 스케줄 도달 여부 점검 및 자동 실행"""
        state = self._load_state()
        if not state.get("daemon_enabled", True):
            return None

        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        current_hm = now.strftime("%H:%M")
        is_open = self.is_krx_open_day(now.date())

        # 날짜가 바뀌었으면 오늘 실행 슬롯 목록 리셋
        if state.get("last_run_date") != today_str:
            state["executed_slots_today"] = []
            state["last_run_date"] = today_str
            self._save_state(state)

        executed_today = set(state.get("executed_slots_today", []))

        # 슬롯 정의 선택
        if is_open:
            slots = state.get("weekday_slots", {})
        else:
            slots = state.get("weekend_slots", {})

        for slot_key, slot_info in slots.items():
            if not slot_info.get("enabled", True):
                continue
            slot_time = slot_info.get("time", "")

            # 현재 시각(HH:MM)과 슬롯 시간이 일치하고 오늘 아직 실행 안 된 경우
            if slot_time == current_hm and slot_key not in executed_today:
                logger.info(f"⏰ [StockShortsScheduler] 정시 슬롯 도달! ({slot_key} - {slot_time}, 개장일={is_open})")

                # 주말이면 고정 주제(3 또는 6), 평일이면 순차 롤링 주제
                if not is_open:
                    topic_to_run = slot_info.get("topic_id", 3)
                else:
                    topic_to_run = state.get("current_topic_index", 1)

                # 실행
                res = self.trigger_now(topic_id=topic_to_run, force_fresh_record=True)

                # 오늘 실행 슬롯에 추가
                state = self._load_state()
                executed_list = state.get("executed_slots_today", [])
                executed_list.append(slot_key)
                state["executed_slots_today"] = executed_list
                self._save_state(state)
                return res

        return None

    def run_continuous_daemon(self, check_interval_seconds: int = 20):
        """24시간 365일 백그라운드 상주 무인 데몬 루프"""
        logger.info("🚀 [StockShortsScheduler] 24시간 365일 무인 자율 숏폼 스케줄러 데몬 가동 시작!")
        while True:
            try:
                self.check_and_run_slot()
            except Exception as e:
                logger.error(f"❌ [StockShortsScheduler 데몬 루프 에러] {e}")
            time.sleep(check_interval_seconds)

    def update_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """대시보드에서 설정 변경 시 저장"""
        state = self._load_state()
        if "daemon_enabled" in config_data:
            state["daemon_enabled"] = bool(config_data["daemon_enabled"])
        if "weekday_slots" in config_data:
            state["weekday_slots"].update(config_data["weekday_slots"])
        if "weekend_slots" in config_data:
            state["weekend_slots"].update(config_data["weekend_slots"])
        if "current_topic_index" in config_data:
            state["current_topic_index"] = int(config_data["current_topic_index"])

        self._save_state(state)
        return self.get_status()
