@echo off
chcp 65001 > nul
title InsureBalance Brunch Login
cd /d "%~dp0kmarket-marketing-engine"
python -u "%~dp0kmarket-marketing-engine\brands\insurance\insurance_brunch_login.py"
pause
