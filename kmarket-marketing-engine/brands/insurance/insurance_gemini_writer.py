# -*- coding: utf-8 -*-
"""
🛡️ InsureBalance 전용 Gemini 2,000자 칼럼 작성기 (InsuranceGeminiWriter)
========================================================================
- 브랜드: InsureBalance (보험 비교 & 보장 분석 & 리모델링)
- 페르소나: "10년 차 공인 보험전문가 & 금융 분석가"
- 원칙:
  1. Cache-First (로컬 캐시 우선 재사용으로 중복 API 호출 0원 보장)
  2. 3대 플랫폼별 최적화 제목 3종 + 16:9 실사 맞춤 사진 프롬프트 동시 생성
  3. 실패 시 자동 키 롤오버 및 비상용 폴백 템플릿
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("InsuranceGeminiWriter")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
CACHE_DIR = PROJECT_ROOT / "outputs" / "insurance" / "blogs"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

# KeyManager import
try:
    from utils.key_manager import get_gemini_key, report_gemini_key_failure, get_paid_gemini_key
except ImportError:
    def get_gemini_key():
        return os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_FREE_API_KEY_AURA_1") or os.environ.get("GEMINI_FREE_API_KEY_KMARKET") or ""
    def report_gemini_key_failure(k):
        pass
    def get_paid_gemini_key():
        return os.environ.get("GEMINI_PAID_API_KEY_AURA_1") or os.environ.get("GEMINI_API_KEY") or ""


class InsuranceGeminiWriter:
    """InsureBalance 보험 비교 & 리모델링 전문 Gemini 원고 생성 엔진 (Cache-First)"""

    def __init__(self):
        self.model_name = "gemini-2.0-flash"

    def write_magazine_article(self, topic: Dict[str, Any], seo_brief: Dict[str, Any]) -> Dict[str, Any]:
        """주제와 SEO 키워드 패키지를 바탕으로 2,000자 전문 칼럼 생성 (Cache-First)"""
        topic_id = topic.get("id", 1)
        topic_title = topic["title"]
        category = topic.get("category", "health_medical")
        intent = topic.get("intent", "보험 비교 및 절약 가이드")
        app_feature = topic.get("app_feature", "InsureBalance AI 보장 분석")
        tags = topic.get("tags", ["보험비교", "보험리모델링", "InsureBalance"])

        # ⚡ 1. Cache-First: 이미 작성된 원고가 있으면 즉시 재사용 (Gemini 호출 0회, 비용 0원)
        cache_file = CACHE_DIR / f"insurance_blog_topic_{topic_id:03d}.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as fp:
                    cached_data = json.load(fp)
                if cached_data.get("body_markdown") and len(cached_data.get("body_markdown", "")) > 100:
                    logger.info(f"⚡ [InsuranceGeminiWriter] 로컬 원고 캐시 즉시 재사용: {cache_file.name} (비용 0원)")
                    cached_data["topic_id"] = topic_id
                    return cached_data
            except Exception as e:
                logger.warning(f"⚠️ [InsuranceGeminiWriter] 캐시 로드 실패 ({e}), 신규 작성 진행")

        import google.generativeai as genai

        seo_titles = seo_brief.get("seo_title_keywords", [])
        subheadings = seo_brief.get("h2_h3_subheading_keywords", [])
        seeds = seo_brief.get("scoped_seeds", [])

        system_instruction = f"""
당신은 대한민국 최고의 금융/보험 전문 분석가이자 'InsureBalance'의 수석 에디터입니다.
소비자의 편에서 복잡하고 불리한 보험 약관을 낱낱이 파헤치고, 불필요한 지출을 막아주는 신뢰감 있고 명쾌한 칼럼을 작성합니다.

[글쓰기 원칙]
1. 분량: 한글 공백 포함 2,000자 내외의 깊이 있는 전문 장문 칼럼.
2. 톤앤매너: 객관적, 전문적, 신뢰감, 친절함. 소비자 권리를 지켜주는 든든한 조언자 어조.
3. 구성:
   - 도입부 (Hook): 매달 통장에서 빠져나가는 보험료에 대한 문제 제기 및 현실적인 고민 공감.
   - H2 소제목 1: {subheadings[0] if len(subheadings) > 0 else '핵심 약관과 보장 내용 팩트체크'}
   - H2 소제목 2: {subheadings[1] if len(subheadings) > 1 else '소비자가 가장 많이 겪는 손해 및 부지급 사례'}
   - H2 소제목 3: {subheadings[2] if len(subheadings) > 2 else '전문가가 추천하는 맞춤형 가입 및 리모델링 전략'}
   - 결론 및 전환 (CTA): 내 보험의 과부족 상태를 3분 만에 진단할 수 있는 '{app_feature}' 솔루션 추천.
4. 검색어 자연 삽입: {', '.join(seeds)} 키워드를 본문에 문맥상 자연스럽게 녹여낼 것.
5. 절대 주의: 뻔하고 피상적인 내용 금지. 실제 약관 조항, 질병 코드(C코드, I코드 등), 수술 종류, 구체적 비용 시뮬레이션을 제시할 것.

