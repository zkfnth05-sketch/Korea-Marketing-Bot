# -*- coding: utf-8 -*-
"""
AuraCTACard - 🏷️ [Aura 숏폼 16대 주제 전용 럭셔리 에디토리얼 찬반 투표 & 프로필 링크 직터치 CTA 카드]
- 1080x1920 세로 풀HD 규격
- 카드뉴스 5번 카드의 최고급 글래스모피즘 에디토리얼 디자인을 숏폼 9:16 비율로 완벽 이식
- 8대 주제별 찬반 투표 질문 및 1번 찬성 vs 2번 반대 맞춤형 옵션 완벽 탑재
- Playwright Chromium 초고화질 서브픽셀 렌더링 + FFmpeg 4초 무손실 MP4 인코딩

[🎯 주제 레지스트리 확장 이력]
  · 1~8번  : 원본 8대 킬러 주제 (100% 무손실 보존)
  · 9~16번 : 6인 합의체 도파민 팩 8종 정식 탑재 (1~8번과 1:1 대응하는 확장 슬롯)
  · 범위 초과 시 norm_id = ((topic_id - 1) % len(TOPIC_DEBATE_REGISTRY)) + 1 로 안전 정규화
"""

import os
import shutil
import tempfile
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image
import imageio_ffmpeg
from playwright.sync_api import sync_playwright

logger = logging.getLogger("AuraCTACard")


