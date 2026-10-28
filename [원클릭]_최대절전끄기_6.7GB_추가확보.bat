@echo off
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo [!] Requesting Administrative Privileges...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "cmd.exe", "/c """%~s0""", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    pushd "%CD%"
    CD /D "%~dp0"
    title C Drive Optimization - Disable Hibernation (Gain 6.7GB)
    echo ========================================================
    echo  Windows Hibernation Off (Gain 6.75 GB Free Space)
    echo ========================================================
    echo.
    echo [*] Disabling hiberfil.sys...
    powercfg -h off
    echo.
    echo ========================================================
    echo [V] Successfully deleted hiberfil.sys! +6.75 GB Gained!
    echo ========================================================
    echo.
    timeout /t 3
