# -*- coding: utf-8 -*-
"""
Aura YouTube Hybrid Pilot (🚀 Aura 유튜브 웜업 + API 무인 배포 통합 파일럿)
=============================================================================
- 역할:
  1. 1단계: [AuraYouTubeStealthIncubator] ➔ 백그라운드 브라우저 쇼츠 웜업 (Trust Score 100% 충전)
  2. 2단계: 최신 Aura 완성 숏폼 영상(바탕화면 '한국 숏폼_산출물/Aura' 내 MP4) 자동 탐색
  3. 3단계: [AuraYouTubeAPIPublisher] ➔ Google Data API v3 0.1초 고속 업로드 + 4단 해시태그 + 고정댓글
  4. 24시간 365일 무인 데몬과 100% 레고 블록 호환
- 원칙: Rule 1 (독립 레고 블록), Rule 5 (땜질 코딩 금지), Rule 7 (공식 검색어 '아우라AI데이팅')
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
from brands.aura.aura_youtube_stealth_incubator import AuraYouTubeStealthIncubator
from brands.aura.aura_youtube_api_publisher import AuraYouTubeAPIPublisher

logger = logging.getLogger("AuraYouTubeHybridPilot")


class AuraYouTubeHybridPilot:
    """🚀 Aura 유튜브 인간 웜업 & API 배포 통합 관제 엔진"""

    def __init__(self, headless: bool = True):
        self.incubator = AuraYouTubeStealthIncubator(headless=headless)
        self.publisher = AuraYouTubeAPIPublisher()
        self.shorts_output_dir = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Aura")

    def find_latest_short_video(self, topic_id: Optional[int] = None) -> Optional[Path]:
        """바탕화면 산출물 폴더에서 가장 최신 렌더링된 Aura 숏폼 MP4 자동 탐색"""
        if not self.shorts_output_dir.exists():
            # 프로젝트 outputs 폴더 폴백
            fallback_dir = BASE_DIR / "outputs" / "aura"
            if fallback_dir.exists():
                candidates = list(fallback_dir.glob("**/*.mp4"))
                if candidates:
                    return max(candidates, key=os.path.getmtime)
            return None

        # 1. 10초 순수 인물 원테이크 우선 탐색 (완독률 극대화)
        one_takes = list(self.shorts_output_dir.glob("**/*10초*순수인물*.mp4"))
        if one_takes:
            return max(one_takes, key=os.path.getmtime)

        # 2. 일반 22초 숏폼 탐색
        all_shorts = list(self.shorts_output_dir.glob("**/*.mp4"))
        if all_shorts:
            return max(all_shorts, key=os.path.getmtime)

        return None

    def execute_hybrid_deployment(
        self,
        video_path: Optional[str] = None,
        topic_id: int = 1,
        skip_warmup: bool = True,
        privacy_status: str = "public"
    ) -> Dict[str, Any]:
        """
        [순수 API 배포] 인간 행동은 AuraHumanBehaviorBot이 전담하므로 업로드 직전 웜업 스킵
        """
        start_time = time.time()
        logger.info("=" * 70)
        logger.info("🚀 [Aura 유튜브 하이브리드 무인 파일럿 가동]")
        logger.info(f"  • 주제 번호: #{topic_id}")
        logger.info(f"  • 웜업 스킵 여부: {skip_warmup}")
        logger.info(f"  • 공개 설정: {privacy_status}")
        logger.info("=" * 70)

        # 1. 명시적으로 전달받은 실시간 신규 비디오 파일 검증 (과거 파일 무단 탐색 100% 차단)
        if not video_path or not Path(video_path).exists():
            raise FileNotFoundError(f"업로드할 실시간 신선 Aura 숏폼 비디오 경로가 지정되지 않았거나 존재하지 않습니다: {video_path}")
        target_video = Path(video_path)

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
            "brand": "Aura AI 데이팅",
            "topic_id": topic_id,
            "video_file": target_video.name if target_video else "none",
            "warmup": warmup_result,
            "publish": publish_result,
            "total_elapsed_sec": total_elapsed,
            "summary": "유튜브 웜업 및 API 쇼츠 배포 파이프라인 완결"
        }

        logger.info("=" * 70)
        logger.info(f"🎉 [Aura 유튜브 하이브리드 파일럿 완료] 총 소요: {total_elapsed}초")
        logger.info("=" * 70)
        return final_report


if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    parser = argparse.ArgumentParser(description="Aura YouTube Hybrid Pilot")
    parser.add_argument("--skip-warmup", action="store_true", help="브라우저 웜업 스킵")
    parser.add_argument("--topic", type=int, default=1, help="주제 번호 (1~8)")
    parser.add_argument("--private", action="store_true", help="비공개 업로드")
    args = parser.parse_args()

    pilot = AuraYouTubeHybridPilot(headless=True)
    privacy = "private" if args.private else "public"
    res = pilot.execute_hybrid_deployment(topic_id=args.topic, skip_warmup=args.skip_warmup, privacy_status=privacy)
    print(json.dumps(res, ensure_ascii=False, indent=2))
