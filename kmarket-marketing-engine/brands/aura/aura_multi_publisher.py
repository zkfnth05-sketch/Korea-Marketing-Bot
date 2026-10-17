# -*- coding: utf-8 -*-
"""
Aura Multi-Platform Publisher (💖 Aura 4대 채널 옴니 무인 자동 배포 매니저)
=========================================================================
- 역할:
  1. 💖 [Aura App Supabase]: 라운지 실시간 VIP 피드(lounge_posts, 4개국어 번역) 및 아카이브(aura_blogs) 즉시 등록
  2. 🟢 [네이버 블로그]: 'title_naver' (스마트블록 최적화 제목) + SmartEditor ONE 고품질 자동 발행
  3. 🟠 [티스토리]: 'title_tistory' (구글 SEO / Daum 검색 최적화 제목) + HTML 서식 완전 무인 발행
  4. 🟡 [카카오 브런치]: 'title_kakao' (소셜 감성 훅) + 브런치스토리 전용 아카이브 및 승인 연동
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")
logger = logging.getLogger("AuraMultiPublisher")

from brands.aura.aura_supabase_manager import AuraSupabaseManager
from brands.aura.aura_naver_publisher import AuraNaverPublisher
from brands.aura.aura_tistory_publisher import AuraTistoryPublisher
from brands.aura.aura_brunch_publisher import AuraBrunchPublisher


class AuraMultiPublisher:
    """Aura 2030 매거진 4대 채널 동시 무인 배포 오케스트레이터 (완전 독립 레고 블록)"""

    def __init__(self):
        self.supabase_mgr = AuraSupabaseManager()
        self.accounts = self._load_accounts()

        creds = self.accounts.get("credentials", {})
        
        # 1. 네이버 블로그 퍼블리셔
        naver_id = creds.get("naver_blog_id") or os.getenv("NAVER_BLOG_ID", "zkfnth01")
        self.naver_pub = AuraNaverPublisher(blog_id=naver_id)

        # 2. 티스토리 블로그 퍼블리셔
        tistory_name = creds.get("tistory_blog_name") or os.getenv("TISTORY_BLOG_NAME", "aura-magazine")
        self.tistory_pub = AuraTistoryPublisher(blog_name=tistory_name)

        # 3. 카카오 브런치스토리 퍼블리셔
        self.brunch_pub = AuraBrunchPublisher()

    def _load_accounts(self) -> Dict[str, Any]:
        acc_path = CURRENT_DIR / "accounts.json"
        if acc_path.exists():
            try:
                with open(acc_path, "r", encoding="utf-8") as fp:
                    return json.load(fp)
            except Exception as e:
                logger.warning(f"⚠️ accounts.json 로드 실패: {e}")
        return {}

    def publish_all(self, article_pkg: Dict[str, Any]) -> Dict[str, Any]:
        """
        4대 채널 동시 옴니채널 자동 배포 실행
        """
        topic_id = article_pkg.get("topic_id", 1)
        title_naver = article_pkg.get("title_naver", article_pkg.get("title", ""))
        title_tistory = article_pkg.get("title_tistory", article_pkg.get("title", ""))
        title_kakao = article_pkg.get("title_kakao", article_pkg.get("title", ""))
        category_name = article_pkg.get("category_name", "카톡 시그널 & 밀당")
        content_html = article_pkg.get("content_html", "")
        content_md = article_pkg.get("content_md", "")
        excerpt = article_pkg.get("excerpt", "")
        tags = article_pkg.get("tags", [])
        img_path = article_pkg.get("image_path", "")
        landing_url = article_pkg.get("landing_url", "https://aura-ai-dating.vercel.app/")

        logger.info(f"\n" + "=" * 60)
        logger.info(f"🚀 [Aura 4대 채널 무인 배포 가동] 주제 #{topic_id}")
        logger.info(f"  🟢 네이버 제목: {title_naver}")
        logger.info(f"  🟠 티스토리 제목: {title_tistory}")
        logger.info(f"  🟡 카카오/브런치 제목: {title_kakao}")
        logger.info("=" * 60)

        results = {
            "topic_id": topic_id,
            "channels": {}
        }

        # 1. 💖 Aura 앱 자체 Supabase 등록 (lounge_posts 4개국어 피드 & aura_blogs 아카이브)
        try:
            feed_res = self.supabase_mgr.publish_to_lounge_feed(article_pkg)
            archive_res = self.supabase_mgr.archive_article_to_aura_blogs(article_pkg)
            results["channels"]["aura_app"] = {
                "status": feed_res.get("status", "success"),
                "feed_post_id": feed_res.get("post_id"),
                "translations_count": len(article_pkg.get("translations", {})),
                "lounge_url": "https://aura-ai-dating.vercel.app/"
            }
            logger.info(f"✅ [1/4] 💖 Aura 앱 라운지 피드 등록 완료 (글ID: {feed_res.get('post_id')})")
        except Exception as e:
            logger.error(f"❌ [1/4] 💖 Aura 앱 등록 실패: {e}")
            results["channels"]["aura_app"] = {"status": "error", "message": str(e)}

        # 2. 🟢 네이버 블로그 자동 발행 (title_naver)
        try:
            # 본문 텍스트 정리 (마크다운 헤더 등 가독성 최적화)
            naver_text = content_md if content_md else excerpt
            naver_res = self.naver_pub.publish_article(
                title=title_naver,
                content_text=naver_text,
                tag_list=tags,
                image_paths=[img_path] if img_path else [],
                category_name=category_name,
                landing_url=landing_url
            )
            results["channels"]["naver_blog"] = naver_res
            logger.info(f"✅ [2/4] 🟢 네이버 블로그 발행: '{title_naver}' -> {naver_res.get('url', '')}")
        except Exception as e:
            logger.error(f"❌ [2/4] 🟢 네이버 블로그 발행 실패: {e}")
            results["channels"]["naver_blog"] = {"status": "error", "message": str(e)}

        # 3. 🟠 티스토리 자동 발행 (title_tistory) — 최대 3회 재시도
        import time as _time
        tistory_res = {"status": "error", "message": "재시도 소진"}
        for _attempt in range(1, 4):
            try:
                tistory_res = self.tistory_pub.publish_post(
                    title=title_tistory,
                    content_html=content_html,
                    tag_list=tags
                )
                t_status = tistory_res.get("status", "")
                if t_status in ("success", "active", "restored"):
                    logger.info(f"✅ [3/4] 🟠 티스토리 발행 성공 (시도 {_attempt}): '{title_tistory}' -> {tistory_res.get('url', '')}")
                    break
                elif t_status == "session_expired":
                    logger.warning(f"⚠️ [3/4] 티스토리 세션 만료 (시도 {_attempt}/3), 10초 후 재시도...")
                    _time.sleep(10)
                else:
                    logger.warning(f"⚠️ [3/4] 티스토리 실패 (시도 {_attempt}/3): {tistory_res.get('message')}, 10초 후 재시도...")
                    _time.sleep(10)
            except Exception as e:
                logger.error(f"❌ [3/4] 티스토리 예외 (시도 {_attempt}/3): {e}")
                tistory_res = {"status": "error", "message": str(e)}
                _time.sleep(10)
        results["channels"]["tistory"] = tistory_res


        # 4. 🟡 카카오 브런치스토리 자동 발행 (title_kakao)
        try:
            brunch_res = self.brunch_pub.publish_column(
                title=title_kakao,
                subtitle=excerpt,
                body_text=content_md,
                topic_id=topic_id,
                landing_url=landing_url
            )
            results["channels"]["brunch"] = brunch_res
            logger.info(f"✅ [4/4] 🟡 카카오 브런치스토리 처리: '{title_kakao}' -> {brunch_res.get('status')}")
        except Exception as e:
            logger.error(f"❌ [4/4] 🟡 카카오 브런치스토리 실패: {e}")
            results["channels"]["brunch"] = {"status": "error", "message": str(e)}

        # 🔍 [사후 무결성 실사 검증 레고 블록] 실제 공개 블로그 등록 여부 '눈으로 확인'
        try:
            from brands.aura.aura_blog_verifier import AuraBlogVerifier
            verifier = AuraBlogVerifier()
            v_res = verifier.verify_all(expected_title=title_naver, capture=True)
            results["verification"] = v_res

            # 네이버 실사 검증 반영
            if not v_res.get("naver", {}).get("verified"):
                if results["channels"].get("naver_blog", {}).get("status") == "success":
                    results["channels"]["naver_blog"]["status"] = "error"
                    results["channels"]["naver_blog"]["message"] = f"사후 실사 검증 실패 (RSS/블로그 미등록: {v_res.get('naver', {}).get('error', '제목 불일치')})"
            else:
                real_url = v_res["naver"].get("real_url")
                if real_url:
                    results["channels"]["naver_blog"]["url"] = real_url
                    results["channels"]["naver_blog"]["post_url"] = real_url

            # 티스토리 실사 검증 반영
            if not v_res.get("tistory", {}).get("verified"):
                if results["channels"].get("tistory", {}).get("status") in ("success", "active", "restored"):
                    results["channels"]["tistory"]["status"] = "error"
                    results["channels"]["tistory"]["message"] = f"사후 실사 검증 실패 (티스토리 미등록: {v_res.get('tistory', {}).get('error', '제목 불일치')})"
            else:
                real_t_url = v_res["tistory"].get("real_url")
                if real_t_url:
                    results["channels"]["tistory"]["url"] = real_t_url
                    results["channels"]["tistory"]["post_url"] = real_t_url
        except Exception as ve:
            logger.warning(f"⚠️ [Aura] 사후 실사 검증 예외: {ve}")

        # 로컬 발행 리포트 저장
        self._save_publish_report(results, article_pkg)
        logger.info("=" * 60)
        logger.info("🎉 [Aura 4대 채널 옴니 무인 배포 완료!]")
        logger.info("=" * 60 + "\n")

        return results

    def _save_publish_report(self, results: Dict[str, Any], article_pkg: Dict[str, Any]):
        out_dir = PROJECT_ROOT / "outputs" / "aura" / "publish_reports"
        out_dir.mkdir(parents=True, exist_ok=True)
        fname = f"publish_report_topic_{article_pkg.get('topic_id', 1):03d}.json"
        with open(out_dir / fname, "w", encoding="utf-8") as fp:
            json.dump({
                "published_at": str(article_pkg.get("published_at", "")),
                "results": results,
                "article_meta": {
                    "title_naver": article_pkg.get("title_naver"),
                    "title_tistory": article_pkg.get("title_tistory"),
                    "title_kakao": article_pkg.get("title_kakao"),
                    "category": article_pkg.get("category"),
                    "landing_url": article_pkg.get("landing_url"),
                    "image_url": article_pkg.get("image_url")
                }
            }, fp, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    pub = AuraMultiPublisher()
    print("AuraMultiPublisher 준비 완료!")
