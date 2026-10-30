# -*- coding: utf-8 -*-
"""
Aura Threads Publisher (🧵 Aura 전용 스레드 독립 레고 블록 발행기)
===================================================================
- 브랜드: 💖 Aura (AI 데이팅)
- 전용 계정: @aura_ai_dating
- 검색 공식 키워드: 아우라AI데이팅 (절대 불변)
- 랜딩 URL: https://aura-ai-dating.vercel.app/
- 프로필 디렉터리: brands/aura/threads_chrome_profile/  (🔒 meta_chrome_profile 과 물리적 완전 격리)
- 세션 파일: brands/aura/threads_session.json
- 골든 세션: brands/aura/threads_session_GOLDEN.json (불변 스냅샷 · 자가치유 원본)
- 기능:
  1. 스레드(threads.net) 완전 무인 자동 로그인 세션 유지
  2. 카드뉴스 이미지(4~5장 슬라이드) 또는 텍스트 타래 게시 (500자 규격 자동 최적화)
  3. 첫 번째 타래 댓글로 공식 검색어('아우라AI데이팅') 및 랜딩 URL 자동 체인 부착
  4. 게시 결과 스크린샷 캡처 및 히스토리 아카이빙
"""

import os
import sys
import json
import time
import uuid
import shutil
import asyncio
import logging
import tempfile
import hashlib
from enum import Enum
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Callable, Awaitable
from playwright.async_api import async_playwright, TimeoutError as PWTimeoutError

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("AuraThreadsPublisher")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# =====================================================================
# 🧭 실패 분류 · 워크플로 상태 · 가디언 상수 (구조적 재설계 핵심)
# =====================================================================
class FailureKind(str, Enum):
    TRANSIENT = "TRANSIENT"   # 재시도 가능 (네트워크/렌더 지연/오버레이)
    SESSION = "SESSION"       # 세션 만료 → 재인증 필요
    UI_DRIFT = "UI_DRIFT"     # 셀렉터/레이아웃 변경 → 어댑터 갱신 필요
    FATAL = "FATAL"           # 즉시 중단 (설정 오류/파일 없음)

class Stage(str, Enum):
    BOOT = "BOOT"
    SESSION_GATE = "SESSION_GATE"
    NAVIGATE = "NAVIGATE"
    COMPOSER_OPEN = "COMPOSER_OPEN"
    CAPTION_INPUT = "CAPTION_INPUT"
    MEDIA_UPLOAD = "MEDIA_UPLOAD"
    POST_SUBMIT = "POST_SUBMIT"
    REPLY_CHAIN = "REPLY_CHAIN"
    PROOF_CAPTURE = "PROOF_CAPTURE"
    PERSIST = "PERSIST"
    DONE = "DONE"

class PublishError(Exception):
    def __init__(self, kind: FailureKind, stage: Stage, message: str, cause: Optional[BaseException] = None):
        super().__init__(f"[{kind.value}@{stage.value}] {message}")
        self.kind = kind
        self.stage = stage
        self.cause = cause

# 타임아웃 계층 (페이지/셀렉터/전체 워크플로)
TIMEOUT_PAGE_MS = 25_000
TIMEOUT_SELECTOR_MS = 12_000
TIMEOUT_WORKFLOW_SEC = 180
# 슬롯 가디언 정책
SLOT_MAX_ATTEMPTS = 3
SLOT_BACKOFF_BASE_SEC = 5.0
SLOT_BACKOFF_CAP_SEC = 60.0
CIRCUIT_FAIL_THRESHOLD = 3
CIRCUIT_COOLDOWN_SEC = 300
# 📂 경로 기준점 (반드시 상수 정의보다 먼저 선언되어야 함)
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
# 하트비트
HEARTBEAT_FILE = CURRENT_DIR / "threads_publisher_heartbeat.json"
# 🔒 프로필 물리 격리: meta_chrome_profile 과 완전 분리된 스레드 전용 프로필
PROFILE_DIR = CURRENT_DIR / "threads_chrome_profile"
SESSION_FILE = CURRENT_DIR / "threads_session.json"
# 🧬 불변 골든 세션 스냅샷 (자가치유 원본)
GOLDEN_SESSION_FILE = CURRENT_DIR / "threads_session_GOLDEN.json"
COOKIE_FILE = CURRENT_DIR / "threads_cookies.json"
META_SESSION_FILE = CURRENT_DIR / "meta_session.json"
HISTORY_FILE = CURRENT_DIR / "threads_publish_history.json"
VERIFIED_FLAG_FILE = CURRENT_DIR / "threads_session_verified.json"

# 🍪 스레드(Threads) 인증에 실제로 유효한 도메인 화이트리스트
THREADS_DOMAINS = (".threads.net", ".threads.com", ".instagram.com")
# 🚫 페이스북 전용 쿠키(절대 threads.net으로 재매핑 금지)
FACEBOOK_ONLY_COOKIE_NAMES = {
    "c_user", "xs", "datr", "sb", "fr", "presence", "wd", "dpr",
    "locale", "m_pixel_ratio", "spin", "i_user", "cppo", "vpd", "lu",
}
# 🔑 스레드 로그인 증명 핵심 쿠키
THREADS_AUTH_COOKIE_NAMES = {"sessionid", "ds_user_id"}



