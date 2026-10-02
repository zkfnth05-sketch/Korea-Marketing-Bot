# -*- coding: utf-8 -*-
"""
Aura Supabase Manager (💖 Aura 앱 자체 데이터베이스 연동 전담 모듈)
===================================================================
- 역할:
  1. Aura 전용 Supabase(https://ncflciezowwpnknuutko.supabase.co) 연결 관리
  2. [lounge_posts] 아우라 앱 라운지 실시간 피드에 공식 매거진 글 자동 등록 (앱 유저 실시간 노출)
  3. [aura_blogs] 3종 맞춤 제목 및 마크다운/HTML 원문 영구 아카이빙
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pathlib import Path
from dotenv import dotenv_values, load_dotenv

logger = logging.getLogger("AuraSupabaseManager")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent


class AuraSupabaseManager:
    """Aura 앱 자체 Supabase 연동 전담 매니저 (완전 독립 레고 블록)"""

    def __init__(self):
        self.client = None
        self.supabase_url = ""
        self.service_role_key = ""
        self._init_connection()

    def _init_connection(self):
        # 1. 환경변수 또는 accounts.json 우선 탐색
        load_dotenv(PROJECT_ROOT / ".env")
        url = os.getenv("AURA_SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        key = os.getenv("AURA_SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        # 2. aura-main/.env.local 에서 자동 로드 시도
        if not url or not key or "ncflciezowwpnknuutko" not in url:
            aura_main_env = Path(r"C:\Users\zkfnt\Desktop\aura-main\.env.local")
            if aura_main_env.exists():
                cfg = dotenv_values(aura_main_env)
                url = cfg.get("NEXT_PUBLIC_SUPABASE_URL") or url
                key = cfg.get("SUPABASE_SERVICE_ROLE_KEY") or cfg.get("NEXT_PUBLIC_SUPABASE_ANON_KEY") or key

        self.supabase_url = url or ""
        self.service_role_key = key or ""

        if self.supabase_url and self.service_role_key:
            try:
                from supabase import create_client
                self.client = create_client(self.supabase_url, self.service_role_key)
                logger.info(f"✅ [AuraSupabase] Aura 전용 Supabase 연결 성공 ({self.supabase_url})")
            except Exception as e:
                logger.warning(f"⚠️ [AuraSupabase] 클라이언트 초기화 실패: {e}")
                self.client = None
        else:
            logger.warning("⚠️ [AuraSupabase] Aura Supabase URL 또는 Key 미설정 (시뮬레이션 모드)")

    def is_connected(self) -> bool:
        return self.client is not None

    def upload_image_to_storage(self, local_image_path: str, bucket_subpath: str = "magazines") -> Optional[str]:
        """
        🖼️ 제미나이가 생성한 로컬 16:9 WebP 이미지를 Aura Supabase Storage(aura-media)에 업로드하고 영구 퍼블릭 URL 반환
        """
        if not self.is_connected() or not local_image_path:
            return None

        p = Path(local_image_path)
        if not p.exists() or p.stat().st_size == 0:
            logger.warning(f"⚠️ [AuraSupabase] 업로드할 이미지 파일이 존재하지 않음: {local_image_path}")
            return None

        import re
        safe_stem = re.sub(r'[^a-zA-Z0-9_\-]', '_', p.stem)
        file_name = f"{safe_stem}{p.suffix.lower()}"
        storage_path = f"{bucket_subpath}/{file_name}"

        try:
            with open(p, "rb") as f:
                img_bytes = f.read()

            suffix = p.suffix.lower()
            if suffix == ".mp4":
                content_type = "video/mp4"
            elif suffix == ".webp":
                content_type = "image/webp"
            elif suffix == ".png":
                content_type = "image/png"
            else:
                content_type = "image/jpeg"

            for attempt in range(3):
                try:
                    self.client.storage.from_("aura-media").upload(
                        path=storage_path,
                        file=img_bytes,
                        file_options={"content-type": content_type, "upsert": "true"}
                    )
                    public_url = self.client.storage.from_("aura-media").get_public_url(storage_path)
                    logger.info(f"✅ [AuraSupabase] Storage 업로드 성공! 영구 URL: {public_url}")
                    return public_url
                except Exception as e:
                    if attempt < 2:
                        import time
                        logger.warning(f"⚠️ [AuraSupabase] Storage 업로드 일시 지연/오류 ({e}), 1.5초 후 재시도 ({attempt+1}/2)...")
                        time.sleep(1.5)
                    else:
                        logger.error(f"❌ [AuraSupabase] Storage 업로드 최종 실패: {e}")
                        return None
        except Exception as e:
            logger.error(f"❌ [AuraSupabase] 이미지 파일 로드 예외: {e}")
            return None

    def map_category_to_lounge(self, cat_key: str) -> str:
        """Aura 6대 카테고리를 라운지 피드 카테고리로 매핑"""
        mapping = {
            "kakaotalk_signals": "연애상담",
            "blind_date_fashion": "소개팅후기",
            "dating_courses": "데이트코스",
            "conversation_skills": "연애상담",
            "mbti_chemistry": "연애상담",
            "self_esteem_confidence": "솔직고민"
        }
        return mapping.get(cat_key, "연애상담")

    def publish_to_lounge_feed(self, article_pkg: Dict[str, Any]) -> Dict[str, Any]:
        """
        📱 아우라 앱 라운지 실시간 피드(lounge_posts)에 공식 VIP 매거진 카드로 즉시 등록
        - 중복 원천 차단: 동일 주제(topic_id)에 대해 단 1개의 공식 매거진 글만 유지 (기존 중복 자동 갱신)
        - 제미나이 생성 맞춤 실사 사진 Supabase Storage 영구 연동
        """
        topic_id = article_pkg.get("topic_id", 1)
        # 아우라 본진 매거진 전용 타이틀 1개 선정 (소셜 감성 훅 우선)
        title = article_pkg.get("title_kakao") or article_pkg.get("title_naver") or article_pkg.get("title", "")
        excerpt = article_pkg.get("excerpt", "")
        cat_key = article_pkg.get("category", "kakaotalk_signals")
        lounge_cat = self.map_category_to_lounge(cat_key)
        landing_url = article_pkg.get("landing_url", "https://aura-ai-dating.vercel.app/")

        # 🖼️ 제미나이 생성 이미지 Supabase Storage 업로드 및 영구 URL 획득
        local_img_path = article_pkg.get("image_path", "")
        img_url = ""
        if local_img_path and Path(local_img_path).exists():
            uploaded_url = self.upload_image_to_storage(local_img_path, bucket_subpath="magazines")
            if uploaded_url:
                img_url = uploaded_url
                article_pkg["image_url"] = uploaded_url  # 패키지 내 URL도 영구 퍼블릭 URL로 갱신

        if not img_url:
            img_url = article_pkg.get("image_url", "")

        # 라운지 피드용 본문 구성: 제미나이가 작성한 2,000자 칼럼 전문 온전히 탑재 (내부 피드이므로 외부 링크 제거)
        full_content = article_pkg.get("content_md") or excerpt
        import re
        full_content = re.sub(r'!\[.*?\]\(.*?\)', '', full_content).strip()
        if full_content.startswith("# "):
            full_content = full_content.split("\n", 1)[-1].strip()

        discussion_prompt = article_pkg.get("discussion_prompt") or "Aura 싱글 여러분의 생각은 어떠신가요? 아래 댓글로 여러분만의 솔직한 생각과 꿀팁을 남겨주세요! 👇"

        lounge_body = (
            f"📌 {title}\n\n"
            f"{full_content}"
        )

        # 🌐 4개 국어(KO 원문 + EN, JA, ES) 라운지 피드 실시간 자동 번역 및 discussion_prompt 저장
        lounge_trans = article_pkg.get("translations", {}).get("lounge") if isinstance(article_pkg.get("translations"), dict) else None
        if not lounge_trans or not isinstance(lounge_trans, dict) or not lounge_trans.get("en"):
            try:
                from .aura_translator import AuraTranslator
                translator = AuraTranslator()
                lounge_trans = translator.translate_lounge_content(lounge_body)
                logger.info(f"🌐 [AuraSupabase] 라운지 3개국어(EN, JA, ES) 실시간 번역 생성 완료")
            except Exception as e:
                logger.warning(f"⚠️ [AuraSupabase] 라운지 번역 생성 실패: {e}")
                lounge_trans = {"en": lounge_body, "ja": lounge_body, "es": lounge_body}

        # 💬 [티키타카 댓글 유도 질문] translations JSONB에 안전하게 보관 (DB 스키마 변경 불필요)
        lounge_trans["discussion_prompt"] = discussion_prompt

        now_iso = datetime.now(timezone.utc).isoformat()
        # 🔑 고유 ID 규칙: 주제 번호 기반 고정 ID로 중복 등록 원천 방지
        post_id = f"mag-topic-{topic_id:03d}"

        row = {
            "id": post_id,
            "user_id": "aura-official-editor",
            "user_name": "💖 Aura 공식 매거진",
            "user_avatar": "https://ncflciezowwpnknuutko.supabase.co/storage/v1/object/public/aura-media/branding/aura_magazine_logo.jpg",
            "user_age": 26,
            "user_gender": "공식",
            "user_location": "서울",
            "is_vip": True,
            "content": lounge_body,
            "image_urls": [img_url] if img_url else [],
            "tags": article_pkg.get("tags", ["매거진", "연애팁", "Aura"]),
            "likes_count": 18,
            "is_anonymous": False,
            "category": lounge_cat,
            "translations": lounge_trans,
            "created_at": now_iso
        }

        if not self.is_connected():
            logger.info(f"[DRY-RUN] Aura 라운지 피드 등록 시뮬레이션: '{title}' ({lounge_cat})")
            return {"status": "success", "mode": "dry_run", "post_id": post_id, "category": lounge_cat}

        try:
            # 🛡️ [중복 원천 제거] 기존에 동일 주제나 공식 에디터로 작성된 구형 글이 있으면 먼저 삭제
            try:
                self.client.table("lounge_posts").delete().eq("id", post_id).execute()
                # 과거 타임스탬프 형식의 중복 글(예: mag-1-..., mag-8-...)도 정리
                self.client.table("lounge_posts").delete().like("id", f"mag-{topic_id}-%").execute()
            except Exception as del_err:
                logger.debug(f"기존 구형 매거진 글 삭제 확인: {del_err}")

            res = self.client.table("lounge_posts").insert(row).execute()
            if res.data:
                logger.info(f"✅ [AuraSupabase] 라운지 피드 4개국어 등록 완료 (ID: {post_id}, 카테고리: {lounge_cat})")
                return {"status": "success", "post_id": post_id, "data": res.data[0]}
            else:
                logger.warning(f"⚠️ [AuraSupabase] 라운지 피드 등록 응답 없음")
                return {"status": "warning", "post_id": post_id}
        except Exception as e:
            logger.error(f"❌ [AuraSupabase] 라운지 피드 등록 실패: {e}")
            return {"status": "error", "message": str(e)}

    def clean_legacy_duplicate_posts(self) -> Dict[str, Any]:
        """
        🧹 과거 테스트로 인해 lounge_posts에 쌓인 중복 매거진 글 일괄 정리
        """
        if not self.is_connected():
            return {"status": "not_connected"}

        try:
            # 공식 에디터 글 중 타임스탬프 형식(mag-...)으로 중복 등록된 글 조회 및 삭제
            res = self.client.table("lounge_posts").select("id").eq("user_id", "aura-official-editor").execute()
            legacy_ids = [r["id"] for r in (res.data or []) if not r["id"].startswith("mag-topic-")]
            if legacy_ids:
                del_res = self.client.table("lounge_posts").delete().in_("id", legacy_ids).execute()
                logger.info(f"🧹 [AuraSupabase] 과거 중복 매거진 글 {len(legacy_ids)}건 삭제 완료: {legacy_ids}")
                return {"status": "success", "deleted_count": len(legacy_ids), "deleted_ids": legacy_ids}
            return {"status": "success", "deleted_count": 0}
        except Exception as e:
            logger.error(f"❌ [AuraSupabase] 과거 중복 글 정리 실패: {e}")
            return {"status": "error", "message": str(e)}

    def archive_article_to_aura_blogs(self, article_pkg: Dict[str, Any]) -> Dict[str, Any]:
        """
        📚 aura_blogs 테이블에 3종 제목, 2,000자 원고 및 4개 국어 번역 영구 아카이빙
        """
        translations_data = article_pkg.get("translations", {})
        row = {
            "topic_id": article_pkg.get("topic_id", 1),
            "category": article_pkg.get("category", "kakaotalk_signals"),
            "category_name": article_pkg.get("category_name", "2030 라이프"),
            "title_naver": article_pkg.get("title_naver", ""),
            "title_tistory": article_pkg.get("title_tistory", ""),
            "title_kakao": article_pkg.get("title_kakao", ""),
            "title": article_pkg.get("title", ""),
            "excerpt": article_pkg.get("excerpt", ""),
            "content_md": article_pkg.get("content_md", ""),
            "content_html": article_pkg.get("content_html", ""),
            "thumbnail_url": article_pkg.get("image_url", ""),
            "visual_prompt": article_pkg.get("visual_prompt", ""),
            "tags": article_pkg.get("tags", []),
            "landing_url": article_pkg.get("landing_url", "https://aura-ai-dating.vercel.app/"),
            "translations": translations_data,
            "published_at": datetime.now(timezone.utc).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        if not self.is_connected():
            return {"status": "success", "mode": "dry_run"}

        try:
            res = self.client.table("aura_blogs").insert(row).execute()
            logger.info("✅ [AuraSupabase] aura_blogs 4개국어 아카이브 저장 완료")
            self._save_local_archive(article_pkg)
            return {"status": "success", "data": res.data}
        except Exception as e:
            err_msg = str(e)
            if "translations" in err_msg and "column" in err_msg:
                try:
                    row_no_trans = dict(row)
                    row_no_trans.pop("translations", None)
                    res = self.client.table("aura_blogs").insert(row_no_trans).execute()
                    logger.info("✅ [AuraSupabase] aura_blogs 아카이브 저장 완료 (기존 컬럼 호환 모드)")
                    self._save_local_archive(article_pkg)
                    return {"status": "success", "data": res.data}
                except Exception as e2:
                    logger.warning(f"⚠️ [AuraSupabase] aura_blogs 재시도 실패: {e2}")

            # aura_blogs 테이블이 아직 생성되지 않은 경우 안내 및 로컬 백업
            logger.info(f"ℹ️ [AuraSupabase] aura_blogs 테이블 미생성 상태 ({e}) - 로컬 백업 저장")
            self._save_local_archive(article_pkg)
            return {"status": "pending_table", "hint": "Run aura_supabase_schema.sql in Supabase SQL Editor"}

    def _save_local_archive(self, article_pkg: Dict[str, Any]):
        out_dir = PROJECT_ROOT / "outputs" / "aura" / "blogs"
        out_dir.mkdir(parents=True, exist_ok=True)
        fname = f"aura_blog_topic_{article_pkg.get('topic_id', 1):03d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(out_dir / fname, "w", encoding="utf-8") as fp:
            json.dump(article_pkg, fp, ensure_ascii=False, indent=2)
        logger.info(f"💾 [AuraSupabase] 로컬 JSON 안전 백업 완료: {fname}")

    def get_aura_traffic_analytics(self, period: str = "today") -> Dict[str, Any]:
        """
        📊 Aura Supabase (site_traffic_logs & users) 100% 실데이터 기반 순 유입자 & 회원가입 분석
        - 🌟 대표님 철칙: 한 사람이 하루에 10번 방문하더라도 session_id 기준 '정확히 1명'으로 중복 제거(Unique Visitor)
        - 📅 오늘 24H / 📊 주간 7일 / 📈 월간 30일 / 🏆 연간 (Yearly/IR) 완벽 분기
        - 🚀 15대 옴니채널별 실제 유입자 수 및 점유율 계산
        """
        from datetime import datetime, timezone, timedelta
        kst = timezone(timedelta(hours=9))
        kst_now = datetime.now(kst)
        today_date = kst_now.date()

        if not self.is_connected():
            return {}

        try:
            # 1. site_traffic_logs 전체 실데이터 조회
            res_logs = self.client.table("site_traffic_logs").select("*").order("created_at", desc=True).limit(5000).execute()
            raw_logs = res_logs.data or []

            # 2. users 전체 회원가입 실데이터 조회
            res_users = self.client.table("users").select("id, name, gender, age, created_at, admission_status").order("created_at", desc=True).execute()
            raw_users = res_users.data or []

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
                        "path": r.get("path") or "/",
                        "referrer": r.get("referrer") or "Direct",
                        "channel": r.get("channel") or "다이렉트 / 북마크",
                        "channel_category": r.get("channel_category") or "direct",
                        "device": r.get("device") or "mobile",
                        "kst_dt": dt_k
                    })

            # 유저 데이터 전처리
            parsed_users = []
            for u in raw_users:
                dt_k = parse_kst(u.get("created_at"))
                if dt_k:
                    parsed_users.append({
                        "id": u.get("id"),
                        "name": u.get("name") or "익명",
                        "gender": u.get("gender") or "미설정",
                        "age": u.get("age") or 25,
                        "admission_status": u.get("admission_status") or "active",
                        "kst_dt": dt_k
                    })

            # 기간별 필터링 함수 (KST 기준)
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
            period_users = [u for u in parsed_users if is_in_period(u["kst_dt"], period)]

            # 🌟 [순 방문자수 계산] session_id 기준 중복 100% 제거
            total_unique_sessions = set(l["session_id"] for l in parsed_logs)
            period_unique_sessions = set(l["session_id"] for l in period_logs)
            today_unique_sessions = set(l["session_id"] for l in parsed_logs if l["kst_dt"].date() == today_date)

            total_signups = len(parsed_users)
            period_signups = len(period_users)
            today_signups = len([u for u in parsed_users if u["kst_dt"].date() == today_date])

            # 기간별 차트 데이터 생성
            if period == "weekly":
                date_list = [(today_date - timedelta(days=i)) for i in range(6, -1, -1)]
                weekly_sessions = {d.strftime("%Y-%m-%d"): set() for d in date_list}
                for l in period_logs:
                    d_str = l["kst_dt"].strftime("%Y-%m-%d")
                    if d_str in weekly_sessions:
                        weekly_sessions[d_str].add(l["session_id"])
                hourly_data = [{"hour": d.strftime("%m/%d"), "count": len(weekly_sessions[d.strftime("%Y-%m-%d")])} for d in date_list]
                chart_title = "📊 [Aura 데이팅] 최근 7일간 일별 순 방문자 유입 추이 (KST)"
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
                chart_title = "📊 [Aura 데이팅] 최근 4주간 주차별 순 방문자 유입 추이 (KST)"
                chart_badge = "기준: 최근 30일 순 방문자(중복제거)"
                period_label = "최근 30일"

            elif period == "yearly":
                mon_sessions = {m: set() for m in range(1, 13)}
                for l in period_logs:
                    if l["kst_dt"].year == today_date.year:
                        mon_sessions[l["kst_dt"].month].add(l["session_id"])
                hourly_data = [{"hour": f"{m}월", "count": len(mon_sessions[m])} for m in range(1, 13)]
                chart_title = f"📊 [Aura 데이팅] {today_date.year}년 연간 월별 순 방문자 유입 추이 (KST)"
                chart_badge = f"기준: {today_date.year}년 연간 순 방문자(중복제거)"
                period_label = f"{today_date.year}년 연간"

            else: # today
                hr_sessions = {h: set() for h in range(24)}
                for l in period_logs:
                    hr_sessions[l["kst_dt"].hour].add(l["session_id"])
                hourly_data = [{"hour": f"{h:02d}시", "count": len(hr_sessions[h])} for h in range(24)]
                chart_title = "📊 [Aura 데이팅] 오늘 24시간 시간대별 순 방문자 유입 추이 (00시~23시 KST)"
                chart_badge = "기준: 오늘 24H 순 방문자(중복제거)"
                period_label = "오늘 24H"

            # 🌟 [15대 마케팅 허브 전담 채널 리졸버]
            def resolve_marketing_channel(referrer_str: str, raw_ch: str, path_str: str) -> Dict[str, str]:
                ref_l = (referrer_str or "").lower()
                ch_l = (raw_ch or "").lower()
                
                # 1. 숏폼 & SNS (#1 숏폼 / #2 카드뉴스)
                if any(k in ref_l for k in ["youtube.com", "youtu.be"]) or "유튜브" in ch_l or "youtube" in ch_l:
                    return {"name": "🎬 #1 유튜브 쇼츠 (YouTube Shorts)", "category": "global_sns", "color": "#EF4444"}
                if "tiktok.com" in ref_l or "틱톡" in ch_l or "tiktok" in ch_l:
                    return {"name": "🎬 #1 틱톡 (TikTok)", "category": "global_sns", "color": "#06B6D4"}
                if "instagram.com" in ref_l or "인스타" in ch_l or "instagram" in ch_l:
                    return {"name": "📸 #2 인스타그램 (릴스 & 피드)", "category": "global_sns", "color": "#EC4899"}
                if any(k in ref_l for k in ["facebook.com", "fb.com"]) or "페이스북" in ch_l or "facebook" in ch_l:
                    return {"name": "📸 #2 페이스북 (릴스 & 그룹)", "category": "global_sns", "color": "#3B82F6"}
                if "post.naver.com" in ref_l or "네이버 포스트" in ch_l:
                    return {"name": "📸 #2 네이버 포스트 (매거진)", "category": "global_sns", "color": "#10B981"}

                # 2. Reddit (#3 리드헌터)
                if "reddit.com" in ref_l or "레딧" in ch_l or "reddit" in ch_l:
                    return {"name": "🤖 #3 Reddit (1:1 리드 헌터)", "category": "community", "color": "#F97316"}

                # 3. 블로그 & 검색 (#4 옴니블로그 / #5 검색엔진 / #7 지식iN)
                if "blog.naver.com" in ref_l or "네이버 블로그" in ch_l or ("naver.com" in ref_l and "blog" in ref_l):
                    return {"name": "💖 #4 네이버 블로그 (스마트블록)", "category": "seo_blog", "color": "#10B981"}
                if "tistory.com" in ref_l or "티스토리" in ch_l:
                    return {"name": "💖 #4 티스토리 (Google SEO)", "category": "seo_blog", "color": "#F97316"}
                if "brunch.co.kr" in ref_l or "브런치" in ch_l:
                    return {"name": "💖 #4 카카오 브런치 (감성 에세이)", "category": "seo_blog", "color": "#334155"}
                if "lounge" in (path_str or "").lower() or "lounge" in ref_l or "라운지" in ch_l:
                    return {"name": "💖 #4 Aura 라운지 매거진 (피드)", "category": "seo_blog", "color": "#EC4899"}
                if "kin.naver.com" in ref_l or "지식in" in ch_l or "지식인" in ch_l:
                    return {"name": "💡 #7 네이버 지식iN (100대 황금키워드)", "category": "seo_blog", "color": "#10B981"}
                if any(k in ref_l for k in ["search.naver.com", "naver.com"]) or "네이버 검색" in ch_l:
                    return {"name": "🌐 #5 네이버 검색 (서치어드바이저)", "category": "seo_blog", "color": "#10B981"}
                if "google.com" in ref_l or "구글" in ch_l or "google" in ch_l:
                    return {"name": "🌐 #5 구글 검색 (서치콘솔 색인)", "category": "seo_blog", "color": "#3B82F6"}

                # 4. 스토리 타래 (#6)
                if "threads.net" in ref_l or "스레드" in ch_l or "threads" in ch_l:
                    return {"name": "📜 #6 Meta 스레드 (바이럴 타래)", "category": "community", "color": "#0F172A"}
                if any(k in ref_l for k in ["twitter.com", "x.com"]) or "트위터" in ch_l or "twitter" in ch_l:
                    return {"name": "📜 #6 X / 트위터 (바이럴 타래)", "category": "community", "color": "#0284C7"}

                # 5. 카페 & 커뮤니티 (#8 ~ #14)
                if "cafe.naver.com" in ref_l or "네이버 카페" in ch_l:
                    return {"name": "☕ #8 네이버 카페 (2030 친목/직장인)", "category": "community", "color": "#10B981"}
                if "cafe.daum.net" in ref_l or "다음 카페" in ch_l or "daum" in ch_l:
                    return {"name": "🍵 #9 다음(Daum) 카페 (공감 썰)", "category": "community", "color": "#EAB308"}
                if "ppomppu.co.kr" in ref_l or "뽐뿌" in ch_l:
                    return {"name": "🛒 #10 뽐뿌 포럼 (솔로 탈출 후기)", "category": "community", "color": "#2563EB"}
                if "dcinside.com" in ref_l or "디시" in ch_l:
                    return {"name": "갤 #11 디시인사이드 (연애 갤러리)", "category": "community", "color": "#4338CA"}
                if "bobaedream.co.kr" in ref_l or "보배" in ch_l:
                    return {"name": "🚗 #12 보배드림 (3040 연애 팁)", "category": "community", "color": "#1E40AF"}
                if "pann.nate.com" in ref_l or "네이트판" in ch_l or "nate" in ref_l:
                    return {"name": "💬 #13 네이트판 (톡커들의 선택)", "category": "community", "color": "#DC2626"}
                if "fmkorea.com" in ref_l or "펨코" in ch_l or "에펨" in ch_l:
                    return {"name": "⚽ #14 에펨코리아 (2030 남성 대화법)", "category": "community", "color": "#059669"}

                # 6. 메신저 (#15)
                if "kakao" in ref_l or "카카오" in ch_l:
                    return {"name": "💬 #15 카카오 알림톡 & 채널", "category": "messenger", "color": "#FACC15"}

                # 7. 기타 다이렉트 / 외부 웹
                if "direct" in ref_l or "direct" in ch_l or not referrer_str or referrer_str == "Direct":
                    return {"name": "🔗 다이렉트 / 즐겨찾기 직접 접속", "category": "other", "color": "#64748B"}
                
                return {"name": f"🌐 외부 웹사이트 ({raw_ch or '직접 링크'})", "category": "other", "color": "#8B5CF6"}

            # 🚀 [15대 옴니채널별 실제 순 유입자 수 계산] (각 채널별 중복 session_id 제거)
            channel_map: Dict[str, Dict[str, Any]] = {}
            for l in period_logs:
                resolved = resolve_marketing_channel(l.get("referrer", ""), l.get("channel", ""), l.get("path", ""))
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

            # 전환율 CVR
            cvr_pct = round((period_signups / max(period_uv_count, 1)) * 100, 1) if period_uv_count > 0 else 0.0

            # 4대 핵심 KPI (Aura 100% 실데이터)
            active_kpis = {
                "today_pv": period_uv_count,
                "cumulative_pv": len(total_unique_sessions),
                "yoy_growth": f"회원가입 {total_signups}명 (오늘 {today_signups}명)",
                "monthly_visitors": period_signups,
                "visitor_unit": "명",
                "kpi_period_label": f"{period_label} [Aura] 순 유입자 수 (중복제거)",
                "visitor_period_label": f"{period_label} [Aura] 실제 신규 회원가입 (명)"
            }

            # 실시간 유입 & 가입 추적 목록
            real_visitors_list = []
            for l in period_logs[:30]:
                resolved = resolve_marketing_channel(l.get("referrer", ""), l.get("channel", ""), l.get("path", ""))
                real_visitors_list.append({
                    "source_name": resolved["name"],
                    "medium": l["device"],
                    "campaign": l["path"],
                    "target_app": "Aura AI 데이팅",
                    "ip": f"세션: {l['session_id'][:12]}...",
                    "created_at": l["kst_dt"].strftime("%Y-%m-%d %H:%M:%S KST")
                })

            return {
                "period": period,
                "brand": "aura",
                "chart_title": chart_title,
                "chart_badge": chart_badge,
                "channels_title": f"🚀 [Aura 데이팅] 옴니채널 실제 유입 실적 ({period_label})",
                "channels_subtitle": f"* {period_label} 동안 Aura 데이팅에 실제로 접속한 순 방문자({period_uv_count}명)의 채널별 실적입니다.",
                "visitors_title": f"👥 [Aura 데이팅] 실제 웹사이트 방문자(순 유입) 실시간 추적 ({period_label})",
                "visitors_subtitle": f"Aura 데이팅에 접속한 진짜 사람의 {period_label} 실시간 접속 기록입니다 (동일인 중복 카운트 0%).",
                "kpis": active_kpis,
                "hourly_data": hourly_data,
                "channel_inflows": channel_inflows,
                "real_visitor_inflows": channel_inflows,
                "real_visitors_list": real_visitors_list,
                "stats_summary": {
                    "unique_visitors": period_uv_count,
                    "total_unique_visitors": len(total_unique_sessions),
                    "period_signups": period_signups,
                    "total_signups": total_signups,
                    "cvr": cvr_pct
                }
            }

        except Exception as e:
            logger.error(f"❌ [AuraSupabase] 유입 분석 쿼리 실패: {e}")
            return {}


if __name__ == "__main__":
    mgr = AuraSupabaseManager()
    print("Supabase 연결 여부:", mgr.is_connected())
    print("URL:", mgr.supabase_url)
    res = mgr.get_aura_traffic_analytics("today")
    print("Today KPIs:", res.get("kpis"))
