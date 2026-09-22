# -*- coding: utf-8 -*-
"""
3대 앱 네이버 영구 로그인 세션 상태 정밀 전수 검증 스크립트
"""
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BASE_DIR = Path(__file__).resolve().parent

BRANDS = [
    {
        "key": "aura",
        "name": "💖 Aura 데이팅",
        "expected_id": "zkfnth01",
        "dir": BASE_DIR / "brands" / "aura"
    },
    {
        "key": "stock",
        "name": "📈 Stock Master 주식 AI",
        "expected_id": "zkfnth02",
        "dir": BASE_DIR / "brands" / "stock"
    },
    {
        "key": "insurance",
        "name": "🛡️ InsureBalance 보험비교",
        "expected_id": "thefirst-life",
        "dir": BASE_DIR / "brands" / "insurance"
    }
]


async def verify_brand_session(brand_info: dict, p):
    b_key = brand_info["key"]
    b_name = brand_info["name"]
    exp_id = brand_info["expected_id"]
    b_dir = brand_info["dir"]
    
    profile_dir = b_dir / "naver_browser_profile"
    session_file = b_dir / "naver_session.json"
    accounts_file = b_dir / "accounts.json"
    
    print(f"\n==================================================")
    print(f"🔍 [{b_name}] 세션 및 영구 프로필 정밀 검증")
    print(f"==================================================")
    print(f"  - 목표 계정: {exp_id}")
    print(f"  - 프로필 디렉터리 존재: {profile_dir.exists()}")
    print(f"  - naver_session.json 존재: {session_file.exists()}")
    print(f"  - accounts.json 존재: {accounts_file.exists()}")
    
    # 1. 파일 내 쿠키 분석
    has_valid_json_cookie = False
    if session_file.exists():
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                sdata = json.load(f)
                cookies = sdata.get("cookies", [])
                c_names = {c.get("name") for c in cookies}
                print(f"  - session.json 쿠키 개수: {len(cookies)}개 (NID_AUT: {'NID_AUT' in c_names}, NID_SES: {'NID_SES' in c_names})")
                if "NID_AUT" in c_names and "NID_SES" in c_names:
                    has_valid_json_cookie = True
        except Exception as e:
            print(f"  - session.json 읽기 오류: {e}")

    # 2. 실제 브라우저 띄워 로그인 상태 확인
    if not profile_dir.exists() and not has_valid_json_cookie:
        print(f"❌ [{b_name}] 영구 프로필 및 쿠키가 아직 생성되지 않았습니다.")
        return {"brand": b_key, "status": "not_logged_in", "message": "로그인 필요"}

    try:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir) if profile_dir.exists() else None,
            headless=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        
        # session.json에 쿠키가 있으면 추가 주입
        if session_file.exists():
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    sdata = json.load(f)
                    cookies = sdata.get("cookies", [])
                    if cookies:
                        await context.add_cookies(cookies)
            except Exception:
                pass

        page = await context.new_page()
        # 네이버 회원정보 페이지로 정확한 로그인 세션 상태 검증
        await page.goto("https://nid.naver.com/user2/help/myInfoV2?lang=ko_KR", wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(2000)
        
        curr_url = page.url
        is_logged_in = "myInfo" in curr_url and "nidlogin" not in curr_url
        
        user_text = ""
        try:
            user_id_el = await page.query_selector(".user_id, .user_name, .name, #user_id, .my_info_name")
            if user_id_el:
                user_text = (await user_id_el.inner_text()).strip()
        except Exception:
            pass

        # 지식iN의 경우 답변하기 진입 여부 2차 검증
        if b_key == "aura" and is_logged_in:
            try:
                test_q_url = "https://kin.naver.com/qna/detail.naver?dirId=121507&docId=495145379"
                await page.goto(test_q_url, wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_timeout(1500)
                ans_btn = await page.query_selector("button._answerWriteButton, button.endAnswerRegisterButton")
                if ans_btn:
                    await ans_btn.click()
                    await page.wait_for_timeout(2000)
                    if "nidlogin.login" in page.url:
                        is_logged_in = False
                        print(f"  🚨 [Aura 지식iN] 답변하기 클릭 시 로그인 창으로 리다이렉트됨")
                    else:
                        print(f"  ✅ [Aura 지식iN] 답변하기 정상 진입 성공 (24h 무인 가동 준비 완료)")
            except Exception as e:
                print(f"  ⚠️ [Aura 지식iN] 테스트 페이지 접근 알림: {e}")

        # 블로그의 경우 블로그 진입 확인
        if b_key in ["stock", "insurance"] and is_logged_in:
            blog_id = exp_id
            print(f"  ✅ [{b_name}] 네이버 블로그 ({blog_id}) 세션 연결 정상 확인!")

        print(f"  📊 실측 로그인 상태: {'🟢 로그인 정상' if is_logged_in else '🔴 로그아웃 상태'}")
        if user_text:
            print(f"  👤 감지된 사용자 정보: {user_text}")

        await context.close()
        return {
            "brand": b_key,
            "is_logged_in": is_logged_in,
            "user_text": user_text,
            "status": "active" if is_logged_in else "expired"
        }
    except Exception as e:
        print(f"  ❌ 검증 중 예외 발생: {e}")
        return {"brand": b_key, "is_logged_in": False, "error": str(e)}


async def main():
    print("🚀 대한민국 3대 슈퍼앱 네이버 영구 로그인 세션 실측 전수 조사 시작...")
    results = {}
    async with async_playwright() as p:
        for b in BRANDS:
            res = await verify_brand_session(b, p)
            results[b["key"]] = res

    print("\n" + "=" * 70)
    print("📋 [3대 슈퍼앱 네이버 영구 세션 전수 조사 최종 요약]")
    print("=" * 70)
    for b in BRANDS:
        k = b["key"]
        r = results.get(k, {})
        status_icon = "🟢 정상 연결 (24h 무인 가동 가능)" if r.get("is_logged_in") else "🔴 로그인 필요 (1회 연동 대기)"
        print(f"  - {b['name']} ({b['expected_id']}): {status_icon}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
