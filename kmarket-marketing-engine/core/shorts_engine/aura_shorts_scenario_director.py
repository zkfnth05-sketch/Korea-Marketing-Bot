# -*- coding: utf-8 -*-
"""
AuraShortsScenarioDirector - 🎬 [Aura 8대 주제 22초 3단계 숏폼 대본 & 비주얼 오버레이 디렉터]
- 8대 주제별 인물 정의 및 배경 정의와 100% 일치 연동
- Wan 2.2 S2V 립싱크 모션 프롬프트: 1.2m 친밀한 테이블 대화 제스처 (스마트폰 파지 배제)
- 22초 3단계 완결형 단일 스토리라인:
  1) [0초 ~ 10초] 인물 립싱크 킬러 훅 (소개팅 썰, 공감 포인트)
  2) [10초 ~ 18초] 라이브 앱 기능 안내 (탈출 전화, 자막 통화, 50:50 게이트 등)
  3) [18초 ~ 22초] 안심 신뢰 뱃지 & 공식 검색어 촉구 CTA ("네이버에 아우라AI데이팅 검색")
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("AuraShortsScenarioDirector")


class AuraShortsScenarioDirector:
    """Aura 22초 완결형 숏폼 대본 및 화면 오버레이 기획 엔진"""

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
            "cta_18_22s": "합법적으로 칼탈출 성공! 네이버에 아우라AI데이팅 한번 검색해보세요!",
            "top_header": "",
            "bottom_step1_title": "",
            "bottom_step1_sub": "",
            "bottom_step2_title": "",
            "bottom_step2_sub": "",
            "cta_button_text": "네이버에 [아우라AI데이팅] 검색 >",
            "s2v_motion_prompt": (
                "a beautiful 28-year-old Korean office woman sitting across a dinner table, looking directly into camera with expressive authentic eye contact, "
                "leaning forward slightly in a relaxed conversational posture, speaking sincerely with smooth realistic lip sync, subtle natural head tilts, "
                "no phone in hand, natural lifelike motion"
            ),
            "char_desc": (
                "a beautiful 28-year-old Korean office woman, calm low ponytail hairstyle, clear fair skin, "
                "refined subtle makeup, wearing a sophisticated beige silk office blouse and tailored slacks, "
                "elegant and poised appearance with genuine expressive eyes looking directly into the camera lens"
            ),
            "bg_desc": (
                "moody upscale evening bistro and wine restaurant in Cheongdam, soft warm pin-spot table lighting, "
                "antique dark wooden dining table, blurred delicate wine glasses and neat linen napkin in the background"
            )
        },
        2: {
            "topic_id": 2,
            "theme_name": "실시간 자막 통화",
            "theme_code": "live_subtitles",
            "gender": "female",
            "hook_p1_5s": "일본어 1도 못하는데 도쿄 사는 일본인 친구랑 40분 동안 통화한 비결!",
            "hook_p2_5s": "아우라 앱으로 영상통화 켜면 화면 밑에 넷플릭스처럼 실시간 자막이 떠요!",
            "hook_0_10s": "일본어 1도 못하는데 도쿄 사는 일본인 친구랑 40분 동안 통화한 비결! 아우라 앱으로 영상통화 켜면 화면 밑에 넷플릭스처럼 실시간 자막이 떠요!",
            "app_10_18s": "상대방이 일본어로 말하면 한국어 자막이 즉시 번역되고, 내가 한국어로 말하면 일본어 자막으로 넘어가서 외국어 울렁증 있어도 소통 끝!",
            "cta_18_22s": "외국인 친구 생기면 어디 가고 싶으신가요? 언어 장벽 없는 글로벌 만남, 네이버에 아우라AI데이팅 검색해보세요!",
            "top_header": "실시간 4개국어 자막 통화 • AURA",
            "bottom_step1_title": "도쿄 존예녀와 실시간 자막 통화",
            "bottom_step1_sub": "영상통화 중 화면 밑에 영화 자막처럼 실시간 표출",
            "bottom_step2_title": "한·일 실시간 동시 통역 100%",
            "bottom_step2_sub": "외국어 울렁증 제로 • 자연스러운 글로벌 데이트",
            "cta_button_text": "네이버에 [아우라AI데이팅] 검색 >",
            "s2v_motion_prompt": (
                "a lovely 24-year-old Japanese young woman in Tokyo, sitting in a bright room looking directly into camera with charming sweet eye contact, "
                "smiling warmly and speaking naturally with smooth clear lip sync, gentle head nodding, relaxed posture, no phone in hand, lifelike video call motion"
            ),
            "char_desc": (
                "an exceptionally gorgeous 24-year-old Japanese model visual, idol group visual center aesthetic, ethereal soft doll-like beauty, "
                "luminous clear dewy skin, charming expressive doe-like eyes, delicate see-through bangs, "
                "wearing an oversized pastel cream-colored fluffy knit sweater with a minimalist silver necklace, irresistible sweet Tokyo it-girl aura"
            ),
            "bg_desc": (
                "bright airy minimalist Tokyo apartment living room, large sunny window with soft morning daylight, "
                "clean white walls, minimalist natural oak wood furniture, small green houseplant"
            )
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
            "cta_18_22s": "남녀 50:50 정원제, 찬성인가요 반대인가요? 불쾌감 없는 프리미엄 소개팅, 네이버에 아우라AI데이팅 검색해보세요!",
            "top_header": "50:50 황금 성비 청정 라운지 • AURA",
            "bottom_step1_title": "남탕 불쾌감 제로! 50:50 정원제",
            "bottom_step1_sub": "남성 대기열 관리 • 여성 VIP 프리패스 즉시 입장",
            "bottom_step2_title": "수질 100% 보장 • 청정 매너 라운지",
            "bottom_step2_sub": "유령회원 영구 차단 • 격이 다른 소개팅",
            "cta_button_text": "네이버에 [아우라AI데이팅] 검색 >",
            "s2v_motion_prompt": (
                "a stylish sophisticated 28-year-old Korean career woman, sitting in a luxury lounge looking directly into camera with confident friendly eye contact, "
                "speaking smoothly with clear realistic lip sync, poised and composed posture, no phone in hand, natural movement"
            ),
            "char_desc": (
                "a stunning sophisticated 28-year-old Korean career woman, high-fashion cool-tone beauty, sleek chic shoulder-length bob haircut, "
                "flawless glass skin, sharp elegant cheekbones, wearing a luxurious tailored navy blue silk collared shirt, "
                "confident aristocratic posture, exclusive VIP lounge queen aura"
            ),
            "bg_desc": (
                "luxurious high-end hotel lounge and rooftop cafe in Seoul, elegant marble table, floor-to-ceiling panoramic glass windows "
                "with distant city view, refined ambient warm glow lighting"
            )
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
            "cta_18_22s": "이 정도 보정이면 사기다 vs 자기관리다? 내 얼굴 그대로 인생 화보 만들기, 네이버에 아우라AI데이팅 검색해보세요!",
            "top_header": "청담동 스냅 화보급 AI 보정 • AURA",
            "bottom_step1_title": "가짜 필터 NO! 본판 100% 보존",
            "bottom_step1_sub": "인위적인 틱톡 필터 탈피 • 자연스러운 실사 화보",
            "bottom_step2_title": "청담 스튜디오 감성 즉각 업그레이드",
            "bottom_step2_sub": "매칭률 5배 상승 • 세련되고 사랑스러운 무드",
            "cta_button_text": "네이버에 [아우라AI데이팅] 검색 >",
            "s2v_motion_prompt": (
                "a gorgeous 23-year-old Korean young woman, sitting in a bright studio cafe looking directly into camera with radiant gentle eye contact, "
                "smiling naturally and speaking smoothly with authentic lip sync, soft delicate head movements, no phone in hand, beautiful candid motion"
            ),
            "char_desc": (
                "a breathtakingly stunning 23-year-old Korean young woman, pure legendary first-love visual aesthetic, "
                "flowing natural dark silky wavy hair, immaculate luminous glass skin, captivating innocent eyes, delicate facial symmetry, "
                "wearing a soft pastel pink cashmere cardigan over a white silk camisole, timeless editorial beauty photoshoot perfection"
            ),
            "bg_desc": (
                "sunlit aesthetic studio cafe in Seongsu-dong, soft white linen sheer curtains with gentle sunlight streaming through, "
                "vintage wooden designer chair, warm cinematic editorial photoshoot atmosphere"
            )
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
            "cta_18_22s": "첫 만남 더치페이, 여러분의 선택은? 나와 생각 통하는 사람 찾기, 네이버에 아우라AI데이팅 검색해보세요!",
            "top_header": "가치관 밸런스 매칭 • AURA",
            "bottom_step1_title": "연락 주기 & 데이트 비용 밸런스 투표",
            "bottom_step1_sub": "더치페이 vs 번갈아 내기 가치관 실시간 확인",
            "bottom_step2_title": "생각 100% 통하는 사람 즉시 연결",
            "bottom_step2_sub": "소비관/연애관 갈등 제로 • 편안한 연애 시작",
            "cta_button_text": "네이버에 [아우라AI데이팅] 검색 >",
            "s2v_motion_prompt": (
                "a bright friendly 21-year-old Korean college girl, seated comfortably at a brunch table, looking into camera with lively authentic eye contact, "
                "gesturing naturally while talking, smooth realistic lip sync, friendly and expressive, no phone in hand, lifelike motion"
            ),
            "char_desc": (
                "an adorably gorgeous 21-year-old Korean college campus goddess, idol visual with bubbly charismatic charm, "
                "fresh glowing dewy skin, youthful bright expressive eyes, neat loose half-updo hairstyle, "
                "wearing a stylish oversized blue-striped boyfriend button-down shirt, heart-melting natural girlfriend aesthetic"
            ),
            "bg_desc": (
                "cozy outdoor brunch cafe patio in Yeonnam-dong, rustic wooden table with cute brunch plates and iced latte, "
                "pleasant tree shade with dappled natural sunlight"
            )
        },
        6: {
            "topic_id": 6,
            "theme_name": "AI 카톡 비서",
            "theme_code": "ai_icebreaker",
            "gender": "male",
            "hook_p1_5s": "소개팅 첫 카톡에서 '안녕하세요 주말에 뭐해요' 보내면 99% 읽씹 당합니다.",
            "hook_p2_5s": "아우라 AI 카톡 비서 켜면 상대 취향 분석해서 센스 넘치는 첫마디를 써줘요!",
            "hook_0_10s": "소개팅 첫 카톡에서 '안녕하세요 주말에 뭐해요' 보내면 99% 읽씹 당합니다. 아우라 AI 카톡 비서 켜면 상대 취향 분석해서 센스 넘치는 첫마디를 써줘요!",
            "app_10_18s": "상대 프로필을 분석해서 1초 만에 티키타카 터지는 맞춤형 대화를 추천해 주니까 첫 대화 피로도가 완전 제로예요.",
            "cta_18_22s": "소개팅 첫 카톡, 뭐라고 보내시나요? 읽씹 없는 대화 치트키, 네이버에 아우라AI데이팅 검색해보세요!",
            "top_header": "AI 카톡 답장 비서 • AURA",
            "bottom_step1_title": "읽씹 탈출! 상대 맞춤형 첫인사 생성",
            "bottom_step1_sub": "숨 막히는 단답 대화 원천 차단 • 티키타카 폭발",
            "bottom_step2_title": "AI 대화 코칭 • 애프터 성공률 98%",
            "bottom_step2_sub": "답장 고민 끝 • 센스 넘치는 자연스러운 핑퐁",
            "cta_button_text": "네이버에 [아우라AI데이팅] 검색 >",
            "s2v_motion_prompt": (
                "a handsome attractive 27-year-old Korean young man, sitting in a cozy library cafe looking directly into camera with warm trustworthy eye contact, "
                "speaking smoothly with clear realistic lip sync, calm confident posture, no phone in hand, natural handsome motion"
            ),
            "char_desc": (
                "a breathtakingly handsome 27-year-old Korean male lead actor visual, top-tier romantic K-drama male lead aesthetic, "
                "clean stylish dandy haircut, immaculate smooth skin, sharp defined jawline, kind yet deeply charismatic romantic eyes, "
                "wearing a tailored dark navy crewneck wool sweater over a crisp white collared shirt, the ultimate dream boyfriend look"
            ),
            "bg_desc": (
                "modern cozy library book cafe and quiet study lounge, warm amber pendant light hanging above, "
                "rich wooden bookshelves with books in the soft background, calm and trustworthy intellectual atmosphere"
            )
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
            "cta_18_22s": "내 아우라 점수, 몇 점 나올 것 같으신가요? 내 고유의 매력 찾기, 네이버에 아우라AI데이팅 검색해보세요!",
            "top_header": "AI 매력도 진단 리포트 • AURA",
            "bottom_step1_title": "상위 % 아우라 진단 카드 도출",
            "bottom_step1_sub": "Gemini Vision AI 얼굴 분위기 & 매력 분석",
            "bottom_step2_title": "인스타 스토리 자랑용 고화질 카드",
            "bottom_step2_sub": "내 매력 타이틀 확인 • 바이럴 폭발 테스트",
            "cta_button_text": "네이버에 [아우라AI데이팅] 검색 >",
            "s2v_motion_prompt": (
                "a fashionable 25-year-old Korean woman, sitting in a trendy cafe looking directly into camera with charming playful eye contact, "
                "smiling delightfully and speaking smoothly with authentic lip sync, natural subtle head movements, no phone in hand, chic motion"
            ),
            "char_desc": (
                "a mesmerizingly attractive 25-year-old Korean it-girl, top 0.1% captivating feline fox-like eyes with subtle cat-eye eyeliner, "
                "trendy textured dark hair with subtle soft ash highlights, flawless glowing porcelain skin, "
                "wearing a chic form-fitting black ribbed knit top and delicate ear studs, irresistible trendy influencer aura"
            ),
            "bg_desc": (
                "trendy hip espresso bar and modern art gallery cafe in Seongsu-dong, mid-century modern aesthetic interior, "
                "framed contemporary art posters, warm designer lamp glow"
            )
        },
        8: {
            "topic_id": 8,
            "theme_name": "500m 안심 레이더",
            "theme_code": "safe_radar",
            "gender": "female",
            "hook_p1_5s": "동네 친구 만나고 싶은데 집 주소 노출될까 봐 불안해서 망설였던 분들 필독!",
            "hook_p2_5s": "아우라는 내 집 위치 500미터 랜덤 보안으로 완벽하게 지켜줍니다!",
            "hook_0_10s": "동네 친구 만나고 싶은데 집 주소 노출될까 봐 불안해서 망설였던 분들 필독! 아우라는 내 집 위치 500미터 랜덤 보안으로 완벽하게 지켜줍니다!",
            "app_10_18s": "실제 주소 노출 없이 성수동 카페 메이트나 가벼운 러닝 메이트를 안전하게 찾아서 당일 번개로 만날 수 있어요.",
            "cta_18_22s": "동네 산책 메이트, 동성만 가능 vs 이성도 가능? 스토킹 걱정 없는 동네 친구, 네이버에 아우라AI데이팅 검색해보세요!",
            "top_header": "500m 안심 지터링 레이더 • AURA",
            "bottom_step1_title": "스토킹 불안 제로! 500m 안심 지터링",
            "bottom_step1_sub": "실제 주소 노출 0% • 동네 번개 카페 메이트",
            "bottom_step2_title": "안전한 24시간 지도 퀘스트",
            "bottom_step2_sub": "성수/연남 러닝·카페 메이트 안심 매칭",
            "cta_button_text": "네이버에 [아우라AI데이팅] 검색 >",
            "s2v_motion_prompt": (
                "an energetic 25-year-old Korean young woman, sitting at a sunny outdoor terrace looking into camera with bright vibrant eye contact, "
                "speaking refreshingly and naturally with clean lip sync, relaxed confident posture, no phone in hand, active pleasant motion"
            ),
            "char_desc": (
                "an exceptionally stunning 25-year-old Korean fitness goddess visual, glowing radiant sun-kissed fair skin, "
                "bright vibrant eyes with a dazzling gentle smile, sleek high ponytail hairstyle, "
                "wearing a chic pastel lilac sporty athletic windbreaker, breathtaking natural athletic beauty turning heads in the park"
            ),
            "bg_desc": (
                "sunny outdoor terrace cafe near Seoul Forest park, lush green trees and park walking trail visible in background, "
                "bright refreshing afternoon natural daylight, pleasant outdoor atmosphere"
            )
        }
    }

    @classmethod
    def get_full_scenario(
        cls,
        topic_id: int = 1,
        gender: Optional[str] = None
    ) -> Dict[str, Any]:
        """EasyTax의 get_full_scenario와 100% 동일한 인터페이스 반환"""
        norm_id = ((topic_id - 1) % len(cls.SCRIPTS_22S)) + 1
        s = cls.SCRIPTS_22S.get(norm_id, cls.SCRIPTS_22S[1])

        effective_gender = gender or s["gender"]
        full_speech = f"{s['hook_0_10s']} {s['app_10_18s']} {s['cta_18_22s']}"

        visual_dir = {
            "top_header": s["top_header"],
            "bottom_step1_title": s["bottom_step1_title"],
            "bottom_step1_sub": s["bottom_step1_sub"],
            "bottom_step2_title": s["bottom_step2_title"],
            "bottom_step2_sub": s["bottom_step2_sub"],
            "cta_button_text": s["cta_button_text"]
        }

        return {
            "topic_id": norm_id,
            "theme_name": s["theme_name"],
            "theme_code": s["theme_code"],
            "gender": effective_gender,
            "speech_hook": s["hook_0_10s"],
            "speech_hook_part1": s.get("hook_p1_5s", ""),
            "speech_hook_part2": s.get("hook_p2_5s", ""),
            "speech_app": s["app_10_18s"],
            "speech_cta": s["cta_18_22s"],
            "full_speech": full_speech,
            "visual_direction": visual_dir,
            "s2v_motion_prompt": s["s2v_motion_prompt"],
            "character_desc": s["char_desc"],
            "background_desc": s["bg_desc"]
        }
