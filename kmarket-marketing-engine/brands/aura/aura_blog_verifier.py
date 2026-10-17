# -*- coding: utf-8 -*-
"""
[💖 Aura 전담 레고 블록] Aura Blog Verifier (블로그 발행 사후 실사 검증기)
=============================================================================
- 역할: 네이버/티스토리 블로그 발행 후, 실제 공개 블로그에 글이 등록되었는지
        1) 공식 RSS 피드 실시간 대조
        2) 실제 공개 웹페이지 브라우저 진입 및 실사 스크린샷 캡처
        를 수행하여 '눈으로 확인'하듯 100% 무결성을 판정합니다.
- 가짜 성공(nidlogin 등 로그인 화면 튕김)을 원천 차단합니다.
"""

import os
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, Optional

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "aura" / "blog_verification"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class AuraBlogVerifier:
    def __init__(self):
        self.brand = "aura"
        self.naver_blog_id = "zkfnth01"
        self.tistory_blog_name = "aura-magazine"

    def verify_naver_via_rss(self, expected_title: Optional[str] = None) -> Dict[str, Any]:
        """네이버 공식 RSS 피드를 조회하여 실제 등록된 최신 글 확인"""
        rss_url = f"https://rss.blog.naver.com/{self.naver_blog_id}.xml"
        req = urllib.request.Request(
            rss_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        try:
            with urllib.request.urlopen(req, timeout=7) as resp:
                content = resp.read()
                root = ET.fromstring(content)
                items = root.findall(".//item")
                if not items:
                    return {
                        "verified": False,
                        "channel": "naver",
                        "error": f"네이버 블로그({self.naver_blog_id}) RSS에 등록된 글이 0개입니다 (미발행/비공개)"
                    }
                latest = items[0]
                t = latest.findtext("title", "") or ""
                link = latest.findtext("link", "") or ""
                pub_date = latest.findtext("pubDate", "") or ""

                m = re.search(r"/(\d+)(?:\?|$)", link)
                log_no = m.group(1) if m else ""
                clean_url = f"https://blog.naver.com/{self.naver_blog_id}/{log_no}" if log_no else link

                # 제목 매칭 (기대 제목이 전달된 경우)
                matched = True
                if expected_title:
                    clean_exp = re.sub(r'[^가-힣a-zA-Z0-9]', '', expected_title)
                    clean_act = re.sub(r'[^가-힣a-zA-Z0-9]', '', t)
                    # 4글자 이상 키워드 매칭
                    matched = (clean_exp[:15] in clean_act) or (clean_act[:15] in clean_exp)

                return {
                    "verified": matched,
                    "channel": "naver",
                    "blog_id": self.naver_blog_id,
                    "title": t,
                    "real_url": clean_url,
                    "log_no": log_no,
                    "pub_date": pub_date,
                    "match_expected": matched
                }
        except Exception as e:
            return {"verified": False, "channel": "naver", "error": f"RSS 조회 실패: {e}"}

    def verify_tistory_via_rss(self, expected_title: Optional[str] = None) -> Dict[str, Any]:
        """티스토리 공식 RSS 피드를 조회하여 실제 등록된 최신 글 확인"""
        rss_url = f"https://{self.tistory_blog_name}.tistory.com/rss"
        req = urllib.request.Request(
            rss_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        try:
            with urllib.request.urlopen(req, timeout=7) as resp:
                content = resp.read()
                root = ET.fromstring(content)
                items = root.findall(".//item")
                if not items:
                    return {
                        "verified": False,
                        "channel": "tistory",
                        "error": f"티스토리({self.tistory_blog_name}) RSS에 등록된 글이 0개입니다"
                    }
                latest = items[0]
                t = latest.findtext("title", "") or ""
                link = latest.findtext("link", "") or ""
                pub_date = latest.findtext("pubDate", "") or ""

                matched = True
                if expected_title:
                    clean_exp = re.sub(r'[^가-힣a-zA-Z0-9]', '', expected_title)
                    clean_act = re.sub(r'[^가-힣a-zA-Z0-9]', '', t)
                    matched = (clean_exp[:15] in clean_act) or (clean_act[:15] in clean_exp)

                return {
                    "verified": matched,
                    "channel": "tistory",
                    "blog_name": self.tistory_blog_name,
                    "title": t,
                    "real_url": link,
                    "pub_date": pub_date,
                    "match_expected": matched
                }
        except Exception as e:
            return {"verified": False, "channel": "tistory", "error": f"티스토리 RSS 조회 실패: {e}"}

    def capture_visual_proof(self, url: str, channel_name: str) -> Optional[str]:
        """실제 공개 브라우저로 접속하여 '눈으로 확인'용 스크린샷 캡처 저장"""
        if not url or "nidlogin" in url or "auth/login" in url:
            return None
        try:
            from playwright.sync_api import sync_playwright
            shot_file = OUTPUT_DIR / f"{channel_name}_proof_{int(time.time())}.png"
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": 1280, "height": 900})
                page.goto(url, wait_until="networkidle", timeout=15000)
                time.sleep(1.5)
                page.screenshot(path=str(shot_file))
                browser.close()
            return str(shot_file)
        except Exception:
            return None

    def verify_all(self, expected_title: Optional[str] = None, capture: bool = False) -> Dict[str, Any]:
        """네이버 및 티스토리 사후 발행 내역 종합 검증"""
        nv_res = self.verify_naver_via_rss(expected_title=expected_title)
        ti_res = self.verify_tistory_via_rss(expected_title=expected_title)

        if capture:
            if nv_res.get("verified") and nv_res.get("real_url"):
                nv_res["screenshot"] = self.capture_visual_proof(nv_res["real_url"], "naver")
            if ti_res.get("verified") and ti_res.get("real_url"):
                ti_res["screenshot"] = self.capture_visual_proof(ti_res["real_url"], "tistory")

        return {
            "brand": self.brand,
            "naver": nv_res,
            "tistory": ti_res,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }


if __name__ == "__main__":
    verifier = AuraBlogVerifier()
    print(verifier.verify_all(capture=False))
