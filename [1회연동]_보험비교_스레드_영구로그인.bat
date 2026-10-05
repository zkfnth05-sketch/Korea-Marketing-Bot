@echo off
chcp 65001 > nul
cd /d "%~dp0kmarket-marketing-engine"
python -u "%~dp0kmarket-marketing-engine\brands\insurance\insurance_threads_login.py"
pause
