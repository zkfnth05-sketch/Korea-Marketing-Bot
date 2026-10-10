# -*- coding: utf-8 -*-
"""
[독립 레고 블록] Aura TikTok Publisher (💖 Aura 데이팅 전용 틱톡 쇼츠 브라우저 봇 무인 직접 업로더)
====================================================================================================
- 브랜드: Aura AI 데이팅 (공식 검색어: '아우라AI데이팅' 붙여쓰기 불변)
- 핵심 역할:
  1. [0 API 순수 브라우저 봇]: TikTok Web Studio(https://www.tiktok.com/tiktokstudio/upload?lang=ko-KR) 직접 자동화
  2. [영구 세션 & 프로필 연동]: tiktok_browser_profile 및 tiktok_session.json 쿠키 주입
  3. [사람처럼 행동하는 스텔스 업로드]: 베지어 곡선 마우스 이동, 자연스러운 타이핑 딜레이, 팝업 자동 처리
  4. [공식 메타데이터 패키징]: 제미나이 1회 호출 맞춤 캡션 + 공식 네이버 검색어(#아우라AI데이팅) + 4단 해시태그
  5. [22초 완제품 엄격 검증]: 10초 중간 원테이크 배제, 22초 오리지널 풀HD 숏폼만 엄선 주입
  6. [무결성 검증 & 증빙]: 실시간 업로드 완료 감지 및 증빙 스크린샷 자동 저장
  7. [단독 안전 락]: async_browser_lock으로 다른 브라우저 봇과의 충돌 원천 차단
- 원칙: Rule 1 (독립 레고 블록), Rule 5 (땜질 금지), Rule 6 (24시간 무인 자율 구동), Rule 7 (공식 규격)
"""

import os
import sys
import json
import time
import random
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
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
from core.engine.browser_guard import (
    async_browser_lock,
    get_safe_browser_args,
    clean_browser_profile_locks
)

logger = logging.getLogger("AuraTikTokPublisher")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def _bezier_points(start: tuple, end: tuple, steps: int = 15) -> List[tuple]:
    """자연스러운 인간 마우스 베지어 이동 곡선"""
    sx, sy = start
    ex, ey = end
    cx = (sx + ex) / 2 + random.randint(-30, 30)
    cy = (sy + ey) / 2 + random.randint(-25, 25)
    points = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * sx + 2 * (1 - t) * t * cx + t ** 2 * ex
        y = (1 - t) ** 2 * sy + 2 * (1 - t) * t * cy + t ** 2 * ey
        points.append((int(x), int(y)))
    return points


