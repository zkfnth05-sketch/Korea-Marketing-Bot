# -*- coding: utf-8 -*-
"""
AuraCardnewsS2MaleProfileBuilder - 📱 [Aura 카드뉴스 2번 전용 숏폼 6번 골든 훈남 프로필 매립 빌더]
=============================================================================================
• 역할:
  - 숏폼 6번("AI 첫대화 비서")의 검증된 [K-드라마 남주인공 / 아이돌 배우급 골든 락]으로 Wan 2.1 T2I 실사 훈남 생성
  - 대표님께서 지정하신 Aura 실제 프로필 탐색 화면의 카드 영역(437x655)에 서브픽셀 정밀 매립
  - 훈남 실사 사진의 상반신(어깨, 자켓, 가슴)이 자연스럽게 이어지도록 그라데이션 스크림 + 텍스트(도윤, 29 / 태그들) 고화질 결합
  - 상단 뱃지(45% 일치, 공통점 3개) 및 카드뉴스 정규 헤더(💖 AURA | 50:50 남녀 황금 성비율 + '02 / 05 >') 결합
"""

import os
import sys
import time
import logging
from pathlib import Path
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from core.engine.wan_pipeline_client import WanPipelineClient

logger = logging.getLogger("AuraCardnewsS2MaleProfileBuilder")


