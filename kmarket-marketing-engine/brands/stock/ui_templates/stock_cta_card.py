# -*- coding: utf-8 -*-
"""
StockCTACard - 🏷️ [StockMaster AI 숏폼 엔딩 댓글 논쟁 및 네이버 공식 검색 CTA 카드]
- 1080x1920 세로 풀HD 규격
- [18초 ~ 22초] 구간 전담 독립 레고 블록
- 공식 검색어: [스톡마스터 AI] (띄어쓰기 100% 필수)
- 신뢰감 있는 딥 네이비 & 일렉트릭 블루/골드 프리미엄 핀테크 에디토리얼 디자인
"""

import os
import sys
import shutil
import tempfile
import logging
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
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

    # ── 팔레트 (다크 핀테크 & 샴페인 골드 에디토리얼) ──────────────────────────────────
    BG_DARK      = (10, 15, 29, 255)    # Deep Midnight Navy
    GLOW_BLUE    = (37, 99, 235, 120)   # Electric Blue Glow
    TEXT_BRAND   = (96, 165, 250, 255)  # Light Blue Accents
    TEXT_SUB     = (148, 163, 184, 255) # Slate Gray
    TEXT_HERO    = (248, 250, 252, 255) # Pure White
    TEXT_DEBATE  = (226, 232, 240, 255) # Light Slate
    DIV_COLOR    = (51, 65, 85)         # Slate Divider Line
    PILL_BORDER  = (59, 130, 246, 255)  # Blue Border
    PILL_BG      = (15, 23, 42, 240)    # Slate Dark Container
    NAVER_GREEN  = (3, 199, 90, 255)

    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.w = 1080
        self.h = 1920

    def _get_font(self, size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
        candidates = [
            r"C:\Windows\Fonts\malgunbd.ttf" if bold else r"C:\Windows\Fonts\malgun.ttf",
            r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arialbd.ttf"  if bold else r"C:\Windows\Fonts\arial.ttf",
        ]
        for p in candidates:
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    continue
        return ImageFont.load_default()

    def _draw_divider(self, draw: ImageDraw.Draw, y: int, color=(51, 65, 85), thickness: int = 2):
        """중앙에서 양끝으로 페이드아웃되는 수평 구분선"""
        cx = self.w // 2
        half = 380
        for dx in range(-half, half + 1):
            x = cx + dx
            ratio = abs(dx) / half
            alpha = int(255 * (1.0 - ratio ** 1.5))
            for t in range(thickness):
                draw.point((x, y + t), fill=(color[0], color[1], color[2], alpha))

    def _draw_bg_glow(self, img: Image.Image):
        """다크 캔버스 위 중앙 소프트 블루 글로우"""
        overlay = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        cx, cy = self.w // 2, self.h // 2
        for radius in range(480, 0, -2):
            alpha = int(120 * (1.0 - radius / 480.0) ** 1.8)
            od.ellipse(
                [cx - radius * 2, cy - radius, cx + radius * 2, cy + radius],
                fill=(37, 99, 235, alpha)
            )
        img.alpha_composite(overlay)

    def render_cta_card_image(
        self,
        topic_title: str = "삼성전자 vs SK하이닉스 AI 반도체 HBM 수급",
        debate_question: str = "HBM 승자는 삼성전자 vs SK하이닉스?",
        search_keyword: str = "스톡마스터 AI",
        hero_copy: str = "실시간 AI 퀀트 수급 분석!"
    ) -> Image.Image:
        """1080x1920 세로 풀HD 프리미엄 핀테크 CTA 프레임 렌더링"""
        img = Image.new("RGBA", (self.w, self.h), self.BG_DARK)
        self._draw_bg_glow(img)
        draw = ImageDraw.Draw(img)

        # ── 폰트 세팅 ─────────────────────────────────────────────
        font_brand   = self._get_font(28, bold=True)
        font_sub     = self._get_font(26, bold=False)
        font_hero    = self._get_font(46, bold=True)
        font_debate  = self._get_font(36, bold=True)
        font_naver_n = self._get_font(42, bold=True)
        font_kw      = self._get_font(46, bold=True)
        font_cta_sub = self._get_font(28, bold=False)

        # 1. 상단 브랜드 뱃지 (y=320)
        draw.text((self.w // 2, 320), "STOCKMASTER AI • 퀀트 알고리즘 엔진", fill=self.TEXT_BRAND, font=font_brand, anchor="mm")
        draw.text((self.w // 2, 370), "빅테크 & 국내 대형주 실시간 AI 밸류에이션", fill=self.TEXT_SUB, font=font_sub, anchor="mm")

        self._draw_divider(draw, y=430, color=self.DIV_COLOR, thickness=2)

        # 2. 메인 히어로 카피 (y=560)
        draw.text((self.w // 2, 560), hero_copy, fill=self.TEXT_HERO, font=font_hero, anchor="mm")

        # 3. 댓글 토론 질문 박스 (y=740)
        box_w, box_h = 880, 140
        bx1 = (self.w - box_w) // 2
        by1 = 740
        draw.rounded_rectangle([bx1, by1, bx1 + box_w, by1 + box_h], radius=24, fill=self.PILL_BG, outline=self.PILL_BORDER, width=2)
        draw.text((self.w // 2, by1 + box_h // 2), f"Q. {debate_question}", fill=self.TEXT_DEBATE, font=font_debate, anchor="mm")

        self._draw_divider(draw, y=980, color=self.DIV_COLOR, thickness=2)

        # 4. 네이버 공식 검색 CTA 박스 (y=1120)
        pill_w, pill_h = 880, 160
        px1 = (self.w - pill_w) // 2
        py1 = 1120
        draw.rounded_rectangle([px1, py1, px1 + pill_w, py1 + pill_h], radius=32, fill=(255, 255, 255, 255), outline=self.NAVER_GREEN, width=4)

        # 네이버 N 아이콘 (y=1170)
        n_size = 76
        nx1 = px1 + 45
        ny1 = py1 + (pill_h - n_size) // 2
        draw.rounded_rectangle([nx1, ny1, nx1 + n_size, ny1 + n_size], radius=18, fill=self.NAVER_GREEN)
        draw.text((nx1 + n_size // 2, ny1 + n_size // 2), "N", fill=(255, 255, 255, 255), font=font_naver_n, anchor="mm")

        # 검색어 텍스트
        draw.text((nx1 + n_size + 35, py1 + pill_h // 2), f"'{search_keyword}'", fill=(15, 23, 42, 255), font=font_kw, anchor="lm")

        # 우측 검색 버튼
        btn_w, btn_h = 130, 80
        btn_x1 = px1 + pill_w - btn_w - 30
        btn_y1 = py1 + (pill_h - btn_h) // 2
        draw.rounded_rectangle([btn_x1, btn_y1, btn_x1 + btn_w, btn_y1 + btn_h], radius=16, fill=self.NAVER_GREEN)
        draw.text((btn_x1 + btn_w // 2, btn_y1 + btn_h // 2), "검색", fill=(255, 255, 255, 255), font=self._get_font(32, bold=True), anchor="mm")

        # 5. 하단 안내 문구 (y=1340)
        draw.text((self.w // 2, 1340), "네이버 검색창에 [스톡마스터 AI]를 검색해보세요!", fill=self.TEXT_SUB, font=font_cta_sub, anchor="mm")
        draw.text((self.w // 2, 1390), "실시간 퀀트 분석 및 뇌동매매 방지 리포트 무료", fill=self.TEXT_BRAND, font=font_brand, anchor="mm")

        return img.convert("RGB")

    def create_cta_segment_mp4(
        self,
        output_path: str,
        duration_sec: float = 1.0,
        topic_title: str = "삼성전자 vs SK하이닉스 HBM 수급",
        debate_question: str = "HBM 승자는 삼성전자 vs SK하이닉스?",
        search_keyword: str = "스톡마스터 AI",
        hero_copy: str = "실시간 AI 퀀트 수급 분석!"
    ) -> str:
        """1초 분량의 1080x1920 세로 풀HD CTA MP4 비디오 렌더링"""
        out_p = Path(output_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        card_img = self.render_cta_card_image(
            topic_title=topic_title,
            debate_question=debate_question,
            search_keyword=search_keyword,
            hero_copy=hero_copy
        )

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_img:
            tmp_img_path = tmp_img.name
            card_img.save(tmp_img_path, format="PNG")

        try:
            cmd = [
                self.ffmpeg_exe, "-y",
                "-loop", "1",
                "-i", tmp_img_path,
                "-t", f"{duration_sec:.2f}",
                "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30",
                "-c:v", "libx264",
                "-tune", "stillimage",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                str(out_p)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            logger.info(f"🏷️ [StockCTACard] CTA 세그먼트 생성 완료: {out_p}")
        finally:
            if os.path.exists(tmp_img_path):
                try:
                    os.remove(tmp_img_path)
                except Exception:
                    pass

        return str(out_p)
