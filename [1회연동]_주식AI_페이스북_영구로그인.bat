@echo off
chcp 65001 > nul
title 📈 StockMaster AI 페이스북 영구 로그인 1회 연동기
echo ========================================================
echo   📈 StockMaster AI 페이스북 영구 로그인 1회 연동기
echo   - 대상 페이지: 스톡마스터 AI
echo   - 브라우저 창이 열리면 로그인 후 창을 닫아주세요.
echo ========================================================
cd /d "%~dp0kmarket-marketing-engine"
python -u "%~dp0kmarket-marketing-engine\brands\stock\stock_setup_facebook_profile.py"
pause
