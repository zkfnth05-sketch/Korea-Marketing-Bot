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
        - 앱 접속 유저 전원의 라운지 피드에 최신 칼럼 실시간 노출
        """
        title = article_pkg.get("title_kakao") or article_pkg.get("title_naver") or article_pkg.get("title", "")
        excerpt = article_pkg.get("excerpt", "")
        cat_key = article_pkg.get("category", "kakaotalk_signals")
        lounge_cat = self.map_category_to_lounge(cat_key)
        landing_url = article_pkg.get("landing_url", "https://aura-ai-dating.vercel.app/")
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
        post_id = f"mag-{article_pkg.get('topic_id', 1)}-{int(datetime.now().timestamp())}"

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


if __name__ == "__main__":
    mgr = AuraSupabaseManager()
    print("Supabase 연결 여부:", mgr.is_connected())
    print("URL:", mgr.supabase_url)
