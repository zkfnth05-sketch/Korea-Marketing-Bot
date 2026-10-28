# -*- coding: utf-8 -*-
"""
[독립 모듈] 3대 브랜드 일일 완제품 영수증 & 송출 3회 서킷브레이커 가드
(core/receipt_engine/daily_receipt_guard.py)

• 역할:
  1. 브랜드별 일일 생산 쿼터 강제 (숏폼 3개 / 카드뉴스 2개)
  2. 바탕화면 실물 산출물(한국 숏폼_산출물, 한국 카드뉴스_산출물) 자동 스캔 → 당일 완제품 자동 영수증 등록
  3. 송출 재시도 상한 3회 서킷브레이커 (3회 실패 시 당일 송출 영구 중단 + 데드레터 격리)

• 무인화 안전 수칙:
  - 원자적 JSON 쓰기 (.tmp 생성 후 os.replace)
  - threading.Lock (프로세스 내) + 파일시스템 락 (프로세스 간) 이중 보호
  - 생산/송출 100% 단방향 분리: 송출 실패가 생산을 재호출하는 역류 경로 원천 차단
    → 이 모듈은 '생산 실행 함수'를 단 하나도 import 하지 않으며, 송출 실패 시
      오직 상태 플래그(dead_letter)만 기록합니다. 재생산 트리거는 존재하지 않습니다.
"""

import os
import re
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional

# ---------------------------------------------------------------------------
# 프로젝트 표준 시각 소스 (KST 단일 소스). 실패 시 로컬 폴백.
# ---------------------------------------------------------------------------
try:
    from config import get_now_kst_str  # type: ignore
except Exception:  # pragma: no cover - 단독 실행/테스트 환경 폴백
    def get_now_kst_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        return time.strftime(fmt, time.localtime())


# ---------------------------------------------------------------------------
# 상수 정의
# ---------------------------------------------------------------------------
DAILY_QUOTAS: Dict[str, int] = {"shorts": 3, "cardnews": 2}
MAX_DISPATCH_RETRIES: int = 3

# 바탕화면 실물 산출물 루트 (emergency_guard.py 와 동일 규약)
DESKTOP_DIR = Path("C:/Users/zkfnt/Desktop")
SHORTS_BASE = DESKTOP_DIR / "한국 숏폼_산출물"
CARDNEWS_BASE = DESKTOP_DIR / "한국 카드뉴스_산출물"

# 브랜드 → 실제 폴더명 매핑 (실측 확정: 숏폼은 영문, 카드뉴스는 한글)
SHORTS_BRAND_DIRS: Dict[str, str] = {
    "aura": "Aura",
    "insurance": "Insurance",
    "stock": "Stock",
}
CARDNEWS_BRAND_DIRS: Dict[str, str] = {
    "aura": "아우라",
    "insurance": "보험",
    "stock": "주식",
}

# 완제품으로 인정하는 확장자
SHORTS_EXTS = {".mp4", ".mov", ".mkv", ".webm"}
CARDNEWS_EXTS = {".png", ".jpg", ".jpeg", ".webp"}

# 숏폼 조각 파일(중간 산출물) 제외 규칙 — emergency_guard.py 규약 계승
SHORTS_FRAGMENT_PREFIXES = ("01_", "02_", "03_", "04_", "05_")
SHORTS_FRAGMENT_KEYWORDS = ("cta", "temp", "tmp", "preview", "fragment", "scene")

# 카드뉴스 topic_id 추출 정규식 (폴더/파일명 → 주제 번호)
# 예: '주제_3', '주제3', 'topic_12', 'T[5]', 'T 7', '03_아우라_...'
_TOPIC_ID_PATTERN = re.compile(r"(?:주제|topic|T)?[_\[\s]*(\d{1,3})", re.IGNORECASE)

# 상태 저장 경로
try:
    from config import DATA_DIR as _CFG_DATA_DIR  # type: ignore
    STATE_DIR = Path(_CFG_DATA_DIR)
except Exception:  # pragma: no cover
    STATE_DIR = Path(__file__).resolve().parents[2] / "data"

