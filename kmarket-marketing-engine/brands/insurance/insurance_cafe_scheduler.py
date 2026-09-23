# -*- coding: utf-8 -*-
"""
[보험 리밸런스] 5대 정예 맘/가계부/재테크 카페 스텔스 로테이션 스케줄러 (Lego Block)
====================================================================================
- 사용자 지정 5일 로테이션 슬롯:
  * Slot 1 (Day 1): 맘스홀릭 베이비 (imsanbu)
  * Slot 2 (Day 2): 레몬테라스 (remonterrace)
  * Slot 3 (Day 3): 짠돌이카페 (onehundredmillion)
  * Slot 4 (Day 4): 월급쟁이 재테크 연구소 (invest79)
  * Slot 5 (Day 5): 파우더룸 (cosmania)
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
HISTORY_FILE = ROOT / "scratch" / "insurance_cafe_rotation_history.json"

ROTATION_SLOTS = [
    {
        "slot_id": 1,
        "name": "보험읽어주는카페 슬롯",
        "cafe_url_ids": ["dnsjejrjfwm"]
    },
    {
        "slot_id": 2,
        "name": "갑상선암 환우회 슬롯",
        "cafe_url_ids": ["thyroidcancers"]
    },
    {
        "slot_id": 3,
        "name": "보찾사 (보험을찾는사람들) 슬롯",
        "cafe_url_ids": ["ipadno1"]
    }
]


class InsuranceCafeScheduler:
    """🛡️ 보험 리밸런스 카페 스텔스 로테이션 및 게이트키퍼 스케줄러"""

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
        """오늘 순번의 슬롯에 해당하는 카페 목록 반환"""
        data = self._read_history()
        slot_idx = data.get("current_slot_index", 0) % len(ROTATION_SLOTS)
        target_slot = ROTATION_SLOTS[slot_idx]
        
        target_url_ids = set(target_slot["cafe_url_ids"])
        today_cafes = [c for c in all_cafes if c["url_id"] in target_url_ids]
        
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
        """댓글 등록 성공 기록 및 상태 저장"""
        data = self._read_history()
        now = datetime.now()
        now_ts = time.time()
        today_str = now.strftime("%Y-%m-%d")
        dt_str = now.strftime("%Y-%m-%d %H:%M:%S")

        data["last_post_date"] = today_str
        data["total_comments_posted"] = data.get("total_comments_posted", 0) + 1
        data["cafe_last_posted"][cafe_name] = now_ts

        replied_ids = set(str(x) for x in data.get("replied_article_ids", []))
        replied_ids.add(str(article_id))
        data["replied_article_ids"] = list(replied_ids)

        post_entry = {
            "timestamp": now_ts,
            "datetime": dt_str,
            "date": today_str,
            "cafe_name": cafe_name,
            "article_id": str(article_id),
            "title": title,
            "reply_text": reply_text
        }
        data.setdefault("post_history", []).append(post_entry)

        data["current_slot_index"] = (data.get("current_slot_index", 0) + 1) % len(ROTATION_SLOTS)
        self._write_history(data)
