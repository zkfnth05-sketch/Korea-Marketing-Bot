# -*- coding: utf-8 -*-
"""
[마스터 데몬] KoreaMarketingMasterDaemon - 🤖 [24시간 365일 3대 앱 완전 자율 통합 데몬]
========================================================================================
- 브랜드: 대한민국 3대 앱 (💖 Aura 데이팅, 🛡️ 보험 리밸런스, 📈 StockMaster AI)
- 24시간 완벽 분리 라이프사이클:
  1. 🌙 [새벽 00:00 ~ 03:00] 한국 마케팅봇 GPU 렌더링 전담 타임
     - 3대 앱 × (숏폼 3개 + 카드뉴스 2개) = 총 15개 콘텐츠 순차 제작
     - 1건 제작 완료 시마다 [5분 쿨다운 + VRAM 0MB 방출] 철저 준수 (GPUSafetyGuard)
     - 새벽 3시 이전 15개 전량 완성하여 오늘자 대기 큐(manifest.json)에 안전 보관
  2. ☀️ [아침 07:00 이후] 저쪽 컴퓨터(KTRS) GPU 100% 양보 & 한국 마케팅봇 정시 송출
     - GPU 부하 제로(0%)로 순수 네트워크/모바일 ADB 기반 골든타임 정시 발행
     - ⏰ 08:30 KST: 동영상 숏폼 ① (3대 앱 순차)
     - ⏰ 12:30 KST: 카드뉴스 5장 ① (3대 앱 순차)
     - ⏰ 15:30 KST: 동영상 숏폼 ② (3대 앱 순차)
     - ⏰ 18:30 KST: 카드뉴스 5장 ② (3대 앱 순차)
     - ⏰ 21:00 KST: 동영상 숏폼 ③ (3대 앱 순차)
"""

import os
import sys
import time
import logging
import datetime
import threading
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s"
)
logger = logging.getLogger("KoreaMasterDaemon")

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from midnight_content_factory import MidnightContentFactory
from daytime_sns_dispatcher import DaytimeSNSDispatcher
from core.gpu_safety_guard import GPUSafetyGuard
import json
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class ComponentState(str, Enum):
    """컴포넌트 생명주기 상태머신."""
    NORMAL = "NORMAL"          # 정상 가동
    STOPPED = "STOPPED"        # 중단(사망 감지)
    RESTARTING = "RESTARTING"  # 재기동 진행 중
    QUARANTINED = "QUARANTINED"  # 서킷브레이커 격리


@dataclass
class ComponentSpec:
    """컴포넌트 등록 명세. 신규 컴포넌트는 여기 추가만 하면 된다."""
    name: str
    factory: Callable[[], Any]                 # 의존성 주입 지점
    required: bool = True                      # 필수 여부(격리 시 데몬 중단 판단)
    max_retries: int = 5                       # 최대 재시도 횟수
    backoff_base_sec: float = 2.0              # 지수 백오프 기준
    backoff_cap_sec: float = 300.0             # 백오프 상한
    liveness_probe: Optional[Callable[[Any], bool]] = None  # 생존 확인 훅


@dataclass
class ComponentRuntime:
    """런타임 상태. 상태머신 + 재시도 카운터 + 백오프 관리."""
    spec: ComponentSpec
    state: ComponentState = ComponentState.STOPPED
    instance: Any = None
    thread: Optional[threading.Thread] = None
    retries: int = 0
    next_retry_at: float = 0.0
    last_error: Optional[str] = None
    started_at: float = 0.0

    def backoff_delay(self) -> float:
        delay = self.spec.backoff_base_sec * (2 ** max(0, self.retries - 1))
        return min(delay, self.spec.backoff_cap_sec)


