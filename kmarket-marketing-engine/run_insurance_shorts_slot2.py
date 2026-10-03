# -*- coding: utf-8 -*-
"""
보험 숏폼 2번 주제(운전자보험 1만원의 법칙) 자율 제작 및 4대 채널 API 무인 송출 실행기
"""
import os
import sys
import json
import logging

os.environ["BLOCK_EXTERNAL_API_DISPATCH"] = "0"
os.environ["ENABLE_EXTERNAL_API_DISPATCH"] = "1"

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger("InsurancePilotRunner")

if __name__ == "__main__":
    from brands.insurance.insurance_pipeline import InsurancePipeline
    logger.info("🚀 [보험 숏폼 2번 주제 자동 제작 & 4대 채널 API 무인 송출 파이프라인 가동]")
    bot = InsurancePipeline(dry_run=False)
    res = bot.run_shorts(topic_id=2, force=True)
    logger.info("=" * 80)
    logger.info(f"🏁 [최종 실행 결과] {json.dumps(res, ensure_ascii=False, indent=2) if isinstance(res, dict) else res}")
    logger.info("=" * 80)
