# -*- coding: utf-8 -*-
"""
StockCardnewsS3Topic4Builder - 📱 [StockMaster AI 주식 4번 주제: 1위 종목 수급 & 체결강도 실측 폰뷰]
======================================================================================================
• 역할:
  - 실제 웹앱 주도주 실시간 수급 & 체결강도 실물 화면 매립
  - 상단 공식 헤더['📈 StockMaster AI | AI 체결 가속도 엔진', '03 / 05 >']
  - 상단 텍스트: [📊 1위 종목 실시간 수급 & 체결강도] + '외인·기관 쌍끌이 순매수 + 체결강도 148% 돌파'
  - 중앙 럭셔리 대형 스마트폰 섀시 프레임 내 실시간 라이브 캡처 화면 배치 (scale 1.08)
  - 하단 넘김 CTA 바 (오렌지 그라데이션)
  - 1080x1350 초고화질 서브픽셀 렌더링
"""

import os
import sys
import base64
import logging
from pathlib import Path
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

logger = logging.getLogger("StockCardnewsS3Topic4Builder")


class StockCardnewsS3Topic4Builder:
    """📈 StockMaster AI 4번 주제 3번 카드: 1위 종목 실시간 수급 & 체결강도 폰뷰 빌더"""

    BRAND_NAME = "StockMaster AI"
    BRAND_SUB = "AI 체결 가속도 엔진"

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.asset_path = self.base_dir / "assets" / "stock_topic4_s3_samsungea_tech.png"
        self.fallback_asset = self.base_dir / "assets" / "stock_s2_supply_real.png"

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
        raise FileNotFoundError(f"3번 수급/체결강도 에셋을 찾을 수 없습니다: {target}")

    def render_slide(self, output_png_path: str, copy_data: Dict[str, Any] = None) -> str:
        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        asset_key = copy_data.get("asset_image") if copy_data else None
        img_b64 = self.get_frame_b64(asset_key)

        badge = copy_data.get("badge", "📊 삼성E&A 실시간 기술 지표") if copy_data else "📊 삼성E&A 실시간 기술 지표"
        h1_line1 = copy_data.get("headline_line1", "당일 체결강도 120.69% 돌파!") if copy_data else "당일 체결강도 120.69% 돌파!"
        h1_line2 = copy_data.get("headline_line2", "▲ 매수 우위 안정 구간 안착") if copy_data else "▲ 매수 우위 안정 구간 안착"
        subtitle = copy_data.get("subtitle", "RSI 40.3pt 중립 & 볼린저 밴드 안정 구간! 5일 이격도 101.92% 수렴") if copy_data else "RSI 40.3pt 중립 & 볼린저 밴드 안정 구간! 5일 이격도 101.92% 수렴"
        cta_text = copy_data.get("cta_text", "👉 옆으로 넘겨서 외인·기관 쌍끌이 순매수 팩트 보기 (3/5) >") if copy_data else "👉 옆으로 넘겨서 외인·기관 쌍끌이 순매수 팩트 보기 (3/5) >"

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Stock Master Topic 4 Slide 3 (1080x1350)</title>
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
      box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.9), 0 0 35px rgba(56, 189, 248, 0.15);
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
    <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/[0.04] border border-[#38BDF8]/30 backdrop-blur-md">
      <span class="text-[#38BDF8] text-base font-black">📈</span>
      <span class="text-white text-base font-bold">{self.BRAND_NAME}</span>
      <span class="text-white/30 text-xs">|</span>
      <span class="text-[#38BDF8] text-base font-semibold">{self.BRAND_SUB}</span>
    </div>
    <div class="px-4 py-1.5 rounded-full bg-white/[0.04] border border-white/10 text-[#38BDF8] text-sm font-bold tracking-wider">
      03 / 05 &gt;
    </div>
  </div>

  <!-- Main Headline Block -->
  <div class="flex flex-col items-center text-center px-4 z-10 -mt-1">
    <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-bold mb-1.5">
      {badge}
    </div>
    <h1 class="text-3xl font-extrabold tracking-tight text-white leading-tight">
      {h1_line1} <span class="text-transparent bg-clip-text bg-gradient-to-r from-[#38BDF8] via-[#0284C7] to-[#0369A1]">{h1_line2}</span>
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
          <img src="data:image/png;base64,{img_b64}" class="phone-img" alt="Supply Preview" />
        </div>
      </div>
    </div>
  </div>

  <!-- Bottom CTA Swipe Banner -->
  <div class="w-full z-10">
    <div class="w-full py-3.5 rounded-xl bg-gradient-to-r from-[#EA580C] via-[#F97316] to-[#F59E0B] shadow-lg shadow-orange-500/20 flex items-center justify-center border border-white/20">
      <span class="text-white text-lg font-black tracking-wide">
        {cta_text}
      </span>
    </div>
  </div>

</body>
</html>
"""

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350})
            page.set_content(html_content, wait_until="networkidle")
            page.screenshot(path=str(out_path), full_page=True)
            browser.close()

        logger.info(f"🎉 [StockCardnewsS3Topic4Builder] 4번 주제 3번 슬라이드 렌더링 완료: {out_path}")
        return str(out_path)


if __name__ == "__main__":
    builder = StockCardnewsS3Topic4Builder()
    out = Path(r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\주식\[주제04] 체결가속도_호가창급등_실시간포착\slide_3.png")
    builder.render_slide(str(out))
    print(f"🎉 3번 슬라이드 렌더링 완료: {out}")
