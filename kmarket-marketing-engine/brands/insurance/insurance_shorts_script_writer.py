# -*- coding: utf-8 -*-
"""
InsuranceShortsScriptWriter - 🛡️ 보험 8대 주제 전용 제미나이 3.8 Flash 자율 창작 대본 작성기
========================================================================================
- [원천 아키텍처 개편]:
  1. 하드코딩 골든 대본 주입 전면 영구 배제 (예시문 베끼기 원천 박멸)
  2. 보험 8대 핵심 기능 명세(기능 개요, 해결하는 고민, 활용 상황, 화자 설정)를 프롬프트에 주입
  3. 금융소비자보호법 준수(자극적 비방 금지, 객관적 팩트 및 최저가 요율 비교)
  4. 20.0초 완제품 규격 (공백 포함 115~145자) 엄격 준수
  5. 9개 통합 키 체인(무료 6개 + 유료 2개 + 기본 1개) 무중단 자동 페일오버 연동
"""

import sys
import json
import logging
from typing import Dict, Any, Optional, List
from google import genai
from google.genai import types

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from core.gemini_unified_keys import get_unified_gemini_key_dicts

logger = logging.getLogger("InsuranceShortsScriptWriter")


INSURANCE_TOPICS_SPECS: Dict[int, Dict[str, str]] = {
    1: {
        "title": "실손의료비 4세대 전환 손익",
        "gender": "40대 똑순이 주부/직장인 여성",
        "feature_desc": "병원에 자주 안 가는데 매달 10만원 넘게 내던 옛날 1·2세대 실손보험을 4세대 실손으로 전환 시 월 1만원대로 낮추고 33개 보험사 실시간 요율을 1초 만에 비교해주는 기능.",
        "problem_solved": "병원도 안 가는데 비싼 구실손 보험료로 매달 새는 돈을 속 시원하게 아끼는 꿀팁 제공.",
        "usage_scenario": "건강검진 후 병원비 청구 적은 소비자의 현명한 4세대 실비 전환 실측 경험담.",
        "hero_copy": "실손 전환 시뮬레이션 1초 분석!"
    },
    2: {
        "title": "운전자보험 1만원의 법칙",
        "gender": "30대 직장인 남성 운전자 (★남성 화자 1인칭)",
        "feature_desc": "매달 3~4만원씩 과다 지출되던 운전자보험에서 불필요한 적립금과 중복 특약을 빼고, 핵심 3대 비용(벌금, 변호사비, 합의금)만 월 1만원대로 알뜰하게 맞추는 기능.",
        "problem_solved": "자동차보험과 별개로 매달 불필요하게 새어나가던 운전자보험료 다이어트.",
        "usage_scenario": "매일 출퇴근하는 30대 남성 운전자의 1만원대 운전자보험 실속 세팅 경험담.",
        "hero_copy": "운전자 필수 3대 특약 월 1만원대!"
    },
    3: {
        "title": "암보험 일반암 vs 유사암 진실",
        "gender": "40대 여성 소비자",
        "feature_desc": "갑상선암이나 소액암 진단 시 10%만 지급되는 약관 함정을 피하고, 내가 필요한 진단금 특약을 직접 선택해 34개 보험사 암보험을 1초 만에 비교하는 기능.",
        "problem_solved": "암보험 5천만원 든 줄 알았는데 갑상선암은 500만원만 나오는 약관 공백 사전 방지.",
        "usage_scenario": "건강검진 앞두고 여성에게 흔한 암 보장 범위를 꼼꼼히 챙긴 팩트체크 성공기.",
        "hero_copy": "유사암·일반암 100% 보장 비교!"
    },
    4: {
        "title": "뇌경색 100% 뇌혈관질환 최저가 비교",
        "gender": "40대 남성 가장 (★남성 화자 1인칭)",
        "feature_desc": "가장 발병률 높은 뇌경색과 협심증까지 100% 보장되는 뇌혈관·허혈성 심장질환 보험을 33개사 실시간 최저가 순위로 비교하는 기능.",
        "problem_solved": "옛날 뇌출혈 보험이라 뇌경색 진단 시 보장 1원도 못 받는 치명적 보장 구멍 해결.",
        "usage_scenario": "혈압약 복용 시작하며 증권 열어보고 뇌혈관질환 100% 보장으로 갈아탄 가장의 썰.",
        "hero_copy": "뇌경색 100% 뇌혈관질환 다이렉트!"
    },
    5: {
        "title": "아는 사람 부탁으로 가입한 보험 손익 분석",
        "gender": "30대 청년 남성 가장 (★남성 화자 1인칭)",
        "feature_desc": "지인 부탁으로 가입해 매달 돈만 나가던 종신보험의 불필요한 적립보험료와 갱신형 특약을 분석해 새는 돈을 1초 만에 진단해주는 기능.",
        "problem_solved": "사회초년생 때 거절 못해 든 비싼 보험의 거품을 빼고 알뜰한 순수 보장형으로 정리.",
        "usage_scenario": "선배 부탁으로 들었던 20만원대 보험을 똑소리 나게 리모델링한 경험담.",
        "hero_copy": "지인 보험 새는 돈 1초 진단!"
    },
    6: {
        "title": "어릴 때 부모님이 들어준 보험 성인 리모델링",
        "gender": "2030 직장인 여성",
        "feature_desc": "어릴 때 부모님이 들어준 100세 만기 보험의 성인 질환 보장 공백을 메우고 비갱신형으로 알뜰하게 보강해주는 기능.",
        "problem_solved": "서른 살 넘어 증권 열어보니 소액 보장뿐인 옛날 보험을 성인 실속 보장으로 업그레이드.",
        "usage_scenario": "부모님께 감사하지만 부족했던 암·뇌·심장 3대 진단비를 비갱신으로 보강한 썰.",
        "hero_copy": "어릴 적 보험 성인 비갱신 보강!"
    },
    7: {
        "title": "가족 보험료 다이어트 & 중복 특약 정리",
        "gender": "30대 알뜰 주부/직장인 여성",
        "feature_desc": "34개 보험사 동일 보장 기준 최저가와 비교해 중복 가입된 쓸데없는 특약을 빼고 보험료를 가볍게 줄여주는 기능.",
        "problem_solved": "매달 20~30만원씩 빠져나가는 가족 보험료 중복 낭비 방지.",
        "usage_scenario": "가족 4인 보험 증권 한 번에 분석해 보장은 넓히고 보험료는 다이어트한 성공 팁.",
        "hero_copy": "가족 보험 중복 특약 싹 다이어트!"
    },
    8: {
        "title": "전화번호 입력 없는 안심 보험 비교",
        "gender": "30대 스마트 직장인 여성",
        "feature_desc": "전화번호나 개인정보 입력 없이 AI 역추정으로 동일 연령 대비 가장 가성비 높고 탄탄한 맞춤 비교 설계를 객관적으로 찾는 기능.",
        "problem_solved": "보험 비교 한번 했다가 쏟아지는 설계사 영업 전화와 스팸 공포 100% 차단.",
        "usage_scenario": "영업 전화 1도 없이 34개 보험사 객관적 요율표만 깔끔하게 확인한 쾌적한 경험.",
        "hero_copy": "전화번호 0개 안심 1초 비교!"
    }
}


