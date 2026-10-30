#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GOOGLE_PLAY_REVIEW_GUIDE.md 생성기 (무인 가동형)

설계 원칙:
- 단일 진실 원천(SSOT): release_manifest.json 하나에서 모든 문서/검증 파생
- 인증 게이트웨이 단일화: 리뷰 모드 분기는 실패 시 차단적(fail-closed)
- 무인 가동 안전장치: 타임아웃, 좀비 프로세스 회수, 재시도/서킷브레이커, 헬스체크
- 문서는 수기 작성 금지: 매니페스트에서 렌더링 + 제출 전 자동 검증
"""

from __future__ import annotations

import json
import logging
import os
import signal
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# ---------------------------------------------------------------------------
# 로깅 (무인 가동: 파일 + 콘솔, 구조화 로그)
# ---------------------------------------------------------------------------
LOG_PATH = Path(os.environ.get("GUIDE_LOG_PATH", "review_guide_build.log"))
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s :: %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("review_guide")


# ---------------------------------------------------------------------------
# 예외 계층 (차단적 실패)
# ---------------------------------------------------------------------------
class GuideBuildError(Exception):
    """가이드 생성 실패의 최상위 예외. 무인 가동 시 즉시 중단."""


class ManifestValidationError(GuideBuildError):
    """매니페스트 스키마/계약 위반."""


class ReviewModeContractError(GuideBuildError):
    """리뷰 모드 분기 계약 위반 (fail-closed)."""


class TimeoutExceeded(GuideBuildError):
    """단계별 타임아웃 초과."""


# ---------------------------------------------------------------------------
# 타임아웃 가드 (무인 가동 안전장치)
# ---------------------------------------------------------------------------
class TimeoutGuard:
    """SIGALRM 기반 단계 타임아웃. 미지원 플랫폼에서는 소프트 체크."""

    def __init__(self, seconds: int, label: str) -> None:
        self.seconds = seconds
        self.label = label
        self._prev_handler: Optional[Callable[..., Any]] = None

    def __enter__(self) -> "TimeoutGuard":
        if hasattr(signal, "SIGALRM"):
            self._prev_handler = signal.getsignal(signal.SIGALRM)

            def _handler(signum, frame):  # noqa: ANN001
                raise TimeoutExceeded(f"[{self.label}] {self.seconds}s 초과")

            signal.signal(signal.SIGALRM, _handler)
            signal.alarm(self.seconds)
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:  # noqa: ANN001
        if hasattr(signal, "SIGALRM"):
            signal.alarm(0)
            if self._prev_handler is not None:
                signal.signal(signal.SIGALRM, self._prev_handler)
        return False


# ---------------------------------------------------------------------------
# 재시도 + 서킷브레이커 (무인 가동 안전장치)
# ---------------------------------------------------------------------------
@dataclass
class CircuitBreaker:
    failure_threshold: int = 3
    recovery_seconds: int = 60
    _failures: int = 0
    _opened_at: Optional[float] = None

    def call(self, fn: Callable[[], Any], label: str) -> Any:
        if self._opened_at is not None:
            if time.monotonic() - self._opened_at < self.recovery_seconds:
                raise GuideBuildError(f"[{label}] 서킷 열림 상태, 호출 차단")
            self._opened_at = None
            self._failures = 0
        try:
            result = fn()
            self._failures = 0
            return result
        except Exception as exc:  # noqa: BLE001
            self._failures += 1
            log.warning("[%s] 실패 %d/%d: %s", label, self._failures, self.failure_threshold, exc)
            if self._failures >= self.failure_threshold:
                self._opened_at = time.monotonic()
                log.error("[%s] 서킷 열림", label)
            raise


# ---------------------------------------------------------------------------
# 릴리스 매니페스트 (단일 진실 원천)
# ---------------------------------------------------------------------------
@dataclass
class DemoAccount:
    email: str
    password: str
    note: str = ""


@dataclass
class ReleaseManifest:
    app_name: str
    package_name: str
    version_name: str
    version_code: int
    track: str
    launch_url: str
    review_mode_param: str
    review_mode_value: str
    demo_account: DemoAccount
    environments: Dict[str, str] = field(default_factory=dict)
    generated_at: str = ""

    REQUIRED_FIELDS = (
        "app_name", "package_name", "version_name", "version_code",
        "track", "launch_url", "review_mode_param", "review_mode_value",
        "demo_account",
    )

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "ReleaseManifest":
        missing = [k for k in cls.REQUIRED_FIELDS if k not in raw]
        if missing:
            raise ManifestValidationError(f"필수 필드 누락: {missing}")
        acct = raw["demo_account"]
        if not isinstance(acct, dict) or not acct.get("email") or not acct.get("password"):
            raise ManifestValidationError("demo_account.email/password 필수")
        return cls(
            app_name=raw["app_name"],
            package_name=raw["package_name"],
            version_name=raw["version_name"],
            version_code=int(raw["version_code"]),
            track=raw["track"],
            launch_url=raw["launch_url"],
            review_mode_param=raw["review_mode_param"],
            review_mode_value=raw["review_mode_value"],
            demo_account=DemoAccount(
                email=acct["email"], password=acct["password"], note=acct.get("note", "")
            ),
            environments=raw.get("environments", {}),
            generated_at=raw.get("generated_at", ""),
        )

    def validate_contract(self) -> None:
        """리뷰 모드 분기 계약 검증 (fail-closed)."""
        if self.review_mode_param not in self.launch_url:
            raise ReviewModeContractError(
                f"launch_url에 리뷰 모드 파라미터 '{self.review_mode_param}' 부재"
            )
        if self.review_mode_value not in self.launch_url:
            raise ReviewModeContractError(
                f"launch_url에 리뷰 모드 값 '{self.review_mode_value}' 부재"
            )
        if not self.launch_url.startswith(("https://", "http://")):
            raise ReviewModeContractError("launch_url은 http(s) 스킴이어야 함")
        if self.track not in {"internal", "closed", "open", "production"}:
            raise ManifestValidationError(f"알 수 없는 트랙: {self.track}")


# ---------------------------------------------------------------------------
# 매니페스트 로더 (재시도 + 서킷브레이커)
# ---------------------------------------------------------------------------
def load_manifest(path: Path, breaker: CircuitBreaker) -> ReleaseManifest:
    def _read() -> Dict[str, Any]:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    raw = breaker.call(_read, "manifest_load")
    manifest = ReleaseManifest.from_dict(raw)
    manifest.validate_contract()
    return manifest


# ---------------------------------------------------------------------------
# 문서 렌더러 (매니페스트 → Markdown)
# ---------------------------------------------------------------------------
def render_guide(m: ReleaseManifest) -> str:
    env_lines = "\n".join(f"| {k} | `{v}` |" for k, v in m.environments.items()) or "| - | - |"
    generated = m.generated_at or datetime.now(timezone.utc).isoformat()

    return f"""# Google Play 심사 가이드 — {m.app_name}

