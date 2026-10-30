"""
Aura Master Independent Pipeline (Aura AI 데이팅 독립 전담 마케팅 파이프라인)
========================================================================
- 브랜드: 💖 Aura AI 데이팅
- 공식 검색어: '아우라AI데이팅' (붙여쓰기 필수)
- 랜딩 URL: https://aura-ai-dating.vercel.app/
- 규칙:
  1. 쏘기 전 즉시 1편 생산 -> 1회 단발 발송 (중복 도배 전면 차단)
  2. 숏폼: 유튜브 Shorts + 네이버 클립(공개) + 인스타 Reels + 페북 Reels
  3. 카드뉴스: 페북 앨범(첫댓글 링크) + 인스타 캐러셀(4단 해시태그)
  4. 휴먼비헤이비어: 네이버 블로그/카페 4회 정시 웜업 (제미나이 0회)
  5. 카페: 순수 파이썬 100% 필터링 + 제미나이 1일 1회 침투
  6. 24시간 365일 무인 자율 구동 데몬 지원
"""

import os
import sys
import json
import time
import uuid
import argparse
import logging
import asyncio
import threading
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

# Root path alignment
current_dir = os.path.dirname(os.path.abspath(__file__))
engine_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if engine_root not in sys.path:
    sys.path.insert(0, engine_root)

from brands.aura.aura_omni_shorts_pilot import AuraOmniShortsPilot
from brands.aura.aura_omni_cardnews_pilot import AuraOmniCardnewsPilot
from brands.aura.aura_human_behavior_bot import AuraHumanBehaviorBot
from brands.aura.aura_cafe_pipeline import AuraCafePipeline
from brands.aura.aura_kin_pipeline import AuraKinPipeline
from brands.aura.aura_blog_scheduler import AuraBlogScheduler
from brands.aura.aura_text_thread_hub import AuraTextThreadHub
from brands.aura.aura_search_indexing_hub import AuraSearchIndexingHub
from core.verification.live_proof_verifier import live_proof_verifier
from config import get_now_kst, get_now_kst_str

