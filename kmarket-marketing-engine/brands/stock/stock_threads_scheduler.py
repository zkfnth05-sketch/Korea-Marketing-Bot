# -*- coding: utf-8 -*-
"""
StockMaster Threads Unified Master Scheduler (📈 주식AI 전용 스레드 [카드뉴스 2회 + 타래텍스트 2회] 4회 무인 스케줄러)
=======================================================================================================================
- 브랜드: 📈 StockMaster AI (퀀트 주식 AI)
- 전용 계정: @stockmaster_ai
- 공식 검색어: 스톡마스터 AI (띄어쓰기 필수, 불변)
- 공식 랜딩 URL: https://stockmaster-ai.vercel.app/
- 공식 스케줄 규격 (하루 총 4회):
  1. 🌅 [08:10] morning_text     : 장 시작 전 글로벌 증시/테마주 타래 텍스트 #1 + 실시간 15개 해시태그 + 1번 타래글
  2. 🎬 [12:15] lunch_cardnews   : 15.5초 카드뉴스 숏폼 비디오 #1 (점심 퀀트 분석) + 실시간 15개 해시태그 + 1번 타래글
  3. 🎬 [19:00] evening_cardnews : 15.5초 카드뉴스 숏폼 비디오 #2 (장마감 수급 분석) + 실시간 15개 해시태그 + 1번 타래글
  4. 🌙 [21:30] night_text       : 야간 미 증시 프리마켓/퀀트 매매 타래 텍스트 #2 + 실시간 15개 해시태그 + 1번 타래글
- 24시간 365일 100% 무인 상주 데몬 지원
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("StockThreadsScheduler")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
HISTORY_FILE = CURRENT_DIR / "threads_schedule_history.json"


class StockThreadsScheduler:
    """📈 StockMaster AI 전용 스레드 카드뉴스 2회 + 타래텍스트 2회 (하루 총 4회) 통합 마스터 스케줄러"""

    BRAND = "stock"
    BRAND_NAME = "StockMaster AI"
    OFFICIAL_SEARCH_KEYWORD = "스톡마스터 AI"
    LANDING_URL = "https://stockmaster-ai.vercel.app/"

    # 하루 4대 공식 골든 슬롯 (카드뉴스 형식 2회 + 타래 텍스트 2회)
    SLOTS = [
        {
            "id": "morning_text",
            "type": "text",
            "writer_slot": "morning",
            "hour": 8,
            "minute": 10,
            "time_str": "08:10",
            "name": "🌅 [08:10] 장전 글로벌/테마주 타래 텍스트 #1"
        },
        {
            "id": "lunch_cardnews",
            "type": "video",
            "hour": 12,
            "minute": 15,
            "time_str": "12:15",
            "name": "🎬 [12:15] 점심 퀀트 15.5초 카드뉴스 숏폼 #1"
        },
        {
            "id": "evening_cardnews",
            "type": "video",
            "hour": 19,
            "minute": 0,
            "time_str": "19:00",
            "name": "🎬 [19:00] 장마감 수급 15.5초 카드뉴스 숏폼 #2"
        },
        {
            "id": "night_text",
            "type": "text",
            "writer_slot": "evening",
            "hour": 21,
            "minute": 30,
            "time_str": "21:30",
            "name": "🌙 [21:30] 미 증시/퀀트 시그널 타래 텍스트 #2"
        }
    ]

    def __init__(self, headless: bool = True):
        self.headless = headless

    async def execute_slot(self, slot_id: str, dry_run: bool = False) -> Dict[str, Any]:
        """지정된 슬롯 1회 실행"""
        slot = next((s for s in self.SLOTS if s["id"] == slot_id), None)
        if not slot:
            logger.error(f"❌ 알 수 없는 슬롯 ID: {slot_id}")
            return {"success": False, "error": f"Invalid slot_id: {slot_id}"}

        logger.info(f"\n🚀 [{self.BRAND_NAME}] 스레드 스케줄 가동 ➔ {slot['name']} (모드: {'DRY-RUN' if dry_run else 'LIVE'})")

        if slot["type"] == "text":
            from brands.stock.stock_threads_text_pipeline import StockThreadsTextPipeline
            pipeline = StockThreadsTextPipeline(headless=self.headless)
            writer_slot = slot.get("writer_slot", "morning")
            result = await pipeline.execute_slot(slot=writer_slot, dry_run=dry_run)
        else:
            # 🎬 15.5초 카드뉴스 숏폼 비디오 파이프라인
            from brands.stock.stock_threads_pipeline import StockThreadsPipeline
            from brands.stock.stock_hashtag_matrix import StockHashtagMatrix

            cardnews_base = Path(r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\주식")
            target_folder = None
            if cardnews_base.exists():
                folders = sorted([f for f in cardnews_base.iterdir() if f.is_dir()], key=lambda x: x.stat().st_mtime, reverse=True)
                if folders:
                    f_idx = 0 if slot_id == "lunch_cardnews" else min(1, len(folders)-1)
                    target_folder = str(folders[f_idx].resolve())
                    logger.info(f"📂 주식 카드뉴스 폴더 매칭 ({slot_id}): {folders[f_idx].name}")

            hashtags = " ".join(StockHashtagMatrix.get_threads_hashtags(count=15))
            caption = (
                "📈 [StockMaster AI 퀀트 급등주 시그널]\n\n"
                "외인/기관 동시 순매수 & 실시간 AI 골든크로스 포착!\n"
                "감정에 휘둘리지 않는 100% 퀀트 알고리즘 매매를 지금 확인해보세요 ✨\n\n"
                "✔️ 15.5초 카드뉴스 영상으로 확인해 보세요!\n\n"
                f"{hashtags}"
            )

            if dry_run:
                logger.info("⚡ [DRY-RUN] 카드뉴스 숏폼 스레드 발행 건너뜀")
                result = {"success": True, "brand": self.BRAND, "mode": "DRY_RUN", "slot": slot_id, "folder": target_folder}
            else:
                pipeline = StockThreadsPipeline(headless=self.headless)
                result = await pipeline.run_pipeline(
                    cardnews_folder=target_folder,
                    custom_caption=caption
                )

        self._record_history(slot_id, slot["type"], result)
        return result

    def _record_history(self, slot_id: str, slot_type: str, result: Dict[str, Any]):
        history = []
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []
        history.append({
            "brand": self.BRAND,
            "slot_id": slot_id,
            "slot_type": slot_type,
            "timestamp": datetime.now().isoformat(),
            "success": result.get("success", False),
            "result": result
        })
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    async def run_daemon(self):
        """24시간 365일 무인 자율 데몬 루프"""
        logger.info(f"🤖 [{self.BRAND_NAME}] 스레드 하루 4회(카드뉴스 2회 + 타래텍스트 2회) 무인 상주 데몬 가동 시작!")
        for s in self.SLOTS:
            logger.info(f"   ⏰ {s['time_str']} -> {s['name']}")

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
                        logger.info(f"⏰ [정시 기상] {slot['name']} 자동 발행 시작!")
                        await self.execute_slot(slot["id"], dry_run=False)
                        executed_today.add(slot_key)
                        logger.info(f"💤 [슬롯 완료] {slot['name']} 완료 후 대기 모드 복귀")

            await asyncio.sleep(25)


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Stock Threads Master Scheduler (Cardnews 2x + Text 2x)")
    parser.add_argument("--daemon", action="store_true", help="24시간 무인 데몬 모드 실행")
    parser.add_argument("--slot", type=str, choices=["morning_text", "lunch_cardnews", "evening_cardnews", "night_text"], help="특정 슬롯 즉시 실행")
    parser.add_argument("--dry-run", action="store_true", help="실제 스레드 송출 없이 테스트")
    args = parser.parse_args()

    scheduler = StockThreadsScheduler(headless=True)

    if args.daemon:
        await scheduler.run_daemon()
    elif args.slot:
        res = await scheduler.execute_slot(args.slot, dry_run=args.dry_run)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print("💡 슬롯 미지정: 기본 'morning_text' DRY-RUN 테스트를 실행합니다.")
        res = await scheduler.execute_slot("morning_text", dry_run=True)
        print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
