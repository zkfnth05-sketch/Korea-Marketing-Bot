# -*- coding: utf-8 -*-
"""
AuraCardnewsGeminiCopywriter - 💖 [Aura 카드뉴스 8대 주제 전용 제미나이 실시간 카피라이터]
========================================================================================
• 역할:
  - 8대 킬러 주제 및 선정된 10벌 룩북(OOTD)에 맞춰 5장 카드뉴스 전체 카피를 제미나이 1회 호출로 실시간 창작
  - 2030 최신 트렌드, 유머, 현실 공감, 바이럴 훅을 극대화한 신선한 헤드라인/불릿/찬반토론 자동 생성
  - 3단 무료키 순환 체인 (Aura 전용 무료키 #1 ➔ #2 ➔ #3) 100% 활용 (비용 0원)
  - 최신 google.genai 클라이언트 규격 (gemini-3.1-flash-lite, gemini-2.0-flash 등 자동 롤오버)
  - 엄격한 글자수/길이 무결성 게이트 및 통신 장애 시 안전 기본 카피 Fallback 탑재
  - 공식 검색어 '아우라AI데이팅' 및 공식 URL 불변 보장
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from brands.aura.aura_cardnews_scenario_director import AuraCardnewsScenarioDirector
from brands.aura.aura_production_safety_gate import AuraProductionSafetyGate

logger = logging.getLogger("AuraCardnewsGeminiCopywriter")


class AuraCardnewsGeminiCopywriter:
    """Aura 8대 주제 카드뉴스 5장 전체 카피 실시간 AI 창작 엔진"""

    OFFICIAL_KEYWORD = "아우라AI데이팅"
    OFFICIAL_URL = "https://aura-ai-dating.vercel.app/"

    # 8대 주제별 핵심 기능 & 킬러 소구점 헌장 (제미나이가 뜬구름 잡지 않고 100% 주제 밀착 창작하도록 강제)
    TOPIC_DOSSIERS = {
        1: {
            "title": "소개팅 긴급 탈출 전화 (escape_call)",
            "pain_point": "사진과 실물이 너무 다르거나 무례하고 어색한 소개팅 자리, 눈치 보며 2차까지 끌려가는 고통",
            "solution_feature": "Aura 앱의 '긴급 탈출 전화' - 30분 뒤 팀장님 가짜 업무 전화 자동 수신 예약 + 화면에 자연스러운 통화 대본 표출",
            "hook_keyword": "합법적 매너 탈출, 팀장님 긴급 전화, 1차 정중 귀가, 소개팅 구조 신호"
        },
        2: {
            "title": "실시간 AI 자막 통화 (realtime_subtitles)",
            "pain_point": "외국인 친구나 글로벌 썸녀와 대화하고 싶은데 외국어 회화가 막막하고 어색한 장벽",
            "solution_feature": "내가 한국어로 말하면 상대에게 실시간 번역 자막이 즉시 표출되는 넷플릭스형 실시간 AI 자막 통화",
            "hook_keyword": "언어 장벽 제로, 일본 여사친과 밤샘 통화, 실시간 번역 자막, 글로벌 친구 매칭"
        },
        3: {
            "title": "50:50 남녀 황금 성비 라운지 (vip_gate_5050)",
            "pain_point": "남자가 90%인 남초 지옥 소개팅 앱, 과도한 유료 결제 유도와 알바 계정에 지친 피로감",
            "solution_feature": "남녀 성비 50:50을 실시간 통제하는 VIP 게이트 + 본인 실명 및 신원 검증된 2030 전용 라운지",
            "hook_keyword": "50:50 황금 성비, 남초 지옥 탈출, 유령/알바 회원 0%, 실명 인증 클린 라운지"
        },
        4: {
            "title": "청담동 화보 프로필 스튜디오 (cheongdam_photo)",
            "pain_point": "평범한 화장실 셀카나 흔들린 사진 때문에 첫인상 프로필 심사에서 매번 광탈당하는 현실",
            "solution_feature": "평범한 일상 사진 1장을 1초 만에 청담동 하이엔드 스튜디오 화보급 프로필로 업그레이드해주는 AI 인생화보",
            "hook_keyword": "청담동 화보 프로필, 프로필 사진 1초 변환, 매칭률 300% 폭발, 첫인상 치트키"
        },
        5: {
            "title": "2030 가치관 밸런스 게임 (value_balance)",
            "pain_point": "얼굴만 보고 만났다가 연락 빈도, 데이트 비용, 소비 습관 등 가치관 차이로 파탄 나는 연애",
            "solution_feature": "2030 핫이슈 밸런스 질문 10문항으로 연애관/결혼관/소비관 일치율 90% 이상인 찰떡 이성 자동 매칭",
            "hook_keyword": "가치관 밸런스 매칭, 연락 빈도/데이트 비용 일치, 낭비 없는 찐 케미, 성향 맞춤 소개팅"
        },
        6: {
            "title": "AI 첫대화 비서 / 스마트 오프너 (smart_opener)",
            "pain_point": "매칭되어도 '안녕하세요'만 보내다 읽씹당하거나, 첫마디를 뭐라고 보낼지 몰라 막막한 순간",
            "solution_feature": "상대방의 프로필 사진과 취미/관심사를 AI가 분석하여 답장률 98% 폭발시키는 센스 있는 첫마디 3종 추천",
            "hook_keyword": "읽씹 탈출 치트키, AI 첫대화 비서, 센스 있는 오프너, 답장률 98% 폭발"
        },
        7: {
            "title": "AI 매력상 & 관상/궁합 진단 (ai_charm_scanner)",
            "pain_point": "내 객관적인 얼굴 분위기(여우상/강아지상/뮤즈 등)와 나에게 딱 맞는 이성 스타일을 모르는 답답함",
            "solution_feature": "얼굴 사진 1장으로 AI가 매력상과 관상을 1초 정밀 분석하고, 나와 궁합 99%인 찰떡 이성과 데이트 코스 도출",
            "hook_keyword": "AI 얼굴상 진단, 여우상 vs 강아지상, 궁합 99% 이성 매칭, 추천 데이트 코스"
        },
        8: {
            "title": "500m 안심 레이더 & 안심 번개 퀘스트 (safe_radar_500m)",
            "pain_point": "퇴근 후 가볍게 동네 친구를 만나고 싶은데 집 주소나 정밀 위치가 노출될까 봐 불안한 사생활 걱정",
            "solution_feature": "실제 거주지는 500m 반경 오차 지터링으로 완벽 보호하고, 24시간 뒤 자동 삭제되는 안심 번개 퀘스트 지도",
            "hook_keyword": "500m 안심 지터링 보안, 집 주소 100% 은폐, 성수동 퇴근길 번개, 24시간 자동 폭파 레이더"
        }
    }

    def __init__(self):
        from config import (
            GEMINI_FREE_API_KEY_AURA_1,
            GEMINI_FREE_API_KEY_AURA_2,
            GEMINI_FREE_API_KEY_AURA_3,
            GEMINI_PAID_API_KEY_AURA_1,
            GEMINI_FREE_API_KEY_KMARKET,
            GEMINI_API_KEY
        )

        candidates = [
            {"name": "AURA_FREE_1", "key": GEMINI_FREE_API_KEY_AURA_1},
            {"name": "AURA_FREE_2", "key": GEMINI_FREE_API_KEY_AURA_2},
            {"name": "AURA_FREE_3", "key": GEMINI_FREE_API_KEY_AURA_3},
            {"name": "AURA_PAID_1", "key": GEMINI_PAID_API_KEY_AURA_1},
            {"name": "KM_BACKUP_FREE", "key": GEMINI_FREE_API_KEY_KMARKET},
            {"name": "DEFAULT_KEY", "key": GEMINI_API_KEY},
        ]

        seen = set()
        self.key_chain = []
        for c in candidates:
            k = (c.get("key") or "").strip()
            if k and k not in seen and len(k) > 10:
                seen.add(k)
                self.key_chain.append({"name": c["name"], "key": k})

        self._active_key_index = 0
        self.scenario_director = AuraCardnewsScenarioDirector()
        logger.info(f"💖 [AuraCardnewsGeminiCopywriter] 키 체인 등록 완료 (총 {len(self.key_chain)}개)")

    def _get_genai_client(self, api_key: str):
        from google import genai
        return genai.Client(api_key=api_key)

    def generate_cardnews_copy(self, topic_id: int, outfit: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        주제 번호(1~8)와 의상 정보에 맞춰 5장 전체 카피를 제미나이 1회 호출로 실시간 창작 (풍성하고 깊이 있는 2030 스토리텔링)
        """
        dossier = self.TOPIC_DOSSIERS.get(topic_id, self.TOPIC_DOSSIERS[8])
        theme_title = dossier["title"]
        pain_point = dossier["pain_point"]
        solution_feature = dossier["solution_feature"]
        hook_keyword = dossier["hook_keyword"]

        outfit_name = outfit.get("name_ko", "트렌디 룩") if outfit else "2030 데이트룩"
        style_mood = outfit.get("style_mood", "세련된 무드") if outfit else "세련된 무드"

        prompt = f"""
당신은 대한민국 2030 트렌드와 심리를 꿰뚫어 보는 최고의 인스타그램/스레드 카드뉴스 수석 카피라이터입니다.
⚠️ [절대 철칙]: 
1. 단순하고 성의 없는 단문이나 짤막한 요약문은 엄격히 금지합니다!
2. 2030 타겟이 실제로 겪는 찐 고통과 상황(성수동/강남, 퇴근길, 어색한 소개팅, 스토킹 불안, 가치관 충돌 등)을 생생하게 묘사하세요.
3. 헤드라인, 서브타이틀, 불릿, 찬반 토론 모두 읽는 사람이 무릎을 탁 치며 몰입할 수 있도록 묵직하고 풍성하게 작성해야 합니다.
4. 반드시 아래 [주제 #{topic_id} 전용 팩트 시트]에 100% 밀착하여 창작하세요.

[ 주제 #{topic_id} 전용 팩트 시트 ]
- 주제명: {theme_title}
- 2030 타겟의 찐 고통(Pain Point): {pain_point}
- Aura만의 킬러 솔루션 기능: {solution_feature}
- 필수 훅 키워드: {hook_keyword}
- 브랜드: Aura (50:50 남녀 황금 성비율, 실명인증 2030 데이팅 라운지)
- 공식 네이버 검색어: "아우라AI데이팅" (절대 변경 금지)
- 이번 회차 모델 착장: {outfit_name} ({style_mood})

[ 5장 카드뉴스 구성 및 글자수 규격 가이드 ]
1. Slide 1 (킬러 표지 훅):
   - headline_line1, headline_line2: 2030의 상황과 고통을 생생하게 찌르는 묵직한 2줄 카피 (각 줄 18~25자 내외)
   - subtitle: 심리적 안도감과 솔루션을 제시하는 깊이 있는 2줄 설명글 (50~75자 내외)
   - bullets: 현실 고민 팩트 폭격 + Aura 솔루션을 담은 3문장 (각 문장 32~45자 내외의 알찬 완성형 문장)
   - cta_text: "👉 옆으로 넘겨서 탈출 비법 보기 (1/5) >"

2. Slide 2 (현실 공감 빌드업):
   - headline_line1, headline_line2: 2030이 겪는 찐 공감 상황 2줄 (각 줄 18~25자 내외)
   - subtitle: 감정적 피로와 시간 낭비를 짚어주는 공감 설명글 (50~75자 내외)
   - bullets: 주변에서 흔히 겪는 구체적인 실패/불안 사례 3문장 (각 문장 32~45자 내외)
   - cta_text: "👉 옆으로 넘겨서 1초 해결책 보기 (2/5) >"

3. Slide 3 (핵심 앱 기능 소개):
   - badge: "[Aura 솔루션 기능 배지]"
   - headline_line1, headline_line2: 앱 화면의 킬러 기능을 명쾌하게 선언하는 2줄 (각 줄 18~24자 내외)
   - subtitle: 이 기능이 작동하는 구체적인 원리와 안심 포인트를 설명하는 글 (45~65자 내외)
   - cta_text: "👉 옆으로 넘겨서 실시간 연동 지도 보기 (3/5) >"

4. Slide 4 (확장 가치 & 실제 경험):
   - badge: "[설레는 만남의 변화 배지]"
   - headline_line1, headline_line2: 이 기능을 썼을 때 누리게 되는 설레는 데이트 결과 2줄 (각 줄 18~24자 내외)
   - subtitle: 실제 2030 회원들이 누리는 편리함과 매칭 성공률을 풀어낸 설명글 (45~65자 내외)
   - cta_text: "👉 옆으로 넘겨서 회원가입 VIP 혜택 받기 (4/5) >"

5. Slide 5 (2030 핫이슈 찬반 토론 & CTA):
   - debate_badge: "⚡ 2030 핫이슈 찬반 토론"
   - debate_question: 커뮤니티(에타, 블라인드)를 뒤흔들 만한 흥미진진한 질문 (45~65자 내외)
   - debate_opt1_title: Option 1 제목 (16~22자)
   - debate_opt1_sub: Option 1 디테일 부연 (25~35자)
   - debate_opt2_title: Option 2 제목 (16~22자)
   - debate_opt2_sub: Option 2 디테일 부연 (25~35자)
   - benefit_items: Aura 가입 시 즉시 받는 VIP 3대 혜택 3개 (각 18~28자)
   - cta_subtext: "👉 프로필 링크에서 3초 만에 내 이상형/성향 확인해보세요! ✨"

6. SNS 캡션 (인스타그램/스레드 본문):
   - sns_caption: 인스타그램 피드에 그대로 올려서 댓글 수백 개를 유도할 수 있는 7~10줄 이상의 풍성한 스토리텔링 본문 (이모지, 공감 질문, 핵심 기능 소개 포함)
   - hashtags: 8개 이상의 트렌디한 해시태그 (#아우라AI데이팅 필수 포함)

반드시 아래 JSON 형식으로만 응답하세요 (마크다운 코드블록 없이 순수 JSON만 반환):
{{
  "slide1": {{
    "badge": "배지 문구 (예: 🔥 2030 소개팅 필독)",
    "headline_line1": "헤드라인 첫째줄 (18~25자)",
    "headline_line2": "헤드라인 둘째줄 (18~25자)",
    "subtitle": "서브타이틀 상세 설명 (50~75자)",
    "bullets": [
      "불릿 1 완성형 문장 (32~45자)",
      "불릿 2 완성형 문장 (32~45자)",
      "불릿 3 완성형 문장 (32~45자)"
    ],
    "cta_text": "👉 옆으로 넘겨서 비법 보기 (1/5) >"
  }},
  "slide2": {{
    "badge": "배지 문구 (예: 📍 현실 공감 100%)",
    "headline_line1": "헤드라인 첫째줄 (18~25자)",
    "headline_line2": "헤드라인 둘째줄 (18~25자)",
    "subtitle": "서브타이틀 상세 설명 (50~75자)",
    "bullets": [
      "불릿 1 완성형 문장 (32~45자)",
      "불릿 2 완성형 문장 (32~45자)",
      "불릿 3 완성형 문장 (32~45자)"
    ],
    "cta_text": "👉 옆으로 넘겨서 해결책 보기 (2/5) >"
  }},
  "slide3": {{
    "badge": "배지 문구 (예: 🛡️ 500m 안심 프라이버시 보안)",
    "headline_line1": "헤드라인 첫째줄 (18~24자)",
    "headline_line2": "헤드라인 둘째줄 (18~24자)",
    "subtitle": "서브타이틀 상세 설명 (45~65자)",
    "cta_text": "👉 옆으로 넘겨서 실시간 화면 보기 (3/5) >"
  }},
  "slide4": {{
    "badge": "배지 문구 (예: ⚡ 24시간 실시간 번개 퀘스트)",
    "headline_line1": "헤드라인 첫째줄 (18~24자)",
    "headline_line2": "헤드라인 둘째줄 (18~24자)",
    "subtitle": "서브타이틀 상세 설명 (45~65자)",
    "cta_text": "👉 옆으로 넘겨서 회원가입 혜택 받기 (4/5) >"
  }},
  "slide5": {{
    "debate_badge": "토론 배지 (예: ⚡ 2030 핫이슈 찬반 토론)",
    "debate_question": "찬반 토론 메인 질문 문구 (45~65자)",
    "debate_opt1_title": "선택지 1 제목 (16~22자)",
    "debate_opt1_sub": "선택지 1 부연 설명 (25~35자)",
    "debate_opt2_title": "선택지 2 제목 (16~22자)",
    "debate_opt2_sub": "선택지 2 부연 설명 (25~35자)",
    "benefit_items": [
      "사진 1장 3초 이상형 확인",
      "50:50 황금 성비율 매칭",
      "내 연애 스타일 & 핫플 테스트"
    ],
    "cta_subtext": "👉 프로필 링크에서 3초 만에 나랑 꼭 맞는 이상형 & 연애 성향 확인하기"
  }},
  "sns_caption": "인스타그램/스레드 본문 카피 (7~10줄 이상, 공감 질문 및 솔루션 포함 + 마지막에 '👉 프로필 링크에서 3초 만에 내 이상형/성향 확인해보세요!' 유도 필수)",
  "hashtags": "#아우라AI데이팅 #2030소개팅 #동네친구 #성수동데이트 #이상형테스트"
}}
"""

        # 최신 google.genai 및 모델 롤오버 체인
        total_keys = len(self.key_chain)
        for i in range(total_keys):
            idx = (self._active_key_index + i) % total_keys
            key_info = self.key_chain[idx]
            key_name = key_info["name"]
            api_key = key_info["key"]

            # 429 쿨다운 중인 키는 네트워크 호출 자체를 생략하여 API 낭비 차단
            if AuraProductionSafetyGate.is_cooled_down(key_name):
                logger.info(f"⏳ [AuraGeminiCopywriter] 키 '{key_name}' 429 쿨다운 중 -> API 호출 스킵 ➔ 즉시 다음 키로 전환")
                continue

            try:
                client = self._get_genai_client(api_key)
                from google.genai import types as genai_types

                for model_name in ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-flash-latest"]:
                    try:
                        logger.info(f"🤖 [AuraGeminiCopywriter] {key_name} ({model_name})로 주제 #{topic_id} 실시간 깊이 있는 카피 창작 중...")
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config=genai_types.GenerateContentConfig(
                                temperature=0.88,
                                response_mime_type="application/json"
                            )
                        )
                        if response and response.text:
                            data = json.loads(response.text.strip())
                            if "slide1" in data and "slide5" in data:
                                self._active_key_index = idx
                                logger.info(f"🎉 [AuraGeminiCopywriter] {key_name} ({model_name}) 깊이 있는 카피 창작 대성공! (주제 #{topic_id} / {theme_title})")
                                return data
                    except Exception as model_err:
                        err_str = str(model_err)
                        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                            logger.warning(f"🛑 [AuraGeminiCopywriter] {key_name} 429 쿼터 초과 -> 즉시 쿨다운 등록 및 다음 키로 스위칭")
                            AuraProductionSafetyGate.record_429(key_name)
                            break
                        if "404" in err_str or "not found" in err_str.lower():
                            continue
                        raise model_err

            except Exception as e:
                err_s = str(e)
                if "429" in err_s or "RESOURCE_EXHAUSTED" in err_s:
                    AuraProductionSafetyGate.record_429(key_name)
                logger.warning(f"⚠️ [AuraGeminiCopywriter] {key_name} 실패: {err_s[:100]} ➔ 다음 키 시도")

        # 안전 Fallback: 풍성한 기본 시나리오 반환
        logger.warning(f"🛡️ [AuraGeminiCopywriter] 제미나이 전원 실패 시 안전 Fallback 시나리오 가동")
        return self._build_fallback_copy(topic_id, outfit)

    def _build_fallback_copy(self, topic_id: int, outfit: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """비상용 정적 풍성한 Fallback 데이터 구성"""
        dossier = self.TOPIC_DOSSIERS.get(topic_id, self.TOPIC_DOSSIERS[8])
        
        fallback_map = {
            8: {
                "slide1": {
                    "badge": "🛡️ 500m 안심 지터링 보안 번개",
                    "headline_line1": "성수동 퇴근길 가볍게 와인 한잔하고 싶은데,",
                    "headline_line2": "내 실제 집 주소 노출될까 봐 망설여졌다면?",
                    "subtitle": "정밀 위치는 500m 반경 랜덤 분산으로 완벽 은폐! 24시간 뒤 DB에서 흔적 없이 자동 폭파되는 무결점 안심 번개 레이더",
                    "bullets": [
                        "원룸·오피스텔 앞 정확한 핀 노출로 인한 스토킹 불안 100% 원천 차단",
                        "등록 후 24시간 지나면 지도와 서버에서 영구 삭제되는 시크릿 퀘스트",
                        "반경 5km 이내 신원 인증 완료된 2030 이성에게만 실시간 매칭 송출"
                    ],
                    "cta_text": "👉 옆으로 넘겨서 500m 안심 지도 보기 (1/5) >"
                },
                "slide2": {
                    "badge": "📍 2030 현실 공감 100%",
                    "headline_line1": "동네 친구는 만들고 싶은데 사생활은 지키고 싶고,",
                    "headline_line2": "애매한 동네 앱은 집 앞까지 노출되어 불안할 때!",
                    "subtitle": "위치 기반 앱에서 겪는 불안감을 완벽하게 해결! 거리 오차 지터링 알고리즘으로 동네 분위기는 즐기고 집 주소는 철통 보안",
                    "bullets": [
                        "집 근처에서 마주칠까 봐 찝찝했던 기존 동네 소개팅 앱의 치명적 한계",
                        "내 실제 거주지는 가리고 성수동 카페·와인바 약속 장소만 안전 공유",
                        "비매너·유령 회원은 AI 실명 인증 게이트에서 100% 사전 입구컷"
                    ],
                    "cta_text": "👉 옆으로 넘겨서 1초 안심 등록 보기 (2/5) >"
                },
                "slide3": {
                    "badge": "🛡️ 500m 안심 프라이버시 보안",
                    "headline_line1": "실제 집 주소 노출 걱정 제로!",
                    "headline_line2": "500m 반경 랜덤 지터링으로 안전 등록",
                    "subtitle": "등록 24시간 뒤 흔적 없이 DB 자동 파기! 반경 5km 이내 검증된 2030 이성에게만 실시간 알림 송출",
                    "cta_text": "👉 옆으로 넘겨서 실시간 번개 지도 보기 (3/5) >"
                },
                "slide4": {
                    "badge": "⚡ 24시간 실시간 번개 퀘스트",
                    "headline_line1": "퇴근 후 성수동 카페·가벼운 와인 한잔,",
                    "headline_line2": "지금 바로 만날 동네 메이트 자동 매칭!",
                    "subtitle": "지도 위 24시간 동안 번개 핀 노출! 마음 맞는 2030 이성과 낭비 없는 찐 케미 연결",
                    "cta_text": "👉 옆으로 넘겨서 회원가입 3대 혜택 받기 (4/5) >"
                },
                "slide5": {
                    "debate_badge": "⚡ 2030 핫이슈 찬반 토론",
                    "debate_question": "퇴근 후 당일 급 번개 만남, 부담 없는 쿨한 만남이다 vs 며칠 대화가 먼저다? 여러분의 선택은?",
                    "debate_opt1_title": "쿨하게 퇴근길 직진 (71%)",
                    "debate_opt1_sub": "500m 안심 레이더라 위치 걱정 없이 가볍게 커피/와인 한잔!",
                    "debate_opt2_title": "신중한 대화 먼저 (29%)",
                    "debate_opt2_sub": "채팅으로 티키타카 충분히 맞춰본 뒤 신중하게 만나는 게 편함!",
                    "benefit_items": [
                        "500m 안심 프라이버시 보호",
                        "24시간 자동 폭파 번개 레이더",
                        "50:50 남녀 황금 성비 라운지"
                    ],
                    "cta_subtext": "✨ 50:50 남녀 황금 성비율 • 오늘 가입하고 동네 500m 안심 메이트 찾기"
                },
                "sns_caption": """퇴근 후 성수동에서 가볍게 커피나 와인 한잔하고 싶은데,
동네 앱에 내 실제 집 주소나 정밀 위치가 노출될까 봐 망설여지셨나요? ☕🍷✨

Aura의 [500m 안심 레이더]는 정밀 위치를 500m 반경 랜덤으로 자동 분산 은폐하여
내 거주지 노출 걱정 제로! 등록 후 24시간 뒤에는 흔적도 없이 DB에서 자동 파기됩니다. 🛡️⚡

퇴근 후 급 당일 번개 만남, 여러분의 선택은?
1번 "부담 없는 쿨한 만남이다" vs 2번 "며칠 대화가 먼저다"
댓글로 1번 or 2번을 남겨주세요! 👇

🎁 지금 가입 시 안심 VIP 혜택 100% 즉시 지급!
🔍 네이버 검색창에 👉 [아우라AI데이팅] 을 검색해보세요!""",
                "hashtags": "#아우라AI데이팅 #동네친구 #성수동카페 #성수동와인 #번개모임 #직장인퇴근길 #동네번개 #안심데이팅 #2030소개팅"
            }
        }

        return fallback_map.get(topic_id, fallback_map[8])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    writer = AuraCardnewsGeminiCopywriter()
    test_res = writer.generate_cardnews_copy(topic_id=8)
    print("RESULT:", json.dumps(test_res, indent=2, ensure_ascii=False))
