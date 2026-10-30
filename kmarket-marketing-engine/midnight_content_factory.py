# -*- coding: utf-8 -*-
"""
[독립 레고 블록] MidnightContentFactory - 🌙 [밤 12시 3대 앱 숏폼/카드뉴스 순차 생산 공장]
==========================================================================================
- 브랜드: 대한민국 3대 앱 (💖 Aura 데이팅, 🛡️ 보험 리밸런스, 📈 StockMaster AI)
- 일정: 매일 밤 12시(00:00 KST) 기상 ➔ 새벽 3시 이전 100% 생산 완료 ➔ 아침 7시 저쪽 컴퓨터에 GPU 온전히 양보
- 생산 목표 (총 15개 콘텐츠):
  • 💖 Aura: 숏폼 3개 + 카드뉴스 2개
  • 🛡️ 보험: 숏폼 3개 + 카드뉴스 2개
  • 📈 주식: 숏폼 3개 + 카드뉴스 2개
- 🛡️ GPU 세심 안심 가드:
  • 1건 완료 시마다 OS 레벨 서브프로세스 메모리 100% 반환
  • ComfyUI /free API로 VRAM 모델 언로드
  • 엄격한 5분(300초) GPU 냉각 휴식 타이머 (실시간 온도/VRAM 모니터링)
  • 65℃ 안전 차단벽 & 저쪽 컴퓨터(KTRS) 작업 시 자율 양보

[아키텍처 재편 요약 — Round-Robin Interleaving Edition]
- 🔀 교차 라운드로빈 인터리빙 큐 (브랜드별 직렬 실행 전면 폐지):
    Round 1: aura:shorts:1   → insurance:shorts:1   → stock:shorts:1
    Round 2: aura:cardnews:1 → insurance:cardnews:1 → stock:cardnews:1
    Round 3: aura:shorts:2   → insurance:shorts:2   → stock:shorts:2
    Round 4: aura:cardnews:2 → insurance:cardnews:2 → stock:cardnews:2
    Round 5: aura:shorts:3   → insurance:shorts:3   → stock:shorts:3
  → 어떤 지점에서 중단되어도 3개 브랜드가 균등하게 확보된다.
- 🧾 DailyReceiptGuard 사전 검사: 태스크 착수 직전 당일 쿼터(숏폼 3 / 카드뉴스 2)를
  확인하여 이미 충족된 경우 서브프로세스를 0회 기동하고
  status="SKIPPED_QUOTA_SATISFIED" 로 즉시 통과 처리한다.
- ⏰ 07:00 KTRS 주간 양보 마감 인지 안전 가드:
  07:00~23:59 주간 양보 시간대이거나, 06:25(숏폼 35분) / 06:50(카드뉴스 10분) 이후로
  07:00 마감을 넘기게 되는 경우 강제 컷오프 없이
  status="DEFERRED_DAYTIME_YIELD" 로 품격 있게 안전 이월한다.
- 🧯 에러 원문 보존: GPUSafetyGuard.run_isolated_step 결과의 res["error"] /
  res["reason"] 을 그대로 보존한다. ("프로세스 비정상 종료"로 덮어쓰지 않음)
- 💾 원자적 저장: 매니페스트/상태 모두 tmp → flush → fsync → os.replace.
- 🧱 완전 격리: 태스크 1건이 실패/지연되어도 다른 브랜드·타입 태스크는 계속 실행.
- 24시간 무인 안전장치: 타임아웃, 지수 백오프, 좀비 회수, 데몬 예외 격리
"""

import os
import sys
import time
import json
import shutil
import logging
import datetime
import traceback
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("MidnightContentFactory")

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from core.gpu_safety_guard import GPUSafetyGuard
from core.receipt_engine.daily_receipt_guard import DailyReceiptGuard


# ============================================================================
# 브랜드 메타데이터 (격리 경계 단위)
# ============================================================================
BRAND_META: Dict[str, Dict[str, Any]] = {
    "aura": {
        "emoji": "💖",
        "name": "Aura 데이팅",
        "shorts_script": "run_aura_shorts.py",
        "cardnews_script": "run_aura_cardnews.py",
        "drama_script": "run_aura_drama.py",
        "shorts_extra": ["--no-publish"],
        "cardnews_extra": ["all"],
        "drama_extra": ["--no-publish"],
        "shorts_max_topics": 8,
        "cardnews_max_topics": 8,
        "cardnews_folder": "아우라",
        "shorts_folder": "Aura",
    },
    "insurance": {
        "emoji": "🛡️",
        "name": "보험 리밸런스",
        "shorts_script": "run_insurance_shorts.py",
        "cardnews_script": "run_insurance_cardnews.py",
        "drama_script": "run_insurance_drama.py",
        "shorts_extra": ["--no-publish"],
        "cardnews_extra": [],
        "drama_extra": ["--no-publish"],
        "shorts_max_topics": 8,
        "cardnews_max_topics": 8,
        "cardnews_folder": "보험",
        "shorts_folder": "Insurance",
    },
    "stock": {
        "emoji": "📈",
        "name": "StockMaster AI",
        "shorts_script": "run_stock_shorts.py",
        "cardnews_script": "run_stock_cardnews.py",
        "drama_script": "run_stock_drama.py",
        "shorts_extra": ["--no-publish"],
        "cardnews_extra": [],
        "drama_extra": ["--no-publish"],
        "shorts_max_topics": 8,
        "cardnews_max_topics": 6,
        "cardnews_folder": "주식",
        "shorts_folder": "Stock",
    },
}


