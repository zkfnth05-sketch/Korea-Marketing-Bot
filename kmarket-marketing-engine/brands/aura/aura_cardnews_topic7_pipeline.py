# -*- coding: utf-8 -*-
"""
AuraCardnewsTopic7Pipeline - 🚀 [Aura 카드뉴스 7번 주제('AI 매력상 & 관상/궁합 진단') 5장 풀세트 무인 통합 파이프라인]
====================================================================================================================
• 핵심 기능:
  1. 👗 10벌의 세련된 직장인 룩 중 이번 회차의 의상(Wardrobe) 1벌 자동 선정 (랜덤/로테이션)
  2. 📸 1번 표지(S1)와 2번 셀카(S2)에 100% 동일한 의상 프롬프트를 동시 주입하여 Wan 2.1 자율 실사 생성
  3. 📱 3번 진단 리포트 & 4번 궁합 매칭 슬라이드에 숏폼 원본 3D 스마트폰 화면 + 상단 공식 카피 결합
  4. 🎁 5번 엔딩 찬반 토론 & VIP 3대 혜택 & 네이버 그린 검색창(['아우라AI데이팅']) 렌더링
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
from brands.aura.aura_cardnews_topic7_wardrobe import get_wardrobe, get_all_wardrobes
from brands.aura.aura_cardnews_gemini_copywriter import AuraCardnewsGeminiCopywriter
from brands.aura.aura_cardnews_s1_topic7_builder import AuraCardnewsS1Topic7Builder
from brands.aura.aura_cardnews_s2_topic7_builder import AuraCardnewsS2Topic7Builder
from brands.aura.aura_cardnews_s3_topic7_builder import AuraCardnewsS3Topic7Builder
from brands.aura.aura_cardnews_s4_topic7_builder import AuraCardnewsS4Topic7Builder
from brands.aura.aura_cardnews_s5_topic7_builder import AuraCardnewsS5Topic7Builder

logger = logging.getLogger("AuraCardnewsTopic7Pipeline")


class AuraCardnewsTopic7Pipeline:
    """Aura 7번 주제 카드뉴스 5장 풀세트 자율 생성 및 의상/제미나이 카피 동기화 파이프라인"""

    def __init__(self):
        self.copywriter = AuraCardnewsGeminiCopywriter()
        self.s1_builder = AuraCardnewsS1Topic7Builder()
        self.s2_builder = AuraCardnewsS2Topic7Builder()
        self.s3_builder = AuraCardnewsS3Topic7Builder()
        self.s4_builder = AuraCardnewsS4Topic7Builder()
        self.s5_builder = AuraCardnewsS5Topic7Builder()

    def run_pipeline(self, outfit_id: Optional[int] = None, target_dir: Optional[str] = None, copy_data: Optional[Dict[str, Any]] = None, seed: Optional[int] = None) -> Dict[str, Any]:
        """
        7번 주제 카드뉴스 5장 풀세트 자동 생성
        - outfit_id: 1~10번 의상 지정 (None이면 랜덤 선택)
        - target_dir: 산출물 저장 디렉터리 (None이면 신규 생성)
        - copy_data: 사전 생성된 카피 (None이면 제미나이가 실시간 창작)
        - seed: 일관성 제어 시드
        """
        # 1. 대상 디렉터리 준비
        if not target_dir:
            out_dir = AuraCardnewsStorage.create_target_directory(theme_code="ai_charm_scanner")
        else:
            out_dir = Path(target_dir)
            out_dir.mkdir(parents=True, exist_ok=True)

        # 2. 이번 회차의 직장인 룩 1벌 선정 (1번과 2번에 동시 주입)
        selected_outfit = get_wardrobe(outfit_id=outfit_id)
        outfit_name = selected_outfit["name_ko"]
        style_mood = selected_outfit["style_mood"]

        logger.info(f"✨ [AuraTopic7Pipeline] 7번 카드뉴스 5장 풀세트 생성 개시")
        logger.info(f"👗 [선정된 의상]: #{selected_outfit['id']} {outfit_name} ({style_mood})")
        logger.info(f"📁 [저장 경로]: {out_dir}")

        # 3. 제미나이 100% 실시간 5장 전체 카피 + SNS 본문 자율 집필 (1회 호출)
        if not copy_data:
            logger.info("🤖 [AuraTopic7Pipeline] 제미나이 깊이 있는 2030 스토리텔링 카피 실시간 창작 중...")
            copy_data = self.copywriter.generate_cardnews_copy(topic_id=7, outfit=selected_outfit)

        # 4. 1번 슬라이드: Wan 2.1 신규 표지 실사 생성 & 렌더링 (의상 + 카피 주입)
        logger.info("▶ [1/5] 1번 표지 카드뉴스 렌더링 중 (제미나이 카피 주입)...")
        s1_path = self.s1_builder.produce(target_dir=str(out_dir), outfit=selected_outfit, copy_data=copy_data, seed=seed)

        # 5. 2번 슬라이드: 3M 와이드 셀카 촬영 컷 생성 & 렌더링 (1번과 동일 의상 + 카피 주입)
        logger.info("▶ [2/5] 2번 3M 와이드 셀카 카드뉴스 렌더링 중 (1번과 동일 의상 동기화)...")
        s2_path = self.s2_builder.produce(target_dir=str(out_dir), outfit=selected_outfit, copy_data=copy_data, seed=seed)

        # 6. 3번 슬라이드: 숏폼 원본 3D 스마트폰 진단 리포트 + 상단 제미나이 카피 결합
        logger.info("▶ [3/5] 3번 진단 리포트 카드뉴스 렌더링 중 (제미나이 카피 주입)...")
        s3_path = self.s3_builder.produce(target_dir=str(out_dir), copy_data=copy_data)

        # 7. 4번 슬라이드: 숏폼 원본 3D 스마트폰 궁합 매칭 + 상단 제미나이 카피 결합
        logger.info("▶ [4/5] 4번 궁합 매칭 카드뉴스 렌더링 중 (제미나이 카피 주입)...")
        s4_path = self.s4_builder.produce(target_dir=str(out_dir), copy_data=copy_data)

        # 8. 5번 슬라이드: 찬반 토론 & VIP 3대 혜택 & 네이버 그린 검색창 (제미나이 카피 주입)
        logger.info("▶ [5/5] 5번 엔딩 CTA 카드뉴스 렌더링 중 (제미나이 찬반 토론 주입)...")
        s5_path = self.s5_builder.produce(target_dir=str(out_dir), copy_data=copy_data)

        # 9. SNS 포스팅 가이드 파일 생성 (AuraSNSGuideMaster 7대 채널 통합)
        from brands.aura.aura_sns_guide_master import AuraSNSGuideMaster
        guide_content = AuraSNSGuideMaster.build_cardnews_guide(
            topic_id=7,
            theme_name="AI 매력상 & 관상/궁합 진단",
            theme_code="ai_charm_scanner",
            copy_data=copy_data
        )
        guide_path = out_dir / "SNS_포스팅_가이드_KO.txt"
        guide_path.write_text(guide_content, encoding="utf-8")

        # 10. 메타데이터 저장
        meta_path = AuraCardnewsStorage.save_metadata(
            target_dir=out_dir,
            theme_code="ai_charm_scanner",
            theme_title="AI 매력상 & 관상/궁합 진단",
            image_paths=[s1_path, s2_path, s3_path, s4_path, s5_path],
            guide_file_path=str(guide_path),
            lang="KO"
        )

        result = {
            "status": "SUCCESS",
            "theme": "ai_charm_scanner",
            "outfit": selected_outfit,
            "target_directory": str(out_dir),
            "slides": [s1_path, s2_path, s3_path, s4_path, s5_path],
            "guide_path": str(guide_path),
            "metadata_path": str(meta_path)
        }
        logger.info(f"🎉 [AuraTopic7Pipeline] 7번 카드뉴스 5장 풀세트 생성 완결!")
        return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pipeline = AuraCardnewsTopic7Pipeline()
    res = pipeline.run_pipeline()
    print("RESULT:", res)
