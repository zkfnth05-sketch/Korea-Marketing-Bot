# -*- coding: utf-8 -*-
"""
유튜브 스튜디오 쇼츠 무인 직접 업로드 및 진짜 실물 URL + 고정 첫 댓글 검증
=============================================================================
"""
import os
import sys
import json
import asyncio
import logging
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RealYouTubeTest")

CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))

from brands.aura.aura_youtube_bot_publisher import AuraYouTubeBotPublisher

async def test_youtube():
    pub = AuraYouTubeBotPublisher(headless=True)
    video_path = r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Aura\Aura_08_safe_radar_20261011_180012\Aura_22초숏폼_주제08_safe_radar_20261011_180012.mp4"
    if not os.path.exists(video_path):
        candidates = list(Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Aura").glob("**/*.mp4"))
        if candidates:
            video_path = str(candidates[0])

    logger.info(f"🚀 [유튜브 쇼츠 실기 업로드 테스트] 대상 영상: {os.path.basename(video_path)}")

    res = await pub.publish_short_async(
        video_path=video_path,
        topic_id=8,
        title="소개팅에서 어색할 때 3초 만에 탈출하는 비법 ㄷㄷ #아우라AI데이팅 #Shorts",
        description=(
            "거리와 취향까지 딱 맞는 내 반경 500m 안심 소개팅 ✨\n"
            "네이버에 [아우라AI데이팅] 한번 검색해보세요!\n"
            "공식 라운지: https://aura-ai-dating.vercel.app/\n\n"
            "#아우라AI데이팅 #소개팅꿀팁 #2030연애 #Shorts"
        ),
        privacy_status="public",
        timeout_sec=120
    )

    logger.info("=" * 60)
    logger.info(f"🎉 [유튜브 쇼츠 업로드 결과] {json.dumps(res, ensure_ascii=False, indent=2)}")
    logger.info("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_youtube())
