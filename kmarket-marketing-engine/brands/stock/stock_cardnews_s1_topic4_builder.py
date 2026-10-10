# -*- coding: utf-8 -*-
"""
StockCardnewsS1Topic4Builder - 📈 [StockMaster AI 주식 4번 주제 '체결 가속도(+%p) 급증 시그널' 1번 표지 전문 빌더]
=====================================================================================================
• 역할:
  - ComfyUI Wan 2.1 14B GPU 엔진을 통해 여의도 야외 현장 훈남 기자(마이크 손에 쥠) 실사 사진 연동 (4번 주제 전용)
  - 1080x1350 카드뉴스 규격 초고화질 서브픽셀 타이포그래피 오버레이
  - Aura 방식 시네마틱 딥네이비 페이드 그라데이션 + 골드 4단 타이포그래피 (상단 블러 100% 제거)
  - 4번 주제 카피: '정체되던 호가창이 불타오른다! 체결 가속도(+%p) 폭증 포착'
"""

import os
import sys
import time
import base64
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from core.engine.wan_pipeline_client import WanPipelineClient
from core.engine.naver_search_bar_component import render_naver_search_bar_html
from core.engine.comfy_process_manager import ComfyProcessManager

logger = logging.getLogger("StockCardnewsS1Topic4Builder")


