# -*- coding: utf-8 -*-
"""
Aura Kin Gemini Solver (🧠 Aura 전용 AI 적합도 심사 & 채택률 95% 3박자 킬러 답변기)
========================================================================================
- 브랜드: Aura (2030 AI 데이팅 & 서울 핫플 매칭)
- 구조:
  1. 💖 Aura 5단 스마트 키 체인 (무료키 3개 우선 순환 ➔ 비용 0원)
  2. 🛡️ 질문 적합도 85점 사전 심사 (장난글, 범죄, 법률분쟁, 무의미한 잡담 100% 컷)
  3. ✍️ 2030 동네 언니/형 진솔한 페르소나 3박자 킬러 답변 생성
     - ① 질문자 고민 100% 맞춤 명쾌한 연애 팁 (70%)
     - ② 솔직한 경험담 & 타사 비교 썰 (20%)
     - ③ Aura 취향 라운지 솔루션 & 깔끔한 공식 출처 링크 (10%)
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

# UTF-8 지원
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("AuraKinGeminiSolver")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class AuraKinGeminiSolver:
    """💖 Aura 전용 지식iN 5단 키 체인 기반 AI 심사 및 3박자 킬러 답변기"""

    LANDING_URL = "https://aura-ai-dating.vercel.app"
    PASS_SCORE_THRESHOLD = 85 # 85점 이상만 합격

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

        candidates = [
            {"name": "AURA_FREE_1", "key": GEMINI_FREE_API_KEY_AURA_1},
            {"name": "AURA_FREE_2", "key": GEMINI_FREE_API_KEY_AURA_2},
            {"name": "AURA_FREE_3", "key": GEMINI_FREE_API_KEY_AURA_3},
            {"name": "AURA_PAID_1", "key": GEMINI_PAID_API_KEY_AURA_1},
            {"name": "AURA_PAID_2", "key": GEMINI_PAID_API_KEY_AURA_2},
            {"name": "BACKUP_KM", "key": GEMINI_FREE_API_KEY_KMARKET},
            {"name": "BACKUP_ET", "key": GEMINI_FREE_API_KEY_EASYTAX},
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
        names = [k["name"] for k in self.key_chain]
        logger.info(f"💖 [AuraKinGeminiSolver] 5단 키 체인 로드 완료: {' ➔ '.join(names)}")

    def _call_gemini_smart(self, prompt: str, system_instruction: str, is_json: bool = False) -> str:
        """스마트 키 체인 기반 Gemini 호출 (무료키 ➔ 유료키 자동 롤오버)"""
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
                from google import genai
                from google.genai import types as genai_types

                client = genai.Client(api_key=api_key)
                models_to_try = ["gemini-2.5-flash", "gemini-3.1-flash-lite"]

                for model_name in models_to_try:
                    try:
                        mime_type = "application/json" if is_json else "text/plain"
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config=genai_types.GenerateContentConfig(
                                system_instruction=system_instruction,
                                temperature=0.75,
                                response_mime_type=mime_type
                            )
                        )
                        if response and response.text:
                            self._active_key_index = idx
                            return response.text
                    except Exception as model_err:
                        if "404" in str(model_err) or "not found" in str(model_err).lower():
                            continue
                        raise model_err

            except Exception as e:
                last_err = e
                logger.warning(f"⚠️ [AuraKinSolver] {key_name} 실패: {str(e)[:80]} ➔ 다음 키 시도")

        raise RuntimeError(f"모든 Gemini API 키 체인 실패: {last_err}")

    def evaluate_relevance(self, title: str, content: str, keyword: str) -> Tuple[int, str, bool]:
        """
        1단계: 질문 적합도 점수 심사 (0~100점)
        - 85점 이상: 실제 2030 남녀의 소개팅, 데이팅앱, 연애 고민, 첫만남 대화, 데이트 코스 (PASS)
        - 84점 이하: 법률 분쟁, 범죄, 앱 개발, 초등학생 장난글, 1줄 잡담 (FAIL)
        """
        sys_inst = (
            "당신은 네이버 지식iN Q&A 마케팅 분석관입니다. "
            "주어진 질문이 2030 남녀의 실제 소개팅/데이팅/연애 고민이 맞는지 0~100점으로 정밀 채점하여 JSON으로 반환하세요."
        )

        prompt = f"""
