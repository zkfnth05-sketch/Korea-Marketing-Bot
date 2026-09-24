# -*- coding: utf-8 -*-
"""
AuraShortsProducer - 💖 [Aura 데이팅 전용 AI 숏폼 영상 생산 엔진]
- EasyTaxShortsProducer의 완벽한 Wan 2.1 T2I + OpenCV 액정 매립 + Wan 2.2 S2V 립싱크 아키텍처 100% 동일 계승
- [1단계] Wan 2.1 T2I 마스터 인물 컷 생성 (스마트폰 액정을 정면으로 들고 입을 다문 채 미소 짓는 2030 모델)
- [2단계] Aura 8대 킬러 주제 UI 생성 및 PhoneScreenEmbedder 액정 정밀 매립 (원근 왜곡 + 손가락 피부 보존)
- [3단계] 맞춤형 스피치 음성 합성 (Edge-TTS) & Wan 2.2 S2V 립싱크 모션 생성
- [4단계] 1080x1920 세로 풀HD 업스케일링 + 마케팅 뱃지 + 네이버 검색 공식 CTA ['아우라AI데이팅'] 결합
- 산출물 경로: C:/Users/zkfnt/Desktop/한국 숏폼_산출물/Aura
"""

import os
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image

from .base_shorts_producer import BaseShortsProducer
from brands.aura.ui_templates.aura_phone_ui_template import AuraPhoneUITemplate
from brands.aura.ui_templates.aura_app_simulator import AuraAppSimulator
from brands.aura.ui_templates.aura_cta_card import AuraCTACard
from brands.aura.ui_templates.aura_escape_audio_builder import AuraEscapeAudioBuilder
from .aura_shorts_scenario_director import AuraShortsScenarioDirector
from .shorts_character_anchor_aura import build_aura_shorts_t2i_character_prompt
from .s2v_clip_stitcher import S2VClipStitcher

logger = logging.getLogger("AuraShortsProducer")