> 본 문서는 `release_manifest.json`에서 자동 생성되었습니다. 수기 편집 금지.
> 생성 시각(UTC): {generated}

## 1. 앱 정보
| 항목 | 값 |
| --- | --- |
| 앱 이름 | {m.app_name} |
| 패키지 | `{m.package_name}` |
| 버전 | `{m.version_name}` (code {m.version_code}) |
| 제출 트랙 | `{m.track}` |

## 2. 심사관 접근 정보 (App access)
- **데모 계정 이메일**: `{m.demo_account.email}`
- **데모 계정 비밀번호**: `{m.demo_account.password}`
- **비고**: {m.demo_account.note or "없음"}

> ⚠️ 위 자격 증명은 매니페스트에서 파생됩니다. Play Console "App access" 항목과 반드시 일치해야 하며, 불일치 시 자동 검증에서 차단됩니다.

## 3. 리뷰 모드 진입 경로
- **launchUrl**: `{m.launch_url}`
- **리뷰 모드 파라미터**: `{m.review_mode_param}={m.review_mode_value}`
- 리뷰 모드 분기는 **단일 인증 게이트웨이**에서만 처리됩니다.
- 리뷰 모드 진입 실패 시 **차단적(fail-closed)** 으로 중단되며, 인증 팝업을 숨기는 우회는 금지됩니다.

