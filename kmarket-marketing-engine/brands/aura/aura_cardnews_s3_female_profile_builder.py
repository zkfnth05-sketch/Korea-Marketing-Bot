# -*- coding: utf-8 -*-
"""
AuraCardnewsS3FemaleProfileBuilder - 📱 [Aura 카드뉴스 3번 전용 고양이상 섹시 여성 프로필 매립 빌더]
=============================================================================================
• 역할:
  - 아주 매혹적인 고양이상(Feline Cat-like Eyes)의 26세 섹시·청순 여성 실사 T2I 생성 (Wan 2.1)
  - 8등신 소두 모델 비율, 완벽한 턱선, 입 다문 미소, 치아 노출 0%
  - 대표님 지시대로 여성용 프로필 정보(서아 26, '주말에 분위기 좋은 와인바 갈래요? 🍷', [와인][필라테스][전시회][드라이브])로 전면 개편
  - 상단 뱃지: [98% 일치] [취향 저격 💖]
  - 상단 공식 카드뉴스 인덱스 ('💖 아우라 AI 데이팅 | 현재 100% 무료 남녀 황금 성비율' + '03 / 05 >') 결합
  - 바탕화면 타겟 폴더의 slide_3.png로 영구 저장
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

logger = logging.getLogger("AuraCardnewsS3FemaleProfileBuilder")


class AuraCardnewsS3FemaleProfileBuilder:
    """Aura 주제 3(50:50 VIP 게이트) 3번 카드 전용 고양이상 여성 프로필 빌더"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.template_path = self.base_dir / "assets" / "aura_male_profile_card_template.png"
        self.wan_client = WanPipelineClient()

    def generate_female_photo(self, seed: int = None) -> Path:
        """아주 매혹적인 고양이상 섹시 여성 실사 사진 생성 (Wan 2.1)"""
        if seed is None:
            seed = int(time.time() * 1000) % 100000000

        pos = (
            "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
            "an exceptionally gorgeous glamorous 25-year-old Korean woman with a breathtakingly seductive feline cat-like facial visual, "
            "captivating alluring cat-like almond hazel eyes with subtle sharp winged eyeliner, sharp high cheekbones, delicate cute button nose, sculpted elegant jawline, "
            "perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck, graceful collarbone, "
            "flawless luminous glass skin with soft natural peach blush, realistic skin pores and authentic fine skin texture, "
            "natural full lips gently closed together with a subtle alluring confident smile, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "voluminous silky dark wavy hair falling gracefully over shoulders, "
            "wearing stylish sophisticated civilian dating clothes, an elegant chic off-shoulder knit top, modern luxurious date-night fashion, "
            "candid medium cowboy portrait shot showing upper body, shoulders, and chest, generous headroom above, "
            "upscale modern wine lounge interior with warm golden ambient lighting and soft bokeh lights, elegant background in tack sharp f/11 focus, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, Apple iPhone 15 Pro Smart HDR photo."
        )
        neg = (
            "open mouth, parted lips, visible teeth, showing teeth, laughing, grinning, smiling wide, "
            "ugly face, old woman, chubby, fat face, broad jaw, double chin, distorted features, bad eyes, asymmetric face, "
            "doll, doll face, porcelain skin, plastic skin, airbrushed skin, beauty filter, skin smoothing, "
            "blurry, lens blur, out of focus, bokeh blur, shallow depth of field, deformed hands, extra fingers, missing fingers, bad fingers, "
            "cartoon, anime, 3d render, cgi, illustration, drawing, watermark, text, male, man"
        )

        logger.info(f"🎨 [AuraCardnewsS3] Wan 2.1 고양이상 섹시 여성 실사 생성 시작 (Seed={seed})...")
        raw_path = self.wan_client.generate_t2i_master(
            positive_prompt=pos,
            negative_prompt=neg,
            width=832,
            height=1216,
            seed=seed,
            prefix="aura_cardnews_s3_female"
        )
        logger.info(f"✅ [AuraCardnewsS3] 고양이상 여성 원본 사진 생성 완료: {raw_path}")
        return Path(raw_path)

    def _render_perfect_card_layer(self, female_photo_path: Path, card_w: int = 437, card_h: int = 655) -> Image.Image:
        """여성 실사 사진 전신 + 그라데이션 스크림 + 여성용 프로필 텍스트를 결합한 카드 생성"""
        import base64

        with open(str(female_photo_path), "rb") as f:
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
    <!-- 1. 고양이상 섹시 여성 실사 사진 전체 배경 -->
    <img class="photo-bg" src="data:image/png;base64,{photo_b64}" alt="Female Profile" />

    <!-- 2. 상단 노란 알약 뱃지 (여성용 맞춤 매칭) -->
    <div class="absolute top-4 left-0 w-full px-5 flex justify-between items-center z-10">
      <span class="bg-amber-400 text-slate-950 font-bold text-xs px-3.5 py-1.5 rounded-full shadow-md">
        98% 일치
      </span>
      <span class="bg-amber-400 text-slate-950 font-bold text-xs px-3.5 py-1.5 rounded-full shadow-md">
        취향 저격 💖
      </span>
    </div>

    <!-- 3. 하단 그라데이션 스크림 + 여성 프로필 정보 (서아 26) -->
    <div class="bottom-scrim z-10">
      <div class="flex items-baseline gap-2 mb-1">
        <h2 class="text-white text-3xl font-extrabold tracking-tight">서아</h2>
        <span class="text-white/90 text-2xl font-bold">26</span>
      </div>
      <p class="text-zinc-200 text-sm font-medium mb-3">
        주말에 분위기 좋은 와인바 갈래요? 🍷
      </p>
      <!-- 여성 라이프스타일 둥근 알약 태그들 -->
      <div class="flex flex-wrap gap-1.5">
        <span class="bg-black/60 backdrop-blur-md border border-white/15 text-white/90 text-xs px-3 py-1 rounded-full font-medium">와인</span>
        <span class="bg-black/60 backdrop-blur-md border border-white/15 text-white/90 text-xs px-3 py-1 rounded-full font-medium">필라테스</span>
        <span class="bg-black/60 backdrop-blur-md border border-white/15 text-white/90 text-xs px-3 py-1 rounded-full font-medium">전시회</span>
        <span class="bg-black/60 backdrop-blur-md border border-white/15 text-white/90 text-xs px-3 py-1 rounded-full font-medium">드라이브</span>
      </div>
    </div>
  </div>
