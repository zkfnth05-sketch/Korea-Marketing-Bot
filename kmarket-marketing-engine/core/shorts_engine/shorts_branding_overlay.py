# -*- coding: utf-8 -*-
"""
ShortsBrandingOverlay (core/shorts_engine/shorts_branding_overlay.py)
===================================================================
- 3대 브랜드(Aura, Insurance, Stock) 숏폼 영상(1080x1920) 전용 브랜딩 오버레이 렌더러

[🚀 2026 대표님 최종 승인 개편 - 하단 네이버 검색 배너 100% 완전 제거]
  · 본문 숏폼 영상에서 하단 네이버 검색창 배너를 완전히 삭제 (코드 레벨 영구 배제)
  · 상단 좌측 다크 글래스모피즘 캡슐 뱃지만 투명 PNG 레이어로 남김
  · presets/branding_overlays/ 에 저장되는 PNG = 하단 배너 없는 깨끗한 상단 뱃지 전용 레이어
  · create_preview_on_photo 합성 시에도 상단 뱃지만 합성 (본문 몰입도 극대화)

[🚀 2026 대표님 긴급 지시 반영 - @handle 일체 제거 / 유니버설 뱃지 전면 개편]
  · 배경: 틱톡·유튜브 쇼츠·메타 릴스·네이버 클립 등 플랫폼마다 계정 아이디(@handle)가 달라
    영상에 특정 @handle 을 박으면 플랫폼별 불일치가 발생한다.
  · 조치: @handle 문자열을 영상 그래픽에서 완전히 배제하고,
    3대 앱(Aura / Insurance / Stock) 공통 '👇 프로필 링크 확인' 유니버설 뱃지로 일체화.
  · 규격: w=420, h=90 (핸들이 빠진 만큼 더 컴팩트하고 화면을 가리지 않는 세련된 캡슐)
  · 테두리: 브랜드별 고유 네온 컬러 유지 (Aura #F472B6 / Insurance #34D399 / Stock #FBBF24)
  · 배경: 반투명 럭셔리 다크 슬레이트 (2, 6, 23, 235), radius=45, width=3
  · 좌측 '👇' 이모지(font_emoji 36) + 우측 '프로필 링크 확인'(font_main 30 bold, 흰색)
  · get_bouncing_profile_badge_path() 는 기존 파일이 있더라도 신규 규격(420x90)이 아니면
    자동으로 덮어쓰기(갱신) 처리한다.

[무인 안전수칙]
  · `except: pass` 완전 배제 - 모든 예외는 logger.error 와 함께 명시적으로 처리
  · Playwright 렌더 실패 시 PIL 폴백으로 상단 뱃지 레이어를 반드시 생성 (무인 공정 중단 방지)
  · py_compile 무결점 검증 통과 필수
"""

import os
import sys

# Windows cp949 콘솔 안전 인코딩 보장
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError, OSError) as enc_err:
        # 콘솔 인코딩 재설정 실패는 치명적이지 않으나, 조용히 넘기지 않고 기록한다.
        print(f"[WARN] stdout 인코딩 재설정 실패: {enc_err}", file=sys.stderr)

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("ShortsBrandingOverlay")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
OVERLAYS_DIR = CURRENT_DIR / "presets" / "branding_overlays"
OVERLAYS_DIR.mkdir(parents=True, exist_ok=True)

# 1080x1920 세로 풀HD 규격 상수
CANVAS_W = 1080
CANVAS_H = 1920

# ==============================================================================
# [대표님 긴급 지시] 유니버설 뱃지 규격 상수 - 3대 앱 공통 단일 진실 공급원
# ==============================================================================
# [대표님 지시] 한 줄(Single Line) 초슬림 럭셔리 글래스모피즘 캡슐 규격
BOUNCING_BADGE_W = 560
BOUNCING_BADGE_H = 70
# Playwright 렌더 시 슈퍼샘플링 배율 (3x 렌더 -> LANCZOS 다운샘플 -> 레티나 선명도 확보)
BOUNCING_BADGE_SUPERSAMPLE = 3
BOUNCING_BADGE_LINE1_TEXT = "프로필 링크"
BOUNCING_BADGE_LINE2_PREFIX = "네이버"
# 구 규격(2단 뚱뚱한 박스) 판별 임계값 - 이 높이를 넘으면 자동 폐기/갱신
BOUNCING_BADGE_LEGACY_MAX_H = 70
# 하위 호환 별칭 (기존 참조 코드 보호)
BOUNCING_BADGE_TEXT = BOUNCING_BADGE_LINE1_TEXT
BOUNCING_BADGE_EMOJI = "👇"


