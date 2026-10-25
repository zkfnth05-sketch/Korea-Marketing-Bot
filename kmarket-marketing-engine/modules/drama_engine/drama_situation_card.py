# -*- coding: utf-8 -*-
"""
modules/drama_engine/drama_situation_card.py
===================================================================================================
[DramaSituationCard] - 5컷 숏드라마 cut0 상황 자막 카드 렌더러
---------------------------------------------------------------------------------------------------
시청자가 3초 안에 상황을 파악할 수 있도록 본편 cut1 앞에 삽입되는
상황 설명 카드 이미지(PNG)와 무음 오디오(MP3)를 생성한다.

[카드 디자인]
  - 1080x1920 세로 풀HD
  - 배경: 딥 다크 그라데이션 (드라마틱 무드)
  - 상단: 위치 뱃지 (로케이션)
  - 중앙: 상황 텍스트 (큰 폰트)
  - 하단: "▼ 지금 무슨 일이 생겼냐면..." 유도 문구

[cut0 음성]
  - 목소리 없음 (BGM 온리) -> 무음 MP3 를 생성하여 stitcher 에 전달
===================================================================================================
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger("DramaSituationCard")

CARD_WIDTH: int = 1080
CARD_HEIGHT: int = 1920
CUT0_DURATION_SEC: float = 2.5

BG_TOP_COLOR: Tuple[int, int, int] = (10, 10, 20)
BG_BOTTOM_COLOR: Tuple[int, int, int] = (25, 20, 45)
TEXT_WHITE = (255, 255, 255, 255)
TEXT_SKY   = (180, 220, 255, 220)
TEXT_DIM   = (160, 160, 180, 200)

FONT_PATHS = [
    Path("C:/Windows/Fonts/malgunbd.ttf"),
    Path("C:/Windows/Fonts/malgun.ttf"),
    Path("C:/Windows/Fonts/NanumGothicBold.ttf"),
]


def _get_font(size: int):
    try:
        from PIL import ImageFont
        for fp in FONT_PATHS:
            if fp.exists():
                try:
                    return ImageFont.truetype(str(fp), size)
                except Exception:
                    continue
        return ImageFont.load_default()
    except ImportError:
        return None


def _draw_centered(draw, text: str, y: int, w: int, font, color) -> None:
    try:
        bbox = font.getbbox(text)
        x = (w - (bbox[2] - bbox[0])) // 2
    except Exception:
        x = w // 4
    draw.text((x, y), text, font=font, fill=color)


def _draw_multiline(draw, text: str, y0: int, w: int, font, color,
                    line_spacing: int = 80, max_chars: int = 18) -> None:
    lines = text.split("\n") if "\n" in text else [
        text[i:i+max_chars] for i in range(0, len(text), max_chars)
    ]
    for ln in lines:
        _draw_centered(draw, ln.strip(), y0, w, font, color)
        y0 += line_spacing


def render_situation_card(
    situation_text: str,
    location_text: str,
    output_path: Path,
    duration_sec: float = CUT0_DURATION_SEC,
    time_hint: Optional[str] = None,
) -> Path:
    """cut0 상황 자막 카드 1080x1920 PNG 생성."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        from PIL import Image, ImageDraw
    except ImportError:
        logger.error("[SituationCard] Pillow 없음 - 검정 카드 폴백")
        _make_black_png(output_path)
        return output_path

    img = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), BG_TOP_COLOR + (255,))
    draw = ImageDraw.Draw(img)

    # 그라데이션 배경
    for y in range(CARD_HEIGHT):
        t = y / CARD_HEIGHT
        r = int(BG_TOP_COLOR[0] + (BG_BOTTOM_COLOR[0] - BG_TOP_COLOR[0]) * t)
        g = int(BG_TOP_COLOR[1] + (BG_BOTTOM_COLOR[1] - BG_TOP_COLOR[1]) * t)
        b = int(BG_TOP_COLOR[2] + (BG_BOTTOM_COLOR[2] - BG_TOP_COLOR[2]) * t)
        draw.line([(0, y), (CARD_WIDTH, y)], fill=(r, g, b, 255))

    # 글로우
    cx, cy = CARD_WIDTH // 2, CARD_HEIGHT // 2
    for rad in range(320, 0, -28):
        a = int(18 * (1 - rad / 320))
        draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=(80, 60, 140, a))

    # 위치 뱃지
    loc_font = _get_font(44)
    loc_y = int(CARD_HEIGHT * 0.32)
    if location_text and loc_font:
        _draw_centered(draw, f"[ {location_text[:22]} ]", loc_y, CARD_WIDTH, loc_font, TEXT_SKY)

    # 구분선
    line_y = loc_y + 68
    draw.line([(cx - 130, line_y), (cx + 130, line_y)], fill=(100, 100, 160, 180), width=2)

    # 상황 텍스트
    sit_font = _get_font(60)
    sit_y = int(CARD_HEIGHT * 0.40)
    if sit_font:
        _draw_multiline(draw, situation_text, sit_y, CARD_WIDTH, sit_font, TEXT_WHITE,
                        line_spacing=82, max_chars=17)

    # 시간 힌트
    if time_hint:
        hint_font = _get_font(38)
        if hint_font:
            _draw_centered(draw, f"[ {time_hint} ]", int(CARD_HEIGHT * 0.72),
                           CARD_WIDTH, hint_font, TEXT_DIM)

    # 하단 유도
    arrow_font = _get_font(36)
    if arrow_font:
        _draw_centered(draw, "▼  지금 무슨 일이 생겼냐면...", int(CARD_HEIGHT * 0.87),
                       CARD_WIDTH, arrow_font, TEXT_DIM)

    img.convert("RGB").save(str(output_path), "PNG")
    logger.info("[SituationCard] cut0 카드 생성: %s", output_path.name)
    return output_path


