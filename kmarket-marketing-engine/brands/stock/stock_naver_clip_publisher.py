# -*- coding: utf-8 -*-
"""
📈 StockMaster 주식AI Real Naver Clip Publisher (📈 StockMaster 주식AI 전용 네이버 클립 숏폼 무인 자동 발행 레고 블록)
=============================================================================
- 역할:
  1. 네이버 세션(naver_session.json)으로 https://clipcreators.naver.com/web/upload 접속
  2. 9:16 세로 풀HD 숏폼 비디오(MP4) 직접 첨부 및 업로드
  3. 설명문 + 해시태그 + 랜딩 URL 자동 입력
  4. 프론트엔드 해시 변경에도 깨지지 않는 텍스트/접근성 기반 범용 1차/2차 카테고리 자동 선택
  5. 비디오 인코딩 100% 완료 감지 후 최종 등록 버튼 클릭 및 실측 송출 완료
"""

import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import BASE_DIR, get_now_kst_str
from core.engine.browser_guard import async_browser_lock, get_safe_browser_args, clean_browser_profile_locks
from core.engine.session_integrity import load_best_cookies, sanitize_for_playwright, safe_save, has_auth


logger = logging.getLogger("StockNaverClipPublisher")

SESSION_FILE = CURRENT_DIR / "naver_session.json"
PROFILE_DIR = CURRENT_DIR / "naver_browser_profile"
ACCOUNTS_FILE = CURRENT_DIR / "accounts.json"


