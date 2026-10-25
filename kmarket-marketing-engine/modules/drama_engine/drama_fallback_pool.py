# -*- coding: utf-8 -*-
"""
modules/drama_engine/drama_fallback_pool.py
===================================================================================================
🎭 [DramaFallbackPool] — Gemini 대본 생성 실패 / 쿼터 소진 시 사용하는 확장 폴백 대본 풀
---------------------------------------------------------------------------------------------------
[설계 원칙]
  1. 기존 14종(약 26일 주기 반복)을 대체하는 8장르 x 4변형 = 32종 풀.
     (director 의 장르 id 와 동일: fluttering / witty / cool / direct / firsttalk / values /
      closure / destiny)
  2. 모든 템플릿은 drama_cut_budget.CutBudgetValidator 실측 예산(Wan S2V 81프레임 5.0625초)을
     음성 배속 1.20 / 1.25 / 1.30 세 값 모두에서 통과해야 한다. (validate_pool 로 증명)
  3. 대사는 배경(로케이션)에 의존하지 않는다. 배경은 플래너/디렉터가 매일 따로 정한다.
  4. 컷당 화자 1명: cut1 female / cut2 male / cut3 female / cut4 female. (대표님 절대 규격)
  5. cut4 는 반드시 공식 검색어 '아우라AI데이팅'(붙여쓰기) + '검색' 을 포함하고 URL 은 넣지 않는다.
  6. try-except pass 금지. 예외는 로그 후 재발생.
===================================================================================================
"""

from __future__ import annotations

import hashlib
import logging
import sys
from typing import Any, Dict, Iterable, List, Optional, Tuple

logger = logging.getLogger(__name__)

OFFICIAL_KEYWORD: str = "아우라AI데이팅"
REQUIRED_CTA_TOKENS: Tuple[str, str] = (OFFICIAL_KEYWORD, "검색")
VALIDATION_SPEEDS: Tuple[float, ...] = (1.20, 1.25, 1.30)

_ROLES: Tuple[Tuple[str, str], ...] = (
    ("hook", "female"),
    ("dialogue", "male"),
    ("solution", "female"),
    ("cta", "female"),
)


