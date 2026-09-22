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

        is_live_trend = seo_brief.get("is_live_trend", False)
        live_stock = seo_brief.get("live_stock", {})

        # ⚡ 1. Cache-First: 일반 주제는 캐시 사용, 실시간 핫 트렌드는 실시간 생성
        cache_file = CACHE_DIR / f"stock_blog_topic_{topic_id:03d}.json"
        if not is_live_trend and cache_file.exists():
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

[3박자 퀀트 글쓰기 절대 원칙]
1. 분량: 한글 공백 포함 2,000자 내외의 완성도 높은 장문 분석 칼럼.
2. 톤앤매너: 전문적, 논리적, 명쾌함, 객관적. 뜬구름 잡는 루머 배제, 팩트와 수치 제시.
3. 3박자 스토리텔링 구성:
   - ① 도입부 (Hook): 오늘 실시간 검색어/외인 수급 집중 팩트 제시 & 뉴스만 보고 추격 매수하는 뇌동매매 위험 경고.
   - ② H2 소제목 1: {subheadings[0] if len(subheadings) > 0 else '실시간 수급 이동과 기업 펀더멘털 팩트체크'}
   - ③ H2 소제목 2: {subheadings[1] if len(subheadings) > 1 else '20일선 지지선·저항선 차트와 적정 밸류에이션 진단'}
   - ④ H2 소제목 3: {subheadings[2] if len(subheadings) > 2 else '리스크 방어: StockMaster 10분 계량 전광판 & -5% 실시간 문자 손절 알림'}
   - ⑤ 결론 (CTA): 10분마다 350개 주도주 체결강도를 스캔하는 'StockMaster AI 전광판'에서 실시간 데이터를 확인하고 안전하게 매매할 것을 권장.
4. 검색어 자연 삽입: {', '.join(seeds)} 키워드를 본문에 자연스럽게 녹여낼 것.
5. 리스크 경고: 모든 투자의 책임은 본인에게 있으며, 분할 매수와 손절 원칙을 항상 환기할 것.

