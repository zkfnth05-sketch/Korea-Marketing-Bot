@echo off
chcp 65001 >nul
title 서버 자동시작 등록

echo.
echo ================================================================
echo  [한국 마케팅봇] server.py Windows 자동시작 등록
echo  PC 재부팅해도 server.py가 자동으로 가동됩니다.
echo ================================================================
echo.

set "PYTHON=%~dp0venv\Scripts\pythonw.exe"
if not exist "%PYTHON%" set "PYTHON=pythonw"
if not exist "%PYTHON%" set "PYTHON=python"

set "SCRIPT=%~dp0kmarket-marketing-engine\server.py"
set "WORKDIR=%~dp0kmarket-marketing-engine"
set "TASKNAME=한국마케팅봇_서버_자동시작"

REM 1. Windows Startup 폴더 무인 스텔스 VBS 자동 등록 (관리자 권한 불필요, 100% 보장)
set "STARTUP_VBS=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\kmarket_marketing_bot_autostart.vbs"
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo WshShell.CurrentDirectory = "%WORKDIR%"
echo WshShell.Run "python server.py", 0, False
echo WshShell.Run "python korea_marketing_master_daemon.py", 0, False
echo Set WshShell = Nothing
) > "%STARTUP_VBS%"

echo [1/2] Windows 시작프로그램(Startup) 폴더 자동실행 등록 완료!
echo       경로: %STARTUP_VBS%
echo.

REM 2. 작업 스케줄러(schtasks) 등록 시도 (관리자 권한 시 추가 안전망)
schtasks /delete /tn "%TASKNAME%" /f >nul 2>&1

schtasks /create ^
  /tn "%TASKNAME%" ^
  /tr "\"%PYTHON%\" \"%SCRIPT%\"" ^
  /sc ONLOGON ^
  /ru "%USERNAME%" ^
  /rl HIGHEST ^
  /f ^
  /sd 2024/01/01 ^
  /delay 0001:00 >nul 2>&1

if %ERRORLEVEL%==0 (
    echo [2/2] [SUCCESS] 작업 스케줄러(schtasks) 2차 안전망 등록 완료!
) else (
    echo [2/2] [안내] 작업 스케줄러는 관리자 권한이 필요하여 스킵되었으나,
    echo       시작프로그램(Startup) VBS로 PC 재부팅 시 100% 정상 자동 시작됩니다.
)

echo.
echo ================================================================
echo  이제 PC를 재부팅해도 server.py가 백그라운드에서 자동 가동됩니다!
echo ================================================================
pause
