# -*- coding: utf-8 -*-
"""
StockAppRecorder - 📱 [StockMaster AI 삼성전자 4대 심층 모달 24초 100% 실물 라이브 녹화 모듈]
=============================================================================================
- Playwright 헤드리스 브라우저 기반
- 타깃 URL: https://stockmaster-ai.vercel.app/
- 24초 풀스크린 완벽 시연 타임라인:
  1) [0.0s ~ 3.5s] 350개 핵심 우량주 10분 계량 전광판 메인 헤더 & 1위 주도주 실시간 조망
  2) [3.5s ~ 6.5s] 검색창에 '삼성전자' 타이핑 ➔ 삼성전자 클릭 ➔ 4대 심층 모달 팝업 오픈
  3) [6.5s ~ 11.0s] [수급 현황] 탭 ➔ 3대 주체별 순매수량 그래프 + 하단 4조 거래대금/신용잔고율 풀뷰
  4) [11.0s ~ 15.5s] [기술 지표] 탭 ➔ 체결강도 158.07% + 볼린저 밴드 + 하단 4대 지표 카드 풀뷰
  5) [15.5s ~ 19.5s] [리스크 평가] 탭 ➔ 안전 위험도(30/100) + 하단 아킬레스건 안전 박스 풀뷰
  6) [19.5s ~ 24.0s] [기본 정보] 탭 ➔ PER 41.67 / PBR 4.27 / ROE 31.39% + 하단 실적 추이 바 차트 풀뷰
- 1080x1920 세로 풀HD 9:16 모바일 최적화 고화질 MP4 출력 (CRF 18, 30fps)
"""

import os
import sys
import time
import shutil
import tempfile
import logging
import subprocess
from pathlib import Path
from typing import Optional

import imageio_ffmpeg
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("StockAppRecorder")


