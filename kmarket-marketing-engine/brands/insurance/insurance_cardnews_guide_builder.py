# -*- coding: utf-8 -*-
"""
InsuranceCardnewsGuideBuilder - 📢 [보험 리밸런스 제미나이 집필 최신 트렌드 집합 SNS 가이드 빌더]
==================================================================================================
• 역할:
  - 제미나이 AI가 집필하는 최신 금융/보험 트렌드 집합 SNS 가이드 자동 생성
  - 카드뉴스(1~5장) 패키지 완성 시 '00_SNS_포스팅_가이드_최신트렌드.txt' 파일 자동 동봉
  - 7대 채널 원스톱 지원:
    1. 📰 네이버 포스트 (Naver Post): 공식 카드형 템플릿 슬라이드 (1~5번 장별 분할 배치)
    2. 📗 네이버 블로그 (Naver Blog): 슬라이드 1~5 배치형 본문 + 검색 유도 + 태그
    3. ☕ 네이버 카페 (Naver Cafe): Zero-URL 침투 원칙 ("네이버에 보험 리밸런스 한번 검색해보세요")
    4. 📸 인스타그램 (Instagram): 캐러셀 넘김 유도 + 프로필 링크 + 4단 티어 해시태그
    5. 🧵 스레드 (Threads): 200자 압축 후킹 + 첫 댓글 링크
    6. 📘 페이스북 (Facebook): 피드 알고리즘 맞춤 첫 댓글 링크
    7. ✈️ 텔레그램 (Telegram): 5장 앨범 + 원클릭 버튼 링크
• 철칙:
  - 공식 검색어: '보험 리밸런스' (띄어쓰기 필수!)
  - 공식 URL: https://insure-rebalance.vercel.app/
  - 네이버 카페: 링크(URL) 삽입 절대 금지, 오직 포털 검색 유도 문구만 사용
  - 100% 무인 자율 구동 & 제미나이 3개 무료키 순차 체인
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .insurance_hashtag_matrix import InsuranceHashtagMatrix

logger = logging.getLogger("InsuranceCardnewsGuideBuilder")

OFFICIAL_KEYWORD = "보험 리밸런스"
OFFICIAL_URL = "https://insure-rebalance.vercel.app/"


class InsuranceCardnewsGuideBuilder:
    """🛡️ 보험 리밸런스 전용 제미나이 집필 최신 트렌드 SNS 가이드 빌더"""

    def __init__(self):
        self.hashtag_matrix = InsuranceHashtagMatrix()

    def build_full_guide(
        self,
        topic_id: int,
        theme_name: str,
        slides_data: List[Dict[str, Any]],
        gemini_copy: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        제미나이 집필 카피와 4단 티어 실시간 트렌드 해시태그를 결합한
        완성형 00_SNS_포스팅_가이드_최신트렌드.txt 텍스트 생성
        """
        logger.info(f"📢 [InsuranceCardnewsGuideBuilder] 주제 #{topic_id} '{theme_name}' 최신 트렌드 SNS 가이드 집필 시작...")

        slide1 = slides_data[0] if len(slides_data) > 0 else {}
        slide2 = slides_data[1] if len(slides_data) > 1 else {}
        slide3 = slides_data[2] if len(slides_data) > 2 else {}
        slide4 = slides_data[3] if len(slides_data) > 3 else {}
        slide5 = slides_data[4] if len(slides_data) > 4 else {}

        # 제미나이 동적 카피 또는 기본값 매핑
        g_copy = gemini_copy or {}
        g_s1 = g_copy.get("slide1", slide1)
        g_s2 = g_copy.get("slide2", slide2)
        g_s3 = g_copy.get("slide3", slide3)
        g_s4 = g_copy.get("slide4", slide4)
        g_s5 = g_copy.get("slide5", slide5)

        title1 = g_s1.get("title", slide1.get("title", "4세대 실손보험 전환 팩트 체크"))
        sub1 = g_s1.get("subtitle", slide1.get("subtitle", "병원 안 가는데 비싼 구실손 유지할 필요 있을까?"))

        title2 = g_s2.get("title", slide2.get("title", "1~3세대 vs 4세대 실손보험료 차이의 진실"))
        sub2 = g_s2.get("subtitle", slide2.get("subtitle", "갱신 폭탄 원인과 비급여 이용량에 따른 손익 분기점"))
        bullets2 = "\n".join([f"  • {b}" for b in g_s2.get("bullets", slide2.get("bullets", []))])

        title3 = g_s3.get("title", slide3.get("title", "이름·전화번호 입력 제로! 4세대 실손 자가진단"))
        sub3 = g_s3.get("subtitle", slide3.get("subtitle", "생년월일만 넣으면 4세대 전환 대상인지 0.1초 만에 확인!"))
        bullets3 = "\n".join([f"  • {b}" for b in g_s3.get("bullets", slide3.get("bullets", []))])

        title4 = g_s4.get("title", slide4.get("title", "스팸 전화 0건! 34개 보험사 최저가 실시간 비교"))
        sub4 = g_s4.get("subtitle", slide4.get("subtitle", "특정사 편파 추천 NO! 34개 모든 보험사 실제 가격표를 투명하게 공개합니다."))
        bullets4 = "\n".join([f"  • {b}" for b in g_s4.get("bullets", slide4.get("bullets", []))])

        title5 = g_s5.get("title", slide5.get("title", "4세대 실손 전환, 지금 갈아타기 vs 기존 1~3세대 유지 중 내 선택은?"))
        sub5 = g_s5.get("subtitle", slide5.get("subtitle", "개인정보 입력 0개로 1분 만에 내 숨은 과납 보험료를 찾아드립니다."))

        # 4단 티어 해시태그 풀 생성
        instagram_tags = self.hashtag_matrix.get_instagram_hashtags(topic_id, count=18)
        threads_tags = self.hashtag_matrix.get_threads_hashtags(topic_id, count=4)
        facebook_tags = self.hashtag_matrix.get_facebook_hashtags(topic_id, count=6)
        naver_tags_str = self.hashtag_matrix.get_naver_tags(topic_id)
        shorts_tags_str = self.hashtag_matrix.get_shorts_hashtags(topic_id)
        hashtags_str = " ".join(instagram_tags)

        # 인스타/페이스북 캡션
        sns_caption = g_copy.get("sns_caption", "")
        if not sns_caption:
            sns_caption = (
                f"매달 나가는 실손보험료 아까우셨던 분들 필독 🚨\n\n"
                f"병원 1년에 몇 번 안 가신다면 옛날 비싼 실비보험 계속 유지할 필요 없습니다.\n"
                f"보험 리밸런스에서 전화번호 입력 없이 34개 보험사 4세대 실손 최저가를 0.1초 만에 비교해 드립니다!\n\n"
                f"✨ 보험 리밸런스 3대 안심 포인트:\n"
                f"1️⃣ 34개 전 보험사 실시간 가격표 0.1초 전수 공개 (월 15,081원 최저가)\n"
                f"2️⃣ 이름·전화번호 입력 제로 (스팸 전화 0건 익명 진단)\n"
                f"3️⃣ 내 나이·성별 맞춤 전환 손익 즉시 판정\n\n"
                f"👉 프로필 링크나 네이버 검색창에 [{OFFICIAL_KEYWORD}]를 검색해보세요!\n\n"
                f"{hashtags_str}"
            )

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        guide_content = f"""================================================================================
🛡️ [보험 리밸런스] 제미나이 집필 최신 트렌드 집합 SNS 포스팅 가이드 (한국어)
================================================================================
📌 테마: {theme_name} (주제 #{topic_id})
⏰ 생성 일시: {now_str}
🔍 공식 포털 검색어: {OFFICIAL_KEYWORD} (띄어쓰기 필수!)
🔗 공식 랜딩 URL: {OFFICIAL_URL}
🏷️ 4단 티어 실시간 바이럴 해시태그 패키지:
{hashtags_str}
================================================================================

[1] 📰 네이버 포스트 (Naver Post) - [카드형] 에디터 전용 가이드
--------------------------------------------------------------------------------
※ 네이버 공식 카드뉴스 플랫폼은 '네이버 포스트 (카드형)'입니다.
   글쓰기 시 반드시 [카드형]을 선택하시면 모바일/PC 좌우 넘김 슬라이드로 완벽 표출됩니다.

📌 [포스트 추천 제목]
{title1} | {theme_name} 팩트체크 총정리

🏷️ [추천 시리즈명]
보험 리밸런스 실전 재테크 백과 (호갱 탈출 꿀팁)

🖼️ [카드형 슬라이드 1~5장 매핑 가이드]
• [표지 카드 1/5]: slide_1.png 업로드
  - 표지 헤드라인: {title1}
  - 표지 서브카피: {sub1}

• [본문 카드 2/5]: slide_2.png 업로드
  - 본문 카피:
{bullets2}

• [본문 카드 3/5]: slide_3.png 업로드 (실물 앱 자가진단 화면)
  - 본문 카피:
{bullets3}

• [본문 카드 4/5]: slide_4.png 업로드 (34개사 최저가 실시간 순위표)
  - 본문 카피:
{bullets4}

• [엔딩 카드 5/5]: slide_5.png 업로드 (찬반 토론 & 네이버 검색 CTA)
  - 엔딩 카피:
    {title5}
    댓글로 여러분의 생각을 자유롭게 남겨주세요!
  - 링크/검색 버튼 설정: 네이버 검색창에 [{OFFICIAL_KEYWORD}] 검색 또는 링크 ({OFFICIAL_URL})

🏷️ [네이버 포스트 공식 태그]
#{OFFICIAL_KEYWORD.replace(' ', '')} #카드뉴스 #네이버포스트 #보험다이어트 #4세대실손 #보험료줄이기 #실비보험 #보험리모델링


[2] 📗 네이버 블로그 (Naver Blog) - 카드뉴스 연속 스크롤 포스팅 가이드
--------------------------------------------------------------------------------
📌 [블로그 추천 포스팅 제목]
{title1} | 34개 보험사 실제 가격표 전수 공개

📝 [네이버 블로그 본문 구성 (카드뉴스 이미지 5장 순서 배치)]
(사진 첨부: slide_1.png)
{title1}
{sub1}

---
(사진 첨부: slide_2.png)
{title2}
{sub2}
{bullets2}

---
(사진 첨부: slide_3.png)
{title3}
{sub3}
{bullets3}

---
(사진 첨부: slide_4.png)
{title4}
{sub4}
{bullets4}

---
(사진 첨부: slide_5.png)
{title5}
{sub5}

💡 [네이버 블로그 하단 CTA 안내문]
내 나이에 딱 맞는 34개 보험사 실시간 최저가 순위표가 궁금하시다면?
네이버 검색창에 [{OFFICIAL_KEYWORD}]를 검색해보세요!
👉 공식 사이트: {OFFICIAL_URL}

🏷️ [네이버 블로그 추천 태그]
{hashtags_str}


[3] ☕ 네이버 카페 (Naver Cafe) - Zero URL 침투 가이드
--------------------------------------------------------------------------------
⚠️ [핵심 침투 철칙]:
네이버 카페 운영원칙상 게시글 및 댓글에 링크(URL) 삽입을 전면 배제하고,
오직 네이버 공식 검색 유도 문구로만 자연스럽게 침투합니다.

📌 [카페 추천 제목]
병원 1년에 한 번 갈까 말까인데 4세대 실손으로 갈아타는 게 맞을까요?

📝 [카페 본문 템플릿]
옛날에 가입해 둔 실비보험인데 매달 보험료가 계속 오르네요 ㅠㅠ
도수치료나 비급여 진료는 거의 안 받는 편인데,
주변에서 4세대로 전환하면 보험료 70%는 줄어든다고 해서 고민 중입니다.

혹시 4세대 실손으로 전환해보신 분들 계신가요?
보장이나 손익 차이 어떤지 후기 궁금합니다!

💬 [카페 댓글 침투 템플릿]
저도 병원 거의 안 가서 옛날 실비 7만원 내다가 4세대로 바꾸고 1만 5천 원으로 줄였어요!
특정 보험사 광고 전화 오는 곳 말고, 네이버에 [{OFFICIAL_KEYWORD}] 검색하면
전화번호 없이 34개 보험사 최저가랑 전환 손익 바로 비교해주더라고요. 한번 검색해보세요!


[4] 📸 인스타그램 (Instagram) - 캐러셀 카드뉴스 캡션 & 해시태그
--------------------------------------------------------------------------------
📌 [캐러셀 피드 본문 캡션 (복사해서 바로 붙여넣기)]:
{sns_caption}


[5] 🧵 스레드 (Threads) - 200자 압축 후킹 가이드
--------------------------------------------------------------------------------
📌 [스레드 본문]:
병원 1년에 한 번 갈까 말까인데 옛날 실비보험료 8만원씩 내고 계신가요? 😭
도수치료 안 받으면 4세대로 갈아타고 월 1만 5천 원으로 70% 아낄 수 있습니다.

스팸 전화 없이 34개 보험사 최저가 가격표 확인하는 법은 첫 번째 댓글에 남겨둘게요 👇

💬 [스레드 첫 번째 댓글 링크]:
네이버 검색창에 [{OFFICIAL_KEYWORD}] 검색하거나 아래 링크에서 확인하세요!
👉 {OFFICIAL_URL}


[6] 📘 페이스북 (Facebook) - 피드 알고리즘 맞춤형 가이드
--------------------------------------------------------------------------------
📌 [페이스북 본문]:
매달 통장에서 빠져나가는 실손보험료, 갱신 폭탄 맞기 전에 꼭 점검해보세요!
1년에 병원 몇 번 안 가는 분들은 4세대 전환만으로도 매달 치킨값 3마리 절약됩니다.

34개 보험사 실시간 최저가 순위표는 첫 번째 댓글에 남겨드립니다.

💬 [페이스북 첫 번째 댓글 링크]:
👉 34개 보험사 실시간 최저가 조회: {OFFICIAL_URL}
(네이버에 [{OFFICIAL_KEYWORD}] 검색)


[7] ✈️ 텔레그램 (Telegram) - 5장 앨범 + 원클릭 버튼 가이드
--------------------------------------------------------------------------------
📌 [텔레그램 메시지]:
🛡️ [보험 리밸런스] {theme_name} 팩트체크 리포트

• 34개 보험사 실시간 최저가 비교 (월 15,081원~)
• 이름·전화번호 입력 제로 (스팸 전화 0건)
• 4세대 실손 전환 자가진단 0.1초 완료

👉 지금 확인하기: {OFFICIAL_URL}
(네이버 검색창에 [{OFFICIAL_KEYWORD}] 검색)


================================================================================
🛡️ 금융소비자보호법(금소법) 심의 프리패스 클린 면책고지
================================================================================
본 콘텐츠는 금융소비자의 이해를 돕기 위한 객관적 정보 제공 목적으로 작성되었으며,
특정 금융상품에 대한 직접적인 계약 체결 권유나 중개 행위를 구성하지 않습니다.
각 보험사별 구체적인 보장 내용, 약관 및 가입 조건은 금융감독원 공시 및 해당 보험사
약관을 통해 반드시 확인하시기 바랍니다.
================================================================================
"""
        return guide_content

    def save_guide_file(
        self,
        target_dir: Path,
        topic_id: int,
        theme_name: str,
        slides_data: List[Dict[str, Any]],
        gemini_copy: Optional[Dict[str, Any]] = None
    ) -> Path:
        """가이드 텍스트 파일을 타겟 폴더에 저장"""
        guide_text = self.build_full_guide(topic_id, theme_name, slides_data, gemini_copy)
        out_path = target_dir / "00_SNS_포스팅_가이드_최신트렌드.txt"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(guide_text)
        logger.info(f"💾 [InsuranceCardnewsGuideBuilder] SNS 가이드 저장 완료: {out_path}")
        return out_path
