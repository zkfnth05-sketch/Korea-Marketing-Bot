from core.gemini_unified_keys import get_unified_gemini_key_dicts, get_unified_gemini_keys, format_gemini_error
# -*- coding: utf-8 -*-
"""
AuraShortsScenarioDirector - 🎬 [Aura 8대 주제 22초 3단계 숏폼 대본 & 비주얼 오버레이 디렉터]
- 8대 주제별 인물 정의 및 배경 정의와 100% 일치 연동
- Wan 2.2 S2V 립싱크 모션 프롬프트: 1.2m 친밀한 테이블 대화 제스처 (스마트폰 파지 배제)
- 22초 3단계 완결형 단일 스토리라인:
  1) [0초 ~ 10초] 인물 립싱크 킬러 훅 (소개팅 썰, 공감 포인트)
  2) [10초 ~ 18초] 라이브 앱 기능 안내 (탈출 전화, 자막 통화, 50:50 게이트 등)
  3) [18초 ~ 22초] 안심 신뢰 뱃지 & 프로필 링크 촉구 CTA ("지금 바로 프로필 링크를 터치해 보세요!")
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("AuraShortsScenarioDirector")

# ==============================================================================
# [대표님 최종 승인] CTA 표준 문구 상수 - 16개 전 슬롯 단일 소스
# ==============================================================================
CTA_BUTTON_TEXT = "👉 프로필 링크 터치 (@aura_ai_dating)"
CTA_NARRATION_DEFAULT = "지금 바로 프로필 링크를 터치해 보세요!"
CTA_NARRATION_FAST = "지금 프로필 링크 누르고 3초 만에 무료로 확인해봐!"

# ==============================================================================
# [대표님 최종 승인] 5번 검증 기반 골든 손동작 모션 프롬프트 규격 (16개 전 슬롯)
# ==============================================================================
GOLDEN_MOTION_TALKING_HANDS = (
    "speaking expressively with smooth realistic lip sync, enthusiastic head nodding and playful head tilts, "
    "natural hand and upper body gestures while talking, friendly and dynamic movement, "
    "no phone in hand, lifelike motion"
)

GOLDEN_MOTION_WINE_HANDS = (
    "holding a crystal wine glass comfortably at waist level in one hand, "
    "while naturally gesturing with the other hand while speaking, "
    "subtle head tilts and gentle nodding, elegant and lively feminine upper body movement, "
    "no phone in hand, authentic evening cocktail party motion"
)

GOLDEN_MOTION_MALE_HANDS = (
    "speaking expressively with articulate lip sync, subtle nodding, "
    "natural masculine hand and upper body gestures while talking, "
    "confident and friendly conversational movement, leaning forward slightly in a friendly engaging conversation, "
    "no phone in hand, lively authentic human motion"
)


class AuraShortsScenarioDirector:
    """Aura 22초 완결형 숏폼 대본 및 화면 오버레이 기획 엔진"""

    # CTA 표준 문구 (외부 모듈에서 참조 가능하도록 클래스 속성으로도 노출)
    CTA_BUTTON_TEXT = CTA_BUTTON_TEXT
    CTA_NARRATION_DEFAULT = CTA_NARRATION_DEFAULT
    CTA_NARRATION_FAST = CTA_NARRATION_FAST

    SCRIPTS_22S = {
        1: {
            "topic_id": 1,
            "theme_name": "소개팅 탈출 전화",
            "theme_code": "escape_call",
            "gender": "female",
            "hook_p1_5s": "소개팅 나갔는데 상대가 완전 빌런일 때 어떻게 하시나요?",
            "hook_p2_5s": "화장실로 튀어서 일 분 뒤 긴급 탈출 예약을 딱 누르세요!",
            "hook_0_10s": "소개팅 나갔는데 상대가 완전 빌런일 때 어떻게 하시나요? 화장실로 튀어서 일 분 뒤 긴급 탈출 예약을 딱 누르세요!",
            "app_10_18s": "일 분 뒤에 진짜 구원 전화가 걸려오고 화면에 탈출 대본까지 다 떠요!",
            "cta_18_22s": "합법적으로 칼탈출 성공! 지금 바로 프로필 링크를 터치해 보세요!",
            "debate_question": "이 탈출법, 센스다 vs 너무하다?",
            "hero_copy": "합법적으로 칼탈출 성공!",
            "top_header": "",
            "bottom_step1_title": "",
            "bottom_step1_sub": "",
            "bottom_step2_title": "",
            "bottom_step2_sub": "",
            "cta_button_text": CTA_BUTTON_TEXT,
            "s2v_motion_prompt": (
                "a beautiful 28-year-old Korean office woman sitting across a dinner table, looking directly into camera with expressive authentic eye contact, "
                + GOLDEN_MOTION_TALKING_HANDS
            ),
            "char_desc": (
                "a beautiful 28-year-old Korean woman, perfect 8-head-high golden ratio model proportions, delicate small petite head and face, slender elegant long neck, calm low ponytail hairstyle, clear fair skin, "
                "refined subtle makeup, wearing stylish sophisticated civilian dating clothes, a chic modern evening dinner outfit, "
                "elegant and poised appearance with genuine expressive eyes looking directly into the camera lens"
            ),
            "bg_desc": (
                "moody upscale evening bistro and wine restaurant in Cheongdam, soft warm pin-spot table lighting, "
                "antique dark wooden dining table, blurred delicate wine glasses and neat linen napkin in the background"
            ),
            "voice_pitch": "+3Hz",
            "voice_rate": "+4%"
        },
        2: {
            "topic_id": 2,
            "theme_name": "실시간 자막 통화",
            "theme_code": "live_subtitles",
            "gender": "female",
            "hook_p1_5s": "곤니치와! 저 한국어 1도 모르는데 친구 사귄 비결!",
            "hook_p2_5s": "아우라 앱으로 영상통화 걸면 화면 밑에 넷플릭스처럼 실시간 자막이 다 떠요!",
            "hook_0_10s": "곤니치와! 저 한국어 1도 모르는데 친구 사귄 비결! 아우라 앱으로 영상통화 걸면 화면 밑에 넷플릭스처럼 실시간 자막이 다 떠요!",
            "app_10_18s": "제가 일본어로 말하면 한국어 자막이 실시간으로 뜨고, 한국어로 말씀하셔도 일본어로 번역돼서 소통 끝!",
            "cta_18_22s": "일본인 친구 생기면 도쿄에서 어디 가고 싶으신가요? 지금 바로 프로필 링크를 터치해 보세요!",
            "debate_question": "자막 통화로 외국인 친구 사귀기, 가능하다 vs 어렵다?",
            "top_header": "",
            "bottom_step1_title": "",
            "bottom_step1_sub": "",
            "bottom_step2_title": "",
            "bottom_step2_sub": "",
            "cta_button_text": CTA_BUTTON_TEXT,
            "s2v_motion_prompt": (
                "a lovely 24-year-old Japanese young woman (Nanami) in Tokyo, sitting in an authentic living room with wooden bookshelves and green plants, looking directly into camera with charming sweet eye contact, "
                + GOLDEN_MOTION_TALKING_HANDS
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
            "voice_pitch": "+5Hz",
            "voice_rate": "+6%"
        },
        3: {
            "topic_id": 3,
            "theme_name": "50:50 VIP 게이트",
            "theme_code": "vip_gate",
            "gender": "female",
            "hook_p1_5s": "소개팅 앱 깔았다가 남자가 90%라 음침한 디엠 쏟아져서 바로 지운 사람 손?",
            "hook_p2_5s": "아우라는 남녀 성비 50:50 안 맞으면 남자 가입 대기 걸어버려요!",
            "hook_0_10s": "소개팅 앱 깔았다가 남자가 90%라 음침한 디엠 쏟아져서 바로 지운 사람 손? 아우라는 남녀 성비 50:50 안 맞으면 남자 가입 대기 걸어버려요!",
            "app_10_18s": "남성은 정원 찰 때까지 줄 서서 대기하고, 여성은 VIP 프리패스로 바로 입장! 물 흐리는 사람 1도 없고 대화 퀄리티가 완전 달라요.",
            "cta_18_22s": "남녀 50:50 정원제, 찬성인가요 반대인가요? 지금 바로 프로필 링크를 터치해 보세요!",
            "top_header": "50:50 황금 성비 청정 라운지 • AURA",
            "bottom_step1_title": "남탕 불쾌감 제로! 50:50 정원제",
            "bottom_step1_sub": "남성 대기열 관리 • 여성 VIP 프리패스 즉시 입장",
            "bottom_step2_title": "수질 100% 보장 • 청정 매너 라운지",
            "bottom_step2_sub": "엄격한 성비 관리 • 고품격 매너 라운지",
            "debate_question": "남녀 50:50 정원제, 찬성 vs 반대?",
            "hero_copy": "남초 제로, 50:50 완벽 성비!",
            "cta_button_text": CTA_BUTTON_TEXT,
            "s2v_motion_prompt": (
                "an exceptionally gorgeous glamorous 26-year-old Korean woman standing by the glass railing of an upscale rooftop terrace, looking directly into camera with deeply captivating alluring eye contact, "
                + GOLDEN_MOTION_WINE_HANDS
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
            "voice_pitch": "-7Hz",
            "voice_rate": "+12%"
        },
        4: {
            "topic_id": 4,
            "theme_name": "청담동 화보 보정",
            "theme_code": "cheongdam_enhance",
            "gender": "female",
            "hook_p1_5s": "소개팅 앱에 인조인간 필터 올렸다가 실물 보고 도망가지 마시고...",
            "hook_p2_5s": "아우라 앱에 셀카 한 장 넣으면 청담동 화보로 바로 바꿔줍니다!",
            "hook_0_10s": "소개팅 앱에 인조인간 필터 올렸다가 실물 보고 도망가지 마시고, 아우라 앱에 셀카 한 장 넣으면 청담동 화보로 바로 바꿔줍니다!",
            "app_10_18s": "내 본래 이목구비는 그대로 살리면서 피부톤과 조명을 청담동 스튜디오 감성으로 세련되고 사랑스럽게 업그레이드해 줘요.",
            "cta_18_22s": "이 정도 보정이면 사기다 vs 자기관리다? 지금 바로 프로필 링크를 터치해 보세요!",
            "debate_question": "이 정도 보정, 사기다 vs 자기관리다?",
            "hero_copy": "내 본판 그대로 인생 화보 완성!",
            "top_header": "청담동 스냅 화보급 AI 보정 • AURA",
            "bottom_step1_title": "가짜 필터 NO! 본판 100% 보존",
            "bottom_step1_sub": "인위적인 틱톡 필터 탈피 • 자연스러운 실사 화보",
            "bottom_step2_title": "청담 스튜디오 감성 즉각 업그레이드",
            "bottom_step2_sub": "매칭률 5배 상승 • 세련되고 사랑스러운 무드",
            "cta_button_text": CTA_BUTTON_TEXT,
            "s2v_motion_prompt": (
                "a gorgeous 23-year-old Korean young woman, sitting gracefully in a designer white armchair inside a modern Cheongdam photography studio, looking directly into camera with radiant gentle eye contact, "
                + GOLDEN_MOTION_TALKING_HANDS
            ),
            "char_desc": (
                "a breathtakingly stunning 23-year-old Korean young woman, perfect 8-head-high golden ratio model proportions, delicate small petite head and face size, slender elegant long neck and collarbone, pure legendary first-love visual aesthetic, "
                "flowing natural dark silky wavy hair, immaculate luminous glass skin, captivating innocent eyes, delicate facial symmetry, "
                "wearing an elegant soft knit cardigan layered over a clean camisole, stylish feminine studio photoshoot attire, refined modern aesthetic fashion, looking directly into the camera lens"
            ),
            "bg_desc": (
                "high-end luxury photography studio in Cheongdam, modern curved architectural round arch alcove wall with soft warm peach-beige ambient indirect glow, "
                "elegant designer single white lounge armchair in the center, clean polished studio floor, tack sharp f/11 focus"
            ),
            "voice_pitch": "+4Hz",
            "voice_rate": "+3%"
        },
        5: {
            "topic_id": 5,
            "theme_name": "가치관 밸런스 매칭",
            "theme_code": "balance_match",
            "gender": "female",
            "hook_p1_5s": "소개팅 첫 만남 더치페이, 칼같이 반띵인가요? 아니면 번갈아 내기인가요?",
            "hook_p2_5s": "아우라에서 밸런스 게임 투표하면 나랑 가치관 똑같은 사람만 연결해 줘요!",
            "hook_0_10s": "소개팅 첫 만남 더치페이, 칼같이 반띵인가요? 아니면 번갈아 내기인가요? 아우라에서 밸런스 게임 투표하면 나랑 가치관 똑같은 사람만 연결해 줘요!",
            "app_10_18s": "얼굴만 보고 만났다가 연락 문제, 데이트 비용 때문에 싸우지 마세요! 가치관 100% 일치자만 매칭되니까 대화가 너무 잘 통해요.",
            "cta_18_22s": "첫 만남 더치페이, 여러분의 선택은? 지금 바로 프로필 링크를 터치해 보세요!",
            "top_header": "가치관 밸런스 매칭 • AURA",
            "bottom_step1_title": "연락 주기 & 데이트 비용 밸런스 투표",
            "bottom_step1_sub": "더치페이 vs 번갈아 내기 가치관 실시간 확인",
            "bottom_step2_title": "생각 100% 통하는 사람 즉시 연결",
            "bottom_step2_sub": "소비관/연애관 갈등 제로 • 편안한 연애 시작",
            "debate_question": "첫 만남 더치페이, 반띵 vs 번갈아 내기?",
            "hero_copy": "생각 통하는 사람만 100% 매칭!",
            "cta_button_text": CTA_BUTTON_TEXT,
            "s2v_motion_prompt": (
                "a bright friendly 21-year-old Korean college girl, seated comfortably at a brunch table, looking into camera with lively authentic eye contact, "
                + GOLDEN_MOTION_TALKING_HANDS
            ),
            "char_desc": (
                "an exceptionally gorgeous 21-year-old Korean campus goddess with breathtakingly enchanting feline cat-like facial features, "
                "captivating alluring cat-like almond dark eyes with subtle sharp upturned winged eyeliner, "
                "sharp high cheekbones, delicate cute petite nose, sculpted flawless V-line jawline, "
                "radiant luminous porcelain glass skin with soft natural peach cheek glow, "
                "neat sleek low bun hairstyle with subtle elegant side fringe framing her face perfectly, "
                "wearing a chic clean minimalist white ribbed-knit sleeveless dress with a wide-strap square neckline, "
                "fitted ribbed texture accentuating her graceful slender collarbone and delicate bare shoulders, elegant sophisticated summer brunch date attire, looking directly into the camera lens"
            ),
            "bg_desc": (
                "cozy outdoor brunch cafe patio with lush green leaves canopy, rustic wooden table with iced latte, "
                "pleasant tree shade with dappled natural sunlight, tack sharp f/11 focus"
            ),
            "voice_pitch": "+6Hz",
            "voice_rate": "+6%"
        },
        6: {
            "topic_id": 6,
            "theme_name": "AI 첫대화 비서",
            "theme_code": "ai_icebreaker",
            "gender": "male",
            "hook_p1_5s": "마음에 드는 이성한테 첫 메세지 보낼 때, 뭐라고 보낼지 막막했던 적 있으시죠?",
            "hook_p2_5s": "아우라 AI 비서 켜면 상대 취향 딱 분석해서 센스 넘치는 첫마디를 써줘요!",
            "hook_0_10s": "마음에 드는 이성한테 첫 메세지 보낼 때, 뭐라고 보낼지 막막했던 적 있으시죠? 아우라 AI 비서 켜면 상대 취향 딱 분석해서 센스 넘치는 첫마디를 써줘요!",
            "app_10_18s": "상대 프로필을 분석해 1초 만에 티키타카 터지는 맞춤 대화를 추천해 주니까 첫 대화 피로도가 제로예요.",
            "cta_18_22s": "읽씹 없는 첫 대화 치트키, 지금 바로 프로필 링크를 터치해 보세요!",
            "top_header": "AI 첫대화 답장 비서 • AURA",
            "bottom_step1_title": "읽씹 탈출! 상대 맞춤형 첫인사 생성",
            "bottom_step1_sub": "숨 막히는 단답 대화 원천 차단 • 티키타카 폭발",
            "bottom_step2_title": "AI 대화 코칭 • 애프터 성공률 98%",
            "bottom_step2_sub": "답장 고민 끝 • 센스 넘치는 자연스러운 핑퐁",
            "debate_question": "매칭 후 첫 메시지, 센스 멘트 vs 솔직 담백?",
            "hero_copy": "읽씹 없는 첫 대화 치트키 가동!",
            "cta_button_text": CTA_BUTTON_TEXT,
            "s2v_motion_prompt": (
                "an exceptionally handsome 26-year-old Korean adult man (K-drama male lead actor visual), standing on an upscale outdoor rooftop sky lounge terrace at night, looking directly into camera with warm romantic eye contact, "
                + GOLDEN_MOTION_MALE_HANDS
            ),
            "char_desc": (
                "an exceptionally handsome 26-year-old Korean adult man (K-drama male lead actor visual, delicate handsome idol-actor appearance, refined aesthetic features), perfect 8-head-high golden ratio male model proportions, small refined masculine head and face size, slender athletic male physique with broad masculine shoulders, "
                "soft gentle smile with lips closed together, refined handsome features, sharp sculpted jawline with natural subtle directional shadow, charismatic warm romantic gaze, strictly no teeth showing, "
                "neat stylish dark brown natural dandy haircut with subtle parted fringe framing his face, "
                "authentic real human skin texture with visible fine pores and natural skin tone, "
                "wearing a stylish, trendy modern casual jacket outfit, sophisticated 2030 Seoul dating fashion with diverse contemporary colors and textures, clean minimalist innerwear, effortless charismatic boyfriend-material date look, "
                "arms resting naturally straight down at sides, hands visible outside pockets, strictly no hands in pockets, "
                "authentic candid mobile phone snapshot on Apple iPhone 15 Pro, looking directly into camera lens"
            ),
            "bg_desc": (
                "upscale modern outdoor open-air rooftop sky lounge terrace in Seoul at night with glowing warm Edison string bulb lights and elegant golden patio lanterns, "
                "standing beside sleek glass balustrade overlooking vibrant colorful glowing city neon lights and panoramic glittering Seoul night skyline in tack sharp f/11 focus, "
                "luxurious warm architectural uplighting illuminating the terrace ambiance naturally, authentic iPhone 15 Pro mobile night photo atmosphere"
            ),
            "voice_pitch": "-3Hz",
            "voice_rate": "+12%"
        },
        7: {
            "topic_id": 7,
            "theme_name": "AI 아우라 진단",
            "theme_code": "aura_diagnosis",
            "gender": "female",
            "hook_p1_5s": "요즘 인스타 스토리에서 난리 난 내 얼굴 아우라 매력 테스트 해보셨나요?",
            "hook_p2_5s": "셀카 한 장 넣었더니 AI가 상위 3.8% 다정한 여우상이라고 분석해 줬어요!",
            "hook_0_10s": "요즘 인스타 스토리에서 난리 난 내 얼굴 아우라 매력 테스트 해보셨나요? 셀카 한 장 넣었더니 AI가 상위 3.8% 다정한 여우상이라고 분석해 줬어요!",
            "app_10_18s": "내 얼굴의 고유한 분위기와 매력 키워드를 분석해서 인스타에 바로 올리고 싶은 고화질 진단 카드로 도출해 줍니다.",
            "cta_18_22s": "내 아우라 점수, 몇 점 나올 것 같으신가요? 지금 바로 프로필 링크를 터치해 보세요!",
            "top_header": "AI 매력도 진단 리포트 • AURA",
            "bottom_step1_title": "상위 % 아우라 진단 카드 도출",
            "bottom_step1_sub": "Gemini Vision AI 얼굴 분위기 & 매력 분석",
            "bottom_step2_title": "인스타 스토리 자랑용 고화질 카드",
            "bottom_step2_sub": "내 매력 타이틀 확인 • 바이럴 폭발 테스트",
            "debate_question": "내 얼굴 아우라 매력, 상위 몇 %일까?",
            "hero_copy": "AI 매력 분석, 상위 3.8% 진단!",
            "cta_button_text": CTA_BUTTON_TEXT,
            "s2v_motion_prompt": (
                "a fashionable 25-year-old Korean woman, sitting in a trendy cafe looking directly into camera with charming playful eye contact, "
                + GOLDEN_MOTION_TALKING_HANDS
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
            "voice_pitch": "+1Hz",
            "voice_rate": "+7%"
        },
        8: {
            "topic_id": 8,
            "theme_name": "500m 안심 레이더",
            "theme_code": "safe_radar",
            "gender": "female",
            "hook_p1_5s": "소개팅 앱에서 며칠씩 간만 보고 톡만 질질 끌다가 지치셨던 분들 계시죠?",
            "hook_p2_5s": "아우라는 내가 원할 때 동네 편한 친구를 500미터 안심 보안으로 바로 만날 수 있어요!",
            "hook_0_10s": "소개팅 앱에서 며칠씩 간만 보고 톡만 질질 끌다가 지치셨던 분들 계시죠? 아우라는 내가 원할 때 동네 편한 친구를 500미터 안심 보안으로 바로 만날 수 있어요!",
            "app_10_18s": "실제 주소 노출 없이 성수동 카페 메이트나 가벼운 러닝 메이트를 안전하게 찾아서 당일 번개로 만날 수 있어요.",
            "cta_18_22s": "동네 산책 메이트, 동성만 가능 vs 이성도 가능? 지금 바로 프로필 링크를 터치해 보세요!",
            "top_header": "500m 안심 레이더 • AURA",
            "bottom_step1_title": "간보기 톡 지쳤다면? 500m 안심 매칭",
            "bottom_step1_sub": "내가 원할 때 바로 만나는 동네 편한 친구",
            "bottom_step2_title": "안전한 24시간 지도 퀘스트",
            "bottom_step2_sub": "실시간 러닝·카페 메이트 안심 번개",
            "debate_question": "동네 산책 메이트, 동성만 vs 이성도 가능?",
            "hero_copy": "스토킹 걱정 제로, 500m 안심 매칭!",
            "cta_button_text": CTA_BUTTON_TEXT,
            "s2v_motion_prompt": (
                "an energetic 25-year-old Korean young woman, sitting at a sunny outdoor terrace cafe looking directly into camera with charming eye contact, "
                + GOLDEN_MOTION_TALKING_HANDS
            ),
            "char_desc": (
                "an exceptionally stunning 25-year-old Korean fitness goddess visual, perfect 8-head-high golden ratio athletic model proportions, delicate small petite head and sculpted face, slender elegant neck, top 0.1% captivating feline fox-like eyes with subtle cat-eye eyeliner, glowing radiant sun-kissed fair skin, "
                "sleek high ponytail hairstyle, "
                "wearing a chic rich saturated deep cobalt blue and dark navy form-fitting athletic zip-up top, sleek stylish outdoor activewear, refreshing fitness runner fashion, looking directly into the camera lens"
            ),
            "bg_desc": (
                "sunny outdoor terrace cafe near Seoul Forest park, lush green trees and park walking trail visible in background, "
                "bright refreshing afternoon natural daylight, pleasant outdoor atmosphere"
            ),
            "voice_pitch": "+4Hz",
            "voice_rate": "+8%"
        }
    }

    # ==========================================================================
    # 🏛️ [6인 합의체 도파민 팩 8종 — 슬롯 9~16번] 기존 1~8번 100% 무손실 보존
    #    - 앵커 캐릭터/배경/S2V 모션은 1~8번 마스터 앵커를 그대로 승계 (비주얼 일관성)
    # ==========================================================================
    SCRIPTS_22S_EXT = {
        9: {
            "topic_id": 9,
            "theme_name": "소개팅 탈출 실전편",
            "theme_code": "escape_real",
            "gender": "female",
            "hook_p1_5s": "소개팅 나갔는데 상대가 완전 빌런일 때 어떻게 하시나요?",
            "hook_p2_5s": "화장실로 튀어서 30초 뒤 긴급 탈출 예약을 딱 누르세요!",
            "hook_0_10s": "소개팅 나갔는데 상대가 완전 빌런일 때 어떻게 하시나요? 화장실로 튀어서 30초 뒤 긴급 탈출 예약을 딱 누르세요!",
            "app_10_18s": "자리 돌아오자마자 팀장님 진짜 구원 전화 울리고 화면에 탈출 대본까지 다 떠요!",
            "cta_18_22s": "합법적으로 30초 칼탈출 성공! 지금 프로필 링크 누르고 3초 만에 무료로 확인해봐!",
            "debate_question": "소개팅 중 가짜 탈출 전화, 센스일까 비매너일까?",
            "hero_copy": "30초 만에 합법 칼탈출!",
            "top_header": "30초 긴급 탈출 전화 • AURA",
            "bottom_step1_title": "화장실 30초 예약 → 팀장님 구원 콜",
            "bottom_step1_sub": "가짜 긴급 업무 호출 • 매너 있게 칼탈출",
            "bottom_step2_title": "탈출 대본까지 화면에 실시간 표시",
            "bottom_step2_sub": "어색한 자리 탈출 • 합법적이고 깔끔한 퇴장",
            "cta_button_text": CTA_BUTTON_TEXT,
            "s2v_motion_prompt": (
                "a beautiful 28-year-old Korean office woman sitting across a dinner table, looking directly into camera with expressive authentic eye contact, "
                + GOLDEN_MOTION_TALKING_HANDS
            ),
            "char_desc": (
                "an exceptionally attractive 28-year-old Korean office woman with natural elegant charm, "
                "authentic real human skin with visible fine skin pores, calm low ponytail hairstyle, "
                "refined subtle makeup, wearing stylish sophisticated civilian dating clothes, a chic modern evening dinner outfit, "
                "elegant and poised appearance with genuine expressive eyes looking directly into the camera lens"
            ),
            "bg_desc": (
                "moody upscale evening bistro and wine restaurant in Cheongdam, soft warm pin-spot table lighting, "
                "antique dark wooden dining table, blurred delicate wine glasses and neat linen napkin in the background"
            ),
            "voice_pitch": "+3Hz",
            "voice_rate": "+4%"
        },
        10: {
            "topic_id": 10,
            "theme_name": "도쿄 현지인 영통 썰",
            "theme_code": "tokyo_call",
            "gender": "female",
            "hook_p1_5s": "스미마셍 말고 1도 몰라도 일본 여사친이랑 밤새 통화하는 법!",
            "hook_p2_5s": "화면 밑에 실시간 번역 자막이 다 떠요!",
            "hook_0_10s": "스미마셍 말고 1도 몰라도 일본 여사친이랑 밤새 통화하는 법! 화면 밑에 실시간 번역 자막이 다 떠요!",
            "app_10_18s": "내가 한국어로 말하면 일본어 자막이, 상대 일본어가 나한테 한글 자막으로 1초 만에 떠서 소통 끝!",
            "cta_18_22s": "외국인 찐친 만들기 성공! 지금 프로필 링크 누르고 3초 만에 무료로 확인해봐!",
            "debate_question": "외국인 찐친 만들기, 번역기 없이 진짜 가능할까?",
            "hero_copy": "실시간 번역 자막으로 소통 끝!",
            "top_header": "실시간 양방향 번역 자막 • AURA",
            "bottom_step1_title": "한국어 → 일본어 자막 1초 실시간",
            "bottom_step1_sub": "번역기 복붙 제로 • 끊김 없는 대화 흐름",
            "bottom_step2_title": "언어 장벽 제로 • 외국인 찐친 만들기",
            "bottom_step2_sub": "도쿄 현지인과 밤새 랜선 수다 • 글로벌 데이팅",
            "cta_button_text": CTA_BUTTON_TEXT,
            "s2v_motion_prompt": (
                "a lovely 24-year-old Japanese young woman (Nanami) in Tokyo, sitting in an authentic living room with wooden bookshelves and green plants, looking directly into camera with charming sweet eye contact, "
                + GOLDEN_MOTION_TALKING_HANDS
            ),
            "char_desc": (
                "an exceptionally gorgeous 24-year-old Japanese young woman (Nanami) with authentic natural beauty, "
                "real human skin with visible fine pores and realistic delicate skin texture, strictly no airbrushing, "
                "charming expressive doe-like hazel-brown eyes, delicate see-through bangs, neat dark brown shoulder-length hair, "
                "wearing clean stylish civilian casual clothes, a neat comfortable daily outfit, looking directly into the camera lens"
            ),
            "bg_desc": (
                "warm cozy living room with authentic dark oak wooden bookshelves filled with books, "
                "vibrant lush green indoor potted plants, warm directional room ambient lighting creating natural depth and rich realistic shadows, "
                "warm inviting atmosphere with over 75% background rich interior details in tack sharp f/11 focus"
            ),
            "voice_pitch": "+5Hz",
            "voice_rate": "+6%"
        },
        11: {
            "topic_id": 11,
            "theme_name": "소개팅앱 삭제하는 이유",
            "theme_code": "delete_app",
            "gender": "female",
            "hook_p1_5s": "소개팅 어플 깔았다가 남초 90%라 음침한 디엠 쏟아져서 바로 지운 사람 손?",
            "hook_p2_5s": "아우라는 성비 5:5 안 맞으면 남자 가입 대기 걸어버려요!",
            "hook_0_10s": "소개팅 어플 깔았다가 남초 90%라 음침한 디엠 쏟아져서 바로 지운 사람 손? 아우라는 성비 5:5 안 맞으면 남자 가입 대기 걸어버려요!",
            "app_10_18s": "남성은 정원 찰 때까지 줄 서서 대기하고 여성은 VIP 프리패스! 물 흐리는 사람 1도 없고 대화 퀄리티가 달라요.",
            "cta_18_22s": "남녀 성비 50:50 완벽 보장! 지금 프로필 링크 누르고 3초 만에 무료로 확인해봐!",
            "debate_question": "성비 50:50 강제 대기열, 남자 역차별이다 vs 필수 안전장치다?",
            "hero_copy": "50:50 안 맞으면 문 닫습니다!",
            "top_header": "50:50 황금 성비 청정 라운지 • AURA",
            "bottom_step1_title": "남초 불쾌감 제로! 50:50 정원제",
            "bottom_step1_sub": "남성 대기열 관리 • 여성 VIP 프리패스 즉시 입장",
            "bottom_step2_title": "수질 100% 보장 • 청정 매너 라운지",
            "bottom_step2_sub": "엄격한 성비 관리 • 고품격 매너 라운지",
            "cta_button_text": CTA_BUTTON_TEXT,
            "s2v_motion_prompt": (
                "a stunning 26-year-old VIP Korean woman standing on a luxury hotel rooftop terrace at night, looking directly into camera with confident magnetic allure, "
                + GOLDEN_MOTION_WINE_HANDS
            ),
            "char_desc": (
                "an exceptionally gorgeous glamorous 26-year-old Korean woman standing with effortless confidence and poise, "
                "natural elegant posture, captivating warm dark eyes, voluminous natural dark silky wavy hair falling gracefully over her shoulders, "
                "authentic real skin texture with visible fine pores, sharp high cheekbones and sculpted jawline, "
                "wearing an ultra-luxurious glamorous evening party dress, a chic upscale rooftop lounge cocktail outfit, sophisticated high-society date-night style"
            ),
            "bg_desc": (
                "romantic midnight night view in Seoul, ultra-luxury high-end hotel rooftop sky lounge and open-air champagne bar in Gangnam, "
                "standing beside modern glass balustrade overlooking breathtaking panoramic sparkling glittering Seoul city night skyline and skyscraper lights against dark midnight blue sky in tack sharp f/11 focus, "
                "soft warm ambient architectural uplighting, glowing warm golden patio mood lamps creating dramatic rich depth, crisp details, and cinematic evening intimacy"
            ),
            "voice_pitch": "+4Hz",
            "voice_rate": "+3%"
        },
        12: {
            "topic_id": 12,
            "theme_name": "실물 손절 방지 화보",
            "theme_code": "genuine_look",
            "gender": "female",
            "hook_p1_5s": "사진 보고 설렜다가 실물 보고 도망친 적 있는 사람 손?!",
            "hook_p2_5s": "내 이목구비는 1mm도 안 건드리는 스튜디오 화보가 떴어요!",
            "hook_0_10s": "사진 보고 설렜다가 실물 보고 도망친 적 있는 사람 손?! 내 이목구비는 1mm도 안 건드리는 스튜디오 화보가 떴어요!",
            "app_10_18s": "방구석 형광등 폰카를 30만원 청담 스튜디오 조명과 피부톤으로만 바꿔주니까 실물 보고도 아무도 안 도망쳐요.",
            "cta_18_22s": "본판 100% 보존 인생 화보 완성! 지금 프로필 링크 누르고 3초 만에 무료로 확인해봐!",
            "debate_question": "AI 화보 보정, 어디까지가 매너일까?",
            "hero_copy": "내 본판 100% 보존 스튜디오 화보!",
            "top_header": "청담동 스냅 화보급 AI 보정 • AURA",
            "bottom_step1_title": "가짜 필터 NO! 본판 100% 보존",
            "bottom_step1_sub": "인위적인 틱톡 필터 탈피 • 자연스러운 실사 화보",
            "bottom_step2_title": "청담 스튜디오 감성 즉각 업그레이드",
            "bottom_step2_sub": "매칭률 5배 상승 • 세련되고 사랑스러운 무드",
            "cta_button_text": CTA_BUTTON_TEXT,
            "s2v_motion_prompt": (
                "a gorgeous 25-year-old Korean model sitting gracefully in a designer armchair, looking directly into camera with gentle genuine eye contact, "
                + GOLDEN_MOTION_TALKING_HANDS
            ),
            "char_desc": (
                "an exceptionally gorgeous 25-year-old Korean fashion model with pure and innocent visual beauty, "
                "natural radiant skin with visible fine pores, captivating crystal-clear almond eyes with soft natural lashes, subtle natural blush, "
                "voluminous soft dark brown long straight hair with airy see-through bangs, "
                "wearing an elegant cozy soft-knit cream beige cardigan over a minimalist silk slip top, clean sophisticated editorial photoshoot fashion"
            ),
            "bg_desc": (
                "minimalist high-end natural light photo studio, soft clean white architectural background, "
                "warm directional daylight streaming through sheer linen curtains, chic designer wooden armchair, "
                "subtle dried flower arrangement in ceramic vase on a low oak side table in tack sharp f/11 focus, airy serene high-fashion editorial atmosphere"
            ),
            "voice_pitch": "+3Hz",
            "voice_rate": "+3%"
        },
        13: {
            "topic_id": 13,
            "theme_name": "소개팅 더치페이 팩폭",
            "theme_code": "dutch_pay",
            "gender": "female",
            "hook_p1_5s": "계산대 앞에서 정적 흐를 때, 이 말 한마디로 애프터 확률 3배 갈립니다.",
            "hook_p2_5s": "나랑 가치관 100% 맞는 사람만 골라 만나보세요!",
            "hook_0_10s": "계산대 앞에서 정적 흐를 때, 이 말 한마디로 애프터 확률 3배 갈립니다. 나랑 가치관 100% 맞는 사람만 골라 만나보세요!",
            "app_10_18s": "첫 만남 더치페이, 연락 빈도 12가지 밸런스 게임을 먼저 풀고 통하는 인연만 골라 매칭해주니 싸울 일이 없어요.",
            "cta_18_22s": "생각 통하는 사람만 100% 매칭! 지금 프로필 링크 누르고 3초 만에 무료로 확인해봐!",
            "debate_question": "첫 소개팅 밥값 더치페이, 여러분의 기준은?",
            "hero_copy": "가치관 100% 일치자 우선 매칭!",
            "top_header": "가치관 밸런스 매칭 • AURA",
            "bottom_step1_title": "연락 주기 & 데이트 비용 밸런스 투표",
            "bottom_step1_sub": "더치페이 vs 번갈아 내기 가치관 실시간 확인",
            "bottom_step2_title": "생각 100% 통하는 사람 즉시 연결",
            "bottom_step2_sub": "소비관/연애관 갈등 제로 • 편안한 연애 시작",
            "cta_button_text": CTA_BUTTON_TEXT,
            "s2v_motion_prompt": (
                "a lovely 25-year-old Korean woman sitting across a cafe table, speaking warmly and expressively directly to camera, "
                + GOLDEN_MOTION_TALKING_HANDS
            ),
            "char_desc": (
                "a gorgeous 25-year-old Korean woman with a warm intellectual charm, graceful posture, "
                "warm honey-brown almond eyes with intelligent gentle gaze, soft natural peach makeup, neat dark brown half-up half-down hairstyle, "
                "wearing a chic pastel lavender knit polo top, delicate silver watch, trendy stylish cafe dating fashion, approachable lovely visual"
            ),
            "bg_desc": (
                "cozy sunlit boutique dessert cafe, warm natural wood interior, small marble table with delicate ceramic coffee cups, "
                "lush green indoor plants, warm afternoon sunlight creating soft natural highlights in tack sharp f/11 focus"
            ),
            "voice_pitch": "+4Hz",
            "voice_rate": "+3%"
        },
        14: {
            "topic_id": 14,
            "theme_name": "첫 카톡 읽씹 탈출 (남성)",
            "theme_code": "first_talk_male",
            "gender": "male",
            "hook_p1_5s": "형들 제발 첫마디로 오늘 날씨 좋네요 그만 보내 제발!",
            "hook_p2_5s": "매칭만 되면 뭐 하냐고 첫마디 몰라 12번째 읽씹당한 사람 필독!",
            "hook_0_10s": "형들 제발 첫마디로 오늘 날씨 좋네요 그만 보내 제발! 매칭만 되면 뭐 하냐고 첫마디 몰라 12번째 읽씹당한 사람 필독!",
            "app_10_18s": "상대 프로필과 취향 키워드를 분석해 센스 있는 아이스브레이킹 질문을 AI가 1초 만에 찔러주니까 바로 칼답이 와요.",
            "cta_18_22s": "읽씹 제로 첫 대화 치트키 가동! 지금 프로필 링크 누르고 3초 만에 무료로 확인해봐!",
            "debate_question": "첫마디 AI 추천, 센스일까 사기일까?",
            "hero_copy": "읽씹 제로 첫 대화 치트키!",
            "top_header": "AI 첫대화 답장 비서 • AURA",
            "bottom_step1_title": "읽씹 탈출! 상대 맞춤형 첫인사 생성",
            "bottom_step1_sub": "숨 막히는 단답 대화 원천 차단 • 티키타카 폭발",
            "bottom_step2_title": "AI 대화 코칭 • 애프터 성공률 98%",
            "bottom_step2_sub": "답장 고민 끝 • 센스 넘치는 자연스러운 핑퐁",
            "cta_button_text": CTA_BUTTON_TEXT,
            "s2v_motion_prompt": (
                "a handsome 26-year-old Korean man sitting at a marble cafe table, speaking directly to camera with confident friendly expression, "
                + GOLDEN_MOTION_MALE_HANDS
            ),
            "char_desc": (
                "an exceptionally handsome 26-year-old Korean male model with athletic build, broad masculine shoulders, "
                "clean sculpted jawline and sharp high nose bridge, captivating dark brown eyes with confident friendly gaze, clean textured natural two-block hairstyle, "
                "wearing a clean crisp minimalist white oxford shirt with rolled-up sleeves, stylish masculine cafe dating fashion, charismatic attractive young professional"
            ),
            "bg_desc": (
                "modern upscale architectural cafe with clean polished white marble tables, floor-to-ceiling glass windows with bright daytime natural daylight, "
                "warm minimalist aesthetic interior in tack sharp f/11 focus"
            ),
            "voice_pitch": "-2Hz",
            "voice_rate": "+4%"
        },
        15: {
            "topic_id": 15,
            "theme_name": "AI 얼굴 아우라 팩폭",
            "theme_code": "aura_scan",
            "gender": "female",
            "hook_p1_5s": "친구들이 해주는 외모 칭찬, 솔직히 다 빈말인 거 아시죠?",
            "hook_p2_5s": "폰카 셀카 한 장 넣었더니 내 이목구비 팩폭 진단이 나왔어요!",
            "hook_0_10s": "친구들이 해주는 외모 칭찬, 솔직히 다 빈말인 거 아시죠? 폰카 셀카 한 장 넣었더니 내 이목구비 팩폭 진단이 나왔어요!",
            "app_10_18s": "내 눈빛과 분위기를 분석해서 다정한 여우상 상위 3.8% 진단 카드가 딱 발급되는데 프로필 달았더니 호감도 폭발!",
            "cta_18_22s": "AI 얼굴 분위기 상위 3% 진단! 지금 프로필 링크 누르고 3초 만에 무료로 확인해봐!",
            "debate_question": "AI 매력 진단, 재미있는 놀이일까 자기 객관화일까?",
            "hero_copy": "AI 얼굴 분위기 상위 3% 진단!",
            "top_header": "AI 매력도 진단 리포트 • AURA",
            "bottom_step1_title": "상위 % 아우라 진단 카드 도출",
            "bottom_step1_sub": "Gemini Vision AI 얼굴 분위기 & 매력 분석",
            "bottom_step2_title": "인스타 스토리 자랑용 고화질 카드",
            "bottom_step2_sub": "내 매력 타이틀 확인 • 바이럴 폭발 테스트",
            "cta_button_text": CTA_BUTTON_TEXT,
            "s2v_motion_prompt": (
                "a stylish 25-year-old Korean influencer woman sitting at an espresso bar, speaking charmingly to camera with alluring eye contact, "
                + GOLDEN_MOTION_TALKING_HANDS
            ),
            "char_desc": (
                "a mesmerizingly attractive 25-year-old Korean it-girl with natural chic allure, "
                "captivating expressive almond eyes with subtle elegant eyeliner, trendy textured dark hair with subtle soft ash highlights, authentic clear skin with visible fine skin pores, "
                "wearing a chic form-fitting ribbed knit top, trendy hip Seongsu cafe fashion, alluring stylish influencer aesthetic, looking directly into the camera lens"
            ),
            "bg_desc": (
                "trendy hip espresso bar and modern art gallery cafe in Seongsu-dong, mid-century modern aesthetic interior, "
                "framed contemporary art posters, warm designer lamp glow in tack sharp f/11 focus"
            ),
            "voice_pitch": "+4Hz",
            "voice_rate": "+5%"
        },
        16: {
            "topic_id": 16,
            "theme_name": "동네 자취생 안심 번개",
            "theme_code": "safe_radar",
            "gender": "female",
            "hook_p1_5s": "동네 데이팅 앱 썼다가 집 앞 편의점에서 마주칠 뻔한 썰 푼다!",
            "hook_p2_5s": "집 주소 노출될까 봐 무서워서 못 만났던 자취생들 주목!",
            "hook_0_10s": "동네 데이팅 앱 썼다가 집 앞 편의점에서 마주칠 뻔한 썰 푼다! 집 주소 노출될까 봐 무서워서 못 만났던 자취생들 주목!",
            "app_10_18s": "실제 내 위치를 500m 랜덤 보안 지터링으로 철통 방어해주니까 집 노출 0%로 성수 연남동 동네 친구 당일 번개 가능!",
            "cta_18_22s": "스토킹 걱정 제로 500m 안심 매칭! 지금 프로필 링크 누르고 3초 만에 무료로 확인해봐!",
            "debate_question": "동네 친구 매칭, 500m 지터링 안전한가?",
            "hero_copy": "집 주소 노출 제로 500m 안심 레이더!",
            "top_header": "500m 안심 레이더 • AURA",
            "bottom_step1_title": "간보기 톡 지쳤다면? 500m 안심 매칭",
            "bottom_step1_sub": "내가 원할 때 바로 만나는 동네 편한 친구",
            "bottom_step2_title": "안전한 24시간 지도 퀘스트",
            "bottom_step2_sub": "실시간 러닝·카페 메이트 안심 번개",
            "cta_button_text": CTA_BUTTON_TEXT,
            "s2v_motion_prompt": (
                "an energetic athletic 25-year-old Korean woman sitting at an outdoor park cafe terrace, speaking refreshingly to camera, "
                + GOLDEN_MOTION_TALKING_HANDS
            ),
            "char_desc": (
                "an exceptionally attractive 25-year-old Korean fitness model, natural athletic posture, glowing radiant sun-kissed fair skin with visible fine pores, "
                "bright expressive eyes, sleek high ponytail hairstyle, "
                "wearing a chic rich saturated deep cobalt blue and dark navy form-fitting athletic zip-up top, sleek stylish outdoor activewear, refreshing fitness runner fashion, looking directly into the camera lens"
            ),
            "bg_desc": (
                "sunny outdoor terrace cafe near Seoul Forest park, rustic warm natural brown oak wooden cafe table, "
                "lush green trees and park walking trail visible in background in tack sharp f/11 focus, bright refreshing afternoon natural daylight, pleasant outdoor atmosphere"
            ),
            "voice_pitch": "+3Hz",
            "voice_rate": "+4%"
        }
    }

    @classmethod
    def get_full_scenario(
        cls,
        topic_id: int = 1,
        gender: Optional[str] = None,
        use_ai_script: bool = True
    ) -> Dict[str, Any]:
        """EasyTax의 get_full_scenario와 100% 동일한 인터페이스 반환 (제미나이 100% 자율 창작 대본 지원)"""
        # 🎯 [1~16번 전 슬롯 보존] 1~8번 + 9~16번 EXT 통합 조회
        ALL_SCRIPTS = {**cls.SCRIPTS_22S, **cls.SCRIPTS_22S_EXT}
        if topic_id is not None and topic_id in ALL_SCRIPTS:
            target_id = topic_id
        else:
            target_id = (((topic_id or 1) - 1) % len(ALL_SCRIPTS)) + 1
        s = ALL_SCRIPTS.get(target_id, ALL_SCRIPTS[1])

        effective_gender = gender or s["gender"]

        hook_p1 = s.get("hook_p1_5s", "")
        hook_p2 = s.get("hook_p2_5s", "")
        hook_full = s.get("hook_0_10s", f"{hook_p1} {hook_p2}")
        app_speech = s.get("app_10_18s", "")
        cta_speech = s.get("cta_18_22s", "")
        debate_q = s.get("debate_question", "여러분의 생각은 어떠신가요?")

        # 🤖 [제미나이 2.5 Flash 실시간 자율 대본 생성]
        if use_ai_script:
            try:
                from brands.aura.aura_shorts_script_writer import AuraShortsScriptWriter
                ai_script = AuraShortsScriptWriter().generate_dynamic_script(topic_id=target_id)
                if ai_script:
                    hook_p1 = ai_script.get("hook_p1_5s", hook_p1)
                    hook_p2 = ai_script.get("hook_p2_5s", hook_p2)
                    hook_full = ai_script.get("hook_0_10s", hook_full)
                    app_speech = ai_script.get("app_10_18s", app_speech)
                    cta_speech = ai_script.get("cta_18_22s", cta_speech)
                    debate_q = ai_script.get("debate_question", debate_q)
                    logger.info(f"🎉 [Aura 시나리오] 주제 #{target_id} 제미나이 100% 순수 자율 창작 대본 탑재 완료")
            except Exception as e:
                logger.warning(f"⚠️ [Aura 시나리오] 제미나이 대본 생성 중 예외 발생, 골든 대본 유지: {e}")

        # 🧩 [2단 통대본 정규화] 0~10초 인물 립싱크 통대본 + 10초 이후 나머지 통대본
        #    - 4초/5초 난분할 금지: 아바타가 10.12초 S2V 구간에서 말을 멈추고 노는 현상 원천 차단
        #    - 제미나이 자율 창작 대본이 hook_10s / remainder_speech 를 직접 반환하면 최우선 채택
        hook_10s = (
            ai_script.get("hook_10s") if use_ai_script and ai_script else None
        ) or hook_full
        hook_10s = (hook_10s or "").strip()

        remainder_speech = (
            ai_script.get("remainder_speech") if use_ai_script and ai_script else None
        )
        if not remainder_speech:
            remainder_speech = f"{app_speech} {cta_speech}".strip()
        remainder_speech = (remainder_speech or "").strip()

        # 하위 호환: 기존 speech_hook 소비자는 10초 통대본을 그대로 받음
        hook_full = hook_10s

        full_speech = f"{hook_10s} {remainder_speech}".strip()

        visual_dir = {
            "top_header": s.get("top_header", ""),
            "bottom_step1_title": s.get("bottom_step1_title", ""),
            "bottom_step1_sub": s.get("bottom_step1_sub", ""),
            "bottom_step2_title": s.get("bottom_step2_title", ""),
            "bottom_step2_sub": s.get("bottom_step2_sub", ""),
            "cta_button_text": s.get("cta_button_text", CTA_BUTTON_TEXT)
        }

        return {
            "topic_id": target_id,
            "theme_name": s["theme_name"],
            "theme_code": s["theme_code"],
            "gender": effective_gender,
            "hook_10s": hook_10s,
            "remainder_speech": remainder_speech,
            "speech_hook": hook_10s,
            "speech_hook_part1": hook_p1,
            "speech_hook_part2": hook_p2,
            "speech_app": app_speech,
            "speech_cta": cta_speech,
            "debate_question": debate_q,
            "hero_copy": s.get("hero_copy", ""),
            "full_speech": full_speech,
            "visual_direction": visual_dir,
            "s2v_motion_prompt": s["s2v_motion_prompt"],
            "character_desc": s["char_desc"],
            "background_desc": s["bg_desc"],
            "voice_pitch": s.get("voice_pitch", "+6Hz"),
            "voice_rate": s.get("voice_rate", "+3%")
        }