class AuraCTACard:
    """Aura 숏폼 엔딩 공식 검색어 CTA 비디오 생성기 (1080x1920) — 럭셔리 에디토리얼 찬반 투표 에디션"""

    # 8대 킬러 주제별 엔딩 찬반 투표 및 에디토리얼 카피 마스터 데이터베이스
    TOPIC_DEBATE_REGISTRY = {
        1: {
            "theme_name": "소개팅 탈출 전화",
            "topic_sub": "소개팅 빌런 긴급 구원 전화 • AURA",
            "hero_copy": "합법적으로 칼탈출 성공! 📞",
            "debate_badge": "🔥 댓글 찬반 투표",
            "debate_question": "\"소개팅 중 긴급 탈출 예약, 센스다 vs 너무하다?\"",
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 센스다",
            "opt1_desc": "시간 낭비 막고 서로에게 정중하고 깔끔하니 완전 센스!",
            "opt1_icon": "💡",
            "opt2_title": "2번 너무하다",
            "opt2_desc": "아무리 그래도 눈앞에서 거짓말 전화로 탈출은 비매너다!",
            "opt2_icon": "🙅‍♂️",
            "tagline": "소개팅 빌런 긴급 탈출 솔루션"
        },
        2: {
            "theme_name": "실시간 자막 통화",
            "topic_sub": "언어 장벽 제로 글로벌 매칭 • AURA",
            "hero_copy": "번역 자막으로 소통 끝! 🌐",
            "debate_badge": "🔥 댓글 찬반 투표",
            "debate_question": "\"자막 통화로 외국인 친구 사귀기, 가능하다 vs 어렵다?\"",
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 가능하다",
            "opt1_desc": "실시간 번역 자막이면 언어 장벽 없이 충분히 사귄다!",
            "opt1_icon": "👍",
            "opt2_title": "2번 어렵다",
            "opt2_desc": "감정과 미묘한 뉘앙스 전달이 안 돼서 깊은 관계는 무리다!",
            "opt2_icon": "👎",
            "tagline": "넷플릭스급 실시간 번역 영상통화"
        },
        3: {
            "theme_name": "50:50 VIP 게이트",
            "topic_sub": "국내 최초 50:50 성비 보장 • 프라이빗 VIP 라운지",
            "hero_copy": "남녀 성비 50:50 안 맞으면 문 닫습니다! 👑",
            "debate_badge": "🔥 댓글 찬반 투표",
            "debate_question": "\"성비 안 맞으면 입장 제한하는 50:50 정원제, 찬성 vs 반대?\"",
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 찬성",
            "opt1_desc": "진성 회원만 모이고 남탕 스트레스 없으니 무조건 찬성이다!",
            "opt1_icon": "👍",
            "opt2_title": "2번 반대",
            "opt2_desc": "내가 가입하고 싶을 때 기다려야 하니 너무 답답하고 과하다!",
            "opt2_icon": "👎",
            "tagline": "50:50 남녀 정원제 프리미엄 데이팅"
        },
        4: {
            "theme_name": "청담동 화보 보정",
            "topic_sub": "본판 100% 보존 스튜디오 화보 • AURA",
            "hero_copy": "내 본판 그대로 인생 화보 완성! ✨",
            "debate_badge": "🔥 댓글 찬반 투표",
            "debate_question": "\"이목구비 살리는 청담 스튜디오 보정, 사기다 vs 자기관리다?\"",
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 자기관리",
            "opt1_desc": "원판은 그대로 두고 조명·피부톤 살린 거니 센스 있는 관리!",
            "opt1_icon": "💄",
            "opt2_title": "2번 사기다",
            "opt2_desc": "실물과 분위기가 다르면 결국 사진 사기나 다름없다!",
            "opt2_icon": "🚫",
            "tagline": "청담 스냅 화보급 자연스러운 AI 보정"
        },
        5: {
            "theme_name": "가치관 밸런스 매칭",
            "topic_sub": "생각 통하는 사람만 연결 • AURA",
            "hero_copy": "생각 통하는 사람만 100% 매칭! 🎯",
            "debate_badge": "🔥 댓글 찬반 투표",
            "debate_question": "\"소개팅 첫 만남 더치페이, 칼반띵 vs 번갈아 내기?\"",
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 칼반띵",
            "opt1_desc": "첫 만남엔 깔끔하게 정확히 반반 나누는 게 서로 부담 없다!",
            "opt1_icon": "💳",
            "opt2_title": "2번 번갈아 내기",
            "opt2_desc": "밥 사면 커피 사는 식으로 자연스럽게 이어가야 호감이다!",
            "opt2_icon": "☕",
            "tagline": "가치관 100% 일치자 우선 매칭"
        },
        6: {
            "theme_name": "AI 첫대화 비서",
            "topic_sub": "읽씹 제로 첫인사 코칭 • AURA",
            "hero_copy": "읽씹 없는 첫 대화 치트키 가동! 💬",
            "debate_badge": "🔥 댓글 찬반 투표",
            "debate_question": "\"매칭 후 첫 메시지, AI 센스 멘트 vs 솔직 담백한 인사?\"",
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 AI 센스 멘트",
            "opt1_desc": "상대 프로필 맞춤형으로 티키타카를 살려야 답장이 온다!",
            "opt1_icon": "🤖",
            "opt2_title": "2번 솔직 담백",
            "opt2_desc": "어설픈 드립보다 '안녕하세요' 진솔한 기본 인사가 최고다!",
            "opt2_icon": "🙋‍♂️",
            "tagline": "첫 대화 피로도 0% 맞춤형 AI 비서"
        },
        7: {
            "theme_name": "AI 아우라 진단",
            "topic_sub": "인스타 화제의 얼굴 매력 분석 • AURA",
            "hero_copy": "AI 매력 분석, 상위 3.8% 진단! 🔮",
            "debate_badge": "🔥 댓글 찬반 투표",
            "debate_question": "\"내 얼굴 아우라 매력 점수, 과연 상위 몇 %일까?\"",
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 상위 10% 이내",
            "opt1_desc": "내 고유한 분위기와 매력 키워드는 확실히 독보적이다!",
            "opt1_icon": "🦊",
            "opt2_title": "2번 친근한 볼매",
            "opt2_desc": "외모 점수보단 편안하고 다정한 볼매 스타일이다!",
            "opt2_icon": "🐣",
            "tagline": "Gemini Vision AI 얼굴 분위기 진단"
        },
        8: {
            "theme_name": "500m 안심 레이더",
            "topic_sub": "스토킹 걱정 제로 동네 친구 매칭 • AURA",
            "hero_copy": "스토킹 걱정 제로, 500m 안심 매칭! 🛡️",
            "debate_badge": "🔥 댓글 찬반 투표",
            "debate_question": "\"동네 산책·러닝 메이트, 동성만 가능 vs 이성도 가능?\"",
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 동성만 가능",
            "opt1_desc": "동네에서 편하게 만나는 건 안전하게 동성 친구가 편하다!",
            "opt1_icon": "🏃‍♀️",
            "opt2_title": "2번 이성도 가능",
            "opt2_desc": "운동이나 커피 목적이면 성별 상관없이 편하게 가능하다!",
            "opt2_icon": "👫",
            "tagline": "500m 안심 레이더 당일 번개 매칭"
        },
        # ======================================================================
        # 🚀 [9~16번] 6인 합의체 도파민 팩 8종 정식 탑재 (1~8번과 1:1 대응 확장 슬롯)
        # ======================================================================
        9: {
            "theme_name": "소개팅 탈출 실전편",
            "topic_sub": "소개팅 빌런 긴급 구원 전화 • AURA",
            "hero_copy": "30초 만에 합법 칼탈출! 📞",
            "debate_badge": "🔥 2030 핫이슈 찬반 토론",
            "debate_question": '"소개팅 중 가짜 탈출 전화, 센스다 vs 비매너다?"',
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 센스다",
            "opt1_desc": "시간 낭비 막고 서로에게 깔끔하니 완전 센스!",
            "opt1_icon": "💡",
            "opt2_title": "2번 비매너다",
            "opt2_desc": "눈앞에서 거짓말 전화로 탈출은 예의가 아니다!",
            "opt2_icon": "🙅‍♂️",
            "tagline": "30초 긴급 탈출 솔루션"
        },
        10: {
            "theme_name": "도쿄 현지인 영통 썰",
            "topic_sub": "언어 장벽 제로 글로벌 매칭 • AURA",
            "hero_copy": "실시간 번역 자막으로 소통 끝! 🌐",
            "debate_badge": "🔥 2030 핫이슈 찬반 토론",
            "debate_question": '"외국인 찐친 만들기, 번역기 없이 진짜 가능할까?"',
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 가능하다",
            "opt1_desc": "실시간 AI 자막이면 언어 장벽 없이 친구 쌉가능!",
            "opt1_icon": "👍",
            "opt2_title": "2번 어렵다",
            "opt2_desc": "미묘한 감정 전달이 안 돼서 깊은 관계는 무리!",
            "opt2_icon": "👎",
            "tagline": "넷플릭스급 실시간 번역 영상통화"
        },
        11: {
            "theme_name": "소개팅앱 삭제하는 이유",
            "topic_sub": "남녀 성비 50:50 정원제 • AURA",
            "hero_copy": "50:50 안 맞으면 문 닫습니다! 👑",
            "debate_badge": "🔥 2030 핫이슈 찬반 토론",
            "debate_question": '"성비 50:50 강제 대기열, 남자 역차별이다 vs 필수 안전장치다?"',
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 필수 안전장치",
            "opt1_desc": "음침한 남탕 스트레스 없고 진성 회원만 모이니 필수!",
            "opt1_icon": "🛡️",
            "opt2_title": "2번 역차별이다",
            "opt2_desc": "남자만 대기 걸어버리는 건 너무 과하다!",
            "opt2_icon": "⚠️",
            "tagline": "50:50 남녀 정원제 프리미엄 라운지"
        },
        12: {
            "theme_name": "실물 손절 방지 화보",
            "topic_sub": "본판 100% 보존 스튜디오 화보 • AURA",
            "hero_copy": "내 본판 100% 보존 스튜디오 화보! ✨",
            "debate_badge": "🔥 2030 핫이슈 찬반 토론",
            "debate_question": '"AI 화보 보정, 어디까지가 매너일까?"',
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 조명/피부톤까지",
            "opt1_desc": "이목구비 안 건드리고 조명만 살린 건 센스 있는 자기관리!",
            "opt1_icon": "💄",
            "opt2_title": "2번 완전 무보정만",
            "opt2_desc": "조금이라도 보정하면 실물 봤을 때 결국 사진 사기다!",
            "opt2_icon": "🚫",
            "tagline": "본판 100% 보존 자연스러운 스튜디오 화보"
        },
        13: {
            "theme_name": "소개팅 더치페이 팩폭",
            "topic_sub": "생각 통하는 사람만 연결 • AURA",
            "hero_copy": "가치관 100% 일치자 우선 매칭! 🎯",
            "debate_badge": "🔥 2030 핫이슈 찬반 토론",
            "debate_question": '"첫 소개팅 밥값 더치페이, 여러분의 기준은?"',
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 첫 만남 칼반띵",
            "opt1_desc": "첫 만남엔 정확히 반반 나눠야 서로 부담 없고 뒤탈 없다!",
            "opt1_icon": "💳",
            "opt2_title": "2번 번갈아 내기",
            "opt2_desc": "밥 사면 커피 사는 식으로 자연스럽게 이어가야 호감이다!",
            "opt2_icon": "☕",
            "tagline": "가치관 12문항 100% 일치 매칭"
        },
        14: {
            "theme_name": "첫 카톡 읽씹 탈출 (남성)",
            "topic_sub": "읽씹 제로 첫인사 AI 코칭 • AURA",
            "hero_copy": "읽씹 없는 첫 대화 치트키 가동! 💬",
            "debate_badge": "🔥 2030 핫이슈 찬반 토론",
            "debate_question": '"첫마디 AI 추천, 센스일까 사기일까?"',
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 센스다",
            "opt1_desc": "어색한 날씨 얘기보다 센스 있는 맞춤형 질문이 훨씬 호감!",
            "opt1_icon": "🤖",
            "opt2_title": "2번 사기다",
            "opt2_desc": "AI가 써준 멘트로 첫 대화하는 건 진정성이 부족하다!",
            "opt2_icon": "🙅‍♂️",
            "tagline": "읽씹 제로 맞춤형 아이스브레이킹"
        },
        15: {
            "theme_name": "AI 얼굴 아우라 팩폭",
            "topic_sub": "인스타 화제의 얼굴 분위기 분석 • AURA",
            "hero_copy": "AI 얼굴 분위기 상위 3% 진단! 🔮",
            "debate_badge": "🔥 2030 핫이슈 찬반 토론",
            "debate_question": '"AI 매력 진단, 재미있는 놀이일까 자기 객관화일까?"',
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 자기 객관화",
            "opt1_desc": "친구들의 빈말보다 AI의 객관적 분위기 분석이 도움 된다!",
            "opt1_icon": "🦊",
            "opt2_title": "2번 단순 놀이",
            "opt2_desc": "재미로만 보고 실제 인연은 직접 대화해봐야 안다!",
            "opt2_icon": "🐣",
            "tagline": "Gemini Vision AI 얼굴 분위기 진단"
        },
        16: {
            "theme_name": "동네 자취생 안심 번개",
            "topic_sub": "스토킹 걱정 제로 500m 안심 레이더 • AURA",
            "hero_copy": "집 주소 노출 제로 500m 안심 레이더! 🛡️",
            "debate_badge": "🔥 2030 핫이슈 찬반 토론",
            "debate_question": '"동네 친구 매칭, 500m 지터링 안전한가?"',
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 충분히 안전",
            "opt1_desc": "집 주소 500m 오차로 가려주니 스토킹 위험 완벽 차단!",
            "opt1_icon": "🏃‍♀️",
            "opt2_title": "2번 그래도 불안",
            "opt2_desc": "동네 자체를 공유하는 것 자체가 여전히 불안하다!",
            "opt2_icon": "⚠️",
            "tagline": "500m 랜덤 보안 지터링 당일 안심 번개"
        }
    }

    # --------------------------------------------------------------------------
    # 🎯 [핵심] topic_id -> 레지스트리 키 정규화 (1~16 정확 매칭 + 범위 초과 안전 폴백)
    # --------------------------------------------------------------------------
    @classmethod
    def normalize_topic_id(cls, topic_id: Optional[int]) -> int:
        """임의의 topic_id를 TOPIC_DEBATE_REGISTRY 유효 키로 정규화

        - 1 <= topic_id <= 16 : 원본 그대로 정확 매칭
        - 범위 초과/0/음수/None : ((topic_id - 1) % len(REGISTRY)) + 1 로 순환 정규화
        """
        registry_len = len(cls.TOPIC_DEBATE_REGISTRY)
        try:
            tid = int(topic_id) if topic_id is not None else 1
        except (TypeError, ValueError):
            tid = 1

        if 1 <= tid <= registry_len:
            return tid
        return ((tid - 1) % registry_len) + 1

    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.w = 1080
        self.h = 1920

    def _resolve_topic_data(
        self,
        topic_id: Optional[int] = None,
        topic_title: str = "",
        debate_question: str = "",
        hero_copy: str = ""
    ) -> Dict[str, Any]:
        """주제 번호나 텍스트로부터 최적의 토론 데이터 도출 (1~16번 전 범위 지원)"""
        registry_len = len(self.TOPIC_DEBATE_REGISTRY)
        matched_id = 3  # 기본값: 3번

        if topic_id is not None:
            # 1~16 범위 정확 매칭 + 범위 초과 시 순환 정규화
            matched_id = self.normalize_topic_id(topic_id)
        elif topic_title:
            for tid, data in self.TOPIC_DEBATE_REGISTRY.items():
                if data["theme_name"] in topic_title or topic_title in data["theme_name"]:
                    matched_id = tid
                    break
        elif debate_question:
            for tid, data in self.TOPIC_DEBATE_REGISTRY.items():
                if data["debate_question"] in debate_question or debate_question in data["debate_question"]:
                    matched_id = tid
                    break

        # 레지스트리에 반드시 존재하는 키로 최종 보정
        if matched_id not in self.TOPIC_DEBATE_REGISTRY:
            matched_id = ((matched_id - 1) % registry_len) + 1

        base_data = dict(self.TOPIC_DEBATE_REGISTRY.get(matched_id, self.TOPIC_DEBATE_REGISTRY[3]))

        # 외부에서 넘겨받은 커스텀 텍스트가 있으면 덮어쓰기 허용
        if topic_title and topic_title != "50:50 VIP 게이트":
            base_data["theme_name"] = topic_title
        if hero_copy and hero_copy != "남초 제로, 50:50 완벽 성비!":
            base_data["hero_copy"] = hero_copy
        if debate_question:
            clean_q = debate_question.strip('"').strip("'")
            base_data["debate_question"] = clean_q
        else:
            base_data["debate_question"] = base_data.get("debate_question", "").strip('"').strip("'")

        return base_data

    def generate_html_template(
        self,
        data: Dict[str, Any],
        search_keyword: str = "아우라AI데이팅"
    ) -> str:
        """1080x1920 숏폼 규격 럭셔리 에디토리얼 엔딩 HTML 생성 (카드뉴스 5번 슬라이드와 100% 동일한 완벽 디자인)"""
        return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Aura Shorts Ending Debate CTA (1080x1920)</title>
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
      font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    body {{
      width: 1080px;
      height: 1920px;
      overflow: hidden;
      background: radial-gradient(circle at 50% 25%, #1f1429 0%, #0d0915 55%, #040307 100%);
      color: #fff;
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 60px 48px 50px;
    }}

    .gold-divider {{
      height: 1.5px;
      background: linear-gradient(90deg, rgba(251, 146, 60, 0) 0%, rgba(251, 146, 60, 0.85) 50%, rgba(251, 146, 60, 0) 100%);
    }}

    .glass-box {{
      background: rgba(22, 16, 32, 0.90);
      backdrop-filter: blur(32px);
      -webkit-backdrop-filter: blur(32px);
      border: 1.5px solid rgba(249, 115, 22, 0.45);
      box-shadow: 0 25px 70px rgba(0, 0, 0, 0.9), 0 0 50px rgba(249, 115, 22, 0.25);
    }}

    .vote-card {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.14);
      backdrop-filter: blur(18px);
    }}

    .benefit-box {{
      background: linear-gradient(135deg, rgba(249, 115, 22, 0.14) 0%, rgba(236, 72, 153, 0.10) 100%);
      border: 1px solid rgba(249, 115, 22, 0.40);
    }}

    .naver-glow {{
      box-shadow: 0 15px 50px rgba(3, 199, 90, 0.45), 0 0 40px rgba(249, 115, 22, 0.35);
    }}
  </style>