</body>
</html>"""

        temp_card_html = self.base_dir / "temp_card_s3_render.html"
        with open(temp_card_html, "w", encoding="utf-8") as f:
            f.write(html_card)

        card_png = self.base_dir / "temp_card_s3_render.png"
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

    def build_s3_card(self, output_png_path: str, custom_photo_path: Path = None, seed: int = None) -> str:
        """여성 프로필 카드 영역 매립 및 1080x1350 카드뉴스 3번 완성본 렌더링"""
        if not self.template_path.exists():
            raise FileNotFoundError(f"프로필 카드 템플릿이 없습니다: {self.template_path}")

        # 1. 고양이상 여성 실사 사진 확보 (지정 사진 없으면 Wan 2.1 신규 생성)
        if custom_photo_path and Path(custom_photo_path).exists():
            female_photo_p = Path(custom_photo_path)
            logger.info(f"📸 기존 지정 여성 사진 로드: {female_photo_p}")
        else:
            female_photo_p = self.generate_female_photo(seed=seed)

        # 2. 템플릿 로드 (758 x 1024 RGBA)
        template_img = Image.open(str(self.template_path)).convert("RGBA")
        t_w, t_h = template_img.size

        # 3. 완벽한 여성 카드 레이어 렌더링 (437 x 655)
        perfect_card = self._render_perfect_card_layer(female_photo_p, card_w=437, card_h=655)

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

        # 6. 상단 브랜드 헤더 배지 ('💖 아우라 AI 데이팅 | 현재 100% 무료 남녀 황금 성비율' + '03 / 05 >')
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
    <!-- Brand Badge -->
    <div class="inline-flex items-center gap-2.5 bg-[#0a0c14] border border-white/20 rounded-full py-2.5 px-5 shadow-[0_4px_25px_rgba(0,0,0,0.95)]">
      <span class="text-rose-400 text-sm">💖</span>
      <span class="text-white font-extrabold text-sm tracking-wider">AURA</span>
      <span class="w-1.5 h-1.5 rounded-full bg-white/40"></span>
      <span class="text-amber-300 font-bold text-xs tracking-wide">현재 100% 무료</span>
    </div>

    <!-- Page Index -->
    <div class="bg-[#0a0c14] border border-white/20 rounded-full py-2.5 px-5 shadow-[0_4px_25px_rgba(0,0,0,0.95)] text-amber-400 font-extrabold text-sm tracking-wider">
      03 / 05 &gt;
    </div>
  </div>
</body>
</html>"""

        temp_html = self.base_dir / "temp_s3_header.html"
        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(html_header)

        header_png = self.base_dir / "temp_s3_header.png"
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

        logger.info(f"🎉 [AuraCardnewsS3FemaleProfileBuilder] 3번 카드 완벽 렌더링 완료: {out_p}")
        return str(out_p)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    builder = AuraCardnewsS3FemaleProfileBuilder()
    out = r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\아우라\아우라_KO_vip_gate_5050_20260930_1709\slide_3.png"
    res = builder.build_s3_card(output_png_path=out)
    print("Done Slide 3:", res)
