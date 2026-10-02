# -*- coding: utf-8 -*-
"""
StockSNSGuideGenerator - 📢 [StockMaster AI 전용 숏폼 5대 SNS 포스팅 가이드 자동 생성 모듈]
========================================================================================
- 유튜브 쇼츠(YouTube Shorts), 틱톡(TikTok), 인스타그램 릴스(Instagram Reels), 페이스북 릴스(Facebook Reels), 네이버 클립(Naver Clip)
- 숏폼 영상 1편이 생성될 때마다 해당 영상 폴더 내에 'SNS_포스팅_가이드.txt'를 100% 무인 자동 생성
- 관리자가 복사(Ctrl+C)해서 각 SNS 플랫폼에 즉시 포스팅할 수 있는 완벽한 템플릿 제공
- 공식 검색어: [스톡마스터 AI] (띄어쓰기 필수!) / 공식 URL: https://stockmaster-ai.vercel.app/
- 자본시장법 준수: 특정 종목 매수/매도 권유 0%, 퀀트 데이터 기반 자가진단 및 객관적 지표 알림 면책고지 탑재
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger("StockSNSGuideGenerator")

STOCK_TOPIC_SNS_DATA: Dict[int, Dict[str, Any]] = {
    1: {
        "theme_name": "삼성전자 vs SK하이닉스 HBM 수급 대결",
        "theme_code": "samsung_vs_hynix_hbm",
        "yt_title": "삼성전자 vs SK하이닉스, 지금 반도체 뭘 사야 할까? 외국인 수급과 퀀트 적정주가로 본 승자는? #Shorts",
        "yt_desc": (
            "삼성전자와 SK하이닉스 중 지금 어디에 들어가야 할지 밤마다 고민되시나요?\n"
            "글로벌 AI 반도체 HBM 공급망 수급과 메이저 외국인 순매수 추이를 퀀트 데이터로 1초 만에 비교해 드립니다!\n"
            "감으로 하는 매매 대신 객관적인 지표로 먼저 확인하세요.\n\n"
            "👉 실시간 반도체 퀀트 수급 & 적정주가 무료 확인\n"
            "🔗 네이버 검색창에 [스톡마스터 AI] 검색!\n"
            "공식 사이트: https://stockmaster-ai.vercel.app/\n"
        ),
        "pinned_comment": "📌 삼전 vs 하이닉스 외인/기관 실시간 수급 비교! 네이버에 '스톡마스터 AI' 검색하고 확인해보세요 ✨",
        "tiktok_caption": (
            "삼성전자 살까 SK하이닉스 살까 고민될 때 ㅋㅋㅋ\n"
            "외국인 수급이랑 적정주가 1초 만에 비교하는 법!\n"
            "👇 프로필 링크에서 실시간 퀀트 데이터 확인!"
        ),
        "reels_caption": (
            "반도체 대장주 투자 고민 중이신 분들 필독 🚨\n\n"
            "깜깜이 매매는 그만! 실시간 외국인·기관 수급과 퀀트 적정주가로 승부처를 확인하세요.\n"
            "스톡마스터 AI에서 전화번호 없이 종목명만으로 즉시 비교 가능합니다!\n\n"
            "✨ 스톡마스터 AI 3대 핵심 포인트:\n"
            "1️⃣ 외국인/기관 실시간 쌍끌이 순매수 레이더\n"
            "2️⃣ 객관적 퀀트 AI 적정주가 & 밸류에이션 산출\n"
            "3️⃣ 리스크 가드 자동 손절매 알림\n\n"
            "👉 프로필 링크나 네이버에서 [스톡마스터 AI]를 검색하세요!"
        ),
        "fb_text": (
            "삼성전자와 SK하이닉스, 과연 승자는? 실시간 외국인 수급과 퀀트 적정주가 비교 리포트를 댓글 링크에서 무료로 확인하세요!"
        ),
        "naver_clip_text": (
            "삼성전자 vs SK하이닉스 HBM 수급 대결 총정리! 스마트 개미를 위한 반도체 퀀트 투자 꿀팁.\n"
            "네이버 검색창에 [스톡마스터 AI]를 검색해보세요."
        ),
        "base_hashtags": ["#삼성전자", "#SK하이닉스", "#HBM", "#반도체주식", "#주식투자", "#스톡마스터AI", "#퀀트투자", "#Shorts", "#Reels"]
    },
    2: {
        "theme_name": "국내 고배당주(금융지주·맥쿼리) 월배당 시뮬레이션",
        "theme_code": "korea_high_dividend_sim",
        "yt_title": "월급 말고 매달 배당금 꽂히는 국내 고배당주 포트폴리오의 비밀 #Shorts",
        "yt_desc": (
            "월급 외에 매달 쏠쏠하게 들어오는 배당 파이프라인, 부러우셨나요?\n"
            "국내 대표 금융지주사와 맥쿼리인프라 등 고배당 알짜주의 황금 비율을 투자금만 넣으면 1초 만에 시뮬레이션해 드립니다!\n\n"
            "👉 내 투자금으로 국내 고배당 계산해보기\n"
            "🔗 네이버 검색창에 [스톡마스터 AI] 검색!\n"
            "공식 사이트: https://stockmaster-ai.vercel.app/\n"
        ),
        "pinned_comment": "💰 매달 배당 파이프라인 만들기! 네이버에 '스톡마스터 AI' 검색하고 시뮬레이션 돌려보세요!",
        "tiktok_caption": (
            "월급 말고 매달 배당금 받는 법 ㄷㄷ\n"
            "국내 고배당주 황금비율 1초 시뮬레이션!\n"
            "👇 프로필 링크에서 내 예상 배당금 확인!"
        ),
        "reels_caption": (
            "통장에 차곡차곡 꽂히는 국내 고배당 파이프라인 📈\n\n"
            "금융지주사와 우량 배당주 포트폴리오로 안정적인 현금흐름을 만드세요.\n"
            "스톡마스터 AI 배당 계산기에서 투자금만 넣으면 월 예상 수령액이 즉시 나옵니다!\n\n"
            "👉 프로필 링크나 네이버에서 [스톡마스터 AI]를 검색하세요!"
        ),
        "fb_text": (
            "국내 고배당주로 월배당 만들기! 최적 배당 비율을 댓글 링크에서 무료로 확인해보세요."
        ),
        "naver_clip_text": (
            "국내 고배당주 월배당 시스템! 알짜 고배당 포트폴리오 비교.\n"
            "네이버 검색창에 [스톡마스터 AI]를 검색해보세요."
        ),
        "base_hashtags": ["#국내배당주", "#고배당주", "#맥쿼리인프라", "#금융지주", "#배당주투자", "#스톡마스터AI", "#파이어족", "#Shorts", "#Reels"]
    },
    3: {
        "theme_name": "코스피·코스닥 세력 체결강도 120% 돌파 유망주",
        "theme_code": "korea_volume_power_breakout",
        "yt_title": "오늘 장중 외국인·기관 체결강도 120% 돌파 급등 유망주 포착 #Shorts",
        "yt_desc": (
            "당일 장중 메이저 세력 수급이 급격히 쏠리는 주도주가 궁금하셨나요?\n"
            "체결강도 120% 돌파 종목과 대량 블록오더를 AI가 실시간으로 분석해 드립니다.\n\n"
            "👉 국내 주도주 실시간 체결강도 전광판 확인하기\n"
            "🔗 네이버 검색창에 [스톡마스터 AI] 검색!\n"
            "공식 사이트: https://stockmaster-ai.vercel.app/\n"
        ),
        "pinned_comment": "🚀 실시간 체결강도 \u0026 세력 수급 분석! 네이버에 '스톡마스터 AI' 검색하고 확인해보세요!",
        "tiktok_caption": "체결강도 120% 돌파 주도주 포착! AI 수급 분석으로 1초 만에 확인하기!",
        "reels_caption": "코스피·코스닥 세력 매집 포착! 실시간 체결강도를 네이버 [스톡마스터 AI]에서 확인하세요.",
        "fb_text": "코스피·코스닥 실시간 체결강도 상위 종목 분석표를 댓글 링크에서 확인하세요.",
        "naver_clip_text": "코스피 코스닥 체결강도 120% 돌파 종목 분석. 네이버에서 [스톡마스터 AI] 검색!",
        "base_hashtags": ["#체결강도", "#코스피", "#코스닥", "#주도주", "#세력수급", "#스톡마스터AI", "#Shorts"]
    },
    4: {
        "theme_name": "저PBR 밸류업 & 고배당 금융주 스크리너",
        "theme_code": "valueup_low_pbr_screener",
        "yt_title": "정부 밸류업 정책 최대 수혜주! PBR 1배 미만 알짜 금융지주사 1초 스크리닝 #Shorts",
        "yt_desc": (
            "밸류업 정책 터졌는데 어떤 저PBR 종목을 사야 할지 막막하셨나요?\n"
            "자사주 소각하고 배당 늘리는 알짜 저평가 기업만 쏙 골라냈습니다.\n\n"
            "👉 저PBR 밸류업 알짜주 무료 스크리닝\n"
            "🔗 네이버 검색창에 [스톡마스터 AI] 검색!\n"
            "공식 사이트: https://stockmaster-ai.vercel.app/\n"
        ),
        "pinned_comment": "🏦 저PBR 밸류업 알짜 수혜주 순위표! 네이버에 '스톡마스터 AI' 검색해보세요!",
        "tiktok_caption": "PBR 1배 미만 알짜 금융주 1초 만에 찾는 법!",
        "reels_caption": "밸류업 정책 수혜주 총정리! 네이버에서 [스톡마스터 AI]를 검색하세요.",
        "fb_text": "저PBR 알짜 기업 리스트를 댓글 링크에서 무료로 확인하세요.",
        "naver_clip_text": "저PBR 밸류업 & 고배당 금융주 스크리닝. 네이버에서 [스톡마스터 AI] 검색!",
        "base_hashtags": ["#저PBR", "#밸류업", "#금융주", "#배당주", "#주식스크리너", "#스톡마스터AI", "#Shorts"]
    },
    5: {
        "theme_name": "뇌동매매 방지! AI 자동 손절매 & 리스크 가드",
        "theme_code": "anti_fomo_ai_risk_guard",
        "yt_title": "급등주 추격매수하다 계좌 녹은 사람 필독! AI 기계적 손절매 원칙의 위력 #Shorts",
        "yt_desc": (
            "급등주 따라 샀다가 손절 타이밍 놓쳐서 물린 적 있으신가요?\n"
            "감정 빼고 AI가 계산해 준 기계적 손절선과 익절 목표가로 원칙 매매를 시작하세요.\n\n"
            "👉 내 종목 AI 손절선 & 리스크 진단\n"
            "🔗 네이버 검색창에 [스톡마스터 AI] 검색!\n"
            "공식 사이트: https://stockmaster-ai.vercel.app/\n"
        ),
        "pinned_comment": "🛡️ 뇌동매매 끝내고 AI 손절선 세팅하기! 네이버에 '스톡마스터 AI' 검색해보세요!",
        "tiktok_caption": "물타기 그만! AI가 알려주는 기계적 손절 라인 ㄷㄷ",
        "reels_caption": "뇌동매매 방지 AI 리스크 가드! 네이버에서 [스톡마스터 AI] 검색!",
        "fb_text": "감정 없는 AI 기계적 손절매 가이드. 댓글 링크에서 확인하세요.",
        "naver_clip_text": "AI 자동 손절매 & 리스크 가드. 네이버에서 [스톡마스터 AI] 검색!",
        "base_hashtags": ["#손절매", "#뇌동매매", "#투자원칙", "#주식리스크", "#스톡마스터AI", "#Shorts"]
    },
    6: {
        "theme_name": "코스피200 우량주 vs 코스닥 성장주 직장인 월적립식 복리",
        "theme_code": "kospi200_kosdaq_compound_sim",
        "yt_title": "월 50만원씩 10년 모으면 얼마 될까? 코스피200 vs 코스닥 성장주 복리 시뮬레이션 #Shorts",
        "yt_desc": (
            "월급 50만 원씩 국내 대표 지수 및 우량주에 꾸준히 모으면 미래 자산은 과연 얼마가 될까요?\n"
            "복리의 마법으로 은퇴 자산 만드는 10년 수익 곡선을 직접 확인하세요!\n\n"
            "👉 10년 복리 자산 시뮬레이션 돌리기\n"
            "🔗 네이버 검색창에 [스톡마스터 AI] 검색!\n"
            "공식 사이트: https://stockmaster-ai.vercel.app/\n"
        ),
        "pinned_comment": "📈 월 50만 원으로 목돈 만들기 복리 시뮬레이터! 네이버에 '스톡마스터 AI' 검색해보세요!",
        "tiktok_caption": "직장인 월 50만원 적립식 투자 10년 후 자산 결과 ㄷㄷ",
        "reels_caption": "코스피200 vs 코스닥 성장주 10년 복리 수익률 비교! 네이버에서 [스톡마스터 AI] 검색!",
        "fb_text": "국내 주식 10년 적립식 복리 계산기. 댓글 링크에서 무료 확인!",
        "naver_clip_text": "직장인 국내 지수 적립식 복리 시뮬레이션. 네이버에서 [스톡마스터 AI] 검색!",
        "base_hashtags": ["#코스피200", "#코스닥", "#적립식투자", "#복리의마법", "#직장인재테크", "#스톡마스터AI", "#Shorts"]
    },
    7: {
        "theme_name": "외국인·기관 쌍끌이 순매수 실시간 레이더",
        "theme_code": "foreign_institution_radar",
        "yt_title": "개미들만 사고 세력은 다 파는 종목에 물리지 마세요! 외인·기관 쌍끌이 레이더 #Shorts",
        "yt_desc": (
            "메이저 큰손들이 3일 연속 쓸어 담는 진짜 주도주를 실시간으로 포착하세요!\n"
            "스톡마스터 AI 수급 레이더로 세력 수급에 올라타는 스마트 매매를 시작하세요.\n\n"
            "👉 실시간 외인·기관 쌍끌이 종목 확인\n"
            "🔗 네이버 검색창에 [스톡마스터 AI] 검색!\n"
            "공식 사이트: https://stockmaster-ai.vercel.app/\n"
        ),
        "pinned_comment": "🔍 외인·기관 실시간 쌍끌이 순매수 종목! 네이버에 '스톡마스터 AI' 검색해보세요!",
        "tiktok_caption": "외국인 기관이 오늘 쓸어 담은 종목 1초 만에 확인하기!",
        "reels_caption": "메이저 세력 수급 추종 매매! 네이버에서 [스톡마스터 AI] 검색!",
        "fb_text": "실시간 외국인/기관 순매수 상위 종목 레이더. 댓글 링크에서 무료 확인!",
        "naver_clip_text": "외국인 기관 실시간 쌍끌이 순매수 레이더. 네이버에서 [스톡마스터 AI] 검색!",
        "base_hashtags": ["#외국인순매수", "#기관순매수", "#쌍끌이매수", "#주도주", "#수급매매", "#스톡마스터AI", "#Shorts"]
    },
    8: {
        "theme_name": "초보 탈출! 원클릭 AI 종목 재무 건전성 진단",
        "theme_code": "oneclick_ai_financial_check",
        "yt_title": "재무제표 볼 줄 몰라도 상장폐지 위험 종목 3초 만에 거르는 AI 진단법 #Shorts",
        "yt_desc": (
            "어려운 재무제표 보느라 머리 아프셨나요?\n"
            "영업이익, 부채비율, 현금흐름 3대 지표를 AI가 100점 만점으로 바로 진단해 드립니다!\n\n"
            "👉 내 보유 종목 재무 건전성 1초 진단\n"
            "🔗 네이버 검색창에 [스톡마스터 AI] 검색!\n"
            "공식 사이트: https://stockmaster-ai.vercel.app/\n"
        ),
        "pinned_comment": "📊 내 종목 재무 건전성 100점 만점 점수 확인! 네이버에 '스톡마스터 AI' 검색해보세요!",
        "tiktok_caption": "상폐 위험 종목 3초 만에 거르는 AI 재무 진단 ㄷㄷ",
        "reels_caption": "초보 투자자를 위한 원클릭 AI 재무 진단! 네이버에서 [스톡마스터 AI] 검색!",
        "fb_text": "내 종목 상폐 위험도 & 재무 건전성 점수 무료 진단. 댓글 링크 확인!",
        "naver_clip_text": "원클릭 AI 종목 재무 건전성 진단. 네이버에서 [스톡마스터 AI] 검색!",
        "base_hashtags": ["#재무제표", "#상장폐지", "#주식초보", "#재무건전성", "#종목진단", "#스톡마스터AI", "#Shorts"]
    }
}


class StockSNSGuideGenerator:
    """📈 StockMaster AI 전용 숏폼 SNS 포스팅 가이드 자동 생성기"""

    OFFICIAL_KEYWORD = "스톡마스터 AI"
    OFFICIAL_URL = "https://stockmaster-ai.vercel.app/"

    @classmethod
    def generate_guide_content(
        cls,
        topic_id: int,
        speech_hook: Optional[str] = None,
        debate_question: Optional[str] = None
    ) -> str:
        norm_id = ((topic_id - 1) % len(STOCK_TOPIC_SNS_DATA)) + 1
        data = STOCK_TOPIC_SNS_DATA.get(norm_id, STOCK_TOPIC_SNS_DATA[1])

        theme_name = data["theme_name"]

        # 🌟 실시간 바이럴 해시태그 융합 (StockKeywordMatrix 실시간 검색 트렌드 + 네이버/구글 핫키워드)
        try:
            from brands.stock.stock_keyword_matrix import StockKeywordMatrix
            matrix = StockKeywordMatrix()
            live_tag_list = matrix.get_live_hashtags(
                topic_id=norm_id,
                base_tags=data.get("base_hashtags", []),
                count=10
            )
            tags_str = " ".join(live_tag_list)
        except Exception:
            tags_str = " ".join(data.get("base_hashtags", []))

        # 💬 [Stock 전용 찬반 논쟁 유발 고정 댓글 생성기 (독립 레고 블록)]
        try:
            from brands.stock.stock_debate_booster import StockDebateBooster
            debate_bundle = StockDebateBooster.generate_pinned_comments(
                topic_id=norm_id,
                custom_question=debate_question
            )
            pinned_comment = debate_bundle["youtube_pinned"]
            active_debate_q = debate_bundle["debate_question"]
        except Exception:
            pinned_comment = data["pinned_comment"]
            active_debate_q = "여러분의 투자 선택은?"

        guide = f"""================================================================================
