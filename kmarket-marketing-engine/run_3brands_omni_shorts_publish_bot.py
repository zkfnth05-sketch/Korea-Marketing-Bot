# -*- coding: utf-8 -*-
"""
[완전 무인 봇] Run3BrandsOmniShortsPublishBot - 🤖 [3대 앱 숏폼 실물 3대 SNS 자율 송출 봇]
========================================================================================
- 브랜드: 대한민국 3대 앱 (💖 Aura 데이팅, 🛡️ 보험 리밸런스, 📈 StockMaster AI)
- 대표님 엄중 지침 준수:
  1. [틱톡 전면 배제]: 틱톡은 추후 완결하며, 현재 100% 호출 금지
  2. [완제품 직결]: 새로 무겁게 GPU 렌더링하지 않고, 바탕화면에 이미 완성된 실물 숏폼 MP4 사용
  3. [3대 SNS 전담]: 유튜브 쇼츠 + 메타 릴스(인스타/페북) + 네이버 클립
  4. [공식 검색어 & 링크 첫 댓글/고정 댓글 100% 완결]:
     - 💖 Aura: '아우라AI데이팅' (붙여쓰기) + https://aura-ai-dating.vercel.app/
     - 🛡️ 보험: '보험 리밸런스' (띄어쓰기) + https://insure-rebalance.vercel.app/
     - 📈 주식: '스톡마스터 AI' (띄어쓰기) + https://stockmaster-ai.vercel.app/
  5. [완전 무인 봇]: 안티그래피티가 수동 조작하지 않고, 봇이 스스로 브라우저를 띄워 순차 자율 완결
"""

import os
import sys
import json
import time
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List

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
logger = logging.getLogger("OmniPublishBot")

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from core.engine.browser_guard import clean_browser_profile_locks


