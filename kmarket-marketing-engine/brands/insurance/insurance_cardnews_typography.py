# -*- coding: utf-8 -*-
"""
InsuranceCardnewsTypography - 🛡️ [보험 리밸런스 전용 1080x1350 고화질 무결점 Playwright 타이포그래피 엔진]
=====================================================================================================
• 핵심 원칙:
  1. 첫 번째 카드(표지) 임팩트 극대화: 초대형 에메랄드 그린 헤드라인 + 3D 외곽선 4px + 고시인성 배지
  2. 5장 완결 체계 (01/05 ~ 05/05)
  3. Playwright Chromium (Google Skia + HarfBuzz) 1080x1350 초고화질 네이티브 텍스트 셰이핑
  4. 하단 3차 가속 감쇠(Cubic Ease-In) 그라디언트 스크림 + 민트그린 불릿 + 웜골드 CTA
"""

import html
import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image
import io
from playwright.sync_api import sync_playwright
from core.engine.naver_search_bar_component import render_naver_search_bar_html


logger = logging.getLogger("InsuranceCardnewsTypography")


class InsuranceCardnewsTypography:
    """🛡️ 보험 리밸런스 전용 1080x1350 카드뉴스 고화질 무결점 타이포그래피 렌더러"""

    OFFICIAL_KEYWORD = "보험 리밸런스"
    OFFICIAL_URL = "https://insure-rebalance.vercel.app/"
    BRAND_NAME = "보험 리밸런스"
    BRAND_SUB = "34개사 실시간 비교"

    def __init__(self):
        self.viewport_w = 540
        self.viewport_h = 675
        self.scale_factor = 2.0  # 540x675 * 2.0 = 1080x1350

    def render_overlay(
        self,
        card_data: Dict[str, Any],
        s_idx: int = 1,
        total_slides: int = 5
    ) -> Image.Image:
        """
        card_data(배지, 제목, 부제, 3줄 불릿, CTA)를 1080x1350 투명 RGBA 이미지로 정밀 렌더링
        (첫 번째 표지 카드는 시선 강탈을 위해 폰트 크기 및 배지 가독성 대폭 강화)
        """
        badge = card_data.get("badge", f"TIP {s_idx}")
        title = card_data.get("title", "")
        subtitle = card_data.get("subtitle", "")
        bullets = card_data.get("bullets", [])

        # 상단 페이지 인덱스 (01 / 05 >)
        page_badge = f"{s_idx:02d} / {total_slides:02d} >"

        # 첫 번째 카드(표지) vs 중간 카드 vs 엔딩 카드 전용 스타일링 분기
        is_cover = (s_idx == 1)
        is_ending = (s_idx == total_slides)

        if is_cover:
            # 🌟 [첫 번째 표지 카드 특화] 시선 강탈 킬러 디자인
            headline_size = "24px"
            headline_stroke = "4.0px"
            subtitle_size = "13px"
            badge_bg = "linear-gradient(135deg, #10b981 0%, #059669 100%)"
            badge_color = "#ffffff"
            cta_bg = "#f59e0b"
            cta_color = "#0f172a"
            btn_text = card_data.get("cta_button") or "👉 옆으로 넘겨서 확인하기 (1/5) >"
        elif is_ending:
            # 🌟 [5번 엔딩 카드 특화] 네이버 공식 검색어 유도
            headline_size = "22px"
            headline_stroke = "3.5px"
            subtitle_size = "12.5px"
            badge_bg = "#10b981"
            badge_color = "#ffffff"
            cta_bg = "#f59e0b"
            cta_color = "#0f172a"
            btn_text = f"네이버에 '{self.OFFICIAL_KEYWORD}' 검색하기 >"
        else:
            # 중간 본문 카드 (2~4번)
            headline_size = "21.5px"
            headline_stroke = "3.5px"
            subtitle_size = "12.5px"
            badge_bg = "#10b981"
            badge_color = "#ffffff"
            cta_bg = "#f59e0b"
            cta_color = "#0f172a"
            btn_text = card_data.get("cta_button") or "다음 내용 보기 >"

        # 불릿 HTML 생성 (최대 3줄)
        bullets_html = ""
        for b in bullets[:3]:
            if b:
                clean_b = re.sub(r'^[•\-\*]\s*|^\d+[\.\)]\s*', '', b)
                bullets_html += f"""
                <div class="bullet-item">
                    <span class="bullet-dot">•</span>
                    <span class="bullet-text">{html.escape(clean_b)}</span>
                </div>
                """

        # 🌟 [하단 CTA 바] 오직 '👉 옆으로 넘겨서...' 자리에만 네이버 공식 검색창 바 1:1 교체
        if is_cover or "옆으로 넘겨" in btn_text or not is_ending:
            bottom_cta_html = render_naver_search_bar_html(brand="insurance")
        else:
            bottom_cta_html = f'<div class="cta-button">{html.escape(btn_text)}</div>'

        raw_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;700;800;900&display=swap');

    * {{
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }}

    body {{
        width: {self.viewport_w}px;
        height: {self.viewport_h}px;
        background: transparent;
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans KR", sans-serif;
        color: #ffffff;
        overflow: hidden;
        position: relative;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 0;
    }}

    /* 🌟 [상단 헤더 영역 - 글래스모피즘] */
    .top-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 22px 20px 0;
        z-index: 10;
    }}
    .brand-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(15, 23, 42, 0.82);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 9999px;
        padding: 6px 14px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.45);
    }}
    .brand-icon {{
        font-size: 13px;
    }}
    .brand-text {{
        font-size: 13px;
        font-weight: 900;
        letter-spacing: 0.5px;
        color: #ffffff;
    }}
    .brand-sub {{
        font-size: 11px;
        font-weight: 700;
        color: #34d399;
        padding-left: 5px;
        border-left: 1px solid rgba(255, 255, 255, 0.25);
    }}
    .page-index {{
        color: #f59e0b;
        font-weight: 800;
        font-size: 12.5px;
        background: rgba(15, 23, 42, 0.82);
        backdrop-filter: blur(14px);
        padding: 6px 13px;
        border-radius: 9999px;
        border: 1px solid rgba(245, 158, 11, 0.4);
        letter-spacing: 0.5px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.45);
    }}

    /* 🌟 [하단 그라디언트 스크림 및 텍스트 컨테이너 - 네모 박스 100% 제거, Aura 규격] */
    .bottom-scrim {{
        width: 100%;
        background: linear-gradient(
            180deg,
            rgba(0, 0, 0, 0) 0%,
            rgba(15, 23, 42, 0.22) 20%,
            rgba(15, 23, 42, 0.58) 50%,
            rgba(15, 23, 42, 0.94) 100%
        );
        padding: 24px 20px 22px;
        display: flex;
        flex-direction: column;
        gap: 7px;
        z-index: 5;
    }}

    /* 카테고리/단계 배지 */
    .category-badge {{
        align-self: flex-start;
        background: {badge_bg};
        color: {badge_color};
        font-weight: 800;
        font-size: 11.5px;
        padding: 4px 12px;
        border-radius: 6px;
        letter-spacing: -0.2px;
        box-shadow: 0 3px 10px rgba(16, 185, 129, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.35);
        margin-bottom: 2px;
    }}

    /* 🌟 [골드 입체 테두리 & 3D 딥 섀도우 헤드라인 - Aura 100% 동일] */
    .headline-title {{
        font-size: {headline_size};
        font-weight: 900;
        color: #ffd700;
        line-height: 1.28;
        -webkit-text-stroke: {headline_stroke} #0a0f1d;
        paint-order: stroke fill;
        text-shadow: 0 4px 16px rgba(0, 0, 0, 0.98), 0 2px 4px rgba(0, 0, 0, 0.95);
        letter-spacing: -0.4px;
        word-break: keep-all;
    }}

    /* 서브타이틀 */
    .subtitle-text {{
        font-size: {subtitle_size};
        font-weight: 700;
        color: #ffffff;
        line-height: 1.38;
        -webkit-text-stroke: 2px #0a0f1d;
        paint-order: stroke fill;
        text-shadow: 0 3px 10px rgba(0, 0, 0, 0.95);
        letter-spacing: -0.2px;
        word-break: keep-all;
        margin-bottom: 2px;
    }}

    /* 3줄 불릿 리스트 - 네모 박스/남색 배경 100% 제거 */
    .bullets-list {{
        display: flex;
        flex-direction: column;
        gap: 3px;
        margin: 2px 0 4px;
    }}
    .bullet-item {{
        display: flex;
        align-items: baseline;
        gap: 6px;
        font-size: 11.5px;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.35;
        -webkit-text-stroke: 1.8px #0a0f1d;
        paint-order: stroke fill;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.95);
    }}
    .bullet-dot {{
        color: #34d399;
        font-weight: 900;
        font-size: 13px;
        text-shadow: 0 2px 6px rgba(0, 0, 0, 0.9);
    }}
    .bullet-text {{
        word-break: keep-all;
    }}

    /* 🌟 [하단 CTA 버튼] */
    .cta-button {{
        width: 100%;
        background: linear-gradient(135deg, {cta_bg} 0%, #ea580c 100%);
        color: {cta_color};
        font-size: 14px;
        font-weight: 900;
        padding: 11px 20px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.35);
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.45);
        letter-spacing: -0.2px;
        margin-top: 3px;
    }}
