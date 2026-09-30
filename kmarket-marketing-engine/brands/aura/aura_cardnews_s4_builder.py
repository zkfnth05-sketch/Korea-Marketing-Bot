# -*- coding: utf-8 -*-
"""
AuraCardnewsS4Builder - 📱 [Aura 카드뉴스 4번 전용 실시간 AI 자막 통화 화면 에셋 빌더]
================================================================================
• 역할:
  - 1~3번 슬라이드의 나나미(Nanami, 24세 일본인) 실제 이미지를 영상통화 화면 속에 1:1 주입
  - 숏폼 2번 영상통화 UI(스마트폰 목업 + 상단 PiP + '한국 놀러 가고 싶어! 🍒' 실시간 자막 바)를
    1080x1350 카드뉴스 황금 비율 규격으로 정밀 렌더링
  - 산출물: brands/aura/assets/aura_subtitles_call_screen.png
"""

import os
import re
import base64
import logging
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

logger = logging.getLogger("AuraCardnewsS4Builder")


class AuraCardnewsS4Builder:
    """Aura 주제 2(실시간 AI 자막 통화) 4번 카드 전용 앱 시연 화면 빌더"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.assets_dir = self.base_dir / "assets"
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.output_asset_path = self.assets_dir / "aura_subtitles_call_screen.png"
        
        # 나나미 원본 T2I 이미지 경로 (Slide 1의 정면 미소 컷)
        self.nanami_source_path = Path(r"D:\ComfyUI_Wan_Engine\ComfyUI\output\aura_cardnews_s1_00001_.png")
        if not self.nanami_source_path.exists():
            # 대안 경로: ComfyUI output 내 최신 s1 이미지
            candidates = sorted(Path(r"D:\ComfyUI_Wan_Engine\ComfyUI\output").glob("aura_cardnews_s1_*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
            if candidates:
                self.nanami_source_path = candidates[0]

    def _get_male_pip_b64(self) -> str:
        """기존 숏폼 UI 템플릿에서 남성 셀카 PiP base64 추출"""
        template_path = self.base_dir / "ui_templates" / "aura_subtitles_call_sim.html"
        if template_path.exists():
            with open(template_path, "r", encoding="utf-8") as f:
                html = f.read()
            # scale-x 클래스를 가진 남성 PiP img 찾기
            imgs = re.findall(r'<img[^>]+>', html)
            for img in imgs:
                if "scale-x" in img:
                    m = re.search(r'src="([^"]+)"', img)
                    if m:
                        return m.group(1)
        return ""

    def _get_nanami_b64(self) -> str:
        """나나미 실물 사진을 스마트폰 통화 화면에 최적화된 base64 JPEG로 인코딩"""
        if self.nanami_source_path.exists():
            img = Image.open(str(self.nanami_source_path)).convert("RGB")
            # 얼굴/상반신 중심 최적 세로 비율 리사이즈 및 인코딩
            import io
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=95)
            b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
            return f"data:image/jpeg;base64,{b64_str}"
        return ""

    def build_s4_screen_asset(self) -> Path:
        """1080x1350 카드뉴스 규격으로 나나미 영상통화 화면 에셋 렌더링"""
        logger.info("🎨 [AuraCardnewsS4Builder] 나나미 실시간 자막 통화 화면 에셋 빌드 시작...")

        nanami_b64 = self._get_nanami_b64()
        male_pip_b64 = self._get_male_pip_b64()

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Aura Subtitles Call Screen (1080x1350)</title>
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
      background: radial-gradient(circle at 50% 30%, #151620 0%, #08080c 60%, #030305 100%);
      color: #fff;
      position: relative;
    }}

    /* 럭셔리 스마트폰 섀시 (카드뉴스 중앙 상단에 최적 배치) */
    .phone-chassis {{
      position: absolute;
      top: 15px;
      left: 100px;
      width: 880px;
      height: 1120px;
      background: #09090b;
      border-radius: 60px;
      padding: 14px;
      box-shadow: 
        0 40px 100px rgba(0, 0, 0, 0.95), 
        0 0 60px rgba(229, 169, 52, 0.25),
        0 0 0 4px #27272a,
        inset 0 0 0 3px rgba(255, 255, 255, 0.15);
    }}

    .phone-screen {{
      position: relative;
      width: 100%;
      height: 100%;
      border-radius: 48px;
      overflow: hidden;
      background: #000;
    }}

    .glass-card {{
      background: rgba(0, 0, 0, 0.78);
      backdrop-filter: blur(28px);
      -webkit-backdrop-filter: blur(28px);
      border: 1px solid rgba(255, 255, 255, 0.2);
    }}

    .glass-pill {{
      background: rgba(12, 12, 16, 0.75);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.2);
    }}

    .glow-gold {{
      box-shadow: 0 0 30px rgba(229, 169, 52, 0.55);
    }}
    .glow-red {{
      box-shadow: 0 10px 30px rgba(239, 68, 68, 0.55);
    }}
  </style>
</head>
<body>

  <!-- Ambient Outer Glows -->
  <div class="absolute w-[700px] h-[700px] rounded-full bg-amber-500/12 blur-[140px] top-10 left-10 pointer-events-none"></div>
  <div class="absolute w-[600px] h-[600px] rounded-full bg-emerald-500/12 blur-[140px] top-60 right-10 pointer-events-none"></div>

  <!-- Main Smartphone Frame -->
  <div class="phone-chassis">
    <div class="phone-screen">

      <!-- 1. Background Video Call Stream (Nanami) -->
      <div class="absolute inset-0 w-full h-full overflow-hidden bg-zinc-950">
        <img 
          src="{nanami_b64}" 
          class="w-full h-full object-cover object-center filter brightness-95 contrast-105"
          alt="Nanami Video Call"
        />
        <!-- Subtle Top & Bottom Cinematic Shadow -->
        <div class="absolute inset-0 bg-gradient-to-b from-black/60 via-transparent to-black/80 pointer-events-none"></div>
      </div>

      <!-- 2. iOS Status Bar -->
      <div class="absolute top-2.5 left-0 right-0 px-10 h-12 flex items-center justify-between text-white text-lg font-bold z-50 pointer-events-none">
        <span class="tracking-tight font-semibold">09:41</span>
        
        <!-- Dynamic Island -->
        <div class="w-40 h-7 bg-black rounded-full flex items-center justify-between px-3 border border-zinc-800/80 shadow-md">
          <div class="w-2.5 h-2.5 rounded-full bg-zinc-900 border border-zinc-700"></div>
          <div class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
        </div>

        <div class="flex items-center gap-2 text-base font-semibold">
          <span class="text-xs font-bold">5G</span>
          <svg width="20" height="12" viewBox="0 0 25 12" fill="currentColor">
            <rect x="0.5" y="0.5" width="20" height="11" rx="3" stroke="currentColor" fill="none"/>
            <rect x="2" y="2" width="16" height="8" rx="1.5"/>
            <path d="M22 4C22.6 4.3 23 4.8 23 5.5C23 6.2 22.6 6.7 22 7V4Z" fill="currentColor"/>
          </svg>
        </div>
      </div>

      <!-- 3. Top Call Control & Info Bar -->
      <div class="absolute top-16 left-0 right-0 px-6 flex items-start justify-between z-40">
        <!-- Live AI Translation Engine Active Pill -->
        <div class="glass-pill px-4 py-2 rounded-full flex items-center gap-2.5 shadow-xl">
          <span class="relative flex h-2.5 w-2.5">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
          </span>
          <div class="flex flex-col">
            <span class="text-xs font-extrabold text-white tracking-wide">AI 실시간 통역</span>
            <span class="text-[10px] text-emerald-400 font-medium tracking-tight">한국어 ↔ 日本語 (0.1s)</span>
          </div>
        </div>

        <!-- Korean Male User PiP with Caller Tag -->
        <div class="relative w-28 h-36 rounded-2xl overflow-hidden shadow-2xl border-2 border-white/40 bg-zinc-900">
          <img 
            src="{male_pip_b64}" 
            class="w-full h-full object-cover scale-x-[-1]"
            alt="My Video Stream"
          />
          <div class="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/85 via-black/40 to-transparent p-1.5 flex flex-col items-center">
            <span class="text-[10px] text-zinc-300 font-bold">나(서울)</span>
          </div>
          <div class="absolute top-1.5 right-1.5 px-2 py-0.5 rounded-full bg-black/60 backdrop-blur-md text-[9px] text-zinc-300 font-semibold border border-white/20">
            00:15
          </div>
        </div>
      </div>

      <!-- 4. Nanami Info Top Badge (Right aligned under PiP) -->
      <div class="absolute top-56 right-6 z-40">
        <div class="glass-pill px-3.5 py-1.5 rounded-full flex items-center gap-2 shadow-lg">
          <span class="text-xs">🇯🇵</span>
          <span class="text-xs font-black text-white">나나미 (도쿄, 24)</span>
        </div>
      </div>

      <!-- 5. Center-Bottom Live Netflix-Style Subtitle Overlay -->
      <div class="absolute bottom-[310px] left-0 right-0 px-6 z-40 flex flex-col items-center space-y-2.5">
        <!-- Live AI Speech Recognition Pulse -->
        <div class="glass-pill px-4 py-1.5 rounded-full text-xs text-amber-300 font-bold flex items-center gap-2 shadow-lg">
          <span class="flex items-center gap-1">
            <span class="w-1 bg-[#E5A934] h-2.5 animate-pulse rounded-full"></span>
            <span class="w-1 bg-[#E5A934] h-4 animate-pulse rounded-full" style="animation-delay: 150ms"></span>
            <span class="w-1 bg-[#E5A934] h-2.5 animate-pulse rounded-full" style="animation-delay: 300ms"></span>
          </span>
          <span>나나미 음성 실시간 인식 중...</span>
        </div>

        <!-- 🌟 Realtime Translated Subtitle Card -->
        <div class="glass-card px-8 py-4.5 rounded-3xl shadow-[0_20px_60px_rgba(0,0,0,0.9)] max-w-lg w-full text-center space-y-1.5 border border-white/25">
          <!-- Korean Translated Live Subtitle (Main) -->
          <p class="text-2xl font-black text-white tracking-wide leading-snug drop-shadow-[0_2px_12px_rgba(0,0,0,0.95)]">
            한국 놀러 가고 싶어! 🍒
          </p>
          <!-- Japanese Original Speech (Sub) -->
          <p class="text-sm text-zinc-300 font-medium italic drop-shadow-[0_1px_4px_rgba(0,0,0,0.85)]">
            Nanami: 韓国に遊びに行きたい！
          </p>
        </div>
      </div>

      <!-- 6. Native In-Call Control Buttons (Bottom) -->
      <div class="absolute bottom-[210px] left-0 right-0 z-40 flex items-center justify-center gap-6 px-6">
        <!-- Mic -->
        <div class="w-14 h-14 rounded-full bg-white/10 text-white backdrop-blur-xl shadow-xl flex items-center justify-center">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>
        </div>

        <!-- Live Subtitles Toggle (Active Gold Glow) -->
        <div class="w-14 h-14 rounded-full text-white backdrop-blur-xl shadow-2xl bg-[#E5A934] glow-gold ring-4 ring-[#E5A934]/60 flex items-center justify-center">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 8 6 6"/><path d="m4 14 6-6 2-3"/><path d="M2 5h12"/><path d="M7 2h1"/><path d="m22 22-5-10-5 10"/><path d="M14 18h6"/></svg>
        </div>

        <!-- End Call (Red) -->
        <div class="w-16 h-16 rounded-full shadow-2xl bg-red-600 glow-red flex items-center justify-center text-white">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="currentColor"><path d="M10.68 13.31a16 16 0 0 0 3.41 2.6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7 2 2 0 0 1 1.72 2v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.42 19.42 0 0 1-3.33-2.67m-2.67-3.34a19.79 19.79 0 0 1-3.07-8.63A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91"/></svg>
        </div>

        <!-- Camera -->
        <div class="w-14 h-14 rounded-full bg-white/10 text-white backdrop-blur-xl shadow-xl flex items-center justify-center">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 8-6 4 6 4V8Z"/><rect width="14" height="12" x="2" y="6" rx="2" ry="2"/></svg>
        </div>
      </div>

    </div>
  </div>

</body>
</html>
"""
        # 임시 HTML 저장 및 Playwright 스크린샷 촬영
        temp_html_path = self.base_dir / "temp_s4_screen.html"
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
            page.goto(temp_html_path.as_uri())
            page.wait_for_timeout(1000) # 스타일 및 폰트 렌더링 대기
            page.screenshot(path=str(self.output_asset_path), type="png")
            browser.close()

        if temp_html_path.exists():
            temp_html_path.unlink()

        logger.info(f"✅ [AuraCardnewsS4Builder] 4번 전용 앱 에셋 렌더링 완료: {self.output_asset_path}")
        return self.output_asset_path


if __name__ == "__main__":
    builder = AuraCardnewsS4Builder()
    res = builder.build_s4_screen_asset()
    print("Done:", res)
