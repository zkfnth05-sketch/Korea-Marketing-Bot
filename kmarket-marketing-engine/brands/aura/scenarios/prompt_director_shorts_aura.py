# -*- coding: utf-8 -*-
"""
PromptDirectorShortsAura - 🎬 [Aura 데이팅 전용 8대 킬러 주제 숏폼 시나리오 & 프롬프트 디렉터]
- 8대 킬러 주제 순환 (탈출 전화, 자막 통화, 50:50 게이트, 화보 보정, 밸런스 매칭, AI 카톡 비서, 아우라 진단, 500m 레이더)
- 첫 3초 후킹(Hook) + 핵심 본문(Speech Script) + 엔딩 논쟁 유도 멘트 + 공식 검색어 CTA
- Wan 2.1 T2I 마스터컷 프롬프트 및 Wan 2.2 S2V 립싱크 헌법(입 다문 미소, 치아 노출 제로)
- 공식 검색어: '아우라AI데이팅' (붙여쓰기 100% 고정)
"""

from typing import Dict, Any, List, Optional
import random


AURA_SHORTS_TOPICS: Dict[int, Dict[str, Any]] = {
    1: {
        "id": 1,
        "key": "escape_call",
        "title": "소개팅 탈출 전화",
        "killer_weapon": "🚨 긴급 전화 & 탈출 대본",
        "hook_3s": "소개팅 나갔는데 상대가 진짜 상상초월 빌런일 때... 화장실로 튀어서 이 버튼 누르세요.",
        "body_script": "화장실에서 예약 누르면 1분 뒤에 진짜 벨소리 울리고 긴급 대본까지 떠서 합법적으로 탈출 성공!",
        "ending_debate": "이 탈출법, 센스다 vs 너무하다?",
        "ui_type": "escape_call",
        "ui_overlay_text": "🚨 긴급 탈출 전화 가동 중 (화면 대본 표출)",
        "default_voice_gender": "female",
        "cta": "세상에서 가장 안전한 소개팅, 네이버에 아우라AI데이팅 한번 검색해보세요."
    },
    2: {
        "id": 2,
        "key": "live_subtitles",
        "title": "실시간 자막 통화",
        "killer_weapon": "🌐 한·일/글로벌 4개국어 통화",
        "hook_3s": "일본어 1도 못하는 토종 한국인이 도쿄 사는 일본인 존예녀랑 40분 동안 통화한 비결.",
        "body_script": "영상통화 켜면 화면 밑에 넷플릭스처럼 실시간 한국어 자막이 떠서 외국어 울렁증 있어도 대화 끝!",
        "ending_debate": "외국인 친구 생기면 어디 가고 싶음?",
        "ui_type": "live_subtitles",
        "ui_overlay_text": "🌐 실시간 4개국어 라이브 자막 비디오 챗",
        "default_voice_gender": "female",
        "cta": "언어 장벽 없는 리얼 글로벌 만남, 네이버에 아우라AI데이팅 검색해보세요."
    },
    3: {
        "id": 3,
        "key": "vip_gate",
        "title": "50:50 VIP 게이트",
        "killer_weapon": "👑 남성 대기열 vs 여성 프리패스",
        "hook_3s": "소개팅 앱 깔았다가 남자가 90%라 음침한 디엠 쏟아져서 바로 삭제했던 사람 손?",
        "body_script": "남녀 성비 50:50 안 맞으면 남자 가입 대기 걸어버리고 여자는 VIP 프리패스! 물 흐리는 사람 제로예요.",
        "ending_debate": "남녀 50:50 정원제, 찬성 vs 반대?",
        "ui_type": "vip_gate",
        "ui_overlay_text": "👑 남녀 50:50 황금 성비 정원제 라운지",
        "default_voice_gender": "female",
        "cta": "불쾌감 없는 50:50 프리미엄 소개팅, 네이버에 아우라AI데이팅 검색해보세요."
    },
    4: {
        "id": 4,
        "key": "cheongdam_enhance",
        "title": "청담동 화보 보정",
        "killer_weapon": "📸 인조인간 필터 탈피 실사 화보",
        "hook_3s": "소개팅 앱에 틱톡 외계인 필터 올렸다가 첫 만남에서 도망가지 마시고...",
        "body_script": "내 이목구비는 그대로 살리면서 청담동 스냅 화보처럼 세련되고 사랑스러운 무드로 즉각 업그레이드!",
        "ending_debate": "이 정도 보정이면 사기다 vs 자기관리다?",
        "ui_type": "cheongdam_enhance",
        "ui_overlay_text": "📸 청담동 스냅 화보급 AI 프로필 보정",
        "default_voice_gender": "female",
        "cta": "내 얼굴 그대로 인생 화보 만들기, 네이버에 아우라AI데이팅 검색해보세요."
    },
    5: {
        "id": 5,
        "key": "balance_match",
        "title": "가치관 밸런스 매칭",
        "killer_weapon": "⚖️ 더치페이/연락 주기 100% 매칭",
        "hook_3s": "소개팅 첫 만남 더치페이, 여러분은 칼같이 반띵인가요? 아니면 번갈아 내기인가요?",
        "body_script": "연락 주기랑 데이트 비용 밸런스 게임 투표하면 나랑 가치관 100% 똑같은 사람만 연결해 줘요.",
        "ending_debate": "첫 만남 더치페이, 여러분의 선택은?",
        "ui_type": "balance_match",
        "ui_overlay_text": "⚖️ 가치관 밸런스 게임 투표 즉시 100% 매칭",
        "default_voice_gender": "female",
        "cta": "나랑 생각 통하는 사람 찾기, 네이버에 아우라AI데이팅 한번 검색해보세요."
    },
    6: {
        "id": 6,
        "key": "ai_icebreaker",
        "title": "AI 카톡 비서",
        "killer_weapon": "💬 읽씹 없는 첫인사 치트키",
        "hook_3s": "소개팅 첫 카톡에서 '안녕하세요 주말에 뭐해요' 보내면 99% 읽씹 당합니다.",
        "body_script": "AI가 상대방 취향과 가치관을 분석해서 1초 만에 티키타카 터지는 맞춤형 첫인사를 써줘요.",
        "ending_debate": "소개팅 첫 카톡, 뭐라고 보내시나요?",
        "ui_type": "ai_icebreaker",
        "ui_overlay_text": "💬 AI 맞춤형 첫 대화 추천 (Icebreaker)",
        "default_voice_gender": "female",
        "cta": "읽씹 없는 대화 치트키, 네이버에 아우라AI데이팅 검색해보세요."
    },
    7: {
        "id": 7,
        "key": "aura_diagnosis",
        "title": "AI 아우라 진단",
        "killer_weapon": "✨ 외모/성향 상위 % 분석",
        "hook_3s": "요즘 인스타 스토리에서 난리 난 내 얼굴 아우라 매력 점수 테스트 해보셨나요?",
        "body_script": "셀카 한 장 넣었더니 AI가 상위 3% 다정한 여우상이라고 분석해 주고 매력 카드까지 뽑아줬어요!",
        "ending_debate": "내 아우라 점수, 몇 점 나올 것 같음?",
        "ui_type": "aura_diagnosis",
        "ui_overlay_text": "✨ Gemini Vision AI '나의 아우라' 매력 진단",
        "default_voice_gender": "female",
        "cta": "내 고유의 매력 점수 찾기, 네이버에 아우라AI데이팅 검색해보세요."
    },
    8: {
        "id": 8,
        "key": "safe_radar",
        "title": "500m 안심 레이더",
        "killer_weapon": "🗺️ 스토킹 방지 동네 번개",
        "hook_3s": "동네 친구 만나고 싶은데 집 주소 노출될까 봐 불안해서 망설였던 분들 필독!",
        "body_script": "내 집 위치는 500미터 랜덤 보안으로 꽁꽁 숨기고 성수동 카페 메이트를 안전하게 찾았어요.",
        "ending_debate": "동네 산책 메이트, 동성만 vs 이성도 가능?",
        "ui_type": "safe_radar",
        "ui_overlay_text": "🗺️ 500m 안심 지터링 보안 24시간 지도 퀘스트",
        "default_voice_gender": "female",
        "cta": "스토킹 걱정 없는 동네 친구, 네이버에 아우라AI데이팅 검색해보세요."
    }
}


