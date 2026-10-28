# -*- coding: utf-8 -*-
"""
run_aura_cardnews.py - 💖 [Aura 카드뉴스 봇 무인 자율 구동 진입점]
===================================================================
• 숏폼 엔진과 100% 분리된 순수 카드뉴스 전용 실행기
• 시나리오 디렉터 ➔ Wan 2.1 T2I ➔ 타이포그래피 ➔ 바탕화면 이지텍스 규격 저장
• [구조 개선] 계약 단일화 / 영수증 기반 성공 판정 / 멱등 재시도 / 얇은 어댑터
"""

import sys
import os
import json
import hashlib
import logging
import argparse
import tempfile
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional

# 콘솔 UTF-8 설정
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("RunAuraCardnews")

WORKSPACE_DIR = Path(__file__).resolve().parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from brands.aura.aura_cardnews_producer import AuraCardnewsProducer


# ============================================================================
# [1] 단일 정규 계약 (Contract) — producer/consumer 공용 스키마
# ============================================================================
class ContractViolation(Exception):
    """산출물 반환 스키마 계약 위반."""
    pass


@dataclass
class SlideResult:
    """단일 슬라이드 산출물 정규 계약."""
    topic_id: int
    slide_num: int
    output_dir: str
    slide_path: str


@dataclass
class CardnewsResult:
    """풀세트 카드뉴스 산출물 정규 계약."""
    topic_id: int
    output_dir: str
    slide_paths: List[str] = field(default_factory=list)
    total_slides: int = 0
    guide_path: str = ""
    metadata_path: str = ""


def _pick(d: Dict[str, Any], *keys: str) -> Optional[Any]:
    """여러 후보 키 중 첫 번째로 존재하는 값을 반환 (계약 정규화용)."""
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return None


def validate_slide_result(raw: Any, topic_id: int, slide_num: int) -> SlideResult:
    """단일 슬라이드 결과를 정규 계약으로 검증·정규화."""
    if not isinstance(raw, dict):
        raise ContractViolation(f"produce_slide 반환값이 dict가 아님: {type(raw).__name__}")
    out_dir = _pick(raw, "output_dir", "target_directory", "target_dir")
    slide_path = _pick(raw, "slide_path", "image_path", "path")
    missing = []
    if not out_dir:
        missing.append("output_dir|target_directory|target_dir")
    if not slide_path:
        missing.append("slide_path|image_path|path")
    if missing:
        raise ContractViolation(
            f"produce_slide 계약 위반 — 누락 필드: {missing} / 실제 키: {sorted(raw.keys())}"
        )
    return SlideResult(
        topic_id=topic_id,
        slide_num=slide_num,
        output_dir=str(out_dir),
        slide_path=str(slide_path),
    )


def validate_cardnews_result(raw: Any, topic_id: int) -> CardnewsResult:
    """풀세트 결과를 정규 계약으로 검증·정규화."""
    if not isinstance(raw, dict):
        raise ContractViolation(f"produce_cardnews 반환값이 dict가 아님: {type(raw).__name__}")
    out_dir = _pick(raw, "output_dir", "target_directory", "target_dir")
    slide_paths = _pick(raw, "slide_paths", "slides") or []
    if not out_dir:
        raise ContractViolation(
            f"produce_cardnews 계약 위반 — output_dir 계열 필드 누락 / 실제 키: {sorted(raw.keys())}"
        )
    if not isinstance(slide_paths, (list, tuple)) or len(slide_paths) == 0:
        raise ContractViolation(
            f"produce_cardnews 계약 위반 — slide_paths 비어있음 / 실제 키: {sorted(raw.keys())}"
        )
    return CardnewsResult(
        topic_id=topic_id,
        output_dir=str(out_dir),
        slide_paths=[str(p) for p in slide_paths],
        total_slides=int(_pick(raw, "total_slides") or len(slide_paths)),
        guide_path=str(_pick(raw, "guide_path") or ""),
        metadata_path=str(_pick(raw, "metadata_path") or ""),
    )


# ============================================================================
# [2] 영수증(Receipt) — 성공 판정의 단일 진실 원천
# ============================================================================
RECEIPT_DIR = WORKSPACE_DIR / ".aura_receipts"


def _receipt_path(topic_id: int, scope: str) -> Path:
    return RECEIPT_DIR / f"topic_{topic_id:03d}_{scope}.json"


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""


def _atomic_write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass


def write_receipt(topic_id: int, scope: str, result: Any) -> Path:
    """주제ID + 산출물 매니페스트를 원자적으로 기록."""
    if isinstance(result, SlideResult):
        artifacts = [result.slide_path]
        payload = asdict(result)
    else:
        artifacts = list(result.slide_paths)
        payload = asdict(result)
    manifest = []
    for p in artifacts:
        fp = Path(p)
        manifest.append({
            "path": str(fp),
            "exists": fp.exists(),
            "sha256": _file_sha256(fp) if fp.exists() else "",
        })
    payload["_manifest"] = manifest
    payload["_scope"] = scope
    payload["_topic_id"] = topic_id
    rp = _receipt_path(topic_id, scope)
    _atomic_write_json(rp, payload)
    return rp


