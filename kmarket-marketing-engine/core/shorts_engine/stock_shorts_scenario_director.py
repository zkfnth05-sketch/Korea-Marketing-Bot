# -*- coding: utf-8 -*-
"""
StockShortsScenarioDirector - 🎬 [StockMaster AI 국내 주식 8대 실시간 숏폼 마스터 시나리오 디렉터]
===================================================================================================
- 국내 주식 100% 독립 전담 (KOSPI/KOSDAQ 350개 우량주 실시간 퀀트)
- 8대 실시간 마스터 라인업 (30초 골든 대본 전량 탑재):
  1) [주제 1] 삼성전자 실시간 4대 모달 퀀트 수급 (30초)
  2) [주제 2] SK하이닉스 실시간 4대 모달 퀀트 수급 (30초)
  3) [주제 3] 뇌동매매 방지! AI 자동 손절매 & 실시간 리스크 가드 (30초)
  4) [주제 4] 당일 10분 계량 전광판 실시간 1위 주도주 발굴 (30초)
  5) [주제 5] KOSPI 시장 종합 스트레스 센터 & 환율/금리 리포트 (30초)
  6) [주제 6] 국내 최초 자기학습 AI 퀀트 비서! Stock Master AI 총괄 소개 (30초)
  7) [주제 7] 외국인/기관 쌍끌이 매수 포착! 스마트머니 추적 레이더 (30초)
  8) [주제 8] 배당주 & 저평가 가치주 발굴! 장기 투자 퀀트 스코어 (30초)
- 공식 검색어 불변: ['스톡마스터 AI'] (띄어쓰기 100% 준수)

[🎯 필수 대본 키 6종 100% 반환 보장]
  · speech_hook       : 3초 오프닝 훅 (시선 강탈 1문장)
  · speech_hook_part1 : 훅 1단 (문제 제기 / 상황 제시)
  · speech_hook_part2 : 훅 2단 (반전 / 해결 예고)
  · speech_app        : 앱 시연 나레이션 (전광판 ➔ 검색 ➔ 4대 모달)
  · speech_cta        : 공식 검색어 유도 CTA ('스톡마스터 AI')
  · full_speech       : 위 5개 파트를 시간 순서대로 결합한 전체 나레이션

[🏆 S2V 골든 모션 규격 100% 통일]
  · 5번 주제 실측 검증 기반 골든 모션 템플릿을 8대 주제 전체에 단일 출처로 적용
  · 손 억제 묘사(subtle hand gestures / gentle nodding 등) 전면 제거
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("StockShortsScenarioDirector")


# ==============================================================================
# 🏆 [5번 골든 규격 검증 완료] 주식 숏폼 S2V 모션 프롬프트 단일 출처(Single Source of Truth)
# ------------------------------------------------------------------------------
# • 5번 주제 실측 렌더링에서 손 제스처가 살아있고 표정/립싱크가 가장 자연스럽게
#   나온 프롬프트 조합을 골든 규격으로 승격하여 8대 주제 전체에 통일 적용.
# • 기존 'subtle hand gestures', 'gentle nodding', 'subtle posture shifts' 등
#   손 움직임을 억제/축소시키던 묘사를 전면 제거 → 손 억제 요소 0%.
# ==============================================================================
GOLDEN_MOTION_STOCK_MALE_HANDS = (
    "speaking clearly with smooth realistic lip sync and articulate mouth motion, "
    "natural masculine hand and upper body gestures while talking, confident and dynamic movement, "
    "sharp intelligent gaze, subtle head nodding, "
    "no phone in hand, trustworthy quant investor motion"
)

GOLDEN_MOTION_STOCK_FEMALE_HANDS = (
    "speaking clearly with smooth realistic lip sync and articulate mouth motion, "
    "natural hand and upper body gestures while talking, friendly and dynamic movement, "
    "professional sharp expression, subtle head tilts and confident nods, "
    "no phone in hand, credible financial expert motion"
)

GENDER_MOTION_GOLDEN = {
    "male": GOLDEN_MOTION_STOCK_MALE_HANDS,
    "female": GOLDEN_MOTION_STOCK_FEMALE_HANDS
}


class StockShortsScenarioDirector:
    """📈 StockMaster AI 국내 주식 8대 실시간 30초 숏폼 시나리오 디렉터"""

    # ==========================================================================
    # 🏆 골든 모션 템플릿 클래스 참조 (외부 모듈에서도 단일 출처로 접근 가능)
    # ==========================================================================
    GOLDEN_MOTION_STOCK_MALE_HANDS = GOLDEN_MOTION_STOCK_MALE_HANDS
    GOLDEN_MOTION_STOCK_FEMALE_HANDS = GOLDEN_MOTION_STOCK_FEMALE_HANDS
    GENDER_MOTION_GOLDEN = GENDER_MOTION_GOLDEN

    # ==========================================================================
    # 🎬 [1~8번] 주제별 30초 골든 대본 전량 레지스트리
    #   · 각 주제는 메타데이터(테마/종목/훅카피/토론질문/연출지시) +
    #     30초 대본 6종(speech_hook / part1 / part2 / app / cta / full_speech)을 100% 보유
    #   · full_speech는 나머지 5개 파트를 시간 순서대로 결합하여 자동 생성 (누락 0% 보장)
    #   · gender / s2v_motion_prompt 는 STOCK_8_TOPIC_PERSONAS 성별 배치와 100% 동기화
    # ==========================================================================
    SCRIPTS_30S = {
        # ----------------------------------------------------------------------
        # [주제 1] 삼성전자 실시간 4대 모달 퀀트 수급  (여성 아나운서)
        # ----------------------------------------------------------------------
        1: {
            "topic_id": 1,
            "theme_name": "삼성전자 실시간 4대 모달 퀀트 수급",
            "theme_code": "samsung_quant_modal",
            "stock_target": "삼성전자",
            "gender": "female",
            "s2v_motion_prompt": GOLDEN_MOTION_STOCK_FEMALE_HANDS,
            "hero_copy": "삼성전자 4대 퀀트 지표 실시간 1초 분석!",
            "debate_question": "삼성전자 지금 구간, 추격 매수 vs 조정 대기?",
            "visual_direction": "전광판 ➔ 삼성전자 검색 ➔ 4대 탭(수급/기술/리스크/기본정보) 스크롤 다운",
            "speech_hook": "삼성전자, 지금 사도 될까요? 3초 만에 판단 끝내드립니다.",
            "speech_hook_part1": "뉴스만 보고 삼성전자에 뛰어들었다가 물린 분들, 정말 많으시죠?",
            "speech_hook_part2": "문제는 수급과 리스크를 따로따로 봐서, 판단이 매번 흔들린다는 겁니다.",
            "speech_app": "스톡마스터 AI에서 삼성전자를 검색하면, 수급·기술·리스크·기본정보 4대 모달이 1초 만에 한 화면에 펼쳐집니다.",
            "speech_cta": "공식 검색어 '스톡마스터 AI', 붙여쓰기로 검색하시면 바로 확인됩니다.",
        },
        # ----------------------------------------------------------------------
        # [주제 2] SK하이닉스 실시간 4대 모달 퀀트 수급  (남성 앵커)
        # ----------------------------------------------------------------------
        2: {
            "topic_id": 2,
            "theme_name": "SK하이닉스 실시간 4대 모달 퀀트 수급",
            "theme_code": "hynix_quant_modal",
            "stock_target": "SK하이닉스",
            "gender": "male",
            "s2v_motion_prompt": GOLDEN_MOTION_STOCK_MALE_HANDS,
            "hero_copy": "SK하이닉스 HBM 퀀트 수급 실시간 1초 분석!",
            "debate_question": "SK하이닉스 HBM 독주 지속 vs 고점 차익 실현?",
            "visual_direction": "전광판 ➔ SK하이닉스 검색 ➔ 4대 탭(수급/기술/리스크/기본정보) 스크롤 다운",
            "speech_hook": "SK하이닉스, HBM 독주 언제까지 갈까요? 숫자로 확인하세요.",
            "speech_hook_part1": "HBM 뉴스가 쏟아질 때마다 고점 논쟁이 반복되고 있습니다.",
            "speech_hook_part2": "감으로 고점을 맞히려 하면, 결국 외국인 수급에 휘둘리게 됩니다.",
            "speech_app": "스톡마스터 AI에서 SK하이닉스를 검색하면, 외국인·기관 수급과 기술적 과열도를 4대 모달로 동시에 보여줍니다.",
            "speech_cta": "공식 검색어 '스톡마스터 AI', 지금 검색해 보세요.",
        },
        # ----------------------------------------------------------------------
        # [주제 3] 뇌동매매 방지! AI 자동 손절매 & 실시간 리스크 가드  (남성 투자자)
        # ----------------------------------------------------------------------
        3: {
            "topic_id": 3,
            "theme_name": "뇌동매매 방지! AI 자동 손절매 & 실시간 리스크 가드",
            "theme_code": "anti_fomo_risk_guard",
            "stock_target": "리스크센터",
            "gender": "male",
            "s2v_motion_prompt": GOLDEN_MOTION_STOCK_MALE_HANDS,
            "hero_copy": "감정 배제! AI 기계적 손절가 & 리스크 가드",
            "debate_question": "급등주 추격 매수 vs AI 리스크 안전 구간 매매?",
            "visual_direction": "전광판 ➔ AI 리스크 센터 ➔ VETO 배제 종목 및 안전 구간 스크롤",
            "speech_hook": "손절 못 해서 계좌가 반토막 난 적 있으시죠?",
            "speech_hook_part1": "급등주를 쫓아 들어가면, 팔 타이밍을 감정이 대신 결정합니다.",
            "speech_hook_part2": "그래서 필요한 건 의지가 아니라, 기계적으로 계산된 손절 기준입니다.",
            "speech_app": "스톡마스터 AI 리스크 센터는 VETO 종목을 자동 배제하고, 안전 구간과 손절가를 실시간으로 표시합니다.",
            "speech_cta": "공식 검색어 '스톡마스터 AI'로 리스크부터 점검하세요.",
        },
        # ----------------------------------------------------------------------
        # [주제 4] 당일 10분 계량 전광판 실시간 1위 주도주 발굴  (여성 투자자)
        # ----------------------------------------------------------------------
        4: {
            "topic_id": 4,
            "theme_name": "당일 10분 계량 전광판 실시간 1위 주도주 발굴",
            "theme_code": "top1_leader_radar",
            "stock_target": "전광판1위",
            "gender": "female",
            "s2v_motion_prompt": GOLDEN_MOTION_STOCK_FEMALE_HANDS,
            "hero_copy": "10분마다 갱신되는 당일 실시간 1위 주도주!",
            "debate_question": "오늘 10분 전광판 1위 주도주, 내일까지 이어질까?",
            "visual_direction": "전광판 상단 ➔ 당일 1위 종목 클릭 ➔ 실시간 퀀트 모달 스크롤",
            "speech_hook": "오늘 시장을 끌고 가는 1등 주도주, 10분마다 새로 뽑힙니다.",
            "speech_hook_part1": "장중에 뒤늦게 뉴스로 종목을 알면, 이미 한참 올라간 뒤입니다.",
            "speech_hook_part2": "속도가 아니라 갱신 주기 싸움이라는 걸 아셔야 합니다.",
            "speech_app": "스톡마스터 AI 10분 계량 전광판은 당일 1위 주도주를 자동 갱신하고, 클릭 한 번에 퀀트 모달로 연결합니다.",
            "speech_cta": "공식 검색어 '스톡마스터 AI', 오늘의 1위를 확인하세요.",
        },
        # ----------------------------------------------------------------------
        # [주제 5] KOSPI 시장 종합 스트레스 센터 & 환율/금리 리포트  (여성 앵커)
        # ----------------------------------------------------------------------
        5: {
            "topic_id": 5,
            "theme_name": "KOSPI 시장 종합 스트레스 센터 & 환율/금리 리포트",
            "theme_code": "macro_stress_report",
            "stock_target": "매크로스트레스",
            "gender": "female",
            "s2v_motion_prompt": GOLDEN_MOTION_STOCK_FEMALE_HANDS,
            "hero_copy": "시장 종합 스트레스 지수 & 4대 계량 매크로 리포트",
            "debate_question": "코스피 현 구간, 반등 랠리 vs 하방 압력?",
            "visual_direction": "메인 상단 글로벌 매크로 ➔ 시장 종합 스트레스 10점 국면 ➔ 4대 지표 스크롤",
            "speech_hook": "코스피가 흔들릴 때, 지금이 기회인지 위기인지 아십니까?",
            "speech_hook_part1": "환율과 금리가 출렁이면 개별 종목 분석은 순식간에 무의미해집니다.",
            "speech_hook_part2": "그래서 시장 전체의 스트레스를 먼저 숫자로 봐야 합니다.",
            "speech_app": "스톡마스터 AI는 시장 종합 스트레스 10점 국면과 환율·금리 4대 지표를 한 화면에 정리해 보여줍니다.",
            "speech_cta": "공식 검색어 '스톡마스터 AI'로 시장 온도부터 확인하세요.",
        },
        # ----------------------------------------------------------------------
        # [주제 6] 국내 최초 자기학습 AI 퀀트 비서! Stock Master AI 총괄 소개  (남성 앵커)
        # ----------------------------------------------------------------------
        6: {
            "topic_id": 6,
            "theme_name": "국내 최초 자기학습 AI 퀀트 비서! Stock Master AI 총괄 소개",
            "theme_code": "stockmaster_official_overview",
            "stock_target": "전광판1위",
            "gender": "male",
            "s2v_motion_prompt": GOLDEN_MOTION_STOCK_MALE_HANDS,
            "hero_copy": "10분 퀀트 스캔 • 30분 Gemini AI • 실시간 손절 알림!",
            "debate_question": "감정 매매 vs 24시간 자기학습 AI 퀀트 비서?",
            "visual_direction": "시장 스트레스 ➔ 10분 계량 전광판 ➔ 1등주 4대 모달 ➔ 실시간 손절 기능",
            "speech_hook": "매일 24시간, 감정 없이 시장을 스캔하는 비서가 있다면?",
            "speech_hook_part1": "사람은 뉴스에 흔들리고, 손절 타이밍을 놓칩니다.",
            "speech_hook_part2": "그래서 자기학습 AI가 10분 단위로 시장을 다시 계산합니다.",
            "speech_app": "스톡마스터 AI는 10분 퀀트 스캔, 30분 Gemini AI 분석, 실시간 손절 알림을 하나로 묶은 국내 최초 자기학습 퀀트 비서입니다.",
            "speech_cta": "공식 검색어 '스톡마스터 AI', 붙여쓰기로 검색하세요.",
        },
        # ----------------------------------------------------------------------
        # [주제 7] 외국인/기관 쌍끌이 매수 포착! 스마트머니 추적 레이더  (남성 투자자)
        # ----------------------------------------------------------------------
        7: {
            "topic_id": 7,
            "theme_name": "외국인/기관 쌍끌이 매수 포착! 스마트머니 추적 레이더",
            "theme_code": "smart_money_radar",
            "stock_target": "수급레이더",
            "gender": "male",
            "s2v_motion_prompt": GOLDEN_MOTION_STOCK_MALE_HANDS,
            "hero_copy": "외국인·기관 쌍끌이 매수 종목 실시간 포착!",
            "debate_question": "외국인 순매수 지속 vs 개인 물량 소화?",
            "visual_direction": "전광판 수급 탭 ➔ 외국인·기관 동반 순매수 필터 ➔ 종목별 수급 모달 스크롤",
            "speech_hook": "외국인과 기관이 동시에 담는 종목, 어떻게 찾으십니까?",
            "speech_hook_part1": "개인 투자자는 수급 데이터를 늘 하루 늦게 확인합니다.",
            "speech_hook_part2": "쌍끌이 매수는 하루만 늦어도 수익 구간이 사라집니다.",
            "speech_app": "스톡마스터 AI 수급 레이더는 외국인·기관 동반 순매수 종목을 실시간으로 걸러내고, 종목별 수급 모달로 바로 연결합니다.",
            "speech_cta": "공식 검색어 '스톡마스터 AI'로 스마트머니를 추적하세요.",
        },
        # ----------------------------------------------------------------------
        # [주제 8] 배당주 & 저평가 가치주 발굴! 장기 투자 퀀트 스코어  (여성 투자자)
        # ----------------------------------------------------------------------
        8: {
            "topic_id": 8,
            "theme_name": "배당주 & 저평가 가치주 발굴! 장기 투자 퀀트 스코어",
            "theme_code": "value_dividend_score",
            "stock_target": "가치주스코어",
            "gender": "female",
            "s2v_motion_prompt": GOLDEN_MOTION_STOCK_FEMALE_HANDS,
            "hero_copy": "배당수익률 & 저평가 퀀트 스코어 한 번에!",
            "debate_question": "배당주 장기 보유 vs 단기 모멘텀 매매?",
            "visual_direction": "전광판 가치주 탭 ➔ 배당수익률·PER·PBR 필터 ➔ 종목별 퀀트 스코어 모달 스크롤",
            "speech_hook": "배당 받으면서 오래 들고 갈 종목, 기준 있으십니까?",
            "speech_hook_part1": "배당수익률만 보고 담으면, 주가 하락으로 배당을 전부 까먹습니다.",
            "speech_hook_part2": "결국 저평가 여부와 재무 건전성을 함께 봐야 합니다.",
            "speech_app": "스톡마스터 AI 가치주 스코어는 배당수익률·PER·PBR·재무 건전성을 합산해 장기 투자 등급을 자동 산출합니다.",
            "speech_cta": "공식 검색어 '스톡마스터 AI', 붙여쓰기로 검색하세요.",
        },
    }

    # ==========================================================================
    # 🔑 [필수 대본 키 6종] get_full_scenario()가 100% 반환해야 하는 절대 키 목록
    # ==========================================================================
    REQUIRED_SPEECH_KEYS = (
        "speech_hook",
        "speech_hook_part1",
        "speech_hook_part2",
        "speech_app",
        "speech_cta",
        "full_speech",
    )

    # ==========================================================================
    # 🛡️ [대본 폴백 문구] 혹시라도 특정 주제에 대본이 비어 있을 때 사용할 안전 기본값
    #   - 절대 빈 문자열/None을 반환하지 않도록 하여 다운스트림 TTS 크래시 0% 보장
    # ==========================================================================
    FALLBACK_SPEECH = {
        "speech_hook": "지금 시장, 감정이 아니라 숫자로 판단하세요.",
        "speech_hook_part1": "뉴스와 소문만으로 매매하면 판단이 매번 흔들립니다.",
        "speech_hook_part2": "그래서 실시간 퀀트 데이터가 필요합니다.",
        "speech_app": "스톡마스터 AI에서 종목을 검색하면 4대 퀀트 모달이 1초 만에 펼쳐집니다.",
        "speech_cta": "공식 검색어 '스톡마스터 AI', 붙여쓰기로 검색하세요.",
    }

    # ==========================================================================
    # 🎙️ [full_speech 조립 순서] 30초 타임라인 고정 순서
    # ==========================================================================
    SPEECH_ORDER = ("speech_hook", "speech_hook_part1", "speech_hook_part2", "speech_app", "speech_cta")

    def _build_full_speech(self, speech: Dict[str, str]) -> str:
        """5개 파트를 30초 타임라인 순서대로 결합하여 full_speech 생성 (누락 파트는 자동 스킵)"""
        parts = []
        for key in self.SPEECH_ORDER:
            text = (speech.get(key) or "").strip()
            if text:
                parts.append(text)
        return " ".join(parts)

    def _resolve_speech(self, script: Dict[str, Any]) -> Dict[str, str]:
        """
        🔑 [필수 대본 키 6종 100% 보장 추출]
        - 스크립트에 대본이 있으면 그대로 사용
        - 없거나 빈 값이면 FALLBACK_SPEECH로 자동 대체 (빈 문자열/None 반환 0% 원천 차단)
        - full_speech는 항상 5개 파트를 결합하여 재생성 (원본 값이 있어도 일관성 우선)
        """
        speech: Dict[str, str] = {}
        for key in self.SPEECH_ORDER:
            value = script.get(key)
            if not value or not str(value).strip():
                value = self.FALLBACK_SPEECH.get(key, "")
                logger.warning(f"⚠️ [대본 폴백] 주제 #{script.get('topic_id')} '{key}' 누락 -> 기본 문구로 대체")
            speech[key] = str(value).strip()

        # full_speech: 원본 값이 유효하면 그대로, 아니면 5개 파트 결합으로 자동 생성
        original_full = script.get("full_speech")
        if original_full and str(original_full).strip():
            speech["full_speech"] = str(original_full).strip()
        else:
            speech["full_speech"] = self._build_full_speech(speech)

        return speech

    def get_full_scenario(self, topic_id: int = 1, gender: Optional[str] = None) -> Dict[str, Any]:
        """
        주제 ID에 해당하는 국내 8대 실시간 시나리오 메타데이터 + 30초 골든 대본 반환 (1~8번 순환)

        🎯 반환 보장:
          - 메타데이터: topic_id, theme_name, theme_code, stock_target, hero_copy,
                        debate_question, visual_direction, search_keyword
          - 성별/모션: gender(effective_gender), s2v_motion_prompt(골든 단일 출처)
          - 필수 대본 키 6종: speech_hook, speech_hook_part1, speech_hook_part2,
                              speech_app, speech_cta, full_speech  (누락 0%)
        """
        total = len(self.SCRIPTS_30S)
        norm_id = ((topic_id - 1) % total) + 1
        s = dict(self.SCRIPTS_30S.get(norm_id, self.SCRIPTS_30S[1]))

        # 🏆 [골든 모션 단일 출처 보장] 성별 정규화 후 골든 프롬프트를 최종 결정
        #    - 공백/대소문자 흔들림을 strip().lower()로 흡수
        #    - 미지의 성별 값은 남성 골든으로 안전 폴백
        effective_gender = (gender or s.get("gender", "male")).strip().lower()
        s2v_motion_prompt = self.GENDER_MOTION_GOLDEN.get(
            effective_gender, GOLDEN_MOTION_STOCK_MALE_HANDS
        )

        visual_dir = {
            "brand_name": "stock",
            "theme_name": s["theme_name"],
            "theme_code": s["theme_code"],
            "top_header": f"스톡마스터 AI • {s['theme_name']}",
            "bottom_step1_title": s["hero_copy"],
            "bottom_step1_sub": "10분 계량 전광판 • 실시간 퀀트 분석",
            "domain_text": "stockmaster-ai.vercel.app",
            "search_keyword": "스톡마스터 AI"
        }

        # 🔑 필수 대본 키 6종 100% 보장 추출
        speech = self._resolve_speech(s)

        result: Dict[str, Any] = {
            "topic_id": norm_id,
            "theme_name": s["theme_name"],
            "theme_code": s["theme_code"],
            "stock_target": s["stock_target"],
            "hero_copy": s["hero_copy"],
            "debate_question": s["debate_question"],
            "visual_direction": visual_dir,
            "search_keyword": "스톡마스터 AI",
            # 🏆 성별 + 골든 모션 프롬프트 반드시 포함 (다운스트림 S2V 렌더러 직결)
            "gender": effective_gender,
            "s2v_motion_prompt": s2v_motion_prompt,
        }

        # 필수 대본 키 6종을 최상위 레벨에 100% 평탄화 반환 (다운스트림 TTS/자막 직결)
        result.update(speech)

        # 🔍 최종 무결성 자체 검증: 6개 키가 모두 비어있지 않은지 확인
        missing = [k for k in self.REQUIRED_SPEECH_KEYS if not result.get(k)]
        if missing:
            logger.error(f"🚨 [대본 무결성 경고] 주제 #{norm_id} 필수 키 누락: {missing}")
        else:
            logger.debug(f"✅ [대본 무결성 합격] 주제 #{norm_id} 필수 대본 키 6종 100% 반환 완료")

        # 🔍 골든 모션 무결성 자체 검증
        if not result.get("s2v_motion_prompt"):
            logger.error(f"🚨 [모션 무결성 경고] 주제 #{norm_id} s2v_motion_prompt 누락")

        return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    director = StockShortsScenarioDirector()
    for tid in range(1, 9):
        scenario = director.get_full_scenario(tid)
        print("=" * 78)
        print(f"[주제 {scenario['topic_id']}] {scenario['theme_name']}")
        print(f"  · 성별      : {scenario['gender']}")
        print(f"  · 모션      : {scenario['s2v_motion_prompt'][:70]}...")
        print(f"  · 훅        : {scenario['speech_hook']}")
        print(f"  · 훅 1단    : {scenario['speech_hook_part1']}")
        print(f"  · 훅 2단    : {scenario['speech_hook_part2']}")
        print(f"  · 앱 시연   : {scenario['speech_app']}")
        print(f"  · CTA       : {scenario['speech_cta']}")
        print(f"  · 전체 대본 : {scenario['full_speech']}")
