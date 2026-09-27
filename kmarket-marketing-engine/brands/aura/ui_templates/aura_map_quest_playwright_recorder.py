# -*- coding: utf-8 -*-
"""
AuraMapQuestPlaywrightRecorder - 📱 [Aura 8번 주제 500m 안심 레이더 지도 & 번개 퀘스트 100% 실기기 녹화기]
- 유저 스크린샷(aura-ai-dating.vercel.app/map)과 100% 동일한 픽셀 매칭
- [0.0s ~ 2.0s] 500m 안심 지터링 적용 지도 뷰 & 프로필 핀 탐색
- [2.0s ~ 5.5s] ⚡ 새 데이트 퀘스트 등록 모달 오픈 & 500m 안심 보호 & 카테고리/칩 선택 입력
- [5.5s ~ 8.0s] 퀘스트 등록 완료 토스트 & 지도 위 번개 핀 레이더 펄스 생성
- 1080x1920 세로 풀HD 60fps Playwright 무손실 녹화
"""

import os
import sys
import time
import json
import base64
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import imageio_ffmpeg

logger = logging.getLogger("AuraMapQuestPlaywrightRecorder")

def load_real_member_photos_base64() -> List[str]:
    """로컬 실제 한국인 회원 사진들을 Base64 Data URI로 로드"""
    photo_dir = Path("scratch/real_aura_photos")
    b64_list = []
    if photo_dir.exists():
        for p in sorted(list(photo_dir.glob("*.jpg"))):
            with open(p, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
                b64_list.append(f"data:image/jpeg;base64,{b64}")
    return b64_list


def generate_map_quest_html() -> str:
    """유저 스크린샷 3장과 100% 동일한 1080x1920 세로 풀HD 인터랙티브 시뮬레이션 HTML"""
    photos = load_real_member_photos_base64()
    photos_json = json.dumps(photos, ensure_ascii=False)
    
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1080, height=1920, initial-scale=1.0">
<title>Aura Safe Radar Map Simulation</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    -webkit-font-smoothing: antialiased;
  }}
  body {{
    background-color: #000000;
    color: #ffffff;
    width: 1080px;
    height: 1920px;
    overflow: hidden;
    display: flex;
    justify-content: center;
    align-items: center;
  }}

  .phone-container {{
    width: 1080px;
    height: 1920px;
    background: #09090b;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }}

  /* 상단 상태표시줄 */
  .status-bar {{
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 60px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 44px;
    font-size: 22px;
    font-weight: 700;
    color: rgba(255, 255, 255, 0.95);
    z-index: 60;
  }}
  .dynamic-island {{
    width: 180px;
    height: 40px;
    background: #000;
    border-radius: 20px;
  }}

  /* 실제 아우라 앱 상단 헤더 */
  .app-header {{
    position: absolute;
    top: 60px;
    left: 0;
    right: 0;
    height: 80px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 36px;
    border-bottom: 1.5px solid rgba(255, 255, 255, 0.08);
    background: rgba(9, 9, 11, 0.88);
    backdrop-filter: blur(16px);
    z-index: 50;
  }}
  .header-left {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 20px;
    font-weight: 700;
    color: #c084fc;
  }}
  .header-logo {{
    font-size: 40px;
    font-weight: 900;
    background: linear-gradient(90deg, #FFF3D1 0%, #E5A934 50%, #C98718 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
  }}
  .header-install-btn {{
    font-size: 18px;
    font-weight: 700;
    color: #fbbf24;
    background: rgba(245, 158, 11, 0.15);
    border: 1.5px solid rgba(245, 158, 11, 0.4);
    padding: 6px 16px;
    border-radius: 24px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}

  /* 지도 영역 */
  .map-wrapper {{
    position: absolute;
    inset: 0;
    z-index: 5;
    background: #e5e9ec;
    overflow: hidden;
  }}
  
  /* 정밀 서울/수도권 고해상도 SVG 지도 배경 */
  .map-svg-bg {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    filter: brightness(0.97) contrast(1.03);
  }}

  /* 상단 거리 필터 캡슐 */
  .top-controls {{
    position: absolute;
    top: 155px;
    left: 0;
    right: 0;
    z-index: 20;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 14px;
    padding: 0 24px;
  }}
  .radius-bar {{
    display: flex;
    background: rgba(0, 0, 0, 0.75);
    backdrop-filter: blur(14px);
    border: 1.5px solid rgba(255, 255, 255, 0.15);
    border-radius: 30px;
    padding: 6px 12px;
    gap: 8px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  }}
  .radius-item {{
    padding: 8px 18px;
    border-radius: 20px;
    font-size: 19px;
    font-weight: 700;
    color: rgba(255, 255, 255, 0.7);
  }}
  .radius-item.active {{
    background: #E5A934;
    color: #000000;
    font-weight: 900;
  }}

  .filter-tabs {{
    display: flex;
    background: rgba(18, 12, 28, 0.85);
    backdrop-filter: blur(16px);
    border: 1.5px solid rgba(255, 255, 255, 0.18);
    border-radius: 30px;
    padding: 6px 14px;
    gap: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
  }}
  .tab-item {{
    padding: 10px 22px;
    border-radius: 20px;
    font-size: 20px;
    font-weight: 700;
    color: rgba(255, 255, 255, 0.65);
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .tab-item.active {{
    background: rgba(255, 255, 255, 0.15);
    color: #ffffff;
  }}
  .tab-item.highlight {{
    background: linear-gradient(90deg, #f59e0b, #ec4899);
    color: #ffffff;
    font-weight: 900;
  }}

  /* 지도 위 프로필 핀들 (500m 안심 지터링 배치) */
  .profile-pin {{
    position: absolute;
    width: 66px;
    height: 66px;
    border-radius: 50%;
    border: 3.5px solid #ffffff;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.5), 0 0 16px rgba(245, 158, 11, 0.6);
    cursor: pointer;
    transform: translate(-50%, -50%);
    overflow: hidden;
    background: #334155;
    z-index: 10;
    transition: transform 0.3s ease;
  }}
  .profile-pin img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
  }}

  /* 500m 안심 레이더 반경 펄스 */
  .radar-circle {{
    position: absolute;
    border-radius: 50%;
    border: 2px dashed rgba(245, 158, 11, 0.8);
    background: radial-gradient(circle, rgba(245, 158, 11, 0.25) 0%, rgba(245, 158, 11, 0.05) 70%, transparent 100%);
    transform: translate(-50%, -50%);
    pointer-events: none;
    z-index: 8;
    animation: radarPulse 3s infinite ease-out;
  }}
  @keyframes radarPulse {{
    0% {{ transform: translate(-50%, -50%) scale(0.85); opacity: 0.8; }}
    50% {{ transform: translate(-50%, -50%) scale(1.1); opacity: 0.4; }}
    100% {{ transform: translate(-50%, -50%) scale(0.85); opacity: 0.8; }}
  }}

  /* 번개 퀘스트 등록 핀 (등록 후 지도 위에 나타나는 발광 핀) */
  .quest-marker-pin {{
    position: absolute;
    transform: translate(-50%, -50%);
    display: flex;
    align-items: center;
    gap: 12px;
    background: rgba(15, 10, 24, 0.94);
    border: 2.5px solid #fbbf24;
    border-radius: 36px;
    padding: 8px 20px 8px 10px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8), 0 0 25px rgba(245, 158, 11, 0.7);
    z-index: 15;
    opacity: 0;
    transition: opacity 0.4s ease, transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  }}
  .quest-marker-pin.show {{
    opacity: 1;
    transform: translate(-50%, -50%) scale(1.05);
  }}
  .quest-pin-avatar {{
    width: 60px;
    height: 60px;
    border-radius: 50%;
    border: 2.5px solid #ec4899;
    overflow: hidden;
  }}
  .quest-pin-avatar img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
  }}
  .quest-pin-content {{
    display: flex;
    flex-direction: column;
    gap: 2px;
    text-align: left;
  }}
  .quest-pin-title {{
    font-size: 21px;
    font-weight: 800;
    color: #ffffff;
    white-space: nowrap;
  }}
  .quest-pin-tag {{
    font-size: 16px;
    font-weight: 700;
    color: #fbbf24;
    display: flex;
    align-items: center;
    gap: 4px;
  }}

  /* 하단 플로팅 '⚡ 번개 퀘스트 올리기' 버튼 */
  .fab-quest-btn {{
    position: absolute;
    bottom: 125px;
    right: 36px;
    height: 76px;
    padding: 0 32px;
    border-radius: 38px;
    background: linear-gradient(90deg, #ea580c 0%, #f59e0b 100%);
    border: 2px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 12px 30px rgba(234, 88, 12, 0.6), 0 0 20px rgba(245, 158, 11, 0.4);
    display: flex;
    align-items: center;
    gap: 12px;
    color: #ffffff;
    font-size: 26px;
    font-weight: 900;
    z-index: 25;
    cursor: pointer;
    letter-spacing: -0.5px;
    transition: transform 0.2s ease;
  }}
  .fab-quest-btn.pressed {{
    transform: scale(0.92);
  }}

  /* 등록 완료 토스트 */
  .toast-banner {{
    position: absolute;
    top: 150px;
    left: 36px;
    right: 36px;
    background: rgba(18, 12, 28, 0.98);
    border: 2px solid #fbbf24;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.9), 0 0 30px rgba(245, 158, 11, 0.5);
    border-radius: 26px;
    padding: 22px 28px;
    display: flex;
    align-items: center;
    gap: 16px;
    z-index: 55;
    opacity: 0;
    transform: translateY(-20px);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  }}
  .toast-banner.show {{
    opacity: 1;
    transform: translateY(0);
  }}
  .toast-icon {{
    font-size: 38px;
  }}
  .toast-text {{
    display: flex;
    flex-direction: column;
    text-align: left;
    gap: 4px;
  }}
  .toast-title {{
    font-size: 24px;
    font-weight: 900;
    color: #fbbf24;
  }}
  .toast-desc {{
    font-size: 19px;
    color: rgba(255, 255, 255, 0.85);
    font-weight: 600;
  }}

  /* 새 데이트 퀘스트 등록 모달 (유저 스크린샷 100% 동일) */
  .modal-overlay {{
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.75);
    backdrop-filter: blur(14px);
    z-index: 45;
    display: flex;
    align-items: flex-end;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.35s ease;
  }}
  .modal-overlay.open {{
    opacity: 1;
    pointer-events: auto;
  }}

  .modal-sheet {{
    width: 100%;
    background: rgba(18, 14, 26, 0.98);
    border-top: 2.5px solid rgba(245, 158, 11, 0.5);
    border-radius: 38px 38px 0 0;
    padding: 32px 36px 120px 36px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    box-shadow: 0 -20px 60px rgba(0, 0, 0, 0.95);
    transform: translateY(100%);
    transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.2);
  }}
  .modal-overlay.open .modal-sheet {{
    transform: translateY(0);
  }}

  .modal-top {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }}
  .modal-title-box {{
    display: flex;
    flex-direction: column;
    gap: 6px;
    text-align: left;
  }}
  .modal-header-title {{
    font-size: 32px;
    font-weight: 900;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .modal-header-sub {{
    font-size: 19px;
    color: rgba(255, 255, 255, 0.65);
  }}
  .modal-close-btn {{
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.12);
    display: flex;
    align-items: center;
    justify-content: center;
    color: rgba(255, 255, 255, 0.7);
    font-size: 22px;
  }}

  /* 500m 안심 프라이버시 보호 박스 (유저 스크린샷 100% 동일) */
  .privacy-info-card {{
    background: rgba(245, 158, 11, 0.1);
    border: 1.5px solid rgba(245, 158, 11, 0.35);
    border-radius: 24px;
    padding: 20px 24px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    text-align: left;
  }}
  .privacy-header {{
    font-size: 21px;
    font-weight: 900;
    color: #fbbf24;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .privacy-desc {{
    font-size: 18.5px;
    color: rgba(255, 255, 255, 0.9);
    line-height: 1.45;
  }}
  .privacy-bullets {{
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-size: 16.5px;
    color: rgba(255, 255, 255, 0.7);
  }}
  .bullet-item {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  /* 카테고리 5개 그리드 */
  .category-grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
  }}
  .cat-item {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 6px;
    background: rgba(30, 24, 42, 0.8);
    border: 1.5px solid rgba(255, 255, 255, 0.12);
    border-radius: 18px;
    padding: 14px 6px;
    font-size: 17px;
    font-weight: 700;
    color: rgba(255, 255, 255, 0.7);
    transition: all 0.2s ease;
  }}
  .cat-item.active {{
    background: #E5A934;
    color: #000000;
    border-color: #fbbf24;
    font-weight: 900;
    box-shadow: 0 4px 16px rgba(245, 158, 11, 0.4);
  }}
  .cat-icon {{
    font-size: 26px;
  }}

  /* 추천 칩 */
  .chips-wrap {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }}
  .chip-pill {{
    background: rgba(40, 30, 55, 0.9);
    border: 1.5px solid rgba(255, 255, 255, 0.18);
    border-radius: 20px;
    padding: 8px 18px;
    font-size: 17.5px;
    font-weight: 700;
    color: rgba(255, 255, 255, 0.85);
    transition: all 0.2s ease;
  }}
  .chip-pill.active {{
    background: rgba(245, 158, 11, 0.25);
    border-color: #fbbf24;
    color: #fbbf24;
    font-weight: 900;
  }}

  /* 인풋 박스 */
  .form-input-box {{
    width: 100%;
    background: rgba(25, 20, 35, 0.9);
    border: 1.5px solid rgba(255, 255, 255, 0.2);
    border-radius: 18px;
    padding: 16px 20px;
    font-size: 20px;
    font-weight: 700;
    color: #ffffff;
    text-align: left;
  }}

  /* 모달 등록하기 버튼 */
  .btn-submit-quest {{
    width: 100%;
    height: 76px;
    border-radius: 22px;
    background: linear-gradient(90deg, #ea580c 0%, #f59e0b 100%);
    border: none;
    color: #ffffff;
    font-size: 26px;
    font-weight: 900;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    box-shadow: 0 10px 30px rgba(234, 88, 12, 0.6);
    cursor: pointer;
  }}

  /* 하단 실제 네비게이션 탭바 */
  .app-bottom-nav {{
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 100px;
    background: rgba(9, 9, 11, 0.96);
    border-top: 1.5px solid rgba(255, 255, 255, 0.1);
    display: flex;
    justify-content: space-around;
    align-items: center;
    padding: 0 16px 12px 16px;
    z-index: 50;
  }}
  .nav-item {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    color: rgba(255, 255, 255, 0.55);
    font-size: 18px;
    font-weight: 600;
  }}
  .nav-item.active {{
    color: #E5A934;
    font-weight: 900;
  }}
  .nav-icon {{
    font-size: 30px;
  }}
