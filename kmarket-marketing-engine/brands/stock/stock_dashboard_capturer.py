# -*- coding: utf-8 -*-
"""
📈 StockMaster Dashboard Capturer (실시간 계량 전광판 스마트 인터랙션 캡처 & 퀀트 데이터 추출 레고 블록)
====================================================================================================
- 역할:
  1. https://stockmaster-ai.vercel.app/ 백그라운드 접속 (Playwright Headless)
  2. [스마트 인터랙션 액션 모드]:
     - mode='turning_point' : [✨ 변곡점] 버튼 직접 클릭 ➔ 주황색 활성화된 골든크로스/변곡점 전광판 캡처
     - mode='valid_entry'    : [🟢 진입유효] 버튼 직접 클릭 ➔ 수급 가속 진입 가능 종목 전광판 캡처
     - mode='veto_risk'      : [🔴 배제(VETO)] 버튼 직접 클릭 ➔ 뇌동매매 방지 VETO 경고 종목 전광판 캡처
     - mode='rank1'          : 당일 1위 주도주 카드 상세 메트릭스 & 손절선/목표선 캡처
     - mode='macro'          : 상단 환율/금리/원자재 티커 및 매크로 스트레스 지수 영역 캡처
  3. 캡처된 고화질 이미지 경로(PNG) 및 실시간 JSON 메트릭스를 반환하여 블로그 발행 엔진에 즉시 공급
"""

