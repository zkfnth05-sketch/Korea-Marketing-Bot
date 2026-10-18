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

[아키텍처 재편 요약]
- 브랜드 단위 격리 경계: Aura / Insurance / Stock 각각 독립 try/except 파이프라인
- 태스크 단위 실행 유닛: 사전점검 → 실행 → 산출물 실물 검증 → 정리 → 백오프 → 즉시 1회 재시도
- 멱등 상태 저장: task_id 기반, 매 태스크 완료 즉시 원자적 flush
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


# ============================================================================
# 브랜드 메타데이터 (격리 경계 단위)
# ============================================================================
BRAND_META: Dict[str, Dict[str, Any]] = {
    "aura": {
        "emoji": "💖",
        "name": "Aura 데이팅",
        "shorts_script": "run_aura_shorts.py",
        "cardnews_script": "run_aura_cardnews.py",
        "shorts_extra": ["--no-publish"],
        "cardnews_extra": ["all"],
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
        "shorts_extra": [],
        "cardnews_extra": [],
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
        "shorts_extra": [],
        "cardnews_extra": [],
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
    TASK_TIMEOUT_SEC = 3600          # 태스크 1건 최대 60분
    MAX_IMMEDIATE_RETRY = 1          # 태스크 단위 즉시 재시도 1회
    BACKOFF_BASE_SEC = 15            # 재시도 백오프 기본값
    BACKOFF_MAX_SEC = 120            # 재시도 백오프 상한

    def __init__(self, cooldown_sec: int = 300):
        self.cooldown_sec = cooldown_sec
        self.QUEUE_DIR.mkdir(parents=True, exist_ok=True)
        self.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

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
                    if brand == "stock" and slides:
                        mod_date = datetime.datetime.fromtimestamp(
                            slides[0].stat().st_mtime
                        ).strftime("%Y%m%d")
                        is_today = (mod_date == today_str)
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
                    if not is_today and mp4s:
                        mod_date = datetime.datetime.fromtimestamp(
                            mp4s[0].stat().st_mtime
                        ).strftime("%Y%m%d")
                        is_today = (mod_date == today_str)
                    if is_today and len(mp4s) >= 1:
                        parts = f.name.replace("[", "_").replace("]", "_").split("_")
                        for p in parts:
                            p_clean = p.replace("주제", "").strip()
                            if p_clean.isdigit():
                                created.add(int(p_clean))
                                break
        return sorted(list(created))

    def _verify_artifact(self, brand: str, content_type: str, topic_id: int) -> bool:
        """특정 주제 산출물이 실제로 완성되었는지 실물 검증"""
        try:
            done = set(self.get_today_created_topics(brand, content_type))
            return topic_id in done
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
        meta = BRAND_META[brand]
        emoji = meta["emoji"]
        name = meta["name"]

        s_topics = self.pick_smart_rotating_topics(
            brand, "shorts", state.get(f"{brand}_shorts_offset", 0), 3, meta["shorts_max_topics"]
        )
        c_topics = self.pick_smart_rotating_topics(
            brand, "cardnews", state.get(f"{brand}_cardnews_offset", 0), 2, meta["cardnews_max_topics"]
        )

        tasks: List[Dict[str, Any]] = []
        for idx, t in enumerate(s_topics, 1):
            cmd = [sys.executable, str(CURRENT_DIR / meta["shorts_script"]), "--topic", str(t)]
            cmd.extend(meta["shorts_extra"])
            tasks.append({
                "task_id": f"{brand}:shorts:{t}",
                "brand": brand,
                "type": "shorts",
                "slot": f"shorts_{idx}",
                "topic_id": t,
                "label": f"{emoji} {name} 숏폼 #{idx} (주제 #{t})",
                "cmd": cmd,
            })
        for idx, t in enumerate(c_topics, 1):
            cmd = [sys.executable, str(CURRENT_DIR / meta["cardnews_script"])]
            cmd.extend(meta["cardnews_extra"])
            cmd.extend(["--topic", str(t)])
            tasks.append({
                "task_id": f"{brand}:cardnews:{t}",
                "brand": brand,
                "type": "cardnews",
                "slot": f"cardnews_{idx}",
                "topic_id": t,
                "label": f"{emoji} {name} 카드뉴스 #{idx} (주제 #{t})",
                "cmd": cmd,
            })
        return tasks

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

            try:
                res = GPUSafetyGuard.run_isolated_step(
                    cmd=task["cmd"],
                    label=attempt_label,
                    cwd=str(CURRENT_DIR),
                    cooldown_sec=self.cooldown_sec,
                )
                elapsed = float(res.get("elapsed_sec", 0) or 0)
                total_elapsed += elapsed
                exit_ok = bool(res.get("success", False))
            except Exception as e:
                logger.error(f"❌ [태스크 예외] {task['label']} attempt={attempt}: {e}")
                logger.debug(traceback.format_exc())
                record["error"] = f"{type(e).__name__}: {e}"
                exit_ok = False

            # 종료코드 0이어도 산출물 실물 검증
            verified = self._verify_artifact(task["brand"], task["type"], task["topic_id"])
            record["verified"] = verified

            if exit_ok and verified:
                record["success"] = True
                record["elapsed_sec"] = round(total_elapsed, 2)
                record["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger.info(f"✅ [완료] {task['label']} (검증 통과, {record['elapsed_sec']}s)")
                return record

            # 실패 사유 정리
            if exit_ok and not verified:
                record["error"] = "프로세스 종료코드 0이지만 산출물 실물 검증 실패"
                logger.warning(f"⚠️ [검증 실패] {task['label']} — 산출물 미완성")
            elif not exit_ok:
                record["error"] = record["error"] or "프로세스 비정상 종료"

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
        브랜드 1개 파이프라인. 예외는 여기서 흡수되어 다른 브랜드에 영향 없음.
        태스크 완료 즉시 매니페스트 flush + 오프셋 멱등 저장.
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

        # 총 태스크 수 사전 계산 (진행률 표시용)
        total_tasks = 0
        for brand in BRAND_META:
            meta = BRAND_META[brand]
            total_tasks += 3 + 2  # 숏폼 3 + 카드뉴스 2

        results: List[Dict[str, Any]] = []

        # 브랜드 단위 격리 실행
        for brand in ["aura", "insurance", "stock"]:
            try:
                self._run_brand_pipeline(
                    brand=brand,
                    state=state,
                    manifest_file=manifest_file,
                    date_str=date_str,
                    results=results,
                    total_tasks=total_tasks,
                    dry_run=dry_run,
                )
            except Exception as e:
                # 브랜드 파이프라인 전체 예외도 흡수 → 다음 브랜드 계속
                logger.error(f"❌❌ [{brand}] 브랜드 파이프라인 치명 예외: {e}")
                logger.debug(traceback.format_exc())

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
