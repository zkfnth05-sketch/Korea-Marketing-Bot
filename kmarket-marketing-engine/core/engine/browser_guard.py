# -*- coding: utf-8 -*-
"""
[공용 인프라] Global Browser Guard (전역 브라우저 동시 실행 직렬화 & RAM/GPU 보호기)
===================================================================================
- 역할:
  1. Playwright 브라우저들의 동시 기동을 원천 차단하여 메모리(RAM) 및 GPU 폭증 방지
  2. 모든 브라우저 작업(숏폼/카드뉴스 업로드, 틱톡, 유튜브, 카페 등)의 안전 직렬화
  3. [신규: 우선순위 기반 선점(Preemption) & 스텔스 봇 즉시 양보]:
     - 숏폼/카드뉴스 4대 채널 정시 발행(High Priority)이 들어오면,
     - 단순 시청/좋아요 스텔스 봇(Low Priority)은 1초 만에 즉시 시청을 멈추고 브라우저를 양보(Yield)
     - 발행 봇이 7분 대기 없이 0초 만에 브라우저를 획득하여 즉시 업로드 개시!
  4. 이전 고아 프로세스의 잉여 락 파일(Stale Lock)을 PID 실시간 검증으로 즉시 자동 회수
  5. Chromium 잉여 LOCK 파일(SingletonLock 등) 자동 제거로 'LockFile Access Denied' 에러 원천 방지
"""

import os
import sys
import time
import json
import logging
import threading
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from contextlib import contextmanager, asynccontextmanager

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
ENGINE_ROOT = CURRENT_DIR.parent.parent
DATA_DIR = ENGINE_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

BROWSER_LOCK_FILE = DATA_DIR / "browser_execution.lock"
BROWSER_STATUS_FILE = DATA_DIR / "browser_current_task.json"
BROWSER_YIELD_FLAG_FILE = DATA_DIR / "browser_yield.flag"

logger = logging.getLogger("BrowserGuard")

SAFE_BROWSER_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",                          # GPU 부하 0% 유지
    "--disable-software-rasterizer",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-background-networking",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-breakpad",
    "--disable-component-update",
    "--disable-domain-reliability",
    "--disable-extensions",                   # 확장 프로그램 차단으로 메모리 절약
    "--disable-sync",
    "--use-mock-keychain",                    # 맥/리눅스 인증서 에러 차단
    "--disable-features=Translate,OptimizationHints,MediaRouter,PaintHolding", # 불필요한 기능 제거
]


def _is_pid_alive(pid: int) -> bool:
    """PID 생존 여부 안전 검사 (Windows/Linux 호환)"""
    if pid <= 0:
        return False
    try:
        import psutil
        return psutil.pid_exists(pid)
    except Exception:
        try:
            os.kill(pid, 0)
            return True
        except (OSError, PermissionError, ProcessLookupError):
            return False


def clean_browser_profile_locks(profile_dir: Union[Path, str]) -> None:
    """
    브라우저 프로필 디렉토리 내의 잉여 고아 LOCK 파일 및 임시 캐시 안전 청소
    (Playwright 'Target crashed / IO error: LockFile Access denied' 원천 방지)
    """
    p_dir = Path(profile_dir)
    if not p_dir.exists():
        return

    lock_patterns = [
        "SingletonLock",
        "SingletonCookie",
        "SingletonSocket",
        "LOCK",
        "lockfile",
        "*.lock"
    ]

    cleaned_count = 0
    for pat in lock_patterns:
        try:
            for lock_file in p_dir.glob(pat):
                try:
                    if lock_file.is_file():
                        lock_file.unlink(missing_ok=True)
                        cleaned_count += 1
                except Exception:
                    pass
        except Exception:
            pass

    try:
        sub_dbs = p_dir.glob("**/LOCK")
        for sub_lock in sub_dbs:
            try:
                if sub_lock.is_file():
                    sub_lock.unlink(missing_ok=True)
                    cleaned_count += 1
            except Exception:
                pass
    except Exception:
        pass

    if cleaned_count > 0:
        logger.debug(f"🧹 [BrowserGuard] 잉여 락 파일 {cleaned_count}개 자동 정리 완료: {p_dir.name}")


def get_safe_browser_args(extra_args: Optional[List[str]] = None) -> List[str]:
    """GPU 0% + 초경량 안전 브라우저 인자 반환"""
    args = list(SAFE_BROWSER_ARGS)
    if extra_args:
        for arg in extra_args:
            if arg not in args:
                args.append(arg)
    return args


