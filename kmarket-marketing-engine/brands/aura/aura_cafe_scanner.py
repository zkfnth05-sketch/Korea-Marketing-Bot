# -*- coding: utf-8 -*-
"""
[Aura] 8대 정예 카페 실시간 스캐너 모듈 (Lego Block)
======================================================
- 역할: 8대 정예 카페에서 최근 5일(120시간) 이내 글을 수집하고,
        AuraCafeFilter(순수 파이썬)를 통해 무결점 사연만 선별
- 8대 카페:
  1. 파우더룸 (cosmania, 10050813)
  2. 여우야 (feko, 10912875)
  3. MBTI & HEALTH (mbticafe, 11856775)
  4. 향수사랑 (perfumelove, 10001688)
  5. 직장인 탐구생활 (workee, 24470111)
  6. 뷰티매니아 (worrytodream, 25389985)
  7. 크지프 KJIF (korjapif, 24573879)
  8. 시크먼트 (parisienlook, 23451561)
"""

import asyncio
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from brands.aura.aura_cafe_filter import AuraCafeFilter

AURA_ELITE_CAFES: List[Dict[str, Any]] = [
    {
        "name": "파우더룸",
        "url_id": "cosmania",
        "club_id": "10050813",
        "keywords": ["소개팅", "자만추", "연애", "썸남", "데이팅앱"],
        "category": "국내 1위 2030 여성 본진"
    },
    {
        "name": "여우야",
        "url_id": "feko",
        "club_id": "10912875",
        "keywords": ["소개팅", "자만추", "연애", "썸남", "데이트", "남친"],
        "category": "230만 뷰티 1위 여성 풀"
    },
    {
        "name": "MBTI & HEALTH",
        "url_id": "mbticafe",
        "club_id": "11856775",
        "keywords": ["소개팅", "연애", "썸남", "썸녀", "애프터", "궁합"],
        "category": "2030 성향/심리 1위"
    },
    {
        "name": "향수사랑",
        "url_id": "perfumelove",
        "club_id": "10001688",
        "keywords": ["소개팅", "데이트", "첫인상", "남친", "연애"],
        "category": "S급 감각/매력녀"
    },
    {
        "name": "직장인 탐구생활",
        "url_id": "workee",
        "club_id": "24470111",
        "keywords": ["소개팅", "연애", "자만추", "외로워", "어플"],
        "category": "2030 직장인 싱글"
    },
    {
        "name": "뷰티매니아",
        "url_id": "worrytodream",
        "club_id": "25389985",
        "keywords": ["소개팅", "데이트", "자만추", "연애", "남친"],
        "category": "여성 뷰티 커뮤니티"
    },
    {
        "name": "크지프 KJIF",
        "url_id": "korjapif",
        "club_id": "24573879",
        "keywords": ["친구", "일본인", "연애", "교류", "외국인"],
        "category": "글로벌 1위 (일본/외국인 여학생)"
    },
    {
        "name": "시크먼트",
        "url_id": "parisienlook",
        "club_id": "23451561",
        "keywords": ["소개팅", "연애", "데이트", "썸남", "썸"],
        "category": "하이엔드 럭셔리 여성"
    }
]

MAX_AGE_HOURS_DEFAULT = 120  # 5일 이내


class AuraCafeScanner:
    """Aura 8대 카페 실시간 스캐너"""

    def __init__(self, filter_instance: Optional[AuraCafeFilter] = None):
        self.c_filter = filter_instance or AuraCafeFilter()
        self.cafes = AURA_ELITE_CAFES

    async def scan_single_cafe(
        self,
        page,
        cafe_info: Dict[str, Any],
        max_age_hours: int = MAX_AGE_HOURS_DEFAULT
    ) -> List[Dict[str, Any]]:
        """단일 카페에 대해 키워드 검색 후 화이트/블랙리스트 필터 통과 글 반환"""
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
            # 1. 시간 검증
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
