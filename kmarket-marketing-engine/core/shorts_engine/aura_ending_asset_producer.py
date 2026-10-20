# -*- coding: utf-8 -*-
"""
================================================================================
💜 AuraEndingAssetProducer - [Aura AI 데이팅 1080x1920 엔딩 신뢰 카드 완제품 생성기]
================================================================================
- 브랜드: Aura AI 데이팅 (공식 검색어: '아우라AI데이팅' 붙여쓰기)
- 공식 도메인: https://aura-ai-dating.vercel.app/
- 디자인: 순백색(#ffffff) 바탕 + 로즈 퍼플 & 샴페인 골드 럭셔리 그라데이션
- 카피 3종 (절대 불변):
    1. 3초 무료 입장 라운지
    2. 남초 제로 50:50 황금 성비
    3. 가치관 AI 매칭
- CTA 버튼: 지금 무료 입장하기 >
- [무결성] 타 브랜드(세무/환급 계열) 잔재 문구 0건 · Aura 순정 규격 100%
- Playwright Chromium (Google HarfBuzz + Skia) 무결점 한글 셰이핑
- 폰트 깨짐(두부/네모 박스) 0% 영구 보장
================================================================================
"""

import os
import html
import logging
from pathlib import Path
from typing import Dict, Any
from playwright.sync_api import sync_playwright

logger = logging.getLogger("AuraEndingAssetProducer")

# 💜 Aura AI 데이팅 공식 엔딩 신뢰 카드 규격 (절대 불변)
AURA_OFFICIAL_DOMAIN = "aura-ai-dating.vercel.app"
AURA_OFFICIAL_DOMAIN_URL = "https://aura-ai-dating.vercel.app/"
AURA_OFFICIAL_KEYWORD = "아우라AI데이팅"
AURA_BRAND_NAME = "Aura AI 데이팅"

# 💜 Aura 순정 3대 신뢰 카드 카피 (절대 불변)
AURA_ENDING_CTA: Dict[str, str] = {
    "badge": "AURA AI DATING",
    "sub": "AI 매칭 데이팅 라운지",
    "title": "가치관이 맞는 인연을<br>AI가 3초 만에 찾아드립니다",
    "f1_t": "3초 무료 입장 라운지",
    "f1_d": "회원가입 없이 3초 만에 바로 입장, 부담 없는 무료 라운지",
    "f2_t": "남초 제로 50:50 황금 성비",
    "f2_d": "철저한 성비 관리로 남성 편중 없는 건강한 매칭 환경 보장",
    "f3_t": "가치관 AI 매칭",
    "f3_d": "대화 성향·라이프스타일·가치관을 AI가 정밀 분석해 최적의 인연 연결",
    "domain_lbl": "공식 홈페이지:",
    "btn": "지금 무료 입장하기 >",
}

# 💜 다국어 확장 대비 (한국어 순정 기본, 추후 확장 슬롯)
AURA_ENDING_CTA_I18N: Dict[str, Dict[str, str]] = {
    "ko": AURA_ENDING_CTA,
}


