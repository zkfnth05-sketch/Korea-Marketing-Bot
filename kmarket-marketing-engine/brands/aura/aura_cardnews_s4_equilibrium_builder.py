# -*- coding: utf-8 -*-
"""
AuraCardnewsS4EquilibriumBuilder - 📱 [Aura 카드뉴스 4번 전용 공식 50:50 게이트 실제 앱 화면 렌더러]
=============================================================================================
• 역할:
  - 대표님께서 지정하신 Aura 실제 앱 50:50 게이트 화면(aura_equilibrium_screen.png)을
  - 카드뉴스 4번 슬라이드(04 / 05 >)로 완벽 렌더링하여 바탕화면 타겟 폴더의 slide_4.png로 저장
"""

import os
import logging
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

logger = logging.getLogger("AuraCardnewsS4EquilibriumBuilder")


class AuraCardnewsS4EquilibriumBuilder:
    """Aura 주제 3(50:50 VIP 게이트) 4번 카드 전용 실물 화면 빌더"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.asset_path = self.base_dir / "assets" / "aura_equilibrium_screen.png"

    def build_s4_card(self, output_png_path: str) -> str:
        """1080x1350 규격 4번 카드 렌더링"""
        if not self.asset_path.exists():
            raise FileNotFoundError(f"Aura 게이트 화면 에셋이 없습니다: {self.asset_path}")

        base_img = Image.open(str(self.asset_path)).convert("RGBA")
        if base_img.size != (1080, 1350):
            base_img = base_img.resize((1080, 1350), Image.Resampling.LANCZOS)

        html_content = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
      font-family: 'Pretendard', sans-serif;
    }
    body {
      width: 1080px;
      height: 1350px;
      overflow: hidden;
      background: transparent;
      padding: 30px 40px;
    }
  </style>
</head>
<body>
  <div class="flex justify-between items-center w-full z-20">
    <!-- Brand Badge -->
    <div class="inline-flex items-center gap-2.5 bg-slate-900/90 backdrop-blur-md border border-white/20 rounded-full py-2.5 px-5 shadow-2xl">
      <span class="text-rose-400 text-sm">💖</span>
      <span class="text-white font-extrabold text-sm tracking-wider">AURA</span>
      <span class="w-1.5 h-1.5 rounded-full bg-white/40"></span>
      <span class="text-amber-300 font-bold text-xs tracking-wide">50:50 남녀 황금 성비율</span>
    </div>

    <!-- Page Index -->
    <div class="bg-slate-900/90 backdrop-blur-md border border-white/20 rounded-full py-2.5 px-5 shadow-2xl text-amber-400 font-extrabold text-sm tracking-wider">
      04 / 05 &gt;
    </div>
  </div>
</body>
</html>"""

        temp_html = self.base_dir / "temp_s4_header.html"
        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(html_content)

        header_png = self.base_dir / "temp_s4_header.png"
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
        combined = Image.alpha_composite(base_img, header_overlay)

        if header_png.exists():
            header_png.unlink()

        out_p = Path(output_png_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        combined.convert("RGB").save(str(out_p), "PNG", quality=95)

        logger.info(f"✅ [AuraCardnewsS4EquilibriumBuilder] 4번 카드 렌더링 완료: {out_p}")
        return str(out_p)


if __name__ == "__main__":
    builder = AuraCardnewsS4EquilibriumBuilder()
    out = r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\아우라\아우라_KO_vip_gate_5050_20260930_1709\slide_4.png"
    res = builder.build_s4_card(out)
    print("Done Slide 4:", res)
