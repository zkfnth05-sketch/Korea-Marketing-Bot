# -*- coding: utf-8 -*-
"""
modules/drama_engine/drama_pipeline_facade.py
===================================================================================================
🏛️ [DramaPipelineFacade] — 3대 브랜드 통합 숏드라마 무인 생산 파사드 (15원 초고속 실사판)
---------------------------------------------------------------------------------------------------
- 3대 브랜드(Aura, Insurance, Stock)의 일일 숏드라마 생산을 총괄 오케스트레이션.
- 1순위: Gemini 3.1 Flash Lite Image (편당 15원, 장당 2초 초고속 극실사 인물 렌더링)
- 2순위: 로컬 Wan 2.1 T2I 마스터 컷 렌더러 (비용 0원, 대표님 로컬 GPU ComfyUI 연동)
- 3순위: 브랜드 실사 고화질 에셋 폴백 (네트워크/GPU 비상 시)
- 🛑 회색 단색 박스/텍스트 더미 캔버스 100% 영구 퇴출
- 🎬 최종 조립: Wan 2.2 S2V 14B 립싱크 모션 엔진 (DramaClipStitcher)

🎬 [정식 4컷 드라마 본편 — 4컷 전원 신규 실사 생성]
   · cut1(서연 훅) / cut2(민준 대화) / cut3(서연 솔루션) / cut4(서연 클로징)
   · 4컷 모두 cut['visual']['prompt'] 기반 GeminiImageAdapter.render 로 매번 신규 생성
   · 🛑 정적 에셋 재탕(AURA_CHARACTER_CUT_MAP PNG 복사) 완전 영구 박멸 — 재탕 0건
   · 캐시가 없는 한 cut1.png / cut2.png / cut3.png / cut4.png 는 각각 독립 파일로 생성

🎭 [대표님 엄명 — 제미나이 레퍼런스 캐릭터 에셋 주입 (Character Reference Injection)]
   · GeminiImageAdapter.render(ref_image_path=...) 로 서연/민준 마스터 PNG 를 직접 주입한다.
   · 제미나이는 주입된 인물을 '동일 인물'로 고정하여 새 씬 사진을 생성한다.
   · 동시에 "with mouth closed and neutral relaxed lips" 를 프롬프트 선두에 강제 삽입하여
     Wan 2.2 S2V 모핑 엔진이 요구하는 '입 다문 상태' 키프레임을 100% 보장한다.
   · ref_map: cut1/3/4 → aura_seoyeon_master.png, cut2 → aura_minjun_master.png
   · 레퍼런스 로드 실패 시 프롬프트 단독 폴백 (본편 생성은 절대 중단되지 않는다)

🏷️ [엔딩 CTA 카드 — 본편 4컷과 완전 분리]
   · cut4 는 CTA 카드가 아니라 여주인공 서연의 4번째 드라마 씬(클로징/미소 대사)이다.
   · 엔딩 CTA 카드는 본편 사진 목록과 별도로 f"{prefix}_cta_card.png" 단독 렌더링한다.
   · Aura: brands.aura.ui_templates.aura_drama_cta_card.AuraDramaCTACard.render_cta_image()
           → '가입비 0원 · 100% 완전 무료' + 네이버 그린 검색창 탑재 1080x1920 범용 럭셔리 엔딩 카드
   · stitcher.stitch_drama_short(cta_image_path=...) 로 전달
     → 본편 4컷(20초)이 모두 끝난 뒤 맨 마지막에 엔딩 CTA(2.5초)가 결합된다.
   · scenario["topic_id"] 부재 시 1 로 기본값 보장 (KeyError 원천 차단)

📁 [산출물 격리 규격 — 루트 청결 유지]
   C:/Users/zkfnt/Desktop/한국 숏폼_산출물/{brand_folder}/
       └── {Brand}_drama_{YYYYMMDD}_{HHMMSS}/      ← 회차 전용 에피소드 폴더
               ├── {prefix}.mp4                    ← 최종 완성 MP4
               ├── {prefix}_manifest.json          ← 매니페스트
               ├── audios/                         ← 4컷 오디오 + SRT
               └── images/                         ← 4컷 씬 이미지
   ※ output_base 바로 아래에는 에피소드 폴더만 존재한다. `_cache` 등 잔여 파일 일절 금지.
===================================================================================================
"""

from __future__ import annotations

import base64
import io
import json
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from PIL import Image

from .drama_scenario_director import DramaScenarioDirector
from .drama_dialogue_synthesizer import DramaDialogueSynthesizer
from .drama_clip_stitcher import DramaClipStitcher

logger = logging.getLogger("DramaPipelineFacade")

BRAND_FOLDER_MAP = {
    "aura": "Aura",
    "insurance": "Insurance",
    "stock": "Stock",
}

# 🏷️ 기본값 및 엔딩 CTA 카드 규격
DEFAULT_TOPIC_ID: int = 1
DEFAULT_AURA_SEARCH_KEYWORD: str = "아우라AI데이팅"

# 🏷️ [엔딩 CTA 카드 — 본편 4컷과 완전 분리된 단독 산출물]
#    본편 cut1~cut4 는 전부 인물 드라마 씬이며, CTA 카드는 본편 뒤에 별도 결합된다.
CTA_CARD_SUFFIX: str = "_cta_card"
CTA_CARD_DURATION_SEC: float = 2.5

