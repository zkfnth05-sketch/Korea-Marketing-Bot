# -*- coding: utf-8 -*-
"""
AuraCardnewsProducer - 💖 [EasyTax 검증 규격 기반 Aura 카드뉴스 전용 배치 생산 엔진]
=============================================================================
• 역할:
  - 숏폼 엔진과 100% 분리된 순수 카드뉴스 전용 독립 엔진
  - 시나리오 디렉터(AuraCardnewsScenarioDirector)가 기획한 1~5장 카피 및 프롬프트 기반 자동 생성
  - Wan 2.1 T2I 모듈 (generate_t2i_master)을 통한 고해상도 인물 사진 생성
  - Playwright 초고화질 타이포그래피 합성 (AuraCardnewsTypography)
  - 바탕화면 전용 패키징 저장 (AuraCardnewsStorage)
"""

import os
import sys
import copy
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image

from .aura_cardnews_scenario_director import AuraCardnewsScenarioDirector
from .aura_cardnews_typography import AuraCardnewsTypography
from .aura_cardnews_storage import AuraCardnewsStorage
from .aura_cardnews_gemini_copywriter import AuraCardnewsGeminiCopywriter
from core.engine.wan_pipeline_client import WanPipelineClient

logger = logging.getLogger("AuraCardnewsProducer")


