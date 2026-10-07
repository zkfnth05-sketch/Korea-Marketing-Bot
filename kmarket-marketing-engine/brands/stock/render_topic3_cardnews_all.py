# -*- coding: utf-8 -*-
"""
RenderTopic3CardnewsAll - 🚀 [StockMaster AI 주식 3번 주제 5장 카드뉴스 전체 일괄 렌더링]
========================================================================================
• 역할:
  - 주식 3번 주제: [뇌동매매 방지! 시장 스트레스 가이드 & 실시간 1위 주도주 수급 팩트 진단]
  - 1번 표지: Wan 2.1 20대 여성 야외 현장 기자 실사 표지 (slide_1.png)
  - 2번: 실시간 웹앱 '💡 시장 스트레스 지표별 투자 행동 지침' 스마트폰 뷰 (slide_2.png)
  - 3번: 실시간 웹앱 10분 계량 전광판 '1위 주도주' 아코디언 오픈 스마트폰 뷰 (slide_3.png)
  - 4번: 실시간 웹앱 1위 주도주 모달 '[수급 현황]' 탭 스마트폰 뷰 (slide_4.png)
  - 5번: 핫이슈 찬반 토론 & 네이버 검색창('스톡마스터 AI') 공식 CTA 카드 (slide_5.png)
  - 최종 저장: Desktop/한국 카드뉴스_산출물/주식/[주제03] 뇌동매매방지_리스크가드_20대여성기자/
"""

import os
import sys
import logging
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RenderTopic3CardnewsAll")

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from brands.stock.capture_stock_topic3_live_iframe_exact import capture_all_topic3_live_screens
from brands.stock.stock_cardnews_s1_topic3_builder import StockCardnewsS1Topic3Builder
from brands.stock.stock_cardnews_s2_topic3_builder import StockCardnewsS2Topic3Builder
from brands.stock.stock_cardnews_s3_topic3_builder import StockCardnewsS3Topic3Builder
from brands.stock.stock_cardnews_s4_topic3_builder import StockCardnewsS4Topic3Builder
from brands.stock.stock_cardnews_s5_topic3_builder import StockCardnewsS5Topic3Builder


def render_all_topic3_cardnews(force_recapture: bool = True):
    output_dir = Path(os.environ.get("USERPROFILE", "C:/Users/zkfnt")) / "Desktop" / "한국 카드뉴스_산출물" / "주식" / "[주제03] 뇌동매매방지_리스크가드_20대여성기자"
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"📂 [주식 3번 주제 카드뉴스 산출물 폴더]: {output_dir}")

    # 1. 📱 [실제 라이브 웹앱 3개 핵심 화면 실시간 캡처]
    if force_recapture:
        logger.info("📱 [Step 1] 실제 라이브 웹앱에서 3개 핵심 화면 실시간 추출 중...")
        capture_all_topic3_live_screens()

    # 2. Slide 1: 20대 여성 야외 현장 기자 표지 (Wan 2.1 마스터 실사)
    slide1_path = output_dir / "slide_1.png"
    s1_builder = StockCardnewsS1Topic3Builder()
    
    # 확정 실사 사진 사용
    artifact_photo = Path(r"C:\Users\zkfnt\.gemini\antigravity-ide\brain\791cf2b6-0a97-4dda-8c5d-f5fab6d0d50c\stock_topic3_reporter_raw2.png")
    if artifact_photo.exists():
        s1_builder.render_cover_slide(artifact_photo, str(slide1_path))
    elif not slide1_path.exists():
        logger.info("🎨 [Slide 1] 20대 여성 기자 Wan 2.1 신규 실사 표지 생성 중...")
        fresh_photo = s1_builder.generate_fresh_wan_photo()
        s1_builder.render_cover_slide(fresh_photo, str(slide1_path))
    logger.info(f"✅ [Slide 1] 야외 현장 기자 표지 렌더링 완료: {slide1_path.name}")

    # 3. Slide 2: 시장 스트레스 지표별 투자 행동 지침 실측 폰뷰
    logger.info("💡 [Slide 2] 시장 스트레스 지표별 투자 행동 지침 폰뷰 렌더링 중...")
    s2_builder = StockCardnewsS2Topic3Builder()
    s2_path = output_dir / "slide_2.png"
    s2_builder.render_slide(str(s2_path))
    logger.info(f"✅ [Slide 2] 시장 스트레스 행동 지침 렌더링 완료: {s2_path.name}")

    # 4. Slide 3: 10분 계량 전광판 1위 주도주 아코디언 폰뷰
    logger.info("⚡ [Slide 3] 10분 계량 전광판 1위 주도주 아코디언 폰뷰 렌더링 중...")
    s3_builder = StockCardnewsS3Topic3Builder()
    s3_path = output_dir / "slide_3.png"
    s3_builder.render_slide(str(s3_path))
    logger.info(f"✅ [Slide 3] 1위 주도주 전광판 렌더링 완료: {s3_path.name}")

    # 5. Slide 4: 1위 주도주 모달의 [수급 현황] 탭 폰뷰
    logger.info("🔥 [Slide 4] 1위 주도주 모달 [수급 현황] 탭 폰뷰 렌더링 중...")
    s4_builder = StockCardnewsS4Topic3Builder()
    s4_path = output_dir / "slide_4.png"
    s4_builder.render_slide(str(s4_path))
    logger.info(f"✅ [Slide 4] 1위 주도주 수급 현황 렌더링 완료: {s4_path.name}")

    # 6. Slide 5: 공식 핫이슈 찬반 토론 & 네이버 검색창 CTA 카드
    logger.info("🏆 [Slide 5] 공식 5번 CTA 카드뉴스 렌더링 중...")
    s5_builder = StockCardnewsS5Topic3Builder()
    s5_path = output_dir / "slide_5.png"
    s5_builder.render_slide(str(s5_path))
    logger.info(f"✅ [Slide 5] 공식 CTA 카드 렌더링 완료: {s5_path.name}")

    logger.info(f"🎉 [주식 3번 주제 완제품 5장 카드뉴스 일괄 렌더링 100% 완료] -> {output_dir}")
    return [
        str(slide1_path),
        str(s2_path),
        str(s3_path),
        str(s4_path),
        str(s5_path)
    ]


if __name__ == "__main__":
    results = render_all_topic3_cardnews(force_recapture=False)
    print("\n" + "=" * 70)
    print("🎉 [StockMaster AI 주식 3번 주제 5장 카드뉴스 전체 완제품 생성 완료]")
    for idx, path in enumerate(results, start=1):
        print(f"  {idx}번 카드: {path}")
    print("=" * 70)