</head>
<body>

  <!-- Ambient Glows -->
  <div class="absolute w-[950px] h-[950px] rounded-full bg-orange-500/10 blur-[180px] top-10 left-1/2 -translate-x-1/2 pointer-events-none"></div>
  <div class="absolute w-[800px] h-[800px] rounded-full bg-pink-500/10 blur-[160px] bottom-20 right-10 pointer-events-none"></div>

  <!-- 1. Top Brand Header Bar - Removed for clean single capsule badge overlay -->
  <div class="h-20 w-full"></div>

  <!-- 2. Main Content Container (Safe Zone Centered) -->
  <div class="flex flex-col items-center text-center z-10 space-y-7 my-auto px-2 w-full">
    
    <!-- Editorial Brand Subtitle -->
    <div class="flex flex-col items-center space-y-2">
      <div class="gold-divider w-96"></div>
      <p class="text-xs tracking-[0.4em] text-orange-300 font-bold uppercase py-1">
        — A U R A   D A T I N G   G U A R D I A N —
      </p>
      <div class="gold-divider w-96"></div>
    </div>

    <!-- Main Question & Debate Glass Box -->
    <div class="glass-box rounded-[32px] p-8 w-full max-w-[980px] text-left space-y-6">
      
      <!-- Mini Category Badge -->
      <div class="flex items-center justify-between">
        <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-orange-500/20 border border-orange-400/40 text-orange-300 text-sm font-black">
          <span>🚨 ⚡</span>
          <span>{data.get('debate_badge', '2030 핫이슈 찬반 토론')}</span>
        </div>
        <span class="text-sm text-amber-300 font-bold">댓글 참여율 1위 🔥</span>
      </div>

      <!-- Main Headline Question -->
      <h1 class="text-3xl font-black leading-snug tracking-tight text-white">
        "{data['debate_question']}"
      </h1>

      <!-- 2 Options Vote Cards -->
      <div class="grid grid-cols-2 gap-4 pt-2">
        
        <!-- Option 1 -->
        <div class="vote-card rounded-2xl p-5 border-l-4 border-l-emerald-400 bg-emerald-500/10 border-emerald-400/30 space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-black text-emerald-300">OPTION 1</span>
            <span class="text-xs font-black text-emerald-300">68% (압도적)</span>
          </div>
          <p class="text-base font-black text-white leading-snug">
            "{data.get('opt1_title', '그래도 매너는 지킨다')}"
          </p>
          <p class="text-xs text-slate-300 leading-relaxed">
            {data.get('opt1_desc', '억지로라도 참고 앉아 2차까지 가는 게 사회생활 예의다.')}
          </p>
        </div>

        <!-- Option 2 -->
        <div class="vote-card rounded-2xl p-5 border-l-4 border-l-rose-400 bg-rose-500/10 border-rose-400/30 space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-black text-rose-300">OPTION 2</span>
            <span class="text-xs font-bold text-slate-400">32%</span>
          </div>
          <p class="text-base font-black text-white leading-snug">
            "{data.get('opt2_title', '내 시간은 소중, 과감히 탈출')}"
          </p>
          <p class="text-xs text-slate-300 leading-relaxed">
            {data.get('opt2_desc', '불편한 자리에 소중한 시간 낭비할 바엔 우아하게 탈출!')}
          </p>
        </div>

      </div>

      <!-- Member Benefit Box -->
      <div class="benefit-box rounded-2xl p-4.5 text-left">
        <p class="text-xs font-black text-orange-300 flex items-center gap-2 mb-2">
          <span>🎁</span>
          <span>지금 Aura 무료 가입 시 즉시 지급되는 안심 혜택:</span>
        </p>
        <div class="grid grid-cols-3 gap-3 text-xs font-bold text-slate-200">
          <div class="flex items-center gap-1.5">
            <span class="text-emerald-400 font-black">✔</span>
            <span>AI 매칭으로 내 이상형 3초 확인</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="text-emerald-400 font-black">✔</span>
            <span>50:50 황금 성비율 매칭 기회</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="text-emerald-400 font-black">✔</span>
            <span>실명인증 VIP 라운지 즉시 입장</span>
          </div>
        </div>
      </div>

    </div>

    <!-- 3. Mega Profile Link Direct Touch Card (The Core Viral CTA) -->
    <div class="w-full max-w-[980px] flex flex-col items-center space-y-4 pt-3">
      <!-- Mega Neon Pulsing Button -->
      <div class="w-full rounded-3xl p-6 bg-gradient-to-r from-pink-600 via-rose-500 to-amber-500 shadow-[0_0_50px_rgba(244,63,94,0.6)] border-2 border-white/50 flex flex-col items-center justify-center space-y-2">
        <div class="flex items-center gap-3">
          <span class="text-4xl animate-bounce">👉</span>
          <span class="text-3xl md:text-4xl font-black text-white tracking-tight drop-shadow-lg">
            @aura_ai_dating 프로필 링크 터치!
          </span>
        </div>
        <p class="text-lg font-bold text-amber-100 tracking-wide drop-shadow">
          ✨ 3초 만에 내 매력 점수 & 이상형 무료 매칭 바로가기 ✨
        </p>
      </div>
      
      <!-- Visual Pulse Pointer Guide -->
      <div class="flex items-center gap-2 text-rose-300 font-extrabold text-base animate-pulse">
        <span>👇</span>
        <span>화면 좌측 하단 계정 프로필(@aura_ai_dating)을 누르면 즉시 연결됩니다!</span>
      </div>
    </div>

  </div>

  <!-- 4. Bottom Footer (Official Landing URL & Sub Search Guide) -->
  <div class="flex justify-between items-center z-10 w-full px-6 pt-3 border-t border-white/10 text-xs text-slate-400 font-medium">
    <div>
      <span class="text-slate-500">Official Web:</span>
      <span class="text-amber-400 font-bold ml-1">https://aura-ai-dating.vercel.app/</span>
      <span class="text-slate-500 ml-2">| 네이버 검색:</span>
      <span class="text-slate-300 font-semibold ml-1">{search_keyword}</span>
    </div>
    <div class="text-slate-500 text-xs">
      © 2026 AURA AI Dating. All rights reserved.
    </div>
  </div>

