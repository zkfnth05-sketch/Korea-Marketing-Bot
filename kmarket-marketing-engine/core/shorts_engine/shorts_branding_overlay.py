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
            "keyword": "아우라AI데이팅",
            "sub_guide": "👉 네이버에 '아우라AI데이팅' 검색 또는 상단 프로필 링크 클릭!",
            "filename": "aura_branding_overlay_1080x1920.png"
        },
        "insurance": {
            "icon": "🛡️",
            "brand_name": "보험 리밸런스",
            "sub_text": "34개사 실시간 비교",
            "sub_color_hex": "#34D399",
            "sub_color_class": "text-emerald-400",
            "keyword": "보험 리밸런스",
            "sub_guide": "👉 네이버에 '보험 리밸런스' 검색 또는 상단 프로필 링크 클릭!",
            "filename": "insurance_branding_overlay_1080x1920.png"
        },
        "stock": {
            "icon": "📈",
            "brand_name": "StockMaster AI",
            "sub_text": "외인·기관 실시간 수급 포착",
            "sub_color_hex": "#FBBF24",
            "sub_color_class": "text-amber-400",
            "keyword": "스톡마스터 AI",
            "sub_guide": "👉 네이버에 '스톡마스터 AI' 검색 또는 상단 프로필 링크 클릭!",
            "filename": "stock_branding_overlay_1080x1920.png"
        }
    }

    @classmethod
    def build_overlay_html(cls, config: Dict[str, Any]) -> str:
        """카드뉴스 디자인을 100% 동일하게 가져온 1080x1920 투명 오버레이 HTML"""
        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdn.tailwindcss.com"></script>
<style>
  body {{
    background: transparent;
    margin: 0;
    padding: 0;
    width: 1080px;
    height: 1920px;
    overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Pretendard', 'Noto Sans KR', sans-serif;
  }}
  .naver-glow {{
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7), 0 0 35px rgba(3, 199, 90, 0.45);
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

  <!-- [2] 하단 골든 세이프존: 카드뉴스 5번 공식 네이버 검색창 UI (바닥에서 310px) -->
  <div style="position:absolute; bottom:230px; left:50%; transform:translateX(-50%); width:900px;" class="flex flex-col items-center">
    
    <!-- 네이버 공식 검색창 본체 (화이트 라운드 카드 + 초록 보더 & 글로우) -->
    <div class="w-full bg-white rounded-3xl p-4 px-6 flex items-center justify-between naver-glow border-2 border-[#03C75A]">
      
      <!-- 좌측: 네이버 공식 N 로고 + 텍스트 키워드 -->
      <div class="flex items-center gap-4">
        <div class="w-14 h-14 rounded-2xl bg-[#03C75A] flex items-center justify-center font-black text-white text-3xl shadow-md">
          N
        </div>
        <div class="text-left">
          <p class="text-xs font-bold text-slate-500 mb-0.5">네이버 검색창에 입력하세요</p>
          <p class="text-3xl font-black text-slate-900 tracking-tight">{config["keyword"]}</p>
        </div>
      </div>

      <!-- 우측: 네이버 녹색 검색 버튼 -->
      <div class="bg-[#03C75A] text-white font-black text-xl px-7 py-3.5 rounded-2xl flex items-center gap-2 shadow-lg">
        <span>검색</span>
        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
        </svg>
      </div>
    </div>

    <!-- 하단 서브 안내 캡슐 바 (다크 글래스모피즘 가이드) -->
    <div class="inline-flex items-center justify-center gap-2 bg-slate-950/85 backdrop-blur-md border border-white/20 rounded-full py-2.5 px-6 shadow-xl mt-3">
      <span class="text-sm font-bold {config["sub_color_class"]} tracking-tight">{config["sub_guide"]}</span>
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
