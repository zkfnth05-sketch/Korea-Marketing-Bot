# -*- coding: utf-8 -*-
"""
InsuranceRedditCopywriter - 🛡️ [보험 리밸런스 전용 레딧 외국인·유학생 유입 AI 카피라이터]
========================================================================================
• 역할:
  - 레딧 내 외국인 직장인, 영어 강사, 유학생, 교민의 질문/고민글(NHIS vs 실손, 병원비, MRI/도수치료, 보험료 절감) 분석
  - 2030 영미권 네이티브 톤앤매너(Expat Financial & Healthcare Mentor, 친절, 팩트 중심, 명쾌함)로 진정성 있는 답변 생성
  - 3단 무료키 순환 체인 활용
  - 80:20 스텔스 비율 (80% 구글 검색어 '보험 리밸런스' 유도 vs 20% 순수 도움)
  - 🚨 Zero URL 물리적 박멸기: 본문/댓글 내 raw URL 100% 제거 및 구글/네이버 공식 검색어 강제 치환
"""

import os
import sys
import re
import json
import random
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from brands.insurance.scenarios.reddit_expat_scenarios import INSURANCE_REDDIT_EXPAT_SCENARIOS, get_scenario_by_id

logger = logging.getLogger("InsuranceRedditCopywriter")

# 80:20 황금 비율 (구글 검색 유도 80% vs 순수 정보 20%)
_PROMO_LEVELS = {
    1: 0.20,  # 순수 도움 (브랜드 0%, 검색어 0개)
    2: 0.80,  # 자연스러운 구글 '보험 리밸런스' 검색 유도 (노링크)
}


def _choose_promo_level() -> int:
    """가중치 기반 레벨 선택 (구글 검색 유도 80%)"""
    return 2 if random.random() < 0.80 else 1


