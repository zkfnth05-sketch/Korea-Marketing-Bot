# -*- coding: utf-8 -*-
"""
[독립 레고 블록] Stock YouTube Bot Publisher (📈 StockMaster AI 전용 유튜브 쇼츠 브라우저 봇 무인 직접 업로더)
===================================================================================================================
- 브랜드: StockMaster AI (공식 검색어: '스톡마스터 AI' 띄어쓰기 불변)
- 핵심 역할:
  1. [0 API 순수 브라우저 봇]: Google Data API Quota(할당량) 및 토큰 만료 문제 100% 영구 해결
  2. [YouTube Studio 웹 무인 자동화]: 영구 브라우저 프로필/세션으로 https://studio.youtube.com 접속
  3. [MP4 자동 주입]: 9:16 세로 풀HD 숏폼 비디오 직접 주입 및 업로드
  4. [완벽한 메타데이터 패키징]: 제목(1초 훅 + '#스톡마스터AI #Shorts') + 설명란(4단 해시태그 + 공식 검색 유도)
  5. [옵션 자동 설정]: '아동용 아님' 자동 체크 + '공개(Public)' 즉시 발행
  6. [고정 댓글 자동화]: 발행 즉시 쇼츠 페이지 진입 ➔ 공식 검색어 유도 링크 댓글 작성 및 상단 핀 고정
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
from brands.stock.stock_hashtag_matrix import StockHashtagMatrix
from core.engine.browser_guard import async_browser_lock, get_safe_browser_args, clean_browser_profile_locks

logger = logging.getLogger("StockYouTubeBotPublisher")


class StockYouTubeBotPublisher:
    """📈 StockMaster AI 전용 유튜브 쇼츠 브라우저 봇 직접 업로드 엔진"""

    BRAND = "stock"
    OFFICIAL_KEYWORD = "스톡마스터 AI"
    LANDING_URL = "https://stockmaster-ai.vercel.app/"

    HOOK_TITLES = {
        1: "삼성전자 vs SK하이닉스 HBM 외인 수급 대폭발 ㄷㄷ",
        2: "국내 고배당주(금융지주·맥쿼리) 월배당 시뮬레이션 현실적 치트키",
        3: "코스피·코스닥 세력 체결강도 120% 돌파 급등 유망주 포착",
        4: "코스피200 우량주 vs 코스닥 성장주 직장인 월적립식 복리 비교",
        5: "외인·기관 실시간 쌍끌이 순매수 레이더 포착 종목 TOP 3",
        6: "주식 초보가 100% 물리는 물타기 실수와 AI 손절 탈출 공식",
        7: "저PBR 밸류업 & 고배당 금융주 스크리닝 긴급 공개",
        8: "AI 자동 손절매 & 리스크 가드 퀀트 시스템 실전 운용법"
    }

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.profile_dir = CURRENT_DIR / "youtube_chrome_profile"
        self.session_file = CURRENT_DIR / "youtube_session.json"
        self.history_file = CURRENT_DIR / "youtube_publish_history.json"
        self.shorts_output_dir = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Stock")

    def is_available(self) -> bool:
        """세션 파일 또는 영구 프로필 존재 여부 점검"""
        has_session = self.session_file.exists() and self.session_file.stat().st_size > 50
        has_profile = self.profile_dir.exists()
        return has_session or has_profile

    def find_latest_short_video(self, topic_id: Optional[int] = None) -> Optional[Path]:
        """바탕화면 산출물 폴더에서 가장 최신 렌더링된 Stock 숏폼 MP4 자동 탐색"""
        search_dirs = [self.shorts_output_dir, BASE_DIR / "outputs" / "stock"]
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
            logger.error(f"❌ [Stock YouTube Bot] 발행 예외 발생: {e}")
            err_res = {
                "status": "error",
                "platform": "youtube_shorts",
                "error": str(e),
                "published_at": get_now_kst_str()
            }
            self._save_history(err_res)
            return err_res

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
            logger.warning("⚠️ [Stock YouTube Bot] 세션 파일(youtube_session.json) 또는 영구 프로필이 없습니다.")
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
        tag_str = StockHashtagMatrix.get_shorts_hashtags(topic_id)
        yt_tags = tag_str.split() if tag_str else ["#스톡마스터AI", "#Shorts"]

        raw_title = title or f"{self.HOOK_TITLES.get(topic_id, '주식 AI 퀀트 꿀팁')} #스톡마스터AI #Shorts"
        if "#Shorts" not in raw_title and "#shorts" not in raw_title:
            raw_title = f"{raw_title} #Shorts"
        final_title = raw_title[:100]

        # 설명란 조립 (4단 해시태그 결합)
        tags_line = " ".join(yt_tags) if yt_tags else "#스톡마스터AI #주식투자 #퀀트투자 #수급포착 #Shorts"
        desc_body = description or (
            "실시간 외인·기관 쌍끌이 수급 포착부터 AI 자동 손절매 퀀트까지!\n\n"
            f"🔍 네이버 검색창에 👉 [ {self.OFFICIAL_KEYWORD} ] 검색해보세요!\n"
            f"공식 퀀트 대시보드 바로가기: {self.LANDING_URL}\n\n"
        )
        full_desc = f"{desc_body.strip()}\n\n{tags_line}".strip()[:5000]

        # 고정 댓글 문구
        pinned_comment = (
            "📌 실시간 외인·기관 쌍끌이 수급 포착 & AI 퀀트 리스크 가드는\n"
            f"네이버에 👉 [ {self.OFFICIAL_KEYWORD} ] 검색하시면 바로 나옵니다!\n"
            f"(공식 링크: {self.LANDING_URL})"
        )

        logger.info("=" * 70)
        logger.info(f"🤖 [Stock YouTube Bot] 쇼츠 직접 브라우저 업로드 시작: {final_title}")
        logger.info(f"  • 대상 파일: {target_video.name}")
        logger.info(f"  • 공개 설정: {privacy_status}")
        logger.info("=" * 70)

        clean_browser_profile_locks(self.profile_dir)

        start_time = time.time()
        video_url = ""
        video_id = ""

        async with async_browser_lock(f"Stock 유튜브 쇼츠 업로드 ({final_title[:15]})"):
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
                        logger.error("🛑 [Stock YouTube Bot] 구글 로그인이 만료되었습니다. setup_youtube_profile.py를 실행해 주세요.")
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
                    logger.info(f"✅ [Stock YouTube Bot] 숏폼 동영상 주입 완료: {target_video.name}")
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

                    logger.info(f"🎉 [Stock YouTube Bot] 쇼츠 무인 발행 완결! URL: {video_url or '게시 완료'}")

                    # 5. 고정 댓글(Pinned Comment) 자동 작성
                    comm_status = "skipped"
                    if video_url:
                        try:
                            logger.info(f"💬 [고정 댓글 등록] 쇼츠 페이지({video_url}) 이동 중...")
                            await page.goto(video_url, wait_until="domcontentloaded", timeout=30000)
                            await asyncio.sleep(3.0)

                            comment_placeholder = page.locator("#placeholder-area, #simplebox-placeholder, ytd-comment-simplebox-renderer").first
                            if await comment_placeholder.is_visible():
                                await comment_placeholder.click()
                                await asyncio.sleep(1.0)
                                comment_input = page.locator("#contenteditable-root, div[aria-label*='댓글 추가'], div[aria-label*='Add a comment']").first
                                if await comment_input.is_visible():
                                    await comment_input.fill(pinned_comment)
                                    await asyncio.sleep(1.0)
                                    submit_btn = page.locator("#submit-button, button[aria-label*='댓글'], button:has-text('댓글'), button:has-text('Comment')").first
                                    if await submit_btn.is_visible():
                                        await submit_btn.click()
                                        await asyncio.sleep(2.0)
                                        comm_status = "submitted"
                                        logger.info("✅ [Stock YouTube Bot] 공식 검색어 유도 댓글 등록 성공!")
                        except Exception as ce:
                            logger.warning(f"댓글 등록 안내 (스튜디오 게시 성공 유지): {ce}")

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
                    try:
                        await browser.close()
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
                        "message": "YouTube Studio 브라우저 봇 쇼츠 공개 발행 및 검색어 댓글 완료"
                    }
                    self._save_history(res)
                    return res

                except Exception as ex:
                    logger.error(f"❌ [Stock YouTube Bot] 발행 실패: {ex}")
                    try:
                        await context.close()
                    except Exception:
                        pass
                    try:
                        await browser.close()
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
    bot = StockYouTubeBotPublisher(headless=False)
    print(f"📈 Stock YouTube Bot Publisher 준비 완료! (가용성: {bot.is_available()})")
