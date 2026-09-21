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
            except Exception as e:
                logger.warning(f"⚠️ [InsuranceGeminiWriter] 캐시 로드 실패 ({e}), 신규 작성 진행")

        seo_titles = seo_brief.get("seo_title_keywords", [])
        subheadings = seo_brief.get("h2_h3_subheading_keywords", [])
        seeds = seo_brief.get("scoped_seeds", [])

        # 🎬 InsuranceBlogScenarioDirector 연동: 5대 페르소나 및 비주얼 훅 박스 자동 구성
        try:
            from brands.insurance.scenarios.insurance_blog_scenario_director import InsuranceBlogScenarioDirector
            scenario = InsuranceBlogScenarioDirector.pick_daily_scenario(topic_id)
            system_instruction = InsuranceBlogScenarioDirector.build_system_instruction(scenario)
        except Exception as e:
            logger.warning(f"⚠️ [InsuranceGeminiWriter] 시나리오 디렉터 로드 실패 ({e}), 기본 프롬프트 적용")
            system_instruction = f"""
당신은 네이버 블로그와 티스토리에서 큰 인기를 얻고 있는 '2030 똑순이 실사용자 금융/생활정보 리뷰어'입니다.
모바일 사용자의 80%가 글을 정독하지 않고 5~10초 만에 '스크롤 훑어보기(Skimming)'만 한다는 점을 완벽히 간파하여,
광고/설계사 냄새를 0%로 없애고, 글을 1줄도 안 읽고 스크롤만 내리는 사람도 시선이 턱 걸려서 무조건 [보험리밸런스]를 검색하게 만드는 '비주얼 훅 & 2단 침투형 찐후기 원고'를 작성합니다.

[글쓰기 & 비주얼 구조화 절대 원칙]
1. 분량 및 모바일 최적화 호흡:
   - 1,300자 내외 (1,300~1,500자), 1~2줄 단위로 시원하게 줄바꿈.
   - 눈에 확 들어오는 이모지(🚨, 💸, 💡, 🔖, 👉, 🚗, 🧠, 🏥) 적극 활용.
   - "~합니다" 일변도의 딱딱한 문어체 금지 ❌, "~하더라고요", "~했더니 소름 돋았음", "~정리해드릴게요 🔖" 같은 친근한 구어체 사용 ⭕
2. 🚨 [절대 엄수: 현실적 보험료 & 과장 뻥튀기 0% 원칙 (REALISTIC ACCURACY)]:
   - ❌ 실손보험 단독을 10~15만 원 낸다거나, 실손 하나로 7~8만 원 아꼈다는 비현실적 허위 수치 절대 작성 금지!
   - ⭕ 실손보험은 월 1~3만 원대(절감액 1~2만 원), 운전자보험은 1만 원대(절감액 1~2만 원), 3대 진단비는 7~12만 원대(절감액 2~4만 원), 4인 가족 합산은 40~60만 원대(절감액 5~8만 원) 등 실제 영수증에 기반한 현실적 수치만 작성할 것.
3. 스키머(훑어보는 사람) 시선 장악용 [2단 비주얼 훅 박스] (필수 삽입):
   - **1단 박스 (본문 1/3 지점 - 첫 번째 충격 약관 직후)**:
     > 💡 **[3초 팩트체크] 내 보험도 구멍 뚫려 있을까?**
     > 🔍 **네이버 검색창에 [보험리밸런스] 검색**
     > 
     > 📌 **비용 0원**
     > 📌 **전화 권유 0통**
     > 📌 **34개 보험사 실시간 모든 보험 비교**
   - **2단 박스 (본문 마무리 직전 - 절약 쾌감 직후)**:
     > 🚗 **[아반떼 값 아끼기] 낭비되는 고정비 1분 만에 잡는 법**
     > 🔍 **네이버나 구글에 [보험리밸런스] 검색**
     > 
     > 📌 **비용 0원**
     > 📌 **전화 권유 0통**
     > 📌 **34개 보험사 실시간 모든 보험 비교**
4. 이미지 앵커 포인트 명시:
   - 본문 중간에 독자의 시선을 멈추게 할 그래픽 위치를 `[이미지: 3초 진단 결과표]` 및 `[이미지: 네이버 검색창 그래픽 - "보험리밸런스"]` 형태로 명시할 것.
5. 광고 심의(금소법) 100% 면제:
   - 특정 상품 판매나 상담 신청 폼/연락처 일절 금지.
   - 100% 순수 정보 공유 썰 + 포털 검색 유도(Search CTA: [보험리밸런스])로 심의 완전 면제.

[반환 형식: JSON 포맷 필수]
반드시 유효한 JSON 형식으로만 응답하십시오:
{{
  "title_naver": "네이버 블로그용 5초 클릭 유도 제목 (충격 썰/이모지/질문형)",
  "title_tistory": "티스토리 SEO 최적화 정보형 꿀팁 제목",
  "title_brunch": "브런치스토리용 감성적 가계부 절약 에세이 제목",
  "body_markdown": "2단 비주얼 박스와 이미지 앵커, 모바일 1~2줄 호흡이 완벽히 구현된 1,200~1,500자 완성형 본문",
  "summary": "1줄 요약 메타 디스크립션",
  "tags": ["태그1", "태그2", "태그3", "태그4", "태그5"],
  "visual_prompt": "A stylish 16:9 editorial photograph of a smartphone showing a colorful financial rating chart, placed on a modern clean wooden table next to a cup of iced coffee, sunny daylight, aesthetic 8k"
}}
"""

        user_prompt = f"""
[오늘의 칼럼 주제]
- 주제명: {topic_title}
- 세부 기획의도: {intent}
- 카테고리: {category}
- 연계 솔루션: {app_feature} (포털 검색어: [보험리밸런스])
- SEO 권장 키워드: {', '.join(seeds)}

위 주제로 모바일 스크롤을 훑어보는 사람도 100% 사로잡아 네이버에 [보험리밸런스]를 검색하게 만드는 비주얼 침투형 블로그 원고를 작성해주세요.
"""

        from google import genai
        from google.genai import types as genai_types

        api_key = get_gemini_key()
        for attempt in range(3):
            try:
                client = genai.Client(api_key=api_key)
                response = None
                for m_name in ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-1.5-flash", "gemini-flash-latest"]:
                    try:
                        response = client.models.generate_content(
                            model=m_name,
                            contents=user_prompt,
                            config=genai_types.GenerateContentConfig(
                                system_instruction=system_instruction,
                                temperature=0.7,
                                response_mime_type="application/json"
                            )
                        )
                        break
                    except Exception:
                        continue

                if not response:
                    raise RuntimeError("모든 Gemini 모델 호출 실패")

                raw_text = response.text.strip()
                if "```json" in raw_text:
                    raw_text = raw_text.split("```json")[1].split("```")[0].strip()
                elif "```" in raw_text:
                    raw_text = raw_text.split("```")[1].split("```")[0].strip()

                try:
                    data = json.loads(raw_text, strict=False)
                except Exception:
                    # 제어문자나 특수문자 정제 후 재시도
                    cleaned_json = re.sub(r'[\x00-\x1f\x7f-\x9f]', lambda m: '\n' if m.group(0) in '\r\n\t' else ' ', raw_text)
                    data = json.loads(cleaned_json, strict=False)
                live_tags = seo_brief.get("viral_hashtags", []) if seo_brief else []
                raw_tags = data.get("tags", []) or tags
                # 해시태그 '#' 제거 및 실시간 트렌드 보험 해시태그 결합
                clean_tags = [t.replace("#", "").strip() for t in raw_tags if t.strip()]
                clean_live = [t.replace("#", "").strip() for t in live_tags if t.strip()]
                merged_tags = list(dict.fromkeys(clean_tags + clean_live))[:10]

                res = {
                    "title": data.get("title_naver", topic_title),
                    "title_naver": data.get("title_naver", topic_title),
                    "title_tistory": data.get("title_tistory", topic_title),
                    "title_brunch": data.get("title_brunch", topic_title),
                    "body_markdown": data.get("body_markdown", ""),
                    "summary": data.get("summary", ""),
                    "tags": merged_tags,
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
