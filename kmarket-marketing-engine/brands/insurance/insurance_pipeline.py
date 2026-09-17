"""
Insurance Master Pipeline (보험 비교 앱 InsureBalance 독립 마케팅 파이프라인)
- 3050 보험 비교 InsureBalance 전용 24대 채널 자율 오케스트레이터
- 블로그, 뽐뿌, 보배드림, 지식iN, 네이버 색인 핑, 카카오 알림톡 100% 무인 실행
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

from brands.insurance.scenarios.prompt_director_insurance import InsurancePromptDirector
from modules.domestic.tistory_engine import TistoryEngine
from modules.domestic.naver_advisor_engine import NaverAdvisorEngine
from modules.domestic.naver_kin_engine import NaverKinEngine
from modules.domestic.ppomppu_engine import PpomppuEngine
from modules.domestic.bobaedream_engine import BobaedreamEngine
from modules.domestic.dcinside_engine import DCInsideEngine
from modules.domestic.kakao_channel_engine import KakaoChannelEngine

logger = logging.getLogger("InsurancePipeline")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class InsurancePipeline:
    BRAND = "insurance"
    NAME = "InsureBalance"

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.director = InsurancePromptDirector()
        self.tistory = TistoryEngine()
        self.advisor = NaverAdvisorEngine()
        self.kin = NaverKinEngine()
        self.ppomppu = PpomppuEngine()
        self.bobaedream = BobaedreamEngine()
        self.dcinside = DCInsideEngine()
        self.kakao = KakaoChannelEngine()

    def run_blog_and_seo_cycle(self) -> Dict[str, Any]:
        """보험 비교 블로그 칼럼 발행 + 네이버 색인 핑"""
        content = self.director.generate_blog_content()
        logger.info(f"🛡️ [보험비교] 블로그 발행 파이프라인 가동: {content['title']}")

        tistory_res = self.tistory.publish_post(
            title=content["title"],
            content_html=content["content_html"],
            tag_list=content["tags"],
            dry_run=self.dry_run
        )
        post_url = tistory_res.get("url", "https://insurebalance.tistory.com/1")
        advisor_res = self.advisor.request_crawl(post_url, dry_run=self.dry_run)

        return {
            "channel": "blog_seo",
            "tistory": tistory_res,
            "advisor": advisor_res
        }

    def run_community_cycle(self) -> Dict[str, Any]:
        """뽐뿌 재테크포럼 + 보배드림 운전자보험 정보글 투고"""
        logger.info("🛡️ [보험비교] 뽐뿌/보배드림 커뮤니티 파이프라인 가동")

        # 1. 뽐뿌 재테크포럼 투고
        pp_post = self.director.generate_ppomppu_post()
        pp_res = self.ppomppu.post_article(
            board_id=pp_post["board"],
            title=pp_post["title"],
            content=pp_post["content"],
            dry_run=self.dry_run
        )

        # 2. 보배드림 교통/사고 포럼 투고
        bb_post = self.director.generate_bobaedream_post()
        bb_res = self.bobaedream.post_article(
            board_code=bb_post["board"],
            title=bb_post["title"],
            content=bb_post["content"],
            dry_run=self.dry_run
        )

        return {
            "channel": "community_infiltrator",
            "ppomppu": pp_res,
            "bobaedream": bb_res
        }

    def run_qa_and_lead_cycle(self) -> Dict[str, Any]:
        """지식iN 실손/암보험 질문 실시간 낚아채기"""
        logger.info("🛡️ [보험비교] 지식iN 실시간 헌팅 파이프라인 가동")
        kin_res = self.kin.submit_answer(
            question_url="https://kin.naver.com/qna/detail.naver?d1id=4&dirId=40103&docId=88888",
            answer_text="실손보험 갱신 시 중복 특약 분리 및 비갱신 전환이 필수적입니다. (인슈어밸런스 비교표 참고)",
            dry_run=self.dry_run
        )
        return {
            "channel": "kin_qa",
            "kin": kin_res
        }

    def run_full_daily_cycle(self) -> Dict[str, Any]:
        """보험 비교 전 채널 일일 무인 종합 가동"""
        logger.info("🚀 ========================================")
        logger.info(f"🚀 [보험비교 InsureBalance] 24대 채널 독립 파이프라인 전체 가동")
        logger.info("🚀 ========================================")

        r1 = self.run_blog_and_seo_cycle()
        r2 = self.run_community_cycle()
        r3 = self.run_qa_and_lead_cycle()

        return {
            "brand": self.BRAND,
            "status": "success",
            "mode": "dry_run" if self.dry_run else "live",
            "results": [r1, r2, r3]
        }


if __name__ == "__main__":
    pipeline = InsurancePipeline(dry_run=True)
    summary = pipeline.run_full_daily_cycle()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
