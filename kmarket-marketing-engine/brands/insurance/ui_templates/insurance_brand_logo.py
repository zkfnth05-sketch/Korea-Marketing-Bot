# -*- coding: utf-8 -*-
"""
InsuranceBrandLogo - 🛡️ [보험 리밸런스 숏폼 전용 22초 상단 고정 공식 로고 배지 모듈]
- 보험 리밸런스 숏폼 비디오 22초 전체 재생 구간 동안 우측 상단에 고정 노출되는 공식 브랜드 엠블럼
- 신뢰감 있는 프리미엄 딥네이비 & 세련된 블루/실버 방패 심볼
- 1080x1920 세로 풀HD 규격 맞춤형 투명 PNG 오버레이 렌더링
"""

import os
import sys
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = CURRENT_DIR / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
LOGO_OVERLAY_PATH = ASSETS_DIR / "insurance_logo_overlay_1080x1920.png"


class InsuranceBrandLogo:
    """🛡️ 보험 리밸런스 공식 로고 오버레이 생성/관리 레고 블록"""

    @classmethod
    def _load_font(cls, size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
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
                    continue
        return ImageFont.load_default()

    @classmethod
    def create_rounded_badge(
        cls,
        size: int = 145,
        radius: int = 18,
        border_width: int = 2,
        border_color: Tuple[int, int, int, int] = (59, 130, 246, 200),
        add_shadow: bool = True
    ) -> Image.Image:
        """
        보험 리밸런스 엠블럼 배지를 고화질 라운드 카드로 렌더링
        - 딥 네이비 글래스 배경
        - 방패(Shield) 보안 심볼 + '보험 리밸런스' 타이틀
        """
        upscale = 4
        s = size * upscale
        r = radius * upscale

        card = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        draw = ImageDraw.Draw(card)

        # 1. 딥 네이비 배경
        draw.rounded_rectangle(
            [(0, 0), (s - 1, s - 1)],
            radius=r,
            fill=(10, 18, 36, 245)
        )

        # 2. 방패(Shield) 아이콘 그리기 (상단 중앙)
        shield_cx = s // 2
        shield_top = int(s * 0.16)
        shield_w = int(s * 0.28)
        shield_h = int(s * 0.32)

        shield_points = [
            (shield_cx - shield_w // 2, shield_top),
            (shield_cx + shield_w // 2, shield_top),
            (shield_cx + shield_w // 2, shield_top + shield_h // 2),
            (shield_cx, shield_top + shield_h),
            (shield_cx - shield_w // 2, shield_top + shield_h // 2),
        ]
        draw.polygon(shield_points, fill=(37, 99, 235, 255))
        draw.line(shield_points + [shield_points[0]], fill=(96, 165, 250, 255), width=3 * upscale)

        # 방패 내부 체크 마크
        ck_start = (shield_cx - int(shield_w * 0.22), shield_top + int(shield_h * 0.45))
        ck_mid = (shield_cx - int(shield_w * 0.05), shield_top + int(shield_h * 0.62))
        ck_end = (shield_cx + int(shield_w * 0.25), shield_top + int(shield_h * 0.30))
        draw.line([ck_start, ck_mid, ck_end], fill=(255, 255, 255, 255), width=3 * upscale)

        # 3. 텍스트: '보험 리밸런스'
        font_main = cls._load_font(15 * upscale, bold=True)
        text_main = "보험 리밸런스"
        bbox_m = draw.textbbox((0, 0), text_main, font=font_main)
        tw_m = bbox_m[2] - bbox_m[0]
        tx_m = (s - tw_m) // 2
        ty_m = int(s * 0.54)
        draw.text((tx_m, ty_m), text_main, fill=(255, 255, 255, 255), font=font_main)

        # 4. 서브 텍스트: 'AI 5대 보장 진단'
        font_sub = cls._load_font(9 * upscale, bold=False)
        text_sub = "AI 5대 보장 진단"
        bbox_s = draw.textbbox((0, 0), text_sub, font=font_sub)
        tw_s = bbox_s[2] - bbox_s[0]
        tx_s = (s - tw_s) // 2
        ty_s = int(s * 0.74)
        draw.text((tx_s, ty_s), text_sub, fill=(147, 197, 253, 230), font=font_sub)

        # 5. 테두리 (블루/시안 악센트)
        if border_width > 0:
            bw = border_width * upscale
            draw.rounded_rectangle(
                [(bw // 2, bw // 2), (s - bw // 2 - 1, s - bw // 2 - 1)],
                radius=r,
                outline=border_color,
                width=bw
            )

        badge = card.resize((size, size), Image.Resampling.LANCZOS)

        # 6. 그림자 효과
        if add_shadow:
            pad = 12
            total_size = size + pad * 2
            shadow_canvas = Image.new("RGBA", (total_size, total_size), (0, 0, 0, 0))

            shadow_mask = Image.new("RGBA", (total_size, total_size), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_mask)
            shadow_draw.rounded_rectangle(
                [(pad, pad + 2), (pad + size, pad + size + 2)],
                radius=radius,
                fill=(0, 0, 0, 150)
            )
            shadow_blurred = shadow_mask.filter(ImageFilter.GaussianBlur(radius=6))

            shadow_canvas = Image.alpha_composite(shadow_canvas, shadow_blurred)
            shadow_canvas.paste(badge, (pad, pad), mask=badge)
            return shadow_canvas

        return badge

    @classmethod
    def get_overlay_1080x1920(
        cls,
        out_path: Optional[str] = None,
        badge_size: int = 145,
        margin_right: int = 45,
        margin_top: int = 65
    ) -> str:
        """
        1080x1920 세로 풀HD 전체 투명 캔버스 위에 우측 상단 보험 리밸런스 공식 배지 배치
        """
        if out_path is None:
            out_path = str(LOGO_OVERLAY_PATH)

        canvas = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        badge_img = cls.create_rounded_badge(
            size=badge_size,
            radius=18,
            border_width=2,
            border_color=(59, 130, 246, 200),
            add_shadow=True
        )

        pad = 12  # shadow padding
        pos_x = 1080 - badge_size - margin_right - pad
        pos_y = margin_top - pad

        canvas.paste(badge_img, (pos_x, pos_y), mask=badge_img)
        canvas.save(out_path, "PNG")
        return out_path


if __name__ == "__main__":
    test_p = InsuranceBrandLogo.get_overlay_1080x1920()
    print(f"✅ [InsuranceBrandLogo] 로고 오버레이 생성 완료: {test_p}")
