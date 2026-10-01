# -*- coding: utf-8 -*-
"""
AuraCardnewsTopic8Pipeline - 🚀 [Aura 카드뉴스 8번 주제('500m 안심 레이더 & 번개 퀘스트') 5장 풀세트 무인 통합 파이프라인]
====================================================================================================================
• 핵심 기능:
  1. 📸 1번 표지(S1): 24세 포니테일 미녀 + 화이트 고프코어 윈드브레이커 + 성수동 테라스 거리 3.5M Wan 2.1 실사 표지
  2. 📱 2번 슬라이드(S2): 1번과 동일 인물/의상으로 3.5M 거리에서 안심 스마트폰 확인 실사
  3. 🛡️ 3번 슬라이드(S3): 숏폼 원본 3.0s '새 데이트 퀘스트 등록 모달' UI 100% 무손실 매립 + 500m 프라이버시 카피 결합
  4. ⚡ 4번 슬라이드(S4): 숏폼 원본 6.5s '번개 퀘스트 등록 완료 & 24시간 지도 레이더' UI 100% 무손실 매립 + 동네 메이트 카피 결합
  5. 🎁 5번 슬라이드(S5): 2030 동네 번개 찬반 토론 + VIP 3대 혜택 + 네이버 그린 검색창(['아우라AI데이팅'])
  6. 📝 SNS 포스팅 가이드 텍스트 자동 생성 및 최종 산출물 폴더 완결 패키징
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
from brands.aura.aura_cardnews_topic8_wardrobe import get_wardrobe, get_all_wardrobes
from brands.aura.aura_cardnews_gemini_copywriter import AuraCardnewsGeminiCopywriter
from brands.aura.aura_cardnews_s1_topic8_builder import AuraCardnewsS1Topic8Builder
from brands.aura.aura_cardnews_s2_topic8_builder import AuraCardnewsS2Topic8Builder
from brands.aura.aura_cardnews_s3_topic8_builder import AuraCardnewsS3Topic8Builder
from brands.aura.aura_cardnews_s4_topic8_builder import AuraCardnewsS4Topic8Builder
from brands.aura.aura_cardnews_s5_topic8_builder import AuraCardnewsS5Topic8Builder

logger = logging.getLogger("AuraCardnewsTopic8Pipeline")


class AuraCardnewsTopic8Pipeline:
    """Aura 8번 주제 카드뉴스 5장 풀세트 자율 생성 파이프라인 (10벌 룩북 + 제미나이 실시간 AI 카피라이터 완벽 연동)"""

    def __init__(self):
        self.copywriter = AuraCardnewsGeminiCopywriter()
        self.s1_builder = AuraCardnewsS1Topic8Builder()
        self.s2_builder = AuraCardnewsS2Topic8Builder()
        self.s3_builder = AuraCardnewsS3Topic8Builder()
        self.s4_builder = AuraCardnewsS4Topic8Builder()
        self.s5_builder = AuraCardnewsS5Topic8Builder()

    def run_pipeline(self, outfit_id: Optional[int] = None, target_dir: Optional[str] = None, copy_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        8번 주제 카드뉴스 5장 풀세트 자동 생성
        - outfit_id: 1~10번 의상 지정 (None이면 랜덤 선택)
        - target_dir: 산출물 저장 디렉터리 (None이면 신규 생성)
        - copy_data: 사전 생성된 카피 (None이면 제미나이가 실시간 창작)
        """
        # 1. 대상 디렉터리 준비
        if not target_dir:
            out_dir = AuraCardnewsStorage.create_target_directory(theme_code="safe_radar_500m")
        else:
            out_dir = Path(target_dir)
            out_dir.mkdir(parents=True, exist_ok=True)

        # 2. 이번 회차의 OOTD 1벌 선정 (1번과 2번에 동시 주입)
        selected_outfit = get_wardrobe(outfit_id=outfit_id)
        outfit_name = selected_outfit["name_ko"]
        style_mood = selected_outfit["style_mood"]
        category = selected_outfit["category"]

        logger.info(f"✨ [AuraTopic8Pipeline] 8번 카드뉴스 5장 풀세트 생성 개시")
        logger.info(f"👗 [선정된 의상]: #{selected_outfit['id']} {outfit_name} ({category} / {style_mood})")
        logger.info(f"📁 [저장 경로]: {out_dir}")

        # 3. 제미나이 8번 주제 실시간 5장 카피 창작 (1회 호출)
        if not copy_data:
            logger.info("🤖 [AuraTopic8Pipeline] 제미나이 실시간 카피라이터 가동...")
            copy_data = self.copywriter.generate_cardnews_copy(topic_id=8, outfit=selected_outfit)
        
        c_s1 = copy_data.get("slide1", {})
        c_s2 = copy_data.get("slide2", {})
        c_s3 = copy_data.get("slide3", {})
        c_s4 = copy_data.get("slide4", {})
        c_s5 = copy_data.get("slide5", {})

        # 4. 1번 슬라이드: Wan 2.1 신규 표지 실사 생성 & 렌더링 (의상 + 제미나이 카피 주입)
        logger.info("▶ [1/5] 1번 표지 카드뉴스 렌더링 중...")
        s1_path = self.s1_builder.produce(target_dir=str(out_dir), outfit=selected_outfit, copy_data=c_s1)

        # 5. 2번 슬라이드: 3.5M 스마트폰 확인 실사 생성 & 렌더링 (1번 동일 인물/의상 + 제미나이 카피 주입)
        logger.info("▶ [2/5] 2번 3.5M 실사 카드뉴스 렌더링 중 (1번과 동일 의상 동기화)...")
        s2_path = self.s2_builder.produce(target_dir=str(out_dir), outfit=selected_outfit, copy_data=c_s2)

        # 6. 3번 슬라이드: 숏폼 원본 3.0s '새 데이트 퀘스트 등록 모달' UI + 상단 카피 결합
        logger.info("▶ [3/5] 3번 500m 안심 등록 모달 카드뉴스 렌더링 중...")
        s3_path = self.s3_builder.produce(target_dir=str(out_dir), copy_data=c_s3)

        # 7. 4번 슬라이드: 숏폼 원본 6.5s '번개 퀘스트 등록 완료 & 지도 레이더' UI + 상단 카피 결합
        logger.info("▶ [4/5] 4번 지도 레이더 카드뉴스 렌더링 중...")
        s4_path = self.s4_builder.produce(target_dir=str(out_dir), copy_data=c_s4)

        # 8. 5번 슬라이드: 찬반 토론 & VIP 3대 혜택 & 네이버 그린 검색창
        logger.info("▶ [5/5] 5번 엔딩 CTA 카드뉴스 렌더링 중...")
        s5_path = self.s5_builder.produce(target_dir=str(out_dir), copy_data=c_s5)

        # 9. SNS 포스팅 가이드 파일 생성 (AuraSNSGuideMaster 7대 채널 통합)
        from brands.aura.aura_sns_guide_master import AuraSNSGuideMaster
        guide_content = AuraSNSGuideMaster.build_cardnews_guide(
            topic_id=8,
            theme_name="500m 안심 레이더 & 안심 번개 퀘스트",
            theme_code="safe_radar_500m",
            copy_data=copy_data
        )
        guide_path = out_dir / "SNS_포스팅_가이드_KO.txt"
        guide_path.write_text(guide_content, encoding="utf-8")

        result = {
            "status": "SUCCESS",
            "theme": "safe_radar_500m",
            "outfit": selected_outfit,
            "copy_data": copy_data,
            "target_directory": str(out_dir),
            "slides": [s1_path, s2_path, s3_path, s4_path, s5_path],
            "guide_path": str(guide_path)
        }
        logger.info(f"🎉 [AuraTopic8Pipeline] 8번 카드뉴스 5장 풀세트 생성 완결!")
        return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pipeline = AuraCardnewsTopic8Pipeline()
    res = pipeline.run_pipeline()
    print("RESULT:", res)
