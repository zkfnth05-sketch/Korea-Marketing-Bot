# -*- coding: utf-8 -*-
"""
Stock Real Naver Clip Publisher (📈 StockMaster AI 전용 진짜 네이버 클립 숏폼 무인 자동 발행 레고 블록)
=============================================================================================
- 역할:
  1. 저장된 Playwright 세션(naver_session.json)으로 https://clipcreators.naver.com/web/upload 접속
  2. 9:16 세로 풀HD 숏폼 비디오(MP4) 직접 첨부 및 업로드
  3. 동영상 설명(최대 300자) + StockMaster 4단 해시태그(#스톡마스터AI) + 공식 검색어/랜딩 URL 자동 입력
  4. 1차/2차 카테고리(경제/테크) 자동 선택
  5. 100% 무인 발행 완료 후 실제 네이버 클립 채널(https://clip.naver.com/@stockmaster_ai)에 즉시 공개 송출
- 원칙: Rule 1 (독립 레고 블록), Rule 6 (24시간 무인 자율 구동), Rule 7 (공식 검색어 '스톡마스터 AI')
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
from brands.stock.stock_hashtag_matrix import StockHashtagMatrix

logger = logging.getLogger("StockNaverClipPublisher")

SESSION_FILE = CURRENT_DIR / "naver_session.json"
ACCOUNTS_FILE = CURRENT_DIR / "accounts.json"


class StockNaverClipPublisher:
    """📈 StockMaster AI 전용 네이버 클립(Clip) 공식 스튜디오 자동 발행 엔진"""

    def __init__(self, clip_id: str = "stockmaster_ai"):
        self.brand = "stock"
        self.clip_id = clip_id
        self.session_file = SESSION_FILE
        self.history_file = CURRENT_DIR / "naver_clip_history.json"
        self.shorts_output_dir = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Stock")
        self.channel_url = f"https://clip.naver.com/@{self.clip_id}"

    def is_available(self) -> bool:
        return self.session_file.exists() and self.session_file.stat().st_size > 100

    def find_latest_short_video(self, topic_id: Optional[int] = None) -> Optional[Path]:
        """바탕화면 산출물 폴더에서 가장 최신 렌더링된 Stock 숏폼 MP4 자동 탐색"""
        search_dirs = [self.shorts_output_dir, BASE_DIR / "outputs" / "stock"]
        for sdir in search_dirs:
            if sdir.exists():
                candidates = [p for p in sdir.glob("**/*.mp4") if "04_app_sim" not in p.name and "temp" not in p.name]
                if candidates:
                    return max(candidates, key=os.path.getmtime)
        return None

    def publish_clip(
        self,
        video_path: Optional[str] = None,
        topic_id: int = 1,
        title: Optional[str] = None,
        description: Optional[str] = None,
        timeout_sec: int = 60
    ) -> Dict[str, Any]:
        """동기 호출 인터페이스"""
        try:
            return asyncio.run(self.publish_clip_async(
                video_path=video_path,
                topic_id=topic_id,
                title=title,
                description=description,
                timeout_sec=timeout_sec
            ))
        except Exception as e:
            logger.error(f"❌ [Naver-Stock Real Clip] 발행 예외 발생: {e}")
            return {"status": "error", "message": str(e), "brand": "stock"}

    async def publish_clip_async(
        self,
        video_path: Optional[str] = None,
        topic_id: int = 1,
        title: Optional[str] = None,
        description: Optional[str] = None,
        timeout_sec: int = 60
    ) -> Dict[str, Any]:
        """Playwright를 통한 실제 Clip Creators 웹 네이버 클립 숏폼 발행 실행"""
        if not self.is_available():
            logger.warning("⚠️ [Naver-Stock] naver_session.json 세션 파일이 없습니다.")
            return {"status": "error", "message": "세션 파일 부재", "brand": "stock"}

        if not video_path or not Path(video_path).exists():
            return {"status": "error", "message": f"업로드할 실시간 신선 숏폼 비디오가 없습니다: {video_path}", "brand": "stock"}
        target_video = Path(video_path)

        hook_titles = {
            1: "기관/외국인이 지금 몰래 쓸어담는 국내 주식 TOP 3 대공개",
            2: "AI 퀀트 적정주가와 세력 체결강도 실시간 계산법 ㄷㄷ",
            3: "삼성전자 vs SK하이닉스 2026년 하반기 승자는 누구?",
            4: "매수 버튼 누르기 전 3초 만에 확인해야 할 수급 골든크로스",
            5: "코스피 코스닥 세력 체결강도 120% 돌파 실시간 진단 결과",
            6: "주식 초보가 100% 물리는 물타기 실수와 AI 탈출 공식",
            7: "외인 연속 순매수 5일 돌파! 내일 급등할 국내 관심종목은?",
            8: "배당 수익률 8% 넘는 국내 알짜배기 고배당주 포트폴리오"
        }
        main_title = title or hook_titles.get(topic_id, "주식 AI 퀀트 분석")
        
        # 네이버 클립 300자 이내 설명문 구성 (블로그 + 공식 Vercel 2개 링크 동시 탑재)
        fallback_desc = (
            f"{main_title}\n\n"
            f"📝 상세 칼럼(블로그): https://blog.naver.com/stockmaster_ai\n"
            f"🚀 AI 수급 분석(체험): https://stockmaster-ai.vercel.app/\n"
            f"🔍 네이버 검색창: [스톡마스터 AI]\n\n"
            f"#스톡마스터AI #주식AI #주식투자 #적정주가 #수급분석"
        )
        clip_desc = description or fallback_desc

        upload_url = "https://clipcreators.naver.com/web/upload"
        logger.info(f"🚀 [Naver-Stock Real Clip] 숏폼 발행 시작: '{main_title}' (영상: {target_video.name})")

        from core.engine.browser_guard import async_browser_lock, get_safe_browser_args

        async with async_browser_lock(f"Stock 네이버 클립 발행 ({main_title[:15]})"):
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=get_safe_browser_args()
                )
                context = await browser.new_context(
                    storage_state=str(self.session_file),
                    viewport={"width": 1280, "height": 900},
                    permissions=["clipboard-read", "clipboard-write"]
                )
                page = await context.new_page()

                try:
                    # 1. 업로드 페이지 이동
                    await page.goto(upload_url, wait_until="networkidle", timeout=timeout_sec * 1000)
                    await asyncio.sleep(2.0)

                    # 프로필 생성 유도 화면이 뜰 경우 1회 자동 생성 처리
                    if "/signup" in page.url:
                        create_link = await page.query_selector("a:has-text('프로필 만들기'), a:has-text('10초')")
                        if create_link:
                            await create_link.click()
                            await asyncio.sleep(2.0)
                            input_el = await page.query_selector("input[type='text'], input")
                            if input_el:
                                await input_el.click()
                                await page.keyboard.press("Control+A")
                                await page.keyboard.press("Backspace")
                                await page.keyboard.type(self.clip_id, delay=15)
                                confirm_btn = await page.query_selector("button:has-text('확인'), a:has-text('확인')")
                                if confirm_btn:
                                    await confirm_btn.click()
                                    await asyncio.sleep(3.0)
                            await page.goto(upload_url, wait_until="networkidle")
                            await asyncio.sleep(2.0)

                    # 2. 동영상 파일 주입
                    file_input = await page.wait_for_selector("input[type='file']", timeout=10000)
                    await file_input.set_input_files(str(target_video.resolve()))
                    logger.info(f"🎬 [Naver-Stock] 동영상 파일 주입 성공: {target_video.name}")

                    # 3. 편집 폼 로드 대기 및 설명문 입력
                    desc_area = await page.wait_for_selector("textarea[name='description']", timeout=15000)
                    await desc_area.click()
                    await desc_area.fill(clip_desc)
                    logger.info("📝 [Naver-Stock] 클립 설명 & 해시태그 입력 완료")
                    await asyncio.sleep(1.0)

                    # 4. 1차 카테고리 선택 (경제/테크)
                    cat1_btn = await page.query_selector(".ClipDetailForm_dropdownPrimary__6ZbSU, button:has-text('1차 카테고리')")
                    if cat1_btn:
                        await cat1_btn.click()
                        await asyncio.sleep(1.0)
                        target_opt = await page.query_selector("button.ClipDetailForm_dropdownOption__KunGJ:has-text('경제'), button.ClipDetailForm_dropdownOption__KunGJ:has-text('테크'), button.ClipDetailForm_dropdownOption__KunGJ")
                        if target_opt:
                            await target_opt.click()
                            await asyncio.sleep(1.0)

                    # 5. 2차 카테고리 선택
                    cat2_btn = await page.query_selector(".ClipDetailForm_dropdownSecondary__2ebKr, button:has-text('2차 카테고리')")
                    if cat2_btn and not await cat2_btn.is_disabled():
                        await cat2_btn.click()
                        await asyncio.sleep(1.0)
                        target_opt2 = await page.query_selector("button.ClipDetailForm_dropdownOption__KunGJ")
                        if target_opt2:
                            await target_opt2.click()
                            await asyncio.sleep(1.0)

                    # 6. 인코딩 완료 대기 및 등록 버튼 활성화
                    submit_btn = await page.wait_for_selector("button.ClipDetailForm_submitBtn__8PUrw, button[type='submit']:has-text('등록')", timeout=10000)
                    for _ in range(30):
                        if not await submit_btn.is_disabled():
                            break
                        await asyncio.sleep(1.0)

                    # 7. 최종 등록 클릭
                    await submit_btn.click()
                    logger.info("🎉 [Naver-Stock] 네이버 클립 [등록] 버튼 클릭 성공!")
                    await asyncio.sleep(5.0)

                    modal_confirm = await page.query_selector("[role='dialog'] button:has-text('확인'), [role='dialog'] button:has-text('등록'), [role='dialog'] button:has-text('게시')")
                    if modal_confirm:
                        await modal_confirm.click()
                        await asyncio.sleep(3.0)

                    await context.storage_state(path=str(self.session_file))

                    logger.info(f"🎉 [Naver-Stock] 네이버 클립 숏폼 공개 발행 완료! 채널 URL: {self.channel_url}")

                    res = {
                        "status": "success",
                        "platform": "naver_clip",
                        "brand": "stock",
                        "topic_id": topic_id,
                        "title": main_title,
                        "video_file": target_video.name,
                        "channel_url": self.channel_url,
                        "published_at": get_now_kst_str()
                    }
                    self._save_history(res)
                    await browser.close()
                    return res

                except Exception as e:
                    logger.error(f"❌ [Naver-Stock Real Clip] 실행 중 예외: {e}")
                    await browser.close()
                    return {"status": "error", "error": str(e), "brand": "stock"}

    def _save_history(self, data: Dict[str, Any]):
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
    pub = StockNaverClipPublisher()
    print("Stock Real Naver Clip Publisher 준비 완료! (세션 유효:", pub.is_available(), ")")
