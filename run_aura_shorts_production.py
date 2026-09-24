# -*- coding: utf-8 -*-
import sys
import os
from pathlib import Path

# UTF-8 출력 보장
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add kmarket-marketing-engine to sys.path
engine_dir = Path(__file__).resolve().parent / "kmarket-marketing-engine"
sys.path.insert(0, str(engine_dir))

from core.shorts_engine.aura_shorts_producer import AuraShortsProducer


def main():
    print("=" * 70)
    print("🎬 [Aura] 24초 풀숏폼 Wan 2.2 S2V 립싱크 초정밀 원클릭 자율생산 시작")
    print("  - 1. 오디오 선두/후두 무음 정밀 트리밍 (Silence Stripping: 0ms 시작)")
    print("  - 2. 레퍼런스 이미지 입술 닫힘 상태 (gently closed mouth, natural lips closed)")
    print("  - 3. Wan-S2V 공식 권장 파라미터 (CFG 4.5, Shift 3.0, 립싱크 네거티브)")
    print("  - 4. 프롬프트 발화 및 입술 움직임 (Articulate speech, pronouncing words clearly)")
    print("=" * 70)

    producer = AuraShortsProducer()
    # 1~8번 주제 자율 순환 & 매 실행 시 완전 무작위 고유 시드로 새로운 인물/착장 생성
    result = producer.produce()

    print("\n" + "=" * 70)
    print("🎉 [Aura 숏폼 생산 100% 완료!]")
    print(f"  - 완성 파일: {result['output_mp4']}")
    print(f"  - 폴더 경로: {result['output_folder']}")
    print("=" * 70)


if __name__ == "__main__":
    main()
