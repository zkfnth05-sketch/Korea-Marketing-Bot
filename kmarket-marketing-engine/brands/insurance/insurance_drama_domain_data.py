# -*- coding: utf-8 -*-
"""보험 5씬 드라마 전용 도메인 데이터 모듈 (InsureBalance)."""
from __future__ import annotations
import re
from typing import Dict, List, Tuple

# ── [10대 핵심 보험 주제 SSOT] 대표님 승인 확정 (2026-10-26) ──────────
#   ★ 왜 16 → 10 으로 축소했는가:
#     기존 16주제는 '숨은 보험금 조회', '2030 포트폴리오', '과다보험료 절감' 처럼
#     보험 상품 축이 아닌 재무 일반론이 섞여 있어, 5씬 드라마의 팩폭 근거가
#     매번 추상적 표현('중복된 특약')으로 수렴했다. 이제 실제 보험 상품 10축으로
#     정렬하여, 각 주제마다 약관·의학 사실(INSURANCE_TOPIC_SPECS)을 1:1 결속한다.
#   · 순서는 로테이션 인덱스와 직결되므로 임의 변경 금지(상태 파일 호환).
INSURANCE_TOPICS: Tuple[str, ...] = (
    "실손의료비보험",
    "암보험",
    "뇌·심혈관보험",
    "종합건강보험",
    "수술비보험",
    "운전자보험",
    "치아보험",
    "간병·치매보험",
    "종신·정기보험",
    "유병자·간편보험",
)

# ── [Wan 2.2 S2V 81프레임(5.06초) 칼수렴: 씬별 엄격한 글자 수 SSOT] ────────
#   · 씬1: 18~24자 (3초, 최대 26자 엄수)
#   · 씬2: 24~30자 (4초, 최대 34자 엄수)
#   · 씬3: 24~30자 (4초, 최대 34자 엄수)
#   · 씬4: 28~34자 (5초, 최대 36자 엄수)
#   · 씬5: 26~34자 (4초, 최대 36자 엄수, '네이버에 보험 리밸런스' 포함)
SCENE_CHAR_LIMITS: Dict[int, Dict[str, int]] = {
    1: {"min": 18, "max": 26, "target": 22},
    2: {"min": 24, "max": 34, "target": 29},
    3: {"min": 24, "max": 34, "target": 29},
    4: {"min": 28, "max": 36, "target": 32},
    5: {"min": 26, "max": 36, "target": 32},
}

