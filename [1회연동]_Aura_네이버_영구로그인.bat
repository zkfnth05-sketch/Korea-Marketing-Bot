@echo off
chcp 65001 > nul
title 💖 Aura 데이팅 네이버 영구 로그인 1회 연동기
echo ========================================================
echo   💖 [Aura 데이팅] 네이버 영구 로그인 1회 연동기
echo   - [✓] 로그인 상태 유지(nvlong) 자동 체크 (영구 토큰 발급)
echo   - [✓] IP보안 해제(유동 IP 세션 파기 원천 차단)
echo   - 스마트폰 네이버 앱의 [QR코드] 또는 [아이디/비번] 1회 입력 시
echo     영구 저장되어 매일 재로그인이 불필요합니다.
echo ========================================================
cd /d "%~dp0kmarket-marketing-engine"
python -u "%~dp0kmarket-marketing-engine\brands\aura\aura_naver_login.py"
pause
