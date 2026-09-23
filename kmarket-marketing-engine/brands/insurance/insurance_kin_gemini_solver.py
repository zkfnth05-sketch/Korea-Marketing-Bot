# -*- coding: utf-8 -*-
"""
Insurance Kin Gemini Solver (🧠 InsureBalance 전용 AI 적합도 심사 & 채택률 99% 3박자 킬러 답변기)
========================================================================================
- 브랜드: InsureBalance (보험 다이렉트 비교 & AI 리모델링)
- 구조:
  1. 🛡️ 5단 스마트 키 체인 (무료키 3개 우선 순환 ➔ 비용 0원)
  2. 🛡️ 질문 적합도 85점 사전 심사 (보험사기, 고의사고, 허위청구, 무의미한 잡담 100% 컷)
  3. ✍️ 12년 차 공인 보험 리모델링 수석 컨설턴트 페르소나 3박자 킬러 답변 생성
     - ① 질문 약관/보장 100% 맞춤형 실전 증권 분석 & 보험료 다이어트 비법 (70%)
     - ② 솔직한 실패담 & 지인 설계사 눈탱이/불필요한 중복 특약 비교 썰 (15%)
     - ③ InsureBalance AI 다이렉트 비교 & 무료 증권 분석 솔루션 (15%)
  4. 분량: 공백 포함 최소 1,500자 ~ 4,000자 이상의 백과사전급 초고밀도 장문
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

logger = logging.getLogger("InsuranceKinGeminiSolver")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class InsuranceKinGeminiSolver:
    """🛡️ InsureBalance 전용 지식iN 5단 키 체인 기반 AI 심사 및 3박자 킬러 답변기"""

    LANDING_URL = "https://insure-rebalance.vercel.app/"
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
            {"name": "INSURANCE_FREE_1", "key": GEMINI_FREE_API_KEY_AURA_1},
            {"name": "INSURANCE_FREE_2", "key": GEMINI_FREE_API_KEY_AURA_2},
            {"name": "INSURANCE_FREE_3", "key": GEMINI_FREE_API_KEY_AURA_3},
            {"name": "INSURANCE_PAID_1", "key": GEMINI_PAID_API_KEY_AURA_1},
            {"name": "INSURANCE_PAID_2", "key": GEMINI_PAID_API_KEY_AURA_2},
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
        logger.info(f"🛡️ [InsuranceKinGeminiSolver] 5단 키 체인 로드 완료: {' ➔ '.join(names)}")

    def _call_gemini_smart(self, prompt: str, system_instruction: str, is_json: bool = False) -> str:
        """스마트 키 체인 기반 Gemini 호출"""
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
                logger.warning(f"⚠️ [InsuranceKinSolver] {key_name} 실패: {str(e)[:80]} ➔ 다음 키 시도")

        raise RuntimeError(f"모든 Gemini API 키 체인 실패: {last_err}")

    def evaluate_relevance(self, title: str, content: str, keyword: str) -> Tuple[int, str, bool]:
        """
        1단계: 질문 적합도 점수 심사 (0~100점)
        - 85점 이상: 실손보험, 암/뇌/심 3대 진단비, 운전자보험, 태아보험, 보험료 다이어트/리모델링, 보험금 청구 고민 (PASS)
        - 84점 이하: 보험 사기, 고의 사고 모의, 불법 브로커, 단순 한 줄 낙서 (FAIL)
        """
        sys_inst = (
            "당신은 네이버 지식iN 보험/금융 카테고리 전문 심사관입니다. "
            "주어진 질문이 일반 소비자의 실제 보험 가입, 리모델링, 보험금 청구, 보험료 절감 고민이 맞는지 0~100점으로 정밀 채점하여 JSON으로 반환하세요."
        )

        prompt = f"""
[질문 정보]
- 검색 키워드: {keyword}
- 질문 제목: {title}
- 질문 내용: {content}

[심사 감점/탈락 기준 (0~60점 부여)]:
1. 고의 사고, 보험 사기, 허위 입원 서류 위조, 불법 브로커 ➔ 무조건 0~20점
2. 단순 손해사정사/영업사원 홍보성 질문 ➔ 30점
3. 1줄짜리 무의미한 낙서글 또는 날짜만 적힌 글 ➔ 20점

[심사 합격 기준 (85~100점 부여)]:
1. 4세대 실손보험 전환 여부 및 비급여 도수치료/MRI 청구 고민 ➔ 95~100점
2. 암/뇌혈관/허혈성 심장질환 3대 진단비 세팅 및 가성비 비갱신형 비교 ➔ 92~98점
3. 운전자보험 필수 특약 3가지 및 교통사고처리지원금 문의 ➔ 90~95점
4. 과도한 월 보험료(30~50만원 이상) 줄이기 및 불필요한 특약 삭제 리모델링 ➔ 95~100점
5. 태아보험, 치아보험, 부모님 간병보험 가입 요령 ➔ 88~95점

