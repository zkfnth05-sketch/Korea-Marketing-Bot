"""
aura_nate_pann_publisher.py
- NatePann 무인 발행 파이프라인 (책임 분리 / preflight / 상태머신 / 안전장치)
- 감사 지적 반영: 단일 클래스 결합 해소, 침묵 실패 제거, 무한 재시도 차단
"""

from __future__ import annotations

import json
import logging
import os
import signal
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Optional, Protocol

# ---------------------------------------------------------------------------
# 0. 로깅
# ---------------------------------------------------------------------------
logger = logging.getLogger("aura.nate")
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(_h)
logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# 1. 결과 타입 (침묵 실패 제거)
# ---------------------------------------------------------------------------
class Outcome(str, Enum):
    OK = "ok"                    # 성공
    RETRYABLE = "retryable"      # 재시도 가능 (일시 오류)
    FATAL = "fatal"              # 치명 (정책/인증/구조 변경)
    SKIPPED = "skipped"          # 멱등성에 의해 스킵


@dataclass
class StepResult:
    outcome: Outcome
    detail: str = ""
    payload: dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.outcome is Outcome.OK


# ---------------------------------------------------------------------------
# 2. 설정 외부화 (하드코딩 제거)
# ---------------------------------------------------------------------------
@dataclass
class PublisherConfig:
    board_url: str = "https://pann.nate.com/talk/200257"  # 기본값, 반드시 preflight로 검증
    category_id: str = "200257"
    search_keyword: str = ""            # Zero URL 유도용 고정 검색어 (정책 검토 필수)
    session_path: str = "nate_session.json"
    history_path: str = "publish_history.jsonl"
    proof_dir: str = "proofs"
    step_timeout_sec: int = 45          # 단계별 타임아웃 상한
    max_retries: int = 2                # 재시도 상한 (무한 실패 차단)
    retry_backoff_sec: float = 3.0
    headless: bool = True

    @classmethod
    def load(cls, path: str = "publisher_config.json") -> "PublisherConfig":
        p = Path(path)
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        return cls()


# ---------------------------------------------------------------------------
# 3. 책임별 인터페이스 (경계 정의)
# ---------------------------------------------------------------------------
class ContentComposer(Protocol):
    def compose(self, topic: str) -> StepResult: ...


class SessionProvider(Protocol):
    def validate(self) -> StepResult: ...
    def cookies(self) -> list: ...


class BoardNavigator(Protocol):
    def open_category(self, category_id: str) -> StepResult: ...
    def open_editor(self) -> StepResult: ...


class PostPublisher(Protocol):
    def submit(self, title: str, body: str) -> StepResult: ...
    def confirm_url(self) -> StepResult: ...


class ProofRecorder(Protocol):
    def capture(self, run_id: str, url: str) -> StepResult: ...
    def append_history(self, record: dict) -> StepResult: ...


# ---------------------------------------------------------------------------
# 4. 상태 머신 (멱등성 + 체크포인트)
# ---------------------------------------------------------------------------
class Stage(str, Enum):
    INIT = "init"
    PREFLIGHT = "preflight"
    COMPOSE = "compose"
    NAVIGATE = "navigate"
    SUBMIT = "submit"
    CONFIRM = "confirm"
    PROOF = "proof"
    DONE = "done"
    FAILED = "failed"


@dataclass
class RunState:
    run_id: str
    idempotency_key: str
    stage: Stage = Stage.INIT
    url: str = ""
    error: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["stage"] = self.stage.value
        return d