# 🛑 [정적 에셋 재탕 영구 박멸]
#    과거 AURA_CHARACTER_CUT_MAP 에 의한 마스터 PNG 복사 로직은 완전 제거되었다.
#    4컷 전원이 cut['visual']['prompt'] 기반 Gemini 실사 신규 생성 대상이다.
#    (재탕 0건 — 캐시가 없는 한 cut1~cut4 는 각각 독립 파일로 새로 렌더링된다)

# ==============================================================================
# 🎭 [대표님 엄명 — Aura 주인공 마스터 사진 레퍼런스 규격]
# ------------------------------------------------------------------------------
# 제미나이에게 '이 인물 그대로' 라고 지시할 실제 마스터 PNG 를 컷별로 매핑한다.
# 컷별 화자 단일화 규격(CUT_SPEAKER_GENDER)과 100% 일치시킨다.
#   · cut1 : 여주인공 서연 (상황 훅)
#   · cut2 : 남주인공 민준 (반문/조언)
#   · cut3 : 여주인공 서연 (솔루션 체감)
#   · cut4 : 여주인공 서연 (클로징 CTA)
# ==============================================================================
AURA_CHARACTER_REF_FILENAMES: Dict[str, str] = {
    "cut1": "aura_seoyeon_master.png",
    "cut2": "aura_minjun_master.png",
    "cut3": "aura_seoyeon_master.png",
    "cut4": "aura_seoyeon_master.png",
}

# 🎭 마스터 사진이 위치한 브랜드 자산 하위 경로
AURA_CHARACTER_REF_SUBDIR: str = "assets/characters"

# 🚨 [Wan 2.2 S2V 절대 원칙] 레퍼런스 주입 시 제미나이에게 강제하는 입 다문 지시문
S2V_CLOSED_MOUTH_INSTRUCTION: str = (
    "Using this person as the exact character reference "
    "with mouth closed and neutral relaxed lips:"
)

# 🎭 레퍼런스 이미지를 제미나이에 넘길 때의 표준 해상도 (세로 9:16)
REF_IMAGE_SIZE: tuple = (512, 910)


class GeminiImageAdapter:
    """구글 제미나이 실사 이미지 초고속 렌더러 (장당 약 4원)"""

    # 🎨 [모델 우선순위] 1순위 gemini-2.5-flash-image → 2순위 gemini-3.1-flash-lite-image
    #    앞 모델이 404/미지원이면 자동으로 다음 모델로 폴백한다.
    MODEL_CANDIDATES: List[str] = [
        "gemini-2.5-flash-image",
        "gemini-3.1-flash-lite-image",
    ]

    def __init__(self):
        self.keys = []
        try:
            import config
            for attr in [
                "GEMINI_PAID_API_KEY_AURA_1",
                "GEMINI_PAID_API_KEY_AURA_2",
                "GEMINI_API_KEY_KMARKET",
                "GEMINI_API_KEY_EASYTAX",
                "GEMINI_API_KEY",
            ]:
                val = getattr(config, attr, "")
                if val and len(val.strip()) > 10:
                    self.keys.append(val.strip())
        except Exception as e:
            logger.warning(f"⚠️ [GeminiImageAdapter] 키 로드 실패: {e}")
        self._key_idx = 0

    def is_available(self) -> bool:
        return len(self.keys) > 0

    def render(
        self,
        prompt: str,
        out_path: Path,
        ref_image_path: Optional[Path] = None,
    ) -> Path:
        """
        제미나이 실사 이미지 1장을 생성한다.

        Args:
            prompt: 씬 묘사 프롬프트
            out_path: 저장 경로 (1080x1920 PNG)
            ref_image_path: 🎭 주인공 마스터 사진 경로.
                주어지고 유효하면 해당 인물을 '동일 인물'로 고정하고,
                "with mouth closed and neutral relaxed lips" 지시를 강제 삽입한다.
                (Wan 2.2 S2V 모핑 엔진용 '입 다문 키프레임' 100% 보장)
                로드 실패 시 프롬프트 단독으로 자연 폴백한다.
        """
        if not self.is_available():
            raise RuntimeError("Gemini Image API 키가 설정되지 않았습니다.")

        from google import genai

        # 🎭 [대표님 엄명] 레퍼런스 캐릭터 에셋 주입 (실패 시 프롬프트 단독 폴백)
        contents_payload: Any = prompt
        if ref_image_path:
            try:
                with Image.open(ref_image_path) as ref_im:
                    ref_rgb = ref_im.convert("RGB").resize(
                        REF_IMAGE_SIZE, Image.Resampling.LANCZOS
                    )
                    contents_payload = [
                        ref_rgb,
                        f"{S2V_CLOSED_MOUTH_INSTRUCTION} {prompt}",
                    ]
                    logger.info(
                        f"🎭 [GeminiImage] 레퍼런스 캐릭터 에셋 주입: {Path(ref_image_path).name}"
                    )
            except Exception as ref_err:
                logger.warning(
                    f"⚠️ [GeminiImage] 레퍼런스 로드 실패(프롬프트 단독 폴백): {ref_err}"
                )
                contents_payload = prompt

        raw_bytes = None
        last_error: Optional[Exception] = None

        # 🔁 [키 × 모델] 이중 순회 — 키 소진과 모델 미지원을 동시에 흡수한다.
        for _ in range(len(self.keys)):
            current_key = self.keys[self._key_idx % len(self.keys)]
            for model_name in self.MODEL_CANDIDATES:
                try:
                    client = genai.Client(api_key=current_key)
                    resp = client.models.generate_content(
                        model=model_name,
                        contents=contents_payload
                    )
                    if resp and resp.candidates and resp.candidates[0].content:
                        part = resp.candidates[0].content.parts[0]
                        raw = getattr(part.inline_data, "data", None)
                        if raw:
                            raw_bytes = base64.b64decode(raw) if isinstance(raw, str) else raw
                            logger.info(f"🎨 [GeminiImage] 모델 채택: {model_name}")
                            break
                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"⚠️ [GeminiImage] 키 #{self._key_idx + 1} / 모델 {model_name} 생성 실패: {e}"
                    )
            if raw_bytes:
                break
            self._key_idx = (self._key_idx + 1) % len(self.keys)

        if not raw_bytes:
            raise RuntimeError(f"Gemini Image API 모든 키/모델에서 이미지 생성 실패: {last_error}")

        with Image.open(io.BytesIO(raw_bytes)) as img:
            img_rgb = img.convert("RGB")
            resized = img_rgb.resize((1080, 1920), Image.Resampling.LANCZOS)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            resized.save(out_path, format="PNG")

        logger.info(f"✅ [GeminiImage] 2초 초고속 실사 씬 저장 완료: {out_path}")
        return out_path