📈 [StockMaster AI 숏폼 5대 SNS 즉시 포스팅 가이드]
================================================================================
- 주제 번호: #{norm_id:02d} - {theme_name}
- 공식 검색어: [{cls.OFFICIAL_KEYWORD}] (띄어쓰기 필수!)
- 공식 웹앱 URL: {cls.OFFICIAL_URL}
- 💬 찬반/투자 토론 질문: {active_debate_q}
- 심의 준수: 특정 종목 매수/매도 권유 0%, 퀀트 데이터 기반 자가진단 및 객관적 지표 알림

--------------------------------------------------------------------------------
1. 🔴 유튜브 쇼츠 (YouTube Shorts) - 제목 & 설명 & 고정댓글
--------------------------------------------------------------------------------
[제목] (복사해서 제목란에 붙여넣기)
{data['yt_title']}

[설명] (복사해서 설명란에 붙여넣기)
{data['yt_desc']}
{tags_str}

[고정 댓글 (댓글창 투자 토론 & 찬반 루프)] (업로드 후 첫 댓글로 달고 '고정' 클릭)
{pinned_comment}

--------------------------------------------------------------------------------
2. ⚫ 틱톡 (TikTok) - 캡션 & 해시태그
--------------------------------------------------------------------------------
[캡션 및 태그] (복사해서 틱톡 캡션에 붙여넣기)
{data['tiktok_caption']}

