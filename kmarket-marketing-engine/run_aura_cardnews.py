# -*- coding: utf-8 -*-
"""
run_aura_cardnews.py - 💖 [Aura 카드뉴스 봇 무인 자율 구동 진입점]
===================================================================
• 숏폼 엔진과 100% 분리된 순수 카드뉴스 전용 실행기
• 시나리오 디렉터 ➔ Wan 2.1 T2I ➔ 타이포그래피 ➔ 바탕화면 이지텍스 규격 저장
"""

import sys
import logging
from pathlib import Path

# 콘솔 UTF-8 설정
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("RunAuraCardnews")

WORKSPACE_DIR = Path(__file__).resolve().parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from brands.aura.aura_cardnews_producer import AuraCardnewsProducer

import argparse

def main():
    parser = argparse.ArgumentParser(description="Aura 5장 카드뉴스 봇 무인 자율 구동 진입점")
    parser.add_argument("slide", nargs="?", default="1", help="생성할 슬라이드 번호 (1~5) 또는 'all' (전체 풀세트)")
    parser.add_argument("--topic", "-t", type=int, default=1, help="주제 ID (1:소개팅탈출, 2:실시간자막, 3:VIP게이트 등)")
    parser.add_argument("--fashion", "-f", type=int, default=None, help="소개팅 착장 프리셋 ID (1~10)")
    args, unknown = parser.parse_known_args()

    producer = AuraCardnewsProducer()
    topic_id = args.topic
    fashion_id = args.fashion

    if args.slide.isdigit():
        slide_num = int(args.slide)
        logger.info(f"🤖 [Aura Cardnews Bot] {topic_id}번 주제 카드뉴스 {slide_num}번 카드 자율 생성 가동 (착장={fashion_id or '기본'})...")
        result = producer.produce_slide(slide_num=slide_num, topic_id=topic_id, fashion_id=fashion_id)
        logger.info("================================================================================")
        logger.info(f"🎉 [성공] {topic_id}번 주제 {slide_num}번 카드 산출물이 바탕화면에 생성되었습니다!")
        logger.info(f"📂 저장 경로: {result['output_dir']}")
        logger.info(f"🖼️ 카드 이미지: {result['slide_path']}")
        logger.info("================================================================================")
        print("OUTPUT_DIR=" + result["output_dir"])
        print(f"SLIDE_{slide_num}=" + result["slide_path"])
    else:
        logger.info(f"🤖 [Aura Cardnews Bot] {topic_id}번 주제 5장 풀세트 카드뉴스 원스톱 자율 생성 가동 (착장={fashion_id or '기본'})...")
        result = producer.produce_cardnews(topic_id=topic_id, fashion_id=fashion_id)
        logger.info("================================================================================")
        logger.info(f"🎉 [성공] {topic_id}번 주제 5장 풀세트 카드뉴스가 바탕화면에 완벽하게 완성되었습니다!")
        logger.info(f"📂 저장 경로: {result['output_dir']}")
        logger.info(f"📊 총 슬라이드 수: {result['total_slides']}장")
        for i, p in enumerate(result['slide_paths'], 1):
            logger.info(f"   [{i}/5] {p}")
        logger.info(f"📝 SNS 포스팅 가이드: {result['guide_path']}")
        logger.info(f"📋 메타데이터: {result['metadata_path']}")
        logger.info("================================================================================")
        print("OUTPUT_DIR=" + result["output_dir"])


if __name__ == "__main__":
    main()
