@echo off
chcp 65001 > nul
title 📈 Stock Master AI 주식 마케팅 봇 가동기
echo ========================================================
echo 📈 Stock Master AI 주식 24대 마케팅 파이프라인 가동
echo ========================================================
cd /d "%~dp0kmarket-marketing-engine"
python run_stock.py
pause