</style>
</head>
<body>
    <div class="top-header">
        <div class="brand-badge">
            <span class="brand-icon">🛡️</span>
            <span class="brand-text">{self.BRAND_NAME}</span>
            <span class="brand-sub">{self.BRAND_SUB}</span>
        </div>
        <div class="page-index">{page_badge}</div>
    </div>
    <div class="bottom-scrim">
        <div class="category-badge">{html.escape(badge)}</div>
        <div class="headline-title">{html.escape(title)}</div>
        {f'<div class="subtitle-text">{html.escape(subtitle)}</div>' if subtitle else ''}
        {f'<div class="bullets-list">{bullets_html}</div>' if bullets_html else ''}
        {bottom_cta_html}
    </div>
</body>
</html>"""

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                viewport={"width": self.viewport_w, "height": self.viewport_h},
                device_scale_factor=self.scale_factor
            )
            page.set_content(raw_html, wait_until="networkidle")
            png_bytes = page.screenshot(type="png", omit_background=True)
            browser.close()

        overlay_img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
        return overlay_img

    def composite_slide(
        self,
        base_photo: Optional[Image.Image] = None,
        card_data: Dict[str, Any] = None,
        s_idx: int = 1,
        total_slides: int = 5,
        bg_image: Optional[Image.Image] = None,
        slide_idx: Optional[int] = None
    ) -> Image.Image:
        """
        보험 5장 카드뉴스 슬라이드 합성 (Aura와 100% 동일 규격):
        - base_photo를 1080x1350 풀블리드 센터 크롭
        - 하단 딥 다크 그라디언트 스크림 강화 (가독성 100% 확보)
        - Playwright 고해상도 3D 타이포그래피 오버레이 알파 합성
        """
        from PIL import ImageDraw
        photo = base_photo if base_photo is not None else bg_image
        if photo is None:
            photo = Image.new("RGB", (1080, 1350), (15, 23, 42))
        
        idx = slide_idx if slide_idx is not None else s_idx
        canvas = Image.new("RGB", (1080, 1350), (15, 23, 42))

        # 1. 베이스 사진 1080x1350 풀블리드 센터 크롭
        W, H = photo.size
        scale = max(1080 / W, 1350 / H)
        resized_photo = photo.resize((int(W * scale), int(H * scale)), Image.Resampling.LANCZOS)

        crop_x = (resized_photo.width - 1080) // 2
        crop_y = (resized_photo.height - 1350) // 2
        photo_cropped = resized_photo.crop((crop_x, crop_y, crop_x + 1080, crop_y + 1350))
        canvas.paste(photo_cropped, (0, 0))

        # 2. 하단 부드러운 그라디언트 스크림 (가독성 100% 보장)
        gradient_layer = Image.new("RGBA", (1080, 1350), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(gradient_layer)
        scrim_start_y = 750
        scrim_height = 1350 - scrim_start_y

        for i in range(scrim_height):
            curr_y = scrim_start_y + i
            ratio = i / float(scrim_height)
            alpha = int((ratio ** 2.2) * 230)
            g_draw.line([(0, curr_y), (1080, curr_y)], fill=(11, 19, 43, alpha))

        canvas = Image.alpha_composite(canvas.convert("RGBA"), gradient_layer).convert("RGB")

        # 3. Playwright Chromium 고해상도 타이포그래피 오버레이 합성
        overlay = self.render_overlay(
            card_data=card_data,
            s_idx=idx,
            total_slides=total_slides
        )
        final_img = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
        return final_img

    def render_slide(
        self,
        bg_image: Image.Image,
        card_data: Dict[str, Any],
        slide_idx: int = 1,
        total_slides: int = 5
    ) -> Image.Image:
        return self.composite_slide(
            base_photo=bg_image,
            card_data=card_data,
            s_idx=slide_idx,
            total_slides=total_slides
        )
