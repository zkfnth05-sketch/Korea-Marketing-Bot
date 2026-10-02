# -*- coding: utf-8 -*-
"""
AuraCardnewsS5Topic3Builder - 🏷️ [Aura 카드뉴스 3번 주제 5번 전용 숏폼 계승 럭셔리 엔딩 CTA 카드 빌더]
===================================================================================================
• 역할:
  - 숏폼 3번 엔딩 CTA 카드의 럭셔리 에디토리얼 디자인을 1080x1350 카드뉴스 규격으로 100% 계승
  - 50:50 VIP 정원제 찬반 토론(1번 찬성 vs 2번 반대)과 네이버 검색창['아우라AI데이팅'] 완벽 융합
  - 상단 브랜드 배지['💖 AURA | 50:50 남녀 황금 성비율', '05 / 05 >'] 및 공식 URL 일체형 렌더링
  - 산출물: 바탕화면 타겟 폴더의 slide_5.png
"""

import os
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright

logger = logging.getLogger("AuraCardnewsS5Topic3Builder")


class AuraCardnewsS5Topic3Builder:
    """Aura 주제 3(50:50 VIP 게이트) 5번 엔딩 찬반 토론 & 네이버 검색 CTA 카드 빌더"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent

    def build_s5_ending_card(self, output_png_path: str, copy_data: dict = None) -> str:
        """1080x1350 카드뉴스 규격 럭셔리 엔딩 CTA 카드 렌더링 (제미나이 동적 카피 주입)"""
        logger.info(f"🎨 [AuraCardnewsS5Topic3Builder] 5번 엔딩 CTA 카드 렌더링 시작: {output_png_path}")

        # 제미나이 동적 카피 또는 기본값
        s5_copy = copy_data.get("slide5", copy_data) if (isinstance(copy_data, dict) and "slide5" in copy_data) else (copy_data or {})
        debate_badge = s5_copy.get("debate_badge", "🔥 댓글 찬반 투표")
        debate_question = s5_copy.get("debate_question", "성비 안 맞으면 입장 제한하는 50:50 정원제, 찬성 vs 반대? 여러분의 생각은?")
        
        opt1_title = s5_copy.get("debate_opt1_title", "1번 찬성")
        opt1_sub = s5_copy.get("debate_opt1_sub", "진성 회원만 모이고 남탕 스트레스 없으니 무조건 찬성이다!")
        opt2_title = s5_copy.get("debate_opt2_title", "2번 반대")
        opt2_sub = s5_copy.get("debate_opt2_sub", "내가 가입하고 싶을 때 기다려야 하니 너무 답답하고 과하다!")

        cta_subtext = s5_copy.get("cta_subtext", "👉 프로필 링크에서 3초 만에 내 이상형/성향 확인해보세요! ✨")

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Aura S5 Ending Debate & Naver Search CTA (1080x1350)</title>
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
      background: radial-gradient(circle at 50% 25%, #181926 0%, #0a0a0f 55%, #030305 100%);
      color: #fff;
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 30px 40px 40px;
    }}

    /* 금빛 수평선 */
    .gold-divider {{
      height: 1px;
      background: linear-gradient(90deg, rgba(229, 169, 52, 0) 0%, rgba(229, 169, 52, 0.8) 50%, rgba(229, 169, 52, 0) 100%);
    }}

    /* 글래스 카드 */
    .glass-box {{
      background: rgba(18, 18, 26, 0.85);
      backdrop-filter: blur(28px);
      -webkit-backdrop-filter: blur(28px);
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.85);
    }}

    .vote-card {{
      border: 1px solid rgba(255, 255, 255, 0.12);
      backdrop-filter: blur(16px);
      transition: all 0.2s ease;
    }}

    .glow-gold {{
      box-shadow: 0 0 50px rgba(229, 169, 52, 0.3);
    }}

    .naver-glow {{
      box-shadow: 0 10px 40px rgba(3, 199, 90, 0.35), 0 0 30px rgba(229, 169, 52, 0.25);
    }}
  </style>
</head>
<body>

  <!-- Ambient Cinematic Background Glows -->
  <div class="absolute w-[800px] h-[800px] rounded-full bg-amber-500/10 blur-[150px] top-0 left-1/2 -translate-x-1/2 pointer-events-none"></div>
  <div class="absolute w-[600px] h-[600px] rounded-full bg-pink-500/10 blur-[130px] bottom-10 right-10 pointer-events-none"></div>

  <!-- 1. Top Header Bar (Aura 50:50 남녀 황금 성비율 + 05/05) -->
  <div class="flex justify-between items-center z-10 w-full px-2">
    <!-- Brand Badge -->
    <div class="inline-flex items-center gap-2.5 bg-slate-900/90 backdrop-blur-md border border-white/20 rounded-full py-2 px-4 shadow-xl">
      <span class="text-base">💖</span>
      <span class="text-base font-black tracking-wider text-white">AURA</span>
      <span class="text-xs font-bold text-pink-400 pl-2.5 border-l border-white/25">50:50 남녀 황금 성비율</span>
    </div>

    <!-- Page Index -->
    <div class="text-amber-400 font-extrabold text-sm bg-slate-900/90 backdrop-blur-md px-5 py-2 rounded-full border border-amber-500/40 shadow-xl tracking-wider">
      05 / 05 &gt;
    </div>
  </div>

  <!-- 2. Main Content Container -->
  <div class="flex flex-col items-center text-center z-10 space-y-4 my-auto px-2">
    
    <!-- Editorial Brand Subtitle -->
    <div class="flex flex-col items-center space-y-1.5">
      <div class="gold-divider w-72"></div>
      <p class="text-xs tracking-[0.35em] text-[#E5A934] font-bold uppercase py-1">
        — A U R A   V I P   L O U N G E —
      </p>
      <div class="gold-divider w-72"></div>
    </div>

    <!-- Topic Title -->
    <p class="text-lg text-zinc-400 font-semibold tracking-wide">
      국내 최초 50:50 성비 보장 • 프라이빗 VIP 라운지
    </p>

    <!-- Hero Title -->
    <h1 class="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-[#E5A934] to-yellow-500 tracking-tight leading-snug drop-shadow-[0_4px_24px_rgba(229,169,52,0.4)]">
      남녀 성비 50:50 안 맞으면 문 닫습니다! 👑
    </h1>

    <!-- Debate Question Box -->
    <div class="glass-box rounded-3xl p-7 w-full max-w-2xl border border-white/20 space-y-5">
      
      <!-- Question Badge -->
      <div class="inline-block px-4 py-1.5 rounded-full bg-pink-500/20 text-pink-400 font-extrabold text-xs tracking-wider border border-pink-500/30">
        {debate_badge}
      </div>

      <h2 class="text-2xl font-black text-white leading-relaxed">
        "{debate_question}"
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
            <span class="text-base font-black text-amber-300">{opt1_title}</span>
          </div>
          <p class="text-xs text-zinc-200 font-medium leading-relaxed">
            {opt1_sub}
          </p>
        </div>

        <!-- Option 2 -->
        <div class="vote-card rounded-2xl p-4 text-left space-y-2 border-zinc-700 bg-white/5">
          <div class="flex items-center gap-2">
            <span class="text-xl">👎</span>
            <span class="text-base font-black text-zinc-300">{opt2_title}</span>
          </div>
          <p class="text-xs text-zinc-400 font-medium leading-relaxed">
            {opt2_sub}
          </p>
        </div>
      </div>

    </div>

    <!-- 3. Official Naver Search Bar (The Core CTA) -->
    <div class="w-full max-w-2xl space-y-3 pt-2">
      <!-- Naver Search Bar -->
      <div class="w-full h-20 rounded-full bg-white flex items-center px-4 shadow-[0_15px_50px_rgba(212,175,55,0.4)] naver-glow border-2 border-amber-300/60">
        <!-- Green Naver N Badge -->
        <div class="w-12 h-12 rounded-full bg-[#03C75A] flex items-center justify-center font-black text-white text-2xl tracking-tighter shadow-md">
          N
        </div>
        <!-- Search Keyword Input -->
        <div class="flex-1 px-4 text-left">
          <span class="text-xs text-zinc-400 font-bold block">네이버 공식 검색어</span>
          <span class="text-2xl font-black text-slate-900 tracking-tight">아우라AI데이팅</span>
        </div>
        <!-- Search Glass Icon Button -->
        <div class="w-12 h-12 rounded-full bg-slate-950 flex items-center justify-center text-amber-400 shadow-md">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        </div>
      </div>

      <!-- Search Instruction Text -->
      <p class="text-base font-bold text-amber-300 tracking-wide pt-1">
        🔍 지금 네이버 검색창에 <span class="text-white underline underline-offset-4 decoration-[#03C75A] font-extrabold">'아우라AI데이팅'</span>을 검색해보세요!
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

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
            page.set_content(html_content, wait_until="networkidle")
            page.screenshot(path=str(out_p), full_page=True)
            browser.close()

        logger.info(f"✅ [AuraCardnewsS5Topic3Builder] 5번 엔딩 카드 렌더링 완료: {out_p}")
        return str(out_p)

    def produce(self, target_dir: str = None, copy_data: dict = None) -> str:
        """5번 엔딩 카드 렌더링 및 저장"""
        if not target_dir:
            from .aura_cardnews_storage import AuraCardnewsStorage
            t_path = AuraCardnewsStorage.create_target_directory(theme_code="vip_gate_5050")
        else:
            t_path = Path(target_dir)
            t_path.mkdir(parents=True, exist_ok=True)

        slide5_path = t_path / "slide_5.png"
        return self.build_s5_ending_card(str(slide5_path), copy_data=copy_data)


if __name__ == "__main__":
    builder = AuraCardnewsS5Topic3Builder()
    out = r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\아우라\test_topic3_s5.png"
    res = builder.build_s5_ending_card(out)
    print("Done Slide 5:", res)
