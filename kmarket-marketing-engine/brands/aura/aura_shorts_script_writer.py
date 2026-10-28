# -*- coding: utf-8 -*-
"""
AuraShortsScriptWriter - 💖 Aura 8대 주제 전용 제미나이 3.8 Flash 자율 창작 대본 작성기
========================================================================================
- [원천 아키텍처 개편]:
  1. 하드코딩 골든 대본 주입 전면 영구 배제 (예시문 베끼기 원천 박멸)
  2. 아우라 8대 핵심 기능 명세(기능 개요, 해결하는 고민, 활용 상황, 화자 설정)를 프롬프트에 주입
  3. 제미나이가 기능을 2030 시청자에게 직접 설명하는 100% 독창적 숏폼 대본 자율 창작
  4. 22.0초 완제품 규격 (공백 포함 150~165자) 엄격 준수
     - 0~10초 립싱크 구간 70~78자 확보 ➔ Wan 2.2 S2V 10.12초 멍때림 원천 차단
  5. 9개 통합 키 체인(무료 6개 + 유료 2개 + 기본 1개) 무중단 자동 페일오버 연동
"""

import sys
import json
import logging
from typing import Dict, Any, Optional, List
from google import genai
from google.genai import types
from google.genai import types as genai_types

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


# ==============================================================================
# 🏛️ [6인 합의체 도파민 서사 팩 8종 (슬롯 9~16번)] — 기존 1~8번 100% 보존
# ==============================================================================
AURA_NARRATIVE_PACKS: Dict[int, Dict[str, Any]] = {
    9: {
        "slot": 9,
        "title": "긴급 탈출 실전편",
        "speaker": "2030 직장인 여성",
        "hook_cue": "화장실 거울 발 동동 구르는 장면 + 카톡 진동음",
        "hook_seed": "하... 2차 가자는데 진짜 어떡하지? 핑계가 안 떠올라...",
        "conflict": "비매너 소개팅에서 예의상 억지로 앉아 있다가 밥값만 10만원 날린 흑역사 썰",
        "kakao_lines": ["상대: 2차 와인바 가시죠?", "나: (화장실 도망) 어쩌지 ㅠㅠ"],
        "twist_solution": "화장실에서 30초 뒤 가짜 호출 예약 걸어둠 ➔ 자리 돌아오자마자 팀장님 진짜 전화 울림 ➔ '죄송해요 회사 서버 터졌대요!' 칼퇴장 성공",
        "debate_q": "소개팅 중 가짜 탈출 전화, 센스일까 비매너일까?",
    },
    10: {
        "slot": 10,
        "title": "도쿄 현지인 영통 썰",
        "speaker": "2030 청년 (여행/덕질러)",
        "hook_cue": "영상통화 화면 + 일본어 쏼라쏼라 음성",
        "hook_seed": "스미마셍 말고는 아는 게 없는데... 진짜 통화가 된다고?!",
        "conflict": "일본 여행 전 현지 친구 사귀려다 번역기 복붙하느라 대화 뚝뚝 끊겨 읽씹당한 굴욕",
        "kakao_lines": ["현지인: これ好き？ (이거 좋아해?)", "나: (자막 실시간 뜸) 나 그거 완전 좋아해!"],
        "twist_solution": "한국어로 말하면 상대방 화면에 일본어 자막이, 상대 일본어가 내 화면에 한글 자막으로 1초 만에 뜸 ➔ 밤 12시까지 랜선 술자리 통화 성공",
        "debate_q": "외국인 찐친 만들기, 번역기 없이 진짜 가능할까?",
    },
    11: {
        "slot": 11,
        "title": "소개팅앱 삭제하는 이유",
        "speaker": "2030 세련된 여성",
        "hook_cue": "경고 사이렌 효과음 + 쏟아지는 음침한 DM 캡처",
        "hook_seed": "도대체 소개팅 어플에 왜 이렇게 음침한 사람들이 많을까?",
        "conflict": "남초 90% 앱에서 무차별 음침 디엠과 유령회원에 질려 하루 만에 앱 삭제하던 피로감",
        "kakao_lines": ["모르는 남: ㅎㅇ 지금 볼래?", "나: (차단) 진짜 질린다 질려"],
        "twist_solution": "남녀 딱 50:50 안 맞으면 남자는 번호표 뽑고 대기해야 입장 가능한 정원제 라운지 ➔ 물 흐리는 사람 0%에 검증된 매너 회원만 1:1 매칭",
        "debate_q": "성비 50:50 강제 대기열, 남자 역차별이다 vs 필수 안전장치다?",
    },
    12: {
        "slot": 12,
        "title": "실물 손절 방지 화보",
        "speaker": "2030 트렌디한 여성",
        "hook_cue": "턱 비정상적으로 깎인 외계인 보정 사진 쾅! 효과음",
        "hook_seed": "사진 보고 설렜다가 실물 보고 도망친 적 있는 사람 손?!",
        "conflict": "눈 키우고 턱 깎는 인조인간 필터는 실물 보는 순간 '사진 사기'로 낙인찍혀 5분 만에 손절당함",
        "kakao_lines": ["친구: 야 너 이 사진 실물이랑 너무 다르잖아", "나: 헐... 애프터 까인 이유가 이거였어?"],
        "twist_solution": "내 이목구비는 1mm도 안 건드리고, 방구석 형광등 폰카를 30만원 스튜디오 조명과 피부톤으로만 바꿔줌 ➔ 이번엔 실물 보고도 아무도 안 도망침",
        "debate_q": "AI 화보 보정, 어디까지가 매너일까?",
    },
    13: {
        "slot": 13,
        "title": "소개팅 더치페이 팩폭",
        "speaker": "2030 캠퍼스/직장인",
        "hook_cue": "영수증 탁! 내려놓는 소리 + 남녀 동공지진 클로즈업",
        "hook_seed": "계산대 앞에서 정적 흐를 때, 이 말 한마디로 애프터 확률 3배 갈립니다.",
        "conflict": "얼굴만 보고 만났다가 연락 주기, 데이트 비용 문제로 3주 만에 싸우고 헤어지는 피로감",
        "kakao_lines": ["나: 더치페이 어떻게 생각해요?", "상대: 당연히 첫 만남은 반반이죠!"],
        "twist_solution": "첫 만남 더치페이, 연락 빈도 등 12가지 밸런스 게임을 먼저 풀고 나랑 가치관 100% 일치하는 인연만 골라 매칭해주니 싸울 일이 없음",
        "debate_q": "첫 소개팅 밥값 더치페이, 여러분의 기준은?",
    },
    14: {
        "slot": 14,
        "title": "첫 카톡 읽씹 탈출 (남성)",
        "speaker": "2030 훈남 직장인 남성 (★남성 화자 1인칭 시점 엄수)",
        "hook_cue": "카톡 숫자 [1] 안 사라지는 화면 + 깊은 한숨 소리",
        "hook_seed": "형들, 제발 첫마디로 '오늘 날씨 좋네요' 그만 보내... 제발!",
        "conflict": "매칭만 되면 뭐 하냐고, 첫마디 뭐라고 보낼지 몰라 식은땀 흘리다 12번째 읽씹당한 남자의 리얼한 고통",
        "kakao_lines": ["나: 프로필 보니 성수동 소금빵 좋아하시네요?", "상대: 헐 거기 제 인생 카페인데 어떻게 아셨어요?!"],
        "twist_solution": "상대 프로필과 취향 키워드를 분석해 센스 있는 아이스브레이킹 질문 자동 추천 ➔ 3분 만에 칼답 오고 이번 주말 애프터 약속 잡힘",
        "debate_q": "첫마디 AI 추천, 센스일까 사기일까?",
    },
    15: {
        "slot": 15,
        "title": "AI 얼굴 아우라 팩폭",
        "speaker": "2030 감각적인 잇걸",
        "hook_cue": "셀카 스캔 삐빅! + 상위 3% 아우라 도장 쾅 찍히는 소리",
        "hook_seed": "친구들이 해주는 외모 칭찬, 솔직히 다 빈말인 거 아시죠?",
        "conflict": "내 얼굴 분위기가 뭔지 몰라 소개팅 앱 프로필 사진 고르는 데만 3시간 걸리던 답답함",
        "kakao_lines": ["친구: 너 다정한 여우상이래 완전 찰떡이다", "나: 그거 방금 AI가 1초 만에 알려줬어!"],
        "twist_solution": "폰카 셀카 한 장 넣었더니 내 이목구비와 눈빛 분위기를 분석해 '다정한 여우상 상위 4%' 팩폭 진단 카드가 발급됨 ➔ 프로필 달았더니 호감도 폭발",
        "debate_q": "AI 매력 진단, 재미있는 놀이일까 자기 객관화일까?",
    },
    16: {
        "slot": 16,
        "title": "동네 자취생 안심 번개",
        "speaker": "2030 건강한 직장인 여성",
        "hook_cue": "지도 줌인 화면 + 스토킹 경고 사이렌 소리",
        "hook_seed": "동네 데이팅 앱 썼다가 집 앞 편의점에서 마주칠 뻔한 썰 푼다...",
        "conflict": "동네 친구 사귀고 싶은데 집 주소 근처까지 노출되는 일반 위치 앱의 소름 돋는 위험성과 스토킹 공포",
        "kakao_lines": ["상대: 혹시 OO빌라 사세요?", "나: (소름 돋아서 앱 삭제)"],
        "twist_solution": "내 실제 집 위치를 500m 반경 안에서 랜덤으로 흔들어주는 보안 레이더 ➔ 집 주소 노출 위험 0%로 성수 카페 메이트, 한강 러닝 메이트 안심 번개 성공",
        "debate_q": "동네 번개 앱에서 500m 위치 난수화, 필수다 vs 오버다?",
    }
}


