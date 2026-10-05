# -*- coding: utf-8 -*-
"""
InsuranceMetaScheduler - 🛡️ [보험 리밸런스 전용 하루 2회 인스타+페북 카드뉴스 & 숏폼 무인 자동화 스케줄러]
======================================================================================================
• 원칙 준수:
  - Rule 1 (완전 독립 레고 블록: brands/insurance/ 전담)
  - Rule 6 (24시간 365일 100% 무인 자율 구동 상주 데몬)
  - Rule 7 (공식 검색어 '보험 리밸런스' 띄어쓰기 + 공식 랜딩 URL)
• 산출물 원천 연동:
  - 카드뉴스: 바탕화면 'C:\\Users\\zkfnt\\Desktop\\한국 카드뉴스_산출물\\Insurance'
  - 숏폼 동영상: 바탕화면 'C:\\Users\\zkfnt\\Desktop\\한국 숏폼_산출물\\Insurance' 22초 완제품
• 스케줄 (대한민국 KST 기준 하루 2회 골든타임):
  - 1회차: 12:00 (점심시간 직장인 재테크/보험 절약 탐색)
  - 2회차: 20:00 (퇴근 후 가계부 정리 및 고정지출 점검)
• 동작:
  - 8대 보험 절약 주제 자동 순환 (data/insurance_meta_rotation_state.json)
  - 4단 티어 해시태그 매트릭스(InsuranceHashtagMatrix) 자동 주입
  - 페이스북 및 인스타그램 100% 무인 자동 발행
"""

import re
import os
import sys
import time
import glob
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

logger = logging.getLogger("InsuranceMetaScheduler")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = DATA_DIR / "insurance_meta_rotation_state.json"

