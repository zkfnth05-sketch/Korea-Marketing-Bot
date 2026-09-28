# -*- coding: utf-8 -*-
"""
AuraBrandLogo - 💖 [Aura 숏폼 전용 22초 상단 고정 공식 로고 배지 모듈]
- Aura 숏폼 비디오 22초 전체 재생 구간 동안 우측 상단에 고정 노출되는 공식 브랜드 로고
- Aura 2030 MAGAZINE & OFFICIAL NAVER BLOG 골드 시그니처 엠블럼
- 1080x1920 세로 풀HD 규격 맞춤형 투명 PNG 오버레이 렌더링
"""

import os
import sys
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFilter

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = CURRENT_DIR / "assets"
LOGO_RAW_PATH = ASSETS_DIR / "aura_magazine_logo.jpg"


class AuraBrandLogo:
    """💖 Aura 2030 매거진 공식 로고 오버레이 생성/관리 레고 블록"""

    @classmethod
    def get_raw_logo_path(cls) -> Path:
        return LOGO_RAW_PATH

    @classmethod
    def create_rounded_badge(
        cls,
        size: int = 200,
        radius: int = 26,
        border_width: int = 2,
        border_color: Tuple[int, int, int, int] = (212, 168, 67, 180),
        add_shadow: bool = True
    ) -> Image.Image:
        """
        Aura 로고 이미지를 고화질 라운드 배지로 렌더링
        - 둥근 모서리 마스킹
        - 섬세한 골드 테두리 및 소프트 다크 섀도우
        """
        if not LOGO_RAW_PATH.exists():
            raise FileNotFoundError(f"Aura 로고 에셋을 찾을 수 없습니다: {LOGO_RAW_PATH}")

        # 원본 로드 및 고품질 리사이징
        raw_img = Image.open(LOGO_RAW_PATH).convert("RGBA")
        resized_logo = raw_img.resize((size, size), Image.Resampling.LANCZOS)

        # 둥근 모서리 마스크 생성
        mask = Image.new("L", (size * 4, size * 4), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle(
            [(0, 0), (size * 4 - 1, size * 4 - 1)],
            radius=radius * 4,
            fill=255
        )
        mask = mask.resize((size, size), Image.Resampling.LANCZOS)

        # 배지 이미지 생성
        badge = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        badge.paste(resized_logo, (0, 0), mask=mask)

        # 골드 테두리 그리기
        if border_width > 0:
            border_overlay = Image.new("RGBA", (size * 4, size * 4), (0, 0, 0, 0))
            draw_border = ImageDraw.Draw(border_overlay)
            draw_border.rounded_rectangle(
                [(border_width * 2, border_width * 2), (size * 4 - border_width * 2 - 1, size * 4 - border_width * 2 - 1)],
                radius=radius * 4,
                outline=border_color,
                width=border_width * 4
            )
            border_overlay = border_overlay.resize((size, size), Image.Resampling.LANCZOS)
            badge = Image.alpha_composite(badge, border_overlay)

        # 그림자 효과 부여 시 캔버스 확장
        if add_shadow:
            pad = 12
            total_size = size + pad * 2
            shadow_canvas = Image.new("RGBA", (total_size, total_size), (0, 0, 0, 0))
            
            # 소프트 블랙 그림자 마스크
            shadow_mask = Image.new("RGBA", (total_size, total_size), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_mask)
            shadow_draw.rounded_rectangle(
                [(pad, pad + 2), (pad + size, pad + size + 2)],
                radius=radius,
                fill=(0, 0, 0, 140)
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
        1080x1920 세로 풀HD 전체 투명 캔버스 위에 우측 상단 콤팩트 Aura 로고 배지 배치
        """
        if out_path is None:
            out_path = str(ASSETS_DIR / "aura_logo_overlay_1080x1920.png")

        # 1080x1920 투명 캔버스
        canvas = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        badge_img = cls.create_rounded_badge(
            size=badge_size,
            radius=18,
            border_width=2,
            border_color=(212, 168, 67, 200),
            add_shadow=True
        )

        # 우측 상단 위치 계산 (패딩 고려)
        pad = 12  # shadow padding
        pos_x = 1080 - badge_size - margin_right - pad
        pos_y = margin_top - pad

        canvas.paste(badge_img, (pos_x, pos_y), mask=badge_img)
        canvas.save(out_path, "PNG")
        return out_path


if __name__ == "__main__":
    test_path = AuraBrandLogo.get_overlay_1080x1920()
    print(f"✅ Aura 로고 오버레이 생성 완료: {test_path} ({os.path.getsize(test_path):,} bytes)")
