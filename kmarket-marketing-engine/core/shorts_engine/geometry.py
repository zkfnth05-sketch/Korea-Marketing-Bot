# -*- coding: utf-8 -*-
import subprocess
import logging
from typing import Dict, List

logger = logging.getLogger('ShortsEngineGeometry')

BOUNCING_BADGE_X_EXPR: str = '60'
BOUNCING_BADGE_AMPLITUDE: int = 18
BOUNCING_BADGE_BASE_Y: int = 1450
BOUNCING_BADGE_FREQ_HZ: float = 1.5
BOUNCING_BADGE_Y_EXPR: str = f'{BOUNCING_BADGE_BASE_Y}-{BOUNCING_BADGE_AMPLITUDE}*abs(sin(2*PI*t*{BOUNCING_BADGE_FREQ_HZ}))'

BOUNCING_PILL_X_EXPR: str = BOUNCING_BADGE_X_EXPR
BOUNCING_PILL_Y_EXPR: str = BOUNCING_BADGE_Y_EXPR

FFMPEG_TIMEOUT_SEC: int = 1800

BRAND_KEY_ALIASES: Dict[str, str] = {
    'aura': 'aura',
    'insurance': 'insurance',
    'insure': 'insurance',
    'insur': 'insurance',
    'stock': 'stock',
    'stock_master': 'stock',
}

def run_ffmpeg_safe(cmd: List[str], timeout: int = FFMPEG_TIMEOUT_SEC) -> subprocess.CompletedProcess:
    try:
        res = subprocess.run(cmd, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        logger.error(f'FFmpeg 타임아웃({timeout}s) - 프로세스 강제 회수')
        raise RuntimeError(f'FFmpeg 타임아웃({timeout}s) 발생')
    if res.returncode != 0:
        err_msg = res.stderr.decode('utf-8', errors='ignore') if res.stderr else ''
        logger.error(f'FFmpeg 종료코드 {res.returncode}: {err_msg[:500]}')
        raise RuntimeError(f'FFmpeg 실패(rc={res.returncode}): {err_msg[:500]}')
    return res

def resolve_brand_key(output_mp4_path: str, brand_name_in_vd: str) -> str:
    mp4_lower = str(output_mp4_path).lower()
    if 'aura' in mp4_lower:
        return 'aura'
    if 'insur' in mp4_lower:
        return 'insurance'
    if 'stock' in mp4_lower:
        return 'stock'
    if brand_name_in_vd in BRAND_KEY_ALIASES:
        return BRAND_KEY_ALIASES[brand_name_in_vd]
    for alias, canonical in BRAND_KEY_ALIASES.items():
        if alias in brand_name_in_vd:
            return canonical
    return brand_name_in_vd or 'aura'
