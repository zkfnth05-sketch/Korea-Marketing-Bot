"""
Aura Scenario & Prompt Director (데이팅 앱 Aura 전용 프롬프트 디렉터)
- C:\\Users\\zkfnt\\Desktop\\aura-main 소스 기반
  (aura-charm-report-flow, chat-reply-flow, daily-balance-game-flow)
- 2030 청년/싱글 타겟 감성 숏폼 대본, 4장 카드뉴스 카피, 지식iN 답변, 네이트판 썰, 네이버 블로그 SEO 원고 자동 생성
"""

import random
from typing import Dict, Any, List

try:
    from brands.aura.aura_blog_engine import AuraBlogEngine
    aura_blog_engine = AuraBlogEngine()
except Exception:
    aura_blog_engine = None


class AuraPromptDirector:
    BRAND_NAME = "Aura (아우라)"
    LANDING_URL = "https://aura-ai-dating.vercel.app/lounge"

    THEMES = [
        "ai_charm_report",      # AI 얼굴/성격 매력도 분석
        "chat_assistant",       # 소개팅 카톡 대화 안 끊기는 치트키
        "daily_balance_game",   # 2030 연애 가치관 밸런스 게임
        "weekend_date_course"   # 주말 AI 맞춤 데이트 코스
    ]

    @classmethod
    def generate_blog_content(cls, topic_id: Any = None) -> Dict[str, Any]:
        """100대 주제 + 3중 가드레일 실시간 키워드 결합 SEO 칼럼 원고 생성"""
        if aura_blog_engine:
            pkg = aura_blog_engine.build_article_package(topic_id=topic_id)
            return {
                "title": pkg["title"],
                "content_html": pkg["content_html"],
                "image_path": pkg.get("image_path", ""),
                "image_url": pkg.get("image_url", ""),
                "tags": pkg["tags"],
                "category": pkg["category"],
                "seed_topic": pkg["seed_topic"],
                "seo_brief": pkg["seo_brief"]
            }

        # Fallback
        titles = [
            "2026 소개팅 첫 카톡 읽씹 피하는 AI 대화 치트키 3가지",
            "내 얼굴과 성격의 진짜 매력 점수는? AI 매력도 분석 리포트 후기",
            "MBTI별 최악의 소개팅 대화법 vs 100% 애프터 부르는 화법 비교",
            "이번 주말 어디 갈까? 성향별 맞춤 AI 데이트 코스 추천"
        ]
        title = random.choice(titles)
        content_html = """
        <h2>소개팅 첫인상을 결정짓는 3초의 법칙</h2>
        <p>안녕하세요! 2030 연애 트렌드 가이드입니다. 많은 분들이 소개팅에서 '첫 카톡'을 보낼 때 지나치게 긴장하거나 어색한 질문을 던져 대화가 끊기는 경험을 합니다.</p>
        <hr/>
        <h3>1. 질문만 던지지 말고 '공감 + 질문'의 핑퐁 구조를 만들어라</h3>
        <p>상대방이 "주말에 카페 갔어요"라고 답했을 때, "어디 카페요?"라고 단답 질문을 던지기보다는 "오 주말에 카페 여유 너무 좋죠! 평소에 디저트 좋아하세요?"처럼 공감 한 스푼을 얹는 것이 핵심입니다.</p>
        <h3>2. 유령회원 제로! 남녀 50:50 황금 성비 AI 소개팅 Aura</h3>
        <p>남초 어플의 읽씹과 허위 프로필에 지치셨나요? Aura(아우라)는 1:1 남녀 50:50 성비 보장과 AI 매력 분석을 통해 진짜 인연을 안전하게 연결해 드립니다.</p>
        <hr/>
        <div style="margin-top:20px; padding:15px; background:linear-gradient(135deg, #FFF1F2 0%, #FDF2F8 100%); border:1px solid #FECDD3; border-radius:10px; color:#4C0519;">
          <strong>💑 [Aura Dating] 유령회원 ZERO! 남녀 50:50 황금 성비 보장 매칭</strong><br/>
          성비 불균형 없는 진짜 1:1 AI 소개팅을 지금 무료로 경험해보세요.<br/>
          <a href="{cls.LANDING_URL}" target="_blank" style="color:#DB2777; font-weight:bold;">👉 Aura 50:50 성비 매칭 바로가기: {cls.LANDING_URL}</a>
        </div>
        """
        return {
            "title": title,
            "content_html": content_html,
            "tags": ["소개팅어플", "50:50성비", "연애팁", "소개팅대화법", "Aura", "AI소개팅"]
        }

    @classmethod
    def generate_shorts_script(cls) -> Dict[str, str]:
        """유튜브/틱톡/릴스/클립용 숏폼 스크립트 생성"""
        scripts = [
            {
                "hook": "소개팅에서 이 카톡 보내면 99% 읽씹 당합니다.",
                "body": "절대 '오늘 뭐하세요?' 하나만 띡 보내지 마세요. 상대방 인스타나 프로필 취향을 딱 하나 짚어서 가벼운 질문을 던져보세요. AI 아우라가 알려주는 대화 치트키, 지금 프로필 링크에서 확인!",
                "cta": "댓글에 링크 확인하고 내 매력 리포트 무료로 받아보세요."
            },
            {
                "hook": "AI가 평가해 준 내 얼굴 매력 점수가 충격적인 이유...",
                "body": "친구가 추천해 줘서 아우라 AI 매력 리포트 돌려봤는데, 내가 몰랐던 내 눈매 장점이랑 추천 헤어스타일까지 다 짚어주네요. 2030 싱글 필독!",
                "cta": "프로필 링크에서 3초 만에 무료 진단 받기."
            }
        ]
        return random.choice(scripts)

    @classmethod
    def generate_natepann_story(cls) -> Dict[str, str]:
        """네이트판 톡커들의선택 사연 썰 원고 생성"""
        return {
            "category": "love_talk",
            "title": "소개팅 매번 삼프터 실패하던 20대 후반, AI 대화 코치 조언받고 연애 시작한 썰",
            "content": (
                "안녕하세요. 28살 흔남 직장인입니다.\n\n"
                "항상 소개팅 나가면 밥 잘 먹고 분위기 좋았는데도 카톡에서 티키타카가 안 돼서 "
                "항상 애프터 거절당하기 일쑤였습니다.\n"
                "친구가 아우라 앱에 있는 AI 답장 추천이랑 매력 리포트 한번 써보라고 해서 "
                "반신반의하며 상대방 카톡 톤에 맞춰 조언받은 대로 답장을 보냈는데...\n"
                "상대방 반응이 확 달라지더니 이번 주말에 먼저 삼프터 신청받았습니다 ㅠㅠ\n"
                "혹시 저처럼 카톡 대화 막막하신 분들은 객관적인 피드백 꼭 받아보세요. 진짜 강추합니다."
            )
        }


if __name__ == "__main__":
    director = AuraPromptDirector()
    blog = director.generate_blog_content()
    print("Aura 블로그 제목:", blog["title"])
    shorts = director.generate_shorts_script()
    print("Aura 숏폼 후킹:", shorts["hook"])
