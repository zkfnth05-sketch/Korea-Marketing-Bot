# -*- coding: utf-8 -*-
"""
InsuranceRedditScanner - 🔍 [보험 리밸런스 전용 레딧 외국인·유학생 타겟 2단계 실시간 족집게 스캐너]
=============================================================================================
• 역할:
  - 1단계: 순수 파이썬(InsuranceRedditFilter) 100% 심사 (비용 0원, 0.001초 판별)
    * 50+ 네거티브 블랙리스트(불법/도박/음란/정치/비자사기/하드웨어) 즉시 0회 탈락
    * 4대 화이트리스트(NHIS vs 실손, 비급여 병원비, ARC 가입 자격, 30개사 비교) 키워드 매칭 및 가중치 점수 산출
    * 상위 1등 알짜 질문글만 엄선하여 제미나이 1회 호출로 전달
  - 2단계: 제미나이 AI 시맨틱 심층 검증 (진성 타겟 유저인지 최종 판정)
  - SQLite DB 중복 검사 및 채널별 안전 Rate Limit 통제
"""

import os
import sys
import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from core.db_manager import DBManager
from core.reddit_browser_driver import RedditBrowserDriver
from brands.insurance.insurance_reddit_copywriter import InsuranceRedditCopywriter

logger = logging.getLogger("InsuranceRedditScanner")

# 12대 외국인·유학생·교민 타겟 핵심 서브레딧 목록
INSURANCE_TARGET_SUBREDDITS = [
    "Living_in_Korea",
    "teachinginkorea",
    "korea",
    "seoul",
    "koreatravel",
    "expats",
    "hanguk",
    "personalfinance",
    "digitalnomad",
    "FinancialPlanning"
]


