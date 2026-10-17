# -*- coding: utf-8 -*-
"""
[통합 실사 검증 도구] Verify All Blogs Visual
=============================================================================
- 3대 브랜드(Aura, Insurance, Stock)의 네이버 블로그와 티스토리를 전수 검증
- 실제 공개 URL 진입 + RSS 대조 + 증거 스크린샷 저장
"""

import sys
import json
from pathlib import Path

# UTF-8 콘솔 출력 강제
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from brands.aura.aura_blog_verifier import AuraBlogVerifier
from brands.insurance.insurance_blog_verifier import InsuranceBlogVerifier
from brands.stock.stock_blog_verifier import StockBlogVerifier



def main():
    print("=" * 80)
    print("🔍 [3대 브랜드] 네이버 & 티스토리 블로그 실제 발행 내역 전수 실사 검증")
    print("=" * 80)

    verifiers = [
        ("💖 Aura 데이팅", AuraBlogVerifier()),
        ("🛡️ InsureBalance 보험비교", InsuranceBlogVerifier()),
        ("📈 StockMaster 주식AI", StockBlogVerifier()),
    ]

    report = {}

    for name, v in verifiers:
        print(f"\n[{name}] 검증 진행 중...")
        res = v.verify_all(capture=True)
        report[v.brand] = res

        nv = res.get("naver", {})
        ti = res.get("tistory", {})

        print(f"  🟢 네이버 블로그 ({v.naver_blog_id}):")
        if nv.get("verified"):
            print(f"     ✅ [실제 발행 확인] {nv.get('title')}")
            print(f"        URL: {nv.get('real_url')}")
            print(f"        시각: {nv.get('pub_date')}")
            if nv.get("screenshot"):
                print(f"        📸 캡처: {nv.get('screenshot')}")
        else:
            print(f"     ❌ [미발행/실패] {nv.get('error', '확인 불가')}")

        print(f"  🟠 티스토리 ({v.tistory_blog_name}):")
        if ti.get("verified"):
            print(f"     ✅ [실제 발행 확인] {ti.get('title')}")
            print(f"        URL: {ti.get('real_url')}")
            print(f"        시각: {ti.get('pub_date')}")
            if ti.get("screenshot"):
                print(f"        📸 캡처: {ti.get('screenshot')}")
        else:
            print(f"     ❌ [미발행/실패] {ti.get('error', '확인 불가')}")

    print("\n" + "=" * 80)
    print("📊 [검증 결과 종합 요약]")
    print("=" * 80)
    for b_key, b_val in report.items():
        nv_ok = "✅ 성공" if b_val["naver"].get("verified") else "❌ 미발행"
        ti_ok = "✅ 성공" if b_val["tistory"].get("verified") else "❌ 미발행"
        print(f" - {b_key.upper():10} | 네이버: {nv_ok:10} | 티스토리: {ti_ok}")
    print("=" * 80)


if __name__ == "__main__":
    main()
