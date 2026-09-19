"""
💖 Aura 2030 데이팅 100대 마스터 블로그 주제 데이터베이스 (Aura100Topics)
==========================================================================
- 6대 핵심 카테고리 매트릭스에 100% 매핑된 고품질 기획 주제 풀
- 각 주제별: 고유 ID, 카테고리, 제목, 타깃 오디언스, 핵심 의도, 연동될 Aura 기능
"""

from typing import Dict, List, Any


AURA_100_TOPICS: List[Dict[str, Any]] = [
    # =========================================================================
    # [카테고리 1] kakaotalk_signals (카톡 밀당 & 시그널 해석 - 18개 주제)
    # =========================================================================
    {
        "id": 1,
        "category": "kakaotalk_signals",
        "title": "소개팅 첫 카톡 읽씹을 피하는 호감형 첫인사 멘트 5가지",
        "intent": "첫 카톡 어색함 극복 및 자연스러운 핑퐁 시작",
        "aura_feature": "Aura AI 카톡 답장 코칭"
    },
    {
        "id": 2,
        "category": "kakaotalk_signals",
        "title": "소개팅 후 카톡 답장 텀 1시간의 진짜 심리 분석",
        "intent": "답장 간격에 따른 상대방의 속마음 및 호감도 판별",
        "aura_feature": "Aura AI 카톡 템포 분석기"
    },
    {
        "id": 3,
        "category": "kakaotalk_signals",
        "title": "소개팅 당일 밤 선톡, 남자가 먼저? 여자가 먼저?",
        "intent": "귀가 후 첫 연락의 타이밍과 이상적인 멘트 가이드",
        "aura_feature": "Aura AI 선톡 타이밍 추천"
    },
    {
        "id": 4,
        "category": "kakaotalk_signals",
        "title": "읽씹 vs 안읽씹, 상대방의 속마음과 대처법",
        "intent": "읽씹/안읽씹 상황에서의 멘탈 관리 및 재연락 전략",
        "aura_feature": "Aura AI 읽씹 복구 가이드"
    },
    {
        "id": 5,
        "category": "kakaotalk_signals",
        "title": "단답형 카톡을 자연스럽게 살려내는 티키타카 심폐소생술",
        "intent": "단답으로 일관하는 대화에 활기를 불어넣는 질문법",
        "aura_feature": "Aura AI 티키타카 질문 생성기"
    },
    {
        "id": 6,
        "category": "kakaotalk_signals",
        "title": "소개팅 애프터 거절 시그널을 부드럽게 돌려말하는 법",
        "intent": "예의를 지키며 완곡하게 거절하는 센스 있는 멘트",
        "aura_feature": "Aura AI 매너 거절 가이드"
    },
    {
        "id": 7,
        "category": "kakaotalk_signals",
        "title": "호감 있는 사람에게만 나오는 무의식적 카톡 말투 특징",
        "intent": "상대방의 카톡 말투에서 포착하는 긍정 시그널 5가지",
        "aura_feature": "Aura AI 호감도 점수 리포트"
    },
    {
        "id": 8,
        "category": "kakaotalk_signals",
        "title": "카톡 이모티콘 사용 빈도로 알아보는 상대방의 호감도",
        "intent": "이모티콘, 물결표(~), ㅋㅋㅋ 빈도로 심리 분석",
        "aura_feature": "Aura AI 감정 분석 리포트"
    },
    {
        "id": 9,
        "category": "kakaotalk_signals",
        "title": "소개팅 전날 카톡 대화, 어디까지 나누는 게 좋을까?",
        "intent": "만나기 전 과도한 카톡으로 인한 기대감 방지 요령",
        "aura_feature": "Aura AI 만남 전 가이드"
    },
    {
        "id": 10,
        "category": "kakaotalk_signals",
        "title": "소개팅 카톡에서 절대 쓰면 안 되는 비호감 말투 BEST 3",
        "intent": "상대방의 정을 떨어뜨리는 무례하거나 어색한 어투 경고",
        "aura_feature": "Aura AI 말투 교정기"
    },
    {
        "id": 11,
        "category": "kakaotalk_signals",
        "title": "카톡 프로필 사진과 상태메시지로 파악하는 상대방 성향",
        "intent": "프사와 상메로 취향과 성격을 읽어내는 사전 팁",
        "aura_feature": "Aura AI 프로필 성향 진단"
    },
    {
        "id": 12,
        "category": "kakaotalk_signals",
        "title": "주말 약속 잡을 때 거절당하지 않는 자연스러운 카톡 빌드업",
        "intent": "음식/장소 화제로 시작해 약속으로 이어지는 대화 흐름",
        "aura_feature": "Aura AI 데이트 빌드업 챗봇"
    },
    {
        "id": 13,
        "category": "kakaotalk_signals",
        "title": "대화가 끊겼을 때 3일 뒤 다시 선톡 보내는 꿀팁",
        "intent": "어색하지 않게 자연스러운 명분으로 대화 재개하는 법",
        "aura_feature": "Aura AI 재연락 멘트 생성"
    },
    {
        "id": 14,
        "category": "kakaotalk_signals",
        "title": "상대방이 카톡 답장을 늦게 할 때 멘탈 관리하는 법",
        "intent": "답장 집착을 줄이고 매력적인 여유를 유지하는 심리 팁",
        "aura_feature": "Aura AI 멘탈 코칭"
    },
    {
        "id": 15,
        "category": "kakaotalk_signals",
        "title": "카톡 밀당의 기술: 적절한 핑퐁 템포 유지법",
        "intent": "과도한 밀당 없이 서로 기분 좋은 템포 맞추기",
        "aura_feature": "Aura AI 밀당 템포 가이드"
    },
    {
        "id": 16,
        "category": "kakaotalk_signals",
        "title": "썸 타는 사이에서 '잘 자' 카톡이 가지는 의미와 타이밍",
        "intent": "하루를 마무리하는 감성 멘트의 적절한 활용법",
        "aura_feature": "Aura AI 감성 카톡 코칭"
    },
    {
        "id": 17,
        "category": "kakaotalk_signals",
        "title": "상대방의 질문 없는 일방적 대화, 계속 이어가야 할까?",
        "intent": "나만 질문하는 관계에서의 손절 타이밍과 대처법",
        "aura_feature": "Aura AI 관계 진단 리포트"
    },
    {
        "id": 18,
        "category": "kakaotalk_signals",
        "title": "AI가 분석한 소개팅 성공률 90% 카톡 대화 패턴 3가지",
        "intent": "빅데이터 기반 호감 상승 대화 패턴 공개",
        "aura_feature": "Aura AI 카톡 성공 패턴 분석"
    },

    # =========================================================================
    # [카테고리 2] date_spots (실전 소개팅 핫플 & 데이트 코스 - 18개 주제)
    # =========================================================================
    {
        "id": 19,
        "category": "date_spots",
        "title": "연남동 조용한 소개팅 와인바 BEST 5 및 예약 꿀팁",
        "intent": "분위기와 대화하기 좋은 연남동 와인 명소 큐레이션",
        "aura_feature": "Aura 주말 AI 데이트 코스 큐레이션"
    },
    {
        "id": 20,
        "category": "date_spots",
        "title": "성수동 첫 만남 어색함 없는 분위기 좋은 룸식당 추천",
        "intent": "소음 없이 프라이빗하게 대화 나누는 성수동 맛집",
        "aura_feature": "Aura AI 맛집 코스 큐레이션"
    },
    {
        "id": 21,
        "category": "date_spots",
        "title": "강남역/신논현역 대화하기 편한 조용한 카페 5곳",
        "intent": "복잡한 강남역에서 테이블 간격 넓고 조용한 카페 엄선",
        "aura_feature": "Aura AI 카페 큐레이션"
    },
    {
        "id": 22,
        "category": "date_spots",
        "title": "소개팅 2차로 가기 딱 좋은 분위기 있는 감성 펍/바",
        "intent": "1차 식사 후 가볍게 한잔하며 호감도 높이는 2차 장소",
        "aura_feature": "Aura 2차 스팟 추천"
    },
    {
        "id": 23,
        "category": "date_spots",
        "title": "비 오는 날 로맨틱한 서울 실내 데이트 코스 BEST 4",
        "intent": "날씨에 구애받지 않고 아늑하게 즐기는 실내 코스",
        "aura_feature": "Aura 실내 데이트 가이드"
    },
    {
        "id": 24,
        "category": "date_spots",
        "title": "한남동/이태원 실패 없는 소개팅 맛집 & 산책 코스",
        "intent": "세련된 다이닝과 트렌디한 골목 산책의 조화",
        "aura_feature": "Aura 한남 데이트 맵"
    },
    {
        "id": 25,
        "category": "date_spots",
        "title": "을지로 힙지로 감성 가득한 이색 소개팅 장소 추천",
        "intent": "레트로하고 특별한 분위기를 선호하는 2030 맞춤 장소",
        "aura_feature": "Aura 이색 데이트 코스"
    },
    {
        "id": 26,
        "category": "date_spots",
        "title": "송리단길/잠실 석촌호수 소개팅 데이트 코스 완벽 정리",
        "intent": "식사 후 호수 산책으로 이어지는 클래식 성공 코스",
        "aura_feature": "Aura 잠실 데이트 가이드"
    },
    {
        "id": 27,
        "category": "date_spots",
        "title": "판교/분당 직장인 평일 저녁 소개팅 추천 스팟",
        "intent": "퇴근 후 깔끔하고 여유롭게 만나는 IT 직장인 코스",
        "aura_feature": "Aura 평일 저녁 코스 추천"
    },
    {
        "id": 28,
        "category": "date_spots",
        "title": "홍대/상수 트렌디한 퓨전 한식 소개팅 다이닝 4선",
        "intent": "부담 없는 가격과 훌륭한 비주얼의 한식 다이닝",
        "aura_feature": "Aura 다이닝 큐레이션"
    },
    {
        "id": 29,
        "category": "date_spots",
        "title": "도산공원/압구정로데오 고급스러운 첫 만남 레스토랑",
        "intent": "격식 있고 세련된 첫인상을 남기는 압구정 명소",
        "aura_feature": "Aura 프리미엄 코스 추천"
    },
    {
        "id": 30,
        "category": "date_spots",
        "title": "주말 낮 소개팅을 위한 서울 브런치 카페 추천",
        "intent": "햇살 가득하고 산뜻한 낮 소개팅 브런치 스팟",
        "aura_feature": "Aura 낮 브런치 코스"
    },
    {
        "id": 31,
        "category": "date_spots",
        "title": "북촌/서촌 고즈넉한 한옥 카페와 골목 산책 데이트",
        "intent": "차분하고 깊이 있는 대화를 원하는 소개팅 코스",
        "aura_feature": "Aura 서촌 감성 코스"
    },
    {
        "id": 32,
        "category": "date_spots",
        "title": "소개팅 장소 고를 때 테이블 간격과 소음 체크하는 노하우",
        "intent": "분위기는 좋으나 시끄러워 망하는 소개팅 예방법",
        "aura_feature": "Aura 장소 체크리스트"
    },
    {
        "id": 33,
        "category": "date_spots",
        "title": "상대방 취향(커피 vs 와인)에 맞춘 맞춤형 데이트 코스 설계법",
        "intent": "사전 질문으로 상대방 취향을 파악해 감동 주는 코스 짜기",
        "aura_feature": "Aura 성향별 코스 설계"
    },
    {
        "id": 34,
        "category": "date_spots",
        "title": "첫 만남에서 너무 비싸지 않으면서 센스 있는 식당 고르는 법",
        "intent": "가성비와 분위기를 모두 잡는 스마트한 식당 선택 기준",
        "aura_feature": "Aura 센스 다이닝 추천"
    },
    {
        "id": 35,
        "category": "date_spots",
        "title": "야경이 예쁜 서울 한강 데이트 스팟과 드라이브 코스",
        "intent": "애프터 이후 로맨틱한 분위기를 완성하는 야경 명소",
        "aura_feature": "Aura 한강 야경 가이드"
    },
    {
        "id": 36,
        "category": "date_spots",
        "title": "AI가 추천하는 주말 취향 맞춤형 1:1 데이트 코스",
        "intent": "MBTI와 관심사 기반 AI 자동 완성 데이트 플랜",
        "aura_feature": "Aura AI 맞춤 데이트 코스"
    },

    # =========================================================================
    # [카테고리 3] conversation_skills (대화 꿀팁 & 어색함 탈출 - 18개 주제)
    # =========================================================================
    {
        "id": 37,
        "category": "conversation_skills",
        "title": "소개팅 첫 만남 10분, 어색한 침묵을 깨는 스몰토크 질문법",
        "intent": "초반 긴장을 풀고 편안한 분위기를 조성하는 오프닝 멘트",
        "aura_feature": "Aura AI 스몰토크 치트키"
    },
    {
        "id": 38,
        "category": "conversation_skills",
        "title": "호감도 200% 올려주는 '공감 + 질문' 핑퐁 대화의 기술",
        "intent": "단순 질문을 넘어 상대방이 신나서 이야기하게 만드는 법",
        "aura_feature": "Aura AI 핑퐁 대화 가이드"
    },
    {
        "id": 39,
        "category": "conversation_skills",
        "title": "소개팅에서 절대 꺼내면 안 되는 3대 금기 대화주제 (정치, 연봉, 전연인)",
        "intent": "분위기를 급랭시키는 위험한 주제 회피 요령",
        "aura_feature": "Aura 금기주제 알리미"
    },
    {
        "id": 40,
        "category": "conversation_skills",
        "title": "상대방이 끊임없이 말하게 만드는 마법의 '리액션 3원칙'",
        "intent": "눈맞춤, 고개 끄덕임, 감탄사로 호감도 극대화",
        "aura_feature": "Aura 리액션 코칭"
    },
    {
        "id": 41,
        "category": "conversation_skills",
        "title": "소개팅 분위기를 화기애애하게 만드는 밸런스게임 질문 10선",
        "intent": "어색한 타이밍에 자연스럽게 가치관을 공유하는 게임 질문",
        "aura_feature": "Aura AI 데일리 밸런스게임"
    },
    {
        "id": 42,
        "category": "conversation_skills",
        "title": "첫 만남 식사 계산, 센스 있게 더치페이/계산하는 매너",
        "intent": "계산대 앞 눈치 싸움 없이 서로 기분 좋은 결제 팁",
        "aura_feature": "Aura 소개팅 에티켓 가이드"
    },
    {
        "id": 43,
        "category": "conversation_skills",
        "title": "상대방의 취미와 관심사를 자연스럽게 이끌어내는 유도 질문",
        "intent": "취미가 없다고 답하는 상대방에게 디테일한 관심사 끌어내기",
        "aura_feature": "Aura 관심사 발굴기"
    },
    {
        "id": 44,
        "category": "conversation_skills",
        "title": "외모 칭찬보다 10배 효과적인 '디테일 칭찬법'",
        "intent": "겉모습 대신 말투, 분위기, 취향을 칭찬하는 고급 기술",
        "aura_feature": "Aura 칭찬 멘트 생성기"
    },
    {
        "id": 45,
        "category": "conversation_skills",
        "title": "내성적/I 성향인 사람을 위한 소개팅 대화 생존 가이드",
        "intent": "말수가 적어도 상대방에게 진중한 매력을 어필하는 법",
        "aura_feature": "Aura I 성향 매력 코칭"
    },
    {
        "id": 46,
        "category": "conversation_skills",
        "title": "직업이나 일 이야기만 하다가 면접 분위기 되지 않는 법",
        "intent": "일 이야기를 감정과 일상 에피소드로 부드럽게 전환하기",
        "aura_feature": "Aura 대화 전환 치트키"
    },
    {
        "id": 47,
        "category": "conversation_skills",
        "title": "상대방의 바디랭귀지로 호감 신호 읽어내는 5가지 단서",
        "intent": "몸의 기울기, 손짓, 시선 처리로 파악하는 상대의 마음",
        "aura_feature": "Aura 바디랭귀지 분석"
    },
    {
        "id": 48,
        "category": "conversation_skills",
        "title": "웃음 코드가 맞는지 확인하는 가벼운 유머 대화법",
        "intent": "부담 없는 셀프 디스나 일상 에피소드로 웃음 유발",
        "aura_feature": "Aura 유머 대화 가이드"
    },
    {
        "id": 49,
        "category": "conversation_skills",
        "title": "대화 도중 침묵이 찾아왔을 때 자연스럽게 넘기는 멘트",
        "intent": "침묵을 두려워하지 않고 여유롭게 화제를 전환하는 요령",
        "aura_feature": "Aura 침묵 극복 멘트"
    },
    {
        "id": 50,
        "category": "conversation_skills",
        "title": "첫인상 3초 법칙: 비언어적 호감(눈맞춤, 미소)의 중요성",
        "intent": "말보다 먼저 전달되는 밝은 표정과 아이컨택의 힘",
        "aura_feature": "Aura 첫인상 분석기"
    },
    {
        "id": 51,
        "category": "conversation_skills",
        "title": "서로의 가치관을 부담 없이 알아가는 가치관 토크 주제",
        "intent": "결혼관, 소비관, 연애관을 부드럽게 확인하는 대화법",
        "aura_feature": "Aura 가치관 매칭 테스트"
    },
    {
        "id": 52,
        "category": "conversation_skills",
        "title": "소개팅 도중 상대방이 마음에 들 때 보내는 은근한 호감 멘트",
        "intent": "부담스럽지 않게 호감을 드러내며 애프터를 유도하는 기술",
        "aura_feature": "Aura 호감 시그널 멘트"
    },
    {
        "id": 53,
        "category": "conversation_skills",
        "title": "상대방이 마음에 안 들 때 예의 지키며 마무리하는 매너",
        "intent": "주선자에게 피해 주지 않고 깔끔하게 식사 마치는 법",
        "aura_feature": "Aura 에티켓 가이드"
    },
    {
        "id": 54,
        "category": "conversation_skills",
        "title": "AI가 코칭해주는 소개팅 티키타카 대화 치트키",
        "intent": "소개팅에서 바로 써먹는 실전 대화 스크립트 모음",
        "aura_feature": "Aura AI 대화 코칭"
    },

    # =========================================================================
    # [카테고리 4] psychology_mbti (연애 심리 & 자가진단 & MBTI - 16개 주제)
    # =========================================================================
    {
        "id": 55,
        "category": "psychology_mbti",
        "title": "2026 연애 MBTI 궁합 순위: 최상의 궁합 vs 상극 궁합",
        "intent": "16개 MBTI 유형별 연애 시너지와 주의할 점 총정리",
        "aura_feature": "Aura MBTI 연애 궁합 리포트"
    },
    {
        "id": 56,
        "category": "psychology_mbti",
        "title": "내 연애 매력도와 플러팅 지수 자가진단 체크리스트",
        "intent": "자신의 연애 장점과 매력 포인트를 객관적으로 점검",
        "aura_feature": "Aura AI 매력도 진단 리포트"
    },
    {
        "id": 57,
        "category": "psychology_mbti",
        "title": "회피형 vs 불안형 애착유형 연애 심리와 갈등 해결법",
        "intent": "애착유형별 소통 방식 차이와 건강한 관계 맺기",
        "aura_feature": "Aura 애착유형 심리 리포트"
    },
    {
        "id": 58,
        "category": "psychology_mbti",
        "title": "남자가 진짜 반했을 때 무의식적으로 하는 행동 5가지",
        "intent": "남성의 무의식적 시선, 말투, 보호 행동 심리 분석",
        "aura_feature": "Aura 남성 심리 분석"
    },
    {
        "id": 59,
        "category": "psychology_mbti",
        "title": "여자가 호감 있을 때 보내는 은밀한 비언어적 시그널",
        "intent": "머리카락 넘기기, 웃음 리액션 등 여성의 호감 신호",
        "aura_feature": "Aura 여성 심리 분석"
    },
    {
        "id": 60,
        "category": "psychology_mbti",
        "title": "소개팅 전 '설렘'과 '불안'을 다스리는 마인드셋",
        "intent": "긴장감을 설렘으로 바꾸는 심리학적 인지 재구성",
        "aura_feature": "Aura 마인드셋 코칭"
    },
    {
        "id": 61,
        "category": "psychology_mbti",
        "title": "T 성향과 F 성향의 연애 소통 방식 차이와 극복 꿀팁",
        "intent": "공감형 F와 해결형 T의 갈등 없는 대화 솔루션",
        "aura_feature": "Aura T/F 소통 가이드"
    },
    {
        "id": 62,
        "category": "psychology_mbti",
        "title": "E 성향과 I 성향의 데이트 에너지 조절 노하우",
        "intent": "외향형과 내향형이 함께 편안한 데이트 템포 맞추기",
        "aura_feature": "Aura E/I 매칭 가이드"
    },
    {
        "id": 63,
        "category": "psychology_mbti",
        "title": "왜 매번 삼프터에서 실패할까? 연애 패턴 자가진단",
        "intent": "반복되는 만남 실패 원인을 분석하고 개선하기",
        "aura_feature": "Aura 연애 패턴 분석"
    },
    {
        "id": 64,
        "category": "psychology_mbti",
        "title": "자존감을 지키며 건강하게 연애를 시작하는 심리학 법칙",
        "intent": "상대에게 휘둘리지 않고 당당한 매력을 유지하는 법",
        "aura_feature": "Aura 자존감 케어"
    },
    {
        "id": 65,
        "category": "psychology_mbti",
        "title": "상대방의 진심을 알아보는 3가지 테스트 질문",
        "intent": "가벼운 만남인지 진지한 연애를 원하는지 가늠하는 법",
        "aura_feature": "Aura 진심 판별기"
    },
    {
        "id": 66,
        "category": "psychology_mbti",
        "title": "나에게 맞는 이상형의 기준을 명확히 정의하는 법",
        "intent": "외모뿐 아니라 가치관과 성향에 맞는 짝 찾기",
        "aura_feature": "Aura 이상형 매칭 프로필"
    },
    {
        "id": 67,
        "category": "psychology_mbti",
        "title": "어장관리와 진짜 호감의 결정적 차이점 4가지",
        "intent": "희망고문 당하지 않고 명확한 관계를 정립하는 법",
        "aura_feature": "Aura 어장관리 감별기"
    },
    {
        "id": 68,
        "category": "psychology_mbti",
        "title": "첫인상 매력 점수를 올려주는 심리학적 후광 효과",
        "intent": "목소리 톤과 미소가 첫인상 호감도에 미치는 영향",
        "aura_feature": "Aura 후광 효과 분석"
    },
    {
        "id": 69,
        "category": "psychology_mbti",
        "title": "전 연인과의 트라우마를 극복하고 새로운 만남 시작하기",
        "intent": "과거 상처를 털어내고 건강한 새 연애로 나아가는 법",
        "aura_feature": "Aura 힐링 연애 코칭"
    },
    {
        "id": 70,
        "category": "psychology_mbti",
        "title": "AI 얼굴/성격 분석으로 찾아내는 나의 진짜 매력 무기",
        "intent": "나도 몰랐던 비주얼과 성격의 독보적인 강점 발견",
        "aura_feature": "Aura AI 매력 리포트"
    },

    # =========================================================================
    # [카테고리 5] lookbook_style (소개팅 룩북 & 스타일링 - 15개 주제)
    # =========================================================================
    {
        "id": 71,
        "category": "lookbook_style",
        "title": "20대 30대 남자 소개팅 룩: 실패 없는 꾸안꾸 남친룩 정석",
        "intent": "과하지 않으면서 깔끔하고 댄디한 남자 소개팅 코디",
        "aura_feature": "Aura AI 남친룩 스타일 가이드"
    },
    {
        "id": 72,
        "category": "lookbook_style",
        "title": "소개팅 여자 첫인상 호감도 1위 메이크업 & 헤어 스타일링",
        "intent": "자연스럽고 맑은 피부 표현과 단정한 헤어 연출법",
        "aura_feature": "Aura AI 비주얼 가이드"
    },
    {
        "id": 73,
        "category": "lookbook_style",
        "title": "과하지 않고 은은한 소개팅 남자/여자 향수 추천 BEST 5",
        "intent": "호불호 없이 은은하게 잔향을 남기는 향수 큐레이션",
        "aura_feature": "Aura 향수 스타일 추천"
    },
    {
        "id": 74,
        "category": "lookbook_style",
        "title": "계절별(봄/가을) 소개팅 깔끔한 셔츠/니트 코디 조합",
        "intent": "간절기 깔끔한 톤온톤 셔츠와 슬랙스 연출법",
        "aura_feature": "Aura 시즌 룩북"
    },
    {
        "id": 75,
        "category": "lookbook_style",
        "title": "여름 소개팅 린넨 셔츠와 슬랙스 쾌적한 스타일링",
        "intent": "땀과 더위에 무너지지 않는 단정한 여름 코디",
        "aura_feature": "Aura 여름 코디 가이드"
    },
    {
        "id": 76,
        "category": "lookbook_style",
        "title": "겨울 소개팅 코트와 목폴라 단정한 클래식 룩",
        "intent": "패딩 대신 깔끔한 울 코트로 세련된 첫인상 남기기",
        "aura_feature": "Aura 겨울 클래식 룩"
    },
    {
        "id": 77,
        "category": "lookbook_style",
        "title": "소개팅에서 피해야 할 최악의 패션 아이템 5가지",
        "intent": "과도한 명품 로고, 찢어진 바지 등 감점 요인 경고",
        "aura_feature": "Aura 워스트 룩 피하기"
    },
    {
        "id": 78,
        "category": "lookbook_style",
        "title": "깔끔한 첫인상을 위한 남자 그루밍(눈썹, 피부톤, 입술) 가이드",
        "intent": "기초 피부 정돈과 입술 보습으로 훈훈함 2배 올리기",
        "aura_feature": "Aura 그루밍 코칭"
    },
    {
        "id": 79,
        "category": "lookbook_style",
        "title": "안경 착용자를 위한 지적이고 세련된 소개팅 스타일링",
        "intent": "얼굴형에 맞는 안경 프레임과 코디 매칭법",
        "aura_feature": "Aura 안경 스타일링"
    },
    {
        "id": 80,
        "category": "lookbook_style",
        "title": "신발 하나로 분위기 바꾸는 소개팅 스니커즈/구두 추천",
        "intent": "더러운 신발 방지 및 깔끔한 로퍼/화이트 스니커즈 추천",
        "aura_feature": "Aura 슈즈 큐레이션"
    },
    {
        "id": 81,
        "category": "lookbook_style",
        "title": "나에게 어울리는 퍼스널 컬러와 소개팅 옷 색상 매칭법",
        "intent": "웜톤/쿨톤에 맞춘 화사한 상의 컬러 선택 요령",
        "aura_feature": "Aura 퍼스널 컬러 진단"
    },
    {
        "id": 82,
        "category": "lookbook_style",
        "title": "체형별 단점을 커버하고 핏을 살리는 소개팅 코디 팁",
        "intent": "키가 커 보이고 슬림해 보이는 실루엣 연출법",
        "aura_feature": "Aura 핏 스타일 가이드"
    },
    {
        "id": 83,
        "category": "lookbook_style",
        "title": "시계, 목걸이, 벨트 등 과하지 않은 센스 있는 액세서리 연출",
        "intent": "작은 디테일로 세련미를 더하는 액세서리 활용법",
        "aura_feature": "Aura 액세서리 팁"
    },
    {
        "id": 84,
        "category": "lookbook_style",
        "title": "소개팅 당일 아침 10분 완성 붓기 빼기 & 스타일링 체크",
        "intent": "약속 전 컨디션과 외모를 최상으로 끌어올리는 루틴",
        "aura_feature": "Aura 당일 체크리스트"
    },
    {
        "id": 85,
        "category": "lookbook_style",
        "title": "AI가 진단해주는 나의 프로필 비주얼 스타일 분석",
        "intent": "내 얼굴형과 분위기에 가장 잘 어울리는 스타일 제안",
        "aura_feature": "Aura AI 비주얼 리포트"
    },

    # =========================================================================
    # [카테고리 6] after_dating (애프터 & 삼프터 고백 타이밍 - 15개 주제)
    # =========================================================================
    {
        "id": 86,
        "category": "after_dating",
        "title": "소개팅 헤어진 직후 당일 밤 카톡 보내는 골든 멘트",
        "intent": "귀가 후 안전 귀가 확인과 즐거웠던 소감 전달",
        "aura_feature": "Aura AI 귀가 카톡 추천"
    },
    {
        "id": 87,
        "category": "after_dating",
        "title": "소개팅 애프터 신청은 언제 하는 게 가장 성공률이 높을까?",
        "intent": "당일 밤 vs 다음 날 점심 등 최적의 타이밍 분석",
        "aura_feature": "Aura 애프터 타이밍 추천"
    },
    {
        "id": 88,
        "category": "after_dating",
        "title": "소개팅 삼프터의 의미와 100% 성공하는 고백 타이밍",
        "intent": "세 번째 만남에서 연인으로 확정 짓는 고백 전략",
        "aura_feature": "Aura AI 삼프터 고백 코칭"
    },
    {
        "id": 89,
        "category": "after_dating",
        "title": "애프터 수락 확률을 2배 높이는 구체적인 제안 화법",
        "intent": "'언제 밥 한번' 대신 구체적 메뉴와 날짜 제시하기",
        "aura_feature": "Aura 애프터 제안 멘트"
    },
    {
        "id": 90,
        "category": "after_dating",
        "title": "소개팅 다음 날 연락 템포: 상대방의 답장 반응별 대처법",
        "intent": "다음 날 상대방 텐션에 맞춰 연락을 유지하는 법",
        "aura_feature": "Aura 텐션 맞춤 코칭"
    },
    {
        "id": 91,
        "category": "after_dating",
        "title": "애프터 거절 신호(완곡한 거절)를 눈치채는 4가지 특징",
        "intent": "'이번 주는 바빠서요' 등 거절 시그널 읽고 쿨하게 대처",
        "aura_feature": "Aura 거절 시그널 분석"
    },
    {
        "id": 92,
        "category": "after_dating",
        "title": "2번째 만남에서 첫 만남보다 더 깊은 유대감 쌓는 법",
        "intent": "애프터에서 긴장 풀고 더 솔직하고 친밀한 대화 나누기",
        "aura_feature": "Aura 2차 만남 가이드"
    },
    {
        "id": 93,
        "category": "after_dating",
        "title": "썸에서 연인으로 발전하기 위한 손잡기/스킨십 타이밍",
        "intent": "자연스럽게 심쿵을 유발하는 에스코트와 스킨십",
        "aura_feature": "Aura 로맨스 타이밍 코칭"
    },
    {
        "id": 94,
        "category": "after_dating",
        "title": "주말 데이트 후 주중 카톡 유지하는 자연스러운 일상 공유법",
        "intent": "평일에도 지루하지 않게 사진과 일상으로 썸 이어가기",
        "aura_feature": "Aura 일상 카톡 가이드"
    },
    {
        "id": 95,
        "category": "after_dating",
        "title": "고백 장소와 타이밍: 로맨틱한 분위기 연출 노하우",
        "intent": "조용하고 분위기 있는 장소에서 진심 전하기",
        "aura_feature": "Aura 고백 스팟 큐레이션"
    },
    {
        "id": 96,
        "category": "after_dating",
        "title": "상대방이 애프터를 먼저 신청하게 만드는 여운 남기기",
        "intent": "다음 만남의 떡밥을 남겨두는 고단수 대화법",
        "aura_feature": "Aura 여운 남기기 기술"
    },
    {
        "id": 97,
        "category": "after_dating",
        "title": "첫 만남에서 호감이 없었지만 애프터로 반전 매력 보여준 후기",
        "intent": "아쉬웠던 첫인상을 2번째 만남에서 만회하는 꿀팁",
        "aura_feature": "Aura 반전 매력 가이드"
    },
    {
        "id": 98,
        "category": "after_dating",
        "title": "장거리 소개팅에서 애프터와 만남을 이어가는 요령",
        "intent": "거리의 한계를 극복하고 랜선 썸과 주말 만남 유지하기",
        "aura_feature": "Aura 장거리 연애 가이드"
    },
    {
        "id": 99,
        "category": "after_dating",
        "title": "연애 시작 직전, 서로의 가치관과 연애관 확인하는 대화",
        "intent": "사귀기 전 꼭 맞춰봐야 할 생활 습관과 연애 스타일",
        "aura_feature": "Aura 연애관 체크리스트"
    },
    {
        "id": 100,
        "category": "after_dating",
        "title": "AI 애프터 성공률 예측 모델로 내 만남 가능성 점검하기",
        "intent": "첫 만남 대화와 분위기를 토대로 성공률 분석",
        "aura_feature": "Aura AI 애프터 예측 리포트"
    }
]


def get_all_topics() -> List[Dict[str, Any]]:
    """100개 마스터 주제 전체 반환"""
    return AURA_100_TOPICS


def get_topic_by_id(topic_id: int) -> Dict[str, Any]:
    """ID로 특정 주제 1개 조회"""
    for t in AURA_100_TOPICS:
        if t["id"] == topic_id:
            return t
    return AURA_100_TOPICS[0]


def get_topics_by_category(category: str) -> List[Dict[str, Any]]:
    """특정 카테고리의 주제 목록 반환"""
    return [t for t in AURA_100_TOPICS if t["category"] == category]


if __name__ == "__main__":
    print(f"💖 [Aura] 100대 마스터 주제 로드 완료: 총 {len(AURA_100_TOPICS)}개")
    cats = {}
    for t in AURA_100_TOPICS:
        c = t["category"]
        cats[c] = cats.get(c, 0) + 1
    for c, count in cats.items():
        print(f"  - {c}: {count}개 주제")