class InsuranceRedditFilter:
    """
    🛡️ [1단계: 순수 파이썬 100% 고정밀 족집게 필터 — 본문(Body) 심층 정밀 분석 탑재]
    - API 비용 0원, 0.001초 만에 비관련/위험 게시글을 100% 원천 차단
    - 제목 및 본문(Body) 전수 정밀 검사 + 4대 타겟 클러스터 유연 정규식 매칭
    - 상위 1등 알짜배기 보험 질문글 엄선하여 점수(Score) 기반 선별
    """

    # 1. 50+ 네거티브 블랙리스트 패턴 (즉시 탈락)
    NEGATIVE_PATTERNS = [
        # 도박/코인/불법/마약/성인
        r"\b(crypto|bitcoin|ethereum|forex\s*trading|casino|gambling|escort|hooker|porn|nude|fake\s*id|visa\s*fraud|illegal\s*stay|overstay\s*fine|drug|weed|thc|cbd|weapon|gun)\b",
        # 극단적 정치/사회 갈등
        r"\b(election\s*fraud|president\s*yoon|political\s*party|impeachment|communist|dictator|protest\s*march)\b",
        # 하드웨어/보일러/차량 수리/이사
        r"\b(boiler\s*broken|boiler\s*error|wifi\s*router|pc\s*repair|screen\s*cracked|car\s*lease|used\s*car\s*dealer|moving\s*truck|plumbing\s*leak)\b",
        # 비관련 학업 불만/시험 불합격
        r"\b(topik\s*test\s*center|ielts\s*score|university\s*rejection|thesis\s*advisor|failed\s*exam)\b",
        # 구인/알바/채용
        r"\b(hiring|job\s*opening|salary|wage|hourly\s*rate|recruiting|looking\s*for\s*(an\s*)?applicant|employment|part-time\s*job)\b"
    ]

    # 글로벌 서브레딧 (한국 앵커 필수 검증 대상)
    GLOBAL_SUBREDDITS = {
        "personalfinance", "digitalnomad", "FinancialPlanning", "expats"
    }

    # 2. 4대 타겟 클러스터 화이트리스트 (유연 정규식 & 가중치 점수 매트릭스)
    POSITIVE_CLUSTERS = {
        "nhis_and_silbi": {
            "weight": 40.0,
            "scenario_id": 1,
            "patterns": [
                r"\b(nhis|national\s*health\s*insurance(\s*korea)?|korean\s*health\s*insurance)\b",
                r"\b(silbi|silson|supplemental\s*insurance\s*korea|4th\s*gen\s*silbi)\b",
                r"\b(health\s*coverage\s*(in\s*)?korea|medical\s*insurance\s*(in\s*)?korea|health\s*insurance\s*in\s*korea)\b",
                r"\b(insurance\s*for\s*expats\s*in\s*korea)\b"
            ]
        },
        "hospital_and_reimbursement": {
            "weight": 35.0,
            "scenario_id": 2,
            "patterns": [
                r"\b(mri\s*(cost\s*)?in\s*korea|hospital\s*bill\s*in\s*korea|clinic\s*(cost|bill)\s*in\s*korea)\b",
                r"\b(dental\s*(cost|bill|implant)\s*in\s*korea|surgery\s*cost\s*in\s*korea|korean\s*hospital\s*cost)\b",
                r"\b(medical\s*reimbursement\s*korea|claim\s*korean\s*insurance|non-covered|bi-geup-yeo)\b",
                r"\b(korean\s*medical\s*expense|korean\s*doctor\s*bill)\b"
            ]
        },
        "expat_and_arc_insurance": {
            "weight": 35.0,
            "scenario_id": 3,
            "patterns": [
                r"\b(arc\s*insurance|alien\s*registration\s*insurance|foreigner\s*(health\s*)?insurance\s*korea)\b",
                r"\b(insurance\s*for\s*(expats|foreigners|teachers|students)\s*in\s*korea)\b",
                r"\b(epik\s*insurance|hagwon\s*insurance|korean\s*international\s*student\s*insurance)\b",
                r"\b((d-2|d-4|e-2|e-7|e-9)\s*insurance|foreigner\s*qualify\s*korean\s*insurance)\b"
            ]
        },
        "comparison_and_rebalance": {
            "weight": 30.0,
            "scenario_id": 7,
            "patterns": [
                r"\b(compare\s*korean\s*insurance|korean\s*insurance\s*recommendation|cheapest\s*korean\s*insurance)\b",
                r"\b(cancel\s*korean\s*insurance|rebalance\s*korean\s*insurance|best\s*private\s*insurance\s*in\s*korea)\b",
                r"\b(insurance\s*quote\s*korea|insurance\s*broker\s*in\s*korea)\b"
            ]
        }
    }

    # 본문(Body) 심층 질문 및 진성 감정 부스터 (가산점)
    BODY_BOOSTERS = [
        r"\b(how|where|anyone\s*know|recommend|advice|suggest|tips|help|looking\s*for|curious)\b",
        r"\b(expensive|bill|cost|shocked|confused|covered|reimbursed|out\s*of\s*pocket|pay)\b"
    ]

    @classmethod
    def evaluate_post(cls, title: str, body: str = "", subreddit: str = "") -> Dict[str, Any]:
        """
        순수 파이썬 100% 심사:
        - 제목 + 본문(Body) 전수 심층 결합 분석
        - 1단계: 50+ 블랙리스트 정규식 검사 (0.001초 탈락)
        - 1.5단계: 글로벌 서브레딧 필수 K-Context 앵커 검사 (해외 보험 원천 차단)
        - 2단계: 4대 화이트리스트 유연 정규식 매칭 및 100점 만점 가중치 채점
        """
        clean_title = (title or "").strip()
        clean_body = (body or "").strip()
        combined = f"{clean_title} \n {clean_body}".lower()

        # 0. 글자수 최소 길이 체크
        if len(clean_title) < 5:
            return {"passed": False, "score": 0.0, "reason": "제목 너무 짧음", "cluster": None, "matched_keywords": []}

        # [1단계: 블랙리스트 즉시 탈락]
        for pattern in cls.NEGATIVE_PATTERNS:
            match = re.search(pattern, combined, re.IGNORECASE)
            if match:
                return {
                    "passed": False,
                    "score": 0.0,
                    "reason": f"블랙리스트 차단: {match.group(0)}",
                    "cluster": None,
                    "matched_keywords": []
                }

        # [1.5단계: 글로벌 서브레딧 한국 앵커 필수 검증]
        sub_lower = (subreddit or "").lower()
        if any(sub_lower == g.lower() for g in cls.GLOBAL_SUBREDDITS):
            k_anchor_pattern = r"\b(korea|korean|seoul|nhis|silbi|silson|arc|alien\s*registration|외국인등록증|epik|hagwon|d-2|d-4|e-2|e-7)\b"
            if not re.search(k_anchor_pattern, combined, re.IGNORECASE):
                return {
                    "passed": False,
                    "score": 0.0,
                    "reason": f"글로벌 서브레딧(r/{subreddit}) 내 한국 의료/보험 앵커 부재",
                    "cluster": None,
                    "matched_keywords": []
                }

        # [2단계: 4대 화이트리스트 유연 매칭 및 가중치 채점]
        total_score = 0.0
        best_cluster = None
        best_scenario_id = 1
        highest_cluster_score = 0.0
        matched_all_keywords = []

        for cluster_name, cluster_info in cls.POSITIVE_CLUSTERS.items():
            c_weight = cluster_info["weight"]
            c_patterns = cluster_info["patterns"]
            c_scenario_id = cluster_info["scenario_id"]
            
            cluster_matches = []
            for pat in c_patterns:
                match = re.search(pat, combined, re.IGNORECASE)
                if match:
                    cluster_matches.append(match.group(0))

            if cluster_matches:
                matched_all_keywords.extend(cluster_matches)
                c_score = c_weight + (len(cluster_matches) * 5.0)
                if c_score > highest_cluster_score:
                    highest_cluster_score = c_score
                    best_cluster = cluster_name
                    best_scenario_id = c_scenario_id
                total_score += c_score

        if not best_cluster:
            return {
                "passed": False,
                "score": 0.0,
                "reason": "보험 관련 핵심 키워드 0건",
                "cluster": None,
                "matched_keywords": []
            }

        # [3단계: 본문(Body) 심층 질문 및 진성 감정 가산점]
        if len(clean_body) > 30:
            total_score += 5.0

        for b_pat in cls.BODY_BOOSTERS:
            if re.search(b_pat, combined, re.IGNORECASE):
                total_score += 4.0

        if "?" in clean_title or "?" in clean_body:
            total_score += 5.0

        final_score = min(round(total_score, 1), 100.0)
        passed = final_score >= 35.0

        return {
            "passed": passed,
            "score": final_score,
            "cluster": best_cluster,
            "scenario_id": best_scenario_id,
            "matched_keywords": list(set(matched_all_keywords)),
            "reason": f"적합 통과 ({final_score:.1f}점) - 클러스터: {best_cluster}" if passed else f"점수 미달 ({final_score:.1f}점 < 35점)"
        }