# (genre_id, theme, cut1, cut2, cut3, cut4)
# 길이 기준: 배속 1.20/1.25/1.30 모두 통과하는 교집합 (공백·문장부호 포함)
#   cut1(여) 17~35 / cut2(남) 21~33 / cut3(여) 27~35 / cut4(여) 19~35
_RAW_POOL: Tuple[Tuple[str, str, str, str, str, str], ...] = (
    # ----------------------------------------------------------------- fluttering (설렘)
    ("fluttering", "손끝이 스친 순간, 시간이 멈췄다",
     "손이 닿았는데, 왜 이렇게 떨리지.",
     "죄송해요, 컵 건네다 손이 닿았네요. 괜찮으세요?",
     "괜찮은데 심장이 안 괜찮아. 이런 설렘 정말 오랜만이야.",
     "이런 설렘 찾는다면 네이버에 아우라AI데이팅 검색해보세요."),
    ("fluttering", "말없이 건넨 작은 배려",
     "내가 추운 걸 어떻게 알았지? 신기해.",
     "손이 차가워 보여서요. 따뜻한 걸 먼저 시켰어요.",
     "말 안 해도 알아주는 사람. 이런 배려가 제일 설레.",
     "섬세한 사람 궁금하면 네이버에 아우라AI데이팅 검색해보세요."),
    ("fluttering", "웃는 얼굴이 자꾸 떠오른다",
     "웃는 얼굴이 자꾸 생각나는데, 어쩌지.",
     "저도 아까 웃던 모습이 계속 생각나서 연락했어요.",
     "같은 순간을 기억했다니. 이런 우연이 사랑의 시작이겠지.",
     "마음 맞는 인연이라면 네이버에 아우라AI데이팅 검색해보세요."),
    ("fluttering", "처음 듣는데 편안한 목소리",
     "목소리가 왜 이렇게 편안하지, 이상하다.",
     "처음인데 이상하게 오래 알던 사람처럼 편하네요.",
     "낯선데 편안한 사람. 이게 진짜 끌림이라는 걸 알았어.",
     "끌리는 사람 만나려면 네이버에 아우라AI데이팅 검색해보세요."),
    # ----------------------------------------------------------------- witty (티키타카)
    ("witty", "티키타카가 통하는 사람이 오래 간다",
     "이 대화, 왜 이렇게 안 끊기지?",
     "저도 신기해요. 서연 씨가 계속 받아쳐 주시잖아요.",
     "웃으며 대화가 이어지는 사람. 이게 잘 맞는 거구나.",
     "대화 통하는 사람 원하면 네이버에 아우라AI데이팅 검색해보세요."),
    ("witty", "취향이 겹치는 순간",
     "잠깐, 나도 그거 엄청 좋아하는데?",
     "진짜요? 이 얘기하면 다들 이상하게 보는데 신기하네요.",
     "취향이 겹치면 대화가 이렇게 쉽구나. 말이 술술 나와.",
     "취향 맞는 사람 궁금하면 네이버에 아우라AI데이팅 검색해보세요."),
    ("witty", "웃음 코드가 같은 사람",
     "방금 그 농담, 나만 웃겼던 거야?",
     "아니요, 저도 터졌어요. 웃음 포인트 같은 분 처음이에요.",
     "웃음 코드가 같다는 건 큰 거야. 심심할 일 없겠어.",
     "웃음 코드 맞는 사람은 네이버에 아우라AI데이팅 검색해보세요."),
    ("witty", "시간 가는 줄 모르는 대화",
     "벌써 두 시간이나 지났다니, 말도 안 돼.",
     "저도 시계 보고 놀랐어요. 시간이 이렇게 빠를 줄이야.",
     "시간 가는 줄 모르는 대화. 이런 사람이 오래 가겠지.",
     "시간 잊는 대화 원하면 네이버에 아우라AI데이팅 검색해보세요."),
    # ----------------------------------------------------------------- cool (쿨한 연애)
    ("cool", "서로의 하루를 존중하는 쿨한 연애",
     "연락 안 와도 이상하게 불안하지 않아.",
     "각자 바쁘게 지내고 저녁에 얘기하는 게 좋더라고요.",
     "서로 믿으니까 편안해. 쿨하게 존중하는 연애가 좋아.",
     "쿨한 인연 찾는다면 네이버에 아우라AI데이팅 검색해보세요."),
    ("cool", "각자의 속도로 걷는 두 사람",
     "우리, 서두르지 말고 천천히 가자.",
     "좋아요. 저는 서연 씨 속도에 맞추는 지금이 편해요.",
     "서두르라는 압박이 없으니 마음이 오히려 더 깊어지네.",
     "내 속도에 맞는 사람은 네이버에 아우라AI데이팅 검색해보세요."),
    ("cool", "혼자 쉬는 시간도 존중하는 사람",
     "오늘은 혼자 쉬고 싶은데 괜찮아?",
     "물론이죠. 쉬고 와서 얘기해 주면 그게 더 반가워요.",
     "이해해 주는 사람이 큰 힘이네. 오히려 더 보고 싶어져.",
     "서로 존중하는 인연은 네이버에 아우라AI데이팅 검색해보세요."),
    ("cool", "집착 없이 깊어지는 마음",
     "나 이렇게 편한 연애는 처음이야.",
     "서로 확인 안 해도 마음이 전해지는 게 신기하죠?",
     "숨 막히지 않는 관계라서 매일 더 좋아져. 이게 건강한 거지.",
     "편안한 연애가 궁금하면 네이버에 아우라AI데이팅 검색해보세요."),
    # ----------------------------------------------------------------- direct (직진 고백)
    ("direct", "오늘은 돌려 말하지 않겠습니다",
     "뭔가 할 말 있는 표정인데, 왜 그래?",
     "네, 돌려 말 안 할게요. 서연 씨 좋아하게 된 것 같아요.",
     "갑자기 심장이 뛰었어. 직진하는 사람 앞에선 말문이 막혀.",
     "솔직한 인연 원하면 네이버에 아우라AI데이팅 검색해보세요."),
    ("direct", "조용한 사람의 반전 직진",
     "평소엔 조용하더니, 오늘은 왜 이래?",
     "오늘은 용기 냈어요. 다음 주에도 같이 있고 싶어요.",
     "이런 반전이라니. 조용한 사람의 직진이 이렇게 설렐 줄이야.",
     "반전 매력 궁금하면 네이버에 아우라AI데이팅 검색해보세요."),
    ("direct", "먼저 건넨 한마디의 용기",
     "먼저 연락해도 될까 고민했는데.",
     "저도 같은 생각이었어요. 먼저 말해줘서 정말 고마워요.",
     "용기 내길 잘했어. 한마디 건넸는데 마음이 이렇게 가벼워졌네.",
     "용기 낸 인연이라면 네이버에 아우라AI데이팅 검색해보세요."),
    ("direct", "솔직해지니 쉬워진 마음",
     "나 사실 처음부터 호감 있었어.",
     "저도요. 말은 못 했지만 계속 눈이 가더라고요.",
     "서로 같은 마음이었다니. 솔직하니까 이렇게 쉬운 일이었네.",
     "솔직한 만남 원하면 네이버에 아우라AI데이팅 검색해보세요."),
    # ----------------------------------------------------------------- firsttalk (첫 대화 팁)
    ("firsttalk", "첫 마디 하나가 분위기를 바꾼다",
     "첫 마디, 뭐라고 해야 할지 모르겠어.",
     "가볍게 요즘 즐겨 듣는 노래 얘기로 시작해 보세요.",
     "진짜 그 한마디로 대화가 풀렸어. 어색함이 사라지네.",
     "대화 막막하면 네이버에 아우라AI데이팅 검색해보세요."),
    ("firsttalk", "질문 하나로 이어지는 대화",
     "무슨 얘기를 이어가야 할지 모르겠어.",
     "상대 얘기에 질문 하나만 덧붙이면 대화가 이어져요.",
     "정말 되네. 질문 하나로 대화가 이렇게 풍성해질 줄이야.",
     "대화 팁이 필요하면 네이버에 아우라AI데이팅 검색해보세요."),
    ("firsttalk", "작은 공통점에서 시작하는 대화",
     "공통점이 하나도 없으면 어쩌지?",
     "작은 것부터 찾아보세요. 좋아하는 음식 하나면 충분해요.",
     "음식 얘기로 시작했는데 취향까지 맞더라. 소재가 끝이 없어.",
     "공통점 찾는 법은 네이버에 아우라AI데이팅 검색해보세요."),
    ("firsttalk", "어색한 침묵도 괜찮아",
     "갑자기 말이 뚝 끊겨서 어색한데.",
     "괜찮아요. 웃으며 잠깐 쉬어도 돼요. 침묵도 대화예요.",
     "그 말에 마음이 놓였어. 어색함이 편안함으로 바뀌었지.",
     "편한 첫 만남 원하면 네이버에 아우라AI데이팅 검색해보세요."),
    # ----------------------------------------------------------------- values (가치관 매칭)
    ("values", "돈보다 시간을 같이 쓰는 사람",
     "이 사람, 생각하는 기준이 나랑 같아.",
     "비싼 곳보다 같이 오래 있을 수 있는 곳이 좋아요.",
     "화려함보다 함께하는 시간을 고르는 사람. 이게 가치관이구나.",
     "가치관 맞는 사람은 네이버에 아우라AI데이팅 검색해보세요."),
    ("values", "생활 리듬이 같은 사람",
     "아침형 인간인 사람 처음 봤어.",
     "저도요. 일찍 일어나서 하루를 길게 쓰는 게 좋아요.",
     "생활 리듬이 맞으니 만나는 시간도 편안해. 오래 가겠다.",
     "생활 맞는 인연 궁금하면 네이버에 아우라AI데이팅 검색해보세요."),
    ("values", "돈 쓰는 기준이 닮은 사람",
     "소비 습관이 이렇게 비슷하다고?",
     "필요한 건 좋은 걸로, 나머진 아껴요. 서연 씨도요?",
     "똑같아. 돈 쓰는 기준이 같으면 마음 쓰는 기준도 닮더라.",
     "나와 닮은 사람 찾는다면 네이버에 아우라AI데이팅 검색해보세요."),
    ("values", "같은 미래를 그리는 사람",
     "앞으로 어떻게 살고 싶은지 궁금해.",
     "소박해도 따뜻한 집에서 좋아하는 사람과 저녁 먹고 싶어요.",
     "나도 같은 꿈이야. 화려하지 않아도 함께면 행복할 거야.",
     "같은 꿈 꾸는 사람은 네이버에 아우라AI데이팅 검색해보세요."),
    # ----------------------------------------------------------------- closure (인연 정리)
    ("closure", "미련을 놓으면 설렘이 들어온다",
     "이제 그 사람 생각 안 나더라.",
     "정리된 마음이라니, 정말 멋져요. 앞으로가 기대돼요.",
     "미련을 놓으니까 새로운 설렘이 들어올 자리가 생기더라.",
     "새 출발을 원한다면 네이버에 아우라AI데이팅 검색해보세요."),
    ("closure", "다시 웃게 된 날",
     "오랜만에 이렇게 많이 웃은 것 같아.",
     "웃는 모습이 정말 예뻐요. 오늘 같은 날 또 있었으면 해요.",
     "다시 웃을 수 있다는 게 얼마나 큰 선물인지 이제 알았어.",
     "새로운 설렘 찾는다면 네이버에 아우라AI데이팅 검색해보세요."),
    ("closure", "지난 인연에게 고마운 마음",
     "지난 일은 이제 추억으로 둘래.",
     "아픈 시간도 서연 씨를 단단하게 만들어 준 거예요.",
     "그 시간 덕분에 지금 사람의 소중함을 알아보는 눈이 생겼어.",
     "좋은 인연 이어가려면 네이버에 아우라AI데이팅 검색해보세요."),
    ("closure", "천천히 시작하는 새 인연",
     "새로운 사람을 만나도 괜찮을까?",
     "당연하죠. 마음의 준비가 됐다면 지금이 가장 좋은 때예요.",
     "그 말에 용기가 났어. 천천히 한 걸음씩 나아가 볼게.",
     "새로운 시작이 필요하면 네이버에 아우라AI데이팅 검색해보세요."),
    # ----------------------------------------------------------------- destiny (운명)
    ("destiny", "결국 다시 만날 사람은 만난다",
     "이 사람, 어디서 본 것 같아.",
     "저도요. 처음 보는데 왜 이렇게 익숙한지 모르겠어요.",
     "처음인데 오래된 사람 같아. 이런 게 운명인가 싶었어.",
     "운명 같은 사람 찾는다면 네이버에 아우라AI데이팅 검색해보세요."),
    ("destiny", "우연이 세 번 겹치면 필연",
     "우리, 오늘 벌써 세 번째 마주쳤어.",
     "정말 신기하네요. 이 정도면 우연이 아닌 것 같아요.",
     "우연이 세 번 겹치면 필연이래. 오늘은 그 말 믿어볼래.",
     "필연 같은 인연이라면 네이버에 아우라AI데이팅 검색해보세요."),
    ("destiny", "균형 잡힌 만남이 만든 인연",
     "남녀 비율이 이렇게 딱 반반이라니.",
     "그래서 대화 상대 고르기도 편하고 분위기도 편안해요.",
     "균형 잡힌 만남이라 마음이 한결 편했어. 좋은 사람도 만났고.",
     "균형 잡힌 만남 원하면 네이버에 아우라AI데이팅 검색해보세요."),
    ("destiny", "처음인데 반가운 사람",
     "혹시 우리 예전에 만난 적 있나?",
     "아니요, 오늘이 처음이에요. 그런데 이상하게 반가워요.",
     "나도 그래. 처음인데 반가운 마음이 드는 게 신기하네.",
     "반가운 인연 만나려면 네이버에 아우라AI데이팅 검색해보세요."),
)


