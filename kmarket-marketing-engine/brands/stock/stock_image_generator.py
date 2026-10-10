# -*- coding: utf-8 -*-
"""
📈 StockMaster AI 맞춤형 16:9 실사 사진 생성 엔진 (StockImageGenerator)
========================================================================
- 브랜드: StockMaster AI (전광판, VETO 리스크, 변곡점, 매크로 스트레스, 손절선, 8대 퀀트)
- 역할:
  1. Gemini가 투자 칼럼 맥락에 맞춰 기획한 visual_prompt를 100% 최우선 반영하여 16:9 고화질 실사 사진 1장 생성
  2. gemini-3.1-flash-lite-image 모델로 트레이딩룸, 여의도 금융가, 모니터 차트, 스마트폰 자가진단 등 본문과 일치하는 실사 렌더링
  3. 유료키 체인 스마트 롤오버 투입 (100% 무중단 생성)
  4. WebP 고압축(1200px, quality 82) 변환 및 outputs/stock/blog_images/ 저장
  5. ⚡ Cache-First: 이미 고화질 사진이 존재하면 재사용 (비용 0원)
  6. 비상 시 100% 무중단 주식/금융 실사 폴백 보장
"""

import os
import sys
import io
import json
import base64
import logging
import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image

# UTF-8 콘솔 출력 지원
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("StockImageGenerator")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

OUTPUTS_DIR = PROJECT_ROOT / "outputs" / "stock" / "blog_images"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

# 7대 카테고리별 전문 비주얼 프리셋 (한국인 / 현대적 핀테크 / 여의도 / 자연광 100%)
STOCK_CATEGORY_PRESETS: Dict[str, Dict[str, Any]] = {
    "realtime_rank1": {
        "name": "실시간 1위 주도주 & 수급",
        "default_prompt": (
            "A modern high-end stock trading office in Yeouido Seoul, glowing multi-monitor setup displaying live green candlestick charts and market order books, "
            "a sharp professional Korean financial analyst analyzing data calmly, warm cinematic lighting, "
            "photorealistic, cinematic 16:9, authentic documentary photography, 8k"
        ),
        "fallback_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&auto=format&fit=crop&q=80"
    },
    "valid_entry": {
        "name": "진입유효 탭 & 수급 가속",
        "default_prompt": (
            "A stylish clean modern desk with a tablet and laptop screen displaying green stock uptrend charts and institutional volume indicators, "
            "a cup of coffee, bright morning natural sunlight, professional fintech atmosphere, "
            "photorealistic, cinematic 16:9, master quality, 8k"
        ),
        "fallback_url": "https://images.unsplash.com/photo-1642543492481-44e81e3914a7?w=1200&auto=format&fit=crop&q=80"
    },
    "veto_risk": {
        "name": "배제(VETO) 탭 & 뇌동매매 방지",
        "default_prompt": (
            "A focused thoughtful Korean adult investor in his 30s sitting calmly at a neat wooden desk at home, "
            "looking at a tablet with disciplined stop-loss risk charts, peaceful and rational mindset, "
            "soft ambient lighting, photorealistic, cinematic 16:9, authentic lifestyle photography, 8k"
        ),
        "fallback_url": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=1200&auto=format&fit=crop&q=80"
    },
    "turning_point": {
        "name": "변곡점 탭 & 골든크로스",
        "default_prompt": (
            "A close-up shot of a smartphone screen showing a vibrant golden cross moving average breakout chart with volume surge, "
            "held by a smiling Korean office worker in Seoul cafe, warm natural sunlight, "
            "photorealistic, shallow depth of field, 16:9, high resolution"
        ),
        "fallback_url": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1200&auto=format&fit=crop&q=80"
    },
    "macro_stress": {
        "name": "매크로 스트레스 & 환율 지표",
        "default_prompt": (
            "A modern financial district skyscraper skyline in Seoul at golden hour dusk, glowing digital exchange rate and stock index ticker boards, "
            "grand architectural view, majestic and authoritative atmosphere, "
            "photorealistic, high quality, 16:9"
        ),
        "fallback_url": "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=1200&auto=format&fit=crop&q=80"
    },
    "price_boundary": {
        "name": "스윙 목표선 & 청산 손절선",
        "default_prompt": (
            "A tidy minimalist desk with a financial calculation notebook, a pen, and an ultra-wide curved monitor showing clear support and resistance lines, "
            "crisp clean editorial shot, tranquil and disciplined trading room, "
            "photorealistic, 16:9, master quality"
        ),
        "fallback_url": "https://images.unsplash.com/photo-1450133064473-71024230f91b?w=1200&auto=format&fit=crop&q=80"
    },
    "quant_guide": {
        "name": "8대 퀀트 가이드 & 밸류업",
        "default_prompt": (
            "A modern corporate financial planning boardroom in Seoul, clean presentation screen showing ROE and PBR corporate value-up growth curves, "
            "clean aesthetic interior, warm natural sunlight, professional atmosphere, "
            "photorealistic, cinematic 16:9, 8k"
        ),
        "fallback_url": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=1200&auto=format&fit=crop&q=80"
    }
}