class OmniPublishBot:
    """3대 브랜드 숏폼 실물 무인 자율 송출 봇"""

    BRANDS_CONFIG = {
        "aura": {
            "name": "💖 Aura AI 데이팅",
            "keyword": "아우라AI데이팅",
            "url": "https://aura-ai-dating.vercel.app/",
            "pinned_comment": "👉 Aura AI 데이팅 공식 앱 바로가기: https://aura-ai-dating.vercel.app/\n네이버 검색창에 '아우라AI데이팅'을 검색해 보세요! ✨",
            "mp4": Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Aura\Aura_08_safe_radar_20261011_180012\Aura_22초숏폼_주제08_safe_radar_20261011_180012.mp4"),
            "topic_id": 8,
            "title": "[안전 레이더] 호감도 1위 소개팅 앱 #아우라AI데이팅 #Shorts"
        },
        "insurance": {
            "name": "🛡️ 보험 리밸런스",
            "keyword": "보험 리밸런스",
            "url": "https://insure-rebalance.vercel.app/",
            "pinned_comment": "👉 보험 리밸런스 무료 자가진단 바로가기: https://insure-rebalance.vercel.app/\n네이버 검색창에 '보험 리밸런스'를 검색해 보세요! 🛡️",
            "mp4": Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Insurance\Insurance_07_duplicate_coverage_diet_20261012_100027\Insurance_22초숏폼_주제07_duplicate_coverage_diet_20261012_100027.mp4"),
            "topic_id": 7,
            "title": "[중복특약 삭제] 매달 새는 보험료 80% 줄이는 꿀팁 #보험리밸런스 #Shorts"
        },
        "stock": {
            "name": "📈 StockMaster AI",
            "keyword": "스톡마스터 AI",
            "url": "https://stockmaster-ai.vercel.app/",
            "pinned_comment": "👉 StockMaster AI 실시간 퀀트 분석 바로가기: https://stockmaster-ai.vercel.app/\n네이버 검색창에 '스톡마스터 AI'를 검색해 보세요! 📈",
            "mp4": Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Stock\[주제01] 삼성전자_20대여성아나운서_20261010_133224\★_Stock_34초숏폼_주제01_삼성전자_완제품.mp4"),
            "topic_id": 1,
            "title": "[삼성전자 수급] 외인 137만주 쌍끌이 실시간 퀀트 진단 #스톡마스터AI #Shorts"
        }
    }

    OUTPUT_RECEIPT = CURRENT_DIR / "outputs" / "proofs" / "3brands_omni_publish_receipt.json"

    def __init__(self):
        self.OUTPUT_RECEIPT.parent.mkdir(parents=True, exist_ok=True)

    def _clean_locks(self, brand: str):
        """브라우저 프로필 락 파일 사전 정리"""
        b_dir = CURRENT_DIR / "brands" / brand
        for p_name in ["youtube_chrome_profile", "meta_chrome_profile", "naver_browser_profile"]:
            p_dir = b_dir / p_name
            if p_dir.exists():
                clean_browser_profile_locks(p_dir)

    def run_brand_publish(self, brand: str) -> Dict[str, Any]:
        """단일 브랜드 3대 플랫폼(유튜브/메타/네이버) 무인 송출 + 댓글 달기"""
        cfg = self.BRANDS_CONFIG.get(brand)
        if not cfg:
            return {"error": f"Unknown brand: {brand}"}

        mp4_path = cfg["mp4"]
        if not mp4_path.exists():
            logger.critical(f"❌ [{cfg['name']}] 실물 숏폼 MP4 파일 부재: {mp4_path}")
            return {"error": "MP4 file not found"}

        logger.info("\n" + "=" * 70)
        logger.info(f"🚀 [{cfg['name']}] 3대 SNS 무인 송출 봇 가동 시작")
        logger.info(f"📁 대상 비디오: {mp4_path.name}")
        logger.info(f"💬 고정 댓글: {cfg['pinned_comment']}")
        logger.info("=" * 70 + "\n")

        self._clean_locks(brand)
        results = {
            "brand": brand,
            "brand_name": cfg["name"],
            "video_file": str(mp4_path),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "channels": {}
        }

        # ── [1. 유튜브 쇼츠 + 고정 댓글 봇] ──
        logger.info(f"🔴 [1/3 유튜브 쇼츠 봇] {cfg['name']} 업로드 및 고정 댓글 작성 시작...")
        try:
            if brand == "aura":
                from brands.aura.aura_youtube_bot_publisher import AuraYouTubeBotPublisher
                pub = AuraYouTubeBotPublisher(headless=True)
            elif brand == "insurance":
                from brands.insurance.insurance_youtube_bot_publisher import InsuranceYouTubeBotPublisher
                pub = InsuranceYouTubeBotPublisher(headless=True)
            else:
                from brands.stock.stock_youtube_bot_publisher import StockYouTubeBotPublisher
                pub = StockYouTubeBotPublisher(headless=True)

            yt_res = pub.publish_short(
                video_path=str(mp4_path),
                topic_id=cfg["topic_id"],
                title=cfg["title"],
                privacy_status="public"
            )
            results["channels"]["youtube"] = yt_res
            logger.info(f"🎉 [{cfg['name']} 유튜브 쇼츠 완료] 상태: {yt_res.get('status')} | URL: {yt_res.get('video_url', '-')}")
        except Exception as ye:
            logger.error(f"❌ [{cfg['name']} 유튜브 예외] {ye}")
            results["channels"]["youtube"] = {"status": "error", "error": str(ye)}

        # 브라우저 인터벌 휴식
        time.sleep(5)
        self._clean_locks(brand)

        # ── [2. Meta 릴스(인스타/페북) 봇] ──
        logger.info(f"🚀 [2/3 Meta 릴스 봇] {cfg['name']} Meta Business Suite 무인 송출 시작...")
        try:
            if brand == "aura":
                from brands.aura.aura_mbs_reels_publisher import AuraMBSReelsPublisher
                mbs = AuraMBSReelsPublisher()
            elif brand == "insurance":
                from brands.insurance.insurance_mbs_reels_publisher import InsuranceMBSReelsPublisher
                mbs = InsuranceMBSReelsPublisher()
            else:
                from brands.stock.stock_mbs_reels_publisher import StockMBSReelsPublisher
                mbs = StockMBSReelsPublisher()

            caption_with_comment = f"{cfg['title']}\n\n{cfg['pinned_comment']}"
            mbs_res = mbs.publish_reel(
                video_path=str(mp4_path),
                caption=caption_with_comment
            )
            results["channels"]["meta_reels"] = mbs_res
            logger.info(f"🎉 [{cfg['name']} Meta 릴스 완료] 상태: {mbs_res.get('status')}")
        except Exception as me:
            logger.error(f"❌ [{cfg['name']} Meta 예외] {me}")
            results["channels"]["meta_reels"] = {"status": "error", "error": str(me)}

        # 브라우저 인터벌 휴식
        time.sleep(5)
        self._clean_locks(brand)

        # ── [3. 네이버 클립 봇] ──
        logger.info(f"🟢 [3/3 네이버 클립 봇] {cfg['name']} 네이버 클립 스튜디오 무인 송출 시작...")
        try:
            if brand == "aura":
                from brands.aura.aura_naver_clip_publisher import AuraNaverClipPublisher
                clip = AuraNaverClipPublisher()
            elif brand == "insurance":
                from brands.insurance.insurance_naver_clip_publisher import InsuranceNaverClipPublisher
                clip = InsuranceNaverClipPublisher()
            else:
                from brands.stock.stock_naver_clip_publisher import StockNaverClipPublisher
                clip = StockNaverClipPublisher()

            clip_res = clip.publish_clip(
                video_path=str(mp4_path),
                topic_id=cfg["topic_id"],
                title=cfg["title"],
                description=cfg["pinned_comment"]
            )
            results["channels"]["naver_clip"] = clip_res
            logger.info(f"🎉 [{cfg['name']} 네이버 클립 완료] 상태: {clip_res.get('status')}")
        except Exception as ce:
            logger.error(f"❌ [{cfg['name']} 네이버 클립 예외] {ce}")
            results["channels"]["naver_clip"] = {"status": "error", "error": str(ce)}

        return results

    def run_all_3brands(self) -> Dict[str, Any]:
        """3개 앱 순차적으로 100% 무인 송출 가동"""
        logger.info("\n" + "=" * 75)
        logger.info("🤖 [대한민국 3대 앱] 숏폼 실물 3대 SNS(유튜브+메타+네이버) 무인 송출 봇 출격")
        logger.info("• 대상: 💖 Aura ➔ 🛡️ 보험 리밸런스 ➔ 📈 StockMaster AI")
        logger.info("• 원칙: 틱톡 0% 배제 / 완성본 MP4 직결 / 공식 검색어 & 링크 첫 댓글 100% 완결")
        logger.info("=" * 75 + "\n")

        all_results = {}
        for brand in ["aura", "insurance", "stock"]:
            res = self.run_brand_publish(brand)
            all_results[brand] = res
            # 브랜드 간 15초 안전 대기
            time.sleep(15)

        with open(self.OUTPUT_RECEIPT, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)

        logger.info(f"\n🎉 [3대 앱 송출 봇 완결] 영수증 파일 저장 완료: {self.OUTPUT_RECEIPT}")
        return all_results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="3대 앱 숏폼 실물 3대 SNS 무인 송출 봇")
    parser.add_argument("--brand", "-b", choices=["aura", "insurance", "stock", "all"], default="all")
    args = parser.parse_args()

    bot = OmniPublishBot()
    if args.brand == "all":
        bot.run_all_3brands()
    else:
        bot.run_brand_publish(args.brand)
