# -*- coding: utf-8 -*-
"""
InsuranceCardnewsProducer - 🛡️ [보험 리밸런스 5장 카드뉴스 전용 배치 생산 엔진]
=============================================================================
• 역할:
  - 숏폼 엔진과 100% 분리된 순수 카드뉴스 전용 독립 엔진
  - 시나리오 디렉터(InsuranceCardnewsScenarioDirector)가 기획한 1~5장 카피 및 프롬프트 기반 자동 생성
  - Wan 2.1 T2I 모듈 (generate_t2i_master)을 통한 고해상도 인물 사진 생성 (오프라인 시 안전 자율 캔버스 폴백)
  - Playwright 초고화질 타이포그래피 합성 (InsuranceCardnewsTypography)
  - 바탕화면 전용 패키징 저장 (InsuranceCardnewsStorage)
"""

import os
import sys
import copy
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw

from .insurance_cardnews_scenario_director import InsuranceCardnewsScenarioDirector
from .insurance_cardnews_typography import InsuranceCardnewsTypography
from .insurance_cardnews_storage import InsuranceCardnewsStorage
from .insurance_cardnews_gemini_copywriter import InsuranceCardnewsGeminiCopywriter
from core.engine.wan_pipeline_client import WanPipelineClient

logger = logging.getLogger("InsuranceCardnewsProducer")