def read_receipt(topic_id: int, scope: str) -> Optional[Dict[str, Any]]:
    rp = _receipt_path(topic_id, scope)
    if not rp.exists():
        return None
    try:
        with open(rp, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def receipt_is_valid(topic_id: int, scope: str) -> bool:
    """영수증 존재 + 주제 일치 + 산출물 실존 검증."""
    r = read_receipt(topic_id, scope)
    if not r:
        return False
    if r.get("_topic_id") != topic_id:
        return False
    for m in r.get("_manifest", []):
        if not m.get("exists"):
            return False
        if not Path(m["path"]).exists():
            return False
    return True


# ============================================================================
# [3] 얇은 어댑터 진입점
# ============================================================================
def _run_single(producer: AuraCardnewsProducer, topic_id: int, slide_num: int,
                fashion_id: Optional[int]) -> int:
    scope = f"slide_{slide_num}"
    if receipt_is_valid(topic_id, scope):
        r = read_receipt(topic_id, scope)
        logger.info(f"♻️ [멱등] 주제 {topic_id} 슬라이드 {slide_num} 영수증 존재 — 재생성 생략")
        print("OUTPUT_DIR=" + r["output_dir"])
        print(f"SLIDE_{slide_num}=" + r["slide_path"])
        return 0

    logger.info(f"🤖 [Aura Cardnews Bot] {topic_id}번 주제 카드뉴스 {slide_num}번 카드 자율 생성 가동 (착장={fashion_id or '기본'})...")
    raw = producer.produce_slide(slide_num=slide_num, topic_id=topic_id, fashion_id=fashion_id)
    result = validate_slide_result(raw, topic_id, slide_num)
    write_receipt(topic_id, scope, result)

    logger.info("================================================================================")
    logger.info(f"🎉 [성공] {topic_id}번 주제 {slide_num}번 카드 산출물이 바탕화면에 생성되었습니다!")
    logger.info(f"📂 저장 경로: {result.output_dir}")
    logger.info(f"🖼️ 카드 이미지: {result.slide_path}")
    logger.info("================================================================================")
    print("OUTPUT_DIR=" + result.output_dir)
    print(f"SLIDE_{slide_num}=" + result.slide_path)
    return 0


def _run_full(producer: AuraCardnewsProducer, topic_id: int,
              fashion_id: Optional[int]) -> int:
    scope = "full"
    if receipt_is_valid(topic_id, scope):
        r = read_receipt(topic_id, scope)
        logger.info(f"♻️ [멱등] 주제 {topic_id} 풀세트 영수증 존재 — 재생성 생략")
        print("OUTPUT_DIR=" + r["output_dir"])
        return 0

    logger.info(f"🤖 [Aura Cardnews Bot] {topic_id}번 주제 5장 풀세트 카드뉴스 원스톱 자율 생성 가동 (착장={fashion_id or '기본'})...")
    raw = producer.produce_cardnews(topic_id=topic_id, fashion_id=fashion_id)
    result = validate_cardnews_result(raw, topic_id)
    write_receipt(topic_id, scope, result)

    logger.info("================================================================================")
    logger.info(f"🎉 [성공] {topic_id}번 주제 5장 풀세트 카드뉴스가 바탕화면에 완벽하게 완성되었습니다!")
    logger.info(f"📂 저장 경로: {result.output_dir}")
    logger.info(f"📊 총 슬라이드 수: {result.total_slides}장")
    for i, p in enumerate(result.slide_paths, 1):
        logger.info(f"   [{i}/{result.total_slides}] {p}")
    logger.info(f"📝 SNS 포스팅 가이드: {result.guide_path}")
    logger.info(f"📋 메타데이터: {result.metadata_path}")
    logger.info("================================================================================")
    print("OUTPUT_DIR=" + result.output_dir)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Aura 5장 카드뉴스 봇 무인 자율 구동 진입점")
    parser.add_argument("slide", nargs="?", default="1", help="생성할 슬라이드 번호 (1~5) 또는 'all' (전체 풀세트)")
    parser.add_argument("--topic", "-t", type=int, default=1, help="주제 ID")
    parser.add_argument("--fashion", "-f", type=int, default=None, help="소개팅 착장 프리셋 ID (1~10)")
    args, _unknown = parser.parse_known_args()

    producer = AuraCardnewsProducer()
    try:
        if args.slide.isdigit():
            return _run_single(producer, args.topic, int(args.slide), args.fashion)
        return _run_full(producer, args.topic, args.fashion)
    except ContractViolation as e:
        logger.error(f"❌ [계약 위반] {e}")
        return 2
    except Exception as e:
        logger.exception(f"❌ [실행 실패] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())