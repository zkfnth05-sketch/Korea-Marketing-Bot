# -*- coding: utf-8 -*-
"""
📈 StockMaster AI 100대 마스터 토픽 풀 (100 Master Topics Pool - 100% 대한민국 국내 증시 전담)
=============================================================================================
- 브랜드: StockMaster AI (주식 AI 계량 분석 & 10분 전광판 & 뇌동매매 방지 VETO & 손절선)
- 타깃: 2050 스마트 개미, 직장인 적립식·스윙 투자자, 뇌동매매 탈출 희망자
- 100% 대한민국 국내 증시(코스피/코스닥) & 우리 웹앱(stockmaster-ai.vercel.app) 365일 상시 고정 7대 영역 1:1 연동:
  1. realtime_rank1  (15개): 🏆 [실시간 1위 TOP PICK] 체결강도 120% 돌파 & 당일 주도주 수급 해석
  2. valid_entry     (15개): 🟢 [진입유효 탭] 외국인 순매수 & 큰손 블록오더 70%+ 수급 유입 종목
  3. veto_risk       (15개): 🔴 [배제(VETO) 탭] 이격과열 경고 & 역배열 물타기 금지 뇌동매매 차단
  4. turning_point   (15개): ✨ [변곡점·신고가 탭] 골든크로스 & 거래량 급증 바닥 탈출 종목
  5. macro_stress    (10개): 📊 [매크로 스트레스 지수] 환율(USD/KRW)·유가 연동 외인 수급 예측
  6. price_boundary  (15개): 🎯 [손절선(SL)·목표선(TP)] ATR 기반 과학적 가격 타점 계산기
  7. quant_guide     (15개): 💡 [8대 퀀트 리스크 가이드] ROE/PBR 밸류업 & DART 공시 건전성 진단
"""

import sys
from typing import List, Dict, Any, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