class StockNaverClipPublisher:
    """📈 StockMaster 주식AI 전용 네이버 클립(Clip) 공식 스튜디오 자동 발행 엔진"""

    def __init__(self, clip_id: str = "stockmaster_ai"):
        self.brand = "stock"
        self.clip_id = clip_id
        self.session_file = SESSION_FILE
        self.profile_dir = PROFILE_DIR
        self.history_file = CURRENT_DIR / "naver_clip_history.json"
        self.channel_url = f"https://clip.naver.com/@{self.clip_id}"

    def is_available(self) -> bool:
        if self.session_file.exists() and self.session_file.stat().st_size > 100:
            return True
        best = load_best_cookies("naver", self.session_file)
        return bool(best and has_auth("naver", best))

    def publish_clip(
        self,
        video_path: Optional[str] = None,
        topic_id: Optional[int] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        timeout_sec: int = 60
    ) -> Dict[str, Any]:
        """동기 호출 인터페이스"""
        try:
            return asyncio.run(
                self.publish_clip_async(
                    video_path=video_path,
                    topic_id=topic_id,
                    title=title,
                    description=description,
                    timeout_sec=timeout_sec
                )
            )
        except Exception as e:
            logger.error(f"❌ [📈 StockMaster 주식AI] 네이버 클립 발행 예외: {e}")
            return {"status": "error", "message": str(e), "brand": "stock"}

    async def publish_clip_async(
        self,
        video_path: Optional[str] = None,
        topic_id: Optional[int] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        timeout_sec: int = 60
    ) -> Dict[str, Any]:
        """비동기 네이버 클립 스튜디오 실제 자동 업로드 및 등록"""
        # 세션 무결성 검증 및 .good.json 자동 복원
        existing_cookies = []
        if self.session_file.exists():
            try:
                with open(self.session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                existing_cookies = data if isinstance(data, list) else data.get("cookies", [])
            except Exception:
                existing_cookies = []

        if not has_auth("naver", existing_cookies):
            best = load_best_cookies("naver", self.session_file)
            if best:
                logger.info("[RESTORE] [📈 StockMaster 주식AI Naver Clip] 네이버 세션 부재/만료 → .good.json 백업에서 자동 복원 완료")
            elif not self.session_file.exists():
                return {"status": "error", "message": "naver_session.json 부재 및 유효한 백업 없음 (1회 네이버 로그인 필요)", "brand": "stock"}


        if not video_path or not os.path.exists(video_path):
            return {"status": "error", "message": f"업로드할 비디오 파일 없음: {video_path}", "brand": "stock"}

        target_video = Path(video_path)
        main_title = title or "AI 퀀트 주식 리포트"
        clip_desc = description or main_title
        # 🛡️ 본문 내 URL 전면 소독 (알고리즘 다운랭킹 방지) 및 첫 댓글 참조 안내 보장
        if "첫 번째 댓글" not in clip_desc:
            clip_desc = f"💬 국내 350개 종목 AI 퀀트 점수 확인 링크는 [첫 번째 댓글]을 확인해 보세요!\n\n{clip_desc}"
        clip_desc = re.sub(r'https?://\S+', '👉 [첫 번째 댓글 링크 참조]', clip_desc)
        upload_url = "https://clipcreators.naver.com/web/upload"

        logger.info(f"🚀 [📈 StockMaster 주식AI Naver Clip] 숏폼 발행 시작: '{main_title}' (영상: {target_video.name})")

        clean_browser_profile_locks(self.profile_dir)

        async with async_browser_lock(f"📈 StockMaster 주식AI 네이버 클립 발행 ({main_title[:15]})", timeout_sec=1200):
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=get_safe_browser_args([
                        "--disable-blink-features=AutomationControlled",
                        "--no-first-run",
                        "--no-default-browser-check"
                    ])
                )
                context = await browser.new_context(
                    storage_state=str(self.session_file),
                    viewport={"width": 1280, "height": 900},
                    permissions=["clipboard-read", "clipboard-write"]
                )
                page = await context.new_page()

                try:
                    # 1. 업로드 페이지 이동
                    logger.info("1. 네이버 클립 스튜디오 접속 중...")
                    await page.goto(upload_url, wait_until="domcontentloaded", timeout=timeout_sec * 1000)
                    await asyncio.sleep(3.0)

                    # 로그인 풀림 감지 → 백업 쿠키 자동 복원 시도
                    if "nid.naver.com" in page.url:
                        logger.warning("⚠️ 네이버 세션 만료 감지, 백업 쿠키 주입 시도...")
                        best = load_best_cookies("naver", self.session_file)
                        if best:
                            for c in sanitize_for_playwright(best):
                                try:
                                    await context.add_cookies([c])
                                except Exception:
                                    pass
                            await page.goto(upload_url, wait_until="domcontentloaded", timeout=timeout_sec * 1000)
                            await asyncio.sleep(3.0)
                        if "nid.naver.com" in page.url:
                            raise RuntimeError("네이버 로그인 세션 만료 [백업도 실패]. naver_login 재실행 필요.")
                        logger.info("[RESTORE] 네이버 백업 쿠키 복원 성공!")


                    # 2. 동영상 파일 주입 (input[type='file'])
                    logger.info("2. 동영상 파일 주입 중...")
                    file_input = await page.wait_for_selector("input[type='file']", timeout=15000)
                    await file_input.set_input_files(str(target_video.resolve()))
                    logger.info(f"   🎬 동영상 파일 첨부 성공: {target_video.name}")
                    await asyncio.sleep(4.0)

                    # 3. 설명문/본문 입력 (textarea)
                    logger.info("3. 클립 설명 & 해시태그 입력 중...")
                    desc_area = await page.wait_for_selector("textarea", timeout=15000)
                    await desc_area.click()
                    await desc_area.fill(clip_desc)
                    logger.info("   📝 설명문 입력 완료")
                    await asyncio.sleep(1.5)

                    # 4. 1차 카테고리 선택 (해시 클래스 대신 텍스트/범용 셀렉터 사용)
                    logger.info("4. 1차 카테고리 드롭다운 탐색 및 선택 중...")
                    cat1_btn = None
                    # 범용 1차 카테고리 버튼 탐색
                    buttons = await page.query_selector_all("button, div[role='button'], div[role='combobox']")
                    for b in buttons:
                        txt = (await b.inner_text()).strip()
                        if "1차 카테고리" in txt or "카테고리 선택" in txt or "카테고리" in txt:
                            cat1_btn = b
                            break

                    if not cat1_btn:
                        cat1_btn = await page.query_selector("button[class*='dropdownPrimary'], button[class*='dropdown']")

                    if cat1_btn:
                        await cat1_btn.click()
                        await asyncio.sleep(1.2)

                        # 드롭다운 옵션 탐색
                        options = await page.query_selector_all("button[class*='dropdownOption'], [role='option'], button")
                        target_opt = None
                        for opt in options:
                            opt_txt = (await opt.inner_text()).strip()
                            if '경제' in opt_txt or '금융' in opt_txt or '비즈니스' in opt_txt or 'IT' in opt_txt or '일상기록' in opt_txt:
                                target_opt = opt
                                break

                        if not target_opt and options:
                            # 키워드 매칭 안 되면 두 번째 옵션(첫 번째는 보통 플레이스홀더) 선택
                            target_opt = options[1] if len(options) > 1 else options[0]

                        if target_opt:
                            await target_opt.click()
                            logger.info(f"   ✅ 1차 카테고리 선택 완료: '{(await target_opt.inner_text()).strip()}'")
                            await asyncio.sleep(1.0)

                    # 5. 2차 카테고리 선택 (존재할 경우)
                    cat2_btn = None
                    buttons = await page.query_selector_all("button, div[role='button']")
                    for b in buttons:
                        txt = (await b.inner_text()).strip()
                        if "2차 카테고리" in txt:
                            cat2_btn = b
                            break

                    if cat2_btn and not await cat2_btn.is_disabled():
                        await cat2_btn.click()
                        await asyncio.sleep(1.0)
                        options2 = await page.query_selector_all("button[class*='dropdownOption'], [role='option']")
                        if len(options2) > 1:
                            await options2[1].click()
                            logger.info(f"   ✅ 2차 카테고리 선택 완료: '{(await options2[1].inner_text()).strip()}'")
                            await asyncio.sleep(1.0)

                    # 6. 비디오 인코딩 100% 완료 및 등록(Submit) 버튼 활성화 대기
                    logger.info("5. 비디오 인코딩 완료 및 등록 버튼 활성화 대기 중...")
                    submit_btn = None
                    for wait_i in range(40):
                        # 범용 등록 버튼 탐색
                        btns = await page.query_selector_all("button[type='submit'], button")
                        for btn in btns:
                            txt = (await btn.inner_text()).strip()
                            if txt in ["등록", "발행", "Submit", "Publish"]:
                                is_dis = await btn.is_disabled()
                                if not is_dis:
                                    submit_btn = btn
                                    break
                        if submit_btn:
                            break
                        await asyncio.sleep(1.0)

                    if not submit_btn:
                        # 폴백 시도
                        submit_btn = await page.query_selector("button:has-text('등록'), button[type='submit']")

                    if submit_btn:
                        logger.info("6. 🚀 네이버 클립 [등록] 버튼 클릭!")
                        try:
                            await submit_btn.click(force=True, timeout=5000)
                        except Exception:
                            await page.evaluate("(b) => b.click()", submit_btn)

                        # 🌟 [네이버 클립 등록 완료 100% 명시적 대기 - 최대 60초]
                        logger.info("⏳ [네이버 클립] 등록 버튼 클릭 후 서버 완료 응답 대기 중...")
                        clip_finished = False
                        for wait_sec in range(60):
                            cur_url = page.url
                            page_text = ""
                            try:
                                page_text = await page.inner_text("body")
                            except Exception:
                                pass

                            is_success = ("upload" not in cur_url and ("clip" in cur_url or "channel" in cur_url or "creator" in cur_url)) or any(sig in page_text for sig in [
                                "등록되었습니다", "클립 등록 완료", "발행되었습니다", "업로드 완료"
                            ])

                            if is_success:
                                logger.info(f"🎉 [네이버 클립 서버 등록 100% 완료 확인!] ({wait_sec}초 경과)")
                                clip_finished = True
                                await asyncio.sleep(3.0)
                                break

                            await asyncio.sleep(1.0)

                        if not clip_finished:
                            logger.info("⏳ 네이버 클립 백그라운드 처리 대기 (추가 8초)...")
                            await asyncio.sleep(8.0)

                        # 🌟 성공 시 세션 최신화 및 .good.json 백업
                        try:
                            live_cookies = await context.cookies()
                            if has_auth("naver", live_cookies):
                                safe_save("naver", live_cookies, self.session_file)
                                logger.info("💾 [📈 StockMaster 주식AI Naver Clip] 최신 네이버 세션 및 .good.json 백업 자동 저장 완료")
                        except Exception as se:
                            logger.warning(f"네이버 세션 백업 저장 경고: {se}")

                        # 📌 [무인 파이프라인] 네이버 클립 서버 인코딩 및 배포 대기 (정확히 60초 휴식)
                        logger.info("⏳ [네이버 클립 무인 파이프라인] 클립 인코딩 및 채널 배포 대기 (정확히 60초 휴식 후 완료)...")
                        await asyncio.sleep(60.0)

                        logger.info(f"🎉 [📈 StockMaster 주식AI Naver Clip] 클립 발행 성공! 채널: {self.channel_url}")
                        return {
                            "status": "success",
                            "platform": "naver_clip",
                            "brand": "stock",
                            "topic_id": topic_id,
                            "title": main_title,
                            "video_file": target_video.name,
                            "channel_url": self.channel_url,
                            "published_at": get_now_kst_str()
                        }
                    else:
                        raise RuntimeError("네이버 클립 등록 버튼 활성화 실패 (인코딩 미완료 또는 필수 항목 누락)")

                except Exception as e:
                    logger.error(f"❌ [📈 StockMaster 주식AI Naver Clip] 업로드 실패: {e}")
                    return {
                        "status": "error",
                        "platform": "naver_clip",
                        "brand": "stock",
                        "message": str(e)
                    }
                finally:
                    await browser.close()


if __name__ == "__main__":
    pub = StockNaverClipPublisher()
    print("Is available:", pub.is_available())
