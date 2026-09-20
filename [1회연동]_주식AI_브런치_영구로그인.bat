@echo off
chcp 65001 > nul
title StockMaster Brunch Login
cd /d "%~dp0kmarket-marketing-engine"
python -u "%~dp0kmarket-marketing-engine\brands\stock\stock_brunch_login.py"
pause
