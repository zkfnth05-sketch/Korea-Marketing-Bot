# -*- coding: utf-8 -*-
"""
[독립 레고 블록] DaytimeSNSDispatcher - ☀️ [주간 SNS 정시 자율 송출기]
========================================================================
- 브랜드: 대한민국 3대 앱 (💖 Aura 데이팅, 🛡️ 보험 리밸런스, 📈 StockMaster AI)
- 역할:
  1. 새벽(00:00~03:00)에 완벽 렌더링된 '오늘자 콘텐츠 큐(manifest.json)'에서 꺼내옴
  2. 아침 7시 이후 GPU는 저쪽 컴퓨터(KTRS)에 온전히 100% 양보
  3. GPU 부하 제로(0%)로 순수 네트워크/ADB 모바일 기반 골든타임 정시 발행
- 정규 송출 시간표:
  • ⏰ ☀️ 08:30 KST: 동영상 숏폼 ① (Aura ➔ 보험 ➔ 주식)
  • ⏰ 🍱 12:30 KST: 카드뉴스 5장 ① (Aura ➔ 보험 ➔ 주식)
  • ⏰ ☕ 15:30 KST: 동영상 숏폼 ② (Aura ➔ 보험 ➔ 주식)
  • ⏰ 🌆 18:30 KST: 카드뉴스 5장 ② (Aura ➔ 보험 ➔ 주식)
  • ⏰ 🌙 21:00 KST: 동영상 숏폼 ③ (Aura ➔ 보험 ➔ 주식)
"""

import os
import sys
import time
import json
import logging
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("DaytimeSNSDispatcher")

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))


