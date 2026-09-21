@echo off
chcp 65001 > nul
title StockMaster AI Naver Login
cd /d "%~dp0kmarket-marketing-engine"
python -u "%~dp0kmarket-marketing-engine\brands\stock\stock_naver_login.py"
pause
