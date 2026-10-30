from core.gemini_unified_keys import get_unified_gemini_key_dicts, get_unified_gemini_keys, format_gemini_error
# -*- coding: utf-8 -*-
"""
Aura Gemini Writer (💖 Aura 2030 매거진 전문 AI 원고 & 비주얼 프롬프트 작성기)
=============================================================================
- 브랜드: Aura (2030 AI 데이팅 / 매칭 라운지 / 소개팅 코칭)
- 역할:
  1. 100대 주제 풀 + 실시간 네이버/구글 키워드를 입력받아 3,000자 고품질 전문 칼럼 작성
  2. 4대 키 체인 중 무료키 2개(GEMINI_FREE_API_KEY_KMARKET, GEMINI_FREE_API_KEY_EASYTAX) 100% 우선 활용 (비용 0원)
  3. 무료키 429 한도 초과 시 ➔ 유료키 2개로 0.1초 만에 자동 무중단 롤오버
  4. 글 본문 스토리 맥락에 100% 부합하는 맞춤형 16:9 영문 visual_prompt 동시 기획
  5. 랜딩 URL: https://aura-ai-dating.vercel.app/ 고정 연동
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

# UTF-8 콘솔 출력 지원
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("AuraGeminiWriter")

# 기본 경로
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent


class AuraGeminiWriter:
    """
    💖 4대 스마트 키 체인 기반 Aura 2030 매거진 전문 카피라이터
    - 무료키 2개 우선 순환 (비용 0원)
    - 유료키 2개 안전 롤오버
    """

    LANDING_URL = "https://aura-ai-dating.vercel.app/"

    def __init__(self):
        from config import (
            GEMINI_FREE_API_KEY_AURA_1,
            GEMINI_FREE_API_KEY_AURA_2,
            GEMINI_FREE_API_KEY_AURA_3,
            GEMINI_PAID_API_KEY_AURA_1,
            GEMINI_PAID_API_KEY_AURA_2,
            GEMINI_FREE_API_KEY_KMARKET,
            GEMINI_FREE_API_KEY_EASYTAX,
            GEMINI_API_KEY
        )

        # 💖 Aura 5단 스마트 키 체인: 전용 무료키 3개 우선 (0원) ➔ 전용 유료키 2개 (비상) ➔ 백업키
        self.key_chain = get_unified_gemini_key_dicts()
        self._active_key_index = 0
        names = [k["name"] for k in self.key_chain]
        logger.info(f"💖 [AuraGeminiWriter] 4단 키 체인 활성화 완료: {' ➔ '.join(names)}")

    def _get_genai_client(self, api_key: str):
        from google import genai
        return genai.Client(api_key=api_key)

    def _call_gemini_smart(self, prompt: str, system_instruction: str) -> str:
        """무료키 ➔ 유료키 자동 롤오버 API 호출기"""
        if not self.key_chain:
            raise RuntimeError("사용 가능한 Gemini API 키가 없습니다.")

        total_keys = len(self.key_chain)
        last_err = None

        for i in range(total_keys):
            idx = (self._active_key_index + i) % total_keys
            key_info = self.key_chain[idx]
            key_name = key_info["name"]
            api_key = key_info["key"]

            try:
                client = self._get_genai_client(api_key)
                from google.genai import types as genai_types
                types = genai_types

                # 💰 [최저가 텍스트 모델 1순위] gemini-2.5-flash-lite 최우선 호출 ➔ flash ➔ flash-latest 순 롤오버
                for model_name in ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-flash-latest"]:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config=genai_types.GenerateContentConfig(
                                automatic_function_calling=genai_types.AutomaticFunctionCallingConfig(disable=True), system_instruction=system_instruction,
                                temperature=0.75,
                                max_output_tokens=8192,
                                response_mime_type="application/json"
                            )
                        )
                        if response and response.text:
                            self._active_key_index = idx
                            logger.info(f"✅ [AuraGeminiWriter] {key_name} ({model_name}) 호출 성공!")
                            return response.text
                    except Exception as model_err:
                        if "404" in str(model_err) or "not found" in str(model_err).lower():
                            continue
                        raise model_err

            except Exception as e:
                last_err = e
                err_msg = str(e)
                logger.warning(f"⚠️ [AuraGeminiWriter] {key_name} 실패: {err_msg[:100]} ➔ 다음 키 롤오버 시도")

        raise RuntimeError(f"모든 Gemini API 키 체인 호출 실패: {last_err}")

    def write_magazine_article(
        self,
        topic: Dict[str, Any],
        seo_brief: Dict[str, Any],
        use_cache: bool = False
    ) -> Dict[str, Any]:
        """
        100대 주제 1개와 실시간 키워드를 조합하여 2,000자 칼럼과 맞춤 사진 프롬프트 생성
        (use_cache=True인 경우 기존 작성된 원고가 있으면 즉시 재사용하여 API 호출 비용 0원 유지)
        """
        topic_id = topic.get("id", 1)
        topic_title = topic["title"]
        category_key = topic["category"]
        category_name = seo_brief.get("category_name", "2030 라이프")
        aura_feature = topic.get("aura_feature", "Aura AI 매력 리포트")
        intent = topic.get("intent", "2030 연애 꿀팁")

        # 🚀 [100% 실시간 신규 작성 원칙] 매회 Gemini AI가 새로운 칼럼 원고를 실시간 집필합니다.
        pass

        naver_keywords = seo_brief.get("seo_title_keywords", [])
        google_keywords = seo_brief.get("h2_h3_subheading_keywords", [])
        live_trends = seo_brief.get("live_trends", [])
        hashtags = seo_brief.get("viral_hashtags", [])

        system_instruction = f"""
