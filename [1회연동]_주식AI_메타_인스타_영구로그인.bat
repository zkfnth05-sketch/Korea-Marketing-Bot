@echo off
chcp 65001 > nul
title 📈 StockMaster AI 메타(인스타·페북) 영구 로그인 1회 연동기
echo ========================================================
echo   📈 [StockMaster AI] 메타(인스타·페북) 영구 로그인 1회 연동기
echo   - [✓] 정품 크롬 전용 프로필 모드 실행 (봇 탐지 0%)
echo   - [✓] 인스타그램 1회 로그인 완료 시 세션 영구 보존
echo ========================================================
cd /d "%~dp0kmarket-marketing-engine"
python -u "%~dp0kmarket-marketing-engine\brands\stock\stock_meta_login.py"
pause
