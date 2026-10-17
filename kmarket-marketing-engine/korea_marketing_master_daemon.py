# -*- coding: utf-8 -*-
"""
[마스터 데몬] KoreaMarketingMasterDaemon - 🤖 [24시간 365일 3대 앱 완전 자율 통합 데몬]
========================================================================================
- 브랜드: 대한민국 3대 앱 (💖 Aura 데이팅, 🛡️ 보험 리밸런스, 📈 StockMaster AI)
- 24시간 완벽 분리 라이프사이클:
  1. 🌙 [새벽 00:00 ~ 03:00] 한국 마케팅봇 GPU 렌더링 전담 타임
     - 3대 앱 × (숏폼 3개 + 카드뉴스 2개) = 총 15개 콘텐츠 순차 제작
     - 1건 제작 완료 시마다 [5분 쿨다운 + VRAM 0MB 방출] 철저 준수 (GPUSafetyGuard)
     - 새벽 3시 이전 15개 전량 완성하여 오늘자 대기 큐(manifest.json)에 안전 보관
  2. ☀️ [아침 07:00 이후] 저쪽 컴퓨터(KTRS) GPU 100% 양보 & 한국 마케팅봇 정시 송출
     - GPU 부하 제로(0%)로 순수 네트워크/모바일 ADB 기반 골든타임 정시 발행
     - ⏰ 08:30 KST: 동영상 숏폼 ① (3대 앱 순차)
     - ⏰ 12:30 KST: 카드뉴스 5장 ① (3대 앱 순차)
     - ⏰ 15:30 KST: 동영상 숏폼 ② (3대 앱 순차)
     - ⏰ 18:30 KST: 카드뉴스 5장 ② (3대 앱 순차)
     - ⏰ 21:00 KST: 동영상 숏폼 ③ (3대 앱 순차)
"""

import os
import sys
import time
import logging
import datetime
import threading
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s"
)
logger = logging.getLogger("KoreaMasterDaemon")

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from midnight_content_factory import MidnightContentFactory
from daytime_sns_dispatcher import DaytimeSNSDispatcher
from core.gpu_safety_guard import GPUSafetyGuard


class KoreaMarketingMasterDaemon:
    """3대 앱 24시간 365일 무인 마케팅 총괄 관제 데몬"""

    def __init__(self, dry_run: bool = False, cooldown_sec: int = 300):
        self.dry_run = dry_run
        self.factory = MidnightContentFactory(cooldown_sec=cooldown_sec)
        self.dispatcher = DaytimeSNSDispatcher(dry_run=dry_run)

    def run(self):
        logger.info("\n" + "=" * 75)
        logger.info("🤖 [대한민국 3대 앱] 24시간 365일 완전 무인 자율 마케팅 마스터 데몬 점화")
        logger.info("• 대상 브랜드: 💖 Aura AI 데이팅 / 🛡️ 보험 리밸런스 / 📈 StockMaster AI")
        logger.info("• 🌙 새벽 00:00: GPU 안전 5분 쿨다운 순차 제작 (숏폼 3개 + 카드뉴스 2개 × 3앱 = 15개)")
        logger.info("• ☀️ 아침 07:00: 저쪽 컴퓨터(KTRS) GPU 100% 양보 & 주간 5대 골든타임 정시 송출")
        logger.info(f"• 실행 모드: {'DRY-RUN (시뮬레이션)' if self.dry_run else 'LIVE (실제 렌더링 및 발행)'}")
        logger.info("=" * 75 + "\n")

        # 1. 야간 생산 스레드
        t_factory = threading.Thread(target=self.factory.start_daemon, daemon=True, name="MidnightFactoryThread")
        # 2. 주간 송출 스레드
        t_dispatcher = threading.Thread(target=self.dispatcher.start_daemon, daemon=True, name="DaytimeDispatcherThread")

        t_factory.start()
        t_dispatcher.start()

        logger.info("✅ 야간 생산 데몬 및 주간 송출 데몬 동시 상주 완료. 24시간 대기 모드로 진입합니다.")

        try:
            while True:
                # 1시간마다 GPU 헬스체크 및 로그 기록
                now = datetime.datetime.now()
                stats = GPUSafetyGuard.get_gpu_stats()
                temp = f"{stats['temp_c']}℃" if stats["available"] else "정상"
                vram = f"{stats['vram_used_mb']}MB" if stats["available"] else "정상"
                logger.info(f"💓 [Heartbeat] {now.strftime('%Y-%m-%d %H:%M:%S')} | GPU 온도: {temp} | VRAM: {vram}")
                time.sleep(3600)
        except KeyboardInterrupt:
            logger.info("\n🛑 마스터 데몬이 관리자에 의해 안전하게 중단되었습니다.")
            GPUSafetyGuard.cleanup_all()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="대한민국 3대 앱 24시간 무인 마케팅 마스터 데몬")
    parser.add_argument("--dry-run", action="store_true", help="가상 시뮬레이션 모드")
    parser.add_argument("--cooldown", type=int, default=300, help="GPU 쿨다운 시간(초, 기본 300초=5분)")
    args = parser.parse_args()

    daemon = KoreaMarketingMasterDaemon(dry_run=args.dry_run, cooldown_sec=args.cooldown)
    daemon.run()
