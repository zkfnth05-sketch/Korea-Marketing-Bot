# -*- coding: utf-8 -*-
"""
brands/insurance/insurance_drama_pipeline.py
===================================================================================================
🛡️ [InsuranceDramaPipeline] — 보험 리밸런스 전용 일일 숏드라마 독립 레고 블록
---------------------------------------------------------------------------------------------------
[대표님 절대 수칙]
  1. 100% 완전 독립 레고 블록
     - 기존 보험 숏폼/카드뉴스 파이프라인(insurance_omni_shorts_pilot.py,
       insurance_shorts_pipeline.py, insurance_cardnews_*.py)에 단 1줄도 간섭하지 않는다.
     - 오직 modules.drama_engine.drama_pipeline_facade.DramaPipelineFacade('insurance') 만 연동한다.
  2. 브랜드 공식 규격 엄수 (절대 불변)
     - 공식 명칭   : '보험 리밸런스'
     - 공식 검색어 : '보험 리밸런스'  (띄어쓰기 필수)
     - 랜딩 URL    : https://insure-rebalance.vercel.app/
  3. 테마 3종 (보험금 미지급 분쟁 / 부모님 갱신형 보험 폭탄 / 사회초년생 호갱 탈출 참교육)
  4. 산출물 경로
     - C:/Users/zkfnt/Desktop/한국 숏폼_산출물/Insurance/insurance_drama_{YYYYMMDD}.mp4

[🎬 4컷 시네마틱 드라마 구조 — 총 20초]
  · Cut 1 (도파민 훅, 3초)   : 보험금 미지급 / 보험료 폭탄 / 호갱 상황 발생
  · Cut 2 (갈등 고조, 6초)   : 주인공 2인 핑퐁 대화 티키타카
  · Cut 3 (반전 솔루션, 7초) : '보험 리밸런스' AI 진단 극적 등장
  · Cut 4 (여운 & CTA, 4초)  : 펀치라인 + 네이버 공식 검색어 '보험 리밸런스' 유도

[🛡️ 예외 은폐 금지 원칙]
  · try-except pass 전면 금지.
  · 모든 예외는 logger.error(..., exc_info=True) 로 스택트레이스 전량 기록 후 재발생(raise).
  · 브랜드 규격 위반 / 날짜 형식 오류 / 시나리오 유효성 검증 실패 / 산출물 부재 시
    ValueError · RuntimeError · FileNotFoundError 를 명시적으로 발생시킨다.
===================================================================================================
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# ==============================================================================
# 🖥️ [Windows 콘솔 UTF-8 강제] 한글 로그 깨짐 방지
# ==============================================================================
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError) as _enc_exc:  # pragma: no cover
        logging.getLogger("InsuranceDramaPipeline").warning(
            f"⚠️ [InsuranceDramaPipeline] 콘솔 UTF-8 재설정 실패(무해): {_enc_exc}"
        )

# ==============================================================================
# 📦 [프로젝트 루트 sys.path 보정] 단독 실행 및 패키지 임포트 양립
# ==============================================================================
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger("InsuranceDramaPipeline")


# ==============================================================================
# 🏛️ [메인 클래스] InsuranceDramaPipeline
# ==============================================================================
class InsuranceDramaPipeline:
    """
    🛡️ 보험 리밸런스 전용 일일 숏드라마 독립 레고 블록.

    - 기존 보험 숏폼/카드뉴스 파이프라인과 완전 분리된 독립 모듈.
    - modules.drama_engine.drama_pipeline_facade.DramaPipelineFacade('insurance') 단일 연동.
    - produce() 단일 진입점으로 4컷 시네마틱 숏드라마 1편을 무인 생산한다.
    """

    # ── 브랜드 식별자 ────────────────────────────────────────────────────────
    BRAND: str = "insurance"
    BRAND_FOLDER_NAME: str = "Insurance"

    # ── 브랜드 공식 규격 (절대 불변 상수) ────────────────────────────────────
    BRAND_OFFICIAL_NAME: str = "보험 리밸런스"
    OFFICIAL_SEARCH_KEYWORD: str = "보험 리밸런스"  # 띄어쓰기 필수
    LANDING_URL: str = "https://insure-rebalance.vercel.app/"

    # ── 보험 전용 3대 테마 (보험금 미지급 / 갱신형 폭탄 / 사회초년생 참교육) ──
    CORE_THEMES: List[str] = [
        "보험금 미지급 분쟁",
        "부모님 갱신형 보험 폭탄",
        "사회초년생 호갱 탈출 참교육",
    ]

    # ── 4컷 시네마틱 타임라인 (3 + 6 + 7 + 4 = 20초) ─────────────────────────
    CUT_DURATIONS: Dict[str, int] = {"cut1": 3, "cut2": 6, "cut3": 7, "cut4": 4}
    TOTAL_DURATION_SEC: int = sum(CUT_DURATIONS.values())  # 20

    # ── 산출물 루트 ──────────────────────────────────────────────────────────
    OUTPUT_ROOT: Path = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물")

    # ── 파일명 규격 ──────────────────────────────────────────────────────────
    FILE_PREFIX: str = "insurance_drama"

    def __init__(self, output_root: Optional[Path] = None) -> None:
        """
        Args:
            output_root: 산출물 루트 경로 (기본: C:/Users/zkfnt/Desktop/한국 숏폼_산출물)
        """
        self.output_root = Path(output_root) if output_root else self.OUTPUT_ROOT
        self.output_dir = self.output_root / self.BRAND_FOLDER_NAME
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 🏛️ [파사드 연동] 보험 브랜드 전용 파사드 인스턴스 (지연 임포트)
        self._facade = None

        logger.info(
            f"🛡️ [InsuranceDramaPipeline] 초기화 완료 | "
            f"브랜드='{self.BRAND_OFFICIAL_NAME}' | 검색어='{self.OFFICIAL_SEARCH_KEYWORD}' | "
            f"산출물={self.output_dir}"
        )

    # ==========================================================================
    # 🏛️ [파사드 지연 로딩] 무거운 의존성(google-genai, PIL, ffmpeg) 로드 시점 분리
    # ==========================================================================
    @property
    def facade(self) -> Any:
        """DramaPipelineFacade('insurance') 지연 생성 및 캐싱"""
        if self._facade is None:
            try:
                from modules.drama_engine.drama_pipeline_facade import DramaPipelineFacade
            except ImportError as exc:
                logger.error(
                    f"🚨 [InsuranceDramaPipeline] DramaPipelineFacade 임포트 실패: {exc}",
                    exc_info=True,
                )
                raise

            try:
                self._facade = DramaPipelineFacade(self.BRAND)
            except ValueError as exc:
                logger.error(
                    f"🚨 [InsuranceDramaPipeline] 파사드 생성 실패(브랜드 미지원): {exc}",
                    exc_info=True,
                )
                raise

            logger.info("🏛️ [InsuranceDramaPipeline] DramaPipelineFacade('insurance') 연동 완료")

        return self._facade

    # ==========================================================================
    # 🧾 [날짜 정규화] YYYY-MM-DD / YYYYMMDD / None(오늘) 모두 허용
    # ==========================================================================
    @staticmethod
    def _normalize_date(date_str: Optional[str]) -> str:
        """
        날짜 문자열을 'YYYY-MM-DD' 표준형으로 정규화한다.

        Args:
            date_str: 'YYYY-MM-DD' | 'YYYYMMDD' | None(오늘)

        Returns:
            str: 'YYYY-MM-DD'

        Raises:
            ValueError: 날짜 형식이 규격에 맞지 않는 경우
        """
        if date_str is None or str(date_str).strip() == "":
            return date.today().isoformat()

        raw = str(date_str).strip()

        # 1) YYYY-MM-DD
        try:
            parsed = datetime.strptime(raw, "%Y-%m-%d")
            return parsed.date().isoformat()
        except ValueError:
            logger.debug(f"🔎 [InsuranceDramaPipeline] '%s' 는 YYYY-MM-DD 형식이 아님 → YYYYMMDD 시도", raw)

        # 2) YYYYMMDD
        try:
            parsed = datetime.strptime(raw, "%Y%m%d")
            return parsed.date().isoformat()
        except ValueError as exc:
            logger.error(
                f"🚨 [InsuranceDramaPipeline] 날짜 형식 오류: '{raw}' "
                f"(허용: YYYY-MM-DD 또는 YYYYMMDD)",
                exc_info=True,
            )
            raise ValueError(
                f"❌ [InsuranceDramaPipeline] 날짜 형식 오류: '{raw}'. "
                f"'YYYY-MM-DD' 또는 'YYYYMMDD' 형식만 허용됩니다."
            ) from exc

    # ==========================================================================
    # 📁 [산출물 경로 산출] insurance_drama_{YYYYMMDD}.mp4
    # ==========================================================================
    def get_output_path(self, date_str: Optional[str] = None) -> Path:
        """
        산출물 MP4 절대 경로를 반환한다.

        Args:
            date_str: 'YYYY-MM-DD' | 'YYYYMMDD' | None(오늘)

        Returns:
            Path: C:/Users/zkfnt/Desktop/한국 숏폼_산출물/Insurance/insurance_drama_{YYYYMMDD}.mp4
        """
        normalized = self._normalize_date(date_str)
        yyyymmdd = normalized.replace("-", "")
        return self.output_dir / f"{self.FILE_PREFIX}_{yyyymmdd}.mp4"

    # ==========================================================================
    # 🔍 [시나리오 유효성 검증] 브랜드 공식 규격 위반 시 ValueError 명시 발생
    # ==========================================================================
    def _validate_scenario(self, scenario: Dict[str, Any]) -> None:
        """
        4컷 시나리오가 보험 리밸런스 공식 규격을 100% 준수하는지 전수 검증한다.

        Raises:
            ValueError: 규격 위반 항목이 하나라도 발견된 경우
        """
        if not isinstance(scenario, dict):
            raise ValueError(
                f"❌ [InsuranceDramaPipeline] 시나리오 타입 오류: dict 기대, 실제 {type(scenario).__name__}"
            )

        # 1) 브랜드 식별자 검증
        scenario_brand = str(scenario.get("brand", "")).lower().strip()
        if scenario_brand != self.BRAND:
            raise ValueError(
                f"❌ [InsuranceDramaPipeline] 브랜드 불일치: '{scenario_brand}' (기대: '{self.BRAND}')"
            )

        # 2) 공식 검색어 검증 (띄어쓰기 필수)
        official_keyword = str(scenario.get("official_search_keyword", "")).strip()
        if official_keyword != self.OFFICIAL_SEARCH_KEYWORD:
            raise ValueError(
                f"❌ [InsuranceDramaPipeline] 공식 검색어 규격 위반: '{official_keyword}' "
                f"(기대: '{self.OFFICIAL_SEARCH_KEYWORD}' — 띄어쓰기 필수)"
            )

        # 3) 4컷 구조 검증
        cuts = scenario.get("cuts")
        if not isinstance(cuts, list) or len(cuts) != 4:
            raise ValueError(
                f"❌ [InsuranceDramaPipeline] 4컷 구조 위반: cuts 개수 {len(cuts) if isinstance(cuts, list) else 'N/A'} (기대: 4)"
            )

        expected_cut_ids = ["cut1", "cut2", "cut3", "cut4"]
        for idx, cut in enumerate(cuts):
            if not isinstance(cut, dict):
                raise ValueError(
                    f"❌ [InsuranceDramaPipeline] 컷 #{idx + 1} 타입 오류: dict 기대, 실제 {type(cut).__name__}"
                )
            cut_id = str(cut.get("cut_id", ""))
            if cut_id != expected_cut_ids[idx]:
                raise ValueError(
                    f"❌ [InsuranceDramaPipeline] 컷 ID 순서 위반: {idx + 1}번째 '{cut_id}' (기대: '{expected_cut_ids[idx]}')"
                )
            speech = str(cut.get("speech", "")).strip()
            if not speech:
                raise ValueError(
                    f"❌ [InsuranceDramaPipeline] 컷 '{cut_id}' 대사(speech) 누락"
                )
            expected_dur = self.CUT_DURATIONS[cut_id]
            actual_dur = cut.get("duration_sec")
            if actual_dur != expected_dur:
                raise ValueError(
                    f"❌ [InsuranceDramaPipeline] 컷 '{cut_id}' 길이 규격 위반: {actual_dur}초 (기대: {expected_dur}초)"
                )

        # 4) 총 길이 20초 검증
        total_dur = scenario.get("total_duration_sec")
        if total_dur != self.TOTAL_DURATION_SEC:
            raise ValueError(
                f"❌ [InsuranceDramaPipeline] 총 길이 규격 위반: {total_dur}초 (기대: {self.TOTAL_DURATION_SEC}초)"
            )

        # 5) CTA 내 공식 검색어 포함 검증 (네이버 검색 유도 필수)
        speech_cta = str(scenario.get("speech_cta", ""))
        if self.OFFICIAL_SEARCH_KEYWORD not in speech_cta:
            raise ValueError(
                f"❌ [InsuranceDramaPipeline] CTA에 공식 검색어 '{self.OFFICIAL_SEARCH_KEYWORD}' 누락: '{speech_cta}'"
            )

        # 6) 6키 평탄화 호환 검증 (기존 렌더러 직결)
        required_flat_keys = (
            "speech_hook",
            "speech_part1",
            "speech_part2",
            "speech_app",
            "speech_cta",
            "full_speech",
        )
        missing_keys = [k for k in required_flat_keys if not str(scenario.get(k, "")).strip()]
        if missing_keys:
            raise ValueError(
                f"❌ [InsuranceDramaPipeline] 6키 평탄화 누락: {missing_keys}"
            )

        logger.info(
            f"✅ [InsuranceDramaPipeline] 시나리오 규격 검증 100% 합격 | "
            f"테마='{scenario.get('theme')}' | 총 {self.TOTAL_DURATION_SEC}초 | "
            f"공식 검색어='{official_keyword}'"
        )

    # ==========================================================================
    # 🎬 [메인 진입점] produce()
    # ==========================================================================
    def produce(
        self,
        date_str: Optional[str] = None,
        auto_publish: bool = True,
    ) -> Dict[str, Any]:
        """
        보험 리밸런스 일일 숏드라마 1편을 무인 생산한다.

        Args:
            date_str: 'YYYY-MM-DD' | 'YYYYMMDD' | None(오늘)
            auto_publish: True 면 생산 직후 SNS 자동 송출 훅까지 실행

        Returns:
            Dict[str, Any]: 생산 결과 매니페스트
                {
                    "status": "success",
                    "brand": "insurance",
                    "brand_official_name": "보험 리밸런스",
                    "official_search_keyword": "보험 리밸런스",
                    "landing_url": "https://insure-rebalance.vercel.app/",
                    "date": "YYYY-MM-DD",
                    "theme": "...",
                    "location": "...",
                    "output_mp4": "...",
                    "output_exists": True,
                    "output_size_bytes": 12345678,
                    "duration_sec": 20,
                    "auto_publish": True,
                    "manifest_path": "...",
                    "facade_manifest": {...}
                }

        Raises:
            ValueError: 날짜 형식 오류 / 시나리오 규격 위반
            RuntimeError: 파사드 생산 실패
            FileNotFoundError: 산출물 MP4 미생성
        """
        normalized_date = self._normalize_date(date_str)
        yyyymmdd = normalized_date.replace("-", "")
        expected_mp4 = self.output_dir / f"{self.FILE_PREFIX}_{yyyymmdd}.mp4"

        logger.info("=" * 88)
        logger.info(
            f"🎬 [InsuranceDramaPipeline] 보험 리밸런스 일일 숏드라마 생산 착수 | "
            f"날짜={normalized_date} | auto_publish={auto_publish}"
        )
        logger.info(f"🎯 공식 명칭='{self.BRAND_OFFICIAL_NAME}' | 공식 검색어='{self.OFFICIAL_SEARCH_KEYWORD}'")
        logger.info(f"🔗 랜딩 URL={self.LANDING_URL}")
        logger.info(f"📁 산출물 예정 경로={expected_mp4}")
        logger.info("=" * 88)

        # ── 1단계: 파사드 연동 및 4컷 시나리오 사전 검증 ──────────────────────
        try:
            scenario_preview = self.facade.scenario_director.get_daily_drama_scenario(
                brand=self.BRAND,
                date_str=normalized_date,
            )
        except ValueError as exc:
            logger.error(
                f"🚨 [InsuranceDramaPipeline] 시나리오 생성 실패: {exc}",
                exc_info=True,
            )
            raise

        self._validate_scenario(scenario_preview)

        # ── 2단계: 파사드 일일 숏드라마 생산 (4컷 렌더 + 핑퐁 더빙 + 조립) ────
        try:
            facade_manifest = self.facade.produce_daily_drama(
                date_str=normalized_date,
                auto_publish=auto_publish,
            )
        except (RuntimeError, ValueError, FileNotFoundError) as exc:
            logger.error(
                f"🚨 [InsuranceDramaPipeline] 파사드 생산 실패: {exc}",
                exc_info=True,
            )
            raise RuntimeError(
                f"❌ [InsuranceDramaPipeline] 보험 리밸런스 숏드라마 생산 실패: {exc}"
            ) from exc

        if not isinstance(facade_manifest, dict):
            raise RuntimeError(
                f"❌ [InsuranceDramaPipeline] 파사드 반환 타입 오류: dict 기대, 실제 {type(facade_manifest).__name__}"
            )

        # ── 3단계: 산출물 실물 검증 (파일 존재 + 용량) ────────────────────────
        produced_mp4 = Path(str(facade_manifest.get("output_mp4", "")))
        if not produced_mp4.exists():
            logger.error(
                f"🚨 [InsuranceDramaPipeline] 산출물 MP4 미생성: {produced_mp4}",
                exc_info=True,
            )
            raise FileNotFoundError(
                f"❌ [InsuranceDramaPipeline] 산출물 MP4가 생성되지 않았습니다: {produced_mp4}"
            )

        output_size = produced_mp4.stat().st_size
        if output_size <= 0:
            logger.error(
                f"🚨 [InsuranceDramaPipeline] 산출물 MP4 용량 0바이트: {produced_mp4}",
                exc_info=True,
            )
            raise RuntimeError(
                f"❌ [InsuranceDramaPipeline] 산출물 MP4가 0바이트입니다: {produced_mp4}"
            )

        # ── 4단계: 보험 전용 통합 매니페스트 저장 ─────────────────────────────
        manifest_path = self.output_dir / f"{self.FILE_PREFIX}_{yyyymmdd}_pipeline_manifest.json"
        result: Dict[str, Any] = {
            "status": "success",
            "brand": self.BRAND,
            "brand_official_name": self.BRAND_OFFICIAL_NAME,
            "official_search_keyword": self.OFFICIAL_SEARCH_KEYWORD,
            "landing_url": self.LANDING_URL,
            "date": normalized_date,
            "theme": facade_manifest.get("theme", ""),
            "location": facade_manifest.get("location", ""),
            "output_mp4": str(produced_mp4),
            "output_exists": True,
            "output_size_bytes": output_size,
            "duration_sec": self.TOTAL_DURATION_SEC,
            "auto_publish": bool(auto_publish),
            "manifest_path": str(manifest_path),
            "facade_manifest": facade_manifest,
        }

        try:
            manifest_path.write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError as exc:
            logger.error(
                f"🚨 [InsuranceDramaPipeline] 매니페스트 저장 실패: {manifest_path} ({exc})",
                exc_info=True,
            )
            raise

        logger.info(
            f"🎉 [InsuranceDramaPipeline] 보험 리밸런스 숏드라마 생산 완결 | "
            f"{produced_mp4.name} ({output_size // 1024}KB, {self.TOTAL_DURATION_SEC}초)"
        )
        logger.info(f"🧾 통합 매니페스트 저장: {manifest_path}")
        logger.info("=" * 88)

        return result

    # ==========================================================================
    # 🧾 [편의 메서드] 브랜드 규격 요약
    # ==========================================================================
    def get_brand_spec(self) -> Dict[str, Any]:
        """보험 리밸런스 공식 규격 요약을 반환한다."""
        return {
            "brand": self.BRAND,
            "brand_official_name": self.BRAND_OFFICIAL_NAME,
            "official_search_keyword": self.OFFICIAL_SEARCH_KEYWORD,
            "landing_url": self.LANDING_URL,
            "core_themes": list(self.CORE_THEMES),
            "cut_durations": dict(self.CUT_DURATIONS),
            "total_duration_sec": self.TOTAL_DURATION_SEC,
            "output_dir": str(self.output_dir),
            "file_prefix": self.FILE_PREFIX,
        }


# ==============================================================================
# 🧪 [테스트 블록] 단독 실행 검증
# ==============================================================================
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    print("=" * 88)
    print("🛡️ [InsuranceDramaPipeline] 보험 리밸런스 전용 일일 숏드라마 독립 레고 블록 자체 점검")
    print("=" * 88)

    pipeline = InsuranceDramaPipeline()

    # 1) 브랜드 공식 규격 출력
    spec = pipeline.get_brand_spec()
    print("\n📋 [브랜드 공식 규격]")
    for key, value in spec.items():
        print(f"  · {key:<26}: {value}")

    # 2) 날짜 정규화 및 산출물 경로 검증
    print("\n📁 [산출물 경로 검증]")
    for sample in (None, "2026-10-17", "20261017"):
        try:
            out_path = pipeline.get_output_path(sample)
            print(f"  · 입력 {str(sample):<12} → {out_path}")
        except ValueError as exc:
            print(f"  · 입력 {str(sample):<12} → ❌ {exc}")

    # 3) 잘못된 날짜 형식 예외 검증
    print("\n🚨 [날짜 형식 예외 검증]")
    try:
        pipeline.get_output_path("2026/10/17")
        print("  · ❌ 예외가 발생하지 않았습니다 (규격 위반)")
    except ValueError as exc:
        print(f"  · ✅ ValueError 정상 발생: {exc}")

    # 4) 시나리오 규격 사전 검증 (실제 렌더링 없이 시나리오만 확인)
    print("\n🔍 [4컷 시나리오 규격 사전 검증]")
    try:
        scenario = pipeline.facade.scenario_director.get_daily_drama_scenario(
            brand=pipeline.BRAND,
            date_str=None,
        )
        pipeline._validate_scenario(scenario)
        print(f"  · ✅ 테마: {scenario.get('theme')}")
        print(f"  · ✅ 로케이션: {scenario.get('location')}")
        print(f"  · ✅ 공식 검색어: {scenario.get('official_search_keyword')}")
        print(f"  · ✅ 총 길이: {scenario.get('total_duration_sec')}초")
        print(f"  · ✅ CTA: {scenario.get('speech_cta')}")
    except (ValueError, ImportError) as exc:
        logger.error(f"🚨 [자체 점검] 시나리오 검증 실패: {exc}", exc_info=True)
        print(f"  · ❌ 시나리오 검증 실패: {exc}")

    print("\n" + "=" * 88)
    print("✅ [InsuranceDramaPipeline] 자체 점검 완료")
    print("   실제 영상 생산은 produce(date_str=None, auto_publish=True) 를 호출하십시오.")
    print("=" * 88)