class AuraCardnewsS2MaleProfileBuilder:
    """Aura 주제 3(50:50 VIP 게이트) 2번 카드 전용 훈남 프로필 매립 빌더"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.template_path = self.base_dir / "assets" / "aura_male_profile_card_template.png"
        self.wan_client = WanPipelineClient()

    def generate_male_photo(self, seed: int = None) -> Path:
        """숏폼 6번 골든 헌법 기반 Wan 2.1 T2I 훈남 실사 인물 사진 생성"""
        if seed is None:
            seed = int(time.time() * 1000) % 100000000

        pos = (
            "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
            "an exceptionally handsome 27-year-old Korean adult man (K-drama male lead actor visual, delicate handsome idol-actor appearance, refined aesthetic features), "
            "perfect 8-head-high golden ratio male model proportions, small refined masculine head and face size, slender athletic male physique with broad masculine shoulders, "
            "soft gentle smile with lips closed together, refined handsome features, sharp sculpted jawline with natural subtle directional shadow, charismatic warm romantic gaze, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "neat stylish dark brown natural dandy haircut with subtle parted fringe framing his face, "
            "authentic real human skin texture with visible fine pores and natural skin tone, "
            "wearing stylish sophisticated civilian dating clothes, a clean chic tailored blazer jacket over a minimalist crisp white inner shirt, "
            "candid medium cowboy portrait shot showing upper body, shoulders, and chest, generous headroom above, "
            "modern warm architectural interior with soft golden ambient lighting, elegant background in tack sharp f/11 focus, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, Apple iPhone 15 Pro Smart HDR photo."
        )
        neg = (
            "open mouth, parted lips, visible teeth, showing teeth, laughing, grinning, smiling wide, "
            "ugly face, old man, middle aged, chubby, fat face, broad jaw, double chin, distorted features, bad eyes, asymmetric face, "
            "doll, doll face, porcelain skin, plastic skin, airbrushed skin, beauty filter, skin smoothing, "
            "blurry, lens blur, out of focus, bokeh blur, shallow depth of field, deformed hands, extra fingers, missing fingers, bad fingers, "
            "cartoon, anime, 3d render, cgi, illustration, drawing, watermark, text, female, woman"
        )

        logger.info(f"🎨 [AuraCardnewsS2] Wan 2.1 K-드라마 남주급 훈남 실사 생성 시작 (Seed={seed})...")
        raw_path = self.wan_client.generate_t2i_master(
            positive_prompt=pos,
            negative_prompt=neg,
            width=832,
            height=1216,
            seed=seed,
            prefix="aura_cardnews_s2_male"
        )
        logger.info(f"✅ [AuraCardnewsS2] 훈남 원본 사진 생성 완료: {raw_path}")
        return Path(raw_path)

    def _render_perfect_card_layer(self, male_photo_path: Path, card_w: int = 437, card_h: int = 655) -> Image.Image:
        """훈남 사진 전신 + 그라데이션 스크림 + 프로필 텍스트를 결합한 완벽한 둥근 카드 생성"""
        import base64

        with open(str(male_photo_path), "rb") as f:
            photo_b64 = base64.b64encode(f.read()).decode("utf-8")

        html_card = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; user-select: none; font-family: 'Pretendard', sans-serif; }}
    body {{
      width: {card_w}px;
      height: {card_h}px;
      overflow: hidden;
      background: transparent;
    }}
    .card-box {{
      width: {card_w}px;
      height: {card_h}px;
      border-radius: 28px;
      overflow: hidden;
      position: relative;
      box-shadow: 0 10px 40px rgba(0,0,0,0.8);
      background: #111;
    }}
    .photo-bg {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: center top;
      position: absolute;
      top: 0;
      left: 0;
    }}
    .bottom-scrim {{
      position: absolute;
      bottom: 0;
      left: 0;
      width: 100%;
      height: 52%;
      background: linear-gradient(to top, rgba(0, 0, 0, 0.94) 0%, rgba(0, 0, 0, 0.75) 45%, rgba(0, 0, 0, 0) 100%);
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      padding: 0 24px 22px;
    }}
  </style>
</head>
<body>
  <div class="card-box">
    <!-- 1. 훈남 실사 사진 전체 배경 -->
    <img class="photo-bg" src="data:image/png;base64,{photo_b64}" alt="Male Profile" />

    <!-- 2. 상단 노란 알약 뱃지 -->
    <div class="absolute top-4 left-0 w-full px-5 flex justify-between items-center z-10">
      <span class="bg-amber-400 text-slate-950 font-bold text-xs px-3.5 py-1.5 rounded-full shadow-md">
        45% 일치
      </span>
      <span class="bg-amber-400 text-slate-950 font-bold text-xs px-3.5 py-1.5 rounded-full shadow-md">
        공통점 3개
      </span>
    </div>

    <!-- 3. 하단 그라데이션 스크림 + 프로필 정보 -->
    <div class="bottom-scrim z-10">
      <div class="flex items-baseline gap-2 mb-1">
        <h2 class="text-white text-3xl font-extrabold tracking-tight">도윤</h2>
        <span class="text-white/90 text-2xl font-bold">29</span>
      </div>
      <p class="text-zinc-300 text-sm font-medium mb-3">
        새로운 만남을 기다립니다!
      </p>
      <!-- 태그들 -->
      <div class="flex flex-wrap gap-1.5">
        <span class="bg-black/60 backdrop-blur-md border border-white/15 text-white/90 text-xs px-3 py-1 rounded-full font-medium">독서</span>
        <span class="bg-black/60 backdrop-blur-md border border-white/15 text-white/90 text-xs px-3 py-1 rounded-full font-medium">영화 감상</span>
        <span class="bg-black/60 backdrop-blur-md border border-white/15 text-white/90 text-xs px-3 py-1 rounded-full font-medium">맛집 탐방</span>
        <span class="bg-black/60 backdrop-blur-md border border-white/15 text-white/90 text-xs px-3 py-1 rounded-full font-medium">여행</span>
      </div>
    </div>
  </div>
</body>
</html>"""

        temp_card_html = self.base_dir / "temp_card_render.html"
        with open(temp_card_html, "w", encoding="utf-8") as f:
            f.write(html_card)

        card_png = self.base_dir / "temp_card_render.png"
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": card_w, "height": card_h}, device_scale_factor=1)
            page.goto(temp_card_html.as_uri())
            page.wait_for_timeout(400)
            page.screenshot(path=str(card_png), type="png", omit_background=True)
            browser.close()

        if temp_card_html.exists():
            temp_card_html.unlink()

        rendered_card = Image.open(str(card_png)).convert("RGBA")
        if card_png.exists():
            card_png.unlink()

        return rendered_card

    def build_s2_card(self, output_png_path: str, custom_photo_path: Path = None, seed: int = None) -> str:
        """프로필 카드 영역 매립 및 1080x1350 카드뉴스 2번 완성본 렌더링"""
        if not self.template_path.exists():
            raise FileNotFoundError(f"프로필 카드 템플릿이 없습니다: {self.template_path}")

        # 1. 훈남 실사 사진 확보 (지정된 사진 없으면 기존 생성본 또는 신규 생성)
        if custom_photo_path and Path(custom_photo_path).exists():
            male_photo_p = Path(custom_photo_path)
        else:
            default_candidate = Path(r"D:\ComfyUI_Wan_Engine\ComfyUI\output\aura_cardnews_s2_male_00001_.png")
            if default_candidate.exists():
                male_photo_p = default_candidate
                logger.info(f"📸 기존 생성된 훈남 사진 재사용: {male_photo_p}")
            else:
                male_photo_p = self.generate_male_photo(seed=seed)

        # 2. 템플릿 로드 (758 x 1024 RGBA)
        template_img = Image.open(str(self.template_path)).convert("RGBA")
        t_w, t_h = template_img.size

        # 3. 완벽한 카드 레이어 렌더링 (437 x 655)
        perfect_card = self._render_perfect_card_layer(male_photo_p, card_w=437, card_h=655)

        # 4. 템플릿의 카드 자리에 결합
        template_img.paste(perfect_card, (157, 111), mask=perfect_card)

        # 5. 1080x1350 카드뉴스 규격 캔버스 중앙에 모바일 화면 배치
        final_canvas = Image.new("RGBA", (1080, 1350), (10, 10, 15, 255))
        scale_target = 1350 / t_h
        scaled_w = int(t_w * scale_target)
        scaled_h = 1350
        resized_template = template_img.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)
        paste_x = (1080 - scaled_w) // 2
        final_canvas.paste(resized_template, (paste_x, 0), mask=resized_template)

        # 6. 상단 브랜드 헤더 배지 ('💖 AURA | 50:50 남녀 황금 성비율' + '02 / 05 >')
        html_header = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; font-family: 'Pretendard', sans-serif; }
    body { width: 1080px; height: 1350px; overflow: hidden; background: transparent; padding: 25px 40px; }
  </style>