# ── [주제별 약관·의학 사실 SSOT] ─────────────────────────────────────
#   ★ 왜 별도 사전인가: 대사(매트릭스)와 사실 근거(스펙)를 분리해야
#     ① 금소법 심의 시 '사실 서술'만 따로 검수할 수 있고,
#     ② 대사 표현을 바꿔도 사실 근거가 드리프트하지 않는다.
#   · 각 항목은 다음 4키를 반드시 갖는다(검증기에서 강제):
#       "fact"    — 핵심 약관/의학 사실 (팩폭 근거)
#       "trap"    — 소비자가 놓치는 맹점 (한숨 근거)
#       "check"   — 리밸런스 점검 포인트 (해결 근거)
#       "keyword" — 씬3 화면/대사에 노출할 비교 키워드
#   · ★ 금액·배수·절감액 수치 표현은 전면 금지(금소법). 비율(%)은 약관 구조
#     설명에 한해 사실 서술로만 사용한다(예: 유사암 지급률 축소).
INSURANCE_TOPIC_SPECS: Dict[str, Dict[str, str]] = {
    "실손의료비보험": {
        "fact": (
            "4세대 실손은 직전 1년간 병원 이용량(도수치료·비급여 주사 등)에 따라 "
            "보험료 할인·할증이 적용되는 재가입 주기 구조"
        ),
        "trap": "병원을 거의 가지 않는데도 갱신 때마다 부담이 늘어나는 체감",
        "check": "최근 1년 비급여 이용 내역과 4세대 전환 손익 비교",
        "keyword": "4세대 실손 할인할증",
    },
    "암보험": {
        "fact": (
            "갑상선암·제자리암·경계성종양 등 유사암은 일반암 대비 지급률이 "
            "10~20% 수준으로 축소된 약관 구조"
        ),
        "trap": "암보험을 여러 개 들어도 유사암 진단비는 한도가 얇게 설계된 맹점",
        "check": "일반암과 유사암 지급률·한도를 나눠서 비교",
        "keyword": "유사암 지급률",
    },
    "뇌·심혈관보험": {
        "fact": (
            "전체 뇌질환 중 뇌출혈 비중은 약 9%인 반면 뇌경색은 약 70%를 차지하며, "
            "뇌출혈만 보장하는 특약은 뇌경색 진단 시 지급되지 않음"
        ),
        "trap": "'뇌혈관'이라는 이름만 보고 가입했는데 정작 뇌경색이 빠진 구조",
        "check": "뇌출혈·뇌경색·심근경색을 각각 별도 보장으로 담았는지 확인",
        "keyword": "뇌경색 보장 범위",
    },
    "종합건강보험": {
        "fact": (
            "암·뇌·심혈관 3대 질환을 비갱신형으로 통합 설계하고, "
            "입원일당 같은 자잘한 특약을 정리하는 구조"
        ),
        "trap": "특약이 많아 보이지만 정작 3대 질환 보장은 얇게 설계된 경우",
        "check": "3대 질환 보장과 자잘한 특약을 분리해 우선순위 정리",
        "keyword": "3대 질환 비갱신",
    },
    "수술비보험": {
        "fact": (
            "질병수술비는 1회성 한도로 끝나는 경우가 많고, "
            "1~5종 수술비·다빈치 로봇수술 특약은 회차별 반복 지급 구조"
        ),
        "trap": "수술을 여러 번 받아도 1회성 특약은 첫 수술 이후 지급이 멈추는 맹점",
        "check": "1회성인지 반복 지급인지, 로봇수술이 포함되는지 확인",
        "keyword": "1~5종 수술비 반복지급",
    },
    "운전자보험": {
        "fact": (
            "자동차보험은 대인·대물 민사 배상 중심이고, "
            "운전자보험은 형사합의금·변호사선임비·벌금을 담당하는 별개 구조"
        ),
        "trap": "자동차보험만 있으면 형사 영역까지 다 해결된다는 착각",
        "check": "변호사선임비·형사합의금·스쿨존 관련 특약 포함 여부 확인",
        "keyword": "변호사선임비 특약",
    },
    "치아보험": {
        "fact": (
            "치아보험은 통상 면책기간 90일, 가입 후 1~2년은 지급률이 "
            "50%로 감액되는 기간이 설정된 구조"
        ),
        "trap": "임플란트를 급히 해야 하는 시점에 가입하면 감액기간에 걸리는 맹점",
        "check": "면책기간·감액기간·연간 임플란트 개수 제한 여부 확인",
        "keyword": "면책 90일 감액기간",
    },
    "간병·치매보험": {
        "fact": (
            "치매 진단뿐 아니라 장기요양등급(1~5등급) 판정 시에도 보장이 작동하며, "
            "간병인 지원형과 현금 지급형으로 지급 방식이 갈림"
        ),
        "trap": "치매만 보장된다고 생각했는데 등급 판정 기준을 못 채우는 경우",
        "check": "장기요양등급 판정 기준과 간병인 지원·현금 지급 방식 비교",
        "keyword": "장기요양등급 보장",
    },
    "종신·정기보험": {
        "fact": (
            "종신보험은 평생 보장 대신 부담이 크고, "
            "정기보험은 자녀 독립기처럼 필요한 기간만 순수보장으로 집중하는 구조"
        ),
        "trap": "보장 기간과 부담을 분리하지 않고 무조건 종신으로만 설계하는 습관",
        "check": "보장이 필요한 기간과 순수보장형 정기보험 비중 점검",
        "keyword": "순수보장형 정기보험",
    },
    "유병자·간편보험": {
        "fact": (
            "고혈압·당뇨로 약을 복용 중이어도 3·5·5 간편고지(3개월 투약, "
            "5년 입원·수술, 5대 질환) 기준으로 가입 가능한 구조"
        ),
        "trap": "병력 때문에 가입이 아예 불가능하다고 단정하고 포기하는 경우",
        "check": "간편고지 3·5·5 기준 충족 여부와 고정지출 구조 점검",
        "keyword": "3·5·5 간편고지",
    },
}

INSURANCE_GENRES: Tuple[str, ...] = (
    "보험료 다이어트 현실극",
    "중복 특약 팩폭 사이다",
    "가족 보장 현실 공감",
    "가계 재정 역전극",
    "보험금 청구 사이다",
    "사회초년생 재무 팩폭",
    "신혼부부 보장 설계",
    "노후 의료비 반전",
)

INSURANCE_LOCATIONS_KO: Tuple[str, ...] = (
    "재무 상담실 원목 테이블",
    "거실 소파 보험증권 테이블",
    "병원 원무과 앞 로비",
    "카페 창가 재무 컨설팅석",
    "홈오피스 서재 노트북 데스크",
    "은행 PB센터 프라이빗 룸",
    "출근길 지하철 스마트폰 화면",
    "신혼집 식탁 가계부 회의",
    "동네 병원 진료실 대기석",
    "세무회계 사무소 상담실",
    "약국 앞 처방전 검토석",
    "직장인 점심 휴게실 소파",
    "주말 브런치 카페 재정 대화",
    "부모님 댁 거실 약봉투 테이블",
    "공원 벤치 통장 잔고 확인",
    "온라인 화상 재무 미팅 데스크",
)

