@echo off
setlocal
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
title [24시간 365일 3대 앱 무인 마케팅 마스터 데몬]

echo ==============================================================================
echo   [대한민국 3대 앱 마케팅봇 24시간 완전 자율 데몬]
echo   - 1. 💖 Aura AI 데이팅 (아우라AI데이팅)
echo   - 2. 🛡️ InsureBalance 보험비교 (보험 리밸런스)
echo   - 3. 📈 StockMaster AI (스톡마스터 AI)
echo.
echo   [핵심 운영 규칙]:
echo   • 🌙 새벽 00:00: GPU 안전 5분 쿨다운 15개 콘텐츠 순차 제작 (숏폼 9개 + 카드뉴스 6개)
echo   • ☀️ 아침 07:00: 저쪽 컴퓨터(KTRS)에 GPU 100%% 양보 (GPU 점유 0%%)
echo   • ⏰ 주간 5대 골든타임 정시 자율 송출 (08:30 / 12:30 / 15:30 / 18:30 / 21:00)
echo ==============================================================================
echo.

cd /d "%~dp0kmarket-marketing-engine"

set "PY=python"
if exist "%~dp0venv\Scripts\python.exe" set "PY=%~dp0venv\Scripts\python.exe"
if exist "%~dp0kmarket-marketing-engine\venv\Scripts\python.exe" set "PY=%~dp0kmarket-marketing-engine\venv\Scripts\python.exe"

echo [안내] 24시간 자율 마스터 데몬을 기동합니다...
echo.

"%PY%" korea_marketing_master_daemon.py

echo.
echo [안내] 데몬이 종료되었습니다.
pause
