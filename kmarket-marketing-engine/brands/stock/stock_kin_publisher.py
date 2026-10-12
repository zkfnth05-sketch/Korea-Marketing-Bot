# -*- coding: utf-8 -*-
"""
StockKinPublisher (🤖 Stock Master (주식 AI) 전용 네이버 지식iN Playwright 자동 답변 등록기)
========================================================================================
- 브랜드: Stock Master (주식 AI)
- 핵심 무결점 원칙:
  1. clean_target_url 원천 정제 (불필요한 &answerNo= 파라미터 사전 제거)
  2. 크롬 SingletonLock 프로세스 충돌 원천 청소
  3. 등록 전후 answer ID 및 URL 실측 비교를 통한 100% 무결점 등록 검증 (거짓 성공 원천 차단)
  4. 네이버 Alert/Confirm 팝업 감지 및 거부 사유 정밀 추적
  5. 영구 프로필 및 session.json 실시간 양방향 동기화
"""

import os
import sys
import json
import time
import random
import logging
import asyncio
import urllib.parse
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
from core.engine.session_integrity import has_auth, load_best_cookies, sanitize_for_playwright, safe_save

logger = logging.getLogger("StockKinPublisher")

SESSION_PATH = CURRENT_DIR / "naver_session.json"


class StockKinPublisher:
    """Stock Master (주식 AI) 전용 네이버 지식iN 자동 답변 등록기 (무결점 실측 검증 엔진)"""

    BRAND = "stock"
    NAME = "Stock Master (주식 AI)"
    PROFILE_DIR = CURRENT_DIR / "naver_browser_profile"

    def __init__(self):
        self.PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def sanitize_question_url(url: str) -> str:
        """URL에서 &answerNo=, &qb= 등 불필요한 앵커 파라미터를 제거하여 순수한 질문 URL 생성"""
        if not url:
            return ""
        parsed = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed.query)
        clean_params = []
        for k in ["dirId", "docId", "d1id"]:
            if k in qs and qs[k]:
                clean_params.append(f"{k}={qs[k][0]}")
        clean_query = "&".join(clean_params)
        if clean_query:
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{clean_query}"
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    async def async_publish_answer(self, question_url: str, answer_text: str, source_url: str = "") -> Dict[str, Any]:
        """
        영구 브라우저 프로필을 통해 실제 지식iN 질문 페이지에 접속하여 답변을 작성하고 등록 (100% 무결점 실측 검증)
        """
        clean_target_url = self.sanitize_question_url(question_url)

        # 1. 크롬 잔여 락 파일 청소 (SingletonLock 충돌 방지)
        for lock_file in ["SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile"]:
            lp = self.PROFILE_DIR / lock_file
            if lp.exists():
                try:
                    lp.unlink()
                except Exception:
                    pass

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.PROFILE_DIR),
                headless=True,  # 🌟 100% 완전 무인 백그라운드 스텔스 모드
                permissions=["clipboard-read", "clipboard-write"],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-first-run",
                    "--no-default-browser-check"
                ]
            )

            # 🛡️ [네이버 영구 세션 보호]: 인증 쿠키 부재 시 .good.json 백업 쿠키 자동 복원
            existing_cookies = await context.cookies()
            session_json = CURRENT_DIR / "naver_session.json"
            if not has_auth("naver", existing_cookies):
                best = load_best_cookies("naver", session_json)
                if best:
                    for c in sanitize_for_playwright(best):
                        try:
                            await context.add_cookies([c])
                        except Exception:
                            pass
                    logger.info(f"   🍪 [네이버 지식iN-{self.brand}] 인증 쿠키 부재 감지 -> .good.json 백업 {len(best)}개 자동 복원 완료")
                elif session_json.exists():
                    try:
                        with open(session_json, "r", encoding="utf-8") as f:
                            sdata = json.load(f)
                            cookies = sdata.get("cookies", [])
                            if cookies:
                                await context.add_cookies(cookies)
                                logger.info("   🍪 [네이버] 세션 쿠키 폴백 복원 완료")
                    except Exception:
                        pass
            else:
                logger.info("   🔐 [네이버 영구 세션 보호] 디스크 프로필 실물 세션 유지")

            page = await context.new_page()

            # 다이얼로그(확인/알림창) 감지 핸들러
            dialog_events = []
            def handle_dialog(dialog):
                msg = f"[{dialog.type}] {dialog.message}"
                logger.warning(f"🚨 [지식iN 팝업 감지] {msg}")
                dialog_events.append({"type": dialog.type, "message": dialog.message})
                asyncio.create_task(dialog.accept())

            page.on("dialog", handle_dialog)

            try:
                # 1. 네이버 도메인 간 SSO 세션 워밍업 (지식iN 도메인 쿠키 동기화)
                await page.goto("https://nid.naver.com/user2/help/myInfoV2?lang=ko_KR", wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_timeout(1000)
                await page.goto("https://kin.naver.com", wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_timeout(1000)

                # 2. 정제된 질문 상세 페이지 접속
                logger.info(f"🌐 [영구 프로필 지식iN 접속] {clean_target_url}")
                await page.goto(clean_target_url, wait_until="domcontentloaded", timeout=25000)
                await page.wait_for_timeout(2000)

                # 🛑 [핵심 중복 방어]: 이미 실제 답변 영역에 동일 브랜드 키워드가 존재하는지 정밀 검사
                try:
                    answer_elements = await page.query_selector_all(".answer-content__list, div.answer-content, div._answerList")
                    answers_text = ""
                    for el in answer_elements:
                        answers_text += (await el.inner_text()) + " "

                    full_check_text = answers_text.lower()
                    if "스톡마스터" in full_check_text or "stock master" in full_check_text or "stockmaster-ai" in full_check_text:
                        logger.warning(f"🛑 [중복 답변 방어] 이미 질문({clean_target_url})에 Stock Master (주식 AI) 답변이 등록되어 있어 중복을 차단합니다.")
                        await context.close()
                        return {
                            "success": False,
                            "status": "already_answered",
                            "published_url": clean_target_url,
                            "message": "이미 Stock Master (주식 AI) 답변이 등록되어 있어 다른 질문으로 이동합니다.",
                            "question_url": clean_target_url
                        }
                except Exception as dup_ex:
                    logger.debug(f"중복 검사 예외 (무시): {dup_ex}")

                # 3. [답변하기] 버튼 탐색 및 클릭
                answer_btn = await page.query_selector(
                    "button._answerWriteButton, button.endAnswerRegisterButton, button.button_write, a._answerWriteBtn, a.c-user-outline__link--write"
                )
                if not answer_btn:
                    logger.warning("⚠️ [답변하기] 버튼 미탐지 — 이미 답변 마감이거나 로그인 세션 만료")
                    await context.close()
                    return {
                        "success": False,
                        "status": "answer_btn_not_found",
                        "message": "[답변하기] 버튼 미탐지: 답변 마감 또는 로그인 세션 만료",
                        "question_url": clean_target_url
                    }
                logger.info("🔘 [답변하기] 버튼 클릭 실행...")
                await answer_btn.click()
                await page.wait_for_timeout(2500)

                # 로그인 리다이렉트 여부 정밀 검사
                if "nidlogin.login" in page.url:
                    logger.warning("⚠️ 네이버 로그인 풀림 감지 -> .good.json 백업 쿠키 주입 후 재진입 시도...")
                    best = load_best_cookies("naver", session_json)
                    if best:
                        for c in sanitize_for_playwright(best):
                            try:
                                await context.add_cookies([c])
                            except Exception:
                                pass
                        await page.goto(clean_target_url, wait_until="domcontentloaded", timeout=25000)
                        await page.wait_for_timeout(2000)
                        answer_btn = await page.query_selector(
                            "button._answerWriteButton, button.endAnswerRegisterButton, button.button_write, a._answerWriteBtn, a.c-user-outline__link--write"
                        )
                        if answer_btn:
                            await answer_btn.click()
                            await page.wait_for_timeout(2500)

                if "nidlogin.login" in page.url:
                    logger.warning("🚨 네이버 로그인 세션이 필요합니다. (백업 복원 후에도 로그인 요구)")
                    await context.close()
                    return {
                        "success": False,
                        "status": "login_required",
                        "message": "네이버 1회 로그인 세션 저장이 필요합니다",
                        "question_url": clean_target_url
                    }

                # 4. 스마트에디터 ONE 영역 탐색 및 본문 작성
                editor_area = await page.query_selector(
                    "div.se-content, div[contenteditable='true'], p.se-placeholder, div.se-component-content"
                )
                if not editor_area:
                    logger.warning(f"⚠️ 스마트에디터 영역 미발견 (답변 마감 또는 비공개): {clean_target_url}")
                    await context.close()
                    return {
                        "success": False,
                        "status": "editor_not_found",
                        "question_url": clean_target_url,
                        "message": "답변 마감 또는 에디터 영역 미발견"
                    }

                logger.info("📝 스마트에디터 입력 영역 포커스 및 작성 시작...")
                await editor_area.scroll_into_view_if_needed()
                await editor_area.click()
                await page.wait_for_timeout(500)

                # 스마트에디터 ONE 무손실 클립보드 주입 (URL, 이모지, 특수서식 100% 보존)
                pasted = False
                try:
                    await page.evaluate("text => navigator.clipboard.writeText(text)", answer_text)
                    await page.keyboard.press("Control+v")
                    await page.wait_for_timeout(1500)
                    pasted = True
                    logger.info("📋 [무인 스텔스 클립보드 무손실 주입 성공] 100% 보존")
                except Exception as clip_err:
                    try:
                        import pyperclip
                        pyperclip.copy(answer_text)
                        await page.keyboard.press("Control+v")
                        await page.wait_for_timeout(1500)
                        pasted = True
                        logger.info("📋 [클립보드 무손실 붙여넣기 성공] 100% 보존 주입")
                    except Exception as clip_err2:
                        logger.warning(f"⚠️ 클립보드 주입 예외: {clip_err2} ➔ 키보드 타이핑 폴백")

                if not pasted:
                    paragraphs = answer_text.split("\n")
                    for p_idx, para in enumerate(paragraphs):
                        if para.strip():
                            await page.keyboard.insert_text(para)
                            await page.wait_for_timeout(random.randint(30, 60))
                        if p_idx < len(paragraphs) - 1:
                            await page.keyboard.press("Enter")
                            await page.wait_for_timeout(random.randint(20, 40))
                    await page.wait_for_timeout(1000)

                # 5. 출처 입력란이 있을 경우
                if source_url:
                    try:
                        source_input = await page.query_selector("input.input_source, input._sourceInput, input[name='source'], input#source")
                        if source_input:
                            await source_input.fill(source_url)
                            await page.wait_for_timeout(500)
                    except Exception:
                        pass

                # 6. [답변 등록] 전 기존 답변 ID 목록 수집 (실측 기준선 확보)
                before_answer_ids = set()
                try:
                    existing_els = await page.query_selector_all("div._answer, div.answer-content__item, [id^='answer_']")
                    for el in existing_els:
                        aid = await el.get_attribute("id")
                        if aid:
                            before_answer_ids.add(aid)
                except Exception:
                    pass
                initial_url = page.url

                # 7. [답변 등록] 버튼 탐색 및 클릭
                register_btn = await page.query_selector(
                    "button#answerRegisterButton, button._answerRegisterButton, button.endAnswerButton, button._registerBtn, button.btn_register, button[type='submit']"
                )
                if not register_btn:
                    logger.warning("⚠️ [답변 등록] 버튼 미탐지 — 에디터 로드 실패 또는 세션 이상")
                    await context.close()
                    return {
                        "success": False,
                        "status": "register_btn_not_found",
                        "message": "[답변 등록] 버튼 미탐지",
                        "question_url": clean_target_url
                    }

                logger.info("🚀 [답변 등록하기] 버튼 클릭 실행...")
                await register_btn.scroll_into_view_if_needed()
                await register_btn.click(force=True)

                # 등록 후 완료 대기 (최대 10초간 URL 변경 또는 신규 답변 DOM 출현 감시)
                new_answer_element_found = False
                new_answer_id = ""
                final_url = page.url

                for wait_step in range(10):
                    await page.wait_for_timeout(1000)
                    final_url = page.url
                    if "answerNo=" in final_url and final_url != initial_url:
                        break

                    now_els = await page.query_selector_all("div._answer, div.answer-content__item, [id^='answer_']")
                    now_ids = set()
                    for el in now_els:
                        aid = await el.get_attribute("id")
                        if aid:
                            now_ids.add(aid)
                    diff = now_ids - before_answer_ids
                    if diff:
                        new_answer_element_found = True
                        new_answer_id = list(diff)[0]
                        break

                # 8. 🔍 [Rule 5 준수: 100% 무결점 실측 검증]
                # A. 거절 팝업(Alert) 발생 여부 체크
                blocking_dialogs = [
                    d for d in dialog_events
                    if any(k in d.get("message", "") for k in ["내용", "초과", "제한", "금칙어", "오류", "확인", "비정상", "문자", "자동등록"])
                ]
                if blocking_dialogs:
                    rejected_msg = blocking_dialogs[0]["message"]
                    logger.warning(f"⚠️ 네이버 지식iN 거부 팝업 발생: {rejected_msg}")
                    await context.close()
                    return {
                        "success": False,
                        "status": "naver_rejected",
                        "message": f"네이버 거부 팝업: {rejected_msg}",
                        "published_url": final_url,
                        "question_url": clean_target_url
                    }

                # B. URL 변경 검증 (초기 URL 대비 신규 answerNo 발급 여부)
                init_qs = urllib.parse.parse_qs(urllib.parse.urlparse(initial_url).query)
                final_qs = urllib.parse.parse_qs(urllib.parse.urlparse(final_url).query)
                init_ans_no = init_qs.get("answerNo", [""])[0]
                final_ans_no = final_qs.get("answerNo", [""])[0]
                url_changed_to_new_answer = bool(final_ans_no and final_ans_no != init_ans_no)

                is_truly_published = url_changed_to_new_answer or new_answer_element_found

                if not is_truly_published:
                    logger.warning(f"⚠️ 등록 실패 — URL 미변경(초기:{init_ans_no} == 최종:{final_ans_no}) 및 신규 답변 엘리먼트 미감지 (URL: {final_url})")
                    await context.close()
                    return {
                        "success": False,
                        "status": "publish_unverified",
                        "message": "답변 등록 미반영 — 버튼 미반응 또는 네이버 거절",
                        "published_url": final_url,
                        "question_url": clean_target_url
                    }

                # 최종 올바른 공개 URL 확정
                if final_ans_no:
                    published_url = final_url
                elif new_answer_id:
                    ans_num = new_answer_id.replace("answer_", "")
                    published_url = f"{clean_target_url}&answerNo={ans_num}"
                else:
                    published_url = final_url

                logger.info(f"🎉 지식iN 실제 답변 등록 검증 성공! (최종 URL: {published_url})")

                # 영구 프로필 및 session.json, .good.json 백업 완전 동기화
                try:
                    await context.storage_state(path=str(session_json))
                    await safe_save("naver", context, session_json, reason="kin_publish_success")
                except Exception:
                    pass

                await context.close()
                return {
                    "success": True,
                    "status": "published",
                    "question_url": clean_target_url,
                    "published_url": published_url,
                    "answer_snippet": answer_text[:100] + "...",
                    "published_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }

            except Exception as e:
                logger.warning(f"지식iN 답변 등록 중 예외: {e}")
                await context.close()
                return {
                    "success": False,
                    "status": "error",
                    "error": str(e),
                    "question_url": clean_target_url
                }

    def publish_answer(self, question_url: str, answer_text: str, source_url: str = "") -> Dict[str, Any]:
        """동기 인터페이스 래퍼"""
        return asyncio.run(self.async_publish_answer(question_url, answer_text, source_url))


if __name__ == "__main__":
    publisher = StockKinPublisher()
    sample_url = "https://kin.naver.com/qna/detail.naver?docId=494781951"
    sample_answer = "테스트 답변 검증 본문입니다."
    res = publisher.publish_answer(sample_url, sample_answer)
    print("Publish Result:", res)
