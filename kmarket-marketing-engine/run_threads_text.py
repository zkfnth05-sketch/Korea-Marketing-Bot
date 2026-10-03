# -*- coding: utf-8 -*-
"""
Threads Text Pipeline Master Runner (🧵 대한민국 3대 브랜드 스레드 순수 텍스트 파이프라인 통합 실행기)
====================================================================================================
- 브랜드:
  1. 💖 Aura AI 데이팅 (아우라AI데이팅)
  2. 🛡️ 보험 리밸런스 (보험 리밸런스)
  3. 📈 StockMaster AI (스톡마스터 AI)
- 역할:
  - 사진 0장! 제미나이 100% 자율 집필 순수 텍스트 단독 글 생성
  - 1번째 댓글(Add to thread)에 공식 검색어 및 공식 랜딩 URL 자동 체인
  - 하루 2회 골든 슬롯 (09:30 모닝 / 19:30 이브닝) 지원
- 사용법:
  python run_threads_text.py --brand aura                # 드라이런 (생성 검증)
  python run_threads_text.py --brand aura --live         # 실제 스레드에 라이브 게시
  python run_threads_text.py --all                       # 3대 브랜드 전체 드라이런
  python run_threads_text.py --all --live                # 3대 브랜드 전체 라이브 게시
  python run_threads_text.py --daemon                    # 24시간 365일 무인 자율 스케줄러 기동
"""

import sys
import json
import argparse
import asyncio
import logging
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("RunThreadsText")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

from brands.aura.aura_threads_text_pipeline import AuraThreadsTextPipeline
from brands.insurance.insurance_threads_text_pipeline import InsuranceThreadsTextPipeline
from brands.stock.stock_threads_text_pipeline import StockThreadsTextPipeline


async def run_single_brand(brand: str, slot: str = "morning", dry_run: bool = True, headless: bool = True):
    brand = brand.lower()
    if brand == "aura":
        pipe = AuraThreadsTextPipeline(headless=headless)
        return await pipe.execute_slot(slot=slot, dry_run=dry_run)
    elif brand == "insurance":
        pipe = InsuranceThreadsTextPipeline(headless=headless)
        return await pipe.execute_slot(slot=slot, dry_run=dry_run)
    elif brand == "stock":
        pipe = StockThreadsTextPipeline(headless=headless)
        return await pipe.execute_slot(slot=slot, dry_run=dry_run)
    else:
        logger.error(f"❌ 알 수 없는 브랜드: {brand}")
        return {"error": f"unknown brand {brand}"}


async def run_all_brands(slot: str = "morning", dry_run: bool = True, headless: bool = True):
    results = {}
    for b in ["aura", "insurance", "stock"]:
        print(f"\n==================== [{b.upper()} 스레드 텍스트 파이프라인 가동] ====================")
        res = await run_single_brand(brand=b, slot=slot, dry_run=dry_run, headless=headless)
        results[b] = res
    return results


async def run_master_daemon():
    """3대 브랜드 스레드 텍스트 하루 2회 동시 무인 데몬"""
    print(f"\n========================================================")
    print(f"🤖 [대한민국 3대 브랜드] 스레드 순수 텍스트 24시간 무인 데몬 가동")
    print(f"• 1. 💖 Aura AI 데이팅 (아우라AI데이팅)")
    print(f"• 2. 🛡️ 보험 리밸런스 (보험 리밸런스)")
    print(f"• 3. 📈 StockMaster AI (스톡마스터 AI)")
    print(f"• ⏰ 1차 슬롯: 09:30 KST (출근/모닝 텍스트 피드)")
    print(f"• ⏰ 2차 슬롯: 19:30 KST (퇴근/야간 텍스트 피크)")
    print(f"========================================================\n")

    executed_today = set()

    while True:
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        h = now.hour
        m = now.minute

        if h == 0 and m < 5:
            executed_today.clear()

        # 09:30 모닝 슬롯
        if h == 9 and m == 30:
            slot_key = f"{today_str}_morning"
            if slot_key not in executed_today:
                logger.info("⏰ [09:30 KST] 3대 브랜드 모닝 스레드 텍스트 동시 기동!")
                await run_all_brands(slot="morning", dry_run=False, headless=True)
                executed_today.add(slot_key)

        # 19:30 이브닝 슬롯
        if h == 19 and m == 30:
            slot_key = f"{today_str}_evening"
            if slot_key not in executed_today:
                logger.info("⏰ [19:30 KST] 3대 브랜드 이브닝 스레드 텍스트 동시 기동!")
                await run_all_brands(slot="evening", dry_run=False, headless=True)
                executed_today.add(slot_key)

        await asyncio.sleep(30)


def main():
    parser = argparse.ArgumentParser(description="Threads Pure Text Pipeline Master Runner")
    parser.add_argument("--brand", type=str, choices=["aura", "insurance", "stock"], help="Target brand")
    parser.add_argument("--all", action="store_true", help="Run for all 3 brands")
    parser.add_argument("--slot", type=str, choices=["morning", "evening"], default="morning", help="Slot time (morning/evening)")
    parser.add_argument("--live", action="store_true", help="Live publishing mode (default: dry-run)")
    parser.add_argument("--headed", action="store_true", help="Run browser with GUI visible")
    parser.add_argument("--daemon", action="store_true", help="Run 24/7 background scheduler")

    args = parser.parse_args()
    dry_run = not args.live
    headless = not args.headed

    if args.daemon:
        asyncio.run(run_master_daemon())
    elif args.all:
        res = asyncio.run(run_all_brands(slot=args.slot, dry_run=dry_run, headless=headless))
        print("\n==================== [3대 브랜드 종합 결과] ====================")
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif args.brand:
        res = asyncio.run(run_single_brand(brand=args.brand, slot=args.slot, dry_run=dry_run, headless=headless))
        print("\n==================== [실행 결과] ====================")
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
