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
            "app_10_20s": "보험 리밸런스 5대 레이더 차트로 내 암보험 증권의 유사암 한도를 한눈에 확인할 수 있어요. 건강검진 받기 전에 내 암 보장 범위가 안전한지 무료로 확인해보세요.",
            "hero_copy": "유사암·소액암 보장 범위 즉시 확인!",
            "s2v_motion_prompt": (
                "a sensible 45-year-old Korean woman in cream knit sweater, looking directly into camera with articulate trustworthy eyes, "
                "speaking articulate words with natural lip sync, confident head tilts and subtle hand gestures"
            ),
            "voice_pitch": "+2Hz",
            "voice_rate": "+3%"
        },
        4: {
            "topic_id": 4,
            "theme_name": "뇌·심장 질환 뇌출혈 vs 뇌혈관",
            "theme_code": "brain_vascular",
            "gender": "male",
            "hook_p1_5s": "가장 흔한 뇌경색 환자 열 명 중 여덟 명이 옛날 뇌출혈 특약 때문에 1원도 못 받습니다!",
            "hook_p2_5s": "증권 펴서 뇌출혈이 아니라 뇌혈관질환이라고 적혀 있는지 지금 당장 확인해보세요!",
            "hook_0_10s": "가장 흔한 뇌경색 환자 열 명 중 여덟 명이 옛날 뇌출혈 특약 때문에 1원도 못 받습니다! 증권 펴서 뇌출혈이 아니라 뇌혈관질환이라고 적혀 있는지 지금 당장 확인해보세요!",
            "app_10_20s": "보험 리밸런스 AI가 내 증권에서 협심증과 뇌경색까지 100% 전액 보장되는지 즉시 판독해줍니다. 약관 글자 하나 때문에 피해보지 마시고 지금 바로 점검해보세요.",
            "hero_copy": "뇌경색 100% 보장하는 뇌혈관질환 확인!",
            "s2v_motion_prompt": (
                "a trustworthy 48-year-old Korean family man in charcoal grey sweater, looking directly into camera with sincere honest eyes, "
                "speaking clearly with smooth natural lip sync, precise mouth movements and subtle head nods"
            ),
            "voice_pitch": "+0Hz",
            "voice_rate": "+3%"
        },
        5: {
            "topic_id": 5,
            "theme_name": "종신보험 저축 오해 & 사업비",
            "theme_code": "whole_life_vs_term",
            "gender": "male",
            "hook_p1_5s": "적금인 줄 알고 매달 30만 원씩 붓던 종신보험... 사업비 30% 떼이는 거 알고 계셨나요?",
            "hook_p2_5s": "사망보장은 정기보험으로 월 3만 원에 세팅하고 남은 돈으로 저축하는 게 훨씬 이득입니다!",
            "hook_0_10s": "적금인 줄 알고 매달 30만 원씩 붓던 종신보험... 사업비 30% 떼이는 거 알고 계셨나요? 사망보장은 정기보험으로 월 3만 원에 세팅하고 남은 돈으로 저축하는 게 훨씬 이득입니다!",
            "app_10_20s": "보험 리밸런스 다이어트 계산기로 내 종신보험의 불필요한 적립금을 싹 걷어내보세요. 매달 줄줄 새는 20만 원 아끼고 싶다면 지금 무료로 시뮬레이션해보세요.",
            "hero_copy": "불필요한 적립보험료 싹 걷어내는 다이어트!",
            "s2v_motion_prompt": (
                "a smart 33-year-old Korean male professional in crisp white shirt, looking directly into camera with earnest engaging expression, "
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
            "app_10_20s": "보험 리밸런스에서 내 어린이보험이나 자녀 태아보험의 갱신형 구멍을 3초 만에 찾아드려요. 2030 세대분들은 본인 증권 구멍부터 꼭 한번 점검해보세요.",
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
            "theme_name": "내 보험 숨은 중복 보장 & 새는 보험료 색출",
            "theme_code": "duplicate_coverage_diet",
            "gender": "male",
            "hook_p1_5s": "매달 보험료 20~30만 원씩 나가는데 정작 아플 때 받을 돈은 없다고요?",
            "hook_p2_5s": "증권 뜯어보면 쓸데없이 중복 가입된 특약이랑 갱신형 폭탄 때문에 줄줄 새는 겁니다!",
            "hook_0_10s": "매달 보험료 20~30만 원씩 나가는데 정작 아플 때 받을 돈은 없다고요? 증권 뜯어보면 쓸데없이 중복 가입된 특약이랑 갱신형 폭탄 때문에 줄줄 새는 겁니다!",
            "app_10_20s": "보험 리밸런스 AI가 내 증권에 숨어있는 중복 보장과 누수 금액을 3초 만에 싹 찾아줘요. 전화 없이 익명으로 매달 새는 돈부터 무료로 다이어트해보세요.",
            "hero_copy": "중복 특약과 갱신형 누수 보험료 완벽 색출!",
            "s2v_motion_prompt": (
                "a sharp 38-year-old Korean male professional in neat navy suit, looking directly into camera with intense relatable gaze, "
                "speaking articulately with natural lip sync and dynamic mouth movements, subtle head gestures"
            ),
            "voice_pitch": "+0Hz",
            "voice_rate": "+4%"
        },
        8: {
            "topic_id": 8,
            "theme_name": "원클릭 내 보험 5대 필수 보장 점수 & 공백 진단",
            "theme_code": "coverage_score_gap_diagnosis",
            "gender": "female",
            "hook_p1_5s": "내가 매달 내는 보험, 100점 만점에 과연 몇 점짜리일까요?",
            "hook_p2_5s": "암, 뇌, 심장, 실손 5대 필수 보장에 치명적인 구멍이 있는지 30초 만에 확인해보세요!",
            "hook_0_10s": "내가 매달 내는 보험, 100점 만점에 과연 몇 점짜리일까요? 암, 뇌, 심장, 실손 5대 필수 보장에 치명적인 구멍이 있는지 30초 만에 확인해보세요!",
            "app_10_20s": "보험 리밸런스 5대 보장 레이더로 내 보험의 안전 점수와 부족한 보장 공백을 정밀 진단해드립니다. 상담원 전화 유도 없이 안전하게 내 점수부터 확인해보세요.",
            "hero_copy": "5대 필수 보장 안전 점수 & 공백 즉시 진단!",
            "s2v_motion_prompt": (
                "a poised 39-year-old Korean woman in stylish slate-blue knit sweater, looking directly into camera with genuine reassuring expression, "
                "speaking clearly with smooth natural lip sync, confident head tilts and subtle hand gestures"
            ),
            "voice_pitch": "+2Hz",
            "voice_rate": "+3%"
        }
    }

    def get_full_scenario(self, topic_id: int = 1, gender: Optional[str] = None) -> Dict[str, Any]:
        """주제 ID에 해당하는 실전 2단 숏폼 대본 반환 (1~8번 순환)"""
        preset_key = ((topic_id - 1) % len(self.SCRIPTS_22S)) + 1
        spec = dict(self.SCRIPTS_22S.get(preset_key, self.SCRIPTS_22S[1]))

        spec["topic_id"] = topic_id
        if gender:
            spec["gender"] = gender

        # 2단 실전 음성 텍스트 및 전체 통합 음성
        spec["speech_hook_part1"] = spec["hook_p1_5s"]
        spec["speech_hook_part2"] = spec["hook_p2_5s"]
        spec["speech_hook"] = spec["hook_0_10s"]
        spec["speech_app"] = spec["app_10_20s"]
        spec["speech_cta"] = ""  # 작위적인 CTA 카드 음성 배제 (앱 시연 나레이션으로 자연 완결)
        spec["full_speech"] = f"{spec['speech_hook']} {spec['speech_app']}"

        # 비주얼 디렉션
        spec["visual_direction"] = {
            "brand_name": "insurance",
            "theme_name": spec["theme_name"],
            "theme_code": spec["theme_code"],
            "top_header": f"보험 리밸런스 • {spec['theme_name']}",
            "bottom_step1_title": spec.get("hero_copy", "객관적 5대 보장 AI 분석"),
            "bottom_step1_sub": "특정 보험사 영업 0% • 무료 자가진단",
            "domain_text": "insure-rebalance.vercel.app",
            "search_keyword": "보험 리밸런스"
        }

        return spec
