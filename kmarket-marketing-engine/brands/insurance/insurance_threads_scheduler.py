# -*- coding: utf-8 -*-
"""
Insurance Threads Unified Master Scheduler (🛡️ 보험 리밸런스 전용 스레드 [카드뉴스 2회 + 타래텍스트 2회] 4회 무인 스케줄러)
===========================================================================================================================
- 브랜드: 🛡️ 보험 리밸런스 (InsureBalance)
- 전용 계정: @goldmomofficial
- 공식 검색어: 보험 리밸런스 (띄어쓰기 필수, 불변)
- 공식 랜딩 URL: https://insure-rebalance.vercel.app/
- 공식 스케줄 규격 (하루 총 4회):
  1. 🌅 [08:45] morning_text     : 아침 가계부/고정지출 절약 타래 텍스트 #1 + 실시간 15개 해시태그 + 1번 타래글
  2. 🎬 [12:30] lunch_cardnews   : 15.5초 카드뉴스 숏폼 비디오 #1 (점심 피크) + 실시간 15개 해시태그 + 1번 타래글
  3. 🎬 [20:00] evening_cardnews : 15.5초 카드뉴스 숏폼 비디오 #2 (저녁 피크) + 실시간 15개 해시태그 + 1번 타래글
  4. 🌙 [22:30] night_text       : 야간 고정비 다이어트/실손 청구 타래 텍스트 #2 + 실시간 15개 해시태그 + 1번 타래글
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

logger = logging.getLogger("InsuranceThreadsScheduler")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
HISTORY_FILE = CURRENT_DIR / "threads_schedule_history.json"


class InsuranceThreadsScheduler:
    """🛡️ 보험 리밸런스 전용 스레드 카드뉴스 2회 + 타래텍스트 2회 (하루 총 4회) 통합 마스터 스케줄러"""

    BRAND = "insurance"
    BRAND_NAME = "보험 리밸런스"
    OFFICIAL_SEARCH_KEYWORD = "보험 리밸런스"
    LANDING_URL = "https://insure-rebalance.vercel.app/"

    # 하루 4대 공식 골든 슬롯 (카드뉴스 형식 2회 + 타래 텍스트 2회)
    SLOTS = [
        {
            "id": "morning_text",
            "type": "text",
            "writer_slot": "morning",
            "hour": 8,
            "minute": 45,
            "time_str": "08:45",
            "name": "🌅 [08:45] 아침 가계부 절약 타래 텍스트 #1"
        },
        {
            "id": "lunch_cardnews",
            "type": "video",
            "hour": 12,
            "minute": 30,
            "time_str": "12:30",
            "name": "🎬 [12:30] 점심 15.5초 카드뉴스 숏폼 #1"
        },
        {
            "id": "evening_cardnews",
            "type": "video",
            "hour": 20,
            "minute": 0,
            "time_str": "20:00",
            "name": "🎬 [20:00] 저녁 15.5초 카드뉴스 숏폼 #2"
        },
        {
            "id": "night_text",
            "type": "text",
            "writer_slot": "evening",
            "hour": 22,
            "minute": 30,
            "time_str": "22:30",
            "name": "🌙 [22:30] 야간 숨은 보험금/실손 청구 타래 텍스트 #2"
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
            from brands.insurance.insurance_threads_text_pipeline import InsuranceThreadsTextPipeline
            pipeline = InsuranceThreadsTextPipeline(headless=self.headless)
            writer_slot = slot.get("writer_slot", "morning")
            result = await pipeline.execute_slot(slot=writer_slot, dry_run=dry_run)
        else:
            # 🎬 15.5초 카드뉴스 숏폼 비디오 파이프라인
            from brands.insurance.insurance_threads_pipeline import InsuranceThreadsPipeline
            from brands.insurance.insurance_hashtag_matrix import InsuranceHashtagMatrix

            # 산출물 디렉터리에서 최신 보험 카드뉴스 폴더 자동 탐색
            cardnews_base = Path(r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\보험")
            target_folder = None
            if cardnews_base.exists():
                folders = sorted([f for f in cardnews_base.iterdir() if f.is_dir()], key=lambda x: x.stat().st_mtime, reverse=True)
                if folders:
                    # 1회차(lunch): 가장 최신 폴더, 2회차(evening): 차순위 폴더
                    f_idx = 0 if slot_id == "lunch_cardnews" else min(1, len(folders)-1)
                    target_folder = str(folders[f_idx].resolve())
                    logger.info(f"📂 보험 카드뉴스 폴더 매칭 ({slot_id}): {folders[f_idx].name}")

            # 15개 실시간 트렌드 해시태그 생성
            hashtags = " ".join(InsuranceHashtagMatrix.get_threads_hashtags(count=15))
            caption = (
                "🌿 [4인 가족 가계부 고정지출 다이어트]\n\n"
                "매달 숨만 쉬어도 빠져나가는 돈 중에서 '이것'만 정리해도 한 달에 15~20만 원이 그냥 굳어요!\n\n"
                "✔️ 보장은 그대로 든든하게 유지하면서 새는 돈 싹 잡는 법\n"
                "✔️ 15.5초 카드뉴스 영상으로 쉽게 확인해보세요 🤍\n\n"
                f"{hashtags}"
            )

            if dry_run:
                logger.info("⚡ [DRY-RUN] 카드뉴스 숏폼 스레드 발행 건너뜀")
                result = {"success": True, "brand": self.BRAND, "mode": "DRY_RUN", "slot": slot_id, "folder": target_folder}
            else:
                pipeline = InsuranceThreadsPipeline(headless=self.headless)
                result = await pipeline.run_pipeline(
                    cardnews_folder=target_folder,
                    custom_caption=caption
                )

        # 실행 히스토리 보관
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
    parser = argparse.ArgumentParser(description="Insurance Threads Master Scheduler (Cardnews 2x + Text 2x)")
    parser.add_argument("--daemon", action="store_true", help="24시간 무인 데몬 모드 실행")
    parser.add_argument("--slot", type=str, choices=["morning_text", "lunch_cardnews", "evening_cardnews", "night_text"], help="특정 슬롯 즉시 실행")
    parser.add_argument("--dry-run", action="store_true", help="실제 스레드 송출 없이 테스트")
    args = parser.parse_args()

    scheduler = InsuranceThreadsScheduler(headless=True)

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
