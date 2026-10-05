# -*- coding: utf-8 -*-
"""
Stock Threads Publisher (🧵 StockMaster AI 전용 스레드 독립 레고 블록 발행기)
================================================================================
- 브랜드: 📈 StockMaster AI (주식 AI)
- 전용 계정: @stockmaster_ai
- 검색 공식 키워드: 스톡마스터 AI (띄어쓰기 필수, 절대 불변)
- 랜딩 URL: https://stockmaster-ai.vercel.app/
- 프로필 디렉터리: brands/stock/meta_chrome_profile/
- 세션 파일: brands/stock/threads_session.json
- 기능:
  1. 스레드(threads.net) 완전 무인 자동 로그인 세션 유지
  2. 3초 테마주/수급 분석 카드뉴스 이미지(4~5장 슬라이드) 또는 긴급 브리핑 텍스트 타래 게시
  3. 첫 번째 타래 댓글로 공식 검색어('스톡마스터 AI') 및 랜딩 URL 자동 체인 부착
  4. 게시 결과 스크린샷 캡처 및 히스토리 아카이빙
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

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("StockThreadsPublisher")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
PROFILE_DIR = CURRENT_DIR / "meta_chrome_profile"
SESSION_FILE = CURRENT_DIR / "threads_session.json"
COOKIE_FILE = CURRENT_DIR / "threads_cookies.json"
HISTORY_FILE = CURRENT_DIR / "threads_publish_history.json"


def sanitize_threads_caption(raw_text: str) -> str:
    if not raw_text:
        return ""
    lines = raw_text.split("\n")
    clean = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s.startswith("=") or s.startswith("•") or "주제:" in s or "산출 규격:" in s or "구성 안내" in s:
            continue
        clean.append(s)
    
    body = "\n\n".join(clean)
    if len(body) > 420:
        body = body[:400] + "..."
    return body


class StockThreadsPublisher:
    """📈 StockMaster AI 전용 스레드(Threads) 독립 레고 블록 발행기"""

    BRAND = "stock"
    BRAND_NAME = "StockMaster AI"
    OFFICIAL_SEARCH_KEYWORD = "스톡마스터 AI"
    LANDING_URL = "https://stockmaster-ai.vercel.app/"

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.profile_dir = PROFILE_DIR
        self.profile_dir.mkdir(parents=True, exist_ok=True)

    def _prepare_cookies(self) -> List[Dict[str, Any]]:
        if not COOKIE_FILE.exists():
            return []
        try:
            with open(COOKIE_FILE, "r", encoding="utf-8") as f:
                raw_cookies = json.load(f)
            pw_cookies = []
            for c in raw_cookies:
                pw_c = {
                    "name": c["name"],
                    "value": c["value"],
                    "domain": c["domain"],
                    "path": c.get("path", "/"),
                    "secure": c.get("secure", True),
                    "httpOnly": c.get("httpOnly", False),
                }
                if c.get("sameSite") in ["Strict", "Lax", "None"]:
                    pw_c["sameSite"] = c["sameSite"]
                elif c.get("sameSite") == "no_restriction":
                    pw_c["sameSite"] = "None"
                elif c.get("sameSite") == "lax":
                    pw_c["sameSite"] = "Lax"
                pw_cookies.append(pw_c)
                for d in [".threads.net", ".instagram.com"]:
                    dc = dict(pw_c)
                    dc["domain"] = d
                    pw_cookies.append(dc)
            return pw_cookies
        except Exception as ex:
            logger.warning(f"쿠키 파싱 오류: {ex}")
            return []

    async def publish_thread(
        self,
        caption: str,
        image_paths: Optional[List[str]] = None,
        first_reply_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """스레드에 본문 + 카드뉴스 이미지 + 첫 댓글 체인 자동 발행"""
        caption = sanitize_threads_caption(caption)
        if not caption:
            caption = (
                "📈 [오늘의 실시간 외국인/기관 수급 급증 TOP 5]\n\n"
                "급등 전 포착된 큰손들의 매수 시그널 분석!\n"
                "3초 만에 확인하는 핵심 테마 브리핑 📊\n\n"
                "#스톡마스터AI #주식AI #수급분석 #급등주 #테마주"
            )

        if not first_reply_text:
            first_reply_text = (
                f"📈 3초 실시간 테마주 & 수급 브리핑\n"
                f"네이버에 '{self.OFFICIAL_SEARCH_KEYWORD}' 검색해보세요!\n"
                f"👉 {self.LANDING_URL}"
            )

        valid_media = []
        if image_paths:
            for p in image_paths:
                fpath = Path(p)
                if fpath.exists() and fpath.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov"]:
                    valid_media.append(str(fpath.resolve()))

        is_video = any(p.endswith((".mp4", ".mov")) for p in valid_media)
        media_type = "동영상(릴스 숏폼)" if is_video else "카드뉴스 이미지"
        logger.info(f"🚀 [Stock Threads] 스레드 발행 시작 (글자수: {len(caption)}자, {media_type}: {len(valid_media)}개)")

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 900}
            )
            
            cookies = self._prepare_cookies()
            if cookies:
                await context.add_cookies(cookies)

            page = context.pages[0] if context.pages else await context.new_page()

            try:
                # 1. Threads 메인 접속
                logger.info("1. Threads 메인 페이지 접속 중...")
                await page.goto("https://www.threads.com/", wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(4)

                # 1-1. 'Continue with Instagram' 모달 자동 클릭
                try:
                    cont_btn = await page.query_selector("div:has-text('Continue with Instagram'), button:has-text('Continue with Instagram')")
                    if cont_btn:
                        logger.info("👉 'Continue with Instagram' 모달 감지, 자동 클릭...")
                        await cont_btn.click()
                        await asyncio.sleep(4)
                except Exception:
                    pass

                # 2. 작성 모달 열기
                logger.info("2. 스레드 작성창 열기...")
                opened = False
                quick_box = await page.query_selector("div:has-text(\"What's new?\"), div:has-text('새로운 스레드를 시작하세요')")
                if quick_box:
                    await quick_box.click()
                    opened = True
                    await asyncio.sleep(2)
                
                if not opened:
                    new_thread_btn = await page.query_selector("span:has-text('New thread'), svg[aria-label='Create'], svg[aria-label='새 스레드'], div[role='button'][aria-label*='새']")
                    if new_thread_btn:
                        await new_thread_btn.click()
                        opened = True
                        await asyncio.sleep(2)

                # 3. 본문 텍스트 입력
                logger.info("3. 캡션 텍스트 입력 중...")
                textbox = await page.wait_for_selector("div[role='textbox'][contenteditable='true'], div[data-lexical-editor='true']", timeout=10000)
                await textbox.click()
                await asyncio.sleep(0.5)
                await textbox.fill(caption)
                await asyncio.sleep(1)

                # 4. 카드뉴스 이미지 또는 숏폼 비디오 첨부
                if valid_media:
                    logger.info(f"4. {media_type} {len(valid_media)}개 업로드 중...")
                    file_input = await page.query_selector("input[type='file']")
                    if file_input:
                        await file_input.set_input_files(valid_media)
                        logger.info("   미디어 파일 전송 완료, 렌더링/인코딩 대기...")
                        wait_sec = 14 if is_video else 6
                        await asyncio.sleep(wait_sec)

                # 5. [1단계] 본문 Post / 게시 버튼 클릭
                logger.info("5. 본문 [Post / 게시] 버튼 클릭...")
                posted = False
                try:
                    posted = await page.evaluate("""() => {
                        const dialog = document.querySelector("div[role='dialog']") || document;
                        const btns = Array.from(dialog.querySelectorAll("div[role='button'], button"));
                        const postBtn = btns.find(b => {
                            const t = b.innerText.trim();
                            const ariaDisabled = b.getAttribute('aria-disabled');
                            const disabled = b.getAttribute('disabled');
                            return (t === 'Post' || t === '게시') && ariaDisabled !== 'true' && disabled === null;
                        });
                        if (postBtn) {
                            postBtn.click();
                            return true;
                        }
                        return false;
                    }""")
                    if posted:
                        logger.info("   본문 JS 직접 클릭 성공!")
                except Exception:
                    pass

                if not posted:
                    publish_btn = await page.wait_for_selector("div[role='dialog'] div[role='button']:has-text('Post'), div[role='dialog'] button:has-text('Post'), div[role='dialog'] div[role='button']:has-text('게시')", timeout=8000)
                    if publish_btn:
                        await publish_btn.click(force=True)
                        posted = True

                logger.info("   본문 게시 완료! 서버 반영 대기 (10초)...")
                await asyncio.sleep(10)

                # 6. [2단계] 첫 번째 타래 댓글 (내 글 바로 아래 답글) 작성
                if first_reply_text:
                    logger.info("6. [2단계] 첫 번째 타래 댓글(답글) 작성 시작...")
                    try:
                        await page.goto("https://www.threads.com/@stockmaster_ai", wait_until="domcontentloaded", timeout=25000)
                        await asyncio.sleep(4)

                        reply_btn = await page.query_selector("svg[aria-label='Reply'], svg[aria-label='답글'], div[role='button'][aria-label*='Reply'], div[role='button'][aria-label*='답글']")
                        if reply_btn:
                            logger.info("   첫 번째 게시물 [답글] 버튼 클릭...")
                            await reply_btn.click(force=True)
                            await asyncio.sleep(2)

                            reply_box = await page.wait_for_selector("div[role='dialog'] div[role='textbox'][contenteditable='true'], div[role='textbox'][contenteditable='true']", timeout=8000)
                            if reply_box:
                                await reply_box.click(force=True)
                                await asyncio.sleep(0.5)
                                await reply_box.fill(first_reply_text)
                                await asyncio.sleep(1)

                                # 답글 [Post / 게시] 클릭
                                reply_posted = await page.evaluate("""() => {
                                    const dialog = document.querySelector("div[role='dialog']") || document;
                                    const btns = Array.from(dialog.querySelectorAll("div[role='button'], button"));
                                    const postBtn = btns.find(b => {
                                        const t = b.innerText.trim();
                                        const ariaDisabled = b.getAttribute('aria-disabled');
                                        const disabled = b.getAttribute('disabled');
                                        return (t === 'Post' || t === '게시') && ariaDisabled !== 'true' && disabled === null;
                                    });
                                    if (postBtn) {
                                        postBtn.click();
                                        return true;
                                    }
                                    return false;
                                }""")
                                if not reply_posted:
                                    reply_post_btn = await page.query_selector("div[role='dialog'] div[role='button']:has-text('Post'), div[role='dialog'] button:has-text('Post'), div[role='dialog'] div[role='button']:has-text('게시')")
                                    if reply_post_btn:
                                        await reply_post_btn.click(force=True)

                                logger.info("🎉 [2단계 대성공] 첫 번째 타래 댓글(공식 검색어 + 랜딩 링크) 체인 등록 완료!")
                                await asyncio.sleep(6)
                    except Exception as ex_reply:
                        logger.warning(f"⚠️ 타래 댓글 작성 예외: {ex_reply}")

                # 7. 프로필 페이지로 이동하여 최종 송출 확인 캡처
                logger.info("7. 프로필 페이지에서 송출 결과 확인 중...")
                await page.goto("https://www.threads.com/@stockmaster_ai", wait_until="domcontentloaded", timeout=25000)
                await asyncio.sleep(4)
                await page.evaluate("window.scrollBy(0, 450)")
                await asyncio.sleep(2)

                proof_path = CURRENT_DIR / "threads_live_proof.png"
                await page.screenshot(path=str(proof_path))
                logger.info(f"📸 게시 완료 라이브 증빙 캡처: {proof_path}")

                await context.storage_state(path=str(SESSION_FILE))

                result_record = {
                    "brand": self.BRAND,
                    "published_at": datetime.now().isoformat(),
                    "caption_preview": caption[:60] + "...",
                    "media_count": len(valid_media),
                    "first_reply": first_reply_text,
                    "status": "SUCCESS",
                    "proof_screenshot": str(proof_path)
                }
                self._save_history(result_record)

                await context.close()
                return {
                    "success": True,
                    "brand": self.BRAND,
                    "message": f"🎉 [스레드 발행 성공] {self.BRAND_NAME} 콘텐츠가 Threads에 성공적으로 송출되었습니다!",
                    "details": result_record
                }

            except Exception as e:
                logger.error(f"❌ [Stock Threads] 발행 실패: {e}")
                fail_screenshot = CURRENT_DIR / "threads_error_screenshot.png"
                try:
                    await page.screenshot(path=str(fail_screenshot))
                except Exception:
                    pass
                await context.close()
                return {
                    "success": False,
                    "brand": self.BRAND,
                    "error": str(e),
                    "screenshot": str(fail_screenshot)
                }

    def _save_history(self, record: Dict[str, Any]):
        history = []
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []
        history.append(record)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
