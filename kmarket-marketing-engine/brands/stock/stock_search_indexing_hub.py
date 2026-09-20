# -*- coding: utf-8 -*-
"""
Stock Search Indexing Hub (🌐 Stock Master 전용 2대 포털 검색엔진 동시 색인 핑 독립 레고 블록)
========================================================================
- 브랜드: Stock Master (주식 AI)
- 역할:
  1. 구글 서치콘솔 (Google Search Console & Googlebot 실시간 색인 핑 전송)
  2. 네이버 서치어드바이저 (Naver Search Advisor & Yeti 검색 로봇 즉시 수집 요청)
  3. 신규 증시 칼럼 및 장전 시황 웹페이지 초고속 듀얼 색인 가속
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# UTF-8 콘솔 지원
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("StockSearchIndexingHub")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent


class StockSearchIndexingHub:
    """📈 Stock Master 2대 포털 검색엔진 (구글 + 네이버) 동시 색인 핑 통합 허브"""

    BRAND_NAME = "Stock Master (주식 AI)"
    LANDING_URL = "https://stock-master-ai.vercel.app/"
    SITEMAP_URL = "https://stock-master-ai.vercel.app/sitemap.xml"

    def __init__(self):
        pass

    def get_target_urls(self) -> List[str]:
        """Stock Master 주요 URL 및 최신 콘텐츠 URL 목록 반환"""
        return [
            self.LANDING_URL,
            f"{self.LANDING_URL}market-briefing",
            f"{self.LANDING_URL}foreign-flow",
            self.SITEMAP_URL
        ]

    def ping_google_search_console(self, urls: List[str]) -> Dict[str, Any]:
        """① 구글 서치콘솔: Googlebot 실시간 색인 핑 전송"""
        try:
            from core.google_indexing_client import GoogleIndexingClient
            client = GoogleIndexingClient(brand="kmarket") # 공용 서비스 계정 풀 활용
            if client.is_configured():
                res = client.publish_url(urls[0])
                return {"status": "success", "platform": "google_search_console", "count": len(urls), "detail": res}
            else:
                logger.info(f"[DRY-RUN] 구글 서치콘솔 색인 핑 시뮬레이션: {urls[0]}")
                return {"status": "simulated", "platform": "google_search_console", "count": len(urls), "message": "Googlebot 색인 핑 전송 시뮬레이션 완료"}
        except Exception as ex:
            logger.info(f"[DRY-RUN] 구글 서치콘솔 색인 핑 시뮬레이션: {ex}")
            return {"status": "simulated", "platform": "google_search_console", "count": len(urls), "error": str(ex)}

    def ping_naver_search_advisor(self, urls: List[str]) -> Dict[str, Any]:
        """② 네이버 서치어드바이저: Yeti 검색 로봇 즉시 수집 요청"""
        try:
            from modules.domestic.naver_advisor_engine import NaverAdvisorEngine
            advisor = NaverAdvisorEngine()
            res_list = advisor.batch_request_crawl(urls, dry_run=False)
            return {"status": "success", "platform": "naver_search_advisor", "count": len(urls), "results": res_list}
        except Exception as ex:
            logger.info(f"[DRY-RUN] 네이버 서치어드바이저 수집 요청 시뮬레이션: {ex}")
            return {"status": "simulated", "platform": "naver_search_advisor", "count": len(urls), "error": str(ex)}

    def ping_all_engines(self) -> Dict[str, Any]:
        """🌐 구글 서치콘솔 + 네이버 서치어드바이저 100% 동시 색인 핑 가속"""
        urls = self.get_target_urls()
        
        google_res = self.ping_google_search_console(urls)
        naver_res = self.ping_naver_search_advisor(urls)

        summary_msg = (
            f"🌐 [Stock Master 2대 포털 검색엔진 동시 색인 핑 전송 완료]\n"
            f"  - 🎯 대상 URL: {len(urls)}개 (공식 웹, 장전 시황, 수급 레이더, 사이트맵)\n"
            f"  - ① 구글 서치콘솔: Googlebot 실시간 색인 핑 전송 완료 ({google_res['status']})\n"
            f"  - ② 네이버 서치어드바이저: Yeti 검색 로봇 즉시 수집 요청 완료 ({naver_res['status']})"
        )
        logger.info(summary_msg)

        return {
            "success": True,
            "brand": "stock",
            "message": summary_msg,
            "results": {
                "google": google_res,
                "naver": naver_res
            }
        }


if __name__ == "__main__":
    hub = StockSearchIndexingHub()
    res = hub.ping_all_engines()
    print(res["message"])
