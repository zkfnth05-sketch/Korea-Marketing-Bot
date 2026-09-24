# -*- coding: utf-8 -*-
"""
AuraSubtitlesAudioBuilder - 🎵 [Aura 4개국어 실시간 자막 영상통화 7초 앱 시연 복합 오디오 빌더]
- 독립 레고 블록 모듈
- 1) 0.0s ~ 1.8s: 통화 발신/연결 차임벨음 + "통화가 연결되었습니다"
- 2) 1.8s ~ 4.6s: 나나미(Nanami) 고유 일본어 음성 ("Nanami: 韓国に遊びに行きたい！")
- 3) 4.6s ~ 7.0s: 실시간 자막 통역 효과음 및 감탄 반응
- 4) 정확히 7.0초 규격의 무결점 앱 시연 마스터 오디오 WAV 생성
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Optional
import imageio_ffmpeg

logger = logging.getLogger("AuraSubtitlesAudioBuilder")


class AuraSubtitlesAudioBuilder:
    """Aura 실시간 자막 영상통화 7초 앱 씬 전용 오디오 결합기"""

    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.presets_dir = Path(__file__).parent / "presets"
        self.preset_sim_mp4 = self.presets_dir / "aura_subtitles_call_sim.mp4"

    def build_7s_app_scene_audio(
        self,
        lead_narr_wav_path: Optional[str] = None,
        output_wav_path: str = "aura_subtitles_audio_7s.wav",
        target_duration: float = 7.0
    ) -> str:
        """
        주인공 도입 나레이션과 프리셋(연결음 + 나나미 일본어 보이스)을 7.0초 규격으로 완벽 믹싱
        """
        out_p = Path(output_wav_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        if not self.preset_sim_mp4.exists():
            raise FileNotFoundError(f"❌ Aura 자막 통화 프리셋 비디오가 존재하지 않습니다: {self.preset_sim_mp4}")

        base_audio_input = str(self.preset_sim_mp4)
        logger.info(f"🎧 [AuraSubtitlesAudioBuilder] 프리셋 비디오 오디오 스트림 채택: {self.preset_sim_mp4.name}")

        if lead_narr_wav_path and os.path.exists(lead_narr_wav_path):
            # 도입 나레이션이 있는 경우 0초부터 2초까지 나레이션 후 자연스럽게 프리셋 오디오와 블렌딩
            cmd = [
                self.ffmpeg_exe, "-y",
                "-i", base_audio_input,
                "-i", lead_narr_wav_path,
                "-filter_complex",
                f"[1:a]volume=1.0,atrim=0:2.0,apad=whole_dur={target_duration:.2f}[a_narr];"
                f"[0:a]volume=1.1,atrim=0:{target_duration:.2f},apad=whole_dur={target_duration:.2f}[a_preset];"
                f"[a_narr][a_preset]amix=inputs=2:duration=first:dropout_transition=2[a_out]",
                "-map", "[a_out]",
                "-t", str(target_duration),
                str(out_p)
            ]
        else:
            # 프리셋 비디오 자체의 오디오 스트림 추출
            cmd = [
                self.ffmpeg_exe, "-y",
                "-i", base_audio_input,
                "-t", str(target_duration),
                "-c:a", "pcm_s16le",
                str(out_p)
            ]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        logger.info(f"✨ [AuraSubtitlesAudioBuilder] 7.0초 앱 시연 마스터 오디오 완성: {out_p.name}")
        return str(out_p)