# =====================================================================
# 🧬 원자적 파일 유틸 (temp → fsync → os.replace)
# =====================================================================
def _atomic_copy(src: Path, dst: Path) -> bool:
    """원본 → 대상 원자적 복사 (불변 스냅샷 생성/복원용)

    ⚠️ Windows 주의: 읽기전용("rb") 핸들에 os.fsync() 를 호출하면
       [Errno 9] Bad file descriptor 가 발생한다.
       반드시 쓰기 가능 핸들("r+b")에서 fsync 를 수행해야 한다.
    """
    try:
        if not src.exists() or src.stat().st_size < 20:
            return False
        dst.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix=f".{dst.stem}_", suffix=".tmp", dir=str(dst.parent))
        os.close(fd)
        try:
            shutil.copyfile(src, tmp_name)
            # ✅ Windows 안전: 쓰기 가능 핸들에서 fsync
            with open(tmp_name, "r+b") as f:
                os.fsync(f.fileno())
            os.replace(tmp_name, dst)
            return True
        except Exception:
            try:
                if os.path.exists(tmp_name):
                    os.unlink(tmp_name)
            except Exception:
                pass
            raise
    except Exception as e:
        logger.warning(f"⚠️ 원자적 복사 실패({src.name} → {dst.name}): {e}")
        return False


def sanitize_threads_caption(raw_text: str) -> str:
    """스레드 500자 제한 맞춤 본문 정제"""
    if not raw_text:
        return ""
    lines = raw_text.split("\n")
    clean = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s.startswith("=") or s.startswith("•") or "주제:" in s or "의상:" in s or "산출 규격:" in s or "구성 안내" in s:
            continue
        clean.append(s)
    
    body = "\n\n".join(clean)
    if len(body) > 420:
        body = body[:400] + "..."
    return body


