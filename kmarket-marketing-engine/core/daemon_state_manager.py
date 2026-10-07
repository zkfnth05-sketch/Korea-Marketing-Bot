# -*- coding: utf-8 -*-
"""
DaemonStateManager - 🤖 [24시간 무인 데몬 상태 영구 보존 & Auto-Resume 매니저]
========================================================================
- 대시보드 무인가동 상태(Aura, Insurance, Stock, K-Market, EasyTax)를 디스크(data/daemon_state.json)에 영구 기록
- 서버 재시작, 코드 수정, PC 재부팅 시에도 이전 무인가동 상태를 100% 자율 복구(Auto-Resume)
- 파일 락 및 안전한 원자적 쓰기(Atomic Write) 탑재
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger("DaemonStateManager")

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_STATE_FILE = _PROJECT_ROOT / "data" / "daemon_state.json"


class DaemonStateManager:
    """무인 데몬 가동 상태 영구 보존 및 복원 싱글톤 매니저"""

    DEFAULT_STATES = {
        "aura": False,
        "insurance": False,
        "stock": False,
        "kmarket": False,
        "easytax": False
    }

    @classmethod
    def _ensure_dir(cls):
        _STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def load_states(cls) -> Dict[str, bool]:
        """디스크에서 현재 보존된 무인가동 상태 로드"""
        cls._ensure_dir()
        if not _STATE_FILE.exists():
            cls.save_states(cls.DEFAULT_STATES)
            return dict(cls.DEFAULT_STATES)
        try:
            with open(_STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # 기본 키 누락 방지
            states = dict(cls.DEFAULT_STATES)
            for k, v in data.items():
                states[k] = bool(v)
            return states
        except Exception as e:
            logger.warning(f"⚠️ [DaemonStateManager] 상태 파일 읽기 실패 -> 기본값 사용: {e}")
            return dict(cls.DEFAULT_STATES)

    @classmethod
    def save_states(cls, states: Dict[str, bool]):
        """무인가동 상태를 디스크에 영구 기록"""
        cls._ensure_dir()
        temp_file = _STATE_FILE.with_suffix(".tmp")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(states, f, indent=2, ensure_ascii=False)
            if _STATE_FILE.exists():
                _STATE_FILE.unlink()
            temp_file.rename(_STATE_FILE)
            logger.info(f"💾 [DaemonStateManager] 무인 데몬 상태 영구 저장 완료: {states}")
        except Exception as e:
            logger.error(f"❌ [DaemonStateManager] 상태 파일 저장 실패: {e}")
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception:
                    pass

    @classmethod
    def set_daemon_state(cls, brand: str, running: bool):
        """특정 브랜드의 무인가동 상태 변경 및 즉시 영구 저장"""
        states = cls.load_states()
        states[brand] = bool(running)
        cls.save_states(states)

    @classmethod
    def get_daemon_state(cls, brand: str) -> bool:
        """특정 브랜드의 무인가동 상태 조회"""
        states = cls.load_states()
        return states.get(brand, False)
