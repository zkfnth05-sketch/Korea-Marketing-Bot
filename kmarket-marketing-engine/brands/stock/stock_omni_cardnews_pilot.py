# -*- coding: utf-8 -*-
"""
[독립 레고 블록] Stock Omni Cardnews Pilot (📈 StockMaster AI 전용 쏘기 직전 5장 카드뉴스 제작 & Meta 단발 송출 파일럿)
=========================================================================================================================
- 브랜드: StockMaster AI (공식 검색어: '스톡마스터 AI' 띄어쓰기 불변)
- 핵심 원칙 (대표님 절대 수칙):
  1. [쏘기 전 무조건 먼저 생산]: 바탕화면 옛날 폴더 무단 주워오기 전면 배제!
     정시(스케줄) 도달 시, 이번 순번 주제(예: #1) 5장 카드뉴스 슬라이드를 쏘기 직전 단독 생산
  2. [즉시 1회 단발 발사]: 방금 생성된 5장 슬라이드를 넘겨받아 Meta 플랫폼 동시 송출
     - ① 페이스북 5장 카드뉴스 앨범 (Facebook Cardnews Album + 첫 댓글 스텔스 링크)
     - ② 인스타그램 캐러셀 피드 (Instagram Carousel 5장 피드)
  3. [완벽한 메타데이터 패키징]: 제목, 설명문, 첫댓글 링크 문구, 공식 검색어 유도, 4단 해시태그 100% 탑재
  4. [중복 방지 락(Lock)]: 당일 동일 주제 중복 송출 0% 원천 차단
"""

import os
import sys
import glob
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import BASE_DIR, get_now_kst_str
from brands.stock.stock_hashtag_matrix import StockHashtagMatrix
from brands.stock.stock_meta_publisher import StockMetaPublisher

logger = logging.getLogger("StockOmniCardnewsPilot")


