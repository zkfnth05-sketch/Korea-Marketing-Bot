@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
title 3대 슈퍼앱 마케팅 사령부 대시보드

echo ==============================================================================
echo   [3대 슈퍼앱 마케팅 사령부] 24시간 무인 관제 센터
echo   - 브랜드: Aura 데이팅  ·  InsureBalance 보험비교  ·  Stock Master 주식 AI
echo   - 웹 대시보드 주소: http://localhost:8080
echo   - 🌟 [일체형 탑재] 3대 브랜드 × 6대 플랫폼 3시간 스텔스 세션 생명 연장 자동 가동
echo ==============================================================================
echo.

cd /d "%~dp0kmarket-marketing-engine"

python server.py

pause
