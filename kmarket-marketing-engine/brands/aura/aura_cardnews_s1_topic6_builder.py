# -*- coding: utf-8 -*-
"""
AuraCardnewsS1Topic6Builder - 📱 [Aura 카드뉴스 6번 주제 'AI 첫대화 비서' 1번 표지 전문 빌더]
========================================================================================
• 역할:
  - 숏폼 6번 주제('AI 첫대화 비서')의 인물, 배경, 의상을 1:1 완벽하게 계승
  - 26세 K-드라마 남배우급 훈남 모델 + 모던 캐주얼 자켓 남친룩 + 서울 루프탑 야경
  - 1080x1350 카드뉴스 규격 초고화질 서브픽셀 타이포그래피 오버레이
  - 상단 50:50 황금 성비 배지 + 헤드라인 + 핵심 불릿 + 하단 넘김 CTA 바 일체형 렌더링
"""

import os
import sys
import time
import logging
from pathlib import Path
from core.engine.naver_search_bar_component import render_naver_search_bar_html

from PIL import Image
from playwright.sync_api import sync_playwright

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from core.engine.wan_pipeline_client import WanPipelineClient

logger = logging.getLogger("AuraCardnewsS1Topic6Builder")


class AuraCardnewsS1Topic6Builder:
    """Aura 주제 6(AI 첫대화 비서) 1번 표지 전문 빌더"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.wan_client = WanPipelineClient()

    def generate_cover_photo(self, seed: int = None) -> Path:
        """숏폼 6번 헌법 기반 26세 K-드라마 남주급 훈남 실사 생성"""
        if seed is None:
            seed = int(time.time() * 1000) % 100000000

        pos = (
            "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
            "an exceptionally handsome 26-year-old Korean adult man (K-drama male lead actor visual, delicate handsome idol-actor appearance, refined aesthetic features), "
            "perfect 8-head-high golden ratio male model proportions, small refined masculine head and face size, slender athletic male physique with broad masculine shoulders, "
            "soft gentle smile with lips closed together, refined handsome features, sharp sculpted jawline with natural subtle directional shadow, charismatic warm romantic gaze, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "neat stylish dark brown natural dandy haircut with subtle parted fringe framing his face, "
            "authentic real human skin texture with visible fine pores and natural skin tone, "
            "wearing a stylish, trendy modern casual jacket outfit, sophisticated 2030 Seoul dating fashion with diverse contemporary colors and textures, clean minimalist innerwear, effortless charismatic boyfriend-material date look, "
            "candid medium cowboy standing shot showing waist, chest, broad shoulders, and tall 8-head model silhouette clearly, generous headroom above, "
            "upscale modern outdoor open-air rooftop sky lounge terrace in Seoul at night with glowing warm Edison string bulb lights and elegant golden patio lanterns, "
            "standing beside sleek glass balustrade overlooking vibrant colorful glowing city neon lights and panoramic glittering Seoul night skyline in tack sharp f/11 focus, "
            "luxurious warm architectural uplighting illuminating the terrace ambiance naturally, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, Apple iPhone 15 Pro Smart HDR photo."
        )
        neg = (
            "open mouth, parted lips, visible teeth, showing teeth, laughing, grinning, smiling wide, "
            "ugly face, old man, middle aged, chubby, fat face, broad jaw, double chin, distorted features, bad eyes, asymmetric face, "
            "doll, doll face, porcelain skin, plastic skin, airbrushed skin, beauty filter, skin smoothing, "
            "blurry, lens blur, out of focus, bokeh blur, shallow depth of field, deformed hands, extra fingers, missing fingers, bad fingers, "
            "cartoon, anime, 3d render, cgi, illustration, drawing, watermark, text, female, woman"
        )

        logger.info(f"🎨 [AuraCardnewsS1Topic6] 6번 숏폼 훈남 실사 생성 시작 (Seed={seed})...")
        raw_path = self.wan_client.generate_t2i_master(
            positive_prompt=pos,
            negative_prompt=neg,
            width=832,
            height=1216,
            seed=seed,
            prefix="aura_topic6_cover_male"
        )
        logger.info(f"✅ [AuraCardnewsS1Topic6] 훈남 원본 사진 생성 완료: {raw_path}")
        return Path(raw_path)

    def render_cover_slide(self, photo_path: Path, output_png_path: str, copy_data: dict = None) -> str:
        """Playwright로 1080x1350 카드뉴스 규격 초고화질 타이포그래피 표지 렌더링 (제미나이 동적 카피 주입)"""
        import base64

        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(str(photo_path), "rb") as f:
            photo_b64 = base64.b64encode(f.read()).decode("utf-8")

        # 제미나이 동적 카피 또는 기본값
        s1_copy = copy_data.get("slide1", {}) if copy_data else {}
        badge = s1_copy.get("badge", "🔥 2030 소개팅 필살기")
        h1_line1 = s1_copy.get("headline_line1", "마음에 드는 이성 매칭됐는데,")
        h1_line2 = s1_copy.get("headline_line2", "첫마디로 '안녕하세요' 보내고 읽씹 당한 적?")
        subtitle = s1_copy.get("subtitle", "프로필만 넣으면 상대 취향 저격 첫 대화를 1초 만에 써주는 AI 비서")

        default_bullets = [
            "소개팅 첫 대화에서 제일 고민되는 첫 멘트 1초 자동 생성",
            "상대방 프로필/관심사 기반 자연스러운 티키타카 유도",
            "답장 성공률 98% 상승 • 읽씹 걱정 없는 스마트 매칭"
        ]
        bullets = s1_copy.get("bullets", default_bullets)
        while len(bullets) < 3:
            bullets.append("Aura AI 실시간 매칭 솔루션")

        cta_text = s1_copy.get("cta_text", "👉 옆으로 넘겨서 AI 첫대화 비서 보기 (1/5) >")
        naver_search_html = render_naver_search_bar_html(brand="aura")

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Aura Topic 6 Cover Slide (1080x1350)</title>
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

    /* 상단 & 하단 시네마틱 비네팅 / 스크림 그라데이션 */
    .scrim-top {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 280px;
      background: linear-gradient(180deg, rgba(0, 0, 0, 0.75) 0%, rgba(0, 0, 0, 0.35) 60%, rgba(0, 0, 0, 0) 100%);
      z-index: 2;
    }}

    .scrim-bottom {{
      position: absolute;
      bottom: 0;
      left: 0;
      width: 100%;
      height: 640px;
      background: linear-gradient(0deg, rgba(5, 7, 15, 0.96) 0%, rgba(5, 7, 15, 0.85) 45%, rgba(5, 7, 15, 0.4) 80%, rgba(0, 0, 0, 0) 100%);
      z-index: 2;
    }}

    /* 헤드라인 텍스트 스트로크 및 드롭 섀도우 */
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

  <!-- 1. Background Photo -->
  <img src="data:image/jpeg;base64,{photo_b64}" class="bg-photo" alt="Cover Photo" />

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
    <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-gradient-to-r from-pink-500 to-rose-600 text-white text-sm font-black shadow-lg">
      <span>{badge}</span>
    </div>

    <!-- Main Headline (Yellow Bold) -->
    <h1 class="text-[40px] font-black leading-[1.22] text-headline">
      {h1_line1}<br>
      {h1_line2}
    </h1>

    <!-- Subtitle -->
    <p class="text-[21px] font-bold text-slate-100 text-subhead leading-relaxed">
      {subtitle}
    </p>

    <!-- Bullets List -->
    <div class="flex flex-col space-y-2 pt-1 pb-2">
      <div class="flex items-center gap-2.5 text-base font-bold text-slate-200 text-subhead">
        <span class="text-sky-400 text-lg">●</span>
        <span>{bullets[0]}</span>
      </div>
      <div class="flex items-center gap-2.5 text-base font-bold text-slate-200 text-subhead">
        <span class="text-sky-400 text-lg">●</span>
        <span>{bullets[1]}</span>
      </div>
      <div class="flex items-center gap-2.5 text-base font-bold text-slate-200 text-subhead">
        <span class="text-sky-400 text-lg">●</span>
        <span>{bullets[2]}</span>
      </div>
    </div>

      <!-- 하단 네이버 공식 검색창 UI 바 (숏폼 일체형) -->
      {naver_search_html}

  </div>

</body>
</html>
"""

        logger.info(f"🎨 [AuraCardnewsS1Topic6] 1080x1350 표지 렌더링 시작 -> {out_path.name}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
            page.set_content(html_content, wait_until="networkidle")
            page.screenshot(path=str(out_path), full_page=True)
            browser.close()

        logger.info(f"✅ [AuraCardnewsS1Topic6] 1번 표지 렌더링 완료: {out_path}")
        return str(out_path)

    def produce(self, target_dir: str = None, copy_data: dict = None, seed: int = None) -> str:
        """사진 생성부터 표지 카드뉴스 렌더링까지 일괄 실행"""
        if not target_dir:
            from .aura_cardnews_storage import AuraCardnewsStorage
            t_path = AuraCardnewsStorage.create_target_directory(theme_code="smart_opener")
        else:
            t_path = Path(target_dir)
            t_path.mkdir(parents=True, exist_ok=True)

        # 1. 훈남 실사 사진 생성
        raw_photo = self.generate_cover_photo(seed=seed)

        # 2. 1080x1350 표지 슬라이드 렌더링
        slide1_path = t_path / "slide_1.png"
        self.render_cover_slide(raw_photo, str(slide1_path), copy_data=copy_data)

        return str(slide1_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    builder = AuraCardnewsS1Topic6Builder()
    builder.produce()
