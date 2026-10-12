@echo off
chcp 65001 > nul
cd /d "%~dp0kmarket-marketing-engine"
python -u core/engine/sync_all_profiles.py --brand aura
pause
