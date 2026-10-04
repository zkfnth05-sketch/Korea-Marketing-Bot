@echo off
chcp 65001 > nul
title 📈 StockMaster AI 주식 유튜브 영구 로그인 1회 연동기
echo ========================================================
echo   📈 [StockMaster AI] 유튜브 스튜디오 영구 로그인 1회 연동기
echo   - 대상 계정: 주식AI 전용 구글 계정
echo   - 브라우저 창이 열리면 로그인 완료 후 창을 닫아주세요.
echo ========================================================
cd /d "%~dp0kmarket-marketing-engine"
python -u "%~dp0kmarket-marketing-engine\brands\stock\setup_youtube_profile.py"
pause
