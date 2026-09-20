# -*- coding: utf-8 -*-
"""
Aura Gemini Writer (💖 Aura 2030 매거진 전문 AI 원고 & 비주얼 프롬프트 작성기)
=============================================================================
- 브랜드: Aura (2030 AI 데이팅 / 매칭 라운지 / 소개팅 코칭)
- 역할:
  1. 100대 주제 풀 + 실시간 네이버/구글 키워드를 입력받아 2,000자 고품질 전문 칼럼 작성
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
        candidates = [
            {"name": "AURA_FREE_1 (전용 무료키 #1)", "key": GEMINI_FREE_API_KEY_AURA_1},
            {"name": "AURA_FREE_2 (전용 무료키 #2)", "key": GEMINI_FREE_API_KEY_AURA_2},
            {"name": "AURA_FREE_3 (전용 무료키 #3)", "key": GEMINI_FREE_API_KEY_AURA_3},
            {"name": "AURA_PAID_1 (전용 유료키 #1)", "key": GEMINI_PAID_API_KEY_AURA_1},
            {"name": "AURA_PAID_2 (전용 유료키 #2)", "key": GEMINI_PAID_API_KEY_AURA_2},
            {"name": "BACKUP_FREE_KM (KMarket 무료키)", "key": GEMINI_FREE_API_KEY_KMARKET},
            {"name": "BACKUP_FREE_ET (EasyTax 무료키)", "key": GEMINI_FREE_API_KEY_EASYTAX},
            {"name": "DEFAULT_KEY (기본키)", "key": GEMINI_API_KEY},
        ]

        seen = set()
        self.key_chain = []
        for c in candidates:
            k = (c.get("key") or "").strip()
            if k and k not in seen and len(k) > 10:
                seen.add(k)
                self.key_chain.append({"name": c["name"], "key": k})

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

                for model_name in ["gemini-3.1-flash-lite", "gemini-2.0-flash", "gemini-flash-latest"]:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config=genai_types.GenerateContentConfig(
                                system_instruction=system_instruction,
                                temperature=0.75,
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
        use_cache: bool = True
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

        # ⚡ [비용 0원 원칙] 기존 로컬에 작성된 고품질 원고가 있으면 즉시 재사용 (Gemini 호출 차단)
        if use_cache:
            blog_dir = PROJECT_ROOT / "outputs" / "aura" / "blogs"
            if blog_dir.exists():
                existing = sorted(list(blog_dir.glob(f"aura_blog_topic_{topic_id:03d}_*.json")), reverse=True)
                if existing:
                    try:
                        with open(existing[0], "r", encoding="utf-8") as fp:
                            cached_data = json.load(fp)
                        if cached_data.get("title") and cached_data.get("content_md"):
                            logger.info(f"⚡ [AuraGeminiWriter] 주제 #{topic_id} 기존 칼럼 원고 캐시 즉시 재사용 (비용 0원!): {existing[0].name}")
                            return {
                                "topic_id": topic_id,
                                "category": category_key,
                                "category_name": category_name,
                                "title": cached_data.get("title", ""),
                                "title_naver": cached_data.get("title_naver", cached_data.get("title", "")),
                                "title_tistory": cached_data.get("title_tistory", cached_data.get("title", "")),
                                "title_kakao": cached_data.get("title_kakao", cached_data.get("title", "")),
                                "excerpt": cached_data.get("excerpt", ""),
                                "visual_prompt": cached_data.get("visual_prompt", ""),
                                "discussion_prompt": cached_data.get("discussion_prompt", "Aura 싱글 여러분의 생각은 어떠신가요? 아래 댓글로 여러분만의 솔직한 생각과 꿀팁을 남겨주세요!"),
                                "content_md": cached_data.get("content_md", ""),
                                "is_cached": True
                            }
                    except Exception as ce:
                        logger.debug(f"캐시 원고 로드 예외: {ce}")

        naver_keywords = seo_brief.get("seo_title_keywords", [])
        google_keywords = seo_brief.get("h2_h3_subheading_keywords", [])
        hashtags = seo_brief.get("viral_hashtags", [])

        system_instruction = f"""
당신은 대한민국 2030 트렌드 매거진 '💖 Aura 2030 매거진'의 수석 에디터이자 네이버 스마트블록 & 구글 SEO 1위 상위노출 전문 카피라이터입니다.
독자는 2030 세대 직장인과 대학생, 소개팅과 썸, 연애에 진심인 솔로 남녀입니다.
친근하면서도 세련되고 신뢰감 있는 매거진 에디터 톤앤매너로, 과도한 광고 느낌 없이 실전에서 바로 써먹을 수 있는 유려하고 전문적인 2,000자 한국어 마스터 칼럼을 집필해 주십시오.

[필수 작성 규칙]
1. 절대 '[본론 1]', '도입부', '심리 분석' 같은 개발/기획 지시어 용어를 본문이나 소제목에 그대로 적지 마십시오.
2. 소제목은 독자가 읽고 싶어지는 매력적이고 세련된 에디토리얼 소제목(예: '✨ 1. 뻔한 질문 대신 상대방의 프로필에서 단서 찾기', '💡 2. 답장 간격보다 중요한 '대화의 텐션' 맞추기')으로 작성하십시오.
3. 제목에 특정 개수(예: '5가지 멘트', '3대 시그널')가 있다면, 본문 소제목이나 불릿포인트에서도 반드시 그 개수에 맞게 구체적인 실전 팁을 하나하나 명확히 다루십시오.
4. 본문(content_md) 안에 `![...](...)` 같은 로컬 이미지 마크다운 코드를 절대 넣지 마십시오. 이미지는 시스템이 에디터 상단에 별도로 업로드합니다.

