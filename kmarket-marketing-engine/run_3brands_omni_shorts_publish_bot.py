# -*- coding: utf-8 -*-
"""
[완전 무인 봇] Run3BrandsOmniShortsPublishBot - 🤖 [3대 앱 숏폼 실물 5대 SNS 자율 송출 봇]
========================================================================================
- 브랜드: 대한민국 3대 앱 (💖 Aura 데이팅, 🛡️ 보험 리밸런스, 📈 StockMaster AI)
- 대표님 엄중 지침 준수:
  1. [5대 채널 전담]: 유튜브 쇼츠 + 메타 릴스(인스타/페북) + 네이버 클립 + 틱톡 + 스레드 카드뉴스
  2. [완제품 직결]: 새로 무겁게 GPU 렌더링하지 않고, 바탕화면에 이미 완성된 실물 숏폼 MP4 사용
  3. [카드뉴스 실물 직결]: 바탕화면 최신 카드뉴스 폴더의 5장 슬라이드를 스레드 파이프라인에 직결
  4. [공식 검색어 & 링크 첫 댓글/고정 댓글 100% 완결]:
     - 💖 Aura: '아우라AI데이팅' (붙여쓰기) + https://aura-ai-dating.vercel.app/
     - 🛡️ 보험: '보험 리밸런스' (띄어쓰기) + https://insure-rebalance.vercel.app/
     - 📈 주식: '스톡마스터 AI' (띄어쓰기) + https://stockmaster-ai.vercel.app/
  5. [완전 무인 봇]: 안티그래피티가 수동 조작하지 않고, 봇이 스스로 브라우저를 띄워 순차 자율 완결
  6. [채널 단위 격리]: 한 채널이 실패해도 나머지 채널은 100% 독립 수행 (예외 완전 격리)
"""

import os
import sys
import json
import time
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

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


# ────────────────────────────────────────────────────────────────
# 채널 상수 정의
# ────────────────────────────────────────────────────────────────
CHANNEL_YOUTUBE = "youtube"
CHANNEL_META = "meta"
CHANNEL_CLIP = "clip"
CHANNEL_TIKTOK = "tiktok"
CHANNEL_THREADS = "threads"

ALL_CHANNELS: List[str] = [
    CHANNEL_YOUTUBE,
    CHANNEL_META,
    CHANNEL_CLIP,
    CHANNEL_TIKTOK,
    CHANNEL_THREADS,
]

CHANNEL_LABELS = {
    CHANNEL_YOUTUBE: "🔴 유튜브 쇼츠",
    CHANNEL_META: "🚀 Meta 릴스",
    CHANNEL_CLIP: "🟢 네이버 클립",
    CHANNEL_TIKTOK: "⚫ 틱톡(TikTok)",
    CHANNEL_THREADS: "🧵 스레드 카드뉴스",
}


