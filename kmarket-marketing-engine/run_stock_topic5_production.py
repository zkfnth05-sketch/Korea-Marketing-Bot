# -*- coding: utf-8 -*-
"""
run_stock_topic5_production.py
- StockMaster AI [주제 05] KOSPI 시장 종합 스트레스 센터 & 환율/금리 리포트 숏폼 풀 프로덕션
- 아우라 1번 인물(28세 여성, 2.0m 오피스 데스크, 3D 조명) Wan 2.1 마스터 사진 적용
- 제미나이 32초 팩트 통대본 (195~215자, +2% 속도)
- Wan 2.2 S2V 10.0초 원테이크 립싱크
- Playwright 실시간 웹앱 라이브 녹화 (시장 스트레스 & 4대 매크로 ➔ Live News 탭 클릭 & 뉴스 피드 스크롤)
- 실시간 트렌드 해시태그 결합 SNS 포스팅 가이드 자동 발행
"""
import os
import sys
import json
import time
import asyncio
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from PIL import Image

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("StockTopic5Production")

import edge_tts
import imageio_ffmpeg

from core.shorts_engine.stock_shorts_producer import StockShortsProducer
from core.shorts_engine.stock_app_recorder import StockAppRecorder
from brands.stock.ui_templates.stock_cta_card import StockCTACard
from core.shorts_engine.shorts_brand_capsule_badge import ShortsBrandCapsuleBadge
from core.bgm_manager import BGMManager
from brands.stock.stock_realtime_data_fetcher import StockRealtimeDataFetcher
from brands.stock.stock_shorts_script_writer import StockShortsScriptWriter

