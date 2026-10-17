# -*- coding: utf-8 -*-
"""
[실행기] Verify3BrandsPublishedPostsAndComments - 📊 [3대 앱 게시물 및 첫 댓글 실측 확인기]
========================================================================================
- 역할:
  1. 3개 앱(Aura, 보험 리밸런스, StockMaster AI)의 유튜브 쇼츠, 메타 릴스, 네이버 클립
     실제 게시물이 살아서 정상 노출되는지 실측 확인
  2. 첫 댓글(공식 검색어 & 공식 랜딩 URL 링크) 및 상단 고정(Pin)이 정상 달렸는지 실측 검증
  3. 실시간 검증 스크린샷 증빙 캡처 및 영수증 자동 생성
"""

import os
import sys
import json
import logging
import asyncio
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
logger = logging.getLogger("OmniVerifierCLI")

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from core.verification.omni_post_comment_verifier import OmniPostCommentVerifier


def load_receipt_urls() -> dict:
    """최근 송출 영수증에서 각 브랜드별 유튜브/릴스 URL 자동 추출"""
    receipt_file = CURRENT_DIR / "outputs" / "proofs" / "3brands_omni_publish_receipt.json"
    yt_urls = {}
    if receipt_file.exists():
        try:
            with open(receipt_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for b, info in data.items():
                if isinstance(info, dict):
                    channels = info.get("channels", {})
                    yt_info = channels.get("youtube", {})
                    url = yt_info.get("video_url") or yt_info.get("url")
                    if url:
                        yt_urls[b] = url
        except Exception as e:
            logger.warning(f"영수증 파일 파싱 주의: {e}")
    return yt_urls


def print_summary_table(report: dict):
    """검증 결과를 터미널 표 형태로 예쁘게 출력"""
    print("\n" + "=" * 90)
    print("📊 [3대 브랜드 3대 SNS 게시물 & 댓글 실측 검증 종합 리포트]")
    print("=" * 90)
    print(f"{'브랜드':<18} | {'플랫폼':<15} | {'게시물 상태':<12} | {'댓글/문구 상태':<20} | {'고정핀':<6}")
    print("-" * 90)

    for brand, b_info in report.items():
        b_name = b_info.get("brand_name", brand)
        for plat_key in ["youtube", "meta", "naver"]:
            plat_data = b_info.get(plat_key, {})
            p_name = plat_data.get("platform", plat_key)
            post_st = plat_data.get("post_status", "UNKNOWN")
            comm_st = plat_data.get("comment_status", "UNKNOWN")
            is_pin = "📌 YES" if plat_data.get("is_pinned") else "NO"
            print(f"{b_name:<16} | {p_name:<15} | {post_st:<12} | {comm_st:<20} | {is_pin:<6}")

    print("=" * 90)
    print("📸 실측 증빙 스크린샷 저장 위치: outputs/proofs/verify_*.png")
    print("📑 상세 JSON 영수증: outputs/proofs/latest_verification_report.json")
    print("=" * 90 + "\n")


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="3대 앱 게시물 및 첫 댓글 실측 확인기")
    parser.add_argument("--brand", "-b", choices=["aura", "insurance", "stock", "all"], default="all")
    parser.add_argument("--url", "-u", help="검증할 유튜브 쇼츠 URL (지정 시 우선 검증)", default=None)
    parser.add_argument("--headless", action="store_true", default=True, help="헤드리스 모드 (기본 True)")
    args = parser.parse_args()

    verifier = OmniPostCommentVerifier(headless=args.headless)
    yt_urls = load_receipt_urls()

    if args.url and args.brand != "all":
        yt_urls[args.brand] = args.url

    # 기본 알려진 최근 URL 등록
    if "aura" not in yt_urls:
        yt_urls["aura"] = "https://youtube.com/shorts/FGHn1Ngu5Xo"

    logger.info("🚀 3대 앱 게시물 및 댓글 실측 검증 시작...")
    if args.brand == "all":
        report = await verifier.verify_all_3brands(yt_urls)
    else:
        single_res = await verifier.verify_single_brand(args.brand, yt_urls.get(args.brand))
        report = {args.brand: single_res}

    print_summary_table(report)


if __name__ == "__main__":
    asyncio.run(main())
