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
            "photographed from 1.6 meters directly across a dining table from the date's first-person eye-level perspective on iPhone 15 Pro, "
            "solo 1person female, perfectly centered in the middle of frame, perfectly frontal portrait view looking directly into the camera lens with warm engaging eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and graceful shoulders, "
            "gently closed mouth, natural lips closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "candid medium cowboy shot showing chest, waist, and dark wooden dining table clearly, generous headroom above, "
            "f/8 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible real pores and hair strands"
        ),
        "char_desc": (
            "a beautiful 28-year-old Korean woman, perfect 8-head-high golden ratio model proportions, delicate small petite head and face, slender elegant long neck, calm low ponytail hairstyle, clear fair skin, "
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
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and graceful shoulders, "
            "gently closed mouth, natural lips closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "candid cowboy medium shot showing chest, waist, and warm wooden furniture clearly, generous headroom above, "
            "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, completely clear background bookshelves and plants in sharp crisp focus, visible real pores and individual hair strands"
        ),
        "char_desc": (
            "an exceptionally gorgeous 24-year-old Japanese young woman (Nanami), perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck, authentic real human model visual, "
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
            "photographed from 1.8 meters away from the date's first-person eye-level perspective on Apple iPhone 15 Pro, "
            "solo 1person female, standing gracefully by the glass railing of an upscale rooftop terrace, perfectly centered in the middle of frame, "
            "perfectly frontal portrait view looking directly into the camera lens with deeply captivating magnetic eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and graceful collarbones, "
            "gently closed mouth, natural full lips closed together with subtle alluring smile, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "elegantly holding a delicate crystal wine glass filled with deep red wine comfortably at waist height in one hand, wine glass held strictly at lower waist level far below the chest and mouth, "
            "candid medium cowboy standing shot showing waist, chest, shoulders, and elegant posture clearly, generous headroom above, "
            "f/8 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, visible real skin texture, fine pores and silky hair strands"
        ),
        "char_desc": (
            "an exceptionally gorgeous glamorous 26-year-old Korean woman standing with effortless confidence and poise, perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck, breathtakingly stunning high-society VIP beauty, "
            "voluminous natural dark silky wavy hair falling gracefully over her bare shoulders, seductive feline cat-like hazel eyes with subtle smoky eyeliner, "
            "flawless luminous glass skin with soft natural cheek blush, sharp high cheekbones and sculpted jawline, "
            "wearing an ultra-luxurious glamorous evening party dress, a chic upscale rooftop lounge cocktail outfit, sophisticated high-society date-night style, "
            "captivating sultry romantic charisma, unforgettable date-night VIP goddess aesthetic"
        ),
        "bg_desc": (
            "romantic midnight night view in Seoul, ultra-luxury high-end hotel rooftop sky lounge and open-air champagne bar in Gangnam, "
            "standing beside modern glass balustrade overlooking breathtaking panoramic sparkling glittering Seoul city night skyline and skyscraper lights against dark midnight blue sky, "
            "soft warm ambient architectural uplighting, glowing warm golden patio mood lamps creating dramatic rich depth, bokeh, and cinematic evening intimacy"
        ),
        "vibe": "밤의 특급호텔 루프탑 테라스에서 서울 야경을 배경으로 와인잔을 들고 서서 상대를 유혹하듯 마주하는 치명적인 섹시 고혹미 VIP 여신"
    },
    4: {
        "topic_id": 4,
        "title": "청담동 화보 보정",
        "gender": "female",
        "framing": (
            "photographed from 2.5 meters away from the photographer's direct eye-level perspective inside a luxury Cheongdam studio on iPhone 15 Pro, "
            "solo 1person female, perfectly centered in frame, medium chest-up seated photoshoot portrait, "
            "seated gracefully in the single designer white lounge armchair with the chair's curved backrest and armrests framing her naturally, "
            "eye-level strictly anchored at the upper 35% golden ratio line of the frame, "
            "tight balanced 15% headroom margin above head, "
            "perfectly frontal portrait view looking directly into the camera lens with captivating gentle eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, slender elegant long neck, collarbone and graceful shoulders visible, "
            "gently closed mouth, natural lips closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "chest and shoulders filling 65% of the frame with high aesthetic elegance, "
            "f/8 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, crisp high micro-contrast, visible real pores and individual hair strands"
        ),
        "char_desc": (
            "a breathtakingly stunning 23-year-old Korean young woman, perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck and collarbone, pure legendary first-love visual aesthetic, "
            "flowing natural dark silky wavy hair, immaculate luminous glass skin, captivating innocent eyes, delicate facial symmetry, "
            "wearing an elegant soft knit cardigan layered over a clean camisole, stylish feminine studio photoshoot attire, refined modern aesthetic fashion, looking directly into the camera lens"
        ),
        "bg_desc": (
            "high-end luxury photography studio in Cheongdam, modern curved architectural round arch alcove wall in warm peach-beige tone clearly visible behind her, "
            "modern curved studio architecture, tack sharp f/8 focus"
        ),
        "vibe": "청담동 최고급 스튜디오의 아치형 백월과 화이트 라운지 체어에 앉아 상단 35% 시선으로 압도적 청순 첫사랑 미모를 뽐내는 정석 화보"
    },
    5: {
        "topic_id": 5,
        "title": "가치관 밸런스 매칭",
        "gender": "female",
        "framing": (
            "photographed from 1.6 meters directly across a brunch table from the date's first-person eye-level perspective on iPhone 15 Pro, "
            "solo 1person female, perfectly centered in the middle of frame, perfectly frontal portrait view looking directly into the camera lens with warm engaging eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and graceful shoulders, "
            "gently closed mouth, natural lips closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "candid medium cowboy shot showing chest, waist, and brunch table clearly, generous headroom above, "
            "f/8 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible real pores and hair strands"
        ),
        "char_desc": (
            "an adorably gorgeous 21-year-old Korean college campus goddess, perfect 8-head-high golden ratio model proportions, delicate small petite head and face, slender elegant neck and collarbone, idol visual with bubbly charismatic charm, "
            "fresh glowing dewy skin, youthful bright expressive eyes, neat loose half-updo hairstyle, "
            "wearing a stylish relaxed button-down shirt, trendy casual boyfriend-fit cafe attire, lovely college campus fashion, looking directly into the camera lens"
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
            "photographed from 1.8 meters directly across a study table from the date's first-person eye-level perspective on iPhone 15 Pro, "
            "solo 1person male, perfectly centered in the middle of frame, perfectly frontal portrait view looking directly into the camera lens with warm engaging eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and broad athletic shoulders, "
            "gently closed mouth, natural lips closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "candid medium cowboy shot showing chest, waist, and study table clearly, generous headroom above, "
            "f/8 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible real pores and hair strands"
        ),
        "char_desc": (
            "a breathtakingly handsome 27-year-old Korean male lead actor visual, perfect 8-head-high golden ratio male model proportions, small masculine refined head and face size, defined jawline and slender athletic neck, top-tier romantic K-drama male lead aesthetic, "
            "clean stylish dandy haircut, immaculate smooth skin, kind yet deeply charismatic romantic eyes, "
            "wearing a tailored neat crewneck knit sweater layered over a crisp collared shirt, modern dandy boyfriend look, smart intellectual fashion, looking directly into the camera lens"
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
            "photographed from 1.6 meters directly across a cafe table from the date's first-person eye-level perspective on iPhone 15 Pro, "
            "solo 1person female, perfectly centered in the middle of frame, perfectly frontal portrait view looking directly into the camera lens with warm engaging eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and graceful collarbone, "
            "gently closed mouth, natural lips closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "candid medium cowboy shot showing chest, waist, and cafe table clearly, generous headroom above, "
            "f/8 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible real pores and hair strands"
        ),
        "char_desc": (
            "a mesmerizingly attractive 25-year-old Korean it-girl, perfect 8-head-high golden ratio model proportions, delicate small petite head and sculpted face, slender elegant neck, top 0.1% captivating feline fox-like eyes with subtle cat-eye eyeliner, "
            "trendy textured dark hair with subtle soft ash highlights, flawless glowing porcelain skin, "
            "wearing a chic form-fitting ribbed knit top, trendy hip Seongsu cafe fashion, alluring stylish influencer aesthetic, looking directly into the camera lens"
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
            "photographed from 2.0 meters directly across a terrace table from the date's first-person eye-level perspective on iPhone 15 Pro, "
            "solo 1person female, perfectly centered in the middle of frame, perfectly frontal portrait view looking directly into the camera lens with warm engaging eye contact, "
            "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and athletic posture, "
            "gently closed mouth, natural lips closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "candid medium cowboy shot showing waist, chest, and terrace table clearly, generous headroom above, "
            "f/8 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible real pores and hair strands"
        ),
        "char_desc": (
            "an exceptionally stunning 25-year-old Korean fitness goddess visual, perfect 8-head-high golden ratio athletic model proportions, delicate small petite head and face, slender toned neck and shoulders, glowing radiant sun-kissed fair skin, "
            "bright vibrant eyes with a dazzling gentle smile, sleek high ponytail hairstyle, "
            "wearing a chic sporty athletic windbreaker, stylish outdoor activewear, refreshing fitness runner fashion, looking directly into the camera lens"
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

    # 📏 [대표님 특명: 8등신 황금비율 & 소두 모델 비율 헌법] (얼빡샷/대두 현상 원천 영구 박멸)
    body_proportion_mandate = (
        "perfect 8-head-high body proportions, golden ratio 1:8 head-to-body proportion, "
        "delicate small petite head and face size, slender elegant long neck, graceful slender collarbone, "
        "well-proportioned slender model physique, graceful shoulders, slender waist, "
        "tall slender high-fashion model silhouette, balanced 20% headroom margin above head, "
        "well-balanced human anatomy with refined small head proportion. "
    )

    # 🖐️ 포즈: 주제별 맞춤 스탠딩/착석 구분 (스마트폰 파지 배제, 자연스러운 제스처)
    if norm_id == 3:
        natural_pose = (
            "standing gracefully with an elegant tall posture by the rooftop glass railing, perfectly upright model silhouette, "
            "holding a delicate crystal wine glass comfortably at lower waist level in one hand, other arm resting naturally, "
            "NO smartphone held in hands, poised confident high-society VIP posture. "
        )
        environment_action = f"standing on {bg}. "
    elif norm_id == 4:
        natural_pose = (
            "seated comfortably and gracefully inside the single designer white lounge armchair with an elegant upright posture, "
            "arms resting naturally on the armchair, cardigan layered softly, NO smartphone held in hands, professional editorial model photoshoot posture. "
        )
        environment_action = f"seated inside the designer armchair with {bg}. "
    elif norm_id == 8:
        natural_pose = (
            "standing or walking naturally along the park trail in an upright athletic posture, head held straight, "
            "hands resting naturally at sides or in jacket pockets, NO smartphone held in hands, athletic natural posture. "
        )
        environment_action = f"walking along {bg}. "
    else:
        natural_pose = (
            "seated comfortably in an upright conversational posture with arms resting naturally on table or chair, "
            "hands resting naturally, NO smartphone held in hands, natural effortless human posture. "
        )
        environment_action = f"sitting in {bg}. "

    # 긍정 프롬프트 최종 조립 (100% 정면 직립 POV + 8등신 소두 모델 비율 + f/8 딥 팬포커스 무필터 실사 규격)
    positive = (
        f"masterpiece, best quality, ultra-photorealistic portrait, authentic candid snapshot shot on iPhone 15 Pro, "
        f"{framing} of {char}. "
        f"{environment_action}"
        f"{natural_pose}"
        f"{body_proportion_mandate}"
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
    elif norm_id == 4:
        topic_specific_neg = (
            "strobe, softbox, studio lighting, beauty filter, airbrushed skin, plastic skin, porcelain skin, skin smoothing, glamour glow, soft glow, creamy skin, "
            "curtain, sheer curtain, window, sunlight streaming through, outdoor, cafe, dining table, brunch table, "
            "backlight, backlighting, optical halation, lens flare, hazy glow, dreamy glow, blown out background, washed out, "
        )

    # 부정 프롬프트 (대두, 얼빡샷, 하단 쏠림, 카우보이샷, 과도한 헤드룸, 고개 기울임, 갸웃거림, 스마트폰 파지, 열린 입, 치아 노출, 3D CGI, 렌즈 블러 원천 차단)
    negative = (
        f"{topic_specific_neg}"
        "cowboy shot, thighs, knees, full body, standing, excessive headroom, empty top half, giant empty ceiling, subject placed too low, character sinking to bottom, bottom heavy framing, tiny face at bottom, "
        "big head, large head, oversized head, bobblehead, broad face, wide jaw, chubby cheeks, fat face, "
        "short thick neck, swollen neck, disproportionate body ratio, giant head, macro face shot, tight bust shot, passport photo crop, "
        "tilted head, head tilt, cocked head, head tilted to the side, crooked head, tilted neck, asymmetric head angle, off-axis head posture, slanted head, "
        "holding phone, phone in hand, smartphone facing camera, electronic device in hand, "
        "open mouth, parted lips, slightly open mouth, half-open mouth, open lips, visible teeth, showing teeth, teeth, smiling with teeth, grinning, laughing, "
        "distant shot, far away, microscopic figure, tiny face, subject far in distance, head cut off, cropped top of head, "
        "deformed fingers, extra digits, missing fingers, bad hands, mutated hands, "
        "cartoon, 3d render, anime, plastic skin, doll, dull, dark, lowres, text, watermark, "
        "blurry, lens blur, out of focus, soft focus, bokeh blur, depth of field blur, hazy, dreamy glow, overexposed, airbrushed, beauty filter, skin smoothing"
    )

    return {"positive": positive, "negative": negative}
