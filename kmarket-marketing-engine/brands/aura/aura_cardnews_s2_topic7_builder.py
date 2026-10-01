# -*- coding: utf-8 -*-
"""
AuraCardnewsS2Topic7Builder - 📱 [Aura 카드뉴스 7번 주제 'AI 매력상 & 관상/궁합 진단' 2번 셀카 촬영 빌더 (3M 와이드 카우보이 샷)]
=============================================================================================================================
• 역할:
  - 1번 표지의 24세 매혹적인 여우상 미녀 모델 + 블랙 골지 니트 + 갤러리 카페 배경 100% 동일 계승
  - 3M 뒤에서 촬영한 와이드 카우보이 화각으로 스마트폰을 든 양손과 폰 기기, 셀카 촬영 포즈를 완벽하게 포착
  - 1080x1350 카드뉴스 규격 초고화질 서브픽셀 렌더링
  - 상단 배지['📸 사진 1장 1초 진단', '02 / 05 >'] + 헤드라인 + 핵심 불릿 + 하단 넘김 CTA 바 일체형 렌더링
"""

import os
import sys
import time
import base64
import logging
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from core.engine.wan_pipeline_client import WanPipelineClient

logger = logging.getLogger("AuraCardnewsS2Topic7Builder")


class AuraCardnewsS2Topic7Builder:
    """Aura 주제 7(AI 매력상 & 관상/궁합 진단) 2번 셀카 촬영 카드 전문 빌더 (3M 와이드 구도)"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.wan_client = WanPipelineClient()

    def generate_s2_photo(self, outfit: dict = None, seed: int = None) -> Path:
        """3M 거리 와이드 카우보이 샷으로 스마트폰을 들고 셀카 찍는 실사 생성 (1번 표지와 100% 동일 의상 주입)"""
        if seed is None:
            seed = int(time.time() * 1000) % 100000000

        if outfit is None:
            from .aura_cardnews_topic7_wardrobe import get_wardrobe
            outfit = get_wardrobe()

        clothing_prompt = outfit.get("s2_clothing", "wearing the exact same chic stylish minimalist black ribbed long-sleeve knit top from slide 1")
        outfit_name = outfit.get("name_ko", "기본 의상")

        pos = (
            "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
            "photographed from 3 meters away, wide medium cowboy shot with generous wide framing and ample headroom above, "
            "solo 1person female, the exact same exceptionally gorgeous glamorous 24-year-old Korean woman from slide 1 (alluring fox-like and feline cat-like facial aesthetic, refined delicate features), "
            "perfect 8-head-high golden ratio model proportions, small refined head and face size, slender elegant long neck, graceful collarbone, "
            "captivating alluring almond-shaped dark eyes with subtle elegant winged eyeliner looking directly at camera, "
            "flawless luminous porcelain glass skin with soft natural peach cheek glow, authentic fine real human skin texture with visible pores, "
            "natural full lips gently closed together with a subtle charming sweet confident smile, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "sleek glossy dark espresso brown long hair falling gracefully over shoulders, "
            f"{clothing_prompt}, "
            "she is holding her sleek modern smartphone steadily up in front of her at chest level with both hands, clearly taking a selfie portrait for her AI face diagnosis, the smartphone body and screen are clearly visible in the shot, "
            "pristine anatomically correct realistic five-finger hands holding the phone naturally and clearly, "
            "seated or standing gracefully in the exact same upscale cozy modern cafe lounge interior with warm glowing art frame lights and golden ambient lighting from slide 1 in tack sharp f/11 focus, "
            "wide cowboy shot showing head to mid-thigh, torso, both arms raised holding smartphone, and cafe background, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, Apple iPhone 15 Pro Smart HDR photo."
        )
        neg = (
            "extreme close up, close up, tight portrait, cropped arms, cropped hands, hidden hands, missing hands, hands not visible, no phone, missing phone, phone not visible, "
            "phone to ear, calling on phone, holding phone near ear, "
            "open mouth, parted lips, visible teeth, showing teeth, laughing, grinning, smiling wide, "
            "ugly face, old woman, middle aged, chubby, fat face, broad jaw, double chin, distorted features, bad eyes, asymmetric face, "
            "doll, doll face, porcelain skin, plastic skin, airbrushed skin, beauty filter, skin smoothing, "
            "blurry, lens blur, out of focus, bokeh blur, shallow depth of field, deformed hands, extra fingers, missing fingers, bad fingers, mutated hands, "
            "cartoon, anime, 3d render, cgi, illustration, drawing, watermark, text, male, man, two people"
        )

        logger.info(f"🎨 [AuraCardnewsS2Topic7] 7번 주제 2번 셀카 촬영(3M 와이드 구도) Wan 2.1 생성 시작 (동일 의상: {outfit_name}, Seed={seed})...")
        raw_path = self.wan_client.generate_t2i_master(
            positive_prompt=pos,
            negative_prompt=neg,
            width=832,
            height=1216,
            seed=seed,
            prefix="aura_topic7_s2_selfie_wide"
        )
        logger.info(f"✅ [AuraCardnewsS2Topic7] 2번 3M 와이드 셀카 사진 생성 완료: {raw_path}")
        return Path(raw_path)

    def render_slide(self, photo_path: Path, output_png_path: str, copy_data: dict = None) -> str:
        """Playwright로 1080x1350 카드뉴스 2번 슬라이드 렌더링 (제미나이 동적 카피 주입)"""
        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(str(photo_path), "rb") as f:
            photo_b64 = base64.b64encode(f.read()).decode("utf-8")

        # 제미나이 동적 카피 또는 기본값
        s2_copy = copy_data.get("slide2", {}) if copy_data else {}
        badge = s2_copy.get("badge", "📸 사진 1장 1초 진단")
        h1_line1 = s2_copy.get("headline_line1", "폰으로 셀카 한 장 찍었을 뿐인데...")
        h1_line2 = s2_copy.get("headline_line2", "내 숨겨진 매력상과 찰떡 이성을 찾는다고?")
        subtitle = s2_copy.get("subtitle", "복잡한 설문 없이 사진 한 장으로 1초 만에 끝내는 AI 비주얼 스캔")

        default_bullets = [
            "각도와 조명에 구애받지 않는 128포인트 정밀 얼굴 인식",
            "내 얼굴 고유의 매력 분위기(여우상·고양이상·과즙미) 도출",
            "나와 시각적 케미가 폭발하는 궁합 이성 1:1 매칭 준비"
        ]
        bullets = s2_copy.get("bullets", default_bullets)
        while len(bullets) < 3:
            bullets.append("Aura 100% 매칭 솔루션")

        cta_text = s2_copy.get("cta_text", "👉 옆으로 넘겨서 AI 분석 결과 보기 (2/5) >")

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Aura Topic 7 Slide 2 (1080x1350)</title>
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
      object-position: center top;
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

  <!-- 1. Background Photo (3M 거리에서 폰을 들고 셀카 찍는 실사 모델) -->
  <img src="data:image/jpeg;base64,{photo_b64}" class="bg-photo" alt="Topic 7 Slide 2 Photo" />

  <!-- 2. Scrim Gradients -->
  <div class="scrim-top"></div>
  <div class="scrim-bottom"></div>

  <!-- 3. Top Header Bar (Brand Badge + Page Index) -->
  <div class="absolute top-8 left-8 right-8 flex justify-between items-center z-10">
    <!-- Brand Badge -->
    <div class="inline-flex items-center gap-3 bg-slate-900/90 backdrop-blur-md border border-white/25 rounded-full py-2.5 px-5 shadow-2xl">
      <span class="text-lg">💖</span>
      <span class="text-base font-black tracking-wider text-white">AURA</span>
      <span class="text-sm font-bold text-pink-400 pl-3 border-l border-white/30">50:50 남녀 황금 성비율</span>
    </div>

    <!-- Page Index -->
    <div class="text-amber-400 font-black text-base bg-slate-900/90 backdrop-blur-md px-5 py-2.5 rounded-full border border-amber-500/50 shadow-2xl tracking-wider">
      02 / 05 &gt;
    </div>
  </div>

  <!-- 4. Bottom Content Area (Headline + Bullets + CTA) -->
  <div class="absolute bottom-10 left-8 right-8 z-10 flex flex-col items-start space-y-4">
    
    <!-- Category Badge -->
    <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-gradient-to-r from-blue-600 via-indigo-600 to-pink-500 text-white text-sm font-black shadow-lg">
      <span>{badge}</span>
    </div>

    <!-- Main Headline (Yellow Bold) -->
    <h1 class="text-[38px] font-black leading-[1.24] text-headline">
      {h1_line1}<br>
      {h1_line2}
    </h1>

    <!-- Subtitle -->
    <p class="text-[20px] font-bold text-slate-100 text-subhead leading-relaxed">
      {subtitle}
    </p>

    <!-- Bullets List -->
    <div class="flex flex-col space-y-2.5 pt-1 pb-2">
      <div class="flex items-start gap-2.5 text-base font-bold text-slate-200 text-subhead">
        <span class="text-blue-400 text-lg">🤳</span>
        <span>{bullets[0]}</span>
      </div>
      <div class="flex items-start gap-2.5 text-base font-bold text-slate-200 text-subhead">
        <span class="text-pink-400 text-lg">🦊</span>
        <span>{bullets[1]}</span>
      </div>
      <div class="flex items-start gap-2.5 text-base font-bold text-amber-300 text-subhead">
        <span class="text-amber-400 text-lg">💡</span>
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

        logger.info(f"🎨 [AuraCardnewsS2Topic7] 1080x1350 2번 슬라이드(3M 와이드 셀카) 렌더링 시작 -> {out_path.name}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
            page.set_content(html_content, wait_until="networkidle")
            page.screenshot(path=str(out_path), full_page=True)
            browser.close()

        logger.info(f"✅ [AuraCardnewsS2Topic7] 2번 슬라이드 렌더링 완료: {out_path}")
        return str(out_path)

    def produce(self, target_dir: str = None, outfit: dict = None, copy_data: dict = None, seed: int = None) -> str:
        """Wan 2.1 사진 생성부터 2번 카드뉴스 렌더링까지 일괄 실행"""
        if not target_dir:
            from .aura_cardnews_storage import AuraCardnewsStorage
            t_path = AuraCardnewsStorage.create_target_directory(theme_code="ai_charm_scanner")
        else:
            t_path = Path(target_dir)
            t_path.mkdir(parents=True, exist_ok=True)

        # 1. 3M 와이드 셀카 찍는 실사 사진 생성 (1번 표지와 동일 의상)
        raw_photo = self.generate_s2_photo(outfit=outfit, seed=seed)

        # 2. 1080x1350 카드뉴스 렌더링
        slide2_path = t_path / "slide_2.png"
        self.render_slide(raw_photo, str(slide2_path), copy_data=copy_data)

        return str(slide2_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    builder = AuraCardnewsS2Topic7Builder()
    builder.produce()
