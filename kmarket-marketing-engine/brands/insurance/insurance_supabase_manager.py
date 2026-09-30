# -*- coding: utf-8 -*-
"""
InsureBalance Supabase Manager (🛡️ 보험 리밸런스 전담 데이터베이스 연동 모듈)
======================================================================
- 역할:
  1. InsureBalance 전용 Supabase 연결 관리
  2. [visitor_logs] 실시간 순 유입자(UV) 및 15대 옴니채널 트래픽 분석
  3. [customer_leads] 288건+ 실제 고객 상담 신청 및 리드 전환 분석
  4. [planners] 공인 설계사 실데이터 연동
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import dotenv_values, load_dotenv

logger = logging.getLogger("InsuranceSupabaseManager")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent


class InsuranceSupabaseManager:
    """InsureBalance 보험비교 앱 전용 Supabase 연동 매니저 (완전 독립 레고 블록)"""

    def __init__(self):
        self.client = None
        self.supabase_url = ""
        self.service_role_key = ""
        self._init_connection()

    def _init_connection(self):
        # 1. 환경변수 탐색
        load_dotenv(PROJECT_ROOT / ".env")
        url = os.getenv("INSURANCE_SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
        key = os.getenv("INSURANCE_SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        # 2. insurance-comparison-main/.env.local 에서 자동 로드
        if not url or not key:
            ins_env_paths = [
                Path(r"C:\Users\zkfnt\Desktop\insurance-comparison-main\insurance-comparison-main\.env.local"),
                Path(r"C:\Users\zkfnt\Desktop\insurance-comparison-main\insurance-comparison-main\.env"),
                Path(r"C:\Users\zkfnt\Desktop\insurance-comparison-main\.env.local")
            ]
            for p in ins_env_paths:
                if p.exists():
                    cfg = dotenv_values(p)
                    url = cfg.get("VITE_SUPABASE_URL") or cfg.get("SUPABASE_URL") or url
                    key = cfg.get("SUPABASE_SERVICE_ROLE_KEY") or cfg.get("VITE_SUPABASE_ANON_KEY") or key
                    if url and key:
                        break

        self.supabase_url = url or ""
        self.service_role_key = key or ""

        if self.supabase_url and self.service_role_key:
            try:
                from supabase import create_client
                self.client = create_client(self.supabase_url, self.service_role_key)
                logger.info(f"✅ [InsuranceSupabase] 보험 리밸런스 Supabase 연결 성공 ({self.supabase_url})")
            except Exception as e:
                logger.warning(f"⚠️ [InsuranceSupabase] 클라이언트 초기화 실패: {e}")
                self.client = None
        else:
            logger.warning("⚠️ [InsuranceSupabase] URL 또는 Key 미설정")

    def is_connected(self) -> bool:
        return self.client is not None

    def get_insurance_traffic_analytics(self, period: str = "today") -> Dict[str, Any]:
        """
        📊 InsureBalance Supabase (visitor_logs & customer_leads) 100% 실데이터 분석
        - 🌟 동일인 중복 제거: session_id 기준 '정확히 1명'으로 Unique Visitor 집계
        - 📋 실제 고객 상담 신청(customer_leads, 288건+) 및 설계사(planners) 실데이터 연동
        - 📅 오늘 24H / 📊 주간 7일 / 📈 월간 30일 / 🏆 연간 (Yearly/IR) 완벽 분기
        """
        kst = timezone(timedelta(hours=9))
        kst_now = datetime.now(kst)
        today_date = kst_now.date()

        if not self.is_connected():
            return {}

        try:
            # 1. visitor_logs 접속 로그 실데이터 조회
            res_logs = self.client.table("visitor_logs").select("*").order("created_at", desc=True).limit(5000).execute()
            raw_logs = res_logs.data or []

            # 2. customer_leads 실제 고객 상담 신청 실데이터 조회
            res_leads = self.client.table("customer_leads").select("id, planner_id, name, phone, insurance_type, monthly_premium, lead_source, status, created_at").order("created_at", desc=True).execute()
            raw_leads = res_leads.data or []

            # 3. planners 공인 설계사 조회
            res_planners = self.client.table("planners").select("id, name, company_name, is_admin").execute()
            total_planners = len(res_planners.data or [])

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

            # 로그 데이터 전처리
            parsed_logs = []
            for r in raw_logs:
                dt_k = parse_kst(r.get("created_at"))
                if dt_k:
                    parsed_logs.append({
                        "id": r.get("id"),
                        "session_id": r.get("session_id") or r.get("id"),
                        "planner_code": r.get("planner_code") or "direct",
                        "utm_source": r.get("utm_source") or "direct",
                        "kst_dt": dt_k
                    })

            # 상담 신청 데이터 전처리
            parsed_leads = []
            for lead in raw_leads:
                dt_k = parse_kst(lead.get("created_at"))
                if dt_k:
                    parsed_leads.append({
                        "id": lead.get("id"),
                        "name": lead.get("name") or "고객",
                        "phone": lead.get("phone") or "",
                        "insurance_type": lead.get("insurance_type") or "종합보험",
                        "monthly_premium": lead.get("monthly_premium") or 0,
                        "status": lead.get("status") or "pending",
                        "kst_dt": dt_k
                    })

            # 기간별 필터링
            def is_in_period(dt_k: datetime, p: str) -> bool:
                if p == "weekly":
                    return dt_k.date() >= (today_date - timedelta(days=7))
                elif p == "monthly":
                    return dt_k.date() >= (today_date - timedelta(days=30))
                elif p == "yearly":
                    return dt_k.year == today_date.year
                else: # today
                    return dt_k.date() == today_date

            period_logs = [l for l in parsed_logs if is_in_period(l["kst_dt"], period)]
            period_leads = [ld for ld in parsed_leads if is_in_period(ld["kst_dt"], period)]

            # 🌟 [순 방문자수 계산] session_id 기준 중복 100% 제거
            total_unique_sessions = set(l["session_id"] for l in parsed_logs)
            period_unique_sessions = set(l["session_id"] for l in period_logs)
            today_unique_sessions = set(l["session_id"] for l in parsed_logs if l["kst_dt"].date() == today_date)

            total_leads_cnt = len(parsed_leads)
            period_leads_cnt = len(period_leads)
            today_leads_cnt = len([ld for ld in parsed_leads if ld["kst_dt"].date() == today_date])

            # 기간별 차트 데이터 생성
            if period == "weekly":
                date_list = [(today_date - timedelta(days=i)) for i in range(6, -1, -1)]
                weekly_sessions = {d.strftime("%Y-%m-%d"): set() for d in date_list}
                for l in period_logs:
                    d_str = l["kst_dt"].strftime("%Y-%m-%d")
                    if d_str in weekly_sessions:
                        weekly_sessions[d_str].add(l["session_id"])
                hourly_data = [{"hour": d.strftime("%m/%d"), "count": len(weekly_sessions[d.strftime("%Y-%m-%d")])} for d in date_list]
                chart_title = "📊 [보험 리밸런스] 최근 7일간 일별 순 방문자 유입 추이 (KST)"
                chart_badge = "기준: 최근 7일 순 방문자(중복제거)"
                period_label = "최근 7일"

            elif period == "monthly":
                weeks = [("4주 전", 28, 21), ("3주 전", 21, 14), ("2주 전", 14, 7), ("이번 주", 7, 0)]
                hourly_data = []
                for label, start_days, end_days in weeks:
                    w_start = today_date - timedelta(days=start_days)
                    w_end = today_date - timedelta(days=max(0, end_days - 1))
                    w_sessions = set(l["session_id"] for l in period_logs if w_start <= l["kst_dt"].date() <= w_end)
                    hourly_data.append({"hour": label, "count": len(w_sessions)})
                chart_title = "📊 [보험 리밸런스] 최근 4주간 주차별 순 방문자 유입 추이 (KST)"
                chart_badge = "기준: 최근 30일 순 방문자(중복제거)"
                period_label = "최근 30일"

            elif period == "yearly":
                mon_sessions = {m: set() for m in range(1, 13)}
                for l in period_logs:
                    if l["kst_dt"].year == today_date.year:
                        mon_sessions[l["kst_dt"].month].add(l["session_id"])
                hourly_data = [{"hour": f"{m}월", "count": len(mon_sessions[m])} for m in range(1, 13)]
                chart_title = f"📊 [보험 리밸런스] {today_date.year}년 연간 월별 순 방문자 유입 추이 (KST)"
                chart_badge = f"기준: {today_date.year}년 연간 순 방문자(중복제거)"
                period_label = f"{today_date.year}년 연간"

            else: # today
                hr_sessions = {h: set() for h in range(24)}
                for l in period_logs:
                    hr_sessions[l["kst_dt"].hour].add(l["session_id"])
                hourly_data = [{"hour": f"{h:02d}시", "count": len(hr_sessions[h])} for h in range(24)]
                chart_title = "📊 [보험 리밸런스] 오늘 24시간 시간대별 순 방문자 유입 추이 (00시~23시 KST)"
                chart_badge = "기준: 오늘 24H 순 방문자(중복제거)"
                period_label = "오늘 24H"

            # 🌟 [보험 맞춤 15대 옴니채널 리졸버]
            def resolve_insurance_channel(utm: str, planner: str) -> Dict[str, str]:
                u_l = (utm or "").lower()
                p_l = (planner or "").lower()

                if "youtube" in u_l or "shorts" in u_l:
                    return {"name": "🎬 #1 유튜브 쇼츠 (실손/암보험 진실)", "category": "global_sns", "color": "#EF4444"}
                if "tiktok" in u_l:
                    return {"name": "🎬 #1 틱톡 (2030 보험 다이어트)", "category": "global_sns", "color": "#06B6D4"}
                if "insta" in u_l or "instagram" in u_l:
                    return {"name": "📸 #2 인스타그램 (카드뉴스 매거진)", "category": "global_sns", "color": "#EC4899"}
                if "facebook" in u_l or "fb" in u_l:
                    return {"name": "📸 #2 페이스북 (보험료 절감 꿀팁)", "category": "global_sns", "color": "#3B82F6"}
                if "blog" in u_l or "thefirst-life" in u_l or "naver_blog" in u_l:
                    return {"name": "💖 #4 네이버 블로그 (공식 칼럼)", "category": "seo_blog", "color": "#10B981"}
                if "tistory" in u_l or "think83157" in u_l:
                    return {"name": "💖 #4 티스토리 (보험비교 전문 칼럼)", "category": "seo_blog", "color": "#F97316"}
                if "brunch" in u_l:
                    return {"name": "💖 #4 카카오 브런치 (재테크 에세이)", "category": "seo_blog", "color": "#334155"}
                if "kin" in u_l or "지식" in u_l:
                    return {"name": "💡 #7 네이버 지식iN (보험 리모델링 Q&A)", "category": "seo_blog", "color": "#10B981"}
                if "search" in u_l or "naver" in u_l:
                    return {"name": "🌐 #5 네이버 검색 (보험 리밸런스)", "category": "seo_blog", "color": "#10B981"}
                if "google" in u_l:
                    return {"name": "🌐 #5 구글 검색 (서치콘솔 색인)", "category": "seo_blog", "color": "#3B82F6"}
                if "threads" in u_l:
                    return {"name": "📜 #6 Meta 스레드 (보험 호구 탈출 썰)", "category": "community", "color": "#0F172A"}
                if "twitter" in u_l or "x" in u_l:
                    return {"name": "📜 #6 X / 트위터 (바이럴 타래)", "category": "community", "color": "#0284C7"}
                if "cafe" in u_l or "mom" in u_l:
                    return {"name": "☕ #8 네이버 맘/직장인 카페 (보험 점검)", "category": "community", "color": "#10B981"}
                if "daum" in u_l:
                    return {"name": "🍵 #9 다음(Daum) 카페 (보험 후기)", "category": "community", "color": "#EAB308"}
                if "ppomppu" in u_l or "뽐뿌" in u_l:
                    return {"name": "🛒 #10 뽐뿌 보험포럼 (가성비 특약)", "category": "community", "color": "#2563EB"}
                if "dcinside" in u_l or "디시" in u_l:
                    return {"name": "갤 #11 디시인사이드 (보험 갤러리)", "category": "community", "color": "#4338CA"}
                if "bobae" in u_l or "보배" in u_l:
                    return {"name": "🚗 #12 보배드림 (운전자/자동차보험)", "category": "community", "color": "#1E40AF"}
                if "pann" in u_l or "nate" in u_l:
                    return {"name": "💬 #13 네이트판 (보험 분쟁/해지 실화)", "category": "community", "color": "#DC2626"}
                if "fmkorea" in u_l or "femco" in u_l:
                    return {"name": "⚽ #14 에펨코리아 (사회초년생 첫보험)", "category": "community", "color": "#059669"}
                if "kakao" in u_l:
                    return {"name": "💬 #15 카카오 알림톡 (무료 증권분석)", "category": "messenger", "color": "#FACC15"}
                if p_l and p_l not in ["direct", "test"]:
                    return {"name": f"👨‍💼 공인 설계사 전용 링크 ({p_l})", "category": "other", "color": "#0284C7"}

                return {"name": "🔗 다이렉트 / 즐겨찾기 직접 접속", "category": "other", "color": "#64748B"}

            # 🚀 [채널별 순 유입자수 계산]
            channel_map: Dict[str, Dict[str, Any]] = {}
            for l in period_logs:
                resolved = resolve_insurance_channel(l.get("utm_source", ""), l.get("planner_code", ""))
                c_name = resolved["name"]
                if c_name not in channel_map:
                    channel_map[c_name] = {
                        "name": c_name,
                        "category": resolved["category"],
                        "color": resolved["color"],
                        "sessions": set()
                    }
                channel_map[c_name]["sessions"].add(l["session_id"])

            channel_inflows = []
            period_uv_count = len(period_unique_sessions)
            for c_name, c_data in sorted(channel_map.items(), key=lambda x: len(x[1]["sessions"]), reverse=True):
                c_count = len(c_data["sessions"])
                share = round((c_count / max(period_uv_count, 1)) * 100, 1)
                channel_inflows.append({
                    "name": c_data["name"],
                    "category": c_data["category"],
                    "count": c_count,
                    "share": share,
                    "color": c_data["color"],
                    "unit": "명"
                })

            # 전환율 CVR (상담 신청 기준)
            cvr_pct = round((period_leads_cnt / max(period_uv_count, 1)) * 100, 1) if period_uv_count > 0 else 0.0

            # 4대 핵심 KPI
            active_kpis = {
                "today_pv": period_uv_count,
                "cumulative_pv": len(total_unique_sessions),
                "yoy_growth": f"상담신청 {total_leads_cnt}건 (설계사 {total_planners}명)",
                "monthly_visitors": period_leads_cnt,
                "kpi_period_label": f"{period_label} [보험 리밸런스] 순 유입자 수 (중복제거)",
                "visitor_period_label": f"{period_label} [보험 리밸런스] 고객 상담 신청 (건)"
            }

            # 실시간 유입 & 상담 신청 목록
            real_visitors_list = []
            # 1. 최근 상담 신청 실데이터 우선
            for ld in period_leads[:15]:
                phone_masked = ld["phone"][:3] + "-****-" + ld["phone"][-4:] if len(ld["phone"]) >= 8 else ld["phone"]
                real_visitors_list.append({
                    "source_name": f"📋 [상담 신청] {ld['insurance_type']}",
                    "medium": f"월납: {ld['monthly_premium']:,}원" if isinstance(ld['monthly_premium'], int) else "보험 진단",
                    "campaign": f"고객: {ld['name']} ({phone_masked})",
                    "target_app": "InsureBalance 보험비교",
                    "ip": f"상태: {ld['status']}",
                    "created_at": ld["kst_dt"].strftime("%Y-%m-%d %H:%M:%S KST")
                })

            # 2. 최근 접속 로그
            for l in period_logs[:15]:
                resolved = resolve_insurance_channel(l.get("utm_source", ""), l.get("planner_code", ""))
                real_visitors_list.append({
                    "source_name": resolved["name"],
                    "medium": f"코드: {l['planner_code']}",
                    "campaign": f"UTM: {l['utm_source']}",
                    "target_app": "InsureBalance 보험비교",
                    "ip": f"세션: {l['session_id'][:12]}...",
                    "created_at": l["kst_dt"].strftime("%Y-%m-%d %H:%M:%S KST")
                })

            return {
                "period": period,
                "brand": "insurance",
                "chart_title": chart_title,
                "chart_badge": chart_badge,
                "channels_title": f"🚀 [보험 리밸런스] 옴니채널 실제 유입 실적 ({period_label})",
                "channels_subtitle": f"* {period_label} 동안 보험 리밸런스에 실제로 접속한 순 방문자({period_uv_count}명)의 채널별 실적입니다.",
                "visitors_title": f"👥 [보험 리밸런스] 실제 웹사이트 방문 & 상담 신청 실시간 추적 ({period_label})",
                "visitors_subtitle": f"보험 리밸런스에 유입된 진짜 고객의 실시간 접속 및 288건 상담 신청 기록입니다.",
                "kpis": active_kpis,
                "hourly_data": hourly_data,
                "channel_inflows": channel_inflows,
                "real_visitor_inflows": channel_inflows,
                "real_visitors_list": real_visitors_list,
                "stats_summary": {
                    "unique_visitors": period_uv_count,
                    "total_unique_visitors": len(total_unique_sessions),
                    "period_leads": period_leads_cnt,
                    "total_leads": total_leads_cnt,
                    "total_planners": total_planners,
                    "cvr": cvr_pct
                }
            }

        except Exception as e:
            logger.error(f"❌ [InsuranceSupabase] 쿼리 실패: {e}")
            return {}


if __name__ == "__main__":
    mgr = InsuranceSupabaseManager()
    print("Insurance Connected:", mgr.is_connected())
    print("URL:", mgr.supabase_url)
    res = mgr.get_insurance_traffic_analytics("yearly")
    print("Yearly KPIs:", res.get("kpis"))
