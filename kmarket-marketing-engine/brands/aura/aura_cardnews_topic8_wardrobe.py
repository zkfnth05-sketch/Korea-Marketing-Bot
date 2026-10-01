# -*- coding: utf-8 -*-
"""
AuraCardnewsTopic8Wardrobe - 👗 [Aura 카드뉴스 8번 주제: 2030 동네 번개 & 성수동 OOTD 10벌 룩북]
===================================================================================================
• 역할:
  - 8번 주제('500m 안심 레이더 & 안심 번개 퀘스트')의 특성에 맞춘 10벌의 트렌디 룩 정의
  - 구성: [트렌디 애슬레저 & 레깅스 룩 5벌] + [성수동 테라스 데일리 & 와인 룩 5벌]
  - 1회 카드뉴스 세트 생성 시 1벌을 선정하여 1번 표지(S1)와 2번 슬라이드(S2)에 100% 동일 의상 프롬프트 주입
  - 매일 봇 자율 가동 시 10벌 로테이션으로 피드의 무한한 신선함과 완벽한 인물 일관성 보장
"""

import random
from typing import Dict, Any, List, Optional

AURA_TOPIC8_WARDROBES: List[Dict[str, Any]] = [
    # 🏃‍♀️ [Group A: 트렌디 애슬레저 & 레깅스 룩 5벌]
    {
        "id": 1,
        "category": "애슬레저 & 레깅스",
        "name_ko": "화이트 윈드브레이커 & 딥블랙 하이웨이스트 레깅스",
        "style_mood": "시그니처 고프코어 & 성수동 테라스 애슬레저",
        "s1_clothing": "wearing a stylish crisp white minimalist gorpcore hooded windbreaker jacket slightly unzipped at collar over a beige ribbed inner top, paired with premium matte black high-waisted seamless athletic yoga leggings, sporty sleek modern Seoul street fashion",
        "s2_clothing": "wearing the exact same stylish crisp white minimalist gorpcore hooded windbreaker jacket slightly unzipped over a beige ribbed inner top with premium matte black high-waisted athletic yoga leggings, holding a black smartphone, sporty sleek modern Seoul street fashion"
    },
    {
        "id": 2,
        "category": "애슬레저 & 레깅스",
        "name_ko": "세이지 그린 크롭 아노락 & 차콜 슬림 레깅스",
        "style_mood": "한강·서울숲 감성 러닝 & 상큼한 스포티룩",
        "s1_clothing": "wearing a trendy muted sage green lightweight crop pullover anorak hoodie with half-zip detail over a white sports bra top, paired with charcoal grey high-waisted compression athletic leggings, clean fresh athletic Seoul lifestyle",
        "s2_clothing": "wearing the exact same muted sage green crop anorak hoodie with half-zip detail and charcoal grey high-waisted compression athletic leggings, holding a smartphone looking down at the screen, clean fresh athletic Seoul lifestyle"
    },
    {
        "id": 3,
        "category": "애슬레저 & 레깅스",
        "name_ko": "라이트 그레이 하프집업 & 딥네이비 레깅스",
        "style_mood": "깔끔하고 건강미 넘치는 데일리 산책룩",
        "s1_clothing": "wearing a sleek light heather grey slim-fit athletic half-zip sweatshirt with collar standing neatly, paired with deep midnight navy high-waisted sculpted yoga leggings, minimalist clean modern athleisure",
        "s2_clothing": "wearing the exact same light heather grey slim-fit half-zip sweatshirt and deep midnight navy high-waisted yoga leggings, holding a modern smartphone at chest level, minimalist clean modern athleisure"
    },
    {
        "id": 4,
        "category": "애슬레저 & 레깅스",
        "name_ko": "크림 오버핏 패딩 조끼 & 딥블랙 레깅스",
        "style_mood": "힙한 스트릿 애슬레저 & 테라스 브런치",
        "s1_clothing": "wearing a trendy matte cream ivory oversized padded vest over a long-sleeve black tight-fitting crop top, paired with jet-black high-rise seamless yoga leggings, trendy Seongsu-dong street athleisure",
        "s2_clothing": "wearing the exact same matte cream ivory oversized padded vest over a black tight-fitting top with jet-black high-rise yoga leggings, holding her smartphone and checking the screen, trendy Seongsu-dong street athleisure"
    },
    {
        "id": 5,
        "category": "애슬레저 & 레깅스",
        "name_ko": "파스텔 핑크 크롭 가디건 & 크림 아이보리 레깅스",
        "style_mood": "화사하고 사랑스러운 페미닌 스포티룩",
        "s1_clothing": "wearing a delicate soft pastel baby pink fine-ribbed cropped zip-up cardigan over a white athletic tank top, paired with warm cream ivory high-waisted seamless leggings, feminine soft sporty aesthetic",
        "s2_clothing": "wearing the exact same soft pastel baby pink cropped zip-up cardigan and warm cream ivory high-waisted leggings, holding her smartphone, feminine soft sporty aesthetic"
    },

    # ☕🍷 [Group B: 성수동 감성 일상 & 테라스 와인 룩 5벌]
    {
        "id": 6,
        "category": "성수동 일상 & 테라스",
        "name_ko": "오버핏 스트라이프 셔츠 & 슬림 데님 팬츠",
        "style_mood": "꾸안꾸 성수동 베이커리 카페 데이트",
        "s1_clothing": "wearing a crisp oversized light sky-blue and white pinstripe cotton boyfriend shirt with top buttons casually unbuttoned and sleeves rolled to forearms, paired with slim-fit medium-wash blue denim jeans, effortless chic Parisian-Seoul cafe look",
        "s2_clothing": "wearing the exact same oversized light sky-blue pinstripe cotton shirt and slim-fit blue denim jeans, sleeves casually rolled up, holding a smartphone, effortless chic Parisian-Seoul cafe look"
    },
    {
        "id": 7,
        "category": "성수동 일상 & 테라스",
        "name_ko": "블랙 슬림핏 골지 니트 & 차콜 핀턱 슬랙스",
        "style_mood": "퇴근 후 분위기 좋은 성수동 와인바 룩",
        "s1_clothing": "wearing an alluring slim-fit black fine-ribbed knit sweater with a flattering soft sweetheart neckline showing elegant collarbones, paired with high-waisted charcoal tailored wide-leg trousers, sophisticated night-out wine bar fashion",
        "s2_clothing": "wearing the exact same slim-fit black ribbed sweetheart neckline knit sweater and charcoal high-waisted wide trousers, holding a smartphone in both hands looking at it, sophisticated night-out wine bar fashion"
    },
    {
        "id": 8,
        "category": "성수동 일상 & 테라스",
        "name_ko": "크림 트위드 크롭 자켓 & 연청 데님",
        "style_mood": "세련된 2030 주말 저녁 브런치 & 번개",
        "s1_clothing": "wearing a chic cropped cream oatmeal tweed jacket with subtle pearl buttons over a simple white silk camisole top, paired with light-wash high-waisted straight denim jeans, modern sophisticated trendy Seoul date style",
        "s2_clothing": "wearing the exact same cropped cream tweed jacket over white silk camisole with light-wash straight denim jeans, holding a sleek smartphone, modern sophisticated trendy Seoul date style"
    },
    {
        "id": 9,
        "category": "성수동 일상 & 테라스",
        "name_ko": "파우더 블루 스퀘어넥 티 & 블랙 미디 스커트",
        "style_mood": "여성스럽고 설레는 첫 만남 데이트룩",
        "s1_clothing": "wearing a soft pastel powder-blue fitted square-neck long-sleeve top highlighting elegant neckline, paired with a sleek black high-waisted A-line midi skirt, graceful charming feminine cafe date aesthetic",
        "s2_clothing": "wearing the exact same soft powder-blue fitted square-neck long-sleeve top and black high-waisted midi skirt, checking notifications on her smartphone, graceful charming feminine cafe date aesthetic"
    },
    {
        "id": 10,
        "category": "성수동 일상 & 테라스",
        "name_ko": "오버핏 빈티지 레더 자켓 & 화이트 티 + 스트레이트 진",
        "style_mood": "힙하고 트렌디한 성수동 골목 감성 펍 & 맛집",
        "s1_clothing": "wearing an edgy oversized vintage washed black vegan leather jacket over a clean fitted white cotton crewneck t-shirt, paired with classic straight-leg blue denim jeans, trendy cool Seongsu hip street vibe",
        "s2_clothing": "wearing the exact same oversized vintage black leather jacket over a white cotton t-shirt with classic blue denim jeans, holding a smartphone with focused gentle smile, trendy cool Seongsu hip street vibe"
    }
]


def get_wardrobe(outfit_id: Optional[int] = None) -> Dict[str, Any]:
    """
    지정된 ID 또는 무작위로 10벌 중 1벌의 룩을 반환합니다.
    - outfit_id: 1~10 사이 정수 (None일 경우 무작위 선택)
    """
    if outfit_id is not None and 1 <= outfit_id <= len(AURA_TOPIC8_WARDROBES):
        return AURA_TOPIC8_WARDROBES[outfit_id - 1]
    return random.choice(AURA_TOPIC8_WARDROBES)


def get_all_wardrobes() -> List[Dict[str, Any]]:
    """10벌의 전체 룩북 리스트를 반환합니다."""
    return AURA_TOPIC8_WARDROBES
