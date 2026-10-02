# -*- coding: utf-8 -*-
"""
AuraCardnewsS5Builder - 🏷️ [Aura 카드뉴스 5번 전용 숏폼 계승 럭셔리 엔딩 CTA 카드 빌더]
=====================================================================================
• 역할:
  - 숏폼 5번 엔딩 CTA 카드(AuraCTACard)의 럭셔리 에디토리얼 디자인을 100% 계승
  - 1080x1350 카드뉴스 규격에 맞춰 찬반 토론(1번 vs 2번)과 네이버 검색창['아우라AI데이팅']을 완벽 융합
  - 상단 브랜드 배지['💖 AURA | 50:50 남녀 황금 성비율', '05 / 05 >'] 및 공식 URL 일체형 렌더링
  - 산출물: 바탕화면 타겟 폴더의 slide_5.png
"""

import os
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright

logger = logging.getLogger("AuraCardnewsS5Builder")


class AuraCardnewsS5Builder:
    """Aura 주제 2(실시간 AI 자막 통화) 5번 엔딩 찬반 토론 & 네이버 검색 CTA 카드 빌더"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent

    def build_s5_ending_card(self, output_png_path: str) -> str:
        """1080x1350 카드뉴스 규격 럭셔리 엔딩 CTA 카드 렌더링"""
        logger.info(f"🎨 [AuraCardnewsS5Builder] 5번 엔딩 CTA 카드 렌더링 시작: {output_png_path}")

        html_content = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Aura S5 Ending Debate & Naver Search CTA (1080x1350)</title>
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
      background: rgba(18, 18, 24, 0.78);
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
  <div class="absolute w-[800px] h-[800px] rounded-full bg-amber-500/10 blur-[150px] top-0 left-1/2 -translate-x-1/2 pointer-events-none"></div>
  <div class="absolute w-[600px] h-[600px] rounded-full bg-emerald-500/10 blur-[130px] bottom-10 right-10 pointer-events-none"></div>

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
      05 / 05 >
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

    <!-- Topic Title -->
    <p class="text-lg text-zinc-400 font-semibold tracking-wide">
      실시간 AI 자막 통화 • 글로벌 매칭
    </p>

    <!-- Hero Title -->
    <h1 class="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-[#E5A934] to-yellow-500 tracking-tight leading-snug drop-shadow-[0_4px_24px_rgba(229,169,52,0.4)]">
      말이 안 통해도 통하는 글로벌 썸! 🍒
    </h1>

    <!-- Debate Question Box -->
    <div class="glass-box rounded-3xl p-7 w-full max-w-2xl border border-white/20 space-y-5">
      
      <!-- Question Badge -->
      <div class="inline-block px-4 py-1.5 rounded-full bg-pink-500/20 text-pink-400 font-extrabold text-xs tracking-wider border border-pink-500/30">
        🔥 댓글 찬반 투표
      </div>

      <h2 class="text-2xl font-black text-white leading-relaxed">
        "언어 안 통해도 AI 자막으로 연애 가능?"
      </h2>
      <p class="text-sm text-zinc-300 font-medium">
        여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇
      </p>

      <!-- Vote Options Grid -->
      <div class="grid grid-cols-2 gap-4 pt-1">
        <!-- Option 1 -->
        <div class="vote-card rounded-2xl p-4 text-left space-y-2 border-amber-500/30 bg-amber-500/10">
          <div class="flex items-center gap-2">
            <span class="text-xl">👍</span>
            <span class="text-base font-black text-amber-300">1번 찬성</span>
          </div>
          <p class="text-xs text-zinc-200 font-medium leading-relaxed">
            마음과 눈빛이 통하면 언어 장벽은 AI가 100% 해결해 준다!
          </p>
        </div>

        <!-- Option 2 -->
        <div class="vote-card rounded-2xl p-4 text-left space-y-2 border-zinc-700 bg-white/5">
          <div class="flex items-center gap-2">
            <span class="text-xl">👎</span>
            <span class="text-base font-black text-zinc-300">2번 반대</span>
          </div>
          <p class="text-xs text-zinc-400 font-medium leading-relaxed">
            미묘한 뉘앙스와 깊은 감정 소통까지는 그래도 무리다!
          </p>
        </div>
      </div>

    </div>

    <!-- 3. Official Naver Search Bar (The Core CTA) -->
    <div class="w-full max-w-2xl space-y-3 pt-2">
      <!-- Naver Search Bar -->
      <div class="w-full h-20 rounded-full bg-white flex items-center px-4 shadow-[0_15px_50px_rgba(212,175,55,0.4)] naver-glow border-2 border-amber-300/60">
        <!-- Green Naver N Badge -->
        <div class="w-13 h-13 rounded-2xl bg-[#03C75A] flex items-center justify-center text-white font-black text-2xl shadow-md p-3">
          N
        </div>
        <!-- Search Keyword (아우라AI데이팅 - 붙여쓰기) -->
        <div class="flex-1 text-left px-5">
          <span class="text-2xl font-black text-zinc-950 tracking-tight">아우라AI데이팅</span>
        </div>
        <!-- Search Glass Icon Button -->
        <div class="w-13 h-13 rounded-full bg-[#03C75A] flex items-center justify-center text-white p-3 shadow-md">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        </div>
      </div>

      <!-- Search Instruction Text -->
      <p class="text-base font-bold text-amber-300 tracking-wide pt-1">
        👉 프로필 링크에서 3초 이상형 확인 또는 네이버에 <span class="text-white underline underline-offset-4 decoration-[#03C75A] font-extrabold">'아우라AI데이팅'</span> 검색!
      </p>
    </div>

  </div>

  <!-- 4. Bottom Footer Info -->
  <div class="flex flex-col items-center space-y-2 z-10 w-full pt-2">
    <div class="gold-divider w-full max-w-xl opacity-60"></div>
    <div class="flex items-center justify-between w-full max-w-xl text-xs text-zinc-400 font-semibold px-2">
      <span>50:50 남녀 정원제 프리미엄 데이팅</span>
      <span class="text-amber-400/90 font-mono tracking-wider">aura-ai-dating.vercel.app</span>
    </div>
  </div>

</body>
</html>
"""
        out_p = Path(output_png_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        temp_html = self.base_dir / "temp_s5_ending.html"
        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(html_content)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
            page.goto(temp_html.as_uri())
            page.wait_for_timeout(800)
            page.screenshot(path=str(out_p), type="png")
            browser.close()

        if temp_html.exists():
            temp_html.unlink()

        logger.info(f"✅ [AuraCardnewsS5Builder] 5번 엔딩 카드 렌더링 완료: {out_p}")
        return str(out_p)


if __name__ == "__main__":
    builder = AuraCardnewsS5Builder()
    out = r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\아우라\아우라_KO_realtime_subtitles_20260930_1613\slide_5.png"
    res = builder.build_s5_ending_card(out)
    print("Done S5:", res)
