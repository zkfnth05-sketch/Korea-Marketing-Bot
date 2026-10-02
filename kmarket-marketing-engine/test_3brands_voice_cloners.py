# -*- coding: utf-8 -*-
"""
Test 3 Brands Independent Voice Cloners (💖 Aura, 🛡️ Insurance, 📈 Stock)
3대 브랜드 완전 독립 알리바바 CosyVoice 음성 복제 파이프라인 전수 검증 스위트
"""

import os
import sys
import logging
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add engine root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("TestVoiceCloners")

from brands.aura.aura_voice_cloner import AuraVoiceCloner
from brands.insurance.insurance_voice_cloner import InsuranceVoiceCloner
from brands.stock.stock_voice_cloner import StockVoiceCloner


def test_all_3brands_voice_cloners():
    output_dir = BASE_DIR / "outputs" / "test_voices"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("🎙️ [3대 브랜드 알리바바 CosyVoice 남/여 듀얼 음성 복제 파이프라인 전수 테스트]")
    print("=" * 70)

    # 1. 💖 Aura 데이팅 (여성: 아라 / 남성: 진우)
    print("\n[1/3] 💖 Aura AI 데이팅")
    aura_cloner = AuraVoiceCloner(output_dir=str(output_dir))
    
    # 1-1. Aura 여성 (아라)
    aura_female_out = output_dir / "test_aura_female_ara.wav"
    aura_female_text = "소개팅 나갔는데 분위기가 너무 어색하고 도망치고 싶을 때, 아우라AI데이팅 긴급 탈출 전화를 써보세요!"
    aura_res_f = aura_cloner.synthesize(aura_female_text, str(aura_female_out), gender="female")
    assert Path(aura_res_f).exists() and Path(aura_res_f).stat().st_size > 1000
    print(f"  ✅ [Aura 여성 (아라)] {aura_female_out.name} ({Path(aura_res_f).stat().st_size} bytes)")

    # 1-2. Aura 남성 (진우)
    aura_male_out = output_dir / "test_aura_male_jinwoo.wav"
    aura_male_text = "여자가 첫눈에 반하는 대화법, 질문 3가지만 바꾸면 오늘부터 애프터 100% 성공합니다. 아우라AI데이팅에서 확인하세요!"
    aura_res_m = aura_cloner.synthesize(aura_male_text, str(aura_male_out), gender="male")
    assert Path(aura_res_m).exists() and Path(aura_res_m).stat().st_size > 1000
    print(f"  ✅ [Aura 남성 (진우)] {aura_male_out.name} ({Path(aura_res_m).stat().st_size} bytes)")

    # 2. 🛡️ 보험 리밸런스 (여성: 서연 / 남성: 진우)
    print("\n[2/3] 🛡️ 보험 리밸런스")
    ins_cloner = InsuranceVoiceCloner(output_dir=str(output_dir))

    # 2-1. 보험 여성 (서연)
    ins_female_out = output_dir / "test_insurance_female_seoyeon.wav"
    ins_female_text = "매달 20만 원 넘게 내는 내 보험, 4세대 실손 전환으로 얼마나 아낄 수 있을까요? 5대 핵심 보장을 지금 분석합니다."
    ins_res_f = ins_cloner.synthesize(ins_female_text, str(ins_female_out), gender="female")
    assert Path(ins_res_f).exists() and Path(ins_res_f).stat().st_size > 1000
    print(f"  ✅ [보험 여성 (서연)] {ins_female_out.name} ({Path(ins_res_f).stat().st_size} bytes)")

    # 2-2. 보험 남성 (진우 - 2번 운전자보험 35세 직장인)
    ins_male_out = output_dir / "test_insurance_male_jinwoo.wav"
    ins_male_text = "출퇴근길 운전하시는 분들, 비싼 특약 다이어트하고 1만 3천 원으로 필수 보장만 꽉 채우는 법! 보험 리밸런스로 확인해보세요."
    ins_res_m = ins_cloner.synthesize(ins_male_text, str(ins_male_out), gender="male")
    assert Path(ins_res_m).exists() and Path(ins_res_m).stat().st_size > 1000
    print(f"  ✅ [보험 남성 (진우)] {ins_male_out.name} ({Path(ins_res_m).stat().st_size} bytes)")

    # 3. 📈 StockMaster AI (남성: 진우 / 여성: 서연)
    print("\n[3/3] 📈 StockMaster AI")
    stock_cloner = StockVoiceCloner(output_dir=str(output_dir))

    # 3-1. 주식 남성 (진우)
    stock_male_out = output_dir / "test_stock_male_jinwoo.wav"
    stock_male_text = "외국인과 기관이 3일 연속 쓸어담은 반도체 대장주! 퀀트 수급과 적정 주가 밸류에이션을 지금 바로 확인하세요."
    stock_res_m = stock_cloner.synthesize(stock_male_text, str(stock_male_out), gender="male")
    assert Path(stock_res_m).exists() and Path(stock_res_m).stat().st_size > 1000
    print(f"  ✅ [주식 남성 (진우)] {stock_male_out.name} ({Path(stock_res_m).stat().st_size} bytes)")

    # 3-2. 주식 여성 (서연)
    stock_female_out = output_dir / "test_stock_female_seoyeon.wav"
    stock_female_text = "오늘의 핵심 테마와 실시간 수급 상위 5대 종목, 스톡마스터 AI 브리핑을 전해드립니다."
    stock_res_f = stock_cloner.synthesize(stock_female_text, str(stock_female_out), gender="female")
    assert Path(stock_res_f).exists() and Path(stock_res_f).stat().st_size > 1000
    print(f"  ✅ [주식 여성 (서연)] {stock_female_out.name} ({Path(stock_res_f).stat().st_size} bytes)")

    print("\n" + "=" * 70)
    print("🎉 [3대 브랜드 남/여 듀얼 음성 복제 파이프라인 100% 무결점 통과]")
    print(f"📁 산출물 저장 위치: {output_dir}")
    print("=" * 70)


if __name__ == "__main__":
    test_all_3brands_voice_cloners()
