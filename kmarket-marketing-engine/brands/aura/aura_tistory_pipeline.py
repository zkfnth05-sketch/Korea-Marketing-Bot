# -*- coding: utf-8 -*-
"""
💖 Aura 데이팅 Tistory Pipeline (🚀 💖 Aura 데이팅 전용 티스토리 무인 자율 파이프라인)
========================================================================================
- 브랜드: 💖 Aura 데이팅
- 역할:
  1. 📚 100대 황금 주제 순환 기획 & Gemini SEO 2,000자 칼럼 생성
  2. 🎨 16:9 와이드 비주얼 사진 매칭
  3. 🤖 크롬 영구 프로필 기반 티스토리 100% 무인 자동 발행 (AuraTistoryPipeline)
  4. 🔄 24시간 세션 킵얼라이브(Keep-Alive) 자동 연장
  5. 📁 독립 히스토리 DB (data/aura_tistory_history.json) 저장 및 일일 캡 제어
"""

import os
import sys
import json
import time
import logging
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# UTF-8 콘솔 지원
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AuraTistoryPipeline")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

STATE_FILE = DATA_DIR / "aura_tistory_daily_state.json"
HISTORY_FILE = DATA_DIR / "aura_tistory_history.json"
GOLDEN_HOURS = [9, 14, 19]


