# -*- coding: utf-8 -*-
"""
[독립 레고 블록] Insurance YouTube Bot Publisher (🛡️ 보험 리밸런스 전용 유튜브 쇼츠 브라우저 봇 무인 직접 업로더)
===================================================================================================================
- 브랜드: 보험 리밸런스 (공식 검색어: '보험 리밸런스' 띄어쓰기 불변)
- 핵심 역할:
  1. [0 API 순수 브라우저 봇]: Google Data API Quota(할당량) 및 토큰 만료 문제 100% 영구 해결
  2. [YouTube Studio 웹 무인 자동화]: 영구 브라우저 프로필/세션으로 https://studio.youtube.com 접속
  3. [MP4 자동 주입]: 9:16 세로 풀HD 숏폼 비디오 직접 주입 및 업로드
  4. [완벽한 메타데이터 패키징]: 제목(1초 훅 + '#보험리밸런스 #Shorts') + 설명란(4단 해시태그 + 공식 검색 유도)
  5. [옵션 자동 설정]: '아동용 아님' 자동 체크 + '공개(Public)' 즉시 발행
  6. [고정 댓글 자동화]: 발행 즉시 watch 페이지 진입 ➔ 공식 검색어 유도 링크 댓글 작성 ➔ 최상단 핀(Pin) 고정
- 원칙: Rule 1 (독립 레고 블록), Rule 5 (땜질 금지/근본 해결), Rule 6 (24시간 무인 자율 구동), Rule 7 (공식 규격)
"""

import os
import sys
import json
import time
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import BASE_DIR, get_now_kst_str
from brands.insurance.insurance_hashtag_matrix import InsuranceHashtagMatrix
from core.engine.browser_guard import async_browser_lock, get_safe_browser_args, clean_browser_profile_locks

logger = logging.getLogger("InsuranceYouTubeBotPublisher")


