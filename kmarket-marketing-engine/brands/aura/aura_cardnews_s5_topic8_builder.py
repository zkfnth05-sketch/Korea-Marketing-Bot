# -*- coding: utf-8 -*-
"""
AuraCardnewsS5Topic8Builder - 🏷️ [Aura 카드뉴스 8번 주제 5번 전용 럭셔리 엔딩 CTA 카드 빌더]
===================================================================================================
• 역할:
  - 8번 주제('500m 안심 레이더 & 안심 번개 퀘스트')의 5번 엔딩을 1080x1350 카드뉴스 규격으로 100% 렌더링
  - 동네 번개 만남 찬반 토론(1번 쿨한 당일 직진 vs 2번 며칠 대화 후 신중 만남)과 'Aura 500m 안심 번개 혜택' 완벽 융합
  - 네이버 검색창['아우라AI데이팅'] 및 상단 브랜드 배지['💖 AURA | 50:50 남녀 황금 성비율', '05 / 05 >'] 일체형
  - 산출물: 타겟 폴더의 slide_5.png
"""

import os
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright

logger = logging.getLogger("AuraCardnewsS5Topic8Builder")


class AuraCardnewsS5Topic8Builder:
    """Aura 주제 8(500m 안심 레이더 & 번개 퀘스트) 5번 엔딩 찬반 토론 & 네이버 검색 CTA 카드 빌더"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent

    def build_s5_ending_card(self, output_png_path: str, copy_data: dict = None) -> str:
        """1080x1350 카드뉴스 규격 럭셔리 엔딩 CTA 카드 렌더링 (제미나이 동적 카피 주입)"""
        logger.info(f"🎨 [AuraCardnewsS5Topic8Builder] 8번 주제 5번 엔딩 CTA 카드 렌더링 시작: {output_png_path}")

        # 제미나이 동적 카피 또는 기본값
        s5_copy = copy_data.get("slide5", copy_data) if (isinstance(copy_data, dict) and "slide5" in copy_data) else (copy_data or {})
        debate_badge = s5_copy.get("debate_badge", "⚡ 동네 안심 번개 찬반 토론")
        debate_q = s5_copy.get("debate_question", "퇴근 후 급 당일 동네 번개 만남, 부담 없는 쿨한 만남이다 vs 며칠 대화가 먼저다? 여러분의 선택은?")
        
        opt1_title = s5_copy.get("debate_opt1_title", "퇴근길 카페·와인 가볍게 만나보고 결정!")
        opt1_sub = s5_copy.get("debate_opt1_sub", "500m 안심 레이더라 위치 노출 걱정 제로")
        
        opt2_title = s5_copy.get("debate_opt2_title", "채팅으로 티키타카 맞춰보고 만나는 게 편함")
        opt2_sub = s5_copy.get("debate_opt2_sub", "가벼운 만남보단 진중한 대화 후 만남 선호")

        default_benefits = [
            "3초 동네 이상형 확인",
            "500m 안심 프라이버시 보호",
            "50:50 황금 성비 라운지"
        ]
        benefits = s5_copy.get("benefit_items", default_benefits)
        while len(benefits) < 3:
            benefits.append("Aura 100% 검증 VIP 혜택")

        cta_sub = s5_copy.get("cta_subtext", "👉 프로필 링크에서 3초 만에 동네 500m 안심 이상형 확인! ✨")

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Aura S5 Topic 8 Ending Debate & Naver Search CTA (1080x1350)</title>
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
      background: radial-gradient(circle at 50% 25%, #18241c 0%, #0c140e 55%, #030804 100%);
      color: #fff;
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 36px 44px 40px;
    }}

    /* 금빛/에메랄드 수평선 */
    .gold-divider {{
      height: 1px;
      background: linear-gradient(90deg, rgba(16, 185, 129, 0) 0%, rgba(234, 179, 8, 0.8) 50%, rgba(16, 185, 129, 0) 100%);
    }}

    /* 글래스 카드 */
    .glass-box {{
      background: rgba(14, 24, 18, 0.92);
      backdrop-filter: blur(28px);
      -webkit-backdrop-filter: blur(28px);
      border: 1px solid rgba(255, 255, 255, 0.16);
      box-shadow: 0 25px 70px rgba(0, 0, 0, 0.9);
    }}

    .vote-card {{
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.14);
      backdrop-filter: blur(16px);
      transition: all 0.2s ease;
    }}

    .benefit-box {{
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(234, 179, 8, 0.1) 100%);
      border: 1px solid rgba(16, 185, 129, 0.4);
    }}

    .glow-radar {{
      box-shadow: 0 0 55px rgba(16, 185, 129, 0.4);
    }}

    .naver-glow {{
      box-shadow: 0 12px 45px rgba(3, 199, 90, 0.45), 0 0 35px rgba(234, 179, 8, 0.4);
    }}
  </style>
</head>
<body>

  <!-- Ambient Cinematic Background Glows -->
  <div class="absolute w-[850px] h-[850px] rounded-full bg-emerald-500/15 blur-[160px] top-0 left-1/2 -translate-x-1/2 pointer-events-none"></div>
  <div class="absolute w-[700px] h-[700px] rounded-full bg-amber-500/12 blur-[140px] bottom-10 right-10 pointer-events-none"></div>

  <!-- 1. Top Header Bar (Aura 50:50 남녀 황금 성비율 + 05/05) -->
  <div class="flex justify-between items-center z-10 w-full px-2 pt-1">
    <!-- Brand Badge -->
    <div class="inline-flex items-center gap-3 bg-slate-900/90 backdrop-blur-md border border-white/20 rounded-full py-2.5 px-5 shadow-xl">
      <span class="text-lg">💖</span>
      <span class="text-base font-black tracking-wider text-white">AURA</span>
      <span class="text-sm font-bold text-pink-400 pl-3 border-l border-white/25">50:50 남녀 황금 성비율</span>
    </div>

    <!-- Page Index -->
    <div class="text-amber-400 font-extrabold text-base bg-slate-900/90 backdrop-blur-md px-5 py-2.5 rounded-full border border-amber-500/40 shadow-xl tracking-wider">
      05 / 05 &gt;
    </div>
  </div>

  <!-- 2. Main Content Container -->
  <div class="flex flex-col items-center text-center z-10 space-y-6 my-auto px-2">
    
    <!-- Editorial Brand Subtitle -->
    <div class="flex flex-col items-center space-y-2">
      <div class="gold-divider w-96"></div>
      <p class="text-sm tracking-[0.4em] text-emerald-300 font-black uppercase py-1">
        — A U R A   S A F E   R A D A R —
      </p>
      <div class="gold-divider w-96"></div>
    </div>

    <!-- Main Question & Debate Glass Box -->
    <div class="glass-box rounded-3xl p-8 w-full max-w-[980px] border border-emerald-500/40 glow-radar text-left">
      
      <!-- Mini Category Badge -->
      <div class="flex items-center justify-between mb-4">
        <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/20 border border-emerald-400/40 text-emerald-300 text-sm font-black">
          <span>{debate_badge}</span>
        </div>
        <span class="text-sm text-amber-300 font-bold">2030 핫이슈 💬</span>
      </div>

      <!-- Main Headline -->
      <h1 class="text-3xl md:text-[31px] font-black leading-snug tracking-tight text-white mb-4">
        {debate_q}
      </h1>

      <!-- 2 Options Vote Cards -->
      <div class="grid grid-cols-2 gap-4 mt-5">
        
        <!-- Option 1: 쿨한 당일 직진 -->
        <div class="vote-card rounded-2xl p-5 border-l-4 border-l-emerald-400 bg-emerald-500/10 border-emerald-400/30">
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-sm font-black text-emerald-300">OPTION 1</span>
            <span class="text-sm font-black text-emerald-300">71% (대세)</span>
          </div>
          <p class="text-base font-black text-white leading-snug">
            {opt1_title}
          </p>
          <p class="text-xs text-slate-300 mt-1.5">
            {opt1_sub}
          </p>
        </div>

        <!-- Option 2: 며칠 대화 후 신중 만남 -->
        <div class="vote-card rounded-2xl p-5 border-l-4 border-l-amber-400">
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-sm font-black text-amber-300">OPTION 2</span>
            <span class="text-xs font-bold text-slate-400">29%</span>
          </div>
          <p class="text-base font-black text-white leading-snug">
            {opt2_title}
          </p>
          <p class="text-xs text-slate-400 mt-1.5">
            {opt2_sub}
          </p>
        </div>

      </div>

      <!-- Member Benefit Box -->
      <div class="benefit-box rounded-2xl p-5 mt-5 text-left">
        <p class="text-sm font-black text-emerald-300 flex items-center gap-2 mb-2">
          <span>🎁</span>
          <span>지금 Aura 무료 가입 시 즉시 지급되는 안심 혜택:</span>
        </p>
        <div class="grid grid-cols-3 gap-3 text-xs font-bold text-slate-200">
          <div class="flex items-center gap-1.5">
            <span class="text-emerald-400">✔</span>
            <span>{benefits[0]}</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="text-emerald-400">✔</span>
            <span>{benefits[1]}</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="text-emerald-400">✔</span>
            <span>{benefits[2]}</span>
          </div>
        </div>
      </div>

    </div>

    <!-- 3. Glow Naver Search Bar (Official Mandatory Keyword) -->
    <div class="w-full max-w-[980px] flex flex-col items-center space-y-2.5">
      <div class="w-full bg-white rounded-2xl p-5 flex items-center justify-between naver-glow border-2 border-[#03C75A]">
        <!-- Naver N Logo -->
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-[#03C75A] flex items-center justify-center font-black text-white text-2xl shadow-md">
            N
          </div>
          <div class="text-left">
            <p class="text-xs font-bold text-slate-500">네이버 검색창에 입력하세요</p>
            <p class="text-2xl font-black text-slate-900 tracking-tight">아우라AI데이팅</p>
          </div>
        </div>

        <!-- Search Button -->
        <div class="bg-[#03C75A] text-white font-black text-lg px-7 py-3.5 rounded-xl flex items-center gap-2 shadow-lg">
          <span>검색</span>
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
        </div>
      </div>
      
      <!-- Sub CTA text -->
      <p class="text-sm text-slate-300 font-bold tracking-wide pt-1">
        {cta_sub}
      </p>
    </div>

  </div>

  <!-- 4. Bottom Footer (Official Landing URL & Copyright) -->
  <div class="flex justify-between items-center z-10 w-full px-4 pt-2 border-t border-white/10 text-xs text-slate-400 font-medium">
    <div>
      <span class="text-slate-500">Official Web:</span>
      <span class="text-amber-400/90 font-bold ml-1">https://aura-ai-dating.vercel.app/</span>
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

        logger.info(f"✅ [AuraCardnewsS5Topic8Builder] 8번 주제 5번 엔딩 CTA 카드 생성 완료: {out_path}")
        return str(out_path)

    def produce(self, target_dir: str = None, copy_data: dict = None) -> str:
        """5번 카드뉴스 렌더링 및 저장"""
        if not target_dir:
            from brands.aura.aura_cardnews_storage import AuraCardnewsStorage
            t_path = AuraCardnewsStorage.create_target_directory(theme_code="safe_radar_500m")
        else:
            t_path = Path(target_dir)
            t_path.mkdir(parents=True, exist_ok=True)

        slide5_path = t_path / "slide_5.png"
        self.build_s5_ending_card(str(slide5_path), copy_data=copy_data)
        return str(slide5_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    builder = AuraCardnewsS5Topic8Builder()
    builder.produce()
