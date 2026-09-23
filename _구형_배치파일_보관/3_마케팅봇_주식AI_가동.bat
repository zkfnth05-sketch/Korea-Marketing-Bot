@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title 📈 Stock Master AI 주식 무인 마케팅 봇 가동기

cd /d "%~dp0kmarket-marketing-engine"

if not "%~1"=="" (
    python run_stock.py %*
    goto end
)

echo ========================================================
echo   📈 Stock Master AI 주식 24대 옴니채널 무인 마케팅 봇
echo ========================================================
echo.
echo   [1] 📈 주식 AI 전체 라이브 가동 (블로그+지식iN 100%% 실제 자동 발행) [기본값: Enter]
echo   [2] 🎯 주식 AI 지식iN 실시간 낚아채기 1회 즉시 실행 (--kin-now --live)
echo   [3] 🤖 주식 AI 지식iN 24시간 실시간 자율 감시 데몬 실행 (--kin-daemon)
echo   [4] 👑 [반도체 주도주] 1600x1600 실시간 캡처 칼럼 3대 채널 즉시 배포 (--semiconductor)
echo   [5] 🥇 [오늘 1위 주도주] 1600x1600 실시간 캡처 칼럼 3대 채널 즉시 배포 (--rank1)
echo   [6] 🧪 주식 AI 드라이런 안전 테스트 (시뮬레이션)
echo.
echo ========================================================
set "choice=1"
set /p "choice=👉 모드 번호를 입력하세요 [1-6, 기본값 1]: "

if "%choice%"=="1" (
    echo.
    echo 🚀 [라이브 가동] Stock Master AI 전체 마케팅 파이프라인 실제 발행을 시작합니다...
    python run_stock.py --live
    goto end
)

if "%choice%"=="2" (
    echo.
    echo 🎯 [지식iN 낚아채기] 주식 AI 네이버 지식iN 실시간 답변 작성을 시작합니다...
    python run_stock.py --kin-now --live
    goto end
)

if "%choice%"=="3" (
    echo.
    echo 🤖 [24시간 데몬] 주식 AI 지식iN 24시간 자율 감시 스케줄러를 가동합니다...
    python run_stock.py --kin-daemon
    goto end
)

if "%choice%"=="4" (
    echo.
    echo 👑 [반도체 주도주] 삼성전자/하이닉스 캡처 칼럼 즉시 발행을 시작합니다...
    python run_stock.py --semiconductor
    goto end
)

if "%choice%"=="5" (
    echo.
    echo 🥇 [1위 주도주] 퀀트 랭킹 1위 주도주 캡처 칼럼 즉시 발행을 시작합니다...
    python run_stock.py --rank1
    goto end
)

if "%choice%"=="6" (
    echo.
    echo 🧪 [드라이런] 발행 없이 주식 AI 전체 시스템 동작 시뮬레이션을 시작합니다...
    python run_stock.py
    goto end
)

echo 잘못된 입력입니다. 기본 라이브 모드로 실행합니다.
python run_stock.py --live

:end
echo.
echo ========================================================
echo 🏁 Stock Master AI 가동이 완료되었습니다.
echo ========================================================
pause
