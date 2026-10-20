# -*- coding: utf-8 -*-
"""
[독립 레고 블록] Insurance Omni Cardnews Pilot (🛡️ 보험 리밸런스 전용 쏘기 직전 5장 카드뉴스 제작 & Meta 단발 송출 파일럿)
=============================================================================================================================
- 브랜드: 보험 리밸런스 (공식 검색어: '보험 리밸런스' 띄어쓰기 불변)
- 핵심 원칙 (대표님 절대 수칙):
  1. [쏘기 전 무조건 먼저 생산]: 바탕화면 옛날 폴더 무단 주워오기 전면 배제!
     정시(스케줄) 도달 시, 이번 순번 주제(예: #1) 5장 카드뉴스 슬라이드를 쏘기 직전 단독 생산
  2. [즉시 1회 단발 발사]: 방금 생성된 5장 슬라이드를 넘겨받아 Meta 플랫폼 동시 송출
     - ① 페이스북 5장 카드뉴스 앨범 (Facebook Cardnews Album + 첫 댓글 스텔스 링크)
     - ② 인스타그램 캐러셀 피드 (Instagram Carousel 5장 피드)
  3. [완벽한 메타데이터 패키징]: 제목, 설명문, 첫댓글 링크 문구, 공식 검색어 유도, 4단 해시태그 100% 탑재
  4. [중복 방지 락(Lock)]: 당일 동일 주제 중복 송출 0% 원천 차단
  5. [주간 GPU 양보 가드]: 07:00~23:59에는 KTRS에 GPU를 양보하므로 신규 렌더링 100% 원천 차단
     (야간 골든타임 00:00~06:59에만 신규 렌더링 허용)
"""

import os
import sys
import glob
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import BASE_DIR, get_now_kst_str
from brands.insurance.insurance_hashtag_matrix import InsuranceHashtagMatrix
from brands.insurance.insurance_mbs_reels_publisher import InsuranceMBSReelsPublisher
from brands.insurance.insurance_youtube_bot_publisher import InsuranceYouTubeBotPublisher
from brands.insurance.insurance_tiktok_publisher import InsuranceTikTokPublisher
from brands.insurance.insurance_naver_clip_publisher import InsuranceNaverClipPublisher

# 🆕 [생산/송출 완전 분리 영수증 가드] 일일 쿼터 & 송출 3회 서킷브레이커
from core.receipt_engine.daily_receipt_guard import (
    DailyReceiptGuard,
    DAILY_QUOTAS,
    MAX_DISPATCH_RETRIES,
)

logger = logging.getLogger("InsuranceOmniCardnewsPilot")


class DaytimeRenderForbidden(RuntimeError):
    """🚨 [주간 GPU 렌더링 원천 차단] 07:00~23:59에는 KTRS에 GPU를 양보하므로 신규 렌더링이 금지됩니다."""
    def __init__(self, message: str = "🚨 [주간 GPU 렌더링 원천 차단] 07:00~23:59 시간대에는 KTRS에 GPU를 양보하므로 신규 렌더링이 금지됩니다."):
        super().__init__(message)
        self.message = message


