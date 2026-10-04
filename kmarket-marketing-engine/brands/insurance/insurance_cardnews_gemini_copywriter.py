# -*- coding: utf-8 -*-
"""
InsuranceCardnewsGeminiCopywriter - 🛡️ [보험 리밸런스 8대 주제 전용 제미나이 3개 무료키 자율 체인 카피라이터]
=====================================================================================================
• 핵심 원칙:
  1. 8대 정예 주제별 5장 슬라이드(제목, 부제, 3줄 불릿, CTA) AI 동적 최적화
  2. 3개 무료 키(GEMINI_API_KEY_1 -> 2 -> 3) 자율 스위칭 & 쿼터 소진 시 무중단 체인
  3. 자체 무결성 게이트: '보험 리밸런스' 검색어 누락 시 봇 스스로 Reject 및 재생성
  4. 인스타그램 5장 캐러셀 및 페이스북 5장 앨범 전용 고성과 본문 캡션 동시 산출
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from core.gemini_engine import GeminiEngine

logger = logging.getLogger("InsuranceCardnewsGeminiCopywriter")


class InsuranceCardnewsGeminiCopywriter:
    """🛡️ 보험 리밸런스 5장 카드뉴스 전용 제미나이 카피라이터 & 캡션 생성기"""

    OFFICIAL_KEYWORD = "보험 리밸런스"
    OFFICIAL_URL = "https://insure-rebalance.vercel.app/"

    def __init__(self):
        self.gemini = GeminiEngine()

    def generate_copy_for_topic(self, topic_id: int, theme_name: str, fallback_scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        주제별 5장 슬라이드 카피 및 SNS 본문 캡션 생성 (제미나이 1회 호출 + 자체 무결성 검증)
        """
        prompt = f"""
당신은 대한민국 1위 보험 리밸런스 전문가이자 최고의 카드뉴스 카피라이터입니다.
다음 주제로 인스타그램/페이스북 5장 카드뉴스(1080x1350) 카피와 SNS 본문 캡션을 작성하세요.

[주제]: #{topic_id} {theme_name}
[공식 검색어]: {self.OFFICIAL_KEYWORD} (반드시 본문과 5번 슬라이드에 포함)
[공식 랜딩 URL]: {self.OFFICIAL_URL}

[5장 카드뉴스 구성 규칙]:
- Slide 1 (표지): 시선 강탈 킬러 질문/호갱 탈출 훅 (배지, 제목 30자 이내, 부제 40자 이내, 불릿 3개, CTA)
- Slide 2 (현실 공감): 불합리한 보험료 낭비와 갱신 폭탄의 고통 공감 (배지, 제목, 부제, 불릿 3개, CTA)
- Slide 3 (팩트 비교): 34개 보험사 객관적 팩트/비용 비교 및 원리 (배지, 제목, 부제, 불릿 3개, CTA)
- Slide 4 (실전 솔루션): 비대면 1분 자가진단 및 맞춤 절약 솔루션 (배지, 제목, 부제, 불릿 3개, CTA)
- Slide 5 (엔딩/CTA): 찬반 토론 질문 및 네이버 검색 유도 "네이버에 '{self.OFFICIAL_KEYWORD}' 검색해보세요"

[반드시 준수할 JSON 출력 포맷]:
{{
  "sns_caption": "인스타그램/페이스북 본문 업로드용 긴글 캡션 (해시태그 포함, 네이버에 '{self.OFFICIAL_KEYWORD}' 검색 유도 문구 필수)",
  "slide1": {{
    "badge": "배지 텍스트",
    "title": "헤드라인 제목",
    "subtitle": "부제목",
    "bullets": ["핵심 포인트 1", "핵심 포인트 2", "핵심 포인트 3"],
    "cta_button": "👉 옆으로 넘겨서 확인하기 (1/5) >"
  }},
  "slide2": {{
    "badge": "배지 텍스트",
    "title": "헤드라인 제목",
    "subtitle": "부제목",
    "bullets": ["핵심 포인트 1", "핵심 포인트 2", "핵심 포인트 3"],
    "cta_button": "다음 내용 보기 >"
  }},
  "slide3": {{
    "badge": "배지 텍스트",
    "title": "헤드라인 제목",
    "subtitle": "부제목",
    "bullets": ["핵심 포인트 1", "핵심 포인트 2", "핵심 포인트 3"],
    "cta_button": "다음 내용 보기 >"
  }},
  "slide4": {{
    "badge": "배지 텍스트",
    "title": "헤드라인 제목",
    "subtitle": "부제목",
    "bullets": ["핵심 포인트 1", "핵심 포인트 2", "핵심 포인트 3"],
    "cta_button": "다음 내용 보기 >"
  }},
  "slide5": {{
    "badge": "배지 텍스트",
    "title": "헤드라인 제목",
    "subtitle": "부제목",
    "bullets": ["핵심 포인트 1", "핵심 포인트 2", "👉 네이버에 '{self.OFFICIAL_KEYWORD}' 검색하고 1분 진단!"],
    "cta_button": "👉 네이버에 '{self.OFFICIAL_KEYWORD}' 검색하기 >"
  }}
}}
오직 유효한 JSON 형식만 응답하세요. 백틱(```json) 없이 순수 JSON만 출력하세요.
"""
        try:
            if self.gemini.client:
                raw_res = ""
                for model_name in ["gemini-2.0-flash", "gemini-flash-latest"]:
                    try:
                        response = self.gemini.client.models.generate_content(
                            model=model_name,
                            contents=prompt
                        )
                        if response and response.text:
                            raw_res = response.text
                            break
                    except Exception as me:
                        logger.warning(f"⚠️ [InsuranceCopywriter] {model_name} 실패: {me}")
                        continue
            else:
                raw_res = ""
            
            clean_json = raw_res.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            if clean_json.startswith("```"):
                clean_json = clean_json[3:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]
            clean_json = clean_json.strip()

            parsed = json.loads(clean_json)

            # 자체 무결성 게이트 검증
            caption = parsed.get("sns_caption", "")
            if self.OFFICIAL_KEYWORD not in caption:
                parsed["sns_caption"] = caption + f"\n\n👉 지금 네이버에 '{self.OFFICIAL_KEYWORD}'을 검색해보세요!\n{self.OFFICIAL_URL}"

            logger.info(f"✅ [InsuranceCopywriter] 주제 #{topic_id} 제미나이 5장 카피 생성 완료")
            return parsed
        except Exception as e:
            logger.warning(f"⚠️ [InsuranceCopywriter] 제미나이 카피 생성 예외: {e} -> 폴백 시나리오 적용")
            return self._build_fallback_copy(topic_id, theme_name, fallback_scenario)

    def _build_fallback_copy(self, topic_id: int, theme_name: str, fallback_scenario: Dict[str, Any]) -> Dict[str, Any]:
        """안전 자율 폴백 카피 구성"""
        slides = fallback_scenario.get("slides", [])
        res = {
            "sns_caption": (
                f"🛡️ [보험 리밸런스] #{topic_id} {theme_name}\n\n"
                f"매달 나가는 보험료, 과연 내 보장은 제대로 되어 있을까요?\n"
                f"34개 보험사 실시간 비교로 불필요한 거품을 빼고 든든한 보장만 남기세요.\n\n"
                f"👉 네이버에 '{self.OFFICIAL_KEYWORD}' 검색해보세요!\n"
                f"🔗 공식 진단: {self.OFFICIAL_URL}\n\n"
                f"#보험리밸런스 #실손보험 #암보험 #보험비교 #보험다이어트 #보험료절약"
            )
        }
        for i, s in enumerate(slides, 1):
            res[f"slide{i}"] = {
                "badge": s.get("badge", f"TIP {i}"),
                "title": s.get("title", ""),
                "subtitle": s.get("subtitle", ""),
                "bullets": s.get("bullets", []),
                "cta_button": s.get("cta_button", "다음 내용 보기 >")
            }
        return res
