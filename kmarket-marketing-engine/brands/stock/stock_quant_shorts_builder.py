# -*- coding: utf-8 -*-
"""
StockQuantShortsBuilder - 📊 [StockMaster AI 국내 주식 5대 실시간 30초 무인 숏폼 빌더]
=======================================================================================
- 100% 국내 주식 전문 (미국주식 0% 배제)
- 5대 마스터 라인업:
  1) [주제 1] 삼성전자 실시간 4대 모달 퀀트 수급
  2) [주제 2] SK하이닉스 실시간 4대 모달 퀀트 수급
  3) [주제 3] 뇌동매매 방지! AI 자동 손절매 & 실시간 리스크 가드
  4) [주제 4] 당일 10분 계량 전광판 실시간 1위 주도주 발굴
  5) [주제 5] KOSPI 시장 종합 스트레스 센터 & 환율/금리 리포트
- 주식앱(stockmaster-ai.vercel.app) 실측 데이터 수집 ➔ Gemini 30초 대본 ➔ 성우 TTS ➔ 라이브 녹화 ➔ 2초 네이버 CTA
"""

import os
import sys
import time
import shutil
import asyncio
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import imageio_ffmpeg
import edge_tts

from core.shorts_engine.stock_app_recorder import StockAppRecorder
from brands.stock.ui_templates.stock_cta_card import StockCTACard
from brands.stock.stock_sns_guide_generator import StockSNSGuideGenerator
from brands.stock.stock_realtime_data_fetcher import StockRealtimeDataFetcher
from brands.stock.stock_shorts_script_writer import StockShortsScriptWriter
from core.shorts_engine.stock_shorts_scenario_director import StockShortsScenarioDirector

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("StockQuantShortsBuilder")


