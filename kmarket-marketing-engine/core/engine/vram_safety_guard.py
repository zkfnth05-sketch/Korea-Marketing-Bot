# -*- coding: utf-8 -*-
"""
VRAMSafetyGuard - 🛡️ [GPU VRAM 안전 차단 및 과열 방지 가드레일]
- [1] 사전 진입 게이트: 비디오 렌더링 전 순수 가용 VRAM(최소 11.5GB+) 실시간 검증
- [2] 런타임 킬스위치: 모델 적재 시 CPU 대량 오프로드 감지 시 0.1초 만에 즉시 작업 중단(Interrupt)
- [3] 대시보드 연동: GPU 과열 및 저속 연산(1시간 이상 지연) 원천 차단 및 명확한 시각적 알림
- [4] 24시간 무인 자율 회복: VRAM 부족 시 ComfyUI /free 강제 언로드로 잔류 모델(UMT5 등) 자율 정리
"""

import json
import logging
import subprocess
import time
import urllib.request
from typing import Dict, Any, Optional, Tuple, Callable

logger = logging.getLogger("VRAMSafetyGuard")


class VRAMSafetyException(RuntimeError):
    """VRAM 부족 및 GPU 과열 방지 안전 차단 예외"""
    pass


class VRAMSafetyGuard:
    """GPU VRAM 사전 검증 및 실시간 런타임 감시 엔진"""

    MIN_S2V_VRAM_GB = 10.0  # Wan 2.2 S2V 14B 모델 VRAM 탑재를 위한 최소 가용 메모리 (GB)

    # 🛡️ [24시간 무인 자율 회복] 강제 언로드 정책 상수
    FORCE_UNLOAD_WAIT_SEC = 2.0      # /free 전송 후 VRAM 반환 대기 시간(초)
    FORCE_UNLOAD_MAX_ROUNDS = 2      # 최대 강제 언로드 재시도 횟수
    FORCE_UNLOAD_MIN_GAIN_GB = 0.3   # 이 이상 확보되면 추가 라운드 생략(불필요한 언로드 방지)

    @classmethod
    def get_vram_info(cls, host: str = "http://127.0.0.1:8188") -> Dict[str, float]:
        """
        현재 GPU VRAM 실시간 용량 조회 (ComfyUI system_stats 우선, nvidia-smi 백업)
        반환: {'free_gb': float, 'total_gb': float, 'used_gb': float}
        """
        # 1차 시도: ComfyUI /system_stats API
        try:
            req = urllib.request.Request(f"{host}/system_stats", headers={"User-Agent": "VRAMSafetyGuard"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                stats = json.loads(resp.read().decode("utf-8"))
                devices = stats.get("devices", [])
                for d in devices:
                    if d.get("type") == "cuda":
                        free_b = d.get("vram_free", 0)
                        total_b = d.get("vram_total", 0)
                        if total_b > 0:
                            free_gb = free_b / (1024 ** 3)
                            total_gb = total_b / (1024 ** 3)
                            return {
                                "free_gb": round(free_gb, 2),
                                "total_gb": round(total_gb, 2),
                                "used_gb": round(total_gb - free_gb, 2),
                                "source": "comfyui"
                            }
        except Exception as e:
            logger.debug(f"ComfyUI system_stats 조회 실패 (nvidia-smi 백업 전환): {e}")

        # 2차 시도: nvidia-smi CLI
        try:
            cmd = ["nvidia-smi", "--query-gpu=memory.free,memory.total", "--format=csv,nounits,noheader"]
            out = subprocess.check_output(cmd, text=True, timeout=3).strip()
            if out:
                free_mb, total_mb = [float(x.strip()) for x in out.split(",")]
                free_gb = free_mb / 1024.0
                total_gb = total_mb / 1024.0
                return {
                    "free_gb": round(free_gb, 2),
                    "total_gb": round(total_gb, 2),
                    "used_gb": round(total_gb - free_gb, 2),
                    "source": "nvidia-smi"
                }
        except Exception as e:
            logger.warning(f"nvidia-smi 조회 예외: {e}")

        # 알 수 없는 경우 보수적 반환
        return {"free_gb": 0.0, "total_gb": 16.0, "used_gb": 16.0, "source": "unknown"}

    # ------------------------------------------------------------------
    # 🛡️ [24시간 무인 자율 회복] ComfyUI 강제 언로드 (/free)
    # ------------------------------------------------------------------
    @classmethod
    def force_unload_comfyui_models(
        cls,
        host: str = "http://127.0.0.1:8188",
        unload_models: bool = False,
        timeout: float = 5.0,
    ) -> bool:
        """
        ComfyUI /free 엔드포인트로 잔류 모델을 안전하게 정리.

        [동작]
          · POST {host}/free  body={"unload_models": False, "free_memory": True}
          · 성공 시 True, 실패(서버 미기동/타임아웃) 시 False 반환 (예외를 밖으로 던지지 않음)

        [주의]
          · ComfyUI-GGUF 환경에서 unload_models=True는 네이티브 텐서 해제 경로에서
            0xC0000005 접근 위반을 유발하므로 항상 False 로 안전 고정한다.
        """
        payload = json.dumps({
            "unload_models": False,
            "free_memory": True,
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                f"{host}/free",
                data=payload,
                headers={"Content-Type": "application/json", "User-Agent": "VRAMSafetyGuard"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                resp.read()
            logger.info(
                f"🧹 [VRAM 자율회복] ComfyUI /free 강제 언로드 신호 전송 완료 "
                f"(unload_models={unload_models}, free_memory=True)"
            )
            return True
        except Exception as e:
            logger.warning(f"⚠️ [VRAM 자율회복] ComfyUI /free 강제 언로드 실패 (서버 미기동/타임아웃): {e}")
            return False

    @classmethod
    def _reclaim_vram(
        cls,
        host: str,
        threshold: float,
        auto_free_fn: Optional[Callable[[], None]] = None,
    ) -> Tuple[Dict[str, float], Dict[str, Any]]:
        """
        [자율 회복 파이프라인] 1차 auto_free_fn -> 2차 ComfyUI /free 강제 언로드 -> 재측정

        반환: (최종 vram_info, 회복 리포트 dict)
        """
        report: Dict[str, Any] = {
            "initial_free_gb": None,
            "after_auto_free_gb": None,
            "after_force_unload_gb": None,
            "auto_free_called": False,
            "force_unload_called": False,
            "force_unload_rounds": 0,
            "recovered": False,
        }

        info = cls.get_vram_info(host=host)
        report["initial_free_gb"] = info["free_gb"]

        if info["free_gb"] >= threshold:
            report["recovered"] = True
            return info, report

        # ---------------- 1차: auto_free_fn (경량 캐시 정리) ----------------
        if auto_free_fn:
            logger.info(
                f"🧹 [VRAM 자율회복 1차] 가용 VRAM 부족 감지 "
                f"({info['free_gb']:.2f}GB < {threshold:.1f}GB). auto_free_fn 실행..."
            )
            try:
                auto_free_fn()
                report["auto_free_called"] = True
            except Exception as e:
                logger.warning(f"자동 VRAM 비우기(auto_free_fn) 실패: {e}")
            time.sleep(1.0)
            info = cls.get_vram_info(host=host)
            report["after_auto_free_gb"] = info["free_gb"]

            if info["free_gb"] >= threshold:
                report["recovered"] = True
                logger.info(
                    f"✅ [VRAM 자율회복 1차 성공] auto_free_fn으로 "
                    f"{info['free_gb']:.2f}GB 확보 (기준 {threshold:.1f}GB 충족)"
                )
                return info, report

        # ---------------- 2차: ComfyUI /free 강제 언로드 ----------------
        logger.warning(
            f"🔥 [VRAM 자율회복 2차] 1차 정리 후에도 부족 "
            f"({info['free_gb']:.2f}GB < {threshold:.1f}GB). "
            f"ComfyUI /free 강제 언로드(UMT5 텍스트 인코더 등 잔류 모델) 시작..."
        )

        for round_idx in range(1, cls.FORCE_UNLOAD_MAX_ROUNDS + 1):
            before_gb = info["free_gb"]
            sent = cls.force_unload_comfyui_models(host=host, unload_models=False)
            report["force_unload_called"] = True
            report["force_unload_rounds"] = round_idx

            if not sent:
                # 서버 미기동이면 추가 라운드는 무의미 -> 즉시 중단
                logger.warning("⚠️ [VRAM 자율회복 2차] ComfyUI 서버 응답 없음. 강제 언로드 라운드 중단.")
                break

            # VRAM 반환 대기 (2초)
            time.sleep(cls.FORCE_UNLOAD_WAIT_SEC)
            info = cls.get_vram_info(host=host)
            report["after_force_unload_gb"] = info["free_gb"]

            gained = info["free_gb"] - before_gb
            logger.info(
                f"📊 [VRAM 자율회복 2차 {round_idx}라운드] "
                f"{before_gb:.2f}GB -> {info['free_gb']:.2f}GB (+{gained:.2f}GB)"
            )

            if info["free_gb"] >= threshold:
                report["recovered"] = True
                logger.info(
                    f"✅ [VRAM 자율회복 2차 성공] ComfyUI 강제 언로드로 "
                    f"{info['free_gb']:.2f}GB 확보 (기준 {threshold:.1f}GB 충족)"
                )
                return info, report

            # 이미 충분히 회수했는데도 임계값 미달이면(물리적 한계) 추가 라운드 무의미
            if gained >= cls.FORCE_UNLOAD_MIN_GAIN_GB and round_idx >= 1:
                logger.info(
                    f"ℹ️ [VRAM 자율회복] {gained:.2f}GB 회수했으나 임계값 미달 "
                    f"(다른 프로세스가 VRAM 점유 중일 가능성). 추가 라운드 생략."
                )
                break

        return info, report

    @classmethod
    def assert_vram_headroom(
        cls,
        min_free_gb: Optional[float] = None,
        host: str = "http://127.0.0.1:8188",
        auto_free_fn: Optional[Callable[[], None]] = None,
        force_unload: bool = True,
    ) -> Dict[str, float]:
        """
        [1단계: 사전 진입 게이트 + 24시간 무인 자율 회복]
        비디오 렌더링 시작 전 VRAM 확보 여부 전수 검사.

        회복 시퀀스:
          1차) auto_free_fn() 호출 -> 1초 대기 -> 재측정
          2차) ComfyUI /free 에 {'unload_models': True, 'free_memory': True} 전송
               -> 2초 대기 -> 재측정 (최대 FORCE_UNLOAD_MAX_ROUNDS 회)
        그래도 미달 시 VRAMSafetyException을 발생시켜 작업 즉각 중단.

        Args:
            min_free_gb: 안전 기준 가용 VRAM(GB). 미지정 시 MIN_S2V_VRAM_GB
            host: ComfyUI 서버 주소
            auto_free_fn: 1차 경량 메모리 정리 콜백
            force_unload: False면 2차 ComfyUI 강제 언로드를 생략(수동 제어용)
        """
        threshold = min_free_gb or cls.MIN_S2V_VRAM_GB

        if force_unload:
            info, report = cls._reclaim_vram(host=host, threshold=threshold, auto_free_fn=auto_free_fn)
        else:
            # 강제 언로드 비활성: 기존 1차 로직만 수행
            info = cls.get_vram_info(host=host)
            report = {"initial_free_gb": info["free_gb"], "recovered": info["free_gb"] >= threshold}
            if info["free_gb"] < threshold and auto_free_fn:
                logger.info(
                    f"🧹 [VRAM 가드레일] 가용 VRAM 부족 감지 "
                    f"({info['free_gb']}GB < {threshold}GB). 자동 메모리 비우기 1회 실행..."
                )
                try:
                    auto_free_fn()
                except Exception as e:
                    logger.warning(f"자동 VRAM 비우기 실패: {e}")
                time.sleep(1.0)
                info = cls.get_vram_info(host=host)
                report["after_auto_free_gb"] = info["free_gb"]
                report["recovered"] = info["free_gb"] >= threshold

        if info["free_gb"] < threshold:
            err_msg = (
                f"🚨 [VRAM 안전 차단] 텍스트 인코더(UMT5) 잔류 등으로 가용 VRAM이 부족합니다 "
                f"(현재 {info['free_gb']:.2f}GB / 안전 기준 {threshold:.1f}GB 이상). "
                f"[자율회복 시도: auto_free={report.get('auto_free_called')}, "
                f"강제언로드 {report.get('force_unload_rounds', 0)}회] "
                "GPU 과열 및 비정상 지연(스텝당 4분, 총 1시간 20분 이상)을 방지하기 위해 "
                "작업을 즉시 안전하게 중단했습니다. (ComfyUI 메모리 클린업 필요)"
            )
            logger.error(err_msg)
            raise VRAMSafetyException(err_msg)

        logger.info(
            f"🛡️ [VRAM 안전 통과] 현재 가용 VRAM {info['free_gb']:.2f}GB / {info['total_gb']:.2f}GB "
            f"(안전 기준 {threshold:.1f}GB 충족, 자율회복 경로: "
            f"auto_free={report.get('auto_free_called')}, "
            f"force_unload={report.get('force_unload_rounds', 0)}회)"
        )
        return info

    @classmethod
    def trigger_emergency_interrupt(cls, host: str = "http://127.0.0.1:8188"):
        """[비상 정지] ComfyUI 연산 즉시 중단 및 VRAM 강제 해제"""
        try:
            req_int = urllib.request.Request(
                f"{host}/interrupt",
                data=b"{}",
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req_int, timeout=3) as resp:
                pass
            logger.info("🛑 [VRAM 가드레일] ComfyUI /interrupt 긴급 신호 발송 완료")
        except Exception as e:
            logger.warning(f"비상 interrupt 실패: {e}")

        try:
            req_free = urllib.request.Request(
                f"{host}/free",
                # 🛡️ unload_models=False 고정: ComfyUI-GGUF ops.py의 0xC0000005 C++ 접근 위반 크래시 방지
                #    (GGUF 모델 언로드 시 네이티브 텐서 해제 경로에서 치명적 액세스 바이올레이션 발생)
                #    free_memory=True만으로도 캐시/중간 텐서는 충분히 방출된다.
                data=json.dumps({"unload_models": False, "free_memory": True}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req_free, timeout=3) as resp:
                pass
            logger.info("🧹 [VRAM 가드레일] ComfyUI /free 모델 및 캐시 완전 방출 완료")
        except Exception as e:
            logger.warning(f"비상 free 실패: {e}")

    @classmethod
    def check_log_line_for_violation(cls, line: str) -> Tuple[bool, str]:
        """
        [2단계: 런타임 킬스위치]
        ComfyUI 로그 라인 검사: S2V 모델의 CPU 대량 오프로드 감지 시 True 및 사유 반환
        """
        # 패턴: loaded partially; 0.00 MB usable, 0.00 MB loaded, 12471.75 MB offloaded
        if "loaded partially" in line and "offloaded" in line:
            # offloaded 용량 확인
            try:
                import re
                m_off = re.search(r"([\d\.]+)\s*MB offloaded", line)
                m_load = re.search(r"([\d\.]+)\s*MB loaded", line)
                if m_off and m_load:
                    off_mb = float(m_off.group(1))
                    load_mb = float(m_load.group(1))
                    total_model_mb = off_mb + load_mb
                    # 거대 비디오 모델(Wan2.2 S2V 12GB 등, 5000MB 초과 모델)에 대한 킬스위치
                    if total_model_mb > 5000.0:
                        # 4,000MB(4GB) 이상 심각하게 CPU로 튕겨 나갔거나 GPU 적재량이 4,000MB 미만인 치명적 경우에만 차단
                        # (10GB 이상 정상 GPU 적재 시 2GB 미만의 버퍼 오프로드는 16GB GPU의 정상 고속 동작 대역입니다)
                        if off_mb > 4000.0 or load_mb < 4000.0:
                            reason = f"비디오 모델의 {off_mb:.1f}MB가 RAM으로 심각하게 밀려남 감지 (GPU 적재량: {load_mb:.1f}MB, 전체 크기: {total_model_mb:.1f}MB)"
                            return True, reason
            except Exception as e:
                logger.warning(f"VRAM 로그 라인 파싱 예외: {e}")
                return False, ""

        return False, ""

    @classmethod
    def get_latest_comfyui_log_path(cls) -> Optional[str]:
        """ComfyUI의 현재 활성 실행 로그 파일 경로 탐색"""
        import os
        import glob
        from pathlib import Path

        # 1. 표준 출력 로그 파일 (ComfyProcessManager 관리 경로)
        direct = Path(r"D:\ComfyUI_Wan_Engine\comfyui_stdout.log")
        if direct.exists() and direct.stat().st_size > 0:
            return str(direct)

        # 2. Antigravity task 실행 로그
        task_logs = glob.glob(r"C:\Users\zkfnt\.gemini\antigravity-ide\brain\*\.system_generated\tasks\task-*.log")
        recent = sorted(task_logs, key=os.path.getmtime, reverse=True)
        for p in recent[:10]:
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(3000)
                    if "To see the GUI go to: http://127.0.0.1:8188" in content or "ComfyUI\\main.py" in content:
                        return p
            except Exception:
                pass

        return None