class DaytimeSNSDispatcher:
    """새벽 제작 큐 기반 주간 SNS 정시 송출기"""

    QUEUE_DIR = CURRENT_DIR / "outputs" / "daily_queue"
    PUBLISH_HISTORY_FILE = CURRENT_DIR / "outputs" / "daytime_publish_history.json"

    SCHEDULE_SLOTS = [
        {"time": "08:30", "slot": "shorts_1", "type": "shorts", "label": "아침 숏폼 ①"},
        {"time": "12:30", "slot": "cardnews_1", "type": "cardnews", "label": "점심 카드뉴스 ①"},
        {"time": "15:30", "slot": "shorts_2", "type": "shorts", "label": "오후 숏폼 ②"},
        {"time": "18:30", "slot": "cardnews_2", "type": "cardnews", "label": "퇴근 카드뉴스 ②"},
        {"time": "21:00", "slot": "shorts_3", "type": "shorts", "label": "야간 숏폼 ③"}
    ]

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    def _load_history(self) -> List[Dict[str, Any]]:
        if self.PUBLISH_HISTORY_FILE.exists():
            try:
                with open(self.PUBLISH_HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_history(self, history: List[Dict[str, Any]]):
        try:
            with open(self.PUBLISH_HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"발행 이력 저장 경고: {e}")

    def is_slot_published_today(self, date_str: str, slot: str, brand: str) -> bool:
        """당일 특정 브랜드의 슬롯 발행 여부 점검 (중복 발행 0% 원천 차단)"""
        history = self._load_history()
        for item in history:
            if item.get("date") == date_str and item.get("slot") == slot and item.get("brand") == brand and item.get("status") == "success":
                return True
        return False

    def load_today_manifest(self, date_str: str = None) -> Optional[Dict[str, Any]]:
        """오늘자 새벽 생산 매니페스트 로드"""
        if not date_str:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        manifest_file = self.QUEUE_DIR / date_str / "manifest.json"
        if manifest_file.exists():
            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"매니페스트 로드 실패: {e}")
        return None

    def publish_single_content(self, brand: str, content_type: str, topic_id: int, slot: str) -> bool:
        """단일 브랜드 콘텐츠 정시 송출 실행"""
        logger.info(f"🚀 [{brand.upper()}] {slot} (주제 #{topic_id}) 정시 송출 트리거...")

        if self.dry_run:
            logger.info(f"   [DRY-RUN] {brand} {content_type} #{topic_id} 송출 시뮬레이션 성공")
            return True

        try:
            if brand == "aura":
                if content_type == "shorts":
                    from brands.aura.aura_omni_shorts_pilot import AuraOmniShortsPilot
                    res = AuraOmniShortsPilot().execute_single_slot(topic_id=topic_id, force=True)
                    return res.get("status") in ["success", "partially_published"]
                else:
                    from brands.aura.aura_omni_cardnews_pilot import AuraOmniCardnewsPilot
                    res = AuraOmniCardnewsPilot().execute_single_slot(topic_id=topic_id, force=True)
                    return res.get("status") in ["success", "partially_published"]

            elif brand == "insurance":
                if content_type == "shorts":
                    from brands.insurance.insurance_omni_shorts_pilot import InsuranceOmniShortsPilot
                    res = InsuranceOmniShortsPilot().execute_single_slot(topic_id=topic_id, force=True)
                    return res.get("status") in ["success", "partially_published"]
                else:
                    from brands.insurance.insurance_omni_cardnews_pilot import InsuranceOmniCardnewsPilot
                    res = InsuranceOmniCardnewsPilot().execute_single_slot(topic_id=topic_id, force=True)
                    return res.get("status") in ["success", "partially_published"]

            elif brand == "stock":
                if content_type == "shorts":
                    from brands.stock.stock_omni_shorts_pilot import StockOmniShortsPilot
                    res = StockOmniShortsPilot().execute_single_slot(topic_id=topic_id, force=True)
                    return res.get("status") in ["success", "partially_published"]
                else:
                    from brands.stock.stock_omni_cardnews_pilot import StockOmniCardnewsPilot
                    res = StockOmniCardnewsPilot().execute_single_slot(topic_id=topic_id, force=True)
                    return res.get("status") in ["success", "partially_published"]

        except Exception as e:
            logger.error(f"❌ [{brand.upper()}] {slot} 송출 중 예외 발생: {e}")
            return False

        return False

    def dispatch_slot(self, target_slot: str, date_str: str = None) -> Dict[str, Any]:
        """
        특정 슬롯(예: shorts_1)의 3대 브랜드 콘텐츠를 순차 송출
        """
        if not date_str:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")

        manifest = self.load_today_manifest(date_str)
        if not manifest:
            logger.warning(f"⚠️ {date_str} 매니페스트 부재 - 오늘 새벽 제작 큐를 먼저 확인하십시오.")
            return {"status": "NO_MANIFEST", "slot": target_slot}

        tasks = [t for t in manifest.get("tasks", []) if t.get("slot") == target_slot]
        if not tasks:
            logger.warning(f"⚠️ {target_slot} 슬롯에 해당하는 태스크가 매니페스트에 없습니다.")
            return {"status": "NO_TASKS", "slot": target_slot}

        logger.info("\n" + "=" * 70)
        logger.info(f"📢 [주간 SNS 정시 송출 가동] 슬롯: {target_slot} (총 {len(tasks)}개 브랜드)")
        logger.info("=" * 70)

        history = self._load_history()
        slot_results = {}

        for task in tasks:
            brand = task["brand"]
            c_type = task["type"]
            topic_id = task["topic_id"]

            if self.is_slot_published_today(date_str, target_slot, brand):
                logger.info(f"⏭️ [{brand.upper()}] {target_slot} 오늘 이미 송출 완료됨 (중복 방지 건너뜀)")
                slot_results[brand] = "ALREADY_PUBLISHED"
                continue

            success = self.publish_single_content(brand, c_type, topic_id, target_slot)
            slot_results[brand] = "SUCCESS" if success else "FAILED"

            history.append({
                "date": date_str,
                "slot": target_slot,
                "brand": brand,
                "type": c_type,
                "topic_id": topic_id,
                "status": "success" if success else "failed",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            self._save_history(history)

            # 브랜드 간 15초 안전 인터벌 (계정 혼선 방지 및 네트워크 안정화)
            time.sleep(15)

        logger.info(f"🎉 [{target_slot}] 3대 브랜드 정시 송출 처리 완료: {slot_results}\n")
        return {"status": "COMPLETED", "slot": target_slot, "results": slot_results}

    def start_daemon(self):
        """24시간 상주하며 정해진 시간표(08:30, 12:30, 15:30, 18:30, 21:00)에 자동 송출"""
        logger.info("🤖 [DaytimeSNSDispatcher Daemon] 24시간 365일 정시 송출 감시 데몬 기동")
        logger.info("⏰ 등록된 황금 시간표:")
        for s in self.SCHEDULE_SLOTS:
            logger.info(f"   • {s['time']} KST ➔ {s['label']} ({s['slot']})")

        while True:
            now = datetime.datetime.now()
            today_str = now.strftime("%Y-%m-%d")
            hm_str = now.strftime("%H:%M")

            for s in self.SCHEDULE_SLOTS:
                if hm_str == s["time"]:
                    logger.info(f"\n⏰ [골든타임 {hm_str} KST 도달!] {s['label']} 정시 송출 가동...")
                    try:
                        self.dispatch_slot(target_slot=s["slot"], date_str=today_str)
                    except Exception as e:
                        logger.error(f"❌ {s['label']} 정시 송출 실패: {e}")
                    # 중복 호출 방지를 위해 60초 대기
                    time.sleep(60)
                    break

            time.sleep(10)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="☀️ 주간 SNS 정시 자율 송출기")
    parser.add_argument("--slot", "-s", type=str, default=None, choices=["shorts_1", "shorts_2", "shorts_3", "cardnews_1", "cardnews_2"], help="즉시 송출할 슬롯")
    parser.add_argument("--dry-run", action="store_true", help="가상 시뮬레이션 모드")
    parser.add_argument("--daemon", action="store_true", help="24시간 상시 감시 데몬 가동")
    args = parser.parse_args()

    dispatcher = DaytimeSNSDispatcher(dry_run=args.dry_run)

    if args.daemon:
        dispatcher.start_daemon()
    elif args.slot:
        dispatcher.dispatch_slot(target_slot=args.slot)
    else:
        print("사용법: python daytime_sns_dispatcher.py --slot shorts_1 --dry-run 또는 --daemon")
