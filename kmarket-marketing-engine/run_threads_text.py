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
from datetime import datetime, timedelta, time

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
    """3대 브랜드 스레드 텍스트 하루 2회 동시 무인 데몬

    🛡️ [15분 간격 자가치유 슬롯 가디언 (Self-Healing Slot Guardian)]
      - 모닝 윈도우: 09:30 ~ 16:00 / 이브닝 윈도우: 19:30 ~ 23:59
      - 브랜드별 완료 여부(completed_slots)를 개별 추적 → 하루 정량(브랜드당 2회) 완수
      - 실패/미완료 시 즉시 포기하지 않고 15분 쿨다운(next_retry_at) 후 자율 재시도
      - 💰 요금 폭탄 원천 차단: 파이프라인이 [파이썬 검증 완료 후 제미나이 1회 호출]
        (Lazy Evaluation) 구조이므로, 브라우저 진입/작성창 활성화 실패 단계에서는
        제미나이 API 호출이 0회 → 15분 재시도가 무한 반복되어도 과금이 발생하지 않음.
    """
    print(f"\n========================================================")
    print(f"🤖 [대한민국 3대 브랜드] 스레드 순수 텍스트 24시간 무인 데몬 가동")
    print(f"• 1. 💖 Aura AI 데이팅 (아우라AI데이팅)")
    print(f"• 2. 🛡️ 보험 리밸런스 (보험 리밸런스)")
    print(f"• 3. 📈 StockMaster AI (스톡마스터 AI)")
    print(f"• ⏰ 1차 슬롯: 09:30 KST (출근/모닝 텍스트 피드) — 윈도우 09:30~16:00")
    print(f"• ⏰ 2차 슬롯: 19:30 KST (퇴근/야간 텍스트 피크) — 윈도우 19:30~23:59")
    print(f"• 🛡️ 자가치유: 실패 시 15분 쿨다운 후 당일 슬롯 완수까지 자율 재시도")
    print(f"• 💰 요금 안전: 브라우저 진입 실패 단계에서는 제미나이 호출 0회 (Lazy)")
    print(f"========================================================\n")

    BRANDS = ["aura", "insurance", "stock"]
    RETRY_COOLDOWN = timedelta(minutes=15)

    # 슬롯 윈도우 정의: (시작 시각, 종료 시각)
    SLOT_WINDOWS = {
        "morning": (time(hour=9, minute=30), time(hour=16, minute=0)),
        "evening": (time(hour=19, minute=30), time(hour=23, minute=59, second=59)),
    }

    current_day = None
    completed_slots = set()   # {(brand, slot)} — success=True 인 항목만 등록
    next_retry_at = {}        # {(brand, slot): datetime} — 15분 쿨다운 만료 시각
    attempt_count = {}        # {(brand, slot): int} — 시도 횟수 (로그용)

    while True:
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        now_t = now.time()

        # ── 날짜 롤오버: 자정 경과 시 당일 상태 전면 초기화 ──
        if current_day != today_str:
            if current_day is not None:
                logger.info(f"🌅 [날짜 전환] {current_day} → {today_str} · 슬롯 상태 초기화")
            current_day = today_str
            completed_slots.clear()
            next_retry_at.clear()
            attempt_count.clear()

        # ── 브랜드 × 슬롯 전수 점검 ──
        for slot, (win_start, win_end) in SLOT_WINDOWS.items():
            if not (win_start <= now_t <= win_end):
                continue  # 윈도우 밖 → 대기

            for brand in BRANDS:
                key = (brand, slot)
                if key in completed_slots:
                    continue  # 당일 이미 성공 완료

                # 15분 쿨다운 미도달 → 대기
                retry_at = next_retry_at.get(key)
                if retry_at is not None and now < retry_at:
                    continue

                attempt_count[key] = attempt_count.get(key, 0) + 1
                attempt = attempt_count[key]
                logger.info(
                    f"⏰ [{slot.upper()} 윈도우 {win_start.strftime('%H:%M')}~{win_end.strftime('%H:%M')}] "
                    f"[{brand.upper()}] 시도 #{attempt} 기동 "
                    f"(완료 {len(completed_slots)}/{len(BRANDS) * len(SLOT_WINDOWS)} · "
                    f"💰 브라우저 진입 실패 시 제미나이 호출 0회 보장)"
                )

                try:
                    res = await run_single_brand(
                        brand=brand, slot=slot, dry_run=False, headless=True
                    )
                except Exception as e:
                    logger.error(f"💥 [{brand.upper()}/{slot}] 파이프라인 예외: {e}")
                    res = {"success": False, "error": str(e)}

                if isinstance(res, dict) and res.get("success") is True:
                    completed_slots.add(key)
                    next_retry_at.pop(key, None)
                    logger.info(
                        f"✅ [{brand.upper()}/{slot}] 당일 슬롯 완수! "
                        f"(누적 {len(completed_slots)}/{len(BRANDS) * len(SLOT_WINDOWS)})"
                    )
                else:
                    next_retry_at[key] = datetime.now() + RETRY_COOLDOWN
                    logger.warning(
                        f"⚠️ [{brand.upper()}/{slot}] 미완료 → 15분 쿨다운 후 자가치유 재시도 예약 "
                        f"(다음 시도: {next_retry_at[key].strftime('%H:%M:%S')} · "
                        f"💰 이 재시도는 제미나이 호출 0회 구간에서 발생)"
                    )

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
