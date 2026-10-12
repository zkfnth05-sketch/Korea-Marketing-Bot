@echo off
chcp 65001 > nul
title [보험 리밸런스] 6대 플랫폼 세션 생명 연장 즉시 실행
cd /d "%~dp0"
python brands\insurance\insurance_session_heartbeat_pipeline.py
pause
