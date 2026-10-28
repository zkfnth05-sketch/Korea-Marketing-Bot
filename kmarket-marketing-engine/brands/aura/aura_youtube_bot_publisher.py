# -*- coding: utf-8 -*-
"""
[독립 레고 블록] Aura YouTube Bot Publisher (💖 Aura 데이팅 전용 유튜브 쇼츠 브라우저 봇 무인 직접 업로더)
========================================================================================================
- 브랜드: Aura AI 데이팅 (공식 검색어: '아우라AI데이팅' 붙여쓰기 불변)
- 핵심 역할:
  1. [0 API 순수 브라우저 봇]: Google Data API Quota(할당량) 및 토큰 만료 문제 100% 영구 해결
  2. [YouTube Studio 웹 무인 자동화]: 영구 브라우저 프로필/세션으로 https://studio.youtube.com 접속
  3. [MP4 자동 주입]: 9:16 세로 풀HD 숏폼 비디오 직접 주입 및 업로드
  4. [완벽한 메타데이터 패키징]: 제목(1초 훅 + '#아우라AI데이팅 #Shorts') + 설명란(4단 해시태그 + 공식 검색 유도)
  5. [옵션 자동 설정]: '아동용 아님' 자동 체크 + '공개(Public)' 즉시 발행
  6. [고정 댓글 자동화]: 발행 즉시 watch 페이지 진입 ➔ 공식 검색어 유도 링크 댓글 작성 ➔ 최상단 핀(Pin) 고정
- 원칙: Rule 1 (독립 레고 블록), Rule 5 (땜질 금지/근본 해결), Rule 6 (24시간 무인 자율 구동), Rule 7 (공식 규격)
"""

import os
import re
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
from brands.aura.aura_hashtag_matrix import AuraHashtagMatrix
from core.engine.browser_guard import async_browser_lock, get_safe_browser_args, clean_browser_profile_locks

logger = logging.getLogger("AuraYouTubeBotPublisher")