class ShortsBrandingOverlay:
    """🎬 숏폼 영상 1080x1920 세로 풀HD 전용 상단 캡슐 뱃지 오버레이 엔진 (하단 배너 전면 폐기)"""

    # ==========================================================================
    # [핵심] 하단 네이버 검색 배너 영구 배제 플래그
    #   - 어떤 호출 경로에서도 하단 배너가 되살아나지 않도록 클래스 상수로 고정
    # ==========================================================================
    INCLUDE_BOTTOM_SEARCH = False

    # ==========================================================================
    # [대표님 긴급 지시] 유니버설 뱃지 규격 (클래스 상수로 외부 검증 가능)
    # ==========================================================================
    BOUNCING_BADGE_SIZE = (BOUNCING_BADGE_W, BOUNCING_BADGE_H)
    BOUNCING_BADGE_TEXT = BOUNCING_BADGE_TEXT
    BOUNCING_BADGE_EMOJI = BOUNCING_BADGE_EMOJI

    # ==========================================================================
    # [대표님 긴급 지시] @handle 일체 제거
    #   - profile_handle 은 내부 참조/로그용으로만 보존하며 영상 그래픽에는 절대 그리지 않는다.
    #   - sub_guide / cta_text 는 플랫폼 공통 유니버설 문구로 정규화한다.
    # ==========================================================================
    BRAND_CONFIGS = {
        "aura": {
            "icon": "💖",
            "brand_name": "AURA",
            "sub_text": "50:50 남녀 황금 성비",
            "sub_color_hex": "#F472B6",
            "sub_color_class": "text-pink-400",
            "keyword": "아우라AI데이팅",
            "profile_handle": "@aura_ai_dating",  # 내부 참조용 (영상 미표기)
            "sub_guide": "👇 프로필 링크 확인",
            "cta_text": "👇 프로필 링크 확인",
            "filename": "aura_branding_overlay_1080x1920.png"
        },
        "insurance": {
            "icon": "🛡️",
            "brand_name": "보험 리밸런스",
            "sub_text": "34개사 실시간 비교",
            "sub_color_hex": "#34D399",
            "sub_color_class": "text-emerald-400",
            "keyword": "보험 리밸런스",
            "profile_handle": "@insure_balance",  # 내부 참조용 (영상 미표기)
            "sub_guide": "👇 프로필 링크 확인",
            "cta_text": "👇 프로필 링크 확인",
            "filename": "insurance_branding_overlay_1080x1920.png"
        },
        "stock": {
            "icon": "📈",
            "brand_name": "StockMaster AI",
            "sub_text": "외인·기관 실시간 수급 포착",
            "sub_color_hex": "#FBBF24",
            "sub_color_class": "text-amber-400",
            "keyword": "스톡마스터 AI",
            "profile_handle": "@stock_master_ai",  # 내부 참조용 (영상 미표기)
            "sub_guide": "👇 프로필 링크 확인",
            "cta_text": "👇 프로필 링크 확인",
            "filename": "stock_branding_overlay_1080x1920.png"
        }
    }

    # ==========================================================================
    # [1] 상단 캡슐 뱃지 전용 HTML (하단 네이버 검색창 코드는 완전 삭제됨)
    # ==========================================================================
    @classmethod
    def build_overlay_html(
        cls,
        config: Dict[str, Any],
        include_bottom_search: bool = False
    ) -> str:
        """1080x1920 투명 오버레이 HTML — 상단 좌측 캡슐 뱃지 단일 레이어

        Args:
            config: 브랜드 설정 딕셔너리
            include_bottom_search: 하단 네이버 검색 배너 포함 여부.
                - 대표님 최종 승인에 따라 기본값 False 이며,
                - True 를 넘겨도 클래스 상수 INCLUDE_BOTTOM_SEARCH=False 에 의해 강제 무시된다.
        """
        if include_bottom_search:
            logger.warning(
                "⚠️ [ShortsBrandingOverlay] include_bottom_search=True 요청이 들어왔으나 "
                "대표님 최종 승인(하단 배너 100% 제거)에 따라 강제 무시합니다."
            )

        # 하단 배너는 어떤 경우에도 생성하지 않는다 (영구 배제)
        bottom_search_html = ""

        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdn.tailwindcss.com"></script>
<style>
  body {{
    background: transparent;
    margin: 0;
    padding: 0;
    width: {CANVAS_W}px;
    height: {CANVAS_H}px;
    overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Pretendard', 'Noto Sans KR', sans-serif;
  }}
