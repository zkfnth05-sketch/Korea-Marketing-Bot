# -*- coding: utf-8 -*-
"""
[독립 레고 블록] Aura Bridge Video Builder (💖 Aura 데이팅 전용 유튜브 직결 15초 롱폼 브릿지 영상 빌더)
=======================================================================================================
- 브랜드: Aura AI 데이팅 (공식 검색어: '아우라AI데이팅')
- 규격: 가로형 16:9 (1920x1080 Full HD, 30fps) -> 유튜브 일반 동영상 등록으로 설명란/댓글 링크 100% 활성화!
- 구성:
  1. [0~5초]: Wan 2.1 T2I 마스터컷 + Wan 2.2 S2V 립싱크 5초 실시간 신규 렌더링
              대본: "진짜 괜찮은 사람 만나고 싶죠? 프리미엄 소개팅, 아우라를 소개합니다!"
  2. [5~15초]: 3번 주제(50:50 황금 성비 VIP 게이트) 앱 시뮬레이션 (04_app_sim_aura_3.mp4)
              나레이션: "남녀 성비 50대 50 황금 정원제! 물 흐리는 사람은 걸러내고 검증된 분들만 입장합니다. 지금 바로 아래 설명란과 첫 댓글 파란 링크를 누르고, 3초 만에 무료로 입장해 보세요!"
  3. [엔딩 10~15초]: 하단 CTA 링크 유도 자막 및 고정댓글 안내
"""

import os
import sys
import time
import shutil
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import imageio_ffmpeg
from PIL import Image

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine.wan_pipeline_client import WanPipelineClient
from core.shorts_engine.shorts_character_anchor_aura import build_aura_shorts_t2i_character_prompt

OUTPUT_DIR = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Aura")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FINAL_OUTPUT_PATH = OUTPUT_DIR / "Aura_공식_앱기능소개_브릿지_15s.mp4"
FONT_PATH = "C:/Windows/Fonts/malgunbd.ttf"
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()


