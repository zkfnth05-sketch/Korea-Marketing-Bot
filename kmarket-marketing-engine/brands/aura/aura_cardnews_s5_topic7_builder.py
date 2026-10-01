# -*- coding: utf-8 -*-
"""
AuraCardnewsS5Topic7Builder - 🏷️ [Aura 카드뉴스 7번 주제 5번 전용 럭셔리 엔딩 CTA 카드 빌더]
===================================================================================================
• 역할:
  - 7번 주제('AI 매력상 & 관상/궁합 진단')의 5번 엔딩을 1080x1350 카드뉴스 규격으로 100% 렌더링
  - 매력상 진단 찬반 토론(1번 객관적 데이터다 vs 2번 재미로만 본다)과 'Aura 무료 회원가입 & 3대 혜택' 완벽 융합
  - 네이버 검색창['아우라AI데이팅'] 및 상단 브랜드 배지['💖 AURA | 50:50 남녀 황금 성비율', '05 / 05 >'] 일체형
  - 산출물: 타겟 폴더의 slide_5.png
"""

import os
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright

logger = logging.getLogger("AuraCardnewsS5Topic7Builder")


class AuraCardnewsS5Topic7Builder:
    """Aura 주제 7(AI 매력상 진단) 5번 엔딩 찬반 토론 & 네이버 검색 CTA 카드 빌더"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent

    def build_s5_ending_card(self, output_png_path: str, copy_data: dict = None) -> str:
        """1080x1350 카드뉴스 규격 럭셔리 엔딩 CTA 카드 렌더링 (제미나이 동적 카피 주입)"""
        logger.info(f"🎨 [AuraCardnewsS5Topic7Builder] 7번 주제 5번 엔딩 CTA 카드 렌더링 시작: {output_png_path}")

        # 제미나이 동적 카피 또는 기본값
        s5_copy = copy_data.get("slide5", copy_data) if (isinstance(copy_data, dict) and "slide5" in copy_data) else (copy_data or {})
        debate_badge = s5_copy.get("debate_badge", "🔥 2030 매력 진단 찬반 토론")
        debate_question = s5_copy.get("debate_question", "AI가 분석해주는 내 매력상 & 궁합 진단, 객관적인 지표다 vs 재미로만 본다? 여러분의 선택은?")
        
        opt1_title = s5_copy.get("debate_opt1_title", "객관적 데이터 분석이다")
        opt1_sub = s5_copy.get("debate_opt1_sub", "얼굴 비율과 시각적 분위기를 정밀 분석하니 충분히 신뢰할 만하다")
        opt2_title = s5_copy.get("debate_opt2_title", "재미로만 가볍게 본다")
        opt2_sub = s5_copy.get("debate_opt2_sub", "흥미롭긴 하지만 연애는 직접 만나서 겪어봐야 진짜를 알 수 있다")

        default_benefits = [
            "AI 화보 보정권 3회",
            "VIP 우선 매칭권",
            "500m 안심 레이더"
        ]
        benefits = s5_copy.get("benefit_items", default_benefits)
        benefit_text = " + ".join(benefits) if isinstance(benefits, list) else str(benefits)

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Aura S5 Topic 7 Ending Debate & Naver Search CTA (1080x1350)</title>
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
      background: radial-gradient(circle at 50% 25%, #22142e 0%, #0e0915 55%, #040307 100%);
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
      background: linear-gradient(90deg, rgba(229, 169, 52, 0) 0%, rgba(229, 169, 52, 0.65) 50%, rgba(229, 169, 52, 0) 100%);
    }}

    /* 발광 텍스트 */
    .glow-gold {{
      text-shadow: 0 0 25px rgba(229, 169, 52, 0.5), 0 2px 4px rgba(0, 0, 0, 0.9);
    }}
    .glow-pink {{
      text-shadow: 0 0 20px rgba(236, 72, 153, 0.6);
    }}

    /* 프리미엄 글래스 카드 */
    .glass-box {{
      background: rgba(18, 14, 28, 0.82);
      backdrop-filter: blur(24px);
      border: 1px solid rgba(229, 169, 52, 0.28);
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }}

    /* 네이버 검색창 전용 스타일링 */
    .naver-search-box {{
      background: #FFFFFF;
      box-shadow: 0 16px 36px rgba(0, 0, 0, 0.5), 0 0 28px rgba(3, 199, 90, 0.35);
      border: 3px solid #03C75A;
    }}
  </style>
</head>
<body>

  <!-- Top Header Bar -->
  <div class="flex justify-between items-center w-full">
    <!-- Brand Badge -->
    <div class="inline-flex items-center gap-3 bg-slate-900/90 backdrop-blur-md border border-white/25 rounded-full py-2.5 px-5 shadow-2xl">
      <span class="text-lg">💖</span>
      <span class="text-base font-black tracking-wider text-white">AURA</span>
      <span class="text-sm font-bold text-pink-400 pl-3 border-l border-white/30">50:50 남녀 황금 성비율</span>
    </div>

    <!-- Page Indicator -->
    <div class="text-amber-400 font-black text-base bg-slate-900/90 backdrop-blur-md px-5 py-2.5 rounded-full border border-amber-500/50 shadow-2xl tracking-wider">
      05 / 05 &gt;
    </div>
  </div>

  <!-- Main Section: Debate Question & Voting Options -->
  <div class="flex flex-col items-center text-center space-y-4 my-auto">
    
    <!-- Category Badge -->
    <div class="inline-flex items-center gap-2 px-5 py-1.5 rounded-full bg-gradient-to-r from-purple-600 via-pink-600 to-amber-500 text-white text-sm font-black tracking-wider shadow-lg">
      <span>{debate_badge}</span>
    </div>

    <!-- Debate Title -->
    <h1 class="text-[34px] font-black leading-[1.28] text-white tracking-tight">
      {debate_question}
    </h1>

    <p class="text-slate-300 text-base font-semibold">
      여러분의 솔직한 생각을 댓글로 남겨주세요! 👇
    </p>

    <!-- 2 Voting Options Cards -->
    <div class="grid grid-cols-2 gap-4 w-full pt-1">
      
      <!-- Option 1 -->
      <div class="glass-box rounded-3xl p-5 text-left border-l-4 border-l-amber-400 hover:border-amber-300 transition-all flex flex-col justify-between">
        <div>
          <div class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-amber-500 text-slate-950 font-black text-sm mb-2 shadow-md">
            1
          </div>
          <h3 class="text-lg font-black text-amber-300 mb-1">
            "{opt1_title}"
          </h3>
          <p class="text-xs text-slate-300 leading-relaxed font-medium">
            {opt1_sub}
          </p>
        </div>
      </div>

      <!-- Option 2 -->
      <div class="glass-box rounded-3xl p-5 text-left border-l-4 border-l-pink-500 hover:border-pink-400 transition-all flex flex-col justify-between">
        <div>
          <div class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-pink-500 text-white font-black text-sm mb-2 shadow-md">
            2
          </div>
          <h3 class="text-lg font-black text-pink-300 mb-1">
            "{opt2_title}"
          </h3>
          <p class="text-xs text-slate-300 leading-relaxed font-medium">
            {opt2_sub}
          </p>
        </div>
      </div>

    </div>

  </div>

  <!-- Bottom Section: Membership Benefits & Naver Search Box -->
  <div class="flex flex-col space-y-4 pt-2">
    
    <div class="gold-divider w-full"></div>

    <!-- 3 Core Benefits Card -->
    <div class="glass-box rounded-3xl p-4 flex items-center justify-between shadow-xl">
      <div class="flex items-center gap-3">
        <div class="w-11 h-11 rounded-2xl bg-gradient-to-tr from-amber-500 to-pink-500 flex items-center justify-center text-xl shadow-lg">
          🎁
        </div>
        <div class="text-left">
          <div class="text-xs font-black text-amber-300 tracking-wider">AURA VIP 회원가입 즉시 100% 무료 지급</div>
          <div class="text-white text-sm font-bold mt-0.5">
            {benefit_text}
          </div>
        </div>
      </div>
      <span class="px-3 py-1.5 rounded-xl bg-amber-500/20 border border-amber-400/50 text-amber-300 text-xs font-black">
        즉시 적용
      </span>
    </div>

    <!-- Official Naver Search Bar -->
    <div class="naver-search-box rounded-2xl px-6 py-4 flex items-center justify-between cursor-pointer">
      <div class="flex items-center gap-3.5">
        <!-- Naver N Logo -->
        <div class="w-8 h-8 rounded-lg bg-[#03C75A] flex items-center justify-center text-white font-black text-lg shadow-sm">
          N
        </div>
        <div class="text-left">
          <span class="text-slate-900 text-xl font-black tracking-tight">아우라AI데이팅</span>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-xs font-extrabold text-[#03C75A] bg-green-50 px-2.5 py-1 rounded-md border border-[#03C75A]/30">
          통합검색
        </span>
        <!-- Search Magnifier Icon -->
        <svg class="w-6 h-6 text-[#03C75A]" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
        </svg>
      </div>
    </div>

    <!-- Sub URL Info -->
    <div class="text-center text-xs text-slate-400 font-medium">
      네이버 검색창에 <span class="text-emerald-400 font-bold">'아우라AI데이팅'</span>을 검색하고 AI 매력 진단 리포트를 받아보세요!
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

        logger.info(f"✅ [AuraCardnewsS5Topic7Builder] 7번 5번 엔딩 CTA 카드 생성 완료: {out_path}")
        return str(out_path)

    def produce(self, target_dir: str = None, copy_data: dict = None) -> str:
        """5번 엔딩 카드 렌더링 및 저장"""
        if not target_dir:
            from .aura_cardnews_storage import AuraCardnewsStorage
            t_path = AuraCardnewsStorage.create_target_directory(theme_code="ai_charm_scanner")
        else:
            t_path = Path(target_dir)
            t_path.mkdir(parents=True, exist_ok=True)

        slide5_path = t_path / "slide_5.png"
        return self.build_s5_ending_card(str(slide5_path), copy_data=copy_data)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    builder = AuraCardnewsS5Topic7Builder()
    builder.produce()

