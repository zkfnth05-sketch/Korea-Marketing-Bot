# -*- coding: utf-8 -*-
"""
Omni Session Heartbeat Keeper (5대 SNS + 블로그 365일 무인 영구 생명 연장 코어 엔진)
=============================================================================
- 역할:
  3개 브랜드(insurance, stock, aura) × 6대 플랫폼(YouTube, Meta MBS, TikTok, Naver Clip, Threads, Tistory)
  각 디스크 프로필 및 세션을 3시간마다 스텔스로 핑(Ping)하여
  플랫폼 보안 서버의 유휴(Inactivity) 만료 타이머를 원천 리셋하고 365일 영구 유지합니다.

[5인 협업체 토론 + 제미나이 감사관 교차 검증 반영 5대 원칙]
  1. Windows/Linux 크로스플랫폼 파일 락 (fcntl 금지 → msvcrt + 원자적 O_EXCL 락, finally 해제 보장)
  2. Threads 프로필 물리 격리 (meta_chrome_profile → threads_chrome_profile)
  3. SESSION / GOLDEN 불변 상태 계층 (SessionStateStore: load_or_restore / restore_from_golden / 원자적 쓰기)
  4. 핑 실패·만료 시 Read-Only 강제 + GOLDEN 자가치유 롤백 (빈 세션 덮어쓰기 절대 금지)
  5. py_compile 무결점 통과
"""

import os
import sys
import json
import time
import shutil
import asyncio
import logging
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from playwright.async_api import async_playwright

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine.session_integrity import (
    has_auth, is_logged_out_url, ensure_auth_cookies, save_if_logged_in, log_event,
    sanitize_for_playwright,
)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("OmniSessionHeartbeat")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


# =====================================================================
# 🔒 원칙 1: Windows / Linux 크로스플랫폼 파일 락 (fcntl 절대 사용 금지)
# =====================================================================
IS_WINDOWS = (sys.platform == "win32")

if IS_WINDOWS:
    try:
        import msvcrt  # type: ignore
    except Exception:  # pragma: no cover
        msvcrt = None  # type: ignore
else:
    msvcrt = None  # type: ignore


class CrossPlatformFileLock:
    """
    Windows(msvcrt.locking) / POSIX(원자적 O_CREAT|O_EXCL 락파일) 공통 안전 락.

    - fcntl 모듈은 절대 import 하지 않는다 (Windows ModuleNotFoundError 원천 차단).
    - with 문 또는 try/finally 어느 쪽으로도 반드시 해제된다.
    - 락 획득 실패 시 예외를 던지지 않고 acquired=False 로 조용히 반환하여
      데몬 전체가 죽지 않도록 방어한다(호출부에서 스킵 판단).
    """

    def __init__(self, lock_path: Path, timeout: float = 30.0, poll: float = 0.2):
        self.lock_path = Path(lock_path)
        self.timeout = float(timeout)
        self.poll = float(poll)
        self.acquired = False
        self._fh = None
        self._excl_created = False

    # ---------- 내부 ----------
    def _try_acquire_windows(self) -> bool:
        """msvcrt.locking: 1바이트 비차단 락 시도"""
        if msvcrt is None:
            return False
        try:
            self.lock_path.parent.mkdir(parents=True, exist_ok=True)
            fh = open(self.lock_path, "a+b")
            fh.seek(0)
            if fh.tell() == 0:
                fh.write(b"\0")
                fh.flush()
            fh.seek(0)
            msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
            self._fh = fh
            return True
        except Exception:
            try:
                if self._fh:
                    self._fh.close()
            except Exception:
                pass
            self._fh = None
            return False

    def _try_acquire_posix(self) -> bool:
        """원자적 O_CREAT|O_EXCL 락파일 생성 (POSIX)"""
        try:
            self.lock_path.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            try:
                os.write(fd, f"{os.getpid()}|{datetime.now().isoformat()}".encode("utf-8"))
            finally:
                os.close(fd)
            self._excl_created = True
            return True
        except FileExistsError:
            # 스테일 락(10분 이상 방치) 자동 회수
            try:
                if time.time() - self.lock_path.stat().st_mtime > 600:
                    self.lock_path.unlink()
                    logger.warning(f"🧹 스테일 락 회수: {self.lock_path.name}")
            except Exception:
                pass
            return False
        except Exception:
            return False

    def acquire(self) -> bool:
        deadline = time.time() + self.timeout
        while True:
            ok = self._try_acquire_windows() if IS_WINDOWS else self._try_acquire_posix()
            if ok:
                self.acquired = True
                return True
            if time.time() >= deadline:
                return False
            time.sleep(self.poll)

    def release(self) -> None:
        """finally 에서 반드시 호출 — 어떤 예외 상황에서도 락을 놓는다."""
        if IS_WINDOWS:
            if self._fh is not None:
                try:
                    self._fh.seek(0)
                    msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)  # type: ignore
                except Exception:
                    pass
                try:
                    self._fh.close()
                except Exception:
                    pass
                self._fh = None
        else:
            if self._excl_created:
                try:
                    self.lock_path.unlink()
                except Exception:
                    pass
                self._excl_created = False
        self.acquired = False

    def __enter__(self) -> "CrossPlatformFileLock":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.release()
        return False


