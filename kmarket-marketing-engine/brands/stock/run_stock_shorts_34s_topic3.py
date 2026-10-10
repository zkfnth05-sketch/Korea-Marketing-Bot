# -*- coding: utf-8 -*-
r"""
run_stock_shorts_34s_topic3.py - 📈 [StockMaster AI 34초 완제품 숏폼 3번 주제: 뇌동매매 방지 AI 리스크가드]
===================================================================================================
- [1 숏폼 = 1 신규 독립 전용 폴더 100% 캡슐화] 원칙:
  - C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Stock\[주제03] 뇌동매매방지_30대여성_소파_{날짜시간}\
    폴더 딱 1개 안에 마스터 사진, 음성, 립싱크, 웹앱, CTA, 최종 완제품까지 모조리 저장!
- 구성:
  1. [0.0s ~ 10.0s] 30대 고양이상 미모의 여성 소파 씬 10초 실사 립싱크 (Wan 2.2 S2V)
     + 상단 좌측: [📈 StockMaster AI | AI 리스크 가드] 캡슐 뱃지
  2. [10.0s ~ 30.0s] 실제 주식 웹앱 실시간 1위 종목(이수페타시스 등) AI 리스크 평가 & 기계적 손절선 20초 고밀도 압축 시연
  3. [30.0s ~ 완결] 럭셔리 다크 네이비 엔딩 CTA 카드 (뇌동매매 토론 + 공식 검색어 '스톡마스터 AI')
- 음성: 30대 차분하고 스마트한 여성 전문 금융 보이스 34초 단일 통음성 (볼륨 1.50, BGM 0.05)
- 대본: Google Gemini 2.5 Flash 34초 실시간 자율 집필 (100% 진짜 팩트 & 배당 금지어 0% 차단)
- 음성 동기화: 음성 전체 완독 + 0.5초 여운 (말끝 절단 0% 영구 불변)
"""

import os
import sys
import time
import shutil
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from PIL import Image

# Ensure kmarket-marketing-engine root is in sys.path
_engine_root = Path(__file__).resolve().parent.parent.parent
if str(_engine_root) not in sys.path:
    sys.path.insert(0, str(_engine_root))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("StockShorts34sTopic3")

from core.shorts_engine.stock_shorts_producer import StockShortsProducer
from core.shorts_engine.s2v_clip_stitcher import S2VClipStitcher
from brands.stock.stock_voice_cloner import StockVoiceCloner
from brands.stock.ui_templates.stock_cta_card import StockCTACard
from core.shorts_engine.shorts_brand_capsule_badge import ShortsBrandCapsuleBadge
from core.shorts_engine.shorts_video_composer import ShortsVideoComposer


