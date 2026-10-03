# -*- coding: utf-8 -*-
"""
[독립 레고 블록] Aura Omni Cardnews Pilot (💖 Aura 전용 쏘기 직전 5장 카드뉴스 제작 & Meta 단발 송출 파일럿)
=============================================================================================================
- 브랜드: Aura AI 데이팅 (공식 검색어: '아우라AI데이팅' 붙여쓰기 불변)
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
from brands.aura.aura_hashtag_matrix import AuraHashtagMatrix
from brands.aura.aura_meta_publisher import AuraMetaPublisher
from brands.aura.aura_mbs_reels_publisher import AuraMBSReelsPublisher

logger = logging.getLogger("AuraOmniCardnewsPilot")


class AuraOmniCardnewsPilot:
    """💖 Aura 데이팅 전용 [쏘기 직전 5장 카드뉴스 제작 ➔ Meta 1회 단발 송출] 통합 관제 파일럿"""

    BRAND = "aura"
    OFFICIAL_KEYWORD = "아우라AI데이팅"
    LANDING_URL = "https://aura-ai-dating.vercel.app/"

    CARDNEWS_TOPICS = {
        1: "소개팅 첫 만남, 어색함 3초 만에 깨는 대화 치트키 4선",
        2: "성수동 소개팅 실패 없는 감성 코스 BEST 4",
        3: "카톡 답장 속도와 말투로 읽는 100% 호감 시그널 4가지",
        4: "2030 남녀가 뽑은 첫 만남 비호감 행동 1위는?",
        5: "애프터 신청 100% 성공하는 골든타임 & 카톡 멘트",
        6: "MBTI 유형별 절대 실패 없는 소개팅 대화법",
        7: "외모보다 대화가 통하는 50:50 황금 성비 라운지 이용법",
        8: "주말에 뭐하지? 솔로 탈출을 위한 2030 주말 힐링 스팟"
    }

    def __init__(self):
        self.hashtag_matrix = AuraHashtagMatrix()
        self.meta_pub = AuraMetaPublisher()
        self.mbs_pub = AuraMBSReelsPublisher()
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

        logger.info(f"🔄 [Aura 카드뉴스 LRU 자동 선정] 후보군 {candidates} ➔ 선정 주제: #{chosen_id} (오늘 송출완료: {today_published})")
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
        🎨 [쏘기 직전 5장 카드뉴스 신선 제작]
        - 쏘기 직전 해당 주제의 5장 슬라이드를 단독 생산
        """
        logger.info("=" * 70)
        logger.info(f"🎨 [Aura 카드뉴스 제작] 쏘기 직전 주제 #{topic_id} 5장 신규 렌더링 시작...")
        logger.info("=" * 70)

        try:
            from brands.aura.aura_cardnews_producer import AuraCardnewsProducer
            producer = AuraCardnewsProducer()
            res = producer.produce_cardnews(topic_id=topic_id)
            fresh_slides = res.get("slide_paths") or res.get("slides")
            if res.get("success") and fresh_slides:
                if len(fresh_slides) >= 4:
                    logger.info(f"🎉 [Aura 카드뉴스 제작 성공] 갓 생성된 신선 슬라이드 {len(fresh_slides)}장 확보!")
                    return fresh_slides
            raise RuntimeError(f"카드뉴스 엔진 반환값 불완전: {res}")
        except Exception as pe:
            logger.error(f"❌ [Aura 카드뉴스 실시간 신규 제작 실패] {pe}")
            raise RuntimeError(f"Aura 주제 #{topic_id} 카드뉴스 실시간 생성 실패: {pe}")

    def build_meta_packages(self, topic_id: int) -> Dict[str, Any]:
        """[제미나이 100% 실시간 카피 + 실시간 급상승 트렌드 해시태그 융합] 5장 카드뉴스 Meta 포스팅 패키지"""
        main_title = self.CARDNEWS_TOPICS.get(topic_id, f"소개팅 꿀팁 카드뉴스 #{topic_id}")
        from core.gemini_domestic_sns_copywriter import GeminiDomesticSNSCopywriter
        copywriter = GeminiDomesticSNSCopywriter(brand="aura")
        pkg = copywriter.generate_full_package(topic_id=topic_id, topic_title=main_title, media_type="cardnews")
        return {
            "title": main_title,
            "ig_caption": pkg["meta"]["ig_caption"],
            "fb_caption": pkg["meta"]["fb_caption"],
            "fb_comment": pkg["meta"]["fb_comment"]
        }

    def execute_single_slot(self, topic_id: Optional[int] = None, force: bool = False) -> Dict[str, Any]:
        """
        🚀 [정시 1회 단발 실행] 쏘기 직전 5장 제작 ➔ Meta 즉시 1회 발사 ➔ 중복 락
        """
        target_topic = topic_id or self.get_next_topic_id()
        today_str = datetime.now().strftime("%Y-%m-%d")

        # 1. 중복 방지 락 검사
        if not force and self.is_already_published_today(target_topic):
            logger.info(f"🛑 [중복 방지 락] 카드뉴스 주제 #{target_topic}은 오늘 이미 송출 완료되었습니다. 스킵합니다.")
            return {"status": "skipped", "message": f"주제 #{target_topic} 오늘 송출 완료 상태"}

        # 2. 쏘기 직전 5장 카드뉴스 신선 제작
        try:
            slides = self.produce_fresh_cardnews(target_topic)
        except Exception as e:
            logger.error(f"❌ [카드뉴스 제작 실패] {e}")
            return {"status": "error", "error": f"제작 실패: {e}"}

        # 🔍 [3단계: 파이썬 실물 전수 검증] "API로 쏘는 건 무조건 바탕화면에 제대로 완이 다 만들고 파이썬 확인 그 다음에 API"
        from brands.aura.aura_production_safety_gate import AuraProductionSafetyGate
        is_valid, verify_msg = AuraProductionSafetyGate.verify_desktop_cardnews_completed(slides)
        if not is_valid:
            logger.critical(f"🛑 [파이썬 완제품 검증 탈락] 바탕화면 카드뉴스 실물 검증 실패: {verify_msg} -> 외부 API(Meta) 송출 원천 차단!")
            return {"status": "verification_failed", "error": f"바탕화면 실물 검증 실패: {verify_msg}"}
        logger.info(f"✅ [3단계 파이썬 완제품 검증 100% 합격] {verify_msg} -> 4단계 외부 API(Meta) 발사(쏘기) 개시!")

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
        dispatch_allowed, dispatch_msg = AuraProductionSafetyGate.is_api_dispatch_allowed()
        if not dispatch_allowed:
            logger.warning(f"{dispatch_msg} (주제 #{target_topic} 바탕화면 실물 {len(slides)}장 보관 완료)")
            results["channels"] = {"all_channels": {"status": "blocked", "message": dispatch_msg}}
            self.save_publish_history(results)
            return results

        # 4. [Channel 1 & 2] Meta 릴스 (MBS 웹 자동화: 인스타그램 + 페이스북 동시 송출)
        cardnews_reels_path = None
        try:
            from core.cardnews_to_reels_converter import CardnewsToReelsConverter
            converter = CardnewsToReelsConverter()
            slide_dir = Path(slides[0]).parent if slides else CURRENT_DIR
            out_reels = str(slide_dir / f"aura_topic{target_topic}_cardnews_reels.mp4")
            conv_res = converter.convert(slide_paths=slides, output_path=out_reels, brand="aura")
            if conv_res.get("status") == "success":
                cardnews_reels_path = out_reels
                logger.info(f"🎬 [CardnewsToReels 완료] 릴스 변환 성공: {out_reels}")
            else:
                logger.warning(f"⚠️ [CardnewsToReels 경고] 릴스 변환 실패: {conv_res.get('message')}")
        except Exception as ce:
            logger.error(f"❌ [CardnewsToReels 예외] {ce}")

        if self.mbs_pub.is_available() and cardnews_reels_path and os.path.exists(cardnews_reels_path):
            logger.info(f"🌐 [Meta Business Suite] 카드뉴스 릴스({os.path.basename(cardnews_reels_path)}) 인스타+페북 웹 무인 발행 개시...")
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
        elif self.meta_pub.is_available():
            logger.info(f"📘 [대체 Graph API] 페이스북 5장 카드뉴스 앨범 송출...")
            try:
                fb_res = self.meta_pub.publish_facebook_cardnews_album(
                    image_paths=slides,
                    caption=pkg["fb_caption"],
                    first_comment=pkg["fb_comment"]
                )
                results["channels"]["facebook_cardnews"] = fb_res
            except Exception as fbe:
                results["channels"]["facebook_cardnews"] = {"status": "error", "error": str(fbe)}
        else:
            logger.warning("⚠️ [Meta] MBS 프로필 및 API 점검 요망 (산출물 5장 완제품 패키징 완료)")
            results["channels"]["meta"] = {"status": "ready_staged", "message": "발행 대기 완료"}

        # 5. 중복 락 및 히스토리 영구 기록
        self._record_history(results)
        logger.info("=" * 70)
        logger.info(f"🎉 [Aura 5장 카드뉴스 1회 단발 송출 완료] 주제 #{target_topic} | 슬라이드 {len(slides)}장")
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
    pilot = AuraOmniCardnewsPilot()
    print(f"💖 Aura Omni Cardnews Pilot 준비 완료! (다음 롤링 주제: #{pilot.get_next_topic_id()})")
