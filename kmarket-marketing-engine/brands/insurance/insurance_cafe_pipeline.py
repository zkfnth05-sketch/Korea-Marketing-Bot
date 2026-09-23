# -*- coding: utf-8 -*-
"""
[보험 리밸런스] 5대 정예 맘/가계부/재테크 카페 스텔스 침투 파이프라인 (Master Lego Block)
========================================================================================
- 원칙:
  1. "파이썬으로 구축해. 제미나이는 답글만 쓰게"
  2. "꼭 적합하지 않으면 댓글을 남기지 말아야 하고" (Strict Gatekeeper Latch)
  3. 하루 최대 1건 댓글 (Daily Cap: 1), Zero URL
  4. 공식 문구: "네이버에 국내보험 전수 비교 보험 리밸런스 한번 검색해보세요"
"""

import asyncio
import sys
import random
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from brands.insurance.insurance_cafe_filter import InsuranceCafeFilter
from brands.insurance.insurance_cafe_scanner import InsuranceCafeScanner, INSURANCE_ELITE_CAFES
from brands.insurance.insurance_cafe_reply_writer import InsuranceCafeReplyWriter
from brands.insurance.insurance_cafe_scheduler import InsuranceCafeScheduler, ROTATION_SLOTS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("InsuranceCafePipeline")


