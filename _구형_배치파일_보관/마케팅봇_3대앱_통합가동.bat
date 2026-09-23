@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title 🏭 대한민국 3대 앱 무인 마케팅 공장 통합 가동기

cd /d "%~dp0kmarket-marketing-engine"

if not "%~1"=="" (
    python run_all_brands.py %*
    goto end
)

echo ========================================================
echo   🏭 대한민국 3대 앱 24대 허브 무인 마케팅 공장 통합 가동기
echo   [Aura 데이팅 · InsureBalance 보험비교 · Stock Master 주식 AI]
echo ========================================================
echo.
echo   [1] 🚀 3대 앱 전체 라이브 동시 가동 (블로그+지식iN 100%% 실제 자동 발행) [기본값: Enter]
echo   [2] 🧪 3대 앱 드라이런 안전 테스트 (게시 없이 전과정 무결성 시뮬레이션)
echo   [3] 🎯 지식iN 3대 앱 실시간 낚아채기 동시 실행 (지식iN 실제 답변 등록)
echo   [4] 🖥️ 3대 앱을 독립된 3개의 개별 콘솔 창으로 분리 가동
echo.
echo ========================================================
set "choice=1"
set /p "choice=👉 모드 번호를 입력하세요 [1-4, 기본값 1]: "

if "%choice%"=="1" (
    echo.
    echo 🚀 [라이브 가동] 3대 앱 전체 마케팅 파이프라인 실제 발행을 시작합니다...
    python run_all_brands.py --live
    goto end
)

if "%choice%"=="2" (
    echo.
    echo 🧪 [드라이런 테스트] 발행 없이 시스템 전체 동작 시뮬레이션을 시작합니다...
    python run_all_brands.py
    goto end
)

if "%choice%"=="3" (
    echo.
    echo 🎯 [지식iN 동시 낚아채기] 3대 앱 지식iN 실시간 등록을 시작합니다...
    python run_all_brands.py --kin-now --live
    goto end
)

if "%choice%"=="4" (
    echo.
    echo 🖥️ 3대 앱을 완전히 독립된 3개의 개별 CMD 프로세스로 분리 실행합니다...
    start "💖 Aura 데이팅 마케팅 봇" cmd /c "cd /d "%~dp0kmarket-marketing-engine" && python run_aura.py --live && pause"
    start "🛡️ InsureBalance 보험비교 마케팅 봇" cmd /c "cd /d "%~dp0kmarket-marketing-engine" && python run_insurance.py --live && pause"
    start "📈 Stock Master AI 주식 마케팅 봇" cmd /c "cd /d "%~dp0kmarket-marketing-engine" && python run_stock.py --live && pause"
    goto end
)

echo 잘못된 입력입니다. 기본 라이브 모드로 실행합니다.
python run_all_brands.py --live

:end
echo.
echo ========================================================
echo 🏁 가동이 완료되었습니다.
echo ========================================================
pause
