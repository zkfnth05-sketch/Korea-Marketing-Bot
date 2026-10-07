"""
Stock Master Independent Pipeline (StockMaster AI 독립 전담 마케팅 파이프라인)
========================================================================
- 브랜드: 📈 StockMaster AI
- 공식 검색어: '스톡마스터 AI' (띄어쓰기 필수)
- 랜딩 URL: https://stockmaster-ai.vercel.app/
- 규칙:
  1. 쏘기 전 즉시 1편 생산 -> 1회 단발 발송 (중복 도배 전면 차단)
  2. 숏폼: 실시간 퀀트 30초 숏폼 렌더링 -> 유튜브 Shorts + 네이버 클립(공개) + 인스타 Reels + 페북 Reels
  3. 카드뉴스: 페북 앨범(첫댓글 링크) + 인스타 캐러셀(4단 해시태그)
  4. 휴먼비헤이비어: 네이버 블로그/카페 4회 정시 웜업 (제미나이 0회)
  5. 카페: 순수 파이썬 100% 필터링 + 제미나이 1일 1회 침투
  6. 24시간 365일 무인 자율 구동 데몬 지원
"""

import os
import sys
import json
import time
import argparse
import logging
import asyncio
import threading
from typing import Dict, Any, Optional

# Root path alignment
current_dir = os.path.dirname(os.path.abspath(__file__))
engine_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if engine_root not in sys.path:
    sys.path.insert(0, engine_root)

from brands.stock.stock_omni_shorts_pilot import StockOmniShortsPilot
from brands.stock.stock_omni_cardnews_pilot import StockOmniCardnewsPilot
from brands.stock.stock_human_behavior_bot import StockHumanBehaviorBot
from brands.stock.stock_cafe_pipeline import StockCafePipeline
from brands.stock.stock_kin_pipeline import StockKinPipeline
from brands.stock.stock_blog_scheduler import StockBlogScheduler
from brands.stock.stock_text_thread_hub import StockTextThreadHub
from brands.stock.stock_search_indexing_hub import StockSearchIndexingHub
from core.verification.live_proof_verifier import live_proof_verifier
from config import get_now_kst, get_now_kst_str

