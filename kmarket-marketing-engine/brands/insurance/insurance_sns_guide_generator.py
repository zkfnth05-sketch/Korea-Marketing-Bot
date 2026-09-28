# -*- coding: utf-8 -*-
"""
InsuranceSNSGuideGenerator - 📝 [보험 리밸런스 8대 국민 보험 SNS 포스팅 가이드 자동 생성기]
- 유튜브 숏폼 (YouTube Shorts)
- 틱톡 (TikTok)
- 인스타그램 릴스 (Instagram Reels)
- 네이버 클립 (Naver Clip)
- 페이스북 릴스 (Facebook Reels)
- 심의 프리패스형 1인칭 제목, 설명란, 해시태그, 고정 댓글, 클린 디스클레이머(면책고지) 완벽 탑재
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

INSURANCE_SNS_TEMPLATES = {
    1: {
        "title": "병원 일 년에 한 번도 안 가는데 옛날 실비보험 5만원 내다 1만원대로 줄인 썰 #shorts",
        "hook_summary": "매달 5만원 넘게 내던 옛날 실비... 4세대로 바꾸고 월 12,000원으로 고정지출 시원하게 다이어트한 현실 후기",
        "hashtags": ["#실비보험", "#4세대실손", "#실손보험", "#보험료줄이기", "#보험리밸런스", "#shorts"],
        "pinned_comment": "📌 전화번호 없이 익명으로 4세대 전환 손익 확인하기 👉 네이버에 [보험 리밸런스] 검색! (공식 사이트: https://insure-rebalance.vercel.app/)"
    },
    2: {
        "title": "운전자보험에 3~4만원씩 내고 계신가요? 1만원이면 충분한 이유 ㄷㄷ #shorts",
        "hook_summary": "자동차보험이랑 헷갈려서 4만원씩 내던 운전자보험... 벌금, 변호사, 합의금 3대 특약만 넣고 월 1만 3천 원으로 다이어트한 비결",
        "hashtags": ["#운전자보험", "#교통사고", "#벌금", "#변호사선임비", "#운전자보험1만원", "#보험리밸런스", "#shorts"],
        "pinned_comment": "📌 내 운전자보험 쓸데없는 중복 특약 점검하기 👉 네이버에 [보험 리밸런스] 검색!"
    },
    3: {
        "title": "암보험 5천만원 들었는데 갑상선암은 5백만원만 나오는 충격적인 이유 #shorts",
        "hook_summary": "소액암, 유사암 분류 기준 모르면 암 걸리고도 보험금 10%밖에 못 받습니다! 건강검진 전 필수 확인 약관",
        "hashtags": ["#암보험", "#유사암", "#갑상선암", "#암진단비", "#건강검진", "#보험리밸런스", "#shorts"],
        "pinned_comment": "📌 내 암보험 증권 소액암 보장 한도 무료 점검 👉 네이버에 [보험 리밸런스] 검색!"
    },
    4: {
        "title": "뇌경색 환자 80%가 옛날 뇌출혈 특약 때문에 1원도 못 받는 진짜 이유 #shorts",
        "hook_summary": "가장 흔한 뇌경색은 뇌출혈 특약에서 1원도 안 나옵니다! 증권에 '뇌혈관질환'이라고 적혀 있는지 지금 확인하세요",
        "hashtags": ["#뇌혈관질환", "#뇌출혈", "#뇌경색", "#협심증", "#건강보험", "#보험리밸런스", "#shorts"],
        "pinned_comment": "📌 내 뇌·심장 보험 보장 범위 판독기 👉 네이버에 [보험 리밸런스] 검색!"
    },
    5: {
        "title": "적금인 줄 알고 매달 30만원씩 붓던 종신보험... 사업비 30% 떼인 거 알고 멘붕 온 썰 #shorts",
        "hook_summary": "사망보장은 정기보험으로 월 3만원에 세팅하고 남은 27만원 저축해서 20년간 6,480만원 아낀 썰",
        "hashtags": ["#종신보험", "#정기보험", "#사망보험금", "#사회초년생", "#재테크", "#보험리밸런스", "#shorts"],
        "pinned_comment": "📌 종신보험 불필요한 적립금 다이어트 계산기 👉 네이버에 [보험 리밸런스] 검색!"
    },
    6: {
        "title": "부모님이 100세 만기로 들어준 어린이보험... 서른 살 넘어 증권 뜯어보고 깜짝 놀란 이유 #shorts",
        "hook_summary": "옛날 보험이라 갱신형에 뇌출혈만 가득했던 어린이보험... 비갱신형으로 깔끔하게 리모델링한 후기",
        "hashtags": ["#어린이보험", "#태아보험", "#어른이보험", "#보험리모델링", "#2030보험", "#보험리밸런스", "#shorts"],
        "pinned_comment": "📌 내 어린이보험 갱신형 구멍 무료 확인 👉 네이버에 [보험 리밸런스] 검색!"
    },
    7: {
        "title": "임플란트 하려고 치아보험 매달 4만원씩 내면 무조건 손해인 이유 #shorts",
        "hook_summary": "치아보험은 몇 년 붓는 게 아니라 감액 기간 계산해서 치과 가기 딱 3달 전에 가입해야 돈 법니다!",
        "hashtags": ["#치아보험", "#임플란트", "#치과치료", "#크라운", "#치아보험비교", "#보험리밸런스", "#shorts"],
        "pinned_comment": "📌 임플란트 치료 전 치아보험 손익 계산기 👉 네이버에 [보험 리밸런스] 검색!"
    },
    8: {
        "title": "수술할 때마다 매번 50만원씩 나오는 알짜 수술비 특약 챙기는 법 #shorts",
        "hook_summary": "1번 받고 끝나는 옛날 보험 말고, 간단한 대장 용종 떼거나 로봇수술 받아도 매회 반복 지급되는 1~5종 수술비 꿀팁",
        "hashtags": ["#수술비보험", "#종수술비", "#질병수술비", "#대장용종", "#로봇수술", "#보험리밸런스", "#shorts"],
        "pinned_comment": "📌 내 증권에 매회 나오는 종수술비 있나 확인하기 👉 네이버에 [보험 리밸런스] 검색!"
    }
}


class InsuranceSNSGuideGenerator:
    """🛡️ 보험 리밸런스 SNS 포스팅 가이드 자동 생성기"""

    DISCLAIMER_TEXT = "※ 본 영상은 특정 금융상품의 가입 권유나 판매 대리가 아니며, 약관에 대한 이해를 돕기 위한 일반적인 소비자 정보 제공 목적입니다."

    @classmethod
    def generate_guide_text(cls, topic_id: int = 1, speech_hook: Optional[str] = None) -> str:
        preset_key = ((topic_id - 1) % len(INSURANCE_SNS_TEMPLATES)) + 1
        tpl = INSURANCE_SNS_TEMPLATES.get(preset_key, INSURANCE_SNS_TEMPLATES[1])

        title = tpl["title"]
        hook_sum = speech_hook or tpl["hook_summary"]

        # 🌟 실시간 바이럴 해시태그 융합 (InsuranceKeywordMatrix 실시간 검색 트렌드 + 네이버/구글 실시간 키워드)
        try:
            from brands.insurance.insurance_keyword_matrix import InsuranceKeywordMatrix
            matrix = InsuranceKeywordMatrix()
            live_tag_list = matrix.get_live_hashtags(topic_id=topic_id, base_tags=tpl["hashtags"], count=10)
            tags_str = " ".join(live_tag_list)
        except Exception:
            tags_str = " ".join(tpl["hashtags"])

        pinned = tpl["pinned_comment"]

        return f"""========================================================================================
