# -*- coding: utf-8 -*-
"""
AuraCardnewsS1Topic5Builder - ⚖️ [Aura 카드뉴스 5번 주제 '가치관 밸런스 매칭' 1번 표지 전문 빌더]
========================================================================================
• 역할:
  - 숏폼 5번 주제('가치관 밸런스 매칭')의 1번 표지 실시간 초고해상도 렌더링
  - 고양이상 21세 여신 (화이트 골지 스퀘어넥 룩 + 연남동 브런치 카페)
  - 1080x1350 카드뉴스 규격 초고화질 서브픽셀 타이포그래피 오버레이
  - ComfyUI Wan 2.1 가용 시 신규 생성, 오프라인 시 마스터 에셋 기반 100% 무인 자율 렌더링 보장
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

logger = logging.getLogger("AuraCardnewsS1Topic5Builder")


class AuraCardnewsS1Topic5Builder:
    """Aura 주제 5(가치관 밸런스 매칭) 1번 표지 전문 빌더"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.wan_client = WanPipelineClient()
        self.asset_base = self.base_dir / "assets" / "aura_topic5_cover_base.png"

    def get_or_generate_cover_photo(self, seed: int = None) -> Path:
        """Wan 2.1 가용 시 실사 생성, 부재 시 에셋 기반 반환"""
        if self.wan_client.check_health():
            try:
                if seed is None:
                    seed = int(time.time() * 1000) % 100000000

                pos = (
                    "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
                    "a stunningly gorgeous 21-year-old Korean college goddess (cat-like facial features, large alluring expressive eyes, delicate feline facial proportions, radiant youthful beauty), "
                    "slender feminine figure with elegant collarbones, natural skin texture with visible pores and subtle healthy glow, "
                    "charming subtle cat-smile with lips gently closed, captivating gaze looking directly at camera, strictly zero open mouth, strictly no teeth showing, "
                    "stylish glossy soft black shoulder-length wolf cut with airy see-through bangs framing her delicate face, "
                    "wearing a chic fitted white ribbed square-neck knit top, sophisticated trendy Yeonnam-dong brunch date fashion, "
                    "sitting at a stylish aesthetic window-seat cafe table in Yeonnam-dong, warm morning natural golden sunlight streaming through clean sheer glass windows, "
                    "marble table with iced latte glass and delicate brunch dessert dish in foreground, aesthetic cafe interior background in gentle soft bokeh, "
                    "candid medium bust shot, f/11 deep pan-focus, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, Apple iPhone 15 Pro Smart HDR photo."
                )
                neg = (
                    "open mouth, parted lips, visible teeth, showing teeth, laughing, grinning, smiling wide, "
                    "ugly face, old woman, chubby, distorted features, bad eyes, asymmetric face, doll, porcelain skin, plastic skin, "
                    "blurry, lens blur, out of focus, bokeh blur, deformed hands, cartoon, anime, 3d render, cgi, watermark, text, male, man"
                )

                logger.info(f"🎨 [AuraCardnewsS1Topic5] 5번 숏폼 여신 실사 생성 시작 (Seed={seed})...")
                raw_path = self.wan_client.generate_t2i_master(
                    positive_prompt=pos,
                    negative_prompt=neg,
                    width=832,
                    height=1216,
                    seed=seed,
                    prefix="aura_topic5_cover_female"
                )
                logger.info(f"✅ [AuraCardnewsS1Topic5] 여신 원본 사진 생성 완료: {raw_path}")
                return Path(raw_path)
            except Exception as e:
                logger.warning(f"⚠️ [AuraCardnewsS1Topic5] Wan 2.1 생성 실패 ({e}) -> 마스터 고화질 에셋 폴백")

        if self.asset_base.exists():
            logger.info(f"📱 [AuraCardnewsS1Topic5] 마스터 고화질 에셋 활용: {self.asset_base}")
            return self.asset_base

        # 최종 안전망: 다크 럭셔리 캔버스 생성
        fallback_path = self.base_dir / "temp_s1_topic5_canvas.png"
        img = Image.new("RGB", (1080, 1350), (20, 24, 39))
        img.save(str(fallback_path), "PNG")
        return fallback_path

    def render_cover_slide(self, photo_path: Path, output_png_path: str, copy_data: dict = None) -> str:
        """Playwright로 1080x1350 카드뉴스 규격 초고화질 타이포그래피 표지 렌더링"""
        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(str(photo_path), "rb") as f:
            photo_b64 = base64.b64encode(f.read()).decode("utf-8")

        # 제미나이 동적 카피 또는 테마 기본값
        s1_copy = copy_data.get("slide1", {}) if copy_data else {}
        badge = s1_copy.get("badge", "⚖️ 2030 소개팅 가치관 토론")
        h1_line1 = s1_copy.get("headline_line1", "소개팅 첫 만남 더치페이,")
        h1_line2 = s1_copy.get("headline_line2", "칼반띵 vs 2차 사기? 여러분의 선택은?")
        subtitle = s1_copy.get("subtitle", "연애관, 연락 빈도, 데이트 비용까지 100% 통하는 상대만 매칭")

        default_bullets = [
            "첫 만남 계산부터 연락 스타일, 남사친 문제까지 사전 매칭",
            "가치관 안 맞아 상처받던 소개팅은 이제 그만",
            "50:50 황금 성비율 • 나와 핏이 딱 맞는 사람만 발견"
        ]
        bullets = s1_copy.get("bullets", default_bullets)
        while len(bullets) < 3:
            bullets.append("Aura AI 가치관 밸런스 매칭")

        cta_text = s1_copy.get("cta_text", "👉 옆으로 넘겨서 3대 가치관 대결 보기 (1/5) >")

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Aura Topic 5 Cover Slide (1080x1350)</title>
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
      background: #0B0E14;
      overflow: hidden;
      position: relative;
    }}
  </style>