INSURANCE_LOCATIONS_EN: Tuple[str, ...] = (
    "cozy financial advisory office wooden consultation table",
    "modern living room sofa with insurance policy documents on table",
    "busy hospital administration reception lobby waiting area",
    "quiet cafe window table with financial consulting paperwork",
    "bright home office desk with laptop and insurance comparison charts",
    "luxurious bank private consultation lounge leather chairs",
    "commuter subway car checking mobile insurance diagnosis app",
    "newlywed dining table reviewing family monthly budget",
    "local clinic waiting room checking medical treatment coverage",
    "professional accounting and tax advisory office desk",
    "pharmacy front counter checking prescription expense receipts",
    "office relaxation lounge reviewing monthly insurance deductions",
    "weekend brunch cafe discussing family insurance restructuring",
    "elderly parents living room reviewing senior care policy documents",
    "autumn park bench checking reduced insurance monthly fee savings",
    "modern remote video conference desk with digital financial dashboard",
)

if len(INSURANCE_LOCATIONS_KO) != len(INSURANCE_LOCATIONS_EN):
    raise ValueError("보험 장소 풀 길이 불일치 (KO != EN)")

# ── [단일 출처: 캐릭터 레지스트리] ────────────────────────────────────
# 프롬프트·매트릭스·씬가이드가 모두 이 레지스트리에서 파생된다.
# 나이/역할/관계/의상/헤어/얼굴톤은 여기서만 정의한다.
CHARACTER_REGISTRY: Dict[str, Dict[str, str]] = {
    "SUJIN": {
        "name_ko": "수진",
        "age": "35",
        "role": "아내",
        "relationship": "민우의 아내, 맞벌이 직장인",
        "hair": "neat shoulder-length dark hair with soft side part",
        "wardrobe": "professional casual navy blazer with simple ivory blouse",
        "face_tone": "radiant youthful luminous skin, bright clear complexion, warm sincere expression",
        "gender": "woman",
    },
    "MINWOO": {
        "name_ko": "민우",
        "age": "37",
        "role": "남편",
        "relationship": "수진의 남편, 보험에 조예가 깊은 직장인",
        "hair": "stylish modern neat haircut",
        "wardrobe": "relaxed dark charcoal knit sweater over crisp white shirt",
        "face_tone": "warm confident expression, healthy skin tone",
        "gender": "man",
    },
}

# ── [공통 촬영 규격: 두 캐릭터·전 씬이 공유] ─────────────────────────
# 조명/배경/렌즈/색보정/금지 토큰을 한 곳에서 관리해 톤 점프를 방지한다.
SHOOTING_SPEC: Dict[str, str] = {
    "lighting": "bright crisp natural daylight, high-key luminous exposure, pristine crystal-clear studio lighting",
    "background": "plain soft neutral background",
    "lens": "85mm portrait lens, shallow depth of field",
    "skin": "ultra realistic skin texture, radiant healthy skin tone",
    "aspect": "vertical 9:16",
    "negative": (
        "absolutely NO candlelight, NO dark moody shadows, NO dim amber lighting, "
        "no text, no watermark, no logo, no cartoon, no illustration"
    ),
}

