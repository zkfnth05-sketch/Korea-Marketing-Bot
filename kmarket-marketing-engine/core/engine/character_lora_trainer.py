# -*- coding: utf-8 -*-
"""
Character LoRA Trainer for Realistic Vision V5.1
================================================

SD 1.5 (SG161222/Realistic_Vision_V5.1_noVAE) 기반 캐릭터 고정용 LoRA 트레이너.
100% 무인 자율 파이프라인 표준 구현.

핵심 아키텍처
-------------
1) 사전 캐싱(Pre-caching Latents & Embeddings)
   - 데이터셋의 모든 image-text 쌍을 스캔
   - VAE(AutoencoderKL)로 이미지 -> [4, 64, 64] latents 캐싱
   - CLIPTextModel로 캡션 -> [77, 768] text embeddings 캐싱
   - 캐싱 직후 VAE / Text Encoder / Tokenizer 를 del + empty_cache() 로 VRAM 100% 확보

2) UNet LoRA 주입 & 학습
   - peft LoraConfig(r, lora_alpha, target_modules=["to_k","to_q","to_v","to_out.0"],
                    init_lora_weights="gaussian")
   - UNet 본체 freeze, LoRA 어댑터 파라미터만 학습
   - DDPMScheduler 로 랜덤 timestep + gaussian noise 주입 후 노이즈 예측 MSE 손실
   - AdamW(lora_params, lr, weight_decay=1e-2) + fp16 autocast + GradScaler

3) 안전한 저장 및 2중 자동 배포
   - unet.save_lora_adapter(save_dir, adapter_name="default",
                            safe_serialization=True, weight_name="xxx.safetensors")
   - 배포지 1: D:/ComfyUI_Wan_Engine/ComfyUI/models/loras/
   - 배포지 2: kmarket-marketing-engine/brands/aura/assets/lora_weights/

4) CLI + 함수형 인터페이스 동시 지원
   - train_character_lora(data_dir, output_name, steps, lr, lora_rank, base_model)
   - argparse CLI: --character --data_dir --output_name --steps --lr --lora_rank --base_model

실측 검증 환경
-------------
- torch 2.15.0.dev+cu130 / diffusers 0.40.0 / peft 0.20.0
- GPU: RTX 5060 Ti (15.9GB, 가용 14.82GB)
- UNet.save_lora_adapter(save_directory, adapter_name='default',
                         upcast_before_saving=False, safe_serialization=True,
                         weight_name: str | None = None)
"""

import os
import sys
import gc
import math
import time
import shutil
import argparse
import logging
from pathlib import Path

import torch
import torch.nn.functional as F
from PIL import Image, ImageOps

from diffusers import AutoencoderKL, DDPMScheduler, UNet2DConditionModel
from transformers import CLIPTextModel, CLIPTokenizer
from peft import LoraConfig


# =============================================================================
# 상수 / 기본값
# =============================================================================

DEFAULT_BASE_MODEL = "SG161222/Realistic_Vision_V5.1_noVAE"
DEFAULT_STEPS = 500
DEFAULT_LR = 1e-4
DEFAULT_LORA_RANK = 16
DEFAULT_RESOLUTION = 512
DEFAULT_SEED = 42
LOG_EVERY = 50

# SD 1.5 VAE scaling factor
VAE_SCALE_FACTOR = 0.18215

# LoRA target modules (SD1.5 UNet cross/self attention projection)
LORA_TARGET_MODULES = ["to_k", "to_q", "to_v", "to_out.0"]

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")

# 배포지 (2중 배포)
COMFYUI_LORA_DIR = Path("D:/ComfyUI_Wan_Engine/ComfyUI/models/loras")
ENGINE_LORA_DIR = Path(
    "kmarket-marketing-engine/brands/aura/assets/lora_weights"
)

# 엔진 루트 추정 (이 파일 기준: core/engine/character_lora_trainer.py)
_THIS_FILE = Path(__file__).resolve()
_ENGINE_ROOT_CANDIDATES = [
    _THIS_FILE.parents[2],  # .../kmarket-marketing-engine
    _THIS_FILE.parents[3],  # .../한국 마케팅봇
]

logger = logging.getLogger("character_lora_trainer")


# =============================================================================
# 로깅 설정
# =============================================================================

