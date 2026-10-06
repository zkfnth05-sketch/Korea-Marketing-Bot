# -*- coding: utf-8 -*-
"""
StockRedditScanner - 🔍 [StockMaster AI 전용 레딧 2단계 실시간 족집게 스캐너]
=============================================================================
• 역할:
  - 1단계: 순수 파이썬(StockRedditFilter) 100% 심사 (비용 0원, 0.001초 판별)
    * 50+ 네거티브 블랙리스트(스팸 리딩방/밈코인 펌핑/도박/비자/정치/의료) 즉시 0회 탈락
    * 5대 화이트리스트(외인기관 수급, AI 퀀트, HBM 반도체, 리스크 관리, 코스피 투자) 키워드 매칭 및 가중치 채점
    * 상위 1등 알짜 질문글만 엄선하여 제미나이 1회 호출로 전달
  - 2단계: 파이썬 시맨틱 인텐트 심층 검증 (진성 타겟 투자자인지 최종 확정)
  - SQLite DB 중복 검사 및 채널별 안전 Rate Limit 통제
"""

import os
import sys
import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# UTF-8 Encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from core.db_manager import DBManager
from core.reddit_browser_driver import RedditBrowserDriver
from brands.stock.stock_reddit_copywriter import StockRedditCopywriter

logger = logging.getLogger("StockRedditScanner")

# 주식/퀀트 타겟 핵심 초활성 서브레딧 목록 (비활성/유령 커뮤니티 제외)
STOCK_TARGET_SUBREDDITS = [
    "stocks",
    "investing",
    "StockMarket",
    "wallstreetbets",
    "algotrading",
    "Daytrading",
    "dividends",
    "options",
    "Korea"
]


