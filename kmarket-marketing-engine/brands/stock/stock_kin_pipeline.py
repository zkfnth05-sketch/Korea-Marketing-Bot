# -*- coding: utf-8 -*-
"""
Stock Kin Pipeline (🚀 Stock Master 전용 네이버 지식iN 실시간 낚아채기 원스톱 오케스트레이터)
========================================================================================
- 브랜드: Stock Master (2030 AI 주식 퀀트 & 종목 진단)
- 역할:
  1. 🔍 100대 황금 키워드 기반 실시간 주식 질문 스캔 (StockKinScanner)
  2. 🧠 AI 적합도 85점 심사 및 1,500자~4,000자 초고밀도 3박자 킬러 답변 생성 (StockKinGeminiSolver)
  3. 🤖 네이버 지식iN 자동 답변 등록 (StockKinPublisher)
  4. 📁 히스토리 DB (data/stock_kin_history.json) 저장 및 대시보드 연동
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# UTF-8 콘솔 지원
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("StockKinPipeline")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_FILE = DATA_DIR / "stock_kin_history.json"

from brands.stock.stock_kin_scanner import StockKinScanner
from brands.stock.stock_kin_gemini_solver import StockKinGeminiSolver
from brands.stock.stock_kin_publisher import StockKinPublisher
from brands.stock.stock_kin_python_filter import StockPythonFilter


class StockKinPipeline:
    """📈 Stock Master 전용 네이버 지식iN 실시간 낚아채기 파이프라인"""

    BRAND = "stock"
    NAME = "Stock Master (주식 AI)"

    def __init__(self):
        self.scanner = StockKinScanner()
        self.solver = StockKinGeminiSolver()
        self.publisher = StockKinPublisher()
        self.filter = StockPythonFilter()

    DAILY_QUOTA = 10  # 하루 상한 등록 목표

    def run_catch_cycle(self, max_catch: int = 10, dry_run: bool = False) -> Dict[str, Any]:
        """
        낙아채기 사이클 실행:
        1. 질문 스캔 (샘플 6개 키워드, 최대 8개 질문)
        2. 적합도 심사 (85점 이상 선별)
        3. 합격한 질문 중 성공 등록될 때까지 순차 시도 (하루 {DAILY_QUOTA}개 할당량 도달 시 중단)
        """
        logger.info(f"🚀 [Stock 지식iN 파이프라인] 실시간 낚아채기 사이클 가동 시작... (mode={'DRY-RUN' if dry_run else 'LIVE'})")

        # 1. 질문 스캔 — 전체 100개 키워드 전수 탐색, 48시간 이내 최신 질문만 수집
        scanned_questions = self.scanner.scan_recent_questions(sample_keywords_count=100, max_questions=100)
        if not scanned_questions:
            logger.info("ℹ️ 현재 실시간 스캔된 신규 주식 질문이 없습니다.")
            return {"success": False, "status": "no_questions", "message": "새 질문 대기 중"}

        # 히스토리 로드
        history = self._load_history()
        # ✅ done_ids: 실제로 "published" 성공한 doc_id만 중복 방어 (실패·미확인은 재시도 허용)
        done_ids = {h.get("doc_id") for h in history if h.get("status") == "published" and "answerNo=" in h.get("published_url", "")}
        # 오늘 이미 실제 성공 등록된 수 계산 (answerNo= 포함된 진짜 URL만 카운트)
        today_str = datetime.now().strftime("%Y-%m-%d")
        today_published = sum(
            1 for h in history
            if h.get("status") == "published"
            and "answerNo=" in h.get("published_url", "")
            and h.get("created_at", "").startswith(today_str)
        )
        if today_published >= self.DAILY_QUOTA:
            logger.info(f"✅ [Stock 지식iN] 오늘 이미 {today_published}개 성공 등록 완료 — 일일 할당량({self.DAILY_QUOTA}개) 달성!")
            return {"success": True, "status": "quota_reached", "today_count": today_published}

        passed_candidates = []

        # 2. 적합도 50점 이상 파이썬 고도화 심사 (0ms 즉각 판정 & API 비용 0원)
        for q in scanned_questions:
            doc_id = q.get("doc_id", "")
            if doc_id in done_ids:
                continue

            score, is_passed, reason = self.filter.score_question(
                title=q["title"],
                content=q.get("content", "")
            )
            logger.info(f"📊 [Stock 필터 심사] {score}점 (합격: {is_passed}) | 제목: {q['title'][:30]}... ({reason})")

            if is_passed:
                passed_candidates.append({
                    "question": q,
                    "score": score,
                    "reason": reason
                })

        if not passed_candidates:
            logger.info("ℹ️ 50점 이상 적합 질문이 없어 다음 주기로 대기합니다.")
            return {"success": False, "status": "no_passed_questions", "message": "적합도 50점 이상 주식 질문 대기 중"}

        # 최고 점수 순 정렬
        passed_candidates.sort(key=lambda x: x["score"], reverse=True)

        published_count = 0
        last_record = None

        # ✅ 합격 후보를 순차적으로 처리 — 성공할 때마다 카운트, 목표 달성 시 중단
        for candidate in passed_candidates:
            remaining_quota = self.DAILY_QUOTA - today_published - published_count
            if remaining_quota <= 0:
                logger.info(f"🎯 [Stock 지식iN] 오늘 목표 {self.DAILY_QUOTA}개 달성! 사이클 종료")
                break
            if published_count >= max_catch:
                break

            t_question = candidate["question"]
            logger.info(f"🎯 [질문 선발] {candidate['score']}점 | {t_question['title']}")

            # ✅ 선발된 질문의 실제 본문(.questionDetail)을 상세 페이지에서 100% 정밀 크롤링 보강
            real_content = self.scanner.fetch_question_detail_content(t_question.get("url", ""))
            if real_content:
                t_question["content"] = real_content
                logger.info(f"📄 [질문 실제 본문 100% 확보 ({len(real_content)}자)]: {real_content[:60]}...")

                # 🔍 [핵심 2차 필터 심사]: 실제 수집된 본문 기준으로 주식 질문 적합도 및 앵커 재검증
                re_score, re_passed, re_reason = self.filter.score_question(
                    title=t_question["title"],
                    content=real_content
                )
                if not re_passed:
                    logger.warning(f"⚠️ [Stock 실제 본문 2차 심사 탈락] {re_score}점 (사유: {re_reason}) | 제목: {t_question['title']} ➔ 다음 후보 탐색")
                    continue
                logger.info(f"✅ [Stock 실제 본문 2차 심사 통과] {re_score}점 ({re_reason})")
            else:
                logger.info(f"ℹ️ [질문 본문 기본 요약본 유지 ({len(t_question.get('content', ''))}자)]")

            # 3. 1,500자~4,000자 킬러 답변 생성
            ans_data = self.solver.generate_killer_answer(
                title=t_question["title"],
                content=t_question.get("content", ""),
                keyword=t_question.get("keyword", "")
            )

            # 4. 네이버 지식iN 자동 등록 (출처란 공란 처리로 링크 제재 원천 차단)
            if dry_run:
                pub_res = {
                    "success": True,
                    "status": "dry_run_success",
                    "mode": "dry_run",
                    "published_url": f"https://kin.naver.com/qna/detail.naver?d1id=4&dirId=40102&docId={t_question['doc_id']}&dry_run=true",
                    "message": "[DRY-RUN] 모의 답변 생성 완료 (실제 게시 생략)"
                }
            else:
                pub_res = self.publisher.publish_answer(
                    question_url=t_question["url"],
                    answer_text=ans_data["answer"],
                    source_url=""
                )

            # 5. 히스토리 기록 저장 (성공·실패 모두 기록하되 status로 구분)
            record = {
                "brand": "stock",
                "doc_id": t_question["doc_id"],
                "keyword": t_question["keyword"],
                "title": t_question["title"],
                "content": t_question.get("content", ""),
                "url": t_question["url"],
                "score": candidate["score"],
                "reason": candidate["reason"],
                "answer": ans_data["answer"],
                "status": pub_res.get("status", "error"),
                "published_url": pub_res.get("published_url", ""),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self._save_history_record(record)
            last_record = record

            if pub_res.get("success"):
                published_count += 1
                done_ids.add(t_question["doc_id"])  # 이 사이클 내 중복 방어
                logger.info(f"✅ [{published_count}번째 성공] {t_question['title']} ➔ {pub_res.get('published_url', '')}")
            else:
                logger.warning(f"⚠️ [등록 실패] {t_question['title']} — {pub_res.get('status')} / {pub_res.get('message', '')}")

        total_today = today_published + published_count
        logger.info(f"🏁 [Stock 지식iN 사이클 완료] 이번 사이클 성공: {published_count}개 | 오늘 누적: {total_today}/{self.DAILY_QUOTA}개")
        return {
            "success": published_count > 0,
            "status": "completed",
            "published_count": published_count,
            "today_total": total_today,
            "record": last_record
        }

    def _load_history(self) -> List[Dict[str, Any]]:
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_history_record(self, record: Dict[str, Any]):
        history = self._load_history()
        history.insert(0, record)
        history = history[:100]
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    pipeline = StockKinPipeline()
    res = pipeline.run_catch_cycle()
    print("Stock Pipeline Result:", json.dumps(res, ensure_ascii=False, indent=2))
