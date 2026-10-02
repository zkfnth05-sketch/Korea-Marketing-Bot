# -*- coding: utf-8 -*-
"""
AuraCardnewsTopic5Pipeline - ⚖️ [Aura 카드뉴스 5번 주제('가치관 밸런스 매칭') 5장 풀세트 무인 통합 파이프라인]
========================================================================================================
• 핵심 기능:
  1. 🤖 제미나이 100% 실시간 카피라이터(AuraCardnewsGeminiCopywriter) 5장 전체 카피 자율 집필 (1회 호출)
  2. 📸 1번 표지: 고양이상 21세 여신 + 연남동 브런치 카페 1080x1350 초고화질 렌더링 (AuraCardnewsS1Topic5Builder)
  3. ⚖️ 2, 3, 4번 슬라이드: 숏폼 가치관 밸런스 매칭 이식 (비용, 연락, 남사친) 1080x1350 렌더링 (AuraCardnewsS2S4BalanceBuilder)
  4. 🎁 5번 엔딩: 실시간 찬반 토론 & 네이버 검색['아우라AI데이팅'] CTA 카드 (AuraCardnewsS5Topic5Builder)
  5. 📝 SNS 포스팅 가이드 자동 생성 및 바탕화면 완결 패키징
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
from brands.aura.aura_cardnews_s1_topic5_builder import AuraCardnewsS1Topic5Builder
from brands.aura.aura_cardnews_s2_s4_balance_builder import AuraCardnewsS2S4BalanceBuilder
from brands.aura.aura_cardnews_s5_topic5_builder import AuraCardnewsS5Topic5Builder
from brands.aura.aura_sns_guide_master import AuraSNSGuideMaster

logger = logging.getLogger("AuraCardnewsTopic5Pipeline")


class AuraCardnewsTopic5Pipeline:
    """Aura 5번 주제 카드뉴스 5장 풀세트 자율 생성 및 제미나이 카피 동기화 파이프라인"""

    def __init__(self):
        self.copywriter = AuraCardnewsGeminiCopywriter()
        self.s1_builder = AuraCardnewsS1Topic5Builder()
        self.s2_s4_builder = AuraCardnewsS2S4BalanceBuilder()
        self.s5_builder = AuraCardnewsS5Topic5Builder()

    def run_pipeline(
        self,
        target_dir: Optional[str] = None,
        copy_data: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        5번 주제 카드뉴스 5장 풀세트 자동 생성
        """
        theme_code = "value_balance"
        theme_name = "가치관 밸런스 매칭"

        # 1. 대상 디렉터리 준비 (바탕화면 전용 경로)
        if not target_dir:
            out_dir = AuraCardnewsStorage.create_target_directory(
                theme_code=theme_code,
                lang="KO",
                theme_title=theme_name
            )
        else:
            out_dir = Path(target_dir)
            out_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"✨ [AuraTopic5Pipeline] 5번 카드뉴스 5장 풀세트 생성 개시 -> {out_dir}")

        # 2. 제미나이 100% 실시간 5장 전체 카피 + SNS 본문 자율 집필 (1회 호출)
        if not copy_data:
            logger.info("🤖 [AuraTopic5Pipeline] 제미나이 가치관 밸런스 카피 실시간 창작 중...")
            copy_data = self.copywriter.generate_cardnews_copy(topic_id=5)

        # 3. 1번 슬라이드: 신선 1번 표지 렌더링 (카피 주입)
        logger.info("▶ [1/5] 1번 표지 카드뉴스 렌더링 중 (제미나이 카피 주입)...")
        s1_path = self.s1_builder.produce(target_dir=str(out_dir), copy_data=copy_data, seed=seed)

        # 4. 2, 3, 4번 슬라이드: 가치관 밸런스 매칭 3대 라운드 초고화질 렌더링
        logger.info("▶ [2~4/5] 2, 3, 4번 가치관 밸런스 카드 렌더링 중...")
        s2_s4_results = self.s2_s4_builder.build_all(str(out_dir))
        s2_path = s2_s4_results[2]
        s3_path = s2_s4_results[3]
        s4_path = s2_s4_results[4]

        # 5. 5번 슬라이드: 찬반 토론 & 네이버 검색['아우라AI데이팅'] CTA 카드
        logger.info("▶ [5/5] 5번 엔딩 CTA 카드뉴스 렌더링 중...")
        s5_path = str(out_dir / "slide_5.png")
        s5_copy = copy_data.get("slide5", copy_data) if (copy_data and isinstance(copy_data, dict)) else None
        self.s5_builder.build_s5_ending_card(s5_path, copy_data=s5_copy)

        slide_paths = [s1_path, s2_path, s3_path, s4_path, s5_path]

        # 6. SNS 포스팅 가이드 파일 생성 (AuraSNSGuideMaster 7대 채널 통합)
        guide_content = AuraSNSGuideMaster.build_cardnews_guide(
            topic_id=5,
            theme_name=theme_name,
            theme_code=theme_code,
            copy_data=copy_data
        )
        guide_path = out_dir / "SNS_포스팅_가이드_KO.txt"
        guide_path.write_text(guide_content, encoding="utf-8")

        # 7. 메타데이터 저장
        meta_path = AuraCardnewsStorage.save_metadata(
            target_dir=out_dir,
            theme_code=theme_code,
            theme_title=theme_name,
            image_paths=slide_paths,
            guide_file_path=str(guide_path),
            lang="KO"
        )

        result = {
            "success": True,
            "status": "SUCCESS",
            "theme_name": theme_name,
            "theme_code": theme_code,
            "theme": theme_code,
            "output_dir": str(out_dir),
            "target_directory": str(out_dir),
            "total_slides": len(slide_paths),
            "slides": slide_paths,
            "slide_paths": slide_paths,
            "guide_path": str(guide_path),
            "metadata_path": str(meta_path)
        }
        logger.info(f"🎉 [AuraTopic5Pipeline] 5번 카드뉴스 5장 풀세트 완벽 생성 완료: {out_dir}")
        return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pipeline = AuraCardnewsTopic5Pipeline()
    res = pipeline.run_pipeline()
    print("RESULT:", res)
