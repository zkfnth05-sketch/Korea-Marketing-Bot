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
    if "--blog-now" in sys.argv or "-bn" in sys.argv:
        print("\n==============================================")
        print("📈 [StockMaster] 2,000자 전문 칼럼 + 16:9 맞춤 사진 1장 즉시 생성 & 3대 채널 배포")
        print("==============================================\n")

        force_topic = None
        for i, arg in enumerate(sys.argv):
            if arg in ["--topic", "--topic-id", "-t"] and i + 1 < len(sys.argv):
                try:
                    force_topic = int(sys.argv[i + 1])
                except ValueError:
                    pass

        scheduler = StockBlogScheduler()
        res = scheduler.run_one_cycle(force_topic_id=force_topic)
        print("\n[발행 결과 요약]:")
        print(f"  - 📚 주제 ID: #{res['topic_id']}")
        print(f"  - 🟢 네이버 블로그 제목: {res.get('title_naver', res['title'])}")
        print(f"  - 🟠 티스토리 제목: {res.get('title_tistory', res['title'])}")
        print(f"  - 🟡 카카오/브런치 제목: {res.get('title_brunch', res['title'])}")
        print(f"  - 🎨 16:9 사진 URL: {res.get('image_url', '-')}")
        print(f"  - 🔗 랜딩 URL: https://stockmaster.co.kr")
        print(f"  - ⏰ 발행 시각: {res['published_at']}")
        print(f"  - ⏭️ 다음 예정 주제 번호: #{res['next_topic_id']}")

        channels = res.get("publish_results", {}).get("channels", {})
        print("\n[🚀 3대 옴니채널 자동 배포 현황]:")
        print(f"  1. 🟢 네이버 블로그: {channels.get('naver_blog', {}).get('status')} -> URL: {channels.get('naver_blog', {}).get('url', '-')}")
        print(f"  2. 🟠 티스토리: {channels.get('tistory', {}).get('status')} -> URL: {channels.get('tistory', {}).get('post_url', channels.get('tistory', {}).get('url', '-'))}")
        print(f"  3. 🟡 카카오/브런치: {channels.get('brunch', {}).get('status')} -> URL: {channels.get('brunch', {}).get('post_url', '-')}")
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
