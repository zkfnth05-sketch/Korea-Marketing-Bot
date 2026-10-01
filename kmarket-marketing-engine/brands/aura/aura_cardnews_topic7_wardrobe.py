# -*- coding: utf-8 -*-
"""
AuraCardnewsTopic7Wardrobe - 👗 [Aura 카드뉴스 7번 주제: 2030 세련된 직장인 10벌 룩북 & 동기화 모듈]
================================================================================================
• 역할:
  - 2030 세련된 직장인 여성(여우상/고양이상 지적 미녀)의 고급스러운 오피스 & 데이트 룩 10벌 정의
  - 카드뉴스 1세트 생성 시 1벌을 선택하여 1번 표지(S1)와 2번 셀카(S2)에 100% 동일한 의상 프롬프트를 자동 주입
  - 매번 생성할 때마다 랜덤 또는 순환 로테이션으로 새로운 착장을 입고 등장하도록 무결성 보장
"""

import random
from typing import Dict, Any, List, Optional

AURA_TOPIC7_WARDROBES: List[Dict[str, Any]] = [
    {
        "id": 1,
        "name_ko": "차콜 슬림 테일러드 수트 & 실크 캐미솔",
        "style_mood": "도회적 지성미 & 스마트 리더형",
        "s1_clothing": "wearing a tailored sharp charcoal grey slim-fit single-breasted blazer over a luxurious ivory silk camisole top, minimal delicate gold pendant necklace, sophisticated urban modern career woman fashion",
        "s2_clothing": "wearing the exact same tailored sharp charcoal grey slim-fit blazer over an ivory silk camisole top with matching tailored charcoal trousers, sleeves slightly pushed up showing slender wrists, sophisticated urban modern career woman fashion"
    },
    {
        "id": 2,
        "name_ko": "크림 아이보리 캐시미어 터틀넥 & 카멜 슬랙스",
        "style_mood": "우아한 올드머니 웜톤 & 고요한 오후의 뮤즈형",
        "s1_clothing": "wearing an ultra-luxurious fine-gauge cream ivory cashmere turtleneck knit sweater hugging her slender neck gracefully, small classic pearl stud earrings, quiet luxury warm-tone old money aesthetic",
        "s2_clothing": "wearing the exact same elegant cream ivory cashmere turtleneck knit sweater paired with high-waisted camel beige tailored wool slacks, quiet luxury old money aesthetic"
    },
    {
        "id": 3,
        "name_ko": "블랙 슬림핏 골지 스퀘어넥 니트 & 골드 포인트",
        "style_mood": "시크하고 매혹적인 미녀 & 고혹적인 고양이상",
        "s1_clothing": "wearing a chic stylish minimalist black ribbed long-sleeve knit top with an elegant square neckline showing delicate collarbones, subtle minimalist gold buttons along the cuffs, modern sophisticated Seoul date-night fashion",
        "s2_clothing": "wearing the exact same chic stylish minimalist black ribbed square-neck long-sleeve knit top paired with black high-waisted slim trousers, modern sophisticated Seoul fashion"
    },
    {
        "id": 4,
        "name_ko": "클래식 네이비 더블 자켓 & 화이트 드레스 셔츠",
        "style_mood": "신뢰감 넘치는 커리어우먼 & 프로페셔널형",
        "s1_clothing": "wearing a structured deep navy double-breasted tailored jacket over an unbuttoned crisp white dress shirt, sharp clean collar, sleek professional modern executive look",
        "s2_clothing": "wearing the exact same structured deep navy double-breasted tailored jacket over a crisp white dress shirt with tailored navy trousers, sleeves neatly rolled to forearms, sleek professional modern executive look"
    },
    {
        "id": 5,
        "name_ko": "오트밀 크림 노카라 트위드 자켓 & 실크 탑",
        "style_mood": "페미닌 럭셔리 룩 & 단아한 부잣집 딸형",
        "s1_clothing": "wearing a luxurious oatmeal cream collarless tweed jacket with subtle delicate golden metallic thread weave and pearl buttons over a fine cream silk inner top, feminine high-end quiet luxury look",
        "s2_clothing": "wearing the exact same luxurious oatmeal cream collarless tweed jacket over a cream silk top with ivory straight-fit tailored trousers, feminine high-end quiet luxury aesthetic"
    },
    {
        "id": 6,
        "name_ko": "더스티 로즈 실키 랩 블라우스",
        "style_mood": "부드럽고 로맨틱한 무드 & 데이트/소개팅 최적화형",
        "s1_clothing": "wearing an elegant fluid dusty rose pink silky satin wrap blouse with a soft V-neckline draping naturally, rose gold delicate chain necklace, romantic sophisticated office-to-date look",
        "s2_clothing": "wearing the exact same fluid dusty rose pink silky wrap blouse tucked into high-waisted taupe grey tailored slacks, romantic sophisticated look"
    },
    {
        "id": 7,
        "name_ko": "딥 버건디 와인 모크넥 슬림 니트",
        "style_mood": "성숙하고 깊은 분위기 & 가을/겨울 감성 매혹형",
        "s1_clothing": "wearing a rich deep burgundy wine-colored fine ribbed mock-neck knit sweater, subtle rose gold watch on wrist, alluring deep autumnal mood",
        "s2_clothing": "wearing the exact same rich deep burgundy wine mock-neck knit sweater with tailored charcoal high-waisted pants, alluring sophisticated look"
    },
    {
        "id": 8,
        "name_ko": "스카이 블루 핀스트라이프 슬림 셔츠",
        "style_mood": "청순 스마트 오피스룩 & 맑고 청량한 지적형",
        "s1_clothing": "wearing a crisp tailored light sky blue pinstripe cotton shirt with the top two buttons casually open, neat modern collar, smart clean contemporary aesthetic",
        "s2_clothing": "wearing the exact same light sky blue pinstripe cotton shirt with sleeves casually rolled up to forearms, tucked into deep navy tailored trousers, smart clean contemporary look"
    },
    {
        "id": 9,
        "name_ko": "모카 브라운 셔링 실크 블라우스",
        "style_mood": "감각적인 컨템포러리 룩 & 감성 카페 탐방형",
        "s1_clothing": "wearing a luxurious glossy mocha brown shirred silk blouse with elegant gathered neckline detail, delicate dangling earrings, warm ambient cafe mood",
        "s2_clothing": "wearing the exact same glossy mocha brown shirred silk blouse tucked into chocolate brown tailored trousers, warm chic contemporary look"
    },
    {
        "id": 10,
        "name_ko": "세이지 그린 니트 가디건 셋업",
        "style_mood": "자연스럽고 편안한 센스룩 & 상큼한 비타민 과즙형",
        "s1_clothing": "wearing a trendy muted sage green fine-knit sleeveless top with a matching soft cardigan draped effortlessly over her shoulders, minimalist silver necklace, fresh trendy 2030 Seoul office look",
        "s2_clothing": "wearing the exact same muted sage green knit top and draped shoulder cardigan set paired with cream tailored wide-leg trousers, fresh trendy look"
    }
]


def get_wardrobe(outfit_id: Optional[int] = None) -> Dict[str, Any]:
    """
    지정된 ID 또는 무작위로 10벌 중 1벌의 룩을 반환합니다.
    - outfit_id: 1~10 사이 정수 (None일 경우 무작위 선택)
    """
    if outfit_id is not None and 1 <= outfit_id <= len(AURA_TOPIC7_WARDROBES):
        return AURA_TOPIC7_WARDROBES[outfit_id - 1]
    return random.choice(AURA_TOPIC7_WARDROBES)


def get_all_wardrobes() -> List[Dict[str, Any]]:
    """10벌의 전체 룩북 리스트를 반환합니다."""
    return AURA_TOPIC7_WARDROBES
