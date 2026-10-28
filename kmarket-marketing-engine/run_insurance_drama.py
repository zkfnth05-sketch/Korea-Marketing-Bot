#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
🛡️ run_insurance_drama.py — 보험 리밸런스 일일 숏폼 드라마 원클릭 독립 러너
================================================================================

[역할]
  · 보험 리밸런스 일일 숏폼 드라마 1편을 무인 생산하는 독립 실행 스크립트.
  · brands.insurance.insurance_drama_pipeline.InsuranceDramaPipeline 인스턴스를
    생성하여 파사드(4컷 렌더 + 핑퐁 더빙 + 조립) 생산을 단일 명령으로 완결한다.

[사용 예시]
  python run_insurance_drama.py
  python run_insurance_drama.py --date 2026-10-26
  python run_insurance_drama.py -d 20261026 --no-publish
  python run_insurance_drama.py --no-publish --episode 7

[대표님 절대 수칙]
  · 공식 명칭   : 보험 리밸런스
  · 공식 검색어 : 보험 리밸런스   (띄어쓰기 필수 — 절대 붙여쓰기 금지)
  · 랜딩 URL    : https://insure-rebalance.vercel.app/

[설계 원칙]
  · try-except-pass 전면 금지 — 예외는 반드시 logger.error(exc_info=True) 후 sys.exit(1).
  · Windows 콘솔 UTF-8 강제 (cp949 콘솔에서 이모지 출력 시 UnicodeEncodeError 즉사 방지).
  · --episode 는 정수/문자열 모두 허용하되, 파이프라인 계약(date_str, auto_publish)을
    오염시키지 않도록 '테마 식별자'로만 해석하여 로그·매니페스트에 기록한다.
================================================================================
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# ──────────────────────────────────────────────────────────────────────────────
# [0] 경로 부트스트랩 — 어느 작업 디렉터리에서 실행해도 프로젝트 루트를 sys.path 최우선에 둔다.
#     (kmarket-marketing-engine 을 cwd 로 두지 않고 바탕화면에서 직접 실행하는 경우 대비)
# ──────────────────────────────────────────────────────────────────────────────
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))


# ──────────────────────────────────────────────────────────────────────────────
# [1] 콘솔 UTF-8 강제 — Windows(cp949) 콘솔에서 이모지/한글 출력 즉사 방지
# ──────────────────────────────────────────────────────────────────────────────
def _force_utf8_console() -> None:
    """Windows 콘솔(stdout/stderr)을 UTF-8 로 강제 재구성한다.

    · sys.platform == 'win32' 에서만 동작한다.
    · reconfigure() 미지원(구형 파이썬/특수 스트림) 시에도 절대 예외를 삼키지 않고
      경고 로그만 남긴 뒤 진행한다 — 출력 인코딩 실패로 생산 자체를 중단시키지 않기 위함.
    """
    if sys.platform != "win32":
        return

    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None:
            continue
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            logging.getLogger("InsuranceDramaRunner").warning(
                "⚠️ %s 스트림이 reconfigure() 를 지원하지 않습니다 — UTF-8 강제 생략",
                stream_name,
            )
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError) as exc:
            logging.getLogger("InsuranceDramaRunner").warning(
                "⚠️ %s UTF-8 재구성 실패: %s", stream_name, exc
            )


# ──────────────────────────────────────────────────────────────────────────────
# [2] 로거 구성 — "InsuranceDramaRunner"
# ──────────────────────────────────────────────────────────────────────────────
LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _build_logger() -> logging.Logger:
    """InsuranceDramaRunner 로거를 구성한다(중복 핸들러 부착 방지)."""
    logger = logging.getLogger("InsuranceDramaRunner")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
        logger.addHandler(handler)

    return logger


# ──────────────────────────────────────────────────────────────────────────────
# [3] CLI 인자 파서
# ──────────────────────────────────────────────────────────────────────────────
def _build_arg_parser() -> argparse.ArgumentParser:
    """명령행 인자 파서를 구성한다.

    · --date / -d      : 대상 날짜 (YYYY-MM-DD 또는 YYYYMMDD, 미지정 시 오늘)
    · --no-publish     : 야간 렌더링 전용 (SNS 송출 없이 파일만 생성)
    · --episode / -e   : 에피소드/테마 식별자 (정수 또는 문자열)
    """
    parser = argparse.ArgumentParser(
        prog="run_insurance_drama.py",
        description=(
            "🛡️ 보험 리밸런스 일일 숏폼 드라마 원클릭 독립 러너 "
            "(공식 검색어: 보험 리밸런스 / https://insure-rebalance.vercel.app/)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "사용 예시:\n"
            "  python run_insurance_drama.py\n"
            "  python run_insurance_drama.py --date 2026-10-26\n"
            "  python run_insurance_drama.py -d 20261026 --no-publish\n"
            "  python run_insurance_drama.py --no-publish --episode 7\n"
        ),
    )

    parser.add_argument(
        "--date",
        "-d",
        dest="date",
        type=str,
        default=None,
        metavar="YYYY-MM-DD",
        help="대상 날짜 (YYYY-MM-DD 또는 YYYYMMDD). 미지정 시 오늘 날짜로 자동 결정.",
    )

    parser.add_argument(
        "--no-publish",
        dest="no_publish",
        action="store_true",
        help="야간 렌더링 전용 모드 — SNS 송출 없이 MP4 파일만 생성 (auto_publish=False).",
    )

    parser.add_argument(
        "--episode",
        "-e",
        dest="episode",
        type=str,
        default=None,
        metavar="EPISODE",
        help="에피소드/테마 식별자 (정수 또는 문자열). 로그·매니페스트 기록용.",
    )

    return parser


