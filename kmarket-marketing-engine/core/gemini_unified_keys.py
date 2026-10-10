# -*- coding: utf-8 -*-
"""
core/gemini_unified_keys.py - 🔑 [대한민국 마케팅 엔진 전 모듈 공통 Gemini 키 및 설정 관리자]
================================================================================
- 사용자 규격 100% 보장: [무료키 6개 + 유료키 2개 + 기본키 1개] = 총 9개 고유 키 통합 풀
- AFC(Automatic Function Calling) 노이즈 및 구글 HTTP 503 디버그 로그 원천 차단
- 3대 브랜드(Aura, Insurance, Stock) 및 모든 마케팅 채널 단일화
"""

import logging
from typing import List, Dict, Any

# 🛑 [구글 GenAI SDK 및 httpx 내부 노이즈 로그 원천 차단]
# 'AFC is enabled with max remote calls: 10' 및 'HTTP Request: 503' 콘솔 도배 방지
for _noisy in ('google_genai', 'google_genai.models', 'httpx', 'httpcore'):
    logging.getLogger(_noisy).setLevel(logging.ERROR)


def get_unified_gemini_key_dicts() -> List[Dict[str, str]]:
    """모든 6개 무료키 + 2개 유료키 + 기본키를 담은 딕셔너리 리스트 반환"""
    try:
        from config import (
            GEMINI_FREE_API_KEY_AURA_1,
            GEMINI_FREE_API_KEY_AURA_2,
            GEMINI_FREE_API_KEY_AURA_3,
            GEMINI_FREE_API_KEY_AURA_4,
            GEMINI_FREE_API_KEY_KMARKET,
            GEMINI_FREE_API_KEY_EASYTAX,
            GEMINI_PAID_API_KEY_AURA_1,
            GEMINI_PAID_API_KEY_AURA_2,
            GEMINI_API_KEY
        )
        candidates = [
            {"name": "AURA_FREE_1", "key": GEMINI_FREE_API_KEY_AURA_1},
            {"name": "AURA_FREE_2", "key": GEMINI_FREE_API_KEY_AURA_2},
            {"name": "AURA_FREE_3", "key": GEMINI_FREE_API_KEY_AURA_3},
            {"name": "AURA_FREE_4", "key": GEMINI_FREE_API_KEY_AURA_4},
            {"name": "KMARKET_FREE", "key": GEMINI_FREE_API_KEY_KMARKET},
            {"name": "EASYTAX_FREE", "key": GEMINI_FREE_API_KEY_EASYTAX},
            {"name": "AURA_PAID_1", "key": GEMINI_PAID_API_KEY_AURA_1},
            {"name": "AURA_PAID_2", "key": GEMINI_PAID_API_KEY_AURA_2},
            {"name": "DEFAULT", "key": GEMINI_API_KEY}
        ]
    except Exception:
        candidates = []

    seen = set()
    chain = []
    for c in candidates:
        k = (c.get("key") or "").strip()
        if k and k not in seen and len(k) > 10:
            seen.add(k)
            chain.append({"name": c.get("name", "KEY"), "key": k})
    return chain


def get_unified_gemini_keys() -> List[str]:
    """순수 API 키 문자열 리스트 반환 (중복 제거된 9개 고유 키)"""
    return [item["key"] for item in get_unified_gemini_key_dicts()]


def get_gemini_content_config(temperature: float = 0.7, json_mode: bool = False):
    """AFC 노이즈를 비활성화한 표준 GenerateContentConfig 반환"""
    from google.genai import types
    kwargs: Dict[str, Any] = {
        "temperature": temperature,
        "automatic_function_calling": types.AutomaticFunctionCallingConfig(disable=True)
    }
    if json_mode:
        kwargs["response_mime_type"] = "application/json"
    return types.GenerateContentConfig(**kwargs)


def format_gemini_error(e: Exception) -> str:
    """지저분한 구글 내부 JSON 대신 깔끔하고 명확한 사유 문자열 반환"""
    err_str = str(e)
    if '429' in err_str:
        return '일일 무료 쿼터(20회) 소진 (429)'
    elif '503' in err_str:
        return '구글 서버 일시 혼잡 (503)'
    elif '500' in err_str:
        return '구글 내부 서버 오류 (500)'
    return err_str[:80]