class Supervisor:
    """컴포넌트 등록·감시·재기동·격리를 전담하는 생명주기 관리자.

    - 짧은 틱(기본 15초)으로 liveness 폴링
    - 실패 시 지수 백오프 + 최대 재시도 + 서킷브레이커 격리
    - 종료 훅에서 정리 및 상태 스냅샷 저장
    """

    def __init__(self, tick_sec: float = 15.0, state_path: Optional[str] = None):
        self.tick_sec = tick_sec
        self.state_path = state_path
        self._specs: Dict[str, ComponentSpec] = {}
        self._runtimes: Dict[str, ComponentRuntime] = {}
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._watchdog_thread: Optional[threading.Thread] = None

    # ---- 등록 ----
    def register(self, spec: ComponentSpec) -> None:
        with self._lock:
            if spec.name in self._specs:
                raise ValueError(f"duplicate component: {spec.name}")
            self._specs[spec.name] = spec
            self._runtimes[spec.name] = ComponentRuntime(spec=spec)

    # ---- 상태 조회 ----
    def snapshot(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            return {
                name: {
                    "state": rt.state.value,
                    "retries": rt.retries,
                    "last_error": rt.last_error,
                    "started_at": rt.started_at,
                }
                for name, rt in self._runtimes.items()
            }

    # ---- 기동 ----
    def _spawn(self, rt: ComponentRuntime) -> None:
        """컴포넌트 인스턴스 생성 + 스레드 기동. 예외는 상태머신으로 승격."""
        try:
            if rt.instance is None:
                rt.instance = rt.spec.factory()
            # 엔트리포인트 유연 감지: run() → start_daemon() → run_daemon()
            # (MidnightContentFactory / DaytimeSNSDispatcher 는 start_daemon() 만 구현)
            target = (
                getattr(rt.instance, "run", None)
                or getattr(rt.instance, "start_daemon", None)
                or getattr(rt.instance, "run_daemon", None)
            )
            if not callable(target):
                raise TypeError(
                    f"{rt.spec.name}: run() / start_daemon() / run_daemon() 모두 미구현"
                )

            def _runner():
                try:
                    target()
                except BaseException as exc:  # noqa: BLE001 - 사망 원인 기록 필수
                    logger.exception("[Supervisor] %s 스레드 사망: %s", rt.spec.name, exc)
                    with self._lock:
                        rt.last_error = f"{type(exc).__name__}: {exc}"
                        rt.state = ComponentState.STOPPED

            th = threading.Thread(target=_runner, name=f"cmp-{rt.spec.name}", daemon=True)
            th.start()
            rt.thread = th
            rt.state = ComponentState.NORMAL
            rt.started_at = time.time()
            logger.info("[Supervisor] %s 기동 완료", rt.spec.name)
        except BaseException as exc:  # noqa: BLE001
            logger.exception("[Supervisor] %s 기동 실패: %s", rt.spec.name, exc)
            rt.last_error = f"{type(exc).__name__}: {exc}"
            rt.state = ComponentState.STOPPED

    def _is_alive(self, rt: ComponentRuntime) -> bool:
        if rt.thread is None or not rt.thread.is_alive():
            return False
        if rt.spec.liveness_probe is not None:
            try:
                return bool(rt.spec.liveness_probe(rt.instance))
            except Exception:  # noqa: BLE001
                return False
        return True

    # ---- 감시 루프 ----
    def _watchdog_loop(self) -> None:
        while not self._stop_event.is_set():
            now = time.time()
            with self._lock:
                for name, rt in self._runtimes.items():
                    if rt.state == ComponentState.QUARANTINED:
                        continue
                    if self._is_alive(rt):
                        if rt.state != ComponentState.NORMAL:
                            rt.state = ComponentState.NORMAL
                            rt.retries = 0
                        continue
                    # 사망 감지
                    if rt.state != ComponentState.STOPPED:
                        logger.warning("[Supervisor] %s 사망 감지", name)
                        rt.state = ComponentState.STOPPED
                    if now < rt.next_retry_at:
                        continue
                    if rt.retries >= rt.spec.max_retries:
                        rt.state = ComponentState.QUARANTINED
                        logger.error("[Supervisor] %s 격리(서킷브레이커): %s",
                                     name, rt.last_error)
                        continue
                    rt.retries += 1
                    rt.state = ComponentState.RESTARTING
                    delay = rt.backoff_delay()
                    rt.next_retry_at = now + delay
                    logger.warning("[Supervisor] %s 재기동 시도 %d/%d (%.1fs 후)",
                                   name, rt.retries, rt.spec.max_retries, delay)
                    # 백오프는 다음 틱에서 반영되도록 상태만 갱신
                    if delay <= 0:
                        self._spawn(rt)
            self._stop_event.wait(self.tick_sec)

    def start(self) -> None:
        with self._lock:
            for rt in self._runtimes.values():
                self._spawn(rt)
        self._watchdog_thread = threading.Thread(
            target=self._watchdog_loop, name="supervisor-watchdog", daemon=True
        )
        self._watchdog_thread.start()
        logger.info("[Supervisor] 워치독 기동 (tick=%.1fs)", self.tick_sec)

    # ---- 종료 ----
    def stop(self, timeout: float = 5.0) -> None:
        self._stop_event.set()
        with self._lock:
            for rt in self._runtimes.values():
                shutdown = getattr(rt.instance, "shutdown", None)
                if callable(shutdown):
                    try:
                        shutdown()
                    except Exception:  # noqa: BLE001
                        logger.exception("[Supervisor] %s 종료 훅 실패", rt.spec.name)
            for rt in self._runtimes.values():
                if rt.thread and rt.thread.is_alive():
                    rt.thread.join(timeout=timeout)
        self._persist_state()

    def _persist_state(self) -> None:
        if not self.state_path:
            return
        try:
            os.makedirs(os.path.dirname(self.state_path) or ".", exist_ok=True)
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(self.snapshot(), f, ensure_ascii=False, indent=2)
            logger.info("[Supervisor] 상태 스냅샷 저장: %s", self.state_path)
        except Exception:  # noqa: BLE001
            logger.exception("[Supervisor] 상태 저장 실패")


class SessionHeartbeatRunner:
    """3시간 주기 전 플랫폼 영구 로그인 생명 연장 러너.

    - Supervisor 는 run() / start_daemon() / run_daemon() 중 존재하는 엔트리포인트를
      자동 감지하므로, 본 러너는 run() 하나만 구현하면 된다.
    - asyncio.run() 으로 별도 이벤트 루프를 새로 열기 때문에 Supervisor 의
      워치독 스레드/타 컴포넌트 스레드와 이벤트 루프가 충돌하지 않는다.
    - 모듈 임포트는 run() 내부에서 지연 수행하여, 하트비트 모듈이 아직 없거나
      의존성(playwright 등)이 미설치여도 데몬 전체 기동이 죽지 않도록 격리한다.
    """

    def __init__(self, interval_hours: float = 3.0):
        self.interval_hours = float(interval_hours)

    def run(self) -> None:
        import asyncio
        from core.auto_publishers.omni_session_heartbeat_keeper import (
            start_heartbeat_daemon,
        )

        logger.info(
            "[SessionHeartbeat] 전 플랫폼 세션 생명 연장 데몬 기동 (주기=%.1f시간)",
            self.interval_hours,
        )
        asyncio.run(start_heartbeat_daemon(interval_hours=self.interval_hours))


class ThreadsTextGuardianRunner:
    """3대 브랜드 스레드 텍스트 24시간 자가치유 슬롯 가디언 러너.

    - 09:30 모닝 / 19:30 이브닝 골든 슬롯 15분 간격 자가치유 무인 발행
    - 브라우저 및 작성창 활성화 전 제미나이 0회 호출 (비용 폭탄 0원)
    - asyncio.run()으로 독립 이벤트 루프에서 run_master_daemon() 기동
    """

    def run(self) -> None:
        import asyncio
        from run_threads_text import run_master_daemon

        logger.info("[ThreadsGuardian] 3대 브랜드 스레드 24시간 무인 슬롯 가디언 데몬 기동")
        asyncio.run(run_master_daemon())


class KoreaMarketingMasterDaemon:
    """3대 앱 24시간 365일 무인 마케팅 총괄 관제 데몬.

    run()은 조정자 역할만 수행하며, 컴포넌트 생명주기는 Supervisor가 전담한다.
    신규 컴포넌트(세션 키퍼, 지식iN 레이더 등)는 register_component()로 추가한다.
    """

    def __init__(
        self,
        dry_run: bool = False,
        cooldown_sec: int = 300,
        tick_sec: float = 15.0,
        state_path: Optional[str] = None,
    ):
        self.dry_run = dry_run
        self.cooldown_sec = cooldown_sec
        self.supervisor = Supervisor(tick_sec=tick_sec, state_path=state_path)
        self._register_default_components()

    def _register_default_components(self) -> None:
        """기본 컴포넌트 등록. dry_run은 팩토리까지 일관 전달.

        4대 필수 컴포넌트:
          1. midnight_factory   : 야간 15개 콘텐츠 순차 렌더링 (start_daemon)
          2. daytime_dispatcher : 주간 5대 골든타임 정시 송출 (start_daemon)
          3. session_heartbeat  : 3시간 주기 전 플랫폼 영구 로그인 생명 연장 (run)
          4. threads_guardian   : 3대 브랜드 스레드 09:30/19:30 15분 자가치유 가디언 (run)
        """
        dry_run = self.dry_run
        cooldown_sec = self.cooldown_sec

        self.supervisor.register(ComponentSpec(
            name="midnight_factory",
            factory=lambda: MidnightContentFactory(cooldown_sec=cooldown_sec),
            required=True,
            max_retries=5,
        ))
        self.supervisor.register(ComponentSpec(
            name="daytime_dispatcher",
            factory=lambda: DaytimeSNSDispatcher(dry_run=dry_run),
            required=True,
            max_retries=5,
        ))
        self.supervisor.register(ComponentSpec(
            name="session_heartbeat",
            factory=lambda: SessionHeartbeatRunner(),
            required=False,
            max_retries=5,
            backoff_base_sec=30.0,
            backoff_cap_sec=600.0,
        ))
        self.supervisor.register(ComponentSpec(
            name="threads_guardian",
            factory=lambda: ThreadsTextGuardianRunner(),
            required=False,
            max_retries=5,
            backoff_base_sec=30.0,
            backoff_cap_sec=600.0,
        ))

    def register_component(self, spec: ComponentSpec) -> None:
        """외부에서 세션 키퍼·레이더 등 신규 컴포넌트를 주입."""
        self.supervisor.register(spec)

    def run(self) -> None:
        """단일 진입점. 배너 출력 → Supervisor 기동 → 주기 헬스체크 → 안전 종료.

        - 컴포넌트 기동/감시/재기동은 전적으로 Supervisor 에 위임한다.
        - 메인 스레드는 60초 틱으로 생존 확인 + 1시간 주기 GPU 통계 로깅만 담당한다.
        - KeyboardInterrupt / 예상치 못한 예외 모두 supervisor.stop() 과
          GPUSafetyGuard.cleanup_all() 을 반드시 통과시켜 VRAM 누수를 차단한다.
        """
        logger.info("\n" + "=" * 75)
        logger.info("🤖 [대한민국 3대 앱] 24시간 365일 완전 무인 자율 마케팅 마스터 데몬 점화")
        logger.info("• 대상 브랜드: 💖 Aura AI 데이팅 / 🛡️ 보험 리밸런스 / 📈 StockMaster AI")
        logger.info("• 🌙 새벽 00:00: GPU 안전 5분 쿨다운 순차 제작 (숏폼 3개 + 카드뉴스 2개 × 3앱 = 15개)")
        logger.info("• ☀️ 아침 07:00: 저쪽 컴퓨터(KTRS) GPU 100% 양보 & 주간 5대 골든타임 정시 송출")
        logger.info("• 🧵 스레드: 09:30 모닝 / 19:30 이브닝 · 15분 자가치유 가디언 (제미나이 0회 보장)")
        logger.info(f"• 실행 모드: {'DRY-RUN (시뮬레이션)' if self.dry_run else 'LIVE (실제 렌더링 및 발행)'}")
        logger.info(f"• GPU 쿨다운: {self.cooldown_sec}초 | 감시 틱: {self.supervisor.tick_sec}초")
        logger.info("=" * 75 + "\n")

        exit_code = 0
        try:
            self.supervisor.start()
            logger.info("✅ Supervisor 기동 완료. 24시간 무인 관제 모드로 진입합니다.")

            last_gpu_log = 0.0
            while True:
                now = time.time()
                # 1시간마다 GPU 헬스체크 및 로그 기록
                if now - last_gpu_log >= 3600.0:
                    last_gpu_log = now
                    try:
                        stats = GPUSafetyGuard.get_gpu_stats()
                        temp = f"{stats['temp_c']}℃" if stats.get("available") else "정상"
                        vram = f"{stats['vram_used_mb']}MB" if stats.get("available") else "정상"
                    except Exception as exc:  # noqa: BLE001 - 헬스체크 실패가 데몬을 죽이면 안 됨
                        temp, vram = "조회실패", f"조회실패({type(exc).__name__})"
                    alive = sum(
                        1 for s in self.supervisor.snapshot().values()
                        if s["state"] == ComponentState.NORMAL.value
                    )
                    logger.info(
                        "💓 [Heartbeat] %s | GPU 온도: %s | VRAM: %s | 정상 컴포넌트: %d",
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        temp, vram, alive,
                    )
                time.sleep(60.0)
        except KeyboardInterrupt:
            logger.info("\n🛑 마스터 데몬이 관리자에 의해 안전하게 중단되었습니다.")
        except BaseException as exc:  # noqa: BLE001 - 치명 예외도 정리 후 재전파
            logger.exception("[Daemon] 치명 예외 발생: %s", exc)
            exit_code = 1
        finally:
            try:
                self.supervisor.stop()
            except Exception:  # noqa: BLE001
                logger.exception("[Daemon] Supervisor 종료 중 오류")
            try:
                GPUSafetyGuard.cleanup_all()
            except Exception:  # noqa: BLE001
                logger.exception("[Daemon] GPU 정리 중 오류")
            logger.info("[Daemon] 종료 완료 (exit_code=%d)", exit_code)
        if exit_code:
            raise SystemExit(exit_code)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="대한민국 3대 앱 24시간 무인 마케팅 마스터 데몬")
    parser.add_argument("--dry-run", action="store_true", help="가상 시뮬레이션 모드")
    parser.add_argument("--cooldown", type=int, default=300, help="GPU 쿨다운 시간(초, 기본 300초=5분)")
    args = parser.parse_args()

    daemon = KoreaMarketingMasterDaemon(dry_run=args.dry_run, cooldown_sec=args.cooldown)
    daemon.run()
