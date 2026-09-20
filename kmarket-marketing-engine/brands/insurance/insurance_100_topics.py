# -*- coding: utf-8 -*-
"""
🛡️ InsureBalance 100대 마스터 토픽 풀 (100 Master Topics Pool)
============================================================
- 브랜드: InsureBalance (보험 비교 & 리모델링 & 보험금 청구 가이드)
- 타깃: 2040 직장인, 사회초년생, 신혼부부, 부모님 보험 점검 희망자
- 6대 핵심 카테고리:
  1. health_medical     : 실손의료보험 / 4세대 실손 / 3대 질병(암·뇌·심장) / 수술비
  2. auto_driver        : 자동차보험 다이렉트 / 운전자보험 필수특약 / 사고대처 / 침수차
  3. life_dental_pet    : 치아보험 / 펫보험 / 일상생활배상책임(일배책) / 주택화재보험
  4. savings_annuity    : 연금저축 vs 연금보험 / IRP / 종신 vs 정기보험 / 절세
  5. claims_knowhow     : 보험금 청구 서류 3분컷 / 부지급 대처 / 손해사정사 / 숨은보험금
  6. remodeling_savings : 중복 특약 다이어트 / 갱신 vs 비갱신 / 사회초년생 포트폴리오
"""

from typing import List, Dict, Any, Optional