class StockRedditFilter:
    """
    🛡️ [1단계: 순수 파이썬 100% 고정밀 족집게 필터 — 본문(Body) 심층 정밀 분석]
    - API 비용 0원, 0.001초 만에 비관련/위험 게시글을 100% 원천 차단
    - 제목 및 본문(Body) 전수 정밀 검사 + 5대 타겟 클러스터 유연 정규식 매칭
    - 상위 1등 알짜배기 질문글 엄선하여 점수(Score) 기반 선별
    """

    # 1. 50+ 네거티브 블랙리스트 패턴 (즉시 탈락)
    NEGATIVE_PATTERNS = [
        # 불법 리딩방/텔레그램 신호/스팸 펌프
        r"\b(whatsapp\s*group|telegram\s*signal|vip\s*pump|guaranteed\s*returns|free\s*signals|pump\s*and\s*dump|airdrop\s*claim|wallet\s*drainer)\b",
        # 밈코인/크립토/도박/카지노
        r"\b(shiba|dogecoin|pepe\s*coin|floki|meme\s*coin|casino|baccarat|blackjack|sports\s*betting|slot\s*machine|gambling\s*addiction)\b",
        # 비자/출입국/체류/추방
        r"\b(visa\s*extension|e-7|e-9|f-2-7|f-4|d-10|immigration\s*office|alien\s*registration|overstay|deportation|visa\s*sponsor)\b",
        # 데이팅/연애/뷰티
        r"\b(tinder|bumble|boyfriend|girlfriend|dating\s*app|korean\s*makeup|skincare\s*routine|k-pop\s*idol|k-drama\s*ost)\b",
        # 정치/사회 갈등/법률 소송/부동산 사기
        r"\b(election|president\s*yoon|political\s*party|court\s*case|lawyer|landlord\s*dispute|jeonse\s*fraud|scam\s*call|voice\s*phishing)\b",
        # 질병/응급/약물/의료
        r"\b(hospital\s*emergency|surgery|prescription|psychiatrist|therapy|depression\s*medication|pharmacy)\b",
        # 하드웨어/보일러/차량 수리
        r"\b(boiler\s*broken|wifi\s*router|pc\s*repair|screen\s*cracked|car\s*lease|used\s*car\s*dealer|moving\s*truck|plumbing)\b",
        # 구인/알바/채용/과외
        r"\b(hiring|job\s*opening|salary|wage|hourly\s*rate|recruiting|looking\s*for\s*(an\s*)?applicant|interpreter\s*needed|tutor\s*needed|paid\s*gig)\b"
    ]

    # 글로벌 일반 서브레딧 (주식/투자 앵커 필수 검증 대상)
    GENERAL_SUBREDDITS = {
        "Korea", "Living_in_Korea", "seoul"
    }

    # 2. 5대 타겟 클러스터 화이트리스트 (유연 정규식 & 가중치 점수 매트릭스)
    POSITIVE_CLUSTERS = {
        "institutional_flow": {
            "weight": 40.0,
            "patterns": [
                r"\b(institutional\s*(inflows?|buying|investors?|money|volume)|foreign\s*(investors?|buying|capital|inflows?))\b",
                r"\b(net\s*buying|order\s*flow|dark\s*pool|smart\s*money|whale\s*accumulation|foreigner\s*holding)\b",
                r"(foreign|institutional)\s*(accumulation|accumulation\s*pattern|buying\s*pressure)",
                r"(who\s*is\s*buying|track\s*institutional\s*money|whale\s*tracker)"
            ]
        },
        "ai_quant_scoring": {
            "weight": 35.0,
            "patterns": [
                r"\b(quant\s*(trading|model|strategy|score|analysis)|algorithmic\s*trading)\b",
                r"\b(fair\s*value|target\s*price|undervalued|overvalued|dcf\s*model)\b",
                r"\b(fundamental\s*analysis|technical\s*analysis|stock\s*screener|valuation\s*model)\b",
                r"(how\s*to\s*value|price\s*target\s*model|quant\s*screener)"
            ]
        },
        "risk_management": {
            "weight": 35.0,
            "patterns": [
                r"\b(risk\s*management|position\s*sizing|stop\s*loss|take\s*profit|drawdown|fomo)\b",
                r"\b(bag\s*holding|loss\s*mitigation|portfolio\s*allocation|hedging|cut\s*losses)\b",
                r"(how\s*to\s*manage\s*risk|avoid\s*fomo|position\s*calculator)"
            ]
        },
        "semiconductor_hbm": {
            "weight": 40.0,
            "patterns": [
                r"\b(samsung|hynix|sk\s*hynix|hbm|hbm3e|hbm4|semiconductor|memory\s*chips?|wafer|foundry)\b",
                r"\b(tsmc|nvidia\s*supplier|packaging\s*tech|ai\s*chips?|hanmi\s*semiconductor)\b",
                r"(memory\s*cycle|semiconductor\s*supply\s*chain|hbm\s*demand)"
            ]
        },
        "korean_market": {
            "weight": 35.0,
            "patterns": [
                r"\b(kospi|kosdaq|korean\s*(stocks?|market|equities|economy))\b",
                r"\b(chaebol|corporate\s*value-up|korea\s*discount|investing\s*in\s*korea|korean\s*etfs?)\b",
                r"(korea\s*stock\s*market|invest\s*in\s*korea|korean\s*semiconductor\s*stocks?)"
            ]
        },
        "dividend_value": {
            "weight": 30.0,
            "patterns": [
                r"\b(dividend\s*(yield|growth|aristocrats?|cut|trap)|high\s*dividend)\b",
                r"\b(free\s*cash\s*flow|payout\s*ratio|value\s*investing|safe\s*dividends?)\b"
            ]
        }
    }

    # 본문(Body) 질문 및 진성 고민 가산점 패턴
    BODY_BOOSTERS = [
        r"\b(how|where|anyone\s*know|recommend|advice|suggest|tips|looking\s*for|curious|analysis)\b",
        r"\b(undervalued|entry\s*point|breakout|support|resistance|volume|strategy|portfolio)\b"
    ]

    @classmethod
    def evaluate_post(cls, title: str, body: str = "", subreddit: str = "") -> Dict[str, Any]:
        """
        순수 파이썬 100% 심사:
        - 제목 + 본문(Body) 전수 심층 결합 분석
        - 1단계: 50+ 블랙리스트 정규식 검사 (0.001초 탈락)
        - 1.5단계: 일반 서브레딧인 경우 주식/투자 앵커 필수 검증
        - 2단계: 5대 화이트리스트 유연 정규식 매칭 및 100점 만점 가중치 채점
        """
        clean_title = (title or "").strip()
        clean_body = (body or "").strip()
        combined = f"{clean_title} \n {clean_body}".lower()

        # 0. 글자수 최소 길이 체크
        if len(clean_title) < 5:
            return {"is_passed": False, "score": 0.0, "reason": "제목이 너무 짧음"}

        # 1. 네거티브 블랙리스트 검사 (스팸/코인/도박/비자 즉각 탈락)
        for pattern in cls.NEGATIVE_PATTERNS:
            match = re.search(pattern, combined, re.IGNORECASE)
            if match:
                return {
                    "is_passed": False,
                    "score": 0.0,
                    "reason": f"블랙리스트 키워드 포착: '{match.group(0)}'"
                }

        # 1.5. 일반 서브레딧(r/Korea 등)인 경우, 주식/투자 앵커 필수 검증
        sub_lower = (subreddit or "").lower()
        if any(sub_lower == g.lower() for g in cls.GENERAL_SUBREDDITS):
            invest_anchor_pattern = r"\b(stock|stocks|invest|investing|kospi|kosdaq|samsung|hynix|equities|etf|trading|market|shares)\b"
            if not re.search(invest_anchor_pattern, combined, re.IGNORECASE):
                return {
                    "is_passed": False,
                    "score": 0.0,
                    "reason": f"일반 서브레딧(r/{subreddit}) 내 주식/투자 앵커 부재"
                }

        # 2. 화이트리스트 유연 매칭 및 채점
        total_score = 0.0
        matched_clusters = []
        matched_keywords = []

        for cluster_name, cluster_data in cls.POSITIVE_CLUSTERS.items():
            cluster_matches = []
            for pat in cluster_data["patterns"]:
                match = re.search(pat, combined, re.IGNORECASE)
                if match:
                    cluster_matches.append(match.group(0))

            if cluster_matches:
                matched_clusters.append(cluster_name)
                matched_keywords.extend(cluster_matches)
                # 클러스터 기본 가중치 + 매칭된 패턴 개수당 5점 가산
                total_score += cluster_data["weight"] + (len(cluster_matches) * 5.0)

        # 타겟 키워드가 1개도 없으면 탈락
        if not matched_keywords:
            return {
                "is_passed": False,
                "score": 0.0,
                "reason": "타겟 화이트리스트 키워드 0개 매칭"
            }

        # 3. 본문(Body) 심층 질문 및 진성 분석 가산점 (최대 20점)
        if len(clean_body) > 30:
            total_score += 5.0

        for b_pat in cls.BODY_BOOSTERS:
            if re.search(b_pat, combined, re.IGNORECASE):
                total_score += 4.0

        if "?" in clean_title or "?" in clean_body:
            total_score += 5.0

        # 최종 판정 (40점 이상 시 합격)
        is_passed = total_score >= 40.0
        return {
            "is_passed": is_passed,
            "score": min(100.0, total_score),
            "matched_cluster": matched_clusters[0] if matched_clusters else None,
            "matched_keywords": matched_keywords,
            "reason": f"파이썬 심사 통과 (점수: {min(100.0, total_score):.1f}점, 매칭: {matched_keywords[:3]})" if is_passed else "점수 미달"
        }


