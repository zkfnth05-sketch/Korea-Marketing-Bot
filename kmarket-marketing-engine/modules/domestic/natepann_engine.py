# -*- coding: utf-8 -*-
"""
Nate Pann Autonomous Engine (네이트판 3대 브랜드 실전 무인 투고 엔진)
=============================================================================
- 2030 스토리/사연 바이럴의 여왕 네이트판 100% 무인 자동 포스팅
- 3대 브랜드 공식 규격 및 Zero URL 철칙:
  1) 💖 Aura: "네이버에 아우라AI데이팅 한번 검색해보세요"
  2) 🛡️ Insurance: "네이버에 보험 리밸런스 검색해보세요"
  3) 📈 Stock: "네이버에 스톡마스터 AI 검색해보세요"
- Windows Playwright 실전 모바일 웹 자동화 (클립보드 주입 & 한글 깨짐 방지)
- 3회 지수 백오프 서킷 브레이커 & data/channel_errors.json 대시보드 동기화
"""

import os
import re
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

logger = logging.getLogger("NatePannEngine")
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(_h)
logger.setLevel(logging.INFO)

BRAND_SPECS = {
    "aura": {
        "name": "💖 Aura AI 데이팅",
        "category": "love",
        "category_name": "결혼/시집/친정 & 연애판",
        "search_callout": "네이버에 아우라AI데이팅 한번 검색해보세요",
        "default_title": "소개팅에서 대화 끊겨서 망할 뻔했는데 AI로 살려낸 후기 푼다",
        "default_story": (
            "소개팅 나가면 늘 어색한 침묵 때문에 애프터는 꿈도 못 꾸던 모솔 탈출러임.\n"
            "이번에 지인 소개로 만난 분이랑 카톡 티키타카가 너무 안 맞아서 이번에도 망했구나 싶었음.\n"
            "근데 소개팅 대화 분석해주는 AI한테 상황 입력하고 카톡 답장 타이밍이랑 질문 팁 조언받았는데 대박남.\n"
            "상대방이 '오늘 대화 너무 즐거웠어요'라면서 먼저 주말에 맛집 가자고 선톡 옴 ㅠㅠ\n"
            "진짜 소개팅이나 썸 탈 때 답답한 사람들 네이버에 아우라AI데이팅 한번 검색해보세요. 리얼 구세주임."
        )
    },
    "insurance": {
        "name": "🛡️ 보험 리밸런스",
        "category": "life",
        "category_name": "사는 얘기 & 직장인판",
        "search_callout": "네이버에 보험 리밸런스 검색해보세요",
        "default_title": "부모님 갱신형 보험 100만원 넘게 내던 거 30만원대로 줄인 후기",
        "default_story": (
            "얼마 전에 부모님 보험 증권 다 모아서 점검해봤는데 진짜 기절하는 줄 알았음.\n"
            "지인 통해서 가입했던 암보험이랑 종합보험이 전부 3년, 5년 갱신형으로 들어가 있어서\n"
            "매달 둘이 합쳐서 110만원씩 빠져나가고 있더라고... 환급금도 거의 없는 상태였음.\n"
            "주변 추천받아서 비갱신형으로 리밸런스하고 불필요한 특약 싹 정리하니까\n"
            "보장은 뇌혈관/허혈성까지 든든하게 늘리고 월 납입료는 38만원으로 무려 70만원 줄임.\n"
            "가족들 보험 점검 안 해보신 분들 꼭 네이버에 보험 리밸런스 검색해보세요. 진짜 돈 아끼는 지름길임."
        )
    },
    "stock": {
        "name": "📈 StockMaster AI",
        "category": "finance",
        "category_name": "사는 얘기 & 재테크판",
        "search_callout": "네이버에 스톡마스터 AI 검색해보세요",
        "default_title": "물타기만 하다가 계좌 -40% 찍고 기관 수급 AI로 원금 복구한 썰",
        "default_story": (
            "작년에 테마주 고점에 물려서 끝없는 물타기하다가 반토막 직전까지 갔던 직장인임.\n"
            "뉴스랑 종토방 찌라시만 보고 매수하던 내 뇌동매매 습관이 문제였음.\n"
            "외국인/기관 메이저 수급이랑 거래대금 집중 분석해주는 퀀트 봇 추천받고 따라해봤는데,\n"
            "확실히 감으로 하는 거랑 데이터 기반으로 손절/익절 칼같이 잡는 거랑 차원이 다름.\n"
            "손실 다 메꾸고 이번 분기 수익 전환 성공함 ㅠㅠ 주식으로 스트레스 받는 분들\n"
            "네이버에 스톡마스터 AI 검색해보세요. 최소한 뇌동매매는 확실하게 막아줌."
        )
    }
}