[질문 정보]
- 검색 키워드: {keyword}
- 질문 제목: {title}
- 질문 내용: {content}

[심사 감점/탈락 기준 (0~60점 부여)]:
1. 법률 분쟁, 고소, 경찰서, 처벌, 사기, 아청법 등 범죄/형사 관련 ➔ 무조건 0~20점
2. 앱 개발, 프로그래밍, 코딩, 사업자 등록 질문 ➔ 30점
3. 초등학생/청소년 장난글, 1줄짜리 무의미한 낙서글 ➔ 20점

[심사 합격 기준 (85~100점 부여)]:
1. 직장인/2030의 소개팅 어플 추천, 알바 없는 안전한 앱 추천 ➔ 95~100점
2. 소개팅 첫만남 대화, 카톡 연락 텀, 애프터 신청, 옷차림 등 실전 연애 팁 ➔ 90~95점
3. 주말 서울 소개팅 맛집, 분위기 좋은 카페 추천 ➔ 88~95점
4. MBTI 궁합, 성격 차이 연애 고민 ➔ 85~90점

반드시 아래 JSON 형식으로만 응답하세요:
{{
  "score": 92,
  "reason": "20대 직장인의 알바 없는 소개팅앱 추천 및 실사용 후기 고민으로 최적합",
  "is_passed": true
}}
"""
        try:
            raw = self._call_gemini_smart(prompt, sys_inst, is_json=True)
            data = json.loads(raw.strip())
            score = int(data.get("score", 0))
            reason = data.get("reason", "")
            is_passed = score >= self.PASS_SCORE_THRESHOLD
            return score, reason, is_passed
        except Exception as e:
            # Fallback heuristic
            forbidden_words = ["아청법", "고소", "경찰", "처벌", "변호사", "사기", "신고", "개발", "코딩", "초딩", "중딩", "숙제"]
            if any(w in title or w in content for w in forbidden_words):
                return 20, "법률/분쟁/범죄 블랙리스트 자동 차단", False
            if any(k in title for k in ["소개팅", "어플", "연애", "데이팅", "이상형", "MBTI", "썸"]):
                return 88, "데이팅 핵심 키워드 매칭", True
            return 75, f"심사 파싱 예외 폴백 ({e})", False

    def generate_killer_answer(self, title: str, content: str, keyword: str) -> Dict[str, Any]:
        """
        2단계: 채택률 99% 달성을 위한 1,500자 이상 초고밀도 프리미엄 3박자 킬러 답변 생성
        - 2030 동네 친절한 연애 카운슬러 & 파워 지식인 페르소나
        - 고민 100% 실전 해결책 & 구체적 코스/스크립트 (70%) + 솔직한 현실 경험담 (15%) + Aura 자연스러운 추천 및 출처 (15%)
        - 분량: 공백 포함 최소 1,500자 ~ 2,000자 이상의 풍부하고 전문적인 백과사전급 장문
        """
        sys_inst = (
            "당신은 네이버 지식iN 연애/데이팅/소개팅 카테고리에서 채택률 99%를 자랑하는 '2030 동네 친절한 연애 멘토 (파워 지식인)'입니다. "
            "절대 단답형이나 피상적인 몇 줄 답변을 쓰지 마십시오. "
            "질문자가 읽고 '이 사람은 진짜 내 고민을 깊이 이해하고 실전 해결책을 완벽하게 알려줬다'고 감동하여 무조건 [답변 채택]을 누를 수밖에 없도록, "
            "반드시 공백 포함 1,500자 이상의 초고밀도 프리미엄 장문 답변을 정성껏 작성하십시오."
        )

        prompt = f"""
