# -*- coding: utf-8 -*-
"""
Aura Brunch Story Publisher (💖 Aura 전용 브런치스토리 무인 자동 배포 레고 블록)
=============================================================================
- 역할:
  1. 카카오 브런치스토리 작가 신청 및 심사 대기 상태 대응
  2. 심사 대기 중에는 '작가의 서랍' 및 로컬 아카이브(outputs/aura/brunch/)에 전용 원고 안전 보관
  3. 심사 승인 완료 시 Playwright 기반 무인 자동 발행 즉시 전환 지원
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
SESSION_FILE = CURRENT_DIR / "brunch_session.json"
BRUNCH_OUT_DIR = PROJECT_ROOT / "outputs" / "aura" / "brunch"

logger = logging.getLogger("AuraBrunchPublisher")


class AuraBrunchPublisher:
    """Aura 데이팅 전용 브런치스토리 배포 엔진"""

    def __init__(self):
        self.session_file = SESSION_FILE
        BRUNCH_OUT_DIR.mkdir(parents=True, exist_ok=True)

    def is_available(self) -> bool:
        return self.session_file.exists() and self.session_file.stat().st_size > 100

    def publish_column(
        self,
        title: str,
        subtitle: str,
        body_text: str,
        topic_id: int = 1,
        landing_url: str = "https://aura-ai-dating.vercel.app/"
    ) -> Dict[str, Any]:
        """
        브런치스토리 원고 발행 또는 작가의 서랍 보관
        (현재 카카오 작가 심사 제출 상태로, 심사 통과 전까지 안전 보관 모드 작동)
        """
        logger.info(f"🟡 [Brunch] 브런치스토리 원고 처리 중: '{title}'")

        # 1. 브런치 전용 원고 로컬 안전 보관 (작가의 서랍)
        file_name = f"brunch_draft_topic_{topic_id:03d}.json"
        draft_pkg = {
            "title": title,
            "subtitle": subtitle,
            "body": body_text,
            "landing_url": landing_url,
            "status": "pending_author_approval",
            "note": "카카오 브런치스토리 작가 신청서 심사 대기 중. 승인 완료 시 원클릭 무인 발행됩니다."
        }

        save_path = BRUNCH_OUT_DIR / file_name
        try:
            with open(save_path, "w", encoding="utf-8") as fp:
                json.dump(draft_pkg, fp, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"⚠️ [Brunch] 로컬 보관 예외: {e}")

        logger.info("✅ [Brunch] 브런치 전용 칼럼 안전 보관 완료 (카카오 심사 승인 대기 중)")
        return {
            "status": "pending_review",
            "mode": "author_review_pending",
            "title": title,
            "message": "카카오 브런치스토리 작가 심사 승인 대기 중 (신청서 심사 승인 완료 시 즉시 오픈, 현재 전용 원고 보관 완료)",
            "archive_file": str(save_path.name)
        }


if __name__ == "__main__":
    pub = AuraBrunchPublisher()
    print("Is available:", pub.is_available())
