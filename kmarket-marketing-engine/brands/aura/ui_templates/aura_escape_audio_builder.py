# -*- coding: utf-8 -*-
"""
AuraEscapeAudioBuilder - 🎵 [Aura 소개팅 탈출 전화 8초 앱 시연 복합 오디오 빌더]
- 독립 레고 블록 모듈
- 1) 0.0s ~ 2.5s: 여성 주인공 안심 라운지 예약 나레이션 ("1분 뒤에 진짜 벨소리가 울려요!")
- 2) 2.5s ~ 4.5s: 실제 전화 수신 벨소리 (따르릉 진동)
- 3) 4.5s ~ 7.5s: 남성 팀장 실제 긴급 호출 음성 ("김 대리 어디야! 당장 회사로 복귀해!")
- 4) 정확히 8.0초 규격의 무결점 앱 시연 마스터 오디오 WAV 생성
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Optional
import imageio_ffmpeg

logger = logging.getLogger("AuraEscapeAudioBuilder")


class AuraEscapeAudioBuilder:
    """Aura 탈출 전화 8초 앱 씬 전용 오디오 결합기"""

    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.presets_dir = Path(__file__).parent / "presets"
        self.preset_sim_mp4 = self.presets_dir / "aura_escape_call_sim.mp4"
        self.boss_preset_mp3 = self.presets_dir / "boss.mp3"

    def build_8s_app_scene_audio(
        self,
        lead_narr_wav_path: Optional[str],
        output_wav_path: str,
        target_duration: float = 8.0
    ) -> str:
        """
        주인공 나레이션과 프리셋(벨소리 + 팀장 음성)을 8.0초 규격으로 완벽 믹싱
        """
        out_p = Path(output_wav_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        # 1. 프리셋 비디오가 존재하면 그 안의 벨소리+팀장 음원을 베이스로 사용
        if self.preset_sim_mp4.exists():
            base_audio_input = str(self.preset_sim_mp4)
            logger.info(f"🎧 [AuraEscapeAudioBuilder] 프리셋 비디오 오디오 스트림 채택: {self.preset_sim_mp4.name}")
        else:
            # 폴백: 무음 생성
            base_audio_input = None

        if lead_narr_wav_path and os.path.exists(lead_narr_wav_path) and base_audio_input:
            # 나레이션과 프리셋 오디오를 자연스럽게 믹싱
            # 나레이션은 0초부터 시작, 프리셋 오디오는 2.5초부터 벨소리/팀장음성이 나오므로
            # amix 필터로 겹침 없이 완벽하게 병합
            cmd = [
                self.ffmpeg_exe, "-y",
                "-i", base_audio_input,
                "-i", lead_narr_wav_path,
                "-filter_complex",
                f"[1:a]volume=1.1,atrim=0:2.8,apad=whole_dur={target_duration:.2f}[a_narr];"
                f"[0:a]volume=1.0,atrim=0:{target_duration:.2f},apad=whole_dur={target_duration:.2f}[a_preset];"
                f"[a_narr][a_preset]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a_out]",
                "-map", "[a_out]",
                "-ac", "1",
                "-ar", "44100",
                "-t", str(target_duration),
                str(out_p)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            logger.info(f"✨ [AuraEscapeAudioBuilder] 8초 복합 오디오 합성 성공 (나레이션+벨소리+팀장): {out_p.name}")
            return str(out_p)
        elif base_audio_input:
            # 프리셋 오디오만 추출
            cmd = [
                self.ffmpeg_exe, "-y",
                "-i", base_audio_input,
                "-vn",
                "-ac", "1",
                "-ar", "44100",
                "-t", str(target_duration),
                str(out_p)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return str(out_p)
        elif lead_narr_wav_path and os.path.exists(lead_narr_wav_path):
            # 나레이션만 패딩
            cmd = [
                self.ffmpeg_exe, "-y",
                "-i", lead_narr_wav_path,
                "-af", f"apad=whole_dur={target_duration:.2f}",
                "-ac", "1",
                "-ar", "44100",
                "-t", str(target_duration),
                str(out_p)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return str(out_p)
        else:
            raise FileNotFoundError("오디오 소스를 찾을 수 없습니다.")