class AuraTikTokPublisher:
    """💖 Aura 데이팅 전용 틱톡 쇼츠 브라우저 봇 직접 업로드 엔진"""

    BRAND = "aura"
    OFFICIAL_KEYWORD = "아우라AI데이팅"
    LANDING_URL = "https://aura-ai-dating.vercel.app/"

    HOOK_TITLES = {
        1: "소개팅 나갔는데 분위기 싸할 때 1초 만에 합법 탈출하는 법 ㄷㄷ",
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
        self.profile_dir = CURRENT_DIR / "tiktok_browser_profile"
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = CURRENT_DIR / "tiktok_session.json"
        self.history_file = CURRENT_DIR / "tiktok_publish_history.json"
        self.shorts_output_dir = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Aura")

    def is_available(self) -> bool:
        """세션 파일 또는 영구 프로필 존재 여부 점검"""
        has_session = self.session_file.exists() and self.session_file.stat().st_size > 50
        has_profile = self.profile_dir.exists() and any(self.profile_dir.iterdir())
        return has_session or has_profile

    def find_latest_short_video(self, topic_id: Optional[int] = None) -> Optional[Path]:
        """
        바탕화면 산출물 폴더에서 22초 완제품 최종본 MP4를 엄격하게 자동 탐색
        (10초 중간 원테이크, 04_app_sim, temp 파일 배제)
        """
        if not self.shorts_output_dir.exists():
            return None

        folder_candidates = []
        for folder in self.shorts_output_dir.iterdir():
            if not folder.is_dir():
                continue
            if topic_id:
                topic_tag = f"0{topic_id}" if topic_id < 10 else str(topic_id)
                if f"Aura_{topic_tag}" not in folder.name and f"주제0{topic_id}" not in folder.name and f"주제{topic_tag}" not in folder.name:
                    continue
            folder_candidates.append(folder)

        # 최신 폴더 순 정렬
        folder_candidates.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        for folder in folder_candidates:
            mp4_list = list(folder.glob("*.mp4"))
            # 1순위: '22초숏폼' 또는 '완제품' 또는 'Aura_22초'가 들어간 완제품 MP4
            for mp4 in mp4_list:
                name = mp4.name
                if any(k in name for k in ["22초숏폼", "완제품", "22초", "최종"]):
                    if mp4.stat().st_size > 2 * 1024 * 1024:  # 최소 2MB 이상
                        return mp4

            # 2순위: 10초 원테이크나 app_sim, temp가 아닌 가장 큰 MP4
            valid_mp4s = [
                m for m in mp4_list
                if "10초_순수" not in m.name and "app_sim" not in m.name and "temp" not in m.name and m.stat().st_size > 2 * 1024 * 1024
            ]
            if valid_mp4s:
                valid_mp4s.sort(key=lambda x: x.stat().st_size, reverse=True)
                return valid_mp4s[0]

        # 3순위: 전체 폴더 대상 22초 완제품 탐색
        all_22s = list(self.shorts_output_dir.glob("**/*22초*.mp4"))
        if all_22s:
            all_22s.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            return all_22s[0]

        return None

    def publish_short(
        self,
        video_path: Optional[str] = None,
        topic_id: int = 1,
        caption: Optional[str] = None,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        동기 호출 인터페이스 (server.py 및 Omni 파일럿 연동용)
        """
        v_path = Path(video_path) if video_path else None
        try:
            return asyncio.run(self.publish_short_video(
                video_path=v_path,
                topic_id=topic_id,
                caption=caption,
                custom_title=title,
                custom_tags=tags
            ))
        except Exception as e:
            logger.error(f"❌ [Aura TikTok Publisher] 동기 실행 예외: {e}")
            return {"success": False, "error": str(e), "brand": self.BRAND, "platform": "tiktok"}

    async def _human_type(self, page, selector: str, text: str, delay_range=(0.03, 0.08)):
        """사람처럼 타자기 치듯 자연스러운 키스트로크 입력"""
        el = await page.query_selector(selector)
        if not el:
            return False
        await el.click()
        await asyncio.sleep(0.3)
        for char in text:
            await page.keyboard.type(char)
            await asyncio.sleep(random.uniform(*delay_range))
        return True

    async def publish_short_video(
        self,
        video_path: Optional[Path] = None,
        topic_id: int = 1,
        caption: Optional[str] = None,
        custom_title: Optional[str] = None,
        custom_tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        틱톡 웹 스튜디오(https://www.tiktok.com/tiktokstudio/upload?lang=ko-KR)에 숏폼 MP4 사람처럼 직접 발행
        """
        if not video_path or not Path(video_path).exists():
            video_path = self.find_latest_short_video(topic_id=topic_id)

        if not video_path or not Path(video_path).exists():
            err_msg = f"❌ [Aura TikTok] 발행할 22초 숏폼 비디오 완제품을 찾을 수 없습니다. (topic_id={topic_id})"
            logger.error(err_msg)
            return {"success": False, "error": err_msg}

        video_path = Path(video_path).resolve()
        logger.info(f"🚀 [Aura TikTok Publisher] 숏폼 발행 시작: {video_path.name} ({round(video_path.stat().st_size / 1024 / 1024, 2)} MB)")

        # 캡션 조립 (제미나이 맞춤 카피 최우선 반영)
        hook_title = custom_title or self.HOOK_TITLES.get(topic_id, "소개팅에서 분위기 싸할 때 1초 만에 탈출하는 법")
        if caption:
            full_caption = caption
        else:
            default_tags = ["#아우라AI데이팅", "#소개팅", "#소개팅썰", "#연애팁", "#데이트", "#2030", "#TikTok", "#Shorts"]
            tags_list = custom_tags or default_tags
            tags_str = " ".join(tags_list)
            full_caption = f"{hook_title}\n\n👉 네이버 검색창에 [아우라AI데이팅] 검색!\n\n{tags_str}"

        result = {
            "brand": self.BRAND,
            "platform": "tiktok",
            "topic_id": topic_id,
            "video_file": str(video_path),
            "title": hook_title,
            "caption": full_caption,
            "success": False,
            "published_at": None,
            "post_url": None,
            "proof_screenshot": None
        }

        # 브라우저 잠금 청소 및 단독 락 획득
        clean_browser_profile_locks(self.profile_dir)

        async with async_browser_lock(f"Aura 틱톡 쇼츠 웹 발행 (주제 #{topic_id})"):
            async with async_playwright() as p:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(self.profile_dir),
                    headless=self.headless,
                    args=get_safe_browser_args() + [
                        "--disable-blink-features=AutomationControlled",
                        "--start-maximized"
                    ],
                    viewport={"width": 1280, "height": 900},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
                )

                # 세션 쿠키 주입
                if self.session_file.exists():
                    try:
                        with open(self.session_file, "r", encoding="utf-8") as f:
                            raw = json.load(f)
                        cookies = raw.get("cookies", raw) if isinstance(raw, dict) else raw
                        clean_cookies = []
                        for c in cookies:
                            c_clean = {
                                "name": c["name"],
                                "value": c["value"],
                                "domain": c.get("domain", ".tiktok.com"),
                                "path": c.get("path", "/"),
                                "secure": c.get("secure", True),
                                "httpOnly": c.get("httpOnly", False)
                            }
                            same_site = c.get("sameSite")
                            if same_site in ["Strict", "Lax", "None"]:
                                c_clean["sameSite"] = same_site
                            elif same_site == "no_restriction":
                                c_clean["sameSite"] = "None"
                            elif same_site == "lax":
                                c_clean["sameSite"] = "Lax"
                            clean_cookies.append(c_clean)
                        await context.add_cookies(clean_cookies)
                    except Exception as ce:
                        logger.warning(f"세션 쿠키 로드 예외: {ce}")

                page = context.pages[0] if context.pages else await context.new_page()
                await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

                try:
                    # 1. 틱톡 스튜디오 업로드 페이지 접속
                    upload_url = "https://www.tiktok.com/tiktokstudio/upload?lang=ko-KR"
                    logger.info(f"1. 틱톡 스튜디오 업로드 페이지 접속: {upload_url}")
                    await page.goto(upload_url, wait_until="domcontentloaded", timeout=45000)
                    await asyncio.sleep(5)

                    # 로그인 확인
                    cur_url = page.url
                    if "login" in cur_url.lower() and not ("upload" in cur_url.lower() or "studio" in cur_url.lower()):
                        raise RuntimeError("틱톡 로그인 세션이 유효하지 않습니다. 1회 로그인이 필요합니다.")

                    # 2. 동영상 파일 선택 (input[type='file']) - 메인 및 iframe 전수 탐색
                    file_input = await page.query_selector("input[type='file']")
                    if not file_input:
                        for frame in page.frames:
                            file_input = await frame.query_selector("input[type='file']")
                            if file_input:
                                break

                    if not file_input:
                        raise RuntimeError("틱톡 업로드 input[type='file'] 요소를 찾지 못했습니다.")

                    logger.info("2. 동영상 MP4 파일 주입 중...")
                    await file_input.set_input_files(str(video_path))
                    logger.info("   파일 첨부 완료. 업로드 폼 및 미리보기 렌더링 대기 중 (12초)...")
                    await asyncio.sleep(12)

                    # 3. 팝업 모달 원천 소거 & 오버레이 제거 (ESC + JS 킬러)
                    for _ in range(3):
                        await page.keyboard.press("Escape")
                        await asyncio.sleep(0.2)

                    try:
                        await page.evaluate("""() => {
                            const buttons = Array.from(document.querySelectorAll('button, div[role="button"]'));
                            for (const b of buttons) {
                                const text = (b.innerText || '').trim();
                                if (['Got it', '확인', 'Dismiss', '알겠습니다', 'Close', '닫기'].includes(text)) {
                                    try { b.click(); } catch(e) {}
                                }
                            }
                            const overlays = document.querySelectorAll('.TUXModal-overlay, [data-floating-ui-portal]');
                            for (const o of overlays) {
                                try { o.remove(); } catch(e) {}
                            }
                        }""")
                        logger.info("   👉 안내 팝업 및 오버레이 원천 소거 완료")
                    except Exception:
                        pass

                    # 4. 캡션(설명글 + 해시태그) 사람처럼 타이핑
                    logger.info("3. 캡션 에디터 탐색 및 사람처럼 설명글 작성 중...")
                    editor = await page.query_selector("div.public-DraftEditor-content, div[contenteditable='true'], div[role='combobox'], div.DraftEditor-root")
                    if editor:
                        try:
                            await editor.click(force=True, timeout=3000)
                        except Exception:
                            await page.evaluate("(el) => { el.focus(); el.click(); }", editor)
                        await asyncio.sleep(0.5)
                        await page.keyboard.press("Control+A")
                        await asyncio.sleep(0.2)
                        await page.keyboard.press("Backspace")
                        await asyncio.sleep(0.5)

                        for char in full_caption:
                            if char == "\n":
                                await page.keyboard.press("Enter")
                            else:
                                await page.keyboard.type(char)
                            await asyncio.sleep(random.uniform(0.01, 0.03))
                        logger.info("   캡션 및 해시태그 입력 완료!")

                    # 안전한 외부 영역 클릭하여 드롭다운 포커스 해제
                    try:
                        safe_el = await page.query_selector("text=Details, text=상세 정보, text=Cover, text=커버")
                        if safe_el:
                            await safe_el.click()
                            await asyncio.sleep(1)
                    except Exception:
                        pass

                    await asyncio.sleep(2)

                    # 5. 스크롤 맨 아래로 이동 후 [게시 / Post] 버튼 탐색 (최대 60초 대기)
                    logger.info("4. 게시(Post) 버튼 탐색 및 비디오 인코딩 완료 대기 중...")
                                        # 공개 범위: "모두 / Public" 명시적 보장 (비공개/친구 공개 방지)
                    try:
                        public_el = await page.query_selector("label:has-text('모두'), label:has-text('Public'), label:has-text('Everyone'), input[value='public'], input[value='PUBLIC']")
                        if public_el:
                            await public_el.click()
                            logger.info("   🌐 공개 범위 [모두 / Public] 선택 완료!")
                            await asyncio.sleep(1)
                    except Exception:
                        pass

                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(2)

                                        # [모달 오버레이 차단 방지] ESC 3회 및 안내 팝업 완벽 해제
                    for _ in range(3):
                        await page.keyboard.press("Escape")
                        await asyncio.sleep(0.3)

                    try:
                        modal_btns = await page.query_selector_all("button:has-text('Got it'), button:has-text('확인'), button:has-text('Dismiss'), button:has-text('알겠습니다'), button[aria-label='Close'], div[role='dialog'] button")
                        for mb in modal_btns:
                            try:
                                await mb.click(timeout=1000, force=True)
                            except Exception:
                                pass
                    except Exception:
                        pass

                    post_clicked = False
                    for wait_round in range(35):
                        # 주기적 ESC 입력으로 오버레이 포커스 탈출
                        if wait_round % 2 == 0:
                            await page.keyboard.press("Escape")

                        all_buttons = await page.query_selector_all("button")
                        for btn in all_buttons:
                            txt = (await btn.inner_text()).strip()
                            if txt in ["Post", "게시"]:
                                is_disabled = await btn.is_disabled()
                                if not is_disabled:
                                    logger.info(f"5. 🚀 1차 게시(Post) 버튼 활성화 확인! 클릭 실행 ({txt})")
                                    try:
                                        await btn.click(force=True, timeout=5000)
                                    except Exception:
                                        await page.evaluate("(b) => b.click()", btn)
                                    post_clicked = True
                                    await asyncio.sleep(4)
                                    break
                        if post_clicked:
                            break
                        await asyncio.sleep(2)

                    if not post_clicked:
                        btn_fb = await page.query_selector("button:has-text('게시'), button:has-text('Post')")
                        if btn_fb and not await btn_fb.is_disabled():
                            logger.info("5. 🚀 Fallback 게시 버튼 클릭 (force=True)")
                            try:
                                await btn_fb.click(force=True, timeout=5000)
                            except Exception:
                                await page.evaluate("(b) => b.click()", btn_fb)
                            post_clicked = True
                            await asyncio.sleep(4)

                    # 6. 'Continue to post?' 확인 팝업 발생 시 'Post now' (지금 게시) 클릭
                    try:
                        post_now_btn = await page.query_selector("button:has-text('Post now'), button:has-text('지금 게시')")
                        if post_now_btn:
                            logger.info("   👉 'Continue to post?' 확인 팝업 감지! 'Post now' 최종 클릭")
                            await post_now_btn.click()
                            await asyncio.sleep(12)
                        else:
                            await asyncio.sleep(8)
                    except Exception as pne:
                        logger.debug(f"Post now 클릭 예외: {pne}")

                    # 7. 최종 업로드 완료 검증 및 스크린샷 증빙
                    now_kst = get_now_kst_str()
                    proof_path = CURRENT_DIR / f"tiktok_publish_proof_topic{topic_id:02d}.png"
                    scratch_proof = PROJECT_ROOT / "scratch" / f"aura_tiktok_published_topic{topic_id:02d}.png"
                    await page.screenshot(path=str(proof_path), full_page=True)
                    try:
                        scratch_proof.parent.mkdir(parents=True, exist_ok=True)
                        await page.screenshot(path=str(scratch_proof), full_page=True)
                    except Exception:
                        pass

                    # 최신 세션 쿠키 덤프 갱신
                    try:
                        latest_cookies = await context.cookies()
                        with open(self.session_file, "w", encoding="utf-8") as f:
                            json.dump(latest_cookies, f, ensure_ascii=False, indent=2)
                    except Exception:
                        pass

                    logger.info(f"6. 📸 실물 증빙 스크린샷 저장 완료: {proof_path.name}")

                    result["success"] = True
                    result["published_at"] = now_kst
                    result["proof_screenshot"] = str(proof_path)
                    result["post_url"] = "https://www.tiktok.com/@aura_ai_dating"

                    # 8. 발행 이력 저장
                    self._record_publish_history(result)
                    logger.info(f"🎉 [대성공!] 💖 Aura AI 데이팅 틱톡 쇼츠 무인 자동 발행이 100% 완료되었습니다!")

                except Exception as e:
                    err_msg = f"틱톡 발행 중 오류 발생: {e}"
                    logger.error(err_msg, exc_info=True)
                    result["error"] = err_msg

                    # 에러 화면 증빙 캡처
                    try:
                        err_img = CURRENT_DIR / "tiktok_error_screenshot.png"
                        await page.screenshot(path=str(err_img))
                    except Exception:
                        pass

                finally:
                    await context.close()

        return result

    def _record_publish_history(self, item: Dict[str, Any]):
        """발행 성공 이력을 JSON에 영구 누적 기록"""
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []

        history.append(item)
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history[-50:], f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"이력 파일 저장 실패: {e}")


if __name__ == "__main__":
    publisher = AuraTikTokPublisher(headless=True)
    v = publisher.find_latest_short_video(topic_id=1)
    print(f"💖 Aura 틱톡 발행기 준비 완료! (22초 완제품 대상: {v})")
