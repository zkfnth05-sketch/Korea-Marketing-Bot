@echo off
setlocal
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
title [3대 슈퍼앱 마케팅봇 대시보드]

echo ==============================================================================
echo   [3대 슈퍼앱 마케팅 사령부] 대시보드 및 서버 가동
echo   - 대상: Aura AI 데이팅 / InsureBalance 보험비교 / StockMaster 주식 AI
echo   - 대시보드 주소: http://localhost:8080
echo   - 잠시 후 기본 브라우저에서 대시보드가 자동으로 열립니다.
echo ==============================================================================
echo.

REM 1. 이전 잔여 8080 포트 프로세스 정리
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

REM 2. 작업 디렉터리 이동
cd /d "%~dp0kmarket-marketing-engine"

set "PY=python"
if exist "%~dp0venv\Scripts\python.exe" set "PY=%~dp0venv\Scripts\python.exe"
if exist "%~dp0kmarket-marketing-engine\venv\Scripts\python.exe" set "PY=%~dp0kmarket-marketing-engine\venv\Scripts\python.exe"

echo [안내] 관제 센터 서버를 기동합니다...
echo [안내] 대시보드를 계속 쓰시려면 이 콘솔 창을 닫지 마세요.
echo.

"%PY%" server.py

echo.
echo [안내] 서버가 종료되었습니다.
pause
