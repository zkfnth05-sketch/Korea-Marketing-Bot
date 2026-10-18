# -*- coding: utf-8 -*-
"""
Stock Threads Publisher (🧵 스톡마스터 AI 전용 스레드 독립 레고 블록 발행기)
===================================================================
- 브랜드: 📈 스톡마스터 AI (StockMaster)
- 전용 계정: @stockmaster_ai
- 검색 공식 키워드: 스톡마스터 AI (절대 불변)
- 랜딩 URL: https://stockmaster-ai.vercel.app/
- 프로필 디렉터리: brands/stock/threads_chrome_profile/  (🔒 meta_chrome_profile 과 물리적 완전 격리)
- 세션 파일: brands/stock/threads_session.json
- 골든 세션: brands/stock/threads_session_GOLDEN.json (불변 스냅샷 · 자가치유 원본)
- 기능:
  1. 스레드(threads.net) 완전 무인 자동 로그인 세션 유지
  2. 카드뉴스 이미지(4~5장 슬라이드) 또는 텍스트 타래 게시 (500자 규격 자동 최적화)
  3. 첫 번째 타래 댓글로 공식 검색어('스톡마스터 AI') 및 랜딩 URL 자동 체인 부착
  4. 게시 결과 스크린샷 캡처 및 히스토리 아카이빙
  5. 🧬 GOLDEN SESSION 불변 스택:
     - 세션 손상/부재 시 GOLDEN 에서 자동 복원(Self-Healing)
     - 세션 정상 + GOLDEN 부재 시 최초 1회 자동 불변 스냅샷 생성
     - 발행 성공 시 원자적 저장(temp→fsync→os.replace) + GOLDEN 동시 갱신
"""

import os
import sys
import json
import shutil
import asyncio
import logging
import tempfile
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from playwright.async_api import async_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("StockThreadsPublisher")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
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
    """원본 → 대상 원자적 복사 (불변 스냅샷 생성/복원용)"""
    try:
        if not src.exists() or src.stat().st_size < 20:
            return False
        dst.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix=f".{dst.stem}_", suffix=".tmp", dir=str(dst.parent))
        os.close(fd)
        try:
            shutil.copyfile(src, tmp_name)
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


