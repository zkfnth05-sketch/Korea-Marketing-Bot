@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title 🛡️ InsureBalance 보험비교 무인 마케팅 봇 가동기

cd /d "%~dp0kmarket-marketing-engine"

if not "%~1"=="" (
    python run_insurance.py %*
    goto end
)

echo ========================================================
echo   🛡️ InsureBalance 보험비교 24대 옴니채널 무인 마케팅 봇
echo ========================================================
echo.
echo   [1] 🛡️ 보험비교 전체 라이브 가동 (블로그+지식iN 100%% 실제 자동 발행) [기본값: Enter]
echo   [2] 🎯 보험비교 지식iN 실시간 낚아채기 1회 즉시 실행 (--kin-now --live)
echo   [3] 🤖 보험비교 지식iN 24시간 실시간 자율 감시 데몬 실행 (--kin-daemon)
echo   [4] 📚 보험비교 2,000자 칼럼 즉시 생성 & 3대 채널 배포 (--blog-now)
echo   [5] 🧪 보험비교 드라이런 안전 테스트 (시뮬레이션)
echo.
echo ========================================================
set "choice=1"
set /p "choice=👉 모드 번호를 입력하세요 [1-5, 기본값 1]: "

if "%choice%"=="1" (
    echo.
    echo 🚀 [라이브 가동] InsureBalance 전체 마케팅 파이프라인 실제 발행을 시작합니다...
    python run_insurance.py --live
    goto end
)

if "%choice%"=="2" (
    echo.
    echo 🎯 [지식iN 낚아채기] InsureBalance 네이버 지식iN 실시간 답변 작성을 시작합니다...
    python run_insurance.py --kin-now --live
    goto end
)

if "%choice%"=="3" (
    echo.
    echo 🤖 [24시간 데몬] InsureBalance 지식iN 24시간 자율 감시 스케줄러를 가동합니다...
    python run_insurance.py --kin-daemon
    goto end
)

if "%choice%"=="4" (
    echo.
    echo 📚 [칼럼 배포] InsureBalance 2,000자 칼럼 생성 및 배포를 시작합니다...
    python run_insurance.py --blog-now
    goto end
)

if "%choice%"=="5" (
    echo.
    echo 🧪 [드라이런] 발행 없이 InsureBalance 전체 시스템 동작 시뮬레이션을 시작합니다...
    python run_insurance.py
    goto end
)

echo 잘못된 입력입니다. 기본 라이브 모드로 실행합니다.
python run_insurance.py --live

:end
echo.
echo ========================================================
echo 🏁 InsureBalance 가동이 완료되었습니다.
echo ========================================================
pause
