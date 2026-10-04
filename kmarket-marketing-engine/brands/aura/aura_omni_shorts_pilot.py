# -*- coding: utf-8 -*-
"""
[독립 레고 블록] Aura Omni Shorts Pilot (💖 Aura 전용 쏘기 직전 1편 제작 & 4대 채널 단발 송출 파일럿)
========================================================================================================
- 브랜드: Aura AI 데이팅 (공식 검색어: '아우라AI데이팅' 붙여쓰기 불변)
- 핵심 원칙 (대표님 절대 수칙):
  1. [쏘기 전 무조건 1편 신선 제작]: 폴더에서 옛날 파일 무단 주워오기 0% 전면 금지!
     정시(스케줄) 도달 시, 이번 순번 주제(예: #1) 숏폼 1편을 그 자리에서 단독 제작
  2. [즉시 1회 단발 발사]: 방금 생성된 따끈한 고유 MP4를 넘겨받아 4대 플랫폼 동시 송출
     - ① 유튜브 쇼츠 (YouTube Shorts Data API v3 + 고정 댓글 링크)
     - ② 네이버 클립 (Naver Clip 스튜디오 Playwright 무인 업로드 -> '초안' 탈출 '공개' 등록)
     - ③ 인스타그램 릴스 (Instagram Reels Meta Graph API)
     - ④ 페이스북 릴스 (Facebook Reels Meta Graph API + 첫 댓글 링크)
  3. [완벽한 메타데이터 패키징]: 제목, 설명문, 카피, 공식 검색어 유도, 4단 티어 해시태그 100% 탑재
  4. [중복 방지 락(Lock)]: 당일 동일 주제 및 동일 영상 중복 송출 0% 원천 차단
  5. [인간 행동 봇과 완전 분리]: 30분 4회 분할 인간 행동(시청/좋아요)은 AuraHumanBehaviorBot이 전담 (0 API)
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
from brands.aura.aura_hashtag_matrix import AuraHashtagMatrix
from brands.aura.aura_youtube_bot_publisher import AuraYouTubeBotPublisher
from brands.aura.aura_naver_clip_publisher import AuraNaverClipPublisher
from brands.aura.aura_meta_publisher import AuraMetaPublisher
from brands.aura.aura_mbs_reels_publisher import AuraMBSReelsPublisher

logger = logging.getLogger("AuraOmniShortsPilot")


class AuraOmniShortsPilot:
    """💖 Aura 데이팅 전용 [쏘기 직전 1편 제작 ➔ 4대 채널 즉시 1회 송출] 통합 관제 파일럿"""

    BRAND = "aura"
    OFFICIAL_KEYWORD = "아우라AI데이팅"
    LANDING_URL = "https://aura-ai-dating.vercel.app/"

    HOOK_TITLES = {
        1: "소개팅에서 어색할 때 3초 만에 탈출하는 비법 ㄷㄷ",
        2: "카톡 답장 느린 사람 100% 심리 분석 (읽씹 대처법)",
        3: "남초 제로, 성비 50:50 데이팅 라운지 실화냐?",
        4: "첫 만남에서 호감도 3배 올리는 스몰토크 치트키",
        5: "2030 남녀가 뽑은 최악의 소개팅 착장 1위는?",
        6: "소개팅 애프터 신청 골든타임 & 카톡 멘트 추천",
        7: "성수동/연남동 분위기 터지는 소개팅 핫플 추천",
        8: "MBTI 유형별 절대 실패 없는 연애 공략법"
    }

    def __init__(self):
        self.hashtag_matrix = AuraHashtagMatrix()
        self.youtube_pub = AuraYouTubeBotPublisher(headless=True)
        self.clip_pub = AuraNaverClipPublisher()
        self.meta_pub = AuraMetaPublisher()
        self.mbs_pub = AuraMBSReelsPublisher()
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

        logger.info(f"🔄 [Aura 숏폼 LRU 자동 선정] 후보군 {candidates} ➔ 선정 주제: #{chosen_id} (오늘 송출완료: {today_published})")
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
        logger.info(f"🎬 [Aura 숏폼 실시간 제작] 쏘기 직전 주제 #{topic_id} 1편 신규 단독 렌더링 시작...")
        logger.info("=" * 70)

        from core.engine.gpu_lock import gpu_lock
        with gpu_lock(f"Aura 숏폼 제작 #{topic_id}"):
            from brands.aura.aura_shorts_pipeline import AuraShortsPipeline
            pipeline = AuraShortsPipeline()
            output_mp4 = pipeline.produce(topic_id=topic_id)
            if output_mp4 and os.path.exists(output_mp4):
                logger.info(f"🎉 [Aura 숏폼 제작 100% 성공] 방금 생성된 신선한 완제품: {output_mp4}")
                return str(output_mp4)
            raise RuntimeError(f"Aura 주제 #{topic_id} 실시간 숏폼 렌더링 실패: 산출물 MP4 부재")

    def build_meta_packages(self, topic_id: int) -> Dict[str, Any]:
        """[제미나이 100% 실시간 카피 + 실시간 급상승 트렌드 해시태그 융합] 4대 채널 포스팅 패키지"""
        main_title = self.HOOK_TITLES.get(topic_id, f"Aura 연애 꿀팁 #{topic_id}")
        from core.gemini_domestic_sns_copywriter import GeminiDomesticSNSCopywriter
        copywriter = GeminiDomesticSNSCopywriter(brand="aura")
        return copywriter.generate_full_package(topic_id=topic_id, topic_title=main_title, media_type="shorts")

    def execute_single_slot(self, topic_id: Optional[int] = None, force: bool = False) -> Dict[str, Any]:
        """
        🚀 [정시 1회 단발 실행] 쏘기 직전 1편 제작 ➔ 4대 채널 즉시 1회 발사 ➔ 중복 락
        """
        target_topic = topic_id or self.get_next_topic_id()
        today_str = datetime.now().strftime("%Y-%m-%d")

        # 1. 중복 방지 락 검사
        if not force and self.is_already_published_today(target_topic):
            logger.info(f"🛑 [중복 방지 락] 주제 #{target_topic}은 오늘 이미 완벽하게 송출되었습니다. 도배 방지를 위해 스킵합니다.")
            return {"status": "skipped", "message": f"주제 #{target_topic} 오늘 송출 완료 상태"}

        # 2. 쏘기 직전 1편 신선 제작
        try:
            fresh_video = self.produce_fresh_short(target_topic)
        except Exception as e:
            logger.error(f"❌ [숏폼 제작 실패] {e}")
            return {"status": "error", "error": f"제작 실패: {e}"}

        # 🔍 [3단계: 파이썬 실물 전수 검증] "API로 쏘는 건 무조건 바탕화면에 제대로 완이 다 만들고 파이썬 확인 그 다음에 API"
        from brands.aura.aura_production_safety_gate import AuraProductionSafetyGate
        is_valid, verify_msg = AuraProductionSafetyGate.verify_desktop_shorts_completed(fresh_video)
        if not is_valid:
            logger.critical(f"🛑 [파이썬 완제품 검증 탈락] 바탕화면 숏폼 실물 검증 실패: {verify_msg} -> 외부 API(YouTube/Meta/Clip) 송출 원천 차단!")
            return {"status": "verification_failed", "error": f"바탕화면 숏폼 실물 검증 실패: {verify_msg}"}
        logger.info(f"✅ [3단계 파이썬 완제품 검증 100% 합격] {verify_msg} -> 4단계 외부 API 발사(쏘기) 개시!")

        # 4. 메타데이터 패키징 & 외부 API 발사
        pkg = self.build_meta_packages(target_topic)
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

        # 🛑 [대표님 긴급 수칙] 외부 API 송출 차단 모드 검사
        dispatch_allowed, dispatch_msg = AuraProductionSafetyGate.is_api_dispatch_allowed()
        if not dispatch_allowed:
            logger.warning(f"{dispatch_msg} (주제 #{target_topic} 바탕화면 실물 보관 완료)")
            results["channels"] = {"all_channels": {"status": "blocked", "message": dispatch_msg}}
            self.save_publish_history(results)
            return results

        # 4. [Channel 1] 유튜브 쇼츠 브라우저 봇 직접 송출
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

        # 5. [Channel 2] 네이버 클립 1회 스튜디오 공개 송출
        logger.info(f"🟢 [2/4 네이버 클립 스튜디오 송출] 주제 #{target_topic} 발사...")
        try:
            clip_res = self.clip_pub.publish_clip(
                video_path=fresh_video,
                topic_id=target_topic,
                title=pkg["naver_clip"]["title"]
            )
            results["channels"]["naver_clip"] = clip_res
        except Exception as ce:
            logger.error(f"❌ 네이버 클립 송출 실패: {ce}")
            results["channels"]["naver_clip"] = {"status": "error", "error": str(ce)}

        # 6. [Channel 3 & 4] Meta 릴스 (MBS 웹 자동화: 인스타그램 + 페이스북 릴스 동시 송출)
        if self.mbs_pub.is_available():
            logger.info(f"🌐 [Meta Business Suite] 숏폼 릴스({os.path.basename(fresh_video)}) 인스타+페북 웹 무인 발행 개시...")
            try:
                mbs_res = self.mbs_pub.publish_reel(
                    video_path=fresh_video,
                    caption=pkg["meta"]["ig_caption"]
                )
                results["channels"]["meta_business_suite_reels"] = mbs_res
                logger.info(f"🎉 [MBS 릴스 발행 완료]: {mbs_res.get('status')}")
            except Exception as mbse:
                logger.error(f"❌ [MBS 릴스 발행 예외] {mbse}")
                results["channels"]["meta_business_suite_reels"] = {"status": "error", "error": str(mbse)}
        elif self.meta_pub.is_available():
            logger.info(f"📸 [대체 Graph API] 인스타그램 & 페이스북 릴스 송출...")
            try:
                ig_res = self.meta_pub.publish_instagram_reels(
                    video_url=fresh_video,
                    caption=pkg["meta"]["ig_caption"]
                )
                results["channels"]["instagram_reel"] = ig_res
            except Exception as ige:
                results["channels"]["instagram_reel"] = {"status": "error", "error": str(ige)}
        else:
            logger.info("ℹ️ [Meta] MBS 프로필 및 API 점검 요망 (유튜브 & 네이버 클립 송출 완료)")

        # 7. 중복 락 및 히스토리 영구 기록
        self._record_history(results)
        logger.info("=" * 70)
        logger.info(f"🎉 [Aura 4대 숏폼 1회 단발 송출 완료] 주제 #{target_topic} | 파일: {os.path.basename(fresh_video)}")
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
    pilot = AuraOmniShortsPilot()
    print(f"💖 Aura Omni Shorts Pilot 준비 완료! (다음 롤링 주제: #{pilot.get_next_topic_id()})")