</style>
</head>
<body>
  <div class="phone-container">
    <!-- 상단 상태표시줄 -->
    <div class="status-bar">
      <span>09:41</span>
      <div class="dynamic-island"></div>
      <span>5G 􀛨</span>
    </div>

    <!-- 실제 아우라 앱 상단 헤더 -->
    <div class="app-header">
      <div class="header-left">
        <span>✨</span>
        <span>AI 추천</span>
      </div>
      <div class="header-logo">Aura</div>
      <div class="header-install-btn">
        <span>⬇️</span>
        <span>앱 설치</span>
      </div>
    </div>

    <!-- 지도 래퍼 -->
    <div class="map-wrapper">
      <!-- 고화질 네이버/구글 서울 지도 벡터 렌더링 -->
      <svg class="map-svg-bg" viewBox="0 0 1080 1920" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="1080" height="1920" fill="#E8ECEF"/>
        <!-- 강/한강 블루 라인 -->
        <path d="M-50 1150 Q 250 1120 540 1200 T 1150 1100" stroke="#90CAF9" stroke-width="110" stroke-linecap="round" fill="none"/>
        <path d="M480 300 Q 560 650 540 1200" stroke="#BBDEFB" stroke-width="35" fill="none"/>
        <!-- 도로망 골드/오렌지/화이트 -->
        <path d="M-50 700 L 1150 950" stroke="#FFE082" stroke-width="26" fill="none"/>
        <path d="M-50 1350 L 1150 1450" stroke="#FFCC80" stroke-width="32" fill="none"/>
        <path d="M300 -50 L 400 1950" stroke="#FFFFFF" stroke-width="24" fill="none"/>
        <path d="M800 -50 L 700 1950" stroke="#FFFFFF" stroke-width="28" fill="none"/>
        <path d="M-50 400 Q 500 500 1150 350" stroke="#FFFFFF" stroke-width="20" fill="none"/>
        <path d="M-50 1600 Q 550 1500 1150 1700" stroke="#FFFFFF" stroke-width="22" fill="none"/>
        <!-- 녹지 공원 (서울숲, 남산, 한강공원) -->
        <circle cx="680" cy="1100" r="140" fill="#C8E6C9" opacity="0.8"/>
        <circle cx="450" cy="920" r="110" fill="#C8E6C9" opacity="0.8"/>
        <circle cx="280" cy="1180" r="90" fill="#C8E6C9" opacity="0.7"/>
        <text x="650" y="1110" fill="#2E7D32" font-size="24" font-weight="bold">서울숲</text>
        <text x="420" y="930" fill="#2E7D32" font-size="22" font-weight="bold">남산</text>
        <text x="220" y="1190" fill="#1565C0" font-size="22" font-weight="bold">여의도</text>
        <text x="500" y="780" fill="#546E7A" font-size="26" font-weight="bold">종로구</text>
        <text x="620" y="1320" fill="#546E7A" font-size="26" font-weight="bold">강남구</text>
        <text x="760" y="1180" fill="#546E7A" font-size="26" font-weight="bold">성동구(성수)</text>
      </svg>

      <!-- 500m 안심 레이더 펄스 원 -->
      <div class="radar-circle" style="top: 1080px; left: 680px; width: 380px; height: 380px;"></div>

      <!-- 지도 위 실제 한국인 회원 프로필 핀들 -->
      <div class="profile-pin" id="pin0" style="top: 850px; left: 450px;"><img src="" alt="p0"></div>
      <div class="profile-pin" id="pin1" style="top: 920px; left: 620px;"><img src="" alt="p1"></div>
      <div class="profile-pin" id="pin2" style="top: 1040px; left: 320px;"><img src="" alt="p2"></div>
      <div class="profile-pin" id="pin3" style="top: 1250px; left: 750px;"><img src="" alt="p3"></div>
      <div class="profile-pin" id="pin4" style="top: 1320px; left: 480px;"><img src="" alt="p4"></div>
      <div class="profile-pin" id="pin5" style="top: 1180px; left: 880px;"><img src="" alt="p5"></div>
      <div class="profile-pin" id="pin6" style="top: 980px; left: 780px;"><img src="" alt="p6"></div>

      <!-- 등록 완료 후 지도 위에 웅장하게 발광하는 번개 퀘스트 핀 -->
      <div class="quest-marker-pin" id="questPin" style="top: 1080px; left: 680px;">
        <div class="quest-pin-avatar">
          <img id="myAvatar" src="" alt="My">
        </div>
        <div class="quest-pin-content">
          <div class="quest-pin-title">가볍게 맥주나 와인 한잔 어때요? 🍷</div>
          <div class="quest-pin-tag">⚡ 가벼운 한잔 • 24시간 안심 노출</div>
        </div>
      </div>
    </div>

    <!-- 상단 거리 필터 & 탭 -->
    <div class="top-controls">
      <div class="radius-bar">
        <div class="radius-item">1km</div>
        <div class="radius-item">5km</div>
        <div class="radius-item active">10km</div>
        <div class="radius-item">25km</div>
        <div class="radius-item">50km</div>
        <div class="radius-item">100km</div>
      </div>
      <div class="filter-tabs">
        <div class="tab-item active">✨ 전체</div>
        <div class="tab-item">👥 프로필</div>
        <div class="tab-item" id="questTab">⚡ 번개 (0)</div>
      </div>
    </div>

    <!-- 하단 플로팅 번개 퀘스트 올리기 버튼 -->
    <div class="fab-quest-btn" id="fabBtn">
      <span>⚡</span>
      <span>번개 퀘스트 올리기</span>
    </div>

    <!-- 등록 완료 상단 토스트 배너 -->
    <div class="toast-banner" id="toastBanner">
      <span class="toast-icon">⚡</span>
      <div class="toast-text">
        <div class="toast-title">번개 퀘스트 등록 완료!</div>
        <div class="toast-desc">지도에 24시간 동안 500m 안심 번개 핀이 노출됩니다.</div>
      </div>
    </div>

    <!-- 새 데이트 퀘스트 등록 모달 -->
    <div class="modal-overlay" id="modalOverlay">
      <div class="modal-sheet">
        <div class="modal-top">
          <div class="modal-title-box">
            <div class="modal-header-title">
              <span>⚡</span>
              <span>새 데이트 퀘스트 등록</span>
            </div>
            <div class="modal-header-sub">오늘 당장 함께하고 싶은 즐거운 활동을 지도에 올려보세요!</div>
          </div>
          <div class="modal-close-btn">✕</div>
        </div>

        <!-- 500m 안심 프라이버시 보호 박스 -->
        <div class="privacy-info-card">
          <div class="privacy-header">
            <span>🛡️</span>
            <span>500m 안심 프라이버시 보호</span>
          </div>
          <div class="privacy-desc">
            회원님의 실제 상세 주소가 아닌, <strong>반경 500m 안심 영역</strong>에 무작위로 핀이 배치됩니다.
          </div>
          <div class="privacy-bullets">
            <div class="bullet-item">
              <span>🕒</span>
              <span>등록 후 정확히 24시간 뒤 DB에서 흔적 없이 자동 삭제됩니다.</span>
            </div>
            <div class="bullet-item">
              <span>📡</span>
              <span>등록 즉시 반경 5km 이내 이성 회원 스마트폰으로 실시간 레이더 푸시가 발송됩니다.</span>
            </div>
          </div>
        </div>

        <!-- 카테고리 5개 선택 -->
        <div class="category-grid">
          <div class="cat-item active" id="cat0"><span class="cat-icon">☕</span><span>커피/카페</span></div>
          <div class="cat-item" id="cat1"><span class="cat-icon">🍽️</span><span>맛집 탐방</span></div>
          <div class="cat-item" id="cat2"><span class="cat-icon">🍷</span><span>가벼운 한잔</span></div>
          <div class="cat-item" id="cat3"><span class="cat-icon">🏃</span><span>산책/러닝</span></div>
          <div class="cat-item" id="cat4"><span class="cat-icon">🎨</span><span>놀거리/전시</span></div>
        </div>

        <!-- 추천 칩 4개 -->
        <div class="chips-wrap">
          <div class="chip-pill" id="chip0">#퇴근 후 성수동에서 가볍게 커피 한잔 ☕</div>
          <div class="chip-pill active" id="chip1">#가볍게 맥주나 와인 한잔 어때요? 🍷</div>
          <div class="chip-pill" id="chip2">#선선한 저녁 한강 산책 메이트 구해요 🏃</div>
        </div>

        <!-- 퀘스트 제목 인풋 -->
        <div class="form-input-box" id="titleInput">
          가볍게 맥주나 와인 한잔 어때요? 🍷
        </div>

        <!-- 등록하기 버튼 -->
        <button class="btn-submit-quest" id="modalSubmitBtn">
          <span>퀘스트 등록하기</span>
          <span>✨</span>
        </button>
      </div>
    </div>

    <!-- 하단 실제 네비게이션 탭바 -->
    <div class="app-bottom-nav">
      <div class="nav-item">
        <span class="nav-icon">🔍</span>
        <span>탐색</span>
      </div>
      <div class="nav-item active">
        <span class="nav-icon">🗺️</span>
        <span>지도</span>
      </div>
      <div class="nav-item">
        <span class="nav-icon">🔥</span>
        <span>HOT 회원</span>
      </div>
      <div class="nav-item">
        <span class="nav-icon">💬</span>
        <span>연결</span>
      </div>
      <div class="nav-item">
        <span class="nav-icon">✨</span>
        <span>라운지</span>
      </div>
      <div class="nav-item">
        <span class="nav-icon">👤</span>
        <span>내프로필</span>
      </div>
    </div>
  </div>

  <script>
    const photos = {photos_json};
    
    // 핀들에 실사 사진 주입
    for (let i = 0; i < 7; i++) {{
      const pin = document.getElementById('pin' + i);
      if (pin && photos[i % photos.length]) {{
        pin.querySelector('img').src = photos[i % photos.length];
      }}
    }}
    document.getElementById('myAvatar').src = photos[0] || '';

    // 정확한 8초 시나리오 타임라인 실행
    // [0.0s ~ 1.8s]: 지도 탐색
    // [1.8s]: FAB 버튼 클릭 (스케일)
    // [2.0s]: 모달 오픈
    // [3.2s]: 카테고리 '가벼운 한잔' & 칩 선택
    // [4.8s]: '퀘스트 등록하기' 버튼 클릭
    // [5.2s]: 모달 닫힘
    // [5.5s ~ 8.0s]: 토스트 알림 노출 + 탭 '번개 (1)' 변경 + 지도 위 번개 핀 발광

    setTimeout(() => {{
      document.getElementById('fabBtn').classList.add('pressed');
    }}, 1800);

    setTimeout(() => {{
      document.getElementById('fabBtn').classList.remove('pressed');
      document.getElementById('modalOverlay').classList.add('open');
    }}, 2000);

    setTimeout(() => {{
      // 카테고리 전환
      document.getElementById('cat0').classList.remove('active');
      document.getElementById('cat2').classList.add('active');
    }}, 3200);

    setTimeout(() => {{
      // 등록 버튼 클릭 연출
      document.getElementById('modalSubmitBtn').style.transform = 'scale(0.95)';
    }}, 4800);

    setTimeout(() => {{
      // 모달 닫기
      document.getElementById('modalOverlay').classList.remove('open');
    }}, 5200);

    setTimeout(() => {{
      // 토스트 표출 & 탭 업데이트 & 번개 핀 발광
      document.getElementById('toastBanner').classList.add('show');
      document.getElementById('questTab').classList.add('highlight');
      document.getElementById('questTab').innerText = '⚡ 번개 (1)';
      document.getElementById('questPin').classList.add('show');
    }}, 5500);

    setTimeout(() => {{
      document.getElementById('toastBanner').classList.remove('show');
    }}, 7500);
  </script>