logger = logging.getLogger("AuraPipeline")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class AuraPipeline:
    BRAND = "aura"
    NAME = "Aura AI 데이팅"
    KEYWORD = "아우라AI데이팅"
    URL = "https://aura-ai-dating.vercel.app/"

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.shorts_pilot = AuraOmniShortsPilot()
        self.cardnews_pilot = AuraOmniCardnewsPilot()
        self.human_bot = AuraHumanBehaviorBot()
        self.cafe_pipe = AuraCafePipeline()
        self.kin_pipe = AuraKinPipeline()
        self.blog_scheduler = AuraBlogScheduler()
        self.thread_hub = AuraTextThreadHub()
        self.seo_hub = AuraSearchIndexingHub()
        self.proof_verifier = live_proof_verifier

    # 1. 숏폼 파이프라인 (쏘기 전 1편 신규 생산 -> 4대 플랫폼 1회 단발 발송 + 실시간 증빙 캡처)
    def run_shorts(self, topic_id: Optional[int] = None, force: bool = False) -> Dict[str, Any]:
        logger.info(f"🎬 [{self.NAME}] 숏폼 파이프라인 가동: 쏘기 직전 1편 신규 제작 및 4대 채널(유튜브+클립+릴스) 단발 송출")
        try:
            if force:
                today_str = get_now_kst().strftime("%Y-%m-%d")
                self.shorts_pilot.published_records = [
                    r for r in self.shorts_pilot.published_records if r.get("date") != today_str
                ]
            res = self.shorts_pilot.execute_single_slot(topic_id=topic_id, force=force)
            if res.get("success") or res.get("youtube_url") or res.get("instagram_url"):
                live_url = res.get("youtube_url") or res.get("instagram_url") or self.URL
                self.proof_verifier.record_and_capture_proof(
                    brand=self.BRAND, channel="youtube", live_url=live_url, title=f"Aura 숏폼 주제 {topic_id or 1}", take_screenshot=True
                )
            else:
                self.proof_verifier.record_failure(
                    brand=self.BRAND, channel="youtube", error_message=res.get("error") or "쇼츠 렌더링/업로드 실패", title=f"Aura 숏폼 주제 {topic_id or 1}"
                )
            return res
        except Exception as e:
            self.proof_verifier.record_failure(
                brand=self.BRAND, channel="youtube", error_message=str(e), title=f"Aura 숏폼 주제 {topic_id or 1}"
            )
            raise

    # 2. 카드뉴스 파이프라인 (쏘기 전 5장 신규 렌더링 -> 2대 플랫폼 1회 단발 발송 + 실시간 증빙 캡처)
    def run_cardnews(self, topic_id: Optional[int] = None, force: bool = False) -> Dict[str, Any]:
        logger.info(f"🎨 [{self.NAME}] 카드뉴스 파이프라인 가동: 쏘기 직전 5장 신규 제작 및 Meta(페북+인스타) 단발 송출")
        try:
            if force:
                today_str = get_now_kst().strftime("%Y-%m-%d")
                self.cardnews_pilot.published_records = [
                    r for r in self.cardnews_pilot.published_records if r.get("date") != today_str
                ]
            res = self.cardnews_pilot.execute_single_slot(topic_id=topic_id, force=force)
            if res.get("success") or res.get("instagram_url") or res.get("facebook_url"):
                live_url = res.get("instagram_url") or res.get("facebook_url") or f"https://www.instagram.com/aura_ai_dating/"
                self.proof_verifier.record_and_capture_proof(
                    brand=self.BRAND, channel="instagram", live_url=live_url, title=f"Aura 카드뉴스 주제 {topic_id or 1}", take_screenshot=True
                )
            else:
                self.proof_verifier.record_failure(
                    brand=self.BRAND, channel="instagram", error_message=res.get("error") or "카드뉴스 렌더링/발행 실패", title=f"Aura 카드뉴스 주제 {topic_id or 1}"
                )
            return res
        except Exception as e:
            self.proof_verifier.record_failure(
                brand=self.BRAND, channel="instagram", error_message=str(e), title=f"Aura 카드뉴스 주제 {topic_id or 1}"
            )
            raise

    # 3. 휴먼비헤이비어 봇 파이프라인 (네이버 블로그/카페 웜업)
    def run_human_behavior(self, mode: str = "once") -> Dict[str, Any]:
        logger.info(f"🤖 [{self.NAME}] 네이버 휴먼비헤이비어 가동 (모드: {mode})")
        if mode == "daemon":
            self.human_bot.run_daemon(check_interval_seconds=30)
            return {"status": "daemon_running"}
        else:
            return self.human_bot.perform_routine()

    # 4. 네이버 카페 스텔스 침투 파이프라인 (+ 실시간 증빙)
    def run_cafe(self) -> Dict[str, Any]:
        logger.info(f"☕ [{self.NAME}] 네이버 카페 스텔스 침투 파이프라인 가동")
        try:
            res = asyncio.run(self.cafe_pipe.run_daily_stealth_infiltration(dry_run=self.dry_run))
            if res.get("status") in ["SUCCESS", "SUCCESS_WAIT", "COMPLETED"] or res.get("article_url"):
                live_url = res.get("article_url") or res.get("cafe_url") or "https://cafe.naver.com/"
                self.proof_verifier.record_and_capture_proof(
                    brand=self.BRAND, channel="naver_cafe", live_url=live_url, title="Aura 카페 댓글 침투", take_screenshot=True
                )
            else:
                self.proof_verifier.record_failure(
                    brand=self.BRAND, channel="naver_cafe", error_message=res.get("message") or res.get("error") or "카페 탐색/댓글 침투 조건 미충족", title="Aura 카페 댓글 침투"
                )
            return res
        except Exception as e:
            self.proof_verifier.record_failure(
                brand=self.BRAND, channel="naver_cafe", error_message=str(e), title="Aura 카페 댓글 침투"
            )
            raise

    # 5. 네이버 지식iN 파이프라인 (+ 실시간 증빙)
    def run_kin(self) -> Dict[str, Any]:
        logger.info(f"🎯 [{self.NAME}] 네이버 지식iN 실시간 낚아채기 파이프라인 가동")
        try:
            res = self.kin_pipe.run_catch_cycle(max_catch=1, dry_run=self.dry_run)
            if res.get("success") or res.get("kin_url") or res.get("url"):
                live_url = res.get("kin_url") or res.get("url") or "https://kin.naver.com/"
                self.proof_verifier.record_and_capture_proof(
                    brand=self.BRAND, channel="naver_kin", live_url=live_url, title="Aura 지식iN 실시간 답변", take_screenshot=True
                )
            else:
                self.proof_verifier.record_failure(
                    brand=self.BRAND, channel="naver_kin", error_message=res.get("message") or res.get("error") or "지식iN 타겟 질문 탐색 대기", title="Aura 지식iN 실시간 답변"
                )
            return res
        except Exception as e:
            self.proof_verifier.record_failure(
                brand=self.BRAND, channel="naver_kin", error_message=str(e), title="Aura 지식iN 실시간 답변"
            )
            raise

    # 6. 블로그/매거진 파이프라인 (+ 실시간 증빙)
    def run_blog(self) -> Dict[str, Any]:
        logger.info(f"✍️ [{self.NAME}] 4대 옴니 블로그/매거진 파이프라인 가동")
        try:
            res = self.blog_scheduler.run_one_cycle()
            nb = res.get("publish_results", {}).get("channels", {}).get("naver_blog", {})
            if nb.get("success") or res.get("blog_url") or res.get("url"):
                live_url = nb.get("url") or res.get("blog_url") or res.get("url") or "https://blog.naver.com/zkfnth01"
                self.proof_verifier.record_and_capture_proof(
                    brand=self.BRAND, channel="naver_blog", live_url=live_url, title="Aura 2030 매거진 발행", take_screenshot=True
                )
            else:
                self.proof_verifier.record_failure(
                    brand=self.BRAND, channel="naver_blog", error_message=nb.get("error") or res.get("message") or "블로그 발행 실패", title="Aura 2030 매거진 발행"
                )
            return res
        except Exception as e:
            self.proof_verifier.record_failure(
                brand=self.BRAND, channel="naver_blog", error_message=str(e), title="Aura 2030 매거진 발행"
            )
            raise

    # 7. 텍스트 스토리 타래 (+ 실시간 증빙)
    def run_threads(self) -> Dict[str, Any]:
        logger.info(f"🧵 [{self.NAME}] 텍스트 타래 배포 파이프라인 가동")
        try:
            res = self.thread_hub.publish_omni_thread()
            if res.get("success") or res.get("thread_url"):
                live_url = res.get("thread_url") or res.get("url") or "https://threads.net/@aura_ai_dating"
                self.proof_verifier.record_and_capture_proof(
                    brand=self.BRAND, channel="threads", live_url=live_url, title="Aura 스레드 옴니 타래", take_screenshot=True
                )
            else:
                self.proof_verifier.record_failure(
                    brand=self.BRAND, channel="threads", error_message=res.get("error") or res.get("message") or "스레드 타래 배포 실패", title="Aura 스레드 옴니 타래"
                )
            return res
        except Exception as e:
            self.proof_verifier.record_failure(
                brand=self.BRAND, channel="threads", error_message=str(e), title="Aura 스레드 옴니 타래"
            )
            raise

    # 8. 검색엔진 색인 핑 (+ 실시간 증빙)
    def run_seo(self) -> Dict[str, Any]:
        logger.info(f"🌐 [{self.NAME}] 검색엔진 색인 핑 파이프라인 가동")
        try:
            res = self.seo_hub.ping_all_engines()
            if res.get("success"):
                self.proof_verifier.record_and_capture_proof(
                    brand=self.BRAND, channel="indexing_ping", live_url=self.URL, title="Aura 네이버/구글 검색 색인핑 200 OK", take_screenshot=False
                )
            else:
                self.proof_verifier.record_failure(
                    brand=self.BRAND, channel="indexing_ping", error_message=res.get("message") or "검색 색인 핑 전송 실패", title="Aura 검색 색인핑"
                )
            return res
        except Exception as e:
            self.proof_verifier.record_failure(
                brand=self.BRAND, channel="indexing_ping", error_message=str(e), title="Aura 검색 색인핑"
            )
            raise

    # 통합 동적 채널 라우터
    def run_channel(self, channel_name: str, **kwargs) -> Dict[str, Any]:
        c = channel_name.lower().strip()
        if c in ["shorts", "youtube", "naver_clip", "reels"]:
            return self.run_shorts(**kwargs)
        elif c in ["cardnews", "meta", "instagram", "facebook"]:
            return self.run_cardnews(**kwargs)
        elif c in ["human", "behavior", "warmup"]:
            return self.run_human_behavior(**kwargs)
        elif c in ["cafe", "naver_cafe"]:
            return self.run_cafe()
        elif c in ["kin", "naver_kin", "qna"]:
            return self.run_kin()
        elif c in ["blog", "magazine", "tistory"]:
            return self.run_blog()
        elif c in ["threads", "story"]:
            return self.run_threads()
        elif c in ["seo", "advisor", "ping"]:
            return self.run_seo()
        else:
            raise ValueError(f"알 수 없는 채널: {channel_name}")

    # 전 채널 1회 종합 순차 검증
    def run_full_cycle(self) -> Dict[str, Any]:
        logger.info("=" * 60)
        logger.info(f"🚀 [{self.NAME}] 전 채널 독립 파이프라인 종합 1회 가동 시작")
        logger.info("=" * 60)

        results = {}
        try:
            results["human"] = self.run_human_behavior(mode="once")
        except Exception as e:
            results["human"] = {"error": str(e)}

        try:
            results["cardnews"] = self.run_cardnews()
        except Exception as e:
            results["cardnews"] = {"error": str(e)}

        try:
            results["shorts"] = self.run_shorts()
        except Exception as e:
            results["shorts"] = {"error": str(e)}

        try:
            results["kin"] = self.run_kin()
        except Exception as e:
            results["kin"] = {"error": str(e)}

        return {
            "brand": self.BRAND,
            "status": "completed",
            "timestamp": get_now_kst_str(),
            "results": results
        }

    def run_full_daily_cycle(self) -> Dict[str, Any]:
        """일일 전 채널 순차 사이클 실행 (하위 호환 및 스케줄러 공식 표준)"""
        return self.run_full_cycle()

    # ============================================================
    # [구조 재설계] 영속 슬롯 원장 + 상태기계 + lease 락 + Producer/Consumer
    # ============================================================
    LEDGER_DIR = os.path.join(current_dir, ".aura_state")
    LEDGER_PATH = os.path.join(LEDGER_DIR, "slot_ledger.json")
    READY_POOL_DIR = os.path.join(LEDGER_DIR, "ready_pool")
    LOCK_DIR = os.path.join(LEDGER_DIR, "locks")
    LEASE_TTL_SEC = 900          # 15분 lease (좀비 회수 기준)
    SLOT_TIMEOUT_SEC = 1800      # 슬롯 실행 하드 타임아웃
    MAX_RETRY = 3
    BACKOFF_BASE_SEC = 60

    # 24시간 균등 분산 슬롯 테이블 (KST)
    # (slot_id, hour, minute, channel, kwargs)
    SLOT_TABLE = [
        ("shorts_0830",   8, 30, "shorts",   {}),
        ("blog_1000",    10,  0, "blog",     {}),
        ("cardnews_1230",12, 30, "cardnews", {}),
        ("blog_1500",    15,  0, "blog",     {}),
        ("shorts_1930",  19, 30, "shorts",   {}),
        ("blog_2000",    20,  0, "blog",     {}),
    ]
    # 지식iN: 매 30분 오프셋(10,40) - 별도 저부하 슬롯
    KIN_MINUTES = [10, 40]

    def _ensure_dirs(self):
        for d in (self.LEDGER_DIR, self.READY_POOL_DIR, self.LOCK_DIR):
            os.makedirs(d, exist_ok=True)

    def _load_ledger(self) -> Dict[str, Any]:
        self._ensure_dirs()
        if not os.path.exists(self.LEDGER_PATH):
            return {"slots": {}, "version": 1}
        try:
            with open(self.LEDGER_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"원장 로드 실패(손상 복구): {e}")
            return {"slots": {}, "version": 1}

    def _save_ledger(self, ledger: Dict[str, Any]):
        self._ensure_dirs()
        tmp = self.LEDGER_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(ledger, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.LEDGER_PATH)  # 원자적 교체

    def _acquire_lease(self, slot_key: str) -> bool:
        """슬롯키 기반 파일 lease. TTL 만료 시 좀비 락 회수."""
        self._ensure_dirs()
        lock_path = os.path.join(self.LOCK_DIR, f"{slot_key}.lock")
        now_ts = time.time()
        try:
            if os.path.exists(lock_path):
                try:
                    with open(lock_path, "r", encoding="utf-8") as f:
                        info = json.load(f)
                    if now_ts - info.get("ts", 0) < self.LEASE_TTL_SEC:
                        return False  # 유효 락 존재
                    logger.warning(f"♻️ 만료 lease 회수: {slot_key}")
                except Exception:
                    pass
            with open(lock_path, "w", encoding="utf-8") as f:
                json.dump({"pid": os.getpid(), "ts": now_ts, "token": uuid.uuid4().hex}, f)
            return True
        except Exception as e:
            logger.error(f"lease 획득 실패 {slot_key}: {e}")
            return False

    def _release_lease(self, slot_key: str):
        lock_path = os.path.join(self.LOCK_DIR, f"{slot_key}.lock")
        try:
            if os.path.exists(lock_path):
                os.remove(lock_path)
        except Exception:
            pass

    def _run_with_timeout(self, fn, timeout_sec: int, *args, **kwargs):
        """블로킹 호출을 별도 스레드로 격리하고 하드 타임아웃 적용."""
        result_box: Dict[str, Any] = {}

        def _target():
            try:
                result_box["ok"] = fn(*args, **kwargs)
            except Exception as e:
                result_box["err"] = e
                result_box["tb"] = traceback.format_exc()

        t = threading.Thread(target=_target, daemon=True)
        t.start()
        t.join(timeout_sec)
        if t.is_alive():
            raise TimeoutError(f"슬롯 실행 타임아웃({timeout_sec}s) 초과")
        if "err" in result_box:
            raise result_box["err"]
        return result_box.get("ok")

    def _dispatch_channel(self, channel: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """채널 라우팅 (기존 run_channel 재사용, human/kin 등 인자 정합)."""
        if channel == "shorts":
            return self.run_shorts(**kwargs)
        if channel == "cardnews":
            return self.run_cardnews(**kwargs)
        if channel == "blog":
            return self.run_blog()
        if channel == "kin":
            return self.run_kin()
        return self.run_channel(channel, **kwargs)

    def _execute_slot(self, slot_key: str, channel: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """원장 상태기계 기반 슬롯 실행. 실패 시 FAILED로 남겨 재시도 가능."""
        ledger = self._load_ledger()
        slot = ledger["slots"].get(slot_key, {
            "slot_key": slot_key, "channel": channel, "status": "PENDING",
            "retry": 0, "created_at": get_now_kst_str(),
        })

        # 이미 완료된 슬롯은 스킵 (멱등)
        if slot.get("status") == "DONE":
            logger.info(f"⏭️ 이미 완료된 슬롯 스킵: {slot_key}")
            return {"status": "SKIPPED", "slot_key": slot_key}

        # lease 획득 실패 = 다른 프로세스가 실행 중
        if not self._acquire_lease(slot_key):
            logger.info(f"🔒 다른 프로세스가 실행 중(lease): {slot_key}")
            return {"status": "LOCKED", "slot_key": slot_key}

        try:
            slot["status"] = "RUNNING"
            slot["started_at"] = get_now_kst_str()
            slot["pid"] = os.getpid()
            ledger["slots"][slot_key] = slot
            self._save_ledger(ledger)

            logger.info(f"▶️ 슬롯 실행: {slot_key} (channel={channel}, retry={slot.get('retry',0)})")
            res = self._run_with_timeout(self._dispatch_channel, self.SLOT_TIMEOUT_SEC, channel, kwargs)

            # 성공 판정
            success = bool(
                isinstance(res, dict) and (
                    res.get("success") or res.get("status") in ("SUCCESS", "COMPLETED", "SUCCESS_WAIT")
                    or res.get("youtube_url") or res.get("instagram_url") or res.get("blog_url")
                    or res.get("thread_url") or res.get("kin_url") or res.get("article_url")
                )
            )

            ledger = self._load_ledger()
            slot = ledger["slots"].get(slot_key, slot)
            if success:
                slot["status"] = "DONE"
                slot["finished_at"] = get_now_kst_str()
                slot["result"] = {"ok": True}
            else:
                slot["retry"] = slot.get("retry", 0) + 1
                slot["last_error"] = str(res.get("error") if isinstance(res, dict) else res)[:500]
                slot["status"] = "FAILED" if slot["retry"] >= self.MAX_RETRY else "PENDING"
                slot["next_retry_at"] = (
                    get_now_kst() + timedelta(seconds=self.BACKOFF_BASE_SEC * (2 ** (slot["retry"] - 1)))
                ).strftime("%Y-%m-%d %H:%M:%S")
            ledger["slots"][slot_key] = slot
            self._save_ledger(ledger)
            return {"status": slot["status"], "slot_key": slot_key, "result": res}

        except Exception as e:
            logger.error(f"❌ 슬롯 실행 예외 {slot_key}: {e}\n{traceback.format_exc()}")
            ledger = self._load_ledger()
            slot = ledger["slots"].get(slot_key, slot)
            slot["retry"] = slot.get("retry", 0) + 1
            slot["last_error"] = str(e)[:500]
            slot["status"] = "FAILED" if slot["retry"] >= self.MAX_RETRY else "PENDING"
            slot["next_retry_at"] = (
                get_now_kst() + timedelta(seconds=self.BACKOFF_BASE_SEC * (2 ** (slot["retry"] - 1)))
            ).strftime("%Y-%m-%d %H:%M:%S")
            ledger["slots"][slot_key] = slot
            self._save_ledger(ledger)
            return {"status": slot["status"], "slot_key": slot_key, "error": str(e)}
        finally:
            self._release_lease(slot_key)

    def _build_due_slots(self, now: datetime) -> List[Dict[str, Any]]:
        """현재 시각 기준 due 슬롯 산출 (캐치업 포함)."""
        today_str = now.strftime("%Y-%m-%d")
        due = []
        for slot_id, h, m, channel, kwargs in self.SLOT_TABLE:
            slot_dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
            if now >= slot_dt:
                due.append({
                    "slot_key": f"{today_str}_{slot_id}",
                    "channel": channel,
                    "kwargs": kwargs,
                })
        # 지식iN: 매 30분 오프셋 슬롯
        for h in range(24):
            for m in self.KIN_MINUTES:
                slot_dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
                if now >= slot_dt:
                    due.append({
                        "slot_key": f"{today_str}_kin_{h:02d}{m:02d}",
                        "channel": "kin",
                        "kwargs": {},
                    })
        return due

    def _recover_zombies(self):
        """RUNNING 상태로 남은 좀비 슬롯을 PENDING으로 회수."""
        ledger = self._load_ledger()
        now_ts = time.time()
        changed = False
        for key, slot in ledger.get("slots", {}).items():
            if slot.get("status") == "RUNNING":
                started = slot.get("started_at")
                try:
                    started_dt = datetime.strptime(started, "%Y-%m-%d %H:%M:%S")
                    if (get_now_kst().replace(tzinfo=None) - started_dt).total_seconds() > self.LEASE_TTL_SEC:
                        slot["status"] = "PENDING"
                        slot["last_error"] = "zombie_recovered"
                        changed = True
                        logger.warning(f"♻️ 좀비 슬롯 회수: {key}")
                except Exception:
                    slot["status"] = "PENDING"
                    changed = True
        if changed:
            self._save_ledger(ledger)

    def _should_retry_now(self, slot: Dict[str, Any], now: datetime) -> bool:
        if slot.get("status") != "PENDING":
            return False
        nra = slot.get("next_retry_at")
        if not nra:
            return True
        try:
            return now >= datetime.strptime(nra, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return True

    # 24시간 365일 무인 자율 구동 데몬 (원장 기반 재설계)
    def run_daemon(self):
        logger.info("=" * 60)
        logger.info(f"🤖 [{self.NAME}] 24시간 365일 무인 자율 백그라운드 데몬 가동 (원장 기반)")
        logger.info(f"   • 공식 검색어: '{self.KEYWORD}'")
        logger.info(f"   • 슬롯 원장: {self.LEDGER_PATH}")
        logger.info(f"   • lease TTL: {self.LEASE_TTL_SEC}s / 슬롯 타임아웃: {self.SLOT_TIMEOUT_SEC}s")
        logger.info("=" * 60)

        self._ensure_dirs()

        # 휴먼 비헤이비어 백그라운드 스레드 (별도 격리)
        t_human = threading.Thread(target=self.run_human_behavior, kwargs={"mode": "daemon"}, daemon=True)
        t_human.start()

        last_recover = 0.0
        while True:
            try:
                now = get_now_kst()
                now_naive = now.replace(tzinfo=None)

                # 5분 주기 좀비 회수
                if time.time() - last_recover > 300:
                    self._recover_zombies()
                    last_recover = time.time()

                # due 슬롯 산출 후 순차 실행 (각 슬롯은 lease로 격리)
                due_slots = self._build_due_slots(now_naive)
                ledger = self._load_ledger()

                for item in due_slots:
                    key = item["slot_key"]
                    slot = ledger["slots"].get(key)
                    if slot and slot.get("status") == "DONE":
                        continue
                    if slot and not self._should_retry_now(slot, now_naive):
                        continue
                    logger.info(f"⏰ [{self.NAME}] due 슬롯 실행: {key}")
                    self._execute_slot(key, item["channel"], item["kwargs"])
                    ledger = self._load_ledger()

                time.sleep(20)  # 폴링 주기 단축 (판정은 원장 기반이므로 안전)
            except Exception as e:
                logger.error(f"❌ [{self.NAME} 데몬 오류] {e}\n{traceback.format_exc()}")
                time.sleep(30)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aura AI 데이팅 독립 마케팅 파이프라인")
    parser.add_argument("--channel", choices=["shorts", "cardnews", "human", "cafe", "kin", "blog", "threads", "seo", "all"], help="실행할 채널")
    parser.add_argument("--topic", type=int, default=None, help="지정할 주제 번호")
    parser.add_argument("--force", action="store_true", help="중복 발송 락 무시하고 강제 실행")
    parser.add_argument("--daemon", action="store_true", help="24시간 무인 자율 데몬 모드로 상주 실행")

    args = parser.parse_args()
    pipeline = AuraPipeline(dry_run=False)

    if args.daemon:
        pipeline.run_daemon()
    elif args.channel == "all":
        res = pipeline.run_full_cycle()
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif args.channel:
        res = pipeline.run_channel(args.channel, topic_id=args.topic, force=args.force)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        parser.print_help()
