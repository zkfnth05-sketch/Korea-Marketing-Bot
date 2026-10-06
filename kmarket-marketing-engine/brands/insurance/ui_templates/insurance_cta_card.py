# -*- coding: utf-8 -*-
"""
InsuranceCTACard - 🏷️ [보험 리밸런스 숏폼 엔딩 다크 에메랄드 그린 글래스모피즘 럭셔리 CTA 카드]
========================================================================================
- 1080x1920 세로 풀HD 규격
- 카드뉴스 5번 CTA와 100% 동일한 럭셔리 글래스모피즘 & 엠비언트 글로우 디자인 룩 이식
- ⚡ 88% vs 12% 찬반 토론 배틀 (시청자 댓글 참여 유도 극대화)
- 🛡️ 3대 안심 혜택 (34개사 실시간 비교 / PII-Free / 0.1초 자가진단)
- 🔍 네이버 공식 규격 검색창 ['보험 리밸런스' (띄어쓰기 100% 필수)]
- Playwright 1080x1920 초고화질 서브픽셀 렌더링 & ffmpeg 초고속 무손실 MP4 인코딩
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

logger = logging.getLogger("InsuranceCTACard")


class InsuranceCTACard:
    """🛡️ 보험 리밸런스 숏폼 엔딩 다크 에메랄드 글래스모피즘 CTA 비디오 생성기 (1080x1920)"""

    BRAND_NAME = "보험 리밸런스"
    BRAND_SUB = "34개사 실시간 비교"
    OFFICIAL_SEARCH = "보험 리밸런스"
    OFFICIAL_URL = "insure-rebalance.vercel.app"

    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.w = 1080
        self.h = 1920

    def render_cta_frame_image(
        self,
        output_png_path: str,
        topic_title: str = "내 보험 정밀 비교 & 새는 보험료 다이어트",
        debate_question: str = "보험 리모델링 시, 설계사 권유 가입 vs 34개사 AI 비교?",
        search_keyword: str = "보험 리밸런스",
        hero_copy: str = "내가 내는 보험료 그대로 보장 최대 업그레이드!",
        debate_opt1_title: str = "🤖 34개사 AI 객관적 비교 선택",
        debate_opt1_sub: str = "동일 보험료로 보장 가장 큰 상품 자율 선택",
        debate_opt1_rate: str = "88% (대세)",
        debate_opt2_title: str = "👤 지인/설계사 추천 상품 유지",
        debate_opt2_sub: str = "기존 권유받은 패키지 그대로 유지",
        debate_opt2_rate: str = "12%",
        benefit_items: Optional[list] = None
    ) -> str:
        """Playwright를 활용한 1080x1920 다크 에메랄드 글래스모피즘 CTA 단일 프레임 렌더링"""
        out_p = Path(output_png_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        if not benefit_items:
            benefit_items = [
                "34개 보험사 객관적 시뮬레이션 비교",
                "이름·전화번호 입력 제로 (PII-Free 안심 구조)",
                "0.1초 만에 동일 보험료 대비 최대 보장 자가진단"
            ]

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Insurance Shorts Ending CTA (1080x1920)</title>
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
      height: 1920px;
      overflow: hidden;
      background: radial-gradient(circle at 50% 25%, #052e1d 0%, #02170e 50%, #010a06 100%);
      color: #fff;
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 70px 52px 65px;
    }}

    /* 글래스 박스 및 글로우 (Deep Forest & Emerald Green) */
    .glass-box {{
      background: rgba(4, 30, 20, 0.88);
      backdrop-filter: blur(28px);
      -webkit-backdrop-filter: blur(28px);
      border: 1.5px solid rgba(16, 185, 129, 0.40);
      border-radius: 32px;
      padding: 40px 44px;
      box-shadow: 0 0 60px rgba(16, 185, 129, 0.22), 0 25px 60px rgba(0, 0, 0, 0.9);
    }}

    .ambient-glow {{
      position: absolute;
      top: 15%;
      left: 50%;
      transform: translateX(-50%);
      width: 900px;
      height: 600px;
      background: radial-gradient(circle, rgba(16, 185, 129, 0.35) 0%, rgba(5, 150, 105, 0.15) 50%, rgba(0,0,0,0) 80%);
      filter: blur(80px);
      z-index: 1;
      pointer-events: none;
    }}

    .naver-green {{
      background: #03C75A;
      color: #FFFFFF;
    }}

    .naver-glow {{
      box-shadow: 0 0 45px rgba(3, 199, 90, 0.50), 0 15px 35px rgba(0, 0, 0, 0.6);
    }}

    .accent-badge {{
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.3) 0%, rgba(5, 150, 105, 0.15) 100%);
      border: 1px solid rgba(16, 185, 129, 0.6);
    }}

    .pulse-opt1 {{
      border: 2px solid #10B981;
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.25) 0%, rgba(4, 30, 20, 0.85) 100%);
      box-shadow: 0 0 30px rgba(16, 185, 129, 0.35);
    }}
  </style>
</head>
<body>

  <!-- Ambient Glow -->
  <div class="ambient-glow"></div>

  <!-- 1. Top Header - Removed for clean single capsule badge overlay -->
  <div class="h-20 w-full"></div>

  <!-- 2. Main Debate Card -->
    <div class="glass-box z-10 w-full max-w-[980px] flex flex-col gap-6 p-8 rounded-[32px] text-left">
      <!-- Debate Badge -->
      <div class="flex items-center justify-between">
        <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/20 border border-emerald-400/40 text-emerald-300 text-sm font-black">
          <span>⚡</span>
          <span>보험 리밸런스 현실 토론</span>
        </div>
        <span class="text-sm font-semibold text-emerald-300">소비자 공감 1위 🔥</span>
      </div>

      <!-- Debate Question -->
      <h2 class="text-3xl font-black text-white leading-snug tracking-tight">
        "{debate_question.strip('"').strip("'")}"
      </h2>

      <!-- Options Box -->
      <div class="grid grid-cols-2 gap-4 pt-2">
        <!-- Option 1 (Winner) -->
        <div class="vote-card rounded-2xl p-5 border-l-4 border-l-emerald-400 bg-emerald-500/10 border-emerald-400/30 space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-black text-emerald-300">OPTION 1</span>
            <span class="text-xs font-black text-emerald-300">{debate_opt1_rate}</span>
          </div>
          <p class="text-base font-black text-white leading-snug">{debate_opt1_title}</p>
          <p class="text-xs text-slate-300 leading-relaxed">{debate_opt1_sub}</p>
        </div>

        <!-- Option 2 -->
        <div class="vote-card rounded-2xl p-5 border-l-4 border-l-rose-400 bg-rose-500/10 border-rose-400/30 space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-black text-rose-300">OPTION 2</span>
            <span class="text-xs font-bold text-slate-400">{debate_opt2_rate}</span>
          </div>
          <p class="text-base font-black text-white leading-snug">{debate_opt2_title}</p>
          <p class="text-xs text-slate-300 leading-relaxed">{debate_opt2_sub}</p>
        </div>
      </div>

      <!-- Zero Cost Benefits Box (Integrated) -->
      <div class="benefit-box rounded-2xl p-4.5 text-left">
        <p class="text-xs font-black text-emerald-300 flex items-center gap-2 mb-2">
          <span>🎁</span>
          <span>지금 보험 리밸런스 무료 자가진단 시 즉시 제공 혜택:</span>
        </p>
        <div class="grid grid-cols-3 gap-3 text-xs font-bold text-slate-200">
          <div class="flex items-center gap-1.5">
            <span class="text-emerald-400 font-black">✔</span>
            <span>{benefit_items[0] if len(benefit_items) > 0 else '34개 보험사 객관적 비교'}</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="text-emerald-400 font-black">✔</span>
            <span>{benefit_items[1] if len(benefit_items) > 1 else '주민번호 0% 안심 구조'}</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="text-emerald-400 font-black">✔</span>
            <span>{benefit_items[2] if len(benefit_items) > 2 else '0.1초 숨은 보장 자가진단'}</span>
          </div>
        </div>
      </div>

    </div>


    <!-- 4. Naver Search CTA Box -->
    <div class="z-10 w-full flex flex-col items-center space-y-3 pt-2">
      <!-- Official Naver Search Bar -->
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
      <p class="text-sm text-emerald-300 font-bold tracking-wide pt-1">
        👉 네이버에 '보험 리밸런스'를 검색하고 내 보험 0.1초 자가진단을 시작하세요!
      </p>
    </div>

  </div>

  <!-- 5. Bottom Footer (Official Landing URL & Copyright) -->
  <div class="flex justify-between items-center z-10 w-full px-6 pt-3 border-t border-white/10 text-xs text-slate-400 font-medium">
    <div>
      <span class="text-slate-500">Official Web:</span>
      <span class="text-emerald-400 font-bold ml-1">https://insure-rebalance.vercel.app/</span>
    </div>
    <div class="text-slate-500 text-xs">
      © 2026 InsureBalance. All rights reserved.
    </div>
  </div>

</body>
</html>"""


        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1920})
            page.set_content(html_content, wait_until="networkidle")
            page.screenshot(path=str(out_p), type="png")
            browser.close()

        logger.info(f"✨ [InsuranceCTACard] 다크 에메랄드 글래스모피즘 CTA 프레임 렌더링 완료: {out_p}")
        return str(out_p)

    def render_cta_image(
        self,
        topic_title: str = "내 보험 정밀 비교 & 새는 보험료 다이어트",
        debate_question: str = "보험 리모델링 시, 설계사 권유 가입 vs 34개사 AI 비교?",
        search_keyword: str = "보험 리밸런스",
        hero_copy: str = "내가 내는 보험료 그대로 보장 최대 업그레이드!",
        **kwargs
    ):
        """PIL Image 객체로 반환하는 래퍼 메서드"""
        from PIL import Image
        temp_dir = Path(tempfile.mkdtemp(prefix="insure_cta_pil_"))
        temp_png = temp_dir / "insure_cta_frame.png"
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
        duration_sec: float = 2.0,
        fps: int = 30,
        topic_title: str = "내 보험 정밀 비교 & 새는 보험료 다이어트",
        debate_question: str = "보험 리모델링 시, 설계사 권유 가입 vs 34개사 AI 비교?",
        search_keyword: str = "보험 리밸런스",
        hero_copy: str = "내가 내는 보험료 그대로 보장 최대 업그레이드!",
        **kwargs
    ) -> str:
        """
        초고화질 다크 에메랄드 글래스모피즘 CTA 세그먼트 MP4 초고속 생성
        """
        out_p = Path(output_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        temp_dir = Path(tempfile.mkdtemp(prefix="insure_cta_glass_"))
        frame_png = temp_dir / "cta_master_frame.png"

        try:
            self.render_cta_frame_image(
                output_png_path=str(frame_png),
                topic_title=topic_title,
                debate_question=debate_question,
                search_keyword=search_keyword,
                hero_copy=hero_copy,
                debate_opt1_title=kwargs.get("debate_opt1_title", "🤖 34개사 AI 객관적 비교 선택"),
                debate_opt1_sub=kwargs.get("debate_opt1_sub", "동일 보험료로 보장 가장 큰 상품 자율 선택"),
                debate_opt1_rate=kwargs.get("debate_opt1_rate", "88% (대세)"),
                debate_opt2_title=kwargs.get("debate_opt2_title", "👤 지인/설계사 추천 상품 유지"),
                debate_opt2_sub=kwargs.get("debate_opt2_sub", "기존 권유받은 패키지 그대로 유지"),
                debate_opt2_rate=kwargs.get("debate_opt2_rate", "12%"),
                benefit_items=kwargs.get("benefit_items")
            )

            # ffmpeg 루프로 초고속 무손실 MP4 인코딩
            cmd = [
                self.ffmpeg_exe, "-y",
                "-loop", "1",
                "-i", str(frame_png),
                "-t", str(duration_sec),
                "-r", str(fps),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-crf", "18",
                "-preset", "fast",
                str(out_p)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            logger.info(f"🎉 [InsuranceCTACard] 숏폼 다크 에메랄드 글래스모피즘 CTA 비디오 완성: {out_p}")
            return str(out_p)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    cta = InsuranceCTACard()
    test_out = r"c:\Users\zkfnt\Desktop\한국 마케팅봇\kmarket-marketing-engine\scratch\test_insurance_cta_emerald_1080x1920.mp4"
    cta.create_cta_segment_mp4(
        output_path=test_out,
        duration_sec=2.0,
        topic_title="AI 보험료 역추정 비교 & 가성비 리모델링",
        debate_question="보험 리모델링 시, 설계사 권유 상품 가입 vs 내 보험료 기준 AI 역추정 비교?",
        search_keyword="보험 리밸런스",
        hero_copy="매달 내는 보험료 역추정 분석!"
    )
    print("✅ [InsuranceCTACard] 다크 에메랄드 글래스모피즘 테스트 CTA 비디오 생성 완료:", test_out)
