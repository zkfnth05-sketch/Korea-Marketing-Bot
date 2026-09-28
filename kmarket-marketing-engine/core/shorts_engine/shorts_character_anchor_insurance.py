# -*- coding: utf-8 -*-
"""
ShortsCharacterAnchorInsurance - 🛡️ [보험 리밸런스 전용 캐릭터 & 배경 앵커 모듈]
- 8대 국민 보험 주제별 실제 주 타깃 연령층(30대~50대) 일반인 소비자 페르소나
- 딱딱한 정장 전문가 ❌ ➔ 편안하고 신뢰감 있는 일상 사복의 일반인(내돈내산 호갱탈출 팁) ⭕
- Wan 2.2 S2V 립싱크 헌법 준수:
  1. 치아 노출 제로, 입을 부드럽게 다문 온화한 미소 (gently closed mouth)
  2. 스마트폰 파지 완전 배제 (순수 인물 상반신 포즈)
  3. 얼빡샷 차단 (1.6m~2.0m 미디엄 카우보이 샷, 풍부한 헤드룸 확보)
"""

from typing import Dict, Any, Optional

INSURANCE_TOPIC_SPECS = {
    1: {
        "topic_id": 1,
        "title": "실손의료비 4세대 전환 손익",
        "gender": "female",
        "age": 42,
        "char_desc": (
            "an authentic relatable 42-year-old Korean woman (homemaker and working professional), healthy glowing skin, neat natural elegant hairstyle, "
            "wearing clean stylish civilian casual clothes, a chic modern daily outfit, comfortably sitting upright on a modern living room sofa, "
            "approachable civilian consumer persona, looking directly into camera with genuine friendly expression"
        ),
        "bg_desc": (
            "modern bright sunlit apartment living room with cozy neutral fabric sofa, stylish clean bookshelf and fresh green indoor plants in background, "
            "crisp clear natural window daylight, vivid vibrant realistic color balance, tack sharp f/11 deep pan-focus, zero yellow tint"
        ),
        "vibe": "병원도 안 가는데 매달 11만원 내던 실비 1만2천원으로 줄이고 속 시원해진 40대 똑순이 주부/직장인"
    },
    2: {
        "topic_id": 2,
        "title": "운전자보험 1만원대 다이어트",
        "gender": "male",
        "age": 36,
        "framing": (
            "photographed from 2.2 meters directly in front on Apple iPhone 15 Pro 24mm wide angle camera, camera pulled back with generous distance, "
            "wide medium standing cowboy shot, showing head, broad masculine shoulders, chest, waist, hips, thighs, and hands holding a sleek Apple iPhone naturally at waist level, "
            "solo 1person male, standing confidently on a wide clean modern Seoul Gangnam business district sidewalk, perfectly centered in frame, looking directly into camera lens with engaging relatable eye contact, "
            "perfectly upright head posture with zero tilt, generous open headroom above head occupying upper 25% of frame, "
            "gently closed mouth, natural lips closed together with subtle confident smile, strictly zero open mouth, absolutely zero teeth showing, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire urban street frame, visible fine skin pores and sharp fabric textures"
        ),
        "char_desc": (
            "a handsome and charming 35-year-old Korean male working professional, perfect 8-head-high golden ratio tall fit model proportions, "
            "strictly no glasses, bare clean face with clear natural skin, authentic handsome Korean male facial features, attractive gentle eyes, sharp clean jawline, "
            "stylish trendy Korean parted perm hairstyle (soft wavy side-parted comma hair with natural textured fringe), "
            "wearing a stylish and clean modern Korean smart business casual outfit, a tailored commuter office look with slacks, chic everyday working professional attire, "
            "holding a sleek Apple iPhone naturally in hand at waist height, looking directly into camera lens with confident warm friendly smile, "
            "modern K-drama handsome relatable civilian commuter look"
        ),
        "bg_desc": (
            "bustling modern Seoul Gangnam and Yeouido business boulevard during bright golden morning commute, towering sleek glass skyscrapers reflecting morning sky, "
            "lush green roadside street trees lining the wide pedestrian sidewalk, warm natural morning sunlight casting realistic shadows on pavement, "
            "crystal clear edge-to-edge deep focus across the entire urban street, vivid authentic Korean city realism, zero yellow tint"
        ),
        "vibe": "강남/여의도 도심 빌딩 숲 출근길에서 아이폰 들고 1만3천원 운전자보험 꿀팁 알려주는 8등신 훈남 직장인 실사 비주얼"
    },
    3: {
        "topic_id": 3,
        "title": "암보험 일반암 vs 유사암 진실",
        "gender": "female",
        "age": 45,
        "char_desc": (
            "a poised and sensible 45-year-old Korean career woman, clear fair skin, neat graceful short bob hairstyle, "
            "wearing an elegant cream-colored knit sweater, articulate and trustworthy expression looking directly into camera"
        ),
        "bg_desc": (
            "warm modern home study library with dark oak bookshelves filled with books, warm ambient lighting, crisp deep focus"
        ),
        "vibe": "건강검진 앞두고 증권 열어봤다가 갑상선암 500만원 보고 깜짝 놀라 팩트체크한 40대 여성"
    },
    4: {
        "topic_id": 4,
        "title": "뇌·심장 질환 뇌출혈 vs 뇌혈관",
        "gender": "male",
        "age": 48,
        "char_desc": (
            "a trustworthy and dependable 48-year-old Korean family man, gentle warm smile with gently closed lips, neat parted haircut, "
            "wearing a clean comfortable charcoal grey crewneck sweater, sincere honest eyes looking directly into camera"
        ),
        "bg_desc": (
            "bright modern living room with large window showing soft daylight, minimalist Scandinavian wooden furniture, tack sharp focus"
        ),
        "vibe": "혈압약 먹기 시작해서 증권 펴봤더니 뇌경색 미보장인 거 알고 뇌혈관으로 제대로 갈아탄 40대 가장"
    },
    5: {
        "topic_id": 5,
        "title": "종신보험 저축 오해 & 사업비",
        "gender": "male",
        "age": 33,
        "char_desc": (
            "a smart and sensible 33-year-old Korean male working professional and newlywed, handsome intellectual facial features, "
            "wearing a crisp modern white oxford cotton shirt, looking directly into lens with earnest engaging expression"
        ),
        "bg_desc": (
            "contemporary bright book cafe with warm wooden interiors and subtle city view through glass window, tack sharp f/11 focus"
        ),
        "vibe": "적금인 줄 알고 30만원씩 붓던 종신보험 사업비 30% 떼인 거 알고 정기보험 3만원으로 갈아탄 30대 가장"
    },
    6: {
        "topic_id": 6,
        "title": "어린이·어른이 100세 만기 리모델링",
        "gender": "female",
        "age": 32,
        "char_desc": (
            "a bright and thoughtful 32-year-old Korean young mother, radiant clear skin, charming expressive brown eyes, natural ponytail hair, "
            "wearing a warm cozy ivory oversized knit sweater, relatable friendly demeanor looking into camera"
        ),
        "bg_desc": (
            "cozy sunlit kitchen dining area with warm wood dining table and small potted herb plants, soft morning daylight, deep focus"
        ),
        "vibe": "부모님이 100세 만기로 들어준 보험 서른 살 넘어 열어보고 비갱신형으로 알뜰하게 리모델링한 30대 엄마"
    },
    7: {
        "topic_id": 7,
        "title": "치아보험 임플란트 가입 타이밍",
        "gender": "male",
        "age": 47,
        "char_desc": (
            "a down-to-earth and sincere 47-year-old Korean male self-employed professional, friendly facial lines with warm closed-lip smile, "
            "wearing a casual stylish washed denim shirt over a white tee, candid believable gaze looking directly into lens"
        ),
        "bg_desc": (
            "outdoor covered terrace cafe on a pleasant day, warm ambient daylight, clean urban street greenery in background focus"
        ),
        "vibe": "임플란트 2개 300만원 견적 받고 치과 가기 딱 3달 전 치아보험 가입해서 제대로 뽑아먹은 40대 후반"
    },
    8: {
        "topic_id": 8,
        "title": "1~5종 수술비 매회 반복 특약",
        "gender": "female",
        "age": 44,
        "char_desc": (
            "a refined and articulate 44-year-old Korean woman, delicate natural makeup, neat shoulder-length dark wavy hair, "
            "wearing a chic olive green blouse, intelligent and warm expression looking directly into camera"
        ),
        "bg_desc": (
            "stylish boutique meeting lounge with warm wood accents and soft designer lighting, deep pan-focus edge-to-edge"
        ),
        "vibe": "대장 용종 떼거나 수술할 때마다 1~5종 수술비에서 50만원씩 꼬박꼬박 챙겨 받는 40대 살림꾼"
    }
}


