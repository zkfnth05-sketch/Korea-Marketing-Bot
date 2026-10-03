@echo off
chcp 65001 > nul
cd /d "%~dp0"
title [💖 Aura AI 데이팅] 스레드(Threads) 1회 영구 로그인 연동기
echo ======================================================================
echo 🔑 [💖 Aura AI 데이팅] 스레드(Threads) 영구 로그인 1회 연동기
echo ======================================================================
echo.
echo * 전용 브라우저 창이 열리면 @aura_ai_dating 계정으로 스레드에 로그인해 주세요.
echo * 로그인이 완료되면 봇이 자동으로 감지하여 영구 저장 후 창을 닫습니다.
echo.
python brands\aura\aura_threads_login.py
pause
