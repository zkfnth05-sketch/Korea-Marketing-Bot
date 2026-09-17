"""
Insurance Scenario & Prompt Director (보험 비교 앱 InsureBalance 전용 프롬프트 디렉터)
- C:\\Users\\zkfnt\\Desktop\\insurance-comparison-main 소스 기반
  (InsuranceCalculator, AIPremiumReport, 실손/암/뇌심장 공시실 데이터)
- 3050 직장인/가장/주부 타겟 보험료 다이어트, 실손 갱신 폭탄 탈출, 뽐뿌/보배드림 꿀팁 원고 자동 생성
"""

import random
from typing import Dict, Any, List


class InsurancePromptDirector:
    BRAND_NAME = "InsureBalance (인슈어밸런스)"
    LANDING_URL = "https://insurebalance.co.kr"

    THEMES = [
        "silson_renewal",      # 실손보험 갱신 폭탄 피하기
        "cancer_comparison",   # 주요 보험사별 암보험 실시간 가격 비교
        "diet_150k",           # 매달 새는 보험료 15만원 다이어트 꿀팁
        "driver_insurance"     # 운전자보험 필수 특약 체크리스트
    ]

    @classmethod
    def generate_blog_content(cls) -> Dict[str, Any]:
        """네이버/티스토리용 장문 SEO 칼럼 원고 생성"""
        titles = [
            "2026 실손보험 갱신 폭탄 피하는 합법적인 리모델링 3단계",
            "보험사별 암보험 실시간 가격 비교: 메리츠 vs 삼성화재 vs 신한라이프",
            "매달 내는 보험료에서 15만 원 줄이는 숨은 중복 특약 정리법",
            "운전자보험 만기환급형 들면 손해인 이유와 필수 특약 총정리"
        ]
        title = random.choice(titles)
        content_html = f"""
        <h2>매달 나가는 보험료, 제대로 보장받고 계신가요?</h2>
        <p>안녕하세요. 가계 금융 절약 솔루션 가이드입니다. 30~50대 직장인과 가장들의 고정 지출 중 가장 큰 비중을 차지하면서도 방치되기 쉬운 항목이 바로 '보험료'입니다.</p>
        <hr/>
        <h3>1. 갱신형 vs 비갱신형 특약의 함정 점검</h3>
        <p>초기 보험료가 저렴하다고 가입했던 갱신형 특약은 50대, 60대에 접어들면 보험료가 3~5배 이상 폭증하여 결국 해지하게 되는 원인이 됩니다. 핵심 3대 질병(암, 뇌혈관, 허혈성심장)은 반드시 비갱신형으로 세팅되어 있는지 확인해야 합니다.</p>
        <h3>2. 불필요한 중복 담보 다이어트로 월 15만 원 절감</h3>
        <p>여러 보험에 중복 가입된 입원일당, 골절진단비 등 가성비가 떨어지는 특약만 정리해도 4인 가족 기준 매달 15만 원 이상의 고정 지출을 합법적으로 아낄 수 있습니다.</p>
        <h3>3. AI 기반 객관적인 실시간 보험 비교 리포트 활용</h3>
        <p>인슈어밸런스(InsureBalance)는 국내 메이저 보험사의 실제 공시실 데이터를 기반으로 내 나이, 성별에 맞는 최적의 보장 견적과 과다 납입 진단을 3초 만에 무료로 제공합니다.</p>
        """
        return {
            "title": title,
            "content_html": content_html,
            "tags": ["실손보험갱신", "암보험비교", "보험료절약", "인슈어밸런스", "보험리모델링"]
        }

    @classmethod
    def generate_ppomppu_post(cls) -> Dict[str, str]:
        """뽐뿌 재테크/보험 포럼 정보글 원고 생성"""
        return {
            "board": "money",
            "title": "[정보/후기] 10년 묵힌 보험증권 뜯어보고 불필요한 특약 빼서 월 13만원 줄인 썰",
            "content": (
                "안녕하세요 회원님들. 최근 고정비 줄이려고 집안 보험증권 전부 모아서 분석해봤습니다.\n\n"
                "1. 예전에 지인 통해서 들었던 종신보험에 불필요한 사망보장이 과하게 잡혀있더군요.\n"
                "2. 실손보험과 중복되는 입원일당 특약 정리하고, 암진단비만 비갱신으로 재조정했습니다.\n"
                "3. 객관적으로 보험사별 가격 비교표 확인해보니 같은 보장인데도 보험사마다 월 3~4만원씩 차이가 납니다.\n\n"
                "혹시 갱신 통지서 받으신 분들은 증권 꼭 한번 자가진단 해보세요. 생각보다 새는 돈이 엄청 많습니다."
            )
        }

    @classmethod
    def generate_bobaedream_post(cls) -> Dict[str, str]:
        """보배드림 교통/사고 게시판 운전자보험 팁 생성"""
        return {
            "board": "accident",
            "title": "[팁] 운전자보험 가입할 때 호갱 안 당하는 3대 필수 특약 정리",
            "content": (
                "보배 형님들 안녕하십니까.\n"
                "운전자보험 만원짜리 들면서도 정작 중요한 특약 빠뜨리는 경우가 많아서 핵심만 정리해 드립니다.\n\n"
                "1. 교통사고처리지원금(형사합의금): 최소 2억 이상 세팅\n"
                "2. 변호사선임비용: 경찰조사 단계부터 보장되는지 필수 확인\n"
                "3. 자동차사고부상치료비(자부상): 14급 기준 보장 한도 체크\n\n"
                "불필요한 적립보험료 넣지 마시고 순수보장형으로 1만원대 초반 맞추는 게 제일 깔끔합니다. 안전운전 하십시오!"
            )
        }


if __name__ == "__main__":
    director = InsurancePromptDirector()
    blog = director.generate_blog_content()
    print("보험 블로그 제목:", blog["title"])
    ppomppu = director.generate_ppomppu_post()
    print("뽐뿌 제목:", ppomppu["title"])