logger = logging.getLogger("StockPipeline")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class StockPipeline:
    BRAND = "stock"
    NAME = "StockMaster AI"
    KEYWORD = "스톡마스터 AI"
    URL = "https://stockmaster-ai.vercel.app/"

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.shorts_pilot = StockOmniShortsPilot()
        self.cardnews_pilot = StockOmniCardnewsPilot()
        self.human_bot = StockHumanBehaviorBot()
        self.cafe_pipe = StockCafePipeline()
        self.kin_pipe = StockKinPipeline()
        self.blog_scheduler = StockBlogScheduler()
        self.thread_hub = StockTextThreadHub()
        self.seo_hub = StockSearchIndexingHub()
        self.proof_verifier = live_proof_verifier

    # 1. 숏폼 파이프라인 (쏘기 전 1편 신규 생산 -> 4대 플랫폼 1회 단발 발송 + 실시간 증빙)
    def run_shorts(self, topic_id: Optional[int] = None, force: bool = False) -> Dict[str, Any]:
        logger.info(f"🎬 [{self.NAME}] 숏폼 파이프라인 가동: 쏘기 직전 실시간 퀀트 30초 숏폼 제작 및 4대 채널(유튜브+클립+릴스) 단발 송출")
        try:
            if force:
                today_str = get_now_kst().strftime("%Y-%m-%d")
                self.shorts_pilot.published_records = [
                    r for r in self.shorts_pilot.published_records if r.get("date") != today_str
                ]
            res = self.shorts_pilot.execute_single_slot(topic_id=topic_id, force=force)
            if res.get("success") or res.get("youtube_url") or res.get("instagram_url"):
                live_url = res.get("youtube_url") or res.get("instagram_url") or self.URL
                self.proof_verifier.record_and_capture_proof(
                    brand=self.BRAND, channel="youtube", live_url=live_url, title=f"StockMaster 숏폼 주제 {topic_id or 1}", take_screenshot=True
                )
            else:
                self.proof_verifier.record_failure(
                    brand=self.BRAND, channel="youtube", error_message=res.get("error") or "쇼츠 렌더링/업로드 실패", title=f"StockMaster 숏폼 주제 {topic_id or 1}"
                )
            return res
        except Exception as e:
            self.proof_verifier.record_failure(
                brand=self.BRAND, channel="youtube", error_message=str(e), title=f"StockMaster 숏폼 주제 {topic_id or 1}"
            )
            raise

    # 2. 카드뉴스 파이프라인 (쏘기 전 5장 신규 렌더링 -> 2대 플랫폼 1회 단발 발송 + 실시간 증빙)
    def run_cardnews(self, topic_id: Optional[int] = None, force: bool = False) -> Dict[str, Any]:
        logger.info(f"🎨 [{self.NAME}] 카드뉴스 파이프라인 가동: 쏘기 직전 5장 신규 제작 및 Meta(페북+인스타) 단발 송출")
        try:
            if force:
                today_str = get_now_kst().strftime("%Y-%m-%d")
                self.cardnews_pilot.published_records = [
                    r for r in self.cardnews_pilot.published_records if r.get("date") != today_str
                ]
            res = self.cardnews_pilot.execute_single_slot(topic_id=topic_id, force=force)
            if res.get("success") or res.get("instagram_url") or res.get("facebook_url"):
                live_url = res.get("instagram_url") or res.get("facebook_url") or "https://www.instagram.com/stockmaster_ai"
                self.proof_verifier.record_and_capture_proof(
                    brand=self.BRAND, channel="instagram", live_url=live_url, title=f"StockMaster 카드뉴스 주제 {topic_id or 1}", take_screenshot=True
                )
            else:
                self.proof_verifier.record_failure(
                    brand=self.BRAND, channel="instagram", error_message=res.get("error") or "카드뉴스 렌더링/발행 실패", title=f"StockMaster 카드뉴스 주제 {topic_id or 1}"
                )
            return res
        except Exception as e:
            self.proof_verifier.record_failure(
                brand=self.BRAND, channel="instagram", error_message=str(e), title=f"StockMaster 카드뉴스 주제 {topic_id or 1}"
            )
            raise

    # 3. 휴먼비헤이비어 봇 파이프라인 (네이버 블로그/카페 웜업)
    def run_human_behavior(self, mode: str = "once") -> Dict[str, Any]:
        logger.info(f"🤖 [{self.NAME}] 네이버 휴먼비헤이비어 가동 (모드: {mode})")
        if mode == "daemon":
            self.human_bot.run_daemon(check_interval_seconds=30)
            return {"status": "daemon_running"}
        else:
            return self.human_bot.perform_routine()

    # 4. 네이버 카페 스텔스 침투 파이프라인 (+ 실시간 증빙)
    def run_cafe(self) -> Dict[str, Any]:
        logger.info(f"☕ [{self.NAME}] 네이버 카페 스텔스 침투 파이프라인 가동")
        try:
            res = asyncio.run(self.cafe_pipe.run_daily_stealth_infiltration(dry_run=self.dry_run))
            if res.get("status") in ["SUCCESS", "SUCCESS_WAIT", "COMPLETED"] or res.get("article_url"):
                live_url = res.get("article_url") or res.get("cafe_url") or "https://cafe.naver.com/"
                self.proof_verifier.record_and_capture_proof(
                    brand=self.BRAND, channel="naver_cafe", live_url=live_url, title="StockMaster 카페 댓글 침투", take_screenshot=True
                )
            else:
                self.proof_verifier.record_failure(
                    brand=self.BRAND, channel="naver_cafe", error_message=res.get("message") or res.get("error") or "카페 탐색/댓글 침투 조건 미충족", title="StockMaster 카페 댓글 침투"
                )
            return res
        except Exception as e:
            self.proof_verifier.record_failure(
                brand=self.BRAND, channel="naver_cafe", error_message=str(e), title="StockMaster 카페 댓글 침투"
            )
            raise

    # 5. 네이버 지식iN 파이프라인 (+ 실시간 증빙)
    def run_kin(self) -> Dict[str, Any]:
        logger.info(f"🎯 [{self.NAME}] 네이버 지식iN 실시간 낚아채기 파이프라인 가동")
        try:
            res = self.kin_pipe.run_catch_cycle(max_catch=1, dry_run=self.dry_run)
            if res.get("success") or res.get("kin_url") or res.get("url"):
                live_url = res.get("kin_url") or res.get("url") or "https://kin.naver.com/"
                self.proof_verifier.record_and_capture_proof(
                    brand=self.BRAND, channel="naver_kin", live_url=live_url, title="StockMaster 지식iN 실시간 답변", take_screenshot=True
                )
            else:
                self.proof_verifier.record_failure(
                    brand=self.BRAND, channel="naver_kin", error_message=res.get("message") or res.get("error") or "지식iN 타겟 질문 탐색 대기", title="StockMaster 지식iN 실시간 답변"
                )
            return res
        except Exception as e:
            self.proof_verifier.record_failure(
                brand=self.BRAND, channel="naver_kin", error_message=str(e), title="StockMaster 지식iN 실시간 답변"
            )
            raise

    # 6. 블로그/시황 파이프라인 (+ 실시간 증빙)
    def run_blog(self) -> Dict[str, Any]:
        logger.info(f"✍️ [{self.NAME}] 4대 옴니 블로그/시황 파이프라인 가동")
        try:
            res = self.blog_scheduler.run_one_cycle()
            nb = res.get("publish_results", {}).get("channels", {}).get("naver_blog", {})
            if nb.get("success") or res.get("blog_url") or res.get("url"):
                live_url = nb.get("url") or res.get("blog_url") or res.get("url") or "https://blog.naver.com/stockmaster_ai"
                self.proof_verifier.record_and_capture_proof(
                    brand=self.BRAND, channel="naver_blog", live_url=live_url, title="StockMaster 퀀트 시황 발행", take_screenshot=True
                )
            else:
                self.proof_verifier.record_failure(
                    brand=self.BRAND, channel="naver_blog", error_message=nb.get("error") or res.get("message") or "블로그 발행 실패", title="StockMaster 퀀트 시황 발행"
                )
            return res
        except Exception as e:
            self.proof_verifier.record_failure(
                brand=self.BRAND, channel="naver_blog", error_message=str(e), title="StockMaster 퀀트 시황 발행"
            )
            raise

    # 7. 텍스트 스토리 타래 (+ 실시간 증빙)
    def run_threads(self) -> Dict[str, Any]:
        logger.info(f"🧵 [{self.NAME}] 텍스트 타래 배포 파이프라인 가동")
        try:
            res = self.thread_hub.publish_omni_thread()
            if res.get("success") or res.get("thread_url"):
                live_url = res.get("thread_url") or res.get("url") or "https://threads.net/@stockmaster_ai"
                self.proof_verifier.record_and_capture_proof(
                    brand=self.BRAND, channel="threads", live_url=live_url, title="StockMaster 스레드 옴니 타래", take_screenshot=True
                )
            else:
                self.proof_verifier.record_failure(
                    brand=self.BRAND, channel="threads", error_message=res.get("error") or res.get("message") or "스레드 타래 배포 실패", title="StockMaster 스레드 옴니 타래"
                )
            return res
        except Exception as e:
            self.proof_verifier.record_failure(
                brand=self.BRAND, channel="threads", error_message=str(e), title="StockMaster 스레드 옴니 타래"
            )
            raise

    # 8. 검색엔진 색인 핑 (+ 실시간 증빙)
    def run_seo(self) -> Dict[str, Any]:
        logger.info(f"🌐 [{self.NAME}] 검색엔진 색인 핑 파이프라인 가동")
        try:
            res = self.seo_hub.ping_all_engines()
            if res.get("success"):
                self.proof_verifier.record_and_capture_proof(
                    brand=self.BRAND, channel="indexing_ping", live_url=self.URL, title="StockMaster 네이버/구글 검색 색인핑 200 OK", take_screenshot=False
                )
            else:
                self.proof_verifier.record_failure(
                    brand=self.BRAND, channel="indexing_ping", error_message=res.get("message") or "검색 색인 핑 전송 실패", title="StockMaster 검색 색인핑"
                )
            return res
        except Exception as e:
            self.proof_verifier.record_failure(
                brand=self.BRAND, channel="indexing_ping", error_message=str(e), title="StockMaster 검색 색인핑"
            )
            raise

    # 9. 레딧 글로벌 투자자 2단계 족집게 스텔스 침투 (+ 실시간 증빙)
    def run_reddit(self, mode: str = "promo") -> Dict[str, Any]:
        logger.info(f"🤖 [{self.NAME}] Reddit 글로벌 투자자 스텔스 침투 파이프라인 가동 (모드: {mode})")
        try:
            from brands.stock.stock_reddit_engine import StockRedditEngine
            engine = StockRedditEngine()
            if mode == "cycle":
                res = engine.run_safe_cycle()
                self.proof_verifier.record_and_capture_proof(
                    brand=self.BRAND, channel="reddit", live_url="https://www.reddit.com/r/stocks/", title="StockMaster Reddit 안전 사이클", take_screenshot=False
                )
                return res
            else:
                count = engine.scan_and_reply(limit_per_sub=10, max_promo=1, auto_post=True)
                if count > 0:
                    self.proof_verifier.record_and_capture_proof(
                        brand=self.BRAND, channel="reddit", live_url="https://www.reddit.com/r/investing/", title="StockMaster Reddit 스텔스 댓글 침투", take_screenshot=False
                    )
                else:
                    self.proof_verifier.record_failure(
                        brand=self.BRAND, channel="reddit", error_message="타겟 주식 글 탐색 중 또는 쿨다운 대기", title="StockMaster Reddit 스텔스 침투"
                    )
                return {"status": "success", "processed_count": count}
        except Exception as e:
            self.proof_verifier.record_failure(
                brand=self.BRAND, channel="reddit", error_message=str(e), title="StockMaster Reddit 스텔스 침투"
            )
            raise

    # 통합 동적 채널 라우터
    def run_channel(self, channel_name: str, **kwargs) -> Dict[str, Any]:
        c = channel_name.lower().strip()
        if c in ["shorts", "youtube", "naver_clip", "reels"]:
            return self.run_shorts(**kwargs)
        elif c in ["cardnews", "meta", "instagram", "facebook"]:
            return self.run_cardnews(**kwargs)
        elif c in ["human", "behavior", "warmup"]:
            return self.run_human_behavior(**kwargs)
        elif c in ["cafe", "naver_cafe"]:
            return self.run_cafe()
        elif c in ["kin", "naver_kin", "qna"]:
            return self.run_kin()
        elif c in ["blog", "briefing", "tistory"]:
            return self.run_blog()
        elif c in ["threads", "story"]:
            return self.run_threads()
        elif c in ["seo", "advisor", "ping"]:
            return self.run_seo()
        elif c in ["reddit", "reddit_promo", "reddit_cycle"]:
            mode = "cycle" if "cycle" in c else "promo"
            return self.run_reddit(mode=mode)
        else:
            raise ValueError(f"알 수 없는 채널: {channel_name}")

    # 전 채널 1회 종합 순차 검증
    def run_full_cycle(self) -> Dict[str, Any]:
        logger.info("=" * 60)
        logger.info(f"🚀 [{self.NAME}] 전 채널 독립 파이프라인 종합 1회 가동 시작")
        logger.info("=" * 60)

        results = {}
        try:
            results["human"] = self.run_human_behavior(mode="once")
        except Exception as e:
            results["human"] = {"error": str(e)}

        try:
            results["cardnews"] = self.run_cardnews()
        except Exception as e:
            results["cardnews"] = {"error": str(e)}

        try:
            results["shorts"] = self.run_shorts()
        except Exception as e:
            results["shorts"] = {"error": str(e)}

        try:
            results["kin"] = self.run_kin()
        except Exception as e:
            results["kin"] = {"error": str(e)}

    def run_full_daily_cycle(self) -> Dict[str, Any]:
        """일일 전 채널 순차 사이클 실행 (하위 호환 및 스케줄러 공식 표준)"""
        return self.run_full_cycle()

    def run_community_cycle(self) -> Dict[str, Any]:
        """디시인사이드 주식갤 & 뽐뿌 증권포럼 시황 브리핑 투고 사이클"""
        from brands.stock.scenarios.prompt_director_stock import StockPromptDirector
        from modules.domestic.ppomppu_engine import PpomppuEngine
        from modules.domestic.dcinside_engine import DCInsideEngine

        director = StockPromptDirector()
        p_data = director.generate_ppomppu_post()
        dc_data = director.generate_dcinside_post()

        res_p = PpomppuEngine().post_article(
            board_id=p_data.get("board", "stock"),
            title=p_data.get("title", ""),
            content=p_data.get("content", ""),
            dry_run=self.dry_run
        )
        res_dc = DCInsideEngine().post_article(
            gallery_id=dc_data.get("gallery", "neostock"),
            title=dc_data.get("title", ""),
            content_html=dc_data.get("content", ""),
            dry_run=self.dry_run
        )
        return {
            "status": "success",
            "ppomppu": res_p,
            "dcinside": res_dc
        }

    def run_premarket_briefing_cycle(self) -> Dict[str, Any]:
        """장전 08:30 핵심 섹터 알림톡/텔레그램 브리핑 발송"""
        from brands.stock.stock_telegram_engine import StockTelegramEngine
        engine = StockTelegramEngine()
        return engine.broadcast_briefing()

    # 24시간 365일 무인 자율 구동 데몬
    def run_daemon(self):
        logger.info("=" * 60)
        logger.info(f"🤖 [{self.NAME}] 24시간 365일 무인 자율 백그라운드 데몬 가동")
        logger.info(f"   • 공식 검색어: '{self.KEYWORD}'")
        logger.info(f"   • ☀️ 오전 08:30: 동영상 숏츠 ① (4대 플랫폼: 유튜브+클립+인스타+페북)")
        logger.info(f"   • 🍱 오후 12:30: 카드뉴스형 콘텐츠 (4대 플랫폼: 유튜브+클립+인스타+페북)")
        logger.info(f"   • 🌙 저녁 19:30: 동영상 숏츠 ② (4대 플랫폼: 유튜브+클립+인스타+페북)")
        logger.info(f"   • ✍️ 블로그: 10:00 / 15:00 / 20:00 KST")
        logger.info(f"   • 🤖 휴먼 웜업: 08:30 / 12:30 / 15:30 / 21:30 KST")
        logger.info("=" * 60)

        # 1. 휴먼 비헤이비어 백그라운드 스레드
        t_human = threading.Thread(target=self.run_human_behavior, kwargs={"mode": "daemon"}, daemon=True)
        t_human.start()

        executed_slots = set()

        while True:
            try:
                now = get_now_kst()
                today_str = now.strftime("%Y-%m-%d")
                hour = now.hour
                minute = now.minute

                # 1차 동영상 숏츠 슬롯 (08:30 KST)
                if hour == 8 and minute == 30:
                    slot_key = f"{today_str}_shorts_0830"
                    if slot_key not in executed_slots:
                        executed_slots.add(slot_key)
                        logger.info(f"⏰ [{self.NAME}] ☀️ 출근길(08:30) 동영상 숏츠 ① 4대 플랫폼 정시 송출 시작...")
                        self.run_shorts()

                # 2차 카드뉴스형 슬롯 (12:30 KST)
                if hour == 12 and minute == 30:
                    slot_key = f"{today_str}_cardnews_1230"
                    if slot_key not in executed_slots:
                        executed_slots.add(slot_key)
                        logger.info(f"⏰ [{self.NAME}] 🍱 점심시간(12:30) 카드뉴스형 콘텐츠 4대 플랫폼 정시 송출 시작...")
                        self.run_cardnews()

                # 3차 동영상 숏츠 슬롯 (19:30 KST)
                if hour == 19 and minute == 30:
                    slot_key = f"{today_str}_shorts_1930"
                    if slot_key not in executed_slots:
                        executed_slots.add(slot_key)
                        logger.info(f"⏰ [{self.NAME}] 🌙 저녁 골든타임(19:30) 동영상 숏츠 ② 4대 플랫폼 정시 송출 시작...")
                        self.run_shorts()

                # 블로그 슬롯 (하루 3회: 10:00, 15:00, 20:00 KST)
                if minute == 0 and hour in [10, 15, 20]:
                    slot_key = f"{today_str}_blog_{hour}00"
                    if slot_key not in executed_slots:
                        executed_slots.add(slot_key)
                        logger.info(f"⏰ [{self.NAME}] {hour}:00 블로그 정시 배포 시작...")
                        self.run_blog()

                # 지식iN 1일 10건 실시간 체크 (매 30분)
                if minute in [20, 50]:
                    slot_key = f"{today_str}_kin_{hour}_{minute}"
                    if slot_key not in executed_slots:
                        executed_slots.add(slot_key)
                        self.run_kin()

                time.sleep(30)
            except Exception as e:
                logger.error(f"❌ [{self.NAME} 데몬 오류] {e}")
                time.sleep(60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="StockMaster AI 독립 마케팅 파이프라인")
    parser.add_argument("--channel", choices=["shorts", "cardnews", "human", "cafe", "kin", "blog", "threads", "seo", "all"], help="실행할 채널")
    parser.add_argument("--topic", type=int, default=None, help="지정할 주제 번호")
    parser.add_argument("--force", action="store_true", help="중복 발송 락 무시하고 강제 실행")
    parser.add_argument("--daemon", action="store_true", help="24시간 무인 자율 데몬 모드로 상주 실행")

    args = parser.parse_args()
    pipeline = StockPipeline(dry_run=False)

    if args.daemon:
        pipeline.run_daemon()
    elif args.channel == "all":
        res = pipeline.run_full_cycle()
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif args.channel:
        res = pipeline.run_channel(args.channel, topic_id=args.topic, force=args.force)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        parser.print_help()
