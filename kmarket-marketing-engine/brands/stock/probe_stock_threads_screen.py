# -*- coding: utf-8 -*-
"""
Stock Threads 화면 덤프 및 DOM 정밀 진단 모듈
===================================================================
- 역할:
  1. brands/stock/meta_chrome_profile + threads_session.json 쿠키 주입 → Chromium 헤드리스로 https://www.threads.net/ 접속
  2. 5초 대기 후 현재 화면 스크린샷 → brands/stock/stock_threads_current_screen.png
  3. 현재 페이지 HTML → brands/stock/stock_threads_dom.html
  4. 페이지 내 보이는 모든 텍스트 / 버튼 / 링크 / textbox 의 텍스트와 role 콘솔 출력
- 실행: python probe_stock_threads_screen.py
"""

import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.async_api import async_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("StockThreadsScreenProbe")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CURRENT_DIR = Path(__file__).resolve().parent
PROFILE_DIR = CURRENT_DIR / "meta_chrome_profile"
SESSION_FILE = CURRENT_DIR / "threads_session.json"
COOKIE_FILE = CURRENT_DIR / "threads_cookies.json"
META_SESSION_FILE = CURRENT_DIR / "meta_session.json"

SCREENSHOT_PATH = CURRENT_DIR / "stock_threads_current_screen.png"
DOM_PATH = CURRENT_DIR / "stock_threads_dom.html"
TARGET_URL = "https://www.threads.net/"

# 🍪 스레드 인증 유효 도메인 화이트리스트
THREADS_DOMAINS = (".threads.net", ".threads.com", ".instagram.com")
# 🚫 페이스북 전용 쿠키 (threads.net 재매핑 절대 금지)
FACEBOOK_ONLY_COOKIE_NAMES = {
    "c_user", "xs", "datr", "sb", "fr", "presence", "wd", "dpr",
    "locale", "m_pixel_ratio", "spin", "i_user", "cppo", "vpd", "lu",
}


# ----------------------------------------------------------------------
# 🍪 쿠키 로더 (stock_threads_publisher 와 동일 규격)
# ----------------------------------------------------------------------
def _normalize_same_site(raw: Any) -> Optional[str]:
    if not raw:
        return None
    s = str(raw).strip().lower()
    if s == "strict":
        return "Strict"
    if s == "lax":
        return "Lax"
    if s in ("none", "no_restriction", "unspecified"):
        return "None"
    return None


def _to_pw_cookie(c: Dict[str, Any], domain_override: Optional[str] = None) -> Optional[Dict[str, Any]]:
    name = c.get("name")
    if not name:
        return None
    domain = domain_override if domain_override else c.get("domain", "")
    if not domain:
        return None
    pw: Dict[str, Any] = {
        "name": name,
        "value": str(c.get("value", "")),
        "domain": domain,
        "path": c.get("path") or "/",
        "secure": bool(c.get("secure", True)),
        "httpOnly": bool(c.get("httpOnly", False)),
    }
    same_site = _normalize_same_site(c.get("sameSite"))
    if same_site:
        pw["sameSite"] = same_site
    expires = c.get("expires", c.get("expirationDate"))
    if isinstance(expires, (int, float)) and expires > 0:
        pw["expires"] = float(expires)
    return pw


def _load_cookie_json(path: Path) -> List[Dict[str, Any]]:
    """list / {cookies:[...]} / {Cookies|data:[...]} / 평면 dict 4포맷 완벽 파싱"""
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


def _is_facebook_only(cookie: Dict[str, Any]) -> bool:
    domain = str(cookie.get("domain", "")).lower()
    name = str(cookie.get("name", "")).lower()
    if "facebook.com" in domain or "fbcdn.net" in domain:
        return True
    return name in FACEBOOK_ONLY_COOKIE_NAMES


def _is_threads_relevant(domain: str) -> bool:
    d = str(domain or "").lower()
    if not d:
        return False
    if "facebook.com" in d or "fbcdn.net" in d:
        return False
    return any(t in d for t in THREADS_DOMAINS)


