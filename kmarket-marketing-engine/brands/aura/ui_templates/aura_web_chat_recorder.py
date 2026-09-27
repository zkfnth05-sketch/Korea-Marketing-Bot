# -*- coding: utf-8 -*-
"""
AuraWebChatRecorder - 🌐 [실제 아우라 웹 앱 브라우저 직접 렌더링 & 녹화 모듈]
- Playwright 헤드리스 크로미움 브라우저를 통해 실제 아우라 앱의 DOM/CSS/JS 화면을 100% 렌더링
- 8초(10초~18초) 동안 [빈 화면 -> AI 첫대화 추천 탭 -> 메시지 전송 -> 상대방 칼답 -> 대화 누적 -> 주말 데이트 확정]을 실제 웹 브라우저에서 실행하고 캡처
- 스마트폰 액정 해상도 (469x1024) 무손실 PIL Image 반환
"""

import os
import time
import logging
from pathlib import Path
from typing import List, Optional
from PIL import Image
import io

logger = logging.getLogger("AuraWebChatRecorder")


class AuraWebChatRecorder:
    """실제 아우라 앱 웹 브라우저 렌더러 및 시퀀스 캡처 엔진"""

    def __init__(self):
        self.width = 469
        self.height = 1024
        self.html_path = Path(__file__).parent / "aura_exact_8s_chat.html"

    def render_step(self, step: int = 4) -> Image.Image:
        """
        Playwright로 실제 아우라 웹 시뮬레이터를 띄워 특정 타임라인 단계의 실사 웹 화면을 캡처
        """
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": self.width, "height": self.height})
            
            file_url = f"file:///{self.html_path.resolve().as_posix()}"
            page.goto(file_url, wait_until="networkidle")
            page.wait_for_timeout(200)

            # 타임라인 애니메이션 실행
            page.evaluate("window.start8sExactAnimation()")
            # step에 따른 시간 대기 (0: 0.8s, 1: 1.6s, 2: 3.4s, 3: 5.7s, 4: 7.8s)
            delays = [800, 1600, 3400, 5700, 7800]
            target_delay = delays[min(max(0, step), len(delays) - 1)]
            page.wait_for_timeout(target_delay)

            png_bytes = page.screenshot(type="png")
            browser.close()

            img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
            return img

    def render_all_frames(self, output_dir: Optional[Path] = None) -> List[Image.Image]:
        """
        8초 동안의 전체 단계별 실사 웹 프레임을 생성하여 리스트로 반환 및 저장
        """
        from playwright.sync_api import sync_playwright

        frames = []
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": self.width, "height": self.height})
            
            file_url = f"file:///{self.html_path.resolve().as_posix()}"
            page.goto(file_url, wait_until="networkidle")
            page.wait_for_timeout(200)

            page.evaluate("window.start8sExactAnimation()")
            timestamps = [800, 1200, 1600, 2400, 3400, 4100, 4800, 5700, 6300, 7800]
            start_t = time.time()
            for idx, target_ms in enumerate(timestamps):
                elapsed_ms = (time.time() - start_t) * 1000
                sleep_ms = target_ms - elapsed_ms
                if sleep_ms > 0:
                    page.wait_for_timeout(sleep_ms)
                png_bytes = page.screenshot(type="png")
                img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
                frames.append(img)
                if output_dir:
                    save_path = output_dir / f"web_chat_step_{idx}.png"
                    img.save(str(save_path))
                    logger.info(f"📸 [아우라 웹 캡처] Step {idx} 저장 완료: {save_path}")

            browser.close()

        return frames