class GlobalBrowserLock:
    """
    전역 브라우저 동시 실행 직렬화 관리자 (싱글톤)
    - 숏폼/카드뉴스 정시 업로드(High Priority) 우선 보장
    - 스텔스 봇(Low Priority)의 자율 즉시 양보(Cooperative Preemption) 지원
    """
    _instance = None
    _thread_lock = threading.RLock()

    def __new__(cls):
        with cls._thread_lock:
            if cls._instance is None:
                cls._instance = super(GlobalBrowserLock, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._current_task: Optional[str] = None
        self._current_pid: Optional[int] = None
        self._current_is_behavior: bool = False
        self._task_start_time: Optional[float] = None
        self._queue_count = 0
        self._yield_requested = False
        self._initialized = True

    def _is_high_priority_task(self, task_name: str) -> bool:
        """숏폼, 카드뉴스, 업로드, 발행 등 핵심 미디어 배포 작업 판별"""
        t = task_name.lower()
        high_keywords = [
            "업로드", "발행", "publish", "쇼츠", "shorts", "클립", "clip",
            "릴스", "reels", "카드뉴스", "cardnews", "threads", "스레드",
            "omni", "youtube shorts", "tiktok", "naver clip", "mbs"
        ]
        # 단, task_name에 '휴식', '시청', 'behavior'가 들어가면 스텔스 작업임
        if any(w in t for w in ["휴식", "시청", "routine", "behavior", "스텔스"]):
            return False
        return any(k in t for k in high_keywords)

    def is_yield_requested(self) -> bool:
        """스텔스 봇이 루프 중간중간 호출하여 양보 요청 여부 확인"""
        if self._yield_requested:
            return True
        if BROWSER_YIELD_FLAG_FILE.exists():
            return True
        return False

    def request_yield(self, target_publisher_task: str):
        """고우선순위 업로드 작업이 스텔스 봇에게 즉시 양보 요청 발송"""
        self._yield_requested = True
        try:
            BROWSER_YIELD_FLAG_FILE.write_text(f"yield_to={target_publisher_task}\ntimestamp={time.time()}", encoding="utf-8")
        except Exception:
            pass
        logger.info(f"🚨 [BrowserGuard 긴급 선점 요청] '{target_publisher_task}' 긴급 배포 진입 -> 현재 스텔스 봇에 즉각 양보 플래그 발송!")

    def clear_yield(self):
        """양보 플래그 정리"""
        self._yield_requested = False
        try:
            BROWSER_YIELD_FLAG_FILE.unlink(missing_ok=True)
        except Exception:
            pass

    def _write_status(self, task_name: Optional[str], status: str):
        try:
            data = {
                "current_task": task_name,
                "status": status,
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": time.time(),
                "queue_count": self._queue_count
            }
            with open(BROWSER_STATUS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def acquire(self, task_name: str, timeout_sec: int = 1800, is_high_priority: Optional[bool] = None) -> bool:
        """동기 브라우저 락 획득 (우선순위 선점 지원)"""
        start_wait = time.time()
        logged_wait = False
        self._queue_count += 1

        is_high = is_high_priority if is_high_priority is not None else self._is_high_priority_task(task_name)
        yield_requested_sent = False

        try:
            while True:
                # 고우선순위 작업인 경우, 현재 실행 중인 스텔스 작업에 즉각 양보 요청
                if is_high and not yield_requested_sent:
                    if BROWSER_LOCK_FILE.exists():
                        try:
                            content = BROWSER_LOCK_FILE.read_text(encoding="utf-8").strip()
                            if any(w in content for w in ["휴식", "시청", "routine", "behavior", "스텔스"]):
                                self.request_yield(task_name)
                                yield_requested_sent = True
                        except Exception:
                            pass

                acquired = self._thread_lock.acquire(blocking=False)
                if acquired:
                    file_locked = False
                    if BROWSER_LOCK_FILE.exists():
                        try:
                            content = BROWSER_LOCK_FILE.read_text(encoding="utf-8").strip()
                            file_age = time.time() - BROWSER_LOCK_FILE.stat().st_mtime
                            
                            import re
                            m = re.search(r"pid=(\d+)", content)
                            if m:
                                lock_pid = int(m.group(1))
                                if not _is_pid_alive(lock_pid):
                                    logger.warning(f"⚠️ [BrowserGuard] 사망한 프로세스(PID={lock_pid})의 잉여 락 파일 즉시 자동 회수: {content}")
                                    BROWSER_LOCK_FILE.unlink(missing_ok=True)
                                    file_locked = False
                                elif is_high and any(w in content for w in ["휴식", "시청", "routine", "behavior", "스텔스"]) and (time.time() - start_wait) > 5.0:
                                    # 고우선순위 작업이 5초 이상 기다렸는데 스텔스 작업이 아직 안 비켰다면 안전 강제 회수
                                    logger.warning(f"⚡ [BrowserGuard 선점 집행] 스텔스 봇(PID={lock_pid}, '{content}') 5초 양보 지연 -> 브라우저 강제 회수 후 업로드 우선권 인계!")
                                    BROWSER_LOCK_FILE.unlink(missing_ok=True)
                                    file_locked = False
                                elif file_age > 1800:
                                    logger.warning(f"⚠️ [BrowserGuard] 30분 초과 고아 브라우저 락 자동 해제: {BROWSER_LOCK_FILE}")
                                    BROWSER_LOCK_FILE.unlink(missing_ok=True)
                                    file_locked = False
                                else:
                                    file_locked = True
                            else:
                                if file_age > 300:
                                    BROWSER_LOCK_FILE.unlink(missing_ok=True)
                                    file_locked = False
                                else:
                                    file_locked = True
                        except Exception:
                            file_locked = False

                    if not file_locked:
                        try:
                            BROWSER_LOCK_FILE.write_text(f"{task_name} (pid={os.getpid()})", encoding="utf-8")
                        except Exception:
                            pass

                        self._current_task = task_name
                        self._current_pid = os.getpid()
                        self._current_is_behavior = not is_high
                        self._task_start_time = time.time()
                        self._write_status(task_name, "running")
                        self.clear_yield()

                        wait_duration = round(time.time() - start_wait, 1)
                        if wait_duration > 1.0:
                            logger.info(f"🌐 [BrowserGuard] '{task_name}' 작업이 대기 {wait_duration}초 후 브라우저 단독 실행에 진입합니다.")
                        else:
                            logger.info(f"🌐 [BrowserGuard] '{task_name}' 브라우저 단독 실행 진입 (GPU 0% 모드)")
                        return True
                    else:
                        self._thread_lock.release()

                elapsed = round(time.time() - start_wait, 1)
                if elapsed > timeout_sec:
                    logger.error(f"❌ [BrowserGuard] '{task_name}' 브라우저 대기 시간({timeout_sec}초) 초과로 중단")
                    return False

                if not logged_wait or int(elapsed) % 15 == 0:
                    cur = self._current_task or "선행 브라우저 봇"
                    logger.info(f"⏳ [BrowserGuard 순차 대기] 현재 '{cur}' 실행 중. '{task_name}'은(는) 안전 대기 중... ({int(elapsed)}초 경과 / 대기열: {self._queue_count}개)")
                    logged_wait = True

                time.sleep(1)  # 1초 간격으로 신속 재시도
        finally:
            self._queue_count = max(0, self._queue_count - 1)

    def release(self, task_name: Optional[str] = None):
        """브라우저 락 해제"""
        try:
            BROWSER_LOCK_FILE.unlink(missing_ok=True)
        except Exception:
            pass

        finished_task = task_name or self._current_task or "브라우저 작업"
        duration = round(time.time() - self._task_start_time, 1) if self._task_start_time else 0

        self._current_task = None
        self._current_pid = None
        self._current_is_behavior = False
        self._task_start_time = None
        self._write_status(None, "idle")
        self.clear_yield()

        try:
            self._thread_lock.release()
        except RuntimeError:
            pass

        logger.info(f"✅ [BrowserGuard] '{finished_task}' 브라우저 세션 정상 완료 및 자원 반환 (소요: {duration}초)")


browser_guard_manager = GlobalBrowserLock()


def is_yield_requested() -> bool:
    """모듈 레벨 헬퍼 함수: 스텔스 봇이 양보 요청 여부 확인"""
    return browser_guard_manager.is_yield_requested()


@contextmanager
def browser_lock(task_name: str, timeout_sec: int = 1800, is_high_priority: Optional[bool] = None):
    """동기 컨텍스트 매니저"""
    acquired = browser_guard_manager.acquire(task_name=task_name, timeout_sec=timeout_sec, is_high_priority=is_high_priority)
    if not acquired:
        raise TimeoutError(f"브라우저 락 획득 타임아웃({timeout_sec}초 경과): {task_name}")
    try:
        yield
    finally:
        browser_guard_manager.release(task_name=task_name)


@asynccontextmanager
async def async_browser_lock(task_name: str, timeout_sec: int = 1800, is_high_priority: Optional[bool] = None):
    """비동기 컨텍스트 매니저 (asyncio 지원)"""
    loop = asyncio.get_running_loop()
    acquired = await loop.run_in_executor(None, browser_guard_manager.acquire, task_name, timeout_sec, is_high_priority)
    if not acquired:
        raise TimeoutError(f"비동기 브라우저 락 획득 타임아웃({timeout_sec}초 경과): {task_name}")
    try:
        yield
    finally:
        await loop.run_in_executor(None, browser_guard_manager.release, task_name)
