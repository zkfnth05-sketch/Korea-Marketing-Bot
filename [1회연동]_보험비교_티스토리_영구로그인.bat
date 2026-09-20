@echo off
chcp 65001 > nul
title InsureBalance Tistory Login
cd /d "%~dp0kmarket-marketing-engine"
python -u "%~dp0kmarket-marketing-engine\brands\insurance\insurance_tistory_login.py"
pause
