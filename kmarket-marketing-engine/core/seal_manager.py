# -*- coding: utf-8 -*-
"""
[독립 레고 블록] SealManager - 🔒 [마케팅 채널 안전핀 봉인 관리자]
=============================================================================
- 역할: 대표님 지시에 따른 특정 채널(예: 보험 블로그) 발행 원천 봉인 및 대시보드 해제 제어
- 영구 저장소: data/seal_config.json (원자적 flush 및 배타적 스레드 락)
- 동작 모드:
  • 봉인(Sealed=True): 스케줄러, 크론, 데몬, 수동 실행 등 모든 발행 경로 0초 만에 안전 차단
  • 해제(Sealed=False): 정상 자율/수동 발행 허용
"""

import os
import sys
import json
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("SealManager")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SEAL_CONFIG_FILE = DATA_DIR / "seal_config.json"


def _get_kst_now_str() -> str:
    try:
        from config import get_now_kst_str
        return get_now_kst_str()
    except Exception:
        import datetime
        from datetime import timezone, timedelta
        kst = timezone(timedelta(hours=9))
        return datetime.datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S")


class SealManager:
    """마케팅 채널 안전핀 봉인 및 대시보드 토글 총괄 관리자 (Thread-Safe 싱글톤 패턴)"""

    _lock = threading.Lock()
    _instance: Optional["SealManager"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SealManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # 기본 초기화 1회 수행
        if not hasattr(self, "_initialized"):
            with self._lock:
                if not hasattr(self, "_initialized"):
                    self.config_file = SEAL_CONFIG_FILE
                    self._ensure_config_exists()
                    self._initialized = True

    def _ensure_config_exists(self):
        """설정 파일이 없으면 기본 봉인 상태(보험 블로그 봉인 체결)로 생성"""
        if not self.config_file.exists():
            default_state = {
                "insurance_blog_sealed": True,
                "insurance_kin_sealed": True,
                "sealed_at": _get_kst_now_str(),
                "sealed_by": "대표님 지시",
                "reason": "대표님 명령에 따른 보험 블로그 발행 잠정 안전 봉인",
                "history": [
                    {
                        "action": "SEAL",
                        "target": "insurance_blog",
                        "sealed": True,
                        "actor": "대표님 지시",
                        "reason": "최초 초기화 안전 봉인 체결",
                        "timestamp": _get_kst_now_str()
                    }
                ]
            }
            self._save_state(default_state)
            logger.info("🔒 [SealManager] 기본 봉인 설정 파일 생성 완료: 보험 블로그 봉인(Sealed=True) 체결됨")

    def _load_state(self) -> Dict[str, Any]:
        """상태 파일 로드"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except Exception as e:
                logger.warning(f"⚠️ [SealManager] 상태 파일 로드 경고: {e}")
        return {
            "insurance_blog_sealed": True,
            "sealed_at": _get_kst_now_str(),
            "sealed_by": "기본값(안전우선)",
            "reason": "로드 실패 시 안전 우선 봉인",
            "history": []
        }

    def _save_state(self, state: Dict[str, Any]) -> bool:
        """원자적 상태 파일 기록 (tmp -> fsync -> os.replace)"""
        try:
            tmp_file = self.config_file.with_suffix(".json.tmp")
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_file, self.config_file)
            return True
        except Exception as e:
            logger.error(f"❌ [SealManager] 상태 파일 원자적 저장 실패: {e}")
            return False

    def is_sealed(self, target: str = "insurance_blog") -> bool:
        """
        특정 채널이 현재 안전 봉인(차단) 상태인지 확인.
        기본값: insurance_blog -> True (봉인됨)
        """
        clean_target = target.replace("_sealed", "").strip()
        key = f"{clean_target}_sealed" if not target.endswith("_sealed") else target
        
        with self._lock:
            state = self._load_state()
            # 타깃 키가 없으면 안전 우선(True)
            return bool(state.get(key, True))

    def set_sealed(
        self,
        target: str = "insurance_blog",
        sealed: bool = True,
        reason: str = "",
        actor: str = "대시보드"
    ) -> Dict[str, Any]:
        """봉인 상태 명시적 설정 (True: 봉인 체결, False: 봉인 해제)"""
        clean_target = target.replace("_sealed", "").strip()
        key = f"{clean_target}_sealed" if not target.endswith("_sealed") else target

        now_str = _get_kst_now_str()
        action_name = "SEAL" if sealed else "UNSEAL"
        default_reason = (
            "대표님 명령에 따른 발행 안전 봉인" if sealed
            else "대표님/대시보드 요청에 따른 발행 봉인 해제 (정상 가동)"
        )
        final_reason = reason or default_reason

        with self._lock:
            state = self._load_state()
            state[key] = bool(sealed)
            state["sealed_at"] = now_str
            state["sealed_by"] = actor
            state["reason"] = final_reason

            history = state.get("history", [])
            history.append({
                "action": action_name,
                "target": clean_target,
                "sealed": bool(sealed),
                "actor": actor,
                "reason": final_reason,
                "timestamp": now_str
            })
            # 히스토리는 최근 50건만 유지
            state["history"] = history[-50:]

            self._save_state(state)

        status_text = "🔒 봉인 체결(발행 차단)" if sealed else "🔓 봉인 해제(정상 가동)"
        logger.info(f"🛡️ [SealManager] {clean_target} 상태 변경: {status_text} | 처리자: {actor}")

        return {
            "success": True,
            "target": clean_target,
            "sealed": bool(sealed),
            "status_text": status_text,
            "updated_at": now_str,
            "actor": actor,
            "reason": final_reason
        }

    def toggle_sealed(
        self,
        target: str = "insurance_blog",
        actor: str = "대시보드"
    ) -> Dict[str, Any]:
        """봉인 상태 토글 (봉인 중이면 해제, 해제 중이면 봉인)"""
        current = self.is_sealed(target)
        new_state = not current
        reason = "대시보드 원클릭 토글 요청"
        return self.set_sealed(target=target, sealed=new_state, reason=reason, actor=actor)

    def get_status(self) -> Dict[str, Any]:
        """현재 모든 봉인 상태 및 최근 히스토리 조회"""
        with self._lock:
            state = self._load_state()
            return {
                "insurance_blog_sealed": bool(state.get("insurance_blog_sealed", True)),
                "insurance_kin_sealed": bool(state.get("insurance_kin_sealed", True)),
                "sealed_at": state.get("sealed_at", ""),
                "sealed_by": state.get("sealed_by", ""),
                "reason": state.get("reason", ""),
                "history": state.get("history", [])[-10:]
            }


# 전역 단일 인스턴스 (편의 객체)
seal_manager = SealManager()