class AuraCardnewsProducer:
    """💖 Aura 2030 데이팅 5장 풀세트 카드뉴스 전용 생산 엔진 (제미나이 100% 실시간 카피라이터 일체형)"""

    OFFICIAL_KEYWORD = "아우라AI데이팅"
    OFFICIAL_URL = "https://aura-ai-dating.vercel.app/"

    def __init__(self):
        self.scenario_director = AuraCardnewsScenarioDirector()
        self.typography_engine = AuraCardnewsTypography()
        self.copywriter = AuraCardnewsGeminiCopywriter()
        self.wan_client = WanPipelineClient()
        self._wan_available = self.wan_client.check_health()
        if self._wan_available:
            logger.info("✅ [AuraCardnewsProducer] ComfyUI Wan 2.1 연결 성공 - GPU 실사 T2I 생성 모드")
        else:
            logger.warning("⚠️ [AuraCardnewsProducer] ComfyUI 미실행 - 서버 확인 필요")

    def _generate_slide_photo(
        self,
        card_data: Dict[str, Any],
        slide_idx: int,
        master_seed: Optional[int] = None
    ) -> Image.Image:
        """시나리오 디렉터에 정의된 프롬프트로 Wan 2.1 실사 사진 생성 (오프라인 시 안전 자율 캔버스 폴백)"""
        positive_prompt = card_data.get("image_prompt", "")
        negative_prompt = card_data.get("negative_prompt", "")
        
        if not positive_prompt:
            raise ValueError(f"[Slide {slide_idx}] 이미지 프롬프트 부재로 실사 사진 생성 불가")

        if master_seed is None:
            master_seed = int(time.time() * 1000) % 100000000

        # Wan 2.1 가용 시에만 로컬 GPU T2I 생성 시도
        if not (self._wan_available or self.wan_client.check_health()):
            raise RuntimeError(f"[Slide {slide_idx}] ComfyUI Wan 2.1 엔진 미실행 (빈 캔버스 폴백 100% 원천 금지)")

        try:
            logger.info(f"🎨 [Slide {slide_idx}] Wan 2.1 T2I 실사 사진 실시간 생성 시작 (Seed={master_seed})...")
            raw_path = self.wan_client.generate_t2i_master(
                positive_prompt=positive_prompt,
                negative_prompt=negative_prompt,
                width=832,
                height=1216,
                seed=master_seed,
                prefix=f"aura_cardnews_s{slide_idx}"
            )
            logger.info(f"✅ [Slide {slide_idx}] 실사 원본 생성 완료: {raw_path}")

            # 1080x1350 스마트 비율 맞춤 크롭
            raw_img = Image.open(raw_path).convert("RGB")
            target_w, target_h = 1080, 1350
            scale = max(target_w / raw_img.width, target_h / raw_img.height)
            new_w = int(raw_img.width * scale)
            new_h = int(raw_img.height * scale)
            resized_img = raw_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            left = (new_w - target_w) // 2
            top = (new_h - target_h) // 2
            cropped = resized_img.crop((left, top, left + target_w, top + target_h))
            return cropped
        except Exception as we:
            logger.error(f"❌ [Slide {slide_idx}] Wan 2.1 실사 T2I 생성 실패: {we}")
            raise RuntimeError(f"Slide {slide_idx} Wan 2.1 실사 이미지 렌더링 실패: {we}")

    def produce_slide(
        self,
        slide_num: int = 1,
        topic_id: int = 1,
        master_seed: Optional[int] = None,
        target_dir: Optional[Path] = None,
        fashion_id: Optional[int] = None,
        copy_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        🚀 [봇 자율 구동] 특정 슬라이드 번호 단독 생성 및 바탕화면 저장
        """
        scenario = self.scenario_director.get_scenario(topic_id=topic_id, fashion_id=fashion_id)
        theme_code = scenario.get("theme_code", "escape_call")
        theme_name = scenario.get("theme_name", "소개팅 긴급 탈출 전화")
        slides = scenario.get("slides", [])

        if not slides or slide_num > len(slides):
            raise ValueError(f"주제 {topic_id}의 {slide_num}번 슬라이드 시나리오가 없습니다.")

        card_data = copy.deepcopy(slides[slide_num - 1])
        logger.info(f"🚀 [AuraCardnewsProducer] {slide_num}번 카드 봇 자율 생성 시작: {theme_name}")

        # 제미나이 동적 카피 주입
        if copy_data:
            s_key = f"slide{slide_num}"
            s_copy = copy_data.get(s_key, copy_data) if isinstance(copy_data, dict) else {}
            if isinstance(s_copy, dict):
                h1 = s_copy.get("headline_line1", "")
                h2 = s_copy.get("headline_line2", "")
                if h1:
                    card_data["title"] = f"{h1}\n{h2}" if h2 else h1
                if s_copy.get("subtitle"):
                    card_data["subtitle"] = s_copy["subtitle"]
                if s_copy.get("bullets"):
                    card_data["bullets"] = s_copy["bullets"]
                if s_copy.get("badge"):
                    card_data["badge"] = s_copy["badge"]
                if s_copy.get("cta_text"):
                    card_data["cta_button"] = s_copy["cta_text"]

        # 1. 고정 에셋(Aura 앱 실물 화면 등)인 경우 Wan 생성 없이 즉시 로드 (영구 재사용)
        asset_rel_path = card_data.get("asset_image")
        if card_data.get("use_direct_asset") and asset_rel_path:
            asset_full = Path(r"C:\Users\zkfnt\Desktop\한국 마케팅봇\kmarket-marketing-engine") / asset_rel_path
            if asset_full.exists():
                logger.info(f"📱 [Slide {slide_num}] 고정 앱 에셋 화면 직접 로드 (Wan 미생성 100% 영구 재사용): {asset_full}")
                base_photo = Image.open(str(asset_full)).convert("RGB")
            else:
                logger.warning(f"⚠️ [Slide {slide_num}] 에셋 파일을 찾을 수 없어 기본 렌더링 진행: {asset_full}")
                base_photo = self._generate_slide_photo(card_data=card_data, slide_idx=slide_num, master_seed=master_seed)
        else:
            # 1. Wan 2.1 사진 생성 (시나리오 디렉터의 비주얼 프롬프트 사용)
            base_photo = self._generate_slide_photo(
                card_data=card_data,
                slide_idx=slide_num,
                master_seed=master_seed
            )

        # 2. 5번 슬라이드의 경우 주제별 전용 럭셔리 엔딩 CTA 빌더 연동
        if slide_num == 5:
            topic_s5_rendered = False
            temp_s5_path = Path(__file__).resolve().parent / f"temp_s5_topic{topic_id}.png"
            s5_copy = copy_data.get("slide5", copy_data) if (copy_data and isinstance(copy_data, dict)) else None
            try:
                if topic_id == 1:
                    from .aura_cardnews_s5_topic1_builder import AuraCardnewsS5Topic1Builder
                    AuraCardnewsS5Topic1Builder().build_s5_ending_card(str(temp_s5_path), copy_data=s5_copy)
                    rendered_slide = Image.open(str(temp_s5_path)).convert("RGB")
                    topic_s5_rendered = True
                elif topic_id == 2:
                    from .aura_cardnews_s5_topic2_builder import AuraCardnewsS5Topic2Builder
                    AuraCardnewsS5Topic2Builder().build_s5_ending_card(str(temp_s5_path), copy_data=s5_copy)
                    rendered_slide = Image.open(str(temp_s5_path)).convert("RGB")
                    topic_s5_rendered = True
                elif topic_id == 3:
                    from .aura_cardnews_s5_topic3_builder import AuraCardnewsS5Topic3Builder
                    AuraCardnewsS5Topic3Builder().build_s5_ending_card(str(temp_s5_path), copy_data=s5_copy)
                    rendered_slide = Image.open(str(temp_s5_path)).convert("RGB")
                    topic_s5_rendered = True
                elif topic_id == 4:
                    from .aura_cardnews_s5_topic4_builder import AuraCardnewsS5Topic4Builder
                    AuraCardnewsS5Topic4Builder().build_s5_ending_card(str(temp_s5_path), copy_data=s5_copy)
                    rendered_slide = Image.open(str(temp_s5_path)).convert("RGB")
                    topic_s5_rendered = True
                elif topic_id == 5:
                    from .aura_cardnews_s5_topic5_builder import AuraCardnewsS5Topic5Builder
                    AuraCardnewsS5Topic5Builder().build_s5_ending_card(str(temp_s5_path), copy_data=s5_copy)
                    rendered_slide = Image.open(str(temp_s5_path)).convert("RGB")
                    topic_s5_rendered = True
                elif topic_id == 6:
                    from .aura_cardnews_s5_topic6_builder import AuraCardnewsS5Topic6Builder
                    AuraCardnewsS5Topic6Builder().build_s5_ending_card(str(temp_s5_path), copy_data=s5_copy)
                    rendered_slide = Image.open(str(temp_s5_path)).convert("RGB")
                    topic_s5_rendered = True
                elif topic_id == 7:
                    from .aura_cardnews_s5_topic7_builder import AuraCardnewsS5Topic7Builder
                    AuraCardnewsS5Topic7Builder().build_s5_ending_card(str(temp_s5_path), copy_data=s5_copy)
                    rendered_slide = Image.open(str(temp_s5_path)).convert("RGB")
                    topic_s5_rendered = True
                elif topic_id == 8:
                    from .aura_cardnews_s5_topic8_builder import AuraCardnewsS5Topic8Builder
                    AuraCardnewsS5Topic8Builder().build_s5_ending_card(str(temp_s5_path), copy_data=s5_copy)
                    rendered_slide = Image.open(str(temp_s5_path)).convert("RGB")
                    topic_s5_rendered = True
            except Exception as e:
                logger.warning(f"⚠️ [Slide 5] 주제별 전용 S5 빌더 실행 실패 ({e}) -> 기본 타이포그래피 모드로 폴백")

            if not topic_s5_rendered:
                logger.info(f"🖋️ [AuraCardnewsProducer] Playwright 골든 타이포그래피 합성 ({slide_num}/5)...")
                rendered_slide = self.typography_engine.render_slide(
                    bg_image=base_photo,
                    card_data=card_data,
                    slide_idx=slide_num,
                    total_slides=5
                )
        else:
            # 2. 타이포그래피 합성 (1080x1350)
            logger.info(f"🖋️ [AuraCardnewsProducer] Playwright 골든 타이포그래피 합성 ({slide_num}/5)...")
            rendered_slide = self.typography_engine.render_slide(
                bg_image=base_photo,
                card_data=card_data,
                slide_idx=slide_num,
                total_slides=5
            )

        # 3. 바탕화면 타겟 폴더 준비 (기존 지정 폴더 없으면 최신 폴더 또는 신규 생성)
        if target_dir is None:
            base_aura = AuraCardnewsStorage.get_base_dir()
            existing_folders = sorted(base_aura.glob(f"아우라_*{theme_code}*"), key=lambda p: p.stat().st_mtime, reverse=True)
            if existing_folders and (time.time() - existing_folders[0].stat().st_mtime) < 1800:
                target_dir = existing_folders[0]
            else:
                target_dir = AuraCardnewsStorage.create_target_directory(theme_code=theme_code, lang="KO", theme_title=theme_name)

        saved_path = AuraCardnewsStorage.save_slide_image(
            image=rendered_slide,
            slide_num=slide_num,
            target_dir=target_dir
        )

        # 워크스페이스 직관 확인용 저장
        ws_current = Path(__file__).resolve().parent / f"current_slide_{slide_num}.png"
        rendered_slide.save(str(ws_current), "PNG", quality=95)

        # 4. metadata.json 갱신
        meta_path = AuraCardnewsStorage.save_metadata(
            target_dir=target_dir,
            theme_code=theme_code,
            theme_title=theme_name,
            image_paths=[str(p) for p in sorted(target_dir.glob("slide_*.png"))],
            guide_file_path=str(target_dir / "SNS_포스팅_가이드_KO.txt"),
            lang="KO"
        )

        result = {
            "success": True,
            "theme_name": theme_name,
            "theme_code": theme_code,
            "output_dir": str(target_dir),
            "slide_num": slide_num,
            "slide_path": str(saved_path),
            "metadata_path": str(meta_path)
        }
        logger.info(f"🎉 [완성] {slide_num}번 카드 바탕화면 저장 완료: {saved_path}")
        return result

    def produce_cardnews(
        self,
        topic_id: int = 1,
        master_seed: Optional[int] = None,
        target_dir: Optional[Path] = None,
        fashion_id: Optional[int] = None,
        copy_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        🚀 [5장 풀세트 원스톱 자동 생산 - 제미나이 100% 실시간 자율 창작 연동]
        """
        # 전용 모듈형 파이프라인으로 라우팅 (주제 5, 6, 7, 8)
        if topic_id == 5:
            from .aura_cardnews_topic5_pipeline import AuraCardnewsTopic5Pipeline
            return AuraCardnewsTopic5Pipeline().run_pipeline(target_dir=str(target_dir) if target_dir else None, copy_data=copy_data, seed=master_seed)
        elif topic_id == 6:
            from .aura_cardnews_topic6_pipeline import AuraCardnewsTopic6Pipeline
            return AuraCardnewsTopic6Pipeline().run_pipeline(target_dir=str(target_dir) if target_dir else None, copy_data=copy_data, seed=master_seed)
        elif topic_id == 7:
            from .aura_cardnews_topic7_pipeline import AuraCardnewsTopic7Pipeline
            return AuraCardnewsTopic7Pipeline().run_pipeline(outfit_id=fashion_id, target_dir=str(target_dir) if target_dir else None, seed=master_seed)
        elif topic_id == 8:
            from .aura_cardnews_topic8_pipeline import AuraCardnewsTopic8Pipeline
            return AuraCardnewsTopic8Pipeline().run_pipeline(outfit_id=fashion_id, target_dir=str(target_dir) if target_dir else None, copy_data=copy_data)

        scenario = self.scenario_director.get_scenario(topic_id=topic_id, fashion_id=fashion_id)
        chosen_fashion = scenario.get("fashion_preset", {})
        chosen_fashion_id = chosen_fashion.get("id")
        theme_code = scenario.get("theme_code", "escape_call")
        theme_name = scenario.get("theme_name", "소개팅 긴급 탈출 전화")
        slides = scenario.get("slides", [])

        if target_dir is None:
            target_dir = AuraCardnewsStorage.create_target_directory(theme_code=theme_code, lang="KO", theme_title=theme_name)
        elif isinstance(target_dir, str):
            target_dir = Path(target_dir)

        fashion_title = f" [{chosen_fashion.get('name_ko')}]" if chosen_fashion else ""
        logger.info(f"🚀 [AuraCardnewsProducer] '{theme_name}'{fashion_title} 5장 풀세트 카드뉴스 생산 가동 -> {target_dir}")

        # 제미나이 100% 실시간 카피 창작 (1회 호출)
        if not copy_data:
            logger.info(f"🤖 [AuraCardnewsProducer] 주제 #{topic_id} 제미나이 실시간 AI 카피라이터 가동...")
            copy_data = self.copywriter.generate_cardnews_copy(topic_id=topic_id, outfit=chosen_fashion)

        slide_paths = []
        for s_idx in range(1, len(slides) + 1):
            logger.info(f"📸 [{s_idx}/{len(slides)}] 카드뉴스 슬라이드 생성 중 (제미나이 카피 주입)...")
            res = self.produce_slide(
                slide_num=s_idx,
                topic_id=topic_id,
                master_seed=master_seed,
                target_dir=target_dir,
                fashion_id=chosen_fashion_id,
                copy_data=copy_data
            )
            slide_paths.append(res["slide_path"])

        # 7대 SNS 포스팅 가이드 완결 생성 (AuraSNSGuideMaster 연동)
        from .aura_sns_guide_master import AuraSNSGuideMaster
        guide_content = AuraSNSGuideMaster.build_cardnews_guide(
            topic_id=topic_id,
            theme_name=theme_name,
            theme_code=theme_code,
            copy_data=copy_data
        )

        guide_path = target_dir / "SNS_포스팅_가이드_KO.txt"
        with open(guide_path, "w", encoding="utf-8") as f:
            f.write(guide_content)
        logger.info(f"✅ SNS 포스팅 가이드 생성 완료: {guide_path}")

        meta_path = AuraCardnewsStorage.save_metadata(
            target_dir=target_dir,
            theme_code=theme_code,
            theme_title=theme_name,
            image_paths=slide_paths,
            guide_file_path=str(guide_path),
            lang="KO"
        )

        result = {
            "success": True,
            "theme_name": theme_name,
            "theme_code": theme_code,
            "output_dir": str(target_dir),
            "total_slides": len(slide_paths),
            "slides": slide_paths,
            "slide_paths": slide_paths,
            "guide_path": str(guide_path),
            "metadata_path": str(meta_path)
        }
        # 🧹 다음 숏폼/카드뉴스 대기 작업을 위한 VRAM 캐시 즉시 완전 방출
        try:
            self.wan_client.free_vram()
        except Exception:
            pass

        logger.info(f"🎉 [성공] '{theme_name}' 5장 카드뉴스 풀세트 완벽 생성 완료: {target_dir}")
        return result

    def produce_slide_1(self, topic_id: int = 1, master_seed: Optional[int] = None) -> Dict[str, Any]:
        return self.produce_slide(slide_num=1, topic_id=topic_id, master_seed=master_seed)

    def produce_slide_2(self, topic_id: int = 1, master_seed: Optional[int] = None) -> Dict[str, Any]:
        return self.produce_slide(slide_num=2, topic_id=topic_id, master_seed=master_seed)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    producer = AuraCardnewsProducer()
    res = producer.produce_slide_1(topic_id=1)
    print("RESULT:", res)
