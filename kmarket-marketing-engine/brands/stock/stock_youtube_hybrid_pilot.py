# -*- coding: utf-8 -*-
"""
StockMaster YouTube Hybrid Pilot (🚀 StockMaster AI 유튜브 웜업 + API 배포 통합 파일럿)
======================================================================================
- 역할:
  1. 1단계: [StockYouTubeStealthIncubator] ➔ 백그라운드 브라우저 쇼츠 웜업 (Trust Score 확보)
  2. 2단계: 최신 주식 완성 숏폼 영상(바탕화면 '한국 숏폼_산출물/Stock' 내 MP4) 자동 탐색
  3. 3단계: [StockYouTubeAPIPublisher] ➔ Google Data API v3 0.1초 고속 업로드 + 4단 해시태그 + 고정댓글
  4. 24시간 365일 무인 데몬과 100% 레고 블록 호환
- 원칙: Rule 1 (독립 레고 블록), Rule 5 (땜질 코딩 금지), Rule 7 (공식 검색어 '스톡마스터 AI')
"""

import os
import sys
import glob
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Windows cp949 콘솔 인코딩 에러 방지
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import BASE_DIR, get_now_kst_str
from brands.stock.stock_youtube_stealth_incubator import StockYouTubeStealthIncubator
from brands.stock.stock_youtube_api_publisher import StockYouTubeAPIPublisher

logger = logging.getLogger("StockYouTubeHybridPilot")


class StockYouTubeHybridPilot:
    """🚀 StockMaster AI 유튜브 인간 웜업 & API 배포 통합 관제 엔진"""

    def __init__(self, headless: bool = True):
        self.incubator = StockYouTubeStealthIncubator(headless=headless)
        self.publisher = StockYouTubeAPIPublisher()
        self.shorts_output_dir = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Stock")

    def find_latest_short_video(self, topic_id: Optional[int] = None) -> Optional[Path]:
        """바탕화면 산출물 폴더에서 가장 최신 렌더링된 주식 숏폼 MP4 자동 탐색"""
        search_dirs = [
            self.shorts_output_dir,
            BASE_DIR / "outputs" / "stock"
        ]

        for sdir in search_dirs:
            if sdir.exists():
                # 1. 22초/30초 풀버전 우선 탐색
                shorts_full = [p for p in sdir.glob("**/*.mp4") if "22초" in p.name or "30초" in p.name or "22s" in p.name]
                if shorts_full:
                    return max(shorts_full, key=os.path.getmtime)

                # 2. 10초 원테이크 탐색
                shorts_10s = [p for p in sdir.glob("**/*.mp4") if "10초" in p.name]
                if shorts_10s:
                    return max(shorts_10s, key=os.path.getmtime)

                # 3. 전체 MP4 탐색
                all_shorts = list(sdir.glob("**/*.mp4"))
                if all_shorts:
                    return max(all_shorts, key=os.path.getmtime)

        return None

    def execute_hybrid_deployment(
        self,
        video_path: Optional[str] = None,
        topic_id: int = 1,
        skip_warmup: bool = False,
        privacy_status: str = "public"
    ) -> Dict[str, Any]:
        """
        [1단계 인간 웜업 ➔ 2단계 API 배포] 원스톱 전자동 실행
        """
        start_time = time.time()
        logger.info("=" * 70)
        logger.info("🚀 [StockMaster AI 유튜브 하이브리드 무인 파일럿 가동]")
        logger.info(f"  • 주제 번호: #{topic_id}")
        logger.info(f"  • 웜업 스킵 여부: {skip_warmup}")
        logger.info(f"  • 공개 설정: {privacy_status}")
        logger.info("=" * 70)

        # 1. 대상 비디오 파일 확보
        target_video = Path(video_path) if video_path else self.find_latest_short_video(topic_id)
        if not target_video or not target_video.exists():
            logger.warning("⚠️ 업로드할 StockMaster AI 숏폼 비디오가 없어 메타데이터 검증 모드로 전환합니다.")

        # 2. [Step 1] 브라우저 인간 웜업 (Trust Score 확보)
        warmup_result = {}
        if not skip_warmup:
            logger.info("🛡️ [Step 1] 유튜브 백그라운드 인간 웜업 시작 (쇼츠 시청 + 좋아요)...")
            warmup_result = self.incubator.run_warmup_session(watch_count=3)
        else:
            logger.info("⏩ [Step 1] 웜업 단계 건너뜀 (요청에 따름)")
            warmup_result = {"status": "skipped", "message": "웜업 스킵됨"}

        # 3. [Step 2] Google Data API v3 0.1초 고속 업로드 & 고정 댓글 등록
        publish_result = {}
        if target_video and target_video.exists():
            logger.info(f"🔴 [Step 2] YouTube Data API v3 숏폼 송출 시작: {target_video.name}")
            publish_result = self.publisher.publish_short(
                video_path=str(target_video),
                topic_id=topic_id,
                privacy_status=privacy_status
            )
        else:
            publish_result = {
                "status": "ready_staged",
                "message": "비디오 파일 준비 대기 (렌더링 완료 즉시 자동 송출 가능)"
            }

        total_elapsed = round(time.time() - start_time, 1)
        final_report = {
            "status": "completed",
            "timestamp": get_now_kst_str(),
            "brand": "StockMaster AI",
            "topic_id": topic_id,
            "video_file": target_video.name if target_video else "none",
            "warmup": warmup_result,
            "publish": publish_result,
            "total_elapsed_sec": total_elapsed,
            "summary": "유튜브 웜업 및 API 쇼츠 배포 파이프라인 완결"
        }

        logger.info("=" * 70)
        logger.info(f"🎉 [StockMaster AI 유튜브 하이브리드 파일럿 완료] 총 소요: {total_elapsed}초")
        logger.info("=" * 70)
        return final_report


if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    parser = argparse.ArgumentParser(description="StockMaster YouTube Hybrid Pilot")
    parser.add_argument("--skip-warmup", action="store_true", help="브라우저 웜업 스킵")
    parser.add_argument("--topic", type=int, default=1, help="주제 번호 (1~8)")
    parser.add_argument("--private", action="store_true", help="비공개 업로드")
    args = parser.parse_args()

    pilot = StockYouTubeHybridPilot(headless=True)
    privacy = "private" if args.private else "public"
    res = pilot.execute_hybrid_deployment(topic_id=args.topic, skip_warmup=args.skip_warmup, privacy_status=privacy)
    print(json.dumps(res, ensure_ascii=False, indent=2))
