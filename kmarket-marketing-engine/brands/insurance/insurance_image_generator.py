# -*- coding: utf-8 -*-
"""
🛡️ InsureBalance 전용 실사형 16:9 사진 생성기 (InsuranceImageGenerator)
======================================================================
- 역할: 본문 주제와 100% 매칭되는 금융/보험/가족/라이프스타일 16:9 감성 사진 1장 생성
- 가드레일:
  1. ⚡ Cache-First: 이미 생성된 사진이 존재하면 Imagen 3 API 호출 없이 즉시 재사용 (비용 0원)
  2. 유료키 우선 시도 (Imagen 3 고품질 실사)
  3. 무료 Pollinations AI 롤오버
  4. AI 생성 실패 시 고품질 금융/보험 Unsplash 실사 사진 즉시 폴백 (절대 중단 없음)
"""

import os
import sys
import time
import logging
import requests
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("InsuranceImageGenerator")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
IMAGES_DIR = PROJECT_ROOT / "outputs" / "insurance" / "blog_images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

# KeyManager import
try:
    from utils.key_manager import get_paid_gemini_key, get_gemini_key, report_gemini_key_failure
except ImportError:
    def get_paid_gemini_key():
        return os.environ.get("GEMINI_PAID_API_KEY_AURA_1") or os.environ.get("GEMINI_API_KEY") or ""
    def get_gemini_key():
        return os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_FREE_API_KEY_AURA_1") or os.environ.get("GEMINI_FREE_API_KEY_KMARKET") or ""
    def report_gemini_key_failure(k):
        pass