class AuraShortsProducer(BaseShortsProducer):
    """Aura 데이팅 숏폼 자동 생산 엔진 (EasyTax 아키텍처 100% 계승)"""

    def __init__(self):
        super().__init__("Aura")
        # 사용자 명시 절대 경로: 바탕화면/한국 숏폼_산출물/Aura
        self.output_base = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Aura")
        self.output_base.mkdir(parents=True, exist_ok=True)

        self.ui_template = AuraPhoneUITemplate()
        self.app_simulator = AuraAppSimulator()
        self.escape_audio_builder = AuraEscapeAudioBuilder()
        self.cta_card = AuraCTACard()
        self.script_director = AuraShortsScenarioDirector()
        self.stitcher = S2VClipStitcher(
            wan_client=self.wan_client,
            tts_synthesizer=self.tts,
            ffmpeg_exe=self.composer.ffmpeg_exe
        )

    def get_character_prompt(
        self,
        topic_id: int = 1,
        custom_char_desc: Optional[str] = None,
        custom_bg_desc: Optional[str] = None,
        **kwargs
    ) -> Dict[str, str]:
        """Aura 8대 주제 전용 T2I 캐릭터 및 배경 프롬프트 생성"""
        return build_aura_shorts_t2i_character_prompt(
            topic_id=topic_id,
            custom_char_desc=custom_char_desc,
            custom_bg_desc=custom_bg_desc
        )

    def render_ui_image(self, lang: str = "ko", topic_id: int = 1, **kwargs) -> Image.Image:
        """Aura 스마트폰 액정 화면 렌더링"""
        return self.ui_template.render(topic_id=topic_id)

    def get_speech_script(self, lang: str = "ko", topic_id: int = 1, **kwargs) -> str:
        """Aura 맞춤형 나레이션 스크립트 반환"""
        scenario = self.script_director.get_full_scenario(topic_id=topic_id)
        return scenario["full_speech"]

    # 🔒 [대표님 지시: 2번 주제(실시간 자막 통화) 고정 생산 모드]
    # (검증 완료 후 None으로 변경하면 1~8번 자율 순환 복구)
    FIXED_TOPIC_ID: Optional[int] = 2

    def _get_next_topic_id(self) -> int:
        """1번부터 8번까지 주제를 자율 순환(Rotation)하며 상태 파일에 영구 기록"""
        # 🔒 임시 고정 모드 작동 시 항상 고정된 주제 반환
        if self.FIXED_TOPIC_ID is not None:
            logger.info(f"🔒 [Aura 숏폼] 대표님 지시로 주제 #{self.FIXED_TOPIC_ID} 임시 고정 생산 모드 가동 중")
            return self.FIXED_TOPIC_ID

        state_file = self.output_base / "aura_shorts_state.json"
        last_id = 0
        if state_file.exists():
            try:
                import json
                data = json.loads(state_file.read_text(encoding="utf-8"))
                last_id = data.get("last_topic_id", 0)
            except Exception:
                pass
        next_id = (last_id % 8) + 1
        try:
            import json
            state_file.write_text(json.dumps({"last_topic_id": next_id}, indent=2), encoding="utf-8")
        except Exception:
            pass
        return next_id

    def produce_master_photo(
        self,
        topic_id: Optional[int] = None,
        gender: Optional[str] = None,
        seed: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        r"""
        Aura 8대 주제별 Wan 2.1 순정 아이폰 실사 마스터 사진 단독 생산 파이프라인
        - ComfyUI 엔진 자동 가동 점검
        - 순정 아이폰 15 Pro 골든 프롬프트 로드
        - 832x1216 해상도 Wan 2.1 14B Q4_0 T2I 마스터컷 렌더링
        - C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Aura\Topic_XX 폴더에 저장
        - GPU VRAM 자동 정리 (100% 무인 최적화)
        """
        import random
        if topic_id is None:
            topic_id = self._get_next_topic_id()
        if seed is None or seed <= 0:
            seed = random.randint(100000, 999999999)

        wan_ready = self.ensure_engine_ready()
        if not wan_ready:
            raise RuntimeError("ComfyUI 엔진 기동에 실패했습니다. D:\\ComfyUI_Wan_Engine 설정을 확인해주세요.")

        scenario = self.script_director.get_full_scenario(topic_id=topic_id, gender=gender)
        theme_name = scenario["theme_name"]
        theme_code = scenario["theme_code"]

        t2i_prompt = self.get_character_prompt(
            topic_id=topic_id,
            custom_char_desc=kwargs.get("custom_char_desc"),
            custom_bg_desc=kwargs.get("custom_bg_desc")
        )
        pos_prompt = t2i_prompt["positive"]
        neg_prompt = t2i_prompt["negative"]

        out_folder = self.output_base / f"Topic_{topic_id:02d}_{theme_name.replace(' ', '')}"
        out_folder.mkdir(parents=True, exist_ok=True)

        logger.info(f"🎨 [Aura 마스터 사진] 주제 {topic_id} [{theme_name}] Wan 2.1 T2I 렌더링 시작 (seed={seed})")

        gen_path = self.wan_client.generate_t2i_master(
            positive_prompt=pos_prompt,
            negative_prompt=neg_prompt,
            width=832,
            height=1216,
            seed=seed,
            prefix=f"aura_master_{topic_id}"
        )
        master_img = Image.open(gen_path)
        master_save_path = out_folder / f"master_t2i_{topic_id:02d}_seed{seed}.png"
        master_img.save(str(master_save_path))

        self.wan_client.free_vram()

        logger.info(f"🎉 [Aura 마스터 사진 완료] 파일 저장: {master_save_path}")
        return {
            "topic_id": topic_id,
            "theme_name": theme_name,
            "theme_code": theme_code,
            "photo_path": str(master_save_path),
            "folder_path": str(out_folder),
            "image_size": f"{master_img.size[0]}x{master_img.size[1]}",
            "seed": seed
        }

    def produce(
        self,
        lang: Optional[str] = "ko",
        topic_id: Optional[int] = None,
        gender: Optional[str] = None,
        custom_hero_image: Optional[Image.Image] = None,
        seed: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Aura 숏폼 풀 프로덕션:
        - topic_id 미지정 시 1~8번 자율 순환
        - seed 미지정 시 완전 무작위 난수 시드 자동 발급 (매번 새로운 인물/외모)
        """
        import random
        if topic_id is None:
            topic_id = self._get_next_topic_id()
        if seed is None or seed <= 0:
            seed = random.randint(100000, 999999999)

        # 1. ComfyUI 엔진 상태 확인
        wan_ready = self.ensure_engine_ready()

        # 2. 시나리오 대본 생성
        scenario = self.script_director.get_full_scenario(topic_id=topic_id, gender=gender)
        theme_name = scenario["theme_name"]
        theme_code = scenario["theme_code"]
        effective_gender = scenario.get("gender", gender or "female")
        speech_hook = scenario["speech_hook"]
        speech_app = scenario["speech_app"]
        speech_cta = scenario["speech_cta"]
        full_speech = scenario["full_speech"]
        visual_dir = scenario["visual_direction"]

        dt_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_folder = self.output_base / f"Aura_{topic_id:02d}_{scenario.get('theme_code', 'topic')}_{dt_str}"
        out_folder.mkdir(parents=True, exist_ok=True)

        logger.info(f"🚀 [Aura 숏폼] 생산 시작: 주제 {topic_id} [{theme_name}] | 성별: {effective_gender} | seed: {seed}")

        # 3. [음성 합성] 처음부터 끝까지 단 하나의 동일한 목소리 (선희 rate=+3%, pitch=+6Hz 100% 통일)
        voice_lang = "ko"
        voice_rate = "+3%"
        voice_pitch = "+6Hz"
        logger.info(f"🎙️ [Step 1] Edge-TTS 단일 여배우 동일 목소리 합성 ({gender}, rate={voice_rate}, pitch={voice_pitch})...")
        hook_wav_path = self.tts.generate_speech_wav(
            text=speech_hook,
            lang=voice_lang,
            gender=gender,
            rate=voice_rate,
            pitch=voice_pitch,
            filename_prefix=f"aura_hook_{topic_id}_{dt_str}"
        )
        app_wav_path = self.tts.generate_speech_wav(
            text=speech_app,
            lang=voice_lang,
            gender=gender,
            rate=voice_rate,
            pitch=voice_pitch,
            filename_prefix=f"aura_app_{topic_id}_{dt_str}"
        )
        cta_wav_path = self.tts.generate_speech_wav(
            text=speech_cta,
            lang=voice_lang,
            gender=gender,
            rate=voice_rate,
            pitch=voice_pitch,
            filename_prefix=f"aura_cta_{topic_id}_{dt_str}"
        )
        full_wav_path = self.tts.generate_speech_wav(
            text=full_speech,
            lang=voice_lang,
            gender=gender,
            rate=voice_rate,
            pitch=voice_pitch,
            filename_prefix=f"aura_full_{topic_id}_{dt_str}"
        )

        # 4. [Step 2] 숏폼 인물 사진 로드 또는 Wan 2.1 T2I 생성 (순수 100% 인물 마스터컷, 인위적 액정 매립 전면 영구 박멸!)
        if custom_hero_image is not None:
            master_img = custom_hero_image
            logger.info("🌟 [Step 2] 전달받은 마스터 인물 사진 사용")
        elif wan_ready:
            t2i_prompt = self.get_character_prompt(
                topic_id=topic_id,
                custom_char_desc=scenario.get("character_desc"),
                custom_bg_desc=scenario.get("background_desc")
            )
            pos_prompt = t2i_prompt["positive"]
            neg_prompt = t2i_prompt["negative"]

            logger.info(f"🎨 [Step 2] Wan 2.1 T2I 인물 마스터 사진 생성 (seed={seed})")
            gen_path = self.wan_client.generate_t2i_master(
                positive_prompt=pos_prompt,
                negative_prompt=neg_prompt,
                width=832,
                height=1216,
                seed=seed,
                prefix=f"shorts_aura_{topic_id}"
            )
            master_img = Image.open(gen_path)
            master_save_path = out_folder / f"01_master_t2i_{topic_id}.png"
            master_img.save(str(master_save_path))
            self.wan_client.free_vram()
        else:
            raise RuntimeError("Wan 2.1 엔진이 준비되지 않았습니다.")

        # 5. [Step 3] Wan 2.2 S2V 립싱크 모션 렌더링 직결 (인위적인 스마트폰 액정 매립/합성 0% 완전 배제!)
        framed_img = self.prepare_framed_input_image(master_img, target_w=384, target_h=672)
        s2v_motion_prompt = scenario.get("s2v_motion_prompt") or (
            "The woman is clearly pronouncing words, articulate speech with natural lip movements while talking to the audience, "
            "highly synchronized lip sync matching the spoken audio, expressive mouth articulation, "
            "a beautiful 28-year-old Korean office woman sitting across a dinner table, looking directly into camera with expressive authentic eye contact, "
            "leaning forward slightly in a relaxed conversational posture, subtle natural head tilts, no phone in hand, natural lifelike motion"
        )

        if wan_ready:
            logger.info("🎬 [Step 3] Wan 2.2 S2V 384x672 5초+5초 10초 원테이크 렌더링 시작 (81프레임 x 2, 0.15s xfade)...")
            person_clip_path, person_audio_path = self.stitcher.render_seamless_dual_clip(
                base_framed_img=framed_img,
                speech_hook_full=speech_hook,
                lang=voice_lang,
                gender=gender,
                out_folder=out_folder,
                dt_str=dt_str,
                motion_prompt=s2v_motion_prompt,
                seed=seed,
                speech_hook_part1=scenario.get("speech_hook_part1"),
                speech_hook_part2=scenario.get("speech_hook_part2")
            )
        else:
            person_clip_path = str(out_folder / f"temp_person_clip_{dt_str}.mp4")
            cmd = [
                self.composer.ffmpeg_exe, "-y",
                "-loop", "1", "-i", str(master_save_path),
                "-t", "10.12",
                "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30",
                "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
                person_clip_path
            ]
            import subprocess
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            person_audio_path = hook_wav_path

        # 6. [Step 4] Aura 웹앱 시뮬레이션 고화질 직결 (동일 여배우 목소리 연속 발화)
        dur_app_audio = self.composer._get_video_duration(app_wav_path)
        app_target_dur = max(4.0, dur_app_audio + 0.1)
        app_clip_path = str(out_folder / f"04_app_sim_aura_{topic_id}.mp4")
        logger.info(f"📱 [Step 4] Aura 앱 시연 비디오 준비 (오디오 {dur_app_audio:.2f}s ➡️ 할당 {app_target_dur:.2f}s)...")
        self.app_simulator.record_simulation_clip(
            topic_id=topic_id,
            duration_sec=app_target_dur,
            output_mp4_path=app_clip_path
        )

        # 7. [Step 5] Aura 엔딩 댓글 논쟁 & 네이버 검색 공식 CTA 비디오 준비
        dur_cta_audio = self.composer._get_video_duration(cta_wav_path)
        cta_target_dur = max(2.5, dur_cta_audio + 0.3)
        cta_clip_path = str(out_folder / f"05_cta_debate_aura_{topic_id}.mp4")
        logger.info(f"🏷️ [Step 5] Aura 댓글 논쟁 & 공식 검색어 CTA 비디오 준비 ({cta_target_dur:.2f}s)...")
        self.cta_card.create_cta_segment_mp4(
            output_path=cta_clip_path,
            duration_sec=cta_target_dur,
            topic_title=theme_name,
            debate_question=scenario.get("debate_question", "여러분의 생각은 어떠신가요?"),
            search_keyword="아우라AI데이팅"
        )

        # 8. [Step 6] 22초 하이브리드 완제품 컴포징 (3단 비디오 + 3단 무결점 씬 오디오 싱크)
        final_mp4_name = f"Aura_22초숏폼_주제{topic_id:02d}_{scenario.get('theme_code', 'topic')}_{dt_str}.mp4"
        final_mp4_path = str(out_folder / final_mp4_name)

        logger.info("✨ [Step 6] 1080p 세로 풀HD 22초 하이브리드 비디오 최종 컴포징...")
        scene_audios = {
            "hook": person_audio_path,
            "app": app_wav_path,
            "cta": cta_wav_path
        }
        self.composer.compose_hybrid_22s_shorts(
            clip_person_path=person_clip_path,
            clip_app_path=app_clip_path,
            full_audio_path=full_wav_path,
            visual_direction=visual_dir,
            output_mp4_path=final_mp4_path,
            lang=voice_lang,
            scene_audios=scene_audios,
            clip_cta_path=cta_clip_path
        )

        # 9. [순수 100% 인물 클로즈업 원테이크 1080x1920 세로 풀HD 단독 완제품 생성] (자료화면/앱시뮬 0% 완전 배제)
        pure_one_take_name = f"Aura_10초_순수인물_원테이크_주제{topic_id:02d}_{scenario.get('theme_code', 'topic')}_{dt_str}.mp4"
        pure_one_take_path = str(out_folder / pure_one_take_name)
        cmd_pure = [
            self.composer.ffmpeg_exe, "-y",
            "-i", person_clip_path,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k",
            pure_one_take_path
        ]
        import subprocess
        subprocess.run(cmd_pure, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        logger.info(f"✨ [순수 인물 1080p 원테이크 완료] 저장: {pure_one_take_path}")

        logger.info(f"🎉 [Aura 숏폼 생산 완료] 완제품 저장: {final_mp4_path}")
        return {
            "topic_id": topic_id,
            "theme_name": theme_name,
            "output_mp4": final_mp4_path,
            "pure_person_mp4": pure_one_take_path,
            "output_folder": str(out_folder),
            "audio_hook": hook_wav_path,
            "audio_app": app_wav_path,
            "audio_cta": cta_wav_path,
            "audio_full": full_wav_path
        }