STOCK_100_TOPICS: List[Dict[str, Any]] = [
    # ── [1. realtime_rank1 : 🏆 실시간 1위 TOP PICK & 당일 주도주 수급 (15개)] ──
    {
        "id": 1,
        "category": "realtime_rank1",
        "title": "오늘 AI 전광판 실시간 1위 주도주와 체결강도 120% 돌파의 숨은 의미",
        "intent": "코스피·코스닥 350개 종목 중 실시간 계량 1위 종목의 수급 폭발과 장중 진입 타점 분석",
        "app_feature": "StockMaster AI 실시간 10분 계량 전광판 1위 카드",
        "app_action_mode": "rank1",
        "tags": ["실시간주도주", "체결강도120", "외국인순매수", "StockMasterAI"]
    },
    {
        "id": 2,
        "category": "realtime_rank1",
        "title": "전광판 1위 종목의 외국계 순매수액 급증: 큰손들의 장중 매집 시그널 포착법",
        "intent": "외국계 증권사 창구로 쏟아지는 억 단위 순매수액을 실시간으로 추적하는 기술",
        "app_feature": "StockMaster AI 외국계 순매수 실시간 트래커",
        "app_action_mode": "rank1",
        "tags": ["외국인순매수", "수급매매기법", "외국계창구", "주식수급분석"]
    },
    {
        "id": 3,
        "category": "realtime_rank1",
        "title": "대량 체결 블록오더 비중 70% 돌파: 개미가 절대 만들 수 없는 세력 매수세",
        "intent": "1억 원 이상 뭉칫돈 주문인 블록오더 비중이 주가 단기 폭발에 미치는 영향",
        "app_feature": "StockMaster AI 블록오더 실시간 비중 분석",
        "app_action_mode": "rank1",
        "tags": ["블록오더", "세력매집", "대량체결", "장중급등주"]
    },
    {
        "id": 4,
        "category": "realtime_rank1",
        "title": "체결 가속도(+%p) 급증 시그널: 정체되던 호가창이 갑자기 불타오르는 순간",
        "intent": "체결강도의 단순 수치가 아닌 가속도(+2.5%p 이상) 변화를 통한 급등 초입 포착",
        "app_feature": "StockMaster AI 체결 가속도 감지기",
        "app_action_mode": "rank1",
        "tags": ["체결가속도", "호가창매매", "급등초입", "단타타점"]
    },
    {
        "id": 5,
        "category": "realtime_rank1",
        "title": "전광판 1위 종목의 스윙 목표선(SWING TP) 도달 시 분할 익절하는 정석 원칙",
        "intent": "AI가 산출한 1차 목표선 도달 시 욕심부리지 않고 50% 수익 실현하는 룰",
        "app_feature": "StockMaster AI 스윙 목표선 계산 카드",
        "app_action_mode": "rank1",
        "tags": ["스윙목표가", "분할익절", "수익실현원칙", "주식매도타이밍"]
    },
    {
        "id": 6,
        "category": "realtime_rank1",
        "title": "청산 손절선(EXIT SL) 이탈 시 칼손절의 미학: 내 계좌 원금을 지키는 방탄 룰",
        "intent": "1위 주도주라 해도 시장 급락 시 손절선을 건드리면 기계적으로 잘라내는 생존법",
        "app_feature": "StockMaster AI 청산 손절선 경보",
        "app_action_mode": "rank1",
        "tags": ["손절선설정", "원금보호", "기계적손절", "스탑로스"]
    },
    {
        "id": 7,
        "category": "realtime_rank1",
        "title": "장 시작 10분(09:10) 전광판 1위 vs 오후 2시(14:00) 1위의 결정적 차이",
        "intent": "시초가 가짜 펌핑에 속지 않고 오후장까지 힘이 유지되는 진짜 주도주 판별법",
        "app_feature": "StockMaster AI 시간대별 전광판 추이",
        "app_action_mode": "rank1",
        "tags": ["시초가매매", "오후장주도주", "종가베팅", "가짜급등구별"]
    },
    {
        "id": 8,
        "category": "realtime_rank1",
        "title": "거래대금 1,000억 이상 터진 전광판 1위: 시장의 모든 돈이 몰리는 대장주 매매",
        "intent": "풍부한 유동성으로 슬리피지 없이 안전하게 큰 금액을 운용하는 대형 주도주 공략법",
        "app_feature": "StockMaster AI 거래대금 상위 레이더",
        "app_action_mode": "rank1",
        "tags": ["거래대금상위", "시장대장주", "안전한단타", "유동성매매"]
    },
    {
        "id": 9,
        "category": "realtime_rank1",
        "title": "코스피 대형주 vs 코스닥 중소형주: 전광판 1위 종목별 변동성 대응 전략",
        "intent": "지수 대형주의 묵직한 추세 추종과 코스닥 급등주의 빠른 손절선 관리법 비교",
        "app_feature": "StockMaster AI 시장별 랭킹 분리 필터",
        "app_action_mode": "rank1",
        "tags": ["코스피대형주", "코스닥급등주", "변동성관리", "투자전략비교"]
    },
    {
        "id": 10,
        "category": "realtime_rank1",
        "title": "전광판 1위 종목의 퀀트 총점 140점 만점 구조: 수급·차트·재무 가중치 해부",
        "intent": "체결강도(40점), 외인기관(45점), 정배열(15점), 저PBR(15점) 등 AI 종합 배점표",
        "app_feature": "StockMaster AI 계량 가중치 분석표",
        "app_action_mode": "rank1",
        "tags": ["퀀트점수", "종합계량분석", "AI종목진단", "수급가중치"]
    },
    {
        "id": 11,
        "category": "realtime_rank1",
        "title": "전광판 1위 종목의 '⚡ 수급 가속 특례' 배지가 떴을 때 장중 상한가 확률",
        "intent": "단순 거래량이 아닌 장중 호가 공백을 메우며 수급이 가속되는 특례 조건 분석",
        "app_feature": "StockMaster AI 수급 가속 특례 배지",
        "app_action_mode": "rank1",
        "tags": ["수급가속특례", "상한가포착", "급등주패턴", "세력주포착"]
    },
    {
        "id": 12,
        "category": "realtime_rank1",
        "title": "전광판 1~3위 종목의 업종(섹터) 쏠림 현상으로 당일 주도 테마 1초 만에 읽기",
        "intent": "상위권에 반도체나 2차전지, 바이오가 몰릴 때 섹터 전체로 확산되는 순환매 매매",
        "app_feature": "StockMaster AI 실시간 섹터 쏠림 분석",
        "app_action_mode": "rank1",
        "tags": ["주도섹터", "테마순환매", "업종대장주", "섹터트렌드"]
    },
    {
        "id": 13,
        "category": "realtime_rank1",
        "title": "전일 대비 갭상승(Gap-Up)한 전광판 1위: 시초가 추격 매수 vs 1차 눌림목 대기",
        "intent": "갭을 메우러 내려오는 5분봉 지지 확인 후 진입하여 승률 80% 만드는 법",
        "app_feature": "StockMaster AI 갭상승 눌림목 판독기",
        "app_action_mode": "rank1",
        "tags": ["갭상승매매", "눌림목매수", "시초가전략", "단기반등"]
    },
    {
        "id": 14,
        "category": "realtime_rank1",
        "title": "전광판 TOP 3 분산 투자 공식: 몰빵 투자 끝내고 계좌 우상향 만드는 법",
        "intent": "1위, 2위, 3위 주도주에 33%씩 비중을 분산하여 하방 리스크를 줄이는 포트폴리오",
        "app_feature": "StockMaster AI TOP3 포트폴리오 빌더",
        "app_action_mode": "rank1",
        "tags": ["분산투자", "포트폴리오구성", "몰빵금지", "계좌우상향"]
    },
    {
        "id": 15,
        "category": "realtime_rank1",
        "title": "직장인을 위한 장 마감 후 전광판 1위 분석법: 퇴근 후 내일 시초가 예약 매수 세팅",
        "intent": "장중 HTS를 볼 수 없는 직장인이 당일 1위 수급 종목으로 다음 날 수익 내는 루틴",
        "app_feature": "StockMaster AI 직장인 퇴근 리포트",
        "app_action_mode": "rank1",
        "tags": ["직장인주식루틴", "예약매매", "퇴근후주식", "내일시초가"]
    },

    # ── [2. valid_entry : 🟢 진입유효 탭 & 큰손 블록오더 순매수 (15개)] ──
    {
        "id": 16,
        "category": "valid_entry",
        "title": "[🟢 진입유효] 필터의 절대 원칙: AI가 350개 종목 중 안전한 종목만 남기는 법",
        "intent": "수급 가속, 정배열 추세, 재무 건전성 3박자를 통과한 종목만 필터링하는 원리",
        "app_feature": "StockMaster AI [🟢 진입유효] 실시간 필터 버튼",
        "app_action_mode": "valid_entry",
        "tags": ["진입유효", "종목스크리닝", "안전한종목", "AI종목선정"]
    },
    {
        "id": 17,
        "category": "valid_entry",
        "title": "외국인·기관 쌍끌이 순매수 종목만 쏙쏙 골라내는 [🟢 진입유효] 탭 활용법",
        "intent": "개미들의 매도세를 받아내며 큰손들이 주가를 밀어 올리는 쌍끌이 종목 발굴",
        "app_feature": "StockMaster AI 쌍끌이 수급 자동 추출",
        "app_action_mode": "valid_entry",
        "tags": ["쌍끌이순매수", "기관외인매집", "주도주포착", "수급유입"]
    },
    {
        "id": 18,
        "category": "valid_entry",
        "title": "이동평균선 20일선 황금 정배열에서 뜬 [🟢 진입유효]: 추세 매매의 정석",
        "intent": "역배열 하락 위험 없이 20일선 지지를 받으며 우상향하는 종목 공략 기법",
        "app_feature": "StockMaster AI 이평선 정배열 감지기",
        "app_action_mode": "valid_entry",
        "tags": ["정배열차트", "20일선지지", "추세추종매매", "골든크로스"]
    },
    {
        "id": 19,
        "category": "valid_entry",
        "title": "거래대금 500억 이상 터진 [🟢 진입유효] 우량주: 거래량 없는 잡주 거르기",
        "intent": "호가창이 얇아 매도하기 힘든 부실주를 거르고 환금성 높은 대형 우량주만 매매",
        "app_feature": "StockMaster AI 거래대금 필터링",
        "app_action_mode": "valid_entry",
        "tags": ["거래대금우량주", "잡주필터링", "환금성", "대형주매매"]
    },
    {
        "id": 20,
        "category": "valid_entry",
        "title": "[🟢 진입유효] 리스트 중 체결강도 130% 초과 종목: 당일 장중 시세 분출 1순위",
        "intent": "진입유효 종목 중에서도 매수세가 매도세를 압도하는 초강세 종목 선별 공식",
        "app_feature": "StockMaster AI 체결강도 상위 정렬",
        "app_action_mode": "valid_entry",
        "tags": ["체결강도130", "초강세종목", "당일급등", "매수우위"]
    },
    {
        "id": 21,
        "category": "valid_entry",
        "title": "바닥권에서 첫 번째로 뜬 [🟢 진입유효]: 3분할 매수로 안전하게 평단가 맞추기",
        "intent": "기나긴 조정을 끝내고 최초로 AI 진입 신호가 뜬 종목의 1차, 2차 분할 매수법",
        "app_feature": "StockMaster AI 바닥권 최초 진입 시그널",
        "app_action_mode": "valid_entry",
        "tags": ["바닥권매수", "3분할매수", "평단가관리", "안전투자"]
    },
    {
        "id": 22,
        "category": "valid_entry",
        "title": "[🟢 진입유효] 종목의 스윙 목표 수익률: 5~10% 안정적 차익 실현 설계법",
        "intent": "단타의 피로감을 줄이고 3~5일 스윙으로 계좌를 꾸준히 불려 나가는 노하우",
        "app_feature": "StockMaster AI 스윙 목표선 자동 제시",
        "app_action_mode": "valid_entry",
        "tags": ["스윙투자", "목표수익률", "차익실현", "단기스윙"]
    },
    {
        "id": 23,
        "category": "valid_entry",
        "title": "상승장에서 [🟢 진입유효] 종목을 끝까지 쥐고 가는 트레일링 스탑의 마법",
        "intent": "일찍 팔아서 배 아픈 실수를 방지하고 최고점 대비 -3% 하락 시 익절하는 기술",
        "app_feature": "StockMaster AI 트레일링 스탑 가이드",
        "app_action_mode": "valid_entry",
        "tags": ["트레일링스탑", "수익극대화", "추세홀딩", "익절관리"]
    },
    {
        "id": 24,
        "category": "valid_entry",
        "title": "코스피 지수 폭락장에서도 [🟢 진입유효]를 유지하는 방어주의 숨은 비밀",
        "intent": "시장 하락 시 기관과 외국인의 피난처가 되는 경기방어주·고배당주 포착법",
        "app_feature": "StockMaster AI 시장 역행 방어주 레이더",
        "app_action_mode": "valid_entry",
        "tags": ["폭락장방어주", "시장역행주", "배당방어주", "하락장대응"]
    },
    {
        "id": 25,
        "category": "valid_entry",
        "title": "[🟢 진입유효] 종목 중 ROE(자기자본이익률) 10% 이상 알짜배기 기업 검증법",
        "intent": "단순 차트 테마주가 아닌 진짜 돈을 잘 버는 펀더멘털 우량 기업 2중 필터링",
        "app_feature": "StockMaster AI ROE 펀더멘털 검증",
        "app_action_mode": "valid_entry",
        "tags": ["ROE우량주", "펀더멘털검증", "진짜우량주", "가치성장주"]
    },
    {
        "id": 26,
        "category": "valid_entry",
        "title": "[🟢 진입유효] 탭에서 PBR 1배 미만 밸류업 저평가 우량주 골라내기",
        "intent": "주가가 청산가치보다 저렴하면서 수급까지 붙어 올라가는 저PBR 수혜주 매매",
        "app_feature": "StockMaster AI 저PBR 밸류업 정렬",
        "app_action_mode": "valid_entry",
        "tags": ["저PBR관련주", "기업밸류업", "저평가우량주", "가치투자"]
    },
    {
        "id": 27,
        "category": "valid_entry",
        "title": "시가총액 1조 이상 대형주 중 [🟢 진입유효] 뜬 종목: 직장인 월급 적립식 투자",
        "intent": "매달 월급날 안정적으로 모아갈 수 있는 코스피 대표 대형주 스크리닝",
        "app_feature": "StockMaster AI 대형주 진입유효 필터",
        "app_action_mode": "valid_entry",
        "tags": ["직장인적립식", "대형주투자", "월급재테크", "우량주적립"]
    },
    {
        "id": 28,
        "category": "valid_entry",
        "title": "코스닥 기술성장주 중 [🟢 진입유효] 포착: 단기 탄력 20% 모멘텀 매매",
        "intent": "바이오, 로봇, AI 팹리스 등 끼 있는 코스닥 성장주의 안전 진입 타이밍",
        "app_feature": "StockMaster AI 코스닥 모멘텀 레이더",
        "app_action_mode": "valid_entry",
        "tags": ["코스닥성장주", "모멘텀매매", "기술성장기업", "단기탄력"]
    },
    {
        "id": 29,
        "category": "valid_entry",
        "title": "[🟢 진입유효] 상태가 3일 연속 유지되는 종목의 중기 스윙 승률 분석",
        "intent": "단발성 수급이 아닌 며칠에 걸쳐 매집이 이어지는 진짜 주도주의 홀딩 전략",
        "app_feature": "StockMaster AI 연속 수급 유지 트래커",
        "app_action_mode": "valid_entry",
        "tags": ["연속수급", "중기스윙", "세력지속매집", "홀딩전략"]
    },
    {
        "id": 30,
        "category": "valid_entry",
        "title": "주린이를 위한 [🟢 진입유효] 원클릭 종목 자가진단 3분 루틴",
        "intent": "아침 9시 30분, 점심 12시 30분 하루 2번 [🟢 진입유효] 버튼 눌러 시장 점검하기",
        "app_feature": "StockMaster AI 원클릭 자가진단 가이드",
        "app_action_mode": "valid_entry",
        "tags": ["주린이루틴", "원클릭진단", "자가진단법", "초보주식공부"]
    },

    # ── [3. veto_risk : 🔴 배제(VETO) 탭 & 뇌동매매 방지 (15개)] ──
    {
        "id": 31,
        "category": "veto_risk",
        "title": "[🔴 배제(VETO)] 필터란 무엇인가? AI가 손실 위험 종목을 원천 차단하는 4대 룰",
        "intent": "이격과열, 역배열 하락, 공매도 과다, 신용 폭탄 종목에 진입 금지 경보를 때리는 원리",
        "app_feature": "StockMaster AI [🔴 배제(VETO)] 실시간 필터 버튼",
        "app_action_mode": "veto_risk",
        "tags": ["VETO필터", "진입금지경보", "리스크관리", "손실차단"]
    },
    {
        "id": 32,
        "category": "veto_risk",
        "title": "5일선/20일선 이격도 115% 초과 '이격과열 경고': 상투 잡는 고점 매수 피하기",
        "intent": "주가가 단기 급등하여 단기 이평선과 너무 벌어졌을 때 발생하는 급락 폭탄 방지",
        "app_feature": "StockMaster AI 이격과열 자동 경보",
        "app_action_mode": "veto_risk",
        "tags": ["이격과열", "고점상투피하기", "이격도분석", "추격매수금지"]
    },
    {
        "id": 33,
        "category": "veto_risk",
        "title": "역배열 하락 추세 종목에 '물타기 금지' 🔴 VETO가 뜨는 냉정한 이유",
        "intent": "떨어지는 칼날을 잡으며 평단가를 낮추려다 계좌가 반토막 나는 물타기 함정 탈출",
        "app_feature": "StockMaster AI 물타기 금지 VETO 감지",
        "app_action_mode": "veto_risk",
        "tags": ["물타기금지", "역배열추세", "떨어지는칼날", "계좌원금보호"]
    },
    {
        "id": 34,
        "category": "veto_risk",
        "title": "공매도 비중 10% 이상 과다 종목의 🔴 VETO 경보: 기관 숏 타깃 피하는 법",
        "intent": "주가 상방이 꽉 막혀 있고 작은 악재에도 투매가 나오는 공매도 집중 종목 회피",
        "app_feature": "StockMaster AI 공매도 과다 경고",
        "app_action_mode": "veto_risk",
        "tags": ["공매도과다", "기관숏포지션", "대차잔고리스크", "투매방지"]
    },
    {
        "id": 35,
        "category": "veto_risk",
        "title": "신용잔고율 5% 초과 '반대매매 폭탄' 위험 종목: 개미 빚투가 부르는 참사",
        "intent": "지수 하락 시 아침 8시 40분 하한가 반대매매 매물이 쏟아질 고위험 종목 거르기",
        "app_feature": "StockMaster AI 신용잔고율 위험 경보",
        "app_action_mode": "veto_risk",
        "tags": ["신용잔고율", "반대매매경보", "빚투위험", "하한가폭탄피하기"]
    },
    {
        "id": 36,
        "category": "veto_risk",
        "title": "실적 발표 어닝쇼크 발생 시 즉시 🔴 VETO로 전환되는 메커니즘",
        "intent": "영업이익이 컨센서스 대비 -20% 이상 미달했을 때 AI가 즉시 매수 금지를 내리는 룰",
        "app_feature": "StockMaster AI 실적 충격 VETO 전환",
        "app_action_mode": "veto_risk",
        "tags": ["어닝쇼크", "실적악화", "즉시배제", "컨센서스미달"]
    },
    {
        "id": 37,
        "category": "veto_risk",
        "title": "DART 전자공시 전환사채(CB)·유상증자 폭탄 터진 종목의 🔴 VETO 필터링",
        "intent": "주식 수가 수천만 주 늘어나 기존 주주 가치가 희석되는 부실 한계기업 회피",
        "app_feature": "StockMaster AI DART 악재 자동 감지",
        "app_action_mode": "veto_risk",
        "tags": ["전환사채CB", "유상증자폭탄", "주주가치희석", "부실기업회피"]
    },
    {
        "id": 38,
        "category": "veto_risk",
        "title": "급등 테마주 불기둥에 뇌동매매(FOMO) 오려 할 때 [🔴 배제] 탭 확인하는 습관",
        "intent": "빨간 불기둥을 보고 충동적으로 매수 버튼에 손이 갈 때 VETO 사유를 확인하고 참기",
        "app_feature": "StockMaster AI 뇌동매매 방지 리스크 확인",
        "app_action_mode": "veto_risk",
        "tags": ["뇌동매매방지", "FOMO탈출", "충동매수금지", "멘탈관리"]
    },
    {
        "id": 39,
        "category": "veto_risk",
        "title": "내가 보유한 종목이 🟢에서 🔴 VETO로 바뀌었을 때 즉시 대처하는 3단계 매뉴얼",
        "intent": "수급이 이탈하고 지지선이 무너질 때 비중 축소 및 손절매를 실행하는 가이드",
        "app_feature": "StockMaster AI 보유 종목 상태 변화 알림",
        "app_action_mode": "veto_risk",
        "tags": ["상태변화대응", "비중축소", "손절매뉴얼", "계좌방어"]
    },
    {
        "id": 40,
        "category": "veto_risk",
        "title": "🔴 VETO(조기 청산 권고)가 떴을 때 수익 보존 익절하는 타이밍 잡기",
        "intent": "수익 중인 종목이라도 VETO 시그널이 발생하면 미련 없이 차익을 챙기는 원칙",
        "app_feature": "StockMaster AI 조기 청산 권고 카드",
        "app_action_mode": "veto_risk",
        "tags": ["조기청산권고", "수익보존익절", "차익실현", "미련버리기"]
    },
    {
        "id": 41,
        "category": "veto_risk",
        "title": "깡통 차는 지름길: 🔴 VETO 뜬 동전주·관리종목에 한 방 역전 노리다 상폐당하는 이유",
        "intent": "주가 1,000원 미만 잡주의 감자·상장폐지 위험을 AI로 사전 차단하는 법",
        "app_feature": "StockMaster AI 동전주 관리종목 경보",
        "app_action_mode": "veto_risk",
        "tags": ["동전주상폐", "관리종목지정", "깡통방지", "상장폐지위험"]
    },
    {
        "id": 42,
        "category": "veto_risk",
        "title": "부채비율 200% 초과 한계기업의 🔴 VETO 경보: 고금리 시대 흑자도산 방지",
        "intent": "영업이익으로 이자도 못 갚는 좀비기업을 걸러내어 내 소중한 투자금 지키기",
        "app_feature": "StockMaster AI 한계기업 흑자도산 감지",
        "app_action_mode": "veto_risk",
        "tags": ["부채비율과다", "좀비기업", "이자보상배율", "흑자도산방지"]
    },
    {
        "id": 43,
        "category": "veto_risk",
        "title": "기관 연속 순매도(블록딜/차익실현) 종목의 🔴 VETO 판독법",
        "intent": "연기금과 투신이 대량으로 물량을 털어내며 개미에게 물량을 넘기는 구간 회피",
        "app_feature": "StockMaster AI 기관 이탈 감지기",
        "app_action_mode": "veto_risk",
        "tags": ["기관이탈", "블록딜", "설거지매물", "외인기관매도"]
    },
    {
        "id": 44,
        "category": "veto_risk",
        "title": "손실을 눈덩이처럼 키우는 '본전 심리' 치료: 🔴 VETO 종목 과감히 쳐내기",
        "intent": "원금 회복에 집착하여 더 좋은 주도주로 갈아탈 기회비용을 날리지 않는 멘탈",
        "app_feature": "StockMaster AI 본전 심리 탈출 계산기",
        "app_action_mode": "veto_risk",
        "tags": ["본전심리극복", "기회비용", "종목교체", "과감한손절"]
    },
    {
        "id": 45,
        "category": "veto_risk",
        "title": "AI VETO 필터로 1년간 계좌 MDD(최대 낙폭)를 반토막 줄이는 원리",
        "intent": "대박 수익보다 더 중요한 큰 손실을 피함으로써 복리의 마법을 지키는 퀀트 철학",
        "app_feature": "StockMaster AI MDD 방어 백테스팅",
        "app_action_mode": "veto_risk",
        "tags": ["MDD방어", "최대낙폭축소", "복리의마법", "손실통제"]
    },

    # ── [4. turning_point : ✨ 변곡점·신고가 탭 & 골든크로스 (15개)] ──
    {
        "id": 46,
        "category": "turning_point",
        "title": "[✨ 변곡점] 탭의 비밀: 기나긴 하락 추세를 끝내고 턴어라운드하는 순간 포착",
        "intent": "바닥권에서 수급과 차트가 상승으로 방향을 트는 최초의 변곡점 신호 분석",
        "app_feature": "StockMaster AI [✨ 변곡점] 실시간 필터 버튼",
        "app_action_mode": "turning_point",
        "tags": ["변곡점포착", "턴어라운드", "바닥탈출", "추세반전"]
    },
    {
        "id": 47,
        "category": "turning_point",
        "title": "5일선이 20일선을 뚫고 올라서는 골든크로스(Golden Cross) 실시간 포착법",
        "intent": "단기 이동평균선이 중기선을 돌파하며 강력한 매수세가 유입되는 타이밍",
        "app_feature": "StockMaster AI 실시간 골든크로스 알림",
        "app_action_mode": "turning_point",
        "tags": ["골든크로스", "이평선돌파", "매수타이밍", "골든크로스종목"]
    },
    {
        "id": 48,
        "category": "turning_point",
        "title": "평소 거래량의 500% 폭발한 '거래량 급증' 장대양봉: 세력 매집의 결정적 증거",
        "intent": "바닥권에서 거래량이 터지며 긴 양봉이 출현할 때 세력의 진입 흔적 읽기",
        "app_feature": "StockMaster AI 거래량 급증 테스터",
        "app_action_mode": "turning_point",
        "tags": ["거래량급증", "장대양봉", "세력매집흔적", "바닥거래량"]
    },
    {
        "id": 49,
        "category": "turning_point",
        "title": "52주 신고가 돌파 종목의 매물대 공백: 위가 뻥 뚫려 거침없이 날아가는 원리",
        "intent": "과거 물려있는 악성 매물이 없어 작은 거래량으로도 신고가를 경신하는 주도주",
        "app_feature": "StockMaster AI 52주 신고가 필터",
        "app_action_mode": "turning_point",
        "tags": ["52주신고가", "매물대공백", "신고가돌파", "주도주매매"]
    },
    {
        "id": 50,
        "category": "turning_point",
        "title": "쌍바닥(이중 바닥 W자) 완성 후 [✨ 변곡점] 뜬 종목: 승률 85% 반등 매매",
        "intent": "직전 저점을 깨지 않고 두 번째 바닥을 찍고 올라서는 신뢰도 높은 차트 패턴",
        "app_feature": "StockMaster AI W자 쌍바닥 감지",
        "app_action_mode": "turning_point",
        "tags": ["이중바닥", "쌍바닥패턴", "반등매매", "차트패턴"]
    },
    {
        "id": 51,
        "category": "turning_point",
        "title": "박스권 상단 저항선을 대량 거래량으로 뚫어내는 돌파 매매의 정석",
        "intent": "수개월간 갇혀 있던 박스권을 뚫고 새로운 시세 영역으로 진입하는 종목 공략",
        "app_feature": "StockMaster AI 박스권 돌파 감지기",
        "app_action_mode": "turning_point",
        "tags": ["박스권돌파", "저항선돌파", "돌파매매", "시세분출"]
    },
    {
        "id": 52,
        "category": "turning_point",
        "title": "120일선(경기선) 바닥권 돌파 변곡점: 대형 우량주의 6개월 중장기 추세 전환",
        "intent": "경기 침체를 딛고 실적 개선과 함께 120일선을 상향 돌파하는 우량주 매수 타점",
        "app_feature": "StockMaster AI 120일선 돌파 추적기",
        "app_action_mode": "turning_point",
        "tags": ["120일선돌파", "경기선돌파", "중장기스윙", "실적턴어라운드"]
    },
    {
        "id": 53,
        "category": "turning_point",
        "title": "[✨ 변곡점] 뜬 종목 중 큰손 블록오더 유입 비중이 높은 알짜주 선별법",
        "intent": "개미들의 찔끔찔끔 매수가 아닌 기관·외인의 대량 뭉칫돈이 들어온 변곡점 종목",
        "app_feature": "StockMaster AI 블록오더 결합 변곡점",
        "app_action_mode": "turning_point",
        "tags": ["블록오더변곡점", "큰손매집", "알짜우량주", "수급변곡점"]
    },
    {
        "id": 54,
        "category": "turning_point",
        "title": "52주 신고가 돌파 종목의 -3% 트레일링 스탑 익절: 달리는 말에서 안전하게 내리기",
        "intent": "신고가 행진 중 주가가 고점 대비 3% 꺾이면 자동으로 이익을 챙기는 기법",
        "app_feature": "StockMaster AI 신고가 트레일링 스탑",
        "app_action_mode": "turning_point",
        "tags": ["신고가익절", "트레일링스탑", "달리는말", "수익보존"]
    },
    {
        "id": 55,
        "category": "turning_point",
        "title": "거래량 급증 후 거래량 마르며 3일선 지지받는 '1차 눌림목' 매수 타점",
        "intent": "급등 당일 따라붙지 않고 거래량이 급감하며 숨고르기할 때 매수하는 안전 기술",
        "app_feature": "StockMaster AI 1차 눌림목 포착",
        "app_action_mode": "turning_point",
        "tags": ["눌림목매수타점", "숨고르기", "안전한매수", "거래량급감"]
    },
    {
        "id": 56,
        "category": "turning_point",
        "title": "악재 뉴스가 쏟아진 후 첫 번째 양봉 변곡점: 역발상 매수의 승패",
        "intent": "더 이상 나빠질 게 없는 악재 소멸 구간에서 첫 양봉과 함께 수급이 도는 타이밍",
        "app_feature": "StockMaster AI 악재 소멸 변곡점",
        "app_action_mode": "turning_point",
        "tags": ["악재소멸", "역발상매수", "첫양봉", "바닥탈출"]
    },
    {
        "id": 57,
        "category": "turning_point",
        "title": "중소형 테마 대장주의 첫 52주 신고가 돌파: 2등주 버리고 대장주만 타는 법",
        "intent": "테마가 형성될 때 굼뜬 2등주, 3등주를 버리고 가장 탄력 있는 대장주를 잡는 룰",
        "app_feature": "StockMaster AI 테마 대장주 판독기",
        "app_action_mode": "turning_point",
        "tags": ["테마대장주", "52주신고가", "대장주매매", "테마주원칙"]
    },
    {
        "id": 58,
        "category": "turning_point",
        "title": "변곡점 시그널과 함께 외국인 순매수가 플러스로 전환된 종목의 파괴력",
        "intent": "연속 매도를 멈추고 외국인이 사자로 돌아서며 차트 변곡점을 만든 종목",
        "app_feature": "StockMaster AI 외인 수급 전환 변곡점",
        "app_action_mode": "turning_point",
        "tags": ["수급전환", "외인순매수전환", "변곡점시그널", "추세상승"]
    },
    {
        "id": 59,
        "category": "turning_point",
        "title": "헤드앤숄더 하락 패턴을 무력화하고 위로 솟구치는 '속임수 변곡점' 공략",
        "intent": "차트상 개미 털기 구간을 지나 직전 고점을 재돌파하는 강력한 반등 파동",
        "app_feature": "StockMaster AI 패턴 실패 반등 감지",
        "app_action_mode": "turning_point",
        "tags": ["개미털기", "속임수패턴", "강력반등", "차트속임수"]
    },
    {
        "id": 60,
        "category": "turning_point",
        "title": "매일 아침 9시 30분 [✨ 변곡점] 탭 3분 스캔으로 당일 급등주 찾는 직장인 루틴",
        "intent": "장 초반 30분 변동성이 잦아든 후 진짜 방향성을 잡는 변곡점 종목 3분 체크법",
        "app_feature": "StockMaster AI 아침 3분 변곡점 스캐너",
        "app_action_mode": "turning_point",
        "tags": ["아침3분루틴", "변곡점스캔", "직장인주식공부", "실시간체크"]
    },

    # ── [5. macro_stress : 📊 상단 매크로 스트레스 & 환율/원자재 연동 (10개)] ──
    {
        "id": 61,
        "category": "macro_stress",
        "title": "상단 [USD/KRW 환율] 실시간 연동: 환율 1,350원 돌파 시 코스피 외인 수급 공식",
        "intent": "원화 약세 시 외국인의 환차손 우려와 대형 수출주(자동차, 반도체) 수혜 명암",
        "app_feature": "StockMaster AI 상단 USD/KRW 환율 티커",
        "app_action_mode": "macro_stress",
        "tags": ["원달러환율", "외인수급영향", "수출주수혜", "환율변동성"]
    },
    {
        "id": 62,
        "category": "macro_stress",
        "title": "상단 [DXY 달러 인덱스] 105 돌파 강달러: 신흥국 증시와 한국 주가 반응",
        "intent": "글로벌 기축통화 달러 강세 시 코스피 지수의 변동성과 안전자산 쏠림 해석",
        "app_feature": "StockMaster AI DXY 달러 인덱스 티커",
        "app_action_mode": "macro_stress",
        "tags": ["달러인덱스", "강달러현상", "신흥국증시", "코스피전망"]
    },
    {
        "id": 63,
        "category": "macro_stress",
        "title": "상단 [WTI 국제 유가] 급등락: 국내 화학·정유·항공주의 실시간 실적 연동",
        "intent": "유가 상승 시 정유주 정제마진 확대와 항공·해운주의 유류비 원가 부담 분석",
        "app_feature": "StockMaster AI WTI 국제유가 티커",
        "app_action_mode": "macro_stress",
        "tags": ["국제유가WTI", "정유주수혜", "항공주리스크", "원자재주식"]
    },
    {
        "id": 64,
        "category": "macro_stress",
        "title": "상단 [GOLD 금 시세] 최고가 랠리: 인플레이션과 지정학적 위기 속 주식 비중 조절",
        "intent": "금 가격 폭등 시 주식 시장의 경계 심리와 안전자산 포트폴리오 밸런싱",
        "app_feature": "StockMaster AI GOLD 금 시세 티커",
        "app_action_mode": "macro_stress",
        "tags": ["금시세최고가", "안전자산선호", "인플레이션헤지", "자산배분"]
    },
    {
        "id": 65,
        "category": "macro_stress",
        "title": "[시장 매크로 스트레스 지수] 5점(안정) vs 80점(위험): 구간별 내 현금 비중 세팅법",
        "intent": "AI가 산출하는 매크로 스트레스 점수에 따라 주식 100% vs 현금 50% 유동적 배분",
        "app_feature": "StockMaster AI 시장 매크로 스트레스 게이지",
        "app_action_mode": "macro_stress",
        "tags": ["매크로스트레스", "현금비중조절", "시장위험도", "계좌자산배분"]
    },
    {
        "id": 66,
        "category": "macro_stress",
        "title": "매크로 스트레스 지수가 '극단적 공포(80점+)'일 때 역발상 분할 매수의 기술",
        "intent": "모두가 패닉에 빠져 투매할 때 우량 대형주를 헐값에 주워 담는 워런 버핏식 매수",
        "app_feature": "StockMaster AI 극단적 공포 역발상 알림",
        "app_action_mode": "macro_stress",
        "tags": ["극단적공포", "역발상투자", "패닉셀매수", "바닥줍기"]
    },
    {
        "id": 67,
        "category": "macro_stress",
        "title": "환율 급등기에 주가 방어력이 가장 높은 국내 고배당주·인프라주 선별법",
        "intent": "원화 가치 하락에도 안정적인 내수 현금 흐름과 고배당을 주는 맥쿼리인프라 등 분석",
        "app_feature": "StockMaster AI 고배당 방어주 스크리너",
        "app_action_mode": "macro_stress",
        "tags": ["환율급등방어주", "고배당인프라", "맥쿼리인프라", "현금흐름주"]
    },
    {
        "id": 68,
        "category": "macro_stress",
        "title": "코스피 NOW vs 코스닥 NOW 등락률 비교: 대형주 장세인가 개별 테마주 장세인가?",
        "intent": "두 지수의 상대 강도를 비교하여 오늘은 대형주를 탈지 중소형주를 탈지 결정하는 법",
        "app_feature": "StockMaster AI 양대 지수 실시간 비교표",
        "app_action_mode": "macro_stress",
        "tags": ["코스피NOW", "코스닥NOW", "장세판단", "대형주vs중소형주"]
    },
    {
        "id": 69,
        "category": "macro_stress",
        "title": "한국은행 금융통화위원회 기준금리 인하 시 국내 증시와 바이오·성장주 수혜",
        "intent": "시중 유동성 공급과 할인율 하락으로 탄력을 받는 코스닥 성장주 매매 전략",
        "app_feature": "StockMaster AI 금리 인하 수혜주 분석",
        "app_action_mode": "macro_stress",
        "tags": ["한국은행금통위", "기준금리인하", "바이오수혜주", "성장주투자"]
    },
    {
        "id": 70,
        "category": "macro_stress",
        "title": "장 시작 전 5개 매크로 지표로 오늘 코스피 시초가 방향성 1분 만에 예측하기",
        "intent": "환율, 유가, 야간선물, 달러지수를 종합하여 갭상승/갭하락 사전 대비하기",
        "app_feature": "StockMaster AI 모닝 매크로 요약",
        "app_action_mode": "macro_stress",
        "tags": ["시초가예측", "모닝브리핑", "야간선물지수", "장전체크"]
    },

    # ── [6. price_boundary : 🎯 손절선(SL)·목표선(TP) 가격 타점 (15개)] ──
    {
        "id": 71,
        "category": "price_boundary",
        "title": "주관적 감정을 100% 배제한 ATR(변동성) 기반 과학적 청산 손절선(EXIT SL) 산출법",
        "intent": "종목의 최근 14일 일일 변동 폭을 수학적으로 계산하여 최적의 손절가를 잡는 룰",
        "app_feature": "StockMaster AI ATR 기반 청산 손절선 카드",
        "app_action_mode": "price_boundary",
        "tags": ["ATR손절선", "과학적손절", "변동성계산", "기계적매매"]
    },
    {
        "id": 72,
        "category": "price_boundary",
        "title": "현재가 기준 스윙 목표선(SWING TP) 달성 확률: 욕심부리지 않고 파는 수학적 목표가",
        "intent": "상단 저항 매물대와 평균 상승 파동 폭을 반영한 1차 스윙 목표 가격 제시",
        "app_feature": "StockMaster AI 스윙 목표선(SWING TP)",
        "app_action_mode": "price_boundary",
        "tags": ["스윙목표선", "목표가산출", "적정목표수익", "수익실현"]
    },
    {
        "id": 73,
        "category": "price_boundary",
        "title": "손익비 1:2 원칙: -3% 잃을 때 +6% 이상 버는 자리에서만 베팅하는 법",
        "intent": "승률이 50%에 불과해도 계좌가 우상향하는 손익비(Risk-Reward Ratio) 세팅 기술",
        "app_feature": "StockMaster AI 손익비 시뮬레이터",
        "app_action_mode": "price_boundary",
        "tags": ["손익비1대2", "리스크리워드", "승률보다손익비", "계좌우상향"]
    },
    {
        "id": 74,
        "category": "price_boundary",
        "title": "주요 지지선 바로 1호가 아래 청산 손절선을 걸어두는 실전 기술",
        "intent": "지지선이 깨지면 투매가 쏟아지는 지점을 파악하여 최소 손실로 빠져나오는 법",
        "app_feature": "StockMaster AI 주요 지지선 분석",
        "app_action_mode": "price_boundary",
        "tags": ["지지선손절", "손실최소화", "호가창손절", "스탑로스주문"]
    },
    {
        "id": 75,
        "category": "price_boundary",
        "title": "전고점 돌파 종목의 1차 목표선과 2차 마디가 목표선 설정법",
        "intent": "전고점을 뚫은 후 라운드 피겨(1만 원, 5만 원, 10만 원) 마디가에서 분할 익절",
        "app_feature": "StockMaster AI 라운드피겨 목표선",
        "app_action_mode": "price_boundary",
        "tags": ["라운드피겨", "전고점돌파목표가", "마디가익절", "분할매도"]
    },
    {
        "id": 76,
        "category": "price_boundary",
        "title": "분할 매수 3단계 진입 시 최종 평단가에 맞춘 손절선 재조정 공식",
        "intent": "1차 30%, 2차 30%, 3차 40% 매수 후 최종 평단가 대비 -3% 라인 재설정",
        "app_feature": "StockMaster AI 분할 매수 평단가 계산기",
        "app_action_mode": "price_boundary",
        "tags": ["분할매수손절선", "평단가재조정", "비중조절", "체계적매매"]
    },
    {
        "id": 77,
        "category": "price_boundary",
        "title": "장중 돌발 악재로 손절선 터치 시 망설임 없이 '시장가 매도'를 치는 마인드셋",
        "intent": "'조금만 반등하면 팔아야지' 하다가 -20% 물리는 뇌의 인지 부조화 극복법",
        "app_feature": "StockMaster AI 손절 마인드셋 가이드",
        "app_action_mode": "price_boundary",
        "tags": ["시장가매도", "망설임없는손절", "인지부조화극복", "원칙매매"]
    },
    {
        "id": 78,
        "category": "price_boundary",
        "title": "스윙 목표선 근처에서 대량 거래량 터질 때: 전량 매도 vs 절반 익절 후 홀딩",
        "intent": "목표가 부근에서 거래량이 폭발할 때 세력의 털기인지 추가 돌파인지 판별하는 법",
        "app_feature": "StockMaster AI 목표가 거래량 판독기",
        "app_action_mode": "price_boundary",
        "tags": ["목표가거래량", "전량매도vs절반익절", "세력털기구별", "수익보존"]
    },
    {
        "id": 79,
        "category": "price_boundary",
        "title": "주가가 올라갈 때마다 손절선을 끌어올리는 '수익 보존 손절선(Trailing SL)' 세팅",
        "intent": "매수가 위에 손절선을 올려두어 어떤 경우에도 손실을 보지 않는 방탄 매매법",
        "app_feature": "StockMaster AI 트레일링 손절선 가이드",
        "app_action_mode": "price_boundary",
        "tags": ["트레일링손절선", "노리스크매매", "수익보존", "원금보장전략"]
    },
    {
        "id": 80,
        "category": "price_boundary",
        "title": "단기 단타(3% 손절) vs 중기 스윙(7% 손절): 내 투자 성향에 맞는 손절폭 최적화",
        "intent": "보유 기간과 종목 변동성에 따라 손절폭을 차등 적용하여 억울한 털림 방지",
        "app_feature": "StockMaster AI 투자 성향별 손절폭 추천",
        "app_action_mode": "price_boundary",
        "tags": ["단타손절3%", "스윙손절7%", "손절폭최적화", "투자성향매매"]
    },
    {
        "id": 81,
        "category": "price_boundary",
        "title": "코스피 대형 우량주에 맞는 넉넉한 손절선과 현실적인 스윙 목표가(3~5%)",
        "intent": "삼성전자, 현대차 등 대형주는 변동 폭이 작으므로 잔파동에 털리지 않는 타점",
        "app_feature": "StockMaster AI 대형주 전용 타점 가이드",
        "app_action_mode": "price_boundary",
        "tags": ["대형주타점", "삼성전자목표가", "대형주손절선", "안정적스윙"]
    },
    {
        "id": 82,
        "category": "price_boundary",
        "title": "코스닥 급등 테마주에 맞는 타이트한 -2~3% 칼손절선 절대 규칙",
        "intent": "변동성이 큰 테마주는 손절 타이밍을 놓치면 하루 만에 -15% 물리므로 칼손절 필수",
        "app_feature": "StockMaster AI 테마주 칼손절 알림",
        "app_action_mode": "price_boundary",
        "tags": ["코스닥칼손절", "테마주손절선", "단타생존법", "빠른손절"]
    },
    {
        "id": 83,
        "category": "price_boundary",
        "title": "손절 후 주가가 다시 지지선을 회복할 때 억울해하지 않고 '재진입'하는 기술",
        "intent": "손절은 보험료일 뿐, 추세가 다시 살아나면 감정을 버리고 다시 매수하는 프로의 자세",
        "app_feature": "StockMaster AI 재진입 시그널 감지",
        "app_action_mode": "price_boundary",
        "tags": ["재진입기술", "감정배제매매", "손절은보험", "프로의매매"]
    },
    {
        "id": 84,
        "category": "price_boundary",
        "title": "물타기로 계좌 묶이지 말고 손절 후 새로운 전광판 1위로 갈아타는 기회비용 계산",
        "intent": "6개월간 -30% 물려있는 돈을 빼서 5%씩 6번 회전시켜 계좌를 복구하는 수학",
        "app_feature": "StockMaster AI 기회비용 복구 시뮬레이션",
        "app_action_mode": "price_boundary",
        "tags": ["기회비용복구", "종목교체매매", "계좌회전율", "물타기탈출"]
    },
    {
        "id": 85,
        "category": "price_boundary",
        "title": "AI가 제시하는 손절선·목표선으로 증권사 HTS '자동 감시 주문(스탑로스)' 걸기",
        "intent": "장중에 컴퓨터를 보지 않아도 목표가에 자동 익절, 손절가에 자동 매도되는 세팅",
        "app_feature": "StockMaster AI HTS 자동감시주문 가이드",
        "app_action_mode": "price_boundary",
        "tags": ["자동감시주문", "HTS스탑로스세팅", "무인자동매매", "직장인주식자동화"]
    },

    # ── [7. quant_guide : 💡 8대 퀀트 리스크 가이드 & 건전성 진단 (15개)] ──
    {
        "id": 86,
        "category": "quant_guide",
        "title": "8대 지표 ① [체결강도 120%]와 [체결가속도 +%p]의 완벽한 구분과 실전 활용",
        "intent": "단순 체결강도와 속도 변화를 결합해 장중 진짜 힘이 붙는 종목 판별",
        "app_feature": "StockMaster AI 8대 퀀트 가이드 모달",
        "app_action_mode": "quant_guide",
        "tags": ["체결강도원리", "체결가속도차이", "8대지표가이드", "계량지표공부"]
    },
    {
        "id": 87,
        "category": "quant_guide",
        "title": "8대 지표 ② [블록오더(큰손 대량 체결) 비중]: 70%를 넘어야 진짜 세력주인 이유",
        "intent": "개미들의 소액 주문을 발라내고 기관·외인의 대량 묶음 주문 비중 계산법",
        "app_feature": "StockMaster AI 블록오더 가이드",
        "app_action_mode": "quant_guide",
        "tags": ["블록오더비중", "세력주판별", "대형체결분석", "수급지표"]
    },
    {
        "id": 88,
        "category": "quant_guide",
        "title": "8대 지표 ③ [외국계 순매수액]: 검은 머리 외국인 거르고 진짜 메이저 외인 읽기",
        "intent": "외국계 증권사 창구 매매와 프로그램 비차익 순매수의 진성 수급 검증",
        "app_feature": "StockMaster AI 진성 외인 수급 판별",
        "app_action_mode": "quant_guide",
        "tags": ["외국계순매수", "진성외인수급", "프로그램비차익", "창구분석"]
    },
    {
        "id": 89,
        "category": "quant_guide",
        "title": "8대 지표 ④ [공매도 비중]과 숏스퀴즈(Short Squeeze): 공매도 상환 폭등주",
        "intent": "공매도 잔고가 많은 종목에서 호재가 터졌을 때 기관이 숏을 청산하며 폭등하는 원리",
        "app_feature": "StockMaster AI 공매도 숏스퀴즈 감지",
        "app_action_mode": "quant_guide",
        "tags": ["공매도비중", "숏스퀴즈", "숏커버링폭등", "공매도잔고"]
    },
    {
        "id": 90,
        "category": "quant_guide",
        "title": "8대 지표 ⑤ [신용잔고율]: 개미 빚투가 5% 넘는 종목이 무거운 이유",
        "intent": "신용 매수 물량이 많으면 상단 매물대가 두터워 주가가 탄력을 받지 못하는 매커니즘",
        "app_feature": "StockMaster AI 신용잔고율 분석",
        "app_action_mode": "quant_guide",
        "tags": ["신용잔고율분석", "빚투종목회피", "매물대부담", "가벼운종목"]
    },
    {
        "id": 91,
        "category": "quant_guide",
        "title": "8대 지표 ⑥ [ROE(자기자본이익률) 15% 룰]: 워런 버핏이 극찬한 돈 잘 버는 기업",
        "intent": "자본 대비 매년 15% 이상 순이익을 내며 복리로 성장하는 대한민국 우량주",
        "app_feature": "StockMaster AI ROE 15% 스크리너",
        "app_action_mode": "quant_guide",
        "tags": ["ROE15퍼센트", "워런버핏투자법", "복리성장주", "우량기업발굴"]
    },
    {
        "id": 92,
        "category": "quant_guide",
        "title": "8대 지표 ⑦ [PBR 1배 미만]: 정부 기업 밸류업 프로그램 인증 저평가주",
        "intent": "순자산 대비 저평가되어 자사주 소각 및 배당 확대 시 주가 리레이팅되는 종목",
        "app_feature": "StockMaster AI 저PBR 밸류업 진단",
        "app_action_mode": "quant_guide",
        "tags": ["저PBR밸류업", "자사주소각", "주주환원율", "기업가치제고"]
    },
    {
        "id": 93,
        "category": "quant_guide",
        "title": "8대 지표 ⑧ [부채비율 100% 미만 & 유보율 1,000%]: 상장폐지 걱정 없는 무차입 경영",
        "intent": "사내 현금이 넘쳐나 고금리 위기에도 끄떡없는 무차입 초우량 기업 선별법",
        "app_feature": "StockMaster AI 무차입 경영 우량주",
        "app_action_mode": "quant_guide",
        "tags": ["부채비율100미만", "유보율1000", "무차입경영", "상폐위험제로"]
    },
    {
        "id": 94,
        "category": "quant_guide",
        "title": "DART 전자공시 전환사채(CB) 3단 폭탄: 리픽싱(행사가액 조정)으로 개미 털어먹는 구조",
        "intent": "사채업자와 대주주가 주가를 억누르며 주식으로 전환하는 부실 작전주 피하기",
        "app_feature": "StockMaster AI DART CB 리픽싱 감지",
        "app_action_mode": "quant_guide",
        "tags": ["전환사채CB", "리픽싱함정", "작전주회피", "DART공시분석"]
    },
    {
        "id": 95,
        "category": "quant_guide",
        "title": "유상증자 공시 판독법: 주주배정(악재 폭탄) vs 제3자배정 대기업 투자(호재 잭팟)",
        "intent": "공시 제목만 보고 던질지 살지 3초 만에 판단하는 실전 공시 독해법",
        "app_feature": "StockMaster AI 유상증자 호악재 판독",
        "app_action_mode": "quant_guide",
        "tags": ["유상증자공시", "주주배정유증", "제3자배정유증", "공시독해법"]
    },
    {
        "id": 96,
        "category": "quant_guide",
        "title": "배당수익률 연 6% 이상 국내 고배당주의 배당락일 전후 퀀트 점수 변화",
        "intent": "금융지주·맥쿼리인프라 등 고배당주의 배당금 확보와 주가 회복 기간 시뮬레이션",
        "app_feature": "StockMaster AI 고배당 퀀트 시뮬레이터",
        "app_action_mode": "quant_guide",
        "tags": ["고배당수익률", "배당락일시뮬레이션", "금융지주배당", "배당재투자"]
    },
    {
        "id": 97,
        "category": "quant_guide",
        "title": "잉여현금흐름(FCF, Free Cash Flow) 플러스 기업: 가짜 장부상 이익에 속지 않는 법",
        "intent": "영업활동으로 실제 통장에 현금이 꽂히는 진짜 흑자 기업을 찾는 퀀트 비법",
        "app_feature": "StockMaster AI FCF 현금흐름 스크리너",
        "app_action_mode": "quant_guide",
        "tags": ["잉여현금흐름FCF", "진짜흑자기업", "현금흐름표", "장부상이익구별"]
    },
    {
        "id": 98,
        "category": "quant_guide",
        "title": "대표이사 및 임원 자사주 장내 매수 공시 시 AI 퀀트 점수 대폭 상향 원리",
        "intent": "회사 내부 사정을 가장 잘 아는 CEO가 자기 돈으로 주식을 살 때의 강력한 바닥 신호",
        "app_feature": "StockMaster AI 임원 자사주 매수 감지",
        "app_action_mode": "quant_guide",
        "tags": ["자사주장내매수", "내부자거래공시", "바닥신호", "CEO매수"]
    },
    {
        "id": 99,
        "category": "quant_guide",
        "title": "퇴근 후 10분, 8대 퀀트 지표로 내 보유 종목 종합 건강검진 하기",
        "intent": "내가 가진 종목이 진입유효인지, VETO 위험에 처했는지 매일 밤 10분 셀프 체크",
        "app_feature": "StockMaster AI 10분 종합 종목 건강검진",
        "app_action_mode": "quant_guide",
        "tags": ["종목건강검진", "퇴근후10분", "포트폴리오점검", "보유종목진단"]
    },
    {
        "id": 100,
        "category": "quant_guide",
        "title": "StockMaster AI 4단계 파이프라인 총정리: 감정 매매 끝, 데이터로 증명하는 승리",
        "intent": "스크리닝 ➔ RAG 백테스트 오답노트 ➔ VETO 필터 ➔ 최적 타점 도출의 풀 파이프라인",
        "app_feature": "StockMaster AI 전체 퀀트 파이프라인",
        "app_action_mode": "quant_guide",
        "tags": ["StockMasterAI", "4단계파이프라인", "퀀트투자원칙", "데이터기반주식"]
    }
]


