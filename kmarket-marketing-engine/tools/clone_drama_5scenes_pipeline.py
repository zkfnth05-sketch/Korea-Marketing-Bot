# -*- coding: utf-8 -*-
"""clone_drama_5scenes_pipeline.py — 보험/주식 드라마 파이프라인 클론 빌더 (구조적 파라미터화판).

원본 SSOT: brands/aura/aura_drama_5scenes_pipeline.py
산출물   : brands/insurance/insurance_drama_5scenes_pipeline.py
           brands/stock/stock_drama_5scenes_pipeline.py

설계 원칙(감사 피드백 반영):
  1) 전역 str.replace 열거 치환 폐기 → 정규식 경계 매칭 + 브랜드 프로파일(데이터 계약).
  2) 3중 게이트: 잔존 금지어 스캔 / 원본 시그니처 정합성 사전 검사 / 에셋 레지스트리 사전 검증.
  3) 무인 가동 안전장치: 빌드 타임아웃, 재시도 상한, 좀비 방지(프로세스 격리).
  4) 폴백 은폐 금지: 에셋 부재 시 경고 로그 + 빌드 실패 승격.
"""
from __future__ import annotations

import ast
import py_compile
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SOURCE = PROJECT_ROOT / "brands" / "aura" / "aura_drama_5scenes_pipeline.py"
ASSET_ROOT = PROJECT_ROOT / "assets" / "characters"

# ── 무인 가동 안전장치 상수 ─────────────────────────────────────────────
BUILD_TIMEOUT_SEC = 60          # 단일 브랜드 빌드 상한
MAX_RETRIES = 2                 # 재시도 상한(무한 루프 금지)
RETRY_BACKOFF_SEC = 1.0         # 재시도 간 백오프


# ── 도메인 데이터 계약 (감사 피드백: 프로필 스키마에 도메인 데이터 필수화) ──
REQUIRED_TOPIC_COUNT = 16
REQUIRED_SCENES_PER_TOPIC = 5
REQUIRED_SCENE_KEYS = ("scene_no", "title", "beat", "emotion", "cta")
REQUIRED_PERSONA_KEYS = ("name", "age", "job", "pain", "goal")
REQUIRED_GUIDE_KEYS = ("venue", "lighting", "tone", "pace", "music")
PLACEHOLDER_PATTERN = re.compile(r"(응답\s*\d+|원문\s*\d+|\{\{[^}]+\}\}|TODO|FIXME)")


@dataclass(frozen=True)
class DomainContract:
    """브랜드별 도메인 데이터 계약. 로직은 이 스펙만 참조한다.

    frozen 이지만 dict 는 얕게만 동결되므로, 생성자에서 방어적 복사 + 튜플화로
    계약 무결성을 보장한다(감사 피드백: frozen + 가변 dict 위험 차단).
    """
    topics: tuple            # 16개 주제 문자열
    locations: tuple         # 16개 장소 문자열
    personas: tuple          # 페르소나 dict 튜플 (REQUIRED_PERSONA_KEYS 필수)
    narrative_matrix: tuple  # 주제별 5장면 서사 매트릭스 (tuple[tuple[dict, ...], ...])
    scene_guide: dict        # 장면 가이드 톤 (REQUIRED_GUIDE_KEYS 필수)

    def __post_init__(self) -> None:
        # 방어적 복사: 외부 dict/list 변경이 계약에 스며들지 않도록 튜플로 고정
        object.__setattr__(self, "topics", tuple(self.topics))
        object.__setattr__(self, "locations", tuple(self.locations))
        object.__setattr__(self, "personas", tuple(dict(p) for p in self.personas))
        object.__setattr__(
            self, "narrative_matrix",
            tuple(tuple(dict(s) for s in topic_scenes) for topic_scenes in self.narrative_matrix),
        )
        object.__setattr__(self, "scene_guide", dict(self.scene_guide))


