# -*- coding: utf-8 -*-
"""
[공용 UI 컴포넌트] Naver Search Bar Component (3개 브랜드 공용 슬림형 네이버 검색창 UI)
=======================================================================================
- 역할: 숏폼 및 카드뉴스 기존 CTA 버튼(42~44px) 자리에 1:1 정밀 호환되는 슬림 네이버 공식 검색창 바
- 1:1 슬림 규격:
  * 전체 높이: 44px (기존 주황색/원형 버튼 규격과 100% 동일)
  * N 뱃지: 28x28px 초록 뱃지
  * 공식 검색어: 15px 볼드 (stock: '스톡마스터 AI', aura: '아우라AI데이팅', insurance: '보험 리밸런스')
  * 검색 버튼: 12px 슬림 버튼 [검색 🔍]
  * 하단 사족 텍스트 완전 배제 -> 순수 44px 단일 슬림 바
"""

from typing import Optional, Dict, Any

BRAND_SEARCH_CONFIGS: Dict[str, Dict[str, str]] = {
    "stock": {
        "keyword": "스톡마스터 AI",
        "guide": "네이버 검색창에 입력해 보세요",
    },
    "aura": {
        "keyword": "아우라AI데이팅",
        "guide": "네이버 검색창에 입력해 보세요",
    },
    "insurance": {
        "keyword": "보험 리밸런스",
        "guide": "네이버 검색창에 입력해 보세요",
    }
}


def render_naver_search_bar_html(brand: str = "stock", custom_keyword: Optional[str] = None) -> str:
    """
    3개 브랜드 공용 네이버 공식 검색창 바 HTML 생성
    (대표님 지정 황금 규격: 50px 슬림 럭셔리 & 고시인성 일체형)
    """
    cfg = BRAND_SEARCH_CONFIGS.get(brand.lower(), BRAND_SEARCH_CONFIGS["stock"])
    keyword = custom_keyword or cfg["keyword"]
    guide = cfg["guide"]

    html = f"""
    <!-- 네이버 공식 검색창 UI (대표님 지정 50px 슬림 럭셔리 규격) -->
    <div style="width: 100%; height: 50px; padding: 0 15px; background: #ffffff; border-radius: 13px; box-shadow: 0 4px 15px rgba(0,0,0,0.35); display: flex; align-items: center; justify-content: space-between; border: 1.5px solid #03C75A; box-sizing: border-box; margin-top: 3px;">
      <div style="display: flex; align-items: center; gap: 11px;">
        <!-- N 뱃지: 32px -->
        <div style="width: 32px; height: 32px; border-radius: 8px; background: #03C75A; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 6px rgba(3, 199, 90, 0.35); flex-shrink: 0;">
          <span style="color: #ffffff; font-size: 18px; font-weight: 900; font-family: sans-serif; line-height: 1;">N</span>
        </div>
        <!-- 안내문구 & 공식 키워드 텍스트 -->
        <div style="display: flex; flex-direction: column; justify-content: center; text-align: left;">
          <span style="font-size: 10px; color: #64748b; font-weight: 700; line-height: 1; margin-bottom: 2px;">{guide}</span>
          <span style="font-size: 17px; color: #0f172a; font-weight: 900; letter-spacing: -0.3px; line-height: 1;">{keyword}</span>
        </div>
      </div>
      <!-- 우측 검색 버튼 -->
      <div style="padding: 5px 13px; border-radius: 8px; background: #03C75A; border: 1px solid #02b150; box-shadow: 0 2px 6px rgba(3, 199, 90, 0.25); display: flex; align-items: center; gap: 4px; flex-shrink: 0;">
        <span style="color: #ffffff; font-size: 13px; font-weight: 900; letter-spacing: -0.2px;">검색</span>
        <span style="font-size: 12px;">🔍</span>
      </div>
    </div>
    """
    return html.strip()


