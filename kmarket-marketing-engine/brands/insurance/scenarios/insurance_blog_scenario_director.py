# -*- coding: utf-8 -*-
"""
🛡️ InsureBalance 보험 블로그 전용 시나리오 디렉터 (InsuranceBlogScenarioDirector)
================================================================================
- 브랜드: InsureBalance (보험 비교 & 보장 분석 & 리밸런싱)
- 목적:
  1. 5대 멀티 페르소나(2030 사회초년생 / 3040 맘&대디 / 4050 가장 / 라이프스타일러 / 앱테크족) 자동 로테이션
  2. 60:25:15 보험 종류별 황금 가중치(암·실손·종합 / 태아·운전자 / 간병·치아·환급) 자동 분배
  3. 스키머 시선 장악용 2단 비주얼 훅 박스 + "(비용 0원 / 전화 권유 0통 / 34개 보험사 실시간 모든 보험 비교)" 3대 킬러 카피 결합
  4. 광고 심의(금소법) 100% 면제 Search CTA([보험리밸런스]) 자동 조립
"""

import random
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("InsuranceBlogScenarioDirector")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent.parent
STATE_FILE = PROJECT_ROOT / "outputs" / "insurance" / "scenario_state.json"


class InsuranceBlogScenarioDirector:
    """InsureBalance 블로그 전용 멀티 페르소나 & 가중치 오케스트레이터"""

    BRAND_NAME = "보험리밸런스"
    SEARCH_KEYWORD = "보험리밸런스"
    LANDING_URL = "https://insure-rebalance.vercel.app/"

    # ========================================================
    # 🎭 1. 5대 멀티 페르소나 (Personas)
    # ========================================================
    PERSONAS = {
        "p1_young_starter": {
            "name": "2030 사회초년생 똑순이/똑돌이 (3년 차 직장인)",
            "tone_description": "월급 아끼려고 고정비 다이어트에 진심인 2030 직장인. 통장에서 매달 빠져나가던 보험료 뜯어보고 깜짝 놀라 3~5만 원 줄인 찐후기 구어체 (~하더라고요, ~했더니 소름 돋았음ㅋㅋ).",
            "hook_intro": "매달 통장에서 꼬박꼬박 빠져나가는 10만 원, 15만 원... 다들 어떻게 관리하고 계세요? 저도 얼마 전까지 그냥 부모님이 들어준 거라 믿고 놔뒀다가 가계부 정리하면서 진짜 경악했거든요ㅋㅋ",
            "preferred_categories": ["cancer_critical", "silson_medical", "youth_comprehensive"]
        },
        "p2_smart_mom_dad": {
            "name": "3040 알뜰살뜰 맘&대디 (가계부 살림꾼)",
            "tone_description": "가족 4인 보험료와 아이들 태아/어린이보험을 꼼꼼하게 챙기는 똑 부러진 3040 살림꾼. 불필요한 특약 싹 빼고 가계부 살려낸 현실적인 살림 팁 어조.",
            "hook_intro": "4인 가족 보험료 매달 60만 원씩 나가는 거 볼 때마다 한숨 쉬셨죠? 저도 남편이랑 아이들 보험 증권 싹 모아서 비교해봤더니 쓸데없는 중복 특약만 수두룩하더라고요.",
            "preferred_categories": ["child_fetal", "cancer_critical", "comprehensive_3major"]
        },
        "p3_senior_family_head": {
            "name": "4050 든든한 가장 (은퇴 준비 & 부모님 효도)",
            "tone_description": "치솟는 실손 갱신보험료와 부모님 간병비가 걱정인 4050 세대 가장. 차분하지만 뼈를 때리는 현실적 팩트체크와 노후 지출 방어 스토리텔링.",
            "hook_intro": "우편함에 날아온 실손보험 갱신 안내장 열어보셨습니까? 50대 접어드니 보험료가 2배로 뛰어서 눈앞이 캄캄하더군요. 무턱대고 해지할 수도 없고 고민하다가 객관적으로 손익을 계산해봤습니다.",
            "preferred_categories": ["silson_medical", "senior_care", "surgery_operation"]
        },
        "p4_active_lifestyle": {
            "name": "2040 라이프스타일러 (운전 / 레저 / 반려인)",
            "tone_description": "출퇴근 운전, 운동(헬스/골프), 반려동물 케어에 관심 많은 활동가. 법 개정 이슈나 생활 속 부상 특약을 1만 원대로 가성비 있게 챙기는 꿀팁 어조.",
            "hook_intro": "도로교통법이랑 스쿨존 벌금 바뀐 거 알고 계셨나요? 운전자보험 만 원짜리 하나 들고 안심하고 있었는데, 경찰조사 단계 변호사비는 0원이었다는 사실에 식겁해서 바로 갈아탔습니다.",
            "preferred_categories": ["driver_auto", "dental_pet", "surgery_operation"]
        },
        "p5_apptech_hunter": {
            "name": "스마트 앱테크족 (숨은 돈/환급금 사냥꾼)",
            "tone_description": "숨은 환급금과 병원비 3초 청구, 고정비 절약에 민첩한 스마트 유저. 묵혀둔 영수증으로 통장에 돈 꽂힌 생생한 환급 후기 어조.",
            "hook_intro": "병원 갈 때마다 서류 떼기 귀찮아서 포기했던 병원비... 앱으로 3초 만에 조회하니까 최근 3년 치 안 받은 돈이 43만 원이나 있더라고요? 사진 찍어 올리자마자 바로 통장에 입금됐습니다.",
            "preferred_categories": ["refund_claim", "silson_medical", "cancer_critical"]
        }
    }

    # ========================================================
    # 📊 2. 60:25:15 황금 가중치 카테고리 (Topic Weights)
    # ========================================================
    CATEGORIES_WEIGHTED = [
        # 🔥 Class A: 초대형 메이저 보험 (가중치 60%)
        ("cancer_critical", 20, "🎗️ 암보험 (일반암 vs 유사암 10배 차이 & 표적항암)"),
        ("silson_medical", 20, "🏥 실손의료보험 (1~4세대 전환 손익 & 도수치료 비급여 팩트체크)"),
        ("comprehensive_3major", 20, "🧠 3대질병 종합보험 (뇌혈관 vs 뇌출혈 10배 격차 & 허혈성 심장)"),

        # 🎯 Class B: 고효율 타깃 보험 (가중치 25%)
        ("child_fetal", 15, "👶 태아 / 어린이 / 청년보험 (산모특약 5개 & 30세만기)"),
        ("driver_auto", 10, "🚗 운전자 / 자동차 다이렉트 (스쿨존 벌금 3천만 & 경찰조사 변호사비)"),

        # 🌿 Class C: 롱테일 틈새 & 효도 보험 (가중치 15%)
        ("senior_care", 5, "👵 부모님 간병인 / 치매보험 (간병인 사용일당 vs 지원일당 실질 가성비)"),
        ("dental_pet", 5, "🦷 치아 / 펫보험 (임플란트 90일 면책 & 강아지 슬개골)"),
        ("refund_claim", 5, "💰 숨은 보험금 환급 & 병원비 3초 청구 노하우")
    ]

    # ========================================================
    # 🔲 3. 고정 3대 안심 배지 & 비주얼 훅 박스
    # ========================================================
    VISUAL_BOX_1 = """
> 💡 **[3초 팩트체크: 내 보험도 구멍 뚫려 있을까?]**
> · 34개 보험사 실시간 보장/보험료 무료 비교
> · 전화 권유 0통 / 가입 강요 0%
> 👉 네이버 검색창에 **[보험리밸런스]** 검색
"""

    VISUAL_BOX_2 = """
> 🚗 **[고정비 다이어트: 매달 새는 보험료 잡는 법]**
> · 불필요한 중복 특약 정리로 월 3~5만 원 절약
> · 내 보험 점수 & 부족 보장 1분 무료 진단
> 👉 네이버나 구글에 **[보험리밸런스]** 검색
"""

    @classmethod
    def pick_daily_scenario(cls, specific_topic_id: Optional[int] = None) -> Dict[str, Any]:
        """매일 다른 카테고리와 최적의 페르소나를 가중치 확률로 자동 추첨"""
        # 1. 이전 히스토리 로드 (연속 중복 방지)
        history = cls._load_history()
        last_persona = history.get("last_persona", "")
        last_category = history.get("last_category", "")

        # 2. 가중치 기반 카테고리 추첨
        categories = [item[0] for item in cls.CATEGORIES_WEIGHTED]
        weights = [item[1] for item in cls.CATEGORIES_WEIGHTED]
        
        # 이전과 다른 카테고리 우선 선택 시도
        chosen_category = random.choices(categories, weights=weights, k=1)[0]
        category_info = next(item for item in cls.CATEGORIES_WEIGHTED if item[0] == chosen_category)

        # 3. 해당 카테고리에 가장 어울리는 페르소나 매칭 (이전 페르소나 제외 우선)
        candidate_personas = [
            p_key for p_key, p_val in cls.PERSONAS.items()
            if chosen_category in p_val["preferred_categories"] and p_key != last_persona
        ]
        if not candidate_personas:
            candidate_personas = [p_key for p_key in cls.PERSONAS.keys() if p_key != last_persona] or list(cls.PERSONAS.keys())

        chosen_persona_key = random.choice(candidate_personas)
        persona_data = cls.PERSONAS[chosen_persona_key]

        # 4. 상태 저장
        cls._save_history({
            "last_persona": chosen_persona_key,
            "last_category": chosen_category,
            "last_topic_id": specific_topic_id or 1
        })

        logger.info(f"🎲 [InsuranceBlogScenarioDirector] 오늘 추첨 결과: 카테고리={chosen_category}, 페르소나={persona_data['name']}")

        return {
            "category_key": chosen_category,
            "category_name": category_info[2],
            "persona_key": chosen_persona_key,
            "persona_name": persona_data["name"],
            "persona_tone": persona_data["tone_description"],
            "persona_intro_hook": persona_data["hook_intro"],
            "visual_box_1": cls.VISUAL_BOX_1.strip(),
            "visual_box_2": cls.VISUAL_BOX_2.strip(),
            "search_keyword": cls.SEARCH_KEYWORD,
            "brand_name": cls.BRAND_NAME
        }

    @classmethod
    def build_system_instruction(cls, scenario: Dict[str, Any]) -> str:
        """선택된 페르소나와 비주얼 훅 박스가 주입된 완벽한 System Instruction 생성"""
        return f"""
당신은 대한민국 1위 네이버/티스토리 파워 블로거이자 '{scenario["persona_name"]}'입니다.

[오늘의 화자(페르소나) 설정]
- 화자: {scenario["persona_name"]}
- 말투 및 톤앤매너: {scenario["persona_tone"]}
- 도입부 권장 호흡: "{scenario["persona_intro_hook"]}"

[글쓰기 & 비주얼 구조화 절대 원칙]
1. 분량 및 모바일 최적화 호흡:
   - **분량: 한글 공백 포함 1,300자 내외 (1,300~1,500자)**로 알차고 탄탄하게 작성.
   - 모바일 독자의 80%는 정독하지 않고 5~10초 만에 스크롤을 훑어보므로, **1~2줄 단위로 시원하게 줄바꿈(엔터 2번으로 문단 분리)**.
   - 눈에 쏙 들어오는 이모지(🚨, 💸, 💡, 🔖, 👉, 🚗, 🧠, 🏥, 👶) 적극 활용.
   - "~합니다" 일변도의 딱딱한 문어체 금지 ❌, 화자의 실제 말투에 맞는 생생한 구어체 사용 ⭕

2. 🚨 [절대 엄수: 현실적 보험료 & 과장 뻥튀기 0% 원칙 (REALISTIC ACCURACY)]:
   - ❌ 실손보험 단독을 10~15만 원 낸다거나, 실손 하나로 7~8만 원 아꼈다는 식의 비현실적 허위 수치 절대 작성 금지! (독자의 신뢰가 즉시 깨짐)
   - ⭕ **보험 종류별 현실적 수치 가이드라인을 철저히 준수할 것**:
     * **단독 실손보험**: 20~40대 기준 월 1만~3만 원대 (50대/유병자 4~7만 원대). 4세대 전환 시 월 1~2만 원(치킨 1마리 값) 절약.
     * **운전자보험**: 기본 9,900원~1.5만 원대. 과거 불필요한 적립금 3~4만 원 내던 것을 순수보장형 1만 원대로 슬림화하여 월 1~2만 원 다이어트.
     * **암·뇌·심 3대 진단비 / 종합보험**: 1인 기준 월 7~12만 원대. 중복 특약 정리나 비효율 갱신형 조정으로 월 2~4만 원 절감.
     * **가계 전체 합산(3~4인 가족 전체)**: 월 40~60만 원대. 가족 전체 중복 보장 다이어트로 월 5~8만 원(통신비 1달 치) 절감.
   - 소비자가 실제 본인 영수증과 고지서를 보듯 100% 고개를 끄덕일 수 있는 정직하고 실질적인 체감 수치만 작성할 것.

3. 스키머(훑어보는 사람) 시선 장악용 [2단 비주얼 훅 박스] (본문에 인용구 '>' 형식으로 필수 삽입):
   - **1단 박스 (본문 1/3 지점 - 첫 번째 충격 약관 직후)**:
{scenario["visual_box_1"]}

   - **2단 박스 (본문 마무리 직전 - 절약 쾌감 직후)**:
{scenario["visual_box_2"]}

4. 🚫 [텍스트 안내문 삽입 절대 금지]:
   - 본문에 `[이미지: ...]`, `[사진: ...]`, `[16:9 ...]` 같은 지시어/안내 문구를 **일절 쓰지 마십시오**.
   - 100% 사람이 읽는 순수한 본문 스토리와 비주얼 훅 박스로만 꽉 채우십시오.

5. 광고 심의(금소법) 100% 면제:
   - 특정 보험사 비방/추천 금지, 설계사 연락처/카톡 상담 링크 삽입 일절 금지.
   - 100% 순수 정보 공유 썰 + 포털 검색 유도(Search CTA: [{scenario["search_keyword"]}])로 심의 완전 면제.

[반환 형식: JSON 포맷 필수]
반드시 유효한 JSON 형식으로만 응답하십시오:
{{
  "title_naver": "네이버 블로그용 5초 클릭 유도 제목 (충격 썰/이모지/질문형)",
  "title_tistory": "티스토리 SEO 최적화 정보형 꿀팁 제목",
  "title_brunch": "브런치스토리용 감성적 가계부 절약 에세이 제목",
  "body_markdown": "2단 비주얼 박스와 모바일 1~2줄 호흡이 완벽히 구현된 1,300~1,500자 완성형 본문 (이미지 안내문 일절 없음)",
  "summary": "1줄 요약 메타 디스크립션",
  "tags": ["태그1", "태그2", "태그3", "태그4", "태그5"],
  "visual_prompt": "A stylish 16:9 editorial photograph of a modern Korean lifestyle scene matching the topic, sunny warm natural daylight, clean minimalist aesthetic 8k"
}}
"""

    @classmethod
    def _load_history(cls) -> Dict[str, Any]:
        """이전 시나리오 상태 로드"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as fp:
                    return json.load(fp)
            except Exception:
                pass
        return {}

    @classmethod
    def _save_history(cls, state: Dict[str, Any]):
        """시나리오 상태 저장"""
        try:
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(STATE_FILE, "w", encoding="utf-8") as fp:
                json.dump(state, fp, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"시나리오 상태 저장 실패: {e}")


if __name__ == "__main__":
    scenario = InsuranceBlogScenarioDirector.pick_daily_scenario(1)
    print("=== 오늘 추첨된 시나리오 ===")
    print(f"카테고리: {scenario['category_name']}")
    print(f"페르소나: {scenario['persona_name']}")
    print(f"말투 톤: {scenario['persona_tone']}")
    print("\n=== 시스템 프롬프트 미리보기 ===")
    sys_prompt = InsuranceBlogScenarioDirector.build_system_instruction(scenario)
    print(sys_prompt[:400] + "...")
