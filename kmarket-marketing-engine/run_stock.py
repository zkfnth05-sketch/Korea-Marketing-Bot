# -*- coding: utf-8 -*-
"""
Stock Runner (Stock Master AI 주식 AI 독립 실행 스크립트)
Usage:
    python run_stock.py               # 드라이런(테스트 모드)
    python run_stock.py --live        # 실제 라이브 발행 모드
    python run_stock.py --blog-now    # 3대 채널 옴니 블로그 1회 즉시 무인 배포
"""

import sys
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from brands.stock.stock_pipeline import StockPipeline
from brands.stock.stock_blog_scheduler import StockBlogScheduler


def main():
    # ── [실시간 캡처 기반 2대 블로그 발행 옵션] ──
    is_semi = "--semiconductor" in sys.argv or "-semi" in sys.argv
    is_rank1 = "--rank1" in sys.argv or "-r1" in sys.argv
    is_blog_now = "--blog-now" in sys.argv or "-bn" in sys.argv

    if is_semi or is_rank1 or is_blog_now:
        article_type = "semiconductor" if is_semi else "rank1"
        type_title = "👑 [반도체 주도주 편 (삼성전자 vs SK하이닉스)]" if is_semi else "🥇 [오늘 계량 전광판 1위 주도주 편]"

        print("\n==============================================")
        print(f"📈 [StockMaster] 실시간 1600x1600 캡처 ✕ 성공 바이블 칼럼 3대 채널 배포")
        print(f"   타입: {type_title}")
        print("==============================================\n")

        scheduler = StockBlogScheduler()
        res = scheduler.run_captured_cycle(article_type=article_type)

        print("\n[🎯 실시간 캡처 블로그 발행 결과 요약]:")
        print(f"  - 🏷️ 발행 타입: {res.get('article_type')}")
        print(f"  - 🟢 네이버 블로그 제목: {res.get('title_naver')}")
        print(f"  - 🟠 티스토리 제목: {res.get('title_tistory')}")
        print(f"  - 🟡 카카오/브런치 제목: {res.get('title_brunch')}")
        print(f"  - 📸 1600x1600 캡처 사진: {res.get('image_path')}")
        print(f"  - 🔗 랜딩 URL: https://stockmaster-ai.vercel.app/")
        print(f"  - ⏰ 발행 시각: {res.get('published_at')}")

        channels = res.get("publish_results", {}).get("channels", {})
        print("\n[🚀 4대 옴니채널 자동 배포 현황]:")
        print(f"  1. 🟢 네이버 블로그: {channels.get('naver_blog', {}).get('status')} -> URL: {channels.get('naver_blog', {}).get('url', '-')}")
        print(f"  2. 🟠 티스토리: {channels.get('tistory', {}).get('status')} -> URL: {channels.get('tistory', {}).get('post_url', channels.get('tistory', {}).get('url', '-'))}")
        print(f"  3. 🟡 카카오/브런치: {channels.get('brunch', {}).get('status')} -> URL: {channels.get('brunch', {}).get('post_url', '-')}")
        print(f"  4. 📊 본진 웹앱 Supabase: {channels.get('supabase_research', {}).get('status')} -> Post ID: {channels.get('supabase_research', {}).get('post_id', '-')}")
        return

    # ── [지식iN 단독 실행 옵션] ──
    if "--kin-now" in sys.argv or "-kn" in sys.argv:
        is_live = "--live" in sys.argv
        from brands.stock.stock_kin_pipeline import StockKinPipeline
        print("\n==============================================")
        print(f"📈 [StockMaster] 네이버 지식iN 실시간 낚아채기 1회 즉시 실행 (Mode: {'LIVE' if is_live else 'DRY-RUN'})")
        print("==============================================\n")
        pipe = StockKinPipeline()
        res = pipe.run_catch_cycle(max_catch=1, dry_run=not is_live)
        print("\n[지식iN 낚아채기 결과 요약]:")
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return

    if "--kin-daemon" in sys.argv or "-kd" in sys.argv:
        from brands.stock.stock_kin_scheduler import StockKinScheduler
        print("\n==============================================")
        print("📈 [StockMaster] 네이버 지식iN 24시간 실시간 낚아채기 자율 스케줄러 가동 (300초 간격)")
        print("==============================================\n")
        scheduler = StockKinScheduler()
        scheduler.run_continuous_daemon(check_interval_seconds=300)
        return

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
