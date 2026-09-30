# -*- coding: utf-8 -*-
"""
AuraCardnewsS5Topic5Builder - 🏷️ [Aura 카드뉴스 5번 주제 5번 전용 숏폼 계승 럭셔리 엔딩 CTA 카드 빌더]
===================================================================================================
• 역할:
  - 숏폼 5번 엔딩 CTA 카드의 럭셔리 에디토리얼 디자인을 1080x1350 카드뉴스 규격으로 100% 계승
  - 가치관 밸런스 찬반 토론(1번 칼반띵 vs 2번 번갈아 내기)과 네이버 검색창['아우라AI데이팅'] 완벽 융합
  - 상단 브랜드 배지['💖 AURA | 50:50 남녀 황금 성비율', '05 / 05 >'] 및 공식 URL 일체형 렌더링
  - 산출물: 바탕화면 타겟 폴더의 slide_5.png
"""

import os
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright

logger = logging.getLogger("AuraCardnewsS5Topic5Builder")


class AuraCardnewsS5Topic5Builder:
    """Aura 주제 5(가치관 밸런스 매칭) 5번 엔딩 찬반 토론 & 네이버 검색 CTA 카드 빌더"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent

    def build_s5_ending_card(self, output_png_path: str) -> str:
        """1080x1350 카드뉴스 규격 럭셔리 엔딩 CTA 카드 렌더링"""
        logger.info(f"🎨 [AuraCardnewsS5Topic5Builder] 5번 주제 5번 엔딩 CTA 카드 렌더링 시작: {output_png_path}")

        html_content = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Aura S5 Topic 5 Ending Debate & Naver Search CTA (1080x1350)</title>
  <!-- Pretendard Font -->
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
      font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    body {
      width: 1080px;
      height: 1350px;
      overflow: hidden;
      background: radial-gradient(circle at 50% 25%, #181926 0%, #0a0a0f 55%, #030305 100%);
      color: #fff;
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 30px 40px 40px;
    }

    /* 금빛 수평선 */
    .gold-divider {
      height: 1px;
      background: linear-gradient(90deg, rgba(212, 175, 55, 0) 0%, rgba(212, 175, 55, 0.8) 50%, rgba(212, 175, 55, 0) 100%);
    }

    /* 글래스 카드 */
    .glass-box {
      background: rgba(18, 18, 24, 0.82);
      backdrop-filter: blur(28px);
      -webkit-backdrop-filter: blur(28px);
      border: 1px solid rgba(255, 255, 255, 0.14);
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.85);
    }

    .vote-card {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.12);
      backdrop-filter: blur(16px);
      transition: all 0.2s ease;
    }

    .glow-gold {
      box-shadow: 0 0 45px rgba(212, 175, 55, 0.45);
    }

    .naver-glow {
      box-shadow: 0 10px 40px rgba(3, 199, 90, 0.35), 0 0 30px rgba(212, 175, 55, 0.3);
    }
  </style>
</head>
<body>

  <!-- Ambient Cinematic Background Glows -->
  <div class="absolute w-[800px] h-[800px] rounded-full bg-pink-500/10 blur-[150px] top-0 left-1/2 -translate-x-1/2 pointer-events-none"></div>
  <div class="absolute w-[600px] h-[600px] rounded-full bg-amber-500/10 blur-[130px] bottom-10 right-10 pointer-events-none"></div>

  <!-- 1. Top Header Bar (Aura 50:50 남녀 황금 성비율 + 05/05) -->
  <div class="flex justify-between items-center z-10 w-full px-2">
    <!-- Brand Badge -->
    <div class="inline-flex items-center gap-2.5 bg-slate-900/85 backdrop-blur-md border border-white/20 rounded-full py-2 px-4 shadow-xl">
      <span class="text-sm">💖</span>
      <span class="text-sm font-black tracking-wider text-white">AURA</span>
      <span class="text-xs font-bold text-pink-400 pl-2 border-l border-white/25">50:50 남녀 황금 성비율</span>
    </div>

    <!-- Page Index -->
    <div class="text-amber-400 font-extrabold text-sm bg-slate-900/85 backdrop-blur-md px-4 py-2 rounded-full border border-amber-500/40 shadow-xl tracking-wider">
      05 / 05 &gt;
    </div>
  </div>

  <!-- 2. Main Content Container -->
  <div class="flex flex-col items-center text-center z-10 space-y-6 my-auto px-4">
    
    <!-- Editorial Brand Subtitle -->
    <div class="flex flex-col items-center space-y-2">
      <div class="gold-divider w-72"></div>
      <p class="text-xs tracking-[0.35em] text-[#D4AF37] font-bold uppercase py-1">
        — A U R A   D A T I N G —
      </p>
      <div class="gold-divider w-72"></div>
    </div>

    <!-- Main Question Box (Glassmorphism) -->
    <div class="glass-box rounded-3xl p-7 w-full max-w-[960px] border border-[#D4AF37]/40 glow-gold">
      
      <!-- Mini Category Badge -->
      <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-pink-500/20 border border-pink-400/40 text-pink-300 text-xs font-black mb-3">
        <span>⚖️</span>
        <span>실시간 가치관 밸런스 토론</span>
      </div>

      <!-- Main Headline -->
      <h1 class="text-2xl md:text-3xl font-black leading-snug tracking-tight text-white mb-2">
        "소개팅 첫 만남 더치페이,<br>
        <span class="text-transparent bg-clip-text bg-gradient-to-r from-amber-300 via-pink-300 to-amber-200">
          칼반띵 vs 번갈아 내기
        </span>
        여러분의 선택은?"
      </h1>
      <p class="text-xs text-slate-300 font-medium tracking-wide">
        나와 생각과 가치관이 100% 통하는 사람과 연애하고 싶다면?
      </p>

      <!-- 2 Options Vote Cards -->
      <div class="grid grid-cols-2 gap-4 mt-5">
        
        <!-- Option 1: 1번 칼반띵 -->
        <div class="vote-card rounded-2xl p-4 text-left border-l-4 border-l-emerald-400">
          <div class="flex items-center justify-between mb-1">
            <span class="text-xs font-black text-emerald-300">OPTION 1</span>
            <span class="text-[11px] font-bold text-slate-400">48%</span>
          </div>
          <p class="text-sm font-black text-white leading-snug">
            첫 만남부터 부담 없는 칼반띵
          </p>
          <p class="text-[11px] text-slate-400 mt-1">
            깔끔한 정산 • 불필요한 부담 제로
          </p>
        </div>

        <!-- Option 2: 2번 번갈아 내기 -->
        <div class="vote-card rounded-2xl p-4 text-left border-l-4 border-l-pink-400 bg-pink-500/10 border-pink-400/30">
          <div class="flex items-center justify-between mb-1">
            <span class="text-xs font-black text-pink-300">OPTION 2</span>
            <span class="text-[11px] font-bold text-pink-300 font-black">52% (인기)</span>
          </div>
          <p class="text-sm font-black text-white leading-snug">
            1차 사면 2차는 상대방이 센스 계산
          </p>
          <p class="text-[11px] text-slate-300 mt-1">
            자연스러운 매너 • 다음 만남 유도
          </p>
        </div>

      </div>

      <!-- Comment Prompt -->
      <div class="mt-4 pt-3 border-t border-white/10 flex items-center justify-center gap-2 text-xs font-extrabold text-amber-300">
        <span>💬</span>
        <span>댓글에 [1번] vs [2번] 여러분의 생각을 남겨주세요!</span>
      </div>

    </div>

    <!-- 3. Glow Naver Search Bar (Official Mandatory Keyword) -->
    <div class="w-full max-w-[960px] flex flex-col items-center space-y-2">
      <div class="w-full bg-white rounded-2xl p-4 flex items-center justify-between naver-glow border-2 border-[#03C75A]">
        <!-- Naver N Logo -->
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-[#03C75A] flex items-center justify-center font-black text-white text-xl shadow-md">
            N
          </div>
          <div class="text-left">
            <p class="text-[11px] font-bold text-slate-500">네이버 검색창에 입력하세요</p>
            <p class="text-xl font-black text-slate-900 tracking-tight">아우라AI데이팅</p>
          </div>
        </div>

        <!-- Search Button -->
        <div class="bg-[#03C75A] text-white font-black text-sm px-5 py-2.5 rounded-xl flex items-center gap-1.5 shadow-lg">
          <span>검색</span>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
        </div>
      </div>
      
      <!-- Sub CTA text -->
      <p class="text-xs text-slate-400 font-bold tracking-wide">
        ✨ 50:50 남녀 황금 성비율 • 가치관 100% 일치 매칭 지금 시작하기
      </p>
    </div>

  </div>

  <!-- 4. Bottom Footer (Official Landing URL & Copyright) -->
  <div class="flex justify-between items-center z-10 w-full px-4 pt-2 border-t border-white/10 text-xs text-slate-400 font-medium">
    <div>
      <span class="text-slate-500">Official Web:</span>
      <span class="text-amber-400/90 font-bold ml-1">https://aura-ai-dating.vercel.app/lounge</span>
    </div>
    <div class="text-slate-500 text-[11px]">
      © 2026 AURA AI Dating. All rights reserved.
    </div>
  </div>

</body>
</html>
"""

        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
            page.set_content(html_content, wait_until="networkidle")
            page.screenshot(path=str(out_path), full_page=True)
            browser.close()

        logger.info(f"✅ [AuraCardnewsS5Topic5Builder] 5번 엔딩 CTA 카드 생성 완료: {out_path}")
        return str(out_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_dir = r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\아우라\아우라_KO_value_balance_20260930_1821"
    builder = AuraCardnewsS5Topic5Builder()
    builder.build_s5_ending_card(os.path.join(test_dir, "slide_5.png"))