</style>
</head>
<body>

  <!-- [1] 상단 좌측: 카드뉴스 표지 공식 다크 글래스모피즘 캡슐 뱃지 (유일 레이어) -->
  <div style="position:absolute; top:75px; left:50px;">
    <div class="inline-flex items-center gap-3.5 bg-slate-950/85 backdrop-blur-xl border border-white/25 rounded-full py-3.5 px-7 shadow-[0_12px_36px_rgba(0,0,0,0.7)]">
      <span class="text-3xl">{config["icon"]}</span>
      <span class="text-2xl font-black tracking-wider text-white">{config["brand_name"]}</span>
      <span class="text-lg font-bold {config["sub_color_class"]} pl-3.5 border-l border-white/30">{config["sub_text"]}</span>
    </div>
  </div>

  {bottom_search_html}

</body>
</html>"""

    # ==========================================================================
    # [2] PIL 폴백 렌더러 (Playwright 실패 시에도 상단 뱃지 레이어 보장)
    # ==========================================================================
    @classmethod
    def _hex_to_rgba(cls, hex_color: str, alpha: int = 255) -> tuple:
        """'#RRGGBB' 문자열을 RGBA 튜플로 변환"""
        try:
            h = hex_color.lstrip("#")
            if len(h) != 6:
                raise ValueError(f"잘못된 HEX 길이: {hex_color}")
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)
        except (ValueError, TypeError) as hex_err:
            logger.error(f"❌ [ShortsBrandingOverlay] HEX 색상 변환 실패 '{hex_color}': {hex_err}")
            return (255, 255, 255, alpha)

    @classmethod
    def _load_font(cls, size: int) -> ImageFont.FreeTypeFont:
        """한글 지원 폰트 로드 (Windows 맑은 고딕 우선, 실패 시 PIL 기본 폰트)"""
        candidates = [
            r"C:\Windows\Fonts\malgunbd.ttf",
            r"C:\Windows\Fonts\malgun.ttf",
            r"C:\Windows\Fonts\arialbd.ttf",
            "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
            "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        ]
        for fp in candidates:
            try:
                if os.path.exists(fp):
                    return ImageFont.truetype(fp, size)
            except (OSError, ValueError) as font_err:
                logger.warning(f"⚠️ [ShortsBrandingOverlay] 폰트 로드 실패 '{fp}': {font_err}")
                continue

        logger.warning("⚠️ [ShortsBrandingOverlay] 지정 폰트 미발견 - PIL 기본 폰트로 폴백")
        return ImageFont.load_default()

    @classmethod
    def _render_overlay_png_pil(cls, config: Dict[str, Any], out_path: str) -> str:
        """Playwright 불가 시 사용하는 PIL 폴백 - 상단 캡슐 뱃지 전용 투명 PNG 생성"""
        canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        # 캡슐 뱃지 기하 (HTML top:75px / left:50px 기준 정합)
        badge_x, badge_y = 50, 75
        badge_h = 84
        pad_x = 28
        gap = 14

        font_icon = cls._load_font(34)
        font_brand = cls._load_font(30)
        font_sub = cls._load_font(22)

        icon_text = str(config.get("icon", "🏷️"))
        brand_text = str(config.get("brand_name", "BRAND"))
        sub_text = str(config.get("sub_text", ""))

        def _text_w(txt: str, fnt) -> int:
            try:
                box = draw.textbbox((0, 0), txt, font=fnt)
                return int(box[2] - box[0])
            except (AttributeError, ValueError, OSError) as tb_err:
                logger.warning(f"⚠️ [ShortsBrandingOverlay] textbbox 실패 - 근사치 사용: {tb_err}")
                return int(len(txt) * getattr(fnt, "size", 20) * 0.9)

        w_icon = _text_w(icon_text, font_icon)
        w_brand = _text_w(brand_text, font_brand)
        w_sub = _text_w(sub_text, font_sub)
        divider_w = 2
        badge_w = pad_x * 2 + w_icon + gap + w_brand + gap + divider_w + gap + w_sub

        # 캡슐 배경 (다크 글래스모피즘 근사: 반투명 슬레이트 + 화이트 보더)
        draw.rounded_rectangle(
            [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
            radius=badge_h // 2,
            fill=(2, 6, 23, 217),
            outline=(255, 255, 255, 64),
            width=2,
        )

        # 텍스트 배치
        cy = badge_y + badge_h // 2
        cx = badge_x + pad_x
        try:
            draw.text((cx, cy), icon_text, font=font_icon, fill=(255, 255, 255, 255), anchor="lm")
            cx += w_icon + gap
            draw.text((cx, cy), brand_text, font=font_brand, fill=(255, 255, 255, 255), anchor="lm")
            cx += w_brand + gap
            draw.line(
                [(cx, cy - 20), (cx, cy + 20)],
                fill=(255, 255, 255, 77),
                width=divider_w,
            )
            cx += divider_w + gap
            sub_rgba = cls._hex_to_rgba(str(config.get("sub_color_hex", "#FFFFFF")), 255)
            draw.text((cx, cy), sub_text, font=font_sub, fill=sub_rgba, anchor="lm")
        except (OSError, ValueError, AttributeError) as draw_err:
            logger.error(f"❌ [ShortsBrandingOverlay] PIL 뱃지 텍스트 드로잉 실패: {draw_err}")
            raise RuntimeError(f"PIL 폴백 뱃지 렌더링 실패: {draw_err}") from draw_err

        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        canvas.save(out_path, "PNG")
        logger.info(f"🛟 [ShortsBrandingOverlay] PIL 폴백 상단 뱃지 생성 완료 -> {out_path}")
        return out_path

    # ==========================================================================
    # [3] 메인 렌더러 (Playwright 우선 → 실패 시 PIL 폴백)
    # ==========================================================================
    @classmethod
    def render_overlay_png(cls, brand_key: str, out_path: Optional[str] = None) -> str:
        """1080x1920 세로 풀HD 투명 오버레이 PNG 생성 — 상단 캡슐 뱃지 전용 (하단 배너 없음)"""
        config = cls.BRAND_CONFIGS.get(brand_key.lower())
        if not config:
            logger.error(f"❌ [ShortsBrandingOverlay] 지원하지 않는 브랜드 키: {brand_key}")
            raise ValueError(f"지원하지 않는 브랜드 키입니다: {brand_key}")

        if not out_path:
            out_path = str(OVERLAYS_DIR / config["filename"])

        Path(out_path).parent.mkdir(parents=True, exist_ok=True)

        # 하단 배너는 절대 포함하지 않는다 (INCLUDE_BOTTOM_SEARCH=False 고정)
        html_content = cls.build_overlay_html(config, include_bottom_search=cls.INCLUDE_BOTTOM_SEARCH)

        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                try:
                    page = browser.new_page(viewport={"width": CANVAS_W, "height": CANVAS_H})
                    page.set_content(html_content)
                    page.wait_for_timeout(500)
                    page.screenshot(path=out_path, omit_background=True)
                finally:
                    browser.close()

            logger.info(f"✅ [ShortsBrandingOverlay] 상단 뱃지 전용 투명 오버레이 렌더 완료: {brand_key.upper()} -> {out_path}")
            return out_path

        except Exception as pw_err:
            # Playwright 미설치/브라우저 부재/타임아웃 등 - 명시적 기록 후 PIL 폴백
            logger.error(
                f"❌ [ShortsBrandingOverlay] Playwright 렌더 실패 ({brand_key.upper()}): "
                f"{type(pw_err).__name__}: {pw_err} → PIL 폴백으로 전환합니다."
            )
            return cls._render_overlay_png_pil(config, out_path)

    # ==========================================================================
    # [4] 오버레이 경로 반환 (하단 배너 완전 배제 보장)
    # ==========================================================================
    @classmethod
    def get_overlay_path(cls, brand_key: str, force_refresh: bool = False) -> str:
        """브랜드별 1080x1920 상단 뱃지 전용 오버레이 파일 경로 반환 (필요시 자동 렌더링)

        - 하단 네이버 검색 배너는 기본적으로 완전히 배제된다.
        - 순수 상단 좌측 캡슐 뱃지만 포함된 투명 PNG 를 보장한다.
        """
        config = cls.BRAND_CONFIGS.get(brand_key.lower())
        if not config:
            logger.error(f"❌ [ShortsBrandingOverlay] 지원하지 않는 브랜드 키: {brand_key}")
            raise ValueError(f"지원하지 않는 브랜드 키입니다: {brand_key}")

        out_path = OVERLAYS_DIR / config["filename"]

        if force_refresh or not out_path.exists():
            logger.info(
                f"🎨 [ShortsBrandingOverlay] 오버레이 생성/갱신: {brand_key.upper()} "
                f"(force_refresh={force_refresh}, exists={out_path.exists()})"
            )
            cls.render_overlay_png(brand_key, str(out_path))
        else:
            logger.debug(f"♻️ [ShortsBrandingOverlay] 기존 상단 뱃지 레이어 재사용: {out_path}")

        if not Path(out_path).exists():
            logger.error(f"❌ [ShortsBrandingOverlay] 오버레이 파일 생성 실패: {out_path}")
            raise FileNotFoundError(f"오버레이 PNG 가 생성되지 않았습니다: {out_path}")

        return str(out_path)

    # ==========================================================================
    # [5] 실사 사진 위 미리보기 합성 (상단 뱃지만 합성)
    # ==========================================================================
    @classmethod
    def create_preview_on_photo(cls, brand_key: str, bg_image_path: str, out_preview_path: str) -> str:
        """실사 인물 사진 배경(1080x1920) 위에 상단 캡슐 뱃지만 정밀 합성

        - 하단 네이버 검색 배너는 합성하지 않는다 (본문 몰입도 극대화).
        """
        overlay_path = cls.get_overlay_path(brand_key)

        # 1. 배경 이미지 로드 및 1080x1920 맞춤
        try:
            bg = Image.open(bg_image_path).convert("RGBA")
        except (FileNotFoundError, OSError, ValueError) as bg_err:
            logger.error(f"❌ [ShortsBrandingOverlay] 배경 이미지 로드 실패 '{bg_image_path}': {bg_err}")
            raise RuntimeError(f"배경 이미지를 열 수 없습니다: {bg_image_path} ({bg_err})") from bg_err

        if bg.size != (CANVAS_W, CANVAS_H):
            logger.info(f"🔧 [ShortsBrandingOverlay] 배경 리사이즈: {bg.size} -> ({CANVAS_W}, {CANVAS_H})")
            bg = bg.resize((CANVAS_W, CANVAS_H), Image.Resampling.LANCZOS)

        # 2. 상단 뱃지 전용 투명 오버레이 로드
        try:
            overlay = Image.open(overlay_path).convert("RGBA")
        except (FileNotFoundError, OSError, ValueError) as ov_err:
            logger.error(f"❌ [ShortsBrandingOverlay] 오버레이 로드 실패 '{overlay_path}': {ov_err}")
            raise RuntimeError(f"오버레이 PNG 를 열 수 없습니다: {overlay_path} ({ov_err})") from ov_err

        if overlay.size != (CANVAS_W, CANVAS_H):
            logger.warning(
                f"⚠️ [ShortsBrandingOverlay] 오버레이 규격 불일치 {overlay.size} - "
                f"({CANVAS_W}, {CANVAS_H}) 로 정규화합니다."
            )
            overlay = overlay.resize((CANVAS_W, CANVAS_H), Image.Resampling.LANCZOS)

        # 3. 알파 채널 합성 (상단 뱃지만)
        combined = Image.alpha_composite(bg, overlay)

        # 4. 저장 (RGB)
        try:
            Path(out_preview_path).parent.mkdir(parents=True, exist_ok=True)
            combined.convert("RGB").save(out_preview_path, "PNG")
        except (OSError, ValueError) as save_err:
            logger.error(f"❌ [ShortsBrandingOverlay] 미리보기 저장 실패 '{out_preview_path}': {save_err}")
            raise RuntimeError(f"미리보기 PNG 저장 실패: {save_err}") from save_err

        logger.info(f"🖼️ [ShortsBrandingOverlay] 상단 뱃지 전용 미리보기 합성 완료 -> {out_preview_path}")
        return out_preview_path

    # ==========================================================================
    # [6] 🎯 [대표님 지시] 한 줄(Single Line) 초슬림 럭셔리 글래스모피즘 뱃지
    #     - 2단 뚱뚱한 박스 전면 폐기 -> 높이 58px 초슬림 다이내믹 캡슐
    #     - 이모지 깨짐 0%: 유니코드 이모지 대신 순수 SVG 벡터(다운 화살표/돋보기)
    #       + 네이버 공식 초록색 사각 [N] 엠블럼 CSS 뱃지
    #     - Playwright Chromium 1순위 렌더 (render_overlay_png 와 동일 아키텍처)
    #     - 레이아웃: [SVG↓ + '프로필 링크'] │ [초록 N + 네이버 '{keyword}' + SVG🔍]
    # ==========================================================================
    @classmethod
    def _build_bouncing_badge_html(cls, config: Dict[str, Any]) -> str:
        """한 줄 초슬림 럭셔리 뱃지 전용 HTML (순수 SVG 벡터 아이콘 + 네이버 [N] 엠블럼)"""
        keyword = str(config.get("keyword", "")).strip()
        neon = str(config.get("sub_color_hex", "#F472B6"))
        w, h = BOUNCING_BADGE_W, BOUNCING_BADGE_H

        # 순수 SVG 다운 화살표 (유니코드 이모지 미사용 -> 깨짐 0%) [120% 확대: 17 -> 23px]
        svg_arrow = (
            '<svg width="23" height="23" viewBox="0 0 24 24" fill="none" '
            'stroke="#FFFFFF" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M12 4v13"/><path d="M6 12l6 6 6-6"/></svg>'
        )
        # 순수 SVG 돋보기 (유니코드 이모지 미사용 -> 깨짐 0%) [120% 확대: 16 -> 20px]
        svg_search = (
            '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" '
            f'stroke="{neon}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">'
            '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21"/></svg>'
        )

        return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html, body {{ width:{w}px; height:{h}px; background:transparent; overflow:hidden; }}
  .wrap {{
    width:{w}px; height:{h}px;
    display:flex; align-items:center; justify-content:center;
    background:transparent;
  }}
  .capsule {{
    display:flex; align-items:center; justify-content:center;
    gap:13px;
    height:{h}px; padding:0 28px 0 24px;
    border-radius:35px;
    background:rgba(10, 15, 29, 0.95);
    border:1.5px solid {neon};
    box-shadow:0 0 16px {neon}66, 0 0 4px {neon}99, inset 0 1px 0 rgba(255,255,255,0.10);
    backdrop-filter:blur(14px);
    -webkit-backdrop-filter:blur(14px);
    font-family:'Malgun Gothic','맑은 고딕',sans-serif;
    white-space:nowrap;
  }}
  .seg {{ display:flex; align-items:center; gap:8px; }}
  .txt1 {{
    color:#FFFFFF; font-size:22px; font-weight:700; letter-spacing:-0.4px;
    text-shadow:0 1px 3px rgba(0,0,0,0.55);
  }}
  .divider {{
    width:1px; height:28px;
    background:rgba(255,255,255,0.22);
    flex:0 0 auto;
  }}
  .nbadge {{
    display:flex; align-items:center; justify-content:center;
    width:25px; height:25px; border-radius:6px;
    background:#03C75A;
    color:#FFFFFF; font-size:16px; font-weight:900;
    font-family:'Malgun Gothic','맑은 고딕',sans-serif;
    line-height:1; flex:0 0 auto;
    box-shadow:0 1px 4px rgba(3,199,90,0.45);
  }}
  .txt2 {{
    color:{neon}; font-size:22px; font-weight:700; letter-spacing:-0.4px;
    text-shadow:0 0 10px {neon}55;
  }}
</style></head>
<body>
  <div class="wrap">
    <div class="capsule">
      <div class="seg">{svg_arrow}<span class="txt1">{BOUNCING_BADGE_LINE1_TEXT}</span></div>
      <div class="divider"></div>
      <div class="seg"><span class="nbadge">N</span><span class="txt2">{BOUNCING_BADGE_LINE2_PREFIX} '{keyword}'</span>{svg_search}</div>
    </div>
  </div>
</body></html>"""

    @classmethod
    def _render_bouncing_badge_pil(cls, config: Dict[str, Any], out_path: str) -> str:
        """PIL 폴백 렌더러 - Playwright 부재/실패 시에도 뱃지 생성을 100% 보장

        유니코드 이모지 대신 벡터 도형(다운 화살표/돋보기)을 직접 그려 깨짐을 원천 차단한다.
        """
        w, h = BOUNCING_BADGE_W, BOUNCING_BADGE_H
        keyword = str(config.get("keyword", "")).strip()
        neon = str(config.get("sub_color_hex", "#F472B6"))
        neon_rgba = cls._hex_to_rgba(neon, alpha=255)

        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        # 1. 다크 아크릴 글래스 캡슐 + 브랜드 네온 1.5px 테두리 [120% 확대: radius 35]
        draw.rounded_rectangle(
            [(1, 1), (w - 2, h - 2)],
            radius=35,
            fill=(10, 15, 29, 242),
            outline=neon_rgba,
            width=2,
        )

        font_main = cls._load_font(22)
        font_n = cls._load_font(16)

        # 2. 좌측 SVG 다운 화살표 (벡터 직접 드로잉) [120% 확대: 23px 상당]
        ax, ay = 24, h // 2
        draw.line([(ax, ay - 10), (ax, ay + 7)], fill=(255, 255, 255, 255), width=3)
        draw.line([(ax - 7, ay), (ax, ay + 7)], fill=(255, 255, 255, 255), width=3)
        draw.line([(ax + 7, ay), (ax, ay + 7)], fill=(255, 255, 255, 255), width=3)

        # 3. '프로필 링크' (White bold)
        t1 = BOUNCING_BADGE_LINE1_TEXT
        b1 = draw.textbbox((0, 0), t1, font=font_main)
        x1 = ax + 16
        y1 = (h - (b1[3] - b1[1])) // 2 - b1[1]
        draw.text((x1, y1), t1, font=font_main, fill=(255, 255, 255, 255))
        x1_end = x1 + (b1[2] - b1[0])

        # 4. 1px 수직 디바이더 [120% 확대: height 28]
        dx = x1_end + 16
        draw.line([(dx, 21), (dx, h - 21)], fill=(255, 255, 255, 56), width=1)

        # 5. 네이버 공식 초록색 사각 [N] 엠블럼 [120% 확대: 25x25, font 16]
        nx = dx + 16
        ny = (h - 25) // 2
        draw.rounded_rectangle([(nx, ny), (nx + 25, ny + 25)], radius=6, fill=(3, 199, 90, 255))
        nb = draw.textbbox((0, 0), "N", font=font_n)
        draw.text(
            (nx + (25 - (nb[2] - nb[0])) // 2 - nb[0], ny + (25 - (nb[3] - nb[1])) // 2 - nb[1]),
            "N", font=font_n, fill=(255, 255, 255, 255),
        )

        # 6. "네이버 '{keyword}'" (브랜드 네온 컬러)
        t2 = f"{BOUNCING_BADGE_LINE2_PREFIX} '{keyword}'"
        b2 = draw.textbbox((0, 0), t2, font=font_main)
        x2 = nx + 34
        y2 = (h - (b2[3] - b2[1])) // 2 - b2[1]
        draw.text((x2, y2), t2, font=font_main, fill=neon_rgba)
        x2_end = x2 + (b2[2] - b2[0])

        # 7. 우측 SVG 돋보기 (벡터 직접 드로잉) [120% 확대: 20px 상당]
        sx, sy = x2_end + 18, h // 2 - 1
        draw.ellipse([(sx - 7, sy - 7), (sx + 7, sy + 7)], outline=neon_rgba, width=2)
        draw.line([(sx + 6, sy + 6), (sx + 12, sy + 12)], fill=neon_rgba, width=2)

        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        canvas.save(out_path, "PNG")
        logger.info(
            f"✨ [ShortsBrandingOverlay] 한 줄 초슬림 뱃지 생성 완료(PIL 폴백) -> {out_path} "
            f"(size={w}x{h}, text=\"{t1} | {t2}\", border={neon})"
        )
        return out_path

    @classmethod
    def render_bouncing_profile_badge(cls, brand_key: str, out_path: Optional[str] = None) -> str:
        """한 줄(Single Line) 초슬림 럭셔리 글래스모피즘 뱃지 생성

        [대표님 지시]
          · 규격: w=560, h=70 (120% 확대 럭셔리 캡슐, 3x 슈퍼샘플링 다운샘플)
          · 배경: rgba(10, 15, 29, 0.95) 다크 아크릴 글래스
          · 테두리: 브랜드 네온 컬러 1.5px + 네온 림라이트 글로우
          · 레이아웃: [SVG↓ + '프로필 링크'] │ [초록 N + 네이버 '{keyword}' + SVG🔍]
          · 이모지 깨짐 0%: 유니코드 이모지 대신 순수 SVG 벡터 + CSS [N] 엠블럼
          · Playwright Chromium 1순위 → 실패 시 PIL 폴백
        """
        brand_key = (brand_key or "aura").lower().strip()
        config = cls.BRAND_CONFIGS.get(brand_key, cls.BRAND_CONFIGS["aura"])

        if not out_path:
            out_path = str(OVERLAYS_DIR / f"{brand_key}_bouncing_profile_badge.png")

        Path(out_path).parent.mkdir(parents=True, exist_ok=True)

        # 1순위: Playwright Chromium 고화질 렌더 (3x 슈퍼샘플링 -> LANCZOS 다운샘플)
        try:
            from playwright.sync_api import sync_playwright
            html_content = cls._build_bouncing_badge_html(config)
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                try:
                    page = browser.new_page(
                        viewport={"width": BOUNCING_BADGE_W, "height": BOUNCING_BADGE_H},
                        device_scale_factor=BOUNCING_BADGE_SUPERSAMPLE,
                    )
                    page.set_content(html_content)
                    page.wait_for_timeout(320)
                    page.screenshot(path=out_path, omit_background=True)
                finally:
                    browser.close()

            # [대표님 지시] 3x 슈퍼샘플링 캡처본을 정확히 (560, 58) 로 LANCZOS 다운샘플링하여 덮어쓰기
            #   -> 벡터/글꼴 안티앨리어싱 극대화 + 파일 규격 100% 고정
            try:
                with Image.open(out_path) as im:
                    raw_size = im.size
                    im.resize(
                        (BOUNCING_BADGE_W, BOUNCING_BADGE_H),
                        Image.Resampling.LANCZOS,
                    ).save(out_path, "PNG")
                logger.info(
                    f"🔎 [ShortsBrandingOverlay] 슈퍼샘플링 다운샘플 완료: {raw_size} -> "
                    f"({BOUNCING_BADGE_W}, {BOUNCING_BADGE_H}) LANCZOS"
                )
            except (FileNotFoundError, OSError, ValueError) as rs_err:
                logger.error(
                    f"❌ [ShortsBrandingOverlay] 슈퍼샘플링 다운샘플 실패 ({brand_key.upper()}): "
                    f"{type(rs_err).__name__}: {rs_err} → 원본 캡처본을 그대로 사용합니다."
                )

            logger.info(
                f"✅ [ShortsBrandingOverlay] 한 줄 초슬림 뱃지 렌더 완료(Playwright) -> {out_path} "
                f"(size={BOUNCING_BADGE_W}x{BOUNCING_BADGE_H}, border={config.get('sub_color_hex')})"
            )
            return out_path

        except Exception as pw_err:
            logger.error(
                f"❌ [ShortsBrandingOverlay] Playwright 뱃지 렌더 실패 ({brand_key.upper()}): "
                f"{type(pw_err).__name__}: {pw_err} → PIL 폴백으로 전환합니다."
            )
            return cls._render_bouncing_badge_pil(config, out_path)

    @classmethod
    def get_bouncing_profile_badge_path(cls, brand_key: str = "aura", force_refresh: bool = False) -> str:
        """한 줄 초슬림 뱃지 PNG 경로 반환

        [대표님 지시] 기존 파일이 존재하더라도 구 규격(2단 뚱뚱한 박스, h > 70)이면
        자동으로 새 한 줄 럭셔리 뱃지로 갱신하여 구 규격 잔존을 원천 차단한다.
        """
        brand_key = (brand_key or "aura").lower().strip()
        out_path = OVERLAYS_DIR / f"{brand_key}_bouncing_profile_badge.png"

        need_render = bool(force_refresh) or (not out_path.exists())

        # 기존 파일 규격 검사 - 구 규격(h > 70) 또는 신규 규격 불일치 시 강제 갱신
        if not need_render:
            try:
                with Image.open(out_path) as existing:
                    existing_size = existing.size
                ex_w, ex_h = int(existing_size[0]), int(existing_size[1])
                if ex_h > BOUNCING_BADGE_LEGACY_MAX_H or (ex_w, ex_h) != (BOUNCING_BADGE_W, BOUNCING_BADGE_H):
                    logger.info(
                        f"🔄 [ShortsBrandingOverlay] 구 규격 뱃지 감지 {existing_size} → "
                        f"신규 한 줄 초슬림 규격 ({BOUNCING_BADGE_W}x{BOUNCING_BADGE_H}) 으로 갱신: {out_path}"
                    )
                    need_render = True
            except (FileNotFoundError, OSError, ValueError) as chk_err:
                logger.warning(
                    f"⚠️ [ShortsBrandingOverlay] 기존 뱃지 규격 확인 실패 - 재생성합니다: {chk_err}"
                )
                need_render = True

        if need_render:
            cls.render_bouncing_profile_badge(brand_key, str(out_path))

        if not Path(out_path).exists():
            logger.error(f"❌ [ShortsBrandingOverlay] 한 줄 뱃지 파일 생성 실패: {out_path}")
            raise FileNotFoundError(f"한 줄 뱃지 PNG 가 생성되지 않았습니다: {out_path}")

        return str(out_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
    for b in ["aura", "insurance", "stock"]:
        out = ShortsBrandingOverlay.render_overlay_png(b)
        print(f"Overlay created (top badge only): {b} -> {out}")
        badge = ShortsBrandingOverlay.get_bouncing_profile_badge_path(b, force_refresh=True)
        print(f"Universal bouncing badge created: {b} -> {badge}")
