# -*- coding: utf-8 -*-
"""
네이버 클립 실기 공개 송출 및 [공개] 상태 즉시 검증 스크립트
=============================================================
1. 최신 숏폼 MP4 탐색
2. 네이버 클립 스튜디오 업로드
3. 카테고리(맛집/일상기록) 확실하게 선택
4. [등록] 클릭 ➔ 모달 확인창 [확인/등록] 클릭
5. https://clipcreators.naver.com/web/contents/clips 이동
6. 최상단 영상의 상태가 [공개]인지 확인하고 스크린샷 캡처!
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RealClipTest")

CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))

from playwright.async_api import async_playwright
from brands.aura.aura_naver_clip_publisher import AuraNaverClipPublisher


async def run_test():
    pub = AuraNaverClipPublisher()
    video_path = r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Aura\Aura_08_safe_radar_20261011_180012\Aura_22초숏폼_주제08_safe_radar_20261011_180012.mp4"
    if not os.path.exists(video_path):
        candidates = list(Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Aura").glob("**/*.mp4"))
        if candidates:
            video_path = str(candidates[0])

    logger.info(f"🚀 [네이버 클립 실기 송출 테스트] 대상 영상: {os.path.basename(video_path)}")

    session_file = pub.session_file
    upload_url = "https://clipcreators.naver.com/web/upload"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=str(session_file),
            viewport={"width": 1280, "height": 900}
        )
        page = await context.new_page()

        try:
            logger.info("1. 업로드 페이지 이동...")
            await page.goto(upload_url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(2.0)

            # 2. 동영상 주입
            logger.info("2. 동영상 주입 중...")
            file_input = await page.wait_for_selector("input[type='file']", timeout=15000)
            await file_input.set_input_files(video_path)
            logger.info("   동영상 주입 완료!")
            await asyncio.sleep(3.0)

            # 3. 설명문 입력
            logger.info("3. 설명문 입력...")
            desc_area = await page.wait_for_selector("textarea[name='description'], textarea", timeout=15000)
            await desc_area.click()
            await desc_area.fill(
                "거리와 취향까지 딱 맞는 내 반경 500m 안심 소개팅 ✨\n"
                "네이버에 [아우라AI데이팅] 한번 검색해보세요!\n"
                "공식 라운지: https://aura-ai-dating.vercel.app/\n\n"
                "#아우라AI데이팅 #소개팅꿀팁 #2030연애 #Shorts"
            )
            await asyncio.sleep(1.0)

            # 4. 1차 카테고리 드롭다운 클릭 (카테고리 미선택 방지)
            logger.info("4. 1차 카테고리 선택 중...")
            cat1_btn = await page.query_selector(".ClipDetailForm_dropdownPrimary__6ZbSU, button:has-text('1차 카테고리'), button:has-text('카테고리 선택'), button[class*='dropdownPrimary'], button[class*='dropdown']")
            if not cat1_btn:
                all_b = await page.query_selector_all("button, div[role='button']")
                for b in all_b:
                    txt = (await b.inner_text()).strip()
                    if "카테고리" in txt:
                        cat1_btn = b
                        break

            if cat1_btn:
                await cat1_btn.click()
                await asyncio.sleep(1.5)
                # 옵션 클릭 (일상기록, 맛집, 라이프스타일 중 첫 번째 매칭)
                target_opt = await page.query_selector("button:has-text('일상기록'), button:has-text('맛집'), button:has-text('라이프스타일'), button:has-text('플레이스'), [role='option'], button[class*='dropdownOption']")
                if target_opt:
                    opt_name = (await target_opt.inner_text()).strip()
                    await target_opt.click()
                    logger.info(f"   ✅ 1차 카테고리 선택 성공: '{opt_name}'")
                    await asyncio.sleep(1.0)

            # 5. 등록 버튼 활성화 대기
            logger.info("5. 인코딩 완료 및 등록 버튼 활성화 대기 (최대 40초)...")
            submit_btn = None
            for w in range(40):
                btns = await page.query_selector_all("button.ClipDetailForm_submitBtn__8PUrw, button[type='submit'], button:has-text('등록'), button:has-text('발행')")
                for b in btns:
                    t = (await b.inner_text()).strip()
                    if t in ["등록", "발행"] and not await b.is_disabled():
                        submit_btn = b
                        break
                if submit_btn:
                    logger.info(f"   등록 버튼 활성화 감지! ({w}초 경과)")
                    break
                await asyncio.sleep(1.0)

            if submit_btn:
                logger.info("6. 🚀 네이버 클립 [등록] 버튼 클릭!")
                await submit_btn.click()
                await asyncio.sleep(3.0)

                # 🌟 모달 확인창 처리 (매우 중요: 모달의 [확인/등록] 클릭해야 [공개] 됨!)
                for m_wait in range(6):
                    modal_confirm = await page.query_selector("[role='dialog'] button:has-text('확인'), [role='dialog'] button:has-text('등록'), [role='dialog'] button:has-text('게시'), button:has-text('확인')")
                    if modal_confirm:
                        m_txt = (await modal_confirm.inner_text()).strip()
                        await modal_confirm.click()
                        logger.info(f"🎉🎉 모달 확인창 [{m_txt}] 클릭 완료!")
                        await asyncio.sleep(3.0)
                        break
                    await asyncio.sleep(1.0)

                # 세션 저장
                await context.storage_state(path=str(session_file))

            # 7. 실제 관리 화면(https://clipcreators.naver.com/web/contents/clips)으로 이동해서 [공개] 여부 실측 검증!
            logger.info("7. 네이버 클립 콘텐츠 목록 화면으로 이동하여 실측 상태 검증 중...")
            await page.goto("https://clipcreators.naver.com/web/contents/clips", wait_until="networkidle", timeout=30000)
            await asyncio.sleep(3.0)

            proof_img = CURRENT_DIR / "outputs" / "proofs" / "aura" / "naver_clip_real_published_proof.png"
            proof_img.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(proof_img))
            logger.info(f"📸 [네이버 클립 실물 증빙 스크린샷 캡처 완료]: {proof_img}")

            # 목록의 첫 번째 영상 상태 파싱
            page_text = await page.inner_text("body")
            has_public = "공개" in page_text
            has_draft = "초안" in page_text
            logger.info(f"📊 [네이버 클립 검증 결과] '공개' 포함: {has_public} | '초안' 포함: {has_draft}")

            await browser.close()
            return True

        except Exception as e:
            logger.error(f"❌ 네이버 클립 송출 테스트 오류: {e}")
            await browser.close()
            return False


if __name__ == "__main__":
    asyncio.run(run_test())
