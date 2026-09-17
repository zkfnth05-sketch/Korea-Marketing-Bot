@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
title Marketing Bot Dashboard - Port 8080

echo ========================================================
echo   [3-in-1 Marketing Bot] Dashboard Controller
echo   Aura Dating / InsureBalance / Stock Master AI
echo   Web Dashboard: http://localhost:8080
echo ========================================================
echo.

cd /d "%~dp0kmarket-marketing-engine"

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') do (
    taskkill /f /pid %%a >nul 2>&1
)

start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8080"

python server.py

pause
