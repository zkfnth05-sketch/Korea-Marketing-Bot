# -*- coding: utf-8 -*-
"""
AuraMetaScheduler - 💖 [Aura 데이팅 전용 하루 2회 인스타+페북 5장 카드뉴스 & 숏폼 무인 자동화 스케줄러]
======================================================================================================
• 원칙 준수:
  - Rule 1 (완전 독립 레고 블록: brands/aura/ 전담)
  - Rule 6 (24시간 365일 100% 무인 자율 구동 상주 데몬)
  - Rule 7 (공식 검색어 '아우라AI데이팅' 붙여쓰기 + 공식 랜딩 URL)
• 바탕화면 산출물 및 SNS 가이드 100% 원본 직결:
  - 카드뉴스: 바탕화면 'C:\\Users\\zkfnt\\Desktop\\한국 카드뉴스_산출물\\아우라' 5장 이미지 탐색
  - 카피라이팅: 폴더 내 'SNS_가이드_KO.txt' 및 'SNS_포스팅_가이드_KO.txt' 본문/댓글 그대로 추출
  - 숏폼 동영상: 바탕화면 'C:\\Users\\zkfnt\\Desktop\\한국 숏폼_산출물\\Aura' 22초 완제품 탐색
• 스케줄 (대한민국 KST 기준 하루 2회 골든타임):
  - 1회차: 11:30 (직장인 점심시간 전 탐색 피크)
  - 2회차: 19:30 (퇴근길 및 저녁 감성 피크)
"""

import os
import sys
import time
import glob
import re
import json
import logging
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("AuraMetaScheduler")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = DATA_DIR / "aura_meta_rotation_state.json"