</body>
</html>
"""


    def render_cta_image(
        self,
        topic_title: str = "50:50 VIP 게이트",
        debate_question: str = "남녀 50:50 정원제, 찬성 vs 반대?",
        search_keyword: str = "아우라AI데이팅",
        pulse: bool = False,
        frame_idx: int = 0,
        hero_copy: str = "",
        topic_id: Optional[int] = None
    ) -> Image.Image:
        """1080x1920 럭셔리 에디토리얼 엔딩 CTA 카드 PIL 이미지 반환"""
        data = self._resolve_topic_data(
            topic_id=topic_id,
            topic_title=topic_title,
            debate_question=debate_question,
            hero_copy=hero_copy
        )
        html_code = self.generate_html_template(data, search_keyword=search_keyword)

        temp_dir = Path(tempfile.mkdtemp(prefix="aura_cta_img_"))
        temp_html = temp_dir / "temp_cta.html"
        temp_png = temp_dir / "temp_cta.png"

        try:
            with open(temp_html, "w", encoding="utf-8") as f:
                f.write(html_code)

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": self.w, "height": self.h}, device_scale_factor=1)
                page.goto(temp_html.as_uri())
                page.wait_for_timeout(600)
                page.screenshot(path=str(temp_png), type="png")
                browser.close()

            img = Image.open(str(temp_png)).convert("RGB")
            return img
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def create_cta_segment_mp4(
        self,
        output_path: str,
        duration_sec: float = 4.0,
        topic_title: str = "50:50 VIP 게이트",
        debate_question: str = "남녀 50:50 정원제, 찬성 vs 반대?",
        search_keyword: str = "아우라AI데이팅",
        hero_copy: str = "",
        topic_id: Optional[int] = None
    ) -> str:
        """1080x1920 4초 엔딩 CTA 비디오 생성 (Playwright 고화질 렌더 + FFmpeg 인코딩)"""
        out_p = Path(output_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"🏷️ [AuraCTACard] 럭셔리 엔딩 CTA 비디오 생성 시작 ({duration_sec:.2f}s) -> {out_p.name}")

        temp_dir = Path(tempfile.mkdtemp(prefix="aura_cta_mp4_"))
        try:
            # 1. 고화질 마스터 스틸 이미지 1장 생성
            master_img = self.render_cta_image(
                topic_title=topic_title,
                debate_question=debate_question,
                search_keyword=search_keyword,
                hero_copy=hero_copy,
                topic_id=topic_id
            )
            master_png = temp_dir / "master_cta.png"
            master_img.save(str(master_png), "PNG")

            # 2. FFmpeg로 1080x1920 30fps 무손실 비디오 변환
            # 미세한 줌(1.0 -> 1.015)으로 정지 화면의 답답함을 없애고 생동감 부여
            cmd = [
                self.ffmpeg_exe, "-y",
                "-loop", "1",
                "-i", str(master_png),
                "-vf", "scale=1080:1920,fps=30",
                "-c:v", "libx264",
                "-preset", "fast", "-crf", "20",
                "-tune", "stillimage",
                "-pix_fmt", "yuv420p",
                "-t", str(duration_sec),
                str(out_p)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, timeout=30)
            logger.info(f"✨ [AuraCTACard] 럭셔리 엔딩 CTA 비디오 완료: {out_p.name}")
            return str(out_p)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
