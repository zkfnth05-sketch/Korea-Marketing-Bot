@echo off
chcp 65001 > nul
title [주식 AI StockMaster] 6대 플랫폼 세션 생명 연장 즉시 실행
cd /d "%~dp0"
python brands\stock\stock_session_heartbeat_pipeline.py
pause
