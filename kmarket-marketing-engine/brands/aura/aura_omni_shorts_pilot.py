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
from brands.aura.aura_tiktok_publisher import AuraTikTokPublisher
from brands.aura.aura_naver_clip_publisher import AuraNaverClipPublisher
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
        self.tiktok_pub = AuraTikTokPublisher(headless=True)
        self.clip_pub = AuraNaverClipPublisher()
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

        from brands.aura.aura_shorts_pipeline import AuraShortsPipeline
        pipeline = AuraShortsPipeline()
        output_mp4 = pipeline.produce(topic_id=topic_id)
        if output_mp4 and Path(output_mp4).exists():
            logger.info(f"🎉 [Aura 숏폼 제작 100% 성공] 방금 생성된 신선한 완제품: {output_mp4}")
            return str(output_mp4)

        raise RuntimeError(f"🚨 [Aura] 주제 #{topic_id} 실시간 숏폼 렌더링 실패! 엉뚱한 과거 파일 주워오기 0% 전면 차단 및 발사 즉각 안전 중단.")

    def build_meta_packages(self, topic_id: int, fresh_video: Optional[str] = None) -> Dict[str, Any]:
        """[제미나이 100% 실시간 카피 + 8대 기능 주입 명세 직결] 4대 채널 텍스트 패키지"""
        from brands.aura.aura_shorts_script_writer import AURA_TOPICS_SPECS
        concept = AURA_TOPICS_SPECS.get(topic_id, {})
        feature_name = concept.get("title", f"Aura 핵심 기능 #{topic_id}")
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
            main_title = f'[{feature_name}] {guide_hook[:40]}'
        else:
            main_title = f'[{feature_name}] 아우라 AI 데이팅 #{topic_id}'
        from brands.aura.aura_domestic_sns_copywriter import AuraDomesticSNSCopywriter
        copywriter = AuraDomesticSNSCopywriter()
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

        # 5. [Channel 2] 틱톡 쇼츠 브라우저 봇 무인 직접 송출
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

        # 6. [Channel 3] 네이버 클립 1회 스튜디오 공개 송출
        logger.info(f"🟢 [2/4 네이버 클립 스튜디오 송출] 주제 #{target_topic} 발사...")
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

        # 7. [Channel 4] Meta 릴스 (Meta Business Suite 웹 자동화: 페이스북 + 인스타그램 동시 발행)
        logger.info(f"🚀 [4/4 Meta 플랫폼] 숏폼 릴스({os.path.basename(fresh_video)}) Meta Business Suite 무인 송출 개시...")
        caption_text = pkg.get("meta", {}).get("ig_caption", pkg.get("main_title"))
        try:
            mbs_res = self.mbs_pub.publish_reel(
                video_path=fresh_video,
                caption=caption_text
            )
            results["channels"]["meta_reels"] = mbs_res
            if mbs_res.get("status") == "success":
                logger.info("🎉 [Meta Business Suite 릴스 발행 성공!]")
        except Exception as me:
            logger.error(f"❌ Meta 릴스 발행 실패: {me}")
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
    parser = argparse.ArgumentParser(description="AuraOmniShortsPilot Runner")
    parser.add_argument("--topic", type=int, default=None, help="Target topic ID")
    parser.add_argument("--force", action="store_true", help="Force publish ignoring today lock")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    pilot = AuraOmniShortsPilot()
    res = pilot.execute_single_slot(topic_id=args.topic, force=args.force)
    print(json.dumps(res, ensure_ascii=False, indent=2))
