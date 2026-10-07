# -*- coding: utf-8 -*-
"""
capture_stock_topic3_live_iframe_exact.py
- StockMaster AI 실제 라이브 웹앱(https://stockmaster-ai.vercel.app/)에 100% 실시간 접속하여
  3개 핵심 뷰포트를 무인 실시간 정밀 캡처:
  1) 2번 카드: '💡 시장 스트레스 지표별 투자 행동 지침 (RISK GUIDELINES)' (경계국면 55점 등)
  2) 3번 카드: 10분 계량 전광판 '1위 주도주' 아코디언 오픈 (계량 가중치 분석 + 실시간 계량 지표)
  3) 4번 카드: '1위 주도주' 모달의 [수급 현황] 탭 (3대 주체별 외인/기관/개미 실시간 수급 & 거래대금)
"""

import os
import sys
import time
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CaptureStockTopic3Live")

BASE_URL = "https://stockmaster-ai.vercel.app/"
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def capture_all_topic3_live_screens():
    logger.info(f"🌐 [StockMaster AI] 실제 라이브 웹앱 실시간 접속: {BASE_URL}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--hide-scrollbars",
                "--mute-audio"
            ]
        )

        # 모바일 뷰포트 (실제 아이폰 세로 비율)
        context = browser.new_context(
            viewport={"width": 430, "height": 932},
            device_scale_factor=2.0,
            is_mobile=True,
            has_touch=True
        )

        page = context.new_page()
        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2500)

        # 1. 광고 및 방해 요소 완전 제거
        page.evaluate("""() => {
            const style = document.createElement('style');
            style.innerHTML = `
                iframe, [class*="ads"], div[id*="google"] { display: none !important; opacity: 0 !important; }
            `;
            document.head.appendChild(style);
            document.querySelectorAll('iframe, [id*="google"]').forEach(el => el.remove());
        }""")
        page.wait_for_timeout(500)

        # =========================================================================
        # 📸 [2번 카드 실시간 캡처]: '💡 시장 스트레스 지표별 투자 행동 지침 (RISK GUIDELINES)'
        # =========================================================================
        logger.info("📸 [2번 카드] 시장 스트레스 지표별 투자 행동 지침 실시간 정렬 캡처...")
        page.evaluate("""() => {
            // '시장 스트레스' 또는 'RISK GUIDELINES' 텍스트 요소 찾기
            const all = Array.from(document.querySelectorAll('*'));
            const target = all.find(el => 
                el.textContent && el.textContent.includes('시장 스트레스 지표별 투자 행동 지침') && el.children.length === 0
            ) || all.find(el => el.textContent && el.textContent.includes('RISK GUIDELINES'));

            if (target) {
                const box = target.closest('[class*="border"]') || target.parentElement.parentElement;
                if (box) {
                    const rect = box.getBoundingClientRect();
                    window.scrollBy(0, rect.top - 60); // 상단 지수 바 아래 깔끔하게 정렬
                }
            } else {
                window.scrollTo(0, 480);
            }
        }""")
        page.wait_for_timeout(800)
        path_s2 = ASSETS_DIR / "stock_topic3_s2_risk_guidelines.png"
        page.screenshot(path=str(path_s2))
        logger.info(f"✅ [2번 카드 캡처 완료] -> {path_s2.name}")

        # =========================================================================
        # 📸 [3번 카드 실시간 캡처]: 10분 계량 전광판 '1위 주도주' 아코디언 오픈
        # =========================================================================
        logger.info("📸 [3번 카드] 10분 계량 전광판 실시간 1위 주도주 아코디언 오픈 캡처...")
        # 전광판 영역으로 스크롤
        top1_info = page.evaluate("""() => {
            // 전광판 내 1위 종목 찾기 (숫자 1 뱃지 또는 첫번째 전광판 아이템)
            const allItems = Array.from(document.querySelectorAll('*')).filter(el => 
                el.textContent && el.textContent.trim() === '1' && el.children.length === 0
            );
            
            let top1Card = null;
            for (let numEl of allItems) {
                let card = numEl.closest('[class*="border"]');
                if (card && card.textContent.includes('계량 종합')) {
                    top1Card = card;
                    break;
                }
            }
            
            if (!top1Card) {
                // 대체 탐색: '계량 종합'을 가진 첫번째 카드
                const cards = Array.from(document.querySelectorAll('[class*="border"]')).filter(el => 
                    el.textContent.includes('계량 종합') || el.textContent.includes('체결강도')
                );
                if (cards.length > 0) top1Card = cards[0];
            }

            if (top1Card) {
                // 아코디언 클릭 (이미 열려있지 않다면)
                if (!top1Card.textContent.includes('DETAIL SCORES') && !top1Card.textContent.includes('RAW METRICS')) {
                    top1Card.click();
                }
                const rect = top1Card.getBoundingClientRect();
                window.scrollBy(0, rect.top - 50); // 상단 바 아래 정렬
                
                // 1위 종목명 추출
                const titleEl = top1Card.querySelector('h3, h4, span, div');
                return { name: titleEl ? titleEl.textContent.trim() : '1위 주도주' };
            }
            window.scrollTo(0, 1800);
            return { name: '1위 주도주' };
        }""")
        page.wait_for_timeout(1000)
        path_s3 = ASSETS_DIR / "stock_topic3_s3_top1_quant_board.png"
        page.screenshot(path=str(path_s3))
        logger.info(f"✅ [3번 카드 캡처 완료] ({top1_info.get('name')}) -> {path_s3.name}")

        # =========================================================================
        # 📸 [4번 카드 실시간 캡처]: 1위 주도주 모달의 [수급 현황] 탭
        # =========================================================================
        logger.info("📸 [4번 카드] 1위 주도주 모달 오픈 및 [수급 현황] 탭 캡처...")
        page.evaluate("() => window.scrollTo(0, 0)")
        page.wait_for_timeout(400)

        # 1위 종목명에서 순수 한글명 추출 (예: '한국콜마')
        raw_top1 = top1_info.get('name', '한국콜마')
        import re
        kor_matches = re.findall(r'[가-힣]{2,}', raw_top1)
        target_stock_name = kor_matches[0] if kor_matches else "한국콜마"
        logger.info(f"🔍 1위 종목 검색창 입력: '{target_stock_name}'")

        inp = page.query_selector('input')
        if inp:
            inp.click()
            inp.fill("")
            for char in target_stock_name:
                inp.type(char, delay=50)
            page.wait_for_timeout(1000)

            # 검색 결과 항목 클릭
            search_item = page.query_selector(f'text="{target_stock_name}"') or page.query_selector('div.cursor-pointer')
            if search_item:
                search_item.click()
                page.wait_for_timeout(2000)
                logger.info(f"✨ [{target_stock_name}] 모달 팝업 오픈 완료!")

                # [수급 현황] 탭 클릭
                tab_supply = page.query_selector('text="수급 현황"')
                if tab_supply:
                    tab_supply.click()
                    page.wait_for_timeout(800)

                # 모달 내부를 스크롤하여 3대 주체 수급 바가 화면 정중앙에 시원하게 보이도록 조정
                page.evaluate("""() => {
                    const scrollables = Array.from(document.querySelectorAll('div')).filter(el => {
                        const style = window.getComputedStyle(el);
                        return (style.overflowY === 'auto' || style.overflowY === 'scroll') && el.scrollHeight > el.clientHeight;
                    });
                    if (scrollables.length > 0) {
                        scrollables[0].scrollTop = 200;
                    }
                }""")
                page.wait_for_timeout(800)

        path_s4 = ASSETS_DIR / "stock_topic3_s4_top1_supply.png"
        page.screenshot(path=str(path_s4))
        logger.info(f"✅ [4번 카드 캡처 완료] 1위 주도주 수급 현황 -> {path_s4.name}")

        browser.close()
        logger.info("🎉 [CaptureStockTopic3Live] 3개 라이브 화면 실시간 추출 100% 완료!")


if __name__ == "__main__":
    capture_all_topic3_live_screens()
