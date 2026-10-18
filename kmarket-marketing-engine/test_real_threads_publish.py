# -*- coding: utf-8 -*-
"""
스레드(Threads) 실기 5장 카드뉴스 송출 및 1번 타래 댓글 완결 검증
==================================================================
"""
import os
import sys
import json
import asyncio
import logging
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RealThreadsTest")

CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))

from brands.aura.aura_threads_publisher import AuraThreadsPublisher

async def test_threads():
    # 바탕화면 5장 카드뉴스 폴더
    desktop = Path(os.environ.get("USERPROFILE", "C:/Users/zkfnt")) / "Desktop" / "한국 카드뉴스_산출물" / "아우라"
    target_folder = None
    if desktop.exists():
        candidates = []
        for d in desktop.iterdir():
            if d.is_dir():
                slides = list(d.glob("slide_*.png"))
                if len(slides) >= 5:
                    candidates.append((d.stat().st_mtime, d))
        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            target_folder = candidates[0][1]

    if not target_folder:
        logger.error("❌ 5장 완제품 카드뉴스 폴더가 없습니다.")
        return

    images = [str(target_folder / f"slide_{i}.png") for i in range(1, 6)]
    logger.info(f"📂 [스레드 송출 대상 5장 카드뉴스] {target_folder.name} ({len(images)}장)")

    caption = (
        "📍 [500m 안심 레이더 & 2030 실시간 소개팅]\n\n"
        "집 주소 노출될까 봐 불안하셨죠?\n"
        "내 집 앞 500m 안심 지오펜싱 보안으로 안전하게!\n\n"
        "거리와 취향까지 딱 맞는 내 반경 500m 인연을 지금 확인해보세요 ✨\n\n"
        "#아우라AI데이팅 #소개팅 #데이팅앱 #안심매칭 #2030"
    )

    first_reply = (
        "💖 2030 매력 진단 & AI 매칭 1분 무료 리포트\n"
        "네이버에 '아우라AI데이팅' 한번 검색해보세요!\n"
        "👉 https://aura-ai-dating.vercel.app/"
    )

    pub = AuraThreadsPublisher(headless=True)
    res = await pub.publish_thread(
        caption=caption,
        image_paths=images,
        first_reply_text=first_reply
    )

    logger.info("=" * 60)
    logger.info(f"🎉 [스레드 송출 결과] {json.dumps(res, ensure_ascii=False, indent=2)}")
    logger.info("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_threads())