class StockCardnewsS1Topic4Builder:
    """주식 4번 주제(체결 가속도 급증 시그널) 1번 표지 전문 빌더 (Wan 2.1 신규 실사 연동)"""

    BRAND_NAME = "StockMaster AI"
    BRAND_SUB = "AI 체결 가속도 엔진"

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.wan_client = WanPipelineClient()

    def generate_fresh_wan_photo(self, seed: int = None) -> Path:
        """ComfyUI Wan 2.1 14B GPU 엔진으로 4번 주제 여의도 야외 훈남 현장 기자 신규 실사 사진 생성"""
        logger.info("🚀 [Wan 2.1] ComfyUI 엔진 상태 확인 및 백그라운드 자동 기동...")
        ComfyProcessManager.ensure_running(wait_timeout=90)

        if not self.wan_client.check_health(auto_start=True):
            raise RuntimeError("ComfyUI Wan 2.1 GPU 엔진 연결 실패! D:\\ComfyUI_Wan_Engine 상태를 확인해주세요.")

        if seed is None:
            seed = int(time.time() * 1000) % 100000000

        positive_prompt = (
            "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on Apple iPhone 15 Pro, "
            "photographed from 2.5 meters away directly in front, "
            "candid medium cowboy shot showing head, strong masculine neck, broad natural shoulders, chest, waist, hips, and tailored suit down to mid-thigh clearly, "
            "minimal compact headroom occupying upper 5% of frame with head positioned high near top edge, "
            "an exceptionally handsome, top 5% visual, charismatic 27-year-old Korean male financial news field journalist, "
            "perfect 8-head-high golden ratio model proportions, tall athletic build, sharp masculine jawline, "
            "breathtakingly stunning K-drama leading actor visual beauty, styled dark silky parted hair, "
            "captivating focused dark brown eyes with calm intelligent gaze, flawless clear skin, "
            "wearing an exceptionally neat, clean, and elegant formal business suit, a tailored slim-fit dark charcoal navy blazer suit jacket over a crisp clean white collared shirt and stylish dark tie, "
            "holding a sleek professional television broadcast cube microphone firmly in one hand at chest level, "
            "standing upright and poised outdoors, perfectly centered in frame, "
            "looking directly into camera lens with composed confident closed-mouth expression (lips firmly closed together, strictly zero visible teeth, strictly no teeth showing), "
            "bustling outdoor Yeouido Seoul financial district street background, towering modern glass skyscrapers, Korean financial center streetscape during daytime with crisp natural daylight, "
            "dramatic 3D volumetric fill lighting, subtle rim light highlighting shoulders and hair silhouette, "
            "f/11 deep pan-focus, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, zero yellow tint."
        )

        negative_prompt = (
            "open mouth, parted lips, visible teeth, showing teeth, laughing, grinning, smiling wide, "
            "ugly face, old man, chubby, distorted features, bad eyes, rolled back eyes, asymmetric face, doll, porcelain skin, plastic skin, "
            "blurry, lens blur, out of focus, bokeh blur, deformed hands, extra fingers, missing fingers, cartoon, anime, 3d render, cgi, watermark, text, female, woman, holding phone, smartphone"
        )

        logger.info(f"🎨 [Wan 2.1 T2I] 4번 주제 야외 훈남 기자 실사 사진 GPU 렌더링 시작 (Seed={seed})...")
        raw_path = self.wan_client.generate_t2i_master(
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            width=832,
            height=1216,
            seed=seed,
            prefix="stock_topic4_cover_reporter_male"
        )
        logger.info(f"✅ [Wan 2.1 T2I] 신규 실사 사진 GPU 렌더링 완료: {raw_path}")
        return Path(raw_path)

    def render_cover_slide(self, photo_path: Path, output_png_path: str, custom_copy: dict = None) -> str:
        """Playwright로 1080x1350 카드뉴스 규격 초고화질 타이포그래피 표지 렌더링"""
        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if not photo_path or not photo_path.exists():
            raise FileNotFoundError(f"실사 사진을 찾을 수 없습니다: {photo_path}")

        with open(str(photo_path), "rb") as f:
            photo_b64 = base64.b64encode(f.read()).decode("utf-8")

        copy_data = custom_copy or {}
        badge = copy_data.get("badge", "⚡ 실시간 급등 포착 • 체결 가속도")
        h1_line1 = copy_data.get("headline_line1", "정체되던 호가창이 불타오른다!")
        h1_line2 = copy_data.get("headline_line2", "체결 가속도(+%p) 폭증 포착")
        subtitle = copy_data.get("subtitle", "순식간에 대량 매수세 유입! AI 10분 체결 가속도 1초 탐지")

        default_bullets = [
            "10분 단위 체결강도 변화율(+%p) 실시간 급증 1위 종목 포착",
            "정체 구간 돌파하는 대량 매수 체결 가속 시그널 1초 자동 경보",
            "국내 350개 우량주 10분 스캔 기반 호가창 매수 강도 급등 분석"
        ]
        bullets = copy_data.get("bullets", default_bullets)
        while len(bullets) < 3:
            bullets.append("StockMaster AI 실시간 체결 가속도 엔진")

        cta_text = copy_data.get("cta_text", "👉 옆으로 넘겨서 실시간 체결 가속도 순위 보기 (1/5) >")
        naver_search_html = render_naver_search_bar_html(brand="stock")

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Stock Master Topic 4 Cover Slide (1080x1350)</title>
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
      background: #070B14;
      overflow: hidden;
      position: relative;
    }}
    .text-glow-yellow {{
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.95), 0 0 2px #000;
    }}
    .text-glow-white {{
      text-shadow: 0 2px 8px rgba(0, 0, 0, 0.9);
    }}
  </style>
