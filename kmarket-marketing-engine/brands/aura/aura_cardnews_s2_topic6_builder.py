# -*- coding: utf-8 -*-
"""
AuraCardnewsS2Topic6Builder - 📱 [Aura 카드뉴스 6번 주제 'AI 첫대화 비서' 2번 공감 카드 전문 빌더]
========================================================================================
• 역할:
  - 1번 표지의 26세 K-드라마 훈남 모델 + 모던 캐주얼 자켓 남친룩 + 성수동 낮 통유리 부티크 카페 100% 동일 계승
  - 스마트폰을 쥐고 첫마디를 고민하는 훈남의 진지한 멘붕 표정 실사 사진 생성
  - 1080x1350 카드뉴스 규격 초고화질 서브픽셀 타이포그래피 오버레이
  - 상단 배지['❌ 읽씹 확률 98%', '02 / 05 >'] + 헤드라인 + 망한 첫마디 3대 유형 불릿 + 하단 넘김 CTA 바 일체형 렌더링
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

logger = logging.getLogger("AuraCardnewsS2Topic6Builder")


class AuraCardnewsS2Topic6Builder:
    """Aura 주제 6(AI 첫대화 비서) 2번 현실 공감 카드 전문 빌더"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.wan_client = WanPipelineClient()

    def generate_s2_photo(self, seed: int = None) -> Path:
        """1번 표지 훈남과 100% 동일 인물/의상/장소 + 숏폼 6번 최신 단독 1인 규격 1:1 계승 — 스마트폰을 쥐고 고민하는 실사 생성"""
        if seed is None:
            seed = int(time.time() * 1000) % 100000000

        pos = (
            "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on Apple iPhone 15 Pro, "
            "photographed from 2.0 meters directly in front on Apple iPhone 15 Pro, "
            "solo 1person male, strictly solo single person, no other people in frame, alone in the frame, "
            "perfectly centered in the middle of frame, perfectly frontal portrait view, "
            "no partner, no interlocutor, no second person, no foreground shoulder, "
            "the exact same exceptionally handsome 26-year-old Korean adult man from slide 1 (top 0.5% ultra-sculpted handsome visual, K-drama male lead actor visual, delicate handsome idol-actor appearance, refined masculine aesthetic features), "
            "perfect 8-head-high golden ratio male model proportions, small refined masculine head and face size, slender athletic male physique with broad masculine shoulders, sharp sculpted jawline, "
            "neat stylish dark brown natural dandy haircut with subtle parted fringe framing his face, "
            "authentic real human skin texture with visible fine pores and natural radiant skin tone, "
            "wearing the exact same stylish, trendy modern casual jacket outfit from slide 1, sophisticated 2030 Seoul dating fashion with clean minimalist innerwear and crisp white innerwear, "
            "he is holding his sleek smartphone steadily in both hands at chest level, looking down intently at the glowing smartphone screen in front of his chest with a troubled, slightly anxious and perplexed facial expression, cute delicate head tilt, lips naturally closed together in serious thought, wondering what opener message to text to his match, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "pristine anatomically correct five-finger hands holding the phone edges naturally, completely clear realistic hands, "
            "seated naturally and gracefully alone at the clean polished white marble cafe table in an upright tall 8-head model posture, "
            "sunlit trendy glasshouse boutique cafe in Seongsu-dong during bright afternoon daylight, "
            "floor-to-ceiling glass windows, natural daylight, lush green indoor plants, elegant minimalist cafe architectural interior, "
            "clean polished white marble cafe table in tack sharp f/11 focus, "
            "dramatic professional home shopping studio fill lighting and 3D volumetric contour lighting, studio key lights and soft rim lighting, "
            "studio key lights and soft rim lighting highlighting hair, broad shoulders, and jawline silhouette with rich three-dimensional depth, "
            "bright soft diffused volumetric fill light evenly illuminating the entire face and body with sculpted dimensional volume, "
            "warm soft natural afternoon daylight streaming through the floor-to-ceiling glass windows, "
            "zero dark muddy shadows, zero yellow tint, zero red tint, zero orange tint, neutral accurate white balance, no harsh shadow, no underexposed areas, no dark night lighting, "
            "crystal-clear bright radiant illumination, "
            "candid medium cowboy portrait shot showing upper body, casual jacket, hands holding smartphone in front of chest, and sunlit daytime cafe background, generous headroom above, "
            "realistic skin subsurface scattering, natural subtle skin highlights, NO flat camera flash look, "
            "Raw unedited authentic iPhone 15 Pro 48MP mobile camera capture, realistic human skin texture with visible real pores and authentic fine details, "
            "Apple iPhone 15 Pro Smart HDR photo, authentic mobile camera sensor capture, pristine optical sharpness, rich deep blacks, high micro-contrast, crisp clean highlights, punchy vivid clarity, NO beauty filter, zero skin smoothing, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, completely clear background in tack sharp crisp focus."
        )
        neg = (
            "other people, second person, woman, female, partner, interlocutor, foreground shoulder, talking to someone, "
            "two people, 2 people, couple, yellow tint, red tint, orange tint, "
            "group of people, crowd, background people, blurred person in background, "
            "date partner, conversation partner, facing another person, talking to a woman, interacting with someone, "
            "man's back, back of head, over-the-shoulder, obstructed foreground, foreground arm, foreground hand of another person, "
            "night, rooftop, dark shadow, "
            "night view, night skyline, dark night background, rooftop terrace, open-air rooftop sky lounge, glass balustrade, city neon lights, "
            "Edison string bulb lights, string lights, patio lanterns, warm golden patio lamps, architectural uplighting, dark ambient night lighting, "
            "dark muddy shadow, gloomy, underexposed, dim lighting, warm yellow cast, reddish skin tone, orange color cast, "
            "phone near ear, phone on ear, phone to ear, holding phone to ear, calling to ear, phone touching head, phone touching ear, "
            "deformed hands, distorted fingers, extra fingers, missing fingers, fused fingers, mutated hands, bad hands, bad fingers, poorly drawn hands, "
            "open mouth, parted lips, visible teeth, showing teeth, laughing, grinning, smiling wide, smiling, "
            "ugly face, old man, middle aged, chubby, fat face, broad jaw, double chin, distorted features, bad eyes, asymmetric face, "
            "doll, doll face, porcelain skin, plastic skin, airbrushed skin, beauty filter, skin smoothing, "
            "blurry, lens blur, out of focus, bokeh blur, shallow depth of field, "
            "cartoon, anime, 3d render, cgi, illustration, drawing, watermark, text"
        )

        logger.info(f"🎨 [AuraCardnewsS2Topic6] 6번 주제 2번 고민하는 훈남 실사 생성 시작 (Seed={seed})...")
        raw_path = self.wan_client.generate_t2i_master(
            positive_prompt=pos,
            negative_prompt=neg,
            width=832,
            height=1216,
            seed=seed,
            prefix="aura_topic6_s2_male_troubled"
        )
        logger.info(f"✅ [AuraCardnewsS2Topic6] 2번 훈남 원본 사진 생성 완료: {raw_path}")
        return Path(raw_path)

    def render_slide(self, photo_path: Path, output_png_path: str, copy_data: dict = None) -> str:
        """Playwright로 1080x1350 카드뉴스 규격 초고화질 타이포그래피 렌더링 (제미나이 동적 카피 주입)"""
        import base64

        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(str(photo_path), "rb") as f:
            photo_b64 = base64.b64encode(f.read()).decode("utf-8")

        # 제미나이 동적 카피 또는 기본값
        s2_copy = copy_data.get("slide2", {}) if copy_data else {}
        badge = s2_copy.get("badge", "❌ 읽씹 확률 98%")
        h1_line1 = s2_copy.get("headline_line1", '"안녕하세요~ 주말 잘 보내세요!"는')
        h1_line2 = s2_copy.get("headline_line2", "왜 100% 읽씹당할까요?")
        subtitle = s2_copy.get("subtitle", "매력적인 이성은 하루에도 똑같은 복붙 인사를 수십 개씩 받습니다.")

        default_bullets = [
            "질문이 없거나 대답하기 애매한 단답형 인사는 탈락 1순위",
            "과한 호구조사('사는 곳이 어디세요?')는 경계심과 피로감 유발",
            "상대의 호기심을 자극하고 대화 리듬을 여는 맞춤 '오프너'가 필요"
        ]
        bullets = s2_copy.get("bullets", default_bullets)
        while len(bullets) < 3:
            bullets.append("Aura AI 실시간 매칭 솔루션")

        cta_text = s2_copy.get("cta_text", "👉 옆으로 넘겨서 AI 프로필 스캔 보기 (2/5) >")
        naver_search_html = render_naver_search_bar_html(brand="aura")

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Aura Topic 6 Slide 2 (1080x1350)</title>
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

    /* 헤드라인 텍스트 드롭 섀도우 */
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
  <img src="data:image/jpeg;base64,{photo_b64}" class="bg-photo" alt="Slide 2 Photo" />

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
      02 / 05 &gt;
    </div>
  </div>

  <!-- 4. Bottom Content Area (Headline + Bullets + CTA) -->
  <div class="absolute bottom-10 left-8 right-8 z-10 flex flex-col items-start space-y-4">
    
    <!-- Category Badge -->
    <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-gradient-to-r from-rose-500 to-red-600 text-white text-sm font-black shadow-lg">
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
        <span class="text-rose-400 text-lg">🚫</span>
        <span>{bullets[0]}</span>
      </div>
      <div class="flex items-start gap-2.5 text-base font-bold text-slate-200 text-subhead">
        <span class="text-rose-400 text-lg">🚫</span>
        <span>{bullets[1]}</span>
      </div>
      <div class="flex items-start gap-2.5 text-base font-bold text-amber-300 text-subhead">
        <span class="text-amber-400 text-lg">💡</span>
        <span>{bullets[2]}</span>
      </div>
    </div>

      <!-- 하단 네이버 공식 검색창 UI 바 (숏폼 일체형) -->
      {naver_search_html}

  </div>