# ── [부부 공간 및 시선 일치 안전장치 SSOT] 대표님 지시 (2026-10-26) ──────────
#   ★ 핵심 원칙: 서 있는 것과 앉아 있는 것이 회차별로 교차되도록 하되,
#     한 씬 내 또는 회차 내에서 두 사람이 따로 놀지 않도록(한 명만 서 있거나 앉는 왜곡 방지)
#     두 사람의 자세(둘 다 앉기 또는 둘 다 서기)와 수평 아이레벨(same eye level)을 100% 결속한다.
#   · Mode A (홀수 회차): [부부 동시 좌식 모드 (SEATED)] - 식탁 마주 앉기, 수평 시선 교환.
#   · Mode B (짝수 회차): [부부 동시 입식 모드 (STANDING)] - 거실 창가/아일랜드 나란히 서기, 수평 시선 교환.
SPATIAL_POSTURE_MODES: Dict[str, Dict[str, str]] = {
    "SEATED": {
        "mode_id": "SEATED",
        "name_ko": "부부 동시 좌식 모드 (Mode A)",
        "desc": "거실 원목 식탁에 부부가 나란히/마주 앉아 보험 증권을 보며 대화",
        "couple_shot": (
            "two-shot composition, husband and wife seated facing each other across a modern wooden dining table, "
            "relaxed sitting posture, upper-body shot, natural eye-line exchange at same seated eye level, "
            "matching warm indoor lighting and color grade, consistent wardrobe and hairstyle with their character sheets"
        ),
        "sujin_posture": "seated at modern wooden dining table, natural sitting posture, upper body, eye level matching seated partner",
        "minwoo_posture": "seated at modern wooden dining table, natural sitting posture, upper body, eye level matching seated partner",
        "eye_line_anchor": "eye_level_seated_horizontal",
    },
    "STANDING": {
        "mode_id": "STANDING",
        "name_ko": "부부 동시 입식 모드 (Mode B)",
        "desc": "거실 창가/아일랜드 식탁 앞에 부부가 나란히 서서 스마트폰/서류를 보며 대화",
        "couple_shot": (
            "two-shot composition, husband and wife standing side by side near modern living room window, "
            "upright natural posture, upper-body shot, natural eye-line exchange at same standing eye level, "
            "matching warm indoor lighting and color grade, consistent wardrobe and hairstyle with their character sheets"
        ),
        "sujin_posture": "standing near modern living room window, natural standing posture, upper body, eye level matching standing partner",
        "minwoo_posture": "standing near modern living room window, natural standing posture, upright upper body, eye level matching standing partner",
        "eye_line_anchor": "eye_level_standing_horizontal",
    },
}


def get_spatial_anchor(run_no: int) -> Dict[str, str]:
    """회차 번호(run_no)에 따라 부부 공간 앵커(좌식 ↔ 입식)를 결정론적으로 교차 반환한다.

    · 홀수 회차(1, 3, 5, ...) -> Mode A (SEATED, 부부 동시 좌식)
    · 짝수 회차(2, 4, 6, ...) -> Mode B (STANDING, 부부 동시 입식)
    · 단일 회차(1~5씬) 내에서는 100% 동일한 공간 앵커를 결속하여 시선/포즈 왜곡을 방지한다.
    """
    mode_key = "SEATED" if (run_no % 2 == 1) else "STANDING"
    return SPATIAL_POSTURE_MODES[mode_key]


# 하위 호환을 위한 레거시 COUPLE_SHOT_SPEC (SEATED 기준)
COUPLE_SHOT_SPEC: str = SPATIAL_POSTURE_MODES["SEATED"]["couple_shot"]

# 씬별 감정 태그 — 매트릭스/씬가이드/검증이 공유하는 계약.
SCENE_EMOTION_TAGS: Tuple[str, ...] = (
    "sigh",       # 씬1: 한숨
    "fact_punch", # 씬2: 팩폭
    "awe",        # 씬3: 감탄
    "relief",     # 씬4: 안도/사이다
    "cta",        # 씬5: 검색유도 클로징
)


def _render_character_prompt(char_key: str) -> str:
    """캐릭터 레지스트리 + 공통 촬영 규격으로부터 프롬프트를 렌더링한다."""
    c = CHARACTER_REGISTRY[char_key]
    s = SHOOTING_SPEC
    return (
        f"Photorealistic studio portrait of a {c['gender']} Korean {c['role']} "
        f"named {c['name_ko']}, age {c['age']}, {c['relationship']}, "
        f"{c['hair']}, {c['face_tone']}, {c['wardrobe']}, "
        f"{s['lighting']}, {s['skin']}, {s['background']}, "
        f"{s['aspect']} portrait, upper body, looking at camera, "
        f"{s['lens']}, {s['negative']}"
    )


INSURANCE_FRESH_FEMALE_PROMPT: str = _render_character_prompt("SUJIN")
INSURANCE_FRESH_MALE_PROMPT: str = _render_character_prompt("MINWOO")

# ── [10개 주제별 5씬 서사 팩토리 & 매트릭스] ──────────────────────────
# 씬1 = 수진(여) 고민/한숨 (3초)
# 씬2 = 민우(남) 전문가 팩폭 (4초)
# 씬3 = 수진(여) 34개사 AI 리밸런스 체감 (4초)
# 씬4 = 민우(남) 리밸런스 후 안도 (5초)
# 씬5 = 수진(여) 네이버 공식 검색어 "보험 리밸런스" 엔딩 (4초)
#
#   ★ 화자 배치 계약(파이프라인 SCENE_PLAN 과 1:1 일치):
#     씬1 여 / 씬2 남 / 씬3 여 / 씬4 남 / 씬5 여
#     → 씬4 는 반드시 민우(남편) 대사여야 하며, 검증기가 이를 강제한다.

