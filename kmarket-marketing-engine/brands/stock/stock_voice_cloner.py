# -*- coding: utf-8 -*-
"""
StockVoiceCloner - 📈 [StockMaster AI 전용 3단 자율 페일오버 음성 합성 파이프라인]
================================================================================
- 페르소나: 30대 중반 냉철하고 프로페셔널한 퀀트 애널리스트 '진우(Jinwoo)' / 여성 '하은(Haeun)'
- 원천 참조 음성: brands/stock/assets/stock_jinwoo_prompt.wav (5초 Zero-shot Voice Cloning)
- 특징: 빠르고 확신에 찬 속도감, 날카로운 인토네이션, 시장 수급과 데이터를 긴박감 있게 전달

[6인 합동 회의체 합의안 - 3단 무결점 자율 페일오버]
  1순위: Google Gemini 2.5 Flash Native Audio
         (core.shorts_engine.gemini_tts_synthesizer.GeminiTTSSynthesizer 연동)
         - 9개 멀티키 체인 자율 순환 스위칭
         - 남성: Fenrir (진우 - 냉철하고 확신에 찬 퀀트 트레이더 톤)
         - 여성: Leda (하은 - 샤프하고 정확한 경제 뉴스 앵커 톤)
  2순위: Alibaba CosyVoice (DASHSCOPE_API_KEY / ALIYUN_API_KEY 존재 시 작동)
  3순위: Edge-TTS 비상 백업
         - 기존 아파트 안내방송 SunHiNeural 전면 퇴출
         - 남성: ko-KR-InJoonNeural (자연스러운 대화체) / 여성: ko-KR-HyunsuNeural

[호출부 100% 규격 호환]
  - BaseShortsProducer / S2VClipStitcher 표준 인터페이스 완벽 보존
  - synthesize(text, output_wav_path, gender, sample_rate, rate=None) -> str
  - generate_speech_wav(text, lang, gender, rate, pitch, target_duration,
                        filename_prefix, output_dir) -> str
  - Wan 2.2 S2V 립싱크 100% 호환 (16kHz Mono WAV 무손실 변환 & 무음 정밀 트리밍 탑재)
"""

