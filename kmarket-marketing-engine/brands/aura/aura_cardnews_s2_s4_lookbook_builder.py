# -*- coding: utf-8 -*-
"""
AuraCardnewsS2S4LookbookBuilder - 🏷️ [Aura 카드뉴스 4번 주제 2, 3, 4번 숏폼 룩북 이식 빌더]
==========================================================================================
• 역할:
  - 숏폼 4번 주제의 '청담동 스냅 화보급 AI 보정 (AURA STUDIO LOOKBOOK)' 4개 룩북 중
    대표님이 엄선하신 1번, 3번, 4번 모델을 1080x1350 카드뉴스 규격으로 100% 완벽 이식
  - 2번 카드 (02/05): LOOK #01 서연 (23) - 화사한 파스텔 핑크 트위드 재킷 (Lovely Spring)
  - 3번 카드 (03/05): LOOK #03 수아 (22) - 실크 캐미솔 + 가디건 레이어드 (Pure Elegance)
  - 4번 카드 (04/05): LOOK #04 유진 (24) - 모던 소프트 브이넥 니트 (Soft Minimal)
  - 세부 비주얼:
    * 샌드/토프 플라스터 월 + 부드러운 사선 햇살 빔 + 오가닉 리프 섀도우
    * 좌측 BEFORE 페이퍼 프레임 & 우측 AFTER 샴페인 골드 테두리 프레임
    * 상단 AURA 브랜드 배지 + 페이지 인덱스 (02/05 >, 03/05 >, 04/05 >)
    * 하단 다크 글래스모피즘 룩북 스펙 카드
"""

import os
import sys
import logging
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter

logger = logging.getLogger("AuraCardnewsS2S4LookbookBuilder")


