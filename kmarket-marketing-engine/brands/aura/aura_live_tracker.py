# -*- coding: utf-8 -*-
"""
Aura Live Publishing Tracker (💖 Aura AI 데이팅 100% 독립 무인 발행 라이브 전광판 레고 블록)
========================================================================================
- 브랜드: 💖 Aura AI 데이팅 (2030 소개팅 · 데이팅 · 매칭 라운지)
- 역할:
  1. Aura 2030 매거진 오늘자 및 최신 발행 내역 (네이버 블로그 실제 URL, 티스토리, 카카오 브런치, 앱 라운지 피드)
  2. Aura 네이버 지식iN (연애/소개팅/밀당) 오늘자 무인 답변 실적 및 최신 URL
  3. Aura 숏폼/릴스/유튜브 최신 발행 링크
  4. 다른 앱과 0.001%도 섞이지 않는 순수 100% 독립 레고 블록
"""

import os
import sys
import json
import logging
import datetime
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
OUTPUTS_DIR = PROJECT_ROOT / "outputs" / "aura"

logger = logging.getLogger("AuraLiveTracker")


class AuraLiveTracker:
    """💖 Aura AI 데이팅 전용 무인 발행 실시간 트래커 (독립 레고 블록)"""

    BRAND_KEY = "aura"
    BRAND_NAME = "💖 Aura AI 데이팅"
    LANDING_URL = "https://aura-ai-dating.vercel.app/"
    NAVER_BLOG_ID = "zkfnth01"
    TISTORY_BLOG_NAME = "aura-magazine"

    def __init__(self):
        self.state_file = DATA_DIR / "aura_blog_rotation_state.json"
        self.kin_history_file = DATA_DIR / "aura_kin_history.json"
        self.kin_daily_file = DATA_DIR / "aura_kin_daily_state.json"
        self.yt_history_file = CURRENT_DIR / "youtube_publish_history.json"
        self.meta_history_file = CURRENT_DIR / "meta_publish_history.json"
        self.cafe_history_file = PROJECT_ROOT / "scratch" / "aura_cafe_rotation_history.json"
        self.reports_dir = OUTPUTS_DIR / "publish_reports"
        self.ig_username = "aura_ai_dating"
        self.page_id = "1356851504174047"

    def get_live_status(self) -> Dict[str, Any]:
        """Aura 전용 실시간 무인 발행 현황 집계"""
        now = datetime.datetime.now()
        today_str = now.strftime("%Y-%m-%d")

        blog_info = self._get_blog_info(today_str)
        kin_info = self._get_kin_info(today_str)
        shorts_info = self._get_shorts_info(today_str)
        cafe_info = self._get_cafe_info(today_str)
        cardnews_info = self._get_cardnews_info(today_str)
        reddit_info = self._get_reddit_info(today_str)
        
        # 📸 12대 채널 실시간 육안 증빙 데이터 연동
        try:
            from core.verification.live_proof_verifier import live_proof_verifier
            proofs_data = live_proof_verifier.get_brand_proofs(self.BRAND_KEY)
        except Exception:
            proofs_data = {}

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
            "today_reddit_count": reddit_info.get("today_count", 0),
            "blog": blog_info,
            "kin": kin_info,
            "shorts": shorts_info,
            "cardnews": cardnews_info,
            "cafe": cafe_info,
            "reddit": reddit_info,
            "live_proofs": proofs_data
        }

    def _get_reddit_info(self, today_str: str) -> Dict[str, Any]:
        """💖 Aura 데이팅 전용 레딧 글로벌 여성 스텔스 침투 이력 집계"""
        posts = []
        today_count = 0
        try:
            import sqlite3
            from config import DB_PATH
            if DB_PATH.exists():
                conn = sqlite3.connect(str(DB_PATH))
                cur = conn.cursor()
                cur.execute("""
                    SELECT id, title, content_text, target_url, created_at
                    FROM marketing_history
                    WHERE service_id = ? AND content_type = 'reddit_reply'
                    ORDER BY id DESC LIMIT 10
                """, (self.BRAND_KEY,))
                rows = cur.fetchall()
                conn.close()
                for r in rows:
                    p_time = str(r[4]) if r[4] else ""
                    is_today = p_time.startswith(today_str)
                    if is_today:
                        today_count += 1
                    posts.append({
                        "id": r[0],
                        "title": r[1] or "레딧 스텔스 답변",
                        "comment_snippet": (r[2] or "")[:150],
                        "url": r[3] or "https://www.reddit.com/r/Living_in_Korea/",
                        "time": p_time,
                        "is_today": is_today
                    })
        except Exception as e:
            logger.warning(f"Failed to read aura reddit history: {e}")

        return {
            "today_count": today_count,
            "target_count": 1,
            "posts": posts,
            "last_post": posts[0] if posts else None
        }

    def _get_cafe_info(self, today_str: str) -> Dict[str, Any]:
        """8대 정예 카페 스텔스 침투 이력 집계"""
        history = []
        slot_idx = 0
        total_comments = 0
        last_post_date = "-"

        cafe_url_map = {
            "파우더룸": "cosmania",
            "여우야": "feko",
            "MBTI & HEALTH": "mbticafe",
            "향수사랑": "perfumelove",
            "뷰티매니아": "worrytodream",
            "직탐": "workee",
            "크지프": "korjapif",
            "크지프 KJIF": "korjapif",
            "시크먼트": "parisienlook"
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
                logger.warning(f"Failed to read aura cafe history: {e}")

        # URL 및 필수 필드 보강
        for h in history:
            c_name = h.get("cafe_name", "")
            art_id = h.get("article_id", "")
            if not h.get("url") and art_id:
                url_id = cafe_url_map.get(c_name, "cosmania")
                h["url"] = f"https://cafe.naver.com/{url_id}/{art_id}"

        today_posts = [h for h in history if (h.get("date") or h.get("datetime", "")[:10]) == today_str]
        recent_posts = list(reversed(history))[:5]

        slot_names = [
            "1. 파우더룸", "2. 여우야", "3. MBTI & HEALTH", 
            "4. 향수사랑/뷰티매니아/직탐", "5. 크지프 KJIF + 시크먼트"
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
                logger.warning(f"Failed to read aura blog state: {e}")

        today_history = [
            h for h in history 
            if (h.get("published_at") or "").startswith(today_str)
        ]

        latest_item = history[0] if history else {}
        if not latest_item and history:
            latest_item = history[-1]

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

        # 1. 네이버 블로그
        naver_url = ""
        naver_status = "idle"
        if "naver_blog" in report_channels:
            nb = report_channels["naver_blog"]
            naver_status = nb.get("status", "unknown")
            naver_url = nb.get("url") or nb.get("post_url") or ""
        elif latest_item.get("publish_results", {}).get("channels", {}).get("naver_blog"):
            nb = latest_item["publish_results"]["channels"]["naver_blog"]
            naver_status = nb.get("status", "unknown")
            naver_url = nb.get("url") or nb.get("post_url") or ""

        # 2. 티스토리 블로그
        tistory_url = ""
        tistory_status = "idle"
        tistory_msg = ""
        session_file = CURRENT_DIR / "tistory_session.json"
        profile_dir = CURRENT_DIR / "tistory_chrome_profile"
        has_fresh_session = (session_file.exists() and session_file.stat().st_size > 100) or (profile_dir.exists() and any(profile_dir.iterdir()))

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

        # 대표님이 방금 1회 로그인을 완료하여 영구 세션이 등록된 경우 session_expired 해제
        if tistory_status == "session_expired" and has_fresh_session:
            tistory_status = "idle"
            tistory_msg = ""

        # 티스토리 URL이 관리자 주소이거나 비어있을 경우 실제 최신 공개 글 링크 자동 조회
        if not tistory_url or "manage" in tistory_url:
            try:
                import urllib.request
                import xml.etree.ElementTree as ET
                rss_url = f"https://{self.TISTORY_BLOG_NAME}.tistory.com/rss"
                req = urllib.request.Request(rss_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    root = ET.fromstring(resp.read().decode("utf-8"))
                    items = root.findall("./channel/item")
                    if items and items[0].find("link") is not None:
                        tistory_url = items[0].find("link").text.strip()
                        if tistory_status != "session_expired":
                            tistory_status = "success"
            except Exception:
                pass

        import re
        has_real_post_url = bool(tistory_url and re.search(r'tistory\.com/\d+', tistory_url))
        is_tistory_success = (tistory_status == "success") and has_real_post_url

        # 3. 카카오 브런치
        brunch_status = "idle"
        if "brunch" in report_channels:
            brunch_status = report_channels["brunch"].get("status", "unknown")

        published_time = latest_item.get("published_at") or last_run_time
        if published_time == "-":
            published_time = ""

        naver_title = latest_item.get("title_naver") or latest_item.get("title") or last_title
        tistory_title = latest_item.get("title_tistory") or latest_item.get("title") or last_title

        channels = {
            "naver_blog": {
                "name": "네이버 블로그",
                "blog_id": self.NAVER_BLOG_ID,
                "title": naver_title,
                "status": naver_status,
                "url": naver_url,
                "published_at": published_time,
                "is_today": bool(published_time and published_time.startswith(today_str)),
                "is_success": naver_status == "success" and bool(naver_url)
            },
            "tistory": {
                "name": "티스토리",
                "blog_name": self.TISTORY_BLOG_NAME,
                "title": tistory_title,
                "status": "success" if is_tistory_success else tistory_status,
                "url": tistory_url if has_real_post_url else "",
                "published_at": published_time,
                "is_today": bool(published_time and published_time.startswith(today_str)),
                "message": tistory_msg or ("오늘 발행 대기 중" if tistory_status == "idle" else ""),
                "is_success": is_tistory_success,
                "is_session_expired": tistory_status == "session_expired"
            },
            "brunch": {
                "name": "카카오 브런치",
                "title": latest_item.get("title") or last_title,
                "status": brunch_status,
                "published_at": published_time,
                "is_success": brunch_status == "success"
            },
            "app_lounge": {
                "name": "💖 Aura VIP 라운지",
                "title": latest_item.get("title") or last_title,
                "status": "success",
                "url": self.LANDING_URL,
                "published_at": published_time,
                "is_success": True
            }
        }

        today_slots = []
        sorted_today_history = sorted(today_history, key=lambda x: x.get("published_at", ""))
        for idx, h in enumerate(sorted_today_history, 1):
            ch = h.get("publish_results", {}).get("channels", {})
            n_data = ch.get("naver_blog", {})
            t_data = ch.get("tistory", {})
            today_slots.append({
                "slot_num": idx,
                "published_at": h.get("published_at", "-"),
                "title": h.get("title", "-"),
                "naver_url": n_data.get("url") or n_data.get("post_url") or "",
                "tistory_url": t_data.get("url") or "",
                "is_naver_success": n_data.get("status") == "success" and bool(n_data.get("url") or n_data.get("post_url")),
                "is_tistory_success": t_data.get("status") == "success" and bool(t_data.get("url"))
            })

        today_cnt = len(today_slots)
        if today_cnt >= 3:
            slot_status_label = f"🟢 [3/3회 완료] 오늘 목표 발행 달성"
        elif today_cnt == 2:
            slot_status_label = f"🟡 [2/3회 완료] 19:45 3차 저녁 정시 대기"
        elif today_cnt == 1:
            slot_status_label = f"🟡 [1/3회 완료] 14:45 2차 오후 정시 대기"
        else:
            slot_status_label = f"⚪ [0/3회 완료] 09:45 1차 오전 정시 대기"

        return {
            "today_count": today_cnt,
            "target_daily": 3,
            "slot_status_label": slot_status_label,
            "today_slots": today_slots,
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
                        
                        if len(recent_answers) < 5:
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
                                "time": c_at,
                                "is_today": c_at.startswith(today_str),
                                "status": item.get("status", "published")
                            })
            except Exception as e:
                logger.warning(f"Failed to read aura kin history: {e}")

        return {
            "today_count": today_count,
            "count_today": today_count,
            "target_count": target_count,
            "recent_answers": recent_answers,
            "posts": recent_answers
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
            "tiktok": {
                "name": "TikTok (틱톡 숏폼)",
                "icon": "📱",
                "status": "idle",
                "is_success": False,
                "url": f"https://www.tiktok.com/@{self.ig_username}",
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
                logger.warning(f"Failed to read aura youtube history: {e}")

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
                            first_line = snippet.split("\n")[0] if snippet else "Aura 숏폼 피드"
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
                logger.warning(f"Failed to read aura meta history: {e}")

        # 3. TikTok 스캔
        tt_history = OUTPUTS_DIR / "tiktok_publish_history.json"
        if not tt_history.exists():
            tt_history = DATA_DIR / "aura_tiktok_history.json"
        if tt_history.exists():
            try:
                with open(tt_history, "r", encoding="utf-8") as f:
                    tdata = json.load(f)
                    if tdata and isinstance(tdata, list) and len(tdata) > 0:
                        t_sorted = sorted(tdata, key=lambda x: x.get("published_at", "") or x.get("timestamp", ""), reverse=True)
                        latest_t = t_sorted[0]
                        p_at = latest_t.get("published_at") or latest_t.get("timestamp", "-")
                        platforms["tiktok"] = {
                            "name": "TikTok (틱톡 숏폼)",
                            "icon": "📱",
                            "status": latest_t.get("status", "success"),
                            "is_success": latest_t.get("status") == "success" or bool(latest_t.get("url")),
                            "url": latest_t.get("url") or f"https://www.tiktok.com/@{self.ig_username}",
                            "title": latest_t.get("title", "Aura 2030 틱톡 숏폼"),
                            "published_at": p_at,
                            "is_today": str(p_at).startswith(today_str)
                        }
            except Exception:
                pass

        # 4. Naver Clip 스캔
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
        """📸 5대 옴니 카드뉴스 & 타래 (인스타/페북/스레드/완제품) 100% 독립 집계"""
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
            "threads": {
                "name": "Threads (스레드 바이럴 타래/카드뉴스)",
                "icon": "🧵",
                "status": "idle",
                "is_success": False,
                "url": f"https://www.threads.net/@{self.ig_username}",
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

        # 1. Meta (Instagram Carousel + Facebook Album/Photo) 스캔
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
                            first_line = snippet.split("\n")[0] if snippet else "Aura 카드뉴스"
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
                logger.warning(f"Failed to read aura cardnews meta history: {e}")

        # 2. Threads (스레드 바이럴 타래/카드뉴스) 스캔
        threads_files = [
            CURRENT_DIR / "threads_publish_history.json",
            DATA_DIR / "aura_threads_history.json",
            PROJECT_ROOT / "scratch" / "threads_aura_history.json"
        ]
        for tf in threads_files:
            if tf.exists():
                try:
                    with open(tf, "r", encoding="utf-8") as f:
                        th_data = json.load(f)
                        if th_data and isinstance(th_data, list) and len(th_data) > 0:
                            th_sorted = sorted(th_data, key=lambda x: x.get("published_at", "") or x.get("timestamp", ""), reverse=True)
                            latest_th = th_sorted[0]
                            p_at = str(latest_th.get("published_at") or latest_th.get("timestamp", "-"))
                            if "T" in p_at:
                                p_at = p_at.replace("T", " ").split(".")[0]
                            th_url = latest_th.get("url") or latest_th.get("thread_url") or f"https://www.threads.net/@{self.ig_username}"
                            platforms["threads"] = {
                                "name": "Threads (스레드 바이럴 타래/카드뉴스)",
                                "icon": "🧵",
                                "status": "success",
                                "is_success": True,
                                "url": th_url,
                                "title": latest_th.get("title", "Aura 바이럴 스레드 타래"),
                                "published_at": p_at,
                                "is_today": p_at.startswith(today_str)
                            }
                            break
                except Exception:
                    pass

        # 3. 로컬 1080x1350 카드뉴스 완제품 디렉터리 스캔
        card_dirs = [
            Path("C:/Users/zkfnt/Desktop/한국 카드뉴스_산출물/아우라"),
            Path("C:/Users/zkfnt/Desktop/한국 카드뉴스_산출물/Aura"),
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
    tracker = AuraLiveTracker()
    print(json.dumps(tracker.get_live_status(), ensure_ascii=False, indent=2))