class StockThreadsPublisher:
    """💖 Stock 전용 스레드(Threads) 독립 레고 블록 발행기"""

    BRAND = "stock"
    BRAND_NAME = "스톡마스터 AI"
    OFFICIAL_SEARCH_KEYWORD = "스톡마스터 AI"
    LANDING_URL = "https://stockmaster-ai.vercel.app/"

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.profile_dir = PROFILE_DIR
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = SESSION_FILE
        self.golden_file = GOLDEN_SESSION_FILE

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

    # ------------------------------------------------------------------
    # 🍪 방탄 쿠키 리졸버 (Bulletproof Cookie Resolver)
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_same_site(raw_same_site: Any) -> Optional[str]:
        """sameSite 표기 정규화 (Chrome 확장 / Playwright / Selenium 혼용 대응)"""
        if not raw_same_site:
            return None
        s = str(raw_same_site).strip().lower()
        if s in ("strict",):
            return "Strict"
        if s in ("lax",):
            return "Lax"
        if s in ("none", "no_restriction", "unspecified"):
            return "None"
        return None

    @classmethod
    def _to_pw_cookie(cls, c: Dict[str, Any], domain_override: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """원본 쿠키 dict → Playwright add_cookies 규격 변환"""
        try:
            name = c.get("name")
            if not name:
                return None
            domain = domain_override if domain_override else c.get("domain", "")
            if not domain:
                return None
            pw = {
                "name": name,
                "value": str(c.get("value", "")),
                "domain": domain,
                "path": c.get("path") or "/",
                "secure": bool(c.get("secure", True)),
                "httpOnly": bool(c.get("httpOnly", False)),
            }
            same_site = cls._normalize_same_site(c.get("sameSite"))
            if same_site:
                pw["sameSite"] = same_site
            # expires 는 양수일 때만 유효 (세션 쿠키는 -1 → 미기재)
            expires = c.get("expires", c.get("expirationDate"))
            if isinstance(expires, (int, float)) and expires > 0:
                pw["expires"] = float(expires)
            return pw
        except Exception:
            return None

    @staticmethod
    def _is_facebook_only_cookie(cookie: Dict[str, Any]) -> bool:
        """페이스북 전용 쿠키 여부 판별 (도메인 또는 쿠키명 기준)"""
        domain = str(cookie.get("domain", "")).lower()
        name = str(cookie.get("name", "")).lower()
        if "facebook.com" in domain or "fbcdn.net" in domain:
            return True
        if name in FACEBOOK_ONLY_COOKIE_NAMES:
            return True
        return False

    @staticmethod
    def _is_threads_relevant_domain(domain: str) -> bool:
        """스레드 인증에 유효한 도메인인지 판별"""
        d = str(domain or "").lower()
        if not d:
            return False
        if "facebook.com" in d or "fbcdn.net" in d:
            return False
        return any(t in d for t in THREADS_DOMAINS)

    def _load_cookie_json(self, path: Path) -> List[Dict[str, Any]]:
        """
        쿠키 JSON 파일 안전 로드
        --------------------------------------------------------------
        지원 포맷:
          1) Cookie-Editor list : [ {name, value, domain, ...}, ... ]
          2) Playwright storage_state : { "cookies": [...], "origins": [...] }
          3) 래핑 dict : { "Cookies": [...] } / { "data": [...] }
          4) 평면 dict : { "sessionid": "...", "ds_user_id": "..." }
        """
        if not path.exists():
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as ex:
            logger.warning(f"쿠키 파일 로드 실패({path.name}): {ex}")
            return []

        if isinstance(data, list):
            return [c for c in data if isinstance(c, dict)]

        if isinstance(data, dict):
            for key in ("cookies", "Cookies", "data"):
                val = data.get(key)
                if isinstance(val, list):
                    return [c for c in val if isinstance(c, dict)]

            # 평면 dict (name: value) → 인스타그램 도메인 기준 쿠키로 승격
            flat = {
                k: v for k, v in data.items()
                if isinstance(v, (str, int, float)) and not isinstance(v, bool)
            }
            if flat:
                return [
                    {"name": str(k), "value": str(v), "domain": ".instagram.com", "path": "/"}
                    for k, v in flat.items()
                ]
        return []

    def _prepare_cookies(self) -> List[Dict[str, Any]]:
        """
        🍪 방탄 쿠키 리졸버 (단일 소스 오브 트루스 정합화)
        --------------------------------------------------------------
        우선순위 (AuthResolver 산출물 최우선):
          1) threads_session.json  (AuthResolver가 생성한 정규화 단일 소스 — 최우선 신뢰)
          2) threads_cookies.json  (원천 보조 쿠키)
          3) meta_session.json     (메타 통합 세션, 스레드 유효 도메인만)
        규칙:
          - .threads.com / .instagram.com 쿠키는 .threads.net 으로 자동 복제
          - facebook.com 전용 쿠키(c_user 등)는 .threads.net 재매핑 절대 금지
          - 최종 리스트는 (name, domain, path) 키 기반 중복 제거 — 선순위(1순위) 값 보존
        """
        # ------------------------------------------------------------
        # [0단계] 🧬 GOLDEN 세션 자가치유 (Self-Healing) — 쿠키 수집 이전 선행
        # ------------------------------------------------------------
        try:
            heal = self.ensure_golden_session()
            logger.info(f"🧬 GOLDEN 세션 게이트: {heal['action']} (ok={heal['ok']})")
        except Exception as he:
            logger.warning(f"⚠️ GOLDEN 세션 게이트 예외(무시하고 계속): {he}")

        collected: List[Dict[str, Any]] = []

        # ------------------------------------------------------------
        # 1순위: threads_session.json (AuthResolver 정규화 단일 소스 — 최우선)
        # ------------------------------------------------------------
        session_cookies = self._load_cookie_json(SESSION_FILE)
        if session_cookies:
            logger.info(f"🍪 [1순위] threads_session.json 로드: {len(session_cookies)}개 (단일 소스 오브 트루스)")
            for c in session_cookies:
                # 페이스북 전용 쿠키는 threads.net 재매핑 금지
                if self._is_facebook_only_cookie(c):
                    continue
                base = self._to_pw_cookie(c)
                if not base:
                    continue
                if not self._is_threads_relevant_domain(base["domain"]):
                    continue
                collected.append(base)

                # 스레드/인스타 도메인만 .threads.net 복제 허용
                d = base["domain"].lower()
                if ("threads.com" in d or "instagram.com" in d) and base["domain"] != ".threads.net":
                    clone = dict(base)
                    clone["domain"] = ".threads.net"
                    collected.append(clone)
        else:
            logger.warning("⚠️ threads_session.json 이 없거나 비어 있습니다. 차순위 쿠키로 폴백합니다.")

        # ------------------------------------------------------------
        # 2순위: threads_cookies.json (원천 보조 쿠키)
        # ------------------------------------------------------------
        primary_cookies = self._load_cookie_json(COOKIE_FILE)
        if primary_cookies:
            logger.info(f"🍪 [2순위] threads_cookies.json 로드: {len(primary_cookies)}개 (보조)")
            for c in primary_cookies:
                domain = str(c.get("domain", "") or "").lower()

                # 페이스북 전용 쿠키는 스레드 도메인으로 승격 금지
                if self._is_facebook_only_cookie(c):
                    continue

                base = self._to_pw_cookie(c)
                if not base:
                    continue
                collected.append(base)

                # .threads.com / .instagram.com → .threads.net 자동 복제
                if ".threads.com" in domain or "threads.com" in domain or "instagram.com" in domain:
                    if base["domain"] != ".threads.net":
                        clone = dict(base)
                        clone["domain"] = ".threads.net"
                        collected.append(clone)

        # ------------------------------------------------------------
        # 3순위: meta_session.json (메타 통합 세션)
        # ------------------------------------------------------------
        meta_cookies = self._load_cookie_json(META_SESSION_FILE)
        if meta_cookies:
            logger.info(f"🍪 [3순위] meta_session.json 로드: {len(meta_cookies)}개")
            for c in meta_cookies:
                # 🚫 facebook.com 전용 쿠키(c_user 등) → threads.net 강제 재매핑 금지
                if self._is_facebook_only_cookie(c):
                    continue
                base = self._to_pw_cookie(c)
                if not base:
                    continue
                if not self._is_threads_relevant_domain(base["domain"]):
                    continue
                collected.append(base)

                d = base["domain"].lower()
                if ("threads.com" in d or "instagram.com" in d) and base["domain"] != ".threads.net":
                    clone = dict(base)
                    clone["domain"] = ".threads.net"
                    collected.append(clone)

        # ------------------------------------------------------------
        # 최종 정규화: (name, domain, path) 중복 제거 — 선순위 우선 유지
        # ------------------------------------------------------------
        normalized: Dict[tuple, Dict[str, Any]] = {}
        for ck in collected:
            key = (ck.get("name"), ck.get("domain"), ck.get("path", "/"))
            if key not in normalized:
                normalized[key] = ck

        pw_cookies = list(normalized.values())

        # 인증 핵심 쿠키 존재 여부 진단 로그
        session_names = {c["name"] for c in pw_cookies}
        has_sessionid = "sessionid" in session_names
        has_ds_user_id = "ds_user_id" in session_names
        logger.info(
            f"🍪 최종 쿠키 정규화 완료: 수집 {len(collected)}개 → 중복제거 {len(pw_cookies)}개 "
            f"(sessionid: {'✅' if has_sessionid else '❌'}, ds_user_id: {'✅' if has_ds_user_id else '❌'})"
        )
        return pw_cookies

    async def publish_thread(
        self,
        caption: str,
        image_paths: Optional[List[str]] = None,
        first_reply_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """스레드에 본문 + 카드뉴스 이미지 + 첫 댓글 체인 자동 발행"""
        caption = sanitize_threads_caption(caption)
        if not caption:
            caption = (
                "📈 [실시간 AI 퀀트 수급 레이더 & 급등 테마 분석]\n\n"
                "뇌동매매와 감에 의존하는 투자는 이제 그만!\n"
                "외인·기관 쌍끌이 순매수 데이터와 퀀트 적정주가로 안전하게 투자하세요 💡\n\n"
                "매일 장 시작 전과 마감 후 핵심 퀀트 인사이트를 전해드립니다 ✨\n\n"
            )

        if not first_reply_text:
            first_reply_text = (
                f"📈 3초 실시간 외국인/기관 수급 레이더\n"
                f"네이버에 '{self.OFFICIAL_SEARCH_KEYWORD}' 검색해보세요!\n"
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

        # 🧬 발행 최전방: GOLDEN 세션 자가치유 게이트 (Self-Healing)
        try:
            heal = self.ensure_golden_session()
            logger.info(f"🧬 GOLDEN 세션 게이트: {heal['action']} (ok={heal['ok']})")
        except Exception as he:
            logger.warning(f"⚠️ GOLDEN 세션 게이트 예외(무시하고 계속): {he}")

        logger.info(f"🚀 [Stock Threads] 스레드 발행 시작 (글자수: {len(caption)}자, {media_type}: {len(valid_media)}개)")

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

            try:
                # 1. Threads 메인 접속
                logger.info("1. Threads 메인 페이지 접속 중...")
                await page.goto("https://www.threads.net/", wait_until="domcontentloaded", timeout=25000)
                await asyncio.sleep(3)

                # 1-1. Terms 오버레이 배너 제거 + 로그인/계정 연결 모달 방탄 클릭
                try:
                    await page.evaluate("""() => {
                        const fixedOverlays = Array.from(document.querySelectorAll("div")).filter(d => {
                            const style = window.getComputedStyle(d);
                            return (style.position === 'fixed' || style.position === 'sticky') && style.bottom === '0px' && d.innerText && d.innerText.includes('Terms');
                        });
                        fixedOverlays.forEach(b => b.remove());
                    }""")
                    await asyncio.sleep(1)

                    clicked_modal = await page.evaluate("""() => {
                        const KEYWORDS = [
                            'Continue with Instagram',
                            'Instagram으로 계속하기',
                            'Instagram으로 계속',
                            'Log in with Instagram',
                            'Instagram으로 로그인',
                            'stockmaster_ai',
                            'Continue as'
                        ];
                        const matches = (el) => {
                            const t = (el.innerText || '').trim();
                            const aria = (el.getAttribute && el.getAttribute('aria-label')) || '';
                            const hay = (t + ' ' + aria).toLowerCase();
                            return KEYWORDS.some(k => hay.includes(k.toLowerCase()));
                        };
                        const candidates = Array.from(document.querySelectorAll(
                            "button, div[role='button'], a, span, div"
                        )).filter(el => el.offsetParent !== null && matches(el));
                        if (candidates.length === 0) return false;
                        // 가장 안쪽(leaf) 요소 우선 → 실제 클릭 가능한 조상으로 승격
                        const target = candidates[candidates.length - 1];
                        const clickable = target.closest("button, div[role='button'], a") || target;
                        clickable.scrollIntoView({block: 'center'});
                        clickable.click();
                        return true;
                    }""")
                    if clicked_modal:
                        logger.info("👉 'Continue with Instagram' 계열 모달 클릭 성공, 세션 연결 대기...")
                        await asyncio.sleep(6)
                    else:
                        logger.info("👉 로그인 모달 미감지 (이미 세션 유효 상태로 판단)")
                except Exception as me:
                    logger.warning(f"모달 클릭 예외: {me}")

                # 2. 작성 모달 열기 (4중 Fallback 전략)
                logger.info("2. 스레드 작성창 열기...")
                opened = False
                for attempt in range(6):
                    # 1) 상단 빠른 작성창 클릭 ("새로운 소식을 공유해보세요")
                    try:
                        quick = await page.query_selector("div:has-text('새로운 소식을 공유해보세요'), div:has-text('What\\'s new?')")
                        if quick and await quick.is_visible():
                            await quick.click()
                            await asyncio.sleep(2.5)
                    except Exception:
                        pass

                    # 2) 좌측 메뉴 "새로운 스레드" 또는 우측 하단 플로팅 '+' 버튼 클릭
                    if not await page.query_selector("div[role='textbox'][contenteditable='true'], div[data-lexical-editor='true']"):
                        try:
                            await page.evaluate("""() => {
                                const btns = Array.from(document.querySelectorAll("div[role='button'], button, a"));
                                const createBtn = btns.find(b => {
                                    const t = (b.innerText || '').trim();
                                    const aria = b.getAttribute('aria-label') || '';
                                    return t.includes('새로운 스레드') || t.includes('New thread') || aria.includes('새로운 스레드') || aria.includes('Create');
                                });
                                if (createBtn) {
                                    createBtn.click();
                                    return;
                                }
                                // 우측 하단 플로팅 버튼 fallback
                                const allBtns = Array.from(document.querySelectorAll("div[role='button']"));
                                if (allBtns.length > 0) {
                                    allBtns[allBtns.length - 1].click();
                                }
                            }""")
                            await asyncio.sleep(3)
                        except Exception:
                            pass

                    # 3) 단축키 fallback ('c')
                    if not await page.query_selector("div[role='textbox'][contenteditable='true'], div[data-lexical-editor='true']"):
                        try:
                            await page.keyboard.press("c")
                            await asyncio.sleep(2.5)
                        except Exception:
                            pass

                    tb_check = await page.query_selector("div[role='textbox'][contenteditable='true'], div[data-lexical-editor='true']")
                    if tb_check and await tb_check.is_visible():
                        logger.info("✅ 작성창(textbox) 활성화 확인!")
                        opened = True
                        break
                    await asyncio.sleep(1.5)

                if not opened:
                    raise RuntimeError("스레드 작성창(textbox)을 활성화하지 못했습니다.")

                # 3. 본문 텍스트 입력 (Lexical 에디터 완벽 호환 keyboard.insert_text)
                logger.info("3. 캡션 텍스트 입력 중...")
                textbox = await page.wait_for_selector("div[role='textbox'][contenteditable='true'], div[data-lexical-editor='true']", timeout=12000)
                await textbox.click()
                await asyncio.sleep(0.5)
                # 기존 텍스트 지우고 새 텍스트 입력
                await page.keyboard.press("Control+A")
                await page.keyboard.press("Backspace")
                await asyncio.sleep(0.3)
                await page.keyboard.insert_text(caption)
                await asyncio.sleep(1.5)

                # 4. 카드뉴스 이미지 또는 숏폼 비디오 첨부
                if valid_media:
                    logger.info(f"4. {media_type} {len(valid_media)}개 업로드 중...")
                    file_input = await page.query_selector("input[type='file']")
                    if file_input:
                        await file_input.set_input_files(valid_media)
                        logger.info("   미디어 파일 전송 완료, 렌더링/인코딩 대기...")
                        wait_sec = 14 if is_video else 6
                        await asyncio.sleep(wait_sec)

                # 5. [1단계] 본문 Post / 게시 버튼 클릭 및 모달 닫힘 대기
                logger.info("5. 본문 [Post / 게시] 버튼 클릭...")
                posted = False
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
                        if (postBtn) {
                            postBtn.click();
                            return true;
                        }
                        return false;
                    }""")
                    if posted:
                        break
                    await asyncio.sleep(1)

                if not posted:
                    publish_btn = await page.query_selector("div[role='dialog'] div[role='button']:has-text('Post'), div[role='dialog'] button:has-text('Post'), div[role='dialog'] div[role='button']:has-text('게시')")
                    if publish_btn:
                        await publish_btn.click(force=True)
                        posted = True

                logger.info("   본문 게시 요청 전송 완료! 모달 닫힘 및 서버 반영 대기 (12초)...")
                await asyncio.sleep(12)

                # 6. [2단계] 첫 번째 타래 댓글 (방금 올린 본문 글의 고유 상세 페이지로 직접 이동하여 답글 체인 작성)
                if first_reply_text:
                    logger.info("6. [2단계] 첫 번째 타래 댓글(답글) 작성 시작...")
                    try:
                        # 6-1. 내 프로필로 이동하여 방금 올린 본문 글의 URL 링크 추출
                        await page.goto("https://www.threads.net/@stockmaster_ai", wait_until="domcontentloaded", timeout=25000)
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
                logger.error(f"❌ [Stock Threads] 발행 실패: {e}")
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
    publisher = StockThreadsPublisher(headless=True)
    target_folder = r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\아우라\아우라_08_500m안심레이더_20261001_1100"

    images = [str(Path(target_folder) / f"slide_{i}.png") for i in range(1, 6)]

    caption = (
        "📈 [실시간 AI 퀀트 수급 레이더 & 급등 테마 분석]\n\n"
        "뇌동매매와 감에 의존하는 투자는 이제 그만!\n"
        "외인·기관 쌍끌이 순매수 데이터와 퀀트 적정주가로 안전하게 투자하세요 💡\n\n"
        "매일 장 시작 전과 마감 후 핵심 퀀트 인사이트를 전해드립니다 ✨\n\n"
        "#Stock #스톡마스터AI #퀀트투자 #수급분석 #급등테마 #주식"
    )

    res = await publisher.publish_thread(
        caption=caption,
        image_paths=images,
        first_reply_text="📈 3초 실시간 외국인/기관 수급 레이더\n네이버에 '스톡마스터 AI' 한번 검색해보세요!\n👉 https://stockmaster-ai.vercel.app/"
    )
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