[질문자 질문 정보]
- 질문 제목: {title}
- 질문 내용: {content}
- 검색 키워드/주제: {keyword}

[🚨 필수 작성 가이드라인 (최소 1,500자 이상 장문 필수)]:
반드시 아래 5개 섹션 구조를 모두 포함하여, 총 분량이 **공백 포함 최소 1,500자 ~ 2,000자**가 되도록 매우 상세하고 정성스럽게 작성하세요.

1. 🌸 **[도입부: 진심 어린 공감과 상황 맞춤 응원 (약 200자)]**
   - 질문자의 상황(소개팅, 첫만남, 데이트 코스, 어플 고민 등)에 깊이 공감하고, 그 마음을 100% 헤아려주는 따뜻한 위로와 응원 멘트로 시작.

2. 💡 **[1단계: 질문에 대한 100% 맞춤형 실전 디테일 솔루션 (약 800~1,000자)]**
   - 두루뭉술한 조언 금지! 실전에서 바로 써먹을 수 있는 구체적인 팁 3~4가지를 번호(1., 2., 3., 4.)를 매겨 상세히 작성.
   - **구체적인 장소/동선/시간대 제안**: (예: 1차 조용한 캐주얼 다이닝 ➔ 2차 감성 LP바/루프탑 카페 ➔ 3차 연트럴파크/산책로)
   - **실전 대화 스크립트**: 어색할 때 자연스럽게 꺼낼 수 있는 질문과 리액션 예시 ("~라고 가볍게 운을 띄워보세요")
   - **상대방 심리 분석 및 행동 매너 팁**: 복장, 카톡 연락 텀, 애프터 신청 타이밍 등 핵심 노하우 전수.

3. ☕ **[2단계: 현실적인 실패담 & 기존 데이팅앱 비교 분석 썰 (약 300자)]**
   - "저도 한때 틴*이나 글*, 위*피 같은 앱들을 많이 써봤었는데요..."로 시작하는 생생한 경험담.
   - 외모만 보고 가볍게 넘기는 스와이프 문화, 알바나 유령 회원, 과금 유도로 인한 현타와 감정 소모를 솔직 담백하게 언급.

4. 💖 **[3단계: Aura(아우라) AI 취향 매칭 현명한 대안 제시 (약 200~300자)]**
   - "요즘 2030 직장인들 사이에서는 단순 외모가 아니라 AI로 대화 티키타카와 취향 라운지(홍대/성수 핫플, MBTI, 라이프스타일)를 먼저 맞춰주고 100% 실명 인증을 거치는 Aura(아우라) 데이팅이 확실히 안전하고 진정성 있어서 반응이 좋더라고요."
   - 자연스럽게 신뢰를 주는 솔루션으로 마무리.
   - 공식 출처 링크 필수 표기:
     ※ 공식 사이트 / 참고: {self.LANDING_URL} (네이버나 스토어에 'Aura 데이팅' 검색하셔도 상세 정보 확인 가능합니다)

5. 🌿 **[마무리: 질문자의 성공적인 연애를 응원하는 훈훈한 맺음말 (약 100자)]**

