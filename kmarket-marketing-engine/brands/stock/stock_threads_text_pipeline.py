# -*- coding: utf-8 -*-
"""
Stock Threads Text Pipeline (📈 StockMaster AI 전용 스레드 순수 텍스트 하루 2회 자율 파이프라인)
===================================================================================================
- 브랜드: 📈 StockMaster AI (주식 AI)
- 공식 검색어: 스톡마스터 AI (띄어쓰기 필수)
- 공식 랜딩 URL: https://stockmaster-ai.vercel.app/
- 역할:
  1. 제미나이 텍스트 집필기(StockThreadsTextWriter)를 통한 사진 0장 순수 텍스트 생성
  2. 스레드 발행기(StockThreadsPublisher)를 통해 image_paths=None 순수 텍스트 + 첫 댓글 체인 발행
  3. 하루 2회 골든 슬롯(오전 09:30, 저녁 19:30) 자동 스케줄링 및 히스토리 아카이빙
"""

import os
import sys
import json
import time
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("StockThreadsTextPipeline")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs" / "stock" / "threads_text"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_FILE = CURRENT_DIR / "threads_text_history.json"

from brands.stock.stock_threads_text_writer import StockThreadsTextWriter
from brands.stock.stock_threads_publisher import StockThreadsPublisher


class StockThreadsTextPipeline:
    """📈 StockMaster AI 스레드 순수 텍스트 하루 2회 독립 파이프라인"""

    BRAND = "stock"
    BRAND_NAME = "StockMaster AI"

    SLOTS = [
        {"id": "morning", "time": "09:30", "hour": 9, "minute": 30, "name": "🌅 오전 09:30 개장/모닝 텍스트 피드"},
        {"id": "evening", "time": "19:30", "hour": 19, "minute": 30, "name": "🌙 저녁 19:30 장마감/야간 텍스트 피크"}
    ]

    def __init__(self, headless: bool = True):
        self.writer = StockThreadsTextWriter()
        self.publisher = StockThreadsPublisher(headless=headless)

    def generate_content(self, slot: str = "morning", custom_theme: Optional[str] = None) -> Dict[str, Any]:
        """제미나이 텍스트 글 생성 및 로컬 저장"""
        post_pkg = self.writer.generate_thread_post(slot=slot, custom_theme=custom_theme)
        
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        pkg_file = OUTPUTS_DIR / f"stock_thread_text_{slot}_{now_str}.json"
        with open(pkg_file, "w", encoding="utf-8") as f:
            json.dump(post_pkg, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 [Stock] 신규 스레드 텍스트 로컬 보관 완료: {pkg_file.name}")
        post_pkg["local_file"] = str(pkg_file)
        return post_pkg

    async def execute_slot(self, slot: str = "morning", dry_run: bool = False, custom_theme: Optional[str] = None) -> Dict[str, Any]:
        """슬롯 1회 텍스트 생성 및 스레드 라이브 송출

        🧬 지연 생성(Lazy Evaluation) 계약:
          - DRY-RUN: 사전에 generate_content 를 1회 호출하여 결과만 반환 (발행 없음)
          - LIVE   : 사전 호출 0회. publish_thread 에 content_generator 콜백을 넘겨
                     브라우저 작성창(textbox)이 실제로 활성화된 직후에만
                     제미나이가 단 1회 호출되도록 보장한다.
                     (세션 만료/작성창 미개설/네비게이션 실패 시 Gemini 호출 0회)
        """
        logger.info(f"🚀 [{self.BRAND_NAME}] 스레드 순수 텍스트 파이프라인 가동 (슬롯: {slot}, 모드: {'DRY-RUN' if dry_run else 'LIVE'})")

        # ── 1) DRY-RUN: 사전 생성 후 즉시 반환 (실제 배포 없음) ──
        if dry_run:
            content = self.generate_content(slot=slot, custom_theme=custom_theme)
            logger.info("⚡ [DRY-RUN] 실제 스레드 배포는 건너뜁니다.")
            return {
                "success": True,
                "brand": self.BRAND,
                "mode": "DRY_RUN",
                "slot": slot,
                "content": content
            }

        # ── 2) LIVE: 제미나이 사전 호출 금지 → 작성창 활성화 직후 1회 호출 ──
        logger.info("🧬 [LAZY] LIVE 모드 — 제미나이 호출을 작성창 활성화 시점까지 지연합니다.")

        def _lazy_generate() -> Dict[str, Any]:
            """publish_thread 내부에서 작성창 포커스 확인 직후 1회만 실행되는 생성기"""
            logger.info("🧬 [LAZY] 작성창 활성화 확인 → 제미나이 텍스트 생성 1회 실행")
            content = self.generate_content(slot=slot, custom_theme=custom_theme)
            return {
                "caption": content.get("caption", ""),
                "first_reply_text": content.get("first_reply", ""),
                "topic": content.get("topic", ""),
            }

        pub_res = await self.publisher.publish_thread(
            caption=None,
            image_paths=None,
            first_reply_text=None,
            content_generator=_lazy_generate
        )

        # ── 3) 히스토리 아카이빙 (pub_res 기반) ──
        details = pub_res.get("details") or {}
        record = {
            "brand": self.BRAND,
            "slot": slot,
            "topic": details.get("topic", ""),
            "caption_preview": (details.get("caption_preview") or "")[:60],
            "published_at": datetime.now().isoformat(),
            "publish_result": pub_res,
            "success": pub_res.get("success", False)
        }
        self._save_history(record)

        return {
            "success": pub_res.get("success", False),
            "brand": self.BRAND,
            "slot": slot,
            "publish_result": pub_res
        }

    def _save_history(self, record: Dict[str, Any]):
        history = []
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []
        history.append(record)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    async def run_daemon(self):
        """24시간 무인 자율 데몬 (하루 2회 09:30, 19:30 자동 발행)"""
        logger.info(f"🤖 [{self.BRAND_NAME}] 스레드 텍스트 하루 2회 무인 데몬 가동 (09:30, 19:30)")
        executed_today = set()

        while True:
            now = datetime.now()
            today_str = now.strftime("%Y-%m-%d")
            h = now.hour
            m = now.minute

            if h == 0 and m < 5:
                executed_today.clear()

            for slot in self.SLOTS:
                slot_key = f"{today_str}_{slot['id']}"
                if slot_key not in executed_today:
                    if h == slot["hour"] and m == slot["minute"]:
                        logger.info(f"⏰ [정시 기상] {slot['name']} 텍스트 발행 시작!")
                        await self.execute_slot(slot=slot["id"], dry_run=False)
                        executed_today.add(slot_key)
                        logger.info(f"💤 [슬롯 완료] {slot['name']} 완료 후 대기 모드 진입")

            await asyncio.sleep(30)


if __name__ == "__main__":
    pipeline = StockThreadsTextPipeline(headless=True)
    res = asyncio.run(pipeline.execute_slot(slot="morning", dry_run=True))
    print(json.dumps(res, ensure_ascii=False, indent=2))