def _build_pool() -> List[Dict[str, Any]]:
    """원시 튜플을 director FALLBACK_TEMPLATES 호환 스키마로 변환."""
    pool: List[Dict[str, Any]] = []
    counters: Dict[str, int] = {}
    for genre_id, theme, *speeches in _RAW_POOL:
        if len(speeches) != 4:
            raise ValueError("폴백 풀 항목은 4컷이어야 합니다: %s / %s" % (genre_id, theme))
        counters[genre_id] = counters.get(genre_id, 0) + 1
        cuts = [
            {"role": role, "speaker_gender": gender, "speech": speech}
            for (role, gender), speech in zip(_ROLES, speeches)
        ]
        pool.append({
            "id": "fp_%s_%02d" % (genre_id, counters[genre_id]),
            "genre_id": genre_id,
            "theme": theme,
            "cuts": cuts,
        })
    return pool


_POOL: List[Dict[str, Any]] = _build_pool()


def get_pool() -> List[Dict[str, Any]]:
    """풀 전체의 깊은 복사본을 반환한다. (원본 변조 방지)"""
    return [
        {**t, "cuts": [dict(c) for c in t["cuts"]]}
        for t in _POOL
    ]


def genre_ids() -> List[str]:
    seen: List[str] = []
    for t in _POOL:
        if t["genre_id"] not in seen:
            seen.append(t["genre_id"])
    return seen


