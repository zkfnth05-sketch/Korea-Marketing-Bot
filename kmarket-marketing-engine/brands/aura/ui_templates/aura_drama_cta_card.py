# -*- coding: utf-8 -*-
"""
AuraDramaCTACard - 🏷️ [Aura 숏드라마 전용 독립 레고 블록 — 범용 럭셔리 엔딩 CTA 카드]
===================================================================================================
🆕 100% 완전 독립 신규 모듈 (기존 aura_cta_card.py 는 단 1바이트도 건드리지 않음)
---------------------------------------------------------------------------------------------------
- 1080x1920 세로 풀HD 규격 (숏폼 9:16 표준)
- 복잡한 찬반투표 옵션 / 작은 글씨 혜택박스 전면 배제
  → 어떤 드라마 스토리에도 공통 적용되는 '범용 럭셔리 엔딩 CTA' 단일 화면
- 기존 다크 퍼플 / 글래스모피즘 + 앰비언트 글로우 미학 100% 계승
- Playwright Chromium headless 초고화질 렌더링 + FFmpeg 무손실 stillimage 클립 인코딩

[🎨 디자인 구성 — 위에서 아래로]
  1. 상단 럭셔리 캡슐 뱃지 : 💖 AURA | 50:50 남녀 황금 성비
  2. 골드 디바이더        : — A U R A   D A T I N G   G U A R D I A N —
  3. 메인 헤드라인        : 대한민국 상위 0.5% 프리미엄 AI 데이팅
                            "내게 딱 맞는 이상형, 지금 바로 만나보세요"
  4. 3대 안심 혜택 미니 뱃지 : ✔ AI 매칭 3초 확인 | ✔ 50:50 황금 성비 보장 | ✔ 실명인증 VIP 라운지
  5. 메가 네온 펄싱 CTA 버튼 : 👉 프로필 링크 & 고정 댓글 터치!
                            ✨ 3초 만에 내 매력 점수 & 이상형 무료 매칭 바로가기 ✨
  6. 안내 가이드          : 👇 화면 좌측 하단 계정 프로필(@aura_ai_dating) 또는 고정 댓글 링크...
  7. 하단 푸터            : Official Web: https://aura-ai-dating.vercel.app/ | 네이버 검색: 아우라AI데이팅

[🔌 공개 API — 레고 블록 결합면]
  · render_cta_image(output_path: Optional[Path] = None) -> Image.Image
  · create_cta_clip(output_path: Path, audio_path: Path, duration_sec: float = 4.0) -> Path
  · generate_html_template() -> str   (디자인 단독 검수용)
===================================================================================================
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from PIL import Image

logger = logging.getLogger("AuraDramaCTACard")


class AuraDramaCTACard:
    """Aura 숏드라마 전용 범용 럭셔리 엔딩 CTA 카드 (1080x1920) — 독립 레고 블록"""

    # ==========================================================================
    # 📐 [출력 규격]
    # ==========================================================================
    WIDTH: int = 1080
    HEIGHT: int = 1920
    FPS: int = 30

    # ==========================================================================
    # ✍️ [카피 마스터 데이터 — 범용 럭셔리 엔딩 CTA]
    #    드라마 주제(소개팅 탈출/자막 통화/성비 게이트/화보 보정 등)와 무관하게
    #    어떤 스토리 뒤에도 자연스럽게 붙는 공통 엔딩 문구만 사용한다.
    # ==========================================================================
    CAPSULE_BADGE: str = "💖 AURA | 가입비 0원 · 100% 완전 무료"
    GOLD_DIVIDER_TEXT: str = "— 1 0 0 %   F R E E   A I   D A T I N G —"

    HEADLINE_MAIN: str = "대한민국 상위 0.5% 프리미엄 AI 데이팅"
    HEADLINE_SUB: str = '"가입비·매칭비 0원! 모든 비용 없이 100% 완전 무료"'

    # 3대 안심 혜택 (심플 한 줄 — 작은 글씨 혜택박스 배제)
    BENEFIT_ITEMS: tuple = (
        "모든 비용 0원 완전 무료",
        "50:50 황금 성비 보장",
        "실명인증 VIP 3초 매칭",
    )

    CTA_BUTTON_MAIN: str = "👉 프로필 링크 & 고정 댓글 터치!"
    CTA_BUTTON_SUB: str = "✨ 가입비 0원! 100% 완전 무료 이상형 매칭 바로가기 ✨"

    GUIDE_TEXT: str = (
        "👇 화면 좌측 하단 계정 프로필(@aura_ai_dating) 또는 "
        "고정 댓글 링크를 누르면 100% 무료 매칭 즉시 시작!"
    )

    OFFICIAL_WEB: str = "https://aura-ai-dating.vercel.app/"
    NAVER_KEYWORD: str = "아우라AI데이팅"
    PROFILE_HANDLE: str = "@aura_ai_dating"

    # 🎨 [디자인 토큰 — 기존 다크 퍼플/글래스모피즘 + 앰비언트 글로우 미학 계승]
    COLOR_BG_OUTER: str = "#040307"
    COLOR_BG_MID: str = "#0d0915"
    COLOR_BG_INNER: str = "#1f1429"
    COLOR_GOLD: str = "#fb923c"
    COLOR_GOLD_SOFT: str = "#fcd34d"
    COLOR_AMBER_TEXT: str = "#fbbf24"

    # 🎬 [FFmpeg 인코딩 규격]
    CRF: int = 16          # 선명도 100% 무손실 지향 (기존 20 → 16 상향)
    PRESET: str = "slow"   # stillimage 정지화면은 slow 프리셋이 압도적으로 유리 (시간 여유 충분)
    AUDIO_BITRATE: str = "192k"
    AUDIO_RATE: int = 48000
    AUDIO_CHANNELS: int = 2

    def __init__(self, ffmpeg_exe: Optional[str] = None):
        self.ffmpeg_exe = ffmpeg_exe or self._resolve_ffmpeg()
        logger.info(f"🏷️ [AuraDramaCTACard] FFmpeg 바이너리 확정: {self.ffmpeg_exe}")

    # ==========================================================================
    # 🛠️ [FFmpeg 바이너리 탐색 — imageio_ffmpeg 최우선, 실패 시 명시적 오류]
    # ==========================================================================
    def _resolve_ffmpeg(self) -> str:
        """imageio_ffmpeg 번들 바이너리 우선 채택, 미설치 시 PATH → 명시적 오류."""
        try:
            import imageio_ffmpeg  # type: ignore

            bundled = imageio_ffmpeg.get_ffmpeg_exe()
            if bundled and Path(bundled).exists():
                return str(bundled)
            logger.warning(f"⚠️ [AuraDramaCTACard] imageio_ffmpeg 경로 부재: {bundled}")
        except ImportError as exc:
            logger.warning(f"⚠️ [AuraDramaCTACard] imageio_ffmpeg 미설치({exc}) → PATH 탐색")

        which_path = shutil.which("ffmpeg")
        if which_path:
            return which_path

        logger.error(
            "🚨 [AuraDramaCTACard] ffmpeg 바이너리 미발견 — "
            "`pip install imageio-ffmpeg` 설치가 필요합니다. 문자열 'ffmpeg' 로 강행합니다."
        )
        return "ffmpeg"

    # ==========================================================================
    # 🎨 [HTML 템플릿] 1080x1920 범용 럭셔리 엔딩 CTA 카드
    # ==========================================================================
    def generate_html_template(self) -> str:
        """1080x1920 숏폼 규격 범용 럭셔리 엔딩 CTA HTML 생성 (찬반투표/혜택박스 배제)."""
        benefit_html = "".join(
            f"""
          <div class="benefit-chip">
            <span class="benefit-check">✔</span>
            <span class="benefit-label">{item}</span>
          </div>"""
            for item in self.BENEFIT_ITEMS
        )

        return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Aura Drama Ending CTA (1080x1920)</title>
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
      -webkit-font-smoothing: antialiased;
      font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}

    html, body {{
      width: {self.WIDTH}px;
      height: {self.HEIGHT}px;
      overflow: hidden;
    }}

    body {{
      background: radial-gradient(circle at 50% 22%, {self.COLOR_BG_INNER} 0%, {self.COLOR_BG_MID} 55%, {self.COLOR_BG_OUTER} 100%);
      color: #ffffff;
      position: relative;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: space-between;
      padding: 84px 56px 56px;
    }}

    /* ── Ambient Glow (앰비언트 글로우) ── */
    .glow {{
      position: absolute;
      border-radius: 9999px;
      pointer-events: none;
      filter: blur(180px);
    }}
    .glow-top {{
      width: 980px; height: 980px;
      top: -140px; left: 50%;
      transform: translateX(-50%);
      background: rgba(249, 115, 22, 0.13);
    }}
    .glow-bottom {{
      width: 860px; height: 860px;
      bottom: -120px; right: -140px;
      background: rgba(236, 72, 153, 0.12);
    }}
    .glow-center {{
      width: 720px; height: 720px;
      top: 46%; left: 50%;
      transform: translate(-50%, -50%);
      background: rgba(168, 85, 247, 0.10);
    }}

    /* ── 1. 상단 럭셔리 캡슐 뱃지 ── */
    .capsule-badge {{
      position: relative;
      z-index: 10;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 20px 52px;
      border-radius: 9999px;
      background: linear-gradient(135deg, rgba(249, 115, 22, 0.22) 0%, rgba(236, 72, 153, 0.16) 100%);
      border: 1.5px solid rgba(251, 146, 60, 0.62);
      box-shadow: 0 0 46px rgba(249, 115, 22, 0.34), inset 0 0 26px rgba(251, 146, 60, 0.14);
      backdrop-filter: blur(26px);
      -webkit-backdrop-filter: blur(26px);
      font-size: 34px;
      font-weight: 900;
      letter-spacing: -0.01em;
      color: #ffffff;
      white-space: nowrap;
    }}

    /* ── 2. 골드 디바이더 ── */
    .divider-block {{
      position: relative;
      z-index: 10;
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 14px;
      margin-top: 36px;
    }}
    .gold-line {{
      width: 100%;
      height: 1.5px;
      background: linear-gradient(90deg, rgba(251, 146, 60, 0) 0%, rgba(251, 146, 60, 0.88) 50%, rgba(251, 146, 60, 0) 100%);
    }}
    .divider-text {{
      font-size: 21px;
      font-weight: 800;
      letter-spacing: 0.30em;
      color: {self.COLOR_GOLD_SOFT};
      text-transform: uppercase;
      white-space: nowrap;
    }}

    /* ── 3. 메인 헤드라인 ── */
    .headline-block {{
      position: relative;
      z-index: 10;
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      gap: 26px;
      margin-top: 52px;
    }}
    .headline-main {{
      font-size: 62px;
      font-weight: 900;
      line-height: 1.24;
      letter-spacing: -0.035em;
      background: linear-gradient(180deg, #ffffff 0%, #ffe9c9 100%);
      -webkit-background-clip: text;
      background-clip: text;
      -webkit-text-fill-color: transparent;
      text-shadow: 0 0 60px rgba(251, 146, 60, 0.30);
    }}
    .headline-sub {{
      font-size: 40px;
      font-weight: 800;
      line-height: 1.42;
      letter-spacing: -0.02em;
      color: #fde3c0;
      text-shadow: 0 0 40px rgba(249, 115, 22, 0.28);
    }}

    /* ── 4. 3대 안심 혜택 미니 뱃지 (심플 한 줄) ── */
    .benefit-row {{
      position: relative;
      z-index: 10;
      width: 100%;
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: center;
      gap: 14px;
      margin-top: 44px;
      flex-wrap: nowrap;
    }}
    .benefit-chip {{
      display: inline-flex;
      align-items: center;
      gap: 9px;
      padding: 15px 22px;
      border-radius: 9999px;
      background: rgba(255, 255, 255, 0.055);
      border: 1px solid rgba(251, 146, 60, 0.34);
      backdrop-filter: blur(18px);
      -webkit-backdrop-filter: blur(18px);
      white-space: nowrap;
    }}
    .benefit-check {{
      font-size: 22px;
      font-weight: 900;
      color: #34d399;
    }}
    .benefit-label {{
      font-size: 22px;
      font-weight: 800;
      color: #e8e3f0;
      letter-spacing: -0.01em;
    }}

    /* ── 5. 메가 네온 펄싱 CTA 버튼 (중앙 압도적 시인성) ── */
    .cta-wrap {{
      position: relative;
      z-index: 10;
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 16px;
      margin-top: auto;
      margin-bottom: auto;
    }}
    .cta-button {{
      width: 100%;
      border-radius: 40px;
      padding: 44px 40px;
      background: linear-gradient(100deg, #db2777 0%, #f43f5e 46%, #f59e0b 100%);
      border: 2.5px solid rgba(255, 255, 255, 0.55);
      box-shadow:
        0 0 90px rgba(244, 63, 94, 0.62),
        0 0 150px rgba(245, 158, 11, 0.34),
        inset 0 0 60px rgba(255, 255, 255, 0.14);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 18px;
      text-align: center;
    }}
    .cta-main-row {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 18px;
    }}
    .cta-emoji {{
      font-size: 62px;
      line-height: 1;
    }}
    .cta-main-text {{
      font-size: 54px;
      font-weight: 900;
      letter-spacing: -0.035em;
      color: #ffffff;
      text-shadow: 0 6px 26px rgba(0, 0, 0, 0.42);
      white-space: nowrap;
    }}
    .cta-sub-text {{
      font-size: 27px;
      font-weight: 800;
      letter-spacing: -0.01em;
      color: #fff3d6;
      text-shadow: 0 3px 16px rgba(0, 0, 0, 0.38);
      line-height: 1.36;
    }}

    /* ── 6. 안내 가이드 ── */
    .guide-text {{
      position: relative;
      z-index: 10;
      width: 100%;
      text-align: center;
      font-size: 25px;
      font-weight: 800;
      line-height: 1.46;
      letter-spacing: -0.015em;
      color: #fda4af;
      text-shadow: 0 0 34px rgba(244, 63, 94, 0.42);
    }}

    /* ── 6-1. 🟢 네이버 그린 검색창 (Glow Naver Search Bar) — 레퍼런스 100% 일치 ── */
    .naver-wrap {{
      position: relative;
      z-index: 10;
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 16px;
      margin-top: 4px;
    }}
    .naver-search-box {{
      background: #ffffff;
      border-radius: 28px;
      padding: 20px 28px;
      border: 3.5px solid #03C75A;
      box-shadow: 0 0 35px rgba(3, 199, 90, 0.45);
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      max-width: 960px;
    }}
    .naver-left {{
      display: flex;
      align-items: center;
      gap: 18px;
    }}
    .naver-logo {{
      width: 52px;
      height: 52px;
      background: #03C75A;
      border-radius: 14px;
      color: #ffffff;
      font-weight: 900;
      font-size: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }}
    .naver-text-col {{
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: 3px;
    }}
    .naver-sub-label {{
      font-size: 15px;
      font-weight: 700;
      color: #64748b;
      line-height: 1.3;
      letter-spacing: -0.01em;
    }}
    .naver-keyword-label {{
      font-size: 36px;
      font-weight: 900;
      color: #000000;
      line-height: 1.2;
      letter-spacing: -0.035em;
      white-space: nowrap;
    }}
    .naver-search-btn {{
      background: #03C75A;
      color: #ffffff;
      font-weight: 900;
      font-size: 24px;
      padding: 14px 32px;
      border-radius: 16px;
      display: flex;
      align-items: center;
      gap: 8px;
      flex-shrink: 0;
      white-space: nowrap;
    }}
    .naver-sub-pill {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 12px 32px;
      border-radius: 9999px;
      background: rgba(15, 23, 42, 0.88);
      border: 1.5px solid rgba(244, 63, 94, 0.5);
      font-size: 22px;
      font-weight: 800;
      color: #fda4af;
      letter-spacing: -0.015em;
      white-space: nowrap;
      text-align: center;
    }}

    /* ── 7. 하단 푸터 ── */
    .footer {{
      position: relative;
      z-index: 10;
      width: 100%;
      padding-top: 26px;
      border-top: 1px solid rgba(255, 255, 255, 0.11);
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 10px;
      text-align: center;
    }}
    .footer-line {{
      font-size: 21px;
      font-weight: 600;
      color: #94a3b8;
      letter-spacing: -0.01em;
      white-space: nowrap;
    }}
    .footer-web {{
      color: {self.COLOR_AMBER_TEXT};
      font-weight: 800;
    }}
    .footer-keyword {{
      color: #e2e8f0;
      font-weight: 800;
    }}
    .footer-copy {{
      font-size: 17px;
      font-weight: 500;
      color: #64748b;
      letter-spacing: 0.02em;
    }}
  </style>
</head>
<body>

  <!-- Ambient Glows -->
  <div class="glow glow-top"></div>
  <div class="glow glow-center"></div>
  <div class="glow glow-bottom"></div>

  <!-- 1. 상단 럭셔리 캡슐 뱃지 -->
  <div class="capsule-badge">{self.CAPSULE_BADGE}</div>

  <!-- 2. 골드 디바이더 -->
  <div class="divider-block">
    <div class="gold-line"></div>
    <p class="divider-text">{self.GOLD_DIVIDER_TEXT}</p>
    <div class="gold-line"></div>
  </div>

  <!-- 3. 메인 헤드라인 -->
  <div class="headline-block">
    <h1 class="headline-main">{self.HEADLINE_MAIN}</h1>
    <p class="headline-sub">{self.HEADLINE_SUB}</p>
  </div>

  <!-- 4. 3대 안심 혜택 미니 뱃지 -->
  <div class="benefit-row">{benefit_html}
  </div>

  <!-- 5. 메가 네온 펄싱 CTA 버튼 -->
  <div class="cta-wrap">
    <div class="cta-button">
      <div class="cta-main-row">
        <span class="cta-emoji">👉</span>
        <span class="cta-main-text">프로필 링크 &amp; 고정 댓글 터치!</span>
      </div>
      <p class="cta-sub-text">{self.CTA_BUTTON_SUB}</p>
    </div>

    <!-- 6. 안내 가이드 -->
    <p class="guide-text">{self.GUIDE_TEXT}</p>
  </div>

  <!-- 6-1. 네이버 그린 검색창 -->
  <div class="naver-wrap">
    <div class="naver-search-box">
      <div class="naver-left">
        <div class="naver-logo">N</div>
        <div class="naver-text-col">
          <p class="naver-sub-label">네이버 검색창에 입력하세요</p>
          <p class="naver-keyword-label">{self.NAVER_KEYWORD}</p>
        </div>
      </div>
      <div class="naver-search-btn">
        <span>검색 🔍</span>
      </div>
    </div>
    <div class="naver-sub-pill">👉 네이버에 '{self.NAVER_KEYWORD}' 검색 또는 상단 프로필 링크 클릭!</div>
  </div>

  <!-- 7. 하단 푸터 -->
  <div class="footer">
    <p class="footer-line">
      <span>Official Web:</span>
      <span class="footer-web">{self.OFFICIAL_WEB}</span>
      <span> | 네이버 검색:</span>
      <span class="footer-keyword">{self.NAVER_KEYWORD}</span>
    </p>
    <p class="footer-copy">© 2026 AURA AI Dating. All rights reserved.</p>
  </div>

</body>
</html>
"""

    # ==========================================================================
    # 🖼️ [공개 API 1] Playwright Chromium headless → 1080x1920 PIL Image
    # ==========================================================================
    def render_cta_image(self, output_path: Optional[Path] = None) -> Image.Image:
        """
        1080x1920 범용 럭셔리 엔딩 CTA 카드를 Playwright Chromium headless 로 렌더링한다.

        Args:
            output_path: PNG 저장 경로 (선택). 지정 시 렌더 결과를 디스크에 저장한다.

        Returns:
            Image.Image: 1080x1920 RGB PIL 이미지

        Raises:
            RuntimeError: Playwright 미설치 또는 렌더링 실패
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise RuntimeError(
                "❌ [AuraDramaCTACard] playwright 미설치 — "
                "`pip install playwright && playwright install chromium` 필요"
            ) from exc

        html_code = self.generate_html_template()

        temp_dir = Path(tempfile.mkdtemp(prefix="aura_drama_cta_img_"))
        temp_html = temp_dir / "drama_cta.html"
        temp_png = temp_dir / "drama_cta.png"

        try:
            with open(temp_html, "w", encoding="utf-8") as f:
                f.write(html_code)

            logger.info("🎨 [AuraDramaCTACard] Playwright Chromium headless 렌더링 착수 (1080x1920)...")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                try:
                    page = browser.new_page(
                        viewport={"width": self.WIDTH, "height": self.HEIGHT},
                        device_scale_factor=1,
                    )
                    page.goto(temp_html.as_uri())
                    # 웹폰트(Pretendard) 로드 완료까지 대기 — 폰트 미적용 렌더 방지
                    try:
                        page.wait_for_load_state("networkidle", timeout=8000)
                    except Exception as exc:  # noqa: BLE001 — CDN 지연은 치명적이지 않음
                        logger.warning(f"⚠️ [AuraDramaCTACard] networkidle 대기 초과(무해): {exc}")
                    page.wait_for_timeout(700)
                    page.screenshot(path=str(temp_png), type="png")
                finally:
                    browser.close()

            if not temp_png.exists() or temp_png.stat().st_size <= 0:
                raise RuntimeError("❌ [AuraDramaCTACard] 스크린샷 PNG 미생성")

            img = Image.open(str(temp_png)).convert("RGB")

            # 규격 강제 검증 — 1080x1920 이 아니면 즉시 실패 (규격 위반 은폐 금지)
            if img.size != (self.WIDTH, self.HEIGHT):
                raise RuntimeError(
                    f"❌ [AuraDramaCTACard] 렌더 규격 위반: {img.size} "
                    f"(기대값 {(self.WIDTH, self.HEIGHT)})"
                )

            if output_path is not None:
                out_p = Path(output_path)
                out_p.parent.mkdir(parents=True, exist_ok=True)
                img.save(str(out_p), "PNG")
                logger.info(f"✅ [AuraDramaCTACard] CTA 카드 이미지 저장 완료: {out_p}")

            logger.info(f"✅ [AuraDramaCTACard] CTA 카드 렌더링 완료: {img.size[0]}x{img.size[1]}")
            return img

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    # ==========================================================================
    # 🎬 [공개 API 2] FFmpeg 무손실 stillimage 루프 → 4초 비디오 클립
    # ==========================================================================
    def create_cta_clip(
        self,
        output_path: Path,
        audio_path: Path,
        duration_sec: float = 4.0,
    ) -> Path:
        """
        CTA 카드 이미지를 고화질 stillimage 루프로 duration_sec 길이의 MP4 클립으로 인코딩한다.

        Args:
            output_path: 출력 MP4 경로
            audio_path: Cut 4 오디오 경로 (AAC 192k / 48kHz / 스테레오 재인코딩)
            duration_sec: 클립 길이 (기본 4.0초)

        Returns:
            Path: 생성된 MP4 경로

        Raises:
            RuntimeError: FFmpeg 인코딩 실패 또는 산출물 미생성
        """
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        aud_p = Path(audio_path)
        if not aud_p.exists():
            raise FileNotFoundError(f"❌ [AuraDramaCTACard] CTA 오디오 없음: {aud_p}")

        duration = float(duration_sec) if duration_sec and duration_sec > 0 else 4.0

        temp_dir = Path(tempfile.mkdtemp(prefix="aura_drama_cta_mp4_"))
        try:
            # 1. 마스터 스틸 이미지 렌더 (1080x1920 PNG)
            master_png = temp_dir / "master_drama_cta.png"
            self.render_cta_image(output_path=master_png)

            # 2. FFmpeg stillimage 루프 → 무손실 지향 인코딩
            #    -crf 16 + -preset slow : 정지화면은 slow 프리셋이 압도적으로 유리 (선명도 극대화)
            #    -tune stillimage       : 정지 이미지 최적화 (링잉/블록 노이즈 억제)
            cmd = [
                self.ffmpeg_exe, "-y",
                "-loop", "1",
                "-i", str(master_png),
                "-i", str(aud_p),
                "-vf", f"scale={self.WIDTH}:{self.HEIGHT},fps={self.FPS},format=yuv420p",
                "-c:v", "libx264",
                "-preset", self.PRESET,
                "-crf", str(self.CRF),
                "-tune", "stillimage",
                "-c:a", "aac",
                "-b:a", self.AUDIO_BITRATE,
                "-ar", str(self.AUDIO_RATE),
                "-ac", str(self.AUDIO_CHANNELS),
                "-t", f"{duration:.2f}",
                str(out_p),
            ]

            logger.info(
                f"🎬 [AuraDramaCTACard] CTA 클립 인코딩 착수 ({duration:.2f}s, "
                f"crf={self.CRF}, preset={self.PRESET})..."
            )
            self._run_cmd(cmd, "Aura 드라마 CTA 카드 클립 인코딩")

            if not out_p.exists() or out_p.stat().st_size <= 0:
                raise RuntimeError(f"❌ [AuraDramaCTACard] CTA 클립 미생성: {out_p}")

            logger.info(
                f"✅ [AuraDramaCTACard] CTA 클립 완성: {out_p.name} "
                f"({out_p.stat().st_size:,} bytes)"
            )
            return out_p

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    # ==========================================================================
    # 🧰 [유틸] FFmpeg 실행
    # ==========================================================================
    def _run_cmd(self, cmd: list, label: str) -> None:
        """FFmpeg 명령 실행 — 실패 시 stderr 를 포함한 RuntimeError 로 승격."""
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=300,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"❌ [AuraDramaCTACard] {label} 타임아웃 (300초 초과)") from exc
        except FileNotFoundError as exc:
            raise RuntimeError(
                f"❌ [AuraDramaCTACard] {label} 실패 — FFmpeg 바이너리 미발견: {self.ffmpeg_exe}"
            ) from exc

        if res.returncode != 0:
            stderr_tail = (res.stderr or "")[-800:]
            logger.error(f"❌ [AuraDramaCTACard] {label} 실패 (rc={res.returncode}): {stderr_tail}")
            raise RuntimeError(f"❌ [AuraDramaCTACard] {label} 실패: {stderr_tail[:400]}")

        logger.info(f"✅ [AuraDramaCTACard] {label} 완료")


# ==============================================================================
# 🧪 [테스트 블록] 단독 실행 검증 — 디자인/규격/클립 인코딩 자체 점검
# ==============================================================================
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    print("=" * 88)
    print("🏷️ [AuraDramaCTACard] 범용 럭셔리 엔딩 CTA 카드 자체 점검")
    print("=" * 88)

    card = AuraDramaCTACard()

    print("\n📐 [출력 규격]")
    print(f"  · 해상도 : {card.WIDTH}x{card.HEIGHT}")
    print(f"  · FPS    : {card.FPS}")
    print(f"  · CRF    : {card.CRF} / preset: {card.PRESET}")

    print("\n✍️ [카피 검수]")
    print(f"  · 캡슐 뱃지 : {card.CAPSULE_BADGE}")
    print(f"  · 디바이더  : {card.GOLD_DIVIDER_TEXT}")
    print(f"  · 헤드라인  : {card.HEADLINE_MAIN}")
    print(f"  · 서브      : {card.HEADLINE_SUB}")
    print(f"  · 혜택 3종  : {' | '.join(card.BENEFIT_ITEMS)}")
    print(f"  · CTA 메인  : {card.CTA_BUTTON_MAIN}")
    print(f"  · CTA 서브  : {card.CTA_BUTTON_SUB}")
    print(f"  · 가이드    : {card.GUIDE_TEXT}")
    print(f"  · 푸터      : Official Web: {card.OFFICIAL_WEB} | 네이버 검색: {card.NAVER_KEYWORD}")

    print("\n🎨 [HTML 템플릿 검증]")
    html = card.generate_html_template()
    print(f"  · 길이            : {len(html):,} chars")
    print(f"  · 1080x1920 명시  : {'1080px' in html and '1920px' in html}")
    print(f"  · 찬반투표 배제    : {'OPTION 1' not in html and '찬반' not in html}")
    print(f"  · 혜택박스 배제    : {'benefit-box' not in html}")

    print("\n🖼️ [Playwright 렌더 검증]")
    try:
        out_png = Path("_verify_drama_cta.png")
        img = card.render_cta_image(output_path=out_png)
        print(f"  · ✅ 렌더 성공 : {img.size[0]}x{img.size[1]} / mode={img.mode}")
        print(f"  · ✅ 파일 저장 : {out_png} ({out_png.stat().st_size:,} bytes)")
        out_png.unlink(missing_ok=True)
    except Exception as exc:  # noqa: BLE001 — 자체 점검은 실패를 삼키지 않고 출력
        print(f"  · ❌ 렌더 실패 : {exc}")

    print("\n" + "=" * 88)
    print("✅ [AuraDramaCTACard] 자체 점검 완료")
    print("=" * 88)
