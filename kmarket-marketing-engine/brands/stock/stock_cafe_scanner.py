# -*- coding: utf-8 -*-
"""
[StockMaster AI] 5대 정예 주식/재테크 카페 실시간 스캐너 모듈 (Lego Block)
========================================================================
- 역할: 5대 정예 카페에서 최근 5일(120시간) 이내 글을 수집하고,
        StockCafeFilter(순수 파이썬)를 통해 무결점 사연만 선별
- 5대 카페:
  1. 주식투자로 부자되기 (stockschart, 11388106)
  2. 거북이투자법 (turtletrade, 11516084)
  3. 월급쟁이 재테크 연구소 (invest79, 14643031)
  4. 짠돌이카페 (onehundredmillion, 10023478)
  5. 직장인 탐구생활 (workee, 24470111)
"""

import asyncio
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from brands.stock.stock_cafe_filter import StockCafeFilter

STOCK_ELITE_CAFES: List[Dict[str, Any]] = [
    {
        "name": "평생주식카페",
        "url_id": "ustock",
        "club_id": "15112066",
        "keywords": ["물림", "손절", "우량주", "수급", "뇌동매매", "단타", "평단"],
        "category": "국내 1위 122만 주식 종합 커뮤니티"
    },
    {
        "name": "거북이투자법",
        "url_id": "geobuk2",
        "club_id": "26251287",
        "keywords": ["우량주", "손실", "평단", "수급", "장기투자", "스윙", "가치투자"],
        "category": "60만 저평가 우량주/가치투자 본진"
    },
    {
        "name": "주식차트 연구소",
        "url_id": "stockschart",
        "club_id": "11974608",
        "keywords": ["물림", "손절", "우량주", "차트", "매매법", "단타", "수급"],
        "category": "60만 절대수익 우량주 매매법 연구소"
    },
    {
        "name": "달팽이주식카페",
        "url_id": "pointns",
        "club_id": "25873056",
        "keywords": ["장기투자", "노후준비", "우량주", "배당주", "손실", "물림"],
        "category": "30만 노후준비 장기투자 전문 커뮤니티"
    },
    {
        "name": "주식광장",
        "url_id": "hayate1",
        "club_id": "11560463",
        "keywords": ["주식고민", "실전투자", "국내주식", "우량주", "손절", "물림"],
        "category": "28만 실전 투자자 정보 커뮤니티"
    },
    {
        "name": "가치투자연구소",
        "url_id": "vilab",
        "club_id": "11525920",
        "keywords": ["가치투자", "기업분석", "우량주", "재무제표", "장특", "평단"],
        "category": "27만 대한민국 가치투자 1번지"
    },
    {
        "name": "하승훈의 주식투자",
        "url_id": "toptrader7",
        "club_id": "26347614",
        "keywords": ["단타", "스윙", "우량주", "수급", "손절", "물림", "뇌동매매"],
        "category": "16만 실전 탑트레이더 커뮤니티"
    }
]

MAX_AGE_HOURS_DEFAULT = 120  # 5일 이내


class StockCafeScanner:
    """StockMaster AI 7대 메이저 주식 카페 실시간 스캐너"""

    def __init__(self, filter_instance: Optional[StockCafeFilter] = None):
        self.c_filter = filter_instance or StockCafeFilter()
        self.cafes = STOCK_ELITE_CAFES

    async def scan_single_cafe(
        self,
        page,
        cafe_info: Dict[str, Any],
        max_age_hours: int = MAX_AGE_HOURS_DEFAULT
    ) -> List[Dict[str, Any]]:
        """단일 주식 카페에 대해 키워드 검색 후 화이트/블랙리스트 필터 통과 글 반환"""
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
