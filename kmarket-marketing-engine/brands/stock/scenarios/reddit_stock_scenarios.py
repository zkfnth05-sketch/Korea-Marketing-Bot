# -*- coding: utf-8 -*-
"""
Stock Reddit Scenarios - 📈 [StockMaster AI 전용 레딧 글로벌/국내 투자자 유입 12대 골든 시나리오 DB]
===================================================================================================
• 역할:
  - 글로벌/국내 주식 투자자(개인 투자자, 퀀트/알고 트레이더, 반도체/HBM 관심자, 코스피 외국인 투자자)의 니즈를 100% 저격
  - 5대 타겟 클러스터(외인기관 수급, AI 퀀트/알고리즘, 반도체/HBM, 리스크관리/Anti-FOMO, 글로벌 분산투자)별 맞춤형 페르소나 및 프롬프트 주입
  - 핵심 소구점:
    1. 외인·기관 실시간 쌍끌이 수급 레이더 (Foreigner & Institutional Real-Time Inflow Radar)
    2. AI 퀀트 4대 모달 종합 스코어링 & 목표가 산출 (4-Modal AI Quant Score & Target Price)
    3. 뇌동매매 방지 Anti-FOMO 리스크 가드 (Risk Management & Position Sizing Guard)
    4. 1초 원클릭 브라우저 AI 퀀트 대시보드 (Zero Login Instant Web Dashboard)
  - 스텔스 철칙: 직접 URL 0% (Zero URL) + 오직 검색어 '스톡마스터 AI' (또는 'StockMaster AI') 유도
"""

from typing import Dict, Any

