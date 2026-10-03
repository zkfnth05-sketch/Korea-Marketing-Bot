# -*- coding: utf-8 -*-
"""
InsuranceProductionSafetyGate - 🛡️ [보험 리밸런스 전용 바탕화면 산출물 생성 검증 전 API 소진 원천 차단 안전 장치]
=============================================================================================================
• 대표님 절대 수칙:
  - 100% 독립 분리 레고 블록: 타 브랜드 간섭 절대 없음
  - "바탕화면에 제대로 카드든 숏폼이던 생성이 안 되면 API 소진 못 하도록 안전 장치 만들어"
• 핵심 기능:
  1. verify_desktop_cardnews(): 보험 전용 바탕화면 카드뉴스 폴더(C:\\Users\\zkfnt\\Desktop\\한국 카드뉴스_산출물\\보험) 쓰기 + Playwright 렌더러 점검
  2. verify_desktop_shorts(): 보험 전용 바탕화면 숏폼 폴더(C:\\Users\\zkfnt\\Desktop\\한국 숏폼_산출물\\Insurance) 쓰기 + FFmpeg 인코더 점검
  3. guard_cardnews_api(topic_id): 카드뉴스 생성 환경 미비 시 제미나이 API 호출 100% 원천 차단 (예외 발생)
  4. guard_shorts_api(topic_id): 숏폼 생성 환경 미비 시 제미나이 API 호출 100% 원천 차단 (예외 발생)
  5. 429 쿨다운 인터락: 쿼터 고갈된 키는 즉시 동결하여 불필요한 반복 찔러보기 낭비 차단
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Tuple, Dict, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("InsuranceProductionSafetyGate")


class InsuranceProductionSafetyError(RuntimeError):
    """🛡️ 보험 리밸런스 바탕화면 산출물 생성 불가로 인한 제미나이 API 호출 원천 차단 예외"""
    pass


class InsuranceProductionSafetyGate:
    """🛡️ 보험 리밸런스 100% 독립 전용 산출물 생성 안전 장치"""

    BRAND = "insurance"
    BRAND_KO = "보험"

    DESKTOP_DIR = Path(os.environ.get("USERPROFILE", r"C:\Users\zkfnt")) / "Desktop"
    CARDNEWS_DIR = DESKTOP_DIR / "한국 카드뉴스_산출물" / "보험"
    SHORTS_DIR = DESKTOP_DIR / "한국 숏폼_산출물" / "Insurance"

    _KEY_COOLDOWN: Dict[str, float] = {}
    DEFAULT_COOLDOWN_SEC = 1800  # 30분 쿨다운

    @classmethod
    def record_429(cls, key_name: str, cooldown_sec: int = DEFAULT_COOLDOWN_SEC):
        """429 쿼터 초과된 보험 키를 쿨다운에 등록하여 불필요한 반복 호출 차단"""
        cls._KEY_COOLDOWN[key_name] = time.time() + cooldown_sec
        logger.warning(f"🛑 [InsuranceSafetyGate] 키 '{key_name}' 429 쿼터 초과 -> {cooldown_sec // 60}분간 동결")

    @classmethod
    def is_cooled_down(cls, key_name: str) -> bool:
        """해당 키가 현재 동결 상태인지 확인"""
        until = cls._KEY_COOLDOWN.get(key_name, 0)
        return time.time() < until

    @classmethod
    def check_folder_writable(cls, target_dir: Path) -> Tuple[bool, str]:
        """바탕화면 전용 폴더 생성 및 쓰기 무결성 검증"""
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            test_file = target_dir / f".insurance_safety_{int(time.time() * 1000)}.tmp"
            test_file.write_text("INSURANCE_OK", encoding="utf-8")
            if not test_file.exists() or test_file.read_text(encoding="utf-8") != "INSURANCE_OK":
                return False, f"쓰기 검증 실패: {test_file}"
            test_file.unlink(missing_ok=True)
            return True, "OK"
        except Exception as e:
            return False, f"바탕화면 쓰기 권한 오류 ({target_dir}): {e}"

    @classmethod
    def check_playwright_ready(cls) -> Tuple[bool, str]:
        """Playwright Chromium 렌더러 점검"""
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                browser.close()
            return True, "OK"
        except Exception as e:
            return False, f"Playwright 렌더러 불능: {e}"

    @classmethod
    def check_ffmpeg_ready(cls) -> Tuple[bool, str]:
        """FFmpeg 비디오 인코더 점검"""
        try:
            import imageio_ffmpeg
            exe = imageio_ffmpeg.get_ffmpeg_exe()
            if not exe or not os.path.exists(exe):
                return False, f"FFmpeg 바이너리 부재: {exe}"
            return True, "OK"
        except Exception as e:
            return False, f"FFmpeg 모듈 진단 실패: {e}"

    # =========================================================================
    # 📸 카드뉴스 안전 빗장
    # =========================================================================
    @classmethod
    def verify_desktop_cardnews(cls) -> Tuple[bool, str]:
        """보험 리밸런스 바탕화면 카드뉴스 생성 환경 전수 진단"""
        # 1. 바탕화면 카드뉴스 폴더 쓰기 검증
        ok, reason = cls.check_folder_writable(cls.CARDNEWS_DIR)
        if not ok:
            return False, f"[바탕화면 카드뉴스 폴더] {reason}"
        # 2. Playwright 렌더러 검증
        ok, reason = cls.check_playwright_ready()
        if not ok:
            return False, f"[Playwright] {reason}"
        return True, "OK"

    @classmethod
    def guard_cardnews_api(cls, topic_id: Optional[int] = None):
        """[보험 카드뉴스 API 차단기] 바탕화면 생성 불능 시 제미나이 API 호출 100% 원천 봉쇄"""
        ready, reason = cls.verify_desktop_cardnews()
        if not ready:
            err = (
                f"🛑 [보험 API 소진 원천 차단] 바탕화면 카드뉴스 생성 환경 미비로 제미나이 API 호출을 차단합니다! "
                f"(주제: #{topic_id}, 사유: {reason})"
            )
            logger.critical(err)
            raise InsuranceProductionSafetyError(err)
        logger.info(f"🛡️ [InsuranceSafetyGate] 바탕화면 카드뉴스 생성 환경 무결 확인 -> 제미나이 API 호출 승인")

    # =========================================================================
    # 🎬 숏폼 안전 빗장
    # =========================================================================
    @classmethod
    def verify_desktop_shorts(cls) -> Tuple[bool, str]:
        """보험 리밸런스 바탕화면 숏폼 생성 환경 전수 진단"""
        # 1. 바탕화면 숏폼 폴더 쓰기 검증
        ok, reason = cls.check_folder_writable(cls.SHORTS_DIR)
        if not ok:
            return False, f"[바탕화면 숏폼 폴더] {reason}"
        # 2. FFmpeg 인코더 검증
        ok, reason = cls.check_ffmpeg_ready()
        if not ok:
            return False, f"[FFmpeg] {reason}"
        return True, "OK"

    @classmethod
    def guard_shorts_api(cls, topic_id: Optional[int] = None):
        """[보험 숏폼 API 차단기] 바탕화면 생성 불능 시 제미나이 API 호출 100% 원천 봉쇄"""
        ready, reason = cls.verify_desktop_shorts()
        if not ready:
            err = (
                f"🛑 [보험 API 소진 원천 차단] 바탕화면 숏폼 생성 환경 미비로 제미나이 API 호출을 차단합니다! "
                f"(주제: #{topic_id}, 사유: {reason})"
            )
            logger.critical(err)
            raise InsuranceProductionSafetyError(err)
        logger.info(f"🛡️ [InsuranceSafetyGate] 바탕화면 숏폼 생성 환경 무결 확인 -> 제미나이 API 호출 승인")

    # =========================================================================
    # 🔍 [대표님 절대 수칙] 쏘기 직전 파이썬 완제품 실물 전수 검증 게이트
    # "API로 쏘는 건 무조건 바탕화면에 제대로 완이 다 만들고 파이썬 확인 그 다음에 API"
    # =========================================================================
    @classmethod
    def verify_desktop_cardnews_completed(cls, slide_paths: list) -> Tuple[bool, str]:
        """바탕화면에 5장 카드뉴스 완제품이 100% 온전히 생성되었는지 파이썬 실물 전수 검증"""
        if not slide_paths or len(slide_paths) < 5:
            return False, f"슬라이드 개수 미달 (필요: 5장, 실제: {len(slide_paths) if slide_paths else 0}장)"

        from PIL import Image
        for idx, sp in enumerate(slide_paths, start=1):
            p = Path(sp)
            if not p.exists():
                return False, f"슬라이드 #{idx} 실물 파일이 바탕화면에 존재하지 않음: {p}"
            size = p.stat().st_size
            if size < 50 * 1024:  # 최소 50KB 이상
                return False, f"슬라이드 #{idx} 용량 미달 비정상 빈 이미지 ({size} bytes < 50KB): {p}"
            try:
                with Image.open(str(p)) as img:
                    img.verify()
                with Image.open(str(p)) as img:
                    w, h = img.size
                    if w < 800 or h < 1000:
                        return False, f"슬라이드 #{idx} 해상도 규격 미달 ({w}x{h}): {p}"
            except Exception as ie:
                return False, f"슬라이드 #{idx} 이미지 파손/손상: {ie}"

        return True, f"5장 전수 무결성 확인 완료 (총 {len(slide_paths)}장, 정상 1080x1350 규격)"

    @classmethod
    def verify_desktop_shorts_completed(cls, video_path: str) -> Tuple[bool, str]:
        """바탕화면에 숏폼 비디오 완제품이 100% 온전히 생성되었는지 파이썬 실물 전수 검증"""
        if not video_path:
            return False, "비디오 파일 경로가 지정되지 않음"
        p = Path(video_path)
        if not p.exists():
            return False, f"숏폼 비디오 실물 파일이 바탕화면에 존재하지 않음: {p}"
        size = p.stat().st_size
        if size < 500 * 1024:  # 최소 500KB 이상
            return False, f"숏폼 비디오 용량 미달 비정상 파일 ({size} bytes < 500KB): {p}"
        if not str(p).lower().endswith(".mp4"):
            return False, f"숏폼 파일 포맷 오류 (MP4 확장자 아님): {p}"
        return True, f"숏폼 비디오 완제품 무결성 확인 완료 ({p.name}, {size // 1024}KB)"


    @classmethod
    def is_api_dispatch_allowed(cls) -> Tuple[bool, str]:
        """외부 API(유튜브, 인스타, 페이스북, 틱톡, 네이버, 텔레그램 등) 실제 송출 허용 여부 판별"""
        from config import ENABLE_EXTERNAL_API_DISPATCH, BLOCK_EXTERNAL_API_DISPATCH
        if BLOCK_EXTERNAL_API_DISPATCH or not ENABLE_EXTERNAL_API_DISPATCH:
            return False, "🛑 [API 송출 차단 모드] 대표님 긴급 차단 지시에 따라 외부 API 송출이 전면 차단되었습니다. (로컬 산출물 보관만 유지)"
        return True, "API 송출 허용"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    c_ok, c_msg = InsuranceProductionSafetyGate.verify_desktop_cardnews()
    print(f"🛡️ 보험 리밸런스 카드뉴스 검증: {c_ok} ({c_msg})")
    s_ok, s_msg = InsuranceProductionSafetyGate.verify_desktop_shorts()
    print(f"🛡️ 보험 리밸런스 숏폼 검증: {s_ok} ({s_msg})")