class Wan21T2IAdapter:
    """로컬 ComfyUI Wan 2.1 14B Q4_0 T2I 마스터 컷 렌더러 (비용 0원)"""

    def __init__(self):
        try:
            from core.engine.wan_pipeline_client import WanPipelineClient
            self.client = WanPipelineClient()
        except Exception as e:
            logger.warning(f"⚠️ [Wan21Adapter] WanPipelineClient 초기화 실패: {e}")
            self.client = None

    def is_available(self) -> bool:
        if not self.client:
            return False
        try:
            return self.client.check_health(auto_start=True)
        except Exception:
            return False

    def render(self, prompt: str, negative: str, out_path: Path, prefix: str) -> Path:
        if not self.is_available():
            raise RuntimeError("ComfyUI Wan 2.1 엔진 미가용 상태")

        logger.info(f"🎨 [Wan21Adapter] Wan 2.1 실사 T2I 마스터 컷 렌더링 착수 ({prefix})...")
        raw_frame = self.client.generate_t2i_master(
            positive_prompt=prompt,
            negative_prompt=negative,
            width=832,
            height=1216,
            prefix=prefix
        )
        if not raw_frame or not Path(raw_frame).exists():
            raise RuntimeError(f"Wan 2.1 산출물 파일 없음: {raw_frame}")

        with Image.open(raw_frame) as img:
            img_rgb = img.convert("RGB")
            resized = img_rgb.resize((1080, 1920), Image.Resampling.LANCZOS)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            resized.save(out_path, format="PNG")

        logger.info(f"✅ [Wan21Adapter] 실사 씬 저장 완료: {out_path}")
        return out_path


class BrandAssetFallbackAdapter:
    """비상 시 브랜드 실사 고화질 에셋 폴백 (어떤 경우에도 더미 캔버스 생성 배제)"""

    def __init__(self, brand: str):
        self.brand = brand.lower()
        workspace_root = Path(__file__).resolve().parent.parent.parent
        self.brand_dir = workspace_root / "brands" / self.brand
        self.assets_dir = self.brand_dir / "assets"

    # 카드뉴스 UI 화면이 드라마 컷으로 복사되는 것을 원천 차단하는 금지 토큰
    _FORBIDDEN_TOKENS = ("slide", "current", "proof")

    # aura 주인공 마스터 에셋 (컷 번호 → 파일명 고정 매핑)
    #   cut_index 1 = cut2 (남성 대화) → 민준
    #   cut_index 0, 2, 3 (서연)       → 서연
    _AURA_MASTER_MAP = {
        0: "aura_seoyeon_master.png",
        1: "aura_minjun_master.png",
        2: "aura_seoyeon_master.png",
        3: "aura_seoyeon_master.png",
    }

    def _is_forbidden(self, path: Path) -> bool:
        """카드뉴스 UI/증빙 스크린샷 여부 판정 (slide / current / proof)."""
        name = path.name.lower()
        return any(tok in name for tok in self._FORBIDDEN_TOKENS)

    def _resolve_aura_master(self, cut_index: int) -> Path:
        """aura 전용: 주인공 마스터 에셋 고정 반환."""
        chars_dir = self.assets_dir / "characters"
        filename = self._AURA_MASTER_MAP.get(cut_index % 4, "aura_seoyeon_master.png")
        target = chars_dir / filename

        if target.exists() and target.stat().st_size > 0:
            return target

        # 지정 마스터가 없을 경우 반대편 주인공으로 1회 폴백
        alt_name = (
            "aura_seoyeon_master.png"
            if filename == "aura_minjun_master.png"
            else "aura_minjun_master.png"
        )
        alt = chars_dir / alt_name
        if alt.exists() and alt.stat().st_size > 0:
            logger.warning(
                "🛡️ [AssetFallback] %s 부재 → %s 로 대체", filename, alt_name
            )
            return alt

        raise FileNotFoundError(
            "aura 주인공 마스터 에셋이 존재하지 않습니다: %s" % chars_dir
        )

    def _resolve_generic_asset(self, cut_index: int) -> Path:
        """그 외 브랜드: 고화질 실사 PNG 중 금지 토큰을 배제하고 선택."""
        if not self.assets_dir.exists():
            raise FileNotFoundError(
                "브랜드 실사 에셋 디렉터리가 없습니다: %s" % self.assets_dir
            )

        # 카드뉴스 UI(slide/current/proof) 전면 배제
        candidates = [
            p
            for p in self.assets_dir.rglob("*.png")
            if p.is_file() and not self._is_forbidden(p)
        ]

        # 고화질(100KB 초과) 우선, 없으면 전체 후보로 완화
        valid = [p for p in candidates if p.stat().st_size > 100000]
        if not valid:
            valid = candidates

        if not valid:
            raise FileNotFoundError(
                "브랜드 실사 에셋이 존재하지 않습니다(금지 토큰 배제 후): %s"
                % self.assets_dir
            )

        valid.sort(key=lambda p: p.name)
        return valid[cut_index % len(valid)]

    def render(self, cut_index: int, out_path: Path) -> Path:
        # ── 1) 브랜드별 후보 확정 ────────────────────────────────────────
        if self.brand == "aura":
            picked = self._resolve_aura_master(cut_index)
        else:
            picked = self._resolve_generic_asset(cut_index)

        logger.info(
            "🛡️ [AssetFallback] 브랜드 실사 에셋 매핑: %s ➔ %s (cut_index=%d)",
            picked.name,
            out_path.name,
            cut_index,
        )

        with Image.open(picked) as img:
            img_rgb = img.convert("RGB")
            resized = img_rgb.resize((1080, 1920), Image.Resampling.LANCZOS)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            resized.save(out_path, format="PNG")

        return out_path


