# -*- coding: utf-8 -*-
"""
ShortsBrandingOverlay (core/shorts_engine/shorts_branding_overlay.py)
===================================================================
- 3대 브랜드(Aura, Insurance, Stock) 숏폼 영상(1080x1920) 전용 브랜딩 오버레이 렌더러
- 카드뉴스 공식 디자인 시스템 100% 동일 계승:
  1. 상단 좌측: 카드뉴스 표지 다크 글래스모피즘 캡슐 뱃지
     - Aura: [💖 AURA | 50:50 남녀 황금 성비]
     - Insurance: [🛡️ 보험 리밸런스 | 34개사 실시간 비교]
     - Stock: [📈 StockMaster AI | 외인·기관 실시간 수급 포착]
  2. 하단 골든 세이프존: 카드뉴스 5번 공식 네이버 검색창 UI
     - 모델 테이블/손목 영역(하단 230px)에 배치하여 숏폼 기본 UI 가림 방지
     - 네이버 공식 녹색 N 뱃지 + 공식 키워드 + 검색 버튼 + 가이드 캡슐 바
"""

import os
import sys

# Windows cp949 콘솔 안전 인코딩 보장
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image

logger = logging.getLogger("ShortsBrandingOverlay")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
OVERLAYS_DIR = CURRENT_DIR / "presets" / "branding_overlays"
OVERLAYS_DIR.mkdir(parents=True, exist_ok=True)


class ShortsBrandingOverlay:
    """🎬 숏폼 영상 1080x1920 세로 풀HD 전용 통합 브랜딩 오버레이 엔진"""

    BRAND_CONFIGS = {
        "aura": {
            "icon": "💖",
            "brand_name": "AURA",
            "sub_text": "50:50 남녀 황금 성비",
            "sub_color_hex": "#F472B6",
            "sub_color_class": "text-pink-400",
            "badge_label": "3초 무료 입장",
            "headline": "아우라 ai 데이팅 모든기능 무료 사용하기",
            "sub_guide": "👉 아래 댓글창을 누르고 공식 웹사이트에 3초 만에 무료 입장하세요!",
            "btn_text": "댓글링크 참조 👉",
            "border_gradient": "linear-gradient(135deg, #F43F5E, #EC4899, #A855F7)",
            "glow_color": "rgba(244, 63, 94, 0.45)",
            "accent_color": "#FB7185",
            "btn_gradient": "linear-gradient(135deg, #F43F5E, #A855F7)",
            "badge_bg": "rgba(244, 63, 94, 0.2)",
            "badge_border": "rgba(251, 113, 133, 0.5)",
            "badge_text": "#FDA4AF",
            "keyword": "아우라AI데이팅",
            "filename": "aura_branding_overlay_1080x1920.png"
        },
        "insurance": {
            "icon": "🛡️",
            "brand_name": "보험 리밸런스",
            "sub_text": "34개사 실시간 비교",
            "sub_color_hex": "#34D399",
            "sub_color_class": "text-emerald-400",
            "badge_label": "34개사 실시간 비교",
            "headline": "보험리밸런스 34개 보험사 모든 보험 무료조회",
            "sub_guide": "👉 아래 댓글창을 누르고 내 숨은 보험료 다이어트를 무료로 시작하세요!",
            "btn_text": "댓글링크 참조 👉",
            "border_gradient": "linear-gradient(135deg, #10B981, #06B6D4, #3B82F6)",
            "glow_color": "rgba(16, 185, 129, 0.45)",
            "accent_color": "#34D399",
            "btn_gradient": "linear-gradient(135deg, #10B981, #06B6D4)",
            "badge_bg": "rgba(16, 185, 129, 0.2)",
            "badge_border": "rgba(52, 211, 153, 0.5)",
            "badge_text": "#6EE7B7",
            "keyword": "보험 리밸런스",
            "filename": "insurance_branding_overlay_1080x1920.png"
        },
        "stock": {
            "icon": "📈",
            "brand_name": "StockMaster AI",
            "sub_text": "외인·기관 실시간 수급 포착",
            "sub_color_hex": "#FBBF24",
            "sub_color_class": "text-amber-400",
            "badge_label": "실시간 퀀트 분석",
            "headline": "10분마다 국내우량주 350개 종목 실시간 퀀트점수 확인",
            "sub_guide": "👉 아래 댓글창을 누르고 오늘 급등 유망주 AI 퀀트 점수를 즉시 확인하세요!",
            "btn_text": "댓글링크 참조 👉",
            "border_gradient": "linear-gradient(135deg, #F59E0B, #EF4444, #EC4899)",
            "glow_color": "rgba(245, 158, 11, 0.45)",
            "accent_color": "#FBBF24",
            "btn_gradient": "linear-gradient(135deg, #F59E0B, #EF4444)",
            "badge_bg": "rgba(245, 158, 11, 0.2)",
            "badge_border": "rgba(251, 191, 36, 0.5)",
            "badge_text": "#FDE68A",
            "keyword": "스톡마스터 AI",
            "filename": "stock_branding_overlay_1080x1920.png"
        }
    }

    @classmethod
    def build_overlay_html(cls, config: Dict[str, Any]) -> str:
        """1080x1920 세로 풀HD 투명 오버레이 HTML (다크 글래스모피즘 댓글링크 참조 배너)"""
        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdn.tailwindcss.com"></script>
