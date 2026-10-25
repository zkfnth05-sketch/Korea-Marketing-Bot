# -*- coding: utf-8 -*-
"""
modules/drama_engine/drama_scenario_director.py
===================================================================================================
[DramaScenarioDirector] - AI 숏드라마 일일 시나리오 디렉터 (365일 무한 시나리오 엔진)
---------------------------------------------------------------------------------------------------
벤치마킹 오픈소스:
- EvoLinkAI/ai-short-drama - OnlyShot 4컷 시네마틱 드라마 구조
- HVision-NKU/StoryDiffusion (캐릭터 & 씬 일관성 앵커)

[4컷 시네마틱 드라마 구조 - 총 20초 / 컷별 화자 100% 단일화]
  - Cut 1 (도파민 훅, 3초)   : 여주인공 독백/상황 훅            -> speaker_gender = "female"
  - Cut 2 (반문/조언, 6초)   : 남주인공의 반문/조언 (단독 발화)  -> speaker_gender = "male"
  - Cut 3 (반전 솔루션, 7초) : 여주인공의 솔루션 체감/리액션     -> speaker_gender = "female"
  - Cut 4 (여운 & CTA, 4초)  : 여주인공의 결말 + 공식 검색어 CTA -> speaker_gender = "female"

[대표님 절대 규격]
  한 컷 안에서 남녀가 섞여 발화하면 단일 얼굴로 립싱크하는 S2V 엔진 특성상
  반드시 성별 불일치(남자가 말하는데 여자가 립싱크)가 발생한다.
  따라서 각 컷의 대사는 반드시 '한 명의 화자'만 발화하도록 대본을 단일화하고,
  cuts_data 각 컷 객체에 speaker_gender 를 명시하여 이미지/음성/립싱크 전 구간에 전파한다.

[365일 무한 시나리오 엔진]
  - 8대 스펙트럼 장르 x 10종 럭셔리 로케이션 x 14종 프리미엄 폴백 템플릿
  - GeminiDramaScenarioWriter: 9키 풀 롤오버 + 15초 타임아웃 + 4컷 JSON 스키마 강제
  - 실패 시 사유를 기록하고 폴백 템플릿으로 무중단 로테이션
===================================================================================================
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
from dataclasses import dataclass, asdict
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

# [2026-10-23 통합 패치] 히스토리 / 플래너 / 예산 / 폴백풀 연동
try:
    from .drama_history_store import DramaHistoryStore
    from .drama_variation_planner import DailyVariationPlanner
    from .drama_cut_budget import CutBudgetValidator
    import modules.drama_engine.drama_fallback_pool as _fallback_pool_mod
    _INTEGRATED_MODULES = True
except Exception as _ie:
    _INTEGRATED_MODULES = False
    logging.getLogger("DramaScenarioDirector").warning(
        "[Director] 통합 모듈 임포트 실패 → 레거시 모드 | %s", _ie
    )

from .drama_character_anchor import DramaCharacterAnchor, CUT_SPEAKER_GENDER

logger = logging.getLogger("DramaScenarioDirector")

# 브랜드 공식 검색어 (절대 불변 상수)
BRAND_SEARCH_KEYWORDS: Dict[str, str] = {
    "aura": "아우라AI데이팅",
    "insurance": "보험 리밸런스",
    "stock": "스톡마스터 AI",
}

BRAND_DISPLAY_NAMES: Dict[str, str] = {
    "aura": "Aura AI 데이팅",
    "insurance": "보험 리밸런스",
    "stock": "StockMaster AI",
}

BRAND_DOMAINS: Dict[str, str] = {
    "aura": "aura-ai-dating.vercel.app",
    "insurance": "insure-rebalance.vercel.app",
    "stock": "stockmaster-ai.vercel.app",
}

CUT_DURATIONS: Dict[str, int] = {
    "cut1": 3,
    "cut2": 6,
    "cut3": 7,
    "cut4": 4,
}
TOTAL_DURATION = sum(CUT_DURATIONS.values())  # 20s

# ==============================================================================
# 8대 스펙트럼 장르 (DRAMA_GENRE_SPECTRUMS)
#   소개팅 빌런 일색에서 벗어나 설렘/위트/쿨한연애/직진고백/가치관 매칭 등
#   8개 축을 골고루 로테이션하여 365일 내내 신선한 대본을 생성한다.
# ==============================================================================
DRAMA_GENRE_SPECTRUMS: List[Dict[str, str]] = [
    {
        "id": "fluttering",
        "name": "설렘 & 심쿵 모먼트",
        "tone": "두근거림, 떨림, 첫 만남의 설렘, 심장이 내려앉는 순간",
        "guide": "상대의 사소한 배려나 눈맞춤에서 시작된 설렘을 섬세하게 그린다.",
    },
    {
        "id": "witty",
        "name": "현실 티키타카 & 위트",
        "tone": "재치 있는 말싸움, 현실 공감, 웃음 포인트",
        "guide": "2030 세대가 실제로 주고받는 티키타카 대화의 리듬을 살린다.",
    },
    {
        "id": "cool",
        "name": "쿨한 현대 연애관",
        "tone": "쿨내, 거리감, 자기주도적 연애, 집착 없음",
        "guide": "서로의 생활을 존중하는 성숙하고 쿨한 연애 태도를 보여준다.",
    },
    {
        "id": "direct",
        "name": "반전 매력 & 직진 고백",
        "tone": "반전, 돌직구, 직진 고백, 의외의 매력",
        "guide": "조용하던 인물이 갑자기 직진하는 반전의 카타르시스를 만든다.",
    },
    {
        "id": "firsttalk",
        "name": "데이팅 첫 대화 꿀팁",
        "tone": "실용 팁, 오프닝 멘트, 대화 이어가기 노하우",
        "guide": "첫 대화에서 막히는 2030 세대에게 실질적인 해법을 제시한다.",
    },
    {
        "id": "values",
        "name": "가치관 & 라이프스타일 매칭",
        "tone": "소비관, 생활패턴, 가치관 일치, 정밀 매칭",
        "guide": "겉모습이 아닌 가치관과 라이프스타일의 일치를 조명한다.",
    },
    {
        "id": "closure",
        "name": "지난 인연 정리 & 새로운 설렘",
        "tone": "미련 정리, 이별 극복, 새 출발, 재회의 설렘",
        "guide": "과거 인연을 정리하고 새로운 설렘으로 나아가는 회복의 서사를 담는다.",
    },
    {
        "id": "destiny",
        "name": "황금 성비 & 운명적 만남",
        "tone": "50대50 성비, 운명적 조우, 우연 같은 필연",
        "guide": "검증된 성비 위에서 이뤄지는 운명적 만남의 감동을 그린다.",
    },
]

GENRE_BY_ID: Dict[str, Dict[str, str]] = {g["id"]: g for g in DRAMA_GENRE_SPECTRUMS}

# ==============================================================================
# 2030 실내 럭셔리 데이팅 로케이션 10종 풀
#   - 야외/부적절 장소(삼청동 돌담길 벤치, 강남역 횡단보도, 편의점 파라솔 등)는 영구 퇴출
#   - 2030 세대가 실제로 소개팅/데이트를 즐기는 '실내 럭셔리 무드' 공간만 수록
# ==============================================================================
LUXURY_DATING_LOCATIONS: List[str] = [
    "은은한 앰비언트 조명의 성수동 아늑한 무드 카페 테이블",
    "촛불과 재즈 선율이 흐르는 청담동 프라이빗 와인바 테이블",
    "따뜻한 우드톤 인테리어의 한남동 감성 에스프레소 바 카운터석",
    "세련된 대리석 테이블이 있는 도산공원 모던 브런치 비스트로",
    "통창 너머 시티뷰가 펼쳐진 강남 부티크 라운지 카페",
    "은은한 간접 조명의 연남동 북유럽풍 디저트 카페 안쪽 자리",
    "차분한 뮤트톤 가구가 놓인 압구정 미니멀 티 라운지 소파석",
    "클래식 인테리어와 잔잔한 샹송이 흐르는 서래마을 클래식 비스트로",
    "빈티지 조명 아래 라이브 재즈가 흐르는 이태원 빈티지 재즈 펍 테이블",
    "유리 돔 아래 도심 야경이 내려다보이는 한남동 루프탑 실내 글라스 라운지",
]

# 브랜드별 로케이션 풀 (aura 는 럭셔리 데이팅 10종 전량 사용)
LOCATION_POOLS: Dict[str, List[str]] = {
    "aura": LUXURY_DATING_LOCATIONS,
    "insurance": [
        "대학병원 원무과 앞 환자 및 보호자 대기실 의자",
        "로펌 상담실 대형 원목 회의 테이블 앞",
        "20년 된 빛바랜 보험 증권이 널브러진 가족 식탁",
        "암센터 외래 진료실 앞 긴장된 정적의 복도 벤치",
        "보험사 고객센터 접수 창구 앞 파티션",
        "자동차 사고 현장 갓길의 비상등 깜빡이는 도로변",
        "야간 응급실 입구 구급차 사이렌 불빛 아래",
    ],
    "stock": [
        "불 꺼진 여의도 증권사 트레이딩룸의 붉은 모니터 불빛 앞",
        "심야 탕비실에서 스마트폰 파란색 하한가창 보고 멍때리는 정수기 앞",
        "차가운 강바람 부는 마포대교 난간 위 야경",
        "새벽 4시 강남역 24시간 카페 구석 노트북 충전석",
        "판교 IT 벤처기업 야근 후 텅 빈 옥상 흡연구역",
        "원룸 방바닥에 배달음식 두고 켜놓은 3개 주식 차트 모니터",
        "지하철 막차 안에서 손잡이 잡고 주식 커뮤니티 새로고침하는 모습",
    ],
}


# ==============================================================================
# 14종 프리미엄 폴백 템플릿 풀 (FALLBACK_TEMPLATES)
#   - 소개팅 빌런 일색에서 완전히 탈피
#   - 8대 스펙트럼(설렘/위트/쿨한연애/직진고백/첫대화/가치관/인연정리/운명)이 골고루 배치
#   - 각 템플릿은 4컷 완성형 대본 (cut1~cut4) + 화자 성별 단일화 준수
#   - speech 길이 규격: cut1 12~20자 / cut2 25~35자 / cut3 30~42자 / cut4 15~24자
# ==============================================================================
FALLBACK_TEMPLATES: List[Dict[str, Any]] = [
    # ---------------------------------------------------------------- 01 설렘
    {
        "id": "fb01_fluttering",
        "genre_id": "fluttering",
        "theme": "눈이 마주친 순간, 심장이 먼저 알아봤다",
        "cuts": [
            {"role": "hook", "speaker_gender": "female",
             "speech": "이 사람, 왜 이렇게 눈이 따뜻하지."},
            {"role": "dialogue", "speaker_gender": "male",
             "speech": "아까부터 계속 웃고 계셔서 저도 모르게 따라 웃었어요."},
            {"role": "solution", "speaker_gender": "female",
             "speech": "이런 사람 처음이야. 말 한마디에 하루가 다 포근해지는 기분."},
            {"role": "cta", "speaker_gender": "female",
             "speech": "설렘 찾는다면 네이버에 아우라AI데이팅 한번 검색해보세요."},
        ],
    },
    # ---------------------------------------------------------------- 02 위트
    {
        "id": "fb02_witty",
        "genre_id": "witty",
        "theme": "티키타카가 통하는 사람이 결국 오래 간다",
        "cuts": [
            {"role": "hook", "speaker_gender": "female",
             "speech": "이 대화, 왜 안 끊기지?"},
            {"role": "dialogue", "speaker_gender": "male",
             "speech": "제가 말재주가 좋은 게 아니라, 누나 반응이 너무 좋아서요."},
            {"role": "solution", "speaker_gender": "female",
             "speech": "웃으면서 대화가 이어지는 사람. 이게 진짜 잘 맞는 거구나 싶었어."},
            {"role": "cta", "speaker_gender": "female",
             "speech": "대화 통하는 사람 만나려면 네이버에 아우라AI데이팅 검색."},
        ],
    },
    # ---------------------------------------------------------------- 03 쿨한 연애
    {
        "id": "fb03_cool",
        "genre_id": "cool",
        "theme": "서로의 하루를 존중하는 쿨한 연애",
        "cuts": [
            {"role": "hook", "speaker_gender": "female",
             "speech": "연락 안 와도 불안하지 않아."},
            {"role": "dialogue", "speaker_gender": "male",
             "speech": "바쁘면 바쁜 대로, 쉬면 쉬는 대로. 그게 편하지 않아요?"},
            {"role": "solution", "speaker_gender": "female",
             "speech": "집착 대신 신뢰를 고르는 사람. 이게 성숙한 연애라는 걸 알았어."},
            {"role": "cta", "speaker_gender": "female",
             "speech": "쿨한 연애 원한다면 네이버에 아우라AI데이팅 검색해보세요."},
        ],
    },
    # ---------------------------------------------------------------- 04 직진 고백
    {
        "id": "fb04_direct",
        "genre_id": "direct",
        "theme": "조용하던 사람의 돌직구, 그게 반전이었다",
        "cuts": [
            {"role": "hook", "speaker_gender": "female",
             "speech": "이 사람, 오늘 뭔가 달라."},
            {"role": "dialogue", "speaker_gender": "male",
             "speech": "돌려 말하는 거 잘 못해서요. 저 누나한테 진심이에요."},
            {"role": "solution", "speaker_gender": "female",
             "speech": "어제까지 조용하던 사람이 오늘 이렇게 직진할 줄은 정말 몰랐어."},
            {"role": "cta", "speaker_gender": "female",
             "speech": "직진하는 사람 만나려면 네이버에 아우라AI데이팅 검색."},
        ],
    },
    # ---------------------------------------------------------------- 05 첫 대화
    {
        "id": "fb05_firsttalk",
        "genre_id": "firsttalk",
        "theme": "첫 대화, 오프닝 한마디가 판을 바꾼다",
        "cuts": [
            {"role": "hook", "speaker_gender": "female",
             "speech": "첫 마디, 뭐라고 해야 할까."},
            {"role": "dialogue", "speaker_gender": "male",
             "speech": "여기 디저트 유명하다던데, 누나 취향은 어떤 쪽이에요?"},
            {"role": "solution", "speaker_gender": "female",
             "speech": "질문 하나로 대화가 이렇게 풀리다니. 첫 마디가 정말 중요했구나."},
            {"role": "cta", "speaker_gender": "female",
             "speech": "첫 대화 팁이 필요하면 네이버에 아우라AI데이팅 검색."},
        ],
    },
    # ---------------------------------------------------------------- 06 가치관
    {
        "id": "fb06_values",
        "genre_id": "values",
        "theme": "겉모습보다 생활이 맞는 사람",
        "cuts": [
            {"role": "hook", "speaker_gender": "female",
             "speech": "이 사람, 생활이 나랑 닮았어."},
            {"role": "dialogue", "speaker_gender": "male",
             "speech": "주말엔 집에서 쉬는 편이에요. 사람 많은 곳보다 조용한 게 좋아서요."},
            {"role": "solution", "speaker_gender": "female",
             "speech": "취향도 소비관도 이렇게 겹치다니. 조건보다 생활이 맞는 게 중요했어."},
            {"role": "cta", "speaker_gender": "female",
             "speech": "가치관 맞는 사람 찾는다면 네이버에 아우라AI데이팅 검색."},
        ],
    },
    # ---------------------------------------------------------------- 07 인연 정리
    {
        "id": "fb07_closure",
        "genre_id": "closure",
        "theme": "지난 인연을 정리하고 새 설렘으로",
        "cuts": [
            {"role": "hook", "speaker_gender": "female",
             "speech": "이제 그 사람은 놓아주기로 했어."},
            {"role": "dialogue", "speaker_gender": "male",
             "speech": "지난 일에 마음 쓰느라 지금 좋은 사람 놓치면 아깝잖아요."},
            {"role": "solution", "speaker_gender": "female",
             "speech": "미련을 내려놓으니 보이는 게 달라졌어. 새 사람이 이렇게 반갑다니."},
            {"role": "cta", "speaker_gender": "female",
             "speech": "새 출발 원한다면 네이버에 아우라AI데이팅 검색해보세요."},
        ],
    },
    # ---------------------------------------------------------------- 08 운명
    {
        "id": "fb08_destiny",
        "genre_id": "destiny",
        "theme": "우연 같은 필연, 황금 성비의 만남",
        "cuts": [
            {"role": "hook", "speaker_gender": "female",
             "speech": "이런 곳에서 마주칠 줄이야."},
            {"role": "dialogue", "speaker_gender": "male",
             "speech": "저도 같은 생각했어요. 이건 우연이 아니라 인연 같다고요."},
            {"role": "solution", "speaker_gender": "female",
             "speech": "검증된 성비 위에서 만난 사람. 우연이 이렇게 설레는 일이구나."},
            {"role": "cta", "speaker_gender": "female",
             "speech": "운명적 만남 원한다면 네이버에 아우라AI데이팅 검색."},
        ],
    },
    # ---------------------------------------------------------------- 09 설렘
    {
        "id": "fb09_fluttering",
        "genre_id": "fluttering",
        "theme": "손끝이 스친 순간, 시간이 멈췄다",
        "cuts": [
            {"role": "hook", "speaker_gender": "female",
             "speech": "손이 닿았는데 왜 이러지."},
            {"role": "dialogue", "speaker_gender": "male",
             "speech": "죄송해요, 일부러 그런 건 아닌데... 얼굴이 너무 빨개지네요."},
            {"role": "solution", "speaker_gender": "female",
             "speech": "사과하는 그 얼굴이 더 설레서, 오히려 내가 먼저 웃음이 났어."},
            {"role": "cta", "speaker_gender": "female",
             "speech": "심쿵하는 순간 원한다면 네이버에 아우라AI데이팅 검색."},
        ],
    },
    # ---------------------------------------------------------------- 10 위트
    {
        "id": "fb10_witty",
        "genre_id": "witty",
        "theme": "웃긴 사람이 오래 간다, 진짜로",
        "cuts": [
            {"role": "hook", "speaker_gender": "female",
             "speech": "이 사람, 웃기다 못해 귀엽네."},
            {"role": "dialogue", "speaker_gender": "male",
             "speech": "제 매력은 얼굴이 아니라 입담이에요. 그거면 충분하죠?"},
            {"role": "solution", "speaker_gender": "female",
             "speech": "하루 종일 웃게 만드는 사람. 이게 진짜 매력이구나 처음 알았어."},
            {"role": "cta", "speaker_gender": "female",
             "speech": "웃긴 사람 만나고 싶다면 네이버에 아우라AI데이팅 검색."},
        ],
    },
    # ---------------------------------------------------------------- 11 쿨한 연애
    {
        "id": "fb11_cool",
        "genre_id": "cool",
        "theme": "각자의 속도로 걷는 두 사람",
        "cuts": [
            {"role": "hook", "speaker_gender": "female",
             "speech": "우리, 서두르지 말자."},
            {"role": "dialogue", "speaker_gender": "male",
             "speech": "좋아요. 대신 방향은 같게. 그거면 충분하다고 생각해요."},
            {"role": "solution", "speaker_gender": "female",
             "speech": "재촉하지 않는 사람과 걷는 게 이렇게 편할 줄 몰랐어. 이게 맞는 거야."},
            {"role": "cta", "speaker_gender": "female",
             "speech": "편한 연애 원한다면 네이버에 아우라AI데이팅 검색해보세요."},
        ],
    },
    # ---------------------------------------------------------------- 12 직진 고백
    {
        "id": "fb12_direct",
        "genre_id": "direct",
        "theme": "오늘은 돌려 말하지 않겠습니다",
        "cuts": [
            {"role": "hook", "speaker_gender": "female",
             "speech": "뭐라고 말하려는 거야."},
            {"role": "dialogue", "speaker_gender": "male",
             "speech": "누나랑 더 있고 싶어요. 오늘 헤어지기 싫어서 이 말 꺼냈어요."},
            {"role": "solution", "speaker_gender": "female",
             "speech": "이렇게 솔직한 고백은 처음이야. 숨기지 않는 마음이 이렇게 따뜻하구나."},
            {"role": "cta", "speaker_gender": "female",
             "speech": "솔직한 고백 받고 싶다면 네이버에 아우라AI데이팅 검색."},
        ],
    },
    # ---------------------------------------------------------------- 13 가치관
    {
        "id": "fb13_values",
        "genre_id": "values",
        "theme": "돈보다 시간을 같이 쓰는 사람",
        "cuts": [
            {"role": "hook", "speaker_gender": "female",
             "speech": "이 사람, 기준이 나랑 같아."},
            {"role": "dialogue", "speaker_gender": "male",
             "speech": "비싼 데보다 같이 오래 있을 수 있는 곳이 좋아요. 저는 그게 중요해요."},
            {"role": "solution", "speaker_gender": "female",
             "speech": "화려함보다 함께하는 시간을 고르는 사람. 이게 진짜 가치관이구나."},
            {"role": "cta", "speaker_gender": "female",
             "speech": "가치관 맞는 사람 만나려면 네이버에 아우라AI데이팅 검색."},
        ],
    },
    # ---------------------------------------------------------------- 14 운명
    {
        "id": "fb14_destiny",
        "genre_id": "destiny",
        "theme": "결국 다시 만날 사람은 만난다",
        "cuts": [
            {"role": "hook", "speaker_gender": "female",
             "speech": "이 사람, 어디서 봤던 것 같아."},
            {"role": "dialogue", "speaker_gender": "male",
             "speech": "저도요. 처음 보는데 왜 이렇게 익숙한지 모르겠어요."},
            {"role": "solution", "speaker_gender": "female",
             "speech": "처음인데 오래된 사람 같아. 이런 게 운명이라는 건가 싶었어."},
            {"role": "cta", "speaker_gender": "female",
             "speech": "운명 같은 사람 찾는다면 네이버에 아우라AI데이팅 검색."},
        ],
    },
]

# 브랜드별 폴백 템플릿 (aura 는 14종 전량, 타 브랜드는 자체 풀)
BRAND_FALLBACK_POOLS: Dict[str, List[Dict[str, Any]]] = {
    "aura": FALLBACK_TEMPLATES,
}


# ==============================================================================
# 고정 주인공 페르소나 (365일 내내 동일 인물 - 캐릭터 일관성 앵커)
# ==============================================================================
FIXED_PERSONAS: Dict[str, str] = {
    "female": (
        "서연 (20대 중후반, 청순하고 세련된 외모, 단정한 긴 생머리, "
        "차분하지만 속마음이 풍부한 말투, 감정을 섬세하게 표현함)"
    ),
    "male": (
        "민준 (20대 후반, 깔끔한 댄디 스타일, 짧고 단정한 헤어, "
        "부드럽고 배려심 깊은 말투, 진심을 담아 조곤조곤 이야기함)"
    ),
}

# Gemini 모델 우선순위 (앞에서부터 시도)
GEMINI_MODELS: List[str] = ["gemini-2.5-flash", "gemini-3.1-flash-lite"]

# 15초 타임아웃 / 최대 3개 키 롤오버
GEMINI_TIMEOUT_SEC = 15
GEMINI_MAX_KEY_ROLLOVER = 3

# 4컷 JSON 스키마 기본값 (실측 예산 계산 전 폴백용)
CUT_SCHEMA_SPEC = """[
  {"cut": 1, "role": "hook",     "duration": 3, "speaker_gender": "female", "speech": "17~35자 내외"},
  {"cut": 2, "role": "dialogue", "duration": 6, "speaker_gender": "male",   "speech": "21~33자 내외"},
  {"cut": 3, "role": "solution", "duration": 7, "speaker_gender": "female", "speech": "27~35자 내외"},
  {"cut": 4, "role": "cta",      "duration": 4, "speaker_gender": "female", "speech": "19~35자 내외 (브랜드 공식 검색어 필수 포함)"}
]"""

_BUDGET_SCHEMA_FALLBACK = CUT_SCHEMA_SPEC  # CutBudgetValidator 로드 실패 시 사용


class GeminiDramaScenarioWriter:
    """Gemini 365일 무한 시나리오 생성기.

    - core.gemini_unified_keys.get_unified_gemini_keys() 9개 키 풀 연동
    - 15초 타임아웃, 최대 3개 키 롤오버
    - 4컷 JSON 스키마 강제 + 브랜드 공식 검색어 포함 유효성 검증
    - try-except pass 절대 배제: 모든 실패는 구조화 로그로 기록
    """

    def __init__(self, brand: str = "aura") -> None:
        self.brand = (brand or "aura").lower()
        self.search_keyword = BRAND_SEARCH_KEYWORDS.get(self.brand, BRAND_SEARCH_KEYWORDS["aura"])
        self.brand_name = BRAND_DISPLAY_NAMES.get(self.brand, BRAND_DISPLAY_NAMES["aura"])
        self.last_error: Optional[str] = None
        self.last_model: Optional[str] = None
        self.last_key_index: Optional[int] = None

    # ------------------------------------------------------------------ keys
    def _load_keys(self) -> List[str]:
        """9개 Gemini 키 풀 로드 (실패 시 빈 리스트 + 사유 기록)."""
        try:
            from core.gemini_unified_keys import get_unified_gemini_keys
        except Exception as exc:
            self.last_error = "key_import_failed: %s: %s" % (type(exc).__name__, exc)
            logger.error("[GeminiWriter] 키 모듈 임포트 실패 | %s", self.last_error)
            return []

        try:
            keys = get_unified_gemini_keys()
        except Exception as exc:
            self.last_error = "key_load_failed: %s: %s" % (type(exc).__name__, exc)
            logger.error("[GeminiWriter] 키 로드 실패 | %s", self.last_error)
            return []

        if isinstance(keys, dict):
            flat: List[str] = []
            for value in keys.values():
                if isinstance(value, (list, tuple)):
                    flat.extend([str(v).strip() for v in value if str(v).strip()])
                elif isinstance(value, str) and value.strip():
                    flat.append(value.strip())
            keys = flat

        if not isinstance(keys, (list, tuple)):
            self.last_error = "key_type_invalid: %s" % type(keys).__name__
            logger.error("[GeminiWriter] 키 타입 이상 | %s", self.last_error)
            return []

        cleaned = [str(k).strip() for k in keys if str(k).strip()]
        if not cleaned:
            self.last_error = "key_pool_empty"
            logger.error("[GeminiWriter] 키 풀이 비어 있습니다.")
        return cleaned

    # --------------------------------------------------------------- prompt
    def _build_prompt(
        self,
        date_str: str,
        genre: Dict[str, str],
        location: str,
        budget_text: Optional[str] = None,
        plan_addendum: Optional[str] = None,
    ) -> str:
        schema = budget_text or CUT_SCHEMA_SPEC
        extra = ("\n[오늘의 연출 변주]\n" + plan_addendum) if plan_addendum else ""
        return (
            "당신은 2030 세대를 겨냥한 한국형 숏드라마 최고 시나리오 작가입니다.\n"
            "아래 조건에 맞춰 4컷 시네마틱 드라마 대본을 JSON 으로만 출력하십시오.\n\n"
            "[오늘 날짜] %s\n"
            "[장르 스펙트럼] %s\n"
            "[장르 톤] %s\n"
            "[연출 가이드] %s\n"
            "[배경 로케이션] %s%s\n\n"
            "[고정 주인공 - 절대 변경 금지]\n"
            "  - 여주인공: %s\n"
            "  - 남주인공: %s\n\n"
            "[4컷 구조 - 총 20초]\n"
            "  - cut1 (hook, 3초, female 단독 발화): 상황을 던지는 도파민 훅.\n"
            "  - cut2 (dialogue, 6초, male 단독 발화): 남주인공의 반문 또는 조언.\n"
            "  - cut3 (solution, 7초, female 단독 발화): 여주인공의 반전 솔루션 체감.\n"
            "  - cut4 (cta, 4초, female 단독 발화): 여운 + CTA.\n\n"
            "[절대 규칙]\n"
            "  1. 한 컷 안에서 남녀가 섞여 말하지 마십시오. 컷당 화자는 반드시 1명입니다.\n"
            "  2. cut4 의 speech 에는 반드시 '%s' 라는 문구가 그대로 포함되어야 합니다.\n"
            "  3. 모든 speech 는 자연스러운 한국어 구어체이며 아래 출력 스키마의 자수 범위를 엄수하십시오.\n"
            "  4. 소개팅 빌런/불친절/무례 같은 부정적 소재는 금지합니다.\n"
            "  5. 출력은 아래 스키마의 JSON 배열 하나만. 설명/마크다운/코드펜스 금지.\n"
            "  6. ⚠️ 중요: JSON 내부의 한국어 대사 문자열 안에는 큰따옴표(\")를 절대 넣지 말고 "
            "작은따옴표(')만 사용하십시오.\n\n"
            "[출력 스키마 — 자수 범위는 Wan S2V 81프레임 제한 내 실측값 기준]\n%s\n"
        ) % (
            date_str,
            genre.get("name", ""),
            genre.get("tone", ""),
            genre.get("guide", ""),
            location,
            extra,
            FIXED_PERSONAS["female"],
            FIXED_PERSONAS["male"],
            self.search_keyword,
            schema,
        )

    # ---------------------------------------------------------------- parse
    @staticmethod
    def _extract_json(text: str) -> Optional[Any]:
        """LLM 응답에서 JSON 배열/객체를 강건하게 추출.

        [2026-10-23 2차 패치 — strict=False 방어]
        - 모든 json.loads 호출에 strict=False 적용:
          문자열 내부의 제어문자(\n, \r, \t)로 인한
          'Unterminated string' / 'Invalid control character' 오류를 완벽 방어한다.
        - 기존 배열/객체 폴백 로직 100% 보존
        - re.search 기반 코드블록(```json ... ```) 추출 단계 유지
        - 최종 실패 시 logger.warning 으로 원문 앞 120자 기록 (침묵 실패 금지)
        """
        if not text:
            logger.warning(
                "⚠️ [GeminiDramaScenarioWriter] JSON 파싱 실패: 빈 응답 | 원문 앞 120자: ''"
            )
            return None

        raw = text.strip()

        # 1) 코드펜스 제거
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        # 2) 정제된 원문 그대로 파싱 (strict=False)
        try:
            return json.loads(raw, strict=False)
        except Exception as e:
            first_err = e

        # 3) re.search 기반 코드블록 추출 (strict=False)
        m = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
        if m:
            block = m.group(1).strip()
            try:
                return json.loads(block, strict=False)
            except Exception:
                pass

        # 4) 본문 내 첫 '[' ~ 마지막 ']' 구간 시도 (strict=False)
        start = raw.find("[")
        end = raw.rfind("]")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(raw[start:end + 1], strict=False)
            except Exception:
                pass

        # 5) 객체 형태 시도 (strict=False)
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(raw[start:end + 1], strict=False)
            except Exception:
                pass

        # 6) 최종 실패 — 원문 앞 120자 로깅
        logger.warning(
            f"⚠️ [GeminiDramaScenarioWriter] JSON 파싱 실패: {first_err} | 원문 앞 120자: {text[:120]}"
        )
        return None

    def _validate_cuts(self, cuts: Any) -> Tuple[bool, str]:
        """4컷 스키마 + 화자 성별 + 검색어 포함 유효성 검증."""
        if not isinstance(cuts, list):
            return False, "cuts_not_list: %s" % type(cuts).__name__
        if len(cuts) != 4:
            return False, "cuts_length_invalid: %d" % len(cuts)

        expected = [
            ("hook", "female", 3),
            ("dialogue", "male", 6),
            ("solution", "female", 7),
            ("cta", "female", 4),
        ]
        for idx, (role, gender, duration) in enumerate(expected):
            cut = cuts[idx]
            if not isinstance(cut, dict):
                return False, "cut%d_not_dict" % (idx + 1)
            speech = str(cut.get("speech", "")).strip()
            if not speech:
                return False, "cut%d_speech_empty" % (idx + 1)
            got_role = str(cut.get("role", "")).strip()
            if got_role and got_role != role:
                return False, "cut%d_role_mismatch: %s != %s" % (idx + 1, got_role, role)
            got_gender = str(cut.get("speaker_gender", "")).strip().lower()
            if got_gender and got_gender != gender:
                return False, "cut%d_gender_mismatch: %s != %s" % (idx + 1, got_gender, gender)
            try:
                got_dur = int(cut.get("duration", duration))
            except Exception:
                got_dur = duration
            if got_dur != duration:
                return False, "cut%d_duration_mismatch: %s != %s" % (idx + 1, got_dur, duration)

        cta_speech = str(cuts[3].get("speech", ""))
        if self.search_keyword not in cta_speech:
            return False, "cta_keyword_missing: '%s'" % self.search_keyword
        return True, "ok"

    # ---------------------------------------------------------------- call
    def _call_gemini(self, api_key: str, model: str, prompt: str) -> Optional[str]:
        """단일 키/모델 호출 (15초 타임아웃). 실패 시 사유 기록 후 None."""
        try:
            import google.generativeai as genai
        except Exception as exc:
            self.last_error = "sdk_import_failed: %s: %s" % (type(exc).__name__, exc)
            logger.error("[GeminiWriter] google.generativeai 임포트 실패 | %s", self.last_error)
            return None

        try:
            genai.configure(api_key=api_key)
            model_obj = genai.GenerativeModel(model)
            resp = model_obj.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.95,
                    "top_p": 0.95,
                    "max_output_tokens": 2048,
                    "response_mime_type": "application/json",
                },
                request_options={"timeout": GEMINI_TIMEOUT_SEC},
            )
        except TypeError:
            # request_options 미지원 구버전 SDK 대응
            try:
                genai.configure(api_key=api_key)
                model_obj = genai.GenerativeModel(model)
                resp = model_obj.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.95,
                        "top_p": 0.95,
                        "max_output_tokens": 2048,
                        "response_mime_type": "application/json",
                    },
                )
            except Exception as exc:
                self.last_error = "generate_failed: %s: %s" % (type(exc).__name__, exc)
                logger.error("[GeminiWriter] 생성 실패(%s) | %s", model, self.last_error)
                return None
        except Exception as exc:
            self.last_error = "generate_failed: %s: %s" % (type(exc).__name__, exc)
            logger.error("[GeminiWriter] 생성 실패(%s) | %s", model, self.last_error)
            return None

        try:
            text = getattr(resp, "text", None)
            if not text:
                self.last_error = "empty_response_text"
                logger.error("[GeminiWriter] 빈 응답(%s)", model)
                return None
            return text
        except Exception as exc:
            self.last_error = "response_read_failed: %s: %s" % (type(exc).__name__, exc)
            logger.error("[GeminiWriter] 응답 읽기 실패(%s) | %s", model, self.last_error)
            return None

    # ---------------------------------------------------------------- main
    def generate(
        self,
        date_str: str,
        genre: Dict[str, str],
        location: str,
        budget_text: Optional[str] = None,
        plan_addendum: Optional[str] = None,
        cps_by_gender: Optional[Dict[str, float]] = None,
        voice_speed: float = 1.25,
    ) -> Tuple[Optional[List[Dict[str, Any]]], str]:
        """4컷 대본 생성. 반환: (cuts or None, 실패사유 or 'ok')"""
        self.last_error = None
        keys = self._load_keys()
        if not keys:
            return None, self.last_error or "key_pool_empty"

        prompt = self._build_prompt(date_str, genre, location, budget_text, plan_addendum)
        tried = 0
        last_reason = "unknown"

        for model in GEMINI_MODELS:
            for key_index, api_key in enumerate(keys):
                if tried >= GEMINI_MAX_KEY_ROLLOVER:
                    break
                tried += 1
                self.last_model = model
                self.last_key_index = key_index

                text = self._call_gemini(api_key, model, prompt)
                if not text:
                    last_reason = self.last_error or "call_failed"
                    logger.warning(
                        "[GeminiWriter] 롤오버 %d/%d | model=%s key#%d | %s",
                        tried, GEMINI_MAX_KEY_ROLLOVER, model, key_index, last_reason,
                    )
                    continue

                parsed = self._extract_json(text)
                if parsed is None:
                    last_reason = "json_parse_failed"
                    logger.warning(
                        "[GeminiWriter] JSON 파싱 실패 | model=%s key#%d", model, key_index
                    )
                    continue

                if isinstance(parsed, dict):
                    for candidate_key in ("cuts", "scenario", "data", "result"):
                        val = parsed.get(candidate_key)
                        if isinstance(val, list):
                            parsed = val
                            break
                        elif isinstance(val, dict):
                            parsed = [val[k] for k in sorted(val.keys()) if isinstance(val[k], dict)]
                            break
                    if isinstance(parsed, dict):
                        cut_keys = [k for k in sorted(parsed.keys()) if "cut" in k.lower() and isinstance(parsed[k], dict)]
                        if len(cut_keys) >= 4:
                            parsed = [parsed[k] for k in cut_keys]

                ok, reason = self._validate_cuts(parsed)
                if not ok:
                    last_reason = reason
                    logger.warning(
                        "[GeminiWriter] 유효성 검증 실패 | model=%s key#%d | %s",
                        model, key_index, reason,
                    )
                    continue

                # [2026-10-23 패치] cut budget 검증 — 위반 시 1회 재생성
                if _INTEGRATED_MODULES and cps_by_gender:
                    try:
                        _validator = CutBudgetValidator()
                        _cuts_for_budget = [
                            {
                                "cut_id": "cut%d" % (i + 1),
                                "speaker_gender": ["female", "male", "female", "female"][i],
                                "speech": str(c.get("speech", "")),
                            }
                            for i, c in enumerate(parsed)
                        ]
                        _budget_rows = _validator.validate_cuts(
                            _cuts_for_budget, cps_by_gender, speed=voice_speed
                        )
                        _violations = [r for r in _budget_rows if not r["ok"]]
                        if _violations:
                            vstr = "; ".join(
                                "%s %s" % (r["cut_id"], r["reason"]) for r in _violations
                            )
                            logger.warning(
                                "[GeminiWriter] 예산 위반 %d컷 — 재생성 시도 | %s",
                                len(_violations), vstr,
                            )
                            last_reason = "budget_violation_retry"
                            continue  # 다음 키/모델로 재생성
                    except Exception as _be:
                        logger.error(
                            "[GeminiWriter] 예산 검증 예외(무시하고 계속) | %s: %s",
                            type(_be).__name__, _be,
                        )

                logger.info(
                    "[GeminiWriter] 생성 성공 | model=%s key#%d genre=%s speed=%.2f",
                    model, key_index, genre.get("id"), voice_speed,
                )
                return parsed, "ok"

            if tried >= GEMINI_MAX_KEY_ROLLOVER:
                break

        self.last_error = last_reason
        logger.error(
            "[GeminiWriter] 최종 실패 | tried=%d | reason=%s", tried, last_reason
        )
        return None, last_reason


# ==============================================================================
# [DramaScenarioDirector] - 일일 시나리오 디렉터
# ==============================================================================
class DramaScenarioDirector:
    """365일 무한 시나리오 디렉터.

    - get_daily_drama_scenario(brand, date_str, use_ai=True)
    - use_ai=True  : GeminiDramaScenarioWriter 로 실시간 집필 시도
    - 실패 시      : 사유를 기록하고 14종 폴백 템플릿 로테이션
    - 반환 payload : 기존 6키 평탄화 / cuts_data / speaker_gender / visual 100% 호환
    """

    def __init__(self, brand: str = "aura") -> None:
        self.brand = (brand or "aura").lower()
        self.anchor = DramaCharacterAnchor(self.brand)
        self.char_anchor_builders: Dict[str, DramaCharacterAnchor] = {
            self.brand: self.anchor
        }
        self.writer = GeminiDramaScenarioWriter(self.brand)
        self.last_source: Optional[str] = None
        self.last_fallback_reason: Optional[str] = None

        # [2026-10-23 통합 패치] 히스토리 / 플래너 / 예산 검증기
        if _INTEGRATED_MODULES:
            try:
                self._history = DramaHistoryStore(self.brand)
                self._planner = DailyVariationPlanner(self.brand, self._history)
                self._budget = CutBudgetValidator()
                # CPS 캘리브레이션 (캐시 파일 있으면 즉시 반환)
                _calib = self._budget.calibrate_chars_per_sec()
                self._cps_by_gender: Optional[Dict[str, float]] = {
                    "female": _calib["female"],
                    "male": _calib["male"],
                }
            except Exception as _init_e:
                logger.error(
                    "[Director] 통합 모듈 초기화 실패 → 레거시 모드 | %s", _init_e
                )
                self._history = None
                self._planner = None
                self._budget = None
                self._cps_by_gender = None
        else:
            self._history = None
            self._planner = None
            self._budget = None
            self._cps_by_gender = None

    # ------------------------------------------------------------ selection
    @staticmethod
    def _stable_index(seed: str, modulo: int) -> int:
        """날짜 기반 결정론적 인덱스 (같은 날짜 = 같은 결과)."""
        if modulo <= 0:
            return 0
        digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
        return int(digest[:12], 16) % modulo

    def _pick_genre(self, date_str: str) -> Dict[str, str]:
        """플래너 사용 가능 시 중복 방지 장르 선택, 불가 시 해시 폴백."""
        if self._planner is not None:
            try:
                _plan = self._planner.plan(
                    date_str,
                    genre_ids=[g["id"] for g in DRAMA_GENRE_SPECTRUMS],
                    locations=(LOCATION_POOLS.get(self.brand) or LUXURY_DATING_LOCATIONS),
                )
                _idx = _plan.get("genre_index", 0)
                return DRAMA_GENRE_SPECTRUMS[_idx % len(DRAMA_GENRE_SPECTRUMS)]
            except Exception as _e:
                logger.error("[Director] 플래너 장르 선택 실패 | %s", _e)
        idx = self._stable_index("%s|genre|%s" % (self.brand, date_str), len(DRAMA_GENRE_SPECTRUMS))
        return DRAMA_GENRE_SPECTRUMS[idx]

    def _pick_location(self, date_str: str) -> str:
        """플래너 사용 가능 시 중복 방지 로케이션 선택, 불가 시 해시 폴백."""
        pool = LOCATION_POOLS.get(self.brand) or LUXURY_DATING_LOCATIONS
        if self._planner is not None:
            try:
                _plan = self._planner.plan(
                    date_str,
                    genre_ids=[g["id"] for g in DRAMA_GENRE_SPECTRUMS],
                    locations=pool,
                )
                _idx = _plan.get("location_index", 0)
                return pool[_idx % len(pool)]
            except Exception as _e:
                logger.error("[Director] 플래너 로케이션 선택 실패 | %s", _e)
        idx = self._stable_index("%s|loc|%s" % (self.brand, date_str), len(pool))
        return pool[idx]

    def _get_plan(self, date_str: str) -> Optional[Dict[str, Any]]:
        """플래너 plan dict 반환 (실패 시 None)."""
        if self._planner is None:
            return None
        try:
            return self._planner.plan(
                date_str,
                genre_ids=[g["id"] for g in DRAMA_GENRE_SPECTRUMS],
                locations=(LOCATION_POOLS.get(self.brand) or LUXURY_DATING_LOCATIONS),
            )
        except Exception as _e:
            logger.error("[Director] 플래너 plan 실패 | %s", _e)
            return None

    def _pick_fallback(
        self,
        date_str: str,
        genre_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """신규 32종 풀에서 genre_id 로 폴백 선택. 로드 실패 시 레거시 14종."""
        if _INTEGRATED_MODULES:
            try:
                _plan = self._get_plan(date_str)
                _seed = (_plan or {}).get("seed_hex") or date_str
                # 최근 7일 사용된 template_id 목록
                _avoid: List[str] = []
                if self._history is not None:
                    for _e in (self._history.recent(7) or []):
                        _tid = _e.get("template_id")
                        if _tid and _tid.startswith("fp_"):
                            _avoid.append(_tid)
                _gid = genre_id or "fluttering"
                return _fallback_pool_mod.pick_template(
                    _gid, avoid_ids=_avoid, seed_hex=_seed
                )
            except Exception as _fe:
                logger.error("[Director] 신규 폴백풀 선택 실패 → 레거시 | %s", _fe)
        pool = BRAND_FALLBACK_POOLS.get(self.brand) or FALLBACK_TEMPLATES
        idx = self._stable_index("%s|fb|%s" % (self.brand, date_str), len(pool))
        return pool[idx]

    # ------------------------------------------------------------- assembly
    def _normalize_cuts(self, raw_cuts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """4컷을 표준 cuts_data 로 정규화 (화자 성별/역할/길이 강제)."""
        spec = [
            ("cut1", "hook", "female", 3),
            ("cut2", "dialogue", "male", 6),
            ("cut3", "solution", "female", 7),
            ("cut4", "cta", "female", 4),
        ]
        out: List[Dict[str, Any]] = []
        for idx, (cut_id, role, gender, duration) in enumerate(spec):
            src = raw_cuts[idx] if idx < len(raw_cuts) else {}
            speech = str(src.get("speech", "")).strip()
            out.append({
                "cut_id": cut_id,
                "cut": idx + 1,
                "role": role,
                "duration_sec": duration,
                "duration": duration,
                "speaker_gender": gender,
                "speech": speech,
                "char_count": len(speech),
            })
        return out

    def _build_visual(
        self,
        location: str,
        genre: Dict[str, str],
        date_str: str = "",
        cut_speakers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """캐릭터 앵커 기반 4컷 비주얼 프롬프트 조립.

        [2026-10-23 패치]
        - 존재하지 않는 get_anchor_prompt() 호출을 전면 제거.
        - DramaCharacterAnchor.build_4cut_prompts() 를 정식 호출하여
          컷별 화자 단일화 + S2V 입 다문 상태(CLOSED_MOUTH_LOCK) 프롬프트를 바인딩한다.
        - 브랜드별 앵커 빌더를 캐시(self.char_anchor_builders)하여 재사용한다.
        """
        brand_key = (self.brand or "aura").lower()
        seed_str = date_str or date.today().isoformat()

        # 브랜드별 앵커 빌더 캐시 (미등록 브랜드는 즉석 생성)
        if not hasattr(self, "char_anchor_builders") or self.char_anchor_builders is None:
            self.char_anchor_builders = {}
        anchor_builder = self.char_anchor_builders.get(brand_key)
        if anchor_builder is None:
            try:
                anchor_builder = DramaCharacterAnchor(brand_key)
            except Exception as exc:
                logger.error(
                    "[Director] 앵커 빌더 생성 실패(%s) | %s: %s",
                    brand_key, type(exc).__name__, exc,
                )
                anchor_builder = self.anchor
            self.char_anchor_builders[brand_key] = anchor_builder

        # 컷별 화자 성별 확정 (CUT_SPEAKER_GENDER 절대 규격)
        resolved_speakers = dict(cut_speakers or CUT_SPEAKER_GENDER)

        try:
            visual_cuts = anchor_builder.build_4cut_prompts(
                date_seed=seed_str,
                location_desc=location,
                gender_lead="female",
                cut_speakers=resolved_speakers,
            )
        except Exception as exc:
            logger.error(
                "[Director] build_4cut_prompts 실패 | %s: %s", type(exc).__name__, exc
            )
            visual_cuts = []

        # 컷별 프롬프트 평탄화 (cut1_prompt ~ cut4_prompt) + visual_cuts 원본 보존
        cut_prompts: Dict[str, str] = {}
        for idx, vc in enumerate(visual_cuts):
            cut_prompts["cut%d_prompt" % (idx + 1)] = str(vc.get("prompt", ""))
        for idx in range(len(visual_cuts), 4):
            cut_prompts.setdefault("cut%d_prompt" % (idx + 1), "")

        female_anchor = ""
        male_anchor = ""
        try:
            female_anchor = anchor_builder.get_persona("female").get_identity_prompt()
            male_anchor = anchor_builder.get_persona("male").get_identity_prompt()
        except Exception as exc:
            logger.error(
                "[Director] 페르소나 조회 실패 | %s: %s", type(exc).__name__, exc
            )
            female_anchor = FIXED_PERSONAS["female"]
            male_anchor = FIXED_PERSONAS["male"]

        return {
            "location": location,
            "genre": genre.get("name", ""),
            "genre_tone": genre.get("tone", ""),
            "date_seed": seed_str,
            "female_anchor": female_anchor,
            "male_anchor": male_anchor,
            "cut1_prompt": cut_prompts.get("cut1_prompt", ""),
            "cut2_prompt": cut_prompts.get("cut2_prompt", ""),
            "cut3_prompt": cut_prompts.get("cut3_prompt", ""),
            "cut4_prompt": cut_prompts.get("cut4_prompt", ""),
            "visual_cuts": visual_cuts,
        }

    def _build_payload(
        self,
        date_str: str,
        genre: Dict[str, str],
        location: str,
        cuts_data: List[Dict[str, Any]],
        source: str,
        fallback_reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """다운스트림 100% 호환 payload 조립.

        [2026-10-23 2차 패치 — drama_pipeline_facade.py 하위호환]
        - 기존 키(brand_name/domain/search_keyword/cuts_data/theme/location) 100% 보존
        - 신규 별칭 키 동시 제공:
            cuts / official_search_keyword / topic_id / brand_display / brand_domain
            full_speech / speech_hook / speech_part1 / speech_part2 / speech_app / speech_cta
        - 두 키가 동일 객체를 가리키므로 다운스트림 어느 쪽을 읽어도 무손상.
        """
        speech_hook = cuts_data[0]["speech"]
        speech_part1 = cuts_data[1]["speech"]
        speech_part2 = cuts_data[2]["speech"]
        speech_app = cuts_data[2]["speech"]
        speech_cta = cuts_data[3]["speech"]
        full_speech = " ".join(
            [speech_hook, speech_part1, speech_part2, speech_cta]
        ).strip()

        theme_title = genre.get("name", "")
        if source == "gemini_ai":
            theme_title = "%s | %s" % (genre.get("name", ""), location.split(" ")[0])

        brand_key = self.brand
        brand_display = BRAND_DISPLAY_NAMES.get(brand_key, "")
        brand_domain = BRAND_DOMAINS.get(brand_key, "")
        official_keyword = BRAND_SEARCH_KEYWORDS.get(brand_key, "")

        # topic_id: 브랜드_날짜_시드해시 (결정론적 고유 식별자)
        seed_int = int(
            hashlib.sha256(
                ("%s|%s|%s" % (brand_key, date_str, genre.get("id", ""))).encode("utf-8")
            ).hexdigest()[:8],
            16,
        )
        topic_id = "%s_%s_%d" % (brand_key, date_str, seed_int)

        # ==================================================================
        # 🎯 [긴급 버그 수정] 컷별 visual 프롬프트 바인딩
        # ------------------------------------------------------------------
        # 문제: cuts_data 각 dict 에 'visual' 키가 없어서 다운스트림
        #       _prepare_scene_images 의 cut.get('visual', {}).get('prompt', '')
        #       가 항상 "" → Gemini 이미지 생성 미호출 → 에셋 폴백.
        # 해결: visual_dict 를 먼저 빌드하고, 각 컷에 visual_cuts[idx] 를 1:1 바인딩.
        # ==================================================================
        visual_dict = self._build_visual(
            location,
            genre,
            date_str=date_str,
            cut_speakers={c["cut_id"]: c["speaker_gender"] for c in cuts_data},
        )

        visual_cuts = visual_dict.get("visual_cuts", []) or []
        for idx, c in enumerate(cuts_data):
            if idx < len(visual_cuts):
                c["visual"] = visual_cuts[idx]
            else:
                c["visual"] = {
                    "cut_id": c.get("cut_id", "cut%d" % (idx + 1)),
                    "prompt": visual_dict.get("cut%d_prompt" % (idx + 1), ""),
                    "negative_prompt": "ugly, blurry, deformed, text, watermark, bad anatomy",
                    "speaker_gender": c.get("speaker_gender", "female"),
                }

        payload: Dict[str, Any] = {
            # --- 메타 (기존 키 100% 보존) ---
            "brand": brand_key,
            "brand_name": brand_display,
            "domain": brand_domain,
            "date": date_str,
            "source": source,
            "fallback_reason": fallback_reason,
            "genre_id": genre.get("id", ""),
            "genre_name": genre.get("name", ""),
            "genre_tone": genre.get("tone", ""),
            "theme": theme_title,
            "location": location,
            "search_keyword": official_keyword,
            "total_duration": TOTAL_DURATION,
            "total_duration_sec": TOTAL_DURATION,
            # --- [신규] 하위호환 별칭 키 ---
            "topic_id": topic_id,
            "brand_display": brand_display,
            "brand_domain": brand_domain,
            "official_search_keyword": official_keyword,
            # --- 6키 평탄화 (다운스트림 호환) ---
            "speech_hook": speech_hook,
            "speech_part1": speech_part1,
            "speech_part2": speech_part2,
            "speech_app": speech_app,
            "speech_cta": speech_cta,
            "full_speech": full_speech,
            # --- 컷 데이터 (cuts / cuts_data 동시 제공) ---
            "cuts": cuts_data,
            "cuts_data": cuts_data,
            "speaker_gender": [c["speaker_gender"] for c in cuts_data],
            "durations": [c["duration"] for c in cuts_data],
            # --- 비주얼 (위에서 1회 빌드한 visual_dict 재사용 — 중복 호출 제거) ---
            "visual": visual_dict,
            # --- 페르소나 ---
            "personas": dict(FIXED_PERSONAS),
            # --- [2026-10-23 5컷판 cut0] 상황 자막 카드 텍스트 ---
            "situation_text": self._build_situation_text(
                genre=genre, location=location, speech_hook=speech_hook,
            ),
        }
        return payload

    @staticmethod
    def _build_situation_text(genre, location, speech_hook):
        genre_name = (genre.get("name") or "").strip()
        loc_short  = location.split(" ")[0] if location else ""
        hook_prev  = speech_hook[:18] if speech_hook else ""
        lines = []
        if loc_short:  lines.append(loc_short)
        if genre_name: lines.append(genre_name)
        if hook_prev:  lines.append('"' + hook_prev + '..."')
        return "\n".join(lines[:3]) if lines else "지금 이 순간,\n무슨 일이 생겼냐면..."

    # ---------------------------------------------------------------- main
    def get_daily_drama_scenario(
        self,
        brand: Optional[str] = None,
        date_str: Optional[str] = None,
        use_ai: bool = True,
    ) -> Dict[str, Any]:
        """일일 시나리오 반환.

        Args:
            brand: 브랜드 키 (aura/insurance/stock). 미지정 시 인스턴스 브랜드.
            date_str: 'YYYY-MM-DD'. 미지정 시 오늘.
            use_ai: True 면 Gemini 실시간 집필 시도, 실패 시 폴백 로테이션.
        """
        if brand:
            self.brand = brand.lower()
            self.writer = GeminiDramaScenarioWriter(self.brand)

        if not date_str:
            date_str = date.today().isoformat()

        # [2026-10-23 통합 패치] 플래너로 오늘의 장르/로케이션/변주 결정
        _plan = self._get_plan(date_str)
        genre = self._pick_genre(date_str)
        location = self._pick_location(date_str)

        # 음성 배속 (기본 1.25, 범위 1.20~1.30)
        _voice_var = (_plan or {}).get("voice_variation") or {}
        _voice_speed: float = float(_voice_var.get("speed", 1.25))
        _voice_speed = max(1.20, min(1.30, _voice_speed))

        # 컷 예산 텍스트 (실측 CPS 기반)
        _budget_text: Optional[str] = None
        if self._budget is not None and self._cps_by_gender:
            try:
                _budget_text = self._budget.build_prompt_budget_text(
                    self._cps_by_gender, speed=_voice_speed
                )
            except Exception as _be:
                logger.error("[Director] 예산 텍스트 생성 실패 | %s", _be)

        # 연출 변주 힌트 (앵글/소품/시간대/의상)
        _plan_addendum: Optional[str] = None
        if _plan:
            _parts = []
            _ca = _plan.get("cut_angles")
            if _ca:
                _parts.append("컷 앵글: " + ", ".join(
                    "%s=%s" % (k, v) for k, v in _ca.items()
                ))
            if _plan.get("props"):
                _pv = _plan["props"]
                _ps = ", ".join(str(p) for p in _pv) if isinstance(_pv, (list, tuple)) else str(_pv)
                _parts.append("주요 소품: " + _ps)
            if _plan.get("time_of_day"):
                _parts.append("시간대: " + _plan["time_of_day"])
            if _plan.get("outfits"):
                _o = _plan["outfits"]
                _parts.append(
                    "의상: 여주인공=%s, 남주인공=%s" % (
                        _o.get("female", ""), _o.get("male", "")
                    )
                )
            if _parts:
                _plan_addendum = "\n".join(_parts)

        # ---------------- 1) Gemini 실시간 집필 시도 ----------------
        if use_ai:
            raw_cuts, reason = self.writer.generate(
                date_str, genre, location,
                budget_text=_budget_text,
                plan_addendum=_plan_addendum,
                cps_by_gender=self._cps_by_gender,
                voice_speed=_voice_speed,
            )
            if raw_cuts:
                cuts_data = self._normalize_cuts(raw_cuts)
                self.last_source = "gemini_ai"
                self.last_fallback_reason = None
                logger.info(
                    "[Director] Gemini 집필 성공 | brand=%s date=%s genre=%s speed=%.2f",
                    self.brand, date_str, genre.get("id"), _voice_speed,
                )
                payload = self._build_payload(
                    date_str, genre, location, cuts_data, "gemini_ai", None
                )
                payload["voice_variation"] = _voice_var
                payload["voice_speed"] = _voice_speed
                # 히스토리 저장
                if self._history is not None:
                    try:
                        from .drama_history_store import DramaHistoryStore as _HS
                        self._history.record({
                            "date": date_str,
                            "genre_id": genre.get("id", ""),
                            "location": location,
                            "template_id": None,
                            "script_hash": _HS.hash_text(
                                " ".join(c["speech"] for c in cuts_data)
                            ),
                            "hook_hash": _HS.hash_text(cuts_data[0]["speech"]),
                        })
                    except Exception as _he:
                        logger.error("[Director] 히스토리 저장 실패 | %s", _he)
                return payload

            fallback_reason = reason or "gemini_unknown_failure"
            logger.warning(
                "[Director] Gemini 실패 -> 폴백 로테이션 | brand=%s date=%s | reason=%s",
                self.brand, date_str, fallback_reason,
            )
        else:
            fallback_reason = "use_ai_disabled"
            logger.info(
                "[Director] use_ai=False -> 폴백 템플릿 사용 | brand=%s date=%s",
                self.brand, date_str,
            )

        # ---------------- 2) 폴백 템플릿 로테이션 (32종 신규 풀 우선) ----------------
        template = self._pick_fallback(date_str, genre_id=genre.get("id"))
        fb_genre = GENRE_BY_ID.get(template.get("genre_id", ""), genre)
        cuts_data = self._normalize_cuts(template.get("cuts", []))

        self.last_source = "fallback_template"
        self.last_fallback_reason = fallback_reason

        payload = self._build_payload(
            date_str, fb_genre, location, cuts_data, "fallback_template", fallback_reason
        )
        payload["template_id"] = template.get("id", "")
        payload["theme"] = template.get("theme", payload["theme"])
        payload["voice_variation"] = _voice_var
        payload["voice_speed"] = _voice_speed

        # 히스토리 저장 (폴백 경로)
        if self._history is not None:
            try:
                from .drama_history_store import DramaHistoryStore as _HS
                self._history.record({
                    "date": date_str,
                    "genre_id": fb_genre.get("id", ""),
                    "location": location,
                    "template_id": template.get("id"),
                    "script_hash": _HS.hash_text(
                        " ".join(c["speech"] for c in cuts_data)
                    ),
                    "hook_hash": _HS.hash_text(cuts_data[0]["speech"]),
                })
            except Exception as _he:
                logger.error("[Director] 히스토리 저장 실패(폴백) | %s", _he)

        return payload


# ==============================================================================
# 모듈 레벨 편의 함수 (기존 호출부 호환)
# ==============================================================================
def get_daily_drama_scenario(
    brand: str = "aura",
    date_str: Optional[str] = None,
    use_ai: bool = True,
) -> Dict[str, Any]:
    """모듈 레벨 단축 함수."""
    return DramaScenarioDirector(brand).get_daily_drama_scenario(
        brand=brand, date_str=date_str, use_ai=use_ai
    )


__all__ = [
    "DramaScenarioDirector",
    "GeminiDramaScenarioWriter",
    "get_daily_drama_scenario",
    "DRAMA_GENRE_SPECTRUMS",
    "LUXURY_DATING_LOCATIONS",
    "FALLBACK_TEMPLATES",
    "BRAND_SEARCH_KEYWORDS",
    "CUT_DURATIONS",
    "TOTAL_DURATION",
]
