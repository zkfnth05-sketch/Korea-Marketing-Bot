# -*- coding: utf-8 -*-
"""
Drama Variation Planner
=======================
드라마 엔진의 일별 변주 결정기 (DailyVariationPlanner).

목적:
    - 같은 브랜드/같은 날짜/같은 이력이면 항상 같은 결과를 내는 "결정론적" 변주 플래너.
    - DramaHistoryStore 의 최근 7일 이력을 조회해 장르/배경 중복을 회피한다.

결정론 원칙:
    - 내장 hash() 절대 금지 (PYTHONHASHSEED 에 따라 값이 달라짐).
    - 모든 시드는 sha256 기반 _stable_seed 로만 산출한다.

인물 묘사 금지 원칙:
    - outfits 는 "의상/소품/배경"만 변주한다.
    - 인물 얼굴/외모/헤어 묘사 필드는 이 모듈에 존재하지 않는다.
      (마스터 사진 레퍼런스가 인물을 고정하므로 텍스트로 재정의하면 충돌한다.)

오디오 상한 원칙:
    - 컬 오디오는 Wan S2V 81프레임 = 5.0625초 상한을 넘지 않아야 한다.
    - 따라서 voice_variation.speed 는 VOICE_SPEED_MIN~MAX 범위 내에서만 선택한다.
"""

from __future__ import annotations

import hashlib
import logging
import os
from datetime import date as _date
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence

from modules.drama_engine.drama_history_store import DramaHistoryStore

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------
# 컬 오디오가 Wan S2V 81프레임 = 5.0625초 상한을 넘지 않는 범위에서만 허용.
# 글자수 예산은 drama_cut_budget 가 당일 배속으로 재산출한다.
VOICE_SPEED_MIN: float = 1.20
VOICE_SPEED_DEFAULT: float = 1.25
VOICE_SPEED_MAX: float = 1.30
# 날짜 시드로 선택하는 배속 후보 (1.25 비중 높음, 소수점 2자리)
VOICE_SPEED_CANDIDATES: Sequence[float] = (1.20, 1.25, 1.25, 1.25, 1.30)

HISTORY_LOOKBACK_DAYS: int = 7
# 연속 중복 0회 보장용 회피 창 상한 (이력 엔트리 개수 기준)
#   K = min(후보 개수 - 1, AVOID_MAX_ENTRIES)
AVOID_MAX_ENTRIES: int = 7
CUT_IDS: Sequence[str] = ("cut1", "cut2", "cut3", "cut4")

# ---------------------------------------------------------------------------
# 변주 풀 (컷별 7종+)
# ---------------------------------------------------------------------------
CUT_ANGLE_POOL: Dict[str, List[str]] = {
    "cut1": [  # hook
        "클로즈업 정면, 눈높이 고정, 얕은 심도",
        "3/4 측면 클로즈업, 턱선 강조, 배경 흐림",
        "로우앵글 클로즈업, 미세한 상향 시선",
        "하이앵글 덮어보기(over-the-shoulder) 클로즈업",
        "어깨 너머 플래시 컷, 순간 광량 강조",
        "정면 클로즈업, 화면 우측 1/3 배치, 좌측 여백",
        "측면 90도 프로필 클로즈업, 창광 림라이트",
        "미디엄 클로즈업, 손끝이 프레임 하단에 걸침",
    ],
    "cut2": [  # dialogue
        "오버더숄더(over-the-shoulder) 미디엄샷, 상대 어깨 전경",
        "측면 실루엣 미디엄샷, 역광 경계선",
        "다이아고널 구도 미디엄샷, 대각 프레이밍",
        "매디엄 투샷(two-shot), 두 인물 좌우 분할",
        "정면 미디엄샷, 어깨 라인 수평 정렬",
        "로우앵글 미디엄샷, 대화 상대는 프레임 밖",
        "측면 45도 미디엄샷, 배경 심도 분리",
        "핸드헬드 느낌의 미디엄샷, 미세 틸트",
    ],
    "cut3": [  # solution
        "폰 화면 확인 미디엄샷, 화면 방향 45도 틸트",
        "손 클로즈업, 폰을 쥔 손끝 디테일",
        "폰 빛이 얼굴에 비치는 클로즈업, 저조도 대비",
        "책상 위 폰 화면 오버헤드 샷, 손 그림자",
        "미디엄샷, 폰 화면을 향한 시선 축 강조",
        "손과 폰만 담은 매크로 컷, 배경 완전 아웃포커스",
        "측면 미디엄샷, 폰 광원이 측광으로 작동",
        "폰 화면 리플렉션 클로즈업, 유리 반사 활용",
    ],
    "cut4": [  # cta
        "정면 아이컨택 미디엄샷, 카메라 정렬",
        "웃음 클로즈업, 눈높이 정면",
        "반신 스마일 샷, 상반신 프레이밍",
        "정면 미디엄샷, 손짓 제스처 포함",
        "살짝 상향 로우앵글 반신샷, 자신감 축",
        "측면 3/4 반신샷, 카메라 쪽 시선",
        "정면 클로즈업, 프레임 중앙 대칭",
        "미디엄샷, 배경 여백을 넓게 둔 안정 구도",
    ],
}

