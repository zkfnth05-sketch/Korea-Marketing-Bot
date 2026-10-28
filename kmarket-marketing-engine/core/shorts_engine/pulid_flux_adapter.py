# -*- coding: utf-8 -*-
"""pulid_flux_adapter.py — PuLID-FLUX 로컬 GPU 씬 생성 독립 레고 블록 모듈.

설계 원칙:
  1) 100% 독립 분리: 외부 거대 프레임워크나 전역 상태에 의존하지 않는 순수 단독 엔진 (SRP 준수).
  2) 3대 브랜드 캐릭터 라우팅:
     - aura: 씬2 남주(민준), 씬1/3/4/5 여주(서연)
     - insurance: 씬2 여주(수진), 씬1/3/4/5 남주(민우)
     - stock: 씬2 남주(준혁), 씬1/3/4/5 여주(지은)
  3) 0원 무인 자동화: ComfyUI REST API(포트 8188)를 통해 GPU 렌더링 자율 수행.
  4) Fail-Closed: 에러 은폐(pass) 전면 배제, 상태/타임아웃/파일크기 엄격 검증.
"""
from __future__ import annotations

import json
import logging
import os
import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

log = logging.getLogger("pulid_flux.engine")

DEFAULT_COMFYUI_HOST = os.getenv("COMFYUI_HOST", "http://127.0.0.1:8188")
DEFAULT_COMFYUI_INPUT = Path(os.getenv("COMFYUI_INPUT_DIR", r"D:\ComfyUI_Wan_Engine\ComfyUI\input"))
DEFAULT_COMFYUI_OUTPUT = Path(os.getenv("COMFYUI_OUTPUT_DIR", r"D:\ComfyUI_Wan_Engine\ComfyUI\output"))


