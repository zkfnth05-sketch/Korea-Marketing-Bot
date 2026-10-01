# -*- coding: utf-8 -*-
"""
AuraCardnewsStorage - 📁 [Aura 카드뉴스 바탕화면 전용 저장 및 패키징 매니저]
=============================================================================
• 역할:
  - 바탕화면 [C:/Users/zkfnt/Desktop/한국 카드뉴스_산출물/아우라/] 전용 디렉터리 관리
  - 이지텍스 산출물(C:/Users/zkfnt/Desktop/카드뉴스_산출물/이지텍스)과 100% 동일한 구조:
    ➔ 아우라_KO_{theme_code}_{YYYYMMDD_HHMM}/
  - 내부 산출물 파일 7종 무결성 패키징:
    1. slide_1.png (커버)
    2. slide_2.png (공감)
    3. slide_3.png (실전팁)
    4. slide_4.png (앱 솔루션)
    5. slide_5.png (논쟁/CTA)
    6. metadata.json (테마, 브랜드 정보, 파일 경로 일체)
    7. SNS_포스팅_가이드_KO.txt (네이버 블로그, 네이버 카페, 인스타, 스레드, 페이스북, 텔레그램 포함)
"""

import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from PIL import Image, ImageDraw, ImageFont

try:
    from brands.aura.aura_cardnews_guide_builder import AuraCardnewsGuideBuilder
except ImportError:
    from aura_cardnews_guide_builder import AuraCardnewsGuideBuilder

logger = logging.getLogger("AuraCardnewsStorage")


class AuraCardnewsStorage:
    """💖 Aura 카드뉴스 바탕화면 전용 저장 매니저"""

    DESKTOP_PATH = Path(r"C:\Users\zkfnt\Desktop")
    BASE_OUTPUT_DIR = DESKTOP_PATH / "한국 카드뉴스_산출물" / "아우라"

    def __init__(self):
        self.BASE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    THEME_NAME_MAP = {
        "escape_call": "01_소개팅긴급탈출전화",
        "realtime_subtitles": "02_실시간AI자막통화",
        "vip_gate_5050": "03_5050_VIP정원제",
        "cheongdam_photo": "04_청담동화보보정",
        "value_balance": "05_가치관밸런스매칭",
        "smart_opener": "06_AI첫대화비서",
        "ai_icebreaker": "06_AI첫대화비서",
        "ai_charm_scanner": "07_AI매력상궁합진단",
        "safe_radar_500m": "08_500m안심레이더"
    }

    @classmethod
    def get_base_dir(cls) -> Path:
        """기본 저장 루트 디렉터리 반환 및 생성"""
        cls.BASE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        return cls.BASE_OUTPUT_DIR

    @classmethod
    def create_target_directory(cls, theme_code: str = "escape_call", lang: str = "KO", theme_title: Optional[str] = None) -> Path:
        """
        주제 번호와 한국어 이름이 명확하게 들어간 직관적인 바탕화면 타겟 폴더 생성
        예: C:/Users/zkfnt/Desktop/한국 카드뉴스_산출물/아우라/아우라_01_소개팅긴급탈출전화_20261001_0853
        """
        cls.BASE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        dt_str = datetime.now().strftime("%Y%m%d_%H%M")
        
        # 한국어 주제 레이블 추출
        topic_label = cls.THEME_NAME_MAP.get(theme_code)
        if not topic_label:
            if theme_title:
                clean_title = "".join(c for c in theme_title if c.isalnum() or c in ("_", "-"))
                topic_label = clean_title
            else:
                topic_label = theme_code

        folder_name = f"아우라_{topic_label}_{dt_str}"
        target_dir = cls.BASE_OUTPUT_DIR / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 [AuraStorage] 직관적인 산출물 폴더 준비 완료: {target_dir}")
        return target_dir

    @classmethod
    def save_slide_image(cls, image: Union[Image.Image, Path, str], slide_num: int, target_dir: Path) -> Path:
        """개별 슬라이드 이미지 저장 (slide_1.png ~ slide_5.png)"""
        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / f"slide_{slide_num}.png"
        
        if isinstance(image, Image.Image):
            image.save(str(file_path), "PNG", quality=95)
        elif isinstance(image, (Path, str)):
            # 기존 이미지 파일 경로인 경우 복사 또는 로드 후 저장
            img = Image.open(str(image))
            img.save(str(file_path), "PNG", quality=95)
        else:
            raise ValueError(f"지원하지 않는 이미지 형식입니다: {type(image)}")
            
        logger.info(f"  💾 [AuraStorage] 슬라이드 저장 완료: {file_path.name}")
        return file_path

    @classmethod
    def save_metadata(
        cls,
        target_dir: Path,
        theme_code: str,
        theme_title: str,
        image_paths: List[str],
        guide_file_path: str,
        lang: str = "ko"
    ) -> Path:
        """
        이지텍스/케이마켓과 동일한 포맷의 metadata.json 생성 및 저장
        """
        target_dir.mkdir(parents=True, exist_ok=True)
        meta_path = target_dir / "metadata.json"
        
        metadata_payload = {
            "service_id": "aura",
            "brand_name": "Aura AI 데이팅",
            "search_keyword": "아우라AI데이팅",
            "landing_url": "https://aura-ai-dating.vercel.app/lounge",
            "lang": lang.lower(),
            "theme_code": theme_code,
            "theme_title": theme_title,
            "total_slides": len(image_paths),
            "image_paths": image_paths,
            "guide_file": str(guide_file_path),
            "folder_path": str(target_dir),
            "timestamp": int(time.time()),
            "channels_supported": [
                "naver_post",
                "naver_blog",
                "naver_cafe",
                "instagram_carousel",
                "threads",
                "facebook",
                "telegram"
            ]
        }
        
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata_payload, f, ensure_ascii=False, indent=2)
            
        logger.info(f"  📋 [AuraStorage] metadata.json 저장 완료: {meta_path.name}")
        return meta_path

    @classmethod
    def save_sns_guide(cls, guide_text: str, target_dir: Path, lang: str = "KO") -> Path:
        """SNS 포스팅 가이드 텍스트 파일 저장 (SNS_포스팅_가이드_KO.txt)"""
        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / f"SNS_포스팅_가이드_{lang.upper()}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(guide_text)
        logger.info(f"  📄 [AuraStorage] SNS 가이드 저장 완료: {file_path.name}")
        return file_path

    @classmethod
    def save_guide_file(
        cls,
        target_dir: Path,
        theme_code: str,
        theme_name: str,
        slides_data: List[Dict[str, Any]],
        lang: str = "KO"
    ) -> Path:
        """AuraCardnewsGuideBuilder를 호출하여 네이버 포스트/블로그/카페 포함 가이드 자동 생성 및 저장"""
        from .aura_cardnews_guide_builder import AuraCardnewsGuideBuilder
        guide_text = AuraCardnewsGuideBuilder.build_full_guide(
            theme_code=theme_code,
            theme_name=theme_name,
            slides_data=slides_data
        )
        return cls.save_sns_guide(guide_text=guide_text, target_dir=target_dir, lang=lang)

    @classmethod
    def save_complete_package(
        cls,
        slides: List[Union[Image.Image, Path, str]],
        theme_code: str = "escape_call",
        theme_title: str = "소개팅 긴급 탈출 전화",
        slides_data: Optional[List[Dict[str, Any]]] = None,
        custom_guide_text: Optional[str] = None,
        lang: str = "KO"
    ) -> Dict[str, Any]:
        """
        [이지텍스 규격 100% 동일 구현]
        5장 슬라이드 이미지 + metadata.json + 네이버 포함 SNS 가이드 텍스트를
        바탕화면 타겟 폴더에 패키징하여 일괄 저장
        """
        target_dir = cls.create_target_directory(theme_code=theme_code, lang=lang)
        slide_paths = []

        # 1. 5장 슬라이드 이미지 저장
        for idx, img_source in enumerate(slides[:5], start=1):
            s_path = cls.save_slide_image(image=img_source, slide_num=idx, target_dir=target_dir)
            slide_paths.append(str(s_path))

        # 2. 네이버 블로그/카페 포함 SNS 가이드 텍스트 생성 및 저장
        if custom_guide_text:
            guide_text = custom_guide_text
        else:
            guide_text = AuraCardnewsGuideBuilder.build_full_guide(
                theme_code=theme_code,
                theme_name=theme_title,
                slides_data=slides_data or []
            )
        guide_path = cls.save_sns_guide(guide_text=guide_text, target_dir=target_dir, lang=lang)

        # 3. metadata.json 저장
        meta_path = cls.save_metadata(
            target_dir=target_dir,
            theme_code=theme_code,
            theme_title=theme_title,
            image_paths=slide_paths,
            guide_file_path=str(guide_path),
            lang=lang
        )

        result = {
            "success": True,
            "output_dir": str(target_dir),
            "slide_paths": slide_paths,
            "metadata_path": str(meta_path),
            "guide_path": str(guide_path),
            "total_slides": len(slide_paths)
        }
        logger.info(f"✅ [AuraStorage] 이지텍스 규격 바탕화면 카드뉴스 패키지 저장 성공! -> {target_dir}")
        return result


