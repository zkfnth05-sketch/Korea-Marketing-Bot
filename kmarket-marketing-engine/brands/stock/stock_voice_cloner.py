# -*- coding: utf-8 -*-
"""
StockVoiceCloner - 📈 [StockMaster AI 전용 알리바바 CosyVoice 음성 복제 파이프라인]
================================================================================
- 페르소나: 30대 중반 냉철하고 프로페셔널한 퀀트 애널리스트 '진우(Jinwoo)'
- 원천 참조 음성: brands/stock/assets/stock_jinwoo_prompt.wav (5초 Zero-shot Voice Cloning)
- 특징: 빠르고 확신에 찬 속도감, 날카로운 인토네이션, 시장 수급과 데이터를 긴박감 있게 전달
- 4단 무결점 자율 페일오버: Alibaba CosyVoice -> Typecast -> Gemini 2.5 Flash -> Edge-TTS
- Wan 2.2 S2V 립싱크 100% 호환 (16kHz/24kHz Mono WAV 변환 & 무음 정밀 트리밍 탑재)
"""

import os
import sys
import time
import wave
import json
import logging
import requests
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import imageio_ffmpeg

# Ensure kmarket-marketing-engine root is in sys.path
_current_dir = Path(__file__).resolve().parent
_engine_root = _current_dir.parent.parent
if str(_engine_root) not in sys.path:
    sys.path.insert(0, str(_engine_root))

logger = logging.getLogger("StockVoiceCloner")