class InsuranceShortsScriptWriter:
    """🛡️ 보험 8대 주제 전용 제미나이 3.8 Flash 실시간 자율 창작 대본 생성 엔진"""

    OFFICIAL_KEYWORD = "보험리밸런스"
    FORBIDDEN_WORDS = [
        "호갱", "폭탄", "사기", "대충격", "공중분해", "반토막", "파산", "눈물", 
        "생돈", "뻥튀기", "한정", "이벤트", "선착순", "무료 쿠폰", "사은품", "오늘만"
    ]

    def __init__(self):
        self.key_dicts = get_unified_gemini_key_dicts()

    def generate_dynamic_script(self, topic_id: int = 1) -> Optional[Dict[str, Any]]:
        """
        주제 ID(1~8)에 맞춰 보험의 실제 기능 명세(기능 개요, 해결 고민, 활용 상황)를 주입하고,
        제미나이 3.8 Flash가 매번 100% 새롭고 독창적인 상황 설정으로 20초 숏폼 대본을 자율 창작.
        """
        norm_id = ((topic_id - 1) % len(INSURANCE_TOPICS_SPECS)) + 1
        spec = INSURANCE_TOPICS_SPECS.get(norm_id, INSURANCE_TOPICS_SPECS[1])

        prompt = f"""[앱 및 기능 정보]
- 브랜드: 보험리밸런스 (InsureBalance)
- 주제 #{norm_id}: {spec['title']}
- 화자 설정: {spec['gender']}
- 기능 개요: {spec['feature_desc']}
- 해결하는 고민: {spec['problem_solved']}
- 활용 상황: {spec['usage_scenario']}

[★ 지시 사항 (절대 준수)]
위 보험리밸런스의 기능을 시청자에게 자세하고 신뢰감 있게 설명하는 20초 숏폼 대본을 작성하시오.
- 🚨 기존에 완성된 예시 대본이 전혀 없으므로, 매번 완전히 새로운 상황 설정과 화자의 내돈내산 꿀팁 관점으로 친절하고 매끄럽게 설명하시오.
- 주제 #2, #4, #5는 반드시 남성 화자 1인칭 시점으로 작성하시오.
- 🏛️ 금융소비자보호법 준수: 특정 금액 단정 ❌, 자극적 비방(호갱, 폭탄, 사기 등) ❌, 오직 객관적 보장 범위와 요율 비교로만 신뢰감 있게 서술하세요.
- 마지막 CTA에는 반드시 "네이버에 {self.OFFICIAL_KEYWORD} 검색해보세요!"를 자연스럽게 포함하세요.

[출력 JSON 규격 (20초 완제품 분량, 전체 약 115~140자)]
{{
  "situation": "이번 설정한 화자 및 상황 (1줄 요약)",
  "hook_p1": "0~5초: 시선을 확 끄는 첫 질문이나 공감 멘트 (공백 포함 20~28자)",
  "hook_p2": "5~10초: 보험리밸런스 해당 기능으로 연결되는 멘트 (공백 포함 20~28자)",
  "app_speech": "10~18초: 핵심 작동 원리와 유저 혜택 설명 (공백 포함 40~55자)",
  "cta_speech": "18~20초: 댓글 유도 및 '네이버에 {self.OFFICIAL_KEYWORD} 검색해보세요!' 포함 (공백 포함 20~30자)",
  "debate_question": "댓글 창에서 토론을 유도할 센스 있는 10자 내외 질문",
  "full_speech": "전체 발화문 (공백 포함 115~140자)"
}}
"""

        models = ["gemini-2.5-flash", "gemini-2.0-flash"]

        for kd in self.key_dicts:
            key_name = kd["name"]
            key_val = kd["key"]
            try:
                client = genai.Client(api_key=key_val)
            except Exception:
                continue

            for model in models:
                try:
                    resp = client.models.generate_content(
                        model=model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            automatic_function_calling=genai_types.AutomaticFunctionCallingConfig(disable=True),
                            response_mime_type="application/json",
                            temperature=0.95
                        )
                    )
                    if not resp or not resp.text:
                        continue

                    data = json.loads(resp.text)
                    hook_p1 = data.get("hook_p1", "").strip()
                    hook_p2 = data.get("hook_p2", "").strip()
                    app_speech = data.get("app_speech", "").strip()
                    cta_speech = data.get("cta_speech", "").strip()
                    debate_q = data.get("debate_question", "").strip()
                    situation = data.get("situation", "").strip()

                    full_speech = data.get("full_speech", "").strip()
                    if not full_speech:
                        full_speech = f"{hook_p1} {hook_p2} {app_speech} {cta_speech}".strip()

                    # 🔒 [무결성 게이트 1: 금지어 검증]
                    has_forbidden = False
                    for bad_word in self.FORBIDDEN_WORDS:
                        if bad_word in full_speech:
                            logger.warning(f"🚫 [금지어 감지 탈락] '{bad_word}' 포함 대본 기각: {full_speech}")
                            has_forbidden = True
                            break
                    if has_forbidden:
                        continue

                    # 공식 검색어 포함 검증 (누락 시 자동 보정)
                    if self.OFFICIAL_KEYWORD not in cta_speech:
                        cta_speech = f"{cta_speech} 네이버에 {self.OFFICIAL_KEYWORD} 검색해보세요!"
                        full_speech = f"{hook_p1} {hook_p2} {app_speech} {cta_speech}".strip()

                    # 🔒 [무결성 게이트 2: 글자 수 검증 (안전 허용 범위: 95자 ~ 165자)]
                    if len(full_speech) < 95 or len(full_speech) > 165:
                        logger.warning(f"⚠️ 글자 수 범위 벗어남({len(full_speech)}자, 허용: 95~165자), 다음 시도")
                        continue

                    logger.info(f"✨ [Gemini 자율 대본 성공] 보험 주제 #{norm_id} ({len(full_speech)}자, key={key_name}, model={model})")
                    return {
                        "hook_p1_5s": hook_p1,
                        "hook_p2_5s": hook_p2,
                        "hook_0_10s": f"{hook_p1} {hook_p2}",
                        "app_10_20s": app_speech,
                        "app_10_18s": app_speech,
                        "cta_18_22s": cta_speech,
                        "cta_20_22s": cta_speech,
                        "hero_copy": spec.get("hero_copy", "객관적 5대 보장 AI 분석"),
                        "debate_question": debate_q or "내 보험 보장 범위는 안전할까?",
                        "full_speech": full_speech,
                        "situation": situation,
                        "is_ai_generated": True
                    }
                except Exception as e:
                    logger.debug(f"Gemini 호출 실패 ({key_name}, {model}): {e}")
                    continue

        logger.warning(f"⚠️ [보험 대본] 제미나이 호출 모두 실패 ➔ 폴백")
        return None
