import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

CURRENT_DIR = Path(r"c:\Users\zkfnt\Desktop\한국 마케팅봇\kmarket-marketing-engine\brands\aura")
PROJECT_ROOT = CURRENT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.engine.browser_guard import clean_browser_profile_locks, get_safe_browser_args
from core.engine.session_integrity import ensure_auth_cookies

PROFILE_DIR = CURRENT_DIR / "youtube_chrome_profile"
SESSION_FILE = CURRENT_DIR / "youtube_session.json"

async def bind_related_video(video_id: str):
    clean_browser_profile_locks(PROFILE_DIR)
    async with async_playwright() as p:
        browser_args = get_safe_browser_args([
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check"
        ])
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=True,
            args=browser_args,
            viewport={"width": 1400, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        await ensure_auth_cookies("youtube", context, SESSION_FILE)
        page = context.pages[0] if context.pages else await context.new_page()
        try:
            edit_url = f"https://studio.youtube.com/video/{video_id}/edit"
            print(f"Opening edit page: {edit_url}")
            await page.goto(edit_url, wait_until="networkidle", timeout=45000)
            await asyncio.sleep(4.0)

            # 건너뛰기 팝업 처리
            await page.evaluate("""() => {
                const els = Array.from(document.querySelectorAll('a, button'));
                const skip = els.find(e => e.innerText && e.innerText.includes('건너뛰기'));
                if (skip) { skip.click(); }
            }""")
            await asyncio.sleep(2.0)

            # 우측 패널 또는 세부정보에서 '관련 동영상' 찾기
            print("Searching for '관련 동영상' button...")
            related_btn = page.locator("ytcp-video-metadata-editor-related-video, [aria-label*='관련 동영상'], [aria-label*='Related video'], ytcp-text-dropdown-trigger:has-text('관련 동영상'), div:has-text('관련 동영상')").first
            
            # 스크린샷 1
            ss1 = CURRENT_DIR / "yt_edit_before.png"
            await page.screenshot(path=str(ss1))
            print(f"Screenshot before binding: {ss1}")

            # '관련 동영상' 요소 클릭 시도
            found = False
            triggers = [
                "ytcp-video-metadata-editor-related-video",
                "[aria-label*='관련 동영상']",
                "button:has-text('관련 동영상')",
                "ytcp-chip:has-text('관련 동영상')",
                "ytcp-button:has-text('관련 동영상')",
                "div[role='button']:has-text('관련 동영상')"
            ]
            for sel in triggers:
                loc = page.locator(sel).first
                if await loc.count() > 0 and await loc.is_visible():
                    print(f"Found trigger with selector: {sel}")
                    await loc.scroll_into_view_if_needed()
                    await loc.click(force=True)
                    found = True
                    break

            if not found:
                # JS 탐색 및 클릭
                clicked_js = await page.evaluate("""() => {
                    const all = Array.from(document.querySelectorAll('*'));
                    const target = all.find(el => el.innerText && el.innerText.trim() === '관련 동영상' && (el.tagName === 'DIV' || el.tagName === 'BUTTON' || el.tagName === 'SPAN' || el.tagName === 'YTCP-BUTTON'));
                    if (target) {
                        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        target.click();
                        return true;
                    }
                    return false;
                }""")
                print("JS click result:", clicked_js)
                found = clicked_js

            await asyncio.sleep(3.0)

            # 다이얼로그(ytcp-video-picker-dialog)가 떴는지 확인
            picker = page.locator("ytcp-video-picker-dialog").first
            if await picker.count() > 0:
                print("Picker dialog opened! Selecting official bridge video...")
                # 아우라 또는 공식 앱 카드를 클릭
                card = page.locator("ytcp-video-picker-dialog ytcp-entity-card:has-text('아우라'), ytcp-video-picker-dialog div[role='row']:has-text('아우라'), ytcp-video-picker-dialog tr:has-text('아우라'), ytcp-video-picker-dialog .video-title").first
                if await card.count() > 0:
                    await card.click(force=True)
                    print("Bridge video selected in dialog!")
                    await asyncio.sleep(2.0)

                    # 저장 버튼 클릭
                    save_btn = page.locator("#save-button, ytcp-button#save-button, button:has-text('저장'), button:has-text('Save')").first
                    if await save_btn.count() > 0 and await save_btn.is_visible():
                        await save_btn.click(force=True)
                        print("Saved changes!")
                        await asyncio.sleep(3.0)
            else:
                print("Picker dialog not found.")

            ss2 = CURRENT_DIR / "yt_edit_after.png"
            await page.screenshot(path=str(ss2))
            print(f"Screenshot after: {ss2}")

        except Exception as e:
            print("Error:", e)
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(bind_related_video("vzNo0A_nNJs"))
