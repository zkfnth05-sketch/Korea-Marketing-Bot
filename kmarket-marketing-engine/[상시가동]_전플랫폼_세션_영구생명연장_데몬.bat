@echo off
chcp 65001 > nul
title [전체 3개 앱] 5대 SNS + 블로그 365일 무인 영구 생명 연장 상시 데몬
cd /d "%~dp0"

echo ==============================================================================
echo  🌟 [한국 마케팅봇] 전 플랫폼 3시간 스텔스 세션 생명 연장 상시 데몬
echo ==============================================================================
echo  - 대상: 3개 브랜드 (보험, 주식, 아우라) × 6대 플랫폼
echo  - 채널: YouTube Shorts, Meta MBS Reels, TikTok, Naver Clip, Threads, Tistory
echo  - 주기: 3시간마다 백그라운드 스텔스 핑 전송 (토큰 수명 365일 무한 갱신)
echo  - 효과: 유휴(Inactivity) 만료 원천 차단으로 세션 절대 풀림 방지
echo ==============================================================================
echo.
python core\auto_publishers\omni_session_heartbeat_keeper.py --daemon
pause
