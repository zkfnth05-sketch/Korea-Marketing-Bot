# -*- coding: utf-8 -*-
"""
AuraShortsPipeline - 🎬 [Aura 데이팅 전용 숏폼 동영상 생산 공장]
- 1단계: '입을 부드럽게 다문 미소' 마스터컷 인물 사진 생성 (Wan2.1 T2I)
- 2단계: Aura 8대 킬러 주제 UI 생성 후 OpenCV 서브픽셀 정밀 매립
- 3단계: 맞춤형 한국어/다국어 음성 생성 (Edge-TTS)
- 4단계: Wan 2.2 S2V 립싱크 렌더링 및 FFmpeg 오디오 결합
- 5단계: 로컬 바탕화면 전용 완성본 출력 (바탕화면/한국 숏폼_산출물/Aura)
"""

from typing import Dict, Any, Optional
from PIL import Image


class AuraShortsPipeline:
    """Aura 숏폼 자동 생산 파이프라인 (EasyTax 파이프라인 구조 100% 동일 계승)"""

    def __init__(self):
        from core.shorts_engine.aura_shorts_producer import AuraShortsProducer
        self._producer = AuraShortsProducer()

    def produce(
        self,
        topic_id: Optional[int] = None,
        gender: Optional[str] = None,
        custom_master_image: Optional[Image.Image] = None,
        seed: Optional[int] = None
    ) -> str:
        """Aura 1080p 숏폼 엔진 호출 및 완성본 MP4 경로 반환 (매번 새로운 인물/주제 순환)"""
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
        """Aura 8대 주제별 순정 아이폰 실사 마스터 사진 단독 생산 (매번 새로운 인물/주제 순환)"""
        return self._producer.produce_master_photo(
            topic_id=topic_id,
            gender=gender,
            seed=seed
        )


if __name__ == "__main__":
    import sys
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    print("=" * 70)
    print("🤖 [Aura 숏폼 자율 마케팅 봇] 24초 풀 프로덕션 원클릭 무인 가동")
    print("  - 주제 1: 소개팅 긴급 탈출 전화 (23.8초 풀HD)")
    print("  - 파이프라인: Wan 2.1 T2I 마스터 사진 ➔ Wan 2.2 S2V 립싱크 ➔ 앱 시연(벨소리+팀장) ➔ CTA")
    print("=" * 70)

    pipeline = AuraShortsPipeline()
    output_path = pipeline.produce(topic_id=1, gender="female", seed=20260924)
    print("=" * 70)
    print(f"🎉 [Aura 숏폼 자율 생산 완결] 완제품 MP4: {output_path}")
    print("=" * 70)

