# -*- coding: utf-8 -*-
"""
AuraCardnewsScenarioDirector - 💖 [Aura 데이팅 8대 킬러 주제 전용 5장 카드뉴스 시나리오 디렉터]
=============================================================================================
• 원칙:
  1. 카드뉴스는 첫 번째 카드가 가장 중요 (시선 강탈 킬러 후킹 표지)
  2. 5장 완결 기승전결 구조 (표지 ➔ 공감 ➔ 실전팁 ➔ 앱기능 ➔ 찬반논쟁 & 검색 CTA)
  3. 1080x1350 규격 최적화 헤드라인, 서브타이틀, 3줄 불릿, 배지, CTA 매핑
  4. 공식 검색어: '아우라AI데이팅' (붙여쓰기 철칙) / 공식 URL: https://aura-ai-dating.vercel.app/
"""

import copy
import logging
from typing import Dict, Any, List, Optional
from .aura_cardnews_fashion_presets import get_fashion_preset, get_all_presets

logger = logging.getLogger("AuraCardnewsScenarioDirector")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Aura 8대 주제별 5장 골든 카드뉴스 시나리오 DB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AURA_8_CARDNEWS_SCENARIOS: Dict[int, Dict[str, Any]] = {
    1: {
        "topic_id": 1,
        "theme_code": "escape_call",
        "theme_name": "소개팅 긴급 탈출 전화",
        "official_keyword": "아우라AI데이팅",
        "slides": [
            {
                "page": 1,
                "badge": "🔥 2030 소개팅 필독",
                "title": "소개팅 나갔는데 분위기 싸할 때 1초 만에 탈출하는 법",
                "subtitle": "사진이랑 너무 다르거나 불편한 자리, 억지로 버티지 마세요",
                "bullets": [
                    "소개팅 최악의 순간 1위: 실물 괴리 & 무례한 태도",
                    "눈치 보며 2차까지 끌려가지 않는 합법적 탈출법",
                    "상대방 기분 안 상하게 매너 탈출하는 비밀 공개"
                ],
                "cta_button": "👉 옆으로 넘겨서 탈출 비법 보기 (1/5) >",
                "image_prompt": (
                    "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
                    "cinematic over-the-shoulder shot (OTS) from directly behind a Korean man's back and dark navy suit jacket shoulder in the foreground, "
                    "the back of the man's head and right shoulder are softly visible in the lower foreground corner looking towards his date across the table, "
                    "seated directly across an antique dark wooden dining table is a breathtakingly beautiful 28-year-old Korean office woman, "
                    "she is seated upright looking directly across the table at him and the camera with warm authentic eye contact, "
                    "she has a subtle gentle polite smile, charming restrained smile with lips naturally closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
                    "perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck, graceful shoulders, "
                    "calm low ponytail hairstyle, clear fair skin with realistic fine skin pores, refined subtle daytime makeup, "
                    "wearing stylish sophisticated civilian dating clothes, an elegant chic modern dinner outfit with light cream knit and tailored jacket, "
                    "on the dark wooden dining table between them are delicate wine glasses, neat cutlery, and folded linen napkins in tack sharp focus, "
                    "moody upscale evening bistro and wine restaurant in Cheongdam, soft warm pin-spot table lighting casting natural 3D facial depth, "
                    "Apple iPhone 15 Pro Smart HDR photo, f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, completely clear background in tack sharp crisp focus."
                ),
                "negative_prompt": (
                    "man's face, facing camera man, front view man, two women, "
                    "open mouth, parted lips, visible teeth, showing teeth, grinning, laughing, wide smile, angry, frowning, grimacing, "
                    "cleavage, deep neckline, exposed chest, bustier, low cut, exposed collarbone, bare shoulders, revealing clothes, nightlife, hostess, "
                    "holding phone, phone in hand, smartphone facing camera, electronic device, "
                    "doll, doll face, porcelain skin, plastic skin, airbrushed skin, beauty filter, skin smoothing, "
                    "blurry, lens blur, out of focus, bokeh blur, shallow depth of field, deformed hands, extra fingers, "
                    "cartoon, anime, 3d render, cgi, illustration, drawing, watermark, text"
                )
            },
            {
                "page": 2,
                "badge": "현실 공감",
                "title": "어색한 자리 억지로 버티면 양쪽 다 손해입니다",
                "subtitle": "마음에도 없는 밥값 내고 주말 시간까지 낭비하셨나요?",
                "bullets": [
                    "거절 멘트 치기엔 너무 어색하고 미안한 순간",
                    "화장실에서 친구한테 '전화 좀 해줘' 카톡 보낸 경험",
                    "갑작스러운 핑계는 티가 나서 서로 민망해집니다"
                ],
                "cta_button": "스마트한 해결책 보기 >",
                "image_prompt": (
                    "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
                    "solo 1person female, the exact same gorgeous 28-year-old Korean office woman from slide 1, "
                    "perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck, calm low ponytail hairstyle, clear fair skin with realistic fine skin pores, refined subtle makeup, "
                    "wearing the exact same stylish sophisticated civilian dating clothes, an elegant chic modern dinner outfit with light cream knit and tailored jacket, "
                    "standing inside an ultra-luxurious 5-star hotel powder room and restroom, grand Italian marble vanity counter, elegant warm vanity mirror lighting with soft ambient golden glow in tack sharp f/11 focus, "
                    "she is holding her sleek smartphone in both hands at chest level, looking down intently at the glowing smartphone screen with a troubled, slightly anxious and frustrated facial expression, lips gently pressed together in serious thought, frantically trying to text a friend for an escape rescue call from an awkward blind date, "
                    "candid medium cowboy portrait shot showing upper body, cream jacket, hands holding smartphone, and luxury marble restroom interior, generous headroom above, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, Apple iPhone 15 Pro Smart HDR photo."
                ),
                "negative_prompt": (
                    "man, male, two people, crowd, open mouth, parted lips, visible teeth, showing teeth, laughing, smiling, happy, grinning, "
                    "cleavage, deep neckline, exposed chest, bustier, low cut, exposed collarbone, bare shoulders, revealing clothes, nightlife, hostess, "
                    "doll, doll face, porcelain skin, plastic skin, airbrushed skin, beauty filter, skin smoothing, "
                    "blurry, lens blur, out of focus, bokeh blur, shallow depth of field, deformed hands, extra fingers, missing fingers, bad fingers, "
                    "cartoon, anime, 3d render, cgi, illustration, drawing, watermark, text"
                )
            },
            {
                "page": 3,
                "badge": "매너 탈출 꿀팁",
                "title": "누구도 반박할 수 없는 '긴급 업무 호출' 명분",
                "subtitle": "회사 팀장님의 긴급 업무 전화는 완벽한 탈출 명분이 됩니다",
                "bullets": [
                    "개인 사정보다 공적인 업무 호출이 10배 자연스럽습니다",
                    "정중하게 사과하고 깔끔하게 1차에서 마무리 가능",
                    "상대방의 자존심도 지켜주는 가장 세련된 매너"
                ],
                "cta_button": "Aura 전용 탈출 기능 >",
                "image_prompt": (
                    "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
                    "solo 1person female, the exact same gorgeous 28-year-old Korean office woman from slide 1 and slide 2, "
                    "perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck, calm low ponytail hairstyle, clear fair skin with realistic fine skin pores, refined subtle makeup, "
                    "wearing the exact same stylish sophisticated civilian dating clothes, an elegant chic modern dinner outfit with light cream knit and tailored jacket, chic trousers, "
                    "photographed from 5.0 meters distance in a wide environmental full-body shot, wide full length shot showing the subject from head to toe with generous headroom above, "
                    "standing outside the grand entrance canopy driveway of an ultra-luxurious 5-star hotel in Seoul at evening, magnificent modern hotel architecture with glowing warm golden entrance canopy lights and glass revolving doors in the background in tack sharp f/11 focus, "
                    "she is standing gracefully with an upright tall model posture, looking towards the camera with a subtle gentle restrained smile, a charming calm poised smile with lips naturally closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, elegant quiet relief and satisfaction after politely escaping an awkward blind date, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, pristine optical clarity, Apple iPhone 15 Pro Smart HDR photo."
                ),
                "negative_prompt": (
                    "open mouth, parted lips, visible teeth, showing teeth, laughing, wide grin, laughing hysterically, crazy smile, grinning, laughing wildly, laughing eyes, "
                    "close up, bust shot, tight shot, macro, cropped head, cropped feet, 1 meter distance, 2 meters distance, headshot, "
                    "man, male, two people, crowd, frown, sad, crying, angry, troubled, "
                    "cleavage, deep neckline, exposed chest, bustier, low cut, exposed collarbone, bare shoulders, revealing clothes, nightlife, hostess, "
                    "doll, doll face, porcelain skin, plastic skin, airbrushed skin, beauty filter, skin smoothing, "
                    "blurry, lens blur, out of focus, bokeh blur, shallow depth of field, deformed hands, extra fingers, missing fingers, bad fingers, "
                    "cartoon, anime, 3d render, cgi, illustration, drawing, watermark, text"
                )

            },
            {
                "page": 4,
                "badge": "실전 앱 안심 구동",
                "title": "버튼 하나로 진짜 팀장님 음성 전화 & 대본 자동 표출",
                "subtitle": "Aura 앱의 '긴급 탈출 전화'로 완벽한 타이밍에 1차 매너 귀가",
                "bullets": [
                    "소개팅 시작 전 30분 뒤 긴급 자동 수신 예약 ON",
                    "실제 스마트폰 벨소리와 함께 팀장님 음성 통화 연결",
                    "화면에 표출되는 자연스러운 통화 대본 보고 읽으면 끝!"
                ],
                "cta_button": "댓글 찬반 투표 참여 >",
                "asset_image": "brands/aura/assets/aura_escape_call_dialog.png",
                "use_direct_asset": True
            },
            {
                "page": 5,
                "badge": "찬반 토론 & 회원가입 CTA",
                "title": "소개팅 긴급 탈출 전화, 센스다 vs 너무하다?",
                "subtitle": "불안한 소개팅은 이제 그만! 안심하고 만나는 Aura 데이팅",
                "bullets": [
                    "사진 1장으로 1초 만에 프로필 등록 & 무료 가입",
                    "50:50 황금 성비율 • 100% 실명 인증된 2030 라운지",
                    "👉 프로필 링크에서 3초 만에 내 이상형/성향 확인!"
                ],
                "cta_button": "👉 프로필 링크에서 3초 이상형 확인 >"
            }
        ]
    },
    2: {
        "topic_id": 2,
        "theme_code": "realtime_subtitles",
        "theme_name": "실시간 AI 자막 통화",
        "official_keyword": "아우라AI데이팅",
        "slides": [
            {
                "page": 1,
                "badge": "🔥 글로벌 썸 치트키",
                "title": "외국어 1도 몰라도 일본 여사친과 3시간 통화한 비결",
                "subtitle": "언어 장벽 제로, 넷플릭스처럼 실시간 번역 자막이 뜹니다",
                "bullets": [
                    "외국인 친구 사귀고 싶은데 회화가 막막하셨나요?",
                    "내가 한국어로 말하면 상대에겐 일본어 자막 자동 생성",
                    "글로벌 친구 매칭부터 밤샘 통화까지 1초 만에 시작"
                ],
                "cta_button": "👉 옆으로 넘겨서 통역 비결 보기 (1/5) >",
                "image_prompt": (
                    "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
                    "solo 1person female, an exceptionally gorgeous 24-year-old Japanese young woman (Nanami), "
                    "perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck, authentic real human model visual, "
                    "authentic natural human skin with visible fine pores and realistic delicate skin texture, strictly no airbrushing, "
                    "charming expressive doe-like hazel-brown eyes, delicate see-through bangs, neat dark brown shoulder-length hair, "
                    "she has a subtle gentle polite smile, charming restrained smile with lips naturally closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
                    "wearing clean stylish civilian casual clothes, a neat comfortable soft knit daily outfit, "
                    "she is holding her sleek smartphone in both hands, looking down affectionately at the glowing smartphone screen in a warm video call and messaging moment, "
                    "sitting in a sunlit trendy glasshouse boutique cafe in Seongsu-dong with clean polished white marble table, warm soft natural sunlight streaming through floor-to-ceiling glass windows, "
                    "warm directional room ambient lighting creating natural depth and rich realistic shadows, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, Apple iPhone 15 Pro Smart HDR photo."
                ),
                "negative_prompt": (
                    "open mouth, parted lips, visible teeth, showing teeth, laughing, grinning, smiling wide, "
                    "two people, man, male, crowd, "
                    "cleavage, deep neckline, exposed chest, bustier, low cut, exposed collarbone, bare shoulders, revealing clothes, nightlife, hostess, "
                    "doll, doll face, porcelain skin, plastic skin, airbrushed skin, beauty filter, skin smoothing, "
                    "blurry, lens blur, out of focus, bokeh blur, shallow depth of field, deformed hands, extra fingers, missing fingers, bad fingers, "
                    "cartoon, anime, 3d render, cgi, illustration, drawing, watermark, text"
                )
            },
            {
                "page": 2,
                "badge": "현실 공감",
                "title": "파파고 복사 붙여넣기 대화는 이제 그만!",
                "subtitle": "말이 안 통해서 식은땀 나고 대화 끊기던 경험 있으신가요?",
                "bullets": [
                    "번역기 돌리느라 대화 흐름 뚝뚝 끊기던 민망한 순간",
                    "목소리는 듣고 싶은데 무슨 말인지 몰라 어색한 침묵",
                    "채팅창과 번역 앱을 번갈아 보며 멘붕 오던 현실"
                ],
                "cta_button": "Aura AI 통화 기능 >",
                "image_prompt": (
                    "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
                    "solo 1person female, the exact same gorgeous 24-year-old Japanese young woman (Nanami) from slide 1, "
                    "perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck, authentic real human model visual, "
                    "authentic natural human skin with visible fine pores and realistic delicate skin texture, strictly no airbrushing, "
                    "charming expressive doe-like hazel-brown eyes, delicate see-through bangs, neat dark brown shoulder-length hair, "
                    "wearing the exact same clean stylish civilian casual clothes, a neat comfortable white turtleneck knit sweater from slide 1, "
                    "she is holding her sleek smartphone steadily in both hands at chest level, looking down intently at the glowing smartphone screen in front of her chest with a troubled, slightly anxious and perplexed facial expression, cute delicate head tilt, lips naturally closed together in serious thought, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
                    "struggling to understand unfamiliar foreign Korean text on the glowing smartphone screen, feeling cute and awkward embarrassment, "
                    "pristine anatomically correct five-finger hands holding the phone edges naturally, completely clear realistic hands, "
                    "sitting in the exact same warm cozy Tokyo apartment living room from slide 1 with authentic dark oak wooden bookshelves filled with books, vibrant lush green indoor potted plants, "
                    "warm directional room ambient lighting creating natural depth and rich realistic shadows, "
                    "candid medium cowboy portrait shot showing upper body, white turtleneck sweater, both hands holding smartphone in front of chest, and living room background, generous headroom above, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, Apple iPhone 15 Pro Smart HDR photo."
                ),
                "negative_prompt": (
                    "phone near ear, phone on ear, phone to ear, holding phone to ear, calling to ear, phone touching head, phone touching ear, "
                    "deformed hands, distorted fingers, extra fingers, missing fingers, fused fingers, mutated hands, bad hands, bad fingers, poorly drawn hands, "
                    "open mouth, parted lips, visible teeth, showing teeth, laughing, grinning, smiling wide, smiling, "
                    "two people, man, male, crowd, "
                    "cleavage, deep neckline, exposed chest, bustier, low cut, exposed collarbone, bare shoulders, revealing clothes, nightlife, hostess, "
                    "doll, doll face, porcelain skin, plastic skin, airbrushed skin, beauty filter, skin smoothing, "
                    "blurry, lens blur, out of focus, bokeh blur, shallow depth of field, "
                    "cartoon, anime, 3d render, cgi, illustration, drawing, watermark, text"
                )
            },
            {
                "page": 3,
                "badge": "설레는 소통",
                "title": "목소리는 생생하게, 자막으로 100% 통하는 밤샘 토크!",
                "subtitle": "실시간 AI 자막으로 언어 장벽 없이 새벽까지 이어지는 티키타카",
                "bullets": [
                    "파파고 복붙 없이 실시간 양방향 자막으로 끊김 없는 대화",
                    "도쿄 현지 로컬 맛집부터 소소한 일상 꿀팁까지 공유",
                    "언어 장벽이 무너지자 시간 가는 줄 모르는 글로벌 썸"
                ],
                "cta_button": "Aura AI 실시간 자막 보기 (3/5) >",
                "image_prompt": (
                    "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
                    "solo 1person female, the exact same gorgeous 24-year-old Japanese young woman (Nanami) from slide 1 and slide 2, "
                    "perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck, authentic real human model visual, "
                    "authentic natural human skin with visible fine pores and realistic delicate skin texture, strictly no airbrushing, "
                    "charming expressive doe-like hazel-brown eyes crinkling warmly in genuine happiness, delicate see-through bangs, neat dark brown shoulder-length hair, "
                    "wearing the exact same clean stylish civilian casual clothes, a neat comfortable white turtleneck knit sweater from slide 1 and slide 2, "
                    "she is holding her sleek smartphone steadily in both hands in front of her chest, looking down intently at the glowing smartphone screen and laughing delightfully in pure joy, "
                    "she has a radiant, bright, cheerful and lovely warm smile, captivating genuine joyful smile, lips naturally parted showing natural white teeth in a pleasant friendly laugh, eyes filled with warmth and romantic excitement, "
                    "having an incredibly fun and heartwarming video call moment where communication flows effortlessly, "
                    "pristine anatomically correct five-finger hands holding the phone naturally, completely clear realistic hands, "
                    "sitting in the exact same warm cozy Tokyo apartment living room from slide 1 with authentic dark oak wooden bookshelves filled with books, vibrant lush green indoor potted plants, "
                    "warm directional room ambient lighting creating natural depth and rich realistic shadows, "
                    "candid medium cowboy portrait shot showing upper body, white turtleneck sweater, both hands holding smartphone, and living room background, generous headroom above, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, Apple iPhone 15 Pro Smart HDR photo."
                ),
                "negative_prompt": (
                    "phone near ear, phone on ear, phone to ear, holding phone to ear, calling to ear, phone touching head, phone touching ear, "
                    "deformed hands, distorted fingers, extra fingers, missing fingers, fused fingers, mutated hands, bad hands, bad fingers, poorly drawn hands, "
                    "frown, angry, sad, crying, grimacing, disgusted, bored, "
                    "two people, man, male, crowd, "
                    "cleavage, deep neckline, exposed chest, bustier, low cut, exposed collarbone, bare shoulders, revealing clothes, nightlife, hostess, "
                    "doll, doll face, porcelain skin, plastic skin, airbrushed skin, beauty filter, skin smoothing, "
                    "blurry, lens blur, out of focus, bokeh blur, shallow depth of field, "
                    "cartoon, anime, 3d render, cgi, illustration, drawing, watermark, text"
                )
            },
            {
                "page": 4,
                "badge": "Aura 통역 엔진",
                "title": "화면 하단에 0.1초 만에 타이핑되는 AI 자막",
                "subtitle": "Aura 실시간 음성 인식(STT)과 번역 AI의 환상 시너지",
                "bullets": [
                    "영상 통화 중 화면 하단에 넷플릭스 스타일 자막 안착",
                    "발음이 서툴러도 AI가 문맥을 파악해 매끄럽게 번역",
                    "100% 본인 인증 완료된 안전한 글로벌 회원 매칭"
                ],
                "cta_button": "댓글 찬반 투표 참여 >",
                "asset_image": "brands/aura/assets/aura_subtitles_call_screen.png",
                "use_direct_asset": True
            },
            {
                "page": 5,
                "badge": "찬반 토론 & 회원가입 CTA",
                "title": "외국어 몰라도 실시간 AI 자막으로 글로벌 연애 가능? 찬성 vs 반대",
                "subtitle": "언어 장벽 없는 글로벌 썸! 안심하고 만나는 Aura 데이팅",
                "bullets": [
                    "사진 1장으로 1초 만에 프로필 등록 & 무료 가입",
                    "50:50 황금 성비율 • 글로벌 라운지 즉시 입장",
                    "👉 프로필 링크에서 3초 만에 내 이상형/성향 확인!"
                ],
                "cta_button": "👉 프로필 링크에서 3초 이상형 확인 >"
            }
        ]
    },
    3: {
        "topic_id": 3,
        "theme_code": "vip_gate_5050",
        "theme_name": "50:50 VIP 게이트",
        "official_keyword": "아우라AI데이팅",
        "slides": [
            {
                "page": 1,
                "badge": "🔥 소개팅 앱의 진실",
                "title": "소개팅 앱에 남자가 90%인 이유? 5:5 아니면 문 닫습니다",
                "subtitle": "유령회원과 남초 지옥에 질린 2030을 위한 VIP 정원제 라운지",
                "bullets": [
                    "대부분의 데이팅 앱은 남성 비율이 80~90%에 달합니다",
                    "과도한 경쟁과 유령회원에 지치셨던 분들 필독",
                    "남녀 성비 50:50이 유지될 때만 입장을 허용하는 공정 시스템"
                ],
                "cta_button": "👉 옆으로 넘겨서 성비의 진실 보기 (1/5) >",
                "image_prompt": (
                    "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
                    "photographed from 1.8 meters away from the date's first-person eye-level perspective on Apple iPhone 15 Pro, "
                    "solo 1person female, standing gracefully by the modern glass railing of an upscale rooftop terrace, perfectly centered in the middle of frame, "
                    "perfectly frontal portrait view looking directly into the camera lens with deeply captivating magnetic eye contact, "
                    "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, perfectly aligned neck and graceful collarbones, "
                    "gently closed mouth, natural full lips closed together with subtle alluring smile, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
                    "an exceptionally gorgeous glamorous 26-year-old Korean woman standing with effortless confidence and poise, "
                    "perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck, breathtakingly stunning high-society VIP beauty, "
                    "voluminous natural dark silky wavy hair falling gracefully over her shoulders, seductive feline cat-like hazel eyes with subtle smoky eyeliner, "
                    "flawless luminous glass skin with soft natural cheek blush, sharp high cheekbones and sculpted jawline, "
                    "wearing an ultra-luxurious glamorous evening party dress, a chic upscale rooftop lounge cocktail outfit, sophisticated high-society date-night style, "
                    "elegantly holding a delicate crystal wine glass filled with deep red wine comfortably at waist height in one hand, wine glass held strictly at lower waist level far below the chest and mouth, "
                    "candid medium cowboy standing shot showing waist, chest, shoulders, and elegant posture clearly, generous headroom above, "
                    "romantic midnight night view in Seoul, ultra-luxury high-end hotel rooftop sky lounge and open-air champagne bar in Gangnam, "
                    "standing beside modern glass balustrade overlooking breathtaking panoramic sparkling glittering Seoul city night skyline and skyscraper lights against dark midnight blue sky in tack sharp f/11 focus, "
                    "soft warm ambient architectural uplighting, glowing warm golden patio mood lamps creating dramatic rich depth, crisp details, and cinematic evening intimacy, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, Apple iPhone 15 Pro Smart HDR photo."
                ),
                "negative_prompt": (
                    "open mouth, parted lips, visible teeth, showing teeth, laughing, wide grin, smiling wide, "
                    "two people, man, male, crowd, "
                    "cleavage, deep neckline, exposed chest, bustier, low cut, exposed collarbone, bare shoulders, revealing clothes, nightlife, hostess, "
                    "doll, doll face, porcelain skin, plastic skin, airbrushed skin, beauty filter, skin smoothing, "
                    "blurry, lens blur, out of focus, bokeh blur, shallow depth of field, deformed hands, extra fingers, missing fingers, bad fingers, "
                    "cartoon, anime, 3d render, cgi, illustration, drawing, watermark, text"
                )
            },
            {
                "page": 2,
                "badge": "Aura 훈남 회원 검증",
                "title": "50:50 정원제를 뚫고 들어온 훈남 회원들",
                "subtitle": "알바·유령회원 제로, 프로필과 매너가 검증된 진짜 남성 회원",
                "bullets": [
                    "대기열 뚫고 들어온 매력적인 2030 직장인 훈남 회원들",
                    "100% 본인 인증 및 엄격한 프로필 심사 통과 완료",
                    "남탕 피로감 없이 여성 회원들과의 높은 티키타카 매칭"
                ],
                "cta_button": "여성 회원 퀄리티 확인하기 (2/5) >",
                "asset_image": "brands/aura/assets/aura_male_profile_card_template.png",
                "use_direct_asset": True
            },
            {
                "page": 3,
                "badge": "Aura 여성 회원 검증",
                "title": "VIP 프리패스로 입장한 매력적인 여성 회원들",
                "subtitle": "남탕 앱 스트레스 없이 입장한 품격 있는 2030 여성 회원",
                "bullets": [
                    "유령회원·알바 0%, 진짜 만남을 기다리는 여성 회원들",
                    "와인바, 드라이브 등 가치관과 취향이 통하는 인연",
                    "50:50 황금 성비로 대기 없이 바로 시작되는 설레는 매칭"
                ],
                "cta_button": "50:50 정원제 시스템 보기 (3/5) >",
                "asset_image": "brands/aura/assets/aura_female_profile_card.png",
                "use_direct_asset": True
            },
            {
                "page": 4,
                "badge": "AURA Equilibrium",
                "title": "국내 최초 50:50 성비 보장 라운지",
                "subtitle": "남초 현상 제로, 남녀 50:50 완벽 균형 매칭 시스템",
                "bullets": [
                    "남녀 성비 50:50으로 엄격히 유지하는 최고급 프라이빗 라운지",
                    "여성 회원: 대기 없이 100% 무료 VIP 프리패스 즉시 입장",
                    "남성 회원: 성비 초과 시 VIP 대기열 순차 입장 관리"
                ],
                "cta_button": "댓글 찬반 투표 참여 >",
                "asset_image": "brands/aura/assets/aura_equilibrium_screen.png",
                "use_direct_asset": True
            },
            {
                "page": 5,
                "badge": "찬반 토론 & 검색 CTA",
                "title": "50:50 안 맞으면 입장 제한하는 정원제, 찬성 vs 반대?",
                "subtitle": "여러분의 솔직한 생각을 댓글로 남겨주세요! 👇",
                "bullets": [
                    "1번: 진성 회원만 매칭되니 무조건 찬성이다",
                    "2번: 기다려야 하니 불편하다 반대다",
                    "👉 프로필 링크에서 3초 만에 내 이상형/성향 확인!"
                ],
                "cta_button": "👉 프로필 링크에서 3초 이상형 확인 >"
            }
        ]
    },
    4: {
        "topic_id": 4,
        "theme_code": "cheongdam_photo",
        "theme_name": "청담동 화보 보정",
        "official_keyword": "아우라AI데이팅",
        "slides": [
            {
                "page": 1,
                "badge": "🔥 프로필 사진 치트키",
                "title": "30만원 스튜디오 안 가도 청담동 화보 만드는 법",
                "subtitle": "평범한 일상 폰카 1장으로 매칭률 5배 폭발시키는 AI 스튜디오",
                "bullets": [
                    "소개팅 앱 매칭의 80%는 첫 번째 프로필 사진에서 결정",
                    "비싼 헤어메이크업과 스튜디오 촬영 예약 고민 끝",
                    "Aura AI가 피부톤, 조명, 구도를 자연스럽게 화보급으로 변신"
                ],
                "cta_button": "👉 옆으로 넘겨서 화보 비결 보기 (1/5) >",
                "image_prompt": (
                    "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
                    "close-up bust shot portrait inside a luxury Cheongdam studio on iPhone 15 Pro, "
                    "solo 1person female, perfectly centered in frame, close-up portrait with face prominently filling upper frame, "
                    "seated gracefully in the single designer white lounge armchair with the chair's curved backrest framing her naturally, "
                    "eye-level strictly anchored high in frame, "
                    "perfectly frontal portrait view looking directly into the camera lens with captivating gentle eye contact, face clearly visible and prominent, "
                    "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, slender elegant long neck, collarbone and graceful shoulders visible, "
                    "gently closed mouth, natural lips closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
                    "an exceptionally gorgeous glamorous 25-year-old Korean young woman with a breathtakingly seductive feline cat-like facial aesthetic, "
                    "captivating alluring cat-like almond hazel eyes with subtle sharp winged eyeliner, sharp high cheekbones, delicate cute button nose, sculpted elegant jawline, "
                    "delicate small petite head and face size, slender elegant long neck, graceful collarbone, "
                    "flawless luminous glass skin with soft natural peach blush, realistic skin pores and authentic fine skin texture, "
                    "natural full lips gently closed together with a subtle alluring confident smile, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
                    "voluminous silky dark wavy hair falling gracefully over shoulders, "
                    "wearing stylish sophisticated civilian dating clothes, an elegant chic off-shoulder knit top, modern luxurious date-night fashion, looking directly into the camera lens, "
                    "high-end luxury photography studio in Cheongdam, modern curved architectural round arch alcove wall in warm peach-beige tone clearly visible behind her, "
                    "modern curved studio architecture, tack sharp f/11 focus, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, Apple iPhone 15 Pro Smart HDR photo."
                ),
                "negative_prompt": (
                    "distant shot, far away, wide shot, tiny face, face covered, face obscured, "
                    "open mouth, parted lips, visible teeth, showing teeth, laughing, wide grin, smiling wide, smiling, "
                    "two people, man, male, crowd, "
                    "cleavage, deep neckline, exposed chest, bustier, low cut, exposed collarbone, bare shoulders, revealing clothes, nightlife, hostess, "
                    "doll, doll face, porcelain skin, plastic skin, airbrushed skin, beauty filter, skin smoothing, "
                    "blurry, lens blur, out of focus, bokeh blur, shallow depth of field, deformed hands, extra fingers, missing fingers, bad fingers, "
                    "cartoon, anime, 3d render, cgi, illustration, drawing, watermark, text"
                )
            },
            {
                "page": 2,
                "badge": "사진 실패 사례",
                "title": "과한 포토샵 사기 사진은 첫 만남에서 100% 역효과!",
                "subtitle": "실물과 너무 다른 턱선 깎기나 외계인 보정은 금물",
                "bullets": [
                    "첫 만남에서 실물 괴리로 실망하고 애프터 실패하는 주원인",
                    "부자연스러운 스노우 필터 대신 은은한 스튜디오 조명이 핵심",
                    "내 본연의 매력을 극대화하는 자연스러운 보정이 필요"
                ],
                "cta_button": "Aura AI 화보 보정 >"
            },
            {
                "page": 3,
                "badge": "Aura AI 스튜디오",
                "title": "청담동 메이크업 & 조명 세팅을 AI로 그대로 재현",
                "subtitle": "잡티와 피부결은 정돈하고 입체적인 윤곽을 살려줍니다",
                "bullets": [
                    "인위적인 왜곡 없이 피부 결점만 자연스럽게 커버",
                    "자연광 & 고급 스튜디오 핀포인트 조명 효과 부여",
                    "이목구비 비율을 살린 8등신 황금비율 프로필 완성"
                ],
                "cta_button": "스타일링 적용 팁 >"
            },
            {
                "page": 4,
                "badge": "실전 스타일링 팁",
                "title": "계절별 룩북과 배경까지 분위기 여신/남신 완성",
                "subtitle": "어색한 방구석 셀카를 성수동 감성 테라스 스냅으로",
                "bullets": [
                    "옷차림과 배경을 모던하고 세련된 데이트 룩으로 교체",
                    "과하지 않고 자연스러운 분위기로 호감도 극대화",
                    "프로필 등록 즉시 '좋아요' 500% 급증 경험"
                ],
                "cta_button": "댓글 찬반 투표 참여 >"
            },
            {
                "page": 5,
                "badge": "찬반 토론 & 검색 CTA",
                "title": "소개팅 프로필 사진 AI 스튜디오 보정, 자기관리다 vs 사진 사기다?",
                "subtitle": "여러분의 솔직한 생각을 댓글로 남겨주세요! 👇",
                "bullets": [
                    "1번: 조명/피부결 정리 정도는 스마트한 자기관리다",
                    "2번: 실물과 조금이라도 다르면 사진 사기다",
                    "👉 프로필 링크에서 3초 만에 내 이상형/성향 확인!"
                ],
                "cta_button": "👉 프로필 링크에서 3초 이상형 확인 >"
            }
        ]
    },
    5: {
        "topic_id": 5,
        "theme_code": "value_balance",
        "theme_name": "연애 가치관 리밸런스",
        "official_keyword": "아우라AI데이팅",
        "slides": [
            {
                "page": 1,
                "badge": "🔥 2030 현실 연애관",
                "title": "첫 만남 더치페이? 연락 텀? 만나기 전에 싹 다 맞추는 법",
                "subtitle": "사귀고 나서 싸우지 말고, 가치관 딱 맞는 사람만 골라 만나세요",
                "bullets": [
                    "연애할 때 가장 많이 싸우는 1위: 연락 빈도 & 데이트 비용",
                    "첫 만남에서 돈 얘기 꺼내기 어색해서 눈치 보던 경험",
                    "만나기 전 12가지 가치관 일치율을 미리 확인하는 스마트 매칭"
                ],
                "cta_button": "👉 옆으로 넘겨서 가치관 매칭 보기 (1/5) >",
                "image_prompt": (
                    "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
                    "photographed from 1.6 meters directly across a brunch table from the date's first-person eye-level perspective on iPhone 15 Pro, "
                    "solo 1person female, perfectly centered in the middle of frame, perfectly frontal portrait view looking directly into the camera lens with enchanting authentic eye contact, "
                    "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, slender elegant long neck, collarbone and delicate bare shoulders visible, "
                    "gently closed mouth, natural lips closed together with a lovely sweet subtle smile, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
                    "an exceptionally gorgeous 21-year-old Korean campus goddess with breathtakingly enchanting feline cat-like facial features, "
                    "captivating alluring cat-like almond dark eyes with subtle sharp upturned winged eyeliner, "
                    "sharp high cheekbones, delicate cute petite nose, sculpted flawless V-line jawline, "
                    "radiant luminous porcelain glass skin with soft natural peach cheek glow, "
                    "neat sleek low bun hairstyle with subtle elegant side fringe framing her face perfectly, "
                    "wearing a chic clean minimalist white ribbed-knit sleeveless dress with a wide-strap square neckline, "
                    "fitted ribbed texture accentuating her graceful slender collarbone and delicate bare shoulders, elegant sophisticated summer brunch date attire, looking directly into the camera lens, "
                    "candid medium cowboy shot showing chest, waist, and brunch table clearly, generous headroom above, "
                    "cozy outdoor brunch cafe patio in Yeonnam-dong surrounded by abundant lush vibrant green leaves, rich lush tree canopy with deep green foliage filling the background in tack sharp f/11 focus, fresh refreshing garden terrace atmosphere, rustic wooden table with a takeout cup of iced latte with rich foam and cute brunch plates, pleasant natural daylight filtering through green leaves, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, visible real pores and individual hair strands, realistic skin subsurface scattering, Apple iPhone 15 Pro Smart HDR photo."
                ),
                "negative_prompt": (
                    "t-shirt, crew neck, short sleeves, sleeves, baggy clothes, casual cotton tee, round neck, "
                    "open mouth, parted lips, visible teeth, showing teeth, laughing, wide grin, smiling wide, smiling, "
                    "two people, man, male, crowd, "
                    "cleavage, deep neckline, exposed chest, bustier, low cut, revealing clothes, nightlife, hostess, "
                    "doll, doll face, porcelain skin, plastic skin, airbrushed skin, beauty filter, skin smoothing, "
                    "blurry, lens blur, out of focus, bokeh blur, shallow depth of field, deformed hands, extra fingers, missing fingers, bad fingers, "
                    "cartoon, anime, 3d render, cgi, illustration, drawing, watermark, text"
                )
            },
            {
                "page": 2,
                "badge": "연애 갈등의 원인",
                "title": "가치관 안 맞는 연애는 시간과 감정 낭비일 뿐!",
                "subtitle": "사소한 생활 습관과 금전 감각 차이가 결국 이별로 이어집니다",
                "bullets": [
                    "칼답 vs 여유로운 연락 텀, 연인 사이 최대의 스트레스",
                    "데이트 통장 찬성 vs 번갈아 내기, 민감한 소비 성향",
                    "처음부터 나와 결이 같은 사람을 찾는 것이 정답입니다"
                ],
                "cta_button": "Aura 가치관 진단 >"
            },
            {
                "page": 3,
                "badge": "Aura 12가지 가치관",
                "title": "12개 핵심 밸런스 게임으로 연애 성향 완벽 분석",
                "subtitle": "MBTI보다 정확한 실전 데이팅 가치관 매칭 알고리즘",
                "bullets": [
                    "연락 주기, 데이트 비용, 주말 데이트 성향 정밀 진단",
                    "상대방 프로필에서 가치관 일치율 % 즉시 확인",
                    "불필요한 갈등 없이 대화가 물 흐르듯 통하는 인연"
                ],
                "cta_button": "매칭 성공률 확인 >"
            },
            {
                "page": 4,
                "badge": "성공적인 연애의 비결",
                "title": "가치관 일치율 85% 이상만 추천되는 맞춤 라운지",
                "subtitle": "Aura AI가 선별해 주는 나와 찰떡궁합인 VIP 인연",
                "bullets": [
                    "취향과 대화 코드가 맞아 첫 만남부터 편안한 분위기",
                    "장기 연애 및 진지한 관계로 이어질 확률 4배 상승",
                    "2030 직장인을 위한 가장 똑똑한 가치관 데이팅"
                ],
                "cta_button": "댓글 찬반 투표 참여 >"
            },
            {
                "page": 5,
                "badge": "찬반 토론 & 검색 CTA",
                "title": "연락 빈도 & 데이트 비용 가치관, 얼굴보다 중요하다 vs 얼굴이 먼저다?",
                "subtitle": "여러분의 솔직한 생각을 댓글로 남겨주세요! 👇",
                "bullets": [
                    "1번: 오래 만나려면 가치관 일치가 무조건 1순위다",
                    "2번: 그래도 첫인상과 얼굴 호감이 먼저다",
                    "👉 프로필 링크에서 3초 만에 내 이상형/성향 확인!"
                ],
                "cta_button": "👉 프로필 링크에서 3초 이상형 확인 >"
            }
        ]
    },
    6: {
        "topic_id": 6,
        "theme_code": "smart_opener",
        "theme_name": "AI 첫대화 치트키",
        "official_keyword": "아우라AI데이팅",
        "slides": [
            {
                "page": 1,
                "badge": "🔥 카톡 첫대화 치트키",
                "title": "매칭됐는데 '안녕하세요' 보냈다가 읽씹당한 분들 필독",
                "subtitle": "답장률 99% 폭발시키는 상대 프로필 맞춤 AI 첫마디 치트키",
                "bullets": [
                    "소개팅 앱 매칭 후 가장 막막한 순간: 첫마디 뭐라 보낼까?",
                    "뻔한 인사말은 수많은 메시지 속에 묻혀 100% 씹힙니다",
                    "상대방 취향과 사진을 분석해 1초 만에 최적의 첫 멘트 추천"
                ],
                "cta_button": "👉 옆으로 넘겨서 치트키 보기 (1/5) >"
            },
            {
                "page": 2,
                "badge": "읽씹 부르는 망한 첫마디",
                "title": "'안녕하세요~ 주말 잘 보내세요'는 절대 금물!",
                "subtitle": "영혼 없는 복사 붙여넣기 멘트에 상대방은 피로감을 느낍니다",
                "bullets": [
                    "매력적인 상대는 하루에도 수십 개의 뻔한 인사를 받습니다",
                    "질문이 없거나 대답하기 애매한 단답형 인사는 탈락 1순위",
                    "상대의 호기심을 자극하고 대화 리듬을 여는 오프너가 필요"
                ],
                "cta_button": "Aura AI 첫마디 비서 >"
            },
            {
                "page": 3,
                "badge": "Aura AI 오프너",
                "title": "상대 프로필 속 '사소한 디테일'을 캐치하는 AI 분석",
                "subtitle": "강아지 사진, 여행지, 좋아하는 음악에서 자연스러운 질문 도출",
                "bullets": [
                    "사진 속 카페 위치나 반려견 견종을 센스 있게 언급",
                    "자연스러운 스몰토크로 어색함 없이 티키타카 시작",
                    "첫 메시지 답장 성공률 300% 이상 폭발적 증가"
                ],
                "cta_button": "실전 대화 팁 확인 >"
            },
            {
                "page": 4,
                "badge": "실전 티키타카 코칭",
                "title": "답장 속도와 말투에 맞춘 실시간 대화 서포트",
                "subtitle": "대화가 끊길 타이밍에 센스 있는 화제 전환 질문 제공",
                "bullets": [
                    "상대의 단답을 막아주는 감성 오픈 질문 추천",
                    "주말 데이트 약속까지 자연스럽게 이어지는 애프터 플로우",
                    "연애 초보도 센스쟁이로 만들어주는 AI 대화 비서"
                ],
                "cta_button": "댓글 찬반 투표 참여 >"
            },
            {
                "page": 5,
                "badge": "찬반 토론 & 검색 CTA",
                "title": "소개팅 앱 첫마디 AI 추천 멘트 사용하는 것, 스마트하다 vs 진정성 없다?",
                "subtitle": "여러분의 솔직한 생각을 댓글로 남겨주세요! 👇",
                "bullets": [
                    "1번: 어색함 깨고 대화 시작하기 위한 스마트한 센스다",
                    "2번: 서툴러도 직접 고민해서 쓴 글이 진정성 있다",
                    "👉 프로필 링크에서 3초 만에 내 이상형/성향 확인!"
                ],
                "cta_button": "👉 프로필 링크에서 3초 이상형 확인 >"
            }
        ]
    },
    7: {
        "topic_id": 7,
        "theme_code": "ai_charm_scanner",
        "theme_name": "AI 매력상 & 궁합 진단",
        "official_keyword": "아우라AI데이팅",
        "slides": [
            {
                "page": 1,
                "badge": "🔥 2030 관상/매력 진단",
                "title": "내 얼굴은 여우상일까 강아지상일까? AI가 1초 만에 진단",
                "subtitle": "얼굴형과 분위기 분석부터 나와 찰떡인 이성 얼굴상까지 추천",
                "bullets": [
                    "친구들이 말해주는 동물상, AI는 어떻게 분석할까?",
                    "내 매력 포인트(청순, 시크, 댕댕미) 정밀 스캔",
                    "나와 시각적 케미가 터지는 황금 궁합 매칭 시스템"
                ],
                "cta_button": "👉 옆으로 넘겨서 매력 진단 보기 (1/5) >"
            },
            {
                "page": 2,
                "badge": "호감의 법칙",
                "title": "사람은 본능적으로 자신과 닮았거나 보완되는 상에 끌린다!",
                "subtitle": "심리학적으로 검증된 시각적 끌림과 호감도 메커니즘",
                "bullets": [
                    "무의식중에 편안함을 느끼는 얼굴 비율과 분위기가 존재",
                    "고양이상 x 대형견상, 시크상 x 과즙상의 대표적 케미",
                    "AI가 1,000만 건의 매칭 데이터를 기반으로 궁합 산출"
                ],
                "cta_button": "Aura 매력 스캐너 >"
            },
            {
                "page": 3,
                "badge": "Aura AI 비주얼 스캔",
                "title": "얼굴 랜드마크 128포인트 정밀 분석 시스템",
                "subtitle": "눈매, 입꼬리, 턱선 비율로 도출하는 나의 대표 매력 키워드",
                "bullets": [
                    "과즙미 뿜뿜 토끼상, 세련된 도시 고양이상 완벽 판독",
                    "내 매력을 200% 돋보이게 하는 헤어/코디 스타일 추천",
                    "프로필에 'AI 공인 매력 배지' 부착으로 관심도 UP"
                ],
                "cta_button": "궁합 매칭 라운지 >"
            },
            {
                "page": 4,
                "badge": "황금 궁합 매칭",
                "title": "나를 가장 매력적으로 봐줄 이상형과의 시크릿 매칭",
                "subtitle": "내 분위기를 선호하는 이성들에게 우선 노출되는 추천 알고리즘",
                "bullets": [
                    "서로의 외모 취향이 완벽히 일치하여 성공률 급증",
                    "첫 만남부터 칭찬으로 시작되는 훈훈한 분위기 형성",
                    "재미와 실속을 모두 잡은 AI 비주얼 데이팅"
                ],
                "cta_button": "댓글 찬반 투표 참여 >"
            },
            {
                "page": 5,
                "badge": "찬반 토론 & 검색 CTA",
                "title": "AI가 분석해주는 내 매력상 & 궁합 진단, 신뢰한다 vs 재미로만 본다?",
                "subtitle": "여러분의 솔직한 생각을 댓글로 남겨주세요! 👇",
                "bullets": [
                    "1번: 객관적인 데이터 분석이니 충분히 신뢰한다",
                    "2번: 흥미롭긴 하지만 재미로만 참고한다",
                    "👉 프로필 링크에서 3초 만에 내 이상형/성향 확인!"
                ],
                "cta_button": "👉 프로필 링크에서 3초 이상형 확인 >"
            }
        ]
    },
    8: {
        "topic_id": 8,
        "theme_code": "safe_radar_500m",
        "theme_name": "500m 안심 레이더",
        "official_keyword": "아우라AI데이팅",
        "slides": [
            {
                "page": 1,
                "badge": "🔥 동네 친구 & 보안 필수",
                "title": "동네 친구 사귀고 싶은데 집 위치 털릴까 봐 불안하셨나요?",
                "subtitle": "스토킹 걱정 0%! 500m 위치 랜덤 안심 레이더로 안전하게",
                "bullets": [
                    "동네 산책 메이트나 러닝 친구 찾을 때 위치 노출 불안",
                    "정확한 번지수 노출 없이 안전한 반경만 공유하는 보안 기술",
                    "2030 직장인이 안심하고 퇴근 후 번개 즐기는 법"
                ],
                "cta_button": "👉 옆으로 넘겨서 안심 보안 보기 (1/5) >"
            },
            {
                "page": 2,
                "badge": "위치 기반 앱의 위험성",
                "title": "실시간 GPS 위치 노출은 스토킹과 사생활 침해의 주범!",
                "subtitle": "상세한 동선과 집 주변이 특정되는 불안감을 해결합니다",
                "bullets": [
                    "내 원룸 바로 앞까지 상대에게 표시되는 공포",
                    "동네 친구는 사귀고 싶지만 사생활은 철저히 보호받아야 함",
                    "랜덤 오프셋 암호화 기술로 완벽한 안심 구역 생성"
                ],
                "cta_button": "Aura 500m 안심 레이더 >"
            },
            {
                "page": 3,
                "badge": "Aura 안심 보안",
                "title": "500m 범위 내에서 무작위 위치로 표시되는 스마트 보호",
                "subtitle": "상대방에겐 대략적인 생활권만 보이고 정확한 주소는 절대 비공개",
                "bullets": [
                    "내가 원할 때만 활성화되는 온/오프 위치 레이더",
                    "성수동, 연남동 등 핫플 카페 번개 시 안전한 거리 유지",
                    "여성 유저 만족도 1위의 독보적인 프라이버시 시스템"
                ],
                "cta_button": "동네 퀘스트 확인 >"
            },
            {
                "page": 4,
                "badge": "당일 동네 퀘스트",
                "title": "퇴근길 맥주 한잔, 주말 러닝 메이트 부담 없는 번개",
                "subtitle": "검증된 동네 이웃들과 만드는 건강하고 가벼운 취향 모임",
                "bullets": [
                    "100% 본인 인증 및 매너 평가 완료된 회원만 참여",
                    "부담 없는 스몰토크와 건강한 동네 인맥 형성",
                    "2030 직장인을 위한 가장 안전하고 스마트한 동네 라운지"
                ],
                "cta_button": "댓글 찬반 투표 참여 >"
            },
            {
                "page": 5,
                "badge": "찬반 토론 & 검색 CTA",
                "title": "동네 친구 만날 때 500m 위치 랜덤 안심 보안, 필수다 vs 굳이?",
                "subtitle": "여러분의 솔직한 생각을 댓글로 남겨주세요! 👇",
                "bullets": [
                    "1번: 사생활과 안전을 위해 무조건 필수다",
                    "2번: 대략적인 동네만 알면 상관없다",
                    "👉 프로필 링크에서 3초 만에 내 이상형/성향 확인!"
                ],
                "cta_button": "👉 프로필 링크에서 3초 이상형 확인 >"
            }
        ]
    }
}


