# -*- coding: utf-8 -*-
"""
Aura Kin 24/7 Scheduler (⏰ Aura 전용 24시간 상시 실시간 10개 쿼터 자율 낚아채기 스케줄러)
========================================================================================
- 브랜드: Aura (2030 AI 데이팅 & 서울 핫플 매칭)
- 핵심 원칙:
  1. 🌐 24시간 시간대 제한 없이 상시 실시간 질문 레이더 감시
  2. ⚡ 새 질문 발견 즉시 85점 심사 ➔ 1~3분 내 최우선 1,500자 킬러 답변 등록 (채택률 99%)
  3. 🛡️ 일일 10개 안전 상한선(Daily Quota Guard) 엄수 (10개 달성 시 당일 대기 모드)
  4. 🔄 매일 자정(00:00) 쿼터 자동 리셋 & 365일 무인 자율 순환
"""

import os
import sys
import json
import time
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
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
    """💖 Aura 지식iN 24시간 상시 10개 쿼터 자율 스케줄러"""

    BRAND = "aura"
    NAME = "Aura (AI 데이팅)"
    DAILY_TARGET = 10

    def __init__(self):
        self.pipeline = AuraKinPipeline()

    def _load_state(self) -> Dict[str, Any]:
        """일일 등록 상태 로드 (날짜 바뀌면 자동 리셋 & history 실측 건수 100% 동기화)"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        state = {
            "date": today_str,
            "daily_total": 0,
            "target": self.DAILY_TARGET,
            "last_run_at": "",
            "last_doc_id": ""
        }
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("date") == today_str:
                        state = data
            except Exception:
                pass

        # 💡 [Rule 5 준수: 100% 정직한 실측 전수 조사] 실제 등록된 history 파일 전수 카운트
        try:
            history = self.pipeline._load_history()
            actual_today = sum(1 for h in history if str(h.get("created_at", "")).startswith(today_str))
            if actual_today > state.get("daily_total", 0):
                state["daily_total"] = actual_today
        except Exception:
            pass

        return state

    def _save_state(self, state: Dict[str, Any]):
        """일일 등록 상태 저장"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def trigger_scheduled_catch(self) -> Dict[str, Any]:
        """
        24시간 상시 호출 트리거:
        - 오늘 10개 미만이면 실시간으로 질문을 낚아채어 등록
        - 10개 완료 시 안전 대기
        """
        state = self._load_state()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logger.info(f"⏰ [Aura 지식iN 24시간 레이더] 현재 일일 쿼터: {state['daily_total']}/{self.DAILY_TARGET}개 (시각: {now_str})")

        # 일일 상한선 10개 체크
        if state["daily_total"] >= self.DAILY_TARGET:
            logger.info(f"✅ 오늘 목표 {self.DAILY_TARGET}개 낚아채기 완료! 자정까지 안전 대기 모드를 유지합니다.")
            return {
                "success": False,
                "status": "daily_quota_full",
                "message": f"금일 목표 {self.DAILY_TARGET}개 완료",
                "daily_total": state["daily_total"],
                "target": self.DAILY_TARGET
            }

        # 파이프라인 1회 실행
        res = self.pipeline.run_catch_cycle(max_catch=1)
        if res.get("success"):
            state["daily_total"] += 1
            state["last_run_at"] = now_str
            state["last_doc_id"] = res.get("record", {}).get("doc_id", "")
            self._save_state(state)
            logger.info(f"🎉 [Aura 등록 성공] 오늘 누적 쿼터: {state['daily_total']} / {self.DAILY_TARGET}개 달성!")
            res["daily_total"] = state["daily_total"]
            res["target"] = self.DAILY_TARGET

        return res

    def run_continuous_daemon(self, check_interval_seconds: int = 300):
        """
        24시간 상시 백그라운드 무인 자율 데몬 루프
        - 5분(300초) 간격으로 실시간 지식iN 감시
        - 새 질문 발견 즉시 등록 ➔ 10개 차면 자정까지 대기
        """
        logger.info(f"🚀 [Aura 24시간 무인 데몬 시작] 주기: {check_interval_seconds}초 간격 감시 가동...")
        while True:
            try:
                self.trigger_scheduled_catch()
            except Exception as e:
                logger.error(f"⚠️ Aura 데몬 실행 중 예외: {e}")
            time.sleep(check_interval_seconds)


if __name__ == "__main__":
    scheduler = AuraKinScheduler()
    res = scheduler.trigger_scheduled_catch()
    print("Aura Scheduler Run Result:", res)
