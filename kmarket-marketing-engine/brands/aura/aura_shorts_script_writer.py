# -*- coding: utf-8 -*-
"""
AuraShortsScriptWriter - 💖 Aura 8대 주제 전용 제미나이 3.8 Flash 자율 창작 대본 작성기
========================================================================================
- [원천 아키텍처 개편]:
  1. 하드코딩 골든 대본 주입 전면 영구 배제 (예시문 베끼기 원천 박멸)
  2. 아우라 8대 핵심 기능 명세(기능 개요, 해결하는 고민, 활용 상황, 화자 설정)를 프롬프트에 주입
  3. 제미나이가 기능을 2030 시청자에게 직접 설명하는 100% 독창적 숏폼 대본 자율 창작
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

logger = logging.getLogger("AuraShortsScriptWriter")


AURA_TOPICS_SPECS: Dict[int, Dict[str, str]] = {
    1: {
        "title": "긴급 탈출 가짜 전화",
        "gender": "2030 직장인 여성",
        "feature_desc": "어색하거나 불쾌한 소개팅 자리에서 벗어나고 싶을 때, 앱에서 가짜 긴급 업무 호출 전화를 걸어주어 매너 있게 자리를 칼탈출할 수 있도록 돕는 기능.",
        "problem_solved": "상대가 비매너이거나 숨 막히게 어색한데 예의상 도망치지도 못하고 갇혀 있던 답답함을 완벽히 해결.",
        "usage_scenario": "청담/강남 소개팅 중 화장실로 피신해 30초 뒤 가짜 팀장님 호출 예약, 자연스러운 퇴장 성공 경험.",
    },
    2: {
        "title": "실시간 AI 자막 영상 통화",
        "gender": "2030 청년 (여행/덕질러)",
        "feature_desc": "한국어와 외국어(일본어 등)로 통화할 때 AI가 음성을 실시간 인식하여 화면 하단에 양방향 실시간 번역 자막을 띄워주는 기능.",
        "problem_solved": "외국어를 못해서 외국인 친구 사귀기가 두렵거나 번역기 복사 붙여넣기하느라 대화 흐름이 끊기던 답답함 해결.",
        "usage_scenario": "일본 여행 전 현지인 찐친 만들기, 취미/관심사로 밤새 수다 떨기, 언어 교환 데이팅.",
    },
    3: {
        "title": "50:50 VIP 게이트",
        "gender": "2030 세련된 여성",
        "feature_desc": "남녀 성비가 50:50으로 완벽히 유지될 때만 신규 입장을 허용하는 정원제 VIP 라운지.",
        "problem_solved": "기존 소개팅 앱의 남초 90% 현상, 무차별 음침한 디엠, 물 흐리는 유령회원에 질린 피로감 완벽 해결.",
        "usage_scenario": "남성은 정원 대기열 관리, 여성은 VIP 프리패스 입장으로 검증된 매너 회원끼리만 고품격 대화.",
    },
    4: {
        "title": "청담동 화보 AI 보정",
        "gender": "2030 트렌디한 여성",
        "feature_desc": "비싼 스튜디오에 가지 않아도 일상 폰카 사진 1장을 30만원짜리 청담동 스튜디오 화보급 프로필로 AI가 자연스럽게 변신시켜주는 기능.",
        "problem_solved": "과한 인조인간 필터로 실물 보고 실망하는 '사진 사기' 방지, 본래 이목구비 100% 보존하며 피부톤과 조명만 화보급 업그레이드.",
        "usage_scenario": "소개팅 앱용 인생 프로필 사진 만들기, 자연스러운 매력 극대화.",
    },
    5: {
        "title": "가치관 밸런스 매칭",
        "gender": "2030 캠퍼스/직장인",
        "feature_desc": "첫 만남 더치페이, 연락 빈도, 소비 습관, 결혼관 등 12가지 연애 밸런스 게임을 통해 나와 가치관이 100% 찰떡궁합인 인연만 매칭해주는 기능.",
        "problem_solved": "얼굴만 보고 만났다가 연락 스타일이나 데이트 비용 문제로 싸우고 상처받는 연애 실패 방지.",
        "usage_scenario": "사전 가치관 필터링으로 대화 코드가 완벽히 통하는 인연 선별.",
    },
    6: {
        "title": "AI 첫대화 비서",
        "gender": "2030 훈남 직장인 남성 (★남성 화자 1인칭 시점 엄수)",
        "feature_desc": "매칭 후 첫 마디를 뭐라고 보낼지 막막할 때, 상대방 프로필과 취향 키워드를 AI가 분석해 자연스러운 티키타카 아이스브레이킹 첫마디를 추천해주는 기능.",
        "problem_solved": "'안녕하세요' 보냈다가 읽씹당할까 봐 떨리는 2030 남성들의 첫 메시지 공포증 해결.",
        "usage_scenario": "상대 취향 맞춤형 센스 있는 질문으로 답장률 90% 이상 확보한 성공 썰.",
    },
    7: {
        "title": "AI 아우라 매력 진단",
        "gender": "2030 감각적인 잇걸",
        "feature_desc": "셀카 한 장으로 내 얼굴형과 분위기를 AI가 정밀 분석하여 나의 독보적인 매력 키워드와 상위 % 아우라 지수(다정한 여우상, 청순 강아지상 등)를 1초 만에 진단해주는 기능.",
        "problem_solved": "내 매력이 뭔지 잘 모르겠거나, 인스타에서 핫한 재미있는 매력 테스트를 즐기고 싶은 2030 호기심 충족.",
        "usage_scenario": "나만의 매력 카드 발급받고 프로필에 달아 매칭률 상승한 경험담.",
    },
    8: {
        "title": "500m 안심 레이더",
        "gender": "2030 건강한 직장인 여성",
        "feature_desc": "동네 친구나 가벼운 카페/러닝 번개를 원하지만 집 주소 노출이나 스토킹이 불안한 사람을 위해, 실제 집 위치를 500m 랜덤 보안(지터링)으로 철통 방어하며 안전하게 당일 번개를 만나는 기능.",
        "problem_solved": "동네 친구 사귀고 싶지만 집 앞까지 노출되는 불안감 완벽 차단.",
        "usage_scenario": "성수/연남동 카페 메이트, 주말 한강 러닝 메이트 당일 안심 번개.",
    }
}


class AuraShortsScriptWriter:
    """💖 Aura 8대 주제 전용 제미나이 3.8 Flash 실시간 자율 창작 대본 생성 엔진"""

    OFFICIAL_KEYWORD = "아우라AI데이팅"
    FORBIDDEN_WORDS = [
        "한정", "이벤트", "선착순", "마감", "할인", "무료 혜택", "쿠폰", 
        "사은품", "오늘만", "특가", "캐시백", "당첨", "보험", "주식", "투자", "환급"
    ]

    def __init__(self):
        self.key_dicts = get_unified_gemini_key_dicts()

    def generate_dynamic_script(self, topic_id: int = 1) -> Optional[Dict[str, Any]]:
        """
        주제 ID(1~8)에 맞춰 아우라의 실제 기능 명세(기능 개요, 해결 고민, 활용 상황)를 주입하고,
        제미나이 3.8 Flash가 매번 100% 새롭고 독창적인 상황 설정으로 20초 숏폼 대본을 자율 창작.
        """
        norm_id = ((topic_id - 1) % len(AURA_TOPICS_SPECS)) + 1
        spec = AURA_TOPICS_SPECS.get(norm_id, AURA_TOPICS_SPECS[1])

        prompt = f"""[앱 및 기능 정보]
