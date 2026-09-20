"""
Aura Runner (Aura 데이팅 독립 실행 스크립트)
Usage:
    python run_aura.py           # 드라이런(테스트 모드)
    python run_aura.py --live    # 실제 라이브 발행 모드
"""

import sys
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from brands.aura.aura_pipeline import AuraPipeline
from brands.aura.aura_blog_scheduler import AuraBlogScheduler


def main():
    if "--blog-now" in sys.argv or "-bn" in sys.argv:
        print("\n==============================================")
        print("💖 [Aura] 2030 매거진 2,000자 칼럼 + 맞춤 사진 1장 즉시 생성 & 4대 채널 배포")
        print("==============================================\n")
        
        force_topic = None
        for i, arg in enumerate(sys.argv):
            if arg in ["--topic", "--topic-id", "-t"] and i + 1 < len(sys.argv):
                try:
                    force_topic = int(sys.argv[i + 1])
                except ValueError:
                    pass

        scheduler = AuraBlogScheduler()
        res = scheduler.run_one_cycle(force_topic_id=force_topic)
        print("\n[발행 결과 요약]:")
        print(f"  - 📚 주제 ID: #{res['topic_id']}")
        print(f"  - 🟢 네이버 블로그 제목: {res.get('title_naver', res['title'])}")
        print(f"  - 🟠 티스토리 제목: {res.get('title_tistory', res['title'])}")
        print(f"  - 🟡 카카오/브런치 제목: {res.get('title_kakao', res['title'])}")
        print(f"  - 🎨 16:9 사진 URL: {res['image_url']}")
        print(f"  - 🔗 랜딩 URL: https://aura-ai-dating.vercel.app/")
        print(f"  - ⏰ 발행 시각: {res['published_at']}")
        print(f"  - ⏭️ 다음 예정 주제 번호: #{res['next_topic_id']}")

        channels = res.get("publish_results", {}).get("channels", {})
        print("\n[🚀 4대 옴니채널 자동 배포 현황]:")
        print(f"  1. 💖 Aura 앱 피드 (Supabase): {channels.get('aura_app', {}).get('status')} (피드ID: {channels.get('aura_app', {}).get('feed_post_id')}, 4개국어 번역: {channels.get('aura_app', {}).get('translations_count')}개)")
        print(f"  2. 🟢 네이버 블로그: {channels.get('naver_blog', {}).get('status')} -> URL: {channels.get('naver_blog', {}).get('url', '-')}")
        print(f"  3. 🟠 티스토리: {channels.get('tistory', {}).get('status')} -> URL: {channels.get('tistory', {}).get('url', '-')}")
        print(f"  4. 🟡 카카오/브런치: {channels.get('brunch', {}).get('status')} -> {channels.get('brunch', {}).get('message', '-')}")
        return

    if "--blog-status" in sys.argv:
        scheduler = AuraBlogScheduler()
        st = scheduler.get_status()
        print(json.dumps(st, ensure_ascii=False, indent=2))
        return

    if "--blog-daemon" in sys.argv:
        scheduler = AuraBlogScheduler()
        scheduler.start_daemon()
        return

    is_live = "--live" in sys.argv
    dry_run = not is_live

    print(f"\n==============================================")
    print(f"💖 Aura 데이팅 마케팅 파이프라인 가동 (Mode: {'LIVE' if is_live else 'DRY-RUN'})")
    print(f"==============================================\n")

    pipeline = AuraPipeline(dry_run=dry_run)
    result = pipeline.run_full_daily_cycle()
    print("\n[가동 결과 요약]:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