class AuraCardnewsScenarioDirector:
    """💖 Aura 데이팅 전용 5장 카드뉴스 시나리오 디렉터"""

    @classmethod
    def get_cardnews_scenario(cls, topic_id: int = 1, fashion_id: Optional[int] = None) -> Dict[str, Any]:
        """
        주제 ID(1~8)에 맞춰 5장 완결 카드뉴스 시나리오 반환
        - 1번 주제일 때: 10대 소개팅 착장 프리셋(fashion_id) 중 하나를 선택하여
          1번(소개팅 OTS), 2번(화장실 파우더룸), 3번(호텔 정문 5m)의 의상/헤어에 100% 동일하게 일관 주입!
        """
        norm_id = ((topic_id - 1) % len(AURA_8_CARDNEWS_SCENARIOS)) + 1
        base_scenario = AURA_8_CARDNEWS_SCENARIOS.get(norm_id, AURA_8_CARDNEWS_SCENARIOS[1])
        scenario = copy.deepcopy(base_scenario)

        # 🌟 1번 주제: 10대 명품 소개팅 착장 일관 주입
        if norm_id == 1:
            fashion = get_fashion_preset(fashion_id)
            hair = fashion["hair_prompt"]
            outfit = fashion["outfit_prompt"]
            fashion_name = fashion["name_ko"]
            scenario["fashion_preset"] = fashion

            logger.info(f"👗 [AuraScenario] 1번 주제 '{fashion_name}'(ID={fashion['id']}) 착장 1~3번 슬라이드 공통 주입")

            # 1번 슬라이드: OTS 소개팅 구도
            if len(scenario["slides"]) >= 1:
                scenario["slides"][0]["image_prompt"] = (
                    "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
                    "cinematic over-the-shoulder shot (OTS) from directly behind a Korean man's back and dark navy suit jacket shoulder in the foreground, "
                    "the back of the man's head and right shoulder are softly visible in the lower foreground corner looking towards his date across the table, "
                    "seated directly across an antique dark wooden dining table is a breathtakingly beautiful 28-year-old Korean office woman, "
                    "she is seated upright looking directly across the table at him and the camera with warm authentic eye contact, "
                    "she has a subtle gentle polite smile, charming restrained smile with lips naturally closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
                    "perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck, graceful shoulders, "
                    f"{hair}, clear fair skin with realistic fine skin pores, refined subtle daytime makeup, "
                    f"wearing {outfit}, "
                    "on the dark wooden dining table between them are delicate wine glasses, neat cutlery, and folded linen napkins in tack sharp focus, "
                    "moody upscale evening bistro and wine restaurant in Cheongdam, soft warm pin-spot table lighting casting natural 3D facial depth, "
                    "Apple iPhone 15 Pro Smart HDR photo, f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, completely clear background in tack sharp crisp focus."
                )

            # 2번 슬라이드: 호텔 파우더룸 화장실 구도
            if len(scenario["slides"]) >= 2:
                scenario["slides"][1]["image_prompt"] = (
                    "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
                    "solo 1person female, the exact same gorgeous 28-year-old Korean office woman from slide 1, "
                    "perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck, "
                    f"{hair}, clear fair skin with realistic fine skin pores, refined subtle makeup, "
                    f"wearing the exact same {outfit}, "
                    "standing inside an ultra-luxurious 5-star hotel powder room and restroom, grand Italian marble vanity counter, elegant warm vanity mirror lighting with soft ambient golden glow in tack sharp f/11 focus, "
                    "she is holding her sleek smartphone in both hands at chest level, looking down intently at the glowing smartphone screen with a troubled, slightly anxious and frustrated facial expression, lips gently pressed together in serious thought, frantically trying to text a friend for an escape rescue call from an awkward blind date, "
                    "candid medium cowboy portrait shot showing upper body, hands holding smartphone, and luxury marble restroom interior, generous headroom above, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, Apple iPhone 15 Pro Smart HDR photo."
                )

            # 3번 슬라이드: 호텔 정문 5m 와이드 구도
            if len(scenario["slides"]) >= 3:
                scenario["slides"][2]["image_prompt"] = (
                    "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
                    "solo 1person female, the exact same gorgeous 28-year-old Korean office woman from slide 1 and slide 2, "
                    "perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck, "
                    f"{hair}, clear fair skin with realistic fine skin pores, refined subtle makeup, "
                    f"wearing the exact same {outfit}, "
                    "photographed from 5.0 meters distance in a wide environmental full-body shot, wide full length shot showing the subject from head to toe with generous headroom above, "
                    "standing outside the grand entrance canopy driveway of an ultra-luxurious 5-star hotel in Seoul at evening, magnificent modern hotel architecture with glowing warm golden entrance canopy lights and glass revolving doors in the background in tack sharp f/11 focus, "
                    "she is standing gracefully with an upright tall model posture, looking towards the camera with a subtle gentle restrained smile, a charming calm poised smile with lips naturally closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, elegant quiet relief and satisfaction after politely escaping an awkward blind date, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, pristine optical clarity, Apple iPhone 15 Pro Smart HDR photo."
                )

        # 🌟 2번 주제: 나나미(Nanami) 전용 10대 도쿄 여친 룩 일관 주입
        elif norm_id == 2:
            try:
                from .aura_cardnews_nanami_fashion_presets import AuraCardnewsNanamiFashionPresets
                nanami_fashion = AuraCardnewsNanamiFashionPresets.get_preset(fashion_id)
                outfit = nanami_fashion["outfit_prompt"]
                fashion_name = nanami_fashion["name_ko"]
                scenario["fashion_preset"] = nanami_fashion

                logger.info(f"👗 [AuraScenario] 2번 주제 나나미 '{fashion_name}'(ID={nanami_fashion['id']}) 착장 1~3번 슬라이드 공통 주입")

                # 1번 슬라이드
                if len(scenario["slides"]) >= 1:
                    scenario["slides"][0]["image_prompt"] = (
                        "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
                        "solo 1person female, an exceptionally gorgeous 24-year-old Japanese young woman (Nanami), "
                        "perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck, authentic real human model visual, "
                        "authentic natural human skin with visible fine pores and realistic delicate skin texture, strictly no airbrushing, "
                        "charming expressive doe-like hazel-brown eyes, delicate see-through bangs, neat dark brown shoulder-length hair, "
                        "she has a subtle gentle polite smile, charming restrained smile with lips naturally closed together, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
                        f"{outfit}, "
                        "she is holding her sleek smartphone in both hands, looking down affectionately at the glowing smartphone screen in a warm video call and messaging moment, "
                        "sitting in a sunlit trendy glasshouse boutique cafe in Seongsu-dong with clean polished white marble table, warm soft natural sunlight streaming through floor-to-ceiling glass windows, "
                        "warm directional room ambient lighting creating natural depth and rich realistic shadows, "
                        "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, Apple iPhone 15 Pro Smart HDR photo."
                    )

                # 2번 슬라이드
                if len(scenario["slides"]) >= 2:
                    scenario["slides"][1]["image_prompt"] = (
                        "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
                        "solo 1person female, the exact same gorgeous 24-year-old Japanese young woman (Nanami) from slide 1, "
                        "perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck, authentic real human model visual, "
                        "authentic natural human skin with visible fine pores and realistic delicate skin texture, strictly no airbrushing, "
                        "charming expressive doe-like hazel-brown eyes, delicate see-through bangs, neat dark brown shoulder-length hair, "
                        f"{outfit}, "
                        "she is holding her sleek smartphone steadily in both hands at chest level, looking down intently at the glowing smartphone screen in front of her chest with a troubled, slightly anxious and perplexed facial expression, cute delicate head tilt, lips naturally closed together in serious thought, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
                        "struggling to understand unfamiliar foreign Korean text on the glowing smartphone screen, feeling cute and awkward embarrassment, "
                        "pristine anatomically correct five-finger hands holding the phone edges naturally, completely clear realistic hands, "
                        "sitting in the exact same warm cozy Tokyo apartment living room from slide 1 with authentic dark oak wooden bookshelves filled with books, vibrant lush green indoor potted plants, "
                        "warm directional room ambient lighting creating natural depth and rich realistic shadows, "
                        "candid medium cowboy portrait shot showing upper body, both hands holding smartphone in front of chest, and living room background, generous headroom above, "
                        "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, Apple iPhone 15 Pro Smart HDR photo."
                    )

                # 3번 슬라이드
                if len(scenario["slides"]) >= 3:
                    scenario["slides"][2]["image_prompt"] = (
                        "masterpiece, best quality, ultra-photorealistic portrait, authentic candid mobile snapshot shot on iPhone 15 Pro, "
                        "solo 1person female, the exact same gorgeous 24-year-old Japanese young woman (Nanami) from slide 1 and slide 2, "
                        "perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck, authentic real human model visual, "
                        "authentic natural human skin with visible fine pores and realistic delicate skin texture, strictly no airbrushing, "
                        "charming expressive doe-like hazel-brown eyes crinkling warmly in genuine happiness, delicate see-through bangs, neat dark brown shoulder-length hair, "
                        f"{outfit}, "
                        "she is holding her sleek smartphone steadily in both hands in front of her chest, looking down intently at the glowing smartphone screen and laughing delightfully in pure joy, "
                        "she has a radiant, bright, cheerful and lovely warm smile, captivating genuine joyful smile, lips naturally parted showing natural white teeth in a pleasant friendly laugh, eyes filled with warmth and romantic excitement, "
                        "having an incredibly fun and heartwarming video call moment where communication flows effortlessly, "
                        "pristine anatomically correct five-finger hands holding the phone naturally, completely clear realistic hands, "
                        "sitting in the exact same warm cozy Tokyo apartment living room from slide 1 with authentic dark oak wooden bookshelves filled with books, vibrant lush green indoor potted plants, "
                        "warm directional room ambient lighting creating natural depth and rich realistic shadows, "
                        "candid medium cowboy portrait shot showing upper body, both hands holding smartphone, and living room background, generous headroom above, "
                        "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus across entire frame, realistic skin subsurface scattering, Apple iPhone 15 Pro Smart HDR photo."
                    )
            except Exception as e:
                logger.warning(f"⚠️ [AuraScenario] 나나미 착장 주입 중 예외 발생: {e}")

        return scenario

    @classmethod
    def get_scenario(cls, topic_id: int = 1, fashion_id: Optional[int] = None) -> Dict[str, Any]:
        """get_cardnews_scenario alias"""
        return cls.get_cardnews_scenario(topic_id=topic_id, fashion_id=fashion_id)

    @classmethod
    def get_all_topics(cls) -> List[Dict[str, Any]]:
        """Aura 8대 주제 메타데이터 목록 반환"""
        topics = []
        for t_id, data in AURA_8_CARDNEWS_SCENARIOS.items():
            topics.append({
                "topic_id": t_id,
                "theme_name": data.get("theme_name", f"주제 {t_id}"),
                "theme_code": data.get("theme_code", f"topic_{t_id:02d}"),
                "total_slides": len(data.get("slides", []))
            })
        return topics
