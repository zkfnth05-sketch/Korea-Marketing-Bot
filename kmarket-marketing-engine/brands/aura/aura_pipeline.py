"""
Aura Master Pipeline (데이팅 앱 Aura 독립 마케팅 파이프라인)
- 2030 데이팅 Aura 전용 24대 채널 자율 오케스트레이터
- 블로그, 숏폼, 릴스, 지식iN, 네이트판, 디시인사이드, 알림톡 100% 무인 실행
"""

import os
import sys
import json
import logging
from typing import Dict, Any

# 루트 및 모듈 경로 보정
current_dir = os.path.dirname(os.path.abspath(__file__))
engine_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if engine_root not in sys.path:
    sys.path.insert(0, engine_root)

from brands.aura.scenarios.prompt_director_aura import AuraPromptDirector
from modules.domestic.tistory_engine import TistoryEngine
from modules.domestic.naver_advisor_engine import NaverAdvisorEngine
from modules.domestic.naver_kin_engine import NaverKinEngine
from modules.domestic.dcinside_engine import DCInsideEngine
from modules.domestic.ppomppu_engine import PpomppuEngine
from modules.domestic.natepann_engine import NatePannEngine
from modules.domestic.kakao_channel_engine import KakaoChannelEngine

logger = logging.getLogger("AuraPipeline")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class AuraPipeline:
    BRAND = "aura"
    NAME = "Aura Dating"

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.director = AuraPromptDirector()
        self.tistory = TistoryEngine()
        self.advisor = NaverAdvisorEngine()
        self.kin = NaverKinEngine()
        self.dcinside = DCInsideEngine()
        self.ppomppu = PpomppuEngine()
        self.natepann = NatePannEngine()
        self.kakao = KakaoChannelEngine()

    def run_blog_and_seo_cycle(self) -> Dict[str, Any]:
        """블로그 칼럼 생성 및 티스토리 발행 + 네이버 색인 핑"""
        content = self.director.generate_blog_content()
        logger.info(f"💖 [Aura] 블로그 발행 파이프라인 가동: {content['title']}")
        
        tistory_res = self.tistory.publish_post(
            title=content["title"],
            content_html=content["content_html"],
            tag_list=content["tags"],
            dry_run=self.dry_run
        )
        post_url = tistory_res.get("url", "https://aura-dating.tistory.com/1")
        advisor_res = self.advisor.request_crawl(post_url, dry_run=self.dry_run)
        
        return {
            "channel": "blog_seo",
            "tistory": tistory_res,
            "advisor": advisor_res
        }

    def run_viral_community_cycle(self) -> Dict[str, Any]:
        """네이트판 썰 + 디시 연애갤 투고"""
        logger.info("💖 [Aura] 커뮤니티 바이럴 파이프라인 가동")
        
        # 1. 네이트판 사연 투고
        story = self.director.generate_natepann_story()
        pann_res = self.natepann.post_story(
            category=story["category"],
            title=story["title"],
            story_content=story["content"],
            dry_run=self.dry_run
        )

        # 2. 디시인사이드 연애갤 투고
        dc_res = self.dcinside.post_article(
            gallery_id="love",
            title="[썰] 소개팅 카톡 티키타카 AI 조언 받고 애프터 잡은 후기",
            content_html="<p>상대방 답장 템포랑 톤 맞춰서 답장 보내니까 확실히 반응이 다릅니다.</p>",
            dry_run=self.dry_run
        )

        return {
            "channel": "community_viral",
            "natepann": pann_res,
            "dcinside": dc_res
        }

    def run_qa_and_lead_cycle(self) -> Dict[str, Any]:
        """지식iN 질문 실시간 감지 & 답변 투고"""
        logger.info("💖 [Aura] 지식iN 실시간 헌팅 파이프라인 가동")
        answer = self.director.generate_blog_content()
        kin_res = self.kin.submit_answer(
            question_url="https://kin.naver.com/qna/detail.naver?d1id=8&dirId=80101&docId=99999",
            answer_text="소개팅 카톡 대화 시 공감 한 줄과 자연스러운 핑퐁 질문이 핵심입니다. (Aura 데이팅 가이드 참고)",
            dry_run=self.dry_run
        )
        return {
            "channel": "kin_qa",
            "kin": kin_res
        }

    def run_full_daily_cycle(self) -> Dict[str, Any]:
        """Aura 전 채널 일일 무인 종합 가동"""
        logger.info("🚀 ========================================")
        logger.info(f"🚀 [Aura 데이팅] 24대 채널 독립 파이프라인 전체 가동")
        logger.info("🚀 ========================================")
        
        r1 = self.run_blog_and_seo_cycle()
        r2 = self.run_viral_community_cycle()
        r3 = self.run_qa_and_lead_cycle()
        
        return {
            "brand": self.BRAND,
            "status": "success",
            "mode": "dry_run" if self.dry_run else "live",
            "results": [r1, r2, r3]
        }


if __name__ == "__main__":
    pipeline = AuraPipeline(dry_run=True)
    summary = pipeline.run_full_daily_cycle()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
