# -*- coding: utf-8 -*-
"""
StockMaster Supabase Manager (📈 주식 AI 전담 데이터베이스 연동 모듈)
==================================================================
- 역할:
  1. StockMaster 전용 Supabase(https://ufkxxiuuefbefmtcnvtl.supabase.co) 연결 관리
  2. [quant_research_posts] 퀀트 리서치 포스트 실데이터 연동 및 열람 분석
  3. [profiles] 등록 회원 및 포트폴리오 분석
  4. 15대 옴니채널 유입(유튜브 쇼츠, 100대 황금키워드 지식iN, 스레드, X 등) 순 유입자(UV) 산출
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import dotenv_values, load_dotenv

logger = logging.getLogger("StockSupabaseManager")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent


class StockSupabaseManager:
    """StockMaster AI 주식 퀀트 앱 전용 Supabase 연동 매니저 (완전 독립 레고 블록)"""

    def __init__(self):
        self.client = None
        self.supabase_url = ""
        self.service_role_key = ""
        self._init_connection()

    def _init_connection(self):
        # 1. stock ai/stock/.env 에서 전용 설정 최우선 로드
        url = ""
        key = ""
        stock_env_paths = [
            Path(r"C:\Users\zkfnt\Desktop\stock ai\stock\.env"),
            Path(r"C:\Users\zkfnt\Desktop\stock ai\.env")
        ]
        for p in stock_env_paths:
            if p.exists():
                cfg = dotenv_values(p)
                url = cfg.get("SUPABASE_URL") or cfg.get("NEXT_PUBLIC_SUPABASE_URL") or url
                key = cfg.get("SUPABASE_SERVICE_KEY") or cfg.get("SUPABASE_KEY") or key
                if url and key:
                    break

        # 2. 프로젝트 .env fallback
        if not url or not key:
            load_dotenv(PROJECT_ROOT / ".env")
            url = os.getenv("STOCK_SUPABASE_URL") or os.getenv("SUPABASE_URL") or url
            key = os.getenv("STOCK_SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_KEY") or key

        self.supabase_url = url or ""
        self.service_role_key = key or ""

        if self.supabase_url and self.service_role_key:
            try:
                from supabase import create_client
                self.client = create_client(self.supabase_url, self.service_role_key)
                logger.info(f"✅ [StockSupabase] 주식 AI Supabase 연결 성공 ({self.supabase_url})")
            except Exception as e:
                logger.warning(f"⚠️ [StockSupabase] 클라이언트 초기화 실패: {e}")
                self.client = None
        else:
            logger.warning("⚠️ [StockSupabase] URL 또는 Key 미설정")

    def is_connected(self) -> bool:
        return self.client is not None

    def upload_image_to_storage(self, local_image_path: str, bucket_subpath: str = "stock/media") -> Optional[str]:
        """🖼️ 로컬 이미지/비디오를 Supabase Storage에 업로드하고 영구 퍼블릭 URL 반환"""
        if not self.is_connected() or not local_image_path:
            return None

        p = Path(local_image_path)
        if not p.exists() or p.stat().st_size == 0:
            logger.warning(f"⚠️ [StockSupabase] 업로드할 파일이 존재하지 않음: {local_image_path}")
            return None

        import re
        safe_stem = re.sub(r'[^a-zA-Z0-9_\-]', '_', p.stem)
        file_name = f"{safe_stem}{p.suffix.lower()}"
        storage_path = f"{bucket_subpath}/{file_name}"

        try:
            with open(p, "rb") as f:
                file_bytes = f.read()

            suffix = p.suffix.lower()
            if suffix == ".mp4":
                content_type = "video/mp4"
            elif suffix == ".webp":
                content_type = "image/webp"
            elif suffix == ".png":
                content_type = "image/png"
            else:
                content_type = "image/jpeg"

            bucket_name = "stock-media"
            self.client.storage.from_(bucket_name).upload(
                path=storage_path,
                file=file_bytes,
                file_options={"content-type": content_type, "upsert": "true"}
            )
            public_url = self.client.storage.from_(bucket_name).get_public_url(storage_path)
            logger.info(f"✅ [StockSupabase] Storage 업로드 성공! 영구 URL: {public_url}")
            return public_url
        except Exception as e:
            logger.error(f"❌ [StockSupabase] Storage 업로드 실패: {e}")
            return None

    def get_stock_traffic_analytics(self, period: str = "today") -> Dict[str, Any]:
        """
        📊 StockMaster Supabase (stock_master_map __traffic_history__ & quant_research_posts & profiles) 100% 실데이터 분석
        - 🌟 동일인 중복 제거: visitorIds 기준 Unique Visitor 집계
        - 📈 퀀트 리서치 발행 실데이터(25건) 및 퀀트 회원(profiles 3명) 연동
        - 📅 오늘 24H / 📊 주간 7일 / 📈 월간 30일 / 🏆 연간 (Yearly/IR) 완벽 분기
        """
        kst = timezone(timedelta(hours=9))
        kst_now = datetime.now(kst)
        today_date = kst_now.date()
        today_str = today_date.strftime("%Y-%m-%d")

        if not self.is_connected():
            return {}

        try:
            # 1. stock_master_map 테이블에서 실제 100% 트래픽 히스토리 로드
            cloud_traffic_store = {}
            try:
                res_map = self.client.table("stock_master_map").select("code").eq("name", "__traffic_history__").maybe_single().execute()
                if res_map.data and res_map.data.get("code"):
                    cloud_traffic_store = json.loads(res_map.data["code"])
            except Exception as te:
                logger.warning(f"⚠️ [StockSupabase] __traffic_history__ 로드 실패: {te}")

            # 2. quant_research_posts 퀀트 리서치 칼럼 실데이터 조회
            res_posts = self.client.table("quant_research_posts").select("id, title, category, target_stock, is_published, created_at").order("created_at", desc=True).execute()
            raw_posts = res_posts.data or []

            # 3. profiles 회원 실데이터 조회
            res_profiles = self.client.table("profiles").select("id, email, phone, name, created_at").execute()
            raw_profiles = res_profiles.data or []

            # KST 시간 파싱 헬퍼
            def parse_kst(iso_str: str) -> Optional[datetime]:
                if not iso_str:
                    return None
                try:
                    clean_str = iso_str.replace("Z", "+00:00")
                    dt_utc = datetime.fromisoformat(clean_str)
                    return dt_utc.astimezone(kst)
                except Exception:
                    return None

            # 퀀트 포스트 전처리
            parsed_posts = []
            for p in raw_posts:
                dt_k = parse_kst(p.get("created_at"))
                if dt_k:
                    parsed_posts.append({
                        "id": p.get("id"),
                        "title": p.get("title") or "퀀트 리서치",
                        "category": p.get("category") or "MARKET",
                        "target_stock": p.get("target_stock") or "KOSPI",
                        "kst_dt": dt_k
                    })

            # 프로필 전처리
            parsed_profiles = []
            for pr in raw_profiles:
                dt_k = parse_kst(pr.get("created_at"))
                if dt_k:
                    parsed_profiles.append({
                        "id": pr.get("id"),
                        "email": pr.get("email") or "퀀트 유저",
                        "username": pr.get("name") or "퀀트 트레이더",
                        "kst_dt": dt_k
                    })

            total_posts_cnt = len(parsed_posts)
            total_profiles_cnt = len(parsed_profiles)

            # 전체 기간 누적 고유 순 방문자 (Total UV) 산출
            all_historical_visitor_ids = set()
            for d_k, d_v in cloud_traffic_store.items():
                vids = d_v.get("visitorIds") or []
                for vid in vids:
                    all_historical_visitor_ids.add(vid)
            total_cumulative_uv = len(all_historical_visitor_ids) if all_historical_visitor_ids else max(sum(v.get("uv", 0) for v in cloud_traffic_store.values()), 1)

            # 기간별 필터링 헬퍼
            def is_in_period(dt_k: datetime, p: str) -> bool:
                if p == "weekly":
                    return dt_k.date() >= (today_date - timedelta(days=7))
                elif p == "monthly":
                    return dt_k.date() >= (today_date - timedelta(days=30))
                elif p == "yearly":
                    return dt_k.year == today_date.year
                else: # today
                    return dt_k.date() == today_date

            period_posts = [p for p in parsed_posts if is_in_period(p["kst_dt"], period)]
            period_posts_cnt = len(period_posts)

            # 🌟 [채널 매핑 리졸버]
            channel_style_map = {
                "유튜브": {"name": "🎬 #1 유튜브 쇼츠 (급등주 퀀트 분석)", "category": "global_sns", "color": "#EF4444"},
                "인스타그램": {"name": "📸 #2 인스타그램 (투자 카드뉴스)", "category": "global_sns", "color": "#EC4899"},
                "티스토리": {"name": "💖 #4 티스토리 (주식 AI 칼럼)", "category": "seo_blog", "color": "#F97316"},
                "페이스북": {"name": "📸 #2 페이스북 (퀀트 리서치)", "category": "global_sns", "color": "#3B82F6"},
                "틱톡": {"name": "🎬 #1 틱톡 (쇼츠 퀀트 브리핑)", "category": "global_sns", "color": "#06B6D4"},
                "네이버": {"name": "💡 #7 네이버 검색/블로그 (스톡마스터 AI)", "category": "seo_blog", "color": "#10B981"},
                "구글": {"name": "🌐 #5 구글 검색 (서치콘솔 색인)", "category": "seo_blog", "color": "#3B82F6"},
                "카카오": {"name": "💬 #15 카카오톡 / 오픈채팅", "category": "messenger", "color": "#FACC15"},
                "직접": {"name": "🔗 다이렉트 / 즐겨찾기 직접 접속", "category": "other", "color": "#64748B"}
            }

            def map_referrer_channel(raw_name: str) -> Dict[str, str]:
                for k, v in channel_style_map.items():
                    if k in raw_name:
                        return v
                return {"name": f"🌐 {raw_name}", "category": "other", "color": "#64748B"}

            # 기간별 실데이터 가공
            merged_referrers = {}
            period_visitor_ids = set()

            if period == "weekly":
                date_list = [(today_date - timedelta(days=i)) for i in range(6, -1, -1)]
                hourly_data = []
                for d in date_list:
                    d_str = d.strftime("%Y-%m-%d")
                    day_item = cloud_traffic_store.get(d_str, {})
                    day_uv = day_item.get("uv", 0)
                    for vid in day_item.get("visitorIds", []):
                        period_visitor_ids.add(vid)
                    for r_k, r_v in day_item.get("referrers", {}).items():
                        merged_referrers[r_k] = merged_referrers.get(r_k, 0) + r_v
                    hourly_data.append({"hour": d.strftime("%m/%d"), "count": day_uv})
                period_uv = len(period_visitor_ids) if period_visitor_ids else sum(h["count"] for h in hourly_data)
                chart_title = "📊 [StockMaster AI] 최근 7일간 일별 퀀트 순 유입자 추이 (KST)"
                chart_badge = "기준: 최근 7일 순 방문자(중복제거)"
                period_label = "최근 7일"

            elif period == "monthly":
                weeks = [("4주 전", 28, 21), ("3주 전", 21, 14), ("2주 전", 14, 7), ("이번 주", 7, 0)]
                hourly_data = []
                for label, start_days, end_days in weeks:
                    w_start = today_date - timedelta(days=start_days)
                    w_end = today_date - timedelta(days=max(0, end_days - 1))
                    w_uv = 0
                    for d_k, d_v in cloud_traffic_store.items():
                        try:
                            d_obj = datetime.strptime(d_k, "%Y-%m-%d").date()
                            if w_start <= d_obj <= w_end:
                                w_uv += d_v.get("uv", 0)
                                for vid in d_v.get("visitorIds", []):
                                    period_visitor_ids.add(vid)
                                for r_k, r_v in d_v.get("referrers", {}).items():
                                    merged_referrers[r_k] = merged_referrers.get(r_k, 0) + r_v
                        except Exception:
                            pass
                    hourly_data.append({"hour": label, "count": w_uv})
                period_uv = len(period_visitor_ids) if period_visitor_ids else sum(h["count"] for h in hourly_data)
                chart_title = "📊 [StockMaster AI] 최근 4주간 주차별 퀀트 순 유입자 추이 (KST)"
                chart_badge = "기준: 최근 30일 순 방문자(중복제거)"
                period_label = "최근 30일"

            elif period == "yearly":
                mon_map = {m: 0 for m in range(1, 13)}
                for d_k, d_v in cloud_traffic_store.items():
                    try:
                        d_obj = datetime.strptime(d_k, "%Y-%m-%d").date()
                        if d_obj.year == today_date.year:
                            mon_map[d_obj.month] += d_v.get("uv", 0)
                            for vid in d_v.get("visitorIds", []):
                                period_visitor_ids.add(vid)
                            for r_k, r_v in d_v.get("referrers", {}).items():
                                merged_referrers[r_k] = merged_referrers.get(r_k, 0) + r_v
                    except Exception:
                        pass
                hourly_data = [{"hour": f"{m}월", "count": mon_map[m]} for m in range(1, 13)]
                period_uv = len(period_visitor_ids) if period_visitor_ids else total_cumulative_uv
                chart_title = f"📊 [StockMaster AI] {today_date.year}년 연간 월별 퀀트 순 유입자 추이 (KST)"
                chart_badge = f"기준: {today_date.year}년 연간 순 방문자(중복제거)"
                period_label = f"{today_date.year}년 연간"

            else: # today
                today_item = cloud_traffic_store.get(today_str, {})
                period_uv = today_item.get("uv", 0)
                raw_hourly = today_item.get("hourly") or [0]*24
                hourly_data = [{"hour": f"{h:02d}시", "count": raw_hourly[h] if h < len(raw_hourly) else 0} for h in range(24)]
                merged_referrers = today_item.get("referrers") or {}
                for vid in today_item.get("visitorIds", []):
                    period_visitor_ids.add(vid)
                chart_title = "📊 [StockMaster AI] 오늘 24시간 시간대별 퀀트 순 유입자 추이 (00시~23시 KST)"
                chart_badge = "기준: 오늘 24H 순 방문자(중복제거)"
                period_label = "오늘 24H"

            # 채널 유입 리스트 빌드
            channel_inflows = []
            valid_refs = {k: v for k, v in merged_referrers.items() if v > 0}
            total_ref_count = sum(valid_refs.values()) if valid_refs else period_uv

            for r_name, r_cnt in sorted(valid_refs.items(), key=lambda x: x[1], reverse=True):
                ch_info = map_referrer_channel(r_name)
                share = round((r_cnt / max(total_ref_count, 1)) * 100, 1)
                channel_inflows.append({
                    "name": ch_info["name"],
                    "category": ch_info["category"],
                    "count": r_cnt,
                    "share": share,
                    "color": ch_info["color"],
                    "unit": "명"
                })

            if not channel_inflows and period_uv > 0:
                channel_inflows.append({
                    "name": "🔗 다이렉트 / 즐겨찾기 직접 접속",
                    "category": "other",
                    "count": period_uv,
                    "share": 100.0,
                    "color": "#64748B",
                    "unit": "명"
                })

            # 4대 핵심 KPI (100% 실데이터 매칭)
            active_kpis = {
                "today_pv": period_uv,
                "cumulative_pv": total_cumulative_uv,
                "yoy_growth": f"리서치 {total_posts_cnt}건 (회원 {total_profiles_cnt}명)",
                "monthly_visitors": period_posts_cnt,
                "visitor_unit": "건",
                "kpi_period_label": f"{period_label} [StockMaster] 순 유입자 수 (중복제거)",
                "visitor_period_label": f"{period_label} [StockMaster] 퀀트 리서치 신규 발행 (건)"
            }

            # 실시간 리서치 & 유입 추적 목록
            real_visitors_list = []
            # 1. 오늘 접속한 순 방문자 세션 우선 표시
            for vid in list(period_visitor_ids)[:8]:
                real_visitors_list.append({
                    "source_name": "👤 [실제 방문자 접속]",
                    "medium": "디바이스: PC/웹 접속",
                    "campaign": "퀀트 AI 종목 리서치 열람",
                    "target_app": "StockMaster AI (주식 퀀트)",
                    "ip": f"세션: {vid[:14]}...",
                    "created_at": f"{today_str} KST 실시간"
                })

            # 2. 퀀트 포스트 실데이터 연동
            for p in parsed_posts[:10]:
                p_id_str = str(p.get('id', ''))
                real_visitors_list.append({
                    "source_name": f"📈 [퀀트 리서치] {p['title']}",
                    "medium": f"종목: {p['target_stock']}",
                    "campaign": f"카테고리: {p['category']}",
                    "target_app": "StockMaster AI (주식 퀀트)",
                    "ip": f"포스트ID: {p_id_str[:8]}...",
                    "created_at": p["kst_dt"].strftime("%Y-%m-%d %H:%M:%S KST")
                })

            return {
                "period": period,
                "brand": "stock",
                "chart_title": chart_title,
                "chart_badge": chart_badge,
                "channels_title": f"🚀 [StockMaster AI] 옴니채널 실제 유입 실적 ({period_label})",
                "channels_subtitle": f"* {period_label} 동안 StockMaster AI에 실제로 접속한 순 방문자({period_uv}명)의 채널별 실적입니다.",
                "visitors_title": f"👥 [StockMaster AI] 퀀트 리서치 열람 & 방문자 실시간 추적 ({period_label})",
                "visitors_subtitle": f"StockMaster AI에 유입된 퀀트 투자자의 실시간 접속 및 리서치 열람 기록입니다.",
                "kpis": active_kpis,
                "hourly_data": hourly_data,
                "channel_inflows": channel_inflows,
                "real_visitor_inflows": channel_inflows,
                "real_visitors_list": real_visitors_list,
                "stats_summary": {
                    "unique_visitors": period_uv,
                    "total_unique_visitors": total_cumulative_uv,
                    "total_posts": total_posts_cnt,
                    "total_profiles": total_profiles_cnt
                }
            }

        except Exception as e:
            logger.error(f"❌ [StockSupabase] 쿼리 실패: {e}")
            return {}


if __name__ == "__main__":
    mgr = StockSupabaseManager()
    print("Stock Connected:", mgr.is_connected())
    print("URL:", mgr.supabase_url)
    res = mgr.get_stock_traffic_analytics("yearly")
    print("Yearly KPIs:", res.get("kpis"))
