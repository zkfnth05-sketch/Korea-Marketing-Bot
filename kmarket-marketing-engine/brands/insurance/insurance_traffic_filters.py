# -*- coding: utf-8 -*-
"""
[보험 리밸런스 전용 독립 모듈] InsuranceTrafficFilters (brands/insurance/insurance_traffic_filters.py)
=============================================================================
• 역할: 대시보드 통계에서 데모/체험/테스트 데이터 제외 (실제 방문자·실제 상담신청만 집계)
• 근거(실측): customer_leads.is_demo=True 13건, 체험 계정(test, test_planner, p1~p4)의 planner_id,
  ※ 010-0000-0000 은 익명 AI 자가진단 '실제' 리드의 자리표시 번호(284건)이므로 테스트로 취급하지 않음.
"""

DEMO_PLANNER_CODES = {"test", "test_planner", "p1", "p2", "p3", "p4"}
DEMO_PLANNER_IDS = {f"{str(n) * 8}-{str(n) * 4}-4{str(n) * 3}-a{str(n) * 3}-{str(n) * 12}" for n in range(1, 7)}
TEST_PHONES = {"010-1234-5678", "010-9999-8888", "010-6666-5555", "010-1111-2222"}


def is_demo_visitor(planner_code: str, utm_source: str) -> bool:
    return (planner_code or "").lower() in DEMO_PLANNER_CODES or (utm_source or "").lower() in ("test", "demo")


def is_demo_lead(is_demo, planner_id: str, phone: str) -> bool:
    if is_demo:
        return True
    if (planner_id or "") in DEMO_PLANNER_IDS:
        return True
    return (phone or "").strip() in TEST_PHONES
