# -*- coding: utf-8 -*-
"""
Stock Kin Gemini Solver (📈 Stock Master 지식iN 3박자 킬러 답변 생성기)
========================================================================
- 브랜드: Stock Master (2030 AI 주식 퀀트 & 종목 진단)
- 목적: 채택률 99% 달성을 위한 초고밀도 1,500자 이상 장문 킬러 답변 생성
- 핵심 원칙:
  1. 10년 차 여의도 수석 증권 분석관 페르소나
  2. 펀더멘털/차트/수급 100% 명쾌 분석 (70%) + 현실적인 실패담 & 리딩방 경고 (15%) + Stock Master AI 솔루션 및 공식 안내 (15%)
  3. 외부 URL 링크 완전 배제, 검색 유도형 브랜드 안내 카드 적용
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Tuple
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("StockKinGeminiSolver")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class StockKinGeminiSolver:
    """📈 Stock Master 전용 지식iN 5단 키 체인 기반 AI 심사 및 3박자 킬러 답변기"""

    LANDING_URL = "https://stockmaster-ai.vercel.app/"
    PASS_SCORE_THRESHOLD = 85  # 85점 이상만 합격

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
            {"name": "STOCK_FREE_1", "key": GEMINI_FREE_API_KEY_AURA_1},
            {"name": "STOCK_FREE_2", "key": GEMINI_FREE_API_KEY_AURA_2},
            {"name": "STOCK_FREE_3", "key": GEMINI_FREE_API_KEY_AURA_3},
            {"name": "STOCK_PAID_1", "key": GEMINI_PAID_API_KEY_AURA_1},
            {"name": "STOCK_PAID_2", "key": GEMINI_PAID_API_KEY_AURA_2},
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
        logger.info(f"📈 [StockKinGeminiSolver] 5단 키 체인 로드 완료: {' ➔ '.join(names)}")

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
                logger.warning(f"⚠️ [StockKinSolver] {key_name} 실패: {str(e)[:80]} ➔ 다음 키 시도")

        raise RuntimeError(f"모든 Gemini API 키 체인 실패: {last_err}")

    def evaluate_relevance(self, title: str, content: str, keyword: str) -> Tuple[int, str, bool]:
        """
        1단계: 질문 적합도 점수 심사 (0~100점)
        - 85점 이상: 국내/미국 주식 종목 분석, ETF 추천, 배당주, 차트 매매 기법, AI 주식 분석, 초보 주식 입문 고민 (PASS)
        - 84점 이하: 불법 대출, 리딩방 홍보, 보이스피싱, 코인 다단계, 단순 한 줄 낙서 (FAIL)
        """
        sys_inst = (
            "당신은 네이버 지식iN 주식/증권/투자 카테고리 마케팅 분석관입니다. "
            "주어진 질문이 개인 투자자의 실제 주식/ETF/투자 고민이 맞는지 0~100점으로 정밀 채점하여 JSON으로 반환하세요."
        )

        prompt = f"""
[질문 정보]
- 검색 키워드: {keyword}
- 질문 제목: {title}
- 질문 내용: {content}

[심사 감점/탈락 기준 (0~60점 부여)]:
1. 불법 대출, 작업 대출, 사채, 보이스피싱, 불법 자금 세탁 ➔ 무조건 0~20점
2. 불법 리딩방 초대 링크 홍보, 유료 카톡방 모집 글 ➔ 20점
3. 코인 다단계, 바카라, 사설 도박 관련 ➔ 10점
4. 해외 주식/해외 선물 전용 질문 ➔ 50점 (국내 주식 서비스 목적과 불일치)
5. 1줄짜리 무의미한 낙서글 또는 날짜만 적힌 글 ➔ 20점

[심사 합격 기준 (85~100점 부여)]:
1. 삼성전자, SK하이닉스, 현대차, 2차전지, 바이오 등 대한민국 코스피/코스닥 대장주 주가 전망 및 매수 타이밍 고민 ➔ 95~100점
2. 국내 저PBR 밸류업, AI 반도체 소부장, 원전/방산 등 실시간 국내 테마주 분석 ➔ 92~98점
3. 국내 주식 차트 분석(이동평균선, 지지/저항, 골든크로스) 및 단타/스윙 매매 전략 ➔ 90~95점
4. AI 주식 프로그램, 퀀트 종목 추천, 국내 종목 진단 도구 추천 ➔ 90~98점
5. 국내 고배당주 순위, ISA/연금저축 절세 및 주린이의 안전한 주식 투자 시작법 ➔ 88~95점

