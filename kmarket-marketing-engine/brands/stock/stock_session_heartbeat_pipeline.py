# -*- coding: utf-8 -*-
"""
Stock Session Heartbeat Pipeline (주식 AI StockMaster 6대 플랫폼 세션 영구 생명 연장 독립 파이프라인)
==================================================================================================
- 브랜드: 주식 AI (StockMaster AI)
- 역할:
  주식 전용 6대 채널(유튜브, 메타 MBS, 틱톡, 네이버 클립, 스레드, 티스토리)의 디스크 프로필을
  3시간마다 스텔스로 핑(Ping)하여 세션 만료를 원천 차단하고 365일 100% 무인 가동을 보장합니다.
"""

import sys
import asyncio
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.auto_publishers.omni_session_heartbeat_keeper import OmniSessionHeartbeatKeeper


class StockSessionHeartbeatPipeline:
    """주식 전용 세션 생명 연장 파이프라인"""

    def __init__(self):
        self.keeper = OmniSessionHeartbeatKeeper(brand="stock")

    async def run_once(self):
        """1회 즉시 생명 연장 실행"""
        return await self.keeper.run_brand_cycle()

    async def run_daemon(self, interval_hours: float = 3.0):
        """주식 전용 3시간 주기 무한 데몬"""
        interval_sec = int(interval_hours * 3600)
        cycle = 1
        while True:
            print(f"\n[주식 Heartbeat] #{cycle}회차 6대 플랫폼 세션 자동 갱신 시작...")
            await self.run_once()
            print(f"[주식 Heartbeat] 다음 갱신까지 {interval_hours}시간 동안 대기합니다...\n")
            cycle += 1
            await asyncio.sleep(interval_sec)


if __name__ == "__main__":
    pipeline = StockSessionHeartbeatPipeline()
    if "--daemon" in sys.argv:
        asyncio.run(pipeline.run_daemon(interval_hours=3.0))
    else:
        res = asyncio.run(pipeline.run_once())
        print("Stock Pipeline Result:", res)