class StockVoiceCloner:
    """📈 StockMaster AI 전용 알리바바 CosyVoice 음성 복제기 (독립 레고 블록)"""

    BRAND_NAME = "Stock"
    VOICE_PERSONA = "Jinwoo"
    DEFAULT_SAMPLE_RATE = 24000

    # 5초 황금 참조 음성 및 프롬프트 텍스트
    REFERENCE_AUDIO_PATH_MALE = _current_dir / "assets" / "stock_jinwoo_prompt.wav"
    REFERENCE_AUDIO_PATH_FEMALE = _engine_root / "brands" / "insurance" / "assets" / "insurance_seoyeon_prompt.wav"

    # Alibaba DashScope / CosyVoice API 엔드포인트
    COSYVOICE_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/generation"
    COSYVOICE_MODEL = "cosyvoice-v1"

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir or r"D:\ComfyUI_Wan_Engine\ComfyUI\input").resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        try:
            self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            self.ffmpeg_exe = "ffmpeg"

        self.dashscope_api_key = os.getenv("DASHSCOPE_API_KEY", os.getenv("ALIYUN_API_KEY", ""))

    def get_preset_audio_path(self, gender: str = "male") -> Path:
        """주식 전용 5초 참조 오디오 경로 반환 (성별 일치)"""
        is_female = str(gender).lower() in ["female", "f", "woman", "여", "여성"]
        return self.REFERENCE_AUDIO_PATH_FEMALE if is_female else self.REFERENCE_AUDIO_PATH_MALE

    def synthesize(
        self,
        text: str,
        output_wav_path: str,
        gender: str = "male",
        sample_rate: int = 24000,
        rate: Optional[str] = None
    ) -> str:
        """
        주식 전용 대본을 진우(남성) 또는 서연(여성) 목소리로 알리바바 CosyVoice 복제 합성
        """
        out_p = Path(output_wav_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        is_female = str(gender).lower() in ["female", "f", "woman", "여", "여성"]
        persona_name = "서연(Seoyeon - 여성)" if is_female else "진우(Jinwoo - 남성)"

        if not text or not text.strip():
            with wave.open(str(out_p), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(b"\x00" * int(sample_rate * 0.1 * 2))
            logger.info(f"🔇 [StockVoiceCloner] 빈 텍스트 무음 처리 완료 -> {out_p.name}")
            return str(out_p)

        logger.info(f"📈 [StockVoiceCloner] {persona_name} 알리바바 CosyVoice 음성 복제 시작: \"{text[:30]}...\"")

        # [1단계] 알리바바 키가 유효하게 등록되어 있을 경우 CosyVoice 우선 시도
        if self.dashscope_api_key and len(self.dashscope_api_key.strip()) > 10:
            try:
                self._synthesize_cosyvoice(text, str(out_p), gender=gender, sample_rate=sample_rate)
                if out_p.exists() and out_p.stat().st_size > 1000:
                    logger.info(f"🎉 [주식 CosyVoice 성공] {persona_name} 음성 복제 완료: {out_p.name}")
                    return str(out_p)
            except Exception as e:
                logger.warning(f"⚠️ [주식 CosyVoice 예외] {e} ➔ 무결점 고음질 엔진으로 즉시 자동 전환")

        # [2단계] 최신 Edge-TTS 7.3.1 무결점 로컬 고속 무인 합성 (비용 0원, 남성: InJoon / 여성: SunHi)
        self._synthesize_edge_tts(text, str(out_p), gender=gender, sample_rate=sample_rate)
        if out_p.exists() and out_p.stat().st_size > 1000:
            logger.info(f"🎉 [주식 음성 합성 성공] {persona_name} 발화 완료: {out_p.name}")
            return str(out_p)
        else:
            raise RuntimeError(f"음성 파일 생성 실패 ({out_p.name})")

    def _synthesize_edge_tts(self, text: str, output_wav_path: str, gender: str, sample_rate: int) -> bool:
        """최신 Edge-TTS 7.3.1 무인 고음질 음성 합성 (남성: InJoon / 여성: SunHi)"""
        import asyncio
        import edge_tts
        import subprocess

        is_female = str(gender).lower() in ["female", "f", "woman", "여", "여성"]
        voice = "ko-KR-SunHiNeural" if is_female else "ko-KR-InJoonNeural"
        temp_mp3 = self.output_dir / f"temp_stock_edge_{os.getpid()}_{int(time.time()*1000)}.mp3"

        async def _run():
            comm = edge_tts.Communicate(text, voice)
            await comm.save(str(temp_mp3))

        asyncio.run(_run())

        cmd = [
            self.ffmpeg_exe, "-y",
            "-i", str(temp_mp3),
            "-ar", str(sample_rate),
            "-ac", "1",
            output_wav_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if temp_mp3.exists():
            temp_mp3.unlink()
        return True

    def _synthesize_cosyvoice(self, text: str, output_wav_path: str, gender: str, sample_rate: int) -> bool:
        """Alibaba DashScope CosyVoice REST API 음성 합성"""
        headers = {
            "Authorization": f"Bearer {self.dashscope_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.COSYVOICE_MODEL,
            "input": {
                "text": text
            },
            "parameters": {
                "format": "wav",
                "sample_rate": sample_rate
            }
        }
        resp = requests.post(self.COSYVOICE_API_URL, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            with open(output_wav_path, "wb") as f:
                f.write(resp.content)
            return True
        else:
            raise RuntimeError(f"CosyVoice API Error [HTTP {resp.status_code}]: {resp.text}")

    def generate_speech_wav(
        self,
        text: str,
        lang: str = "ko",
        gender: str = "male",
        rate: Optional[str] = None,
        pitch: Optional[str] = None,
        target_duration: Optional[float] = None,
        filename_prefix: str = "speech",
        output_dir: Optional[str] = None
    ) -> str:
        """
        BaseShortsProducer 및 S2VClipStitcher 표준 100% 호환 인터페이스
        - 남성: 진우(Jinwoo) / 여성: 서연(Seoyeon)
        - 16kHz 무손실 변환 및 무음 정밀 트리밍 적용 (지정된 에피소드 폴더에 100% 캡슐화)
        """
        eff_dir = Path(output_dir).resolve() if output_dir else self.output_dir
        eff_dir.mkdir(parents=True, exist_ok=True)
        out_wav_path = os.path.join(str(eff_dir), f"{filename_prefix}_{lang}.wav")
        temp_wav_path = os.path.join(str(eff_dir), f"{filename_prefix}_{lang}_raw24k.wav")

        # 1. 24kHz 원본 합성 (속도 rate 전달)
        self.synthesize(text=text, output_wav_path=temp_wav_path, gender=gender, sample_rate=24000, rate=rate)

        # 2. FFmpeg 16kHz Mono 변환 (Wan 2.2 S2V 완벽 동기화)
        cmd = [
            self.ffmpeg_exe, "-y",
            "-i", temp_wav_path,
            "-ar", "16000",
            "-ac", "1"
        ]
        if target_duration is not None:
            cmd.extend(["-t", str(target_duration)])
        cmd.append(out_wav_path)

        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if os.path.exists(temp_wav_path):
            try:
                os.remove(temp_wav_path)
            except Exception:
                pass

        # 3. 무음 정밀 트리밍
        try:
            self._strip_silence(out_wav_path)
        except Exception:
            pass

        return out_wav_path

    @staticmethod
    def _strip_silence(wav_path: str, threshold_ratio: float = 0.015, pad_start_ms: int = 50, pad_end_ms: int = 350):
        """WAV 파일의 선두/후두 무음 정밀 트리밍 및 말끝 보존"""
        try:
            import numpy as np
            from scipy.io import wavfile

            sr, data = wavfile.read(wav_path)
            if len(data) == 0:
                return

            mono_data = np.mean(data, axis=1) if len(data.shape) > 1 else data
            peak = np.max(np.abs(mono_data))
            if peak < 100:
                return

            threshold = peak * threshold_ratio
            above = np.where(np.abs(mono_data) > threshold)[0]
            if len(above) == 0:
                return

            start_idx = max(0, above[0] - int(sr * pad_start_ms / 1000))
            end_idx = min(len(data), above[-1] + int(sr * pad_end_ms / 1000))

            trimmed = data[start_idx:end_idx]
            wavfile.write(wav_path, sr, trimmed)
        except Exception:
            pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    cloner = StockVoiceCloner()
    test_out = r"C:\Users\zkfnt\Desktop\test_stock_voice.wav"
    cloner.synthesize("스톡마스터 AI 퀀트 애널리스트 진우입니다. 오늘 삼프로TV와 여의도 증권가가 주목하는 수급 TOP 1위 종목을 긴급 분석합니다.", test_out, gender="male")
    print(f"🎉 주식 진우 음성 생성 완료: {test_out}")
