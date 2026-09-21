@echo off
chcp 65001 > nul
title Aura Dating Naver Login
cd /d "%~dp0kmarket-marketing-engine"
python -u "%~dp0kmarket-marketing-engine\brands\aura\aura_naver_login.py"
pause
