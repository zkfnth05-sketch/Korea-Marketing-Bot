# -*- coding: utf-8 -*-
"""
AuraCardnewsS1Topic7Builder - 📱 [Aura 카드뉴스 7번 주제 'AI 매력상 & 관상/궁합 진단' 1번 표지 Wan 2.1 자율 생성 빌더]
========================================================================================================================
• 역할:
  - 숏폼 7번의 인물(24세 매혹적인 여우/고양이상 미녀), 의상(블랙 골지 니트), 배경(따뜻한 갤러리 카페) 스펙 100% 계승
  - 카드뉴스 생성 시마다 Wan 2.1 T2I를 호출하여 매번 새롭고 독창적인 초고화질 실사 인물 사진을 자율 생성
  - 1080x1350 카드뉴스 규격 초고화질 서브픽셀 렌더링
  - 상단 공식 헤더['💖 아우라 AI 데이팅 | 현재 100% 무료 남녀 황금 성비율', '01 / 05 >'] + 카테고리 배지 + 옐로우 헤드라인 + 3대 불릿 + 하단 넘김 CTA 바 일체형 렌더링
"""

import os
import sys
import time
import base64
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image
from playwright.sync_api import sync_playwright

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from core.engine.wan_pipeline_client import WanPipelineClient

logger = logging.getLogger("AuraCardnewsS1Topic7Builder")


