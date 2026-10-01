# -*- coding: utf-8 -*-
"""
AuraCardnewsS2Topic8Builder - 📱 [Aura 카드뉴스 8번 주제 2번 핸드폰 화면 확인 빌더 (3.5M 와이드)]
======================================================================================================
• 역할:
  - 1번 표지의 24세 포니테일 미녀 모델 + 화이트 윈드브레이커 + 성수동 테라스 배경 100% 동일 계승
  - 3.5M 거리 와이드 카우보이 화각으로 스마트폰을 손에 쥐고 안심 지도를 확인하는 자연스러운 포즈 포착
  - 회색 박스 없는 투명 시네마틱 스크림 & 플로팅 타이포그래피 렌더링
  - 상단 공식 헤더['💖 AURA | 50:50 남녀 황금 성비율', '02 / 05 >'] + 1080x1350 초고화질 렌더링
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

logger = logging.getLogger("AuraCardnewsS2Topic8Builder")


class AuraCardnewsS2Topic8Builder:
    """Aura 주제 8(500m 안심 레이더) 2번 핸드폰 확인 카드 전문 빌더 (3.5M 와이드 구도)"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.wan_client = WanPipelineClient()

    def generate_s2_photo(self, outfit: Dict[str, Any] = None, seed: int = None) -> Path:
        """3.5M 거리 와이드 카우보이 샷으로 스마트폰을 들고 화면을 보고 있는 실사 생성"""
        if seed is None:
            seed = int(time.time() * 1000) % 100000000

        # 의상 프롬프트 주입 (outfit이 없으면 기본 1번 의상)
        if outfit and "s2_clothing" in outfit:
            clothing_prompt = outfit["s2_clothing"]
            outfit_name = outfit.get("name_ko", "지정 의상")
        else:
            clothing_prompt = "wearing the exact same stylish crisp white minimalist gorpcore hooded windbreaker jacket slightly unzipped over a beige ribbed inner top with premium matte black high-waisted athletic yoga leggings, holding a black smartphone, sporty sleek modern Seoul street fashion"
            outfit_name = "화이트 윈드브레이커 & 딥블랙 레깅스"

        pos = (
            "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
            "photographed from 3.5 meters away with natural smartphone wide camera lens, "
            "wide environmental cowboy shot, generous wide framing with ample spacious headroom above, showing complete upper body from head down past waist and hips, "
            "solo 1person female, the exact same exceptionally gorgeous glamorous 24-year-old Korean young woman from slide 1 (healthy radiant natural beauty, neat high sleek dark ponytail hairstyle with soft baby hair), "
            "flawless 8-head-high golden ratio model proportions, small refined head and face size, slender neck, graceful collarbone, "
            "flawless glowing porcelain glass skin with soft natural peach cheek glow, authentic fine real human skin texture with visible real pores, "
            f"{clothing_prompt}, "
            "she is holding her sleek modern smartphone naturally in both hands at chest and waist level, looking down at the smartphone screen with an intrigued curious gentle pleasant smile, "
            "the phone body and screen are clearly visible in the shot, pristine anatomically correct realistic five-finger hands holding the phone naturally, "
            "natural full lips gently closed together with a subtle sweet confident smile, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "seated comfortably at the exact same sleek modern outdoor marble cafe terrace table in Seongsu-dong cafe street with architectural brick walls and outdoor glass windows in tack sharp f/11 focus, "
            "subject occupies only about 38% of vertical frame with generous surroundings, "
            "f/11 deep pan-focus, zero bokeh, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, Apple iPhone 15 Pro Smart HDR photo, NO beauty filter, NO skin smoothing."
        )
        neg = (
            "close up, extreme close up, tight portrait, cropped head, cropped shoulders, cropped hands, hidden hands, missing hands, hands not visible, no phone, missing phone, phone not visible, "
            "phone to ear, calling on phone, holding phone near ear, "
            "bokeh, blurry background, shallow depth of field, lens blur, out of focus, smeared background, watercolor trees, blurred scenery, "
            "open mouth, parted lips, visible teeth, showing teeth, laughing, grinning, smiling wide, "
            "ugly face, old woman, middle aged, chubby, fat face, broad jaw, double chin, distorted features, bad eyes, asymmetric face, "
            "doll, doll face, porcelain skin, plastic skin, airbrushed skin, beauty filter, skin smoothing, "
            "deformed hands, extra fingers, missing fingers, bad fingers, mutated hands, "
            "cartoon, anime, 3d render, cgi, illustration, drawing, watermark, text, male, man, two people"
        )

        logger.info(f"🎨 [AuraCardnewsS2Topic8] 8번 주제 2번 핸드폰 확인(3.5M 와이드, 착장: {outfit_name}) Wan 2.1 생성 시작 (Seed={seed})...")
        raw_path = self.wan_client.generate_t2i_master(
            positive_prompt=pos,
            negative_prompt=neg,
            width=832,
            height=1216,
            seed=seed,
            prefix="aura_topic8_s2_phone_wide"
        )
        logger.info(f"✅ [AuraCardnewsS2Topic8] 2번 3.5M 와이드 사진 생성 완료: {raw_path}")
        return Path(raw_path)

    def render_slide(self, photo_path: Path, output_png_path: str, copy_data: Dict[str, Any] = None) -> str:
        """Playwright로 1080x1350 카드뉴스 2번 슬라이드 렌더링 (제미나이 동적 카피 주입)"""
        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(str(photo_path), "rb") as f:
            photo_b64 = base64.b64encode(f.read()).decode("utf-8")

        # 제미나이 동적 카피 또는 기본값
        badge = copy_data.get("badge", "📱 500m 안심 레이더 가동") if copy_data else "📱 500m 안심 레이더 가동"
        h1_line1 = copy_data.get("headline_line1", "내 집 앞 500m 안심 지터링 보안으로") if copy_data else "내 집 앞 500m 안심 지터링 보안으로"
        h1_line2 = copy_data.get("headline_line2", "집 주소 노출 없이 안전한 성수동 번개!") if copy_data else "집 주소 노출 없이 안전한 성수동 번개!"
        subtitle = copy_data.get("subtitle", "정밀 위치는 500m 랜덤 분산! 안전하게 검증된 동네 카페 메이트 탐색") if copy_data else "정밀 위치는 500m 랜덤 분산! 안전하게 검증된 동네 카페 메이트 탐색"
        
        default_bullets = [
            "반경 500m 지터링 보안 알고리즘 (실시간 거주지 100% 은폐)",
            "지금 바로 만날 수 있는 2030 동네 친구 실시간 레이더",
            "스토킹·사생활 유출 100% 원천 차단 안심 시스템"
        ]
        bullets = copy_data.get("bullets", default_bullets) if copy_data else default_bullets
        while len(bullets) < 3:
            bullets.append("Aura 100% 검증 안전 시스템")
        
        cta_text = copy_data.get("cta_text", "👉 옆으로 넘겨서 500m 레이더 지도 보기 (2/5) >") if copy_data else "👉 옆으로 넘겨서 500m 레이더 지도 보기 (2/5) >"

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Aura Topic 8 Slide 2 (1080x1350)</title>
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

    /* 배경 사진 풀블리드 (3.5M 카우보이 화각 최적 맞춤) */
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

    /* 상단 & 하단 시네마틱 미세 스크림 */
    .scrim-top {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 200px;
      background: linear-gradient(180deg, rgba(0, 0, 0, 0.65) 0%, rgba(0, 0, 0, 0.2) 60%, rgba(0, 0, 0, 0) 100%);
      z-index: 2;
    }}

    .scrim-bottom {{
      position: absolute;
      bottom: 0;
      left: 0;
      width: 100%;
      height: 480px;
      background: linear-gradient(0deg, rgba(0, 0, 0, 0.85) 0%, rgba(0, 0, 0, 0.5) 45%, rgba(0, 0, 0, 0.15) 80%, rgba(0, 0, 0, 0) 100%);
      z-index: 2;
    }}

    /* 텍스트 섀도우 */
    .text-headline {{
      color: #FFF275;
      text-shadow: 0 4px 18px rgba(0, 0, 0, 0.98), 0 2px 6px rgba(0, 0, 0, 0.95);
      letter-spacing: -0.03em;
    }}

    .text-subhead {{
      text-shadow: 0 2px 12px rgba(0, 0, 0, 0.95), 0 1px 3px rgba(0, 0, 0, 0.9);
    }}

    /* CTA 바 발광 */
    .cta-glow {{
      background: linear-gradient(135deg, #FF6B00 0%, #FF8800 50%, #FFAA00 100%);
      box-shadow: 0 10px 30px rgba(255, 107, 0, 0.5), 0 0 20px rgba(255, 170, 0, 0.35);
    }}
  </style>
</head>
<body>

  <!-- 1. Background Photo (3.5M 거리에서 스마트폰 보는 실사 모델) -->
  <img src="data:image/jpeg;base64,{photo_b64}" class="bg-photo" alt="Topic 8 Slide 2 Photo" />

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
    <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-gradient-to-r from-blue-600 via-indigo-600 to-emerald-500 text-white text-sm font-black shadow-lg">
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
        <span class="text-blue-400 text-lg">📍</span>
        <span>{bullets[0]}</span>
      </div>
      <div class="flex items-start gap-2.5 text-base font-bold text-slate-200 text-subhead">
        <span class="text-emerald-400 text-lg">🏃‍♀️</span>
        <span>{bullets[1]}</span>
      </div>
      <div class="flex items-start gap-2.5 text-base font-bold text-amber-300 text-subhead">
        <span class="text-amber-400 text-lg">🛡️</span>
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

        logger.info(f"🎨 [AuraCardnewsS2Topic8] 1080x1350 2번 슬라이드(3.5M 핸드폰 확인) 렌더링 시작 -> {out_path.name}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
            page.set_content(html_content, wait_until="networkidle")
            page.screenshot(path=str(out_path), full_page=True)
            browser.close()

        logger.info(f"✅ [AuraCardnewsS2Topic8] 2번 슬라이드 렌더링 완료: {out_path}")
        return str(out_path)

    def produce(self, target_dir: str = None, outfit: Dict[str, Any] = None, seed: int = None, copy_data: Dict[str, Any] = None) -> str:
        """Wan 2.1 사진 생성부터 2번 카드뉴스 렌더링까지 일괄 실행"""
        if not target_dir:
            from brands.aura.aura_cardnews_storage import AuraCardnewsStorage
            t_path = AuraCardnewsStorage.create_target_directory(theme_code="safe_radar_500m")
        else:
            t_path = Path(target_dir)
            t_path.mkdir(parents=True, exist_ok=True)

        # 1. 3.5M 와이드 핸드폰 확인 실사 사진 생성 (동일 의상 주입)
        raw_photo = self.generate_s2_photo(outfit=outfit, seed=seed)

        # 2. 1080x1350 카드뉴스 렌더링
        slide2_path = t_path / "slide_2.png"
        self.render_slide(raw_photo, str(slide2_path), copy_data=copy_data)

        return str(slide2_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    builder = AuraCardnewsS2Topic8Builder()
    builder.produce()