def setup_logging(verbose: bool = False) -> None:
    """콘솔 로깅 초기화 (중복 핸들러 방지)."""
    level = logging.DEBUG if verbose else logging.INFO
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] %(levelname)-7s | %(message)s",
                datefmt="%H:%M:%S",
            )
        )
        root.addHandler(handler)
    root.setLevel(level)
    logger.setLevel(level)


# =============================================================================
# 유틸리티
# =============================================================================

def resolve_engine_lora_dir() -> Path:
    """엔진 자체 LoRA 저장소의 절대 경로를 결정한다."""
    for root in _ENGINE_ROOT_CANDIDATES:
        candidate = root / ENGINE_LORA_DIR
        # kmarket-marketing-engine 폴더가 실제로 존재하는 루트를 우선 선택
        if (root / "kmarket-marketing-engine").is_dir():
            return candidate
    # 폴백: 현재 작업 디렉터리 기준
    return Path.cwd() / ENGINE_LORA_DIR


def ensure_safetensors_suffix(name: str) -> str:
    """weight_name 이 반드시 .safetensors 로 끝나도록 보장한다.

    diffusers 의 save_lora_adapter 는 weight_name 을 '파일명'으로 그대로 사용하므로
    확장자가 없으면 ComfyUI 로더가 인식하지 못한다.
    """
    name = (name or "").strip()
    if not name:
        name = "character_lora"
    if not name.lower().endswith(".safetensors"):
        name = f"{name}.safetensors"
    return name


