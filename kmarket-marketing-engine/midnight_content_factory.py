# -*- coding: utf-8 -*-
"""
[독립 레고 블록] MidnightContentFactory - 🌙 [밤 12시 3대 앱 숏폼/카드뉴스 순차 생산 공장]
==========================================================================================
- 브랜드: 대한민국 3대 앱 (💖 Aura 데이팅, 🛡️ 보험 리밸런스, 📈 StockMaster AI)
- 일정: 매일 밤 12시(00:00 KST) 기상 ➔ 새벽 3시 이전 100% 생산 완료 ➔ 아침 7시 저쪽 컴퓨터에 GPU 온전히 양보
- 생산 목표 (총 15개 콘텐츠):
  • 💖 Aura: 숏폼 3개 + 카드뉴스 2개
  • 🛡️ 보험: 숏폼 3개 + 카드뉴스 2개
  • 📈 주식: 숏폼 3개 + 카드뉴스 2개
- 🛡️ GPU 세심 안심 가드:
  • 1건 완료 시마다 OS 레벨 서브프로세스 메모리 100% 반환
  • ComfyUI /free API로 VRAM 모델 언로드
  • 엄격한 5분(300초) GPU 냉각 휴식 타이머 (실시간 온도/VRAM 모니터링)
  • 65℃ 안전 차단벽 & 저쪽 컴퓨터(KTRS) 작업 시 자율 양보
"""

import os
import sys
import time
import json
import logging
import datetime
from pathlib import Path
from typing import Dict, Any, List

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
logger = logging.getLogger("MidnightContentFactory")

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from core.gpu_safety_guard import GPUSafetyGuard


