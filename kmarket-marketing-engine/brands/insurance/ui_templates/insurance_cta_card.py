# -*- coding: utf-8 -*-
"""
InsuranceCTACard - 🏷️ [보험 리밸런스 숏폼 엔딩 댓글 논쟁 및 네이버 공식 검색 CTA 카드]
- 1080x1920 세로 풀HD 규격
- [18초 ~ 22초] 구간 전담 독립 레고 블록
- 공식 검색어: [보험 리밸런스] (띄어쓰기 100% 필수)
- 신뢰감 있는 딥 네이비 & 블루/실버 프리미엄 핀테크 에디토리얼 디자인
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

logger = logging.getLogger("InsuranceCTACard")


class InsuranceCTACard:
    """🛡️ 보험 리밸런스 숏폼 엔딩 공식 검색어 CTA 비디오 생성기 (1080x1920)"""

    # ── 팔레트 (베이지 럭셔리 에디토리얼) ──────────────────────────────────────
    BG_BEIGE     = (247, 243, 235, 255) # #F7F3EB (Warm Champagne Beige)
    GLOW_BEIGE   = (255, 255, 255, 160)
    TEXT_BRAND   = (145, 115, 80, 255)  # Refined Bronze Gold
    TEXT_SUB     = (120, 115, 105, 255) # Warm Taupe Gray
    TEXT_HERO    = (18, 24, 38, 255)    # Deep Slate Midnight Navy
    TEXT_DEBATE  = (35, 45, 60, 255)    # Deep Slate Dark
    DIV_COLOR    = (215, 198, 180)      # Champagne Gradient Line
    PILL_BORDER  = (222, 208, 192, 255)
    PILL_SHADOW  = (195, 180, 160, 75)
    GLOW_TEXT    = (200, 185, 165, 80)
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

    def _draw_divider(self, draw: ImageDraw.Draw, y: int, color=(215, 198, 180), thickness: int = 2):
        """중앙에서 양끝으로 페이드아웃되는 샴페인 수평 구분선"""
        cx = self.w // 2
        half = 380
        for dx in range(-half, half + 1):
            x = cx + dx
            ratio = abs(dx) / half
            alpha = int(255 * (1.0 - ratio ** 1.5))
            for t in range(thickness):
                draw.point((x, y + t), fill=(color[0], color[1], color[2], alpha))

    def _draw_bg_glow(self, img: Image.Image):
        """베이지 캔버스 위 중앙 소프트 웜 글로우"""
        overlay = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        cx, cy = self.w // 2, self.h // 2
        for radius in range(480, 0, -2):
            alpha = int(160 * (1.0 - radius / 480.0) ** 1.8)
            od.ellipse(
                [cx - radius * 2, cy - radius, cx + radius * 2, cy + radius],
                fill=(255, 255, 255, alpha)
            )
        img.alpha_composite(overlay)

    def _draw_particles(self, img: Image.Image, seed: int = 101):
        """웜 샴페인 미세 파티클"""
        import random
        rng = random.Random(seed)
        overlay = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        for _ in range(50):
            x = rng.randint(60, self.w - 60)
            y = rng.randint(60, self.h - 60)
            r = rng.uniform(1.0, 2.5)
            alpha = rng.randint(25, 75)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(210, 180, 140, alpha))
        img.alpha_composite(overlay)

    def _draw_search_pill(
        self, img: Image.Image,
        center_y: int,
        search_keyword: str = "보험 리밸런스",
        glow_intensity: float = 1.0
    ):
        """네이버 공식 검색창 (고광택 화이트 알약 + 초록 N 배지 + 띄어쓰기 100% 필수)"""
        bar_y1, bar_y2 = center_y - 67, center_y + 68
        bar_x1, bar_x2 = 110, 970

        # 1. 섀도우
        pill_shadow_layer = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        psd = ImageDraw.Draw(pill_shadow_layer)
        psd.rounded_rectangle(
            [(bar_x1 - 4, bar_y1 + 4), (bar_x2 + 4, bar_y2 + 14)],
            radius=60, fill=self.PILL_SHADOW
        )
        pill_shadow_layer = pill_shadow_layer.filter(ImageFilter.GaussianBlur(radius=16))
        img.alpha_composite(pill_shadow_layer)

        # 2. 본체
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle(
            [(bar_x1, bar_y1), (bar_x2, bar_y2)],
            radius=54, fill=(255, 255, 255, 255), outline=self.PILL_BORDER, width=2
        )

        # 3. [N] 아이콘
        n_x1, n_y1 = bar_x1 + 16, bar_y1 + 14
        n_x2, n_y2 = n_x1 + 110, bar_y2 - 14
        draw.rounded_rectangle([(n_x1, n_y1), (n_x2, n_y2)], radius=22, fill=self.NAVER_GREEN)
        f_naver_n = self._get_font(50, bold=True)
        draw.text(((n_x1 + n_x2) // 2, (n_y1 + n_y2) // 2), "N", font=f_naver_n, fill=(255, 255, 255, 255), anchor="mm")

        # 4. 키워드 ('보험 리밸런스' - 띄어쓰기 필수!)
        f_search = self._get_font(48, bold=True)
        draw.text((n_x2 + 28, (bar_y1 + bar_y2) // 2), search_keyword, font=f_search, fill=(15, 23, 42, 255), anchor="lm")

    def render_cta_frame(
        self,
        topic_title: str,
        debate_question: str,
        search_keyword: str = "보험 리밸런스",
        hero_copy: str = "중복·과납 잡는 1건씩 개별 정밀 분석!",
        t_normalized: float = 0.0,
        sub_desc: str = ""
    ) -> Image.Image:
        """1080x1920 세로 풀HD 베이지 럭셔리 CTA 단일 프레임 렌더링"""
        img = Image.new("RGBA", (self.w, self.h), self.BG_BEIGE)
        self._draw_bg_glow(img)
        self._draw_particles(img, seed=101 + int(t_normalized * 10))

        draw = ImageDraw.Draw(img)

        # 1. 상단 장식선
        self._draw_divider(draw, y=260, color=self.DIV_COLOR, thickness=1)

        # 2. 브랜드 영문 서브타이틀
        f_label = self._get_font(30, bold=False)
        brand_text = "—   I N S U R E   R E B A L A N C E   —"
        draw.text((self.w // 2, 310), brand_text, font=f_label, fill=self.TEXT_BRAND, anchor="mm")

        # 3. 서브 카피
        actual_topic = sub_desc.strip() if sub_desc.strip() else topic_title
        f_sub = self._get_font(40, bold=False)
        draw.text((self.w // 2, 780), actual_topic, font=f_sub, fill=self.TEXT_SUB, anchor="mm")

        # 4. 영웅 헤드라인 (대형 타이포그래피 + 엠비언트 섀도우)
        actual_hero = hero_copy.strip()
        target_size = 80
        if len(actual_hero) > 18:
            target_size = 60
        elif len(actual_hero) > 14:
            target_size = 68
        elif len(actual_hero) > 10:
            target_size = 76
        f_hero = self._get_font(target_size, bold=True)

        glow_layer = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow_layer)
        gd.text((self.w // 2, 902), actual_hero, font=f_hero, fill=self.GLOW_TEXT, anchor="mm")
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=10))
        img.alpha_composite(glow_layer)

        draw = ImageDraw.Draw(img)
        draw.text((self.w // 2, 900), actual_hero, font=f_hero, fill=self.TEXT_HERO, anchor="mm")

        # 5. 메인 구분선
        self._draw_divider(draw, y=1020, color=self.DIV_COLOR, thickness=2)

        # 6. 논쟁 / 질문 카피
        f_cta = self._get_font(42, bold=False)
        draw.text((self.w // 2, 1085), debate_question, font=f_cta, fill=self.TEXT_DEBATE, anchor="mm")

        # 7. 네이버 공식 규격 검색창
        self._draw_search_pill(img, center_y=1237, search_keyword=search_keyword)

        # 8. 검색 유도 안내
        f_hint = self._get_font(36, bold=False)
        hint_text = "지금 네이버에서 직접 검색해보세요"
        draw.text((self.w // 2, 1380), hint_text, font=f_hint, fill=self.TEXT_SUB, anchor="mm")

        # 9. 하단 장식선
        self._draw_divider(draw, y=1650, color=self.DIV_COLOR, thickness=1)

        # 10. 공식 도메인
        f_dom = self._get_font(28, bold=False)
        dom_text = "insure-rebalance.vercel.app"
        draw.text((self.w // 2, 1700), dom_text, font=f_dom, fill=(145, 140, 130, 255), anchor="mm")

        return img.convert("RGB")

    def create_cta_segment_mp4(
        self,
        output_path: str,
        duration_sec: float = 4.0,
        fps: int = 30,
        topic_title: str = "내 보험 숨은 중복 보장 & 새는 보험료 색출",
        debate_question: str = "지금 내는 보험료에서 얼마가 새고 있을까?",
        search_keyword: str = "보험 리밸런스",
        hero_copy: str = "중복·과납 잡는 1건씩 개별 정밀 분석!"
    ) -> str:
        """4.0초 베이지 럭셔리 엔딩 CTA 비디오 MP4 생성"""
        out_p = Path(output_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        total_frames = int(duration_sec * fps)
        temp_dir = Path(tempfile.mkdtemp(prefix="insure_cta_"))
        try:
            for f_idx in range(total_frames):
                t_norm = f_idx / total_frames
                frame = self.render_cta_frame(
                    topic_title=topic_title,
                    debate_question=debate_question,
                    search_keyword=search_keyword,
                    hero_copy=hero_copy,
                    t_normalized=t_norm
                )
                frame.save(str(temp_dir / f"frame_{f_idx:04d}.jpg"), "JPEG", quality=95)

            cmd = [
                self.ffmpeg_exe, "-y",
                "-r", str(fps),
                "-i", str(temp_dir / "frame_%04d.jpg"),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-crf", "18",
                "-preset", "fast",
                str(out_p)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            logger.info(f"🏷️ [InsuranceCTACard] CTA 세그먼트 생성 완료: {out_p}")
            return str(out_p)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    cta = InsuranceCTACard()
    test_out = r"c:\Users\zkfnt\Desktop\한국 마케팅봇\kmarket-marketing-engine\scratch\test_insurance_cta_beige.mp4"
    cta.create_cta_segment_mp4(
        output_path=test_out,
        duration_sec=4.0,
        topic_title="내 보험 숨은 중복 보장 & 새는 보험료 색출",
        debate_question="지금 내는 보험료에서 얼마가 새고 있을까?",
        search_keyword="보험 리밸런스",
        hero_copy="중복·과납 잡는 1건씩 개별 정밀 분석!"
    )
    print("✅ [InsuranceCTACard] 베이지 럭셔리 테스트 CTA 비디오 생성 완료:", test_out)