class AuraBridgeVideoBuilder:
    """💖 Aura 데이팅 전용 15초 가로 16:9 유튜브 브릿지 롱폼 영상 자동 렌더러"""

    def __init__(self):
        self.output_path = FINAL_OUTPUT_PATH
        self.temp_dir = CURRENT_DIR / "temp_bridge_build"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.wan_client = WanPipelineClient()

        # 대본 정의 (사용자 승인 규격)
        self.speech_part1 = "진짜 괜찮은 사람 만나고 싶죠? 프리미엄 소개팅, 아우라를 소개합니다!"
        self.speech_part2 = (
            "남녀 성비 50대 50 황금 정원제! 물 흐리는 사람은 걸러내고 검증된 분들만 입장합니다. "
            "지금 바로 아래 설명란과 첫 댓글 파란 링크를 누르고, 3초 만에 무료로 입장해 보세요!"
        )

    async def generate_tts(self, text: str, output_wav: Path, rate: str = "+3%", pitch: str = "+4Hz") -> Path:
        """Edge-TTS 고음질 20대 여성 보이스 생성"""
        import edge_tts
        voice = "ko-KR-SunHiNeural"
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await communicate.save(str(output_wav))
        return output_wav

    def find_topic3_app_sim(self) -> Path:
        """3번 주제(50:50 VIP 게이트) 앱 시뮬레이션 비디오 검색"""
        app_sim_videos = sorted(
            OUTPUT_DIR.glob("**/04_app_sim_aura_3.mp4"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        if not app_sim_videos:
            # 3번이 없으면 일반 app_sim 중 최신 검색
            app_sim_videos = sorted(
                OUTPUT_DIR.glob("**/04_app_sim_aura_*.mp4"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
        if not app_sim_videos:
            raise FileNotFoundError("앱 시뮬레이션 비디오를 찾을 수 없습니다.")
        return app_sim_videos[0]

    def render_fresh_wan_clip1(self) -> Path:
        """1단계: 1번 극상여성 Wan 2.1 T2I 마스터컷 + Wan 2.2 S2V 립싱크 5초 비디오 신규 생성"""
        print("\n" + "=" * 70)
        print("🎨 [1단계] 1번 주제 극상여성 Wan 2.1 T2I 마스터 사진 신규 생성 시작...")
        print("=" * 70)

        # 1-1. 검증된 극상여성 마스터 컷 우선 로드 (기존 생성물 재사용으로 2분 단축)
        verified_master = PROJECT_ROOT / "bridge_wan_master_fresh.png"
        if not verified_master.exists():
            verified_master = CURRENT_DIR / "bridge_wan_master_fresh.png"
        if not verified_master.exists():
            verified_master = Path(r"D:\ComfyUI_Wan_Engine\ComfyUI\output\bridge_wan_master_00001_.png")

        if verified_master.exists():
            print(f"✨ [마스터 컷 즉시 로드] 대표님 승인 검증 극상여성 마스터 사진 사용: {verified_master}")
            master_img_path = str(verified_master)
            seed = 91764295
        else:
            # T2I 프롬프트 빌드
            prompt_info = build_aura_shorts_t2i_character_prompt(topic_id=1)
            pos_prompt = prompt_info["positive"]
            neg_prompt = prompt_info["negative"]

            seed = int(time.time()) % 100000000
            master_img_path = self.wan_client.generate_t2i_master(
                positive_prompt=pos_prompt,
                negative_prompt=neg_prompt,
                width=832,
                height=1216,
                seed=seed,
                prefix="bridge_wan_master"
            )
            print(f"✅ Wan 2.1 초고화질 마스터 사진 생성 완료: {master_img_path}")

        # 1-2. Part 1 음성 합성 (5초 립싱크용)
        wav_part1 = self.temp_dir / "tts_part1.wav"
        asyncio.run(self.generate_tts(self.speech_part1, wav_part1, rate="+2%", pitch="+3Hz"))
        print(f"✅ Part 1 음성 합성 완료: {wav_part1}")

        # 1-3. ComfyUI input 폴더에 자산 복사
        comfy_input = Path(self.wan_client.comfy_input_dir)
        comfy_img_name = "bridge_input_face.png"
        comfy_audio_name = "bridge_input_audio.wav"

        # 🛡️ [종횡비 100% 보존 중앙 크롭] 원본 황금비율 보존 후 384x672 리사이즈
        img = Image.open(master_img_path).convert("RGB")
        w, h = img.size
        target_ratio = 384 / 672
        crop_w = int(h * target_ratio)
        left = max(0, (w - crop_w) // 2)
        img_cropped = img.crop((left, 0, left + crop_w, h))
        img_resized = img_cropped.resize((384, 672), Image.Resampling.LANCZOS)
        img_resized.save(comfy_input / comfy_img_name, "PNG")

        shutil.copy2(str(wav_part1), str(comfy_input / comfy_audio_name))

        # 1-4. Wan 2.2 S2V 립싱크 렌더링 (81프레임, 16fps = 약 5.06초)
        print("\n" + "=" * 70)
        print("🎬 [2단계] Wan 2.2 S2V 14B 81프레임 립싱크 모션 GPU 렌더링 시작 (비율 정상 복원)...")
        print("=" * 70)

        motion_prompt = (
            "speaking warmly and gently to the camera with delicate lip sync matching the spoken audio, "
            "subtle confident gentle smile, graceful head posture, charming trustworthy dating host, "
            "lifelike natural eye blinks, authentic mobile video portrait"
        )
        raw_s2v_output = self.temp_dir / "s2v_part1_raw.mp4"

        s2v_result_mp4 = self.wan_client.generate_s2v_video(
            image_name=comfy_img_name,
            audio_name=comfy_audio_name,
            prompt_text=motion_prompt,
            output_mp4_path=str(raw_s2v_output),
            seed=seed,
            width=384,
            height=672,
            frames=81,
            prefix="bridge_s2v"
        )
        print(f"🎉 Wan 2.2 S2V 5초 신규 비디오 렌더링 대성공: {s2v_result_mp4}")
        return Path(s2v_result_mp4)

    def get_media_duration(self, path: Path) -> float:
        """FFmpeg을 통해 오디오/비디오 파일의 정확한 재생 길이(초) 측정"""
        cmd = [FFMPEG_EXE, "-i", str(path)]
        res = subprocess.run(cmd, capture_output=True)
        out = res.stderr.decode("utf-8", errors="ignore")
        for line in out.split("\n"):
            if "Duration:" in line:
                parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        return 10.0

    def render_full_bridge_video(self) -> Dict[str, Any]:
        """Wan 5초 신규 영상 + 3번 앱 시뮬레이션 결합하여 15초 가로 16:9 브릿지 완성"""
        # 1. Wan 5초 신규 영상 렌더링
        fresh_wan_clip = self.render_fresh_wan_clip1()

        # 2. 3번 앱 시뮬레이션 소스
        app_sim_path = self.find_topic3_app_sim()
        print(f"📱 앱 기능 시뮬레이션 소스: {app_sim_path}")

        # 3. Part 2 음성 합성
        wav_part2 = self.temp_dir / "tts_part2.wav"
        asyncio.run(self.generate_tts(self.speech_part2, wav_part2, rate="+12%", pitch="+3Hz"))
        dur_part2 = self.get_media_duration(wav_part2)
        print(f"✅ Part 2 앱 소개 음성 합성 완료 ({dur_part2:.1f}초): {wav_part2}")

        font_opt = "fontfile='C\\:/Windows/Fonts/malgunbd.ttf'"

        # 4. 클립 1 렌더링 (0~5초, Wan 신규 실사 인물 + 가로 1920x1080 순수 블랙 배경 필러박스)
        clip1_mp4 = self.temp_dir / "clip1_wan_1080.mp4"
        cmd_clip1 = [
            FFMPEG_EXE, "-y", "-ss", "0", "-t", "5.0",
            "-i", str(fresh_wan_clip),
            "-filter_complex",
            f"[0:v]scale=-2:1080,pad=1920:1080:(1920-iw)/2:0:black,"
            f"drawtext={font_opt}:text='[Aura AI 데이팅] 공식 앱 기능 가이드':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=60:box=1:boxcolor=black@0.6:boxborderw=15[v]",
            "-map", "[v]", "-map", "0:a?",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-r", "30",
            "-c:a", "aac", "-b:a", "192k",
            str(clip1_mp4)
        ]
        subprocess.run(cmd_clip1, check=True)
        print("✅ 클립 1 가로 16:9 순수 블랙 배경 합성 완료!")

        # 5. 클립 2 렌더링 (5초 이후, 3번 앱 시뮬레이션 + 순수 블랙 배경 + Part 2 음성 + CTA 자막)
        clip2_video_only = self.temp_dir / "clip2_video_only.mp4"
        cta_start = max(1.0, dur_part2 - 5.0)
        cmd_clip2 = [
            FFMPEG_EXE, "-y",
            "-stream_loop", "-1", "-i", str(app_sim_path),
            "-t", f"{dur_part2:.2f}",
            "-filter_complex",
            f"[0:v]scale=-2:1080,pad=1920:1080:(1920-iw)/2:0:black,"
            f"drawtext={font_opt}:text='[핵심 기능] 남녀 50대50 황금 성비 정원제 라운지':fontcolor=white:fontsize=42:x=(w-text_w)/2:y=60:box=1:boxcolor=black@0.6:boxborderw=12,"
            f"drawtext={font_opt}:text='[공식 링크] 아래 설명란 & 첫 댓글 링크 터치! (3초 무료 입장)':fontcolor='#FFD700':fontsize=46:x=(w-text_w)/2:y=h-120:box=1:boxcolor=black@0.7:boxborderw=15:enable='between(t,{cta_start:.1f},{dur_part2:.1f})'[v]",
            "-map", "[v]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-r", "30",
            "-an", str(clip2_video_only)
        ]
        subprocess.run(cmd_clip2, check=True)

        clip2_with_audio = self.temp_dir / "clip2_with_audio.mp4"
        cmd_clip2_mux = [
            FFMPEG_EXE, "-y",
            "-i", str(clip2_video_only),
            "-i", str(wav_part2),
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(clip2_with_audio)
        ]
        subprocess.run(cmd_clip2_mux, check=True)
        print("✅ 클립 2 가로 16:9 앱 기능 소개 합성 완료!")

        # 6. 최종 Concat 병합 (15초 가로 16:9 Full HD)
        concat_txt = self.temp_dir / "concat_final.txt"
        with open(concat_txt, "w", encoding="utf-8") as f:
            f.write(f"file '{clip1_mp4.resolve()}'\n")
            f.write(f"file '{clip2_with_audio.resolve()}'\n")

        cmd_concat = [
            FFMPEG_EXE, "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_txt),
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-r", "30",
            "-c:a", "aac", "-b:a", "192k",
            str(self.output_path)
        ]
        subprocess.run(cmd_concat, check=True)
        print("=" * 70)
        print(f"🎉 [완전 완결] 15초 공식 브릿지 완제품 생성 완료: {self.output_path}")
        print("=" * 70)

        return {
            "status": "success",
            "output_path": str(self.output_path),
            "size_bytes": self.output_path.stat().st_size,
            "resolution": "1920x1080 (16:9)"
        }


if __name__ == "__main__":
    builder = AuraBridgeVideoBuilder()
    res = builder.render_full_bridge_video()
    print("Bridge Video Result:", res)


