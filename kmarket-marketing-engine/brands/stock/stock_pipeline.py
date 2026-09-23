"""
Stock Master Pipeline (주식 AI 앱 Stock Master AI 독립 마케팅 파이프라인)
- 전연령 주식 투자자 타겟 Stock Master AI 전용 24대 채널 자율 오케스트레이터
- 장전 08:30 시황, 블로그, 디시 주갤, 뽐뿌 증권, 텔레그램/카카오 알림톡 100% 무인 실행
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

from brands.stock.scenarios.prompt_director_stock import StockPromptDirector
from brands.stock.stock_kin_pipeline import StockKinPipeline
from modules.domestic.tistory_engine import TistoryEngine
from modules.domestic.naver_advisor_engine import NaverAdvisorEngine
from modules.domestic.dcinside_engine import DCInsideEngine
from modules.domestic.ppomppu_engine import PpomppuEngine
from modules.domestic.kakao_channel_engine import KakaoChannelEngine

logger = logging.getLogger("StockPipeline")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class StockPipeline:
    BRAND = "stock"
    NAME = "Stock Master AI"

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.director = StockPromptDirector()
        self.tistory = TistoryEngine()
        self.advisor = NaverAdvisorEngine()
        self.kin = StockKinPipeline()
        self.dcinside = DCInsideEngine()
        self.ppomppu = PpomppuEngine()
        self.kakao = KakaoChannelEngine()

    def run_blog_and_seo_cycle(self) -> Dict[str, Any]:
        """주식 심층 종목 분석 블로그 칼럼 발행 + 네이버 색인 핑"""
        content = self.director.generate_blog_content()
        logger.info(f"📈 [주식AI] 블로그 발행 파이프라인 가동: {content['title']}")

        tistory_res = self.tistory.publish_post(
            title=content["title"],
            content_html=content["content_html"],
            tag_list=content["tags"],
            dry_run=self.dry_run
        )
        post_url = tistory_res.get("url", "https://stockmaster.tistory.com/1")
        advisor_res = self.advisor.request_crawl(post_url, dry_run=self.dry_run)

        return {
            "channel": "blog_seo",
            "tistory": tistory_res,
            "advisor": advisor_res
        }

    def run_community_cycle(self) -> Dict[str, Any]:
        """디시 주식갤러리 + 뽐뿌 증권포럼 시황 투고"""
        logger.info("📈 [주식AI] 커뮤니티 시황 파이프라인 가동")

        # 1. 디시인사이드 주식갤러리 투고
        dc_post = self.director.generate_dcinside_post()
        dc_res = self.dcinside.post_article(
            gallery_id=dc_post["gallery"],
            title=dc_post["title"],
            content_html=dc_post["content"],
            dry_run=self.dry_run
        )

        # 2. 뽐뿌 증권포럼 투고
        pp_post = self.director.generate_ppomppu_post()
        pp_res = self.ppomppu.post_article(
            board_id=pp_post["board"],
            title=pp_post["title"],
            content=pp_post["content"],
            dry_run=self.dry_run
        )

        return {
            "channel": "community_market",
            "dcinside": dc_res,
            "ppomppu": pp_res
        }

    def run_premarket_briefing_cycle(self) -> Dict[str, Any]:
        """장전 08:30 카카오 알림톡 및 VIP 시황 푸시"""
        logger.info("📈 [주식AI] 장전 08:30 알림톡 브리핑 파이프라인 가동")
        kakao_res = self.kakao.send_alimtalk(
            receiver_phone="010-0000-0000",
            template_code="STK_PRE_01",
            title="[Stock Master AI] 장전 핵심 유망 섹터 브리핑",
            message="회원님, 오늘 장 시작 전 외인 순매수 집중 예상 섹터와 핵심 공략주가 업데이트되었습니다.",
            dry_run=self.dry_run
        )
        return {
            "channel": "premarket_push",
            "kakao": kakao_res
        }

    def run_qa_and_lead_cycle(self) -> Dict[str, Any]:
        """지식iN 주식 질문 실시간 낚아채기 (Stock Master 전용 독립 레고 블록)"""
        logger.info("📈 [주식AI] 지식iN 실시간 헌팅 파이프라인 가동")
        kin_res = self.kin.run_catch_cycle(max_catch=1, dry_run=self.dry_run)
        return {
            "channel": "kin_qa",
            "kin": kin_res
        }

    def run_full_daily_cycle(self) -> Dict[str, Any]:
        """주식 AI 전 채널 일일 무인 종합 가동"""
        logger.info("🚀 ========================================")
        logger.info(f"🚀 [주식 AI Stock Master] 24대 채널 독립 파이프라인 전체 가동")
        logger.info("🚀 ========================================")

        r1 = self.run_blog_and_seo_cycle()
        r2 = self.run_community_cycle()
        r3 = self.run_premarket_briefing_cycle()
        r4 = self.run_qa_and_lead_cycle()

        return {
            "brand": self.BRAND,
            "status": "success",
            "mode": "dry_run" if self.dry_run else "live",
            "results": [r1, r2, r3, r4]
        }


if __name__ == "__main__":
    pipeline = StockPipeline(dry_run=True)
    summary = pipeline.run_full_daily_cycle()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
