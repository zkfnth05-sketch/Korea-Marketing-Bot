@echo off
chcp 65001 > nul
title 🔍 3대 브랜드 네이버 영구 로그인 스마트 점검 및 연동기
echo ========================================================
echo   🔍 [한국 마케팅봇] 네이버 영구 로그인 스마트 점검 및 연동기
echo   - 💖 Aura 데이팅, 🛡️ 보험 리밸런스, 📈 StockMaster AI
echo   - 이미 로그인된 브랜드는 자동으로 건너뜁니다 (OK).
echo   - 로그인이 안 되었거나 만료된 브랜드만 화면에 띄웁니다.
echo ========================================================
cd /d "%~dp0kmarket-marketing-engine"
python -u "%~dp0kmarket-marketing-engine\core\engine\check_and_login_naver.py"
pause
