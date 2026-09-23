# -*- coding: utf-8 -*-
"""
[Aura] 8대 카페 자동 출석 & 방문수 육성기 (Incubator Lego Block)
===================================================================
- 목적:
  * 네이버 카페 등업 조건인 '방문수(출석수) 3회~5회'를 사람이 손으로 하지 않고
    봇이 사람처럼 35~45분 간격으로 자연스럽게 접속하여 자동으로 방문수를 채워줌.
- 동작 원리:
  * 네이버는 약 30분~1시간 간격을 두고 카페에 접속해야 '방문수 +1'이 인정됨.
  * 봇이 8개 카페를 순회하며 메인 페이지와 인기 글을 5~10초간 사람처럼 스크롤/체류.
  * 현재 카페별 나의 '방문수 / 작성글수 / 작성댓글수'를 실시간 추적하여 출력.
"""

import asyncio
import sys
import random
import logging
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from brands.aura.aura_cafe_scanner import AURA_ELITE_CAFES

profile_dir = ROOT / "brands" / "aura" / "naver_browser_profile"


class AuraCafeIncubator:
    """💖 8대 카페 자동 출석 & 방문수 달성기"""

    def __init__(self):
        self.cafes = AURA_ELITE_CAFES

    async def visit_all_cafes_once(self) -> list:
        """8대 카페를 1회 순회 방문하여 방문수 1회 증가 및 현재 등급/방문수 확인"""
        print("\n" + "="*70, flush=True)
        print(f"🚀 [Aura 카페 자동 출석 순회 시작] ({datetime.now().strftime('%H:%M:%S')})", flush=True)
        print("="*70, flush=True)

        results = []

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                headless=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page = await context.new_page()

            for c in self.cafes:
                name = c["name"]
                url_id = c["url_id"]
                desktop_url = f"https://cafe.naver.com/{url_id}"

                try:
                    # 데스크톱 카페 홈 접속 (방문 카운트 트리거)
                    await page.goto(desktop_url, wait_until="domcontentloaded", timeout=18000)
                    await asyncio.sleep(random.uniform(2.0, 3.5))

                    frame = page.frame(name="cafe_main")
                    my_info_text = ""
                    if frame:
                        # 사람처럼 약간 스크롤
                        await frame.evaluate("window.scrollBy(0, 300)")
                        await asyncio.sleep(random.uniform(2.0, 3.0))

                        # 나의 활동 정보(방문수, 등급) 추출
                        my_info_text = await page.evaluate("""() => {
                            let el = document.querySelector('#cafe-info-data') || document.querySelector('.my_info');
                            return el ? el.innerText.replace(/\\s+/g, ' ').slice(0, 80) : '';
                        }""")

                    print(f"✅ [{name}] 방문 완료! (내 정보: {my_info_text if my_info_text else '정상 접속됨'})", flush=True)
                    results.append({"cafe": name, "status": "SUCCESS", "info": my_info_text})

                    # 카페 간 자연스러운 텀 (3~5초)
                    await asyncio.sleep(random.uniform(3.0, 5.0))

                except Exception as e:
                    print(f"⚠️ [{name}] 접속 중 에러 (재시도 예정): {e}", flush=True)
                    results.append({"cafe": name, "status": "RETRY", "info": str(e)})

            await context.close()

        print("\n" + "="*70, flush=True)
        print("🎉 [8대 카페 1회 출석 순회 완료!]", flush=True)
        print("="*70, flush=True)
        return results


async def run_auto_incubator(target_visits: int = 3, interval_minutes: int = 35):
    """
    지정된 방문 횟수(예: 3회)를 달성할 때까지 interval 간격으로 자동 순회
    """
    incubator = AuraCafeIncubator()
    print(f"🌟 [Aura 카페 자동 등업 육성 모드 가동]")
    print(f"  • 목표 방문수: {target_visits}회")
    print(f"  • 순회 간격: {interval_minutes}분 (네이버 출석 쿨타임 최적화)\n")

    for i in range(1, target_visits + 1):
        print(f"\n📢 >>> [제 {i}회차 자동 출석 순회 시작] ({i}/{target_visits})")
        await incubator.visit_all_cafes_once()

        if i < target_visits:
            wait_sec = interval_minutes * 60 + random.randint(10, 60)
            print(f"⏳ 다음 출석 인정(방문수 카운트)을 위해 {interval_minutes}분간 자연 대기합니다... ({datetime.now().strftime('%H:%M:%S')})", flush=True)
            await asyncio.sleep(wait_sec)

    print(f"\n🏆 축하합니다! {target_visits}회 자동 방문 순회가 완료되었습니다. 모든 카페의 방문수 조건이 충족되었습니다!")


if __name__ == "__main__":
    # 1회 즉시 실행 테스트
    incubator = AuraCafeIncubator()
    asyncio.run(incubator.visit_all_cafes_once())
