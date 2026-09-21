# -*- coding: utf-8 -*-
"""
📈 StockMaster Supabase Research Publisher (본진 웹앱 퀀트 리서치 연동 모듈)
===========================================================================
- 마케팅봇이 발행하는 1600x1600 캡처 및 퀀트 분석 칼럼을 Supabase DB에 실시간 INSERT
- 본진 웹앱(Stock Master AI)의 [퀀트 리서치] 탭에서 즉시 열람 가능
- RLS 보안 정책 준수 (service_role 키를 통한 안전한 발행)
"""

import os
import json
import logging
import base64
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("StockSupabasePublisher")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
STOCK_APP_DIR = Path(r"C:\Users\zkfnt\Desktop\stock ai\stock")
STOCK_ENV_FILE = STOCK_APP_DIR / ".env"


def load_stock_env() -> Dict[str, str]:
    """stock ai/stock/.env 파일에서 환경 변수 파싱"""
    env_vars = {}
    if STOCK_ENV_FILE.exists():
        try:
            content = STOCK_ENV_FILE.read_text(encoding="utf-8")
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env_vars[k.strip()] = v.strip().strip('"').strip("'")
        except Exception as e:
            logger.warning(f"⚠️ stock .env 읽기 실패: {e}")
    return env_vars


class StockSupabasePublisher:
    """본진 웹앱 Supabase quant_research_posts 테이블 실시간 발행기"""

    def __init__(self):
        env_vars = load_stock_env()
        self.supabase_url = env_vars.get("SUPABASE_URL") or os.getenv("SUPABASE_URL", "")
        self.service_key = (
            env_vars.get("SUPABASE_SERVICE_KEY")
            or env_vars.get("SUPABASE_KEY")
            or os.getenv("SUPABASE_SERVICE_KEY", "")
        )
        self.anon_key = env_vars.get("SUPABASE_KEY", "")
        self.client = None

        if self.supabase_url and self.service_key:
            try:
                from supabase import create_client
                self.client = create_client(self.supabase_url, self.service_key)
                logger.info("✅ [StockSupabase] Supabase 클라이언트 연결 성공")
            except Exception as e:
                logger.error(f"❌ [StockSupabase] 클라이언트 초기화 실패: {e}")
        else:
            logger.warning("⚠️ [StockSupabase] SUPABASE_URL 또는 SUPABASE_KEY가 설정되지 않았습니다.")

    def is_available(self) -> bool:
        return self.client is not None

    def publish_research(
        self,
        category: str,
        title: str,
        summary: str,
        target_stock: str,
        quant_data: Dict[str, Any],
        content_markdown: str,
        image_path: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Supabase quant_research_posts 테이블에 신규 퀀트 리포트 등록
        """
        if not self.is_available():
            return {"status": "skipped", "message": "Supabase client not initialized"}

        try:
            # 1. 이미지 처리 (Base64 Data URI로 저장하여 별도 스토리지 의존 없이 영구 보존)
            image_url = ""
            if image_path and Path(image_path).exists():
                try:
                    img_bytes = Path(image_path).read_bytes()
                    # 1.8MB 이내면 바로 data URI로 저장
                    if len(img_bytes) < 2 * 1024 * 1024:
                        b64_str = base64.b64encode(img_bytes).decode("utf-8")
                        image_url = f"data:image/png;base64,{b64_str}"
                    else:
                        image_url = str(image_path)
                except Exception as e:
                    logger.warning(f"이미지 인코딩 실패: {e}")

            # 2. 본문 HTML 변환
            content_html = self._format_html(content_markdown)

            post_data = {
                "category": category,
                "title": title,
                "summary": summary,
                "target_stock": target_stock,
                "quant_data": quant_data or {},
                "image_url": image_url,
                "content_html": content_html,
                "content_markdown": content_markdown,
                "tags": tags or ["주식AI", "퀀트리서치", "StockMaster", target_stock.split()[0] if target_stock else ""],
                "is_published": True,
                "created_at": datetime.utcnow().isoformat()
            }

            res = self.client.table("quant_research_posts").insert(post_data).execute()
            
            if res.data and len(res.data) > 0:
                post_id = res.data[0].get("id")
                logger.info(f"🎉 [StockSupabase] 본진 퀀트 리서치 등록 성공! (ID: {post_id}, 제목: '{title}')")
                return {
                    "status": "success",
                    "post_id": post_id,
                    "title": title,
                    "category": category
                }
            else:
                logger.error(f"❌ [StockSupabase] 등록 응답 데이터 없음: {res}")
                return {"status": "error", "message": "No data returned"}

        except Exception as e:
            logger.error(f"❌ [StockSupabase] 발행 중 오류: {e}")
            return {"status": "error", "message": str(e)}

    def fetch_latest_posts(self, limit: int = 20, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """최신 리서치 칼럼 목록 조회 (프론트/테스트용)"""
        if not self.is_available():
            return []
        try:
            query = self.client.table("quant_research_posts").select("*").eq("is_published", True).order("created_at", desc=True).limit(limit)
            if category and category != "ALL":
                query = query.eq("category", category)
            res = query.execute()
            return res.data or []
        except Exception as e:
            logger.error(f"❌ [StockSupabase] 포스트 조회 실패: {e}")
            return []

    @staticmethod
    def _format_html(markdown_text: str) -> str:
        """마크다운을 가독성 높은 HTML 블록으로 변환"""
        import re
        html = markdown_text
        html = re.sub(r'### (.*?)\n', r'<h3 class="text-xl font-bold text-cyan-300 mt-6 mb-3 flex items-center gap-2"><span>✨</span>\1</h3>', html)
        html = re.sub(r'## (.*?)\n', r'<h2 class="text-2xl font-black text-white mt-8 mb-4 border-b border-white/10 pb-2 flex items-center gap-2"><span>📈</span>\1</h2>', html)
        html = re.sub(r'# (.*?)\n', r'<h1 class="text-3xl font-black text-white mt-4 mb-4">\1</h1>', html)
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong class="text-cyan-300 font-bold">\1</strong>', html)
        html = re.sub(r'^- (.*?)$', r'<li class="ml-4 text-white/80 list-disc">\1</li>', html, flags=re.MULTILINE)
        html = html.replace("\n\n", "</p><p class=\"text-white/80 leading-relaxed mb-4\">")
        return f'<div class="quant-article-body text-white/80 leading-relaxed"><p class="mb-4">{html}</p></div>'


if __name__ == "__main__":
    pub = StockSupabasePublisher()
    print("Is Supabase available:", pub.is_available())
    if pub.is_available():
        posts = pub.fetch_latest_posts(limit=3)
        print(f"Current posts in DB: {len(posts)}")