PROPS_POOL: List[str] = [
    "커피잔",
    "와인잔",
    "핸드폰",
    "꽃 한 송이",
    "책",
    "노트북",
    "디저트 접시",
    "아이스티",
    "스크런치 노트",
    "향초",
    "무선 이어폰 케이스",
    "미니 화분",
    "테이블 램프",
    "린넨 쿠션",
]

# 실내 한정 표현만 사용한다. (실외/야외/해변/공원 금지)
# 해질녘 역광 등 '실내 창가 빛'은 허용.
TIME_OF_DAY_POOL: List[str] = [
    "이른 아침 (실내 창가 자연광, 낮은 색온도)",
    "오전 (커튼을 통과한 부드러운 확산광)",
    "정오 (창가 직사광, 짧은 그림자)",
    "늦은 오후 (실내로 길게 드는 골든아워 측광)",
    "해질녘 (창가 주황-핑크 그라데이션 역광)",
    "저녁 (실내 조명 + 창밖 블루아워)",
    "밤 (실내 단일 광원, 짙은 그림자)",
]

# 의상/소품/배경만 변주. 인물 얼굴/외모/헤어 묘사 금지.
OUTFIT_POOL: Dict[str, List[str]] = {
    "female": [
        "아이보리 니트 + 베이지 슬랙스, 골드 미니 이어링",
        "네이비 셔츠 + 화이트 데님, 실버 체인 목걸이",
        "오트밀 트렌치코트 + 블랙 슬랙스, 레더 스트랩 워치",
        "라이트그레이 후드 + 조거팬츠, 스터드 볼 캡",
        "블랙 터틀넥 + 울 스커트, 진주 드롭 이어링",
        "스트라이프 셔츠 + 크림 와이드팬츠, 슬림 벨트",
        "카멜 니트 베스트 + 화이트 셔츠, 브라운 레더 시계",
        "소프트 핑크 가디건 + 진, 미니멀 골드 링",
        "차콜 블레이저 + 실크 블라우스, 실버 뱅글 브레이슬릿",
        "린넨 원피스 + 스트로 햇, 우드 비즈 목걸이",
    ],
    "male": [
        "화이트 셔츠 + 차콜 슬랙스, 실버 메탈 워치",
        "그레이 니트 + 블랙 데님, 블랙 레더 벨트",
        "네이비 블레이저 + 베이지 치노, 브라운 더비 슈즈",
        "블랙 맨투맨 + 카고팬츠, 스틸 체인 목걸이",
        "다크그린 셔츠 + 블랙 슬랙스, 가죽 스트랩 워치",
        "스트라이프 티 + 린넨 팬츠, 캔버스 스니커즈",
        "오트밀 카디건 + 화이트 티, 실버 링",
        "라이트블루 셔츠 + 슬림 진, 브라운 레더 벨트",
        "차콜 수트 재킷 + 니트, 실버 타이 바",
        "베이지 셔츠 + 크림 슬랙스, 우드 비즈 브레이슬릿",
    ],
}

TONE_HINT_POOL: List[str] = [
    "차분하고 낮은 톤, 문장 끝을 부드럽게 내림",
    "밝고 경쾌한 톤, 중간 강세 살짝 강조",
    "속삭이듯 가까운 톤, 호흡 짧게",
    "단호한 톤, 핵심 단어에서 또렷한 강세",
    "따뜻하고 다정한 톤, 완만한 억양 곡선",
    "호기심 어린 톤, 문장 끝 살짝 올림",
    "정돈된 리포터 톤, 균일한 속도감",
]


