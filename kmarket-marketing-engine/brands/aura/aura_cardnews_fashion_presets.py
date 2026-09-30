# -*- coding: utf-8 -*-
"""
AuraCardnewsFashionPresets - 👗 [Aura 카드뉴스 2030 여성 10대 명품 소개팅 착장 프리셋]
===================================================================================
• 역할:
  - 1번 주제("소개팅 긴급 탈출 전화") 등 실사 인물 카드뉴스에서
  - 1번(OTS 소개팅), 2번(호텔 화장실 파우더룸), 3번(호텔 정문 5m 탈출)에
  - 100% 동일한 의상(Outfit)과 헤어스타일(Hairstyle)을 주입하여 완벽한 개연성 보장
  - 카드뉴스 생성 시마다 10종의 스타일리시한 명품 착장을 순환/랜덤 적용하여 다양성 극대화
"""

import random
from typing import Dict, Any, List, Optional

AURA_FASHION_PRESETS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "name_ko": "클래식 청담 트위드 룩",
        "hair_prompt": "calm and elegant low bun hairstyle, refined and neat side parting",
        "outfit_prompt": (
            "stylish sophisticated civilian dating clothes, an upscale chic dinner outfit with a tailored cream ivory tweed cropped jacket with subtle gold buttons, "
            "layered over a soft ivory silk sleeveless blouse and elegant high-waisted wide-leg tailored cream trousers"
        ),
        "vibe": "고급스럽고 격식 있는 청담동 비스트로"
    },
    {
        "id": 2,
        "name_ko": "청순 캐시미어 페미닌 룩",
        "hair_prompt": "natural soft long wavy hairstyle falling gently over shoulders, natural feminine C-curl",
        "outfit_prompt": (
            "stylish sophisticated civilian dating clothes, a luxurious soft oatmeal beige boat-neck cashmere knit sweater, "
            "paired with a graceful flowing pleated midi skirt in warm neutral ivory, delicate minimalist gold pendant necklace"
        ),
        "vibe": "단아하고 청순하며 여성스러운 분위기"
    },
    {
        "id": 3,
        "name_ko": "시크 네이비 테일러드 룩",
        "hair_prompt": "sleek polished low ponytail hairstyle, clean silhouette with delicate wisps of hair",
        "outfit_prompt": (
            "stylish sophisticated civilian dating clothes, a perfectly fitted deep dark navy single-breasted tailored blazer, "
            "crisp white silk-cotton collar shirt, and slim tailored cigarette trousers with subtle black leather belt"
        ),
        "vibe": "세련되고 지적인 전문직 커리어우먼 느낌"
    },
    {
        "id": 4,
        "name_ko": "러블리 로즈 트위드 셋업",
        "hair_prompt": "graceful romantic half-up half-down hairstyle with soft face-framing wavy strands",
        "outfit_prompt": (
            "stylish sophisticated civilian dating clothes, an enchanting muted pastel rose-pink tweed cropped jacket and matching A-line midi skirt two-piece set, "
            "delicate pearl button accents and subtle romantic sheen"
        ),
        "vibe": "사랑스럽고 화사한 첫인상"
    },
    {
        "id": 5,
        "name_ko": "카멜 캐시미어 & 모크넥 룩",
        "hair_prompt": "sophisticated shoulder-length natural S-curl hair with rich healthy shine",
        "outfit_prompt": (
            "stylish sophisticated civilian dating clothes, an elegant camel brown handmade double-faced wool coat draped softly, "
            "fitted ivory fine-gauge mock-neck knit, and deep mocha brown tailored wide trousers"
        ),
        "vibe": "가을/겨울 감성 럭셔리 호텔 다이닝"
    },
    {
        "id": 6,
        "name_ko": "모던 스카이블루 실크 룩",
        "hair_prompt": "neat and clean medium-length glossy straight hair tucked neatly behind ears",
        "outfit_prompt": (
            "stylish sophisticated civilian dating clothes, a subtle lustrous pastel sky-blue silk draped blouse, "
            "paired with a high-waisted charcoal gray pencil skirt and refined silver accents"
        ),
        "vibe": "도회적이고 지적인 모던 시크"
    },
    {
        "id": 7,
        "name_ko": "포근 라벤더 니트 & 슬립 스커트",
        "hair_prompt": "effortlessly chic claw-clip updo hairstyle with soft natural texture",
        "outfit_prompt": (
            "stylish sophisticated civilian dating clothes, a cozy soft pastel lavender mohair knit cardigan worn as a top with delicate mother-of-pearl buttons, "
            "paired with a flowing cream ivory bias-cut satin silk slip midi skirt"
        ),
        "vibe": "트렌디한 한남/성수 와인바 감성"
    },
    {
        "id": 8,
        "name_ko": "프렌치 카키 트렌치 룩",
        "hair_prompt": "chic textured chin-length tassel bob cut or sleek neat low bun",
        "outfit_prompt": (
            "stylish sophisticated civilian dating clothes, a classic khaki beige double-breasted cotton trench coat, "
            "layered over a minimalist black fine-knit long dress with clean lines"
        ),
        "vibe": "무심한 듯 감각적인 파리지앵 프렌치 시크"
    },
    {
        "id": 9,
        "name_ko": "세이지 민트 & 머메이드 룩",
        "hair_prompt": "voluminous long soft wavy hair with warm natural luster",
        "outfit_prompt": (
            "stylish sophisticated civilian dating clothes, a fresh delicate sage mint half-neck fitted fine knit, "
            "paired with an elegant flowing beige mermaid-silhouette midi skirt that flatters graceful movement"
        ),
        "vibe": "화사하고 산뜻한 봄/초여름 소개팅"
    },
    {
        "id": 10,
        "name_ko": "한남 힙 오버핏 블레이저 룩",
        "hair_prompt": "sleek center-parted low ponytail with immaculate high-fashion gloss",
        "outfit_prompt": (
            "stylish sophisticated civilian dating clothes, a contemporary charcoal oversized tailored blazer with structured shoulders, "
            "layered over a minimalist black slip top and tailored charcoal trousers, modern sculptural silver earrings"
        ),
        "vibe": "트렌디하고 감각적인 한남동 와인 다이닝"
    }
]


def get_fashion_preset(preset_id: Optional[int] = None) -> Dict[str, Any]:
    """
    지정된 ID(1~10) 또는 랜덤으로 2030 여성 소개팅 착장 프리셋 반환
    """
    if preset_id is not None:
        for p in AURA_FASHION_PRESETS:
            if p["id"] == preset_id:
                return p
    # 미지정 시 랜덤 선택
    return random.choice(AURA_FASHION_PRESETS)


def get_all_presets() -> List[Dict[str, Any]]:
    """전체 10개 프리셋 목록 반환"""
    return AURA_FASHION_PRESETS
