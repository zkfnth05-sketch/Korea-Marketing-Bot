# -*- coding: utf-8 -*-
"""
AuraCardnewsPipeline - 💖 [Aura 데이팅 전용 1080x1350 카드뉴스 완전 독립 파이프라인]
==================================================================================
• 앱별 완전 독립 레고 블록 원칙 준수 (brands/aura/ 전담)
• KTRS 파이프라인 아키텍처 100% 이식:
  - 1080x1350 풀블리드 센터 크롭
  - Playwright Chromium 초고해상도 타이포그래피 (골드 헤드라인 + 외곽선 + 스크림)
  - 8대 킬러 주제 6장 기승전결 완결 스토리텔링
  - 실시간 트렌드 키워드 & 찬반 논쟁 고정 댓글 가이드 동시 발행
• 로컬 바탕화면 [C:/Users/zkfnt/Desktop/한국 숏폼_산출물/Aura_Cardnews/] 자동 저장
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image

from .aura_cardnews_producer import AuraCardnewsProducer
from .aura_cardnews_scenario_director import AuraCardnewsScenarioDirector

# UTF-8 콘솔 출력 보장
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("AuraCardnewsPipeline")


class AuraCardnewsPipeline:
    """💖 Aura 데이팅 전용 1080x1350 풀블리드 카드뉴스 통합 파이프라인"""

    OFFICIAL_KEYWORD = "아우라AI데이팅"
    OFFICIAL_URL = "https://aura-ai-dating.vercel.app/"

    def __init__(self):
        self.producer = AuraCardnewsProducer()
        self.scenario_director = AuraCardnewsScenarioDirector()

    def get_available_topics(self) -> List[Dict[str, Any]]:
        """Aura 8대 킬러 주제 목록 반환"""
        return self.scenario_director.get_all_topics()

    def produce(
        self,
        topic_id: int = 1,
        fashion_id: Optional[int] = None,
        copy_data: Optional[Dict[str, Any]] = None,
        master_seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Aura 1개 주제 5장 카드뉴스 풀세트 및 SNS 포스팅 가이드 일괄 생산 (제미나이 100% 자율 집필)
        """
        return self.producer.produce_cardnews(
            topic_id=topic_id,
            fashion_id=fashion_id,
            copy_data=copy_data,
            master_seed=master_seed
        )

    def produce_all_topics(self) -> List[Dict[str, Any]]:
        """Aura 8대 주제 전체 카드뉴스 일괄 일괄 배치 생산"""
        results = []
        topics = self.get_available_topics()
        for t in topics:
            t_id = t["topic_id"]
            logger.info(f"🚀 [AuraCardnewsPipeline] 전체 배치 중 주제 #{t_id} 생산 진행...")
            res = self.produce(topic_id=t_id)
            results.append(res)
        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    print("=" * 70)
    print("💖 Aura 데이팅 1080x1350 카드뉴스 파이프라인 단독 테스트 실행")
    print("=" * 70)

    pipeline = AuraCardnewsPipeline()
    result = pipeline.produce(topic_id=1)

    print("\n✨ 생산 완료 결과:")
    print(f"• 주제: #{result['topic_id']} {result['theme_name']}")
    print(f"• 저장 폴더: {result['output_dir']}")
    print(f"• 슬라이드 파일 수: {result['total_slides']}장")
    print(f"• SNS 가이드 파일: {result['guide_path']}")
