"""
All Brands Runner (3대 앱 24채널 독립 마케팅 공장 통합 가동기)
Usage:
    python run_all_brands.py           # 드라이런 전체 시뮬레이션
    python run_all_brands.py --live    # 실제 라이브 모드 순차 가동
"""

import sys
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from brands.aura.aura_pipeline import AuraPipeline
from brands.insurance.insurance_pipeline import InsurancePipeline
from brands.stock.stock_pipeline import StockPipeline


def main():
    is_live = "--live" in sys.argv
    dry_run = not is_live

    # ── [지식iN 3대 앱 동시 즉시 실행 모드] ──
    if "--kin-now" in sys.argv or "-kn" in sys.argv:
        print(f"\n========================================================")
        print(f"🎯 대한민국 3대 앱 네이버 지식iN 실시간 낚아채기 동시 가동")
        print(f"Mode: {'LIVE (실제 답변 등록)' if is_live else 'DRY-RUN (시뮬레이션)'}")
        print(f"========================================================\n")
        
        from brands.aura.aura_kin_pipeline import AuraKinPipeline
        from brands.insurance.insurance_kin_pipeline import InsuranceKinPipeline
        from brands.stock.stock_kin_pipeline import StockKinPipeline
        
        results = {}
        
        print("\n💖 [1/3] Aura 데이팅 지식iN 실시간 낚아채기 시작...")
        results["aura"] = AuraKinPipeline().run_catch_cycle(max_catch=1, dry_run=dry_run)
        
        print("\n🛡️ [2/3] InsureBalance 보험비교 지식iN 실시간 낚아채기 시작...")
        results["insurance"] = InsuranceKinPipeline().run_catch_cycle(max_catch=1, dry_run=dry_run)
        
        print("\n📈 [3/3] Stock Master AI 주식 지식iN 실시간 낚아채기 시작...")
        results["stock"] = StockKinPipeline().run_catch_cycle(max_catch=1, dry_run=dry_run)
        
        print("\n========================================================")
        print("🎉 3대 앱 지식iN 실시간 낚아채기 가동 완료!")
        print("========================================================\n")
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    print(f"\n========================================================")
    print(f"🏭 대한민국 3대 앱 24대 허브 무인 마케팅 공장 전체 점화")
    print(f"Mode: {'LIVE' if is_live else 'DRY-RUN'} (손 하나 안 대는 24시간 자율 가동)")
    print(f"========================================================\n")

    summary = {}

    # 1. Aura 데이팅 파이프라인
    print("\n💖 [1/3] Aura 데이팅 파이프라인 가동 시작...")
    aura = AuraPipeline(dry_run=dry_run)
    summary["aura"] = aura.run_full_daily_cycle()

    # 2. Insurance 보험 비교 파이프라인
    print("\n🛡️ [2/3] InsureBalance 보험 비교 파이프라인 가동 시작...")
    insurance = InsurancePipeline(dry_run=dry_run)
    summary["insurance"] = insurance.run_full_daily_cycle()

    # 3. Stock 주식 AI 파이프라인
    print("\n📈 [3/3] Stock Master AI 주식 마케팅 파이프라인 가동 시작...")
    stock = StockPipeline(dry_run=dry_run)
    summary["stock"] = stock.run_full_daily_cycle()

    print("\n========================================================")
    print("🎉 3대 앱 전체 무인 가동 완료!")
    print("========================================================\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