<style>
  @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
  body {{
    background: transparent;
    margin: 0;
    padding: 0;
    width: 1080px;
    height: 1920px;
    overflow: hidden;
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', sans-serif;
  }}
  .glass-card {{
    background: rgba(13, 17, 28, 0.94);
    backdrop-filter: blur(28px);
    border-radius: 28px;
    position: relative;
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.85), 0 0 50px {config['glow_color']};
  }}
  .glass-card::before {{
    content: '';
    position: absolute;
    inset: -2px;
    border-radius: 30px;
    padding: 2.5px;
    background: {config['border_gradient']};
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
  }}
  .btn-gradient {{
    background: {config['btn_gradient']};
    box-shadow: 0 8px 24px {config['glow_color']};
  }}
  .pulse-dot {{
    animation: pulse 1.8s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }}
  @keyframes pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: .6; transform: scale(1.15); }}
  }}
</style>
</head>
<body>

  <!-- [1] 상단 좌측: 카드뉴스 표지 공식 다크 글래스모피즘 캡슐 뱃지 -->
  <div style="position:absolute; top:75px; left:50px;">
    <div class="inline-flex items-center gap-3.5 bg-slate-950/85 backdrop-blur-xl border border-white/25 rounded-full py-3.5 px-7 shadow-[0_12px_36px_rgba(0,0,0,0.7)]">
      <span class="text-3xl">{config["icon"]}</span>
      <span class="text-2xl font-black tracking-wider text-white">{config["brand_name"]}</span>
      <span class="text-lg font-bold {config["sub_color_class"]} pl-3.5 border-l border-white/30">{config["sub_text"]}</span>
    </div>
  </div>

  <!-- [2] 하단 골든 세이프존: 신규 다크 글래스모피즘 댓글링크 참조 배너 UI (바닥에서 230px) -->
  <div style="position:absolute; bottom:230px; left:50%; transform:translateX(-50%); width:960px;">
    
    <div class="glass-card w-full p-6 px-8 flex flex-col gap-3">
      
      <!-- 상단 라인: 뱃지 + 헤드라인 + 우측 CTA 버튼 -->
      <div class="flex items-center justify-between gap-5">
        
        <div class="flex items-center gap-4 flex-1 min-w-0">
          <!-- 💬 댓글 아이콘 박스 -->
          <div class="w-14 h-14 rounded-2xl flex items-center justify-center text-3xl shrink-0" 
               style="background: {config['badge_bg']}; border: 1.5px solid {config['badge_border']};">
            💬
          </div>

          <div class="flex flex-col gap-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full text-xs font-black tracking-wide"
                    style="background: {config['badge_bg']}; color: {config['badge_text']}; border: 1px solid {config['badge_border']};">
                <span class="w-1.5 h-1.5 rounded-full bg-current pulse-dot"></span>
                {config['badge_label']}
              </span>
              <span class="text-xs font-bold text-slate-400">| 첫 댓글 고정</span>
            </div>
            <!-- 대표님 지정 헤드라인 문구 -->
            <h2 class="text-[25px] font-black text-white tracking-tight leading-tight truncate">
              {config['headline']}
            </h2>
          </div>
        </div>

        <!-- 우측: '댓글링크 참조 👉' 네온 버튼 -->
        <div class="btn-gradient shrink-0 px-6 py-4 rounded-2xl flex items-center gap-2.5 text-white font-black text-xl tracking-tight shadow-xl">
          <span>{config['btn_text']}</span>
        </div>

      </div>

      <!-- 하단 안내 라인 -->
      <div class="flex items-center justify-between pt-2.5 border-t border-white/10 text-xs font-medium text-slate-300">
        <div class="flex items-center gap-2">
          <span class="text-emerald-400 font-bold">● 1초 직결</span>
          <span>{config['sub_guide']}</span>
        </div>
        <div class="flex items-center gap-1.5 text-slate-400 font-bold">
          <span>무료 혜택 즉시 적용</span>
          <span>⚡</span>
        </div>
      </div>

    </div>

  </div>