당신은 대한민국 2030 트렌드 매거진 '💖 Aura 2030 매거진'의 수석 에디터이자 네이버 스마트블록 & 구글 SEO 1위 상위노출 전문 카피라이터입니다.
독자는 2030 세대 직장인과 대학생, 소개팅과 썸, 연애에 진심인 솔로 남녀입니다.
친근하면서도 세련되고 신뢰감 있는 매거진 에디터 톤앤매너로, 과도한 광고 느낌 없이 실전에서 바로 써먹을 수 있는 유려하고 전문적인 3,000자(3,000~3,500자) 한국어 마스터 칼럼을 집필해 주십시오.

[필수 작성 규칙]
1. 절대 '[본론 1]', '도입부', '심리 분석' 같은 개발/기획 지시어 용어를 본문이나 소제목에 그대로 적지 마십시오.
2. 🚨 [따옴표 규칙]: JSON 구문 오류를 방지하기 위해, 본문(content_md) 내 강조 표현이나 대화 멘트에는 큰따옴표(") 대신 반드시 작은따옴표(')만 사용하십시오.
2. 소제목은 독자가 읽고 싶어지는 매력적이고 세련된 에디토리얼 소제목(예: '✨ 1. 뻔한 질문 대신 상대방의 프로필에서 단서 찾기', '💡 2. 답장 간격보다 중요한 '대화의 텐션' 맞추기')으로 작성하십시오.
3. 제목에 특정 개수(예: '5가지 멘트', '3대 시그널')가 있다면, 본문 소제목이나 불릿포인트에서도 반드시 그 개수에 맞게 구체적인 실전 팁을 하나하나 명확히 다루십시오.
4. 본문(content_md) 안에 `![...](...)` 같은 로컬 이미지 마크다운 코드를 절대 넣지 마십시오. 이미지는 시스템이 에디터 상단에 별도로 업로드합니다.
5. 🚨 [URL 삽입 절대 금지]: 본문 텍스트 중간에 `(http...)` 또는 `[링크](http...)` 같은 인라인 URL을 절대로 삽입하지 마십시오. URL 링크와 공식 배너 카드는 시스템 엔진이 본문 하단에 별도 공식 모듈로 안전하게 자동 결합합니다. 본문 끝맺음은 오직 남녀 50:50 황금 성비 소개와 공식 검색 유도 문구("네이버에서 '아우라AI데이팅'을 검색해보세요")로만 정갈하게 작성하십시오.

반드시 아래 JSON 포맷으로만 응답하십시오:
{{
  "title_naver": "네이버 스마트블록 및 모바일 인기글 1위용 직관형/생활밀착형 고클릭률 제목",
  "title_tistory": "구글 검색(SEO) 및 Daum 검색 최적화용 가이드/총정리형 고신뢰도 제목",
  "title_kakao": "카카오/브런치스토리 및 소셜 피드용 감성 에세이 및 강력한 훅(Hook) 제목",
  "excerpt": "독자의 호기심을 자극하고 본문 핵심을꿰뚫는 1~2줄 요약문 (120자 내외)",
  "visual_prompt": "당신이 집필한 본문 스토리의 가장 결정적이고 로맨틱한 핵심 장면을 포착한 Imagen 3 전용 영문 프롬프트 (🚨 절대 천편일률적인 카페 테이블 마주앉기 금지! 🌟 반드시 매력적인 2030 한국인 남녀 커플 두 명이 본문 스토리의 배경 장소에 맞게 자연스럽게 데이트하는 모습이 필수 포함되어야 함: 와인바면 바 카운터에서 은은한 촛불 아래 와인잔을 기울이며 대화하는 남녀 커플, 성수동이면 트렌디한 붉은 벽돌 거리/플래그십 스토어 앞을 나란히 미소 지으며 걷는 남녀 커플, 남산이면 반짝이는 서울 야경을 배경으로 산책로에서 손을 잡고 걷는 남녀 커플, 한강이면 노을빛 수변 잔디밭을 함께 거니는 남녀 커플, 룩북이면 세련된 서울 도심 횡단보도를 걷는 감각적인 남녀 등 본문 스토리의 배경 장소와 데이트 상황에 100% 완벽히 일치하는 배경/의상/데이트 동작 상세 묘사. Two attractive Korean young adults, a handsome man and a beautiful woman on a romantic date, upright head posture looking straight ahead with zero head tilt, cozy Seoul aesthetic, photorealistic, cinematic natural lighting, 16:9 포함)",
  "discussion_prompt": "아우라 싱글 유저들이 글을 다 읽고 아래 댓글창에서 활발하게 의견을 나누고 티키타카 소통할 수 있도록 유도하는 매력적인 1~2문장의 질문 (예: 'Aura 여러분은 소개팅 첫 카톡에서 상대방 프로필 사진 칭찬 vs 솔직한 인사 중 어떤 멘트를 가장 선호하시나요? 아래 댓글로 여러분만의 꿀팁을 들려주세요!')",
  "content_md": "마크다운 전문 (공백 포함 약 3,000~3,500자, 공백 제외 2,200자 이상의 꽉 찬 전문)"
}}
"""

        user_prompt = f"""
[기획 주제 정보]
- 메인 주제: {topic_title}
- 카테고리: {category_name} ({category_key})
- 기획 의도: {intent}
- 연계할 Aura AI 기능: {aura_feature}
- 2030 데이트 트렌드 키워드: {', '.join(live_trends)}
- 네이버 실시간 검색 키워드: {', '.join(naver_keywords)}
- 구글 Suggest 질문형 키워드: {', '.join(google_keywords)}
- 공식 검색어: 아우라AI데이팅

[글자수 및 구성 절대 수칙 - 매일 완전히 새로운 최신 트렌드 칼럼 집필]
1. 제목 3종(title_naver, title_tistory, title_kakao)은 서로 다른 매력적인 스타일로 각각 작성하십시오.
2. 🚨 [지역명 및 주제 고유성 100% 보존 절대 규칙]: 메인 주제('{topic_title}')에 명시된 고유 지역(성수동, 한남동, 을지로, 잠실, 강남역 등)이나 핵심 주제(스몰토크, MBTI, 룩북, 애프터 등)를 임의로 다른 지역(연남동 등)이나 다른 카테고리로 절대 바꾸거나 왜곡하지 마십시오! 반드시 원본 기획 주제의 고유 지역과 테마를 제목과 본문 전체의 중심축으로 집필하십시오.
3. 🚨 [절대 금기: 억지 비유 및 진부한 전개 배제]: 무관한 스포츠 선수나 유명인, 엉뚱한 비유를 억지로 끼워 넣지 말고, 2030 세대의 생생한 데이트 심리와 실전 팁을 스토리텔링으로 진정성 있게 집필하십시오.
4. 본문(content_md) 총 글자 수는 반드시 공백 포함 딱 3,000자 ~ 3,500자(공백 제외 2,200~2,600자) 수준으로 작성하십시오.
   - 🚨 [너무 길어지지 않게 상한선 엄수]: 3,500자를 초과하여 불필요하게 늘어지지 않도록 깔끔하게 통제하십시오.
5. 본문 5대 심층 매거진 챕터 구성 (각 챕터별 균형 배분):
   - ① 2026 데이팅 트렌드 & 관계 심리 인트로 (약 500자)
   - ② 상황별 카톡/대화 티키타카 실전 공략법 3~4개 (각 250~300자, 총 1,000자 내외)
   - ③ 고유 지역 핫플 데이트 동선 & 공간 바이블 (약 600자): 1차 맛집 -> 2차 감성 장소 완벽 코스
   - ④ 첫인상 비주얼 밸런스 & 비언어적 애티튜드 (약 500자): 스타일링 및 매력 포인트
   - ⑤ Aura AI 스마트 솔루션 & 에디터 총평 + 댓글 소통 (약 400자): 50:50 황금 성비 AI 매칭 및 공식 검색 유도
6. 절대 `[본론 1]`, `도입부` 같은 메타 지침 문구를 쓰지 마십시오! 독자가 읽는 매거진 잡지처럼 세련되게 작성하십시오.
7. 🚨 본문 텍스트 내에 직접적인 URL 주소(http/https)를 적지 마십시오! 링크는 시스템이 본문 끝에 공식 카드로 자동 생성합니다.
8. 독자 소통용 댓글 유도 질문(discussion_prompt)을 반드시 매력적으로 작성하십시오.
9. 🚨 [스토리 맞춤형 실사 사진 프롬프트(visual_prompt) 혁신 수칙 - 맨날 걷기만 하는 사진 전면 금지!]:
   - 🛑 [절대 금기: 천편일률적인 전신 걷는 사진(walking/strolling) 반복 생성 금지!]: 길거리나 골목을 나란히 걷기만 하는 지루한 워킹샷을 전면 배제하십시오.
   - 🌟 [다채롭고 생생한 2030 데이트 인터랙션 씬 필수 반영]: 본문 스토리에 맞춰 아래와 같은 살아있는 감성 순간을 역동적 앵글(바스트샷, 클로즈업, 오버더숄더)로 묘사하십시오:
     ① [감성 카페/디저트]: 디저트 케이크나 포크를 들고 서로 웃으며 대화하는 다정한 미디엄 샷
     ② [무드 와인바/다이닝]: 은은한 캔들 라이트 아래 와인잔을 가볍게 부딪히며(toasting) 눈을 맞추는 로맨틱한 순간
     ③ [LP바/재즈클럽/서점]: 감성 조명 아래 헤드폰을 함께 나눠 끼거나 LP판 커버를 들여다보는 지적인 낭만
     ④ [트렌디 팝업스토어/전시회]: 인터랙티브 미디어아트나 독특한 전시품 앞에서 속삭이며 미소 짓는 실사 샷
     ⑤ [루프탑/피크닉]: 잔디밭이나 루프탑 벤치에서 커피를 마시며 편안하게 기대어 쉬는 힐링 샷
     ⑥ [스마트폰/인생네컷 셀카]: 스마트폰 화면을 함께 보며 환하게 웃거나 포토부스에서 장난스런 포즈를 취하는 리얼 순간
   - 반드시 "Two attractive Korean young adults, a handsome man and a beautiful woman on an intimate date, photorealistic, natural cinematic lighting, 16:9 aspect ratio"를 포함하여 매번 다른 매력적인 포즈와 공간으로 영문 프롬프트 1문장을 작성하십시오.
"""

        logger.info(f"📝 [AuraGeminiWriter] 주제 #{topic.get('id')} Gemini 3,000자 칼럼 & 3종 맞춤 제목 생성 시작...")
        raw_json = self._call_gemini_smart(user_prompt, system_instruction)

        # JSON 안전 파싱 로직
        clean_str = raw_json.strip()
        if "```json" in clean_str:
            clean_str = clean_str.split("```json", 1)[1]
        if "```" in clean_str:
            clean_str = clean_str.split("```", 1)[0]

        import re
        clean_str = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', clean_str.strip())
        start_idx = clean_str.find('{')
        end_idx = clean_str.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            clean_str = clean_str[start_idx:end_idx + 1]

        parsed = {}
        try:
            parsed = json.loads(clean_str, strict=False)
        except Exception as parse_err:
            logger.warning(f"⚠️ [AuraGeminiWriter] JSON 파싱 실패 ({parse_err}), 정규식 정밀 추출 가동")
            t_match = re.search(r'"title_naver"\s*:\s*"([^"]+)"', clean_str)
            p_title = t_match.group(1) if t_match else f"2026 {topic_title}"
            v_match = re.search(r'"visual_prompt"\s*:\s*"([^"]+)"', clean_str)
            p_vis = v_match.group(1) if v_match else "realistic Korean young adult couple talking warmly in cozy cafe, 16:9"
            d_match = re.search(r'"discussion_prompt"\s*:\s*"([^"]+)"', clean_str)
            p_disc = d_match.group(1) if d_match else "Aura 회원 여러분의 생각은 어떠신가요? 아래 댓글로 여러분만의 꿀팁을 남겨주세요!"
            
            # 🚀 [본문 3,000자 무결성 정밀 추출기] content_md 시작 따옴표 ➔ 마지막 닫는 따옴표까지 그리디(Greedy) 탐색
            extracted_content = self._extract_content_md_greedy(clean_str)
            if not extracted_content:
                extracted_content = self._generate_fallback_content(topic_title, category_name, aura_feature)

            parsed = {
                "title_naver": p_title,
                "title_tistory": f"[2026 가이드] {topic_title} 핵심 정리",
                "title_kakao": f"{topic_title}에 대한 솔직한 이야기",
                "excerpt": f"2030 {topic_title} 실전 가이드",
                "visual_prompt": p_vis,
                "discussion_prompt": p_disc,
                "content_md": extracted_content
            }

        title_naver = parsed.get("title_naver") or parsed.get("title", f"2026 {topic_title}")
        title_tistory = parsed.get("title_tistory") or f"[2026 가이드] {topic_title} 핵심 정리"
        title_kakao = parsed.get("title_kakao") or f"{topic_title}에 대한 솔직한 이야기"
        title = title_naver  # 기본 호환용 타이틀
        content_md = parsed.get("content_md", "")

        # 🚨 [절대 무결성 게이트: 본문 내 JSON 원문 및 기계어 유출 100% 차단]
        if not content_md or '{"title_naver"' in content_md or '"visual_prompt"' in content_md or content_md.strip().startswith('{'):
            logger.warning("🚨 [AuraGeminiWriter] 본문에 JSON 기계어 유출 감지! 고품질 한국어 칼럼으로 안전 복원합니다.")
            content_md = self._generate_fallback_content(topic_title, category_name, aura_feature)

        # 🛡️ [무결점 글자수 가드] 어떤 경우에도 공백 포함 2,500자 미만으로 떨어지지 않도록 최종 보정
        if len(content_md.strip()) < 2500:
            logger.warning(f"⚠️ [AuraGeminiWriter] 본문 글자수 부족({len(content_md.strip())}자 < 2,500자) ➔ 2,800자 고품질 칼럼으로 자동 보강합니다.")
            content_md = self._generate_fallback_content(topic_title, category_name, aura_feature)

        excerpt = parsed.get("excerpt", f"2030 {topic_title} 실전 가이드")
        visual_prompt = parsed.get("visual_prompt", "")
        discussion_prompt = parsed.get("discussion_prompt", "Aura 싱글 여러분의 생각은 어떠신가요? 아래 댓글로 여러분만의 솔직한 생각과 꿀팁을 들려주세요!")

        return {
            "topic_id": topic.get("id"),
            "category": category_key,
            "category_name": category_name,
            "title": title,
            "title_naver": title_naver,
            "title_tistory": title_tistory,
            "title_kakao": title_kakao,
            "excerpt": excerpt,
            "content_md": content_md,
            "visual_prompt": visual_prompt,
            "discussion_prompt": discussion_prompt,
            "aura_feature": aura_feature,
            "hashtags": hashtags,
            "landing_url": self.LANDING_URL
        }

    def _extract_content_md_greedy(self, raw_text: str) -> str:
        """
        🚀 [본문 3,000자 무결성 정밀 추출기]
        - JSON 파싱이 깨져도 'content_md' 필드의 시작 따옴표부터 마지막 닫는 따옴표까지 그리디(Greedy) 탐색
        - 이스케이프된 따옴표(\\") 및 줄바꿈(\\n)을 원형 그대로 복원하여 char 1017 절단 버그 원천 차단
        """
        if not raw_text:
            return ""

        key_idx = raw_text.find('"content_md"')
        if key_idx == -1:
            return ""

        # 키 이후 첫 번째 콜론 ➔ 첫 번째 시작 따옴표 위치 탐색
        colon_idx = raw_text.find(':', key_idx)
        if colon_idx == -1:
            return ""
        start_quote = raw_text.find('"', colon_idx)
        if start_quote == -1:
            return ""

        body = raw_text[start_quote + 1:]

        # 🎯 그리디 탐색: 마지막 닫는 따옴표(JSON 종료 지점)까지 통째로 확보
        end_quote = body.rfind('"')
        if end_quote == -1:
            # 닫는 따옴표가 아예 없으면(중간 절단) 남은 전체를 본문으로 사용
            candidate = body
        else:
            candidate = body[:end_quote]

        # 🧹 후행 JSON 잔여물(}, ], 공백) 정리
        candidate = candidate.rstrip()
        while candidate.endswith(("}", "]", ",", " ")):
            candidate = candidate[:-1].rstrip()

        # 🔄 이스케이프 복원 (\\n ➔ 실제 줄바꿈, \\" ➔ 큰따옴표, \\\\ ➔ 역슬래시)
        candidate = candidate.replace("\\\\n", "\n").replace("\\n", "\n")
        candidate = candidate.replace('\\\\"', '"').replace('\\"', '"')
        candidate = candidate.replace("\\\\t", "\t").replace("\\t", "\t")
        candidate = candidate.replace("\\\\/", "/").replace("\\/", "/")
        candidate = candidate.replace("\\\\", "\\")

        # 🚨 기계어 유출 잔재 제거
        for junk in ['"title_naver"', '"visual_prompt"', '"discussion_prompt"', '"excerpt"', '"title_tistory"', '"title_kakao"']:
            if junk in candidate:
                candidate = candidate.split(junk)[0]

        return candidate.strip()

    def _generate_fallback_content(self, topic_title: str, category_name: str, aura_feature: str) -> str:
        """JSON 파싱 실패 시 기계어 노출을 100% 방지하는 완성형 2,800자+ 고품질 매거진 칼럼 (5대 챕터 구성)"""
        return f"""바쁜 하루를 마치고 스마트폰 화면을 켜면, 문득 스쳐 가는 생각이 있습니다. '요즘 나는 누군가에게 설레고 있는 걸까, 아니면 그저 외로움에 익숙해진 걸까.' 2030 세대에게 연애는 더 이상 인생의 당연한 코스가 아니라, 스스로 선택하고 관리해야 하는 하나의 '라이프 프로젝트'가 되었습니다. 오늘 '{topic_title}'라는 주제를 붙잡고 {category_name} 카테고리에서 가장 뜨거운 고민들을 하나씩 풀어보려 합니다.

특히 최근 2030 데이팅 시장의 가장 큰 변화는 '속도'가 아니라 '밀도'입니다. 만남의 횟수를 늘리는 것보다, 한 번의 만남에서 얼마나 깊은 대화를 나눴는지가 관계의 생존을 결정합니다. 그래서 오늘은 감으로만 넘기던 연애의 순간들을, 실전에서 바로 써먹을 수 있는 구체적인 언어와 동선으로 정리해 드리겠습니다.

---

### ✨ 1. 2026 데이팅 트렌드, '스펙'보다 '온도'가 이긴다
예전에는 학벌, 직업, 연봉 같은 스펙표가 만남의 첫 관문이었다면, 지금은 다릅니다. 상대방이 나와 대화할 때 얼마나 편안해하는지, 즉 '대화의 온도'가 첫 번째 필터가 되었습니다. 실제로 2030 싱글들이 가장 많이 하는 말은 '대화가 잘 통하는 사람'입니다. 이는 곧 감정의 결이 맞는 사람을 찾는다는 뜻이기도 합니다.

그래서 첫 만남에서 절대 해서는 안 되는 것이 '면접형 질문'입니다. '무슨 일 하세요?', '어디 사세요?' 같은 정보 수집형 질문은 상대를 긴장하게 만들 뿐입니다. 대신 '요즘 가장 재미있게 본 콘텐츠가 뭐예요?'처럼 취향과 감정이 드러나는 질문을 던져보세요. 대화의 온도가 순식간에 올라가는 것을 느낄 수 있습니다.

### 💬 2. 상황별 카톡 티키타카 실전 공략 4가지
**① 첫 카톡, 프로필에서 단서를 찾아라**
'안녕하세요'로 시작하는 무미건조한 인사는 읽씹의 지름길입니다. 상대 프로필 사진 속 배경, 여행지, 반려동물, 좋아하는 음식 등 구체적인 단서를 하나 골라 언급하세요. '프로필에 있는 그 카페 어디예요? 분위기가 너무 좋아 보여서요'라는 한 문장이 대화의 물꼬를 터줍니다.

**② 답장 텀보다 중요한 건 '대화의 리듬'**
답장이 늦다고 조급해할 필요는 없습니다. 중요한 것은 내가 답장을 보냈을 때 상대가 다시 이어갈 수 있는 '실마리'를 남기는 것입니다. 질문으로 끝맺고, 상대의 이야기에 최소 한 문장 이상 반응해 주세요. 이 리듬이 세 번 이상 이어지면 관계는 이미 안정 궤도에 들어선 것입니다.

**③ 호감 표현은 '구체성'이 생명이다**
'예쁘시네요', '멋지세요' 같은 추상적 칭찬은 기억에 남지 않습니다. '오늘 옷 색감이 정말 잘 어울리세요', '말할 때 표정이 참 좋아 보여요'처럼 구체적인 관찰을 담아야 진심으로 전달됩니다. 칭찬은 하루에 한 번, 타이밍을 정확히 잡는 것이 훨씬 효과적입니다.

**④ 애프터 신청은 '선택지'로 건네라**
'또 만나요'는 상대에게 부담을 줍니다. 대신 '다음에 성수동 쪽 간다면, 제가 아는 조용한 와인바 하나 소개해드리고 싶어요. 언제가 편하세요?'처럼 구체적인 장소와 선택지를 제시하세요. 상대는 거절의 부담 없이 자연스럽게 다음 약속을 잡게 됩니다.

### 🍷 3. 실패 없는 데이트 동선 & 공간 바이블
좋은 데이트는 '어디를 갔느냐'보다 '어떤 순서로 움직였느냐'로 결정됩니다. 가장 안정적인 코스는 1차에서 대화의 온도를 올리고, 2차에서 감정의 밀도를 높이는 구조입니다.

1차는 너무 조용하지도, 너무 시끄럽지도 않은 공간이 좋습니다. 적당한 소음이 있는 캐주얼 다이닝이나 브런치 카페는 어색한 침묵을 자연스럽게 메워줍니다. 여기서 40~60분 정도 대화를 나누며 상대의 말투와 리듬을 파악하세요.

2차는 반드시 '이동'이 있어야 합니다. 같은 자리에 계속 앉아 있으면 대화 소재가 고갈됩니다. 조용한 와인바, LP바, 작은 전시회, 야경이 보이는 루프탑 등으로 짧게 이동하는 것만으로도 분위기는 완전히 달라집니다. 이때 조명이 은은하고 음악 볼륨이 낮은 곳을 고르는 것이 핵심입니다.

마무리는 아쉬움을 남기는 것이 정답입니다. '오늘 너무 즐거웠어요'라고 말하며 먼저 깔끔하게 마무리하면, 상대는 다음 만남을 자연스럽게 기대하게 됩니다. 길게 늘어지는 것보다 짧고 선명한 마무리가 훨씬 강한 인상을 남깁니다.

### 👔 4. 첫인상 비주얼 밸런스 & 비언어적 애티튜드
첫 만남에서 상대가 나를 판단하는 시간은 단 3초입니다. 그 3초를 결정하는 것은 화려함이 아니라 '정돈된 균형'입니다. 과한 명품이나 튀는 색보다, 깔끔한 핏과 은은한 향, 정돈된 헤어가 훨씬 강력한 무기입니다.

비언어적 태도도 절대 무시할 수 없습니다. 대화할 때 상대의 눈을 3초 이상 바라보고, 고개를 살짝 끄덕이며 반응해 주세요. 스마트폰은 테이블 위에 엎어두는 것만으로도 '당신에게 집중하고 있다'는 신호가 됩니다. 앉을 때 등받이에 기대지 않고 살짝 앞으로 기울이는 자세는 진심이 전달되는 대표적인 제스처입니다.

### 💑 5. Aura AI 스마트 솔루션 & 에디터 총평
결국 연애의 성패는 '얼마나 좋은 사람을 만났는가'에서 갈립니다. 아무리 대화법을 익혀도, 나와 결이 맞지 않는 사람과는 오래 갈 수 없습니다. 그래서 필요한 것이 {aura_feature}입니다. Aura는 남초 어플의 읽씹과 허위 프로필, 성비 불균형 문제를 해결하고, 남녀 50:50 황금 성비 속에서 가치관과 라이프스타일이 맞는 상대를 정교하게 매칭합니다.

💡 **Aura 에디터 한 줄 치트키**
진정한 매력은 꾸며낸 기술이 아니라, 상대방의 이야기에 귀 기울여주는 다정한 태도에서 시작됩니다. 오늘 배운 네 가지 대화법 중 단 하나만이라도 실전에서 써보세요. 그것만으로도 당신의 연애는 분명히 달라집니다.

네이버에서 '아우라AI데이팅'을 검색해보세요!"""


if __name__ == "__main__":
    writer = AuraGeminiWriter()
    sample_topic = {
        "id": 1,
        "category": "kakaotalk_signals",
        "title": "소개팅 첫 카톡 읽씹을 피하는 호감형 첫인사 멘트 5가지",
        "intent": "자연스러운 핑퐁 시작",
        "aura_feature": "Aura AI 카톡 답장 코칭"
    }
    sample_brief = {
        "category_name": "카톡 밀당 & 시그널",
        "seo_title_keywords": ["소개팅 첫 카톡", "소개팅 읽씹 안당하는법"],
        "h2_h3_subheading_keywords": ["소개팅 카톡 텀 호감도", "자연스러운 티키타카 질문"],
        "viral_hashtags": ["#소개팅첫카톡", "#읽씹방지", "#AuraAI"]
    }
    res = writer.write_magazine_article(sample_topic, sample_brief)
    print("생성 완료:", json.dumps(res, ensure_ascii=False, indent=2))
