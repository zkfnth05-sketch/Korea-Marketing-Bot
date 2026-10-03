# -*- coding: utf-8 -*-
"""
Aura Threads Publisher (🧵 Aura 전용 스레드 독립 레고 블록 발행기)
===================================================================
- 브랜드: 💖 Aura (AI 데이팅)
- 전용 계정: @aura_ai_dating
- 검색 공식 키워드: 아우라AI데이팅 (절대 불변)
- 랜딩 URL: https://aura-ai-dating.vercel.app/
- 프로필 디렉터리: brands/aura/meta_chrome_profile/
- 세션 파일: brands/aura/threads_session.json
- 기능:
  1. 스레드(threads.net) 완전 무인 자동 로그인 세션 유지
  2. 카드뉴스 이미지(4~5장 슬라이드) 또는 텍스트 타래 게시 (500자 규격 자동 최적화)
  3. 첫 번째 타래 댓글로 공식 검색어('아우라AI데이팅') 및 랜딩 URL 자동 체인 부착
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

logger = logging.getLogger("AuraThreadsPublisher")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
PROFILE_DIR = CURRENT_DIR / "meta_chrome_profile"
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
        if s.startswith("=") or s.startswith("•") or "주제:" in s or "의상:" in s or "산출 규격:" in s or "구성 안내" in s:
            continue
        clean.append(s)
    
    body = "\n\n".join(clean)
    if len(body) > 420:
        body = body[:400] + "..."
    return body


class AuraThreadsPublisher:
    """💖 Aura 전용 스레드(Threads) 독립 레고 블록 발행기"""

    BRAND = "aura"
    BRAND_NAME = "Aura AI 데이팅"
    OFFICIAL_SEARCH_KEYWORD = "아우라AI데이팅"
    LANDING_URL = "https://aura-ai-dating.vercel.app/"

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
                "📍 [500m 안심 레이더 & 안심 번개 매칭]\n\n"
                "집 주소 노출될까 봐 불안하셨죠?\n"
                "내 집 앞 500m 안심 지터링 보안으로 안전하게!\n\n"
                "거리와 취향까지 딱 맞는 내 반경 500m 인연을 지금 확인해보세요 ✨\n\n"
                "#Aura #데이팅 #소개팅 #안심매칭 #2030"
            )

        if not first_reply_text:
            first_reply_text = (
                f"💖 2030 매력 진단 & AI 매칭 리포트\n"
                f"네이버에 '{self.OFFICIAL_SEARCH_KEYWORD}' 한번 검색해보세요!\n"
                f"👉 {self.LANDING_URL}"
            )

        valid_images = []
        if image_paths:
            for p in image_paths:
                fpath = Path(p)
                if fpath.exists() and fpath.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
                    valid_images.append(str(fpath.resolve()))

        logger.info(f"🚀 [Aura Threads] 스레드 발행 시작 (글자수: {len(caption)}자, 이미지: {len(valid_images)}장)")

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
                await page.goto("https://www.threads.net/", wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(4)

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

                # 4. 카드뉴스 이미지 첨부
                if valid_images:
                    logger.info(f"4. 카드뉴스 이미지 {len(valid_images)}장 업로드 중...")
                    file_input = await page.query_selector("input[type='file']")
                    if file_input:
                        await file_input.set_input_files(valid_images)
                        logger.info("   이미지 파일 전송 완료, 렌더링 대기...")
                        await asyncio.sleep(6)

                # 5. 첫 번째 타래 댓글 (Add to thread)
                if first_reply_text:
                    logger.info("5. 첫 번째 타래 댓글 작성 시도...")
                    try:
                        add_btn = await page.query_selector("div:has-text('Add to thread'), span:has-text('Add to thread'), div:has-text('스레드에 추가')")
                        if add_btn:
                            await add_btn.click(force=True)
                            await asyncio.sleep(1.5)
                            boxes = await page.query_selector_all("div[role='textbox'][contenteditable='true'], div[data-lexical-editor='true']")
                            if len(boxes) >= 2:
                                second_box = boxes[-1]
                                await second_box.click(force=True)
                                await second_box.fill(first_reply_text)
                                await asyncio.sleep(1)
                                logger.info("   타래 댓글 작성 완료!")
                    except Exception as ex_comment:
                        logger.warning(f"   타래 댓글 첨부 건너뜀: {ex_comment}")

                # 6. Post / 게시 버튼 클릭
                logger.info("6. 스레드 [Post / 게시] 버튼 클릭...")
                posted = False
                try:
                    # JavaScript evaluate 로 모달 내의 Post 버튼 직접 클릭
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
                        logger.info("   JS 직접 클릭 성공!")
                except Exception:
                    pass

                if not posted:
                    publish_btn = await page.wait_for_selector("div[role='dialog'] div[role='button']:has-text('Post'), div[role='dialog'] button:has-text('Post')", timeout=8000)
                    if publish_btn:
                        await publish_btn.click(force=True)
                        posted = True

                logger.info("   게시 완료! 서버 반영 대기 (12초)...")
                await asyncio.sleep(12)

                # 7. 프로필 페이지로 이동하여 최종 송출 확인 캡처
                logger.info("7. 프로필 페이지에서 송출 결과 확인 중...")
                await page.goto("https://www.threads.net/@aura_ai_dating", wait_until="domcontentloaded", timeout=25000)
                await asyncio.sleep(5)

                proof_path = CURRENT_DIR / "threads_live_proof.png"
                await page.screenshot(path=str(proof_path))
                logger.info(f"📸 게시 완료 라이브 증빙 캡처: {proof_path}")

                # 8. 세션 및 히스토리 보관
                await context.storage_state(path=str(SESSION_FILE))

                result_record = {
                    "brand": self.BRAND,
                    "published_at": datetime.now().isoformat(),
                    "caption_preview": caption[:60] + "...",
                    "images_count": len(valid_images),
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
                logger.error(f"❌ [Aura Threads] 발행 실패: {e}")
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


async def main():
    publisher = AuraThreadsPublisher(headless=True)
    target_folder = r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\아우라\아우라_08_500m안심레이더_20261001_1100"
    
    images = [str(Path(target_folder) / f"slide_{i}.png") for i in range(1, 6)]
    
    caption = (
        "📍 [500m 안심 레이더 & 성수동 테라스 번개]\n\n"
        "집 주소 노출될까 봐 불안하셨죠?\n"
        "내 집 앞 500m 안심 지터링 보안으로 집 주소 노출 없이 안전하게!\n\n"
        "거리와 취향까지 딱 맞는 내 반경 500m 인연을 지금 만나보세요 ✨\n\n"
        "#Aura #아우라 #데이팅 #소개팅 #안심매칭 #2030"
    )

    res = await publisher.publish_thread(
        caption=caption,
        image_paths=images,
        first_reply_text="💖 2030 매력 진단 & AI 매칭 리포트\n네이버에 '아우라AI데이팅' 한번 검색해보세요!\n👉 https://aura-ai-dating.vercel.app/"
    )
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