반드시 아래 JSON 형식으로만 응답하세요:
{{
  "score": 95,
  "reason": "국내 반도체 대장주 주가 전망 및 분할매수 타이밍에 대한 실제 개인 투자자 고민으로 최적합",
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
            forbidden_words = ["대출", "사채", "바카라", "도박", "토토", "리딩방가입", "카톡방링크", "선물거래불법"]
            if any(w in title or w in content for w in forbidden_words):
                return 20, "불법/스팸 블랙리스트 자동 차단", False
            if any(k in title for k in ["주식", "주가", "전망", "ETF", "배당", "매수", "차트", "AI", "수급"]):
                return 90, "주식 핵심 키워드 매칭", True
            return 75, f"심사 파싱 예외 폴백 ({e})", False

    def generate_killer_answer(self, title: str, content: str, keyword: str) -> Dict[str, Any]:
        """
        2단계: 채택률 99% 달성을 위한 1,500자 이상 초고밀도 프리미엄 3박자 킬러 답변 생성
        - 10년 차 여의도 수석 증권 분석관 페르소나
        - 펀더멘털/차트/수급 100% 명쾌 분석 (70%) + 현실적인 실패담 & 리딩방 경고 (15%) + Stock Master AI 솔루션 및 출처 (15%)
        - 분량: 공백 포함 최소 1,500자 ~ 3,000자 이상의 백과사전급 장문
        """
        sys_inst = (
            "당신은 네이버 지식iN 주식/증권/투자 카테고리에서 채택률 99%를 자랑하는 '10년 차 여의도 수석 증권 분석관 (파워 지식인)'입니다. "
            "절대 동문서답을 하거나 피상적인 복붙 답변을 쓰지 마십시오. "
            "질문자가 무엇을 물어보았는지(질문 내용)를 가장 먼저 정밀하게 읽고, "
            "질문자가 물어본 바로 그 의문에 대해 가장 정확하고 명쾌한 1:1 직답(결론, 수치, 기준, Yes/No)을 첫머리에 시원하게 내려준 뒤, "
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

1. 📊 **[도입부: 질문에 대한 100% 명쾌한 1:1 직답 & 핵심 결론 (약 200~300자)]**
   - ⚠️ **[최우선 절대 원칙]**: 질문자가 물어본 핵심 질문(예: 배당 주기, 매달 나오는지 여부, 매매 타이밍, 목표가, 세금 등)에 대해 **첫 문장부터 명확한 결론(Yes/No, 정확한 주기/수치, 이유)을 1:1 직답**으로 즉시 답해줄 것!
   - 딴소리나 일반론으로 말을 돌리지 말고, 질문자의 질문을 완벽히 이해했음을 보여주며 시원하게 결론부터 제시.

2. 💡 **[1단계: 질문 주제에 100% 밀착된 심층 실전 분석 & 가이드 (약 1,000자)]**
   - 질문자가 물어본 종목 및 구체적인 상황(배당, 실적, 차트, 매수/매도, 절세 계좌 등)에 정확히 맞춘 실전 퀀트 솔루션 제공:
     * 배당 질문인 경우: 배당락일, 배당 기준일, 분기별 배당 일정, 세금(배당소득세 15.4%), 실제 100주 기준 예상 수령액 계산법 등.
     * 종목 전망 질문인 경우: 펀더멘털 실적, 글로벌 업황 사이클, 이동평균선(20일/60일선) 지지/저항, 외국인/기관 수급 분석.
     * 매매 전략: 리스크 관리를 위한 분할 매수/매도 원칙 제시.

3. ☕ **[2단계: 현실적인 실패담 & 감정 매매의 위험성 경고 (약 300자)]**
   - "저 역시 10년 전 초보 시절 남의 말이나 확인되지 않은 소문에 뇌동매매했다가 큰 손실을 본 뼈아픈 경험이 있습니다..."로 시작하는 현실적인 썰.
   - 근거 없는 소문이나 조급한 감정 매매를 멈추고, 객관적인 데이터와 원칙을 세워야 하는 이유를 진솔하게 경고.

4. 📈 **[3단계: 네이버 직접 검색 유도 & Stock Master AI 퀀트 진단실 안내 (약 200~300자)]**
   - 질문자가 해당 종목(또는 보유 종목)의 배당 일정, 실시간 외국인/기관 수급, AI 매매 타이밍을 직접 무료로 점검해 볼 수 있도록 네이버 검색을 자연스럽게 유도:
     "질문자님께서 보유하신 종목의 정확한 배당 기준일과 외국인·기관 수급 유입 현황은 네이버에서 **'스톡마스터 AI'**를 검색하시면 공식 퀀트 진단실에서 무료로 실시간 종목 진단을 받아보실 수 있습니다."
   - 하단에 아래 공식 안내 박스를 반드시 포함:
[📊 Stock Master AI 퀀트 진단실 안내]
• 국내 코스피·코스닥 우량주 외국인/기관 수급 분석
• 보유 종목 AI 매매 타이밍 & 퀀트 지표 무료 진단
👉 네이버에서 '스톡마스터 AI' 검색 → 공식 AI 퀀트 진단실 바로가기

5. 🌿 **[마무리: 성공 투자를 응원하는 훈훈한 맺음말 및 채택 요청 (약 100자)]**

[작성 스타일]:
- 문체: 전문적이면서도 알기 쉽고 신뢰감 있는 정중한 해요체 (~합니다, ~추천드립니다, ~확인하세요)
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
            logger.error(f"Stock 답변 생성 예외: {e}")
            fallback_text = (
                f"안녕하세요! {title} 관련해서 고민이 많으실 텐데, 10년 차 금융 분석관으로서 실전 투자 가이드를 정리해 드립니다.\n\n"
                "💡 **[1단계: 실패 없는 실전 주식 투자 분석]**\n"
                "1. **재무 건전성 및 밸류에이션 점검**: 해당 종목의 최근 영업이익 성장세와 PER/PBR 지표를 동종 업계 평균과 비교하여 저평가 여부를 먼저 확인하세요.\n"
                "2. **차트 지지선과 이동평균선**: 20일선 및 60일 중기 이동평균선 지지 여부를 체크하고, 거래량이 동반된 양봉이 출현할 때 분할 매수로 접근하는 것이 안전합니다.\n"
                "3. **3분할 분산 투자 원칙**: 원금의 30%, 30%, 40%로 나누어 하락 시 비중을 조절하는 철저한 리스크 관리가 필수입니다.\n\n"
                "☕ **[2단계: 현실적인 투자 팁]**\n"
                "근거 없는 소문이나 리딩방에 의존하는 투자는 원금 손실의 지름길입니다. 감정을 배제한 데이터 투자가 핵심입니다.\n\n"
                "📈 **[3단계: AI 퀀트 데이터 기반 투자]**\n"
                "최근에는 AI 빅데이터로 실시간 외국인/기관 수급과 퀀트 모멘텀을 분석해주는 Stock Master AI를 활용해 객관적인 진단을 내리는 투자자들이 늘고 있습니다.\n\n"
                "[📊 Stock Master AI 퀀트 진단실 안내]\n"
                "• 국내 코스피·코스닥 우량주 외국인/기관 수급 분석\n"
                "• 보유 종목 AI 매매 타이밍 & 퀀트 지표 무료 진단\n"
                "👉 네이버에서 '스톡마스터 AI' 검색 → 공식 AI 퀀트 진단실 바로가기\n\n"
                "성공적인 투자를 진심으로 응원합니다! 도움 되셨다면 채택 부탁드립니다 :)"
            )
            return {
                "success": True,
                "title": title,
                "keyword": keyword,
                "answer": fallback_text,
                "landing_url": self.LANDING_URL
            }


if __name__ == "__main__":
    solver = StockKinGeminiSolver()
    q = ("삼성전자 주가 전망 매수해도 될까요?", "지금 7만원대인데 장기투자로 분할매수 어떻게 해야 할지 궁금합니다.", "삼성전자 주가 전망")
    score, r, passed = solver.evaluate_relevance(*q)
    print(f"📊 심사 결과: {score}점 ({r}) - 합격: {passed}")
