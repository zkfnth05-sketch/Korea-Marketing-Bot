# -*- coding: utf-8 -*-
"""
StockMetaScheduler - 📈 [StockMaster AI 전용 하루 2회 인스타+페북 카드뉴스 무인 자동화 스케줄러]
=============================================================================================
• 원칙 준수:
  - Rule 1 (완전 독립 레고 블록: brands/stock/ 전담)
  - Rule 6 (24시간 365일 100% 무인 자율 구동 상주 데몬)
  - Rule 7 (공식 검색어 '스톡마스터 AI' 띄어쓰기 + 공식 랜딩 URL)
• 스케줄 (대한민국 KST 기준 하루 2회 골든타임):
  - 1회차: 08:30 (장 시작 전 당일 주도 섹터 수급 레이더 & 모닝 브리핑)
  - 2회차: 16:00 (장 마감 후 외국인·기관 쌍끌이 매수 결산 & AI 퀀트 분석)
• 동작:
  - 8대 주식 퀀트 주제 자동 순환 (data/stock_meta_rotation_state.json)
  - 4단 티어 해시태그 매트릭스(StockHashtagMatrix) 자동 주입
  - 정품 카드뉴스 앨범 페이스북 페이지 및 인스타그램 피드 100% 무인 발행
"""

import os
import sys
import time
import json
import logging
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("StockMetaScheduler")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = DATA_DIR / "stock_meta_rotation_state.json"

