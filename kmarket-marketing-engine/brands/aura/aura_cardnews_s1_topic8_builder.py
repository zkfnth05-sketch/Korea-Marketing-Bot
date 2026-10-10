# -*- coding: utf-8 -*-
"""
AuraCardnewsS1Topic8Builder - 📱 [Aura 카드뉴스 8번 주제 '500m 안심 레이더 & 안심 번개 퀘스트' 1번 표지 Wan 2.1 자율 생성 빌더]
=============================================================================================================================
• 역할:
  - 8번 전용 10벌 룩북(OOTD)과 3.5M 거리 8등신 아이폰 15 Pro 무필터 실사 생성
  - 제미나이 실시간 창작 카피 주입 및 1080x1350 초고화질 서브픽셀 렌더링
  - 상단 공식 헤더['💖 아우라 AI 데이팅 | 현재 100% 무료 남녀 황금 성비율', '01 / 05 >']
"""

import os
import sys
import time
import base64
import logging
from pathlib import Path
from core.engine.naver_search_bar_component import render_naver_search_bar_html

from typing import Dict, Any, Optional
from PIL import Image
from playwright.sync_api import sync_playwright

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from core.engine.wan_pipeline_client import WanPipelineClient

logger = logging.getLogger("AuraCardnewsS1Topic8Builder")


