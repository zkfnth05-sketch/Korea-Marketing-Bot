# -*- coding: utf-8 -*-
"""
🤖 [완전 무인 봇] Run3BrandsMetaReelsBot - 3대 브랜드 Meta 릴스 자율 송출 봇
========================================================================
- 브랜드: 대한민국 3대 앱 (💖 Aura 데이팅, 🛡️ 보험 리밸런스, 📈 StockMaster AI)
- 대표님 지침 준수:
  1. 100% 무인 봇이 백그라운드에서 순차 자율 실행
  2. 글자 레시피(영/한 이중 언어 매칭) 기반 무결점 Meta Business Suite 업로드
  3. 인스타그램 & 페이스북 동시 송출 및 첫 댓글/캡션 기입 완결
  4. 송출 완료 후 실물 증빙(영수증 및 캡처) 자동 저장
"""

import os
import sys
import json
import time
import logging
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("3BrandsMetaReelsBot")

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from core.engine.browser_guard import clean_browser_profile_locks

BRANDS_CONFIG = {
    "aura": {
        "name": "💖 Aura AI 데이팅",
        "keyword": "아우라AI데이팅",
        "url": "https://aura-ai-dating.vercel.app/",
        "pinned_comment": "👉 Aura AI 데이팅 공식 앱 바로가기: https://aura-ai-dating.vercel.app/\n네이버 검색창에 '아우라AI데이팅'을 검색해 보세요! ✨",
        "mp4": Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Aura\Aura_08_safe_radar_20261011_180012\Aura_22초숏폼_주제08_safe_radar_20261011_180012.mp4"),
        "title": "[안전 레이더] 호감도 1위 소개팅 앱 #아우라AI데이팅 #Shorts"
    },
    "insurance": {
        "name": "🛡️ 보험 리밸런스",
        "keyword": "보험 리밸런스",
        "url": "https://insure-rebalance.vercel.app/",
        "pinned_comment": "👉 보험 리밸런스 무료 자가진단 바로가기: https://insure-rebalance.vercel.app/\n네이버 검색창에 '보험 리밸런스'를 검색해 보세요! 🛡️",
        "mp4": Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Insurance\Insurance_07_duplicate_coverage_diet_20261012_100027\Insurance_22초숏폼_주제07_duplicate_coverage_diet_20261012_100027.mp4"),
        "title": "[중복특약 삭제] 매달 새는 보험료 80% 줄이는 꿀팁 #보험리밸런스 #Shorts"
    },
    "stock": {
        "name": "📈 StockMaster AI",
        "keyword": "스톡마스터 AI",
        "url": "https://stockmaster-ai.vercel.app/",
        "pinned_comment": "👉 StockMaster AI 실시간 퀀트 분석 바로가기: https://stockmaster-ai.vercel.app/\n네이버 검색창에 '스톡마스터 AI'를 검색해 보세요! 📈",
        "mp4": Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Stock\[주제01] 삼성전자_20대여성아나운서_20261010_133224\★_Stock_34초숏폼_주제01_삼성전자_완제품.mp4"),
        "title": "[삼성전자 수급] 외인 137만주 쌍끌이 실시간 퀀트 진단 #스톡마스터AI #Shorts"
    }
}

RECEIPT_FILE = CURRENT_DIR / "outputs" / "proofs" / "3brands_meta_reels_receipt.json"


def clean_brand_meta_locks(brand: str):
    p_dir = CURRENT_DIR / "brands" / brand / "meta_chrome_profile"
    if p_dir.exists():
        clean_browser_profile_locks(p_dir)


def run_meta_bot():
    RECEIPT_FILE.parent.mkdir(parents=True, exist_ok=True)
    summary_results = {}

    logger.info("================================================================================")
    logger.info("🚀 [3대 브랜드 Meta 릴스 무인 자율 송출 봇] 전격 가동 시작")
    logger.info("================================================================================")

    for brand_key in ["aura", "insurance", "stock"]:
        cfg = BRANDS_CONFIG[brand_key]
        logger.info(f"\n▶ [{cfg['name']}] Meta Business Suite 릴스 송출 착수...")

        clean_brand_meta_locks(brand_key)
        mp4_path = cfg["mp4"]
        caption = f"{cfg['title']}\n\n{cfg['pinned_comment']}"

        if not mp4_path.exists():
            logger.critical(f"❌ [{cfg['name']}] 비디오 파일 부재: {mp4_path}")
            summary_results[brand_key] = {"status": "error", "error": "mp4 missing"}
            continue

        try:
            if brand_key == "aura":
                from brands.aura.aura_mbs_reels_publisher import AuraMBSReelsPublisher
                publisher = AuraMBSReelsPublisher()
            elif brand_key == "insurance":
                from brands.insurance.insurance_mbs_reels_publisher import InsuranceMBSReelsPublisher
                publisher = InsuranceMBSReelsPublisher()
            else:
                from brands.stock.stock_mbs_reels_publisher import StockMBSReelsPublisher
                publisher = StockMBSReelsPublisher()

            res = publisher.publish_reel(
                video_path=str(mp4_path),
                caption=caption
            )
            summary_results[brand_key] = res
            logger.info(f"✅ [{cfg['name']}] Meta 릴스 송출 결과: {res.get('status')} | {res.get('message', '')}")

        except Exception as e:
            logger.error(f"❌ [{cfg['name']}] Meta 릴스 송출 중 예외 발생: {e}")
            summary_results[brand_key] = {"status": "error", "error": str(e)}

        # 브라우저 간 간섭 방지 인터벌
        time.sleep(8)
        clean_brand_meta_locks(brand_key)

    with open(RECEIPT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary_results, f, ensure_ascii=False, indent=2)

    logger.info("================================================================================")
    logger.info(f"🎉 3대 브랜드 Meta 릴스 송출 사이클 완료! 결과 영수증: {RECEIPT_FILE}")
    logger.info("================================================================================")


if __name__ == "__main__":
    run_meta_bot()
