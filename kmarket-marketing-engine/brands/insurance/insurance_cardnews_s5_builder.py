# -*- coding: utf-8 -*-
"""
InsuranceCardnewsS5Builder - 🏷️ [보험 리밸런스 5번 전용 찬반 토론 & 네이버 검색 CTA 카드 빌더]
================================================================================================
• 역할:
  - 보험 리밸런스 5번 엔딩을 1080x1350 카드뉴스 규격으로 100% 렌더링
  - 찬반 토론(1번 4세대 갈아타기 vs 2번 기존 실손 유지)과 '보험 리밸런스 0원 무료 진단' 혜택 완벽 융합
  - 네이버 공식 검색창['보험 리밸런스' (띄어쓰기 필수)] 및 상단 브랜드 배지 일체형
  - 산출물: 타겟 폴더의 slide_5.png
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from playwright.sync_api import sync_playwright

logger = logging.getLogger("InsuranceCardnewsS5Builder")


class InsuranceCardnewsS5Builder:
    """🛡️ 보험 리밸런스 5번 엔딩 찬반 토론 & 네이버 검색 CTA 카드 빌더"""

    BRAND_NAME = "보험 리밸런스"
    BRAND_SUB = "34개사 실시간 비교"
    OFFICIAL_SEARCH = "보험 리밸런스"
    OFFICIAL_URL = "https://insure-rebalance.vercel.app/"

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent

    def render_slide(self, output_png_path: str, copy_data: Dict[str, Any] = None) -> str:
        """1080x1350 규격 럭셔리 5번 엔딩 CTA 카드뉴스 렌더링"""
        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        s5_copy = copy_data or {}
        debate_badge = s5_copy.get("debate_badge", "⚡ 4세대 실손보험 찬반 토론")
        debate_question = s5_copy.get("debate_question", "4세대 실손 전환, 지금 갈아타기 vs 기존 1~3세대 유지 중 내 선택은?")
        
        opt1_title = s5_copy.get("debate_opt1_title", "📉 지금 즉시 4세대 전환")
        opt1_sub = s5_copy.get("debate_opt1_sub", "병원 거의 안 가고 월 보험료 최대 70% 아끼기!")
        opt1_rate = s5_copy.get("debate_opt1_rate", "74% (대세)")

        opt2_title = s5_copy.get("debate_opt2_title", "🏥 기존 1~3세대 실손 유지")
        opt2_sub = s5_copy.get("debate_opt2_sub", "도수치료/비급여 청구 많아서 기존 혜택 지키기!")
        opt2_rate = s5_copy.get("debate_opt2_rate", "26%")

        default_benefits = [
            "34개 보험사 실시간 최저가 비교",
            "이름·전화번호 입력 제로 (PII-Free)",
            "0.1초 만에 갱신 폭탄 자가진단"
        ]
        benefits = s5_copy.get("benefit_items", default_benefits)
        while len(benefits) < 3:
            benefits.append("보험 리밸런스 100% 무료 진단")

        cta_subtext = s5_copy.get("cta_subtext", "✨ 스팸 전화 0건 • 지금 조회하고 내 통장에서 매달 새는 보험료 막기")

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Insurance S5 Ending CTA (1080x1350)</title>
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
      background: radial-gradient(circle at 50% 25%, #052e1d 0%, #02170e 50%, #010a06 100%);
      color: #fff;
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 38px 48px 40px;
    }}

    /* 글래스 박스 및 글로우 (Deep Forest & Emerald Green) */
    .glass-box {{
      background: rgba(4, 30, 20, 0.88);
      backdrop-filter: blur(28px);
      -webkit-backdrop-filter: blur(28px);
      border: 1.5px solid rgba(16, 185, 129, 0.40);
      border-radius: 28px;
      padding: 32px 36px;
      box-shadow: 0 0 50px rgba(16, 185, 129, 0.20), 0 25px 60px rgba(0, 0, 0, 0.9);
    }}

    .vote-card-opt1 {{
      background: rgba(255, 255, 255, 0.04);
      border: 1.5px solid #10b981;
      border-radius: 20px;
      padding: 20px 22px;
      backdrop-filter: blur(16px);
    }}

    .vote-card-opt2 {{
      background: rgba(255, 255, 255, 0.04);
      border: 1.5px solid #f59e0b;
      border-radius: 20px;
      padding: 20px 22px;
      backdrop-filter: blur(16px);
    }}

    .benefit-box {{
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(16, 185, 129, 0.30);
      border-radius: 18px;
      padding: 16px 22px;
    }}

    .naver-glow {{
      box-shadow: 0 0 45px rgba(16, 185, 129, 0.55), 0 10px 30px rgba(0, 0, 0, 0.6);
    }}
  </style>
</head>
<body>

  <!-- Ambient Cinematic Background Glows -->
  <div class="absolute w-[850px] h-[850px] rounded-full bg-emerald-600/22 blur-[180px] top-1/4 left-1/2 -translate-x-1/2 pointer-events-none"></div>

  <!-- 1. Top Header Bar -->
  <div class="flex justify-between items-center z-10 w-full px-2">
    <!-- Brand Badge -->
    <div class="inline-flex items-center gap-3 bg-slate-900/90 backdrop-blur-md border border-white/20 rounded-full py-2.5 px-5 shadow-xl">
      <span class="text-base">🛡️</span>
      <span class="text-base font-black tracking-wider text-white">{self.BRAND_NAME}</span>
      <span class="text-xs font-bold text-emerald-300 pl-3 border-l border-white/25">{self.BRAND_SUB}</span>
    </div>

    <!-- Page Index -->
    <div class="text-amber-400 font-extrabold text-sm bg-slate-900/90 backdrop-blur-md px-5 py-2.5 rounded-full border border-amber-500/40 shadow-xl tracking-wider">
      05 / 05 &gt;
    </div>
  </div>

  <!-- 2. Main Content Container -->
  <div class="flex flex-col items-center text-center z-10 space-y-7 my-auto px-2">
    
    <!-- Editorial Brand Subtitle -->
    <p class="text-[13px] tracking-[0.35em] text-[#34D399] font-black uppercase">
      — I N S U R E R E B A L A N C E —
    </p>

    <!-- Main Question & Debate Glass Box -->
    <div class="glass-box w-full max-w-[960px] text-left">
      
      <!-- Mini Category Badge -->
      <div class="flex items-center justify-between mb-4">
        <div class="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-purple-500/20 border border-purple-400/40 text-purple-300 text-xs font-black">
          <span>{debate_badge}</span>
        </div>
        <span class="text-sm font-bold text-slate-300 flex items-center gap-1.5">
          <span>{s5_copy.get('theme_name', '보험 핫이슈')}</span>
          <span>💬</span>
        </span>
      </div>

      <!-- Main Headline -->
      <h1 class="text-[26px] font-black leading-[1.35] tracking-tight text-white mb-5">
        {debate_question}
      </h1>

      <!-- 2 Options Vote Cards -->
      <div class="grid grid-cols-2 gap-4 mt-4">
        
        <!-- Option 1 -->
        <div class="vote-card-opt1">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-black text-purple-300 tracking-wider">OPTION 1</span>
            <span class="text-xs font-black text-purple-300">{opt1_rate}</span>
          </div>
          <p class="text-[17px] font-black text-white leading-snug flex items-center gap-1.5">
            <span>{opt1_title}</span>
          </p>
          <p class="text-xs text-slate-400 mt-1.5 leading-relaxed font-medium">
            {opt1_sub}
          </p>
        </div>

        <!-- Option 2 -->
        <div class="vote-card-opt2">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-black text-amber-400 tracking-wider">OPTION 2</span>
            <span class="text-xs font-bold text-slate-400">{opt2_rate}</span>
          </div>
          <p class="text-[17px] font-black text-white leading-snug flex items-center gap-1.5">
            <span>{opt2_title}</span>
          </p>
          <p class="text-xs text-slate-400 mt-1.5 leading-relaxed font-medium">
            {opt2_sub}
          </p>
        </div>

      </div>

      <!-- Member Benefit Box -->
      <div class="benefit-box mt-5 text-left">
        <p class="text-xs font-black text-purple-300 flex items-center gap-1.5 mb-2.5">
          <span>🎁</span>
          <span>지금 보험 리밸런스 무료 조회 시 즉시 확인 가능한 안심 혜택:</span>
        </p>
        <div class="grid grid-cols-3 gap-2 text-xs font-bold text-slate-200">
          <div class="flex items-center gap-1.5">
            <span class="text-purple-400 font-black">✔</span>
            <span>{benefits[0]}</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="text-purple-400 font-black">✔</span>
            <span>{benefits[1]}</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="text-purple-400 font-black">✔</span>
            <span>{benefits[2]}</span>
          </div>
        </div>
      </div>

    </div>

    <!-- 3. Glow Naver Search Bar (Official Mandatory Keyword: '보험 리밸런스') -->
    <div class="w-full max-w-[960px] flex flex-col items-center space-y-2.5">
      <div class="w-full bg-white rounded-3xl p-4 px-6 flex items-center justify-between naver-glow border-2 border-[#03C75A]">
        <!-- Naver N Logo -->
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-2xl bg-[#03C75A] flex items-center justify-center font-black text-white text-2xl shadow-md">
            N
          </div>
          <div class="text-left">
            <p class="text-[11px] font-bold text-slate-500">네이버 검색창에 입력하세요</p>
            <p class="text-[25px] font-black text-slate-900 tracking-tight">{self.OFFICIAL_SEARCH}</p>
          </div>
        </div>

        <!-- Search Button -->
        <div class="bg-[#03C75A] text-white font-black text-lg px-7 py-3 rounded-2xl flex items-center gap-2 shadow-lg">
          <span>검색</span>
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
        </div>
      </div>
      
      <!-- Sub CTA text -->
      <p class="text-xs text-slate-300 font-bold tracking-wide pt-0.5">
        ✨ 스팸 전화 0건 • 지금 조회하고 내 통장에서 매달 새는 보험료 막기
      </p>
    </div>

  </div>

  <!-- 4. Bottom Footer (Official Landing URL & Copyright) -->
  <div class="flex justify-between items-center z-10 w-full px-4 pt-2 border-t border-white/10 text-xs text-slate-400 font-medium">
    <div>
      <span class="text-slate-500">Official Web:</span>
      <span class="text-emerald-400 font-bold ml-1">{self.OFFICIAL_URL}</span>
    </div>
    <div class="text-slate-500 text-[11px]">
      © 2026 InsureBalance. All rights reserved.
    </div>
  </div>

</body>
</html>"""

        logger.info(f"🎨 [InsuranceCardnewsS5] 1080x1350 5번 슬라이드 렌더링 시작 -> {out_path.name}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
            page.set_content(html_content, wait_until="networkidle")
            page.screenshot(path=str(out_path), full_page=True)
            browser.close()

        logger.info(f"✅ [InsuranceCardnewsS5] 5번 슬라이드 렌더링 완료: {out_path}")
        return str(out_path)
