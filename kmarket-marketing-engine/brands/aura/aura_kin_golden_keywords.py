# -*- coding: utf-8 -*-
"""
Aura Kin Golden Keywords (💖 Aura 전용 지식iN 실시간 고유입 골든 키워드 컬렉션)
==================================================================================
- 브랜드: Aura (2030 AI 데이팅 & 서울 핫플 매칭)
- 설계 원칙:
  1. 🚫 질문 없는 장문 롱테일 문장 배제 ("소개팅 실패 안하는법" 등 X)
  2. 🎯 네이버 지식iN에서 매일 수십~수백 건의 신규 질문이 폭발하는 핵심 유입 키워드(High-Volume Keywords) 선별
  3. 📂 3대 핵심 카테고리 구성:
     - A. 소개팅 & 데이팅앱/플랫폼 (직접적 타겟 유저)
     - B. 연애 고민 & 썸 심리 (잠재적 데이팅 유저)
     - C. 데이트 코스 & 만남/인연 (핫플 및 매칭 니즈)
"""

from typing import List, Dict, Any

AURA_GOLDEN_KEYWORD_GROUPS: Dict[str, List[str]] = {
    # 📱 1그룹: 소개팅 & 소개팅 어플/플랫폼 (Aura 서비스 직접 매칭 타겟)
    "dating_apps_and_blind_dates": [
        "소개팅 어플 추천",
        "소개팅앱 추천",
        "소개팅 어플",
        "소개팅앱",
        "데이팅앱 추천",
        "데이팅 어플",
        "소개팅앱 후기",
        "직장인 소개팅 어플",
        "20대 소개팅 어플",
        "소개팅 첫만남",
        "소개팅 대화",
        "소개팅 애프터",
        "소개팅 연락",
        "소개팅 장소",
        "소개팅 옷",
        "소개팅 매너",
        "소개팅 고민",
        "소개팅 주선",
        "직장인 소개팅",
        "대학생 소개팅",
    ],
    # 💬 2그룹: 연애 고민 & 썸 심리 & 연락 텀 (연애 니즈 고관여층)
    "dating_concerns_and_chemistry": [
        "연애 고민",
        "연애 상담",
        "썸남 심리",
        "썸녀 심리",
        "썸남 연락",
        "썸녀 연락",
        "고백 타이밍",
        "짝사랑 포기",
        "연애 시작",
        "이성 호감 신호",
        "카톡 연락 텀",
        "첫만남 대화",
        "애프터 신청",
        "남친 고민",
        "여친 고민",
        "연애 잘하는법",
        "모태솔로 탈출",
        "이상형 만나는법",
    ],
    # ☕ 3그룹: 데이트 코스 & 만남/인연 플랫폼 (자만추/성수/홍대 핫플)
    "hotplaces_and_matchmaking": [
        "데이트 코스",
        "첫 데이트 장소",
        "서울 데이트 코스",
        "홍대 데이트 맛집",
        "강남 소개팅 맛집",
        "성수 데이트 코스",
        "조용한 소개팅 카페",
        "결정사 후기",
        "결혼정보회사 추천",
        "진지한 만남",
        "솔로 탈출",
        "인연 찾기",
        "자만추 방법",
        "새로운 만남",
    ]
}


def get_aura_golden_keywords() -> List[str]:
    """네이버 지식iN 실시간 신규 질문이 풍부한 골든 키워드 전수 반환 (총 52개)"""
    keywords: List[str] = []
    for group in AURA_GOLDEN_KEYWORD_GROUPS.values():
        for kw in group:
            if kw not in keywords:
                keywords.append(kw)
    return keywords


if __name__ == "__main__":
    kws = get_aura_golden_keywords()
    print(f"Total Aura Golden Keywords: {len(kws)}")
    print("Sample:", kws[:10])
