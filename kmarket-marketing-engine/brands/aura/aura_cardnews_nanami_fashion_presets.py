# -*- coding: utf-8 -*-
"""
AuraCardnewsNanamiFashionPresets - 👗 [Aura 카드뉴스 2번 주제 나나미 전용 10대 도쿄 여친 룩 프리셋]
=============================================================================================
• 역할:
  - 2번 주제("실시간 AI 자막 통화")의 주인공 '나나미(Nanami, 24세 일본인)'의 
    얼굴, 헤어스타일(시스루 뱅, 다크브라운 중단발), 도쿄 서재 거실 배경은 100% 영구 고정(Anchor)
  - 1번(설렘), 2번(곤란 갸우뚱), 3번(활짝 웃음), 4번(영상통화 캡처)에
    10종의 사랑스러운 '도쿄 여친 라이프스타일 룩(モテコーデ)'을 100% 동일하게 일관 주입
  - 카드뉴스 생성 시 `--fashion 1~10`으로 지정하거나 자동 순환하여 콘텐츠 다양성 극대화
"""

import random
from typing import Dict, Any, List, Optional, Tuple

NANAMI_FASHION_PRESETS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "name_ko": "화이트 골지 터틀넥 니트 (클래식 도쿄 미니멀)",
        "vibe": "단아하고 청순하며 깔끔한 도쿄 홈 데이팅 룩",
        "outfit_prompt": (
            "wearing the exact same clean stylish civilian casual clothes, a neat comfortable white fine-gauge ribbed turtleneck knit sweater"
        ),
        "scene_detail": "따뜻하고 포근한 저녁, 아늑한 서재 거실에서 설레는 첫 통화"
    },
    {
        "id": 2,
        "name_ko": "소프트 핑크 모헤어 가디건 (딸기우유 심쿵 룩)",
        "vibe": "보호본능을 자극하는 사랑스럽고 따뜻한 여친 룩",
        "outfit_prompt": (
            "wearing the exact same clean stylish civilian casual clothes, a cozy oversized pastel baby-pink fluffy mohair knit cardigan with subtle pearl buttons, layered gently over a simple white cotton camisole"
        ),
        "scene_detail": "샤워 후 포근한 소파에서 편안하게 이어지는 밤샘 통화"
    },
    {
        "id": 3,
        "name_ko": "오버핏 네이비 스웻셔츠 (도쿄 캠퍼스 여사친 룩)",
        "vibe": "편안하면서도 센스 넘치는 내추럴 시크",
        "outfit_prompt": (
            "wearing the exact same clean stylish civilian casual clothes, a relaxed comfortable deep navy blue oversized cotton crewneck sweatshirt with a layered crisp white inner tee collar peek"
        ),
        "scene_detail": "주말 오후 소파에 기대어 장난스럽게 웃으며 대화하는 무드"
    },
    {
        "id": 4,
        "name_ko": "베이지 루즈핏 린넨 셔츠 (다이칸야마 카페 감성)",
        "vibe": "자연스럽고 세련된 꾸안꾸 프렌치-재패니즈 룩",
        "outfit_prompt": (
            "wearing the exact same clean stylish civilian casual clothes, a chic relaxed-fit warm oatmeal beige button-down cotton-linen shirt with rolled-up cuffs and an open collar"
        ),
        "scene_detail": "외출 전 햇살 비치는 창가에서 가볍게 통화하는 도쿄 감성"
    },
    {
        "id": 5,
        "name_ko": "세이지 그린 케이블 니트 (힐링 내추럴 룩)",
        "vibe": "마음이 편안해지는 따스하고 부드러운 그린 톤",
        "outfit_prompt": (
            "wearing the exact same clean stylish civilian casual clothes, a cozy textured sage-mint green thick cable-knit crewneck woolen sweater with soft tactile ribbed hem"
        ),
        "scene_detail": "비 오는 날 따뜻한 차 한 잔 마시며 소소한 일상을 공유하는 힐링 통화"
    },
    {
        "id": 6,
        "name_ko": "스퀘어넥 플로럴 블라우스 (로맨틱 데이트 룩)",
        "vibe": "쇄골 라인이 돋보이는 화사하고 여성스러운 무드",
        "outfit_prompt": (
            "wearing the exact same clean stylish civilian casual clothes, an elegant flattering square-neckline long-sleeve chiffon blouse with subtle micro French vintage wildflower print on cream background"
        ),
        "scene_detail": "친구들과 브런치 모임 다녀와서 기분 좋게 랜선 데이트하는 순간"
    },
    {
        "id": 7,
        "name_ko": "헤더 그레이 크롭 후디 셋업 (트렌디 스트릿 홈웨어)",
        "vibe": "힙하고 트렌디하면서도 편안한 20대 일상 룩",
        "outfit_prompt": (
            "wearing the exact same clean stylish civilian casual clothes, a trendy relaxed heather-gray zip-up crop hoodie jacket layered over a minimalist white rib-knit tank top"
        ),
        "scene_detail": "밤늦은 시간 침대 위에서 엎드려 폰 화면을 들여다보는 귀여운 무드"
    },
    {
        "id": 8,
        "name_ko": "모카 라떼 브이넥 니트 (성숙한 도쿄 오피스걸 룩)",
        "vibe": "지적이고 성숙하며 우아한 저녁 무드",
        "outfit_prompt": (
            "wearing the exact same clean stylish civilian casual clothes, a warm sophisticated mocha brown soft merino wool modest V-neck knit sweater, accented with a tiny delicate minimalist pearl pendant necklace"
        ),
        "scene_detail": "퇴근 후 집에서 편안하게 풀린 표정으로 소통하는 설레는 어른의 썸"
    },
    {
        "id": 9,
        "name_ko": "라이트 라벤더 드레이프 셔츠 (은은한 파스텔 시크)",
        "vibe": "도회적이고 단아하며 맑은 분위기",
        "outfit_prompt": (
            "wearing the exact same clean stylish civilian casual clothes, a refined lustrous soft pastel lavender silk drape-collar blouse with clean flowing lines"
        ),
        "scene_detail": "금요일 저녁 다음 만남 일정을 잡으며 미소 짓는 설렘 가득한 순간"
    },
    {
        "id": 10,
        "name_ko": "크림 보아 플리스 집업 (포근한 겨울 뽀글이 룩)",
        "vibe": "극강의 포근함과 귀여움, 한겨울 랜선 썸의 정석",
        "outfit_prompt": (
            "wearing the exact same clean stylish civilian casual clothes, an adorable warm cream ivory fluffy sherpa boa fleece zip-up jacket with light camel brown piping details"
        ),
        "scene_detail": "추운 겨울밤 따뜻한 방 안에서 시간 가는 줄 모르는 3시간 랜선 통화"
    }
]