🛡️ [보험 리밸런스] 5대 숏폼 플랫폼 업로드 완벽 가이드 (주제 #{topic_id:02d})
========================================================================================
※ 브랜드 원칙 준수:
  - 공식 네이버 검색어: [보험 리밸런스] (띄어쓰기 필수!)
  - 공식 랜딩 URL: https://insure-rebalance.vercel.app/
  - 특정 보험사 영업 0% / 객관적 5대 보장 AI 분석
  - 금융당국 심의 100% 프리패스 클린 디스클레이머 탑재

----------------------------------------------------------------------------------------
[1. 추천 영상 제목 (Title)]
{title}

----------------------------------------------------------------------------------------
[2. 영상 설명란 (Description)]
{hook_sum}

엄마 친구, 친척 말만 믿고 매달 내던 보험료...
알고 보면 보장 공백이나 불필요한 과다 지출이 수두룩할 수 있습니다.

내 증권에 구멍이 있나 궁금하신 분들은
네이버 검색창에 👉 "보험 리밸런스" 검색해서 무료로 객관적 진단 받아보세요!

{tags_str}

----------------------------------------------------------------------------------------
[3. 🛡️ 금융당국 심의 면책 고지 (클린 디스클레이머 필수 삽입)]
{cls.DISCLAIMER_TEXT}

----------------------------------------------------------------------------------------
[4. 필수 고정 댓글 (Pinned Comment)]
{pinned}

========================================================================================
"""

    @classmethod
    def save_guide_file(cls, output_folder: Path, topic_id: int = 1, speech_hook: Optional[str] = None) -> Path:
        guide_text = cls.generate_guide_text(topic_id=topic_id, speech_hook=speech_hook)
        guide_path = output_folder / f"SNS_포스팅_가이드_주제{topic_id:02d}.txt"
        guide_path.write_text(guide_text, encoding="utf-8")
        return guide_path
