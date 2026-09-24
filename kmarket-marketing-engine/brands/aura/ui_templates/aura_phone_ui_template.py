# -*- coding: utf-8 -*-
"""
AuraPhoneUITemplate - 📱 [Aura 스마트폰 액정 화면 템플릿]
- EasyTax의 RefundReceiptTemplate을 100% 계승하여 스마트폰 액정(469x1024)에 OpenCV로 매립되는 UI 렌더러
- 8대 킬러 주제별 모바일 앱 실제 화면 렌더링
  1: 소개팅 탈출 전화 (통화 수신 화면)
  2: 실시간 라이브 자막 통화
  3: 50:50 황금 성비 VIP 게이트
  4: 청담동 화보 프로필
  5: 가치관 밸런스 게임 매칭
  6: AI 카톡 비서 말풍선
  7: AI 아우라 매력 진단 카드
  8: 500m 안심 레이더 지도
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


class AuraPhoneUITemplate:
    """Aura 모바일 앱 스마트폰 액정 화면 UI 생성기 (469x1024)"""

    def __init__(self):
        self.width = 469
        self.height = 1024

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

    def render(self, topic_id: int = 1) -> Image.Image:
        """주제 ID(1~8)에 맞춰 469x1024 크기의 스마트폰 액정 UI 생성"""
        ui = Image.new("RGBA", (self.width, self.height), (15, 23, 42, 255))
        draw = ImageDraw.Draw(ui)

        # 상단 모바일 상태 바 (시간, 와이파이, 배터리)
        f_status = self._get_font(18, bold=True)
        draw.text((35, 20), "09:41", font=f_status, fill=(255, 255, 255, 255))
        draw.text((self.width - 70, 20), "5G 􀛨", font=f_status, fill=(255, 255, 255, 255))

        # Aura 상단 네비게이션 바
        draw.rectangle([0, 55, self.width, 115], fill=(30, 41, 59, 255))
        f_nav = self._get_font(24, bold=True)
        draw.text((self.width // 2, 85), "💖 Aura Lounge", font=f_nav, fill=(244, 114, 182, 255), anchor="mm")

        # 주제별 화면 본문
        if topic_id == 1:
            self._render_escape_call(draw)
        elif topic_id == 2:
            self._render_live_subtitles(draw)
        elif topic_id == 3:
            self._render_vip_gate(draw)
        elif topic_id == 4:
            self._render_cheongdam(draw)
        elif topic_id == 5:
            self._render_balance(draw)
        elif topic_id == 6:
            self._render_icebreaker(draw)
        elif topic_id == 7:
            self._render_aura_diag(draw)
        elif topic_id == 8:
            self._render_radar(draw)
        else:
            self._render_escape_call(draw)

        # 하단 홈 인디케이터 바
        draw.rounded_rectangle([self.width // 2 - 70, self.height - 25, self.width // 2 + 70, self.height - 18], radius=4, fill=(255, 255, 255, 180))

        return ui

    def _render_escape_call(self, draw: ImageDraw.ImageDraw):
        f_title = self._get_font(28, bold=True)
        f_sub = self._get_font(20, bold=False)
        f_script = self._get_font(22, bold=True)
        f_btn = self._get_font(18, bold=True)

        draw.rounded_rectangle([25, 140, self.width - 25, 340], radius=24, fill=(30, 41, 59, 255), outline=(239, 68, 68, 255), width=3)
        draw.text((self.width // 2, 175), "🚨 [소개팅 탈출 전화 예약]", font=f_title, fill=(248, 113, 113, 255), anchor="mt")
        draw.text((self.width // 2, 220), "설정: 1분 뒤 긴급 자동 수신", font=f_sub, fill=(226, 232, 240, 255), anchor="mt")
        draw.text((self.width // 2, 260), "상태: 전화 대기 중 (벨소리 ON)", font=f_sub, fill=(74, 222, 128, 255), anchor="mt")

        # 수신 화면
        draw.rounded_rectangle([25, 370, self.width - 25, 800], radius=28, fill=(17, 24, 39, 255), outline=(255, 255, 255, 40), width=2)
        draw.ellipse([self.width // 2 - 50, 410, self.width // 2 + 50, 510], fill=(55, 65, 81, 255))
        draw.text((self.width // 2, 460), "👔", font=self._get_font(48), anchor="mm")
        draw.text((self.width // 2, 535), "팀장님 (비상 연락)", font=f_title, fill=(255, 255, 255, 255), anchor="mt")
        draw.text((self.width // 2, 575), "통화 연결 중...", font=f_sub, fill=(156, 163, 175, 255), anchor="mt")

        # 대본 박스
        draw.rounded_rectangle([45, 620, self.width - 45, 710], radius=16, fill=(39, 39, 42, 255))
        draw.text((self.width // 2, 635), "💬 탈출 대본", font=self._get_font(16, bold=True), fill=(250, 204, 21, 255), anchor="mt")
        draw.text((self.width // 2, 665), '"네 팀장님! 지금 바로 가겠습니다!"', font=f_script, fill=(255, 255, 255, 255), anchor="mt")

        # 버튼
        draw.ellipse([self.width // 2 - 35, 730, self.width // 2 + 35, 800], fill=(239, 68, 68, 255))
        draw.text((self.width // 2, 765), "종료", font=f_btn, fill=(255, 255, 255, 255), anchor="mm")

    def _render_live_subtitles(self, draw: ImageDraw.ImageDraw):
        f_title = self._get_font(26, bold=True)
        f_sub = self._get_font(20, bold=False)
        draw.rounded_rectangle([25, 140, self.width - 25, 780], radius=28, fill=(17, 24, 39, 255), outline=(56, 189, 248, 200), width=2)
        draw.text((self.width // 2, 175), "🌐 LIVE 자막 영상통화", font=f_title, fill=(56, 189, 248, 255), anchor="mt")
        draw.text((self.width // 2, 215), "나나미 (도쿄, 24세) 연결됨", font=f_sub, fill=(203, 213, 225, 255), anchor="mt")

        # 영상 영역 박스
        draw.rounded_rectangle([45, 260, self.width - 45, 600], radius=20, fill=(30, 41, 59, 255))
        draw.text((self.width // 2, 420), "🌸", font=self._get_font(70), anchor="mm")

        # 넷플릭스 자막 바
        draw.rounded_rectangle([45, 630, self.width - 45, 740], radius=16, fill=(0, 0, 0, 230))
        draw.text((self.width // 2, 645), "Nanami: 韓国に遊びに行きたい！", font=self._get_font(18), fill=(203, 213, 225, 255), anchor="mt")
        draw.text((self.width // 2, 680), "[실시간 자막] 한국 놀러 가고 싶어! 🍜", font=self._get_font(20, bold=True), fill=(250, 204, 21, 255), anchor="mt")

    def _render_vip_gate(self, draw: ImageDraw.ImageDraw):
        f_title = self._get_font(26, bold=True)
        f_sub = self._get_font(19, bold=False)
        draw.rounded_rectangle([25, 140, self.width - 25, 450], radius=24, fill=(17, 24, 39, 255), outline=(234, 179, 8, 255), width=2)
        draw.text((self.width // 2, 175), "👑 50:50 황금 성비 정원제", font=f_title, fill=(253, 224, 71, 255), anchor="mt")

        # 게이지 바
        draw.rectangle([50, 230, self.width // 2, 275], fill=(59, 130, 246, 255))
        draw.rectangle([self.width // 2, 230, self.width - 50, 275], fill=(236, 72, 153, 255))
        draw.text((self.width // 4 + 10, 252), "남성 50%", font=self._get_font(16, bold=True), fill=(255, 255, 255, 255), anchor="mm")
        draw.text((self.width * 3 // 4 - 10, 252), "여성 50%", font=self._get_font(16, bold=True), fill=(255, 255, 255, 255), anchor="mm")

        draw.text((self.width // 2, 310), "남성: 142명 대기열 대기 중", font=f_sub, fill=(147, 197, 253, 255), anchor="mt")
        draw.text((self.width // 2, 350), "여성: VIP 프리패스 즉시 입장!", font=f_sub, fill=(244, 114, 182, 255), anchor="mt")

        # 골드 티켓
        draw.rounded_rectangle([40, 500, self.width - 40, 750], radius=24, fill=(30, 27, 75, 255), outline=(245, 158, 11, 255), width=3)
        draw.text((self.width // 2, 540), "✨ FEMALE VIP PASS ✨", font=self._get_font(24, bold=True), fill=(251, 191, 36, 255), anchor="mt")
        draw.text((self.width // 2, 600), "대기 없이 청정 라운지 입장", font=f_sub, fill=(255, 255, 255, 255), anchor="mt")
        draw.text((self.width // 2, 650), "남탕 불쾌감 0% • 완벽 수질 보장", font=f_sub, fill=(52, 211, 153, 255), anchor="mt")

    def _render_cheongdam(self, draw: ImageDraw.ImageDraw):
        f_title = self._get_font(26, bold=True)
        draw.rounded_rectangle([25, 140, self.width - 25, 750], radius=24, fill=(17, 24, 39, 255), outline=(244, 114, 182, 255), width=2)
        draw.text((self.width // 2, 175), "📸 청담 스냅 화보 보정", font=f_title, fill=(244, 114, 182, 255), anchor="mt")
        draw.text((self.width // 2, 220), "인위적인 가짜 필터 NO! 본판 100% 보존", font=self._get_font(18), fill=(203, 213, 225, 255), anchor="mt")

        # 비교 카드
        draw.rounded_rectangle([45, 280, self.width - 45, 680], radius=20, fill=(30, 41, 59, 255))
        draw.text((self.width // 2, 380), "BEFORE 쌩얼 셀카", font=self._get_font(20, bold=True), fill=(156, 163, 175, 255), anchor="mm")
        draw.line([(50, 480), (self.width - 50, 480)], fill=(244, 114, 182, 255), width=3)
        draw.text((self.width // 2, 580), "AFTER 청담 스냅 화보 ✨", font=self._get_font(22, bold=True), fill=(244, 114, 182, 255), anchor="mm")

    def _render_balance(self, draw: ImageDraw.ImageDraw):
        f_title = self._get_font(26, bold=True)
        draw.rounded_rectangle([25, 140, self.width - 25, 750], radius=24, fill=(17, 24, 39, 255), outline=(168, 85, 247, 255), width=2)
        draw.text((self.width // 2, 175), "⚖️ 가치관 밸런스 매칭", font=f_title, fill=(192, 132, 252, 255), anchor="mt")
        draw.text((self.width // 2, 220), "Q. 첫 만남 데이트 비용은?", font=self._get_font(22, bold=True), fill=(255, 255, 255, 255), anchor="mt")

        draw.rounded_rectangle([45, 290, self.width - 45, 390], radius=16, fill=(59, 130, 246, 230))
        draw.text((self.width // 2, 340), "A. 50:50 칼더치페이 (48%)", font=self._get_font(20, bold=True), fill=(255, 255, 255, 255), anchor="mm")

        draw.rounded_rectangle([45, 420, self.width - 45, 520], radius=16, fill=(236, 72, 153, 230))
        draw.text((self.width // 2, 470), "B. 1차 내가, 2차 상대가 (52%)", font=self._get_font(20, bold=True), fill=(255, 255, 255, 255), anchor="mm")

        draw.text((self.width // 2, 600), "나와 생각 똑같은 이성 18명 매칭!", font=self._get_font(20, bold=True), fill=(250, 204, 21, 255), anchor="mt")

    def _render_icebreaker(self, draw: ImageDraw.ImageDraw):
        f_title = self._get_font(26, bold=True)
        draw.rounded_rectangle([25, 140, self.width - 25, 750], radius=24, fill=(17, 24, 39, 255), outline=(34, 197, 94, 255), width=2)
        draw.text((self.width // 2, 175), "💬 AI 카톡 비서", font=f_title, fill=(74, 222, 128, 255), anchor="mt")

        draw.rounded_rectangle([45, 280, self.width - 120, 360], radius=16, fill=(55, 65, 81, 255))
        draw.text((65, 320), "주말에 보통 뭐 하세요? ㅎㅎ", font=self._get_font(18), fill=(255, 255, 255, 255), anchor="lm")

        draw.rounded_rectangle([45, 410, self.width - 45, 530], radius=16, fill=(34, 197, 94, 40), outline=(34, 197, 94, 255), width=2)
        draw.text((65, 435), "✨ AI 추천 답장 (답장률 98%)", font=self._get_font(16, bold=True), fill=(74, 222, 128, 255))
        draw.text((65, 475), '"성수동 카페투어 좋아해요!\n가보신 좋은 곳 있으세요?"', font=self._get_font(18, bold=True), fill=(255, 255, 255, 255))

    def _render_aura_diag(self, draw: ImageDraw.ImageDraw):
        f_title = self._get_font(26, bold=True)
        draw.rounded_rectangle([25, 140, self.width - 25, 750], radius=24, fill=(17, 24, 39, 255), outline=(234, 179, 8, 255), width=2)
        draw.text((self.width // 2, 175), "✨ 나의 아우라 진단", font=f_title, fill=(253, 224, 71, 255), anchor="mt")
        draw.text((self.width // 2, 280), "상위 3.8% [다정한 여우상]", font=self._get_font(24, bold=True), fill=(251, 191, 36, 255), anchor="mt")
        draw.text((self.width // 2, 340), "#성수동감성 #배려심99점 #티키타카", font=self._get_font(18), fill=(203, 213, 225, 255), anchor="mt")

    def _render_radar(self, draw: ImageDraw.ImageDraw):
        f_title = self._get_font(26, bold=True)
        draw.rounded_rectangle([25, 140, self.width - 25, 750], radius=24, fill=(17, 24, 39, 255), outline=(59, 130, 246, 255), width=2)
        draw.text((self.width // 2, 175), "🗺️ 500m 안심 레이더", font=f_title, fill=(96, 165, 250, 255), anchor="mt")
        draw.text((self.width // 2, 280), "📍 성수동 카페거리 (500m 안심 보호)", font=self._get_font(20, bold=True), fill=(255, 255, 255, 255), anchor="mt")
        draw.text((self.width // 2, 340), "집 주소 노출 0% • 안심 산책 메이트", font=self._get_font(18), fill=(74, 222, 128, 255), anchor="mt")