def _build_narrative_matrix() -> Dict[str, Tuple[Tuple[str, str], ...]]:
    matrix: Dict[str, Tuple[Tuple[str, str], ...]] = {}

    # ★ 금융광고 심의(금소법) 준수: 구체적 금액·절감액·배수·반값 표현 전면 금지.
    #   → '고정지출', '중복된 특약', '새는 보험료', '핵심 보장 위주 리밸런스' 등
    #     사실 서술형·중립 표현만 사용한다.
    #   · 비율(%)은 약관 구조 설명에 한해 사실 서술로만 허용(예: 유사암 지급률 축소).
    #   · 공포 마케팅·질책성 표현('눈탱이', '호구', '사기') 금지.
    # ★ 81프레임(5.06초) 칼수렴: 씬별 엄격한 글자 수 상한 엄수
    #   · 씬1: 18~26자 (3초)   · 씬2: 24~34자 (4초)
    #   · 씬3: 24~34자 (4초)   · 씬4: 28~36자 (5초)
    #   · 씬5: 26~36자 (4초, '네이버에 보험 리밸런스' 포함)
    topic_dialogues: Dict[str, Tuple[str, str, str, str, str]] = {
        "실손의료비보험": (
            "병원 안 가는데 고정지출만 늘어… 4세대 맞나?",
            "약관 안 보고 유지하면 손해야. 비급여 이용량부터 따져봐!",
            "보험 리밸런스로 보니까 4세대 할인할증이 한눈에 보이네!",
            "비급여 정리하고 핵심만 담으니까 가계가 훨씬 가벼워졌어!",
            "새는 보험료 두지 말고, 네이버에 보험 리밸런스 검색해보세요!",
        ),
        "암보험": (
            "암보험 여러 개인데… 유사암 보장 빈 거 아냐?",
            "유사암은 일반암보다 지급률이 확 줄어. 한도부터 확인해!",
            "보험 리밸런스로 보니까 얇아진 유사암 지급률이 딱 나오네!",
            "일반암과 유사암 한도를 나눠서 맞추니까 보장이 훨씬 명확해!",
            "중복가입 두지 말고, 네이버에 보험 리밸런스 한번 검색해보세요!",
        ),
        "뇌·심혈관보험": (
            "뇌혈관 들었는데… 뇌경색은 빠진 거 아냐?",
            "뇌질환 대부분은 뇌경색이야. 뇌출혈만 담으면 지급 안 돼!",
            "보험 리밸런스로 비교하니까 뇌경색 보장 여부가 딱 보여!",
            "뇌경색과 심근경색까지 별도로 담고 나니까 속이 다 후련해!",
            "이름만 보지 말고, 네이버에 보험 리밸런스 한번 검색해보세요!",
        ),
        "종합건강보험": (
            "특약은 많은데… 3대 질환 보장은 얇아 불안해.",
            "자잘한 입원비만 늘었어. 암·뇌·심혈관 비갱신부터 채워!",
            "보험 리밸런스로 보니까 3대 질환 비갱신 보장이 딱 나와!",
            "불필요한 특약 빼고 3대 질환 위주로 맞추니까 보장이 탄탄해!",
            "특약에 속지 말고, 네이버에 보험 리밸런스 한번 검색해보세요!",
        ),
        "수술비보험": (
            "수술비 특약… 두 번째 수술부터 안 나온대?",
            "질병수술비는 1회성이 많아. 1~5종 수술비가 반복 지급이야!",
            "보험 리밸런스로 보니까 반복지급 여부가 한눈에 보이네!",
            "1회성과 반복 지급을 나눠서 맞추니까 수술비 보장이 든든해!",
            "헷갈리면 지금, 네이버에 보험 리밸런스 한번 검색해보세요!",
        ),
        "운전자보험": (
            "자동차보험만 있으면 되지… 운전자보험 왜 들어?",
            "민사는 자동차보험, 형사합의금은 운전자보험이야. 분리해!",
            "보험 리밸런스로 보니까 변호사선임비 특약이 빠져 있네!",
            "형사합의금과 벌금까지 채워 넣고 나니까 운전할 때 안심돼!",
            "따로 챙겨야 해, 네이버에 보험 리밸런스 한번 검색해보세요!",
        ),
        "치아보험": (
            "임플란트 해야 하는데… 지금 들면 보장될까?",
            "치아보험은 면책 90일에 감액기간 있어. 급하면 손해야!",
            "보험 리밸런스로 보니까 면책기간과 감액기간이 딱 나와!",
            "감액기간과 임플란트 개수 확인하고 맞추니까 속이 시원해!",
            "급히 들지 말고, 네이버에 보험 리밸런스 한번 검색해보세요!",
        ),
        "간병·치매보험": (
            "부모님 간병비 생각하면… 지금 보장으론 안 돼.",
            "치매만 보면 안 돼. 장기요양등급과 간병인 지원형을 따져!",
            "보험 리밸런스로 보니까 장기요양등급 기준이 한눈에 보여!",
            "지원 방식과 현금 지급형 비교해서 맞추니까 훨씬 안심돼!",
            "미루지 마시고, 네이버에 보험 리밸런스 한번 검색해보세요!",
        ),
        "종신·정기보험": (
            "종신 하나면 끝인 줄 알았는데… 부담만 커.",
            "평생 묶지 마. 자녀 독립기만 순수보장 정기보험으로 집중해!",
            "보험 리밸런스로 보니까 필요한 보장 기간이 딱 정리되네!",
            "필요한 기간만 순수보장으로 맞추니까 가계가 훨씬 가벼워!",
            "부담 줄이려면, 네이버에 보험 리밸런스 한번 검색해보세요!",
        ),
        "유병자·간편보험": (
            "혈압약 먹는데… 가입 자체가 안 되는 거 아냐?",
            "3·5·5 간편고지만 거치면 약 먹어도 가입돼. 포기하지 마!",
            "보험 리밸런스로 보니까 3·5·5 간편 조건이 바로 나오네!",
            "약 먹어도 핵심 보장 깔끔하게 맞추고 나니까 마음이 편해!",
            "겁먹지 마시고, 네이버에 보험 리밸런스 한번 검색해보세요!",
        ),
    }

    # ★ 주제 문자열 자체에 금액이 박혀 있을 수 있으므로(예: '30만원'),
    #   대사에 삽입하기 전에 반드시 금액 토큰을 중립 표현으로 세정한다.
    _MONEY_TOKEN_RE = re.compile(
        r"\d+\s*(?:만원|천만원|억원|억|원)|반값|\d+\s*배"
    )

    def _sanitize_topic(topic: str) -> str:
        """주제 문자열에서 금액·배수 토큰을 제거하고 중립 표현으로 치환한다."""
        cleaned = _MONEY_TOKEN_RE.sub("", topic)
        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
        return cleaned or "보험료 구조"

    for t in INSURANCE_TOPICS:
        if t in topic_dialogues:
            d = topic_dialogues[t]
        else:
            # [미등록 주제 방어] 새 주제가 추가되고 대사가 없을 때도
            #   금액 토큰 없는 중립 대사로 5씬 계약을 유지한다(자리표시자 금지).
            safe_t = _sanitize_topic(t)
            d = (
                f"고정지출 늘어나는데… {safe_t} 제대로 보장되나?",
                f"약관 안 보고 사인했지? {safe_t} 중복 특약부터 봐!",
                f"보험 리밸런스로 보니까 불필요한 특약이 한눈에 보이네!",
                f"중복 특약 정리하고 핵심만 담으니까 가계가 훨씬 가벼워!",
                f"{safe_t} 불안해 말고, 네이버에 보험 리밸런스 검색해보세요!",
            )
        matrix[t] = (
            (d[0], "cinematic close up, woman sighing at desk reviewing insurance policy, cold tone, 35mm film grain"),
            (d[1], "close up of Minwoo sitting opposite, professional and direct expression, modern office bokeh, 50mm lens"),
            (d[2], "close up of Korean woman Sujin holding mobile phone screen showing 34 insurance comparison chart glowing, warm bokeh, 50mm lens"),
            (d[3], "close up of Minwoo smiling relieved while reviewing restructured insurance policy documents, warm natural daylight, shallow depth of field"),
            (d[4], "wide shot of modern financial district street at dusk, confident woman walking, cold blue tone"),
        )
    return matrix

