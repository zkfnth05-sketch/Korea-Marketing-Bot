# -*- coding: utf-8 -*-
"""
Stock Shorts Runner (📈 StockMaster AI 숏폼 독립 원클릭 실행 스크립트)
========================================================================
Usage:
    python run_stock_shorts.py                  # 다음 순환 주제 1건 숏폼 자동 생산
    python run_stock_shorts.py --topic 1        # 특정 주제 (예: 1번 삼전 vs 하이닉스) 숏폼 생산
    python run_stock_shorts.py --photo --topic 1 # 마스터 실사 사진만 단독 렌더링
    python run_stock_shorts.py --all            # 1~8번 주제 연속 자동 생산
    python run_stock_shorts.py --all --no-publish  # 🌙 야간보관 모드: 렌더링만, SNS 송출 차단
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
    parser.add_argument("--no-publish", action="store_true", help="SNS 자동 송출 차단 (순수 렌더링 파일만 저장)")
    args = parser.parse_args()

    # 🌙 야간보관 모드 판정: --no-publish 지정 시 SNS 자동 송출 전면 차단
    auto_publish = not args.no_publish
    publish_state = "ON" if auto_publish else "OFF(야간보관)"

    logger.info(f"📡 [StockShorts Runner] auto_publish = {publish_state} (SNS 자동 송출 {'허용' if auto_publish else '차단'})")

    pipeline = StockShortsPipeline()

    if args.photo:
        print("\n🎨 [StockShorts] Wan 2.1 마스터 사진 단독 생산 가동...")
        print(f"📡 [StockShorts] auto_publish = {publish_state} (사진 단독 모드는 SNS 송출 없음)")
        res = pipeline.produce_master_photo(topic_id=args.topic, gender=args.gender, seed=args.seed)
        print(f"🎉 [사진 완료] 저장 경로: {res.get('photo_path')}")
        return

    if args.all:
        print(f"\n🚀 [StockShorts] 1~8번 주제 연속 무인 숏폼 생산 가동... (auto_publish = {publish_state})")
        results = pipeline.produce_topics(
            start_topic=1,
            end_topic=8,
            gender=args.gender,
            auto_publish=auto_publish
        )
        print(f"🎉 [전체 완료] 총 {len(results)}건 생산 완료 (auto_publish = {publish_state})")
        return

    print(f"\n🚀 [StockShorts] 22초 하이브리드 완제품 숏폼 생산 가동... (auto_publish = {publish_state})")
    out_mp4 = pipeline.produce(
        topic_id=args.topic,
        gender=args.gender,
        seed=args.seed,
        auto_publish=auto_publish
    )
    print(f"\n🎉 [생산 완결] 완제품 MP4: {out_mp4}")
    print(f"📡 [송출 상태] auto_publish = {publish_state}")


if __name__ == "__main__":
    main()