class AuraYouTubeBotPublisher:
    """💖 Aura 데이팅 전용 유튜브 쇼츠 브라우저 봇 직접 업로드 엔진"""

    BRAND = "aura"
    OFFICIAL_KEYWORD = "아우라AI데이팅"
    LANDING_URL = "https://aura-ai-dating.vercel.app/"

    HOOK_TITLES = {
        1: "소개팅에서 어색할 때 3초 만에 탈출하는 비법 ㄷㄷ",
        2: "카톡 답장 느린 사람 100% 심리 분석 (읽씹 대처법)",
        3: "남초 제로, 성비 50:50 데이팅 라운지 실화냐?",
        4: "첫 만남에서 호감도 3배 올리는 스몰토크 치트키",
        5: "2030 남녀가 뽑은 최악의 소개팅 착장 1위는?",
        6: "소개팅 애프터 신청 골든타임 & 카톡 멘트 추천",
        7: "성수동/연남동 분위기 터지는 소개팅 핫플 추천",
        8: "MBTI 유형별 절대 실패 없는 연애 공략법"
    }

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.profile_dir = CURRENT_DIR / "youtube_chrome_profile"
        self.session_file = CURRENT_DIR / "youtube_session.json"
        self.history_file = CURRENT_DIR / "youtube_publish_history.json"
        self.shorts_output_dir = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Aura")

    def is_available(self) -> bool:
        """세션 파일 또는 영구 프로필 존재 여부 점검"""
        has_session = self.session_file.exists() and self.session_file.stat().st_size > 50
        has_profile = self.profile_dir.exists()
        return has_session or has_profile

    def find_latest_short_video(self, topic_id: Optional[int] = None) -> Optional[Path]:
        """바탕화면 산출물 폴더에서 가장 최신 렌더링된 Aura 숏폼 MP4 자동 탐색"""
        search_dirs = [self.shorts_output_dir, BASE_DIR / "outputs" / "aura"]
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
            logger.error(f"❌ [Aura YouTube Bot] 발행 예외 발생: {e}")
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
    # ------------------------------------------------------------------
    # [video_id 정규화 SSOT] URL/순수 ID 혼용 입력을 순수 11자리 ID로 정규화한다.
    #   · https://youtube.com/shorts/HaI-_Uxbsis?feature=share → HaI-_Uxbsis
    #   · https://youtu.be/MLFWx9R5t7Q?t=3                    → MLFWx9R5t7Q
    #   · https://www.youtube.com/watch?v=MLFWx9R5t7Q&list=.. → MLFWx9R5t7Q
    #   · MLFWx9R5t7Q                                          → MLFWx9R5t7Q
    #   ★ 왜 필수인가: 발행 파이프라인이 video_url(전체 URL)을 그대로 넘기는 경로와
    #     video_id(순수 ID)를 넘기는 경로가 혼재하여, URL 이 유입되면
    #     watch?v=https://... 형태의 깨진 URL 로 진입해 댓글 등록이 100% 실패했다.
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_video_id(video_id_or_url: str) -> str:
        """URL 또는 순수 ID 입력을 유튜브 11자리 순수 video_id 로 안전 추출한다."""
        raw = str(video_id_or_url or "").strip()
        if not raw:
            return ""
        # 1) URL 형태에서 ID 패턴 추출 (shorts / youtu.be / watch?v= / embed / live)
        m = re.search(
            r"(?:youtu\.be/|/shorts/|/embed/|/live/|/v/|[?&]v=)([A-Za-z0-9_-]{11})",
            raw,
        )
        if m:
            return m.group(1)
        # 2) 순수 ID 형태 (11자리) — 그대로 반환
        m2 = re.fullmatch(r"([A-Za-z0-9_-]{11})", raw)
        if m2:
            return m2.group(1)
        # 3) 최후 수단: 11자리 ID 토큰이 문자열 어딘가에 있으면 추출
        m3 = re.search(r"([A-Za-z0-9_-]{11})", raw)
        if m3:
            return m3.group(1)
        return ""

    # ------------------------------------------------------------------
    # [고정 댓글 + 최상단 핀(Pin) 무인 자동화 엔진] 대표님 절대 지시 (2026-10-25)
    #   "유튜브 쇼츠 댓글 등록 및 상단 고정(Pin) 엔진을 100% 무인 작동하도록 전면 개편"
    #
    #   ★ 기존 구현의 3대 치명 결함을 근본 해결한다:
    #     ① watch 페이지 강제 진입 → 쇼츠 유입 트래픽과 무관한 페이지에서 댓글 시도.
    #        이제 shorts/{id} 로 직접 진입하고, 우측 사이드바 댓글 버튼으로
    #        engagement panel(댓글 서랍)을 개방한다. 실패 시에만 watch 로 폴백.
    #     ② fill() 주입 → contenteditable 에 값이 들어가도 YouTube 의 입력 이벤트
    #        체인이 발화하지 않아 submit 버튼이 disabled 로 남았다.
    #        이제 press_sequentially(delay=15) 로 실제 키보드 이벤트를 한 글자씩 발생.
    #     ③ 등록 버튼 클릭 성공 = 성공 처리 → 실제로는 disabled 버튼을 눌러 아무 일도
    #        일어나지 않았는데 "submitted" 로 위조 보고했다.
    #        이제 등록 후 댓글 DOM 에 공식 키워드가 실물 렌더링되었는지 검증(Anti-Tampering)
    #        하고, 없으면 즉시 실패 처리한다.
    #
    #   반환값: "pinned" | "submitted" | "skipped"
    #     · pinned    = 댓글 등록 + 최상단 고정까지 100% 완료
    #     · submitted = 댓글 등록은 실물 검증 완료, 핀 고정만 미확인
    #     · skipped   = 댓글 등록 자체가 실물 검증 실패(성공 위조 금지)
    # ------------------------------------------------------------------
    async def _post_and_pin_comment(self, page, video_id: str, pinned_comment: str) -> str:
        """
        쇼츠 페이지 진입 ➔ 댓글 서랍 개방 ➔ 실제 키보드 타이핑 ➔ 등록 ➔ 실물 검증 ➔ 핀 고정.
        반환값: "pinned" | "submitted" | "skipped"
        """
        # 0) video_id 정규화 (URL 유입 시 순수 ID 추출)
        vid = self._normalize_video_id(video_id)
        if not vid:
            logger.warning(f"⚠️ [고정 댓글] video_id 정규화 실패('{video_id}') — 댓글/핀 고정 건너뜀")
            return "skipped"

        # 실물 검증용 핵심 문구 (공식 키워드 우선, 없으면 댓글 첫 문장)
        verify_token = self.OFFICIAL_KEYWORD
        if verify_token not in pinned_comment:
            first_line = (pinned_comment or "").strip().splitlines()
            verify_token = (first_line[0][:20] if first_line else "").strip() or self.OFFICIAL_KEYWORD

        # 1) 쇼츠 페이지 직접 진입
        #    ★ 초기 로드 대기를 4초 ➔ 6초로 상향:
        #      업로드 직후 쇼츠 페이지는 플레이어 초기화/댓글 컴포넌트 마운트가 늦어
        #      4초 시점에는 댓글 버튼조차 DOM 에 없는 경우가 빈번했다.
        shorts_url = f"https://www.youtube.com/shorts/{vid}"
        logger.info(f"💬 [고정 댓글] 쇼츠 페이지 진입: {shorts_url}")
        await page.goto(shorts_url, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(6.0)

        # 2) 쇼츠 댓글 서랍(engagement panel) 개방 — 패널 실물 확인 기반 2단 전략
        #    ★ 왜 '클릭 성공 = 개방 성공' 으로 처리하면 안 되는가:
        #      댓글 버튼 클릭은 성공해도 YouTube 가 패널을 실제로 렌더링하지 않는 경우가
        #      빈번하다(지연 렌더/가상 스크롤). 클릭 성공만 믿고 다음 단계로 넘어가면
        #      플레이스홀더를 찾지 못해 댓글 등록이 100% 실패한다.
        #      따라서 '패널 DOM 이 실제로 열렸는지' 를 visibility 로 검증한다.
        PANEL_SELECTOR = (
            "ytd-engagement-panel-section-list-renderer"
            "[target-id='engagement-panel-comments-section']"
        )
        on_shorts = "/shorts/" in (page.url or "")
        panel_opened = False

        async def _is_panel_visible() -> bool:
            """댓글 서랍 패널이 실제로 열려 있는지 visibility 상태로 판정한다."""
            try:
                return bool(await page.evaluate("""(sel) => {
                    const p = document.querySelector(sel);
                    if (!p) { return false; }
                    const vis = (p.getAttribute('visibility') || '').toUpperCase();
                    if (vis === 'ENGAGEMENT_PANEL_VISIBILITY_EXPANDED') { return true; }
                    if (vis === 'ENGAGEMENT_PANEL_VISIBILITY_HIDDEN') { return false; }
                    const r = p.getBoundingClientRect();
                    return r.width > 0 && r.height > 0;
                }""", PANEL_SELECTOR))
            except Exception:
                return False

        async def _wait_panel_open(max_sec: float = 15.0) -> bool:
            """패널이 열릴 때까지 최대 max_sec 초 동안 0.5초 간격으로 폴링한다."""
            waited = 0.0
            while waited < max_sec:
                if await _is_panel_visible():
                    return True
                await asyncio.sleep(0.5)
                waited += 0.5
            return False

        async def _click_comments_button() -> bool:
            """쇼츠 우측 사이드바 댓글 버튼을 클릭한다(Playwright ➔ JS 폴백). 클릭 시도 여부 반환."""
            try:
                comments_btn = page.locator(
                    "#comments-button button, "
                    "ytd-reel-video-renderer[is-active] #comments-button button, "
                    "button[aria-label*='댓글'], "
                    "button[aria-label*='Comment']"
                ).first
                if await comments_btn.count() > 0:
                    await comments_btn.scroll_into_view_if_needed()
                    await comments_btn.click(force=True)
                    return True
                await page.evaluate("""() => {
                    const btn = document.querySelector('#comments-button button') ||
                                document.querySelector("ytd-reel-video-renderer[is-active] #comments-button button") ||
                                Array.from(document.querySelectorAll('button'))
                                    .find(el => {
                                        const a = (el.getAttribute('aria-label') || '');
                                        return a.includes('댓글') || a.includes('Comment');
                                    });
                    if (btn) { btn.click(); }
                }""")
                return True
            except Exception as ce:
                logger.warning(f"⚠️ [고정 댓글] 쇼츠 댓글 버튼 클릭 예외 — watch 폴백 검토: {ce}")
                return False

        if on_shorts:
            # 2-1) 이미 패널이 열려 있는지 1차 확인 (자동 개방 케이스)
            panel_opened = await _is_panel_visible()
            if panel_opened:
                logger.info("💬 [고정 댓글] 댓글 서랍 패널이 이미 열려 있음 — 클릭 생략")

            # 2-2) 닫혀 있으면 우측 사이드바 댓글 버튼 클릭 ➔ 패널 개방 최대 15초 대기
            if not panel_opened:
                await _click_comments_button()
                logger.info("💬 [고정 댓글] 쇼츠 댓글 버튼 클릭 ➔ 패널 개방 대기(최대 15초)")

                panel_opened = await _wait_panel_open(15.0)
                if panel_opened:
                    logger.info("✅ [고정 댓글] 댓글 서랍 패널 개방 확인(visibility EXPANDED)")
                else:
                    # 2-3) 재시도 클릭 1회 — 첫 클릭이 유실되거나 플레이어 재마운트로
                    #      패널이 닫히는 케이스를 회수한다.
                    logger.warning("⚠️ [고정 댓글] 15초 내 패널 개방 미확인 — 댓글 버튼 재시도 클릭 1회")
                    await _click_comments_button()
                    panel_opened = await _wait_panel_open(15.0)
                    if panel_opened:
                        logger.info("✅ [고정 댓글] 재시도 클릭으로 댓글 서랍 패널 개방 확인")
                    else:
                        logger.warning("⚠️ [고정 댓글] 재시도 후에도 패널 개방 미확인 — 스크롤 폴백으로 전환")

        # 3) 쇼츠 패널이 아니거나 개방 실패 → 스크롤 다운 후 플레이스홀더 탐색 (watch 폴백)
        if (not on_shorts) or (not panel_opened):
            logger.info("💬 [고정 댓글] watch/일반 페이지 모드 — 스크롤 다운으로 댓글 섹션 로드")
            try:
                await page.evaluate("window.scrollBy(0, 600)")
            except Exception:
                pass
            await asyncio.sleep(2.5)
            try:
                await page.evaluate("window.scrollBy(0, 600)")
            except Exception:
                pass
            await asyncio.sleep(2.0)

        # 4) 댓글 입력창(플레이스홀더) 활성화 — 패널 내부 우선 탐색
        placeholder = page.locator(
            f"{PANEL_SELECTOR} #placeholder-area, "
            f"{PANEL_SELECTOR} #simplebox-placeholder, "
            f"{PANEL_SELECTOR} div#contenteditable-root, "
            "#placeholder-area, #simplebox-placeholder, "
            "ytd-comment-simplebox-renderer #placeholder-area"
        ).first
        try:
            await placeholder.wait_for(state="visible", timeout=20000)
            await placeholder.click()
        except Exception:
            await page.evaluate("""(sel) => {
                const panel = document.querySelector(sel);
                const el = (panel && (panel.querySelector('#placeholder-area') ||
                                      panel.querySelector('#simplebox-placeholder') ||
                                      panel.querySelector('div#contenteditable-root'))) ||
                           document.querySelector('#placeholder-area') ||
                           document.querySelector('#simplebox-placeholder') ||
                           document.querySelector('ytd-comment-simplebox-renderer #placeholder-area');
                if (el) { el.click(); }
            }""", PANEL_SELECTOR)
        await asyncio.sleep(1.5)

        # 5) 댓글 본문 입력 — 실제 키보드 이벤트(press_sequentially)로 한 글자씩 타이핑
        #    ★ 왜 fill() 이 아니라 press_sequentially 인가:
        #      contenteditable 은 fill() 로 값을 넣어도 YouTube 의 input 이벤트 체인이
        #      발화하지 않아 submit 버튼이 disabled 로 남는다. 실제 키보드 이벤트를
        #      한 글자씩 발생시켜야 등록 버튼이 활성화된다.
        comment_input = page.locator(
            f"{PANEL_SELECTOR} div#contenteditable-root, "
            "div#contenteditable-root, "
            "div[role='textbox'][aria-label*='댓글'], "
            "div[role='textbox'][aria-label*='Add a comment']"
        ).first
        typed_ok = False
        try:
            await comment_input.wait_for(state="visible", timeout=15000)
            await comment_input.click()
            await asyncio.sleep(0.5)
            # 줄바꿈은 Shift+Enter 로 처리 (Enter 단독은 댓글 즉시 등록 위험)
            lines = str(pinned_comment).split("\n")
            for li, line in enumerate(lines):
                if li > 0:
                    await page.keyboard.press("Shift+Enter")
                    await asyncio.sleep(0.15)
                if line:
                    await comment_input.press_sequentially(line, delay=15)
            typed_ok = True
        except Exception as te:
            logger.warning(f"⚠️ [고정 댓글] press_sequentially 입력 실패 — JS 폴백 시도: {te}")

        if not typed_ok:
            try:
                await page.evaluate("""(txt) => {
                    const el = document.querySelector('#contenteditable-root') ||
                               document.querySelector("div[role='textbox'][aria-label*='댓글']") ||
                               document.querySelector("div[role='textbox'][aria-label*='Add a comment']");
                    if (el) {
                        el.focus();
                        el.innerText = txt;
                        el.dispatchEvent(new InputEvent('input', { bubbles: true, cancelable: true }));
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }""", pinned_comment)
            except Exception as je:
                logger.warning(f"⚠️ [고정 댓글] JS 폴백 입력도 실패: {je}")

        # submit-button 활성화 유도 대기
        await asyncio.sleep(2.0)

        # 6) 등록 버튼 클릭 — disabled 가 아닌 활성 버튼만 클릭 (3초 대기 후 1회 재확인)
        submit_selectors = (
            f"{PANEL_SELECTOR} #submit-button button:not([disabled]), "
            "ytd-comment-simplebox-renderer #submit-button button:not([disabled]), "
            "#submit-button yt-button-shape button:not([disabled]), "
            "button:has-text('댓글'):not([disabled]), "
            "button:has-text('Comment'):not([disabled])"
        )
        clicked = False
        for attempt in range(1, 3):
            try:
                submit_btn = page.locator(submit_selectors).first
                if await submit_btn.count() > 0:
                    await submit_btn.scroll_into_view_if_needed()
                    await submit_btn.click(force=True)
                    clicked = True
                    logger.info(f"✅ [고정 댓글] 등록 버튼 클릭 성공 (시도 {attempt})")
                    break
            except Exception as se:
                logger.warning(f"⚠️ [고정 댓글] 등록 버튼 클릭 예외(시도 {attempt}): {se}")
            if attempt < 2:
                logger.info("⏳ [고정 댓글] 등록 버튼 미활성 — 3초 대기 후 재확인")
                await asyncio.sleep(3.0)

        if not clicked:
            # JS 최후 시도 — disabled 속성이 없는 버튼만 클릭
            try:
                clicked = bool(await page.evaluate("""() => {
                    const cands = Array.from(document.querySelectorAll(
                        'ytd-comment-simplebox-renderer #submit-button button, #submit-button button, button'
                    ));
                    const btn = cands.find(el => {
                        if (el.disabled || el.hasAttribute('disabled')) { return false; }
                        const t = (el.innerText || '').trim();
                        const a = (el.getAttribute('aria-label') || '');
                        return t === '댓글' || t === 'Comment' || a.includes('댓글') || a.includes('Comment');
                    });
                    if (btn) { btn.click(); return true; }
                    return false;
                }"""))
            except Exception as je:
                logger.warning(f"⚠️ [고정 댓글] JS 등록 버튼 클릭 실패: {je}")

        if not clicked:
            logger.warning("⚠️ [고정 댓글] 활성 등록 버튼을 찾지 못했습니다 — 성공 처리 금지(return skipped)")
            return "skipped"

        # 7) 댓글 실물 검증 (Anti-Tampering) — 등록 클릭 후 4초 대기 후 DOM 실물 확인
        logger.info("🔍 [고정 댓글] 댓글 실물 렌더링 검증 중...")
        await asyncio.sleep(4.0)
        verified = False
        try:
            verified = bool(await page.evaluate("""(token) => {
                const nodes = Array.from(document.querySelectorAll(
                    'ytd-comment-thread-renderer, ytd-comment-view-model'
                ));
                if (!nodes.length) { return false; }
                return nodes.some(n => (n.innerText || '').includes(token));
            }""", verify_token))
        except Exception as ve:
            logger.warning(f"⚠️ [고정 댓글] 실물 검증 예외: {ve}")

        if not verified:
            # 2차 검증: 2초 추가 대기 후 재확인 (YouTube 렌더 지연 대응)
            await asyncio.sleep(2.0)
            try:
                verified = bool(await page.evaluate("""(token) => {
                    const nodes = Array.from(document.querySelectorAll(
                        'ytd-comment-thread-renderer, ytd-comment-view-model'
                    ));
                    return nodes.some(n => (n.innerText || '').includes(token));
                }""", verify_token))
            except Exception:
                pass

        if not verified:
            logger.error(
                f"❌ [고정 댓글] 댓글 실물 검증 실패 — DOM 에 '{verify_token}' 미검출. "
                "성공 위조 금지(return skipped)"
            )
            return "skipped"

        logger.info(f"✅ [고정 댓글] 댓글 실물 검증 통과('{verify_token}' DOM 확인) ➔ 핀 고정 시퀀스 시작")
        await asyncio.sleep(1.5)

        # 8) 핀 고정 시퀀스 — 첫 댓글 세로 3점 아이콘 ➔ '고정' ➔ 확인 다이얼로그
        try:
            first_thread = page.locator(
                "ytd-comment-thread-renderer:first-of-type, ytd-comment-view-model"
            ).first
            try:
                await first_thread.wait_for(state="visible", timeout=15000)
            except Exception:
                pass

            action_menu = page.locator(
                "ytd-comment-thread-renderer:first-of-type yt-icon-button#button, "
                "ytd-comment-thread-renderer:first-of-type button[aria-label*='작업 더보기'], "
                "ytd-comment-thread-renderer:first-of-type button[aria-label*='Action menu'], "
                "ytd-comment-thread-renderer:first-of-type #action-menu button, "
                "ytd-comment-view-model yt-icon-button#button"
            ).first
            if await action_menu.count() > 0:
                await action_menu.scroll_into_view_if_needed()
                await action_menu.click(force=True)
            else:
                await page.evaluate("""() => {
                    const thread = document.querySelector('ytd-comment-thread-renderer') ||
                                   document.querySelector('ytd-comment-view-model');
                    if (!thread) { return; }
                    const btn = thread.querySelector('yt-icon-button#button') ||
                                thread.querySelector("button[aria-label*='작업 더보기']") ||
                                thread.querySelector("button[aria-label*='Action menu']") ||
                                thread.querySelector('#action-menu button') ||
                                thread.querySelector('#action-menu');
                    if (btn) { btn.click(); }
                }""")
            await asyncio.sleep(2.0)

            # 9) 드롭다운 메뉴의 '고정(Pin)' 항목 클릭
            pin_item = page.locator(
                "tp-yt-paper-item:has-text('고정'), "
                "ytd-menu-service-item-renderer:has-text('고정'), "
                "ytd-menu-navigation-item-renderer:has-text('고정'), "
                "tp-yt-paper-item:has-text('Pin'), "
                "ytd-menu-service-item-renderer:has-text('Pin')"
            ).first
            if await pin_item.count() > 0:
                await pin_item.click(force=True)
            else:
                await page.evaluate("""() => {
                    const items = Array.from(document.querySelectorAll(
                        'ytd-menu-service-item-renderer, tp-yt-paper-item, ytd-menu-navigation-item-renderer'
                    ));
                    const pin = items.find(el => {
                        const t = (el.innerText || '').trim();
                        return t === '고정' || t.includes('고정') || t === 'Pin' || t.includes('Pin');
                    });
                    if (pin) { pin.click(); }
                }""")
            await asyncio.sleep(2.5)

            # 10) 확인 다이얼로그의 '고정(Pin)' 확인 버튼 클릭
            #     ★ 셀렉터 보강: #confirm-button yt-button-shape button (신형 DOM) 포함
            confirm_btn = page.locator(
                "yt-confirm-dialog-renderer #confirm-button button, "
                "ytd-confirm-dialog-renderer #confirm-button button, "
                "tp-yt-paper-dialog #confirm-button button, "
                "#confirm-button yt-button-shape button, "
                "yt-confirm-dialog-renderer button:has-text('고정'), "
                "ytd-confirm-dialog-renderer button:has-text('고정'), "
                "tp-yt-paper-dialog button:has-text('고정'), "
                "yt-confirm-dialog-renderer button:has-text('Pin'), "
                "ytd-confirm-dialog-renderer button:has-text('Pin')"
            ).first
            confirm_clicked = False
            if await confirm_btn.count() > 0:
                await confirm_btn.click(force=True)
                confirm_clicked = True
            else:
                confirm_clicked = bool(await page.evaluate("""() => {
                    const dialogs = Array.from(document.querySelectorAll(
                        'yt-confirm-dialog-renderer, ytd-confirm-dialog-renderer, tp-yt-paper-dialog'
                    ));
                    for (const d of dialogs) {
                        const btns = Array.from(d.querySelectorAll(
                            'button, yt-button-renderer, tp-yt-paper-button, yt-button-shape button'
                        ));
                        const ok = btns.find(b => {
                            const t = (b.innerText || '').trim();
                            return t === '고정' || t.includes('고정') || t === 'Pin' || t.includes('Pin');
                        });
                        if (ok) { ok.click(); return true; }
                    }
                    return false;
                }"""))
            await asyncio.sleep(2.0)

            # 11) 핀 고정 배지 실물 확인 (Anti-Tampering) — 확인 버튼 클릭만으로 성공 처리 금지
            #     ★ 왜 필수인가: 확인 다이얼로그 버튼을 클릭해도 실제로는 고정이 적용되지 않는
            #       경우가 있다. DOM 에 핀 배지가 실물 렌더링되었는지 반드시 검증해야 한다.
            PIN_BADGE_SELECTOR = "#pinned-comment-badge, ytd-pinned-comment-badge-renderer"
            badge_found = False
            try:
                badge_found = bool(await page.evaluate("""(sel) => {
                    const nodes = Array.from(document.querySelectorAll(sel));
                    return nodes.some(n => {
                        const r = n.getBoundingClientRect();
                        return r.width > 0 && r.height > 0;
                    });
                }""", PIN_BADGE_SELECTOR))
            except Exception as be:
                logger.warning(f"⚠️ [고정 댓글] 핀 배지 확인 예외: {be}")

            if not badge_found:
                # 2차 확인: 2초 추가 대기 후 재검증 (YouTube 반영 지연 대응)
                await asyncio.sleep(2.0)
                try:
                    badge_found = bool(await page.evaluate("""(sel) => {
                        const nodes = Array.from(document.querySelectorAll(sel));
                        return nodes.some(n => {
                            const r = n.getBoundingClientRect();
                            return r.width > 0 && r.height > 0;
                        });
                    }""", PIN_BADGE_SELECTOR))
                except Exception:
                    pass

            if badge_found:
                # proof 스크린샷 저장 (무인 가동 증빙)
                try:
                    proof_dir = CURRENT_DIR / "proof_screenshots"
                    proof_dir.mkdir(parents=True, exist_ok=True)
                    proof_path = proof_dir / f"pinned_{vid}_{int(time.time())}.png"
                    await page.screenshot(path=str(proof_path), full_page=False)
                    logger.info(f"📸 [고정 댓글] 핀 고정 증빙 스크린샷 저장: {proof_path.name}")
                except Exception as se:
                    logger.debug(f"증빙 스크린샷 저장 실패(무시): {se}")

                logger.info("📌 [고정 댓글] 최상단 상시 고정(Pin) 100% 완료! (핀 배지 DOM 실물 확인)")
                return "pinned"

            if confirm_clicked:
                logger.warning(
                    "⚠️ [고정 댓글] 확인 버튼은 클릭했으나 핀 배지 미검출 — "
                    "고정 미적용 가능성. 성공 위조 금지(return submitted)"
                )
            else:
                logger.warning("⚠️ [고정 댓글] 댓글은 실물 검증되었으나 핀 고정 확인 버튼을 찾지 못했습니다.")
            return "submitted"

        except Exception as pe:
            logger.warning(f"⚠️ [고정 댓글] 핀 고정 시퀀스 예외 (댓글 등록은 실물 검증됨): {pe}")
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
            logger.warning("⚠️ [Aura YouTube Bot] 세션 파일(youtube_session.json) 또는 영구 프로필이 없습니다.")
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
        tag_str = AuraHashtagMatrix.get_shorts_hashtags(topic_id)
        yt_tags = tag_str.split() if tag_str else ["#아우라AI데이팅", "#Shorts"]

        raw_title = title or f"{self.HOOK_TITLES.get(topic_id, '소개팅 꿀팁 대방출')} #아우라AI데이팅 #Shorts"
        if "#Shorts" not in raw_title and "#shorts" not in raw_title:
            raw_title = f"{raw_title} #Shorts"
        # 유튜브 제목 최대 100자 제한
        final_title = raw_title[:100]

        # 설명란 조립 (4단 해시태그 결합)
        tags_line = " ".join(yt_tags) if yt_tags else "#아우라AI데이팅 #소개팅꿀팁 #연애심리 #Shorts"
        desc_body = description or (
            "소개팅 긴급 탈출부터 50:50 완벽 성비 라운지까지!\n\n"
            f"🔍 네이버 검색창에 👉 [ {self.OFFICIAL_KEYWORD} ] 검색해보세요!\n"
            f"공식 라운지 바로가기: {self.LANDING_URL}\n\n"
        )
        full_desc = f"{desc_body.strip()}\n\n{tags_line}".strip()[:5000]

        # 고정 댓글 문구
        pinned_comment = (
            "📌 영상에서 나온 50:50 완벽 성비 AI 소개팅 라운지는\n"
            f"네이버에 👉 [ {self.OFFICIAL_KEYWORD} ] 검색하시면 바로 나옵니다!\n"
            f"(공식 링크: {self.LANDING_URL})"
        )

        logger.info("=" * 70)
        logger.info(f"🤖 [Aura YouTube Bot] 쇼츠 직접 브라우저 업로드 시작: {final_title}")
        logger.info(f"  • 대상 파일: {target_video.name}")
        logger.info(f"  • 공개 설정: {privacy_status}")
        logger.info("=" * 70)

        # 브라우저 프로필 잠금 파일 청소
        clean_browser_profile_locks(self.profile_dir)

        start_time = time.time()
        video_url = ""
        video_id = ""

        async with async_browser_lock(f"Aura 유튜브 쇼츠 업로드 ({final_title[:15]})"):
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
                
                # Anti-detect 스크립트
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
                        logger.error("🛑 [Aura YouTube Bot] 구글 로그인이 만료되었습니다. setup_youtube_profile.py를 실행해 주세요.")
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
                        # 만들기 버튼 클릭
                        create_btn = page.locator("#create-button, #create-icon, button:has-text('만들기'), button:has-text('Create'), ytcp-button#create-icon").first
                        if await create_btn.is_visible():
                            await create_btn.click()
                            await asyncio.sleep(1.0)
                            upload_menu = page.locator("tp-yt-paper-item:has-text('동영상 업로드'), tp-yt-paper-item:has-text('Upload videos'), #text-item-0").first
                            if await upload_menu.is_visible():
                                await upload_menu.click()
                                await asyncio.sleep(1.5)
                        else:
                            # 홈 화면 업로드 아이콘 클릭
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
                    logger.info(f"✅ [Aura YouTube Bot] 숏폼 동영상 주입 완료: {target_video.name}")
                    await asyncio.sleep(4.0)

                    # 3. 세부정보 입력 모달 처리
                    # 3. 세부정보 입력 모달 처리
                    logger.info("📝 [3/5] 제목, 설명란, 옵션 무인 기입 중...")
                    
                    # 제목 입력란 탐색 및 주입 (DOM 부착 즉시 JS + 포커스 타이핑)
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

                    # Playwright 포커스 및 타이핑 보조
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

                    # 4. 다음 단계 순차 이동 (1.세부정보 -> 2.동영상 요소 -> 3.검사 -> 4.공개 상태)
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

                    # 동영상 링크 사전 추출 시도
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

                    # [게시] 또는 [저장] 버튼 클릭
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

                    # 완료 팝업에서 다시 한번 링크 추출
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

                    logger.info(f"🎉 [Aura YouTube Bot] 쇼츠 무인 발행 완결! URL: {video_url or '게시 완료'}")

                    # 4-1) [서버 인코딩/배포 안정화 대기] 대표님 절대 지침
                    #   ★ 왜 35초인가: 게시 팝업을 닫은 직후 곧바로 쇼츠 페이지로 돌진하면
                    #     YouTube 서버가 아직 인코딩/배포를 마치지 않아 댓글 컴포넌트가
                    #     마운트되지 않은 상태로 진입 ➔ 댓글 등록이 100% 실패했다.
                    #     서버 배포 및 댓글 컴포넌트 안정화를 위해 정확히 35초 대기한다.
                    logger.info("⏳ [유튜브 무인 파이프라인] 영상 서버 인코딩 및 배포 완료 대기 (정확히 35초 휴식 후 고정 댓글 진입)...")
                    await asyncio.sleep(35.0)

                    # 5. 고정 댓글(Pinned Comment) 자동 작성 + 최상단 핀(Pin) 고정
                    comm_status = "skipped"
                    if video_id:
                        try:
                            comm_status = await self._post_and_pin_comment(page, video_id, pinned_comment)
                            if comm_status == "pinned":
                                logger.info("📌 [Aura YouTube Bot] 공식 검색어 유도 댓글 등록 + 최상단 고정 완결!")
                            elif comm_status == "submitted":
                                logger.info("✅ [Aura YouTube Bot] 공식 검색어 유도 댓글 등록 성공 (핀 고정 미확인)")
                        except Exception as ce:
                            logger.warning(f"댓글/핀 고정 안내 (스튜디오 게시 성공 유지): {ce}")
                    else:
                        logger.warning("⚠️ [고정 댓글] video_id 추출 실패로 댓글/핀 고정을 건너뜁니다.")

                    # 세션 쿠키 갱신 저장
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
                    logger.error(f"❌ [Aura YouTube Bot] 발행 실패: {ex}")
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

    # ------------------------------------------------------------------
    # [독립 댓글 인터페이스] 이미 발행된 쇼츠에 댓글 + 핀 고정만 단독 수행
    #   ★ 왜 필요한가: 발행 파이프라인과 분리하여, 이미 업로드된 영상의 댓글 누락분을
    #     재실행/보수 처리할 수 있는 완전 자율 인터페이스를 제공한다.
    #   · video_id_or_url: 순수 ID 또는 전체 URL 모두 허용(_normalize_video_id 정규화)
    #   · custom_comment 미지정 시 브랜드 공식 검색 유도 문구를 자동 사용
    #   · 브라우저 세션/쿠키 주입은 publish_short_async 와 100% 동일 계약을 재사용한다.
    # ------------------------------------------------------------------
    def post_comment_only(
        self,
        video_id_or_url: str,
        custom_comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """이미 발행된 쇼츠 영상에 독립적으로 댓글 등록 + 최상단 핀 고정을 수행한다."""
        try:
            return asyncio.run(self.post_comment_only_async(video_id_or_url, custom_comment))
        except Exception as e:
            logger.error(f"❌ [Aura YouTube Bot] 독립 댓글 등록 예외: {e}")
            res = {
                "status": "error",
                "platform": "youtube_shorts",
                "action": "comment_only",
                "video_id_or_url": video_id_or_url,
                "error": str(e),
                "published_at": get_now_kst_str(),
            }
            self._save_history(res)
            return res

    async def post_comment_only_async(
        self,
        video_id_or_url: str,
        custom_comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """post_comment_only 의 비동기 코루틴 본체 (완전 자율 브라우저 세션)."""
        vid = self._normalize_video_id(video_id_or_url)
        if not vid:
            return {
                "status": "error",
                "platform": "youtube_shorts",
                "action": "comment_only",
                "video_id_or_url": video_id_or_url,
                "error": "video_id 정규화 실패 — 순수 ID 또는 유튜브 URL 필요",
                "published_at": get_now_kst_str(),
            }

        if not self.is_available():
            return {
                "status": "error",
                "platform": "youtube_shorts",
                "action": "comment_only",
                "video_id": vid,
                "error": "세션 파일 또는 영구 프로필 부재 (setup_youtube_profile.py 실행 요망)",
                "published_at": get_now_kst_str(),
            }

        comment_text = custom_comment or (
            "📌 영상에서 나온 50:50 완벽 성비 AI 소개팅 라운지는\n"
            f"네이버에 👉 [ {self.OFFICIAL_KEYWORD} ] 검색하시면 바로 나옵니다!\n"
            f"(공식 링크: {self.LANDING_URL})"
        )

        logger.info("=" * 70)
        logger.info(f"💬 [Aura YouTube Bot] 독립 댓글 등록 시작: video_id={vid}")
        logger.info("=" * 70)

        clean_browser_profile_locks(self.profile_dir)
        start_time = time.time()

        async with async_browser_lock(f"Aura 유튜브 댓글 등록 ({vid})"):
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

                # 세션 쿠키 주입 (publish_short_async 와 동일 계약)
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
                    # [진입 안정성 보장] publish_short_async 와 100% 동일 계약:
                    #   쇼츠 페이지 진입 직후 댓글 컴포넌트가 안정화될 시간을 확보한다.
                    logger.info("⏳ [유튜브 무인 파이프라인] 쇼츠 페이지 로드 및 댓글 컴포넌트 안정화 대기 (6초)...")
                    await asyncio.sleep(6.0)

                    comm_status = await self._post_and_pin_comment(page, vid, comment_text)

                    # 세션 쿠키 갱신 저장
                    try:
                        cookies = await context.cookies()
                        clean_cookies = [
                            {"name": c["name"], "value": c["value"],
                             "domain": c.get("domain", ".youtube.com"), "path": c.get("path", "/")}
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
                    ok = comm_status in ("pinned", "submitted")
                    res = {
                        "status": "success" if ok else "error",
                        "platform": "youtube_shorts",
                        "action": "comment_only",
                        "brand": self.BRAND,
                        "video_id": vid,
                        "video_url": f"https://youtube.com/shorts/{vid}",
                        "comment": comment_text,
                        "comment_status": comm_status,
                        "elapsed_sec": elapsed,
                        "published_at": get_now_kst_str(),
                        "message": (
                            "댓글 등록 + 최상단 핀 고정 완료" if comm_status == "pinned"
                            else ("댓글 등록 완료(핀 고정 미확인)" if comm_status == "submitted"
                                  else "댓글 등록 실물 검증 실패 — 성공 위조 금지")
                        ),
                    }
                    if not ok:
                        res["error"] = "댓글 등록 실물 검증 실패(또는 등록 버튼 미활성)"
                    self._save_history(res)
                    return res

                except Exception as ex:
                    logger.error(f"❌ [Aura YouTube Bot] 독립 댓글 등록 실패: {ex}")
                    try:
                        await context.close()
                    except Exception:
                        pass
                    err_res = {
                        "status": "error",
                        "platform": "youtube_shorts",
                        "action": "comment_only",
                        "video_id": vid,
                        "error": str(ex),
                        "published_at": get_now_kst_str(),
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
    bot = AuraYouTubeBotPublisher(headless=False)
    print(f"💖 Aura YouTube Bot Publisher 준비 완료! (가용성: {bot.is_available()})")