if __name__ == "__main__":
    import sys
    # Windows CP949 콘솔 안전 인코딩 설정
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # 단독 테스트 실행: 더미 5장 슬라이드로 바탕화면 저장 테스트
    logging.basicConfig(level=logging.INFO)
    logger.info("[테스트] Aura 카드뉴스 바탕화면 저장 매니저 검증 시작...")
    
    # 1080x1350 규격 5장 더미 이미지 생성
    dummy_slides = []
    colors = [(20, 20, 30), (30, 20, 40), (20, 30, 40), (40, 20, 30), (25, 25, 35)]
    for i, c in enumerate(colors, start=1):
        img = Image.new("RGB", (1080, 1350), color=c)
        draw = ImageDraw.Draw(img)
        draw.text((100, 600), f"Aura Cardnews Slide {i}", fill=(255, 215, 0))
        dummy_slides.append(img)
        
    res = AuraCardnewsStorage.save_complete_package(
        slides=dummy_slides,
        theme_code="escape_call",
        theme_title="소개팅 긴급 탈출 전화",
        slides_data=[
            {"title": "소개팅 나갔는데 분위기 싸할 때 1초 탈출법", "subtitle": "억지로 버티지 마세요", "bullets": ["실물 괴리", "자연스러운 탈출", "비밀 공개"]},
            {"title": "어색한 자리 억지로 버티면 손해", "subtitle": "주말 시간 낭비", "bullets": ["거절 멘트 어색", "화장실 카톡", "갑작스러운 핑계"]},
            {"title": "누구도 반박 못할 긴급 업무 호출", "subtitle": "회사 팀장님 명분", "bullets": ["업무 호출이 최고", "정중한 사과", "자존심 지킴"]},
            {"title": "아우라 AI 긴급 탈출 전화 버튼", "subtitle": "10초 뒤 진짜 전화", "bullets": ["실제 음성 벨소리", "자연스러운 시나리오", "1초 매너 런"]},
            {"title": "소개팅 분위기 싸할 때 바로 런 vs 억지 식사?", "subtitle": "네이버에 아우라AI데이팅 검색", "bullets": []}
        ]
    )
    print("저장 완료 결과:", json.dumps(res, indent=2, ensure_ascii=False))

