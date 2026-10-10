# -*- coding: utf-8 -*-
"""
[StockMaster AI] 5대 정예 주식 카페 스텔스 침투 파이프라인 (Master Lego Block)
============================================================================
- 원칙:
  1. "파이썬으로 구축해. 제미나이는 답글만 쓰게"
  2. "꼭 적합하지 않으면 댓글을 남기지 말아야 하고" (Strict Gatekeeper Latch)
  3. 하루 최대 1건 댓글 (Daily Cap: 1), Zero URL
  4. 공식 문구: "네이버에 10분마다 국내 우량주 분석 스톡마스터 AI 한번 검색해보세요"
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

from brands.stock.stock_cafe_filter import StockCafeFilter
from brands.stock.stock_cafe_scanner import StockCafeScanner, STOCK_ELITE_CAFES
from brands.stock.stock_cafe_reply_writer import StockCafeReplyWriter
from brands.stock.stock_cafe_scheduler import StockCafeScheduler, ROTATION_SLOTS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("StockCafePipeline")


class StockCafePipeline:
    """📈 StockMaster AI 5대 주식 카페 스텔스 침투 오케스트레이터"""

    def __init__(self, profile_dir: Optional[Path] = None):
        self.profile_dir = profile_dir or (ROOT / "brands" / "stock" / "naver_browser_profile")
        self.c_filter = StockCafeFilter()
        self.scanner = StockCafeScanner(filter_instance=self.c_filter)
        self.writer = StockCafeReplyWriter()
        self.scheduler = StockCafeScheduler()

    async def run_daily_stealth_infiltration(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        일일 스텔스 침투 파이프라인 실행
        :param dry_run: True이면 댓글 등록을 실제로 누르지 않고 최종 검증만 수행
        """
        print("\n" + "="*75, flush=True)
        print("📈 [StockMaster AI] 5대 정예 주식 카페 스텔스 침투 파이프라인 가동", flush=True)
        print("="*75, flush=True)

        # 1. 1일 1건 제한(Daily Cap: 1) 검사
        if not self.scheduler.can_post_today(max_daily_posts=1):
            msg = "🛡️ [안전 차단] 오늘 이미 일일 제한(1건) 댓글 침투를 완료했습니다. 네이버 계정 보존을 위해 작업을 마칩니다."
            print(msg, flush=True)
            return {"status": "SKIPPED_DAILY_CAP", "message": msg}

        # 2. 오늘 순번의 로테이션 슬롯 카페 목록 추출
        today_cafes = self.scheduler.get_today_target_cafes(STOCK_ELITE_CAFES)
        cafe_names = [c["name"] for c in today_cafes]
        print(f"🎯 오늘의 침투 타겟 슬롯 카페 ({len(today_cafes)}곳): {', '.join(cafe_names)}", flush=True)

        candidate_posts = []

        # 3. 브라우저 구동하여 대상 카페 스캔
        session_file = ROOT / "brands" / "stock" / "naver_session.json"
        fallback_session = ROOT / "brands" / "aura" / "naver_session.json"
        target_sess = session_file if session_file.exists() else fallback_session
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            if target_sess.exists():
                try:
                    import json
                    with open(target_sess, "r", encoding="utf-8") as sf:
                        s_data = json.load(sf)
                        cookies = s_data.get("cookies", [])
                        if cookies:
                            await context.add_cookies(cookies)
                            logger.info(f"🍪 [Stock Cafe] 네이버 세션 쿠키 {len(cookies)}개 주입 완료")
                except Exception as ce:
                    logger.warning(f"쿠키 주입 통과: {ce}")

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
            # 4. 🚨 [절대 철칙] "꼭 적합하지 않으면 댓글을 남기지 말아야 하고 (없으면 패스)" (Gatekeeper Latch)
            if not candidate_posts:
                msg = f"🛡️ [게이트키퍼] 오늘 대상 카페({', '.join(cafe_names)})에서 기준(35점 이상)을 통과한 순수 주식 고민글이 0건입니다. '없으면 패스' 철칙에 따라 무음 휴식합니다."
                print("\n" + "="*75, flush=True)
                print(msg, flush=True)
                print("="*75, flush=True)
                self.scheduler.advance_slot()
                await context.close()
                return {"status": "SKIPPED_NO_QUALIFIED_POST", "message": msg}

            # 5. 최적의 후보 글 순차 검증 및 댓글 침투 (Auto-Fallback)
            candidate_posts.sort(key=lambda x: (x["score"], -x["age_hours"]), reverse=True)
            
            posted_result = None
            for rank, target_post in enumerate(candidate_posts, 1):
                cafe_slug = target_post.get("url_id") or target_post["club_id"]
                article_url = f"https://cafe.naver.com/{cafe_slug}/{target_post['article_id']}"
                
                print("\n" + "🌟"*35, flush=True)
                print(f"🏆 [{rank}/{len(candidate_posts)}순위 주식 타겟 글 검증 진입]", flush=True)
                print(f"- 카페: {target_post['cafe_name']} (Club ID: {target_post['club_id']})", flush=True)
                print(f"- 제목: {target_post['title']}", flush=True)
                print(f"- 작성자: {target_post['writer']} ({target_post['age_str']})", flush=True)
                print(f"- 적합도 점수: {target_post['score']}점 (매칭 키워드: {', '.join(target_post['matched_w'])})", flush=True)
                print(f"- 접속 URL: {article_url}", flush=True)
                print("🌟"*35 + "\n", flush=True)

                try:
                    await page.goto(article_url, wait_until="domcontentloaded", timeout=20000)
                    await asyncio.sleep(2.5)
                except Exception as ge:
                    print(f"⚠️ 게시글 접속 타임아웃 ({ge}) ➔ 다음 순위 후보로 이동", flush=True)
                    continue

                frame = page.frame(name="cafe_main")
                if not frame:
                    print("⚠️ cafe_main iframe 미발견 ➔ 다음 순위 후보로 이동", flush=True)
                    continue

                # 댓글 영역 로딩을 위한 스크롤
                await frame.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1.5)

                # 1) 진짜 네이버 로그인 세션 만료 여부 확인 (로그아웃 링크 또는 유저 이름 엘리먼트 존재 여부)
                is_logged_in = (await page.locator("a:has-text('로그아웃'), #gnb_name2, .gnb_my_name, .gnb_my_interface").count() > 0)
                if not is_logged_in:
                    has_cookie = any(c.get("name") == "NID_AUT" for c in (cookies if 'cookies' in locals() else []))
                    if not has_cookie:
                        print("❌ [네이버 세션 만료 감지] 네이버 로그인이 풀려있습니다. 세션 갱신이 필요합니다.", flush=True)
                        await context.close()
                        return {"status": "ERROR_SESSION_EXPIRED", "message": "네이버 로그인 세션 만료"}

                # 2) 게시판 등업/댓글 작성 권한 여부 정밀 확인
                no_perm_text = await frame.locator("text='댓글 쓰기 권한이 없습니다', text='등업이 필요합니다', text='작성 권한이 없습니다'").count()
                comment_box = frame.locator("textarea.comment_inbox_text, .CommentWriter textarea, .comment_inbox textarea")
                box_count = await comment_box.count()

                if no_perm_text > 0 or box_count == 0:
                    print(f"⚠️ [게시판 등업 제한 감지] '{target_post['title']}' 글은 현재 회원 등급에서 댓글 작성이 불가합니다.", flush=True)
                    print(f"   ➔ 다음 {rank + 1}순위 적합 후보 글로 자동 전환(Auto-Fallback)합니다...", flush=True)
                    continue

                # 3) 댓글 작성 가능 확인 완료
                print(f"✅ [댓글 작성 권한 확인 완료] '{target_post['title']}'에 1:1 맞춤 침투를 진행합니다!", flush=True)

                # 6. 제미나이 80% 공감 + 20% 스톡마스터 AI 추천 답글 생성 (Zero URL)
                print("✍️ 제미나이 1:1 맞춤형 주식 공감 댓글 작성 요청 중...", flush=True)
                reply_text = self.writer.generate_sympathy_reply(
                    title=target_post["title"],
                    summary=target_post["summary"],
                    cafe_name=target_post["cafe_name"]
                )

                print("\n📝 [생성된 침투 댓글 미리보기]:", flush=True)
                print("-" * 65, flush=True)
                print(reply_text, flush=True)
                print("-" * 65, flush=True)

                # 7. 실행 모드 분기 (Dry-run vs Real Post)
                if dry_run:
                    print("\n🧪 [DRY-RUN 모드] 댓글 작성 가능 및 대본 무결성 검증 완료 (실제 등록 미클릭).", flush=True)
                    await context.close()
                    return {
                        "status": "SUCCESS_DRY_RUN",
                        "target_post": target_post,
                        "reply_text": reply_text
                    }

                # 8. 실제 댓글 등록 수행
                print("\n🚀 [실전 모드] 네이버 카페 댓글 등록 시작...", flush=True)
                target_box = comment_box.first
                await target_box.click()
                await asyncio.sleep(1)
                await target_box.fill(reply_text)
                await asyncio.sleep(random.uniform(1.5, 2.5))

                register_btn = frame.locator(".btn_register, button.btn_register, a.btn_register, .register_box .button")
                if await register_btn.count() > 0:
                    await register_btn.first.click()
                else:
                    await target_box.press("Enter")
                await asyncio.sleep(4)

                proof_dir = ROOT / "scratch"
                proof_dir.mkdir(parents=True, exist_ok=True)
                proof_path = proof_dir / f"live_comment_proof_stock_{target_post['article_id']}.png"
                await page.screenshot(path=str(proof_path), full_page=False)
                print(f"📸 등록 증빙 스크린샷 저장 완료: {proof_path}", flush=True)

                self.scheduler.record_post_success(
                    cafe_name=target_post["cafe_name"],
                    article_id=target_post["article_id"],
                    title=target_post["title"],
                    reply_text=reply_text
                )
                print(f"🎉 [{target_post['cafe_name']}] 댓글 침투 등록 완료 및 히스토리 기록 완료!", flush=True)

                posted_result = {
                    "status": "SUCCESS_POSTED",
                    "target_post": target_post,
                    "reply_text": reply_text,
                    "proof_screenshot": str(proof_path),
                    "article_url": article_url
                }
                break

            await context.close()
            if not posted_result:
                msg = "🛡️ [게이트키퍼] 오늘 스캔된 후보 글들이 모두 등업 제한 게시판이거나 작성 불가 상태였습니다. 억지 작성을 배제하고 다음 슬롯으로 전진합니다."
                print("\n" + "="*75, flush=True)
                print(msg, flush=True)
                print("="*75, flush=True)
                self.scheduler.advance_slot()
                return {"status": "SKIPPED_ALL_RESTRICTED", "message": msg}

            return posted_result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="StockMaster AI Cafe Infiltration Pipeline")
    parser.add_argument("--live", action="store_true", help="실제 라이브 댓글 등록 실행")
    args = parser.parse_args()

    pipeline = StockCafePipeline()
    asyncio.run(pipeline.run_daily_stealth_infiltration(dry_run=not args.live))
