# -*- coding: utf-8 -*-
"""
InsuranceWebSimulatorActions - 📱 [보험 리밸런스 8대 대주제별 웹앱 인터랙션 레고 블록 모듈]
- 각 주제별(Topic 1 ~ Topic 8) 브라우저 조작, 폼 입력값, 스크롤 구간 완벽 독립 정의
- 공통 12초 세로 9:16 Full HD 규격 준수:
  1) [0.0s ~ 0.8s] 상단 헤더/팝업 없는 신뢰도 뷰 시작
     - Topic 1~6: '제휴 협력 파트너 33개사 실시간 통합 비교' 로고 그리드(y=3780)
     - Topic 7~8: '원클릭 내 보험 분석 & 고객과의 안심 3대 약속' 뷰(y=13450)
  2) [0.8s ~ 2.8s] 주제별 맞춤 카테고리/특약/생년월일/성별 클릭 및 정밀 분석 버튼 실행
  3) [2.8s ~ 12.0s] (무려 9.2초 동안!) 가독성 높고 여유롭게 주제별 리포트 및 비교 순위표 안착 스크롤
  4) ✨ 불필요한 공시자료/상담 푸터 영역 침범 Zero
"""

from typing import Dict, Any


TOPIC_ACTIONS: Dict[int, Dict[str, Any]] = {
    1: {
        "topic_id": 1,
        "theme_name": "실손의료비 4세대 전환 손익",
        "init_scroll_y": 3780,
        "birth": "19820512",
        "gender": "여성",
        "category_keyword": "의료실비",
        "sub_keyword": "4세대 실손",
        "start_scroll_y": 22600,
        "end_scroll_y": 25650,
        "duration_scroll_ms": 8800,
        "mode": "standard"
    },
    2: {
        "topic_id": 2,
        "theme_name": "운전자보험 1만원의 법칙",
        "init_scroll_y": 3780,
        "birth": "19880315",
        "gender": "남성",
        "category_keyword": "운전자",
        "sub_keyword": "필수 3대 특약",
        "start_scroll_y": 24500,
        "end_scroll_y": 27550,
        "duration_scroll_ms": 8800,
        "mode": "standard"
    },
    3: {
        "topic_id": 3,
        "theme_name": "암보험 일반암 vs 유사암 진실",
        "init_scroll_y": 3780,
        "birth": "19800720",
        "gender": "여성",
        "category_keyword": "암보험",
        "sub_keyword": "진단비",
        "start_scroll_y": 21900,
        "end_scroll_y": 24950,
        "duration_scroll_ms": 8800,
        "mode": "standard"
    },
    4: {
        "topic_id": 4,
        "theme_name": "뇌·심장 질환 뇌출혈 vs 뇌혈관",
        "init_scroll_y": 3780,
        "birth": "19781105",
        "gender": "남성",
        "category_keyword": "뇌혈관",
        "sub_keyword": "허혈성",
        "start_scroll_y": 21200,
        "end_scroll_y": 24250,
        "duration_scroll_ms": 8800,
        "mode": "standard"
    },
    5: {
        "topic_id": 5,
        "theme_name": "종신보험 저축 오해 & 사업비 다이어트",
        "init_scroll_y": 3780,
        "birth": "19900912",
        "gender": "남성",
        "category_keyword": "종신",
        "sub_keyword": "비갱신",
        "start_scroll_y": 23000,
        "end_scroll_y": 26400,
        "duration_scroll_ms": 8800,
        "mode": "standard"
    },
    6: {
        "topic_id": 6,
        "theme_name": "어린이·어른이 100세 만기 비갱신 리모델링",
        "init_scroll_y": 3780,
        "birth": "19950418",
        "gender": "여성",
        "category_keyword": "종합건강",
        "sub_keyword": "기본형",
        "start_scroll_y": 24000,
        "end_scroll_y": 27050,
        "duration_scroll_ms": 8800,
        "mode": "standard"
    },
    7: {
        "topic_id": 7,
        "theme_name": "내 보험 숨은 중복 보장 & 새는 보험료 색출",
        "init_scroll_y": 13400,
        "birth": "19850624",
        "gender": "여성",
        "category_keyword": "암보험",
        "sub_keyword": "진단비",
        "start_scroll_y": 26490,
        "end_scroll_y": 33000,
        "duration_scroll_ms": 8500,
        "mode": "oneclick"
    },
    8: {
        "topic_id": 8,
        "theme_name": "원클릭 내 보험 5대 필수 보장 점수 & 공백 진단",
        "init_scroll_y": 13400,
        "birth": "19871203",
        "gender": "여성",
        "category_keyword": "암보험",
        "sub_keyword": "진단비 최대 1억",
        "start_scroll_y": 26490,
        "end_scroll_y": 33000,
        "duration_scroll_ms": 8500,
        "mode": "oneclick"
    }
}


def get_topic_action_spec(topic_id: int) -> Dict[str, Any]:
    """주제 ID에 대응하는 웹 시뮬레이션 설정 반환 (1~8 순환)"""
    key = ((topic_id - 1) % len(TOPIC_ACTIONS)) + 1
    return TOPIC_ACTIONS.get(key, TOPIC_ACTIONS[1])