# =====================================================================
# 🧬 원칙 3: SESSION / GOLDEN 불변 상태 계층 (Self-Healing Store)
# =====================================================================
class SessionStateStore:
    """
    세션 파일(session_file)과 불변 골든 백업(*_GOLDEN.json)의 2계층 상태 저장소.

    - load_or_restore(): 정상 세션이면 통과, 골든이 없으면 최초 1회 자동 백업,
                          세션 부재/손상 시 골든에서 자동 복원(Self-Healing).
    - restore_from_golden(): 디스크 작업본을 골든으로 강제 롤백.
    - save_verified(): 검증 통과 시에만 원자적 저장 + 골든 동기화.
    - 원자적 쓰기: temp → flush → fsync → os.replace (덮어쓰기 깨짐 방지)
    """

    def __init__(self, platform: str, session_file: Path):
        self.platform = platform
        self.session_file = Path(session_file)
        self.golden_file = self.session_file.parent / f"{self.session_file.stem}_GOLDEN.json"
        self.lock_file = self.session_file.parent / f".{self.session_file.stem}.lock"

    # ---------- 저수준 ----------
    @staticmethod
    def _read_cookies(path: Path) -> List[Dict[str, Any]]:
        try:
            if not path.exists() or path.stat().st_size < 20:
                return []
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                ck = data.get("cookies")
                return list(ck) if isinstance(ck, list) else []
            if isinstance(data, list):
                return [c for c in data if isinstance(c, dict)]
        except Exception:
            return []
        return []

    def _atomic_write(self, path: Path, cookies: List[Dict[str, Any]]) -> bool:
        """temp → fsync → os.replace 원자적 쓰기 (중간 크래시에도 파일 깨짐 없음)"""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp_name = tempfile.mkstemp(
                prefix=f".{path.stem}_", suffix=".tmp", dir=str(path.parent)
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump({"cookies": cookies}, f, ensure_ascii=False, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp_name, path)
                return True
            except Exception:
                try:
                    if os.path.exists(tmp_name):
                        os.unlink(tmp_name)
                except Exception:
                    pass
                raise
        except Exception as e:
            logger.warning(f"⚠️ 원자적 쓰기 실패({path.name}): {e}")
            return False

    def _is_valid(self, path: Path) -> bool:
        return has_auth(self.platform, self._read_cookies(path))

    # ---------- 공개 API ----------
    def load_or_restore(self) -> Dict[str, Any]:
        """
        반환: {"ok": bool, "action": "pass"|"golden_created"|"restored"|"no_source", "cookies": [...]}
        """
        cur = self._read_cookies(self.session_file)
        cur_ok = has_auth(self.platform, cur)

        # (a) 현재 세션 정상 → 골든이 없으면 최초 1회 자동 백업
        if cur_ok:
            if not self.golden_file.exists() or not self._is_valid(self.golden_file):
                if self._atomic_write(self.golden_file, cur):
                    log_event(self.session_file, self.platform, "golden_created",
                              n=len(cur), src="session_file")
                    logger.info(f"🧬 GOLDEN 최초 생성: {self.golden_file.name} ({len(cur)}개 쿠키)")
                    return {"ok": True, "action": "golden_created", "cookies": cur}
            return {"ok": True, "action": "pass", "cookies": cur}

        # (b) 세션 부재/손상 → 골든에서 자동 복원 (Self-Healing)
        golden = self._read_cookies(self.golden_file)
        if has_auth(self.platform, golden):
            if self._atomic_write(self.session_file, golden):
                log_event(self.session_file, self.platform, "self_healed_from_golden",
                          n=len(golden), reason="session_missing_or_corrupt")
                logger.warning(f"🩹 SELF-HEALING: {self.session_file.name} ← GOLDEN 복원 ({len(golden)}개)")
                return {"ok": True, "action": "restored", "cookies": golden}

        log_event(self.session_file, self.platform, "no_valid_source",
                  n_cur=len(cur), n_golden=len(golden))
        return {"ok": False, "action": "no_source", "cookies": []}

    def restore_from_golden(self) -> bool:
        """디스크 작업본을 GOLDEN으로 강제 롤백 (만료 감지 시 Read-Only 복구)"""
        golden = self._read_cookies(self.golden_file)
        if not has_auth(self.platform, golden):
            log_event(self.session_file, self.platform, "rollback_failed_no_golden")
            return False
        ok = self._atomic_write(self.session_file, golden)
        if ok:
            log_event(self.session_file, self.platform, "rolled_back_to_golden", n=len(golden))
            logger.warning(f"♻️ GOLDEN 롤백 완료: {self.session_file.name} ({len(golden)}개 쿠키)")
        return ok

    def save_verified(self, cookies: List[Dict[str, Any]], reason: str = "") -> bool:
        """검증 통과(정상 로그인) 시에만 원자적 저장 + GOLDEN 동기화"""
        if not has_auth(self.platform, cookies):
            log_event(self.session_file, self.platform, "save_blocked_no_auth", reason=reason)
            return False
        if not self._atomic_write(self.session_file, cookies):
            return False
        self._atomic_write(self.golden_file, cookies)
        log_event(self.session_file, self.platform, "saved_verified", reason=reason, n=len(cookies))
        return True

    def snapshot_cookies(self) -> List[Dict[str, Any]]:
        """현재 유효 쿠키(세션 → 골든 순) 반환 — Read-Only 주입용"""
        cur = self._read_cookies(self.session_file)
        if has_auth(self.platform, cur):
            return cur
        golden = self._read_cookies(self.golden_file)
        if has_auth(self.platform, golden):
            return golden
        return []


# =====================================================================
# 🌐 플랫폼 설정 (원칙 2: Threads 프로필 물리 격리)
# =====================================================================
PLATFORM_CONFIG = {
    "youtube": {
        "profile_dir_name": "youtube_chrome_profile",
        "ping_url": "https://studio.youtube.com/",
        "description": "YouTube Shorts (Google DBSC 토큰)"
    },
    "meta": {
        "profile_dir_name": "meta_chrome_profile",
        "ping_url": "https://business.facebook.com/latest/home",
        "description": "Meta MBS Reels (Meta 세션)"
    },
    "tiktok": {
        "profile_dir_name": "tiktok_chrome_profile",
        "ping_url": "https://www.tiktok.com/tiktokstudio/content",
        "description": "TikTok Studio (sid_tt 토큰)"
    },
    "naver": {
        "profile_dir_name": "naver_browser_profile",
        "ping_url": "https://clipcreators.naver.com/",
        "description": "Naver Clip Creator (NID_AUT 쿠키)"
    },
    "threads": {
        # 🔒 원칙 2: meta_chrome_profile 과 완전 분리된 물리 격리 프로필
        "profile_dir_name": "threads_chrome_profile",
        "session_file_name": "threads_session.json",
        "ping_url": "https://www.threads.net/",
        "description": "Threads (Instagram 연동 세션)"
    }
}

STEALTH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--no-first-run",
    "--no-default-browser-check",
]

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

