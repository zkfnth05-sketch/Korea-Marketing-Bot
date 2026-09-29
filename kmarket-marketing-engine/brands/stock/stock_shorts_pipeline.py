# -*- coding: utf-8 -*-
"""
StockShortsPipeline - 🎬 [StockMaster AI 전용 숏폼 동영상 생산 공장]
======================================================================
- 1단계: '입을 부드럽게 다문 신뢰감 있는 스마트 개미 투자자' 2040 인물 마스터컷 생성 (Wan 2.1 T2I)
- 2단계: 객관적 AI 퀀트 전광판 & 수급/밸류에이션/리스크 가드 시연 비디오 (12초)
- 3단계: Google Gemini 2.5 Flash TTS 초실사 음성 합성 (Aoede)
- 4단계: Wan 2.2 S2V 10초 원테이크 립싱크 (5s+5s xfade) 모션 렌더링
- 5단계: 로컬 바탕화면 전용 완성본 출력 (바탕화면/한국 숏폼_산출물/Stock)
- 심의 100% 프리패스: 로고 없는 100% 클린 뷰 적용
"""

from typing import Dict, Any, Optional
from PIL import Image


class StockShortsPipeline:
    """📈 StockMaster AI 숏폼 자동 생산 파이프라인 (완전 독립 레고 블록)"""

    def __init__(self):
        from core.shorts_engine.stock_shorts_producer import StockShortsProducer
        self._producer = StockShortsProducer()

    def produce(
        self,
        topic_id: Optional[int] = None,
        gender: Optional[str] = None,
        custom_master_image: Optional[Image.Image] = None,
        seed: Optional[int] = None,
        force_fresh_record: bool = False
    ) -> str:
        """주식 1080p 숏폼 엔진 호출 및 완성본 MP4 경로 반환 (매번 새로운 인물/주제 순환)"""
        res = self._producer.produce(
            topic_id=topic_id,
            gender=gender,
            custom_hero_image=custom_master_image,
            seed=seed,
            force_fresh_record=force_fresh_record
        )
        return res.get("output_mp4", "")

    def produce_master_photo(
        self,
        topic_id: Optional[int] = None,
        gender: Optional[str] = None,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """주식 주제별 순정 실사 마스터 사진 단독 생산"""
        return self._producer.produce_master_photo(
            topic_id=topic_id,
            gender=gender,
            seed=seed
        )

    def produce_topics(
        self,
        start_topic: int = 1,
        end_topic: int = 8,
        gender: Optional[str] = None
    ) -> list:
        """주식 숏폼을 지정 범위까지 100% 무인 순차적으로 연속 렌더링"""
        import logging
        log = logging.getLogger("StockShortsPipeline")
        results = []
        for t_id in range(start_topic, end_topic + 1):
            log.info(f"🚀 [주식 숏폼] [{t_id}/{end_topic}] 주제 #{t_id} 무인 렌더링 가동...")
            try:
                res = self._producer.produce(topic_id=t_id, gender=gender)
                results.append(res)
                log.info(f"🎉 [주식 숏폼] [{t_id}/{end_topic}] 주제 #{t_id} 완료: {res.get('output_mp4')}")
            except Exception as e:
                log.error(f"❌ [주식 숏폼] [{t_id}/{end_topic}] 주제 #{t_id} 실패: {e}")
                results.append({"topic_id": t_id, "error": str(e)})
        return results


    def produce_realtime_30s_shorts(self, stock_name: str = "삼성전자", force_fresh_record: bool = True) -> Dict[str, Any]:
        """📊 30초 실시간 퀀트 전광판 숏폼 단독 무인 생산 파이프라인 호출"""
        from brands.stock.stock_quant_shorts_builder import StockQuantShortsBuilder
        builder = StockQuantShortsBuilder()
        return builder.build_30s_samsung_shorts(force_fresh_record=force_fresh_record)


if __name__ == "__main__":
    import sys
    import logging

    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    print("=" * 70)
    print("📈 [StockMaster AI 숏폼 자율 마케팅 봇] 30초 실시간 퀀트 무인 숏폼 가동")
    print("=" * 70)

    pipeline = StockShortsPipeline()
    res = pipeline.produce_realtime_30s_shorts()
    print("RESULT:", res)
    print("=" * 70)
    print(f"🎉 [주식 숏폼 자율 생산 완결] 완제품 MP4: {res.get('root_final_mp4')}")
    print("=" * 70)
