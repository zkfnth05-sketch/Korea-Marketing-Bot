# -*- coding: utf-8 -*-
"""
[Aura 전용 독립 모듈] AuraTrafficFilters (brands/aura/aura_traffic_filters.py)
=============================================================================
• 역할: 대시보드 유입 통계에서 테스트/개발/자기참조 트래픽 제외 (실제 방문자만 집계)
"""

import re

# 개발·테스트·자기참조 referrer 패턴
NOISE_REFERRER_PATTERNS = (
    "localhost", "127.0.0.1", "0.0.0.0",
    "vercel.com",                 # Vercel 대시보드 미리보기
    "aura-ai-dating.vercel.app",  # 자기 도메인 내부 이동/새로고침
    "-vercel.app",                # 프리뷰 배포 도메인
)

# 개발자 테스트 계정/내부 경로 (테스트 전화번호 세션 등)
NOISE_PATH_PATTERNS = (
    re.compile(r"_user_8210\d+"),
    re.compile(r"_user_82101234"),
)


def is_noise_traffic(referrer: str, path: str) -> bool:
    ref = (referrer or "").lower()
    if any(p in ref for p in NOISE_REFERRER_PATTERNS):
        return True
    pth = path or ""
    return any(p.search(pth) for p in NOISE_PATH_PATTERNS)
