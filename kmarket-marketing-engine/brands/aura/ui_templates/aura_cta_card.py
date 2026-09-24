# -*- coding: utf-8 -*-
"""
AuraCTACard - 🏷️ [Aura 숏폼 엔딩 댓글 논쟁 유도 및 공식 네이버 검색 CTA 카드]
- 1080x1920 세로 풀HD 규격
- [18초 ~ 22초] 구간 전담 독립 레고 블록
- 디자인 철학: 검정 바탕 + 금색 포인트 / 에디토리얼 럭셔리 / 싸구려 테두리·박스 전면 배제
"""

import os
import shutil
import tempfile
import logging
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

logger = logging.getLogger("AuraCTACard")


class AuraCTACard:
    """Aura 숏폼 엔딩 공식 검색어 CTA 비디오 생성기 (1080x1920) — 럭셔리 에디토리얼 에디션"""

    # ── 팔레트 ──────────────────────────────────────────────────────────────────
    BG_BLACK    = (6, 6, 8, 255)
    GOLD_BRIGHT = (212, 175, 55, 255)
    GOLD_DARK   = (120, 90, 20, 255)
    WHITE_PURE  = (255, 255, 255, 255)
    GRAY_MID    = (130, 125, 115, 255)
    NAVER_GREEN = (3, 199, 90, 255)

    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.w = 1080
        self.h = 1920

    # ── 폰트 ────────────────────────────────────────────────────────────────────
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

    # ── 헬퍼: 금색 수평 그라디언트 선 ──────────────────────────────────────────
    def _draw_gold_divider(self, draw: ImageDraw.Draw, y: int, thickness: int = 2):
        """중앙에서 양끝으로 페이드아웃되는 황금 수평 구분선"""
        cx = self.w // 2
        half = 370  # 선 반길이
        for dx in range(-half, half + 1):
            x = cx + dx
            ratio = abs(dx) / half
            alpha = int(255 * (1.0 - ratio ** 1.4))
            r = int(self.GOLD_BRIGHT[0] * (1 - ratio) + self.GOLD_DARK[0] * ratio)
            g = int(self.GOLD_BRIGHT[1] * (1 - ratio) + self.GOLD_DARK[1] * ratio)
            b = int(self.GOLD_BRIGHT[2] * (1 - ratio) + self.GOLD_DARK[2] * ratio)
            for t in range(thickness):
                draw.point((x, y + t), fill=(r, g, b, alpha))

    # ── 헬퍼: 소프트 중앙 글로우 배경 ─────────────────────────────────────────
    def _draw_bg_glow(self, img: Image.Image):
        """순수 블랙 배경 위 중앙 극미세 웜 글로우 (시네마틱 비네팅)"""
        overlay = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        cx, cy = self.w // 2, self.h // 2
        for radius in range(350, 0, -1):
            alpha = int(28 * (1.0 - radius / 350.0) ** 2)
            d.ellipse(
                [cx - radius * 2, cy - radius, cx + radius * 2, cy + radius],
                fill=(35, 25, 5, alpha)
            )
        img.alpha_composite(overlay)

    # ── 헬퍼: 금빛 파티클 ─────────────────────────────────────────────────────
    def _draw_gold_particles(self, img: Image.Image, seed: int = 0):
        """소수의 미세 금빛 점 — 사치스러운 분위기 연출"""
        import random
        rng = random.Random(seed)
        overlay = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        for _ in range(55):
            x = rng.randint(60, self.w - 60)
            y = rng.randint(60, self.h - 60)
            r = rng.uniform(0.8, 2.4)
            alpha = rng.randint(30, 110)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(212, 175, 55, alpha))
        img.alpha_composite(overlay)

    # ── 헬퍼: 배경 글로우로 텍스트 깊이감 표현 (테두리 없음) ─────────────────
    def _draw_text_with_glow(
        self, img: Image.Image, pos: tuple, text: str,
        font, fill_color: tuple,
        glow_color=(212, 175, 55, 50), glow_radius: int = 18
    ):
        glow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow_layer)
        gd.text(pos, text, font=font, fill=glow_color, anchor="mm")
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=glow_radius))
        img.alpha_composite(glow_layer)
        d = ImageDraw.Draw(img)
        d.text(pos, text, font=font, fill=fill_color, anchor="mm")

    # ── 메인 렌더 ───────────────────────────────────────────────────────────────
    def render_cta_image(
        self,
        topic_title: str = "소개팅 탈출 전화",
        debate_question: str = "이 탈출법, 센스다 vs 너무하다?",
        search_keyword: str = "아우라AI데이팅",
        pulse: bool = False,
        frame_idx: int = 0
    ) -> Image.Image:
        """1080x1920 럭셔리 에디토리얼 엔딩 CTA 카드"""

        # 1. 칠흑 캔버스 + 웜 비네팅 글로우
        img = Image.new("RGBA", (self.w, self.h), self.BG_BLACK)
        self._draw_bg_glow(img)
        self._draw_gold_particles(img, seed=frame_idx // 15)

        draw = ImageDraw.Draw(img)

        # 2. 상단 장식 금선
        self._draw_gold_divider(draw, y=260, thickness=1)

        # 폰트 세트
        f_label   = self._get_font(30, bold=False)
        f_sub     = self._get_font(40, bold=False)
        f_hero    = self._get_font(88, bold=True)
        f_cta     = self._get_font(42, bold=False)
        f_search  = self._get_font(48, bold=True)
        f_naver_n = self._get_font(50, bold=True)

        # 3. 브랜드 라벨 (금색 고급 레터링)
        draw.text((self.w // 2, 310), "✦  A U R A  D A T I N G  ✦",
                  font=f_label, fill=self.GOLD_BRIGHT, anchor="mm")

        # 4. 서브 카피 (회색)
        draw.text((self.w // 2, 780), topic_title,
                  font=f_sub, fill=self.GRAY_MID, anchor="mm")

        # 5. 영웅 카피 (금색 볼드 + 금빛 글로우 — 진짜 골드)
        self._draw_text_with_glow(
            img, (self.w // 2, 900),
            "합법적으로 칼탈출 성공!",
            font=f_hero,
            fill_color=self.GOLD_BRIGHT,
            glow_color=(255, 220, 80, 70),
            glow_radius=30
        )

        # 6. 메인 골드 구분선
        draw = ImageDraw.Draw(img)
        self._draw_gold_divider(draw, y=1020, thickness=2)

        # 7. 논쟁 유도 텍스트
        draw.text((self.w // 2, 1085), debate_question,
                  font=f_cta, fill=self.GRAY_MID, anchor="mm")

        # 8. 네이버 검색창 (금빛 오라 + 화이트 알약)
        glow_alpha = 100 + (35 if pulse else 0)
        bar_y1, bar_y2 = 1170, 1305
        bar_x1, bar_x2 = 110, 970

        glow_overlay = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow_overlay)
        gd.rounded_rectangle(
            [(bar_x1 - 10, bar_y1 - 10), (bar_x2 + 10, bar_y2 + 10)],
            radius=62, fill=(212, 175, 55, glow_alpha)
        )
        glow_overlay = glow_overlay.filter(ImageFilter.GaussianBlur(radius=20))
        img.alpha_composite(glow_overlay)

        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle(
            [(bar_x1, bar_y1), (bar_x2, bar_y2)],
            radius=54, fill=self.WHITE_PURE
        )

        # N 배지
        n_x1, n_y1 = bar_x1 + 16, bar_y1 + 14
        n_x2, n_y2 = n_x1 + 110, bar_y2 - 14
        draw.rounded_rectangle([(n_x1, n_y1), (n_x2, n_y2)],
                                radius=22, fill=self.NAVER_GREEN)
        draw.text(((n_x1 + n_x2) // 2, (n_y1 + n_y2) // 2), "N",
                  font=f_naver_n, fill=self.WHITE_PURE, anchor="mm")

        # 검색 키워드
        draw.text((n_x2 + 28, (bar_y1 + bar_y2) // 2), search_keyword,
                  font=f_search, fill=(12, 12, 20, 255), anchor="lm")

        # 9. 검색 유도 안내
        draw.text((self.w // 2, 1380), "지금 네이버에서 직접 검색해보세요",
                  font=self._get_font(36, bold=False), fill=self.GRAY_MID, anchor="mm")

        # 10. 하단 장식 금선
        self._draw_gold_divider(draw, y=1650, thickness=1)

        # 11. 브랜드 URL (극소)
        draw.text((self.w // 2, 1700), "aura-ai-dating.vercel.app",
                  font=self._get_font(28, bold=False), fill=(70, 65, 55, 255), anchor="mm")

        return img.convert("RGB")

    # ── 비디오 생성 ────────────────────────────────────────────────────────────
    def create_cta_segment_mp4(
        self,
        output_path: str,
        duration_sec: float = 4.0,
        topic_title: str = "소개팅 탈출 전화",
        debate_question: str = "이 탈출법, 센스다 vs 너무하다?",
        search_keyword: str = "아우라AI데이팅"
    ) -> str:
        """1080x1920 4초 엔딩 CTA 비디오 생성"""
        out_p = Path(output_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"🏷️ [AuraCTACard] 엔딩 CTA 비디오 생성 시작 ({duration_sec:.2f}s) -> {out_p.name}")

        temp_dir = Path(tempfile.mkdtemp(prefix="aura_cta_frames_"))
        try:
            fps = 30
            total_frames = int(duration_sec * fps)

            for i in range(total_frames):
                pulse = (i % 20 < 10)
                frame_img = self.render_cta_image(
                    topic_title=topic_title,
                    debate_question=debate_question,
                    search_keyword=search_keyword,
                    pulse=pulse,
                    frame_idx=i
                )
                frame_path = temp_dir / f"frame_{i:04d}.png"
                frame_img.save(str(frame_path), "PNG")

            cmd = [
                self.ffmpeg_exe, "-y",
                "-framerate", str(fps),
                "-i", str(temp_dir / "frame_%04d.png"),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-t", str(duration_sec),
                str(out_p)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            logger.info(f"✨ [AuraCTACard] 엔딩 CTA 비디오 완료: {out_p.name}")
            return str(out_p)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