</head>
<body class="flex flex-col justify-between">

  <!-- 1. 배경 인물 실사 이미지 레이어 -->
  <div class="absolute inset-0 z-0 overflow-hidden">
    <img src="data:image/png;base64,{photo_b64}" class="w-full h-full object-cover object-center transform scale-[1.02]" alt="Cover Visual" />
    <!-- 상하단 멀티 레이어 럭셔리 비네팅 그라디언트 -->
    <div class="absolute inset-0 bg-gradient-to-t from-[#0B0E14] via-[#0B0E14]/40 to-transparent" style="bottom: 0; height: 65%;"></div>
    <div class="absolute inset-0 bg-gradient-to-b from-[#0B0E14]/90 via-[#0B0E14]/30 to-transparent" style="top: 0; height: 35%;"></div>
  </div>

  <!-- 2. 상단 헤더 영역 (50:50 황금 성비 배지 & 테마 태그) -->
  <div class="relative z-10 pt-14 px-12 flex justify-between items-center">
    <div class="inline-flex items-center gap-2.5 px-5 py-2.5 rounded-full bg-black/60 backdrop-blur-md border border-[#F43F5E]/40 shadow-lg">
      <span class="w-2.5 h-2.5 rounded-full bg-[#F43F5E] animate-pulse"></span>
      <span class="text-white text-lg font-extrabold tracking-tight">{badge}</span>
    </div>

    <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-md border border-white/20">
      <span class="text-[#FBBF24] text-sm font-black tracking-wider">AURA BALANCE #05</span>
    </div>
  </div>

  <!-- 3. 하단 메인 타이포그래피 & 핵심 카드 영역 -->
  <div class="relative z-10 px-12 pb-14 flex flex-col gap-6">

    <!-- 메인 헤드라인 (가독성 극대화) -->
    <div class="flex flex-col gap-2">
      <h2 class="text-white text-4xl font-extrabold leading-tight tracking-tight drop-shadow-md">
        {h1_line1}
      </h2>
      <h1 class="text-5xl font-black leading-tight tracking-tight bg-gradient-to-r from-[#F43F5E] via-[#FB7185] to-[#FDA4AF] bg-clip-text text-transparent drop-shadow-lg">
        {h1_line2}
      </h1>
      <p class="text-slate-300 text-2xl font-medium mt-2 leading-relaxed drop-shadow">
        {subtitle}
      </p>
    </div>

    <!-- 3단 핵심 요약 불릿 박스 -->
    <div class="bg-black/60 backdrop-blur-xl border border-white/15 rounded-3xl p-6 shadow-2xl flex flex-col gap-3.5">
      <div class="flex items-center gap-3.5">
        <div class="w-7 h-7 rounded-full bg-[#F43F5E]/20 border border-[#F43F5E] flex items-center justify-center shrink-0">
          <span class="text-[#F43F5E] text-sm font-black">✓</span>
        </div>
        <span class="text-white text-xl font-bold tracking-tight">{bullets[0]}</span>
      </div>

      <div class="flex items-center gap-3.5">
        <div class="w-7 h-7 rounded-full bg-[#F43F5E]/20 border border-[#F43F5E] flex items-center justify-center shrink-0">
          <span class="text-[#F43F5E] text-sm font-black">✓</span>
        </div>
        <span class="text-white text-xl font-bold tracking-tight">{bullets[1]}</span>
      </div>

      <div class="flex items-center gap-3.5">
        <div class="w-7 h-7 rounded-full bg-[#F43F5E]/20 border border-[#F43F5E] flex items-center justify-center shrink-0">
          <span class="text-[#F43F5E] text-sm font-black">✓</span>
        </div>
        <span class="text-white text-xl font-bold tracking-tight">{bullets[2]}</span>
      </div>
    </div>

    <!-- 하단 스와이프 CTA 배너 -->
    <div class="w-full py-4 rounded-2xl bg-gradient-to-r from-[#F43F5E] to-[#E11D48] shadow-xl shadow-[#F43F5E]/30 flex items-center justify-center border border-white/30">
      <span class="text-white text-xl font-black tracking-wide">
        {cta_text}
      </span>
    </div>

  </div>

</body>
</html>
"""

        logger.info(f"🎨 [AuraCardnewsS1Topic5] 1080x1350 표지 렌더링 시작 -> {out_path.name}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
            page.set_content(html_content, wait_until="networkidle")
            page.screenshot(path=str(out_path), full_page=True)
            browser.close()

        logger.info(f"✅ [AuraCardnewsS1Topic5] 1번 표지 렌더링 완료: {out_path}")
        return str(out_path)

    def produce(self, target_dir: str = None, copy_data: dict = None, seed: int = None) -> str:
        """사진 획득 및 표지 카드뉴스 렌더링 일괄 실행"""
        if not target_dir:
            from .aura_cardnews_storage import AuraCardnewsStorage
            t_path = AuraCardnewsStorage.create_target_directory(theme_code="value_balance", theme_title="가치관 밸런스 매칭")
        else:
            t_path = Path(target_dir)
            t_path.mkdir(parents=True, exist_ok=True)

        raw_photo = self.get_or_generate_cover_photo(seed=seed)
        slide1_path = t_path / "slide_1.png"
        self.render_cover_slide(raw_photo, str(slide1_path), copy_data=copy_data)
        return str(slide1_path)
