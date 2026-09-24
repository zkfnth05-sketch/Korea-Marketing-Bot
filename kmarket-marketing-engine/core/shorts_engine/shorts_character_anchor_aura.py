# -*- coding: utf-8 -*-
"""
ShortsCharacterAnchorAura - 💖 [Aura 8대 주제 전용 2030 캐릭터 & 배경 앵커 모듈]
- 8대 주제별 특화 인물 정의(Persona & Fashion) 및 배경 정의(Setting & Lighting) 100% 통일
- [Wan 실전 줌인 편향 보정 규격]:
  1. 주제별 최적 거리 차등화 (1.4m 비디오챗 ~ 4.0m 야외 러닝 와이드 롱샷)
  2. 머리 위 여백(Generous Headroom) 및 주변 환경 심도(Environmental Depth) 확보
  3. 포즈: 스마트폰 파지 완전 배제, 자연스러운 일상 대화/야외 포즈
  4. 표정: Wan 2.2 S2V 립싱크 헌법 준수 (치아 노출 제로, 입을 부드럽게 다문 온화한 미소)
  5. 얼빡샷(extreme close-up) 강력 차단 네거티브 탑재
"""

from typing import Dict, Any, Optional

# 8대 주제별 인물, 배경 및 Wan 실전 보정 거리 매트릭스
AURA_8_TOPIC_SPECS = {
    1: {
        "topic_id": 1,
        "title": "소개팅 탈출 전화",
        "gender": "female",
        "framing": (
            "photographed from 1.2 meters directly across a dining table from the date's first-person eye-level perspective on iPhone 15 Pro, "
            "solo 1person female, perfectly centered in the middle of frame, perfectly frontal portrait view looking directly into the camera lens with warm engaging eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and shoulders, "
            "gently closed mouth, natural lips closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "candid medium shot showing chest, shoulders, and dark wooden dining table clearly, "
            "f/8 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible real pores and hair strands"
        ),
        "char_desc": (
            "a beautiful 28-year-old Korean woman, calm low ponytail hairstyle, clear fair skin, "
            "refined subtle makeup, wearing stylish sophisticated civilian dating clothes, a chic modern evening dinner outfit, "
            "elegant and poised appearance with genuine expressive eyes looking directly into the camera lens"
        ),
        "bg_desc": (
            "moody upscale evening bistro and wine restaurant in Cheongdam, soft warm pin-spot table lighting, "
            "antique dark wooden dining table, delicate wine glasses and neat linen napkin in the background"
        ),
        "vibe": "청담동 고급 비스트로에서 눈길을 싹쓸이하는 세련되고 우아한 로맨스 드라마 여주급 직장인 비주얼"
    },
    2: {
        "topic_id": 2,
        "title": "실시간 자막 통화",
        "gender": "female",
        "framing": (
            "photographed from 2.0 meters away from the date's first-person eye-level perspective on Apple iPhone 15 Pro 24mm main camera, "
            "solo 1person female, perfectly centered in the middle of frame, perfectly frontal portrait view looking directly into the camera lens with warm engaging eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and shoulders, "
            "gently closed mouth, natural lips closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "candid cowboy medium shot showing chest, waist, and warm wooden furniture clearly, generous headroom above, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, completely clear background bookshelves and plants in sharp crisp focus, visible real pores and individual hair strands"
        ),
        "char_desc": (
            "an exceptionally gorgeous 24-year-old Japanese young woman (Nanami), authentic real human model visual, "
            "authentic natural human skin with visible fine pores and realistic delicate skin texture, strictly no airbrushing, "
            "charming expressive doe-like hazel-brown eyes, delicate see-through bangs, neat dark brown shoulder-length hair, "
            "wearing clean stylish civilian casual clothes, a neat comfortable daily outfit, looking directly into the camera lens"
        ),
        "bg_desc": (
            "warm cozy living room with authentic dark oak wooden bookshelves filled with books, "
            "vibrant lush green indoor potted plants, warm directional room ambient lighting creating natural depth and rich realistic shadows, "
            "warm inviting atmosphere with over 75% background rich interior details in tack sharp f/11 focus"
        ),
        "vibe": "도쿄 잇걸 미모의 나나미, 따뜻한 원목 책장과 초록 식물 배경에서 세련된 일상 사복으로 쨍하고 선명한 아이폰 15 Pro 실사 비주얼"
    },
    3: {
        "topic_id": 3,
        "title": "50:50 VIP 게이트",
        "gender": "female",
        "framing": (
            "photographed from 1.2 meters directly across a dining table from the date's first-person eye-level perspective on iPhone 15 Pro, "
            "perfectly frontal portrait view looking directly into the camera lens with warm engaging eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and shoulders, "
            "candid medium shot showing chest, shoulders, and luxurious marble table clearly, "
            "f/8 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible real pores and hair strands"
        ),
        "char_desc": (
            "a stunning sophisticated 28-year-old Korean career woman, high-fashion cool-tone beauty, sleek chic shoulder-length bob haircut, "
            "flawless glass skin, sharp elegant cheekbones, wearing a luxurious tailored navy blue silk collared shirt, "
            "confident aristocratic posture, looking directly into the camera lens"
        ),
        "bg_desc": (
            "luxurious high-end hotel lounge and rooftop cafe in Seoul, elegant marble table, floor-to-ceiling panoramic glass windows "
            "with distant city view, refined ambient warm glow lighting"
        ),
        "vibe": "럭셔리 호텔 라운지에 어울리는 독보적인 세련미와 도회적인 쿨뷰티 여신"
    },
    4: {
        "topic_id": 4,
        "title": "청담동 화보 보정",
        "gender": "female",
        "framing": (
            "photographed from 1.2 meters directly across a dining table from the date's first-person eye-level perspective on iPhone 15 Pro, "
            "perfectly frontal portrait view looking directly into the camera lens with warm engaging eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and shoulders, "
            "candid medium shot showing chest, shoulders, and cafe table clearly, "
            "f/8 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible real pores and hair strands"
        ),
        "char_desc": (
            "a breathtakingly stunning 23-year-old Korean young woman, pure legendary first-love visual aesthetic, "
            "flowing natural dark silky wavy hair, immaculate luminous glass skin, captivating innocent eyes, delicate facial symmetry, "
            "wearing a soft pastel pink cashmere cardigan over a white silk camisole, looking directly into the camera lens"
        ),
        "bg_desc": (
            "sunlit aesthetic studio cafe in Seongsu-dong, soft white linen sheer curtains with gentle sunlight streaming through, "
            "vintage wooden designer chair, warm ambient atmosphere"
        ),
        "vibe": "화보 찍으려고 태어난 듯한 백옥 피부의 압도적 청순 여신 비주얼"
    },
    5: {
        "topic_id": 5,
        "title": "가치관 밸런스 매칭",
        "gender": "female",
        "framing": (
            "photographed from 1.2 meters directly across a dining table from the date's first-person eye-level perspective on iPhone 15 Pro, "
            "perfectly frontal portrait view looking directly into the camera lens with warm engaging eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and shoulders, "
            "candid medium shot showing chest, shoulders, and brunch table clearly, "
            "f/8 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible real pores and hair strands"
        ),
        "char_desc": (
            "an adorably gorgeous 21-year-old Korean college campus goddess, idol visual with bubbly charismatic charm, "
            "fresh glowing dewy skin, youthful bright expressive eyes, neat loose half-updo hairstyle, "
            "wearing a stylish oversized blue-striped boyfriend button-down shirt, looking directly into the camera lens"
        ),
        "bg_desc": (
            "cozy outdoor brunch cafe patio in Yeonnam-dong, rustic wooden table with cute brunch plates and iced latte, "
            "pleasant tree shade with dappled natural sunlight"
        ),
        "vibe": "성수/연남동에서 번호 따일 확률 100%인 사랑스럽고 발랄한 대학생 캠퍼스 여신"
    },
    6: {
        "topic_id": 6,
        "title": "AI 카톡 비서",
        "gender": "male",
        "framing": (
            "photographed from 1.2 meters directly across a dining table from the date's first-person eye-level perspective on iPhone 15 Pro, "
            "perfectly frontal portrait view looking directly into the camera lens with warm engaging eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and shoulders, "
            "candid medium shot showing chest, shoulders, and study table clearly, "
            "f/8 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible real pores and hair strands"
        ),
        "char_desc": (
            "a breathtakingly handsome 27-year-old Korean male lead actor visual, top-tier romantic K-drama male lead aesthetic, "
            "clean stylish dandy haircut, immaculate smooth skin, sharp defined jawline, kind yet deeply charismatic romantic eyes, "
            "wearing a tailored dark navy crewneck wool sweater over a crisp white collared shirt, looking directly into the camera lens"
        ),
        "bg_desc": (
            "modern cozy library book cafe and quiet study lounge, warm amber pendant light hanging above, "
            "rich wooden bookshelves with books in the background, calm and trustworthy intellectual atmosphere"
        ),
        "vibe": "첫 카톡 오면 무조건 칼답장 부르는 넷플릭스 로코 남주급 댄디 훈남"
    },
    7: {
        "topic_id": 7,
        "title": "AI 아우라 진단",
        "gender": "female",
        "framing": (
            "photographed from 1.2 meters directly across a dining table from the date's first-person eye-level perspective on iPhone 15 Pro, "
            "perfectly frontal portrait view looking directly into the camera lens with warm engaging eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and shoulders, "
            "candid medium shot showing chest, shoulders, and cafe table clearly, "
            "f/8 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible real pores and hair strands"
        ),
        "char_desc": (
            "a mesmerizingly attractive 25-year-old Korean it-girl, top 0.1% captivating feline fox-like eyes with subtle cat-eye eyeliner, "
            "trendy textured dark hair with subtle soft ash highlights, flawless glowing porcelain skin, "
            "wearing a chic form-fitting black ribbed knit top and delicate ear studs, looking directly into the camera lens"
        ),
        "bg_desc": (
            "trendy hip espresso bar and modern art gallery cafe in Seongsu-dong, mid-century modern aesthetic interior, "
            "framed contemporary art posters, warm designer lamp glow"
        ),
        "vibe": "상위 0.1% 아우라를 뿜어내는 매혹적인 트렌디 핫플 여우상 퀸"
    },
    8: {
        "topic_id": 8,
        "title": "500m 안심 레이더",
        "gender": "female",
        "framing": (
            "photographed from 1.2 meters directly across a dining table from the date's first-person eye-level perspective on iPhone 15 Pro, "
            "perfectly frontal portrait view looking directly into the camera lens with warm engaging eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and shoulders, "
            "candid medium shot showing chest, shoulders, and terrace table clearly, "
            "f/8 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible real pores and hair strands"
        ),
        "char_desc": (
            "an exceptionally stunning 25-year-old Korean fitness goddess visual, glowing radiant sun-kissed fair skin, "
            "bright vibrant eyes with a dazzling gentle smile, sleek high ponytail hairstyle, "
            "wearing a chic pastel lilac sporty athletic windbreaker, looking directly into the camera lens"
        ),
        "bg_desc": (
            "sunny outdoor terrace cafe near Seoul Forest park, lush green trees and park walking trail visible in background, "
            "bright refreshing afternoon natural daylight, pleasant outdoor atmosphere"
        ),
        "vibe": "서울숲에서 마주치면 고개 돌아가는 건강미 넘치는 산뜻한 여신 러너"
    }
}


