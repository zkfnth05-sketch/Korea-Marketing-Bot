# -*- coding: utf-8 -*-
"""
📈 StockMaster 100대 마스터 토픽 풀 (100 Master Topics Pool)
============================================================
- 브랜드: StockMaster AI (주식 AI 분석 & 퀀트 & 포트폴리오 & 뇌동매매 방지)
- 타깃: 2040 스마트 서학개미·동학개미, 직장인 적립식 투자자, AI 퀀트 관심자
- 6대 핵심 카테고리:
  1. korea_market     : 국내 대형주 / 반도체(삼성전자·SK하이닉스) / 밸류업 저PBR / 2차전지
  2. us_dividend_tech : 미국 배당성장주(SCHD·O·JEPQ) / 빅테크 M7(엔비디아·애플) / 절세
  3. etf_index        : 지수 추종 ETF(S&P 500·나스닥100) / 채권 ETF / 월적립식 복리
  4. macro_economy    : 미국 연준(Fed) FOMC 금리 / 원달러 환율 / CPI 물가지표 / 경기침체
  5. chart_financials : 초보 재무제표(PER·PBR·ROE) / 이동평균선 / 지지·저항선 / DART 공시
  6. quant_risk       : 뇌동매매 방지 멘탈 / 손절매 기준 / AI 퀀트 알고리즘 / 자산배분
"""

from typing import List, Dict, Any, Optional