class InsuranceImageGenerator:
    """InsureBalance 보험 전용 16:9 실사 이미지 생성기 (Cache-First)"""

    FALLBACK_IMAGES = [
        "https://images.unsplash.com/photo-1450133064473-71024230f91b?w=1200&auto=format&fit=crop&q=80",  # 서류와 만년필
        "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=1200&auto=format&fit=crop&q=80",  # 계산기와 재무 계획
        "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=1200&auto=format&fit=crop&q=80",  # 병원 및 의료 상담
        "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=1200&auto=format&fit=crop&q=80",  # 부동산과 가족
        "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=1200&auto=format&fit=crop&q=80"   # 태블릿과 디지털 금융
    ]

    CATEGORY_DEFAULT_PROMPTS = {
        "health_medical": "A modern clean hospital consultation room, a doctor explaining medical charts to a patient, warm natural lighting, professional and calm, 8k editorial photography, 16:9 aspect ratio",
        "auto_driver": "A clean modern car interior with safety features, dashboard view on a scenic highway, golden hour sunlight, realistic automotive photography, 16:9 aspect ratio",
        "life_dental_pet": "A happy young family playing with their cute golden retriever in a sunlit living room, warm and cozy lifestyle photography, 16:9 aspect ratio",
        "savings_annuity": "A cozy home office with a neat wooden desk, a cup of coffee, a notebook with financial plans, warm morning sunlight, peaceful retirement mood, 16:9 aspect ratio",
        "claims_knowhow": "A neat workspace with organized insurance claim documents, a digital tablet with clear checklists, glasses and pen, crisp clean professional look, 16:9 aspect ratio",
        "remodeling_savings": "A smiling young Korean couple reviewing household financial budget on a laptop, bright modern living room, relieved and happy expression, 16:9 aspect ratio"
    }

    def generate_article_photo(
        self,
        topic_id: int,
        category: str,
        topic_title: str,
        custom_visual_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """주제에 맞는 16:9 실사 사진 1장 생성 (Cache-First: 기존 파일 우선 재사용)"""
        # 고정된 캐시 파일명 규칙
        local_filename = f"insurance_topic_{topic_id:03d}.webp"
        local_path = IMAGES_DIR / local_filename

        # ⚡ 1. Cache-First: 이미 생성된 사진이 존재하면 API 호출 없이 즉시 재사용
        if local_path.exists() and local_path.stat().st_size > 1000:
            logger.info(f"⚡ [InsuranceImageGen] 로컬 이미지 캐시 즉시 재사용: {local_filename} (비용 0원)")
            return {
                "image_path": str(local_path),
                "web_url": str(local_path),
                "is_fallback": False,
                "prompt_used": "cached"
            }

        # jpg 확장자 캐시 확인 (기존 생성분 호환)
        alt_jpg = IMAGES_DIR / f"insurance_topic_{topic_id:03d}.jpg"
        if alt_jpg.exists() and alt_jpg.stat().st_size > 1000:
            logger.info(f"⚡ [InsuranceImageGen] 로컬 이미지(JPG) 캐시 즉시 재사용: {alt_jpg.name} (비용 0원)")
            return {
                "image_path": str(alt_jpg),
                "web_url": str(alt_jpg),
                "is_fallback": False,
                "prompt_used": "cached"
            }

        prompt = custom_visual_prompt or self.CATEGORY_DEFAULT_PROMPTS.get(
            category,
            "A professional financial planner desk with neat insurance documents and tablet, warm light, 16:9"
        )

        # 2. Imagen 3 생성 시도 (1회만)
        generated = self._try_gemini_image(prompt, local_path)
        if generated:
            return {
                "image_path": str(local_path),
                "web_url": str(local_path),
                "is_fallback": False,
                "prompt_used": prompt
            }

        # 3. 무료 Pollinations AI 실사 생성 시도
        generated_poll = self._try_pollinations_image(prompt, local_path)
        if generated_poll:
            return {
                "image_path": str(local_path),
                "web_url": str(local_path),
                "is_fallback": False,
                "prompt_used": prompt
            }

        # 4. 비상용 Unsplash 고화질 실사 폴백 및 로컬 디스크 다운로드 보장
        import random
        fallback_url = random.choice(self.FALLBACK_IMAGES)
        logger.info(f"📸 [InsuranceImageGen] 고화질 실사 사진 다운로드 저장: {fallback_url}")
        try:
            resp = requests.get(fallback_url, timeout=15)
            if resp.status_code == 200 and len(resp.content) > 1000:
                with open(local_path, "wb") as f:
                    f.write(resp.content)
                return {
                    "image_path": str(local_path),
                    "web_url": str(local_path),
                    "is_fallback": True,
                    "prompt_used": prompt
                }
        except Exception as e:
            logger.warning(f"폴백 이미지 다운로드 실패: {e}")

        return {
            "image_path": str(local_path) if local_path.exists() else "",
            "web_url": fallback_url,
            "is_fallback": True,
            "prompt_used": prompt
        }

    def _try_gemini_image(self, prompt: str, save_path: Path) -> bool:
        """Google Gemini 공식 이미지 모델(gemini-2.5-flash-image)을 통한 고품질 실사 이미지 직접 생성"""
        try:
            from google import genai
            from google.genai import types
            api_key = get_paid_gemini_key() or get_gemini_key()
            if not api_key:
                return False

            client = genai.Client(api_key=api_key)
            # 16:9 비율 실사 프롬프트
            full_prompt = f"{prompt}, realistic 16:9 photography, clean natural sunlight, 8k professional editorial shot"

            for m_name in ["gemini-2.5-flash-image", "gemini-3.1-flash-image", "gemini-3-pro-image"]:
                try:
                    response = client.models.generate_content(
                        model=m_name,
                        contents=full_prompt
                    )
                    if response and response.candidates:
                        for part in response.candidates[0].content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                with open(save_path, "wb") as f:
                                    f.write(part.inline_data.data)
                                logger.info(f"✅ [InsuranceImageGen] Gemini AI 이미지 직접 생성 성공 ({m_name}): {save_path.name}")
                                return True
                except Exception as inner_e:
                    logger.debug(f"모델 {m_name} 시도 통과: {inner_e}")
                    continue
        except Exception as e:
            logger.warning(f"⚠️ [InsuranceImageGen] Gemini 이미지 생성 실패: {e}")
        return False

    def _try_pollinations_image(self, prompt: str, save_path: Path) -> bool:
        """무료 Pollinations AI 실사 이미지 생성"""
        try:
            import urllib.parse
            clean_prompt = f"{prompt}, photorealistic, 8k, professional photography, natural lighting, no text"
            encoded = urllib.parse.quote(clean_prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=1280&height=720&model=flux&nologo=true"
            resp = requests.get(url, timeout=20)
            if resp.status_code == 200 and len(resp.content) > 10000:
                with open(save_path, "wb") as f:
                    f.write(resp.content)
                logger.info(f"✅ [InsuranceImageGen] Pollinations 생성 성공: {save_path.name}")
                return True
        except Exception as e:
            logger.debug(f"Pollinations 시도 실패 ({e})")
        return False
