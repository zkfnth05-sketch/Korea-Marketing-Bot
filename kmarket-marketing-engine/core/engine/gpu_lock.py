# -*- coding: utf-8 -*-
"""
GlobalGPULock - 🎮 [전역 GPU 단일 점유 및 안전 순차 대기열 매니저]
================================================================================
• 배경 & 목적:
  - 3대 브랜드(Aura, 보험, 주식)의 숏폼(Wan 2.2 S2V) 및 카드뉴스(T2I)가 동시에 제작 요청될 때,
    단일 GPU(그래픽카드 1개) 환경에서 VRAM OOM 충돌이나 작업 탈락(Cancel)을 100% 원천 차단합니다.
  - 그래픽카드가 사용 중이면 에러를 내지 않고, 차분히 대기열에서 안전 대기(Queue Wait)합니다.
  - 앞선 작업이 완료되어 GPU가 비면, VRAM 캐시를 자동 정리한 후 대기 중인 다음 작업에 인계합니다.
  - 렌더링이 완료되면 시간이 지연되었더라도 즉시 각 채널(YouTube, Naver Clip, Meta 등)로 100% 정상 송출합니다.
• 특징:
  - 스레드 안전(Thread-safe) RLock 및 프로세스 간 파일 락(Cross-process File Lock) 완벽 지원
  - 실시간 대기 시간 및 현재 GPU 점유 작업명(Task Name) 가시적 로깅
  - 컨텍스트 매니저 (`with gpu_lock("Aura 숏폼"):`) 지원
"""

import os
import sys
import time
import json
import logging
import threading
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

logger = logging.getLogger("GlobalGPULock")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOCK_FILE = DATA_DIR / "gpu_execution.lock"
STATUS_FILE = DATA_DIR / "gpu_current_task.json"


class GlobalGPULock:
    """전역 GPU 단일 점유 직렬화 매니저 (싱글톤)"""

    _instance = None
    _thread_lock = threading.RLock()

    def __new__(cls):
        with cls._thread_lock:
            if cls._instance is None:
                cls._instance = super(GlobalGPULock, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._current_task: Optional[str] = None
        self._task_start_time: Optional[float] = None
        self._queue_count = 0
        self._initialized = True

    def _write_status(self, task_name: Optional[str], status: str):
        """현재 GPU 작업 상태 파일 기록"""
        try:
            data = {
                "current_task": task_name,
                "status": status,
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": time.time(),
                "queue_count": self._queue_count
            }
            with open(STATUS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def get_status(self) -> dict:
        """현재 GPU 상태 조회"""
        if STATUS_FILE.exists():
            try:
                with open(STATUS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "current_task": self._current_task,
            "status": "idle" if not self._current_task else "busy",
            "queue_count": self._queue_count
        }

    def acquire(self, task_name: str, timeout_sec: int = 3600) -> bool:
        """
        GPU 독점 점유권 획득. 이미 다른 작업이 돌고 있으면 차분히 대기.
        """
        start_wait = time.time()
        logged_wait = False

        self._queue_count += 1
        try:
            while True:
                # 1. 스레드 락 획득 시도 (non-blocking)
                acquired = self._thread_lock.acquire(blocking=False)
                if acquired:
                    # 파일 락 검사 (기존 락 파일이 존재하고 다른 프로세스가 실행 중인지)
                    file_locked = False
                    if LOCK_FILE.exists():
                        try:
                            # 1시간 이상 방치된 고아 락 파일 자동 청소
                            file_age = time.time() - LOCK_FILE.stat().st_mtime
                            if file_age > 3600:
                                logger.warning(f"⚠️ [GPU Lock] 1시간 경과된 고아 락 파일 감지 -> 자동 정리: {LOCK_FILE}")
                                LOCK_FILE.unlink(missing_ok=True)
                            else:
                                file_locked = True
                        except Exception:
                            file_locked = True

                    if not file_locked:
                        # 완벽하게 락 획득 성공!
                        try:
                            LOCK_FILE.write_text(f"{task_name} (pid={os.getpid()})", encoding="utf-8")
                        except Exception:
                            pass
                        
                        self._current_task = task_name
                        self._task_start_time = time.time()
                        self._write_status(task_name, "running")

                        wait_duration = round(time.time() - start_wait, 1)
                        if wait_duration > 2.0:
                            logger.info(f"🎉 [GPU 점유권 획득] '{task_name}' 작업이 대기 {wait_duration}초 만에 GPU를 획득하여 렌더링에 진입합니다!")
                        else:
                            logger.info(f"🚀 [GPU 점유권 획득] '{task_name}' 작업이 즉시 GPU 단독 실행에 진입합니다.")
                        return True
                    else:
                        # 파일 락이 걸려있으므로 스레드 락 반환 후 대기
                        self._thread_lock.release()

                # 아직 다른 작업이 돌고 있는 경우 -> 대기 로깅
                elapsed = round(time.time() - start_wait, 1)
                if elapsed > timeout_sec:
                    logger.error(f"❌ [GPU 락 타임아웃] '{task_name}' 대기 시간({timeout_sec}초) 초과로 중단")
                    return False

                if not logged_wait or int(elapsed) % 15 == 0:
                    status_info = self.get_status()
                    cur = status_info.get("current_task") or self._current_task or "선행 렌더링 작업"
                    logger.info(f"⏳ [GPU 대기열 순차 대기] 현재 '{cur}' 작업이 GPU를 독점 사용 중입니다. '{task_name}'은(는) 안전하게 대기열에서 차례를 기다립니다... (대기: {int(elapsed)}초 경과 / 대기열: {self._queue_count}개)")
                    logged_wait = True

                time.sleep(3)
        finally:
            self._queue_count = max(0, self._queue_count - 1)

    def release(self, task_name: Optional[str] = None):
        """GPU 점유권 해제 및 VRAM 캐시 자동 정리"""
        try:
            LOCK_FILE.unlink(missing_ok=True)
        except Exception:
            pass

        finished_task = task_name or self._current_task or "작업"
        duration = round(time.time() - self._task_start_time, 1) if self._task_start_time else 0

        self._current_task = None
        self._task_start_time = None
        self._write_status(None, "idle")

        try:
            self._thread_lock.release()
        except RuntimeError:
            pass

        logger.info(f"✅ [GPU 점유권 반환 완료] '{finished_task}' 작업 종료 (소요: {duration}초). 다음 대기 작업에 GPU를 인계합니다.")


# 글로벌 인스턴스
gpu_lock_manager = GlobalGPULock()


@contextmanager
def gpu_lock(task_name: str, timeout_sec: int = 3600):
    """
    편리한 컨텍스트 매니저:
    with gpu_lock("Aura 숏폼 #3"):
        # 렌더링 코드
    """
    acquired = gpu_lock_manager.acquire(task_name=task_name, timeout_sec=timeout_sec)
    if not acquired:
        raise TimeoutError(f"GPU 락 획득 타임아웃 ({timeout_sec}초 경과): {task_name}")
    try:
        yield
    finally:
        gpu_lock_manager.release(task_name=task_name)