class StockRedditScanner:
    """StockMaster AI 전용 레딧 실시간 2단계 족집게 스캐너"""

    def __init__(self, db_mgr: Optional[DBManager] = None, driver: Optional[RedditBrowserDriver] = None):
        self.db_mgr = db_mgr or DBManager()
        self.driver = driver or RedditBrowserDriver(service_id="stock")
        self.copywriter = StockRedditCopywriter()

    def scan_target_subreddits(
        self,
        subreddits: Optional[List[str]] = None,
        limit_per_sub: int = 15,
        max_final_leads: int = 3
    ) -> List[Dict[str, Any]]:
        """
        타겟 서브레딧 스캔 ➔ 1단계 순수 파이썬 제목+본문 심층 심사(비용 0원) ➔ 상위 1등 글 선별
        """
        target_subs = subreddits or STOCK_TARGET_SUBREDDITS
        logger.info(f"🔍 [Stock Reddit Scanner] {len(target_subs)}개 서브레딧 실시간 스캔 가동...")

        live_posts = self.driver.fetch_live_posts(target_subs, limit_per_sub=limit_per_sub)
        if not live_posts:
            logger.info("실시간 스캔된 글이 없어 대기합니다.")
            return []

        # =========================================================================
        # 1단계: 순수 파이썬 100% 족집게 심사 (제목 + 본문 심층 전수 검사)
        # =========================================================================
        python_candidates = []
        for post in live_posts:
            post_id = post.get("id")
            title = post.get("title", "")
            body = post.get("body", "")
            subreddit = post.get("subreddit", "")
            post_url = post.get("url", "")

            # DB 중복 검사
            if self.db_mgr.is_already_processed(post_id):
                continue

            # 파이썬 고정밀 제목+본문 심층 평가
            eval_res = StockRedditFilter.evaluate_post(title, body, subreddit=subreddit)
            if not eval_res["is_passed"]:
                logger.debug(f"🚫 [파이썬 1차 탈락] r/{subreddit}: '{title[:30]}' ({eval_res['reason']})")
                continue

            logger.info(f"✅ [파이썬 1차 합격] (점수: {eval_res['score']:.1f}점) r/{subreddit}: '{title[:35]}' (본문길이: {len(body)}자)")
            python_candidates.append({
                "post_id": post_id,
                "title": title,
                "body": body,
                "subreddit": subreddit,
                "post_url": post_url,
                "score": eval_res["score"],
                "eval": eval_res
            })

        if not python_candidates:
            logger.info("파이썬 1차 심사를 통과한 적합 글이 없습니다.")
            return []

        # 점수 기준 내림차순 정렬 (가장 알짜배기 글이 1등)
        python_candidates.sort(key=lambda x: x["score"], reverse=True)
        top_candidates = python_candidates[:max_final_leads]
        logger.info(f"🏆 [파이썬 심사 완료] 총 {len(python_candidates)}개 합격 글 중 1등 글 선별 (점수: {top_candidates[0]['score']:.1f}점)")

        # =========================================================================
        # 2단계: 파이썬 시맨틱 인텐트 및 클러스터 정밀 검증 (제미나이 0회 호출)
        # =========================================================================
        qualified_leads = []
        for candidate in top_candidates:
            title = candidate["title"]
            body = candidate["body"]
            subreddit = candidate["subreddit"]

            intent_res = self.copywriter.classify_stock_reddit_intent(title, body)
            if not intent_res.get("is_relevant", False):
                logger.info(f"⏭️ [파이썬 인텐트 탈락] '{title[:35]}' ({intent_res.get('reason', '')})")
                continue

            logger.info(f"🎯 [최종 합격 리드 탄생!] r/{subreddit}: '{title[:40]}' (카테고리: {intent_res.get('category')})")
            qualified_leads.append({
                "post_id": candidate["post_id"],
                "title": title,
                "body": body,
                "subreddit": subreddit,
                "post_url": candidate["post_url"],
                "score": candidate["score"],
                "intent": intent_res
            })

        return qualified_leads


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # 1. 파이썬 필터 단독 테스트
    print("\n--- [1단계 순수 파이썬 필터 검증] ---")
    test_cases = [
        ("Join our WhatsApp group for 1000% crypto airdrop signals", "Guaranteed profit telegram link", False),
        ("How do you track institutional accumulation before a semiconductor breakout?", "I want to see foreign buying volume in Samsung & SK Hynix", True),
        ("What is the best risk management rule for position sizing?", "How to avoid FOMO bag holding when volatility spikes", True),
        ("Best skincare routine in Seoul?", "Looking for Olive Young recommendations", False),
        ("How to invest in Korean stocks (KOSPI) as a US citizen?", "Corporate Value-up program and Samsung semiconductor value chain", True),
    ]
    for t, b, expected in test_cases:
        res = StockRedditFilter.evaluate_post(t, b)
        status = "PASS" if res["is_passed"] else "FAIL"
        print(f"[{status}] (Score: {res['score']}pt) '{t}' -> Expected: {expected} | Actual: {res['is_passed']}")