[반환 형식: JSON 포맷 필수]
반드시 마크다운 코드블록(```json ... ```) 안에 유효한 JSON 형식으로만 응답하십시오:
{{
  "title_naver": "{seo_titles[0] if seo_titles else '네이버 스마트블록 검색 1위용 클릭 유도 제목'}",
  "title_tistory": "{seo_titles[1] if len(seo_titles) > 1 else '티스토리 SEO 최적화 전문 정보형 제목'}",
  "title_brunch": "{seo_titles[2] if len(seo_titles) > 2 else '브런치스토리 감성적·통찰력 있는 투자 에세이형 제목'}",
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
- 연계 StockMaster 기능: 10분 계량 전광판 (350개 주도주 실시간 스캔 & -5% 손절 알림)
- 실시간 핫 종목: {live_stock.get('name', '우량주')} ({live_stock.get('sector', '핵심 섹터')})
- SEO 권장 키워드: {', '.join(seeds)}

위 실시간 수급 핫이슈와 퀀트 데이터를 결합하여 투자자들의 뇌동매매를 방지하는 완성도 높은 2,000자 투자 칼럼을 작성해주세요.
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

    def write_captured_article(self, capture_result: Dict[str, Any], article_type: str = "rank1") -> Dict[str, Any]:
        """
        주식 웹앱에서 실시간 캡처한 실제 수치를 주입하여, 대표님의 '성공 블로그 원문(바이블)' 포맷으로 2,000자 칼럼 생성
        article_type: 'rank1' (계량 전광판 1위 주도주 편) 또는 'semiconductor' (반도체 주도주 편)
        """
        metrics = capture_result.get("metrics", {})
        image_path = capture_result.get("image_path", "")

        from google import genai
        from google.genai import types as genai_types

        api_key = get_gemini_key()

        if article_type == "semiconductor":
            # ── [모드 B: 반도체 주도주 편 (삼성전자 vs SK하이닉스)] ──
            samsung = metrics.get("samsung", {})
            hynix = metrics.get("hynix", {})
            s_rank = samsung.get("rank", 3)
            h_rank = hynix.get("rank", 12)
            s_status = samsung.get("status", "🔴 VETO: 현재가")
            h_status = hynix.get("status", "🔴 이격과열 경고 (조기 청산 권고)")
            s_for = samsung.get("foreign_net_buy", "+468.0억원")
            h_for = hynix.get("foreign_net_buy", "-4769.0억원")
            s_blk = samsung.get("block_order_ratio", "71%")
            h_blk = hynix.get("block_order_ratio", "85%")

            system_instruction = f"""
당신은 대한민국 최고의 데이터 기반 퀀트 투자자이자 'StockMaster AI'의 수석 투자 전략가입니다.
시장의 소음과 뇌동매매를 배제하고, 철저히 데이터와 펀더멘털, 수급과 팩터에 기반한 냉철하고 명쾌한 투자 인사이트를 제공합니다.

[대표님 성공 블로그 원문 바이블 스타일 - 필수 준수 원칙]
1. 인사말: "안녕하세요! 스마트한 주식 투자를 위한 AI 퀀트 파트너입니다. 📈✨"로 시작.
2. 뼈 때리는 현실 공감 Hook:
   - "매일 아침 9시 장이 열리면 여러분은 어떤 방식으로 종목을 찾으시나요?"
   - HTS 번쩍이는 급등주 뇌동매매와 찌라시 추격매수 언급.
   - 장 시작 직후 9시~9시 10분은 세력이 개미에게 물량 넘기기 가장 좋은 시간대라 윗꼬리에 물려 고통받는 현실 지적.
   - 감(Feel)과 조급함을 끝내고 실시간 퀀트 데이터와 AI 리스크 검증으로 살아남는 법 제시.
3. 💡 1. 세력의 '가짜 수급'에 속지 않는 법 : 체결강도 & 블록오더(대형체결)
   - 체결강도 100% 이상의 진정성 (비유: 차를 앞으로 밀어붙이는 액셀 페달의 압력)
   - 5천만 원 이상 블록오더 비중 (비유: 차에 실린 거대한 슈퍼 엔진)
4. 🛑 2. 아무리 좋아 보여도 거르는 'VETO (AI 리스크 배제)' 4대 원칙
   - ❌ 이격도 과열 (105% 이상)
   - ❌ 체결 가속도 급락 & 이탈
   - ❌ 외국계 창구의 기습 이탈
   - ❌ 연속 적자 및 신용잔고 과다
5. 📊 3. 10분마다 350개 주도주를 스캔하는 [계량 전광판] 루틴 & 오늘자 반도체 실시간 성적표
   - 09:00 ~ 09:10 : 장 개장 직후 거친 호가 변동성이 가라앉고 진짜 수급 데이터가 쌓이는 시간
   - 09:10 이후 (10분 주기) : 국내 350개 핵심 종목의 실시간 수급·이격도·외국계 순매수 집계 상위 후보군 갱신
   - 09:30 이후 (30분 주기) : Gemini AI가 리스크를 통과한 종목들의 차트 추세와 재무 건전성을 2차 심층 분석하여 최종 리포트 발행
   - [실제 데이터 상세 대입]:
     * 오늘 350개 종목 중 삼성전자는 {s_rank}위({s_status}, 외인 순매수 {s_for}, 블록오더 {s_blk})
     * SK하이닉스는 {h_rank}위({h_status}, 외인 순매수 {h_for}, 블록오더 {h_blk})
     * 두 종목의 순위 격차와 외국계 창구 수급, 블록오더 비중이 왜 이렇게 갈렸는지 명쾌한 이유 설명!
6. 🎯 마무리: "투자는 예측이 아니라 대응과 철저한 리스크 관리입니다"
7. 랜딩 링크 및 무료 체험 CTA 고정 삽입:
   - https://stockmaster-ai.vercel.app/
   - "Stock Master AI - 10분 퀀트 스캔 & 실시간 -5% 손절 알림 (100% 무료 경험)"

[반환 형식: JSON 포맷 필수]
```json
{{
  "title_naver": "삼성전자 vs SK하이닉스, 오늘 350개 종목 중 몇 위일까? 실시간 수급 격차와 AI 리스크 진단",
  "title_tistory": "삼성전자 SK하이닉스 주가 전망: 오늘 10분 계량 전광판 순위와 외인 수급·블록오더 정밀 비교",
  "title_brunch": "거인의 전쟁: 350개 주도주 전광판에서 본 삼성전자와 SK하이닉스의 현주소",
  "body_markdown": "2,000자 내외의 완성형 마크다운 본문",
  "summary": "오늘 350개 종목 중 삼성전자와 SK하이닉스의 10분 계량 전광판 순위 및 외국계 수급 분석",
  "tags": ["삼성전자", "SK하이닉스", "반도체주도주", "AI주식", "퀀트투자", "체결강도", "블록오더", "스톡마스터AI"]
}}
```
"""
            user_prompt = f"위 지침에 따라 오늘자 삼성전자({s_rank}위)와 SK하이닉스({h_rank}위)의 실시간 수급 격차와 퀀트 리스크 진단 칼럼을 작성하세요."

        else:
            # ── [모드 A: 당일 10분 계량 전광판 1위 주도주 편] ──
            s_name = metrics.get("stock_name", "삼성E&A")
            s_code = metrics.get("stock_code", "028050")
            s_sector = metrics.get("sector", "일반서비스")
            s_score = metrics.get("total_score", 140)
            s_strength = metrics.get("chegyul_strength", "120.93%")
            s_accel = metrics.get("chegyul_accel", "+13.4%p")
            s_block = metrics.get("block_order_ratio", "73.1%")
            s_for = metrics.get("foreign_net_buy", "+27억원")
            s_cur = metrics.get("current_price", "45,600원")
            s_tp = metrics.get("swing_tp", "57,160원")
            s_sl = metrics.get("exit_sl", "39,820원")
            s_short = metrics.get("short_ratio", "4.92%")
            s_badge = metrics.get("special_badge", "⚡ 수급 가속 특례")

            system_instruction = f"""
당신은 대한민국 최고의 데이터 기반 퀀트 투자자이자 'StockMaster AI'의 수석 투자 전략가입니다.
시장의 소음과 뇌동매매를 배제하고, 철저히 데이터와 펀더멘털, 수급과 팩터에 기반한 냉철하고 명쾌한 투자 인사이트를 제공합니다.

[대표님 성공 블로그 원문 바이블 스타일 - 필수 준수 원칙]
1. 제목: "장 시작 10분 만에 털리는 개미 vs 세력의 진짜 수급을 발라내는 AI 퀀트 매매법 (오늘 전광판 1위: {s_name})" 스타일.
2. 인사말: "안녕하세요! 스마트한 주식 투자를 위한 AI 퀀트 파트너입니다. 📈✨"로 시작.
3. 뼈 때리는 현실 공감 Hook:
   - "매일 아침 9시 장이 열리면 여러분은 어떤 방식으로 종목을 찾으시나요?"
   - HTS 번쩍이는 급등주 뇌동매매와 찌라시 추격매수 언급.
   - 장 시작 직후 9시~9시 10분은 세력이 개미에게 물량 넘기기 가장 좋은 시간대라 윗꼬리에 물려 고통받는 현실 지적.
   - 감(Feel)과 조급함을 끝내고 실시간 퀀트 데이터와 AI 리스크 검증으로 살아남는 법 제시.
4. 💡 1. 세력의 '가짜 수급'에 속지 않는 법 : 체결강도 & 블록오더(대형체결)
   - 체결강도 100% 이상의 진정성 (비유: 차를 앞으로 밀어붙이는 액셀 페달의 압력)
   - 5천만 원 이상 블록오더 비중 (비유: 차에 실린 거대한 슈퍼 엔진)
   - [실제 1위 수치 인용]: 오늘 1위 종목 {s_name}({s_code})의 체결강도는 {s_strength}, 블록오더 비중은 {s_block}, 체결 가속도는 {s_accel}에 달함!
5. 🛑 2. 아무리 좋아 보여도 거르는 'VETO (AI 리스크 배제)' 4대 원칙
   - ❌ 이격도 과열 (105% 이상)
   - ❌ 체결 가속도 급락 & 이탈
   - ❌ 외국계 창구의 기습 이탈
   - ❌ 연속 적자 및 신용잔고 과다
   - {s_name}는 {s_badge}로 위험을 유예받고 진입 유효 판정을 받은 이유 설명.
6. 📊 3. 10분마다 350개 주도주를 스캔하는 [계량 전광판] 루틴 & ATR 진입/청산 가이드
   - 09:00 ~ 09:10 : 장 개장 직후 거친 호가 변동성이 가라앉고 진짜 수급 데이터가 쌓이는 시간
   - 09:10 이후 (10분 주기) : 국내 350개 핵심 종목 실시간 수급 집계
   - 🎯 ATR 변동성 기준: 현재가 {s_cur} 기준 📉 청산 손절선(Exit SL) {s_sl} vs 📈 스윙 목표선(Swing TP) {s_tp} 명시!
7. 🎯 마무리: "투자는 예측이 아니라 대응과 철저한 리스크 관리입니다"
8. 랜딩 링크 및 무료 체험 CTA 고정 삽입:
   - https://stockmaster-ai.vercel.app/
   - "Stock Master AI - 10분 퀀트 스캔 & 실시간 -5% 손절 알림 (100% 무료 경험)"

[반환 형식: JSON 포맷 필수]
```json
{{
  "title_naver": "장 시작 10분 만에 털리는 개미 vs 세력 수급 발라내는 AI 퀀트 (오늘 전광판 1위: {s_name})",
  "title_tistory": "오늘 350개 주도주 중 1위 찍은 {s_name}: 체결강도 {s_strength}와 블록오더 {s_block}의 비밀",
  "title_brunch": "숫자는 거짓말을 하지 않는다: 10분 퀀트 전광판 1위 {s_name} 심층 해부",
  "body_markdown": "2,000자 내외의 완성형 마크다운 본문",
  "summary": "오늘 10분 계량 전광판 1위 {s_name}의 체결강도 {s_strength}, 블록오더 {s_block}, ATR 목표가 분석",
  "tags": ["{s_name}", "주식투자", "AI종목분석", "체결강도", "블록오더", "스톡마스터AI", "수급분석", "단타매매"]
}}
```
"""
            user_prompt = f"위 지침에 따라 오늘 10분 계량 전광판 1위 종목인 {s_name}({s_code})의 실제 퀀트 수치 기반 전문 칼럼을 작성하세요."

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
                return {
                    "title": data.get("title_naver", f"[StockMaster] {article_type}"),
                    "title_naver": data.get("title_naver", ""),
                    "title_tistory": data.get("title_tistory", ""),
                    "title_brunch": data.get("title_brunch", ""),
                    "body_markdown": data.get("body_markdown", ""),
                    "summary": data.get("summary", ""),
                    "tags": data.get("tags", ["주식투자", "StockMaster"]),
                    "image_path": image_path,
                    "metrics": metrics,
                    "article_type": article_type
                }
            except Exception as e:
                logger.warning(f"⚠️ [StockGeminiWriter] 캡처 칼럼 작성 시도 {attempt+1} 실패 ({e})")
                report_gemini_key_failure(api_key)
                api_key = get_paid_gemini_key()

        # 비상용 기본 리턴
        return {
            "title": f"장 시작 10분 만에 털리는 개미 vs 세력 수급 AI 퀀트",
            "title_naver": f"장 시작 10분 만에 털리는 개미 vs 세력 수급 AI 퀀트 (스톡마스터 AI)",
            "title_tistory": f"오늘 350개 주도주 10분 퀀트 전광판 분석 및 실전 매매 전략",
            "title_brunch": f"투자는 감이 아닌 데이터: 실시간 퀀트와 AI 리스크 검증",
            "body_markdown": "## 실시간 퀀트 데이터 분석\n\nStockMaster AI 전광판 데이터를 기반으로 작성된 분석 리포트입니다.",
            "summary": "실시간 퀀트 계량 지표 기반 투자 분석 칼럼",
            "tags": ["주식투자", "스톡마스터AI"],
            "image_path": image_path,
            "metrics": metrics,
            "article_type": article_type
        }

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
