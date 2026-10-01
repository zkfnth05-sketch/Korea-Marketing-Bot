# -*- coding: utf-8 -*-
"""
AuraCardnewsS3Topic6Builder - 📱 [Aura 카드뉴스 6번 주제 'AI 첫대화 비서' 3번 숏폼 원본 + 핵심 카피 결합 빌더]
=============================================================================================================
• 역할:
  - 1080x1350 카드뉴스 규격 초고화질 서브픽셀 렌더링
  - 상단 공식 헤더['💖 AURA | 50:50 남녀 황금 성비율', '03 / 05 >']
  - 상단 텍스트 카피: [✨ Aura AI 실시간 추천] + 'Aura에서는 AI가 상대 취향 맞춤 첫마디를 1초 만에 실시간 추천!' + '사진·취미를 분석해 첫 대화의 막막함과 어색함을 완벽하게 없애줍니다.'
  - 중앙 숏폼 엔진 3D 스마트폰 실물 화면(04_app_sim_aura_6.mp4 / 0.2s 추천 문구 3종 UI) 100% 무손실 매립
  - 하단 넘김 CTA 바
"""

import os
import sys
import base64
import logging
from pathlib import Path
from PIL import Image
import cv2
from playwright.sync_api import sync_playwright

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

logger = logging.getLogger("AuraCardnewsS3Topic6Builder")


class AuraCardnewsS3Topic6Builder:
    """Aura 주제 6 3번 카드 - 숏폼 엔진 원본 화면 + 핵심 헤드라인 텍스트 결합 빌더"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.asset_path = self.base_dir / "assets" / "aura_topic6_slide3_screen.png"

    def get_frame_b64(self) -> str:
        """미리 저장된 6번 주제 3번 숏폼 원본 고화질 PNG 에셋을 base64로 로드"""
        if self.asset_path.exists():
            with open(self.asset_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        raise FileNotFoundError(f"6번 3번 숏폼 화면 에셋을 찾을 수 없습니다: {self.asset_path}")

    def render_slide(self, output_png_path: str, copy_data: dict = None) -> str:
        """Playwright로 1080x1350 규격 3번 카드뉴스 렌더링 (제미나이 동적 카피 주입)"""
        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        img_b64 = self.get_frame_b64()

        # 제미나이 동적 카피 또는 기본값
        s3_copy = copy_data.get("slide3", {}) if copy_data else {}
        badge = s3_copy.get("badge", "✨ Aura AI 실시간 추천")
        h1_line1 = s3_copy.get("headline_line1", "Aura에서는 AI가 상대 취향 맞춤")
        h1_line2 = s3_copy.get("headline_line2", "첫마디를 1초 만에 실시간 추천!")
        subtitle = s3_copy.get("subtitle", "사진과 취미를 분석해 첫 대화의 막막함과 어색함을 완벽하게 없애줍니다.")
        cta_text = s3_copy.get("cta_text", "👉 옆으로 넘겨서 실제 대화 결과 보기 (3/5) >")

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Aura Topic 6 Slide 3</title>
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
      background: radial-gradient(circle at 50% 15%, #161825 0%, #090a10 50%, #030406 100%);
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
      width: 800px;
      height: 350px;
      background: radial-gradient(circle, rgba(229, 169, 52, 0.22) 0%, rgba(168, 85, 247, 0.15) 50%, rgba(0, 0, 0, 0) 80%);
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
      margin-top: 4px;
      margin-bottom: 6px;
      z-index: 10;
    }}
    .phone-img {{
      max-height: 940px;
      width: auto;
      object-fit: contain;
      filter: drop-shadow(0 20px 40px rgba(0, 0, 0, 0.95)) drop-shadow(0 0 30px rgba(229, 169, 52, 0.25));
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
      <span class="text-base font-black tracking-wider text-white">AURA</span>
      <span class="text-sm font-bold text-pink-400 pl-3 border-l border-white/30">50:50 남녀 황금 성비율</span>
    </div>

    <div class="text-amber-400 font-black text-base bg-slate-900/90 backdrop-blur-md px-5 py-2.5 rounded-full border border-amber-500/50 shadow-2xl tracking-wider">
      03 / 05 &gt;
    </div>
  </div>

  <!-- 2. Top Text Info Area (Representative Request Copy) -->
  <div class="z-10 flex flex-col items-center text-center space-y-2 pt-1">
    <!-- Category Badge -->
    <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-gradient-to-r from-purple-600 via-pink-600 to-amber-500 text-white text-xs font-black shadow-lg">
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
    <img src="data:image/png;base64,{img_b64}" class="phone-img" alt="Shortform UI 0s" />
  </div>

  <!-- 4. Bottom CTA Bar -->
  <div class="z-10 w-full cta-glow rounded-2xl py-4 flex items-center justify-center gap-2 shadow-2xl">
    <span class="text-white text-xl font-black tracking-wide">
      {cta_text}
    </span>
  </div>

</body>
</html>"""

        logger.info(f"🎨 [AuraCardnewsS3Topic6] 1080x1350 3번 슬라이드(숏폼+카피) 렌더링 시작 -> {out_path.name}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
            page.set_content(html_content, wait_until="networkidle")
            page.screenshot(path=str(out_path), full_page=True)
            browser.close()

        logger.info(f"✅ [AuraCardnewsS3Topic6] 3번 슬라이드 렌더링 완료: {out_path}")
        return str(out_path)

    def produce(self, target_dir: str = None, copy_data: dict = None) -> str:
        """3번 카드뉴스 렌더링 및 저장"""
        if not target_dir:
            from .aura_cardnews_storage import AuraCardnewsStorage
            t_path = AuraCardnewsStorage.create_target_directory(theme_code="smart_opener")
        else:
            t_path = Path(target_dir)
            t_path.mkdir(parents=True, exist_ok=True)

        slide3_path = t_path / "slide_3.png"
        self.render_slide(str(slide3_path), copy_data=copy_data)
        return str(slide3_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    builder = AuraCardnewsS3Topic6Builder()
    builder.produce()
