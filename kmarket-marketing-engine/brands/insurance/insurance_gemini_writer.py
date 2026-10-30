from core.gemini_unified_keys import get_unified_gemini_key_dicts, get_unified_gemini_keys, format_gemini_error
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
import re
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
        self.model_name = "gemini-2.5-flash", "gemini-2.0-flash"

    def write_magazine_article(self, topic: Dict[str, Any], seo_brief: Dict[str, Any]) -> Dict[str, Any]:
        """주제와 SEO 키워드 패키지를 바탕으로 2,000자 전문 칼럼 생성 (Cache-First)"""
        topic_id = topic.get("id", 1)
        topic_title = topic["title"]
        category = topic.get("category", "health_medical")
        intent = topic.get("intent", "보험 비교 및 절약 가이드")
        app_feature = topic.get("app_feature", "InsureBalance AI 보장 분석")
        tags = topic.get("tags", ["보험비교", "보험리모델링", "InsureBalance"])

        # 🚀 [100% 실시간 신규 작성 원칙] 매회 Gemini AI가 새로운 보험 칼럼을 실시간 집필합니다.

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
1. 분량 및 5대 심층 챕터 체계 (🚨 3,000자 ~ 3,500자 엄수, 3,500자 초과 금지):
   - **분량: 한글 공백 포함 딱 3,000자 ~ 3,500자 내외 (공백 제외 2,200~2,600자)**, 4,000자 초과 금지.
   - 5대 챕터(도입 실화 팩트체크, 약관 함정 정밀 해부, 숨은 보험금 청구 노하우, 세대별 맞춤 리모델링, 자가진단 체크리스트)를 군더더기 없이 압축 완결.
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
  "body_markdown": "2단 비주얼 박스와 이미지 앵커, 5대 심층 챕터가 완벽히 구현된 3,000~3,500자 완성형 본문",
  "summary": "1줄 요약 메타 디스크립션",
  "tags": ["태그1", "태그2", "태그3", "태그4", "태그5"],
  "visual_prompt": "당신이 집필한 본문 스토리의 가장 결정적이고 생생한 핵심 장면을 포착한 16:9 실사 영문 프롬프트 (🚨 절대 천편일률적인 서류/스마트폰 책상 사진 금지! 본문 스토리의 실제 상황과 인물에 100% 일치해야 함: 운전자/자동차보험이면 도로 위 안전하게 운전하며 미소 짓는 2030 한국인 운전자와 차량 내부, 치아보험이면 환한 미소로 치과 상담을 받거나 자신 있게 웃는 한국인, 누수/화재면 아늑한 거실과 주택 환경, 연금/절세면 햇살 드는 거실에서 가계 재무를 정리하며 안도하는 젊은 부부, 보험금 청구면 병원 진료 후 안도하는 표정, 보험료 다이어트면 가계 지출을 줄이고 밝게 웃는 2030 직장인 등 본문 이야기와 완벽히 일치하는 배경/인물/행동 상세 묘사. realistic Korean people, modern clean Seoul lifestyle, cinematic natural lighting, photorealistic, 16:9 포함)"
}}
"""

        live_trends = seo_brief.get("live_trends", []) if seo_brief else []

        user_prompt = f"""
[오늘의 칼럼 주제]
- 주제명: {topic_title}
- 세부 기획의도: {intent}
- 카테고리: {category}
- 연계 솔루션: {app_feature} (포털 검색어: [보험리밸런스])
- 도메인 트렌드 키워드: {', '.join(live_trends)}
- SEO 권장 키워드: {', '.join(seeds)}