반드시 아래 JSON 포맷으로만 응답하십시오:
{{
  "title_naver": "네이버 스마트블록 및 모바일 인기글 1위용 직관형/생활밀착형 고클릭률 제목",
  "title_tistory": "구글 검색(SEO) 및 Daum 검색 최적화용 가이드/총정리형 고신뢰도 제목",
  "title_kakao": "카카오/브런치스토리 및 소셜 피드용 감성 에세이 및 강력한 훅(Hook) 제목",
  "excerpt": "독자의 호기심을 자극하고 본문 핵심을 꿰뚫는 1~2줄 요약문 (120자 내외)",
  "visual_prompt": "이 글의 장면과 분위기에 100% 부합하는 Imagen 3 전용 영문 사진 프롬프트 1문장 (반드시 realistic Korean young adult, cozy Seoul aesthetic, cinematic natural lighting, photorealistic, 16:9 포함)",
  "discussion_prompt": "아우라 싱글 유저들이 글을 다 읽고 아래 댓글창에서 활발하게 의견을 나누고 티키타카 소통할 수 있도록 유도하는 매력적인 1~2문장의 질문 (예: 'Aura 여러분은 소개팅 첫 카톡에서 상대방 프로필 사진 칭찬 vs 솔직한 인사 중 어떤 멘트를 가장 선호하시나요? 아래 댓글로 여러분만의 꿀팁을 들려주세요!')",
  "content_md": "마크다운 전문 (공백 포함 약 1,800~2,200자, 공백 제외 1,400자 이상의 꽉 찬 전문)"
}}
"""

        user_prompt = f"""
[기획 주제 정보]
- 메인 주제: {topic_title}
- 카테고리: {category_name} ({category_key})
- 기획 의도: {intent}
- 연계할 Aura AI 기능: {aura_feature}
- 네이버 실시간 고노출 키워드: {', '.join(naver_keywords)}
- 구글 Suggest 질문형 키워드: {', '.join(google_keywords)}
- 바이럴 해시태그: {' '.join(hashtags)}
- 공식 랜딩 링크: {self.LANDING_URL}

[글자수 및 구성 절대 수칙]
1. 제목 3종(title_naver, title_tistory, title_kakao)은 서로 다른 매력적인 스타일로 각각 작성하십시오.
2. 본문(content_md) 총 글자 수는 반드시 공백 포함 1,800자 ~ 2,200자 분량으로 풍성하고 깊이 있게 집필하십시오.
3. 본문 구성:
   - 감성적이면서도 2030 독자의 공감을 100% 자극하는 오프닝 (300~350자)
   - 주제에 부합하는 실전 핵심 공략법/멘트/팁 3~5개 항목 (각 항목마다 세련된 소제목 부여, 1,000자 이상)
   - Aura의 '{aura_feature}'를 자연스럽게 소개하는 스마트 솔루션 제안 (300자)
   - 💡 Aura 에디터 실전 치트키 (Tip Box, 150자)
   - 공식 앱 바로가기 링크 ({self.LANDING_URL}) 및 해시태그
4. 절대 `[본론 1]`, `도입부` 같은 메타 지침 문구를 쓰지 마십시오! 독자가 읽는 매거진 잡지처럼 세련되게 작성하십시오.
5. 로컬 이미지 마크다운 태그(`![...](...)`)는 본문에 포함하지 마십시오.
6. 독자 소통용 댓글 유도 질문(discussion_prompt)을 반드시 매력적으로 작성하십시오.
"""

        logger.info(f"📝 [AuraGeminiWriter] 주제 #{topic.get('id')} Gemini 2,000자 칼럼 & 3종 맞춤 제목 생성 시작...")
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

        try:
            parsed = json.loads(clean_str)
        except Exception as parse_err:
            logger.warning(f"⚠️ [AuraGeminiWriter] JSON 파싱 실패 ({parse_err}), 정규식 구조 추출 시도")
            t_match = re.search(r'"title_naver"\s*:\s*"([^"]+)"', clean_str)
            p_title = t_match.group(1) if t_match else f"2026 {topic_title}"
            v_match = re.search(r'"visual_prompt"\s*:\s*"([^"]+)"', clean_str)
            p_vis = v_match.group(1) if v_match else "realistic Korean young adult couple talking warmly in cozy cafe, 16:9"
            d_match = re.search(r'"discussion_prompt"\s*:\s*"([^"]+)"', clean_str)
            p_disc = d_match.group(1) if d_match else "Aura 회원 여러분의 생각은 어떠신가요? 아래 댓글로 여러분만의 꿀팁을 남겨주세요!"
            parsed = {
                "title_naver": p_title,
                "title_tistory": f"[2026 가이드] {topic_title} 핵심 정리",
                "title_kakao": f"{topic_title}에 대한 솔직한 이야기",
                "excerpt": f"2030 {topic_title} 실전 가이드",
                "visual_prompt": p_vis,
                "discussion_prompt": p_disc,
                "content_md": clean_str
            }

        title_naver = parsed.get("title_naver") or parsed.get("title", f"2026 {topic_title}")
        title_tistory = parsed.get("title_tistory") or f"[2026 가이드] {topic_title} 핵심 정리"
        title_kakao = parsed.get("title_kakao") or f"{topic_title}에 대한 솔직한 이야기"
        title = title_naver  # 기본 호환용 타이틀
        content_md = parsed.get("content_md", "")
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
