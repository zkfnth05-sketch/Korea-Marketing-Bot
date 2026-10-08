# -*- coding: utf-8 -*-
"""
RenderTopic6CardnewsAll - 🚀 [StockMaster AI 주식 6번 주제 5장 카드뉴스 전체 일괄 렌더링]
========================================================================================
• 역할:
  - 주식 6번 주제: [AI 퀀트 비서 총괄 소개 (20대 훈남 앵커)]
  - 1번 표지: Wan 2.1 26세 8등신 훈남 앵커 블룸버그/삼프로TV 스튜디오 실사 표지 (slide_1.png)
  - 2번: 실시간 1위 종목(LG에너지솔루션) 10분 계량 전광판 아코디언 오픈 폰뷰 (slide_2.png)
  - 3번: 실시간 1위 종목(LG에너지솔루션) 실시간 퀀트 모달 [기술 지표] 폰뷰 (slide_3.png)
  - 4번: 실시간 1위 종목(LG에너지솔루션) 실시간 퀀트 모달 [수급 현황] 폰뷰 (slide_4.png)
  - 5번: 공식 핫이슈 찬반 토론 & 네이버 검색창('스톡마스터 AI') CTA 완제품 카드 (slide_5.png)
  - 최종 저장: Desktop/한국 카드뉴스_산출물/주식/[주제06] AI퀀트비서_총괄소개_20대훈남/
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
logger = logging.getLogger("RenderTopic6CardnewsAll")

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from brands.stock.capture_stock_topic6_live_iframe_exact import capture_all_topic6_exact_screens
from brands.stock.stock_cardnews_s1_topic6_builder import StockCardnewsS1Topic6Builder
from brands.stock.stock_cardnews_s2_topic6_builder import StockCardnewsS2Topic6Builder
from brands.stock.stock_cardnews_s3_topic6_builder import StockCardnewsS3Topic6Builder
from brands.stock.stock_cardnews_s4_topic6_builder import StockCardnewsS4Topic6Builder
from brands.stock.stock_cardnews_s5_topic6_builder import StockCardnewsS5Topic6Builder


def render_all_topic6_cardnews(force_recapture: bool = False, custom_photo_path: str = None):
    output_dir = Path(os.environ.get("USERPROFILE", "C:/Users/zkfnt")) / "Desktop" / "한국 카드뉴스_산출물" / "주식" / "[주제06] AI퀀트비서_총괄소개_20대훈남"
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"📂 [주식 6번 주제 카드뉴스 산출물 폴더]: {output_dir}")

    # 1. 📱 [실제 라이브 웹앱 실시간 동적 캡처]
    if force_recapture:
        logger.info("📱 [Step 1] 실제 라이브 웹앱에서 3대 실물 화면 실시간 추출 중...")
        try:
            capture_all_topic6_exact_screens()
        except Exception as e:
            logger.warning(f"웹앱 캡처 중 경고 (기존 에셋 활용): {e}")

    # 2. Slide 1: 블룸버그/삼프로TV 스튜디오 8등신 훈남 앵커 표지
    slide1_path = output_dir / "slide_1.png"
    s1_builder = StockCardnewsS1Topic6Builder()
    
    photo_file = Path(r"D:\ComfyUI_Wan_Engine\ComfyUI\output\stock_topic6_cover_male_fresh_00001_.png")
    if not photo_file.exists():
        candidates = list(Path("D:/ComfyUI_Wan_Engine/ComfyUI/output").glob("stock_topic6_*.png"))
        if candidates:
            photo_file = sorted(candidates, key=os.path.getmtime, reverse=True)[0]

    if photo_file and photo_file.exists():
        logger.info(f"🎨 [Slide 1] 기존 생성된 훈남 앵커 실사 사용: {photo_file.name}")
        s1_builder.render_cover_slide(photo_file, str(slide1_path))
    else:
        logger.info("🎨 [Slide 1] Wan 2.1 신규 훈남 앵커 실사 표지 GPU 생성 중...")
        fresh_photo = s1_builder.generate_fresh_wan_photo()
        s1_builder.render_cover_slide(fresh_photo, str(slide1_path))
    logger.info(f"✅ [Slide 1] 스튜디오 훈남 앵커 표지 렌더링 완료: {slide1_path.name}")

    # 3. Slide 2: 10분 계량 전광판 1위 종목 아코디언 오픈 폰뷰
    logger.info("⚡ [Slide 2] 10분 계량 전광판 1위 아코디언 폰뷰 렌더링 중...")
    s2_builder = StockCardnewsS2Topic6Builder()
    s2_path = output_dir / "slide_2.png"
    s2_builder.render_slide(str(s2_path))
    logger.info(f"✅ [Slide 2] 10분 계량 전광판 1위 아코디언 폰뷰 렌더링 완료: {s2_path.name}")

    # 4. Slide 3: 1위 종목 기술 지표 모달 폰뷰
    logger.info("📊 [Slide 3] 1위 종목 기술 지표 폰뷰 렌더링 중...")
    s3_builder = StockCardnewsS3Topic6Builder()
    s3_path = output_dir / "slide_3.png"
    s3_builder.render_slide(str(s3_path))
    logger.info(f"✅ [Slide 3] 1위 종목 기술 지표 폰뷰 렌더링 완료: {s3_path.name}")

    # 5. Slide 4: 1위 종목 수급 현황 모달 폰뷰
    logger.info("🐋 [Slide 4] 1위 종목 수급 현황 폰뷰 렌더링 중...")
    s4_builder = StockCardnewsS4Topic6Builder()
    s4_path = output_dir / "slide_4.png"
    s4_builder.render_slide(str(s4_path))
    logger.info(f"✅ [Slide 4] 1위 종목 수급 현황 폰뷰 렌더링 완료: {s4_path.name}")

    # 6. Slide 5: 공식 핫이슈 찬반 토론 & 네이버 검색창 CTA 카드
    logger.info("🏆 [Slide 5] 공식 5번 CTA 카드뉴스 렌더링 중...")
    s5_builder = StockCardnewsS5Topic6Builder()
    s5_path = output_dir / "slide_5.png"
    s5_builder.render_slide(str(s5_path))
    logger.info(f"✅ [Slide 5] 공식 CTA 카드 렌더링 완료: {s5_path.name}")

    logger.info(f"🎉 [주식 6번 주제 완제품 5장 카드뉴스 일괄 렌더링 100% 완료] -> {output_dir}")
    return [
        str(slide1_path),
        str(s2_path),
        str(s3_path),
        str(s4_path),
        str(s5_path)
    ]


if __name__ == "__main__":
    results = render_all_topic6_cardnews(force_recapture=True)
    print("\n" + "=" * 70)
    print("🎉 [StockMaster AI 주식 6번 주제 5장 카드뉴스 전체 완제품 생성 완료]")
    for idx, path in enumerate(results, start=1):
        print(f"  {idx}번 카드: {path}")
    print("=" * 70)
