# -*- coding: utf-8 -*-
"""
InsuranceCardnewsS4Builder - 📱 [보험 리밸런스 4번 카드뉴스 34개사 실시간 가격비교 실물 화면 전용 빌더]
=============================================================================================
• 역할:
  - 사용자가 제공한 실제 모바일 웹앱 34개사 실시간 가격비교(15,081원 최저가) 순위표 실물 화면 100% 무손실 매립
  - 상단 공식 헤더['🛡️ 보험 리밸런스 | 34개사 실시간 비교', '04 / 05 >']
  - 상단 텍스트 카피: [📊 대한민국 34개사 전수 공개] + '스팸 전화 0건! 34개 보험사 최저가' + '내 눈으로 0.1초 만에 전수 비교'
  - 중앙 럭셔리 스마트폰 섀시 프레임 내 실물 모바일 순위표 화면 선명 배치
  - 하단 넘김 CTA 바
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

logger = logging.getLogger("InsuranceCardnewsS4Builder")


class InsuranceCardnewsS4Builder:
    """🛡️ 보험 리밸런스 4번 카드 - 34개사 실시간 가격비교 순위표 실물 앱 화면 럭셔리 스마트폰 뷰 빌더"""

    BRAND_NAME = "보험 리밸런스"
    BRAND_SUB = "34개사 실시간 비교"

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.asset_path = self.base_dir / "assets" / "slide4_price_comparison.png"

    def get_frame_b64(self, custom_asset: Optional[str] = None) -> str:
        """실물 스크린샷 에셋을 base64로 로드"""
        target = self.asset_path
        if custom_asset:
            candidate = Path(custom_asset)
            if candidate.exists():
                target = candidate
            elif (self.base_dir.parent.parent / custom_asset).exists():
                target = self.base_dir.parent.parent / custom_asset
            elif (self.base_dir / custom_asset).exists():
                target = self.base_dir / custom_asset

        if target.exists():
            with open(target, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        raise FileNotFoundError(f"4번 앱 화면 에셋을 찾을 수 없습니다: {target}")

    def render_slide(self, output_png_path: str, copy_data: Dict[str, Any] = None) -> str:
        """Playwright로 1080x1350 규격 4번 카드뉴스 렌더링"""
        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        asset_key = copy_data.get("asset_image") if copy_data else None
        img_b64 = self.get_frame_b64(asset_key)

        badge = copy_data.get("badge", "📊 대한민국 34개사 전수 공개") if copy_data else "📊 대한민국 34개사 전수 공개"
        title = copy_data.get("title", "") if copy_data else ""
        if "\n" in title:
            h1_line1, h1_line2 = title.split("\n", 1)
        else:
            h1_line1 = copy_data.get("headline_line1", "스팸 전화 0건! 34개 보험사 최저가") if copy_data else "스팸 전화 0건! 34개 보험사 최저가"
            h1_line2 = copy_data.get("headline_line2", "내 눈으로 0.1초 만에 전수 비교") if copy_data else "내 눈으로 0.1초 만에 전수 비교"
        
        subtitle = copy_data.get("subtitle", "특정사 편파 추천 NO! 34개 모든 보험사 실제 가격표를 투명하게 공개합니다.") if copy_data else "특정사 편파 추천 NO! 34개 모든 보험사 실제 가격표를 투명하게 공개합니다."
        cta_text = copy_data.get("cta_button") or copy_data.get("cta_text", "👉 옆으로 넘겨서 내 보험료 1초 만에 조회하기 (4/5) >") if copy_data else "👉 옆으로 넘겨서 내 보험료 1초 만에 조회하기 (4/5) >"
        naver_search_html = render_naver_search_bar_html(brand="insurance")

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Insurance Slide 4</title>
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
      background: radial-gradient(circle at 50% 18%, #052e1d 0%, #02170e 50%, #010a06 100%);
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 28px 32px 30px 32px;
      color: #fff;
    }}

    /* 앰비언트 글로우 (Deep Forest & Emerald Green) */
    .ambient-glow {{
      position: absolute;
      top: -50px;
      left: 50%;
      transform: translateX(-50%);
      width: 850px;
      height: 350px;
      background: radial-gradient(circle, rgba(16, 185, 129, 0.35) 0%, rgba(5, 150, 105, 0.20) 50%, rgba(0, 0, 0, 0) 80%);
      filter: blur(50px);
      z-index: 1;
      pointer-events: none;
    }}

    /* 텍스트 섀도우 */
    .text-headline {{
      color: #34D399;
      text-shadow: 0 4px 18px rgba(0, 0, 0, 0.95), 0 0 25px rgba(52, 211, 153, 0.5);
      letter-spacing: -0.03em;
    }}

    /* 럭셔리 스마트폰 섀시 */
    .phone-img-container {{
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      margin-top: 6px;
      margin-bottom: 8px;
      z-index: 10;
    }}
    .phone-img-wrapper {{
      max-height: 870px;
      border-radius: 36px;
      overflow: hidden;
      border: 3px solid rgba(255, 255, 255, 0.25);
      box-shadow: 0 25px 65px rgba(0, 0, 0, 0.95), 0 0 40px rgba(16, 185, 129, 0.30);
      display: flex;
      background: #ffffff;
    }}
    .phone-img {{
      max-height: 870px;
      width: auto;
      object-fit: contain;
      display: block;
    }}

    .cta-glow {{
      background: linear-gradient(135deg, #FF6B00 0%, #FF8800 50%, #FFAA00 100%);
      box-shadow: 0 10px 30px rgba(255, 107, 0, 0.5), 0 0 20px rgba(255, 170, 0, 0.35);
    }}
  </style>
</head>
<body>

  <!-- Ambient Glow -->
  <div class="ambient-glow"></div>

  <!-- 1. Top Header Bar -->
  <div class="flex justify-between items-center z-10 w-full pt-1">
    <div class="inline-flex items-center gap-3 bg-slate-900/90 backdrop-blur-md border border-white/25 rounded-full py-2.5 px-5 shadow-2xl">
      <span class="text-lg">🛡️</span>
      <span class="text-base font-black tracking-wider text-white">{self.BRAND_NAME}</span>
      <span class="text-sm font-bold text-purple-300 pl-3 border-l border-white/30">{self.BRAND_SUB}</span>
    </div>

    <div class="text-amber-400 font-black text-base bg-slate-900/90 backdrop-blur-md px-5 py-2.5 rounded-full border border-amber-500/50 shadow-2xl tracking-wider">
      04 / 05 &gt;
    </div>
  </div>

  <!-- 2. Top Text Info Area -->
  <div class="z-10 flex flex-col items-center text-center space-y-2 pt-1">
    <!-- Category Badge -->
    <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-gradient-to-r from-purple-600 via-indigo-600 to-violet-500 text-white text-xs font-black shadow-lg">
      <span>{badge}</span>
    </div>

    <!-- Main Headline -->
    <h1 class="text-[34px] font-black leading-[1.25] text-white">
      {h1_line1}<br>
      <span class="text-headline">{h1_line2}</span>
    </h1>

    <!-- Subtitle -->
    <p class="text-[17px] font-medium text-slate-300 leading-snug">
      {subtitle}
    </p>
  </div>

  <!-- 3. Center Smartphone App Screen Mockup -->
  <div class="phone-img-container">
    <div class="phone-img-wrapper">
      <img src="data:image/png;base64,{img_b64}" class="phone-img" alt="34개사 실시간 가격비교 실물 순위표 화면" />
    </div>
  </div>

  <!-- 4. 하단 네이버 공식 검색창 UI 바 (숏폼 일체형) -->
  {naver_search_html}

</body>
</html>"""

        logger.info(f"🎨 [InsuranceCardnewsS4] 1080x1350 4번 슬라이드 렌더링 시작 -> {out_path.name}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
            page.set_content(html_content, wait_until="networkidle")
            page.screenshot(path=str(out_path), full_page=True)
            browser.close()

        logger.info(f"✅ [InsuranceCardnewsS4] 4번 슬라이드 렌더링 완료: {out_path}")
        return str(out_path)


