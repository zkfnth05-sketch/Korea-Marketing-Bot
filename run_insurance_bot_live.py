# -*- coding: utf-8 -*-
import asyncio
import sys
from pathlib import Path

# UTF-8 설정
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent
engine_dir = ROOT / "kmarket-marketing-engine"
if str(engine_dir) not in sys.path:
    sys.path.insert(0, str(engine_dir))

from brands.insurance.insurance_cafe_pipeline import InsuranceCafePipeline

async def main():
    print("="*80)
    print("🤖 [보험 리밸런스] 100% 무인 자율 스텔스 침투 봇 가동 (LIVE 실전 모드)")
    print("="*80)
    
    # 무인 봇 파이프라인 인스턴스 생성
    pipeline = InsuranceCafePipeline()
    
    # 봇 스스로 100% 자율 실행 (dry_run=False -> 실제 라이브 댓글 등록)
    result = await pipeline.run_daily_stealth_infiltration(dry_run=False)
    
    print("\n" + "="*80)
    print("🏁 [무인 봇 실행 결과 보고]")
    print(f"상태: {result.get('status')}")
    if result.get('status') == 'SUCCESS_POSTED':
        print(f"✅ 타깃 카페: {result['target_post']['cafe_name']}")
        print(f"✅ 타깃 게시글: {result['target_post']['title']}")
        print(f"✅ 게시글 URL: {result.get('article_url')}")
        print(f"✅ 봇이 등록한 댓글: {result.get('reply_text')}")
        print(f"✅ 증빙 스크린샷: {result.get('proof_screenshot')}")
    else:
        print(f"메시지: {result.get('message')}")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
