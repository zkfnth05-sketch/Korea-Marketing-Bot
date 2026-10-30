# -*- coding: utf-8 -*-
"""
[독립 레고 블록] Stock Omni Shorts Pilot (📈 StockMaster AI 전용 쏘기 직전 1편 제작 & 4대 채널 단발 송출 파일럿)
===================================================================================================================
- 브랜드: StockMaster AI (공식 검색어: '스톡마스터 AI' 띄어쓰기 불변)
- 핵심 원칙 (대표님 절대 수칙):
  1. [쏘기 전 무조건 1편 신선 제작]: 폴더에서 옛날 파일 무단 주워오기 0% 전면 금지!
     정시(스케줄) 도달 시, 이번 순번 주제(예: #1) 숏폼 1편을 그 자리에서 단독 제작 (StockQuantShortsBuilder)
  2. [즉시 1회 단발 발사]: 방금 생성된 따끈한 고유 MP4를 넘겨받아 4대 플랫폼 동시 송출
     - ① 유튜브 쇼츠 (YouTube Shorts Data API v3 + 고정 댓글 링크)
     - ② 네이버 클립 (Naver Clip 스튜디오 Playwright 무인 업로드 -> '초안' 탈출 '공개' 등록)
     - ③ 인스타그램 릴스 (Instagram Reels Meta Graph API)
     - ④ 페이스북 릴스 (Facebook Reels Meta Graph API + 첫 댓글 링크)
  3. [완벽한 메타데이터 패키징]: 제목, 설명문, 카피, 공식 검색어 유도, 4단 티어 해시태그 100% 탑재
  4. [중복 방지 락(Lock)]: 당일 동일 주제 및 동일 영상 중복 송출 0% 원천 차단
  5. [인간 행동 봇과 완전 분리]: 30분 4회 분할 인간 행동(시청/좋아요)은 StockHumanBehaviorBot이 전담 (0 API)

[⚡ 주간 온디맨드 자율 렌더링 가드 (대표님 100% 무인 정시 송출 절대 지침)]
  · 07:00 ~ 23:59 (주간) : 완제품 부재 시 GPUSafetyGuard.wait_for_safe_gpu_entry() 안전 진입 대기 후
                            온디맨드 실시간 렌더링 개시 ➔ 정시 송출 100% 보장 (렌더링 봉쇄 해제)
  · 00:00 ~ 06:59 (야간 골든타임) : 대기 없이 즉시 신규 렌더링 허용
  · 단, 바탕화면에 오늘자 완제품이 이미 존재하면 시간대와 무관하게 즉시 송출 (GPU 소모 0)
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

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
from brands.stock.stock_hashtag_matrix import StockHashtagMatrix
from brands.stock.stock_youtube_bot_publisher import StockYouTubeBotPublisher
from brands.stock.stock_tiktok_publisher import StockTikTokPublisher
from brands.stock.stock_naver_clip_publisher import StockNaverClipPublisher
from brands.stock.stock_mbs_reels_publisher import StockMBSReelsPublisher

# 🆕 [생산/송출 완전 분리 영수증 가드] 일일 쿼터 & 송출 3회 서킷브레이커
from core.receipt_engine.daily_receipt_guard import (
    DailyReceiptGuard,
    DAILY_QUOTAS,
    MAX_DISPATCH_RETRIES,
)

logger = logging.getLogger("StockOmniShortsPilot")


# ==============================================================================
# 🚨 [도메인 예외] 주간 GPU 렌더링 원천 차단
#   - 07:00~23:59 시간대에 신규 렌더링(StockShortsPipeline.produce)을 시도하면 발생
#   - execute_single_slot()에서 포착하여 'daytime_skipped' 상태로 안전 반환
# ==============================================================================
class DaytimeRenderForbidden(RuntimeError):
    """🚨 [주간 GPU 렌더링 원천 차단] 07:00~23:59에는 KTRS에 GPU를 양보하므로 신규 렌더링이 금지됩니다."""

    def __init__(self, message: str = "🚨 [주간 GPU 렌더링 원천 차단] 07:00~23:59 시간대에는 KTRS에 GPU를 양보하므로 신규 렌더링이 금지됩니다."):
        super().__init__(message)
        self.message = message


class StockOmniShortsPilot:
    """📈 StockMaster AI 전용 [쏘기 직전 1편 제작 ➔ 4대 채널 즉시 1회 송출] 통합 관제 파일럿"""

    BRAND = "stock"
    MEDIA_TYPE = "shorts"
    OFFICIAL_KEYWORD = "스톡마스터 AI"
    LANDING_URL = "https://stockmaster-ai.vercel.app/"

    # ==========================================================================
    # 🚨 [주간 GPU 양보 시간대 상수] 07시 ~ 23시 = KTRS 전용 (주식 신규 렌더링 금지)
    #   · DAYTIME_START_HOUR(7) <= now.hour <= DAYTIME_END_HOUR(23) ➔ 차단
    #   · 그 외(00~06) = 야간 골든타임 ➔ 렌더링 허용
    # ==========================================================================
    DAYTIME_START_HOUR = 7
    DAYTIME_END_HOUR = 23

    # 🆕 [실패 주제 쿨다운] 실패한 주제가 무한 재선정되는 것을 막는 냉각 시간(시간 단위)
    FAIL_COOLDOWN_HOURS = 6

    HOOK_TITLES = {
        1: "삼성전자 vs SK하이닉스 HBM 외인 수급 대폭발 ㄷㄷ",
        2: "국내 고배당주(금융지주·맥쿼리) 월배당 시뮬레이션 현실적 치트키",
        3: "코스피·코스닥 세력 체결강도 120% 돌파 급등 유망주 포착",
        4: "코스피200 우량주 vs 코스닥 성장주 직장인 월적립식 복리 비교",
        5: "외인·기관 실시간 쌍끌이 순매수 레이더 포착 종목 TOP 3",
        6: "주식 초보가 100% 물리는 물타기 실수와 AI 손절 탈출 공식",
        7: "저PBR 밸류업 & 고배당 금융주 스크리닝 긴급 공개",
        8: "AI 자동 손절매 & 리스크 가드 퀀트 시스템 실전 운용법"
    }

    def __init__(self):
        self.hashtag_matrix = StockHashtagMatrix()
        self.youtube_pub = StockYouTubeBotPublisher(headless=True)
        self.tiktok_pub = StockTikTokPublisher(headless=True)
        self.clip_pub = StockNaverClipPublisher()
        self.mbs_pub = StockMBSReelsPublisher()
        self.history_file = CURRENT_DIR / "omni_shorts_publish_history.json"
        self.state_file = CURRENT_DIR / "omni_shorts_schedule_state.json"

        # 🆕 [영수증 가드] 일일 쿼터(숏폼 3개) & 송출 3회 서킷브레이커 단일 관제
        self.guard = DailyReceiptGuard()
        self.daily_quota = DAILY_QUOTAS.get(self.MEDIA_TYPE, 3)

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
        """당일 숏폼 생산 쿼터(3개) 잔여 여부. 가드 예외 시 보수적 차단."""
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
        """완제품 확보 시 영수증 봉인. 실패해도 송출 자체는 막지 않음(경고만)."""
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
           어떤 경우에도 생산(produce_fresh_short)을 재호출하지 않습니다.
        """
        try:
            self.guard.record_dispatch_result(
                self.BRAND, self.MEDIA_TYPE, int(topic_id),
                success=success, error_msg=error_msg
            )
        except Exception as re:
            logger.warning(f"⚠️ [영수증 결과 기록 경고] {re}")

    def _guard_auto_scan(self) -> list:
        """바탕화면 당일 완제품 자동 스캔 ➔ 영수증 자동 등록 (쿼터까지만)."""
        try:
            sealed = self.guard.auto_scan_and_seal(self.BRAND, self.MEDIA_TYPE)
            if sealed:
                logger.info(f"🧾 [영수증 자동 스캔] 당일 완제품 {len(sealed)}건 자동 봉인: {sealed}")
            return sealed
        except Exception as ae:
            logger.warning(f"⚠️ [영수증 자동 스캔 경고] {ae}")
            return []

    def _find_any_today_completed_short(self) -> Optional[str]:
        """
        🆕 [쿼터 달성 시 폴백] 주제 번호 무관, '오늘자' 바탕화면 완제품 중 최신 1편 반환.
        - 신규 렌더링 없이 '이미 생산된 완제품'만 재사용 (생산 0%)
        - 오늘자 날짜폴더(today_str 포함) 조건을 반드시 유지하여 과거 파일 재사용을 원천 차단
        - 주식 고유 glob 3종("*32초*" / "*22초*" / "*숏폼*")을 그대로 사용
        """
        today_str = datetime.now().strftime("%Y%m%d")
        desktop_base = Path(os.environ.get("USERPROFILE", "C:/Users/zkfnt")) / "Desktop" / "한국 숏폼_산출물" / "Stock"
        if not desktop_base.exists():
            return None

        candidates = []
        try:
            for folder in desktop_base.iterdir():
                if not folder.is_dir() or today_str not in folder.name:
                    continue
                found_mp4s = (
                    list(folder.glob("*32초*.mp4"))
                    + list(folder.glob("*22초*.mp4"))
                    + list(folder.glob("*숏폼*.mp4"))
                )
                seen_paths = set()
                for mp4 in found_mp4s:
                    if mp4 in seen_paths:
                        continue
                    seen_paths.add(mp4)
                    name_lower = mp4.name.lower()
                    if any(w in name_lower for w in ["10초", "원테이크", "temp", "clip_", "person_"]):
                        continue
                    if mp4.stat().st_size > 2 * 1024 * 1024:
                        candidates.append((mp4.stat().st_mtime, mp4))
        except Exception:
            return None

        if not candidates:
            return None

        candidates.sort(key=lambda x: x[0], reverse=True)
        best = str(candidates[0][1])
        logger.info(f"♻️ [완제품 재사용] 오늘자 기존 완제품 재사용: {best}")
        return best

    # ==========================================================================
    # 🚨 [주간 GPU 양보 판정] 현재 시각이 KTRS 전용 시간대(07~23시)인지 검사
    # ==========================================================================
    def is_daytime_gpu_yield_window(self, now: Optional[datetime] = None) -> bool:
        """현재 시각이 주간 GPU 양보 시간대(07:00~23:59)인지 여부를 반환"""
        now = now or datetime.now()
        return self.DAYTIME_START_HOUR <= now.hour <= self.DAYTIME_END_HOUR

    def get_next_topic_id(self) -> int:
        """
        🔄 [8-Topic LRU Anti-Duplication Ring Buffer]
        - 최근 발행 이력(history)을 전수 역추적하여 가장 오랫동안 송출되지 않은 주제(LRU)를 자동 선정
        - 오늘 이미 송출된 주제는 최우선적으로 배제 (하루 3회 정시 슬롯 간 중복 0% 철통 보장)

        🚨 [결함 수정] 기존 로직은 '한 번도 성공하지 못한 주제'와 '실패한 주제'를
           모두 last_seen=999999 로 부여한 뒤 reverse=True 정렬을 수행했습니다.
           그 결과 실패 주제가 매번 최우선 1순위로 무한 승격되어,
           실패한 주제만 하루 종일 반복 선택되는 역설이 발생했습니다.

        ✅ [수정 원칙]
           1. 성공 이력이 있는 주제: 실제 최근 성공 순번(작을수록 최근)을 사용
           2. 성공 이력이 없는 주제: '미시도'로 간주하여 성공 주제보다 우선하되,
              동일 그룹 내에서는 주제 번호 오름차순으로 결정적(deterministic) 선정
           3. 실패 이력은 승격 근거(999999)로 절대 사용하지 않음
           4. 실패 주제는 FAIL_COOLDOWN_HOURS(6시간) 내 재선정 금지 ➔ 무한 재시도 루프 차단
        """
        all_topics = list(self.HOOK_TITLES.keys())
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
            f"🔄 [주식 숏폼 LRU 자동 선정] 후보군 {fresh_candidates} ➔ 선정 주제: #{chosen_id} "
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

    def produce_fresh_short(self, topic_id: int, slot: Optional[str] = None, subtype: Optional[str] = None) -> Optional[str]:
        """
        🎬 [쏘기 직전 1편 실시간 100% 신선 제작 - 봇 자율 파이프라인]

        [3단계 실행 순서]
          · 1단계: 오늘 완성된 최신 완제품이 이미 바탕화면에 존재하는지 우선 탐색
                   (중복 GPU 렌더링 방지 & 즉각 송출 — 시간대 무관 허용)
          · 2단계: 완제품이 없을 때 현재 시각이 주간(07~23시)이면
                   GPUSafetyGuard.wait_for_safe_gpu_entry()로 GPU 안전 진입을 대기한 뒤
                   온디맨드 실시간 렌더링을 즉시 개시 (100% 무인 정시 송출 절대 지침)
          · 3단계: 야간 골든타임(00~06시)은 대기 없이 즉시 StockShortsPipeline().produce() 신규 렌더링

        🎭 [드라마 슬롯 분기]
          - subtype == "drama" 또는 slot in ("shorts_2", "shorts_3") ➔ 드라마 산출물 폴더만 탐색
          - 그 외 ➔ 기존 일반 숏폼(*32초* / *22초* / *숏폼*) 탐색 100% 유지
        """
        is_drama = (subtype == "drama") or (slot in ["shorts_2", "shorts_3"])
        logger.info("=" * 70)
        logger.info(
            f"🎬 [StockMaster 숏폼 제작/감지] 주제 #{topic_id} 완제품 확인 및 파이프라인 가동... "
            f"(slot={slot or '-'}, subtype={subtype or '-'}, drama={is_drama})"
        )
        logger.info("=" * 70)

        # 0단계: 🆕 [영수증 상한 가드] 당일 생산 쿼터(3개) 달성 시 신규 렌더링 원천 차단
        if not self._guard_can_produce():
            logger.info(
                f"🛑 [영수증 상한 {self.daily_quota}개 달성] 주식 숏폼 오늘치 완제품 생산 완료. "
                f"신규 렌더링 100% 원천 차단."
            )
            # 신규 렌더링 없이 '오늘자 기존 완제품'만 탐색하여 반환 (없으면 None ➔ 상위에서 스킵)
            existing_any = self._find_any_today_completed_short()
            if existing_any:
                logger.info(f"♻️ [신규 렌더링 0%] 오늘자 기존 완제품으로 송출 진행: {existing_any}")
                return existing_any
            logger.warning("🛑 [영수증 상한 달성 + 재사용 가능한 완제품 없음] 신규 렌더링 없이 스킵합니다.")
            return None

        # ------------------------------------------------------------------
        # [1단계] 오늘자 바탕화면 완제품 검색 (기존 로직 100% 유지)
        #   · 완제품이 있으면 GPU 렌더링 0회로 즉시 반환 ➔ 주간에도 송출 가능
        # ------------------------------------------------------------------
        today_str = datetime.now().strftime("%Y%m%d")
        desktop_base = Path(os.environ.get("USERPROFILE", "C:/Users/zkfnt")) / "Desktop" / "한국 숏폼_산출물" / "Stock"

        # 🎭 [드라마 슬롯 전용 탐색] 폴더명에 drama 포함 + 오늘자 + mp4 실물 (2MB 초과)
        if is_drama:
            drama_candidates = []
            if desktop_base.exists():
                for folder in desktop_base.iterdir():
                    if folder.is_dir() and today_str in folder.name and "drama" in folder.name.lower():
                        for mp4 in folder.glob("*.mp4"):
                            name_lower = mp4.name.lower()
                            # 🚨 temp/중간 생성물 배제
                            if any(w in name_lower for w in ["temp", "clip_", "person_"]):
                                continue
                            if mp4.stat().st_size > 2 * 1024 * 1024:
                                drama_candidates.append((mp4.stat().st_mtime, mp4))
            if drama_candidates:
                drama_candidates.sort(key=lambda x: x[0], reverse=True)
                latest_drama = str(drama_candidates[0][1])
                logger.info(f"🎭 [StockMaster 숏폼 드라마 완제품 즉각 확보] 오늘 완성된 드라마 완제품 감지: {latest_drama}")
                # 🆕 기존 완제품도 영수증 봉인 (쿼터 카운트에 반영)
                self._guard_seal(topic_id, latest_drama)
                return latest_drama
            logger.info("🎭 [드라마 완제품 미발견] 오늘자 drama 폴더에 송출 가능한 mp4가 없습니다.")

        # ------------------------------------------------------------------
        # [1단계] 오늘자 바탕화면 완제품 검색 (기존 로직 100% 유지)
        #   · 완제품이 있으면 GPU 렌더링 0회로 즉시 반환 ➔ 주간에도 송출 가능
        # ------------------------------------------------------------------
        if desktop_base.exists():
            topic_str = f"{topic_id:02d}"
            candidates = []
            for folder in desktop_base.iterdir():
                if folder.is_dir() and f"_{topic_str}_" in folder.name and today_str in folder.name:
                    found_mp4s = list(folder.glob("*32초*.mp4")) + list(folder.glob("*22초*.mp4")) + list(folder.glob("*숏폼*.mp4"))
                    seen_paths = set()
                    for mp4 in found_mp4s:
                        if mp4 in seen_paths:
                            continue
                        seen_paths.add(mp4)
                        name_lower = mp4.name.lower()
                        # 🚨 10초, 원테이크, temp 등 중간 생성물은 100% 원천 배제
                        if any(w in name_lower for w in ["10초", "원테이크", "temp", "clip_", "person_"]):
                            continue
                        if mp4.stat().st_size > 2 * 1024 * 1024:
                            candidates.append((mp4.stat().st_mtime, mp4))
            if candidates:
                candidates.sort(key=lambda x: x[0], reverse=True)
                latest_fresh = str(candidates[0][1])
                logger.info(f"✨ [StockMaster 숏폼 완제품 즉각 확보] 오늘 완성된 무결점 완제품 감지: {latest_fresh}")
                # 🆕 기존 완제품도 영수증 봉인 (쿼터 카운트에 반영)
                self._guard_seal(topic_id, latest_fresh)
                return latest_fresh

        # ------------------------------------------------------------------
        # [2단계] 완제품 없음 ➔ 주간(07~23시) 온디맨드 자율 렌더링 (봉쇄 해제)
        #   · 대표님 100% 무인 정시 송출 절대 지침: 밤에 미생산되어 완제품이 없으면
        #     낮 시간대라도 GPUSafetyGuard 안전 진입 대기 후 즉시 실시간 렌더링하여 100% 송출
        # ------------------------------------------------------------------
        now = datetime.now()
        if self.is_daytime_gpu_yield_window(now):
            logger.info(
                f"⚡ [주식 주간 온디맨드 자율 렌더링] 현재 {now.strftime('%H:%M')} 완제품 부재 감지 ➔ "
                f"100% 정시 송출을 위해 GPUSafetyGuard 안전 진입 대기 후 실시간 렌더링을 개시합니다."
            )
            try:
                from core.gpu_safety_guard import GPUSafetyGuard
                GPUSafetyGuard.wait_for_safe_gpu_entry(timeout_sec=120)
                logger.info("✅ [GPUSafetyGuard] 안전 진입 승인 ➔ 주식 온디맨드 렌더링 개시")
            except Exception as ge:
                logger.warning(f"⚠️ GPUSafetyGuard 진입 예외(무시하고 계속): {ge}")

        # ------------------------------------------------------------------
        # [3단계] 신규 렌더링 실행 (야간 골든타임 + 주간 온디맨드 공통 경로)
        # ------------------------------------------------------------------
        logger.info(
            f"🌙 [신규 렌더링 승인] 현재 {now.strftime('%H:%M')} — "
            f"StockShortsPipeline 신규 렌더링을 개시합니다."
        )
        from brands.stock.stock_shorts_pipeline import StockShortsPipeline
        pipeline = StockShortsPipeline()
        output_mp4 = pipeline.produce(topic_id=topic_id, auto_publish=False)
        if output_mp4 and Path(output_mp4).exists():
            logger.info(f"🎉 [StockMaster 숏폼 제작 100% 성공] 방금 생성된 신선한 완제품: {output_mp4}")
            # 🆕 신규 렌더링 성공 ➔ 영수증 봉인
            self._guard_seal(topic_id, str(output_mp4))
            return str(output_mp4)

        raise RuntimeError(f"🚨 [StockMaster] 주제 #{topic_id} 실시간 숏폼 렌더링 실패! 엉뚱한 과거 파일 주워오기 0% 전면 차단 및 발사 즉각 안전 중단.")

    def build_meta_packages(self, topic_id: int, fresh_video: Optional[str] = None, subtype: Optional[str] = None) -> Dict[str, Any]:
        """
        [제미나이 100% 실시간 카피 + 8대 기능 주입 명세 직결] 4대 채널 텍스트 패키지

        🎭 [드라마 편 메타 분기]
          - subtype == "drama" 이거나 파일/폴더명에 drama 포함 ➔ 숏드라마 전용 타이틀 규격 적용
          - 공식 검색어 '스톡마스터 AI' 띄어쓰기 필수 탑재 (대표님 절대 수칙)
        """
        # 🎭 드라마 여부 판정 (subtype 우선, 없으면 파일/폴더명으로 자동 감지)
        is_drama = bool(subtype == "drama")
        if not is_drama and fresh_video:
            try:
                _vp = Path(fresh_video)
                if "drama" in _vp.name.lower() or "drama" in _vp.parent.name.lower():
                    is_drama = True
            except Exception:
                pass

        guide_hook = ''
        guide_tags = ''
        if fresh_video and os.path.exists(fresh_video):
            guide_file = Path(fresh_video).parent / 'SNS_포스팅_가이드.txt'
            if guide_file.exists():
                try:
                    with open(guide_file, 'r', encoding='utf-8', errors='ignore') as gf:
                        for gline in gf.read().split('\n'):
                            if '발화 훅 요약:' in gline:
                                guide_hook = gline.split('발화 훅 요약:', 1)[1].strip()
                            elif '추천 통합 해시태그:' in gline:
                                guide_tags = gline.split('추천 통합 해시태그:', 1)[1].strip()
                except Exception:
                    pass

        # 🎭 [드라마 편] 가이드 부재 시 manifest.json 폴백 조회 (발화 훅/해시태그 보강)
        if is_drama and not guide_hook and fresh_video:
            try:
                manifest_file = Path(fresh_video).parent / 'manifest.json'
                if manifest_file.exists():
                    with open(manifest_file, 'r', encoding='utf-8', errors='ignore') as mf:
                        mdata = json.load(mf)
                    if isinstance(mdata, dict):
                        guide_hook = guide_hook or str(mdata.get("hook") or mdata.get("guide_hook") or "").strip()
                        guide_tags = guide_tags or str(mdata.get("hashtags") or mdata.get("tags_line") or "").strip()
            except Exception:
                pass

        if is_drama:
            # 🎬 숏드라마 전용 타이틀 규격 (공식 검색어 '스톡마스터 AI' 띄어쓰기 필수)
            drama_hook = guide_hook or '잡주 몰빵 -70% 패닉 탈출 vs AI 퀀트'
            main_title = f"[스톡마스터 AI 숏드라마] {drama_hook[:40]}"
            logger.info(f"🎭 [드라마 메타 패키징] {main_title}")
        elif guide_hook:
            main_title = f'[StockMaster AI] {guide_hook[:40]}'
        else:
            main_title = f'[StockMaster AI] 퀀트 주식 AI 분석 #{topic_id}'

        from brands.stock.stock_domestic_sns_copywriter import StockDomesticSNSCopywriter
        copywriter = StockDomesticSNSCopywriter()
        pkg = copywriter.generate_full_package(topic_id=topic_id, topic_title=main_title, media_type='shorts')
        pkg['main_title'] = main_title
        if guide_tags:
            pkg['tags_line'] = guide_tags

        # 🎭 [드라마 편] 4대 채널 패키지 누락 방어 (youtube/tiktok/naver_clip/meta_reels)
        if is_drama:
            if not isinstance(pkg.get("youtube"), dict):
                pkg["youtube"] = {}
            pkg["youtube"].setdefault("title", main_title[:100])
            if not isinstance(pkg.get("tiktok"), dict):
                pkg["tiktok"] = {}
            pkg["tiktok"].setdefault("caption", f"{main_title}\n{pkg.get('tags_line', '')}".strip())
            if not isinstance(pkg.get("naver_clip"), dict):
                pkg["naver_clip"] = {}
            pkg["naver_clip"].setdefault("title", main_title[:100])
            pkg["naver_clip"].setdefault("description", pkg.get("tags_line", ""))
            if not isinstance(pkg.get("meta_reels"), dict):
                pkg["meta_reels"] = {}
            pkg["meta_reels"].setdefault("caption", f"{main_title}\n{pkg.get('tags_line', '')}".strip())
            pkg["is_drama"] = True

        return pkg

    def execute_single_slot(
        self,
        topic_id: Optional[int] = None,
        force: bool = False,
        force_render: bool = False,
        slot: Optional[str] = None,
        subtype: Optional[str] = None,
        video_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        🚀 [정시 1회 단발 실행] 쏘기 직전 1편 제작 ➔ 4대 채널 즉시 1회 발사 ➔ 중복 락

        🎬 [완제품 직행 송출]
          - video_path가 전달되고 실제 파일이 존재하면 새벽 팩토리 생산 완제품을 그대로 수령하여
            produce_fresh_short() 호출을 100% 생략하고 실물 검증 ➔ 4대 채널 송출로 직행 (GPU 소모 0%)

        🚨 [주간 GPU 양보 가드]
          - produce_fresh_short()가 DaytimeRenderForbidden을 발생시키면
            {"status": "daytime_skipped", "message": "주간 GPU 양보 시간대(신규 렌더링 스킵)"} 로 안전 반환
          - 예외가 상위로 전파되어 스케줄러가 죽는 사고를 원천 차단
        """
        target_topic = topic_id or self.get_next_topic_id()
        today_str = datetime.now().strftime("%Y-%m-%d")

        # 0. 🆕 [영수증 자동 스캔] 바탕화면 당일 완제품을 먼저 영수증으로 등록 (쿼터 정확 산정)
        self._guard_auto_scan()

        # 1. 중복 방지 락 검사
        if not force and self.is_already_published_today(target_topic):
            logger.info(f"🛑 [중복 방지 락] 주식 숏폼 주제 #{target_topic}은 오늘 이미 송출되었습니다. 스킵합니다.")
            return {"status": "skipped", "message": f"주제 #{target_topic} 오늘 송출 완료 상태"}

        # 2. 🆕 [서킷브레이커] 송출 가능 판정 (3회 실패 격리 / 중복 송출 차단)
        if not self._guard_can_dispatch(target_topic):
            logger.warning(
                f"🛑 [3회 송출 실패 서킷브레이커] 주식 숏폼 오늘 송출 중단 (데드레터 격리) "
                f"➔ 주제 #{target_topic}"
            )
            return {"status": "circuit_open", "message": "송출 재시도 3회 초과 차단"}

        # 2. 🎬 [완제품 직행] 새벽 팩토리 산출물이 넘어온 경우 재렌더링 0%로 즉시 확보
        fresh_video: Optional[str] = None
        if video_path and Path(str(video_path)).exists():
            fresh_video = str(video_path)
            logger.info(f"✨ [완제품 직행 송출] 새벽 팩토리 생산 완제품 즉각 수령: {fresh_video}")
            # 🆕 완제품 수령 ➔ 영수증 봉인 (쿼터 카운트 반영)
            self._guard_seal(target_topic, fresh_video)
        else:
            if video_path:
                logger.warning(f"⚠️ [완제품 경로 무효] 전달된 video_path가 존재하지 않습니다 ➔ 신규 제작 경로로 폴백: {video_path}")
            # 2-1. 쏘기 직전 1편 신선 제작 (주간 GPU 양보 시간대는 여기서 안전 스킵)
            try:
                fresh_video = self.produce_fresh_short(target_topic, slot=slot, subtype=subtype)
            except DaytimeRenderForbidden as dfe:
                logger.warning(f"🌙 [주간 GPU 양보] 주식 숏폼 주제 #{target_topic} 신규 렌더링 스킵 — {dfe}")
                return {"status": "daytime_skipped", "message": "주간 GPU 양보 시간대(신규 렌더링 스킵)"}
            except Exception as e:
                logger.error(f"❌ [주식 숏폼 제작 실패] {e}")
                # 🆕 제작 실패도 송출 실패로 기록 (3회 누적 시 서킷브레이커 작동)
                self._guard_record_result(target_topic, success=False, error_msg=f"제작 실패: {e}")
                return {"status": "error", "error": f"제작 실패: {e}"}

        # 🆕 [영수증 상한 달성 + 재사용 완제품 없음] ➔ 신규 렌더링 없이 스킵
        if not fresh_video:
            logger.info(
                f"🛑 [영수증 상한 {self.daily_quota}개 달성] 주식 숏폼 오늘치 완제품 생산 완료. "
                f"신규 렌더링 100% 원천 차단 ➔ 주제 #{target_topic} 스킵."
            )
            return {
                "status": "quota_reached",
                "message": f"일일 숏폼 생산 상한 {self.daily_quota}개 달성 (신규 렌더링 차단)",
            }

        # 🔍 [3단계: 파이썬 실물 전수 검증] "API로 쏘는 건 무조건 바탕화면에 제대로 완이 다 만들고 파이썬 확인 그 다음에 API"
        from brands.stock.stock_production_safety_gate import StockProductionSafetyGate
        is_valid, verify_msg = StockProductionSafetyGate.verify_desktop_shorts_completed(fresh_video)
        if not is_valid:
            logger.critical(f"🛑 [파이썬 완제품 검증 탈락] 바탕화면 숏폼 실물 검증 실패: {verify_msg} -> 외부 API(YouTube/Meta/Clip) 송출 원천 차단!")
            # 🆕 검증 탈락도 송출 실패로 기록 (3회 누적 시 서킷브레이커 작동)
            self._guard_record_result(target_topic, success=False, error_msg=f"실물 검증 실패: {verify_msg}")
            return {"status": "verification_failed", "error": f"바탕화면 숏폼 실물 검증 실패: {verify_msg}"}
        logger.info(f"✅ [3단계 파이썬 완제품 검증 100% 합격] {verify_msg} -> 4단계 외부 API 발사(쏘기) 개시!")

        return self.publish_video(video_path=fresh_video, topic_id=target_topic, subtype=subtype, slot=slot)

    def publish_video(self, video_path: str, topic_id: int, subtype: Optional[str] = None, slot: Optional[str] = None) -> Dict[str, Any]:
        """
        🚀 [4대 채널 100% 무인 일체형 송출]
        유튜브 쇼츠, 틱톡, 네이버 클립, 메타 릴스(인스타+페북)에 검증된 완제품 비디오를 즉시 자율 송출

        🎭 [드라마 슬롯 지원] subtype/slot을 메타 패키징까지 전달하여 숏드라마 전용 타이틀 규격을 유지
        """
        fresh_video = str(Path(video_path).resolve())
        target_topic = topic_id
        today_str = datetime.now().strftime("%Y-%m-%d")

        # 4. 메타데이터 패키징 & 외부 API 발사
        pkg = self.build_meta_packages(target_topic, fresh_video, subtype=subtype)
        results = {
            "status": "success",
            "date": today_str,
            "published_at": get_now_kst_str(),
            "brand": self.BRAND,
            "topic_id": target_topic,
            "slot": slot,
            "subtype": subtype,
            "title": pkg["main_title"],
            "video_file": os.path.basename(fresh_video),
            "channels": {}
        }

        # 🌐 [대표님 절대 수칙] API 배제 -> 사람처럼 크롬 브라우저를 직접 띄워 올리는 4대 웹 브라우저 봇 자동 송출
        logger.info("🌐 [사람처럼 올리는 4대 브라우저 봇 가동] 유튜브 스튜디오, 틱톡, 네이버 클립, 메타 비즈니스 사이트 무인 송출 시작!")

        # 1. [Channel 1] 유튜브 쇼츠 브라우저 봇 직접 송출
        logger.info(f"🔴 [1/4 유튜브 쇼츠 브라우저 봇 직접 송출] 주제 #{target_topic} 발사...")
        try:
            yt_res = self.youtube_pub.publish_short(
                video_path=fresh_video,
                topic_id=target_topic,
                title=pkg["youtube"]["title"],
                privacy_status="public"
            )
            results["channels"]["youtube"] = yt_res
        except Exception as ye:
            logger.error(f"❌ 유튜브 송출 실패: {ye}")
            results["channels"]["youtube"] = {"status": "error", "error": str(ye)}

        # 2. [Channel 2] 틱톡 쇼츠 브라우저 봇 무인 직접 송출
        logger.info(f"🎵 [2/4 틱톡 쇼츠 브라우저 봇 직접 송출] 주제 #{target_topic} 발사...")
        try:
            tk_caption = pkg.get("tiktok", {}).get("caption")
            tk_res = self.tiktok_pub.publish_short(
                video_path=fresh_video,
                topic_id=target_topic,
                caption=tk_caption,
                title=pkg.get("main_title")
            )
            results["channels"]["tiktok"] = tk_res
        except Exception as tke:
            logger.error(f"❌ 틱톡 송출 실패: {tke}")
            results["channels"]["tiktok"] = {"status": "error", "error": str(tke)}

        # 3. [Channel 3] 네이버 클립 1회 스튜디오 공개 송출
        logger.info(f"🟢 [3/4 네이버 클립 스튜디오 송출] 주제 #{target_topic} 발사...")
        try:
            clip_res = self.clip_pub.publish_clip(
                video_path=fresh_video,
                topic_id=target_topic,
                title=pkg.get("naver_clip", {}).get("title", pkg.get("main_title", "")),
                description=pkg.get("naver_clip", {}).get("description") or pkg.get("naver_clip", {}).get("desc") or pkg.get("tags_line", "")
            )
            results["channels"]["naver_clip"] = clip_res
        except Exception as ce:
            logger.error(f"❌ 네이버 클립 송출 실패: {ce}")
            results["channels"]["naver_clip"] = {"status": "error", "error": str(ce)}

        # 4. [Channel 4] Meta 릴스(인스타+페북) MBS 브라우저 봇 직접 송출
        logger.info(f"📘 [4/4 Meta 플랫폼 MBS] 숏폼 릴스({os.path.basename(fresh_video)}) 인스타그램 릴스 + 페이스북 동시 송출 개시...")
        try:
            caption_text = pkg.get("meta_reels", {}).get("caption") or pkg.get("tags_line", "")
            mbs_res = self.mbs_pub.publish_reel(
                video_path=fresh_video,
                caption=caption_text
            )
            results["channels"]["meta_reels"] = mbs_res
            logger.info(f"📘 메타 릴스 송출 결과: {mbs_res.get('status')}")
        except Exception as me:
            logger.error(f"❌ 메타 릴스 송출 실패: {me}")
            results["channels"]["meta_reels"] = {"status": "error", "error": str(me)}

        # 8. 🆕 [영수증 가드] 채널 송출 결과 집계 ➔ 성공/실패 단일 기록
        #    🚨 단방향 원칙: 실패해도 생산을 재호출하지 않고 '기록'만 수행합니다.
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

        # 9. 이력 저장
        self._record_history(results)
        return results

    def _record_history(self, record: Dict[str, Any]):
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []
        history.append(record)
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"이력 저장 경고: {e}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="StockOmniShortsPilot Runner")
    parser.add_argument("--topic", type=int, default=None, help="Target topic ID")
    parser.add_argument("--force", action="store_true", help="Force publish ignoring today lock")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    pilot = StockOmniShortsPilot()
    res = pilot.execute_single_slot(topic_id=args.topic, force=args.force)
    print(json.dumps(res, ensure_ascii=False, indent=2))