</body>
</html>
"""

        logger.info(f"🎨 [AuraCardnewsS2Topic6] 1080x1350 2번 슬라이드 렌더링 시작 -> {out_path.name}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
            page.set_content(html_content, wait_until="networkidle")
            page.screenshot(path=str(out_path), full_page=True)
            browser.close()

        logger.info(f"✅ [AuraCardnewsS2Topic6] 2번 슬라이드 렌더링 완료: {out_path}")
        return str(out_path)

    def produce(self, target_dir: str = None, copy_data: dict = None, seed: int = None) -> str:
        """사진 생성부터 2번 카드뉴스 렌더링까지 일괄 실행"""
        if not target_dir:
            from .aura_cardnews_storage import AuraCardnewsStorage
            t_path = AuraCardnewsStorage.create_target_directory(theme_code="smart_opener")
        else:
            t_path = Path(target_dir)
            t_path.mkdir(parents=True, exist_ok=True)

        # 1. 고민하는 훈남 실사 사진 생성
        raw_photo = self.generate_s2_photo(seed=seed)

        # 2. 1080x1350 카드뉴스 렌더링
        slide2_path = t_path / "slide_2.png"
        self.render_slide(raw_photo, str(slide2_path), copy_data=copy_data)

        return str(slide2_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    builder = AuraCardnewsS2Topic6Builder()
    builder.produce()