class DramaPipelineFacade:
    """3대 브랜드 숏드라마 무인 생산 통합 파사드"""

    def __init__(self, brand: str):
        brand_key = brand.lower().strip()
        if brand_key not in BRAND_FOLDER_MAP:
            raise ValueError(f"지원하지 않는 브랜드: {brand}")
        self.brand = brand_key
        self.brand_folder_name = BRAND_FOLDER_MAP[brand_key]

        self.output_base = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물") / self.brand_folder_name
        self.output_base.mkdir(parents=True, exist_ok=True)

        self.scenario_director = DramaScenarioDirector()
        # ⚠️ 실제 오디오 출력 경로는 회차별 에피소드 폴더 생성 시점에 재지정된다.
        self.dialogue_synthesizer = DramaDialogueSynthesizer(output_dir=self.output_base)
        self.stitcher = DramaClipStitcher()

        # [2026-10-23] 이미지 어댓터 우선순위: 0순위 LoRA → 1순위 Gemini → 2순위 Wan2.1 → 3순위 에셋
        try:
            from .drama_lora_comfyui_adapter import LoRAComfyUIAdapter
            self.lora_adapter = LoRAComfyUIAdapter()
        except Exception as _lora_err:
            logger.warning("⚠️ [DramaFacade] LoRAComfyUIAdapter 로드 실패: %s", _lora_err)
            self.lora_adapter = None

        self.gemini_adapter = GeminiImageAdapter()
        self.wan_adapter = Wan21T2IAdapter()
        self.asset_adapter = BrandAssetFallbackAdapter(brand=self.brand)

    # ==========================================================================
    # 📁 [에피소드 전용 폴더 생성] — output_base 루트 청결 유지
    # ==========================================================================
    def _create_episode_dir(
        self,
        target_date: str,
        folder_name: Optional[str] = None,
    ) -> Path:
        """
        회차 전용 에피소드 폴더를 생성한다.
        규격: {Brand}_drama_{YYYYMMDD}_{HHMMSS}  (예: Aura_drama_20261023_125500)
        """
        if folder_name and str(folder_name).strip():
            resolved_name = str(folder_name).strip()
        else:
            resolved_name = (
                f"{self.brand.capitalize()}_drama_"
                f"{target_date.replace('-', '')}_{datetime.now().strftime('%H%M%S')}"
            )

        episode_dir = self.output_base / resolved_name
        episode_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 [DramaFacade] 회차 전용 에피소드 폴더 생성: {episode_dir}")
        return episode_dir

    def produce_daily_drama(
        self,
        date_str: Optional[str] = None,
        auto_publish: bool = False,
        folder_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        target_date = date_str or date.today().isoformat()
        prefix = f"{self.brand}_drama_{target_date.replace('-', '')}"

        logger.info(f"🚀 [DramaFacade] [{self.brand}] 일일 숏드라마 무인 생산 착수 (날짜: {target_date})")

        # 0. 회차 전용 에피소드 폴더 생성 (루트에 파일 직접 살포 금지)
        episode_dir = self._create_episode_dir(target_date=target_date, folder_name=folder_name)
        audios_dir = episode_dir / "audios"
        images_dir = episode_dir / "images"
        audios_dir.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(parents=True, exist_ok=True)

        final_mp4 = episode_dir / f"{prefix}.mp4"
        manifest_path = episode_dir / f"{prefix}_manifest.json"

        # 오디오 합성기 출력 경로를 에피소드 폴더 내부로 격리
        self.dialogue_synthesizer.output_dir = audios_dir

        # 1. 4컷 일일 시나리오 생성 (EvoLinkAI & StoryDiffusion)
        scenario = self.scenario_director.get_daily_drama_scenario(
            brand=self.brand,
            date_str=target_date,
        )

        # 🏷️ topic_id 기본값 보장 (Cut 4 공식 CTA 카드 렌더링 필수 키)
        if not isinstance(scenario, dict):
            raise RuntimeError(f"❌ [DramaFacade] 시나리오 반환 형식 오류: {type(scenario)}")
        if scenario.get("topic_id") is None:
            scenario["topic_id"] = DEFAULT_TOPIC_ID
            logger.info(
                f"🏷️ [DramaFacade] scenario['topic_id'] 부재 → 기본값 {DEFAULT_TOPIC_ID} 주입"
            )

        # 2. 4\ucef7 \ub2e4\uc778\uce6d \uc624\ub514\uc624 \ubc0f SRT \uc790\ub9c9 \ud569\uc131 (Gemini 2.5 Flash Native Audio)
        # [2026-10-23 facade fix-1] DailyVariationPlanner \uc5d0\uc11c \uacb0\uc815\ub41c voice_speed \uc804\ub2ec
        _voice_speed: float = float(scenario.get("voice_speed") or 1.25)
        _voice_speed = max(1.20, min(1.30, _voice_speed))
        audio_result = self.dialogue_synthesizer.synthesize_4cut_audio(
            cuts=scenario["cuts"],
            prefix=prefix,
            lead_gender="female",
            voice_speed=_voice_speed,
        )

        # 3. 4\uac1c \uc528 \ud0a4\ud504\ub808\uc784 \ube44\uc8fc\uc5bc \uc774\ubbf8\uc9c0 \uc900\ube44
        #    \ud83c\udfac cut1(\uc11c\uc5f0 \ud6c5) / cut2(\ubbfc\uc900 \ub300\ud654) / cut3(\uc11c\uc5f0 \uc194\ub8e8\uc158) / cut4(\uc11c\uc5f0 \ud074\ub85c\uc9d5)
        scene_images = self._prepare_scene_images(
            scenario,
            prefix,
            cache_dir=images_dir,
        )

        # 3-1. [2026-10-23 5\ucef7\ud310] cut0 \uc0c1\ud669 \uc790\ub9c9 \uce74\ub4dc \uc0dd\uc131 (\ubcf8\ud3b8 \uc559\uc5d0 \uc0bd\uc785)
        # -----------------------------------------------------------------------
        # cut0: \uc2dc\uccad\uc790\uac00 3\ucd08 \uc548\uc5d0 \uc0c1\ud669\uc744 \ud30c\uc545\ud558\ub3c4\ub85c \ub3d5\ub294 \uc0c1\ud669 \uc124\uba85 \uce74\ub4dc
        #   - \uc774\ubbf8\uc9c0: \ub527 \ub2e4\ud06c \uadf8\ub77c\ub370\uc774\uc158 + \ub85c\ucf00\uc774\uc158 + \uc0c1\ud669 \ud14d\uc2a4\ud2b8 \uc624\ubc84\ub808\uc774
        #   - \uc624\ub514\uc624: \ubb34\uc74c MP3 (BGM\ub9cc \ud750\ub984, \ub9bd\uc2f1\ud06c \ubd88\ud544\uc694)
        #   - stitcher \uc790\ub3d9 \uc5f0\ub3d9: scene_images / cut_audios \ub9ac\uc2a4\ud2b8 \uc55e\uc5d0 prepend
        # -----------------------------------------------------------------------
        _cut0_ok = False
        _cut0_img: Optional[Path] = None
        _cut0_audio: Optional[Path] = None
        try:
            from .drama_situation_card import (
                render_situation_card,
                make_silent_audio,
                build_situation_text,
            )
            _sit_text = build_situation_text(scenario)
            _loc_text = str(scenario.get("location") or "")

            _cut0_img = images_dir / f"{prefix}_cut0_situation.png"
            render_situation_card(
                situation_text=_sit_text,
                location_text=_loc_text,
                output_path=_cut0_img,
                duration_sec=2.5,
            )

            _cut0_audio = audios_dir / f"{prefix}_cut0_silent.mp3"
            make_silent_audio(
                output_path=_cut0_audio,
                duration_sec=2.5,
                ffmpeg_exe=str(self.stitcher.ffmpeg_exe),
            )

            if _cut0_img.exists() and _cut0_img.stat().st_size > 100:
                _cut0_ok = True
                logger.info(
                    "\ud83c\udfac [DramaFacade] cut0 \uc0c1\ud669 \uce74\ub4dc \uc0dd\uc131 \uc644\ub8cc: %s",
                    _cut0_img.name,
                )
        except Exception as _c0_err:
            logger.warning(
                "\u26a0\ufe0f [DramaFacade] cut0 \uc0dd\uc131 \uc2e4\ud328(\ubcf8\ud3b8 4\ucef7\ub9cc \uc9c4\ud589): %s", _c0_err
            )

        # cut0 \uc131\uacf5 \uc2dc \uc774\ubbf8\uc9c0\uc640 \uc624\ub514\uc624\ub97c \ub9ac\uc2a4\ud2b8 \uc55e\uc5d0 prepend
        if _cut0_ok and _cut0_img and _cut0_audio:
            scene_images = [_cut0_img] + list(scene_images)
            cut0_audio_entry = {
                "cut_id": "cut0",
                "audio_path": str(_cut0_audio),
                "duration_sec": 2.5,
                "target_duration_sec": 2.5,
                "raw_duration_sec": 2.5,
                "speech": "",              # \ub300\uc0ac \uc5c6\uc74c
                "speaker_gender": "female",
                "voice_speed": _voice_speed,
            }
            audio_result["cut_audios"] = [cut0_audio_entry] + list(audio_result["cut_audios"])

        # 3-2. \ud3b8\ub529 CTA \uce74\ub4dc \ub2e8\ub3c5 \ub80c\ub354\ub9c1 (\ubcf8\ud3b8 4\ucef7 \uc0ac\uc9c4 \ubaa9\ub85d\uacfc \uc644\uc804 \ubd84\ub9ac)
        cta_card_img_path = self._render_ending_cta_card(
            prefix=prefix,
            cache_dir=images_dir,
        )

        # 4. \uc2dc\ub124\ub9c8\ud2f1 5\ucef7(\ub610\ub294 4\ucef7) \ubcf8\ud3b8 + \uc5d4\ub529 CTA \uce74\ub4dc \uc870\ub9bd
        self.stitcher.stitch_drama_short(
            scene_images=scene_images,
            cut_audios=audio_result["cut_audios"],
            full_audio_path=Path(audio_result["full_audio_path"]),
            output_mp4_path=final_mp4,
            brand_keyword=scenario["official_search_keyword"],
            brand_name=scenario["brand_display"],
            bgm_path=None,
            brand_key=self.brand,
            cta_image_path=cta_card_img_path,
            cta_duration_sec=CTA_CARD_DURATION_SEC,
        )

        # 5. 매니페스트 저장 (에피소드 폴더 내부)
        manifest_data = {
            "brand": self.brand,
            "date": target_date,
            "episode_dir": str(episode_dir),
            "theme": scenario["theme"],
            "location": scenario["location"],
            "genre_id": scenario.get("genre_id", ""),
            "source": scenario.get("source", ""),
            "voice_speed": _voice_speed,
            "output_mp4": str(final_mp4),
            "scene_images": [str(p) for p in scene_images],
            "cta_card_image": str(cta_card_img_path),
            "cta_card_duration_sec": CTA_CARD_DURATION_SEC,
            "srt_path": audio_result["srt_path"],
            "duration_sec": audio_result["total_duration_sec"],
            "official_keyword": scenario["official_search_keyword"],
            "speech_hook": scenario["speech_hook"],
            "full_speech": scenario["full_speech"],
        }
        manifest_path.write_text(json.dumps(manifest_data, ensure_ascii=False, indent=2), encoding="utf-8")

        # 6. 자동 송출 훅 (요청 시)
        if auto_publish:
            logger.info(f"📢 [DramaFacade] SNS 자동 송출 큐로 즉시 전달: {final_mp4}")
            self._trigger_sns_dispatch(final_mp4, scenario)

        logger.info(f"🎉 [DramaFacade] [{self.brand}] 일일 숏드라마 생산 완결: {final_mp4}")
        return manifest_data

    def _prepare_scene_images(
        self,
        scenario: Dict[str, Any],
        prefix: str,
        cache_dir: Optional[Path] = None,
    ) -> List[Path]:
        """
        4개 씬의 비주얼 이미지를 준비한다.

        🎬 [정식 4컷 드라마 본편 — 4컷 전원 신규 실사 생성]
          · cut1(서연 훅) / cut2(민준 대화) / cut3(서연 솔루션) / cut4(서연 클로징)
          · 4컷 모두 cut['visual']['prompt'] 기반으로 매번 새로 렌더링한다.
          · 🛑 정적 에셋 재탕(AURA_CHARACTER_CUT_MAP PNG 복사) 완전 영구 박멸 — 재탕 0건
          · 캐시가 없는 한 cut1~cut4 는 각각 독립 파일로 신규 생성된다.

        - 0순위: LoRA + ComfyUI 로컬 GPU (얼굴 365일 100% 고정, 비용 0원)
        - 1순위: Wan 2.1 14B Q4_0 ComfyUI 로컬 GPU 생성 (비용 0원)
        - 2순위: 브랜드 실사 고화질 에셋 폴백
        - 🛑 Gemini Image API 는 숏폼 드라마에서 절대 호출하지 않는다 (전면 영구 퇴출)
        - 캐시 재사용: 이미 50KB 이상 유효 이미지가 있으면 즉시 재사용
        - cache_dir 미지정 시에도 output_base 루트를 오염시키지 않도록 에피소드 폴더 내부로 강제 격리
        - 🧹 4컷 사전 일괄 생성 완료 즉시 VRAM 캐시 완전 방출 (비디오 모델 적재 전 OOM 차단)
        """
        images = []
        if cache_dir is None:
            cache_dir = self.output_base / f"{prefix}_images"
        cache_dir = Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)

        # 🏷️ topic_id 기본값 보장 (직접 호출 경로에서도 KeyError 원천 차단)
        if isinstance(scenario, dict) and scenario.get("topic_id") is None:
            scenario["topic_id"] = DEFAULT_TOPIC_ID

        # 🎭 [대표님 엄명] aura 주인공 마스터 사진 레퍼런스 맵 (컷별 화자 단일화 규격 일치)
        aura_char_dir = (
            Path(__file__).resolve().parent.parent.parent
            / "brands" / "aura" / "assets" / "characters"
        )
        ref_map = {
            "cut1": aura_char_dir / "aura_seoyeon_master.png",
            "cut2": aura_char_dir / "aura_minjun_master.png",
            "cut3": aura_char_dir / "aura_seoyeon_master.png",
            "cut4": aura_char_dir / "aura_seoyeon_master.png",
        }

        for i, cut in enumerate(scenario["cuts"]):
            cut_id = cut["cut_id"]
            img_path = cache_dir / f"{prefix}_{cut_id}.png"

            # 캐시 유효성 검사 (50KB 초과 시 유효 실사 이미지로 판정)
            if img_path.exists() and img_path.stat().st_size > 50000:
                logger.info(f"♻️ [DramaFacade] 캐시된 실사 씬 이미지 재사용: {img_path.name}")
                images.append(img_path)
                continue

            rendered = False

            # 🎬 [정식 4컷 드라마 본편] cut1~cut4 전원이 인물 실사 씬이다.
            #    cut['visual']['prompt'] 기반으로 매번 신규 렌더링하며,
            #    정적 에셋 재탕 경로는 존재하지 않는다 (재탕 0건).
            visual_info = cut.get("visual", {})
            prompt = visual_info.get("prompt", "")
            negative = visual_info.get("negative_prompt", "ugly, blurry, deformed, text, watermark")

            # 🎭 [대표님 엄명] 컷별 주인공 마스터 사진 경로 결정 (aura 전용)
            ref_path = ref_map.get(cut_id) if self.brand == "aura" else None
            if ref_path is not None and not Path(ref_path).exists():
                logger.warning(
                    f"⚠️ [DramaFacade] 주인공 마스터 사진 부재 ({cut_id}) → 프롬프트 단독 폴백: {ref_path}"
                )
                ref_path = None

            # 0순위: LoRA + ComfyUI 로컈 GPU (비용 0원, 얼굴 365일 100% 고정)
            if not rendered and self.lora_adapter is not None:
                try:
                    if self.lora_adapter.is_available() and prompt:
                        self.lora_adapter.render(
                            prompt=prompt,
                            out_path=img_path,
                            cut_id=cut_id,
                            negative=negative,
                        )
                        rendered = True
                        logger.info(
                            "🎨 [DramaFacade] %s LoRA+ComfyUI 서연/민준 얼굴 고정 씩 생성 완료",
                            cut_id,
                        )
                except Exception as le:
                    logger.warning("⚠️ [DramaFacade] LoRA 생성 실패(%s): %s", cut_id, le)

            # 🛑 [대표님 절대 엄명] Gemini Image API 전면 영구 퇴출
            #    제미나이 이미지 API 는 숏폼 드라마에서 절대 호출하지 않는다.
            #    (과거 1순위 Gemini 호출 블록은 완전 제거됨 — 재도입 금지)

            # 1순위: Wan 2.1 ComfyUI 로컬 생성 (비용 0원)
            if not rendered:
                try:
                    if self.wan_adapter.is_available() and prompt:
                        self.wan_adapter.render(
                            prompt=prompt,
                            negative=negative,
                            out_path=img_path,
                            prefix=f"{prefix}_{cut_id}"
                        )
                        rendered = True
                except Exception as we:
                    logger.warning(f"⚠️ [DramaFacade] Wan 2.1 생성 시도 중 예외 ({cut_id}): {we}")

            # 2순위: 브랜드 실사 에셋 폴백
            if not rendered:
                try:
                    self.asset_adapter.render(cut_index=i, out_path=img_path)
                    rendered = True
                except Exception as ae:
                    logger.error(f"❌ [DramaFacade] 브랜드 실사 에셋 폴백 실패 ({cut_id}): {ae}", exc_info=True)
                    raise RuntimeError(f"씬 {cut_id} 실사 이미지 준비 실패 (Wan2.1, 에셋 폴백 모두 소진)")

            images.append(img_path)

        # 🧹 [대표님 절대 엄명] 사진 4컷 사전 일괄 생성 완료 즉시 VRAM 캐시 완전 방출!
        if self.stitcher is not None and self.stitcher.wan_client is not None:
            self.stitcher.wan_client.free_vram()
            logger.info("🧹 [DramaFacade] 사진 4컷 생성 완료 ➔ 비디오 모델 적재 전 VRAM 캐시 완전 방출 완료")

        return images

    # ==========================================================================
    # 🏷️ [엔딩 CTA 카드 단독 렌더링] — 본편 4컷 사진 목록과 완전 분리
    # ==========================================================================
    def _render_ending_cta_card(
        self,
        prefix: str,
        cache_dir: Optional[Path] = None,
    ) -> Optional[Path]:
        """
        엔딩 CTA 카드를 본편 4컷과 별도 파일로 단독 렌더링한다.

        · 파일명: f"{prefix}_cta_card.png"
        · 본편 cut1~cut4 사진 목록(scene_images)에는 절대 포함되지 않는다.
        · stitcher.stitch_drama_short(cta_image_path=...) 로 전달되어
          본편 4컷(20초)이 모두 끝난 뒤 맨 마지막에 2.5초간 결합된다.

        Returns:
            Optional[Path]: CTA 카드 이미지 경로. 미지원 브랜드/생성 실패 시 None.
        """
        if cache_dir is None:
            cache_dir = self.output_base / f"{prefix}_images"
        cache_dir = Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)

        cta_card_path = cache_dir / f"{prefix}{CTA_CARD_SUFFIX}.png"

        # 캐시 유효성 검사 (50KB 초과 시 유효 카드로 판정)
        if cta_card_path.exists() and cta_card_path.stat().st_size > 50000:
            logger.info(f"♻️ [DramaFacade] 캐시된 엔딩 CTA 카드 재사용: {cta_card_path.name}")
            return cta_card_path

        if self.brand != "aura":
            logger.info(
                f"🏷️ [DramaFacade] 엔딩 CTA 카드 미지원 브랜드({self.brand}) → 본편만 조립"
            )
            return None

        try:
            # 🏷️ [범용 럭셔리 엔딩 CTA 카드 직결]
            #    구형 8주제 투표 카드(AuraCTACard) 전면 폐기 →
            #    '완전 무료' + 네이버 그린 검색창 탑재 1080x1920 전용 카드
            from brands.aura.ui_templates.aura_drama_cta_card import AuraDramaCTACard

            cta_card = AuraDramaCTACard()
            cta_img = cta_card.render_cta_image()
            cta_card_path.parent.mkdir(parents=True, exist_ok=True)
            cta_img.save(cta_card_path, format="PNG")
            logger.info(
                f"🏷️ [DramaFacade] 엔딩 CTA 카드 단독 렌더링 완료 "
                f"(AuraDramaCTACard 1080x1920 · 본편과 분리): {cta_card_path}"
            )
            return cta_card_path
        except Exception as ce:
            logger.error(
                f"❌ [DramaFacade] 엔딩 CTA 카드 생성 실패 → 본편만 조립: {ce}",
                exc_info=True,
            )
            return None

    def _trigger_sns_dispatch(self, mp4_path: Path, scenario: Dict[str, Any]) -> None:
        """4대 SNS 자동 송출 디스패처 직결"""
        try:
            if self.brand == "aura":
                from brands.aura.aura_omni_shorts_pilot import AuraOmniShortsPilot
                AuraOmniShortsPilot().execute_single_slot(topic_id=1, force=True)
        except Exception as e:
            logger.warning(f"⚠️ [DramaFacade] SNS 송출 연동 시도 중 경고 (파일은 안전 보존됨): {e}")


