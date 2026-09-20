# -*- coding: utf-8 -*-
"""
📈 StockMaster 전용 실사형 16:9 사진 생성기 (StockImageGenerator)
==================================================================
- 역할: 본문 주제와 100% 매칭되는 트레이딩룸/캔들차트/월스트리트/핀테크 16:9 감성 사진 1장 생성
- 가드레일:
  1. 유료키 우선 시도 (Imagen 3 고품질 실사)
  2. 무료키 2단 롤오버
  3. AI 생성 실패 시 고품질 주식/금융 Unsplash 실사 사진 즉시 폴백 (절대 중단 없음)
"""

import os
import sys
import time
import logging
import requests
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("StockImageGenerator")

CURRENT_DIR = Path(__file__).resolve().parent
IMAGES_DIR = CURRENT_DIR / "generated_images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# KeyManager import
try:
    from utils.key_manager import get_paid_gemini_key, get_gemini_key, report_gemini_key_failure
except ImportError:
    def get_paid_gemini_key():
        return os.environ.get("GEMINI_API_KEY", "")
    def get_gemini_key():
        return os.environ.get("GEMINI_API_KEY", "")
    def report_gemini_key_failure(k):
        pass


class StockImageGenerator:
    """StockMaster 주식 전용 16:9 실사 이미지 생성기"""

    FALLBACK_IMAGES = [
        "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&auto=format&fit=crop&q=80",  # 캔들차트와 트레이딩
        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1200&auto=format&fit=crop&q=80",  # 뉴욕 증권거래소 분위기
        "https://images.unsplash.com/photo-1642543492481-44e81e3914a7?w=1200&auto=format&fit=crop&q=80",  # 모던 핀테크 차트
        "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=1200&auto=format&fit=crop&q=80",  # 화폐와 글로벌 금융
        "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=1200&auto=format&fit=crop&q=80"   # 비즈니스 분석과 그래프
    ]

    CATEGORY_DEFAULT_PROMPTS = {
        "korea_market": "A modern Korean high-tech semiconductor plant cleanroom and glowing silicon wafer, futuristic technology atmosphere, cinematic 8k editorial photography, 16:9 aspect ratio",
        "us_dividend_tech": "A prestigious Wall Street skyscraper view at dusk, glowing financial ticker board, modern corporate headquarters, cinematic 8k editorial photography, 16:9 aspect ratio",
        "etf_index": "A high-end trading desk with three monitors showing green stock market charts, S&P 500 index graphs, sleek minimalist setup, 8k editorial photography, 16:9 aspect ratio",
        "macro_economy": "Federal Reserve building exterior in Washington D.C., majestic marble columns, dramatic sky with morning sunlight, financial authority atmosphere, 16:9 aspect ratio",
        "chart_financials": "Close-up of a tablet screen displaying vibrant green and red candlestick charts, financial ratios, elegant wooden desk, shallow depth of field, 16:9 aspect ratio",
        "quant_risk": "A calm sophisticated quantitative analyst studying financial data models on a curved ultrawide monitor, dark aesthetic fintech office, focused and disciplined, 16:9 aspect ratio"
    }

    def generate_article_photo(
        self,
        topic_id: int,
        category: str,
        topic_title: str,
        custom_visual_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """주제에 맞는 16:9 실사 사진 1장 생성 (실패 시 Unsplash 자동 폴백)"""
        prompt = custom_visual_prompt or self.CATEGORY_DEFAULT_PROMPTS.get(
            category,
            "A professional stock trading desk with candlestick charts on monitors, city skyline view, 16:9"
        )

        timestamp = int(time.time())
        local_filename = f"stock_{category}_{topic_id}_{timestamp}.jpg"
        local_path = IMAGES_DIR / local_filename

        # 1. Imagen 3 또는 Google GenAI 이미지 생성 시도
        generated = self._try_gemini_image(prompt, local_path)
        if generated:
            return {
                "image_path": str(local_path),
                "web_url": str(local_path),
                "is_fallback": False,
                "prompt_used": prompt
            }

        # 2. 무료 Pollinations AI 실사 생성 시도
        generated_poll = self._try_pollinations_image(prompt, local_path)
        if generated_poll:
            return {
                "image_path": str(local_path),
                "web_url": str(local_path),
                "is_fallback": False,
                "prompt_used": prompt
            }

        # 3. 비상용 Unsplash 고화질 실사 폴백
        import random
        fallback_url = random.choice(self.FALLBACK_IMAGES)
        logger.info(f"📸 [StockImageGen] 비상용 Unsplash 폴백 사용: {fallback_url}")
        return {
            "image_path": "",
            "web_url": fallback_url,
            "is_fallback": True,
            "prompt_used": prompt
        }

    def _try_gemini_image(self, prompt: str, save_path: Path) -> bool:
        """Google Imagen 3 API를 통한 고품질 실사 이미지 생성"""
        try:
            from google import genai
            from google.genai import types
            api_key = get_paid_gemini_key() or get_gemini_key()
            if not api_key:
                return False

            client = genai.Client(api_key=api_key)
            result = client.models.generate_images(
                model='imagen-3.0-generate-002',
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="16:9",
                    person_generation="ALLOW_ADULT",
                    safety_filter_level="BLOCK_MEDIUM_AND_ABOVE"
                )
            )
            for generated_image in result.generated_images:
                with open(save_path, "wb") as f:
                    f.write(generated_image.image.image_bytes)
                logger.info(f"✅ [StockImageGen] Imagen 3 생성 성공: {save_path.name}")
                return True
        except Exception as e:
            logger.debug(f"Imagen 3 시도 실패 ({e})")
        return False

    def _try_pollinations_image(self, prompt: str, save_path: Path) -> bool:
        """무료 Pollinations AI 실사 이미지 생성"""
        try:
            import urllib.parse
            clean_prompt = f"{prompt}, photorealistic, 8k, professional fintech photography, dramatic lighting, no text"
            encoded = urllib.parse.quote(clean_prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=1280&height=720&model=flux&nologo=true"
            resp = requests.get(url, timeout=20)
            if resp.status_code == 200 and len(resp.content) > 10000:
                with open(save_path, "wb") as f:
                    f.write(resp.content)
                logger.info(f"✅ [StockImageGen] Pollinations 생성 성공: {save_path.name}")
                return True
        except Exception as e:
            logger.debug(f"Pollinations 시도 실패 ({e})")
        return False
