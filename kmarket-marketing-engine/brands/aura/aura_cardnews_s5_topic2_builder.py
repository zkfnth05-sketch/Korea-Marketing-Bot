# -*- coding: utf-8 -*-
"""
AuraCardnewsS5Topic2Builder - 🏷️ [Aura 카드뉴스 2번 주제 5번 전용 글로벌 회원유입 럭셔리 엔딩 CTA 카드 빌더]
=======================================================================================================
• 역할:
  - 2번 주제('실시간 AI 자막 통화 / 글로벌 썸')의 5번 엔딩을 1080x1350 카드뉴스 규격으로 100% 렌더링
  - 찬반 토론(1번 감정 통하면 가능 vs 2번 깊은 대화는 무리)과 '글로벌 라운지 무료 가입' 직결 혜택 완벽 융합
  - 네이버 검색창['아우라AI데이팅'] 및 상단 브랜드 배지['💖 AURA | 50:50 남녀 황금 성비율', '05 / 05 >'] 일체형
  - 산출물: 타겟 폴더의 slide_5.png
"""

import os
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright

logger = logging.getLogger("AuraCardnewsS5Topic2Builder")


class AuraCardnewsS5Topic2Builder:
    """Aura 주제 2(실시간 AI 자막 통화) 5번 엔딩 글로벌 회원유입 & 네이버 검색 CTA 카드 빌더"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent

    def build_s5_ending_card(self, output_png_path: str, copy_data: dict = None) -> str:
        """1080x1350 카드뉴스 규격 럭셔리 엔딩 CTA 카드 렌더링 (제미나이 동적 카피 주입)"""
        logger.info(f"🎨 [AuraCardnewsS5Topic2Builder] 2번 주제 5번 엔딩 CTA 카드 렌더링 시작: {output_png_path}")

        # 제미나이 동적 카피 또는 기본값
        s5_copy = copy_data.get("slide5", copy_data) if (isinstance(copy_data, dict) and "slide5" in copy_data) else (copy_data or {})
        debate_badge = s5_copy.get("debate_badge", "🌐 글로벌 썸 찬반 토론")
        debate_question = s5_copy.get("debate_question", "외국어 몰라도 실시간 AI 자막으로 글로벌 연애 가능 vs 그래도 무리? 여러분의 생각은?")
        
        opt1_title = s5_copy.get("debate_opt1_title", "마음과 눈빛이 통하면 언어는 AI가 해결!")
        opt1_sub = s5_copy.get("debate_opt1_sub", "실시간 자막으로 새벽까지 3시간 통화 가능")
        opt2_title = s5_copy.get("debate_opt2_title", "깊은 감정 교류까지는 그래도 무리다")
        opt2_sub = s5_copy.get("debate_opt2_sub", "직접 언어가 통해야 진짜 연애가 된다")

        default_benefits = [
            "3초 글로벌 이상형 확인",
            "글로벌 라운지 입장",
            "실시간 자막 통화 무료"
        ]
        benefits = s5_copy.get("benefit_items", default_benefits)
        while len(benefits) < 3:
            benefits.append("Aura VIP 글로벌 혜택")

        cta_subtext = s5_copy.get("cta_subtext", "👉 프로필 링크에서 3초 만에 글로벌 이상형 확인해보세요! ✨")

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Aura S5 Topic 2 Ending CTA (1080x1350)</title>
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
      background: radial-gradient(circle at 50% 25%, #151a2e 0%, #0a0d18 55%, #030408 100%);
      color: #fff;
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 36px 44px 40px;
    }}

    /* 금빛 수평선 */
    .gold-divider {{
      height: 1px;
      background: linear-gradient(90deg, rgba(56, 189, 248, 0) 0%, rgba(56, 189, 248, 0.8) 50%, rgba(56, 189, 248, 0) 100%);
    }}

    /* 글래스 카드 */
    .glass-box {{
      background: rgba(15, 23, 42, 0.88);
      backdrop-filter: blur(28px);
      -webkit-backdrop-filter: blur(28px);
      border: 1px solid rgba(255, 255, 255, 0.14);
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.85);
    }}

    .vote-card {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.12);
      backdrop-filter: blur(16px);
      transition: all 0.2s ease;
    }}

    .benefit-box {{
      background: linear-gradient(135deg, rgba(56, 189, 248, 0.12) 0%, rgba(168, 85, 247, 0.08) 100%);
      border: 1px solid rgba(56, 189, 248, 0.35);
    }}

    .glow-cyan {{
      box-shadow: 0 0 45px rgba(56, 189, 248, 0.35);
    }}

    .naver-glow {{
      box-shadow: 0 10px 40px rgba(3, 199, 90, 0.4), 0 0 30px rgba(56, 189, 248, 0.35);
    }}
  </style>
</head>
<body>

  <!-- Ambient Cinematic Background Glows -->
  <div class="absolute w-[800px] h-[800px] rounded-full bg-sky-500/10 blur-[150px] top-0 left-1/2 -translate-x-1/2 pointer-events-none"></div>
  <div class="absolute w-[600px] h-[600px] rounded-full bg-purple-500/10 blur-[130px] bottom-10 right-10 pointer-events-none"></div>

  <!-- 1. Top Header Bar (Aura 50:50 남녀 황금 성비율 + 05/05) -->
  <div class="flex justify-between items-center z-10 w-full px-2">
    <!-- Brand Badge -->
    <div class="inline-flex items-center gap-2.5 bg-slate-900/90 backdrop-blur-md border border-white/20 rounded-full py-2.5 px-5 shadow-xl">
      <span class="text-base">💖</span>
      <span class="text-base font-black tracking-wider text-white">AURA</span>
      <span class="text-xs font-bold text-pink-400 pl-2.5 border-l border-white/25">50:50 남녀 황금 성비율</span>
    </div>

    <!-- Page Index -->
    <div class="text-amber-400 font-extrabold text-sm bg-slate-900/90 backdrop-blur-md px-5 py-2.5 rounded-full border border-amber-500/40 shadow-xl tracking-wider">
      05 / 05 &gt;
    </div>
  </div>

  <!-- 2. Main Content Container -->
  <div class="flex flex-col items-center text-center z-10 space-y-5 my-auto px-2">
    
    <!-- Editorial Brand Subtitle -->
    <div class="flex flex-col items-center space-y-1.5">
      <div class="gold-divider w-80"></div>
      <p class="text-xs tracking-[0.35em] text-sky-400 font-bold uppercase py-1">
        — A U R A   G L O B A L   S U B T I T L E —
      </p>
      <div class="gold-divider w-80"></div>
    </div>

    <!-- Main Question & Debate Glass Box -->
    <div class="glass-box rounded-3xl p-6 w-full max-w-[960px] border border-sky-400/40 glow-cyan text-left">
      
      <!-- Mini Category Badge -->
      <div class="flex items-center justify-between mb-3">
        <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-sky-500/20 border border-sky-400/40 text-sky-300 text-xs font-black">
          <span>🌐</span>
          <span>{debate_badge}</span>
        </div>
        <span class="text-xs text-amber-300 font-bold">2030 핫이슈 🔥</span>
      </div>

      <!-- Main Headline -->
      <h1 class="text-2xl md:text-[28px] font-black leading-snug tracking-tight text-white mb-2">
        "{debate_question}"
      </h1>

      <!-- 2 Options Vote Cards -->
      <div class="grid grid-cols-2 gap-3.5 mt-4">
        
        <!-- Option 1: 가능 -->
        <div class="vote-card rounded-2xl p-4 border-l-4 border-l-emerald-400">
          <div class="flex items-center justify-between mb-1">
            <span class="text-xs font-black text-emerald-300">OPTION 1</span>
            <span class="text-xs font-black text-emerald-300">58% (인기)</span>
          </div>
          <p class="text-sm font-black text-white leading-snug">
            "{opt1_title}"
          </p>
          <p class="text-[11px] text-slate-400 mt-1">
            {opt1_sub}
          </p>
        </div>

        <!-- Option 2: 무리 -->
        <div class="vote-card rounded-2xl p-4 border-l-4 border-l-rose-400">
          <div class="flex items-center justify-between mb-1">
            <span class="text-xs font-black text-rose-300">OPTION 2</span>
            <span class="text-xs font-bold text-slate-400">42%</span>
          </div>
          <p class="text-sm font-black text-white leading-snug">
            "{opt2_title}"
          </p>
          <p class="text-[11px] text-slate-400 mt-1">
            {opt2_sub}
          </p>
        </div>

      </div>

      <!-- Member Benefit Box -->
      <div class="benefit-box rounded-2xl p-4 mt-4 text-left">
        <p class="text-xs font-black text-sky-300 flex items-center gap-1.5 mb-1.5">
          <span>🎁</span>
          <span>지금 Aura 무료 가입 시 즉시 지급되는 글로벌 혜택:</span>
        </p>
        <div class="grid grid-cols-3 gap-2 text-[11px] font-bold text-slate-200">
          <div class="flex items-center gap-1">
            <span class="text-emerald-400">✔</span>
            <span>{benefits[0]}</span>
          </div>
          <div class="flex items-center gap-1">
            <span class="text-emerald-400">✔</span>
            <span>{benefits[1]}</span>
          </div>
          <div class="flex items-center gap-1">
            <span class="text-emerald-400">✔</span>
            <span>{benefits[2]}</span>
          </div>
        </div>
      </div>

    </div>

    <!-- 3. Glow Naver Search Bar (Official Mandatory Keyword) -->
    <div class="w-full max-w-[960px] flex flex-col items-center space-y-2">
      <div class="w-full bg-white rounded-2xl p-4 flex items-center justify-between naver-glow border-2 border-[#03C75A]">
        <!-- Naver N Logo -->
        <div class="flex items-center gap-3.5">
          <div class="w-10 h-10 rounded-xl bg-[#03C75A] flex items-center justify-center font-black text-white text-2xl shadow-md">
            N
          </div>
          <div class="text-left">
            <p class="text-[11px] font-bold text-slate-500">네이버 검색창에 입력하세요</p>
            <p class="text-2xl font-black text-slate-900 tracking-tight">아우라AI데이팅</p>
          </div>
        </div>

        <!-- Search Button -->
        <div class="bg-[#03C75A] text-white font-black text-base px-6 py-3 rounded-xl flex items-center gap-1.5 shadow-lg">
          <span>검색</span>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
        </div>
      </div>
      
      <!-- Sub CTA text -->
      <p class="text-xs text-slate-300 font-bold tracking-wide pt-0.5">
        {cta_subtext}
      </p>
    </div>

  </div>

  <!-- 4. Bottom Footer (Official Landing URL & Copyright) -->
  <div class="flex justify-between items-center z-10 w-full px-4 pt-2 border-t border-white/10 text-xs text-slate-400 font-medium">
    <div>
      <span class="text-slate-500">Official Web:</span>
      <span class="text-sky-400 font-bold ml-1">https://aura-ai-dating.vercel.app/</span>
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

        logger.info(f"✅ [AuraCardnewsS5Topic2Builder] 2번 주제 5번 엔딩 CTA 카드 생성 완료: {out_path}")
        return str(out_path)

    def produce(self, target_dir: str = None, copy_data: dict = None) -> str:
        """5번 엔딩 카드 렌더링 및 저장"""
        if not target_dir:
            from .aura_cardnews_storage import AuraCardnewsStorage
            t_path = AuraCardnewsStorage.create_target_directory(theme_code="realtime_subtitles")
        else:
            t_path = Path(target_dir)
            t_path.mkdir(parents=True, exist_ok=True)

        slide5_path = t_path / "slide_5.png"
        return self.build_s5_ending_card(str(slide5_path), copy_data=copy_data)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_out = r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\아우라\test_topic2_s5.png"
    builder = AuraCardnewsS5Topic2Builder()
    builder.build_s5_ending_card(test_out)
