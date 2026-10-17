# -*- coding: utf-8 -*-
"""
Kin Visual Verifier (지식iN 3대 브랜드 실물 답변 시각적 전수 검증 모듈)
====================================================================
- 역할:
  1. 3대 브랜드(Aura, InsureBalance, StockMaster)의 지식iN 최신 발행 URL 자동 탐색
  2. 실제 네이버 웹페이지에 접속하여 우리 봇이 작성한 답변 블록 정밀 탐색
  3. 실물 검증 배지(🟢 [실물 검증 완료]) 및 네온 하이라이트 테두리 자동 주입
  4. 답변 전체 영역(작성자 닉네임, 본문 3박자 솔루션, 공식 검색어 CTA) 고화질 스크린샷 캡처
  5. --gui 옵션 시 실제 크롬 브라우저 창을 띄워 사용자가 직접 모니터에서 눈으로 확인 가능
"""

import sys
import json
import asyncio
import argparse
from pathlib import Path
from playwright.async_api import async_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs" / "proofs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

BRANDS_CONFIG = [
    {
        "id": "aura",
        "name": "💖 Aura AI 데이팅",
        "search_kw": "아우라",
        "official_kw": "아우라AI데이팅",
        "history_file": DATA_DIR / "aura_kin_history.json",
        "color": "#10b981", # Emerald Green
        "fallback_url": "https://kin.naver.com/qna/detail.naver?dirId=61303&docId=495579375&answerNo=4"
    },
    {
        "id": "insurance",
        "name": "🛡️ InsureBalance 보험비교",
        "search_kw": "리밸런스",
        "official_kw": "보험 리밸런스",
        "history_file": DATA_DIR / "insurance_kin_history.json",
        "color": "#3b82f6", # Bright Blue
        "fallback_url": "https://kin.naver.com/qna/detail.naver?dirId=40308&docId=493861200&answerNo=5"
    },
    {
        "id": "stock",
        "name": "📈 StockMaster 주식AI",
        "search_kw": "스톡마스터",
        "official_kw": "스톡마스터 AI",
        "history_file": DATA_DIR / "stock_kin_history.json",
        "color": "#f59e0b", # Amber Gold
        "fallback_url": "https://kin.naver.com/qna/detail.naver?dirId=40102&docId=495584596&answerNo=4"
    }
]