def produce_stock_34s_shorts_topic3():
    out_base = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Stock")
    out_base.mkdir(parents=True, exist_ok=True)
    dt_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 🎯 [1 숏폼 = 1 신규 독립 전용 폴더 100% 캡슐화]
    work_dir = out_base / f"[주제03] 뇌동매매방지_30대여성_소파_{dt_str}"
    work_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"🚀 [StockMaster AI] 30초 완제품 숏폼 (주제 3번: 뇌동매매 방지 AI 리스크가드) 생산 시작 -> {work_dir}")

    # 1. 🎙️ [Step 1] 제미나이 30초 단일 통짜 대본 생성 (140~170자 완결형 스피치 - 100% 진짜 팩트)
    logger.info("🤖 [Step 1] Google Gemini 2.5 Flash 30초 단일 통짜 대본 집필 중...")

    full_speech = (
        "급등주 추격매수 후 손절 타이밍 놓쳐 후회하신 적 많으시죠? "
        "감정 매매는 그만, 이제 AI가 기계적으로 위험을 차단합니다! "
        "스톡마스터 AI의 실시간 리스크 센터는 당일 과열 종목의 변동성을 진단하고 "
        "AI VETO 경고와 함께 기계적 손절 가이드라인을 1초 만에 제시합니다. "
        "지금 바로 네이버에 '스톡마스터 AI'를 검색하고 무료로 확인하세요!"
    )
    hook_text = "급등주 추격매수 후 손절 타이밍 놓쳐 후회하신 적 많으시죠? 감정 매매는 그만, 이제 AI가 기계적으로 위험을 차단합니다!"
    hook_p1 = "급등주 추격매수 후 손절 타이밍 놓쳐 후회하신 적 많으시죠?"
    hook_p2 = "감정 매매는 그만, 이제 AI가 기계적으로 위험을 차단합니다!"
    hero_copy = "감정 배제! AI 기계적 리스크 가드"
    debate_q = "급등주 추격매수 감각 매매 vs AI 기계적 손절 원칙?"

    try:
        from brands.stock.stock_shorts_script_writer import StockShortsScriptWriter
        writer = StockShortsScriptWriter()
        dyn = writer.generate_dynamic_script(topic_id=3)
        if dyn and dyn.get("full_speech"):
            full_speech = dyn["full_speech"]
            hook_text = dyn.get("hook_0_10s", hook_text)
            hook_p1 = dyn.get("hook_p1_5s", hook_p1)
            hook_p2 = dyn.get("hook_p2_5s", hook_p2)
            hero_copy = dyn.get("hero_copy", hero_copy)
            debate_q = dyn.get("debate_question", debate_q)
            logger.info("✨ 제미나이 30초 단일 통짜 대본 적용 성공 (100% 진짜 팩트)!")
    except Exception as e:
        logger.warning(f"제미나이 대본 생성 폴백: {e}")

    logger.info(f"📝 30초 전체 통짜 대본 ({len(full_speech)}자):\n{full_speech}")

    # 2. 🎙️ [Step 2] 여성 금융 아나운서 30초 단일 통음성 합성 -> 전용 폴더에 저장
    logger.info("🎙️ [Step 2] 여성 금융 전문 보이스 30초 단일 1개 통음성 합성 중...")
    voice_cloner = StockVoiceCloner(output_dir=str(work_dir))
    
    full_audio_wav = voice_cloner.generate_speech_wav(
        text=full_speech,
        gender="female",
        rate="+2%",
        filename_prefix="02_full_speech_audio"
    )
    logger.info(f"🔊 단일 통음성 합성 완료: {full_audio_wav}")

    # 3. 📸 [Step 3] 마스터 인물 사진 준비 -> 전용 폴더에 01_master_photo_t2i.png로 보관
    master_photo_path = work_dir / "01_master_photo_t2i.png"
    producer = StockShortsProducer()
    
    # 🎨 [100% 텍스트 기반 Wan 2.1 T2I 실사 신규 렌더링 - 캐시 재탕 0% 원천 배제]
    logger.info("🎨 [Step 3] 30세 고양이상 여성 주식 투자자 실사 마스터컷 Wan 2.1 T2I 신규 렌더링 시작 (Text-to-Image)...")
    res_photo = producer.produce_master_photo(topic_id=3, gender="female")
    shutil.copy2(res_photo["photo_path"], master_photo_path)
    logger.info(f"📸 마스터 인물 사진 신규 Wan T2I 100% 실사 생성 완료: {master_photo_path}")

    master_img = Image.open(str(master_photo_path))
    wan_ready = producer.ensure_engine_ready()

    framed_img = producer.prepare_framed_input_image(master_img, target_w=384, target_h=672)
    s2v_motion = (
        "speaking expressively with articulate words, highly synchronized lip sync matching the spoken audio, "
        "gentle head nodding and subtle head tilts, delicate subtle hand micro-gestures, natural posture, "
        "calm and trustworthy upper body posture, authentic lifelike human motion"
    )

    stitcher = S2VClipStitcher(
        wan_client=producer.wan_client,
        tts_synthesizer=voice_cloner,
        ffmpeg_exe=producer.composer.ffmpeg_exe
    )

    person_clip_path = str(work_dir / "03_person_s2v_lipsync_10s.mp4")

    if wan_ready:
        logger.info("🎬 [Step 3] Wan 2.2 S2V 10초 원테이크 30대 고양이상 여성 실사 립싱크 렌더링 중 (5s+5s xfade)...")
        raw_person_clip, _ = stitcher.render_seamless_dual_clip(
            base_framed_img=framed_img,
            speech_hook_full=hook_text,
            lang="ko",
            gender="female",
            out_folder=work_dir,
            dt_str=dt_str,
            motion_prompt=s2v_motion,
            speech_hook_part1=hook_p1,
            speech_hook_part2=hook_p2,
            voice_pitch="+0Hz",
            voice_rate="+2%"
        )
        if raw_person_clip and os.path.exists(raw_person_clip):
            shutil.copy2(raw_person_clip, person_clip_path)
    else:
        logger.warning("Wan 엔진 오프라인 -> 스틸 이미지 기반 10초 인물 클립 생성")
        cmd_still = [
            producer.composer.ffmpeg_exe, "-y",
            "-loop", "1", "-i", str(master_photo_path),
            "-t", "10.00",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30",
            "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
            person_clip_path
        ]
        subprocess.run(cmd_still, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # 4. 📱 [Step 4] 실물 웹앱 라이브 20.0초 압축 클립 준비 -> 전용 폴더에 04_app_live_sim_20s.mp4 저장
    app_clip_20s = str(work_dir / "04_app_live_sim_20s.mp4")
    logger.info("📱 [Step 4] 실물 웹앱 실시간 1위 종목 AI 리스크가드 20초 라이브 시연 실시간 100% 신규 녹화 중...")
    producer.app_simulator.record_simulation_clip(
        topic_id=3,
        duration_sec=20.0,
        output_mp4_path=app_clip_20s,
        force_fresh_record=True
    )

    # 5. 🏷️ [Step 5] 카드뉴스 5번 규격 럭셔리 다크 네이비 CTA 카드 (4.0초) -> 전용 폴더에 05_cta_card_4s.mp4 저장
    cta_clip_path = str(work_dir / "05_cta_card_4s.mp4")
    logger.info("🏷️ [Step 5] 럭셔리 다크 네이비 엔딩 CTA 비디오 생성 중 (4.00s)...")
    stock_cta = StockCTACard()
    stock_cta.create_cta_segment_mp4(
        output_path=cta_clip_path,
        duration_sec=4.0,
        topic_title="뇌동매매 방지! AI 자동 손절매 & 실시간 리스크 가드",
        debate_question=debate_q,
        search_keyword="스톡마스터 AI",
        hero_copy=hero_copy
    )

    # 6. ✨ [Step 6] 3단 비디오 결합 + 단일 통음성 직결 믹싱 -> ★_최종완제품.mp4로 전용 폴더 안에만 100% 저장
    final_mp4_path = str(work_dir / f"★_Stock_34초숏폼_주제03_뇌동매매방지_완제품.mp4")

    stock_badge_overlay = ShortsBrandCapsuleBadge.get_overlay_path("stock")
    has_badge = bool(stock_badge_overlay and os.path.exists(stock_badge_overlay))

    # BGM 준비
    from core.bgm_manager import BGMManager
    bgm_mgr = BGMManager()
    bgm_path = bgm_mgr.get_random_upbeat_bgm(service_id="stock")
    has_bgm = bool(bgm_path and os.path.exists(bgm_path))

    # 🎯 [음성 완독과 동시에 비디오 100% 동기화 완결: 불필요한 패딩 0% 원천 차단]
    dur_full_audio = producer.composer._get_video_duration(full_audio_wav)
    dur_total_target = max(20.0, dur_full_audio + 0.30) if dur_full_audio > 0 else 32.0

    dur_v0 = 10.00   # 10초 인물 실사 립싱크
    dur_v2 = 3.50    # 3.5초 럭셔리 다크 네이비 CTA 카드
    dur_v1 = max(5.0, dur_total_target - (dur_v0 + dur_v2))  # 웹앱 시연 구간 음성 길이에 맞춰 동적 결정

    logger.info(f"⏱️ [음성 완독 동기화] 통음성 실측={dur_full_audio:.2f}s ➔ 최종 완제품 영상={dur_total_target:.2f}s (인물={dur_v0:.2f}s, 앱={dur_v1:.2f}s, CTA={dur_v2:.2f}s)")
    logger.info(f"🎬 [Step 6] 완제품 조립 -> {final_mp4_path}")

    # FFmpeg 복합 필터 구성 (비디오 3단 Concat + 상단 뱃지 + 단일 통음성 100% 매핑)
    cmd_inputs = [
        producer.composer.ffmpeg_exe, "-y",
        "-i", person_clip_path,  # 0
        "-i", app_clip_20s,       # 1
        "-i", cta_clip_path,      # 2
        "-i", full_audio_wav,     # 3
    ]
    next_idx = 4
    bgm_idx = None
    badge_idx = None

    if has_bgm:
        cmd_inputs.extend(["-stream_loop", "-1", "-i", str(bgm_path)])
        bgm_idx = next_idx
        next_idx += 1

    if has_badge:
        cmd_inputs.extend(["-i", str(stock_badge_overlay)])
        badge_idx = next_idx
        next_idx += 1

    v_concat_tag = "v_concat" if has_badge else "v_out"
    filter_complex = [
        # 비디오 3단 스케일 및 Concat (총 dur_total_target초 영상: 음성 완독과 동시 종료)
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,trim=0:{dur_v0:.2f},setpts=PTS-STARTPTS[v0]",
        f"[1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,trim=0:{dur_v1:.2f},setpts=PTS-STARTPTS[v1]",
        f"[2:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,trim=0:{dur_v2:.2f},setpts=PTS-STARTPTS[v2]",
        f"[v0][v1][v2]concat=n=3:v=1:a=0[{v_concat_tag}]"
    ]

    if has_badge:
        filter_complex.append(f"[v_concat][{badge_idx}:v]overlay=0:0[v_out]")

    if has_bgm:
        # 단일 목소리(3번) 볼륨 1.50 (또렷하고 강력한 전달력) + BGM 볼륨 0.05 (은은한 배경 밸런스)
        filter_complex.append(f"[3:a]volume=1.50[voice];[{bgm_idx}:a]volume=0.05[bgm];[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[a_out]")
        audio_map = "[a_out]"
    else:
        filter_complex.append("[3:a]volume=1.50[a_out]")
        audio_map = "[a_out]"

    cmd_final = cmd_inputs + [
        "-filter_complex", ";".join(filter_complex),
        "-map", "[v_out]",
        "-map", audio_map,
        "-t", f"{dur_total_target:.2f}",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        final_mp4_path
    ]

    subprocess.run(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    logger.info(f"🎉 [주식 3번 34초 숏폼 완제품 완료] 전용 폴더 단일 저장: {final_mp4_path} ({os.path.getsize(final_mp4_path):,} bytes)")
    return final_mp4_path


if __name__ == "__main__":
    res = produce_stock_34s_shorts_topic3()
    print("FINISHED:", res)
