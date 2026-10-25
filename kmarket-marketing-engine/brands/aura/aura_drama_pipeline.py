# -*- coding: utf-8 -*-
"""
brands/aura/aura_drama_pipeline.py
===================================================================================================
💜 [AuraDramaPipeline] — Aura AI 데이팅 전용 일일 숏드라마 독립 레고 블록 (정식 완성형)
---------------------------------------------------------------------------------------------------
[대표님 절대 수칙]
  1. 100% 완전 독립 레고 블록
     - 기존 Aura 숏폼/카드뉴스 파이프라인(run_aura_shorts.py, aura_omni_shorts_pilot.py,
       aura_shorts_pipeline.py, aura_cardnews_*.py 등)에 단 1줄도 간섭하지 않는다.
     - 오직 modules.drama_engine.drama_pipeline_facade.DramaPipelineFacade('aura') 만 연동한다.
  2. 브랜드 공식 규격 엄수 (절대 불변)
     - 공식 명칭   : 'Aura AI 데이팅'
     - 공식 검색어 : '아우라AI데이팅'  (붙여쓰기 필수, 띄어쓰기 금지)
     - 랜딩 URL    : https://aura-ai-dating.vercel.app/
  3. 테마 3종
     - 소개팅 최악의 빌런 vs 긴급 탈출
     - 자만추 꿈꾸지만 집콕하는 청춘
     - 어색한 첫 대화 공포증 극복기
  4. 산출물 경로 (회차별 전용 폴더 격리)
     - C:/Users/zkfnt/Desktop/한국 숏폼_산출물/Aura/Aura_drama_{YYYYMMDD}_{HHMMSS}/
         ├─ aura_drama_{YYYYMMDD}.mp4
         ├─ aura_drama_{YYYYMMDD}_pipeline_manifest.json
         ├─ audios/
         └─ images/
     - Aura 루트(self.output_dir)에는 어떤 파일/임시 디렉터리도 직접 기록하지 않는다.

[🎬 4컷 시네마틱 드라마 구조 — 총 20초]
  · Cut 1 (도파민 훅, 3초)   : 소개팅 빌런 / 읽씹 / 집콕 솔로 상황 발생
  · Cut 2 (갈등 고조, 6초)   : 주인공 2인 핑퐁 대화 티키타카 (탈출 vs 버티기)
  · Cut 3 (반전 솔루션, 7초) : 'Aura AI 데이팅' AI 매칭·오프닝 비서 극적 등장
  · Cut 4 (여운 & CTA, 4초)  : 펀치라인 + 네이버 공식 검색어 '아우라AI데이팅' 유도

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
        logging.getLogger("AuraDramaPipeline").warning(
            f"⚠️ [AuraDramaPipeline] 콘솔 UTF-8 재설정 실패(무해): {_enc_exc}"
        )

# ==============================================================================
# 📦 [프로젝트 루트 sys.path 보정] 단독 실행 및 패키지 임포트 양립
# ==============================================================================
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger("AuraDramaPipeline")


# ==============================================================================
# 🏛️ [메인 클래스] AuraDramaPipeline
# ==============================================================================
class AuraDramaPipeline:
    """
    💜 Aura AI 데이팅 전용 일일 숏드라마 독립 레고 블록.

    - 기존 Aura 숏폼/카드뉴스 파이프라인과 완전 분리된 독립 모듈.
    - modules.drama_engine.drama_pipeline_facade.DramaPipelineFacade('aura') 단일 연동.
    - produce() 단일 진입점으로 4컷 시네마틱 숏드라마 1편을 무인 생산한다.
    - 모든 산출물은 회차별 전용 에피소드 폴더(episode_dir) 내부로 완전 격리된다.
    """

    # ── 브랜드 식별자 ────────────────────────────────────────────────────────
    BRAND: str = "aura"
    BRAND_FOLDER_NAME: str = "Aura"

    # ── 브랜드 공식 규격 (절대 불변 상수) ────────────────────────────────────
    BRAND_OFFICIAL_NAME: str = "Aura AI 데이팅"
    OFFICIAL_SEARCH_KEYWORD: str = "아우라AI데이팅"  # 붙여쓰기 필수, 띄어쓰기 금지
    LANDING_URL: str = "https://aura-ai-dating.vercel.app/"

    # ── Aura 전용 3대 테마 (빌런 탈출 / 자만추 집콕 / 첫 대화 공포증) ────────
    CORE_THEMES: List[str] = [
        "소개팅 최악의 빌런 vs 긴급 탈출",
        "자만추 꿈꾸지만 집콕하는 청춘",
        "어색한 첫 대화 공포증 극복기",
    ]

    # ── 4컷 시네마틱 타임라인 (3 + 6 + 7 + 4 = 20초) ─────────────────────────
    CUT_DURATIONS: Dict[str, int] = {"cut1": 3, "cut2": 6, "cut3": 7, "cut4": 4}
    TOTAL_DURATION_SEC: int = sum(CUT_DURATIONS.values())  # 20

    # ── 산출물 루트 ──────────────────────────────────────────────────────────
    OUTPUT_ROOT: Path = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물")

    # ── 파일명 규격 ──────────────────────────────────────────────────────────
    FILE_PREFIX: str = "aura_drama"

    def __init__(self, output_root: Optional[Path] = None) -> None:
        """
        Args:
            output_root: 산출물 루트 경로 (기본: C:/Users/zkfnt/Desktop/한국 숏폼_산출물)
        """
        self.output_root = Path(output_root) if output_root else self.OUTPUT_ROOT
        self.output_dir = self.output_root / self.BRAND_FOLDER_NAME
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 🏛️ [파사드 연동] Aura 브랜드 전용 파사드 인스턴스 (지연 임포트)
        self._facade = None

        logger.info(
            f"💜 [AuraDramaPipeline] 초기화 완료 | "
            f"브랜드='{self.BRAND_OFFICIAL_NAME}' | 검색어='{self.OFFICIAL_SEARCH_KEYWORD}' | "
            f"산출물 루트={self.output_dir}"
        )

    # ==========================================================================
    # 🏛️ [파사드 지연 로딩] 무거운 의존성(google-genai, PIL, ffmpeg) 로드 시점 분리
    # ==========================================================================
    @property
    def facade(self) -> Any:
        """DramaPipelineFacade('aura') 지연 생성 및 캐싱"""
        if self._facade is None:
            try:
                from modules.drama_engine.drama_pipeline_facade import DramaPipelineFacade
            except ImportError as exc:
                logger.error(
                    f"🚨 [AuraDramaPipeline] DramaPipelineFacade 임포트 실패: {exc}",
                    exc_info=True,
                )
                raise

            try:
                self._facade = DramaPipelineFacade(self.BRAND)
            except ValueError as exc:
                logger.error(
                    f"🚨 [AuraDramaPipeline] 파사드 생성 실패(브랜드 미지원): {exc}",
                    exc_info=True,
                )
                raise

            logger.info("🏛️ [AuraDramaPipeline] DramaPipelineFacade('aura') 연동 완료")

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
            logger.debug(
                f"🔎 [AuraDramaPipeline] '{raw}' 는 YYYY-MM-DD 형식이 아님 → YYYYMMDD 시도"
            )

        # 2) YYYYMMDD
        try:
            parsed = datetime.strptime(raw, "%Y%m%d")
            return parsed.date().isoformat()
        except ValueError as exc:
            logger.error(
                f"🚨 [AuraDramaPipeline] 날짜 형식 오류: '{raw}' "
                f"(허용: YYYY-MM-DD 또는 YYYYMMDD)",
                exc_info=True,
            )
            raise ValueError(
                f"❌ [AuraDramaPipeline] 날짜 형식 오류: '{raw}'. "
                f"'YYYY-MM-DD' 또는 'YYYYMMDD' 형식만 허용됩니다."
            ) from exc

    # ==========================================================================
    # 📁 [에피소드 폴더 탐색] 회차별 전용 폴더 내 mp4 우선 반환 (하위 호환 유지)
    # ==========================================================================
    def _find_latest_episode_mp4(self, yyyymmdd: str) -> Optional[Path]:
        """
        회차별 전용 에피소드 폴더(Aura_drama_{YYYYMMDD}_{HHMMSS}) 내부에서
        해당 날짜의 mp4 산출물을 탐색하여 가장 최신 파일을 반환한다.

        Args:
            yyyymmdd: 'YYYYMMDD' 8자리 문자열

        Returns:
            Optional[Path]: 최신 에피소드 폴더 내 mp4 경로. 없으면 None.
        """
        pattern = (
            f"{self.BRAND.capitalize()}_drama_{yyyymmdd}_*/"
            f"{self.FILE_PREFIX}_{yyyymmdd}.mp4"
        )
        try:
            candidates = [p for p in self.output_dir.glob(pattern) if p.is_file()]
        except OSError as exc:
            logger.error(
                f"🚨 [AuraDramaPipeline] 에피소드 폴더 탐색 실패(패턴={pattern}): {exc}",
                exc_info=True,
            )
            return None

        if not candidates:
            logger.debug(
                f"🔎 [AuraDramaPipeline] '{yyyymmdd}' 에피소드 폴더 내 mp4 미발견 → 루트 경로 폴백"
            )
            return None

        # 폴더명에 HHMMSS 가 포함되므로 경로 문자열 정렬로 최신 회차를 확정한다.
        latest = max(candidates, key=lambda p: (p.parent.name, p.stat().st_mtime))
        logger.info(
            f"📁 [AuraDramaPipeline] 에피소드 폴더 내 mp4 발견 → 최신 회차 우선 반환: {latest}"
        )
        return latest

    # ==========================================================================
    # 📁 [산출물 경로 산출] 에피소드 폴더 우선 → 루트 폴백 (하위 호환)
    # ==========================================================================
    def get_output_path(self, date_str: Optional[str] = None) -> Path:
        """
        산출물 MP4 절대 경로를 반환한다.

        [우선순위]
          1순위: 회차별 전용 에피소드 폴더 내 mp4
                 (Aura_drama_{YYYYMMDD}_{HHMMSS}/aura_drama_{YYYYMMDD}.mp4)
          2순위: 하위 호환용 Aura 루트 경로
                 (Aura/aura_drama_{YYYYMMDD}.mp4)

        Args:
            date_str: 'YYYY-MM-DD' | 'YYYYMMDD' | None(오늘)

        Returns:
            Path: 산출물 MP4 절대 경로
        """
        normalized = self._normalize_date(date_str)
        yyyymmdd = normalized.replace("-", "")

        # 1순위: 에피소드 폴더 내 최신 mp4
        episode_mp4 = self._find_latest_episode_mp4(yyyymmdd)
        if episode_mp4 is not None:
            return episode_mp4

        # 2순위: 하위 호환 — Aura 루트 경로
        return self.output_dir / f"{self.FILE_PREFIX}_{yyyymmdd}.mp4"

    # ==========================================================================
    # 🔍 [시나리오 유효성 검증] 브랜드 공식 규격 위반 시 ValueError 명시 발생
    # ==========================================================================
    def _validate_scenario(self, scenario: Dict[str, Any]) -> None:
        """
        4컷 시나리오가 Aura AI 데이팅 공식 규격을 100% 준수하는지 전수 검증한다.

        Raises:
            ValueError: 규격 위반 항목이 하나라도 발견된 경우
        """
        if not isinstance(scenario, dict):
            raise ValueError(
                f"❌ [AuraDramaPipeline] 시나리오 타입 오류: dict 기대, 실제 {type(scenario).__name__}"
            )

        # 1) 브랜드 식별자 검증
        scenario_brand = str(scenario.get("brand", "")).lower().strip()
        if scenario_brand != self.BRAND:
            raise ValueError(
                f"❌ [AuraDramaPipeline] 브랜드 불일치: '{scenario_brand}' (기대: '{self.BRAND}')"
            )

        # 2) 공식 검색어 검증 (붙여쓰기 필수 — 띄어쓰기 금지)
        official_keyword = str(scenario.get("official_search_keyword", "")).strip()
        if official_keyword != self.OFFICIAL_SEARCH_KEYWORD:
            raise ValueError(
                f"❌ [AuraDramaPipeline] 공식 검색어 규격 위반: '{official_keyword}' "
                f"(기대: '{self.OFFICIAL_SEARCH_KEYWORD}' — 붙여쓰기 필수, 띄어쓰기 금지)"
            )

        # 3) 4컷 구조 검증
        cuts = scenario.get("cuts")
        if not isinstance(cuts, list) or len(cuts) != 4:
            raise ValueError(
                f"❌ [AuraDramaPipeline] 4컷 구조 위반: cuts 개수 "
                f"{len(cuts) if isinstance(cuts, list) else 'N/A'} (기대: 4)"
            )

        expected_cut_ids = ["cut1", "cut2", "cut3", "cut4"]
        for idx, cut in enumerate(cuts):
            if not isinstance(cut, dict):
                raise ValueError(
                    f"❌ [AuraDramaPipeline] 컷 #{idx + 1} 타입 오류: dict 기대, 실제 {type(cut).__name__}"
                )
            cut_id = str(cut.get("cut_id", ""))
            if cut_id != expected_cut_ids[idx]:
                raise ValueError(
                    f"❌ [AuraDramaPipeline] 컷 ID 순서 위반: {idx + 1}번째 '{cut_id}' "
                    f"(기대: '{expected_cut_ids[idx]}')"
                )
            speech = str(cut.get("speech", "")).strip()
            if not speech:
                raise ValueError(
                    f"❌ [AuraDramaPipeline] 컷 '{cut_id}' 대사(speech) 누락"
                )
            expected_dur = self.CUT_DURATIONS[cut_id]
            actual_dur = cut.get("duration_sec")
            if actual_dur != expected_dur:
                raise ValueError(
                    f"❌ [AuraDramaPipeline] 컷 '{cut_id}' 길이 규격 위반: {actual_dur}초 "
                    f"(기대: {expected_dur}초)"
                )

        # 4) 총 길이 20초 검증
        total_dur = scenario.get("total_duration_sec")
        if total_dur != self.TOTAL_DURATION_SEC:
            raise ValueError(
                f"❌ [AuraDramaPipeline] 총 길이 규격 위반: {total_dur}초 "
                f"(기대: {self.TOTAL_DURATION_SEC}초)"
            )

        # 5) CTA 내 공식 검색어 포함 검증 (네이버 검색 유도 필수)
        speech_cta = str(scenario.get("speech_cta", ""))
        if self.OFFICIAL_SEARCH_KEYWORD not in speech_cta:
            raise ValueError(
                f"❌ [AuraDramaPipeline] CTA에 공식 검색어 '{self.OFFICIAL_SEARCH_KEYWORD}' 누락: '{speech_cta}'"
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
                f"❌ [AuraDramaPipeline] 6키 평탄화 누락: {missing_keys}"
            )

        logger.info(
            f"✅ [AuraDramaPipeline] 시나리오 규격 검증 100% 합격 | "
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
        Aura AI 데이팅 일일 숏드라마 1편을 무인 생산한다.

        Args:
            date_str: 'YYYY-MM-DD' | 'YYYYMMDD' | None(오늘)
            auto_publish: True 면 생산 직후 SNS 자동 송출 훅까지 실행

        Returns:
            Dict[str, Any]: 생산 결과 매니페스트
                {
                    "status": "success",
                    "brand": "aura",
                    "brand_official_name": "Aura AI 데이팅",
                    "official_search_keyword": "아우라AI데이팅",
                    "landing_url": "https://aura-ai-dating.vercel.app/",
                    "date": "YYYY-MM-DD",
                    "theme": "...",
                    "location": "...",
                    "episode_dir": "...Aura_drama_YYYYMMDD_HHMMSS",
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

        logger.info("=" * 88)
        logger.info(
            f"🎬 [AuraDramaPipeline] Aura AI 데이팅 일일 숏드라마 생산 착수 | "
            f"날짜={normalized_date} | auto_publish={auto_publish}"
        )
        logger.info(
            f"🎯 공식 명칭='{self.BRAND_OFFICIAL_NAME}' | 공식 검색어='{self.OFFICIAL_SEARCH_KEYWORD}'"
        )
        logger.info(f"🔗 랜딩 URL={self.LANDING_URL}")
        logger.info(
            f"📁 산출물 루트={self.output_dir} "
            f"(회차별 전용 폴더 {self.BRAND.capitalize()}_drama_{yyyymmdd}_HHMMSS 내부로 완전 격리)"
        )
        logger.info("=" * 88)

        # ── 1단계: 파사드 연동 및 4컷 시나리오 사전 검증 ──────────────────────
        try:
            scenario_preview = self.facade.scenario_director.get_daily_drama_scenario(
                brand=self.BRAND,
                date_str=normalized_date,
            )
        except ValueError as exc:
            logger.error(
                f"🚨 [AuraDramaPipeline] 시나리오 생성 실패: {exc}",
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
                f"🚨 [AuraDramaPipeline] 파사드 생산 실패: {exc}",
                exc_info=True,
            )
            raise RuntimeError(
                f"❌ [AuraDramaPipeline] Aura AI 데이팅 숏드라마 생산 실패: {exc}"
            ) from exc

        if not isinstance(facade_manifest, dict):
            raise RuntimeError(
                f"❌ [AuraDramaPipeline] 파사드 반환 타입 오류: dict 기대, "
                f"실제 {type(facade_manifest).__name__}"
            )

        # ── 3단계: 산출물 실물 검증 (파일 존재 + 용량) ────────────────────────
        produced_mp4 = Path(str(facade_manifest.get("output_mp4", "")))
        if not produced_mp4.exists():
            logger.error(
                f"🚨 [AuraDramaPipeline] 산출물 MP4 미생성: {produced_mp4}",
                exc_info=True,
            )
            raise FileNotFoundError(
                f"❌ [AuraDramaPipeline] 산출물 MP4가 생성되지 않았습니다: {produced_mp4}"
            )

        output_size = produced_mp4.stat().st_size
        if output_size <= 0:
            logger.error(
                f"🚨 [AuraDramaPipeline] 산출물 MP4 용량 0바이트: {produced_mp4}",
                exc_info=True,
            )
            raise RuntimeError(
                f"❌ [AuraDramaPipeline] 산출물 MP4가 0바이트입니다: {produced_mp4}"
            )

        # 🗂️ [회차별 전용 폴더 격리] 파사드가 반환한 mp4 의 부모가 곧 episode_dir
        episode_dir = produced_mp4.parent
        if not episode_dir.exists():
            logger.error(
                f"🚨 [AuraDramaPipeline] 에피소드 폴더 부재: {episode_dir}",
                exc_info=True,
            )
            raise FileNotFoundError(
                f"❌ [AuraDramaPipeline] 에피소드 폴더가 존재하지 않습니다: {episode_dir}"
            )

        # ── 4단계: Aura 전용 통합 매니페스트 저장 (Aura 루트 무기록 · 에피소드 폴더 내부) ──
        manifest_path = produced_mp4.parent / f"{self.FILE_PREFIX}_{yyyymmdd}_pipeline_manifest.json"
        result: Dict[str, Any] = {
            "status": "success",
            "brand": self.BRAND,
            "brand_official_name": self.BRAND_OFFICIAL_NAME,
            "official_search_keyword": self.OFFICIAL_SEARCH_KEYWORD,
            "landing_url": self.LANDING_URL,
            "date": normalized_date,
            "theme": facade_manifest.get("theme", ""),
            "location": facade_manifest.get("location", ""),
            "episode_dir": str(produced_mp4.parent),
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
                f"🚨 [AuraDramaPipeline] 매니페스트 저장 실패: {manifest_path} ({exc})",
                exc_info=True,
            )
            raise

        logger.info(
            f"🎉 [AuraDramaPipeline] Aura AI 데이팅 숏드라마 생산 완결 | "
            f"{produced_mp4.name} ({output_size // 1024}KB, {self.TOTAL_DURATION_SEC}초)"
        )
        logger.info(f"🗂️ 에피소드 전용 폴더: {episode_dir}")
        logger.info(f"🧾 통합 매니페스트 저장: {manifest_path}")
        logger.info("=" * 88)

        return result

    # ==========================================================================
    # 🧾 [편의 메서드] 브랜드 규격 요약
    # ==========================================================================
    def get_brand_spec(self) -> Dict[str, Any]:
        """Aura AI 데이팅 공식 규격 요약을 반환한다."""
        return {
            "brand": self.BRAND,
            "brand_official_name": self.BRAND_OFFICIAL_NAME,
            "official_search_keyword": self.OFFICIAL_SEARCH_KEYWORD,
            "landing_url": self.LANDING_URL,
            "core_themes": list(self.CORE_THEMES),
            "cut_durations": dict(self.CUT_DURATIONS),
            "total_duration_sec": self.TOTAL_DURATION_SEC,
            "output_dir": str(self.output_dir),
            "episode_dir_pattern": (
                f"{self.BRAND.capitalize()}_drama_YYYYMMDD_HHMMSS"
            ),
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
    print("💜 [AuraDramaPipeline] Aura AI 데이팅 전용 일일 숏드라마 독립 레고 블록 자체 점검")
    print("=" * 88)

    pipeline = AuraDramaPipeline()

    # 1) 브랜드 공식 규격 출력
    spec = pipeline.get_brand_spec()
    print("\n📋 [브랜드 공식 규격]")
    for key, value in spec.items():
        print(f"  · {key:<26}: {value}")

    # 2) 날짜 정규화 및 산출물 경로 검증 (에피소드 폴더 우선 → 루트 폴백)
    print("\n📁 [산출물 경로 검증 — 에피소드 폴더 우선 / 루트 폴백]")
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

    # 4) 공식 검색어 붙여쓰기 규격 검증 (띄어쓰기 금지)
    print("\n🔤 [공식 검색어 붙여쓰기 규격 검증]")
    if " " in pipeline.OFFICIAL_SEARCH_KEYWORD:
        print(f"  · ❌ 공식 검색어에 띄어쓰기가 포함되어 있습니다: '{pipeline.OFFICIAL_SEARCH_KEYWORD}'")
    else:
        print(f"  · ✅ 붙여쓰기 규격 준수: '{pipeline.OFFICIAL_SEARCH_KEYWORD}'")

    # 5) 시나리오 규격 사전 검증 (실제 렌더링 없이 시나리오만 확인)
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
    print("✅ [AuraDramaPipeline] 자체 점검 완료")
    print("   실제 영상 생산은 produce(date_str=None, auto_publish=True) 를 호출하십시오.")
    print("=" * 88)
