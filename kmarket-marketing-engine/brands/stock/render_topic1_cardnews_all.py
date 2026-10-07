# -*- coding: utf-8 -*-
"""
RenderTopic1CardnewsAll - 🎨 [StockMaster AI 주식 1번 주제 5장 완제품 카드뉴스 일괄 렌더러]
========================================================================================
• 주제: [주제01] 삼성전자 vs SK하이닉스 HBM 수급 쌍끌이
• 구성:
  - Slide 1: Wan 2.1 14B 실사 아나운서 표지 (Aura 초깔끔 노블러 규격)
  - Slide 2: 라이브 웹앱 실시간 다크 퀀트 전광판 ('삼성전자 005930' 최상단 정렬 & 세부지표)
  - Slide 3: 라이브 웹앱 실시간 [기본 정보] (기업 펀더멘털 & 분기 실적 추이 바차트)
  - Slide 4: 라이브 웹앱 실시간 [수급 현황] (3대 주체별 외인 137만주 순매수 vs 개미 손절)
  - Slide 5: 공식 엔딩 네이버 검색 유도 CTA ("네이버에 '스톡마스터 AI' 검색")
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
logger = logging.getLogger("RenderTopic1CardnewsAll")

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from brands.stock.stock_realtime_data_fetcher import StockRealtimeDataFetcher
from brands.stock.stock_cardnews_copy_writer import StockCardnewsCopyWriter
from brands.stock.capture_genuine_stock_screens import capture_all_stock_screens
from brands.stock.stock_cardnews_s1_topic1_builder import StockCardnewsS1Topic1Builder
from brands.stock.stock_cardnews_s2_topic1_builder import StockCardnewsS2Topic1Builder
from brands.stock.stock_cardnews_s3_topic1_builder import StockCardnewsS3Topic1Builder
from brands.stock.stock_cardnews_s4_topic1_builder import StockCardnewsS4Topic1Builder
from brands.stock.stock_cardnews_s5_topic1_builder import StockCardnewsS5Topic1Builder


def render_all():
    out_dir = Path(os.environ.get("USERPROFILE", "C:/Users/zkfnt")) / "Desktop" / "한국 카드뉴스_산출물" / "주식" / "[주제01] 삼성전자_수급쌍끌이_20대여성아나운서"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. 🌐 [실시간 주식앱 라이브 데이터 크롤링]
    logger.info("🌐 [1/7] 주식앱 실제 웹사이트에서 삼성전자 실시간 팩트 데이터 추출 중...")
    fetcher = StockRealtimeDataFetcher()
    real_data = fetcher.fetch_stock_data("삼성전자")
    logger.info(f"📊 [실시간 팩트 데이터 추출 성공]: 현재가={real_data.get('price', '실시간')} / 점수={real_data.get('total_score', '95.0')}점 / 외인={real_data.get('foreign_net', '대량 순매수')}")

    # 2. ✍️ [제미나이 1~5번 실시간 팩트 기반 맞춤 카피 집필]
    logger.info("✍️ [2/7] 제미나이(Gemini 2.0 Flash) 실시간 팩트 기반 카드뉴스 1~5번 카피 집필 중...")
    writer = StockCardnewsCopyWriter()
    copy_pkg = writer.write_cardnews_copy("삼성전자", real_data, topic_title="삼성전자 외인·기관 수급 쌍끌이 & 실시간 퀀트 진단")

    # 3. 실제 라이브 웹앱 실시간 캡처 실행 (2, 3, 4번 실측 화면)
    logger.info("🌐 [3/7] StockMaster AI 실제 라이브 웹앱 실시간 캡처 시작...")
    capture_all_stock_screens()

    # 4. Slide 1 (표지)
    logger.info("🎨 [4/7] Slide 1 (실사 아나운서 표지) 렌더링...")
    b1 = StockCardnewsS1Topic1Builder()
    s1_file = out_dir / "slide_1.png"
    # 기존 고화질 실사 사진 탐색
    photo_candidates = list(b1.base_dir.glob("*.png")) + list((b1.base_dir / "assets").glob("*.png"))
    stock_photo = None
    for p in photo_candidates:
        if "cover" in p.name.lower() or "anchor" in p.name.lower() or "fresh" in p.name.lower() or "wan" in p.name.lower():
            stock_photo = p
            break
    
    if stock_photo and stock_photo.exists():
        b1.render_cover_slide(stock_photo, str(s1_file), copy_pkg.get("slide_1"))
    else:
        b1.produce_fresh_slide1(out_dir)

    # 5. Slide 2 (다크 퀀트 전광판 실측)
    logger.info("🎨 [5/7] Slide 2 (다크 퀀트 전광판 실측) 렌더링...")
    b2 = StockCardnewsS2Topic1Builder()
    s2_file = out_dir / "slide_2.png"
    b2.render_slide(str(s2_file), copy_pkg.get("slide_2"))

    # 6. Slide 3 (기업 펀더멘털 & 실적 바차트)
    logger.info("🎨 [6/7] Slide 3 (기업 펀더멘털 & 실적 추이) 렌더링...")
    b3 = StockCardnewsS3Topic1Builder()
    s3_file = out_dir / "slide_3.png"
    b3.render_slide(str(s3_file), copy_pkg.get("slide_3"))

    # 7. Slide 4 (3대 주체별 외인 매수 vs 개미 손절)
    logger.info("🎨 [7/7] Slide 4 (3대 주체별 실시간 수급) 렌더링...")
    b4 = StockCardnewsS4Topic1Builder()
    s4_file = out_dir / "slide_4.png"
    b4.render_slide(str(s4_file), copy_pkg.get("slide_4"))

    # 8. Slide 5 (엔딩 네이버 검색 CTA)
    b5 = StockCardnewsS5Topic1Builder()
    s5_file = out_dir / "slide_5.png"
    b5.render_slide(str(s5_file), copy_pkg.get("slide_5"))

    logger.info("=" * 60)
    logger.info(f"🎉 [주제01] 삼성전자 vs SK하이닉스 5장 완제품 카드뉴스 제작 100% 완료!")
    logger.info(f"📂 저장 경로: {out_dir}")
    for i in range(1, 6):
        p = out_dir / f"slide_{i}.png"
        logger.info(f"  - Slide {i}: {p.name} ({p.stat().st_size / 1024:.1f} KB)")
    logger.info("=" * 60)


if __name__ == "__main__":
    render_all()
