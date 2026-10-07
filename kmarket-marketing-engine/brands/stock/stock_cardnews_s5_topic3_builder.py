# -*- coding: utf-8 -*-
"""
StockCardnewsS5Topic3Builder - 🏆 [StockMaster AI 주식 3번 주제: 5번 공식 CTA 엔딩 카드 전문 빌더]
================================================================================================
• 역할:
  - 3번 주제(뇌동매매 방지 AI 리스크가드) 찬반 토론:
    • OPTION 1(74% 대세, 민트): '기계적 손절 & AI 리스크 원칙 매매'
    • OPTION 2(26%, 골드): '급등주 감각 추격 매수 & 존버'
  - 3대 혜택 박스 (VETO 과열 배제 / 기계적 손절 라인 / 350개 우량주 4대 모달 무료)
  - 네이버 검색창: 초록 N 큐브 로고 + 공식 검색어 '스톡마스터 AI' + 초록 '검색 🔍' 버튼
  - 상단 프로필 링크 유도 골드 바
  - 1080x1350 초고화질 서브픽셀 렌더링
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

logger = logging.getLogger("StockCardnewsS5Topic3Builder")


class StockCardnewsS5Topic3Builder:
    """🏆 StockMaster AI 3번 주제 5번 공식 CTA 엔딩 카드뉴스 빌더 (1080x1350)"""

    BRAND_NAME = "StockMaster AI"
    OFFICIAL_KEYWORD = "스톡마스터 AI"
    OFFICIAL_URL = "https://stockmaster-ai.vercel.app/"

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent

    def render_slide(self, output_png_path: str, copy_data: Dict[str, Any] = None) -> str:
        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        opt1_title = "AI 리스크 원칙 & 조정 대기 매매"
        opt1_sub = "감정 배제 100%! 손실 원천 차단"
        opt1_pct = "74%"

        opt2_title = "1위 주도주 단기 추격 매수"
        opt2_sub = "단기 급등 기대 & 감각 매매"
        opt2_pct = "26%"

        benefit_title = "🎁 지금 스톡마스터 AI 무료 조회 시 0.1초 만에 확인 가능한 혜택:"
        benefits = [
            "1️⃣ 국내 350개 우량주 실시간 시장 스트레스 & 리스크 행동 지침",
            "2️⃣ 10분 계량 전광판 1위 주도주 및 VETO 과열 배제 종목 1초 필터",
            "3️⃣ 3대 주체별 실시간 수급 & 체결강도 4대 모달 무제한 무료 조회"
        ]

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Stock Master Topic 3 Slide 5 CTA (1080x1350)</title>
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
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
      background: #070B14;
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 44px 48px;
      color: #fff;
    }}
    .glow-gold {{
      box-shadow: 0 0 35px rgba(245, 158, 11, 0.25);
    }}
    .glow-mint {{
      box-shadow: 0 0 35px rgba(16, 185, 129, 0.25);
    }}
    .naver-green {{
      background-color: #03C75A;
    }}
  </style>
</head>
<body class="bg-gradient-to-b from-[#0A101D] via-[#070B14] to-[#04060B]">

  <!-- Top Header Section -->
  <div class="flex flex-col items-center text-center">
    <div class="text-[#FBBF24] text-xs font-black tracking-[0.3em] uppercase mb-1">
      — S T O C K M A S T E R &nbsp;&nbsp; A I —
    </div>
    <h2 class="text-white text-xl font-bold tracking-tight text-white/80">
      📈 실시간 AI 리스크 센터 &amp; 퀀트 분석기
    </h2>
    <div class="w-16 h-0.5 bg-gradient-to-r from-transparent via-[#F59E0B] to-transparent mt-2"></div>
  </div>

  <!-- Middle Main Content (Debate + Benefits) -->
  <div class="flex flex-col gap-4 my-auto">

    <!-- Debate Card 1 (Mint Option) -->
    <div class="w-full p-5 rounded-2xl bg-gradient-to-r from-emerald-950/40 via-emerald-900/20 to-black/40 border border-emerald-500/40 glow-mint flex items-center justify-between">
      <div class="flex flex-col gap-1">
        <div class="inline-flex items-center gap-2">
          <span class="px-2.5 py-0.5 rounded-full bg-emerald-500 text-black text-xs font-black">OPTION 1</span>
          <span class="text-emerald-400 text-xs font-bold tracking-tight">74% 투자자의 선택</span>
        </div>
        <h3 class="text-white text-2xl font-black tracking-tight mt-1">{opt1_title}</h3>
        <p class="text-emerald-200/70 text-sm font-medium">{opt1_sub}</p>
      </div>
      <div class="flex flex-col items-end justify-center pl-4">
        <span class="text-4xl font-black text-emerald-400">{opt1_pct}</span>
        <span class="text-emerald-500/80 text-xs font-bold">압도적 대세</span>
      </div>
    </div>

    <!-- VS Divider Badge -->
    <div class="flex items-center justify-center -my-2 z-10">
      <span class="px-4 py-1 rounded-full bg-[#1E293B] border border-white/20 text-[#FBBF24] text-xs font-black tracking-wider shadow-lg">
        VS 실전 매매 토론
      </span>
    </div>

    <!-- Debate Card 2 (Gold Option) -->
    <div class="w-full p-5 rounded-2xl bg-gradient-to-r from-amber-950/30 via-amber-900/10 to-black/40 border border-[#F59E0B]/30 glow-gold flex items-center justify-between opacity-85">
      <div class="flex flex-col gap-1">
        <div class="inline-flex items-center gap-2">
          <span class="px-2.5 py-0.5 rounded-full bg-[#F59E0B] text-black text-xs font-black">OPTION 2</span>
          <span class="text-[#FBBF24] text-xs font-bold tracking-tight">26% 투자자</span>
        </div>
        <h3 class="text-white text-2xl font-black tracking-tight mt-1">{opt2_title}</h3>
        <p class="text-amber-200/70 text-sm font-medium">{opt2_sub}</p>
      </div>
      <div class="flex flex-col items-end justify-center pl-4">
        <span class="text-4xl font-black text-[#FBBF24]">{opt2_pct}</span>
        <span class="text-[#F59E0B]/80 text-xs font-bold">감정 매매</span>
      </div>
    </div>

    <!-- 3 Core Benefits Card -->
    <div class="w-full p-5 rounded-2xl bg-white/[0.03] border border-white/10 backdrop-blur-md flex flex-col gap-2.5 mt-1">
      <h4 class="text-[#FBBF24] text-sm font-black tracking-tight flex items-center gap-1.5">
        {benefit_title}
      </h4>
      <div class="flex flex-col gap-1.5 text-white/90 text-sm font-semibold leading-relaxed">
        <div class="flex items-center gap-2">
          <span class="text-[#38BDF8]">•</span>
          <span>{benefits[0]}</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-[#38BDF8]">•</span>
          <span>{benefits[1]}</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-[#38BDF8]">•</span>
          <span>{benefits[2]}</span>
        </div>
      </div>
    </div>

  </div>

  <!-- Bottom CTA & Naver Search Section -->
  <div class="flex flex-col gap-3">

    <!-- Official Naver Search Bar -->
    <div class="w-full p-3.5 rounded-2xl bg-[#03C75A]/10 border border-[#03C75A]/50 flex items-center justify-between px-5 shadow-lg shadow-green-500/10">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-lg naver-green flex items-center justify-center font-black text-white text-xl shadow-md">
          N
        </div>
        <div class="flex flex-col">
          <span class="text-white/60 text-xs font-bold">네이버 검색창에 입력하세요</span>
          <span class="text-white text-2xl font-black tracking-tight">{self.OFFICIAL_KEYWORD}</span>
        </div>
      </div>
      <div class="px-5 py-2 rounded-xl naver-green text-white text-base font-black flex items-center gap-1.5 shadow-md">
        <span>검색</span>
        <span class="text-sm">🔍</span>
      </div>
    </div>

    <!-- Profile Link Induction Bar -->
    <div class="w-full py-3.5 rounded-xl bg-gradient-to-r from-[#EA580C] via-[#F97316] to-[#F59E0B] shadow-lg shadow-orange-500/20 flex items-center justify-center border border-white/20">
      <span class="text-white text-base font-black tracking-wide flex items-center gap-2">
        👉 상단 프로필 링크 클릭 시 0.1초 만에 퀀트 데이터 무료 조회!
      </span>
    </div>

    <!-- Footer Copyright -->
    <div class="flex justify-between items-center px-2 pt-1 text-white/40 text-[11px]">
      <span>Official Web: {self.OFFICIAL_URL}</span>
      <span>© 2026 StockMaster AI. All rights reserved.</span>
    </div>

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

        logger.info(f"🎉 [StockCardnewsS5Topic3Builder] 3번 주제 5번 CTA 슬라이드 렌더링 완료: {out_path}")
        return str(out_path)


if __name__ == "__main__":
    builder = StockCardnewsS5Topic3Builder()
    out = Path(r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\주식\[주제03] 뇌동매매방지_리스크가드_20대여성기자\slide_5.png")
    builder.render_slide(str(out))
    print(f"🎉 5번 CTA 슬라이드 렌더링 완료: {out}")