class InsuranceRedditScanner:
    """
    보험 리밸런스 전용 레딧 2단계 실시간 족집게 스캐너
    - 1단계: 순수 파이썬 100% 필터(InsuranceRedditFilter)로 1위 후보 선별 (API 0회)
    - 2단계: 최상위 1등 글만 제미나이 1회 시맨틱 검증 수행 (API 1회)
    """

    def __init__(self, db_mgr: Optional[DBManager] = None, driver: Optional[RedditBrowserDriver] = None):
        self.db_mgr = db_mgr or DBManager()
        self.driver = driver or RedditBrowserDriver(service_id="insurance")
        self.copywriter = InsuranceRedditCopywriter()

    def scan_target_subreddits(
        self,
        subreddits: Optional[List[str]] = None,
        limit_per_sub: int = 15,
        max_final_leads: int = 3
    ) -> List[Dict[str, Any]]:
        """
        12대 서브레딧을 스캔하여 1단계 파이썬 필터를 통과하고
        2단계 제미나이/파이썬 인텐트 검증까지 완료한 최상위 진성 리드 반환
        """
        targets = subreddits or INSURANCE_TARGET_SUBREDDITS
        all_candidates = []

        logger.info(f"🔍 [Insurance Reddit] {len(targets)}개 타겟 서브레딧 실시간 스캔 시작 (채널당 {limit_per_sub}건)...")

        live_posts = self.driver.fetch_live_posts(targets, limit_per_sub=limit_per_sub)
        if not live_posts:
            logger.info("실시간 스캔된 글이 없어 대기합니다.")
            return []

        for post in live_posts:
            post_id = post.get("id") or post.get("submission_id", "")
            title = post.get("title", "")
            body = post.get("body", "")
            sub = post.get("subreddit", "")
            post_url = post.get("url", f"https://www.reddit.com{post.get('permalink', '')}")

            # 1. DB 중복 검사 (이미 댓글을 작성한 글은 스킵)
            if self.db_mgr.is_already_processed(post_id):
                continue

            # 2. [1단계: 순수 파이썬 100% 고정밀 심사 — 본문 심층 전수 검사] (비용 0원)
            eval_res = InsuranceRedditFilter.evaluate_post(title=title, body=body, subreddit=sub)
            if not eval_res["passed"]:
                continue

            logger.info(f"✅ [보험 파이썬 1차 합격] (점수: {eval_res['score']:.1f}점) r/{sub}: '{title[:35]}' (본문길이: {len(body)}자)")
            all_candidates.append({
                "post_id": post_id,
                "title": title,
                "body": body,
                "subreddit": sub,
                "post_url": post_url,
                "score": eval_res["score"],
                "cluster": eval_res["cluster"],
                "scenario_id": eval_res["scenario_id"],
                "matched_keywords": eval_res["matched_keywords"]
            })

        if not all_candidates:
            logger.info("ℹ️ [Insurance Reddit] 1단계 필터를 통과한 신규 질문글이 없습니다.")
            return []

        # 점수 기준 내림차순 정렬 -> 상위 후보 선별
        all_candidates.sort(key=lambda x: x["score"], reverse=True)
        top_candidates = all_candidates[:max_final_leads]
        logger.info(f"🏆 [1단계 파이썬 심사] 총 {len(all_candidates)}개 합격 글 중 상위 {len(top_candidates)}개 선별")

        # 3. [2단계: 파이썬 인텐트 심층 정밀 검증 (제미나이 0회 호출)]
        qualified_leads = []
        for cand in top_candidates:
            intent = self.copywriter.verify_lead_intent(
                post_title=cand["title"],
                post_body=cand["body"],
                subreddit=cand["subreddit"]
            )
            if not intent.get("is_relevant", False):
                logger.info(f"🛡️ [파이썬 인텐트 심사 탈락] '{cand['title'][:30]}' 사유: {intent.get('reason')}")
                continue

            cand["intent"] = intent
            logger.info(f"✨ [파이썬 최종 승인 리드] r/{cand['subreddit']}: '{cand['title'][:35]}' ({intent.get('reason')})")
            qualified_leads.append(cand)

        return qualified_leads
