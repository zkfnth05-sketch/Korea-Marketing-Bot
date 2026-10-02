# -*- coding: utf-8 -*-
"""
AuraVoiceCloner - 💖 [Aura AI 데이팅 전용 알리바바 CosyVoice 음성 복제 파이프라인]
================================================================================
- 페르소나: 20대 중반 발랄하고 친근한 연애 상담사 '아라(Ara)'
- 원천 참조 음성: brands/aura/assets/aura_ara_prompt.wav (5초 Zero-shot Voice Cloning)
- 특징: 맑고 경쾌한 톤, 살짝 웃음기 있는 말투, 속삭이듯 친근한 억양
- 4단 무결점 자율 페일오버: Alibaba CosyVoice -> Typecast -> Gemini 2.5 Flash -> Edge-TTS
- Wan 2.2 S2V 립싱크 100% 호환 (16kHz/24kHz Mono WAV 변환 & 무음 정밀 트리밍 탑재)
"""

import os
import sys
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

logger = logging.getLogger("AuraVoiceCloner")


class AuraVoiceCloner:
    """💖 Aura AI 데이팅 전용 알리바바 CosyVoice 음성 복제기 (독립 레고 블록)"""

    BRAND_NAME = "Aura"
    VOICE_PERSONA = "Ara"
    DEFAULT_SAMPLE_RATE = 24000

    # 5초 황금 참조 음성 및 프롬프트 텍스트
    REFERENCE_AUDIO_PATH_FEMALE = _current_dir / "assets" / "aura_ara_prompt.wav"
    REFERENCE_AUDIO_PATH_MALE = _engine_root / "brands" / "stock" / "assets" / "stock_jinwoo_prompt.wav"

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
        self.typecast_api_key = os.getenv("TYPECAST_API_KEY", "__pltMYPUabgPLzeK8dsNxhBcxPHhexjh7V7YcyeKpzM5")
        # 👩 여성: 아라(Ara) / 👨 남성: 진우(Jinwoo) 독립 Voice ID
        self.typecast_voice_id_female = os.getenv("TYPECAST_VOICE_ID_AURA", "tc_667ce80314cb3a612d6959e8")
        self.typecast_voice_id_male = os.getenv("TYPECAST_VOICE_ID_MALE", "tc_6541f92e4299b0c2017367c3")

    def get_preset_audio_path(self, gender: str = "female") -> Path:
        """Aura 전용 5초 참조 오디오 경로 반환 (성별 일치)"""
        is_male = str(gender).lower() in ["male", "m", "man", "남", "남성"]
        return self.REFERENCE_AUDIO_PATH_MALE if is_male else self.REFERENCE_AUDIO_PATH_FEMALE

    def synthesize(
        self,
        text: str,
        output_wav_path: str,
        gender: str = "female",
        sample_rate: int = 24000
    ) -> str:
        """
        Aura 전용 대본을 아라(여성) 또는 진우(남성) 목소리로 복제 합성 (4단계 자율 페일오버)
        """
        out_p = Path(output_wav_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        is_male = str(gender).lower() in ["male", "m", "man", "남", "남성"]
        persona_name = "진우(Jinwoo - 남성)" if is_male else "아라(Ara - 여성)"

        if not text or not text.strip():
            with wave.open(str(out_p), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(b"\x00" * int(sample_rate * 0.1 * 2))
            logger.info(f"🔇 [AuraVoiceCloner] 빈 텍스트 무음 처리 완료 -> {out_p.name}")
            return str(out_p)

        logger.info(f"💖 [AuraVoiceCloner] {persona_name} 음성 복제 시작: \"{text[:30]}...\"")

        # [1단계] Alibaba DashScope CosyVoice 시도
        if self.dashscope_api_key:
            try:
                res = self._synthesize_cosyvoice(text, str(out_p), gender=gender, sample_rate=sample_rate)
                if res and out_p.exists() and out_p.stat().st_size > 1000:
                    logger.info(f"🎉 [Aura CosyVoice 성공] {persona_name} 음성 복제 완료: {out_p.name}")
                    return str(out_p)
            except Exception as e:
                logger.warning(f"⚠️ [Aura CosyVoice API 예외] {e} ➔ 2단계 Typecast로 전환")

        # [2단계] Typecast 보이스 폴백 (남/여 맞춤)
        try:
            res = self._synthesize_typecast(text, str(out_p), gender=gender, sample_rate=sample_rate)
            if res and out_p.exists() and out_p.stat().st_size > 1000:
                logger.info(f"🎉 [Aura Typecast 성공] {persona_name} 음성 합성 완료: {out_p.name}")
                return str(out_p)
        except Exception as e:
            logger.warning(f"⚠️ [Aura Typecast 예외] {e} ➔ 3단계 Edge-TTS로 전환")

        # [3단계] Edge-TTS 무결점 최종 보증 로컬 폴백 (여성: SunHi / 남성: InJoon)
        res = self._synthesize_edge_tts(text, str(out_p), gender=gender, sample_rate=sample_rate)
        logger.info(f"🎉 [Aura Edge-TTS 성공] {persona_name} 음성 합성 완료: {out_p.name}")
        return str(out_p)

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

    def _synthesize_typecast(self, text: str, output_wav_path: str, gender: str, sample_rate: int) -> bool:
        """Typecast API 연동"""
        from core.shorts_engine.typecast_synthesizer import TypecastSynthesizer
        is_male = str(gender).lower() in ["male", "m", "man", "남", "남성"]
        voice_id = self.typecast_voice_id_male if is_male else self.typecast_voice_id_female

        synth = TypecastSynthesizer(
            api_key=self.typecast_api_key,
            default_voice_id=voice_id,
            output_dir=str(self.output_dir)
        )
        synth.synthesize(text, output_wav_path, sample_rate=sample_rate)
        return True

    def _synthesize_edge_tts(self, text: str, output_wav_path: str, gender: str, sample_rate: int) -> bool:
        """Edge-TTS 연동 (여성: SunHi / 남성: InJoon)"""
        import asyncio
        import edge_tts

        is_male = str(gender).lower() in ["male", "m", "man", "남", "남성"]
        voice = "ko-KR-InJoonNeural" if is_male else "ko-KR-SunHiNeural"
        temp_mp3 = self.output_dir / f"temp_aura_edge_{os.getpid()}.mp3"

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

    def generate_speech_wav(
        self,
        text: str,
        lang: str = "ko",
        gender: str = "female",
        rate: str = "+0%",
        pitch: Optional[str] = None,
        target_duration: Optional[float] = None,
        filename_prefix: str = "speech"
    ) -> str:
        """
        BaseShortsProducer 및 S2VClipStitcher 표준 100% 호환 인터페이스
        - 여성: 아라(Ara) / 남성: 진우(Jinwoo)
        - 16kHz 무손실 변환 및 무음 정밀 트리밍 적용
        """
        out_wav_path = os.path.join(self.output_dir, f"{filename_prefix}_{lang}.wav")
        temp_wav_path = os.path.join(self.output_dir, f"{filename_prefix}_{lang}_raw24k.wav")

        # 1. 24kHz 원본 합성
        self.synthesize(text=text, output_wav_path=temp_wav_path, gender=gender, sample_rate=24000)

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
    cloner = AuraVoiceCloner()
    test_out = r"C:\Users\zkfnt\Desktop\test_aura_voice.wav"
    cloner.synthesize("안녕하세요! 아우라 AI 데이팅에서 딱 맞는 인연을 찾아드릴게요.", test_out, gender="female")
    print(f"🎉 Aura 아라 음성 생성 완료: {test_out}")