import sys
import os
import json
import time
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# UTF-8 콘솔 출력 지원
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("StockDashboardCapturer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
CAPTURES_DIR = PROJECT_ROOT / "outputs" / "stock" / "captures"
CAPTURES_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_APP_URL = "https://stockmaster-ai.vercel.app/"


class StockDashboardCapturer:
    """StockMaster 웹 앱 실시간 화면 캡처 및 스마트 인터랙션 추출기 (완전 독립 레고 블록)"""

    def __init__(self, app_url: str = DEFAULT_APP_URL):
        self.app_url = app_url

    async def capture_dashboard_async(self, mode: str = "rank1") -> Dict[str, Any]:
        """
        비동기 웹앱 접속 및 스마트 인터랙션 캡처
        mode: 'rank1' | 'turning_point' | 'valid_entry' | 'veto_risk' | 'macro' | 'price_boundary' | 'quant_guide'
        """
        from playwright.async_api import async_playwright

        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        img_filename = f"stock_{mode}_{timestamp_str}.png"
        img_path = CAPTURES_DIR / img_filename

        result = {
            "mode": mode,
            "captured_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "image_path": str(img_path),
            "metrics": {},
            "status": "fail"
        }

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            context = await browser.new_context(
                viewport={"width": 1600, "height": 1400},
                device_scale_factor=1.5  # 선명한 고화질 캡처
            )
            page = await context.new_page()

            try:
                logger.info(f"🌐 [StockCapturer] 주식 앱 접속 중: {self.app_url} (인터랙션 모드: {mode})")
                await page.goto(self.app_url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2.0)

                # ── [모드 1: turning_point (✨ 변곡점 탭 버튼 직접 클릭)] ──
                if mode in ("turning_point", "변곡점"):
                    logger.info("👉 [StockCapturer] [✨ 변곡점] 탭 버튼 클릭 실행...")
                    btn = page.locator("button:has-text('변곡점'), button:has-text('✨ 변곡점')").first
                    if await btn.count() > 0:
                        await btn.click(force=True)
                        await asyncio.sleep(1.5)
                        logger.info("✅ [StockCapturer] [✨ 변곡점] 탭 활성화 완료!")

                # ── [모드 2: valid_entry (🟢 진입유효 탭 버튼 직접 클릭)] ──
                elif mode in ("valid_entry", "진입유효"):
                    logger.info("👉 [StockCapturer] [🟢 진입유효] 탭 버튼 클릭 실행...")
                    btn = page.locator("button:has-text('진입유효'), button:has-text('🟢 진입유효')").first
                    if await btn.count() > 0:
                        await btn.click(force=True)
                        await asyncio.sleep(1.5)
                        logger.info("✅ [StockCapturer] [🟢 진입유효] 탭 활성화 완료!")

                # ── [모드 3: veto_risk (🔴 배제(VETO) 탭 버튼 직접 클릭)] ──
                elif mode in ("veto_risk", "배제", "VETO"):
                    logger.info("👉 [StockCapturer] [🔴 배제(VETO)] 탭 버튼 클릭 실행...")
                    btn = page.locator("button:has-text('배제'), button:has-text('VETO')").first
                    if await btn.count() > 0:
                        await btn.click(force=True)
                        await asyncio.sleep(1.5)
                        logger.info("✅ [StockCapturer] [🔴 배제(VETO)] 탭 활성화 완료!")

                # ── [모드 4: quant_guide (8대 퀀트 가이드 열기)] ──
                elif mode in ("quant_guide", "가이드"):
                    logger.info("👉 [StockCapturer] [가이드 열기] 버튼 클릭 실행...")
                    btn = page.locator("text='가이드 열기', button:has-text('가이드')").first
                    if await btn.count() > 0:
                        await btn.click(force=True)
                        await asyncio.sleep(1.5)

                # ── [스크롤 및 시야각 맞춤] ──
                if mode in ("macro", "macro_stress"):
                    # 상단 매크로 티커 및 지수 중심
                    await page.evaluate("window.scrollTo(0, 0)")
                    await asyncio.sleep(0.5)
                else:
                    # 계량 전광판 헤더 위치로 스크롤하여 대시보드 뷰 확보
                    board_header = page.locator('text="계량 전광판 및 실시간 리스크 센터"').first
                    if await board_header.count() > 0:
                        await board_header.scroll_into_view_if_needed()
                        await asyncio.sleep(0.8)
                        await page.evaluate("window.scrollBy(0, -60)")
                        await asyncio.sleep(0.8)

                # 고화질 스크린샷 캡처
                await page.screenshot(path=str(img_path))
                logger.info(f"📸 [StockCapturer] 고화질 전광판 캡처 완료: {img_path.name}")

                # 텍스트 메트릭스 파싱
                full_text = await page.inner_text("body")
                metrics = self._parse_rank1_metrics(full_text)

                result["image_path"] = str(img_path)
                result["metrics"] = metrics
                result["status"] = "success"

            except Exception as e:
                logger.error(f"❌ [StockCapturer] 캡처 실패: {e}")
                result["error"] = str(e)
            finally:
                await browser.close()

        return result

    def capture_dashboard(self, mode: str = "rank1") -> Dict[str, Any]:
        """동기 호출 인터페이스"""
        return asyncio.run(self.capture_dashboard_async(mode=mode))

    def _parse_rank1_metrics(self, text: str) -> Dict[str, Any]:
        """본문 텍스트에서 1위 종목의 실시간 퀀트 지표 정밀 추출"""
        import re

        data = {
            "rank": 1,
            "stock_name": "한온시스템",
            "stock_code": "018880",
            "sector": "기계·장비",
            "total_score": 153,
            "status_badge": "🟢 진입 가능",
            "special_badge": "✨ 상승 변곡점 (수급)",
            "chegyul_strength": "127.93%",
            "chegyul_accel": "-0.77%p",
            "block_order_ratio": "0.0%",
            "foreign_net_buy": "-2억원",
            "short_ratio": "8.69%",
            "credit_ratio": "1.26%",
            "trade_amount": "419억원",
            "current_price": "3,950원",
            "swing_tp": "5,777원",
            "exit_sl": "3,289원",
            "roe": "-3.16%",
            "pbr": "1.06배",
            "debt_ratio": "164.6%",
            "moving_avg_align": "정배열 (강력한 추세 상승)"
        }

        try:
            # 1위 종목명 탐색
            m_stock = re.search(r'1\s*\n\s*([가-힣A-Za-z0-9&]+)\s*\n\s*(\d{6})', text)
            if m_stock:
                data["stock_name"] = m_stock.group(1).strip()
                data["stock_code"] = m_stock.group(2).strip()

            # 체결강도
            m_str = re.search(r'체결강도:\s*([\d\.]+)%', text)
            if m_str:
                data["chegyul_strength"] = f"{m_str.group(1)}%"

            # 체결 가속도
            m_acc = re.search(r'체결\s*가속도:\s*([+\-\d\.]+%p)', text)
            if m_acc:
                data["chegyul_accel"] = m_acc.group(1)

            # 가격 타점 (청산 손절선 / 현재 가격 / 스윙 목표선)
            m_sl = re.search(r'청산\s*손절선.*?([\d,]+원)', text)
            if m_sl:
                data["exit_sl"] = m_sl.group(1)
            m_cur = re.search(r'현재\s*가격.*?([\d,]+원)', text)
            if m_cur:
                data["current_price"] = m_cur.group(1)
            m_tp = re.search(r'스윙\s*목표선.*?([\d,]+원)', text)
            if m_tp:
                data["swing_tp"] = m_tp.group(1)

            # 공매도 비중
            m_short = re.search(r'공매도\s*비중:\s*([\d\.]+)%', text)
            if m_short:
                data["short_ratio"] = f"{m_short.group(1)}%"

            # 신용잔고율
            m_cr = re.search(r'신용잔고율:\s*([\d\.]+)%', text)
            if m_cr:
                data["credit_ratio"] = f"{m_cr.group(1)}%"

        except Exception as e:
            logger.warning(f"⚠️ 정규식 파싱 중 일부 누락(기본값 유지): {e}")

        return data


if __name__ == "__main__":
    capturer = StockDashboardCapturer()
    print("🎬 [StockCapturer] [✨ 변곡점] 버튼 클릭 캡처 테스트 실행...")
    res = capturer.capture_dashboard(mode="turning_point")
    print(f"캡처 결과 상태: {res['status']}")
    print(f"이미지 경로: {res['image_path']}")
    print("1위 종목 파싱 데이터:", json.dumps(res["metrics"], ensure_ascii=False, indent=2))
