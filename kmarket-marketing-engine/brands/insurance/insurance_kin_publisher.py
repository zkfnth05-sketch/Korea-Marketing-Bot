# -*- coding: utf-8 -*-
"""
Insurance Kin Publisher (🤖 InsureBalance 전용 네이버 지식iN Playwright 자동 답변 등록기)
========================================================================================
- 브랜드: InsureBalance (보험비교 & AI 리모델링)
- 역할:
  1. brands/insurance/naver_browser_profile 및 naver_session.json 쿠키 자동 마운트
  2. 네이버 도메인 SSO 세션 워밍업 (myInfoV2 ➔ kin.naver.com)
  3. 질문 상세 페이지 진입 및 스마트에디터 ONE에 1,500자 이상 킬러 답변 주입
  4. 지식iN 답변 등록 완료 및 영구 프로필 실시간 동기화
"""

import os
import sys
import json
import time
import random
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright

# UTF-8 콘솔 지원
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("InsuranceKinPublisher")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent


class InsuranceKinPublisher:
    """🛡️ InsureBalance 전용 네이버 지식iN 자동 답변 등록기"""

    BRAND = "insurance"
    NAME = "InsureBalance (보험비교)"
    PROFILE_DIR = CURRENT_DIR / "naver_browser_profile"

    def __init__(self):
        self.PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    async def async_publish_answer(self, question_url: str, answer_text: str, source_url: str = "") -> Dict[str, Any]:
        """
        영구 브라우저 프로필을 통해 실제 지식iN 질문 페이지에 접속하여 답변을 작성하고 등록
        """
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.PROFILE_DIR),
                headless=False,  # 클립보드(pyperclip) 정상 동작을 위해 반드시 False
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized",
                    "--no-first-run",
                    "--no-default-browser-check"
                ]
            )

            session_json = CURRENT_DIR / "naver_session.json"
            if session_json.exists():
                try:
                    with open(session_json, "r", encoding="utf-8") as f:
                        sdata = json.load(f)
                        cookies = sdata.get("cookies", [])
                        if cookies:
                            await context.add_cookies(cookies)
                except Exception:
                    pass

            page = await context.new_page()
            # 다이얼로그(확인/알림창) 자동 승인 핸들러
            page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))

            try:
                # 1. 네이버 도메인 간 SSO 세션 워밍업
                await page.goto("https://nid.naver.com/user2/help/myInfoV2?lang=ko_KR", wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_timeout(1000)
                await page.goto("https://kin.naver.com", wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_timeout(1000)

                # 2. 질문 상세 페이지 접속
                logger.info(f"🌐 [Insurance 영구 프로필 지식iN 접속] {question_url}")
                await page.goto(question_url, wait_until="domcontentloaded", timeout=25000)
                await page.wait_for_timeout(2000)

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
                        "question_url": question_url
                    }
                logger.info("🔘 [답변하기] 버튼 클릭 실행...")
                await answer_btn.click()
                await page.wait_for_timeout(2500)

                # 로그인 리다이렉트 여부 검사
                if "nidlogin.login" in page.url:
                    logger.warning("🚨 InsureBalance 네이버 로그인 세션이 필요합니다.")
                    await context.close()
                    return {
                        "success": False,
                        "status": "login_required",
                        "message": "InsureBalance 네이버 1회 로그인 세션 저장이 필요합니다",
                        "question_url": question_url
                    }

                # 4. 스마트에디터 ONE 영역 탐색 및 본문 작성
                editor_area = await page.query_selector(
                    "div.se-content, div[contenteditable='true'], p.se-placeholder, div.se-component-content"
                )
                if editor_area:
                    logger.info("📝 스마트에디터 입력 영역 포커스 및 작성 시작...")
                    await editor_area.scroll_into_view_if_needed()
                    await editor_area.click()
                    await page.wait_for_timeout(500)

                    # 스마트에디터 ONE 무손실 클립보드 주입 (URL, 이모지, 특수서식 100% 보존)
                    pasted = False
                    try:
                        import pyperclip
                        pyperclip.copy(answer_text)
                        await page.keyboard.press("Control+v")
                        await page.wait_for_timeout(1500)
                        pasted = True
                        logger.info("📋 [클립보드 무손실 붙여넣기 성공] URL 및 보험 센터 카드 서식 100% 보존 주입")
                    except Exception as clip_err:
                        logger.warning(f"⚠️ 클립보드 주입 예외: {clip_err} ➔ 키보드 타이핑 폴백")

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

                    # 6. [답변 등록] 버튼 탐색
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
                            "question_url": question_url
                        }

                    logger.info("🚀 [답변 등록하기] 버튼 클릭 실행...")
                    await register_btn.scroll_into_view_if_needed()
                    await register_btn.click(force=True)
                    await page.wait_for_timeout(6000)

                    # ✅ 등록 성공 검증: URL에 answerNo= 포함 여부 확인
                    # (빈 답변 제출 시 네이버가 alert 표시 후 페이지 유지 → answerNo= 미포함)
                    final_url = page.url
                    published_ok = "answerNo=" in final_url

                    if not published_ok:
                        logger.warning(f"⚠️ 등록 실패 — URL에 answerNo= 미포함 (URL: {final_url}). 빈 내용 또는 네이버 거부")
                        await context.close()
                        return {
                            "success": False,
                            "status": "publish_unverified",
                            "message": "등록 후 answerNo= 미포함 — 빈 내용 제출 또는 네이버 거부",
                            "published_url": final_url,
                            "question_url": question_url
                        }

                    logger.info(f"🎉 InsureBalance 지식iN 답변 등록 완료! (현재 URL: {final_url})")

                    # 영구 프로필 및 session.json 완전 동기화 (쿠키 + 로컬스토리지 영구 보존)
                    try:
                        await context.storage_state(path=str(session_json))
                    except Exception:
                        pass

                    await context.close()
                    return {
                        "success": True,
                        "status": "published",
                        "question_url": question_url,
                        "published_url": final_url,
                        "answer_snippet": answer_text[:100] + "...",
                        "published_at": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                else:
                    logger.warning(f"⚠️ 스마트에디터 영역 미발견 (답변 마감 또는 비공개): {question_url}")
                    await context.close()
                    return {
                        "success": False,
                        "status": "editor_not_found",
                        "question_url": question_url,
                        "message": "답변 마감 또는 에디터 영역 미발견"
                    }

            except Exception as e:
                logger.warning(f"Insurance 지식iN 답변 등록 중 예외: {e}")
                await context.close()
                return {
                    "success": False,
                    "status": "error",
                    "error": str(e),
                    "question_url": question_url
                }

    def publish_answer(self, question_url: str, answer_text: str, source_url: str = "") -> Dict[str, Any]:
        """동기 인터페이스 래퍼"""
        return asyncio.run(self.async_publish_answer(question_url, answer_text, source_url))


if __name__ == "__main__":
    publisher = InsuranceKinPublisher()
    sample_url = "https://kin.naver.com/qna/detail.naver?dirId=40103&docId=494614491"
    sample_answer = "4세대 실손보험 전환 및 3대 진단비 비교 분석 내용..."
    res = publisher.publish_answer(sample_url, sample_answer, "https://insure-rebalance.vercel.app/")
    print("Publish Result:", res)