class AuraCardnewsS2S4LookbookBuilder:
    """1080x1350 카드뉴스 규격 청담동 화보 룩북 (2, 3, 4번 슬라이드) 전문 빌더"""

    def __init__(self):
        self.w = 1080
        self.h = 1350
        self.artifact_dir = Path(r"C:\Users\zkfnt\.gemini\antigravity-ide\brain\9d989a93-cf2f-49a0-94dd-4e770271805c")
        
        # 대표님 선정 3대 모델 정의 (1번, 3번, 4번)
        self.models = {
            2: {
                "num": "01",
                "name": "서연",
                "age": 23,
                "style": "화사한 파스텔 핑크 트위드 재킷 (Lovely Spring)",
                "before_img": "woman1_before_seoyeon_1790299355914.jpg",
                "after_img": "woman1_after_seoyeon_v2_1790299815639.jpg",
                "badge_kr": "Lovely Spring",
                "slide_idx": 2
            },
            3: {
                "num": "03",
                "name": "수아",
                "age": 22,
                "style": "실크 캐미솔 + 가디건 레이어드 (Pure Elegance)",
                "before_img": "woman3_before_suah_1790299697602.jpg",
                "after_img": "woman3_after_suah_1790299719616.jpg",
                "badge_kr": "Pure Elegance",
                "slide_idx": 3
            },
            4: {
                "num": "04",
                "name": "유진",
                "age": 24,
                "style": "모던 소프트 브이넥 니트 (Soft Minimal)",
                "before_img": "woman4_before_yujin_1790299743008.jpg",
                "after_img": "woman4_after_yujin_1790299766621.jpg",
                "badge_kr": "Soft Minimal",
                "slide_idx": 4
            }
        }

        # 1080x1350 전용 스튜디오 배경 캐싱
        self._bg_1350 = self._create_studio_background_1350()

    def _get_font(self, size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
        candidates = [
            r"C:\Windows\Fonts\malgunbd.ttf" if bold else r"C:\Windows\Fonts\malgun.ttf",
            r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        ]
        for p in candidates:
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    def _create_studio_background_1350(self) -> Image.Image:
        """1080x1350 샌드/토프 플라스터 월 + 햇살 빔 + 나뭇잎 섀도우 생성"""
        arr = np.zeros((self.h, self.w, 3), dtype=np.float32)
        for y in range(self.h):
            ratio = y / self.h
            arr[y, :, 0] = 218.0 - ratio * 16.0
            arr[y, :, 1] = 205.0 - ratio * 18.0
            arr[y, :, 2] = 192.0 - ratio * 20.0

        np.random.seed(42)
        noise = np.random.normal(0, 3.0, (self.h, self.w, 3))
        arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
        bg = Image.fromarray(arr, mode="RGB")

        # 1. 사선 햇살 빔
        sun_layer = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(sun_layer)
        sun_poly = [(-150, -80), (680, -80), (400, 1450), (-250, 1450)]
        s_draw.polygon(sun_poly, fill=(255, 250, 235, 38))
        sun_layer = sun_layer.filter(ImageFilter.GaussianBlur(70))
        bg = Image.alpha_composite(bg.convert("RGBA"), sun_layer)

        # 2. 우측 은은한 나뭇잎 그림자
        leaf_layer = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        l_draw = ImageDraw.Draw(leaf_layer)
        shadow_col = (70, 55, 45, 50)

        stems = [
            [(1120, 280), (960, 480), (840, 720), (780, 950), (830, 1200)],
            [(1120, 750), (970, 920), (870, 1150)]
        ]
        for stem in stems:
            l_draw.line(stem, fill=shadow_col, width=15)

        leaf_centers = [
            (930, 420, 65, 120, -35),
            (880, 580, 75, 135, -50),
            (820, 780, 80, 145, -25),
            (760, 940, 85, 150, 10),
            (790, 1080, 80, 145, 35),
            (850, 1220, 80, 140, 45),
            (970, 880, 70, 125, -40),
            (910, 1040, 75, 135, -15),
            (1030, 220, 80, 140, -60),
            (1060, 380, 75, 130, -45)
        ]
        for lx, ly, lw, lh, rot in leaf_centers:
            leaf_mask = Image.new("RGBA", (lh * 2, lh * 2), (0, 0, 0, 0))
            lm_draw = ImageDraw.Draw(leaf_mask)
            cx, cy = lh, lh
            lm_draw.ellipse([cx - lw // 2, cy - lh // 2, cx + lw // 2, cy + lh // 2], fill=shadow_col)
            rotated = leaf_mask.rotate(rot, resample=Image.Resampling.BICUBIC)
            leaf_layer.paste(rotated, (lx - lh, ly - lh), rotated)

        leaf_layer = leaf_layer.filter(ImageFilter.GaussianBlur(28))
        bg = Image.alpha_composite(bg, leaf_layer)
        return bg.convert("RGB")

    def _render_paper_frame(
        self,
        photo_path: Path,
        frame_w: int,
        frame_h: int,
        border_size: int = 18,
        is_gold_border: bool = False
    ) -> Image.Image:
        """단일 사진 액자 (파인아트 페이퍼 질감 & 골드 테두리)"""
        frame = Image.new("RGBA", (frame_w, frame_h), (252, 250, 246, 255))
        f_draw = ImageDraw.Draw(frame)
        f_draw.rectangle([(0, 0), (frame_w - 1, frame_h - 1)], outline=(225, 220, 210, 255), width=1)

        pw = frame_w - border_size * 2
        ph = frame_h - border_size * 2

        if photo_path.exists():
            p_img = Image.open(photo_path).convert("RGB")
            img_w, img_h = p_img.size
            tr = pw / ph
            cr = img_w / img_h
            if cr > tr:
                nw = int(img_h * tr)
                p_img = p_img.crop(((img_w - nw) // 2, 0, (img_w + nw) // 2, img_h))
            else:
                nh = int(img_w / tr)
                p_img = p_img.crop((0, (img_h - nh) // 2, img_w, (img_h + nh) // 2))
            p_img = p_img.resize((pw, ph), Image.Resampling.LANCZOS)
            frame.paste(p_img.convert("RGBA"), (border_size, border_size))
            f_draw.rectangle([(border_size, border_size), (border_size + pw - 1, border_size + ph - 1)], outline=(200, 195, 185, 150), width=1)

            if is_gold_border:
                f_draw.rectangle([(border_size - 3, border_size - 3), (border_size + pw + 2, border_size + ph + 2)], outline=(212, 175, 55, 230), width=2)
                f_draw.rectangle([(0, 0), (frame_w - 1, frame_h - 1)], outline=(212, 175, 55, 245), width=3)

        return frame

    def _apply_drop_shadow(
        self,
        canvas: Image.Image,
        frame: Image.Image,
        x: int,
        y: int,
        blur_rad: int = 28,
        offset=(14, 22),
        shadow_alpha: int = 115
    ) -> Image.Image:
        """다층 소프트 3D 드롭 섀도우"""
        w, h = canvas.size
        fw, fh = frame.size
        pad = blur_rad * 3

        full_shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))

        s_img = Image.new("RGBA", (fw + pad * 2, fh + pad * 2), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(s_img)
        s_draw.rectangle([(pad + offset[0], pad + offset[1]), (pad + fw + offset[0], pad + fh + offset[1])], fill=(40, 30, 20, shadow_alpha))
        s_blurred = s_img.filter(ImageFilter.GaussianBlur(blur_rad))
        full_shadow.paste(s_blurred, (x - pad, y - pad), s_blurred)

        c_img = Image.new("RGBA", (fw + pad * 2, fh + pad * 2), (0, 0, 0, 0))
        c_draw = ImageDraw.Draw(c_img)
        c_draw.rectangle([(pad + 4, pad + 7), (pad + fw + 4, pad + fh + 7)], fill=(30, 20, 15, int(shadow_alpha * 0.85)))
        c_blurred = c_img.filter(ImageFilter.GaussianBlur(7))
        full_shadow.paste(c_blurred, (x - pad, y - pad), c_blurred)

        canvas_rgba = canvas.convert("RGBA")
        canvas_rgba = Image.alpha_composite(canvas_rgba, full_shadow)
        canvas_rgba.paste(frame, (x, y), frame)
        return canvas_rgba.convert("RGB")

    def _render_top_header_playwright(self, slide_num: int) -> Image.Image:
        """Playwright로 상단 브랜드 배지(💖 AURA)와 페이지 인덱스(02 / 05 >)를 1080x1350 투명 PNG로 렌더링"""
        from playwright.sync_api import sync_playwright
        import tempfile
        import shutil

        page_str = f"{slide_num:02d} / 05 &gt;"
        html_code = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
    * {{
        box-sizing: border-box;
        margin: 0;
        padding: 0;
        font-family: 'Pretendard', sans-serif;
    }}
    body {{
        width: 1080px;
        height: 1350px;
        background: transparent;
        overflow: hidden;
    }}
    .top-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 44px 40px 0;
        width: 100%;
    }}
    .brand-badge {{
        display: inline-flex;
        align-items: center;
        gap: 12px;
        background: rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(28px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 9999px;
        padding: 12px 28px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
    }}
    .brand-icon {{
        font-size: 26px;
    }}
    .brand-text {{
        font-size: 26px;
        font-weight: 900;
        letter-spacing: 1px;
        color: #ffffff;
    }}
    .brand-sub {{
        font-size: 22px;
        font-weight: 700;
        color: #f472b6;
        padding-left: 14px;
        border-left: 1px solid rgba(255, 255, 255, 0.25);
    }}
    .page-badge {{
        font-size: 24px;
        font-weight: 800;
        color: #fbbf24;
        background: rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(28px);
        border: 1px solid rgba(251, 191, 36, 0.4);
        border-radius: 9999px;
        padding: 12px 28px;
        letter-spacing: 1px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
    }}
</style>
</head>
<body>
    <div class="top-header">
        <div class="brand-badge">
            <span class="brand-icon">💖</span>
            <span class="brand-text">아우라 AI 데이팅</span>
            <span class="brand-sub">현재 100% 무료</span>
        </div>
        <div class="page-badge">
            {page_str}
        </div>
    </div>
</body>
</html>
"""
        temp_dir = Path(tempfile.mkdtemp(prefix="aura_top_bar_"))
        temp_html = temp_dir / "top_bar.html"
        temp_png = temp_dir / "top_bar.png"
        try:
            with open(temp_html, "w", encoding="utf-8") as f:
                f.write(html_code)
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
                page.goto(temp_html.as_uri())
                page.wait_for_timeout(300)
                page.screenshot(path=str(temp_png), type="png", omit_background=True)
                browser.close()
            return Image.open(str(temp_png)).convert("RGBA")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def build_lookbook_slide(self, slide_num: int, output_path: str) -> str:
        """
        1080x1350 카드뉴스 슬라이드 생성 (slide_num = 2, 3, 4)
        """
        m = self.models.get(slide_num, self.models[2])
        b_path = self.artifact_dir / m["before_img"]
        a_path = self.artifact_dir / m["after_img"]

        # 1080x1350 황금 프레임 사이즈
        fw, fh = 430, 560
        border = 18

        # 엇갈린 배치 (왼쪽 BEFORE는 살짝 아래, 오른쪽 AFTER는 위로 올려 황금비율 강조)
        left_x = 75
        left_y = 360

        right_x = 575
        right_y = 280

        # 액자 렌더링
        f_before = self._render_paper_frame(b_path, fw, fh, border_size=border, is_gold_border=False)
        f_after = self._render_paper_frame(a_path, fw, fh, border_size=border, is_gold_border=True)

        img = self._bg_1350.copy()
        img = self._apply_drop_shadow(img, f_before, left_x, left_y, blur_rad=28, offset=(12, 20), shadow_alpha=110)
        img = self._apply_drop_shadow(img, f_after, right_x, right_y, blur_rad=32, offset=(16, 24), shadow_alpha=125)

        draw = ImageDraw.Draw(img)

        # ── 1. 최상단 브랜드 바 (Playwright 서브픽셀 렌더링 - 💖 이모지 100% 무결점) ───
        top_bar_img = self._render_top_header_playwright(slide_num)
        img = Image.alpha_composite(img.convert("RGBA"), top_bar_img).convert("RGB")
        draw = ImageDraw.Draw(img)

        # ── 2. 에디토리얼 상단 타이틀 ──────────────────────────────────────────
        f_brand = self._get_font(22, bold=True)
        draw.text((self.w // 2, 125), "A U R A   S T U D I O   L O O K B O O K", font=f_brand, fill=(160, 125, 45), anchor="mm")

        f_title = self._get_font(38, bold=True)
        draw.text((self.w // 2, 175), "청담동 스냅 화보급 AI 보정", font=f_title, fill=(35, 30, 25), anchor="mm")

        f_sub = self._get_font(20, bold=False)
        draw.text((self.w // 2, 225), "자연스러운 본판 100% 보존 • 고급스러운 음영 조명", font=f_sub, fill=(115, 100, 90), anchor="mm")

        draw.line([(self.w // 2 - 110, 260), (self.w // 2 + 110, 260)], fill=(200, 165, 75), width=2)

        # ── 3. 액자 하단 라벨 (BEFORE vs AFTER) ─────────────────────────────────
        # Left: — BEFORE —
        b_label_y = left_y + fh + 25
        f_badge_en = self._get_font(24, bold=True)
        f_badge_kr = self._get_font(18, bold=False)
        draw.text((left_x + fw // 2, b_label_y), "—  B E F O R E  —", font=f_badge_en, fill=(130, 100, 45), anchor="mm")
        draw.text((left_x + fw // 2, b_label_y + 30), "[ 형광등 일상 셀카 ]", font=f_badge_kr, fill=(105, 90, 80), anchor="mm")

        # Right: — AFTER —
        a_label_y = right_y + fh + 25
        pill_w = 270
        pill_h = 46
        pill_x1 = right_x + fw // 2 - pill_w // 2
        pill_y1 = a_label_y - pill_h // 2
        
        draw.rounded_rectangle([(pill_x1, pill_y1), (pill_x1 + pill_w, pill_y1 + pill_h)], radius=15, fill=(55, 42, 22), outline=(212, 175, 55), width=2)
        draw.text((right_x + fw // 2, a_label_y - 2), "—  A F T E R  —", font=f_badge_en, fill=(255, 230, 140), anchor="mm")
        draw.text((right_x + fw // 2, a_label_y + 36), "[ 본판 보존 • 청담동 화보 ]", font=f_badge_kr, fill=(145, 110, 45), anchor="mm")

        # ── 4. 하단 플로팅 글래스모피즘 스펙 카드 ───────────────────────────────
        card_w = 980
        card_h = 220
        card_x1 = (self.w - card_w) // 2
        card_y1 = 1030

        glass = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(glass)
        g_draw.rounded_rectangle([(card_x1, card_y1), (card_x1 + card_w, card_y1 + card_h)], radius=28, fill=(24, 20, 18, 230), outline=(212, 175, 55, 180), width=2)
        
        # 배지 장식
        badge_w = 160
        badge_h = 32
        g_draw.rounded_rectangle([(card_x1 + 45, card_y1 + 35), (card_x1 + 45 + badge_w, card_y1 + 35 + badge_h)], radius=12, fill=(212, 175, 55, 40), outline=(212, 175, 55, 160), width=1)
        
        img = Image.alpha_composite(img.convert("RGBA"), glass).convert("RGB")
        draw = ImageDraw.Draw(img)

        # 배지 텍스트
        f_card_badge = self._get_font(15, bold=True)
        draw.text((card_x1 + 45 + badge_w // 2, card_y1 + 35 + badge_h // 2), m["badge_kr"], font=f_card_badge, fill=(255, 225, 130), anchor="mm")

        # 모델 타이틀
        f_model_name = self._get_font(32, bold=True)
        draw.text((card_x1 + 45 + badge_w + 20, card_y1 + 51), f"LOOK #{m['num']}   {m['name']} ({m['age']})", font=f_model_name, fill=(245, 215, 120), anchor="lm")

        # 스타일링 설명
        f_tag = self._get_font(22, bold=True)
        draw.text((card_x1 + 50, card_y1 + 105), f"스타일링: {m['style']}", font=f_tag, fill=(235, 230, 225))

        # 본판 보존 포인트
        f_desc = self._get_font(20, bold=False)
        draw.text((card_x1 + 50, card_y1 + 155), "• 본래 이목구비 100% 보존 • 청담동 스튜디오 핀포인트 조명 & 피부결 터치", font=f_desc, fill=(185, 170, 155))

        # ── 5. 최하단 푸터 ─────────────────────────────────────────────────────
        draw.line([(self.w // 2 - 250, 1285), (self.w // 2 + 250, 1285)], fill=(180, 150, 75, 120), width=1)
        f_footer = self._get_font(16, bold=False)
        draw.text((self.w // 2, 1310), "자연스러운 AI 프로필 화보 • AURA | aura-ai-dating.vercel.app", font=f_footer, fill=(120, 105, 95), anchor="mm")

        out_p = Path(output_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(out_p), "PNG", quality=95)
        logger.info(f"✅ [AuraLookbookBuilder] {slide_num}번 카드 저장 완료: {out_p.name}")
        return str(out_p)


if __name__ == "__main__":
    builder = AuraCardnewsS2S4LookbookBuilder()
    target_folder = Path(r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\아우라\아우라_KO_cheongdam_photo_20260930_1758")
    for s_idx in [2, 3, 4]:
        out_f = target_folder / f"slide_{s_idx}.png"
        builder.build_lookbook_slide(s_idx, str(out_f))
        print("Completed:", out_f)