[반환 형식: JSON 포맷 필수]
반드시 마크다운 코드블록(```json ... ```) 안에 유효한 JSON 형식으로만 응답하십시오:
{{
  "title_naver": "네이버 스마트블록 검색 1위용 클릭 유도 제목 (핵심 키워드 포함)",
  "title_tistory": "티스토리 SEO 최적화 전문 정보형 제목",
  "title_brunch": "브런치스토리 감성적·통찰력 있는 칼럼형 제목",
  "body_markdown": "H2, H3 소제목과 볼드체, 인용구를 적절히 활용한 2,000자 내외의 완성형 마크다운 본문",
  "summary": "1줄 요약 (메타 디스크립션용)",
  "tags": ["태그1", "태그2", "태그3", "태그4", "태그5"],
  "visual_prompt": "A professional 16:9 photography prompt in English depicting modern financial planning, insurance documents on a neat wooden desk, a tablet showing graphs, warm natural daylight, highly detailed, realistic 8k editorial look"
}}
"""

        user_prompt = f"""
[오늘의 칼럼 주제]
- 주제명: {topic_title}
- 세부 기획의도: {intent}
- 카테고리: {category}
- 연계 InsureBalance 기능: {app_feature}
- SEO 권장 키워드: {', '.join(seeds)}

위 주제로 소비자가 무릎을 탁 칠 만한 실전 보험 가이드 2,000자 칼럼을 작성해주세요.
"""

        from google import genai
        from google.genai import types as genai_types

        api_key = get_gemini_key()
        for attempt in range(3):
            try:
                client = genai.Client(api_key=api_key)
                for m_name in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]:
                    try:
                        response = client.models.generate_content(
                            model=m_name,
                            contents=user_prompt,
                            config=genai_types.GenerateContentConfig(
                                system_instruction=system_instruction,
                                temperature=0.7,
                                max_output_tokens=4096
                            )
                        )
                        break
                    except Exception:
                        continue

                raw_text = response.text.strip()
                if "```json" in raw_text:
                    raw_text = raw_text.split("```json")[1].split("```")[0].strip()
                elif "```" in raw_text:
                    raw_text = raw_text.split("```")[1].split("```")[0].strip()

                data = json.loads(raw_text)
                res = {
                    "title": data.get("title_naver", topic_title),
                    "title_naver": data.get("title_naver", topic_title),
                    "title_tistory": data.get("title_tistory", topic_title),
                    "title_brunch": data.get("title_brunch", topic_title),
                    "body_markdown": data.get("body_markdown", ""),
                    "summary": data.get("summary", ""),
                    "tags": data.get("tags", tags),
                    "visual_prompt": data.get("visual_prompt", ""),
                    "topic_id": topic_id
                }

                # ⚡ 캐시 파일로 영구 저장
                try:
                    with open(cache_file, "w", encoding="utf-8") as fp:
                        json.dump(res, fp, ensure_ascii=False, indent=2)
                    logger.info(f"💾 [InsuranceGeminiWriter] 신규 칼럼 캐시 저장 완료: {cache_file.name}")
                except Exception as save_err:
                    logger.warning(f"캐시 저장 실패: {save_err}")

                return res
            except Exception as e:
                logger.warning(f"⚠️ [InsuranceGeminiWriter] 시도 {attempt+1} 실패 ({e}), 키 롤오버 시도")
                report_gemini_key_failure(api_key)
                api_key = get_paid_gemini_key()

        # 완전 실패 시 안전한 폴백 템플릿 반환
        return self._generate_fallback(topic, seo_brief)

    def _generate_fallback(self, topic: Dict[str, Any], seo_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Gemini API 장애 시 비상용 완성형 템플릿"""
        title = topic["title"]
        return {
            "title": f"[보험 상식] {title}",
            "title_naver": f"{title} 핵심 정리 및 손해 안 보는 팁",
            "title_tistory": f"[InsureBalance] {title} 완벽 가이드",
            "title_brunch": f"우리가 매달 내는 보험료, {title}",
            "body_markdown": f"""## {title}\n\n매달 지출되는 보험료, 과연 내가 낸 만큼 제대로 보장받고 있을까요?\n\n많은 소비자들이 보험에 가입할 때는 친절한 설명을 듣지만, 막상 병원에 가거나 보험금을 청구할 때는 복잡한 약관과 부지급 조항 때문에 당황하곤 합니다.\n\n### 1. 꼭 알아야 할 핵심 약관\n보험사 약관은 글자 하나 차이로 수천만 원의 보장 여부가 갈립니다. 보장 범위가 가장 넓은 특약을 선택하고, 갱신 주기와 자기부담금 비율을 꼼꼼히 따져보아야 합니다.\n\n### 2. 소비자가 자주 놓치는 보상 포인트\n숨은 보험금과 청구 소멸시효(3년)를 확인하여 지난 영수증도 빠짐없이 챙기는 지혜가 필요합니다.\n\n### 3. InsureBalance로 3분 만에 끝내는 보험 진단\n내 보험의 과보장/부족보장 상태를 InsureBalance AI 분석기를 통해 무료로 점검해보세요.""",
            "summary": f"{title}에 대한 필수 보험 약관과 손해 보지 않는 보상 노하우 정리",
            "tags": topic.get("tags", ["보험비교", "보험리모델링", "InsureBalance"]),
            "visual_prompt": "A modern clean office desk with insurance documents and financial tablet, natural daylight",
            "topic_id": topic["id"]
        }
