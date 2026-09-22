# -*- coding: utf-8 -*-
"""
Aura Kin Scanner (🔍 Aura 전용 네이버 지식iN 100개 키워드 실시간 질문 레이더)
========================================================================================
- 브랜드: Aura (2030 AI 데이팅 & 서울 핫플 매칭)
- 역할:
  1. 100대 황금 키워드 기반 지식iN 최신순 실시간 질문 탐색
  2. 질문 ID(docId), 제목, 질문 본문 요약, URL, 등록시간 메타데이터 정밀 수집
  3. Playwright & 영구 세션 기반 100% 안정적 질문 낚아채기
"""

import os
import sys
import re
import time
import json
import random
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright

# UTF-8 콘솔 지원
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("AuraKinScanner")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

try:
    from brands.aura.aura_kin_keywords_100 import get_all_100_keywords
except ImportError:
    from aura_kin_keywords_100 import get_all_100_keywords


class AuraKinScanner:
    """💖 Aura 전용 네이버 지식iN 100개 키워드 실시간 질문 스캐너"""

    BRAND = "aura"
    SESSION_PATH = CURRENT_DIR / "naver_session.json"

    def __init__(self):
        self.all_keywords = get_all_100_keywords()

    async def async_scan_questions(self, sample_keywords_count: int = 3, max_questions: int = 5) -> List[Dict[str, Any]]:
        """100개 키워드 중 무작위 샘플링하여 실시간 질문 스캔"""
        selected_keywords = random.sample(self.all_keywords, min(sample_keywords_count, len(self.all_keywords)))
        collected = []
        seen_doc_ids = set()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )

            # 네이버 세션 쿠키 탑재
            if self.SESSION_PATH.exists():
                try:
                    with open(self.SESSION_PATH, "r", encoding="utf-8") as f:
                        sdata = json.load(f)
                        cookies = sdata.get("cookies", [])
                        if cookies:
                            await context.add_cookies(cookies)
                except Exception as ex:
                    logger.debug(f"세션 로드 예외: {ex}")

            page = await context.new_page()

            for kw in selected_keywords:
                try:
                    import urllib.parse
                    url = f"https://kin.naver.com/search/list.naver?query={urllib.parse.quote(kw)}&sort=date"
                    await page.goto(url, wait_until="domcontentloaded", timeout=12000)

                    items = await page.query_selector_all("ul.basic1 > li")
                    for li in items:
                        title_el = await li.query_selector("dt a")
                        if not title_el:
                            continue

                        title = (await title_el.inner_text()).strip()
                        href = await title_el.get_attribute("href") or ""
                        if "docId=" not in href:
                            continue

                        doc_id_match = re.search(r'docId=(\d+)', href)
                        doc_id = doc_id_match.group(1) if doc_id_match else ""

                        if not doc_id or doc_id in seen_doc_ids:
                            continue
                        seen_doc_ids.add(doc_id)

                        # 요약 및 본문
                        desc_el = await li.query_selector("dd:not(.txt_block)")
                        desc = (await desc_el.inner_text()).strip() if desc_el else ""

                        date_el = await li.query_selector(".txt_date")
                        date_str = (await date_el.inner_text()).strip() if date_el else ""

                        item = {
                            "brand": "aura",
                            "doc_id": doc_id,
                            "keyword": kw,
                            "title": title,
                            "content": desc,
                            "url": href,
                            "scanned_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "date_text": date_str,
                            "status": "scanned"
                        }
                        collected.append(item)
                        if len(collected) >= max_questions:
                            break

                    await page.wait_for_timeout(300)
                except Exception as ex:
                    logger.warning(f"키워드 [{kw}] 지식iN 스캔 예외: {ex}")

                if len(collected) >= max_questions:
                    break

            await browser.close()

        logger.info(f"🔍 [Aura 지식iN 레이더] {len(collected)}개 질문 포착 완료 (샘플: {', '.join(selected_keywords)})")
        return collected

    def scan_recent_questions(self, sample_keywords_count: int = 3, max_questions: int = 5) -> List[Dict[str, Any]]:
        """동기 인터페이스 래퍼"""
        return asyncio.run(self.async_scan_questions(sample_keywords_count, max_questions))


if __name__ == "__main__":
    scanner = AuraKinScanner()
    items = scanner.scan_recent_questions(sample_keywords_count=2, max_questions=3)
    for q in items:
        print(f"[{q['keyword']}] {q['title']}")
        print(f"  URL: {q['url']}")
        print(f"  내용: {q['content'][:70]}...\n")
