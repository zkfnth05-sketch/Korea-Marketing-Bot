# -*- coding: utf-8 -*-
"""
run_stock_shorts_34s_topic6.py - 📈 [StockMaster AI 34초 완제품 숏폼 6번 주제: AI 퀀트 비서 총괄 소개]
===================================================================================================
- [1 숏폼 = 1 신규 독립 전용 폴더 100% 캡슐화] 원칙:
  - C:\\Users\\zkfnt\\Desktop\\한국 숏폼_산출물\\Stock\\[주제06] 스톡마스터AI_총괄소개_20대훈남_{날짜시간}\\
- 아우라/보험 숏폼 아키텍처 100% 레고 블록 복제:
  1. [0.0s ~ 10.0s] 20대 훈남 경제 앵커 10초 실사 인물 립싱크 / 모션 (Wan 2.2 S2V)
     + 상단 좌측: [📈 StockMaster AI | 24시 AI 퀀트 비서] 캡슐 뱃지
  2. [10.0s ~ 30.0s] 실제 주식 웹앱 실시간 계량 전광판 1위 & 리스크 센터 & AI 퀀트 분석 라이브 녹화 시연
  3. [30.0s ~ 완결] 럭셔리 다크 네이비 엔딩 CTA 카드 (찬반 토론 + 공식 검색어 '스톡마스터 AI')
- 음성: 20대 스마트 남성 전문 금융 보이스 30~34초 단일 통음성
- 대본: Google Gemini 2.5 Flash 30초 실시간 라이브 팩트 집필
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
logger = logging.getLogger("StockShorts34sTopic6")

from core.shorts_engine.stock_shorts_producer import StockShortsProducer
from core.shorts_engine.s2v_clip_stitcher import S2VClipStitcher
from brands.stock.stock_voice_cloner import StockVoiceCloner
from brands.stock.ui_templates.stock_cta_card import StockCTACard
from core.shorts_engine.shorts_brand_capsule_badge import ShortsBrandCapsuleBadge
from core.shorts_engine.shorts_video_composer import ShortsVideoComposer


def produce_stock_34s_shorts_topic6():
    out_base = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Stock")
    out_base.mkdir(parents=True, exist_ok=True)
    dt_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 🎯 [1 숏폼 = 1 신규 독립 전용 폴더 100% 캡슐화]
    work_dir = out_base / f"[주제06] 스톡마스터AI_총괄소개_20대훈남_{dt_str}"
    work_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"🚀 [StockMaster AI] 34초 완제품 숏폼 (주제 6번: AI 퀀트 비서 총괄 소개) 생산 시작 -> {work_dir}")

    # 1. 🎙️ [Step 1] 제미나이 30초 대본 생성 (100% 진짜 라이브 팩트 주입)
    logger.info("🤖 [Step 1] Google Gemini 2.5 Flash 30초 단일 통짜 대본 집필 중...")

    full_speech = (
        "10분 퀀트 스캔과 30분 AI 분석! "
        "내 손안의 24시간 실시간 AI 퀀트 비서, 스톡마스터 AI를 소개합니다. "
        "국내 350개 우량주 중 체결강도 1위 주도주와 실시간 시장 스트레스 리스크를 0.1초 만에 포착해 "
        "감정을 배제한 과학적 목표가와 손절가를 투명하게 안내합니다. "
        "지금 바로 네이버에 '스톡마스터 AI'를 검색하고 무료로 확인해보세요!"
    )
    hook_text = "10분 퀀트 스캔과 30분 AI 분석! 내 손안의 24시간 실시간 AI 퀀트 비서, 스톡마스터 AI를 소개합니다."
    hook_p1 = "10분 퀀트 스캔과 30분 AI 분석!"
    hook_p2 = "내 손안의 24시간 실시간 AI 퀀트 비서, 스톡마스터 AI를 소개합니다."
    hero_copy = "10분 퀀트 스캔 • 30분 AI 분석 24시 퀀트 비서!"
    debate_q = "감정 매매 vs 24시간 실시간 AI 퀀트 비서?"

    target_stock_name = "LG에너지솔루션"
    try:
        from brands.stock.stock_shorts_script_writer import StockShortsScriptWriter
        writer = StockShortsScriptWriter()
        dyn = writer.generate_dynamic_script(topic_id=6)
        if dyn and dyn.get("full_speech"):
            full_speech = dyn["full_speech"]
            target_stock_name = dyn.get("target_stock_name", "LG에너지솔루션")
            hook_text = dyn.get("hook_0_10s", hook_text)
            hook_p1 = dyn.get("hook_p1_5s", hook_p1)
            hook_p2 = dyn.get("hook_p2_5s", hook_p2)
            hero_copy = dyn.get("hero_copy", hero_copy)
            debate_q = dyn.get("debate_question", debate_q)
            logger.info(f"✨ 제미나이 30초 단일 통짜 대본 적용 성공 (타깃 종목: {target_stock_name})!")
    except Exception as e:
        logger.warning(f"제미나이 대본 생성 폴백: {e}")

    logger.info(f"📝 30초 전체 통짜 대본 ({len(full_speech)}자):\n{full_speech}")

    # 2. 🎙️ [Step 2] 20대 스마트 남성 금융 보이스 단일 통음성 합성
    logger.info("🎙️ [Step 2] 20대 스마트 남성 전문 금융 보이스 단일 통음성 합성 중...")
    voice_cloner = StockVoiceCloner(output_dir=str(work_dir))
    
    full_audio_wav = voice_cloner.generate_speech_wav(
        text=full_speech,
        gender="male",
        rate="+2%",
        pitch="+0Hz",
        filename_prefix="02_full_speech_audio"
    )
    logger.info(f"🔊 단일 통음성 합성 완료: {full_audio_wav}")

    producer = StockShortsProducer()

    # 음성 길이 기반 정확한 비디오 타임라인 계산
    dur_full_audio = producer.composer._get_video_duration(full_audio_wav)
    dur_total_target = max(20.0, dur_full_audio + 0.30) if dur_full_audio > 0 else 32.0

    dur_v0 = 10.00   # 10초 인물 실사 립싱크
    dur_v2 = 3.50    # 3.5초 럭셔리 다크 네이비 CTA 카드
    dur_v1 = max(5.0, dur_total_target - (dur_v0 + dur_v2))  # 웹앱 시연 구간

    logger.info(f"⏱️ [음성 완독 동기화] 통음성 실측={dur_full_audio:.2f}s ➔ 웹앱 녹화 타깃={dur_v1:.2f}s (인물={dur_v0:.2f}s, CTA={dur_v2:.2f}s, 최종영상={dur_total_target:.2f}s)")

    # 3. 📸 [Step 3] 20대 훈남 앵커 마스터 인물 사진 연결
    master_photo_path = work_dir / "01_master_photo_t2i.png"
    
    # 카드뉴스 6번 표지에서 생성한 20대 훈남 앵커 실사 사진 우선 연결
    cover_candidates = list(Path(r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\주식\[주제06] AI퀀트비서_총괄소개_20대훈남").glob("slide_1.png")) + \
                       list(Path(_engine_root / "brands/stock/assets").glob("stock_topic6_cover_*.png")) + \
                       list(Path(r"D:\ComfyUI_Wan_Engine\ComfyUI\output").glob("stock_topic6_*.png"))
    
    if cover_candidates and cover_candidates[0].exists():
        shutil.copy2(cover_candidates[0], master_photo_path)
        logger.info(f"📸 6번 주제 20대 훈남 앵커 마스터 사진 연결: {master_photo_path}")
    else:
        res_photo = producer.produce_master_photo(topic_id=6, gender="male")
        shutil.copy2(res_photo["photo_path"], master_photo_path)
        logger.info(f"📸 마스터 사진 신규 생성: {master_photo_path}")

    master_img = Image.open(str(master_photo_path))
    wan_ready = producer.ensure_engine_ready()

    framed_img = producer.prepare_framed_input_image(master_img, target_w=384, target_h=672)
    s2v_motion = (
        "professional Korean male economic news anchor speaking articulately with confident smile, "
        "highly synchronized lip sync matching spoken audio, subtle head nodding, premium Bloomberg TV studio background, "
        "lifelike upper body posture, 4k ultra realistic"
    )

    stitcher = S2VClipStitcher(
        wan_client=producer.wan_client,
        tts_synthesizer=voice_cloner,
        ffmpeg_exe=producer.composer.ffmpeg_exe
    )

    person_clip_path = str(work_dir / "03_person_s2v_lipsync_10s.mp4")

    if wan_ready:
        logger.info("🎬 [Step 3] Wan 2.2 S2V 10초 원테이크 20대 훈남 앵커 립싱크 렌더링 중 (5s+5s xfade)...")
        raw_person_clip, _ = stitcher.render_seamless_dual_clip(
            base_framed_img=framed_img,
            speech_hook_full=hook_text,
            lang="ko",
            gender="male",
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
        logger.warning("Wan 엔진 오프라인 -> 고화질 줌인 모션 10초 인물 클립 생성")
        cmd_still = [
            producer.composer.ffmpeg_exe, "-y",
            "-loop", "1", "-i", str(master_photo_path),
            "-t", "10.00",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30",
            "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
            person_clip_path
        ]
        subprocess.run(cmd_still, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # 4. 📱 [Step 4] 실물 웹앱 라이브 dur_v1초 동적 녹화 (전광판 1위 ➔ 리스크센터 ➔ AI 퀀트 모달)
    app_clip_path = str(work_dir / "04_app_live_sim.mp4")
    logger.info(f"📱 [Step 4] 실물 웹앱 {dur_v1:.2f}초 라이브 시연 실시간 100% 신규 녹화 중...")
    producer.app_simulator.record_simulation_clip(
        topic_id=6,
        duration_sec=dur_v1,
        output_mp4_path=app_clip_path,
        force_fresh_record=True,
        target_stock_name=target_stock_name
    )

    # 5. 🏷️ [Step 5] 럭셔리 다크 네이비 CTA 카드 (3.5초)
    cta_clip_path = str(work_dir / "05_cta_card_4s.mp4")
    logger.info(f"🏷️ [Step 5] 럭셔리 다크 네이비 엔딩 CTA 비디오 생성 중 ({dur_v2:.2f}s)...")
    stock_cta = StockCTACard()
    stock_cta.create_cta_segment_mp4(
        output_path=cta_clip_path,
        duration_sec=dur_v2,
        topic_title="국내 최초 자기학습 AI 퀀트 비서! Stock Master AI 총괄 소개",
        debate_question=debate_q,
        search_keyword="스톡마스터 AI",
        hero_copy=hero_copy
    )

    # 6. ✨ [Step 6] 3단 비디오 결합 + 단일 통음성 직결 믹싱 -> 완제품 MP4 출력
    final_mp4_path = str(work_dir / f"★_Stock_34초숏폼_주제06_총괄소개_완제품.mp4")

    stock_badge_overlay = ShortsBrandCapsuleBadge.get_overlay_path("stock")
    has_badge = bool(stock_badge_overlay and os.path.exists(stock_badge_overlay))

    # BGM 준비
    from core.bgm_manager import BGMManager
    bgm_mgr = BGMManager()
    bgm_path = bgm_mgr.get_random_upbeat_bgm(service_id="stock")
    has_bgm = bool(bgm_path and os.path.exists(bgm_path))

    logger.info(f"🎬 [Step 6] 완제품 조립 -> {final_mp4_path}")

    cmd_inputs = [
        producer.composer.ffmpeg_exe, "-y",
        "-i", person_clip_path,  # 0
        "-i", app_clip_path,      # 1
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
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v0]",
        f"[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v1]",
        f"[2:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v2]",
        f"[v0][v1][v2]concat=n=3:v=1:a=0[{v_concat_tag}]"
    ]

    if has_badge:
        filter_complex.append(f"[{v_concat_tag}][{badge_idx}:v]overlay=0:0[v_out]")

    if has_bgm:
        filter_complex.append(f"[3:a]volume=1.50[a_voice];[{bgm_idx}:a]volume=0.05[a_bgm];[a_voice][a_bgm]amix=inputs=2:duration=first:dropout_transition=2[a_out]")
    else:
        filter_complex.append(f"[3:a]volume=1.50[a_out]")

    cmd = cmd_inputs + [
        "-filter_complex", ";".join(filter_complex),
        "-map", "[v_out]",
        "-map", "[a_out]",
        "-t", f"{dur_total_target:.2f}",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        final_mp4_path
    ]

    logger.info(f"🔨 FFmpeg 완제품 숏폼 렌더링 명령어 실행 중...")
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)

    logger.info("=" * 70)
    logger.info(f"🎉 [StockMaster AI] 6번 주제 완제품 숏폼 생성 100% 완료: {final_mp4_path}")
    logger.info("=" * 70)

    return final_mp4_path


if __name__ == "__main__":
    produce_stock_34s_shorts_topic6()
