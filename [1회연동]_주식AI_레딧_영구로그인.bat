@echo off
chcp 65001 > nul
title StockMaster AI Reddit Login
cd /d "%~dp0kmarket-marketing-engine"
python -u "%~dp0kmarket-marketing-engine\brands\stock\stock_reddit_login.py"
pause