def get_all_topics() -> List[Dict[str, Any]]:
    return STOCK_100_TOPICS


def get_topic_by_id(topic_id: int) -> Dict[str, Any]:
    for t in STOCK_100_TOPICS:
        if t["id"] == topic_id:
            return t
    return STOCK_100_TOPICS[0]


def get_topics_by_category(category: str) -> List[Dict[str, Any]]:
    return [t for t in STOCK_100_TOPICS if t["category"] == category]


def get_interleaved_topic_order() -> List[int]:
    """
    7대 카테고리를 골고루 1개씩 교차 순환(인터리빙)하는 100개 토픽 ID 리스트 반환
    - [realtime_rank1, valid_entry, veto_risk, turning_point, macro_stress, price_boundary, quant_guide] 순환
    - 특정 카테고리가 며칠 연속으로 쏠리는 현상 100% 원천 차단
    """
    categories = [
        "realtime_rank1",
        "valid_entry",
        "veto_risk",
        "turning_point",
        "macro_stress",
        "price_boundary",
        "quant_guide"
    ]
    pools: Dict[str, List[int]] = {cat: [] for cat in categories}
    for t in STOCK_100_TOPICS:
        cat = t["category"]
        if cat in pools:
            pools[cat].append(t["id"])

    interleaved = []
    max_len = max(len(p) for p in pools.values())
    for i in range(max_len):
        for cat in categories:
            if i < len(pools[cat]):
                interleaved.append(pools[cat][i])

    return interleaved


if __name__ == "__main__":
    print(f"📈 [StockMaster 100대 주제 풀 로드] 총 {len(STOCK_100_TOPICS)}개")
    order = get_interleaved_topic_order()
    print(f"🔄 인터리빙 순환 순서 (총 {len(order)}개): {order[:14]}...")