class ComfyUIPulidFluxEngine:
    """PuLID-FLUX 로컬 GPU 기반 캐릭터 얼굴 일관성 씬 생성 엔진."""

    def __init__(
        self,
        endpoint: str = DEFAULT_COMFYUI_HOST,
        comfyui_input_dir: Path = DEFAULT_COMFYUI_INPUT,
        comfyui_output_dir: Path = DEFAULT_COMFYUI_OUTPUT,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.input_dir = Path(comfyui_input_dir)
        self.output_dir = Path(comfyui_output_dir)

    def is_available(self, timeout: float = 2.0) -> bool:
        """ComfyUI 서버의 liveness 및 GPU 통신 상태를 비파괴 검사한다."""
        try:
            url = f"{self.endpoint}/system_stats"
            req = urllib.request.Request(url, headers={"User-Agent": "PuLID-Flux-Client"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                devices = data.get("devices", [])
                has_cuda = any(d.get("type") == "cuda" for d in devices)
                return has_cuda or len(devices) > 0
        except Exception as e:
            log.debug("ComfyUI 미가용 (%s): %s", self.endpoint, e)
            return False

    def resolve_character_master(
        self, brand: str, scene_idx: int, project_root: Optional[Path] = None
    ) -> Path:
        """브랜드 및 씬 인덱스에 따라 전속 마스터 캐릭터 이미지 경로를 결정한다."""
        brand_clean = str(brand).lower().strip()
        if project_root is None:
            project_root = Path(__file__).resolve().parent.parent.parent

        if brand_clean == "aura":
            # 씬 2, 4: 남주 민준, 씬 1, 3, 5: 여주 서연 (SCENE_CHARACTER_MAP SSOT)
            char_id = "aura_minjun_master.png" if scene_idx in (2, 4) else "aura_seoyeon_master.png"
        elif brand_clean == "insurance":
            # 씬 2, 4: 남주 민우, 씬 1, 3, 5: 여주 수진 (3대 앱 공통 표준 규격)
            char_id = "insurance_minwoo_master.png" if scene_idx in (2, 4) else "insurance_sujin_master.png"
        elif brand_clean == "stock":
            # 씬 2, 4: 남주 준혁, 씬 1, 3, 5: 여주 지은
            char_id = "stock_junhyuk_master.png" if scene_idx in (2, 4) else "stock_jieun_master.png"
        else:
            raise ValueError(f"지원되지 않는 브랜드 식별자: '{brand}' (허용: aura, insurance, stock)")

        candidates = [
            project_root / "brands" / brand_clean / "assets" / "characters" / char_id,
            project_root / "assets" / "characters" / char_id,
            project_root / "brands" / brand_clean / "assets" / char_id,
        ]

        for p in candidates:
            if p.is_file() and p.stat().st_size > 0:
                return p

        raise FileNotFoundError(
            f"브랜드 '{brand_clean}' 씬 {scene_idx}용 캐릭터 마스터 에셋 부재: '{char_id}'\n"
            f"탐색 경로: {[str(c) for c in candidates]}"
        )

    def sync_master_to_comfyui(self, master_path: Path) -> str:
        """마스터 이미지를 ComfyUI의 input 디렉터리로 복사하고 파일명을 반환한다."""
        master = Path(master_path)
        if not master.is_file():
            raise FileNotFoundError(f"원본 마스터 파일 미존재: {master}")

        filename = master.name
        self.input_dir.mkdir(parents=True, exist_ok=True)
        target = self.input_dir / filename

        if not target.exists() or target.stat().st_size != master.stat().st_size:
            shutil.copy2(master, target)
            log.info("ComfyUI input 동기화 완료: %s -> %s", master, target)

        return filename

    def build_workflow(
        self,
        image_filename: str,
        prompt_text: str,
        filename_prefix: str,
        seed: int = 42,
        guidance: float = 3.5,
        steps: int = 20,
    ) -> Dict[str, Any]:
        """검증 완료된 PuLID-FLUX + FLUX.1-Dev GGUF ComfyUI 워크플로우 딕셔너리를 생성한다."""
        return {
            "10": {"class_type": "VAELoader", "inputs": {"vae_name": "ae.safetensors"}},
            "16": {
                "class_type": "DualCLIPLoaderGGUF",
                "inputs": {
                    "clip_name1": "t5-v1_1-xxl-encoder-Q4_K_M.gguf",
                    "clip_name2": "clip_l.safetensors",
                    "type": "flux",
                },
            },
            "17": {
                "class_type": "UnetLoaderGGUF",
                "inputs": {"unet_name": "flux1-dev-Q4_K_S.gguf"},
            },
            "25": {
                "class_type": "EmptySD3LatentImage",
                "inputs": {"batch_size": 1, "height": 1280, "width": 720},
            },
            "26": {
                "class_type": "CLIPTextEncode",
                "inputs": {"clip": ["16", 0], "text": str(prompt_text)},
            },
            "27": {
                "class_type": "CLIPTextEncode",
                "inputs": {"clip": ["16", 0], "text": ""},
            },
            "41": {
                "class_type": "LoadImage",
                "inputs": {"image": str(image_filename)},
            },
            "45": {
                "class_type": "PulidFluxModelLoader",
                "inputs": {"pulid_file": "pulid_flux_v0.9.0.safetensors"},
            },
            "47": {
                "class_type": "PulidFluxInsightFaceLoader",
                "inputs": {"provider": "CUDA"},
            },
            "48": {
                "class_type": "PulidFluxEvaClipLoader",
                "inputs": {"eva_clip_file": "EVA02_CLIP_L_336_psz14_s6B.pt"},
            },
            "49": {
                "class_type": "ApplyPulidFlux",
                "inputs": {
                    "attn_mask": None,
                    "end_at": 1.0,
                    "eva_clip": ["48", 0],
                    "face_analysis": ["47", 0],
                    "image": ["41", 0],
                    "model": ["17", 0],
                    "pulid_flux": ["45", 0],
                    "start_at": 0.0,
                    "weight": 0.85,
                },
            },
            "50": {
                "class_type": "FluxGuidance",
                "inputs": {"conditioning": ["26", 0], "guidance": float(guidance)},
            },
            "51": {
                "class_type": "BasicGuider",
                "inputs": {"conditioning": ["50", 0], "model": ["49", 0]},
            },
            "52": {
                "class_type": "RandomNoise",
                "inputs": {"noise_seed": int(seed)},
            },
            "53": {
                "class_type": "BasicScheduler",
                "inputs": {
                    "denoise": 1.0,
                    "model": ["49", 0],
                    "scheduler": "simple",
                    "steps": int(steps),
                },
            },
            "54": {
                "class_type": "KSamplerSelect",
                "inputs": {"sampler_name": "euler"},
            },
            "55": {
                "class_type": "SamplerCustomAdvanced",
                "inputs": {
                    "guider": ["51", 0],
                    "latent_image": ["25", 0],
                    "noise": ["52", 0],
                    "sampler": ["54", 0],
                    "sigmas": ["53", 0],
                },
            },
            "56": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["55", 0], "vae": ["10", 0]},
            },
            "57": {
                "class_type": "SaveImage",
                "inputs": {
                    "filename_prefix": str(filename_prefix),
                    "images": ["56", 0],
                },
            },
        }

    def generate_scene(
        self,
        prompt: str,
        brand: str,
        scene_idx: int,
        out_path: Path,
        seed: Optional[int] = None,
        timeout: float = 180.0,
    ) -> Path:
        """단일 씬에 대해 PuLID-FLUX 로컬 GPU 렌더링을 실행하고 out_path로 저장한다."""
        if not self.is_available():
            raise RuntimeError(f"ComfyUI 서버({self.endpoint}) 응답 없음 또는 GPU 미가용")

        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        master_path = self.resolve_character_master(brand, scene_idx)
        input_image_name = self.sync_master_to_comfyui(master_path)

        if seed is None:
            import random
            seed = random.randint(1000, 99999999)

        # [3D 입체 조명 SSOT] 대표님 절대 지침: 3D 입체 조명 항상 강제 주입 & 어두운 촛불 조명 전면 차단
        lighting_3d = (
            "3D volumetric lighting, dramatic cinematic 3D lighting, sculpted dimensional light and shadow, "
            "beautiful soft rim light highlighting face and hair contours, high-end 3D depth, "
            "bright sunlit studio key light with crystal clear illumination, vivid clear skin, "
            "ABSOLUTELY NO dark muddy shadows, NO dim candlelight, NO flat lighting"
        )

        # [입모양 봉인 SSOT] Wan 2.2 S2V 립싱크 필수 규격 — 시작 키프레임 입모양 100% 다물기 강제
        mouth_seal = (
            "strictly closed mouth, neutral relaxed lips pressed together, mouth shut tightly, "
            "absolutely NO open mouth, NO visible teeth, NO smiling with open mouth, lips completely sealed"
        )

        # [1인 단독 샷 SSOT] 2인 난입 / 트윈 인물 / 파트너 중복 원천 차단
        solo_shot = (
            "solo portrait, single person only, exactly ONE person centered in frame, looking straight at camera, "
            "absolutely NO second person, NO twin, NO couple, NO woman next to him, NO extra body, NO partial person in frame"
        )

        # [브랜드별 캐릭터 의상 SSOT & 체형 SSOT] 대표님 엄명: 화자 일치 의상 고정 & 남주 8등신 건장 체형
        b_low = brand.lower().strip()
        if "aura" in b_low:
            # 씬 2, 4: 남주 민준 | 씬 1, 3, 5: 여주 서연
            if scene_idx in (2, 4):
                wardrobe_str = (
                    "wearing a stylish clean olive-khaki overshirt button-down layered over a crisp white t-shirt, "
                    "consistent signature outfit, absolutely NO brown sweater, NO plain brown sweatshirt, NO female clothing, NO blazer"
                )
                physique_str = (
                    "tall athletic handsome Korean man in his mid-20s, perfectly proportioned 8-head body ratio (8-head proportion physique), "
                    "broad masculine shoulders, healthy well-built chest and neck, handsome confident posture, "
                    "absolutely NO skinny emaciated body, NO narrow shoulders, NO thin neck, NO frail bony frame"
                )
            else:
                wardrobe_str = (
                    "wearing an elegant smart-casual camel brown blazer jacket over a clean white crew-neck top, "
                    "stylish tailored jacket, consistent signature outfit, "
                    "absolutely NO sleeveless top, NO camisole, NO tank top, NO bare shoulders"
                )
                physique_str = (
                    "slender graceful elegant Korean woman in her mid-20s, healthy glowing skin, "
                    "balanced 8-head model proportion, sophisticated poised posture"
                )
        elif "insurance" in b_low:
            # 씬 2, 4: 남주 민우 (남성) | 씬 1, 3, 5: 고객 수진 (여성)
            if scene_idx in (2, 4):
                wardrobe_str = (
                    "wearing a sharp modern dark-navy tailored suit jacket over a crisp white dress shirt with no tie, "
                    "clean professional look, consistent signature outfit, absolutely NO casual clothes, NO female clothing, NO blazer"
                )
                physique_str = (
                    "tall athletic handsome Korean man in his 20s, perfectly proportioned 8-head body ratio (8-head proportion physique), "
                    "broad masculine shoulders, healthy well-built chest, strong confident posture, "
                    "absolutely NO skinny emaciated body, NO narrow shoulders, NO thin neck"
                )
            else:
                wardrobe_str = (
                    "wearing an elegant light-grey smart-casual office blazer over a soft pastel knit, consistent signature outfit, "
                    "absolutely NO sleeveless top, NO camisole, NO tank top, NO bare shoulders"
                )
                physique_str = (
                    "slender graceful elegant Korean woman, healthy glowing skin, balanced 8-head model proportion, sophisticated poised posture"
                )
        else:  # stock or default
            # 씬 1, 3, 5: 여주 지은 | 씬 2, 4: 고객 준혁 (남성)
            if scene_idx in (2, 4):
                wardrobe_str = (
                    "wearing a sophisticated navy knit sweater over a white collared shirt, "
                    "smart financial investor look, consistent signature outfit, absolutely NO female clothing, NO blazer"
                )
                physique_str = (
                    "tall athletic handsome Korean man in his 20s, perfectly proportioned 8-head body ratio (8-head proportion physique), "
                    "broad masculine shoulders, healthy well-built chest, strong confident posture, "
                    "absolutely NO skinny emaciated body, NO narrow shoulders, NO thin neck"
                )
            else:
                wardrobe_str = (
                    "wearing a chic charcoal-grey tailored blazer over a minimalist ivory silk blouse, "
                    "professional financial look, consistent signature outfit, "
                    "absolutely NO sleeveless top, NO camisole, NO tank top"
                )
                physique_str = (
                    "slender graceful elegant Korean woman, healthy glowing skin, balanced 8-head model proportion, sophisticated poised posture"
                )

        # 오염 토큰 소거 (2인 유발 문구)
        prompt_clean = prompt.strip()
        for pollute in ["side by side", "with partner", "two people", "couple walking", "two-shot", "holding hands"]:
            prompt_clean = prompt_clean.replace(pollute, "")

        additions = [solo_shot, physique_str, wardrobe_str]
        if "3d volumetric" not in prompt_clean.lower():
            additions.append(lighting_3d)
        if "closed mouth" not in prompt_clean.lower() and "mouth shut" not in prompt_clean.lower():
            additions.append(mouth_seal)

        full_prompt = f"{prompt_clean}, {', '.join(additions)}" if additions else prompt_clean

        prefix = f"PuLID_{brand.capitalize()}_S{scene_idx}"
        workflow = self.build_workflow(
            image_filename=input_image_name,
            prompt_text=full_prompt,
            filename_prefix=prefix,
            seed=seed,
        )

        prompt_req_data = json.dumps({"prompt": workflow}).encode("utf-8")
        submit_url = f"{self.endpoint}/prompt"
        req = urllib.request.Request(
            submit_url,
            data=prompt_req_data,
            headers={"Content-Type": "application/json", "User-Agent": "PuLID-Flux-Client"},
        )

        with urllib.request.urlopen(req, timeout=10.0) as resp:
            submit_res = json.loads(resp.read().decode("utf-8"))
            prompt_id = submit_res.get("prompt_id")
            if not prompt_id:
                raise RuntimeError(f"ComfyUI 큐 등록 실패 (응답: {submit_res})")

        log.info(
            "PuLID 렌더링 큐 등록 완료 [브랜드=%s, 씬=%d, prompt_id=%s]",
            brand,
            scene_idx,
            prompt_id,
        )

        start_t = time.time()
        poll_interval = 3.0
        while time.time() - start_t < timeout:
            time.sleep(poll_interval)
            try:
                hist_url = f"{self.endpoint}/history/{prompt_id}"
                with urllib.request.urlopen(hist_url, timeout=5.0) as h_resp:
                    hist = json.loads(h_resp.read().decode("utf-8"))
                    if prompt_id in hist:
                        task_data = hist[prompt_id]
                        status_info = task_data.get("status", {})
                        status_str = status_info.get("status_str")

                        if status_str == "error":
                            messages = status_info.get("messages", [])
                            err_msg = str(messages[-1]) if messages else "알 수 없는 ComfyUI 노드 에러"
                            raise RuntimeError(f"ComfyUI 실행 에러 발생: {err_msg}")

                        outputs = task_data.get("outputs", {})
                        save_node = outputs.get("57", {})
                        images = save_node.get("images", [])
                        if not images:
                            raise RuntimeError(f"ComfyUI 렌더 완료되었으나 이미지 산출물 없음: {outputs}")

                        out_filename = images[0]["filename"]
                        subfolder = images[0].get("subfolder", "")
                        source_image = self.output_dir / subfolder / out_filename

                        if not source_image.is_file():
                            raise FileNotFoundError(f"ComfyUI 산출물 파일 미존재: {source_image}")

                        shutil.copy2(source_image, out_path)

                        if not out_path.is_file() or out_path.stat().st_size == 0:
                            raise IOError(f"산출물 복사 검증 실패: {out_path}")

                        elapsed = time.time() - start_t
                        log.info(
                            "PuLID 렌더링 완료 [브랜드=%s, 씬=%d, 소요=%.1f초, 파일크기=%d 바이트]",
                            brand,
                            scene_idx,
                            elapsed,
                            out_path.stat().st_size,
                        )

                        # Wan S2V 및 후속 작업을 위해 ComfyUI 캐시 메모리 방출 (C++ 언로드 크래시 회피를 위해 unload_models=False 고정)
                        try:
                            req_free = urllib.request.Request(
                                f"{self.endpoint}/free",
                                data=json.dumps({"unload_models": False, "free_memory": True}).encode("utf-8"),
                                headers={"Content-Type": "application/json"},
                            )
                            with urllib.request.urlopen(req_free, timeout=5.0) as _:
                                pass
                            log.info("ComfyUI VRAM 캐시 방출 완료 (Wan S2V 가용 VRAM 확보)")
                        except Exception as free_e:
                            log.debug("VRAM 방출 신호: %s", free_e)

                        return out_path

            except (urllib.error.URLError, TimeoutError) as net_err:
                log.debug("폴링 일시적 지연: %s", net_err)
                continue

        raise TimeoutError(f"PuLID 렌더링 시간 초과 ({timeout}초 경과, prompt_id={prompt_id})")