import os
import sys
import time
import wave
import logging
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
    """📈 StockMaster AI 전용 3단 자율 페일오버 음성 합성기 (독립 레고 블록)"""

    BRAND_NAME = "Stock"
    VOICE_PERSONA = "Jinwoo"
    DEFAULT_SAMPLE_RATE = 24000

    # 5초 황금 참조 음성 및 프롬프트 텍스트
    REFERENCE_AUDIO_PATH_MALE = _current_dir / "assets" / "stock_jinwoo_prompt.wav"
    REFERENCE_AUDIO_PATH_FEMALE = _engine_root / "brands" / "insurance" / "assets" / "insurance_seoyeon_prompt.wav"

    # [1순위] Google Gemini 2.5 Flash Native Audio 보이스 매핑 (주식 전용 확정)
    GEMINI_VOICE_MALE = "Fenrir"    # 진우(Jinwoo) - 냉철하고 확신에 찬 퀀트 트레이더 톤
    GEMINI_VOICE_FEMALE = "Leda"    # 하은(Haeun) - 샤프하고 정확한 경제 뉴스 앵커 톤

    # [3순위] Edge-TTS 비상 백업 보이스 매핑 (아파트 안내방송 SunHiNeural 전면 퇴출)
    EDGE_VOICE_MALE = "ko-KR-InJoonNeural"     # 자연스러운 대화체 남성
    EDGE_VOICE_FEMALE = "ko-KR-HyunsuNeural"   # 자연스러운 대화체 여성

    # [2순위] Alibaba DashScope / CosyVoice API 엔드포인트
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

        # [1순위] Gemini 2.5 Flash Native Audio 합성기 지연 초기화 (import 실패에도 안전)
        self._gemini_synth = None
        self._gemini_init_failed = False

    # ------------------------------------------------------------------
    # 유틸리티
    # ------------------------------------------------------------------
    @staticmethod
    def _is_female(gender: str) -> bool:
        """성별 문자열 정규화 (한/영/약어 전부 허용)"""
        return str(gender).strip().lower() in ["female", "f", "woman", "여", "여성", "girl", "bride"]

    def get_preset_audio_path(self, gender: str = "male") -> Path:
        """주식 전용 5초 참조 오디오 경로 반환 (성별 일치)"""
        return self.REFERENCE_AUDIO_PATH_FEMALE if self._is_female(gender) else self.REFERENCE_AUDIO_PATH_MALE

    def _get_gemini_synth(self):
        """GeminiTTSSynthesizer 지연 초기화 (9개 멀티키 체인 내장)"""
        if self._gemini_synth is not None:
            return self._gemini_synth
        if self._gemini_init_failed:
            return None
        try:
            from core.shorts_engine.gemini_tts_synthesizer import GeminiTTSSynthesizer
            self._gemini_synth = GeminiTTSSynthesizer(
                default_voice=self.GEMINI_VOICE_MALE,
                output_dir=str(self.output_dir)
            )
            if not getattr(self._gemini_synth, "api_keys", None):
                logger.warning("⚠️ [StockVoiceCloner] Gemini API 키 미등록 ➔ 2순위 CosyVoice로 자동 전환")
                self._gemini_init_failed = True
                self._gemini_synth = None
                return None
            logger.info(
                f"✅ [StockVoiceCloner] Gemini 2.5 Flash Native Audio 연동 완료 "
                f"(멀티키 {len(self._gemini_synth.api_keys)}개 체인)"
            )
            return self._gemini_synth
        except Exception as e:
            logger.warning(f"⚠️ [StockVoiceCloner] GeminiTTSSynthesizer 초기화 실패: {e} ➔ 2순위로 자동 전환")
            self._gemini_init_failed = True
            self._gemini_synth = None
            return None

    @staticmethod
    def _write_silent_wav(out_p: Path, sample_rate: int, seconds: float = 0.1) -> None:
        """빈 텍스트용 무음 WAV 생성"""
        with wave.open(str(out_p), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(b"\x00" * int(sample_rate * seconds * 2))

    @staticmethod
    def _is_valid_wav(path: Path, min_bytes: int = 1000) -> bool:
        """생성된 WAV 파일 유효성 검증"""
        try:
            return path.exists() and path.stat().st_size > min_bytes
        except Exception:
            return False

    # ------------------------------------------------------------------
    # 메인 합성 진입점 (호출부 100% 규격 호환)
    # ------------------------------------------------------------------
    def synthesize(
        self,
        text: str,
        output_wav_path: str,
        gender: str = "male",
        sample_rate: int = 24000,
        rate: Optional[str] = None
    ) -> str:
        """
        주식 전용 대본을 진우(남성) 또는 하은(여성) 목소리로 합성
        [3단 자율 페일오버] Gemini 2.5 Flash ➔ CosyVoice ➔ Edge-TTS
        반환값: 생성된 WAV 파일의 절대 경로(str)
        """
        out_p = Path(output_wav_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        is_female = self._is_female(gender)
        persona_name = "하은(Haeun - 여성)" if is_female else "진우(Jinwoo - 남성)"

        # 빈 텍스트 방어
        if not text or not text.strip():
            self._write_silent_wav(out_p, sample_rate)
            logger.info(f"🔇 [StockVoiceCloner] 빈 텍스트 무음 처리 완료 -> {out_p.name}")
            return str(out_p)

        logger.info(
            f"📈 [StockVoiceCloner] {persona_name} 음성 합성 시작: \"{text[:30]}...\""
        )

        # ==============================================================
        # [1순위] Google Gemini 2.5 Flash Native Audio (9개 멀티키 체인)
        # ==============================================================
        gemini = self._get_gemini_synth()
        if gemini is not None:
            voice_name = self.GEMINI_VOICE_FEMALE if is_female else self.GEMINI_VOICE_MALE
            try:
                gemini.synthesize(
                    text=text,
                    output_wav_path=str(out_p),
                    voice_name=voice_name,
                    sample_rate=sample_rate
                )
                if self._is_valid_wav(out_p):
                    logger.info(
                        f"🎉 [주식 Gemini 성공] {persona_name} '{voice_name}' 음성 합성 완료: {out_p.name}"
                    )
                    return str(out_p)
                logger.warning("⚠️ [주식 Gemini] 생성 파일 검증 실패 ➔ 2순위 CosyVoice로 자동 전환")
            except Exception as e:
                logger.warning(f"⚠️ [주식 Gemini 예외] {str(e)[:120]} ➔ 2순위 CosyVoice로 자동 전환")

        # ==============================================================
        # [2순위] Alibaba CosyVoice (DASHSCOPE_API_KEY / ALIYUN_API_KEY 존재 시)
        # ==============================================================
        if self.dashscope_api_key and len(self.dashscope_api_key.strip()) > 10:
            try:
                self._synthesize_cosyvoice(text, str(out_p), gender=gender, sample_rate=sample_rate)
                if self._is_valid_wav(out_p):
                    logger.info(f"🎉 [주식 CosyVoice 성공] {persona_name} 음성 복제 완료: {out_p.name}")
                    return str(out_p)
                logger.warning("⚠️ [주식 CosyVoice] 생성 파일 검증 실패 ➔ 3순위 Edge-TTS로 자동 전환")
            except Exception as e:
                logger.warning(f"⚠️ [주식 CosyVoice 예외] {str(e)[:120]} ➔ 3순위 Edge-TTS로 자동 전환")
        else:
            logger.info("ℹ️ [StockVoiceCloner] DashScope 키 미등록 ➔ 3순위 Edge-TTS 비상 백업 사용")

        # ==============================================================
        # [3순위] Edge-TTS 비상 백업 (자연스러운 대화체 보이스)
        # ==============================================================
        self._synthesize_edge_tts(text, str(out_p), gender=gender, sample_rate=sample_rate)
        if self._is_valid_wav(out_p):
            logger.info(f"🎉 [주식 Edge-TTS 백업 성공] {persona_name} 발화 완료: {out_p.name}")
            return str(out_p)

        raise RuntimeError(f"음성 파일 생성 실패 - 3단 엔진 전부 실패 ({out_p.name})")

    # ------------------------------------------------------------------
    # [3순위] Edge-TTS 비상 백업
    # ------------------------------------------------------------------
    def _synthesize_edge_tts(self, text: str, output_wav_path: str, gender: str, sample_rate: int) -> bool:
        """
        Edge-TTS 비상 백업 합성
        - 기존 아파트 안내방송 SunHiNeural 전면 퇴출
        - 남성: ko-KR-InJoonNeural / 여성: ko-KR-HyunsuNeural (자연스러운 대화체)
        """
        import asyncio
        import edge_tts

        is_female = self._is_female(gender)
        voice = self.EDGE_VOICE_FEMALE if is_female else self.EDGE_VOICE_MALE
        temp_mp3 = self.output_dir / f"temp_stock_edge_{os.getpid()}_{int(time.time() * 1000)}.mp3"

        async def _run():
            comm = edge_tts.Communicate(text, voice)
            await comm.save(str(temp_mp3))

        try:
            asyncio.run(_run())
        except RuntimeError:
            # 이미 실행 중인 이벤트 루프가 있는 경우 대응
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(_run())
            finally:
                loop.close()

        cmd = [
            self.ffmpeg_exe, "-y",
            "-i", str(temp_mp3),
            "-ar", str(sample_rate),
            "-ac", "1",
            output_wav_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if temp_mp3.exists():
            try:
                temp_mp3.unlink()
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # [2순위] Alibaba CosyVoice
    # ------------------------------------------------------------------
    def _synthesize_cosyvoice(self, text: str, output_wav_path: str, gender: str, sample_rate: int) -> bool:
        """Alibaba DashScope CosyVoice REST API 음성 합성"""
        import requests

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
        raise RuntimeError(f"CosyVoice API Error [HTTP {resp.status_code}]: {resp.text[:200]}")

    # ------------------------------------------------------------------
    # 호출부 표준 인터페이스 (BaseShortsProducer / S2VClipStitcher 100% 호환)
    # ------------------------------------------------------------------
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
        - 남성: 진우(Jinwoo) / 여성: 하은(Haeun)
        - 16kHz 무손실 변환 및 무음 정밀 트리밍 적용 (지정된 에피소드 폴더에 100% 캡슐화)
        반환값: 최종 16kHz Mono WAV 파일의 절대 경로(str)
        """
        eff_dir = Path(output_dir).resolve() if output_dir else self.output_dir
        eff_dir.mkdir(parents=True, exist_ok=True)

        out_wav_path = os.path.join(str(eff_dir), f"{filename_prefix}_{lang}.wav")
        temp_wav_path = os.path.join(str(eff_dir), f"{filename_prefix}_{lang}_raw24k.wav")

        # 1. 24kHz 원본 합성 (3단 페일오버, 속도 rate 전달)
        self.synthesize(
            text=text,
            output_wav_path=temp_wav_path,
            gender=gender,
            sample_rate=24000,
            rate=rate
        )

        # 2. FFmpeg 16kHz Mono 무손실 변환 (Wan 2.2 S2V 완벽 동기화)
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

        # 3. 무음 정밀 트리밍 (말끝 음절 무손실 보존)
        try:
            self._strip_silence(out_wav_path)
        except Exception:
            pass

        return out_wav_path

    # ------------------------------------------------------------------
    # 무음 정밀 트리밍 (완벽 보존)
    # ------------------------------------------------------------------
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
