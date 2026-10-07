# -*- coding: utf-8 -*-
"""
RenderTopic2CardnewsAll - 🚀 [StockMaster AI 주식 2번 주제 5장 카드뉴스 전체 일괄 렌더링]
========================================================================================
• 역할:
  - 주식 2번 주제: [SK하이닉스 HBM 실시간 퀀트 수급 & AI 리스크 진단]
  - 1번 표지: Wan 2.1 20대 훈남 남성 퀀트 앵커 실사 표지 (slide_1.png)
  - 2번: 실시간 웹앱 SK하이닉스 다크 퀀트 전광판 스마트폰 뷰 (slide_2.png)
  - 3번: 실시간 웹앱 SK하이닉스 [기본 정보] 기업 실적 추이 스마트폰 뷰 (slide_3.png)
  - 4번: 실시간 웹앱 SK하이닉스 [수급 현황] 외인/기관 순매수 스마트폰 뷰 (slide_4.png)
  - 5번: 핫이슈 찬반 토론 & 네이버 검색창('스톡마스터 AI') CTA 완제품 (slide_5.png)
  - 최종 저장: Desktop/한국 카드뉴스_산출물/주식/[주제02] SK하이닉스_HBM수급_20대남성아나운서/
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
logger = logging.getLogger("RenderTopic2CardnewsAll")

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from brands.stock.stock_realtime_data_fetcher import StockRealtimeDataFetcher
from brands.stock.stock_cardnews_copy_writer import StockCardnewsCopyWriter
from brands.stock.capture_hynix_live_screens import capture_all_hynix_screens
from brands.stock.stock_cardnews_s1_topic2_builder import StockCardnewsS1Topic2Builder
from brands.stock.stock_cardnews_s2_topic2_builder import StockCardnewsS2Topic2Builder
from brands.stock.stock_cardnews_s3_topic2_builder import StockCardnewsS3Topic2Builder
from brands.stock.stock_cardnews_s4_topic2_builder import StockCardnewsS4Topic2Builder
from brands.stock.stock_cardnews_s5_topic2_builder import StockCardnewsS5Topic2Builder


def render_all_topic2_cardnews():
    output_dir = Path(os.environ.get("USERPROFILE", "C:/Users/zkfnt")) / "Desktop" / "한국 카드뉴스_산출물" / "주식" / "[주제02] SK하이닉스_HBM수급_20대남성아나운서"
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"📂 [주식 2번 주제 카드뉴스 산출물 폴더]: {output_dir}")

    # 1. 🌐 [실시간 주식앱 라이브 데이터 크롤링]
    logger.info("🌐 [Step 1] 주식앱 실제 웹사이트에서 SK하이닉스 실시간 팩트 데이터 추출 중...")
    fetcher = StockRealtimeDataFetcher()
    real_data = fetcher.fetch_stock_data("SK하이닉스")
    logger.info(f"📊 [실시간 팩트 데이터 추출 성공]: 현재가={real_data.get('price', '1,734,000')} / 점수={real_data.get('total_score', '92.5')}점 / 외인={real_data.get('foreign_net', '대량 순매수')}")

    # 2. ✍️ [제미나이 1~5번 실시간 팩트 기반 맞춤 카피 집필]
    logger.info("✍️ [Step 2] 제미나이(Gemini 2.0 Flash) 실시간 팩트 기반 카드뉴스 1~5번 카피 집필 중...")
    writer = StockCardnewsCopyWriter()
    copy_pkg = writer.write_cardnews_copy("SK하이닉스", real_data, topic_title="SK하이닉스 HBM 실시간 퀀트 수급 & AI 리스크 진단")

    # 3. 📱 [실시간 라이브 웹앱 화면 캡처]
    assets_dir = Path(__file__).resolve().parent / "assets"
    s2_asset = assets_dir / "stock_topic2_s2_quant_board_exact.png"
    s3_asset = assets_dir / "stock_topic2_s3_fundamental_real.png"
    s4_asset = assets_dir / "stock_topic2_s4_supply_real.png"

    if not (s2_asset.exists() and s3_asset.exists() and s4_asset.exists()):
        logger.info("📱 [Step 3] 실시간 라이브 웹앱 SK하이닉스 화면 캡처 실행 중...")
        capture_all_hynix_screens(assets_dir)

    # 4. Slide 1: 20대 남성 훈남 앵커 표지 (Wan 2.1 신규 실사 및 제미나이 카피)
    slide1_path = output_dir / "slide_1.png"
    s1_builder = StockCardnewsS1Topic2Builder()
    if not slide1_path.exists():
        logger.info("🎨 [Slide 1] 20대 남성 앵커 Wan 2.1 신규 실사 표지 생성 중...")
        fresh_photo = s1_builder.generate_fresh_wan_photo()
        s1_builder.render_cover_slide(fresh_photo, str(slide1_path), copy_pkg.get("slide_1"))
    else:
        # 기존 남성 실사 사진에 제미나이 실시간 카피 덮어쓰기 렌더링
        fresh_photos = list(Path(__file__).resolve().parent.glob("**/stock_topic2_cover_male_*.png")) + list(Path("D:/ComfyUI_Wan_Engine/ComfyUI/output").glob("stock_topic2_cover_male_*.png"))
        target_photo = fresh_photos[0] if fresh_photos else slide1_path
        s1_builder.render_cover_slide(target_photo, str(slide1_path), copy_pkg.get("slide_1"))
    logger.info(f"✅ [Slide 1] 남성 앵커 표지 렌더링 완료: {slide1_path.name}")

    # 5. Slide 2: 실시간 다크 퀀트 전광판 폰뷰 (제미나이 카피 주입)
    logger.info("📱 [Slide 2] SK하이닉스 실시간 다크 퀀트 전광판 폰뷰 렌더링 중...")
    s2_builder = StockCardnewsS2Topic2Builder()
    s2_path = output_dir / "slide_2.png"
    s2_builder.render_slide(str(s2_path), copy_pkg.get("slide_2"))

    # 6. Slide 3: 기업 펀더멘털 & 분기 실적 추이 폰뷰 (제미나이 카피 주입)
    logger.info("📊 [Slide 3] SK하이닉스 실시간 기업 펀더멘털 & 실적 추이 폰뷰 렌더링 중...")
    s3_builder = StockCardnewsS3Topic2Builder()
    s3_path = output_dir / "slide_3.png"
    s3_builder.render_slide(str(s3_path), copy_pkg.get("slide_3"))

    # 7. Slide 4: 3대 주체별 실시간 수급 현황 폰뷰 (제미나이 카피 주입)
    logger.info("🔥 [Slide 4] SK하이닉스 3대 주체별 실시간 수급 현황 폰뷰 렌더링 중...")
    s4_builder = StockCardnewsS4Topic2Builder()
    s4_path = output_dir / "slide_4.png"
    s4_builder.render_slide(str(s4_path), copy_pkg.get("slide_4"))

    # 8. Slide 5: 찬반 토론 & 네이버 검색창 CTA 카드 (제미나이 카피 주입)
    logger.info("🏷️ [Slide 5] SK하이닉스 찬반 토론 & 네이버 검색 CTA 카드 렌더링 중...")
    s5_builder = StockCardnewsS5Topic2Builder()
    s5_path = output_dir / "slide_5.png"
    s5_builder.render_slide(str(s5_path), copy_pkg.get("slide_5"))

    logger.info("🎉 [RenderTopic2CardnewsAll] 주식 2번 주제 5장 완제품 카드뉴스 100% 렌더링 완료!")
    for idx in range(1, 6):
        p = output_dir / f"slide_{idx}.png"
        if p.exists():
            size_kb = p.stat().st_size / 1024
            logger.info(f"  - slide_{idx}.png ({size_kb:.1f} KB): {p}")


if __name__ == "__main__":
    render_all_topic2_cardnews()
