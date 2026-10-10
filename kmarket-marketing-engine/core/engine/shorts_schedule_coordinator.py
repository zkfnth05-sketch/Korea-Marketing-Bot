# -*- coding: utf-8 -*-
"""
[독립 모듈] Shorts Schedule Coordinator (3대 브랜드 숏폼 정시 스케줄 관제 코디네이터)
=====================================================================================
- 숏폼 1편 렌더링+4대 채널 송출 실측 20~25분 소요에 맞춘 철통 30분 텀 분리:
  * 오전: Aura(09:30) ➔ Insurance(10:00, +30분) ➔ Stock(10:30, +30분)
  * 점심: Aura(12:00) ➔ Insurance(12:30, +30분) ➔ Stock(13:00, +30분)
  * 저녁: Aura(18:00) ➔ Insurance(18:30, +30분) ➔ Stock(19:00, +30분)
- 핵심 원칙:
  1. [25분 정시 윈도우 가드]: 슬롯 시작 시각으로부터 25분 이내에만 트리거. 중간 시간 재시작 시 동시 난입 0% 차단.
  2. [영구 슬롯 상태 보존]: data/shorts_schedule_state.json 파일로 서버 재부팅 시에도 당일 중복 발사 0% 차단.
  3. [1일 3회 정시 상한 보장]: 하루 오전/점심/저녁 3회를 초과하는 중복 발행 원천 차단.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("ShortsScheduleCoordinator")

STATE_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "shorts_schedule_state.json"

# 브랜드별 30분 시차 슬롯 정의 (슬롯ID, 시작_시, 시작_분, 종료_시, 종료_분, 라벨)
# 각 슬롯은 시작 시각부터 25분 동안만 유효 윈도우로 열림 (브랜드 간 겹침 0%)
BRAND_SHORTS_SLOTS: Dict[str, List[Tuple[str, int, int, int, int, str]]] = {
    "aura": [
        ("morning", 9, 30, 9, 55, "오전 09:30"),
        ("lunch", 12, 0, 12, 25, "점심 12:00"),
        ("evening", 18, 0, 18, 25, "저녁 18:00"),
    ],
    "insurance": [
        ("morning", 10, 0, 10, 25, "오전 10:00"),
        ("lunch", 12, 30, 12, 55, "점심 12:30"),
        ("evening", 18, 30, 18, 55, "저녁 18:30"),
    ],
    "stock": [
        ("morning", 10, 30, 10, 55, "오전 10:30"),
        ("lunch", 13, 0, 13, 25, "점심 13:00"),
        ("evening", 19, 0, 19, 25, "저녁 19:00"),
    ],
}


class ShortsScheduleCoordinator:
    """3대 앱 숏폼 30분 텀 무인 스케줄 관제 코디네이터"""

    def __init__(self, state_path: Optional[Path] = None):
        self.state_file = state_path or STATE_FILE
        self._ensure_state_file()

    def _ensure_state_file(self):
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            if not self.state_file.exists():
                with open(self.state_file, "w", encoding="utf-8") as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"상태 파일 초기화 경고: {e}")

    def _load_state(self) -> Dict[str, Any]:
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_state(self, state: Dict[str, Any]):
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"상태 파일 저장 실패: {e}")

    def get_slots(self, brand: str) -> List[Tuple[str, int, int, int, int, str]]:
        return BRAND_SHORTS_SLOTS.get(brand, [])

    def get_slot_description(self, brand: str) -> str:
        slots = self.get_slots(brand)
        return " / ".join([s[5] for s in slots])

    def check_slot_to_execute(self, brand: str, now: datetime) -> Optional[Tuple[str, str]]:
        """
        현재 시각에 실행해야 할 유효 슬롯이 있는지 점검.
        실행 대상인 경우 (slot_id, label) 반환, 없으면 None 반환.
        """
        slots = self.get_slots(brand)
        today_str = now.strftime("%Y-%m-%d")
        cur_min = now.hour * 60 + now.minute

        state = self._load_state()
        brand_state = state.get(brand, {})
        today_executed = set(brand_state.get(today_str, []))

        # 오늘 이미 3회 이상 송출 완료 시 일일 한도 차단
        if len(today_executed) >= 3:
            return None

        for slot_id, s_h, s_m, e_h, e_m, s_label in slots:
            start_total = s_h * 60 + s_m
            end_total = e_h * 60 + e_m

            # 25분 정시 윈도우 범위 내 && 오늘 아직 미실행
            if start_total <= cur_min <= end_total and slot_id not in today_executed:
                return (slot_id, s_label)

        return None

    def mark_executed(self, brand: str, slot_id: str, date_str: str):
        """슬롯 실행 완료를 영구 상태 파일에 기록"""
        state = self._load_state()
        if brand not in state:
            state[brand] = {}
        if date_str not in state[brand]:
            state[brand][date_str] = []
        if slot_id not in state[brand][date_str]:
            state[brand][date_str].append(slot_id)
        self._save_state(state)
        logger.info(f"✅ [{brand}] {date_str} '{slot_id}' 슬롯 영구 완료 기록 완료 (오늘 완료: {state[brand][date_str]})")

    def is_slot_executed(self, brand: str, slot_id: str, date_str: str) -> bool:
        state = self._load_state()
        return slot_id in state.get(brand, {}).get(date_str, [])