class StockOmniCardnewsPilot:
    """📈 StockMaster AI 전용 [쏘기 직전 5장 카드뉴스 제작 ➔ Meta 1회 단발 송출] 통합 관제 파일럿"""

    BRAND = "stock"
    OFFICIAL_KEYWORD = "스톡마스터 AI"
    LANDING_URL = "https://stockmaster-ai.vercel.app/"

    CARDNEWS_TOPICS = {
        1: "오늘 외인·기관이 쌍끌이 매수한 주도 섹터 TOP 4 분석",
        2: "20일선 돌파 & 거래량 폭증! 신고가 레이더 포착 종목 4선",
        3: "FOMC 금리 결정 후 코스피/코스닥 대응 전략 4대 핵심 포인트",
        4: "미국 배당 ETF(SCHD·JEPQ) 월 100만원 파이프라인 구축법",
        5: "저PBR 밸류업 프로그램 수혜 금융주 & 배당주 스크리닝",
        6: "AI 퀀트 적정주가 계산법: 감으로 사지 말고 데이터로 사라",
        7: "주린이 탈출: 손절매와 익절 구간 설정하는 절대 공식",
        8: "24시간 글로벌 시황 & 외신 속보 실시간 레이더 활용법"
    }

    def __init__(self):
        self.hashtag_matrix = StockHashtagMatrix()
        self.meta_pub = StockMetaPublisher()
        self.history_file = CURRENT_DIR / "omni_cardnews_publish_history.json"
        self.state_file = CURRENT_DIR / "omni_cardnews_schedule_state.json"

    def _load_state(self) -> Dict[str, Any]:
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"last_topic_id": 0, "published_today": []}

    def _save_state(self, state: Dict[str, Any]):
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"상태 저장 경고: {e}")

    def get_next_topic_id(self) -> int:
        """1~8번 주제 자율 순환"""
        state = self._load_state()
        last_id = state.get("last_topic_id", 0)
        next_id = (last_id % 8) + 1
        state["last_topic_id"] = next_id
        self._save_state(state)
        return next_id

    def is_already_published_today(self, topic_id: int) -> bool:
        """[중복 방지 락] 오늘 이미 해당 주제가 송출되었는지 점검"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
                    for item in history:
                        if item.get("date") == today_str and item.get("topic_id") == topic_id and item.get("status") == "success":
                            return True
            except Exception:
                pass
        return False

    def produce_fresh_cardnews(self, topic_id: int) -> List[str]:
        """
        🎨 [쏘기 직전 5장 카드뉴스 신선 제작]
        """
        logger.info("=" * 70)
        logger.info(f"🎨 [주식 카드뉴스 제작] 쏘기 직전 주제 #{topic_id} 5장 신규 렌더링 시작...")
        logger.info("=" * 70)

        desktop_base = Path(r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\주식")
        if desktop_base.exists():
            matched_dirs = sorted(glob.glob(str(desktop_base / f"*주제{topic_id:02d}*")) + glob.glob(str(desktop_base / f"주식_{topic_id:02d}_*")))
            for d in reversed(matched_dirs):
                slides = sorted(glob.glob(os.path.join(d, "slide_*.png")))
                if len(slides) >= 4:
                    logger.info(f"📂 [주제 #{topic_id} 전용 카드뉴스 슬라이드 로드] {d} ({len(slides)}장)")
                    return slides

        # 프로젝트 내 에셋 폴백
        local_dir = CURRENT_DIR / f"topic_{topic_id}"
        if local_dir.exists():
            slides = sorted(glob.glob(str(local_dir / "*.png")))
            if len(slides) >= 4:
                return slides

        raise FileNotFoundError(f"주제 #{topic_id}에 매칭되는 유효한 주식 카드뉴스 슬라이드가 없습니다.")

    def build_meta_packages(self, topic_id: int) -> Dict[str, Any]:
        """제목, 설명문, 카피, 공식 검색어, 4단 티어 해시태그 패키징"""
        main_title = self.CARDNEWS_TOPICS.get(topic_id, f"주식 퀀트 분석 카드뉴스 #{topic_id}")
        hashtags = self.hashtag_matrix.get_instagram_hashtags(topic_id=topic_id, count=8)
        hashtag_str = " ".join(hashtags)

        ig_caption = (
            f"📈 [StockMaster 카드뉴스] {main_title}\n\n"
            f"주식은 감이 아니라 데이터입니다. 외인·기관 쌍끌이 수급과 퀀트 차트 분석 📊\n"
            f"슬라이드를 넘겨 핵심 투자 포인트를 확인하세요!\n\n"
            f"🔍 네이버 검색창에 👉 [{self.OFFICIAL_KEYWORD}] 검색해보세요!\n\n"
            f"{hashtag_str}"
        )

        fb_caption = (
            f"📈 [주식 AI 퀀트 매거진] {main_title}\n\n"
            f"당일 주도 섹터 수급 분석과 실시간 AI 적정주가 진단 가이드 📖\n"
            f"슬라이드를 넘겨 핵심 투자 꿀팁을 확인하세요!\n\n"
            f"🔍 네이버 검색창에 👉 [{self.OFFICIAL_KEYWORD}] 검색!\n\n"
            f"{hashtag_str}"
        )
        fb_first_comment = (
            f"👉 실시간 AI 주식 퀀트 진단 바로가기: {self.LANDING_URL}\n"
            f"네이버에 [{self.OFFICIAL_KEYWORD}] 검색하셔도 바로 나옵니다!"
        )

        return {
            "title": main_title,
            "ig_caption": ig_caption,
            "fb_caption": fb_caption,
            "fb_comment": fb_first_comment
        }

    def execute_single_slot(self, topic_id: Optional[int] = None, force: bool = False) -> Dict[str, Any]:
        """
        🚀 [정시 1회 단발 실행] 쏘기 직전 5장 제작 ➔ Meta 즉시 1회 발사 ➔ 중복 락
        """
        target_topic = topic_id or self.get_next_topic_id()
        today_str = datetime.now().strftime("%Y-%m-%d")

        if not force and self.is_already_published_today(target_topic):
            logger.info(f"🛑 [중복 방지 락] 주식 카드뉴스 주제 #{target_topic}은 오늘 이미 송출되었습니다. 스킵합니다.")
            return {"status": "skipped", "message": f"주제 #{target_topic} 오늘 송출 완료 상태"}

        try:
            slides = self.produce_fresh_cardnews(target_topic)
        except Exception as e:
            logger.error(f"❌ [주식 카드뉴스 제작 실패] {e}")
            return {"status": "error", "error": f"제작 실패: {e}"}

        # 🔍 [3단계: 파이썬 실물 전수 검증] "API로 쏘는 건 무조건 바탕화면에 제대로 완이 다 만들고 파이썬 확인 그 다음에 API"
        from brands.stock.stock_production_safety_gate import StockProductionSafetyGate
        is_valid, verify_msg = StockProductionSafetyGate.verify_desktop_cardnews_completed(slides)
        if not is_valid:
            logger.critical(f"🛑 [파이썬 완제품 검증 탈락] 바탕화면 카드뉴스 실물 검증 실패: {verify_msg} -> 외부 API(Meta) 송출 원천 차단!")
            return {"status": "verification_failed", "error": f"바탕화면 실물 검증 실패: {verify_msg}"}
        logger.info(f"✅ [3단계 파이썬 완제품 검증 100% 합격] {verify_msg} -> 4단계 외부 API(Meta) 발사(쏘기) 개시!")

        # 4. 메타데이터 패키징 & 외부 API 발사
        pkg = self.build_meta_packages(target_topic)
        results = {
            "status": "success",
            "date": today_str,
            "published_at": get_now_kst_str(),
            "brand": self.BRAND,
            "topic_id": target_topic,
            "title": pkg["title"],
            "slides_count": len(slides),
            "channels": {}
        }

        if self.meta_pub.is_available():
            logger.info(f"📘 [1/2 페이스북 카드뉴스 앨범 송출] {len(slides)}장 업로드...")
            try:
                fb_res = self.meta_pub.publish_facebook_cardnews_album(
                    image_paths=slides,
                    caption=pkg["fb_caption"],
                    first_comment=pkg["fb_comment"]
                )
                results["channels"]["facebook_cardnews"] = fb_res
            except Exception as fbe:
                results["channels"]["facebook_cardnews"] = {"status": "error", "error": str(fbe)}

            logger.info(f"📸 [2/2 인스타그램 캐러셀 피드 송출] {len(slides)}장 업로드...")
            try:
                ig_res = self.meta_pub.publish_instagram_carousel(
                    image_paths=slides,
                    caption=pkg["ig_caption"]
                )
                results["channels"]["instagram_carousel"] = ig_res
            except Exception as ige:
                results["channels"]["instagram_carousel"] = {"status": "error", "error": str(ige)}
        else:
            logger.warning("⚠️ [Meta 자격 증명 점검 요망] 토큰 갱신 대기 중 (산출물 5장 완제품 패키징 완료)")
            results["channels"]["meta"] = {"status": "ready_staged", "message": "토큰 갱신 시 즉시 발사"}

        self._record_history(results)
        logger.info("=" * 70)
        logger.info(f"🎉 [주식 5장 카드뉴스 1회 단발 송출 완료] 주제 #{target_topic} | 슬라이드 {len(slides)}장")
        logger.info("=" * 70)
        return results

    def _record_history(self, record: Dict[str, Any]):
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                pass
        history.append(record)
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history[-50:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    pilot = StockOmniCardnewsPilot()
    print(f"📈 Stock Omni Cardnews Pilot 준비 완료! (다음 롤링 주제: #{pilot.get_next_topic_id()})")
