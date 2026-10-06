# -*- coding: utf-8 -*-
"""
[독립 레고 블록] Stock Omni Cardnews Pilot (📈 StockMaster AI 전용 쏘기 직전 5장 카드뉴스 제작 & Meta 단발 송출 파일럿)
=========================================================================================================================
- 브랜드: StockMaster AI (공식 검색어: '스톡마스터 AI' 띄어쓰기 불변)
- 핵심 원칙 (대표님 절대 수칙):
  1. [쏘기 전 무조건 먼저 생산]: 바탕화면 옛날 폴더 무단 주워오기 전면 배제!
     정시(스케줄) 도달 시, 이번 순번 주제(예: #1) 5장 카드뉴스 슬라이드를 쏘기 직전 단독 생산
  2. [즉시 1회 단발 발사]: 방금 생성된 5장 슬라이드를 넘겨받아 Meta 플랫폼 동시 송출
     - ① 페이스북 5장 카드뉴스 앨범 (Facebook Cardnews Album + 첫 댓글 스텔스 링크)
     - ② 인스타그램 캐러셀 피드 (Instagram Carousel 5장 피드)
  3. [완벽한 메타데이터 패키징]: 제목, 설명문, 첫댓글 링크 문구, 공식 검색어 유도, 4단 해시태그 100% 탑재
  4. [중복 방지 락(Lock)]: 당일 동일 주제 중복 송출 0% 원천 차단
"""

import os
import sys
import glob
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import BASE_DIR, get_now_kst_str
from brands.stock.stock_hashtag_matrix import StockHashtagMatrix
from brands.stock.stock_meta_publisher import StockMetaPublisher
from brands.stock.stock_mbs_reels_publisher import StockMBSReelsPublisher
from brands.stock.stock_youtube_bot_publisher import StockYouTubeBotPublisher
from brands.stock.stock_naver_clip_publisher import StockNaverClipPublisher

logger = logging.getLogger("StockOmniCardnewsPilot")