DESKTOP_CARDNEWS_DIR = Path(r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\Stock")
DESKTOP_SHORTS_DIR = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Stock")

# 하루 2회 골든타임 (KST 기준): 08시 30분, 16시 00분
GOLDEN_TIMES = [
    {"hour": 8, "minute": 30, "label": "장전 모닝 브리핑 피크"},
    {"hour": 16, "minute": 0, "label": "장마감 퀀트 분석 피크"}
]

import glob
from brands.stock.stock_meta_publisher import StockMetaPublisher
from brands.stock.stock_hashtag_matrix import StockHashtagMatrix


class StockMetaScheduler:
    """📈 StockMaster AI 하루 2회 메타(인스타+페북) 무인 자율 스케줄러"""

    BRAND = "stock"
    OFFICIAL_KEYWORD = "스톡마스터 AI"
    LANDING_URL = "https://stockmaster-ai.vercel.app/"

    TOPICS = [
        {"topic_id": 1, "theme_name": "삼성전자 vs SK하이닉스 HBM 수급 대결"},
        {"topic_id": 2, "theme_name": "국내 고배당주(금융지주·맥쿼리) 월배당 시뮬레이션"},
        {"topic_id": 3, "theme_name": "코스피·코스닥 세력 체결강도 120% 돌파 유망주"},
        {"topic_id": 4, "theme_name": "밸류업 프로그램 저PBR 고배당 금융주"},
        {"topic_id": 5, "theme_name": "직장인 뇌동매매 방지 AI 손절매 & 리스크 가드"},
        {"topic_id": 6, "theme_name": "코스피200 우량주 vs 코스닥 성장주 직장인 월적립식 복리"},
        {"topic_id": 7, "theme_name": "외국인·기관 쌍끌이 순매수 실시간 레이더"},
        {"topic_id": 8, "theme_name": "초보 탈출! 원클릭 AI 종목 재무 건전성 진단"}
    ]

    def __init__(self):
        self.publisher = StockMetaPublisher()
        self.hashtag_matrix = StockHashtagMatrix()
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️ 상태 파일 파싱 실패, 초기화: {e}")

        initial_state = {
            "current_topic_index": 0,
            "last_topic_id": 0,
            "last_run_time": "",
            "published_count": 0,
            "history": []
        }
        self._save_state(initial_state)
        return initial_state

    def _save_state(self, state: Dict[str, Any]):
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ 상태 저장 실패: {e}")

    def find_desktop_cardnews(self, topic_id: int) -> List[str]:
        if not DESKTOP_CARDNEWS_DIR.exists():
            return []
        pattern = str(DESKTOP_CARDNEWS_DIR / f"**/*주제{topic_id:02d}*")
        matched = sorted(glob.glob(pattern, recursive=True))
        for d in reversed(matched):
            if os.path.isdir(d):
                slides = sorted(glob.glob(os.path.join(d, "slide_*.png")))
                if len(slides) >= 4:
                    return slides
        return []

    def find_desktop_shorts(self, topic_id: int) -> Optional[str]:
        if not DESKTOP_SHORTS_DIR.exists():
            return None
        pattern = str(DESKTOP_SHORTS_DIR / f"**/*주제{topic_id:02d}*.mp4")
        matched = glob.glob(pattern, recursive=True)
        final_clips = [m for m in matched if ("30초" in m or "완성" in m or "25초" in m) and os.path.getsize(m) > 2000000]
        if final_clips:
            return final_clips[0]
        elif matched:
            return matched[0]
        return None

    def run_one_cycle(self, force_topic_id: Optional[int] = None, mode: str = "all") -> Dict[str, Any]:
        """🚀 1회 메타 카드뉴스 & 숏폼 무인 자동 배포 사이클 실행"""
        total_topics = len(self.TOPICS)

        if force_topic_id is not None:
            topic_id = force_topic_id
            topic_info = next((t for t in self.TOPICS if t["topic_id"] == topic_id), self.TOPICS[0])
        else:
            idx = self.state.get("current_topic_index", 0) % total_topics
            topic_info = self.TOPICS[idx]
            topic_id = topic_info["topic_id"]

        theme_name = topic_info.get("theme_name", "주식 퀀트 분석")
        logger.info(f"📈 [StockMetaScheduler] 주제 #{topic_id} [{theme_name}] 배포 시작")

        slide_paths = self.find_desktop_cardnews(topic_id)
        shorts_path = self.find_desktop_shorts(topic_id)

        # 🚀 [코드 분리 원칙] 인간 행동(체류/좋아요)은 StockHumanBehaviorBot이 하루 30분 정시 전담!
        # API 송출 봇은 0.1초 고속 정시 배포만 깔끔하게 실행합니다.
        insta_tags = " ".join(self.hashtag_matrix.get_instagram_hashtags(topic_id=topic_id, count=18))
        fb_tags = " ".join(self.hashtag_matrix.get_facebook_hashtags(topic_id=topic_id, count=6))

        results = {}

        # 페이스북 공식 캡션 조립
        fb_caption = (
            f"📈 [StockMaster AI] {theme_name} 📊\n\n"
            f"복잡한 재무제표와 실시간 수급을 AI 퀀트 엔진으로 한눈에!\n"
            f"외국인·기관 쌍끌이 매수 포착부터 적정주가 산출까지 스마트한 데이터 투자를 시작하세요.\n\n"
            f"🔍 네이버 검색창에 👉 [ {self.OFFICIAL_KEYWORD} ] 검색해보세요!\n"
            f"👉 공식 분석: {self.LANDING_URL}\n\n"
            f"{fb_tags}"
        )

        ig_caption = (
            f"📈 [StockMaster AI] {theme_name}\n\n"
            f"네이버 검색창에 👉 [ {self.OFFICIAL_KEYWORD} ] 검색해보세요!\n"
            f"프로필 링크에서 실시간 퀀트 적정주가 무료 진단 ✨\n\n"
            f"{insta_tags}"
        )

        if mode in ["cardnews", "all"]:
            if slide_paths:
                results["facebook_cardnews"] = self.publisher.publish_facebook_cardnews_album(slide_paths, fb_caption)
                results["instagram_carousel"] = self.publisher.publish_instagram_carousel(slide_paths, ig_caption)
            else:
                sample_img_url = "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1080"
                results["facebook_photo"] = self.publisher.publish_facebook_photo(sample_img_url, fb_caption)
                results["instagram_feed"] = self.publisher.publish_instagram_photo(sample_img_url, ig_caption)

        if mode in ["shorts", "all"] and shorts_path and os.path.exists(shorts_path):
            video_title = f"[StockMaster] {theme_name}"
            video_desc = (
                f"📈 [StockMaster AI] {theme_name} 📊\n\n"
                f"🔍 네이버 검색창에 👉 [ {self.OFFICIAL_KEYWORD} ] 검색해보세요!\n"
                f"👉 공식 분석: {self.LANDING_URL}\n\n"
                f"{fb_tags}"
            )
            results["facebook_video"] = self.publisher.publish_facebook_video(shorts_path, video_title, video_desc)
            results["instagram_reels"] = self.publisher.publish_instagram_reels(shorts_path, ig_caption)

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 상태 갱신
        if force_topic_id is None:
            self.state["current_topic_index"] = (self.state.get("current_topic_index", 0) + 1) % total_topics
        self.state["last_topic_id"] = topic_id
        self.state["last_run_time"] = now_str
        self.state["published_count"] = self.state.get("published_count", 0) + 1

        log_entry = {
            "timestamp": now_str,
            "topic_id": topic_id,
            "theme_name": theme_name,
            "results": results
        }
        self.state.setdefault("history", []).append(log_entry)
        if len(self.state["history"]) > 50:
            self.state["history"] = self.state["history"][-50:]
        self._save_state(self.state)

        logger.info(f"🎉 [StockMetaScheduler] 주제 #{topic_id} 배포 완료! (누적: {self.state['published_count']}회)")
        return log_entry

    def start_daemon(self, check_interval_seconds: int = 60):
        """24시간 365일 백그라운드 상주 데몬 (하루 2회 정시 기상/배포)"""
        logger.info("=" * 65)
        logger.info("🤖 [StockMaster AI] 하루 2회 메타(인스타+페북) 24시간 무인 자율 데몬 시작")
        logger.info("⏰ 정기 발행 시각 (KST): 매일 08:30 / 16:00")
        logger.info("=" * 65)

        last_executed_slot = ""
        while True:
            try:
                now = datetime.datetime.now()
                current_hour = now.hour
                current_minute = now.minute
                today_str = now.strftime("%Y-%m-%d")

                for slot in GOLDEN_TIMES:
                    target_h = slot["hour"]
                    target_m = slot["minute"]
                    slot_id = f"{today_str}_{target_h:02d}{target_m:02d}"

                    if current_hour == target_h and abs(current_minute - target_m) <= 2:
                        if last_executed_slot != slot_id:
                            logger.info(f"⏰ [주식AI] {slot['label']} ({target_h}:{target_m:02d}) 도달! 카드뉴스 무인 발행 시작...")
                            self.run_one_cycle()
                            last_executed_slot = slot_id
                            break

                time.sleep(check_interval_seconds)
            except Exception as e:
                logger.error(f"❌ [StockMetaScheduler] 데몬 루프 에러: {e}")
                time.sleep(check_interval_seconds)


if __name__ == "__main__":
    scheduler = StockMetaScheduler()
    if "--now" in sys.argv or "-n" in sys.argv:
        res = scheduler.run_one_cycle()
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif "--daemon" in sys.argv or "-d" in sys.argv:
        scheduler.start_daemon()
    else:
        print("Usage: python stock_meta_scheduler.py [--now | --daemon]")
