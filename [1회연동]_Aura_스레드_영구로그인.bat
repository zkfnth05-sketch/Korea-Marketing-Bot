@echo off
chcp 65001 > nul
title 💖 [Aura AI 데이팅] 스레드(Threads) 영구 로그인 1회 연동기
echo ========================================================
echo   💖 [Aura 데이팅] 스레드(Threads) 영구 로그인 1회 연동기
echo   - 계정: @aura_ai_dating
echo   - 1. 화면에 전용 브라우저 창이 열립니다.
echo   - 2. 스레드(threads.net)에 로그인해 주세요.
echo   - 3. 메인 피드가 뜨면 봇이 자동 감지하여 영구 저장 후 창을 닫습니다.
echo ========================================================
cd /d "%~dp0kmarket-marketing-engine"
python -u "%~dp0kmarket-marketing-engine\brands\aura\aura_threads_login.py"
pause