INSURANCE_NARRATIVE_MATRIX: Dict[str, Tuple[Tuple[str, str], ...]] = _build_narrative_matrix()

INSURANCE_SCENE_GUIDE_PROMPT = """
너는 한국 보험 비교·리모델링 서비스 '보험 리밸런스'의 숏폼 드라마 작가다.
주제='{topic}', 장르='{genre}', 회차={run_no}.
[주제 사실 근거] {topic_fact}
[소비자 맹점] {topic_trap}
[점검 포인트] {topic_check}
5씬 시나리오를 JSON으로만 출력하라. 설명/마크다운 금지.
★ 절대 금지: 오페라, 인생 명언, 3인칭 나레이션, 문어체, 소개팅/데이팅 대사.
실제 부부(수진 35세 아내 / 민우 37세 남편)의 극사실주의 구어체 티키타카로 작성하라.
★ 씬2(민우) 대사에는 위 [주제 사실 근거]를 구체적으로 인용하여 팩폭의 근거를 대라.
★ 씬1(수진) 대사에는 위 [소비자 맹점]을 체감형 일상어로 풀어내라.

★★ [금융광고 심의 절대 준수 — 금소법] ★★
  - 구체적인 금액 언급 절대 금지: 숫자+원, 만원, 억, 천만원, 반값, 몇만원, 2배, 3배 등
    모든 수치·비율·절감액 표현을 쓰지 마라.
  - 대신 다음의 중립·사실 서술 표현만 사용하라:
    '매달 나가는 고정지출', '중복된 특약', '새는 보험료', '핵심 보장 위주로 리밸런스'.
  - 과장·단정 표현 금지: '무조건', '100% 보장', '최고', '완벽', '확실히 아껴준다' 등 금지.
  - 약관은 객관적 사실로만 비교 서술하고, 특정 상품의 우열을 단정하지 마라.
  - 기존 계약의 부당 해지·해지를 조장하는 표현 금지. 리밸런스는 '점검·비교·정리'의 관점으로만 서술하라.
  - 공포 마케팅·질책성 표현('눈탱이', '호구', '사기') 금지.

씬 구성 (1씬 = 1캐릭터 단독 대사, 화자 교차 엄수):
  씬1 = 수진(여) 단독 — 매달 나가는 고정지출/새는 보험료에 대한 현실 한숨 ({d1}초)
  씬2 = 민우(남) 단독 — 중복된 특약을 짚는 객관적 팩폭 진단 ({d2}초)
  씬3 = 수진(여) 단독 — 34개사 AI 비교로 새는 보험료를 확인하는 체감 ({d3}초)
  씬4 = 민우(남) 단독 — 핵심 보장 위주로 리밸런스한 뒤의 안도 ({d4}초)
  씬5 = 수진(여) 단독 — 검색유도 클로징 ({d5}초)
씬5 narration에는 반드시 '보험 리밸런스'와 '네이버에 보험 리밸런스 한번 검색해보세요!'를 포함하라.
"""