class StateStore:
    """체크포인트 저장소. 재시작 시 중복 발행 방지."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self, idem_key: str) -> Optional[RunState]:
        if not self.path.exists():
            return None
        for line in self.path.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("idempotency_key") == idem_key:
                return RunState(
                    run_id=rec["run_id"],
                    idempotency_key=rec["idempotency_key"],
                    stage=Stage(rec["stage"]),
                    url=rec.get("url", ""),
                    error=rec.get("error", ""),
                )
        return None

    def save(self, state: RunState) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(state.to_dict(), ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# 5. 안전장치: 타임아웃 / 프로세스 회수
# ---------------------------------------------------------------------------
class StepTimeout(Exception):
    pass


def run_with_timeout(fn, timeout_sec: int, label: str):
    """단계별 타임아웃 상한. SIGALRM 기반 (POSIX)."""
    def _handler(signum, frame):
        raise StepTimeout(f"{label} timeout after {timeout_sec}s")

    old = signal.signal(signal.SIGALRM, _handler)
    signal.alarm(timeout_sec)
    try:
        return fn()
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)


class BrowserGuard:
    """브라우저 프로세스 그룹 회수 (좀비 방지)."""

    def __init__(self):
        self._pids: list[int] = []

    def register(self, pid: int) -> None:
        self._pids.append(pid)

    def reap(self) -> None:
        for pid in self._pids:
            try:
                os.killpg(os.getpgid(pid), signal.SIGTERM)
                logger.info("browser pg %s terminated", pid)
            except (ProcessLookupError, PermissionError):
                pass
        self._pids.clear()


# ---------------------------------------------------------------------------
# 6. 오케스트레이터 (책임 위임만 수행)
# ---------------------------------------------------------------------------
class PublishOrchestrator:
    def __init__(
        self,
        cfg: PublisherConfig,
        composer: ContentComposer,
        session: SessionProvider,
        navigator: BoardNavigator,
        publisher: PostPublisher,
        recorder: ProofRecorder,
        store: StateStore,
        guard: BrowserGuard,
    ):
        self.cfg = cfg
        self.composer = composer
        self.session = session
        self.navigator = navigator
        self.publisher = publisher
        self.recorder = recorder
        self.store = store
        self.guard = guard

    # --- preflight: 실패를 발행 전으로 앞당김 ---
    def preflight(self) -> StepResult:
        s = self.session.validate()
        if not s.ok:
            return StepResult(Outcome.FATAL, f"session invalid: {s.detail}")
        n = self.navigator.open_category(self.cfg.category_id)
        if not n.ok:
            return StepResult(Outcome.FATAL, f"category unreachable: {n.detail}")
        return StepResult(Outcome.OK, "preflight passed")

    def _retry(self, fn, label: str) -> StepResult:
        last = StepResult(Outcome.FATAL, "no attempt")
        for attempt in range(1, self.cfg.max_retries + 1):
            try:
                res = run_with_timeout(fn, self.cfg.step_timeout_sec, label)
            except StepTimeout as e:
                last = StepResult(Outcome.RETRYABLE, str(e))
            except Exception as e:  # noqa: BLE001
                last = StepResult(Outcome.FATAL, f"{label} exception: {e}")
            else:
                if res.outcome is not Outcome.RETRYABLE:
                    return res
                last = res
            logger.warning("%s attempt %d/%d failed: %s", label, attempt, self.cfg.max_retries, last.detail)
            if attempt < self.cfg.max_retries:
                time.sleep(self.cfg.retry_backoff_sec * attempt)
        return last

    def run(self, topic: str) -> RunState:
        idem = f"{self.cfg.category_id}:{topic.strip()}"
        prev = self.store.load(idem)
        if prev and prev.stage is Stage.DONE:
            logger.info("idempotent skip: %s", idem)
            return prev

        state = prev or RunState(run_id=str(uuid.uuid4()), idempotency_key=idem)

        def _fail(res: StepResult) -> RunState:
            state.stage = Stage.FAILED
            state.error = res.detail
            self.store.save(state)
            logger.error("run %s failed at %s: %s", state.run_id, state.stage, res.detail)
            return state

        # PREFLIGHT
        if state.stage in (Stage.INIT, Stage.PREFLIGHT):
            res = self.preflight()
            if not res.ok:
                return _fail(res)
            state.stage = Stage.PREFLIGHT
            self.store.save(state)

        # COMPOSE
        if state.stage is Stage.PREFLIGHT:
            res = self._retry(lambda: self.composer.compose(topic), "compose")
            if not res.ok:
                return _fail(res)
            state.stage = Stage.COMPOSE
            self.store.save(state)
            composed = res.payload
        else:
            composed = {"title": topic, "body": topic}

        # NAVIGATE
        if state.stage is Stage.COMPOSE:
            res = self._retry(self.navigator.open_editor, "navigate")
            if not res.ok:
                return _fail(res)
            state.stage = Stage.NAVIGATE
            self.store.save(state)

        # SUBMIT
        if state.stage is Stage.NAVIGATE:
            res = self._retry(
                lambda: self.publisher.submit(composed.get("title", topic), composed.get("body", topic)),
                "submit",
            )
            if not res.ok:
                return _fail(res)
            state.stage = Stage.SUBMIT
            self.store.save(state)

        # CONFIRM (URL 확정 실패는 미확정으로 별도 기록)
        if state.stage is Stage.SUBMIT:
            res = self._retry(self.publisher.confirm_url, "confirm")
            if res.ok:
                state.url = res.payload.get("url", "")
                state.stage = Stage.CONFIRM
            else:
                state.error = f"url unconfirmed: {res.detail}"
                state.stage = Stage.CONFIRM  # 미확정이지만 발행은 진행
            self.store.save(state)

        # PROOF
        if state.stage is Stage.CONFIRM:
            res = self._retry(lambda: self.recorder.capture(state.run_id, state.url), "proof")
            if not res.ok:
                logger.warning("proof capture failed (non-fatal): %s", res.detail)
            self.recorder.append_history(state.to_dict())
            state.stage = Stage.DONE
            self.store.save(state)

        self.guard.reap()
        return state


# ---------------------------------------------------------------------------
# 7. 참조 구현 (실제 셀렉터/세션 로직은 어댑터에서 주입)
# ---------------------------------------------------------------------------
class FileSessionProvider:
    def __init__(self, cfg: PublisherConfig):
        self.cfg = cfg

    def validate(self) -> StepResult:
        p = Path(self.cfg.session_path)
        if not p.exists():
            return StepResult(Outcome.FATAL, f"session file missing: {p}")
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            return StepResult(Outcome.FATAL, f"session json invalid: {e}")
        if not data.get("cookies"):
            return StepResult(Outcome.FATAL, "session has no cookies")
        return StepResult(Outcome.OK, "session ok")

    def cookies(self) -> list:
        return json.loads(Path(self.cfg.session_path).read_text(encoding="utf-8")).get("cookies", [])


class StubComposer:
    def compose(self, topic: str) -> StepResult:
        return StepResult(Outcome.OK, "composed", {"title": topic, "body": f"{topic}\n\n(본문)"})


class StubNavigator:
    def __init__(self, cfg: PublisherConfig):
        self.cfg = cfg

    def open_category(self, category_id: str) -> StepResult:
        if not category_id.isdigit():
            return StepResult(Outcome.FATAL, f"invalid category id: {category_id}")
        return StepResult(Outcome.OK, "category ok")

    def open_editor(self) -> StepResult:
        return StepResult(Outcome.OK, "editor ok")


class StubPublisher:
    def submit(self, title: str, body: str) -> StepResult:
        return StepResult(Outcome.OK, "submitted", {"title": title})

    def confirm_url(self) -> StepResult:
        return StepResult(Outcome.OK, "confirmed", {"url": "https://pann.nate.com/talk/000000"})


class FileProofRecorder:
    def __init__(self, cfg: PublisherConfig):
        self.cfg = cfg
        Path(cfg.proof_dir).mkdir(parents=True, exist_ok=True)

    def capture(self, run_id: str, url: str) -> StepResult:
        out = Path(self.cfg.proof_dir) / f"{run_id}.json"
        out.write_text(json.dumps({"run_id": run_id, "url": url}, ensure_ascii=False), encoding="utf-8")
        return StepResult(Outcome.OK, str(out))

    def append_history(self, record: dict) -> StepResult:
        with Path(self.cfg.history_path).open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return StepResult(Outcome.OK, "history appended")


# ---------------------------------------------------------------------------
# 8. 엔트리포인트
# ---------------------------------------------------------------------------
def build_default_orchestrator(cfg: Optional[PublisherConfig] = None) -> PublishOrchestrator:
    cfg = cfg or PublisherConfig.load()
    return PublishOrchestrator(
        cfg=cfg,
        composer=StubComposer(),
        session=FileSessionProvider(cfg),
        navigator=StubNavigator(cfg),
        publisher=StubPublisher(),
        recorder=FileProofRecorder(cfg),
        store=StateStore("run_state.jsonl"),
        guard=BrowserGuard(),
    )


if __name__ == "__main__":
    orch = build_default_orchestrator()
    final = orch.run("테스트 토픽")
    logger.info("final state: %s", final.to_dict())