INSURANCE_100_TOPICS: List[Dict[str, Any]] = [
    # ── [카테고리 1: health_medical (실손 / 암 / 3대 질병 / 건강)] ──
    {
        "id": 1,
        "category": "health_medical",
        "title": "4세대 실손보험 전환, 지금 해야 이득일까? 손해일까?",
        "intent": "기존 1~3세대 실손 유지와 4세대 전환의 장단점 및 보험료 시뮬레이션 비교",
        "app_feature": "InsureBalance 4세대 실손 전환 손익 계산기",
        "tags": ["4세대실손", "실손보험비교", "보험료절약", "실비보험전환"]
    },
    {
        "id": 2,
        "category": "health_medical",
        "title": "암보험 가입 전 필수 체크: 일반암과 유사암 진단비 한도의 진실",
        "intent": "유사암(갑상선암, 경계성종양 등) 진단비 축소 추세와 일반암 진단비 최적 구성법",
        "app_feature": "InsureBalance 3대 질병 진단비 진단 분석",
        "tags": ["암보험비교", "암진단비", "유사암한도", "2030암보험"]
    },
    {
        "id": 3,
        "category": "health_medical",
        "title": "뇌혈관질환 vs 뇌졸중 vs 뇌출혈: 보장 범위 10배 차이 나는 이유",
        "intent": "가장 넓은 보장 범위(뇌혈관질환)를 선택해야 하는 이유와 약관 코드 분석",
        "app_feature": "InsureBalance 뇌·심장 보장 범위 판독기",
        "tags": ["뇌혈관질환보험", "뇌졸중진단비", "보험약관분석", "건강보험비교"]
    },
    {
        "id": 4,
        "category": "health_medical",
        "title": "허혈성 심장질환 vs 급성심근경색: 협심증까지 보장받는 법",
        "intent": "협심증 환자가 급증하는 현실에서 급성심근경색만 가입했을 때의 부지급 위험",
        "app_feature": "InsureBalance 심혈관 보장 범위 체크",
        "tags": ["허혈성심장질환", "협심증보험", "급성심근경색", "심장보험비교"]
    },
    {
        "id": 5,
        "category": "health_medical",
        "title": "수술비 보험 종수술비 vs 질병수술비: 매회 지급되는 특약 고르는 법",
        "intent": "1~5종 수술비 특약의 장점과 최신 다빈치 로봇수술 보장 여부 가이드",
        "app_feature": "InsureBalance 수술비 특약 가성비 분석",
        "tags": ["수술비보험", "1종5종수술비", "질병수술비", "로봇수술보장"]
    },
    {
        "id": 6,
        "category": "health_medical",
        "title": "간병인 사용일당 vs 간병인 지원일당: 부모님 간병비 월 400만원 시대 대처법",
        "intent": "간병비 부담 급증에 따른 간병인 보험 2가지 유형의 차이점과 실질 가성비",
        "app_feature": "InsureBalance 부모님 간병보험 맞춤 비교",
        "tags": ["간병인보험", "간병비부담", "간병인사용일당", "부모님보험"]
    },
    {
        "id": 7,
        "category": "health_medical",
        "title": "질병후유장해 3% 이상 특약: 평생 연금처럼 보장받는 숨은 핵심",
        "intent": "디스크, 관절염, 시력 감퇴 등 일상적인 질환도 보장받는 후유장해 특약 활용법",
        "app_feature": "InsureBalance 질병후유장해 가성비 진단",
        "tags": ["질병후유장해", "후유장해3프로", "보험특약추천", "숨은보장"]
    },
    {
        "id": 8,
        "category": "health_medical",
        "title": "표적항암약물치료비 특약: 부작용 적은 신약 치료 보장의 모든 것",
        "intent": "고액 비급여 항암 신약 치료에 대비하는 최신 암보험 필수 특약 정리",
        "app_feature": "InsureBalance 최신 암치료 특약 비교",
        "tags": ["표적항암치료", "중입자치료보험", "암보험특약", "비급여항암"]
    },
    {
        "id": 9,
        "category": "health_medical",
        "title": "치매보험 가입 시기: CDR 척도 1점(경도치매)부터 보장받는 팁",
        "intent": "중증치매만 보장하는 깡통 치매보험 피하고 경도치매 보장 챙기는 법",
        "app_feature": "InsureBalance 치매보험 보장 범위 비교",
        "tags": ["치매보험", "CDR척도", "경도치매보장", "부모님치매보험"]
    },
    {
        "id": 10,
        "category": "health_medical",
        "title": "유병자 보험(3·5·5 vs 3·2·5): 과거 병력 있어도 할증 없이 가입하는 전략",
        "intent": "간편고지 유병자 보험 종류별 가입 조건과 고지 의무 최소화 전략",
        "app_feature": "InsureBalance 유병자 간편보험 비교",
        "tags": ["유병자보험", "간편고지보험", "355보험", "고혈압당뇨보험"]
    },
    {
        "id": 11,
        "category": "health_medical",
        "title": "어린이보험(어른이보험) 30대 가입 막차? 청년보험 현명하게 고르기",
        "intent": "어린이보험 가입 연령 축소 이후 2030 청년보험의 면책기간 및 감액기간 혜택",
        "app_feature": "InsureBalance 2030 청년보험 비교",
        "tags": ["어른이보험", "청년보험", "20대보험추천", "면책기간없음"]
    },
    {
        "id": 12,
        "category": "health_medical",
        "title": "도수치료·체외충격파 실손보험 청구: 4세대 실비 비급여 특약 주의사항",
        "intent": "비급여 도수치료 연간 보장 횟수(최대 50회)와 비급여 의료 이용량 할인·할증제",
        "app_feature": "InsureBalance 실비 비급여 청구 가이드",
        "tags": ["도수치료실비", "4세대실비할증", "체외충격파보험", "비급여의료비"]
    },
    {
        "id": 13,
        "category": "health_medical",
        "title": "백내장 다초점 렌즈 수술비 실손보험 분쟁: 대법원 판례와 지급 기준",
        "intent": "백내장 수술 통원 vs 입원 판정 기준과 실손보험금 수령 노하우",
        "app_feature": "InsureBalance 백내장 보험금 분쟁 가이드",
        "tags": ["백내장수술비", "백내장실손보험", "다초점렌즈", "보험금분쟁"]
    },
    {
        "id": 14,
        "category": "health_medical",
        "title": "갑상선 결절과 고주파절제술: 실손과 수술비 보험 동시 수령법",
        "intent": "갑상선 결절 절제술 시 수술비 특약 인정 여부 및 청구 서류 준비법",
        "app_feature": "InsureBalance 수술비 동시 청구 시뮬레이션",
        "tags": ["갑상선고주파절제술", "수술비특약청구", "갑상선결절", "실비중복보장"]
    },
    {
        "id": 15,
        "category": "health_medical",
        "title": "대장용종 제거술 실비와 종수술비: 내시경 받기 전 꼭 확인해야 할 특약",
        "intent": "건강검진 대장내시경 중 용종 절제 시 1종 수술비 청구로 30~50만원 받는 법",
        "app_feature": "InsureBalance 건강검진 전 보험 점검",
        "tags": ["대장용종수술비", "대장내시경보험청구", "1종수술비", "건강검진특약"]
    },
    {
        "id": 16,
        "category": "health_medical",
        "title": "응급실 내원비 특약: 응급 vs 비응급 환자 실손보험 보장 차이",
        "intent": "야간 응급실 방문 시 대학병원 권역응급센터 비응급 환자 전액 본인부담금 대처",
        "app_feature": "InsureBalance 응급실 보장 체크",
        "tags": ["응급실내원비", "응급실실손", "비응급환자비용", "야간진료보험"]
    },

    # ── [카테고리 2: auto_driver (운전자 / 자동차보험 / 사고대처)] ──
    {
        "id": 17,
        "category": "auto_driver",
        "title": "자동차보험 다이렉트 비교: 5대 손보사 보험료 30만원 아끼는 특약 꿀팁",
        "intent": "주행거리(마일리지), 티맵 안전운전 점수, 블랙박스 등 할인 특약 총정리",
        "app_feature": "InsureBalance 자동차 다이렉트 최저가 비교",
        "tags": ["자동차보험비교", "다이렉트자동차보험", "티맵할인", "주행거리특약"]
    },
    {
        "id": 18,
        "category": "auto_driver",
        "title": "운전자보험 vs 자동차보험 차이: 운전자보험 월 1만원대면 충분한 이유",
        "intent": "자동차보험이 민사상 책임이라면 운전자보험은 형사상 책임(벌금·변호사·합의금)",
        "app_feature": "InsureBalance 운전자보험 1만원 견적기",
        "tags": ["운전자보험비교", "자동차보험차이", "1만원운전자보험", "형사합의금"]
    },
    {
        "id": 19,
        "category": "auto_driver",
        "title": "스쿨존 민식이법 사고 대비: 운전자보험 벌금 3,000만원 상향 특약 필수 확인",
        "intent": "어린이보호구역 사고 시 벌금 한도와 과거 가입 운전자보험 업그레이드 필요성",
        "app_feature": "InsureBalance 운전자보험 필수 특약 진단",
        "tags": ["민식이법벌금", "스쿨존사고", "운전자보험특약", "벌금3천만원"]
    },
    {
        "id": 20,
        "category": "auto_driver",
        "title": "교통사고 처리지원금(형사합의금): 경찰조사 단계부터 나오는 변호사 선임비용",
        "intent": "검찰 기소 전 경찰조사 단계부터 변호사 선임비용이 지원되는 최신 특약 비교",
        "app_feature": "InsureBalance 변호사선임비용 특약 비교",
        "tags": ["경찰조사변호사선임", "교통사고형사합의", "교통사고처리지원금", "운전자보험추천"]
    },
    {
        "id": 21,
        "category": "auto_driver",
        "title": "자동차보험 대물배상 한도 10억원 설정해야 하는 진짜 이유 (포르쉐·슈퍼카 사고)",
        "intent": "대물 2억과 10억의 보험료 차이는 단 몇 천원! 슈퍼카 다중 추돌 대비 필수",
        "app_feature": "InsureBalance 자동차보험 담보 최적화",
        "tags": ["대물배상10억", "슈퍼카사고보험", "자동차보험한도", "대물배상비교"]
    },
    {
        "id": 22,
        "category": "auto_driver",
        "title": "자동차상해(자상) vs 자기신체사고(자손): 무조건 자상을 골라야 하는 3가지 이유",
        "intent": "과실 상계 없이 위자료, 휴업손해까지 100% 보상받는 자상 특약의 압도적 우위",
        "app_feature": "InsureBalance 자상 vs 자손 비교 분석",
        "tags": ["자동차상해", "자기신체사고", "자상자손차이", "교통사고보상"]
    },
    {
        "id": 23,
        "category": "auto_driver",
        "title": "무보험차상해 특약: 뺑소니·무보험차 사고 시 나뿐만 아니라 가족까지 보장",
        "intent": "보행 중 무보험차 사고도 보장되는 무보험차상해 5억원 이상 설정 팁",
        "app_feature": "InsureBalance 무보험차상해 진단",
        "tags": ["무보험차상해", "뺑소니보상", "가족보장특약", "자동차보험특약"]
    },
    {
        "id": 24,
        "category": "auto_driver",
        "title": "여름철 차량 침수 피해 자차보험 보상 기준: 창문·선루프 열어두면 부지급?",
        "intent": "자차 침수 보상 인정 기준과 침수차 전손 처리 시 취등록세 감면 혜택",
        "app_feature": "InsureBalance 침수차 자차 보상 체크",
        "tags": ["차량침수자차", "침수차보험보상", "전손처리", "자차보험처리"]
    },
    {
        "id": 25,
        "category": "auto_driver",
        "title": "자동차 사고 시 보험처리 vs 자비처리 손익분기점: 3년간 할증액 계산법",
        "intent": "물적사고 할증기준금액(200만원)과 사고 건수 요율에 따른 현명한 판단법",
        "app_feature": "InsureBalance 사고처리 손익 계산기",
        "tags": ["사고보험처리할증", "자비처리계산", "할증기준200만원", "환입제도"]
    },
    {
        "id": 26,
        "category": "auto_driver",
        "title": "교통사고 과실비율 분쟁 심의위원회(분심위) 건너뛰고 바로 소송 가는 법",
        "intent": "분심위 결정의 한계와 과실비율 불복 시 자차 선처리 후 구상금 소송 전략",
        "app_feature": "InsureBalance 과실비율 대처 가이드",
        "tags": ["과실비율분심위", "교통사고소송", "구상금소송", "교통사고과실"]
    },
    {
        "id": 27,
        "category": "auto_driver",
        "title": "음주운전·무면허 사고 자기부담금 대인·대물 전액 구상권: 패가망신의 지름길",
        "intent": "강화된 음주운전 사고부담금 법령과 피해자 보상 후 가해자 전액 구상 체계",
        "app_feature": "InsureBalance 자동차 법규 가이드",
        "tags": ["음주운전사고부담금", "무면허사고구상", "자동차보험법률", "사고부담금전액"]
    },
    {
        "id": 28,
        "category": "auto_driver",
        "title": "자동차보험 환입 제도: 경미한 사고 보험금 토해내고 무사고 등급 살리는 법",
        "intent": "사고 후 갱신 시 보험료 폭탄 피하기 위해 과거 지급 보험금을 환입하는 노하우",
        "app_feature": "InsureBalance 보험금 환입 시뮬레이터",
        "tags": ["자동차보험환입", "보험료할증방지", "무사고할인", "보험금반환"]
    },
    {
        "id": 29,
        "category": "auto_driver",
        "title": "렌터카 완전자차(슈퍼자차)의 함정: 휴차료와 단독사고 보상 제외 약관 확인",
        "intent": "제주도 렌터카 여행 전 원데이 자동차보험 가입으로 비용 70% 아끼는 꿀팁",
        "app_feature": "InsureBalance 원데이 자동차보험 비교",
        "tags": ["렌터카완전자차", "원데이자동차보험", "휴차료보상", "제주도렌터카보험"]
    },
    {
        "id": 30,
        "category": "auto_driver",
        "title": "가족한정 vs 부부한정 vs 1인 한정: 운전자 범위 좁혀서 보험료 20% 낮추기",
        "intent": "실제 운전하는 사람만 지정하여 보험료 절약하고 임시운전자 특약 활용하는 법",
        "app_feature": "InsureBalance 운전자 범위 최적화",
        "tags": ["운전자범위한정", "부부한정특약", "가족한정보험료", "임시운전자특약"]
    },
    {
        "id": 31,
        "category": "auto_driver",
        "title": "블랙박스·첨단안전장치(차선이탈·전방충돌방지) 할인 특약 꼼꼼히 챙기기",
        "intent": "차량 출고 시 장착된 옵션 사진 제출만으로 연간 수만원 환급받는 방법",
        "app_feature": "InsureBalance 자동차 첨단장치 할인 조회",
        "tags": ["블랙박스할인", "첨단안전장치특약", "차선이탈방지할인", "보험료환급"]
    },
    {
        "id": 32,
        "category": "auto_driver",
        "title": "자전거·전동 킥보드(PM) 사고: 자동차보험과 일상생활배상책임 보장 여부",
        "intent": "개인형 이동장치 사고 시 운전자보험 및 일배책 적용 기준과 보상 사각지대",
        "app_feature": "InsureBalance 전동킥보드 보장 체크",
        "tags": ["전동킥보드사고", "자전거사고보험", "일배책킥보드", "PM교통사고"]
    },

    # ── [카테고리 3: life_dental_pet (치아 / 펫 / 일상생활 / 화재)] ──
    {
        "id": 33,
        "category": "life_dental_pet",
        "title": "치아보험 가입 후 언제 임플란트 심어야 100% 받을까? 면책·감액기간 총정리",
        "intent": "치아보험 90일 면책기간과 1~2년 감액기간(50% 지급)을 고려한 똑똑한 치료 일정",
        "app_feature": "InsureBalance 치아보험 보상 시뮬레이터",
        "tags": ["치아보험임플란트", "치아보험면책기간", "감액기간", "크라운보장"]
    },
    {
        "id": 34,
        "category": "life_dental_pet",
        "title": "치아보험 레진 vs 인레이 vs 크라운: 충치 치료비 실속 있게 받는 법",
        "intent": "보존치료(충치 때우기) 보장 한도와 치과 방문 전 고지의무(5년 내 잇몸질환 등)",
        "app_feature": "InsureBalance 치아 보존치료 견적 비교",
        "tags": ["치아보존치료", "크라운보험금", "레진치료보험", "인레이보장"]
    },
    {
        "id": 35,
        "category": "life_dental_pet",
        "title": "펫보험 가입 전 필수: 슬개골 탈구, 피부병, 구강질환 보장되는 상품 찾기",
        "intent": "강아지·고양이 다빈도 질환의 자기부담금과 1일 통원의료비 보장 한도 비교",
        "app_feature": "InsureBalance 펫보험 최저가·보장 비교",
        "tags": ["펫보험비교", "슬개골탈구보험", "강아지보험추천", "반려묘보험"]
    },
    {
        "id": 36,
        "category": "life_dental_pet",
        "title": "일상생활배상책임(일배책) 특약: 월 1,000원으로 1억원 한도 보장받는 법",
        "intent": "아랫집 누수 피해, 자녀가 친구 TV 파손, 반려견이 타인 물었을 때 완벽 보상",
        "app_feature": "InsureBalance 일배책 보장 진단",
        "tags": ["일상생활배상책임", "일배책누수", "반려견사고보상", "1천원특약"]
    },
    {
        "id": 37,
        "category": "life_dental_pet",
        "title": "아파트 누수 사고 시 일배책 청구 가이드: 아랫집 도배 비용과 우리집 방수공사비",
        "intent": "손해방지비용으로 인정되는 우리집 방수공사비 범위와 누수 탐지비 청구 팁",
        "app_feature": "InsureBalance 누수 사고 보상 가이드",
        "tags": ["누수보험청구", "일배책손해방지비용", "아파트누수도배", "방수공사보상"]
    },
    {
        "id": 38,
        "category": "life_dental_pet",
        "title": "주택화재보험 월 1만원대로 가입하기: 이웃집 화재 배상책임과 가전제품 고장 수리비",
        "intent": "실화책임법 개정에 따른 화재 배상책임 및 12대 가전제품 고장 수리비 특약 활용법",
        "app_feature": "InsureBalance 주택화재보험 비교",
        "tags": ["주택화재보험", "가전제품수리비특약", "화재배상책임", "아파트화재보험"]
    },
    {
        "id": 39,
        "category": "life_dental_pet",
        "title": "골절진단비 & 깁스치료비 특약: 통깁스만 보장? 반깁스(부목) 인정 여부",
        "intent": "치아 파손(치아파절) 포함 골절진단비 선택법과 깁스치료비 약관의 함정",
        "app_feature": "InsureBalance 골절 특약 가성비 체크",
        "tags": ["골절진단비", "치아파절포함", "깁스치료비특약", "반깁스보장여부"]
    },
    {
        "id": 40,
        "category": "life_dental_pet",
        "title": "휴대폰 파손보험 vs 일상생활배상책임: 친구 스마트폰 떨어뜨렸을 때 보상법",
        "intent": "친구 폰 파손 시 일배책 자기부담금(20만원)과 통신사 파손보험 중복 여부",
        "app_feature": "InsureBalance 전자기기 파손 보상 가이드",
        "tags": ["휴대폰파손보험", "일배책스마트폰", "자기부담금", "액정파손보상"]
    },
    {
        "id": 41,
        "category": "life_dental_pet",
        "title": "해외여행자보험 가입 안 하고 출국하면 후회하는 3대 이유 (해외 의료비·휴대품 도난)",
        "intent": "미국·동남아 해외 병원비 수천만원 폭탄 방지 및 휴대품 도난 보상 청구법",
        "app_feature": "InsureBalance 해외여행보험 3분 비교",
        "tags": ["해외여행자보험", "해외의료비보상", "휴대품도난보상", "비행기지연특약"]
    },
    {
        "id": 42,
        "category": "life_dental_pet",
        "title": "골프보험(홀인원보험): 홀인원 축하비용 300만원과 골프채 파손 보상 꿀팁",
        "intent": "골프 라운딩 중 타구 사고 배상책임과 홀인원 영수증 청구 요령",
        "app_feature": "InsureBalance 원데이 골프보험 비교",
        "tags": ["골프보험", "홀인원보험", "골프채파손보상", "골프타구사고"]
    },
    {
        "id": 43,
        "category": "life_dental_pet",
        "title": "자녀 학폭(학교폭력) 피해 치료비 특약: 법률 지원과 심리상담 보장 알아보기",
        "intent": "학교폭력대책심의위원회(학폭위) 결과에 따른 피해 치료비 및 법률비용 특약",
        "app_feature": "InsureBalance 어린이 안심 특약 점검",
        "tags": ["학교폭력보험", "학폭피해치료비", "자녀안심보험", "심리상담지원"]
    },
    {
        "id": 44,
        "category": "life_dental_pet",
        "title": "임신·출산 태아보험 가입 시기: 22주 이내 가입해야 선천이상 특약 챙긴다",
        "intent": "태아보험 1차 기형아 검사 전 가입 권장 이유와 산모 특약(임신중독증 등)",
        "app_feature": "InsureBalance 태아보험 주수별 견적 비교",
        "tags": ["태아보험가입시기", "22주태아보험", "선천이상수술비", "산모특약"]
    },
    {
        "id": 45,
        "category": "life_dental_pet",
        "title": "신생아 인큐베이터 입원일당 & 저체중아 출생축하금 특약 똑똑하게 고르기",
        "intent": "고령 임신 증가에 따른 조산 및 저체중아 보장 담보 구성 가이드",
        "app_feature": "InsureBalance 신생아 보장 분석",
        "tags": ["인큐베이터입원일당", "저체중아출생", "태아보험특약", "어린이보험"]
    },
    {
        "id": 46,
        "category": "life_dental_pet",
        "title": "군인 상해보험: 입대 전 군 단체보험과 개인 실손보험 중지 신청 꿀팁",
        "intent": "군 복무 기간 동안 실손보험료 납부 일시 중지하고 제대 후 무심사 부활하는 법",
        "app_feature": "InsureBalance 군복무 실손 중지 가이드",
        "tags": ["군인실손보험중지", "군복무보험료절약", "군인상해보험", "제대후실손부활"]
    },
    {
        "id": 47,
        "category": "life_dental_pet",
        "title": "독감(인플루엔자) 항바이러스제 치료비 특약: 타미플루 처방받고 20만원 받기",
        "intent": "유행성 독감 확진 시 검사비와 처방비 보조하는 생활 밀착형 특약 가치 분석",
        "app_feature": "InsureBalance 생활 질병 특약 조회",
        "tags": ["독감치료비특약", "타미플루보험청구", "인플루엔자특약", "생활보험"]
    },
    {
        "id": 48,
        "category": "life_dental_pet",
        "title": "보이스피싱 사기 피해 보상 특약: 계좌 이체 피해 시 최대 1,000만원 보장",
        "intent": "부모님 타깃 피싱 문자·스미싱 사기 피해를 보상하는 금융 안심 특약",
        "app_feature": "InsureBalance 금융 사기 방어 특약",
        "tags": ["보이스피싱보험", "스미싱피해보상", "금융사기특약", "부모님안심특약"]
    },

    # ── [카테고리 4: savings_annuity (연금 / 저축 / 종신 / 절세)] ──
    {
        "id": 49,
        "category": "savings_annuity",
        "title": "연금저축보험 vs 연금보험 차이: 연말정산 세액공제 최대 99만원 받는 법",
        "intent": "세액공제형(연금저축)과 비과세형(연금보험)의 소득 구간별 유리한 선택 기준",
        "app_feature": "InsureBalance 연말정산 연금 절세 계산기",
        "tags": ["연금저축보험", "연금보험비교", "연말정산세액공제", "비과세연금"]
    },
    {
        "id": 50,
        "category": "savings_annuity",
        "title": "IRP(개인형 퇴직연금)와 연금저축 펀드·보험 최적 배분 전략 (연 900만원 한도)",
        "intent": "연금저축 600만원 + IRP 300만원 조합으로 세액공제 한도 100% 채우기",
        "app_feature": "InsureBalance IRP 연금 포트폴리오 진단",
        "tags": ["IRP세액공제", "연금저축펀드", "연금저축보험비교", "퇴직연금절세"]
    },
    {
        "id": 51,
        "category": "savings_annuity",
        "title": "종신보험 vs 정기보험: 가장의 사망보장, 보험료 1/5로 줄이는 방법",
        "intent": "평생 보장하는 비싼 종신보험 대신 자녀 독립 시기까지만 보장하는 정기보험 추천",
        "app_feature": "InsureBalance 사망보장 가성비 리포트",
        "tags": ["종신보험비교", "정기보험추천", "사망보험금", "가장보험료절약"]
    },
    {
        "id": 52,
        "category": "savings_annuity",
        "title": "사회초년생 종신보험 가입 권유받았다면? 저축성 보험으로 둔갑한 종신 주의보",
        "intent": "높은 사업비로 원금 회복까지 15년 이상 걸리는 종신보험 불완전판매 대처법",
        "app_feature": "InsureBalance 종신보험 원금 회복 분석",
        "tags": ["종신보험저축오인", "사회초년생종신보험", "불완전판매민원", "보험해지환급금"]
    },
    {
        "id": 53,
        "category": "savings_annuity",
        "title": "비과세 저축보험 10년 유지 시 이자소득세 15.4% 면제 조건 총정리",
        "intent": "월납 150만원 이하, 5년 이상 납입 후 10년 유지 시 비과세 혜택 완벽 가이드",
        "app_feature": "InsureBalance 비과세 저축 시뮬레이터",
        "tags": ["비과세저축보험", "이자소득세면제", "10년비과세", "목돈만들기"]
    },
    {
        "id": 54,
        "category": "savings_annuity",
        "title": "경영인정기보험(CEO보험): 법인세 절감과 퇴직금 재원 마련의 명암",
        "intent": "법인 비용 처리(손비 인정) 요건과 국세청 세무조사 리스크 팩트체크",
        "app_feature": "InsureBalance 법인보험 분석",
        "tags": ["경영인정기보험", "법인세절감보험", "CEO퇴직금플랜", "법인보험세무"]
    },
    {
        "id": 55,
        "category": "savings_annuity",
        "title": "변액유니버셜보험(VUL) 펀드 관리법: 채권형과 주식형 스위칭으로 수익률 방어",
        "intent": "방치된 변액보험의 마이너스 수익률 탈출을 위한 펀드 변경 주기와 노하우",
        "app_feature": "InsureBalance 변액보험 펀드 진단",
        "tags": ["변액유니버셜보험", "변액보험펀드변경", "수익률관리", "변액연금"]
    },
    {
        "id": 56,
        "category": "savings_annuity",
        "title": "연금 수령 시 연금소득세(3.3~5.5%)와 건강보험료 피부양자 탈락 기준",
        "intent": "사적연금 연간 1,500만원 초과 시 종합소득세 분리과세 선택 및 건보료 영향",
        "app_feature": "InsureBalance 연금 세금 계산기",
        "tags": ["연금소득세", "건보료피부양자탈락", "사적연금1500만원", "종합소득세분리과세"]
    },
    {
        "id": 57,
        "category": "savings_annuity",
        "title": "상속세 재원 마련용 종신보험: 계약자·수익자를 자녀로 지정해야 하는 이유",
        "intent": "피보험자 부모, 계약자·수익자 자녀 설정 시 상속세 과세 제외되는 절세 플랜",
        "app_feature": "InsureBalance 상속세 절세 종신 컨설팅",
        "tags": ["상속세종신보험", "계약자수익자지정", "상속세재원마련", "절세보험"]
    },
    {
        "id": 58,
        "category": "savings_annuity",
        "title": "퇴직금 IRP 수령 vs 일시금 수령: 퇴직소득세 30~40% 감면받는 법",
        "intent": "IRP 계좌로 퇴직금 이체 후 10년 이상 연금 분할 수령 시 세금 혜택",
        "app_feature": "InsureBalance 퇴직소득세 절세 시뮬레이터",
        "tags": ["퇴직금IRP이체", "퇴직소득세감면", "연금수령절세", "은퇴자금관리"]
    },
    {
        "id": 59,
        "category": "savings_annuity",
        "title": "보증형 연금보험: 종신토록 매달 확정 금액이 나오는 평생 월급 만들기",
        "intent": "투자 손실 위험 없이 기대수명 증가에 대비하는 종신연금형 상품의 장단점",
        "app_feature": "InsureBalance 평생 연금액 계산기",
        "tags": ["종신연금보험", "확정금리연금", "노후준비", "평생월급만들기"]
    },
    {
        "id": 60,
        "category": "savings_annuity",
        "title": "주택연금 vs 연금보험 비교: 내 집으로 평생 연금 받기 vs 금융자산 연금화",
        "intent": "공시지가 12억원 이하 주택연금 가입 요건과 사적연금과의 복합 은퇴 설계",
        "app_feature": "InsureBalance 은퇴 소득 포트폴리오",
        "tags": ["주택연금비교", "사적연금설계", "노후생활비", "은퇴설계"]
    },
    {
        "id": 61,
        "category": "savings_annuity",
        "title": "청년도약계좌 만기 자금 연금저축 계좌로 전환 납입 시 추가 세액공제 혜택",
        "intent": "도약계좌 만기 수령액 중 일부를 연금계좌로 이전하여 세제 혜택 극대화",
        "app_feature": "InsureBalance 청년 재테크 연계 진단",
        "tags": ["청년도약계좌연금전환", "추가세액공제", "청년자산형성", "연금저축납입"]
    },
    {
        "id": 62,
        "category": "savings_annuity",
        "title": "외화달러보험(USD 종신/저축): 환차익 비과세와 달러 자산 배분",
        "intent": "고환율 시기 달러보험 가입 시 주의할 환율 변동 위험과 장기 분산 투자 효과",
        "app_feature": "InsureBalance 달러보험 환율 리스크 체크",
        "tags": ["달러보험", "외화보험비교", "환차익비과세", "글로벌자산배분"]
    },
    {
        "id": 63,
        "category": "savings_annuity",
        "title": "국민연금 조기노령연금 vs 연기연금: 몇 세에 받는 것이 통계적으로 가장 유리할까?",
        "intent": "조기 수령 시 감액률(최대 30%)과 연기 수령 시 가산율(최대 36%)의 손익분기점 나이",
        "app_feature": "InsureBalance 국민연금 최적 수령 나이 계산",
        "tags": ["국민연금수령나이", "조기노령연금", "연기연금손익분기점", "공적연금설계"]
    },
    {
        "id": 64,
        "category": "savings_annuity",
        "title": "연금저축 중도해지 시 기타소득세 16.5% 페널티: 세액공제 뱉어내지 않는 특수해지 사유",
        "intent": "천재지변, 3개월 이상 요양, 개인회생·파산 등 부득이한 사유로 저율 과세 해지법",
        "app_feature": "InsureBalance 연금저축 특수해지 가이드",
        "tags": ["연금저축중도해지", "기타소득세16.5", "특수해지사유", "연금해지페널티"]
    },

    # ── [카테고리 5: claims_knowhow (보험금 청구 / 부지급 대처 / 분쟁 / 노하우)] ──
    {
        "id": 65,
        "category": "claims_knowhow",
        "title": "실손보험 청구 서류 3분 만에 준비하기: 진료비 영수증 vs 세부내역서 차이",
        "intent": "병원에서 떼야 하는 무료 서류와 유료 서류 구분 및 모바일 간편 청구 요령",
        "app_feature": "InsureBalance 서류 없는 1초 보험금 청구",
        "tags": ["보험금청구서류", "진료비세부내역서", "실비청구방법", "모바일보험금청구"]
    },
    {
        "id": 66,
        "category": "claims_knowhow",
        "title": "보험사 현장심사(손해사정사 면담) 나올 때 절대 서명하면 안 되는 서류 3가지",
        "intent": "의무기록 열람 동의서의 함정과 국세청 홈택스 자료 제출 요구 거부 권리",
        "app_feature": "InsureBalance 현장심사 대응 매뉴얼",
        "tags": ["보험사현장심사", "손해사정사서명주의", "의무기록열람동의", "보험금지급거절"]
    },
    {
        "id": 67,
        "category": "claims_knowhow",
        "title": "보험금 부지급 통보받았을 때 역전하는 3단계: 금융감독원 민원과 재심사 청구",
        "intent": "보험사 자체 의료자문 결과에 반박하는 주치의 소견서 확보 및 금감원 민원 팁",
        "app_feature": "InsureBalance 부지급 이의신청 가이드",
        "tags": ["보험금부지급대처", "금감원민원넣는법", "의료자문거부", "보험금재심사"]
    },
    {
        "id": 68,
        "category": "claims_knowhow",
        "title": "독립 손해사정사 무료 선임 권리(단독 손사): 소비자가 비용 안 내고 선임하는 법",
        "intent": "보험업법 개정으로 보험금 청구 시 소비자가 직접 손해사정사를 선임하는 제도",
        "app_feature": "InsureBalance 독립 손사 매칭 가이드",
        "tags": ["독립손해사정사", "손사선임비용보험사부담", "보험금분쟁해결", "소비자권리"]
    },
    {
        "id": 69,
        "category": "claims_knowhow",
        "title": "숨은 내 보험금 찾기(내보험찾아줌): 잠자는 환급금 12조원 즉시 조회하고 입금받기",
        "intent": "만기보험금, 중도보험금, 휴면보험금 조회 시스템 활용법과 숨은 돈 찾기",
        "app_feature": "InsureBalance 숨은 보험금 1분 조회",
        "tags": ["내보험찾아줌", "숨은보험금찾기", "휴면보험금조회", "환급금조회"]
    },
    {
        "id": 70,
        "category": "claims_knowhow",
        "title": "고지의무 위반과 제척기간(3년): 가입 전 병력 숨겨도 3년 지나면 해지 못할까?",
        "intent": "상법 제651조 고지의무 위반 해지권 제척기간의 진실과 사기에 의한 계약 취소",
        "app_feature": "InsureBalance 고지의무 안전 진단",
        "tags": ["고지의무위반", "보험제척기간3년", "보험강제해지", "상법651조"]
    },
    {
        "id": 71,
        "category": "claims_knowhow",
        "title": "직업 변경 고지의무 위반으로 보험금 삭감된 사연: 사무직에서 현장직 변경 시 필수",
        "intent": "상해급수 1급에서 3급으로 변경 시 통지의무를 다해야 삭감 없이 전액 보상",
        "app_feature": "InsureBalance 직업 급수 변경 체크",
        "tags": ["직업변경고지", "상해급수변경", "보험금비례삭감", "통지의무위반"]
    },
    {
        "id": 72,
        "category": "claims_knowhow",
        "title": "보험금 청구 소멸시효 3년: 3년 전 치료받은 영수증 지금 청구해도 나올까?",
        "intent": "사고일이 아닌 치료일 기준 3년 이내 건은 모두 소급 청구 가능한 법적 근거",
        "app_feature": "InsureBalance 지난 3년 미청구 영수증 찾기",
        "tags": ["보험금소멸시효3년", "지난영수증청구", "미청구보험금", "소급청구"]
    },
    {
        "id": 73,
        "category": "claims_knowhow",
        "title": "통원 치료 1일 한도 25만원 초과할 때: 입원 처리로 수백만원 실비 받는 기준",
        "intent": "입원(6시간 이상 체류 및 의사 관찰) 기준과 낮병동 입원료 인정 요건",
        "app_feature": "InsureBalance 입원 vs 통원 실비 한도 가이드",
        "tags": ["통원한도25만원", "실비입원한도5천만원", "낮병동입원", "당일입원보험"]
    },
    {
        "id": 74,
        "category": "claims_knowhow",
        "title": "실손보험 중복 가입자(회사 단체보험 + 개인 실손): 개인 실손 중지하고 환급받기",
        "intent": "비례보상으로 중복 보장 안 되는 실손보험료 이중 납부 방지 및 단체실손 연계",
        "app_feature": "InsureBalance 실손 중복 가입 조회",
        "tags": ["단체실손개인실손", "실비중복가입", "개인실손중지제도", "보험료이중납부방지"]
    },
    {
        "id": 75,
        "category": "claims_knowhow",
        "title": "정신과 치료(F코드) 받으면 실손보험·암보험 가입 평생 거절될까?",
        "intent": "우울증, 불면증, ADHD 진료 후 실비 보장 여부(F01~F03, F40~F48 등)와 유병자 가입",
        "app_feature": "InsureBalance 정신과 진료 이력 가입 가이드",
        "tags": ["정신과F코드실손", "우울증보험가입", "불면증진료기록", "정신과보험거절"]
    },
    {
        "id": 76,
        "category": "claims_knowhow",
        "title": "보험사 의료자문 동의서 거부권: 보험사 전속 의사의 엉터리 판정 막는 법",
        "intent": "제3의 대학병원 재감정 요구 권리와 보험사 자체 자문 결과 무효화 전략",
        "app_feature": "InsureBalance 의료자문 분쟁 솔루션",
        "tags": ["의료자문동의서거부", "제3대학병원자문", "보험금지급분쟁", "환자권리"]
    },
    {
        "id": 77,
        "category": "claims_knowhow",
        "title": "치료 목적 vs 미용 목적 분쟁: 안검하수 눈꺼풀 수술 실손보험 받는 법",
        "intent": "시야 장애 진단서와 안과 시야검사 결과지를 통한 실손 인정 노하우",
        "app_feature": "InsureBalance 안검하수 보상 가이드",
        "tags": ["안검하수실손보험", "치료목적성형", "시야장애진단서", "쌍꺼풀수술보험"]
    },
    {
        "id": 78,
        "category": "claims_knowhow",
        "title": "하지정맥류 레이저 수술 실비 청구: 보건복지부 신의료기술 인정 요건",
        "intent": "초음파 검사상 역류 소견 0.5초 이상 확인서로 부지급 막는 핵심 팁",
        "app_feature": "InsureBalance 하지정맥류 청구 체크",
        "tags": ["하지정맥류실비", "혈관초음파역류소견", "비급여수술비", "실손보험부지급"]
    },
    {
        "id": 79,
        "category": "claims_knowhow",
        "title": "비급여 주사제(마늘주사, 백옥주사, 영양주사): 실손보험 청구 시 식품의약품안전처 허가 기준",
        "intent": "식약처 허가 효능·효과에 부합하는 질병 치료 목적 소견서 작성 요령",
        "app_feature": "InsureBalance 영양주사 실비 청구 기준",
        "tags": ["비급여주사제실손", "식약처허가범위", "영양주사보험청구", "치료소견서"]
    },
    {
        "id": 80,
        "category": "claims_knowhow",
        "title": "보험금 지연이자 받는 법: 청구 후 3영업일 넘어가면 연 4~8% 이자 붙는다",
        "intent": "보험금 지급 지연 시 보험회사의 약관상 지연이자 지급 의무와 독촉 요령",
        "app_feature": "InsureBalance 보험금 지연이자 계산기",
        "tags": ["보험금지연이자", "보험금지급기한", "약관상이자율", "보험금독촉"]
    },

    # ── [카테고리 6: remodeling_savings (보험 리모델링 / 특약 다이어트 / 절약)] ──
    {
        "id": 81,
        "category": "remodeling_savings",
        "title": "월 보험료 30만원 내는데 보장은 빈약? 보험 리모델링으로 10만원대 줄이기",
        "intent": "중복 특약 삭제, 적립보험료 0원 전환, 보장 분석표를 통한 거품 제거 실전",
        "app_feature": "InsureBalance AI 보험 리모델링 진단",
        "tags": ["보험리모델링", "보험료다이어트", "적립보험료삭제", "중복보험정리"]
    },
    {
        "id": 82,
        "category": "remodeling_savings",
        "title": "적립보험료의 함정: 매달 5만원씩 보험사에 무이자로 빌려주고 있었다고?",
        "intent": "보장보험료 외에 얹어 내는 적립보험료를 즉시 삭제하여 월 납입금 낮추기",
        "app_feature": "InsureBalance 적립보험료 즉시 삭제 가이드",
        "tags": ["적립보험료함정", "보장보험료비교", "보험료줄이기", "환급금의진실"]
    },
    {
        "id": 83,
        "category": "remodeling_savings",
        "title": "갱신형 vs 비갱신형 보험: 2030 세대가 갱신형 가입하면 60대에 보험료 10배 폭탄",
        "intent": "초기 보험료가 저렴한 갱신형의 위험성과 20년납 100세만기 비갱신형의 안전성",
        "app_feature": "InsureBalance 갱신 vs 비갱신 평생 보험료 비교",
        "tags": ["갱신형보험폭탄", "비갱신형보험추천", "보험료인상률", "20년납100세만기"]
    },
    {
        "id": 84,
        "category": "remodeling_savings",
        "title": "사회초년생 첫 보험 포트폴리오 완벽 가이드: 월 7~10만원으로 끝내는 3대 세팅",
        "intent": "1순위 실손 + 2순위 3대 진단비(비갱신) + 3순위 운전자/일배책 조합법",
        "app_feature": "InsureBalance 사회초년생 맞춤 플랜",
        "tags": ["사회초년생보험", "첫보험추천", "월7만원보험", "20대재테크"]
    },
    {
        "id": 85,
        "category": "remodeling_savings",
        "title": "무해지(해약환급금 미지급형) 환급형 보험: 일반형보다 보험료 30% 저렴한 이유",
        "intent": "납입 기간 중 해지 환급금이 없는 대신 월 보험료를 대폭 낮춘 가성비 구조",
        "app_feature": "InsureBalance 무해지 환급형 최저가 비교",
        "tags": ["무해지환급형", "가성비보험", "보험료30프로할인", "해약환급금미지급"]
    },
    {
        "id": 86,
        "category": "remodeling_savings",
        "title": "CI보험(중대한 질병 보험) 가입자 필수 확인: 암에 걸려도 돈 안 나오는 이유",
        "intent": "'중대한(Critical)' 조건 충족이 까다로운 구형 CI보험 진단비 정상화 리모델링",
        "app_feature": "InsureBalance CI보험 약관 해부 리포트",
        "tags": ["CI보험의함정", "중대한질병조건", "CI보험리모델링", "일반암진단비전환"]
    },
    {
        "id": 87,
        "category": "remodeling_savings",
        "title": "부모님 6070 보험 리모델링: 비싼 갱신형 암보험 정리하고 간병비·수술비로 재배치",
        "intent": "나이 들수록 급증하는 간병비와 입원·수술비 위주로 부모님 맞춤 설계하는 법",
        "app_feature": "InsureBalance 부모님 보험 효도 진단",
        "tags": ["부모님보험리모델링", "60대보험추천", "간병비보험재배치", "노후건강보험"]
    },
    {
        "id": 88,
        "category": "remodeling_savings",
        "title": "보험 감액완납 제도: 보험료 내기 힘들 때 해지하지 않고 보장 유지하는 비결",
        "intent": "지금까지 낸 해약환급금으로 완납 처리하고 보장 금액만 줄여 유지하는 제도",
        "app_feature": "InsureBalance 보험 유지 솔루션",
        "tags": ["감액완납제도", "보험해지방지", "보험료납입부담", "보장축소유지"]
    },
    {
        "id": 89,
        "category": "remodeling_savings",
        "title": "보험 중도인출 vs 보험계약대출(약관대출): 신용등급 영향 없이 급전 마련하기",
        "intent": "해약환급금 범위 내 대출의 금리와 중도인출 수수료 없는 활용법 비교",
        "app_feature": "InsureBalance 약관대출 금리 비교",
        "tags": ["보험약관대출", "보험중도인출", "신용등급영향없음", "비상금마련"]
    },
    {
        "id": 90,
        "category": "remodeling_savings",
        "title": "사망보험금 1억원 필요한 시기: 신혼부부 맞춤 정기보험 월 2~3만원 설계",
        "intent": "아이 출생 후 자녀 독립 시점(25세)까지만 집중 보장하는 가성비 정기보험",
        "app_feature": "InsureBalance 신혼부부 가장 플랜",
        "tags": ["정기보험설계", "신혼부부보험", "사망보험금1억", "월3만원사망보장"]
    },
    {
        "id": 91,
        "category": "remodeling_savings",
        "title": "보험 증권 1장으로 내 보장 100% 읽는 법: 담보명, 가입금액, 갱신여부 보는 눈",
        "intent": "복잡한 보험증권에서 필수 5대 담보만 3분 만에 찾아내는 초보자 가이드",
        "app_feature": "InsureBalance AI 보험증권 자동 분석기",
        "tags": ["보험증권보는법", "보장분석표", "필수담보확인", "보험진단"]
    },
    {
        "id": 92,
        "category": "remodeling_savings",
        "title": "통합보험 하나로 다 된다는 설계사의 거짓말: 생명보험 vs 손해보험 분산 가입 원칙",
        "intent": "사망은 생명보험, 뇌·심장 및 수술비·실손은 손해보험이 압도적으로 유리한 이유",
        "app_feature": "InsureBalance 생보사 vs 손보사 조합 플랜",
        "tags": ["생명보험손해보험차이", "통합보험단점", "분산가입원칙", "보험설계노하우"]
    },
    {
        "id": 93,
        "category": "remodeling_savings",
        "title": "보험료 자동이체 통장 잔고 부족으로 실효(효력 상실)됐을 때 부활 청약 요령",
        "intent": "실효 후 3년 이내 연체 보험료와 이자 납입 후 무심사 또는 간이심사 부활법",
        "app_feature": "InsureBalance 실효 보험 부활 가이드",
        "tags": ["보험실효부활", "보험료연체", "효력상실대처", "부활청약"]
    },
    {
        "id": 94,
        "category": "remodeling_savings",
        "title": "골다공증·당뇨약 복용 중인 부모님: 고지혈증 있어도 할증 없는 최신 유병자 플랜",
        "intent": "만성질환자도 정상체와 큰 차이 없는 보험료로 가입 가능한 3·10·5 초간편 플랜",
        "app_feature": "InsureBalance 부모님 만성질환 플랜",
        "tags": ["당뇨고혈압보험", "골다공증보험", "초간편유병자", "부모님맞춤보험"]
    },
    {
        "id": 95,
        "category": "remodeling_savings",
        "title": "보험 다이어트 후 남은 돈으로 매달 15만원 ETF 적립식 투자하는 재테크 공식",
        "intent": "과도한 보장성 보험료를 줄여 실질적인 은퇴 자산 및 투자 시드머니로 전환하기",
        "app_feature": "InsureBalance 자산 배분 전환 시뮬레이터",
        "tags": ["보험료다이어트재테크", "보험줄여ETF투자", "목돈만들기", "가계지출절약"]
    },
    {
        "id": 96,
        "category": "remodeling_savings",
        "title": "치아보험 2개 중복 가입하면 임플란트 2배로 나올까? 중복 보장 체크리스트",
        "intent": "정액보상 특약(진단비, 수술비, 치아)과 비례보상 특약(실손, 일배책)의 차이점",
        "app_feature": "InsureBalance 중복 보장 가능 여부 판독",
        "tags": ["정액보상비례보상", "치아보험중복가입", "수술비중복수령", "보험금두배"]
    },
    {
        "id": 97,
        "category": "remodeling_savings",
        "title": "보험 청약 철회 제도: 가입 후 30일 이내면 100% 전액 환불받는 법",
        "intent": "증권 받은 날로부터 15일, 청약일로부터 30일 이내 무조건 계약 취소 권리",
        "app_feature": "InsureBalance 청약철회 1분 가이드",
        "tags": ["보험청약철회", "가입후30일취소", "보험료100프로환불", "단순변심해지"]
    },
    {
        "id": 98,
        "category": "remodeling_savings",
        "title": "품질보증해지 제도: 약관 미전달, 자필서명 누락 시 3개월 이내 원금+이자 환불",
        "intent": "3대 기본 지키기 위반 시 납입한 보험료 전액과 약정이자까지 돌려받는 강력한 무기",
        "app_feature": "InsureBalance 불완전판매 구제 신청",
        "tags": ["품질보증해지", "자필서명누락", "보험료전액환불", "불완전판매취소"]
    },
    {
        "id": 99,
        "category": "remodeling_savings",
        "title": "단독 실손보험만 가입하고 싶은데 끼워팔기 거절당했을 때 대처법",
        "intent": "금융소비자보호법상 실손 단독 가입 거부 금지 규정과 다이렉트 단독 가입 노하우",
        "app_feature": "InsureBalance 단독 실손 다이렉트 가입처",
        "tags": ["단독실손가입", "실비끼워팔기거절", "금소법위반", "다이렉트단독실비"]
    },
    {
        "id": 100,
        "category": "remodeling_savings",
        "title": "InsureBalance 3분 AI 보험 진단: 내 보험 보장 점수 확인하고 최적 리모델링 끝내기",
        "intent": "국내 30여 개 보험사 상품을 1초 만에 분석하여 과보장/부족보장 완벽 진단",
        "app_feature": "InsureBalance 원클릭 AI 통합 리포트",
        "tags": ["InsureBalance", "AI보험진단", "보험비교플랫폼", "보험리모델링앱"]
    }
]


def get_all_topics() -> List[Dict[str, Any]]:
    return INSURANCE_100_TOPICS


def get_topic_by_id(topic_id: int) -> Dict[str, Any]:
    for t in INSURANCE_100_TOPICS:
        if t["id"] == topic_id:
            return t
    return INSURANCE_100_TOPICS[0]


def get_topics_by_category(category: str) -> List[Dict[str, Any]]:
    return [t for t in INSURANCE_100_TOPICS if t["category"] == category]
