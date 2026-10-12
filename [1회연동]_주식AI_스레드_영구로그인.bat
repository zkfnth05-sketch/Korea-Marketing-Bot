@echo off
chcp 65001 > nul
title [StockMaster AI] Threads Login
echo ========================================================
echo   [StockMaster AI] 스레드(Threads) 1회 영구 로그인 연동기
echo   - 계정: @stockmaster_ai
echo   - 1. 화면에 전용 브라우저 창이 열립니다.
echo   - 2. 인스타그램 / 스레드에 로그인해 주세요.
echo   - 3. 메인 피드가 뜨거나 창을 닫으면 자동 감지되어 영구 저장됩니다.
echo ========================================================
cd /d "%~dp0kmarket-marketing-engine"
python -u "%~dp0kmarket-marketing-engine\brands\stock\stock_threads_login.py"
pause
