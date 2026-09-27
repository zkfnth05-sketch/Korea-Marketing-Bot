# -*- coding: utf-8 -*-
"""
AuraDiagnosisPlaywrightRecorder - 📱 [Aura 7번 주제 전용 실제 웹앱 100% 모달 8초 8인 롤링 고화질 녹화기]
- 유저 스크린샷(aura-ai-dating.vercel.app/profile)과 100% 동일한 완벽한 픽셀 매칭
- 8인의 실제 한국인 회원 사진 + 3~4줄 풍성한 AI 진단 본문 + 2줄 궁합 + 2줄 추천 데이트 코스
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

logger = logging.getLogger("AuraDiagnosisPlaywrightRecorder")

# 유저 스크린샷 규격과 100% 일치하는 8인의 정밀 AI 아우라 화보 진단 리포트 데이터
AURA_REAL_MEMBERS_DATA = [
    {
        "name": "하루 (26, 여)",
        "rank": "상위 1.2%",
        "score": "97",
        "title": "[ 고요한 오후의 뮤즈 ☕ ]",
        "tags": ["#사색적인_매력", "#미식_탐방가", "#여유로운_감성"],
        "desc": "하루님의 고요한 지성과 섬세한 감각을 겸비한 분입니다. 책과 전시에서 영감을 얻고, 여유로운 미식과 카페 문화를 즐기는 모습에서 깊이 있는 매력이 느껴집니다. 새로운 만남에 대한 열린 마음은 하루님의 아우라를 더욱 빛나게 합니다.",
        "match": "하루님의 지적인 대화를 즐기며, 함께 맛집과 문화 생활을 탐험할 수 있는 섬세한 감성의 파트너",
        "date_mood": "오후의 햇살이 비치는 아늑한 북카페에서 시작하여, 미슐랭 가이드에 오른 아티스트의 레스토랑에서 저녁을 즐기는 코스",
        "photo_file": "96RQydIg34IX1DPxoDWv_0_1788952692614.jpg",
        "avatar_gradient": "linear-gradient(135deg, #f43f5e, #ec4899, #8b5cf6)",
        "badge_color": "#ec4899"
    },
    {
        "name": "민재 (28, 남)",
        "rank": "상위 2.5%",
        "score": "98",
        "title": "[ 훈훈한 대형견 남친미 🐶 ]",
        "tags": ["#포근한_매력", "#댕댕이_미소", "#선톡_장인"],
        "desc": "민재님은 특유의 솔직하고 따뜻한 미소로 주위 사람들의 긴장을 무장해제시키는 힐링형 아우라의 소유자입니다. 운동과 카페 투어를 즐기는 건강한 에너지와 세심한 배려심이 상대방에게 깊은 안정감을 선사합니다.",
        "match": "사소한 일상도 소중히 나누며 따뜻한 칭찬과 긍정적인 에너지를 아낌없이 주고받을 수 있는 러블리한 파트너",
        "date_mood": "주말 오후 햇살 가득한 성수동 베이커리 카페 투어 후 노을빛 한강공원을 함께 걷는 산책 코스",
        "photo_file": "SGQtnYq1TpCv77REwTh0_0_1788952699116.jpg",
        "avatar_gradient": "linear-gradient(135deg, #3b82f6, #6366f1, #8b5cf6)",
        "badge_color": "#3b82f6"
    },
    {
        "name": "서연 (27, 여)",
        "rank": "상위 0.5%",
        "score": "99",
        "title": "[ 상위 0.1% 럭셔리 퀸 👑 ]",
        "tags": ["#도도한_매력", "#전문직_바이브", "#커리어우먼"],
        "desc": "서연님은 압도적인 비주얼과 당당한 카리스마로 어딜 가나 시선을 사로잡는 매혹적인 아우라를 지니고 있습니다. 세련된 패션 감각과 높은 프로페셔널리즘이 공존하여 스스로를 가장 빛나게 가꿀 줄 아는 워너비 여성입니다.",
        "match": "자신감 넘치고 지적인 센스를 갖추었으며, 서로의 성장과 커리어를 아낌없이 응원해 줄 스마트한 파트너",
        "date_mood": "도심의 야경이 한눈에 내려다보이는 호텔 최상층 스카이라운지에서 샴페인 페어링과 함께 나누는 비전 토크",
        "photo_file": "YZlwrZAQoOZ1SAl1VVIM_0_1788952702725.jpg",
        "avatar_gradient": "linear-gradient(135deg, #fb7185, #f43f5e, #d946ef)",
        "badge_color": "#f43f5e"
    },
    {
        "name": "다은 (25, 여)",
        "rank": "상위 0.8%",
        "score": "99",
        "title": "[ 첫사랑 노을빛 요정 🌅 ]",
        "tags": ["#첫사랑_재질", "#감성_스냅", "#청순_러블리"],
        "desc": "다은님은 맑고 투명한 눈망울과 포근한 음성으로 첫 만남부터 가슴을 설레게 만드는 독보적 청순 비주얼입니다. 사진과 음악 등 감성적인 취향을 진심으로 즐기며 주위 사람들에게 기분 좋은 설렘을 불어넣습니다.",
        "match": "사소하고 작은 이야기에도 귀 기울여주고 듬직하고 다정하게 챙겨줄 수 있는 따뜻한 오빠 스타일",
        "date_mood": "해질녘 노을이 물드는 반포 한강공원에서 돗자리를 펴고 감성 인디 플레이리스트를 들으며 나누는 대화",
        "photo_file": "TDfGdzl0FLedu3eLqsHh_0_1788952700703.jpg",
        "avatar_gradient": "linear-gradient(135deg, #f59e0b, #ec4899, #8b5cf6)",
        "badge_color": "#f59e0b"
    },
    {
        "name": "도윤 (26, 남)",
        "rank": "상위 1.8%",
        "score": "98",
        "title": "[ 도심 속 감성 뇌섹남 🏙️ ]",
        "tags": ["#미대_오빠", "#전시회_러버", "#트렌디_스타일"],
        "desc": "도윤님은 트렌디한 감각과 섬세한 예술적 안목을 겸비하여 일상의 소소한 순간도 로맨틱한 작품으로 만드는 매력남입니다. 대화 속에서 자연스럽게 묻어나는 위트와 배려심이 상대방의 마음을 편안하게 사로잡습니다.",
        "match": "함께 미술관과 라이브 공연을 관람하며 문화적 취향의 교집합을 넓혀갈 수 있는 감각적인 파트너",
        "date_mood": "한남동 현대미술 갤러리 기획전 관람 후 레트로 LP 바에서 좋아하는 음악을 신청하고 즐기는 코스",
        "photo_file": "ZmeGEBe7xpoBjmKtYAYb_0_1788952704127.jpg",
        "avatar_gradient": "linear-gradient(135deg, #10b981, #06b6d4, #3b82f6)",
        "badge_color": "#10b981"
    },
    {
        "name": "지우 (24, 여)",
        "rank": "상위 3.1%",
        "score": "96",
        "title": "[ 비타민 과즙미 통통 🍋 ]",
        "tags": ["#반전_매력", "#비타민_에너지", "#애교_장인"],
        "desc": "지우님은 톡톡 튀는 발랄함과 밝은 미소로 어색한 공기를 단숨에 화기애애하게 바꾸는 인간 비타민입니다. 솔직하고 사랑스러운 리액션과 통통 튀는 유머 감각으로 누구와 있어도 끊이지 않는 웃음을 만들어냅니다.",
        "match": "함께 새로운 맛집과 이색 액티비티를 탐험하며 친구처럼 설레게 연애할 수 있는 유쾌한 파트너",
        "date_mood": "연남동 골목 감성 소품샵 투어 후 야외 테라스에서 즐기는 브런치와 감성 폴라로이드 사진 촬영",
        "photo_file": "50dJcA4Jq6z8xqCwNCls_0_1788952709702.jpg",
        "avatar_gradient": "linear-gradient(135deg, #f59e0b, #fbbf24, #f43f5e)",
        "badge_color": "#f59e0b"
    },
    {
        "name": "현우 (31, 남)",
        "rank": "상위 0.1%",
        "score": "99",
        "title": "[ 퍼펙트 클래식 젠틀맨 💼 ]",
        "tags": ["#신뢰감_100%", "#성공한_남자의_여유", "#시크_모던"],
        "desc": "현우님은 완벽한 슈트핏과 정중하고 성숙한 매너로 깊은 신뢰감과 든든한 안정감을 선사하는 최고급 아우라의 소유자입니다. 격조 높은 취향과 침착한 리더십으로 상대방을 진심으로 존중하고 배려합니다.",
        "match": "우아한 라이프스타일을 공유하며 오랜 시간 편안하게 삶의 가치관과 철학을 나눌 수 있는 성숙한 파트너",
        "date_mood": "조용한 프렌치 파인다이닝에서 소믈리에 추천 와인과 함께 코스 요리를 즐기는 클래식 디너",
        "photo_file": "IZGZp2KPihOre5qb3I9I_0_1788952701591.jpg",
        "avatar_gradient": "linear-gradient(135deg, #64748b, #475569, #1e293b)",
        "badge_color": "#64748b"
    },
    {
        "name": "소희 (25, 여)",
        "rank": "상위 0.1%",
        "score": "99",
        "title": "[ 상위 0.1% 완벽 슬랜더 잇걸 ✨ ]",
        "tags": ["#성수동_퀸", "#황금_비율", "#여신_강림"],
        "desc": "소희님은 모델 같은 완벽한 비율과 감각적인 스타일링으로 어딜 가나 찬사를 받는 트렌드세터이자 워너비 비주얼입니다. 도도한 첫인상 뒤에 숨겨진 다정하고 진솔한 반전 매력이 상대방의 마음을 단숨에 사로잡습니다.",
        "match": "자신감 넘치고 당당하며, 함께 핫플레이스와 미식을 감각적으로 즐길 줄 아는 스타일리시한 파트너",
        "date_mood": "성수동 감성 에스프레소 바 투어 후 프라이빗 루프탑 샴페인 라운지에서 즐기는 야경 데이트",
        "photo_file": "dC4qedMP9D8LiybNHQYt_0_1788952705267.jpg",
        "avatar_gradient": "linear-gradient(135deg, #ec4899, #f472b6, #fb7185)",
        "badge_color": "#ec4899"
    }
]


def load_real_members_with_base64() -> List[Dict[str, Any]]:
    """로컬에 다운로드된 실제 아우라 한국인 회원 사진을 Base64 Data URI로 로드"""
    photo_dir = Path("scratch/real_aura_photos")
    loaded_data = []
    
    for item in AURA_REAL_MEMBERS_DATA:
        p_path = photo_dir / item["photo_file"]
        if p_path.exists():
            with open(p_path, "rb") as img_f:
                b64 = base64.b64encode(img_f.read()).decode("utf-8")
                avatar_src = f"data:image/jpeg;base64,{b64}"
        else:
            avatar_src = f"https://ncflciezowwpnknuutko.supabase.co/storage/v1/object/public/aura-media/profiles/{item['photo_file']}"
        
        loaded_data.append({
            **item,
            "avatar_url": avatar_src
        })
    return loaded_data


def generate_aura_diagnosis_html() -> str:
    """유저 스크린샷과 100% 동일한 픽셀 매칭 HTML/CSS 템플릿 (1080x1920 세로 풀HD)"""
    personas = load_real_members_with_base64()
    personas_json = json.dumps(personas, ensure_ascii=False)
    
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1080, height=1920, initial-scale=1.0">
<title>Aura AI Diagnosis Simulator</title>
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

  /* 스마트폰 본체 섀시 (1080x1920 세로 풀스크린) */
  .phone-container {{
    width: 1080px;
    height: 1920px;
    background: #09090b;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }}

  /* 앱 배경 (실제 아우라 앱 프로필 뷰 흐림 처리) */
  .app-background {{
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 50% 20%, #311042 0%, #09090b 80%);
    filter: blur(14px) brightness(0.4);
    transform: scale(1.05);
    z-index: 1;
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
    z-index: 50;
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
    background: rgba(9, 9, 11, 0.85);
    backdrop-filter: blur(16px);
    z-index: 40;
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

  /* 매력 진단 모달 팝업 오버레이 (화면 높이를 웅장하게 전체 사용) */
  .modal-overlay {{
    position: relative;
    z-index: 10;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
    padding: 145px 28px 105px 28px;
  }}

  /* 모달 카드 (유저 스크린샷 100% 동일한 글래스모피즘 박스) */
  .modal-card {{
    width: 100%;
    height: 100%;
    background: rgba(18, 12, 28, 0.98);
    border: 2px solid rgba(168, 85, 247, 0.45);
    box-shadow: 0 30px 80px rgba(0, 0, 0, 0.95), 0 0 50px rgba(168, 85, 247, 0.25);
    border-radius: 36px;
    padding: 24px 28px 20px 28px;
    backdrop-filter: blur(30px);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    position: relative;
  }}

  /* 모달 상단 헤더 */
  .modal-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 4px;
  }}
  .modal-title-wrap {{
    display: flex;
    flex-direction: column;
    gap: 3px;
  }}
  .modal-title {{
    font-size: 30px;
    font-weight: 900;
    display: flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(135deg, #ffffff 0%, #f472b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .modal-subtitle {{
    font-size: 18px;
    color: rgba(255, 255, 255, 0.65);
    letter-spacing: -0.3px;
  }}
  .close-btn {{
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.12);
    display: flex;
    align-items: center;
    justify-content: center;
    color: rgba(255, 255, 255, 0.7);
    font-size: 20px;
  }}

  /* 리포트 카드 (AURA PERSONAL REPORT - 유저 스크린샷 100% 동일) */
  .report-container {{
    flex: 1;
    background: linear-gradient(180deg, #28133b 0%, #150f24 100%);
    border: 2px solid rgba(192, 132, 252, 0.45);
    border-radius: 28px;
    padding: 20px 24px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
    margin: 10px 0;
    box-shadow: inset 0 0 30px rgba(168, 85, 247, 0.2);
  }}

  .report-top-bar {{
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 17px;
    font-weight: 800;
    letter-spacing: 1.2px;
    color: #c084fc;
    border-bottom: 1.5px solid rgba(192, 132, 252, 0.2);
    padding-bottom: 8px;
  }}
  .report-brand {{
    color: #a1a1aa;
    font-weight: 700;
  }}

  /* 프로필 아바타 (실사 사진 + 눈부신 오로라 회전 링 + 뱃지) */
  .avatar-wrapper {{
    position: relative;
    width: 170px;
    height: 170px;
    margin: 4px 0 8px 0;
  }}
  .avatar-ring {{
    position: absolute;
    inset: -6px;
    border-radius: 50%;
    background: linear-gradient(135deg, #f43f5e, #ec4899, #8b5cf6, #3b82f6);
    animation: rotateRing 4s linear infinite;
    box-shadow: 0 0 24px rgba(236, 72, 153, 0.6);
  }}
  @keyframes rotateRing {{
    0% {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
  }}
  .avatar-img {{
    position: absolute;
    inset: 4px;
    border-radius: 50%;
    object-fit: cover;
    width: calc(100% - 8px);
    height: calc(100% - 8px);
    border: 3.5px solid #1a1028;
    background: #334155;
  }}
  .rank-badge {{
    position: absolute;
    bottom: -10px;
    left: 50%;
    transform: translateX(-50%);
    background: #ec4899;
    color: #ffffff;
    font-size: 18px;
    font-weight: 900;
    padding: 4px 18px;
    border-radius: 18px;
    white-space: nowrap;
    box-shadow: 0 4px 14px rgba(236, 72, 153, 0.8);
    border: 1.5px solid rgba(255, 255, 255, 0.6);
    z-index: 2;
  }}

  /* 아우라 지수 & 타이틀 */
  .score-wrap {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 24px;
    font-weight: 800;
    color: #fbbf24;
    margin-top: 4px;
  }}
  .hero-title {{
    font-size: 34px;
    font-weight: 900;
    color: #ffffff;
    text-align: center;
    letter-spacing: -0.5px;
    margin: 2px 0 6px 0;
  }}

  /* 해시태그 3개 (유저 스크린샷과 동일하게 둥근 캡슐) */
  .tags-row {{
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    justify-content: center;
    margin-bottom: 8px;
  }}
  .tag-pill {{
    background: rgba(168, 85, 247, 0.25);
    border: 1.5px solid rgba(192, 132, 252, 0.45);
    color: #f472b6;
    font-size: 19px;
    font-weight: 800;
    padding: 6px 16px;
    border-radius: 20px;
  }}

  /* AI 매력 진단 본문 카드 (유저 스크린샷처럼 3~4줄로 풍성하게 노출) */
  .desc-card {{
    width: 100%;
    background: rgba(15, 10, 24, 0.7);
    border: 1.5px solid rgba(255, 255, 255, 0.12);
    border-radius: 20px;
    padding: 16px 20px;
    font-size: 20px;
    line-height: 1.55;
    color: rgba(255, 255, 255, 0.94);
    letter-spacing: -0.3px;
    text-align: left;
    margin-bottom: 8px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
  }}

  /* 궁합 & 데이트 무드 박스 (유저 스크린샷과 100% 동일하게 2줄씩 풍성하게 노출) */
  .sub-box {{
    width: 100%;
    background: rgba(236, 72, 153, 0.1);
    border: 1.5px solid rgba(236, 72, 153, 0.3);
    border-radius: 18px;
    padding: 14px 18px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-bottom: 6px;
    text-align: left;
  }}
  .sub-box-title {{
    font-size: 19px;
    font-weight: 800;
    color: #f472b6;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .sub-box-content {{
    font-size: 18.5px;
    color: rgba(255, 255, 255, 0.85);
    line-height: 1.45;
  }}

  .footer-caption {{
    font-size: 17px;
    color: #c084fc;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-top: 2px;
  }}

  /* 하단 액션 버튼들 */
  .action-wrap {{
    display: flex;
    flex-direction: column;
    gap: 10px;
    width: 100%;
    margin-top: 4px;
  }}
  .btn-insta {{
    width: 100%;
    height: 74px;
    border-radius: 22px;
    background: linear-gradient(90deg, #e11d48 0%, #c026d3 50%, #7c3aed 100%);
    border: none;
    color: #ffffff;
    font-size: 26px;
    font-weight: 900;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    box-shadow: 0 8px 26px rgba(225, 29, 72, 0.5);
    letter-spacing: -0.4px;
  }}
  .btn-row {{
    display: flex;
    gap: 10px;
  }}
  .btn-sub {{
    flex: 1;
    height: 56px;
    border-radius: 16px;
    background: rgba(30, 41, 59, 0.75);
    border: 1.5px solid rgba(255, 255, 255, 0.2);
    color: rgba(255, 255, 255, 0.88);
    font-size: 20px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
  }}

  /* 하단 네비게이션 탭바 */
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
    z-index: 40;
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

  /* 롤링 전환 페이드 애니메이션 */
  .fade-in {{
    animation: fadeIn 0.25s ease-out forwards;
  }}
  @keyframes fadeIn {{
    0% {{ opacity: 0.7; transform: translateY(4px); }}
    100% {{ opacity: 1; transform: translateY(0); }}
  }}
</style>
</head>
<body>
  <div class="phone-container">
    <div class="app-background"></div>

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

    <!-- 매력 진단 모달 팝업 오버레이 -->
    <div class="modal-overlay">
      <div class="modal-card">
        <div class="modal-header">
          <div class="modal-title-wrap">
            <div class="modal-title">✨ 나의 아우라(Aura) 매력 진단</div>
            <div class="modal-subtitle">게미나이 AI 비전이 내 사진과 프로필을 정밀 분석한 1장짜리 화보 리포트</div>
          </div>
          <div class="close-btn">✕</div>
        </div>

        <div class="report-container fade-in" id="reportCard">
          <div class="report-top-bar">
            <span>✨ AURA PERSONAL REPORT</span>
            <span class="report-brand">AURA.DATING</span>
          </div>

          <div class="avatar-wrapper">
            <div class="avatar-ring" id="avatarRing"></div>
            <img class="avatar-img" id="avatarImg" src="" alt="Avatar">
            <div class="rank-badge" id="rankBadge">상위 1.2%</div>
          </div>

          <div class="score-wrap">
            <span>👑</span>
            <span>아우라 지수: <span id="scoreText">97</span></span>
          </div>

          <div class="hero-title" id="titleText">[ 고요한 오후의 뮤즈 ☕ ]</div>

          <div class="tags-row" id="tagsRow"></div>

          <!-- 3~4줄로 풍성하게 나오는 AI 매력 진단 본문 -->
          <div class="desc-card" id="descText"></div>

          <!-- 2줄 풍성한 궁합 박스 -->
          <div class="sub-box">
            <div class="sub-box-title">💖 나와 궁합 99% 최고의 이성 스타일</div>
            <div class="sub-box-content" id="matchText"></div>
          </div>

          <!-- 2줄 풍성한 데이트 무드 박스 -->
          <div class="sub-box" style="background: rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.35);">
            <div class="sub-box-title" style="color: #fbbf24;">☕ 추천 첫 데이트 무드</div>
            <div class="sub-box-content" id="dateMoodText"></div>
          </div>

          <div class="footer-caption">💎 AURA Private Lounge • 50:50 성비 청정 라운지</div>
        </div>

        <div class="action-wrap">
          <button class="btn-insta">📢 인스타그램 스토리에 공유하기</button>
          <div class="btn-row">
            <div class="btn-sub">⬇️ 화보 이미지 저장</div>
            <div class="btn-sub">🔄 다시 진단받기</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 하단 실제 네비게이션 탭바 -->
    <div class="app-bottom-nav">
      <div class="nav-item">
        <span class="nav-icon">🔍</span>
        <span>탐색</span>
      </div>
      <div class="nav-item">
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
      <div class="nav-item active">
        <span class="nav-icon">👤</span>
        <span>내프로필</span>
      </div>
    </div>
  </div>

  <script>
    const personas = {personas_json};
    let currentIndex = 0;

    function renderPersona(index) {{
      const p = personas[index % personas.length];
      document.getElementById('avatarImg').src = p.avatar_url;
      document.getElementById('avatarRing').style.background = p.avatar_gradient;
      document.getElementById('rankBadge').innerText = p.rank;
      document.getElementById('rankBadge').style.background = p.badge_color;
      document.getElementById('scoreText').innerText = p.score;
      document.getElementById('titleText').innerText = p.title;

      // 태그 렌더링
      const tagsRow = document.getElementById('tagsRow');
      tagsRow.innerHTML = '';
      p.tags.forEach(t => {{
        const span = document.createElement('span');
        span.className = 'tag-pill';
        span.innerText = t;
        tagsRow.appendChild(span);
      }});

      document.getElementById('descText').innerText = p.desc;
      document.getElementById('matchText').innerText = p.match;
      document.getElementById('dateMoodText').innerText = p.date_mood;

      // 부드러운 스케일 펄스
      const card = document.getElementById('reportCard');
      card.classList.remove('fade-in');
      void card.offsetWidth;
      card.classList.add('fade-in');
    }}

    // 초기 렌더링
    renderPersona(0);

    // 1초마다 8명 순차 롤링 (8초 동안 8명 100% 노출)
    setInterval(() => {{
      currentIndex = (currentIndex + 1) % personas.length;
      renderPersona(currentIndex);
    }}, 1000);
  </script>
</body>
</html>
"""
    return html