def build_cookies() -> List[Dict[str, Any]]:
    """
    우선순위: threads_session.json(1순위) → threads_cookies.json(2순위) → meta_session.json(3순위)
    (name, domain, path) 중복 제거 시 선순위 값 보존
    """
    collected: List[Dict[str, Any]] = []

    # 1순위: threads_session.json (AuthResolver 단일 소스 오브 트루스)
    for c in _load_cookie_json(SESSION_FILE):
        if _is_facebook_only(c):
            continue
        base = _to_pw_cookie(c)
        if not base or not _is_threads_relevant(base["domain"]):
            continue
        collected.append(base)
        d = base["domain"].lower()
        if ("threads.com" in d or "instagram.com" in d) and base["domain"] != ".threads.net":
            clone = dict(base)
            clone["domain"] = ".threads.net"
            collected.append(clone)

    # 2순위: threads_cookies.json (보조)
    for c in _load_cookie_json(COOKIE_FILE):
        if _is_facebook_only(c):
            continue
        base = _to_pw_cookie(c)
        if not base:
            continue
        collected.append(base)
        d = base["domain"].lower()
        if ("threads.com" in d or "instagram.com" in d) and base["domain"] != ".threads.net":
            clone = dict(base)
            clone["domain"] = ".threads.net"
            collected.append(clone)

    # 3순위: meta_session.json (메타 통합 세션)
    for c in _load_cookie_json(META_SESSION_FILE):
        if _is_facebook_only(c):
            continue
        base = _to_pw_cookie(c)
        if not base or not _is_threads_relevant(base["domain"]):
            continue
        collected.append(base)
        d = base["domain"].lower()
        if ("threads.com" in d or "instagram.com" in d) and base["domain"] != ".threads.net":
            clone = dict(base)
            clone["domain"] = ".threads.net"
            collected.append(clone)

    normalized: Dict[tuple, Dict[str, Any]] = {}
    for ck in collected:
        key = (ck.get("name"), ck.get("domain"), ck.get("path", "/"))
        if key not in normalized:
            normalized[key] = ck

    pw_cookies = list(normalized.values())
    names = {c["name"] for c in pw_cookies}
    logger.info(
        f"🍪 쿠키 정규화: 수집 {len(collected)}개 → 중복제거 {len(pw_cookies)}개 "
        f"(sessionid: {'✅' if 'sessionid' in names else '❌'}, "
        f"ds_user_id: {'✅' if 'ds_user_id' in names else '❌'})"
    )
    return pw_cookies


# ----------------------------------------------------------------------
# 🔍 DOM 정밀 진단 JS
# ----------------------------------------------------------------------
DOM_DUMP_JS = r"""
() => {
    const isVisible = (el) => {
        if (!el) return false;
        const rect = el.getBoundingClientRect();
        if (rect.width <= 0 || rect.height <= 0) return false;
        const style = window.getComputedStyle(el);
        if (style.visibility === 'hidden' || style.display === 'none' || style.opacity === '0') return false;
        return true;
    };
    const clean = (t) => (t || '').replace(/\s+/g, ' ').trim();

    const result = {
        url: location.href,
        title: document.title,
        viewport: { w: window.innerWidth, h: window.innerHeight },
        scrollHeight: document.documentElement.scrollHeight,
        counts: {},
        buttons: [],
        links: [],
        textboxes: [],
        texts: [],
        dialogs: [],
        loginHints: []
    };

    // 1) 버튼 (button / div[role=button] / a[role=button])
    const btnEls = Array.from(document.querySelectorAll("button, div[role='button'], a[role='button'], [role='button']"));
    result.counts.buttons_total = btnEls.length;
    btnEls.forEach((el, i) => {
        if (!isVisible(el)) return;
        const text = clean(el.innerText);
        const aria = clean(el.getAttribute('aria-label'));
        if (!text && !aria) return;
        result.buttons.push({
            idx: i,
            tag: el.tagName.toLowerCase(),
            role: el.getAttribute('role') || '',
            text: text.slice(0, 120),
            aria: aria.slice(0, 120),
            disabled: el.getAttribute('aria-disabled') === 'true' || el.hasAttribute('disabled')
        });
    });

    // 2) 링크
    const linkEls = Array.from(document.querySelectorAll("a[href]"));
    result.counts.links_total = linkEls.length;
    linkEls.forEach((el) => {
        if (!isVisible(el)) return;
        const text = clean(el.innerText);
        const href = el.getAttribute('href') || '';
        if (!text && !href) return;
        result.links.push({ text: text.slice(0, 100), href: href.slice(0, 160) });
    });

    // 3) 텍스트박스 (contenteditable / textarea / input[text])
    const tbEls = Array.from(document.querySelectorAll(
        "div[role='textbox'], div[contenteditable='true'], div[data-lexical-editor='true'], textarea, input[type='text']"
    ));
    result.counts.textboxes_total = tbEls.length;
    tbEls.forEach((el) => {
        if (!isVisible(el)) return;
        result.textboxes.push({
            tag: el.tagName.toLowerCase(),
            role: el.getAttribute('role') || '',
            placeholder: clean(el.getAttribute('placeholder') || el.getAttribute('aria-label') || el.getAttribute('data-placeholder')),
            contenteditable: el.getAttribute('contenteditable') || '',
            lexical: el.getAttribute('data-lexical-editor') || '',
            text: clean(el.innerText).slice(0, 100)
        });
    });

    // 4) 다이얼로그(모달)
    const dlgEls = Array.from(document.querySelectorAll("div[role='dialog'], [role='dialog']"));
    result.counts.dialogs_total = dlgEls.length;
    dlgEls.forEach((el) => {
        if (!isVisible(el)) return;
        result.dialogs.push({ text: clean(el.innerText).slice(0, 400) });
    });

    // 5) 보이는 텍스트 노드 수집 (중복 제거, 최대 200개)
    const seen = new Set();
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
    let node;
    while ((node = walker.nextNode())) {
        const t = clean(node.nodeValue);
        if (!t || t.length < 2) continue;
        const parent = node.parentElement;
        if (!parent || !isVisible(parent)) continue;
        if (seen.has(t)) continue;
        seen.add(t);
        result.texts.push(t.slice(0, 160));
        if (result.texts.length >= 200) break;
    }

    // 6) 로그인/계정연결 관련 힌트 문구 스캔
    const HINTS = ['continue with instagram', 'instagram으로 계속', 'log in with instagram',
                   'instagram으로 로그인', 'stockmaster_ai', 'continue as', 'log in', '로그인'];
    const bodyText = clean(document.body ? document.body.innerText : '').toLowerCase();
    HINTS.forEach(h => {
        if (bodyText.includes(h)) result.loginHints.push(h);
    });

    return result;
}
"""


