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

    # ── [3대 브랜드 24시간 365일 완전 무인 통합 데몬 모드] ──
    if "--daemon" in sys.argv or "-d" in sys.argv:
        import time
        import threading
        print(f"\n========================================================")
        print(f"🤖 [대한민국 3대 브랜드] 24시간 365일 무인 자율 마케팅 데몬 통합 기동")
        print(f"Mode: {'LIVE (실제 발행)' if is_live else 'DRY-RUN (시뮬레이션)'}")
        print(f"• 1. 💖 Aura AI 데이팅 (아우라AI데이팅)")
        print(f"• 2. 🛡️ InsureBalance 보험비교 (보험 리밸런스)")
        print(f"• 3. 📈 StockMaster AI (스톡마스터 AI)")
        print(f"• ⏰ ☀️ 08:30 KST: 동영상 숏츠 ① (유튜브 쇼츠 + 네이버 클립 + 인스타/페북 릴스)")
        print(f"• ⏰ 🍱 12:30 KST: 카드뉴스형 콘텐츠 (유튜브 쇼츠 + 네이버 클립 + 인스타/페북 피드&릴스)")
        print(f"• ⏰ 🌙 19:30 KST: 동영상 숏츠 ② (유튜브 쇼츠 + 네이버 클립 + 인스타/페북 릴스)")
        print(f"• ⏰ 블로그(2,000자 칼럼+16:9 사진): 10:00 / 15:00 / 20:00 KST")
        print(f"• ⏰ 휴먼 웜업(네이버 블로그/카페): 08:30 / 12:30 / 15:30 / 21:30 KST")
        print(f"• ⏰ 네이버 지식iN 실시간 모니터링: 30분 간격 자동 탐색")
        print(f"========================================================\n")

        aura_pipe = AuraPipeline(dry_run=dry_run)
        insure_pipe = InsurancePipeline(dry_run=dry_run)
        stock_pipe = StockPipeline(dry_run=dry_run)

        t_aura = threading.Thread(target=aura_pipe.run_daemon, daemon=True, name="AuraDaemon")
        t_insure = threading.Thread(target=insure_pipe.run_daemon, daemon=True, name="InsuranceDaemon")
        t_stock = threading.Thread(target=stock_pipe.run_daemon, daemon=True, name="StockDaemon")

        t_aura.start()
        t_insure.start()
        t_stock.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 3대 브랜드 통합 데몬이 사용자에 의해 중단되었습니다.")
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
