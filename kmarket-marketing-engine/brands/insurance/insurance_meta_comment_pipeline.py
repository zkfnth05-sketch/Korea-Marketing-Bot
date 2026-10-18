# -*- coding: utf-8 -*-
"""
🛡️ [보험 리밸런스 전용] Meta 릴스 발행 후 인스타 & 페이스북 댓글 연속 집행 오케스트레이터 (독립 레고 블록)
========================================================================================
- 비동기 정식 인터페이스: run_insurance_meta_comments_async()
- 동기 호환 인터페이스: run_insurance_meta_comments()
  → 이미 이벤트 루프가 돌고 있는 환경(Playwright async 컨텍스트 등)에서도
    RuntimeError("asyncio.run() cannot be called from a running event loop") 없이 안전 집행.
"""
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logger = logging.getLogger("InsuranceMetaCommentPipeline")
if not logger.handlers:
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("[%(asctime)s] [InsuranceMetaComment] %(message)s"))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from brands.insurance.insurance_instagram_commenter import InsuranceInstagramCommenter
from brands.insurance.insurance_facebook_commenter import InsuranceFacebookCommenter


async def run_insurance_meta_comments_async() -> Dict[str, Any]:
    """🛡️ 보험 릴스 발행 직후 인스타그램 및 페이스북에 단독 3단 첫 댓글을 자율 집행 (비동기 정식 경로)"""
    logger.info("🚀 [Insurance Meta Comment] 인스타그램 & 페이스북 첫 댓글 자율 파이프라인 가동 (async)...")
    results: Dict[str, Any] = {}

    # 1. 인스타그램 댓글
    try:
        insta = InsuranceInstagramCommenter()
        results["instagram"] = await insta.post_comment_on_latest_reel_async()
    except Exception as e:
        logger.error(f"❌ 보험 인스타 댓글 예외: {e}")
        results["instagram"] = {"status": "error", "message": str(e)}

    # 2. 페이스북 댓글
    try:
        fb = InsuranceFacebookCommenter()
        results["facebook"] = await fb.post_comment_on_latest_post_async()
    except Exception as e:
        logger.error(f"❌ 보험 페이스북 댓글 예외: {e}")
        results["facebook"] = {"status": "error", "message": str(e)}

    logger.info(f"🎉 [Insurance Meta Comment] 결과 요약: {results}")
    return results


def _run_coro_safely(coro) -> Any:
    """이미 이벤트 루프가 돌고 있어도 안전하게 코루틴을 완료시키는 범용 실행기.

    우선순위:
      1) 실행 중인 루프가 없으면 asyncio.run() 정상 경로
      2) 실행 중인 루프가 있으면 nest_asyncio 적용 후 run_until_complete
      3) nest_asyncio 부재 시 별도 스레드 + 신규 이벤트 루프에서 완료
    """
    try:
        running_loop = asyncio.get_running_loop()
    except RuntimeError:
        running_loop = None

    # 1) 실행 중인 루프 없음 → 표준 경로
    if running_loop is None:
        return asyncio.run(coro)

    # 2) 실행 중인 루프 존재 → nest_asyncio 로 루프 재진입 허용
    try:
        import nest_asyncio  # type: ignore

        nest_asyncio.apply(running_loop)
        logger.info("🔁 [Insurance Meta Comment] 실행 중 이벤트 루프 감지 → nest_asyncio 재진입 집행")
        return running_loop.run_until_complete(coro)
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"⚠️ nest_asyncio 재진입 실패, 스레드 우회로 전환: {e}")

    # 3) nest_asyncio 부재/실패 → 별도 스레드에서 신규 루프로 완료
    import threading

    box: Dict[str, Any] = {}

    def _worker() -> None:
        try:
            box["result"] = asyncio.run(coro)
        except BaseException as exc:  # noqa: BLE001
            box["error"] = exc

    logger.info("🧵 [Insurance Meta Comment] 실행 중 이벤트 루프 감지 → 별도 스레드 신규 루프 집행")
    th = threading.Thread(target=_worker, name="insurance-meta-comment", daemon=True)
    th.start()
    th.join()

    if "error" in box:
        raise box["error"]
    return box.get("result")


def run_insurance_meta_comments() -> Dict[str, Any]:
    """🛡️ 동기 호환 인터페이스.

    이미 이벤트 루프가 돌고 있는 환경에서도 RuntimeError 없이 안전하게 집행한다.
    """
    logger.info("🚀 [Insurance Meta Comment] 인스타그램 & 페이스북 첫 댓글 자율 파이프라인 가동 (sync)...")
    try:
        return _run_coro_safely(run_insurance_meta_comments_async())
    except Exception as e:
        logger.error(f"❌ [Insurance Meta Comment] 동기 래퍼 최종 예외: {e}")
        return {
            "instagram": {"status": "error", "message": str(e)},
            "facebook": {"status": "error", "message": str(e)},
        }


if __name__ == "__main__":
    res = run_insurance_meta_comments()
    print("집행 결과:", res)
