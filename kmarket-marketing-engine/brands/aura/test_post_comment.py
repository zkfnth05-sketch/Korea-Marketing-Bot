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

async def post_first_comment(video_id: str):
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
            # 일반 동영상 URL로 접속 (댓글창이 항상 하단에 활성화됨)
            watch_url = f"https://www.youtube.com/watch?v={video_id}"
            print(f"Navigating to watch URL: {watch_url}")
            await page.goto(watch_url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(4.0)

            # 아래로 스크롤하여 댓글 섹션 로드 유도
            await page.evaluate("window.scrollBy(0, 500)")
            await asyncio.sleep(2.5)

            # 댓글 입력창 찾기
            print("Looking for comment placeholder...")
            placeholder = page.locator("#placeholder-area, #simplebox-placeholder").first
            if await placeholder.is_visible():
                await placeholder.click()
                await asyncio.sleep(1.5)

            comment_input = page.locator("#contenteditable-root, div[aria-label*='댓글 추가'], div[aria-label*='Add a comment']").first
            if await comment_input.is_visible():
                comment_text = (
                    "📌 영상에서 나온 50:50 완벽 성비 AI 소개팅 라운지는\n"
                    "네이버에 👉 [ 아우라AI데이팅 ] 검색하시면 바로 나옵니다!\n"
                    "(공식 링크: https://aura-ai-dating.vercel.app/)"
                )
                await comment_input.fill(comment_text)
                await asyncio.sleep(1.0)

                submit_btn = page.locator("#submit-button, button[aria-label*='댓글'], button:has-text('댓글'), button:has-text('Comment')").first
                if await submit_btn.is_visible():
                    await submit_btn.click()
                    print("✅ Comment submitted successfully!")
                    await asyncio.sleep(3.0)

            # 결과 스크린샷
            ss = CURRENT_DIR / "yt_comment_proof.png"
            await page.screenshot(path=str(ss))
            print(f"Screenshot saved: {ss}")

        except Exception as e:
            print("Error posting comment:", e)
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(post_first_comment("vzNo0A_nNJs"))