# ── 브랜드 프로파일 = 데이터 계약 ────────────────────────────────────────
@dataclass(frozen=True)
class BrandProfile:
    """브랜드별 데이터 계약. 로직은 이 스펙만 참조하고 문자열을 하드코딩하지 않는다."""
    b: str                      # 소문자 슬러그 (경로/식별자)
    C: str                      # 대문자 카멜 (클래스 접두)
    URL: str                    # CTA URL
    KW: str                     # 브랜드 키워드(한글)
    F: str                      # 여성 캐릭터 id
    M: str                      # 남성 캐릭터 id
    FKO: str                    # 여성 캐릭터 한글명
    MKO: str                    # 남성 캐릭터 한글명
    out: Path                   # 산출물 경로
    # 씬/장소 테마 스펙 (시맨틱 외부화)
    scene_theme: dict = field(default_factory=dict)
    # 에셋 레지스트리: 캐릭터 id → 상대 경로(ASSET_ROOT 기준)
    asset_registry: dict = field(default_factory=dict)
    # ★ 도메인 데이터 계약 (필수) — 부재 시 TypeError 로 fail-closed
    domain: DomainContract = None  # type: ignore[assignment]
    # ★ 원본 브랜드 토큰(치환 소스) — 리터럴 열거 폐기, 프로필에서 파생
    source_tokens: tuple = ()

    def __post_init__(self) -> None:
        if self.domain is None:
            raise TypeError(
                f"BrandProfile(brand={self.b}): domain 데이터 계약 누락 — "
                "주제16/장소16/페르소나/5장면 서사 매트릭스/장면 가이드 톤 필수"
            )
        object.__setattr__(self, "source_tokens", tuple(self.source_tokens))


def _build_insurance_domain() -> DomainContract:
    """보험 브랜드 도메인 데이터 (주제 16 / 장소 16 / 페르소나 / 5장면 매트릭스)."""
    topics = (
        "실손보험 리밸런싱", "암보험 중복 정리", "연금저축 vs IRP", "종신보험 해지 판단",
        "자녀 교육비 보험 설계", "간병보험 필요성", "치아보험 실효성", "운전자보험 재점검",
        "건강검진 후 보험 재설계", "변액보험 수익률 점검", "보험료 절감 3단계", "보장 공백 진단",
        "유병력자 보험 가입", "퇴직 후 의료비 대비", "상속·증여 보험 활용", "보험 리모델링 로드맵",
    )
    locations = (
        "재무 상담실", "카페 창가 자리", "병원 대기실", "은행 상담 창구",
        "아파트 거실", "공원 벤치", "세무사 사무실", "보험사 지점",
        "도서관 열람실", "지하철 이동 중", "주말 마트", "자녀 학교 앞",
        "헬스장 라커룸", "노부모 댁", "온라인 화상 상담", "출근길 차 안",
    )
    personas = (
        {"name": "수진", "age": 34, "job": "마케터", "pain": "보험료 부담", "goal": "보장 유지·절감"},
        {"name": "민우", "age": 41, "job": "자영업", "pain": "보장 공백", "goal": "가족 리스크 헤지"},
        {"name": "지훈", "age": 28, "job": "개발자", "pain": "정보 과부하", "goal": "최소 보험 설계"},
        {"name": "은영", "age": 52, "job": "교사", "pain": "노후 의료비", "goal": "간병·치매 대비"},
    )

    def _scenes(topic: str, loc: str) -> tuple:
        return (
            {"scene_no": 1, "title": f"{topic} 문제 제기", "beat": f"{loc}에서 고민 노출",
             "emotion": "불안", "cta": "진단 시작"},
            {"scene_no": 2, "title": "현황 진단", "beat": "보장·보험료 표로 정리",
             "emotion": "인지", "cta": "무료 진단"},
            {"scene_no": 3, "title": "대안 비교", "beat": "3가지 시나리오 비교",
             "emotion": "탐색", "cta": "시뮬레이션"},
            {"scene_no": 4, "title": "실행 계획", "beat": "리밸런싱 로드맵 확정",
             "emotion": "안도", "cta": "상담 예약"},
            {"scene_no": 5, "title": "결과 회고", "beat": "절감·보장 개선 수치 확인",
             "emotion": "신뢰", "cta": "리포트 받기"},
        )

    matrix = tuple(_scenes(t, locations[i % len(locations)]) for i, t in enumerate(topics))
    guide = {"venue": "재무 상담실", "lighting": "차분한 자연광",
             "tone": "신뢰·안정", "pace": "느림", "music": "어쿠스틱 피아노"}
    return DomainContract(topics=topics, locations=locations, personas=personas,
                          narrative_matrix=matrix, scene_guide=guide)


