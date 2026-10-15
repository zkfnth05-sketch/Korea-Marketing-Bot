@echo off
chcp 65001 >nul
title 서버 자동시작 해제

echo.
echo ================================================================
echo  [한국 마케팅봇] server.py Windows 자동시작 완전 해제
echo  PC 재부팅 시 서버가 자동으로 실행되지 않도록 설정합니다.
echo ================================================================
echo.

REM 1. Windows Startup 폴더 VBS 파일 삭제
set "STARTUP_VBS=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\kmarket_marketing_bot_autostart.vbs"
if exist "%STARTUP_VBS%" (
    del /f /q "%STARTUP_VBS%" >nul 2>&1
    echo [1/3] 시작프로그램(Startup) VBS 파일 삭제 완료!
) else (
    echo [1/3] 시작프로그램(Startup) VBS 파일이 이미 없습니다.
)

REM 2. 작업 스케줄러(schtasks) 등록 해제
schtasks /delete /tn "한국마케팅봇_서버_자동시작" /f >nul 2>&1
echo [2/3] 작업 스케줄러 등록 해제 완료!

REM 3. 레지스트리 자동실행 항목 삭제
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "한국마케팅봇서버" /f >nul 2>&1
echo [3/3] 레지스트리 자동실행 항목 삭제 완료!

echo.
echo ================================================================
echo  [완료] 이제 PC를 켜도 서버가 자동으로 시작되지 않습니다.
echo  대시보드를 쓰실 때는 '0_마케팅봇_대시보드_실행.bat'을 실행하세요.
echo ================================================================
pause