class PromptDirectorShortsAura:
    """AURA 8대 킬러 주제 전용 숏폼 시나리오 & 프롬프트 디렉터"""

    BRAND_NAME = "Aura AI 데이팅"
    OFFICIAL_SEARCH_KEYWORD = "아우라AI데이팅"
    LANDING_URL = "https://aura-ai-dating.vercel.app/lounge"

    @classmethod
    def get_topic(cls, topic_id: int) -> Dict[str, Any]:
        """주제 ID(1~8)에 해당하는 시나리오 반환 (범위 외일 경우 모듈러 1~8)"""
        norm_id = ((topic_id - 1) % len(AURA_SHORTS_TOPICS)) + 1
        return AURA_SHORTS_TOPICS.get(norm_id, AURA_SHORTS_TOPICS[1])

    @classmethod
    def get_all_topics(cls) -> List[Dict[str, Any]]:
        """전체 8개 주제 리스트 반환"""
        return [AURA_SHORTS_TOPICS[i] for i in range(1, 9)]

    @classmethod
    def build_speech_script(cls, topic_id: int) -> str:
        """숏폼 음성 합성(TTS)용 전체 발화 스크립트 결합 (후킹 + 본문 + 엔딩 논쟁 + CTA)"""
        t = cls.get_topic(topic_id)
        # 숏폼 최적 호흡 (약 15~20초 분량)
        return f"{t['hook_3s']} {t['body_script']} {t['ending_debate']} {t['cta']}"

    @classmethod
    def get_t2i_prompt(
        cls,
        topic_id: int,
        persona: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Wan 2.1 T2I용 고화질 인물 마스터컷 프롬프트 생성:
        - 페르소나의 성별, 외모, 연령, 패션, 배경 연동
        - 스마트폰 정면 파지 구도 (스마트폰 화면이 정면 카메라를 향함)
        - 🤐 S2V 립싱크 헌법: 입 다문 편안한 미소 (lips naturally closed together, no teeth showing)
        - 아이폰 15 Pro 무필터 실사 락
        """
        t = cls.get_topic(topic_id)
        char_desc = persona.get("char_desc", "a charming Korean young woman in her 20s")
        bg_desc = persona.get("bg_desc", "modern warm cafe interior with soft lighting")

        # 아이폰 15 Pro 3.5m 원거리 카우보이 화각
        iphone_framing = (
            "authentic candid snapshot shot on iPhone 15 Pro, casual everyday mobile phone photo taken by a friend, "
            "photographed from 3.0 meters away with natural smartphone camera lens, "
            "wide environmental cowboy shot, waist-up view showing the complete upper body from head down past hips and belt, "
            "natural 8-head tall realistic adult human body proportions, natural slender neck and shoulders, "
            "subject occupies only about 35% to 40% of the vertical frame with generous open room space and surrounding interior around, "
            "tack sharp deep pan-focus across the entire background (f/11 aperture) with all background details completely in sharp crisp focus with zero blur, "
        )

        closed_mouth_mandate = (
            "lips completely closed together, mouth gently shut, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, "
            "calm confident pleasant gentle resting smile, looking directly into the camera lens with authentic trustworthy eye contact ready to speak. "
        )

        pos = (
            f"masterpiece, best quality, ultra-photorealistic portrait, {iphone_framing} of {char_desc}. "
            f"sitting comfortably in {bg_desc}, "
            f"holding a modern sleek smartphone vertically in one hand at chest and waist level facing directly forward towards camera lens. "
            f"{closed_mouth_mandate} "
            f"Sharp focus on her/his clear face, delicate natural skin texture with subtle real pores, realistic hair strands, 8k uhd, cinematic film still, "
            f"natural everyday room ambient lighting, realistic mobile phone camera sensor capture, authentic candid mobile photo, NO beauty filter."
        )

        neg = (
            "open mouth, showing teeth, smiling wide with mouth open, parted lips, talking mouth, grinning with teeth, "
            "deformed fingers, extra digits, missing fingers, bad hands, blurry screen, tilted phone, "
            "overexposed, cartoon, 3d render, anime, plastic skin, dull, dark, lowres, text, watermark, "
            "close-up, extreme close-up, cropped torso, bust shot, headshot, zoomed-in, person filling frame"
        )

        return {"positive": pos, "negative": neg}