class AuraThreadsPublisher:
    """💖 Aura 전용 스레드(Threads) 독립 레고 블록 발행기"""

    BRAND = "aura"
    BRAND_NAME = "Aura AI 데이팅"
    OFFICIAL_SEARCH_KEYWORD = "아우라AI데이팅"
    LANDING_URL = "https://aura-ai-dating.vercel.app/"

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.profile_dir = PROFILE_DIR
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = SESSION_FILE
        self.golden_file = GOLDEN_SESSION_FILE
        # 🧯 서킷브레이커 상태 (프로세스 내)
        self._circuit_fail_count = 0
        self._circuit_open_until: Optional[datetime] = None
        # 🧭 워크플로 상태 추적
        self._stage: Stage = Stage.BOOT
        self._run_id: str = ""
        self._idempotency_key: str = ""

    # ------------------------------------------------------------------
    # 🧭 상태 전이 · 하트비트 · 서킷브레이커 (관측/복구 폐루프)
    # ------------------------------------------------------------------
    def _enter(self, stage: Stage) -> None:
        self._stage = stage
        logger.info(f"🧭 [STAGE] {stage.value} (run_id={self._run_id})")
        self._heartbeat(stage)

    def _heartbeat(self, stage: Stage, extra: Optional[Dict[str, Any]] = None) -> None:
        try:
            payload = {
                "run_id": self._run_id,
                "stage": stage.value,
                "ts": datetime.now().isoformat(),
                "pid": os.getpid(),
            }
            if extra:
                payload.update(extra)
            tmp = HEARTBEAT_FILE.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, HEARTBEAT_FILE)
        except Exception as he:
            logger.debug(f"heartbeat 기록 실패(무시): {he}")

    def _circuit_guard(self) -> None:
        if self._circuit_open_until and datetime.now() < self._circuit_open_until:
            remain = int((self._circuit_open_until - datetime.now()).total_seconds())
            raise PublishError(
                FailureKind.TRANSIENT, self._stage,
                f"서킷브레이커 OPEN (잔여 {remain}s) — 반복 실패로 인한 보호 정지"
            )

    def _circuit_record(self, ok: bool) -> None:
        if ok:
            self._circuit_fail_count = 0
            self._circuit_open_until = None
            return
        self._circuit_fail_count += 1
        if self._circuit_fail_count >= CIRCUIT_FAIL_THRESHOLD:
            self._circuit_open_until = datetime.now() + timedelta(seconds=CIRCUIT_COOLDOWN_SEC)
            logger.error(
                f"🔴 [CIRCUIT] 연속 {self._circuit_fail_count}회 실패 → "
                f"{CIRCUIT_COOLDOWN_SEC}s 쿨다운 진입"
            )

    @staticmethod
    def _make_idempotency_key(caption: str, media: List[str]) -> str:
        h = hashlib.sha256()
        h.update(caption.encode("utf-8"))
        for m in media:
            h.update(Path(m).name.encode("utf-8"))
        return h.hexdigest()[:24]

    def _is_duplicate(self, key: str) -> bool:
        """멱등키 기반 중복 발행 방지 (최근 24h 내 동일 키 SUCCESS 존재 시 차단)"""
        if not HISTORY_FILE.exists():
            return False
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
            cutoff = datetime.now() - timedelta(hours=24)
            for rec in history[-50:]:
                if rec.get("idempotency_key") != key:
                    continue
                if rec.get("status") != "SUCCESS":
                    continue
                try:
                    ts = datetime.fromisoformat(rec.get("published_at", ""))
                except Exception:
                    continue
                if ts >= cutoff:
                    return True
        except Exception as de:
            logger.warning(f"멱등 검사 예외(무시): {de}")
        return False

    # ------------------------------------------------------------------
    # 🧬 GOLDEN SESSION 불변 스택 (Self-Healing)
    # ------------------------------------------------------------------
    @staticmethod
    def _read_cookie_list(path: Path) -> List[Dict[str, Any]]:
        """쿠키 JSON 파일에서 cookies 리스트만 안전 추출"""
        try:
            if not path.exists() or path.stat().st_size < 20:
                return []
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                ck = data.get("cookies")
                return [c for c in ck if isinstance(c, dict)] if isinstance(ck, list) else []
            if isinstance(data, list):
                return [c for c in data if isinstance(c, dict)]
        except Exception:
            return []
        return []

    @classmethod
    def _has_threads_auth(cls, cookies: List[Dict[str, Any]]) -> bool:
        """스레드 로그인 증명 쿠키(sessionid / ds_user_id)가 실제로 존재하는가"""
        names = {str(c.get("name", "")).lower() for c in (cookies or []) if isinstance(c, dict)}
        return bool(names & THREADS_AUTH_COOKIE_NAMES)

    def _is_session_valid(self, path: Path) -> bool:
        """세션 파일이 '유효 인증 쿠키'를 담고 있는지 판정"""
        return self._has_threads_auth(self._read_cookie_list(path))

    def ensure_golden_session(self) -> Dict[str, Any]:
        """
        🧬 세션 / GOLDEN 2계층 자가치유 게이트

        a. SESSION_FILE 이 없거나 유효 인증 쿠키(sessionid / ds_user_id)가 없으면
           → GOLDEN_SESSION_FILE 이 존재할 때 즉시 threads_session.json 으로 복원(Self-Healing)
        b. SESSION_FILE 이 존재하고 유효한데 GOLDEN_SESSION_FILE 이 아직 없으면
           → 즉시 최초 1회 GOLDEN_SESSION_FILE 로 원자적 복사 백업(불변 스냅샷 생성)

        반환: {"ok": bool, "action": "pass"|"golden_created"|"restored"|"no_source"}
        """
        session_ok = self._is_session_valid(self.session_file)
        golden_ok = self._is_session_valid(self.golden_file)

        # (a) 세션 부재/손상 → GOLDEN 에서 자동 복원
        if not session_ok:
            if golden_ok:
                if _atomic_copy(self.golden_file, self.session_file):
                    logger.warning(
                        f"🩹 [SELF-HEALING] threads_session.json 손상/부재 → "
                        f"GOLDEN 세션으로 즉시 복원 완료 ({self.golden_file.name})"
                    )
                    return {"ok": True, "action": "restored"}
                logger.warning("⚠️ GOLDEN 복원 시도 실패 (원자적 복사 오류)")
                return {"ok": False, "action": "no_source"}
            logger.warning("⚠️ threads_session.json 무효 + GOLDEN 세션도 없음 (1회 연동 필요)")
            return {"ok": False, "action": "no_source"}

        # (b) 세션 정상 + GOLDEN 부재 → 최초 1회 불변 스냅샷 생성
        if not golden_ok:
            if _atomic_copy(self.session_file, self.golden_file):
                logger.info(
                    f"🧬 [GOLDEN 생성] 정상 세션 최초 1회 불변 스냅샷 백업 완료 → {self.golden_file.name}"
                )
                return {"ok": True, "action": "golden_created"}
            logger.warning("⚠️ GOLDEN 최초 백업 실패 (세션은 정상이므로 발행은 계속 진행)")

        return {"ok": True, "action": "pass"}

    def sync_golden_session(self) -> bool:
        """최신 정상 세션을 GOLDEN 에 동기화 (불변 스택 갱신)"""
        if not self._is_session_valid(self.session_file):
            logger.warning("⚠️ GOLDEN 동기화 스킵: 현재 세션에 인증 쿠키가 없습니다.")
            return False
        ok = _atomic_copy(self.session_file, self.golden_file)
        if ok:
            logger.info(f"🧬 [GOLDEN 동기화] 최신 정상 세션 → {self.golden_file.name}")
        return ok

    async def _save_session_atomic(self, context) -> bool:
        """
        발행 성공 후 세션 원자적 저장 + GOLDEN 동시 갱신
        - storage_state 는 임시 파일에 먼저 쓰고 fsync 후 os.replace 로 교체
        - 저장된 세션에 인증 쿠키가 실제로 있을 때만 GOLDEN 동기화
        """
        tmp_path = self.session_file.with_suffix(".json.tmp")
        try:
            await context.storage_state(path=str(tmp_path))
            # ✅ Windows 안전: 쓰기 가능 핸들에서 fsync
            with open(tmp_path, "r+b") as f:
                os.fsync(f.fileno())
            os.replace(tmp_path, self.session_file)
            logger.info(f"💾 세션 원자적 저장 완료: {self.session_file.name}")
        except Exception as e:
            logger.warning(f"⚠️ 세션 원자적 저장 실패: {e}")
            try:
                if tmp_path.exists():
                    tmp_path.unlink()
            except Exception:
                pass
            return False

        return self.sync_golden_session()

    def _prepare_cookies(self) -> List[Dict[str, Any]]:
        # ------------------------------------------------------------
        # [0단계] 🧬 GOLDEN 세션 자가치유 (Self-Healing) — 쿠키 수집 이전 선행
        # ------------------------------------------------------------
        try:
            heal = self.ensure_golden_session()
            logger.info(f"🧬 GOLDEN 세션 게이트: {heal['action']} (ok={heal['ok']})")
        except Exception as he:
            logger.warning(f"⚠️ GOLDEN 세션 게이트 예외(무시하고 계속): {he}")

        pw_cookies = []
        # 1. meta_session.json 로드
        meta_file = CURRENT_DIR / "meta_session.json"
        if meta_file.exists():
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    meta_cookies = data if isinstance(data, list) else data.get("cookies", [])
                for c in meta_cookies:
                    domain = c.get("domain", "")
                    if "instagram.com" in domain or "facebook.com" in domain:
                        pw = {
                            "name": c["name"],
                            "value": str(c["value"]),
                            "domain": domain,
                            "path": c.get("path", "/"),
                            "secure": c.get("secure", True),
                            "httpOnly": c.get("httpOnly", False)
                        }
                        if c.get("sameSite") in ["Strict", "Lax", "None"]:
                            pw["sameSite"] = c["sameSite"]
                        elif c.get("sameSite") == "no_restriction":
                            pw["sameSite"] = "None"
                        pw_cookies.append(pw)
                        if "instagram.com" in domain:
                            for td in [".threads.com", ".threads.net"]:
                                tc = dict(pw)
                                tc["domain"] = td
                                pw_cookies.append(tc)
            except Exception as me:
                logger.warning(f"메타 세션 쿠키 파싱 예외: {me}")

        # 2. threads_cookies.json 로드
        if COOKIE_FILE.exists():
            try:
                with open(COOKIE_FILE, "r", encoding="utf-8") as f:
                    raw_cookies = json.load(f)
                for c in raw_cookies:
                    pw_c = {
                        "name": c["name"],
                        "value": str(c["value"]),
                        "domain": c["domain"],
                        "path": c.get("path", "/"),
                        "secure": c.get("secure", True),
                        "httpOnly": c.get("httpOnly", False),
                    }
                    if c.get("sameSite") in ["Strict", "Lax", "None"]:
                        pw_c["sameSite"] = c["sameSite"]
                    elif c.get("sameSite") == "no_restriction":
                        pw_c["sameSite"] = "None"
                    elif c.get("sameSite") == "lax":
                        pw_c["sameSite"] = "Lax"
                    pw_cookies.append(pw_c)
                    for d in [".threads.net", ".threads.com", ".instagram.com"]:
                        dc = dict(pw_c)
                        dc["domain"] = d
                        pw_cookies.append(dc)
            except Exception as ex:
                logger.warning(f"쿠키 파싱 오류: {ex}")

        # 3. threads_session.json 로드
        if SESSION_FILE.exists():
            try:
                with open(SESSION_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    t_cookies = data if isinstance(data, list) else data.get("cookies", [])
                for c in t_cookies:
                    domain = c.get("domain", ".threads.net")
                    pw = {
                        "name": c["name"],
                        "value": str(c["value"]),
                        "domain": domain,
                        "path": c.get("path", "/"),
                        "secure": c.get("secure", True),
                        "httpOnly": c.get("httpOnly", False)
                    }
                    if c.get("sameSite") in ["Strict", "Lax", "None"]:
                        pw["sameSite"] = c["sameSite"]
                    pw_cookies.append(pw)
                    for td in [".threads.net", ".instagram.com"]:
                        if td != domain:
                            tc = dict(pw)
                            tc["domain"] = td
                            pw_cookies.append(tc)
            except Exception as te:
                logger.warning(f"스레드 세션 쿠키 파싱 예외: {te}")

        return pw_cookies

    # ------------------------------------------------------------------
    # 🧩 브라우저 어댑터 (오버레이 정책 · 로케이터 전략 분리)
    # ------------------------------------------------------------------
    async def _dismiss_overlays(self, page) -> None:
        """오버레이 정책: Terms/쿠키 배너만 '정책적으로' 제거 (부작용 최소화)"""
        try:
            await page.evaluate("""() => {
                const fixedOverlays = Array.from(document.querySelectorAll("div")).filter(d => {
                    const style = window.getComputedStyle(d);
                    const txt = d.innerText || '';
                    return (style.position === 'fixed' || style.position === 'sticky')
                        && style.bottom === '0px'
                        && (txt.includes('Terms') || txt.includes('쿠키') || txt.includes('Cookie'));
                });
                fixedOverlays.forEach(b => b.remove());
            }""")
        except Exception as oe:
            logger.debug(f"오버레이 제거 예외(무시): {oe}")

    async def _wait_composer(self, page, timeout_ms: int = TIMEOUT_SELECTOR_MS):
        """작성창(textbox) 대기 — 로케이터 전략 단일화"""
        return await page.wait_for_selector(
            "div[role='textbox'][contenteditable='true'], div[data-lexical-editor='true']",
            timeout=timeout_ms,
        )

    async def _open_composer(self, page) -> None:
        """작성창 열기 (4중 Fallback + 명시적 실패 분류)"""
        self._enter(Stage.COMPOSER_OPEN)
        for attempt in range(6):
            try:
                quick = await page.query_selector(
                    "div:has-text('새로운 소식을 공유해보세요'), div:has-text('What\\'s new?')"
                )
                if quick and await quick.is_visible():
                    await quick.click()
                    await asyncio.sleep(1.0)
            except Exception as qe:
                logger.debug(f"quick composer 클릭 예외(무시): {qe}")

            if not await page.query_selector(
                "div[role='textbox'][contenteditable='true'], div[data-lexical-editor='true']"
            ):
                try:
                    await page.evaluate("""() => {
                        const btns = Array.from(document.querySelectorAll("div[role='button'], button, a"));
                        const createBtn = btns.find(b => {
                            const t = (b.innerText || '').trim();
                            const aria = b.getAttribute('aria-label') || '';
                            return t.includes('새로운 스레드') || t.includes('New thread')
                                || aria.includes('새로운 스레드') || aria.includes('Create');
                        });
                        if (createBtn) { createBtn.click(); return; }
                        const allBtns = Array.from(document.querySelectorAll("div[role='button']"));
                        if (allBtns.length > 0) allBtns[allBtns.length - 1].click();
                    }""")
                    await asyncio.sleep(1.0)
                except Exception as ce:
                    logger.debug(f"create 버튼 클릭 예외(무시): {ce}")

            if not await page.query_selector(
                "div[role='textbox'][contenteditable='true'], div[data-lexical-editor='true']"
            ):
                try:
                    await page.keyboard.press("c")
                    await asyncio.sleep(1.0)
                except Exception as ke:
                    logger.debug(f"단축키 'c' 예외(무시): {ke}")

            tb = await page.query_selector(
                "div[role='textbox'][contenteditable='true'], div[data-lexical-editor='true']"
            )
            if tb and await tb.is_visible():
                logger.info("✅ 작성창(textbox) 활성화 확인")
                return
            await asyncio.sleep(1.0)

        raise PublishError(
            FailureKind.UI_DRIFT, Stage.COMPOSER_OPEN,
            "작성창(textbox) 활성화 실패 — 셀렉터/레이아웃 변경 의심"
        )

    async def _submit_post(self, page) -> None:
        """본문 게시 버튼 클릭 (명시적 실패 분류)"""
        self._enter(Stage.POST_SUBMIT)
        for _ in range(5):
            posted = await page.evaluate("""() => {
                const dialog = document.querySelector("div[role='dialog']") || document;
                const btns = Array.from(dialog.querySelectorAll("div[role='button'], button"));
                const postBtn = btns.find(b => {
                    const t = (b.innerText || '').trim();
                    const ariaDisabled = b.getAttribute('aria-disabled');
                    const disabled = b.getAttribute('disabled');
                    return (t === 'Post' || t === '게시') && ariaDisabled !== 'true' && disabled === null;
                });
                if (postBtn) { postBtn.click(); return true; }
                return false;
            }""")
            if posted:
                return
            await asyncio.sleep(1.0)

        publish_btn = await page.query_selector(
            "div[role='dialog'] div[role='button']:has-text('Post'), "
            "div[role='dialog'] button:has-text('Post'), "
            "div[role='dialog'] div[role='button']:has-text('게시')"
        )
        if publish_btn:
            await publish_btn.click(force=True)
            return

        raise PublishError(
            FailureKind.UI_DRIFT, Stage.POST_SUBMIT,
            "게시(Post) 버튼을 찾지 못했습니다."
        )

    # ------------------------------------------------------------------
    # 🛡️ 슬롯 가디언 (지수백오프 + 서킷브레이커 + 재시도 주체)
    # ------------------------------------------------------------------
    async def _slot_guardian(
        self,
        task: Callable[[], Awaitable[Dict[str, Any]]],
        slot_label: str = "default",
    ) -> Dict[str, Any]:
        last_err: Optional[BaseException] = None
        for attempt in range(1, SLOT_MAX_ATTEMPTS + 1):
            self._circuit_guard()
            try:
                result = await task()
                self._circuit_record(ok=True)
                return result
            except PublishError as pe:
                last_err = pe
                # SESSION / FATAL 은 재시도 무의미 → 즉시 에스컬레이션
                if pe.kind in (FailureKind.SESSION, FailureKind.FATAL):
                    self._circuit_record(ok=False)
                    raise
                delay = min(
                    SLOT_BACKOFF_BASE_SEC * (2 ** (attempt - 1)),
                    SLOT_BACKOFF_CAP_SEC,
                )
                logger.warning(
                    f"🛡️ [SLOT:{slot_label}] 시도 {attempt}/{SLOT_MAX_ATTEMPTS} 실패 "
                    f"({pe.kind.value}) → {delay:.1f}s 백오프 후 재시도"
                )
                await asyncio.sleep(delay)
            except Exception as e:
                last_err = e
                delay = min(
                    SLOT_BACKOFF_BASE_SEC * (2 ** (attempt - 1)),
                    SLOT_BACKOFF_CAP_SEC,
                )
                logger.warning(
                    f"🛡️ [SLOT:{slot_label}] 시도 {attempt}/{SLOT_MAX_ATTEMPTS} 예외 "
                    f"({type(e).__name__}) → {delay:.1f}s 백오프"
                )
                await asyncio.sleep(delay)

        self._circuit_record(ok=False)
        raise PublishError(
            FailureKind.TRANSIENT, self._stage,
            f"슬롯 '{slot_label}' {SLOT_MAX_ATTEMPTS}회 재시도 모두 실패",
            cause=last_err,
        )

    async def publish_thread(
        self,
        caption: Optional[str] = None,
        image_paths: Optional[List[str]] = None,
        first_reply_text: Optional[str] = None,
        content_generator: Optional[Callable[[], Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """스레드에 본문 + 카드뉴스 이미지 + 첫 댓글 체인 자동 발행 (가디언 래핑)

        🧬 지연 생성(Lazy Evaluation) 계약:
          - content_generator 가 주어지면, 브라우저가 열리고 오버레이가 제거되며
            작성창(textbox)이 실제로 클릭되어 커서가 깜빡이는 것이 100% 확인된
            '직후'에 단 1회만 호출된다.
          - 세션 만료 / 작성창 미개설 / 네비게이션 실패 시에는 절대 호출되지 않는다.
            (Gemini 등 외부 LLM 호출 0회 보장)
          - content_generator 는 {"caption": str, "first_reply_text": str} 형태의
            dict 를 반환해야 한다. (동기 함수 권장)
        """
        self._run_id = uuid.uuid4().hex[:12]
        self._enter(Stage.BOOT)

        # 🧬 지연 생성 모드: 본문/댓글은 작성창 확보 후에만 결정된다.
        lazy_mode = content_generator is not None
        if lazy_mode:
            logger.info("🧬 [LAZY] content_generator 감지 → 본문 생성은 작성창 확보 후로 지연")
            caption = sanitize_threads_caption(caption or "")
            if not first_reply_text:
                first_reply_text = None  # 생성기 결과로 채워짐
        else:
            caption = sanitize_threads_caption(caption or "")
            if not caption:
                caption = (
                    "📍 [500m 안심 레이더 & 안심 번개 매칭]\n\n"
                    "집 주소 노출될까 봐 불안하셨죠?\n"
                    "내 집 앞 500m 안심 지터링 보안으로 안전하게!\n\n"
                    "거리와 취향까지 딱 맞는 내 반경 500m 인연을 지금 확인해보세요 ✨\n\n"
                    "#Aura #데이팅 #소개팅 #안심매칭 #2030"
                )

            if not first_reply_text:
                first_reply_text = (
                    f"💖 2030 매력 진단 & AI 매칭 1분 무료 리포트\n"
                    f"네이버에 '{self.OFFICIAL_SEARCH_KEYWORD}' 한번 검색해보세요!\n"
                    f"👉 {self.LANDING_URL}"
                )

        valid_media = []
        if image_paths:
            for p in image_paths:
                fpath = Path(p)
                if fpath.exists() and fpath.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov"]:
                    valid_media.append(str(fpath.resolve()))

        is_video = any(p.endswith((".mp4", ".mov")) for p in valid_media)
        media_type = "동영상(릴스 숏폼)" if is_video else "카드뉴스 이미지"

        # 🧬 멱등키 기반 중복 발행 방지
        #    (지연 모드에서는 본문이 아직 없으므로 미디어 기준 임시 키 사용)
        self._idempotency_key = self._make_idempotency_key(caption or "", valid_media)
        if not lazy_mode and self._is_duplicate(self._idempotency_key):
            logger.warning(
                f"♻️ [DEDUP] 동일 콘텐츠 24h 내 발행 이력 존재 "
                f"(key={self._idempotency_key}) → 중복 발행 차단"
            )
            return {
                "success": True,
                "brand": self.BRAND,
                "message": "♻️ 중복 발행 방지(멱등키 일치) — 기존 발행 유지",
                "details": {"idempotency_key": self._idempotency_key, "dedup": True},
            }

        # 🧬 세션 게이트 (명시적 실패 분류)
        self._enter(Stage.SESSION_GATE)
        try:
            heal = self.ensure_golden_session()
            logger.info(f"🧬 GOLDEN 세션 게이트: {heal['action']} (ok={heal['ok']})")
            if not heal["ok"]:
                raise PublishError(
                    FailureKind.SESSION, Stage.SESSION_GATE,
                    "유효 세션/GOLDEN 부재 — 재인증 필요"
                )
        except PublishError:
            raise
        except Exception as he:
            raise PublishError(
                FailureKind.SESSION, Stage.SESSION_GATE,
                f"세션 게이트 예외: {he}", cause=he
            )

        logger.info(
            f"🚀 [Aura Threads] 스레드 발행 시작 "
            f"(run_id={self._run_id}, 글자수: {len(caption or '')}자, "
            f"{media_type}: {len(valid_media)}개, lazy={lazy_mode})"
        )

        # 🛡️ 슬롯 가디언으로 전체 워크플로 래핑 (재시도 주체 확립)
        return await self._slot_guardian(
            lambda: self._publish_once(
                caption, valid_media, first_reply_text, is_video, media_type,
                content_generator=content_generator,
            ),
            slot_label="threads_main",
        )

    async def _publish_once(
        self,
        caption: Optional[str],
        valid_media: List[str],
        first_reply_text: Optional[str],
        is_video: bool,
        media_type: str,
        content_generator: Optional[Callable[[], Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """단일 발행 시도 (워크플로 상태기계)"""
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 900}
            )
            
            cookies = self._prepare_cookies()
            if cookies:
                await context.add_cookies(cookies)

            page = context.pages[0] if context.pages else await context.new_page()
            page.set_default_timeout(TIMEOUT_SELECTOR_MS)

            try:
                # 1. Threads 메인 접속
                self._enter(Stage.NAVIGATE)
                logger.info("1. Threads 메인 페이지 접속 중...")
                await page.goto("https://www.threads.net/", wait_until="domcontentloaded", timeout=TIMEOUT_PAGE_MS)
                await asyncio.sleep(2)

                # 1-1. 오버레이 정책 적용 + 세션 연결 모달
                await self._dismiss_overlays(page)
                try:
                    clicked_modal = await page.evaluate("""() => {
                        const all = Array.from(document.querySelectorAll("button, div[role='button'], a, div"));
                        const cont = all.find(el => el.innerText && (
                            el.innerText.trim().includes('Continue with Instagram')
                            || el.innerText.trim().includes('Log in with Instagram')
                            || el.innerText.trim().includes('aura_ai_dating')
                        ));
                        if (cont) {
                            const clickable = cont.closest("button, div[role='button'], a") || cont;
                            clickable.click();
                            return true;
                        }
                        return false;
                    }""")
                    if clicked_modal:
                        logger.info("👉 'Continue with Instagram' 모달 클릭 → 세션 연결 대기")
                        await asyncio.sleep(4)
                except Exception as me:
                    logger.warning(f"모달 클릭 예외(계속 진행): {me}")

                # 2. 작성창 열기 (어댑터 위임)
                logger.info("2. 스레드 작성창 열기...")
                await self._open_composer(page)

                # 3. 본문 텍스트 입력
                self._enter(Stage.CAPTION_INPUT)
                logger.info("3. 캡션 텍스트 입력 중...")
                textbox = await self._wait_composer(page)
                await textbox.click()
                await asyncio.sleep(0.4)
                await page.keyboard.press("Control+A")
                await page.keyboard.press("Backspace")
                await asyncio.sleep(0.2)

                # 🧬 [LAZY EVALUATION] 작성창 클릭·커서 활성 100% 확인 직후에만 생성기 1회 호출
                #    → 세션 만료/작성창 미개설/네비게이션 실패 시 여기까지 도달하지 않으므로
                #      content_generator(Gemini 등)는 절대 실행되지 않는다. (호출 0회 보장)
                if content_generator is not None:
                    try:
                        focused = await page.evaluate("""() => {
                            const el = document.activeElement;
                            if (!el) return false;
                            const editable = el.getAttribute('contenteditable');
                            const role = el.getAttribute('role');
                            return editable === 'true' || role === 'textbox'
                                || !!el.closest("div[role='textbox'][contenteditable='true']")
                                || !!el.closest("div[data-lexical-editor='true']");
                        }""")
                    except Exception as fe:
                        focused = False
                        logger.debug(f"포커스 확인 예외(무시): {fe}")

                    if not focused:
                        raise PublishError(
                            FailureKind.UI_DRIFT, Stage.CAPTION_INPUT,
                            "작성창 포커스 미확인 — content_generator 호출 차단(지연 생성 보호)"
                        )

                    logger.info("🧬 [LAZY] 작성창 포커스 100% 확인 → content_generator 1회 호출")
                    try:
                        gen = content_generator()
                        if asyncio.iscoroutine(gen):
                            gen = await gen
                    except Exception as ge:
                        raise PublishError(
                            FailureKind.TRANSIENT, Stage.CAPTION_INPUT,
                            f"content_generator 실행 실패: {ge}", cause=ge
                        )

                    if not isinstance(gen, dict):
                        raise PublishError(
                            FailureKind.FATAL, Stage.CAPTION_INPUT,
                            f"content_generator 반환 형식 오류(dict 아님): {type(gen).__name__}"
                        )

                    gen_caption = sanitize_threads_caption(gen.get("caption") or "")
                    if gen_caption:
                        caption = gen_caption
                    gen_reply = gen.get("first_reply_text")
                    if gen_reply:
                        first_reply_text = gen_reply

                    if not caption:
                        raise PublishError(
                            FailureKind.FATAL, Stage.CAPTION_INPUT,
                            "content_generator 가 빈 본문을 반환했습니다."
                        )

                    # 🧬 생성된 본문 기준으로 멱등키 재계산 + 중복 발행 차단
                    self._idempotency_key = self._make_idempotency_key(caption, valid_media)
                    if self._is_duplicate(self._idempotency_key):
                        logger.warning(
                            f"♻️ [DEDUP] 생성 본문이 24h 내 발행 이력과 일치 "
                            f"(key={self._idempotency_key}) → 중복 발행 차단"
                        )
                        try:
                            await context.close()
                        except Exception:
                            pass
                        return {
                            "success": True,
                            "brand": self.BRAND,
                            "message": "♻️ 중복 발행 방지(멱등키 일치) — 기존 발행 유지",
                            "details": {"idempotency_key": self._idempotency_key, "dedup": True},
                        }

                    logger.info(
                        f"🧬 [LAZY] 생성 완료 → 본문 {len(caption)}자 / "
                        f"1댓글 {'있음' if first_reply_text else '없음'}"
                    )

                await page.keyboard.insert_text(caption)
                await asyncio.sleep(1.2)

                # 4. 미디어 첨부
                if valid_media:
                    self._enter(Stage.MEDIA_UPLOAD)
                    logger.info(f"4. {media_type} {len(valid_media)}개 업로드 중...")
                    file_input = await page.query_selector("input[type='file']")
                    if not file_input:
                        raise PublishError(
                            FailureKind.UI_DRIFT, Stage.MEDIA_UPLOAD,
                            "파일 입력(input[type=file]) 미발견"
                        )
                    await file_input.set_input_files(valid_media)
                    wait_sec = 14 if is_video else 6
                    logger.info(f"   미디어 전송 완료 → 렌더/인코딩 대기 {wait_sec}s")
                    await asyncio.sleep(wait_sec)

                # 5. 본문 게시
                logger.info("5. 본문 [Post / 게시] 버튼 클릭...")
                await self._submit_post(page)
                logger.info("   게시 요청 전송 완료 → 서버 반영 대기 (10s)")
                await asyncio.sleep(10)

                # 6. [2단계] 첫 번째 타래 댓글 (방금 올린 본문 글의 고유 상세 페이지로 직접 이동하여 답글 체인 작성)
                if first_reply_text:
                    logger.info("6. [2단계] 첫 번째 타래 댓글(답글) 작성 시작...")
                    try:
                        # 6-1. 내 프로필로 이동하여 방금 올린 본문 글의 URL 링크 추출
                        await page.goto("https://www.threads.net/@aura_ai_dating", wait_until="domcontentloaded", timeout=25000)
                        await asyncio.sleep(4)

                        # Terms 제거
                        await page.evaluate("""() => {
                            const fixedOverlays = Array.from(document.querySelectorAll("div")).filter(d => {
                                const style = window.getComputedStyle(d);
                                return (style.position === 'fixed' || style.position === 'sticky') && style.bottom === '0px' && d.innerText && d.innerText.includes('Terms');
                            });
                            fixedOverlays.forEach(b => b.remove());
                        }""")

                        post_href = await page.evaluate("""() => {
                            const links = Array.from(document.querySelectorAll("a[href*='/post/']"));
                            if (links.length > 0) return links[0].getAttribute('href');
                            return null;
                        }""")
                        logger.info(f"   방금 올린 본문 글 링크: {post_href}")

                        if post_href:
                            post_url = f"https://www.threads.net{post_href}" if post_href.startswith("/") else post_href
                            logger.info(f"   본문 글 고유 상세 페이지 직접 이동: {post_url}")
                            await page.goto(post_url, wait_until="domcontentloaded", timeout=25000)
                            await asyncio.sleep(4)

                                                        # 상세 페이지 내 답글 입력창 클릭 (이미지 오버레이 차단 방지 Leaf Element 정밀 타겟팅)
                            clicked_reply = await page.evaluate("""() => {
                                const elements = Array.from(document.querySelectorAll("span, div"));
                                const replyEl = elements.reverse().find(el => {
                                    const t = (el.innerText || '').trim();
                                    return (t.startsWith('Reply to') || t.startsWith('답글')) && el.children.length === 0;
                                });
                                if (replyEl) {
                                    const clickable = replyEl.closest("div[role='button']") || replyEl;
                                    clickable.click();
                                    return true;
                                }
                                return false;
                            }""")
                            await asyncio.sleep(1.5)

                            reply_box = await page.wait_for_selector("div[role='textbox'][contenteditable='true'], div[data-lexical-editor='true']", timeout=10000)
                            if reply_box:
                                await reply_box.click()
                                await asyncio.sleep(0.5)
                                await page.keyboard.press("Control+A")
                                await page.keyboard.press("Backspace")
                                await asyncio.sleep(0.3)
                                await page.keyboard.insert_text(first_reply_text)
                                await asyncio.sleep(2.5)  # OpenGraph 미리보기 렌더링 대기

                                # 답글 전송 (Post 버튼 클릭 + Control+Enter 2중 보장)
                                reply_posted = await page.evaluate("""() => {
                                    const btns = Array.from(document.querySelectorAll("div[role='button'], button"));
                                    const postBtn = btns.find(b => {
                                        const t = (b.innerText || '').trim();
                                        const aria = b.getAttribute('aria-disabled');
                                        return (t === 'Post' || t === '게시' || t === 'Reply' || t === '답글') && aria !== 'true';
                                    });
                                    if (postBtn) {
                                        postBtn.click();
                                        return true;
                                    }
                                    return false;
                                }""")
                                if not reply_posted:
                                    await page.keyboard.press("Control+Enter")
                                await asyncio.sleep(4)
                                logger.info("   1번 타래 댓글 체인 부착 완료!")
                    except Exception as re:
                        logger.warning(f"⚠️ 타래 댓글 작성 예외: {re}")

                # 7. 본문 + 1번 타래 결합 최종 증빙 캡처
                logger.info("7. 본문 + 1번 타래 결합 최종 증빙 캡처 중...")
                proof_path = CURRENT_DIR / "threads_live_proof.png"
                try:
                    await page.screenshot(path=str(proof_path))
                except Exception:
                    pass
                logger.info(f"📸 게시 완료 라이브 증빙 캡처: {proof_path}")

                # 8. 세션 및 히스토리 보관
                # 8. 세션 및 히스토리 보관 (원자적 저장 + GOLDEN 동시 갱신)
                await self._save_session_atomic(context)

                # 9. 검증 완료 플래그 동기화 & 잔여 에러 스크린샷 정리
                verified_flag = CURRENT_DIR / "threads_session_verified.json"
                try:
                    with open(verified_flag, "w", encoding="utf-8") as vf:
                        json.dump({"verified_at": datetime.now().isoformat(), "brand": self.BRAND, "status": "authenticated"}, vf, indent=2)
                    err_file = CURRENT_DIR / "threads_error_screenshot.png"
                    if err_file.exists():
                        err_file.unlink()
                except Exception:
                    pass

                result_record = {
                    "brand": self.BRAND,
                    "published_at": datetime.now().isoformat(),
                    "caption_preview": caption[:60] + "...",
                    "media_count": len(valid_media),
                    "first_reply": first_reply_text,
                    "status": "SUCCESS",
                    "proof_screenshot": str(proof_path)
                }
                self._save_history(result_record)

                await context.close()
                return {
                    "success": True,
                    "brand": self.BRAND,
                    "message": f"🎉 [스레드 발행 성공] {self.BRAND_NAME} 콘텐츠가 Threads에 성공적으로 송출되었습니다!",
                    "details": result_record
                }

            except Exception as e:
                logger.error(f"❌ [Aura Threads] 발행 실패: {e}")
                fail_screenshot = CURRENT_DIR / "threads_error_screenshot.png"
                try:
                    await page.screenshot(path=str(fail_screenshot))
                except Exception:
                    pass

                # 실패 시 검증 플래그 파기 -> 관제판에 즉시 세션만료(빨간색) 반영
                try:
                    vf = CURRENT_DIR / "threads_session_verified.json"
                    if vf.exists():
                        vf.unlink()
                except Exception:
                    pass

                result_record = {
                    "brand": self.BRAND,
                    "published_at": datetime.now().isoformat(),
                    "caption_preview": caption[:60] + "..." if caption else "",
                    "media_count": len(valid_media),
                    "first_reply": first_reply_text,
                    "status": "FAILED",
                    "error": str(e),
                    "screenshot": str(fail_screenshot)
                }
                self._save_history(result_record)

                await context.close()
                return {
                    "success": False,
                    "brand": self.BRAND,
                    "error": str(e),
                    "screenshot": str(fail_screenshot)
                }

    def _save_history(self, record: Dict[str, Any]):
        history = []
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []
        history.append(record)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)


async def main():
    publisher = AuraThreadsPublisher(headless=True)
    target_folder = r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\아우라\아우라_08_500m안심레이더_20261001_1100"
    
    images = [str(Path(target_folder) / f"slide_{i}.png") for i in range(1, 6)]
    
    caption = (
        "📍 [500m 안심 레이더 & 성수동 테라스 번개]\n\n"
        "집 주소 노출될까 봐 불안하셨죠?\n"
        "내 집 앞 500m 안심 지터링 보안으로 집 주소 노출 없이 안전하게!\n\n"
        "거리와 취향까지 딱 맞는 내 반경 500m 인연을 지금 만나보세요 ✨\n\n"
        "#Aura #아우라 #데이팅 #소개팅 #안심매칭 #2030"
    )

    res = await publisher.publish_thread(
        caption=caption,
        image_paths=images,
        first_reply_text="💖 2030 매력 진단 & AI 매칭 리포트\n네이버에 '아우라AI데이팅' 한번 검색해보세요!\n👉 https://aura-ai-dating.vercel.app/"
    )
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
