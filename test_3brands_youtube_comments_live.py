# -*- coding: utf-8 -*-
"""
3대 브랜드(Aura, 보험 리밸런스, StockMaster AI) 유튜브 쇼츠 댓글 등록 및 핀 고정 실물 테스트 러너
"""
import sys
import json
import logging
from pathlib import Path

# UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent
ENGINE_ROOT = PROJECT_ROOT / "kmarket-marketing-engine"
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from brands.aura.aura_youtube_bot_publisher import AuraYouTubeBotPublisher
from brands.insurance.insurance_youtube_bot_publisher import InsuranceYouTubeBotPublisher
from brands.stock.stock_youtube_bot_publisher import StockYouTubeBotPublisher

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger("Test3BrandsYouTube")

TARGETS = [
    {
        "brand": "aura",
        "name": "💖 Aura 데이팅",
        "cls": AuraYouTubeBotPublisher,
        "video_id": "HaI-_Uxbsis",  # 오늘 업로드된 공식 최신 영상
        "keyword": "아우라AI데이팅"
    },
    {
        "brand": "insurance",
        "name": "🛡️ 보험 리밸런스",
        "cls": InsuranceYouTubeBotPublisher,
        "video_id": "BAC45AnvTxk",
        "keyword": "보험 리밸런스"
    },
    {
        "brand": "stock",
        "name": "📈 StockMaster AI",
        "cls": StockYouTubeBotPublisher,
        "video_id": "2UtWJchudqA",
        "keyword": "스톡마스터 AI"
    }
]

def main():
    logger.info("=" * 70)
    logger.info("🚀 [3대 브랜드 유튜브 쇼츠 댓글 100% 무인 등록 및 핀 고정 실물 테스트 가동]")
    logger.info("=" * 70)

    results = {}
    for target in TARGETS:
        brand = target["brand"]
        name = target["name"]
        vid = target["video_id"]
        logger.info(f"\n▶ [{name}] 유튜브 댓글 + 핀 고정 시작 (대상 영상: https://youtube.com/shorts/{vid})")

        try:
            bot = target["cls"](headless=False)
            res = bot.post_comment_only(vid)
            results[brand] = res
            status = res.get("status")
            comm_status = res.get("comment_status")
            logger.info(f"결과: status={status}, comment_status={comm_status}, msg={res.get('message')}")
        except Exception as e:
            logger.error(f"❌ [{name}] 실행 중 예외 발생: {e}")
            results[brand] = {"status": "error", "error": str(e)}

    report_path = PROJECT_ROOT / "outputs" / "proofs" / "youtube_comments_test_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logger.info("\n" + "=" * 70)
    logger.info(f"📋 최종 테스트 결과 저장 완료: {report_path}")
    logger.info(json.dumps(results, ensure_ascii=False, indent=2))
    logger.info("=" * 70)

if __name__ == "__main__":
    main()