class AuraCardnewsNanamiFashionPresets:
    """나나미(Nanami) 전용 10대 도쿄 착장 관리 매니저"""

    @classmethod
    def get_preset(cls, preset_id: Optional[int] = None) -> Dict[str, Any]:
        """착장 ID로 프리셋 조회 (없거나 범위 밖이면 1번 기본 반환)"""
        if preset_id is not None:
            for p in NANAMI_FASHION_PRESETS:
                if p["id"] == preset_id:
                    return p
        return NANAMI_FASHION_PRESETS[0]

    @classmethod
    def get_random_preset(cls) -> Dict[str, Any]:
        """10종 중 무작위 착장 1종 추첨 (무인 자율 구동 시 다양성 확보)"""
        return random.choice(NANAMI_FASHION_PRESETS)

    @classmethod
    def get_all_presets(cls) -> List[Dict[str, Any]]:
        """전체 10종 프리셋 목록 반환"""
        return NANAMI_FASHION_PRESETS

    @classmethod
    def apply_fashion_to_prompt(cls, raw_prompt: str, preset: Dict[str, Any]) -> str:
        """
        원천 이미지 프롬프트 내의 기본 의상 문구를 선택된 착장 프리셋으로 완벽 치환
        기본 치환 대상:
        'wearing the exact same clean stylish civilian casual clothes, a neat comfortable white turtleneck knit sweater from slide 1'
        등의 패턴을 프리셋의 outfit_prompt로 1:1 교체
        """
        outfit_replacement = preset["outfit_prompt"]
        
        # 패턴 1: 기본 터틀넥 문구 교체
        import re
        pattern = r"wearing the exact same clean stylish civilian casual clothes, a neat comfortable white turtleneck knit sweater[^\,]*"
        if re.search(pattern, raw_prompt):
            return re.sub(pattern, outfit_replacement, raw_prompt)
        
        # 패턴 2: 단독 터틀넥 문구 교체
        pattern2 = r"wearing [^\,]*white [^\,]*turtleneck[^\,]*sweater"
        if re.search(pattern2, raw_prompt):
            return re.sub(pattern2, outfit_replacement, raw_prompt)

        return raw_prompt
