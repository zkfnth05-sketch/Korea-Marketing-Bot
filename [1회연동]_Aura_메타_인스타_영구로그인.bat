@echo off
chcp 65001 > nul
title 💖 Aura AI 데이팅 메타(페이스북/인스타) 영구 로그인 1회 연동기
echo ========================================================
echo   💖 Aura AI 데이팅 메타 비즈니스 스튜디오 영구 로그인 1회 연동기
echo   - 브라우저 창이 열리면 페이스북/인스타 로그인 후 창을 닫아주세요.
echo ========================================================
cd /d "%~dp0kmarket-marketing-engine"
python -u "%~dp0kmarket-marketing-engine\brands\aura\setup_meta_profile.py"
pause