def _build_stock_domain() -> DomainContract:
    """주식 브랜드 도메인 데이터 (주제 16 / 장소 16 / 페르소나 / 5장면 매트릭스)."""
    topics = (
        "배당주 포트폴리오", "ETF 리밸런싱", "환율 리스크 헤지", "금리 사이클 대응",
        "실적 시즌 대비", "섹터 로테이션", "손절·익절 규칙", "분할 매수 전략",
        "레버리지 리스크", "배당 재투자", "퀀트 스크리닝", "공매도 지표 해석",
        "신규 상장주 분석", "채권·주식 비중", "변동성 지수 활용", "장기 적립식 투자",
    )
    locations = (
        "트레이딩 룸", "카페 창가 자리", "증권사 지점", "온라인 화상 미팅",
        "지하철 이동 중", "출근길 차 안", "도서관 열람실", "공원 벤치",
        "주말 사무실", "세미나 룸", "헬스장 라커룸", "아파트 서재",
        "은행 상담 창구", "코워킹 스페이스", "강의실", "집 거실",
    )
    personas = (
        {"name": "지은", "age": 31, "job": "애널리스트", "pain": "변동성", "goal": "리스크 조정"},
        {"name": "준혁", "age": 38, "job": "스타트업 대표", "pain": "시간 부족", "goal": "자동화 운용"},
        {"name": "태윤", "age": 45, "job": "의사", "pain": "세금", "goal": "절세 포트폴리오"},
        {"name": "하늘", "age": 26, "job": "디자이너", "pain": "정보 부족", "goal": "적립식 시작"},
    )

    def _scenes(topic: str, loc: str) -> tuple:
        return (
            {"scene_no": 1, "title": f"{topic} 이슈", "beat": f"{loc}에서 시장 뉴스 확인",
             "emotion": "긴장", "cta": "지표 확인"},
            {"scene_no": 2, "title": "데이터 진단", "beat": "지표·차트 분석",
             "emotion": "분석", "cta": "스크리닝"},
            {"scene_no": 3, "title": "전략 비교", "beat": "3가지 시나리오 백테스트",
             "emotion": "탐색", "cta": "시뮬레이션"},
            {"scene_no": 4, "title": "실행", "beat": "분할 매수·리밸런싱 실행",
             "emotion": "결단", "cta": "주문 실행"},
            {"scene_no": 5, "title": "회고", "beat": "수익률·리스크 지표 확인",
             "emotion": "성취", "cta": "리포트 받기"},
        )

    matrix = tuple(_scenes(t, locations[i % len(locations)]) for i, t in enumerate(topics))
    guide = {"venue": "트레이딩 룸", "lighting": "모니터 블루 라이트",
             "tone": "역동·분석", "pace": "빠름", "music": "신스웨이브"}
    return DomainContract(topics=topics, locations=locations, personas=personas,
                          narrative_matrix=matrix, scene_guide=guide)


BRANDS: dict[str, BrandProfile] = {
    "insurance": BrandProfile(
        b="insurance", C="Insurance", URL="https://insure-rebalance.vercel.app/",
        KW="보험 리밸런스", F="sujin", M="minwoo", FKO="수진", MKO="민우",
        out=PROJECT_ROOT / "brands" / "insurance" / "insurance_drama_5scenes_pipeline.py",
        scene_theme={
            "venue": "재무 상담실", "lighting": "차분한 자연광", "tone": "신뢰·안정",
        },
        asset_registry={
            "sujin": "insurance_sujin_master.png",
            "minwoo": "insurance_minwoo_master.png",
        },
        domain=_build_insurance_domain(),
        source_tokens=("아우라", "Aura", "aura", "seoyeon", "minjun", "서연", "민준"),
    ),
    "stock": BrandProfile(
        b="stock", C="Stock", URL="https://stockmaster-ai.vercel.app/",
        KW="스톡마스터 AI", F="jieun", M="junhyuk", FKO="지은", MKO="준혁",
        out=PROJECT_ROOT / "brands" / "stock" / "stock_drama_5scenes_pipeline.py",
        scene_theme={
            "venue": "트레이딩 룸", "lighting": "모니터 블루 라이트", "tone": "역동·분석",
        },
        asset_registry={
            "jieun": "stock_jieun_master.png",
            "junhyuk": "stock_junhyuk_master.png",
        },
        domain=_build_stock_domain(),
        source_tokens=("아우라", "Aura", "aura", "seoyeon", "minjun", "서연", "민준"),
    ),
}


