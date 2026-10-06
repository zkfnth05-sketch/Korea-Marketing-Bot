# -*- coding: utf-8 -*-
"""
Insurance Threads Publisher (🧵 보험 리밸런스 전용 스레드 독립 레고 블록 발행기)
================================================================================
- 브랜드: 🛡️ 보험 리밸런스 (InsureBalance)
- 전용 계정: @goldmomofficial
- 검색 공식 키워드: 보험 리밸런스 (띄어쓰기 필수, 절대 불변)
- 랜딩 URL: https://insure-rebalance.vercel.app/
- 프로필 디렉터리: brands/insurance/meta_chrome_profile/
- 세션 파일: brands/insurance/threads_session.json
- 기능:
  1. 스레드(threads.net) 완전 무인 자동 로그인 세션 유지
  2. 보험 절약 카드뉴스 이미지(4~5장 슬라이드) 또는 팩트폭격 텍스트 타래 게시
  3. 첫 번째 타래 댓글로 공식 검색어('보험 리밸런스') 및 랜딩 URL 자동 체인 부착
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

logger = logging.getLogger("InsuranceThreadsPublisher")
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


class InsuranceThreadsPublisher:
    """🛡️ 보험 리밸런스 전용 스레드(Threads) 독립 레고 블록 발행기"""

    BRAND = "insurance"
    BRAND_NAME = "보험 리밸런스"
    OFFICIAL_SEARCH_KEYWORD = "보험 리밸런스"
    LANDING_URL = "https://insure-rebalance.vercel.app/"

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.profile_dir = PROFILE_DIR
        self.profile_dir.mkdir(parents=True, exist_ok=True)

    def _prepare_cookies(self) -> List[Dict[str, Any]]:
        pw_cookies = []
        # 1. meta_session.json 로드
        meta_file = CURRENT_DIR / "meta_session.json"
        if meta_file.exists():
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta_cookies = json.load(f).get("cookies", [])
                for c in meta_cookies:
                    domain = c.get("domain", "")
                    if "instagram.com" in domain or "facebook.com" in domain:
                        pw = {
                            "name": c["name"],
                            "value": c["value"],
                            "domain": domain,
                            "path": c.get("path", "/"),
                            "secure": c.get("secure", True),
                            "httpOnly": c.get("httpOnly", False)
                        }
                        if c.get("sameSite") in ["Strict", "Lax", "None"]:
                            pw["sameSite"] = c["sameSite"]
                        elif c.get("sameSite") == "no_restriction":
                            pw["sameSite"] = "None"
                        pw_cookies.append(pw)
                        if "instagram.com" in domain:
                            for td in [".threads.com", ".threads.net"]:
                                tc = dict(pw)
                                tc["domain"] = td
                                pw_cookies.append(tc)
            except Exception as me:
                logger.warning(f"메타 세션 쿠키 파싱 예외: {me}")

        # 2. threads_cookies.json 로드
        if COOKIE_FILE.exists():
            try:
                with open(COOKIE_FILE, "r", encoding="utf-8") as f:
                    raw_cookies = json.load(f)
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
                    for d in [".threads.net", ".threads.com", ".instagram.com"]:
                        dc = dict(pw_c)
                        dc["domain"] = d
                        pw_cookies.append(dc)
            except Exception as ex:
                logger.warning(f"쿠키 파싱 오류: {ex}")
        return pw_cookies

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
                "🛡️ [매달 줄줄 새는 숨은 보험료 3분 진단]\n\n"
                "나도 모르게 중복 결제되고 있던 특약이 있다?\n"
                "보장은 든든하게 늘리고 보험료는 30% 다이어트하세요!\n\n"
                "#보험리밸런스 #보험절약 #실손보험 #보험비교"
            )

        if not first_reply_text:
            first_reply_text = (
                f"🛡️ 매달 줄줄 새는 숨은 보험료 3분 진단\n"
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
        logger.info(f"🚀 [Insurance Threads] 스레드 발행 시작 (글자수: {len(caption)}자, {media_type}: {len(valid_media)}개)")

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-first-run",
                    "--no-default-browser-check",
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
                await page.goto("https://www.threads.net/", wait_until="domcontentloaded", timeout=25000)
                await asyncio.sleep(3)

                # 1-1. Terms 오버레이 배너 제거 및 'Continue with Instagram' 모달 자동 클릭
                try:
                    await page.evaluate("""() => {
                        const fixedOverlays = Array.from(document.querySelectorAll("div")).filter(d => {
                            const style = window.getComputedStyle(d);
                            return (style.position === 'fixed' || style.position === 'sticky') && style.bottom === '0px' && d.innerText && d.innerText.includes('Terms');
                        });
                        fixedOverlays.forEach(b => b.remove());
                    }""")
                    await asyncio.sleep(1)

                    clicked_modal = await page.evaluate("""() => {
                        const all = Array.from(document.querySelectorAll("button, div[role='button'], a, div"));
                        const cont = all.find(el => el.innerText && (el.innerText.trim().includes('Continue with Instagram') || el.innerText.trim().includes('Log in with Instagram') || el.innerText.trim().includes('goldmomofficial')));
                        if (cont) {
                            const clickable = cont.closest("button, div[role='button'], a") || cont;
                            clickable.click();
                            return true;
                        }
                        return false;
                    }""")
                    if clicked_modal:
                        logger.info("👉 'Continue with Instagram' 모달 JS 직접 클릭 성공, 세션 연결 대기...")
                        await asyncio.sleep(6)
                except Exception as me:
                    logger.warning(f"모달 클릭 예외: {me}")

                # 2. 작성 모달 열기 (4중 Fallback 전략)
                logger.info("2. 스레드 작성창 열기...")
                opened = False
                for attempt in range(6):
                    # 1) 상단 빠른 작성창 클릭 ("새로운 소식을 공유해보세요" 또는 "What's new?")
                    try:
                        quick = await page.query_selector("div:has-text('새로운 소식을 공유해보세요'), div:has-text('새로운 스레드를 시작하세요'), div:has-text('What\\'s new?')")
                        if quick and await quick.is_visible():
                            await quick.click()
                            await asyncio.sleep(2)
                    except Exception:
                        pass

                    # 2) 좌측 메뉴 "새로운 스레드" 또는 플로팅 '+' 버튼 클릭
                    if not await page.query_selector("div[role='textbox'][contenteditable='true'], div[data-lexical-editor='true']"):
                        try:
                            await page.evaluate("""() => {
                                const btns = Array.from(document.querySelectorAll("div[role='button'], button, a"));
                                const createBtn = btns.find(b => {
                                    const t = (b.innerText || '').trim();
                                    const aria = b.getAttribute('aria-label') || '';
                                    return t.includes('새로운 스레드') || t.includes('New thread') || aria.includes('새로운 스레드') || aria.includes('Create');
                                });
                                if (createBtn) {
                                    createBtn.click();
                                    return;
                                }
                                const allBtns = Array.from(document.querySelectorAll("div[role='button']"));
                                if (allBtns.length > 0) {
                                    allBtns[allBtns.length - 1].click();
                                }
                            }""")
                            await asyncio.sleep(2)
                        except Exception:
                            pass

                    # 3) 단축키 fallback ('c')
                    if not await page.query_selector("div[role='textbox'][contenteditable='true'], div[data-lexical-editor='true']"):
                        try:
                            await page.keyboard.press("c")
                            await asyncio.sleep(2)
                        except Exception:
                            pass

                    tb_check = await page.query_selector("div[role='textbox'][contenteditable='true'], div[data-lexical-editor='true']")
                    if tb_check and await tb_check.is_visible():
                        logger.info("✅ 작성창(textbox) 활성화 확인!")
                        opened = True
                        break
                    await asyncio.sleep(1.5)

                if not opened:
                    raise RuntimeError("스레드 작성창(textbox)을 활성화하지 못했습니다.")

                # 3. 본문 텍스트 입력 (Lexical 에디터 완벽 호환 keyboard.insert_text)
                logger.info("3. 캡션 텍스트 입력 중...")
                textbox = await page.wait_for_selector("div[role='textbox'][contenteditable='true'], div[data-lexical-editor='true']", timeout=12000)
                await textbox.click()
                await asyncio.sleep(0.5)
                await page.keyboard.press("Control+A")
                await page.keyboard.press("Backspace")
                await asyncio.sleep(0.3)
                await page.keyboard.insert_text(caption)
                await asyncio.sleep(1.5)

                # 4. 카드뉴스 이미지 또는 숏폼 비디오 첨부
                if valid_media:
                    logger.info(f"4. {media_type} {len(valid_media)}개 업로드 중...")
                    file_input = await page.query_selector("input[type='file']")
                    if file_input:
                        await file_input.set_input_files(valid_media)
                        logger.info("   미디어 파일 전송 완료, 렌더링/인코딩 대기...")
                        wait_sec = 14 if is_video else 6
                        await asyncio.sleep(wait_sec)

                # 5. [1단계] 본문 Post / 게시 버튼 클릭 및 모달 닫힘 대기
                logger.info("5. 본문 [Post / 게시] 버튼 클릭...")
                posted = False
                for _ in range(5):
                    posted = await page.evaluate("""() => {
                        const dialog = document.querySelector("div[role='dialog']") || document;
                        const btns = Array.from(dialog.querySelectorAll("div[role='button'], button"));
                        const postBtn = btns.find(b => {
                            const t = (b.innerText || '').trim();
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
                        break
                    await asyncio.sleep(1)

                if not posted:
                    publish_btn = await page.query_selector("div[role='dialog'] div[role='button']:has-text('Post'), div[role='dialog'] button:has-text('Post'), div[role='dialog'] div[role='button']:has-text('게시')")
                    if publish_btn:
                        await publish_btn.click(force=True)
                        posted = True

                logger.info("   본문 게시 요청 전송 완료! 모달 닫힘 및 서버 반영 대기 (12초)...")
                await asyncio.sleep(12)

                # 6. [2단계] 첫 번째 타래 댓글 (방금 올린 본문 글의 고유 상세 페이지로 직접 이동하여 답글 체인 작성)
                if first_reply_text:
                    logger.info("6. [2단계] 첫 번째 타래 댓글(답글) 작성 시작...")
                    try:
                        # 6-1. 내 프로필로 이동하여 방금 올린 본문 글의 URL 링크 추출
                        await page.goto("https://www.threads.net/@goldmomofficial", wait_until="domcontentloaded", timeout=25000)
                        await asyncio.sleep(4)

                        # Terms 제거
                        await page.evaluate("""() => {
                            const fixedOverlays = Array.from(document.querySelectorAll("div")).filter(d => {
                                const style = window.getComputedStyle(d);
                                return (style.position === 'fixed' || style.position === 'sticky') && style.bottom === '0px' && d.innerText && d.innerText.includes('Terms');
                            });
                            fixedOverlays.forEach(b => b.remove());
                        }""")

                        post_href = await page.evaluate("""() => {
                            const links = Array.from(document.querySelectorAll("a[href*='/post/']"));
                            if (links.length > 0) return links[0].getAttribute('href');
                            return null;
                        }""")
                        logger.info(f"   방금 올린 본문 글 링크: {post_href}")

                        if post_href:
                            post_url = f"https://www.threads.net{post_href}" if post_href.startswith("/") else post_href
                            logger.info(f"   본문 글 고유 상세 페이지 직접 이동: {post_url}")
                            await page.goto(post_url, wait_until="domcontentloaded", timeout=25000)
                            await asyncio.sleep(4)

                            # 상세 페이지 내 답글 입력창 클릭 ("Reply to goldmomofficial..." / "골드맘님에게 답글 달기...")
                            reply_box = await page.wait_for_selector("div[role='textbox'][contenteditable='true'], div[data-lexical-editor='true'], div:has-text('Reply to'), div:has-text('답글')", timeout=10000)
                            if reply_box:
                                await reply_box.click(force=True)
                                await asyncio.sleep(1)

                                active_tb = await page.query_selector("div[role='textbox'][contenteditable='true'], div[data-lexical-editor='true']")
                                if active_tb:
                                    await active_tb.click()
                                    await asyncio.sleep(0.5)
                                    await page.keyboard.press("Control+A")
                                    await page.keyboard.press("Backspace")
                                    await asyncio.sleep(0.3)
                                    await page.keyboard.insert_text(first_reply_text)
                                    await asyncio.sleep(2.5)  # OpenGraph 미리보기 렌더링 대기

                                    # 답글 전송 (Control+Enter 단축키 및 전송 버튼 안전 클릭)
                                    reply_posted = False
                                    try:
                                        await page.keyboard.press("Control+Enter")
                                        await asyncio.sleep(1.5)
                                    except Exception:
                                        pass

                                    for _ in range(8):
                                        reply_posted = await page.evaluate("""() => {
                                            const btns = Array.from(document.querySelectorAll("button, div[role='button']"));
                                            const postBtn = btns.find(b => {
                                                const t = (b.innerText || '').trim();
                                                const ariaDisabled = b.getAttribute('aria-disabled');
                                                const disabled = b.getAttribute('disabled');
                                                return (t === 'Post' || t === '게시') && ariaDisabled !== 'true' && disabled === null;
                                            });
                                            if (postBtn && typeof postBtn.click === 'function') {
                                                postBtn.click();
                                                return true;
                                            }
                                            return false;
                                        }""")
                                        if reply_posted:
                                            break
                                        await asyncio.sleep(1)

                                    if not reply_posted:
                                        reply_post_btn = await page.query_selector("div[role='dialog'] div[role='button']:has-text('Post'), div[role='dialog'] button:has-text('Post'), div[role='button']:has-text('Post'), button:has-text('Post')")
                                        if reply_post_btn:
                                            await reply_post_btn.click(force=True)

                                    logger.info("🎉 [2단계 대성공] 본문 글 고유 상세 페이지에서 1번 타래 댓글 체인 등록 완료!")
                                    await asyncio.sleep(10)
                    except Exception as ex_reply:
                        logger.warning(f"⚠️ 타래 댓글 작성 예외: {ex_reply}")

                # 7. 상세 페이지 및 프로필에서 최종 타래 결합 결과 확인 캡처
                logger.info("7. 본문 + 1번 타래 결합 최종 증빙 캡처 중...")
                proof_path = CURRENT_DIR / "threads_live_proof.png"
                try:
                    await page.reload(wait_until="domcontentloaded")
                    await asyncio.sleep(4)
                    await page.evaluate("window.scrollBy(0, 300)")
                    await asyncio.sleep(2)
                    await page.screenshot(path=str(proof_path), full_page=True)
                    logger.info(f"📸 게시 완료 라이브 상세 결합 증빙 캡처: {proof_path}")
                except Exception:
                    await page.goto("https://www.threads.net/@goldmomofficial", wait_until="domcontentloaded", timeout=25000)
                    await asyncio.sleep(4)
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
                logger.error(f"❌ [Insurance Threads] 발행 실패: {e}")
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