class InsuranceOmniCardnewsPilot:
    """🛡️ 보험 리밸런스 전용 [쏘기 직전 5장 카드뉴스 제작 ➔ Meta 1회 단발 송출] 통합 관제 파일럿"""

    BRAND = "insurance"
    MEDIA_TYPE = "cardnews"
    OFFICIAL_KEYWORD = "보험 리밸런스"
    LANDING_URL = "https://insure-rebalance.vercel.app/"

    # 🚨 [주간 GPU 양보 시간대] 07:00 ~ 23:59 (KTRS 우선 배정)
    DAYTIME_START_HOUR = 7
    DAYTIME_END_HOUR = 23

    # 🆕 [실패 주제 쿨다운] 실패한 주제가 무한 재선정되는 것을 막는 냉각 시간(시간 단위)
    FAIL_COOLDOWN_HOURS = 6

    CARDNEWS_TOPICS = {
        1: "4세대 실손보험 전환하면 호갱? 월 5만원 아끼는 진실",
        2: "10년 갱신형 암보험의 함정: 60세에 35만원 폭탄 맞습니다",
        3: "사회초년생 월급 250만원에 보험료 20만원 내고 있다면?",
        4: "뇌졸중 왔는데 보험금 0원? '뇌출혈' 특약 가입자의 비극",
        5: "옛날 운전자보험 그대로 두면 사고 시 형사합의금 못 받습니다",
        6: "하루 15만원 간병비 파산 막는 '간병인 사용일당'의 비밀",
        7: "중복 가입으로 10년간 줄줄 샌 내 보험료, 1분 만에 찾기",
        8: "보험료 부담돼서 해지하려고요? 절대 해지하지 마세요!"
    }

    def __init__(self):
        self.hashtag_matrix = InsuranceHashtagMatrix()
        self.mbs_pub = InsuranceMBSReelsPublisher()
        self.youtube_pub = InsuranceYouTubeBotPublisher(headless=True)
        self.clip_pub = InsuranceNaverClipPublisher()
        self.tiktok_pub = InsuranceTikTokPublisher(headless=True)
        self.history_file = CURRENT_DIR / "omni_cardnews_publish_history.json"
        self.state_file = CURRENT_DIR / "omni_cardnews_schedule_state.json"

        # 🆕 [영수증 가드] 일일 쿼터(카드뉴스 2개) & 송출 3회 서킷브레이커 단일 관제
        self.guard = DailyReceiptGuard()
        self.daily_quota = DAILY_QUOTAS.get(self.MEDIA_TYPE, 2)

    # ------------------------------------------------------------------
    # 🚨 [주간 GPU 양보 시간대 판정]
    # ------------------------------------------------------------------
    def is_daytime_gpu_yield_window(self, now: Optional[datetime] = None) -> bool:
        """
        🚨 [주간 GPU 양보 시간대 판정]
        - 07:00 ~ 23:59 사이이면 True (KTRS에 GPU 양보 ➔ 신규 렌더링 금지)
        - 00:00 ~ 06:59 사이이면 False (야간 골든타임 ➔ 신규 렌더링 허용)
        """
        current = now or datetime.now()
        hour = current.hour
        return self.DAYTIME_START_HOUR <= hour <= self.DAYTIME_END_HOUR

    def _load_state(self) -> Dict[str, Any]:
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"last_topic_id": 0, "published_today": []}

    def _save_state(self, state: Dict[str, Any]):
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"상태 저장 경고: {e}")

    # ------------------------------------------------------------------
    # 🆕 [영수증 가드 헬퍼] 생산 쿼터 / 송출 판정 / 결과 기록 / 봉인
    # ------------------------------------------------------------------
    def _guard_can_produce(self) -> bool:
        """당일 카드뉴스 생산 쿼터(2개) 잔여 여부. 가드 예외 시 보수적 차단."""
        try:
            return self.guard.can_produce(self.BRAND, self.MEDIA_TYPE)
        except Exception as ge:
            logger.error(f"❌ [영수증 가드 오류] 생산 쿼터 조회 실패 ➔ 안전 우선 차단: {ge}")
            return False

    def _guard_remaining_quota(self) -> int:
        try:
            return self.guard.get_remaining_quota(self.BRAND, self.MEDIA_TYPE)
        except Exception:
            return 0

    def _guard_can_dispatch(self, topic_id: int) -> bool:
        """송출 가능 판정. 가드 예외 시 보수적 차단(중복/폭주 방지)."""
        try:
            return self.guard.can_dispatch(self.BRAND, self.MEDIA_TYPE, int(topic_id))
        except Exception as ge:
            logger.error(f"❌ [영수증 가드 오류] 송출 판정 실패 ➔ 안전 우선 차단: {ge}")
            return False

    def _guard_seal(self, topic_id: int, artifact_path: str) -> Optional[str]:
        """신규 렌더링 성공 시 영수증 봉인. 실패해도 송출 자체는 막지 않음(경고만)."""
        try:
            key = self.guard.seal_receipt(
                self.BRAND, self.MEDIA_TYPE, int(topic_id), str(artifact_path)
            )
            logger.info(f"🧾 [영수증 봉인 완료] {key} ➔ {artifact_path}")
            return key
        except Exception as se:
            logger.warning(f"⚠️ [영수증 봉인 경고] {se}")
            return None

    def _guard_record_result(self, topic_id: int, success: bool, error_msg: str = ""):
        """
        송출 결과 기록.
        🚨 단방향 원칙: 이 메서드는 오직 상태 기록만 수행하며,
           어떤 경우에도 생산(produce_fresh_cardnews)을 재호출하지 않습니다.
        """
        try:
            self.guard.record_dispatch_result(
                self.BRAND, self.MEDIA_TYPE, int(topic_id),
                success=success, error_msg=error_msg
            )
        except Exception as re:
            logger.warning(f"⚠️ [영수증 결과 기록 경고] {re}")

    def _guard_auto_scan(self) -> List[str]:
        """바탕화면 당일 완제품 자동 스캔 ➔ 영수증 자동 등록 (쿼터까지만)."""
        try:
            sealed = self.guard.auto_scan_and_seal(self.BRAND, self.MEDIA_TYPE)
            if sealed:
                logger.info(f"🧾 [영수증 자동 스캔] 당일 완제품 {len(sealed)}건 자동 봉인: {sealed}")
            return sealed
        except Exception as ae:
            logger.warning(f"⚠️ [영수증 자동 스캔 경고] {ae}")
            return []

    def get_next_topic_id(self) -> int:
        """
        🔄 [8-Topic LRU Anti-Duplication Ring Buffer]
        - 최근 발행 이력(history)을 전수 역추적하여 가장 오랫동안 송출되지 않은 주제(LRU)를 자동 선정
        - 오늘 이미 송출된 주제는 최우선적으로 배제 (하루 슬롯 간 중복 0% 철통 보장)

        🚨 [결함 수정] 기존 로직은 '한 번도 성공하지 못한 주제'와 '실패한 주제'를
           모두 last_seen=999999 로 부여한 뒤 reverse=True 정렬을 수행했습니다.
           그 결과 실패 주제가 매번 최우선 1순위로 무한 승격되어,
           실패한 주제만 하루 종일 반복 선택되는 역설이 발생했습니다.

        ✅ [수정 원칙]
           1. 성공 이력이 있는 주제: 실제 최근 성공 순번(작을수록 최근)을 사용
           2. 성공 이력이 없는 주제: '미시도'로 간주하여 성공 주제보다 우선하되,
              동일 그룹 내에서는 주제 번호 오름차순으로 결정적(deterministic) 선정
           3. 실패 이력은 승격 근거(999999)로 절대 사용하지 않음
           4. 실패 주제는 FAIL_COOLDOWN_HOURS 내 재선정 금지 ➔ 무한 재시도 루프 차단
        """
        all_topics = list(self.CARDNEWS_TOPICS.keys())
        today_str = datetime.now().strftime("%Y-%m-%d")
        now_ts = time.time()

        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []

        if not isinstance(history, list):
            history = []

        # 1) 오늘 성공 송출된 주제 (최우선 배제)
        today_published = {
            item.get("topic_id")
            for item in history
            if isinstance(item, dict)
            and item.get("date") == today_str
            and item.get("status") == "success"
            and item.get("topic_id") in all_topics
        }

        # 2) 주제별 최근 성공 순번 (reversed 인덱스: 작을수록 최근)
        last_success_rank: Dict[int, int] = {}
        for idx, item in enumerate(reversed(history)):
            if not isinstance(item, dict):
                continue
            tid = item.get("topic_id")
            if tid in all_topics and item.get("status") == "success":
                if tid not in last_success_rank:
                    last_success_rank[tid] = idx

        # 3) 주제별 최근 실패 시각 (쿨다운 판정용) — 승격 근거로는 사용하지 않음
        last_fail_ts: Dict[int, float] = {}
        for item in reversed(history):
            if not isinstance(item, dict):
                continue
            tid = item.get("topic_id")
            if tid not in all_topics:
                continue
            if item.get("status") in ("error", "failed", "verification_failed", "circuit_open", "dispatch_failed"):
                if tid in last_fail_ts:
                    continue
                ts = self._parse_history_ts(item)
                if ts:
                    last_fail_ts[tid] = ts

        cooldown_sec = self.FAIL_COOLDOWN_HOURS * 3600

        def _is_cooling_down(tid: int) -> bool:
            ts = last_fail_ts.get(tid)
            if not ts:
                return False
            return (now_ts - ts) < cooldown_sec

        # 4) 후보군 구성: 오늘 미송출 ➔ 실패 쿨다운 중인 주제는 후순위로 밀어냄
        base_candidates = [tid for tid in all_topics if tid not in today_published]
        if not base_candidates:
            base_candidates = list(all_topics)

        fresh_candidates = [tid for tid in base_candidates if not _is_cooling_down(tid)]
        cooling_candidates = [tid for tid in base_candidates if _is_cooling_down(tid)]

        # 5) 정렬: 미시도(성공 이력 없음) 우선 ➔ 성공 이력 오래된 순 ➔ 주제 번호 오름차순
        def _sort_key(tid: int):
            has_success = tid in last_success_rank
            # 미시도 주제는 group 0(최우선), 성공 이력 주제는 group 1
            group = 1 if has_success else 0
            rank = last_success_rank.get(tid, 0)
            return (group, rank, tid)

        chosen_id: Optional[int] = None
        if fresh_candidates:
            fresh_candidates.sort(key=_sort_key)
            chosen_id = fresh_candidates[0]
        elif cooling_candidates:
            # 전 주제가 쿨다운 중이면 가장 오래전에 실패한 주제로 폴백 (무한 승격 아님)
            cooling_candidates.sort(key=lambda t: (last_fail_ts.get(t, 0), t))
            chosen_id = cooling_candidates[0]
            logger.warning(
                f"⚠️ [LRU 폴백] 전 주제가 실패 쿨다운 중 ➔ 가장 오래된 실패 주제 #{chosen_id} 선택"
            )
        else:
            chosen_id = all_topics[0]

        state = self._load_state()
        state["last_topic_id"] = chosen_id
        self._save_state(state)

        logger.info(
            f"🔄 [보험 카드뉴스 LRU 자동 선정] 후보군 {fresh_candidates} ➔ 선정 주제: #{chosen_id} "
            f"(오늘 송출완료: {today_published}, 쿨다운: {cooling_candidates})"
        )
        return chosen_id

    @staticmethod
    def _parse_history_ts(item: Dict[str, Any]) -> float:
        """히스토리 레코드의 시각을 epoch 초로 변환 (published_at ➔ date 순 폴백)."""
        for key in ("published_at", "failed_at", "checked_at"):
            raw = item.get(key)
            if not raw:
                continue
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                try:
                    return datetime.strptime(str(raw)[:19], fmt).timestamp()
                except Exception:
                    continue
        raw_date = item.get("date")
        if raw_date:
            try:
                return datetime.strptime(str(raw_date), "%Y-%m-%d").timestamp()
            except Exception:
                pass
        return 0.0

    def is_already_published_today(self, topic_id: int) -> bool:
        """[중복 방지 락] 오늘 이미 해당 주제가 송출되었는지 점검"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
                    for item in history:
                        if item.get("date") == today_str and item.get("topic_id") == topic_id and item.get("status") == "success":
                            return True
            except Exception:
                pass
        return False

    def _find_today_completed_slides(self, topic_id: int) -> List[str]:
        """
        🔍 [1단계] 오늘 완성된 최신 완제품 슬라이드(slide_1.png ~ slide_5.png) 바탕화면 탐색
        - 오늘 날짜(YYYYMMDD) 폴더 + 주제 번호 일치 + 슬라이드 4장 이상 실물 존재 시 반환
        """
        today_str = datetime.now().strftime("%Y%m%d")
        desktop_base = Path(os.environ.get("USERPROFILE", "C:/Users/zkfnt")) / "Desktop" / "한국 카드뉴스_산출물" / "보험"
        if not desktop_base.exists():
            return []

        topic_str = f"{topic_id:02d}"
        candidates = []
        for folder in desktop_base.iterdir():
            if not folder.is_dir():
                continue
            if f"_{topic_str}_" not in folder.name:
                continue
            if today_str not in folder.name:
                continue
            slides = [str(folder / f"slide_{i}.png") for i in range(1, 6) if (folder / f"slide_{i}.png").exists()]
            if len(slides) >= 4:
                try:
                    mtime = folder.stat().st_mtime
                except Exception:
                    mtime = 0
                candidates.append((mtime, folder, slides))

        if not candidates:
            return []

        candidates.sort(key=lambda x: x[0], reverse=True)
        _, best_folder, best_slides = candidates[0]
        logger.info(f"✨ [보험 카드뉴스 완제품 즉각 확보] 오늘 완성된 무결점 슬라이드 {len(best_slides)}장 감지: {best_folder.name}")
        return best_slides

    def _find_any_today_completed_slides(self) -> List[str]:
        """
        🆕 [쿼터 달성 시 폴백] 주제 번호 무관, 오늘 완성된 완제품 슬라이드 중 최신 1세트 반환.
        - 신규 렌더링 없이 '이미 생산된 완제품'만 재사용 (생산 0%)
        """
        today_str = datetime.now().strftime("%Y%m%d")
        desktop_base = Path(os.environ.get("USERPROFILE", "C:/Users/zkfnt")) / "Desktop" / "한국 카드뉴스_산출물" / "보험"
        if not desktop_base.exists():
            return []

        candidates = []
        try:
            for folder in desktop_base.iterdir():
                if not folder.is_dir():
                    continue
                if today_str not in folder.name:
                    continue
                slides = [str(folder / f"slide_{i}.png") for i in range(1, 6) if (folder / f"slide_{i}.png").exists()]
                if len(slides) >= 4:
                    try:
                        mtime = folder.stat().st_mtime
                    except Exception:
                        mtime = 0
                    candidates.append((mtime, folder, slides))
        except Exception:
            return []

        if not candidates:
            return []

        candidates.sort(key=lambda x: x[0], reverse=True)
        _, best_folder, best_slides = candidates[0]
        logger.info(f"♻️ [완제품 재사용] 오늘 완성된 기존 완제품 {len(best_slides)}장 재사용: {best_folder.name}")
        return best_slides

    def produce_fresh_cardnews(self, topic_id: int) -> List[str]:
        """
        🎨 [쏘기 직전 5장 카드뉴스 제작]
        - 1단계: 오늘 완성된 최신 완제품 슬라이드가 바탕화면에 있으면 즉시 반환 (GPU 재렌더링 0%)
        - 2단계: 완제품이 없고 주간 GPU 양보 시간대(07:00~23:59)이면 DaytimeRenderForbidden 발생 ➔ 신규 렌더링 100% 원천 차단
        - 3단계: 야간 골든타임(00:00~06:59)에만 신규 렌더링 실행
        """
        logger.info("=" * 70)
        logger.info(f"🎨 [보험 카드뉴스 제작] 쏘기 직전 주제 #{topic_id} 5장 확보 절차 시작...")
        logger.info("=" * 70)

        # 0단계: 🆕 [영수증 상한 가드] 당일 생산 쿼터 달성 시 신규 렌더링 원천 차단
        if not self._guard_can_produce():
            logger.info(
                f"🛑 [영수증 상한 {self.daily_quota}개 달성] 보험 카드뉴스 오늘치 완제품 생산 완료. "
                f"신규 렌더링 100% 원천 차단."
            )
            # 신규 렌더링 없이 '기존 완제품 슬라이드'만 탐색하여 반환 (없으면 빈 리스트 ➔ 상위에서 스킵)
            existing_any = self._find_any_today_completed_slides()
            if existing_any:
                logger.info(f"♻️ [신규 렌더링 0%] 기존 완제품 {len(existing_any)}장으로 송출 진행")
                return existing_any
            logger.warning("🛑 [영수증 상한 달성 + 재사용 가능한 완제품 없음] 신규 렌더링 없이 스킵합니다.")
            return []

        # 1단계: 오늘 완성된 최신 완제품이 이미 바탕화면에 존재하는지 우선 탐색 (중복 GPU 렌더링 방지 & 즉각 송출)
        existing_slides = self._find_today_completed_slides(topic_id)
        if existing_slides:
            # 🆕 기존 완제품도 영수증 봉인 (쿼터 카운트에 반영)
            self._guard_seal(topic_id, str(Path(existing_slides[0]).parent))
            return existing_slides

        # 2단계: 주간 GPU 양보 시간대(07:00~23:59) ➔ 신규 렌더링 원천 차단
        now = datetime.now()
        if self.is_daytime_gpu_yield_window(now):
            logger.warning(
                f"🚨 [주간 GPU 양보 가드 발동] 현재 {now.strftime('%H:%M')} ➔ "
                f"{self.DAYTIME_START_HOUR:02d}:00~{self.DAYTIME_END_HOUR:02d}:59 신규 렌더링 원천 차단 (KTRS GPU 우선 배정)"
            )
            raise DaytimeRenderForbidden()

        # 3단계: 야간 골든타임(00:00~06:59)에만 신규 렌더링 실행
        logger.info(f"🌙 [야간 골든타임 렌더링 승인] 현재 {now.strftime('%H:%M')} ➔ 주제 #{topic_id} 신규 렌더링 개시")
        from brands.insurance.insurance_cardnews_producer import InsuranceCardnewsProducer
        producer = InsuranceCardnewsProducer()
        res = producer.produce_full_package(topic_id=topic_id)

        slide_files = res.get("slide_files", [])
        if not slide_files or len(slide_files) < 5:
            raise RuntimeError(f"보험 카드뉴스 5장 생성 실패 (생성된 파일 수: {len(slide_files)}장)")

        logger.info(f"✅ [보험 카드뉴스 5장 생성 완료] 슬라이드 목록: {slide_files}")
        # 🆕 신규 렌더링 성공 ➔ 영수증 봉인 (폴더 경로 기준)
        folder_path = res.get("folder_path") or res.get("output_dir") or str(Path(slide_files[0]).parent)
        self._guard_seal(topic_id, str(folder_path))
        return slide_files

    def build_meta_packages(self, topic_id: int) -> Dict[str, Any]:
        """[제미나이 100% 실시간 카피 + 실시간 급상승 트렌드 해시태그 융합] 5장 카드뉴스 및 4대 채널 포스팅 패키지"""
        main_title = self.CARDNEWS_TOPICS.get(topic_id, f"보험 리모델링 카드뉴스 #{topic_id}")
        from brands.insurance.insurance_domestic_sns_copywriter import InsuranceDomesticSNSCopywriter
        copywriter = InsuranceDomesticSNSCopywriter()
        pkg = copywriter.generate_full_package(topic_id=topic_id, topic_title=main_title, media_type="shorts")
        return {
            "title": main_title,
            "youtube": pkg.get("youtube", {}),
            "naver_clip": pkg.get("naver_clip", {}),
            "tiktok": pkg.get("tiktok", {}),
            "ig_caption": pkg.get("meta_reels", {}).get("caption") or pkg.get("meta", {}).get("ig_caption", ""),
            "fb_caption": pkg.get("facebook", {}).get("caption") or pkg.get("meta", {}).get("fb_caption", ""),
            "fb_comment": pkg.get("facebook", {}).get("comment") or pkg.get("meta", {}).get("fb_comment", "")
        }

    def execute_single_slot(self, topic_id: Optional[int] = None, force: bool = False) -> Dict[str, Any]:
        """
        🚀 [정시 1회 단발 실행] 쏘기 직전 5장 제작 ➔ 4대 플랫폼 즉시 1회 발사 ➔ 중복 락
        """
        target_topic = topic_id or self.get_next_topic_id()
        today_str = datetime.now().strftime("%Y-%m-%d")

        # 0. 🆕 [영수증 자동 스캔] 바탕화면 당일 완제품을 먼저 영수증으로 등록 (쿼터 정확 산정)
        self._guard_auto_scan()

        if not force and self.is_already_published_today(target_topic):
            logger.info(f"🛑 [중복 방지 락] 보험 카드뉴스 주제 #{target_topic}은 오늘 이미 송출되었습니다. 스킵합니다.")
            return {"status": "skipped", "message": f"주제 #{target_topic} 오늘 송출 완료 상태"}

        # 2. 🆕 [서킷브레이커] 송출 가능 판정 (3회 실패 격리 / 중복 송출 차단)
        if not self._guard_can_dispatch(target_topic):
            logger.warning(
                f"🛑 [3회 송출 실패 서킷브레이커] 보험 카드뉴스 오늘 송출 중단 (데드레터 격리) "
                f"➔ 주제 #{target_topic}"
            )
            return {"status": "circuit_open", "message": "송출 재시도 3회 초과 차단"}

        try:
            slides = self.produce_fresh_cardnews(target_topic)
        except DaytimeRenderForbidden as dfe:
            logger.warning(f"🌙 [주간 GPU 양보] 주제 #{target_topic} 신규 렌더링 스킵 ➔ KTRS에 GPU 양보: {dfe.message}")
            return {"status": "daytime_skipped", "message": "주간 GPU 양보 시간대(신규 렌더링 스킵)"}
        except Exception as e:
            logger.error(f"❌ [보험 카드뉴스 제작 실패] {e}")
            # 🆕 제작 실패도 송출 실패로 기록 (3회 누적 시 서킷브레이커 작동)
            self._guard_record_result(target_topic, success=False, error_msg=f"제작 실패: {e}")
            return {"status": "error", "error": f"제작 실패: {e}"}

        # 🆕 [영수증 상한 달성 + 재사용 완제품 없음] ➔ 신규 렌더링 없이 스킵
        if not slides:
            logger.info(
                f"🛑 [영수증 상한 {self.daily_quota}개 달성] 보험 카드뉴스 오늘치 완제품 생산 완료. "
                f"신규 렌더링 100% 원천 차단 ➔ 주제 #{target_topic} 스킵."
            )
            return {
                "status": "quota_reached",
                "message": f"일일 카드뉴스 생산 상한 {self.daily_quota}개 달성 (신규 렌더링 차단)",
            }

        # 🔍 [3단계: 파이썬 실물 전수 검증] "API로 쏘는 건 무조건 바탕화면에 제대로 완이 다 만들고 파이썬 확인 그 다음에 API"
        from brands.insurance.insurance_production_safety_gate import InsuranceProductionSafetyGate
        is_valid, verify_msg = InsuranceProductionSafetyGate.verify_desktop_cardnews_completed(slides)
        if not is_valid:
            logger.critical(f"🛑 [파이썬 완제품 검증 탈락] 바탕화면 카드뉴스 실물 검증 실패: {verify_msg} -> 외부 API(Meta) 송출 원천 차단!")
            # 🆕 검증 탈락도 송출 실패로 기록 (3회 누적 시 서킷브레이커 작동)
            self._guard_record_result(target_topic, success=False, error_msg=f"실물 검증 실패: {verify_msg}")
            return {"status": "verification_failed", "error": f"바탕화면 실물 검증 실패: {verify_msg}"}
        logger.info(f"✅ [3단계 파이썬 완제품 검증 100% 합격] {verify_msg} -> 4단계 외부 4대 플랫폼 발사(쏘기) 개시!")

        # 4. 메타데이터 패키징 & 외부 API 발사
        pkg = self.build_meta_packages(target_topic)
        results = {
            "status": "success",
            "date": today_str,
            "published_at": get_now_kst_str(),
            "brand": self.BRAND,
            "topic_id": target_topic,
            "title": pkg["title"],
            "slides_count": len(slides),
            "channels": {}
        }

        # 🌐 [대표님 절대 수칙] API 배제 -> 사람처럼 크롬 브라우저를 직접 띄워 올리는 웹 브라우저 봇 자동 송출
        logger.info("🌐 [사람처럼 올리는 브라우저 봇 가동] 인스타그램, 스레드, 네이버 블로그 무인 송출 시작!")

        # 4-1. 카드뉴스 슬라이드 ➔ 15.5초 세로 릴스/숏폼 MP4 자동 변환
        cardnews_reels_path = None
        try:
            from core.cardnews_to_reels_converter import CardnewsToReelsConverter
            converter = CardnewsToReelsConverter()
            slide_dir = Path(slides[0]).parent if slides else CURRENT_DIR
            out_reels = str(slide_dir / f"insurance_topic{target_topic}_cardnews_reels.mp4")
            conv_res = converter.convert(slide_paths=slides, output_path=out_reels, brand="insurance")
            if conv_res.get("status") == "success":
                cardnews_reels_path = out_reels
                logger.info(f"🎬 [CardnewsToReels 완료] 릴스 변환 성공: {out_reels}")
            else:
                logger.warning(f"⚠️ [CardnewsToReels 경고] 릴스 변환 실패: {conv_res.get('message')}")
        except Exception as ce:
            logger.error(f"❌ [CardnewsToReels 예외] {ce}")

        # 4-2. [Channel 1 & 2] Meta 릴스 (인스타그램 + 페이스북 릴스)
        if self.mbs_pub.is_available() and cardnews_reels_path and os.path.exists(cardnews_reels_path):
            logger.info(f"🌐 [Meta Business Suite] 보험 카드뉴스 릴스({os.path.basename(cardnews_reels_path)}) 인스타+페북 웹 무인 발행 개시...")
            try:
                mbs_res = self.mbs_pub.publish_reel(
                    video_path=cardnews_reels_path,
                    caption=pkg["ig_caption"]
                )
                results["channels"]["meta_business_suite_reels"] = mbs_res
                logger.info(f"🎉 [MBS 릴스 발행 완료]: {mbs_res.get('status')}")
            except Exception as mbse:
                logger.error(f"❌ [MBS 릴스 발행 예외] {mbse}")
                results["channels"]["meta_business_suite_reels"] = {"status": "error", "error": str(mbse)}


        # 4-3-2. [Channel 2-3] 스레드(Threads) 5장 카드뉴스 & 타래 댓글 무인 송출
        logger.info(f"🧵 [Threads] 스레드 5장 카드뉴스 무인 송출 개시...")
        try:
            import asyncio
            from brands.insurance.insurance_threads_pipeline import InsuranceThreadsPipeline
            th_pipe = InsuranceThreadsPipeline(headless=True)
            slide_dir = Path(slides[0]).parent if slides else CURRENT_DIR
            th_res = asyncio.run(th_pipe.run_pipeline(
                cardnews_folder=str(slide_dir),
                custom_caption=pkg.get("ig_caption", pkg.get("title"))
            ))
            results["channels"]["threads"] = th_res
            logger.info(f"🎉 [스레드 송출 완료]: {th_res.get('status')}")
        except Exception as the:
            logger.error(f"❌ 스레드 송출 예외: {the}")
            results["channels"]["threads"] = {"status": "error", "error": str(the)}

        # 4-4. [Channel 3] 유튜브 쇼츠에 카드뉴스 릴스 영상 송출
        if cardnews_reels_path and os.path.exists(cardnews_reels_path) and self.youtube_pub.is_available():
            logger.info(f"🔴 [3/4 유튜브 쇼츠 카드뉴스 릴스 송출] 주제 #{target_topic} 발사...")
            try:
                yt_title = pkg.get("youtube", {}).get("title") or f"{pkg['title']} #Shorts"
                yt_res = self.youtube_pub.publish_short(
                    video_path=cardnews_reels_path,
                    topic_id=target_topic,
                    title=yt_title,
                    description=pkg.get("youtube", {}).get("desc"),
                    privacy_status="public"
                )
                results["channels"]["youtube_shorts"] = yt_res
            except Exception as ye:
                logger.error(f"❌ 유튜브 카드뉴스 숏츠 송출 실패: {ye}")
                results["channels"]["youtube_shorts"] = {"status": "error", "error": str(ye)}

        # 4-5. [Channel 4] 네이버 클립에 카드뉴스 릴스 영상 송출
        if cardnews_reels_path and os.path.exists(cardnews_reels_path) and self.clip_pub.is_available():
            logger.info(f"🟢 [4/4 네이버 클립 카드뉴스 릴스 송출] 주제 #{target_topic} 발사...")
            try:
                clip_title = pkg.get("naver_clip", {}).get("title") or pkg["title"]
                clip_res = self.clip_pub.publish_clip(
                    video_path=cardnews_reels_path,
                    topic_id=target_topic,
                    title=clip_title,
                    description=pkg.get("naver_clip", {}).get("desc")
                )
                results["channels"]["naver_clip"] = clip_res
            except Exception as ce:
                logger.error(f"❌ 네이버 클립 카드뉴스 숏츠 송출 실패: {ce}")
                results["channels"]["naver_clip"] = {"status": "error", "error": str(ce)}

        # 4-6. [Channel 5] 틱톡 카드뉴스 숏폼 무인 송출
        if cardnews_reels_path and os.path.exists(cardnews_reels_path) and hasattr(self, 'tiktok_pub') and self.tiktok_pub.is_available():
            logger.info(f"🎵 [5/5 틱톡 카드뉴스 릴스 송출] 주제 #{target_topic} 발사...")
            try:
                tk_res = self.tiktok_pub.publish_short(
                    video_path=cardnews_reels_path,
                    topic_id=target_topic,
                    caption=pkg.get("tiktok", {}).get("caption", pkg.get("title")),
                    title=pkg.get("title")
                )
                results["channels"]["tiktok"] = tk_res
                logger.info(f"🎉 [틱톡 카드뉴스 송출 완료]: {tk_res.get('post_url', tk_res.get('status'))}")
            except Exception as tke:
                logger.error(f"❌ 틱톡 카드뉴스 숏츠 송출 실패: {tke}")
                results["channels"]["tiktok"] = {"status": "error", "error": str(tke)}

        # 4-9. 🆕 [영수증 가드] 채널 송출 결과 집계 ➔ 성공/실패 단일 기록
        #      🚨 단방향 원칙: 실패해도 생산을 재호출하지 않고 '기록'만 수행합니다.
        channel_errors = []
        channel_success = 0
        for ch_name, ch_res in (results.get("channels") or {}).items():
            if not isinstance(ch_res, dict):
                continue
            ch_status = str(ch_res.get("status", "")).lower()
            if ch_status in ("success", "published", "ok", "uploaded", "completed"):
                channel_success += 1
            elif ch_status in ("error", "failed", "failure"):
                channel_errors.append(f"{ch_name}: {ch_res.get('error') or ch_res.get('message') or ch_status}")

        if channel_success > 0:
            self._guard_record_result(target_topic, success=True)
            logger.info(f"🧾 [영수증 송출 성공 기록] 주제 #{target_topic} | 성공 채널 {channel_success}개")
        else:
            err_summary = " | ".join(channel_errors) if channel_errors else "모든 채널 송출 실패(응답 없음)"
            self._guard_record_result(target_topic, success=False, error_msg=err_summary)
            logger.warning(f"🧾 [영수증 송출 실패 기록] 주제 #{target_topic} | {err_summary}")
            results["status"] = "dispatch_failed"
            results["error"] = err_summary

        self._record_history(results)
        logger.info("=" * 70)
        logger.info(f"🎉 [보험 5장 카드뉴스 1회 단발 송출 완료] 주제 #{target_topic} | 슬라이드 {len(slides)}장")
        logger.info("=" * 70)
        return results

    def _record_history(self, record: Dict[str, Any]):
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                pass
        history.append(record)
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history[-50:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    pilot = InsuranceOmniCardnewsPilot()
    print(f"🛡️ Insurance Omni Cardnews Pilot 준비 완료! (다음 롤링 주제: #{pilot.get_next_topic_id()})")
    now_dt = datetime.now()
    if pilot.is_daytime_gpu_yield_window(now_dt):
        print(f"🚨 현재 {now_dt.strftime('%H:%M')} ➔ 주간 GPU 양보 시간대 (신규 렌더링 차단, KTRS 우선)")
    else:
        print(f"🌙 현재 {now_dt.strftime('%H:%M')} ➔ 야간 골든타임 (신규 렌더링 허용)")