def pick_device() -> torch.device:
    """학습 디바이스 선택 (CUDA 우선)."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    logger.warning("CUDA 미가용 — CPU 로 진행합니다 (매우 느립니다).")
    return torch.device("cpu")


def log_gpu_memory(tag: str = "") -> None:
    """VRAM 사용량 로깅 (진단용)."""
    if not torch.cuda.is_available():
        return
    try:
        allocated = torch.cuda.memory_allocated() / (1024 ** 3)
        reserved = torch.cuda.memory_reserved() / (1024 ** 3)
        total = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
        logger.info(
            "VRAM[%s] allocated=%.2fGB reserved=%.2fGB total=%.2fGB",
            tag or "-", allocated, reserved, total,
        )
    except Exception:  # 진단 실패는 학습을 막지 않는다
        pass


# =============================================================================
# 1) 데이터셋
# =============================================================================

class CharacterDataset(torch.utils.data.Dataset):
    """캐릭터 이미지 + 캡션 페어 데이터셋.

    - .png / .jpg / .jpeg / .webp 스캔
    - 동명 .txt 캡션 읽기 (없으면 'a photo of {character}' 폴백)
    - 512x512 리사이즈 후 [-1, 1] 텐서 변환
    """

    def __init__(
        self,
        data_dir,
        character: str = "character",
        resolution: int = DEFAULT_RESOLUTION,
    ):
        self.data_dir = Path(data_dir)
        self.character = character
        self.resolution = int(resolution)
        self.fallback_caption = f"a photo of {character}"
        self.samples = []  # list[tuple[Path, str]]

        if not self.data_dir.is_dir():
            raise FileNotFoundError(f"데이터셋 폴더가 없습니다: {self.data_dir}")

        self._scan()

        if not self.samples:
            raise RuntimeError(
                f"이미지-캡션 쌍을 찾지 못했습니다: {self.data_dir} "
                f"(지원 확장자: {', '.join(IMAGE_EXTENSIONS)})"
            )

        logger.info(
            "데이터셋 스캔 완료: %d개 이미지 (%s)",
            len(self.samples), self.data_dir,
        )

    def _scan(self) -> None:
        """이미지 파일을 정렬된 순서로 수집하고 캡션을 결합한다."""
        image_paths = sorted(
            p for p in self.data_dir.iterdir()
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
        )

        missing_caption = 0
        for img_path in image_paths:
            caption_path = img_path.with_suffix(".txt")
            if caption_path.is_file():
                try:
                    caption = caption_path.read_text(encoding="utf-8").strip()
                except UnicodeDecodeError:
                    caption = caption_path.read_text(
                        encoding="utf-8", errors="ignore"
                    ).strip()
            else:
                caption = ""

            if not caption:
                caption = self.fallback_caption
                missing_caption += 1

            self.samples.append((img_path, caption))

        if missing_caption:
            logger.warning(
                "캡션 누락 %d건 → 폴백 캡션 '%s' 사용",
                missing_caption, self.fallback_caption,
            )

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int):
        img_path, caption = self.samples[index]

        with Image.open(img_path) as im:
            im = im.convert("RGB")
            # 비율 보존 크롭(ImageOps.fit): 1080x1920 세로 인물 사진을 512x512 정사각으로
            # 단순 resize 하면 얼굴이 넙데데하게 찌그러진다. ImageOps.fit 은 종횡비를
            # 유지한 채 중앙 크롭하므로 왜곡이 0% 이며, centering=(0.5, 0.35) 로
            # 크롭 중심을 상단 35% 지점(얼굴/상반신)에 고정하여 인물 구도를 보존한다.
            im = ImageOps.fit(
                im,
                (self.resolution, self.resolution),
                method=Image.LANCZOS,
                centering=(0.5, 0.35),
            )
            # PIL -> tensor [3, H, W], 0~1
            tensor = torch.from_numpy(
                __import__("numpy").array(im, dtype="float32")
            ).permute(2, 0, 1) / 255.0

        # [0, 1] -> [-1, 1]
        tensor = tensor * 2.0 - 1.0

        return {"pixel_values": tensor, "caption": caption, "path": str(img_path)}


# =============================================================================
# 2) 사전 캐싱 (Latents & Embeddings)
# =============================================================================

@torch.no_grad()
def precache_latents_and_embeddings(
    dataset: CharacterDataset,
    base_model: str,
    device: torch.device,
    cache_dir=None,
    batch_size: int = 1,
    use_cache: bool = True,
):
    """VAE latents 와 CLIP text embeddings 를 사전 계산하여 캐싱한다.

    Returns
    -------
    (latents, embeddings) : tuple[torch.Tensor, torch.Tensor]
        latents    : [N, 4, 64, 64]  (float16, CPU)
        embeddings : [N, 77, 768]    (float16, CPU)

    캐싱 완료 후 VAE / Text Encoder / Tokenizer 를 메모리에서 완전 해제하여
    학습 단계에서 VRAM 을 100% 확보한다.
    """
    cache_path = None
    if cache_dir is not None:
        cache_path = Path(cache_dir) / "latents_embeddings_cache.pt"
        if use_cache and cache_path.is_file():
            try:
                payload = torch.load(cache_path, map_location="cpu")
                if (
                    payload.get("num_samples") == len(dataset)
                    and payload.get("base_model") == base_model
                ):
                    logger.info("캐시 재사용: %s", cache_path)
                    return payload["latents"], payload["embeddings"]
                logger.info("캐시 무효(개수/모델 불일치) → 재생성")
            except Exception as exc:
                logger.warning("캐시 로드 실패(%s) → 재생성", exc)

    logger.info("VAE / Text Encoder 로드 중: %s", base_model)
    vae = AutoencoderKL.from_pretrained(
        base_model, subfolder="vae", torch_dtype=torch.float16
    ).to(device)
    vae.eval()

    tokenizer = CLIPTokenizer.from_pretrained(base_model, subfolder="tokenizer")
    text_encoder = CLIPTextModel.from_pretrained(
        base_model, subfolder="text_encoder", torch_dtype=torch.float16
    ).to(device)
    text_encoder.eval()

    log_gpu_memory("캐싱 시작")

    all_latents = []
    all_embeddings = []
    total = len(dataset)
    t0 = time.time()

    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        batch_pixels = []
        batch_captions = []

        for i in range(start, end):
            item = dataset[i]
            batch_pixels.append(item["pixel_values"])
            batch_captions.append(item["caption"])

        pixel_values = torch.stack(batch_pixels, dim=0).to(
            device, dtype=torch.float16
        )

        # --- VAE latent 인코딩: [B,3,512,512] -> [B,4,64,64] ---
        latent_dist = vae.encode(pixel_values).latent_dist
        latents = latent_dist.sample() * VAE_SCALE_FACTOR
        all_latents.append(latents.detach().to("cpu", dtype=torch.float16))

        # --- CLIP text embedding: [B,77] -> [B,77,768] ---
        tokens = tokenizer(
            batch_captions,
            padding="max_length",
            max_length=tokenizer.model_max_length,
            truncation=True,
            return_tensors="pt",
        )
        embeds = text_encoder(tokens.input_ids.to(device))[0]
        all_embeddings.append(embeds.detach().to("cpu", dtype=torch.float16))

        done = end
        if done % 10 == 0 or done == total:
            logger.info(
                "캐싱 진척 %d/%d (%.1f%%) elapsed=%.1fs",
                done, total, done * 100.0 / total, time.time() - t0,
            )

    latents_tensor = torch.cat(all_latents, dim=0)
    embeddings_tensor = torch.cat(all_embeddings, dim=0)

    logger.info(
        "캐싱 완료: latents=%s embeddings=%s",
        tuple(latents_tensor.shape), tuple(embeddings_tensor.shape),
    )

    # --- 캐시 디스크 저장 ---
    if cache_path is not None:
        try:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            torch.save(
                {
                    "latents": latents_tensor,
                    "embeddings": embeddings_tensor,
                    "num_samples": len(dataset),
                    "base_model": base_model,
                },
                cache_path,
            )
            logger.info("캐시 저장: %s", cache_path)
        except Exception as exc:
            logger.warning("캐시 저장 실패(무시하고 진행): %s", exc)

    # --- VRAM 100% 확보: VAE / Text Encoder / Tokenizer 완전 해제 ---
    try:
        del vae
        del text_encoder
        del tokenizer
    except Exception:
        pass
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
    log_gpu_memory("캐싱 후 해제")

    return latents_tensor, embeddings_tensor


# =============================================================================
# 3) LoRA 주입
# =============================================================================

def build_lora_unet(
    base_model: str,
    lora_rank: int,
    device: torch.device,
    gradient_checkpointing: bool = True,
):
    """UNet 로드 + LoRA 어댑터 주입 + LoRA 파라미터만 학습 가능 상태로 전환."""
    logger.info("UNet 로드 중: %s (subfolder=unet, fp16)", base_model)
    unet = UNet2DConditionModel.from_pretrained(
        base_model, subfolder="unet", torch_dtype=torch.float16
    )

    lora_config = LoraConfig(
        r=int(lora_rank),
        lora_alpha=int(lora_rank),
        target_modules=list(LORA_TARGET_MODULES),
        init_lora_weights="gaussian",
    )
    unet.add_adapter(lora_config, adapter_name="default")
    logger.info(
        "LoRA 주입 완료: r=%d alpha=%d targets=%s",
        lora_rank, lora_rank, LORA_TARGET_MODULES,
    )

    # UNet 본체 전체 freeze
    unet.requires_grad_(False)

    # LoRA 어댑터 파라미터만 학습 활성화
    # NOTE: UNet 이 fp16 으로 로드되면 add_adapter 가 만든 LoRA 파라미터도 fp16 이 되고,
    #       GradScaler.unscale_() 가 "Attempting to unscale FP16 gradients" 로 예외를 던진다.
    #       따라서 LoRA 파라미터만 float32 로 승격하여 수치적 안정성과 GradScaler 호환성을 확보한다.
    lora_params = []
    for name, param in unet.named_parameters():
        if "lora" in name.lower():
            if param.dtype != torch.float32:
                param.data = param.data.to(torch.float32)
            param.requires_grad_(True)
            lora_params.append(param)

    if not lora_params:
        raise RuntimeError(
            "LoRA 파라미터를 찾지 못했습니다. add_adapter 배선을 확인하십시오."
        )

    # fp32 승격 검증 (GradScaler 호환성 보장)
    fp16_left = [n for n, p in unet.named_parameters()
                 if "lora" in n.lower() and p.dtype != torch.float32]
    if fp16_left:
        logger.warning(
            "LoRA 파라미터 중 fp32 미승격 %d건: %s",
            len(fp16_left), fp16_left[:3],
        )
    else:
        logger.info("LoRA 파라미터 fp32 승격 완료 (GradScaler 호환)")

    trainable = sum(p.numel() for p in lora_params)
    total = sum(p.numel() for p in unet.parameters())
    logger.info(
        "학습 파라미터: %s / 전체 %s (%.3f%%)",
        f"{trainable:,}", f"{total:,}", trainable * 100.0 / max(total, 1),
    )

    if gradient_checkpointing:
        try:
            unet.enable_gradient_checkpointing()
            logger.info("gradient checkpointing 활성화 (VRAM 절감)")
        except Exception as exc:
            logger.warning("gradient checkpointing 실패(무시): %s", exc)

    unet.to(device)
    unet.train()
    log_gpu_memory("UNet 로드 후")

    return unet, lora_params


# =============================================================================
# 3-1) LoRA 키 표준화 (unet. 접두사 강제)
# =============================================================================

def _standardize_lora_keys_in_file(safetensors_path) -> dict:
    """safetensors 파일의 모든 텐서 키에 'unet.' 접두사를 강제로 부여한다.

    배경
    ----
    `UNet2DConditionModel.save_lora_adapter()` 는 diffusers 버전/저장 경로에 따라
    키를 `to_q.lora_A.weight` 처럼 접두사 없이 저장하는 경우가 있다.
    이 경우 `StableDiffusionPipeline.load_lora_weights()` 와 ComfyUI 로더가
    "No LoRA keys associated to UNet2DConditionModel found" 경고를 내고
    LoRA 를 전혀 적용하지 않는 치명적 무음 실패(silent failure)가 발생한다.

    처리
    ----
    - 이미 'unet.' 으로 시작하는 키는 그대로 유지
    - 그 외 모든 키는 'unet.' + key 로 변환
    - 변경이 있을 때만 원자적(임시파일 → os.replace)으로 덮어쓴다.

    Returns
    -------
    dict
        {"path": str, "total": int, "renamed": int, "already_ok": int,
         "sample_before": list[str], "sample_after": list[str]}
    """
    from safetensors.torch import load_file, save_file

    path = Path(safetensors_path)
    if not path.is_file():
        raise FileNotFoundError(f"LoRA safetensors 파일이 없습니다: {path}")

    state_dict = load_file(str(path), device="cpu")
    total = len(state_dict)
    if total == 0:
        logger.warning("LoRA 파일이 비어 있습니다(키 0개): %s", path)
        return {
            "path": str(path), "total": 0, "renamed": 0, "already_ok": 0,
            "sample_before": [], "sample_after": [],
        }

    sample_before = list(state_dict.keys())[:3]

    standardized = {}
    renamed = 0
    already_ok = 0
    for key, tensor in state_dict.items():
        if key.startswith("unet."):
            new_key = key
            already_ok += 1
        else:
            new_key = "unet." + key
            renamed += 1
        standardized[new_key] = tensor

    sample_after = list(standardized.keys())[:3]

    if renamed == 0:
        logger.info(
            "LoRA 키 표준화 불필요 — 이미 전 키(%d개)가 'unet.' 접두사 보유", total,
        )
        return {
            "path": str(path), "total": total, "renamed": 0,
            "already_ok": already_ok,
            "sample_before": sample_before, "sample_after": sample_after,
        }

    # 원자적 덮어쓰기 (중간 실패 시 원본 보존)
    tmp_path = path.with_name(path.name + ".tmp")
    try:
        save_file(standardized, str(tmp_path), metadata={"format": "pt"})
        os.replace(str(tmp_path), str(path))
    finally:
        if tmp_path.is_file():
            try:
                tmp_path.unlink()
            except Exception:
                pass

    logger.info(
        "LoRA 키 표준화 완료: 총 %d개 중 %d개에 'unet.' 접두사 부여 "
        "(이미 정상 %d개) → %s",
        total, renamed, already_ok, path,
    )
    logger.info("  키 예시 before=%s", sample_before)
    logger.info("  키 예시 after =%s", sample_after)

    return {
        "path": str(path), "total": total, "renamed": renamed,
        "already_ok": already_ok,
        "sample_before": sample_before, "sample_after": sample_after,
    }


# =============================================================================
# 4) 학습 루프
# =============================================================================

def train_character_lora(
    data_dir,
    output_name: str = "character_lora",
    steps: int = DEFAULT_STEPS,
    lr: float = DEFAULT_LR,
    lora_rank: int = DEFAULT_LORA_RANK,
    base_model: str = DEFAULT_BASE_MODEL,
    character: str = "character",
    resolution: int = DEFAULT_RESOLUTION,
    seed: int = DEFAULT_SEED,
    cache_dir=None,
    gradient_accumulation: int = 1,
    deploy: bool = True,
    verbose: bool = False,
):
    """캐릭터 LoRA 학습 메인 함수 (함수형 인터페이스).

    Returns
    -------
    dict
        {
          "weight_name": str,
          "primary_path": str,
          "deployed": list[str],
          "final_loss": float,
          "steps": int,
        }
    """
    setup_logging(verbose)
    t_start = time.time()

    device = pick_device()
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    weight_name = ensure_safetensors_suffix(output_name)
    logger.info("=" * 70)
    logger.info("캐릭터 LoRA 학습 시작")
    logger.info("  character   : %s", character)
    logger.info("  data_dir    : %s", data_dir)
    logger.info("  output_name : %s", weight_name)
    logger.info("  steps       : %d", steps)
    logger.info("  lr          : %g", lr)
    logger.info("  lora_rank   : %d", lora_rank)
    logger.info("  base_model  : %s", base_model)
    logger.info("  device      : %s", device)
    logger.info("=" * 70)

    # ---- 1) 데이터셋 ----
    dataset = CharacterDataset(
        data_dir=data_dir, character=character, resolution=resolution
    )

    # ---- 2) 사전 캐싱 (VRAM 확보) ----
    latents, embeddings = precache_latents_and_embeddings(
        dataset=dataset,
        base_model=base_model,
        device=device,
        cache_dir=cache_dir,
        batch_size=1,
        use_cache=True,
    )
    num_samples = latents.shape[0]

    # ---- 3) UNet + LoRA ----
    unet, lora_params = build_lora_unet(
        base_model=base_model,
        lora_rank=lora_rank,
        device=device,
        gradient_checkpointing=True,
    )

    # ---- 4) 스케줄러 / 옵티마이저 ----
    noise_scheduler = DDPMScheduler.from_pretrained(
        base_model, subfolder="scheduler"
    )
    num_train_timesteps = int(noise_scheduler.config.num_train_timesteps)

    optimizer = torch.optim.AdamW(
        lora_params, lr=float(lr), weight_decay=1e-2
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=max(int(steps), 1), eta_min=float(lr) * 0.1
    )
    scaler = torch.amp.GradScaler(
        "cuda", enabled=(device.type == "cuda")
    )

    # ---- 5) 학습 루프 ----
    logger.info("학습 루프 시작 (%d steps)", steps)
    unet.train()
    optimizer.zero_grad(set_to_none=True)

    running_loss = 0.0
    loss_count = 0
    final_loss = float("nan")
    t_train = time.time()

    for step in range(1, int(steps) + 1):
        idx = torch.randint(0, num_samples, (1,)).item()

        latents_batch = latents[idx: idx + 1].to(
            device, dtype=torch.float16, non_blocking=True
        )
        embeds_batch = embeddings[idx: idx + 1].to(
            device, dtype=torch.float16, non_blocking=True
        )

        noise = torch.randn_like(latents_batch)
        timesteps = torch.randint(
            0, num_train_timesteps, (1,), device=device, dtype=torch.long
        )
        noisy_latents = noise_scheduler.add_noise(
            latents_batch, noise, timesteps
        )

        with torch.autocast(
            device_type=device.type,
            dtype=torch.float16,
            enabled=(device.type == "cuda"),
        ):
            model_pred = unet(
                noisy_latents,
                timesteps,
                encoder_hidden_states=embeds_batch,
            ).sample

            if noise_scheduler.config.prediction_type == "v_prediction":
                target = noise_scheduler.get_velocity(
                    latents_batch, noise, timesteps
                )
            else:
                target = noise

            loss = F.mse_loss(
                model_pred.float(), target.float(), reduction="mean"
            )
            loss_scaled = loss / max(int(gradient_accumulation), 1)

        scaler.scale(loss_scaled).backward()

        if step % max(int(gradient_accumulation), 1) == 0:
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(lora_params, max_norm=1.0)
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad(set_to_none=True)
            scheduler.step()

        loss_value = float(loss.detach().item())
        running_loss += loss_value
        loss_count += 1
        final_loss = loss_value

        if step % LOG_EVERY == 0 or step == 1 or step == int(steps):
            avg = running_loss / max(loss_count, 1)
            elapsed = time.time() - t_train
            per_step = elapsed / step
            eta = per_step * (int(steps) - step)
            logger.info(
                "step %4d/%d (%.1f%%) loss=%.5f avg=%.5f lr=%.2e "
                "%.2fs/step ETA=%.0fs",
                step, int(steps), step * 100.0 / int(steps),
                loss_value, avg, optimizer.param_groups[0]["lr"],
                per_step, eta,
            )
            running_loss = 0.0
            loss_count = 0

    train_elapsed = time.time() - t_train
    logger.info(
        "학습 완료: %d steps, %.1fs (%.2fs/step), final_loss=%.5f",
        int(steps), train_elapsed, train_elapsed / max(int(steps), 1),
        final_loss,
    )
    log_gpu_memory("학습 종료")

    # ---- 6) 저장 및 2중 배포 ----
    primary_dir = resolve_engine_lora_dir()
    primary_dir.mkdir(parents=True, exist_ok=True)

    logger.info("LoRA 저장 중: %s (weight_name=%s)", primary_dir, weight_name)
    unet.save_lora_adapter(
        str(primary_dir),
        adapter_name="default",
        safe_serialization=True,
        weight_name=weight_name,
    )

    primary_path = primary_dir / weight_name
    if not primary_path.is_file():
        # diffusers 버전에 따라 하위 폴더에 저장될 수 있으므로 탐색
        found = list(primary_dir.rglob(weight_name))
        if found:
            primary_path = found[0]
        else:
            raise RuntimeError(
                f"LoRA 저장 실패 — 파일을 찾을 수 없습니다: {primary_path}"
            )

    size_mb = primary_path.stat().st_size / (1024 ** 2)
    logger.info("1차 저장 완료: %s (%.2f MB)", primary_path, size_mb)

    # ---- 6-1) LoRA 키 표준화 ('unet.' 접두사 강제) ----
    # diffusers/ComfyUI 가 'No LoRA keys associated' 경고 없이 100% 즉시 로드하도록
    # 저장 직후 파일을 열어 키를 정규화한다. 실패해도 학습 결과물은 보존한다.
    key_report = None
    try:
        key_report = _standardize_lora_keys_in_file(primary_path)
        size_mb = primary_path.stat().st_size / (1024 ** 2)
        logger.info(
            "키 표준화 후 파일 크기: %.2f MB (키 %d개)",
            size_mb, key_report["total"],
        )
    except Exception as exc:
        logger.warning("LoRA 키 표준화 실패(원본 유지, 무시하고 계속): %s", exc)

    # ---- 7) 2중 배포 ----
    deployed = []
    if deploy:
        targets = [COMFYUI_LORA_DIR, resolve_engine_lora_dir()]
        for target in targets:
            try:
                target = Path(target)
                target.mkdir(parents=True, exist_ok=True)
                dest = target / weight_name
                if dest.resolve() == primary_path.resolve():
                    logger.info("배포 생략(동일 경로): %s", dest)
                    deployed.append(str(dest))
                    continue
                shutil.copy2(str(primary_path), str(dest))
                if dest.is_file() and dest.stat().st_size == primary_path.stat().st_size:
                    logger.info("배포 완료: %s", dest)
                    deployed.append(str(dest))
                else:
                    logger.warning("배포 검증 실패(크기 불일치): %s", dest)
            except Exception as exc:
                logger.warning("배포 실패(무시하고 계속): %s → %s", target, exc)

    total_elapsed = time.time() - t_start
    logger.info("=" * 70)
    logger.info("전체 작업 완료: %.1fs", total_elapsed)
    logger.info("  weight_name : %s", weight_name)
    logger.info("  primary     : %s", primary_path)
    for d in deployed:
        logger.info("  deployed    : %s", d)
    logger.info("=" * 70)

    return {
        "weight_name": weight_name,
        "primary_path": str(primary_path),
        "deployed": deployed,
        "final_loss": final_loss,
        "steps": int(steps),
        "lora_keys": key_report,
    }


# =============================================================================
# 5) CLI
# =============================================================================

def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "SD1.5 Realistic Vision V5.1 기반 캐릭터 고정 LoRA 트레이너 "
            "(사전 캐싱 + UNet LoRA + 2중 자동 배포)"
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--character", type=str, default="character",
        help="캐릭터 이름 (캡션 폴백 및 로깅에 사용)",
    )
    parser.add_argument(
        "--data_dir", type=str, default=None,
        help="이미지-캡션 쌍 폴더 (미지정 시 brands/aura/assets/datasets/{character})",
    )
    parser.add_argument(
        "--output_name", type=str, default=None,
        help="LoRA 가중치 파일명 (미지정 시 {character}_lora.safetensors)",
    )
    parser.add_argument(
        "--steps", type=int, default=DEFAULT_STEPS,
        help="학습 스텝 수",
    )
    parser.add_argument(
        "--lr", type=float, default=DEFAULT_LR,
        help="학습률",
    )
    parser.add_argument(
        "--lora_rank", type=int, default=DEFAULT_LORA_RANK,
        help="LoRA rank (r = lora_alpha)",
    )
    parser.add_argument(
        "--base_model", type=str, default=DEFAULT_BASE_MODEL,
        help="베이스 모델 (HF repo id 또는 로컬 경로)",
    )
    parser.add_argument(
        "--resolution", type=int, default=DEFAULT_RESOLUTION,
        help="학습 해상도",
    )
    parser.add_argument(
        "--seed", type=int, default=DEFAULT_SEED,
        help="랜덤 시드",
    )
    parser.add_argument(
        "--cache_dir", type=str, default=None,
        help="latents/embeddings 캐시 저장 폴더 (미지정 시 data_dir/.lora_cache)",
    )
    parser.add_argument(
        "--gradient_accumulation", type=int, default=1,
        help="그래디언트 누적 스텝 수",
    )
    parser.add_argument(
        "--no_deploy", action="store_true",
        help="2중 자동 배포(ComfyUI 등) 생략",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="상세 로그 출력",
    )
    return parser


def _default_data_dir(character: str) -> str:
    """캐릭터명 기반 기본 데이터셋 경로 추정.

    탐색 우선순위
    -------------
    1순위: brands/aura/assets/lora_train/{character}   (실제 학습 데이터 실물 위치)
    2순위: brands/aura/assets/datasets/{character}     (레거시/대체 경로)

    각 루트 후보를 순회하며 1순위 → 2순위 순으로 검사하고,
    발견 즉시 절대 경로를 반환한다. 전부 없으면 1순위 경로를 기본값으로 반환한다.
    """
    sub_paths = [
        ("kmarket-marketing-engine", "brands", "aura", "assets", "lora_train", character),
        ("kmarket-marketing-engine", "brands", "aura", "assets", "datasets", character),
    ]

    for parts in sub_paths:
        for root in _ENGINE_ROOT_CANDIDATES:
            candidate = root.joinpath(*parts)
            if candidate.is_dir():
                logger.info("기본 데이터셋 경로 확정: %s", candidate)
                return str(candidate)

    # 폴백: 1순위(lora_train) 경로를 기본값으로 반환
    fallback = Path.cwd().joinpath(*sub_paths[0])
    logger.warning("데이터셋 폴더 미발견 → 기본 경로 반환: %s", fallback)
    return str(fallback)


def main(argv=None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    setup_logging(args.verbose)

    data_dir = args.data_dir or _default_data_dir(args.character)
    output_name = args.output_name or f"{args.character}_lora"
    cache_dir = args.cache_dir or str(Path(data_dir) / ".lora_cache")

    try:
        result = train_character_lora(
            data_dir=data_dir,
            output_name=output_name,
            steps=args.steps,
            lr=args.lr,
            lora_rank=args.lora_rank,
            base_model=args.base_model,
            character=args.character,
            resolution=args.resolution,
            seed=args.seed,
            cache_dir=cache_dir,
            gradient_accumulation=args.gradient_accumulation,
            deploy=not args.no_deploy,
            verbose=args.verbose,
        )
    except FileNotFoundError as exc:
        logger.error("데이터셋 오류: %s", exc)
        return 2
    except RuntimeError as exc:
        logger.error("학습 실패: %s", exc)
        return 3
    except KeyboardInterrupt:
        logger.warning("사용자 중단(Ctrl+C)")
        return 130
    except Exception as exc:  # 예상치 못한 오류도 무인 파이프라인을 죽이지 않는다
        logger.exception("예상치 못한 오류: %s", exc)
        return 1

    logger.info(
        "결과 요약 → weight=%s loss=%.5f deployed=%d곳",
        result["weight_name"], result["final_loss"], len(result["deployed"]),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
