# -*- coding: utf-8 -*-
"""
StockCardnewsS3Topic1Builder - 📱 [StockMaster AI 주식 3번 카드뉴스: 삼성전자 기업 펀더멘털 & 실적 추이]
=================================================================================================
• 역할:
  - 사용자가 제공한 실제 StockMaster AI 삼성전자 [기본 정보] 모달(펀더멘털 지표 & 최근 실적 추이 바차트) 실물 화면 100% 매립
  - 상단 공식 헤더['📈 StockMaster AI | 외인·기관 실시간 수급 퀀트', '03 / 05 >']
  - 상단 텍스트: [📊 기업 펀더멘털 & 분기 실적 추이] + '영업이익 대폭 턴어라운드 전망!' + '삼성전자 펀더멘털 & 실적 추이'
  - 중앙 럭셔리 스마트폰 섀시 프레임 내 실시간 라이브 캡처 화면 선명 배치
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

logger = logging.getLogger("StockCardnewsS3Topic1Builder")


class StockCardnewsS3Topic1Builder:
    """📈 StockMaster AI 3번 카드: 기업 펀더멘털 & 실적 추이 실측 스마트폰 뷰 빌더"""

    BRAND_NAME = "StockMaster AI"
    BRAND_SUB = "외인·기관 실시간 수급 퀀트"

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.asset_path = self.base_dir / "assets" / "stock_s3_fundamental_real.png"

    def get_frame_b64(self, custom_asset: Optional[str] = None) -> str:
        """실물 스크린샷 에셋을 base64로 로드"""
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
        raise FileNotFoundError(f"3번 펀더멘털 에셋을 찾을 수 없습니다: {target}")

    def render_slide(self, output_png_path: str, copy_data: Dict[str, Any] = None) -> str:
        """Playwright로 1080x1350 규격 3번 카드뉴스 렌더링"""
        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        asset_key = copy_data.get("asset_image") if copy_data else None
        img_b64 = self.get_frame_b64(asset_key)

        badge = copy_data.get("badge", "📊 기업 펀더멘털 & 분기 실적 추이") if copy_data else "📊 기업 펀더멘털 & 분기 실적 추이"
        h1_line1 = copy_data.get("headline_line1", "영업이익 대폭 턴어라운드 전망!") if copy_data else "영업이익 대폭 턴어라운드 전망!"
        h1_line2 = copy_data.get("headline_line2", "삼성전자 펀더멘털 & 실적 분석") if copy_data else "삼성전자 펀더멘털 & 실적 분석"
        subtitle = copy_data.get("subtitle", "ROE 31.4% 폭발적 수익성 & 2026년 분기 영업이익 급증 팩트 데이터") if copy_data else "ROE 31.4% 폭발적 수익성 & 2026년 분기 영업이익 급증 팩트 데이터"
        cta_text = copy_data.get("cta_text", "👉 옆으로 넘겨서 3대 주체 실시간 수급 보기 (3/5) >") if copy_data else "👉 옆으로 넘겨서 3대 주체 실시간 수급 보기 (3/5) >"
        naver_search_html = render_naver_search_bar_html(brand="stock")

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Stock Master Slide 3 (1080x1350)</title>
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

    /* 앰비언트 글로우 */
    .ambient-glow {{
      position: absolute;
      top: -60px;
      left: 50%;
      transform: translateX(-50%);
      width: 880px;
      height: 360px;
      background: radial-gradient(circle, rgba(245, 158, 11, 0.25) 0%, rgba(16, 185, 129, 0.15) 50%, rgba(0, 0, 0, 0) 80%);
      filter: blur(50px);
      z-index: 1;
      pointer-events: none;
    }}

    /* 텍스트 섀도우 */
    .text-headline {{
      color: #FBBF24;
      text-shadow: 0 4px 18px rgba(0, 0, 0, 0.95), 0 0 25px rgba(245, 158, 11, 0.45);
      letter-spacing: -0.03em;
    }}

    /* 럭셔리 스마트폰 섀시 - 황금 밸런스 튜닝 */
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
      background: #FFFFFF;
      transform: scale(1.08);
      transform-origin: center center;
    }}
    .phone-img {{
      max-height: 900px;
      width: auto;
      object-fit: contain;
      display: block;
    }}

    .cta-glow {{
      background: linear-gradient(135deg, #EA580C 0%, #F97316 50%, #F59E0B 100%);
      box-shadow: 0 10px 30px rgba(234, 88, 12, 0.45), 0 0 20px rgba(245, 158, 11, 0.35);
    }}
  </style>
</head>
<body>

  <!-- Ambient Glow -->
  <div class="ambient-glow"></div>

  <!-- 1. Top Header Bar -->
  <div class="flex justify-between items-center z-10 w-full pt-0.5">
    <div class="inline-flex items-center gap-3 bg-slate-900/90 backdrop-blur-md border border-white/25 rounded-full py-2 px-5 shadow-2xl">
      <span class="text-lg">📈</span>
      <span class="text-base font-black tracking-wider text-white">{self.BRAND_NAME}</span>
      <span class="text-sm font-bold text-amber-300 pl-3 border-l border-white/30">{self.BRAND_SUB}</span>
    </div>

    <div class="text-amber-400 font-black text-base bg-slate-900/90 backdrop-blur-md px-5 py-2 rounded-full border border-amber-500/50 shadow-2xl tracking-wider">
      03 / 05 &gt;
    </div>
  </div>

  <!-- 2. Top Text Info Area -->
  <div class="z-10 flex flex-col items-center text-center space-y-1.5 pt-0.5">
    <!-- Category Badge -->
    <div class="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-gradient-to-r from-blue-600 via-indigo-600 to-amber-500 text-white text-xs font-black shadow-lg">
      <span>{badge}</span>
    </div>

    <!-- Main Headline -->
    <h1 class="text-[31px] font-black leading-[1.22] text-white">
      {h1_line1}<br>
      <span class="text-headline">{h1_line2}</span>
    </h1>

    <!-- Subtitle -->
    <p class="text-[16px] font-medium text-slate-300 leading-tight">
      {subtitle}
    </p>
  </div>

  <!-- 3. Center Smartphone App Screen Mockup -->
  <div class="phone-img-container">
    <div class="phone-img-wrapper">
      <img src="data:image/png;base64,{img_b64}" class="phone-img" alt="삼성전자 기업 펀더멘털 및 실적 추이 실측 화면" />
    </div>
  </div>

  <!-- 4. 하단 네이버 공식 검색창 UI 바 (숏폼 일체형) -->
  {naver_search_html}

</body>
</html>"""

        logger.info(f"🎨 [StockCardnewsS3Topic1] 1080x1350 3번 슬라이드 렌더링 시작 -> {out_path.name}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
            page.set_content(html_content, wait_until="networkidle")
            page.screenshot(path=str(out_path), full_page=True)
            browser.close()

        logger.info(f"✅ [StockCardnewsS3Topic1] 3번 슬라이드 렌더링 완료: {out_path}")
        return str(out_path)


if __name__ == "__main__":
    builder = StockCardnewsS3Topic1Builder()
    out_dir = Path(os.environ.get("USERPROFILE", "C:/Users/zkfnt")) / "Desktop" / "한국 카드뉴스_산출물" / "주식" / "[주제01] 삼성전자_수급쌍끌이_20대여성아나운서"
    out_file = out_dir / "slide_3.png"
    res = builder.render_slide(str(out_file))
    print(f"🎉 3번 슬라이드 완성: {res}")