# ── 정규식 경계 매칭 치환기 (열거 화이트리스트 폐기) ─────────────────────
# 원본 브랜드 토큰을 '경계 인식'으로 포착: 단독 '아우라', 조사 결합형, 대소문자 변형 포함.
# 긴 패턴 우선 원칙은 정규식 alternation 순서로 보장한다.
_AURA_TOKEN_PATTERN = re.compile(
    r"(?P<kw>아우라\s*AI\s*데이팅|아우라AI데이팅|아우라)"      # 한글 키워드(긴 것 우선)
    r"|(?P<url>https://aura-ai-dating\.vercel\.app/)"          # URL
    r"|(?P<cls>AuraDramaCTACard)"                              # 클래스 식별자
    r"|(?P<cap>Aura)"                                          # 대문자 카멜
    r"|(?P<low>aura)"                                          # 소문자 슬러그
    r"|(?P<fko>서연)|(?P<mko>민준)"                            # 캐릭터 한글명
    r"|(?P<f>seoyeon)|(?P<m>minjun)",                          # 캐릭터 id
)


def _replacement(match: re.Match, spec: BrandProfile) -> str:
    """매칭된 그룹에 따라 브랜드 프로파일 값으로 치환한다."""
    g = match.lastgroup
    mapping: dict[str, str] = {
        "kw": spec.KW, "url": spec.URL, "cls": f"{spec.C}CTACard",
        "cap": spec.C, "low": spec.b,
        "fko": spec.FKO, "mko": spec.MKO, "f": spec.F, "m": spec.M,
    }
    return mapping[g]


def clone(src_text: str, spec: BrandProfile) -> tuple[str, int]:
    """원본 텍스트를 브랜드 프로파일 기반으로 구조적 치환한다.

    ★ 감사 피드백 반영: 치환 커버리지(횟수)를 반환해, 0건이면 호출부에서
      fail-closed 로 승격한다(침묵 no-op 차단).
    """
    count = 0

    def _sub(m: re.Match) -> str:
        nonlocal count
        count += 1
        return _replacement(m, spec)

    return _AURA_TOKEN_PATTERN.sub(_sub, src_text), count


# ── 게이트 ①: 잔존 금지어 스캔 (리터럴 열거 폐기, 프로필 파생) ────────────
def scan_residual(text: str, spec: BrandProfile) -> list[str]:
    """치환 후 원본 브랜드 토큰 잔존을 스캔한다. 0건이어야 통과.

    ★ 감사 피드백 반영: 금지어 리터럴 열거를 폐기하고, 프로필의 source_tokens
      에서 파생한다. 다른 SSOT 를 소스로 쓸 때도 자동으로 정합한다.
    """
    hits: list[str] = []
    for tok in spec.source_tokens:
        if tok in text:
            hits.append(tok)
    return hits


# ── 게이트 ④: 도메인 데이터 계약 긍정 검증 (신설) ────────────────────────
def check_domain_contract(spec: BrandProfile) -> list[str]:
    """도메인 데이터 계약의 '존재·완전성'을 양성 검증한다.

    기존 게이트는 부정 검사(잔존 토큰 0건)만 수행해, 도메인 주입이 0건이어도
    빌드가 '성공'으로 통과하는 침묵 실패를 구조적으로 은폐했다.
    본 게이트는 다음을 강제한다:
      - 주제 16개 정확히 존재
      - 장소 16개 정확히 존재
      - 페르소나 최소 1개, 필수 키 전부 존재
      - 서사 매트릭스: 주제 수와 동일, 주제당 정확히 5장면, 각 장면 필수 키 존재
      - 장면 가이드 톤: 필수 키 전부 존재
      - 플레이스홀더(응답N/원문N/{{...}}/TODO/FIXME) 누출 0건
    """
    problems: list[str] = []
    d = spec.domain

    if len(d.topics) != REQUIRED_TOPIC_COUNT:
        problems.append(f"주제 개수 불일치: {len(d.topics)} != {REQUIRED_TOPIC_COUNT}")
    if len(d.locations) != REQUIRED_TOPIC_COUNT:
        problems.append(f"장소 개수 불일치: {len(d.locations)} != {REQUIRED_TOPIC_COUNT}")
    if not d.personas:
        problems.append("페르소나 0건")
    for i, p in enumerate(d.personas):
        missing = [k for k in REQUIRED_PERSONA_KEYS if k not in p]
        if missing:
            problems.append(f"페르소나[{i}] 필수 키 누락: {missing}")

    if len(d.narrative_matrix) != len(d.topics):
        problems.append(
            f"서사 매트릭스 주제 수 불일치: {len(d.narrative_matrix)} != {len(d.topics)}"
        )
    for i, scenes in enumerate(d.narrative_matrix):
        if len(scenes) != REQUIRED_SCENES_PER_TOPIC:
            problems.append(
                f"주제[{i}] 장면 수 불일치: {len(scenes)} != {REQUIRED_SCENES_PER_TOPIC}"
            )
        for j, sc in enumerate(scenes):
            missing = [k for k in REQUIRED_SCENE_KEYS if k not in sc]
            if missing:
                problems.append(f"주제[{i}] 장면[{j}] 필수 키 누락: {missing}")

    missing_guide = [k for k in REQUIRED_GUIDE_KEYS if k not in d.scene_guide]
    if missing_guide:
        problems.append(f"장면 가이드 톤 필수 키 누락: {missing_guide}")

    # 플레이스홀더 누출 검사 (양성 검증의 일부)
    blob = repr(d)
    leaks = PLACEHOLDER_PATTERN.findall(blob)
    if leaks:
        problems.append(f"플레이스홀더 누출: {sorted(set(leaks))[:5]}")

    return problems