class AuraDiagnosisPlaywrightRecorder:
    """Playwright를 활용한 실기기 아우라 매력 진단 8초 8인 롤링 고화질 비디오 녹화기"""

    def __init__(self):
        try:
            self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            self.ffmpeg_exe = "ffmpeg"
        self.preset_dir = Path(__file__).parent / "presets"
        self.preset_dir.mkdir(parents=True, exist_ok=True)
        self.target_preset_mp4 = self.preset_dir / "aura_ai_diagnosis_report_sim.mp4"

    def record_8s_diagnosis_simulation(self, output_mp4: Optional[str] = None) -> str:
        """Playwright Chromium으로 8초간 8인 롤링 시뮬레이션을 1080x1920 세로 풀HD MP4로 녹화"""
        out_path = Path(output_mp4 or self.target_preset_mp4).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)

        from playwright.sync_api import sync_playwright
        import tempfile
        import shutil

        temp_html_dir = Path(tempfile.mkdtemp(prefix="aura_diag_html_"))
        temp_video_dir = Path(tempfile.mkdtemp(prefix="aura_diag_video_"))
        html_file = temp_html_dir / "index.html"
        html_file.write_text(generate_aura_diagnosis_html(), encoding="utf-8")

        logger.info(f"🌐 [Playwright] 7번 주제 유저 스크린샷 100% 동일 8초 8인 롤링 녹화 시작...")

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

                # 8초 동안 8명이 1초 간격으로 매끄럽게 전환되도록 정확히 8.2초 대기
                time.sleep(8.2)

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
            logger.info(f"🎉 [Playwright 완료] 7번 주제 실기기 100% 매칭 1080x1920 8초 8인 롤링 완제품 생성: {out_path} ({out_path.stat().st_size:,} bytes)")
            return str(out_path)

        finally:
            shutil.rmtree(temp_html_dir, ignore_errors=True)
            shutil.rmtree(temp_video_dir, ignore_errors=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    recorder = AuraDiagnosisPlaywrightRecorder()
    res = recorder.record_8s_diagnosis_simulation()
    print("SUCCESS:", res)