async def generate_tts_wav(text: str, voice: str, rate: str, output_wav: str):
    """Edge-TTS 고음질 음성 생성 후 16kHz mono WAV 변환"""
    ff_exe = imageio_ffmpeg.get_ffmpeg_exe()
    temp_mp3 = Path(output_wav).with_suffix(".temp.mp3")
    comm = edge_tts.Communicate(text, voice, rate=rate)
    await comm.save(str(temp_mp3))
    
    cmd = [
        ff_exe, "-y",
        "-i", str(temp_mp3),
        "-ar", "16000",
        "-ac", "1",
        output_wav
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    if temp_mp3.exists():
        temp_mp3.unlink()

def run_production():
    dt_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Stock") / f"[주제05] KOSPI_시장스트레스_20대여성_{dt_str}"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"📂 [Stock 숏폼 5번] 작업 디렉터리: {out_dir}")
    
    producer = StockShortsProducer()
    wan_ready = producer.ensure_engine_ready()
    if not wan_ready:
        raise RuntimeError("❌ ComfyUI GPU 엔진 기동 실패")
    logger.info("✅ [ComfyUI GPU 엔진] 100% 준비 완료")
    ff_exe = producer.composer.ffmpeg_exe
    
    # -------------------------------------------------------------
    # 1. 제미나이 32초 팩트 통대본 생성 (글자수 195~215자)
    # -------------------------------------------------------------
    logger.info("🤖 [Step 1] 제미나이 2.5 Flash 실시간 시장 스트레스 & 매크로 팩트 대본 집필 중...")
    script_writer = StockShortsScriptWriter()
    dynamic_script = script_writer.generate_dynamic_script(topic_id=5)
    
    if not dynamic_script:
        # 안전한 고품질 골든 대본 (196자, +2% 기준 32.5초 완벽 싱크)
        logger.info("📋 골든 팩트 대본 적용 (200자)")
        hook_p1 = "연일 출렁이는 코스피 시장, 지금 구간 안전할까요?"
        hook_p2 = "스톡마스터 AI 시장 종합 스트레스 센터가 1초 만에 진단합니다!"
        app_speech = (
            "스톡마스터 AI 앱 최상단에서 시장 종합 스트레스 지수와 원달러 환율, "
            "미국채 10년물 금리 등 4대 매크로 계량 지표를 실시간으로 스캔합니다. "
            "실시간 라이브 뉴스 탭으로 시장의 돌발 악재와 호재까지 한눈에 점검하세요."
        )
        cta_speech = "지금 바로 네이버에 스톡마스터 AI를 검색하고 무료로 확인하세요!"
    else:
        hook_p1 = dynamic_script["hook_p1_5s"]
        hook_p2 = dynamic_script["hook_p2_5s"]
        app_speech = dynamic_script["app_10_20s"]
        cta_speech = dynamic_script["cta_18_22s"]
        logger.info(f"✨ 제미나이 대본 생성 성공: {len(hook_p1 + hook_p2 + app_speech + cta_speech)}자")

    hook_speech = f"{hook_p1} {hook_p2}"
    full_speech = f"{hook_p1} {hook_p2} {app_speech} {cta_speech}"
    
    logger.info(f"📝 [대본 전문 ({len(full_speech)}자)]:\n{full_speech}")
    
    # -------------------------------------------------------------
    # 2. 고음질 통음성 합성 (+2% 속도)
    # -------------------------------------------------------------
    logger.info("🎙️ [Step 2] 여성 아나운서 음성 (+2%) 합성 중...")
    full_wav_path = str(out_dir / "02_full_speech_audio_ko.wav")
    hook_wav_path = str(out_dir / "02_hook_audio_10s.wav")
    
    # 여성 보이스 (SunHi: 부드럽고 명확한 아나운서)
    voice_name = "ko-KR-SunHiNeural"
    asyncio.run(generate_tts_wav(full_speech, voice_name, "+2%", full_wav_path))
    asyncio.run(generate_tts_wav(hook_speech, voice_name, "+2%", hook_wav_path))
    
    dur_full_audio = producer.composer._get_video_duration(full_wav_path)
    dur_hook_audio = producer.composer._get_video_duration(hook_wav_path)
    logger.info(f"🔊 통음성 실측 길이: {dur_full_audio:.2f}초 / 훅 길이: {dur_hook_audio:.2f}초")
    
    # -------------------------------------------------------------
    # 3. 마스터 사진 로드 (앞서 생성한 5번 마스터 사진 사용)
    # -------------------------------------------------------------
    logger.info("🖼️ [Step 3] 아우라 1번 인물(28세 여성) 2.0m 오피스 3D조명 마스터 사진 준비...")
    prev_master_photo = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Stock\Topic_05_KOSPI시장종합스트레스센터&환율-금리리포트\master_t2i_05_seed156159063.png")
    master_save_path = out_dir / "01_master_t2i_05.png"
    
    if prev_master_photo.exists():
        img = Image.open(str(prev_master_photo))
        img.save(str(master_save_path))
        logger.info(f"✅ 기존 생성된 마스터 사진 복사 완료: {master_save_path}")
    else:
        logger.info("🎨 마스터 사진 새로 생성 중 (Wan 2.1 T2I)...")
        photo_res = producer.produce_master_photo(topic_id=5, seed=156159063)
        img = Image.open(photo_res["photo_path"])
        img.save(str(master_save_path))
    
    # -------------------------------------------------------------
    # 4. Wan 2.2 S2V 10.0초 원테이크 립싱크 렌더링
    # -------------------------------------------------------------
    logger.info("🎬 [Step 4] Wan 2.2 S2V 10.0초 원테이크 립싱크 렌더링 (5s + 5s xfade)...")
    framed_img = producer.prepare_framed_input_image(img, target_w=384, target_h=672)
    s2v_motion = (
        "speaking expressively with articulate words, highly synchronized lip sync matching the spoken audio, "
        "gentle head nodding and subtle head tilts, calm composed upper body posture, authentic lifelike human motion"
    )
    
    person_clip_path, person_audio_path = producer.stitcher.render_seamless_dual_clip(
        base_framed_img=framed_img,
        speech_hook_full=hook_speech,
        lang="ko",
        gender="female",
        out_folder=out_dir,
        dt_str=dt_str,
        motion_prompt=s2v_motion,
        seed=156159063,
        speech_hook_part1=hook_p1,
        speech_hook_part2=hook_p2,
        voice_pitch="+0Hz",
        voice_rate="+2%"
    )
    logger.info(f"✅ 인물 10초 립싱크 클립 완성: {person_clip_path}")
    
    # -------------------------------------------------------------
    # 5. Playwright 실시간 웹앱 라이브 시연 녹화
    # -------------------------------------------------------------
    dur_person = 10.00
    dur_cta = 3.00
    dur_app = max(18.0, dur_full_audio - dur_person - dur_cta + 0.5)
    logger.info(f"📱 [Step 5] 실시간 웹앱 5번 주제 라이브 시연 녹화 중 (목표 길이: {dur_app:.2f}초)...")
    
    app_clip_path = str(out_dir / "04_app_live_sim_topic5.mp4")
    recorder = StockAppRecorder()
    recorder.record_simulation_clip(
        topic_id=5,
        duration_sec=dur_app,
        output_mp4_path=app_clip_path,
        force_fresh_record=True
    )
    logger.info(f"✅ 웹앱 시연 클립 완성: {app_clip_path}")
    
    # -------------------------------------------------------------
    # 6. 네이버 검색 CTA 카드 생성 (3.0초)
    # -------------------------------------------------------------
    logger.info("🏷️ [Step 6] CTA 카드 비디오 생성 중 (3.0초)...")
    cta_clip_path = str(out_dir / "05_cta_card.mp4")
    cta = StockCTACard()
    cta.create_cta_segment_mp4(
        output_path=cta_clip_path,
        duration_sec=dur_cta,
        topic_title="KOSPI 시장 종합 스트레스 센터 & 환율·금리 리포트",
        debate_question="코스피 현 구간, 반등 랠리 vs 하방 압력?",
        search_keyword="스톡마스터 AI",
        hero_copy="시장 종합 스트레스 10점 척도 & 4대 매크로 실시간 진단"
    )
    logger.info(f"✅ CTA 카드 완성: {cta_clip_path}")
    
    # -------------------------------------------------------------
    # 7. FFmpeg 최종 완제품 결합 (인물 10초 + 웹앱 20초 + CTA 3초 = 약 33초)
    # -------------------------------------------------------------
    logger.info("✨ [Step 7] 1080x1920 세로 풀HD 완제품 최종 합성 중...")
    final_mp4_path = str(out_dir / "★_Stock_33초숏폼_주제05_시장스트레스_완제품.mp4")
    
    badge_overlay = ShortsBrandCapsuleBadge.get_overlay_path("stock")
    has_badge = bool(badge_overlay and os.path.exists(badge_overlay))
    
    bgm_mgr = BGMManager()
    bgm_path = bgm_mgr.get_random_upbeat_bgm(service_id="stock")
    has_bgm = bool(bgm_path and os.path.exists(bgm_path))
    
    total_video_target = dur_full_audio + 0.3
    dur_app_exact = total_video_target - dur_person - dur_cta
    
    inputs = [
        ff_exe, "-y",
        "-i", person_clip_path,
        "-i", app_clip_path,
        "-i", cta_clip_path,
        "-i", full_wav_path
    ]
    
    filter_complex = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,trim=duration={dur_person}[v0];"
        f"[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,trim=duration={dur_app_exact:.2f}[v1];"
        f"[2:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,trim=duration={dur_cta}[v2];"
        f"[v0][v1][v2]concat=n=3:v=1:a=0[v_concat];"
    )
    
    if has_badge:
        inputs.extend(["-i", badge_overlay])
        filter_complex += "[v_concat][4:v]overlay=40:80[v_out];"
    else:
        filter_complex += "[v_concat]null[v_out];"
        
    if has_bgm:
        inputs.extend(["-i", bgm_path])
        filter_complex += (
            f"[3:a]volume=1.50[a_voice];"
            f"[5:a]volume=0.05,aloop=loop=-1:size=2e+09[a_bgm];"
            f"[a_voice][a_bgm]amix=inputs=2:duration=first:dropout_transition=2[a_out]"
        )
    else:
        filter_complex += "[3:a]volume=1.50[a_out]"
        
    cmd_final = inputs + [
        "-filter_complex", filter_complex,
        "-map", "[v_out]",
        "-map", "[a_out]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", f"{total_video_target:.2f}",
        final_mp4_path
    ]
    
    res = subprocess.run(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if res.returncode != 0:
        raise RuntimeError(f"최종 합성 실패 (FFmpeg error)")
        
    logger.info(f"🎉 [성공] 완제품 생성 완료: {final_mp4_path}")
    
    # -------------------------------------------------------------
    # 8. 실시간 트렌드 해시태그 SNS 포스팅 가이드 생성
    # -------------------------------------------------------------
    logger.info("📋 [Step 8] 실시간 트렌드 해시태그 SNS 포스팅 가이드 작성...")
    hashtags = [
        "#스톡마스터AI", "#주식마스터AI", "#코스피", "#코스닥", "#주식시황",
        "#환율", "#금리", "#시장종합스트레스지수", "#거시경제", "#매크로분석",
        "#LiveNews", "#실시간뉴스", "#AI주식", "#주식초보", "#주식투자",
        "#증시전망", "#재테크", "#손절라인", "#10분전광판"
    ]
    
    guide_content = f"""[StockMaster AI 숏폼 SNS 포스팅 가이드 - 주제 05]
================================================================================
■ 영상 제목: [주식속보] 코스피 시장 종합 스트레스 지수 & 4대 매크로 실시간 진단!
■ 숏폼 타깃: 국내 주식 투자자, 거시경제 및 시장 위험 구간 팩트체크를 원하는 투자자
■ 공식 검색어: 스톡마스터 AI (네이버 검색)
■ 공식 랜딩 URL: https://stockmaster-ai.vercel.app/

--------------------------------------------------------------------------------
[1. 쇼츠 / 릴스 / 틱톡 본문 캡션 원고]
--------------------------------------------------------------------------------
연일 출렁이는 코스피 시장, 지금 구간 진입해도 안전할까요? 🤔
스톡마스터 AI 앱에서 '시장 종합 스트레스 지수 10점 척도'와 
원/달러 환율, 미국 10년물 국채 금리, 유가 등 4대 매크로 지표를 실시간 1초 만에 확인하세요! 📈

💡 실시간 Live News 탭으로 시장의 돌발 악재와 호재까지 한눈에 점검!
👉 네이버에 '스톡마스터 AI'를 검색해보세요!

--------------------------------------------------------------------------------
[2. 실시간 트렌드 해시태그]
--------------------------------------------------------------------------------
{' '.join(hashtags)}

--------------------------------------------------------------------------------
[3. 대본 전문 (32초 완독)]
--------------------------------------------------------------------------------
{full_speech}
================================================================================
"""
    guide_path = out_dir / "[SNS포스팅가이드]_주제05_시장종합스트레스.txt"
    guide_path.write_text(guide_content, encoding="utf-8")
    logger.info(f"✅ SNS 가이드 저장: {guide_path}")
    
    return {
        "out_dir": str(out_dir),
        "final_mp4": final_mp4_path,
        "guide_txt": str(guide_path),
        "speech": full_speech,
        "duration": total_video_target
    }

if __name__ == "__main__":
    res = run_production()
    print("FINAL_RESULT:", json.dumps(res, ensure_ascii=False, indent=2))