class InsuranceCardnewsProducer:
    """🛡️ 보험 리밸런스 5장 풀세트 카드뉴스 전용 생산 엔진"""

    OFFICIAL_KEYWORD = "보험 리밸런스"
    OFFICIAL_URL = "https://insure-rebalance.vercel.app/"

    def __init__(self):
        self.scenario_director = InsuranceCardnewsScenarioDirector()
        self.typography_engine = InsuranceCardnewsTypography()
        self.copywriter = InsuranceCardnewsGeminiCopywriter()
        self.storage = InsuranceCardnewsStorage()
        self.wan_client = WanPipelineClient()
        self._wan_available = self.wan_client.check_health()
        if self._wan_available:
            logger.info("✅ [InsuranceProducer] ComfyUI Wan 2.1 연결 성공 - GPU 실사 T2I 생성 모드")
        else:
            logger.warning("ℹ️ [InsuranceProducer] ComfyUI 미실행 - 안전 자율 그래픽 캔버스 모드 가동")

    def _generate_slide_photo(
        self,
        card_data: Dict[str, Any],
        slide_idx: int,
        master_seed: Optional[int] = None
    ) -> Image.Image:
        """프롬프트로 Wan 2.1 실사 사진 생성 (ComfyUI 무인 자동 기동 지원)"""
        # 1. 고정 앱 에셋 화면 직접 로드 (Wan 미생성 100% 영구 재사용)
        asset_rel_path = card_data.get("asset_image")
        if card_data.get("use_direct_asset") and asset_rel_path:
            asset_full = Path(r"C:\Users\zkfnt\Desktop\한국 마케팅봇\kmarket-marketing-engine") / asset_rel_path
            if asset_full.exists():
                logger.info(f"📱 [Insurance Slide {slide_idx}] 고정 앱 에셋 화면 직접 로드: {asset_full}")
                raw_img = Image.open(str(asset_full)).convert("RGB")
                target_w, target_h = 1080, 1350
                scale = max(target_w / raw_img.width, target_h / raw_img.height)
                new_w = int(raw_img.width * scale)
                new_h = int(raw_img.height * scale)
                resized_img = raw_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                left = (new_w - target_w) // 2
                top = (new_h - target_h) // 2
                return resized_img.crop((left, top, left + target_w, top + target_h))

        # ComfyUI 무인 자율 기동 및 헬스체크
        if not (self._wan_available or self.wan_client.check_health()):
            logger.info(f"🚀 [Insurance Slide {slide_idx}] ComfyUI 백그라운드 무인 자동 기동 개시...")
            from core.engine.comfy_process_manager import ComfyProcessManager
            self._wan_available = ComfyProcessManager.ensure_running()

        # 1. Wan 2.1 가용 시 GPU 실사 렌더링
        positive_prompt = card_data.get("image_prompt", "")
        negative_prompt = card_data.get("negative_prompt", "blurry, low quality, deformed, cartoon, anime, open mouth, teeth")

        if self._wan_available or self.wan_client.check_health():
            try:
                logger.info(f"🎨 [Insurance Slide {slide_idx}] Wan 2.1 T2I 실사 사진 생성 시작 (Seed={master_seed})...")
                raw_path = self.wan_client.generate_t2i_master(
                    positive_prompt=positive_prompt,
                    negative_prompt=negative_prompt,
                    width=832,
                    height=1216,
                    seed=master_seed,
                    prefix=f"ins_cardnews_s{slide_idx}"
                )
                logger.info(f"✅ [Insurance Slide {slide_idx}] 실사 원본 생성 완료: {raw_path}")

                raw_img = Image.open(raw_path).convert("RGB")
                target_w, target_h = 1080, 1350
                scale = max(target_w / raw_img.width, target_h / raw_img.height)
                new_w = int(raw_img.width * scale)
                new_h = int(raw_img.height * scale)
                resized_img = raw_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                left = (new_w - target_w) // 2
                top = 0  # 🌟 [상단 헤드룸 100% 보존 - 얼박샷/머리잘림 원천 방지]
                return resized_img.crop((left, top, left + target_w, top + target_h))
            except Exception as we:
                logger.error(f"❌ [Insurance Slide {slide_idx}] Wan 2.1 실사 생성 예외: {we}")
                raise RuntimeError(f"Wan 2.1 실사 이미지 렌더링 실패: {we}")

        # 2. ComfyUI 가동 불가 시 안전 폴백
        raise RuntimeError("ComfyUI Wan 2.1 엔진 기동 실패로 실사 생성 불가")

    def produce_single_slide(self, slide_num: int = 1, topic_id: int = 1) -> Dict[str, Any]:
        """
        🎯 [1장 단독 생산] 특정 슬라이드 번호(예: 1번 표지)만 단독 생성 및 바탕화면 저장
        """
        scenario = self.scenario_director.get_scenario(topic_id=topic_id)
        theme_name = scenario.get("theme_name", "보험 리밸런스 핵심 진단")
        slides = scenario.get("slides", [])

        if not slides or slide_num > len(slides):
            raise ValueError(f"주제 {topic_id}의 {slide_num}번 슬라이드 시나리오가 없습니다.")

        card_info = slides[slide_num - 1]
        target_dir = self.storage.get_topic_package_dir(topic_id, theme_name)
        master_seed = int(time.time() * 1000) % 100000000

        # 3번, 4번 또는 5번 슬라이드의 경우 전용 빌더 연동
        saved_file = target_dir / f"slide_{slide_num}.png"
        if slide_num == 3:
            from .insurance_cardnews_s3_builder import InsuranceCardnewsS3Builder
            InsuranceCardnewsS3Builder().render_slide(str(saved_file), copy_data=card_info)
        elif slide_num == 4:
            from .insurance_cardnews_s4_builder import InsuranceCardnewsS4Builder
            InsuranceCardnewsS4Builder().render_slide(str(saved_file), copy_data=card_info)
        elif slide_num == 5:
            from .insurance_cardnews_s5_builder import InsuranceCardnewsS5Builder
            InsuranceCardnewsS5Builder().render_slide(str(saved_file), copy_data=card_info)
        else:
            # (1) 배경 사진 생성
            bg_photo = self._generate_slide_photo(card_info, slide_num, master_seed)

            # (2) Aura 동일 규격 Playwright 3D 타이포그래피 & 하단 감쇠 스크림 정밀 합성
            final_rgb = self.typography_engine.composite_slide(
                base_photo=bg_photo,
                card_data=card_info,
                s_idx=slide_num,
                total_slides=len(slides)
            )

            # (3) 바탕화면 저장
            saved_file = self.storage.save_slide_image(final_rgb, target_dir, slide_num)

        logger.info(f"🎉 [InsuranceProducer] {slide_num}번 단독 카드뉴스 완성: {saved_file}")

        return {
            "success": True,
            "topic_id": topic_id,
            "slide_num": slide_num,
            "theme_name": theme_name,
            "file_path": str(saved_file),
            "package_dir": str(target_dir)
        }

    def produce_full_package(self, topic_id: int = 1) -> Dict[str, Any]:
        """
        🚀 [보험 리밸런스 5장 카드뉴스 풀패키지 완제품 생산 & 바탕화면 저장]
        """
        scenario = self.scenario_director.get_scenario(topic_id=topic_id)
        theme_name = scenario.get("theme_name", "보험 리밸런스 핵심 진단")
        slides = scenario.get("slides", [])

        logger.info(f"🚀 [InsuranceProducer] 주제 #{topic_id} '{theme_name}' 5장 풀패키지 생산 시작...")

        # 1. 제미나이 5장 카피 & 캡션 생성
        copy_data = self.copywriter.generate_copy_for_topic(topic_id, theme_name, scenario)
        sns_caption = copy_data.get("sns_caption", "")

        # 2. 바탕화면 전용 패키지 폴더 생성
        target_dir = self.storage.get_topic_package_dir(topic_id, theme_name)
        saved_paths = []

        # 3. 5장 슬라이드 순차 렌더링 및 합성
        master_seed = int(time.time() * 1000) % 100000000

        for slide_num in range(1, len(slides) + 1):
            slide_raw = slides[slide_num - 1]
            slide_copy = copy_data.get(f"slide{slide_num}", slide_raw)

            card_info = {
                "badge": slide_copy.get("badge", slide_raw.get("badge")),
                "title": slide_copy.get("title", slide_raw.get("title")),
                "subtitle": slide_copy.get("subtitle", slide_raw.get("subtitle")),
                "bullets": slide_copy.get("bullets", slide_raw.get("bullets", [])),
                "cta_button": slide_copy.get("cta_button", slide_raw.get("cta_button")),
                "image_prompt": slide_raw.get("image_prompt", "")
            }

            # 3번, 4번 또는 5번 슬라이드의 경우 전용 빌더 연동
            saved_file = target_dir / f"slide_{slide_num}.png"
            if slide_num == 3:
                from .insurance_cardnews_s3_builder import InsuranceCardnewsS3Builder
                InsuranceCardnewsS3Builder().render_slide(str(saved_file), copy_data=card_info)
            elif slide_num == 4:
                from .insurance_cardnews_s4_builder import InsuranceCardnewsS4Builder
                InsuranceCardnewsS4Builder().render_slide(str(saved_file), copy_data=card_info)
            elif slide_num == 5:
                from .insurance_cardnews_s5_builder import InsuranceCardnewsS5Builder
                InsuranceCardnewsS5Builder().render_slide(str(saved_file), copy_data=card_info)
            else:
                # (1) 배경 사진 생성
                bg_photo = self._generate_slide_photo(card_info, slide_num, master_seed + slide_num * 17)

                # (2) Aura 동일 규격 Playwright 3D 타이포그래피 & 하단 감쇠 스크림 정밀 합성
                final_rgb = self.typography_engine.composite_slide(
                    base_photo=bg_photo,
                    card_data=card_info,
                    s_idx=slide_num,
                    total_slides=len(slides)
                )

                # (3) 바탕화면 저장
                saved_file = self.storage.save_slide_image(final_rgb, target_dir, slide_num)
            saved_paths.append(str(saved_file))

        # 4. 제미나이 집필 최신 트렌드 & 4단 티어 해시태그 결합 7대 채널 SNS 가이드 자동 동봉
        from .insurance_cardnews_guide_builder import InsuranceCardnewsGuideBuilder
        guide_builder = InsuranceCardnewsGuideBuilder()
        guide_file = guide_builder.save_guide_file(
            target_dir=target_dir,
            topic_id=topic_id,
            theme_name=theme_name,
            slides_data=slides,
            gemini_copy=copy_data
        )

        logger.info(f"🎉 [InsuranceProducer] 주제 #{topic_id} 5장 카드뉴스 풀패키지 + 최신 트렌드 SNS 가이드 완성! (저장 폴더: {target_dir})")

        return {
            "success": True,
            "topic_id": topic_id,
            "theme_name": theme_name,
            "slides_count": len(saved_paths),
            "package_dir": str(target_dir),
            "slide_files": saved_paths,
            "guide_file": str(guide_file),
            "sns_caption": sns_caption
        }
