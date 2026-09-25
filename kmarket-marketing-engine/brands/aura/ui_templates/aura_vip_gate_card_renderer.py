# -*- coding: utf-8 -*-
"""
AuraVipGateCardRenderer - 📱 [Aura 주제 #3 전용 8초 모바일 앱 시연 렌더러]
- 독립 레고 블록 모듈
- 1080x1920 세로 풀HD 규격, 30fps
- 시나리오 싱크 (내레이션: "남성은 정원 찰 때까지 줄 서서 대기하고, 여성은 VIP 프리패스로 바로 입장! 물 흐리는 사람 1도 없고 대화 퀄리티가 완전 달라요.")
  1) [0.0s ~ 1.6s]: 국내 최초 50:50 성비 보장 라운지 입장 게이트 (남초 제로, 성비 균형 게이트 통과 애니메이션)
  2) [1.6s ~ 8.0s]: 8인 실사 훈남훈녀 프로필 카드 탐색 스와이프 (각 0.8초, 매칭률 94~99%, 하트 펄스 애니메이션)
"""

import os
import shutil
import tempfile
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

logger = logging.getLogger("AuraVipGateCardRenderer")


class AuraVipGateCardRenderer:
    """Aura 주제 #3 (50:50 VIP 게이트) 전용 1080x1920 고화질 8초 시연 렌더러"""

    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.w = 1080
        self.h = 1920
        self.base_dir = Path(__file__).resolve().parent
        self.assets_dir = self.base_dir / "assets" / "topic3_profiles"

        # 8인 프로필 메타데이터
        self.profiles = [
            {
                "img": "card_01_female_seoyeon.jpg",
                "name": "서연",
                "age": 23,
                "location": "한남동",
                "match": 98,
                "common": 3,
                "quote": "주말엔 전시회랑 브런치 카페 투어 좋아해요! ☕",
                "tags": ["전시회", "브런치", "사진", "카페투어"]
            },
            {
                "img": "card_02_male_minjun.jpg",
                "name": "민준",
                "age": 24,
                "location": "연남동",
                "match": 95,
                "common": 4,
                "quote": "편하게 동네에서 산책하고 커피 한잔할 친구 🌿",
                "tags": ["카페투어", "산책", "LP음악", "댕댕이"]
            },
            {
                "img": "card_03_female_jiwoo.jpg",
                "name": "지우",
                "age": 23,
                "location": "성수동",
                "match": 97,
                "common": 3,
                "quote": "새로운 디저트 맛집 찾아다니는 게 취미예요! 🍰",
                "tags": ["베이커리", "맛집탐방", "드라이브", "필라테스"]
            },
            {
                "img": "card_04_male_dohyun.jpg",
                "name": "도현",
                "age": 23,
                "location": "북촌",
                "match": 94,
                "common": 4,
                "quote": "한옥 감성이랑 고즈넉한 카페 좋아합니다 ☕",
                "tags": ["감성카페", "독서", "여행", "건축"]
            },
            {
                "img": "card_05_female_yujin.jpg",
                "name": "유진",
                "age": 22,
                "location": "홍대",
                "match": 99,
                "common": 5,
                "quote": "말차 라떼랑 독립서점 구경하는 거 좋아해요 📖",
                "tags": ["북카페", "전시", "러닝", "인디음악"]
            },
            {
                "img": "card_06_male_junwoo.jpg",
                "name": "준우",
                "age": 24,
                "location": "여의도",
                "match": 96,
                "common": 3,
                "quote": "날씨 좋은 날 한강에서 자전거 타는 거 좋아해요 🚴",
                "tags": ["한강", "운동", "아메리카노", "테니스"]
            },
            {
                "img": "card_07_female_suah.jpg",
                "name": "수아",
                "age": 24,
                "location": "해방촌",
                "match": 98,
                "common": 4,
                "quote": "노을 보면서 루프탑에서 이야기 나누는 시간 🌇",
                "tags": ["루프탑", "야경", "와인", "맛집"]
            },
            {
                "img": "card_08_male_hyunwoo.jpg",
                "name": "현우",
                "age": 24,
                "location": "한남동",
                "match": 97,
                "common": 4,
                "quote": "편집숍 투어랑 라이프스타일 디자인 관심 많아요 ✨",
                "tags": ["디자인", "쇼핑", "미술관", "패션"]
            },
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
                    continue
        return ImageFont.load_default()

    def render_video(self, output_mp4_path: str, duration_sec: float = 8.0) -> str:
        """1080x1920 8초 시연 비디오 렌더링"""
        out_p = Path(output_mp4_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"🚀 [AuraVipGateCardRenderer] 8초 시연 비디오 생성 시작 -> {out_p.name}")
        fps = 30
        total_frames = int(duration_sec * fps)
        gate_frames = int(1.6 * fps)  # 0~1.6s 50:50 게이트
        card_frames = total_frames - gate_frames
        frames_per_card = card_frames / len(self.profiles)  # 0.8s each

        temp_dir = Path(tempfile.mkdtemp(prefix="aura_vip_sim_"))
        try:
            # 1. 50:50 게이트 프레임 생성
            gate_img = self._render_gate_screen()

            # 2. 8개 프로필 카드 기본 이미지 사전 렌더링
            card_images = []
            for prof in self.profiles:
                card_img = self._render_profile_card_screen(prof)
                card_images.append(card_img)

            # 프레임 루프
            for frame_idx in range(total_frames):
                if frame_idx < gate_frames:
                    # 게이트 화면 연출: 미세 펄스 글로우 및 1.4s에 승인 플래시
                    progress = frame_idx / gate_frames
                    frame_img = self._render_gate_screen(progress=progress)
                else:
                    card_rel_idx = frame_idx - gate_frames
                    card_num = int(card_rel_idx // frames_per_card)
                    card_num = min(card_num, len(self.profiles) - 1)
                    
                    sub_frame = card_rel_idx % frames_per_card
                    sub_progress = sub_frame / frames_per_card  # 0.0 ~ 1.0
                    
                    # 스와이프 트랜지션 연출: 카드 시작 시 스와이프 인, 끝날 때 하트 펄스
                    prof = self.profiles[card_num]
                    frame_img = self._render_profile_card_screen(
                        prof=prof,
                        anim_progress=sub_progress,
                        heart_pulse=(sub_progress > 0.5)
                    )

                frame_path = temp_dir / f"frame_{frame_idx:04d}.png"
                frame_img.save(str(frame_path), "PNG")

            # FFmpeg 컴파일 (1080x1920 30fps)
            cmd = [
                self.ffmpeg_exe, "-y",
                "-framerate", str(fps),
                "-i", str(temp_dir / "frame_%04d.png"),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-crf", "18",
                "-preset", "fast",
                "-t", str(duration_sec),
                str(out_p)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            logger.info(f"✨ [AuraVipGateCardRenderer] 8초 시연 비디오 렌더링 완성: {out_p.name} ({out_p.stat().st_size} bytes)")
            return str(out_p)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _render_phone_chassis(self) -> Tuple[Image.Image, ImageDraw.ImageDraw]:
        """기본 다크모드 스마트폰 베이스 프레임"""
        img = Image.new("RGBA", (self.w, self.h), (11, 15, 25, 255))
        draw = ImageDraw.Draw(img)

        # 은은한 앰비언트 백라이트
        draw.ellipse([(140, 100), (940, 900)], fill=(30, 41, 59, 100))
        draw.ellipse([(100, 800), (980, 1700)], fill=(244, 114, 182, 25))

        # 스마트폰 베젤
        bx1, by1, bx2, by2 = 60, 70, 1020, 1850
        draw.rounded_rectangle([(bx1, by1), (bx2, by2)], radius=56, fill=(15, 23, 42, 255), outline=(51, 65, 85, 255), width=4)

        # 다이내믹 아일랜드
        draw.rounded_rectangle([(self.w // 2 - 110, by1 + 22), (self.w // 2 + 110, by1 + 62)], radius=20, fill=(0, 0, 0, 255))
        draw.ellipse([(self.w // 2 + 65, by1 + 35), (self.w // 2 + 85, by1 + 55)], fill=(30, 41, 59, 255))

        # 상단 상태 표시줄
        f_stat = self._get_font(26, bold=True)
        draw.text((bx1 + 55, by1 + 32), "09:41", font=f_stat, fill=(255, 255, 255, 230))
        draw.text((bx2 - 130, by1 + 32), "5G 􀛨", font=f_stat, fill=(255, 255, 255, 230))

        # 하단 홈 인디케이터
        draw.rounded_rectangle([(self.w // 2 - 120, by2 - 30), (self.w // 2 + 120, by2 - 18)], radius=6, fill=(255, 255, 255, 180))

        return img, draw

    def _render_gate_screen(self, progress: float = 1.0) -> Image.Image:
        """1단계 (0.0s ~ 1.6s): 50:50 성비 보장 라운지 입장 게이트"""
        img, draw = self._render_phone_chassis()
        by1 = 70

        # 언어 선택 알약 뱃지
        f_pill = self._get_font(22, bold=True)
        draw.rounded_rectangle([(self.w // 2 - 80, by1 + 95), (self.w // 2 + 80, by1 + 135)], radius=20, fill=(245, 158, 11, 230))
        draw.text((self.w // 2, by1 + 115), "🇰🇷 한국어", font=f_pill, fill=(15, 23, 42, 255), anchor="mm")

        # 메인 브랜드 타이틀
        f_brand = self._get_font(72, bold=True)
        f_subbrand = self._get_font(30, bold=False)
        draw.text((self.w // 2, by1 + 220), "Aura", font=f_brand, fill=(245, 158, 11, 255), anchor="mm")
        draw.text((self.w // 2, by1 + 285), "운명적인 인연을 발견하세요", font=f_subbrand, fill=(203, 213, 225, 255), anchor="mm")

        # 50:50 황금 게이트 메인 카드 컨테이너
        cx1, cy1, cx2, cy2 = 110, by1 + 360, 970, by1 + 1260
        draw.rounded_rectangle([(cx1, cy1), (cx2, cy2)], radius=36, fill=(20, 26, 38, 255), outline=(245, 158, 11, 255), width=3)

        # 상단 배지 헤더
        f_badge = self._get_font(24, bold=True)
        draw.text((cx1 + 40, cy1 + 45), "👑 국내 최초 50:50 성비 보장 라운지", font=f_badge, fill=(251, 191, 36, 255))
        draw.text((cx2 - 40, cy1 + 45), "✨ AURA Equilibrium", font=f_badge, fill=(148, 163, 184, 255), anchor="rt")

        # 메인 카피
        f_head = self._get_font(38, bold=True)
        f_body = self._get_font(24, bold=False)
        draw.text((self.w // 2, cy1 + 120), "남초 현상 제로, 남녀 50:50 완벽 균형 매칭", font=f_head, fill=(255, 255, 255, 255), anchor="mt")
        draw.text((self.w // 2, cy1 + 175), "남녀 성비를 50:50으로 엄격히 유지하는 최고급 프라이빗 라운지", font=f_body, fill=(148, 163, 184, 255), anchor="mt")

        # 50:50 실시간 밸런스 미터 박스
        bx_y = cy1 + 245
        draw.rounded_rectangle([(cx1 + 30, bx_y), (cx2 - 30, bx_y + 195)], radius=24, fill=(13, 18, 28, 255), outline=(51, 65, 85, 200), width=2)
        
        draw.text((cx1 + 55, bx_y + 35), "🟢 50:50 GENDER EQUILIBRIUM", font=self._get_font(24, bold=True), fill=(74, 222, 128, 255))
        draw.text((cx2 - 55, bx_y + 35), "실시간 엄격 수질 관리 ✨", font=self._get_font(22, bold=False), fill=(148, 163, 184, 255), anchor="rt")

        # 듀얼 컬러 게이지 바 (Cyan 50% vs Pink 50%)
        bar_x1, bar_y1, bar_x2, bar_y2 = cx1 + 55, bx_y + 80, cx2 - 55, bx_y + 115
        bar_w = bar_x2 - bar_x1
        mid_x = bar_x1 + bar_w // 2

        # 남성 50% (시안 블루)
        draw.rounded_rectangle([(bar_x1, bar_y1), (mid_x, bar_y2)], radius=16, fill=(56, 189, 248, 255))
        # 여성 50% (핑크)
        draw.rounded_rectangle([(mid_x, bar_y1), (bar_x2, bar_y2)], radius=16, fill=(244, 114, 182, 255))

        # 중앙 골드 균형 알약
        draw.rounded_rectangle([(mid_x - 55, bar_y1 - 6), (mid_x + 55, bar_y2 + 6)], radius=18, fill=(245, 158, 11, 255))
        draw.text((mid_x, (bar_y1 + bar_y2) // 2), "완벽 균형", font=self._get_font(18, bold=True), fill=(15, 23, 42, 255), anchor="mm")

        # 하단 라벨
        draw.text((bar_x1 + 10, bx_y + 145), "🟦 남성 회원 50%", font=self._get_font(24, bold=True), fill=(56, 189, 248, 255))
        draw.text((bar_x2 - 10, bx_y + 145), "50% 여성 회원 🌸", font=self._get_font(24, bold=True), fill=(244, 114, 182, 255), anchor="rt")

        # 서브 카드 1: 여성 회원 100% 프리패스
        p_y = bx_y + 225
        draw.rounded_rectangle([(cx1 + 30, p_y), (cx2 - 30, p_y + 115)], radius=20, fill=(35, 21, 35, 220), outline=(244, 114, 182, 180), width=2)
        draw.text((cx1 + 55, p_y + 28), "🌸 여성 회원: 100% 프리패스", font=self._get_font(26, bold=True), fill=(244, 114, 182, 255))
        draw.text((cx1 + 55, p_y + 70), "성비 균형 유지를 위해 대기 없이 즉시 무료 프리패스 승인", font=self._get_font(22, bold=False), fill=(226, 232, 240, 255))

        # 서브 카드 2: 남성 회원 VIP 대기열
        b_y = p_y + 135
        draw.rounded_rectangle([(cx1 + 30, b_y), (cx2 - 30, b_y + 115)], radius=20, fill=(18, 30, 48, 220), outline=(56, 189, 248, 180), width=2)
        draw.text((cx1 + 55, b_y + 28), "🛡️ 남성 회원: VIP 정원제 대기열", font=self._get_font(26, bold=True), fill=(56, 189, 248, 255))
        draw.text((cx1 + 55, b_y + 70), "수질 관리 및 정원 엄수 • 여사친 초대 시 0순위 프리패스", font=self._get_font(22, bold=False), fill=(226, 232, 240, 255))

        # 하단 황금 입장 버튼
        btn_y1 = cy1 + 760
        draw.rounded_rectangle([(cx1 + 30, btn_y1), (cx2 - 30, btn_y1 + 100)], radius=30, fill=(245, 158, 11, 255))
        draw.text((self.w // 2, btn_y1 + 50), "🔓 VIP 라운지 입장 승인 완료 (탐색 시작)", font=self._get_font(32, bold=True), fill=(15, 23, 42, 255), anchor="mm")

        # 하단 안내 텍스트
        draw.text((self.w // 2, by1 + 1360), "엄격한 50:50 정원제로 대화 성공률과 매칭 만족도가 극대화됩니다", font=self._get_font(24, bold=False), fill=(148, 163, 184, 230), anchor="mt")

        return img

    def _render_profile_card_screen(
        self,
        prof: Dict[str, Any],
        anim_progress: float = 0.5,
        heart_pulse: bool = False
    ) -> Image.Image:
        """2단계 (1.6s ~ 8.0s): 8인 프로필 카드 스와이프 탐색 화면"""
        img, draw = self._render_phone_chassis()
        by1 = 70

        # 상단 네비게이션 바 (AI 추천 | Aura 골드 | ⚙️)
        top_y = by1 + 95
        f_rec = self._get_font(24, bold=True)
        draw.text((120, top_y), "✨ AI 추천", font=f_rec, fill=(245, 158, 11, 255))

        f_logo = self._get_font(42, bold=True)
        draw.text((self.w // 2, top_y - 5), "Aura", font=f_logo, fill=(245, 158, 11, 255), anchor="mt")

        draw.rounded_rectangle([(850, top_y - 10), (960, top_y + 35)], radius=18, fill=(30, 41, 59, 200), outline=(51, 65, 85, 200), width=1)
        draw.text((905, top_y + 12), "필터 ⚙️", font=self._get_font(20, bold=True), fill=(203, 213, 225, 255), anchor="mm")

        # 메인 프로필 카드 영역 (120, 240, 960, 1380)
        card_x1, card_y1, card_x2, card_y2 = 120, 230, 960, 1380
        card_w = card_x2 - card_x1
        card_h = card_y2 - card_y1

        # 카드 프로필 사진 로드 및 리사이즈
        img_p = self.assets_dir / prof["img"]
        if img_p.exists():
            photo = Image.open(str(img_p)).convert("RGBA")
            # Aspect fill
            scale = max(card_w / photo.width, card_h / photo.height)
            nw = int(photo.width * scale)
            nh = int(photo.height * scale)
            photo = photo.resize((nw, nh), Image.LANCZOS)
            # Center crop
            cx = (nw - card_w) // 2
            cy = (nh - card_h) // 2
            cropped = photo.crop((cx, cy, cx + card_w, cy + card_h))

            # 둥근 모서리 마스크 생성
            mask = Image.new("L", (card_w, card_h), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle([(0, 0), (card_w, card_h)], radius=36, fill=255)

            # 카드에 하단 어두운 그라데이션 오버레이 적용 (텍스트 가독성)
            grad = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
            g_draw = ImageDraw.Draw(grad)
            for y_step in range(int(card_h * 0.45), card_h):
                alpha = int(240 * ((y_step - card_h * 0.45) / (card_h * 0.55)))
                g_draw.line([(0, y_step), (card_w, y_step)], fill=(10, 15, 25, alpha))

            card_composite = Image.alpha_composite(cropped, grad)

            # 스와이프 효과 (미세 진입 슬라이드)
            offset_x = 0
            if anim_progress < 0.2:
                # 진입 시 오른쪽에서 슬라이드
                offset_x = int((1.0 - (anim_progress / 0.2)) * 60)
            elif anim_progress > 0.85:
                # 다음 카드로 살짝 스와이프 아웃
                offset_x = -int(((anim_progress - 0.85) / 0.15) * 60)

            img.paste(card_composite, (card_x1 + offset_x, card_y1), mask=mask)
        else:
            draw.rounded_rectangle([(card_x1, card_y1), (card_x2, card_y2)], radius=36, fill=(30, 41, 59, 255))

        # 카드 테두리 선
        draw.rounded_rectangle([(card_x1, card_y1), (card_x2, card_y2)], radius=36, outline=(245, 158, 11, 160), width=3)

        # 상단 뱃지 1: 매칭률 (골드 알약)
        badge_y = card_y1 + 30
        draw.rounded_rectangle([(card_x1 + 30, badge_y), (card_x1 + 190, badge_y + 55)], radius=20, fill=(245, 158, 11, 230))
        draw.text((card_x1 + 110, badge_y + 28), f"🔥 {prof['match']}% 일치", font=self._get_font(24, bold=True), fill=(15, 23, 42, 255), anchor="mm")

        # 상단 뱃지 2: 공통점
        draw.rounded_rectangle([(card_x2 - 180, badge_y), (card_x2 - 30, badge_y + 55)], radius=20, fill=(15, 23, 42, 200), outline=(245, 158, 11, 200), width=2)
        draw.text((card_x2 - 105, badge_y + 28), f"공통점 {prof['common']}개", font=self._get_font(22, bold=True), fill=(251, 191, 36, 255), anchor="mm")

        # 카드 하단 정보 (이름, 나이, 지역)
        info_y = card_y2 - 280
        f_name = self._get_font(52, bold=True)
        draw.text((card_x1 + 40, info_y), f"{prof['name']}, {prof['age']}", font=f_name, fill=(255, 255, 255, 255))

        # 인증 배지 (그린 체크)
        f_ver = self._get_font(26, bold=True)
        draw.rounded_rectangle([(card_x1 + 310, info_y + 10), (card_x1 + 450, info_y + 50)], radius=15, fill=(34, 197, 94, 220))
        draw.text((card_x1 + 380, info_y + 30), f"✓ {prof['location']}", font=f_ver, fill=(255, 255, 255, 255), anchor="mm")

        # 한줄 소개
        f_quote = self._get_font(28, bold=False)
        draw.text((card_x1 + 40, info_y + 75), prof["quote"], font=f_quote, fill=(226, 232, 240, 255))

        # 관심사 태그 알약들
        pill_y = info_y + 140
        curr_px = card_x1 + 40
        f_tag = self._get_font(22, bold=True)
        for tag in prof["tags"]:
            tag_text = f"#{tag}"
            bbox = draw.textbbox((curr_px, pill_y), tag_text, font=f_tag)
            tw = bbox[2] - bbox[0] + 32
            draw.rounded_rectangle([(curr_px, pill_y), (curr_px + tw, pill_y + 44)], radius=18, fill=(30, 41, 59, 210), outline=(71, 85, 105, 180), width=1)
            draw.text((curr_px + tw // 2, pill_y + 22), tag_text, font=f_tag, fill=(203, 213, 225, 255), anchor="mm")
            curr_px += tw + 14

        # 하단 액션 버튼들 (✕ 패스 | 💬 대화 | 💖 라이크)
        act_y = 1480
        # ✕ 패스 버튼
        draw.ellipse([(200, act_y - 45), (290, act_y + 45)], fill=(30, 41, 59, 255), outline=(71, 85, 105, 200), width=2)
        draw.text((245, act_y), "✕", font=self._get_font(38, bold=True), fill=(148, 163, 184, 255), anchor="mm")

        # 💬 메시지 버튼
        draw.ellipse([(self.w // 2 - 40, act_y - 40), (self.w // 2 + 40, act_y + 40)], fill=(30, 41, 59, 255), outline=(56, 189, 248, 200), width=2)
        draw.text((self.w // 2, act_y), "💬", font=self._get_font(32), anchor="mm")

        # 💖 라이크 버튼 (하트 펄스 애니메이션)
        heart_r = 55 if heart_pulse else 45
        draw.ellipse([(880 - 45 - heart_r, act_y - heart_r), (880 - 45 + heart_r, act_y + heart_r)], fill=(244, 114, 182, 255) if heart_pulse else (225, 29, 72, 255))
        draw.text((880 - 45, act_y), "💖", font=self._get_font(42 if heart_pulse else 36), anchor="mm")

        # 하단 탭 네비게이션 바
        nav_y = 1680
        draw.line([(60, nav_y), (1020, nav_y)], fill=(30, 41, 59, 220), width=2)

        tabs = [
            ("🔍", "탐색", True),
            ("🗺️", "지도", False),
            ("🔥", "HOT", False),
            ("💬", "매칭", False),
            ("✨", "라운지", False),
            ("👤", "마이", False)
        ]
        step_x = (1020 - 60) // len(tabs)
        for t_idx, (icon, label, active) in enumerate(tabs):
            tx = 60 + step_x * t_idx + step_x // 2
            f_icon = self._get_font(32)
            f_tlabel = self._get_font(20, bold=active)
            draw.text((tx, nav_y + 35), icon, font=f_icon, anchor="mm")
            draw.text((tx, nav_y + 75), label, font=f_tlabel, fill=(245, 158, 11, 255) if active else (148, 163, 184, 255), anchor="mm")

        return img


if __name__ == "__main__":
    renderer = AuraVipGateCardRenderer()
    out_file = Path(__file__).resolve().parent / "presets" / "aura_vip_5050_card_sim.mp4"
    renderer.render_video(output_mp4_path=str(out_file), duration_sec=8.0)
