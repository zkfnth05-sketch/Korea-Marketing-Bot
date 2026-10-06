# -*- coding: utf-8 -*-
"""
AuraCardnewsS4Topic8Builder - 📱 [Aura 카드뉴스 8번 주제 4번 숏폼 원본 24시간 지도 레이더 빌더]
================================================================================================
• 역할:
  - 숏폼 8번 엔진의 실제 3D 스마트폰 지도 화면 (04_app_sim_aura_8.mp4 / 6.5s '번개 퀘스트 등록 완료 & 지도 레이더') 100% 무손실 매립
  - 상단 공식 헤더['💖 아우라 AI 데이팅 | 현재 100% 무료 남녀 황금 성비율', '04 / 05 >']
  - 상단 텍스트 카피: [⚡ 24시간 실시간 번개 퀘스트] + '퇴근 후 성수동 카페·가벼운 와인 한잔, 지금 바로 만날 동네 메이트 자동 매칭!' + '지도 위 24시간 동안 번개 핀 노출! 마음 맞는 2030 이성과 즉시 연결'
  - 하단 넘김 CTA 바
  - 1080x1350 초고화질 서브픽셀 렌더링
"""

import os
import sys
import base64
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import cv2
from playwright.sync_api import sync_playwright

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

logger = logging.getLogger("AuraCardnewsS4Topic8Builder")


class AuraCardnewsS4Topic8Builder:
    """Aura 주제 8 4번 카드 - 숏폼 원본 24시간 지도 레이더 UI + 상단 카피 결합 빌더"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.asset_path = self.base_dir / "assets" / "aura_topic8_slide4_screen.png"

    def get_frame_b64(self) -> str:
        """미리 저장된 8번 주제 4번 숏폼 원본 고화질 PNG 에셋을 base64로 로드"""
        if self.asset_path.exists():
            with open(self.asset_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        raise FileNotFoundError(f"8번 4번 숏폼 화면 에셋을 찾을 수 없습니다: {self.asset_path}")

    def render_slide(self, output_png_path: str, copy_data: Dict[str, Any] = None) -> str:
        """Playwright로 1080x1350 규격 4번 카드뉴스 렌더링 (제미나이 동적 카피 주입)"""
        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        img_b64 = self.get_frame_b64()

        # 제미나이 동적 카피 또는 기본값
        badge = copy_data.get("badge", "⚡ 24시간 실시간 번개 퀘스트") if copy_data else "⚡ 24시간 실시간 번개 퀘스트"
        h1_line1 = copy_data.get("headline_line1", "퇴근 후 성수동 카페·가벼운 와인 한잔,") if copy_data else "퇴근 후 성수동 카페·가벼운 와인 한잔,"
        h1_line2 = copy_data.get("headline_line2", "지금 바로 만날 동네 메이트 자동 매칭!") if copy_data else "지금 바로 만날 동네 메이트 자동 매칭!"
        subtitle = copy_data.get("subtitle", "지도 위 24시간 동안 번개 핀 노출! 마음 맞는 2030 이성과 즉시 연결") if copy_data else "지도 위 24시간 동안 번개 핀 노출! 마음 맞는 2030 이성과 즉시 연결"
        cta_text = copy_data.get("cta_text", "👉 옆으로 넘겨서 회원가입 3대 혜택 받기 (4/5) >") if copy_data else "👉 옆으로 넘겨서 회원가입 3대 혜택 받기 (4/5) >"

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Aura Topic 8 Slide 4</title>
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
      background: radial-gradient(circle at 50% 15%, #18201a 0%, #0c140e 50%, #030804 100%);
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 28px 32px 30px 32px;
      color: #fff;
    }}

    /* 앰비언트 글로우 */
    .ambient-glow {{
      position: absolute;
      top: -50px;
      left: 50%;
      transform: translateX(-50%);
      width: 850px;
      height: 350px;
      background: radial-gradient(circle, rgba(234, 179, 8, 0.22) 0%, rgba(16, 185, 129, 0.18) 50%, rgba(0, 0, 0, 0) 80%);
      filter: blur(50px);
      z-index: 1;
      pointer-events: none;
    }}

    /* 텍스트 섀도우 */
    .text-headline {{
      color: #FFF275;
      text-shadow: 0 4px 18px rgba(0, 0, 0, 0.95), 0 0 25px rgba(229, 169, 52, 0.35);
      letter-spacing: -0.03em;
    }}

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
      max-height: 860px;
      border-radius: 28px;
      overflow: hidden;
      border: 2.5px solid rgba(255, 255, 255, 0.18);
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.95), 0 0 35px rgba(234, 179, 8, 0.3);
      display: flex;
    }}
    .phone-img {{
      max-height: 860px;
      width: auto;
      object-fit: cover;
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
      <span class="text-lg">💖</span>
      <span class="text-base font-black tracking-wider text-white">아우라 AI 데이팅</span>
      <span class="text-sm font-bold text-pink-400 pl-3 border-l border-white/30">현재 100% 무료</span>
    </div>

    <div class="text-amber-400 font-black text-base bg-slate-900/90 backdrop-blur-md px-5 py-2.5 rounded-full border border-amber-500/50 shadow-2xl tracking-wider">
      04 / 05 &gt;
    </div>
  </div>

  <!-- 2. Top Text Info Area -->
  <div class="z-10 flex flex-col items-center text-center space-y-2 pt-1">
    <!-- Category Badge -->
    <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-gradient-to-r from-amber-500 via-orange-500 to-emerald-500 text-white text-xs font-black shadow-lg">
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

  <!-- 3. Center Shortform Engine Raw Phone Screen -->
  <div class="phone-img-container">
    <div class="phone-img-wrapper">
      <img src="data:image/png;base64,{img_b64}" class="phone-img" alt="Shortform Safe Radar Map UI" />
    </div>
  </div>

  <!-- 4. Bottom CTA Bar -->
  <div class="z-10 w-full cta-glow rounded-2xl py-4 flex items-center justify-center gap-2 shadow-2xl">
    <span class="text-white text-xl font-black tracking-wide">
      {cta_text}
    </span>
  </div>

 </body>
</html>"""

        logger.info(f"🎨 [AuraCardnewsS4Topic8] 1080x1350 4번 슬라이드(지도 레이더) 렌더링 시작 -> {out_path.name}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
            page.set_content(html_content, wait_until="networkidle")
            page.screenshot(path=str(out_path), full_page=True)
            browser.close()

        logger.info(f"✅ [AuraCardnewsS4Topic8] 4번 슬라이드 렌더링 완료: {out_path}")
        return str(out_path)

    def produce(self, target_dir: str = None, copy_data: Dict[str, Any] = None) -> str:
        """4번 카드뉴스 렌더링 및 저장"""
        if not target_dir:
            from brands.aura.aura_cardnews_storage import AuraCardnewsStorage
            t_path = AuraCardnewsStorage.create_target_directory(theme_code="safe_radar_500m")
        else:
            t_path = Path(target_dir)
            t_path.mkdir(parents=True, exist_ok=True)

        slide4_path = t_path / "slide_4.png"
        self.render_slide(str(slide4_path), copy_data=copy_data)
        return str(slide4_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    builder = AuraCardnewsS4Topic8Builder()
    builder.produce()
