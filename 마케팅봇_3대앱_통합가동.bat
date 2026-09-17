@echo off
chcp 65001 > nul
title 대한민국 3대 앱 무인 마케팅 공장 통합 가동기
echo ========================================================
echo 🏭 대한민국 3대 앱 (데이팅 · 보험 · 주식) 24대 허브 전체 가동
echo ========================================================
cd /d "%~dp0kmarket-marketing-engine"
python run_all_brands.py
pause