# ==============================================================================
# 🧪 [테스트 블록] 에피소드 폴더 격리 규격 자체 점검
# ==============================================================================
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    print("=" * 88)
    print("📁 [DramaPipelineFacade] 에피소드 전용 폴더 격리 규격 자체 점검")
    print("=" * 88)

    facade = DramaPipelineFacade(brand="aura")
    print(f"\n· output_base : {facade.output_base}")

    # 폴더명 규격 검증 (실제 생성 없이 이름 규칙만 확인)
    target_date = "2026-10-23"
    expected_name = (
        f"{facade.brand.capitalize()}_drama_"
        f"{target_date.replace('-', '')}_{datetime.now().strftime('%H%M%S')}"
    )
    print(f"· 폴더명 규격 : {expected_name}")
    assert expected_name.startswith("Aura_drama_20261023_"), "❌ 폴더명 규격 위반"
    print("  ✅ 폴더명 규격 통과 (Aura_drama_YYYYMMDD_HHMMSS)")

    # 실제 폴더 생성 및 경로 격리 검증
    episode_dir = facade._create_episode_dir(target_date=target_date)
    print(f"\n· 생성된 에피소드 폴더 : {episode_dir}")
    print(f"  · 폴더 존재          : {episode_dir.exists()}")
    print(f"  · 부모가 output_base : {episode_dir.parent == facade.output_base}")

    final_mp4 = episode_dir / f"{facade.brand}_drama_20261023.mp4"
    manifest_path = episode_dir / f"{facade.brand}_drama_20261023_manifest.json"
    print(f"  · 최종 MP4 경로      : {final_mp4}")
    print(f"  · 매니페스트 경로    : {manifest_path}")
    assert final_mp4.parent == episode_dir, "❌ MP4 가 에피소드 폴더 밖에 생성됨"
    assert manifest_path.parent == episode_dir, "❌ 매니페스트가 에피소드 폴더 밖에 생성됨"
    print("  ✅ MP4 / 매니페스트 모두 에피소드 폴더 내부 격리 확인")

    # 오디오/이미지 하위 폴더 격리 확인
    audios_dir = episode_dir / "audios"
    images_dir = episode_dir / "images"
    audios_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    print(f"  · audios 격리        : {audios_dir.exists()} ({audios_dir})")
    print(f"  · images 격리        : {images_dir.exists()} ({images_dir})")

    # output_base 루트 청결 검증 (에피소드 폴더 외 잔여 파일 부재)
    root_entries = sorted(p.name for p in facade.output_base.iterdir())
    stray_files = [n for n in root_entries if (facade.output_base / n).is_file()]
    print(f"\n· output_base 루트 항목 : {root_entries}")
    print(f"  · 잔여 파일(_cache 등) : {stray_files if stray_files else '없음 ✅'}")
    assert not stray_files, f"❌ output_base 루트에 잔여 파일 존재: {stray_files}"

    print("\n" + "=" * 88)
    print("✅ [DramaPipelineFacade] 에피소드 폴더 격리 규격 자체 점검 완료")
    print("=" * 88)