def build_insurance_shorts_t2i_character_prompt(
    topic_id: int = 1,
    custom_char_desc: Optional[str] = None,
    custom_bg_desc: Optional[str] = None,
    gender: Optional[str] = None,
    **kwargs
) -> Dict[str, str]:
    """
    보험 리밸런스 8대 주제별 실제 타깃 연령대(30대~50대) 일반인 마스터 프롬프트 빌더
    - 일상 사복 패션 & 편안한 공간 배경
    - 립싱크 최적화 (gently closed mouth, zero teeth)
    - 얼빡샷 차단 (1.6m~2.8m 미디엄 카우보이 샷)
    """
    preset_key = ((topic_id - 1) % len(INSURANCE_TOPIC_SPECS)) + 1
    spec = INSURANCE_TOPIC_SPECS.get(preset_key, INSURANCE_TOPIC_SPECS[1])

    char_desc = custom_char_desc or spec["char_desc"]
    bg_desc = custom_bg_desc or spec["bg_desc"]
    effective_gender = gender or spec.get("gender", "female")

    # 주제별 맞춤 framing 지원
    if "framing" in spec:
        framing = spec["framing"]
    else:
        framing = (
            f"photographed from 2.8 meters directly in front on Apple iPhone 15 Pro 24mm wide angle camera, "
            f"camera pulled back with generous distance, wide medium seated cowboy shot, showing head, chest, waist, hips, lap, thighs and both hands resting naturally, "
            f"solo 1person {effective_gender}, sitting comfortably upright in the middle of a spacious sofa, perfectly centered in frame, looking directly into camera lens, "
            f"perfectly upright head posture with zero tilt, generous open headroom above head occupying upper 30% of frame, "
            f"gently closed mouth, natural lips closed together with subtle confident smile, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            f"spacious sofa and wide living room background clearly visible on both sides, "
            f"f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, visible fine skin pores and individual fabric knit textures"
        )

    positive_prompt = (
        f"{framing}, {char_desc}, {bg_desc}, "
        f"natural bright crisp daylight lighting, highly realistic 8k resolution, authentic Korean civilian documentary look, master quality"
    )

    negative_prompt = (
        "glasses, spectacles, eyewear, sunglasses, rimless glasses, "
        "chinese style, mainland chinese facial features, douyin aesthetic, heavy square jaw, broad flat nose, round wide face, old fashioned haircut, short buzz cut, slicked back hair, "
        "close-up, extreme close-up, tight shot, bust shot, portrait crop, shoulders only, headshot, face filling frame, cropped forehead, cropped head, head touching frame top, cut off head, "
        "zoomed in, telephoto lens, cropped waist, "
        "looking down, face obstructed, phone blocking face, phone covering mouth, "
        "open mouth, parted lips, showing teeth, tongue out, smiling with teeth, screaming, laughing with open mouth, "
        "tilted head, sideways glance, looking away from camera, angled face, side profile, "
        "heavy bokeh, blurry background, shallow depth of field, f/1.4 blur, cinematic bokeh blur, out of focus background, "
        "distorted hands, extra fingers, deformed face, unnatural plastic skin, cartoon, anime, illustration, 3d render, watermark"
    )

    return {
        "positive": positive_prompt,
        "negative": negative_prompt,
        "topic_id": topic_id,
        "gender": effective_gender,
        "vibe": spec.get("vibe", "")
    }
