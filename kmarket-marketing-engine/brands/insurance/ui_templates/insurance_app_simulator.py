# -*- coding: utf-8 -*-
"""
InsuranceAppSimulator - 📱 [보험 리밸런스 웹앱 객관적 분석 고화질 시뮬레이션 렌더링 모듈]
- insure-rebalance.vercel.app 100% 객관적 8대 국민 보험 AI 분석 시뮬레이션
- 1080x1920 세로 풀HD 스마트폰 뷰포트 내 라이브 인터랙션 모션:
  1) [0.0s ~ 3.0s] 내 증권 데이터 스캔 & AI 5대 보장 밸런스 점수 계산
  2) [3.0s ~ 7.0s] 5대 영역 레이더 차트 (암·뇌·심·실비·수술) 실시간 시각화 & 약관 공백 탐지
  3) [7.0s ~ 11.0s] 중복 특약 다이어트 리포트 및 최종 절감액 리포트 화면 클로즈업
"""

import os
import sys
import math
import shutil
import tempfile
import logging
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("InsuranceAppSimulator")

CURRENT_DIR = Path(__file__).resolve().parent
PRESETS_DIR = CURRENT_DIR / "presets"
PRESETS_DIR.mkdir(parents=True, exist_ok=True)


class InsuranceAppSimulator:
    """🛡️ 보험 리밸런스 모바일 앱 객관적 분석 비디오 생성기 (1080x1920)"""

    TOPIC_UI_SPECS = {
        1: {
            "title": "4세대 실손 전환 손익 계산기",
            "warn": "🚨 1~2세대 실비 매년 갱신 폭탄 (월 118,000원)",
            "fix": "➔ 병원 이용 적으면 4세대 전환 시 월 12,500원",
            "saving": "💰 연간 126만원 고정지출 즉시 다이어트!",
            "radar_b": [0.85, 0.70, 0.70, 0.95, 0.60],
            "radar_a": [0.85, 0.70, 0.70, 0.90, 0.60]
        },
        2: {
            "title": "운전자보험 필수 3대 특약 진단",
            "warn": "🚨 불필요한 과다 특약 포함 (월 38,000원 지출)",
            "fix": "➔ 벌금·변호사·합의금 3대 특약만 월 9,900원 세팅",
            "saving": "💰 월 28,100원 절감 (연 33만원 다이어트)",
            "radar_b": [0.50, 0.50, 0.50, 0.60, 0.50],
            "radar_a": [0.95, 0.95, 0.95, 0.95, 0.95]
        },
        3: {
            "title": "암보험 일반암 vs 유사암 한도 분석",
            "warn": "🚨 갑상선·경계성종양 유사암 한도 10% 축소 발견!",
            "fix": "➔ 일반암 진단비의 50~100% 매칭 포트폴리오 권고",
            "saving": "🛡️ 암 진단 시 부지급 리스크 0% 완벽 방어",
            "radar_b": [0.35, 0.60, 0.60, 0.80, 0.50],
            "radar_a": [0.95, 0.60, 0.60, 0.80, 0.50]
        },
        4: {
            "title": "뇌·심장 2대 질환 보장 범위 판독",
            "warn": "🚨 뇌출혈만 가입됨 (가장 흔한 뇌경색 80% 미보장!)",
            "fix": "➔ 뇌혈관질환 & 허혈성심장질환 100% 전액 보장 전환",
            "saving": "🛡️ 뇌경색·협심증 진단비 100% 전액 보장 달성",
            "radar_b": [0.80, 0.20, 0.25, 0.90, 0.60],
            "radar_a": [0.80, 0.95, 0.95, 0.90, 0.60]
        },
        5: {
            "title": "종신보험 사업비 다이어트 계산기",
            "warn": "🚨 저축 오해 종신보험 사업비 30% 과다 차감!",
            "fix": "➔ 60세 만기 정기보험 월 3만원 + 순수 저축 분리",
            "saving": "💰 월 270,000원 절감 (20년간 6,480만원 세이브)",
            "radar_b": [0.60, 0.50, 0.50, 0.70, 0.40],
            "radar_a": [0.90, 0.90, 0.90, 0.90, 0.85]
        },
        6: {
            "title": "어린이·어른이 갱신형 구멍 판독기",
            "warn": "🚨 100세 만기 내 3년 갱신형 특약 5건 발견!",
            "fix": "➔ 20년납 비갱신형으로 리모델링 (보험료 인상 제로)",
            "saving": "🛡️ 노후 보험료 폭탄 원천 차단 완벽 방어",
            "radar_b": [0.55, 0.40, 0.40, 0.85, 0.50],
            "radar_a": [0.90, 0.90, 0.90, 0.95, 0.85]
        },
        7: {
            "title": "치아보험 임플란트 손익 계산기",
            "warn": "🚨 매달 45,000원 3년 납부 시 총 162만원 지출!",
            "fix": "➔ 치료 3달 전 가입 후 감액 기간 종료 즉시 청구 전략",
            "saving": "💰 임플란트 2개 치료 시 실부담금 70% 세이브",
            "radar_b": [0.50, 0.50, 0.50, 0.50, 0.40],
            "radar_a": [0.85, 0.85, 0.85, 0.85, 0.95]
        },
        8: {
            "title": "1~5종 수술비 매회 반복 지급 분석",
            "warn": "🚨 1회성 질병수술비만 가입됨 (반복 수술 미보장)",
            "fix": "➔ 매회 지급 1~5종 수술비 & 로봇수술 특약 보강",
            "saving": "🛡️ 대장 용종·로봇수술 시 매회 50~100만원 수령",
            "radar_b": [0.75, 0.60, 0.60, 0.85, 0.30],
            "radar_a": [0.85, 0.85, 0.85, 0.90, 0.95]
        }
    }

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

    def _render_radar_chart(
        self,
        draw: ImageDraw.Draw,
        cx: int,
        cy: int,
        radius: int,
        values: List[float],
        labels: List[str],
        font: ImageFont.FreeTypeFont,
        color=(37, 99, 235, 180)
    ):
        """5대 보장 영역 인터랙티브 레이더 차트 그리기"""
        num_vars = len(values)
        angle_step = 2 * math.pi / num_vars

        for level in [0.25, 0.5, 0.75, 1.0]:
            r_lvl = radius * level
            grid_pts = [
                (cx + r_lvl * math.sin(i * angle_step), cy - r_lvl * math.cos(i * angle_step))
                for i in range(num_vars)
            ]
            draw.polygon(grid_pts, outline=(51, 65, 85, 180), width=1)

        for i, label in enumerate(labels):
            angle = i * angle_step
            ax = cx + radius * math.sin(angle)
            ay = cy - radius * math.cos(angle)
            draw.line([(cx, cy), (ax, ay)], fill=(71, 85, 105, 180), width=1)

            lx = cx + (radius + 40) * math.sin(angle)
            ly = cy - (radius + 25) * math.cos(angle)
            bbox = draw.textbbox((0, 0), label, font=font)
            lw = bbox[2] - bbox[0]
            lh = bbox[3] - bbox[1]
            draw.text((lx - lw // 2, ly - lh // 2), label, fill=(203, 213, 225), font=font)

        data_pts = [
            (cx + radius * val * math.sin(i * angle_step), cy - radius * val * math.cos(i * angle_step))
            for i, val in enumerate(values)
        ]
        draw.polygon(data_pts, fill=color, outline=(96, 165, 250, 255))
        for pt in data_pts:
            draw.ellipse([(pt[0] - 6, pt[1] - 6), (pt[0] + 6, pt[1] + 6)], fill=(255, 255, 255), outline=(37, 99, 235), width=2)

    def generate_simulation_frames(self, topic_id: int = 1, fps: int = 30, duration_sec: float = 10.0) -> List[Image.Image]:
        """주제별 객관적 AI 리밸런싱 프레임 시퀀스 생성"""
        total_frames = int(fps * duration_sec)
        frames = []

        font_header = self._get_font(38, bold=True)
        font_title = self._get_font(44, bold=True)
        font_body = self._get_font(28, bold=False)
        font_bold = self._get_font(32, bold=True)
        font_score = self._get_font(68, bold=True)
        font_small = self._get_font(24, bold=False)
        font_chart = self._get_font(26, bold=True)

        preset_key = ((topic_id - 1) % len(self.TOPIC_UI_SPECS)) + 1
        spec = self.TOPIC_UI_SPECS.get(preset_key, self.TOPIC_UI_SPECS[1])

        categories = ["암 진단비", "뇌혈관", "허혈심장", "실손의료", "수술·입원"]
        radar_before = spec["radar_b"]
        radar_after = spec["radar_a"]

        for i in range(total_frames):
            t = i / fps
            img = Image.new("RGBA", (self.w, self.h), (11, 19, 38, 255))
            draw = ImageDraw.Draw(img)

            # 1. 상단 앱 헤더
            draw.rectangle([(0, 0), (self.w, 140)], fill=(15, 23, 42, 255))
            draw.text((60, 50), "🛡️ 보험 리밸런스", fill=(255, 255, 255), font=font_header)
            draw.text((self.w - 360, 58), spec["title"], fill=(96, 165, 250), font=font_small)

            # 2. 메인 진단 카드
            draw.rounded_rectangle([(50, 170), (self.w - 50, 1780)], radius=32, fill=(19, 31, 60, 250), outline=(37, 99, 235, 120), width=2)

            if t < 3.0:
                # ── Phase 1 (0.0s ~ 3.0s): AI 증권 스캔 및 보장 분석 로딩 ──
                draw.text((90, 230), "📊 내 보험 증권 AI 정밀 스캔 중...", fill=(255, 255, 255), font=font_title)
                draw.text((90, 300), "특정 보험사 영업 0% • 객관적 데이터 자가진단", fill=(148, 163, 184), font=font_body)

                progress = min(1.0, t / 2.6)
                bar_w = int((self.w - 180) * progress)
                draw.rounded_rectangle([(90, 420), (self.w - 90, 450)], radius=15, fill=(30, 41, 59))
                draw.rounded_rectangle([(90, 420), (90 + bar_w, 450)], radius=15, fill=(37, 99, 235))

                draw.text((90, 480), f"약관 분석 진행률: {int(progress * 100)}%", fill=(96, 165, 250), font=font_bold)

                items = [
                    ("✅ 3대 질병(암·뇌·심장) 보장 범위 판독", t > 0.8),
                    ("✅ 불필요한 중복 특약 및 갱신형 탐지", t > 1.6),
                    ("✅ 고정지출 다이어트 손익 계산", t > 2.4),
                ]
                for idx, (item_text, is_checked) in enumerate(items):
                    color = (255, 255, 255) if is_checked else (100, 116, 139)
                    draw.text((90, 600 + idx * 80), item_text, fill=color, font=font_body)

                pulse_r = int(50 + 10 * math.sin(t * 8))
                draw.ellipse([(self.w // 2 - pulse_r, 1120 - pulse_r), (self.w // 2 + pulse_r, 1120 + pulse_r)], outline=(59, 130, 246), width=4)
                draw.text((self.w // 2 - 80, 1240), "AI 진단 중...", fill=(147, 197, 253), font=font_bold)

            elif t < 6.5:
                # ── Phase 2 (3.0s ~ 6.5s): 5대 보장 레이더 차트 & 공백 탐지 ──
                draw.text((90, 220), "🎯 AI 5대 보장 밸런스 분석 결과", fill=(255, 255, 255), font=font_title)
                score_val = int(58 + min(1.0, (t - 3.0) / 2.0) * 6)
                draw.text((90, 290), f"보장 점수: ", fill=(148, 163, 184), font=font_bold)
                draw.text((240, 278), f"{score_val}점", fill=(239, 68, 68), font=font_score)
                draw.text((400, 295), "(보장 공백 발생)", fill=(248, 113, 113), font=font_bold)

                interp = min(1.0, (t - 3.0) / 1.0)
                cur_radar = [v * interp for v in radar_before]
                self._render_radar_chart(draw, cx=self.w // 2, cy=740, radius=260, values=cur_radar, labels=categories, font=font_chart)

                draw.rounded_rectangle([(90, 1180), (self.w - 90, 1400)], radius=20, fill=(69, 10, 10, 230), outline=(239, 68, 68), width=2)
                draw.text((120, 1210), spec["warn"], fill=(254, 202, 202), font=font_bold)
                draw.text((120, 1280), spec["fix"], fill=(255, 255, 255), font=font_body)

                draw.rounded_rectangle([(90, 1540), (self.w - 90, 1660)], radius=25, fill=(37, 99, 235))
                draw.text((self.w // 2 - 180, 1580), "⚡ AI 리밸런싱 최적화 보기", fill=(255, 255, 255), font=font_title)

            else:
                # ── Phase 3 (6.5s ~ 10.0s): 최적화 완료 리포트 및 최종 절감액 ──
                draw.text((90, 220), "✨ AI 리밸런싱 최적화 완료", fill=(52, 211, 153), font=font_title)
                draw.text((90, 290), "보장 점수 58점 ➔ ", fill=(148, 163, 184), font=font_bold)
                draw.text((340, 278), "95점", fill=(52, 211, 153), font=font_score)
                draw.text((500, 295), "(완벽 보장 달성)", fill=(110, 231, 183), font=font_bold)

                interp2 = min(1.0, (t - 6.5) / 1.0)
                cur_radar2 = [radar_before[k] + (radar_after[k] - radar_before[k]) * interp2 for k in range(5)]
                self._render_radar_chart(draw, cx=self.w // 2, cy=740, radius=260, values=cur_radar2, labels=categories, font=font_chart, color=(16, 185, 129, 180))

                draw.rounded_rectangle([(90, 1160), (self.w - 90, 1460)], radius=24, fill=(6, 78, 59, 230), outline=(16, 185, 129), width=2)
                draw.text((120, 1190), "📊 리밸런싱 최종 결과", fill=(167, 243, 208), font=font_bold)
                draw.text((120, 1260), spec["fix"], fill=(209, 250, 229), font=font_body)
                draw.text((120, 1330), spec["saving"], fill=(250, 204, 21), font=font_bold)

                draw.rounded_rectangle([(90, 1540), (self.w - 90, 1660)], radius=25, fill=(16, 185, 129))
                draw.text((self.w // 2 - 220, 1580), "🔍 내 보험 무료 점검 받기", fill=(255, 255, 255), font=font_title)

            frames.append(img.convert("RGB"))

        return frames

    def record_simulation_clip(
        self,
        topic_id: int = 1,
        duration_sec: float = 10.0,
        output_mp4_path: str = "insurance_app_sim.mp4"
    ) -> str:
        """보험 리밸런스 앱 시뮬레이션 클립을 1080x1920 MP4로 렌더링"""
        out_p = Path(output_mp4_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"📱 [InsuranceAppSimulator] 주제 {topic_id} 고화질 앱 시뮬레이션 프레임 렌더링 중...")
        frames = self.generate_simulation_frames(topic_id=topic_id, fps=30, duration_sec=duration_sec)

        temp_dir = Path(tempfile.mkdtemp(prefix="insure_sim_"))
        try:
            for idx, frame in enumerate(frames):
                frame.save(str(temp_dir / f"frame_{idx:05d}.jpg"), "JPEG", quality=95)

            cmd = [
                self.ffmpeg_exe, "-y",
                "-r", "30",
                "-i", str(temp_dir / "frame_%05d.jpg"),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-crf", "18",
                "-preset", "fast",
                str(out_p)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            logger.info(f"🎉 [InsuranceAppSimulator] 앱 시뮬레이션 MP4 완료: {out_p} ({out_p.stat().st_size:,} bytes)")
            return str(out_p)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
