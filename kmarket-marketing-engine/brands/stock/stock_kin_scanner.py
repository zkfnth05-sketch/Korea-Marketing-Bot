# -*- coding: utf-8 -*-
"""
Stock Kin Scanner (🔍 Stock Master 전용 네이버 지식iN 실시간 주식 질문 레이더)
========================================================================================
- 브랜드: Stock Master (2030 AI 주식 퀀트 & 종목 진단)
- 역할:
  1. 100% 대한민국 국내 주식(코스피/코스닥) 핀포인트 키워드 기반 실시간 질문 탐색
  2. 3대 초신선 골든 필터 적용:
     - 📅 작성일: 최근 24~48시간 (오늘~어제, max_days=2)
     - 💬 답변수: 기존 답변 0개 ~ 최대 4개 이하
     - 🚫 내 계정(zkfnth02 등) 중복 답변 제외
  3. Playwright & 네이버 세션 기반 안정적 질문 크롤링
"""

import os
import sys
import re
import time
import json
import random
import logging
import asyncio
import urllib.parse
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("StockKinScanner")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

try:
    from brands.stock.stock_kin_keywords_100 import get_all_domestic_stock_keywords
except ImportError:
    from stock_kin_keywords_100 import get_all_domestic_stock_keywords


class StockKinScanner:
    """📈 Stock Master 전용 네이버 지식iN 실시간 주식 질문 스캐너"""

    BRAND = "stock"
    SESSION_PATH = CURRENT_DIR / "naver_session.json"

    def __init__(self):
        self.all_keywords = get_all_domestic_stock_keywords()

    @staticmethod
    def is_within_days(date_str: str, max_days: int = 2) -> bool:
        """최근 max_days일(기본: 최근 24~48시간 오늘~어제) 이내 질문인지 엄격 검사"""
        if not date_str:
            return False
        date_str = date_str.strip()
        if any(x in date_str for x in ["방금", "분 전", "시간 전", "어제"]):
            return True
        match = re.search(r"(\d{4})\.(\d{1,2})\.(\d{1,2})", date_str)
        if match:
            y, m, d = int(match.group(1)), int(match.group(2)), int(match.group(3))
            post_date = datetime(y, m, d)
            now = datetime.now()
            diff = (now - post_date).days
            return 0 <= diff <= max_days
        return False

    @staticmethod
    def extract_answer_count(txt_block: str) -> int:
        """답변 수 추출"""
        match = re.search(r"답변수\s*(\d+)", txt_block)
        if match:
            return int(match.group(1))
        return 0

    async def async_scan_questions(
        self,
        sample_keywords_count: int = 3,
        max_questions: int = 5,
        max_days: int = 2,
        max_answers: int = 4,
        custom_keywords: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        초신선 골든 필터 기반 실시간 주식 질문 스캔:
        1. 작성일: 최근 24~48시간 (오늘~어제, max_days=2)만 허용
        2. 답변수: 0개 ~ 최대 4개 이하만 선별
        3. 내 답변 제외: 본인 계정 답변 완료글 배제
        """
        if custom_keywords:
            selected_keywords = custom_keywords
        else:
            selected_keywords = random.sample(self.all_keywords, min(sample_keywords_count, len(self.all_keywords)))

        collected = []
        seen_doc_ids = set()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )

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

                        doc_id_match = re.search(r"docId=(\d+)", href)
                        doc_id = doc_id_match.group(1) if doc_id_match else ""

                        if not doc_id or doc_id in seen_doc_ids:
                            continue

                        # 날짜 추출
                        date_el = await li.query_selector("dd.txt_inline") or await li.query_selector(".txt_date")
                        date_str = (await date_el.inner_text()).strip() if date_el else ""

                        # 1. 작성일 필터 (최근 2일 이내: 오늘~어제)
                        if not self.is_within_days(date_str, max_days=max_days):
                            continue

                        # 부가 정보 (답변수 및 답변자)
                        txt_block_el = await li.query_selector("dd.txt_block")
                        txt_block = (await txt_block_el.inner_text()).strip() if txt_block_el else ""

                        # 2. 내 계정 답변 중복 배제 (zkfn 등)
                        if "zkfn" in txt_block.lower():
                            continue

                        # 3. 답변수 상한 필터 (최대 4개 이하)
                        ans_count = self.extract_answer_count(txt_block)
                        if ans_count > max_answers:
                            continue

                        seen_doc_ids.add(doc_id)

                        # 요약 본문
                        desc_el = await li.query_selector("dd:not(.txt_block):not(.txt_inline):not(.tag_area)")
                        desc = (await desc_el.inner_text()).strip() if desc_el else ""

                        item = {
                            "brand": "stock",
                            "doc_id": doc_id,
                            "keyword": kw,
                            "title": title,
                            "content": desc,
                            "url": href,
                            "scanned_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "date_text": date_str,
                            "answer_count": ans_count,
                            "status": "scanned"
                        }
                        collected.append(item)
                        if len(collected) >= max_questions:
                            break

                    await page.wait_for_timeout(200)
                except Exception as ex:
                    logger.warning(f"Stock 키워드 [{kw}] 지식iN 스캔 예외: {ex}")

                if len(collected) >= max_questions:
                    break

            await browser.close()

        logger.info(f"🔍 [Stock 지식iN 레이더] {len(collected)}개 질문 포착 완료 (샘플: {', '.join(selected_keywords[:3])})")
        return collected

    def scan_recent_questions(
        self,
        sample_keywords_count: int = 3,
        max_questions: int = 5,
        max_days: int = 2,
        max_answers: int = 4,
        custom_keywords: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """동기 인터페이스 래퍼"""
        return asyncio.run(self.async_scan_questions(
            sample_keywords_count=sample_keywords_count,
            max_questions=max_questions,
            max_days=max_days,
            max_answers=max_answers,
            custom_keywords=custom_keywords
        ))

    @staticmethod
    def fetch_question_detail_content(url: str) -> str:
        """질문 상세 페이지(URL)에 직접 접속하여 질문자가 쓴 진짜 본문(.questionDetail)을 100% 정밀 추출"""
        if not url:
            return ""
        try:
            import urllib.request
            from bs4 import BeautifulSoup
            clean_url = url.split("&answerNo=")[0] if "&answerNo=" in url else url
            req = urllib.request.Request(
                clean_url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
            )
            with urllib.request.urlopen(req, timeout=6) as response:
                html = response.read().decode("utf-8", errors="ignore")
            soup = BeautifulSoup(html, "html.parser")
            for sel in [".questionDetail", ".c-heading__content", ".question-content", "div._contentWrap .questionDetail", "div.c-heading._questionContentsArea"]:
                el = soup.select_one(sel)
                if el and el.get_text(strip=True):
                    return el.get_text("\n", strip=True)
            for p in soup.select(".c-heading p, .end_question p"):
                t = p.get_text(strip=True)
                if len(t) > 20:
                    return t
        except Exception as e:
            logger.warning(f"Stock 질문 상세 본문 추출 예외 ({url}): {e}")
        return ""


if __name__ == "__main__":
    scanner = StockKinScanner()
    items = scanner.scan_recent_questions(sample_keywords_count=3, max_questions=5)
    for q in items:
        print(f"[{q['keyword']}] {q['title']}")
        print(f"  작성일: {q['date_text']} | 답변수: {q['answer_count']}개 | URL: {q['url']}\n")