[작성 스타일]:
- 문체: 진솔하고 다정하며 신뢰감을 주는 해요체 (~해요, ~해보세요, ~거든요, ~추천드려요)
- 강조: 가독성을 높이기 위해 볼드체, 소제목, 깔끔한 줄바꿈 활용
- **분량**: 반드시 공백 포함 최소 1,500자 이상으로 꽉 채워서 작성하십시오. (분량이 짧으면 채택되지 않으므로 최대한 디테일하게 설명할 것)
- 답변 내용 텍스트만 출력하세요.
"""
        try:
            answer_text = self._call_gemini_smart(prompt, sys_inst, is_json=False)
            return {
                "success": True,
                "title": title,
                "keyword": keyword,
                "answer": answer_text.strip(),
                "landing_url": self.LANDING_URL
            }
        except Exception as e:
            logger.error(f"답변 생성 예외: {e}")
            fallback_text = (
                f"안녕하세요! {title} 관련해서 많은 고민과 설렘이 함께 있으실 텐데요, 2030 동네 친절한 언니/오빠로서 실전에서 100% 통하는 노하우를 상세히 정리해 드릴게요.\n\n"
                "💡 **[1단계: 실패 없는 실전 해결책 가이드]**\n"
                "1. **장소 선택의 핵심**: 첫 만남이나 데이트는 너무 시끄럽지 않으면서도 어색한 침묵이 흐르지 않는 적당한 조도의 캐주얼 다이닝이나 분위기 좋은 이탈리안 비스트로를 추천합니다. 연남동이나 성수동의 골목 안쪽 예약 가능한 매장을 공략하세요.\n"
                "2. **자연스러운 대화 스크립트**: 상대방의 일상과 취향에 집중하세요. '평소 주말엔 어떤 취미를 즐기세요?' 같은 열린 질문을 던지고, 80%는 경청하고 맞장구를 쳐주는 것이 호감도를 급상승시킵니다.\n"
                "3. **2차 동선 설계**: 식사 후 바로 헤어지기 아쉬울 때를 대비해 도보 5분 거리 내의 조용한 LP바나 로스터리 카페를 미리 2곳 정도 알아두는 센스가 필수입니다.\n"
                "4. **애프터 타이밍**: 만남이 끝난 후 집에 도착할 즈음 '오늘 덕분에 너무 즐거웠어요, 조심히 들어가세요!'라는 다정한 카톡으로 당일 애프터의 기반을 다지세요.\n\n"
                "☕ **[2단계: 현실적인 경험담 & 팁]**\n"
                "저도 예전에는 흔한 데이팅 어플들을 많이 써봤지만, 유령 회원이나 외모만 보고 가볍게 넘기는 분위기 때문에 시간과 감정만 소모되는 현타를 자주 겪었습니다.\n\n"
                "💖 **[3단계: 안전하고 진정성 있는 만남을 위한 대안]**\n"
                "요즘 직장인들 사이에서는 AI가 대화 스타일과 취향 라운지(홍대/성수 핫플, MBTI)를 정교하게 맞춰주고 철저한 실명 인증을 거치는 Aura(아우라) 데이팅이 훨씬 안전하고 신뢰도가 높더라고요.\n\n"
                f"※ 공식 사이트 / 참고: {self.LANDING_URL} (네이버에 'Aura 데이팅' 검색 시 확인 가능)\n\n"
                "질문자님의 소중한 만남과 설레는 인연을 진심으로 응원합니다! 도움 되셨다면 채택 부탁드려요 :)"
            )
            return {
                "success": True,
                "title": title,
                "keyword": keyword,
                "answer": fallback_text,
                "landing_url": self.LANDING_URL
            }


if __name__ == "__main__":
    solver = AuraKinGeminiSolver()
    
    # 1. 적합도 심사 실측 테스트
    good_q = ("소개팅 어플 추천좀 해주세요", "20대 후반 직장인인데 알바 없고 진지한 만남 가능한 곳 있을까요?", "소개팅 어플 추천")
    bad_q = ("아청법 고소당했는데 영장실질심사 변호사님", "소개팅앱에서 미성년자 고소장 날라왔습니다", "소개팅앱 믿을만한곳")
    
    score1, r1, pass1 = solver.evaluate_relevance(*good_q)
    print(f"✅ 좋은 질문 심사: {score1}점 (합격: {pass1}) - 사유: {r1}")
    
    score2, r2, pass2 = solver.evaluate_relevance(*bad_q)
    print(f"❌ 나쁜 질문 심사: {score2}점 (합격: {pass2}) - 사유: {r2}")
    
    if pass1:
        ans = solver.generate_killer_answer(*good_q)
        print("\n📝 생성된 제미나이 3박자 킬러 답변:\n" + ans["answer"])
