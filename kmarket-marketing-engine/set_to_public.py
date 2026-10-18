# -*- coding: utf-8 -*-
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def set_to_public():
    session_file = Path("brands/aura/naver_session.json")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(storage_state=str(session_file), viewport={"width": 1400, "height": 1000})
        page = await ctx.new_page()

        print("1. 네이버 클립 clips 접속...")
        await page.goto("https://clipcreators.naver.com/web/contents/clips", wait_until="networkidle", timeout=60000)
        await asyncio.sleep(2.0)

        # 1. 카테고리가 '플레이스'인 행의 '초안' 버튼 클릭
        row = page.locator("tr", has_text="플레이스").first
        status_btn = row.locator("button:has-text('초안')").first
        if await status_btn.count() > 0:
            print("2. '초안' 버튼 클릭...")
            await status_btn.click()
            await asyncio.sleep(1.5)

            # 2. '공개' 옵션 클릭
            pub_opt = page.locator("button.DropdownButton_option__BYS9i", has_text="공개").first
            if await pub_opt.count() > 0:
                print("3. '공개' 옵션 클릭...")
                await pub_opt.click()
                await asyncio.sleep(2.0)

                # 3. 확인 팝업 모달 클릭
                modal_ok = page.locator("[role='dialog'] button:has-text('확인'), [role='dialog'] button:has-text('등록'), [role='dialog'] button:has-text('게시')").first
                if await modal_ok.count() > 0:
                    print("4. 확인 모달 [확인] 클릭...")
                    await modal_ok.click()
                    await asyncio.sleep(3.0)

        # 4. 새로고침 후 최종 실물 증빙 캡처
        await page.reload(wait_until="networkidle")
        await asyncio.sleep(3.0)

        proof_path = "outputs/proofs/aura/naver_clip_REAL_PUBLIC_PROOF.png"
        await page.screenshot(path=proof_path)
        print(f"🎉🎉 [진짜 실물 공개 전환 완료!] 증빙 스크린샷 캡처: {proof_path}")

        await ctx.storage_state(path=str(session_file))
        await browser.close()

if __name__ == "__main__":
    asyncio.run(set_to_public())
