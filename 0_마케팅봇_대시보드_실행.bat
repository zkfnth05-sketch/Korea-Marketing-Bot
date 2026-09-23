@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
title 🛸 대한민국 3대 슈퍼앱 24시간 무인 마케팅 컨트롤 센터

echo ========================================================
echo   🛸 대한민국 3대 슈퍼앱 24시간 무인 마케팅 컨트롤 센터
echo   💖 Aura 데이팅  ·  🛡️ InsureBalance 보험비교  ·  📈 Stock Master 주식 AI
echo   🌐 웹 대시보드 관제 센터: http://localhost:8080
echo ========================================================
echo.
echo   🚀 서버 시작 시 3대 앱의 24시간 무인 오토파일럿이 자동 점화됩니다.
echo   - 💖 Aura 데이팅: 2,000자 칼럼 자동 발행 + 지식iN 24시간 레이더 (10건 목표)
echo   - 🛡️ 보험비교: 2,000자 칼럼 자동 발행 + 지식iN 24시간 레이더 (10건 목표)
echo   - 📈 주식 AI: 실시간 캡처 칼럼 자동 발행 + 지식iN 24시간 레이더 (10건 목표)
echo   - 🌐 포털 색인: 신규 글 등록 즉시 구글·네이버 실시간 색인 핑 전송
echo.

cd /d "%~dp0kmarket-marketing-engine"

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') do (
    taskkill /f /pid %%a >nul 2>&1
)

start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8080"

python server.py

pause