BLOCK_PATTERN = "**/*.{png,jpg,jpeg,webp,gif,svg,woff,woff2,ttf,mp4,webm}"


class OmniSessionHeartbeatKeeper:
    """전 플랫폼 3시간 스텔스 생명 연장 코어 엔진"""

    def __init__(self, brand: str):
        self.brand = brand.lower()
        self.brand_dir = PROJECT_ROOT / "brands" / self.brand
        self.log_file = self.brand_dir / "session_heartbeat_history.json"

    # ------------------------------------------------------------------
    # 유틸
    # ------------------------------------------------------------------
    def _cleanup_locks(self, profile_dir: Path):
        """SingletonLock만 제거 (SingletonCookie/Socket은 실제 Chrome 데이터라 건드리지 않음)"""
        for fname in ["SingletonLock"]:
            lp = profile_dir / fname
            if lp.exists():
                try:
                    lp.unlink()
                except Exception:
                    pass

    def _log_heartbeat(self, platform: str, status: str, message: str):
        records = []
        if self.log_file.exists():
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    records = json.load(f)
                if not isinstance(records, list):
                    records = []
            except Exception:
                records = []
        records.append({
            "timestamp": datetime.now().isoformat(),
            "brand": self.brand,
            "platform": platform,
            "status": status,
            "message": message
        })
        records = records[-100:]
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.log_file.with_suffix(".json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, self.log_file)
        except Exception:
            pass

    def _session_path(self, platform_key: str) -> Path:
        cfg = PLATFORM_CONFIG.get(platform_key, {})
        name = cfg.get("session_file_name") or f"{platform_key}_session.json"
        return self.brand_dir / name

    # ------------------------------------------------------------------
    # 🔁 공통 핑 실행기 (원칙 4: Read-Only 강제 + GOLDEN 롤백)
    # ------------------------------------------------------------------
    async def _ping_with_store(
        self,
        platform_key: str,
        cfg: Dict[str, Any],
        target_url: str,
        wait_sec: float = 3.0,
        timeout_ms: int = 15000,
    ) -> Dict[str, Any]:
        session_file = self._session_path(platform_key)
        store = SessionStateStore(platform_key, session_file)

        # 0) 락 획득 (크로스플랫폼, finally 해제 보장)
        lock = CrossPlatformFileLock(store.lock_file, timeout=30.0)
        if not lock.acquire():
            msg = "다른 프로세스가 세션을 점유 중 (락 획득 실패 → Read-Only 스킵)"
            logger.warning(f"   ⏭️ [{self.brand.upper()}] {cfg['description']}: {msg}")
            self._log_heartbeat(platform_key, "skipped", msg)
            return {"status": "skipped", "message": msg}

        try:
            # 1) SESSION/GOLDEN 계층 로드 (Self-Healing)
            state = store.load_or_restore()
            if not state["ok"]:
                msg = f"{cfg['description']} 유효 세션 없음 (1회 연동 필요)"
                logger.warning(f"   ⏭️ [{self.brand.upper()}] {msg}")
                self._log_heartbeat(platform_key, "skipped", msg)
                return {"status": "skipped", "message": msg}

            prof_dir = self.brand_dir / cfg["profile_dir_name"]
            has_profile = prof_dir.exists() and any(prof_dir.iterdir())
            if has_profile:
                self._cleanup_locks(prof_dir)

            logger.info(f"[{self.brand.upper()}] {cfg['description']} 스텔스 핑 전송 시작...")

            async with async_playwright() as p:
                browser = None
                if has_profile:
                    context = await p.chromium.launch_persistent_context(
                        user_data_dir=str(prof_dir),
                        headless=True,
                        args=STEALTH_ARGS,
                        viewport={"width": 1280, "height": 900},
                        user_agent=DEFAULT_UA,
                    )
                else:
                    # 프로필이 없으면 세션 쿠키만 주입한 임시 컨텍스트 (Read-Only)
                    browser = await p.chromium.launch(headless=True, args=STEALTH_ARGS)
                    context = await browser.new_context(
                        viewport={"width": 1280, "height": 900},
                        user_agent=DEFAULT_UA,
                    )
                    injected = 0
                    for ck in sanitize_for_playwright(store.snapshot_cookies()):
                        try:
                            await context.add_cookies([ck])
                            injected += 1
                        except Exception:
                            pass
                    logger.info(f"   🍪 세션 쿠키 {injected}개 주입 (프로필 부재 → 임시 컨텍스트)")

                try:
                    # 2) 인증 쿠키 없을 때만 정상 백업에서 복원 (있으면 회전 최신 쿠키 보호)
                    await ensure_auth_cookies(platform_key, context, session_file)

                    page = context.pages[0] if context.pages else await context.new_page()
                    await page.route(BLOCK_PATTERN, lambda route: route.abort())

                    try:
                        await page.goto(target_url, wait_until="domcontentloaded", timeout=timeout_ms)
                        await asyncio.sleep(wait_sec)
                    except Exception:
                        pass

                    cur_url = page.url or ""
                    cookies = await context.cookies()
                    logged_in = (not is_logged_out_url(platform_key, cur_url)) and has_auth(platform_key, cookies)

                    if logged_in:
                        # ✅ 검증 통과 시에만 원자적 저장 + GOLDEN 동기화
                        store.save_verified(cookies, reason="heartbeat_ping")
                        msg = f"세션 생명 연장 성공 (URL: {cur_url[:55]})"
                        logger.info(f"   [성공] [{self.brand.upper()}] {cfg['description']}: {msg}")
                        self._log_heartbeat(platform_key, "active", msg)
                        return {"status": "active", "message": msg}

                    # ❌ 만료/실패 → 절대 빈 세션으로 덮어쓰지 않음 (Read-Only 강제)
                    log_event(session_file, platform_key, "heartbeat_expired", url=cur_url[:80])
                    rolled = store.restore_from_golden()
                    msg = (
                        f"세션 만료 감지 (재연동 필요, URL: {cur_url})"
                        + (" · GOLDEN 롤백 완료" if rolled else " · GOLDEN 없음(롤백 불가)")
                    )
                    logger.warning(f"   ⚠️ [{self.brand.upper()}] {cfg['description']}: {msg}")
                    self._log_heartbeat(platform_key, "expired", msg)
                    return {"status": "expired", "message": msg}
                finally:
                    try:
                        await context.close()
                    except Exception:
                        pass
                    if browser is not None:
                        try:
                            await browser.close()
                        except Exception:
                            pass

        except Exception as e:
            msg = f"핑 예외: {e}"
            logger.warning(f"   [에러] [{self.brand.upper()}] {cfg['description']}: {msg}")
            self._log_heartbeat(platform_key, "error", msg)
            return {"status": "error", "message": msg}
        finally:
            # 🔓 원칙 1: 어떤 경로로 빠져나가든 락은 반드시 해제
            lock.release()

    # ------------------------------------------------------------------
    # 플랫폼별 핑
    # ------------------------------------------------------------------
    async def ping_profile_platform(self, platform_key: str) -> Dict[str, Any]:
        cfg = PLATFORM_CONFIG.get(platform_key)
        if not cfg:
            return {"status": "error", "message": f"알 수 없는 플랫폼: {platform_key}"}

        prof_dir = self.brand_dir / cfg["profile_dir_name"]
        session_file = self._session_path(platform_key)
        has_profile = prof_dir.exists() and any(prof_dir.iterdir())

        if not has_profile and not session_file.exists():
            msg = f"{cfg['description']} 프로필/세션 부재 (1회 연동 필요)"
            self._log_heartbeat(platform_key, "skipped", msg)
            return {"status": "skipped", "message": msg}

        target_url = cfg["ping_url"]
        # 🛡️ 보험비교는 인스타그램 단독 연동 계정이므로 instagram.com으로 스텔스 핑
        if platform_key == "meta" and self.brand == "insurance":
            target_url = "https://www.instagram.com/"

        return await self._ping_with_store(
            platform_key=platform_key,
            cfg=cfg,
            target_url=target_url,
            wait_sec=3.0,
            timeout_ms=15000,
        )

    async def ping_threads(self) -> Dict[str, Any]:
        cfg = PLATFORM_CONFIG["threads"]
        session_file = self._session_path("threads")
        prof_dir = self.brand_dir / cfg["profile_dir_name"]  # 🔒 threads_chrome_profile (물리 격리)

        has_profile = prof_dir.exists() and any(prof_dir.iterdir())
        if not session_file.exists() and not has_profile:
            msg = "Threads 세션/프로필 부재 (1회 연동 필요)"
            self._log_heartbeat("threads", "skipped", msg)
            return {"status": "skipped", "message": msg}

        logger.info(f"[{self.brand.upper()}] Threads(스레드) 스텔스 핑 전송 시작...")
        return await self._ping_with_store(
            platform_key="threads",
            cfg=cfg,
            target_url=cfg["ping_url"],
            wait_sec=2.0,
            timeout_ms=12000,
        )

    async def ping_tistory(self) -> Dict[str, Any]:
        logger.info(f"[{self.brand.upper()}] Tistory(카카오 SSO) 스텔스 생명 연장 가동...")
        try:
            if self.brand == "insurance":
                from brands.insurance.insurance_tistory_publisher import InsuranceTistoryPublisher
                pub = InsuranceTistoryPublisher()
            elif self.brand == "stock":
                from brands.stock.stock_tistory_publisher import StockTistoryPublisher
                pub = StockTistoryPublisher()
            elif self.brand == "aura":
                from brands.aura.aura_tistory_publisher import AuraTistoryPublisher
                pub = AuraTistoryPublisher()
            else:
                return {"status": "skipped", "message": "알 수 없는 브랜드"}

            # 비동기 함수 직접 await 호출 (이벤트 루프 충돌 방지)
            if hasattr(pub, "_keep_alive_async"):
                res = await pub._keep_alive_async()
            else:
                res = pub.keep_alive_session()

            status = res.get("status", "unknown")
            msg = res.get("message", "")

            if status == "active":
                logger.info(f"   [성공] [{self.brand.upper()}] Tistory: {msg}")
                self._log_heartbeat("tistory", "active", msg)
            else:
                logger.warning(f"   [주의] [{self.brand.upper()}] Tistory: {msg}")
                self._log_heartbeat("tistory", status, msg)
            return res
        except Exception as e:
            msg = f"Tistory 생명 연장 예외: {e}"
            logger.warning(f"   [에러] [{self.brand.upper()}] Tistory: {msg}")
            self._log_heartbeat("tistory", "error", msg)
            return {"status": "error", "message": msg}

    # ------------------------------------------------------------------
    # 사이클
    # ------------------------------------------------------------------
    async def run_brand_cycle(self) -> Dict[str, Any]:
        logger.info(f"\n=======================================================")
        logger.info(f"[{self.brand.upper()}] 6대 플랫폼 세션 생명 연장 파이프라인 가동")
        logger.info(f"=======================================================")

        results = {}
        results["youtube"] = await self.ping_profile_platform("youtube")
        results["meta"] = await self.ping_profile_platform("meta")
        results["tiktok"] = await self.ping_profile_platform("tiktok")
        results["naver"] = await self.ping_profile_platform("naver")
        results["threads"] = await self.ping_threads()
        results["tistory"] = await self.ping_tistory()

        active_cnt = sum(1 for r in results.values() if r.get("status") == "active")
        logger.info(f"[{self.brand.upper()}] 완료: 총 {len(results)}개 플랫폼 중 {active_cnt}개 활성 유지 성공\n")
        return {"brand": self.brand, "results": results, "active_count": active_cnt}


async def run_all_brands_cycle() -> Dict[str, Any]:
    all_res = {}
    for b in ["insurance", "stock", "aura"]:
        keeper = OmniSessionHeartbeatKeeper(brand=b)
        all_res[b] = await keeper.run_brand_cycle()
    return all_res


async def start_heartbeat_daemon(interval_hours: float = 3.0):
    interval_sec = int(interval_hours * 3600)
    logger.info(f"[OmniSessionHeartbeat] 365일 무인 영구 생명 연장 데몬 시작 (주기: {interval_hours}시간 / {interval_sec}초)")

    cycle_num = 1
    while True:
        logger.info(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 제 #{cycle_num}회차 전 플랫폼 세션 갱신 사이클 시작")
        try:
            await run_all_brands_cycle()
        except Exception as e:
            logger.error(f"사이클 실행 중 예외: {e}")

        logger.info(f"다음 사이클까지 {interval_hours}시간({interval_sec}초) 동안 백그라운드 대기합니다...\n")
        cycle_num += 1
        await asyncio.sleep(interval_sec)


if __name__ == "__main__":
    if "--daemon" in sys.argv:
        asyncio.run(start_heartbeat_daemon(interval_hours=3.0))
    elif "--brand" in sys.argv:
        idx = sys.argv.index("--brand")
        target_b = sys.argv[idx + 1] if len(sys.argv) > idx + 1 else "insurance"
        keeper = OmniSessionHeartbeatKeeper(brand=target_b)
        asyncio.run(keeper.run_brand_cycle())
    else:
        asyncio.run(run_all_brands_cycle())