class AuraTistoryPipeline:
    """💖 Aura 데이팅 전용 티스토리 블로그 독립 무인 자동 파이프라인"""

    DAILY_QUOTA = 3  # 블로그 도배 방지 안전 일일 한도

    def __init__(self):
        from brands.aura.aura_tistory_publisher import AuraTistoryPublisher
        from brands.aura.aura_blog_engine import AuraBlogEngine

        self.publisher = AuraTistoryPublisher()
        self.engine = AuraBlogEngine()
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        default_state = {
            "current_topic_index": 0,
            "last_topic_id": 1,
            "last_run_time": None,
            "last_title": None,
            "last_url": None,
            "published_count": 0,
            "history": []
        }
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in default_state.items():
                        if k not in data:
                            data[k] = v
                    return data
            except Exception as e:
                logger.warning(f"⚠️ [💖 Aura 데이팅 Tistory] 상태 파일 로드 실패 (초기화): {e}")
        return default_state

    def _save_state(self):
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ [💖 Aura 데이팅 Tistory] 상태 저장 실패: {e}")

    def _load_history(self) -> List[Dict[str, Any]]:
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_history_record(self, record: Dict[str, Any]):
        hist = self._load_history()
        hist.insert(0, record)
        hist = hist[:100]  # 최근 100건 보존
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(hist, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ [💖 Aura 데이팅 Tistory] 히스토리 저장 실패: {e}")

    def can_publish_today(self) -> tuple[bool, str]:
        """일일 발행 캡 및 최소 쿨타임(2시간) 안전 검증"""
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        history = self._load_history()
        today_posts = [h for h in history if (h.get("published_at") or "").startswith(today_str) and h.get("status") == "success"]

        if len(today_posts) >= self.DAILY_QUOTA:
            return False, f"⚠️ [일일 한도 도달] 오늘 이미 {len(today_posts)}건 발행 완료 (최대 {self.DAILY_QUOTA}건 제한)"

        if today_posts:
            last_pub_str = today_posts[0].get("published_at", "")
            try:
                last_dt = datetime.datetime.strptime(last_pub_str, "%Y-%m-%d %H:%M:%S")
                diff_hours = (datetime.datetime.now() - last_dt).total_seconds() / 3600.0
                if diff_hours < 2.0:
                    return False, f"⚠️ [안전 쿨타임] 직전 발행 후 최소 2시간 대기 필요 (경과: {diff_hours:.1f}시간)"
            except Exception:
                pass

        return True, "발행 가능"

    def keep_alive(self) -> Dict[str, Any]:
        """티스토리 세션 24시간 수명 자동 연장 (Keep-Alive)"""
        logger.info(f"🔄 [💖 Aura 데이팅 Tistory] 카카오 세션 킵얼라이브 가동...")
        res = self.publisher.keep_alive_session()
        logger.info(f"👉 [💖 Aura 데이팅 Tistory Keep-Alive 결과] {res.get('status')} - {res.get('message')}")
        return res

    def get_status(self) -> Dict[str, Any]:
        """현재 파이프라인 및 세션 상태 종합 보고"""
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        history = self._load_history()
        today_success = [h for h in history if (h.get("published_at") or "").startswith(today_str) and h.get("status") == "success"]
        
        return {
            "brand": "aura",
            "brand_name": "💖 Aura 데이팅",
            "is_available": self.publisher.is_available(),
            "today_count": len(today_success),
            "daily_quota": self.DAILY_QUOTA,
            "current_topic_index": self.state.get("current_topic_index", 0),
            "last_title": self.state.get("last_title"),
            "last_url": self.state.get("last_url"),
            "last_run_time": self.state.get("last_run_time"),
            "history_count": len(history)
        }

    def run_cycle(self, force_topic_id: Optional[int] = None, force: bool = False, dry_run: bool = False) -> Dict[str, Any]:
        """
        🚀 [티스토리 단독 무인 자율 발행 1회 사이클]
        1. 안전 가드레일 (일일 3건 캡, force=True 시 우회)
        2. 100대 주제 교차 순환 순번 자동 결정
        3. Gemini 2,000자 SEO 칼럼 + 16:9 와이드 맞춤 사진 패키지 생성
        4. TistoryPublisher 무인 발행 실행 (TinyMCE 동기화 + 태그 등록 + 공개 발행)
        5. 성공 URL 파싱, 히스토리 저장, 다음 주제 순환 갱신
        """
        if not force and force_topic_id is None:
            can_pub, reason = self.can_publish_today()
            if not can_pub:
                logger.warning(f"🛑 [💖 Aura 데이팅 Tistory] {reason}")
                return {"status": "BLOCKED_DAILY_CAP", "message": reason}

        # 순환 순서 가져오기
        try:
            from brands.aura.aura_100_topics import get_interleaved_topic_order
            interleaved_order = get_interleaved_topic_order()
        except Exception:
            interleaved_order = list(range(1, 101))

        total_topics = len(interleaved_order)

        if force_topic_id is not None:
            topic_id = force_topic_id
        else:
            cur_idx = self.state.get("current_topic_index", 0)
            topic_id = interleaved_order[cur_idx % total_topics]

        logger.info(f"🚀 [💖 Aura 데이팅 Tistory Pipeline] 주제 #{topic_id} 단독 무인 발행 사이클 시작...")

        # 1. 기사 패키지 생성
        try:
            package = self.engine.build_article_package(topic_id=topic_id, use_gemini=True)
        except Exception as e:
            logger.error(f"❌ [💖 Aura 데이팅 Tistory] 칼럼 생성 실패: {e}")
            return {"status": "error", "message": f"칼럼 생성 실패: {e}"}

        title_tistory = package.get("title_tistory") or package.get("title", "")
        content_html = package.get("content_html", "")
        tags = package.get("tags") or ['Aura', '소개팅', '연애심리', '2030매거진', '데이트코스']

        logger.info(f"📝 [💖 Aura 데이팅 Tistory 칼럼 준비 완료]")
        logger.info(f"  - 제목: {title_tistory}")
        logger.info(f"  - 본문 길이: {len(content_html)}자")
        logger.info(f"  - 태그: {tags}")

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 2. 모의 또는 실제 발행
        if dry_run:
            logger.info("🧪 [DRY-RUN] 모의 발행 완료 (실제 게시 생략)")
            pub_res = {
                "status": "success",
                "blog_name": self.publisher.blog_name,
                "title": title_tistory,
                "url": f"https://{self.publisher.blog_name}.tistory.com/dry-run-{topic_id}",
                "tags": tags
            }
        else:
            pub_res = self.publisher.publish_post(
                title=title_tistory,
                content_html=content_html,
                tag_list=tags
            )

        post_url = pub_res.get("url", "")
        status = pub_res.get("status", "error")

        # 3. 히스토리 기록
        record = {
            "brand": "aura",
            "topic_id": topic_id,
            "title": title_tistory,
            "content_length": len(content_html),
            "image_url": package.get("image_url", ""),
            "tags": tags,
            "status": status,
            "published_url": post_url,
            "published_at": now_str,
            "error_message": pub_res.get("message") if status != "success" else None
        }
        self._save_history_record(record)

        if status == "success":
            next_idx = (self.state.get("current_topic_index", 0) + 1) % total_topics
            self.state["current_topic_index"] = next_idx
            self.state["last_topic_id"] = topic_id
            self.state["last_run_time"] = now_str
            self.state["last_title"] = title_tistory
            self.state["last_url"] = post_url
            self.state["published_count"] = self.state.get("published_count", 0) + 1
            self._save_state()

            logger.info(f"🎉 [💖 Aura 데이팅 Tistory Pipeline] 단독 발행 대성공! URL: {post_url} (다음 주제: #{next_idx + 1})")
            return {
                "status": "success",
                "brand": "aura",
                "topic_id": topic_id,
                "next_topic_id": next_idx + 1,
                "title": title_tistory,
                "url": post_url,
                "published_at": now_str,
                "record": record
            }
        else:
            logger.warning(f"⚠️ [💖 Aura 데이팅 Tistory Pipeline] 발행 실패: {pub_res.get('message')}")
            return {
                "status": status,
                "brand": "aura",
                "topic_id": topic_id,
                "message": pub_res.get("message"),
                "record": record
            }

    def start_daemon(self, is_running_checker=None, on_log=None):
        """
        🔄 [24시간 무인 상주 스케줄러]
        - 정시 골든타임 자동 포스팅
        - 4시간 간격 카카오 티스토리 세션 킵얼라이브 자동 순환
        """
        start_msg = f"🚀 [💖 Aura 데이팅 Tistory Daemon] 골든타임 정시 발행 & 4시간 주기 세션 킵얼라이브 상주 가동 시작!"
        logger.info(start_msg)
        if on_log:
            on_log(start_msg, "success")

        last_executed_slot = None
        last_keepalive_time = 0

        while True:
            if is_running_checker and not is_running_checker():
                stop_msg = f"⏹️ [💖 Aura 데이팅 Tistory Daemon] 종료 신호 수신으로 데몬이 정지되었습니다."
                logger.info(stop_msg)
                if on_log:
                    on_log(stop_msg, "warning")
                break

            try:
                now = datetime.datetime.now()
                hour = now.hour
                date_str = now.strftime("%Y-%m-%d")
                now_ts = time.time()

                # 1. 4시간 주기 세션 킵얼라이브 자동 연장
                if now_ts - last_keepalive_time > 14400:  # 4시간 = 14400초
                    last_keepalive_time = now_ts
                    ka_res = self.keep_alive()
                    ka_msg = f"🔄 [💖 Aura 데이팅 Tistory] 세션 킵얼라이브 주기 실행: {ka_res.get('status')}"
                    logger.info(ka_msg)
                    if on_log:
                        on_log(ka_msg, "info")

                # 2. 골든타임 정시 발행
                for g_hour in GOLDEN_HOURS:
                    slot_key = f"{date_str}_{g_hour}"
                    if hour == g_hour and last_executed_slot != slot_key:
                        alert_msg = f"⏰ [💖 Aura 데이팅 Tistory] 골든타임 도달: {g_hour}:00 KST ➔ 티스토리 자동 발행 시작!"
                        logger.info(alert_msg)
                        if on_log:
                            on_log(alert_msg, "info")

                        res = self.run_cycle()
                        if res.get("status") == "success":
                            fin_msg = f"🎉 [💖 Aura 데이팅 Tistory] {g_hour}:00 발행 완료! {res.get('url')}"
                            logger.info(fin_msg)
                            if on_log:
                                on_log(fin_msg, "success")
                        else:
                            fail_msg = f"⚠️ [💖 Aura 데이팅 Tistory] {g_hour}:00 발행 결과: {res.get('status')} ({res.get('message')})"
                            logger.warning(fail_msg)
                            if on_log:
                                on_log(fail_msg, "warning")

                        last_executed_slot = slot_key
                        break

                for _ in range(3):
                    if is_running_checker and not is_running_checker():
                        break
                    time.sleep(10)

            except KeyboardInterrupt:
                logger.info(f"🛑 [💖 Aura 데이팅 Tistory Daemon] 사용자에 의해 정지되었습니다.")
                break
            except Exception as e:
                err_msg = f"⚠️ [💖 Aura 데이팅 Tistory Daemon] 루프 오류: {e}"
                logger.error(err_msg)
                if on_log:
                    on_log(err_msg, "error")
                time.sleep(15)


if __name__ == "__main__":
    pipeline = AuraTistoryPipeline()

    if "--now" in sys.argv or "-n" in sys.argv:
        print(f"\n=== [💖 Aura 데이팅 Tistory] 즉시 1회 발행 테스트 ===")
        res = pipeline.run_cycle(force=True)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif "--dry" in sys.argv:
        print(f"\n=== [💖 Aura 데이팅 Tistory] 모의(DRY-RUN) 테스트 ===")
        res = pipeline.run_cycle(dry_run=True, force=True)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif "--keepalive" in sys.argv or "-k" in sys.argv:
        print(f"\n=== [💖 Aura 데이팅 Tistory] 세션 킵얼라이브 실행 ===")
        res = pipeline.keep_alive()
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif "--status" in sys.argv or "-s" in sys.argv:
        st = pipeline.get_status()
        print(json.dumps(st, ensure_ascii=False, indent=2))
    elif "--daemon" in sys.argv or "-d" in sys.argv:
        pipeline.start_daemon()
    else:
        print("사용법:")
        print("  python aura_tistory_pipeline.py --now        (즉시 1회 자동 생성 & 티스토리 단독 발행)")
        print("  python aura_tistory_pipeline.py --dry        (모의 테스트, 실제 발행 안함)")
        print("  python aura_tistory_pipeline.py --keepalive  (카카오 티스토리 세션 24시간 즉시 연장)")
        print("  python aura_tistory_pipeline.py --status     (현재 상태 및 히스토리 조회)")
        print("  python aura_tistory_pipeline.py --daemon     (24시간 무인 자율 상주 스케줄러 가동)")