class AuraShortsScriptWriter:
    """💖 Aura 1~16대 전용 제미나이 3.8 Flash 실시간 자율 창작 대본 생성 엔진 (A/B 병렬 지원판)"""

    OFFICIAL_KEYWORD = "아우라AI데이팅"
    LANDING_URL = "https://aura-ai-dating.vercel.app/"
    DUAL_BANNER_TEXT = "프로필 링크에서 3초 무료 진단! 네이버에 아우라AI데이팅 검색해보세요!"
    FORBIDDEN_WORDS = [
        "한정", "이벤트", "선착순", "마감", "할인", "무료 혜택", "쿠폰", 
        "사은품", "오늘만", "특가", "캐시백", "당첨", "보험", "주식", "투자", "환급"
    ]
    EXPLANATORY_PATTERNS = [
        "해줍니다", "제공합니다", "지원합니다", "가능합니다", "기능입니다"
    ]

    def __init__(self):
        self.key_dicts = get_unified_gemini_key_dicts()

    def generate_dynamic_script(self, topic_id: int = 1) -> Optional[Dict[str, Any]]:
        """
        주제 ID(1~16)에 맞춰 자율 대본 창작:
        - 1~8번: 기존 레거시 기능 명세 기반 대본 (하위 호환 100% 보존)
        - 9~16번: 6인 합의체 도파민 서사 팩 기반 4분절 실전 썰 대본 (A/B 신규)
        """
        if 9 <= topic_id <= 16:
            return self._generate_narrative_script(topic_id)
        else:
            return self._generate_legacy_script(topic_id)

    def _generate_narrative_script(self, topic_id: int) -> Optional[Dict[str, Any]]:
        """🏛️ 6인 합의체 9~16번 서사 팩 전용 [2단 통대본] 자율 창작 파이프라인
        - 1단: hook_10s (0~10초 인물 립싱크 통대본, 98~105자) ➔ Wan 2.2 S2V 10.12초 무음 멍때림 원천 차단
        - 2단: remainder_speech (10~22초 나머지 통대본, 160~180자) ➔ 앱 시연 + CTA
        """
        pack = AURA_NARRATIVE_PACKS.get(topic_id, AURA_NARRATIVE_PACKS[9])
        kakao_lines_str = "\n".join(f"  - {line}" for line in pack["kakao_lines"])
        is_male_topic = (topic_id == 14)

        prompt = f"""[서사 팩 (Narrative Pack)]
- 브랜드: 아우라 (Aura) 데이팅
- 킬러 슬롯 #{pack['slot']}: {pack['title']}
- 화자 설정: {pack['speaker']}
- 0~2초 도입 큐(시청각): {pack['hook_cue']}
- 0~2초 훅 시드 대사: "{pack['hook_seed']}"
- 극공감 현실 갈등: {pack['conflict']}
- 실전 카톡 대사:
{kakao_lines_str}
- 8~17초 반전 치트키 (앱 기능): {pack['twist_solution']}
- 18~22초 2in1 듀얼 스마트 배너: "{self.DUAL_BANNER_TEXT}"
- 댓글 논쟁 유도 쟁점: {pack['debate_q']}

[★ 절대 준수 지시 사항]
1. 인사말/배경설명 없이 곧바로 강렬한 대사나 질문으로 시작할 것!
2. "~해줍니다", "~제공합니다" 같은 설명서 어투는 절대 금지! 1인칭 실전 썰로 이야기할 것!
3. 카톡 대사 1줄 이상을 대본에 실감 나게 녹여낼 것!
{"4. 반드시 2030 남성 화자 1인칭('형들', '내가' 등)으로만 작성할 것!" if is_male_topic else ""}
5. 나머지 통대본(remainder_speech) 마지막에는 반드시 "{self.DUAL_BANNER_TEXT}"를 그대로 포함할 것!
6. 허위 이벤트(할인, 쿠폰 등)는 절대 금지.

[🚨 2단 통대본 구조 — 절대 준수]
이 대본은 4초/5초로 잘게 쪼개지 않습니다. 오직 2개의 통대본으로만 구성합니다.
- 1단 hook_10s: 0~10초 인물 립싱크 통대본. 공백 포함 98~105자 엄수.
  ➔ 이 구간은 아바타가 10.12초 내내 쉬지 않고 말해야 하므로 절대 짧게 쓰지 말 것!
  ➔ 4초/5초 단위로 끊어 쓰지 말고, 하나의 끊김 없는 문장 흐름으로 작성할 것!
- 2단 remainder_speech: 10~22초 나머지 통대본. 공백 포함 160~180자 엄수.
  ➔ 앱 기능 반전 설명 + 카톡 대사 + 마지막 2in1 배너 CTA를 하나의 통대본으로 작성할 것!
- full_speech = hook_10s + " " + remainder_speech (공백 포함 250~300자)

[출력 JSON 규격]
{{
  "hook_10s": "0~10초 인물 립싱크 통대본 (공백 포함 98~105자, 끊김 없는 단일 흐름)",
  "remainder_speech": "10~22초 나머지 통대본 (공백 포함 160~180자, 배너 CTA 포함)",
  "debate_question": "{pack['debate_q']}",
  "full_speech": "전체 발화문 = hook_10s + remainder_speech (공백 포함 250~300자)"
}}
"""
        models = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-flash-latest"]

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
                    hook_10s = data.get("hook_10s", "").strip()
                    remainder_speech = data.get("remainder_speech", "").strip()
                    debate_q = data.get("debate_question", pack["debate_q"]).strip()
                    full_speech = data.get("full_speech", "").strip()

                    # 🧩 [2단 통대본 재조립] hook_10s + remainder_speech 단일 흐름 강제
                    if not hook_10s or not remainder_speech:
                        logger.warning(f"⚠️ [2단 통대본 누락] 서사 팩 #{topic_id} hook_10s/remainder_speech 결손 ➔ 재시도")
                        continue

                    if not full_speech:
                        full_speech = f"{hook_10s} {remainder_speech}".strip()

                    # 🔒 [무결성 게이트 1: 금지어 검증]
                    has_forbidden = any(bad in full_speech for bad in self.FORBIDDEN_WORDS)
                    if has_forbidden:
                        continue

                    # 🔒 [무결성 게이트 2: 설명조 어투 검출]
                    if any(pat in remainder_speech for pat in self.EXPLANATORY_PATTERNS):
                        logger.warning(f"⚠️ [설명조 감지] 서사 팩 #{topic_id} 설명조 어투 발견, 재시도")
                        continue

                    # 🔒 [무결성 게이트 3: 2in1 듀얼 배너 누락 시 자동 보정]
                    if self.OFFICIAL_KEYWORD not in remainder_speech:
                        remainder_speech = f"{remainder_speech} {self.DUAL_BANNER_TEXT}".strip()
                        full_speech = f"{hook_10s} {remainder_speech}".strip()

                    # 🔒 [무결성 게이트 4: 2단 통대본 글자 수 검증]
                    #    hook_10s 95~110자 / remainder_speech 150~190자 / full_speech 250~300자
                    if not (95 <= len(hook_10s) <= 110):
                        logger.warning(
                            f"⚠️ [1단 분량 미달] 서사 팩 #{topic_id} hook_10s {len(hook_10s)}자 "
                            f"(목표 98~105자 / 허용 95~110자) ➔ 재시도"
                        )
                        continue

                    if not (150 <= len(remainder_speech) <= 190):
                        logger.warning(
                            f"⚠️ [2단 분량 미달] 서사 팩 #{topic_id} remainder_speech {len(remainder_speech)}자 "
                            f"(목표 160~180자 / 허용 150~190자) ➔ 재시도"
                        )
                        continue

                    if not (250 <= len(full_speech) <= 300):
                        logger.warning(
                            f"⚠️ [총 분량 미달] 서사 팩 #{topic_id} full_speech {len(full_speech)}자 "
                            f"(목표 250~300자) ➔ 재시도"
                        )
                        continue

                    # 🎬 [10초 립싱크 안전장치] hook_10s 를 5초 단위 2분절로만 분할 (4초/5초 난분할 금지)
                    hook_p1_5s, hook_p2_5s = self._split_into_two_halves(hook_10s)
                    # 🎬 [나머지 통대본] 앱 시연부 / CTA부 호환 분할
                    app_10_18s, cta_18_22s = self._split_remainder(remainder_speech)

                    logger.info(
                        f"✨ [2단 통대본 성공] 슬롯 #{topic_id} "
                        f"(hook_10s={len(hook_10s)}자 / remainder={len(remainder_speech)}자 / "
                        f"full={len(full_speech)}자, key={key_name}, model={model})"
                    )
                    return {
                        "slot": topic_id,
                        "hook_10s": hook_10s,
                        "hook_0_10s": hook_10s,
                        "hook_p1_5s": hook_p1_5s,
                        "hook_p2_5s": hook_p2_5s,
                        "remainder_speech": remainder_speech,
                        "app_10_18s": app_10_18s,
                        "cta_18_22s": cta_18_22s,
                        "banner_dual": self.DUAL_BANNER_TEXT,
                        "debate_question": debate_q,
                        "full_speech": full_speech,
                        "is_narrative_v2": True,
                        "is_two_stage_speech": True,
                        "is_ai_generated": True
                    }
                except Exception as e:
                    logger.debug(f"Gemini 서사 호출 실패 ({key_name}, {model}): {e}")
                    continue

        logger.warning(f"⚠️ [Aura 서사 대본] 제미나이 호출 모두 실패 ➔ 폴백")
        return None

    def _generate_legacy_script(self, topic_id: int) -> Optional[Dict[str, Any]]:
        """1~8번 기존 레거시 기능 명세 기반 대본 (하위 호환 100% 보존)"""
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
위 아우라의 기능을 2030 시청자에게 자세하고 흥미진진하게 설명하는 22초 숏폼 대본을 작성하시오.
- 🚨 기존에 완성된 예시 대본이 전혀 없으므로, 매번 완전히 새로운 상황 설정과 화자의 관점으로 친절하고 매끄럽게 설명하시오.
- 주제 #6은 반드시 남성 화자 1인칭 시점으로 작성하시오.
- 🚨 허위 이벤트(무료 쿠폰, 선착순, 할인 등)는 절대 금지합니다.
- 나머지 통대본(remainder_speech) 마지막에는 반드시 "네이버에 {self.OFFICIAL_KEYWORD} 검색해보세요!"를 자연스럽게 포함하세요.

