"""
Stock Scenario & Prompt Director (주식 AI 앱 Stock Master AI 전용 프롬프트 디렉터)
- C:\\Users\\zkfnt\\Desktop\\stock ai\\stock 소스 기반
  (aiApi.js, stockApi.js, KIS 실시간 시세, Gemini 종목 심층 분석)
- 전연령 개인투자자 타겟 장전 08:30 AI 급등 테마, 외인/기관 수급 분석, 디시 주갤/뽐뿌 증권 포스팅 원고 자동 생성
"""

import random
from typing import Dict, Any, List


class StockPromptDirector:
    BRAND_NAME = "Stock Master AI (주식마스터 AI)"
    LANDING_URL = "https://stockmaster-ai.vercel.app/"

    THEMES = [
        "premarket_themes",     # 장전 08:30 AI 급등 유망 테마 TOP 3
        "institutional_flow",   # 오늘 외인/기관 순매수 집중 종목 긴급 분석
        "condition_screener",   # 골든크로스 & 거래량 폭증 AI 조건검색식
        "closing_briefing"      # 장마감 주도 섹터 및 내일 대응 전략
    ]

    @classmethod
    def generate_blog_content(cls) -> Dict[str, Any]:
        """네이버/티스토리용 장문 주식 분석 칼럼 원고 생성"""
        titles = [
            "2026 내일 장 시작 전 꼭 봐야 할 AI 추천 급등 테마 TOP 3",
            "외국인·기관 쌍끌이 순매수 유입 종목 긴급 차트/수급 팩트체크",
            "단타 매매 필승 공식: AI가 포착한 거래량 급증 골든크로스 종목군",
            "삼성전자·SK하이닉스 눌림목 매수 타이밍과 AI 산출 목표주가"
        ]
        title = random.choice(titles)
        content_html = f"""
        <h2>내일 주식 시장을 주도할 핵심 섹터는 어디인가?</h2>
        <p>안녕하세요. Stock Master AI 주식 전략 연구소입니다. 매일 아침 수많은 뉴스와 테마 속에서 진짜 수급이 쏠리는 종목을 선별하는 것은 개인 투자자에게 가장 중요한 과제입니다.</p>
        <hr/>
        <h3>1. 외국인 및 기관 순매수 자금의 이동 경로 포착</h3>
        <p>단순 호재성 뉴스에 현혹되지 마시고, 메이저 수급 주체(외국인, 사모펀드, 연기금)가 조용히 바닥권에서 3영업일 이상 연속 매집 중인 종목을 추적해야 승률이 올라갑니다.</p>
        <h3>2. 보조지표와 거래량 회전율을 통한 변곡점 진단</h3>
        <p>RSI 과매도 탈출 구간과 일봉상 20일 이동평균선 안착 여부를 AI가 실시간 스캔하여 리스크 대비 기대 수익률이 높은 손익비 구간을 도출합니다.</p>
        <h3>3. 10분마다 350개 주도주를 스캔하는 Stock Master AI 계량 전광판</h3>
        <p>코스피·코스닥 350개 핵심 종목의 체결강도, 블록오더, 외국계 수급을 10분마다 전수 조사하여 실시간 주도주와 -5% 실시간 문자 손절 알림을 100% 무료로 제공합니다.</p>
        <hr/>
        <div style="margin-top:20px; padding:15px; background:#09090b; border-left:4px solid #10b981; border-radius:8px; color:#fff;">
          <strong>📈 [StockMaster AI] 10분마다 실시간 350개 국내 주도주 정밀 분석!</strong><br/>
          뇌동매매는 이제 그만! AI 리스크 방어 신호와 손익비 전략을 지금 확인하세요.<br/>
          <a href="{cls.LANDING_URL}" target="_blank" style="color:#10b981; font-weight:bold;">👉 실시간 전광판 바로가기: {cls.LANDING_URL}</a>
        </div>
        """
        return {
            "title": title,
            "content_html": content_html,
            "tags": ["주식추천", "급등주", "주식시황", "주식마스터AI", "10분전광판", "체결강도"]
        }

    @classmethod
    def generate_dcinside_post(cls) -> Dict[str, str]:
        """디시인사이드 주식갤러리/미주갤 정보글 원고 생성"""
        return {
            "gallery": "neostock",
            "title": "[정보] 장전 08:30 오늘 외인/기관 수급 쏠릴 유망 섹터 AI 데이터 요약",
            "content": (
                "<p>장 시작 전에 메이저 수급 이동 데이터 공유합니다.</p>"
                "<p>1. 반도체 소부장 밸류체인 쪽으로 기관 연속 순매수 유입 감지</p>"
                "<p>2. 2차전지/로봇 섹터 단기 낙폭과대 반등 자리 형성</p>"
                "<p>3. 섣부른 시초가 갭상승 추격 매수보다는 9시 30분 이후 눌림목 확인하고 진입하는 걸 권장합니다.</p>"
            )
        }

    @classmethod
    def generate_ppomppu_post(cls) -> Dict[str, str]:
        """뽐뿌 증권포럼 정보글 원고 생성"""
        return {
            "board": "stock",
            "title": "[시황] 오늘 코스피/코스닥 외인 매매동향 및 수급 특징주 정리",
            "content": (
                "회원님들 성투하고 계십니까. 오늘 시장 메이저 수급 특이사항 정리해서 올립니다.\n\n"
                "• 코스피: 외인 현물 순매수 전환하며 대형 IT 섹터 지수 견인\n"
                "• 코스닥: 제약/바이오 및 AI 소프트웨어 테마로 순환매 지속\n\n"
                "변동성이 큰 장세인 만큼 비중 조절과 분할 매수 원칙 꼭 지키시길 바랍니다."
            )
        }


if __name__ == "__main__":
    director = StockPromptDirector()
    blog = director.generate_blog_content()
    print("주식 블로그 제목:", blog["title"])
    dc = director.generate_dcinside_post()
    print("디시 주갤 제목:", dc["title"])
