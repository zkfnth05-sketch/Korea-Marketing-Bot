# -*- coding: utf-8 -*-
"""
Insurance Threads Pipeline (🧵 🛡️ 보험 리밸런스 전용 스레드 독립 파이프라인)
========================================================================
- 브랜드: 🛡️ 보험 리밸런스 (InsureBalance)
- 전용 계정: @goldmomofficial
- 공식 검색어: '보험 리밸런스' (띄어쓰기 필수, 불변)
- 랜딩 URL: https://insure-rebalance.vercel.app/
- 역할:
  1. 보험 리밸런스 전용 카드뉴스(4~5장 이미지) 또는 보험료 절약 텍스트 타래 패키징
  2. 스레드(Threads) 독립 레고 블록 발행기(InsuranceThreadsPublisher)를 통한 100% 무인 송출
  3. 첫 번째 타래 댓글로 공식 검색어 및 랜딩 링크 자동 체인 연동
  4. 송출 히스토리 및 증빙 스크린샷 독립 보관
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("InsuranceThreadsPipeline")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent


class InsuranceThreadsPipeline:
    """🛡️ 보험 리밸런스 전용 스레드 완전 독립 레고 블록 파이프라인"""

    BRAND = "insurance"
    BRAND_NAME = "보험 리밸런스"
    OFFICIAL_SEARCH_KEYWORD = "보험 리밸런스"
    LANDING_URL = "https://insure-rebalance.vercel.app/"

    def __init__(self, headless: bool = True):
        self.headless = headless
        from brands.insurance.insurance_threads_publisher import InsuranceThreadsPublisher
        self.publisher = InsuranceThreadsPublisher(headless=self.headless)

    async def run_pipeline(self, cardnews_folder: Optional[str] = None, custom_caption: Optional[str] = None) -> Dict[str, Any]:
        """보험 리밸런스 전용 스레드 자동 송출 실행"""
        logger.info(f"🚀 [{self.BRAND_NAME}] 스레드 독립 파이프라인 가동")

        image_paths = []
        caption = custom_caption or ""

        # 1. 특정 카드뉴스 폴더가 지정된 경우
        if cardnews_folder:
            target_dir = Path(cardnews_folder)
            if target_dir.exists():
                for i in range(1, 10):
                    f = target_dir / f"slide_{i}.png"
                    if f.exists():
                        image_paths.append(str(f.resolve()))
                
                guide_file = target_dir / "SNS_포스팅_가이드_KO.txt"
                if guide_file.exists() and not caption:
                    try:
                        with open(guide_file, "r", encoding="utf-8") as gf:
                            lines = [line.strip() for line in gf.readlines() if line.strip()]
                            caption = "\n\n".join(lines[:6])
                    except Exception as e:
                        logger.warning(f"가이드 파일 로드 경고: {e}")

        # 2. 기본 캡션 세팅
        if not caption:
            caption = (
                "🛡️ [매달 줄줄 새는 보험료 3분 진단]\n\n"
                "나도 모르게 중복 결제되고 있던 특약이 있다?\n"
                "보장은 든든하게 늘리고 보험료는 30% 다이어트하세요!\n\n"
                "#보험리밸런스 #보험절약 #실손보험 #보험비교"
            )

        # 3. 첫 번째 댓글 체인 (공식 검색어 & 랜딩 URL)
        first_reply = (
            f"🛡️ 매달 줄줄 새는 숨은 보험료 3분 진단\n"
            f"네이버에 '{self.OFFICIAL_SEARCH_KEYWORD}' 검색해보세요!\n"
            f"👉 {self.LANDING_URL}"
        )

        # 4. 스레드 독립 퍼블리셔 송출
        result = await self.publisher.publish_thread(
            caption=caption,
            image_paths=image_paths,
            first_reply_text=first_reply
        )
        return result


async def main():
    pipeline = InsuranceThreadsPipeline(headless=False)
    res = await pipeline.run_pipeline()
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
