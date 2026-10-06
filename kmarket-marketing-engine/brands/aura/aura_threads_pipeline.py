# -*- coding: utf-8 -*-
"""
Aura Threads Pipeline (🧵 💖 Aura AI 데이팅 전용 스레드 독립 파이프라인)
======================================================================
- 브랜드: 💖 Aura (AI 데이팅)
- 전용 계정: @aura_ai_dating
- 공식 검색어: '아우라AI데이팅' (붙여쓰기 필수, 불변)
- 랜딩 URL: https://aura-ai-dating.vercel.app/
- 역할:
  1. Aura 전용 카드뉴스(4~5장 이미지) 또는 2030 연애 텍스트 타래 자동 패키징
  2. 스레드(Threads) 독립 레고 블록 발행기(AuraThreadsPublisher)를 통한 100% 무인 송출
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

logger = logging.getLogger("AuraThreadsPipeline")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent


class AuraThreadsPipeline:
    """💖 Aura 전용 스레드 완전 독립 레고 블록 파이프라인"""

    BRAND = "aura"
    BRAND_NAME = "Aura AI 데이팅"
    OFFICIAL_SEARCH_KEYWORD = "아우라AI데이팅"
    LANDING_URL = "https://aura-ai-dating.vercel.app/"

    def __init__(self, headless: bool = True):
        self.headless = headless
        from brands.aura.aura_threads_publisher import AuraThreadsPublisher
        self.publisher = AuraThreadsPublisher(headless=self.headless)

    async def run_pipeline(self, cardnews_folder: Optional[str] = None, custom_caption: Optional[str] = None) -> Dict[str, Any]:
        """Aura 전용 스레드 자동 송출 실행"""
        logger.info(f"🚀 [{self.BRAND_NAME}] 스레드 독립 파이프라인 가동")

        media_paths = []
        caption = custom_caption or ""

        # 1. 특정 카드뉴스 폴더가 지정된 경우
        if cardnews_folder:
            target_dir = Path(cardnews_folder)
            if target_dir.exists():
                slide_images = []
                for i in range(1, 10):
                    f = target_dir / f"slide_{i}.png"
                    if f.exists():
                        slide_images.append(str(f.resolve()))

                # 🎬 15.5초 카드뉴스 숏폼 비디오 변환 및 탐색
                video_candidates = list(target_dir.glob("*_cardnews_reels.mp4")) + list(target_dir.glob("cardnews_reels.mp4"))
                if video_candidates and video_candidates[0].exists():
                    media_paths = [str(video_candidates[0].resolve())]
                    logger.info(f"🎬 [Aura Threads] 기존 카드뉴스 숏폼 영상 감지: {video_candidates[0].name}")
                elif len(slide_images) >= 4:
                    try:
                        from core.cardnews_to_reels_converter import CardnewsToReelsConverter
                        converter = CardnewsToReelsConverter()
                        out_reels = str(target_dir / "aura_cardnews_reels.mp4")
                        conv_res = converter.convert(slide_paths=slide_images, output_path=out_reels, brand="aura")
                        if conv_res.get("status") == "success" and os.path.exists(out_reels):
                            media_paths = [out_reels]
                            logger.info(f"🎬 [Aura Threads] 카드뉴스 5장 ➔ 15.5초 숏폼 비디오 변환 성공: {out_reels}")
                        else:
                            media_paths = slide_images
                    except Exception as ce:
                        logger.warning(f"⚠️ [Aura Threads] 비디오 변환 예외, 이미지로 대체: {ce}")
                        media_paths = slide_images
                else:
                    media_paths = slide_images
                
                # 가이드 텍스트 읽기
                guide_file = target_dir / "SNS_포스팅_가이드_KO.txt"
                if guide_file.exists() and not caption:
                    try:
                        with open(guide_file, "r", encoding="utf-8") as gf:
                            raw_lines = [line.strip() for line in gf.readlines() if line.strip()]
                            clean_lines = [l for l in raw_lines if not l.startswith("=") and not l.startswith("•") and "주제:" not in l and "의상:" not in l]
                            caption = "\n\n".join(clean_lines[:5])
                    except Exception as e:
                        logger.warning(f"가이드 파일 로드 경고: {e}")

        # 2. 기본 캡션 세팅
        if not caption:
            caption = (
                "📍 [500m 안심 레이더 & 2030 실시간 매칭]\n\n"
                "거리와 취향까지 딱 맞는 내 반경 500m 인연 찾기!\n"
                "가장 솔직하고 안심되는 AI 매칭을 지금 확인해보세요 ✨\n\n"
                "#Aura #데이팅 #소개팅 #안심매칭 #2030연애"
            )

        # 3. 첫 번째 댓글 체인 (공식 검색어 & 랜딩 URL)
        first_reply = (
            f"💖 2030 매력 진단 & AI 매칭 1분 무료 리포트\n"
            f"네이버에 '{self.OFFICIAL_SEARCH_KEYWORD}' 한번 검색해보세요!\n"
            f"👉 {self.LANDING_URL}"
        )

        # 4. 스레드 독립 퍼블리셔 송출 (숏폼 비디오 형태)
        result = await self.publisher.publish_thread(
            caption=caption,
            image_paths=media_paths,
            first_reply_text=first_reply
        )
        return result


async def main():
    pipeline = AuraThreadsPipeline(headless=False)
    res = await pipeline.run_pipeline()
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
