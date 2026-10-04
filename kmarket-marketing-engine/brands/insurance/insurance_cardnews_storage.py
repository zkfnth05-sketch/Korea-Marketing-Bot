# -*- coding: utf-8 -*-
"""
InsuranceCardnewsStorage - 🛡️ [보험 리밸런스 5장 카드뉴스 패키지 바탕화면 전용 저장 관리자]
========================================================================================
• 역할:
  - 1080x1350 완성형 5장 슬라이드를 바탕화면 전용 폴더에 번호순으로 안전 패키징
  - 인스타그램/페이스북 업로드 캡션 텍스트 파일(00_인스타_페이스북_업로드_본문.txt) 자동 동봉
  - 이전 임시 생성물 자동 정리 및 고해상도 PNG 무손실 보관
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from PIL import Image

logger = logging.getLogger("InsuranceCardnewsStorage")


class InsuranceCardnewsStorage:
    """🛡️ 보험 리밸런스 5장 카드뉴스 전용 바탕화면 패키징 관리자"""

    DESKTOP_PATH = Path(r"C:\Users\zkfnt\Desktop")
    BASE_OUTPUT_DIR = DESKTOP_PATH / "한국 카드뉴스_산출물" / "보험"

    def __init__(self):
        self.BASE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.desktop_dir = self.BASE_OUTPUT_DIR

    def get_topic_package_dir(self, topic_id: int, theme_name: str, create_new: bool = False) -> Path:
        """주제별 바탕화면 전용 패키지 폴더 경로 반환 (최근 동일 주제 폴더가 있으면 재사용하여 1~5장 한 폴더에 집약)"""
        safe_theme = "".join([c for c in theme_name if c.isalnum() or c in (" ", "_", "-")]).strip().replace(" ", "_")
        
        if not create_new:
            import time
            existing = sorted(self.BASE_OUTPUT_DIR.glob(f"보험_{topic_id:02d}_*"), key=lambda p: p.stat().st_mtime, reverse=True)
            if existing and (time.time() - existing[0].stat().st_mtime) < 7200:
                return existing[0]

        dt_str = datetime.now().strftime("%Y%m%d_%H%M")
        folder_name = f"보험_{topic_id:02d}_{safe_theme}_{dt_str}"
        target_dir = self.BASE_OUTPUT_DIR / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir

    def save_slide_image(self, img: Image.Image, target_dir: Path, slide_num: int) -> Path:
        """개별 슬라이드 고해상도 PNG 파일 저장 (예: slide_1.png)"""
        filename = f"slide_{slide_num}.png"
        out_path = target_dir / filename
        img.save(out_path, format="PNG", quality=95)
        logger.info(f"💾 [InsuranceStorage] 슬라이드 {slide_num} 저장 완료: {out_path}")
        return out_path

    def save_caption_file(self, caption_text: str, target_dir: Path, topic_id: int, theme_name: str) -> Path:
        """인스타/페북 업로드용 캡션 및 안내 파일 동봉 저장"""
        caption_path = target_dir / "00_인스타_페이스북_업로드_가이드.txt"
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = (
            f"========================================================\n"
            f"🛡️ [보험 리밸런스] 5장 카드뉴스 완성 패키지 (주제 #{topic_id} {theme_name})\n"
            f"⏰ 생성 일시: {now_str}\n"
            f"========================================================\n\n"
            f"📱 [인스타그램 / 페이스북 업로드 캡션 복사본]:\n\n"
            f"{caption_text}\n\n"
            f"========================================================\n"
            f"📁 포함 파일 목록:\n"
            f"  - slide_1.png (1080x1350 킬러 후킹 표지)\n"
            f"  - slide_2.png (1080x1350 현실 공감)\n"
            f"  - slide_3.png (1080x1350 팩트/비교 분석)\n"
            f"  - slide_4.png (1080x1350 실전 솔루션)\n"
            f"  - slide_5.png (1080x1350 엔딩 & 검색 CTA)\n"
            f"========================================================\n"
        )
        with open(caption_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"📄 [InsuranceStorage] 캡션 가이드 파일 저장 완료: {caption_path}")
        return caption_path