[🚨 2단 통대본 구조 — 절대 준수]
이 대본은 4초/5초로 잘게 쪼개지 않습니다. 오직 2개의 통대본으로만 구성합니다.
- 1단 hook_10s: 0~10초 인물 립싱크 통대본. 공백 포함 98~105자 엄수.
  ➔ 이 구간은 아바타가 10.12초 내내 쉬지 않고 말해야 하므로 절대 짧게 쓰지 말 것!
  ➔ 4초/5초 단위로 끊어 쓰지 말고, 하나의 끊김 없는 문장 흐름으로 작성할 것!
- 2단 remainder_speech: 10~22초 나머지 통대본. 공백 포함 160~180자 엄수.
  ➔ 앱 핵심 작동 원리 + 유저 혜택 + 마지막 네이버 검색 CTA를 하나의 통대본으로 작성할 것!
- full_speech = hook_10s + " " + remainder_speech (공백 포함 250~300자)

[출력 JSON 규격]
{{
  "situation": "이번 설정한 화자 및 상황 (1줄 요약)",
  "hook_10s": "0~10초 인물 립싱크 통대본 (공백 포함 98~105자, 끊김 없는 단일 흐름)",
  "remainder_speech": "10~22초 나머지 통대본 (공백 포함 160~180자, '네이버에 {self.OFFICIAL_KEYWORD} 검색해보세요!' 포함)",
  "debate_question": "댓글 창에서 토론을 유도할 센스 있는 10자 내외 질문",
  "full_speech": "전체 발화문 = hook_10s + remainder_speech (공백 포함 250~300자)"
}}
"""
        models = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-flash-latest"]

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
                    hook_10s = data.get("hook_10s", "").strip()
                    remainder_speech = data.get("remainder_speech", "").strip()
                    debate_q = data.get("debate_question", "").strip()
                    situation = data.get("situation", "").strip()

                    # 🧩 [2단 통대본 재조립] hook_10s + remainder_speech 단일 흐름 강제
                    if not hook_10s or not remainder_speech:
                        logger.warning(f"⚠️ [2단 통대본 누락] 주제 #{norm_id} hook_10s/remainder_speech 결손 ➔ 재시도")
                        continue

                    full_speech = data.get("full_speech", "").strip()
                    if not full_speech:
                        full_speech = f"{hook_10s} {remainder_speech}".strip()

                    has_forbidden = any(bad in full_speech for bad in self.FORBIDDEN_WORDS)
                    if has_forbidden:
                        continue

                    # 🔒 [무결성 게이트: 네이버 검색 키워드 누락 시 자동 보정]
                    if self.OFFICIAL_KEYWORD not in remainder_speech:
                        remainder_speech = f"{remainder_speech} 네이버에 {self.OFFICIAL_KEYWORD} 검색해보세요!"
                        full_speech = f"{hook_10s} {remainder_speech}".strip()

                    # 🔒 [무결성 게이트: 2단 통대본 글자 수 검증]
                    #    hook_10s 95~110자 / remainder_speech 150~190자 / full_speech 250~300자
                    if not (95 <= len(hook_10s) <= 110):
                        logger.warning(
                            f"⚠️ [1단 분량 미달] 주제 #{norm_id} hook_10s {len(hook_10s)}자 "
                            f"(목표 98~105자 / 허용 95~110자) ➔ 재시도"
                        )
                        continue

                    if not (150 <= len(remainder_speech) <= 190):
                        logger.warning(
                            f"⚠️ [2단 분량 미달] 주제 #{norm_id} remainder_speech {len(remainder_speech)}자 "
                            f"(목표 160~180자 / 허용 150~190자) ➔ 재시도"
                        )
                        continue

                    if not (250 <= len(full_speech) <= 300):
                        logger.warning(
                            f"⚠️ [총 분량 미달] 주제 #{norm_id} full_speech {len(full_speech)}자 "
                            f"(목표 250~300자) ➔ 재시도"
                        )
                        continue

                    # 🎬 [10초 립싱크 안전장치] hook_10s 를 5초 단위 2분절로만 분할 (4초/5초 난분할 금지)
                    hook_p1_5s, hook_p2_5s = self._split_into_two_halves(hook_10s)
                    # 🎬 [나머지 통대본] 앱 시연부 / CTA부 호환 분할
                    app_10_18s, cta_18_22s = self._split_remainder(remainder_speech)

                    logger.info(
                        f"✨ [2단 통대본 성공] 주제 #{norm_id} "
                        f"(hook_10s={len(hook_10s)}자 / remainder={len(remainder_speech)}자 / "
                        f"full={len(full_speech)}자, key={key_name}, model={model})"
                    )
                    return {
                        "hook_10s": hook_10s,
                        "hook_0_10s": hook_10s,
                        "hook_p1_5s": hook_p1_5s,
                        "hook_p2_5s": hook_p2_5s,
                        "remainder_speech": remainder_speech,
                        "app_10_18s": app_10_18s,
                        "cta_18_22s": cta_18_22s,
                        "debate_question": debate_q or "여러분의 생각은 어떠신가요?",
                        "full_speech": full_speech,
                        "situation": situation,
                        "is_narrative_v2": False,
                        "is_two_stage_speech": True,
                        "is_ai_generated": True
                    }
                except Exception as e:
                    logger.debug(f"Gemini 호출 실패 ({key_name}, {model}): {e}")
                    continue

        logger.warning(f"⚠️ [Aura 대본] 제미나이 호출 모두 실패 ➔ 폴백")
        return None

    # ==========================================================================
    # 🎬 [2단 통대본 호환 분할 유틸] — 4초/5초 난분할 금지, 5초 2분절만 허용
    # ==========================================================================
    @staticmethod
    def _split_into_two_halves(text: str) -> tuple:
        """10초 통대본을 5초/5초 2분절로만 분할 (문장부호 ➔ 공백 순 우선 탐색)"""
        text = (text or "").strip()
        if not text:
            return "", ""

        total = len(text)
        mid = total // 2
        window = max(6, total // 5)  # 중앙 ±20% 이내에서만 절단점 탐색

        best_idx = -1
        best_dist = 10 ** 9
        for i in range(max(1, mid - window), min(total - 1, mid + window) + 1):
            ch = text[i - 1]
            if ch in ".!?。？！":
                dist = abs(i - mid)
                if dist < best_dist:
                    best_dist = dist
                    best_idx = i

        if best_idx < 0:
            for i in range(max(1, mid - window), min(total - 1, mid + window) + 1):
                if text[i - 1] == " ":
                    dist = abs(i - mid)
                    if dist < best_dist:
                        best_dist = dist
                        best_idx = i

        if best_idx < 0:
            best_idx = mid

        return text[:best_idx].strip(), text[best_idx:].strip()

    @staticmethod
    def _split_remainder(text: str) -> tuple:
        """나머지 통대본을 앱 시연부 / CTA부로 호환 분할 (원문 손실 0%)"""
        text = (text or "").strip()
        if not text:
            return "", ""

        # CTA 문구 시작점을 기준으로 분할 (없으면 70% 지점)
        cta_markers = ["네이버에", "프로필 링크", "검색해보세요", "검색!"]
        cut = -1
        for marker in cta_markers:
            pos = text.rfind(marker)
            if pos > 0:
                cut = pos
                break

        if cut <= 0:
            cut = int(len(text) * 0.7)

        app_part = text[:cut].strip()
        cta_part = text[cut:].strip()
        if not app_part or not cta_part:
            return text, ""
        return app_part, cta_part