class StockQuantShortsBuilder:
    """📊 주식앱 100% 실측치 기반 국내 5대 실시간 30초 숏폼 빌더"""

    def __init__(self):
        self.output_base = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Stock")
        self.output_base.mkdir(parents=True, exist_ok=True)
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.data_fetcher = StockRealtimeDataFetcher()
        self.script_writer = StockShortsScriptWriter()
        self.scenario_director = StockShortsScenarioDirector()
        self.recorder = StockAppRecorder()
        self.cta_card = StockCTACard()

    @staticmethod
    def phonetic_normalize(text: str) -> str:
        """신경망 TTS 발음 오류 교정 (영문 약어 및 종목명 한국어 정음 표기화)"""
        replacements = [
            ("SK하이닉스", "에스케이하이닉스"),
            ("SK이노베이션", "에스케이이노베이션"),
            ("SK텔레콤", "에스케이텔레콤"),
            ("SK", "에스케이"),
            ("LG에너지솔루션", "엘지에너지솔루션"),
            ("LG화학", "엘지화학"),
            ("LG전자", "엘지전자"),
            ("LG", "엘지"),
            ("HBM", "에이치비엠"),
            ("AI", "에이아이"),
            ("KOSPI", "코스피"),
            ("KOSDAQ", "코스닥"),
            ("PER", "피이알"),
            ("PBR", "피비알"),
            ("ROE", "알오이"),
            ("RSI", "알에스아이"),
            ("VETO", "비토"),
            ("veto", "비토")
        ]
        norm = text
        for orig, sub in replacements:
            norm = norm.replace(orig, sub)
        return norm

    async def _generate_voice_async(self, text: str, output_path: str, voice: str = "ko-KR-InJoonNeural", rate: str = "+10%"):
        """Edge TTS 숏폼 전용 고음질 한국어 전문 금융 성우 음성 생성 (발화속도 +10% 정밀 맞춤)"""
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(output_path)

    def get_exact_audio_duration(self, audio_path: str) -> float:
        """FFmpeg로 mp3 음성 파일의 정확한 재생 길이(초)를 실측"""
        try:
            cmd = [self.ffmpeg_exe, "-i", str(audio_path)]
            res = subprocess.run(cmd, capture_output=True)
            stderr = res.stderr.decode("utf-8", errors="ignore")
            import re
            match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", stderr)
            if match:
                h, m, s = match.groups()
                return int(h) * 3600 + int(m) * 60 + float(s)
        except Exception as e:
            logger.warning(f"음성 길이 측정 실패 폴백: {e}")
        return 30.0

    def generate_speech(self, text: str, output_path: str) -> str:
        """초고속 TTS 음성 생성 (정밀 맞춤 + 음성학적 정음 교정)"""
        phonetic_text = self.phonetic_normalize(text)
        logger.info(f"🎙️ [TTS 정음 교정 대본]: {phonetic_text}")
        asyncio.run(self._generate_voice_async(phonetic_text, output_path, rate="+10%"))
        return output_path

    def build_shorts_by_topic(self, topic_id: int = 1, force_fresh_record: bool = True) -> Dict[str, Any]:
        """국내 5대/6대 마스터 주제별 완제품 숏폼 자동 빌드 (대본 길이에 맞춤 100% 자동 동적 동기화)"""
        scenario = self.scenario_director.get_full_scenario(topic_id=topic_id)
        theme_name = scenario["theme_name"]
        stock_target = scenario.get("stock_target", "전광판1위" if topic_id == 4 else "삼성전자")
        stock_name = stock_target

        topic_folder_names = {
            1: "[주제01] 삼성전자_실시간_4대모달_퀀트수급_30초",
            2: "[주제02] SK하이닉스_HBM독주_실시간수급_30초",
            3: "[주제03] 뇌동매매방지_1위이수페타시스_AI리스크가드_30초",
            4: "[주제04] 10분계량전광판_당일1위주도주_발굴_30초",
            5: "[주제05] 코스피_시장종합스트레스_환율금리_30초",
            6: "[주제06] 스톡마스터AI_국내최초자기학습퀀트_총괄소개_30초"
        }

        folder_name = topic_folder_names.get(topic_id, f"[주제{topic_id:02d}] {theme_name}")
        out_folder = self.output_base / folder_name
        out_folder.mkdir(parents=True, exist_ok=True)

        logger.info(f"🚀 [StockQuantShortsBuilder] {folder_name} 실시간 숏폼 제작 가동!")

        # 1. [Step 1] 주식앱 실제 배포 사이트에서 오늘 실시간 퀀트 & 매크로 데이터 수집
        logger.info(f"📡 [Step 1] stockmaster-ai.vercel.app '{stock_name}' 실시간 데이터 수집 중...")
        realtime_data = self.data_fetcher.fetch_stock_data(stock_name)

        # 2. [Step 2] Gemini Flash 맞춤 30초 대본 생성
        logger.info(f"🤖 [Step 2] Gemini Flash 실시간 맞춤 대본 생성 중 (주제 {topic_id})...")
        script = self.script_writer.generate_30s_script(realtime_data, topic_id=topic_id)
        logger.info(f"📝 [확정 대본]: {script}")

        # 3. [Step 3] 전문 금융 성우 음성 합성
        speech_audio_path = str(out_folder / "speech_audio.mp3")
        logger.info("🎙️ [Step 3] 전문 금융 성우 음성 합성 중 (+10% 정밀 속도)...")
        self.generate_speech(script, speech_audio_path)

        # 3-1. [오디오 퍼스트 동적 타임라인 계산]
        audio_dur = self.get_exact_audio_duration(speech_audio_path)
        cta_duration = 2.5
        total_duration = round(audio_dur + 0.6, 2)
        live_app_duration = max(18.0, round(total_duration - cta_duration, 2))
        logger.info(f"⏱️ [Audio-First 동적 시간 동기화]: 음성실측={audio_dur:.2f}s, 앱녹화={live_app_duration:.2f}s, CTA={cta_duration:.2f}s, 완제품총길이={total_duration:.2f}s")

        # 4. [Step 4] 실물 웹앱 라이브 화면 녹화
        live_app_mp4 = str(out_folder / f"01_live_app_topic{topic_id:02d}_live.mp4")
        logger.info(f"📱 [Step 4] Playwright 실물 브라우저 {live_app_duration:.1f}초 라이브 녹화 ({stock_name})...")
        self.recorder.record_simulation_clip(
            topic_id=topic_id,
            duration_sec=live_app_duration,
            output_mp4_path=live_app_mp4,
            force_fresh_record=force_fresh_record
        )

        # 5. [Step 5] 2.5초 네이버 공식 검색 CTA 비디오 생성
        cta_mp4 = str(out_folder / "02_cta_2.5s.mp4")
        logger.info(f"🏷️ [Step 5] {cta_duration:.1f}초 네이버 공식 검색 CTA 비디오 생성...")
        self.cta_card.create_cta_segment_mp4(
            output_path=cta_mp4,
            duration_sec=cta_duration,
            topic_title=theme_name,
            debate_question=scenario.get("debate_question", f"{stock_name} 지금 구간, 추격 매수 vs 조정 대기?"),
            search_keyword="스톡마스터 AI",
            hero_copy="10분마다 실시간 퀀트 데이터 무료 확인!"
        )

        # 6. [Step 6] 앱 영상 + CTA 결합 및 음성 믹싱 (대본 종료 시점 자동 완결)
        final_mp4 = out_folder / f"[주제{topic_id:02d}_완성본]_30초_세로풀HD.mp4"
        logger.info(f"✨ [Step 6] {total_duration:.2f}초 1080x1920 세로 풀HD 최종 완제품 인코딩 중 -> {final_mp4}")

        concat_list = out_folder / "concat_list.txt"
        concat_list.write_text(
            f"file '{Path(live_app_mp4).resolve().as_posix()}'\n"
            f"file '{Path(cta_mp4).resolve().as_posix()}'\n",
            encoding="utf-8"
        )

        cmd = [
            self.ffmpeg_exe, "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-i", speech_audio_path,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-t", f"{total_duration:.2f}",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            str(final_mp4)
        ]

        res = subprocess.run(cmd, capture_output=True)
        if res.returncode != 0:
            err = res.stderr.decode("utf-8", errors="ignore")
            logger.error(f"❌ FFmpeg 컴포징 실패: {err}")
            raise RuntimeError(f"FFmpeg composite failed: {err}")

        # 대표 썸네일 추출 (15초 지점)
        thumb_jpg = out_folder / f"[주제{topic_id:02d}_대표썸네일].jpg"
        thumb_cmd = [self.ffmpeg_exe, "-y", "-ss", "15.0", "-i", str(final_mp4), "-vframes", "1", "-q:v", "2", str(thumb_jpg)]
        subprocess.run(thumb_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 7. [Step 7] SNS 5대 플랫폼 업로드 원클릭 가이드 자동 생성
        guide_file = out_folder / "[SNS_업로드_원클릭_복사붙여넣기_가이드].txt"
        topic_titles = {
            1: "오늘 삼성전자 4.1조원 수급 폭발! 4대 모달 실시간 퀀트 분석",
            2: "SK하이닉스 HBM 독주와 5.1조원 거래대금 폭발! 실시간 퀀트 지표",
            3: "급등주 추격 매수로 계좌 녹이지 마세요! 전광판 1위 이수페타시스 142점 & AI 리스크 가드",
            4: "오늘 장중 국내 350개 우량주 중 진짜 1위 주도주 발굴!",
            5: "대한민국 증시 시장 종합 스트레스 지수 10점 안정 국면! 글로벌 4대 매크로 리포트",
            6: "하루 종일 HTS 보지 마세요! 국내 최초 자기학습 AI 퀀트 비서 Stock Master AI 총괄 소개"
        }
        topic_tags = {
            1: "#삼성전자 #주식수급 #외인기관수급 #주식AI #스톡마스터AI #삼성전자주가 #퀀트투자",
            2: "#SK하이닉스 #HBM반도체 #반도체주식 #주식AI #스톡마스터AI #SK하이닉스주가 #수급분석",
            3: "#이수페타시스 #뇌동매매방지 #주식손절매 #리스크관리 #주식AI #스톡마스터AI #원금보호 #퀀트투자",
            4: "#주도주 #급등주발굴 #10분전광판 #주식수급 #주식AI #스톡마스터AI #세력매집",
            5: "#코스피 #시장스트레스 #미국국채금리 #환율전망 #주식AI #스톡마스터AI #증시시황",
            6: "#스톡마스터AI #주식AI #퀀트투자 #주식어플 #AI트레이딩 #직장인주식 #주식손절알림"
        }

        guide_text = f"""================================================================================
📱 [주제 {topic_id:02d}] 유튜브 쇼츠 / 인스타그램 릴스 / 틱톡 업로드용 원클릭 가이드
================================================================================

📌 1. 영상 제목 (YouTube Shorts / Reels / TikTok):
{topic_titles.get(topic_id, theme_name)}

📝 2. 영상 본문 설명 (Copy & Paste):
{script}

🔥 10분마다 실시간 계량 퀀트 분석 무료 확인하기!
네이버 검색창에 [스톡마스터 AI]를 검색해보세요!

🔗 서비스 랜딩 링크: https://stockmaster-ai.vercel.app/

🏷️ 3. 추천 해시태그:
{topic_tags.get(topic_id, '#스톡마스터AI #주식AI #퀀트투자')}

🏷️ 4. 공식 검색 키워드 (네이버 검색):
스톡마스터 AI (띄어쓰기 필수)

================================================================================
"""
        guide_file.write_text(guide_text, encoding="utf-8")

        # SQLite 마케팅 DB에 실시간 실적 기록
        try:
            from core.db_manager import DBManager
            DBManager().record_history(
                service_id="stock",
                target_lang="ko",
                content_type="shorts",
                content_text=f"[{topic_titles.get(topic_id, theme_name)}]\n{script}",
                target_url="https://stockmaster-ai.vercel.app/",
                score=95.0
            )
        except Exception as dbe:
            logger.warning(f"DB 기록 실패 (계속 진행): {dbe}")

        logger.info(f"🎉 [{folder_name} 30초 완제품 완성!] {final_mp4} ({final_mp4.stat().st_size / 1024 / 1024:.2f} MB)")
        return {
            "topic_id": topic_id,
            "theme_name": theme_name,
            "output_mp4": str(final_mp4),
            "thumbnail_jpg": str(thumb_jpg),
            "sns_guide_path": str(guide_file),
            "output_folder": str(out_folder),
            "realtime_data": realtime_data,
            "script": script
        }

    def build_samsung_shorts(self, force_fresh_record: bool = True) -> Dict[str, Any]:
        """주제 1 단독 래퍼"""
        return self.build_shorts_by_topic(topic_id=1, force_fresh_record=force_fresh_record)

    def build_30s_samsung_shorts(self, force_fresh_record: bool = True) -> Dict[str, Any]:
        """호환용 래퍼"""
        return self.build_shorts_by_topic(topic_id=1, force_fresh_record=force_fresh_record)


if __name__ == "__main__":
    builder = StockQuantShortsBuilder()
    res = builder.build_shorts_by_topic(topic_id=2, force_fresh_record=True)
    print("FINISHED TOPIC 2:", res)
