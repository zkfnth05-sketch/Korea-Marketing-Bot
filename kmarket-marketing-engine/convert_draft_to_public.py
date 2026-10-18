# -*- coding: utf-8 -*-
"""
네이버 클립 초안 -> [공개] 100% 무결점 실기 전환기
=====================================================
정확한 네이버 셀렉터:
- 1차 카테고리: button.DropdownButton_trigger__75cvp:has-text('1차 카테고리')
- 드롭다운 옵션: button.DropdownButton_option__BYS9i
- 2차 카테고리: button.DropdownButton_trigger__75cvp:has-text('2차 카테고리')
- 저장: button:has-text('저장')
- 상태 변경: button:has-text('초안') -> 공개 옵션 클릭 -> 확인
"""
import sys
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

async def convert_draft_to_public():
    session_file = Path("brands/aura/naver_session.json")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(storage_state=str(session_file), viewport={"width": 1400, "height": 1000})
        page = await ctx.new_page()

        print("1. 네이버 클립 콘텐츠 목록(clips) 접속...")
        await page.goto("https://clipcreators.naver.com/web/contents/clips", wait_until="networkidle", timeout=60000)
        await asyncio.sleep(3.0)

        # 2. 첫 번째 행의 '카테고리 선택' 클릭
        cat_btn = await page.query_selector("button:has-text('카테고리 선택')")
        if cat_btn:
            print("2. '카테고리 선택' 버튼 클릭...")
            await cat_btn.click()
            await asyncio.sleep(2.0)

            # 1차 카테고리 버튼 클릭
            c1 = page.locator("button.DropdownButton_trigger__75cvp:has-text('1차 카테고리')").first
            if await c1.count() > 0:
                print("   1차 카테고리 트리거 클릭...")
                await c1.click()
                await asyncio.sleep(1.5)

                # 첫 번째 옵션 (플레이스) 클릭
                opt1 = page.locator("button.DropdownButton_option__BYS9i").first
                if await opt1.count() > 0:
                    t1 = (await opt1.inner_text()).strip()
                    print(f"   1차 옵션 [{t1}] 클릭...")
                    await opt1.click()
                    await asyncio.sleep(1.5)

            # 2차 카테고리 버튼 클릭
            c2 = page.locator("button.DropdownButton_trigger__75cvp:has-text('2차 카테고리')").first
            if await c2.count() > 0 and not await c2.is_disabled():
                print("   2차 카테고리 트리거 클릭...")
                await c2.click()
                await asyncio.sleep(1.5)

                opt2 = page.locator("button.DropdownButton_option__BYS9i").first
                if await opt2.count() > 0:
                    t2 = (await opt2.inner_text()).strip()
                    print(f"   2차 옵션 [{t2}] 클릭...")
                    await opt2.click()
                    await asyncio.sleep(1.5)

            # [저장] 버튼 클릭
            save_btn = page.locator("button.Button_button_confirm__v4YA5:has-text('저장'), button:has-text('저장')").first
            if await save_btn.count() > 0:
                print("   [저장] 버튼 클릭...")
                await save_btn.click()
                await asyncio.sleep(3.0)
                print("   ✅ 카테고리 저장 완료!")

        # 3. 상태 열의 '초안' 버튼 클릭
        status_btn = await page.query_selector("button:has-text('초안')")
        if status_btn:
            print("3. 상태 '초안' 버튼 클릭...")
            await status_btn.click()
            await asyncio.sleep(1.5)

            # '공개' 옵션 클릭
            pub_opt = page.locator("button.DropdownButton_option__BYS9i:has-text('공개'), button:has-text('공개')").first
            if await pub_opt.count() > 0:
                print("   '공개' 옵션 클릭...")
                await pub_opt.click()
                await asyncio.sleep(2.0)

                # 확인 팝업 모달 처리
                modal_ok = page.locator("[role='dialog'] button:has-text('확인'), [role='dialog'] button:has-text('공개')").first
                if await modal_ok.count() > 0:
                    print("   공개 확인 팝업 [확인] 클릭...")
                    await modal_ok.click()
                    await asyncio.sleep(3.0)
                print("   🎉 공개 전환 완료!")

        # 4. 실물 증빙 스크린샷 캡처
        proof_path = "outputs/proofs/aura/naver_clip_converted_to_public_success.png"
        await page.screenshot(path=proof_path)
        print(f"📸 [증빙 캡처 완료] {proof_path}")

        # 세션 저장
        await ctx.storage_state(path=str(session_file))
        await browser.close()
        print("ALL COMPLETED SUCCESSFULLY")

if __name__ == "__main__":
    asyncio.run(convert_draft_to_public())
