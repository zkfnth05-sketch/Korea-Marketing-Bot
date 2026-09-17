@echo off
chcp 65001 > nul
title InsureBalance 보험비교 마케팅 봇 가동기
echo ========================================================
echo 🛡️ InsureBalance 보험 비교 24대 마케팅 파이프라인 가동
echo ========================================================
cd /d "%~dp0kmarket-marketing-engine"
python run_insurance.py
pause
