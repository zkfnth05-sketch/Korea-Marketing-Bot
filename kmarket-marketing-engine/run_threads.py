# -*- coding: utf-8 -*-
r"""
Threads Omni Pipeline Runner (🧵 3대 브랜드 스레드 독립 파이프라인 전용 실행기)
================================================================================
- 역할:
  1. 3대 브랜드(Aura, 보험 리밸런스, StockMaster) 스레드 전용 독립 송출
  2. 카드뉴스 이미지(슬라이드 4~5장) 및 텍스트 스토리 타래 선택 송출 지원
  3. 첫 번째 타래 댓글로 공식 검색어 및 랜딩 URL 자동 체인 부착
- 사용법:
  - 아우라 특정 카드뉴스 폴더 송출:
    python run_threads.py --brand aura --folder "C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\아우라\아우라_08_500m안심레이더_20261001_1100"
  - 브랜드별 최신 카드뉴스 자동 송출:
    python run_threads.py --brand aura
    python run_threads.py --brand insurance
    python run_threads.py --brand stock
  - 3대 브랜드 일괄 송출:
    python run_threads.py --all
"""

import os
import sys
import argparse
import asyncio
import logging
from pathlib import Path
from typing import Optional, List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("RunThreads")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR


async def publish_brand_threads(brand: str, folder_path: Optional[str] = None, headless: bool = True):
    brand = brand.lower()
    
    # 1. 대상 이미지 및 캡션 준비
    image_paths = []
    caption = ""
    first_reply = ""
    
    if folder_path:
        target_dir = Path(folder_path)
        if not target_dir.exists():
            logger.error(f"❌ 대상 폴더가 존재하지 않습니다: {folder_path}")
            return
        
        # 슬라이드 이미지 수집 (slide_1.png ~ slide_5.png 정렬)
        for i in range(1, 10):
            slide_file = target_dir / f"slide_{i}.png"
            if slide_file.exists():
                image_paths.append(str(slide_file.resolve()))
        
        if not image_paths:
            # 기타 이미지 탐색
            for f in sorted(target_dir.glob("*.png")):
                image_paths.append(str(f.resolve()))
        
        # SNS 포스팅 가이드 텍스트 탐색
        guide_file = target_dir / "SNS_포스팅_가이드_KO.txt"
        if guide_file.exists():
            try:
                with open(guide_file, "r", encoding="utf-8") as f:
                    guide_content = f.read()
                    # 본문 발췌
                    caption = guide_content.strip()
                    # 너무 길면 축약 또는 첫 500자
                    if len(caption) > 480:
                        lines = caption.split("\n")
                        caption = "\n".join(lines[:12])
            except Exception as e:
                logger.warning(f"가이드 읽기 오류: {e}")

    # 기본 캡션 세팅
    if not caption:
        if brand == "aura":
            caption = (
                "📍 [500m 안심 레이더 & 매칭 리포트]\n\n"
                "거리와 취향까지 딱 맞는 내 반경 500m 인연 찾기!\n"
                "가장 솔직하고 안심되는 매칭을 지금 확인해보세요 ✨\n\n"
                "#Aura #데이팅 #소개팅 #안심매칭 #2030"
            )
        elif brand == "insurance":
            caption = (
                "🛡️ [매달 줄줄 새는 보험료 3분 진단]\n\n"
                "나도 모르게 중복 결제되고 있던 특약이 있다?\n"
                "보장은 든든하게 늘리고 보험료는 30% 다이어트하세요!\n\n"
                "#보험리밸런스 #보험절약 #실손보험 #보험비교"
            )
        elif brand == "stock":
            caption = (
                "📈 [오늘의 실시간 외국인/기관 수급 급증 TOP 5]\n\n"
                "급등 전 포착된 큰손들의 매수 시그널 분석!\n"
                "3초 만에 확인하는 핵심 테마 브리핑 📊\n\n"
                "#스톡마스터AI #주식AI #수급분석 #급등주 #테마주"
            )

    # 2. 브랜드별 독립 퍼블리셔 호출
    if brand == "aura":
        from brands.aura.aura_threads_publisher import AuraThreadsPublisher
        pub = AuraThreadsPublisher(headless=headless)
        return await pub.publish_thread(caption=caption, image_paths=image_paths)
    elif brand == "insurance":
        from brands.insurance.insurance_threads_publisher import InsuranceThreadsPublisher
        pub = InsuranceThreadsPublisher(headless=headless)
        return await pub.publish_thread(caption=caption, image_paths=image_paths)
    elif brand == "stock":
        from brands.stock.stock_threads_publisher import StockThreadsPublisher
        pub = StockThreadsPublisher(headless=headless)
        return await pub.publish_thread(caption=caption, image_paths=image_paths)
    else:
        logger.error(f"❌ 알 수 없는 브랜드: {brand}")


def main():
    parser = argparse.ArgumentParser(description="Threads Dedicated Omni Pipeline Runner")
    parser.add_argument("--brand", type=str, choices=["aura", "insurance", "stock"], help="Target brand")
    parser.add_argument("--folder", type=str, help="Path to cardnews output folder containing slide images")
    parser.add_argument("--all", action="store_true", help="Publish to all 3 brands")
    parser.add_argument("--headed", action="store_true", help="Run with browser visible")
    args = parser.parse_args()

    headless = not args.headed

    if args.all:
        for b in ["aura", "insurance", "stock"]:
            print(f"\n==================== [{b.upper()} 스레드 송출] ====================")
            asyncio.run(publish_brand_threads(brand=b, headless=headless))
    elif args.brand:
        print(f"\n==================== [{args.brand.upper()} 스레드 송출] ====================")
        res = asyncio.run(publish_brand_threads(brand=args.brand, folder_path=args.folder, headless=headless))
        print(res)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
