@echo off
chcp 65001 > nul
title Aura 데이팅 마케팅 봇 가동기
echo ========================================================
echo 💖 Aura 데이팅 24대 마케팅 파이프라인 가동
echo ========================================================
cd /d "%~dp0kmarket-marketing-engine"
python run_aura.py
pause
