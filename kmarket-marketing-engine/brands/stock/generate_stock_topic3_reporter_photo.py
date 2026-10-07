# -*- coding: utf-8 -*-
"""
generate_stock_topic3_reporter_photo.py
- StockMaster AI [주제 3번] 여의도 야외 현장 기자(Field Reporter) 컨셉 Wan 2.1 14B T2I 마스터 사진 생성기
"""

import os
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from core.engine.wan_pipeline_client import WanPipelineClient
from core.engine.comfy_process_manager import ComfyProcessManager


def generate_topic3_reporter_photo(seed: int = None):
    print("🚀 [Wan 2.1] ComfyUI 엔진 상태 확인 및 백그라운드 자동 기동...")
    ComfyProcessManager.ensure_running(wait_timeout=90)

    wan_client = WanPipelineClient()
    if not wan_client.check_health(auto_start=True):
        raise RuntimeError("ComfyUI Wan 2.1 GPU 엔진 연결 실패! D:\\ComfyUI_Wan_Engine 상태를 확인해주세요.")

    if seed is None:
        seed = int(time.time() * 1000) % 100000000

    positive_prompt = (
        "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on Apple iPhone 15 Pro, "
        "photographed from 2.5 meters away directly in front, "
        "candid medium cowboy shot showing head, elegant neck, natural shoulders, chest, waist, hips, and tailored suit down to mid-thigh clearly, "
        "minimal compact headroom occupying upper 5% of frame with head positioned high near top edge, "
        "an exceptionally gorgeous, captivating, and glamorous 24-year-old Korean female financial news reporter, "
        "perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck, "
        "breathtakingly stunning K-drama visual beauty, voluminous natural dark silky wavy hair, "
        "seductive feline cat-like hazel eyes with subtle elegant eyeliner, flawless luminous glass skin with soft natural cheek blush, "
        "wearing an exceptionally neat, clean, and elegant formal business suit, a tailored slim-fit dark navy blazer suit jacket over a crisp clean white collared shirt and matching navy tailored suit trousers, "
        "holding a sleek professional television broadcast cube microphone in one hand at chest level, "
        "standing upright and poised outdoors, perfectly centered in frame, "
        "looking directly into camera lens with composed confident closed-mouth expression (lips firmly closed together, strictly zero visible teeth, strictly no teeth showing), "
        "bustling outdoor Yeouido Seoul financial district street background, towering modern glass skyscrapers, Korean financial center streetscape during daytime with crisp natural daylight, "
        "professional outdoor fill lighting, "
        "f/11 deep pan-focus, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, zero yellow tint."
    )

    negative_prompt = (
        "open mouth, parted lips, visible teeth, showing teeth, laughing, grinning, smiling wide, "
        "ugly face, old woman, chubby, distorted features, bad eyes, rolled back eyes, asymmetric face, doll, porcelain skin, plastic skin, "
        "blurry, lens blur, out of focus, bokeh blur, deformed hands, extra fingers, missing fingers, cartoon, anime, 3d render, cgi, watermark, text, male, man, holding phone, smartphone"
    )

    print(f"🎨 [Wan 2.1 T2I] 주제 3번 야외 현장 기자 실사 사진 GPU 렌더링 시작 (Seed={seed})...")
    raw_path = wan_client.generate_t2i_master(
        positive_prompt=positive_prompt,
        negative_prompt=negative_prompt,
        width=832,
        height=1216,
        seed=seed,
        prefix="stock_topic3_reporter_female"
    )
    print(f"✅ [Wan 2.1 T2I] 신규 실사 사진 GPU 렌더링 완료: {raw_path}")
    return Path(raw_path)


if __name__ == "__main__":
    photo_path = generate_topic3_reporter_photo()
    print(f"🎉 생성 완료: {photo_path}")