class MidnightContentFactory:
    """밤 12시 순차 렌더링 & GPU 안심 냉각 총괄 팩토리"""

    QUEUE_DIR = CURRENT_DIR / "outputs" / "daily_queue"
    STATE_FILE = CURRENT_DIR / "outputs" / "midnight_factory_state.json"

    def __init__(self, cooldown_sec: int = 300):
        self.cooldown_sec = cooldown_sec  # 5분(300초) 냉각
        self.QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    def _load_state(self) -> Dict[str, Any]:
        if self.STATE_FILE.exists():
            try:
                with open(self.STATE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "last_run_date": "",
            "aura_shorts_offset": 0,
            "aura_cardnews_offset": 0,
            "insurance_shorts_offset": 0,
            "insurance_cardnews_offset": 0,
            "stock_shorts_offset": 0,
            "stock_cardnews_offset": 0
        }

    def _save_state(self, state: Dict[str, Any]):
        try:
            with open(self.STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"상태 저장 경고: {e}")

    def pick_rotation_topics(self, offset: int, count: int, max_topics: int = 8) -> List[int]:
        """주제 번호(1~max_topics)를 offset부터 순환 선택"""
        topics = []
        for i in range(count):
            t = ((offset + i) % max_topics) + 1
            topics.append(t)
        return topics

    def run_nightly_production(self, date_str: str = None, dry_run: bool = False) -> Dict[str, Any]:
        """
        🌙 밤 12시 3대 앱 숏폼 3개 + 카드뉴스 2개 순차 무인 생산 사이클
        총 15개 콘텐츠를 5분 쿨다운과 함께 GPU 과열 없이 새벽 3시 이전에 완결
        """
        if not date_str:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")

        today_queue_dir = self.QUEUE_DIR / date_str
        today_queue_dir.mkdir(parents=True, exist_ok=True)
        manifest_file = today_queue_dir / "manifest.json"

        state = self._load_state()

        logger.info("\n" + "=" * 70)
        logger.info(f"🌙 [밤 12시 콘텐츠 무인 생산 공장 점화] 기준 날짜: {date_str}")
        logger.info(f"❄️ GPU 냉각 규격: 작업당 {self.cooldown_sec}초(5분) 쿨다운 + VRAM 강제 방출")
        logger.info(f"🎯 생산 계획: 3대 앱 × (숏폼 3개 + 카드뉴스 2개) = 총 15개 콘텐츠")
        logger.info("=" * 70 + "\n")

        # 3대 브랜드별 오늘자 주제 선정 (각 숏폼 3개, 카드뉴스 2개)
        aura_s_topics = self.pick_rotation_topics(state.get("aura_shorts_offset", 0), 3, 8)
        aura_c_topics = self.pick_rotation_topics(state.get("aura_cardnews_offset", 0), 2, 8)

        insure_s_topics = self.pick_rotation_topics(state.get("insurance_shorts_offset", 0), 3, 8)
        insure_c_topics = self.pick_rotation_topics(state.get("insurance_cardnews_offset", 0), 2, 8)

        stock_s_topics = self.pick_rotation_topics(state.get("stock_shorts_offset", 0), 3, 8)
        stock_c_topics = self.pick_rotation_topics(state.get("stock_cardnews_offset", 0), 2, 6)

        tasks = []

        # 1. 💖 Aura 데이팅
        for idx, t in enumerate(aura_s_topics, 1):
            tasks.append({
                "brand": "aura",
                "type": "shorts",
                "slot": f"shorts_{idx}",
                "topic_id": t,
                "label": f"💖 Aura 데이팅 숏폼 #{idx} (주제 #{t})",
                "cmd": [sys.executable, str(CURRENT_DIR / "run_aura_shorts.py"), "--topic", str(t), "--no-publish"]
            })
        for idx, t in enumerate(aura_c_topics, 1):
            tasks.append({
                "brand": "aura",
                "type": "cardnews",
                "slot": f"cardnews_{idx}",
                "topic_id": t,
                "label": f"💖 Aura 데이팅 카드뉴스 #{idx} (주제 #{t})",
                "cmd": [sys.executable, str(CURRENT_DIR / "run_aura_cardnews.py"), "all", "--topic", str(t)]
            })

        # 2. 🛡️ 보험 리밸런스
        for idx, t in enumerate(insure_s_topics, 1):
            tasks.append({
                "brand": "insurance",
                "type": "shorts",
                "slot": f"shorts_{idx}",
                "topic_id": t,
                "label": f"🛡️ 보험 리밸런스 숏폼 #{idx} (주제 #{t})",
                "cmd": [sys.executable, str(CURRENT_DIR / "run_insurance_shorts.py"), "--topic", str(t)]
            })
        for idx, t in enumerate(insure_c_topics, 1):
            tasks.append({
                "brand": "insurance",
                "type": "cardnews",
                "slot": f"cardnews_{idx}",
                "topic_id": t,
                "label": f"🛡️ 보험 리밸런스 카드뉴스 #{idx} (주제 #{t})",
                "cmd": [sys.executable, str(CURRENT_DIR / "run_insurance_cardnews.py"), "--topic", str(t)]
            })

        # 3. 📈 StockMaster AI
        for idx, t in enumerate(stock_s_topics, 1):
            tasks.append({
                "brand": "stock",
                "type": "shorts",
                "slot": f"shorts_{idx}",
                "topic_id": t,
                "label": f"📈 StockMaster AI 숏폼 #{idx} (주제 #{t})",
                "cmd": [sys.executable, str(CURRENT_DIR / "run_stock_shorts.py"), "--topic", str(t)]
            })
        for idx, t in enumerate(stock_c_topics, 1):
            tasks.append({
                "brand": "stock",
                "type": "cardnews",
                "slot": f"cardnews_{idx}",
                "topic_id": t,
                "label": f"📈 StockMaster AI 카드뉴스 #{idx} (주제 #{t})",
                "cmd": [sys.executable, str(CURRENT_DIR / "run_stock_cardnews.py"), "--topic", str(t)]
            })

        total_tasks = len(tasks)
        logger.info(f"📋 총 {total_tasks}개 무인 제작 태스크 스케줄 등록 완료\n")

        results = []
        for i, task in enumerate(tasks, 1):
            logger.info(f"\n========================================================")
            logger.info(f"▶️ [{i}/{total_tasks}] {task['label']} 순차 제작 시작")
            logger.info(f"========================================================")

            if dry_run:
                logger.info(f"[DRY-RUN 시뮬레이션] {task['cmd']} 가상 실행 (쿨다운 2초)")
                time.sleep(2)
                task_res = {"success": True, "dry_run": True}
            else:
                task_res = GPUSafetyGuard.run_isolated_step(
                    cmd=task["cmd"],
                    label=f"[{i}/{total_tasks}] {task['label']}",
                    cwd=str(CURRENT_DIR),
                    cooldown_sec=self.cooldown_sec
                )

            task_record = {
                "step": i,
                "brand": task["brand"],
                "type": task["type"],
                "slot": task["slot"],
                "topic_id": task["topic_id"],
                "label": task["label"],
                "success": task_res.get("success", False),
                "elapsed_sec": task_res.get("elapsed_sec", 0),
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            results.append(task_record)

            # 중간 저장 (혹시 모를 중단 대비 무결성 보장)
            with open(manifest_file, "w", encoding="utf-8") as f:
                json.dump({
                    "date": date_str,
                    "completed_tasks": i,
                    "total_tasks": total_tasks,
                    "tasks": results
                }, f, ensure_ascii=False, indent=2)

        # 다음 회차를 위한 오프셋 갱신
        state["last_run_date"] = date_str
        state["aura_shorts_offset"] = (state.get("aura_shorts_offset", 0) + 3) % 8
        state["aura_cardnews_offset"] = (state.get("aura_cardnews_offset", 0) + 2) % 8
        state["insurance_shorts_offset"] = (state.get("insurance_shorts_offset", 0) + 3) % 8
        state["insurance_cardnews_offset"] = (state.get("insurance_cardnews_offset", 0) + 2) % 8
        state["stock_shorts_offset"] = (state.get("stock_shorts_offset", 0) + 3) % 8
        state["stock_cardnews_offset"] = (state.get("stock_cardnews_offset", 0) + 2) % 6
        self._save_state(state)

        logger.info("\n" + "=" * 70)
        logger.info(f"🎉 [밤 12시 3대 앱 콘텐츠 15개 전체 제작 완료!]")
        logger.info(f"📂 오늘자 매니페스트 저장 완료: {manifest_file}")
        logger.info(f"🤝 저쪽 컴퓨터(KTRS) 사용을 위해 GPU VRAM을 100% 비우고 대기 상태로 전환합니다.")
        logger.info("=" * 70 + "\n")

        # 최종 VRAM 클리어
        GPUSafetyGuard.cleanup_all()

        return {
            "date": date_str,
            "manifest_file": str(manifest_file),
            "total_produced": len(results),
            "success_count": sum(1 for r in results if r.get("success"))
        }

    def start_daemon(self):
        """24시간 상주하며 매일 밤 12시(00:00 KST)에 자동 기상하여 제작"""
        logger.info("🤖 [MidnightContentFactory Daemon] 24시간 365일 무인 감시 상주 시작")
        logger.info("⏰ 트리거 조건: 매일 00:00 KST (밤 12시)")

        while True:
            now = datetime.datetime.now()
            today_str = now.strftime("%Y-%m-%d")
            state = self._load_state()

            # 밤 12시(00:00 ~ 00:05 사이)이고 오늘 아직 안 돌렸으면 실행
            if now.hour == 0 and state.get("last_run_date") != today_str:
                logger.info(f"⏰ [밤 12시 도달] {today_str} 오늘치 3대 앱 15개 콘텐츠 순차 제작 점화!")
                try:
                    self.run_nightly_production(date_str=today_str)
                except Exception as e:
                    logger.error(f"❌ 야간 제작 공장 실행 중 예외 발생: {e}")

            time.sleep(30)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="🌙 밤 12시 3대 앱 콘텐츠 무인 생산 공장")
    parser.add_argument("--now", action="store_true", help="지금 즉시 1회 생산 가동")
    parser.add_argument("--dry-run", action="store_true", help="가상 시뮬레이션 모드")
    parser.add_argument("--daemon", action="store_true", help="밤 12시 상주 감시 데몬 가동")
    parser.add_argument("--cooldown", type=int, default=300, help="쿨다운 초 (기본: 300초 = 5분)")
    args = parser.parse_args()

    factory = MidnightContentFactory(cooldown_sec=args.cooldown)

    if args.daemon:
        factory.start_daemon()
    else:
        factory.run_nightly_production(dry_run=args.dry_run)