def pick_template(
    genre_id: str,
    avoid_ids: Optional[Iterable[str]] = None,
    seed_hex: Optional[str] = None,
) -> Dict[str, Any]:
    """장르 변형 중 avoid_ids 에 없는 것을 sha256 기반으로 결정론 선택한다.

    - unknown genre 는 ValueError.
    - 모든 변형이 avoid 이면 logger.warning 후 전체 후보에서 시드 선택(중단하지 않음).
    """
    candidates = [t for t in _POOL if t["genre_id"] == genre_id]
    if not candidates:
        raise ValueError("알 수 없는 장르 id: %r (허용: %s)" % (genre_id, genre_ids()))

    avoid = set(avoid_ids or ())
    usable = [t for t in candidates if t["id"] not in avoid]
    if not usable:
        logger.warning(
            "[FallbackPool] %s 장르 변형 %d종 전부 최근 사용 -> 시드 기준 재사용",
            genre_id, len(candidates),
        )
        usable = candidates

    digest = hashlib.sha256(("%s|%s" % (genre_id, seed_hex or "")).encode("utf-8")).hexdigest()
    picked = usable[int(digest[:8], 16) % len(usable)]
    return {**picked, "cuts": [dict(c) for c in picked["cuts"]]}


def validate_pool(
    speeds: Tuple[float, ...] = VALIDATION_SPEEDS,
    cps_by_gender: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """풀 전체를 실측 컷 예산으로 검증한다. (절단/보정 없이 위반만 보고)"""
    from modules.drama_engine.drama_cut_budget import CutBudgetValidator

    validator = CutBudgetValidator()
    if cps_by_gender is None:
        calib = validator.calibrate_chars_per_sec()
        cps_by_gender = {"female": calib["female"], "male": calib["male"]}

    violations: List[Dict[str, Any]] = []
    cta_missing: List[str] = []
    gender_errors: List[str] = []
    total_cuts = 0

    for tpl in _POOL:
        cuts = [dict(c, cut_id="cut%d" % (i + 1)) for i, c in enumerate(tpl["cuts"])]
        cta = cuts[3]["speech"]
        for token in REQUIRED_CTA_TOKENS:
            if token not in cta:
                cta_missing.append("%s: '%s' 누락" % (tpl["id"], token))
        if "http" in cta.lower() or "www." in cta.lower():
            cta_missing.append("%s: URL 포함" % tpl["id"])
        for (role, gender), cut in zip(_ROLES, cuts):
            if cut["speaker_gender"] != gender or cut["role"] != role:
                gender_errors.append("%s/%s" % (tpl["id"], cut["cut_id"]))

        for sp in speeds:
            for row in validator.validate_cuts(cuts, cps_by_gender, speed=sp):
                total_cuts += 1
                if not row["ok"]:
                    violations.append({
                        "template": tpl["id"], "speed": sp, "cut_id": row["cut_id"],
                        "chars": row["chars"], "min": row["min"], "max": row["max"],
                        "reason": row["reason"],
                    })

    return {
        "templates": len(_POOL),
        "checked_cuts": total_cuts,
        "violations": violations,
        "cta_missing": cta_missing,
        "gender_errors": gender_errors,
        "speeds": list(speeds),
    }


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(name)s: %(message)s")

    print("=" * 72)
    print("DramaFallbackPool 자체 점검")
    print("=" * 72)
    pool = get_pool()
    print("템플릿 수 :", len(pool))
    by_genre: Dict[str, int] = {}
    for t in pool:
        by_genre[t["genre_id"]] = by_genre.get(t["genre_id"], 0) + 1
    print("장르별    :", by_genre)

    hooks = [t["cuts"][0]["speech"] for t in pool]
    fulls = [" ".join(c["speech"] for c in t["cuts"]) for t in pool]
    themes = [t["theme"] for t in pool]
    print("훅 대사 고유 수   : %d / %d" % (len(set(hooks)), len(pool)))
    print("대본 전문 고유 수 : %d / %d" % (len(set(fulls)), len(pool)))
    print("테마 고유 수      : %d / %d" % (len(set(themes)), len(pool)))

    report = validate_pool()
    print("검증 배속         :", report["speeds"])
    print("검증 컷 수        :", report["checked_cuts"])
    print("예산 위반         :", len(report["violations"]))
    for v in report["violations"]:
        print("   - %(template)s x%(speed)s %(cut_id)s chars=%(chars)s "
              "range=%(min)s~%(max)s | %(reason)s" % v)
    print("CTA 필수어/URL 위반:", len(report["cta_missing"]))
    for m in report["cta_missing"]:
        print("   -", m)
    print("화자/역할 오류    :", len(report["gender_errors"]))

    print("-" * 72)
    print("pick_template 결정론:",
          pick_template("witty", seed_hex="abc")["id"] == pick_template("witty", seed_hex="abc")["id"])
    first = pick_template("witty", seed_hex="abc")["id"]
    print("avoid 적용 후 다른 변형:", pick_template("witty", avoid_ids={first}, seed_hex="abc")["id"] != first)

    bad = len(report["violations"]) + len(report["cta_missing"]) + len(report["gender_errors"])
    print("=" * 72)
    print("결과:", "통과" if bad == 0 else "실패 (%d건)" % bad)
    sys.exit(0 if bad == 0 else 1)