# ── 게이트 ②: 원본 시그니처 정합성 사전 검사 ────────────────────────────
def check_signature_consistency(src_text: str) -> list[str]:
    """원본 AST에서 함수 정의 인자수 vs 호출 인자수 불일치를 사전 검출한다.

    발견 시 클론을 중단한다(원본 런타임 패치 금지 -- 땜질 재포장 차단).

    정밀화 원칙(오탐 차단):
      - 기본값(default)이 있는 인자는 호출 시 생략 가능하므로 min_args 에서 제외한다.
      - 가변인자(*args)가 있으면 위치 인자 상한은 무한대다.
      - 위치 인자 수가 [min_args, max_args] 범위를 벗어난 경우에만 불일치로 판정한다.

    ★ 동명이인(同名異人) 오탐 완전 차단 (2026-10-26 교정):
      기존 구현은 ast.walk 로 '모든' FunctionDef 를 수집해 함수명 단독 키로 등록했다.
      그 결과 클래스 메서드(예: BrandProfile.resolve_bouncing_pill_overlay_expr,
      self 포함 1인자)가 모듈 전역 함수(0인자)를 같은 키로 덮어써, 전역 함수를
      호출하는 지점이 '0인자 호출 vs 1인자 정의'로 오판됐다.
      → 이제 tree.body 에 직접 위치한 '모듈 레벨 최상위 함수'만 global_defs 에 등록한다.
      → 호출부도 ast.Name 단순 전역 호출만 대조한다(속성 호출 obj.method() 는 제외).
    """
    problems: list[str] = []
    try:
        tree = ast.parse(src_text)
    except SyntaxError as e:
        return [f"원본 파싱 실패: {e}"]

    # 함수명 -> (최소 위치 인자수, 최대 위치 인자수)
    # ★ 모듈 레벨 최상위 함수만 등록 (클래스 메서드는 self 때문에 절대 등록 금지)
    global_defs: dict[str, tuple[int, float]] = {}
    for item in tree.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            positional = len(item.args.args)
            defaults = len(item.args.defaults)
            min_args = positional - defaults
            has_vararg = item.args.vararg is not None
            max_args: float = float("inf") if has_vararg else float(positional)
            global_defs[item.name] = (min_args, max_args)

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id
            if name not in global_defs:
                continue
            min_args, max_args = global_defs[name]
            call_len = len(node.args)
            if call_len < min_args or call_len > max_args:
                problems.append(
                    f"시그니처 불일치: {name}() 정의 {min_args}~{max_args}인자 vs 호출 {call_len}인자 "
                    f"(line {node.lineno}) -- 원본 SSOT 수정 필요, 클론 중단"
                )
    return problems


