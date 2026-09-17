"""
Stock Runner (Stock Master AI 주식 AI 독립 실행 스크립트)
Usage:
    python run_stock.py           # 드라이런(테스트 모드)
    python run_stock.py --live    # 실제 라이브 발행 모드
"""

import sys
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from brands.stock.stock_pipeline import StockPipeline


def main():
    is_live = "--live" in sys.argv
    dry_run = not is_live

    print(f"\n==============================================")
    print(f"📈 Stock Master AI 주식 마케팅 파이프라인 가동 (Mode: {'LIVE' if is_live else 'DRY-RUN'})")
    print(f"==============================================\n")

    pipeline = StockPipeline(dry_run=dry_run)
    result = pipeline.run_full_daily_cycle()
    print("\n[가동 결과 요약]:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