class KinVisualVerifier:
    """3대 브랜드 지식iN 실물 답변 시각적 전수 검증기"""

    def __init__(self, headless: bool = True):
        self.headless = headless

    def get_latest_url(self, binfo: dict) -> tuple[str, str]:
        """히스토리 파일에서 가장 최근에 성공한 지식iN URL 및 질문 제목 동적 추출"""
        hfile = binfo["history_file"]
        if hfile.exists():
            try:
                with open(hfile, "r", encoding="utf-8") as f:
                    hist = json.load(f)
                    # 1순위: 확실하게 published 판정을 받은 건 우선 탐색
                    for item in hist:
                        url = item.get("published_url") or item.get("url")
                        status = item.get("status")
                        title = item.get("question_title") or item.get("title") or "지식iN 질문"
                        if status == "published" and url and "kin.naver.com" in url:
                            return url, title
                    # 2순위: 기타 성공 건
                    for item in hist:
                        url = item.get("published_url") or item.get("url")
                        status = item.get("status")
                        title = item.get("question_title") or item.get("title") or "지식iN 질문"
                        if status in ("publish_unverified", "success") and url and "kin.naver.com" in url and "answerNo=" in url:
                            return url, title
            except Exception:
                pass
        return binfo["fallback_url"], "지식iN 질문"

    async def verify_and_capture_brand(self, page, binfo: dict) -> dict:
        url, title = self.get_latest_url(binfo)
        brand_id = binfo["id"]
        brand_name = binfo["name"]
        color = binfo["color"]
        out_png = OUTPUTS_DIR / f"kin_proof_{brand_id}.png"

        print(f"\n[{brand_name}] 실시간 검증 접속 시작...")
        print(f"  • 대상 질문: {title}")
        print(f"  • 실물 URL: {url}")

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=25000)
            await page.wait_for_timeout(2000)

            # 답변 컨테이너 전체 탐색
            handles = await page.query_selector_all("div.answer-content, div._answerList, div[id*='answer_'], div.se-main-container")
            target = None
            kw = binfo["search_kw"]

            for h in handles:
                try:
                    txt = await h.inner_text()
                    if kw in txt:
                        # answer-content 또는 _answerList 최상위 블록 선택
                        target = h
                        break
                except Exception:
                    continue

            if not target:
                print(f"  ❌ [{brand_name}] 답변 본문에서 키워드('{kw}')를 포함한 답변 블록을 찾지 못했습니다.")
                return {"brand": brand_id, "success": False, "url": url}

            # 눈에 띄는 하이라이트 테두리 및 검증 배지 삽입
            banner_html = f"🟢 [네이버 지식iN 실물 검증 완료] {brand_name} 공식 봇 채택/등록 답변"
            await page.evaluate("""([el, color, bannerText]) => {
                const parent = el.closest('div.answer-content') || el.closest('div._answerList') || el;
                parent.style.border = `4px solid ${color}`;
                parent.style.boxShadow = `0 0 35px ${color}88`;
                parent.style.borderRadius = "14px";
                parent.style.padding = "20px";
                parent.style.backgroundColor = "#ffffff";
                
                const banner = document.createElement('div');
                banner.innerHTML = bannerText;
                banner.style.backgroundColor = color;
                banner.style.color = '#ffffff';
                banner.style.fontWeight = 'bold';
                banner.style.padding = '10px 18px';
                banner.style.borderRadius = '8px';
                banner.style.marginBottom = '18px';
                banner.style.fontSize = '15px';
                banner.style.letterSpacing = '-0.5px';
                parent.insertBefore(banner, parent.firstChild);
                
                parent.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }""", [target, color, banner_html])

            await page.wait_for_timeout(1000)

            # 최상위 답변 요소 핸들 다시 획득
            parent_handle = await target.evaluate_handle("el => el.closest('div.answer-content') || el.closest('div._answerList') || el")
            if parent_handle:
                await parent_handle.as_element().screenshot(path=str(out_png))
            else:
                await target.screenshot(path=str(out_png))

            print(f"  ✅ [{brand_name}] 실물 캡처 완료! -> {out_png.name} (저장 완료)")

            if not self.headless:
                print(f"  👀 [화면 대기] 모니터에서 직접 확인하세요! (3초간 유지)")
                await page.wait_for_timeout(3500)

            return {
                "brand": brand_id,
                "name": brand_name,
                "success": True,
                "url": url,
                "title": title,
                "image_path": str(out_png)
            }

        except Exception as e:
            print(f"  ❌ [{brand_name}] 검증 예외 발생: {e}")
            return {"brand": brand_id, "success": False, "error": str(e), "url": url}

    async def run_all(self) -> list:
        print("\n" + "="*70)
        print("🔍 [지식iN 3대 브랜드 실물 답변 시각적 전수 검증 가동]")
        print(f"   모드: {'🖥️ 실제 브라우저 팝업(GUI)' if not self.headless else '🤖 고화질 증빙 캡처(Headless)'}")
        print("="*70)

        results = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                args=["--start-maximized" if not self.headless else "--no-sandbox"]
            )
            context = await browser.new_context(
                viewport={"width": 1280, "height": 950} if self.headless else None,
                no_viewport=True if not self.headless else False,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            for binfo in BRANDS_CONFIG:
                res = await self.verify_and_capture_brand(page, binfo)
                results.append(res)

            await browser.close()

        print("\n" + "="*70)
        print("🏆 [지식iN 시각적 실물 검증 종합 결과]")
        print("="*70)
        for r in results:
            st = "🟢 실물 확인 & 캡처 완료" if r.get("success") else "🔴 실패"
            print(f"  • {r.get('name', r.get('brand')):<20}: {st}")
            if r.get("success"):
                print(f"    - URL: {r.get('url')}")
                print(f"    - 캡처: {r.get('image_path')}")
        print("="*70 + "\n")
        return results


def main():
    parser = argparse.ArgumentParser(description="지식iN 3대 브랜드 실물 답변 시각적 검증")
    parser.add_argument("--gui", "--show", action="store_true", help="실제 브라우저 창을 화면에 띄워 눈으로 직접 확인")
    args = parser.parse_args()

    verifier = KinVisualVerifier(headless=not args.gui)
    asyncio.run(verifier.run_all())


if __name__ == "__main__":
    main()
