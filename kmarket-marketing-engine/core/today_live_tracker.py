# -*- coding: utf-8 -*-
"""
Today Live Publishing Tracker (🚀 3대 브랜드 독립 레고 블록 조립 오케스트레이터)
=============================================================================
- 브랜드: Aura 데이팅, InsureBalance 보험비교, StockMaster AI 주식
- 원칙:
  1. 각 앱의 실시간 로직은 brands/{brand}/{brand}_live_tracker.py 에 100% 독립 분리
  2. 본 모듈은 각 브랜드의 독립 레고 블록을 조립하여 종합 전광판 데이터만 전달
"""

import sys
import datetime
import logging
from typing import Dict, Any

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from brands.aura.aura_live_tracker import AuraLiveTracker
from brands.insurance.insurance_live_tracker import InsuranceLiveTracker
from brands.stock.stock_live_tracker import StockLiveTracker

logger = logging.getLogger("TodayLiveTracker")


class TodayLiveTracker:
    """3대 슈퍼앱 독립 레고 블록 조립 오케스트레이터"""

    def __init__(self):
        pass

    def get_all_live_feed(self) -> Dict[str, Any]:
        """3대 브랜드의 독립 모듈을 각각 호출하여 종합 반환"""
        now = datetime.datetime.now()
        today_str = now.strftime("%Y-%m-%d")

        try:
            import importlib
            import brands.aura.aura_live_tracker as alt
            import brands.insurance.insurance_live_tracker as ilt
            import brands.stock.stock_live_tracker as slt
            importlib.reload(alt)
            importlib.reload(ilt)
            importlib.reload(slt)
            aura_tracker = alt.AuraLiveTracker()
            insurance_tracker = ilt.InsuranceLiveTracker()
            stock_tracker = slt.StockLiveTracker()
        except Exception:
            aura_tracker = AuraLiveTracker()
            insurance_tracker = InsuranceLiveTracker()
            stock_tracker = StockLiveTracker()

        aura_data = aura_tracker.get_live_status()
        insurance_data = insurance_tracker.get_live_status()
        stock_data = stock_tracker.get_live_status()

        total_blog = (
            aura_data.get("today_blog_count", 0) +
            insurance_data.get("today_blog_count", 0) +
            stock_data.get("today_blog_count", 0)
        )
        total_kin = (
            aura_data.get("today_kin_count", 0) +
            insurance_data.get("today_kin_count", 0) +
            stock_data.get("today_kin_count", 0)
        )
        total_shorts = (
            aura_data.get("today_shorts_count", 0) +
            insurance_data.get("today_shorts_count", 0) +
            stock_data.get("today_shorts_count", 0)
        )
        total_cardnews = (
            aura_data.get("today_cardnews_count", 0) +
            insurance_data.get("today_cardnews_count", 0) +
            stock_data.get("today_cardnews_count", 0)
        )
        total_cafe = (
            aura_data.get("today_cafe_count", 0) +
            insurance_data.get("today_cafe_count", 0) +
            stock_data.get("today_cafe_count", 0)
        )
        total_reddit = (
            aura_data.get("today_reddit_count", 0) +
            insurance_data.get("today_reddit_count", 0) +
            stock_data.get("today_reddit_count", 0)
        )

        return {
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "today": today_str,
            "summary": {
                "total_blog_today": total_blog,
                "total_kin_today": total_kin,
                "total_shorts_today": total_shorts,
                "total_cardnews_today": total_cardnews,
                "total_cafe_today": total_cafe,
                "total_reddit_today": total_reddit
            },
            "brands": {
                "aura": aura_data,
                "insurance": insurance_data,
                "stock": stock_data
            }
        }

    def get_brand_live_status(self, brand: str) -> Dict[str, Any]:
        """단일 브랜드 전용 독립 상태 반환"""
        import importlib
        if brand == "aura":
            import brands.aura.aura_live_tracker as alt
            importlib.reload(alt)
            return alt.AuraLiveTracker().get_live_status()
        elif brand == "insurance":
            import brands.insurance.insurance_live_tracker as ilt
            importlib.reload(ilt)
            return ilt.InsuranceLiveTracker().get_live_status()
        elif brand == "stock":
            import brands.stock.stock_live_tracker as slt
            importlib.reload(slt)
            return slt.StockLiveTracker().get_live_status()
        return {}


if __name__ == "__main__":
    tracker = TodayLiveTracker()
    import json
    print(json.dumps(tracker.get_all_live_feed(), ensure_ascii=False, indent=2))
