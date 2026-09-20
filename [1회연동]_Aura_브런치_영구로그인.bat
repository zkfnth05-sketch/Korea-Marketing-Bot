@echo off
chcp 65001 > nul
title Aura Dating Brunch Login
cd /d "%~dp0kmarket-marketing-engine"
python -u "%~dp0kmarket-marketing-engine\brands\aura\aura_brunch_login.py"
pause
