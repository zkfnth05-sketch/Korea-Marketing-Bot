# -*- coding: utf-8 -*-
"""
AuraBalanceMatchCardRenderer - 📱 [주제 5: 가치관 밸런스 매칭 4대 세로형 비대칭 파스텔 카드 시뮬레이터]
- 대표님 특명 100% 반영:
  1) 4번 룩북처럼 2개의 네모 카드가 비대칭(Left 아래 y=640, Right 위 y=460)으로 엇갈려 배치
  2) 카드 내부의 어색한 무늬 전면 배제 -> 글자만 극도로 정갈하고 큼직하게 정렬
  3) 4개 라운드(비용, 연락, 주말, 친구)마다 캔버스 배경과 카드 색상이 전부 다른 파스텔 톤온톤
  4) 하단 정보 박스: 핑크/파스텔 배경에 녹아드는 소프트 웜 크림 아이보리 + 골드 테두리
  5) 체크마크 깨짐 없는 PIL 벡터 드로잉
- 1080x1920 30fps MP4 (총 8.0초, 240프레임) -> presets/aura_balance_match_card_sim.mp4
"""

import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import shutil
import tempfile
import subprocess
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

class AuraBalanceMatchCardRenderer:
    def __init__(self):
        self.w = 1080
        self.h = 1920
        self.fps = 30
        self.duration_sec = 8.0
        self.total_frames = int(self.duration_sec * self.fps)  # 240 frames
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

        # 4대 라운드별 고유 파스텔 캔버스 및 카드 색상 팔레트
        self.rounds = [
            {
                "round_num": 1,
                "title_en": "D A T I N G   C O S T",
                "question": "소개팅 첫 만남 계산은?",
                "bg_pastel": (246, 198, 188),               # 소프트 피치 핑크
                "card_a_bg": (20, 65, 45),                  # 딥 세이지 그린
                "card_a_text": (255, 255, 255),
                "card_b_bg": (252, 248, 240),               # 웜 크림 아이보리
                "card_b_border": (212, 175, 55),            # 샴페인 골드
                "opt_a_main1": "칼같이 반띵",
                "opt_a_main2": "더치페이",
                "opt_a_sub": "[ 부담 없는 1/N 정산 ]",
                "opt_a_ratio": "48%",
                "opt_b_main1": "1차 사면",
                "opt_b_main2": "2차는 상대방이",
                "opt_b_sub": "[ 센스 있는 번갈아 내기 ]",
                "opt_b_ratio": "52% 선택",
                "info_title": "ROUND #01  데이트 비용 가치관",
                "info_selected": "선택: 1차 사면 2차는 상대방이 센스 있게 계산 (52% 일치)",
                "info_sub": "나와 생각 통하는 사람만 100% 매칭 • 갈등 없는 편안한 연애"
            },
            {
                "round_num": 2,
                "title_en": "C O N T A C T   S T Y L E",
                "question": "연인 간 일상 카톡 연락은?",
                "bg_pastel": (248, 235, 205),               # 소프트 버터 크림
                "card_a_bg": (65, 55, 80),                  # 딥 라벤더 슬레이트
                "card_a_text": (255, 255, 255),
                "card_b_bg": (255, 253, 248),               # 소프트 밀크 화이트
                "card_b_border": (168, 85, 247),            # 라벤더 퍼플 골드
                "opt_a_main1": "30분 이내",
                "opt_a_main2": "칼답 필수!",
                "opt_a_sub": "[ 즉각적인 애정 확인 ]",
                "opt_a_ratio": "38%",
                "opt_b_main1": "일할 땐 집중",
                "opt_b_main2": "자유롭게 몰아서",
                "opt_b_sub": "[ 서로의 일상 존중 ]",
                "opt_b_ratio": "62% 선택",
                "info_title": "ROUND #02  연락 빈도 가치관",
                "info_selected": "선택: 일할 땐 자유롭게, 쉴 때 정성 연락 (62% 일치)",
                "info_sub": "답장 압박 없는 건강한 연애 • 신뢰 기반의 성숙한 소통"
            },
            {
                "round_num": 3,
                "title_en": "W E E K E N D   L I F E",
                "question": "주말에 더 선호하는 데이트는?",
                "bg_pastel": (215, 235, 222),               # 소프트 세이지 민트
                "card_a_bg": (42, 95, 78),                  # 어둡지 않은 화사한 미디엄 세이지 틸
                "card_a_border": (60, 130, 105),
                "card_a_text": (255, 255, 255),
                "card_b_bg": (250, 246, 238),               # 페일 샌드 크림
                "card_b_border": (245, 158, 11),            # 웜 앰버 골드
                "opt_a_main1": "집콕 넷플릭스",
                "opt_a_main2": "홈캉스 힐링",
                "opt_a_sub": "[ 편안한 집 데이트 ]",
                "opt_a_ratio": "45%",
                "opt_b_main1": "야외 핫플 카페",
                "opt_b_main2": "감성 테라스 투어",
                "opt_b_sub": "[ 낭만적인 야외 데이트 ]",
                "opt_b_ratio": "55% 선택",
                "info_title": "ROUND #03  주말 라이프 가치관",
                "info_selected": "선택: 야외 감성 카페 & 맛집 탐방 선호 (55% 일치)",
                "info_sub": "주말 취향 100% 일치 • 매주 기다려지는 설레는 데이트"
            },
            {
                "round_num": 4,
                "title_en": "F R I E N D S H I P",
                "question": "내 애인의 남사친/여사친 허용은?",
                "bg_pastel": (210, 228, 242),               # 소프트 파우더 스카이블루
                "card_a_bg": (55, 80, 120),                 # 칙칙한 플럼 대신 세련되고 밝은 소프트 데님 블루
                "card_a_border": (75, 110, 160),
                "card_a_text": (255, 255, 255),
                "card_b_bg": (253, 252, 250),               # 화이트 아이스 크림
                "card_b_border": (244, 114, 182),           # 로즈 골드
                "opt_a_main1": "단둘이 식사/커피",
                "opt_a_main2": "쿨하게 OK",
                "opt_a_sub": "[ 오랜 친구는 인정 ]",
                "opt_a_ratio": "24%",
                "opt_b_main1": "단둘이 만나는 건",
                "opt_b_main2": "절대 불가!",
                "opt_b_sub": "[ 연인 사이 최소한의 예의 ]",
                "opt_b_ratio": "76% 선택",
                "info_title": "ROUND #04  이성 친구 가치관",
                "info_selected": "선택: 단둘 만남 절대 불가 • 상호 배려 원칙 (76% 일치)",
                "info_sub": "불안감 제로 안심 연애 • 오직 서로에게만 집중하는 만남"
            }
        ]

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

    def _draw_vector_check(self, draw_obj, cx, cy, size=20, color=(255, 255, 255), width=3):
        """PIL 선으로 직접 그리는 깨짐 없는 완벽한 체크마크"""
        p1 = (cx - size // 2, cy)
        p2 = (cx - size // 6, cy + size // 2)
        p3 = (cx + size // 2, cy - size // 2)
        draw_obj.line([p1, p2, p3], fill=color, width=width, joint="curve")

    def _create_pastel_canvas(self, base_color: Tuple[int, int, int]) -> Image.Image:
        """라운드별 파스텔 캔버스 및 부드러운 웜 그라데이션"""
        r, g, b = base_color
        arr = np.zeros((self.h, self.w, 4), dtype=np.uint8)
        for y in range(self.h):
            ratio = y / self.h
            arr[y, :, 0] = np.clip(int(r - ratio * 8), 0, 255)
            arr[y, :, 1] = np.clip(int(g - ratio * 10), 0, 255)
            arr[y, :, 2] = np.clip(int(b - ratio * 12), 0, 255)
            arr[y, :, 3] = 255
        return Image.fromarray(arr, mode="RGBA")

    def _apply_drop_shadow(self, canvas: Image.Image, frame: Image.Image, x: int, y: int, radius: int = 32, blur_rad: int = 34, offset=(18, 28), shadow_alpha: int = 110):
        """4번 룩북 다중 레이어 소프트 3D 드롭 섀도우"""
        fw, fh = frame.size
        pad = blur_rad * 3
        full_shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))

        s_img = Image.new("RGBA", (fw + pad * 2, fh + pad * 2), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(s_img)
        s_draw.rounded_rectangle([(pad + offset[0], pad + offset[1]), (pad + fw + offset[0], pad + fh + offset[1])], radius=radius, fill=(40, 25, 20, shadow_alpha))
        s_blurred = s_img.filter(ImageFilter.GaussianBlur(blur_rad))
        full_shadow.paste(s_blurred, (x - pad, y - pad), s_blurred)

        canvas = Image.alpha_composite(canvas, full_shadow)
        canvas.paste(frame, (x, y), frame)
        return canvas

    def render_round_card_pair(self, r_data: Dict[str, Any]) -> Tuple[Image.Image, Image.Image]:
        """무늬 없는 극도로 깔끔한 비대칭 2대 세로형 네모 카드 렌더링"""
        cw, ch = 450, 680
        radius = 32

        # 1. 왼쪽 카드 (Option A)
        card_a = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ca_draw = ImageDraw.Draw(card_a)
        ca_bg = r_data["card_a_bg"]
        ca_border = r_data.get("card_a_border", (ca_bg[0] + 25, ca_bg[1] + 25, ca_bg[2] + 25))
        ca_draw.rounded_rectangle([(0, 0), (cw, ch)], radius=radius, fill=ca_bg + (255,), outline=ca_border + (255,), width=2)
        ca_draw.rounded_rectangle([(18, 18), (cw - 19, ch - 19)], radius=radius - 8, outline=ca_border + (140,), width=1)

        f_badge = self._get_font(26, bold=True)
        f_main1 = self._get_font(42, bold=True)
        f_main2 = self._get_font(42, bold=True)
        f_subtxt = self._get_font(22, bold=False)
        f_ratio = self._get_font(34, bold=True)

        # OPTION A 뱃지
        badge_bg = (max(0, ca_bg[0] - 15), max(0, ca_bg[1] - 15), max(0, ca_bg[2] - 15), 220)
        ca_draw.rounded_rectangle([(cw // 2 - 85, 130), (cw // 2 + 85, 178)], radius=24, fill=badge_bg, outline=ca_border + (255,), width=2)
        ca_draw.text((cw // 2, 154), "OPTION A", font=f_badge, fill=(225, 235, 230), anchor="mm")

        # 메인 글자
        ca_draw.text((cw // 2, 290), r_data["opt_a_main1"], font=f_main1, fill=r_data["card_a_text"], anchor="mm")
        ca_draw.text((cw // 2, 355), r_data["opt_a_main2"], font=f_main2, fill=r_data["card_a_text"], anchor="mm")
        ca_draw.line([(cw // 2 - 50, 420), (cw // 2 + 50, 420)], fill=ca_border, width=2)
        ca_draw.text((cw // 2, 465), r_data["opt_a_sub"], font=f_subtxt, fill=(210, 225, 220), anchor="mm")

        # 투표율 박스
        ca_draw.rounded_rectangle([(cw // 2 - 90, 535), (cw // 2 + 90, 600)], radius=22, fill=badge_bg, outline=ca_border + (255,), width=2)
        ca_draw.text((cw // 2, 568), r_data["opt_a_ratio"], font=f_ratio, fill=(230, 240, 235), anchor="mm")

        # 2. 오른쪽 카드 (Option B - 선택 하이라이트)
        card_b = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        cb_draw = ImageDraw.Draw(card_b)
        b_border = r_data["card_b_border"]
        cb_draw.rounded_rectangle([(0, 0), (cw, ch)], radius=radius, fill=r_data["card_b_bg"] + (255,), outline=(225, 215, 195, 255), width=2)
        cb_draw.rounded_rectangle([(3, 3), (cw - 4, ch - 4)], radius=radius - 1, outline=b_border + (255,), width=3)
        cb_draw.rounded_rectangle([(18, 18), (cw - 19, ch - 19)], radius=radius - 8, outline=b_border + (160,), width=1)

        # OPTION B 뱃지
        cb_draw.rounded_rectangle([(cw // 2 - 85, 130), (cw // 2 + 85, 178)], radius=24, fill=b_border + (255,))
        cb_draw.text((cw // 2, 154), "OPTION B", font=f_badge, fill=(255, 255, 255), anchor="mm")

        # 메인 글자
        cb_draw.text((cw // 2, 290), r_data["opt_b_main1"], font=f_main1, fill=(45, 30, 20), anchor="mm")
        cb_draw.text((cw // 2, 355), r_data["opt_b_main2"], font=f_main2, fill=(45, 30, 20), anchor="mm")
        cb_draw.line([(cw // 2 - 50, 420), (cw // 2 + 50, 420)], fill=b_border, width=2)
        cb_draw.text((cw // 2, 465), r_data["opt_b_sub"], font=f_subtxt, fill=(120, 90, 75), anchor="mm")

        # 선택 완료 투표율
        cb_draw.rounded_rectangle([(cw // 2 - 110, 535), (cw // 2 + 110, 600)], radius=22, fill=b_border + (255,))
        self._draw_vector_check(cb_draw, cw // 2 - 75, 568, size=20, color=(255, 255, 255), width=3)
        cb_draw.text((cw // 2 + 15, 568), r_data["opt_b_ratio"], font=f_ratio, fill=(255, 255, 255), anchor="mm")

        return card_a, card_b

    def render_round_frame(self, round_idx: int) -> Image.Image:
        """한 라운드의 풀HD 프레임 완성 (파스텔 캔버스 + 비대칭 카드 + 크림 정보박스)"""
        r_data = self.rounds[round_idx]
        canvas = self._create_pastel_canvas(r_data["bg_pastel"])
        draw = ImageDraw.Draw(canvas)

        f_en_head = self._get_font(28, bold=True)
        f_title = self._get_font(46, bold=True)
        f_sub = self._get_font(24, bold=False)

        # 상단 헤더
        draw.text((self.w // 2, 130), f"V E R T I C A L   B A L A N C E   •   {r_data['title_en']}", font=f_en_head, fill=(120, 75, 65), anchor="mm")
        draw.text((self.w // 2, 195), r_data["question"], font=f_title, fill=(45, 25, 20), anchor="mm")
        draw.text((self.w // 2, 255), "나의 솔직한 가치관을 선택해 보세요 • AURA LOUNGE", font=f_sub, fill=(115, 80, 70), anchor="mm")
        draw.line([(self.w // 2 - 140, 305), (self.w // 2 + 140, 305)], fill=(175, 110, 100), width=2)

        # 비대칭 2대 네모 카드 배치 (왼쪽 아래 y=640, 오른쪽 위 y=460)
        card_a, card_b = self.render_round_card_pair(r_data)
        canvas = self._apply_drop_shadow(canvas, card_a, 70, 640, radius=32, blur_rad=32, offset=(14, 24), shadow_alpha=110)
        canvas = self._apply_drop_shadow(canvas, card_b, 560, 460, radius=32, blur_rad=36, offset=(18, 28), shadow_alpha=125)

        # 중앙 VS 라벨
        v_draw = ImageDraw.Draw(canvas)
        f_vs = self._get_font(32, bold=True)
        vs_x, vs_y = self.w // 2, 590
        v_draw.ellipse([(vs_x - 36, vs_y - 36), (vs_x + 36, vs_y + 36)], fill=(255, 255, 255, 250), outline=(210, 160, 150, 255), width=2)
        v_draw.text((vs_x, vs_y), "VS", font=f_vs, fill=(155, 75, 65), anchor="mm")

        # 하단 소프트 웜 크림 정보 박스
        info_box_y = 1430
        info_w, info_h = self.w - 140, 235
        ix1, iy1, ix2, iy2 = 70, info_box_y, self.w - 70, info_box_y + info_h

        # 박스 그림자
        info_shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        is_img = Image.new("RGBA", (info_w + 100, info_h + 100), (0, 0, 0, 0))
        is_draw = ImageDraw.Draw(is_img)
        is_draw.rounded_rectangle([(50, 60), (50 + info_w, 60 + info_h)], radius=32, fill=(40, 20, 15, 65))
        is_blurred = is_img.filter(ImageFilter.GaussianBlur(25))
        info_shadow.paste(is_blurred, (ix1 - 50, iy1 - 50), is_blurred)
        canvas = Image.alpha_composite(canvas, info_shadow)

        # 크림 아이보리 박스
        v_draw = ImageDraw.Draw(canvas)
        v_draw.rounded_rectangle([(ix1, iy1), (ix2, iy2)], radius=32, fill=(254, 250, 244, 245), outline=(212, 175, 55, 240), width=2)

        f_round = self._get_font(32, bold=True)
        f_desc1 = self._get_font(26, bold=False)
        f_desc2 = self._get_font(24, bold=False)

        v_draw.text((115, iy1 + 45), r_data["info_title"], font=f_round, fill=(155, 45, 35), anchor="lm")
        v_draw.text((115, iy1 + 105), r_data["info_selected"], font=f_desc1, fill=(45, 30, 20), anchor="lm")
        self._draw_vector_check(v_draw, 125, iy1 + 168, size=18, color=(40, 140, 90), width=3)
        v_draw.text((150, iy1 + 168), r_data["info_sub"], font=f_desc2, fill=(105, 75, 65), anchor="lm")

        return canvas.convert("RGB")

    def render_full_simulation_video(self, output_mp4_path: str) -> str:
        """4개 라운드가 각 2.0초씩(총 8초, 240프레임) 파스텔 톤온톤으로 전환되는 비디오 렌더링"""
        out_p = Path(output_mp4_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        temp_dir = Path(tempfile.mkdtemp(prefix="aura_balance_pastel_"))

        try:
            # 4개 라운드 이미지 사전 렌더링
            round_frames = [self.render_round_frame(i) for i in range(4)]

            frames_per_round = 60  # 2.0s * 30fps

            for i in range(self.total_frames):
                r_idx = min(3, i // frames_per_round)
                frame_img = round_frames[r_idx]
                f_path = temp_dir / f"frame_{i:04d}.png"
                frame_img.save(str(f_path), "PNG")

            # FFmpeg 컴파일
            cmd = [
                self.ffmpeg_exe, "-y",
                "-framerate", str(self.fps),
                "-i", str(temp_dir / "frame_%04d.png"),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-crf", "18",
                "-preset", "fast",
                str(out_p)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return str(out_p)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    renderer = AuraBalanceMatchCardRenderer()
    preset_target = Path(r"C:\Users\zkfnt\Desktop\한국 마케팅봇\kmarket-marketing-engine\brands\aura\ui_templates\presets\aura_balance_match_card_sim.mp4")
    print("🎬 [AuraBalanceMatchCardRenderer] 4대 파스텔 밸런스 카드 시뮬레이션 MP4 렌더링 시작...")
    out = renderer.render_full_simulation_video(str(preset_target))
    print("🎉 [완료] 프리셋 비디오 생성 완료:", out)