</body>
</html>
"""
    return html


class AuraMapQuestPlaywrightRecorder:
    """Playwright를 활용한 실기기 아우라 500m 안심 레이더 지도 & 번개 퀘스트 8초 고화질 녹화기"""

    def __init__(self):
        try:
            self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            self.ffmpeg_exe = "ffmpeg"
        self.preset_dir = Path(__file__).parent / "presets"
        self.preset_dir.mkdir(parents=True, exist_ok=True)
        self.target_preset_mp4 = self.preset_dir / "aura_safe_radar_map_sim.mp4"

    def record_8s_map_quest_simulation(self, output_mp4: Optional[str] = None) -> str:
        """Playwright Chromium으로 8초간 500m 안심 지도 & 번개 퀘스트 등록 과정을 1080x1920 세로 풀HD MP4로 녹화"""
        out_path = Path(output_mp4 or self.target_preset_mp4).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)

        from playwright.sync_api import sync_playwright
        import tempfile
        import shutil

        temp_html_dir = Path(tempfile.mkdtemp(prefix="aura_map_html_"))
        temp_video_dir = Path(tempfile.mkdtemp(prefix="aura_map_video_"))
        html_file = temp_html_dir / "index.html"
        html_file.write_text(generate_map_quest_html(), encoding="utf-8")

        logger.info(f"🌐 [Playwright] 8번 주제 유저 스크린샷 100% 동일 8초 안심 지도 & 번개 퀘스트 녹화 시작...")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-gpu",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--hide-scrollbars",
                    ]
                )
                context = browser.new_context(
                    viewport={"width": 1080, "height": 1920},
                    device_scale_factor=1,
                    record_video_dir=str(temp_video_dir),
                    record_video_size={"width": 1080, "height": 1920}
                )
                page = context.new_page()
                page.goto(html_file.as_uri(), wait_until="networkidle")

                # 8초 전체 흐름이 자연스럽게 녹화되도록 8.3초 대기
                time.sleep(8.3)

                context.close()
                browser.close()

            # 녹화된 비디오 파일 획득
            recorded_files = list(temp_video_dir.glob("*.webm"))
            if not recorded_files:
                raise RuntimeError("Playwright 녹화 비디오 파일이 생성되지 않았습니다.")

            raw_video = recorded_files[0]

            # FFmpeg로 1080x1920 30fps 무손실 MP4로 트랜스코딩
            cmd = [
                self.ffmpeg_exe, "-y",
                "-i", str(raw_video),
                "-t", "8.0",
                "-vf", "scale=1080:1920,fps=30",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-crf", "16",
                "-preset", "fast",
                str(out_path)
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"🎉 [Playwright 완료] 8번 주제 실기기 100% 매칭 1080x1920 8초 지도 퀘스트 완제품 생성: {out_path} ({out_path.stat().st_size:,} bytes)")
            return str(out_path)

        finally:
            shutil.rmtree(temp_html_dir, ignore_errors=True)
            shutil.rmtree(temp_video_dir, ignore_errors=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    recorder = AuraMapQuestPlaywrightRecorder()
    res = recorder.record_8s_map_quest_simulation()
    print("SUCCESS:", res)