</head>
<body>
  <div class="flex justify-between items-center w-full z-30">
    <!-- Brand Badge (깔끔한 다크 글래스 필터로 배경 완벽 차폐) -->
    <div class="inline-flex items-center gap-2.5 bg-[#0a0c14] border border-white/20 rounded-full py-2.5 px-5 shadow-[0_4px_25px_rgba(0,0,0,0.95)]">
      <span class="text-rose-400 text-sm">💖</span>
      <span class="text-white font-extrabold text-sm tracking-wider">AURA</span>
      <span class="w-1.5 h-1.5 rounded-full bg-white/40"></span>
      <span class="text-amber-300 font-bold text-xs tracking-wide">50:50 남녀 황금 성비율</span>
    </div>

    <!-- Page Index -->
    <div class="bg-[#0a0c14] border border-white/20 rounded-full py-2.5 px-5 shadow-[0_4px_25px_rgba(0,0,0,0.95)] text-amber-400 font-extrabold text-sm tracking-wider">
      02 / 05 &gt;
    </div>
  </div>
</body>
</html>"""

        temp_html = self.base_dir / "temp_s2_header.html"
        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(html_header)

        header_png = self.base_dir / "temp_s2_header.png"
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
            page.goto(temp_html.as_uri())
            page.wait_for_timeout(400)
            page.screenshot(path=str(header_png), type="png", omit_background=True)
            browser.close()

        if temp_html.exists():
            temp_html.unlink()

        header_overlay = Image.open(str(header_png)).convert("RGBA")
        final_result = Image.alpha_composite(final_canvas, header_overlay)

        if header_png.exists():
            header_png.unlink()

        # 7. 저장
        out_p = Path(output_png_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        final_result.convert("RGB").save(str(out_p), "PNG", quality=95)

        logger.info(f"🎉 [AuraCardnewsS2MaleProfileBuilder] 2번 카드 완벽 렌더링 완료: {out_p}")
        return str(out_p)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    builder = AuraCardnewsS2MaleProfileBuilder()
    out = r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\아우라\아우라_KO_vip_gate_5050_20260930_1709\slide_2.png"
    res = builder.build_s2_card(output_png_path=out)
    print("Done Slide 2:", res)
