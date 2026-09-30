# -*- coding: utf-8 -*-
"""
RunTopic5CardnewsPipeline - 🏷️ [Aura 카드뉴스 5번 주제 '가치관 밸런스 매칭' 5장 완결 패키징 파이프라인]
=======================================================================================================
• 역할:
  - 1번 표지 (slide_1.png): 고양이상 21세 여신 (화이트 골지 스퀘어넥 룩 + 연남동 브런치 카페)
  - 2, 3, 4번 (slide_2~4.png): 숏폼 5번 가치관 밸런스 매칭 이식 (비용, 연락, 남사친/여사친)
  - 5번 엔딩 (slide_5.png): 찬반 토론 & 네이버 검색['아우라AI데이팅'] CTA 카드
  - SNS 포스팅 가이드 및 metadata.json 완결 생성
"""

import os
import sys
import json
import logging
import shutil
from pathlib import Path

# UTF-8 출력 보장
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 모듈 경로 추가
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(CURRENT_DIR))

from brands.aura.aura_cardnews_s2_s4_balance_builder import AuraCardnewsS2S4BalanceBuilder
from brands.aura.aura_cardnews_s5_topic5_builder import AuraCardnewsS5Topic5Builder

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RunTopic5CardnewsPipeline")


def run_pipeline(target_dir: str = None) -> str:
    if not target_dir:
        target_dir = r"C:\Users\zkfnt\Desktop\한국 카드뉴스_산출물\아우라\아우라_KO_value_balance_20260930_1821"
    
    out_dir = Path(target_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"🚀 [Aura Theme 5] 카드뉴스 5장 풀세트 패키징 시작 -> {out_dir}")

    # 1. 1번 표지 확인
    s1_path = out_dir / "slide_1.png"
    if not s1_path.exists():
        logger.warning(f"⚠️ slide_1.png 미존재: 백업 탐색 중...")
        # 최근 생성된 최신 1번 표지 탐색
        parent_dir = out_dir.parent
        for d in sorted(parent_dir.glob("아우라_KO_value_balance_*"), reverse=True):
            candidate = d / "slide_1.png"
            if candidate.exists() and candidate != s1_path:
                shutil.copy(candidate, s1_path)
                logger.info(f"✅ slide_1.png 백업 복사 완료 from {candidate}")
                break
    
    if s1_path.exists():
        logger.info(f"✅ [Slide 1/5] 표지 확인 완료: {s1_path}")
    else:
        logger.error("❌ slide_1.png를 찾을 수 없습니다.")

    # 2. 2, 3, 4번 슬라이드 (가치관 밸런스 매칭 3대 라운드) 생성
    logger.info("🎨 [Slide 2~4/5] 가치관 밸런스 매칭 카드 렌더링 중...")
    s2_s4_builder = AuraCardnewsS2S4BalanceBuilder()
    s2_s4_results = s2_s4_builder.build_all(str(out_dir))
    for s_idx, p in s2_s4_results.items():
        logger.info(f"✅ [Slide {s_idx}/5] 생성 완료: {p}")

    # 3. 5번 엔딩 CTA 카드 생성
    logger.info("🎨 [Slide 5/5] 엔딩 찬반 토론 & 네이버 검색 CTA 카드 렌더링 중...")
    s5_builder = AuraCardnewsS5Topic5Builder()
    s5_path = out_dir / "slide_5.png"
    s5_builder.build_s5_ending_card(str(s5_path))
    logger.info(f"✅ [Slide 5/5] 생성 완료: {s5_path}")

    # 4. SNS 포스팅 가이드 작성
    guide_path = out_dir / "SNS_포스팅_가이드_KO.txt"
    guide_content = """[아우라 AI 데이팅] 인스타그램 / 스레드 / 페이스북 카드뉴스 배포 가이드

📌 [콘텐츠 주제]: Aura Theme 5 - "소개팅 첫 만남 더치페이, 칼반띵 vs 2차 사기? 가치관 밸런스 매칭"
📌 [타겟층]: 2030 싱글 남녀, 소개팅 전 가치관 갈등으로 지친 사용자
📌 [공식 유입 키워드]: 네이버 검색창 [아우라AI데이팅] (붙여쓰기)
📌 [공식 웹 랜딩 URL]: https://aura-ai-dating.vercel.app/lounge

================================================================================
📸 [카드뉴스 슬라이드 순서 및 구성]
================================================================================
1. slide_1.png (표지): "소개팅 첫 만남 계산은? 칼반띵 vs 1차 사면 2차 사기 (50:50 황금 성비율)"
2. slide_2.png (ROUND #01 데이트 비용): 칼같이 반띵 48% vs 1차 사면 2차는 상대방이 52% (52% 일치 매칭)
3. slide_3.png (ROUND #02 연락 빈도): 30분 칼답 필수 38% vs 일할 땐 집중 몰아서 자유롭게 62% (62% 일치 매칭)
4. slide_4.png (ROUND #04 이성 친구): 단둘이 식사/커피 OK 24% vs 단둘 만남 절대 불가 76% (76% 일치 매칭)
5. slide_5.png (엔딩 CTA): 실시간 가치관 밸런스 토론 + 네이버 검색 [아우라AI데이팅] + 공식 웹 URL

================================================================================
📝 [인스타그램 / 스레드 피드 본문 캡션 (복사해서 바로 사용)]
================================================================================
소개팅 나갔는데 첫 만남 계산부터 연락 스타일, 남사친 문제까지
가치관 안 맞아서 스트레스 받은 적 있으신가요? 💬

AURA AI는 나와 연애관, 가치관, 라이프스타일이 100% 일치하는 상대만
엄격하게 선별하여 매칭해드립니다. 💖

⚖️ 오늘의 가치관 밸런스 토론!
"소개팅 첫 만남 더치페이, 여러분의 선택은?"
👉 1번: 첫 만남부터 부담 없는 칼반띵 (48%)
👉 2번: 1차 사면 2차는 상대방이 센스 계산 (52%)

댓글에 [1번] vs [2번] 여러분의 솔직한 생각을 남겨주세요! 👇

🔍 네이버 검색창에 [아우라AI데이팅] 검색하고
나랑 가치관 100% 맞는 인연을 지금 바로 만나보세요! ✨

🔗 프로필 링크 또는 공식 웹: https://aura-ai-dating.vercel.app/lounge

#아우라AI데이팅 #소개팅가치관 #밸런스게임 #소개팅더치페이 #데이트비용 #소개팅팁 #20대연애 #30대연애 #직장인소개팅 #데이팅앱추천 #성비50대50 #가치관매칭 #AURA
"""
    with open(guide_path, "w", encoding="utf-8") as f:
        f.write(guide_content)
    logger.info(f"✅ SNS 포스팅 가이드 작성 완료: {guide_path}")

    # 5. metadata.json 작성
    metadata_path = out_dir / "metadata.json"
    meta_info = {
        "brand": "Aura AI Dating",
        "theme_id": 5,
        "theme_name": "가치관 밸런스 매칭 (Value Balance Matching)",
        "resolution": "1080x1350",
        "total_slides": 5,
        "slides": {
            "slide_1": "고양이상 21세 여신 표지 (화이트 골지 스퀘어넥 룩)",
            "slide_2": "ROUND #01 데이트 비용 (칼반띵 48% vs 번갈아 내기 52%)",
            "slide_3": "ROUND #02 연락 빈도 (30분 칼답 38% vs 집중 몰아서 62%)",
            "slide_4": "ROUND #04 이성 친구 (단둘이 OK 24% vs 절대 불가 76%)",
            "slide_5": "실시간 찬반 토론 & 네이버 검색 [아우라AI데이팅] CTA"
        },
        "official_search_keyword": "아우라AI데이팅",
        "official_landing_url": "https://aura-ai-dating.vercel.app/lounge",
        "output_dir": str(out_dir)
    }
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(meta_info, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ metadata.json 작성 완료: {metadata_path}")

    logger.info("🎉 [Aura Theme 5] 카드뉴스 5장 풀세트 패키징 100% 완료!")
    return str(out_dir)


if __name__ == "__main__":
    run_pipeline()
