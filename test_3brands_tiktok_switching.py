# -*- coding: utf-8 -*-
"""
📱 [3대 브랜드 틱톡 계정 자동 분리 및 스위칭 전수 검증 테스트]
================================================================================
- 💖 Aura 데이팅: @aura_ai_dating 계정으로 스위칭 및 영수증 캡처
- 🛡️ 보험 리밸런스: @goldmom82 계정으로 스위칭 및 영수증 캡처
- 📈 StockMaster AI: @stock_master_ai 계정으로 스위칭 및 영수증 캡처
================================================================================
"""

import sys
import time
from pathlib import Path
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# unbuffered print wrapper
_orig_print = print
def print(*args, **kwargs):
    kwargs["flush"] = True
    _orig_print(*args, **kwargs)

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR
BRANDS_DIR = PROJECT_ROOT / "brands"

sys.path.insert(0, str(BRANDS_DIR / "aura" / "mobile"))
sys.path.insert(0, str(BRANDS_DIR / "insurance" / "mobile"))
sys.path.insert(0, str(BRANDS_DIR / "stock" / "mobile"))

from phone_aura_tiktok_uploader import PhoneAuraTikTokUploader
from phone_insurance_tiktok_uploader import PhoneInsuranceTikTokUploader
from phone_stock_tiktok_uploader import PhoneStockTikTokUploader

OUTPUTS_DIR = PROJECT_ROOT / "kmarket-marketing-engine" / "outputs" / "proofs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def test_brand_switching():
    print("=" * 70)
    print("🧪 [3대 브랜드 모바일 틱톡 계정 격리 & 무인 스위칭 검증 시작]")
    print("=" * 70)

    # 1. Aura 계정 검증
    print("\n[1/3] 💖 Aura AI 데이팅 계정(@aura_ai_dating) 스위칭 테스트...")
    aura_bot = PhoneAuraTikTokUploader()
    aura_bot.run_adb("shell", "am", "force-stop", "com.ss.android.ugc.trill")
    time.sleep(1.0)
    aura_bot.run_adb("shell", "am", "start", "-n", "com.ss.android.ugc.trill/com.ss.android.ugc.aweme.splash.SplashActivity")
    time.sleep(4.5)
    aura_res = aura_bot.ensure_brand_account("aura_ai_dating")
    time.sleep(2.0)
    aura_proof = OUTPUTS_DIR / "proof_switching_1_aura.png"
    aura_bot.run_adb("shell", "screencap", "-p", "/sdcard/aura_proof.png")
    aura_bot.run_adb("pull", "/sdcard/aura_proof.png", str(aura_proof))
    print(f"  📸 Aura 계정 스위칭 영수증 저장: {aura_proof} (결과: {aura_res})")

    # 2. 보험 계정 검증
    print("\n[2/3] 🛡️ 보험 리밸런스 계정(@goldmom82) 스위칭 테스트...")
    ins_bot = PhoneInsuranceTikTokUploader()
    ins_res = ins_bot.ensure_brand_account("goldmom82")
    time.sleep(2.0)
    ins_proof = OUTPUTS_DIR / "proof_switching_2_insurance.png"
    ins_bot.run_adb("shell", "screencap", "-p", "/sdcard/ins_proof.png")
    ins_bot.run_adb("pull", "/sdcard/ins_proof.png", str(ins_proof))
    print(f"  📸 보험 계정 스위칭 영수증 저장: {ins_proof} (결과: {ins_res})")

    # 3. 주식 계정 검증
    print("\n[3/3] 📈 StockMaster AI 계정(@stock_master_ai) 스위칭 테스트...")
    stock_bot = PhoneStockTikTokUploader()
    stock_res = stock_bot.ensure_brand_account("stock_master_ai")
    time.sleep(2.0)
    stock_proof = OUTPUTS_DIR / "proof_switching_3_stock.png"
    stock_bot.run_adb("shell", "screencap", "-p", "/sdcard/stock_proof.png")
    stock_bot.run_adb("pull", "/sdcard/stock_proof.png", str(stock_proof))
    print(f"  📸 주식 계정 스위칭 영수증 저장: {stock_proof} (결과: {stock_res})")

    # 클린 종료
    aura_bot.run_adb("shell", "am", "force-stop", "com.ss.android.ugc.trill")
    aura_bot.run_adb("shell", "input", "keyevent", "3")

    print("\n" + "=" * 70)
    print("🎉 [3대 브랜드 틱톡 계정 격리 & 무인 스위칭 검증 완료]")
    print(f"  - Aura 결과: {aura_res} -> {aura_proof}")
    print(f"  - 보험 결과: {ins_res} -> {ins_proof}")
    print(f"  - 주식 결과: {stock_res} -> {stock_proof}")
    print("=" * 70)


if __name__ == "__main__":
    test_brand_switching()