STOCK_100_TOPICS: List[Dict[str, Any]] = [
    # ── [카테고리 1: korea_market (국내 대형주 / 반도체 / 밸류업 / 섹터)] ──
    {
        "id": 1,
        "category": "korea_market",
        "title": "삼성전자 vs SK하이닉스: HBM(고대역폭 메모리) 승부처와 AI 반도체 수혜주",
        "intent": "HBM3E 납품 경쟁과 엔비디아 밸류체인 속 두 기업의 실적 및 밸류에이션 비교",
        "app_feature": "StockMaster AI 반도체 수급 레이더",
        "tags": ["삼성전자주가", "SK하이닉스HBM", "AI반도체주", "국내주식전망"]
    },
    {
        "id": 2,
        "category": "korea_market",
        "title": "정부 밸류업 프로그램 저PBR 수혜주: 금융지주·지주사 배당 확대 분석",
        "intent": "PBR 1배 미만 기업들의 자사주 소각 및 주주환원율 상향이 주가에 미치는 영향",
        "app_feature": "StockMaster 저PBR 밸류업 스크리너",
        "tags": ["기업밸류업", "저PBR관련주", "금융주배당", "주주환원율"]
    },
    {
        "id": 3,
        "category": "korea_market",
        "title": "2차전지 양극재 기업 주가 반등 조건: 전기차 캐즘(Chasm) 탈출 시점은 언제?",
        "intent": "에코프로, 포스코퓨처엠 등 양극재 기업의 리튬 가격 연동 실적 턴어라운드 전망",
        "app_feature": "StockMaster 2차전지 밸류체인 진단",
        "tags": ["2차전지주가", "에코프로전망", "전기차캐즘", "리튬가격"]
    },
    {
        "id": 4,
        "category": "korea_market",
        "title": "K-방산 빅4(한화에어로·현대로템·KAI·LIG넥스원) 수주 잔고 100조의 의미",
        "intent": "유럽 및 중동 수출 계약과 글로벌 지정학적 리스크 속 방산주의 실적 지속성",
        "app_feature": "StockMaster 방산 섹터 모멘텀 리포트",
        "tags": ["방산주추천", "한화에어로스페이스", "현대로템수주", "K방산전망"]
    },
    {
        "id": 5,
        "category": "korea_market",
        "title": "바이오/제약 임상 성공과 주가 폭등의 명암: 유한양행 레이저티닙 FDA 승인 교훈",
        "intent": "신약 개발 기술수출(L/O) 계약 구조와 임상 3상 데이터 해석하는 노하우",
        "app_feature": "StockMaster 바이오 파이프라인 분석기",
        "tags": ["바이오주투자", "유한양행렉라자", "신약임상성공", "제약바이오전망"]
    },
    {
        "id": 6,
        "category": "korea_market",
        "title": "조선주 슈퍼사이클 도래: 친환경 LNG선 수주와 카타르 프로젝트 수혜",
        "intent": "HD현대중공업, 삼성중공업, 한화오션 3사의 신조선가 지수 상승 및 흑자 전환",
        "app_feature": "StockMaster 조선 업황 트래커",
        "tags": ["조선주슈퍼사이클", "HD현대중공업", "신조선가지수", "LNG선수주"]
    },
    {
        "id": 7,
        "category": "korea_market",
        "title": "자동차 현대차·기아 호실적에도 주가 저평가된 이유: 하이브리드 vs EV 전략",
        "intent": "역대 최대 영업이익 달성 배경과 글로벌 완성차 밸류에이션 리레이팅 가능성",
        "app_feature": "StockMaster 현대차 기아 적정주가 계산기",
        "tags": ["현대차주가", "기아배당", "하이브리드차수혜", "자동차주전망"]
    },
    {
        "id": 8,
        "category": "korea_market",
        "title": "공모주 청약(IPO) 상장 첫날 따따블(400%) 매도 전략: 기관 의무보유확약 비율 확인",
        "intent": "수요예측 결과표에서 경쟁률과 확약 비율을 분석해 첫날 차익 실현하는 방법",
        "app_feature": "StockMaster 공모주 청약 알림 & 분석",
        "tags": ["공모주청약", "IPO따따블", "기관의무보유확약", "공모주매도타이밍"]
    },
    {
        "id": 9,
        "category": "korea_market",
        "title": "외국인·기관 순매수 수급 추종 매매법: 검은 머리 외국인 거르는 필터링 팁",
        "intent": "프로그램 매매와 대차잔고 추이, 연기금 연속 순매수 종목 포착 공식",
        "app_feature": "StockMaster 실시간 수급 포착기",
        "tags": ["외국인순매수", "기관수급주", "연기금매수종목", "수급매매기법"]
    },
    {
        "id": 10,
        "category": "korea_market",
        "title": "금투세(금융투자소득세) 폐지 논란과 연말 대주주 양도세 50억원 회피 물량",
        "intent": "12월 결산법인 배당락일 전후 큰손들의 매도 패턴과 1월 효과(January Effect)",
        "app_feature": "StockMaster 연말 세금 이벤트 대응 캘린더",
        "tags": ["금투세폐지", "대주주양도세", "1월효과", "배당락일매매"]
    },
    {
        "id": 11,
        "category": "korea_market",
        "title": "원자력 발전(K-원전) 체코 수주 잭팟: 두산에너빌리티와 한전기술 수혜 분석",
        "intent": "SMR(소형 모듈 원자로) 시장 개화와 글로벌 탈탄소 원전 르네상스 투자",
        "app_feature": "StockMaster 원전 섹터 밸류체인 지도",
        "tags": ["체코원전수주", "두산에너빌리티", "SMR관련주", "원자력테마주"]
    },
    {
        "id": 12,
        "category": "korea_market",
        "title": "전력기기·변압기(HD현대일렉트릭, 효성중공업) 미국 AI 데이터센터 전력망 특수",
        "intent": "AI 데이터센터 전력 소비 폭증으로 인한 노후 전력망 교체 슈퍼사이클",
        "app_feature": "StockMaster AI 전력망 인프라 분석",
        "tags": ["전력기기대장주", "HD현대일렉트릭", "변압기수출", "AI데이터센터전력"]
    },
    {
        "id": 13,
        "category": "korea_market",
        "title": "엔터주(하이브, SM, JYP) 실적 바닥 찍었을까? 신인 아이돌 데뷔와 음원 IP 가치",
        "intent": "멀티레이블 리스크 극복과 글로벌 팬덤 플랫폼(위버스 등) 수익 다각화 점검",
        "app_feature": "StockMaster K-엔터 IP 모멘텀 진단",
        "tags": ["엔터주투자", "하이브주가", "JYP실적", "KPOP관련주"]
    },
    {
        "id": 14,
        "category": "korea_market",
        "title": "게임주 신작 모멘텀 매매법: 출시 1달 전 매도해야 수익 나는 공식",
        "intent": "사전 예약자 수와 출시 당일 앱스토어 매출 순위가 주가에 미치는 전형적 패턴",
        "app_feature": "StockMaster 게임 신작 캘린더 분석",
        "tags": ["게임주매매전략", "신작모멘텀", "게임대장주", "크래프톤엔씨소프트"]
    },
    {
        "id": 15,
        "category": "korea_market",
        "title": "화장품 OEM/ODM(한국콜마, 코스맥스) 미국 아마존 인디 브랜드 열풍 수혜",
        "intent": "올리브영 및 북미 수출 급증으로 사상 최대 실적 행진을 이어가는 화장품주",
        "app_feature": "StockMaster K-뷰티 수출 데이터 분석",
        "tags": ["화장품관련주", "한국콜마", "코스맥스", "인디뷰티수출"]
    },
    {
        "id": 16,
        "category": "korea_market",
        "title": "음식료주 불닭볶음면 삼양식품 주가 10배 폭등의 비결: 글로벌 K-푸드 수출 분석",
        "intent": "내수 중심 산업에서 해외 매출 비중 70% 돌파 기업으로 탈바꿈한 밸류에이션 재평가",
        "app_feature": "StockMaster K-푸드 수출액 트래커",
        "tags": ["삼양식품불닭", "K푸드수출", "음식료주식", "해외수출성장주"]
    },

    # ── [카테고리 2: us_dividend_tech (미국 배당주 / 빅테크 M7 / 절세)] ──
    {
        "id": 17,
        "category": "us_dividend_tech",
        "title": "SCHD(슈드) vs JEPI(제피) 배당 ETF 비교: 월배당 파이프라인 누구를 담아야 할까?",
        "intent": "배당 성장률 중심의 SCHD와 고배당 커버드콜 JEPI의 연령대별 최적 포트폴리오",
        "app_feature": "StockMaster 배당 ETF 백테스팅 계산기",
        "tags": ["SCHD배당금", "JEPI월배당", "미국배당ETF", "배당성장주"]
    },
    {
        "id": 18,
        "category": "us_dividend_tech",
        "title": "엔비디아(NVDA) 독점 붕괴될까? 빅테크 자체 AI 칩(커스텀 ASIC) 개발 경쟁",
        "intent": "블랙웰(Blackwell) 아키텍처 출시와 빅테크 CAPEX(설비투자) 증가세 지속 여부",
        "app_feature": "StockMaster 엔비디아 AI 생태계 분석",
        "tags": ["엔비디아주가", "NVDA실적", "AI반도체독점", "빅테크CAPEX"]
    },
    {
        "id": 19,
        "category": "us_dividend_tech",
        "title": "미국주식 양도소득세 250만원 공제 100% 활용법: 손실 종목 손익통산과 양도세 절세",
        "intent": "연말 마이너스 수익률 종목을 매도 후 재매수하여 양도세 22% 합법적으로 줄이기",
        "app_feature": "StockMaster 미국주식 양도세 절세 시뮬레이터",
        "tags": ["미국주식양도세", "250만원공제", "손익통산절세", "해외주식세금"]
    },
    {
        "id": 20,
        "category": "us_dividend_tech",
        "title": "마이크로소프트(MSFT)와 오픈AI: B2B 클라우드 애저(Azure) 수익화 가속도",
        "intent": "코파일럿(Copilot) 유료 구독 모델 안착과 엔터프라이즈 AI 시장 점유율 분석",
        "app_feature": "StockMaster 빅테크 B2B AI 진단",
        "tags": ["마이크로소프트주가", "오픈AI수혜주", "애저클라우드", "코파일럿수익"]
    },
    {
        "id": 21,
        "category": "us_dividend_tech",
        "title": "애플(AAPL) 애플 인텔리전스(Apple Intelligence) 출시와 아이폰 교체 슈퍼사이클",
        "intent": "온디바이스 AI 탑재 신형 기기 출시가 서비스 부문 및 하드웨어 매출에 미치는 파급력",
        "app_feature": "StockMaster 애플 온디바이스 AI 리포트",
        "tags": ["애플주가전망", "애플인텔리전스", "아이폰교체주기", "온디바이스AI"]
    },
    {
        "id": 22,
        "category": "us_dividend_tech",
        "title": "리얼티인컴(O) 월배당 리츠(REITs): 미국 상업용 부동산 위기에도 든든한 이유",
        "intent": "월마트, 세븐일레븐 등 트리플 넷 리스(NNN) 구조와 금리 인하기 리츠 주가 탄력성",
        "app_feature": "StockMaster 미국 리츠 배당 진단",
        "tags": ["리얼티인컴배당", "미국월배당주", "상업용부동산리츠", "배당귀족주"]
    },
    {
        "id": 23,
        "category": "us_dividend_tech",
        "title": "테슬라(TSLA) 로보택시와 FSD(완전자율주행): 단순 자동차 회사가 아닌 AI 로봇 기업",
        "intent": "옵티머스 휴머노이드 로봇 상용화 로드맵과 자율주행 소프트웨어 구독 매출 비중",
        "app_feature": "StockMaster 테슬라 AI 밸류에이션",
        "tags": ["테슬라로보택시", "FSD완전자율주행", "옵티머스로봇", "TSLA주가전망"]
    },
    {
        "id": 24,
        "category": "us_dividend_tech",
        "title": "알파벳(구글 GOOGL) 검색 독점 반독점 소송 리스크와 제미나이(Gemini) AI 역습",
        "intent": "미 법무부 크롬/안드로이드 분할 요구 리스크와 유튜브 쇼츠 및 클라우드 실적 성장",
        "app_feature": "StockMaster 구글 반독점 리스크 진단",
        "tags": ["구글주가전망", "알파벳반독점", "제미나이AI", "유튜브광고수익"]
    },
    {
        "id": 25,
        "category": "us_dividend_tech",
        "title": "메타(META) 라마(Llama) 오픈소스 AI 전략과 맞춤형 디지털 광고 회복",
        "intent": "스마트 안경(레이밴 메타)의 폭발적 반응과 메타버스 투자 적자 폭 축소",
        "app_feature": "StockMaster 메타 AI 광고 수익성 분석",
        "tags": ["메타플랫폼스주가", "라마오픈소스", "스마트글래스", "디지털광고수혜"]
    },
    {
        "id": 26,
        "category": "us_dividend_tech",
        "title": "아마존(AMZN) AWS 클라우드 성장 재가속과 프라임 리테일 물류 효율화",
        "intent": "자체 AI 가속기 칩 트레이니엄(Trainium) 도입과 클라우드 영업이익률 개선",
        "app_feature": "StockMaster 아마존 클라우드 리포트",
        "tags": ["아마존주가", "AWS클라우드실적", "트레이니엄칩", "이커머스마진"]
    },
    {
        "id": 27,
        "category": "us_dividend_tech",
        "title": "배당 귀족주(50년 연속 배당 인상): 코카콜라(KO), 존슨앤존슨(JNJ), 프록터앤갬블(PG)",
        "intent": "경기 침체에도 끄떡없는 필수소비재 글로벌 1위 기업들의 인플레이션 방어력",
        "app_feature": "StockMaster 배당 귀족주 포트폴리오",
        "tags": ["배당귀족주", "코카콜라배당금", "존슨앤존슨", "필수소비재투자"]
    },
    {
        "id": 28,
        "category": "us_dividend_tech",
        "title": "JEPQ(나스닥 고배당 커버드콜): 연 9~11% 월배당 받으며 원금 깎아먹지 않는 전략",
        "intent": "커버드콜 옵션 프리미엄 원리와 나스닥 횡보장·상승장에서의 실질 수익률 비교",
        "app_feature": "StockMaster 커버드콜 옵션 위험 진단",
        "tags": ["JEPQ배당금", "커버드콜원리", "고배당월배당", "나스닥배당ETF"]
    },
    {
        "id": 29,
        "category": "us_dividend_tech",
        "title": "미국 배당소득세(15.4%) 원천징수와 종합소득세 금융소득종합과세(2,000만원) 기준",
        "intent": "배당금 연 2,000만원 초과 시 다른 소득과 합산 과세되는 세금 함정 피하기",
        "app_feature": "StockMaster 금융소득종합과세 계산기",
        "tags": ["배당소득세15.4", "금융소득종합과세", "배당금2천만원", "절세계좌활용"]
    },
    {
        "id": 30,
        "category": "us_dividend_tech",
        "title": "일라이릴리(LLY) 비만치료제(마운자로/젭바운드) 제약업계 최초 시총 1조 달러 도전",
        "intent": "노보노디스크(위고비)와의 비만약 패권 경쟁과 심혈관·수면무호흡증 적응증 확대",
        "app_feature": "StockMaster 비만치료제 파이프라인 진단",
        "tags": ["일라이릴리주가", "비만치료제수혜주", "마운자로위고비", "GLP1관련주"]
    },
    {
        "id": 31,
        "category": "us_dividend_tech",
        "title": "버크셔 해서웨이(워런 버핏) 현금 보유액 사상 최대 3,000억 달러: 대폭락 전조?",
        "intent": "버핏이 애플과 뱅크오브아메리카 주식을 대량 매도하고 단기 국채에 묻어둔 이유",
        "app_feature": "StockMaster 버크셔 해서웨이 포트폴리오 추적",
        "tags": ["워런버핏포트폴리오", "버크셔해서웨이", "현금보유액사상최대", "버핏지수"]
    },
    {
        "id": 32,
        "category": "us_dividend_tech",
        "title": "미국 대선과 수혜주: 공화당 vs 민주당 정책에 따른 에너지·방산·빅테크 섹터 대응",
        "intent": "화석연료 규제 완화 vs 신재생에너지 보조금, 법인세율 변화가 S&P500에 미치는 영향",
        "app_feature": "StockMaster 미국 대선 정책 수혜주 맵",
        "tags": ["미국대선관련주", "공화당민주당수혜주", "법인세율변화", "IRA보조금"]
    },

    # ── [카테고리 3: etf_index (지수 추종 ETF / 채권 / 월적립식 복리)] ──
    {
        "id": 33,
        "category": "etf_index",
        "title": "S&P 500 ETF 삼총사(SPY vs IVV vs VOO): 수수료 0.03%의 복리 마법",
        "intent": "운용 보수 차이와 유동성, 장기 적립식 투자자가 VOO나 SPLG를 골라야 하는 이유",
        "app_feature": "StockMaster S&P 500 ETF 수수료 비교기",
        "tags": ["SPY비교", "VOO수수료", "IVV비교", "SP500적립식투자"]
    },
    {
        "id": 34,
        "category": "etf_index",
        "title": "QQQ vs QQM: 나스닥 100 지수 추종 ETF 소액 적립식 투자자를 위한 최선의 선택",
        "intent": "동일한 나스닥 100 지수를 추종하면서 보수가 더 저렴한 QQM 활용 가이드",
        "app_feature": "StockMaster 나스닥 적립식 시뮬레이터",
        "tags": ["QQQ주가", "QQM수수료", "나스닥100ETF", "빅테크지수투자"]
    },
    {
        "id": 35,
        "category": "etf_index",
        "title": "월 50만원씩 S&P 500에 20년 복리 투자하면 통장에 얼마가 찍힐까? (과거 30년 백테스트)",
        "intent": "연평균 수익률 10% 가정 시 원금 1억 2천만원이 3억 8천만원으로 불어나는 수학적 원리",
        "app_feature": "StockMaster 복리 은퇴자산 계산기",
        "tags": ["월50만원적립식", "SP500복리수익", "20년장기투자", "경제적자유"]
    },
    {
        "id": 36,
        "category": "etf_index",
        "title": "미국 장기채 ETF(TLT): 금리 인하기 주가 상승 폭과 월배당 이자 수익 동시 잡기",
        "intent": "20년물 미국 국채 듀레이션(Duration) 효과와 금리 1%p 하락 시 기대 자본 차익",
        "app_feature": "StockMaster 채권 금리 듀레이션 계산기",
        "tags": ["TLT장기채", "미국국채투자", "금리인하채권수혜", "채권월배당"]
    },
    {
        "id": 37,
        "category": "etf_index",
        "title": "레버리지 ETF(TQQQ, SOXL) 장기 보유하면 계좌 녹아내리는 이유: 음의 복리(Vol Drag)",
        "intent": "3배 레버리지 상품의 횡보장 계좌 침식 원리와 단기 스윙 트레이딩 원칙",
        "app_feature": "StockMaster 레버리지 음의 복리 시뮬레이터",
        "tags": ["TQQQ장기투자위험", "SOXL음의복리", "3배레버리지함정", "변동성침식"]
    },
    {
        "id": 38,
        "category": "etf_index",
        "title": "국내 상장 미국 ETF(TIGER 미국S&P500, ACE 미국나스닥100): ISA·연금저축 절세 꿀팁",
        "intent": "직접 환전해 미국 주식 사는 것보다 연금계좌에서 국내 상장 해외 ETF 담는 이유",
        "app_feature": "StockMaster 절세 계좌 ETF 최적 배분",
        "tags": ["TIGER미국S&P500", "ACE나스닥100", "연금저축해외ETF", "ISA계좌절세"]
    },
    {
        "id": 39,
        "category": "etf_index",
        "title": "배당 다우존스(한국판 SCHD): TIGER vs SOL vs ACE 배당성장 ETF 삼파전",
        "intent": "월배당 지급일, 총보수율(기타비용 포함), 추적오차율을 종합 비교한 1위 상품",
        "app_feature": "StockMaster 한국판 SCHD 3사 실부담비용 비교",
        "tags": ["한국판SCHD", "TIGER미국배당다우존스", "SOL미국배당", "월배당ETF추천"]
    },
    {
        "id": 40,
        "category": "etf_index",
        "title": "반도체 지수 ETF(SOXX vs SMH): 엔비디아 비중 20% 넘는 SMH가 압도한 비결",
        "intent": "필라델피아 반도체 지수(SOXX)와 반도체 대장주 압축 포트폴리오(SMH) 비교",
        "app_feature": "StockMaster 글로벌 반도체 ETF 분석",
        "tags": ["SOXX주가", "SMH비교", "반도체ETF추천", "필라델피아반도체"]
    },
    {
        "id": 41,
        "category": "etf_index",
        "title": "금(Gold) 투자 ETF(GLD, IAU)와 은(Silver): 인플레이션과 지정학적 위기 속 안전자산",
        "intent": "중앙은행들의 금 매집 열풍과 달러 패권 약화 헤지 수단으로서의 금 포트폴리오",
        "app_feature": "StockMaster 금 은 원자재 트래커",
        "tags": ["금투자ETF", "GLD주가", "골드바투자비교", "안전자산헤지"]
    },
    {
        "id": 42,
        "category": "etf_index",
        "title": "인도 니프티 50 ETF(TIGER 인도니프티50): 글로벌 공급망 대체 1순위 인도의 성장성",
        "intent": "중국을 제치고 세계 1위 인구 대국으로 부상한 인도의 인프라 및 소비재 투자",
        "app_feature": "StockMaster 신흥국 인도 ETF 리포트",
        "tags": ["인도니프티50", "인도주식투자", "신흥국ETF", "포스트차이나인도"]
    },
    {
        "id": 43,
        "category": "etf_index",
        "title": "비트코인 현물 ETF(IBIT) 제도권 편입: 주식 계좌에서 디지털 금 담는 법",
        "intent": "블랙록 IBIT 승인 이후 기관 자금 유입과 4년 반감기 사이클 속 자산 배분 비중",
        "app_feature": "StockMaster 비트코인 현물 ETF 자금 유출입 추적",
        "tags": ["비트코인현물ETF", "IBIT블랙록", "가상자산제도권", "암호화폐자산배분"]
    },
    {
        "id": 44,
        "category": "etf_index",
        "title": "단기 채권 파킹통장형 ETF(CD금리, KOFR, SOFR): 하루만 넣어도 연 3.5% 이자",
        "intent": "주식 예수금을 놀리지 않고 매일 복리로 이자가 쌓이는 초단기 금리형 ETF",
        "app_feature": "StockMaster 파킹형 ETF 금리 비교기",
        "tags": ["CD금리ETF", "KOFR파킹통장", "SOFR미국달러파킹", "예수금이자늘리기"]
    },
    {
        "id": 45,
        "category": "etf_index",
        "title": "인버스(곱버스) ETF로 하락장에 베팅했다가 망하는 이유: 시장의 장기 우상향 법칙",
        "intent": "지수 하락에 베팅하는 역방향 ETF의 시간 가치 손실과 리스크 관리 원칙",
        "app_feature": "StockMaster 인버스 위험도 분석기",
        "tags": ["인버스ETF위험", "곱버스함정", "하락장베팅주의", "지수우상향원칙"]
    },
    {
        "id": 46,
        "category": "etf_index",
        "title": "고배당 인프라 펀드(맥쿼리인프라): 도로·항만 통행료로 연 6~7% 배당받는 법",
        "intent": "인플레이션 연동 통행료 인상과 정부 최소운영수입보장(MRG) 구조의 안전성",
        "app_feature": "StockMaster 맥쿼리인프라 배당 분석",
        "tags": ["맥쿼리인프라배당", "고배당주추천", "인프라펀드", "국내월배당주"]
    },
    {
        "id": 47,
        "category": "etf_index",
        "title": "원자재 원유(WTI) ETF 롤오버 비용의 함정: 유가가 올라도 계좌가 손실인 까닭",
        "intent": "콘탱고(Contango)와 백워데이션(Backwardation) 월물 교체 비용의 수학적 구조",
        "app_feature": "StockMaster 원유 선물 롤오버 손익 분석",
        "tags": ["원유ETF롤오버", "WTI유가투자", "콘탱고비용", "선물ETF주의점"]
    },
    {
        "id": 48,
        "category": "etf_index",
        "title": "올웨더 포트폴리오(레이 달리오) ETF 구성: 주식 30 + 채권 55 + 금/원자재 15",
        "intent": "어떤 경제 위기나 인플레이션에도 MDD(최대 낙폭) 10% 이내로 방어하는 자산배분",
        "app_feature": "StockMaster 올웨더 자동 리밸런싱 포트폴리오",
        "tags": ["올웨더포트폴리오", "레이달리오자산배분", "사계절포트폴리오", "MDD최소화"]
    },

    # ── [카테고리 4: macro_economy (거시경제 / 환율 / 금리 / 물가)] ──
    {
        "id": 49,
        "category": "macro_economy",
        "title": "미국 연준(Fed) 기준금리 인하 사이클 시작: 주식, 채권, 부동산 자산별 희비",
        "intent": "빅컷(0.5%p) vs 베이비컷(0.25%p)과 점도표(Dot Plot)가 예고하는 향후 2년 유동성",
        "app_feature": "StockMaster FOMC 점도표 시각화",
        "tags": ["미국기준금리인하", "연준FOMC회의", "점도표해석", "유동성장세"]
    },
    {
        "id": 50,
        "category": "macro_economy",
        "title": "원/달러 환율 1,350원대 고착화: 환차익 노리는 달러 예금 vs 미국주식 환노출(UH)",
        "intent": "환노출(UH)과 환헤지(H) ETF의 차이점 및 원화 약세 국면에서의 미국 주식 방어력",
        "app_feature": "StockMaster 환노출 vs 환헤지 수익률 비교",
        "tags": ["원달러환율전망", "환노출환헤지차이", "달러투자방법", "환차익비과세"]
    },
    {
        "id": 51,
        "category": "macro_economy",
        "title": "CPI(소비자물가지수)와 PPI(생산자물가지수) 발표 날 미국 증시가 요동치는 이유",
        "intent": "근원 CPI(Core CPI)와 헤드라인 CPI의 차이 및 인플레이션 고착화 우려 분석",
        "app_feature": "StockMaster 실시간 거시지표 브리핑",
        "tags": ["미국CPI발표", "소비자물가지수", "근원CPI", "인플레이션헤지"]
    },
    {
        "id": 52,
        "category": "macro_economy",
        "title": "장단기 금리차 역전(10년물 - 2년물) 해소: 과거 50년 경기침체(R의 공포) 공식",
        "intent": "금리 역전 자체가 아니라 역전이 해소되는 순간 주식 시장이 폭락했던 역사적 교훈",
        "app_feature": "StockMaster 장단기 금리차 실시간 트래커",
        "tags": ["장단기금리차역전", "R의공포경기침체", "10년물국채금리", "미국증시폭락전조"]
    },
    {
        "id": 53,
        "category": "macro_economy",
        "title": "엔 캐리 트레이드(Yen Carry Trade) 청산 공포: 일본은행(BOJ) 금리 인상의 파장",
        "intent": "초저금리 엔화 빌려 글로벌 자산에 투자하던 거대 자금의 회수가 촉발한 블랙 먼데이",
        "app_feature": "StockMaster 글로벌 유동성 리스크 감지기",
        "tags": ["엔캐리트레이드청산", "일본은행금리인상", "엔화환율전망", "블랙먼데이원인"]
    },
    {
        "id": 54,
        "category": "macro_economy",
        "title": "미국 고용지표(비농업 고용 NFP, 실업률 삼의 법칙 Sahm Rule) 경기침체 판독법",
        "intent": "실업률 3개월 이동평균이 최근 1년 최저치 대비 0.5%p 상승 시 침체 진입 공식",
        "app_feature": "StockMaster 삼의 법칙 침체 확률 판독기",
        "tags": ["비농업고용지표", "미국실업률", "삼의법칙", "경기침체시그널"]
    },
    {
        "id": 55,
        "category": "macro_economy",
        "title": "국제 유가(WTI, 브렌트유) 100달러 돌파 시 한국 경제와 주가에 미치는 충격",
        "intent": "에너지 수입 의존도가 높은 한국 무역수지 적자와 정유주 vs 항공주 수혜/피해",
        "app_feature": "StockMaster 유가 변동 수혜주 분석",
        "tags": ["국제유가전망", "WTI유가상승", "정유주주가", "항공주피해"]
    },
    {
        "id": 56,
        "category": "macro_economy",
        "title": "중국 경제 디플레이션과 부동산 부도 위기: 대중국 수출 비중 높은 한국 기업 리스크",
        "intent": "헝다·비구이위안 사태 이후 중국 소비 둔화와 한국 화학·철강·화장품 섹터 영향",
        "app_feature": "StockMaster 대중국 익스포저 위험 진단",
        "tags": ["중국디플레이션", "중국부동산위기", "대중국수출주", "철강화학주전망"]
    },
    {
        "id": 57,
        "category": "macro_economy",
        "title": "공포와 탐욕 지수(Fear & Greed Index): 극단적 공포(Extreme Fear)에서 분할 매수하기",
        "intent": "CNN 공포탐욕 지수 20 이하 구간에서 주식을 쓸어 담았을 때 1년 뒤 수익률 통계",
        "app_feature": "StockMaster 공포탐욕지수 알림봇",
        "tags": ["공포와탐욕지수", "CNN피어앤그리드", "바닥매수타이밍", "역발상투자"]
    },
    {
        "id": 58,
        "category": "macro_economy",
        "title": "VIX 지수(변동성 지수, 공포 지수) 40 돌파: 옵션 만기일과 시장 폭락 대응법",
        "intent": "S&P 500 지수 옵션 변동성을 기반으로 한 시장 변동성 지표의 급등 시 대처 요령",
        "app_feature": "StockMaster VIX 변동성 경보 시스템",
        "tags": ["VIX지수급등", "공포지수해석", "변동성완화장치", "폭락장대응법"]
    },
    {
        "id": 59,
        "category": "macro_economy",
        "title": "달러 인덱스(DXY) 105 돌파 강달러 현상: 신흥국 자금 유출과 코스피 외인 이탈",
        "intent": "유로, 엔, 파운드 등 6개 주요국 통화 대비 달러 가치가 한국 증시에 미치는 매커니즘",
        "app_feature": "StockMaster 달러 인덱스 상관관계 분석",
        "tags": ["달러인덱스DXY", "킹달러수혜주", "외국인자금이탈", "신흥국증시전망"]
    },
    {
        "id": 60,
        "category": "macro_economy",
        "title": "한국은행 금융통화위원회 기준금리 동결 vs 인하: 가계부채와 부동산 PF의 딜레마",
        "intent": "한미 금리차 2.0%p 역대 최대 역전 상황에서 한은 총재의 통화정책 고심 분석",
        "app_feature": "StockMaster 한은 금통위 전망 리포트",
        "tags": ["한국은행기준금리", "금통위금리인하", "한미금리차", "가계부채부동산PF"]
    },
    {
        "id": 61,
        "category": "macro_economy",
        "title": "글로벌 공급망 재편(프렌드쇼어링)과 미국의 리쇼어링 정책: 멕시코·베트남 수혜",
        "intent": "중국 중심의 서플라이 체인 분절화 속 미국 인접국 제조 시설 투자 기업",
        "app_feature": "StockMaster 글로벌 니어쇼어링 수혜주 맵",
        "tags": ["프렌드쇼어링", "리쇼어링정책", "글로벌공급망", "해외생산기지"]
    },
    {
        "id": 62,
        "category": "macro_economy",
        "title": "스태그플레이션(경기침체 속 물가상승): 1970년대 오일쇼크에서 배우는 포트폴리오",
        "intent": "주식과 채권이 동시에 폭락하는 최악의 경제 시나리오에서 살아남는 원자재와 현금 비중",
        "app_feature": "StockMaster 스태그플레이션 방어 포트폴리오",
        "tags": ["스태그플레이션대비", "오일쇼크교훈", "원자재투자비중", "인플레방어주"]
    },
    {
        "id": 63,
        "category": "macro_economy",
        "title": "미국 재무부 국채 발행 계획(QRA): 채권 공급 폭탄이 시중 유동성을 흡수할 때",
        "intent": "재닛 옐런 재무장관의 단기채 vs 장기채 발행 비중 조절이 주식 시장을 살린 원리",
        "app_feature": "StockMaster 미국 재무부 유동성 지표 추적",
        "tags": ["미국국채발행QRA", "시중유동성추이", "재무부채권발행", "증시유동성영향"]
    },
    {
        "id": 64,
        "category": "macro_economy",
        "title": "구리(Dr. Copper) 가격 급등: 경기 회복의 신호탄인가, 친환경 인프라 쇼티지인가?",
        "intent": "산업 전반에 쓰여 경기 바로미터로 불리는 구리 가격과 AI 데이터센터 전력선 수요",
        "app_feature": "StockMaster 닥터 코퍼 경기 선행 지표",
        "tags": ["구리가격급등", "닥터코퍼경기선행", "구리관련주", "전력선원자재"]
    },

    # ── [카테고리 5: chart_financials (차트 / 재무제표 / 수급 / 공시)] ──
    {
        "id": 65,
        "category": "chart_financials",
        "title": "주식 초보도 3분 만에 마스터하는 재무제표 3대 지표: PER, PBR, ROE 보는 법",
        "intent": "동일 업종 내 저평가 우량주를 1초 만에 골라내는 기본적 분석 핵심 공식",
        "app_feature": "StockMaster 원클릭 재무제표 진단표",
        "tags": ["PER보는법", "PBR해석", "ROE우량주", "주식재무제표초보"]
    },
    {
        "id": 66,
        "category": "chart_financials",
        "title": "이동평균선 골든크로스(Golden Cross)와 데드크로스: 20일선과 60일선 매매 기법",
        "intent": "단기 이평선이 장기 이평선을 상향 돌파할 때의 신뢰도와 가짜 신호(속임수) 판별법",
        "app_feature": "StockMaster AI 골든크로스 자동 포착기",
        "tags": ["골든크로스매매", "데드크로스손절", "이동평균선매매법", "20일선돌파"]
    },
    {
        "id": 67,
        "category": "chart_financials",
        "title": "지지선과 저항선 긋기: 바닥 매수와 천장 매도 타이밍을 잡아내는 마법의 선",
        "intent": "전고점과 전저점, 매물대 차트를 활용한 최적의 손익비(Risk/Reward) 진입 자리",
        "app_feature": "StockMaster AI 자동 지지저항선 차트",
        "tags": ["지지선저항선", "매물대차트보는법", "전고점돌파", "손익비좋은자리"]
    },
    {
        "id": 68,
        "category": "chart_financials",
        "title": "DART 전자공시 시스템 필수 확인 공시 3가지: 유상증자, 전환사채(CB), 무상증자",
        "intent": "주주가치를 희석시키는 악성 공시(CB/BW 발행)와 주가 급등 호재 구별법",
        "app_feature": "StockMaster DART 악성 공시 필터링봇",
        "tags": ["DART전자공시", "유상증자악재", "전환사채CB함정", "무상증자호재"]
    },
    {
        "id": 69,
        "category": "chart_financials",
        "title": "거래량 없는 상승 vs 대량 거래량 장대양봉: 주포(세력)의 매집 흔적 찾는 법",
        "intent": "바닥권에서 터진 평소 500% 이상의 대량 거래량이 의미하는 강력한 추세 전환",
        "app_feature": "StockMaster 대량 거래량 급등주 알림",
        "tags": ["거래량매매법", "장대양봉의의미", "세력매집차트", "바닥거래량급증"]
    },
    {
        "id": 70,
        "category": "chart_financials",
        "title": "RSI(상대강도지수) 과매수(70 이상) 과매도(30 이하): 역추세 매매의 정석",
        "intent": "다이버전스(Divergence, 주가와 지표의 불일치)를 이용한 고점 매도와 저점 매수",
        "app_feature": "StockMaster RSI 다이버전스 자동 스캐너",
        "tags": ["RSI지표보는법", "과매도30이하", "RSI다이버전스", "보조지표매매"]
    },
    {
        "id": 71,
        "category": "chart_financials",
        "title": "영업이익 vs 당기순이익 차이: 일회성 부동산 매각 이익에 속지 않는 법",
        "intent": "본업에서 번 돈(영업이익)과 금융수익/일회성 이익이 섞인 당기순이익의 실체",
        "app_feature": "StockMaster 본업 영업이익 성장률 분석",
        "tags": ["영업이익당기순이익차이", "영업이익률비교", "영업외수익함정", "진짜돈버는기업"]
    },
    {
        "id": 72,
        "category": "chart_financials",
        "title": "볼린저 밴드(Bollinger Bands) 하단 터치 매수 기법: 밴드 수축 후 확장(스퀴즈) 폭발",
        "intent": "표준편차 2σ를 이용한 변동성 돌파 매매와 밴드 상단 이탈 시 익절 기준",
        "app_feature": "StockMaster 볼린저밴드 스퀴즈 감지기",
        "tags": ["볼린저밴드매매법", "밴드하단매수", "볼린저스퀴즈", "변동성돌파"]
    },
    {
        "id": 73,
        "category": "chart_financials",
        "title": "부채비율 100% 미만 & 유보율 1,000% 이상: 상장폐지 당하지 않는 안전지대 종목",
        "intent": "이자보상배율 1 미만(좀비 기업) 거르고 현금성 자산이 빵빵한 알짜 품절주 발굴",
        "app_feature": "StockMaster 재무 건전성 100점 스크리너",
        "tags": ["부채비율유보율", "상장폐지피하는법", "이자보상배율", "현금부자기업"]
    },
    {
        "id": 74,
        "category": "chart_financials",
        "title": "이중 바닥(W자 쌍바닥) vs 헤드앤숄더(Head & Shoulders): 차트 패턴 완성 조건",
        "intent": "넥라인(Neckline) 돌파 확인 후 진입하는 정석 패턴 매매와 손절 라인 잡기",
        "app_feature": "StockMaster 차트 패턴 AI 인식기",
        "tags": ["쌍바닥W패턴", "헤드앤숄더패턴", "넥라인돌파", "차트패턴매매"]
    },
    {
        "id": 75,
        "category": "chart_financials",
        "title": "공매도 잔고와 숏스퀴즈(Short Squeeze): 에코프로처럼 주가 폭등하는 원리",
        "intent": "기관 공매도 세력이 손실을 줄이기 위해 주식을 되사는 숏커버링 유입 시그널",
        "app_feature": "StockMaster 공매도 잔고 급감 추적기",
        "tags": ["공매도잔고조회", "숏스퀴즈원리", "숏커버링매수", "공매도비율"]
    },
    {
        "id": 76,
        "category": "chart_financials",
        "title": "잉여현금흐름(FCF, Free Cash Flow): 워런 버핏이 가장 사랑하는 진짜 돈의 흐름",
        "intent": "회계상 장부 이익이 아닌 설비투자(CAPEX)를 빼고 회사에 순수하게 남는 현금",
        "app_feature": "StockMaster FCF 잉여현금흐름 상위 기업",
        "tags": ["잉여현금흐름FCF", "워런버핏지표", "진짜현금창출능력", "CAPEX설비투자"]
    },
    {
        "id": 77,
        "category": "chart_financials",
        "title": "갭(Gap) 상승과 갭 하락: 갭은 반드시 메워진다는 주식 격언의 진실과 돌파 갭",
        "intent": "일반 갭과 강력한 호재로 발생한 돌파 갭(Breakaway Gap)의 구별 및 매매 전략",
        "app_feature": "StockMaster 갭상승 지지선 분석기",
        "tags": ["갭상승갭하락", "갭메우기법칙", "돌파갭매매", "차트갭해석"]
    },
    {
        "id": 78,
        "category": "chart_financials",
        "title": "피보나치 되돌림(Fibonacci Retracement): 0.382와 0.618 반등 타점 잡기",
        "intent": "상승 파동 후 조정 국면에서 가장 강력하게 지지가 나오는 황금 비율 매수법",
        "app_feature": "StockMaster 피보나치 자동 되돌림 차트",
        "tags": ["피보나치되돌림", "황금비율0.618", "눌림목매수타점", "조정파동반등"]
    },
    {
        "id": 79,
        "category": "chart_financials",
        "title": "내부자 거래(Insider Trading) 공시: CEO와 임원이 자사주를 장내 매수할 때",
        "intent": "누구보다 회사 사정을 잘 아는 경영진의 자기 돈 매수는 가장 확실한 바닥 신호",
        "app_feature": "StockMaster 임원 자사주 매수 알림",
        "tags": ["내부자거래공시", "대표이사자사주매수", "경영진장내매수", "바닥신호공시"]
    },
    {
        "id": 80,
        "category": "chart_financials",
        "title": "잠정 실적 공시(어닝 서프라이즈 vs 어닝 쇼크): 컨센서스 대비 괴리율 매매",
        "intent": "실적이 잘 나와도 컨센서스를 밑돌면 폭락하는 이유와 선반영의 매커니즘",
        "app_feature": "StockMaster 실적 컨센서스 괴리율 분석",
        "tags": ["어닝서프라이즈", "어닝쇼크주가", "컨센서스선반영", "실적발표매매"]
    },

    # ── [카테고리 6: quant_risk (AI 퀀트 / 뇌동매매 방지 / 리스크 관리)] ──
    {
        "id": 81,
        "category": "quant_risk",
        "title": "뇌동매매(FOMO) 고치는 3대 원칙: 급등하는 불기둥에 올라타지 않는 멘탈 관리법",
        "intent": "남들이 돈 벌었다는 소리에 조급해져 고점에 물리는 심리적 편향 극복 노하우",
        "app_feature": "StockMaster FOMO 방지 심리 체크리스트",
        "tags": ["뇌동매매극복", "FOMO증후군방지", "주식멘탈관리", "불기둥추격매수금지"]
    },
    {
        "id": 82,
        "category": "quant_risk",
        "title": "기계적인 손절매(Stop-Loss) 설정 기준: -5% 또는 전저점 이탈 시 무조건 자르기",
        "intent": "손실 -50%를 복구하려면 +100% 수익이 필요하다는 손실 복구의 비대칭성 원리",
        "app_feature": "StockMaster 자동 스탑로스 설정 가이드",
        "tags": ["손절매기준", "스탑로스설정", "손실복구수익률", "원금보존원칙"]
    },
    {
        "id": 83,
        "category": "quant_risk",
        "title": "분할 매수(Scale-in)와 분할 매도(Scale-out): 3분할 3분할 공식으로 평단가 관리",
        "intent": "몰빵 투자의 공포를 없애고 심리적 우위를 점하는 스마트 분할 진입·청산법",
        "app_feature": "StockMaster 3분할 매수매도 계산기",
        "tags": ["분할매수원칙", "분할매도익절", "평단가관리법", "몰빵금지투자"]
    },
    {
        "id": 84,
        "category": "quant_risk",
        "title": "AI 퀀트 알고리즘 투자란 무엇인가? 감정을 배제한 백테스팅 기반 룰 세팅",
        "intent": "모멘텀 지표, 밸류 지표, 퀄리티 지표를 조합한 팩터(Factor) 투자의 기본 원리",
        "app_feature": "StockMaster AI 퀀트 팩터 엔진 소개",
        "tags": ["AI퀀트투자", "팩터투자원리", "백테스팅기반", "감정배제매매"]
    },
    {
        "id": 85,
        "category": "quant_risk",
        "title": "MDD(Maximum Drawdown, 최대 낙폭): 수익률보다 MDD가 낮은 전략을 골라야 하는 이유",
        "intent": "고점 대비 계좌가 박살 나는 최대 하락률을 관리해야 복리 투자가 중단되지 않는다",
        "app_feature": "StockMaster 포트폴리오 MDD 측정기",
        "tags": ["MDD최대낙폭", "계좌원금보호", "복리투자유지", "샤프지수해석"]
    },
    {
        "id": 86,
        "category": "quant_risk",
        "title": "물타기(Averaging Down)의 함정: 끝없이 추락하는 잡주에 물타기하다 깡통 차는 이유",
        "intent": "우량주와 잡주의 물타기 구분법 및 상승 추세에서 비중을 늘리는 불타기 전략",
        "app_feature": "StockMaster 물타기 vs 불타기 판단기",
        "tags": ["물타기함정", "잡주물타기금지", "불타기전략", "평단가낮추기주의"]
    },
    {
        "id": 87,
        "category": "quant_risk",
        "title": "켈리 공식(Kelly Criterion): 수학적으로 입증된 최적의 배팅(투자 비중) 비율",
        "intent": "승률과 손익비를 계산하여 한 종목에 전체 자산의 몇 %를 넣어야 파산하지 않는가",
        "app_feature": "StockMaster 켈리 공식 투자 비중 계산기",
        "tags": ["켈리공식", "최적투자비중", "파산확률0퍼센트", "자금관리원칙"]
    },
    {
        "id": 88,
        "category": "quant_risk",
        "title": "주식 투자 일지(매매 일지) 작성법: 나의 뇌동매매 패턴을 발견하고 교정하기",
        "intent": "매수 이유, 매도 이유, 감정 상태를 기록하여 승률을 2배 끌어올리는 복기 습관",
        "app_feature": "StockMaster AI 자동 매매 일지 템플릿",
        "tags": ["매매일지작성법", "투자일지복기", "오답노트주식", "투자습관개선"]
    },
    {
        "id": 89,
        "category": "quant_risk",
        "title": "현금 비중 20~30% 유지가 주는 마법: 폭락장에서 웃을 수 있는 유일한 무기",
        "intent": "풀매수 상태에서는 패닉셀을 부르고, 현금이 있어야 저가 매수 기회를 잡는다",
        "app_feature": "StockMaster 자산별 현금 비중 리밸런서",
        "tags": ["현금비중유지", "폭락장저가매수", "패닉셀방지", "심리적안정감"]
    },
    {
        "id": 90,
        "category": "quant_risk",
        "title": "미수·신용·영끌 투자의 파멸: 반대매매(Forced Liquidation)가 폭락을 부르는 매커니즘",
        "intent": "담보유지비율 140% 미달 시 개장 직후 하한가로 강제 처분되는 빚투의 끔찍한 결말",
        "app_feature": "StockMaster 신용잔고 리스크 경보",
        "tags": ["반대매매공포", "신용미수금지", "빚투의결말", "담보유지비율140"]
    },
    {
        "id": 91,
        "category": "quant_risk",
        "title": "상승장에서는 누구나 천재다: 워런 버핏의 '썰물이 빠져야 누가 발가벗고 헤엄쳤는지 안다'",
        "intent": "유동성 파티가 끝난 후 실적과 펀더멘털이 없는 거품 주식이 폭락하는 냉정한 현실",
        "app_feature": "StockMaster 기업 펀더멘털 점수 진단",
        "tags": ["워런버핏명언", "상승장착각", "하락장검증", "진짜우량주구별"]
    },
    {
        "id": 92,
        "category": "quant_risk",
        "title": "확증 편향(Confirmation Bias) 탈출: 내가 산 주식의 호재 뉴스만 찾아보는 뇌의 착각",
        "intent": "매수 후 객관성을 잃지 않기 위해 비판적 리포트와 하방 리스크를 먼저 읽는 습관",
        "app_feature": "StockMaster 종목별 하방 리스크 AI 요약",
        "tags": ["확증편향극복", "객관적투자", "호재뉴스중독", "리스크체크습관"]
    },
    {
        "id": 93,
        "category": "quant_risk",
        "title": "손실 회피 편향(Loss Aversion): 본전 심리 때문에 쓰레기 주식을 평생 안고 가는 이유",
        "intent": "원금 회복에 집착하여 더 좋은 주식으로 갈아탈 기회비용을 날리는 심리 치료",
        "app_feature": "StockMaster 본전 심리 탈출 갈아타기 진단",
        "tags": ["본전심리극복", "손실회피편향", "기회비용계산", "종목교체매매"]
    },
    {
        "id": 94,
        "category": "quant_risk",
        "title": "수익 보존 익절(Trailing Stop): 수익 중인 주식을 끝까지 끌고 가며 이익 극대화하기",
        "intent": "고점 대비 3% 또는 5% 하락 시 자동으로 이익 실현하는 트레일링 스탑의 마법",
        "app_feature": "StockMaster 트레일링 스탑 계산기",
        "tags": ["트레일링스탑", "익절라인관리", "수익극대화", "추세추종매매"]
    },
    {
        "id": 95,
        "category": "quant_risk",
        "title": "월급쟁이 직장인에게 최적화된 주식 투자 루틴: 장중 HTS 안 보고 퇴근 후 10분 점검",
        "intent": "업무 집중도를 지키면서 자동 예약 매수·매도 기능을 활용한 스트레스 제로 투자",
        "app_feature": "StockMaster 직장인 10분 퇴근 루틴봇",
        "tags": ["직장인주식루틴", "HTS중독탈출", "예약매매활용", "스트레스없는주식"]
    },
    {
        "id": 96,
        "category": "quant_risk",
        "title": "테마주(정치테마, 초전도체, 양자컴퓨터) 롤러코스터에서 살아남는 불문율",
        "intent": "실체 없는 테마주는 대장주만 단기 매매하고 이슈 소멸 전 전량 털고 나오는 법칙",
        "app_feature": "StockMaster 실시간 테마주 대장주 판독기",
        "tags": ["테마주매매원칙", "정치테마주위험", "초전도체테마", "대장주매매"]
    },
    {
        "id": 97,
        "category": "quant_risk",
        "title": "상관관계(Correlation) 분산 투자: 서로 반대로 움직이는 자산을 묶어 계좌 변동성 죽이기",
        "intent": "미국 주식과 달러 현금, 금과 채권의 음의 상관관계를 이용한 방탄 포트폴리오",
        "app_feature": "StockMaster 자산 간 상관관계 매트릭스",
        "tags": ["상관관계분산투자", "방탄포트폴리오", "자산배분효과", "계좌변동성축소"]
    },
    {
        "id": 98,
        "category": "quant_risk",
        "title": "동전주(페니 스톡) 대박 꿈꾸다 상장폐지 정리매매 당하는 이유: 감자·유증의 굴레",
        "intent": "주가 1,000원 미만 관리종목의 자본잠식과 회계감사 거절 폭탄 피하기",
        "app_feature": "StockMaster 관리종목 위험 자동 경보",
        "tags": ["동전주위험", "페니스톡상장폐지", "자본잠식거절", "정리매매함정"]
    },
    {
        "id": 99,
        "category": "quant_risk",
        "title": "투자 대가 피터 린치의 명언: '당신이 아는 것에 투자하라'의 현대적 재해석",
        "intent": "일상에서 소비하는 제품(아이폰, 스타벅스, 나이키) 속에서 10루타(Tenbagger) 종목 찾기",
        "app_feature": "StockMaster 피터 린치형 생활 속 종목 발굴기",
        "tags": ["피터린치명언", "10루타종목발굴", "생활속주식투자", "텐배거찾기"]
    },
    {
        "id": 100,
        "category": "quant_risk",
        "title": "StockMaster AI와 함께하는 스마트 데이터 투자: 뇌동매매 끝, 데이터로 증명하는 승리",
        "intent": "국내외 수만 개 종목의 수급, 재무, 모멘텀을 AI가 실시간 분석하여 최적의 타점 제공",
        "app_feature": "StockMaster AI 종합 시그널 대시보드",
        "tags": ["StockMaster", "주식AI추천", "스마트퀀트투자", "데이터기반주식"]
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
