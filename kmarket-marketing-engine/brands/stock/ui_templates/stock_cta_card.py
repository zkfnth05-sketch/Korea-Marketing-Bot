# -*- coding: utf-8 -*-
"""
StockCTACard - 🏷️ [StockMaster AI 숏폼 엔딩 댓글 찬반 토론 및 네이버 공식 검색 CTA 카드]
========================================================================================
- 1080x1920 세로 풀HD 규격
- 카드뉴스 5번 슬라이드와 100% 동일한 프리미엄 다크 네이비 글래스모피즘 룩
- 공식 검색어: [스톡마스터 AI] (띄어쓰기 100% 필수)
- Playwright Chromium 초고화질 서브픽셀 렌더링 + FFmpeg 무손실 MP4 인코딩
"""

import os
import sys
import shutil
import tempfile
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from playwright.sync_api import sync_playwright
import imageio_ffmpeg

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("StockCTACard")


class StockCTACard:
    """📈 StockMaster AI 숏폼 엔딩 공식 검색어 CTA 비디오 생성기 (1080x1920)"""

    BRAND_NAME = "StockMaster AI"
    BRAND_SUB = "외인·기관 실시간 수급 포착"
    OFFICIAL_SEARCH = "스톡마스터 AI"
    OFFICIAL_URL = "stockmaster-ai.vercel.app"

    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.w = 1080
        self.h = 1920

    def generate_html_template(
        self,
        topic_title: str = "삼성전자 vs SK하이닉스 AI 반도체 HBM 수급",
        debate_question: str = "외인·기관 쌍끌이 순매수 종목, 눌림목 매수다 vs 추세 돌파 매수다?",
        search_keyword: str = "스톡마스터 AI",
        hero_copy: str = "실시간 AI 퀀트 수급 분석!",
        opt1_title: str = "눌림목 분할 매수",
        opt1_desc: str = "수급 유입 확인 후 지지선 눌림목에서 분할로 안전하게 진입한다",
        opt1_rate: str = "71% (대세)",
        opt2_title: str = "추세 돌파 불타기",
        opt2_desc: str = "강한 거래량과 전고점 돌파 확인 즉시 비중을 싣는다",
        opt2_rate: str = "29%",
        benefit_items: Optional[list] = None
    ) -> str:
        """1080x1920 숏폼 규격 프리미엄 핀테크 에디토리얼 엔딩 HTML 생성"""
        if not benefit_items:
            benefit_items = [
                "장중 실시간 외인·기관 쌍끌이 수급 포착",
                "4대 퀀트 팩터 기반 종합 스코어카드 진단",
                "회원가입/설치 제로 100% 브라우저 즉시 조회"
            ]

        return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>StockMaster AI Shorts Ending Debate CTA (1080x1920)</title>
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
      height: 1920px;
      overflow: hidden;
      background: radial-gradient(circle at 50% 25%, #0f172a 0%, #090e1a 50%, #020617 100%);
      color: #fff;
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 60px 48px 50px;
    }}

    .gold-divider {{
      height: 1.5px;
      background: linear-gradient(90deg, rgba(245, 158, 11, 0) 0%, rgba(245, 158, 11, 0.85) 50%, rgba(245, 158, 11, 0) 100%);
    }}

    .glass-box {{
      background: rgba(15, 23, 42, 0.90);
      backdrop-filter: blur(32px);
      -webkit-backdrop-filter: blur(32px);
      border: 1.5px solid rgba(245, 158, 11, 0.45);
      box-shadow: 0 25px 70px rgba(0, 0, 0, 0.9), 0 0 50px rgba(245, 158, 11, 0.22);
    }}

    .vote-card {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.14);
      backdrop-filter: blur(18px);
    }}

    .benefit-box {{
      background: linear-gradient(135deg, rgba(37, 99, 235, 0.14) 0%, rgba(245, 158, 11, 0.10) 100%);
      border: 1px solid rgba(245, 158, 11, 0.40);
    }}

    .naver-glow {{
      box-shadow: 0 15px 50px rgba(3, 199, 90, 0.45), 0 0 40px rgba(245, 158, 11, 0.35);
    }}
  </style>