# ---------------------------------------------------------------------------
# 결정론 시드
# ---------------------------------------------------------------------------
def _stable_seed(*parts: Any) -> int:
    """sha256 기반 결정론 정수 시드. 내장 hash() 사용 금지."""
    joined = "|".join("" if p is None else str(p) for p in parts)
    digest = hashlib.sha256(joined.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


class DailyVariationPlanner:
    """일별 변주 플래너 (결정론 + 이력 회피)."""

    def __init__(
        self,
        brand: str = "aura",
        history_store: Optional[DramaHistoryStore] = None,
    ) -> None:
        if not brand or not str(brand).strip():
            raise ValueError("brand 는 비어 있을 수 없습니다.")
        self.brand: str = str(brand).strip()
        self.history_store: DramaHistoryStore = (
            history_store
            if history_store is not None
            else DramaHistoryStore(self.brand)
        )

    # -- 내부 유틸 ---------------------------------------------------------
    @staticmethod
    def _pick(pool: Sequence[Any], seed: int) -> Any:
        if not pool:
            raise ValueError("pool 이 비어 있습니다.")
        return pool[seed % len(pool)]

    def _pick_avoiding(
        self,
        pool: Sequence[str],
        used: set,
        seed: int,
        kind: str,
    ) -> int:
        """시드 시작점에서 회전하며 used 에 없는 첫 인덱스 선택.

        used 는 '이력 엔트리 개수' 기준으로 산출된 회피 집합이며,
        크기가 항상 len(pool) - 1 이하이므로 최소 1개 후보가 남는다.
        따라서 정상 경로에서 연속 중복이 수학적으로 0회 보장된다.
        '전부 소진' 분기는 방어 로직으로만 남긴다.
        """
        n = len(pool)
        if n == 0:
            raise ValueError(f"{kind} 후보 풀이 비어 있습니다.")
        start = seed % n
        for offset in range(n):
            idx = (start + offset) % n
            if pool[idx] not in used:
                return idx

        # 방어 로직: 회피 집합이 후보를 전부 덮은 비정상 상태
        oldest_value = self._oldest_used_value(kind, used)
        if oldest_value is not None and oldest_value in pool:
            logger.warning(
                "%s 후보 전부 소진(방어 분기 진입) -> 이력상 가장 오래된 값 재사용: %s",
                kind,
                oldest_value,
            )
            return list(pool).index(oldest_value)
        logger.warning("%s 후보 전부 소진(방어 분기 진입) -> 시드 시작점 재사용", kind)
        return start

    def _oldest_used_value(self, kind: str, used: set) -> Optional[str]:
        """최근 이력에서 used 집합에 속한 값 중 가장 오래된 날짜의 값."""
        try:
            records = self.history_store.recent(n_days=HISTORY_LOOKBACK_DAYS)
        except OSError:
            logger.error("이력 조회 실패(%s) -> 시드 시작점 사용", kind, exc_info=True)
            return None
        oldest_date: Optional[str] = None
        oldest_value: Optional[str] = None
        for rec in records:
            val = rec.get(kind)
            if not isinstance(val, str) or val not in used:
                continue
            d = str(rec.get("date", ""))
            if oldest_date is None or d < oldest_date:
                oldest_date = d
                oldest_value = val
        return oldest_value

    def _avoid_set(self, kind: str, date_str: str, pool_size: int) -> set:
        """회피 집합: '이력 엔트리 개수' 기준 최근 K개 값.

        캘린더 일수 창(n_days)은 경계를 포함해 후보를 소진시키므로 사용하지 않는다.
        대상 엔트리는 date < date_str 인 이력만(같은 날짜 재호출 시 결정론 보장,
        당일 이후 엔트리 제외) 날짜 내림차순 정렬 후 최근 K개.
        K = min(후보 개수 - 1, AVOID_MAX_ENTRIES)
        """
        if pool_size <= 0:
            raise ValueError(f"{kind} 후보 개수는 1 이상이어야 합니다.")
        k = min(pool_size - 1, AVOID_MAX_ENTRIES)
        if k <= 0:
            return set()

        try:
            records = self.history_store.load()
        except OSError:
            logger.error("이력 조회 실패(%s) -> 빈 집합 사용", kind, exc_info=True)
            return set()

        prior: List[Dict[str, Any]] = []
        for rec in records:
            if not isinstance(rec, dict):
                continue
            rec_date = str(rec.get("date", ""))[:10]
            if not rec_date or rec_date >= date_str:
                continue
            prior.append(rec)
        prior.sort(key=lambda r: str(r.get("date", ""))[:10], reverse=True)

        avoid: set = set()
        for rec in prior[:k]:
            val = rec.get(kind)
            if isinstance(val, str) and val.strip():
                avoid.add(val.strip())
        return avoid

    # -- 메인 --------------------------------------------------------------
    def plan(
        self,
        date_str: str,
        genre_count: int = 8,
        location_count: int = 10,
        genre_ids: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """해당 날짜의 변주 플랜을 결정론적으로 산출한다."""
        if not isinstance(date_str, str) or not date_str.strip():
            raise ValueError("date_str 는 비어 있을 수 없습니다.")
        date_str = date_str.strip()[:10]
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"date_str 형식은 YYYY-MM-DD 여야 합니다: {date_str!r}")

        if genre_count <= 0 or location_count <= 0:
            raise ValueError("genre_count / location_count 는 1 이상이어야 합니다.")

        genre_pool: List[str] = (
            list(genre_ids) if genre_ids else [f"g{i}" for i in range(genre_count)]
        )
        location_pool: List[str] = (
            list(locations) if locations else [f"l{i}" for i in range(location_count)]
        )
        if not genre_pool or not location_pool:
            raise ValueError("장르/배경 후보 리스트가 비어 있습니다.")

        base_seed = _stable_seed(self.brand, date_str, "plan")

        # 장르 / 배경: 이력 엔트리 개수 기준 회피 (연속 중복 0회 보장)
        genre_index = self._pick_avoiding(
            genre_pool,
            self._avoid_set("genre_id", date_str, len(genre_pool)),
            base_seed,
            "genre_id",
        )
        location_index = self._pick_avoiding(
            location_pool,
            self._avoid_set("location", date_str, len(location_pool)),
            _stable_seed(self.brand, date_str, "location"),
            "location",
        )

        # 컷별 독립 시드
        cut_angles: Dict[str, str] = {}
        for cut_id in CUT_IDS:
            cut_seed = _stable_seed(self.brand, date_str, cut_id, "angle")
            cut_angles[cut_id] = self._pick(CUT_ANGLE_POOL[cut_id], cut_seed)

        # 소품 2개 (서로 다른 인덱스 보장)
        prop_seed = _stable_seed(self.brand, date_str, "props")
        p1 = prop_seed % len(PROPS_POOL)
        p2 = (prop_seed // 7 + 1) % len(PROPS_POOL)
        if p2 == p1:
            p2 = (p1 + 1) % len(PROPS_POOL)
        props: List[str] = [PROPS_POOL[p1], PROPS_POOL[p2]]

        time_of_day = self._pick(
            TIME_OF_DAY_POOL, _stable_seed(self.brand, date_str, "time_of_day")
        )

        outfits = {
            "female": self._pick(
                OUTFIT_POOL["female"], _stable_seed(self.brand, date_str, "outfit_f")
            ),
            "male": self._pick(
                OUTFIT_POOL["male"], _stable_seed(self.brand, date_str, "outfit_m")
            ),
        }

        # speed: 날짜 시드로 후보 [1.20, 1.25, 1.25, 1.25, 1.30] 중 선택
        #   컬 오디오가 81프레임 = 5.0625초 상한을 넘지 않는 범위에서만 허용.
        #   글자수 예산은 drama_cut_budget 가 당일 배속으로 재산출한다.
        speed_seed = _stable_seed(self.brand, date_str, "voice_speed")
        speed = round(
            float(VOICE_SPEED_CANDIDATES[speed_seed % len(VOICE_SPEED_CANDIDATES)]), 2
        )
        speed = min(max(speed, VOICE_SPEED_MIN), VOICE_SPEED_MAX)

        voice_variation = {
            "speed": speed,
            "tone_hint": self._pick(
                TONE_HINT_POOL, _stable_seed(self.brand, date_str, "tone")
            ),
        }

        seed_hex = hashlib.sha256(
            f"{self.brand}|{date_str}|plan".encode("utf-8")
        ).hexdigest()

        return {
            "date": date_str,
            "brand": self.brand,
            "genre_index": genre_index,
            "genre_id": genre_pool[genre_index],
            "location_index": location_index,
            "location": location_pool[location_index],
            "cut_angles": cut_angles,
            "props": props,
            "time_of_day": time_of_day,
            "outfits": outfits,
            "voice_variation": voice_variation,
            "seed_hex": seed_hex,
        }

    # -- 프롬프트 보강 -----------------------------------------------------
    def build_visual_addendum(
        self, plan: Dict[str, Any], cut_id: str, speaker_gender: str
    ) -> str:
        """플랜을 컬별 영문 프롬프트 보강 문구로 변환. 인물 외모 묘사 금지."""
        if not isinstance(plan, dict):
            raise TypeError("plan 은 dict 여야 합니다.")
        if cut_id not in CUT_IDS:
            raise ValueError(f"cut_id 는 {list(CUT_IDS)} 중 하나여야 합니다: {cut_id!r}")
        gender = str(speaker_gender).strip().lower()
        if gender not in ("female", "male"):
            raise ValueError("speaker_gender 는 'female' 또는 'male' 이어야 합니다.")

        angle = plan.get("cut_angles", {}).get(cut_id, "")
        props = plan.get("props", []) or []
        time_of_day = plan.get("time_of_day", "")
        outfit = plan.get("outfits", {}).get(gender, "")

        parts: List[str] = []
        if angle:
            parts.append(f"Camera angle: {angle}.")
        if props:
            parts.append("Props: " + ", ".join(str(p) for p in props) + ".")
        if time_of_day:
            parts.append(f"Time of day: {time_of_day}.")
        if outfit:
            parts.append(f"Wardrobe ({gender}): {outfit}.")
        parts.append(
            "Identity is locked to the master photo reference; "
            "do not alter face, appearance, or hairstyle."
        )
        return " ".join(parts)


# ---------------------------------------------------------------------------
# 자체 점검
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="[%(levelname)s] %(name)s: %(message)s"
    )

    print("=" * 72)
    print("DailyVariationPlanner 자체 점검")
    print("=" * 72)

    TEST_BRAND = "selftest_planner"
    GENRE_IDS = [f"genre_{i:02d}" for i in range(8)]
    LOCATIONS = [f"loc_{i:02d}" for i in range(10)]

    store = DramaHistoryStore(TEST_BRAND)
    planner = DailyVariationPlanner(brand=TEST_BRAND, history_store=store)
    print(f"STORE PATH : {store.path}")
    print(f"GENRE_IDS  : {GENRE_IDS}")
    print(f"LOCATIONS  : {LOCATIONS}")

    # 잔여물 정리
    for leftover in (
        store.path,
        store.path.with_suffix(store.path.suffix + ".corrupt"),
    ):
        if leftover.exists():
            os.remove(leftover)
            print(f"기존 잔여물 삭제: {leftover.name}")

    # 60일 시뮬레이션
    #   DramaHistoryStore.recent() 는 "오늘 기준" 상대 창이므로,
    #   시뮬레이션 날짜를 오늘로 매핑해 이력 창과 정합시킨다.
    print("\n[1] 60일 시뮬레이션 (plan -> record)")
    today = _date.today()
    sim_dates: List[str] = [
        (today - timedelta(days=59 - i)).isoformat() for i in range(60)
    ]
    plans: List[Dict[str, Any]] = []
    for i, sim_date in enumerate(sim_dates):
        mapped_date = (today - timedelta(days=59 - i)).isoformat()
        p = planner.plan(
            mapped_date,
            genre_count=len(GENRE_IDS),
            location_count=len(LOCATIONS),
            genre_ids=GENRE_IDS,
            locations=LOCATIONS,
        )
        p["_sim_date"] = sim_date
        plans.append(p)
        store.record(
            {
                "date": mapped_date,
                "genre_id": p["genre_id"],
                "location": p["location"],
                "template_id": f"tpl_{p['genre_index']}",
                "script_hash": DramaHistoryStore.hash_text(
                    f"{mapped_date}|{p['seed_hex']}"
                ),
                "hook_hash": DramaHistoryStore.hash_text(
                    f"hook|{mapped_date}|{p['seed_hex']}"
                ),
            }
        )
    print(f"    기록 건수 = {len(store.load())}")

    # 연속 중복 집계
    print("\n[2] 연속 날짜 중복 집계")
    genre_dup = sum(
        1
        for a, b in zip(plans, plans[1:])
        if a["genre_id"] == b["genre_id"]
    )
    loc_dup = sum(
        1
        for a, b in zip(plans, plans[1:])
        if a["location"] == b["location"]
    )
    print(f"    연속 날짜 장르 중복 횟수 = {genre_dup} / {len(plans) - 1}")
    print(f"    연속 날짜 배경 중복 횟수 = {loc_dup} / {len(plans) - 1}")
    print(f"    [판정] 연속 장르 중복 0회 = {genre_dup == 0}")
    print(f"    [판정] 연속 배경 중복 0회 = {loc_dup == 0}")

    # 배속 분포
    print("\n[2-1] 음성 배속 분포")
    speed_counts: Dict[float, int] = {}
    for p in plans:
        sp = float(p["voice_variation"]["speed"])
        speed_counts[sp] = speed_counts.get(sp, 0) + 1
    for sp in sorted(speed_counts):
        print(f"    speed={sp:.2f} : {speed_counts[sp]}일")
    print(f"    허용 범위 = {VOICE_SPEED_MIN} ~ {VOICE_SPEED_MAX}")
    print(f"    기본값 = {VOICE_SPEED_DEFAULT}")
    print(
        "    범위 준수 = "
        f"{all(VOICE_SPEED_MIN <= float(p['voice_variation']['speed']) <= VOICE_SPEED_MAX for p in plans)}"
    )
    print(
        "    후보 외 값 없음 = "
        f"{all(round(float(p['voice_variation']['speed']), 2) in [round(c, 2) for c in VOICE_SPEED_CANDIDATES] for p in plans)}"
    )

    # 의상 풀 배경 문구 잔존 검사
    print("\n[2-2] 의상 풀 배경 문구 잔존 검사")
    banned = ("배경", "야외", "정원", "테라스", "거리", "카페", "스튜디오", "데스크")
    dirty = [
        item
        for gender in ("female", "male")
        for item in OUTFIT_POOL[gender]
        if any(b in item for b in banned)
    ]
    print(f"    잔존 항목 수 = {len(dirty)}")
    for item in dirty:
        print(f"    !! {item}")
    print(f"    장르 사용 종류 = {len({p['genre_id'] for p in plans})} / {len(GENRE_IDS)}")
    print(f"    배경 사용 종류 = {len({p['location'] for p in plans})} / {len(LOCATIONS)}")

    # 결정론 검증
    print("\n[3] 결정론 검증 (동일 입력 재호출)")
    probe_date = sim_dates[-1]
    mapped_probe = today.isoformat()
    a = planner.plan(
        mapped_probe,
        genre_count=len(GENRE_IDS),
        location_count=len(LOCATIONS),
        genre_ids=GENRE_IDS,
        locations=LOCATIONS,
    )
    b = planner.plan(
        mapped_probe,
        genre_count=len(GENRE_IDS),
        location_count=len(LOCATIONS),
        genre_ids=GENRE_IDS,
        locations=LOCATIONS,
    )
    print(f"    재호출 결과 일치 = {a == b}")
    print(f"    seed_hex 일치 = {a['seed_hex'] == b['seed_hex']}")
    print(f"    seed_hex = {a['seed_hex'][:32]}...")
    print(
        f"    speed 범위 준수 = "
        f"{VOICE_SPEED_MIN <= a['voice_variation']['speed'] <= VOICE_SPEED_MAX}"
    )
    print(f"    speed 기본값 = {VOICE_SPEED_DEFAULT}")

    # 샘플 3일
    print("\n[4] 샘플 3일 플랜")
    for p in plans[-3:]:
        print(f"    --- {p['_sim_date']} ---")
        print(f"        genre_index={p['genre_index']} ({p['genre_id']})")
        print(f"        location_index={p['location_index']} ({p['location']})")
        print(f"        props={p['props']}")
        print(f"        time_of_day={p['time_of_day']}")
        print(f"        voice={p['voice_variation']}")
        for cut_id in CUT_IDS:
            print(f"        {cut_id}: {p['cut_angles'][cut_id]}")
        print(f"        outfits.female={p['outfits']['female']}")
        print(f"        outfits.male={p['outfits']['male']}")

    # 프롬프트 보강 샘플
    print("\n[5] build_visual_addendum 샘플")
    sample = plans[-1]
    for cut_id in CUT_IDS:
        print(f"    {cut_id} (female): {planner.build_visual_addendum(sample, cut_id, 'female')}")
    print(f"    cut1 (male)  : {planner.build_visual_addendum(sample, 'cut1', 'male')}")

    # 정리
    print("\n[6] 테스트 이력 파일 정리")
    for leftover in (
        store.path,
        store.path.with_suffix(store.path.suffix + ".corrupt"),
    ):
        if leftover.exists():
            os.remove(leftover)
            print(f"    삭제: {leftover.name}")
    print(f"    최종 잔여 파일 존재 = {store.path.exists()}")

    print("\n" + "=" * 72)
    print("자체 점검 완료")
    print("=" * 72)
