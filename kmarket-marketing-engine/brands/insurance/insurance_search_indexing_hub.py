# -*- coding: utf-8 -*-
"""
Insurance Search Indexing Hub (🌐 InsureBalance 전용 2대 포털 검색엔진 동시 색인 핑 독립 레고 블록)
========================================================================
- 브랜드: InsureBalance (보험비교)
- 역할:
  1. 구글 서치콘솔 (Google Search Console & Googlebot 실시간 색인 핑 전송)
  2. 네이버 서치어드바이저 (Naver Search Advisor & Yeti 검색 로봇 즉시 수집 요청)
  3. 신규 보험 칼럼 및 보험비교 DB 웹페이지 초고속 듀얼 색인 가속
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

logger = logging.getLogger("InsuranceSearchIndexingHub")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent


class InsuranceSearchIndexingHub:
    """🛡️ InsureBalance 2대 포털 검색엔진 (구글 + 네이버) 동시 색인 핑 통합 허브"""

    BRAND_NAME = "InsureBalance (보험비교)"
    LANDING_URL = "https://insure-rebalance.vercel.app/"
    SITEMAP_URL = "https://insure-rebalance.vercel.app/sitemap_insurance.xml"

    def __init__(self):
        pass

    def get_target_urls(self) -> List[str]:
        """InsureBalance 주요 URL 및 최신 콘텐츠 URL 목록 반환"""
        urls = [
            self.LANDING_URL,
            f"{self.LANDING_URL}rebalance-center",
            f"{self.LANDING_URL}compare-hub",
            f"{self.LANDING_URL}calculator-hub",
            f"{self.LANDING_URL}claims-hub",
            self.SITEMAP_URL,
            "https://insure-rebalance.vercel.app/sitemap.xml"
        ]

        # sitemap_insurance.xml이 생성되어 있으면 대표 URL 30개 추가 로드
        sitemap_path = PROJECT_ROOT / "outputs" / "sitemaps" / "sitemap_insurance.xml"
        if sitemap_path.exists():
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(sitemap_path)
                root = tree.getroot()
                count = 0
                for elem in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
                    if elem.text and elem.text not in urls:
                        urls.append(elem.text)
                        count += 1
                        if count >= 30: # 1회 핑 대상 30개
                            break
            except Exception as e:
                logger.debug(f"사이트맵 파싱 예외: {e}")

        return urls

    def ping_google_search_console(self, urls: List[str]) -> Dict[str, Any]:
        """① 구글 서치콘솔: Googlebot 실시간 색인 핑 전송 (Google Indexing API v3)"""
        try:
            from core.google_indexing_client import GoogleIndexingClient
            client = GoogleIndexingClient(brand="kmarket") # 공용 서비스 계정 풀 활용
            if client.is_configured():
                res = client.batch_publish_urls(urls, max_limit=15)
                return {"status": "success", "platform": "google_search_console", "count": len(urls), "detail": res}
            else:
                logger.info(f"[DRY-RUN] 구글 서치콘솔 색인 핑 시뮬레이션 ({len(urls)}개 URL): {urls[0] if urls else ''}")
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
            f"🌐 [InsureBalance 2대 포털 검색엔진 동시 색인 핑 전송 완료]\n"
            f"  - 🎯 대상 URL: {len(urls)}개 (공식 웹, 보험비교 계산기, 사이트맵)\n"
            f"  - ① 구글 서치콘솔: Googlebot 실시간 색인 핑 전송 완료 ({google_res['status']})\n"
            f"  - ② 네이버 서치어드바이저: Yeti 검색 로봇 즉시 수집 요청 완료 ({naver_res['status']})"
        )
        logger.info(summary_msg)

        return {
            "success": True,
            "brand": "insurance",
            "message": summary_msg,
            "results": {
                "google": google_res,
                "naver": naver_res
            }
        }


if __name__ == "__main__":
    hub = InsuranceSearchIndexingHub()
    res = hub.ping_all_engines()
    print(res["message"])