</head>
<body class="flex flex-col justify-between">

  <!-- 1. 배경 인물 실사 이미지 레이어 (Wan 2.1 야외 훈남 현장 기자) -->
  <div class="absolute inset-0 z-0 overflow-hidden">
    <img src="data:image/png;base64,{photo_b64}" class="w-full h-full object-cover object-top transform scale-[1.01]" alt="Stock Reporter Visual" />
    <!-- 하단 텍스트 가독성을 위한 최하단 46% 부드러운 소프트 그라데이션만 적용 -->
    <div class="absolute inset-x-0 bottom-0 h-[46%] bg-gradient-to-t from-[#070B14] via-[#070B14]/70 via-35% to-transparent pointer-events-none"></div>
  </div>

  <!-- 2. 상단 헤더 영역 (캡슐 뱃지 & 페이지 번호) -->
  <div class="relative z-10 pt-14 px-12 flex justify-between items-center">
    <div class="inline-flex items-center gap-2.5 px-6 py-2.5 rounded-full bg-black/60 border border-[#F59E0B]/50 shadow-lg">
      <span class="text-[#F59E0B] text-lg font-black">📈</span>
      <span class="text-white text-lg font-extrabold tracking-tight">{self.BRAND_NAME}</span>
      <span class="text-white/40">|</span>
      <span class="text-[#FBBF24] text-lg font-bold tracking-tight">{self.BRAND_SUB}</span>
    </div>

    <div class="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-full bg-black/60 border border-white/20 shadow-lg">
      <span class="text-[#FBBF24] text-lg font-black tracking-wider">01 / 05</span>
      <span class="text-white/60 text-lg font-bold">&gt;</span>
    </div>
  </div>

  <!-- 3. 하단 메인 타이포그래피 영역 (초깔끔 4단 텍스트 구조) -->
  <div class="relative z-10 px-12 pb-14 flex flex-col gap-4">

    <!-- 서브 뱃지 (급등 포착) -->
    <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-gradient-to-r from-[#F59E0B] to-[#EA580C] shadow-md self-start">
      <span class="text-white text-base font-extrabold tracking-tight">{badge}</span>
    </div>

    <!-- 메인 헤드라인 (옐로우/골드 굵은 텍스트) -->
    <div class="flex flex-col gap-1.5">
      <h1 class="text-[#FBBF24] text-5xl font-black leading-tight tracking-tight text-glow-yellow">
        {h1_line1} {h1_line2}
      </h1>
      <p class="text-white text-2xl font-medium mt-1 leading-relaxed text-glow-white">
        {subtitle}
      </p>
    </div>

    <!-- 3단 핵심 요약 불릿 -->
    <div class="flex flex-col gap-2.5 my-1">
      <div class="flex items-center gap-3">
        <span class="text-[#38BDF8] text-2xl leading-none">•</span>
        <span class="text-white text-xl font-bold tracking-tight text-glow-white">{bullets[0]}</span>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-[#38BDF8] text-2xl leading-none">•</span>
        <span class="text-white text-xl font-bold tracking-tight text-glow-white">{bullets[1]}</span>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-[#38BDF8] text-2xl leading-none">•</span>
        <span class="text-white text-xl font-bold tracking-tight text-glow-white">{bullets[2]}</span>
      </div>
    </div>

    <!-- 하단 네이버 공식 검색창 UI 바 (숏폼 일체형) -->
    {naver_search_html}

  </div>

</body>
</html>
"""

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350})
            page.set_content(html_content, wait_until="networkidle")
            page.screenshot(path=str(out_path), full_page=True)
            browser.close()

        logger.info(f"🎉 [StockCardnewsS1Topic4Builder] 4번 주제 1번 표지 슬라이드 렌더링 완료: {out_path}")
        return str(out_path)

    def produce_fresh_slide1(self, output_dir: Path = None) -> str:
        """Wan 2.1 신규 실사 생성부터 1080x1350 카드뉴스 1번 표지 렌더링까지 원스톱 실행"""
        if output_dir is None:
            output_dir = Path(os.environ.get("USERPROFILE", "C:/Users/zkfnt")) / "Desktop" / "한국 카드뉴스_산출물" / "주식" / "[주제04] 체결가속도_호가창급등_실시간포착"

        output_dir.mkdir(parents=True, exist_ok=True)
        out_slide1 = output_dir / "slide_1.png"

        # 1. Wan 2.1 신규 실사 사진 GPU 생성
        fresh_photo = self.generate_fresh_wan_photo()

        # 2. 1080x1350 타이포그래피 표지 완제품 렌더링
        res = self.render_cover_slide(fresh_photo, str(out_slide1))
        return res


if __name__ == "__main__":
    builder = StockCardnewsS1Topic4Builder()
    res = builder.produce_fresh_slide1()
    print(f"🎉 1번 표지 렌더링 결과: {res}")