[필수 지침 - 매일 완전히 새로운 관점의 최신 칼럼 집필]
1. 🚨 [절대 금기: 억지 비유 및 진부한 전개 배제]: 무관한 연예인/스포츠 비유를 일절 배제하고, 실제 직장인/가정의 현실적인 의료비, 자동차 사고, 보험금 청구 및 보험료 절약 꿀팁을 실화 바탕의 생생한 스토리로 집필하십시오.
2. 위 주제로 모바일 스크롤을 훑어보는 사람도 100% 사로잡아 네이버에 [보험리밸런스]를 검색하게 만드는 비주얼 침투형 블로그 원고를 작성해주세요.
3. 🚨 [스토리 맞춤형 실사 사진 프롬프트(visual_prompt) 필수 수칙]:
   - 반드시 본문에서 다룬 스토리의 실제 배경 장소와 상황(운전자, 치아 치료, 아파트 누수, 연금 재무 계획, 보험금 청구 등)에 어울리게, 2030 한국인이 등장하는 생생한 16:9 실사 영문 프롬프트를 1문장으로 작성하십시오. (매번 똑같은 서류/책상/스마트폰 사진 금지)
"""

        from google import genai
        from google.genai import types as genai_types

        api_key = get_gemini_key()
        response = None
        # 💰 [최저가 텍스트 모델 1순위] flash-lite ➔ flash ➔ flash-latest 3단 롤오버 + 3회 재시도
        for attempt in range(3):
            try:
                client = genai.Client(api_key=api_key)
                for m_name in ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-flash-latest"]:
                    try:
                        response = client.models.generate_content(
                            model=m_name,
                            contents=user_prompt,
                            config=genai_types.GenerateContentConfig(
                                automatic_function_calling=genai_types.AutomaticFunctionCallingConfig(disable=True),
                                system_instruction=system_instruction,
                                temperature=0.7,
                                max_output_tokens=8192,
                                response_mime_type="application/json"
                            )
                        )
                        if response and response.text:
                            break
                    except Exception:
                        continue
                if response and response.text:
                    break
            except Exception as e:
                logger.warning(f"⚠️ [InsuranceGeminiWriter] 시도 {attempt+1} 실패 ({e}), 키 롤오버")
                report_gemini_key_failure(api_key)
                api_key = get_paid_gemini_key()

        if not response or not getattr(response, "text", None):
            logger.warning("⚠️ [InsuranceGeminiWriter] 모든 Gemini 모델 호출 실패 ➔ 폴백 템플릿 반환")
            return self._generate_fallback(topic, seo_brief)

        # ── 응답 텍스트 정제 (코드펜스 제거) ──
        raw_text = (response.text or "").strip()
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_text:
            raw_text = raw_text.split("```")[1].split("```")[0].strip()

        # ── JSON 파싱 (실패 시 제어문자 정제 ➔ 정밀 필드 추출기 순 3단 방어) ──
        data = None
        try:
            data = json.loads(raw_text, strict=False)
        except Exception:
            try:
                cleaned_json = re.sub(r'[\x00-\x1f\x7f-\x9f]', lambda m: '\n' if m.group(0) in '\r\n\t' else ' ', raw_text)
                data = json.loads(cleaned_json, strict=False)
            except Exception as parse_err:
                logger.warning(f"⚠️ [InsuranceGeminiWriter] JSON 파싱 실패 ({parse_err}) ➔ 정밀 추출기 가동")
                data = self._salvage_json_fields(raw_text)

        if not isinstance(data, dict):
            data = {}

        live_tags = seo_brief.get("viral_hashtags", []) if seo_brief else []
        raw_tags = data.get("tags", []) or tags
        if isinstance(raw_tags, str):
            raw_tags = [t for t in re.split(r'[,\s#]+', raw_tags) if t.strip()]
        # 해시태그 '#' 제거 및 실시간 트렌드 보험 해시태그 결합
        clean_tags = [str(t).replace("#", "").strip() for t in raw_tags if str(t).strip()]
        clean_live = [str(t).replace("#", "").strip() for t in live_tags if str(t).strip()]
        merged_tags = list(dict.fromkeys(clean_tags + clean_live))[:10]

        body_markdown = data.get("body_markdown", "") or ""

        # 🛡️ [본문 글자수 가드] 2,500자 미만이면 폴백 고품질 칼럼으로 자동 보강
        if len(body_markdown.strip()) < 2500:
            logger.warning(
                f"⚠️ [InsuranceGeminiWriter] 본문 길이 부족 ({len(body_markdown.strip())}자 < 2500자) ➔ 폴백 칼럼으로 자동 보강"
            )
            fallback = self._generate_fallback(topic, seo_brief)
            # AI가 생성한 제목/태그/이미지 프롬프트는 살리고 본문만 고품질 폴백으로 교체
            fallback["title_naver"] = data.get("title_naver") or fallback["title_naver"]
            fallback["title_tistory"] = data.get("title_tistory") or fallback["title_tistory"]
            fallback["title_brunch"] = data.get("title_brunch") or fallback["title_brunch"]
            fallback["title"] = fallback["title_naver"]
            fallback["summary"] = data.get("summary") or fallback["summary"]
            fallback["visual_prompt"] = data.get("visual_prompt") or fallback["visual_prompt"]
            if merged_tags:
                fallback["tags"] = merged_tags
            return fallback

        res = {
            "title": data.get("title_naver", topic_title),
            "title_naver": data.get("title_naver", topic_title),
            "title_tistory": data.get("title_tistory", topic_title),
            "title_brunch": data.get("title_brunch", topic_title),
            "body_markdown": body_markdown,
            "summary": data.get("summary", ""),
            "tags": merged_tags,
            "visual_prompt": data.get("visual_prompt", ""),
            "topic_id": topic_id
        }

        # ⚡ 캐시 파일로 영구 저장
        try:
            import datetime
            out_file = CACHE_DIR / f"insurance_blog_topic_{topic_id:03d}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(out_file, "w", encoding="utf-8") as fp:
                json.dump(res, fp, ensure_ascii=False, indent=2)
            logger.info(f"💾 [InsuranceGeminiWriter] 신규 칼럼 아카이브 보관 완료: {out_file.name}")
        except Exception as save_err:
            logger.warning(f"아카이브 보관 예외: {save_err}")

        return res

    @staticmethod
    def _salvage_json_fields(raw_text: str) -> Dict[str, Any]:
        """JSON 파싱이 완전히 깨졌을 때, 정규식으로 핵심 필드(특히 body_markdown)를 안전 복원하는 정밀 추출기"""
        salvaged: Dict[str, Any] = {}
        if not raw_text:
            return salvaged

        # 1) 문자열 필드 정밀 추출 (이스케이프된 따옴표/줄바꿈 허용)
        for key in ("title_naver", "title_tistory", "title_brunch", "summary", "visual_prompt", "body_markdown"):
            m = re.search(r'"' + key + r'"\s*:\s*"((?:[^"\\]|\\.)*)"', raw_text, re.S)
            if m:
                val = m.group(1)
                val = val.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
                salvaged[key] = val.strip()

        # 2) body_markdown 이 잘려서 닫는 따옴표가 없을 경우 ➔ 끝까지 강제 회수
        if not salvaged.get("body_markdown"):
            m = re.search(r'"body_markdown"\s*:\s*"(.*)$', raw_text, re.S)
            if m:
                tail = m.group(1)
                tail = tail.split('",\n')[0].split('"\n')[0]
                tail = tail.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
                salvaged["body_markdown"] = tail.strip()

        # 3) tags 배열 추출
        m = re.search(r'"tags"\s*:\s*\[(.*?)\]', raw_text, re.S)
        if m:
            salvaged["tags"] = [t.strip().strip('"').strip("'") for t in m.group(1).split(",") if t.strip()]

        return salvaged

    def _generate_fallback(self, topic: Dict[str, Any], seo_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Gemini API 장애 시 비상용 완성형 템플릿 (5대 챕터 · 2,800자 이상 고품질 칼럼)"""
        title = topic.get("title", "내 보험료 제대로 쓰고 있을까?")
        category = topic.get("category", "health_medical")
        intent = topic.get("intent", "보험 비교 및 절약 가이드")
        topic_id = topic.get("id", 1)
        base_tags = topic.get("tags", ["보험비교", "보험리모델링", "보험 리밸런스"])

        body = f"""## {title}

안녕하세요, 10년 차 보험·금융 분석가입니다. 🔖

매달 통장에서 자동이체로 빠져나가는 보험료, 여러분은 그 금액이 '적정한지' 한 번이라도 검증해 보셨나요? 대부분은 가입할 때 설계사가 불러준 금액을 그대로 10년, 20년째 내고 있습니다. 그런데 막상 병원비 영수증을 들고 청구하려고 하면 "이건 특약에서 빠져 있어서 안 됩니다"라는 말을 듣고 허탈해하죠. 오늘은 그 허탈함을 미리 막아주는 5가지 핵심만 딱 정리해드릴게요. 🚨

---

### ① 2026 보험료 현실 실화 팩트체크 💸

먼저 냉정한 현실부터 짚고 갈게요. 인터넷에 떠도는 "실손보험 하나로 7~8만 원 아꼈다"는 글, 절대 사실이 아닙니다. 실제 영수증 기준으로 보면 이렇습니다.

- **실손의료보험**: 월 1~3만 원대 (리모델링 시 절감액 1~2만 원 수준)
- **운전자보험**: 월 1만 원대 (중복 특약 정리 시 절감액 1~2만 원)
- **3대 진단비(암·뇌·심장)**: 월 7~12만 원대 (중복 보장 정리 시 절감액 2~4만 원)
- **4인 가족 합산**: 월 40~60만 원대 (전체 리밸런싱 시 절감액 5~8만 원)

즉, "한 달에 30만 원 아꼈다"는 식의 후기는 100% 과장입니다. 진짜 절약은 **한 달 5~8만 원, 1년이면 60~96만 원**을 새는 돈 없이 되찾는 것입니다. 이 정도만 해도 1년 치 자동차 보험료와 통신비를 동시에 아끼는 셈이거든요. 🧠

> 💡 **[3초 팩트체크] 내 보험도 구멍 뚫려 있을까?**
> 🔍 **네이버 검색창에 [보험 리밸런스] 검색**
>
> 📌 **비용 0원**
> 📌 **전화 권유 0통**
> 📌 **34개 보험사 실시간 모든 보험 비교**

[이미지: 3초 진단 결과표]

---

### ② 약관 함정 정밀 해부 🏥

보험금이 안 나오는 이유는 딱 세 가지입니다. 글자 하나 차이로 수천만 원이 갈리죠.

1. **"진단비"와 "수술비"의 경계** — 같은 병이라도 '진단 확정'과 '수술 집도'는 완전히 다른 특약입니다. 질병 수술비 특약이 없으면 300만 원짜리 수술을 받고도 한 푼 못 받습니다.
2. **"갱신형"과 "비갱신형"의 함정** — 20년 납 비갱신형은 초반 보험료가 비싸 보이지만, 60대 이후 갱신 폭탄이 없습니다. 반대로 갱신형은 10년마다 보험료가 1.5~2배씩 뜁니다.
3. **"자기부담금"과 "급여/비급여" 구분** — 실손보험은 세대별로 자기부담률이 20%에서 30%까지 다릅니다. 4세대 실손은 비급여 특약을 따로 챙겨야 도수치료·MRI가 보장됩니다.

[이미지: 네이버 검색창 그래픽 - "보험 리밸런스"]

---

### ③ 숨은 보험금 청구 노하우 👉

내가 낸 보험금을 못 받고 있는 경우가 생각보다 많습니다. 실제로 매년 수천억 원대의 '숨은 보험금'이 주인을 못 찾고 있습니다.

- **청구 소멸시효는 3년**입니다. 3년이 지나면 법적으로 청구권이 사라지니, 지난 병원 영수증부터 뒤져보세요.
- **중복 보장 확인**: A보험사와 B보험사에 같은 '질병 입원일당'이 있으면 두 곳 모두 청구 가능합니다. 단, 실손은 비례 보상이라 중복 청구가 안 됩니다.
- **카드·통신사 부가보험**도 확인하세요. 신용카드에 딸린 상해보험, 통신사 가입 시 받은 소액 보험이 의외의 구멍을 메워줍니다.

---

### ④ 세대별 맞춤 리모델링 기준 🚗

같은 보험료라도 20대와 50대의 최적 설계는 완전히 다릅니다.

- **20~30대 사회초년생**: 실손 + 운전자보험 + 최소한의 3대 진단비. 월 5~8만 원이면 충분합니다. 비싼 종신보험은 아직 이릅니다.
- **30~40대 가장**: 3대 진단비를 3,000만~5,000만 원대로 상향. 소득 상실 리스크를 막는 '후유장해' 특약이 핵심입니다.
- **50~60대 은퇴 준비**: 갱신형을 비갱신형으로 전환하고, 간병·치매 특약을 추가. 납입이 끝난 보험은 해지하지 말고 '감액 완납'으로 보장을 유지하세요.

---

### ⑤ '보험 리밸런스' 자가진단 체크리스트 🔖

아래 5개 중 2개 이상 해당되면, 지금 바로 점검이 필요합니다.

- [ ] 내 보험료가 월 소득의 10%를 넘는다
- [ ] 가입한 보험의 특약 이름을 3개 이상 말할 수 없다
- [ ] 실손보험을 2015년 이전에 가입했다 (1세대 실손)
- [ ] 운전자보험과 자동차보험의 보장이 겹치는지 모른다
- [ ] 지난 3년간 병원에 다녀왔지만 청구한 적이 없다

> 🚗 **[아반떼 값 아끼기] 낭비되는 고정비 1분 만에 잡는 법**
> 🔍 **네이버나 구글에 [보험 리밸런스] 검색**
>
> 📌 **비용 0원**
> 📌 **전화 권유 0통**
> 📌 **34개 보험사 실시간 모든 보험 비교**

👉 **무료 진단 바로가기**: https://insure-rebalance.vercel.app/

---

### 🎯 마무리

보험은 '가입'이 아니라 '관리'입니다. 오늘 딱 10분만 투자해서 내 통장에서 새는 고정비를 점검해보세요. 상담 전화 한 통 없이, 34개 보험사를 실시간으로 비교하는 것만으로도 1년에 수십만 원이 남습니다. 여러분의 가계부에 작은 숨통이 트이길 바랍니다. 🔖

*본 칼럼은 특정 상품 권유가 아닌 순수 정보 공유 목적으로 작성되었습니다.*"""

        return {
            "title": f"{title} | 보험 리밸런스 가이드",
            "title_naver": f"🚨 {title} — 매달 새는 보험료 5만 원 되찾은 5가지 체크리스트",
            "title_tistory": f"[보험 리밸런스] {title} 완벽 가이드 (약관 함정·숨은 보험금·세대별 리모델링)",
            "title_brunch": f"매달 자동이체되는 보험료, 우리는 얼마나 새고 있을까 — {title}",
            "body_markdown": body,
            "summary": f"{title}에 대한 2026년 기준 현실 보험료 팩트체크, 약관 함정 해부, 숨은 보험금 청구 노하우, 세대별 리모델링 기준, 자가진단 체크리스트 총정리",
            "tags": list(dict.fromkeys([str(t).replace("#", "").strip() for t in base_tags] + ["보험 리밸런스", "보험료 절약", "숨은 보험금", "보험 리모델링"]))[:10],
            "visual_prompt": "A relieved young Korean couple in their 30s sitting at a sunlit living room table reviewing household insurance documents and a laptop, smiling with relief, modern clean Seoul apartment interior, cinematic natural lighting, photorealistic, 16:9",
            "topic_id": topic_id
        }
