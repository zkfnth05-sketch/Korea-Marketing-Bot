# -*- coding: utf-8 -*-
"""
Threads Human Routine Runner (🧵 3대 브랜드 스레드 인간 행동 봇 전용 실행기)
=============================================================================
- 역할:
  1. 3대 브랜드(Aura, 보험 리밸런스, StockMaster AI) 스레드 인간 행동 독립 실행
  2. 일상/유머/맛집(50%) + 타겟 관심사(50%) 자연스러운 체류 & 좋아요 2~3회
  3. 섀도우밴 원천 차단 및 For You 추천 알고리즘 점수 부스팅
- 사용법:
  python run_threads_human.py --brand aura
  python run_threads_human.py --brand insurance
  python run_threads_human.py --brand stock
  python run_threads_human.py --all
"""

import sys
import argparse
import asyncio
import logging

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("RunThreadsHuman")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


async def run_brand_human_routine(brand: str, duration_sec: int = 600, target_likes: int = 3, headless: bool = True):
    brand = brand.lower()
    if brand == "aura":
        from brands.aura.aura_threads_human_bot import AuraThreadsHumanBot
        bot = AuraThreadsHumanBot(headless=headless)
        return await bot.run_session(duration_sec=duration_sec, target_likes=target_likes)
    elif brand == "insurance":
        from brands.insurance.insurance_threads_human_bot import InsuranceThreadsHumanBot
        bot = InsuranceThreadsHumanBot(headless=headless)
        return await bot.run_session(duration_sec=duration_sec, target_likes=target_likes)
    elif brand == "stock":
        from brands.stock.stock_threads_human_bot import StockThreadsHumanBot
        bot = StockThreadsHumanBot(headless=headless)
        return await bot.run_session(duration_sec=duration_sec, target_likes=target_likes)
    else:
        logger.error(f"❌ 알 수 없는 브랜드: {brand}")


def main():
    parser = argparse.ArgumentParser(description="Threads Dedicated Human Routine Runner")
    parser.add_argument("--brand", type=str, choices=["aura", "insurance", "stock"], help="Target brand")
    parser.add_argument("--all", action="store_true", help="Run for all 3 brands sequentially")
    parser.add_argument("--duration", type=int, default=600, help="Dwell duration in seconds (default: 600)")
    parser.add_argument("--likes", type=int, default=3, help="Target likes per session (default: 3)")
    parser.add_argument("--headed", action="store_true", help="Run with browser visible")
    args = parser.parse_args()

    headless = not args.headed

    if args.all:
        for b in ["aura", "insurance", "stock"]:
            print(f"\n==================== [{b.upper()} 스레드 인간 행동 봇 가동] ====================")
            asyncio.run(run_brand_human_routine(brand=b, duration_sec=args.duration, target_likes=args.likes, headless=headless))
    elif args.brand:
        print(f"\n==================== [{args.brand.upper()} 스레드 인간 행동 봇 가동] ====================")
        res = asyncio.run(run_brand_human_routine(brand=args.brand, duration_sec=args.duration, target_likes=args.likes, headless=headless))
        print(res)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
