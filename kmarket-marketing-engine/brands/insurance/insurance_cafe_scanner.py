# -*- coding: utf-8 -*-
"""
[보험 리밸런스] 5대 정예 맘/가계부/재테크 카페 실시간 스캐너 모듈 (Lego Block)
============================================================================
- 역할: 5대 정예 카페에서 최근 5일(120시간) 이내 글을 수집하고,
        InsuranceCafeFilter(순수 파이썬)를 통해 무결점 사연만 선별
- 5대 카페:
  1. 맘스홀릭 베이비 (imsanbu, 10094499)
  2. 레몬테라스 (remonterrace, 10298136)
  3. 짠돌이카페 (onehundredmillion, 10023478)
  4. 월급쟁이 재테크 연구소 (invest79, 14643031)
  5. 파우더룸 (cosmania, 10050813)
"""

import asyncio
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from brands.insurance.insurance_cafe_filter import InsuranceCafeFilter

INSURANCE_ELITE_CAFES: List[Dict[str, Any]] = [
    {
        "name": "보험읽어주는카페",
        "url_id": "dnsjejrjfwm",
        "club_id": "12922121",
        "keywords": ["보험료", "보험리모델링", "증권분석", "실비", "종합보험", "특약", "암보험", "해지"],
        "category": "국내 1위 순수 보험 리모델링/상담 전문 카페 (10.6만)"
    },
    {
        "name": "보찾사 (보험을찾는사람들)",
        "url_id": "ipadno1",
        "club_id": "20082867",
        "keywords": ["보험료", "보험고민", "실손", "암보험", "특약", "의료실비", "종신보험"],
        "category": "국내 1위 실비/암/종신 비교 전문 카페 (10.1만)"
    },
    {
        "name": "갑상선암 환우회 (갑상선포럼)",
        "url_id": "thyroidcancers",
        "club_id": "13005023",
        "keywords": ["보험", "실비", "진단비", "수술비", "특약", "유병자", "청구", "암보험"],
        "category": "국내 1위 갑상선암 환우회 (33.3만, 실손/수술비 분쟁)"
    }
]

MAX_AGE_HOURS_DEFAULT = 120  # 5일 이내


class InsuranceCafeScanner:
    """보험 리밸런스 5대 맘/가계부/재테크 카페 실시간 스캐너"""

    def __init__(self, filter_instance: Optional[InsuranceCafeFilter] = None):
        self.c_filter = filter_instance or InsuranceCafeFilter()
        self.cafes = INSURANCE_ELITE_CAFES

    async def scan_single_cafe(
        self,
        page,
        cafe_info: Dict[str, Any],
        max_age_hours: int = MAX_AGE_HOURS_DEFAULT
    ) -> List[Dict[str, Any]]:
        """단일 보험 관련 카페에 대해 키워드 검색 후 화이트/블랙리스트 필터 통과 글 반환"""
        name = cafe_info["name"]
        club_id = cafe_info["club_id"]
        keywords = cafe_info["keywords"]
        
        seen_ids = set()
        all_items = []

        for kw in keywords:
            captured = []

            async def on_res(res):
                if "cafe-search-api" in res.url:
                    try:
                        d = await res.json()
                        captured.append(d)
                    except Exception:
                        pass

            page.on("response", on_res)
            search_url = f"https://m.cafe.naver.com/ca-fe/web/cafes/{club_id}/search?q={kw}&mi=0&ta=SUBJECT&pc=ALL&od=NEW"
            try:
                await page.goto(search_url, wait_until="networkidle", timeout=16000)
                await page.wait_for_timeout(1000)
            except Exception:
                pass
            finally:
                page.remove_listener("response", on_res)

            if captured:
                for c_data in captured:
                    items = c_data.get("result", {}).get("articleList", [])
                    for it in items:
                        item = it.get("item", {})
                        a_id = item.get("articleId")
                        if not a_id or a_id in seen_ids:
                            continue
                        seen_ids.add(a_id)
                        all_items.append(item)

        now = datetime.now()
        passed_posts = []

        for item in all_items:
            # 1. 시간 검증 (5일 이내)
            add_date_str = item.get("addDate", "")
            current_sec = item.get("currentSecTime", "")
            age_hours = 9999

            if add_date_str:
                try:
                    p_dt = datetime.fromisoformat(add_date_str)
                    age_hours = (now - p_dt).total_seconds() / 3600
                except Exception:
                    pass
            elif current_sec:
                m_days = re.search(r"(\d+)일", current_sec)
                if m_days:
                    age_hours = int(m_days.group(1)) * 24
                elif "시간" in current_sec or "분" in current_sec:
                    age_hours = 1

            if age_hours > max_age_hours:
                continue

            raw_sub = item.get("subject", "")
            raw_sum = item.get("summary", "")
            subject = re.sub(r"<[^>]+>", "", raw_sub).strip()
            summary = re.sub(r"<[^>]+>", "", raw_sum).strip()
            writer = item.get("writerInfo", {}).get("nickname", item.get("writerNickname", ""))
            article_id = item.get("articleId", "")

            if not subject:
                continue

            # 2. 순수 파이썬 화이트리스트 / 블랙리스트 평가
            score, is_passed, reason, matched_w, matched_b = self.c_filter.evaluate_post(subject, summary, name)

            if is_passed:
                # 🕒 최신글 가중치 (Recency Bonus: 최대 +15점)
                recency_bonus = 0
                if age_hours <= 6:
                    recency_bonus = 15
                elif age_hours <= 12:
                    recency_bonus = 12
                elif age_hours <= 24:
                    recency_bonus = 8
                elif age_hours <= 48:
                    recency_bonus = 4

                final_score = min(100, score + recency_bonus)
                age_str = current_sec if current_sec else f"{age_hours:.1f}시간 전"
                bonus_desc = f" (최신성 +{recency_bonus}점 가산)" if recency_bonus > 0 else ""

                passed_posts.append({
                    "cafe_name": name,
                    "url_id": cafe_info.get("url_id", ""),
                    "club_id": club_id,
                    "article_id": article_id,
                    "title": subject,
                    "summary": summary,
                    "writer": writer,
                    "score": final_score,
                    "base_score": score,
                    "recency_bonus": recency_bonus,
                    "reason": f"{reason}{bonus_desc}",
                    "matched_w": matched_w,
                    "age_hours": age_hours,
                    "age_str": age_str,
                    "add_date": add_date_str
                })

        # 점수 높은 순 정렬 (동점 시 더 최신 글이 1순위)
        passed_posts.sort(key=lambda x: (x["score"], -x["age_hours"]), reverse=True)
        return passed_posts
