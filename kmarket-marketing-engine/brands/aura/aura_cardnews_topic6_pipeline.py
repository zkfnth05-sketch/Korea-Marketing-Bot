# -*- coding: utf-8 -*-
"""
AuraCardnewsTopic6Pipeline - 🚀 [Aura 카드뉴스 6번 주제('AI 첫대화 비서 / 스마트 오프너') 5장 풀세트 무인 통합 파이프라인]
===================================================================================================================
• 핵심 기능:
  1. 🤖 제미나이 100% 실시간 카피라이터(AuraCardnewsGeminiCopywriter)를 통한 5장 전체 카피 + SNS 본문 자율 집필 (1회 호출)
  2. 📸 1번 표지(S1)와 2번 고민컷(S2)에 26세 훈남 모델 + 서울 루프탑 야경 실사 생성
  3. 📱 3번 추천 문구 3종 & 4번 티키타카 대화 성공 슬라이드에 숏폼 원본 3D 스마트폰 화면 + 상단 제미나이 카피 결합
  4. 🎁 5번 엔딩 찬반 토론 & VIP 대화 혜택 & 네이버 그린 검색창(['아우라AI데이팅']) 렌더링
  5. 📝 SNS 포스팅 가이드 텍스트 자동 생성 및 최종 산출물 폴더 완결 패키징
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from brands.aura.aura_cardnews_storage import AuraCardnewsStorage
from brands.aura.aura_cardnews_gemini_copywriter import AuraCardnewsGeminiCopywriter
from brands.aura.aura_cardnews_s1_topic6_builder import AuraCardnewsS1Topic6Builder
from brands.aura.aura_cardnews_s2_topic6_builder import AuraCardnewsS2Topic6Builder
from brands.aura.aura_cardnews_s3_topic6_builder import AuraCardnewsS3Topic6Builder
from brands.aura.aura_cardnews_s4_topic6_builder import AuraCardnewsS4Topic6Builder
from brands.aura.aura_cardnews_s5_topic6_builder import AuraCardnewsS5Topic6Builder

logger = logging.getLogger("AuraCardnewsTopic6Pipeline")


class AuraCardnewsTopic6Pipeline:
    """Aura 6번 주제 카드뉴스 5장 풀세트 자율 생성 및 제미나이 카피 동기화 파이프라인"""

    def __init__(self):
        self.copywriter = AuraCardnewsGeminiCopywriter()
        self.s1_builder = AuraCardnewsS1Topic6Builder()
        self.s2_builder = AuraCardnewsS2Topic6Builder()
        self.s3_builder = AuraCardnewsS3Topic6Builder()
        self.s4_builder = AuraCardnewsS4Topic6Builder()
        self.s5_builder = AuraCardnewsS5Topic6Builder()

    def run_pipeline(self, target_dir: Optional[str] = None, copy_data: Optional[Dict[str, Any]] = None, seed: Optional[int] = None) -> Dict[str, Any]:
        """
        6번 주제 카드뉴스 5장 풀세트 자동 생성
        - target_dir: 산출물 저장 디렉터리 (None이면 신규 생성)
        - copy_data: 사전 생성된 카피 (None이면 제미나이가 실시간 창작)
        - seed: 인물 실사 일관성 제어 시드
        """
        # 1. 대상 디렉터리 준비
        if not target_dir:
            out_dir = AuraCardnewsStorage.create_target_directory(theme_code="smart_opener")
        else:
            out_dir = Path(target_dir)
            out_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"✨ [AuraTopic6Pipeline] 6번 카드뉴스 5장 풀세트 생성 개시 -> {out_dir}")

        # 2. 제미나이 100% 실시간 5장 전체 카피 + SNS 본문 자율 집필 (1회 호출)
        if not copy_data:
            logger.info("🤖 [AuraTopic6Pipeline] 제미나이 깊이 있는 2030 스토리텔링 카피 실시간 창작 중...")
            copy_data = self.copywriter.generate_cardnews_copy(topic_id=6)

        # 3. 1번 슬라이드: Wan 2.1 신규 표지 실사 생성 & 렌더링 (카피 주입)
        logger.info("▶ [1/5] 1번 표지 카드뉴스 렌더링 중 (제미나이 카피 주입)...")
        s1_path = self.s1_builder.produce(target_dir=str(out_dir), copy_data=copy_data, seed=seed)

        # 4. 2번 슬라이드: 고민하는 훈남 실사 생성 & 렌더링 (1번과 동일 인물/의상 + 카피 주입)
        logger.info("▶ [2/5] 2번 고민 컷 카드뉴스 렌더링 중 (제미나이 카피 주입)...")
        s2_path = self.s2_builder.produce(target_dir=str(out_dir), copy_data=copy_data, seed=seed)

        # 5. 3번 슬라이드: 숏폼 원본 3D 스마트폰 화면 + 상단 제미나이 카피 결합
        logger.info("▶ [3/5] 3번 추천 문구 카드뉴스 렌더링 중 (제미나이 카피 주입)...")
        s3_path = self.s3_builder.produce(target_dir=str(out_dir), copy_data=copy_data)

        # 6. 4번 슬라이드: 숏폼 원본 3D 스마트폰 화면 + 상단 제미나이 카피 결합
        logger.info("▶ [4/5] 4번 대화 성공 카드뉴스 렌더링 중 (제미나이 카피 주입)...")
        s4_path = self.s4_builder.produce(target_dir=str(out_dir), copy_data=copy_data)

        # 7. 5번 슬라이드: 찬반 토론 & VIP 대화 혜택 & 네이버 그린 검색창 (제미나이 카피 주입)
        logger.info("▶ [5/5] 5번 엔딩 CTA 카드뉴스 렌더링 중 (제미나이 찬반 토론 주입)...")
        s5_path = self.s5_builder.produce(target_dir=str(out_dir), copy_data=copy_data)

        # 8. SNS 포스팅 가이드 파일 생성 (AuraSNSGuideMaster 7대 채널 통합)
        from brands.aura.aura_sns_guide_master import AuraSNSGuideMaster
        guide_content = AuraSNSGuideMaster.build_cardnews_guide(
            topic_id=6,
            theme_name="AI 첫대화 비서 / 스마트 오프너",
            theme_code="smart_opener",
            copy_data=copy_data
        )
        guide_path = out_dir / "SNS_포스팅_가이드_KO.txt"
        guide_path.write_text(guide_content, encoding="utf-8")

        # 9. 메타데이터 저장
        meta_path = AuraCardnewsStorage.save_metadata(
            target_dir=out_dir,
            theme_code="smart_opener",
            theme_title="AI 첫대화 비서 / 스마트 오프너",
            image_paths=[s1_path, s2_path, s3_path, s4_path, s5_path],
            guide_file_path=str(guide_path),
            lang="KO"
        )

        result = {
            "status": "SUCCESS",
            "theme": "smart_opener",
            "target_directory": str(out_dir),
            "slides": [s1_path, s2_path, s3_path, s4_path, s5_path],
            "guide_path": str(guide_path),
            "metadata_path": str(meta_path)
        }
        logger.info(f"🎉 [AuraTopic6Pipeline] 6번 카드뉴스 5장 풀세트 생성 완결!")
        return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pipeline = AuraCardnewsTopic6Pipeline()
    res = pipeline.run_pipeline()
    print("RESULT:", res)
