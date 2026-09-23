# -*- coding: utf-8 -*-
"""
Insurance Kin 24/7 Scheduler (⏰ InsureBalance 전용 24시간 상시 실시간 10개 쿼터 자율 낚아채기 스케줄러)
====================================================================================================
- 브랜드: InsureBalance (2030 AI 보험비교 & 리모델링)
- 핵심 원칙:
  1. 🌐 24시간 시간대 제한 없이 상시 실시간 보험 질문 레이더 감시
  2. ⚡ 새 질문 발견 즉시 85점 심사 ➔ 1~3분 내 최우선 1,500자 공인 컨설턴트 킬러 답변 등록 (채택률 99%)
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
logger = logging.getLogger("InsuranceKinScheduler")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "data"
STATE_FILE = DATA_DIR / "insurance_kin_daily_state.json"

try:
    from brands.insurance.insurance_kin_pipeline import InsuranceKinPipeline
except ImportError:
    from insurance_kin_pipeline import InsuranceKinPipeline


class InsuranceKinScheduler:
    """🛡️ InsureBalance 지식iN 24시간 상시 10개 쿼터 자율 스케줄러"""

    BRAND = "insurance"
    NAME = "InsureBalance (보험비교)"
    DAILY_TARGET = 10

    def __init__(self):
        self.pipeline = InsuranceKinPipeline()

    def _load_state(self) -> Dict[str, Any]:
        """일일 등록 상태 로드 (날짜 바뀌면 자동 리셋)"""
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
            "target": self.DAILY_TARGET,
            "last_run_at": "",
            "last_doc_id": ""
        }

    def _save_state(self, state: Dict[str, Any]):
        """일일 등록 상태 저장"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def trigger_scheduled_catch(self) -> Dict[str, Any]:
        """
        24시간 상시 호출 트리거:
        - 오늘 10개 미만이면 실시간으로 보험 질문을 낚아채어 등록
        - 10개 완료 시 안전 대기
        """
        state = self._load_state()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logger.info(f"⏰ [Insurance 지식iN 24시간 레이더] 현재 일일 쿼터: {state['daily_total']}/{self.DAILY_TARGET}개 (시각: {now_str})")

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
            logger.info(f"🎉 [Insurance 등록 성공] 오늘 누적 쿼터: {state['daily_total']} / {self.DAILY_TARGET}개 달성!")
            res["daily_total"] = state["daily_total"]
            res["target"] = self.DAILY_TARGET

        return res

    def run_continuous_daemon(self, check_interval_seconds: int = 300):
        """
        24시간 상시 백그라운드 무인 자율 데몬 루프
        - 5분(300초) 간격으로 실시간 지식iN 감시
        - 새 질문 발견 즉시 등록 ➔ 10개 차면 자정까지 대기
        """
        logger.info(f"🚀 [Insurance 24시간 무인 데몬 시작] 주기: {check_interval_seconds}초 간격 감시 가동...")
        while True:
            try:
                self.trigger_scheduled_catch()
            except Exception as e:
                logger.error(f"⚠️ Insurance 데몬 실행 중 예외: {e}")
            time.sleep(check_interval_seconds)


if __name__ == "__main__":
    scheduler = InsuranceKinScheduler()
    res = scheduler.trigger_scheduled_catch()
    print("Insurance Scheduler Run Result:", res)