{tags_str}

--------------------------------------------------------------------------------
3. 🟣 인스타그램 릴스 (Instagram Reels) - 캡션 & 해시태그
--------------------------------------------------------------------------------
[본문 및 해시태그] (복사해서 인스타 릴스 캡션에 붙여넣기)
{data['reels_caption']}

.
.
{tags_str}

--------------------------------------------------------------------------------
4. 🔵 페이스북 릴스 / 피드 (Facebook Reels)
--------------------------------------------------------------------------------
{data['fb_text']}

{tags_str}

--------------------------------------------------------------------------------
5. 🟢 네이버 클립 / 블로그 모먼트 (Naver Clip)
--------------------------------------------------------------------------------
{data['naver_clip_text']}

{tags_str}

================================================================================
"""
        return guide

    @classmethod
    def save_guide_file(
        cls,
        output_folder: Path,
        topic_id: int,
        speech_hook: Optional[str] = None,
        debate_question: Optional[str] = None
    ) -> Path:
        out_p = Path(output_folder).resolve()
        out_p.mkdir(parents=True, exist_ok=True)
        guide_file = out_p / "SNS_포스팅_가이드.txt"
        content = cls.generate_guide_content(
            topic_id=topic_id,
            speech_hook=speech_hook,
            debate_question=debate_question
        )
        guide_file.write_text(content, encoding="utf-8")
        logger.info(f"📄 [StockSNSGuideGenerator] SNS 포스팅 가이드 저장 완료: {guide_file}")
        return guide_file
