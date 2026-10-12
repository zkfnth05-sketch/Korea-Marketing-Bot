@echo off
chcp 65001 > nul
title 🛡️ 보험 리밸런스 페이스북 영구 로그인 1회 연동기
echo ========================================================
echo   🛡️ 보험 리밸런스 페이스북 영구 로그인 1회 연동기
echo   - 대상 페이지: Goldmom
echo   - 브라우저 창이 열리면 로그인 후 창을 닫아주세요.
echo ========================================================
cd /d "%~dp0kmarket-marketing-engine"
python -u "%~dp0kmarket-marketing-engine\brands\insurance\insurance_setup_facebook_profile.py"
pause
