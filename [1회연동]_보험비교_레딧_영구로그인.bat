@echo off
chcp 65001 > nul
title InsureBalance Reddit Login
cd /d "%~dp0kmarket-marketing-engine"
python -u "%~dp0kmarket-marketing-engine\brands\insurance\insurance_reddit_login.py"
pause