DESKTOP_CARDNEWS_DIR = Path(r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\아우라")
DESKTOP_SHORTS_DIR = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Aura")

GOLDEN_TIMES = [
    {"hour": 11, "minute": 30, "label": "점심 피크"},
    {"hour": 19, "minute": 30, "label": "저녁 피크"}
]

from brands.aura.aura_meta_publisher import AuraMetaPublisher
from brands.aura.aura_hashtag_matrix import AuraHashtagMatrix
from brands.aura.aura_cardnews_scenario_director import AuraCardnewsScenarioDirector


class AuraMetaScheduler:
    """💖 Aura AI 데이팅 하루 2회 메타(인스타+페북) 무인 자율 스케줄러"""

    BRAND = "aura"
    OFFICIAL_KEYWORD = "아우라AI데이팅"
    LANDING_URL = "https://aura-ai-dating.vercel.app/"

    def __init__(self):
        self.publisher = AuraMetaPublisher()
        self.hashtag_matrix = AuraHashtagMatrix()
        self.scenario_director = AuraCardnewsScenarioDirector()
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

    def find_desktop_cardnews_and_guide(self, topic_id: int) -> Tuple[List[str], str, str, str]:
        """
        바탕화면 카드뉴스 폴더에서 해당 주제의 5장 PNG 슬라이드 및 SNS 가이드 텍스트 추출
        반환: (slide_paths, ig_caption, fb_caption, fb_first_comment)
        """
        slide_paths = []
        ig_caption = ""
        fb_caption = ""
        fb_comment = ""

        if DESKTOP_CARDNEWS_DIR.exists():
            pattern = str(DESKTOP_CARDNEWS_DIR / f"아우라_{topic_id:02d}_*")
            matched_dirs = sorted(glob.glob(pattern))
            for d in reversed(matched_dirs):
                slides = sorted(glob.glob(os.path.join(d, "slide_*.png")))
                if len(slides) == 5:
                    slide_paths = slides
                    # SNS 가이드 파일 탐색 및 파싱
                    txt_files = glob.glob(os.path.join(d, "*.txt"))
                    if txt_files:
                        with open(txt_files[0], "r", encoding="utf-8", errors="replace") as f:
                            content = f.read()

                        # 1. 인스타그램 가이드 파싱
                        ig_sec = re.search(r"\[\d+\]\s*📸\s*인스타그램[^\n]*\n-+\n(.*?)(?=\n\[\d+\]|\n={5,}|\Z)", content, re.DOTALL)
                        if ig_sec:
                            raw = ig_sec.group(1).strip()
                            cap_match = re.search(r"📌\s*\[인스타\s*캡션[^\n]*\n(.*?)(?=\n📌|\n🏷️|\Z)", raw, re.DOTALL)
                            tags_match = re.search(r"📌\s*\[인스타[^\n]*해시태그[^\n]*\n(.*?)(?=\n📌|\n🏷️|\Z)", raw, re.DOTALL)
                            if cap_match:
                                ig_caption = cap_match.group(1).strip()
                                if tags_match:
                                    ig_caption += "\n\n" + tags_match.group(1).strip()
                            else:
                                lines = [l for l in raw.split("\n") if not l.startswith("📌 [추천 캡션")]
                                ig_caption = "\n".join(lines).strip()

                        # 2. 페이스북 가이드 파싱
                        fb_sec = re.search(r"\[\d+\]\s*📘\s*페이스북[^\n]*\n-+\n(.*?)(?=\n\[\d+\]|\n={5,}|\Z)", content, re.DOTALL)
                        if fb_sec:
                            raw = fb_sec.group(1).strip()
                            cap_match = re.search(r"📌\s*\[페북[^\n]*\n(.*?)(?=\n💬|\n📌|\Z)", raw, re.DOTALL)
                            comm_match = re.search(r"💬\s*\[첫\s*번째\s*댓글[^\n]*\n(.*?)(?=\n📌|\Z)", raw, re.DOTALL)
                            if cap_match:
                                fb_caption = cap_match.group(1).strip()
                            else:
                                comm_split = re.split(r"💬\s*\[첫\s*번째\s*댓글[^\]]*\]", raw)
                                lines = [l for l in comm_split[0].split("\n") if not l.startswith("📌 [추천 본문")]
                                fb_caption = "\n".join(lines).strip()
                                if len(comm_split) > 1:
                                    fb_comment = comm_split[1].strip()
                            if comm_match:
                                fb_comment = comm_match.group(1).strip()

                        # 3. 통합 카피 블록 파싱 (공용 카피인 경우)
                        if not ig_caption and not fb_caption:
                            shared = re.search(r"📌\s*\[인스타그램[^\n]*\n-+\n(.*?)(?=\n={5,}|\n\[|\Z)", content, re.DOTALL)
                            if shared:
                                c = shared.group(1).strip()
                                ig_caption = c
                                fb_caption = c

                        logger.info(f"📂 [Aura 바탕화면 카드뉴스 & SNS가이드 로드 완료] {d} (5장 + 가이드 연동)")
                        break

        # 대체 슬라이드
        if not slide_paths:
            slide_paths = [str(CURRENT_DIR / f"slide_{i}.png") for i in range(1, 6)]

        # 대체 캡션 (가이드가 없는 경우)
        if not fb_caption:
            fb_tags = " ".join(self.hashtag_matrix.get_facebook_hashtags(topic_id=topic_id, count=6))
            fb_caption = (
                f"💖 [Aura AI 데이팅] 소개팅 꿀팁 🚀\n\n"
                f"외모보다 통하는 대화! 남녀 50:50 황금 성비 청정 라운지에서 특별한 인연을 만나보세요.\n\n"
                f"🔍 네이버 검색창에 👉 [ {self.OFFICIAL_KEYWORD} ] 검색해보세요!\n"
                f"👉 공식 라운지: {self.LANDING_URL}\n\n"
                f"{fb_tags}"
            )
        if not ig_caption:
            insta_tags = " ".join(self.hashtag_matrix.get_instagram_hashtags(topic_id=topic_id, count=18))
            ig_caption = (
                f"💖 [Aura AI 데이팅]\n\n"
                f"외모보다 통하는 대화, 남녀 50:50 황금 성비 청정 라운지 ✨\n"
                f"네이버 검색창에 👉 [ {self.OFFICIAL_KEYWORD} ] 검색해보세요!\n\n"
                f"{insta_tags}"
            )

        return slide_paths, ig_caption, fb_caption, fb_comment

    def find_desktop_shorts(self, topic_id: int) -> Optional[str]:
        """바탕화면 산출물 폴더에서 해당 주제의 22초 숏폼 MP4 비디오 탐색"""
        if not DESKTOP_SHORTS_DIR.exists():
            return None

        pattern = str(DESKTOP_SHORTS_DIR / f"**/*주제{topic_id:02d}*.mp4")
        matched = glob.glob(pattern, recursive=True)
        final_clips = [m for m in matched if ("22초" in m or "완성" in m) and os.path.getsize(m) > 2000000]
        if final_clips:
            logger.info(f"🎬 [Aura 바탕화면 숏폼 포착] {final_clips[0]} ({os.path.getsize(final_clips[0])} bytes)")
            return final_clips[0]
        elif matched:
            return matched[0]

        return None

    def run_one_cycle(self, force_topic_id: Optional[int] = None, mode: str = "all") -> Dict[str, Any]:
        """
        🚀 1회 메타 5장 카드뉴스 앨범 & 숏폼 무인 자동 배포 사이클 실행
        - mode: "cardnews" (5장 카드뉴스), "shorts" (숏폼 비디오), "all" (둘 다 배포)
        """
        all_topics = self.scenario_director.get_all_topics()
        total_topics = len(all_topics)

        if force_topic_id is not None:
            topic_id = force_topic_id
            topic_info = next((t for t in all_topics if t["topic_id"] == topic_id), all_topics[0])
        else:
            idx = self.state.get("current_topic_index", 0) % total_topics
            topic_info = all_topics[idx]
            topic_id = topic_info["topic_id"]

        theme_name = topic_info.get("theme_name", "소개팅 꿀팁")
        logger.info(f"💖 [AuraMetaScheduler] 주제 #{topic_id} [{theme_name}] 바탕화면 원본 산출물 배포 가동")

        # 1. 바탕화면 5장 카드뉴스 슬라이드 및 SNS 가이드 카피 로드
        slide_paths, ig_caption, fb_caption, fb_comment = self.find_desktop_cardnews_and_guide(topic_id)
        shorts_path = self.find_desktop_shorts(topic_id)

        # 🚀 [코드 분리 원칙] 인간 행동(체류/좋아요)은 AuraHumanBehaviorBot이 하루 30분 정시 전담!
        # API 송출 봇은 0.1초 고속 정시 배포만 깔끔하게 실행합니다.
        results = {}

        # 1. 페이스북 & 인스타그램 5장 완(Wan 2.1) 카드뉴스 풀세트 발행 (SNS 가이드 원본 본문 사용)
        if mode in ["cardnews", "all"]:
            results["facebook_cardnews"] = self.publisher.publish_facebook_cardnews_album(slide_paths, fb_caption, fb_comment)

            # 인스타그램 5장 카드뉴스 캐러셀 앨범 발행 (바탕화면 Wan 2.1 5장 슬라이드 + SNS 가이드 카피)
            results["instagram_carousel"] = self.publisher.publish_instagram_carousel(slide_paths, ig_caption)

        # 2. 페이스북 & 인스타그램 숏폼 비디오/릴스 발행 (바탕화면 22초 MP4 완제품)
        if mode in ["shorts", "all"] and shorts_path and os.path.exists(shorts_path):
            video_title = f"[Aura] {theme_name}"
            video_desc = fb_caption
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
            "cardnews_slides_count": len(slide_paths),
            "cardnews_source_dir": str(Path(slide_paths[0]).parent) if slide_paths else None,
            "shorts_video": os.path.basename(shorts_path) if shorts_path else None,
            "results": results
        }
        self.state.setdefault("history", []).append(log_entry)
        if len(self.state["history"]) > 50:
            self.state["history"] = self.state["history"][-50:]
        self._save_state(self.state)

        logger.info(f"🎉 [AuraMetaScheduler] 주제 #{topic_id} 배포 완료! (누적: {self.state['published_count']}회)")
        return log_entry

    def start_daemon(self, check_interval_seconds: int = 60):
        """24시간 365일 백그라운드 상주 데몬 (하루 2회 정시 기상/배포)"""
        logger.info("=" * 65)
        logger.info("🤖 [Aura] 하루 2회 메타(인스타+페북) 24시간 무인 자율 데몬 시작")
        logger.info("⏰ 정기 발행 시각 (KST): 매일 11:30 / 19:30")
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
                            logger.info(f"⏰ [Aura] {slot['label']} ({target_h}:{target_m:02d}) 도달! 바탕화면 원본 5장 카드뉴스+숏폼 무인 발행 시작...")
                            self.run_one_cycle()
                            last_executed_slot = slot_id
                            break

                time.sleep(check_interval_seconds)
            except Exception as e:
                logger.error(f"❌ [AuraMetaScheduler] 데몬 루프 에러: {e}")
                time.sleep(check_interval_seconds)


if __name__ == "__main__":
    scheduler = AuraMetaScheduler()
    force_topic = None
    mode = "all"

    for i, arg in enumerate(sys.argv):
        if arg in ["--topic", "-t"] and i + 1 < len(sys.argv):
            try:
                force_topic = int(sys.argv[i + 1])
            except ValueError:
                pass
        if arg in ["--mode", "-m"] and i + 1 < len(sys.argv):
            mode = sys.argv[i + 1]

    if "--now" in sys.argv or "-n" in sys.argv:
        res = scheduler.run_one_cycle(force_topic_id=force_topic, mode=mode)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif "--daemon" in sys.argv or "-d" in sys.argv:
        scheduler.start_daemon()
    else:
        print("Usage: python aura_meta_scheduler.py [--now | --daemon] [--topic N] [--mode all|cardnews|shorts]")
