# -*- coding: utf-8 -*-
"""
StockCardnewsS1Topic1Builder - 📈 [StockMaster AI 주식 1번 주제 '삼성전자/HBM 수급 쌍끌이' 1번 표지 전문 빌더]
=====================================================================================================
• 역할:
  - ComfyUI Wan 2.1 14B Q4_0 GPU 엔진을 통해 신규 2.0m 아나운서 실사 사진 100% 원천 생성
  - 1080x1350 카드뉴스 규격 초고화질 서브픽셀 타이포그래피 오버레이
  - Aura 방식 시네마틱 딥네이비 페이드 그라데이션 + 골드 4단 타이포그래피 (Playwright 렌더러)
"""

import os
import sys
import time
import base64
import logging
from pathlib import Path
from core.engine.naver_search_bar_component import render_naver_search_bar_html

from playwright.sync_api import sync_playwright

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from core.engine.wan_pipeline_client import WanPipelineClient
from core.engine.comfy_process_manager import ComfyProcessManager

logger = logging.getLogger("StockCardnewsS1Topic1Builder")


class StockCardnewsS1Topic1Builder:
    """주식 1번 주제(삼성전자/HBM 수급) 1번 표지 전문 빌더 (Wan 2.1 신규 실사 생성 탑재)"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.wan_client = WanPipelineClient()

    def generate_fresh_wan_photo(self, seed: int = None) -> Path:
        """ComfyUI Wan 2.1 14B GPU 엔진으로 1번 주제 2.0m 신규 실사 사진 생성"""
        print("🚀 [Wan 2.1] ComfyUI 엔진 상태 확인 및 백그라운드 자동 기동...")
        ComfyProcessManager.ensure_running(wait_timeout=90)

        if not self.wan_client.check_health(auto_start=True):
            raise RuntimeError("ComfyUI Wan 2.1 GPU 엔진 연결 실패! D:\\ComfyUI_Wan_Engine 상태를 확인해주세요.")

        if seed is None:
            seed = int(time.time() * 1000) % 100000000

        positive_prompt = (
            "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on Apple iPhone 15 Pro, "
            "photographed from 2.0 meters away directly in front, "
            "an exceptionally gorgeous, captivating, and glamorous 24-year-old Korean female financial news anchor, "
            "perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck, "
            "breathtakingly stunning K-drama visual beauty, voluminous natural dark silky wavy hair, "
            "seductive feline cat-like hazel eyes with subtle elegant eyeliner, flawless luminous glass skin with soft natural cheek blush, "
            "wearing an exceptionally neat, clean, and elegant formal business suit, a tailored slim-fit dark navy blazer suit jacket over a crisp clean white collared shirt, "
            "minimalist sophisticated Korean television news anchor formal suit fashion, impeccably ironed fabric with zero wrinkles, "
            "sitting upright and comfortably at a sleek modern glass broadcast news anchor desk, perfectly centered in frame, "
            "looking directly into camera lens with composed confident closed-mouth expression (lips firmly closed together, strictly zero visible teeth, strictly no teeth showing), "
            "state-of-the-art modern Korean broadcast television news studio in Yeouido Seoul, "
            "sleek high-tech financial newsroom backdrop with sophisticated dark navy and golden-amber glowing LED digital display walls showing subtle abstract financial market charts, "
            "professional studio key lights and soft rim lighting, "
            "candid medium bust shot, f/11 deep pan-focus, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, zero yellow tint."
        )

        negative_prompt = (
            "open mouth, parted lips, visible teeth, showing teeth, laughing, grinning, smiling wide, "
            "ugly face, old woman, chubby, distorted features, bad eyes, rolled back eyes, asymmetric face, doll, porcelain skin, plastic skin, "
            "blurry, lens blur, out of focus, bokeh blur, deformed hands, cartoon, anime, 3d render, cgi, watermark, text, male, man, holding phone, smartphone"
        )

        print(f"🎨 [Wan 2.1 T2I] 1번 주제 2.0m 아나운서 신규 실사 사진 GPU 렌더링 시작 (Seed={seed})...")
        raw_path = self.wan_client.generate_t2i_master(
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            width=832,
            height=1216,
            seed=seed,
            prefix="stock_topic1_cover_female_fresh"
        )
        print(f"✅ [Wan 2.1 T2I] 신규 실사 사진 GPU 렌더링 완료: {raw_path}")
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
        badge = copy_data.get("badge", "🔴 LIVE 퀀트 수급 포착")
        h1_line1 = copy_data.get("headline_line1", "삼성전자 vs SK하이닉스")
        h1_line2 = copy_data.get("headline_line2", "외인·기관이 몰래 담은 1종목 공개")
        subtitle = copy_data.get("subtitle", "장 마감 직전 메이저 수급 300억 쌍끌이 매집 긴급 분석")

        default_bullets = [
            "외국인 3일 연속 순매수 전환 • 기관 동시 유입 포착",
            "HBM 공급망 수혜주 퀀트 점수 89.4점 최고 등급",
            "감정에 휘둘리는 뇌동매매 끝 • 100% 팩트 데이터"
        ]
        bullets = copy_data.get("bullets", default_bullets)
        while len(bullets) < 3:
            bullets.append("StockMaster AI 실시간 퀀트 분석")

        cta_text = copy_data.get("cta_text", "👉 옆으로 넘겨서 실시간 수급 차트 보기 (1/5) >")
        naver_search_html = render_naver_search_bar_html(brand="stock")

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Stock Master Topic 1 Cover Slide (1080x1350)</title>
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

  <!-- 1. 배경 인물 실사 이미지 레이어 (Wan 2.1 2.0m 아나운서) -->
  <div class="absolute inset-0 z-0 overflow-hidden">
    <img src="data:image/png;base64,{photo_b64}" class="w-full h-full object-cover object-top transform scale-[1.01]" alt="Stock Anchor Visual" />
    <!-- 상단 블러 100% 걷어냄! 하단 텍스트 가독성을 위한 최하단 40% 부드러운 소프트 그라데이션만 적용 -->
    <div class="absolute inset-x-0 bottom-0 h-[45%] bg-gradient-to-t from-[#070B14] via-[#070B14]/65 via-35% to-transparent pointer-events-none"></div>
  </div>

  <!-- 2. 상단 헤더 영역 (Aura 동일 규격 캡슐 뱃지 & 페이지 번호) -->
  <div class="relative z-10 pt-14 px-12 flex justify-between items-center">
    <div class="inline-flex items-center gap-2.5 px-6 py-2.5 rounded-full bg-black/60 border border-[#F59E0B]/50 shadow-lg">
      <span class="text-[#F59E0B] text-lg font-black">📈</span>
      <span class="text-white text-lg font-extrabold tracking-tight">StockMaster AI</span>
      <span class="text-white/40">|</span>
      <span class="text-[#FBBF24] text-lg font-bold tracking-tight">외인·기관 실시간 수급 퀀트</span>
    </div>

    <div class="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-full bg-black/60 border border-white/20 shadow-lg">
      <span class="text-[#FBBF24] text-lg font-black tracking-wider">01 / 05</span>
      <span class="text-white/60 text-lg font-bold">&gt;</span>
    </div>
  </div>

  <!-- 3. 하단 메인 타이포그래피 영역 (Aura 동일 초깔끔 4단 텍스트 구조) -->
  <div class="relative z-10 px-12 pb-14 flex flex-col gap-4">

    <!-- 서브 뱃지 (긴급 속보) -->
    <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-gradient-to-r from-[#EF4444] to-[#F59E0B] shadow-md self-start">
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

    <!-- 3단 핵심 요약 불릿 (박스 없이 깔끔하게 직접 배치) -->
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

        logger.info(f"🎉 [StockCardnewsS1Topic1Builder] 1번 표지 슬라이드 렌더링 완료: {out_path}")
        return str(out_path)

    def produce_fresh_slide1(self, output_dir: Path = None) -> str:
        """Wan 2.1 신규 실사 생성부터 1080x1350 카드뉴스 1번 표지 렌더링까지 원스톱 실행"""
        if output_dir is None:
            now_str = time.strftime("%Y%m%d_%H%M%S")
            output_dir = Path(os.environ.get("USERPROFILE", "C:/Users/zkfnt")) / "Desktop" / "한국 카드뉴스_산출물" / "주식" / f"[주제01] 삼성전자_수급쌍끌이_20대여성아나운서_{now_str}"

        output_dir.mkdir(parents=True, exist_ok=True)
        out_slide1 = output_dir / "slide_1.png"

        # 1. Wan 2.1 신규 실사 사진 GPU 생성
        fresh_photo = self.generate_fresh_wan_photo()

        # 2. 1080x1350 타이포그래피 표지 완제품 렌더링
        res = self.render_cover_slide(fresh_photo, str(out_slide1))
        return res


if __name__ == "__main__":
    builder = StockCardnewsS1Topic1Builder()
    final_png = builder.produce_fresh_slide1()
    print(f"🎉 [Wan 2.1 신규 실사 생성 완료] 주식 1번 표지 카드뉴스: {final_png}")
