# -*- coding: utf-8 -*-
"""
AuraAppSimulator - 📱 [Aura 웹앱 실시간 시뮬레이션 고화질 8초 녹화 및 렌더링 모듈]
- EasyTaxAppRecorder의 역할을 100% 전담하는 Aura 전용 독립 레고 블록
- 1080x1920 세로 풀HD 규격
- 주제 1 (소개팅 긴급 탈출 전화):
  1) [0.0s ~ 2.5s] Aura 앱 안심 라운지 (1분 뒤 긴급 자동 수신 예약 ON)
  2) [2.5s ~ 5.5s] 실제 전화 수신 벨소리 화면 (팀장님 긴급 호출, 벨소리/진동)
  3) [5.5s ~ 8.0s] 통화 연결 및 화면 탈출 대본 표출 ("어 김대리! 지금 당장 회사 복귀해!")
"""

import os
import shutil
import tempfile
import logging
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

logger = logging.getLogger("AuraAppSimulator")


class AuraAppSimulator:
    """Aura 모바일 앱 실시간 시뮬레이션 비디오 생성기 (1080x1920)"""

    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.w = 1080
        self.h = 1920

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
                    continue
        return ImageFont.load_default()

    def record_simulation_clip(
        self,
        topic_id: int = 1,
        duration_sec: float = 8.0,
        output_mp4_path: str = "aura_app_sim.mp4"
    ) -> str:
        """Aura 앱 8초 시뮬레이션 클립을 1080x1920 MP4로 렌더링"""
        out_p = Path(output_mp4_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        if topic_id == 2:
            preset_file = Path(__file__).parent / "presets" / "aura_subtitles_call_sim.mp4"
        else:
            preset_file = Path(__file__).parent / "presets" / "aura_escape_call_sim.mp4"

        if preset_file.exists() and preset_file.stat().st_size > 0:
            logger.info(f"✨ [AuraAppSimulator] 주제 {topic_id} 100% 실기기 브라우저 영구 녹화 프리셋 활용: {preset_file.name} -> {out_p.name}")
            shutil.copyfile(preset_file, out_p)
            return str(out_p)

        logger.info(f"📱 [AuraAppSimulator] 8초 앱 시뮬레이션 렌더링 시작 (주제={topic_id}, {duration_sec:.2f}s) -> {out_p.name}")

        temp_dir = Path(tempfile.mkdtemp(prefix="aura_sim_frames_"))
        try:
            # 30fps 기준으로 프레임 생성
            fps = 30
            total_frames = int(duration_sec * fps)
            p1_end = int(total_frames * 0.32)  # ~2.5s
            p2_end = int(total_frames * 0.68)  # ~5.5s

            # 3단계 핵심 키프레임 베이스 이미지 렌더링
            img_p1 = self._render_phase1_reservation()
            img_p2 = self._render_phase2_incoming_call()
            img_p3 = self._render_phase3_script_display()

            for i in range(total_frames):
                if i < p1_end:
                    frame_img = img_p1
                elif i < p2_end:
                    # 벨소리 수신 진동 깜빡임 연출
                    frame_img = self._render_phase2_incoming_call(pulse=(i % 10 < 5))
                else:
                    frame_img = img_p3

                frame_path = temp_dir / f"frame_{i:04d}.png"
                frame_img.save(str(frame_path), "PNG")

            # FFmpeg로 1080x1920 30fps MP4 컴파일
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
            logger.info(f"✨ [AuraAppSimulator] 앱 시연 비디오 렌더링 완료: {out_p.name}")
            return str(out_p)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _render_phone_frame(self) -> Tuple[Image.Image, ImageDraw.ImageDraw]:
        """고급스러운 다크 모드 1080x1920 스마트폰 프레임 생성"""
        img = Image.new("RGBA", (self.w, self.h), (11, 15, 25, 255))
        draw = ImageDraw.Draw(img)

        # 은은한 배경 앰비언트 글로우
        draw.ellipse([(140, 200), (940, 1000)], fill=(30, 41, 59, 120))
        draw.ellipse([(200, 800), (880, 1600)], fill=(244, 114, 182, 35))

        # 스마트폰 본체 섀시 (가로 940, 세로 1740)
        bx1, by1, bx2, by2 = 70, 90, 1010, 1830
        draw.rounded_rectangle([(bx1, by1), (bx2, by2)], radius=56, fill=(15, 23, 42, 255), outline=(51, 65, 85, 255), width=4)

        # 상단 노치 / 다이내믹 아일랜드
        draw.rounded_rectangle([(self.w // 2 - 110, by1 + 22), (self.w // 2 + 110, by1 + 62)], radius=20, fill=(0, 0, 0, 255))
        draw.ellipse([(self.w // 2 + 65, by1 + 35), (self.w // 2 + 85, by1 + 55)], fill=(30, 41, 59, 255))

        # 상단 상태 표시줄
        f_stat = self._get_font(26, bold=True)
        draw.text((bx1 + 50, by1 + 32), "09:41", font=f_stat, fill=(255, 255, 255, 230))
        draw.text((bx2 - 120, by1 + 32), "5G 􀛨", font=f_stat, fill=(255, 255, 255, 230))

        # Aura 네비게이션 헤더
        draw.line([(bx1, by1 + 105), (bx2, by1 + 105)], fill=(30, 41, 59, 200), width=2)
        f_brand = self._get_font(34, bold=True)
        draw.text((self.w // 2, by1 + 135), "💖 Aura Lounge • 안심 케어", font=f_brand, fill=(244, 114, 182, 255), anchor="mm")

        # 하단 홈 인디케이터 바
        draw.rounded_rectangle([(self.w // 2 - 120, by2 - 32), (self.w // 2 + 120, by2 - 20)], radius=6, fill=(255, 255, 255, 180))

        return img, draw

    def _render_phase1_reservation(self) -> Image.Image:
        """1단계: 소개팅 긴급 탈출 전화 가동 및 1분 뒤 예약"""
        img, draw = self._render_phone_frame()
        f_title = self._get_font(42, bold=True)
        f_mid = self._get_font(30, bold=True)
        f_sub = self._get_font(24, bold=False)
        f_cnt = self._get_font(68, bold=True)

        # 메인 카드 박스
        card = (120, 290, 960, 800)
        draw.rounded_rectangle([(card[0], card[1]), (card[2], card[3])], radius=32, fill=(30, 41, 59, 240), outline=(239, 68, 68, 255), width=3)
        draw.text((self.w // 2, 340), "🚨 [소개팅 긴급 탈출 전화]", font=f_title, fill=(248, 113, 113, 255), anchor="mt")
        draw.text((self.w // 2, 405), "소개팅 빌런 만났을 때 화장실에서 1초 만에 예약!", font=f_sub, fill=(203, 213, 225, 255), anchor="mt")

        # 토글 버튼 및 상태 박스
        draw.rounded_rectangle([(160, 470), (920, 560)], radius=20, fill=(15, 23, 42, 255))
        draw.text((195, 515), "긴급 수신 타이머 설정", font=f_mid, fill=(255, 255, 255, 255), anchor="lm")
        draw.rounded_rectangle([(770, 490), (890, 540)], radius=25, fill=(34, 197, 94, 255))
        draw.ellipse([(835, 495), (880, 535)], fill=(255, 255, 255, 255))
        draw.text((800, 515), "ON", font=self._get_font(20, bold=True), fill=(255, 255, 255, 255), anchor="mm")

        # 카운트다운 타이머 박스
        draw.rounded_rectangle([(160, 590), (920, 750)], radius=24, fill=(17, 24, 39, 255), outline=(74, 222, 128, 200), width=2)
        draw.text((self.w // 2, 630), "⏳ 1분 뒤 자동 전화 수신 대기 중", font=f_sub, fill=(74, 222, 128, 255), anchor="mt")
        draw.text((self.w // 2, 690), "00 : 59", font=f_cnt, fill=(255, 255, 255, 255), anchor="mt")

        # 하단 안내 카드
        draw.rounded_rectangle([(120, 850), (960, 1680)], radius=32, fill=(24, 32, 47, 220), outline=(51, 65, 85, 200), width=2)
        draw.text((170, 900), "💡 안전한 소개팅 탈출 3단계 공식", font=f_mid, fill=(251, 191, 36, 255))
        steps = [
            ("1. 화장실 이동", "상대 모르게 화장실로 가서 아우라 앱 접속"),
            ("2. 1분 예약 터치", "자리로 돌아와 대화하는 중 1분 뒤 실제 벨소리 울림"),
            ("3. 대본 읽고 칼탈출", "팀장님 음성과 화면에 뜨는 긴급 대본 읽고 자연 퇴장!"),
        ]
        sy = 970
        for title, desc in steps:
            draw.text((170, sy), f"• {title}", font=f_mid, fill=(255, 255, 255, 255))
            draw.text((195, sy + 45), desc, font=f_sub, fill=(148, 163, 184, 255))
            sy += 120

        return img

    def _render_phase2_incoming_call(self, pulse: bool = False) -> Image.Image:
        """2단계: 실제 벨소리 및 팀장님 긴급 전화 수신 화면"""
        img, draw = self._render_phone_frame()
        f_title = self._get_font(44, bold=True)
        f_sub = self._get_font(28, bold=False)
        f_badge = self._get_font(24, bold=True)

        # 전화 수신 풀스크린 컨테이너
        draw.rounded_rectangle([(110, 270), (970, 1720)], radius=36, fill=(10, 15, 30, 255), outline=(59, 130, 246, 255) if pulse else (30, 41, 59, 255), width=3)

        # 안심 가상 전화 뱃지
        draw.rounded_rectangle([(self.w // 2 - 190, 310), (self.w // 2 + 190, 365)], radius=20, fill=(30, 58, 138, 220), outline=(96, 165, 250, 255), width=2)
        draw.text((self.w // 2, 337), "🛡️ Aura 안심 가상 비상 수신", font=f_badge, fill=(191, 219, 254, 255), anchor="mm")

        # 벨소리 진동 파동 원
        cy = 580
        if pulse:
            draw.ellipse([(self.w // 2 - 140, cy - 140), (self.w // 2 + 140, cy + 140)], outline=(244, 114, 182, 120), width=4)
            draw.ellipse([(self.w // 2 - 170, cy - 170), (self.w // 2 + 170, cy + 170)], outline=(239, 68, 68, 80), width=3)

        # 프로필 아바타
        draw.ellipse([(self.w // 2 - 110, cy - 110), (self.w // 2 + 110, cy + 110)], fill=(30, 41, 59, 255), outline=(255, 255, 255, 255), width=4)
        draw.text((self.w // 2, cy), "👔", font=self._get_font(96), anchor="mm")

        # 발신자 정보
        draw.text((self.w // 2, 740), "직장 상사 (팀장님)", font=f_title, fill=(255, 255, 255, 255), anchor="mt")
        draw.text((self.w // 2, 805), "실제 전화 벨소리 울림 중 🎵", font=f_sub, fill=(244, 114, 182, 255), anchor="mt")

        # 수신 슬라이더 및 통화 버튼
        by = 1380
        # 거절 버튼
        draw.ellipse([(240, by), (380, by + 140)], fill=(239, 68, 68, 255))
        draw.text((310, by + 70), "📞", font=self._get_font(54), fill=(255, 255, 255, 255), anchor="mm")
        draw.text((310, by + 165), "거절", font=f_sub, fill=(156, 163, 175, 255), anchor="mt")

        # 수신 버튼
        draw.ellipse([(700, by), (840, by + 140)], fill=(34, 197, 94, 255))
        draw.text((770, by + 70), "📞", font=self._get_font(54), fill=(255, 255, 255, 255), anchor="mm")
        draw.text((770, by + 165), "응답 (통화 연결)", font=f_sub, fill=(74, 222, 128, 255), anchor="mt")

        return img

    def _render_phase3_script_display(self) -> Image.Image:
        """3단계: 통화 연결 및 화면 탈출 대본 표출"""
        img, draw = self._render_phone_frame()
        f_title = self._get_font(38, bold=True)
        f_stat = self._get_font(26, bold=False)
        f_script_title = self._get_font(32, bold=True)
        f_script = self._get_font(34, bold=True)
        f_guide = self._get_font(26, bold=False)

        # 상단 통화 연결 바
        draw.rounded_rectangle([(110, 270), (970, 410)], radius=24, fill=(17, 24, 39, 255), outline=(74, 222, 128, 255), width=2)
        draw.ellipse([(150, 310), (210, 370)], fill=(30, 41, 59, 255))
        draw.text((180, 340), "👔", font=self._get_font(32), anchor="mm")
        draw.text((230, 320), "팀장님 통화 중", font=f_title, fill=(255, 255, 255, 255))
        draw.text((230, 368), "00 : 04 • 긴급 상사 보이스 출력 중", font=f_stat, fill=(74, 222, 128, 255))

        # 핵심 탈출 대본 박스 (화면 중앙 강렬한 옐로우/오렌지 박스)
        sbox = (110, 450, 970, 1100)
        draw.rounded_rectangle([(sbox[0], sbox[1]), (sbox[2], sbox[3])], radius=32, fill=(24, 30, 45, 255), outline=(245, 158, 11, 255), width=4)

        draw.rounded_rectangle([(sbox[0] + 30, sbox[1] + 25), (sbox[2] - 30, sbox[1] + 95)], radius=18, fill=(245, 158, 11, 240))
        draw.text((self.w // 2, sbox[1] + 60), "📋 [화면 탈출 대본 - 그대로 읽으세요]", font=f_script_title, fill=(15, 23, 42, 255), anchor="mm")

        # 대본 본문
        script_lines = [
            "\"어 김대리! 지금 본사에 긴급 비상 걸렸어!\"",
            "\"거래처 서버 다운됐으니까 지금 바로 회사로 복귀해!\"",
            "\"빨리 택시 타고 30분 안으로 본사 들어와!\""
        ]
        sy = sbox[1] + 160
        for line in script_lines:
            draw.text((self.w // 2, sy), line, font=f_script, fill=(254, 240, 138, 255), anchor="mt")
            sy += 110

        # 행동 가이드
        draw.rounded_rectangle([(sbox[0] + 30, sbox[3] - 140), (sbox[2] - 30, sbox[3] - 25)], radius=20, fill=(15, 23, 42, 255))
        draw.text((self.w // 2, sbox[3] - 82), "👉 \"죄송해요 회사에 긴급 호출 와서 먼저 가봐야 해요\" 하고 합법 탈출!", font=f_guide, fill=(74, 222, 128, 255), anchor="mm")

        # 하단 통화 종료 버튼
        draw.ellipse([(self.w // 2 - 60, 1400), (self.w // 2 + 60, 1520)], fill=(239, 68, 68, 255))
        draw.text((self.w // 2, 1460), "📞", font=self._get_font(48), fill=(255, 255, 255, 255), anchor="mm")
        draw.text((self.w // 2, 1545), "통화 종료", font=f_stat, fill=(156, 163, 175, 255), anchor="mt")

        return img
