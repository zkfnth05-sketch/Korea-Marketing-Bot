# -*- coding: utf-8 -*-
"""
Aura Cardnews Omni Publish & Live Verification Test
===================================================
1. 바탕화면 최신 아우라 5장 완제품 카드뉴스 로드
2. [스레드] 5장 카드뉴스 포스팅 + 첫 타래 댓글(공식 검색어 & 링크) 작성
3. [Meta] 카드뉴스 릴스 변환 및 MBS(페이스북 + 인스타그램) 무인 송출
4. [페이스북 댓글러] 페이스북 최신 글 첫 댓글(공식 검색어 & 링크) 작성
5. [인스타그램 댓글러] 인스타그램 최신 릴스 첫 댓글(공식 검색어 & 링크) 작성
6. [실측 감사 검증기] 5대 플랫폼 실제 라이브 페이지 접속 확인 및 스크린샷 캡처
7. [대시보드 리포트] outputs/live_verification_dashboard.html 자동 생성
"""

import os
import sys
import json
import time
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
logger = logging.getLogger("AuraOmniTest")

CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))

from brands.aura.aura_omni_cardnews_pilot import AuraOmniCardnewsPilot
from brands.aura.aura_post_comment_verifier import AuraPostCommentVerifier


def main():
    logger.info("=" * 70)
    logger.info("🚀 [Aura 카드뉴스 3대 SNS 송출 + 댓글 + 실측 검증 통합 테스트 가동]")
    logger.info("• 대상 채널: 인스타그램, 페이스북, 스레드")
    logger.info("• 필수 수칙: 첫 댓글(아우라AI데이팅 & 랜딩 URL) 100% 등록 및 실측 검증")
    logger.info("=" * 70)

    # 1. 바탕화면에서 가장 최신의 5장 완제품 카드뉴스 폴더 찾기
    desktop = Path(os.environ.get("USERPROFILE", "C:/Users/zkfnt")) / "Desktop" / "한국 카드뉴스_산출물" / "아우라"
    target_folder = None
    if desktop.exists():
        candidates = []
        for d in desktop.iterdir():
            if d.is_dir():
                slides = list(d.glob("slide_*.png"))
                if len(slides) >= 5:
                    candidates.append((d.stat().st_mtime, d))
        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            target_folder = candidates[0][1]

    if not target_folder:
        logger.error("❌ 바탕화면에 5장 완제품 아우라 카드뉴스 폴더가 없습니다.")
        return

    logger.info(f"📂 [송출 대상 카드뉴스 확보] {target_folder.name}")
    slides = [str(target_folder / f"slide_{i}.png") for i in range(1, 6)]

    pilot = AuraOmniCardnewsPilot()
    topic_id = 6  # AI 첫대화 비서

    # 2. 메타데이터 패키징
    pkg = pilot.build_meta_packages(topic_id)
    logger.info(f"📝 [메타데이터 패키징 완료] 제목: {pkg['title']}")

    # 3. 카드뉴스 ➔ 15.5초 릴스 변환
    from core.cardnews_to_reels_converter import CardnewsToReelsConverter
    converter = CardnewsToReelsConverter()
    out_reels = str(target_folder / f"aura_topic{topic_id}_cardnews_reels.mp4")
    if not os.path.exists(out_reels):
        logger.info("🎬 [CardnewsToReels] 카드뉴스 5장 ➔ 15.5초 세로 릴스 비디오 변환 중...")
        converter.convert(slide_paths=slides, output_path=out_reels, brand="aura")
    else:
        logger.info(f"🎬 [CardnewsToReels] 기존 릴스 비디오 활용: {os.path.basename(out_reels)}")

    publish_results = {"channels": {}}

    # 4. [Channel 1 & 2] Meta Business Suite 릴스 (인스타그램 + 페이스북)
    if os.path.exists(out_reels) and pilot.mbs_pub.is_available():
        logger.info("🌐 [1/3 Meta Business Suite] 인스타그램 + 페이스북 릴스 무인 송출 시작...")
        try:
            mbs_res = pilot.mbs_pub.publish_reel(
                video_path=out_reels,
                caption=pkg.get("ig_caption", pkg["title"])
            )
            publish_results["channels"]["meta_business_suite_reels"] = mbs_res
            logger.info(f"🎉 [MBS 발행 완료]: {mbs_res.get('status')}")
        except Exception as e:
            logger.error(f"❌ MBS 송출 예외: {e}")
            publish_results["channels"]["meta_business_suite_reels"] = {"status": "error", "error": str(e)}

        # 4-1. 페이스북 최신 글 첫 댓글 달기
        logger.info("💬 [2/3 페이스북 댓글러] 최신 게시물에 첫 댓글(공식 검색어 & 링크) 작성 중...")
        try:
            from brands.aura.aura_facebook_commenter import AuraFacebookCommenter
            fb_res = asyncio.run(AuraFacebookCommenter().post_comment_on_latest_post_async())
            publish_results["channels"]["facebook_comment"] = fb_res
            logger.info(f"🎉 [페이스북 첫 댓글 완료]: {fb_res.get('status')}")
        except Exception as e:
            logger.error(f"❌ 페이스북 댓글 예외: {e}")
            publish_results["channels"]["facebook_comment"] = {"status": "error", "error": str(e)}

        # 4-2. 인스타그램 최신 릴스 첫 댓글 달기
        logger.info("💬 [3/3 인스타그램 댓글러] 최신 릴스에 첫 댓글(공식 검색어 & 링크) 작성 중...")
        try:
            from brands.aura.aura_instagram_commenter import AuraInstagramCommenter
            ig_res = asyncio.run(AuraInstagramCommenter().post_comment_on_latest_reel_async())
            publish_results["channels"]["instagram_comment"] = ig_res
            logger.info(f"🎉 [인스타그램 첫 댓글 완료]: {ig_res.get('status')}")
        except Exception as e:
            logger.error(f"❌ 인스타그램 댓글 예외: {e}")
            publish_results["channels"]["instagram_comment"] = {"status": "error", "error": str(e)}

    # 5. [Channel 3] 스레드(Threads) 5장 카드뉴스 & 첫 타래 댓글 송출
    logger.info("🧵 [스레드 독립 파이프라인] 5장 카드뉴스 및 첫 타래 댓글 무인 송출 시작...")
    try:
        from brands.aura.aura_threads_pipeline import AuraThreadsPipeline
        th_pipe = AuraThreadsPipeline(headless=True)
        th_res = asyncio.run(th_pipe.run_pipeline(
            cardnews_folder=str(target_folder),
            custom_caption=pkg.get("ig_caption", pkg["title"])
        ))
        publish_results["channels"]["threads"] = th_res
        logger.info(f"🎉 [스레드 송출 완료]: {th_res.get('status')}")
    except Exception as e:
        logger.error(f"❌ 스레드 송출 예외: {e}")
        publish_results["channels"]["threads"] = {"status": "error", "error": str(e)}

    # 6. 🕵️ [실측 감사 검증기 가동] 진짜로 올라갔는지 웹 브라우저로 100% 실측 점검
    logger.info("\n" + "=" * 70)
    logger.info("🕵️ [실측 감사 검증기 가동] 실제로 게시물이 올라가고 댓글이 달렸는지 전수 확인 시작...")
    logger.info("=" * 70)
    verifier = AuraPostCommentVerifier(headless=True)
    report = asyncio.run(verifier.run_full_verification())

    logger.info("\n" + "=" * 70)
    logger.info("📊 [Aura 마케팅봇 실측 감사 리포트 완료]")
    logger.info(f"• 페이스북: {report['platforms']['facebook'].get('post_status')} | 댓글: {report['platforms']['facebook'].get('comment_status')}")
    logger.info(f"• 인스타그램: {report['platforms']['instagram'].get('post_status')} | 댓글: {report['platforms']['instagram'].get('comment_status')}")
    logger.info(f"• 스레드: {report['platforms']['threads'].get('post_status')} | 댓글: {report['platforms']['threads'].get('comment_status')}")
    logger.info(f"• 대시보드 리포트: outputs/live_verification_dashboard.html")
    logger.info("=" * 70 + "\n")


if __name__ == "__main__":
    main()
