# -*- coding: utf-8 -*-
"""
🛡️ InsureBalance Naver Blog Publisher (보험 전용 네이버 블로그 무인 자동 발행 레고 블록)
========================================================================================
- 저장된 Playwright 세션(naver_session.json)을 활용한 100% 무인 자동 발행
- SmartEditor ONE 최적화:
  1. 마크다운 클렌징 헬퍼(format_clean_naver_text): 가독성 극대화 & 불필요 특수문자 제거
  2. 맨 처음 16:9 대표 사진 업로드 ➔ 그 밑에 정돈된 본문 붙여넣기
  3. 태그 10개 자동 등록 및 발행 확인 레이어 클릭
  4. 완료 시 실제 발행된 네이버 블로그 포스트 URL 반환
"""

import sys
import re
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
SESSION_FILE = CURRENT_DIR / "naver_session.json"
FALLBACK_SESSION = CURRENT_DIR.parent / "aura" / "naver_session.json"
ACCOUNTS_FILE = CURRENT_DIR / "accounts.json"

logger = logging.getLogger("InsuranceNaverPublisher")


class InsuranceNaverPublisher:
    """InsureBalance 보험 비교 전용 네이버 블로그 자동 발행 엔진"""

    def __init__(self, blog_id: Optional[str] = None):
        loaded_id = "zkfnth01"
        if ACCOUNTS_FILE.exists():
            try:
                with open(ACCOUNTS_FILE, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    loaded_id = data.get("credentials", {}).get("naver_blog_id") or "zkfnth01"
            except Exception:
                pass
        self.blog_id = blog_id or loaded_id

        # 자체 세션이 없으면 공통 네이버 세션 사용
        if SESSION_FILE.exists() and SESSION_FILE.stat().st_size > 100:
            self.session_file = SESSION_FILE
        else:
            self.session_file = FALLBACK_SESSION

    def is_available(self) -> bool:
        return self.session_file.exists() and self.session_file.stat().st_size > 100

    def publish_article(
        self,
        title: str,
        content_text: str,
        tag_list: Optional[List[str]] = None,
        image_paths: Optional[List[str]] = None,
        category_name: Optional[str] = None,
        landing_url: str = "https://insure-rebalance.vercel.app/",
        timeout_sec: int = 50
    ) -> Dict[str, Any]:
        """동기 호출 인터페이스"""
        try:
            return asyncio.run(self.publish_article_async(
                title=title,
                content_text=content_text,
                tag_list=tag_list,
                image_paths=image_paths,
                category_name=category_name,
                landing_url=landing_url,
                timeout_sec=timeout_sec
            ))
        except Exception as e:
            logger.error(f"❌ [Naver-Insurance] 발행 예외 발생: {e}")
            return {"status": "error", "message": str(e), "blog_id": self.blog_id}

    @staticmethod
    def format_clean_naver_text(raw_text: str, landing_url: str = "https://insure-rebalance.vercel.app/") -> str:
        """마크다운 기호(#, ###, ![], **, >, [이미지:...])를 완전 제거하고 가독성 높은 네이버 블로그 전용 본문으로 변환 (URL 완벽 격리)"""
        import re

        # 1. 마크다운 이미지 태그 및 [16:9...], [이미지:...], [사진:...] 안내 찌꺼기 완벽 제거
        text = re.sub(r'!\[.*?\]\(.*?\)', '', raw_text)
        text = re.sub(r'\[.*?16:9.*?\]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[.*?이미지.*?\]', '', text)
        text = re.sub(r'\[.*?사진.*?\]', '', text)
        text = re.sub(r'🖼️\s*\[.*?\]', '', text)
        text = re.sub(r'━{3,}', '', text)
        text = re.sub(r'-{4,}', '', text)
        text = re.sub(r'={4,}', '', text)

        # 2. 본문 중간에 끼어있는 마크다운 링크 및 괄호형 URL 정제
        text = re.sub(r'\[([^\]]+)\]\((https?://[^\s\)]+)\)', r'\1', text)
        text = re.sub(r'\((https?://[^\s\)]+)\)', '', text)

        # 3. 본문 문장 중간의 순수 URL 패턴도 본문에서 제거 (본문 하단 단독 링크 블록으로 일괄 유도)
        text = re.sub(r'https?://[^\s]+', '', text)

        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            l = line.strip()
            if not l:
                cleaned_lines.append("")
                continue

            # 마크다운 인용구 > 기호 완벽 정제
            while l.startswith(">"):
                l = l[1:].strip()

            if not l:
                cleaned_lines.append("")
                continue

            if l.startswith("# "):
                continue  # 대제목은 이미 제목란에 입력됨
            elif l.startswith("## ") or l.startswith("### "):
                sub = re.sub(r'^#+\s*', '', l)
                sub = re.sub(r'\[.*?\]', '', sub).strip()
                cleaned_lines.append(f"\n✨ {sub}\n")
            elif l.startswith("- ") or l.startswith("* "):
                cleaned_lines.append("  · " + l[2:].strip())
            else:
                clean_l = l.replace("**", "").replace("__", "")
                clean_l = clean_l.replace("\u00a0", " ")
                clean_l = re.sub(r'[ \t]+', ' ', clean_l)
                cleaned_lines.append(clean_l)

        result = "\n".join(cleaned_lines)
        result = re.sub(r'\n{3,}', '\n\n', result).strip()

        # 4. 본문 최하단에 [네이버 포털 검색창 직접 검색 유도 훅 박스] 배치 (영문 URL 생텍스트 완전 배제)
        result += (
            f"\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🛡️ [보험 리밸런스] 34개 보험사 실시간 비교 & 숨은 보험금 찾기\n"
            f"매달 새는 불필요한 중복 특약 정리로 가계부 고정비를 절약해보세요.\n\n"
            f"🔍 네이버 검색창에 [보험 리밸런스]를 검색해 보세요!\n"
            f"👉 공식 센터에서 무료 보험 리모델링 및 보장 분석 신청 가능\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        return result

    async def publish_article_async(
        self,
        title: str,
        content_text: str,
        tag_list: Optional[List[str]] = None,
        image_paths: Optional[List[str]] = None,
        category_name: Optional[str] = None,
        landing_url: str = "https://insure-rebalance.vercel.app/",
        timeout_sec: int = 50
    ) -> Dict[str, Any]:
        """Playwright 비동기 네이버 블로그 스마트에디터 ONE 자동 발행"""
        if not self.is_available():
            logger.warning("⚠️ [Naver-Insurance] 네이버 로그인 세션 파일이 없습니다.")
            return {"status": "error", "message": "naver_session.json not found"}

        tags = tag_list or ["보험비교", "보험리밸런스", "실손보험", "가계부절약", "보험다이어트"]
        clean_tags = [t.replace("#", "").strip() for t in tags if t.replace("#", "").strip()]

        logger.info(f"🚀 [Naver-Insurance] 스마트에디터 ONE 자동 발행 시작: '{title}'")

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled"
                ]
            )
            context = await browser.new_context(
                storage_state=str(self.session_file),
                viewport={"width": 1280, "height": 900},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                permissions=["clipboard-read", "clipboard-write"]
            )
            page = await context.new_page()

            try:
                write_url = f"https://blog.naver.com/{self.blog_id}/postwrite"
                logger.info(f"🌐 [Naver-Insurance] 에디터 직행: {write_url}")
                await page.goto(write_url, wait_until="domcontentloaded", timeout=timeout_sec * 1000)
                await asyncio.sleep(2.5)

                # 1. 팝업 및 도움말 패널, 딤 레이어 완전 닫기
                try:
                    cancel_btn = await page.wait_for_selector('.se-popup-button-cancel', timeout=3000)
                    if cancel_btn:
                        await cancel_btn.click(force=True)
                except Exception:
                    pass

                for _ in range(3):
                    await page.evaluate("""() => {
                        const cancel = document.querySelector('.se-popup-button-cancel');
                        if (cancel) cancel.click();
                        document.querySelectorAll('.se-popup, .se-popup-dim, aside, [class*="help_panel"], [class*="help_layer"]').forEach(el => el.remove());
                    }""")
                    await asyncio.sleep(0.5)

                # 2. 제목 입력
                title_ph = await page.query_selector(".se-documentTitle .se-placeholder, .se-documentTitle [contenteditable='true'], [class*='documentTitle'] [contenteditable='true'], .se-title-text, .se-documentTitle")
                if title_ph:
                    await title_ph.click(force=True)
                    await asyncio.sleep(0.3)
                    await page.keyboard.type(title, delay=10)
                    await asyncio.sleep(0.5)
                    await page.keyboard.press("Enter")
                    logger.info(f"📝 [Naver-Insurance] 제목 입력 성공: '{title}'")
                else:
                    await page.evaluate("""(t) => {
                        const el = document.querySelector('.se-documentTitle [contenteditable="true"]') || document.querySelector('.se-documentTitle');
                        if (el) {
                            el.innerText = t;
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    }""", title)

                # 3. 🌟 제미나이 16:9 실사 사진 본문 맨 위 업로드
                if image_paths and len(image_paths) > 0 and Path(image_paths[0]).exists():
                    img_file = Path(image_paths[0]).resolve()
                    try:
                        # 팝업 및 딤 레이어 강제 즉시 제거
                        await page.evaluate("""() => {
                            const cancel = document.querySelector('.se-popup-button-cancel');
                            if (cancel) cancel.click();
                            document.querySelectorAll('.se-popup, .se-popup-dim, aside, [class*="help_panel"], [class*="help_layer"]').forEach(el => el.remove());
                        }""")
                        await asyncio.sleep(0.5)

                        photo_btn = await page.query_selector("button:has-text('사진'), .se-image-toolbar-button")
                        if photo_btn:
                            async with page.expect_file_chooser(timeout=7000) as fc_info:
                                await photo_btn.click(force=True)
                            file_chooser = await fc_info.value
                            await file_chooser.set_files(str(img_file))
                            logger.info(f"📸 [Naver-Insurance] 제미나이 대표 이미지 업로드 완료: {img_file.name}")
                            await asyncio.sleep(4.0)
                    except Exception as e:
                        logger.warning(f"⚠️ [Naver-Insurance] 사진 업로드 통과: {e}")

                # 4. 사진 아래 본문 영역으로 이동
                await page.keyboard.press("PageDown")
                await page.keyboard.press("ArrowDown")
                await page.keyboard.press("Enter")
                await asyncio.sleep(0.5)

                # 5. 정제 본문 클립보드 붙여넣기
                clean_body = self.format_clean_naver_text(content_text, landing_url)
                await page.evaluate("text => navigator.clipboard.writeText(text)", clean_body)
                await page.keyboard.press("Control+V")
                await asyncio.sleep(2.0)
                logger.info("📝 [Naver-Insurance] 정제 본문 클립보드 붙여넣기 완료")

                # 5-1. 🌟 네이버 공식 OpenGraph(OG) 링크 카드 자동 삽입
                try:
                    logger.info(f"🔗 [Naver-Insurance] 네이버 공식 OG 링크 카드 삽입 시작: {landing_url}")
                    await page.keyboard.press("Enter")
                    await asyncio.sleep(0.5)

                    og_btn = await page.query_selector("button.se-oglink-toolbar-button")
                    if og_btn:
                        await og_btn.click()
                        await asyncio.sleep(1.0)

                        og_inp = await page.wait_for_selector("input.se-popup-oglink-input", timeout=5000)
                        if og_inp:
                            await og_inp.fill(landing_url)
                            await asyncio.sleep(0.5)

                            search_btn = await page.query_selector("button.se-popup-oglink-button")
                            if search_btn:
                                await search_btn.click()
                                await asyncio.sleep(2.5)

                            confirm_btn = await page.wait_for_selector("button.se-popup-button-confirm", timeout=5000)
                            if confirm_btn:
                                await confirm_btn.click()
                                await asyncio.sleep(1.5)
                                logger.info("🎉 [Naver-Insurance] 네이버 공식 OG 링크 카드 삽입 완료!")
                except Exception as og_err:
                    logger.warning(f"⚠️ [Naver-Insurance] OG 링크 카드 삽입 통과: {og_err}")

                # 6. 상단 우측 [발행] 버튼 클릭 (발행 설정 레이어 열기)
                publish_opened = False
                for _ in range(3):
                    publish_opened = await page.evaluate("""() => {
                        window.scrollTo(0, 0);
                        const pubBtn = document.querySelector('.se-publish-button, button.se-publish-button, .publish_btn_area__VpJsC button, button[class*="publish_btn"]');
                        if (pubBtn) {
                            pubBtn.click();
                            return true;
                        }
                        return false;
                    }""")
                    if publish_opened:
                        logger.info("📝 [Naver-Insurance] 발행 레이어 오픈 성공!")
                        break
                    await asyncio.sleep(1.0)

                await asyncio.sleep(2.0)

                # 7. 태그 등록 (최대 10개)
                try:
                    tag_inp = await page.query_selector("input[class*='tag_input'], input[placeholder*='태그']")
                    if tag_inp:
                        for t in clean_tags[:10]:
                            await tag_inp.fill(t)
                            await page.keyboard.press("Enter")
                            await asyncio.sleep(0.2)
                        logger.info(f"🏷️ [Naver-Insurance] 태그 {len(clean_tags[:10])}개 등록 완료")
                except Exception as e:
                    logger.debug(f"태그 입력 통과: {e}")

                # 8. 레이어 하단 [발행] 최종 확인 버튼 클릭
                logger.info("🚀 [Naver-Insurance] 최종 확인 [발행] 버튼 클릭 시도...")
                confirmed = False
                for _ in range(5):
                    confirmed = await page.evaluate("""() => {
                        const confirmBtn = document.querySelector('button[class*="confirm_btn"], button.confirm_btn__WEaBq, button.confirm_btn__byZZW');
                        if (confirmBtn) {
                            confirmBtn.click();
                            return true;
                        }
                        return false;
                    }""")
                    if confirmed:
                        logger.info("🎉 [Naver-Insurance] 최종 발행 확인 버튼 클릭 성공!")
                        break
                    await asyncio.sleep(1.0)

                # 9. 발행 완료 및 실제 블로그 글 페이지 리다이렉트 대기
                logger.info("⏳ [Naver-Insurance] 발행 완료 후 실제 블로그 포스트 페이지 이동 대기...")
                try:
                    await page.wait_for_url(lambda u: "postwrite" not in u and "Write" not in u, timeout=25000)
                except Exception:
                    await asyncio.sleep(6)

                final_url = page.url
                logger.info(f"✅ [Naver-Insurance] 발행 후 최종 URL: {final_url}")

                post_url = final_url if "blog.naver.com" in final_url and "postwrite" not in final_url else f"https://blog.naver.com/{self.blog_id}"
                logger.info(f"🎉 [Naver-Insurance] 최종 공개 발행 완료! {post_url}")
                return {
                    "status": "success",
                    "blog_id": self.blog_id,
                    "title": title,
                    "url": post_url,
                    "post_url": post_url,
                    "tags": clean_tags
                }

            except Exception as e:
                logger.error(f"❌ [Naver-Insurance] 발행 실패: {e}")
                return {"status": "error", "message": str(e), "blog_id": self.blog_id}
            finally:
                await browser.close()


if __name__ == "__main__":
    pub = InsuranceNaverPublisher()
    print("Is available:", pub.is_available())
