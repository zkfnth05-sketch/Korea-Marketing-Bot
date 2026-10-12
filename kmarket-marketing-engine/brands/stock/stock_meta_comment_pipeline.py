# -*- coding: utf-8 -*-
"""
📈 [StockMaster AI 전용] Meta 릴스 발행 후 인스타 & 페이스북 댓글 연속 집행 오케스트레이터 (독립 레고 블록)
"""
import sys
import logging
from pathlib import Path
from typing import Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logger = logging.getLogger("StockMetaCommentPipeline")
if not logger.handlers:
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("[%(asctime)s] [StockMetaComment] %(message)s"))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from brands.stock.stock_instagram_commenter import StockInstagramCommenter
from brands.stock.stock_facebook_commenter import StockFacebookCommenter


def run_stock_meta_comments() -> Dict[str, Any]:
    """📈 스톡마스터 AI 릴스 발행 직후 인스타그램 및 페이스북에 단독 3단 첫 댓글을 자율 집행"""
    logger.info("🚀 [Stock Meta Comment] 인스타그램 & 페이스북 첫 댓글 자율 파이프라인 가동...")
    results = {}

    # 1. 인스타그램 댓글
    try:
        insta = StockInstagramCommenter()
        results["instagram"] = insta.post_comment_on_latest_reel()
    except Exception as e:
        logger.error(f"❌ 스톡마스터 인스타 댓글 예외: {e}")
        results["instagram"] = {"status": "error", "message": str(e)}

    # 2. 페이스북 댓글
    try:
        fb = StockFacebookCommenter()
        results["facebook"] = fb.post_comment_on_latest_post()
    except Exception as e:
        logger.error(f"❌ 스톡마스터 페이스북 댓글 예외: {e}")
        results["facebook"] = {"status": "error", "message": str(e)}

    logger.info(f"🎉 [Stock Meta Comment] 결과 요약: {results}")
    return results


if __name__ == "__main__":
    res = run_stock_meta_comments()
    print("집행 결과:", res)