class AuraCardnewsS1Topic7Builder:
    """Aura 주제 7(AI 매력상 & 관상/궁합 진단) 1번 표지 카드 전문 빌더 (Wan 2.1 T2I 실사 자율 생성)"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.wan_client = WanPipelineClient()

    def generate_s1_photo(self, outfit: dict = None, seed: int = None) -> Path:
        """Wan 2.1 T2I로 7번 주제 전용 매혹적인 여우상 미녀 모델 실사 신규 생성 (의상 동기화 주입)"""
        if seed is None:
            seed = int(time.time() * 1000) % 100000000

        if outfit is None:
            from .aura_cardnews_topic7_wardrobe import get_wardrobe
            outfit = get_wardrobe()

        clothing_prompt = outfit.get("s1_clothing", "wearing a chic stylish minimalist black ribbed long-sleeve knit top, modern sophisticated Seoul date-night fashion")
        outfit_name = outfit.get("name_ko", "기본 의상")

        pos = (
            "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
            "solo 1person female, perfectly centered in frame, frontal portrait view looking directly into camera with captivating charismatic gaze, "
            "an exceptionally gorgeous glamorous 24-year-old Korean woman with a breathtakingly attractive fox-like and feline cat-like facial aesthetic, "
            "captivating alluring almond-shaped dark eyes with subtle elegant winged eyeliner, sculpted sharp high cheekbones, delicate cute petite button nose, flawless sculpted V-line jawline, "
            "perfect 8-head-high golden ratio model proportions, small refined head and face size, slender elegant long neck, graceful collarbone, "
            "flawless luminous porcelain glass skin with soft natural peach cheek glow, authentic fine real human skin texture with visible pores, "
            "natural full lips gently closed together with a subtle alluring confident calm smile, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "sleek glossy dark espresso brown long layered hair falling gracefully over shoulders, "
            f"{clothing_prompt}, "
            "seated gracefully at a marble table with folded hands resting naturally, "
            "upscale cozy modern cafe lounge interior with warm glowing art frame lights and golden ambient lighting in background in tack sharp f/11 focus, "
            "candid medium cowboy portrait shot showing upper body, shoulders, and chest, generous headroom above, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, Apple iPhone 15 Pro Smart HDR photo."
        )
        neg = (
            "open mouth, parted lips, visible teeth, showing teeth, laughing, grinning, smiling wide, "
            "ugly face, old woman, middle aged, chubby, fat face, broad jaw, double chin, distorted features, bad eyes, asymmetric face, "
            "doll, doll face, porcelain skin, plastic skin, airbrushed skin, beauty filter, skin smoothing, "
            "blurry, lens blur, out of focus, bokeh blur, shallow depth of field, deformed hands, extra fingers, missing fingers, bad fingers, "
            "cartoon, anime, 3d render, cgi, illustration, drawing, watermark, text, male, man, two people"
        )

        logger.info(f"🎨 [AuraCardnewsS1Topic7] 7번 주제 1번 표지 모델 Wan 2.1 신규 생성 시작 (의상: {outfit_name}, Seed={seed})...")
        raw_path = self.wan_client.generate_t2i_master(
            positive_prompt=pos,
            negative_prompt=neg,
            width=832,
            height=1216,
            seed=seed,
            prefix="aura_topic7_s1_fox_charm"
        )
        logger.info(f"✅ [AuraCardnewsS1Topic7] 7번 표지 신규 사진 생성 완료: {raw_path}")
        return Path(raw_path)

    def render_slide(self, photo_path: Path, output_png_path: str, copy_data: Dict[str, Any] = None) -> str:
        """Playwright로 1080x1350 카드뉴스 1번 표지 렌더링 (제미나이 동적 카피 주입)"""
        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(str(photo_path), "rb") as f:
            photo_b64 = base64.b64encode(f.read()).decode("utf-8")

        # 제미나이 동적 카피 또는 기본값
        badge = copy_data.get("badge", "🔥 2030 관상/매력 진단") if copy_data else "🔥 2030 관상/매력 진단"
        h1_line1 = copy_data.get("headline_line1", "내 얼굴은 여우상일까 강아지상일까?") if copy_data else "내 얼굴은 여우상일까 강아지상일까?"
        h1_line2 = copy_data.get("headline_line2", "AI가 1초 만에 매력·관상 진단!") if copy_data else "AI가 1초 만에 매력·관상 진단!"
        subtitle = copy_data.get("subtitle", "얼굴형과 분위기 분석부터 나와 찰떡인 이성 얼굴상까지 추천") if copy_data else "얼굴형과 분위기 분석부터 나와 찰떡인 이성 얼굴상까지 추천"

        default_bullets = [
            "눈매, 입꼬리, 턱선 비율 기반 128포인트 정밀 스캔",
            "고양이상·여우상 vs 🐶 강아지상 대표 매력 판독",
            "나와 시각적 케미 터지는 황금 궁합 매칭 시스템"
        ]
        bullets = copy_data.get("bullets", default_bullets) if copy_data else default_bullets
        while len(bullets) < 3:
            bullets.append("Aura 100% 매칭 시스템")

        cta_text = copy_data.get("cta_text", "👉 옆으로 넘겨서 매력 진단 보기 (1/5) >") if copy_data else "👉 옆으로 넘겨서 매력 진단 보기 (1/5) >"

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Aura Topic 7 Slide 1 (1080x1350)</title>
  <!-- Pretendard Font -->
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <!-- Tailwind CSS -->
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
      position: relative;
      background: #000;
    }}

    /* 배경 사진 풀블리드 */
    .bg-photo {{
      position: absolute;
      top: 0;
      left: 0;
      width: 1080px;
      height: 1350px;
      object-fit: cover;
      object-position: center 15%;
      z-index: 1;
    }}

    /* 상단 & 하단 시네마틱 스크림 그라데이션 */
    .scrim-top {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 280px;
      background: linear-gradient(180deg, rgba(0, 0, 0, 0.8) 0%, rgba(0, 0, 0, 0.4) 60%, rgba(0, 0, 0, 0) 100%);
      z-index: 2;
    }}

    .scrim-bottom {{
      position: absolute;
      bottom: 0;
      left: 0;
      width: 100%;
      height: 620px;
      background: linear-gradient(0deg, rgba(5, 7, 15, 0.98) 0%, rgba(5, 7, 15, 0.88) 45%, rgba(5, 7, 15, 0.45) 80%, rgba(0, 0, 0, 0) 100%);
      z-index: 2;
    }}

    /* 텍스트 섀도우 */
    .text-headline {{
      color: #FFF275;
      text-shadow: 0 4px 18px rgba(0, 0, 0, 0.95), 0 2px 4px rgba(0, 0, 0, 0.9);
      letter-spacing: -0.03em;
    }}

    .text-subhead {{
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.9);
    }}

    /* CTA 바 발광 */
    .cta-glow {{
      background: linear-gradient(135deg, #FF6B00 0%, #FF8800 50%, #FFAA00 100%);
      box-shadow: 0 10px 30px rgba(255, 107, 0, 0.5), 0 0 20px rgba(255, 170, 0, 0.35);
    }}
  </style>
</head>
<body>

  <!-- 1. Background Photo (Wan 2.1 실사 신규 모델) -->
  <img src="data:image/jpeg;base64,{photo_b64}" class="bg-photo" alt="Topic 7 Cover Photo" />

  <!-- 2. Scrim Gradients -->
  <div class="scrim-top"></div>
  <div class="scrim-bottom"></div>

  <!-- 3. Top Header Bar (Brand Badge + Page Index) -->
  <div class="absolute top-8 left-8 right-8 flex justify-between items-center z-10">
    <!-- Brand Badge -->
    <div class="inline-flex items-center gap-3 bg-slate-900/90 backdrop-blur-md border border-white/25 rounded-full py-2.5 px-5 shadow-2xl">
      <span class="text-lg">💖</span>
      <span class="text-base font-black tracking-wider text-white">아우라 AI 데이팅</span>
      <span class="text-sm font-bold text-pink-400 pl-3 border-l border-white/30">현재 100% 무료</span>
    </div>

    <!-- Page Index -->
    <div class="text-amber-400 font-black text-base bg-slate-900/90 backdrop-blur-md px-5 py-2.5 rounded-full border border-amber-500/50 shadow-2xl tracking-wider">
      01 / 05 &gt;
    </div>
  </div>

  <!-- 4. Bottom Content Area (Headline + Bullets + CTA) -->
  <div class="absolute bottom-10 left-8 right-8 z-10 flex flex-col items-start space-y-4">
    
    <!-- Category Badge -->
    <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-gradient-to-r from-purple-600 via-pink-600 to-amber-500 text-white text-sm font-black shadow-lg">
      <span>{badge}</span>
    </div>

    <!-- Main Headline (Yellow Bold) -->
    <h1 class="text-[38px] font-black leading-[1.24] text-headline">
      {h1_line1}<br>
      {h1_line2}
    </h1>

    <!-- Subtitle -->
    <p class="text-[19px] font-bold text-slate-100 text-subhead leading-relaxed">
      {subtitle}
    </p>

    <!-- Bullets List -->
    <div class="flex flex-col space-y-2.5 pt-1 pb-2">
      <div class="flex items-start gap-2.5 text-base font-bold text-slate-200 text-subhead">
        <span class="text-purple-400 text-lg">✨</span>
        <span>{bullets[0]}</span>
      </div>
      <div class="flex items-start gap-2.5 text-base font-bold text-slate-200 text-subhead">
        <span class="text-pink-400 text-lg">🦊</span>
        <span>{bullets[1]}</span>
      </div>
      <div class="flex items-start gap-2.5 text-base font-bold text-amber-300 text-subhead">
        <span class="text-amber-400 text-lg">💖</span>
        <span>{bullets[2]}</span>
      </div>
    </div>

    <!-- Bottom Swipe CTA Bar -->
    <div class="w-full cta-glow rounded-2xl py-4 flex items-center justify-center gap-2 shadow-2xl">
      <span class="text-white text-xl font-black tracking-wide">
        {cta_text}
      </span>
    </div>

  </div>

</body>
</html>
"""

        logger.info(f"🎨 [AuraCardnewsS1Topic7] 1080x1350 1번 표지(Wan 2.1 신규 실사) 렌더링 시작 -> {out_path.name}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
            page.set_content(html_content, wait_until="networkidle")
            page.screenshot(path=str(out_path), full_page=True)
            browser.close()

        logger.info(f"✅ [AuraCardnewsS1Topic7] 1번 표지 렌더링 완료: {out_path}")
        return str(out_path)

    def produce(self, target_dir: str = None, outfit: dict = None, copy_data: Dict[str, Any] = None) -> str:
        """Wan 2.1 사진 신규 생성부터 1번 표지 카드뉴스 렌더링까지 일괄 실행"""
        if not target_dir:
            from .aura_cardnews_storage import AuraCardnewsStorage
            t_path = AuraCardnewsStorage.create_target_directory(theme_code="ai_charm_scanner")
        else:
            t_path = Path(target_dir)
            t_path.mkdir(parents=True, exist_ok=True)

        # 1. Wan 2.1 실사 사진 신규 생성 (의상 동기화)
        raw_photo = self.generate_s1_photo(outfit=outfit)

        # 2. 1080x1350 카드뉴스 렌더링
        slide1_path = t_path / "slide_1.png"
        self.render_slide(raw_photo, str(slide1_path), copy_data=copy_data)

        return str(slide1_path)

        return str(slide1_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    builder = AuraCardnewsS1Topic7Builder()
    builder.produce()
