@echo off
chcp 65001 > nul
title [검증] 네이버 지식iN 3대 브랜드 실제 답변 브라우저 확인
echo.
echo ======================================================================
echo 🔍 [지식iN 3대 브랜드 실물 답변 모니터 실시간 확인 모드]
echo   - 💖 Aura AI 데이팅
echo   - 🛡️ InsureBalance 보험비교
echo   - 📈 StockMaster 주식AI
echo.
echo 🖥️ 실제 크롬 브라우저 창이 화면에 열리고,
echo    각 질문의 우리 봇 답변 위치로 자동 스크롤되어 하이라이트됩니다!
echo ======================================================================
echo.

python -u "%~dp0kmarket-marketing-engine\modules\domestic\kin_visual_verifier.py" --gui

echo.
echo ======================================================================
echo 📸 캡처된 고화질 증빙 이미지는 아래 폴더에 저장되었습니다:
echo    kmarket-marketing-engine\outputs\proofs\
echo ======================================================================
echo.
pause
