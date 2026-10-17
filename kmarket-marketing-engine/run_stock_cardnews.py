# -*- coding: utf-8 -*-
"""
run_stock_cardnews.py - 📈 [StockMaster AI 주식 카드뉴스 봇 독립 원클릭 실행 스크립트]
====================================================================================
• 숏폼 엔진과 100% 분리된 순수 카드뉴스 전용 실행기
• 라이브 웹앱 실시간 데이터 추출 ➔ 제미나이 카피 ➔ Wan 2.1 실사 표지 + 대형 폰뷰 5장 렌더링
Usage:
    python run_stock_cardnews.py                  # 다음 순환 주제 5장 풀세트 자동 생산
    python run_stock_cardnews.py --topic 1        # 특정 주제 (예: 1번 삼전 vs 하이닉스) 생산
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
logger = logging.getLogger("RunStockCardnews")

WORKSPACE_DIR = Path(__file__).resolve().parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from brands.stock.stock_omni_cardnews_pilot import StockOmniCardnewsPilot


def main():
    parser = argparse.ArgumentParser(description="📈 StockMaster AI 5장 카드뉴스 무인 생산 진입점")
    parser.add_argument("slide", nargs="?", default="all", help="생성할 슬라이드 번호 또는 'all'")
    parser.add_argument("--topic", "-t", type=int, default=1, help="주제 ID (1~8)")
    args, _ = parser.parse_known_args()

    pilot = StockOmniCardnewsPilot()
    topic_id = args.topic

    logger.info(f"🤖 [Stock Cardnews Bot] {topic_id}번 주제 5장 풀세트 카드뉴스 무인 생산 가동...")
    slides = pilot.produce_fresh_cardnews(topic_id=topic_id)

    logger.info("================================================================================")
    logger.info(f"🎉 [성공] {topic_id}번 주제 5장 풀세트 카드뉴스가 완성되었습니다!")
    logger.info(f"📊 총 슬라이드 수: {len(slides)}장")
    for i, p in enumerate(slides, 1):
        logger.info(f"   [{i}/5] {p}")
    logger.info("================================================================================")
    if slides:
        pkg_dir = Path(slides[0]).parent
        print("OUTPUT_DIR=" + str(pkg_dir))


if __name__ == "__main__":
    main()
