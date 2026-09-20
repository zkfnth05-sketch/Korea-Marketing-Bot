# -*- coding: utf-8 -*-
"""
📈 StockMaster 전용 Gemini 2,000자 칼럼 작성기 (StockGeminiWriter)
==================================================================
- 브랜드: StockMaster AI (주식 AI 분석 & 퀀트 & 뇌동매매 방지)
- 페르소나: "StockMaster 수석 퀀트 & AI 투자 전략가"
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

logger = logging.getLogger("StockGeminiWriter")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
CACHE_DIR = PROJECT_ROOT / "outputs" / "stock" / "blogs"
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


class StockGeminiWriter:
    """StockMaster 주식 AI & 투자 전문 Gemini 원고 생성 엔진 (Cache-First)"""

    def __init__(self):
        self.model_name = "gemini-2.0-flash"

    def write_magazine_article(self, topic: Dict[str, Any], seo_brief: Dict[str, Any]) -> Dict[str, Any]:
        """주제와 SEO 키워드 패키지를 바탕으로 2,000자 전문 투자 칼럼 생성 (Cache-First)"""
        topic_id = topic.get("id", 1)
        topic_title = topic["title"]
        category = topic.get("category", "korea_market")
        intent = topic.get("intent", "주식 투자 및 리스크 관리 전략")
        app_feature = topic.get("app_feature", "StockMaster AI 수급 레이더")
        tags = topic.get("tags", ["주식투자", "주식AI", "StockMaster"])

        # ⚡ 1. Cache-First: 이미 작성된 원고가 있으면 즉시 재사용 (Gemini 호출 0회, 비용 0원)
        cache_file = CACHE_DIR / f"stock_blog_topic_{topic_id:03d}.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as fp:
                    cached_data = json.load(fp)
                if cached_data.get("body_markdown") and len(cached_data.get("body_markdown", "")) > 100:
                    logger.info(f"⚡ [StockGeminiWriter] 로컬 원고 캐시 즉시 재사용: {cache_file.name} (비용 0원)")
                    cached_data["topic_id"] = topic_id
                    return cached_data
            except Exception as e:
                logger.warning(f"⚠️ [StockGeminiWriter] 캐시 로드 실패 ({e}), 신규 작성 진행")

        import google.generativeai as genai

        seo_titles = seo_brief.get("seo_title_keywords", [])
        subheadings = seo_brief.get("h2_h3_subheading_keywords", [])
        seeds = seo_brief.get("scoped_seeds", [])

        system_instruction = f"""
당신은 대한민국 최고의 데이터 기반 퀀트 투자자이자 'StockMaster AI'의 수석 투자 전략가입니다.
시장의 소음과 뇌동매매를 배제하고, 철저히 데이터와 펀더멘털, 수급과 팩터에 기반한 냉철하고 명쾌한 투자 인사이트를 제공합니다.

[글쓰기 원칙]
1. 분량: 한글 공백 포함 2,000자 내외의 완성도 높은 장문 분석 칼럼.
2. 톤앤매너: 전문적, 논리적, 명쾌함, 객관적. 뜬구름 잡는 루머 배제, 팩트와 수치 제시.
3. 구성:
   - 도입부 (Hook): 오늘 시장의 핵심 화두 제시 및 투자자들의 공통된 고민(FOMO, 물림) 포착.
   - H2 소제목 1: {subheadings[0] if len(subheadings) > 0 else '시장 환경 및 기업 펀더멘털 정밀 분석'}
   - H2 소제목 2: {subheadings[1] if len(subheadings) > 1 else '차트와 외국인·기관 수급 데이터 체크포인트'}
   - H2 소제목 3: {subheadings[2] if len(subheadings) > 2 else '리스크 요인과 스마트 포트폴리오 대응 전략'}
   - 결론 및 전환 (CTA): 뇌동매매 없이 AI 데이터로 승률을 높이는 '{app_feature}' 솔루션 추천.