DESKTOP_CARDNEWS_DIRS = [
    Path(r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\보험"),
    Path(r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\Insurance")
]
DESKTOP_SHORTS_DIRS = [
    Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\보험"),
    Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Insurance")
]

GOLDEN_TIMES = [
    {"hour": 12, "minute": 0, "label": "점심 재테크 피크"},
    {"hour": 20, "minute": 0, "label": "저녁 가계부 피크"}
]

from brands.insurance.insurance_meta_publisher import InsuranceMetaPublisher
from brands.insurance.insurance_mbs_reels_publisher import InsuranceMBSReelsPublisher
from brands.insurance.insurance_hashtag_matrix import InsuranceHashtagMatrix


class InsuranceMetaScheduler:
    """🛡️ 보험 리밸런스 하루 2회 메타(인스타+페북) 무인 자율 스케줄러"""

    BRAND = "insurance"
    OFFICIAL_KEYWORD = "보험 리밸런스"
    LANDING_URL = "https://insure-rebalance.vercel.app/"

    TOPICS = [
        {"topic_id": 1, "theme_name": "4세대 실손보험 전환 팩트"},
        {"topic_id": 2, "theme_name": "운전자보험 1만원의 법칙"},
        {"topic_id": 3, "theme_name": "암보험 일반암 vs 유사암 진실"},
        {"topic_id": 4, "theme_name": "뇌·심장 질환 뇌출혈 vs 뇌혈관"},
        {"topic_id": 5, "theme_name": "아는 사람 부탁으로 가입한 보험 손익 분석"},
        {"topic_id": 6, "theme_name": "어린이·어른이 100세 만기 리모델링"},
        {"topic_id": 7, "theme_name": "내 보험 정밀 비교 & 새는 보험료 다이어트"},
        {"topic_id": 8, "theme_name": "AI 보험료 역추정 비교 & 가성비 리모델링"}
    ]

    def __init__(self):
        self.publisher = InsuranceMetaPublisher()
        self.mbs_pub = InsuranceMBSReelsPublisher()
        self.hashtag_matrix = InsuranceHashtagMatrix()
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

    def find_desktop_cardnews_and_guide(self, topic_id: int) -> Tuple[List[str], str, str]:
        """
        바탕화면 카드뉴스 폴더에서 해당 주제의 5장 PNG 슬라이드 및 SNS 가이드 텍스트 추출
        반환: (slide_paths, ig_caption, fb_caption)
        """
        slide_paths = []
        ig_caption = ""
        fb_caption = ""

        matched_dirs = []
        for base_dir in DESKTOP_CARDNEWS_DIRS:
            if base_dir.exists():
                patterns = [
                    str(base_dir / f"보험_{topic_id:02d}_*"),
                    str(base_dir / f"**/*주제{topic_id:02d}*"),
                    str(base_dir / f"**/*Topic_{topic_id:02d}*")
                ]
                for pat in patterns:
                    matched_dirs.extend(glob.glob(pat, recursive=True))

        matched_dirs = sorted(list(set(matched_dirs)))
        for d in reversed(matched_dirs):
            if os.path.isdir(d):
                slides = sorted(glob.glob(os.path.join(d, "slide_*.png")))
                if len(slides) >= 4:
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
                            if cap_match:
                                fb_caption = cap_match.group(1).strip()
                            else:
                                lines = [l for l in raw.split("\n") if not l.startswith("📌 [추천 본문")]
                                fb_caption = "\n".join(lines).strip()

                        logger.info(f"📂 [Insurance 바탕화면 카드뉴스 & SNS가이드 로드 완료] {d} ({len(slide_paths)}장 + 가이드 연동)")
                        break

        return slide_paths, ig_caption, fb_caption

    def find_desktop_shorts(self, topic_id: int) -> Optional[str]:
        matched = []
        for base_dir in DESKTOP_SHORTS_DIRS:
            if base_dir.exists():
                patterns = [
                    str(base_dir / f"**/*주제{topic_id:02d}*.mp4"),
                    str(base_dir / f"**/*Topic_{topic_id:02d}*.mp4")
                ]
                for pat in patterns:
                    matched.extend(glob.glob(pat, recursive=True))

        final_clips = [m for m in matched if ("22초" in m or "완성" in m) and os.path.getsize(m) > 2000000]
        if final_clips:
            return final_clips[0]
        elif matched:
            return matched[0]
        return None

    def run_one_cycle(self, force_topic_id: Optional[int] = None, mode: str = "all") -> Dict[str, Any]:
        total_topics = len(self.TOPICS)

        if force_topic_id is not None:
            topic_id = force_topic_id
            topic_info = next((t for t in self.TOPICS if t["topic_id"] == topic_id), self.TOPICS[0])
        else:
            idx = self.state.get("current_topic_index", 0) % total_topics
            topic_info = self.TOPICS[idx]
            topic_id = topic_info["topic_id"]

        theme_name = topic_info.get("theme_name", "보험 절약 팁")
        logger.info(f"🛡️ [InsuranceMetaScheduler] 주제 #{topic_id} [{theme_name}] 바탕화면 산출물 배포 가동")

        slide_paths, guide_ig_cap, guide_fb_cap = self.find_desktop_cardnews_and_guide(topic_id)
        shorts_path = self.find_desktop_shorts(topic_id)

        insta_tags = " ".join(self.hashtag_matrix.get_instagram_hashtags(topic_id=topic_id, count=18))
        fb_tags = " ".join(self.hashtag_matrix.get_facebook_hashtags(topic_id=topic_id, count=6))

        results = {}

        fb_caption = guide_fb_cap or (
            f"🛡️ [보험 리밸런스] {theme_name} 🚗💨\n\n"
            f"매달 빠져나가는 내 보험료, 과연 적정할까요?\n"
            f"불필요한 중복 보장은 줄이고, 꼭 필요한 보장만 쏙쏙 골라 담는 스마트 보험 다이어트!\n"
            f"알면 아반떼 1대 값 아끼는 34개 보험사 무료 자가진단을 시작해보세요.\n\n"
            f"🔍 네이버 검색창에 👉 [ {self.OFFICIAL_KEYWORD} ] 검색해보세요!\n"
            f"👉 공식 진단: {self.LANDING_URL}\n\n"
            f"{fb_tags}"
        )

        ig_caption = guide_ig_cap or (
            f"🛡️ [보험 리밸런스] {theme_name}\n\n"
            f"네이버 검색창에 👉 [ {self.OFFICIAL_KEYWORD} ] 검색해보세요!\n"
            f"프로필 링크에서 34개 보험사 무료 진단 ✨\n\n"
            f"{insta_tags}"
        )

        if mode in ["cardnews", "all"]:
            cardnews_reels_path = None
            if slide_paths and len(slide_paths) >= 2:
                try:
                    from core.cardnews_to_reels_converter import CardnewsToReelsConverter
                    converter = CardnewsToReelsConverter()
                    slide_dir = Path(slide_paths[0]).parent
                    out_reels = str(slide_dir / f"insurance_topic{topic_id}_cardnews_reels.mp4")
                    conv_res = converter.convert(slide_paths=slide_paths, output_path=out_reels, brand="insurance")
                    if conv_res.get("status") == "success":
                        cardnews_reels_path = out_reels
                        logger.info(f"🎬 [CardnewsToReels 완료] 릴스 변환 성공: {out_reels}")
                except Exception as ce:
                    logger.error(f"❌ [CardnewsToReels 변환 예외] {ce}")

            if self.mbs_pub.is_available() and cardnews_reels_path and os.path.exists(cardnews_reels_path):
                logger.info(f"🌐 [Meta Business Suite] 카드뉴스 릴스({os.path.basename(cardnews_reels_path)}) 인스타+페북 동시 발행...")
                results["mbs_cardnews_reels"] = self.mbs_pub.publish_reel(cardnews_reels_path, ig_caption)
            elif slide_paths:
                results["facebook_cardnews"] = self.publisher.publish_facebook_cardnews_album(slide_paths, fb_caption)
                results["instagram_carousel"] = self.publisher.publish_instagram_carousel(slide_paths, ig_caption)

        if mode in ["shorts", "all"] and shorts_path and os.path.exists(shorts_path):
            if self.mbs_pub.is_available():
                logger.info(f"🌐 [Meta Business Suite] 숏폼 릴스({os.path.basename(shorts_path)}) 인스타+페북 동시 발행...")
                results["mbs_shorts_reels"] = self.mbs_pub.publish_reel(shorts_path, ig_caption)
            else:
                video_title = f"[보험 리밸런스] {theme_name}"
                video_desc = (
                    f"🛡️ [보험 리밸런스] {theme_name} 🚗💨\n\n"
                    f"🔍 네이버 검색창에 👉 [ {self.OFFICIAL_KEYWORD} ] 검색해보세요!\n"
                    f"👉 공식 진단: {self.LANDING_URL}\n\n"
                    f"{fb_tags}"
                )
                results["facebook_video"] = self.publisher.publish_facebook_video(shorts_path, video_title, video_desc)
                results["instagram_reels"] = self.publisher.publish_instagram_reels(shorts_path, ig_caption)

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if force_topic_id is None:
            self.state["current_topic_index"] = (self.state.get("current_topic_index", 0) + 1) % total_topics
        self.state["last_topic_id"] = topic_id
        self.state["last_run_time"] = now_str
        self.state["published_count"] = self.state.get("published_count", 0) + 1

        log_entry = {
            "timestamp": now_str,
            "topic_id": topic_id,
            "theme_name": theme_name,
            "shorts_video": os.path.basename(shorts_path) if shorts_path else None,
            "results": results
        }
        self.state.setdefault("history", []).append(log_entry)
        if len(self.state["history"]) > 50:
            self.state["history"] = self.state["history"][-50:]
        self._save_state(self.state)

        logger.info(f"🎉 [InsuranceMetaScheduler] 주제 #{topic_id} 배포 완료! (누적: {self.state['published_count']}회)")
        return log_entry

    def start_daemon(self, check_interval_seconds: int = 60):
        logger.info("=" * 65)
        logger.info("🤖 [보험 리밸런스] 하루 2회 메타(인스타+페북) 24시간 무인 자율 데몬 시작")
        logger.info("⏰ 정기 발행 시각 (KST): 매일 12:00 / 20:00")
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
                            logger.info(f"⏰ [보험] {slot['label']} ({target_h}:{target_m:02d}) 도달! 카드뉴스+숏폼 무인 발행 시작...")
                            self.run_one_cycle()
                            last_executed_slot = slot_id
                            break

                time.sleep(check_interval_seconds)
            except Exception as e:
                logger.error(f"❌ [InsuranceMetaScheduler] 데몬 루프 에러: {e}")
                time.sleep(check_interval_seconds)


if __name__ == "__main__":
    scheduler = InsuranceMetaScheduler()
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
        print("Usage: python insurance_meta_scheduler.py [--now | --daemon] [--topic N] [--mode all|cardnews|shorts]")