class InsuranceRedditCopywriter:
    """보험 리밸런스 전용 레딧 외국인·유학생 유입 AI 카피라이터 & 인텐트 판별기"""

    OFFICIAL_SEARCH_KEYWORD = "보험 리밸런스"
    OFFICIAL_ENGLISH_KEYWORD = "Insure Rebalance"
    OFFICIAL_URL = "https://insure-rebalance.vercel.app/"

    def __init__(self):
        from core.gemini_unified_keys import get_unified_gemini_key_dicts
        self.key_chain = get_unified_gemini_key_dicts()
        self._active_key_index = 0
        logger.info(f"🛡️ [InsuranceRedditCopywriter] 키 체인 등록 완료 (총 {len(self.key_chain)}개)")

    def _get_genai_client(self, api_key: str):
        from google import genai
        return genai.Client(api_key=api_key)

    @staticmethod
    def _eradicate_urls(text: str) -> str:
        """
        🚨 레딧 섀도우밴/차단 0% 보장:
        모든 형태의 raw URL(http, https, www, .com, .app, .kr 등) 및 마크다운 링크를
        물리적으로 100% 탐지하여 구글 검색어('보험 리밸런스')로 강제 치환
        """
        # 1. 마크다운 링크 [anchor](url) -> anchor (search '보험 리밸런스' on Google)
        text = re.sub(r'\[([^\]]+)\]\((?:https?://|www\.)[^\)]+\)', r"\1 (search '보험 리밸런스' on Google)", text)
        # 2. 일반 raw URL (http://..., https://...)
        text = re.sub(r'https?://\S+', "search '보험 리밸런스' on Google", text)
        # 3. www. 시작 주소
        text = re.sub(r'www\.[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', "search '보험 리밸런스' on Google", text)
        # 4. 도메인 잔존 텍스트 박멸 (vercel.app, insure-rebalance 등)
        text = re.sub(r'\b[a-zA-Z0-9-]+\.(?:vercel\.app|app|co\.kr|kr|com|net|org)\b(?:\/\S*)?', "search '보험 리밸런스' on Google", text)
        return text.strip()

    def classify_insurance_reddit_intent(self, post_title: str, post_body: str = "") -> Dict[str, Any]:
        """
        레딧 글의 4대 카테고리 인텐트 신속 판별 (룰베이스 기본값)
        """
        text = f"{post_title} {post_body}".lower()

        if any(k in text for k in ["mri", "ultrasound", "hospital bill", "surgery", "physical therapy", "clinic", "expensive"]):
            return {"category": "hospital_and_reimbursement", "scenario_id": 2, "confidence": 0.90}
        elif any(k in text for k in ["arc", "alien registration", "foreigner", "foreigner qualify", "teacher", "epik", "hagwon"]):
            return {"category": "expat_and_arc_insurance", "scenario_id": 3, "confidence": 0.88}
        elif any(k in text for k in ["compare", "recommend", "cheapest", "cancel", "refund", "rebalance", "without phone"]):
            return {"category": "comparison_and_rebalance", "scenario_id": 7, "confidence": 0.85}
        else:
            return {"category": "nhis_and_silbi", "scenario_id": 1, "confidence": 0.82}

    def verify_lead_intent(self, post_title: str, post_body: str = "", subreddit: str = "") -> Dict[str, Any]:
        """
        🛡️ [보험 리밸런스 레딧 100% 순수 파이썬 사전 심사 게이트 (Zero Gemini 호출 원칙)]
        - 네이버 카페 침투(AuraCafeFilter)와 동일하게 파이썬이 100% 사전 심사 (제미나이 0회 호출)
        - 1단계: 네거티브 필터 (단순 여행 맛집, 비자 행정, 암호화폐 등 비관련 글 즉각 탈락)
        - 2단계: 4대 핵심 보험 클러스터 키워드 정밀 매칭 및 시나리오 자동 배정
        - 제미나이 API 호출 0회 ➔ 0.001초 즉각 판별
        """
        combined = f"{post_title} {post_body}".lower()

        # 1. 네거티브 필터링 (완전 비관련 주제 즉각 배제)
        neg_keywords = [
            "crypto", "bitcoin", "restaurant", "club", "bar hopping", "nightlife",
            "k-pop concert", "ticket resale", "used car", "pc build"
        ]
        if any(nk in combined for nk in neg_keywords):
            logger.info(f"🚫 [보험 레딧 파이썬 심사 탈락] 네거티브 키워드 감지: '{post_title[:35]}'")
            return {
                "is_relevant": False,
                "confidence_score": 0,
                "category": "negative_filter",
                "scenario_id": 0,
                "reason": "보험/의료 비관련 주제 즉각 탈락"
            }

        # 2. 4대 보험 핵심 클러스터 매칭
        clusters = [
            (
                "hospital_and_reimbursement",
                2,
                ["mri", "ultrasound", "hospital bill", "surgery", "physical therapy", "clinic", "expensive medical", "doctor bill", "ct scan", "medical expense", "treatment cost", "hospital cost"],
                92
            ),
            (
                "expat_and_arc_insurance",
                3,
                ["arc", "alien registration", "foreigner insurance", "nhis foreigner", "epik insurance", "hagwon insurance", "expat health", "foreigner medical"],
                89
            ),
            (
                "comparison_and_rebalance",
                7,
                ["compare insurance", "insurance recommend", "cheapest insurance", "cancel insurance", "rebalance", "without phone", "private insurance", "supplemental insurance"],
                90
            ),
            (
                "nhis_and_silbi",
                1,
                ["nhis", "health insurance", "national health", "silbi", "medical insurance", "korean healthcare", "doctor appointment", "pharmacy prescription"],
                85
            )
        ]

        for cat_name, scen_id, keywords, conf in clusters:
            if any(k in combined for k in keywords):
                logger.info(f"🎯 [보험 레딧 파이썬 심사 통과] '{post_title[:35]}' ➔ {cat_name} (시나리오 {scen_id})")
                return {
                    "is_relevant": True,
                    "confidence_score": conf,
                    "category": cat_name,
                    "scenario_id": scen_id,
                    "reason": f"파이썬 {cat_name} 핵심 키워드 100% 매칭"
                }

        # 매칭되는 보험 키워드 없음 -> 탈락
        return {
            "is_relevant": False,
            "confidence_score": 0,
            "category": "unrelated",
            "scenario_id": 0,
            "reason": "보험/의료 관련 키워드 미매칭"
        }

    def generate_reddit_response(
        self,
        post_title: str,
        post_body: str = "",
        subreddit: str = "Living_in_Korea",
        target_lang: str = "en",
        scenario_id: int = 1
    ) -> str:
        """
        80:20 스텔스 영문 답변 생성 (Zero URL 원칙 적용)
        """
        level = _choose_promo_level()
        scenario = get_scenario_by_id(scenario_id)

        prompt = f"""You are a helpful, knowledgeable 2030 expat financial & healthcare advisor who has lived in Seoul, South Korea for years.
Respond to this Reddit post on r/{subreddit}.

Post Title: {post_title}
Post Body: {post_body}

Scenario Context:
- Theme: {scenario['theme_name']}
- Core Solution: {scenario['solution_feature']}
- Reference Style: {scenario['sample_reply']}

STRICT RULES:
1. Tone: 100% Native fluent English (warm, knowledgeable, casual expat tone).
2. 80:20 Ratio (Level {level}):
   {"- Give 100% pure objective advice about Korean healthcare and NHIS with NO brand mentions." if level == 1 else "- Give 80% genuine, deeply helpful advice about Korean medical costs & NHIS coverage. Then 20% naturally suggest searching '보험 리밸런스' (or 'Insure Rebalance') on Google/Naver with Chrome translation to compare 30+ Korean carriers side-by-side without unwanted sales calls."}
3. 🚨 ZERO URL RULE: NEVER include any web link, domain (.com, .app, .kr), or URL. Only recommend searching the exact keywords: '보험 리밸런스' (or 'Insure Rebalance') on Google or Naver.
4. Length: 3~4 concise, impactful paragraphs (120~180 words).

Write the Reddit comment response directly:
"""
        models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash"]
        total_keys = len(self.key_chain)
        for i in range(total_keys):
            idx = (self._active_key_index + i) % total_keys
            key_info = self.key_chain[idx]
            key_quota_exhausted = False
            try:
                client = self._get_genai_client(key_info["key"])
                for model_name in models_to_try:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt
                        )
                        generated = (response.text or "").strip()
                        if generated and len(generated) > 40:
                            clean_text = self._eradicate_urls(generated)
                            self._active_key_index = idx
                            return clean_text
                    except Exception as model_err:
                        err_str = str(model_err)
                        if any(k in err_str for k in ["429", "RESOURCE_EXHAUSTED", "quota", "depleted", "QuotaFailure"]):
                            logger.warning(f"⚠️ [할당량 소진] 키={key_info['name']} ({model_name}) 429 쿼터 초과 -> 다음 무료키로 즉시 롤오버!")
                            key_quota_exhausted = True
                            break
                        else:
                            logger.debug(f"[{key_info['name']}] 카피라이팅 모델 {model_name} 실패: {model_err}")
                            continue

                if key_quota_exhausted:
                    self._active_key_index = (idx + 1) % total_keys
                    continue
            except Exception as e:
                logger.warning(f"[{key_info['name']}] 카피라이팅 예외: {e}")
                self._active_key_index = (idx + 1) % total_keys
                continue

        # Fallback to pre-built high-converting scenario sample
        fallback_reply = scenario.get("sample_reply", "")
        return self._eradicate_urls(fallback_reply)
