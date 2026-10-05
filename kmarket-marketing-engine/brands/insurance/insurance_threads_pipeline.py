# -*- coding: utf-8 -*-
"""
Insurance Threads Pipeline (🧵 🛡️ 보험 리밸런스 전용 스레드 독립 파이프라인)
========================================================================
- 브랜드: 🛡️ 보험 리밸런스 (InsureBalance)
- 전용 계정: @goldmomofficial
- 공식 검색어: '보험 리밸런스' (띄어쓰기 필수, 불변)
- 랜딩 URL: https://insure-rebalance.vercel.app/
- 역할:
  1. 보험 리밸런스 전용 카드뉴스(4~5장 이미지) 또는 보험료 절약 텍스트 타래 패키징
  2. 제미나이(Gemini) 심의 준수 자율 집필 엔진을 통한 300~450자 풍성한 본문 캡션 탑재
  3. 스레드(Threads) 독립 레고 블록 발행기(InsuranceThreadsPublisher)를 통한 100% 무인 송출
  4. 첫 번째 타래 댓글로 공식 검색어 및 랜딩 링크 자동 체인 연동
  5. 송출 히스토리 및 증빙 스크린샷 독립 보관
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("InsuranceThreadsPipeline")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from brands.insurance.insurance_cardnews_gemini_copywriter import InsuranceCardnewsGeminiCopywriter


class InsuranceThreadsPipeline:
    """🛡️ 보험 리밸런스 전용 스레드 완전 독립 레고 블록 파이프라인"""

    BRAND = "insurance"
    BRAND_NAME = "보험 리밸런스"
    OFFICIAL_SEARCH_KEYWORD = "보험 리밸런스"
    LANDING_URL = "https://insure-rebalance.vercel.app/"

    def __init__(self, headless: bool = True):
        self.headless = headless
        from brands.insurance.insurance_threads_publisher import InsuranceThreadsPublisher
        self.publisher = InsuranceThreadsPublisher(headless=self.headless)
        self.copywriter = InsuranceCardnewsGeminiCopywriter()

    async def run_pipeline(
        self,
        cardnews_folder: Optional[str] = None,
        custom_caption: Optional[str] = None,
        topic_id: int = 1,
        theme_name: str = "4세대 실손보험 전환 팩트 체크"
    ) -> Dict[str, Any]:
        """보험 리밸런스 전용 스레드 자동 송출 실행 (순수 제미나이 심의 준수 캡션 탑재)"""
        logger.info(f"🚀 [{self.BRAND_NAME}] 스레드 독립 파이프라인 가동 (주제 #{topic_id}: {theme_name})")

        image_paths = []
        caption = custom_caption or ""

        # 1. 특정 카드뉴스 폴더가 지정된 경우
        if cardnews_folder:
            target_dir = Path(cardnews_folder)
            if target_dir.exists():
                for i in range(1, 10):
                    f = target_dir / f"slide_{i}.png"
                    if f.exists():
                        image_paths.append(str(f.resolve()))
                
                # 00_SNS_포스팅_가이드_최신트렌드.txt 또는 SNS_포스팅_가이드_KO.txt 확인
                for guide_name in ["00_SNS_포스팅_가이드_최신트렌드.txt", "SNS_포스팅_가이드_KO.txt"]:
                    guide_file = target_dir / guide_name
                    if guide_file.exists() and not caption:
                        try:
                            with open(guide_file, "r", encoding="utf-8") as gf:
                                content = gf.read()
                                # 스레드 또는 인스타 섹션 추출 시도
                                if "[5] 🧵 스레드 (Threads)" in content:
                                    s_part = content.split("[5] 🧵 스레드 (Threads)")[1].split("--------------------------------------------------------------------------------")[1]
                                    lines = [l.strip() for l in s_part.split("\n") if l.strip() and not l.startswith("📌") and not l.startswith("💬") and not l.startswith("[")]
                                    if lines:
                                        caption = "\n\n".join(lines[:4])
                                elif "[4] 📸 인스타그램 (Instagram)" in content:
                                    i_part = content.split("[4] 📸 인스타그램 (Instagram)")[1].split("--------------------------------------------------------------------------------")[1]
                                    lines = [l.strip() for l in i_part.split("\n") if l.strip() and not l.startswith("📌") and not l.startswith("[")]
                                    if lines:
                                        caption = "\n\n".join(lines[:5])
                        except Exception as e:
                            logger.warning(f"가이드 파일 파싱 경고: {e}")

        # 2. 캡션이 없는 경우 순수 제미나이 심의 준수 카피라이터 가동
        if not caption or len(caption) < 50:
            logger.info(f"✍️ [InsuranceThreadsPipeline] 순수 제미나이 심의 준수 캡션 생성 시작 (주제 #{topic_id})...")
            try:
                gemini_res = self.copywriter.generate_copy_for_topic(topic_id=topic_id, theme_name=theme_name)
                caption = gemini_res.get("sns_caption", "")
            except Exception as ge:
                logger.warning(f"⚠️ 제미나이 캡션 생성 예외: {ge}")

        # 3. 폴백 안전 캡션 (300~450자 풍성한 심의 준수형)
        if not caption:
            caption = (
                f"🛡️ [보험 리밸런스 팩트체크 리포트] #{topic_id} {theme_name}\n\n"
                f"매달 통장에서 나가는 보험료, 과연 현재 보장 내역과 내 상황에 맞게 최적화되어 있을까요?\n\n"
                f"📌 금융소비자가 꼭 알아야 할 3대 점검 팩트:\n"
                f"1️⃣ 4세대 실손보험은 병원 이용이 적을 경우 기존 1~3세대 대비 월 보험료를 합리적으로 절감할 수 있습니다. (급여 20%/비급여 30% 자기부담금 기준)\n"
                f"2️⃣ 실손 및 운전자 담보는 '비례보상' 원칙이 적용되므로 중복 가입 시 불필요한 보험료 낭비가 발생합니다.\n"
                f"3️⃣ 34개 생명·손해보험사 공시 가격표를 객관적으로 비교하여 불필요한 특약 거품을 덜어내세요.\n\n"
                f"👉 지금 네이버에 '{self.OFFICIAL_SEARCH_KEYWORD}'을 검색해보세요!\n"
                f"🔗 공식 0.1초 자가진단: {self.LANDING_URL}\n\n"
                f"※ 본 콘텐츠는 금융소비자의 이해를 돕기 위한 정보 제공 목적으로 작성되었으며, 개별 약관 및 가입 조건에 따라 달라질 수 있습니다.\n\n"
                f"#보험리밸런스 #실손보험 #4세대실손 #보험비교 #보험다이어트 #보험료줄이기"
            )

        # 4. 첫 번째 타래 댓글 체인 (공식 검색어 & 랜딩 URL)
        first_reply = (
            f"🛡️ 매달 줄줄 새는 숨은 보험료 3분 진단\n"
            f"네이버에 '{self.OFFICIAL_SEARCH_KEYWORD}' 검색해보세요!\n"
            f"👉 {self.LANDING_URL}"
        )

        logger.info(f"📝 [본문 캡션 미리보기 ({len(caption)}자)]:\n{caption[:150]}...")
        logger.info(f"💬 [1번 타래 댓글]: {first_reply}")

        # 5. 스레드 독립 퍼블리셔 송출
        result = await self.publisher.publish_thread(
            caption=caption,
            image_paths=image_paths,
            first_reply_text=first_reply
        )
        return result


async def main():
    pipeline = InsuranceThreadsPipeline(headless=False)
    res = await pipeline.run_pipeline()
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