STATE_FILE = STATE_DIR / "daily_receipt_guard_state.json"
LOCK_FILE = STATE_DIR / "daily_receipt_guard.lock"

# 프로세스 내 재진입 방지 락 (RLock: 같은 스레드 내 중첩 호출 안전)
_THREAD_LOCK = threading.RLock()


# ---------------------------------------------------------------------------
# 파일시스템 락 (프로세스 간 동기화) — Windows msvcrt / POSIX fcntl
# ---------------------------------------------------------------------------
class _FileLock:
    """크로스 프로세스 배타 락. 원자적 JSON 쓰기 구간 전체를 감쌉니다."""

    def __init__(self, lock_path: Path, timeout: float = 10.0):
        self.lock_path = Path(lock_path)
        self.timeout = timeout
        self._fh = None

    def __enter__(self):
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self.lock_path, "a+b")
        deadline = time.time() + self.timeout
        while True:
            try:
                self._acquire_os_lock()
                return self
            except (OSError, IOError):
                if time.time() >= deadline:
                    # 락 획득 실패 시에도 파일 핸들은 반드시 닫습니다.
                    try:
                        self._fh.close()
                    finally:
                        self._fh = None
                    raise TimeoutError(
                        f"파일 락 획득 실패(타임아웃 {self.timeout}s): {self.lock_path}"
                    )
                time.sleep(0.02)

    def _acquire_os_lock(self):
        if os.name == "nt":
            import msvcrt
            self._fh.seek(0)
            msvcrt.locking(self._fh.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _release_os_lock(self):
        try:
            if os.name == "nt":
                import msvcrt
                self._fh.seek(0)
                msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
        except Exception:
            pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._fh is not None:
            self._release_os_lock()
            try:
                self._fh.close()
            finally:
                self._fh = None
        return False


class DailyReceiptGuard:
    """3대 브랜드 일일 완제품 영수증 & 송출 3회 서킷브레이커 가드"""

    def __init__(self, state_file: Optional[Path] = None, lock_file: Optional[Path] = None):
        self.state_file = Path(state_file) if state_file else STATE_FILE
        self.lock_file = Path(lock_file) if lock_file else LOCK_FILE
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    # =======================================================================
    # 내부 유틸 — 날짜 / 상태 입출력
    # =======================================================================
    @staticmethod
    def _today_key() -> str:
        """당일 날짜 키 (YYYY-MM-DD). 일일 쿼터 리셋 기준."""
        return get_now_kst_str("%Y-%m-%d")

    @staticmethod
    def _today_compact() -> str:
        """당일 날짜 압축형 (YYYYMMDD). 폴더/파일명 매칭용."""
        return get_now_kst_str("%Y%m%d")

    @staticmethod
    def _now_str() -> str:
        return get_now_kst_str("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _normalize_brand(brand: str) -> str:
        b = (brand or "").strip().lower()
        if b not in SHORTS_BRAND_DIRS:
            raise ValueError(
                f"지원하지 않는 브랜드입니다: '{brand}'. "
                f"허용: {sorted(SHORTS_BRAND_DIRS.keys())}"
            )
        return b

    @staticmethod
    def _normalize_media(media_type: str) -> str:
        m = (media_type or "").strip().lower()
        if m not in DAILY_QUOTAS:
            raise ValueError(
                f"지원하지 않는 미디어 타입입니다: '{media_type}'. "
                f"허용: {sorted(DAILY_QUOTAS.keys())}"
            )
        return m

    @staticmethod
    def _receipt_key(brand: str, media_type: str, topic_id: int) -> str:
        return f"{brand}::{media_type}::{int(topic_id)}"

    @staticmethod
    def _empty_state() -> Dict[str, Any]:
        return {"version": 1, "updated_at": "", "days": {}}

    def _read_state(self) -> Dict[str, Any]:
        """상태 파일 로드. 손상 시 빈 상태로 안전 복구(무인 가동 중단 방지)."""
        if not self.state_file.exists():
            return self._empty_state()
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict) or "days" not in data:
                return self._empty_state()
            if not isinstance(data.get("days"), dict):
                data["days"] = {}
            return data
        except Exception:
            # 손상된 파일은 격리 후 빈 상태로 재시작 (예외 전파 금지)
            try:
                broken = self.state_file.with_suffix(
                    f".corrupt.{int(time.time())}.json"
                )
                os.replace(self.state_file, broken)
            except Exception:
                pass
            return self._empty_state()

    def _write_state_atomic(self, state: Dict[str, Any]) -> None:
        """원자적 JSON 쓰기: .tmp 생성 → flush/fsync → os.replace."""
        state["updated_at"] = self._now_str()
        tmp_path = self.state_file.with_suffix(
            f".tmp.{os.getpid()}.{threading.get_ident()}"
        )
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self.state_file)
        finally:
            if tmp_path.exists():
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    def _day_bucket(self, state: Dict[str, Any], day: Optional[str] = None) -> Dict[str, Any]:
        """당일 버킷 확보. 날짜가 바뀌면 자동으로 새 버킷 생성(=일일 쿼터 리셋)."""
        d = day or self._today_key()
        days = state.setdefault("days", {})
        bucket = days.setdefault(d, {})
        bucket.setdefault("receipts", {})
        bucket.setdefault("counters", {})
        bucket.setdefault("dispatch_attempts", {})
        bucket.setdefault("dead_letters", {})
        return bucket

    def _counter_key(self, brand: str, media_type: str) -> str:
        return f"{brand}::{media_type}"

    # =======================================================================
    # 1) 생산 쿼터
    # =======================================================================
    def get_remaining_quota(self, brand: str, media_type: str) -> int:
        """당일 남은 생산 가능 수량 반환 (0 이상)."""
        b = self._normalize_brand(brand)
        m = self._normalize_media(media_type)
        quota = DAILY_QUOTAS[m]

        with _THREAD_LOCK:
            with _FileLock(self.lock_file):
                state = self._read_state()
                bucket = self._day_bucket(state)
                used = int(bucket["counters"].get(self._counter_key(b, m), 0))

        remaining = quota - used
        return remaining if remaining > 0 else 0

    def can_produce(self, brand: str, media_type: str) -> bool:
        """당일 쿼터가 남아 있으면 True. (생산 실행은 하지 않음 — 판단만)"""
        return self.get_remaining_quota(brand, media_type) > 0

    # =======================================================================
    # 2) 영수증 봉인 (완제품 등록)
    # =======================================================================
    def seal_receipt(
        self, brand: str, media_type: str, topic_id: int, artifact_path: str
    ) -> str:
        """
        완제품 영수증을 봉인(등록)하고 receipt_key 를 반환합니다.

        • 쿼터 초과 시 등록 거부 (ValueError)
        • 동일 (brand, media_type, topic_id) 재봉인은 멱등 처리 (기존 키 반환)
        • 실물 파일이 존재하면 크기/수정시각을 함께 기록
        """
        b = self._normalize_brand(brand)
        m = self._normalize_media(media_type)
        tid = int(topic_id)
        key = self._receipt_key(b, m, tid)

        artifact = Path(artifact_path) if artifact_path else None
        exists = bool(artifact and artifact.exists())
        size_bytes = 0
        mtime_str = ""
        if exists:
            try:
                st = artifact.stat()
                size_bytes = int(st.st_size)
                mtime_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime))
            except Exception:
                pass

        with _THREAD_LOCK:
            with _FileLock(self.lock_file):
                state = self._read_state()
                bucket = self._day_bucket(state)
                receipts = bucket["receipts"]

                # 멱등: 이미 봉인된 영수증이면 그대로 반환
                if key in receipts:
                    return key

                ckey = self._counter_key(b, m)
                used = int(bucket["counters"].get(ckey, 0))
                if used >= DAILY_QUOTAS[m]:
                    raise ValueError(
                        f"[쿼터 초과] {b}/{m} 당일 생산 한도 {DAILY_QUOTAS[m]}개를 "
                        f"이미 모두 사용했습니다. (topic_id={tid})"
                    )

                receipts[key] = {
                    "brand": b,
                    "media_type": m,
                    "topic_id": tid,
                    "artifact_path": str(artifact) if artifact else "",
                    "artifact_exists": exists,
                    "size_bytes": size_bytes,
                    "artifact_mtime": mtime_str,
                    "sealed_at": self._now_str(),
                    "day": self._today_key(),
                    # 송출 상태 (단방향: 송출 실패는 이 플래그만 변경)
                    "dispatch_attempts": 0,
                    "dispatched": False,
                    "dead_letter": False,
                    "last_error": "",
                    "last_attempt_at": "",
                    "dispatched_at": "",
                }
                bucket["counters"][ckey] = used + 1
                self._write_state_atomic(state)

        return key

    # =======================================================================
    # 3) 송출 판정 / 결과 기록 (서킷브레이커)
    # =======================================================================
    def can_dispatch(self, brand: str, media_type: str, topic_id: int) -> bool:
        """
        송출 가능 여부 판정.
        • 영수증 미봉인 → False
        • 이미 송출 성공 → False (중복 송출 차단)
        • 데드레터 격리됨 → False (당일 영구 중단)
        • 재시도 3회 도달 → False
        """
        b = self._normalize_brand(brand)
        m = self._normalize_media(media_type)
        key = self._receipt_key(b, m, int(topic_id))

        with _THREAD_LOCK:
            with _FileLock(self.lock_file):
                state = self._read_state()
                bucket = self._day_bucket(state)
                receipt = bucket["receipts"].get(key)

        if not receipt:
            return False
        if receipt.get("dispatched"):
            return False
        if receipt.get("dead_letter"):
            return False
        if int(receipt.get("dispatch_attempts", 0)) >= MAX_DISPATCH_RETRIES:
            return False
        return True

    def record_dispatch_result(
        self,
        brand: str,
        media_type: str,
        topic_id: int,
        success: bool,
        error_msg: str = "",
    ) -> None:
        """
        송출 결과 기록.

        🚨 단방향 설계 원칙:
          - 이 메서드는 오직 '상태 기록'만 수행합니다.
          - 실패 시에도 생산 파이프라인을 절대 호출/재호출하지 않습니다.
            (이 모듈은 생산 모듈을 import 하지 않으며, 재생산 트리거 코드가 존재하지 않음)
          - 3회 실패 도달 시 dead_letter=True 로 당일 송출 영구 중단 + 격리.
        """
        b = self._normalize_brand(brand)
        m = self._normalize_media(media_type)
        key = self._receipt_key(b, m, int(topic_id))

        with _THREAD_LOCK:
            with _FileLock(self.lock_file):
                state = self._read_state()
                bucket = self._day_bucket(state)
                receipt = bucket["receipts"].get(key)

                if not receipt:
                    # 영수증 없는 송출 결과는 무시 (생산 역류 방지: 새로 만들지 않음)
                    return

                now = self._now_str()
                receipt["last_attempt_at"] = now

                if success:
                    receipt["dispatched"] = True
                    receipt["dispatched_at"] = now
                    receipt["last_error"] = ""
                    self._write_state_atomic(state)
                    return

                # ---- 실패 처리 ----
                attempts = int(receipt.get("dispatch_attempts", 0)) + 1
                receipt["dispatch_attempts"] = attempts
                receipt["last_error"] = (error_msg or "")[:500]

                if attempts >= MAX_DISPATCH_RETRIES:
                    receipt["dead_letter"] = True
                    receipt["dead_letter_at"] = now
                    bucket["dead_letters"][key] = {
                        "brand": b,
                        "media_type": m,
                        "topic_id": int(topic_id),
                        "attempts": attempts,
                        "error": receipt["last_error"],
                        "quarantined_at": now,
                        "note": "당일 송출 영구 중단 (3회 서킷브레이커 작동)",
                    }

                self._write_state_atomic(state)

    # =======================================================================
    # 4) 송출 대상 조회
    # =======================================================================
    def get_dispatchable_receipts(self, brand: str, media_type: str) -> List[Dict[str, Any]]:
        """송출 가능한 영수증 목록 반환 (봉인 순서 유지)."""
        b = self._normalize_brand(brand)
        m = self._normalize_media(media_type)

        with _THREAD_LOCK:
            with _FileLock(self.lock_file):
                state = self._read_state()
                bucket = self._day_bucket(state)
                receipts = dict(bucket["receipts"])

        result: List[Dict[str, Any]] = []
        for key, r in receipts.items():
            if r.get("brand") != b or r.get("media_type") != m:
                continue
            if r.get("dispatched") or r.get("dead_letter"):
                continue
            if int(r.get("dispatch_attempts", 0)) >= MAX_DISPATCH_RETRIES:
                continue
            item = dict(r)
            item["receipt_key"] = key
            item["remaining_retries"] = MAX_DISPATCH_RETRIES - int(
                r.get("dispatch_attempts", 0)
            )
            result.append(item)

        result.sort(key=lambda x: (x.get("sealed_at", ""), x.get("topic_id", 0)))
        return result

    # =======================================================================
    # 5) 바탕화면 실물 산출물 자동 스캔 → 자동 영수증 등록
    # =======================================================================
    @staticmethod
    def _is_today_name(name: str, today_compact: str, today_dash: str) -> bool:
        """폴더/파일명에 당일 날짜(YYYYMMDD 또는 YYYY-MM-DD)가 포함되는지."""
        return (today_compact in name) or (today_dash in name)

    @staticmethod
    def _extract_topic_id(name: str) -> Optional[int]:
        """
        폴더/파일명에서 topic_id 를 안전하게 추출한다.

        지원 패턴 예: '주제_3', '주제3', 'topic_12', 'T[5]', 'T 7', '3', '03_...'
        • 정규식: r'(?:주제|topic|T)?[_\\[\\s]*(\\d{1,3})'
        • 추출 실패 또는 0 이하 값은 None 반환 (호출측에서 순번 폴백)
        """
        if not name:
            return None
        try:
            match = _TOPIC_ID_PATTERN.search(str(name))
        except Exception:
            return None
        if not match:
            return None
        try:
            tid = int(match.group(1))
        except Exception:
            return None
        return tid if tid > 0 else None

    def _scan_brand_artifacts(self, brand: str, media_type: str) -> List[Path]:
        """
        당일 날짜가 붙은 완제품 목록 수집.

        • shorts   : 완제품 영상 파일(mp4 등) 1개 = 완제품 1개 (조각/임시 파일 배제)
        • cardnews : 슬라이드 이미지들이 담긴 '패키지 디렉터리' 1개 = 완제품 1개
                     (개별 slide_1.png / slide_2.png 를 각각 완제품으로 세지 않음)
                     대표 경로는 d/'slide_1.png' 가 있으면 그 파일, 없으면 폴더 자체.
        """
        b = self._normalize_brand(brand)
        m = self._normalize_media(media_type)
        today_compact = self._today_compact()
        today_dash = self._today_key()

        if m == "shorts":
            base = SHORTS_BASE / SHORTS_BRAND_DIRS[b]
            exts = SHORTS_EXTS
        else:
            base = CARDNEWS_BASE / CARDNEWS_BRAND_DIRS[b]
            exts = CARDNEWS_EXTS

        if not base.exists():
            return []

        found: List[Path] = []
        try:
            if m == "cardnews":
                # ---- 카드뉴스: 패키지 디렉터리 단위 수집 ----
                for d in base.rglob("*"):
                    if not d.is_dir():
                        continue

                    # 폴더명(또는 상위 경로)에 당일 날짜가 있어야 '당일 완제품'
                    rel_parts = d.relative_to(base).parts
                    name_hit = any(
                        self._is_today_name(part, today_compact, today_dash)
                        for part in rel_parts
                    )
                    if not name_hit:
                        continue

                    # 폴더 내부에 유효한 슬라이드 이미지가 최소 1장 있어야 인정
                    has_slide = False
                    try:
                        for child in d.iterdir():
                            if child.is_file() and child.suffix.lower() in exts:
                                has_slide = True
                                break
                    except Exception:
                        continue
                    if not has_slide:
                        continue

                    # 대표 경로: slide_1.png 우선, 없으면 폴더 자체
                    slide_1 = d / "slide_1.png"
                    found.append(slide_1 if slide_1.is_file() else d)
            else:
                # ---- 숏폼: 완제품 영상 파일 단위 수집 ----
                for p in base.rglob("*"):
                    if not p.is_file():
                        continue
                    if p.suffix.lower() not in exts:
                        continue

                    # 파일명 또는 상위 폴더명에 당일 날짜가 있어야 '당일 완제품'
                    rel_parts = p.relative_to(base).parts
                    name_hit = any(
                        self._is_today_name(part, today_compact, today_dash)
                        for part in rel_parts
                    )
                    if not name_hit:
                        continue

                    # 숏폼 조각 파일 배제
                    low = p.name.lower()
                    if any(low.startswith(pre) for pre in SHORTS_FRAGMENT_PREFIXES):
                        continue
                    if any(kw in low for kw in SHORTS_FRAGMENT_KEYWORDS):
                        continue

                    # 🚨 중간 씬 클립 배제 — 상위 폴더 경로에 'scene' 이 포함되어 있거나
                    #    'scene_' 으로 시작하는 폴더 내부의 영상은 최종 완제품이 아닙니다.
                    #    (예: .../scene_01/scene.mp4, .../scenes/scene_03.mp4)
                    parent_parts = [str(part).lower() for part in rel_parts[:-1]]
                    if any("scene" in part for part in parent_parts):
                        continue
                    if any(part.startswith("scene_") for part in parent_parts):
                        continue

                    found.append(p)
        except Exception:
            return found

        found.sort(key=lambda x: str(x))
        return found

    def auto_scan_and_seal(self, brand: str, media_type: str) -> List[str]:
        """
        바탕화면 실물 산출물을 스캔하여 당일 완제품을 자동 영수증 등록합니다.

        • 카드뉴스는 '패키지 폴더 1개 = 완제품 1개' 로 집계합니다.
          (폴더 내 5장 슬라이드가 5개 주제로 둔갑하는 쿼터 낭비를 원천 차단)
        • topic_id 는 폴더/파일명에서 정규식으로 추출하며, 추출 실패 시 순번 폴백.
        • 이미 (brand, media_type, topic_id) 가 봉인되어 있으면 멱등 스킵.
        • 쿼터(숏폼 3 / 카드뉴스 2) 잔여분 내에서만 봉인합니다.
        • 반환: 새로 봉인된 receipt_key 목록
        """
        b = self._normalize_brand(brand)
        m = self._normalize_media(media_type)

        artifacts = self._scan_brand_artifacts(b, m)
        if not artifacts:
            return []

        # 이미 봉인된 topic_id / artifact_path 집합 (멱등 중복 방지)
        with _THREAD_LOCK:
            with _FileLock(self.lock_file):
                state = self._read_state()
                bucket = self._day_bucket(state)
                sealed_topic_ids = set()
                sealed_paths = set()
                for r in bucket["receipts"].values():
                    if r.get("brand") != b or r.get("media_type") != m:
                        continue
                    try:
                        sealed_topic_ids.add(int(r.get("topic_id", -1)))
                    except Exception:
                        pass
                    ap = r.get("artifact_path")
                    if ap:
                        sealed_paths.add(str(ap))

        sealed_keys: List[str] = []
        for idx, path in enumerate(artifacts, start=1):
            # 1) topic_id 결정 — '패키지 폴더명' 최우선 추출 → 실패 시 순번 폴백
            #    🚨 대표 경로가 d/'slide_1.png' 인 경우 path.name('slide_1.png')에서
            #       숫자 1을 잘못 뽑아 실제 폴더명(예: '아우라_06_...' → 주제 6번)을
            #       덮어쓰는 사고를 원천 차단합니다.
            folder_name = path.parent.name if path.is_file() else path.name
            topic_id = self._extract_topic_id(folder_name)

            # 1-1) 폴더명에서 못 찾은 경우에만 파일명 시도.
            #      단, 'slide_' 로 시작하는 슬라이드 파일명은 topic_id 추출 대상에서 제외.
            if topic_id is None and path.is_file():
                file_stem = path.name
                if not file_stem.lower().startswith("slide_"):
                    topic_id = self._extract_topic_id(file_stem)

            # 1-2) 그래도 없으면 순번 폴백
            if topic_id is None:
                topic_id = idx

            # 2) 멱등 스킵 — 동일 topic_id 또는 동일 대표 경로는 재봉인 금지
            if topic_id in sealed_topic_ids:
                continue
            if str(path) in sealed_paths:
                continue

            # 3) 쿼터 잔여 확인 — 남은 쿼터 내에서만 봉인
            if not self.can_produce(b, m):
                break

            try:
                key = self.seal_receipt(b, m, topic_id=topic_id, artifact_path=str(path))
                sealed_keys.append(key)
                sealed_topic_ids.add(topic_id)
                sealed_paths.add(str(path))
            except ValueError:
                # 쿼터 초과 — 더 이상 등록하지 않음
                break
            except Exception:
                continue

        return sealed_keys

    def auto_scan_all(self) -> Dict[str, List[str]]:
        """3대 브랜드 × 2개 미디어 전량 자동 스캔/봉인."""
        report: Dict[str, List[str]] = {}
        for b in SHORTS_BRAND_DIRS.keys():
            for m in DAILY_QUOTAS.keys():
                try:
                    report[f"{b}::{m}"] = self.auto_scan_and_seal(b, m)
                except Exception:
                    report[f"{b}::{m}"] = []
        return report

    # =======================================================================
    # 6) 관제용 스냅샷
    # =======================================================================
    def get_daily_snapshot(self) -> Dict[str, Any]:
        """대시보드 표시용 당일 현황 스냅샷."""
        with _THREAD_LOCK:
            with _FileLock(self.lock_file):
                state = self._read_state()
                bucket = self._day_bucket(state)
                receipts = dict(bucket["receipts"])
                counters = dict(bucket["counters"])
                dead_letters = dict(bucket["dead_letters"])

        brands: Dict[str, Any] = {}
        for b in SHORTS_BRAND_DIRS.keys():
            brands[b] = {}
            for m in DAILY_QUOTAS.keys():
                ckey = self._counter_key(b, m)
                used = int(counters.get(ckey, 0))
                items = [
                    r for r in receipts.values()
                    if r.get("brand") == b and r.get("media_type") == m
                ]
                brands[b][m] = {
                    "quota": DAILY_QUOTAS[m],
                    "used": used,
                    "remaining": max(0, DAILY_QUOTAS[m] - used),
                    "sealed": len(items),
                    "dispatched": sum(1 for r in items if r.get("dispatched")),
                    "dead_letter": sum(1 for r in items if r.get("dead_letter")),
                }

        return {
            "day": self._today_key(),
            "checked_at": self._now_str(),
            "quotas": dict(DAILY_QUOTAS),
            "max_dispatch_retries": MAX_DISPATCH_RETRIES,
            "brands": brands,
            "dead_letters": dead_letters,
            "total_dead_letters": len(dead_letters),
        }


# ---------------------------------------------------------------------------
# 모듈 레벨 싱글턴 (무인 데몬에서 공용 사용)
# ---------------------------------------------------------------------------
_DEFAULT_GUARD: Optional[DailyReceiptGuard] = None
_DEFAULT_GUARD_LOCK = threading.Lock()


def get_guard() -> DailyReceiptGuard:
    """프로세스 전역 DailyReceiptGuard 싱글턴 반환."""
    global _DEFAULT_GUARD
    if _DEFAULT_GUARD is None:
        with _DEFAULT_GUARD_LOCK:
            if _DEFAULT_GUARD is None:
                _DEFAULT_GUARD = DailyReceiptGuard()
    return _DEFAULT_GUARD


__all__ = [
    "DAILY_QUOTAS",
    "MAX_DISPATCH_RETRIES",
    "SHORTS_BASE",
    "CARDNEWS_BASE",
    "SHORTS_BRAND_DIRS",
    "CARDNEWS_BRAND_DIRS",
    "DailyReceiptGuard",
    "get_guard",
]