def _make_black_png(output_path: Path) -> None:
    """Pillow 없을 때 작은 검정 PNG 생성."""
    import struct, zlib
    def chunk(t, d):
        c = t + d
        return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    idat = zlib.compress(b"\x00\x00\x00\x00")
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")
    output_path.write_bytes(png)


def make_silent_audio(
    output_path: Path,
    duration_sec: float,
    ffmpeg_exe: str = "ffmpeg",
) -> Path:
    """지정 길이의 무음 MP3 생성 (cut0 전용 오디오)."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg_exe, "-y",
        "-f", "lavfi",
        "-i", "anullsrc=r=48000:cl=stereo",
        "-t", str(duration_sec),
        "-c:a", "libmp3lame", "-b:a", "128k",
        str(output_path),
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True,
                             encoding="utf-8", errors="replace", check=False)
        if res.returncode != 0 or not output_path.exists():
            logger.error("[SituationCard] 무음 MP3 실패: %s", (res.stderr or "")[:300])
            output_path.write_bytes(b"")
        else:
            logger.info("[SituationCard] 무음 오디오 생성: %.1fs -> %s", duration_sec, output_path.name)
    except Exception as exc:
        logger.error("[SituationCard] ffmpeg 오류: %s", exc)
        output_path.write_bytes(b"")
    return output_path


def build_situation_text(scenario: dict) -> str:
    """
    시나리오 payload 에서 cut0 상황 텍스트를 자동 추출한다.

    우선순위:
      1. scenario["situation_text"] (디렉터 직접 집필)
      2. genre_name + hook 대사 앞부분 조합
      3. theme 그대로
      4. 기본 문구
    """
    if scenario.get("situation_text"):
        return str(scenario["situation_text"])

    hook = str(scenario.get("speech_hook") or "").strip()
    genre = str(scenario.get("genre_name") or "").strip()
    if hook and genre:
        hook_short = hook[:22]
        return f"[{genre}]\n\"{hook_short}...\""

    theme = str(scenario.get("theme") or "").strip()
    if theme:
        return theme[:40]

    return "지금 이 순간,\n무슨 일이 생겼냐면..."
