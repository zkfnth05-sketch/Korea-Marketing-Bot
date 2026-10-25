# -*- coding: utf-8 -*-
"""
Drama History Store
===================
드라마 엔진의 일별 제작 이력 저장소.

목적:
    - 같은 장르/장소/템플릿/대본이 연속 재사용되는 것을 방지하기 위한 근거 데이터.
    - DailyVariationPlanner 가 "최근 N일 이력"을 조회해 회피 결정을 내린다.

설계 원칙:
    - 원자적 쓰기: tempfile.mkstemp(dir=같은 폴더) -> write -> fsync -> os.replace
    - JSON 손상 시: logger.error(exc_info=True) + 원본 .corrupt 백업 + 빈 이력 재시작
    - try-except pass 금지 / replace 눈가림 금지
    - 루트 경로 하드코딩 금지: Path(__file__).resolve().parents[2]
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import tempfile
from datetime import date as _date
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 루트 산출 (하드코딩 금지)
#   <root>/modules/drama_engine/drama_history_store.py
#   parents[0] = drama_engine, parents[1] = modules, parents[2] = <root>
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
DATA_DIR: Path = PROJECT_ROOT / "data"

MAX_RECORDS: int = 400
DEFAULT_RECENT_DAYS: int = 7

# used_values(kind=...) 에서 허용하는 필드명
VALID_KINDS: Set[str] = {
    "genre_id",
    "location",
    "template_id",
    "script_hash",
    "hook_hash",
}


class DramaHistoryStore:
    """브랜드별 드라마 제작 이력 저장소."""

    def __init__(self, brand: str) -> None:
        if not brand or not str(brand).strip():
            raise ValueError("brand 는 비어 있을 수 없습니다.")
        self.brand: str = str(brand).strip()
        self.data_dir: Path = DATA_DIR
        self.path: Path = self.data_dir / f"drama_history_{self.brand}.json"
        self._ensure_data_dir()

    # -- 내부 유틸 ---------------------------------------------------------
    def _ensure_data_dir(self) -> None:
        """data 디렉터리 보장. 실패 시 logger.error 후 재발생(삼키기 금지)."""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            logger.error(
                "data 디렉터리 생성 실패: %s", self.data_dir, exc_info=True
            )
            raise

    @staticmethod
    def hash_text(text: str) -> str:
        """대본 전문/훅 전문의 sha256 hex digest."""
        if text is None:
            text = ""
        return hashlib.sha256(str(text).encode("utf-8")).hexdigest()

    @staticmethod
    def _today_str() -> str:
        return _date.today().isoformat()

    @staticmethod
    def _parse_date(value: Any) -> Optional[_date]:
        if not isinstance(value, str):
            return None
        try:
            return datetime.strptime(value.strip()[:10], "%Y-%m-%d").date()
        except ValueError:
            return None

    # -- 읽기 --------------------------------------------------------------
    def load(self) -> List[Dict[str, Any]]:
        """이력 전체 로드. 파일 없으면 빈 리스트. 손상 시 백업 후 빈 이력."""
        if not self.path.exists():
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as fp:
                raw = json.load(fp)
        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.error(
                "이력 JSON 손상 감지: %s -> .corrupt 백업 후 빈 이력으로 재시작",
                self.path,
                exc_info=True,
            )
            self._backup_corrupt()
            return []
        except OSError:
            logger.error("이력 파일 읽기 실패: %s", self.path, exc_info=True)
            raise

        if isinstance(raw, dict):
            raw = raw.get("records", [])
        if not isinstance(raw, list):
            logger.error(
                "이력 JSON 구조 이상(list 아님): %s -> .corrupt 백업 후 빈 이력",
                self.path,
                exc_info=True,
            )
            self._backup_corrupt()
            return []

        records: List[Dict[str, Any]] = []
        for item in raw:
            if isinstance(item, dict) and item.get("date"):
                records.append(item)
        return records

    def _backup_corrupt(self) -> None:
        """손상 원본을 .corrupt 로 보존. 백업 실패도 조용히 넘기지 않는다."""
        backup = self.path.with_suffix(self.path.suffix + ".corrupt")
        try:
            os.replace(self.path, backup)
            logger.error("손상 이력 백업 완료: %s", backup)
        except OSError:
            logger.error("손상 이력 백업 실패: %s", self.path, exc_info=True)
            raise

    # -- 쓰기 --------------------------------------------------------------
    def _atomic_write(self, records: List[Dict[str, Any]]) -> None:
        """tempfile -> write -> fsync -> os.replace 원자적 쓰기."""
        self._ensure_data_dir()
        fd, tmp_name = tempfile.mkstemp(
            prefix=f".{self.path.stem}_", suffix=".tmp", dir=str(self.data_dir)
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fp:
                json.dump(records, fp, ensure_ascii=False, indent=2)
                fp.flush()
                os.fsync(fp.fileno())
            os.replace(tmp_name, self.path)
        except OSError:
            logger.error("이력 원자적 쓰기 실패: %s", self.path, exc_info=True)
            if os.path.exists(tmp_name):
                try:
                    os.remove(tmp_name)
                except OSError:
                    logger.error(
                        "임시 파일 정리 실패: %s", tmp_name, exc_info=True
                    )
            raise

    def record(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """이력 1건 기록. 같은 date 는 덮어쓰기. 400건 롤링."""
        if not isinstance(entry, dict):
            raise TypeError("entry 는 dict 여야 합니다.")

        item: Dict[str, Any] = dict(entry)
        item.setdefault("date", self._today_str())
        item.setdefault("genre_id", "")
        item.setdefault("location", "")
        item.setdefault("template_id", "")
        item.setdefault("script_hash", "")
        item.setdefault("hook_hash", "")
        item["recorded_at"] = datetime.now().isoformat(timespec="seconds")

        records = self.load()
        target_date = item["date"]
        merged: List[Dict[str, Any]] = [
            r for r in records if r.get("date") != target_date
        ]
        merged.append(item)
        merged.sort(key=lambda r: str(r.get("date", "")))

        if len(merged) > MAX_RECORDS:
            merged = merged[-MAX_RECORDS:]

        self._atomic_write(merged)
        return item

    # -- 조회 --------------------------------------------------------------
    def recent(self, n_days: int = DEFAULT_RECENT_DAYS) -> List[Dict[str, Any]]:
        """최근 n_days 일(오늘 포함) 이력. 날짜 내림차순."""
        if n_days < 0:
            raise ValueError("n_days 는 0 이상이어야 합니다.")
        cutoff = _date.today() - timedelta(days=int(n_days))
        out: List[Dict[str, Any]] = []
        for rec in self.load():
            d = self._parse_date(rec.get("date"))
            if d is None:
                continue
            if d >= cutoff:
                out.append(rec)
        out.sort(key=lambda r: str(r.get("date", "")), reverse=True)
        return out

    def used_values(self, kind: str, n_days: int = DEFAULT_RECENT_DAYS) -> Set[str]:
        """최근 n_days 동안 사용된 특정 필드 값 집합."""
        if kind not in VALID_KINDS:
            raise ValueError(
                f"kind 는 {sorted(VALID_KINDS)} 중 하나여야 합니다. (입력: {kind!r})"
            )
        values: Set[str] = set()
        for rec in self.recent(n_days=n_days):
            val = rec.get(kind)
            if isinstance(val, str) and val.strip():
                values.add(val.strip())
        return values

    def is_recently_used(
        self, kind: str, value: str, n_days: int = DEFAULT_RECENT_DAYS
    ) -> bool:
        """최근 n_days 안에 해당 값이 쓰였는지 여부."""
        if not isinstance(value, str) or not value.strip():
            return False
        return value.strip() in self.used_values(kind=kind, n_days=n_days)


# ---------------------------------------------------------------------------
# 자체 점검
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(name)s: %(message)s",
    )

    print("=" * 68)
    print("DramaHistoryStore 자체 점검")
    print("=" * 68)
    print(f"PROJECT_ROOT : {PROJECT_ROOT}")
    print(f"DATA_DIR     : {DATA_DIR} (exists={DATA_DIR.is_dir()})")

    TEST_BRAND = "selftest"
    store = DramaHistoryStore(TEST_BRAND)
    print(f"STORE PATH   : {store.path}")

    # 기존 테스트 잔여물 정리
    for leftover in (
        store.path,
        store.path.with_suffix(store.path.suffix + ".corrupt"),
    ):
        if leftover.exists():
            os.remove(leftover)
            print(f"기존 잔여물 삭제: {leftover.name}")

    # 10일치 기록
    print("\n[1] 10일치 기록")
    today = _date.today()
    for i in range(10):
        d = (today - timedelta(days=i)).isoformat()
        script = f"대본-{i}-{d}"
        hook = f"훅-{i}-{d}"
        store.record(
            {
                "date": d,
                "genre_id": f"genre_{i % 3}",
                "location": f"loc_{i % 4}",
                "template_id": f"tpl_{i % 2}",
                "script_hash": DramaHistoryStore.hash_text(script),
                "hook_hash": DramaHistoryStore.hash_text(hook),
            }
        )
    print(f"    기록 완료 -> load() 건수 = {len(store.load())}")

    # recent
    print("\n[2] recent(n_days=7)")
    rec7 = store.recent(n_days=7)
    print(f"    건수 = {len(rec7)}")
    for r in rec7:
        print(
            f"    {r['date']} | {r['genre_id']:<9} | {r['location']:<6} | "
            f"{r['template_id']:<6} | script={r['script_hash'][:12]}..."
        )

    # used_values
    print("\n[3] used_values")
    for kind in ("genre_id", "location", "template_id"):
        vals = store.used_values(kind, n_days=7)
        print(f"    {kind:<12} (7일) = {sorted(vals)}")
    print(f"    genre_id     (10일) = {sorted(store.used_values('genre_id', 10))}")

    # is_recently_used
    print("\n[4] is_recently_used")
    checks = [
        ("genre_id", "genre_0", 7),
        ("genre_id", "genre_0", 10),
        ("location", "loc_3", 7),
        ("template_id", "tpl_1", 7),
        ("genre_id", "genre_없음", 7),
    ]
    for kind, value, nd in checks:
        result = store.is_recently_used(kind, value, n_days=nd)
        print(f"    {kind:<12} {value:<12} n_days={nd:<2} -> {result}")

    # 덮어쓰기 검증
    print("\n[5] 같은 date 덮어쓰기 검증")
    before = len(store.load())
    store.record(
        {
            "date": today.isoformat(),
            "genre_id": "genre_OVERWRITE",
            "location": "loc_OVERWRITE",
            "template_id": "tpl_OVERWRITE",
            "script_hash": DramaHistoryStore.hash_text("덮어쓴 대본"),
            "hook_hash": DramaHistoryStore.hash_text("덮어쓴 훅"),
        }
    )
    after = len(store.load())
    print(f"    건수 before={before} after={after} (동일해야 정상)")
    print(f"    오늘 genre_id = {store.load()[-1]['genre_id']}")

    # 손상 복구 검증
    print("\n[6] JSON 손상 복구 검증")
    with open(store.path, "w", encoding="utf-8") as fp:
        fp.write("{ this is not valid json ")
    recovered = store.load()
    corrupt_path = store.path.with_suffix(store.path.suffix + ".corrupt")
    print(f"    손상 후 load() 건수 = {len(recovered)} (0 이어야 정상)")
    print(f"    .corrupt 백업 존재 = {corrupt_path.exists()}")

    # 정리
    print("\n[7] 테스트 파일 정리")
    for leftover in (store.path, corrupt_path):
        if leftover.exists():
            os.remove(leftover)
            print(f"    삭제: {leftover.name}")
    print(f"    최종 잔여 파일 존재 = {store.path.exists()}")

    print("\n" + "=" * 68)
    print("자체 점검 완료")
    print("=" * 68)
