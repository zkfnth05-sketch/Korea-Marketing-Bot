# -*- coding: utf-8 -*-
"""
run_insurance_cardnews.py - 🛡️ [보험 리밸런스 카드뉴스 봇 독립 원클릭 실행 스크립트]
================================================================================
• 숏폼 엔진과 100% 분리된 순수 카드뉴스 전용 실행기
• 시나리오 디렉터 ➔ Wan 2.1 T2I ➔ Playwright 타이포그래피 ➔ 바탕화면 이지텍스 규격 저장
Usage:
    python run_insurance_cardnews.py                  # 다음 순환 주제 5장 풀세트 자동 생산
    python run_insurance_cardnews.py --topic 1        # 특정 주제 (예: 1번 실손보험 개정) 생산
"""

import sys
import logging
from pathlib import Path
import argparse

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("RunInsuranceCardnews")

WORKSPACE_DIR = Path(__file__).resolve().parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from brands.insurance.insurance_cardnews_producer import InsuranceCardnewsProducer


def main():
    parser = argparse.ArgumentParser(description="🛡️ 보험 리밸런스 5장 카드뉴스 무인 생산 진입점")
    parser.add_argument("slide", nargs="?", default="all", help="생성할 슬라이드 번호 또는 'all'")
    parser.add_argument("--topic", "-t", type=int, default=1, help="주제 ID (1~8)")
    args, _ = parser.parse_known_args()

    producer = InsuranceCardnewsProducer()
    topic_id = args.topic

    logger.info(f"🤖 [Insurance Cardnews Bot] {topic_id}번 주제 5장 풀세트 카드뉴스 무인 생산 가동...")
    result = producer.produce_full_package(topic_id=topic_id)

    logger.info("================================================================================")
    logger.info(f"🎉 [성공] {topic_id}번 주제 5장 풀세트 카드뉴스가 완성되었습니다!")
    logger.info(f"📂 저장 경로: {result.get('package_dir')}")
    logger.info(f"📊 총 슬라이드 수: {result.get('slides_count')}장")
    for i, p in enumerate(result.get('slide_files', []), 1):
        logger.info(f"   [{i}/5] {p}")
    logger.info(f"📝 SNS 포스팅 가이드: {result.get('guide_file')}")
    logger.info("================================================================================")
    print("OUTPUT_DIR=" + str(result.get("package_dir", "")))


if __name__ == "__main__":
    main()
