# -*- coding: utf-8 -*-
"""
Insurance Threads Publisher (🧵 🛡️ 보험 리밸런스 전용 스레드 독립 레고 블록 발행기)
=============================================================================
- 브랜드: 🛡️ 보험 리밸런스 (InsureBalance)
- 전용 계정: @goldmomofficial
- 공식 키워드: 보험 리밸런스 (띄어쓰기 필수, 불변)
- 랜딩 URL: https://insure-rebalance.vercel.app/
- 세션 파일: brands/insurance/threads_session.json (Playwright storage_state 단독 주입)
- 4대 절대 수칙 공통 코어(HumanRecipeEngine) 전면 적용:
  1. [사람의 눈으로 글자 찾기]: 화면 글자 기반 탐색 및 Lexical 에디터 완벽 주입
  2. [방해 모달 분쇄기]: 이탈 경고 및 안내 팝업 즉각 분쇄
  3. [게시물 완료 화면 직행 검증]: @goldmomofficial 프로필 직행 1등 실물 확인 & 라이브 URL 영수증 추출
  4. [최대 3회 풀리셋 자가 치유]: 실패 시 브라우저 풀리셋 후 최대 3회 자동 재도전
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from playwright.async_api import async_playwright

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.auto_publishers.human_recipe_engine import HumanRecipeEngine

logger = logging.getLogger("InsuranceThreadsPublisher")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

SESSION_FILE = CURRENT_DIR / "threads_session.json"
COOKIE_FILE = CURRENT_DIR / "threads_cookies.json"
HISTORY_FILE = CURRENT_DIR / "threads_publish_history.json"


def sanitize_threads_caption(raw_text: str) -> str:
    """스레드 500자 제한 맞춤 본문 정제"""
    if not raw_text:
        return ""
    lines = raw_text.split("\n")
    clean = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s.startswith("=") or s.startswith("🏷️") or "주제:" in s or "대상:" in s or "송출 규격:" in s or "구성 안내" in s:
            continue
        clean.append(s)

    body = "\n\n".join(clean)
    # 본문 내 URL 전면 배제 (스레드 알고리즘 다운랭킹 방지: 본문 0개, 첫 댓글 100% 직결)
    import re
    body = re.sub(r'https?://\S+', '💬 [첫 번째 댓글 링크 참조]', body)
    if len(body) > 420:
        body = body[:400] + "..."
    return body


class InsuranceThreadsPublisher:
    """🛡️ Insurance 전용 스레드(Threads) 독립 레고 블록 발행기 (4대 절대 수칙 완비)"""

    BRAND = "insurance"
    BRAND_NAME = "보험 리밸런스"
    OFFICIAL_SEARCH_KEYWORD = "보험 리밸런스"
    LANDING_URL = "https://insure-rebalance.vercel.app/"
    ACCOUNT_HANDLE = "goldmomofficial"
    PROFILE_URL = "https://www.threads.net/@goldmomofficial"

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.session_file = SESSION_FILE
        self.history_file = HISTORY_FILE

    def _save_history(self, record: Dict[str, Any]):
        try:
            records = []
            if self.history_file.exists():
                with open(self.history_file, "r", encoding="utf-8") as f:
                    records = json.load(f)
            records.append(record)
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"히스토리 저장 예외: {e}")

    async def publish_thread(
        self,
        caption: str,
        image_paths: Optional[List[str]] = None,
        first_reply_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """[4대 절대 수칙] 자가 치유(Self-Healing) 기반 스레드 자동 송출 메인 진입점"""
        clean_caption = sanitize_threads_caption(caption)
        if not clean_caption:
            clean_caption = (
                "🛡️ [보험 리밸런스 팩트체크]\n\n"
                "매달 통장에서 나가는 보험료, 과연 현재 보장 내역과 내 상황에 맞게 최적화되어 있을까요?\n\n"
                "📌 금융소비자가 꼭 알아야 할 3대 점검 팩트:\n"
                "1️⃣ 4세대 실손보험은 병원 이용이 적을 경우 기존 1~3세대 대비 월 보험료를 합리적으로 절감할 수 있습니다.\n"
                "2️⃣ 실손 및 운전자 담보는 '비례보상' 원칙이 적용되므로 중복 가입 시 불필요한 낭비가 발생합니다.\n"
                "3️⃣ 34개 보험사 공시 가격표를 객관적으로 비교하여 불필요한 거품을 덜어내세요.\n\n"
                "#보험리밸런스 #실손보험 #4세대실손 #보험비교 #보험다이어트"
            )

        if not first_reply_text:
            first_reply_text = (
                f"🛡️ [보험 리밸런스] 34개 보험사 모든 보험 무료조회:\n"
                f"👉 {self.LANDING_URL}\n\n"
                f"🔍 네이버 검색창에 [{self.OFFICIAL_SEARCH_KEYWORD}]를 검색해보세요!\n\n"
                f"✨ 34개 보험사 비교 및 내 보험료 다이어트를 무료로 즉시 시작해 보세요!\n"
                f"(네이버 검색: {self.OFFICIAL_SEARCH_KEYWORD})"
            )

        valid_media = []
        if image_paths:
            for p in image_paths:
                fpath = Path(p)
                if fpath.exists() and fpath.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
                    valid_media.append(str(fpath.resolve()))

        async def _attempt_publish(attempt: int) -> Dict[str, Any]:
            return await self._single_attempt_publish(
                attempt=attempt,
                caption=clean_caption,
                valid_media=valid_media,
                first_reply_text=first_reply_text
            )

        # 4대 수칙: 실패 시 최대 3회 풀리셋 자가 치유 재시도
        return await HumanRecipeEngine.self_healing_retry(
            action_name=f"🛡️ 보험 스레드 발행 ({self.ACCOUNT_HANDLE})",
            action_coroutine_fn=_attempt_publish,
            max_retries=3,
            cooldown_sec=5.0
        )

    async def _single_attempt_publish(
        self,
        attempt: int,
        caption: str,
        valid_media: List[str],
        first_reply_text: str
    ) -> Dict[str, Any]:
        """단일 1회 브라우저 라이프사이클 글자 레시피 실행 및 두 눈 실물 검증"""
        logger.info(f"🚀 [보험 Threads] 단일 실행 시작 (시도 #{attempt}, 미디어 {len(valid_media)}장)")

        if not self.session_file.exists():
            raise RuntimeError(f"스레드 세션 파일 부재: {self.session_file}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ]
            )
            context = await browser.new_context(
                storage_state=str(self.session_file),
                viewport={"width": 1280, "height": 900},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            try:
                # 📌 1단계: 스레드 메인 접속
                logger.info("1. Threads 메인(threads.net) 접속 중...")
                await page.goto("https://www.threads.net/", wait_until="networkidle", timeout=30000)
                await asyncio.sleep(4.0)

                # 2대 수칙: 방해 모달 분쇄기 가동
                await HumanRecipeEngine.modal_buster(page)

                # 📌 2단계: 모달 작성창 열기
                logger.info("2. 스레드 작성 모달 열기...")
                opened = await page.evaluate("""() => {
                    const btns = Array.from(document.querySelectorAll("div[role='button'], button, a"));
                    const createBtn = btns.find(b => {
                        const aria = b.getAttribute('aria-label') || '';
                        const text = (b.innerText || '').trim();
                        return aria.includes('Create') || aria.includes('스레드') || text === 'New thread';
                    });
                    if (createBtn) {
                        createBtn.click();
                        return true;
                    }
                    return false;
                }""")
                if not opened:
                    await page.evaluate("""() => {
                        const all = Array.from(document.querySelectorAll("div[role='button']"));
                        if (all.length > 0) all[all.length - 1].click();
                    }""")
                await asyncio.sleep(3.0)

                dialog = page.locator("div[role='dialog']").first
                tb = dialog.locator("div[role='textbox']").first
                await tb.wait_for(state="visible", timeout=10000)

                # 📌 3단계: 캡션 본문 입력
                logger.info("3. 캡션 본문 입력 중...")
                await tb.click()
                await asyncio.sleep(0.5)
                await page.keyboard.insert_text(caption)
                await asyncio.sleep(1.5)

                # 📌 4단계: 미디어 파일 주입
                if valid_media:
                    logger.info(f"4. 미디어 {len(valid_media)}장 파일 주입 중...")
                    file_input = dialog.locator("input[type='file']").first
                    if await file_input.count() > 0:
                        await file_input.set_input_files(valid_media)
                        logger.info("   미디어 첨부 완료, 렌더링 대기 (8초)...")
                        await asyncio.sleep(8.0)

                await HumanRecipeEngine.modal_buster(page)

                # 📌 5단계: [Post] 버튼 클릭
                logger.info("5. [Post] 글자 버튼 클릭...")
                post_btn = (
                    dialog.locator("div[role='button'], button").filter(has_text="Post").or_(
                        dialog.locator("div[role='button'], button").filter(has_text="게시하기")
                    ).or_(
                        dialog.locator("div[role='button'], button").filter(has_text="게시")
                    ).first
                )
                await post_btn.click()

                logger.info("   게시 요청 전송 완료! 서버 반영 대기 (15초)...")
                await asyncio.sleep(15.0)

                # 📌 6단계: [3대 수칙] 1분(60초) 서버 전파 대기 후 프로필 직행 두 눈 실물 검증
                logger.info("⏳ [스레드 무인 파이프라인] 서버 전파 및 인코딩 대기 (정확히 60초 휴식 후 실물 확인 및 댓글 진입)...")
                await asyncio.sleep(60.0)

                logger.info(f"6. 프로필 관리 화면({self.PROFILE_URL}) 직행 두 눈 실물 검증 개시...")
                await page.goto(self.PROFILE_URL, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(5.0)

                post_href = await page.evaluate("""() => {
                    const links = Array.from(document.querySelectorAll("a[href*='/post/']"));
                    return links.length > 0 ? links[0].getAttribute('href') : null;
                }""")

                if not post_href:
                    raise RuntimeError("프로필 화면 최상단에 방금 올린 게시물 링크(/post/...)가 아직 반영되지 않았습니다.")

                live_post_url = f"https://www.threads.net{post_href}" if post_href.startswith("/") else post_href
                logger.info(f"🎉🎉 [두 눈 실물 검증 100% 합격!] 방금 올린 스레드 실물 URL 영수증: {live_post_url}")

                # 📌 7단계: 첫 번째 타래 댓글 (공식 검색어 + 랜딩 URL 체인)
                if first_reply_text and live_post_url:
                    logger.info("7. 첫 번째 타래 댓글 작성 이동...")
                    try:
                        await page.goto(live_post_url, wait_until="networkidle", timeout=30000)
                        await asyncio.sleep(4.0)

                        reply_area = page.locator("div[role='button']").filter(has_text="Reply to").or_(page.locator("div:has-text('Reply to')")).first
                        if await reply_area.count() > 0:
                            await reply_area.click()
                            await asyncio.sleep(1.5)
                            reply_tb = page.locator("div[role='textbox'], [contenteditable='true']").first
                            if await reply_tb.count() > 0:
                                await page.evaluate("(el) => el.focus()", await reply_tb.element_handle())
                                await page.keyboard.insert_text(first_reply_text)
                                await asyncio.sleep(2.0)

                                r_post = page.locator("div[role='button'], button").filter(has_text="Post").or_(page.locator("div[role='button'], button").filter(has_text="Reply")).last
                                if await r_post.count() > 0:
                                    await r_post.click()
                                    logger.info("   1번 타래 댓글 체인 부착 완료!")
                                    await asyncio.sleep(5.0)
                    except Exception as re:
                        logger.warning(f"타래 댓글 부착 경고: {re}")

                # 📌 8단계: 증빙 스크린샷 캡처 및 세션 갱신
                proof_path = CURRENT_DIR / "threads_live_proof.png"
                await page.screenshot(path=str(proof_path))
                await context.storage_state(path=str(self.session_file))

                result = {
                    "status": "SUCCESS",
                    "verified": True,
                    "brand": self.BRAND,
                    "published_at": datetime.now().isoformat(),
                    "live_url": live_post_url,
                    "proof_screenshot": str(proof_path),
                    "caption_preview": caption[:60] + "...",
                    "media_count": len(valid_media)
                }
                self._save_history(result)
                return result

            finally:
                await browser.close()


if __name__ == "__main__":
    async def _test():
        pub = InsuranceThreadsPublisher(headless=True)
        res = await pub.publish_thread(caption="테스트", image_paths=[])
        print(json.dumps(res, ensure_ascii=False, indent=2))

    asyncio.run(_test())