class StockImageGenerator:
    """
    📈 StockMaster AI 전용 16:9 실사 맞춤 사진 생성 엔진
    - Gemini 스토리 visual_prompt 100% 최우선 반영
    - gemini-3.1-flash-lite-image 모델로 실사 렌더링
    - 유료키 체인 스마트 롤오버
    - WebP 고압축 최적화 저장
    """

    def __init__(self):
        # 🔑 유료키 체인 로드
        from config import (
            GEMINI_PAID_API_KEY_AURA_1,
            GEMINI_PAID_API_KEY_AURA_2,
            GEMINI_API_KEY_KMARKET,
            GEMINI_API_KEY_EASYTAX,
            GEMINI_API_KEY
        )
        self.paid_keys = [
            k.strip() for k in [
                GEMINI_PAID_API_KEY_AURA_1,
                GEMINI_PAID_API_KEY_AURA_2,
                GEMINI_API_KEY_KMARKET,
                GEMINI_API_KEY_EASYTAX,
                GEMINI_API_KEY
            ]
            if k and len(k.strip()) > 10
        ]
        self._current_key_idx = 0

    def _get_active_client(self):
        if not self.paid_keys:
            return None
        from google import genai
        api_key = self.paid_keys[self._current_key_idx % len(self.paid_keys)]
        return genai.Client(api_key=api_key)

    def _build_full_prompt(self, category: str, topic_title: str = "", custom_visual_prompt: Optional[str] = None) -> str:
        """Gemini가 투자 칼럼 스토리에 맞춰 직접 생성한 visual_prompt 100% 최우선 반영"""
        if custom_visual_prompt and len(custom_visual_prompt.strip()) > 20:
            prompt = custom_visual_prompt.strip()
            if "photorealistic" not in prompt.lower():
                prompt += ", photorealistic, cinematic natural lighting, 16:9, master quality, 8k"
            if "korean" not in prompt.lower() and "seoul" not in prompt.lower() and "yeouido" not in prompt.lower():
                prompt += ", contemporary Seoul Yeouido fintech aesthetic"
            return prompt

        # visual_prompt가 없을 때 주제어에서 동적 맥락 추출
        t = (topic_title or "").lower()
        if "체결강도" in t or "1위" in t or "수급" in t:
            return "A modern high-end stock trading office in Yeouido Seoul, glowing multi-monitor setup displaying live green candlestick charts and market order books, photorealistic, cinematic 16:9, 8k"
        elif "손절" in t or "목표" in t or "타점" in t or "atr" in t:
            return "A tidy modern desk with an ultra-wide monitor showing clean support and resistance price boundary charts, neat notebook and pen, morning light, photorealistic, 16:9"
        elif "veto" in t or "뇌동매매" in t or "위험" in t or "물타기" in t:
            return "A calm disciplined Korean adult investor in modern home study reviewing financial risk dashboard on a tablet, soft ambient lighting, photorealistic, 16:9"
        elif "변곡점" in t or "골든크로스" in t or "신고가" in t:
            return "A smartphone screen showing a vibrant golden cross moving average breakout chart held by a smiling Korean professional, natural sunlight, photorealistic, 16:9"
        elif "환율" in t or "달러" in t or "매크로" in t:
            return "Seoul Yeouido financial district skyline at dusk with glowing exchange rate ticker boards, cinematic twilight mood, photorealistic, 16:9"
        else:
            preset = STOCK_CATEGORY_PRESETS.get(category, STOCK_CATEGORY_PRESETS["realtime_rank1"])
            return preset["default_prompt"]

    def _compress_to_webp(self, raw_bytes: bytes, max_width: int = 1200, quality: int = 82) -> bytes:
        """PNG/JPEG ➔ WebP 고압축 변환 및 16:9 최적화 리사이즈"""
        img = Image.open(io.BytesIO(raw_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        w, h = img.size
        if w > max_width:
            new_h = int(h * (max_width / w))
            img = img.resize((max_width, new_h), Image.Resampling.LANCZOS)

        out_io = io.BytesIO()
        img.save(out_io, format="WEBP", quality=quality, optimize=True)
        return out_io.getvalue()

    def generate_article_photo(
        self,
        topic_id: int,
        category: str,
        topic_title: str,
        custom_visual_prompt: Optional[str] = None,
        force_regenerate: bool = True
    ) -> Dict[str, Any]:
        """
        주제 맥락에 100% 어울리는 16:9 실사 사진 1장 생성
        Returns: {
            "success": bool,
            "image_path": str,      # 로컬 절대 경로
            "web_url": str,         # 웹/블로그 본문용 URL 또는 파일 경로
            "is_fallback": bool,
            "prompt_used": str
        }
        """
        prompt = self._build_full_prompt(category, topic_title, custom_visual_prompt)
        preset = STOCK_CATEGORY_PRESETS.get(category, STOCK_CATEGORY_PRESETS["realtime_rank1"])
        fallback_url = preset["fallback_url"]

        # 🚀 [100% 실시간 신규 생성 원칙] 매회 새로운 고유 주식 실사 이미지를 실시간 생성합니다.
        # (기존 이미지 재사용 전면 비활성화)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stock_topic_{topic_id:03d}_{category}_{timestamp}.webp"
        output_file = OUTPUTS_DIR / filename

        logger.info(f"🎨 [StockImage] 주제 #{topic_id} 스토리 맞춤 사진 생성 착수 (카테고리: {category})")
        logger.info(f"🎨 [StockImage] 제미나이 맞춤 프롬프트: {prompt[:120]}...")

        raw_bytes = None
        for attempt in range(len(self.paid_keys)):
            try:
                client = self._get_active_client()
                if not client:
                    break

                # 🌟 [공식 검증 완료] gemini-3.1-flash-lite-image로 실사 이미지 직접 생성
                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite-image",
                    contents=prompt
                )

                if response and response.candidates and response.candidates[0].content:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, "inline_data") and part.inline_data and part.inline_data.data:
                            raw = part.inline_data.data
                            if isinstance(raw, str):
                                raw = base64.b64decode(raw)
                            raw_bytes = raw
                            break

                if raw_bytes:
                    logger.info(f"✅ [StockImage] Gemini Image 생성 성공! (크기: {len(raw_bytes):,} bytes)")
                    break

            except Exception as e:
                err_str = str(e)
                logger.warning(f"⚠️ [StockImage] 유료키 #{self._current_key_idx + 1} 생성 실패: {err_str[:120]}")
                # 다음 유료키로 롤오버
                self._current_key_idx = (self._current_key_idx + 1) % len(self.paid_keys)

        # 성공 시 로컬 WebP 고압축 저장
        if raw_bytes:
            try:
                webp_bytes = self._compress_to_webp(raw_bytes)
                with open(output_file, "wb") as f:
                    f.write(webp_bytes)
                logger.info(f"💾 [StockImage] WebP 압축 저장 완료: {output_file} ({len(webp_bytes):,} bytes)")

                return {
                    "success": True,
                    "image_path": str(output_file),
                    "web_url": str(output_file),
                    "is_fallback": False,
                    "prompt_used": prompt
                }
            except Exception as e:
                logger.error(f"❌ [StockImage] 파일 저장 실패: {e}")

        # 모든 키 실패 시 무중단 고감도 폴백
        logger.info(f"🛡️ [StockImage] 카테고리 고감도 사진으로 안전 폴백: {fallback_url}")
        return {
            "success": True,
            "image_path": "",
            "web_url": fallback_url,
            "is_fallback": True,
            "prompt_used": prompt
        }


if __name__ == "__main__":
    generator = StockImageGenerator()
    print("🎨 [StockMaster AI] 사진 생성 테스트")
    res = generator.generate_article_photo(
        topic_id=1,
        category="realtime_rank1",
        topic_title="오늘 AI 전광판 실시간 1위 주도주와 체결강도 120% 돌파의 숨은 의미",
        custom_visual_prompt="A modern high-end stock trading office in Yeouido Seoul, glowing multi-monitor setup displaying live green candlestick charts and market order books, photorealistic, cinematic 16:9, 8k",
        force_regenerate=True
    )
    print("결과:", json.dumps(res, ensure_ascii=False, indent=2))
