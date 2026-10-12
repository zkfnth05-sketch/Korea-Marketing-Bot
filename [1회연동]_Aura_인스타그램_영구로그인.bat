@echo off
chcp 65001 > nul
title 💖 Aura AI 데이팅 인스타그램 영구 로그인 1회 연동기
echo ========================================================
echo   💖 Aura AI 데이팅 인스타그램 영구 로그인 1회 연동기
echo   - 대상 계정: @aura_ai_dating
echo   - 브라우저 창이 열리면 로그인 후 창을 닫아주세요.
echo ========================================================
cd /d "%~dp0kmarket-marketing-engine"
python -u "%~dp0kmarket-marketing-engine\brands\aura\aura_setup_instagram_profile.py"
pause
