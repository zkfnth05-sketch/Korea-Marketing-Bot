# -*- coding: utf-8 -*-
"""
Aura Kin Publisher (🤖 Aura 전용 네이버 지식iN Playwright 자동 답변 등록기)
========================================================================================
- 브랜드: Aura (2030 AI 데이팅 & 서울 핫플 매칭)
- 역할:
  1. brands/aura/naver_session.json 쿠키를 이용한 지식iN 자동 세션 마운트
  2. 질문 상세 페이지(https://kin.naver.com/qna/detail.naver?...) 진입
  3. [답변하기] 버튼 클릭 및 스마트에디터에 3박자 킬러 답변 + 출처 입력
  4. 인간형 타이핑 딜레이 및 답변 등록 완료 후 최종 결과 반환
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

logger = logging.getLogger("AuraKinPublisher")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
SESSION_PATH = CURRENT_DIR / "naver_session.json"


class AuraKinPublisher:
    """💖 Aura 전용 네이버 지식iN 자동 답변 등록기 (영구 브라우저 프로필 기반)"""

    BRAND = "aura"
    NAME = "Aura (AI 데이팅)"
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
                headless=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                args=["--no-first-run", "--no-default-browser-check", "--disable-blink-features=AutomationControlled"]
            )

            # 백업용 naver_session.json 쿠키가 있다면 주입
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

            try:
                # 1. 네이버 도메인 간 SSO 세션 워밍업 (지식iN 도메인 쿠키 동기화)
                await page.goto("https://nid.naver.com/user2/help/myInfoV2?lang=ko_KR", wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_timeout(1000)
                await page.goto("https://kin.naver.com", wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_timeout(1000)

                # 2. 질문 상세 페이지 접속
                logger.info(f"🌐 [영구 프로필 지식iN 접속] {question_url}")
                await page.goto(question_url, wait_until="domcontentloaded", timeout=25000)
                await page.wait_for_timeout(2000)

                # 3. [답변하기] 버튼 탐색 및 클릭
                answer_btn = await page.query_selector(
                    "button._answerWriteButton, button.endAnswerRegisterButton, button.button_write, a._answerWriteBtn, a.c-user-outline__link--write"
                )
                if answer_btn:
                    logger.info("🔘 [답변하기] 버튼 클릭 실행...")
                    await answer_btn.click()
                    await page.wait_for_timeout(2500)

                # 로그인 리다이렉트 여부 정밀 검사
                if "nidlogin.login" in page.url:
                    logger.warning("🚨 네이버 로그인 세션이 필요합니다.")
                    await context.close()
                    return {
                        "success": False,
                        "status": "login_required",
                        "message": "네이버 1회 로그인 세션 저장이 필요합니다",
                        "question_url": question_url
                    }

                # 4. 스마트에디터 ONE 영역 탐색 및 본문 작성
                editor_area = await page.query_selector(
                    "div.se-content, div[contenteditable='true'], p.se-placeholder, div.se-component-content"
                )
                if editor_area:
                    logger.info("📝 스마트에디터 입력 영역 포커스 및 작성 시작...")
                    await editor_area.click()
                    await page.wait_for_timeout(500)
                    
                    # 스마트에디터 ONE 문단별 자연스러운 주입 (1500자 이상 고밀도 텍스트 완벽 지원)
                    paragraphs = answer_text.split("\n")
                    for p_idx, para in enumerate(paragraphs):
                        if para.strip():
                            await page.keyboard.insert_text(para)
                            await page.wait_for_timeout(random.randint(40, 80))
                        if p_idx < len(paragraphs) - 1:
                            await page.keyboard.press("Enter")
                            await page.wait_for_timeout(random.randint(30, 60))
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

                    # 6. [답변 등록] 버튼 클릭 (검증된 셀렉터: #answerRegisterButton, ._answerRegisterButton)
                    register_btn = await page.query_selector(
                        "button#answerRegisterButton, button._answerRegisterButton, button.endAnswerButton, button._registerBtn, button.btn_register, button[type='submit']"
                    )
                    if register_btn:
                        logger.info("🚀 [답변 등록하기] 버튼 클릭 실행...")
                        await register_btn.click()
                        await page.wait_for_timeout(4000)
                        logger.info(f"🎉 지식iN 실제 답변 등록 완료! (현재 URL: {page.url})")

                    # 영구 프로필에 실시간 쿠키 자동 동기화
                    cookies_after = await context.cookies()
                    if cookies_after:
                        with open(session_json, "w", encoding="utf-8") as f:
                            json.dump({"cookies": cookies_after}, f, ensure_ascii=False, indent=2)

                    final_url = page.url
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
                logger.warning(f"지식iN 답변 등록 중 예외: {e}")
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
    publisher = AuraKinPublisher()
    sample_url = "https://kin.naver.com/qna/detail.naver?docId=494781951"
    sample_answer = "안녕하세요! 소개팅 첫만남 대화 관련해서 꿀팁 공유해 드립니다..."
    res = publisher.publish_answer(sample_url, sample_answer, "https://aura-ai-dating.vercel.app")
    print("Publish Result:", res)
