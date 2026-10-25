# -*- coding: utf-8 -*-
"""
modules/drama_engine/drama_dialogue_synthesizer.py
===================================================================================================
🎙️ [DramaDialogueSynthesizer] — 20대 실사 청춘 감정 연기 2인 핑퐁 티키타카 음성 엔진
---------------------------------------------------------------------------------------------------
[대표님 엄명 & 6인 회의체 승인 규격]
1. 🚫 아파트 관리사무소 안내방송 목소리 (ko-KR-SunHiNeural) 영구 퇴출!
2. 🎙️ 1순위: Google Gemini 2.5 Flash Native Audio (극상의 인간 음성)
     - 기계음 0%, 20대 청춘의 자연스러운 호흡, 웃음기, 감정 연기 탑재
     - 여주인공: 'Aoede' (맑고 발랄한 20대 여성 아라 보이스)
     - 남주인공: 'Puck' (생생하고 자연스러운 20대 청년 보이스)
     - 9개 멀티키 자동 순환 체인으로 100% 무인 생성
3. 🛡️ 2순위: Edge-TTS 자연 대화체 비상 백업
     - 여주: 'ko-KR-HyunsuNeural' (자연스러운 20대 대화체, rate="+8%", pitch="+1Hz")
     - 남주: 'ko-KR-InJoonNeural' (rate="+6%", pitch="+0Hz")
4. 🛠️ FFmpeg / FFprobe 바이너리 탐색(imageio_ffmpeg) 및 오디오 길이 3단 측정 탑재
5. ⏱️ [오디오 종료 시점 칼전환] 대사가 끝나는 그 순간 비디오도 칼같이 끝난다
     - atempo 배속 단독 적용 — atrim 뒷말 절단 영구 제거
     - 실측 conformed_dur 를 duration_sec 로 기록하여 stitcher 에 동적 전파
     - "말하는 거에 영상을 맞춘다" — 영상 길이를 음성 종료 시점에 100% 일치
6. 🚀 [SHORTS_SPEECH_SPEED = 1.20] 숏폼 최적 1.2배속 고정 (대표님 확정 명령)
     - "완이 81프레임까지 만드는데... 105프레임 125프레임 129프레임을 어떻게 소화하냐고...
        말하는 속도 1.2배로 만들어봐"
     - 모든 컷 오디오를 atempo=1.20 으로 일정하고 찰지게 정규화한다.
     - 1.2배속이면 8초 대사가 6.67초로 줄어 Wan S2V 81프레임(5.06초) 상한 안에 수렴한다.
     - ⚠️ atrim 절단 필터는 절대 사용 금지! 대사가 온전히 끝날 때까지 재생하고,
          변환된 실제 길이(conformed_dur)를 그대로 반환한다.
7. 🎵 [CONFORM_PRESERVE_NATURAL] 자연 발화 속도 보존 모드 (기본 OFF — 1.2배속 고정이 우선)
     - True 로 전환하면 배속을 일절 적용하지 않고 원본 발화 속도를 100% 보존한다.
     - False(기본) 이면 SHORTS_SPEECH_SPEED(1.20) 고정 배속이 적용된다.

🚨 [대표님 절대 규격 — 컷별 화자 100% 단일화]
  한 컷 안에서 남녀가 섞여 발화하면 단일 얼굴로 립싱크하는 S2V 엔진 특성상
  반드시 성별 불일치(남자가 말하는데 여자가 립싱크)가 발생한다.
  따라서 컷(cut) 단위로는 반드시 '한 명의 화자'만 발화하도록 강제하며,
  컷 객체의 speaker_gender 를 최우선 신뢰하여 보이스를 결정한다.
    · cut1 : female (여주인공)  · cut2 : male (남주인공)
    · cut3 : female (여주인공)  · cut4 : female (여주인공)
===================================================================================================
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("DramaDialogueSynthesizer")

# 비상 Edge-TTS 20대 자연 대화체 성우 (관리소 SunHi 영구 퇴출)
DEFAULT_EDGE_VOICES = {
    "female": "ko-KR-HyunsuNeural",
    "male": "ko-KR-InJoonNeural",
}

# Gemini 2.5 Flash Native Audio 보이스 매핑
GEMINI_VOICES = {
    "female": "Aoede",
    "male": "Puck",
}

# 대화 턴 간 호흡 간격 (초)
TURN_GAP_SEC: float = 0.2
BYTES_PER_SECOND_128KBPS: float = 16000.0

# ⏱️ [목표 시간 정규화 규격]
CONFORM_TOLERANCE_SEC: float = 0.15      # 목표 대비 허용 오차 (이내면 원본 유지)
CONFORM_SPEED_MIN: float = 0.85          # atempo 최소 배속 (0.5 미만 불가 → 안전 하한)
CONFORM_SPEED_MAX: float = 1.35          # atempo 최대 배속 (2.0 초과 불가 → 안전 상한)

# 🚀 [숏폼 최적 말하는 속도 1.2배속 고정 — 대표님 확정 명령]
#   "완이 81프레임까지 만드는데... 105프레임 125프레임 129프레임을 어떻게 소화하냐고...
#    말하는 속도 1.2배로 만들어봐"
#   → 모든 컷 오디오를 atempo=1.20 으로 일정하고 찰지게 정규화한다.
#   → 1.2배속이면 8초 대사가 6.67초로 줄어 Wan S2V 81프레임(5.06초) 상한 안에 수렴한다.
#   ⚠️ atrim 절단 필터는 절대 사용 금지 — 대사가 온전히 끝날 때까지 재생한다.
SHORTS_SPEECH_SPEED: float = 1.20

# 🎵 [자연 발화 속도 100% 보존 모드]
#   False(기본) → SHORTS_SPEECH_SPEED(1.20) 고정 배속 적용  ← 대표님 확정 명령
#   True        → 배속을 일절 적용하지 않고 원본 TTS 의 자연스러운 호흡/억양을 그대로 살린다.
CONFORM_PRESERVE_NATURAL: bool = False

# 🎬 4컷 기본 타임라인 (초) — 컷 순서 고정 (참고용, 실제 길이는 오디오 실측이 결정)
DEFAULT_CUT_TIMELINE: Dict[str, float] = {
    "cut1": 3.0,
    "cut2": 6.0,
    "cut3": 7.0,
    "cut4": 4.0,
}


class DramaDialogueSynthesizer:
    """4컷 숏드라마 전용 남녀 대화형 다인칭 음성 합성 및 자막 생성 엔진"""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\drama_cache")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ffmpeg_exe = self._resolve_ffmpeg()
        self.ffprobe_exe = self._resolve_ffprobe(self.ffmpeg_exe)

        # 🎙️ 1순위: Gemini 2.5 Flash Native Audio 합성기 지연 로드
        self._gemini_tts = None
        self._init_gemini_tts()

    def _init_gemini_tts(self) -> None:
        try:
            from core.shorts_engine.gemini_tts_synthesizer import GeminiTTSSynthesizer
            self._gemini_tts = GeminiTTSSynthesizer()
            logger.info("🎙️ [DramaTTS] Google Gemini 2.5 Flash Native Audio 9키 체인 연동 완료 (Aoede/Puck)")
        except Exception as exc:
            logger.warning(f"⚠️ [DramaTTS] GeminiTTSSynthesizer 로드 실패, Edge-TTS 비상 모드로 대기: {exc}")
            self._gemini_tts = None

    def _resolve_ffmpeg(self) -> str:
        try:
            import imageio_ffmpeg
            bundled = imageio_ffmpeg.get_ffmpeg_exe()
            if bundled and Path(bundled).exists():
                return str(bundled)
        except Exception:
            pass
        which_path = shutil.which("ffmpeg")
        if which_path:
            return which_path
        return "ffmpeg"

    def _resolve_ffprobe(self, ffmpeg_exe: str) -> str:
        which_probe = shutil.which("ffprobe")
        if which_probe:
            return which_probe
        return "ffprobe"

    # ==========================================================================
    # 🎯 [화자 단일화] 컷 대사에서 화자 성별을 1명으로 확정
    # ==========================================================================
    def parse_dialogue_turns(self, dialogue_text: str) -> List[Dict[str, str]]:
        """'A: 첫번째 대사 / B: 두번째 대사' 형식의 텍스트를 화자별 턴으로 분할한다."""
        turns: List[Dict[str, str]] = []
        parts = re.split(r"[\n/]+", dialogue_text)
        current_speaker = "female"

        for raw_part in parts:
            part = raw_part.strip()
            if not part:
                continue

            if part.startswith("A:") or part.startswith("여:") or part.startswith("여자:"):
                current_speaker = "female"
                text = re.sub(r"^(A|여|여자)\s*:\s*", "", part).strip()
            elif part.startswith("B:") or part.startswith("남:") or part.startswith("남자:"):
                current_speaker = "male"
                text = re.sub(r"^(B|남|남자)\s*:\s*", "", part).strip()
            else:
                text = part

            if text:
                turns.append({"speaker": current_speaker, "text": text})

        if not turns and dialogue_text.strip():
            turns.append({"speaker": "female", "text": dialogue_text.strip()})

        return turns

    @staticmethod
    def _strip_speaker_prefix(text: str) -> str:
        """'A: ...' / 'B: ...' / '여: ...' / '남: ...' 등 화자 접두어를 제거한다."""
        return re.sub(r"^\s*(A|B|여|남|여자|남자)\s*:\s*", "", str(text or "")).strip()

    def resolve_cut_speaker(self, cut: Dict[str, Any], lead_gender: str = "female") -> str:
        """
        컷 객체에서 화자 성별을 1명으로 확정한다.
        우선순위: cut['speaker_gender'] → cut['visual']['speaker_gender'] → lead_gender → 'female'
        """
        for candidate in (
            cut.get("speaker_gender"),
            (cut.get("visual") or {}).get("speaker_gender") if isinstance(cut.get("visual"), dict) else None,
        ):
            if isinstance(candidate, str) and candidate.lower().strip() in ("female", "male"):
                return candidate.lower().strip()

        fallback = (lead_gender or "female").lower().strip()
        return fallback if fallback in ("female", "male") else "female"

    def synthesize_dialogue(
        self,
        dialogue_text: str,
        output_filename: str,
        lead_gender: str = "female",
        force_speaker: Optional[str] = None,
    ) -> Tuple[Path, float]:
        """
        2인 핑퐁 대화를 화자별로 합성하고 결합하여 최종 MP3 파일과 재생 시간을 반환한다.

        Args:
            dialogue_text: 대사 텍스트
            output_filename: 출력 파일명
            lead_gender: 기본 리드 성별
            force_speaker: 지정 시 해당 컷의 모든 턴을 이 성별 1명으로 강제 단일화 (컷별 화자 100% 단일화)
        """
        turns = self.parse_dialogue_turns(dialogue_text)

        # 🎯 컷별 화자 100% 단일화 — force_speaker 지정 시 전 턴을 단일 화자로 고정
        if force_speaker in ("female", "male"):
            merged_text = " ".join(self._strip_speaker_prefix(t["text"]) for t in turns if t.get("text")).strip()
            if not merged_text:
                merged_text = self._strip_speaker_prefix(dialogue_text)
            turns = [{"speaker": force_speaker, "text": merged_text}]
            logger.info(f"🎯 [DramaTTS] 컷 화자 단일화 강제 적용 → {force_speaker} (턴 {len(turns)}개)")

        out_final = self.output_dir / output_filename
        temp_files: List[Path] = []

        try:
            for idx, turn in enumerate(turns):
                speaker = turn["speaker"]
                text = turn["text"]
                temp_wav = self.output_dir / f"temp_{output_filename}_{idx}_{speaker}.wav"

                success = False
                # ── [1순위: Google Gemini 2.5 Flash Native Audio] ────────────────
                if self._gemini_tts is not None:
                    v_name = GEMINI_VOICES.get(speaker, GEMINI_VOICES["female"])
                    try:
                        self._gemini_tts.synthesize(text, str(temp_wav), voice_name=v_name)
                        if temp_wav.exists() and temp_wav.stat().st_size > 1000:
                            success = True
                            logger.info(f"✨ [Gemini 2.5 Audio] 턴 #{idx+1} '{v_name}' 초실사 감정 연기 합성 성공: '{text[:25]}...'")
                    except Exception as exc:
                        logger.warning(f"⚠️ [Gemini 2.5 Audio] 합성 실패, Edge-TTS로 페일오버: {exc}")

                # ── [2순위: Edge-TTS 자연 대화체 (관리소 SunHi 배제)] ──────────
                if not success:
                    voice = DEFAULT_EDGE_VOICES.get(speaker, DEFAULT_EDGE_VOICES.get(lead_gender, DEFAULT_EDGE_VOICES["female"]))
                    rate = "+8%" if speaker == "female" else "+6%"
                    pitch = "+1Hz" if speaker == "female" else "+0Hz"
                    logger.info(f"🎙️ [Edge-TTS 비상] 턴 #{idx+1} ({speaker} -> {voice}): '{text[:25]}...'")
                    asyncio.run(self._synthesize_single_edge_tts(text, voice, temp_wav, rate=rate, pitch=pitch))

                temp_files.append(temp_wav)

            if len(temp_files) == 1:
                # 단일 파일 mp3 변환
                self._convert_to_mp3(temp_files[0], out_final)
            elif len(temp_files) > 1:
                self._concat_audio_files(temp_files, out_final)
            else:
                raise ValueError("합성할 대사 턴이 비어 있습니다.")

            duration = self._get_audio_duration(out_final)
            logger.info(f"✅ [DramaTTS] 대화 결합 완결: {out_final.name} (길이: {duration:.2f}초)")
            return out_final, duration

        finally:
            for tf in temp_files:
                if tf.exists() and tf != out_final:
                    try:
                        tf.unlink()
                    except Exception:
                        pass

    async def _synthesize_single_edge_tts(
        self, text: str, voice: str, out_path: Path, rate: str = "+8%", pitch: str = "+1Hz"
    ) -> Path:
        """Edge-TTS 비동기 합성 (속도/피치 미세 튜닝)"""
        import edge_tts
        temp_mp3 = out_path.with_suffix(".mp3")
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
        await communicate.save(str(temp_mp3))
        # wav 형식 요구 시 변환
        if out_path.suffix.lower() == ".wav":
            self._convert_to_wav(temp_mp3, out_path)
            if temp_mp3.exists():
                temp_mp3.unlink()
        return out_path

    def _convert_to_mp3(self, src_path: Path, dst_path: Path) -> None:
        cmd = [self.ffmpeg_exe, "-y", "-i", str(src_path), "-c:a", "libmp3lame", "-b:a", "192k", str(dst_path)]
        subprocess.run(cmd, capture_output=True, check=False)

    def _convert_to_wav(self, src_path: Path, dst_path: Path) -> None:
        cmd = [self.ffmpeg_exe, "-y", "-i", str(src_path), "-ar", "24000", "-ac", "1", str(dst_path)]
        subprocess.run(cmd, capture_output=True, check=False)

    def _concat_audio_files(self, file_paths: List[Path], output_path: Path) -> None:
        """FFmpeg filter_complex concat으로 다중 오디오 무손실 결합"""
        inputs = []
        filter_parts = []
        for i, p in enumerate(file_paths):
            inputs.extend(["-i", str(p)])
            filter_parts.append(f"[{i}:a]")

        filter_str = "".join(filter_parts) + f"concat=n={len(file_paths)}:v=0:a=1[aout]"
        cmd = [
            self.ffmpeg_exe, "-y",
            *inputs,
            "-filter_complex", filter_str,
            "-map", "[aout]",
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            str(output_path),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        if res.returncode != 0:
            logger.error(f"❌ [DramaTTS] 오디오 결합 실패: {res.stderr}")
            raise RuntimeError(f"FFmpeg 결합 오류: {res.stderr[:200]}")

    def _get_audio_duration(self, audio_path: Path) -> float:
        """ffprobe -> ffmpeg time= 파싱 -> 파일크기 3단 안전 측정"""
        if not audio_path.exists():
            return 3.0

        # 1차 ffprobe
        try:
            probe_cmd = [
                self.ffprobe_exe, "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(audio_path),
            ]
            res = subprocess.run(probe_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
            if res.returncode == 0 and res.stdout.strip():
                return float(res.stdout.strip().splitlines()[0])
        except Exception:
            pass

        # 2차 ffmpeg time= 파싱
        try:
            decode_cmd = [self.ffmpeg_exe, "-i", str(audio_path), "-f", "null", "-"]
            decode_res = subprocess.run(decode_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
            matches = re.findall(r"time=(\d+):(\d+):(\d+\.\d+)", decode_res.stderr or "")
            if matches:
                h, m, s = matches[-1]
                return int(h) * 3600 + int(m) * 60 + float(s)
        except Exception:
            pass

        # 3차 파일 크기 환산
        try:
            return max(0.5, os.path.getsize(audio_path) / BYTES_PER_SECOND_128KBPS)
        except Exception:
            return 3.0

    # ==========================================================================
    # ⏱️ [1.2배속 고정 정규화] 컷 오디오를 숏폼 최적 속도로 일정하게 변환
    # ==========================================================================
    def _conform_audio_duration(
        self,
        audio_path: Path,
        target_duration: float,
        output_path: Path,
        speed_override: Optional[float] = None,
    ) -> Tuple[Path, float]:
        """
        오디오를 숏폼 최적 속도로 정규화한다.

        [2026-10-23 변주 패치] speed_override 파라미터 추가:
          - 기본값(None): SHORTS_SPEECH_SPEED(1.20) 상수 적용 (기존 동작 유지)
          - 명시 지정 시: 해당 배속으로 오버라이드 (DailyVariationPlanner 연동)
          - 범위 클램핑: max(0.5, min(2.0, speed_override))

        🚀 [SHORTS_SPEECH_SPEED = 1.25 기본 — 일일 변주 1.20~1.30 범위]
          · ⚠️ atrim 절단 필터는 절대 사용하지 않는다 — 대사가 온전히 끝날 때까지 재생.
          · 변환 후 실측 길이(conformed_dur)를 그대로 반환한다.

        🎵 [CONFORM_PRESERVE_NATURAL = True — 선택 모드]
          배속을 일절 적용하지 않고 원본 발화 속도를 100% 보존하며 raw_dur 를 그대로 반환한다.

        Args:
            audio_path: 원본 오디오 경로
            target_duration: 목표 재생 시간 (초) — 참고용 (배속 고정 모드에서는 무시됨)
            output_path: 정규화 결과 저장 경로
            speed_override: 명시적 atempo 배속 (None 이면 SHORTS_SPEECH_SPEED 사용)

        Returns:
            (정규화된 파일 경로, 실측 duration)
        """
        audio_path = Path(audio_path)
        output_path = Path(output_path)

        # ── 0단계: 원본 존재 확인 ───────────────────────────────────────────
        if not audio_path.exists():
            logger.error(f"❌ [Conform] 원본 오디오 없음: {audio_path}")
            return audio_path, 0.0

        # ── 1단계: raw duration 측정 ────────────────────────────────────────
        raw_dur = self._get_audio_duration(audio_path)

        # ══════════════════════════════════════════════════════════════════════
        # 🎵 [자연 발화 속도 100% 보존 모드] — 배속 비틀기 전면 금지 (선택)
        # ══════════════════════════════════════════════════════════════════════
        if CONFORM_PRESERVE_NATURAL:
            if audio_path.resolve() != output_path.resolve():
                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(audio_path), str(output_path))
                    logger.info(
                        f"🎵 [Conform:자연보존] 배속 미적용 · 원본 발화 속도 100% 유지 → 복사: "
                        f"{output_path.name} (실측 {raw_dur:.2f}s / 참고목표 {target_duration}s)"
                    )
                    return output_path, raw_dur
                except Exception as exc:
                    logger.warning(f"⚠️ [Conform:자연보존] 복사 실패, 원본 경로 반환: {exc}")
                    return audio_path, raw_dur
            logger.info(
                f"🎵 [Conform:자연보존] 배속 미적용 · 원본 발화 속도 100% 유지: "
                f"{audio_path.name} (실측 {raw_dur:.2f}s / 참고목표 {target_duration}s)"
            )
            return audio_path, raw_dur

        # ══════════════════════════════════════════════════════════════════════
        # 🚀 [배속 고정 모드] — 기본 1.25배, 일일 변주 1.20~1.30
        #    speed_override 지정 시 해당 값 우선 적용
        #    atempo 단독 적용. atrim 절단 필터 절대 금지.
        # ══════════════════════════════════════════════════════════════════════
        if speed_override is not None:
            speed = float(speed_override)
        else:
            speed = float(SHORTS_SPEECH_SPEED)
        if speed <= 0.0:
            speed = 1.25
        # atempo 허용 범위(0.5~2.0) 안전 클램핑
        speed = max(0.5, min(2.0, speed))

        output_path.parent.mkdir(parents=True, exist_ok=True)

        filter_chain = f"atempo={speed:.2f}"

        cmd = [
            self.ffmpeg_exe, "-y",
            "-i", str(audio_path),
            "-filter:a", filter_chain,
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            str(output_path),
        ]
        res = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False
        )

        if res.returncode != 0 or not output_path.exists() or output_path.stat().st_size <= 0:
            logger.error(f"❌ [Conform] FFmpeg 배속 정규화 실패 (rc={res.returncode}): {(res.stderr or '')[:300]}")
            return audio_path, raw_dur

        conformed_dur = self._get_audio_duration(output_path)
        logger.info(
            f"🚀 [Conform:{speed:.2f}배속] 정규화 완료(무절단): {output_path.name} | "
            f"raw {raw_dur:.2f}s → atempo {speed:.2f} → 실측 {conformed_dur:.2f}s "
            f"(대사 끝까지 보존 · Wan S2V 81프레임 상한 대응)"
        )
        return output_path, conformed_dur

    def synthesize_4cut_audio(
        self,
        cuts: List[Dict[str, Any]],
        prefix: str,
        lead_gender: str = "female",
        voice_speed: float = 1.25,
    ) -> Dict[str, Any]:
        """
        4개 컷 각각의 오디오를 합성하고, 타임라인 및 전체 오디오 결합본을 생성한다.
        🎯 컷별 화자 100% 단일화: cut['speaker_gender'] 를 최우선 신뢰하여 보이스를 결정한다.
        🚀 voice_speed (기본 1.25, 일일 변주 1.20~1.30) 배속으로 숏폼 최적 속도 정규화.
        """
        # 안전 클램핑: 1.20~1.30
        _speed = float(voice_speed)
        _speed = max(1.20, min(1.30, _speed))

        cut_audios: List[Dict[str, Any]] = []
        cut_files: List[Path] = []

        # 🎬 컷 순서에 따른 참고 목표 시간 (cut1=3s, cut2=6s, cut3=7s, cut4=4s)
        default_timeline: Dict[str, float] = dict(DEFAULT_CUT_TIMELINE)

        for cut in cuts:
            cut_id = cut["cut_id"]
            speech = cut["speech"]
            speaker_gender = self.resolve_cut_speaker(cut, lead_gender=lead_gender)

            cut_fn = f"{prefix}_{cut_id}.mp3"
            audio_path, duration = self.synthesize_dialogue(
                speech,
                cut_fn,
                lead_gender=lead_gender,
                force_speaker=speaker_gender,
            )

            # ── 🚀 배속 변주 정규화 (conform) ─────────────────────────────
            target_duration = float(
                cut.get("duration_sec")
                or default_timeline.get(cut_id, duration)
            )
            conformed_path = self.output_dir / f"{prefix}_{cut_id}_conformed.mp3"
            conformed_path, conformed_dur = self._conform_audio_duration(
                audio_path=audio_path,
                target_duration=target_duration,
                output_path=conformed_path,
                speed_override=_speed,
            )

            # 🎬 [오디오 종료 시점 = 비디오 종료 시점] 실측 길이를 duration_sec 로 확정 기록
            cut_audios.append({
                "cut_id": cut_id,
                "audio_path": str(conformed_path),
                "duration_sec": conformed_dur,
                "target_duration_sec": target_duration,
                "raw_duration_sec": duration,
                "speech": speech,
                "speaker_gender": speaker_gender,
                "voice_speed": _speed,
            })
            cut_files.append(conformed_path)
            logger.info(
                f"🎯 [DramaTTS] {cut_id} 화자 확정: {speaker_gender} (단일 발화) | "
                f"{_speed:.2f}배속 실측 종료 시점 {conformed_dur:.2f}s → 비디오 길이로 직결 (무절단)"
            )

        # 전체 4컷 결합본
        full_audio_path = self.output_dir / f"{prefix}_full_dialogue.mp3"
        self._concat_audio_files(cut_files, full_audio_path)
        total_dur = self._get_audio_duration(full_audio_path)

        # 자막(SRT) 파일 자동 생성
        srt_path = self._generate_srt(cut_audios, self.output_dir / f"{prefix}_subtitles.srt")

        return {
            "full_audio_path": str(full_audio_path),
            "total_duration_sec": total_dur,
            "cut_audios": cut_audios,
            "srt_path": str(srt_path),
            "voice_speed": _speed,
        }

    def _generate_srt(self, cut_audios: List[Dict[str, Any]], srt_path: Path) -> Path:
        current_time = 0.0
        lines = []
        for idx, cut in enumerate(cut_audios):
            dur = cut["duration_sec"]
            start_tc = self._format_timestamp(current_time)
            end_tc = self._format_timestamp(current_time + dur)
            lines.append(f"{idx + 1}")
            lines.append(f"{start_tc} --> {end_tc}")
            lines.append(cut["speech"])
            lines.append("")
            current_time += dur
        srt_path.write_text("\n".join(lines), encoding="utf-8")
        return srt_path

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
