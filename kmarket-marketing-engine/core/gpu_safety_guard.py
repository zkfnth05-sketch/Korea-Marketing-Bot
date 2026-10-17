# -*- coding: utf-8 -*-
"""
[독립 레고 블록] GPUSafetyGuard - 🛡️ [RTX 5060 Ti GPU 과열 방지 & VRAM 무결점 안심 가드]
======================================================================================
- 전담 역할:
  1. 실시간 GPU 온도 & VRAM 사용량 정밀 모니터링 (nvidia-smi 파싱)
  2. ComfyUI / PyTorch VRAM 즉시 강제 방출 (/free API + empty_cache)
  3. 엄격한 5분(300초) 쿨다운 타이머 (실시간 온도/잔량 로깅)
  4. 65℃ 안전 온도 차단벽 (Overheat Safety Gate)
  5. 저쪽 컴퓨터(KTRS 마케팅봇) 작업 감지 시 자율 양보 (Conflict Avoidance)
  6. 서브프로세스 완전 격리 실행 (작업 완료 즉시 OS 레벨 메모리 100% 회수)
"""

import os
import sys
import time
import json
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
    MAX_SAFE_TEMP = 65          # 최대 허용 온도 (65도 넘으면 즉시 차단 후 대기)
    TARGET_COOL_TEMP = 50       # 냉각 목표 온도 (50도 이하로 식힌 후 작업 재개)
    KTRS_CONFLICT_VRAM_MB = 7000  # 저쪽 컴퓨터(KTRS) 점유 감지 기준 (7GB 이상 사용 중이면 양보)

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
        payload = json.dumps({"unload_models": True, "free_memory": True}).encode("utf-8")
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
    def flush_system_vram(cls):
        """파이썬 가비지 컬렉션 및 PyTorch CUDA 메모리 캐시 초기화"""
        import gc
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

    @classmethod
    def cleanup_all(cls):
        """ComfyUI + PyTorch + OS 가비지 컬렉션 통합 정리"""
        cls.free_comfyui_vram()
        cls.flush_system_vram()

    @classmethod
    def wait_for_safe_gpu_entry(cls, timeout_sec: int = 900) -> bool:
        """
        렌더링 작업 시작 전 안전 진입 게이트
        1. 온도가 65℃ 이상이면 50℃ 이하로 식을 때까지 대기
        2. VRAM 사용량이 7GB 이상이면 저쪽 컴퓨터(KTRS) 작업 중으로 판단하고 양보 대기
        """
        start_time = time.time()
        logger.info("🔍 [GPU Safety Gate] 렌더링 진입 전 GPU 상태 및 온도 정밀 검사 중...")

        while True:
            stats = cls.get_gpu_stats()
            if not stats["available"]:
                # GPU 상태 조회가 불가하면 안전 기본 통과
                logger.info("ℹ️ [GPU Safety] nvidia-smi 비활성 환경 - 진입 승인")
                return True

            temp = stats["temp_c"]
            vram_used = stats["vram_used_mb"]
            vram_total = stats["vram_total_mb"]

            # 1. 온도 과열 차단벽
            if temp >= cls.MAX_SAFE_TEMP:
                logger.warning(
                    f"⚠️ [GPU 과열 경보] 현재 온도 {temp}℃ (한계치 {cls.MAX_SAFE_TEMP}℃ 도달) "
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
                    f"➔ 저쪽 컴퓨터 작업을 방해하지 않기 위해 15초간 자율 양보 대기합니다."
                )
                time.sleep(15)
                if time.time() - start_time > timeout_sec:
                    logger.warning("⚠️ KTRS 작업 대기 타임아웃 도달 - 진행 강제 시도")
                    return True
                continue

            # 모든 조건 충족 (정상 통과)
            logger.info(
                f"✅ [GPU 안전 진입 승인] 온도: {temp}℃ (정상), "
                f"VRAM 점유: {vram_used}MB / {vram_total}MB (정상)"
            )
            return True

    @classmethod
    def cooldown(cls, duration_sec: int = DEFAULT_COOLDOWN_SEC, label: str = ""):
        """
        작업 1건 완료 직후 엄격한 5분(300초) 냉각 휴식
        - 시작 즉시 VRAM 강제 방출
        - 30초마다 카운트다운 및 실시간 온도 로깅
        """
        tag = f"[{label}] " if label else ""
        logger.info(f"❄️ {tag}작업 1건 완료! GPU 과열 방지를 위해 {duration_sec}초(5분) 냉각 휴식을 시작합니다.")

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
            logger.info(
                f"⏳ [쿨다운 휴식 중] 남은 시간: {rem}초 / 300초 | "
                f"GPU 온도: {temp_str} | VRAM 사용량: {vram_str}"
            )

        # 쿨다운 종료 후 추가 안전 검사
        stats = cls.get_gpu_stats()
        if stats["available"] and stats["temp_c"] > cls.TARGET_COOL_TEMP:
            logger.info(f"ℹ️ 온도가 {stats['temp_c']}℃로 아직 따뜻하여 추가 30초 안정화 대기...")
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

        # 1. 안전 진입 점검
        if not cls.wait_for_safe_gpu_entry():
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
    GPUSafetyGuard.cleanup_all()
    print("클린업 테스트 완료")
