@echo off
chcp 65001 > nul
title InsureBalance Naver Login
cd /d "%~dp0kmarket-marketing-engine"
python -u "%~dp0kmarket-marketing-engine\brands\insurance\insurance_naver_login.py"
pause
