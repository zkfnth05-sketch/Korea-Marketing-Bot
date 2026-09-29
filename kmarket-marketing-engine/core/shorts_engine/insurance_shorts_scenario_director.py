# -*- coding: utf-8 -*-
"""
InsuranceShortsScenarioDirector - 🎬 [보험 리밸런스 22초 실전 2단 직결 숏폼 대본 디렉터]
- 심의 100% 프리패스 (특정 보험사/상품 0% 언급, 팩트 기반 약관 원리 분석, 자가점검 유도)
- 군더더기 없는 실전 2단 직결 구조:
  1) [0초 ~ 10초] 실제 타깃 연령 일반인 인물 립싱크 킬러 훅 (내돈내산 현실 썰)
  2) [10초 ~ 20초] 우리 앱 아이프레임 실제 시연 및 무료 점검 해결책 나레이션
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("InsuranceShortsScenarioDirector")


class InsuranceShortsScenarioDirector:
    """🛡️ 보험 리밸런스 8대 국민 보험 22초 완결형 숏폼 대본 엔진"""

    SCRIPTS_22S = {
        1: {
            "topic_id": 1,
            "theme_name": "실손의료비 4세대 전환 손익",
            "theme_code": "silbi_gen4",
            "gender": "female",
            "hook_p1_5s": "병원 일 년에 한두 번 갈까 말까인데 옛날 실비보험 매달 5만 원 넘게 내고 계신가요?",
            "hook_p2_5s": "저도 꼬박 내다가 이번에 4세대로 바꾸고 월 1만 2천 원으로 줄였습니다!",
            "hook_0_10s": "병원 일 년에 한두 번 갈까 말까인데 옛날 실비보험 매달 5만 원 넘게 내고 계신가요? 저도 꼬박 내다가 이번에 4세대로 바꾸고 월 1만 2천 원으로 줄였습니다!",
            "app_10_20s": "보험 리밸런스에서는 전화번호 없이 익명으로 대한민국 모든 보험사 상품을 0.1초 만에 비교해 줘요. 내 나이에 딱 맞는 4세대 전환 손익부터 무료로 확인해보세요.",
            "hero_copy": "병원 안 가면 월 1만원대로 다이어트!",
            "s2v_motion_prompt": (
                "a relatable 42-year-old Korean woman in clean stylish civilian casual clothes sitting comfortably in a bright room, looking directly into camera with genuine friendly expression, "
                "speaking clearly with precise lip sync and articulate mouth motion, gentle head nodding, subtle hand gestures explaining facts, "
                "no phone in hand, confident trustworthy motion"
            ),
            "voice_pitch": "+2Hz",
            "voice_rate": "+3%"
        },
        2: {
            "topic_id": 2,
            "theme_name": "운전자보험 1만원의 법칙",
            "theme_code": "driver_insurance",
            "gender": "male",
            "hook_p1_5s": "자동차보험 말고 운전자보험에 매달 3~4만 원씩 내고 계신 분들 진짜 많죠?",
            "hook_p2_5s": "벌금, 변호사, 합의금 딱 3개만 챙기면 월 1만 3천 원이면 끝납니다!",
            "hook_0_10s": "자동차보험 말고 운전자보험에 매달 3~4만 원씩 내고 계신 분들 진짜 많죠? 벌금, 변호사, 합의금 딱 3개만 챙기면 월 1만 3천 원이면 끝납니다!",
            "app_10_20s": "보험 리밸런스에서 내 운전자보험 증권 스캔해보면 쓸데없이 껴있는 중복 특약을 다 찾아줘요. 운전하시는 분들은 불필요한 지출 다이어트 꼭 한번 해보세요.",
            "hero_copy": "필수 3대 특약으로 월 13,000원 완성!",
            "s2v_motion_prompt": (
                "a sharp 36-year-old Korean male commuter driver standing on a modern city street, looking directly into camera with honest relatable gaze, "
                "speaking articulately with realistic mouth movements and natural lip synchronization, subtle head nodding, calm upper body posture in urban city background"
            ),
            "voice_pitch": "+0Hz",
            "voice_rate": "+4%"
        },
        3: {
            "topic_id": 3,
            "theme_name": "암보험 일반암 vs 유사암 진실",
            "theme_code": "cancer_coverage",
            "gender": "female",
            "hook_p1_5s": "암보험 5천만 원 든 줄 알았는데 갑상선암 걸리면 5백만 원만 나온다는 사실 아셨나요?",
            "hook_p2_5s": "소액암이랑 유사암 분류 기준 모르면 암 걸리고도 보험금 10%밖에 못 받아요!",
            "hook_0_10s": "암보험 5천만 원 든 줄 알았는데 갑상선암 걸리면 5백만 원만 나온다는 사실 아셨나요? 소액암이랑 유사암 분류 기준 모르면 암 걸리고도 보험금 10%밖에 못 받아요!",
            "app_10_20s": "보험 리밸런스에서 내가 필요한 암 진단금을 고르고 간단한 조건만 넣으면, 국내 34개 보험사의 암보험을 실시간으로 한눈에 비교 분석해 줍니다!",
            "hero_copy": "내가 원하는 진단금으로 34개 암보험 실시간 비교!",
            "s2v_motion_prompt": (
                "a sensible 45-year-old Korean woman in cream knit sweater, looking directly into camera with articulate trustworthy eyes, "
                "speaking articulate words with natural lip sync, confident head tilts and subtle hand gestures"
            ),
            "voice_pitch": "+2Hz",
            "voice_rate": "+3%"
        },
        4: {
            "topic_id": 4,
            "theme_name": "뇌경색 100% 뇌혈관질환 최저가 다이렉트 비교",
            "theme_code": "brain_vascular",
            "gender": "male",
            "hook_p1_5s": "뇌경색이랑 협심증 100% 보장받는 뇌혈관 보험, 아직도 아는 사람 통해서 비싸게 드시나요?",
            "hook_p2_5s": "내 나이 생년월일만 넣으면 전 보험사 최저가 순위가 바로 나옵니다!",
            "hook_0_10s": "뇌경색이랑 협심증 100% 보장받는 뇌혈관 보험, 아직도 아는 사람 통해서 비싸게 드시나요? 내 나이 생년월일만 넣으면 전 보험사 최저가 순위가 바로 나옵니다!",
            "app_10_20s": "보험 리밸런스에서 나이와 성별만 클릭하면, 뇌혈관과 허혈성 심장질환 보장 기준 국내 33개 보험사 실시간 보험료를 1초 만에 비교해 줍니다. 불필요한 영업 전화 없이 최저가 견적을 직접 확인해보세요.",
            "hero_copy": "뇌경색 100% 보장하는 뇌혈관보험 최저가 찾기!",
            "s2v_motion_prompt": (
                "a trustworthy 48-year-old Korean family man in stylish neat casual daily clothes, looking directly into camera with sincere honest eyes, "
                "speaking clearly with smooth natural lip sync, precise mouth movements and subtle head nods"
            ),
            "voice_pitch": "+0Hz",
            "voice_rate": "+3%"
        },
        5: {
            "topic_id": 5,
            "theme_name": "아는 사람 부탁으로 가입한 보험 손익 분석",
            "theme_code": "whole_life_vs_term",
            "gender": "male",
            "hook_p1_5s": "아는 사람 부탁으로 가입했던 보험, 매달 돈만 나가고 무슨 보장인지도 모르셨죠?",
            "hook_p2_5s": "내 나이만 넣으면 얼마를 손해보고 있는지 바로 알려줍니다!",
            "hook_0_10s": "아는 사람 부탁으로 가입했던 보험... 매달 돈만 나가고 무슨 보장인지도 모르셨죠? 내 나이만 넣으면 얼마를 손해보고 있는지 바로 알려줍니다!",
            "app_10_20s": "보험 리밸런스에서는 전화번호 없이 익명으로 국내 34개 보험사의 최저가를 1초 만에 비교해 드려요. 내 나이와 조건에 맞춰 매달 줄줄 새는 불필요한 보험료부터 지금 바로 확인해보세요.",
            "hero_copy": "아는 사람 부탁 보험, 매달 새는 돈 1초 색출!",
            "s2v_motion_prompt": (
                "a sincere, polite, and handsome 33-year-old Korean male professional in crisp white oxford shirt, looking directly into camera with genuine engaging expression, "
                "speaking clearly with smooth natural lip sync, articulate facial articulation, subtle posture shifts"
            ),
            "voice_pitch": "+1Hz",
            "voice_rate": "+4%"
        },
        6: {
            "topic_id": 6,
            "theme_name": "어린이·어른이 100세 만기 리모델링",
            "theme_code": "child_to_adult",
            "gender": "female",
            "hook_p1_5s": "부모님이 100세 만기로 들어주셨던 어린이보험... 서른 살 넘어서 증권 뜯어보고 깜짝 놀랐습니다!",
            "hook_p2_5s": "옛날 보험이라 갱신형에 뇌출혈만 가득해서 비갱신형으로 깔끔하게 리모델링했어요!",
            "hook_0_10s": "부모님이 100세 만기로 들어주셨던 어린이보험... 서른 살 넘어서 증권 뜯어보고 깜짝 놀랐습니다! 옛날 보험이라 갱신형에 뇌출혈만 가득해서 비갱신형으로 깔끔하게 리모델링했어요!",
            "app_10_20s": "보험 리밸런스에서는 생년월일과 성별만 직접 넣으면, 국내 모든 보험사의 비갱신형 상품을 1초 만에 비교해 드려요. 갱신 없이 끝까지 안전한 최저가 견적을 전화번호 없이 무료로 확인해보세요.",
            "hero_copy": "갱신형 구멍 찾아내고 비갱신형 리모델링!",
            "s2v_motion_prompt": (
                "a bright 32-year-old Korean young mother in cozy ivory sweater, looking directly into camera with relatable friendly demeanor, "
                "speaking naturally with realistic lip sync and dynamic mouth movements, gentle nodding"
            ),
            "voice_pitch": "+3Hz",
            "voice_rate": "+4%"
        },
        7: {
            "topic_id": 7,
            "theme_name": "내 보험 정밀 비교 & 새는 보험료 다이어트",
            "theme_code": "duplicate_coverage_diet",
            "gender": "female",
            "hook_p1_5s": "매달 보험료 20~30만 원씩 비싸게 내고 계신가요?",
            "hook_p2_5s": "지금 내는 보험보다 보험료는 훨씬 싸고 보장은 더 든든한 상품이 정말 많습니다!",
            "hook_0_10s": "매달 보험료 20~30만 원씩 비싸게 내고 계신가요? 지금 내는 보험보다 보험료는 훨씬 싸고 보장은 더 든든한 상품이 정말 많습니다!",
            "app_10_20s": "보험 리밸런스에서는 전화번호 없이 익명으로, 내가 가진 보험보다 더 저렴하고 보장이 든든한 국내 34개사 최적의 상품을 1초 만에 정밀 비교해 드려요. 매달 줄줄 새는 보험료부터 지금 바로 다이어트해보세요.",
            "hero_copy": "내 보험보다 더 싸고 든든한 34개사 최저가 정밀 비교!",
            "s2v_motion_prompt": (
                "a sharp and sensible 37-year-old Korean woman in clean stylish smart-casual daily outfit, looking directly into camera with articulate relatable gaze, "
                "speaking clearly with smooth natural lip sync and dynamic mouth movements, subtle head gestures, natural confident posture"
            ),
            "voice_pitch": "+2Hz",
            "voice_rate": "+4%"
        },
        8: {
            "topic_id": 8,
            "theme_name": "AI 보험료 역추정 비교 & 가성비 리모델링",
            "theme_code": "coverage_score_gap_diagnosis",
            "gender": "female",
            "hook_p1_5s": "매달 내는 보험료, 과연 제값 하고 있을까요?",
            "hook_p2_5s": "같은 돈 내고 보장은 더 받거나, 똑같은 보장에 보험료를 아주 많이 줄일 수 있습니다!",
            "hook_0_10s": "매달 내는 보험료, 과연 제값 하고 있을까요? 같은 돈 내고 보장은 더 받거나, 똑같은 보장에 보험료를 아주 많이 줄일 수 있습니다!",
            "app_10_20s": "보험 리밸런스 AI가 내 보험료를 역추정해서, 같은 금액에 보장이 훨씬 넓은 보험과 똑같은 보장에 더 저렴한 상품을 1초 만에 찾아드려요. 전화번호 없이 최적의 비교 견적을 지금 바로 확인해보세요.",
            "hero_copy": "같은 가격엔 더 큰 보장, 같은 보장엔 더 싼 보험!",
            "s2v_motion_prompt": (
                "a poised 39-year-old Korean woman in clean stylish smart-casual daily outfit, looking directly into camera with genuine reassuring expression, "
                "speaking clearly with smooth natural lip sync, confident head tilts and subtle hand gestures"
            ),
            "voice_pitch": "+2Hz",
            "voice_rate": "+3%"
        }
    }

    def get_full_scenario(self, topic_id: int = 1, gender: Optional[str] = None, use_ai_script: bool = True) -> Dict[str, Any]:
        """주제 ID에 해당하는 22초 실전 아나운서 숏폼 대본 반환 (1~8번 순환, 제미나이 2.5 자율 집필 탑재)"""
        norm_id = ((topic_id - 1) % len(self.SCRIPTS_22S)) + 1
        s = dict(self.SCRIPTS_22S.get(norm_id, self.SCRIPTS_22S[1]))
        effective_gender = gender or s.get("gender", "female")

        hook_p1 = s.get("hook_p1_5s", "")
        hook_p2 = s.get("hook_p2_5s", "")
        hook_full = s.get("hook_0_10s", f"{hook_p1} {hook_p2}")
        app_speech = s.get("app_10_20s", "")
        cta_speech = s.get("cta_18_22s", "")
        hero_copy = s.get("hero_copy", "객관적 5대 보장 AI 분석")
        debate_q = s.get("debate_question", "내 보험 보장 범위는 안전할까?")

        # 🤖 [제미나이 2.5 Flash 실시간 자율 대본 생성 (매번 참신한 아나운서 멘트)]
        if use_ai_script:
            try:
                from brands.insurance.insurance_shorts_script_writer import InsuranceShortsScriptWriter
                ai_script = InsuranceShortsScriptWriter().generate_dynamic_script(topic_id=norm_id)
                if ai_script:
                    hook_p1 = ai_script.get("hook_p1_5s", hook_p1)
                    hook_p2 = ai_script.get("hook_p2_5s", hook_p2)
                    hook_full = ai_script.get("hook_0_10s", hook_full)
                    app_speech = ai_script.get("app_10_20s", app_speech)
                    cta_speech = ai_script.get("cta_18_22s", cta_speech)
                    hero_copy = ai_script.get("hero_copy", hero_copy)
                    debate_q = ai_script.get("debate_question", debate_q)
                    logger.info(f"🎉 [보험 시나리오] 주제 #{norm_id} 제미나이 100% 순수 자율 창작 아나운서 대본 탑재 완료")
            except Exception as e:
                logger.warning(f"⚠️ [보험 시나리오] 제미나이 대본 생성 중 예외 발생, 골든 대본 유지: {e}")

        full_speech = f"{hook_full} {app_speech} {cta_speech}".strip()

        visual_dir = {
            "brand_name": "insurance",
            "theme_name": s["theme_name"],
            "theme_code": s["theme_code"],
            "top_header": f"보험 리밸런스 • {s['theme_name']}",
            "bottom_step1_title": hero_copy,
            "bottom_step1_sub": "특정 보험사 영업 0% • 무료 자가진단",
            "domain_text": "insure-rebalance.vercel.app",
            "search_keyword": "보험 리밸런스"
        }

        return {
            "topic_id": norm_id,
            "theme_name": s["theme_name"],
            "theme_code": s["theme_code"],
            "gender": effective_gender,
            "speech_hook": hook_full,
            "speech_hook_part1": hook_p1,
            "speech_hook_part2": hook_p2,
            "speech_app": app_speech,
            "speech_cta": cta_speech,
            "debate_question": debate_q,
            "hero_copy": hero_copy,
            "full_speech": full_speech,
            "visual_direction": visual_dir,
            "s2v_motion_prompt": s["s2v_motion_prompt"],
            "character_desc": s.get("char_desc", ""),
            "background_desc": s.get("bg_desc", ""),
            "voice_pitch": s.get("voice_pitch", "+2Hz"),
            "voice_rate": s.get("voice_rate", "+5%")
        }