async def probe() -> Dict[str, Any]:
    """헤드리스 Chromium 접속 → 스크린샷 + DOM 저장 + 콘솔 덤프"""
    cookies = build_cookies()

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ],
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
        )

        if cookies:
            await context.add_cookies(cookies)
            logger.info(f"🍪 쿠키 {len(cookies)}개 주입 완료")

        page = context.pages[0] if context.pages else await context.new_page()

        logger.info(f"1. 접속 중: {TARGET_URL}")
        await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
        logger.info("2. 5초 대기 (렌더링/세션 반영)...")
        await asyncio.sleep(5)

        # 3. 스크린샷 저장
        await page.screenshot(path=str(SCREENSHOT_PATH), full_page=False)
        logger.info(f"📸 스크린샷 저장: {SCREENSHOT_PATH}")

        # 4. HTML 저장
        html = await page.content()
        with open(DOM_PATH, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info(f"📄 DOM HTML 저장: {DOM_PATH} ({len(html):,} bytes)")

        # 5. DOM 정밀 진단
        dump = await page.evaluate(DOM_DUMP_JS)

        await context.close()
        return dump


def print_dump(dump: Dict[str, Any]) -> None:
    """콘솔 가독 출력"""
    line = "=" * 78
    print("\n" + line)
    print("🧵 STOCK THREADS 화면 덤프 / DOM 정밀 진단 결과")
    print(line)
    print(f"URL          : {dump.get('url')}")
    print(f"TITLE        : {dump.get('title')}")
    print(f"VIEWPORT     : {dump.get('viewport')}")
    print(f"SCROLL HEIGHT: {dump.get('scrollHeight')}")
    print(f"COUNTS       : {dump.get('counts')}")
    print(f"LOGIN HINTS  : {dump.get('loginHints')}")

    print("\n" + "-" * 78)
    print(f"🔘 버튼 (보이는 것만, {len(dump.get('buttons', []))}개)")
    print("-" * 78)
    for b in dump.get("buttons", []):
        print(f"  [{b['idx']:>3}] <{b['tag']}> role={b['role'] or '-'} disabled={b['disabled']} "
              f"| text='{b['text']}' | aria='{b['aria']}'")

    print("\n" + "-" * 78)
    print(f"🔗 링크 (보이는 것만, {len(dump.get('links', []))}개)")
    print("-" * 78)
    for l in dump.get("links", []):
        print(f"  text='{l['text']}' → href='{l['href']}'")

    print("\n" + "-" * 78)
    print(f"⌨️  TEXTBOX (보이는 것만, {len(dump.get('textboxes', []))}개)")
    print("-" * 78)
    for t in dump.get("textboxes", []):
        print(f"  <{t['tag']}> role={t['role'] or '-'} contenteditable={t['contenteditable'] or '-'} "
              f"lexical={t['lexical'] or '-'} placeholder='{t['placeholder']}' text='{t['text']}'")

    print("\n" + "-" * 78)
    print(f"🪟 DIALOG (보이는 것만, {len(dump.get('dialogs', []))}개)")
    print("-" * 78)
    for d in dump.get("dialogs", []):
        print(f"  text='{d['text']}'")

    print("\n" + "-" * 78)
    print(f"📝 보이는 텍스트 노드 ({len(dump.get('texts', []))}개)")
    print("-" * 78)
    for i, t in enumerate(dump.get("texts", []), 1):
        print(f"  {i:>3}. {t}")

    print("\n" + line + "\n")


async def main() -> int:
    try:
        dump = await probe()
    except Exception as ex:
        logger.error(f"❌ 진단 실패: {ex}")
        return 1

    print_dump(dump)

    # 진단 결과 JSON 백업 (후속 분석용)
    json_path = CURRENT_DIR / "stock_threads_screen_dump.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dump, f, ensure_ascii=False, indent=2)
    logger.info(f"🗂  진단 JSON 저장: {json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
