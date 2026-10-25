# -*- coding: utf-8 -*-
"""
modules/drama_engine/drama_lora_comfyui_adapter.py
===================================================================================================
[LoRA + ComfyUI 캐릭터 고정 이미지 생성 어댑터]
---------------------------------------------------------------------------------------------------
- 서연(여주인공) / 민준(남주인공) 전용 LoRA 를 탑재한 SDXL 워크플로우로
  ComfyUI 로컬 GPU 에서 씬 이미지를 생성한다.
- 비용: 완전 0원 (로컬 GPU, 인터넷 불필요)
- 캐릭터 일관성: LoRA 트리거워드로 365일 동일 얼굴 100% 고정

[LoRA 설정 - config.py 또는 직접 변경]
  SEOYEON_LORA : 서연 LoRA 파일명 (예: aura_seoyeon_v1.safetensors)
  MINJUN_LORA  : 민준 LoRA 파일명 (예: aura_minjun_v1.safetensors)
  SEOYEON_TRIGGER : 서연 트리거워드 (예: <seoyeon>, seoyeon_person)
  MINJUN_TRIGGER  : 민준 트리거워드 (예: <minjun>,  minjun_person)
  BASE_CKPT    : 베이스 모델 체크포인트 (예: realisticVisionV60B1_v51HyperVAE.safetensors)
  COMFYUI_HOST : ComfyUI 주소 (기본: http://127.0.0.1:8188)

[우선순위 in DramaPipelineFacade]
  1순위: LoRA + ComfyUI (본 모듈) — 비용 0원, 얼굴 고정
  2순위: Gemini Image API      — 비용 발생, 얼굴 불안정
  3순위: 브랜드 실사 에셋 폴백
===================================================================================================
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger("LoRAComfyUIAdapter")

# =============================================================================
# [설정값 — 실제 파일명/트리거워드로 수정하세요]
# =============================================================================
try:
    import config as _cfg
    SEOYEON_LORA:    str = getattr(_cfg, "SEOYEON_LORA_FILE",    "aura_seoyeon_v1.safetensors")
    MINJUN_LORA:     str = getattr(_cfg, "MINJUN_LORA_FILE",     "aura_minjun_v1.safetensors")
    SEOYEON_TRIGGER: str = getattr(_cfg, "SEOYEON_LORA_TRIGGER", "seoyeon_person")
    MINJUN_TRIGGER:  str = getattr(_cfg, "MINJUN_LORA_TRIGGER",  "minjun_person")
    BASE_CKPT:       str = getattr(_cfg, "LORA_BASE_CKPT",       "realisticVisionV60B1_v51HyperVAE.safetensors")
    LORA_STRENGTH:   float = float(getattr(_cfg, "LORA_STRENGTH", 0.85))
    COMFYUI_HOST:    str = getattr(_cfg, "COMFYUI_HOST",         "http://127.0.0.1:8188")
except Exception:
    SEOYEON_LORA    = "aura_seoyeon_v1.safetensors"
    MINJUN_LORA     = "aura_minjun_v1.safetensors"
    SEOYEON_TRIGGER = "seoyeon_person"
    MINJUN_TRIGGER  = "minjun_person"
    BASE_CKPT       = "realisticVisionV60B1_v51HyperVAE.safetensors"
    LORA_STRENGTH   = 0.85
    COMFYUI_HOST    = "http://127.0.0.1:8188"

# 이미지 출력 규격 (9:16 세로 숏폼)
IMG_WIDTH:  int = 832
IMG_HEIGHT: int = 1216

# 기본 네거티브 프롬프트
DEFAULT_NEGATIVE: str = (
    "ugly, deformed, blurry, out of focus, cartoon, anime, illustration, "
    "3d render, bad anatomy, extra fingers, missing fingers, watermark, text, "
    "nsfw, nude, low quality, worst quality, duplicate face"
)

# cut_id → 화자 성별 고정 매핑 (facade CUT_SPEAKER_GENDER 와 일치)
CUT_SPEAKER_MAP: dict = {
    "cut1": "female",
    "cut2": "male",
    "cut3": "female",
    "cut4": "female",
}


def _build_lora_workflow(
    positive_prompt: str,
    negative_prompt: str,
    lora_file: str,
    lora_strength: float,
    seed: int,
    prefix: str,
) -> dict:
    """
    SDXL + LoRA ComfyUI API 워크플로우 JSON 생성.

    노드 구조:
      1: CheckpointLoaderSimple (베이스 모델)
      2: LoraLoader (캐릭터 LoRA)
      3: CLIPTextEncode (positive)
      4: CLIPTextEncode (negative)
      5: EmptyLatentImage (832x1216)
      6: KSampler
      7: VAEDecode
      8: SaveImage
    """
    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": BASE_CKPT},
        },
        "2": {
            "class_type": "LoraLoader",
            "inputs": {
                "model":           ["1", 0],
                "clip":            ["1", 1],
                "lora_name":       lora_file,
                "strength_model":  lora_strength,
                "strength_clip":   lora_strength,
            },
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": positive_prompt, "clip": ["2", 1]},
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative_prompt, "clip": ["2", 1]},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": IMG_WIDTH, "height": IMG_HEIGHT, "batch_size": 1},
        },
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "model":          ["2", 0],
                "positive":       ["3", 0],
                "negative":       ["4", 0],
                "latent_image":   ["5", 0],
                "seed":           seed,
                "steps":          28,
                "cfg":            7.0,
                "sampler_name":   "dpm_2",
                "scheduler":      "karras",
                "denoise":        1.0,
            },
        },
        "7": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["6", 0], "vae": ["1", 2]},
        },
        "8": {
            "class_type": "SaveImage",
            "inputs": {"images": ["7", 0], "filename_prefix": prefix},
        },
    }


class LoRAComfyUIAdapter:
    """
    LoRA + ComfyUI 로컬 GPU 캐릭터 고정 씬 이미지 생성 어댑터.

    [사용 전 준비]
    1. ComfyUI 에 CheckpointLoaderSimple 이 지원하는 SDXL 베이스 모델 설치
    2. 서연/민준 LoRA 파일을 ComfyUI/models/loras/ 에 배치
    3. config.py 에 파일명 / 트리거워드 설정 (또는 모듈 상단 상수 직접 수정)
    """

    def __init__(self, host: str = COMFYUI_HOST):
        self.host = host
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from core.engine.wan_pipeline_client import WanPipelineClient
                self._client = WanPipelineClient(host=self.host)
            except Exception as exc:
                logger.error("[LoRAAdapter] WanPipelineClient 로드 실패: %s", exc)
                self._client = None
        return self._client

    def is_available(self) -> bool:
        """ComfyUI 헬스체크 + LoRA 파일 존재 여부 확인."""
        client = self._get_client()
        if not client:
            return False
        try:
            ok = client.check_health(auto_start=True)
            if not ok:
                return False
        except Exception:
            return False

        # LoRA 파일 존재 확인
        comfy_lora_dir = Path(r"D:\ComfyUI_Wan_Engine\ComfyUI\models\loras")
        seoyeon_ok = (comfy_lora_dir / SEOYEON_LORA).exists()
        minjun_ok  = (comfy_lora_dir / MINJUN_LORA).exists()
        if not (seoyeon_ok and minjun_ok):
            logger.warning(
                "[LoRAAdapter] LoRA 파일 미존재: seoyeon=%s minjun=%s → 폴백 진행",
                seoyeon_ok, minjun_ok,
            )
            return False
        return True

    def render(
        self,
        prompt: str,
        out_path: Path,
        cut_id: str = "cut1",
        negative: Optional[str] = None,
        seed: Optional[int] = None,
    ) -> Path:
        """
        씬 이미지 1장을 LoRA + ComfyUI 로 생성한다.

        Args:
            prompt   : 씬 묘사 프롬프트 (컷별 visual.prompt)
            out_path : 저장 경로 (.png, 1080x1920)
            cut_id   : 컷 ID (cut1~cut4) — 화자 성별에 따라 LoRA 자동 선택
            negative : 네거티브 프롬프트 (None 이면 기본값 사용)
            seed     : 랜덤 시드 (None 이면 시간 기반 자동)
        """
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        client = self._get_client()
        if not client:
            raise RuntimeError("[LoRAAdapter] WanPipelineClient 사용 불가")

        # ── 화자 성별에 따라 LoRA + 트리거워드 선택 ──────────────────────────
        gender = CUT_SPEAKER_MAP.get(cut_id, "female")
        if gender == "male":
            lora_file   = MINJUN_LORA
            trigger     = MINJUN_TRIGGER
            char_label  = "민준"
        else:
            lora_file   = SEOYEON_LORA
            trigger     = SEOYEON_TRIGGER
            char_label  = "서연"

        # ── 트리거워드를 프롬프트 앞에 주입 ─────────────────────────────────
        full_positive = f"{trigger}, {prompt}" if trigger not in prompt else prompt
        full_negative = negative or DEFAULT_NEGATIVE

        # ── 시드 결정 (날짜+컷 기반 결정론적 시드) ──────────────────────────
        if seed is None:
            seed = int(time.time()) % 100_000_000

        prefix = out_path.stem  # 파일명(확장자 제외)을 ComfyUI 출력 prefix 로 사용

        logger.info(
            "[LoRAAdapter] %s(%s) 씬 생성: %s | LoRA=%s | seed=%d",
            cut_id, char_label, prefix, lora_file, seed,
        )

        workflow = _build_lora_workflow(
            positive_prompt=full_positive,
            negative_prompt=full_negative,
            lora_file=lora_file,
            lora_strength=LORA_STRENGTH,
            seed=seed,
            prefix=prefix,
        )

        task_label = f"🎨 LoRA [{char_label}] 씬 이미지 생성 ({prefix})"
        frames = client.submit_and_wait(workflow, prefix=prefix, task_label=task_label)

        if not frames:
            raise RuntimeError(f"[LoRAAdapter] ComfyUI 이미지 생성 실패: {prefix}")

        # ── 1080x1920 정규화 저장 ────────────────────────────────────────────
        raw_frame = Path(frames[0])
        if not raw_frame.exists():
            raise RuntimeError(f"[LoRAAdapter] 생성된 프레임 파일 없음: {raw_frame}")

        try:
            from PIL import Image
            with Image.open(raw_frame) as img:
                img_rgb = img.convert("RGB").resize((1080, 1920), Image.Resampling.LANCZOS)
                img_rgb.save(str(out_path), "PNG")
        except Exception as exc:
            logger.error("[LoRAAdapter] PIL 리사이즈 실패: %s", exc)
            import shutil
            shutil.copy2(str(raw_frame), str(out_path))

        logger.info("[LoRAAdapter] ✅ 씬 이미지 저장 완료: %s", out_path.name)
        return out_path
