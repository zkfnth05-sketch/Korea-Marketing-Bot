# -*- coding: utf-8 -*-
"""
Stock Shorts Runner (📈 StockMaster AI 숏폼 독립 원클릭 실행 스크립트)
========================================================================
Usage:
    python run_stock_shorts.py                  # 다음 순환 주제 1건 숏폼 자동 생산
    python run_stock_shorts.py --topic 1        # 특정 주제 (예: 1번 삼전 vs 하이닉스) 숏폼 생산
    python run_stock_shorts.py --photo --topic 1 # 마스터 실사 사진만 단독 렌더링
    python run_stock_shorts.py --all            # 1~8번 주제 연속 자동 생산
"""

import sys
import argparse
import logging

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("StockShortsRunner")

from brands.stock.stock_shorts_pipeline import StockShortsPipeline


def main():
    parser = argparse.ArgumentParser(description="📈 StockMaster AI 숏폼 무인 생산 러너")
    parser.add_argument("--topic", "-t", type=int, default=None, help="주제 ID (1~8)")
    parser.add_argument("--gender", "-g", type=str, default=None, choices=["female", "male"], help="모델 성별")
    parser.add_argument("--seed", "-s", type=int, default=None, help="난수 시드")
    parser.add_argument("--photo", "-p", action="store_true", help="Wan 2.1 마스터 사진만 단독 생성")
    parser.add_argument("--all", "-a", action="store_true", help="1~8번 주제 연속 생산")
    args = parser.parse_args()

    pipeline = StockShortsPipeline()

    if args.photo:
        print("\n🎨 [StockShorts] Wan 2.1 마스터 사진 단독 생산 가동...")
        res = pipeline.produce_master_photo(topic_id=args.topic, gender=args.gender, seed=args.seed)
        print(f"🎉 [사진 완료] 저장 경로: {res.get('photo_path')}")
        return

    if args.all:
        print("\n🚀 [StockShorts] 1~8번 주제 연속 무인 숏폼 생산 가동...")
        results = pipeline.produce_topics(start_topic=1, end_topic=8, gender=args.gender)
        print(f"🎉 [전체 완료] 총 {len(results)}건 생산 완료")
        return

    print("\n🚀 [StockShorts] 22초 하이브리드 완제품 숏폼 생산 가동...")
    out_mp4 = pipeline.produce(topic_id=args.topic, gender=args.gender, seed=args.seed)
    print(f"\n🎉 [생산 완결] 완제품 MP4: {out_mp4}")


if __name__ == "__main__":
    main()