def build_aura_shorts_t2i_character_prompt(
    topic_id: int = 1,
    custom_char_desc: Optional[str] = None,
    custom_bg_desc: Optional[str] = None
) -> Dict[str, str]:
    """
    Wan 2.1 T2I용 고화질 숏폼 인물 프롬프트 구성 (Wan 실전 줌인 편향 보정 골든 공식):
    1. 8대 주제별 맞춤형 카메라 거리 차등화 (1.4m ~ 4.0m)
    2. 머리 위 여백(Generous Headroom) 및 주변 환경 심도(Environmental Depth) 확보
    3. 스마트폰 파지 배제, 자연스러운 일상 제스처
    4. 🤐 [S2V 립싱크 헌법]: 치아 없는 입 다문 부드러운 미소 (lips completely closed together, zero teeth)
    5. 📐 [완벽한 정면 직립 헌법]: 고개 기울임(Head tilt) 제로, 수직 직립 정면 응시
    6. 얼빡샷(extreme close-up) 강력 차단 네거티브 탑재
    """
    norm_id = ((topic_id - 1) % len(AURA_8_TOPIC_SPECS)) + 1
    spec = AURA_8_TOPIC_SPECS.get(norm_id, AURA_8_TOPIC_SPECS[1])

    char = custom_char_desc or spec["char_desc"]
    bg = custom_bg_desc or spec["bg_desc"]
    framing = spec["framing"]

    # 🤐 S2V 립싱크 전용 정면 직립 + 입 다문 미소 헌법 (Wan 2.2 S2V 립싱크 궤적 극대화 & 고개 틀어짐 원천 차단)
    head_and_mouth_mandate = (
        "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, symmetrical upright head angle, looking straight and directly into the camera lens with level eye line, "
        "gently closed mouth, natural lips closed, looking at camera, mouth gently shut, lips naturally closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
        "charming gentle confident resting smile, looking directly into the camera lens with warm authentic eye contact ready to speak. "
    )

    # 🖐️ 포즈: 스마트폰 파지 배제, 편안하고 자연스러운 제스처 (고개는 틀지 않고 똑바로)
    if norm_id == 8:
        natural_pose = (
            "standing or walking naturally along the park trail in an upright athletic posture, head held straight, "
            "hands resting naturally at sides or in jacket pockets, NO smartphone held in hands, athletic natural posture. "
        )
    else:
        natural_pose = (
            "seated comfortably in an upright conversational posture with arms resting naturally on table or chair, "
            "hands resting naturally, NO smartphone held in hands, natural effortless human posture. "
        )

    # 긍정 프롬프트 최종 조립 (100% 정면 직립 POV + f/8 딥 팬포커스 무필터 실사 규격)
    positive = (
        f"masterpiece, best quality, ultra-photorealistic portrait, authentic candid snapshot shot on iPhone 15 Pro, casual everyday mobile phone photo taken across a table by a friend, "
        f"{framing} of {char}. "
        f"sitting in {bg}. "
        f"{natural_pose}"
        f"{head_and_mouth_mandate}"
        f"Raw unedited authentic iPhone 15 Pro 48MP mobile camera capture, realistic human skin texture with visible real pores and authentic fine details, "
        f"Apple iPhone 15 Pro Smart HDR photo, authentic mobile camera sensor capture, pristine optical sharpness, rich deep blacks, high micro-contrast, crisp clean highlights, punchy vivid clarity, NO beauty filter, zero skin smoothing, "
        f"f/8 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, clear background in focus."
    )

    # 주제별 특화 네거티브 차단
    topic_specific_neg = ""
    if norm_id == 1:
        topic_specific_neg = (
            "man, male, man's back, back of head, back of shoulder, man's shoulder, suit jacket in foreground, over-the-shoulder, 2 people, two people, second person, obstructed foreground, "
            "cleavage, deep neckline, exposed chest, bustier, low cut, exposed collarbone, bare shoulders, revealing clothes, nightlife, hostess, "
        )
    elif norm_id == 2:
        topic_specific_neg = (
            "doll, doll face, porcelain skin, plastic skin, airbrushed skin, beauty filter, skin smoothing, soft skin, glowing skin, dreamy glow, "
            "blurry background, bokeh, bokeh blur, shallow depth of field, out of focus background, hazy, smeared texture, low contrast, "
        )

    # 부정 프롬프트 (고개 기울임, 갸웃거림, 스마트폰 파지, 열린 입, 치아 노출, 3D CGI, 렌즈 블러 원천 차단)
    negative = (
        f"{topic_specific_neg}"
        "tilted head, head tilt, cocked head, head tilted to the side, crooked head, tilted neck, asymmetric head angle, off-axis head posture, slanted head, "
        "holding phone, phone in hand, smartphone facing camera, electronic device in hand, "
        "open mouth, parted lips, slightly open mouth, half-open mouth, open lips, visible teeth, showing teeth, teeth, smiling with teeth, grinning, laughing, "
        "distant shot, far away, full body shot, cowboy shot, tiny face, subject far in distance, "
        "deformed fingers, extra digits, missing fingers, bad hands, mutated hands, "
        "cartoon, 3d render, anime, plastic skin, doll, dull, dark, lowres, text, watermark, "
        "blurry, lens blur, out of focus, soft focus, bokeh blur, depth of field blur, hazy, dreamy glow, overexposed, airbrushed, beauty filter, skin smoothing"
    )

    return {"positive": positive, "negative": negative}