def validate_insurance_domain_data() -> bool:
    # ── 기본 개수 계약 ──
    #   ★ 대표님 승인 확정 (2026-10-26): 10대 핵심 보험 주제로 축소.
    assert len(INSURANCE_TOPICS) == 10, "주제 10개 필수"
    assert len(INSURANCE_GENRES) == 8, "장르 8개 필수"
    assert len(INSURANCE_LOCATIONS_KO) == 16, "장소 KO 16개 필수"
    assert len(INSURANCE_LOCATIONS_EN) == 16, "장소 EN 16개 필수"
    assert len(INSURANCE_NARRATIVE_MATRIX) == 10, "매트릭스 10개 필수"
    assert len(INSURANCE_TOPIC_SPECS) == 10, "주제 스펙 10개 필수"

    # ── 주제 ↔ 스펙 ↔ 매트릭스 3자 1:1 결속 계약 ──
    #   ★ 왜 필수인가: 주제만 추가하고 스펙/대사를 빠뜨리면 씬2 팩폭 근거가
    #     비어 추상적 대사로 수렴한다. 세 사전의 키 집합이 완전히 일치해야 한다.
    assert set(INSURANCE_TOPIC_SPECS.keys()) == set(INSURANCE_TOPICS), (
        f"주제 스펙 키 불일치: {sorted(set(INSURANCE_TOPIC_SPECS) ^ set(INSURANCE_TOPICS))}"
    )
    assert set(INSURANCE_NARRATIVE_MATRIX.keys()) == set(INSURANCE_TOPICS), (
        f"매트릭스 키 불일치: {sorted(set(INSURANCE_NARRATIVE_MATRIX) ^ set(INSURANCE_TOPICS))}"
    )

    # ── 주제 스펙 4키 완전성 + 금액 토큰 부재 계약 ──
    _MONEY_RE = re.compile(r"\d+\s*(?:만원|천만원|억원|억|원)|반값|\d+\s*배")
    for t, spec in INSURANCE_TOPIC_SPECS.items():
        for key in ("fact", "trap", "check", "keyword"):
            assert key in spec, f"주제 스펙 '{t}' 에 '{key}' 누락"
            assert spec[key].strip(), f"주제 스펙 '{t}.{key}' 비어 있음"
        # 금소법: 스펙 문구에도 금액·배수 표현 금지(비율 % 는 허용).
        assert not _MONEY_RE.search(spec["fact"]), f"주제 스펙 '{t}.fact' 에 금액 토큰"
        assert not _MONEY_RE.search(spec["trap"]), f"주제 스펙 '{t}.trap' 에 금액 토큰"
        assert not _MONEY_RE.search(spec["check"]), f"주제 스펙 '{t}.check' 에 금액 토큰"

    # ── 캐릭터 레지스트리 계약 ──
    assert set(CHARACTER_REGISTRY.keys()) == {"SUJIN", "MINWOO"}, "캐릭터는 수진/민우 2인 필수"
    assert CHARACTER_REGISTRY["SUJIN"]["age"] == "35", "수진 나이 35세 고정"
    assert CHARACTER_REGISTRY["MINWOO"]["age"] == "37", "민우 나이 37세 고정"
    assert CHARACTER_REGISTRY["SUJIN"]["role"] == "아내", "수진 역할=아내"
    assert CHARACTER_REGISTRY["MINWOO"]["role"] == "남편", "민우 역할=남편"

    # ── 프롬프트가 레지스트리·규격에서 파생되었는지(단일 출처) 검사 ──
    for key, prompt in (
        ("SUJIN", INSURANCE_FRESH_FEMALE_PROMPT),
        ("MINWOO", INSURANCE_FRESH_MALE_PROMPT),
    ):
        c = CHARACTER_REGISTRY[key]
        assert f"age {c['age']}" in prompt, f"{key} 프롬프트에 나이 미반영"
        assert c["role"] in prompt, f"{key} 프롬프트에 역할 미반영"
        assert c["name_ko"] in prompt, f"{key} 프롬프트에 이름 미반영"
        # 공통 촬영 규격 토큰 포함 여부
        for spec_key in ("lighting", "background", "lens", "skin", "aspect", "negative"):
            assert SHOOTING_SPEC[spec_key] in prompt, f"{key} 프롬프트에 규격 '{spec_key}' 누락"
        # 금지 페르소나 회귀 방지
        assert "consultant" not in prompt.lower(), f"{key} 프롬프트에 'consultant' 페르소나 잔존"
        assert "early 30s" not in prompt.lower(), f"{key} 프롬프트에 'early 30s' 잔존"

    # ── 부부 투샷 규격 존재 ──
    assert "two-shot" in COUPLE_SHOT_SPEC, "부부 투샷 규격 필수"
    assert "eye-line" in COUPLE_SHOT_SPEC, "시선 교환 규격 필수"

    # ── 감정 태그 커버리지(5씬 전부) ──
    assert len(SCENE_EMOTION_TAGS) == 5, "감정 태그 5개(씬별) 필수"

    # ── 매트릭스 씬 계약 ──
    for t, scenes in INSURANCE_NARRATIVE_MATRIX.items():
        assert len(scenes) == 5, f"주제 {t} 씬 개수 5개 필수"
        assert "보험 리밸런스" in scenes[4][0], f"씬5 키워드 누락 ({t})"
        # 씬2·씬4는 민우(남편) 지시문이어야 함 — SCENE_PLAN(여/남/여/남/여) 일치 계약
        assert "민우" in scenes[1][1] or "Minwoo" in scenes[1][1], f"씬2 민우 지시문 누락 ({t})"
        assert "민우" in scenes[3][1] or "Minwoo" in scenes[3][1], f"씬4 민우 지시문 누락 ({t})"
        # 씬1·씬3·씬5는 수진(여) 지시문이어야 함 — 화자 교차 엄수
        for idx in (0, 2, 4):
            assert "woman" in scenes[idx][1].lower(), f"씬{idx + 1} 수진(여) 지시문 누락 ({t})"
        # 금소법: 대사 전건에 금액·배수 토큰 부재(비율 % 는 허용).
        # 81프레임(5.06초) 칼수렴: 씬별 글자 수 상한 엄수 계약.
        for idx, (narr, _prm) in enumerate(scenes, start=1):
            assert not _MONEY_RE.search(narr), f"씬{idx} 대사에 금액 토큰 ({t}): {narr}"
            max_limit = SCENE_CHAR_LIMITS[idx]["max"]
            assert len(narr) <= max_limit, (
                f"주제 '{t}' 씬{idx} 글자 수 초과: {len(narr)}자 (상한 {max_limit}자) | '{narr}'"
            )
    return True


# ── [무인 가동 안전장치: fail-fast 정책] ─────────────────────────────
# 검증 실패 시 조용히 통과시키지 않고 즉시 예외로 중단한다.
# (외부 생성 호출부는 이 모듈을 import하는 측에서 타임아웃·재시도 상한·
#  서킷브레이커·좀비 프로세스 회수를 반드시 적용해야 한다.)
if not validate_insurance_domain_data():
    raise RuntimeError("보험 도메인 데이터 무결성 검증 실패")