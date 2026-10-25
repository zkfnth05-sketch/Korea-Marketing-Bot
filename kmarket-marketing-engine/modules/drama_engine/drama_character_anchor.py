# -*- coding: utf-8 -*-
"""
modules/drama_engine/drama_character_anchor.py
===================================================================================================
🎭 [DramaCharacterAnchor] — StoryDiffusion 벤치마킹 기반 4컷 캐릭터 일관성 앵커
---------------------------------------------------------------------------------------------------
오픈소스 기술 접목:
- HVision-NKU/StoryDiffusion의 'Consistent Self-Attention & Style Template' 원리를
  T2I 프롬프트 엔지니어링 및 키프레임 앵커 구조로 실체화.
- 씬(Scene 1~4)과 로케이션이 바뀌어도 주인공(Character A & B)의 얼굴 골격, 헤어스타일,
  의상 시그니처가 왜곡되거나 딴사람으로 바뀌지 않도록 물리적으로 고정(Anchor).
- 컷별 감정선(도파민 훅 ➔ 갈등 핑퐁 ➔ 반전 솔루션 ➔ 여운 미소)과 카메라 앵글을 동적으로 조율.

🚨 [대표님 절대 규격 — 컷별 화자 100% 단일화]
  한 컷 안에서 남녀가 섞여 발화하면, 단일 얼굴로 립싱크하는 S2V 엔진 특성상
  반드시 성별 불일치(남자가 말하는데 여자가 립싱크)가 발생한다.
  따라서 컷별 화자(speaker_gender)를 1명으로 100% 단일화하고,
  해당 컷의 페르소나 얼굴/의상/정체성 프롬프트를 그 화자로 고정한다.
    · cut1 : female (여주인공 독백/상황 훅)
    · cut2 : male   (남주인공의 반문/조언)
    · cut3 : female (여주인공의 솔루션 체감/리액션)
    · cut4 : female (여주인공의 결말 & 공식 검색어 CTA)

💎 [대표님 엄명 — Aura 극상 비주얼 업그레이드 (2026)]
  숏폼 피드에서 '1초 스크롤 스토퍼'로 작동하도록, aura 브랜드의 서연/민준 페르소나를
  대한민국 외모 상위 0.5% 극상 비주얼 규격으로 전면 상향했다.
  (insurance / stock 브랜드 페르소나는 100% 무손상 보존)

🚨🚨 [Wan 2.2 S2V 절대 원칙 — 모든 컷 인물 사진 '입 다문 상태(closed mouth)' 강제]
  S2V(Speech-to-Video)는 오디오 음소에 맞춰 '닫힌 입'을 벌리고 오므리는 모핑 엔진이다.
  시작 키프레임 이미지가 이미 입을 벌리고 있거나('mouth slightly parted', 'speaking' 등)
  치아가 노출되어 있으면, 모핑 시작점과 음소가 어긋나 입술이 찢어지거나 치아가 뭉개지는
  치명적 왜곡(Artifact)이 발생한다.
  따라서 4컷 전 컷의 키프레임은 반드시 '입을 다문 중립 상태'로 고정한다.
    · NEGATIVE_PROMPT_GOLDEN 에 open mouth / parted lips / teeth showing 등 전면 차단어 추가
    · cut_configs 의 모든 감정선 프롬프트에 'closed mouth' 명시
    · build_4cut_prompts 템플릿에 CLOSED_MOUTH_LOCK 상수를 공통 강제 부착
===================================================================================================
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("DramaCharacterAnchor")


# ==============================================================================
# 🎬 [대표님 엄명 — 고화질 시네마틱 수식어 (모든 페르소나 프롬프트 말단 고정)]
# ==============================================================================
CINEMATIC_QUALITY_SUFFIX = (
    "award-winning cinematic 85mm portrait, shallow depth of field, soft beauty lighting, "
    "masterpiece photography, Vogue Korea editorial grade, hyper-detailed authentic facial texture"
)


# ==============================================================================
# 🚨 [Wan 2.2 S2V 절대 원칙 — 입 다문 상태 강제 잠금 상수]
# ------------------------------------------------------------------------------
# S2V 는 '닫힌 입'을 시작점으로 음소 모핑을 수행한다.
# 키프레임이 이미 벌어진 입/노출된 치아를 담고 있으면 입술 찢어짐·치아 뭉개짐이 발생하므로,
# 4컷 전 컷 프롬프트에 아래 문구를 공통 강제 부착한다.
# ==============================================================================
CLOSED_MOUTH_LOCK = (
    "lips closed, mouth firmly closed, neutral relaxed lips, "
    "no teeth visible, sealed lips resting naturally"
)


@dataclass
class PersonaAnchor:
    name: str
    gender: str
    age: str
    ethnicity: str
    hair: str
    facial_features: str
    wardrobe: str
    voice_role: str  # e.g., "female_lead", "male_lead"

    def get_identity_prompt(self) -> str:
        """인물 정체성을 100% 고정하는 베이스 프롬프트

        [대표님 엄명 반영]
        - 프롬프트 말단에 시네마틱 85mm / 보그 코리아 에디토리얼급 고화질 수식어를 고정 부착한다.
        - 수식어는 CINEMATIC_QUALITY_SUFFIX 단일 상수에서만 관리하여 전 페르소나에 일괄 적용한다.
        """
        return (
            f"photorealistic Korean {self.gender}, {self.age} years old, {self.ethnicity}, "
            f"{self.hair}, {self.facial_features}, wearing {self.wardrobe}, "
            f"authentic pore skin texture, realistic natural lighting, 35mm portrait lens, master quality, "
            f"{CINEMATIC_QUALITY_SUFFIX}"
        )


# ==============================================================================
# 👥 브랜드별 고정 페르소나 라이브러리 (StoryDiffusion Style)
# ==============================================================================
BRAND_PERSONAS: Dict[str, Dict[str, PersonaAnchor]] = {
    "aura": {
        # 💎 [여주인공 서연 — 26세 / 대한민국 외모 상위 0.5% 극상 비주얼]
        "female": PersonaAnchor(
            name="서연",
            gender="woman",
            age="26",
            ethnicity="Korean",
            hair=(
                "luxurious glossy shoulder-length soft S-wave jet black hair "
                "with airy curtain bangs framing the face"
            ),
            facial_features=(
                "breathtaking top 0.5% Korean goddess visual, stunning actress-level facial harmony, "
                "sparkling clear almond-shaped eyes with subtle aegyo-sal, perfectly contoured slim V-line jaw, "
                "delicate high nose bridge, soft rosy gradient lips, radiant porcelain glass skin with zero blemishes, "
                "captivating idol-tier aura that makes viewers stop scrolling instantly"
            ),
            wardrobe=(
                "high-end Cheongdam-dong quiet luxury style, elegant off-white cashmere knit top "
                "with subtle collarbone exposure, dainty rose gold necklace"
            ),
            voice_role="female_lead",
        ),
        # 💎 [남주인공 민준 — 28세 / 대한민국 외모 상위 0.5% 극상 비주얼]
        "male": PersonaAnchor(
            name="민준",
            gender="man",
            age="28",
            ethnicity="Korean",
            hair=(
                "impeccably styled natural textured dandy cut with slight parted see-through bangs, "
                "deep dark espresso hair"
            ),
            facial_features=(
                "breathtaking top 0.5% Korean heartthrob visual, Cha Eun-woo and Song Kang tier handsome features, "
                "razor-sharp masculine jawline with defined cheekbones, deep captivating gaze with gentle double eyelids, "
                "aristocratic straight nose bridge, immaculate poreless skin, "
                "commanding yet approachable leading-man charisma"
            ),
            wardrobe=(
                "tailored midnight navy oversized unstructured Italian wool blazer over crisp minimalist white t-shirt, "
                "subtle luxury steel chronograph watch"
            ),
            voice_role="male_lead",
        ),
    },
    "insurance": {
        "female": PersonaAnchor(
            name="지수",
            gender="woman",
            age="34",
            ethnicity="Korean",
            hair="neat low ponytail dark hair",
            facial_features="serious worried expression turning confident, smart rectangular light spectacles",
            wardrobe="tailored beige business trench coat with black inner knit",
            voice_role="female_lead",
        ),
        "male": PersonaAnchor(
            name="도현",
            gender="man",
            age="36",
            ethnicity="Korean",
            hair="classic side-parted textured haircut",
            facial_features="determined expression, slight stubble, earnest realistic appearance",
            wardrobe="navy blue semi-formal knit zip-up with collared shirt",
            voice_role="male_lead",
        ),
    },
    "stock": {
        "female": PersonaAnchor(
            name="유진",
            gender="woman",
            age="29",
            ethnicity="Korean",
            hair="sleek straight bob black hair behind ears",
            facial_features="sharp focused intelligent gaze, modern city tech look",
            wardrobe="minimalist charcoal turtleneck and matte silver watch",
            voice_role="female_lead",
        ),
        "male": PersonaAnchor(
            name="현우",
            gender="man",
            age="31",
            ethnicity="Korean",
            hair="slightly tousled short black hair",
            facial_features="tired late-night working eyes turning sharp with renewed energy",
            wardrobe="relaxed fit sky-blue oxford shirt with sleeves rolled up to elbows",
            voice_role="male_lead",
        ),
    },
}

# ==============================================================================
# 🚫 [네거티브 프롬프트 — Wan 2.2 S2V 입 모핑 왜곡 차단어 전면 추가]
# ------------------------------------------------------------------------------
# S2V 시작 키프레임에 벌어진 입/노출된 치아가 들어가면 입술 찢어짐·치아 뭉개짐이 발생한다.
# 따라서 '입을 벌린 상태'를 지시하는 모든 시각 요소를 네거티브로 강제 차단한다.
# ==============================================================================
NEGATIVE_PROMPT_GOLDEN = (
    "ugly, deformed, disfigured, poor details, bad anatomy, bad hands, missing fingers, "
    "extra fingers, distorted eyes, blurry, low quality, oversaturated, 3d render, cartoon, anime, illustration, "
    "open mouth, parted lips, teeth showing, open lips, speaking mouth, shouting, teeth"
)

# ==============================================================================
# 🎯 [컷별 화자 성별 100% 단일화 매핑 — 절대 불변 규격]
# ==============================================================================
CUT_SPEAKER_GENDER: Dict[str, str] = {
    "cut1": "female",  # 여주인공 독백/상황 훅
    "cut2": "male",    # 남주인공의 반문/조언
    "cut3": "female",  # 여주인공의 솔루션 체감/리액션
    "cut4": "female",  # 여주인공의 결말 & 공식 검색어 CTA
}


class DramaCharacterAnchor:
    """4컷 숏드라마 인물 및 씬 시각 앵커 관리기"""

    def __init__(self, brand: str = "aura"):
        brand_key = brand.lower().strip()
        if brand_key not in BRAND_PERSONAS:
            raise ValueError(f"❌ [DramaCharacterAnchor] 지원하지 않는 브랜드: {brand}. 지원: {list(BRAND_PERSONAS.keys())}")
        self.brand = brand_key
        self.personas = BRAND_PERSONAS[brand_key]

    def get_persona(self, speaker_gender: str) -> PersonaAnchor:
        """화자 성별('female'/'male')에 해당하는 페르소나를 반환한다. (미지정 시 여주인공 폴백)"""
        key = (speaker_gender or "female").lower().strip()
        if key not in self.personas:
            logger.warning(f"⚠️ [DramaCharacterAnchor] 알 수 없는 화자 성별 '{speaker_gender}' → female 폴백")
            key = "female"
        return self.personas[key]

    def build_4cut_prompts(
        self,
        date_seed: str,
        location_desc: str,
        gender_lead: str = "female",
        cut_speakers: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        4개 컷별로 '해당 컷 화자 1명'의 정체성 프롬프트만 적용하여
        캐릭터 프롬프트 및 카메라 앵글을 생성한다.

        🚨 [Wan 2.2 S2V 절대 원칙]
        - 4컷 전 컷의 감정선 프롬프트에 'closed mouth' 를 명시한다.
        - 템플릿 말단에 CLOSED_MOUTH_LOCK 상수를 공통 강제 부착한다.
        - 네거티브에는 벌린 입/노출된 치아 차단어가 포함된다.

        Args:
            date_seed: 일일 결정론적 시드 문자열
            location_desc: 로케이션 묘사
            gender_lead: 기본 리드 성별 (cut_speakers 미지정 컷의 폴백)
            cut_speakers: {"cut1": "female", "cut2": "male", ...} 형태의 컷별 화자 오버라이드

        Returns:
            List[Dict]: 컷별 프롬프트 + speaker_gender / character_name / gender 명시
        """
        # 컷별 화자 성별 확정 (오버라이드 → 기본 매핑 → 리드 성별 순)
        resolved_speakers: Dict[str, str] = {}
        for cut_id, default_gender in CUT_SPEAKER_GENDER.items():
            override = None
            if cut_speakers:
                override = cut_speakers.get(cut_id)
            resolved_speakers[cut_id] = (override or default_gender or gender_lead or "female").lower().strip()

        # 🚨 [S2V 절대 원칙] 모든 컷 감정선에 'closed mouth' 필수 명시
        cut_configs = [
            {
                "cut_id": "cut1",
                "seconds": 3,
                "role": "hook",
                "shot_type": "medium close-up, dramatic side angle",
                "emotion": (
                    "shocked expression with eyes widened in conflict, "
                    "mouth closed, neutral closed lips"
                ),
                "lighting": "cinematic moody contrast lighting, sharp rim light",
            },
            {
                "cut_id": "cut2",
                "seconds": 6,
                "role": "dialogue_pingpong",
                # 🎬 [6인 회의체 심의 결과 — 컷2 투샷 구도 정상화]
                #    기존 'over-the-shoulder conversation shot' 은 누구의 어깨인지 모호하여
                #    남주인공 단독 컷인데도 시선 방향이 뒤집히는 구도 오류가 발생했다.
                #    → 여주인공 서연의 시그니처(긴 흑발 웨이브 + 오프화이트 니트 어깨)를
                #      전경(foreground)에 명시적으로 결속하여 '서연 ➔ 민준' 시선을 확정한다.
                "shot_type": (
                    "over-the-shoulder conversation shot looking from behind female lead Seoyeon "
                    "(showing her distinctive long soft-wavy jet-black hair and off-white knit shoulder "
                    "in foreground), facing the handsome Korean man Minjun sitting across the cafe table"
                ),
                "emotion": (
                    "calm serious listening expression, "
                    "mouth closed, relaxed natural closed lips"
                ),
                "lighting": "natural ambient dialogue lighting, authentic room atmosphere",
            },
            {
                "cut_id": "cut3",
                "seconds": 7,
                "role": "solution_revelation",
                "shot_type": "waist-up shot holding smartphone illuminating face with soft screen glow",
                "emotion": (
                    "relieved gentle expression looking down at smartphone, "
                    "mouth closed, subtle closed-lip pleasant look"
                ),
                "lighting": "warm high-key glowing screen bounce light, premium clarity",
            },
            {
                "cut_id": "cut4",
                "seconds": 4,
                "role": "punchline_cta",
                "shot_type": "clean vertical 9:16 portrait front angle, centered composition",
                "emotion": (
                    "captivating confident gaze looking into camera, "
                    "subtle charming closed-mouth smile, closed lips"
                ),
                "lighting": "studio-grade flattering beauty softbox lighting, clean upper third space",
            },
        ]

        results: List[Dict[str, Any]] = []
        for cfg in cut_configs:
            cut_id = cfg["cut_id"]
            speaker_gender = resolved_speakers[cut_id]

            # 🎯 해당 컷 화자의 페르소나만 단독 적용 (다른 성별 인물 절대 배제)
            persona = self.get_persona(speaker_gender)
            identity = persona.get_identity_prompt()

            # 🚨 [S2V 절대 원칙] CLOSED_MOUTH_LOCK 을 템플릿에 공통 강제 부착
            prompt = (
                f"{identity}, {cfg['emotion']}, {cfg['shot_type']}, "
                f"setting: {location_desc}, {cfg['lighting']}, "
                f"{CLOSED_MOUTH_LOCK}, "
                f"single person only, only one character in frame, "
                f"sharp focus, 8k resolution, raw color grading, hyper-realistic vertical 9:16 framing"
            )
            negative = (
                f"{NEGATIVE_PROMPT_GOLDEN}, two people, multiple people, crowd, "
                f"gender swap, wrong gender, opposite gender in frame"
            )

            results.append({
                "cut_id": cut_id,
                "role": cfg["role"],
                "duration_sec": cfg["seconds"],
                "prompt": prompt,
                "negative_prompt": negative,
                "speaker_gender": speaker_gender,
                "character_name": persona.name,
                "gender": persona.gender,
                "voice_role": persona.voice_role,
            })

        speaker_summary = ", ".join(f"{c['cut_id']}={c['character_name']}({c['speaker_gender']})" for c in results)
        logger.info(
            f"🎭 [DramaCharacterAnchor] 4컷 화자 단일화 앵커 빌드 완료 "
            f"(브랜드={self.brand} | {speaker_summary} | S2V 입 다문 상태 강제 적용)"
        )
        return results
