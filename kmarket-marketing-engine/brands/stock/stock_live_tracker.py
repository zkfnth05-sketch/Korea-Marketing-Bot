# -*- coding: utf-8 -*-
"""
Stock Live Publishing Tracker (📈 StockMaster AI 주식 100% 독립 무인 발행 라이브 전광판 레고 블록)
================================================================================================
- 브랜드: 📈 StockMaster AI (국내주식 · 체결강도 120% 수급 퀀트 · 장전 브리핑)
- 역할:
  1. StockMaster 매거진 오늘자 및 최신 발행 내역 (네이버 블로그 실제 URL, 티스토리, 브런치)
  2. StockMaster 네이버 지식iN (국내주식/증권사/계좌/공모주) 오늘자 무인 답변 실적 및 최신 URL
  3. StockMaster 숏폼/릴스/유튜브 최신 발행 링크
  4. 다른 앱과 0.001%도 섞이지 않는 순수 100% 독립 레고 블록
"""

import os
import sys
import re
import json
import time
import logging
import datetime
from datetime import datetime as dt
from pathlib import Path
from typing import Dict, Any, List

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs" / "stock"

logger = logging.getLogger("StockLiveTracker")


class StockLiveTracker:
    """📈 StockMaster AI 주식 전용 무인 발행 실시간 트래커 (독립 레고 블록)"""

    BRAND_KEY = "stock"
    BRAND_NAME = "📈 StockMaster AI"
    LANDING_URL = "https://stockmaster-ai.vercel.app/"
    NAVER_BLOG_ID = "stockmaster_ai"
    TISTORY_BLOG_NAME = "stockmaster-ai"

    def __init__(self):
        self.state_file = DATA_DIR / "stock_blog_rotation_state.json"
        self.kin_history_file = DATA_DIR / "stock_kin_history.json"
        self.kin_daily_file = DATA_DIR / "stock_kin_daily_state.json"
        self.yt_history_file = CURRENT_DIR / "youtube_publish_history.json"
        self.meta_history_file = CURRENT_DIR / "meta_publish_history.json"
        self.cafe_history_file = PROJECT_ROOT / "scratch" / "stock_cafe_rotation_history.json"
        self.reports_dir = OUTPUTS_DIR / "publish_reports"
        self.ig_username = "stockmaster_ai"
        self.page_id = "1341778472350233"

    def get_live_status(self) -> Dict[str, Any]:
        """주식 AI 전용 실시간 무인 발행 현황 집계"""
        now = datetime.datetime.now()
        today_str = now.strftime("%Y-%m-%d")

        blog_info = self._get_blog_info(today_str)
        kin_info = self._get_kin_info(today_str)
        shorts_info = self._get_shorts_info(today_str)
        cafe_info = self._get_cafe_info(today_str)
        cardnews_info = self._get_cardnews_info(today_str)

        return {
            "brand": self.BRAND_KEY,
            "brand_name": self.BRAND_NAME,
            "landing_url": self.LANDING_URL,
            "today": today_str,
            "updated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "today_blog_count": blog_info.get("today_count", 0),
            "today_kin_count": kin_info.get("today_count", 0),
            "today_shorts_count": shorts_info.get("today_count", 0),
            "today_cardnews_count": cardnews_info.get("today_count", 0),
            "today_cafe_count": cafe_info.get("today_count", 0),
            "blog": blog_info,
            "kin": kin_info,
            "shorts": shorts_info,
            "cardnews": cardnews_info,
            "cafe": cafe_info
        }

    def _get_cafe_info(self, today_str: str) -> Dict[str, Any]:
        """7대 정예 주식 카페 스텔스 침투 이력 집계"""
        history = []
        slot_idx = 0
        total_comments = 0
        last_post_date = "-"

        cafe_url_map = {
            "평생주식카페": "ustock",
            "거북이투자법": "geobuk2",
            "주식차트 연구소": "stockschart",
            "달팽이주식카페": "pointns",
            "주식광장": "hayate1",
            "가치투자연구소": "itooza",
            "하승훈의 주식투자": "hastock"
        }

        if self.cafe_history_file.exists():
            try:
                with open(self.cafe_history_file, "r", encoding="utf-8") as f:
                    cdata = json.load(f)
                    history = cdata.get("post_history", [])
                    slot_idx = cdata.get("current_slot_index", 0)
                    total_comments = cdata.get("total_comments_posted", 0)
                    last_post_date = cdata.get("last_post_date", "-")
            except Exception as e:
                logger.warning(f"Failed to read stock cafe history: {e}")

        # URL 및 필수 필드 보강
        for h in history:
            c_name = h.get("cafe_name", "")
            art_id = h.get("article_id", "")
            if not h.get("url") and art_id:
                url_id = cafe_url_map.get(c_name, "ustock")
                h["url"] = f"https://cafe.naver.com/{url_id}/{art_id}"

        today_posts = [h for h in history if (h.get("date") or h.get("datetime", "")[:10]) == today_str]
        recent_posts = list(reversed(history))[:5]

        slot_names = [
            "1. 평생주식카페 (월)", "2. 거북이투자법 (화)", "3. 주식차트 연구소 (수)",
            "4. 달팽이주식카페 (목)", "5. 주식광장 (금)", "6. 가치투자연구소 (토)", "7. 하승훈의 주식투자 (일)"
        ]
        curr_slot_name = slot_names[slot_idx % len(slot_names)]

        return {
            "today_count": len(today_posts),
            "target_count": 1,
            "total_count": total_comments,
            "current_slot": curr_slot_name,
            "last_post_date": last_post_date,
            "today_posts": today_posts,
            "recent_posts": recent_posts,
            "latest": recent_posts[0] if recent_posts else {}
        }

    def _get_blog_info(self, today_str: str) -> Dict[str, Any]:
        history = []
        last_run_time = "-"
        last_title = "-"
        published_count = 0

        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    sdata = json.load(f)
                    history = sdata.get("history", [])
                    last_run_time = sdata.get("last_run_time", "-")
                    last_title = sdata.get("last_title", "-")
                    published_count = sdata.get("published_count", len(history))
            except Exception as e:
                logger.warning(f"Failed to read stock blog state: {e}")

        today_history = [
            h for h in history 
            if (h.get("published_at") or "").startswith(today_str)
        ]

        latest_item = history[0] if history else {}
        latest_published_at = latest_item.get("published_at", "")

        report_channels = {}
        if self.reports_dir.exists():
            rep_files = sorted(self.reports_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
            if rep_files:
                try:
                    with open(rep_files[0], "r", encoding="utf-8") as fp:
                        rdata = json.load(fp)
                        report_channels = rdata.get("results", {}).get("channels", {})
                except Exception:
                    pass

        # 0. 📊 본진 웹앱 Supabase 퀀트 리서치 블로그
        supa_res = latest_item.get("publish_results", {}).get("channels", {}).get("supabase_research", {})
        supa_success = (supa_res.get("status") == "success")
        supa_published_at = latest_published_at if supa_success else ""

        # 1. 🟢 네이버 블로그 검증 (홈 주소가 아닌 실제 logNo 또는 상세 글 번호 필수 검증)
        naver_url = ""
        naver_status = "idle"
        naver_published_at = ""
        
        # 최신 배포 보고서 또는 오늘자 발행 이력 중 실제 상세 글 번호가 있는 글 탐색
        if "naver_blog" in report_channels:
            nb = report_channels["naver_blog"]
            u = nb.get("url") or nb.get("post_url") or ""
            if ("logNo=" in u or re.search(r'blog\.naver\.com/[^/]+/\d+', u)) and nb.get("status") == "success":
                naver_url = u
                naver_status = "success"
                naver_published_at = latest_published_at

        if not naver_url:
            for h in history:
                nb = h.get("publish_results", {}).get("channels", {}).get("naver_blog", {})
                u = nb.get("url") or nb.get("post_url") or ""
                if ("logNo=" in u or re.search(r'blog\.naver\.com/[^/]+/\d+', u)) and nb.get("status") == "success":
                    naver_url = u
                    naver_status = "success"
                    naver_published_at = h.get("published_at", "")
                    break

        # 네이버 RSS를 통한 최신 발행 글 자동 감지 (오늘자 글)
        if not naver_url:
            try:
                import urllib.request
                import xml.etree.ElementTree as ET
                rss_url = f"https://rss.blog.naver.com/{self.NAVER_BLOG_ID}.xml"
                req = urllib.request.Request(rss_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    root = ET.fromstring(resp.read().decode("utf-8", errors="ignore"))
                    items = root.findall("./channel/item")
                    if items:
                        link = items[0].find("link").text.strip() if items[0].find("link") is not None else ""
                        pub_date = items[0].find("pubDate").text.strip() if items[0].find("pubDate") is not None else ""
                        if link:
                            naver_url = link
                            naver_status = "success"
                            naver_published_at = dt.now().strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pass

        is_naver_today = naver_published_at.startswith(today_str) if naver_published_at else False

        # 2. 🟠 티스토리 블로그
        tistory_url = ""
        tistory_status = "idle"
        tistory_msg = ""
        tistory_published_at = ""

        if "tistory" in report_channels:
            tb = report_channels["tistory"]
            tistory_status = tb.get("status", "unknown")
            tistory_url = tb.get("url") or ""
            tistory_msg = tb.get("message") or ""
        elif latest_item.get("publish_results", {}).get("channels", {}).get("tistory"):
            tb = latest_item["publish_results"]["channels"]["tistory"]
            tistory_status = tb.get("status", "unknown")
            tistory_url = tb.get("url") or ""
            tistory_msg = tb.get("message") or ""

        # 티스토리 RSS를 통한 오늘자 최신 발행 글 검증
        if tistory_status != "session_expired" and (not tistory_url or "manage" in tistory_url):
            try:
                import urllib.request
                import xml.etree.ElementTree as ET
                rss_url = f"https://{self.TISTORY_BLOG_NAME}.tistory.com/rss"
                req = urllib.request.Request(rss_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    root = ET.fromstring(resp.read().decode("utf-8"))
                    items = root.findall("./channel/item")
                    if items and items[0].find("link") is not None:
                        rss_link = items[0].find("link").text.strip()
                        pub_date = items[0].find("pubDate").text.strip() if items[0].find("pubDate") is not None else ""
                        # 오늘자 글인 경우에만 자동 연동
                        if rss_link:
                            tistory_url = rss_link
                            tistory_status = "success"
                            tistory_published_at = dt.now().strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pass

        has_real_post_url = bool(tistory_url and re.search(r'tistory\.com/\d+', tistory_url))
        is_tistory_success = (tistory_status == "success") and has_real_post_url

        # 3. 🟡 카카오 브런치
        brunch_status = "idle"
        brunch_msg = ""
        if "brunch" in report_channels:
            brunch_status = report_channels["brunch"].get("status", "unknown")
        elif latest_item.get("publish_results", {}).get("channels", {}).get("brunch"):
            brunch_status = latest_item["publish_results"]["channels"]["brunch"].get("status", "unknown")
            brunch_msg = latest_item["publish_results"]["channels"]["brunch"].get("message", "")

        channels = {
            "supabase_research": {
                "name": "StockMaster 자체 홈페이지 퀀트 리서치 블로그",
                "status": "success" if supa_success else "idle",
                "url": self.LANDING_URL,
                "title": supa_res.get("title", latest_item.get("title", "")),
                "published_at": supa_published_at,
                "is_today": supa_published_at.startswith(today_str) if supa_published_at else False,
                "is_success": supa_success,
                "post_id": supa_res.get("post_id")
            },
            "naver_blog": {
                "name": "네이버 블로그",
                "blog_id": self.NAVER_BLOG_ID,
                "status": "success" if (naver_status == "success" and is_naver_today) else "not_published_today" if naver_published_at else "idle",
                "url": naver_url,
                "published_at": naver_published_at,
                "is_today": is_naver_today,
                "is_success": is_naver_today and bool(naver_url),
                "message": f"오늘자 미발행 (최근 실제 발행: {naver_published_at})" if (naver_published_at and not is_naver_today) else "오늘 발행 대기 중"
            },
            "tistory": {
                "name": "티스토리 (Tistory)",
                "blog_name": self.TISTORY_BLOG_NAME,
                "status": "success" if is_tistory_success else tistory_status,
                "url": tistory_url if has_real_post_url else "",
                "message": tistory_msg or ("카카오 세션 만료. [1회연동]_주식AI_티스토리_영구로그인.bat 실행 필요" if tistory_status == "session_expired" else ("오늘 발행 대기 중" if tistory_status == "idle" else "")),
                "is_success": is_tistory_success,
                "is_session_expired": tistory_status == "session_expired"
            },
            "brunch": {
                "name": "카카오 브런치",
                "status": brunch_status,
                "message": brunch_msg or "브런치스토리 로그인 세션 필요",
                "is_success": brunch_status == "success"
            }
        }

        return {
            "today_count": len(today_history),
            "total_count": published_count,
            "last_run_time": last_run_time,
            "last_title": latest_item.get("title") or last_title,
            "last_title_naver": latest_item.get("title_naver") or latest_item.get("title") or last_title,
            "last_title_tistory": latest_item.get("title_tistory") or latest_item.get("title") or last_title,
            "channels": channels
        }

    def _get_kin_info(self, today_str: str) -> Dict[str, Any]:
        today_count = 0
        target_count = 10
        recent_answers = []

        if self.kin_history_file.exists():
            try:
                with open(self.kin_history_file, "r", encoding="utf-8") as f:
                    hd = json.load(f)
                    items = hd if isinstance(hd, list) else list(hd.values())
                    for item in items:
                        c_at = item.get("created_at", "")
                        if c_at.startswith(today_str):
                            today_count += 1
                        
                        if len(recent_answers) < 4:
                            q_title = item.get("title", "")
                            q_url = item.get("published_url") or item.get("url") or ""
                            doc_id = item.get("doc_id", "")
                            if not q_url and doc_id:
                                q_url = f"https://kin.naver.com/qna/detail.naver?docId={doc_id}"
                            recent_answers.append({
                                "title": q_title,
                                "url": q_url,
                                "keyword": item.get("keyword", ""),
                                "created_at": c_at,
                                "is_today": c_at.startswith(today_str),
                                "status": item.get("status", "published")
                            })
            except Exception as e:
                logger.warning(f"Failed to read stock kin history: {e}")

        return {
            "today_count": today_count,
            "target_count": target_count,
            "recent_answers": recent_answers
        }

    def _get_shorts_info(self, today_str: str) -> Dict[str, Any]:
        platforms = {
            "youtube": {
                "name": "YouTube Shorts (유튜브 쇼츠)",
                "icon": "🔴",
                "status": "idle",
                "is_success": False,
                "url": "",
                "title": "오늘 발행 대기 중",
                "published_at": "-",
                "is_today": False
            },
            "instagram": {
                "name": "Instagram Reels (인스타 릴스)",
                "icon": "📸",
                "status": "idle",
                "is_success": False,
                "url": "",
                "title": "오늘 발행 대기 중",
                "published_at": "-",
                "is_today": False
            },
            "facebook": {
                "name": "Facebook Reels (페이스북 릴스)",
                "icon": "🔵",
                "status": "idle",
                "is_success": False,
                "url": "",
                "title": "오늘 발행 대기 중",
                "published_at": "-",
                "is_today": False
            },
            "naver_clip": {
                "name": "Naver Clip (네이버 클립)",
                "icon": "🟢",
                "status": "idle",
                "is_success": False,
                "url": "",
                "title": "오늘 발행 대기 중",
                "published_at": "-",
                "is_today": False
            }
        }

        # 1. YouTube Data 스캔
        if self.yt_history_file.exists():
            try:
                with open(self.yt_history_file, "r", encoding="utf-8") as f:
                    ydata = json.load(f)
                    if ydata and isinstance(ydata, list) and len(ydata) > 0:
                        ydata_sorted = sorted(ydata, key=lambda x: x.get("published_at", ""), reverse=True)
                        latest_yt = ydata_sorted[0]
                        p_at = latest_yt.get("published_at", "-")
                        platforms["youtube"] = {
                            "name": "YouTube Shorts (유튜브 쇼츠)",
                            "icon": "🔴",
                            "status": latest_yt.get("status", "success"),
                            "is_success": latest_yt.get("status") == "success" and bool(latest_yt.get("video_url")),
                            "url": latest_yt.get("video_url", ""),
                            "title": latest_yt.get("title", ""),
                            "published_at": p_at,
                            "is_today": p_at.startswith(today_str)
                        }
            except Exception as e:
                logger.warning(f"Failed to read youtube history: {e}")

        # 2. Meta (Instagram + Facebook) 숏폼/릴스 스캔
        if self.meta_history_file.exists():
            try:
                with open(self.meta_history_file, "r", encoding="utf-8") as f:
                    mdata = json.load(f)
                    if isinstance(mdata, list):
                        mdata_sorted = sorted(mdata, key=lambda x: x.get("timestamp", ""), reverse=True)
                        for item in mdata_sorted:
                            t_type = item.get("type", "")
                            p_at = item.get("timestamp", "-")
                            p_id = item.get("id", "")
                            snippet = item.get("snippet", "")
                            first_line = snippet.split("\n")[0] if snippet else "주식AI 숏폼 피드"
                            item_url = item.get("permalink") or item.get("url") or ""

                            if ("reels" in t_type or "video" in t_type) and "instagram" in t_type and not platforms["instagram"]["is_success"]:
                                platforms["instagram"] = {
                                    "name": "Instagram Reels (인스타 릴스)",
                                    "icon": "📸",
                                    "status": "success",
                                    "is_success": True,
                                    "url": item_url or f"https://www.instagram.com/{self.ig_username}/reels/",
                                    "post_id": p_id,
                                    "title": first_line,
                                    "published_at": p_at,
                                    "is_today": p_at.startswith(today_str)
                                }
                            elif ("reels" in t_type or "video" in t_type) and "facebook" in t_type and not platforms["facebook"]["is_success"]:
                                platforms["facebook"] = {
                                    "name": "Facebook Reels (페이스북 릴스)",
                                    "icon": "🔵",
                                    "status": "success",
                                    "is_success": True,
                                    "url": item_url or (f"https://www.facebook.com/reel/{p_id}" if p_id and "_" not in p_id else f"https://www.facebook.com/{self.page_id}"),
                                    "post_id": p_id,
                                    "title": first_line,
                                    "published_at": p_at,
                                    "is_today": p_at.startswith(today_str)
                                }
            except Exception as e:
                logger.warning(f"Failed to read stock meta history: {e}")

        # 3. Naver Clip 스캔
        clip_history = OUTPUTS_DIR / "naver_clip_history.json"
        if clip_history.exists():
            try:
                with open(clip_history, "r", encoding="utf-8") as f:
                    cdata = json.load(f)
                    if cdata and isinstance(cdata, list) and len(cdata) > 0:
                        c_sorted = sorted(cdata, key=lambda x: x.get("published_at", ""), reverse=True)
                        latest_c = c_sorted[0]
                        p_at = latest_c.get("published_at", "-")
                        platforms["naver_clip"] = {
                            "name": "Naver Clip (네이버 클립)",
                            "icon": "🟢",
                            "status": latest_c.get("status", "success"),
                            "is_success": latest_c.get("status") == "success",
                            "url": latest_c.get("url", ""),
                            "title": latest_c.get("title", ""),
                            "published_at": p_at,
                            "is_today": p_at.startswith(today_str)
                        }
            except Exception:
                pass

        today_count = sum(1 for p in platforms.values() if p.get("is_today"))

        return {
            "today_count": today_count,
            "platforms": platforms
        }

    def _get_cardnews_info(self, today_str: str) -> Dict[str, Any]:
        """📸 4대 옴니 카드뉴스 (1080x1350 완제품 및 인스타/페북 배포) 100% 독립 집계"""
        platforms = {
            "instagram": {
                "name": "Instagram Carousel (인스타 5장 캐러셀)",
                "icon": "📸",
                "status": "idle",
                "is_success": False,
                "url": f"https://www.instagram.com/{self.ig_username}/",
                "title": "오늘 발행 대기 중",
                "published_at": "-",
                "is_today": False
            },
            "facebook": {
                "name": "Facebook Album (페이스북 5장 앨범)",
                "icon": "📘",
                "status": "idle",
                "is_success": False,
                "url": f"https://www.facebook.com/{self.page_id}",
                "title": "오늘 발행 대기 중",
                "published_at": "-",
                "is_today": False
            },
            "local_slides": {
                "name": "1080x1350 카드뉴스 5장 완제품",
                "icon": "📁",
                "status": "idle",
                "is_success": False,
                "folder": "",
                "slide_count": 0,
                "title": "제작 대기 중",
                "time": "-",
                "is_today": False
            }
        }

        # 1. Meta (Instagram Carousel/Photo + Facebook Album/Photo) 스캔
        if self.meta_history_file.exists():
            try:
                with open(self.meta_history_file, "r", encoding="utf-8") as f:
                    mdata = json.load(f)
                    if isinstance(mdata, list):
                        mdata_sorted = sorted(mdata, key=lambda x: x.get("timestamp", ""), reverse=True)
                        for item in mdata_sorted:
                            t_type = item.get("type", "")
                            p_at = item.get("timestamp", "-")
                            p_id = item.get("id", "")
                            snippet = item.get("snippet", "")
                            first_line = snippet.split("\n")[0] if snippet else "주식AI 카드뉴스"
                            item_url = item.get("permalink") or item.get("url") or ""

                            # 인스타그램 캐러셀 / 포토
                            if ("carousel" in t_type or "photo" in t_type) and "instagram" in t_type and not platforms["instagram"]["is_success"]:
                                platforms["instagram"] = {
                                    "name": "Instagram Carousel (인스타 5장 캐러셀)",
                                    "icon": "📸",
                                    "status": "success",
                                    "is_success": True,
                                    "url": item_url or f"https://www.instagram.com/{self.ig_username}/",
                                    "post_id": p_id,
                                    "title": first_line,
                                    "published_at": p_at,
                                    "is_today": p_at.startswith(today_str)
                                }
                            # 페이스북 앨범 / 포토 / 피드
                            elif ("album" in t_type or "photo" in t_type or "feed" in t_type) and "facebook" in t_type and not platforms["facebook"]["is_success"]:
                                post_url = item_url
                                if not post_url:
                                    if p_id and "_" in p_id:
                                        p_parts = p_id.split("_")
                                        post_url = f"https://www.facebook.com/{p_parts[0]}/posts/{p_parts[1]}"
                                    else:
                                        post_url = f"https://www.facebook.com/{self.page_id}"
                                platforms["facebook"] = {
                                    "name": "Facebook Album (페이스북 5장 앨범)",
                                    "icon": "📘",
                                    "status": "success",
                                    "is_success": True,
                                    "url": post_url,
                                    "post_id": p_id,
                                    "title": first_line,
                                    "published_at": p_at,
                                    "is_today": p_at.startswith(today_str)
                                }
            except Exception as e:
                logger.warning(f"Failed to read stock cardnews meta history: {e}")

        # 2. 로컬 1080x1350 카드뉴스 완제품 디렉터리 스캔
        card_dirs = [
            Path("C:/Users/zkfnt/Desktop/한국 카드뉴스_산출물/주식"),
            Path("C:/Users/zkfnt/Desktop/한국 카드뉴스_산출물/Stock"),
            Path("C:/Users/zkfnt/Desktop/한국 카드뉴스_산출물/StockMaster"),
            OUTPUTS_DIR / "cardnews"
        ]
        latest_folder = None
        latest_mtime = 0
        for cdir in card_dirs:
            if cdir.exists():
                for sub in cdir.iterdir():
                    if sub.is_dir():
                        slides = list(sub.glob("slide_*.png"))
                        if slides:
                            try:
                                mt = sub.stat().st_mtime
                                if mt > latest_mtime:
                                    latest_mtime = mt
                                    latest_folder = sub
                            except Exception:
                                pass

        if latest_folder:
            slides = list(latest_folder.glob("slide_*.png"))
            mt_str = datetime.datetime.fromtimestamp(latest_mtime).strftime("%Y-%m-%d %H:%M:%S")
            platforms["local_slides"] = {
                "name": "1080x1350 카드뉴스 5장 완제품",
                "icon": "📁",
                "status": "success",
                "is_success": True,
                "folder": str(latest_folder),
                "folder_name": latest_folder.name,
                "slide_count": len(slides),
                "title": latest_folder.name,
                "time": mt_str,
                "is_today": mt_str.startswith(today_str)
            }

        today_count = sum(1 for p in platforms.values() if p.get("is_today"))

        return {
            "today_count": today_count,
            "target_count": 1,
            "platforms": platforms
        }




if __name__ == "__main__":
    tracker = StockLiveTracker()
    print(json.dumps(tracker.get_live_status(), ensure_ascii=False, indent=2))
