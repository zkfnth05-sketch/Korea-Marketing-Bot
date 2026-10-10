import os
import sys
import logging
from pathlib import Path

BASE_DIR = Path(r"C:\Users\zkfnt\Desktop\한국 마케팅봇\kmarket-marketing-engine")
sys.path.insert(0, str(BASE_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TestPublishStockShorts")

from brands.stock.stock_omni_shorts_pilot import StockOmniShortsPilot

video_path = r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Stock\[주제03] 뇌동매매방지_기계적손절매_30초_20261010_184508\[주제03_완성본]_30초_세로풀HD.mp4"
topic_id = 3

logger.info(f"🚀 [주식 숏폼 4대 채널 송출 테스트 개시]")
logger.info(f"  • 대상 비디오: {video_path}")
logger.info(f"  • 주제 번호: #{topic_id}")

pilot = StockOmniShortsPilot()
results = pilot.publish_video(video_path=video_path, topic_id=topic_id)

logger.info("=" * 70)
logger.info(f"🎉 [송출 결과 종합]:\n{results}")
logger.info("=" * 70)
