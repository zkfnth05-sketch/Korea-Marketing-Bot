@echo off
chcp 65001 > nul
title StockMaster AI TikTok Login Helper
cd /d "%~dp0kmarket-marketing-engine"
python -u "%~dp0kmarket-marketing-engine\brands\stock\stock_tiktok_login.py"
pause
