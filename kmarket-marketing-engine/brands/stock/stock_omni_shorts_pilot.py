# -*- coding: utf-8 -*-
"""
[독립 레고 블록] Stock Omni Shorts Pilot (📈 StockMaster AI 전용 쏘기 직전 1편 제작 & 4대 채널 단발 송출 파일럿)
===================================================================================================================
- 브랜드: StockMaster AI (공식 검색어: '스톡마스터 AI' 띄어쓰기 불변)
- 핵심 원칙 (대표님 절대 수칙):
  1. [쏘기 전 무조건 1편 신선 제작]: 폴더에서 옛날 파일 무단 주워오기 0% 전면 금지!
     정시(스케줄) 도달 시, 이번 순번 주제(예: #1) 숏폼 1편을 그 자리에서 단독 제작 (StockQuantShortsBuilder)
  2. [즉시 1회 단발 발사]: 방금 생성된 따끈한 고유 MP4를 넘겨받아 4대 플랫폼 동시 송출
     - ① 유튜브 쇼츠 (YouTube Shorts Data API v3 + 고정 댓글 링크)
     - ② 네이버 클립 (Naver Clip 스튜디오 Playwright 무인 업로드 -> '초안' 탈출 '공개' 등록)
     - ③ 인스타그램 릴스 (Instagram Reels Meta Graph API)
     - ④ 페이스북 릴스 (Facebook Reels Meta Graph API + 첫 댓글 링크)
  3. [완벽한 메타데이터 패키징]: 제목, 설명문, 카피, 공식 검색어 유도, 4단 티어 해시태그 100% 탑재
  4. [중복 방지 락(Lock)]: 당일 동일 주제 및 동일 영상 중복 송출 0% 원천 차단
  5. [인간 행동 봇과 완전 분리]: 30분 4회 분할 인간 행동(시청/좋아요)은 StockHumanBehaviorBot이 전담 (0 API)
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

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
from brands.stock.stock_youtube_bot_publisher import StockYouTubeBotPublisher
from brands.stock.stock_tiktok_publisher import StockTikTokPublisher
from brands.stock.stock_naver_clip_publisher import StockNaverClipPublisher
from brands.stock.stock_mbs_reels_publisher import StockMBSReelsPublisher

logger = logging.getLogger("StockOmniShortsPilot")


class StockOmniShortsPilot:
    """📈 StockMaster AI 전용 [쏘기 직전 1편 제작 ➔ 4대 채널 즉시 1회 송출] 통합 관제 파일럿"""

    BRAND = "stock"
    OFFICIAL_KEYWORD = "스톡마스터 AI"
    LANDING_URL = "https://stockmaster-ai.vercel.app/"

    HOOK_TITLES = {
        1: "삼성전자 vs SK하이닉스 HBM 외인 수급 대폭발 ㄷㄷ",
        2: "국내 고배당주(금융지주·맥쿼리) 월배당 시뮬레이션 현실적 치트키",
        3: "코스피·코스닥 세력 체결강도 120% 돌파 급등 유망주 포착",
        4: "코스피200 우량주 vs 코스닥 성장주 직장인 월적립식 복리 비교",
        5: "외인·기관 실시간 쌍끌이 순매수 레이더 포착 종목 TOP 3",
        6: "주식 초보가 100% 물리는 물타기 실수와 AI 손절 탈출 공식",
        7: "저PBR 밸류업 & 고배당 금융주 스크리닝 긴급 공개",
        8: "AI 자동 손절매 & 리스크 가드 퀀트 시스템 실전 운용법"
    }

    def __init__(self):
        self.hashtag_matrix = StockHashtagMatrix()
        self.youtube_pub = StockYouTubeBotPublisher(headless=True)
        self.tiktok_pub = StockTikTokPublisher(headless=True)
        self.clip_pub = StockNaverClipPublisher()
        self.mbs_pub = StockMBSReelsPublisher()
        self.history_file = CURRENT_DIR / "omni_shorts_publish_history.json"
        self.state_file = CURRENT_DIR / "omni_shorts_schedule_state.json"

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
        all_topics = list(self.HOOK_TITLES.keys())
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

        logger.info(f"🔄 [주식 숏폼 LRU 자동 선정] 후보군 {candidates} ➔ 선정 주제: #{chosen_id} (오늘 송출완료: {today_published})")
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

    def produce_fresh_short(self, topic_id: int) -> str:
        """
        🎬 [쏘기 직전 1편 실시간 100% 신선 제작]
        - 과거 생성된 오래된 파일을 무단 주워오지 않고, 쏘기 직전 해당 주제 1편을 실시간으로 신선하게 제작
        - 실패 시 절대 옛날 파일을 주워오지 않고 즉시 중단(Fail-Fast)
        """
        logger.info("=" * 70)
        logger.info(f"🎬 [StockMaster 숏폼 실시간 제작] 쏘기 직전 주제 #{topic_id} 1편 신규 단독 렌더링 시작...")
        logger.info("=" * 70)

        from brands.stock.stock_shorts_pipeline import StockShortsPipeline
        pipeline = StockShortsPipeline()
        output_mp4 = pipeline.produce(topic_id=topic_id)
        if output_mp4 and Path(output_mp4).exists():
            logger.info(f"🎉 [StockMaster 숏폼 제작 100% 성공] 방금 생성된 신선한 완제품: {output_mp4}")
            return str(output_mp4)

        raise RuntimeError(f"🚨 [StockMaster] 주제 #{topic_id} 실시간 숏폼 렌더링 실패! 엉뚱한 과거 파일 주워오기 0% 전면 차단 및 발사 즉각 안전 중단.")

    def build_meta_packages(self, topic_id: int, fresh_video: Optional[str] = None) -> Dict[str, Any]:
        """[제미나이 100% 실시간 카피 + 8대 기능 주입 명세 직결] 4대 채널 텍스트 패키지"""
        guide_hook = ''
        guide_tags = ''
        if fresh_video and os.path.exists(fresh_video):
            guide_file = Path(fresh_video).parent / 'SNS_포스팅_가이드.txt'
            if guide_file.exists():
                try:
                    with open(guide_file, 'r', encoding='utf-8', errors='ignore') as gf:
                        for gline in gf.read().split('\n'):
                            if '발화 훅 요약:' in gline:
                                guide_hook = gline.split('발화 훅 요약:', 1)[1].strip()
                            elif '추천 통합 해시태그:' in gline:
                                guide_tags = gline.split('추천 통합 해시태그:', 1)[1].strip()
                except Exception:
                    pass
        if guide_hook:
            main_title = f'[StockMaster AI] {guide_hook[:40]}'
        else:
            main_title = f'[StockMaster AI] 퀀트 주식 AI 분석 #{topic_id}'
        from brands.stock.stock_domestic_sns_copywriter import StockDomesticSNSCopywriter
        copywriter = StockDomesticSNSCopywriter()
        pkg = copywriter.generate_full_package(topic_id=topic_id, topic_title=main_title, media_type='shorts')
        pkg['main_title'] = main_title
        if guide_tags:
            pkg['tags_line'] = guide_tags
        return pkg
    def execute_single_slot(self, topic_id: Optional[int] = None, force: bool = False) -> Dict[str, Any]:
        """
        🚀 [정시 1회 단발 실행] 쏘기 직전 1편 제작 ➔ 4대 채널 즉시 1회 발사 ➔ 중복 락
        """
        target_topic = topic_id or self.get_next_topic_id()
        today_str = datetime.now().strftime("%Y-%m-%d")

        if not force and self.is_already_published_today(target_topic):
            logger.info(f"🛑 [중복 방지 락] 주식 숏폼 주제 #{target_topic}은 오늘 이미 송출되었습니다. 스킵합니다.")
            return {"status": "skipped", "message": f"주제 #{target_topic} 오늘 송출 완료 상태"}

        try:
            fresh_video = self.produce_fresh_short(target_topic)
        except Exception as e:
            logger.error(f"❌ [주식 숏폼 제작 실패] {e}")
            return {"status": "error", "error": f"제작 실패: {e}"}

        # 🔍 [3단계: 파이썬 실물 전수 검증] "API로 쏘는 건 무조건 바탕화면에 제대로 완이 다 만들고 파이썬 확인 그 다음에 API"
        from brands.stock.stock_production_safety_gate import StockProductionSafetyGate
        is_valid, verify_msg = StockProductionSafetyGate.verify_desktop_shorts_completed(fresh_video)
        if not is_valid:
            logger.critical(f"🛑 [파이썬 완제품 검증 탈락] 바탕화면 숏폼 실물 검증 실패: {verify_msg} -> 외부 API(YouTube/Meta/Clip) 송출 원천 차단!")
            return {"status": "verification_failed", "error": f"바탕화면 숏폼 실물 검증 실패: {verify_msg}"}
        logger.info(f"✅ [3단계 파이썬 완제품 검증 100% 합격] {verify_msg} -> 4단계 외부 API 발사(쏘기) 개시!")

        return self.publish_video(video_path=fresh_video, topic_id=target_topic)

    def publish_video(self, video_path: str, topic_id: int) -> Dict[str, Any]:
        """
        🚀 [4대 채널 100% 무인 일체형 송출]
        유튜브 쇼츠, 틱톡, 네이버 클립, 메타 릴스(인스타+페북)에 검증된 완제품 비디오를 즉시 자율 송출
        """
        fresh_video = str(Path(video_path).resolve())
        target_topic = topic_id
        today_str = datetime.now().strftime("%Y-%m-%d")

        # 4. 메타데이터 패키징 & 외부 API 발사
        pkg = self.build_meta_packages(target_topic, fresh_video)
        results = {
            "status": "success",
            "date": today_str,
            "published_at": get_now_kst_str(),
            "brand": self.BRAND,
            "topic_id": target_topic,
            "title": pkg["main_title"],
            "video_file": os.path.basename(fresh_video),
            "channels": {}
        }

        # 🌐 [대표님 절대 수칙] API 배제 -> 사람처럼 크롬 브라우저를 직접 띄워 올리는 4대 웹 브라우저 봇 자동 송출
        logger.info("🌐 [사람처럼 올리는 4대 브라우저 봇 가동] 유튜브 스튜디오, 틱톡, 네이버 클립, 메타 비즈니스 사이트 무인 송출 시작!")

        # 1. [Channel 1] 유튜브 쇼츠 브라우저 봇 직접 송출
        logger.info(f"🔴 [1/4 유튜브 쇼츠 브라우저 봇 직접 송출] 주제 #{target_topic} 발사...")
        try:
            yt_res = self.youtube_pub.publish_short(
                video_path=fresh_video,
                topic_id=target_topic,
                title=pkg["youtube"]["title"],
                privacy_status="public"
            )
            results["channels"]["youtube"] = yt_res
        except Exception as ye:
            logger.error(f"❌ 유튜브 송출 실패: {ye}")
            results["channels"]["youtube"] = {"status": "error", "error": str(ye)}

        # 2. [Channel 2] 틱톡 쇼츠 브라우저 봇 무인 직접 송출
        logger.info(f"🎵 [2/4 틱톡 쇼츠 브라우저 봇 직접 송출] 주제 #{target_topic} 발사...")
        try:
            tk_caption = pkg.get("tiktok", {}).get("caption")
            tk_res = self.tiktok_pub.publish_short(
                video_path=fresh_video,
                topic_id=target_topic,
                caption=tk_caption,
                title=pkg.get("main_title")
            )
            results["channels"]["tiktok"] = tk_res
        except Exception as tke:
            logger.error(f"❌ 틱톡 송출 실패: {tke}")
            results["channels"]["tiktok"] = {"status": "error", "error": str(tke)}

        # 3. [Channel 3] 네이버 클립 1회 스튜디오 공개 송출
        logger.info(f"🟢 [3/4 네이버 클립 스튜디오 송출] 주제 #{target_topic} 발사...")
        try:
            clip_res = self.clip_pub.publish_clip(
                video_path=fresh_video,
                topic_id=target_topic,
                title=pkg.get("naver_clip", {}).get("title", pkg.get("main_title", "")),
                description=pkg.get("naver_clip", {}).get("description") or pkg.get("naver_clip", {}).get("desc") or pkg.get("tags_line", "")
            )
            results["channels"]["naver_clip"] = clip_res
        except Exception as ce:
            logger.error(f"❌ 네이버 클립 송출 실패: {ce}")
            results["channels"]["naver_clip"] = {"status": "error", "error": str(ce)}

        # 4. [Channel 4] Meta 릴스(인스타+페북) MBS 브라우저 봇 직접 송출
        logger.info(f"📘 [4/4 Meta 플랫폼 MBS] 숏폼 릴스({os.path.basename(fresh_video)}) 인스타그램 릴스 + 페이스북 동시 송출 개시...")
        try:
            caption_text = pkg.get("meta_reels", {}).get("caption") or pkg.get("tags_line", "")
            mbs_res = self.mbs_pub.publish_reel(
                video_path=fresh_video,
                caption=caption_text
            )
            results["channels"]["meta_reels"] = mbs_res
            logger.info(f"📘 메타 릴스 송출 결과: {mbs_res.get('status')}")
        except Exception as me:
            logger.error(f"❌ 메타 릴스 송출 실패: {me}")
            results["channels"]["meta_reels"] = {"status": "error", "error": str(me)}

        # 8. 이력 저장
        self._record_history(results)
        return results

    def _record_history(self, record: Dict[str, Any]):
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []
        history.append(record)
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"이력 저장 경고: {e}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="StockOmniShortsPilot Runner")
    parser.add_argument("--topic", type=int, default=None, help="Target topic ID")
    parser.add_argument("--force", action="store_true", help="Force publish ignoring today lock")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    pilot = StockOmniShortsPilot()
    res = pilot.execute_single_slot(topic_id=args.topic, force=args.force)
    print(json.dumps(res, ensure_ascii=False, indent=2))
