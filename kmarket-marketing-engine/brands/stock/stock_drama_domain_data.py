# -*- coding: utf-8 -*-
"""2030 주식 투자 현실극 5씬 드라마 전용 도메인 데이터 모듈 (StockMaster AI).

[구조 개편 요약]
- EXPECTED_TOPIC_COUNT: 카디널리티 SSOT (데이터/스펙/검증 3곳 공통 참조)
- 16개 주제 × 5씬 = 80개 대사 전량 수작업 큐레이션 (폴백 경로 완전 제거)
- STOCK_TOPICS는 _CURATED_DIALOGUES.keys()에서 파생 → 이중 표현 제거
- 프롬프트: 단일 블롭 → SSOT 조립 (페르소나/비트/금지어 분리 감사 가능)
- import 시점 자동 validate() 제거 → 명시적 호출(__main__/파이프라인 게이트)
- 키 집합 3자 동등성(TOPICS/DIALOGUES/SPECS) 사전 검증으로 침묵 실패 차단
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# ── [SSOT] 카디널리티 계약 ────────────────────────────────────────────
EXPECTED_TOPIC_COUNT: int = 16
EXPECTED_GENRE_COUNT: int = 8
EXPECTED_LOCATION_COUNT: int = 16
SCENES_PER_TOPIC: int = 5

# ── [SSOT] 씬별 글자수 계약 (씬 인덱스 1-based → (min, max)) ──────────
SCENE_CHAR_LIMITS: Dict[int, Tuple[int, int]] = {
    1: (18, 32),
    2: (24, 34),
    3: (24, 35),
    4: (28, 38),
    5: (24, 36),
}

# ── [SSOT] 씬별 화자/역할 시퀀스 (씬1~5) ─────────────────────────────
SCENE_SPEAKER_SEQUENCE: Tuple[Tuple[str, str], ...] = (
    ("지은", "여"),
    ("준혁", "남"),
    ("지은", "여"),
    ("지은", "여"),
    ("지은", "여"),
)

# ── [SSOT] 씬5 필수 문구 (단일 문구 — 부분 문자열 중복 제거) ─────────
SCENE5_REQUIRED_PHRASES: Tuple[str, ...] = (
    "네이버에 스톡마스터 AI 한번 검색해보세요!",
)

# ── [SSOT] 금지어 (문어체/3인칭/데이팅/AI매칭 잔재) ──────────────────
FORBIDDEN_PHRASES: Tuple[str, ...] = (
    "그는", "그녀는", "인생이란", "명언", "오페라", "나레이션",
    "소개팅", "데이팅", "매칭", "이상형", "썸",
)

# ── [SSOT] 씬별 비트 (2030 주식 투자 현실극 톤) ──────────────────────
SCENE_BEATS: Dict[int, str] = {
    1: "지은(여) 한숨 훅 — 손실/변동성/정보 과부하 등 투자 현실 한숨",
    2: "준혁(남) 팩폭 티키타카 — 선배 투자자의 원칙/리스크 관리 팩폭",
    3: "지은(여) 솔루션 체감 — 스톡마스터 AI로 판단 근거 확보 감탄",
    4: "지은(여) 성과 확인 — 원칙 준수/리스크 통제 성과 사이다",
    5: "지은(여) 검색유도 엔딩 — 사이다 클로징",
}


@dataclass(frozen=True)
class SceneSpec:
    index: int
    speaker: str
    gender: str
    dialogue: str
    char_min: int
    char_max: int
    visual: str

    def char_len(self) -> int:
        return len(self.dialogue)

    def is_within_limits(self) -> bool:
        return self.char_min <= self.char_len() <= self.char_max


@dataclass(frozen=True)
class TopicSpec:
    topic: str
    scenes: Tuple[SceneSpec, ...] = field(default_factory=tuple)


# ── [16개] 2030 주식 투자 현실극 주제 (SSOT: _CURATED_DIALOGUES에서 파생) ──
# 주제 추가/삭제는 _CURATED_DIALOGUES만 수정하면 자동 반영됨.

STOCK_GENRES: Tuple[str, ...] = (
    "주식 입문 성장극",
    "손실 극복 사이다",
    "리스크 관리 팩폭극",
    "배당 장기 투자극",
    "분산 투자 안내극",
    "실적 시즌 긴장극",
    "세금 정산 현실극",
    "루틴 정착 힐링극",
)

STOCK_LOCATIONS_KO: Tuple[str, ...] = (
    "증권사 앱 켠 원룸 책상",
    "출근 전 지하철 모바일 HTS 화면",
    "점심시간 회사 옥상 휴대폰 차트",
    "퇴근 후 카페 노트북 리서치석",
    "주말 집 소파 재무제표 검토",
    "동네 도서관 투자 서적 코너",
    "편의점 앞 흡연 구역 시황 토론",
    "헬스장 러닝머신 위 팟캐스트 청취",
    "지하철 환승 통로 유튜브 시황",
    "사무실 창가 자리 몰래 시세 확인",
    "퇴근길 버스 정류장 앱 알림 확인",
    "주말 카페 브런치 투자 메모",
    "은행 창구 계좌 상담 데스크",
    "세무서 연말 정산 상담 창구",
    "증권사 지점 상담 테이블",
    "집 거실 TV 경제 뉴스 화면",
)

STOCK_LOCATIONS_EN: Tuple[str, ...] = (
    "studio apartment desk with brokerage app open",
    "subway commute mobile trading screen before work",
    "office rooftop lunch break phone chart check",
    "cafe laptop research seat after work",
    "weekend living room sofa financial statement review",
    "neighborhood library investing books corner",
    "convenience store front smoking corner market talk",
    "gym treadmill row listening to finance podcast",
    "subway transfer corridor watching market youtube",
    "office window seat discreet price check",
    "bus stop on evening commute app alert check",
    "weekend cafe brunch investment notes",
    "bank counter account consultation desk",
    "tax office year-end settlement consultation window",
    "brokerage branch consultation table",
    "living room TV economy news screen at home",
)

STOCK_FRESH_FEMALE_PROMPT = (
    "Photorealistic studio portrait of a sharp intelligent Korean woman in her late 20s, "
    "office worker, modern stylish chic haircut, confident focused gaze, "
    "smart modern casual beige knit with neat collar, "
    "bright crisp natural daylight, high-key luminous exposure, pristine crystal-clear studio lighting, "
    "radiant healthy skin tone, plain soft neutral background, "
    "vertical 9:16 portrait, upper body, looking at camera, "
    "ultra realistic skin texture, 85mm portrait lens, shallow depth of field, "
    "absolutely NO candlelight, NO dark moody shadows, NO dim amber lighting, "
    "no text, no watermark, no logo, no cartoon, no illustration"
)

STOCK_FRESH_MALE_PROMPT = (
    "Photorealistic studio portrait of a brilliant Korean office worker man in his early 30s, "
    "modern stylish haircut, intellectual sharp eyes, sleek dark grey modern blazer, "
    "bright crisp natural daylight, high-key luminous exposure, pristine crystal-clear studio lighting, "
    "radiant healthy skin tone, plain soft neutral background, "
    "vertical 9:16 portrait, upper body, looking at camera, "
    "ultra realistic skin texture, 85mm portrait lens, shallow depth of field, "
    "absolutely NO candlelight, NO dark moody shadows, NO dim amber lighting, "
    "no text, no watermark, no logo, no cartoon, no illustration"
)

# ── [SSOT] 씬별 비주얼 프롬프트 (2030 주식 투자 톤) ──────────────────
SCENE_VISUALS: Dict[int, str] = {
    1: "cinematic close up, woman sighing at desk staring at red stock chart on monitor, cold blue tone, 35mm film grain",
    2: "close up of Junhyuk sitting opposite, sharp intellectual expression giving risk advice, modern cafe bokeh, 50mm lens",
    3: "close up of smartphone screen glowing with AI stock assistant app, warm neon bokeh, 50mm lens",
    4: "woman smiling relieved looking at balanced portfolio dashboard, warm daylight, shallow depth of field",
    5: "wide shot of city skyline at dusk with rising chart overlay, confident woman walking, cold blue tone",
}

# ── [16개 주제 × 5씬 = 80개 대사 전량 수작업 큐레이션] ──────────────
_CURATED_DIALOGUES: Dict[str, Tuple[str, str, str, str, str]] = {
    "내가 사면 떨어지는 기적의 이유": (
        "내가 사자마자 파란불 뜨는 거 진짜 실화야?",
        "너 거래량 터진 꼭대기에서 샀잖아, 차트 좀 봐라.",
        "스톡마스터 AI 보니까 세력 이탈 구간이었네, 소름 돋아!",
        "AI 데이터대로 바닥 다질 때 분할 매수하니까 바로 빨간불 떴어!",
        "네이버에 스톡마스터 AI 한번 검색해보세요!",
    ),
    "남들은 다 돈 버는데 나만 마이너스": (
        "동기는 300 벌었다는데 내 계좌는 왜 파란불이야?",
        "걔는 외인 수급 보고 샀고, 너는 단톡방 소문 듣고 샀잖아.",
        "스톡마스터 AI 수급 분석 보니까 진짜 기관만 샀었네!",
        "남들 소문 대신 AI 메이저 수급 따라가니까 첫 수익 났잖아!",
        "네이버에 스톡마스터 AI 한번 검색해보세요!",
    ),
    "뉴스 보고 샀더니 거기가 상투": (
        "초대형 호재 뉴스 보고 샀는데 왜 떡락하는 건데?",
        "뉴스 떴을 땐 이미 세력이 개미한테 물량 넘긴 뒤지!",
        "스톡마스터 AI 과열 경보 보니까 진작 매도 신호였어!",
        "뉴스 뒤꽁무니 안 쫓고 AI 선행 데이터 보니까 물릴 일이 없어!",
        "네이버에 스톡마스터 AI 한번 검색해보세요!",
    ),
    "팔면 오르고 사면 내리는 마법": (
        "손절하니까 폭등하고 사면 폭락해, 마법 걸렸나 봐!",
        "심리로 매매하니까 세력 흔들기에 딱 털리는 거야.",
        "스톡마스터 AI 지지선 확인하니까 손절할 자리가 아니었네!",
        "감정 빼고 AI 타점 맞춰서 버티니까 반등 먹고 제대로 익절함!",
        "네이버에 스톡마스터 AI 한번 검색해보세요!",
    ),
    "물타기 하다가 대주주 될 판": (
        "물타기 계속하다가 진짜 이 회사 대주주 되겠어...",
        "하락 추세에서 물타면 비중만 커지고 계좌 다 녹아내려!",
        "스톡마스터 AI 반등 추세선 보니까 바닥 신호가 떴어!",
        "무지성 물타기 멈추고 AI 변곡점 노려서 평단 확 낮췄잖아!",
        "네이버에 스톡마스터 AI 한번 검색해보세요!",
    ),
    "단타 친다고 화장실만 들락날락": (
        "단타 치느라 회사 화장실을 도대체 몇 번 가는 건지...",
        "호가창 1초마다 보다가 멘탈 털리고 일도 손에 안 잡히지?",
        "스톡마스터 AI 조건 알림 켜두니까 화장실 안 가도 돼!",
        "목표가랑 손절가 AI가 딱 잡아주니까 업무도 편하고 수익도 봄!",
        "네이버에 스톡마스터 AI 한번 검색해보세요!",
    ),
    "친구 따라 샀다가 나만 물림": (
        "친구가 무조건 오른대서 샀는데 나만 마이너스야...",
        "친구는 이미 저 밑에서 샀고 너한테 고점 떠넘긴 거잖아.",
        "스톡마스터 AI로 종목 진단 돌려보니까 재무 완전 깡통이네!",
        "친구 말 다신 안 믿고 AI 실적 퀀트 데이터로 갈아타서 복구함!",
        "네이버에 스톡마스터 AI 한번 검색해보세요!",
    ),
    "익절은 2% 손절은 -40% 법칙": (
        "왜 벌 때는 2만원이고 잃을 때는 200만원인 거지?",
        "수익은 쫄아서 바로 팔고 손실은 희망 회로 돌려서 그래.",
        "스톡마스터 AI 손익비 계산기 쓰니까 매매 원칙이 서네!",
        "손절은 짧게 끊고 익절은 AI 추세 끝까지 발라먹으니 계좌 역전!",
        "네이버에 스톡마스터 AI 한번 검색해보세요!",
    ),
    "본전 오면 다 판다더니 평생 안 옴": (
        "제발 본전만 오면 주식 접는다고 기도한 지 1년째야...",
        "실적 꺾인 종목은 기도한다고 본전 절대 안 와, 냉정해져라.",
        "스톡마스터 AI 종목 교체 리포트 보니까 답이 바로 나오네!",
        "죽은 종목 털고 AI 주도주로 리밸런싱하니까 석 달 만에 본전 회복!",
        "네이버에 스톡마스터 AI 한번 검색해보세요!",
    ),
    "월급날 주식 샀다가 반토막 난 썰": (
        "피땀 흘려 번 월급 주식 넣자마자 반토막 났어 ㅠㅠ",
        "월급날 충동 매수하니까 시장 흐름도 안 보고 당하는 거지.",
        "스톡마스터 AI 거시 지표 보니까 지금 매수 타이밍 아니었어!",
        "월급 그냥 안 넣고 AI 분할 적립 시그널 받아서 넣으니 마음 편함!",
        "네이버에 스톡마스터 AI 한번 검색해보세요!",
    ),
    "유튜브 추천주 믿고 전재산 몰빵": (
        "유튜브 믿고 전재산 몰빵했는데 거래정지 당했어...",
        "조회수 빨아먹는 작전주 방송을 믿고 몰빵하면 어떡하냐!",
        "스톡마스터 AI 리스크 레이더 보니까 위험 종목 딱 뜨네!",
        "유튜브 사기꾼들 다 차단하고 AI 팩트 데이터로만 투자하기로 함!",
        "네이버에 스톡마스터 AI 한번 검색해보세요!",
    ),
    "차트 볼 줄 몰라서 감으로 매매": (
        "이동평균선이 뭔지도 모르고 그냥 느낌으로 샀어...",
        "카지노 룰렛 돌리듯 매매하니까 계좌가 남아나질 않지.",
        "스톡마스터 AI가 골든크로스랑 매수 타이밍 다 짚어주네!",
        "복잡한 차트 공부 안 해도 AI가 승률 높은 자리만 집어주니 신세계!",
        "네이버에 스톡마스터 AI 한번 검색해보세요!",
    ),
    "수익 난 건 팔고 물린 것만 남음": (
        "계좌 열어보니까 온통 -50% 잡주만 수두룩해...",
        "수익 난 좋은 주식은 팔아치우고 똥주만 모셔두니 그렇지.",
        "스톡마스터 AI 포트폴리오 진단하니까 문제점 바로 찔러주네!",
        "잡주 싹 정리하고 AI 추천 우량주 모아가니까 계좌 색깔이 바뀜!",
        "네이버에 스톡마스터 AI 한번 검색해보세요!",
    ),
    "세력이 개미 털어내는 구간": (
        "악재 뉴스에 무서워서 던졌더니 상한가 직행했어...",
        "거래량 없는 하락은 전형적인 개미 털기인데 그걸 털렸네.",
        "스톡마스터 AI 수급 보니까 개미만 털리고 기관은 풀매수였어!",
        "세력 속임수 패턴 AI로 미리 파악하니까 공포 구간에서 오히려 줍줍!",
        "네이버에 스톡마스터 AI 한번 검색해보세요!",
    ),
    "하루 종일 주식창만 보며 멘붕": (
        "눈 뜨자마자 주식창 보고 일도 안 잡히고 미치겠어...",
        "시세 중독되면 뇌동매매 터진다, 원칙부터 세우고 창 꺼라.",
        "스톡마스터 AI 자동 모니터링 걸어두니까 마음이 편안해!",
        "하루 종일 폰 안 쳐다봐도 AI가 알아서 알림 주니 일상도 찾음!",
        "네이버에 스톡마스터 AI 한번 검색해보세요!",
    ),
    "감 매매 끝내고 AI 데이터로 탈출": (
        "촉만 믿고 주식하다가 마이너스 4천 찍고 멘붕 왔어...",
        "감으로 하는 매매는 끝났어, 지금은 퀀트 데이터 싸움이야.",
        "스톡마스터 AI 알고리즘 돌려보니까 승률 80% 자리 딱 나와!",
        "감 매매 싹 버리고 AI 데이터 원칙 지키니까 마침내 플러스 전환!",
        "네이버에 스톡마스터 AI 한번 검색해보세요!",
    ),
}

# ── [SSOT] 주제 목록은 _CURATED_DIALOGUES에서 파생 (이중 표현 제거) ──
STOCK_TOPICS: Tuple[str, ...] = tuple(_CURATED_DIALOGUES.keys())


def _build_scene_specs(topic: str) -> Tuple[SceneSpec, ...]:
    """단일 생성 경로 — 폴백 없음. 누락 시 KeyError로 즉시 실패."""
    dialogues = _CURATED_DIALOGUES[topic]
    specs: List[SceneSpec] = []
    for i in range(SCENES_PER_TOPIC):
        idx = i + 1
        speaker, gender = SCENE_SPEAKER_SEQUENCE[i]
        cmin, cmax = SCENE_CHAR_LIMITS[idx]
        specs.append(
            SceneSpec(
                index=idx,
                speaker=speaker,
                gender=gender,
                dialogue=dialogues[i],
                char_min=cmin,
                char_max=cmax,
                visual=SCENE_VISUALS[idx],
            )
        )
    return tuple(specs)


def _build_stock_topic_specs() -> Dict[str, TopicSpec]:
    return {t: TopicSpec(topic=t, scenes=_build_scene_specs(t)) for t in STOCK_TOPICS}


STOCK_TOPIC_SPECS: Dict[str, TopicSpec] = _build_stock_topic_specs()

STOCK_NARRATIVE_MATRIX: Dict[str, Tuple[Tuple[str, str], ...]] = {
    t: tuple((s.dialogue, s.visual) for s in spec.scenes)
    for t, spec in STOCK_TOPIC_SPECS.items()
}


def build_scene_guide_prompt(topic: str, genre: str, run_no: int,
                             durations: Tuple[int, int, int, int, int] = (3, 4, 4, 5, 4)) -> str:
    """SSOT 조립 방식 — 페르소나/비트/금지어/길이를 각각 주입."""
    forbidden = ", ".join(FORBIDDEN_PHRASES)
    beats = "\n".join(
        f"  씬{i} = {SCENE_BEATS[i]} ({durations[i-1]}초, "
        f"{SCENE_CHAR_LIMITS[i][0]}~{SCENE_CHAR_LIMITS[i][1]}자)"
        for i in range(1, SCENES_PER_TOPIC + 1)
    )
    return (
        "너는 2030 직장인 현실극 숏폼 드라마 작가다.\n"
        f"주제='{topic}', 장르='{genre}', 회차={run_no}.\n"
        f"{SCENES_PER_TOPIC}씬 시나리오를 JSON으로만 출력하라. 설명/마크다운 금지.\n"
        f"★ 절대 금지: {forbidden}.\n"
        "실제 2030 직장인의 극사실주의 구어체 대화로 작성하라.\n"
        "★ 씬별 글자수 상한 엄수 (SSOT):\n"
        f"{beats}\n"
        f"씬5에는 반드시 '{SCENE5_REQUIRED_PHRASES[0]}'를 포함하라.\n"
    )


def validate_stock_domain_data() -> bool:
    """계약 검증기 — 카디널리티/길이/화자/필수문구/금지어 전수 검증."""
    errors: List[str] = []

    if len(STOCK_TOPICS) != EXPECTED_TOPIC_COUNT:
        errors.append(f"주제 {EXPECTED_TOPIC_COUNT}개 필수 (현재 {len(STOCK_TOPICS)})")
    if len(STOCK_GENRES) != EXPECTED_GENRE_COUNT:
        errors.append(f"장르 {EXPECTED_GENRE_COUNT}개 필수 (현재 {len(STOCK_GENRES)})")
    if len(STOCK_LOCATIONS_KO) != EXPECTED_LOCATION_COUNT:
        errors.append(f"장소 KO {EXPECTED_LOCATION_COUNT}개 필수 (현재 {len(STOCK_LOCATIONS_KO)})")
    if len(STOCK_LOCATIONS_EN) != EXPECTED_LOCATION_COUNT:
        errors.append(f"장소 EN {EXPECTED_LOCATION_COUNT}개 필수 (현재 {len(STOCK_LOCATIONS_EN)})")
    if len(STOCK_LOCATIONS_KO) != len(STOCK_LOCATIONS_EN):
        errors.append("장소 KO/EN 길이 불일치")
    if len(STOCK_TOPIC_SPECS) != EXPECTED_TOPIC_COUNT:
        errors.append(f"매트릭스 {EXPECTED_TOPIC_COUNT}개 필수 (현재 {len(STOCK_TOPIC_SPECS)})")
    if len(_CURATED_DIALOGUES) != EXPECTED_TOPIC_COUNT:
        errors.append(f"큐레이션 대사 {EXPECTED_TOPIC_COUNT}개 필수 (현재 {len(_CURATED_DIALOGUES)})")

    # ── 키 집합 3자 동등성 사전 검증 (침묵 실패 차단) ──────────────
    topics_set = set(STOCK_TOPICS)
    dialogues_set = set(_CURATED_DIALOGUES.keys())
    specs_set = set(STOCK_TOPIC_SPECS.keys())
    if topics_set != dialogues_set:
        missing = dialogues_set - topics_set
        extra = topics_set - dialogues_set
        errors.append(
            f"STOCK_TOPICS ↔ _CURATED_DIALOGUES 키 불일치 "
            f"(누락={sorted(missing)}, 초과={sorted(extra)})"
        )
    if topics_set != specs_set:
        missing = topics_set - specs_set
        extra = specs_set - topics_set
        errors.append(
            f"STOCK_TOPICS ↔ STOCK_TOPIC_SPECS 키 불일치 "
            f"(누락={sorted(missing)}, 초과={sorted(extra)})"
        )

    for t, spec in STOCK_TOPIC_SPECS.items():
        if len(spec.scenes) != SCENES_PER_TOPIC:
            errors.append(f"[{t}] 씬 개수 {SCENES_PER_TOPIC}개 필수 (현재 {len(spec.scenes)})")
            continue
        for s in spec.scenes:
            if not s.is_within_limits():
                errors.append(
                    f"[{t}] 씬{s.index} 글자수 위반: {s.char_len()}자 "
                    f"(허용 {s.char_min}~{s.char_max})"
                )
            exp_speaker, exp_gender = SCENE_SPEAKER_SEQUENCE[s.index - 1]
            if s.speaker != exp_speaker or s.gender != exp_gender:
                errors.append(
                    f"[{t}] 씬{s.index} 화자 불일치: "
                    f"{s.speaker}/{s.gender} (기대 {exp_speaker}/{exp_gender})"
                )
            for bad in FORBIDDEN_PHRASES:
                if bad in s.dialogue:
                    errors.append(f"[{t}] 씬{s.index} 금지어 포함: '{bad}'")
        scene5 = spec.scenes[4]
        for phrase in SCENE5_REQUIRED_PHRASES:
            if phrase not in scene5.dialogue:
                errors.append(f"[{t}] 씬5 필수 문구 누락: '{phrase}'")

    if errors:
        raise ValueError(
            "도메인 데이터 무결성 검증 실패:\n  - " + "\n  - ".join(errors)
        )
    return True


# ── 명시적 검증 호출 (import 부작용 제거) ────────────────────────────
# 무인 파이프라인은 진입 전 별도 게이트에서 validate_stock_domain_data()를
# 명시적으로 호출해야 한다. 모듈 import만으로는 검증이 실행되지 않는다.
if __name__ == "__main__":
    validate_stock_domain_data()
    print(
        f"[OK] 도메인 데이터 검증 통과: "
        f"주제 {len(STOCK_TOPICS)}개 × {SCENES_PER_TOPIC}씬 = "
        f"{len(STOCK_TOPICS) * SCENES_PER_TOPIC}개 대사"
    )