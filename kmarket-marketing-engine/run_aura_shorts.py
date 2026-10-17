# -*- coding: utf-8 -*-
"""
Aura Shorts Runner (💖 Aura AI 데이팅 숏폼 독립 원클릭 실행 스크립트)
===================================================================
Usage:
    python run_aura_shorts.py                  # 다음 순환 주제 1건 숏폼 자동 생산
    python run_aura_shorts.py --topic 1        # 특정 주제 (예: 1번 긴급탈출) 숏폼 생산
    python run_aura_shorts.py --no-publish     # 야간 렌더링 전용 (SNS 송출 없이 파일만 생성)
    python run_aura_shorts.py --photo --topic 1 # 마스터 실사 사진만 단독 렌더링
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
logger = logging.getLogger("AuraShortsRunner")

from brands.aura.aura_shorts_pipeline import AuraShortsPipeline


def main():
    parser = argparse.ArgumentParser(description="💖 Aura AI 데이팅 숏폼 무인 생산 러너")
    parser.add_argument("--topic", "-t", type=int, default=None, help="주제 ID (1~8)")
    parser.add_argument("--gender", "-g", type=str, default=None, choices=["female", "male"], help="모델 성별")
    parser.add_argument("--seed", "-s", type=int, default=None, help="난수 시드")
    parser.add_argument("--no-publish", action="store_true", help="SNS 자동 송출 차단 (순수 렌더링 파일만 저장)")
    parser.add_argument("--photo", "-p", action="store_true", help="Wan 2.1 마스터 사진만 단독 생성")
    args = parser.parse_args()

    pipeline = AuraShortsPipeline()

    if args.photo:
        print("\n🎨 [AuraShorts] Wan 2.1 마스터 사진 단독 생산 가동...")
        res = pipeline.produce_master_photo(topic_id=args.topic, gender=args.gender, seed=args.seed)
        print(f"🎉 [사진 완료] 저장 경로: {res.get('photo_path')}")
        return

    auto_publish = not args.no_publish
    print(f"\n🚀 [AuraShorts] 24초 완제품 숏폼 생산 가동 (자동송출={'ON' if auto_publish else 'OFF(야간보관)'})...")
    out_mp4 = pipeline.produce(
        topic_id=args.topic,
        gender=args.gender,
        seed=args.seed,
        auto_publish=auto_publish
    )
    print(f"\n🎉 [생산 완결] 완제품 MP4: {out_mp4}")


if __name__ == "__main__":
    main()
