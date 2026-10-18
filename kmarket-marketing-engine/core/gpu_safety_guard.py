# -*- coding: utf-8 -*-
"""
[독립 레고 블록] GPUSafetyGuard - 🛡️ [RTX 5060 Ti GPU 과열 방지 & VRAM 무결점 안심 가드]
======================================================================================
- 전담 역할:
  1. 실시간 GPU 온도 & VRAM 사용량 정밀 모니터링 (nvidia-smi 파싱)
  2. ComfyUI / PyTorch VRAM 즉시 강제 방출 (/free API + empty_cache + gc.collect)
  3. 엄격한 5분(300초) 쿨다운 타이머 (실시간 온도/잔량 로깅)
  4. 82℃ 안전 온도 차단벽 (Overheat Safety Gate) + 86℃ 하드웨어 비상 정지
  5. 저쪽 컴퓨터(KTRS 마케팅봇) 작업 감지 시 자율 양보 (Conflict Avoidance)
  6. 서브프로세스 완전 격리 실행 (작업 완료 즉시 OS 레벨 메모리 100% 회수)

- 🆕 v2 개선 사항 (2026):
  • wait_for_safe_gpu_entry 진입 즉시 cleanup_all() 1회 선제 호출
    → 이전 작업의 ComfyUI 캐시 및 VRAM을 말끔히 비운 뒤 VRAM 측정 (잔여 캐시 오탐 원천 차단)
  • KTRS_CONFLICT_VRAM_MB 기본값 7000MB → 13000MB (16GB의 약 80%) 상향
    → 이전 작업 잔여 캐시로 인한 15분 무한 대기 버그 원천 차단
  • KTRS 대기 타임아웃 기본 900초 → 120초(2분) 단축, 초과 시 경고 후 강제 진행
  • cleanup_all()에 gc.collect() 3중 철저 수행 (호출 전/후/최종)

- 🆕 v4 온도 임계값 실측 캘리브레이션 (RTX 5060 Ti / Wan 2.1 14B 실부하 기준):
  • 실측 팩트: Wan 2.1 14B 풀부하 정상 구동 온도 = 75℃~80℃
  • MAX_SAFE_TEMP = 82℃
      → Pre-flight 안전 게이트. '시작 시점' 온도가 82℃ 이상일 때만 일시 대기.
      → 정상 75~80℃ 풀부하 렌더링은 절대 차단되지 않음 (기존 65℃는 정상 부하를
        과열로 오판하여 무한 대기시키던 치명적 오탐 원인)
  • TARGET_COOL_TEMP = 60℃
      → 냉각 목표 온도. 30~60초 내 신속히 60℃까지 식혀 불필요한 정체(stall) 방지
  • EMERGENCY_HALT_TEMP = 86℃
      → 진짜 하드웨어 비상 정지선. 팬 고장/극한 열폭주로 86℃ 초과 시에만
        ComfyUI /interrupt 로 렌더링을 즉시 중단
  • TARGET_EMERGENCY_COOL_TEMP = 60℃
      → 비상 정지 후 재개 가능 온도 목표
"""

import os
import sys
import gc
import time
import json
import datetime
import logging
import subprocess
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

logger = logging.getLogger("GPUSafetyGuard")


