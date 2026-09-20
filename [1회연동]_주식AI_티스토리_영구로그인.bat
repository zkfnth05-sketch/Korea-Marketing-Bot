@echo off
chcp 65001 > nul
title StockMaster Tistory Login
cd /d "%~dp0kmarket-marketing-engine"
python -u "%~dp0kmarket-marketing-engine\brands\stock\stock_tistory_login.py"
pause
