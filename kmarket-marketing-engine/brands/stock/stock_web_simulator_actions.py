# -*- coding: utf-8 -*-
"""
StockWebSimulatorActions - 🎯 [StockMaster AI 8대 주제별 실물 웹앱 실시간 시뮬레이션 액션 스펙]
======================================================================================
- 10분마다 국내 350개 우량주 실시간 업데이트 계량 전광판 & 리스크 센터 전담
- 타깃 URL: https://stockmaster-ai.vercel.app/
- 1080x1920 세로 9:16 모바일 풀HD 뷰 최적화
- [0.0s ~ 1.5s] 350개 핵심 종목 10분 계량 전광판 헤더 & 당일 1위 주도주 조망
- [1.5s ~ 3.5s] 검색창 종목 검색 (삼성전자/SK하이닉스/이수페타시스) 또는 필터 탭 클릭
- [3.5s ~ 12.0s] 체결강도, 외인/기관 수급, AI 적정주가 상세 차트로 부드러운 안착 스크롤
"""

from typing import Dict, Any

STOCK_TOPIC_ACTION_SPECS: Dict[int, Dict[str, Any]] = {
    1: {
        "topic_id": 1,
        "title": "삼성전자 vs SK하이닉스 HBM 수급 대결",
        "init_scroll_y": 4090,          # 10분 계량 전광판 350개 종목 헤더 위치
        "search_query": "삼성전자",
        "filter_btn": "",
        "start_scroll_y": 4090,
        "end_scroll_y": 5500,
        "duration_scroll_ms": 7800,
        "description": "350개 종목 10분 계량 전광판에서 삼성전자 실시간 검색 ➔ 외국인/기관 수급 및 체결강도 1초 분석"
    },
    2: {
        "topic_id": 2,
        "title": "미국 배당성장 ETF(SCHD·JEPQ) 월 100만원 배당",
        "init_scroll_y": 4090,
        "search_query": "SK하이닉스",
        "filter_btn": "",
        "start_scroll_y": 4090,
        "end_scroll_y": 5600,
        "duration_scroll_ms": 7800,
        "description": "10분 계량 전광판에서 SK하이닉스 실시간 수급 및 외국계 순매수 추이 분석"
    },
    3: {
        "topic_id": 3,
        "title": "코스피·코스닥 세력 체결강도 120% 돌파 유망주",
        "init_scroll_y": 4090,
        "search_query": "이수페타시스",
        "filter_btn": "",
        "start_scroll_y": 4090,
        "end_scroll_y": 5400,
        "duration_scroll_ms": 7800,
        "description": "국내 반도체 공급망 1위 수급 가속 종목 실시간 퀀트 점수 및 체결강도 확인"
    },
    4: {
        "topic_id": 4,
        "title": "저PBR 밸류업 & 고배당 금융주 스크리너",
        "init_scroll_y": 4090,
        "search_query": "",
        "filter_btn": "✨ 변곡점",
        "start_scroll_y": 4090,
        "end_scroll_y": 5800,
        "duration_scroll_ms": 7800,
        "description": "10분 전광판에서 수급 상승 변곡점 종목 1초 필터링"
    },
    5: {
        "topic_id": 5,
        "title": "뇌동매매 방지! AI 자동 손절매 & 리스크 가드",
        "init_scroll_y": 4090,
        "search_query": "",
        "filter_btn": "🔴 배제(VETO)",
        "start_scroll_y": 4090,
        "end_scroll_y": 5800,
        "duration_scroll_ms": 7800,
        "description": "실시간 리스크 센터에서 배제(VETO) 종목 및 손절선 알림 확인"
    },
    6: {
        "topic_id": 6,
        "title": "S&P 500 vs 나스닥 100: 직장인 20년 월적립식 복리",
        "init_scroll_y": 4090,
        "search_query": "",
        "filter_btn": "🟢 진입유효",
        "start_scroll_y": 4090,
        "end_scroll_y": 5800,
        "duration_scroll_ms": 7800,
        "description": "10분 단위 퀀트 점수 상위 진입 유효 주도주 실시간 확인"
    },
    7: {
        "topic_id": 7,
        "title": "외국인·기관 쌍끌이 순매수 실시간 레이더",
        "init_scroll_y": 4090,
        "search_query": "",
        "filter_btn": "체결강도순",
        "start_scroll_y": 4090,
        "end_scroll_y": 5900,
        "duration_scroll_ms": 7800,
        "description": "350개 종목 중 당일 체결강도 40점 만점 쌍끌이 주도주 정렬"
    },
    8: {
        "topic_id": 8,
        "title": "초보 탈출! 원클릭 AI 종목 재무 건전성 진단",
        "init_scroll_y": 4090,
        "search_query": "현대차",
        "filter_btn": "",
        "start_scroll_y": 4090,
        "end_scroll_y": 5600,
        "duration_scroll_ms": 7800,
        "description": "종목 검색으로 10분 계량 가중치 및 재무 건전성 1초 진단"
    }
}


def get_stock_topic_action_spec(topic_id: int) -> Dict[str, Any]:
    norm_id = ((topic_id - 1) % len(STOCK_TOPIC_ACTION_SPECS)) + 1
    return STOCK_TOPIC_ACTION_SPECS.get(norm_id, STOCK_TOPIC_ACTION_SPECS[1])
