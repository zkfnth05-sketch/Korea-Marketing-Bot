# -*- coding: utf-8 -*-
"""
AuraCardnewsS2S4BalanceBuilder - 🏷️ [Aura 카드뉴스 5번 주제 2, 3, 4번 숏폼 가치관 밸런스 매칭 이식 빌더]
===================================================================================================
• 역할:
  - 숏폼 5번 주제의 '가치관 밸런스 매칭 4대 세로형 비대칭 파스텔 카드 시뮬레이터'를
    1080x1350 카드뉴스 규격으로 1:1 완벽 이식
  - 대표님 피드백 완벽 반영:
    1) 상단 질문 큼직하게 하향 배치 (48px Black)
    2) 카드 내부 메인 2줄(38px), 구분선, 서브 설명(22px), 투표율 뱃지(22px) 풍성하게 확대
    3) 하단 일치율 정보 박스를 위로 확실하게 올리고 글씨를 28px/19px 초대형으로 확대
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any
from playwright.sync_api import sync_playwright

logger = logging.getLogger("AuraCardnewsS2S4BalanceBuilder")


class AuraCardnewsS2S4BalanceBuilder:
    """1080x1350 카드뉴스 규격 가치관 밸런스 매칭 (2, 3, 4번 슬라이드) 전문 빌더"""

    def __init__(self):
        self.slides_data: Dict[int, Dict[str, Any]] = {
            2: {
                "slide_num": 2,
                "round_num": "01",
                "tag_en": "VERTICAL BALANCE • DATING COST",
                "question": "소개팅 첫 만남 계산은?",
                "bg_gradient": "radial-gradient(circle at 50% 25%, #FDEEE9 0%, #F6C6BC 60%, #E8B4AA 100%)",
                "card_a": {
                    "bg": "#14412D",
                    "border": "#245A42",
                    "inner_border": "rgba(255, 255, 255, 0.18)",
                    "text_color": "#FFFFFF",
                    "sub_color": "#D1E7DD",
                    "divider_color": "#38A169",
                    "badge_bg": "rgba(0, 0, 0, 0.35)",
                    "badge_border": "rgba(255, 255, 255, 0.25)",
                    "badge_text": "#F1F5F9",
                    "sub": "[ 부담 없는 1/N 정산 ]",
                    "main1": "칼같이 반띵",
                    "main2": "더치페이",
                    "ratio": "48%",
                    "ratio_bg": "rgba(0, 0, 0, 0.35)",
                    "ratio_border": "rgba(255, 255, 255, 0.3)",
                    "ratio_text": "#F8FAFC"
                },
                "card_b": {
                    "bg": "#FCF8F0",
                    "border": "#D4AF37",
                    "inner_border": "rgba(212, 175, 55, 0.4)",
                    "glow_color": "rgba(212, 175, 55, 0.5)",
                    "text_color": "#111827",
                    "sub_color": "#785A4B",
                    "divider_color": "#D4AF37",
                    "badge_bg": "#D4AF37",
                    "badge_border": "#B8860B",
                    "badge_text": "#FFFFFF",
                    "sub": "[ 센스 있는 번갈아 내기 ]",
                    "main1": "1차 사면",
                    "main2": "2차는 상대방이",
                    "ratio": "✓ 52% 선택",
                    "ratio_bg": "linear-gradient(135deg, #D4AF37 0%, #B8860B 100%)",
                    "ratio_border": "#996515",
                    "ratio_text": "#FFFFFF"
                },
                "info_badge": "ROUND #01 데이트 비용 가치관",
                "info_selected": "선택: 1차 사면 2차는 상대방이 센스 있게 계산 (52% 일치)",
                "info_sub": "나와 생각 통하는 사람만 100% 매칭 • 갈등 없는 편안한 연애"
            },
            3: {
                "slide_num": 3,
                "round_num": "02",
                "tag_en": "VERTICAL BALANCE • CONTACT STYLE",
                "question": "연인 간 일상 카톡 연락은?",
                "bg_gradient": "radial-gradient(circle at 50% 25%, #FEF9EB 0%, #F8EBCD 60%, #EAD8B0 100%)",
                "card_a": {
                    "bg": "#413750",
                    "border": "#5B4D72",
                    "inner_border": "rgba(255, 255, 255, 0.18)",
                    "text_color": "#FFFFFF",
                    "sub_color": "#E9D5FF",
                    "divider_color": "#9333EA",
                    "badge_bg": "rgba(0, 0, 0, 0.35)",
                    "badge_border": "rgba(255, 255, 255, 0.25)",
                    "badge_text": "#F1F5F9",
                    "sub": "[ 즉각적인 애정 확인 ]",
                    "main1": "30분 이내",
                    "main2": "칼답 필수!",
                    "ratio": "38%",
                    "ratio_bg": "rgba(0, 0, 0, 0.35)",
                    "ratio_border": "rgba(255, 255, 255, 0.3)",
                    "ratio_text": "#F8FAFC"
                },
                "card_b": {
                    "bg": "#FFFEFB",
                    "border": "#A855F7",
                    "inner_border": "rgba(168, 85, 247, 0.4)",
                    "glow_color": "rgba(168, 85, 247, 0.45)",
                    "text_color": "#111827",
                    "sub_color": "#6B21A8",
                    "divider_color": "#A855F7",
                    "badge_bg": "#A855F7",
                    "badge_border": "#7E22CE",
                    "badge_text": "#FFFFFF",
                    "sub": "[ 서로의 일상 존중 ]",
                    "main1": "일할 땐 집중",
                    "main2": "자유롭게 몰아서",
                    "ratio": "✓ 62% 선택",
                    "ratio_bg": "linear-gradient(135deg, #A855F7 0%, #7E22CE 100%)",
                    "ratio_border": "#6B21A8",
                    "ratio_text": "#FFFFFF"
                },
                "info_badge": "ROUND #02 연락 빈도 가치관",
                "info_selected": "선택: 일할 땐 자유롭게, 쉴 때 정성 연락 (62% 일치)",
                "info_sub": "답장 압박 없는 건강한 연애 • 신뢰 기반의 성숙한 소통"
            },
            4: {
                "slide_num": 4,
                "round_num": "04",
                "tag_en": "VERTICAL BALANCE • FRIENDSHIP",
                "question": "내 애인의 남사친/여사친 허용은?",
                "bg_gradient": "radial-gradient(circle at 50% 25%, #EDF6FC 0%, #D2E4F2 60%, #B8D2E7 100%)",
                "card_a": {
                    "bg": "#375078",
                    "border": "#4B6B9E",
                    "inner_border": "rgba(255, 255, 255, 0.18)",
                    "text_color": "#FFFFFF",
                    "sub_color": "#BAE6FD",
                    "divider_color": "#38BDF8",
                    "badge_bg": "rgba(0, 0, 0, 0.35)",
                    "badge_border": "rgba(255, 255, 255, 0.25)",
                    "badge_text": "#F1F5F9",
                    "sub": "[ 오랜 친구는 인정 ]",
                    "main1": "단둘이 식사/커피",
                    "main2": "쿨하게 OK",
                    "ratio": "24%",
                    "ratio_bg": "rgba(0, 0, 0, 0.35)",
                    "ratio_border": "rgba(255, 255, 255, 0.3)",
                    "ratio_text": "#F8FAFC"
                },
                "card_b": {
                    "bg": "#FDFAFC",
                    "border": "#F472B6",
                    "inner_border": "rgba(244, 114, 182, 0.4)",
                    "glow_color": "rgba(244, 114, 182, 0.45)",
                    "text_color": "#111827",
                    "sub_color": "#9D174D",
                    "divider_color": "#F472B6",
                    "badge_bg": "#F472B6",
                    "badge_border": "#DB2777",
                    "badge_text": "#FFFFFF",
                    "sub": "[ 연인 사이 최소한의 예의 ]",
                    "main1": "단둘이 만나는 건",
                    "main2": "절대 불가!",
                    "ratio": "✓ 76% 선택",
                    "ratio_bg": "linear-gradient(135deg, #F472B6 0%, #DB2777 100%)",
                    "ratio_border": "#BE185D",
                    "ratio_text": "#FFFFFF"
                },
                "info_badge": "ROUND #04 이성 친구 가치관",
                "info_selected": "선택: 단둘 만남 절대 불가 • 상호 배려 원칙 (76% 일치)",
                "info_sub": "불안감 제로 안심 연애 • 오직 서로에게만 집중하는 만남"
            }
        }

    def _generate_slide_html(self, slide_idx: int) -> str:
        """단일 슬라이드의 1080x1350 초고화질 HTML 코드 생성"""
        data = self.slides_data[slide_idx]
        slide_num_str = f"{data['slide_num']:02d} / 05 &gt;"
        
        ca = data["card_a"]
        cb = data["card_b"]

        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Aura Slide {slide_idx} - Value Balance Matching</title>
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
      background: {data["bg_gradient"]};
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 34px 44px 38px;
    }}

    /* 글래스 & 섀도우 효과 */
    .card-shadow-a {{
      box-shadow: 0 24px 50px rgba(20, 25, 35, 0.28), 0 8px 16px rgba(0, 0, 0, 0.15);
    }}

    .card-shadow-b {{
      box-shadow: 0 30px 65px {cb["glow_color"]}, 0 10px 24px rgba(0, 0, 0, 0.12);
    }}

    .info-glass-box {{
      background: rgba(255, 253, 248, 0.96);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border: 2px solid rgba(212, 175, 55, 0.6);
      box-shadow: 0 24px 55px rgba(50, 40, 30, 0.18);
    }}

    .vs-badge-glow {{
      box-shadow: 0 0 35px rgba(0, 0, 0, 0.4), 0 0 18px rgba(212, 175, 55, 0.6);
    }}
  </style>
</head>
<body>

  <!-- 1. Top Header Bar (Brand Badge + Page Index) -->
  <div class="flex justify-between items-center z-10 w-full">
    <!-- Brand Badge -->
    <div class="inline-flex items-center gap-3 bg-slate-900/90 backdrop-blur-md border border-white/25 rounded-full py-2.5 px-5 shadow-xl">
      <span class="text-lg">💖</span>
      <span class="text-base font-black tracking-wider text-white">AURA</span>
      <span class="text-sm font-bold text-pink-400 pl-3 border-l border-white/30">50:50 남녀 황금 성비율</span>
    </div>

    <!-- Page Index -->
    <div class="text-amber-400 font-black text-base bg-slate-900/90 backdrop-blur-md px-5 py-2.5 rounded-full border border-amber-500/50 shadow-xl tracking-wider">
      {slide_num_str}
    </div>
  </div>

  <!-- 2. Question & Editorial Subtitle Area (큼직하고 아래로 안정감 있게 배치) -->
  <div class="flex flex-col items-center text-center z-10 mt-5 mb-1">
    <div class="flex items-center gap-3 mb-2">
      <span class="h-[2px] w-14 bg-slate-700/50"></span>
      <span class="text-sm font-black tracking-[0.3em] text-slate-800 uppercase">
        {data["tag_en"]}
      </span>
      <span class="h-[2px] w-14 bg-slate-700/50"></span>
    </div>
    <h1 class="text-[46px] font-black text-slate-950 tracking-tight leading-none drop-shadow-sm">
      {data["question"]}
    </h1>
  </div>

  <!-- 3. Asymmetric Balance Matching Cards Container (With Central VS Badge) -->
  <div class="relative w-full flex justify-between items-center z-10 my-auto px-1">
    
    <!-- Option A Card (Left - Slightly Lower) -->
    <div class="w-[475px] h-[530px] rounded-[34px] p-7 flex flex-col justify-between card-shadow-a mt-10 relative"
         style="background-color: {ca['bg']}; color: {ca['text_color']}; border: 2.5px solid {ca['border']};">
      
      <!-- Inner Luxury Border -->
      <div class="absolute inset-3 rounded-[26px] pointer-events-none"
           style="border: 1.5px solid {ca['inner_border']};"></div>

      <!-- Top OPTION A Badge -->
      <div class="flex justify-center z-10 pt-1">
        <div class="px-6 py-2 rounded-full text-xs font-black tracking-widest uppercase shadow-md"
             style="background: {ca['badge_bg']}; color: {ca['badge_text']}; border: 1px solid {ca['badge_border']};">
          OPTION A
        </div>
      </div>

      <!-- Main Content (Main 2 Lines + Divider + Sub Explanation) -->
      <div class="text-center z-10 flex flex-col items-center my-auto">
        <h2 class="text-[38px] font-black leading-tight tracking-tight text-white mb-2">
          {ca["main1"]}<br>{ca["main2"]}
        </h2>
        
        <!-- Gold/Point Divider -->
        <div class="w-24 h-[2.5px] rounded-full my-2" style="background-color: {ca['divider_color']};"></div>

        <!-- Sub Korean Label (즉각적인 애정 확인 등) -->
        <p class="text-[21px] font-extrabold tracking-normal mt-1" style="color: {ca['sub_color']};">
          {ca["sub"]}
        </p>
      </div>

      <!-- Bottom Ratio Badge -->
      <div class="flex justify-center z-10 pb-1">
        <div class="px-8 py-3 rounded-full text-[21px] font-black tracking-wider shadow-inner"
             style="background: {ca['ratio_bg']}; color: {ca['ratio_text']}; border: 1.5px solid {ca['ratio_border']};">
          {ca["ratio"]}
        </div>
      </div>
    </div>

    <!-- Central VS Badge (Floating in Between) -->
    <div class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-20 vs-badge-glow">
      <div class="w-20 h-20 rounded-full bg-slate-900 border-2 border-amber-400 flex items-center justify-center text-amber-400 font-black text-2xl tracking-wider shadow-2xl">
        VS
      </div>
    </div>

    <!-- Option B Card (Right - Slightly Higher & Selected Gold Rim) -->
    <div class="w-[475px] h-[530px] rounded-[34px] p-7 flex flex-col justify-between card-shadow-b -mt-10 relative"
         style="background-color: {cb['bg']}; color: {cb['text_color']}; border: 3.5px solid {cb['border']};">
      
      <!-- Inner Luxury Border -->
      <div class="absolute inset-3 rounded-[26px] pointer-events-none"
           style="border: 1.5px solid {cb['inner_border']};"></div>

      <!-- Top OPTION B Badge -->
      <div class="flex justify-center z-10 pt-1">
        <div class="px-6 py-2 rounded-full text-xs font-black tracking-widest uppercase shadow-md"
             style="background: {cb['badge_bg']}; color: {cb['badge_text']}; border: 1px solid {cb['badge_border']};">
          OPTION B
        </div>
      </div>

      <!-- Main Content (Main 2 Lines + Divider + Sub Explanation) -->
      <div class="text-center z-10 flex flex-col items-center my-auto">
        <h2 class="text-[38px] font-black leading-tight tracking-tight text-slate-950 mb-2">
          {cb["main1"]}<br>{cb["main2"]}
        </h2>
        
        <!-- Gold/Point Divider -->
        <div class="w-24 h-[2.5px] rounded-full my-2" style="background-color: {cb['divider_color']};"></div>

        <!-- Sub Korean Label (서로의 일상 존중 등) -->
        <p class="text-[21px] font-black tracking-normal mt-1" style="color: {cb['sub_color']};">
          {cb["sub"]}
        </p>
      </div>

      <!-- Bottom Ratio Badge (Glow Active) -->
      <div class="flex justify-center z-10 pb-1">
        <div class="px-8 py-3 rounded-full text-[21px] font-black tracking-wider shadow-lg"
             style="background: {cb['ratio_bg']}; color: {cb['ratio_text']}; border: 1.5px solid {cb['ratio_border']};">
          {cb["ratio"]}
        </div>
      </div>
    </div>

  </div>

  <!-- 4. Bottom Info Match Box (위로 올리고 글자 크기 28px/19px로 대폭 확대) -->
  <div class="w-full info-glass-box rounded-3xl p-7 flex flex-col justify-center text-center z-10 space-y-2.5 mb-3">
    <div class="flex items-center justify-center gap-2">
      <span class="bg-amber-100 text-amber-950 text-base font-black px-5 py-2 rounded-full border border-amber-300 shadow-sm">
        {data["info_badge"]}
      </span>
    </div>
    <p class="text-[28px] font-black text-slate-950 tracking-tight leading-snug">
      {data["info_selected"]}
    </p>
    <p class="text-[19px] font-extrabold text-slate-700">
      {data["info_sub"]}
    </p>
  </div>

  <!-- 5. Bottom Brand Watermark -->
  <div class="text-center z-10">
    <p class="text-[12px] font-black tracking-[0.35em] text-slate-700/80 uppercase">
      AURA AI VALUE BALANCE MATCHING SYSTEM • 100% VERIFIED
    </p>
  </div>

</body>
</html>
"""
        return html

    def build_slide(self, slide_idx: int, output_png_path: str) -> str:
        """단일 슬라이드를 Playwright로 1080x1350 초고화질 서브픽셀 렌더링"""
        if slide_idx not in self.slides_data:
            raise ValueError(f"지원하지 않는 슬라이드 인덱스: {slide_idx} (2, 3, 4번만 지원)")

        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        html_content = self._generate_slide_html(slide_idx)

        logger.info(f"🎨 [AuraCardnewsS2S4BalanceBuilder] 슬라이드 {slide_idx}번 렌더링 시작 -> {out_path.name}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
            page.set_content(html_content, wait_until="networkidle")
            page.screenshot(path=str(out_path), full_page=True)
            browser.close()

        logger.info(f"✅ [AuraCardnewsS2S4BalanceBuilder] 슬라이드 {slide_idx}번 렌더링 완료: {out_path}")
        return str(out_path)

    def build_all(self, target_dir: str) -> Dict[int, str]:
        """2번, 3번, 4번 슬라이드 전체 생성 및 반환"""
        t_path = Path(target_dir)
        results = {}
        for idx in [2, 3, 4]:
            out_file = t_path / f"slide_{idx}.png"
            results[idx] = self.build_slide(idx, str(out_file))
        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_dir = r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\아우라\아우라_KO_value_balance_20260930_1821"
    builder = AuraCardnewsS2S4BalanceBuilder()
    builder.build_all(test_dir)
