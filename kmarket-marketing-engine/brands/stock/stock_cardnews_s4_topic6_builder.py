# -*- coding: utf-8 -*-
"""
stock_cardnews_s4_topic6_builder.py - 📱 [StockMaster AI 주식 6번 주제: 실시간 1위 종목 AI 분석 근거 폰뷰]
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

logger = logging.getLogger("StockCardnewsS4Topic6Builder")


class StockCardnewsS4Topic6Builder:
    """📈 StockMaster AI 6번 주제 4번 카드: 실시간 1위 종목 AI 분석 근거 폰뷰 빌더"""

    BRAND_NAME = "StockMaster AI"
    BRAND_SUB = "AI 퀀트 리포트"

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.asset_path = self.base_dir / "assets" / "live_sec1_ai_pick.png"
        self.fallback_asset = self.base_dir / "assets" / "stock_s4_quant_board_real.png"

    def get_frame_b64(self, custom_asset: Optional[str] = None) -> str:
        target = self.asset_path
        if custom_asset:
            candidate = Path(custom_asset)
            if candidate.exists():
                target = candidate
            elif (self.base_dir / custom_asset).exists():
                target = self.base_dir / custom_asset

        if not target.exists() and self.fallback_asset.exists():
            target = self.fallback_asset

        if target.exists():
            with open(target, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        raise FileNotFoundError(f"4번 AI 분석 근거 에셋을 찾을 수 없습니다: {target}")

    def render_slide(self, output_png_path: str, copy_data: Dict[str, Any] = None) -> str:
        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        asset_key = copy_data.get("asset_image") if copy_data else None
        img_b64 = self.get_frame_b64(asset_key)

        badge = copy_data.get("badge", "🤖 AI 퀀트 추천 1위 • LG에너지솔루션") if copy_data else "🤖 AI 퀀트 추천 1위 • LG에너지솔루션"
        h1_line1 = copy_data.get("headline_line1", "0.1초 만에 퀀트 스캔 완료!") if copy_data else "0.1초 만에 퀀트 스캔 완료!"
        h1_line2 = copy_data.get("headline_line2", "외인 8.1만주·기관 5.1만주 쌍끌이") if copy_data else "외인 8.1만주·기관 5.1만주 쌍끌이"
        subtitle = copy_data.get("subtitle", "체결강도 142.85% 강력한 단기 낙폭 돌파 주도주 포착 & 목표가 49.3만원") if copy_data else "체결강도 142.85% 강력한 단기 낙폭 돌파 주도주 포착 & 목표가 49.3만원"
        cta_text = copy_data.get("cta_text", "👉 옆으로 넘겨서 실시간 찬반 토론 & 무료 진단 보기 (4/5) >") if copy_data else "👉 옆으로 넘겨서 실시간 찬반 토론 & 무료 진단 보기 (4/5) >"
        naver_search_html = render_naver_search_bar_html(brand="stock")

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Stock Master Topic 6 Slide 4 (1080x1350)</title>
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
    .phone-wrapper {{
      position: relative;
      width: 100%;
      max-width: 620px;
      margin: 0 auto;
      border-radius: 46px;
      padding: 10px;
      background: linear-gradient(145deg, rgba(255,255,255,0.22) 0%, rgba(255,255,255,0.03) 50%, rgba(0,0,0,0.85) 100%);
      box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.9), 0 0 35px rgba(245, 158, 11, 0.15);
      border: 1px solid rgba(255, 255, 255, 0.12);
    }}
    .phone-inner {{
      position: relative;
      width: 100%;
      border-radius: 38px;
      overflow: hidden;
      background: #000;
      border: 2px solid rgba(0, 0, 0, 0.8);
    }}
    .phone-img-wrapper {{
      width: 100%;
      max-height: 900px;
      display: flex;
      align-items: flex-start;
      justify-content: center;
      background: #000;
    }}
    .phone-img {{
      width: 100%;
      height: auto;
      object-fit: cover;
      object-position: top center;
      display: block;
      transform: scale(1.08);
      transform-origin: top center;
    }}
  </style>
</head>
<body>

  <!-- Top Header Bar -->
  <div class="flex justify-between items-center w-full px-2 z-10">
    <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/[0.04] border border-[#F59E0B]/30 backdrop-blur-md">
      <span class="text-[#F59E0B] text-base font-black">📈</span>
      <span class="text-white text-base font-bold">{self.BRAND_NAME}</span>
      <span class="text-white/30 text-xs">|</span>
      <span class="text-[#FBBF24] text-base font-semibold">{self.BRAND_SUB}</span>
    </div>
    <div class="px-4 py-1.5 rounded-full bg-white/[0.04] border border-white/10 text-[#FBBF24] text-sm font-bold tracking-wider">
      04 / 05 &gt;
    </div>
  </div>

  <!-- Main Headline Block -->
  <div class="flex flex-col items-center text-center px-4 z-10 -mt-1">
    <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold mb-1.5">
      {badge}
    </div>
    <h1 class="text-3xl font-extrabold tracking-tight text-white leading-tight">
      {h1_line1} <span class="text-transparent bg-clip-text bg-gradient-to-r from-[#FBBF24] via-[#F59E0B] to-[#D97706]">{h1_line2}</span>
    </h1>
    <p class="text-white/70 text-base font-medium mt-1">
      {subtitle}
    </p>
  </div>

  <!-- Center Luxury Smartphone Viewport -->
  <div class="flex-1 flex items-center justify-center my-auto z-10 overflow-visible py-1">
    <div class="phone-wrapper">
      <div class="phone-inner">
        <div class="phone-img-wrapper">
          <img src="data:image/png;base64,{img_b64}" class="phone-img" alt="AI Analysis Pick Preview" />
        </div>
      </div>
    </div>
  </div>

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

        logger.info(f"🎉 [StockCardnewsS4Topic6Builder] 6번 주제 4번 슬라이드 렌더링 완료: {out_path}")
        return str(out_path)


if __name__ == "__main__":
    builder = StockCardnewsS4Topic6Builder()
    test_out = builder.base_dir / "test_topic6_s4.png"
    builder.render_slide(str(test_out))