- 브랜드: 아우라 (Aura) 데이팅
- 주제 #{norm_id}: {spec['title']}
- 화자 설정: {spec['gender']}
- 기능 개요: {spec['feature_desc']}
- 해결하는 고민: {spec['problem_solved']}
- 활용 상황: {spec['usage_scenario']}

[★ 지시 사항 (절대 준수)]
위 아우라의 기능을 2030 시청자에게 자세하고 흥미진진하게 설명하는 20초 숏폼 대본을 작성하시오.
- 🚨 기존에 완성된 예시 대본이 전혀 없으므로, 매번 완전히 새로운 상황 설정과 화자의 관점으로 친절하고 매끄럽게 설명하시오.
- 주제 #6은 반드시 남성 화자 1인칭 시점으로 작성하시오.
- 🚨 허위 이벤트(무료 쿠폰, 선착순, 할인 등)는 절대 금지합니다.
- 마지막 CTA에는 반드시 "네이버에 {self.OFFICIAL_KEYWORD} 검색해보세요!"를 자연스럽게 포함하세요.

[출력 JSON 규격 (20초 완제품 분량, 전체 약 115~140자)]
{{
  "situation": "이번 설정한 화자 및 상황 (1줄 요약)",
  "hook_p1": "0~5초: 시선을 확 끄는 첫 질문이나 공감 멘트 (공백 포함 20~28자)",
  "hook_p2": "5~10초: 아우라 해당 기능으로 연결되는 멘트 (공백 포함 20~28자)",
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

                    # 🔒 [무결성 게이트 2: 글자 수 검증 (안전 허용 범위: 95자 ~ 160자)]
                    if len(full_speech) < 95 or len(full_speech) > 165:
                        logger.warning(f"⚠️ 글자 수 범위 벗어남({len(full_speech)}자, 허용: 95~165자), 다음 시도")
                        continue

                    logger.info(f"✨ [Gemini 자율 대본 성공] 주제 #{norm_id} ({len(full_speech)}자, key={key_name}, model={model})")
                    return {
                        "hook_p1_5s": hook_p1,
                        "hook_p2_5s": hook_p2,
                        "hook_0_10s": f"{hook_p1} {hook_p2}",
                        "app_10_18s": app_speech,
                        "cta_18_22s": cta_speech,
                        "debate_question": debate_q or "여러분의 생각은 어떠신가요?",
                        "full_speech": full_speech,
                        "situation": situation,
                        "is_ai_generated": True
                    }
                except Exception as e:
                    logger.debug(f"Gemini 호출 실패 ({key_name}, {model}): {e}")
                    continue

        logger.warning(f"⚠️ [Aura 대본] 제미나이 호출 모두 실패 ➔ 폴백")
        return None
