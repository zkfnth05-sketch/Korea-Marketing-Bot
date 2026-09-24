# -*- coding: utf-8 -*-
"""
Aura Image Generator (💖 Aura 2030 매거진 전용 맞춤 사진 생성 독립 레고 블록)
========================================================================
- 브랜드: Aura (2030 데이팅 / 성수·연남 핫플 / 카톡 심리 / 매칭 라운지)
- 역할:
  1. Gemini가 글 스토리 맥락에 맞춰 기획한 visual_prompt를 받아 16:9 고화질 감성 사진 1장 생성
  2. 4대 키 체인 중 유료키 2개(GEMINI_API_KEY_KMARKET, GEMINI_API_KEY_EASYTAX) 스마트 롤오버 투입 (장당 약 5원 내외)
  3. 6대 카테고리별 2030 감성 비주얼 가드레일 (한국/서울 감성, 과도한 인공미 배제, 16:9)
  4. WebP 고압축 변환 및 로컬 outputs/aura/blog_images/ 저장 + Supabase Storage 연동
  5. API 일시 장애 시 100% 무중단 카테고리별 고감도 실사 폴백 보장
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

logger = logging.getLogger("AuraImageGenerator")

# 기본 경로 설정
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs" / "aura" / "blog_images"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# 6대 카테고리별 2030 감성 비주얼 프롬프트 프리셋 (한국인/서울 핫플/자연광 100%)
AURA_CATEGORY_PRESETS: Dict[str, Dict[str, Any]] = {
    "kakaotalk_signals": {
        "name": "카톡 밀당 & 시그널",
        "default_prompt": (
            "A cozy aesthetic Seoul cafe interior, warm natural sunlight through glass window, "
            "a stylish Korean young adult in their 20s looking gently at a smartphone screen on a wooden table, "
            "soft blurred cafe background, minimalist coffee cup and notebook nearby, "
            "authentic candid snapshot, photorealistic, cinematic 16:9, warm mood, 8k"
        ),
        "fallback_url": "https://images.unsplash.com/photo-1517256064527-09c73fc73e38?w=1200&auto=format&fit=crop&q=80"
    },
    "date_spots": {
        "name": "실전 소개팅 핫플",
        "default_prompt": (
            "Romantic intimate Seongsu-dong wine bar in Seoul, warm dim candle light on dark wood table, "
            "two glasses of red wine and elegant tapas dish, cozy atmosphere for a private date, "
            "stylish Seoul evening mood, photorealistic, cinematic lighting, 16:9, bokeh background, 8k"
        ),
        "fallback_url": "https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=1200&auto=format&fit=crop&q=80"
    },
    "conversation_skills": {
        "name": "대화 치트키 & 스몰토크",
        "default_prompt": (
            "Two attractive Korean young adults sitting opposite each other at an outdoor terrace cafe in Yeonnam-dong, "
            "engaged in a cheerful and genuine conversation, warm pleasant smiles, spring afternoon sunlight, "
            "candid lifestyle photography, photorealistic, shallow depth of field, 16:9, high resolution"
        ),
        "fallback_url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1200&auto=format&fit=crop&q=80"
    },
    "psychology_mbti": {
        "name": "연애 심리 & MBTI",
        "default_prompt": (
            "Aesthetic emotional flatlay on clean aesthetic desk, cup of hot latte, stylish leather diary with pen, "
            "soft warm morning sunlight casting gentle shadows, contemplative and cozy atmosphere, "
            "modern Seoul lifestyle, photorealistic, high quality, 16:9"
        ),
        "fallback_url": "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=1200&auto=format&fit=crop&q=80"
    },
    "lookbook_style": {
        "name": "소개팅 룩북 & 스타일",
        "default_prompt": (
            "Modern chic Seoul street style fashion look, clean minimalist neutral-toned casual date outfit, "
            "stylish young Korean in Seongsu street with architectural background, soft cinematic natural light, "
            "lookbook editorial photography, photorealistic, high-end fashion magazine feel, 16:9"
        ),
        "fallback_url": "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=1200&auto=format&fit=crop&q=80"
    },
    "after_dating": {
        "name": "애프터 & 고백",
        "default_prompt": (
            "A romantic evening stroll near Han River Seoul park, glowing city skyline night lights reflecting on water, "
            "cozy romantic twilight vibe, subtle cinematic street lamps, nostalgic and heart-fluttering mood, "
            "photorealistic, cinematic 16:9, master quality"
        ),
        "fallback_url": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=1200&auto=format&fit=crop&q=80"
    }
}


class AuraImageGenerator:
    """
    💖 Aura 2030 매거진 맞춤 사진 생성 독립 엔진
    - 유료키 2개 스마트 롤오버 (K-Market 유료키 ➔ EasyTax 유료키)
    - 16:9 WebP 고압축 최적화 저장
    """

    def __init__(self):
        # 🔑 Aura 전용 신규 유료키 2개 우선 로드 (이미지 전용)
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

    def _build_full_prompt(self, category: str, custom_visual_prompt: Optional[str] = None) -> str:
        """카테고리 가드레일 + Gemini 커스텀 비주얼 프롬프트 결합"""
        preset = AURA_CATEGORY_PRESETS.get(category, AURA_CATEGORY_PRESETS["kakaotalk_signals"])
        base_prompt = preset["default_prompt"]

        if custom_visual_prompt and custom_visual_prompt.strip():
            user_p = custom_visual_prompt.strip()
            # 필수 2030 감성 가드레일 추가
            if "photorealistic" not in user_p.lower():
                user_p += ", photorealistic, cinematic natural lighting, authentic mood, 16:9, 8k"
            if "seoul" not in user_p.lower() and "korean" not in user_p.lower():
                user_p += ", contemporary Seoul aesthetic"
            if "head" not in user_p.lower() and "upright" not in user_p.lower():
                user_p += ", upright head posture looking straight ahead with zero tilt"
            return user_p

        return base_prompt

    def _compress_to_webp(self, raw_bytes: bytes, max_width: int = 1200, quality: int = 82) -> bytes:
        """PNG 이미지 ➔ WebP 고압축 변환 및 16:9 리사이즈"""
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
        custom_visual_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        주제 맥락에 100% 어울리는 16:9 사진 1장 생성
        Returns: {
            "success": bool,
            "image_path": str,      # 로컬 절대 경로
            "web_url": str,         # 웹/블로그 본문용 URL 또는 상대 경로
            "is_fallback": bool,
            "prompt_used": str
        }
        """
        prompt = self._build_full_prompt(category, custom_visual_prompt)
        preset = AURA_CATEGORY_PRESETS.get(category, AURA_CATEGORY_PRESETS["kakaotalk_signals"])
        fallback_url = preset["fallback_url"]

        # ⚡ [비용 0원 원칙] 해당 주제에 대해 이미 생성된 이미지가 존재하면 재사용 (API 중복 호출 원천 차단)
        existing_images = sorted(list(OUTPUTS_DIR.glob(f"aura_topic_{topic_id:03d}_*.webp")), reverse=True)
        if existing_images and existing_images[0].stat().st_size > 1024:
            cached_file = existing_images[0]
            logger.info(f"⚡ [AuraImage] 주제 #{topic_id} 기존 고화질 이미지 캐시 즉시 재사용 (비용 0원!): {cached_file.name}")
            
            # Supabase Storage 영구 URL 획득 (필요 시 1회 업로드)
            final_web_url = fallback_url
            try:
                from brands.aura.aura_supabase_manager import AuraSupabaseManager
                sb_mgr = AuraSupabaseManager()
                uploaded_url = sb_mgr.upload_image_to_storage(str(cached_file), bucket_subpath="magazines")
                if uploaded_url:
                    final_web_url = uploaded_url
            except Exception as e:
                logger.debug(f"캐시 이미지 Storage 연동 확인: {e}")

            return {
                "success": True,
                "image_path": str(cached_file),
                "web_url": final_web_url,
                "is_fallback": (final_web_url == fallback_url),
                "prompt_used": "CACHED_REUSE"
            }

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aura_topic_{topic_id:03d}_{category}_{timestamp}.webp"
        output_file = OUTPUTS_DIR / filename

        logger.info(f"🎨 [AuraImage] 주제 #{topic_id} 신규 사진 1회 생성 착수 (카테고리: {category})")
        logger.info(f"🎨 [AuraImage] 프롬프트: {prompt[:90]}...")

        # 유료키 2개 순차 롤오버 시도
        raw_bytes = None
        for attempt in range(len(self.paid_keys)):
            try:
                client = self._get_active_client()
                if not client:
                    break

                from google.genai import types as genai_types
                # 1순위: 초저가 고품질 모델
                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite-image",
                    contents=prompt,
                    config=genai_types.GenerateContentConfig(
                        response_modalities=["IMAGE", "TEXT"]
                    )
                )

                if response and response.candidates and response.candidates[0].content:
                    for part in response.candidates[0].content.parts:
                        if part.inline_data and part.inline_data.data:
                            raw = part.inline_data.data
                            if isinstance(raw, str):
                                raw = base64.b64decode(raw)
                            raw_bytes = raw
                            break

                if raw_bytes:
                    logger.info(f"✅ [AuraImage] Gemini Image 생성 성공! (크기: {len(raw_bytes):,} bytes)")
                    break

            except Exception as e:
                err_str = str(e)
                logger.warning(f"⚠️ [AuraImage] 유료키 #{self._current_key_idx + 1} 생성 실패: {err_str[:120]}")
                # 다음 유료키로 롤오버
                self._current_key_idx = (self._current_key_idx + 1) % len(self.paid_keys)

        # 성공 시 로컬 WebP 저장 및 Supabase Storage 자동 업로드
        if raw_bytes:
            try:
                webp_bytes = self._compress_to_webp(raw_bytes)
                with open(output_file, "wb") as f:
                    f.write(webp_bytes)
                logger.info(f"💾 [AuraImage] WebP 압축 저장 완료: {output_file} ({len(webp_bytes):,} bytes)")

                # 🚀 Supabase Storage(aura-media/magazines)에 즉시 자동 업로드하여 공식 영구 URL 확보
                final_web_url = fallback_url
                try:
                    from brands.aura.aura_supabase_manager import AuraSupabaseManager
                    sb_mgr = AuraSupabaseManager()
                    uploaded_url = sb_mgr.upload_image_to_storage(str(output_file), bucket_subpath="magazines")
                    if uploaded_url:
                        final_web_url = uploaded_url
                        logger.info(f"🌐 [AuraImage] Supabase Storage 영구 퍼블릭 URL 바인딩 완료: {final_web_url}")
                except Exception as up_err:
                    logger.warning(f"⚠️ [AuraImage] Storage 업로드 예외 (폴백 URL 사용): {up_err}")

                return {
                    "success": True,
                    "image_path": str(output_file),
                    "web_url": final_web_url,
                    "is_fallback": (final_web_url == fallback_url),
                    "prompt_used": prompt
                }
            except Exception as e:
                logger.error(f"❌ [AuraImage] 파일 저장 실패: {e}")

        # 모든 키 실패 시 무중단 고감도 폴백
        logger.info(f"🛡️ [AuraImage] 카테고리 고감도 감성 사진으로 안전 폴백: {fallback_url}")
        return {
            "success": True,
            "image_path": "",
            "web_url": fallback_url,
            "is_fallback": True,
            "prompt_used": prompt
        }


if __name__ == "__main__":
    generator = AuraImageGenerator()
    print("🎨 [Aura] 6대 카테고리별 사진 생성 테스트")
    res = generator.generate_article_photo(
        topic_id=1,
        category="kakaotalk_signals",
        topic_title="소개팅 첫 카톡 읽씹 피하기",
        custom_visual_prompt="A young stylish Korean man smiling looking at his smartphone in a modern Yeonnam-dong cafe"
    )
    print("결과:", json.dumps(res, ensure_ascii=False, indent=2))