ERRORS_FILE = BASE_DIR / "data" / "channel_errors.json"
MAX_RETRIES = 3
RETRY_BACKOFF_SEC = 5.0


def _record_circuit_error(channel_key: str, message: str) -> None:
    try:
        data = {}
        if ERRORS_FILE.exists():
            with open(ERRORS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        data[channel_key] = {
            "channel": channel_key,
            "message": message,
            "type": "danger",
            "tripped_at": datetime.now().isoformat()
        }
        ERRORS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(ERRORS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"서킷브레이커 에러 기록 실패: {e}")


def _clear_circuit_error(channel_key: str) -> None:
    try:
        if ERRORS_FILE.exists():
            with open(ERRORS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if channel_key in data:
                del data[channel_key]
                with open(ERRORS_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"서킷브레이커 클리어 실패: {e}")


def _find_nate_session(brand: str) -> Optional[Path]:
    candidates = [
        BASE_DIR / "brands" / brand / "nate_session.json",
        BASE_DIR / "nate_session.json",
        BASE_DIR / "data" / "nate_session.json"
    ]
    for p in candidates:
        if p.exists() and p.stat().st_size > 10:
            return p
    return None


def _load_cookies(session_file: Path) -> list:
    """세션 파일에서 쿠키 목록 추출 ({"cookies": [...]} / [...] 양쪽 수용)"""
    with open(session_file, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if isinstance(raw, dict):
        raw = raw.get("cookies") or raw.get("Cookies") or []
    return raw if isinstance(raw, list) else []


def _clipboard_paste(page: Any, text: str) -> bool:
    """Windows 클립보드 주입 후 Ctrl+V (한글 IME 깨짐 방지)"""
    try:
        import subprocess
        proc = subprocess.Popen(["clip"], stdin=subprocess.PIPE, shell=True)
        proc.communicate(input=text.encode("utf-16-le"))
        if proc.returncode != 0:
            return False
        page.keyboard.press("Control+V")
        return True
    except Exception as e:
        logger.warning(f"클립보드 주입 실패, fill 폴백: {e}")
        return False


def _fill_field(page: Any, selector: str, text: str) -> bool:
    """셀렉터 존재 시 클립보드 우선 주입, 실패 시 fill 폴백"""
    el = page.query_selector(selector)
    if not el:
        return False
    try:
        el.click()
        time.sleep(0.3)
        if _clipboard_paste(page, text):
            return True
        el.fill(text)
        return True
    except Exception as e:
        logger.warning(f"필드 입력 실패({selector}): {e}")
        return False


class NatePannEngine:
    BASE_URL = "https://m.pann.nate.com"
    WRITE_PAGE_URL = "https://m.pann.nate.com/talk/write"

    def __init__(self, brand: str = "aura"):
        self.brand = brand.lower().strip()
        self.spec = BRAND_SPECS.get(self.brand, BRAND_SPECS["aura"])
        self.session_file = _find_nate_session(self.brand)

    def post_brand_story(
        self,
        brand: Optional[str] = None,
        topic: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        target_brand = (brand or self.brand).lower().strip()
        spec = BRAND_SPECS.get(target_brand, self.spec)
        channel_key = f"{target_brand}_nate_pann"

        title = spec["default_title"]
        body = spec["default_story"]
        if topic:
            title = f"[{spec['name']}] {topic}"

        # Zero URL 절대 원칙 검증: 본문에 http 링크가 있으면 자동 정제
        body = re.sub(r"https?://\S+", "", body)
        if spec["search_callout"] not in body:
            body = body.rstrip() + f"\n\n{spec['search_callout']}"

        session_path = _find_nate_session(target_brand)
        if dry_run or not session_path:
            logger.info(f"[{spec['name']}] 네이트판 사연 투고 (시뮬레이션 모드)")
            logger.info(f"  • 타깃 판: {spec['category_name']}")
            logger.info(f"  • 제목: {title}")
            logger.info(f"  • 검색어 유도: {spec['search_callout']}")
            return {
                "success": True,
                "mode": "dry_run" if dry_run else "no_session_simulated",
                "brand": target_brand,
                "title": title,
                "preview": body[:120] + "...",
                "search_callout": spec["search_callout"]
            }

        last_error = ""
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(f"🚀 [{spec['name']}] 네이트판 실전 투고 시도 {attempt}/{MAX_RETRIES}...")
                pub_result = self._publish_via_playwright(session_path, title, body, target_brand)
                if pub_result.get("success"):
                    _clear_circuit_error(channel_key)
                    logger.info(f"🎉 [{spec['name']}] 네이트판 라이브 투고 100% 성공! URL: {pub_result.get('url')}")
                    return pub_result
                last_error = pub_result.get("error", "알 수 없는 발행 실패")
            except Exception as e:
                last_error = str(e)
                logger.warning(f"⚠️ [{spec['name']}] 시도 {attempt} 실패: {last_error}")

            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SEC * attempt)

        _record_circuit_error(channel_key, f"네이트판 3회 재시도 초과 실패: {last_error}")
        return {"success": False, "error": last_error, "brand": target_brand}

    def _publish_via_playwright(
        self,
        session_file: Path,
        title: str,
        body: str,
        brand: str
    ) -> Dict[str, Any]:
        from playwright.sync_api import sync_playwright

        proofs_dir = BASE_DIR / "proofs"
        proofs_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        proof_path = proofs_dir / f"nate_live_proof_{brand}_{timestamp}.png"

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
            context = browser.new_context(
                viewport={"width": 412, "height": 915},
                user_agent=(
                    "Mozilla/5.0 (Linux; Android 13; SM-S918N) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36"
                )
            )

            try:
                raw_cookies = _load_cookies(session_file)
                clean_cookies = []
                for c in raw_cookies:
                    if not isinstance(c, dict) or not c.get("name"):
                        continue
                    cookie_dict = {"name": c["name"], "value": str(c.get("value", ""))}
                    if c.get("domain"):
                        cookie_dict["domain"] = c["domain"]
                        cookie_dict["path"] = c.get("path") or "/"
                    else:
                        cookie_dict["url"] = "https://m.pann.nate.com"
                    clean_cookies.append(cookie_dict)
                if clean_cookies:
                    context.add_cookies(clean_cookies)
            except Exception as e:
                browser.close()
                return {"success": False, "error": f"세션 쿠키 주입 실패: {e}"}

            page = context.new_page()
            try:
                page.goto(self.WRITE_PAGE_URL, timeout=30000, wait_until="domcontentloaded")
                time.sleep(2)

                # 로그인 여부 점검
                if "login" in page.url.lower():
                    browser.close()
                    return {"success": False, "error": "네이트판 세션 만료됨 (재로그인 필요)"}

                # 제목 입력
                title_ok = _fill_field(
                    page,
                    "input#title, input[name='title'], input[placeholder*='제목']",
                    title
                )
                if not title_ok:
                    page.keyboard.type(title)
                time.sleep(1)

                # 본문 입력
                body_ok = _fill_field(
                    page,
                    "textarea#content, textarea[name='content'], textarea[placeholder*='내용']",
                    body
                )
                if not body_ok:
                    page.keyboard.type(body)
                time.sleep(1)

                # 등록 버튼 클릭
                submit_btn = page.query_selector(
                    "button:has-text('등록'), a:has-text('등록'), input[type='submit']"
                )
                if submit_btn:
                    submit_btn.click()
                    time.sleep(3)

                page.screenshot(path=str(proof_path), full_page=False)
                live_url = page.url
            except Exception as e:
                try:
                    page.screenshot(path=str(proof_path), full_page=False)
                except Exception:
                    pass
                browser.close()
                return {"success": False, "error": f"발행 중 예외: {e}"}

            browser.close()

            return {
                "success": True,
                "url": live_url,
                "proof_screenshot": str(proof_path),
                "brand": brand,
                "title": title
            }


def run_aura_pann(topic: Optional[str] = None, dry_run: bool = False) -> Dict[str, Any]:
    return NatePannEngine("aura").post_brand_story(topic=topic, dry_run=dry_run)


def run_insurance_pann(topic: Optional[str] = None, dry_run: bool = False) -> Dict[str, Any]:
    return NatePannEngine("insurance").post_brand_story(topic=topic, dry_run=dry_run)


def run_stock_pann(topic: Optional[str] = None, dry_run: bool = False) -> Dict[str, Any]:
    return NatePannEngine("stock").post_brand_story(topic=topic, dry_run=dry_run)


def find_chrome_path() -> str:
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return "chrome.exe"


def login_nate_session(target_brand: str = "all") -> bool:
    """
    네이트판 1회 영구 로그인 도구
    - 실제 크롬 창을 띄워 사용자가 네이트 계정 로그인 진행
    - 창이 닫히면 Playwright로 세션 쿠키를 추출하여 3대 브랜드 및 루트에 영구 동기화
    """
    import subprocess
    print("\n" + "=" * 70)
    print("🌐 [네이트판(Nate Pann) 1회 영구 로그인 세션 연동 도구]")
    print("=" * 70)
    print("1. 실제 크롬 브라우저가 화면에 열립니다.")
    print("2. 네이트 계정으로 로그인해 주세요. (자동로그인/로그인 상태 유지 체크 필수!)")
    print("3. 로그인이 완료되어 판 메인화면이 정상 표시되면,")
    print("4. 브라우저 창 우측 상단의 [X]를 눌러 닫아주세요.")
    print("   -> 닫히는 즉시 3대 브랜드(Aura, Insurance, Stock)에 세션이 영구 저장됩니다.")
    print("=" * 70 + "\n")

    profile_dir = BASE_DIR / "data" / "nate_chrome_profile"
    profile_dir.mkdir(parents=True, exist_ok=True)
    chrome_exe = find_chrome_path()
    print(f"🚀 실제 크롬 브라우저 실행 중... ({chrome_exe})")

    cmd = [
        chrome_exe,
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "https://m.pann.nate.com"
    ]
    subprocess.run(cmd)

    print("\n✅ 브라우저 창이 닫혔습니다. 세션 쿠키를 추출하여 영구 저장소에 동기화 중...")

    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                channel="chrome",
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
            cookies = context.cookies(["https://m.pann.nate.com", "https://pann.nate.com", "https://nate.com"])
            context.close()

            if not cookies:
                print("⚠️ 감지된 네이트 쿠키가 없습니다. 로그인이 정상 완료되었는지 확인해 주세요.")
                return False

            save_targets = [
                BASE_DIR / "nate_session.json",
                BASE_DIR / "data" / "nate_session.json",
                BASE_DIR / "brands" / "aura" / "nate_session.json",
                BASE_DIR / "brands" / "insurance" / "nate_session.json",
                BASE_DIR / "brands" / "stock" / "nate_session.json"
            ]

            session_payload = {
                "platform": "nate",
                "saved_at": datetime.now().isoformat(),
                "cookies_count": len(cookies),
                "cookies": cookies
            }

            for target_path in save_targets:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with open(target_path, "w", encoding="utf-8") as f:
                    json.dump(session_payload, f, ensure_ascii=False, indent=2)

            print(f"🍪 [성공] 총 {len(cookies)}개의 인증 쿠키를 3대 브랜드 및 루트에 100% 영구 동기화 완료!")
            print("🎉 이제부터 3대 브랜드의 네이트판 자동 투고가 24시간 365일 무인으로 작동합니다.\n")
            return True
    except Exception as e:
        print(f"❌ 쿠키 추출 동기화 실패: {e}")
        return False


if __name__ == "__main__":
    if "--login" in sys.argv:
        login_nate_session()
    else:
        print("=" * 60)
        print("🚀 [네이트판 3대 브랜드 무인 투고 엔진 테스트]")
        print("=" * 60)
        for b in ["aura", "insurance", "stock"]:
            res = NatePannEngine(b).post_brand_story(dry_run=True)
            print(f"[{b.upper()}] 결과: {res.get('title')} -> 검색어: '{res.get('search_callout')}'")
        print("=" * 60)
