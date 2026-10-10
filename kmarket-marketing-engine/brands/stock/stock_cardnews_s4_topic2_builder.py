# -*- coding: utf-8 -*-
"""
StockCardnewsS4Topic2Builder - 🔥 [StockMaster AI 주식 2번 주제: SK하이닉스 3대 주체별 수급 현황 폰뷰]
======================================================================================================
• 역할:
  - 실제 웹앱 SK하이닉스 [수급 현황] 모달(외인/기관 대량 순매수 vs 개미 손절 그래프 & 거래대금) 실물 화면 매립
  - 상단 공식 헤더['📈 StockMaster AI | 외인·기관 실시간 수급 퀀트', '04 / 05 >']
  - 상단 텍스트: [🔥 3대 주체별 실시간 수급 공방] + '외인·기관 긴급 동시 쌍끌이!' + '개미 손절 물량 싹쓸이 매집 포착'
  - 중앙 럭셔리 스마트폰 섀시 프레임 내 실시간 라이브 캡처 화면 배치
  - 하단 넘김 CTA 바 (오렌지 그라데이션)
  - 1080x1350 초고화질 서브픽셀 렌더링
"""

import os
import sys
import base64
import logging
from pathlib import Path
from core.engine.naver_search_bar_component import render_naver_search_bar_html

from typing import Dict, Any, Optional
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

logger = logging.getLogger("StockCardnewsS4Topic2Builder")


class StockCardnewsS4Topic2Builder:
    """📈 StockMaster AI 2번 주제 4번 카드: SK하이닉스 실시간 수급 현황 모달 폰뷰 빌더"""

    BRAND_NAME = "StockMaster AI"
    BRAND_SUB = "외인·기관 실시간 수급 퀀트"

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.asset_path = self.base_dir / "assets" / "stock_topic2_s4_supply_real.png"

    def get_frame_b64(self, custom_asset: Optional[str] = None) -> str:
        target = self.asset_path
        if custom_asset:
            candidate = Path(custom_asset)
            if candidate.exists():
                target = candidate
            elif (self.base_dir / custom_asset).exists():
                target = self.base_dir / custom_asset

        if target.exists():
            with open(target, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        raise FileNotFoundError(f"4번 수급현황 에셋을 찾을 수 없습니다: {target}")

    def render_slide(self, output_png_path: str, copy_data: Dict[str, Any] = None) -> str:
        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        asset_key = copy_data.get("asset_image") if copy_data else None
        img_b64 = self.get_frame_b64(asset_key)

        badge = copy_data.get("badge", "🔥 3대 주체별 실시간 수급 공방") if copy_data else "🔥 3대 주체별 실시간 수급 공방"
        h1_line1 = copy_data.get("headline_line1", "외인·기관 긴급 동시 쌍끌이!") if copy_data else "외인·기관 긴급 동시 쌍끌이!"
        h1_line2 = copy_data.get("headline_line2", "개미 손절 물량 싹쓸이 매집 포착") if copy_data else "개미 손절 물량 싹쓸이 매집 포착"
        subtitle = copy_data.get("subtitle", "외국인 5일 연속 순매수 폭격 • 거래대금 최상위 퀀트 수급 쏠림 확인") if copy_data else "외국인 5일 연속 순매수 폭격 • 거래대금 최상위 퀀트 수급 쏠림 확인"
        cta_text = copy_data.get("cta_text", "👉 옆으로 넘겨서 실시간 퀀트 무료 리포트 받기 (4/5) >") if copy_data else "👉 옆으로 넘겨서 실시간 퀀트 무료 리포트 받기 (4/5) >"
        naver_search_html = render_naver_search_bar_html(brand="stock")

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Stock Master Topic 2 Slide 4 (1080x1350)</title>
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
      font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    body {{
      width: 1080px;
      height: 1350px;
      overflow: hidden;
      background: radial-gradient(circle at 50% 15%, #0d1527 0%, #070b14 55%, #03050a 100%);
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 18px 24px 22px 24px;
      color: #fff;
    }}
    /* 럭셔리 스마트폰 섀시 - 황금 밸런스 튜닝 (1번 주제 동일 규격) */
    .phone-img-container {{
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: visible;
      margin-top: 2px;
      margin-bottom: 4px;
      z-index: 10;
    }}
    .phone-img-wrapper {{
      max-height: 900px;
      width: auto;
      border-radius: 38px;
      overflow: hidden;
      border: 3.5px solid rgba(255, 255, 255, 0.25);
      box-shadow: 0 30px 75px rgba(0, 0, 0, 0.95), 0 0 45px rgba(245, 158, 11, 0.30);
      display: flex;
      background: #0B0E14;
      transform: scale(1.08);
      transform-origin: center center;
    }}
    .phone-img {{
      max-height: 900px;
      width: auto;
      object-fit: contain;
      display: block;
    }}
    .text-glow-yellow {{
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.95), 0 0 2px #000;
    }}
  </style>
</head>
<body>

  <!-- [1. 상단 공식 헤더 바] -->
  <div class="w-full flex justify-between items-center px-4 pt-2">
    <div class="inline-flex items-center gap-2.5 px-5 py-2 rounded-full bg-black/60 border border-[#F59E0B]/50 shadow-lg backdrop-blur-md">
      <span class="text-[#F59E0B] text-base font-black">📈</span>
      <span class="text-white text-base font-extrabold tracking-tight">{self.BRAND_NAME}</span>
      <span class="text-white/40">|</span>
      <span class="text-[#FBBF24] text-base font-bold tracking-tight">{self.BRAND_SUB}</span>
    </div>

    <div class="inline-flex items-center gap-1.5 px-4 py-2 rounded-full bg-black/60 border border-white/20 shadow-lg backdrop-blur-md">
      <span class="text-[#FBBF24] text-base font-black tracking-wider">04 / 05</span>
      <span class="text-white/60 text-base font-bold">&gt;</span>
    </div>
  </div>

  <!-- [2. 상단 헤드라인 & 뱃지] -->
  <div class="w-full px-4 flex flex-col items-center text-center mt-1">
    <div class="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full bg-gradient-to-r from-[#EF4444] to-[#DC2626] border border-red-400/40 shadow-md mb-2">
      <span class="text-white text-base font-extrabold tracking-tight">{badge}</span>
    </div>

    <h2 class="text-3xl font-black leading-snug tracking-tight text-white">
      {h1_line1}<br>
      <span class="text-[#FBBF24] text-4xl text-glow-yellow">{h1_line2}</span>
    </h2>

    <p class="text-white/80 text-lg font-medium mt-1 tracking-tight">
      {subtitle}
    </p>
  </div>

  <!-- [3. 중앙 럭셔리 대형 스마트폰 프레임 & 실시간 웹앱 모달 실측 캡처] -->
  <div class="phone-img-container">
    <div class="phone-img-wrapper">
      <img src="data:image/png;base64,{img_b64}" class="phone-img" alt="SK Hynix Supply Real Modal" />
    </div>
  </div>

  <!-- [4. 하단 스와이프 CTA 배너] -->
    <!-- 하단 네이버 공식 검색창 UI 바 (숏폼 일체형) -->
    {naver_search_html}

</body>
</html>
"""

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350})
            page.set_content(html_content, wait_until="networkidle")
            page.screenshot(path=str(out_path), full_page=True)
            browser.close()

        logger.info(f"🎉 [StockCardnewsS4Topic2Builder] 4번 슬라이드 렌더링 완료: {out_path}")
        return str(out_path)