# ──────────────────────────────────────────────────────────────────────────────
# [4] 메인 실행부
# ──────────────────────────────────────────────────────────────────────────────
def main(argv: Optional[list] = None) -> int:
    """보험 리밸런스 일일 숏드라마 생산을 실행하고 종료 코드를 반환한다."""
    _force_utf8_console()
    logger = _build_logger()

    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    # --no-publish → auto_publish=False (야간 렌더링 전용)
    auto_publish: bool = not bool(args.no_publish)

    # --episode 는 정수/문자열 모두 허용 — 표기만 정규화하여 로그에 남긴다.
    episode_label: Optional[str] = None
    if args.episode is not None and str(args.episode).strip() != "":
        raw_episode = str(args.episode).strip()
        try:
            episode_label = str(int(raw_episode))
        except ValueError:
            episode_label = raw_episode

    logger.info("=" * 88)
    logger.info("🛡️ [InsuranceDramaRunner] 보험 리밸런스 일일 숏폼 드라마 생산 착수")
    logger.info("🎯 공식 명칭='보험 리밸런스' | 공식 검색어='보험 리밸런스'")
    logger.info("🔗 랜딩 URL=https://insure-rebalance.vercel.app/")
    logger.info(
        "⚙️ 실행 옵션 | date=%s | auto_publish=%s | episode=%s",
        args.date if args.date else "오늘(자동)",
        auto_publish,
        episode_label if episode_label else "미지정",
    )
    logger.info("=" * 88)

    # ── 파이프라인 임포트 & 생산 실행 (최신 5신 무인 드라마 파이프라인 직결) ──
    try:
        from datetime import datetime
        from brands.insurance.insurance_drama_5scenes_pipeline import (
            PipelineConfig,
            allocate_output_dir,
            build_default_5scenes_spec,
            select_image_adapter,
            select_tts_adapter,
            select_video_adapter,
            PipelineOrchestrator,
            SpecValidator,
            DEFAULT_CONTEXT_AGE_MIN,
            DEFAULT_CONVERSATION_ID,
        )
    except ImportError as exc:
        logger.error(
            "🚨 [InsuranceDramaRunner] InsuranceDrama5ScenesPipeline 임포트 실패: %s",
            exc,
            exc_info=True,
        )
        return 1

    try:
        scenes = build_default_5scenes_spec()
        SpecValidator.validate_all(scenes, DEFAULT_CONTEXT_AGE_MIN, DEFAULT_CONVERSATION_ID)
        output_root = allocate_output_dir()
        cfg = PipelineConfig(output_root=output_root)
        image = select_image_adapter(cfg)
        tts = select_tts_adapter(cfg)
        video = select_video_adapter(cfg)
        orch = PipelineOrchestrator(cfg, image, tts, video)
        pipeline_res = orch.run(scenes)

        final_vid = pipeline_res.get("final_video")
        if not final_vid or not Path(final_vid).exists():
            raise RuntimeError(
                f"최종 비디오 생성 실패: ok={pipeline_res.get('ok')}, failed={pipeline_res.get('failed')}"
            )

        result: Dict[str, Any] = {
            "date": args.date or datetime.now().strftime("%Y-%m-%d"),
            "theme": scenes[0].topic if scenes else "보험 리밸런스 드라마",
            "location": scenes[0].location_en if scenes else "",
            "episode_dir": str(output_root),
            "output_mp4": str(final_vid),
            "output_size_bytes": Path(final_vid).stat().st_size,
            "duration_sec": round(sum(s.duration_sec for s in scenes), 2),
            "manifest_path": str(output_root / "manifest.json"),
        }
    except Exception as exc:
        logger.error(
            "🚨 [InsuranceDramaRunner] 보험 리밸런스 숏드라마 생산 실패: %s",
            exc,
            exc_info=True,
        )
        return 1

    # ── 반환 매니페스트 검증 (dict 계약 + output_mp4 실재) ──────────────────────
    if not isinstance(result, dict):
        logger.error(
            "🚨 [InsuranceDramaRunner] produce() 반환 타입 오류: dict 기대, 실제 %s",
            type(result).__name__,
            exc_info=True,
        )
        return 1

    out_mp4 = str(result.get("output_mp4", "") or "").strip()
    if not out_mp4:
        logger.error(
            "🚨 [InsuranceDramaRunner] produce() 반환값에 'output_mp4' 키가 없습니다: %s",
            list(result.keys()),
            exc_info=True,
        )
        return 1

    out_path = Path(out_mp4)
    if not out_path.exists():
        logger.error(
            "🚨 [InsuranceDramaRunner] 산출물 MP4 실물 부재: %s", out_mp4, exc_info=True
        )
        return 1

    # ── 완결 보고 ───────────────────────────────────────────────────────────────
    logger.info("=" * 88)
    logger.info("✅ [InsuranceDramaRunner] 생산 매니페스트 요약")
    logger.info("   · 날짜        : %s", result.get("date", ""))
    logger.info("   · 테마        : %s", result.get("theme", ""))
    logger.info("   · 장소        : %s", result.get("location", ""))
    logger.info("   · 에피소드    : %s", episode_label if episode_label else "미지정")
    logger.info("   · 용량        : %s bytes", result.get("output_size_bytes", ""))
    logger.info("   · 길이        : %s 초", result.get("duration_sec", ""))
    logger.info("   · SNS 송출    : %s", "실행" if auto_publish else "생략(--no-publish)")
    logger.info("   · 매니페스트  : %s", result.get("manifest_path", ""))
    logger.info("=" * 88)

    print(f"\n🎉 [생산 완결] 완제품 MP4: {out_mp4}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