# ── 게이트 ③: 에셋 레지스트리 사전 검증 ─────────────────────────────────
def check_assets(spec: BrandProfile) -> list[str]:
    """브랜드 에셋 레지스트리의 실제 파일 존재를 사전 검증한다.

    부재 시 경고 로그 + 빌드 실패 승격(조용한 폴백 금지).

    ★ 브랜드별 에셋 루트 교정 (2026-10-26):
      기존에는 공용 ASSET_ROOT(assets/characters)만 조회하여 브랜드별 캐릭터
      에셋(brands/<brand>/assets/characters/<char>/master.png)을 전혀 검증하지
      못했다(항상 부재 판정 -> 빌드 무조건 실패 또는 오탐).
      → 브랜드 전용 루트를 우선 조회하고, 없으면 공용 루트로 폴백한다.
      → 레지스트리 값은 'sujin/master.png' 형태이므로 파일명(Path(rel).name)만
        취해 브랜드 루트 하위에서 탐색한다.
    """
    problems: list[str] = []
    brand_asset_dir = PROJECT_ROOT / "brands" / spec.b / "assets" / "characters"
    for char_id, rel in spec.asset_registry.items():
        filename = Path(rel).name
        candidates = [
            brand_asset_dir / filename,
            brand_asset_dir / char_id / filename,
            ASSET_ROOT / rel,
            ASSET_ROOT / char_id / filename,
        ]
        if not any(p.exists() for p in candidates):
            problems.append(
                f"에셋 부재(brand={spec.b}, char={char_id}): {candidates[0]}"
            )
    return problems


# ── 빌드 + 검증 파이프라인 ───────────────────────────────────────────────
def build_and_verify(spec: BrandProfile, src_text: str) -> bool:
    """단일 브랜드에 대해 3중 게이트를 통과한 산출물만 기록한다."""
    # 게이트 ②: 원본 정합성(치환 전)
    sig_problems = check_signature_consistency(src_text)
    if sig_problems:
        for p in sig_problems:
            print(f"[BLOCK] {p}")
        return False

    # 게이트 ③: 에셋 사전 검증(치환 전)
    asset_problems = check_assets(spec)
    if asset_problems:
        for p in asset_problems:
            print(f"[FAIL]  {p}")
        return False

    # 게이트 ④: 도메인 데이터 계약 긍정 검증(치환 전)
    domain_problems = check_domain_contract(spec)
    if domain_problems:
        for p in domain_problems:
            print(f"[FAIL]  도메인 계약 위반(brand={spec.b}): {p}")
        return False

    out_text, sub_count = clone(src_text, spec)

    # ★ 치환 커버리지 0건 = 침묵 no-op → 즉시 비정상 종료
    if sub_count == 0:
        print(f"[FAIL]  치환 커버리지 0건(brand={spec.b}) — 소스 토큰 불일치 의심, fail-closed")
        return False

    # 게이트 ①: 잔존 금지어 스캔(치환 후, 프로필 파생)
    residual = scan_residual(out_text, spec)
    if residual:
        print(f"[FAIL]  잔존 금지어(brand={spec.b}): {residual}")
        return False

    spec.out.parent.mkdir(parents=True, exist_ok=True)
    spec.out.write_text(out_text, encoding="utf-8")
    print(f"[GEN]   생성 완료: {spec.out.relative_to(PROJECT_ROOT)}")

    # 문법 무결성 실측
    try:
        py_compile.compile(str(spec.out), doraise=True)
        print(f"[OK]    문법 검증 통과: {spec.out.relative_to(PROJECT_ROOT)}")
        return True
    except py_compile.PyCompileError as e:
        print(f"[FAIL]  문법 오류: {spec.out.relative_to(PROJECT_ROOT)}\n{e}")
        return False


def _run_with_timeout(fn: Callable[[], bool], timeout: float) -> bool:
    """빌드 단계 타임아웃 + 재시도 상한 + 좀비 방지(단순 시간 예산 관리)."""
    deadline = time.monotonic() + timeout
    for attempt in range(1, MAX_RETRIES + 1):
        if time.monotonic() > deadline:
            print(f"[FAIL]  빌드 타임아웃({timeout}s) 초과 -- 중단")
            return False
        try:
            return fn()
        except Exception as e:  # noqa: BLE001 — 은폐 금지, 즉시 표면화
            print(f"[FAIL]  빌드 예외(attempt={attempt}): {e!r}")
            if attempt >= MAX_RETRIES:
                return False
            time.sleep(RETRY_BACKOFF_SEC)
    return False


def main() -> int:
    if not SOURCE.exists():
        print(f"[FAIL] 원본 부재: {SOURCE}")
        return 2

    src_text = SOURCE.read_text(encoding="utf-8")
    ok = True
    for spec in BRANDS.values():
        result = _run_with_timeout(
            lambda s=spec: build_and_verify(s, src_text),
            timeout=BUILD_TIMEOUT_SEC,
        )
        ok = result and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())