</head>
<body>

  <!-- Ambient Glows -->
  <div class="absolute w-[950px] h-[950px] rounded-full bg-blue-500/10 blur-[180px] top-10 left-1/2 -translate-x-1/2 pointer-events-none"></div>
  <div class="absolute w-[800px] h-[800px] rounded-full bg-amber-500/10 blur-[160px] bottom-20 right-10 pointer-events-none"></div>

  <!-- 1. Top Brand Header Bar - Removed for clean single capsule badge overlay -->
  <!-- Top spacing anchor for single fixed capsule badge -->
  <div class="h-20 w-full"></div>

  <!-- 2. Main Content Container (Safe Zone Centered) -->
  <div class="flex flex-col items-center text-center z-10 space-y-7 my-auto px-2 w-full">
    
    <!-- Editorial Brand Subtitle -->
    <div class="flex flex-col items-center space-y-2">
      <div class="gold-divider w-96"></div>
      <p class="text-xs tracking-[0.4em] text-amber-400 font-bold uppercase py-1">
        — S T O C K M A S T E R   A I   Q U A N T —
      </p>
      <div class="gold-divider w-96"></div>
    </div>

    <!-- Main Question & Debate Glass Box -->
    <div class="glass-box rounded-[32px] p-8 w-full max-w-[980px] text-left space-y-6">
      
      <!-- Mini Category Badge -->
      <div class="flex items-center justify-between">
        <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-500/20 border border-amber-400/40 text-amber-300 text-sm font-black">
          <span>📈 ⚡</span>
          <span>주식AI 수급 찬반 토론</span>
        </div>
        <span class="text-sm text-amber-300 font-bold">투자자 참여 1위 🔥</span>
      </div>

      <!-- Main Headline Question -->
      <h1 class="text-3xl font-black leading-snug tracking-tight text-white">
        "{debate_question}"
      </h1>

      <!-- 2 Options Vote Cards -->
      <div class="grid grid-cols-2 gap-4 pt-2">
        
        <!-- Option 1 -->
        <div class="vote-card rounded-2xl p-5 border-l-4 border-l-emerald-400 bg-emerald-500/10 border-emerald-400/30 space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-black text-emerald-300">OPTION 1</span>
            <span class="text-xs font-black text-emerald-300">{opt1_rate}</span>
          </div>
          <p class="text-base font-black text-white leading-snug">
            "{opt1_title}"
          </p>
          <p class="text-xs text-slate-300 leading-relaxed">
            {opt1_desc}
          </p>
        </div>

        <!-- Option 2 -->
        <div class="vote-card rounded-2xl p-5 border-l-4 border-l-blue-400 bg-blue-500/10 border-blue-400/30 space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-black text-blue-300">OPTION 2</span>
            <span class="text-xs font-bold text-slate-400">{opt2_rate}</span>
          </div>
          <p class="text-base font-black text-white leading-snug">
            "{opt2_title}"
          </p>
          <p class="text-xs text-slate-300 leading-relaxed">
            {opt2_desc}
          </p>
        </div>

      </div>

      <!-- Member Benefit Box -->
      <div class="benefit-box rounded-2xl p-4.5 text-left">
        <p class="text-xs font-black text-amber-300 flex items-center gap-2 mb-2">
          <span>🎁</span>
          <span>지금 StockMaster AI 무료 접속 시 즉시 제공 혜택:</span>
        </p>
        <div class="grid grid-cols-3 gap-3 text-xs font-bold text-slate-200">
          <div class="flex items-center gap-1.5">
            <span class="text-amber-400 font-black">✔</span>
            <span>{benefit_items[0]}</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="text-amber-400 font-black">✔</span>
            <span>{benefit_items[1]}</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="text-amber-400 font-black">✔</span>
            <span>{benefit_items[2]}</span>
          </div>
        </div>
      </div>

    </div>

    <!-- 3. Glow Naver Search Bar (The Core CTA) -->
    <div class="w-full max-w-[980px] flex flex-col items-center space-y-3 pt-2">
      <div class="w-full bg-white rounded-2xl p-4.5 flex items-center justify-between naver-glow border-2 border-[#03C75A]">
        <!-- Naver N Logo & Keyword -->
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-[#03C75A] flex items-center justify-center font-black text-white text-2xl shadow-md">
            N
          </div>
          <div class="text-left">
            <p class="text-xs font-bold text-slate-500">네이버 검색창에 입력하세요</p>
            <p class="text-3xl font-black text-slate-900 tracking-tight">{search_keyword}</p>
          </div>
        </div>

        <!-- Search Button with Magnifier -->
        <div class="bg-[#03C75A] text-white font-black text-lg px-8 py-3.5 rounded-xl flex items-center gap-2 shadow-lg">
          <span>검색</span>
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
        </div>
      </div>
      
      <!-- Sub CTA text -->
      <p class="text-sm text-amber-300 font-bold tracking-wide pt-1">
        👉 네이버에 '스톡마스터 AI'를 검색하고 장중 수급 레이더를 무료로 확인하세요!
      </p>
    </div>

  </div>

  <!-- 4. Bottom Footer (Official Landing URL & Copyright) -->
  <div class="flex justify-between items-center z-10 w-full px-6 pt-3 border-t border-white/10 text-xs text-slate-400 font-medium">
    <div>
      <span class="text-slate-500">Official Web:</span>
      <span class="text-amber-400 font-bold ml-1">https://stockmaster-ai.vercel.app/</span>
    </div>
    <div class="text-slate-500 text-xs">
      © 2026 StockMaster AI. All rights reserved.
    </div>
  </div>

</body>
</html>
"""

    def render_cta_frame_image(
        self,
        output_png_path: str,
        topic_title: str = "삼성전자 vs SK하이닉스 AI 반도체 HBM 수급",
        debate_question: str = "외인·기관 쌍끌이 순매수 종목, 눌림목 매수다 vs 추세 돌파 매수다?",
        search_keyword: str = "스톡마스터 AI",
        hero_copy: str = "실시간 AI 퀀트 수급 분석!",
        **kwargs
    ) -> str:
        """Playwright를 활용한 1080x1920 다크 핀테크 글래스모피즘 CTA 단일 프레임 렌더링"""
        out_p = Path(output_png_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        html_content = self.generate_html_template(
            topic_title=topic_title,
            debate_question=debate_question,
            search_keyword=search_keyword,
            hero_copy=hero_copy,
            **kwargs
        )

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1920})
            page.set_content(html_content, wait_until="networkidle")
            page.screenshot(path=str(out_p), type="png")
            browser.close()

        logger.info(f"✨ [StockCTACard] 다크 핀테크 글래스모피즘 CTA 프레임 렌더링 완료: {out_p}")
        return str(out_p)

    def render_cta_image(
        self,
        topic_title: str = "삼성전자 vs SK하이닉스 AI 반도체 HBM 수급",
        debate_question: str = "외인·기관 쌍끌이 순매수 종목, 눌림목 매수다 vs 추세 돌파 매수다?",
        search_keyword: str = "스톡마스터 AI",
        hero_copy: str = "실시간 AI 퀀트 수급 분석!",
        **kwargs
    ):
        """PIL Image 객체로 반환하는 래퍼 메서드"""
        from PIL import Image
        temp_dir = Path(tempfile.mkdtemp(prefix="stock_cta_pil_"))
        temp_png = temp_dir / "stock_cta_frame.png"
        try:
            self.render_cta_frame_image(
                output_png_path=str(temp_png),
                topic_title=topic_title,
                debate_question=debate_question,
                search_keyword=search_keyword,
                hero_copy=hero_copy,
                **kwargs
            )
            return Image.open(str(temp_png)).convert("RGB")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def create_cta_segment_mp4(
        self,
        output_path: str,
        duration_sec: float = 1.0,
        fps: int = 30,
        topic_title: str = "삼성전자 vs SK하이닉스 AI 반도체 HBM 수급",
        debate_question: str = "외인·기관 쌍끌이 순매수 종목, 눌림목 매수다 vs 추세 돌파 매수다?",
        search_keyword: str = "스톡마스터 AI",
        hero_copy: str = "실시간 AI 퀀트 수급 분석!",
        **kwargs
    ) -> str:
        """초고화질 다크 핀테크 글래스모피즘 CTA 세그먼트 MP4 초고속 생성"""
        out_p = Path(output_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        temp_dir = Path(tempfile.mkdtemp(prefix="stock_cta_mp4_"))
        try:
            # 1. 고화질 스틸 프레임 1장 생성
            still_png = temp_dir / "stock_cta_frame.png"
            self.render_cta_frame_image(
                output_png_path=str(still_png),
                topic_title=topic_title,
                debate_question=debate_question,
                search_keyword=search_keyword,
                hero_copy=hero_copy,
                **kwargs
            )

            # 2. FFmpeg 무손실 비디오 변환
            cmd = [
                self.ffmpeg_exe, "-y",
                "-loop", "1",
                "-i", str(still_png),
                "-c:v", "libx264",
                "-tune", "stillimage",
                "-pix_fmt", "yuv420p",
                "-t", str(duration_sec),
                "-r", str(fps),
                str(out_p)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            logger.info(f"✨ [StockCTACard] 다크 핀테크 CTA 비디오 생성 완료 ({duration_sec}s): {out_p.name}")
            return str(out_p)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