class StockAppRecorder:
    """📈 StockMaster AI 삼성전자 4대 탭 심층 모달 24초 실물 웹앱 녹화기"""

    BASE_URL = "https://stockmaster-ai.vercel.app/"

    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.presets_dir = Path(__file__).resolve().parent / "presets"
        self.presets_dir.mkdir(parents=True, exist_ok=True)
        logger.info("📱 [StockAppRecorder] 초기화 완료")

    def record_simulation_clip(
        self,
        topic_id: int = 1,
        duration_sec: float = 24.0,
        output_mp4_path: str = "stock_app_sim.mp4",
        force_fresh_record: bool = False
    ) -> str:
        """
        삼성전자 4대 탭(수급 현황 ➔ 기술 지표 ➔ 리스크 평가 ➔ 기본 정보) 상하단 100% 풀뷰 24초 실물 녹화
        - 1080x1920 세로 풀HD 고화질 출력
        """
        out_p = Path(output_mp4_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        preset_cache = self.presets_dir / f"stock_app_sim_topic{topic_id}_24s.mp4"

        if preset_cache.exists() and not force_fresh_record and preset_cache.stat().st_size > 100000:
            logger.info(f"⚡ [StockAppRecorder] 캐시된 24초 고화질 실물 전광판 녹화본 사용 (주제 {topic_id}): {preset_cache}")
            shutil.copyfile(preset_cache, out_p)
            return str(out_p)

        logger.info(f"🎬 [StockAppRecorder] 삼성전자 4대 모달 탭 24초 실물 라이브 녹화 시작 (주제 {topic_id}, {self.BASE_URL})")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_recordings = Path(temp_dir) / "recordings"
            temp_recordings.mkdir(parents=True, exist_ok=True)

            raw_webm = self._record_browser_flow(temp_recordings, topic_id=topic_id, target_duration=duration_sec)

            if not raw_webm or not Path(raw_webm).exists():
                raise RuntimeError("❌ [StockAppRecorder] 브라우저 녹화 파일 생성 실패")

            # FFmpeg 트랜스코딩: 1080x1920 9:16 Full HD & 30fps & 고화질 (crf 18)
            logger.info(f"🔄 [StockAppRecorder] 1080x1920 세로 풀HD 트랜스코딩 중: {raw_webm} -> {out_p}")

            offset = getattr(self, "_ready_offset", 0.0)

            cmd = [
                self.ffmpeg_exe,
                "-y",
                "-ss", f"{offset:.2f}",
                "-i", str(raw_webm),
                "-t", f"{duration_sec:.2f}",
                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
                "-c:v", "libx264",
                "-preset", "slow",
                "-crf", "18",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                "-an",
                str(out_p)
            ]

            res = subprocess.run(cmd, capture_output=True)
            if res.returncode != 0:
                err_msg = res.stderr.decode("utf-8", errors="ignore") if res.stderr else "unknown"
                logger.error(f"❌ FFmpeg 변환 실패: {err_msg}")
                raise RuntimeError(f"FFmpeg transcode error: {err_msg}")

            # 캐시 저장
            try:
                shutil.copyfile(out_p, preset_cache)
                logger.info(f"💾 [StockAppRecorder] 프리셋 캐시 저장 완료 (주제 {topic_id}): {preset_cache}")
            except Exception as e:
                logger.warning(f"⚠️ 캐시 저장 실패: {e}")

        logger.info(f"🎉 [StockAppRecorder] 24초 실물 4대 모달 완벽 시연 클립 완성 (주제 {topic_id}): {out_p} ({out_p.stat().st_size / 1024 / 1024:.2f} MB)")
        return str(out_p)

    def _record_browser_flow(self, record_dir: Path, topic_id: int = 1, target_duration: float = 24.0) -> Optional[str]:
        """Playwright 브라우저에서 인스타 릴스처럼 부드러운 스크롤 애니메이션으로 4대 탭의 상하단 내용을 완벽하게 녹화"""

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

            context = browser.new_context(
                viewport={"width": 430, "height": 840},
                device_scale_factor=2.0,
                is_mobile=True,
                has_touch=True,
                record_video_dir=str(record_dir),
                record_video_size={"width": 430, "height": 840}
            )

            page = context.new_page()

            try:
                # 1. 페이지 로드
                logger.info(f"🌐 [StockAppRecorder] 페이지 로딩: {self.BASE_URL}")
                t_browser_start = time.time()
                page.goto(self.BASE_URL, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(300)

                # 2. 광고 iframe 및 팝업 정리
                page.evaluate("""() => {
                    const style = document.createElement('style');
                    style.innerHTML = `
                        iframe,
                        [class*="ads"],
                        div[id*="google"] {
                            display: none !important;
                            opacity: 0 !important;
                            visibility: hidden !important;
                            pointer-events: none !important;
                        }
                    `;
                    document.head.appendChild(style);
                    document.querySelectorAll('iframe, [id*="google"]').forEach(el => el.remove());
                    document.body.style.margin = '0';
                    document.body.style.padding = '0';
                    document.body.style.overflowX = 'hidden';

                    // 부드러운 스크롤 헬퍼 등록
                    window.smoothScrollModal = function(targetY, durationMs = 600) {
                        return new Promise(resolve => {
                            const modal = document.querySelector('div.fixed.inset-0') || document.body;
                            const startY = modal.scrollTop || 0;
                            const diff = targetY - startY;
                            const startTime = performance.now();
                            function step(now) {
                                const progress = Math.min((now - startTime) / durationMs, 1);
                                const ease = 0.5 - Math.cos(progress * Math.PI) / 2;
                                modal.scrollTop = startY + diff * ease;
                                if (progress < 1) {
                                    requestAnimationFrame(step);
                                } else {
                                    modal.scrollTop = targetY;
                                    resolve();
                                }
                            }
                            requestAnimationFrame(step);
                        });
                    };

                    // 메인 페이지 순수 선형 초저속 연속 스크롤 헬퍼 (일정한 속도로 천천히 하강)
                    window.smoothScrollPageLinear = function(targetY, durationMs = 24000) {
                        return new Promise(resolve => {
                            const startY = window.scrollY || 0;
                            const diff = targetY - startY;
                            const startTime = performance.now();
                            function step(now) {
                                const progress = Math.min((now - startTime) / durationMs, 1);
                                window.scrollTo(0, startY + diff * progress);
                                if (progress < 1) {
                                    requestAnimationFrame(step);
                                } else {
                                    window.scrollTo(0, targetY);
                                    resolve();
                                }
                            }
                            requestAnimationFrame(step);
                        });
                    };
                }""")
                page.wait_for_timeout(200)

                # 주제별 시작 스크롤 위치 및 연출 분기
                if topic_id in [3, 5]:
                    # [주제 3, 5] 앱 맨 처음 최상단 (y=0)에서 시작
                    page.evaluate("() => window.scrollTo(0, 0)")
                    page.wait_for_timeout(300)
                else:
                    # [주제 1, 2, 4] 10분 계량 전광판 위치로 스크롤 이동
                    page.evaluate("() => window.scrollTo(0, 4090)")
                    page.wait_for_timeout(300)

                # 정확한 녹화 시작 타임스탬프 계산
                self._ready_offset = time.time() - t_browser_start
                logger.info(f"⏱️ [StockAppRecorder] 녹화 시작점 동기화: offset={self._ready_offset:.2f}s (주제 {topic_id})")

                if topic_id == 5:
                    # =========================================================================
                    # 🌟 [주제 5: 매크로 스트레스 센터] 28초 타임라인
                    # =========================================================================
                    # [0~8초] 종합 스트레스 10점 & 안내 가이드 조망
                    page.wait_for_timeout(8000)
                    # [8~18초] US 10Y BOND & USD/KRW FX 스트레스 카드 스크롤
                    page.evaluate("() => window.scrollBy({top: 400, behavior: 'smooth'})")
                    page.wait_for_timeout(10000)
                    # [18~28초] KOSPI & KOSDAQ Z-Score 지표 조망
                    page.evaluate("() => window.scrollBy({top: 400, behavior: 'smooth'})")
                    page.wait_for_timeout(9500)

                elif topic_id == 3:
                    # =========================================================================
                    # 🌟 [주제 3: 28초 녹화 전체 동안 최상단(y=0)부터 1등주(y=4400)까지 완벽한 균일 속도 스크롤]
                    # =========================================================================
                    # [0.0s ~ 27.5s (27.5초간)] 초당 ~160px의 완전히 균일한 속도로 앱 맨 위부터 1등주 카드까지 스크롤
                    # 중간 가속/감속이나 멈춤 없이 30초 내내 물 흐르듯 균일하게 지수, AI VETO, 시장 스트레스, 1등주 카드가 이어짐
                    page.evaluate("() => window.smoothScrollPageLinear(4400, 27500)")
                    page.wait_for_timeout(27500)
                    page.wait_for_timeout(500)

                else:
                    # =========================================================================
                    # 🌟 [주제 1, 2, 4: 전광판 및 종목 모달] 28초 타임라인
                    # =========================================================================
                    # [0.0s ~ 4.5s] 350개 우량주 10분 전광판 헤더 & 당일 1위 종목 조망
                    page.wait_for_timeout(4500)

                    # [4.5s ~ 7.5s] 검색창에 타깃 종목 타이핑 ➔ 종목 클릭 ➔ 모달 오픈
                    stock_query = "SK하이닉스" if topic_id == 2 else "삼성전자"
                    inp = page.query_selector('input')
                    if inp:
                        inp.click()
                        inp.fill("")
                        for char in stock_query:
                            inp.type(char, delay=60)
                        page.wait_for_timeout(400)

                    span_target = page.query_selector(f'text="{stock_query}"')
                    if span_target:
                        span_target.click()
                        page.wait_for_timeout(1000)

                    # [주제 1, 2, 4] 4대 탭 순차 순환
                    # 1번째: [수급 현황] 탭
                    tab_supply = page.query_selector('text="수급 현황"')
                    if tab_supply:
                        tab_supply.click()
                        page.wait_for_timeout(1000)
                        page.evaluate("() => window.smoothScrollModal(320, 700)")
                        page.wait_for_timeout(3500)

                    # 2번째: [기술 지표] 탭
                    page.evaluate("() => window.smoothScrollModal(0, 300)")
                    page.wait_for_timeout(350)
                    tab_tech = page.query_selector('text="기술 지표"')
                    if tab_tech:
                        tab_tech.click()
                        page.wait_for_timeout(800)
                        page.evaluate("() => window.smoothScrollModal(380, 700)")
                        page.wait_for_timeout(3800)

                    # 3번째: [리스크 평가] 탭
                    page.evaluate("() => window.smoothScrollModal(0, 300)")
                    page.wait_for_timeout(350)
                    tab_risk = page.query_selector('text="리스크 평가"')
                    if tab_risk:
                        tab_risk.click()
                        page.wait_for_timeout(800)
                        page.evaluate("() => window.smoothScrollModal(260, 700)")
                        page.wait_for_timeout(3400)

                    # 4번째: [기본 정보] 탭
                    page.evaluate("() => window.smoothScrollModal(0, 300)")
                    page.wait_for_timeout(350)
                    tab_basic = page.query_selector('text="기본 정보"')
                    if tab_basic:
                        tab_basic.click()
                        page.wait_for_timeout(800)
                        page.evaluate("() => window.smoothScrollModal(320, 700)")
                        page.wait_for_timeout(3400)

                # 28초 채우기
                elapsed = time.time() - t_browser_start - self._ready_offset
                remain = target_duration - elapsed
                if remain > 0:
                    page.wait_for_timeout(int(remain * 1000) + 100)

            except Exception as e:
                logger.error(f"❌ [StockAppRecorder] 브라우저 자동화 중 오류: {e}")
            finally:
                context.close()
                browser.close()

        # 녹화된 파일 찾기
        recorded_files = list(record_dir.glob("*.webm"))
        if recorded_files:
            return str(recorded_files[0])
        return None

