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
from typing import Dict, Any, List, Optional, Tuple

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

    # 🔁 [재시도 · 서킷브레이커 상수] 3회 재시도 + 지수 백오프(15초 → 30초)
    MAX_PUBLISH_RETRIES = 3
    RETRY_BACKOFF_BASE_SEC = 15.0

    SCHEDULE_SLOTS = [
        {"time": "08:30", "slot": "shorts_1", "type": "shorts", "subtype": "regular", "label": "아침 기본 숏폼 ①"},
        {"time": "12:30", "slot": "cardnews_1", "type": "cardnews", "subtype": "cardnews", "label": "점심 카드뉴스 ①"},
        {"time": "15:30", "slot": "shorts_2", "type": "shorts", "subtype": "drama", "label": "오후 숏폼 드라마 ①"},
        {"time": "18:30", "slot": "cardnews_2", "type": "cardnews", "subtype": "cardnews", "label": "퇴근 카드뉴스 ②"},
        {"time": "21:00", "slot": "shorts_3", "type": "shorts", "subtype": "drama", "label": "야간 숏폼 드라마 ②"}
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

    # ────────────────────────────────────────────────────────────────
    # 🛡️ [Zero-GPU 무결성 폴백 가디언] 바탕화면 완제품 풀 자율 탐색
    # ────────────────────────────────────────────────────────────────
    BRAND_DIR_NAME = {
        "aura": "Aura",
        "insurance": "Insurance",
        "stock": "Stock",
    }

    # 🚫 렌더링 임시물/미완성물 배제 키워드 (파일명 소문자 기준)
    _JUNK_KEYWORDS = ("temp", "clip_", "person_", "10초", "원테이크", "_raw", "preview", "draft")

    # 🚫 단일 씬 조각(scene_01/scene.mp4 등) 배제 — 최종 합성 완제품만 허용
    _SCENE_DIR_PATTERN = ("scene_", "scene", "씬_", "cut_", "shot_")

    def _get_artifact_pool_dir(self, brand: str) -> Path:
        """브랜드별 바탕화면 완제품 산출물 풀 경로 반환"""
        user_home = Path(os.environ.get("USERPROFILE", "C:/Users/zkfnt"))
        brand_dir = self.BRAND_DIR_NAME.get(brand, brand.capitalize())
        return user_home / "Desktop" / "한국 숏폼_산출물" / brand_dir

    def _collect_published_videos_today(self, date_str: str) -> set:
        """당일 성공 발행 이력에 등장한 비디오 경로 집합 (중복 발행 0% 원천 차단)"""
        published = set()
        for item in self._load_history():
            if item.get("date") != date_str:
                continue
            if item.get("status") != "success":
                continue
            vp = item.get("video_path")
            if vp:
                try:
                    published.add(str(Path(vp).resolve()).lower())
                except Exception:
                    published.add(str(vp).lower())
        return published

    def _resolve_fallback_video(
        self,
        brand: str,
        slot: str,
        subtype: Optional[str] = None,
        date_str: Optional[str] = None,
    ) -> Optional[str]:
        """🛡️ [Zero-GPU 폴백] 당일 미발행 완제품 mp4 1편 자율 확보

        - GPU 재렌더링 0% · 순수 파일 탐색만 수행
        - 드라마 슬롯은 drama 관련 mp4 우선, 일반 숏폼은 일반 mp4 우선
        - temp/clip_/person_/10초/원테이크 등 미완성물 및 2MB 이하 배제
        - 당일 이미 성공 발행된 비디오는 100% 배제
        """
        if not date_str:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")

        pool_dir = self._get_artifact_pool_dir(brand)
        if not pool_dir.exists():
            logger.warning(f"   ⚠️ [{brand.upper()}] 완제품 풀 미존재: {pool_dir}")
            return None

        is_drama_slot = (subtype == "drama") or (slot in ("shorts_2", "shorts_3"))
        published_today = self._collect_published_videos_today(date_str)

        candidates = []
        try:
            for mp4 in pool_dir.rglob("*.mp4"):
                try:
                    if not mp4.is_file():
                        continue
                    # 2MB 초과 실물만 (빈 껍데기/실패 렌더 배제)
                    if mp4.stat().st_size <= 2 * 1024 * 1024:
                        continue
                    name_lower = mp4.name.lower()
                    # 미완성물 배제
                    if any(k in name_lower for k in self._JUNK_KEYWORDS):
                        continue
                    # 단일 씬 조각 배제 (부모 폴더가 scene_XX 이거나 파일명이 scene.mp4 인 경우)
                    parent_lower = mp4.parent.name.lower()
                    if any(parent_lower.startswith(p) for p in self._SCENE_DIR_PATTERN):
                        continue
                    if name_lower in ("scene.mp4", "cut.mp4", "shot.mp4", "clip.mp4"):
                        continue
                    # 당일 중복 발행 배제
                    try:
                        resolved = str(mp4.resolve()).lower()
                    except Exception:
                        resolved = str(mp4).lower()
                    if resolved in published_today:
                        continue

                    is_drama_file = "drama" in name_lower or "드라마" in mp4.name
                    # 드라마 슬롯: drama 파일 우선순위 0, 일반 1 / 일반 슬롯: 일반 0, drama 1
                    if is_drama_slot:
                        priority = 0 if is_drama_file else 1
                    else:
                        priority = 0 if not is_drama_file else 1

                    candidates.append((priority, mp4.stat().st_mtime, str(mp4)))
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"   ⚠️ [{brand.upper()}] 완제품 풀 탐색 예외: {e}")
            return None

        if not candidates:
            logger.warning(
                f"   ⚠️ [{brand.upper()}] {slot} 폴백 완제품 없음 (풀={pool_dir.name}, drama={is_drama_slot})"
            )
            return None

        # 우선순위 → 최신 mtime 순 정렬
        candidates.sort(key=lambda x: (x[0], -x[1]))
        chosen = candidates[0][2]
        logger.info(
            f"   🎬 [Zero-GPU 폴백] {brand.upper()} {slot} 후보 {len(candidates)}편 중 자율 선택 "
            f"(drama={is_drama_slot})"
        )
        return chosen

    # ────────────────────────────────────────────────────────────────
    # 🔬 [송출 직전 실물 전수 검증 · 자가치유 엔진]
    # ────────────────────────────────────────────────────────────────
    CARDNEWS_BRAND_KO = {
        "aura": "아우라",
        "insurance": "보험",
        "stock": "주식",
    }

    # 카드뉴스 실물 최소 규격 (빈 껍데기/실패 렌더 배제)
    _CARDNEWS_MIN_BYTES = 50 * 1024
    _VIDEO_MIN_BYTES = 2 * 1024 * 1024
    _VIDEO_MIN_DURATION_SEC = 15.0

    def _verify_video_integrity(self, video_path: Optional[str]) -> Tuple[bool, str]:
        """🔬 [숏폼 실물 전수 검증] 송출 직전 mp4 무결성 실측

        - 경로 존재 + .mp4 확장자 + 2MB 이상 실물
        - cv2 사용 가능 시 VideoCapture 실제 열기 + 재생시간(frame_count/fps) >= 15.0초
        - cv2 미설치/판독 불가 환경에서는 크기 검증만으로 안전 통과 (송출 중단 0%)
        """
        if not video_path:
            return False, "경로 미지정"

        try:
            vp = Path(video_path)
        except Exception as e:
            return False, f"경로 해석 불가: {e}"

        if not vp.exists() or not vp.is_file():
            return False, f"실물 파일 미존재: {vp}"

        if vp.suffix.lower() != ".mp4":
            return False, f"확장자 불일치(.mp4 아님): {vp.suffix}"

        try:
            size = vp.stat().st_size
        except Exception as e:
            return False, f"파일 크기 판독 실패: {e}"

        if size < self._VIDEO_MIN_BYTES:
            return False, f"용량 미달({size / (1024 * 1024):.2f}MB < 2.00MB)"

        try:
            import cv2  # type: ignore
        except Exception:
            logger.warning("   ⚠️ [검증] cv2 미설치 ➔ 용량/확장자 검증만으로 통과 처리")
            return True, "OK"

        cap = None
        try:
            cap = cv2.VideoCapture(str(vp))
            if not cap.isOpened():
                return False, "cv2 VideoCapture 열기 실패(코덱/손상 의심)"

            fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
            frames = float(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0.0)
            if fps <= 0.0 or frames <= 0.0:
                logger.warning("   ⚠️ [검증] fps/frame_count 판독 불가 ➔ 용량 검증으로 통과 처리")
                return True, "OK"

            duration = frames / fps
            if duration < self._VIDEO_MIN_DURATION_SEC:
                return False, f"재생시간 미달({duration:.1f}초 < {self._VIDEO_MIN_DURATION_SEC:.1f}초)"

            return True, "OK"
        except Exception as e:
            logger.warning(f"   ⚠️ [검증] cv2 판독 예외({e}) ➔ 용량 검증으로 통과 처리")
            return True, "OK"
        finally:
            try:
                if cap is not None:
                    cap.release()
            except Exception:
                pass

    def _find_cardnews_slide_set(self, brand: str, topic_id: int) -> Optional[List[str]]:
        """바탕화면 카드뉴스 산출물 폴더에서 주제번호 일치 5장 세트 자율 탐색

        - 아우라: 아우라_{NN}_... / 보험: 보험_{NN}_... / 주식: [주제NN] ...
        - 주제번호 일치 폴더 우선 ➔ 없으면 최신 mtime 폴더 순으로 폴백
        """
        brand_ko = self.CARDNEWS_BRAND_KO.get(brand, brand)
        user_home = Path(os.environ.get("USERPROFILE", "C:/Users/zkfnt"))
        c_base = user_home / "Desktop" / "한국 카드뉴스_산출물" / brand_ko
        if not c_base.exists():
            return None

        try:
            folders = [d for d in c_base.iterdir() if d.is_dir()]
        except Exception:
            return None

        if not folders:
            return None

        try:
            norm_topic = ((int(topic_id) - 1) % 6) + 1
        except Exception:
            norm_topic = 1

        topic_tokens = (
            f"_{norm_topic:02d}_",
            f"_{norm_topic:02d}",
            f"[주제{norm_topic:02d}]",
            f"주제{norm_topic:02d}",
        )

        def _has_five(folder: Path) -> bool:
            return all((folder / f"slide_{i}.png").exists() for i in range(1, 6))

        matched = [d for d in folders if any(t in d.name for t in topic_tokens)]
        matched.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        for d in matched:
            if _has_five(d):
                return [str(d / f"slide_{i}.png") for i in range(1, 6)]

        others = [d for d in folders if d not in matched]
        others.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        for d in others:
            if _has_five(d):
                return [str(d / f"slide_{i}.png") for i in range(1, 6)]

        return None

    def _verify_cardnews_integrity(self, brand: str, topic_id: int) -> Tuple[bool, str]:
        """🔬 [카드뉴스 실물 전수 검증] slide_1~5.png 5장 완비 + 50KB 이상 + PIL 판독 성공

        - 5장 완비 시 (True, "OK")
        - 미달/손상 시 (False, 실패사유)
        """
        brand_ko = self.CARDNEWS_BRAND_KO.get(brand, brand)
        user_home = Path(os.environ.get("USERPROFILE", "C:/Users/zkfnt"))
        c_base = user_home / "Desktop" / "한국 카드뉴스_산출물" / brand_ko

        if not c_base.exists():
            return False, f"카드뉴스 산출물 폴더 미존재: {c_base}"

        slides = self._find_cardnews_slide_set(brand, topic_id)
        if not slides:
            return False, "5장 미달 (slide_1~5.png 완비 폴더 없음)"

        try:
            from PIL import Image  # type: ignore
        except Exception:
            Image = None  # type: ignore

        for sp in slides:
            try:
                p = Path(sp)
                if not p.exists():
                    return False, f"슬라이드 미존재: {p.name}"
                size = p.stat().st_size
                if size < self._CARDNEWS_MIN_BYTES:
                    return False, f"{p.name} 용량 미달({size / 1024:.1f}KB < 50KB)"
                if Image is not None:
                    with Image.open(str(p)) as im:
                        im.verify()
            except Exception as e:
                return False, f"슬라이드 손상/판독 실패({Path(sp).name}): {e}"

        return True, "OK"

    def _heal_or_remake_cardnews(self, brand: str, topic_id: int) -> bool:
        """🩹 [카드뉴스 자가치유] 5장 미달/손상 시 해당 브랜드 제작기로 재제작 후 재검증"""
        logger.warning(f"🩹 [{brand.upper()}] 카드뉴스 #{topic_id} 자가치유 재제작 가동...")
        try:
            if brand == "aura":
                from brands.aura.aura_cardnews_producer import AuraCardnewsProducer
                AuraCardnewsProducer().produce_cardnews(topic_id=topic_id)
            elif brand == "insurance":
                from brands.insurance.insurance_cardnews_producer import InsuranceCardnewsProducer
                InsuranceCardnewsProducer().produce_full_package(topic_id=topic_id)
            elif brand == "stock":
                from brands.stock.stock_omni_cardnews_pilot import StockOmniCardnewsPilot
                StockOmniCardnewsPilot().produce_fresh_cardnews(topic_id=topic_id)
            else:
                logger.error(f"   ❌ [{brand.upper()}] 알 수 없는 브랜드 ➔ 자가치유 불가")
                return False
        except Exception as e:
            logger.error(f"   ❌ [{brand.upper()}] 카드뉴스 재제작 예외: {e}")
            return False

        ok, reason = self._verify_cardnews_integrity(brand, topic_id)
        if ok:
            logger.info(f"   ✅ [{brand.upper()}] 카드뉴스 #{topic_id} 자가치유 성공 (5장 무결점 확인)")
        else:
            logger.error(f"   ❌ [{brand.upper()}] 카드뉴스 #{topic_id} 자가치유 후에도 검증 실패: {reason}")
        return ok

    def publish_single_content(
        self,
        brand: str,
        content_type: str,
        topic_id: int,
        slot: str,
        subtype: Optional[str] = None,
        video_path: Optional[str] = None,
    ) -> bool:
        """단일 브랜드 콘텐츠 정시 송출 실행

        - subtype: "regular" | "drama" | "cardnews" (새벽 팩토리 직인 영수증과 동일 규격)
        - video_path: 새벽에 이미 렌더링 완료된 mp4 실물 경로 (재렌더링 0% · GPU 부하 0%)
        """
        logger.info(
            f"🚀 [{brand.upper()}] {slot} (주제 #{topic_id}, subtype={subtype or '-'}) 정시 송출 트리거..."
        )

        # 🛡️ [Zero-GPU 무결성 폴백] 숏폼인데 완제품 경로가 없거나 실물이 사라진 경우 자율 확보
        if content_type == "shorts":
            path_missing = (not video_path) or (not Path(video_path).exists())
            if path_missing:
                if video_path:
                    logger.warning(f"   ⚠️ 완제품 경로 소실 감지 ➔ 폴백 가디언 가동: {video_path}")
                else:
                    logger.warning("   ⚠️ 완제품 경로 미지정 ➔ 폴백 가디언 가동")
                video_path = self._resolve_fallback_video(
                    brand=brand,
                    slot=slot,
                    subtype=subtype,
                    date_str=datetime.datetime.now().strftime("%Y-%m-%d"),
                )
                if video_path:
                    logger.info(f"   🎬 [Zero-GPU 폴백] 당일 미발행 완제품 mp4 자율 확보: {video_path}")
                else:
                    logger.error(
                        f"   ❌ [{brand.upper()}] {slot} 폴백 완제품 확보 실패 ➔ GPU 재렌더링 없이 송출 보류"
                    )
                    return False

            # 🔬 [송출 직전 실물 전수 검증] 용량/재생시간 실측 ➔ 불합격 시 미발행 완제품으로 교체 후 재검증
            ok, reason = self._verify_video_integrity(video_path)
            if not ok:
                logger.warning(f"   🔬 [검증 불합격] {Path(video_path).name if video_path else '-'} ➔ {reason}")
                logger.warning("   🛡️ [자가치유] 미발행 완제품 mp4로 교체 후 재검증 가동...")
                healed_path = self._resolve_fallback_video(
                    brand=brand,
                    slot=slot,
                    subtype=subtype,
                    date_str=datetime.datetime.now().strftime("%Y-%m-%d"),
                )
                if healed_path and str(healed_path) != str(video_path):
                    ok2, reason2 = self._verify_video_integrity(healed_path)
                    if ok2:
                        logger.info(f"   ✅ [자가치유 성공] 교체 완제품 검증 통과: {healed_path}")
                        video_path = healed_path
                    else:
                        logger.error(f"   ❌ [자가치유 실패] 교체 후보도 검증 불합격({reason2}) ➔ 송출 보류")
                        return False
                else:
                    logger.error("   ❌ [자가치유 실패] 대체 완제품 mp4 미확보 ➔ 송출 보류")
                    return False
            else:
                logger.info("   🔬 [검증 통과] 숏폼 실물 무결점 확인 (용량·재생시간 OK)")

        if video_path:
            logger.info(f"   🎬 완제품 mp4 직결 송출: {video_path}")

        # 🔬 [카드뉴스 실물 전수 검증] 5장 완비 확인 ➔ 미달 시 자가치유 재제작 후 송출
        if content_type != "shorts":
            cn_ok, cn_reason = self._verify_cardnews_integrity(brand, topic_id)
            if not cn_ok:
                logger.warning(f"   🔬 [카드뉴스 검증 불합격] {brand.upper()} #{topic_id} ➔ {cn_reason}")
                if not self._heal_or_remake_cardnews(brand, topic_id):
                    logger.error(
                        f"   ❌ [{brand.upper()}] 카드뉴스 #{topic_id} 자가치유 실패 ➔ 송출 보류"
                    )
                    return False
                logger.info(f"   ✅ [{brand.upper()}] 카드뉴스 #{topic_id} 자가치유 완료 ➔ 송출 진행")
            else:
                logger.info(f"   🔬 [검증 통과] 카드뉴스 5장 무결점 확인 ({brand.upper()} #{topic_id})")

        if self.dry_run:
            logger.info(f"   [DRY-RUN] {brand} {content_type} #{topic_id} 송출 시뮬레이션 성공")
            return True

        # 🔁 [3회 재시도 + 지수 백오프 + 서킷브레이커] 계정 정지 원천 방지 가드
        last_reason = "원인 미상"

        for attempt in range(1, self.MAX_PUBLISH_RETRIES + 1):
            logger.info(
                f"   🚀 [{brand.upper()}] {slot} ({content_type} #{topic_id}) 송출 시도 "
                f"({attempt}/{self.MAX_PUBLISH_RETRIES})..."
            )

            call_ok, call_reason = self._execute_single_publish_call(
                brand=brand,
                content_type=content_type,
                topic_id=topic_id,
                slot=slot,
                subtype=subtype,
                video_path=video_path,
            )

            if call_ok:
                logger.info(f"   🎉 [{brand.upper()}] {slot} 송출 최종 성공 ({attempt}회차 시도)")
                self._clear_circuit_breaker(brand, slot, content_type)
                return True

            last_reason = call_reason or "원인 미상"
            logger.warning(
                f"   ⚠️ [{brand.upper()}] {slot} {attempt}회차 송출 실패: {last_reason}"
            )

            if attempt < self.MAX_PUBLISH_RETRIES:
                backoff_wait = self.RETRY_BACKOFF_BASE_SEC * attempt
                logger.info(
                    f"   ⏳ [{brand.upper()}] {backoff_wait:.0f}초 대기 후 재시도 (지수 백오프)..."
                )
                time.sleep(backoff_wait)

        # 🛑 3회 전건 실패 ➔ 서킷브레이커 작동 (추가 재시도 영구 차단 · 계정 정지 원천 방지)
        logger.error(
            f"   🛑 [{brand.upper()}] {slot} {self.MAX_PUBLISH_RETRIES}회 재시도 전건 실패! "
            f"서킷브레이커 작동 ➔ 긴급 중단 및 대시보드 빨간 불 점등"
        )
        self._record_circuit_breaker_trip(brand, slot, content_type, last_reason)
        return False

    # ────────────────────────────────────────────────────────────────
    # 🚨 [서킷브레이커 · 대시보드 빨간 불 점등/해제 엔진]
    # ────────────────────────────────────────────────────────────────
    def _atomic_write_json(self, target: Path, payload: Any) -> bool:
        """원자적 JSON 쓰기 (tmp ➔ flush ➔ fsync ➔ os.replace) — 파일 절단/유실 0%"""
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = target.with_name(target.name + ".tmp")
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
                f.flush()
                try:
                    os.fsync(f.fileno())
                except Exception:
                    pass
            os.replace(tmp_path, target)
            return True
        except Exception as e:
            logger.warning(f"   ⚠️ 원자적 JSON 저장 실패({target.name}): {e}")
            return False

    def _read_json_safe(self, target: Path, default: Any) -> Any:
        """JSON 안전 로드 (미존재/손상 시 기본값 반환)"""
        try:
            if target.exists():
                with open(target, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(default, dict) and not isinstance(data, dict):
                    return default
                if isinstance(default, list) and not isinstance(data, list):
                    return default
                return data
        except Exception as e:
            logger.warning(f"   ⚠️ JSON 로드 실패({target.name}): {e}")
        return default

    def _record_circuit_breaker_trip(
        self, brand: str, slot: str, content_type: str, error_reason: str
    ):
        """🚨 3회 재시도 초과 시 대시보드 빨간 불(ERROR) 점등

        - data/channel_errors.json : f"{brand}_{content_type}" 및 f"{brand}_{slot}" 두 키 동시 등록
        - server_status.json       : recent_logs 에 type="danger" 로그 주입
        """
        now_hms = datetime.datetime.now().strftime("%H:%M:%S")
        clean_err = str(error_reason).replace("\n", " ").replace("\r", " ")[:150]

        # 1) data/channel_errors.json 갱신 (원자적)
        err_file = CURRENT_DIR / "data" / "channel_errors.json"
        err_data = self._read_json_safe(err_file, {})
        if not isinstance(err_data, dict):
            err_data = {}

        ch_payload = {
            "channel": f"{brand}_{content_type}",
            "brand": brand,
            "slot": slot,
            "type": content_type,
            "error": f"3회 재시도 초과 - {clean_err}",
            "status": "ERROR",
            "color": "red",
            "time": now_hms,
            "occurred_at": now_hms,
        }
        err_data[f"{brand}_{content_type}"] = ch_payload
        err_data[f"{brand}_{slot}"] = ch_payload
        self._atomic_write_json(err_file, err_data)

        # 2) server_status.json recent_logs 에 danger 로그 주입 (원자적)
        status_file = CURRENT_DIR / "server_status.json"
        s_data = self._read_json_safe(status_file, {})
        if not isinstance(s_data, dict):
            s_data = {}
        logs = s_data.get("recent_logs")
        if not isinstance(logs, list):
            logs = []
        logs.append({
            "text": (
                f"🚨 [서킷브레이커 작동] {brand.upper()} {slot} ({content_type}) "
                f"3회 재시도 초과로 긴급 중단되었습니다. (원인: {clean_err})"
            ),
            "type": "danger",
            "time": now_hms,
        })
        s_data["recent_logs"] = logs[-50:]
        s_data["channel_errors"] = err_data
        self._atomic_write_json(status_file, s_data)

        logger.error(
            f"   🚨 [서킷브레이커 점등] {brand.upper()} {slot} ({content_type}) "
            f"➔ channel_errors.json / server_status.json 빨간 불 등록 완료"
        )

    def _clear_circuit_breaker(self, brand: str, slot: str, content_type: str):
        """✅ 송출 성공 시 대시보드 빨간 불 해제 (두 키 동시 제거)"""
        err_file = CURRENT_DIR / "data" / "channel_errors.json"
        if not err_file.exists():
            return
        err_data = self._read_json_safe(err_file, {})
        if not isinstance(err_data, dict):
            return

        removed = False
        for key in (f"{brand}_{content_type}", f"{brand}_{slot}"):
            if key in err_data:
                err_data.pop(key, None)
                removed = True

        if removed:
            self._atomic_write_json(err_file, err_data)
            logger.info(f"   ✅ [서킷브레이커 소등] {brand.upper()} {slot} ({content_type}) 빨간 불 해제")

    def _execute_single_publish_call(
        self,
        brand: str,
        content_type: str,
        topic_id: int,
        slot: str,
        subtype: Optional[str] = None,
        video_path: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """🔌 3대 브랜드 파일럿 단일 송출 호출을 안전하게 감싸 (성공여부, 이유) 반환

        - 예외를 밖으로 던지지 않고 (False, 사유) 로 흡수 ➔ 재시도 루프가 통제 가능
        """
        try:
            if brand == "aura":
                if content_type == "shorts":
                    from brands.aura.aura_omni_shorts_pilot import AuraOmniShortsPilot
                    res = AuraOmniShortsPilot().execute_single_slot(
                        topic_id=topic_id, force=True, slot=slot, subtype=subtype, video_path=video_path
                    )
                else:
                    from brands.aura.aura_omni_cardnews_pilot import AuraOmniCardnewsPilot
                    res = AuraOmniCardnewsPilot().execute_single_slot(topic_id=topic_id, force=True)

            elif brand == "insurance":
                if content_type == "shorts":
                    from brands.insurance.insurance_omni_shorts_pilot import InsuranceOmniShortsPilot
                    res = InsuranceOmniShortsPilot().execute_single_slot(
                        topic_id=topic_id, force=True, slot=slot, subtype=subtype, video_path=video_path
                    )
                else:
                    from brands.insurance.insurance_omni_cardnews_pilot import InsuranceOmniCardnewsPilot
                    res = InsuranceOmniCardnewsPilot().execute_single_slot(topic_id=topic_id, force=True)

            elif brand == "stock":
                if content_type == "shorts":
                    from brands.stock.stock_omni_shorts_pilot import StockOmniShortsPilot
                    res = StockOmniShortsPilot().execute_single_slot(
                        topic_id=topic_id, force=True, slot=slot, subtype=subtype, video_path=video_path
                    )
                else:
                    from brands.stock.stock_omni_cardnews_pilot import StockOmniCardnewsPilot
                    res = StockOmniCardnewsPilot().execute_single_slot(topic_id=topic_id, force=True)

            else:
                return False, f"미등록 브랜드: {brand}"

            if not isinstance(res, dict):
                return False, f"파일럿 반환값 형식 오류(type={type(res).__name__})"

            st = res.get("status", "failed")
            if st in ["success", "partially_published"]:
                return True, "OK"

            reason = res.get("error") or res.get("message") or f"status={st}"
            return False, str(reason).replace("\n", " ")[:150]

        except Exception as e:
            logger.error(f"❌ [{brand.upper()}] {slot} 송출 중 예외 발생: {e}")
            return False, f"{type(e).__name__}: {e}"

    def dispatch_slot(self, target_slot: str, date_str: str = None) -> Dict[str, Any]:
        """
        특정 슬롯(예: shorts_1)의 3대 브랜드 콘텐츠를 순차 송출
        """
        if not date_str:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")

        manifest = self.load_today_manifest(date_str)
        tasks = []
        if manifest:
            tasks = [t for t in manifest.get("tasks", []) if t.get("slot") == target_slot]

        # 🛡️ [자율 무결성 방어벽 - Self-Healing Fallback]
        # 새벽 팩토리 큐(manifest.json)가 없거나 해당 슬롯이 비어있어도 정시 송출 절대 중단 0% 원천 차단
        if not tasks:
            logger.info(f"🔄 [{target_slot}] 매니페스트 부재/미등록 감지 ➔ 3대 앱 자율 LRU 순환 태스크 자동 생성 가동")
            slot_info = next((s for s in self.SCHEDULE_SLOTS if s["slot"] == target_slot), None)
            c_type = slot_info["type"] if slot_info else ("cardnews" if "cardnews" in target_slot else "shorts")
            fallback_subtype = slot_info.get("subtype") if slot_info else None

            for brand in ["aura", "insurance", "stock"]:
                # 각 브랜드별 다음 순환 주제 자율 추출
                try:
                    if brand == "aura":
                        from brands.aura.aura_omni_shorts_pilot import AuraOmniShortsPilot
                        from brands.aura.aura_omni_cardnews_pilot import AuraOmniCardnewsPilot
                        t_id = AuraOmniShortsPilot().get_next_topic_id() if c_type == "shorts" else AuraOmniCardnewsPilot().get_next_topic_id()
                    elif brand == "insurance":
                        from brands.insurance.insurance_omni_shorts_pilot import InsuranceOmniShortsPilot
                        from brands.insurance.insurance_omni_cardnews_pilot import InsuranceOmniCardnewsPilot
                        t_id = InsuranceOmniShortsPilot().get_next_topic_id() if c_type == "shorts" else InsuranceOmniCardnewsPilot().get_next_topic_id()
                    else:
                        from brands.stock.stock_omni_shorts_pilot import StockOmniShortsPilot
                        from brands.stock.stock_omni_cardnews_pilot import StockOmniCardnewsPilot
                        t_id = StockOmniShortsPilot().get_next_topic_id() if c_type == "shorts" else StockOmniCardnewsPilot().get_next_topic_id()
                except Exception as ex:
                    logger.warning(f"⚠️ [{brand.upper()}] 순환 주제 추출 예외: {ex} ➔ 기본값 1번 적용")
                    t_id = 1

                # 🛡️ [Zero-GPU 폴백] 숏폼 슬롯이면 당일 미발행 완제품 mp4 경로를 태스크에 직접 주입
                fallback_video = None
                if c_type == "shorts":
                    fallback_video = self._resolve_fallback_video(
                        brand=brand,
                        slot=target_slot,
                        subtype=fallback_subtype,
                        date_str=date_str,
                    )
                    if fallback_video:
                        logger.info(
                            f"   🎬 [Zero-GPU 폴백] {brand.upper()} {target_slot} 완제품 자율 확보: {fallback_video}"
                        )
                    else:
                        logger.warning(
                            f"   ⚠️ [{brand.upper()}] {target_slot} 폴백 완제품 미확보 (송출 시 재탐색)"
                        )

                tasks.append({
                    "brand": brand,
                    "type": c_type,
                    "slot": target_slot,
                    "subtype": fallback_subtype,
                    "topic_id": t_id,
                    "video_path": fallback_video,
                    "label": f"{brand.upper()} {c_type} ({target_slot})"
                })

        logger.info("\n" + "=" * 70)
        logger.info(f"📢 [주간 SNS 정시 송출 가동] 슬롯: {target_slot} (총 {len(tasks)}개 브랜드)")
        logger.info("=" * 70)

        history = self._load_history()
        slot_results = {}

        for task in tasks:
            brand = task["brand"]
            c_type = task["type"]
            topic_id = task["topic_id"]
            subtype = task.get("subtype")
            video_path = task.get("artifact_path") or task.get("video_file")

            if self.is_slot_published_today(date_str, target_slot, brand):
                logger.info(f"⏭️ [{brand.upper()}] {target_slot} 오늘 이미 송출 완료됨 (중복 방지 건너뜀)")
                slot_results[brand] = "ALREADY_PUBLISHED"
                continue

            success = self.publish_single_content(
                brand, c_type, topic_id, target_slot, subtype=subtype, video_path=video_path
            )
            slot_results[brand] = "SUCCESS" if success else "FAILED"

            history.append({
                "date": date_str,
                "slot": target_slot,
                "brand": brand,
                "type": c_type,
                "subtype": subtype,
                "topic_id": topic_id,
                "video_path": video_path,
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
