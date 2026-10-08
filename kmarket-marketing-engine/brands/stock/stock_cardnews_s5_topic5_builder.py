# -*- coding: utf-8 -*-
"""
StockCardnewsS5Topic5Builder - 🏷️ [StockMaster AI 주식 5번 주제 5번: 공식 핫이슈 찬반 토론 & 네이버 검색 CTA 카드 빌더]
=============================================================================================================
• 역할:
  - 주식 5번 주제 5번 엔딩을 1080x1350 카드뉴스 공식 규격으로 100% 렌더링
  - 핫이슈 찬반 토론 글래스 박스 (OPTION 1 민트 & OPTION 2 골드) + 3대 혜택 박스
  - 네이버 공식 검색창 캡슐 (초록 N 큐브 로고 + '스톡마스터 AI' + 검색 버튼)
  - 상단 프로필 링크 유도 골드 바 + 공식 푸터 일체형
  - 산출물: Desktop/한국 카드뉴스_산출물/주식/[주제05] KOSPI_시장종합스트레스_4대매크로리포트/slide_5.png
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
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

logger = logging.getLogger("StockCardnewsS5Topic5Builder")


class StockCardnewsS5Topic5Builder:
    """📈 StockMaster AI 5번 주제 5번 엔딩 찬반 토론 & 네이버 검색 CTA 카드 공식 규격 빌더"""

    BRAND_NAME = "StockMaster AI"
    BRAND_SUB = "외인·기관 실시간 수급 퀀트"
    OFFICIAL_SEARCH = "스톡마스터 AI"
    OFFICIAL_URL = "https://stockmaster-ai.vercel.app/"

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent

    def render_slide(self, output_png_path: str, copy_data: Dict[str, Any] = None) -> str:
        """1080x1350 규격 럭셔리 5번 엔딩 공식 CTA 카드뉴스 렌더링"""
        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        s5_copy = copy_data or {}
        debate_badge = s5_copy.get("debate_badge", "실시간 주도주 찬반 토론")
        debate_question = s5_copy.get("debate_question", "시장 스트레스 55점 경계 국면! 지금 구간 현금 비중 확대 vs 1위 주도주 분할 매수?")
        
        opt1_title = s5_copy.get("debate_opt1_title", "🛡️ 현금 비중 확대")
        opt1_sub = s5_copy.get("debate_opt1_sub", "환율 상승 & 지표 불균형 감지! 분할 매수 20% 축소하고 리스크 방어")
        opt1_rate = s5_copy.get("debate_opt1_rate", "68% (대세)")

        opt2_title = s5_copy.get("debate_opt2_title", "🚀 1위 주도주 분할 매수")
        opt2_sub = s5_copy.get("debate_opt2_sub", "외인·기관 쌍끌이 90점 종목(LG엔솔) 수급 변곡점 적극 공략")
        opt2_rate = s5_copy.get("debate_opt2_rate", "32%")

        default_benefits = [
            "전종목 10분 주기 실시간 계량 점수",
            "감정 0% 기계적 AI 리스크가드",
            "거래대금 상위 1% 수급 쏠림 추적"
        ]
        benefits = s5_copy.get("benefit_items", default_benefits)
        while len(benefits) < 3:
            benefits.append("스톡마스터 AI 100% 무료 퀀트")

        cta_subtext = s5_copy.get("cta_subtext", "네이버에서 '스톡마스터 AI' 검색 • StockMaster AI 100% 무료 진단")

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Stock Master Topic 5 S5 Ending Debate & Naver Search CTA (1080x1350)</title>
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
      background: radial-gradient(circle at 50% 25%, #0d1527 0%, #070b14 55%, #03050a 100%);
      color: #fff;
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 38px 48px 40px;
    }}

    /* 글래스 박스 및 글로우 (Dark Navy & Amber Gold) */
    .glass-box {{
      background: rgba(15, 23, 42, 0.88);
      backdrop-filter: blur(28px);
      -webkit-backdrop-filter: blur(28px);
      border: 1.5px solid rgba(245, 158, 11, 0.40);
      border-radius: 28px;
      padding: 32px 36px;
      box-shadow: 0 0 50px rgba(245, 158, 11, 0.20), 0 25px 60px rgba(0, 0, 0, 0.9);
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
      border: 1px solid rgba(245, 158, 11, 0.30);
      border-radius: 18px;
      padding: 16px 22px;
    }}

    .naver-glow {{
      box-shadow: 0 0 45px rgba(0, 199, 60, 0.50), 0 10px 30px rgba(0, 0, 0, 0.6);
    }}
  </style>
</head>
<body>

  <!-- Ambient Cinematic Background Glows -->
  <div class="absolute w-[850px] h-[850px] rounded-full bg-amber-500/18 blur-[180px] top-1/4 left-1/2 -translate-x-1/2 pointer-events-none"></div>

  <!-- 1. Top Header Bar -->
  <div class="flex justify-between items-center z-10 w-full px-2">
    <!-- Brand Badge -->
    <div class="inline-flex items-center gap-3 bg-slate-900/90 backdrop-blur-md border border-white/20 rounded-full py-2.5 px-5 shadow-xl">
      <span class="text-base">📈</span>
      <span class="text-base font-black tracking-wider text-white">{self.BRAND_NAME}</span>
      <span class="text-xs font-bold text-amber-300 pl-3 border-l border-white/25">{self.BRAND_SUB}</span>
    </div>

    <!-- Page Index -->
    <div class="text-amber-400 font-extrabold text-sm bg-slate-900/90 backdrop-blur-md px-5 py-2.5 rounded-full border border-amber-500/40 shadow-xl tracking-wider">
      05 / 05 &gt;
    </div>
  </div>

  <!-- 2. Main Content Container -->
  <div class="flex flex-col items-center text-center z-10 space-y-6 my-auto px-2">
    
    <!-- Editorial Brand Subtitle -->
    <p class="text-[13px] tracking-[0.35em] text-[#FBBF24] font-black uppercase">
      — S T O C K M A S T E R   A I —
    </p>

    <!-- Main Question & Debate Glass Box -->
    <div class="glass-box w-full max-w-[960px] text-left">
      
      <!-- Mini Category Badge -->
      <div class="flex items-center justify-between mb-4">
        <div class="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-amber-500/20 border border-amber-400/40 text-amber-300 text-xs font-black">
          <span>🔥 {debate_badge}</span>
        </div>
        <span class="text-sm font-bold text-slate-300 flex items-center gap-1.5">
          <span>국내 주식 핫이슈</span>
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
            <span class="text-xs font-black text-emerald-300 tracking-wider">OPTION 1</span>
            <span class="text-xs font-black text-emerald-300">{opt1_rate}</span>
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
        <p class="text-xs font-black text-amber-300 flex items-center gap-1.5 mb-2.5">
          <span>🎁</span>
          <span>지금 스톡마스터 AI 무료 조회 시 0.1초 만에 확인 가능한 혜택:</span>
        </p>
        <div class="grid grid-cols-3 gap-2 text-xs font-bold text-slate-200">
          <div class="flex items-center gap-1.5">
            <span class="text-amber-400 font-black">✔</span>
            <span>{benefits[0]}</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="text-amber-400 font-black">✔</span>
            <span>{benefits[1]}</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="text-amber-400 font-black">✔</span>
            <span>{benefits[2]}</span>
          </div>
        </div>
      </div>

    </div>

    <!-- 3. Glow Naver Search Bar (Official Mandatory Keyword: '스톡마스터 AI') -->
    <div class="w-full max-w-[960px] flex flex-col items-center space-y-2.5">
      <div class="w-full bg-white rounded-3xl p-4 px-6 flex items-center justify-between naver-glow border-2 border-[#00C73C]">
        <!-- Naver N Logo -->
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-2xl bg-[#00C73C] flex items-center justify-center font-black text-white text-2xl shadow-md">
            N
          </div>
          <div class="text-left">
            <p class="text-[11px] font-bold text-slate-500">네이버 검색창에 입력하세요</p>
            <p class="text-[25px] font-black text-slate-900 tracking-tight">{self.OFFICIAL_SEARCH}</p>
          </div>
        </div>

        <!-- Search Button -->
        <div class="bg-[#00C73C] text-white font-black text-lg px-7 py-3 rounded-2xl flex items-center gap-2 shadow-lg">
          <span>검색</span>
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
        </div>
      </div>
      
      <!-- Sub CTA text -->
      <div class="w-full bg-amber-500/20 border border-amber-400/50 rounded-2xl py-2.5 px-4 flex items-center justify-center gap-2 shadow-lg">
        <span class="text-amber-300 text-[15px] font-black tracking-tight">👉 상단 프로필 링크 클릭 시 0.1초 만에 퀀트 데이터 무료 조회!</span>
      </div>
      <p class="text-[11px] text-slate-300 font-medium tracking-wide">
        {cta_subtext}
      </p>
    </div>

  </div>

  <!-- 4. Bottom Footer (Official Landing URL & Copyright) -->
  <div class="flex justify-between items-center z-10 w-full px-4 pt-2 border-t border-white/10 text-xs text-slate-400 font-medium">
    <div>
      <span class="text-slate-500">Official Web:</span>
      <span class="text-amber-400 font-bold ml-1">{self.OFFICIAL_URL}</span>
    </div>
    <div class="text-slate-500 text-[11px]">
      © 2026 StockMaster AI. All rights reserved.
    </div>
  </div>

</body>
</html>"""

        logger.info(f"🎨 [StockCardnewsS5Topic5] 1080x1350 5번 슬라이드 렌더링 시작 -> {out_path.name}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
            page.set_content(html_content, wait_until="networkidle")
            page.screenshot(path=str(out_path), full_page=True)
            browser.close()

        logger.info(f"✅ [StockCardnewsS5Topic5] 5번 슬라이드 렌더링 완료: {out_path}")
        return str(out_path)


if __name__ == "__main__":
    builder = StockCardnewsS5Topic5Builder()
    out = Path(r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\주식\[주제05] KOSPI_시장종합스트레스_4대매크로리포트\slide_5.png")
    builder.render_slide(str(out))
    print(f"🎉 5번 슬라이드 렌더링 완료: {out}")