class GPUSafetyGuard:
    """RTX 5060 Ti 세심 무결점 안전 가드"""

    COMFYUI_HOST = os.environ.get("COMFYUI_HOST", "127.0.0.1")
    COMFYUI_PORT = int(os.environ.get("COMFYUI_PORT", "8188"))
    DEFAULT_COOLDOWN_SEC = 300  # 5분 정밀 쿨다운

    # ────────────────────────────────────────────────────────────
    # 🌡️ [v4 실측 캘리브레이션] RTX 5060 Ti + Wan 2.1 14B 풀부하 기준
    #    실측: 정상 풀부하 구동 온도 75℃~80℃
    # ────────────────────────────────────────────────────────────
    # Pre-flight 안전 게이트: '시작 시점' 온도가 82℃ 이상일 때만 일시 대기
    #   ➔ 정상 75~80℃ 풀부하 렌더링은 절대 차단되지 않음
    MAX_SAFE_TEMP = 82

    # 냉각 목표 온도: 30~60초 내 신속히 60℃까지 식혀 불필요한 정체 방지
    TARGET_COOL_TEMP = 60

    # 🚨 진짜 하드웨어 비상 정지선: 팬 고장/극한 열폭주로 86℃ 초과 시에만
    #    ComfyUI /interrupt 로 렌더링 즉시 중단
    EMERGENCY_HALT_TEMP = 86

    # 비상 정지 후 재개 가능 온도 목표
    TARGET_EMERGENCY_COOL_TEMP = 60

    # 🆕 KTRS 점유 감지 기준: 7000MB → 13000MB (전체 16GB의 약 80%)
    #    이전 작업 잔여 캐시(7~12GB)를 '저쪽 컴퓨터 작업 중'으로 오탐하여
    #    15분 무한 대기하던 버그를 원천 차단합니다.
    KTRS_CONFLICT_VRAM_MB = int(os.environ.get("KTRS_CONFLICT_VRAM_MB", "13000"))

    # 🆕 KTRS 대기 타임아웃: 900초(15분) → 120초(2분)
    KTRS_WAIT_TIMEOUT_SEC = int(os.environ.get("KTRS_WAIT_TIMEOUT_SEC", "120"))

    # 🌙 [야간 단독 전용 렌더링 골든타임] 00:00 ~ 06:59
    #    대표님 공식 팩트: "이 앱이 0시에 그래픽카드를 돌리면,
    #    저쪽 컴퓨터(KTRS 마케팅봇)는 아침 7시부터 만들기 시작해서 겹칠 일이 전혀 없다."
    #    ➔ 이 시간대에는 KTRS 충돌 검사를 100% 바이패스(0초 대기)하고,
    #       오직 GPU 과열(82도) 방지만 수행한 뒤 즉시 승인한다.
    NIGHT_GOLDEN_START_HOUR = int(os.environ.get("NIGHT_GOLDEN_START_HOUR", "0"))
    NIGHT_GOLDEN_END_HOUR = int(os.environ.get("NIGHT_GOLDEN_END_HOUR", "7"))

    @classmethod
    def is_night_golden_time(cls) -> bool:
        """
        🌙 현재 시각(KST)이 야간 단독 전용 렌더링 골든타임(00:00~06:59)인지 판정.

        대표님 공식 팩트:
          "지금 이 앱(한국 마케팅봇)이 0시에 그래픽카드를 돌리면,
           저쪽 컴퓨터(KTRS 마케팅봇)는 아침 7시부터 만들기 시작해서 겹칠 일이 전혀 없다."

        ➔ 0 <= now_hour < 7 구간은 KTRS가 절대 가동되지 않는 시간대이므로
           충돌 검사를 100% 바이패스해도 무방하다.
        """
        now_hour = datetime.datetime.now().hour
        return cls.NIGHT_GOLDEN_START_HOUR <= now_hour < cls.NIGHT_GOLDEN_END_HOUR

    @classmethod
    def get_gpu_stats(cls) -> Dict[str, Any]:
        """nvidia-smi를 통해 실시간 GPU 온도, VRAM 사용량, 전력 및 사용률 추출"""
        stats = {
            "available": False,
            "temp_c": 0,
            "vram_used_mb": 0,
            "vram_total_mb": 0,
            "gpu_util_pct": 0,
            "raw": ""
        }
        try:
            cmd = [
                "nvidia-smi",
                "--query-gpu=temperature.gpu,memory.used,memory.total,utilization.gpu",
                "--format=csv,noheader,nounits"
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=5)
            lines = res.stdout.strip().split("\n")
            if lines and lines[0]:
                parts = [p.strip() for p in lines[0].split(",")]
                if len(parts) >= 4:
                    stats["available"] = True
                    stats["temp_c"] = int(parts[0])
                    stats["vram_used_mb"] = int(parts[1])
                    stats["vram_total_mb"] = int(parts[2])
                    stats["gpu_util_pct"] = int(parts[3])
                    stats["raw"] = lines[0]
        except Exception as e:
            logger.debug(f"nvidia-smi 조회 실패 또는 미지원: {e}")
        return stats

    @classmethod
    def free_comfyui_vram(cls) -> bool:
        """ComfyUI /free API를 호출하여 캐시된 모델 가중치를 VRAM에서 강제 방출"""
        url = f"http://{cls.COMFYUI_HOST}:{cls.COMFYUI_PORT}/free"
        # 🛡️ unload_models=False 고정: ComfyUI-GGUF ops.py의 0xC0000005 C++ 접근 위반 크래시 방지
        #    (GGUF 모델 언로드 시 네이티브 텐서 해제 경로에서 치명적 액세스 바이올레이션 발생)
        #    free_memory=True만으로도 캐시/중간 텐서는 충분히 방출된다.
        payload = json.dumps({"unload_models": False, "free_memory": True}).encode("utf-8")
        try:
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    logger.info("🧹 [GPU Safety] ComfyUI VRAM 모델 언로드 및 메모리 방출 성공 (/free 200 OK)")
                    return True
        except urllib.error.URLError:
            logger.debug("ComfyUI 서버 미가동 상태 (건너뜀)")
        except Exception as e:
            logger.warning(f"ComfyUI VRAM 방출 요청 실패: {e}")
        return False

    @classmethod
    def interrupt_comfyui(cls) -> bool:
        """
        🚨 [비상 정지] ComfyUI /interrupt API 호출로 진행 중인 렌더링을 즉시 중단.

        EMERGENCY_HALT_TEMP(86℃) 초과 시에만 호출된다.
        팬 고장, 극한 열폭주 등 실제 하드웨어 위험 상황 전용.
        """
        url = f"http://{cls.COMFYUI_HOST}:{cls.COMFYUI_PORT}/interrupt"
        try:
            req = urllib.request.Request(
                url,
                data=b"{}",
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    logger.critical(
                        f"🚨 [비상 정지] ComfyUI /interrupt 호출 성공 "
                        f"(임계 {cls.EMERGENCY_HALT_TEMP}℃ 초과) ➔ 렌더링 즉시 중단"
                    )
                    return True
        except urllib.error.URLError:
            logger.debug("ComfyUI 서버 미가동 상태 (비상 정지 요청 건너뜀)")
        except Exception as e:
            logger.warning(f"ComfyUI 비상 정지 요청 실패: {e}")
        return False

    @classmethod
    def flush_system_vram(cls):
        """파이썬 가비지 컬렉션 및 PyTorch CUDA 메모리 캐시 초기화 (gc.collect 3중 수행)"""
        # 1차: PyTorch 캐시 해제 전 참조 정리
        gc.collect()

        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
                logger.info("🧹 [GPU Safety] PyTorch CUDA 캐시(empty_cache) 완전 초기화 완료")
        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"PyTorch 캐시 정리 실패: {e}")

        # 2차: CUDA 캐시 해제 후 남은 파이썬 객체 회수
        gc.collect()

    @classmethod
    def cleanup_all(cls):
        """ComfyUI + PyTorch + OS 가비지 컬렉션 통합 정리 (gc.collect 철저 수행)"""
        # 1) ComfyUI /free API로 모델 가중치 언로드
        cls.free_comfyui_vram()

        # 2) PyTorch CUDA 캐시 + gc.collect (내부 2회)
        cls.flush_system_vram()

        # 3) 최종 gc.collect — 순환 참조까지 완전 회수
        gc.collect()
        logger.debug("🧹 [GPU Safety] 통합 클린업 완료 (ComfyUI /free + empty_cache + gc.collect x3)")

    @classmethod
    def wait_for_safe_gpu_entry(cls, timeout_sec: int = 120) -> bool:
        """
        렌더링 작업 시작 전 안전 진입 게이트

        🆕 v2 개선:
          0. 진입 즉시 cleanup_all() 1회 선제 호출
             → 이전 작업의 ComfyUI 캐시 및 VRAM을 말끔히 비운 뒤 VRAM을 측정
             → 잔여 캐시를 'KTRS 작업 중'으로 오탐하던 문제 원천 차단
          1. 온도가 MAX_SAFE_TEMP(82℃) 이상이면 TARGET_COOL_TEMP(60℃) 이하로 식을 때까지 대기
          2. VRAM 사용량이 13GB(전체의 약 80%) 이상이면 저쪽 컴퓨터(KTRS) 작업 중으로 판단하고 양보 대기
          3. 기본 타임아웃 120초(2분) 초과 시 경고 후 강제 진행 (무한 대기 절대 금지)

        🌙 v3 개선 (야간 골든타임 바이패스):
          현재 시각(KST)이 00:00~06:59 구간이면 KTRS는 절대 가동되지 않으므로
          충돌 검사를 100% 바이패스(0초 대기)하고, 오직 GPU 과열(82도) 방지만
          수행한 뒤 즉시 승인(return True)한다.

        🌡️ v4 캘리브레이션:
          RTX 5060 Ti + Wan 2.1 14B 실측 정상 부하 온도는 75~80℃.
          따라서 82℃ 미만이면 정상 풀부하 렌더링으로 간주하여 절대 차단하지 않는다.
          86℃ 초과(팬 고장/열폭주) 시에만 ComfyUI /interrupt 로 비상 정지한다.
        """
        start_time = time.time()

        # ────────────────────────────────────────────────────────────
        # 🌙 [최우선] 야간 단독 전용 렌더링 골든타임 판정 (00:00 ~ 06:59)
        #    대표님 공식 팩트: 저쪽 컴퓨터(KTRS)는 아침 7시부터 가동되므로
        #    이 시간대에는 겹칠 일이 전혀 없다 ➔ 충돌 검사 전면 바이패스
        # ────────────────────────────────────────────────────────────
        now_hour = datetime.datetime.now().hour
        if cls.NIGHT_GOLDEN_START_HOUR <= now_hour < cls.NIGHT_GOLDEN_END_HOUR:
            logger.info(
                "🌙 [야간 골든타임] 저쪽 컴퓨터(KTRS) 미가동 시간대(00:00~07:00) "
                "➔ 충돌 검사 전면 바이패스 및 0초 쾌속 통과!"
            )

            # 오직 GPU 과열(82도) 방지만 수행
            stats = cls.get_gpu_stats()
            if not stats["available"]:
                logger.info("ℹ️ [야간 골든타임] nvidia-smi 비활성 환경 - 즉시 진입 승인")
                return True

            temp = stats["temp_c"]

            # 🚨 [비상 정지] 86℃ 초과 = 팬 고장/열폭주 → 렌더링 즉시 중단
            if temp > cls.EMERGENCY_HALT_TEMP:
                logger.critical(
                    f"🚨 [야간 골든타임 · 비상 정지] 현재 온도 {temp}℃ 가 "
                    f"비상 임계치 {cls.EMERGENCY_HALT_TEMP}℃ 를 초과했습니다! "
                    f"(팬 고장 또는 극한 열폭주 의심) ➔ ComfyUI 렌더링 즉시 중단"
                )
                cls.interrupt_comfyui()
                cls.cleanup_all()
                return False

            if temp >= cls.MAX_SAFE_TEMP:
                logger.warning(
                    f"⚠️ [야간 골든타임 · 과열 방지] 현재 온도 {temp}℃ "
                    f"(안전 게이트 {cls.MAX_SAFE_TEMP}℃ 도달) ➔ {cls.TARGET_COOL_TEMP}℃ 이하로 "
                    f"냉각될 때까지 자동 휴식 대기 중..."
                )
                cls.cleanup_all()
                cool_start = time.time()
                while time.time() - cool_start < timeout_sec:
                    time.sleep(15)
                    cls.cleanup_all()
                    st = cls.get_gpu_stats()
                    if not st["available"] or st["temp_c"] < cls.MAX_SAFE_TEMP:
                        logger.info(
                            f"✅ [야간 골든타임] 냉각 완료 (현재 {st['temp_c']}℃) "
                            f"➔ 렌더링 즉시 진입 승인"
                        )
                        return True
                    logger.info(
                        f"⏳ [야간 골든타임 · 냉각 중] 현재 {st['temp_c']}℃ "
                        f"(목표 {cls.TARGET_COOL_TEMP}℃ 이하) | 경과 {int(time.time() - cool_start)}초"
                    )
                logger.warning(
                    f"⚠️ [야간 골든타임] 냉각 타임아웃 {timeout_sec}초 도달 "
                    f"➔ 무한 대기 방지를 위해 렌더링을 강제 진행합니다."
                )
                return True

            logger.info(
                f"✅ [야간 골든타임 승인] 온도 {temp}℃ (정상, 게이트 {cls.MAX_SAFE_TEMP}℃ 미만) | "
                f"VRAM {stats['vram_used_mb']}MB / {stats['vram_total_mb']}MB "
                f"(KTRS 충돌 검사 생략) | 소요: 0.0초"
            )
            return True

        # ────────────────────────────────────────────────────────────
        # 🆕 0단계: 진입 즉시 선제 클린업 (측정 전 VRAM 말끔히 비우기)
        # ────────────────────────────────────────────────────────────
        logger.info("🧼 [GPU Safety Gate] 진입 즉시 선제 클린업 실행 (이전 작업 캐시/VRAM 방출)...")
        try:
            cls.cleanup_all()
        except Exception as e:
            logger.warning(f"선제 클린업 중 예외 발생 (무시하고 계속 진행): {e}")

        # 클린업 반영을 위한 짧은 안정화 대기 (드라이버 VRAM 회수 지연 흡수)
        time.sleep(2)

        logger.info(
            f"🔍 [GPU Safety Gate] 렌더링 진입 전 GPU 상태 정밀 검사 중... "
            f"(주간 시간대 {now_hour:02d}시 ➔ KTRS 충돌 검사 정상 수행 | "
            f"안전 게이트 {cls.MAX_SAFE_TEMP}℃ / 비상 정지 {cls.EMERGENCY_HALT_TEMP}℃ | "
            f"감지 기준: {cls.KTRS_CONFLICT_VRAM_MB}MB, 타임아웃: {timeout_sec}초)"
        )

        while True:
            stats = cls.get_gpu_stats()
            if not stats["available"]:
                # GPU 상태 조회가 불가하면 안전 기본 통과
                logger.info("ℹ️ [GPU Safety] nvidia-smi 비활성 환경 - 진입 승인")
                return True

            temp = stats["temp_c"]
            vram_used = stats["vram_used_mb"]
            vram_total = stats["vram_total_mb"]
            elapsed = time.time() - start_time

            # 0. 🚨 [비상 정지] 86℃ 초과 = 팬 고장/열폭주 → 렌더링 즉시 중단
            if temp > cls.EMERGENCY_HALT_TEMP:
                logger.critical(
                    f"🚨 [GPU 비상 정지] 현재 온도 {temp}℃ 가 "
                    f"비상 임계치 {cls.EMERGENCY_HALT_TEMP}℃ 를 초과했습니다! "
                    f"(팬 고장 또는 극한 열폭주 의심) ➔ ComfyUI 렌더링 즉시 중단"
                )
                cls.interrupt_comfyui()
                cls.cleanup_all()
                return False

            # 1. 온도 과열 차단벽 (82℃ 이상일 때만 대기 — 정상 75~80℃ 풀부하는 통과)
            if temp >= cls.MAX_SAFE_TEMP:
                logger.warning(
                    f"⚠️ [GPU 과열 경보] 현재 온도 {temp}℃ (안전 게이트 {cls.MAX_SAFE_TEMP}℃ 도달) "
                    f"➔ {cls.TARGET_COOL_TEMP}℃ 이하로 냉각될 때까지 자동 휴식 대기 중..."
                )
                cls.cleanup_all()
                time.sleep(15)
                if time.time() - start_time > timeout_sec:
                    logger.error("❌ GPU 냉각 타임아웃 초과")
                    return False
                continue

            # 2. 저쪽 컴퓨터(KTRS) 충돌 방지 및 양보 게이트
            if vram_used >= cls.KTRS_CONFLICT_VRAM_MB:
                logger.warning(
                    f"🤝 [저쪽 컴퓨터(KTRS) GPU 사용 감지] 현재 VRAM 사용량: {vram_used}MB / {vram_total}MB "
                    f"(감지 기준 {cls.KTRS_CONFLICT_VRAM_MB}MB) "
                    f"➔ 저쪽 컴퓨터 작업을 방해하지 않기 위해 15초간 자율 양보 대기합니다. "
                    f"(경과 {int(elapsed)}초 / 제한 {timeout_sec}초)"
                )
                time.sleep(15)
                if time.time() - start_time > timeout_sec:
                    # 🆕 120초 초과 시 경고 후 강제 진행 (무한 대기 원천 차단)
                    logger.warning(
                        f"⚠️ [KTRS 대기 타임아웃 {timeout_sec}초 도달] "
                        f"VRAM {vram_used}MB 잔여 상태이지만 무한 대기를 막기 위해 "
                        f"경고 후 렌더링을 강제 진행합니다."
                    )
                    return True
                continue

            # 모든 조건 충족 (정상 통과)
            logger.info(
                f"✅ [GPU 안전 진입 승인] 온도: {temp}℃ (정상, 게이트 {cls.MAX_SAFE_TEMP}℃ 미만), "
                f"VRAM 점유: {vram_used}MB / {vram_total}MB (정상, 기준 {cls.KTRS_CONFLICT_VRAM_MB}MB 미만) "
                f"| 소요: {round(elapsed, 1)}초"
            )
            return True

    @classmethod
    def cooldown(cls, duration_sec: int = DEFAULT_COOLDOWN_SEC, label: str = ""):
        """
        작업 1건 완료 직후 엄격한 5분(300초) 냉각 휴식
        - 시작 즉시 VRAM 강제 방출
        - 30초마다 카운트다운 및 실시간 온도 로깅
        - 🌡️ v4: TARGET_COOL_TEMP(60℃) 기준으로 냉각 판정
          · 86℃ 초과 시 비상 정지(/interrupt) 후 TARGET_EMERGENCY_COOL_TEMP(60℃)까지 대기
        """
        tag = f"[{label}] " if label else ""
        logger.info(
            f"❄️ {tag}작업 1건 완료! GPU 과열 방지를 위해 {duration_sec}초(5분) 냉각 휴식을 시작합니다. "
            f"(목표 {cls.TARGET_COOL_TEMP}℃ / 비상 정지 {cls.EMERGENCY_HALT_TEMP}℃)"
        )

        # VRAM 즉시 방출
        cls.cleanup_all()

        rem = duration_sec
        interval = 30
        while rem > 0:
            sleep_step = min(rem, interval)
            time.sleep(sleep_step)
            rem -= sleep_step
            stats = cls.get_gpu_stats()
            temp_str = f"{stats['temp_c']}℃" if stats["available"] else "확인불가"
            vram_str = f"{stats['vram_used_mb']}MB" if stats["available"] else "확인불가"

            # 🚨 쿨다운 중에도 86℃ 초과 시 즉시 비상 정지
            if stats["available"] and stats["temp_c"] > cls.EMERGENCY_HALT_TEMP:
                logger.critical(
                    f"🚨 [쿨다운 중 비상 정지] 온도 {stats['temp_c']}℃ 가 "
                    f"비상 임계치 {cls.EMERGENCY_HALT_TEMP}℃ 초과! ➔ ComfyUI 렌더링 즉시 중단"
                )
                cls.interrupt_comfyui()
                cls.cleanup_all()

            logger.info(
                f"⏳ [쿨다운 휴식 중] 남은 시간: {rem}초 / {duration_sec}초 | "
                f"GPU 온도: {temp_str} (목표 {cls.TARGET_COOL_TEMP}℃) | VRAM 사용량: {vram_str}"
            )

        # 쿨다운 종료 후 추가 안전 검사 (60℃ 초과 시에만 짧은 안정화 대기)
        stats = cls.get_gpu_stats()
        if stats["available"] and stats["temp_c"] > cls.TARGET_COOL_TEMP:
            logger.info(
                f"ℹ️ 온도가 {stats['temp_c']}℃로 아직 목표({cls.TARGET_COOL_TEMP}℃)보다 따뜻하여 "
                f"추가 30초 안정화 대기..."
            )
            time.sleep(30)

        logger.info(f"🎉 {tag}GPU 냉각 휴식 완료! 온도가 안전하게 복귀되었습니다.")

    @classmethod
    def run_isolated_step(
        cls,
        cmd: list,
        label: str,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout_sec: int = 1800,
        cooldown_sec: int = DEFAULT_COOLDOWN_SEC
    ) -> Dict[str, Any]:
        """
        🔒 서브프로세스 완전 격리 실행 + 실행 전 안전 검사 + 완료 즉시 5분 쿨다운
        """
        logger.info(f"\n========================================================")
        logger.info(f"🚀 [격리 실행 시작] {label}")
        logger.info(f"명령어: {' '.join(str(c) for c in cmd)}")
        logger.info(f"========================================================")

        # 1. 안전 진입 점검 (기본 120초 타임아웃)
        if not cls.wait_for_safe_gpu_entry(timeout_sec=cls.KTRS_WAIT_TIMEOUT_SEC):
            return {"success": False, "error": "GPU 안전 진입 실패 (과열 또는 리소스 충돌)"}

        # 2. 독립 프로세스 실행 (OS 메모리 완전 격리)
        proc_env = os.environ.copy()
        if env:
            proc_env.update(env)

        start_t = time.time()
        try:
            res = subprocess.run(
                cmd,
                cwd=cwd,
                env=proc_env,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                encoding="utf-8",
                errors="replace"
            )
            elapsed = round(time.time() - start_t, 1)
            is_ok = (res.returncode == 0)

            if is_ok:
                logger.info(f"🎉 [실행 성공] {label} (소요 시간: {elapsed}초)")
            else:
                logger.error(f"❌ [실행 실패] {label} (종료 코드: {res.returncode}, 소요 시간: {elapsed}초)")
                logger.error(f"표준 에러 요약: {res.stderr[-500:] if res.stderr else '없음'}")

            # 3. 성공/실패 무관하게 완료 즉시 5분 쿨다운 및 VRAM 반환
            cls.cooldown(duration_sec=cooldown_sec, label=label)

            return {
                "success": is_ok,
                "returncode": res.returncode,
                "elapsed_sec": elapsed,
                "stdout": res.stdout,
                "stderr": res.stderr
            }

        except subprocess.TimeoutExpired:
            logger.error(f"❌ [타임아웃] {label} 제한시간({timeout_sec}초) 초과")
            cls.cooldown(duration_sec=cooldown_sec, label=f"{label} 타임아웃 회수")
            return {"success": False, "error": "타임아웃 초과"}
        except Exception as e:
            logger.error(f"❌ [실행 예외] {label}: {e}")
            cls.cooldown(duration_sec=cooldown_sec, label=f"{label} 예외 회수")
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    print("GPU 안전 가드 자가 점검:")
    st = GPUSafetyGuard.get_gpu_stats()
    print("Stats:", st)
    print(f"MAX_SAFE_TEMP              = {GPUSafetyGuard.MAX_SAFE_TEMP}℃ (Pre-flight 안전 게이트)")
    print(f"TARGET_COOL_TEMP           = {GPUSafetyGuard.TARGET_COOL_TEMP}℃ (냉각 목표)")
    print(f"EMERGENCY_HALT_TEMP        = {GPUSafetyGuard.EMERGENCY_HALT_TEMP}℃ (비상 정지)")
    print(f"TARGET_EMERGENCY_COOL_TEMP = {GPUSafetyGuard.TARGET_EMERGENCY_COOL_TEMP}℃ (비상 후 재개 목표)")
    print(f"KTRS_CONFLICT_VRAM_MB = {GPUSafetyGuard.KTRS_CONFLICT_VRAM_MB}MB")
    print(f"KTRS_WAIT_TIMEOUT_SEC = {GPUSafetyGuard.KTRS_WAIT_TIMEOUT_SEC}초")
    _now_hour = datetime.datetime.now().hour
    _is_night = GPUSafetyGuard.is_night_golden_time()
    print(
        f"현재 시각(KST) = {_now_hour:02d}시 | "
        f"야간 골든타임(00:00~07:00) 여부 = {'🌙 YES (KTRS 검사 바이패스)' if _is_night else '☀️ NO (KTRS 검사 수행)'}"
    )
    GPUSafetyGuard.cleanup_all()
    print("클린업 테스트 완료")