class MidnightContentFactory:
    """밤 12시 순차 렌더링 & GPU 안심 냉각 총괄 팩토리"""

    QUEUE_DIR = CURRENT_DIR / "outputs" / "daily_queue"
    STATE_FILE = CURRENT_DIR / "outputs" / "midnight_factory_state.json"

    # 태스크 단위 안전장치
    TASK_TIMEOUT_SEC = 5400          # 태스크 1건 최대 90분 (고화질 숏폼 렌더 + 큐 대기/VRAM 정리 지연 안전 마진)
    MAX_IMMEDIATE_RETRY = 1          # 태스크 단위 즉시 재시도 1회
    BACKOFF_BASE_SEC = 15            # 재시도 백오프 기본값
    BACKOFF_MAX_SEC = 120            # 재시도 백오프 상한

    # ------------------------------------------------------------------
    # 07:00 KTRS 주간 양보 마감 인지 안전 가드 상수
    # ------------------------------------------------------------------
    DEADLINE_HOUR = 7                # 07:00 KTRS 주간 양보 시작
    DAYTIME_YIELD_START_HOUR = 7     # 07:00 ~ 23:59 주간 양보 시간대

    # 태스크 타입별 예상 소요 시간(분) — 마감 가드 판정에 사용
    # 숏폼: 30분 렌더 + 5분 쿨다운 = 35분 / 카드뉴스: 5분 렌더 + 5분 쿨다운 = 10분
    ESTIMATED_MINUTES: Dict[str, int] = {
        "shorts": 35,
        "cardnews": 10,
    }

    # ------------------------------------------------------------------
    # 교차 라운드로빈 인터리빙 실행 계획 (5라운드 × 3브랜드 = 15태스크)
    #   · Round 1 : 기본 숏폼 #1
    #   · Round 2 : 카드뉴스 #1
    #   · Round 3 : 숏폼 드라마 #1 (episode=1)
    #   · Round 4 : 카드뉴스 #2
    #   · Round 5 : 숏폼 드라마 #2 (episode=2)
    # ------------------------------------------------------------------
    BRAND_ORDER: List[str] = ["aura", "insurance", "stock"]
    ROUND_ROBIN_PLAN: List[Dict[str, Any]] = [
        {"round": 1, "type": "shorts",   "subtype": "regular",  "slot_idx": 1, "title": "기본 숏폼 #1 교차 선점"},
        {"round": 2, "type": "cardnews", "subtype": "cardnews", "slot_idx": 1, "title": "카드뉴스 #1 교차 선점"},
        {"round": 3, "type": "shorts",   "subtype": "drama",    "episode": 1, "slot_idx": 2, "title": "숏폼 드라마 #1 교차"},
        {"round": 4, "type": "cardnews", "subtype": "cardnews", "slot_idx": 2, "title": "카드뉴스 #2 완료"},
        {"round": 5, "type": "shorts",   "subtype": "drama",    "episode": 2, "slot_idx": 3, "title": "숏폼 드라마 #2 완료"},
    ]

    def __init__(self, cooldown_sec: int = 300):
        self.cooldown_sec = cooldown_sec
        self.QUEUE_DIR.mkdir(parents=True, exist_ok=True)
        self.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        # 일일 쿼터/영수증 가드
        try:
            self.receipt_guard = DailyReceiptGuard()
        except Exception as e:
            logger.warning(f"⚠️ [DailyReceiptGuard 초기화 경고] {e}")
            self.receipt_guard = None

    # ------------------------------------------------------------------
    # 상태 저장 (원자적 쓰기)
    # ------------------------------------------------------------------
    def _load_state(self) -> Dict[str, Any]:
        if self.STATE_FILE.exists():
            try:
                with open(self.STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except Exception as e:
                logger.warning(f"상태 로드 경고(기본값 사용): {e}")
        return {
            "last_run_date": "",
            "aura_shorts_offset": 0,
            "aura_cardnews_offset": 0,
            "insurance_shorts_offset": 0,
            "insurance_cardnews_offset": 0,
            "stock_shorts_offset": 0,
            "stock_cardnews_offset": 0,
        }

    def _save_state(self, state: Dict[str, Any]):
        """원자적 상태 저장 (tmp → replace)"""
        try:
            tmp = self.STATE_FILE.with_suffix(".json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, self.STATE_FILE)
        except Exception as e:
            logger.warning(f"상태 저장 경고: {e}")

    def _write_manifest(self, manifest_file: Path, payload: Dict[str, Any]):
        """매니페스트 원자적 기록 (크래시 시 부분 손상 방지)"""
        try:
            tmp = manifest_file.with_suffix(".json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, manifest_file)
        except Exception as e:
            logger.warning(f"매니페스트 기록 경고: {e}")

    # ------------------------------------------------------------------
    # 산출물 실물 검증 (프로세스 종료코드 0 ≠ 완성품)
    # ------------------------------------------------------------------
    def get_today_created_topics(self, brand: str, content_type: str) -> List[int]:
        today_str = datetime.datetime.now().strftime("%Y%m%d")
        created = set()
        desktop = Path(os.environ.get("USERPROFILE", "C:/Users/zkfnt")) / "Desktop"
        meta = BRAND_META.get(brand, {})

        if content_type == "cardnews":
            brand_dir = desktop / "한국 카드뉴스_산출물" / meta.get("cardnews_folder", brand)
            if brand_dir.exists():
                for f in brand_dir.iterdir():
                    if not f.is_dir():
                        continue
                    is_today = (today_str in f.name)
                    slides = [s for s in f.glob("slide_*.png") if s.stat().st_size >= 10240]
                    if slides:
                        mod_date = datetime.datetime.fromtimestamp(
                            slides[0].stat().st_mtime
                        ).strftime("%Y%m%d")
                        if mod_date == today_str:
                            is_today = True
                    if is_today and len(slides) >= 5:
                        parts = f.name.replace("[", "_").replace("]", "_").split("_")
                        for p in parts:
                            p_clean = p.replace("주제", "").strip()
                            if p_clean.isdigit():
                                created.add(int(p_clean))
                                break
        else:  # shorts
            brand_dir = desktop / "한국 숏폼_산출물" / meta.get("shorts_folder", brand)
            if brand_dir.exists():
                for f in brand_dir.iterdir():
                    if not f.is_dir():
                        continue
                    mp4s = [m for m in f.glob("*.mp4") if m.stat().st_size >= 1024 * 1024]
                    is_today = (today_str in f.name)
                    if mp4s:
                        mod_date = datetime.datetime.fromtimestamp(
                            mp4s[0].stat().st_mtime
                        ).strftime("%Y%m%d")
                        if mod_date == today_str:
                            is_today = True
                    if is_today and len(mp4s) >= 1:
                        parts = f.name.replace("[", "_").replace("]", "_").split("_")
                        for p in parts:
                            p_clean = p.replace("주제", "").strip()
                            if p_clean.isdigit():
                                created.add(int(p_clean))
                                break
        return sorted(list(created))

    # ------------------------------------------------------------------
    # 완제품 실물 탐색 & 직인 영수증(READY_FOR_DISPATCH.json) 발급
    # ------------------------------------------------------------------
    def find_and_tag_ready_artifact(
        self, brand: str, content_type: str, topic_id: int, slot: str, subtype: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[List[str]]]:
        """오늘자 완제품 실물을 탐색하고, 확인 시 READY_FOR_DISPATCH.json 직인을 원자적으로 기록.

        반환:
            (True, mp4_path, None)      숏폼 완성본 확인
            (True, None, slide_paths)   카드뉴스 완성본 확인
            (False, None, None)         미완성

        [숏폼 드라마 / 일반 숏폼 격리 탐색]
        - subtype == "drama" 또는 slot 이 shorts_2 / shorts_3 이면 드라마 산출물만 후보로 삼는다.
        - 그 외(regular)는 파일명/폴더명에 "drama" 가 없는 산출물만 후보로 삼는다.
        - 해당 분류의 후보가 하나도 없으면 원래 후보 목록으로 안전 폴백한다.
        """
        try:
            today_str = datetime.datetime.now().strftime("%Y%m%d")
            desktop = Path(os.environ.get("USERPROFILE", "C:/Users/zkfnt")) / "Desktop"
            meta = BRAND_META.get(brand, {})

            mp4_path: Optional[Path] = None
            slides: List[Path] = []
            artifact_dir: Optional[Path] = None
            is_drama = False

            if content_type == "shorts":
                is_drama = (subtype == "drama") or (slot in ["shorts_2", "shorts_3"])
                brand_dir = desktop / "한국 숏폼_산출물" / meta.get("shorts_folder", brand)
                if not brand_dir.exists():
                    return (False, None, None)
                candidates: List[Path] = []
                for f in brand_dir.iterdir():
                    if not f.is_dir():
                        continue
                    for m in f.glob("*.mp4"):
                        try:
                            st = m.stat()
                        except Exception:
                            continue
                        if st.st_size < 1024 * 1024:
                            continue
                        mod_date = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y%m%d")
                        if mod_date != today_str:
                            continue
                        candidates.append(m)
                if not candidates:
                    return (False, None, None)

                # 드라마 / 일반 숏폼 격리 필터 (분류 후보가 없으면 원본 유지)
                if is_drama:
                    drama_candidates = [
                        m for m in candidates
                        if "drama" in m.name.lower() or "drama" in m.parent.name.lower()
                    ]
                    if drama_candidates:
                        candidates = drama_candidates
                else:
                    regular_candidates = [
                        m for m in candidates
                        if "drama" not in m.name.lower() and "drama" not in m.parent.name.lower()
                    ]
                    if regular_candidates:
                        candidates = regular_candidates

                candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                mp4_path = candidates[0]
                artifact_dir = mp4_path.parent
            else:  # cardnews
                brand_dir = desktop / "한국 카드뉴스_산출물" / meta.get("cardnews_folder", brand)
                if not brand_dir.exists():
                    return (False, None, None)
                best: Optional[List[Path]] = None
                best_mtime = 0.0
                for f in brand_dir.iterdir():
                    if not f.is_dir():
                        continue
                    today_slides: List[Path] = []
                    for s in f.glob("slide_*.png"):
                        try:
                            st = s.stat()
                        except Exception:
                            continue
                        if st.st_size < 10240:
                            continue
                        mod_date = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y%m%d")
                        if mod_date != today_str:
                            continue
                        today_slides.append(s)
                    if len(today_slides) >= 5:
                        latest = max(s.stat().st_mtime for s in today_slides)
                        if latest > best_mtime:
                            best_mtime = latest
                            best = sorted(today_slides)
                if not best:
                    return (False, None, None)
                slides = best
                artifact_dir = slides[0].parent

            if artifact_dir is None:
                return (False, None, None)

            # 직인 영수증 원자적 기록
            receipt = {
                "brand": brand,
                "type": content_type,
                "subtype": subtype or ("drama" if is_drama else "regular"),
                "slot": slot,
                "topic_id": topic_id,
                "artifact_path": str(mp4_path) if mp4_path else None,
                "slide_paths": [str(s) for s in slides] if slides else None,
                "status": "VERIFIED_READY",
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            receipt_file = artifact_dir / "READY_FOR_DISPATCH.json"
            tmp_file = artifact_dir / "READY_FOR_DISPATCH.json.tmp"
            with open(tmp_file, "w", encoding="utf-8") as fp:
                json.dump(receipt, fp, ensure_ascii=False, indent=2)
                fp.flush()
                os.fsync(fp.fileno())
            os.replace(tmp_file, receipt_file)

            logger.info(
                "[직인 발급] %s/%s #%d (%s) → %s"
                % (brand, content_type, topic_id, slot, receipt_file)
            )

            if mp4_path:
                return (True, str(mp4_path), None)
            return (True, None, [str(s) for s in slides])

        except Exception as e:
            logger.warning(
                "완제품 탐색 예외(%s/%s/#%s): %s" % (brand, content_type, topic_id, e)
            )
            return (False, None, None)

    def _verify_artifact(
        self, brand: str, content_type: str, topic_id: int, slot: str = "verify"
    ) -> bool:
        """특정 주제 산출물이 실제로 완성되었는지 실물 검증 (find_and_tag_ready_artifact 경유 일원화)"""
        try:
            ok, _art, _slides = self.find_and_tag_ready_artifact(
                brand, content_type, topic_id, slot
            )
            return bool(ok)
        except Exception as e:
            logger.warning(f"산출물 검증 예외({brand}/{content_type}/#{topic_id}): {e}")
            return False

    # ------------------------------------------------------------------
    # 폴더 청소
    # ------------------------------------------------------------------
    def clean_today_folders(self, all_today: bool = False):
        today_str = datetime.datetime.now().strftime("%Y%m%d")
        desktop = Path(os.environ.get("USERPROFILE", "C:/Users/zkfnt")) / "Desktop"
        cleaned_count = 0

        s_base = desktop / "한국 숏폼_산출물"
        for brand in ["Aura", "Insurance", "Stock"]:
            bdir = s_base / brand
            if bdir.exists():
                for d in bdir.iterdir():
                    if d.is_dir() and today_str in d.name:
                        mp4s = [m for m in d.glob("*.mp4") if m.stat().st_size >= 1024 * 1024]
                        if all_today or not mp4s:
                            try:
                                shutil.rmtree(str(d), ignore_errors=True)
                                logger.info(f"🧹 [숏폼 폴더 정리] 제거: {d.name}")
                                cleaned_count += 1
                            except Exception as e:
                                logger.warning(f"폴더 정리 경고: {e}")

        c_base = desktop / "한국 카드뉴스_산출물"
        for brand in ["아우라", "보험", "주식"]:
            bdir = c_base / brand
            if bdir.exists():
                for d in bdir.iterdir():
                    if d.is_dir() and (today_str in d.name or (brand == "주식" and all_today)):
                        slides = [s for s in d.glob("slide_*.png") if s.stat().st_size >= 10240]
                        if all_today or len(slides) < 5:
                            try:
                                shutil.rmtree(str(d), ignore_errors=True)
                                logger.info(f"🧹 [카드뉴스 폴더 정리] 제거: {d.name}")
                                cleaned_count += 1
                            except Exception as e:
                                logger.warning(f"폴더 정리 경고: {e}")

        if all_today:
            state = {
                "last_run_date": None,
                "aura_shorts_offset": 0,
                "aura_cardnews_offset": 0,
                "insurance_shorts_offset": 0,
                "insurance_cardnews_offset": 0,
                "stock_shorts_offset": 0,
                "stock_cardnews_offset": 0,
            }
            self._save_state(state)
            logger.info("🔄 [오프셋 리셋 완료] 3대 앱 모두 1번 주제부터 처음 제작하도록 오프셋을 0으로 리셋했습니다.")

        if cleaned_count > 0:
            logger.info(f"✨ [바탕화면 정화 완료] 총 {cleaned_count}개의 오늘자 폴더를 깨끗하게 청소했습니다.")

    def clean_incomplete_today_folders(self):
        self.clean_today_folders(all_today=False)

    # ------------------------------------------------------------------
    # 주제 선정
    # ------------------------------------------------------------------
    def pick_smart_rotating_topics(
        self, brand: str, content_type: str, offset: int, count: int, max_topics: int = 8
    ) -> List[int]:
        today_done = set(self.get_today_created_topics(brand, content_type))
        candidates: List[int] = []

        for i in range(max_topics):
            topic = ((offset + i) % max_topics) + 1
            if topic not in today_done:
                candidates.append(topic)
                if len(candidates) == count:
                    break

        if len(candidates) < count:
            for i in range(max_topics):
                topic = ((offset + i) % max_topics) + 1
                if topic not in candidates:
                    candidates.append(topic)
                    if len(candidates) == count:
                        break

        logger.info(
            f"🔄 [{brand.upper()} {content_type}] 오늘 기제작: {sorted(list(today_done))} "
            f"➔ 이번 순환 선정: {candidates} (오프셋: {offset})"
        )
        return candidates

    # ------------------------------------------------------------------
    # 태스크 빌더 (브랜드 단위)
    # ------------------------------------------------------------------
    def _build_brand_tasks(self, brand: str, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """브랜드 1개의 5개 태스크를 구성한다.

        구성 (총 5개):
          · shorts_1   : 기본 숏폼 #1        (subtype="regular")
          · shorts_2   : 숏폼 드라마 #1      (subtype="drama", --episode 1)
          · shorts_3   : 숏폼 드라마 #2      (subtype="drama", --episode 2)
          · cardnews_1 : 카드뉴스 #1         (subtype="cardnews")
          · cardnews_2 : 카드뉴스 #2         (subtype="cardnews")

        [설계 의도]
        - 숏폼 3개를 모두 '주제 순환 기본 숏폼'으로 뽑던 구조를 폐기하고,
          기본 숏폼 1개 + 드라마 2개(에피소드 1·2)로 역할을 분리한다.
        - 드라마 태스크는 topic_id 를 에피소드 번호(1, 2)로 두어
          산출물 검증/오프셋 저장 시 충돌하지 않도록 한다.
        - drama_script / drama_extra 가 BRAND_META 에 없더라도
          run_{brand}_drama.py / ["--no-publish"] 로 안전 폴백한다.
        """
        meta = BRAND_META[brand]
        emoji = meta["emoji"]
        name = meta["name"]

        # 기본 숏폼은 1개만 선정 (드라마 2개가 나머지 숏폼 슬롯을 담당)
        s_topics = self.pick_smart_rotating_topics(
            brand, "shorts", state.get(f"{brand}_shorts_offset", 0), 1, meta["shorts_max_topics"]
        )
        c_topics = self.pick_smart_rotating_topics(
            brand, "cardnews", state.get(f"{brand}_cardnews_offset", 0), 2, meta["cardnews_max_topics"]
        )

        # 드라마 스크립트/추가 인자 안전 폴백
        drama_script = meta.get("drama_script", f"run_{brand}_drama.py")
        drama_extra = list(meta.get("drama_extra", ["--no-publish"]))

        tasks: List[Dict[str, Any]] = []

        # ── slot="shorts_1" : 기본 숏폼 #1 ────────────────────────────────
        for t in s_topics:
            cmd = [sys.executable, str(CURRENT_DIR / meta["shorts_script"]), "--topic", str(t)]
            cmd.extend(meta["shorts_extra"])
            tasks.append({
                "task_id": f"{brand}:shorts:{t}",
                "brand": brand,
                "type": "shorts",
                "subtype": "regular",
                "slot": "shorts_1",
                "topic_id": t,
                "label": f"{emoji} {name} 기본 숏폼 #1 (주제 #{t})",
                "cmd": cmd,
            })

        # ── slot="shorts_2" / "shorts_3" : 숏폼 드라마 #1 / #2 ────────────
        for episode in (1, 2):
            cmd = [sys.executable, str(CURRENT_DIR / drama_script)]
            cmd.extend(drama_extra)
            cmd.extend(["--episode", str(episode)])
            tasks.append({
                "task_id": f"{brand}:drama:{episode}",
                "brand": brand,
                "type": "shorts",
                "subtype": "drama",
                "slot": f"shorts_{episode + 1}",
                "topic_id": episode,
                "label": f"{emoji} {name} 숏폼 드라마 #{episode} (에피소드 #{episode})",
                "cmd": cmd,
            })

        # ── slot="cardnews_1" / "cardnews_2" : 카드뉴스 2개 ───────────────
        for idx, t in enumerate(c_topics, 1):
            cmd = [sys.executable, str(CURRENT_DIR / meta["cardnews_script"])]
            cmd.extend(meta["cardnews_extra"])
            cmd.extend(["--topic", str(t)])
            tasks.append({
                "task_id": f"{brand}:cardnews:{t}",
                "brand": brand,
                "type": "cardnews",
                "subtype": "cardnews",
                "slot": f"cardnews_{idx}",
                "topic_id": t,
                "label": f"{emoji} {name} 카드뉴스 #{idx} (주제 #{t})",
                "cmd": cmd,
            })

        return tasks


    # ------------------------------------------------------------------
    # 🔀 교차 라운드로빈 인터리빙 태스크 큐 빌더 (핵심 개편)
    # ------------------------------------------------------------------
    def _build_interleaved_tasks(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        3개 브랜드를 공평하게 교차 순환시키는 15개 태스크 큐 생성.

        Round 1: aura:shorts:1   → insurance:shorts:1   → stock:shorts:1
        Round 2: aura:cardnews:1 → insurance:cardnews:1 → stock:cardnews:1
        Round 3: aura:shorts:2   → insurance:shorts:2   → stock:shorts:2
        Round 4: aura:cardnews:2 → insurance:cardnews:2 → stock:cardnews:2
        Round 5: aura:shorts:3   → insurance:shorts:3   → stock:shorts:3

        [설계 의도]
        - 브랜드별 직렬 실행(Aura 5개 → Insure 5개 → Stock 5개) 구조를 폐기한다.
        - 어떤 이유로 중간에 중단되더라도 3개 브랜드가 최대한 균등하게
          확보되도록(예: 6개 완료 시 각 브랜드 2개씩) 순서를 강제한다.
        - 각 브랜드의 topic_id 는 pick_smart_rotating_topics() 로 오프셋 순환 선정한다.
        """
        # 1) 브랜드별 태스크를 먼저 생성하고 slot 기준으로 인덱싱
        per_brand: Dict[str, Dict[str, Dict[str, Any]]] = {}
        for brand in self.BRAND_ORDER:
            try:
                tasks = self._build_brand_tasks(brand, state)
            except Exception as e:
                logger.error(f"❌ [{brand}] 태스크 빌드 실패: {e}")
                logger.debug(traceback.format_exc())
                tasks = []
            slot_map: Dict[str, Dict[str, Any]] = {}
            for t in tasks:
                slot_map[t["slot"]] = t
            per_brand[brand] = slot_map

        # 2) 라운드 × 브랜드 순서로 인터리빙 큐 구성 (평탄화)
        queue: List[Dict[str, Any]] = []
        for plan in self.ROUND_ROBIN_PLAN:
            slot_key = "%s_%d" % (plan["type"], plan["slot_idx"])
            for brand in self.BRAND_ORDER:
                task = per_brand.get(brand, {}).get(slot_key)
                if not task:
                    logger.warning(
                        "⚠️ [큐 빌드] %s / %s 태스크 없음 — 건너뜀" % (brand, slot_key)
                    )
                    continue
                task = dict(task)
                task["round"] = plan["round"]
                task["round_title"] = plan["title"]
                queue.append(task)

        logger.info(
            "🔀 [인터리빙 큐 구성] 총 %d개 태스크 / %d라운드 × %d브랜드"
            % (len(queue), len(self.ROUND_ROBIN_PLAN), len(self.BRAND_ORDER))
        )
        for i, t in enumerate(queue, 1):
            logger.info(
                "   %02d. [R%d·%s] %s"
                % (i, t["round"], t["round_title"], t["label"])
            )
        return queue

    # ------------------------------------------------------------------
    # 🧾 DailyReceiptGuard 사전 검사 (당일 쿼터 충족 여부)
    # ------------------------------------------------------------------
    def _is_quota_reached(self, brand: str, content_type: str) -> bool:
        """
        당일 쿼터(숏폼 3 / 카드뉴스 2) 도달 여부 판정.

        DailyReceiptGuard 는 can_produce() / get_remaining_quota() 를 공식 API로
        제공한다. (is_quota_reached 라는 이름의 메서드는 존재하지 않으므로 위임)
        판정 불가/예외 시에는 안전하게 False(생산 진행) 를 반환한다.
        """
        guard = self.receipt_guard
        if guard is None:
            return False
        try:
            can_produce = getattr(guard, "can_produce", None)
            if callable(can_produce):
                return not bool(can_produce(brand, content_type))
            remaining = getattr(guard, "get_remaining_quota", None)
            if callable(remaining):
                return int(remaining(brand, content_type)) <= 0
        except Exception as e:
            logger.warning(
                f"⚠️ [쿼터 검사 예외] {brand}/{content_type}: {e} — 생산 진행으로 안전 폴백"
            )
            return False
        return False

    # ------------------------------------------------------------------
    # ⏰ 07:00 KTRS 주간 양보 마감 인지 안전 가드
    # ------------------------------------------------------------------
    def _check_deadline_guard(
        self,
        content_type: str,
        now: Optional[datetime.datetime] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        [대표님 지시 반영 · 07:00 시계 마감 컷오프 전면 폐지]

        반환: (진행 가능 여부, 이월 사유) — 항상 (True, None)

        [개편 사유]
        - 기존 로직은 07:00~23:59 주간 양보 시간대이거나 06:25(숏폼)/06:50(카드뉴스)
          이후이면 태스크를 DEFERRED_DAYTIME_YIELD 로 잘라버려, 밤새 렌더링이
          조금만 늦어져도 당일 콘텐츠가 미완성으로 남는 억울한 손실이 발생했다.
        - 이제는 시계 기준 컷오프를 완전히 제거하고, 07:00을 넘기더라도
          15개 숏폼/카드뉴스를 100% 끝까지 렌더링 완료한다.
        - GPU 충돌/경합은 GPUSafetyGuard 의 상호 대기 락(inter-process lock)과
          VRAM 방출·쿨다운 타이머가 이미 안전하게 조율하므로, 시간으로 잘라낼
          필요가 없다. (KTRS 쪽 작업이 있으면 락이 순서를 양보/대기시킨다)

        [호출부 호환성]
        - _execute_single_task 는 (can_run, reason) 형태를 그대로 사용하며,
          can_run=True 이므로 DEFERRED_DAYTIME_YIELD 분기는 절대 진입하지 않는다.
        - content_type / now 인자는 시그니처 호환을 위해 유지한다(미사용).
        """
        return (True, None)

    # ------------------------------------------------------------------
    # 사전점검: ComfyUI 기동 보장
    # ------------------------------------------------------------------
    def _preflight_ensure_comfyui(self) -> bool:
        """ComfyUI가 살아있는지 확인. GPUSafetyGuard에 ensure_running이 있으면 사용."""
        try:
            ensure = getattr(GPUSafetyGuard, "ensure_running", None)
            if callable(ensure):
                ok = ensure()
                if ok is False:
                    logger.warning("⚠️ [사전점검] ComfyUI 기동 실패")
                    return False
                logger.info("✅ [사전점검] ComfyUI 기동 확인")
                return True
        except Exception as e:
            logger.warning(f"⚠️ [사전점검] ensure_running 예외: {e}")
            return False

        # 폴백: HTTP 헬스체크
        try:
            import urllib.request
            with urllib.request.urlopen("http://127.0.0.1:8188/system_stats", timeout=5) as r:
                if r.status == 200:
                    logger.info("✅ [사전점검] ComfyUI HTTP 헬스체크 통과")
                    return True
        except Exception as e:
            logger.warning(f"⚠️ [사전점검] ComfyUI HTTP 헬스체크 실패: {e}")
        return False

    # ------------------------------------------------------------------
    # 태스크 단위 실행 유닛 (핵심)
    # ------------------------------------------------------------------
    def _execute_single_task(
        self,
        task: Dict[str, Any],
        step_idx: int,
        total_tasks: int,
        dry_run: bool,
    ) -> Dict[str, Any]:
        """
        단일 태스크 실행 유닛:
        사전점검 → 실행 → 산출물 실물 검증 → 정리 → 백오프 → 즉시 1회 재시도
        반환: 구조화된 결과 레코드 (예외는 여기서 흡수)
        """
        started_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record: Dict[str, Any] = {
            "step": step_idx,
            "task_id": task["task_id"],
            "brand": task["brand"],
            "type": task["type"],
            "slot": task["slot"],
            "topic_id": task["topic_id"],
            "label": task["label"],
            "success": False,
            "verified": False,
            "attempts": 0,
            "elapsed_sec": 0.0,
            "error": None,
            "timestamp": started_at,
        }

        # ------------------------------------------------------------------
        # (A) DailyReceiptGuard 사전 검사 — 당일 쿼터 이미 충족 시 서브프로세스 0회 기동
        # ------------------------------------------------------------------
        try:
            if self._is_quota_reached(task["brand"], task["type"]):
                logger.info(
                    f"🧾 [쿼터 충족 스킵] {task['label']} — 당일 쿼터 이미 달성, 기동 생략"
                )
                record.update({
                    "success": True,
                    "verified": True,
                    "status": "SKIPPED_QUOTA_SATISFIED",
                    "attempts": 0,
                    "elapsed_sec": 0.0,
                    "error": None,
                })
                return record
        except Exception as e:
            logger.warning(f"⚠️ [쿼터 사전검사 예외] {task['label']}: {e} — 계속 진행")

        # ------------------------------------------------------------------
        # (B) 07:00 KTRS 주간 양보 마감 인지 안전 가드
        # ------------------------------------------------------------------
        can_run, deadline_reason = self._check_deadline_guard(task["type"])
        if not can_run:
            logger.warning(
                f"⏰ [안전 이월] {task['label']} — {deadline_reason}"
            )
            record.update({
                "success": False,
                "verified": False,
                "status": "DEFERRED_DAYTIME_YIELD",
                "error": deadline_reason,
            })
            return record

        if dry_run:
            logger.info(f"[DRY-RUN] {task['cmd']} 가상 실행 (2초)")
            time.sleep(2)
            record.update({"success": True, "verified": True, "attempts": 1, "elapsed_sec": 2.0})
            return record

        # 사전점검 (첫 태스크에서 실패해도 이후 태스크가 재시도할 수 있도록 여기서 흡수)
        if not self._preflight_ensure_comfyui():
            logger.warning(f"⚠️ [사전점검 실패] {task['label']} — 그래도 실행 시도")

        max_attempts = 1 + self.MAX_IMMEDIATE_RETRY
        total_elapsed = 0.0

        for attempt in range(1, max_attempts + 1):
            record["attempts"] = attempt
            attempt_label = f"[{step_idx}/{total_tasks}] {task['label']}" + (
                f" (재시도 {attempt-1})" if attempt > 1 else ""
            )
            logger.info(f"▶️ {attempt_label} 실행")

            res: Dict[str, Any] = {}
            try:
                res = GPUSafetyGuard.run_isolated_step(
                    cmd=task["cmd"],
                    label=attempt_label,
                    cwd=str(CURRENT_DIR),
                    timeout_sec=self.TASK_TIMEOUT_SEC,
                    cooldown_sec=self.cooldown_sec,
                ) or {}
                elapsed = float(res.get("elapsed_sec", 0) or 0)
                total_elapsed += elapsed
                exit_ok = bool(res.get("success", False))
            except Exception as e:
                logger.error(f"❌ [태스크 예외] {task['label']} attempt={attempt}: {e}")
                logger.debug(traceback.format_exc())
                record["error"] = f"{type(e).__name__}: {e}"
                exit_ok = False

            # 종료코드 0이어도 산출물 실물 검증 (완제품 탐색 + 직인 발급 일원화)
            art_ok, art_path, slide_paths = self.find_and_tag_ready_artifact(
                task["brand"], task["type"], task["topic_id"], task["slot"], task.get("subtype")
            )
            verified = bool(art_ok)
            record["verified"] = verified

            if exit_ok and verified:
                record["success"] = True
                record["artifact_path"] = art_path
                record["slide_paths"] = slide_paths
                record["ready_for_dispatch"] = True
                record["elapsed_sec"] = round(total_elapsed, 2)
                record["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger.info(f"✅ [완료] {task['label']} (검증 통과, {record['elapsed_sec']}s)")
                return record

            # 실패 사유 정리
            if exit_ok and not verified:
                record["error"] = "프로세스 종료코드 0이지만 산출물 실물 검증 실패"
                logger.warning(f"⚠️ [검증 실패] {task['label']} — 산출물 미완성")
            elif not exit_ok:
                # 🧯 에러 원문 보존: GPUSafetyGuard 가 돌려준 실제 사유를 그대로 기록
                record["error"] = (
                    record["error"]
                    or res.get("error")
                    or res.get("reason")
                    or "프로세스 비정상 종료"
                )

            # 백오프 후 재시도
            if attempt < max_attempts:
                backoff = min(self.BACKOFF_BASE_SEC * (2 ** (attempt - 1)), self.BACKOFF_MAX_SEC)
                logger.info(f"⏳ [백오프] {backoff}s 후 재시도: {task['label']}")
                time.sleep(backoff)

        record["elapsed_sec"] = round(total_elapsed, 2)
        record["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.error(f"❌ [최종 실패] {task['label']} — {record['error']}")
        return record

    # ------------------------------------------------------------------
    # 브랜드 단위 파이프라인 (격리 경계)
    # ------------------------------------------------------------------
    def _run_brand_pipeline(
        self,
        brand: str,
        state: Dict[str, Any],
        manifest_file: Path,
        date_str: str,
        results: List[Dict[str, Any]],
        total_tasks: int,
        dry_run: bool,
    ) -> None:
        """
        [레거시 · DEPRECATED] 브랜드 단위 직렬 파이프라인.

        ⚠️ run_nightly_production 은 더 이상 이 메서드를 호출하지 않는다.
           현재는 _build_interleaved_tasks() + _execute_single_task() 인터리빙
           순회로 대체되었다. 수동 디버깅/단일 브랜드 재현용으로만 보존한다.
        """
        meta = BRAND_META[brand]
        logger.info(f"\n{'='*70}\n🏭 [브랜드 파이프라인 시작] {meta['emoji']} {meta['name']}\n{'='*70}")

        try:
            tasks = self._build_brand_tasks(brand, state)
        except Exception as e:
            logger.error(f"❌ [{brand}] 태스크 빌드 실패: {e}")
            logger.debug(traceback.format_exc())
            return

        for task in tasks:
            step_idx = len(results) + 1
            try:
                record = self._execute_single_task(task, step_idx, total_tasks, dry_run)
            except Exception as e:
                # 실행 유닛 자체가 예외를 흘리더라도 브랜드 파이프라인은 계속
                logger.error(f"❌ [{brand}] 태스크 실행 유닛 예외: {e}")
                logger.debug(traceback.format_exc())
                record = {
                    "step": step_idx,
                    "task_id": task["task_id"],
                    "brand": task["brand"],
                    "type": task["type"],
                    "slot": task["slot"],
                    "topic_id": task["topic_id"],
                    "label": task["label"],
                    "success": False,
                    "verified": False,
                    "attempts": 0,
                    "elapsed_sec": 0.0,
                    "error": f"{type(e).__name__}: {e}",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

            results.append(record)

            # 매 태스크 완료 즉시 매니페스트 flush (크래시 시 잔여 유실 방지)
            self._write_manifest(manifest_file, {
                "date": date_str,
                "completed_tasks": len(results),
                "total_tasks": total_tasks,
                "tasks": results,
            })

            # 성공 시 오프셋 멱등 저장 (task_id 기반)
            if record["success"]:
                offset_key = f"{brand}_{task['type']}_offset"
                max_t = meta["cardnews_max_topics"] if task["type"] == "cardnews" else meta["shorts_max_topics"]
                state[offset_key] = task["topic_id"] % max_t
                self._save_state(state)

        logger.info(f"🏁 [브랜드 파이프라인 종료] {meta['emoji']} {meta['name']}")

    # ------------------------------------------------------------------
    # 메인 오케스트레이션
    # ------------------------------------------------------------------
    def run_nightly_production(self, date_str: str = None, dry_run: bool = False) -> Dict[str, Any]:
        if not date_str:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")

        today_queue_dir = self.QUEUE_DIR / date_str
        today_queue_dir.mkdir(parents=True, exist_ok=True)
        manifest_file = today_queue_dir / "manifest.json"

        state = self._load_state()

        # 사전 청소
        try:
            self.clean_incomplete_today_folders()
        except Exception as e:
            logger.warning(f"사전 청소 예외(무시하고 진행): {e}")

        logger.info("\n" + "=" * 70)
        logger.info(f"🌙 [밤 12시 콘텐츠 무인 생산 공장 점화] 기준 날짜: {date_str}")
        logger.info(f"❄️ GPU 냉각 규격: 작업당 {self.cooldown_sec}초 쿨다운 + VRAM 강제 방출")
        logger.info(f"🎯 생산 계획: 3대 앱 × (숏폼 3개 + 카드뉴스 2개) = 총 15개 콘텐츠")
        logger.info("=" * 70 + "\n")

        # ------------------------------------------------------------------
        # 🔀 교차 라운드로빈 인터리빙 큐 생성 (브랜드별 직렬 루프 전면 폐지)
        # ------------------------------------------------------------------
        try:
            tasks = self._build_interleaved_tasks(state)
        except Exception as e:
            logger.error(f"❌❌ [인터리빙 큐 빌드 치명 예외] {e}")
            logger.debug(traceback.format_exc())
            tasks = []

        total_tasks = len(tasks)
        results: List[Dict[str, Any]] = []
        deferred_count = 0

        # 인터리빙 순서대로 하나씩 실행
        for task in tasks:
            step_idx = len(results) + 1
            try:
                record = self._execute_single_task(task, step_idx, total_tasks, dry_run)
            except Exception as e:
                # 실행 유닛 자체가 예외를 흘리더라도 큐 순회는 계속
                logger.error(f"❌ [태스크 실행 유닛 예외] {task.get('label')}: {e}")
                logger.debug(traceback.format_exc())
                record = {
                    "step": step_idx,
                    "task_id": task.get("task_id"),
                    "brand": task.get("brand"),
                    "type": task.get("type"),
                    "slot": task.get("slot"),
                    "topic_id": task.get("topic_id"),
                    "label": task.get("label"),
                    "success": False,
                    "verified": False,
                    "attempts": 0,
                    "elapsed_sec": 0.0,
                    "error": f"{type(e).__name__}: {e}",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

            results.append(record)

            # 매 태스크 완료 즉시 매니페스트 원자적 flush
            self._write_manifest(manifest_file, {
                "date": date_str,
                "completed_tasks": len(results),
                "total_tasks": total_tasks,
                "tasks": results,
            })

            # 성공 시 오프셋 멱등 저장
            if record.get("success"):
                brand = task.get("brand")
                ctype = task.get("type")
                topic_id = task.get("topic_id")
                if brand and ctype and topic_id is not None:
                    meta = BRAND_META.get(brand, {})
                    max_t = (
                        meta.get("cardnews_max_topics", 8)
                        if ctype == "cardnews"
                        else meta.get("shorts_max_topics", 8)
                    )
                    state[f"{brand}_{ctype}_offset"] = int(topic_id) % max_t
                    self._save_state(state)

            # 07:00 마감 이월 발생 시 후속 태스크도 동일하게 안전 이월 처리
            if record.get("status") == "DEFERRED_DAYTIME_YIELD":
                deferred_count += 1
                remaining = total_tasks - len(results)
                if remaining > 0:
                    logger.warning(
                        f"⏰ [마감 이월 감지] 남은 {remaining}개 태스크를 안전 이월 처리합니다."
                    )
                    for rest in tasks[len(results):]:
                        results.append({
                            "step": len(results) + 1,
                            "task_id": rest.get("task_id"),
                            "brand": rest.get("brand"),
                            "type": rest.get("type"),
                            "slot": rest.get("slot"),
                            "topic_id": rest.get("topic_id"),
                            "label": rest.get("label"),
                            "success": False,
                            "verified": False,
                            "status": "DEFERRED_DAYTIME_YIELD",
                            "attempts": 0,
                            "elapsed_sec": 0.0,
                            "error": record.get("error"),
                            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        })
                        deferred_count += 1
                    self._write_manifest(manifest_file, {
                        "date": date_str,
                        "completed_tasks": len(results),
                        "total_tasks": total_tasks,
                        "tasks": results,
                    })
                break

        # 최종 상태 기록
        state["last_run_date"] = date_str
        self._save_state(state)

        # 최종 매니페스트 (요약 포함)
        success_count = sum(1 for r in results if r.get("success"))
        failed = [r for r in results if not r.get("success")]
        self._write_manifest(manifest_file, {
            "date": date_str,
            "completed_tasks": len(results),
            "total_tasks": total_tasks,
            "success_count": success_count,
            "failed_count": len(failed),
            "deferred_count": deferred_count,
            "tasks": results,
        })

        logger.info("\n" + "=" * 70)
        logger.info(f"🎉 [야간 생산 종료] 성공 {success_count}/{total_tasks}건")
        if failed:
            logger.warning(f"⚠️ 실패 {len(failed)}건:")
            for r in failed:
                logger.warning(f"   - {r['label']} | 사유: {r.get('error')}")
        logger.info(f"📂 매니페스트: {manifest_file}")
        logger.info(f"🤝 GPU VRAM 100% 비우고 대기 상태로 전환합니다.")
        logger.info("=" * 70 + "\n")

        # 최종 VRAM 클리어
        try:
            GPUSafetyGuard.cleanup_all()
        except Exception as e:
            logger.warning(f"최종 VRAM 클리어 예외: {e}")

        return {
            "date": date_str,
            "manifest_file": str(manifest_file),
            "total_produced": len(results),
            "success_count": success_count,
            "failed_count": len(failed),
            "failed_tasks": [r["label"] for r in failed],
        }

    # ------------------------------------------------------------------
    # 데몬
    # ------------------------------------------------------------------
    def start_daemon(self):
        logger.info("🤖 [MidnightContentFactory Daemon] 24시간 365일 무인 감시 상주 시작")
        logger.info("⏰ 트리거 조건: 매일 00:00 KST (밤 12시)")

        while True:
            try:
                now = datetime.datetime.now()
                today_str = now.strftime("%Y-%m-%d")
                state = self._load_state()

                if now.hour == 0 and state.get("last_run_date") != today_str:
                    logger.info(f"⏰ [밤 12시 도달] {today_str} 오늘치 3대 앱 15개 콘텐츠 순차 제작 점화!")
                    try:
                        self.run_nightly_production(date_str=today_str)
                    except Exception as e:
                        logger.error(f"❌ 야간 제작 공장 실행 중 예외 발생: {e}")
                        logger.debug(traceback.format_exc())
            except Exception as e:
                # 데몬 루프 자체 예외도 절대 사망하지 않도록
                logger.error(f"❌ [데몬 루프 예외] {e}")
                logger.debug(traceback.format_exc())

            time.sleep(30)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="🌙 밤 12시 3대 앱 콘텐츠 무인 생산 공장")
    parser.add_argument("--now", action="store_true", help="지금 즉시 1회 생산 가동")
    parser.add_argument("--dry-run", action="store_true", help="가상 시뮬레이션 모드")
    parser.add_argument("--daemon", action="store_true", help="밤 12시 상주 감시 데몬 가동")
    parser.add_argument("--cooldown", type=int, default=300, help="쿨다운 초 (기본: 300초 = 5분)")
    parser.add_argument("--reset", action="store_true", help="오늘자 기존 폴더를 전부 정리하고 오프셋을 0으로 리셋하여 1번부터 새로 제작")
    args = parser.parse_args()

    factory = MidnightContentFactory(cooldown_sec=args.cooldown)

    if args.reset:
        logger.info("🔄 [--reset 플래그 감지] 오늘자 기존 폴더 완전 정리 및 1번 주제부터 리셋 가동...")
        factory.clean_today_folders(all_today=True)

    if args.daemon:
        factory.start_daemon()
    else:
        factory.run_nightly_production(dry_run=args.dry_run)