class StockOmniCardnewsPilot:
    """📈 StockMaster AI 전용 [쏘기 직전 5장 카드뉴스 제작 ➔ Meta 1회 단발 송출] 통합 관제 파일럿"""

    BRAND = "stock"
    OFFICIAL_KEYWORD = "스톡마스터 AI"
    LANDING_URL = "https://stockmaster-ai.vercel.app/"

    CARDNEWS_TOPICS = {
        1: "오늘 외인·기관이 쌍끌이 매수한 주도 섹터 TOP 4 분석",
        2: "20일선 돌파 & 거래량 폭증! 신고가 레이더 포착 종목 4선",
        3: "FOMC 금리 결정 후 코스피/코스닥 대응 전략 4대 핵심 포인트",
        4: "미국 배당 ETF(SCHD·JEPQ) 월 100만원 파이프라인 구축법",
        5: "저PBR 밸류업 프로그램 수혜 금융주 & 배당주 스크리닝",
        6: "AI 퀀트 적정주가 계산법: 감으로 사지 말고 데이터로 사라",
        7: "주린이 탈출: 손절매와 익절 구간 설정하는 절대 공식",
        8: "24시간 글로벌 시황 & 외신 속보 실시간 레이더 활용법"
    }

    def __init__(self):
        self.hashtag_matrix = StockHashtagMatrix()
        self.meta_pub = StockMetaPublisher()
        self.mbs_pub = StockMBSReelsPublisher()
        self.youtube_pub = StockYouTubeBotPublisher(headless=True)
        self.clip_pub = StockNaverClipPublisher()
        self.history_file = CURRENT_DIR / "omni_cardnews_publish_history.json"
        self.state_file = CURRENT_DIR / "omni_cardnews_schedule_state.json"

    def _load_state(self) -> Dict[str, Any]:
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"last_topic_id": 0, "published_today": []}

    def _save_state(self, state: Dict[str, Any]):
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"상태 저장 경고: {e}")

    def get_next_topic_id(self) -> int:
        """
        🔄 [8-Topic LRU Anti-Duplication Ring Buffer]
        - 최근 발행 이력(history)을 전수 역추적하여 가장 오랫동안 송출되지 않은 주제(LRU)를 자동 선정
        - 오늘 이미 송출된 주제는 최우선적으로 배제 (하루 3회 정시 슬롯 간 중복 0% 철통 보장)
        """
        all_topics = list(self.CARDNEWS_TOPICS.keys())
        today_str = datetime.now().strftime("%Y-%m-%d")

        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []

        today_published = {
            item.get("topic_id")
            for item in history
            if item.get("date") == today_str and item.get("status") == "success" and item.get("topic_id") is not None
        }

        last_seen = {}
        for idx, item in enumerate(reversed(history)):
            tid = item.get("topic_id")
            if tid in all_topics and item.get("status") == "success":
                if tid not in last_seen:
                    last_seen[tid] = idx

        for tid in all_topics:
            if tid not in last_seen:
                last_seen[tid] = 999999

        candidates = [tid for tid in all_topics if tid not in today_published]
        if not candidates:
            candidates = all_topics

        candidates.sort(key=lambda t: last_seen.get(t, 999999), reverse=True)
        chosen_id = candidates[0]

        state = self._load_state()
        state["last_topic_id"] = chosen_id
        self._save_state(state)

        logger.info(f"🔄 [주식 카드뉴스 LRU 자동 선정] 후보군 {candidates} ➔ 선정 주제: #{chosen_id} (오늘 송출완료: {today_published})")
        return chosen_id

    def is_already_published_today(self, topic_id: int) -> bool:
        """[중복 방지 락] 오늘 이미 해당 주제가 송출되었는지 점검"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
                    for item in history:
                        if item.get("date") == today_str and item.get("topic_id") == topic_id and item.get("status") == "success":
                            return True
            except Exception:
                pass
        return False

    def produce_fresh_cardnews(self, topic_id: int) -> List[str]:
        """
        🎨 [쏘기 직전 5장 카드뉴스 실시간 100% 신선 제작]
        - 옛날 파일 무단 주워오기 100% 전면 배제!
        """
        logger.info("=" * 70)
        logger.info(f"🎨 [주식 카드뉴스 실시간 제작] 쏘기 직전 주제 #{topic_id} 5장 신규 렌더링 시작...")
        logger.info("=" * 70)

        # 주식 카드뉴스 전용 실시간 생산 엔진 연동
        raise NotImplementedError(f"주식 카드뉴스 주제 #{topic_id} 실시간 렌더링 엔진 구축 준비 중 (과거 파일 무단 송출 원천 차단)")

    def build_meta_packages(self, topic_id: int) -> Dict[str, Any]:
        """[제미나이 100% 실시간 카피 + 실시간 급상승 트렌드 해시태그 융합] 5장 카드뉴스 및 4대 채널 포스팅 패키지"""
        main_title = self.CARDNEWS_TOPICS.get(topic_id, f"주식 퀀트 분석 카드뉴스 #{topic_id}")
        from core.gemini_domestic_sns_copywriter import GeminiDomesticSNSCopywriter
        copywriter = GeminiDomesticSNSCopywriter(brand="stock")
        pkg = copywriter.generate_full_package(topic_id=topic_id, topic_title=main_title, media_type="shorts")
        return {
            "title": main_title,
            "youtube": pkg.get("youtube", {}),
            "naver_clip": pkg.get("naver_clip", {}),
            "ig_caption": pkg.get("meta", {}).get("ig_caption", ""),
            "fb_caption": pkg.get("meta", {}).get("fb_caption", ""),
            "fb_comment": pkg.get("meta", {}).get("fb_comment", "")
        }

    def execute_single_slot(self, topic_id: Optional[int] = None, force: bool = False) -> Dict[str, Any]:
        """
        🚀 [정시 1회 단발 실행] 쏘기 직전 5장 제작 ➔ 4대 플랫폼 즉시 1회 발사 ➔ 중복 락
        """
        target_topic = topic_id or self.get_next_topic_id()
        today_str = datetime.now().strftime("%Y-%m-%d")

        if not force and self.is_already_published_today(target_topic):
            logger.info(f"🛑 [중복 방지 락] 주식 카드뉴스 주제 #{target_topic}은 오늘 이미 송출되었습니다. 스킵합니다.")
            return {"status": "skipped", "message": f"주제 #{target_topic} 오늘 송출 완료 상태"}

        try:
            slides = self.produce_fresh_cardnews(target_topic)
        except Exception as e:
            logger.error(f"❌ [주식 카드뉴스 제작 실패] {e}")
            return {"status": "error", "error": f"제작 실패: {e}"}

        # 🔍 [3단계: 파이썬 실물 전수 검증] "API로 쏘는 건 무조건 바탕화면에 제대로 완이 다 만들고 파이썬 확인 그 다음에 API"
        from brands.stock.stock_production_safety_gate import StockProductionSafetyGate
        is_valid, verify_msg = StockProductionSafetyGate.verify_desktop_cardnews_completed(slides)
        if not is_valid:
            logger.critical(f"🛑 [파이썬 완제품 검증 탈락] 바탕화면 카드뉴스 실물 검증 실패: {verify_msg} -> 외부 API(Meta) 송출 원천 차단!")
            return {"status": "verification_failed", "error": f"바탕화면 실물 검증 실패: {verify_msg}"}
        logger.info(f"✅ [3단계 파이썬 완제품 검증 100% 합격] {verify_msg} -> 4단계 외부 4대 플랫폼 발사(쏘기) 개시!")

        # 4. 메타데이터 패키징 & 외부 API 발사
        pkg = self.build_meta_packages(target_topic)
        results = {
            "status": "success",
            "date": today_str,
            "published_at": get_now_kst_str(),
            "brand": self.BRAND,
            "topic_id": target_topic,
            "title": pkg["title"],
            "slides_count": len(slides),
            "channels": {}
        }

        # 🛑 [대표님 긴급 수칙] 외부 API 송출 차단 모드 검사
        dispatch_allowed, dispatch_msg = StockProductionSafetyGate.is_api_dispatch_allowed()
        if not dispatch_allowed:
            logger.warning(f"{dispatch_msg} (주제 #{target_topic} 바탕화면 실물 {len(slides)}장 보관 완료)")
            results["channels"] = {"all_channels": {"status": "blocked", "message": dispatch_msg}}
            self.save_publish_history(results)
            return results

        # 4-1. 카드뉴스 슬라이드 ➔ 15.5초 세로 릴스/숏폼 MP4 자동 변환
        cardnews_reels_path = None
        try:
            from core.cardnews_to_reels_converter import CardnewsToReelsConverter
            converter = CardnewsToReelsConverter()
            slide_dir = Path(slides[0]).parent if slides else CURRENT_DIR
            out_reels = str(slide_dir / f"stock_topic{target_topic}_cardnews_reels.mp4")
            conv_res = converter.convert(slide_paths=slides, output_path=out_reels, brand="stock")
            if conv_res.get("status") == "success":
                cardnews_reels_path = out_reels
                logger.info(f"🎬 [CardnewsToReels 완료] 릴스 변환 성공: {out_reels}")
            else:
                logger.warning(f"⚠️ [CardnewsToReels 경고] 릴스 변환 실패: {conv_res.get('message')}")
        except Exception as ce:
            logger.error(f"❌ [CardnewsToReels 예외] {ce}")

        # 4-2. [Channel 1 & 2] Meta 릴스 (인스타그램 + 페이스북 릴스)
        if self.mbs_pub.is_available() and cardnews_reels_path and os.path.exists(cardnews_reels_path):
            logger.info(f"🌐 [Meta Business Suite] 주식 AI 카드뉴스 릴스({os.path.basename(cardnews_reels_path)}) 인스타+페북 웹 무인 발행 개시...")
            try:
                mbs_res = self.mbs_pub.publish_reel(
                    video_path=cardnews_reels_path,
                    caption=pkg["ig_caption"]
                )
                results["channels"]["meta_business_suite_reels"] = mbs_res
                logger.info(f"🎉 [MBS 릴스 발행 완료]: {mbs_res.get('status')}")
            except Exception as mbse:
                logger.error(f"❌ [MBS 릴스 발행 예외] {mbse}")
                results["channels"]["meta_business_suite_reels"] = {"status": "error", "error": str(mbse)}

        # 4-3. [Channel 2-1] 페이스북 5장 카드뉴스 앨범 피드 송출
        if self.meta_pub.is_available():
            logger.info(f"📘 [Meta Graph API] 페이스북 5장 카드뉴스 앨범 송출...")
            try:
                fb_res = self.meta_pub.publish_facebook_cardnews_album(
                    image_paths=slides,
                    caption=pkg["fb_caption"],
                    first_comment=pkg["fb_comment"]
                )
                results["channels"]["facebook_cardnews"] = fb_res
            except Exception as fbe:
                results["channels"]["facebook_cardnews"] = {"status": "error", "error": str(fbe)}

        # 4-4. [Channel 3] 유튜브 쇼츠에 카드뉴스 릴스 영상 송출
        if cardnews_reels_path and os.path.exists(cardnews_reels_path) and self.youtube_pub.is_available():
            logger.info(f"🔴 [3/4 유튜브 쇼츠 카드뉴스 릴스 송출] 주제 #{target_topic} 발사...")
            try:
                yt_title = pkg.get("youtube", {}).get("title") or f"{pkg['title']} #Shorts"
                yt_res = self.youtube_pub.publish_short(
                    video_path=cardnews_reels_path,
                    topic_id=target_topic,
                    title=yt_title,
                    description=pkg.get("youtube", {}).get("desc"),
                    privacy_status="public"
                )
                results["channels"]["youtube_shorts"] = yt_res
            except Exception as ye:
                logger.error(f"❌ 유튜브 카드뉴스 숏츠 송출 실패: {ye}")
                results["channels"]["youtube_shorts"] = {"status": "error", "error": str(ye)}

        # 4-5. [Channel 4] 네이버 클립에 카드뉴스 릴스 영상 송출
        if cardnews_reels_path and os.path.exists(cardnews_reels_path) and self.clip_pub.is_available():
            logger.info(f"🟢 [4/4 네이버 클립 카드뉴스 릴스 송출] 주제 #{target_topic} 발사...")
            try:
                clip_title = pkg.get("naver_clip", {}).get("title") or pkg["title"]
                clip_res = self.clip_pub.publish_clip(
                    video_path=cardnews_reels_path,
                    topic_id=target_topic,
                    title=clip_title,
                    description=pkg.get("naver_clip", {}).get("desc")
                )
                results["channels"]["naver_clip"] = clip_res
            except Exception as ce:
                logger.error(f"❌ 네이버 클립 카드뉴스 숏츠 송출 실패: {ce}")
                results["channels"]["naver_clip"] = {"status": "error", "error": str(ce)}

        self._record_history(results)
        logger.info("=" * 70)
        logger.info(f"🎉 [주식 5장 카드뉴스 1회 단발 송출 완료] 주제 #{target_topic} | 슬라이드 {len(slides)}장")
        logger.info("=" * 70)
        return results

    def _record_history(self, record: Dict[str, Any]):
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                pass
        history.append(record)
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history[-50:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    pilot = StockOmniCardnewsPilot()
    print(f"📈 Stock Omni Cardnews Pilot 준비 완료! (다음 롤링 주제: #{pilot.get_next_topic_id()})")