class AuraCardnewsS1Topic8Builder:
    """Aura 주제 8(500m 안심 레이더 & 안심 번개 퀘스트) 1번 표지 카드 전문 빌더 (Wan 2.1 T2I 실사 자율 생성)"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.wan_client = WanPipelineClient()

    def generate_s1_photo(self, outfit: Dict[str, Any] = None, seed: int = None) -> Path:
        """Wan 2.1 T2I로 8번 주제 전용 청순하고 스포티한 포니테일 미녀 모델 실사 신규 생성"""
        if seed is None:
            seed = int(time.time() * 1000) % 100000000

        # 의상 프롬프트 주입 (outfit이 없으면 기본 1번 의상)
        if outfit and "s1_clothing" in outfit:
            clothing_prompt = outfit["s1_clothing"]
            outfit_name = outfit.get("name_ko", "지정 의상")
        else:
            clothing_prompt = "wearing a stylish crisp white minimalist gorpcore hooded windbreaker jacket slightly unzipped at collar over a beige ribbed inner top, paired with premium matte black high-waisted seamless athletic yoga leggings, sporty sleek modern Seoul street fashion"
            outfit_name = "화이트 윈드브레이커 & 딥블랙 레깅스"

        pos = (
            "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
            "photographed from 3.5 meters away with natural smartphone wide camera lens, "
            "wide environmental cowboy shot, generous wide framing with ample spacious headroom above, showing complete upper body from head down past waist and hips, "
            "solo 1person female, perfectly centered in frame, looking directly into camera with bright friendly confident gaze, "
            "an exceptionally gorgeous glamorous 24-year-old Korean young woman with healthy energetic radiant natural beauty, "
            "neat high sleek dark ponytail hairstyle with delicate soft baby hair along the hairline, "
            "clear bright almond-shaped dark eyes with subtle natural makeup, delicate high nose bridge, cute refined jawline, "
            "flawless 8-head-high golden ratio model proportions, small refined head and face size, slender neck, graceful collarbone, "
            "flawless glowing porcelain glass skin with soft healthy natural peach cheek glow, authentic fine real human skin texture with visible real pores, "
            "natural full lips gently closed together with a bright cheerful confident warm smile, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            f"{clothing_prompt}, "
            "seated comfortably at a sleek modern outdoor marble cafe terrace table with hands resting naturally together, "
            "subject occupies only about 38% of vertical frame with generous scenic Seongsu-dong modern brick cafe exterior, outdoor glass windows, and stylish cafe street in tack sharp f/11 focus, "
            "f/11 deep pan-focus, zero bokeh, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, authentic everyday Apple iPhone 15 Pro Smart HDR photo, NO beauty filter, NO skin smoothing."
        )
        neg = (
            "close up, extreme close up, tight portrait, cropped head, cropped shoulders, cropped chest, zoomed-in, person filling entire frame, "
            "bokeh, blurry background, shallow depth of field, lens blur, out of focus, smeared background, watercolor trees, blurred scenery, "
            "open mouth, parted lips, visible teeth, showing teeth, laughing, grinning, smiling wide, "
            "ugly face, old woman, middle aged, chubby, fat face, broad jaw, double chin, distorted features, bad eyes, asymmetric face, "
            "doll, doll face, porcelain skin, plastic skin, airbrushed skin, beauty filter, skin smoothing, "
            "deformed hands, extra fingers, missing fingers, bad fingers, "
            "cartoon, anime, 3d render, cgi, illustration, drawing, watermark, text, male, man, two people"
        )

        logger.info(f"🎨 [AuraCardnewsS1Topic8] 8번 표지 3.5M 실사 생성 시작 (착장: {outfit_name}, Seed={seed})...")
        raw_path = self.wan_client.generate_t2i_master(
            positive_prompt=pos,
            negative_prompt=neg,
            width=832,
            height=1216,
            seed=seed,
            prefix="aura_topic8_s1_safe_radar_8head"
        )
        logger.info(f"✅ [AuraCardnewsS1Topic8] 8번 표지 신규 사진 생성 완료: {raw_path}")
        return Path(raw_path)

    def render_slide(self, photo_path: Path, output_png_path: str, copy_data: Dict[str, Any] = None) -> str:
        """Playwright로 1080x1350 카드뉴스 1번 표지 렌더링 (제미나이 동적 카피 주입)"""
        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(str(photo_path), "rb") as f:
            photo_b64 = base64.b64encode(f.read()).decode("utf-8")

        # 제미나이 동적 카피 또는 기본값
        badge = copy_data.get("badge", "🛡️ 500m 안심 지터링 보안 번개") if copy_data else "🛡️ 500m 안심 지터링 보안 번개"
        h1_line1 = copy_data.get("headline_line1", "집 주소 노출될까 봐 불안했지?") if copy_data else "집 주소 노출될까 봐 불안했지?"
        h1_line2 = copy_data.get("headline_line2", "500m 안심 레이더로 안전한 동네 친구 찾기!") if copy_data else "500m 안심 레이더로 안전한 동네 친구 찾기!"
        subtitle = copy_data.get("subtitle", "스토킹 & 사생활 걱정 제로! 내 위치는 500m 랜덤 보안으로 숨기고 동네 번개") if copy_data else "스토킹 & 사생활 걱정 제로! 내 위치는 500m 랜덤 보안으로 숨기고 동네 번개"
        bullets = copy_data.get("bullets", [
            "500m 반경 오차 지터링 보안 (실제 집 주소 100% 비공개)",
            "성수동 카페·산책·러닝 24시간 실시간 동네 번개 퀘스트",
            "GPS 위치 & 본인 실명 인증된 검증 회원 간 안심 매칭"
        ]) if copy_data else [
            "500m 반경 오차 지터링 보안 (실제 집 주소 100% 비공개)",
            "성수동 카페·산책·러닝 24시간 실시간 동네 번개 퀘스트",
            "GPS 위치 & 본인 실명 인증된 검증 회원 간 안심 매칭"
        ]
        cta_text = copy_data.get("cta_text", "👉 옆으로 넘겨서 안심 레이더 지도 보기 (1/5) >") if copy_data else "👉 옆으로 넘겨서 안심 레이더 지도 보기 (1/5) >"
        naver_search_html = render_naver_search_bar_html(brand="aura")

        b1 = bullets[0] if len(bullets) > 0 else "500m 반경 오차 지터링 보안"
        b2 = bullets[1] if len(bullets) > 1 else "24시간 실시간 동네 번개 퀘스트"
        b3 = bullets[2] if len(bullets) > 2 else "본인 실명 인증된 검증 회원 간 안심 매칭"

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Aura Topic 8 Slide 1 (1080x1350)</title>
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
      background-color: #0c1210;
      color: #fff;
    }}

    /* 실사 배경 사진 */
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

    /* 상단 은은한 앰비언트 비네팅 */
    .scrim-top {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 220px;
      background: linear-gradient(180deg, rgba(0, 0, 0, 0.75) 0%, rgba(0, 0, 0, 0.4) 50%, rgba(0, 0, 0, 0) 100%);
      z-index: 2;
      pointer-events: none;
    }}

    /* 하단 글래스 스크림 (회색 박스 없는 투명 시네마틱 그라데이션) */
    .scrim-bottom {{
      position: absolute;
      bottom: 0;
      left: 0;
      width: 100%;
      height: 650px;
      background: linear-gradient(180deg, rgba(0, 0, 0, 0) 0%, rgba(5, 12, 10, 0.45) 25%, rgba(5, 12, 10, 0.88) 65%, rgba(3, 8, 6, 0.98) 100%);
      z-index: 2;
      pointer-events: none;
    }}

    /* 텍스트 섀도우 및 타이포그래피 */
    .text-headline {{
      color: #FFF275;
      text-shadow: 0 4px 20px rgba(0, 0, 0, 0.95), 0 0 30px rgba(229, 169, 52, 0.45);
      letter-spacing: -0.03em;
    }}

    .text-subhead {{
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.9);
    }}

    /* CTA 글로우 */
    .cta-glow {{
      background: linear-gradient(135deg, #FF6B00 0%, #FF8800 50%, #FFAA00 100%);
      box-shadow: 0 10px 30px rgba(255, 107, 0, 0.5), 0 0 20px rgba(255, 170, 0, 0.35);
    }}
  </style>
</head>
<body>

  <!-- 1. Background Photo -->
  <img src="data:image/png;base64,{photo_b64}" class="bg-photo" alt="Aura 8등신 3.5M 실사" />

  <!-- 2. Scrims -->
  <div class="scrim-top"></div>
  <div class="scrim-bottom"></div>

  <!-- 3. Top Header Bar (Brand Badge + Page Index) -->
  <div class="absolute top-8 left-8 right-8 flex justify-between items-center z-10">
    <div class="inline-flex items-center gap-3 bg-slate-900/90 backdrop-blur-md border border-white/25 rounded-full py-2.5 px-5 shadow-2xl">
      <span class="text-lg">💖</span>
      <span class="text-base font-black tracking-wider text-white">아우라 AI 데이팅</span>
      <span class="text-sm font-bold text-pink-400 pl-3 border-l border-white/30">현재 100% 무료</span>
    </div>

    <div class="text-amber-400 font-black text-base bg-slate-900/90 backdrop-blur-md px-5 py-2.5 rounded-full border border-amber-500/50 shadow-2xl tracking-wider">
      01 / 05 &gt;
    </div>
  </div>

  <!-- 4. Bottom Content Area (Headline + Bullets + CTA) -->
  <div class="absolute bottom-10 left-8 right-8 z-10 flex flex-col items-start space-y-4">
    
    <!-- Category Badge -->
    <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-500 text-white text-sm font-black shadow-lg">
      <span>🛡️</span>
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
        <span class="text-emerald-400 text-lg">🛡️</span>
        <span>{b1}</span>
      </div>
      <div class="flex items-start gap-2.5 text-base font-bold text-slate-200 text-subhead">
        <span class="text-teal-400 text-lg">☕</span>
        <span>{b2}</span>
      </div>
      <div class="flex items-start gap-2.5 text-base font-bold text-amber-300 text-subhead">
        <span class="text-amber-400 text-lg">🔒</span>
        <span>{b3}</span>
      </div>
    </div>

      <!-- 하단 네이버 공식 검색창 UI 바 (숏폼 일체형) -->
      {naver_search_html}

  </div>

 </body>
</html>
"""

        logger.info(f"🎨 [AuraCardnewsS1Topic8] 1080x1350 1번 표지(8등신 3.5M 실사) 렌더링 시작 -> {out_path.name}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
            page.set_content(html_content, wait_until="networkidle")
            page.screenshot(path=str(out_path), full_page=True)
            browser.close()

        logger.info(f"✅ [AuraCardnewsS1Topic8] 1번 표지 렌더링 완료: {out_path}")
        return str(out_path)

    def produce(self, target_dir: str = None, outfit: Dict[str, Any] = None, copy_data: Dict[str, Any] = None, seed: int = None) -> str:
        """Wan 2.1 사진 신규 생성부터 1번 표지 카드뉴스 렌더링까지 일괄 실행 (제미나이 카피 결합)"""
        if not target_dir:
            from brands.aura.aura_cardnews_storage import AuraCardnewsStorage
            t_path = AuraCardnewsStorage.create_target_directory(theme_code="safe_radar_500m")
        else:
            t_path = Path(target_dir)
            t_path.mkdir(parents=True, exist_ok=True)

        # 1. Wan 2.1 실사 사진 신규 생성 (의상 주입)
        raw_photo = self.generate_s1_photo(outfit=outfit, seed=seed)

        # 2. 1080x1350 카드뉴스 렌더링 (제미나이 카피 주입)
        slide1_path = t_path / "slide_1.png"
        self.render_slide(raw_photo, str(slide1_path), copy_data=copy_data)

        return str(slide1_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    builder = AuraCardnewsS1Topic8Builder()
    builder.produce()
