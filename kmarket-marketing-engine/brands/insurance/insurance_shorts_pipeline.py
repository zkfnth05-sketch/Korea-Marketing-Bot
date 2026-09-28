# -*- coding: utf-8 -*-
"""
InsuranceShortsPipeline - 🎬 [보험 리밸런스 전용 숏폼 동영상 생산 공장]
- 1단계: '입을 부드럽게 다문 신뢰감 있는 미소' 30대 금융 어드바이저 마스터컷 인물 사진 생성 (Wan 2.1 T2I)
- 2단계: 객관적 AI 5대 보장(암/뇌/심/실비/수술) 레이더 차트 & 중복 탐지 시연 비디오 (8초)
- 3단계: Google Gemini 2.5 Flash TTS 초실사 음성 합성
- 4단계: Wan 2.2 S2V 10초 원테이크 립싱크 (5s+5s xfade) 모션 렌더링
- 5단계: 로컬 바탕화면 전용 완성본 출력 (바탕화면/한국 숏폼_산출물/Insurance)
- 심의 100% 프리패스: 로고 없는 100% 클린 뷰 적용
"""

from typing import Dict, Any, Optional
from PIL import Image


class InsuranceShortsPipeline:
    """🛡️ 보험 리밸런스 숏폼 자동 생산 파이프라인 (Aura 파이프라인 구조 100% 동일 계승)"""

    def __init__(self):
        from core.shorts_engine.insurance_shorts_producer import InsuranceShortsProducer
        self._producer = InsuranceShortsProducer()

    def produce(
        self,
        topic_id: Optional[int] = None,
        gender: Optional[str] = None,
        custom_master_image: Optional[Image.Image] = None,
        seed: Optional[int] = None
    ) -> str:
        """보험 1080p 숏폼 엔진 호출 및 완성본 MP4 경로 반환 (매번 새로운 인물/주제 순환)"""
        res = self._producer.produce(
            topic_id=topic_id,
            gender=gender,
            custom_hero_image=custom_master_image,
            seed=seed
        )
        return res.get("output_mp4", "")

    def produce_master_photo(
        self,
        topic_id: Optional[int] = None,
        gender: Optional[str] = None,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """보험 주제별 순정 실사 마스터 사진 단독 생산"""
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
        """보험 숏폼을 지정 범위까지 100% 무인 순차적으로 연속 렌더링"""
        import logging
        log = logging.getLogger("InsuranceShortsPipeline")
        results = []
        for t_id in range(start_topic, end_topic + 1):
            log.info(f"🚀 [보험 숏폼] [{t_id}/{end_topic}] 주제 #{t_id} 무인 렌더링 가동...")
            try:
                res = self._producer.produce(topic_id=t_id, gender=gender)
                results.append(res)
                log.info(f"🎉 [보험 숏폼] [{t_id}/{end_topic}] 주제 #{t_id} 완료: {res.get('output_mp4')}")
            except Exception as e:
                log.error(f"❌ [보험 숏폼] [{t_id}/{end_topic}] 주제 #{t_id} 실패: {e}")
                results.append({"topic_id": t_id, "error": str(e)})
        return results


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
    print("🛡️ [보험 리밸런스 숏폼 자율 마케팅 봇] 22초 풀 프로덕션 무인 가동")
    print("  - 주제 1: 4세대 실손보험 전환 손익 분석 (22초 세로 풀HD)")
    print("  - 파이프라인: Wan 2.1 T2I ➔ Wan 2.2 S2V 10초 원테이크 ➔ 5대 보장 레이더 차트 8초 ➔ 공식 CTA 4초")
    print("=" * 70)

    pipeline = InsuranceShortsPipeline()
    output_path = pipeline.produce(topic_id=1, gender="female", seed=20260928)
    print("=" * 70)
    print(f"🎉 [보험 숏폼 자율 생산 완결] 완제품 MP4: {output_path}")
    print("=" * 70)
