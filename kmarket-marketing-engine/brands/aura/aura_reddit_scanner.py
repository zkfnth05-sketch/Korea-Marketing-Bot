# -*- coding: utf-8 -*-
"""
AuraRedditScanner - 🔍 [Aura 데이팅 전용 레딧 글로벌 여성 타겟 2단계 실시간 족집게 스캐너]
========================================================================================
• 역할:
  - 1단계: 순수 파이썬(AuraRedditFilter) 100% 심사 (비용 0원, 0.001초 판별)
    * 50+ 네거티브 블랙리스트(비자/법률/코인/정치/의료/기술) 즉시 0회 탈락
    * 4대 화이트리스트(언어교환, K-데이팅, 서울여행, 무인증 가입) 키워드 매칭 및 가중치 점수 산출
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
from brands.aura.aura_reddit_copywriter import AuraRedditCopywriter

logger = logging.getLogger("AuraRedditScanner")

# 12대 글로벌 여성 타겟 핵심 서브레딧 목록
AURA_TARGET_SUBREDDITS = [
    "Language_Exchange",
    "Korean",
    "LearnKorean",
    "koreatravel",
    "Living_in_Korea",
    "seoul",
    "kdramas",
    "kpop",
    "AsianBeauty",
    "interracialdating",
    "dating",
    "LongDistance"
]


class AuraRedditFilter:
    """
    🛡️ [1단계: 순수 파이썬 100% 고정밀 족집게 필터 — 본문(Body) 심층 정밀 분석 탑재]
    - API 비용 0원, 0.001초 만에 비관련/위험 게시글을 100% 원천 차단
    - 제목 및 본문(Body) 전수 정밀 검사 + 4대 타겟 클러스터 유연 정규식 매칭
    - 상위 1등 알짜배기 질문글 엄선하여 점수(Score) 기반 선별
    """

    # 1. 50+ 네거티브 블랙리스트 패턴 (즉시 탈락)
    NEGATIVE_PATTERNS = [
        # 비자/출입국/체류/추방
        r"\b(visa\s*extension|e-7|e-9|f-2-7|f-4|d-10|d-2\s*visa|d-4\s*visa|immigration\s*office|alien\s*registration|overstay|deportation|visa\s*sponsor|visa\s*run)\b",
        # 세무/금융/코인/외환/송금
        r"\b(tax\s*return|withholding\s*tax|crypto|bitcoin|ethereum|forex|stock\s*trading|bank\s*transfer\s*error|wire\s*transfer|tuition\s*fee|nhis\s*bill)\b",
        # 정치/사회 갈등/법률 소송/부동산 사기
        r"\b(election|president\s*yoon|political\s*party|court\s*case|lawyer|landlord\s*dispute|jeonse\s*fraud|scam\s*call|voice\s*phishing)\b",
        # 질병/응급/약물/의료
        r"\b(hospital\s*emergency|surgery|prescription|psychiatrist|therapy|depression\s*medication|std\s*test|covid\s*test|pharmacy)\b",
        # 하드웨어/보일러/차량 수리
        r"\b(boiler\s*broken|wifi\s*router|pc\s*repair|screen\s*cracked|car\s*lease|used\s*car\s*dealer|moving\s*truck|plumbing)\b",
        # 비관련 학업 불만/시험 불합격
        r"\b(topik\s*test\s*center|ielts\s*score|university\s*rejection|thesis\s*advisor|failed\s*exam)\b",
        # 구인/알바/채용/과외/통역사 모집
        r"\b(hiring|job\s*opening|salary|wage|hourly\s*rate|recruiting|looking\s*for\s*(an\s*)?applicant|interpreter\s*needed|tutor\s*needed|paid\s*gig|recruiter|work\s*remotely|employment)\b"
    ]

    # 글로벌 서브레딧 (한국 앵커 필수 검증 대상)
    GLOBAL_SUBREDDITS = {
        "interracialdating", "dating", "LongDistance", "AsianBeauty", "kdramas", "kpop", "Language_Exchange"
    }

    # 2. 4대 타겟 클러스터 화이트리스트 (유연 정규식 & 가중치 점수 매트릭스)
    POSITIVE_CLUSTERS = {
        "language_exchange": {
            "weight": 35.0,
            "patterns": [
                r"\[?seeking:?\]?\s*korean",
                r"korean\s*(native|speaker|partner|friend|buddy|exchange|practice|conversation|slang|study)",
                r"(practice|learn|study|speak|improve|conversing\s*in)\s*korean",
                r"korean\s*language\s*exchange",
                r"\b(tandem|hellotalk|hilocal)\b.*korean",
                r"(talk|chat|converse|speaking)\s*(with|to)\s*(koreans?|natives?)",
                r"conversational\s*korean"
            ]
        },
        "k_dating_culture": {
            "weight": 40.0,
            "patterns": [
                r"dating\s*(in\s*korea|in\s*seoul|korean\s*(guys?|men|women|girls?)|culture)",
                r"korean\s*(guy|guys|men|man|boyfriend|crush|date|dating|romance|blind\s*date)",
                r"\b(k-drama\s*romance|korean\s*mbti|korean\s*ideal\s*type|sogaeting|some\s*relationship)\b",
                r"dating\s*culture\s*(in\s*korea|korean)",
                r"meeting\s*(koreans?|locals)\s*in\s*(korea|seoul)",
                r"\b(tinder|bumble|hinge)\s*(in\s*korea|in\s*seoul)\b",
                r"korean\s*dating\s*apps?",
                r"date\s*(korean\s*men|korean\s*guys|in\s*seoul)"
            ]
        },
        "korea_travel": {
            "weight": 30.0,
            "patterns": [
                r"solo\s*(female|traveler|trip|woman|travel)\s*(in\s*seoul|to\s*seoul|in\s*korea|to\s*korea)",
                r"\b(hongdae|seongsu|yeonnam|gangnam|seoul|myeongdong|itaewon|busan)\s*(cafe|bars?|buddy|nightlife|friends?|hangout)\b",
                r"meet\s*(locals?|friends?)\s*in\s*(seoul|korea)",
                r"making\s*friends\s*in\s*(seoul|korea)",
                r"travel\s*buddy\s*in\s*(seoul|korea)",
                r"\b(safe\s*local\s*friends?|cafe\s*hopping\s*seoul|hang\s*out\s*in\s*seoul)\b",
                r"visiting\s*seoul\s*(next\s*week|soon|solo|as\s*a\s*woman)"
            ]
        },
        "zero_friction_app": {
            "weight": 35.0,
            "patterns": [
                r"korean\s*(social\s*app|dating\s*app|chat\s*app)",
                r"(apps?|website)\s*to\s*(practice|talk|meet|chat)\s*(with\s*koreans?)",
                r"no\s*(korean\s*number|phone\s*number|korean\s*sim|arc)",
                r"korean\s*chat\s*app\s*for\s*foreigners",
                r"app\s*without\s*(korean\s*number|korean\s*sim|arc)"
            ]
        }
    }

    # 본문(Body) 심층 질문 및 진성 감정 부스터 (가산점)
    BODY_BOOSTERS = [
        r"\b(how|where|anyone\s*know|recommend|advice|suggest|tips|looking\s*for|curious)\b",
        r"\b(shy|awkward|safe|creepy|weird\s*guys|polite|culture|honest|friend|dating)\b"
    ]

    @classmethod
    def evaluate_post(cls, title: str, body: str = "", subreddit: str = "") -> Dict[str, Any]:
        """
        순수 파이썬 100% 심사:
        - 제목 + 본문(Body) 전수 심층 결합 분석
        - 1단계: 50+ 블랙리스트 정규식 검사 (0.001초 탈락)
        - 1.5단계: 글로벌 서브레딧 필수 K-Context 앵커 검사 (한국 무관 글 원천 차단)
        - 2단계: 4대 화이트리스트 유연 정규식 매칭 및 100점 만점 가중치 채점
        """
        clean_title = (title or "").strip()
        clean_body = (body or "").strip()
        combined = f"{clean_title} \n {clean_body}".lower()

        # 0. 글자수 최소 길이 체크
        if len(clean_title) < 5:
            return {"is_passed": False, "score": 0.0, "reason": "제목이 너무 짧음"}

        # 1. 네거티브 블랙리스트 검사 (구인/비자/금융/의료 즉각 탈락)
        for pattern in cls.NEGATIVE_PATTERNS:
            match = re.search(pattern, combined, re.IGNORECASE)
            if match:
                return {
                    "is_passed": False,
                    "score": 0.0,
                    "reason": f"블랙리스트 키워드 포착: '{match.group(0)}'"
                }

        # 1.5. 글로벌 서브레딧인 경우, 한국 관련 앵커(K-Context) 필수 검증
        sub_lower = (subreddit or "").lower()
        if any(sub_lower == g.lower() for g in cls.GLOBAL_SUBREDDITS):
            k_anchor_pattern = r"\b(korea|korean|koreans|seoul|busan|incheon|daegu|daejeon|gwangju|한국|한국인|hanguk|yeonnam|hongdae|gangnam|itaewon)\b"
            if not re.search(k_anchor_pattern, combined, re.IGNORECASE):
                return {
                    "is_passed": False,
                    "score": 0.0,
                    "reason": f"글로벌 서브레딧(r/{subreddit}) 내 한국 앵커(Korea/Korean/Seoul 등) 부재"
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

        # 3. 본문(Body) 심층 질문 및 진성 감정 가산점 (최대 20점)
        if len(clean_body) > 30:
            total_score += 5.0  # 본문이 충실한 질문글에 기본 가산

        for b_pat in cls.BODY_BOOSTERS:
            if re.search(b_pat, combined, re.IGNORECASE):
                total_score += 4.0

        # 물음표 포함 시 5점 추가
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


class AuraRedditScanner:
    """Aura 데이팅 전용 레딧 실시간 2단계 족집게 스캐너"""

    def __init__(self, db_mgr: Optional[DBManager] = None, driver: Optional[RedditBrowserDriver] = None):
        self.db_mgr = db_mgr or DBManager()
        self.driver = driver or RedditBrowserDriver(service_id="aura")
        self.copywriter = AuraRedditCopywriter()

    def scan_target_subreddits(
        self,
        subreddits: Optional[List[str]] = None,
        limit_per_sub: int = 15,
        max_final_leads: int = 3
    ) -> List[Dict[str, Any]]:
        """
        타겟 서브레딧 스캔 ➔ 1단계 순수 파이썬 제목+본문 심층 심사(비용 0원) ➔ 상위 1등 글에만 2단계 제미나이 정밀 검증
        """
        target_subs = subreddits or AURA_TARGET_SUBREDDITS
        logger.info(f"🔍 [Aura Reddit Scanner] {len(target_subs)}개 서브레딧 실시간 스캔 가동...")

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
            eval_res = AuraRedditFilter.evaluate_post(title, body, subreddit=subreddit)
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

            intent_res = self.copywriter.classify_aura_reddit_intent(title, body)
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
        ("I need help with my F-2-7 visa point calculation", "Immigration office rejected my document", False),
        ("Looking for Korean language exchange partner to practice speaking without creeps", "Tandem was too awkward and full of weird guys", True),
        ("Solo female traveler in Seoul looking for Hongdae cafe buddy", "Anyone want to grab coffee in Seongsu or Yeonnam?", True),
        ("How to trade crypto without Korean bank account?", "Upbit verification is blocked", False),
        ("Are there any Korean chat apps that don't need a Korean phone number?", "KakaoTalk and other apps require PASS", True),
    ]
    for t, b, expected in test_cases:
        res = AuraRedditFilter.evaluate_post(t, b)
        status = "PASS" if res["is_passed"] else "FAIL"
        print(f"[{status}] (Score: {res['score']}pt) '{t}' -> Expected: {expected} | Actual: {res['is_passed']}")
