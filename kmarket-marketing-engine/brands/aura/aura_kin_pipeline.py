# -*- coding: utf-8 -*-
"""
Aura Kin Pipeline (🚀 Aura 전용 네이버 지식iN 실시간 낚아채기 원스톱 오케스트레이터)
========================================================================================
- 브랜드: Aura (2030 AI 데이팅 & 서울 핫플 매칭)
- 역할:
  1. 🔍 100대 키워드 기반 실시간 질문 스캔 (AuraKinScanner)
  2. 🧠 AI 적합도 85점 심사 및 3박자 킬러 답변 생성 (AuraKinGeminiSolver)
  3. 🤖 네이버 지식iN 자동 답변 등록 (AuraKinPublisher)
  4. 📁 히스토리 DB (data/aura_kin_history.json) 저장 및 대시보드 연동
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
logger = logging.getLogger("AuraKinPipeline")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_FILE = DATA_DIR / "aura_kin_history.json"

from brands.aura.aura_kin_scanner import AuraKinScanner
from brands.aura.aura_kin_gemini_solver import AuraKinGeminiSolver
from brands.aura.aura_kin_publisher import AuraKinPublisher


class AuraKinPipeline:
    """💖 Aura 전용 네이버 지식iN 실시간 낚아채기 파이프라인"""

    BRAND = "aura"
    NAME = "Aura (AI 데이팅)"

    def __init__(self):
        self.scanner = AuraKinScanner()
        self.solver = AuraKinGeminiSolver()
        self.publisher = AuraKinPublisher()

    def run_catch_cycle(self, max_catch: int = 1) -> Dict[str, Any]:
        """
        1회 낚아채기 사이클 실행:
        1. 질문 스캔 (샘플 3개 키워드, 최대 5개 질문)
        2. 적합도 심사 (85점 이상 선별)
        3. 합격한 질문 중 최상위 1개에 대해 3박자 답변 생성 및 등록
        """
        logger.info("🚀 [Aura 지식iN 파이프라인] 실시간 낚아채기 사이클 가동 시작...")

        # 1. 질문 스캔
        scanned_questions = self.scanner.scan_recent_questions(sample_keywords_count=3, max_questions=6)
        if not scanned_questions:
            logger.info("ℹ️ 현재 실시간 스캔된 신규 질문이 없습니다.")
            return {"success": False, "status": "no_questions", "message": "새 질문 대기 중"}

        # 히스토리 로드 (기존 답변 완료된 doc_id 확인)
        history = self._load_history()
        done_ids = {h.get("doc_id") for h in history}

        passed_candidates = []

        # 2. 적합도 85점 심사
        for q in scanned_questions:
            doc_id = q.get("doc_id", "")
            if doc_id in done_ids:
                continue

            score, reason, is_passed = self.solver.evaluate_relevance(
                title=q["title"],
                content=q.get("content", ""),
                keyword=q.get("keyword", "")
            )
            logger.info(f"📊 [심사 결과] {score}점 (합격: {is_passed}) | 제목: {q['title'][:30]}... ({reason})")

            if is_passed:
                passed_candidates.append({
                    "question": q,
                    "score": score,
                    "reason": reason
                })

        if not passed_candidates:
            logger.info("ℹ️ 85점 이상 적합 질문이 없어 다음 주기로 대기합니다.")
            return {"success": False, "status": "no_passed_questions", "message": "적합도 85점 이상 질문 대기 중"}

        # 최고 점수 순 정렬
        passed_candidates.sort(key=lambda x: x["score"], reverse=True)
        target = passed_candidates[0]
        t_question = target["question"]

        logger.info(f"🎯 [최고점 질문 선발] {target['score']}점 | {t_question['title']}")

        # 3. 3박자 킬러 답변 생성
        ans_data = self.solver.generate_killer_answer(
            title=t_question["title"],
            content=t_question.get("content", ""),
            keyword=t_question.get("keyword", "")
        )

        # 4. 네이버 지식iN 자동 등록
        pub_res = self.publisher.publish_answer(
            question_url=t_question["url"],
            answer_text=ans_data["answer"],
            source_url=ans_data.get("landing_url", "https://aura-ai-dating.vercel.app")
        )

        # 5. 히스토리 기록 저장
        record = {
            "brand": "aura",
            "doc_id": t_question["doc_id"],
            "keyword": t_question["keyword"],
            "title": t_question["title"],
            "url": t_question["url"],
            "score": target["score"],
            "reason": target["reason"],
            "answer": ans_data["answer"],
            "status": pub_res.get("status", "completed"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self._save_history_record(record)

        logger.info(f"✅ [Aura 지식iN 낚아채기 완료] {t_question['title']} ➔ 대시보드 기록 완료!")
        return {
            "success": True,
            "status": "completed",
            "record": record
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
        history.insert(0, record) # 최신순 앞에 추가
        # 최대 100개 유지
        history = history[:100]
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    pipeline = AuraKinPipeline()
    res = pipeline.run_catch_cycle()
    print("Pipeline Result:", json.dumps(res, ensure_ascii=False, indent=2))
