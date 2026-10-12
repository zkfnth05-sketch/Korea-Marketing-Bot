# -*- coding: utf-8 -*-
"""
================================================================================
📱 [Core Mobile] PC 렌더링 동영상 -> 스마트폰(Galaxy S10) 자동 전송 및 미디어 동기화 모듈
================================================================================
- PC 렌더링 산출물 폴더에서 브랜드별 최신 MP4 동영상을 자동 감지
- ADB를 통해 스마트폰 사진첩(/sdcard/DCIM/Camera/)으로 초고속 전송
- touch 명령어로 mtime(수정시간)을 현재 시각으로 갱신하여 갤러리 최상단 1순위 정렬 보장
- MediaScanner 브로드캐스트로 안드로이드 갤러리 즉시 색인 완결
================================================================================
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

# 한글 입출력 보장
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent

# ADB 경로
ADB_PATH = PROJECT_ROOT / "tools" / "platform-tools" / "adb.exe"

# PC 숏폼 산출물 기본 경로
DEFAULT_DESKTOP_OUTPUT_DIR = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물")


def run_adb(*args) -> str:
    """ADB 명령어 동기 실행"""
    cmd = [str(ADB_PATH)] + list(args)
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return res.stdout.strip()


def get_latest_rendered_video(brand: str) -> Optional[Path]:
    """
    브랜드별 PC 최신 렌더링 영상 검색
    1. C:\\Users\\zkfnt\\Desktop\\한국 숏폼_산출물\\{brand}
    2. kmarket-marketing-engine/outputs/{brand}
    """
    candidates = []

    # 1. 바탕화면 산출물 폴더 (재귀 검색)
    desktop_brand_dir = DEFAULT_DESKTOP_OUTPUT_DIR / brand
    if desktop_brand_dir.exists():
        for f in desktop_brand_dir.glob("**/*.mp4"):
            if "temp_" not in f.name and "backup" not in str(f).lower():
                candidates.append(f)

    # 2. 프로젝트 내부 outputs 폴더
    project_output_dir = PROJECT_ROOT / "outputs" / brand.lower()
    if project_output_dir.exists():
        for f in project_output_dir.glob("**/*.mp4"):
            if "temp_" not in f.name and "backup" not in str(f).lower():
                candidates.append(f)

    if not candidates:
        return None

    # 완성본 숏폼 우선 및 최신 수정 시간 기준 내림차순 정렬
    candidates.sort(key=lambda x: (1 if "숏폼" in x.name else 0, x.stat().st_mtime), reverse=True)
    return candidates[0]


def sync_video_to_phone(
    brand: str = "Aura",
    local_video_path: Optional[Path] = None,
    remote_filename: Optional[str] = None
) -> Dict[str, Any]:
    """
    PC의 최신 동영상을 스마트폰 /sdcard/DCIM/Camera/ 로 전송하고 미디어 색인
    """
    print(f"\n📡 [스마트폰 동영상 Sync] '{brand}' 최신 영상 모바일 전송 시작...")

    if not ADB_PATH.exists():
        return {
            "success": False,
            "error": f"ADB 실행 파일을 찾을 수 없습니다: {ADB_PATH}"
        }

    # 영상 파일 확인
    if local_video_path is None:
        local_video_path = get_latest_rendered_video(brand)

    if local_video_path is None or not Path(local_video_path).exists():
        return {
            "success": False,
            "error": f"전송할 {brand} 동영상 파일을 찾을 수 없습니다."
        }

    target_local = Path(local_video_path)
    if not remote_filename:
        # 기본 파일명: {Brand}_latest_shorts.mp4
        remote_filename = f"{brand}_latest_shorts.mp4"

    remote_path = f"/sdcard/DCIM/Camera/{remote_filename}"

    print(f"  - 원본 PC 파일: {target_local} ({target_local.stat().st_size / (1024*1024):.2f} MB)")
    print(f"  - 스마트폰 대상 경로: {remote_path}")

    # 1. 디바이스 연결 확인
    devices = run_adb("devices")
    if "device" not in devices.replace("List of devices attached", "").strip():
        return {
            "success": False,
            "error": "연결된 안드로이드 기기가 없습니다."
        }

    # 2. ADB push 파일 전송
    push_out = run_adb("push", str(target_local), remote_path)
    print(f"  - 전송 결과: {push_out}")

    # 3. mtime을 현재 시각으로 갱신 (갤러리 최상단 정렬을 위한 필수 처리)
    run_adb("shell", "touch", remote_path)

    # 4. MediaScanner로 갤러리 색인 브로드캐스트
    scan_uri = f"file://{remote_path}"
    run_adb("shell", "am", "broadcast", "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE", "-d", scan_uri)
    time.sleep(1.0)

    print(f"✅ [동기화 완료] 스마트폰 갤러리 최상단에 '{remote_filename}' 등록 완료!\n")
    return {
        "success": True,
        "local_path": str(target_local),
        "remote_path": remote_path,
        "remote_filename": remote_filename
    }


if __name__ == "__main__":
    res = sync_video_to_phone("Aura")
    print(res)
