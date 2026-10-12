# -*- coding: utf-8 -*-
"""
[100% 무인 자율 송출] OmniMediaDesktopWatcher (숏폼 + 카드뉴스 일체형 무인 자동 송출기)
========================================================================================
- 역할:
  1. 바탕화면 '한국 숏폼_산출물' 및 '한국 카드뉴스_산출물' 폴더(Aura, Insurance, Stock) 상시 감시 (30초 주기)
  2. 렌더링이 완료된 '오늘 날짜 신선 숏폼 완제품(MP4)' 및 '신선 카드뉴스(4~5장 슬라이드)' 실시간 포착
  3. 당일 미송출 상태 발견 시:
     -> 사람이나 AI 에이전트의 수동 개입 0%!
     -> 봇 스스로 즉시 해당 통합 파일럿(execute_single_slot)을 가동하여 100% 무인 자율 송출!
  4. 숏폼(4대 SNS: 유튜브 쇼츠, 틱톡, 네이버 클립, 메타 릴스) + 카드뉴스(Meta 페북/인스타, 쇼츠 변환 배포)
  5. 24시간 365일 무인 자율 가동으로 사람 손을 0%도 타지 않는 완전 자동화 구조 철통 보장
========================================================================================
"""

import os
import sys
import time
import re
import json
import logging
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
ENGINE_ROOT = CURRENT_DIR.parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

USER_PROFILE = Path(os.environ.get("USERPROFILE", "C:/Users/zkfnt"))
DESKTOP_SHORTS_DIR = USER_PROFILE / "Desktop" / "한국 숏폼_산출물"
DESKTOP_CARDNEWS_DIR = USER_PROFILE / "Desktop" / "한국 카드뉴스_산출물"

logger = logging.getLogger("OmniMediaDesktopWatcher")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BRANDS_SHORTS_CONFIG = {
    "aura": {
        "kr": "💖 Aura 데이팅",
        "folder": DESKTOP_SHORTS_DIR / "Aura",
        "pilot_module": "brands.aura.aura_omni_shorts_pilot",
        "pilot_class": "AuraOmniShortsPilot"
    },
    "insurance": {
        "kr": "🛡️ 보험 리밸런스",
        "folder": DESKTOP_SHORTS_DIR / "Insurance",
        "pilot_module": "brands.insurance.insurance_omni_shorts_pilot",
        "pilot_class": "InsuranceOmniShortsPilot"
    },
    "stock": {
        "kr": "📈 StockMaster 주식AI",
        "folder": DESKTOP_SHORTS_DIR / "Stock",
        "pilot_module": "brands.stock.stock_omni_shorts_pilot",
        "pilot_class": "StockOmniShortsPilot"
    }
}

BRANDS_CARDNEWS_CONFIG = {
    "aura": {
        "kr": "💖 Aura 데이팅",
        "folder": DESKTOP_CARDNEWS_DIR / "아우라",
        "pilot_module": "brands.aura.aura_omni_cardnews_pilot",
        "pilot_class": "AuraOmniCardnewsPilot"
    },
    "insurance": {
        "kr": "🛡️ 보험 리밸런스",
        "folder": DESKTOP_CARDNEWS_DIR / "보험",
        "pilot_module": "brands.insurance.insurance_omni_cardnews_pilot",
        "pilot_class": "InsuranceOmniCardnewsPilot"
    },
    "stock": {
        "kr": "📈 StockMaster 주식AI",
        "folder": DESKTOP_CARDNEWS_DIR / "주식",
        "pilot_module": "brands.stock.stock_omni_cardnews_pilot",
        "pilot_class": "StockOmniCardnewsPilot"
    }
}