STOCK_REDDIT_SCENARIOS: Dict[int, Dict[str, Any]] = {
    1: {
        "scenario_id": 1,
        "cluster": "institutional_flow",
        "theme_name": "외인·기관 실시간 쌍끌이 수급 포착 레이더 (Foreigner & Institutional Inflow Radar)",
        "target_subreddits": ["stocks", "investing", "StockMarket", "koreanstocks", "Daytrading"],
        "pain_points": "개미 투자자들이 항상 늦게 진입하여 외인/기관의 차익 실현 물량받이가 되는 문제",
        "solution_feature": "StockMaster AI의 실시간 외인·기관 쌍끌이 수급 분석 레이더 (장중 실시간 순매수 포착)",
        "stealth_cta": "Just search 'StockMaster AI' (or '스톡마스터 AI') on Google to check out their live institutional inflow radar directly in your browser.",
        "sample_reply": (
            "The hardest part for retail traders is seeing institutional money moves before the breakout actually happens. 📉 "
            "By the time financial news reports foreign buying, retail investors are already holding the bag at the top. "
            "I've been tracking a real-time institutional & foreign money inflow radar that tracks net buying volume during market hours. "
            "It alerts you when both foreign funds and domestic institutions double-accumulate specific tech/semiconductor tickers before big rallies. "
            "You can search 'StockMaster AI' (or '스톡마스터 AI') on Google to view the live inflow radar for free in your browser."
        )
    },
    2: {
        "scenario_id": 2,
        "cluster": "ai_quant_scoring",
        "theme_name": "AI 퀀트 4대 모달 종합 스코어 & 목표가 진단 (4-Modal AI Quant Score & Target Price)",
        "target_subreddits": ["stocks", "investing", "algotrading", "StockMarket", "wallstreetbets"],
        "pain_points": "재무제표, 차트, 수급, 뉴스 공시를 개인이 일일이 종합 분석하기 복잡하고 시간이 부족함",
        "solution_feature": "재무/기술/수급/감성 4대 모달 AI 퀀트 스코어링 및 실시간 적정 목표가 산출",
        "stealth_cta": "Search 'StockMaster AI' (or '스톡마스터 AI') on Google to test the free 4-modal AI quant scorecard.",
        "sample_reply": (
            "Trying to manually cross-analyze 10-K financial ratios, MACD/RSI technical indicators, order book depth, and market sentiment takes hours for each ticker. "
            "There's an AI quant engine that synthesizes all four dimensions (Fundamentals, Technicals, Institutional Flow, and News Sentiment) into a single 0-100 Quant Score with dynamic fair value target prices. "
            "It gives you an objective snapshot of whether a stock is truly undervalued or just a bull trap. "
            "Search 'StockMaster AI' (or '스톡마스터 AI') on Google to analyze your watchlist tickers instantly!"
        )
    },
    3: {
        "scenario_id": 3,
        "cluster": "risk_management",
        "theme_name": "뇌동매매 방지 Anti-FOMO 리스크 가드 (Risk Management & Anti-FOMO Position Sizing)",
        "target_subreddits": ["Daytrading", "wallstreetbets", "stocks", "investing"],
        "pain_points": "급등주를 보고 충동적으로 추격 매수(FOMO)했다가 고점에 물리고 손절을 못해 큰 손실 발생",
        "solution_feature": "StockMaster AI의 Anti-FOMO 포지션 사이징 가이드 및 변동성 기반 손절/익절 자동 계산기",
        "stealth_cta": "Search 'StockMaster AI' (or '스톡마스터 AI') on Google to calculate your optimal position size and risk limits.",
        "sample_reply": (
            "Emotional FOMO buying at the peak is what wipes out 90% of retail trading accounts. 🛑 "
            "Having a strict risk management framework based on ATR (Average True Range) and kelly criterion sizing completely changes your win rate. "
            "I use an AI risk guard tool that calculates the exact dollar position size and hard stop-loss level before you enter any high-volatility trade so you never risk more than 1-2% of total capital. "
            "Just search 'StockMaster AI' (or '스톡마스터 AI') on Google to calculate your safe position limits."
        )
    },
    4: {
        "scenario_id": 4,
        "cluster": "semiconductor_hbm",
        "theme_name": "삼성전자/SK하이닉스 HBM 반도체 밸류체인 진단 (HBM Semiconductor Value Chain Tracker)",
        "target_subreddits": ["koreanstocks", "stocks", "investing", "Korea", "algotrading"],
        "pain_points": "엔비디아 발 AI 반도체 붐 속에서 한국/글로벌 HBM 수혜주 밸류체인을 명확히 파악하기 어려움",
        "solution_feature": "글로벌 AI 반도체 및 HBM3E/HBM4 관련 소부장(소재/부품/장비) 실시간 밸류체인 맵",
        "stealth_cta": "Search 'StockMaster AI' (or '스톡마스터 AI') on Google to view the live semiconductor supply chain matrix.",
        "sample_reply": (
            "If you're following the global AI hardware boom, understanding the Samsung & SK Hynix HBM (High Bandwidth Memory) packaging supply chain is crucial. 💡 "
            "Beyond just NVIDIA, the second-tier Korean semiconductor equipment and testing makers (TC bonders, advanced packaging) often experience massive institutional capital inflows first. "
            "There's a specialized AI radar mapping out the real-time supply chain relationships and foreign buying momentum for memory tech. "
            "Search 'StockMaster AI' (or '스톡마스터 AI') on Google to explore the live HBM value chain tracker."
        )
    },
    5: {
        "scenario_id": 5,
        "cluster": "ai_quant_scoring",
        "theme_name": "테마주 급등락 변동성 예측 & 골든크로스 시그널 (Volatility Forecaster & Golden Cross)",
        "target_subreddits": ["Daytrading", "StockMarket", "stocks", "algotrading"],
        "pain_points": "단기 급등주나 돌파 구간에서 가짜 돌파(Fakeout)에 속아 손실을 입는 현상",
        "solution_feature": "거래량 급증 및 호가창 체결 강도 기반 AI 돌파 신뢰도 판별 엔진",
        "stealth_cta": "Search 'StockMaster AI' (or '스톡마스터 AI') on Google to test real-time breakout confirmation signals.",
        "sample_reply": (
            "Fakeouts on breakout charts happen constantly when volume doesn't back up the price action. 📊 "
            "Instead of relying on basic moving average crossovers, looking at order book absorption ratios and tick-by-tick buyer aggression gives a much clearer picture of real institutional breakouts. "
            "An AI algorithm that filters out fake volume spikes has helped me avoid so many trap entries. "
            "Search 'StockMaster AI' (or '스톡마스터 AI') on Google to check breakout validation metrics in real time."
        )
    },
    6: {
        "scenario_id": 6,
        "cluster": "global_tech_sync",
        "theme_name": "미국 빅테크(NVDA/TSLA) vs 아시아 수혜주 동조화 분석 (Global Tech Sync & Beneficiary Radar)",
        "target_subreddits": ["stocks", "investing", "koreanstocks", "StockMarket"],
        "pain_points": "미국 증시 빅테크 실적 발표 후 아시아/한국 관련주가 어떻게 반응할지 선제적 대응이 늦음",
        "solution_feature": "미국 선물 및 나스닥 빅테크 변동성과 아시아 반도체/2차전지 동조화 AI 상관계수 레이더",
        "stealth_cta": "Search 'StockMaster AI' (or '스톡마스터 AI') on Google to track global correlation signals before market open.",
        "sample_reply": (
            "When NVIDIA or Tesla moves ±5% after-hours, Asian suppliers and ecosystem stocks react strongly the very next morning at Seoul/Tokyo open. 🌐 "
            "Having an automated cross-market correlation dashboard that calculates exact beta and lead-lag relationships helps you position before market opening bells. "
            "It saves a ton of guessing on overnight earnings impacts. "
            "You can search 'StockMaster AI' (or '스톡마스터 AI') on Google to view live global synchronization insights."
        )
    },
    7: {
        "scenario_id": 7,
        "cluster": "zero_friction",
        "theme_name": "1초 원클릭 브라우저 AI 퀀트 대시보드 (Zero Verification Instant Web Quant Platform)",
        "target_subreddits": ["investing", "stocks", "algotrading", "koreanstocks"],
        "pain_points": "복잡한 HTS 설치나 공인인증서/유료 가입 없이 웹 브라우저에서 바로 실시간 퀀트 분석을 보고 싶음",
        "solution_feature": "별도 설치 없는 100% 웹 기반 실시간 AI 퀀트 대시보드 및 무료 종목 진단",
        "stealth_cta": "Search 'StockMaster AI' (or '스톡마스터 AI') on Google to open the instant web quant platform without any installation.",
        "sample_reply": (
            "Most Korean/Asian market trading software requires clunky HTS installations, security plugins, and identity verifications that foreigners can barely navigate. 💻 "
            "StockMaster AI runs 100% in modern web browsers with zero installation and zero complicated signup walls. "
            "You get instant access to live quant scores, institutional flow charts, and technical alerts right from your phone or laptop. "
            "Just search 'StockMaster AI' (or '스톡마스터 AI') on Google to test it directly in your browser."
        )
    },
    8: {
        "scenario_id": 8,
        "cluster": "dividend_value",
        "theme_name": "고배당주 & 가치주 안전 리밸런싱 (High Dividend & Value Stock Safety Rebalancer)",
        "target_subreddits": ["dividends", "investing", "stocks"],
        "pain_points": "배당 수익률만 보고 진입했다가 주가 폭락이나 배당 삭감(배당 트랩)으로 원금을 잃는 문제",
        "solution_feature": "배당 지속가능성(잉여현금흐름 FCF 기반) 및 밸류에이션 안전 마진 AI 스크리너",
        "stealth_cta": "Search 'StockMaster AI' (or '스톡마스터 AI') on Google to screen dividend sustainability and safety scores.",
        "sample_reply": (
            "Chasing high dividend yields without checking Free Cash Flow (FCF) payout ratios is how dividend investors get trapped in dying businesses. 💰 "
            "An AI screening model that checks 5-year dividend CAGR, operating cash flow coverage, and debt maturity schedules helps filter out dividend traps before cuts happen. "
            "It automatically ranks companies with fortress balance sheets that can sustain 6-9% yields safely. "
            "Search 'StockMaster AI' (or '스톡마스터 AI') on Google to check dividend safety ratings for your portfolio."
        )
    },
    9: {
        "scenario_id": 9,
        "cluster": "algotrading_quant",
        "theme_name": "승률 80% 퀀트 백테스팅 전략 검증 (Backtested Quant Trading Strategies)",
        "target_subreddits": ["algotrading", "Daytrading", "options", "stocks"],
        "pain_points": "자신의 매매 원칙이나 차트 패턴의 실제 역사적 승률과 MDD(최대 낙폭)를 검증하기 어려움",
        "solution_feature": "10년치 틱 데이터 기반 AI 퀀트 백테스팅 및 최적 리스크-보상 비율 산출",
        "stealth_cta": "Search 'StockMaster AI' (or '스톡마스터 AI') on Google to explore backtested algorithmic setups.",
        "sample_reply": (
            "Trading discretionary setups without backtesting is essentially gambling against quantitative hedge funds. 📈 "
            "Running historical backtests on volume-profile breakouts and mean-reversion RSI divergences reveals the exact Sharpe ratio, profit factor, and maximum drawdown of every strategy. "
            "StockMaster AI's backtested models highlight setups with statistically proven >75% win rates under various market regimes. "
            "Search 'StockMaster AI' (or '스톡마스터 AI') on Google to see algorithmically validated trade setups."
        )
    },
    10: {
        "scenario_id": 10,
        "cluster": "macro_hedging",
        "theme_name": "글로벌 거시경제(환율/금리/유가) 연동 포트폴리오 헤지 (Macro Risk Hedging Radar)",
        "target_subreddits": ["investing", "stocks", "StockMarket", "Korea"],
        "pain_points": "원/달러 환율 급등이나 미국 연준 금리 변동 시 내 보유 종목이 받는 타격을 예측하기 어려움",
        "solution_feature": "환율/국채금리/원자재 가격 변동에 따른 업종별 민감도 AI 거시 리스크 매트릭스",
        "stealth_cta": "Search 'StockMaster AI' (or '스톡마스터 AI') on Google to view the macro sensitivity hedge matrix.",
        "sample_reply": (
            "Macro factors like USD/KRW currency spikes and US 10-year Treasury yield surges can completely derail individual stock momentum. 📉 "
            "Having an AI macro risk dashboard that flags which export tech stocks benefit from weak currencies versus which consumer staples get hurt by input inflation is essential for hedging. "
            "It gives you a clear roadmap for defensive portfolio adjustments. "
            "Search 'StockMaster AI' (or '스톡마스터 AI') on Google to analyze macro currency & interest rate impacts on your assets."
        )
    },
    11: {
        "scenario_id": 11,
        "cluster": "disclosure_factcheck",
        "theme_name": "실시간 공시/수주 찌라시 팩트체크 (Real-Time Disclosure & News Fact Checker)",
        "target_subreddits": ["koreanstocks", "stocks", "Daytrading", "StockMarket"],
        "pain_points": "주식 커뮤니티의 가짜 호재나 과장된 찌라시 뉴스에 속아 뇌동매매하는 위험",
        "solution_feature": "금감원 DART 전자공시 및 언론사 보도 실시간 AI 팩트체크 & 핵심 요약 엔진",
        "stealth_cta": "Search 'StockMaster AI' (or '스톡마스터 AI') on Google for verified corporate disclosure summaries.",
        "sample_reply": (
            "Social media stock hype and unverified forum rumors cause massive pump-and-dump losses for retail investors every week. 🔍 "
            "An AI fact-checking tool that instantly parses official DART regulatory filings, contract supply sizes, and convertible bond dilution risks in 3 seconds helps you separate real corporate value from hot air. "
            "Always verify official regulatory filings before jumping on rumor pumps. "
            "Search 'StockMaster AI' (or '스톡마스터 AI') on Google to get verified AI filing summaries."
        )
    },
    12: {
        "scenario_id": 12,
        "cluster": "korean_market",
        "theme_name": "외국인 투자자를 위한 KOSPI/KOSDAQ 완벽 공략 (Foreign Investor Guide to Korean Stocks)",
        "target_subreddits": ["koreanstocks", "Korea", "Living_in_Korea", "investing", "stocks"],
        "pain_points": "외국인이 한국 주식 시장(KOSPI/KOSDAQ)의 지배구조(재벌), 공매도 규정, 세금 규정을 이해하기 어려움",
        "solution_feature": "외국인 친화적 영문 코스피 퀀트 분석 및 한국 밸류업 프로그램 수혜주 스크리너",
        "stealth_cta": "Search 'StockMaster AI' (or '스톡마스터 AI') on Google to navigate Korean market equities with AI English analytics.",
        "sample_reply": (
            "Investing in the Korean stock market (KOSPI & KOSDAQ) as an international investor can be tricky due to chaebol governance structures and unique valuation metrics like the 'Korea Discount'. 🇰🇷 "
            "With the recent Corporate Value-Up Program targeting PBR < 1.0 companies with high shareholder return potential, AI quant screening has made finding top-tier Korean blue chips much easier. "
            "StockMaster AI provides clean English quant breakdowns of Korean market leaders and foreign capital flows. "
            "Search 'StockMaster AI' (or '스톡마스터 AI') on Google to explore Korean market investment opportunities!"
        )
    }
}