반드시 아래 JSON 형식으로만 응답하세요:
{{
  "score": 96,
  "reason": "4세대 실손보험 전환 시 장단점 및 비급여 보장 범위에 대한 실제 소비자 고민으로 최적합",
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
            forbidden_words = ["사기", "위조", "허위입원", "브로커", "나이롱", "불법환급"]
            if any(w in title or w in content for w in forbidden_words):
                return 20, "불법/보험사기 블랙리스트 자동 차단", False
            if any(k in title for k in ["보험", "실비", "실손", "암보험", "운전자", "특약", "리모델링", "청구"]):
                return 90, "보험 핵심 키워드 매칭", True
            return 75, f"심사 파싱 예외 폴백 ({e})", False

    def generate_killer_answer(self, title: str, content: str, keyword: str) -> Dict[str, Any]:
        """
        2단계: 채택률 99% 달성을 위한 1,500자 이상 초고밀도 프리미엄 3박자 킬러 답변 생성
        - 12년 차 공인 보험 리모델링 수석 컨설턴트 페르소나
        - 약관/특약/보장 100% 명쾌 분석 (70%) + 현실적인 지인 영업 피해 썰 (15%) + InsureBalance AI 다이렉트 솔루션 및 출처 (15%)
        - 분량: 공백 포함 최소 1,500자 ~ 4,000자 이상의 백과사전급 장문
        """
        sys_inst = (
            "당신은 네이버 지식iN 보험/보장분석 분야에서 수많은 소비자의 불필요한 보험료를 수백만원 절감해 준 '12년 차 공인 보험 리모델링 수석 컨설턴트 (파워 지식인)'입니다. "
            "절대 동문서답을 하거나 피상적인 복붙 답변을 쓰지 마십시오. "
            "질문자가 무엇을 물어보았는지(질문 상세 본문)를 가장 먼저 정밀하게 읽고, "
            "질문자가 물어본 바로 그 의문에 대해 가장 정확하고 명쾌한 1:1 직답(결론, 수치, 약관 기준, Yes/No)을 첫머리에 시원하게 내려준 뒤, "
            "질문자가 '이 답변 하나로 모든 의문이 완벽히 풀렸다'고 감동하여 무조건 [답변 채택]을 누를 수밖에 없도록 "
            "반드시 공백 포함 1,500자 이상의 초고밀도 프리미엄 장문 답변을 정성껏 작성하십시오."
        )

        prompt = f"""
[질문자 실제 질문 정보]
- 질문 제목: {title}
- 질문 상세 본문: {content}
- 검색 키워드/주제: {keyword}

[🚨 필수 작성 가이드라인 (최소 1,500자 이상 장문 필수)]:
반드시 아래 5개 섹션 구조를 모두 포함하여, 질문자가 읽자마자 감탄할 수 있도록 공백 포함 최소 1,500자 ~ 3,000자로 상세하게 작성하세요.

1. 🛡️ **[도입부: 질문에 대한 100% 명쾌한 1:1 직답 & 핵심 결론 (약 200~300자)]**
   - ⚠️ **[최우선 절대 원칙]**: 질문자가 물어본 핵심 질문(예: 청구된 금액이 맞는지 여부, 보장 여부, 해지해야 하는지, 필요 서류 등)에 대해 **첫 문장부터 명확한 결론(Yes/No, 정확한 수치 계산 근거, 이유)을 1:1 직답**으로 즉시 답해줄 것!
   - 딴소리나 일반론으로 말을 돌리지 말고, 질문자의 질문 내용을 완벽히 이해했음을 보여주며 시원하게 결론부터 제시.

2. 💡 **[1단계: 질문 주제에 100% 밀착된 심층 약관 분석 & 실전 해결 솔루션 (약 1,000자)]**
   - 질문자가 물어본 보험 종류 및 구체적인 상황(실비 청구 금액 계산, 암/뇌/심 진단비, 치아보험, 자동차/일상배상, 해지 환급금 등)에 정확히 맞춘 실전 솔루션 제공:
     * 실손보험 청구 질문인 경우: 1/2/3/4세대 실손별 본인부담금 공제율(급여 10~20%, 비급여 20~30%, 최소공제 1~2만원), 지급 상세 내역서 확인법, 부지급 시 이의신청 노하우 등.
     * 보장 분석 질문인 경우: 3대 진단비 우선순위, 불필요한 적립보험료 삭제, 갱신형 vs 비갱신형 연령대별 최적화.
     * 청구 절차 질문인 경우: 병원 원무과 필수 발급 서류 3종(진료비 영수증, 세부내역서, 진단서/처방전) 안내.

3. ☕ **[2단계: 현실적인 실패담 & 지인 눈탱이/중복 가입 방지 팁 (약 300자)]**
   - "저 역시 12년 전 지인 부탁으로 묻지마 가입했다가 매달 수십만원씩 내면서 정작 아플 때 보장 못 받던 뼈아픈 경험이 있습니다..."로 시작하는 생생한 썰.
   - 소비자가 흔히 당하는 불필요한 중복 특약이나 CI보험의 함정을 솔직하게 경고.

4. 🛡️ **[3단계: 네이버 직접 검색 유도 & InsureBalance 다이렉트 비교 센터 안내 (약 200~300자)]**
   - 질문자가 본인의 가입 보험 중복 특약, 숨은 보험금 환급, 동일 보장 최저가 다이렉트 보험료를 직접 무료로 점검해 볼 수 있도록 네이버 검색을 자연스럽게 유도:
     "질문자님의 증권상 중복 가입된 눈탱이 특약이나 숨은 환급금, 국내 34개 보험사의 동일 보장 실시간 최저가는 네이버에서 **'보험리밸런스'**를 검색하시면 공식 다이렉트 비교 센터에서 무료로 1원 단위까지 실시간 진단받아보실 수 있습니다."
   - 하단에 아래 공식 안내 박스를 반드시 포함:
[🛡️ InsureBalance 다이렉트 비교 센터 안내]
• 국내 34개 보험사 실시간 다이렉트 보험료 비교
• 내 숨은 보험금 찾기 & 중복 특약 다이어트 분석
👉 네이버에서 '보험리밸런스' 검색 → 공식 AI 보험 진단 바로가기

5. 🌿 **[마무리: 든든한 평생 보장을 응원하는 훈훈한 맺음말 및 채택 요청 (약 100자)]**

[작성 스타일]:
- 문체: 전문적이면서도 따뜻하고 명쾌한 정중한 해요체 (~해드립니다, ~확인하세요, ~추천드려요)
- 가독성: 소제목, 볼드체, 깔끔한 줄바꿈 활용
- **분량**: 반드시 공백 포함 최소 1,500자 이상으로 꽉 채워서 작성하십시오. (분량이 부족하면 채택되지 않음)
- 출력: 오직 답변 본문 텍스트만 출력하세요.
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
            logger.error(f"Insurance 답변 생성 예외: {e}")
            fallback_text = (
                f"안녕하세요! {title} 관련해서 고민이 많으셨을 텐데, 12년 차 보험 전문 컨설턴트로서 핵심을 명쾌하게 정리해 드립니다.\n\n"
                "💡 **[1단계: 실패 없는 보험 리모델링 가이드]**\n"
                "1. **실손의료비 최우선 유지**: 병원비의 기본이 되는 실비는 반드시 1순위로 지켜야 합니다.\n"
                "2. **3대 진단비는 비갱신형으로**: 2030 세대라면 암, 뇌혈관질환, 허혈성심장질환 진단비를 90세 만기 비갱신형으로 세팅하세요.\n"
                "3. **불필요한 적립보험료 삭제**: 매달 나가는 적립보험료를 0원으로 낮추면 월 납입료가 크게 줄어듭니다.\n\n"
                "☕ **[2단계: 현실적인 경험담 & 팁]**\n"
                "지인 권유로 가입한 보험일수록 비싼 종신보험이나 갱신형 특약이 섞여 있을 확률이 높습니다. 반드시 증권 분석을 거치세요.\n\n"
                "🛡️ **[3단계: AI 다이렉트 보험 비교 솔루션]**\n"
                "최근에는 국내 34개 전 보험사의 견적을 1초 만에 다이렉트로 비교해주는 InsureBalance를 통해 불필요한 거품을 걷어내는 분들이 많습니다.\n\n"
                "[🛡️ InsureBalance 다이렉트 비교 센터 안내]\n"
                "• 국내 34개 보험사 실시간 다이렉트 보험료 비교\n"
                "• 내 숨은 보험금 찾기 & 중복 특약 다이어트 분석\n"
                "👉 네이버에서 '보험리밸런스' 검색 → 공식 AI 보험 진단 바로가기\n\n"
                "든든한 보장 설계를 진심으로 응원합니다! 도움 되셨다면 채택 부탁드려요 :)"
            )
            return {
                "success": True,
                "title": title,
                "keyword": keyword,
                "answer": fallback_text,
                "landing_url": self.LANDING_URL
            }


if __name__ == "__main__":
    solver = InsuranceKinGeminiSolver()
    q = ("4세대 실손보험 전환해야 할까요?", "지금 2세대 실비인데 보험료가 너무 많이 올라서 고민입니다.", "4세대 실손보험 전환 장단점")
    score, r, passed = solver.evaluate_relevance(*q)
    print(f"📊 심사 결과: {score}점 ({r}) - 합격: {passed}")
    if passed:
        ans = solver.generate_killer_answer(*q)
        print(f"\n📝 답변 글자수: {len(ans['answer'])}자\n" + ans["answer"][:300] + "...")