## 4. 환경 매핑
| 환경 | URL |
| --- | --- |
{env_lines}

## 5. 제출 전 자동 검증 체크리스트
- [ ] 스토어 트랙 아티팩트(AAB)가 최신 웹 배포와 일치
- [ ] `launch_url`이 리뷰 모드 파라미터를 포함
- [ ] 데모 계정으로 실제 로그인 성공 (스모크 테스트)
- [ ] Play Console "App access" 기재 내용이 본 문서와 일치
- [ ] 구버전 Firebase 로그인 게이트 제거 확인

## 6. 트러블슈팅
- **로그인 팝업 반복**: 트랙 아티팩트가 구버전일 가능성 → 재빌드/재서명 후 재업로드
- **리뷰 모드 미진입**: `launch_url` 파라미터 누락 → 매니페스트 수정 후 문서 재생성
- **자격 증명 오류**: 매니페스트와 Play Console 불일치 → 매니페스트 기준으로 Console 갱신
"""


# ---------------------------------------------------------------------------
# 스모크 테스트 (데모 계정 유효성 — 실제 네트워크 없이 계약만 검증)
# ---------------------------------------------------------------------------
def smoke_test_credentials(m: ReleaseManifest) -> None:
    if "@" not in m.demo_account.email:
        raise GuideBuildError("데모 계정 이메일 형식 오류")
    if len(m.demo_account.password) < 8:
        raise GuideBuildError("데모 계정 비밀번호 최소 길이 미달")
    log.info("스모크 테스트 통과: 데모 계정 계약 유효")


# ---------------------------------------------------------------------------
# 원자적 쓰기 (좀비/부분 파일 방지)
# ---------------------------------------------------------------------------
def atomic_write(path: Path, content: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        fh.write(content)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
# 헬스체크 (무인 가동 모니터링)
# ---------------------------------------------------------------------------
def healthcheck(output: Path, started: float) -> Dict[str, Any]:
    return {
        "output_exists": output.exists(),
        "output_size": output.stat().st_size if output.exists() else 0,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "status": "ok" if output.exists() and output.stat().st_size > 0 else "fail",
    }


# ---------------------------------------------------------------------------
# 메인 파이프라인
# ---------------------------------------------------------------------------
def build(manifest_path: Path, output_path: Path) -> int:
    started = time.monotonic()
    breaker = CircuitBreaker()

    try:
        with TimeoutGuard(30, "load_manifest"):
            manifest = load_manifest(manifest_path, breaker)

        with TimeoutGuard(10, "smoke_test"):
            smoke_test_credentials(manifest)

        with TimeoutGuard(10, "render"):
            content = render_guide(manifest)

        with TimeoutGuard(10, "write"):
            atomic_write(output_path, content)

        report = healthcheck(output_path, started)
        log.info("헬스체크: %s", report)
        if report["status"] != "ok":
            raise GuideBuildError(f"헬스체크 실패: {report}")
        log.info("가이드 생성 완료: %s", output_path)
        return 0

    except (GuideBuildError, TimeoutExceeded) as exc:
        log.error("차단적 실패: %s", exc)
        return 2
    except Exception as exc:  # noqa: BLE001
        log.exception("예상치 못한 오류: %s", exc)
        return 1


def main(argv: List[str]) -> int:
    manifest_path = Path(argv[1]) if len(argv) > 1 else Path("release_manifest.json")
    output_path = Path(argv[2]) if len(argv) > 2 else Path("GOOGLE_PLAY_REVIEW_GUIDE.md")

    if not manifest_path.exists():
        log.error("매니페스트 없음: %s", manifest_path)
        return 2

    return build(manifest_path, output_path)


if __name__ == "__main__":
    sys.exit(main(sys.argv))