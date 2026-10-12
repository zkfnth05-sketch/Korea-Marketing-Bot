@echo off
chcp 65001 > nul
title [아우라 Aura] 6대 플랫폼 세션 생명 연장 즉시 실행
cd /d "%~dp0"
python brands\aura\aura_session_heartbeat_pipeline.py
pause