class OmniPublishBot:
    """3대 브랜드 숏폼 실물 무인 자율 송출 봇 (5대 채널)"""

    BRANDS_CONFIG = {
        "aura": {
            "name": "💖 Aura AI 데이팅",
            "keyword": "아우라AI데이팅",
            "url": "https://aura-ai-dating.vercel.app/",
            "pinned_comment": "👉 Aura AI 데이팅 공식 앱 바로가기: https://aura-ai-dating.vercel.app/\n네이버 검색창에 '아우라AI데이팅'을 검색해 보세요! ✨",
            "mp4": Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Aura\Aura_08_safe_radar_20261011_180012\Aura_22초숏폼_주제08_safe_radar_20261011_180012.mp4"),
            "cardnews_root": Path(r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\아우라"),
            "topic_id": 8,
            "title": "[안전 레이더] 호감도 1위 소개팅 앱 #아우라AI데이팅 #Shorts",
            "tiktok_caption": "📍 [500m 안심 레이더 & 2030 실시간 매칭]\n거리와 취향까지 딱 맞는 내 반경 500m 인연 찾기!\n네이버에 '아우라AI데이팅' 검색 ✨\n#Aura #데이팅 #소개팅 #안심매칭 #2030연애",
        },
        "insurance": {
            "name": "🛡️ 보험 리밸런스",
            "keyword": "보험 리밸런스",
            "url": "https://insure-rebalance.vercel.app/",
            "pinned_comment": "👉 보험 리밸런스 무료 자가진단 바로가기: https://insure-rebalance.vercel.app/\n네이버 검색창에 '보험 리밸런스'를 검색해 보세요! 🛡️",
            "mp4": Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Insurance\Insurance_07_duplicate_coverage_diet_20261012_100027\Insurance_22초숏폼_주제07_duplicate_coverage_diet_20261012_100027.mp4"),
            "cardnews_root": Path(r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\보험"),
            "topic_id": 7,
            "title": "[중복특약 삭제] 매달 새는 보험료 80% 줄이는 꿀팁 #보험리밸런스 #Shorts",
            "tiktok_caption": "🛡️ [중복특약 다이어트]\n매달 새는 보험료, 중복 특약만 정리해도 80% 절감!\n네이버에 '보험 리밸런스' 검색 🛡️\n#보험리밸런스 #보험료절감 #중복특약 #재테크 #보험상식",
        },
        "stock": {
            "name": "📈 StockMaster AI",
            "keyword": "스톡마스터 AI",
            "url": "https://stockmaster-ai.vercel.app/",
            "pinned_comment": "👉 StockMaster AI 실시간 퀀트 분석 바로가기: https://stockmaster-ai.vercel.app/\n네이버 검색창에 '스톡마스터 AI'를 검색해 보세요! 📈",
            "mp4": Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Stock\[주제01] 삼성전자_20대여성아나운서_20261010_133224\★_Stock_34초숏폼_주제01_삼성전자_완제품.mp4"),
            "cardnews_root": Path(r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\주식"),
            "topic_id": 1,
            "title": "[삼성전자 수급] 외인 137만주 쌍끌이 실시간 퀀트 진단 #스톡마스터AI #Shorts",
            "tiktok_caption": "📈 [삼성전자 외인 수급 137만주]\n실시간 퀀트 점수로 세력 수급 포착!\n네이버에 '스톡마스터 AI' 검색 📈\n#스톡마스터AI #삼성전자 #주식 #퀀트 #수급분석",
        }
    }

    OUTPUT_RECEIPT = CURRENT_DIR / "outputs" / "proofs" / "3brands_omni_publish_receipt.json"

    def __init__(self):
        self.OUTPUT_RECEIPT.parent.mkdir(parents=True, exist_ok=True)

    # ────────────────────────────────────────────────────────────
    # 유틸리티
    # ────────────────────────────────────────────────────────────
    def _clean_locks(self, brand: str):
        """브라우저 프로필 락 파일 사전 정리 (5대 채널 전 프로필)"""
        b_dir = CURRENT_DIR / "brands" / brand
        for p_name in [
            "youtube_chrome_profile",
            "meta_chrome_profile",
            "naver_browser_profile",
            "tiktok_chrome_profile",
            "threads_chrome_profile",
        ]:
            p_dir = b_dir / p_name
            if p_dir.exists():
                try:
                    clean_browser_profile_locks(p_dir)
                except Exception as le:
                    logger.warning(f"⚠️ [{brand}] 프로필 락 정리 경고({p_name}): {le}")

    def find_latest_cardnews_folder(self, brand: str) -> Optional[Path]:
        """바탕화면 카드뉴스 루트에서 slide_*.png 5장 이상 보유한 최신 폴더 탐색"""
        cfg = self.BRANDS_CONFIG.get(brand)
        if not cfg:
            return None

        root: Path = cfg["cardnews_root"]
        if not root.exists():
            logger.error(f"❌ [{cfg['name']}] 카드뉴스 루트 폴더 부재: {root}")
            return None

        candidates = []
        for d in root.iterdir():
            if not d.is_dir():
                continue
            try:
                slides = sorted(d.glob("slide_*.png"))
                if len(slides) >= 5:
                    candidates.append((d.stat().st_mtime, d, len(slides)))
            except Exception:
                continue

        if not candidates:
            logger.error(f"❌ [{cfg['name']}] slide_*.png 5장 이상 보유한 카드뉴스 폴더 미발견: {root}")
            return None

        candidates.sort(key=lambda x: x[0], reverse=True)
        mtime, folder, cnt = candidates[0]
        logger.info(f"🗂️ [{cfg['name']}] 최신 카드뉴스 폴더 확정: {folder.name} (슬라이드 {cnt}장)")
        return folder

    def _run_async(self, coro):
        """이미 실행 중인 이벤트 루프가 있어도 안전하게 코루틴 실행"""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop is not None and loop.is_running():
            # 중첩 루프 환경: 별도 스레드에서 새 루프 구동
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                return ex.submit(lambda: asyncio.run(coro)).result()
        return asyncio.run(coro)

    # ────────────────────────────────────────────────────────────
    # 영수증 즉시 병합 저장 (단독 브랜드 실행 대응)
    # ────────────────────────────────────────────────────────────
    def _merge_receipt(self, brand: str, brand_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        기존 OUTPUT_RECEIPT 파일이 있으면 로드하여 해당 브랜드 결과만 즉시 병합/업데이트 후 저장.
        - 단독 브랜드 실행(--brand stock 등) 시에도 영수증이 즉시 갱신되도록 보장
        - 다른 브랜드의 기존 결과는 100% 보존 (덮어쓰기 금지)
        - 파일 손상/형식 오류 시에도 예외 없이 신규 딕셔너리로 안전 복구
        """
        merged: Dict[str, Any] = {}
        try:
            if self.OUTPUT_RECEIPT.exists() and self.OUTPUT_RECEIPT.stat().st_size > 0:
                with open(self.OUTPUT_RECEIPT, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    merged = loaded
                else:
                    logger.warning(f"⚠️ 기존 영수증 형식이 dict가 아닙니다({type(loaded).__name__}). 신규 영수증으로 재생성합니다.")
        except Exception as le:
            logger.warning(f"⚠️ 기존 영수증 로드 실패(신규 생성으로 진행): {le}")
            merged = {}

        # 해당 브랜드 결과만 병합/업데이트 (나머지 브랜드 결과는 그대로 보존)
        merged[brand] = brand_result

        try:
            with open(self.OUTPUT_RECEIPT, "w", encoding="utf-8") as f:
                json.dump(merged, f, ensure_ascii=False, indent=2)
            logger.info(f"🧾 [{brand}] 영수증 즉시 병합 저장 완료: {self.OUTPUT_RECEIPT}")
        except Exception as se:
            logger.error(f"❌ [{brand}] 영수증 저장 실패: {se}")

        return merged

    # ────────────────────────────────────────────────────────────
    # 채널별 단일 실행기 (예외 완전 격리)
    # ────────────────────────────────────────────────────────────
    def _publish_youtube(self, brand: str, cfg: Dict[str, Any], mp4_path: Path) -> Dict[str, Any]:
        if brand == "aura":
            from brands.aura.aura_youtube_bot_publisher import AuraYouTubeBotPublisher
            pub = AuraYouTubeBotPublisher(headless=True)
        elif brand == "insurance":
            from brands.insurance.insurance_youtube_bot_publisher import InsuranceYouTubeBotPublisher
            pub = InsuranceYouTubeBotPublisher(headless=True)
        else:
            from brands.stock.stock_youtube_bot_publisher import StockYouTubeBotPublisher
            pub = StockYouTubeBotPublisher(headless=True)

        return pub.publish_short(
            video_path=str(mp4_path),
            topic_id=cfg["topic_id"],
            title=cfg["title"],
            privacy_status="public"
        )

    def _publish_meta(self, brand: str, cfg: Dict[str, Any], mp4_path: Path) -> Dict[str, Any]:
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
        return mbs.publish_reel(
            video_path=str(mp4_path),
            caption=caption_with_comment
        )

    def _publish_clip(self, brand: str, cfg: Dict[str, Any], mp4_path: Path) -> Dict[str, Any]:
        if brand == "aura":
            from brands.aura.aura_naver_clip_publisher import AuraNaverClipPublisher
            clip = AuraNaverClipPublisher()
        elif brand == "insurance":
            from brands.insurance.insurance_naver_clip_publisher import InsuranceNaverClipPublisher
            clip = InsuranceNaverClipPublisher()
        else:
            from brands.stock.stock_naver_clip_publisher import StockNaverClipPublisher
            clip = StockNaverClipPublisher()

        return clip.publish_clip(
            video_path=str(mp4_path),
            topic_id=cfg["topic_id"],
            title=cfg["title"],
            description=cfg["pinned_comment"]
        )

    def _publish_tiktok(self, brand: str, cfg: Dict[str, Any], mp4_path: Path) -> Dict[str, Any]:
        """틱톡 웹 스튜디오 업로드 + 발행 성공 시 첫 댓글 자율 연동"""
        if brand == "aura":
            from brands.aura.aura_tiktok_publisher import AuraTikTokPublisher
            pub = AuraTikTokPublisher(headless=True)
        elif brand == "insurance":
            from brands.insurance.insurance_tiktok_publisher import InsuranceTikTokPublisher
            pub = InsuranceTikTokPublisher(headless=True)
        else:
            from brands.stock.stock_tiktok_publisher import StockTikTokPublisher
            pub = StockTikTokPublisher(headless=True)

        caption = cfg.get("tiktok_caption") or f"{cfg['title']}\n\n{cfg['pinned_comment']}"

        # publish_short 는 내부에서 asyncio.run 을 호출하는 동기 래퍼
        return pub.publish_short(
            video_path=str(mp4_path),
            topic_id=cfg["topic_id"],
            caption=caption,
            title=cfg["title"],
        )

    def _publish_threads(self, brand: str, cfg: Dict[str, Any]) -> Dict[str, Any]:
        """최신 카드뉴스 5장 슬라이드 ➔ 스레드 파이프라인 (5장 이미지 + 1번 타래 링크 댓글)"""
        folder = self.find_latest_cardnews_folder(brand)
        if folder is None:
            return {
                "status": "error",
                "error": "최신 카드뉴스 폴더(slide_*.png 5장 이상) 미발견",
                "brand": brand,
            }

        if brand == "aura":
            from brands.aura.aura_threads_pipeline import AuraThreadsPipeline
            pipeline = AuraThreadsPipeline(headless=True)
        elif brand == "insurance":
            from brands.insurance.insurance_threads_pipeline import InsuranceThreadsPipeline
            pipeline = InsuranceThreadsPipeline(headless=True)
        else:
            from brands.stock.stock_threads_pipeline import StockThreadsPipeline
            pipeline = StockThreadsPipeline(headless=True)

        res = self._run_async(pipeline.run_pipeline(cardnews_folder=str(folder)))
        if isinstance(res, dict):
            res.setdefault("cardnews_folder", str(folder))
        return res if isinstance(res, dict) else {"status": "unknown", "raw": str(res)}

    # ────────────────────────────────────────────────────────────
    # 브랜드 단위 실행
    # ────────────────────────────────────────────────────────────
    def run_brand_publish(
        self,
        brand: str,
        channels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """단일 브랜드 다채널 무인 송출 + 댓글 달기"""
        cfg = self.BRANDS_CONFIG.get(brand)
        if not cfg:
            return {"error": f"Unknown brand: {brand}"}

        target_channels = channels if channels else list(ALL_CHANNELS)
        target_channels = [c for c in target_channels if c in ALL_CHANNELS]
        if not target_channels:
            return {"error": f"No valid channels: {channels}"}

        mp4_path: Path = cfg["mp4"]
        needs_video = any(c != CHANNEL_THREADS for c in target_channels)

        if needs_video and not mp4_path.exists():
            logger.critical(f"❌ [{cfg['name']}] 실물 숏폼 MP4 파일 부재: {mp4_path}")
            return {"error": "MP4 file not found", "video_file": str(mp4_path)}

        logger.info("\n" + "=" * 70)
        logger.info(f"🚀 [{cfg['name']}] 무인 송출 봇 가동 시작")
        logger.info(f"📁 대상 비디오: {mp4_path.name if mp4_path.exists() else '(카드뉴스 전용 모드)'}")
        logger.info(f"📡 대상 채널: {', '.join(CHANNEL_LABELS[c] for c in target_channels)}")
        logger.info(f"💬 고정 댓글: {cfg['pinned_comment']}")
        logger.info("=" * 70 + "\n")

        self._clean_locks(brand)
        results: Dict[str, Any] = {
            "brand": brand,
            "brand_name": cfg["name"],
            "video_file": str(mp4_path),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "channels": {}
        }

        total = len(target_channels)
        for idx, ch in enumerate(target_channels, start=1):
            label = CHANNEL_LABELS[ch]
            logger.info(f"{label} [{idx}/{total}] {cfg['name']} 송출 시작...")
            try:
                if ch == CHANNEL_YOUTUBE:
                    res = self._publish_youtube(brand, cfg, mp4_path)
                elif ch == CHANNEL_META:
                    res = self._publish_meta(brand, cfg, mp4_path)
                elif ch == CHANNEL_CLIP:
                    res = self._publish_clip(brand, cfg, mp4_path)
                elif ch == CHANNEL_TIKTOK:
                    res = self._publish_tiktok(brand, cfg, mp4_path)
                elif ch == CHANNEL_THREADS:
                    res = self._publish_threads(brand, cfg)
                else:
                    res = {"status": "error", "error": f"미지원 채널: {ch}"}

                results["channels"][ch] = res
                # 🎯 성공 판별 강화: success=True 불리언 / status='success' / status='SUCCESS' 대문자까지 모두 성공 인식
                status = "success" if (res.get("success") is True or res.get("status") in ["success", "SUCCESS"]) else res.get("status", "unknown")
                logger.info(f"🎉 [{cfg['name']} {label} 완료] 상태: {status}")
            except Exception as e:
                logger.error(f"❌ [{cfg['name']} {label} 예외] {e}")
                results["channels"][ch] = {"status": "error", "error": str(e)}

            # 채널 간 브라우저 인터벌 휴식 (마지막 채널 제외)
            if idx < total:
                time.sleep(5)
                self._clean_locks(brand)

        # 🧾 [영수증 즉시 갱신] 단독 브랜드 실행 시에도 기존 영수증에 해당 브랜드 결과를 즉시 병합/저장
        try:
            self._merge_receipt(brand, results)
        except Exception as re_err:
            logger.warning(f"⚠️ [{brand}] 영수증 병합 저장 경고: {re_err}")

        return results

    # ────────────────────────────────────────────────────────────
    # 전체 실행
    # ────────────────────────────────────────────────────────────
    def run_all_3brands(self, channels: Optional[List[str]] = None) -> Dict[str, Any]:
        """3개 앱 순차적으로 100% 무인 송출 가동"""
        target_channels = channels if channels else list(ALL_CHANNELS)
        target_channels = [c for c in target_channels if c in ALL_CHANNELS]

        logger.info("\n" + "=" * 75)
        logger.info("🤖 [대한민국 3대 앱] 숏폼 실물 5대 SNS 무인 송출 봇 출격")
        logger.info("• 대상: 💖 Aura ➔ 🛡️ 보험 리밸런스 ➔ 📈 StockMaster AI")
        logger.info(f"• 채널: {', '.join(CHANNEL_LABELS[c] for c in target_channels)}")
        logger.info("• 원칙: 완성본 MP4 직결 / 최신 카드뉴스 5장 직결 / 공식 검색어 & 링크 댓글 100% 완결")
        logger.info("=" * 75 + "\n")

        all_results: Dict[str, Any] = {}
        brands = ["aura", "insurance", "stock"]
        for i, brand in enumerate(brands):
            res = self.run_brand_publish(brand, channels=target_channels)
            all_results[brand] = res
            if i < len(brands) - 1:
                # 브랜드 간 15초 안전 대기
                time.sleep(15)

        with open(self.OUTPUT_RECEIPT, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)

        logger.info(f"\n🎉 [3대 앱 송출 봇 완결] 영수증 파일 저장 완료: {self.OUTPUT_RECEIPT}")
        return all_results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="3대 앱 숏폼 실물 5대 SNS 무인 송출 봇")
    parser.add_argument(
        "--brand", "-b",
        choices=["aura", "insurance", "stock", "all"],
        default="all",
        help="대상 브랜드 (기본: all)"
    )
    parser.add_argument(
        "--channel", "-c",
        choices=["all", "youtube", "meta", "clip", "tiktok", "threads"],
        default="all",
        help="대상 채널 (기본: all)"
    )
    args = parser.parse_args()

    selected_channels = list(ALL_CHANNELS) if args.channel == "all" else [args.channel]

    bot = OmniPublishBot()
    if args.brand == "all":
        bot.run_all_3brands(channels=selected_channels)
    else:
        bot.run_brand_publish(args.brand, channels=selected_channels)