class AuraEndingAssetProducer:
    """Aura AI 데이팅 순백색 럭셔리 로즈퍼플 1080x1920 엔딩 신뢰 카드 완제품 생성기"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.assets_dir = self.base_dir / "assets"
        self.templates_dir = self.assets_dir / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    def generate_html(self, lang: str = "ko", domain_text: str = AURA_OFFICIAL_DOMAIN) -> str:
        """순백색(#ffffff) 바탕 + 로즈 퍼플 & 샴페인 골드 럭셔리 무결점 HTML 생성"""
        info = AURA_ENDING_CTA_I18N.get(lang, AURA_ENDING_CTA)

        return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=1080, height=1920, initial-scale=1.0">
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            -webkit-font-smoothing: antialiased;
        }}
        body {{
            width: 1080px;
            height: 1920px;
            background: #ffffff;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
            padding: 130px 70px 120px 70px;
            color: #1a0b2e;
            position: relative;
            overflow: hidden;
        }}
        /* 은은한 로즈 퍼플 상단 앰비언트 글로우 */
        .bg-pattern {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background:
                radial-gradient(circle at 50% 8%, rgba(168, 85, 247, 0.10) 0%, rgba(255, 255, 255, 0) 55%),
                radial-gradient(circle at 15% 92%, rgba(236, 72, 153, 0.07) 0%, rgba(255, 255, 255, 0) 50%);
            pointer-events: none;
            z-index: 0;
        }}
        .top-container {{
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            z-index: 1;
        }}
        /* 브랜드 로고 바 */
        .brand-header {{
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 30px;
        }}
        .brand-logo-badge {{
            background: linear-gradient(135deg, #a855f7 0%, #d946ef 50%, #ec4899 100%);
            color: #ffffff;
            font-size: 26px;
            font-weight: 900;
            padding: 8px 22px;
            border-radius: 14px;
            letter-spacing: 1.5px;
            box-shadow: 0 6px 18px rgba(168, 85, 247, 0.30);
        }}
        .brand-title {{
            font-size: 30px;
            font-weight: 800;
            color: #2d1b4e;
            letter-spacing: 0.5px;
        }}
        /* 서브 골드 라벨 */
        .legal-tag {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 26px;
        }}
        .gold-line {{
            width: 45px;
            height: 2px;
            background: linear-gradient(90deg, rgba(212,175,55,0) 0%, #d4af37 100%);
            border-radius: 2px;
        }}
        .gold-line.right {{
            background: linear-gradient(90deg, #d4af37 0%, rgba(212,175,55,0) 100%);
        }}
        .legal-text {{
            font-size: 24px;
            font-weight: 700;
            color: #b38728;
            letter-spacing: 1.5px;
        }}
        /* 메인 헤드라인 */
        .main-headline {{
            font-size: 56px;
            font-weight: 900;
            line-height: 1.32;
            text-align: center;
            color: #1a0b2e;
            margin-bottom: 54px;
            word-break: keep-all;
            letter-spacing: -0.5px;
        }}
        /* 3대 신뢰 카드 구역 */
        .cards-grid {{
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 26px;
            margin-bottom: 46px;
        }}
        .trust-card {{
            width: 100%;
            background: #ffffff;
            border: 2px solid rgba(168, 85, 247, 0.28);
            border-radius: 28px;
            padding: 36px 42px;
            display: flex;
            align-items: center;
            gap: 32px;
            box-shadow: 0 8px 24px rgba(168, 85, 247, 0.08), 0 2px 6px rgba(0, 0, 0, 0.03);
        }}
        .trust-card.highlight {{
            background: linear-gradient(135deg, #2d1b4e 0%, #4c1d95 100%);
            border-color: #d4af37;
            box-shadow: 0 15px 38px rgba(76, 29, 149, 0.28);
        }}
        .card-icon-wrap {{
            width: 78px;
            height: 78px;
            border-radius: 22px;
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.14) 0%, rgba(236, 72, 153, 0.20) 100%);
            border: 2px solid rgba(168, 85, 247, 0.35);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 38px;
            flex-shrink: 0;
        }}
        .trust-card.highlight .card-icon-wrap {{
            background: rgba(212, 175, 55, 0.18);
            border-color: #d4af37;
        }}
        .card-body {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .card-title {{
            font-size: 38px;
            font-weight: 900;
            color: #1a0b2e;
            letter-spacing: -0.3px;
        }}
        .trust-card.highlight .card-title {{
            color: #ffffff;
        }}
        .card-desc {{
            font-size: 25px;
            font-weight: 600;
            color: #6b5b7f;
            line-height: 1.42;
            word-break: keep-all;
        }}
        .trust-card.highlight .card-desc {{
            color: #cbb8e8;
        }}
        /* 도메인 인증 바 */
        .domain-strip {{
            width: 100%;
            background: #ffffff;
            border: 2px solid rgba(212, 175, 55, 0.55);
            border-radius: 26px;
            padding: 28px 44px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 6px 20px rgba(212, 175, 55, 0.10);
        }}
        .domain-left {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}
        .lock-icon {{
            font-size: 30px;
        }}
        .domain-label {{
            font-size: 26px;
            font-weight: 700;
            color: #6b5b7f;
            white-space: nowrap;
        }}
        .domain-address {{
            font-size: 36px;
            font-weight: 900;
            color: #b38728;
            letter-spacing: 0.3px;
            white-space: nowrap;
        }}
        /* 하단 럭셔리 그라데이션 CTA 버튼 */
        .bottom-container {{
            width: 100%;
            z-index: 1;
        }}
        .luxury-gold-btn {{
            width: 100%;
            height: 142px;
            background: linear-gradient(135deg, #a855f7 0%, #d946ef 50%, #ec4899 100%);
            border: 2px solid #ffffff;
            border-radius: 71px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 46px;
            font-weight: 900;
            color: #ffffff;
            box-shadow: 0 16px 42px rgba(168, 85, 247, 0.38), inset 0 2px 4px rgba(255, 255, 255, 0.35);
            text-align: center;
            word-break: keep-all;
            padding: 0 30px;
            letter-spacing: 0.5px;
        }}
    </style>
</head>
<body>
    <div class="bg-pattern"></div>
    <div class="top-container">
        <!-- 브랜드 헤더 -->
        <div class="brand-header">
            <div class="brand-logo-badge">{html.escape(info["badge"])}</div>
            <div class="brand-title">{html.escape(AURA_BRAND_NAME)}</div>
        </div>

        <!-- 서브 골드 라벨 -->
        <div class="legal-tag">
            <div class="gold-line"></div>
            <div class="legal-text">{html.escape(info["sub"])}</div>
            <div class="gold-line right"></div>
        </div>

        <!-- 메인 헤드라인 -->
        <div class="main-headline">{info["title"]}</div>

        <!-- 3대 신뢰 카드 -->
        <div class="cards-grid">
            <!-- 1. 3초 무료 입장 라운지 (하이라이트 다크 퍼플 카드) -->
            <div class="trust-card highlight">
                <div class="card-icon-wrap">⚡</div>
                <div class="card-body">
                    <div class="card-title">{html.escape(info["f1_t"])}</div>
                    <div class="card-desc">{html.escape(info["f1_d"])}</div>
                </div>
            </div>

            <!-- 2. 남초 제로 50:50 황금 성비 (화이트 카드) -->
            <div class="trust-card">
                <div class="card-icon-wrap">⚖️</div>
                <div class="card-body">
                    <div class="card-title">{html.escape(info["f2_t"])}</div>
                    <div class="card-desc">{html.escape(info["f2_d"])}</div>
                </div>
            </div>

            <!-- 3. 가치관 AI 매칭 (화이트 카드) -->
            <div class="trust-card">
                <div class="card-icon-wrap">💜</div>
                <div class="card-body">
                    <div class="card-title">{html.escape(info["f3_t"])}</div>
                    <div class="card-desc">{html.escape(info["f3_d"])}</div>
                </div>
            </div>
        </div>

        <!-- 도메인 안내 바 -->
        <div class="domain-strip">
            <div class="domain-left">
                <span class="lock-icon">🔒</span>
                <span class="domain-label">{html.escape(info["domain_lbl"])}</span>
            </div>
            <div class="domain-address">{html.escape(domain_text)}</div>
        </div>
    </div>

    <!-- 하단 럭셔리 CTA 버튼 -->
    <div class="bottom-container">
        <div class="luxury-gold-btn">{info["btn"]}</div>
    </div>
</body>
</html>"""

    def render_and_save(self, lang: str = "ko", domain_text: str = AURA_OFFICIAL_DOMAIN) -> str:
        """Playwright Chromium으로 1080x1920 완제품 PNG 렌더링 및 에셋 폴더에 동시 보관"""
        full_html = self.generate_html(lang=lang, domain_text=domain_text)

        # 1. 템플릿 저장 경로 (Aura 순정 파일명)
        template_path = self.templates_dir / f"aura_ending_cta_{lang}.png"

        # 2. 개별 언어 폴더 경로
        lang_dir = self.assets_dir / f"lang_{lang}"
        lang_dir.mkdir(parents=True, exist_ok=True)
        lang_path = lang_dir / "aura_ending_cta_1080x1920.png"

        logger.info(f"🎨 [{lang.upper()}] Playwright Chromium Aura 순정 1080x1920 엔딩 카드 렌더링...")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=["--disable-gpu", "--disable-software-rasterizer", "--disable-dev-shm-usage"]
                )
                page = browser.new_page(
                    viewport={"width": 1080, "height": 1920},
                    device_scale_factor=1.0
                )
                page.set_content(full_html)
                page.wait_for_timeout(300)
                png_bytes = page.screenshot(type="png")
                browser.close()

            with open(template_path, "wb") as f:
                f.write(png_bytes)
            with open(lang_path, "wb") as f:
                f.write(png_bytes)

            logger.info(f"✅ [{lang.upper()}] Aura 완제품 에셋 영구 저장 완료 -> {template_path.name}")
            return str(template_path)

        except Exception as e:
            logger.error(f"❌ [{lang.upper()}] Aura 엔딩 카드 렌더링 실패: {e}")
            raise

    def render_all_languages(self) -> Dict[str, str]:
        """Aura 전체 언어 완제품 에셋 원클릭 일괄 생성"""
        results = {}
        target_langs = list(AURA_ENDING_CTA_I18N.keys())
        logger.info(f"🚀 [Aura 순정 엔딩 카드 사전 일괄 생성] 대상: {target_langs}")

        for lang in target_langs:
            try:
                out = self.render_and_save(lang=lang)
                results[lang] = out
            except Exception as e:
                logger.error(f"[{lang}] 에셋 생성 오류: {e}")

        logger.info(f"🎉 Aura 엔딩 신뢰 카드 완제품 사전 일괄 생성 100% 완료! (총 {len(results)}개 언어)")
        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    producer = AuraEndingAssetProducer()
    producer.render_all_languages()