class InsuranceCafePipeline:
    """🛡️ 보험 리밸런스 3대 정예 카페 스텔스 침투 오케스트레이터"""

    def __init__(self, profile_dir: Optional[Path] = None):
        if profile_dir:
            self.profile_dir = profile_dir
        else:
            p1 = ROOT / "kmarket-marketing-engine" / "brands" / "insurance" / "naver_browser_profile"
            p2 = ROOT / "brands" / "insurance" / "naver_browser_profile"
            self.profile_dir = p1 if p1.exists() else p2

        self.c_filter = InsuranceCafeFilter()
        self.scanner = InsuranceCafeScanner(filter_instance=self.c_filter)
        self.writer = InsuranceCafeReplyWriter()
        self.scheduler = InsuranceCafeScheduler()

    async def run_daily_stealth_infiltration(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        일일 스텔스 침투 파이프라인 실행
        :param dry_run: True이면 댓글 등록을 실제로 누르지 않고 최종 검증만 수행
        """
        print("\n" + "="*75, flush=True)
        print("🛡️ [보험 리밸런스] 5대 정예 카페 스텔스 침투 파이프라인 가동", flush=True)
        print("="*75, flush=True)

        # 1. 1일 1건 제한(Daily Cap: 1) 검사
        if not self.scheduler.can_post_today(max_daily_posts=1):
            msg = "🛡️ [안전 차단] 오늘 이미 일일 제한(1건) 댓글 침투를 완료했습니다. 네이버 계정 보존을 위해 작업을 마칩니다."
            print(msg, flush=True)
            return {"status": "SKIPPED_DAILY_CAP", "message": msg}

        # 2. 오늘 순번의 로테이션 슬롯 카페 목록 추출
        today_cafes = self.scheduler.get_today_target_cafes(INSURANCE_ELITE_CAFES)
        cafe_names = [c["name"] for c in today_cafes]
        print(f"🎯 오늘의 침투 타겟 슬롯 카페 ({len(today_cafes)}곳): {', '.join(cafe_names)}", flush=True)

        candidate_posts = []

        # 3. 브라우저 구동하여 대상 카페 스캔
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page = await context.new_page()

            for cafe_info in today_cafes:
                name = cafe_info["name"]
                print(f"\n🔍 [{name}] 5일 이내 게시글 스캔 & 파이썬 필터 심사 중...", flush=True)
                posts = await self.scanner.scan_single_cafe(page, cafe_info, max_age_hours=120)
                
                # 이미 댓글 단 글 제외
                fresh_posts = [
                    p for p in posts 
                    if not self.scheduler.is_article_already_replied(p["article_id"])
                ]
                print(f"  ➔ [{name}] 적합 후보: {len(fresh_posts)}건 선별 완료", flush=True)
                candidate_posts.extend(fresh_posts)

            # 4. 🚨 [절대 철칙] "꼭 적합하지 않으면 댓글을 남기지 말아야 하고 (없으면 패스)" (Gatekeeper Latch)
            if not candidate_posts:
                msg = f"🛡️ [게이트키퍼] 오늘 대상 카페({', '.join(cafe_names)})에서 기준(40점 이상)을 통과한 순수 보험 고민글이 0건입니다. '없으면 패스' 철칙에 따라 무음 휴식합니다."
                print("\n" + "="*75, flush=True)
                print(msg, flush=True)
                print("="*75, flush=True)
                self.scheduler.advance_slot()
                await context.close()
                return {"status": "SKIPPED_NO_QUALIFIED_POST", "message": msg}

            # 5. 최적의 1등 글 선별 (적합도 점수 최고점, 최신순)
            candidate_posts.sort(key=lambda x: (x["score"], -x["age_hours"]), reverse=True)
            top_post = candidate_posts[0]

            print("\n" + "🌟"*35, flush=True)
            print("🏆 [오늘의 최우선 침투 타겟 글 선별 완료]", flush=True)
            print(f"- 카페: {top_post['cafe_name']} (Club ID: {top_post['club_id']})", flush=True)
            print(f"- 제목: {top_post['title']}", flush=True)
            print(f"- 작성자: {top_post['writer']} ({top_post['age_str']})", flush=True)
            print(f"- 적합도 점수: {top_post['score']}점 (매칭 키워드: {', '.join(top_post['matched_w'])})", flush=True)
            print(f"- 선별 사유: {top_post['reason']}", flush=True)
            print("🌟"*35 + "\n", flush=True)

            # 6. 제미나이 80% 공감 + 20% 보험 리밸런스 추천 답글 생성 (Zero URL)
            print("✍️ 제미나이 1:1 맞춤형 보험 공감 댓글 작성 요청 중...", flush=True)
            reply_text = self.writer.generate_sympathy_reply(
                title=top_post["title"],
                summary=top_post["summary"],
                cafe_name=top_post["cafe_name"]
            )

            print("\n📝 [생성된 침투 댓글 미리보기]:", flush=True)
            print("-" * 65, flush=True)
            print(reply_text, flush=True)
            print("-" * 65, flush=True)

            # 7. 실행 모드 분기 (Dry-run vs Real Post)
            if dry_run:
                print("\n🧪 [DRY-RUN 모드] 실제 댓글 등록 버튼을 누르지 않고 파이프라인 검증을 성공적으로 마쳤습니다.", flush=True)
                await context.close()
                return {
                    "status": "SUCCESS_DRY_RUN",
                    "target_post": top_post,
                    "reply_text": reply_text
                }

            # 8. 실제 댓글 등록 수행
            print("\n🚀 [실전 모드] 네이버 카페 댓글 등록 시작...", flush=True)
            cafe_slug = top_post.get("url_id") or top_post["club_id"]
            article_url = f"https://cafe.naver.com/{cafe_slug}/{top_post['article_id']}"
            print(f"🌐 타겟 게시글 접속: {article_url}", flush=True)

            async def on_dialog(dialog):
                print(f"📢 [네이버 카페 알림창 감지]: {dialog.message}", flush=True)
                await dialog.accept()
            page.on("dialog", on_dialog)

            await page.goto(article_url, wait_until="networkidle")
            await asyncio.sleep(2)

            frame = page.frame(name="cafe_main")
            if not frame:
                print("❌ cafe_main iframe을 찾지 못했습니다.", flush=True)
                await context.close()
                return {"status": "ERROR_FRAME_NOT_FOUND"}

            comment_box = frame.locator("textarea.comment_inbox_text")
            if await comment_box.count() == 0:
                print("❌ 댓글 입력창을 찾지 못했습니다 (권한 부족 또는 등업 필요).", flush=True)
                await context.close()
                return {"status": "ERROR_COMMENT_BOX_NOT_FOUND"}

            await comment_box.click()
            await asyncio.sleep(1)
            await comment_box.fill(reply_text)
            await asyncio.sleep(random.uniform(1.5, 2.5))

            register_btn = frame.locator(".btn_register")
            await register_btn.click()
            await asyncio.sleep(4)

            proof_dir = ROOT / "scratch"
            proof_dir.mkdir(parents=True, exist_ok=True)
            proof_path = proof_dir / f"live_comment_proof_insure_{top_post['article_id']}.png"
            await page.screenshot(path=str(proof_path), full_page=False)
            print(f"📸 등록 증빙 스크린샷 저장 완료: {proof_path}", flush=True)

            try:
                artifact_path = Path("C:/Users/zkfnt/.gemini/antigravity-ide/brain/b8daaffd-1714-4ee8-b3e2-69cbbff3e6cb") / f"live_comment_proof_insure_{top_post['article_id']}.png"
                with open(proof_path, "rb") as s_f, open(artifact_path, "wb") as d_f:
                    d_f.write(s_f.read())
            except Exception:
                pass

            self.scheduler.record_post_success(
                cafe_name=top_post["cafe_name"],
                article_id=top_post["article_id"],
                title=top_post["title"],
                reply_text=reply_text
            )
            print(f"🎉 [{top_post['cafe_name']}] 댓글 침투 등록 완료 및 히스토리 기록 완료!", flush=True)

            await context.close()
            return {
                "status": "SUCCESS_POSTED",
                "target_post": top_post,
                "reply_text": reply_text,
                "proof_screenshot": str(proof_path),
                "article_url": article_url
            }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Insurance Cafe Infiltration Pipeline")
    parser.add_argument("--live", action="store_true", help="실제 라이브 댓글 등록 실행")
    args = parser.parse_args()

    pipeline = InsuranceCafePipeline()
    asyncio.run(pipeline.run_daily_stealth_infiltration(dry_run=not args.live))
