# -*- coding: utf-8 -*-
"""
[Aura] 8대 정예 카페 스텔스 로테이션 스케줄러 (Lego Block)
============================================================
- 사용자 지정 5일 로테이션 슬롯:
  * Slot 1 (Day 1): 파우더룸 (cosmania)
  * Slot 2 (Day 2): 여우야 (feko)
  * Slot 3 (Day 3): MBTI & HEALTH (mbticafe)
  * Slot 4 (Day 4): 향수사랑 (perfumelove) / 뷰티매니아 (worrytodream) / 직탐 (workee)
  * Slot 5 (Day 5): 🌟 [크지프 KJIF (korjapif) + 시크먼트 (parisienlook)] 같은 날 묶음 순회!
- 철통 원칙:
  1. 하루 최대 1건 댓글 제한 (Daily Cap: 1)
  2. "꼭 적합하지 않으면 댓글을 절대 남기지 않는다" (Zero Spam, Skip Latch)
  3. 중복 댓글 방지: 이미 댓글을 남긴 article_id 영구 보존
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
HISTORY_FILE = ROOT / "scratch" / "aura_cafe_rotation_history.json"

# 🌟 사용자 맞춤 5개 로테이션 그룹 (Day 5: 크지프 + 시크먼트 묶음)
ROTATION_SLOTS = [
    {
        "slot_id": 1,
        "name": "파우더룸 슬롯",
        "cafe_url_ids": ["cosmania"]
    },
    {
        "slot_id": 2,
        "name": "여우야 슬롯",
        "cafe_url_ids": ["feko"]
    },
    {
        "slot_id": 3,
        "name": "MBTI & HEALTH 슬롯",
        "cafe_url_ids": ["mbticafe"]
    },
    {
        "slot_id": 4,
        "name": "향수사랑 / 뷰티매니아 / 직탐 슬롯",
        "cafe_url_ids": ["perfumelove", "worrytodream", "workee"]
    },
    {
        "slot_id": 5,
        "name": "크지프 KJIF + 시크먼트 (동일 일자 묶음 순회)",
        "cafe_url_ids": ["korjapif", "parisienlook"]
    }
]


class AuraCafeScheduler:
    """💖 Aura 카페 스텔스 로테이션 및 게이트키퍼 스케줄러"""

    def __init__(self, history_path: Path = HISTORY_FILE):
        self.history_path = history_path
        self._ensure_history_file()

    def _ensure_history_file(self):
        """히스토리 파일 생성 및 초기화"""
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.history_path.exists():
            initial_data = {
                "last_post_date": "",
                "total_comments_posted": 0,
                "current_slot_index": 0,
                "cafe_last_posted": {},
                "replied_article_ids": [],
                "post_history": []
            }
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, ensure_ascii=False, indent=2)

    def _read_history(self) -> Dict[str, Any]:
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {
                "last_post_date": "",
                "total_comments_posted": 0,
                "current_slot_index": 0,
                "cafe_last_posted": {},
                "replied_article_ids": [],
                "post_history": []
            }

    def _write_history(self, data: Dict[str, Any]):
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def can_post_today(self, max_daily_posts: int = 1) -> bool:
        """오늘 이미 1건 제한을 채웠는지 검사"""
        data = self._read_history()
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        today_posts = [
            h for h in data.get("post_history", [])
            if h.get("date") == today_str
        ]
        
        if len(today_posts) >= max_daily_posts:
            return False
        return True

    def is_article_already_replied(self, article_id: str) -> bool:
        """해당 게시글에 이미 댓글을 달았는지 검사"""
        data = self._read_history()
        replied_ids = set(str(x) for x in data.get("replied_article_ids", []))
        return str(article_id) in replied_ids

    def get_today_target_cafes(self, all_cafes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        오늘 순번의 슬롯에 해당하는 카페 목록 반환
        (Day 5인 경우: 크지프 KJIF와 시크먼트가 함께 반환됨)
        """
        data = self._read_history()
        slot_idx = data.get("current_slot_index", 0) % len(ROTATION_SLOTS)
        target_slot = ROTATION_SLOTS[slot_idx]
        
        target_url_ids = set(target_slot["cafe_url_ids"])
        today_cafes = [c for c in all_cafes if c["url_id"] in target_url_ids]
        
        # 만약 슬롯 카페 중 하나라도 안 찾아지면 전체 카페 fallback
        return today_cafes if today_cafes else all_cafes

    def advance_slot(self):
        """다음 로테이션 슬롯으로 전진 (순환)"""
        data = self._read_history()
        data["current_slot_index"] = (data.get("current_slot_index", 0) + 1) % len(ROTATION_SLOTS)
        self._write_history(data)

    def record_post_success(
        self,
        cafe_name: str,
        article_id: str,
        title: str,
        reply_text: str
    ):
        """댓글 등록 성공 이력 기록 및 슬롯 전진"""
        data = self._read_history()
        now = datetime.now()
        now_ts = now.timestamp()
        today_str = now.strftime("%Y-%m-%d")

        data["last_post_date"] = today_str
        data["total_comments_posted"] = data.get("total_comments_posted", 0) + 1
        
        if "cafe_last_posted" not in data:
            data["cafe_last_posted"] = {}
        data["cafe_last_posted"][cafe_name] = now_ts

        if "replied_article_ids" not in data:
            data["replied_article_ids"] = []
        if str(article_id) not in data["replied_article_ids"]:
            data["replied_article_ids"].append(str(article_id))

        if "post_history" not in data:
            data["post_history"] = []
        data["post_history"].append({
            "timestamp": now_ts,
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "date": today_str,
            "cafe_name": cafe_name,
            "article_id": str(article_id),
            "title": title,
            "reply_text": reply_text
        })

        # 다음 슬롯으로 전진
        data["current_slot_index"] = (data.get("current_slot_index", 0) + 1) % len(ROTATION_SLOTS)
        self._write_history(data)