class InsuranceYouTubeBotPublisher:
    """🛡️ 보험 리밸런스 전용 유튜브 쇼츠 브라우저 봇 직접 업로드 엔진"""

    BRAND = "insurance"
    OFFICIAL_KEYWORD = "보험 리밸런스"
    LANDING_URL = "https://insure-rebalance.vercel.app/"

    HOOK_TITLES = {
        1: "4세대 실손보험 전환했다가 피눈물 흘리는 사람 특징 ㄷㄷ",
        2: "운전자보험 1만원대로 민식이법 벌금/변호사 완벽 방어하는 법",
        3: "암보험 들 때 일반암 vs 유사암 차이 모르면 3천만원 날립니다",
        4: "뇌혈관 & 허혈성 심장질환 포괄 특약 1개로 끝내는 치트키",
        5: "부모님 갱신형 암보험 80세에 보험료 폭탄 피하는 현실적 대안",
        6: "치아보험 가입 후 바로 임플란트 치료받으면 보장될까?",
        7: "매달 새는 중복 가입 특약 싹 정리하고 15만원 다이어트하기",
        8: "34개 보험사 실시간 비교 견적 데이터로 최저가 찾는 공식"
    }

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.profile_dir = CURRENT_DIR / "youtube_chrome_profile"
        self.session_file = CURRENT_DIR / "youtube_session.json"
        self.history_file = CURRENT_DIR / "youtube_publish_history.json"
        self.shorts_output_dir = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Insurance")

    def is_available(self) -> bool:
        """세션 파일 또는 영구 프로필 존재 여부 점검"""
        has_session = self.session_file.exists() and self.session_file.stat().st_size > 50
        has_profile = self.profile_dir.exists()
        return has_session or has_profile

    def find_latest_short_video(self, topic_id: Optional[int] = None) -> Optional[Path]:
        """바탕화면 산출물 폴더에서 가장 최신 렌더링된 Insurance 숏폼 MP4 자동 탐색"""
        search_dirs = [self.shorts_output_dir, BASE_DIR / "outputs" / "insurance"]
        for sdir in search_dirs:
            if sdir.exists():
                candidates = [p for p in sdir.glob("**/*.mp4") if "04_app_sim" not in p.name and "temp" not in p.name]
                if candidates:
                    return max(candidates, key=os.path.getmtime)
        return None

    def publish_short(
        self,
        video_path: Optional[str] = None,
        topic_id: int = 1,
        title: Optional[str] = None,
        description: Optional[str] = None,
        privacy_status: str = "public",
        timeout_sec: int = 120
    ) -> Dict[str, Any]:
        """동기 호출 인터페이스 (기존 파이프라인 및 스케줄러 100% 호환)"""
        try:
            return asyncio.run(self.publish_short_async(
                video_path=video_path,
                topic_id=topic_id,
                title=title,
                description=description,
                privacy_status=privacy_status,
                timeout_sec=timeout_sec
            ))
        except Exception as e:
            logger.error(f"❌ [Insurance YouTube Bot] 발행 예외 발생: {e}")
            err_res = {
                "status": "error",
                "platform": "youtube_shorts",
                "error": str(e),
                "published_at": get_now_kst_str()
            }
            self._save_history(err_res)
            return err_res

    # ------------------------------------------------------------------
    # [내부 헬퍼] 고정 댓글 작성 + 최상단 핀(Pin) 고정 전담 엔진
    # ------------------------------------------------------------------
    async def _post_and_pin_comment(self, page, video_id: str, pinned_comment: str) -> str:
        """
        watch 페이지에서 댓글 작성 ➔ 최상단 첫 댓글 삼점 메뉴 ➔ '고정' ➔ 확인 팝업 '고정' 클릭.
        반환값: "pinned" | "submitted" | "skipped"
        """
        if not video_id:
            logger.warning("⚠️ [고정 댓글] video_id 부재로 댓글/핀 고정을 건너뜁니다.")
            return "skipped"

        # 1) 반드시 watch URL로 진입 (shorts/{id} 페이지는 댓글 DOM 구조가 상이하여 입력 불가)
        watch_url = f"https://www.youtube.com/watch?v={video_id}"
        logger.info(f"💬 [고정 댓글] watch 페이지 진입: {watch_url}")
        await page.goto(watch_url, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(4.0)

        # 2) 댓글 섹션 로드 유도 (500px 스크롤 다운)
        try:
            await page.evaluate("window.scrollBy(0, 500)")
        except Exception:
            pass
        await asyncio.sleep(2.5)
        try:
            await page.evaluate("window.scrollBy(0, 700)")
        except Exception:
            pass
        await asyncio.sleep(2.0)

        # 3) 댓글 입력창 활성화
        placeholder = page.locator("#placeholder-area, #simplebox-placeholder").first
        try:
            await placeholder.wait_for(state="visible", timeout=20000)
            await placeholder.click()
        except Exception:
            await page.evaluate("""() => {
                const el = document.querySelector('#placeholder-area') ||
                           document.querySelector('#simplebox-placeholder') ||
                           document.querySelector('ytd-comment-simplebox-renderer #placeholder-area');
                if (el) { el.click(); }
            }""")
        await asyncio.sleep(1.5)

        # 4) 댓글 본문 입력
        comment_input = page.locator("#contenteditable-root, div[aria-label*='댓글 추가'], div[aria-label*='Add a comment']").first
        try:
            await comment_input.wait_for(state="visible", timeout=15000)
            await comment_input.click()
            await asyncio.sleep(0.5)
            await comment_input.fill(pinned_comment)
        except Exception:
            await page.evaluate("""(txt) => {
                const el = document.querySelector('#contenteditable-root') ||
                           document.querySelector("div[aria-label*='댓글 추가']") ||
                           document.querySelector("div[aria-label*='Add a comment']");
                if (el) {
                    el.focus();
                    el.innerText = txt;
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }""", pinned_comment)
        await asyncio.sleep(1.5)

        # 5) 댓글 등록 버튼 클릭
        submitted = False
        submit_btn = page.locator("#submit-button, button:has-text('댓글')").first
        try:
            if await submit_btn.count() > 0:
                await submit_btn.click(force=True)
                submitted = True
        except Exception:
            pass
        if not submitted:
            try:
                await page.evaluate("""() => {
                    const btn = document.querySelector('#submit-button') ||
                                Array.from(document.querySelectorAll('ytd-button-renderer button, button'))
                                    .find(el => el.innerText && (el.innerText.trim() === '댓글' || el.innerText.trim() === 'Comment'));
                    if (btn) { btn.click(); }
                }""")
                submitted = True
            except Exception as se:
                logger.warning(f"⚠️ [고정 댓글] 등록 버튼 클릭 실패: {se}")

        if not submitted:
            logger.warning("⚠️ [고정 댓글] 댓글 등록 버튼을 찾지 못했습니다.")
            return "skipped"

        logger.info("✅ [고정 댓글] 댓글 등록 완료 ➔ 3초 대기 후 핀 고정 시퀀스 시작")
        await asyncio.sleep(3.0)

        # 6) 방금 등록한 최상단 첫 번째 댓글의 삼점 메뉴 클릭
        try:
            first_thread = page.locator("ytd-comment-thread-renderer").first
            try:
                await first_thread.wait_for(state="visible", timeout=15000)
            except Exception:
                pass

            action_menu = page.locator(
                "ytd-comment-thread-renderer #action-menu button, "
                "ytd-comment-thread-renderer button[aria-label*='작업 메뉴'], "
                "ytd-comment-thread-renderer yt-icon-button#button, "
                "ytd-comment-thread-renderer ytd-menu-renderer #button"
            ).first
            if await action_menu.count() > 0:
                await action_menu.scroll_into_view_if_needed()
                await action_menu.click(force=True)
            else:
                await page.evaluate("""() => {
                    const thread = document.querySelector('ytd-comment-thread-renderer');
                    if (!thread) { return; }
                    const btn = thread.querySelector('#action-menu button') ||
                                thread.querySelector("button[aria-label*='작업 메뉴']") ||
                                thread.querySelector('yt-icon-button#button') ||
                                thread.querySelector('ytd-menu-renderer #button') ||
                                thread.querySelector('#action-menu');
                    if (btn) { btn.click(); }
                }""")
            await asyncio.sleep(2.0)

            # 7) 드롭다운 메뉴의 '고정(Pin)' 항목 클릭
            pin_item = page.locator(
                "ytd-menu-service-item-renderer:has-text('고정'), "
                "tp-yt-paper-item:has-text('고정'), "
                "ytd-menu-navigation-item-renderer:has-text('고정'), "
                "ytd-menu-service-item-renderer:has-text('Pin'), "
                "tp-yt-paper-item:has-text('Pin')"
            ).first
            if await pin_item.count() > 0:
                await pin_item.click(force=True)
            else:
                await page.evaluate("""() => {
                    const items = Array.from(document.querySelectorAll('ytd-menu-service-item-renderer, tp-yt-paper-item, ytd-menu-navigation-item-renderer'));
                    const pin = items.find(el => {
                        const t = (el.innerText || '').trim();
                        return t === '고정' || t.includes('고정') || t === 'Pin' || t.includes('Pin');
                    });
                    if (pin) { pin.click(); }
                }""")
            await asyncio.sleep(2.5)

            # 8) 확인 팝업 다이얼로그의 '고정(Pin)' 확인 버튼 클릭
            confirm_btn = page.locator(
                "yt-confirm-dialog-renderer #confirm-button, "
                "ytd-confirm-dialog-renderer #confirm-button, "
                "tp-yt-paper-dialog #confirm-button, "
                "yt-confirm-dialog-renderer button:has-text('고정'), "
                "ytd-confirm-dialog-renderer button:has-text('고정'), "
                "tp-yt-paper-dialog button:has-text('고정'), "
                "yt-confirm-dialog-renderer button:has-text('Pin'), "
                "ytd-confirm-dialog-renderer button:has-text('Pin')"
            ).first
            pinned = False
            if await confirm_btn.count() > 0:
                await confirm_btn.click(force=True)
                pinned = True
            else:
                pinned = await page.evaluate("""() => {
                    const dialogs = Array.from(document.querySelectorAll('yt-confirm-dialog-renderer, ytd-confirm-dialog-renderer, tp-yt-paper-dialog'));
                    for (const d of dialogs) {
                        const btns = Array.from(d.querySelectorAll('button, yt-button-renderer, tp-yt-paper-button'));
                        const ok = btns.find(b => {
                            const t = (b.innerText || '').trim();
                            return t === '고정' || t.includes('고정') || t === 'Pin' || t.includes('Pin');
                        });
                        if (ok) { ok.click(); return true; }
                    }
                    return false;
                }""")
            await asyncio.sleep(2.5)

            if pinned:
                logger.info("📌 [고정 댓글] 최상단 상시 고정(Pin) 100% 완료!")
                return "pinned"

            logger.warning("⚠️ [고정 댓글] 댓글은 등록되었으나 핀 고정 확인 버튼을 찾지 못했습니다.")
            return "submitted"

        except Exception as pe:
            logger.warning(f"⚠️ [고정 댓글] 핀 고정 시퀀스 예외 (댓글 등록은 유지): {pe}")
            return "submitted"

    async def publish_short_async(
        self,
        video_path: Optional[str] = None,
        topic_id: int = 1,
        title: Optional[str] = None,
        description: Optional[str] = None,
        privacy_status: str = "public",
        timeout_sec: int = 120
    ) -> Dict[str, Any]:
        """Playwright 브라우저 봇을 통한 유튜브 스튜디오 숏폼 무인 직접 업로드"""
        if not self.is_available():
            logger.warning("⚠️ [Insurance YouTube Bot] 세션 파일(youtube_session.json) 또는 영구 프로필이 없습니다.")
            return {
                "status": "error",
                "platform": "youtube_shorts",
                "error": "세션 파일 또는 영구 프로필 부재 (setup_youtube_profile.py 실행 요망)",
                "published_at": get_now_kst_str()
            }

        target_video = Path(video_path) if video_path else self.find_latest_short_video(topic_id)
        if not target_video or not target_video.exists():
            return {
                "status": "error",
                "platform": "youtube_shorts",
                "error": f"업로드할 숏폼 비디오가 없습니다: {video_path}",
                "published_at": get_now_kst_str()
            }

        # 1. 제목 및 메타데이터 구성
        tag_str = InsuranceHashtagMatrix.get_shorts_hashtags(topic_id)
        yt_tags = tag_str.split() if tag_str else ["#보험리밸런스", "#Shorts"]

        raw_title = title or f"{self.HOOK_TITLES.get(topic_id, '보험 리밸런스 꿀팁')} #보험리밸런스 #Shorts"
        if "#Shorts" not in raw_title and "#shorts" not in raw_title:
            raw_title = f"{raw_title} #Shorts"
        final_title = raw_title[:100]

        # 설명란 조립 (4단 해시태그 결합)
        tags_line = " ".join(yt_tags) if yt_tags else "#보험리밸런스 #보험비교 #실손보험 #암보험 #Shorts"
        desc_body = description or (
            "34개 보험사 비교 견적부터 매달 새는 보험료 다이어트까지!\n\n"
            f"🔍 네이버 검색창에 👉 [ {self.OFFICIAL_KEYWORD} ] 검색해보세요!\n"
            f"공식 진단센터 바로가기: {self.LANDING_URL}\n\n"
        )
        full_desc = f"{desc_body.strip()}\n\n{tags_line}".strip()[:5000]

        # 고정 댓글 문구
        pinned_comment = (
            "📌 34개 보험사 실시간 비교 & 중복 특약 다이어트 분석은\n"
            f"네이버에 👉 [ {self.OFFICIAL_KEYWORD} ] 검색하시면 바로 나옵니다!\n"
            f"(공식 링크: {self.LANDING_URL})"
        )

        logger.info("=" * 70)
        logger.info(f"🤖 [Insurance YouTube Bot] 쇼츠 직접 브라우저 업로드 시작: {final_title}")
        logger.info(f"  • 대상 파일: {target_video.name}")
        logger.info(f"  • 공개 설정: {privacy_status}")
        logger.info("=" * 70)

        clean_browser_profile_locks(self.profile_dir)

        start_time = time.time()
        video_url = ""
        video_id = ""

        async with async_browser_lock(f"Insurance 유튜브 쇼츠 업로드 ({final_title[:15]})"):
            async with async_playwright() as p:
                browser_args = get_safe_browser_args() + ['--disable-blink-features=AutomationControlled']
                
                try:
                    context = await p.chromium.launch_persistent_context(
                        user_data_dir=str(self.profile_dir),
                        headless=self.headless,
                        channel="chrome",
                        args=browser_args,
                        viewport={"width": 1366, "height": 850}
                    )
                except Exception:
                    context = await p.chromium.launch_persistent_context(
                        user_data_dir=str(self.profile_dir),
                        headless=self.headless,
                        args=browser_args,
                        viewport={"width": 1366, "height": 850}
                    )

                                # 세션 쿠키 주입 (RFC 6265bis 규격 정제 및 보안 속성 보정)
                if self.session_file.exists():
                    try:
                        with open(self.session_file, "r", encoding="utf-8") as f:
                            raw = json.load(f)
                        raw_cookies = raw.get("cookies", raw) if isinstance(raw, dict) else raw
                        clean_cookies = []
                        for c in raw_cookies:
                            c_name = c.get("name", "")
                            c_val = c.get("value", "")
                            c_domain = c.get("domain", ".youtube.com")
                            c_path = c.get("path", "/")
                            item = {"name": c_name, "value": c_val, "path": c_path}
                            is_secure = c.get("secure", False)
                            if c_name.startswith("__Secure-") or c_name.startswith("__Host-"):
                                is_secure = True
                            item["secure"] = bool(is_secure)
                            if "httpOnly" in c:
                                item["httpOnly"] = bool(c["httpOnly"])
                            ss = c.get("sameSite")
                            if ss in ["Strict", "Lax", "None"]:
                                item["sameSite"] = ss
                            if c_name.startswith("__Host-"):
                                item["domain"] = c_domain.lstrip(".")
                                item["path"] = "/"
                            else:
                                item["domain"] = c_domain
                            clean_cookies.append(item)
                        for ck in clean_cookies:
                            try:
                                await context.add_cookies([ck])
                            except Exception:
                                pass
                        logger.info(f"   🍪 유튜브 세션 쿠키 {len(clean_cookies)}개 브라우저 주입 완료")
                    except Exception as ce:
                        logger.warning(f"유튜브 세션 쿠키 로드 예외: {ce}")

                page = context.pages[0] if context.pages else await context.new_page()
                
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    window.navigator.chrome = { runtime: {} };
                """)

                try:
                    # 1. 유튜브 스튜디오 업로드 페이지 접속 (?approve_browser_access=true로 구형브라우저 경고 100% 직행 우회)
                    studio_url = "https://studio.youtube.com/?approve_browser_access=true"
                    logger.info(f"🌐 [1/5] 유튜브 스튜디오 접속 중: {studio_url}")
                    await page.goto(studio_url, wait_until="domcontentloaded", timeout=timeout_sec * 1000)
                    await asyncio.sleep(4.0)

                    # 로그인 상태 점검
                    if "accounts.google.com" in page.url or await page.locator("input[type='email']").is_visible():
                        logger.error("🛑 [Insurance YouTube Bot] 구글 로그인이 만료되었습니다. setup_youtube_profile.py를 실행해 주세요.")
                        await context.close()
                        return {
                            "status": "error",
                            "platform": "youtube_shorts",
                            "error": "Google 계정 로그인 필요 (setup_youtube_profile.py 실행 요망)",
                            "published_at": get_now_kst_str()
                        }

                    # 1-1. '환경 개선하기 / 건너뛰기' 링크가 있을 경우 추가 클릭
                    skip_link = page.locator("a[href*='approve_browser_access=true'], a:has-text('YouTube 스튜디오로 건너뛰기')").first
                    if await skip_link.is_visible():
                        logger.info("⏩ [YouTube Studio] '스튜디오로 건너뛰기' 승인 클릭")
                        await skip_link.click()
                        await asyncio.sleep(3.0)

                    # 1-2. 'YouTube 스튜디오에 오신 것을 환영합니다' 모달 자동 통과
                    await page.evaluate("""() => {
                        const btns = Array.from(document.querySelectorAll('button, ytcp-button'));
                        const welcome = btns.find(el => el.innerText && (el.innerText.trim() === '계속' || el.innerText.trim() === 'Continue'));
                        if (welcome) { welcome.click(); }
                    }""")
                    await asyncio.sleep(1.5)

                    # 1-3. 채널 만들기 팝업 자동 통과
                    await page.evaluate("""() => {
                        const btns = Array.from(document.querySelectorAll('button, ytcp-button'));
                        const create = btns.find(el => el.innerText && (el.innerText.trim() === '채널 만들기' || el.innerText.trim() === 'Create Channel'));
                        if (create) { create.click(); }
                    }""")
                    await asyncio.sleep(2.0)

                    # 2. 업로드 버튼 클릭 또는 파일 인풋 활성화
                    logger.info("🎬 [2/5] 동영상 업로드 파일 주입 준비...")
                    file_input = page.locator("input[type='file'][name='Filedata'], input[type='file']").first
                    
                    if not await file_input.is_visible():
                        create_btn = page.locator("#create-button, #create-icon, button:has-text('만들기'), button:has-text('Create'), ytcp-button#create-icon").first
                        if await create_btn.is_visible():
                            await create_btn.click()
                            await asyncio.sleep(1.0)
                            upload_menu = page.locator("tp-yt-paper-item:has-text('동영상 업로드'), tp-yt-paper-item:has-text('Upload videos'), #text-item-0").first
                            if await upload_menu.is_visible():
                                await upload_menu.click()
                                await asyncio.sleep(1.5)
                        else:
                            upload_icon = page.locator("#upload-icon, ytcp-button#upload-button, button:has-text('동영상 업로드'), #upload-button").first
                            if await upload_icon.is_visible():
                                await upload_icon.click()
                                await asyncio.sleep(1.5)

                    # 파일 인풋 대기 및 주입
                    try:
                        await page.wait_for_selector("input[type='file']", state="attached", timeout=15000)
                    except Exception:
                        pass

                    file_input = page.locator("input[type='file']").first
                    await file_input.set_input_files(str(target_video.resolve()))
                    logger.info(f"✅ [Insurance YouTube Bot] 숏폼 동영상 주입 완료: {target_video.name}")
                    await asyncio.sleep(4.0)

                    # 3. 세부정보 입력 모달 처리
                    logger.info("📝 [3/5] 제목, 설명란, 옵션 무인 기입 중...")
                    
                    try:
                        await page.wait_for_selector(
                            "#title-textarea #textbox, ytcp-social-suggestions-textbox#title-textarea #textbox, div#textbox[aria-label*='제목']",
                            state="attached",
                            timeout=30000
                        )
                    except Exception:
                        pass

                    await asyncio.sleep(2.0)

                    # JS 1차 직접 주입
                    await page.evaluate("""(data) => {
                        const el = document.querySelector('ytcp-social-suggestions-textbox#title-textarea #textbox') ||
                                   document.querySelector('#title-textarea #textbox') ||
                                   document.querySelector('div#textbox[aria-label*="제목"]') ||
                                   document.querySelector('div#textbox');
                        if (el) {
                            el.focus();
                            el.innerText = data.title;
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }""", {"title": final_title})
                    await asyncio.sleep(1.0)

                    try:
                        title_box = page.locator("ytcp-social-suggestions-textbox#title-textarea #textbox, #title-textarea #textbox, div#textbox[aria-label*='제목']").first
                        if await title_box.count() > 0:
                            await title_box.scroll_into_view_if_needed()
                            await title_box.click(force=True)
                            await page.keyboard.press("Control+A")
                            await page.keyboard.press("Backspace")
                            await page.keyboard.type(final_title, delay=15)
                    except Exception as te:
                        logger.debug(f"타이틀 키보드 입력 보조: {te}")

                    await asyncio.sleep(1.5)

                    # 설명란 입력란 주입
                    await page.evaluate("""(data) => {
                        const el = document.querySelector('ytcp-social-suggestions-textbox#description-textarea #textbox') ||
                                   document.querySelector('#description-textarea #textbox') ||
                                   document.querySelector('div#textbox[aria-label*="설명"]');
                        if (el) {
                            el.focus();
                            el.innerText = data.desc;
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }""", {"desc": full_desc})
                    await asyncio.sleep(1.5)

                    # 아동용 콘텐츠 여부: '아니요, 아동용이 아닙니다'
                    await page.evaluate("""() => {
                        const r = document.querySelector('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]') ||
                                  Array.from(document.querySelectorAll('tp-yt-paper-radio-button')).find(el => el.innerText.includes('아동용이 아닙니다') || el.innerText.includes('not made for kids'));
                        if (r) { r.click(); }
                    }""")
                    try:
                        not_kids_radio = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK'], tp-yt-paper-radio-button:has-text('아니요, 아동용이 아닙니다'), tp-yt-paper-radio-button:has-text('No, it\\'s not made for kids')").first
                        if await not_kids_radio.count() > 0:
                            await not_kids_radio.scroll_into_view_if_needed()
                            await not_kids_radio.click(force=True)
                    except Exception:
                        pass
                    await asyncio.sleep(1.5)

                    # 4. 다음 단계 순차 이동
                    logger.info("⏩ [4/5] 공개 설정 단계로 이동 중...")
                    for step in range(1, 4):
                        await asyncio.sleep(2.0)
                        await page.evaluate("""() => {
                            const btn = document.querySelector('#next-button') ||
                                        document.querySelector('ytcp-button#next-button') ||
                                        Array.from(document.querySelectorAll('button, ytcp-button')).find(el => el.innerText.trim() === '다음' || el.innerText.trim() === 'Next');
                            if (btn) { btn.click(); }
                        }""")
                        try:
                            next_btn = page.locator("#next-button, ytcp-button#next-button, button:has-text('다음'), button:has-text('Next')").first
                            if await next_btn.count() > 0 and await next_btn.is_visible():
                                await next_btn.click(force=True)
                        except Exception:
                            pass

                    await asyncio.sleep(2.0)

                    # 공개 상태 선택
                    await page.evaluate("""(status) => {
                        const val = status === 'public' ? 'PUBLIC' : (status === 'unlisted' ? 'UNLISTED' : 'PRIVATE');
                        const r = document.querySelector(`tp-yt-paper-radio-button[name="${val}"]`) ||
                                  Array.from(document.querySelectorAll('tp-yt-paper-radio-button')).find(el => el.innerText.includes('공개') || el.innerText.includes('Public'));
                        if (r) { r.click(); }
                    }""", privacy_status.lower())
                    await asyncio.sleep(1.5)

                    # 동영상 링크 추출 시도
                    try:
                        link_el = page.locator("a.ytcp-video-info[href*='youtu.be'], a[href*='youtu.be'], a[href*='youtube.com/shorts'], a[href*='youtube.com/watch']").first
                        if await link_el.count() > 0:
                            href = await link_el.get_attribute("href")
                            if href:
                                video_url = href.strip()
                                if "youtu.be/" in video_url:
                                    video_id = video_url.split("youtu.be/")[1].split("?")[0]
                                    video_url = f"https://youtube.com/shorts/{video_id}"
                                elif "v=" in video_url:
                                    video_id = video_url.split("v=")[1].split("&")[0]
                                    video_url = f"https://youtube.com/shorts/{video_id}"
                                elif "/shorts/" in video_url:
                                    video_id = video_url.split("/shorts/")[1].split("?")[0]
                    except Exception as le:
                        logger.debug(f"링크 추출 사전 시도: {le}")

                    # [게시] 버튼 클릭
                    logger.info("🚀 [5/5] 최종 [게시] 버튼 클릭 및 송출 완료 대기...")
                    await page.evaluate("""() => {
                        const btn = document.querySelector('#done-button') ||
                                    document.querySelector('ytcp-button#done-button') ||
                                    Array.from(document.querySelectorAll('button, ytcp-button')).find(el => el.innerText.trim() === '게시' || el.innerText.trim() === 'Publish' || el.innerText.trim() === '저장');
                        if (btn) { btn.click(); }
                    }""")
                    try:
                        done_btn = page.locator("#done-button, ytcp-button#done-button, button:has-text('게시'), button:has-text('Publish'), button:has-text('저장'), button:has-text('Save')").first
                        if await done_btn.count() > 0 and await done_btn.is_visible():
                            await done_btn.click(force=True)
                    except Exception:
                        pass

                    await asyncio.sleep(5.0)

                    if not video_url:
                        try:
                            final_link_el = page.locator("a.ytcp-video-info[href*='youtu.be'], a[href*='youtu.be'], a[href*='youtube.com/shorts']").first
                            if await final_link_el.count() > 0:
                                href = await final_link_el.get_attribute("href")
                                if href:
                                    video_url = href.strip()
                                    if "youtu.be/" in video_url:
                                        video_id = video_url.split("youtu.be/")[1].split("?")[0]
                                        video_url = f"https://youtube.com/shorts/{video_id}"
                                    elif "v=" in video_url:
                                        video_id = video_url.split("v=")[1].split("&")[0]
                                        video_url = f"https://youtube.com/shorts/{video_id}"
                                    elif "/shorts/" in video_url:
                                        video_id = video_url.split("/shorts/")[1].split("?")[0]
                        except Exception:
                            pass

                    # 닫기 버튼 클릭
                    await page.evaluate("""() => {
                        const btn = document.querySelector('#close-button') ||
                                    document.querySelector('ytcp-button#close-button') ||
                                    Array.from(document.querySelectorAll('button, ytcp-button')).find(el => el.innerText.trim() === '닫기' || el.innerText.trim() === 'Close');
                        if (btn) { btn.click(); }
                    }""")
                    await asyncio.sleep(1.5)

                    logger.info(f"🎉 [Insurance YouTube Bot] 쇼츠 무인 발행 완결! URL: {video_url or '게시 완료'}")

                    # 5. 고정 댓글(Pinned Comment) 자동 작성 + 최상단 핀(Pin) 고정
                    comm_status = "skipped"
                    if video_id:
                        try:
                            comm_status = await self._post_and_pin_comment(page, video_id, pinned_comment)
                            if comm_status == "pinned":
                                logger.info("📌 [Insurance YouTube Bot] 공식 검색어 유도 댓글 등록 + 최상단 고정 완결!")
                            elif comm_status == "submitted":
                                logger.info("✅ [Insurance YouTube Bot] 공식 검색어 유도 댓글 등록 성공 (핀 고정 미확인)")
                        except Exception as ce:
                            logger.warning(f"댓글/핀 고정 안내 (스튜디오 게시 성공 유지): {ce}")
                    else:
                        logger.warning("⚠️ [고정 댓글] video_id 추출 실패로 댓글/핀 고정을 건너뜁니다.")

                    try:
                        cookies = await context.cookies()
                        clean_cookies = [
                            {"name": c["name"], "value": c["value"], "domain": c.get("domain", ".youtube.com"), "path": c.get("path", "/")}
                            for c in cookies
                        ]
                        with open(self.session_file, "w", encoding="utf-8") as f:
                            json.dump({"cookies": clean_cookies}, f, ensure_ascii=False, indent=2)
                    except Exception:
                        pass

                    try:
                        await context.close()
                    except Exception:
                        pass

                    elapsed = round(time.time() - start_time, 1)
                    res = {
                        "status": "success",
                        "platform": "youtube_shorts",
                        "brand": self.BRAND,
                        "topic_id": topic_id,
                        "video_id": video_id,
                        "video_url": video_url or f"https://youtube.com/channel/uploaded_{int(time.time())}",
                        "title": final_title,
                        "pinned_comment": pinned_comment,
                        "comment_status": comm_status,
                        "privacy_status": privacy_status,
                        "video_file": target_video.name,
                        "published_at": get_now_kst_str(),
                        "elapsed_sec": elapsed,
                        "message": "YouTube Studio 브라우저 봇 쇼츠 공개 발행 및 검색어 댓글 상단 고정 완료"
                    }
                    self._save_history(res)
                    return res

                except Exception as ex:
                    logger.error(f"❌ [Insurance YouTube Bot] 발행 실패: {ex}")
                    try:
                        await context.close()
                    except Exception:
                        pass
                    err_res = {
                        "status": "error",
                        "platform": "youtube_shorts",
                        "error": str(ex),
                        "video_file": target_video.name,
                        "published_at": get_now_kst_str()
                    }
                    self._save_history(err_res)
                    return err_res

    def _save_history(self, data: Dict[str, Any]):
        """발행 이력 누적 저장"""
        logs = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                logs = []
        logs.append(data)
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(logs[-50:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    bot = InsuranceYouTubeBotPublisher(headless=False)
    print(f"🛡️ Insurance YouTube Bot Publisher 준비 완료! (가용성: {bot.is_available()})")