class OmniShortsDesktopWatcher:
    """바탕화면 숏폼 및 카드뉴스 완제품 상시 감시 및 100% 무인 4대 SNS 자율 송출 데몬"""

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._file_sizes_tracker: Dict[str, int] = {}

    def extract_topic_id(self, name: str) -> Optional[int]:
        """파일명 또는 폴더명에서 주제 번호(01~08) 추출"""
        m = re.search(r"주제(\d{2})", name)
        if m:
            return int(m.group(1))
        m2 = re.search(r"_(\d{2})_", name)
        if m2:
            return int(m2.group(1))
        m3 = re.search(r"topic_?(\d+)", name, re.IGNORECASE)
        if m3:
            return int(m3.group(1))
        m4 = re.search(r"topic(\d+)", name, re.IGNORECASE)
        if m4:
            return int(m4.group(1))
        return None

    def scan_and_dispatch_shorts(self) -> List[Dict[str, Any]]:
        """1회 스캔: 미송출 신선 숏폼(MP4) 즉각 자율 송출"""
        today_ymd = datetime.now().strftime("%Y%m%d")
        dispatched = []

        for brand_key, binfo in BRANDS_SHORTS_CONFIG.items():
            base_folder = binfo["folder"]
            if not base_folder.exists():
                continue

            subfolders = sorted(
                [f for f in base_folder.iterdir() if f.is_dir() and today_ymd in f.name],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )

            brand_dispatched = False
            for subfolder in subfolders:
                if brand_dispatched:
                    break

                mp4_files = sorted(
                    [p for p in subfolder.glob("*.mp4") if p.is_file()],
                    key=lambda x: x.stat().st_mtime,
                    reverse=True
                )

                for mp4 in mp4_files:
                    try:
                        sz = mp4.stat().st_size
                    except Exception:
                        continue

                    fname = mp4.name
                    name_lower = fname.lower()

                    # 🚨 [10초 원테이크/중간본 원천 배제] 10초, 원테이크, temp, clip_, person_ 전면 차단
                    if any(w in name_lower for w in ["10초", "원테이크", "temp", "clip_", "person_"]):
                        continue

                    # 🚨 [최소 용량 2MB 미만 축소본/중간본 차단]
                    if sz < 2 * 1024 * 1024:
                        continue

                    # 🚨 [브랜드별 완제품 식별] Aura/Insurance는 22초숏폼, Stock은 32초/22초숏폼
                    is_valid_name = ("22초" in fname or "32초" in fname or "숏폼" in fname)
                    if not is_valid_name:
                        continue

                    # 🎬 [OpenCV 실물 비디오 재생 시간 검증 (>= 20.0초 필수)]
                    try:
                        import cv2
                        cap = cv2.VideoCapture(str(mp4.resolve()))
                        if not cap.isOpened():
                            continue
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                        cap.release()
                        dur_sec = (frame_count / fps) if fps and fps > 0 else 0
                        if dur_sec < 20.0:
                            logger.warning(f"⚠️ [OmniShortsWatcher 차단] 실측 재생시간 {dur_sec:.1f}초 (< 20.0초) 미달 파일 차단: {fname}")
                            continue
                    except Exception as ve:
                        logger.debug(f"실측 검증 예외 (통과): {ve}")

                    topic_id = self.extract_topic_id(fname) or self.extract_topic_id(subfolder.name)
                    if not topic_id:
                        continue

                    fpath_str = str(mp4)
                    file_age = time.time() - mp4.stat().st_mtime
                    if file_age < 10.0:
                        prev_sz = self._file_sizes_tracker.get(fpath_str, -1)
                        if prev_sz != sz:
                            self._file_sizes_tracker[fpath_str] = sz
                            continue
                    self._file_sizes_tracker[fpath_str] = sz

                    try:
                        import importlib
                        mod = importlib.import_module(binfo["pilot_module"])
                        pilot_cls = getattr(mod, binfo["pilot_class"])
                        pilot = pilot_cls()

                        if pilot.is_already_published_today(topic_id):
                            continue

                        logger.info("=" * 70)
                        logger.info(f"🚨 [OmniShortsWatcher] [{binfo['kr']}] 주제 #{topic_id} 신선 숏폼 완제품 포착!")
                        logger.info(f"📁 파일: {mp4.name} ({round(sz / 1024 / 1024, 2)} MB)")
                        logger.info(f"🚀 [100% 무인 숏폼 자율 송출 시작] 4대 SNS(유튜브+틱톡+클립+릴스) 즉시 발사!")
                        logger.info("=" * 70)

                        res = pilot.execute_single_slot(topic_id=topic_id, force=True)
                        logger.info(f"🎉 [{binfo['kr']}] 숏폼 주제 #{topic_id} 자율 송출 결과: {res.get('status')}")
                        dispatched.append({
                            "type": "shorts",
                            "brand": brand_key,
                            "topic_id": topic_id,
                            "file": mp4.name,
                            "result": res
                        })
                        brand_dispatched = True
                        break
                    except Exception as pe:
                        logger.error(f"❌ [{binfo['kr']}] 숏폼 주제 #{topic_id} 자율 송출 중 예외: {pe}")

        return dispatched

    def scan_and_dispatch_cardnews(self) -> List[Dict[str, Any]]:
        """1회 스캔: 미송출 신선 카드뉴스(PNG 슬라이드 세트) 즉각 자율 송출"""
        today_ymd = datetime.now().strftime("%Y%m%d")
        dispatched = []

        for brand_key, binfo in BRANDS_CARDNEWS_CONFIG.items():
            base_folder = binfo["folder"]
            if not base_folder.exists():
                continue

            subfolders = sorted(
                [f for f in base_folder.iterdir() if f.is_dir() and (today_ymd in f.name or "topic" in f.name.lower())],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )

            brand_dispatched = False
            for subfolder in subfolders:
                if brand_dispatched:
                    break

                # 폴더 내 슬라이드 이미지(PNG/JPG) 확인
                slides = sorted(list(subfolder.glob("*.png")) + list(subfolder.glob("*.jpg")))
                if len(slides) < 4:
                    continue

                topic_id = self.extract_topic_id(subfolder.name)
                if not topic_id:
                    continue

                # 폴더 수정 시간 확인 (최근 12시간 이내 생성된 신선 카드뉴스만 대상)
                folder_age = time.time() - subfolder.stat().st_mtime
                if folder_age > 12 * 3600:
                    continue

                try:
                    import importlib
                    mod = importlib.import_module(binfo["pilot_module"])
                    pilot_cls = getattr(mod, binfo["pilot_class"])
                    pilot = pilot_cls()

                    if pilot.is_already_published_today(topic_id):
                        continue

                    logger.info("=" * 70)
                    logger.info(f"🚨 [OmniCardnewsWatcher] [{binfo['kr']}] 카드뉴스 주제 #{topic_id} 완제품 포착!")
                    logger.info(f"📁 폴더: {subfolder.name} (슬라이드 {len(slides)}장)")
                    logger.info(f"🚀 [100% 무인 카드뉴스 자율 송출 시작] Meta(페북+인스타) 및 숏폼 변환 배포 즉시 발사!")
                    logger.info("=" * 70)

                    res = pilot.execute_single_slot(topic_id=topic_id, force=True)
                    logger.info(f"🎉 [{binfo['kr']}] 카드뉴스 주제 #{topic_id} 자율 송출 결과: {res.get('status')}")
                    dispatched.append({
                        "type": "cardnews",
                        "brand": brand_key,
                        "topic_id": topic_id,
                        "folder": subfolder.name,
                        "result": res
                    })
                    brand_dispatched = True
                    break
                except Exception as cne:
                    logger.error(f"❌ [{binfo['kr']}] 카드뉴스 주제 #{topic_id} 자율 송출 중 예외: {cne}")

        return dispatched

    def scan_and_dispatch(self) -> List[Dict[str, Any]]:
        """숏폼 + 카드뉴스 전수 자율 스캔 및 송출"""
        results = []
        results.extend(self.scan_and_dispatch_shorts())
        results.extend(self.scan_and_dispatch_cardnews())
        return results

    def run_loop(self, poll_interval_sec: int = 30):
        """상시 백그라운드 무한 감시 루프"""
        self._running = True
        logger.info(f"👀 [OmniMediaDesktopWatcher] 100% 무인 [숏폼 + 카드뉴스] 자동 감지 & 자율 송출 데몬 가동 시작 (주기: {poll_interval_sec}초)")
        while self._running:
            try:
                self.scan_and_dispatch()
            except Exception as e:
                logger.error(f"⚠️ [OmniMediaDesktopWatcher 루프 예외 - 자동 복구] {e}")
            time.sleep(poll_interval_sec)

    def start_background(self, poll_interval_sec: int = 30):
        """백그라운드 스레드로 비동기 기동"""
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(
            target=self.run_loop,
            args=(poll_interval_sec,),
            daemon=True,
            name="OmniMediaDesktopWatcherThread"
        )
        self._thread.start()
        logger.info("🚀 [OmniMediaDesktopWatcher] 백그라운드 감시 스레드 정상 등록 완료")

    def stop(self):
        self._running = False


# 싱글톤 인스턴스
omni_shorts_desktop_watcher = OmniShortsDesktopWatcher()


if __name__ == "__main__":
    print("👀 [OmniMediaDesktopWatcher] 숏폼 + 카드뉴스 1회 전수 검사 및 자율 송출 테스트...")
    watcher = OmniShortsDesktopWatcher()
    results = watcher.scan_and_dispatch()
    print(f"결과: {len(results)}건 처리됨")
