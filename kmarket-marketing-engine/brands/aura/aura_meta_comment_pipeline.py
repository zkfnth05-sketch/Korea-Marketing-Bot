# -*- coding: utf-8 -*-
"""
💖 [Aura 전용] Meta 릴스 발행 후 인스타 & 페이스북 댓글 연속 집행 오케스트레이터 (독립 레고 블록)
=====================================================================================================
- 핵심 역할:
  1. [비동기 정공법] run_aura_meta_comments_async() : 이미 실행 중인 이벤트 루프 안에서
     인스타/페이스북 댓글러의 *_async() 메서드를 직접 await 호출 (asyncio.run 중첩 충돌 0%)
  2. [동기 하위호환] run_aura_meta_comments() : 기존 스케줄러/파이프라인 100% 호환.
     - 실행 중인 루프가 없으면 asyncio.run() 안전 호출
     - 실행 중인 루프가 있으면 별도 스레드에서 asyncio.run() 구동 (RuntimeError: asyncio.run() cannot be called 방지)
- 원칙: Rule 1 (독립 레고 블록), Rule 5 (땜질 금지/근본 해결), Rule 6 (24시간 무인 자율 구동)
"""
import sys
import asyncio
import logging
import threading
from pathlib import Path
from typing import Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logger = logging.getLogger("AuraMetaCommentPipeline")
if not logger.handlers:
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("[%(asctime)s] [AuraMetaComment] %(message)s"))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from brands.aura.aura_instagram_commenter import AuraInstagramCommenter
from brands.aura.aura_facebook_commenter import AuraFacebookCommenter


# ======================================================================
# [1] 비동기 정공법 엔진 (이벤트 루프 내부에서 직접 await)
# ======================================================================
async def run_aura_meta_comments_async() -> Dict[str, Any]:
    """💖 아우라 릴스 발행 직후 인스타그램 및 페이스북에 단독 첫 댓글을 비동기로 자율 집행

    - 이미 실행 중인 이벤트 루프 안에서 호출해도 안전합니다 (asyncio.run 중첩 호출 없음).
    - 인스타그램: AuraInstagramCommenter.post_comment_on_latest_reel_async() 직접 await
    - 페이스북  : AuraFacebookCommenter.post_comment_on_latest_post_async() 직접 await
    """
    logger.info("🚀 [Aura Meta Comment] 인스타그램 & 페이스북 첫 댓글 비동기 파이프라인 가동...")
    results: Dict[str, Any] = {}

    # 1. 인스타그램 댓글 (비동기 직접 호출)
    try:
        insta = AuraInstagramCommenter()
        results["instagram"] = await insta.post_comment_on_latest_reel_async()
        logger.info(f"✅ [Aura Meta Comment] 인스타그램 댓글 결과: {results['instagram']}")
    except Exception as e:
        logger.error(f"❌ 아우라 인스타 댓글 예외: {e}")
        results["instagram"] = {"status": "error", "message": str(e)}

    # 2. 페이스북 댓글 (비동기 직접 호출)
    try:
        fb = AuraFacebookCommenter()
        results["facebook"] = await fb.post_comment_on_latest_post_async()
        logger.info(f"✅ [Aura Meta Comment] 페이스북 댓글 결과: {results['facebook']}")
    except Exception as e:
        logger.error(f"❌ 아우라 페이스북 댓글 예외: {e}")
        results["facebook"] = {"status": "error", "message": str(e)}

    logger.info(f"🎉 [Aura Meta Comment] 비동기 결과 요약: {results}")
    return results


# ======================================================================
# [2] 이벤트 루프 안전 감지 유틸
# ======================================================================
def _has_running_loop() -> bool:
    """현재 스레드에 이미 실행 중인 이벤트 루프가 있는지 판별"""
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


def _run_coro_in_new_thread(coro) -> Any:
    """실행 중인 루프가 있는 스레드에서 asyncio.run()을 안전하게 구동하기 위한 격리 스레드 실행기

    - 별도 스레드는 자체 이벤트 루프를 가지므로 asyncio.run() 중첩 RuntimeError가 발생하지 않습니다.
    - 원본 코루틴의 반환값/예외를 그대로 호출자에게 전달합니다.
    """
    box: Dict[str, Any] = {}

    def _worker():
        try:
            box["result"] = asyncio.run(coro)
        except BaseException as e:  # noqa: BLE001 - 원본 예외를 그대로 재전달
            box["error"] = e

    t = threading.Thread(target=_worker, name="AuraMetaCommentLoopBridge", daemon=True)
    t.start()
    t.join()

    if "error" in box:
        raise box["error"]
    return box.get("result")


# ======================================================================
# [3] 동기 하위호환 래퍼 (기존 스케줄러/파이프라인 100% 호환)
# ======================================================================
def run_aura_meta_comments() -> Dict[str, Any]:
    """💖 아우라 릴스 발행 직후 인스타그램 및 페이스북에 단독 첫 댓글을 자율 집행 (동기 인터페이스)

    - 실행 중인 이벤트 루프가 없으면 : asyncio.run()으로 안전 호출
    - 실행 중인 이벤트 루프가 있으면 : 별도 스레드에서 asyncio.run() 구동
      (RuntimeError: asyncio.run() cannot be called from a running event loop 100% 방지)
    """
    logger.info("🚀 [Aura Meta Comment] 인스타그램 & 페이스북 첫 댓글 동기 파이프라인 가동...")

    if _has_running_loop():
        logger.info("🔀 [Aura Meta Comment] 실행 중인 이벤트 루프 감지 ➔ 격리 스레드에서 안전 구동")
        try:
            return _run_coro_in_new_thread(run_aura_meta_comments_async())
        except Exception as e:
            logger.error(f"❌ [Aura Meta Comment] 격리 스레드 실행 예외: {e}")
            return {
                "instagram": {"status": "error", "message": str(e)},
                "facebook": {"status": "error", "message": str(e)},
            }

    try:
        return asyncio.run(run_aura_meta_comments_async())
    except Exception as e:
        logger.error(f"❌ [Aura Meta Comment] asyncio.run 실행 예외: {e}")
        return {
            "instagram": {"status": "error", "message": str(e)},
            "facebook": {"status": "error", "message": str(e)},
        }


if __name__ == "__main__":
    res = run_aura_meta_comments()
    print("집행 결과:", res)
