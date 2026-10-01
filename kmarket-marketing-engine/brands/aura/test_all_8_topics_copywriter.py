# -*- coding: utf-8 -*-
"""
Test all 8 topics Gemini Copywriter & S5 Builders
"""
import os
import sys
import logging
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "한국 마케팅봇" / "kmarket-marketing-engine"
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TestAll8Topics")

from brands.aura.aura_cardnews_gemini_copywriter import AuraCardnewsGeminiCopywriter
from brands.aura.aura_cardnews_s5_topic1_builder import AuraCardnewsS5Topic1Builder
from brands.aura.aura_cardnews_s5_topic2_builder import AuraCardnewsS5Topic2Builder
from brands.aura.aura_cardnews_s5_topic3_builder import AuraCardnewsS5Topic3Builder
from brands.aura.aura_cardnews_s5_topic4_builder import AuraCardnewsS5Topic4Builder
from brands.aura.aura_cardnews_s5_topic5_builder import AuraCardnewsS5Topic5Builder
from brands.aura.aura_cardnews_s5_topic6_builder import AuraCardnewsS5Topic6Builder
from brands.aura.aura_cardnews_s5_topic7_builder import AuraCardnewsS5Topic7Builder
from brands.aura.aura_cardnews_s5_topic8_builder import AuraCardnewsS5Topic8Builder

s5_builders = {
    1: AuraCardnewsS5Topic1Builder(),
    2: AuraCardnewsS5Topic2Builder(),
    3: AuraCardnewsS5Topic3Builder(),
    4: AuraCardnewsS5Topic4Builder(),
    5: AuraCardnewsS5Topic5Builder(),
    6: AuraCardnewsS5Topic6Builder(),
    7: AuraCardnewsS5Topic7Builder(),
    8: AuraCardnewsS5Topic8Builder(),
}

def main():
    copywriter = AuraCardnewsGeminiCopywriter()
    test_out = Path(__file__).resolve().parent / "s5_tests"
    test_out.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("🚀 [Aura 8대 주제 전체] 제미나이 100% 자율 집필 & S5 엔딩 렌더러 무결성 전수 검증")
    print("=" * 80)

    for t_id in range(1, 9):
        print(f"\n--- [Topic #{t_id} 검증 시작] ---")
        copy_data = copywriter.generate_cardnews_copy(topic_id=t_id)
        
        # 검증
        assert "slide1" in copy_data, f"Topic {t_id} missing slide1"
        assert "slide5" in copy_data, f"Topic {t_id} missing slide5"
        assert "sns_caption" in copy_data, f"Topic {t_id} missing sns_caption"
        
        s1 = copy_data["slide1"]
        s5 = copy_data["slide5"]
        print(f"✅ Topic #{t_id} S1 헤드라인: {s1.get('headline_line1')} / {s1.get('headline_line2')}")
        print(f"✅ Topic #{t_id} S1 부제: {s1.get('subtitle')[:40]}...")
        print(f"✅ Topic #{t_id} S5 찬반: {s5.get('debate_question', s5.get('ending_debate', {}).get('question'))}")
        print(f"✅ Topic #{t_id} SNS 캡션 길이: {len(copy_data.get('sns_caption', ''))}자")

        # S5 렌더링 테스트
        builder = s5_builders[t_id]
        png_out = test_out / f"test_s5_topic_{t_id}.png"
        builder.build_s5_ending_card(str(png_out), copy_data=s5)
        assert png_out.exists() and png_out.stat().st_size > 100000, f"Topic {t_id} S5 PNG render failed"
        print(f"🎉 Topic #{t_id} S5 1080x1350 렌더링 성공: {png_out.name} ({png_out.stat().st_size} bytes)")

    print("\n" + "=" * 80)
    print("🏆 [Aura 8대 주제 전수 검증 100% 통과 완료!] 모든 주제 제미나이 자율 집필 및 S5 렌더러 완벽 작동!")
    print("=" * 80)

if __name__ == "__main__":
    main()
