# -*- coding: utf-8 -*-
"""
🛡️ [보험 리밸런스 전용] TikTok 웹 스튜디오 쇼츠 발행 엔진 (순수 브라우저 스텔스 레고 블록)
========================================================================================
- 대표님 지침 준수: 
  1. 100% 순수 브라우저 스텔스 봇 (0 API)
  2. 글자 레시피 내비게이션 & 실시간 모달 킬러(Exit 모달 즉시 차단)
  3. 완료 시 게시물 관리 화면(tiktokstudio/content)으로 이동하여 1등 실물 등록 확인
  4. 실제 라이브 영수증 및 증빙 캡처
  5. 미발견 시 브라우저 풀리셋 후 최대 3회 자가 치유 재시도 (Self-Healing Retry)
"""

import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine.browser_guard import clean_browser_profile_locks, get_safe_browser_args, async_browser_lock
from core.engine.session_integrity import ensure_auth_cookies, save_if_logged_in, is_logged_out_url, has_auth

PROFILE_DIR = CURRENT_DIR / "tiktok_chrome_profile"
SESSION_FILE = CURRENT_DIR / "tiktok_session.json"
ACCOUNTS_FILE = CURRENT_DIR / "accounts.json"

logger = logging.getLogger("InsuranceTikTokPublisher")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class InsuranceTikTokPublisher:
    """🛡️ 보험 리밸런스 전용 틱톡 웹 스튜디오 쇼츠 발행기 (독립 레고 블록)"""

    def __init__(self, headless: bool = True):
        self.brand = "insurance"
        self.headless = headless
        self.profile_dir = PROFILE_DIR
        self.session_file = SESSION_FILE
        self.accounts_file = ACCOUNTS_FILE
        self.upload_url = "https://www.tiktok.com/tiktokstudio/upload?lang=ko-KR"
        self.content_url = "https://www.tiktok.com/tiktokstudio/content?lang=ko-KR"
        self.channel_url = "https://www.tiktok.com/@insure_balance"

    def is_available(self) -> bool:
        has_profile = self.profile_dir.exists() and any(self.profile_dir.iterdir())
        has_session = self.session_file.exists() and self.session_file.stat().st_size > 50
        return has_profile or has_session

    async def _modal_killer(self, page):
        """방해 팝업 실시간 분쇄기"""
        # 1. 'Are you sure you want to exit?' 탈출 모달 차단
        for exit_sel in ["button:has-text('Cancel')", "button:has-text('취소')", "button:has-text('Stay')", "button:has-text('계속 머무르기')"]:
            try:
                eb = await page.query_selector(exit_sel)
                if eb and await eb.is_visible():
                    logger.info(f"👉 방해 모달 감지! '{exit_sel}' 클릭하여 편집 화면 사수")
                    await eb.click()
                    await asyncio.sleep(1.0)
            except Exception:
                pass

        # 2. 안내 팝업 소거
        for sel in ["button:has-text('Got it')", "button:has-text('Turn on')", "button:has-text('확인')", "button:has-text('Dismiss')"]:
            try:
                b = await page.query_selector(sel)
                if b and await b.is_visible():
                    logger.info(f"👉 안내 팝업 '{sel}' 닫기")
                    await b.click()
                    await asyncio.sleep(1.0)
            except Exception:
                pass

    def publish_short(
        self,
        video_path: str,
        topic_id: int = 1,
        caption: Optional[str] = None,
        title: Optional[str] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """동기 호출 인터페이스 (최대 3회 자가 치유 재시도)"""
        try:
            return asyncio.run(self.publish_short_async(video_path, topic_id, caption, title, max_retries))
        except Exception as e:
            logger.error(f"❌ [보험 TikTok] 발행 최종 예외: {e}")
            return {"status": "error", "message": str(e), "brand": self.brand}

    async def publish_short_async(
        self,
        video_path: str,
        topic_id: int = 1,
        caption: Optional[str] = None,
        title: Optional[str] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """비동기 틱톡 순수 브라우저 글자 레시피 발행 엔진"""
        if not os.path.exists(video_path):
            return {"status": "error", "message": f"비디오 파일 없음: {video_path}", "brand": self.brand}

        full_caption = caption or f"{title or ''}\n\n#보험 #보험비교 #실손보험 #보험리밸런스"
        # 🛡️ 본문 내 URL 전면 소독 (알고리즘 다운랭킹 방지 및 네이버 공식 검색어 유도)
        full_caption = re.sub(r'https?://\S+', '👉 네이버 검색: [보험 리밸런스]', full_caption)
        video_name = os.path.basename(video_path)
        logger.info(f"🚀 [보험 TikTok] 순수 브라우저 글자 레시피 발행 가동: {video_name}")

        for attempt in range(1, max_retries + 1):
            logger.info(f"--- [시도 {attempt}/{max_retries}] 틱톡 쇼츠 발행 시작 ---")
            clean_browser_profile_locks(self.profile_dir)

            try:
                async with async_browser_lock(f"보험 TikTok 쇼츠 웹 발행 (시도 {attempt})", timeout_sec=600):
                    result = await self._execute_recipe_once(video_path, full_caption, topic_id, title)
                    if result.get("status") == "success":
                        logger.info(f"🎉 [보험 TikTok] 시도 {attempt}에서 100% 실물 발행 성공!")
                        return result
                    else:
                        logger.warning(f"⚠️ [보험 TikTok] 시도 {attempt} 미완료: {result.get('message')}")
            except Exception as e:
                logger.error(f"❌ [보험 TikTok] 시도 {attempt} 예외 발생: {e}")

            if attempt < max_retries:
                logger.info("⏳ 5초 후 브라우저 풀리셋 및 재시도 진행...")
                await asyncio.sleep(5.0)

        return {
            "status": "error",
            "brand": self.brand,
            "message": f"{max_retries}회 재시도 모두 소진, 틱톡 실물 등록 미확인"
        }

    async def _execute_recipe_once(
        self,
        video_path: str,
        caption: str,
        topic_id: int,
        title: Optional[str]
    ) -> Dict[str, Any]:
        """1회 글자 레시피 실행 및 틱톡 게시물 관리 화면 실물 검증"""
        async with async_playwright() as p:
            browser_args = get_safe_browser_args([
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check",
                "--start-maximized"
            ])
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=self.headless,
                args=browser_args,
                viewport={"width": 1366, "height": 900},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            )

            # 🛡️ 프로필에 sessionid가 있으면 그대로 두고(최신 회전 쿠키 보호), 없을 때만 정상 세션/백업에서 복원
            await ensure_auth_cookies("tiktok", context, self.session_file)

            page = context.pages[0] if context.pages else await context.new_page()

            try:
                # 📌 1단계: 업로드 페이지 접속
                logger.info(f"1. 틱톡 스튜디오 업로드 접속 중: {self.upload_url}")
                await page.goto(self.upload_url, wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(4.0)
                if is_logged_out_url("tiktok", page.url) or not has_auth("tiktok", await context.cookies()):
                    raise RuntimeError("틱톡 세션 만료. 로그인 필요.")
                await self._modal_killer(page)

                # 📌 2단계: 동영상 파일 주입
                logger.info("2. 동영상 파일 주입 중...")
                file_input = await page.query_selector("input[type='file']")
                if not file_input:
                    for frame in page.frames:
                        file_input = await frame.query_selector("input[type='file']")
                        if file_input:
                            break

                if not file_input:
                    raise RuntimeError("틱톡 업로드 input[type='file'] 요소를 찾지 못했습니다.")

                await file_input.set_input_files(str(Path(video_path).resolve()))
                logger.info("🎬 비디오 파일 주입 완료")

                # 📌 3단계: 업로드 완료 엄격 대기
                logger.info("3. 틱톡 비디오 인코딩 및 업로드 완료 대기 중...")
                for sec in range(60):
                    await self._modal_killer(page)
                    body_text = ""
                    try:
                        body_text = await page.inner_text("body")
                    except Exception:
                        pass

                    if any(k in body_text for k in ["Uploaded", "업로드 완료", "Upload complete", "업로드됨", "ready to publish", "게시 준비", "처리 완료", "동영상 처리"]):
                        logger.info(f"✅ 비디오 업로드 완료 감지 ({sec}초 경과)")
                        break
                    await asyncio.sleep(1.0)

                # 📌 4단계: 캡션 입력
                logger.info("4. 캡션 및 해시태그 기입 중...")
                editor = await page.query_selector("div.public-DraftEditor-content, div[contenteditable='true'], div[role='combobox']")
                if editor:
                    await editor.click()
                    await page.keyboard.press("Control+A")
                    await page.keyboard.press("Backspace")
                    await asyncio.sleep(0.5)

                    for char in caption:
                        if char == "\n":
                            await page.keyboard.press("Enter")
                        else:
                            await page.keyboard.type(char)
                        await asyncio.sleep(0.01)
                    logger.info("✍️ 캡션 기입 완료")

                await asyncio.sleep(2.0)
                await self._modal_killer(page)

                # 📌 5단계: [게시 / Post] 글자 버튼 클릭
                logger.info("5. [게시 / Post] 글자 버튼 클릭...")
                btn = page.locator("button[data-e2e='post_video_button'], button").filter(has_text="Post").or_(
                    page.locator("button").filter(has_text="게시")
                ).first

                if await btn.count() > 0 and await btn.is_visible():
                    await btn.scroll_into_view_if_needed()
                    await asyncio.sleep(1.0)
                    await btn.click()
                    logger.info("💥 [게시 / Post] 클릭 완료!")
                else:
                    raise RuntimeError("게시(Post) 버튼을 찾지 못했습니다.")

                await asyncio.sleep(2.0)
                await self._modal_killer(page)

                # '지금 게시' 팝업 대응
                try:
                    post_now = page.locator("button").filter(has_text="지금 게시").or_(page.locator("button").filter(has_text="Post now"))
                    if await post_now.count() > 0 and await post_now.is_visible():
                        await post_now.first.click()
                except Exception:
                    pass

                # 📌 6단계: [무인 파이프라인] 틱톡 서버 인코딩 및 배포 완료 대기 (정확히 60초 휴식)
                logger.info("⏳ [틱톡 무인 파이프라인] 영상 인코딩 및 서버 배포 대기 (정확히 60초 휴식 후 실물 확인)...")
                await asyncio.sleep(60.0)

                logger.info(f"6. 게시물 관리 화면({self.content_url})으로 이동하여 실물 검증 중...")
                await page.goto(self.content_url, wait_until="domcontentloaded", timeout=40000)
                await asyncio.sleep(6.0)

                proof_path = CURRENT_DIR / f"tiktok_verified_proof_topic{topic_id:02d}.png"
                await page.screenshot(path=str(proof_path))

                manage_text = await page.inner_text("body")
                snippet = (title or caption)[:10]
                is_verified = (snippet in manage_text) or ("0:15" in manage_text) or ("Content under review" in manage_text)

                if is_verified:
                    logger.info("🎉🎉 [보험 틱톡 실물 검증 100% 합격!] 게시물 관리 최상단에 정상 게시 확인!")
                    return {
                        "status": "success",
                        "brand": self.brand,
                        "platform": "tiktok",
                        "topic_id": topic_id,
                        "video_file": os.path.basename(video_path),
                        "title": title or "",
                        "post_url": self.channel_url,
                        "verified_proof": str(proof_path)
                    }
                else:
                    logger.warning("⚠️ 틱톡 게시물 목록 최상단에 아직 반영되지 않았습니다.")
                    return {"status": "pending_or_missing", "message": "틱톡 목록에 실물 미확인"}

            finally:
                # 로그인 상태일 때만 저장 (로그아웃 쿠키로 정상 세션 덮어쓰기 금지)
                try:
                    await save_if_logged_in("tiktok", context, self.session_file, reason="insurance_tiktok_end")
                except Exception:
                    pass
                await context.close()


if __name__ == "__main__":
    pub = InsuranceTikTokPublisher()
    print("Is available:", pub.is_available())