</body>
</html>"""

    @classmethod
    def render_overlay_png(cls, brand_key: str, out_path: Optional[str] = None) -> str:
        """Playwright Chromium을 통해 1080x1920 세로 풀HD 투명 오버레이 PNG 생성"""
        config = cls.BRAND_CONFIGS.get(brand_key.lower())
        if not config:
            raise ValueError(f"지원하지 않는 브랜드 키입니다: {brand_key}")

        if not out_path:
            out_path = str(OVERLAYS_DIR / config["filename"])

        html_content = cls.build_overlay_html(config)

        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1920})
            page.set_content(html_content)
            page.wait_for_timeout(500)
            page.screenshot(path=out_path, omit_background=True)
            browser.close()

        logger.info(f"투명 오버레이 렌더 완료: {brand_key.upper()} -> {out_path}")
        return out_path

    @classmethod
    def get_overlay_path(cls, brand_key: str, force_refresh: bool = False) -> str:
        """브랜드별 1080x1920 통합 오버레이 파일 경로 반환 (필요시 자동 렌더링)"""
        config = cls.BRAND_CONFIGS.get(brand_key.lower())
        if not config:
            raise ValueError(f"지원하지 않는 브랜드 키입니다: {brand_key}")

        out_path = OVERLAYS_DIR / config["filename"]
        if force_refresh or not out_path.exists():
            cls.render_overlay_png(brand_key, str(out_path))

        return str(out_path)

    @classmethod
    def create_preview_on_photo(cls, brand_key: str, bg_image_path: str, out_preview_path: str) -> str:
        """실사 인물 사진 배경(1080x1920) 위에 상단 뱃지와 하단 네이버 검색창 오버레이를 정밀 합성"""
        overlay_path = cls.get_overlay_path(brand_key)

        # 1. 배경 이미지 로드 및 1080x1920 맞춤
        bg = Image.open(bg_image_path).convert("RGBA")
        if bg.size != (1080, 1920):
            bg = bg.resize((1080, 1920), Image.Resampling.LANCZOS)

        # 2. 투명 오버레이 로드
        overlay = Image.open(overlay_path).convert("RGBA")

        # 3. 알파 채널 합성
        combined = Image.alpha_composite(bg, overlay)

        # 4. 저장 (RGB)
        Path(out_preview_path).parent.mkdir(parents=True, exist_ok=True)
        combined.convert("RGB").save(out_preview_path, "PNG", quality=95)
        return out_preview_path


if __name__ == "__main__":
    for b in ["aura", "insurance", "stock"]:
        out = ShortsBrandingOverlay.render_overlay_png(b)
        print(f"Overlay created: {b} -> {out}")