4. 검색어 자연 삽입: {', '.join(seeds)} 키워드를 본문에 자연스럽게 녹여낼 것.
5. 리스크 경고: 모든 투자의 책임은 본인에게 있으며, 분할 매수와 손절 원칙을 항상 환기할 것.

[반환 형식: JSON 포맷 필수]
반드시 마크다운 코드블록(```json ... ```) 안에 유효한 JSON 형식으로만 응답하십시오:
{{
  "title_naver": "네이버 스마트블록 검색 1위용 클릭 유도 제목 (핵심 키워드 포함)",
  "title_tistory": "티스토리 SEO 최적화 전문 정보형 제목",
  "title_brunch": "브런치스토리 감성적·통찰력 있는 투자 에세이형 제목",
  "body_markdown": "H2, H3 소제목과 볼드체, 인용구를 적절히 활용한 2,000자 내외의 완성형 마크다운 본문",
  "summary": "1줄 요약 (메타 디스크립션용)",
  "tags": ["태그1", "태그2", "태그3", "태그4", "태그5"],
  "visual_prompt": "A modern sleek financial trading room in English, high-tech multi-monitor trading desk showing stock charts and candlestick graphs, city skyline at dusk visible through large window, professional fintech atmosphere, cinematic 8k editorial look, 16:9 aspect ratio"
}}
"""

        user_prompt = f"""
[오늘의 칼럼 주제]
- 주제명: {topic_title}
- 세부 기획의도: {intent}
- 카테고리: {category}
- 연계 StockMaster 기능: {app_feature}
- SEO 권장 키워드: {', '.join(seeds)}

위 주제로 투자자들에게 실질적인 도움이 되는 2,000자 투자 칼럼을 작성해주세요.
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
                    logger.info(f"💾 [StockGeminiWriter] 신규 칼럼 캐시 저장 완료: {cache_file.name}")
                except Exception as save_err:
                    logger.warning(f"캐시 저장 실패: {save_err}")

                return res
            except Exception as e:
                logger.warning(f"⚠️ [StockGeminiWriter] 시도 {attempt+1} 실패 ({e}), 키 롤오버 시도")
                report_gemini_key_failure(api_key)
                api_key = get_paid_gemini_key()

        return self._generate_fallback(topic, seo_brief)

    def _generate_fallback(self, topic: Dict[str, Any], seo_brief: Dict[str, Any]) -> Dict[str, Any]:
        """비상용 완성형 템플릿"""
        title = topic["title"]
        return {
            "title": f"[투자 분석] {title}",
            "title_naver": f"{title} 주가 전망 및 핵심 투자 포인트",
            "title_tistory": f"[StockMaster] {title} 실전 매매 전략",
            "title_brunch": f"시장의 소음을 넘어선 투자, {title}",
            "body_markdown": f"""## {title}\n\n시장이 급변할 때마다 개인 투자자들은 불안감에 휩싸입니다. 하지만 주가는 결국 기업의 이익과 펀더멘털로 회귀합니다.\n\n### 1. 시장 환경과 펀더멘털 분석\n거시경제 지표와 업황 사이클을 종합적으로 고려하여 기업의 내재가치를 평가해야 합니다. 일시적인 테마에 휩쓸리지 않고 실적의 지속 가능성을 확인하는 것이 급선무입니다.\n\n### 2. 수급과 차트 시그널\n외국인과 기관의 연속 순매수 여부, 그리고 거래량이 실린 지지선 형성을 확인해야 합니다. 하락 추세에서의 섣부른 물타기는 금물입니다.\n\n### 3. StockMaster AI로 완성하는 스마트 투자\n감정을 배제하고 데이터로 최적의 매매 타점을 찾아주는 StockMaster AI 레이더를 지금 경험해보세요.""",
            "summary": f"{title}에 대한 데이터 기반 투자 분석 및 리스크 관리 전략",
            "tags": topic.get("tags", ["주식투자", "주식AI", "StockMaster"]),
            "visual_prompt": "A modern trading desk with candlestick charts on multiple screens, professional financial atmosphere",
            "topic_id": topic["id"]
        }
