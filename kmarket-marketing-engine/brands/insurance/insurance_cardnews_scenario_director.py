# -*- coding: utf-8 -*-
"""
InsuranceCardnewsScenarioDirector - 🛡️ [보험 리밸런스 8대 킬러 주제 전용 5장 카드뉴스 시나리오 디렉터]
=============================================================================================
• 원칙:
  1. 100% 대한민국 금융소비자보호법(금소법) 및 보험광고 심의 기준 준수 (과장/공포/비하/단정 0%)
  2. 5장 완결 기승전결 구조 (표지 ➔ 현실 공감 ➔ 팩트/비교 ➔ 절약 솔루션 ➔ 찬반논쟁 & 검색 CTA)
  3. 1080x1350 규격 최적화 헤드라인, 서브타이틀, 3줄 불릿, 배지, CTA 매핑
  4. 공식 검색어: '보험 리밸런스' (띄어쓰기 필수) / 공식 URL: https://insure-rebalance.vercel.app/
  5. 2.0m 황금 웨이스트업 화각 및 K-드라마 남주/여주 신뢰감 있는 실사 비주얼 매핑
"""

import copy
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("InsuranceCardnewsScenarioDirector")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 보험 리밸런스 8대 주제별 5장 골든 카드뉴스 시나리오 DB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INSURANCE_8_CARDNEWS_SCENARIOS: Dict[int, Dict[str, Any]] = {
    1: {
        "topic_id": 1,
        "theme_code": "silson_4th_gen",
        "theme_name": "4세대 실손보험 전환 팩트",
        "official_keyword": "보험 리밸런스",
        "slides": [
            {
                "page": 1,
                "badge": "🔥 실손보험 팩트 체크",
                "title": "병원도 안 가는데 옛날 실비보험\n계속 유지하는 게 맞을까요?",
                "subtitle": "4세대 실손 전환 시 내 비급여 이용량에 따른 객관적 손익을 확인해보세요",
                "bullets": [
                    "병원 이용량이 적은 가입자에게 4세대 실손이 유리한 약관 구조",
                    "전화번호 요구 0개! 스팸 전화 없이 내 눈으로 직접 비교",
                    "대한민국 34개 전 보험사 실시간 객관적 요율 전수 공개"
                ],
                "cta_button": "👉 옆으로 넘겨서 비교 팩트 보기 (1/5) >",
                "image_prompt": (
                    "masterpiece, best quality, ultra-photorealistic portrait, "
                    "photographed from 2.0 meters away on Apple iPhone 15 Pro, "
                    "clear medium waist-up shot showing head, graceful neck, natural shoulders, chest, arms, and torso down to the waistline, "
                    "subtle headroom occupying upper 5% of frame, "
                    "solo 1person female, comfortably sitting upright on a modern living room sofa, perfectly centered in frame, "
                    "perfectly upright head posture with zero tilt, head held straight and level, "
                    "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, "
                    "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and fabric textures, "
                    "an exceptionally gorgeous and poised 42-year-old Korean female (top-tier Korean drama female lead actress look, youthful charming look in her early 40s), "
                    "strictly no glasses, bare clean face with clear glowing porcelain skin, authentic beautiful Korean female facial features, sharp elegant jawline, warm engaging dark eyes, "
                    "neat natural stylish Korean hairstyle, wearing clean stylish civilian casual clothes, a chic modern daily outfit, "
                    "looking directly into camera with genuine composed closed-mouth expression (lips fully closed together, strictly zero teeth showing), "
                    "modern bright sunlit apartment living room with cozy neutral fabric sofa, stylish clean bookshelf and fresh green indoor plants in background, "
                    "crisp clear natural window daylight, vivid vibrant realistic color balance, tack sharp f/11 deep pan-focus, zero yellow tint"
                ),
                "negative_prompt": "ugly, average face, round face, chubby face, plain face, bloated, asymmetrical face, close-up, extreme close-up, cropped face, cropped head, zoomed-in face, male, man, two people, crowd, open mouth, parted lips, visible teeth, showing teeth, laughing, smiling, happy, grinning, cartoon, anime, 3d render, illustration, deformed hands, extra fingers, blurry, low quality, glasses"
            },
            {
                "page": 2,
                "badge": "⚠️ 실손 갱신 구조의 이해",
                "title": "연령 증가와 손해율 상승에 따른\n구세대 실손의 갱신 보험료 구조",
                "subtitle": "구실손(1~2세대)은 전체 가입자의 비급여 청구율이 함께 반영되는 공동 부담 구조입니다.",
                "bullets": [
                    "공동 부담 구조: 비급여 이용량이 많은 그룹의 손해율이 전체 갱신 보험료에 영향",
                    "연령별 위험률: 연령 증가에 따라 갱신 주기마다 보험료 변동 폭 확대",
                    "4세대 개별 할인·할증: 비급여 이용량에 따라 개별적으로 보험료가 차등 적용되는 원리"
                ],
                "cta_button": "👉 다음 장: 4세대 전환 대상 자가진단 (2/5) >",
                "image_prompt": (
                    "masterpiece, best quality, ultra-photorealistic portrait, "
                    "photographed from 2.0 meters away on Apple iPhone 15 Pro, "
                    "clear medium waist-up shot showing head, upper torso, arms holding a smartphone while seated on sofa, torso down to waistline, "
                    "subtle headroom occupying upper 5% of frame, "
                    "solo 1person female, the exact same exceptionally gorgeous and poised 42-year-old Korean female from slide 1, "
                    "strictly no glasses, bare clean face with clear glowing porcelain skin, authentic beautiful Korean female facial features, sharp elegant jawline, "
                    "neat natural stylish Korean hairstyle, wearing the exact same clean stylish civilian casual clothes, a chic modern daily outfit, "
                    "comfortably sitting on the modern fabric living room sofa, holding her sleek smartphone in both hands at chest level, looking down intently at the screen, "
                    "showing a genuine troubled, thoughtful, and serious facial expression (진지하게 고민하는 현실 자각 표정), subtle furrowed brow, lips firmly closed together, strictly zero open mouth, strictly no visible teeth, "
                    "bright natural indoor ambient daylight, modern clean living room background, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and fabric textures"
                ),
                "negative_prompt": "ugly, average face, round face, chubby face, plain face, bloated, asymmetrical face, close-up, extreme close-up, cropped face, cropped head, zoomed-in face, male, man, two people, crowd, open mouth, parted lips, visible teeth, showing teeth, laughing, smiling, happy, grinning, cartoon, anime, 3d render, illustration, deformed hands, extra fingers, blurry, low quality, glasses"
            },
            {
                "page": 3,
                "badge": "💡 0.1초 자가진단",
                "title": "이름·전화번호 없이 내 조건만 체크!\n4세대 전환 대상인지 0.1초 확인",
                "subtitle": "생년월일과 비급여 이용량만 선택하면 4세대 손익이 즉시 나옵니다.",
                "bullets": [
                    "100% PII-Free: 이름, 주민번호, 연락처 단 1개도 요구하지 않는 안심 구조",
                    "비급여 이용량 분석: 도수치료·비급여 주사제 이용 패턴에 따른 전환 손익 산출",
                    "즉시 판별: 가입 이력과 간단 조건만으로 신규/전환 대상 여부 0.1초 진단"
                ],
                "cta_button": "👉 다음 장: 34개 보험사 객관적 순위표 보기 (3/5) >",
                "use_direct_asset": True,
                "asset_image": "brands/insurance/assets/slide3_silbi_condition.png"
            },
            {
                "page": 4,
                "badge": "📊 대한민국 34개사 전수 공개",
                "title": "스팸 전화 0건! 34개 보험사\n동일 보장 기준 실시간 요율 비교",
                "subtitle": "특정사 편파 추천 없이 대한민국 모든 생·손보사 실제 가격을 실시간 공개합니다.",
                "bullets": [
                    "동일 보장 기준 최저가 순위: 연령별 최적의 다이렉트 상품 투명 공개",
                    "스팸 영업 0건: 조회 즉시 빗발치는 가입 권유 전화 원천 차단",
                    "금융감독원 공시 연동: 34개사 실제 공시 요율을 0.1초 만에 최저가 순위 정렬"
                ],
                "cta_button": "👉 다음 장: 내 보험료 1초 만에 조회하는 법 (4/5) >",
                "use_direct_asset": True,
                "asset_image": "brands/insurance/assets/slide4_price_comparison.png"
            },
            {
                "page": 5,
                "badge": "찬반 토론 & 1분 진단 CTA",
                "title": "구세대 실손 유지 vs 4세대 전환\n내 병원 이용 패턴에 맞춘 현명한 선택",
                "subtitle": "개인정보 입력 없이 1분 만에 내 실손보험의 객관적 손익을 진단해보세요",
                "bullets": [
                    "전화번호 없이 안전하게 34개 보험사 실시간 다이렉트 견적 조회",
                    "비급여 이용 패턴에 맞춰 내게 유리한 최적의 세대 선택",
                    "👉 지금 네이버 검색창에 '보험 리밸런스'를 검색해보세요!"
                ],
                "cta_button": "👉 네이버에 '보험 리밸런스' 검색하기 >",
                "debate_badge": "⚡ 실손보험 현실 토론",
                "debate_question": "실손보험, 구실손(1~2세대) 유지 vs 4세대 전환?",
                "debate_opt1_title": "🔄 4세대 실손 전환",
                "debate_opt1_sub": "병원 이용 적으면 보험료 경감 및 개별 할인 혜택 선택",
                "debate_opt1_rate": "72% (대세)",
                "debate_opt2_title": "🛡️ 기존 구실손 유지",
                "debate_opt2_sub": "자기부담금 적은 기존 보장 혜택 만기까지 유지",
                "debate_opt2_rate": "28%",
                "benefit_items": [
                    "34개 보험사 실손보험 실시간 객관적 비교",
                    "이름·전화번호 입력 제로 (PII-Free 안심 구조)",
                    "0.1초 만에 비급여 이용량별 손익 자가진단"
                ],
                "cta_subtext": "✨ 스팸 전화 0건 • 지금 조회하고 내 실손보험 객관적 분석하기"
            }
        ]
    },
    2: {
        "topic_id": 2,
        "theme_code": "driver_insurance",
        "theme_name": "운전자보험 1만원의 법칙",
        "official_keyword": "보험 리밸런스",
        "slides": [
            {
                "page": 1,
                "badge": "🚗 운전자보험 필수 점검",
                "title": "운전자보험 매달 3, 4만 원씩 내시나요?\n필수 3대 특약만 챙기면 월 1만 원대 설계 가능!",
                "subtitle": "자동차보험과 중복되는 상해 특약을 분리하고 필수 형사 책임 보장 위주로 완성하기",
                "bullets": [
                    "민사 배상책임은 자동차보험에서, 형사처벌 위험은 운전자보험에서 분리",
                    "벌금 + 변호사선임비용 + 교통사고처리지원금 필수 3대 세팅",
                    "34개 보험사 다이렉트 운전자보험 실시간 0.1초 객관적 비교"
                ],
                "cta_button": "👉 1만원대 운전자보험 맞추는 법 (1/5) >",
                "image_prompt": (
                    "masterpiece, best quality, ultra-photorealistic portrait, "
                    "photographed from 2.0 meters away on Apple iPhone 15 Pro, "
                    "clear medium waist-up shot showing head, broad suited shoulders, suit jacket, arms, and torso down to the waistline and belt, "
                    "subtle headroom occupying upper 5% of frame, "
                    "solo 1person male, standing with natural upright posture, perfectly centered in frame, "
                    "perfectly upright head posture with zero tilt, head held straight and level, "
                    "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, symmetrical eyes with natural relaxed eyelids, "
                    "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and sharp fabric textures, "
                    "an exceptionally handsome and sharp 35-year-old Korean male professional (top-tier Korean drama male lead actor look, striking youthful attractive look in his 30s), "
                    "strictly no glasses, bare clean face with clear smooth natural skin, authentic handsome Korean male facial features, attractive gentle dark eyes, sharp masculine chiseled jawline, "
                    "stylish trendy Korean parted perm hairstyle (soft wavy side-parted comma hair with natural textured fringe, thick rich jet-black healthy hair, strictly ZERO grey hair, strictly NO white hair), "
                    "wearing a sharp tailored dark navy business suit jacket over a crisp white dress shirt and neat tie, pristine executive professional look, "
                    "looking directly into camera lens with confident composed closed-mouth expression (lips firmly closed together, strictly zero teeth showing), "
                    "modern K-drama handsome relatable commuter lead look, "
                    "bustling modern Seoul Gangnam business boulevard background with modern architectural glass facade and green city trees behind him, "
                    "bright crisp natural morning sunlight, crystal clear edge-to-edge deep focus across the entire scene, vivid authentic Korean city realism, zero yellow tint"
                ),
                "negative_prompt": "ugly, average face, round face, chubby face, plain face, bloated, asymmetrical face, close-up, extreme close-up, cropped face, cropped head, zoomed-in face, female, woman, two people, crowd, open mouth, parted lips, visible teeth, showing teeth, laughing, smiling, happy, grinning, cartoon, anime, 3d render, illustration, deformed hands, extra fingers, blurry, low quality, glasses, beard, mustache, goatee, stubble, facial hair, whiskers, 5 o'clock shadow"
            },
            {
                "page": 2,
                "badge": "🚨 현실 분석 100%",
                "title": "자동차보험과 운전자보험\n보장 영역 완벽 분리하기",
                "subtitle": "대물·대인 배상은 자동차보험에서 처리됩니다. 운전자보험은 형사합의·벌금에 집중하세요",
                "bullets": [
                    "자동차보험(민사적 책임) vs 운전자보험(형사적·행정적 책임) 역할 분담",
                    "골절·상해·입원일당 등 중복 특약 여부 점검으로 보험료 최적화",
                    "스쿨존 사고·12대 중과실 형사처벌 대비 핵심 3대 특약 집중"
                ],
                "cta_button": "👉 다음 장: 필수 3대 특약 확인하기 (2/5) >",
                "image_prompt": (
                    "masterpiece, best quality, ultra-photorealistic portrait, "
                    "photographed from 2.0 meters away on Apple iPhone 15 Pro, "
                    "clear medium waist-up shot showing head, upper torso in dark navy suit, arms holding smartphone in car driver seat, torso down to waistline, "
                    "subtle headroom occupying upper 5% of frame, "
                    "solo 1person male, the exact same exceptionally handsome and sharp 35-year-old Korean male professional from slide 1 (top-tier Korean drama male lead actor look), "
                    "strictly no glasses, bare clean face with clear smooth natural skin, authentic handsome Korean male facial features, sharp masculine chiseled jawline, "
                    "the exact same stylish trendy Korean parted perm hairstyle (soft wavy side-parted comma hair with natural textured fringe), "
                    "wearing the exact same sharp tailored dark navy business suit jacket over a crisp white dress shirt and neat tie, "
                    "seated in the driver seat of a modern sleek sedan car, holding his smartphone in hand, looking at an insurance policy notice on phone screen, "
                    "showing a realistic troubled and thoughtful expression (진지하게 점검하는 현실 자각 표정), furrowed brow, lips firmly closed together, strictly zero open mouth, strictly no visible teeth, "
                    "bright crisp natural daylight entering car window, modern car leather interior visible, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and sharp fabric textures, vivid authentic Korean city realism"
                ),
                "negative_prompt": "ugly, average face, round face, chubby face, plain face, bloated, asymmetrical face, close-up, extreme close-up, cropped face, cropped head, zoomed-in face, female, woman, two people, crowd, open mouth, parted lips, visible teeth, showing teeth, laughing, smiling, happy, grinning, cartoon, anime, 3d render, illustration, deformed hands, extra fingers, blurry, low quality, glasses, beard, mustache, goatee, stubble, facial hair, whiskers, 5 o'clock shadow"
            },
            {
                "page": 3,
                "badge": "💡 0.1초 안심 자가진단",
                "title": "전화번호 없이 생년월일만 체크!\n내 운전자보험료 0.1초 즉시 계산",
                "subtitle": "이름·전화번호 단 1개도 요구하지 않는 100% PII-Free 안심 구조",
                "bullets": [
                    "생년월일과 운전 용도(자가용/영업용)만 선택하면 0.1초 즉시 진단",
                    "스팸 영업 전화 0건: 연락처 수집 없는 완벽한 익명 진단",
                    "필수 3대 특약만 맞춤 세팅하여 불필요한 과납 보험료 사전 차단"
                ],
                "cta_button": "👉 다음 장: 34개 보험사 최저가 순위표 보기 (3/5) >",
                "use_direct_asset": True,
                "asset_image": "brands/insurance/assets/driver_slide3_condition.png"
            },
            {
                "page": 4,
                "badge": "📊 대한민국 34개사 전수 공개",
                "title": "스팸 전화 0건! 34개 보험사\n운전자보험 실시간 다이렉트 순위표",
                "subtitle": "특정사 편파 추천 없이 대한민국 모든 손해보험사 실제 가격을 실시간 공개합니다.",
                "bullets": [
                    "동일 3대 필수 보장 기준 최저가 1위 회사 투명 공개",
                    "스팸 영업 전화 0건: 조회 즉시 빗발치는 가입 권유 전화 원천 차단",
                    "금융감독원 공시 연동: 34개사 실제 공시 요율을 0.1초 만에 최저가 순위 정렬"
                ],
                "cta_button": "👉 다음 장: 내 숨은 보험료 1초 만에 확인하기 (4/5) >",
                "use_direct_asset": True,
                "asset_image": "brands/insurance/assets/driver_slide4_result.png"
            },
            {
                "page": 5,
                "badge": "찬반 토론 & 1분 진단 CTA",
                "title": "운전자보험 필수 3대형 vs 상해 종합형\n여러분은 어떤 구성을 선택하셨나요?",
                "subtitle": "개인정보 입력 0개로 1분 만에 내 중복 특약 여부를 확인해보세요",
                "bullets": [
                    "전화번호 없이 안전하게 34개사 다이렉트 견적 조회",
                    "불필요한 중복 상해특약을 정비하고 핵심 형사책임 보장만 알뜰 설계",
                    "👉 지금 네이버 검색창에 '보험 리밸런스'를 검색해보세요!"
                ],
                "cta_button": "👉 네이버에 '보험 리밸런스' 검색하기 >",
                "debate_badge": "⚡ 운전자보험 현실 토론",
                "debate_question": "운전자보험, 월 1만원대 필수 3대만 가입 vs 월 3~4만원 상해특약 풀가입?",
                "debate_opt1_title": "🛡️ 월 1만원대 필수 3대만 가입",
                "debate_opt1_sub": "교통사고처리지원금·변호사·벌금 형사책임만 알뜰 세팅!",
                "debate_opt1_rate": "84% (대세)",
                "debate_opt2_title": "📑 월 3~4만원 상해특약 포함 가입",
                "debate_opt2_sub": "골절·깁스·입원일당까지 운전자보험 하나로 통합 가입",
                "debate_opt2_rate": "16%",
                "benefit_items": [
                    "34개 보험사 운전자보험 실시간 최저가 비교",
                    "이름·전화번호 입력 제로 (PII-Free 안심 구조)",
                    "0.1초 만에 불필요 중복 특약 자가진단"
                ],
                "cta_subtext": "✨ 스팸 전화 0건 • 지금 조회하고 내 운전자보험 객관적 분석하기"
            }
        ]
    },
    3: {
        "topic_id": 3,
        "theme_code": "cancer_coverage",
        "theme_name": "암보험 일반암 vs 유사암 진실",
        "official_keyword": "보험 리밸런스",
        "slides": [
            {
                "page": 1,
                "badge": "🚨 암보험 약관 점검",
                "title": "암보험 5천만 원 든 줄 알았는데…\n갑상선암은 소액암으로 분류된다고요?",
                "subtitle": "약관상 일반암과 유사암(10~20%)의 보장 비율 차이를 확인하세요",
                "bullets": [
                    "일반암(100% 지급) vs 유사암·소액암(10~20% 감액) 약관 분리 기준",
                    "갑상선암·제자리암·경계성종양의 약관상 보장 한도 점검",
                    "34개 보험사 다이렉트 암보험 객관적 요율 실시간 0.1초 확인"
                ],
                "cta_button": "👉 내가 원하는 암 진단금 맞추는 법 (1/5) >",
                "image_prompt": (
                    "masterpiece, best quality, ultra-photorealistic portrait, "
                    "photographed from 2.0 meters away on Apple iPhone 15 Pro, "
                    "clear medium waist-up shot showing head, broad shoulders, cream knit sweater, arms, and torso down to the waistline, "
                    "subtle headroom occupying upper 5% of frame, "
                    "solo 1person female, standing with natural upright posture, perfectly centered in frame, "
                    "perfectly upright head posture with zero tilt, head held straight and level, "
                    "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, symmetrical eyes with natural relaxed eyelids, "
                    "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and sharp fabric textures, "
                    "a sensible, elegant, and poised 45-year-old Korean career woman (top-tier Korean drama female lead actress look), "
                    "strictly no glasses, bare clean face with clear glowing porcelain skin, authentic beautiful Korean female facial features, sharp elegant jawline, warm engaging dark eyes, "
                    "neat elegant Korean medium bob hairstyle with soft natural waves, "
                    "wearing a high-end cozy cream soft knit sweater with fine knit texture, pristine elegant civilian look, "
                    "looking directly into camera lens with sincere composed closed-mouth expression (lips firmly closed together, strictly zero teeth showing), "
                    "cozy bright modern Korean apartment living room background with soft morning ambient sunlight and tasteful wooden interior shelf behind her, "
                    "crystal clear edge-to-edge deep focus across the entire scene, vivid authentic Korean home realism, zero yellow tint"
                ),
                "negative_prompt": "ugly, average face, round face, chubby face, plain face, bloated, asymmetrical face, close-up, extreme close-up, cropped face, cropped head, zoomed-in face, male, man, two people, crowd, open mouth, parted lips, visible teeth, showing teeth, laughing, smiling, happy, grinning, cartoon, anime, 3d render, illustration, deformed hands, extra fingers, blurry, low quality, glasses"
            },
            {
                "page": 2,
                "badge": "📊 약관 팩트 분석",
                "title": "일반암과 유사암·소액암의\n약관상 보장 범위 팩트",
                "subtitle": "갑상선암, 제자리암, 경계성종양은 대부분의 약관에서 유사암으로 분류됩니다",
                "bullets": [
                    "발병 통계 상위 갑상선암의 약관상 유사암 분류 기준 확인",
                    "유사암 진단비 별도 가입 여부에 따른 실제 보장 범위 점검",
                    "34개 보험사별 일반암 및 유사암 보장 한도 0.1초 객관적 분석"
                ],
                "cta_button": "👉 다음 장: 내 암보험 보장 범위 확인하기 (2/5) >",
                "image_prompt": (
                    "masterpiece, best quality, ultra-photorealistic portrait, "
                    "photographed from 2.0 meters away on Apple iPhone 15 Pro, "
                    "clear medium waist-up shot showing head, upper torso in knit sweater, arms holding an insurance policy document at table, torso down to waistline, "
                    "subtle headroom occupying upper 5% of frame, "
                    "solo 1person female, the exact same sensible, elegant, and attractive 45-year-old Korean career woman from slide 1, "
                    "strictly no glasses, bare clean face with clear natural skin, authentic beautiful Korean female facial features, sharp elegant jawline, "
                    "neat elegant Korean medium bob hairstyle with soft natural waves, "
                    "wearing the exact same cozy cream soft knit sweater, "
                    "seated at a modern wooden table in a bright study room, looking down at her insurance policy document showing a serious and thoughtful expression (약관을 꼼꼼히 확인하는 표정), furrowed brow, lips firmly closed together, strictly zero open mouth, strictly no visible teeth, "
                    "bright crisp natural morning daylight entering the window, modern clean study interior with oak bookshelf, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and fabric textures"
                ),
                "negative_prompt": "ugly, average face, round face, chubby face, plain face, bloated, asymmetrical face, close-up, extreme close-up, cropped face, cropped head, zoomed-in face, male, man, two people, crowd, open mouth, parted lips, visible teeth, showing teeth, laughing, smiling, happy, grinning, cartoon, anime, 3d render, illustration, deformed hands, extra fingers, blurry, low quality, glasses"
            },
            {
                "page": 3,
                "badge": "💡 0.1초 안심 자가진단",
                "title": "전화번호 없이 생년월일만 체크!\n내가 원하는 암 진단금 0.1초 즉시 계산",
                "subtitle": "일반암 진단비 + 암주요치료비 + 표적항암 맞춤형 설계 비교",
                "bullets": [
                    "생년월일 선택 시 연령별 암보험 요율 0.1초 즉시 계산",
                    "최신 암주요치료비 및 표적항암 특약 구성 조건별 비교",
                    "스팸 영업 전화 0건: 연락처 수집 없는 완벽한 익명 진단"
                ],
                "cta_button": "👉 다음 장: 34개 보험사 암보험 순위표 보기 (3/5) >",
                "use_direct_asset": True,
                "asset_image": "brands/insurance/assets/cancer_slide3_condition.png"
            },
            {
                "page": 4,
                "badge": "📊 대한민국 34개사 전수 공개",
                "title": "스팸 전화 0건! 34개 보험사\n암보험 다이렉트 실시간 순위표",
                "subtitle": "특정사 편파 추천 없이 대한민국 모든 보험사 실제 가격을 실시간 공개합니다.",
                "bullets": [
                    "동일 일반암 진단금 기준 최저가 1위 회사 투명 공개",
                    "스팸 영업 전화 0건: 조회 즉시 빗발치는 가입 권유 전화 원천 차단",
                    "금융감독원 공시 연동: 34개사 실제 공시 요율을 0.1초 만에 최저가 순위 정렬"
                ],
                "cta_button": "👉 다음 장: 내 암보험료 1초 만에 확인하기 (4/5) >",
                "use_direct_asset": True,
                "asset_image": "brands/insurance/assets/cancer_slide4_result.png"
            },
            {
                "page": 5,
                "badge": "찬반 토론 & 1분 진단 CTA",
                "title": "암 진단비 집중 vs 암 치료비(항암/방사선) 보강\n내게 꼭 맞는 암보험 구성은?",
                "subtitle": "개인정보 입력 0개로 1분 만에 내 증권의 암 보장 범위를 점검해보세요",
                "bullets": [
                    "전화번호 없이 안전하게 34개사 암보험 다이렉트 견적 조회",
                    "유사암·소액암 보장 한도와 최신 치료비 특약을 객관적으로 비교",
                    "👉 지금 네이버 검색창에 '보험 리밸런스'를 검색해보세요!"
                ],
                "cta_button": "👉 네이버에 '보험 리밸런스' 검색하기 >",
                "debate_badge": "⚡ 암보험 현실 토론",
                "debate_question": "암보험 리밸런스, 진단비 일시금 집중 vs 최신 항암 치료비 특약 추가?",
                "debate_opt1_title": "🛡️ 진단비 일시금 집중",
                "debate_opt1_sub": "생활비 및 치료비 목돈으로 자유롭게 활용 가능한 진단비 확보",
                "debate_opt1_rate": "68%",
                "debate_opt2_title": "💊 최신 표적·중입자 치료비 보강",
                "debate_opt2_sub": "고액 비급여 신약 치료비에 대비하는 맞춤형 치료비 특약 추가",
                "debate_opt2_rate": "32%",
                "benefit_items": [
                    "34개 보험사 암보험 실시간 최저가 비교",
                    "이름·전화번호 입력 제로 (PII-Free 안심 구조)",
                    "0.1초 만에 일반암 vs 유사암 보장 범위 자가진단"
                ],
                "cta_subtext": "✨ 스팸 전화 0건 • 지금 조회하고 내 암보험 보장 범위 완벽 체크"
            }
        ]
    },
    4: {
        "topic_id": 4,
        "theme_code": "brain_heart_vascular",
        "theme_name": "뇌·심장 질환 뇌출혈 vs 뇌혈관",
        "official_keyword": "보험 리밸런스",
        "slides": [
            {
                "page": 1,
                "badge": "🚨 2대 혈관질환 약관 점검",
                "title": "뇌질환 진단비 든 줄 알았는데…\n뇌경색은 보장 제외될 수 있다고요?",
                "subtitle": "뇌출혈 vs 뇌졸중 vs 뇌혈관질환, 약관상 보장 범위의 차이를 확인하세요",
                "bullets": [
                    "뇌출혈(약 16%) ➔ 뇌졸중(약 60%) ➔ 뇌혈관질환(100% 포괄) 범위 비교",
                    "급성심근경색 단독 vs 허혈성·심혈관질환 포괄 특약 차이 점검",
                    "34개 보험사 다이렉트 뇌·심장 보험료 실시간 0.1초 비교"
                ],
                "cta_button": "👉 뇌·심장 100% 보장 범위 맞추는 법 (1/5) >",
                "image_prompt": (
                    "masterpiece, best quality, ultra-photorealistic portrait, "
                    "photographed from 2.0 meters away on Apple iPhone 15 Pro, "
                    "clear medium waist-up shot showing head, broad masculine shoulders, charcoal-grey knit sweater, arms, and torso down to the waistline, "
                    "subtle headroom occupying upper 5% of frame, "
                    "solo 1person male, standing with natural upright posture, perfectly centered in frame, "
                    "perfectly upright head posture with zero tilt, head held straight and level, "
                    "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, symmetrical eyes with natural relaxed eyelids, "
                    "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and sharp fabric textures, "
                    "an exceptionally handsome and charming 40s Korean male (top-tier Korean drama male lead actor look, striking youthful attractive look in his early 40s), "
                    "strictly no glasses, bare clean face with clear smooth healthy skin, authentic handsome Korean male facial features, sharp masculine chiseled jawline, warm charismatic dark eyes, "
                    "strictly clean-shaven, completely hairless smooth skin on chin and upper lip, strictly zero facial hair, strictly no beard, strictly no mustache, strictly no goatee, strictly no stubble, "
                    "stylish trendy Korean parted perm hairstyle (soft wavy side-parted comma hair with natural textured fringe, thick rich jet-black healthy hair, strictly ZERO grey hair, strictly NO white hair), "
                    "wearing a modern sophisticated charcoal-grey crewneck knit sweater, chic high-end Korean civilian casual look, "
                    "looking directly into camera lens with composed trustworthy closed-mouth expression (lips firmly closed together, strictly zero teeth showing), "
                    "bright modern luxury Korean apartment living room with cozy sofa and large window showing soft morning natural daylight, minimalist Scandinavian wooden furniture behind him, "
                    "crystal clear edge-to-edge deep focus across the entire scene, vivid authentic Korean home realism, zero yellow tint"
                ),
                "negative_prompt": "ugly, average face, round face, chubby face, plain face, bloated, asymmetrical face, close-up, extreme close-up, cropped face, cropped head, zoomed-in face, female, woman, two people, crowd, open mouth, parted lips, visible teeth, showing teeth, laughing, smiling, happy, grinning, cartoon, anime, 3d render, illustration, deformed hands, extra fingers, blurry, low quality, glasses, suit, tie, jacket, beard, mustache, goatee, stubble, facial hair, whiskers, 5 o'clock shadow"
            },
            {
                "page": 2,
                "badge": "🚨 약관 보장 범위 팩트",
                "title": "뇌질환 환자의 다수는 뇌경색\n'뇌출혈' 단독 특약의 보장 공백",
                "subtitle": "뇌경색·뇌동맥류는 '뇌출혈 진단비' 단독 약관에서는 보장 대상에서 제외됩니다",
                "bullets": [
                    "뇌출혈 보장 범위: 전체 뇌질환 통계의 일부(약 16%) 커버",
                    "뇌졸중 보장 범위: 뇌출혈 + 뇌경색 (약 60% 커버)",
                    "뇌혈관질환 보장 범위: 초기 뇌동맥류 및 기타 뇌혈관 질환까지 포괄 보장"
                ],
                "cta_button": "👉 다음 장: 100% 보장 범위 확인하기 (2/5) >",
                "image_prompt": (
                    "masterpiece, best quality, ultra-photorealistic portrait, "
                    "photographed from 2.0 meters away on Apple iPhone 15 Pro, "
                    "clear medium waist-up shot showing head, upper torso, arms holding an insurance policy document in hand, torso down to waistline, "
                    "subtle headroom occupying upper 5% of frame, "
                    "solo 1person male, the exact same exceptionally handsome and charming 40s Korean male from slide 1 (top-tier Korean drama male lead actor look), "
                    "strictly no glasses, bare clean face with clear smooth healthy skin, authentic handsome Korean male facial features, sharp masculine chiseled jawline, "
                    "strictly clean-shaven, completely hairless smooth skin on chin and upper lip, strictly zero facial hair, strictly no beard, strictly no mustache, strictly no goatee, strictly no stubble, "
                    "the exact same stylish natural soft wavy side-parted comma hairstyle with textured fringe bangs covering part of forehead, thick rich jet-black healthy hair, strictly ZERO grey hair, strictly NO white hair, "
                    "wearing the exact same modern sophisticated charcoal-grey crewneck knit sweater, chic high-end Korean civilian casual look, "
                    "comfortably sitting upright on the modern neutral fabric living room sofa, looking down at his old insurance policy paper showing a realistic thoughtful and serious expression (약관을 진지하게 점검하는 표정), furrowed brow, lips firmly closed together, strictly zero open mouth, strictly no visible teeth, "
                    "bright crisp natural morning daylight from large window, minimalist Scandinavian wooden living room interior with neutral sofa, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and fabric textures, vivid authentic Korean home realism"
                ),
                "negative_prompt": "ugly, average face, round face, chubby face, plain face, bloated, asymmetrical face, close-up, extreme close-up, cropped face, cropped head, zoomed-in face, female, woman, two people, crowd, open mouth, parted lips, visible teeth, showing teeth, laughing, smiling, happy, grinning, cartoon, anime, 3d render, illustration, deformed hands, extra fingers, blurry, low quality, glasses, suit, tie, jacket, beard, mustache, goatee, stubble, facial hair, whiskers, 5 o'clock shadow"
            },
            {
                "page": 3,
                "badge": "💡 0.1초 안심 자가진단",
                "title": "전화번호 없이 생년월일만 체크!\n뇌혈관질환 진단비 0.1초 즉시 계산",
                "subtitle": "뇌혈관 진단비 1,000만원 기준 최적화 설계 + 100% PII-Free 익명 진단",
                "bullets": [
                    "생년월일(19821003)과 남성 선택 시 0.1초 즉시 계산",
                    "뇌혈관질환 진단비 1,000만원 맞춤형 원클릭 세팅",
                    "스팸 영업 전화 0건: 연락처 수집 없는 완벽한 익명 진단"
                ],
                "cta_button": "👉 다음 장: 34개 보험사 뇌혈관 순위표 보기 (3/5) >",
                "use_direct_asset": True,
                "asset_image": "brands/insurance/assets/brain_slide3_condition.png"
            },
            {
                "page": 4,
                "badge": "📊 대한민국 34개사 전수 공개",
                "title": "스팸 전화 0건! 34개 보험사\n뇌혈관 최저가 실시간 순위표",
                "subtitle": "특정사 편파 추천 없이 대한민국 모든 손해보험사 실제 가격을 실시간 공개합니다.",
                "bullets": [
                    "동일 뇌혈관 1,000만원 기준 최저가 1위 회사 투명 공개",
                    "스팸 영업 전화 0건: 조회 즉시 빗발치는 가입 권유 전화 원천 차단",
                    "금융감독원 공시 연동: 34개사 실제 공시 요율을 0.1초 만에 최저가 순위 정렬"
                ],
                "cta_button": "👉 다음 장: 내 뇌혈관 보험료 1초 만에 확인하기 (4/5) >",
                "use_direct_asset": True,
                "asset_image": "brands/insurance/assets/brain_slide4_result.png"
            },
            {
                "page": 5,
                "badge": "찬반 토론 & 1분 진단 CTA",
                "title": "뇌혈관 단독 특약 보강 vs 종합보험 재설계\n여러분은 어떻게 리밸런스 하셨나요?",
                "subtitle": "개인정보 입력 0개로 1분 만에 내 증권의 2대 혈관질환 보장 범위를 확인해보세요",
                "bullets": [
                    "전화번호 없이 안전하게 34개사 뇌혈관 다이렉트 견적 조회",
                    "뇌출혈만 가입된 좁은 특약에 뇌혈관·허혈성 특약을 스마트하게 보강",
                    "👉 지금 네이버 검색창에 '보험 리밸런스'를 검색해보세요!"
                ],
                "cta_button": "👉 네이버에 '보험 리밸런스' 검색하기 >",
                "debate_badge": "⚡ 뇌혈관질환 현실 토론",
                "debate_question": "뇌혈관 보장 리밸런스, 기존 보험 유지하며 단독 특약 추가 vs 전체 재가입?",
                "debate_opt1_title": "🛡️ 단독 특약 추가 보강",
                "debate_opt1_sub": "기존 좋은 실손/암보험은 유지하고 뇌혈관·허혈성만 쏙 보강!",
                "debate_opt1_rate": "81% (대세)",
                "debate_opt2_title": "🔄 전체 해지 후 최신 종합보험 재가입",
                "debate_opt2_sub": "복잡한 여러 개 보험 하나로 싹 통합해서 일괄 관리",
                "debate_opt2_rate": "19%",
                "benefit_items": [
                    "34개 보험사 뇌혈관 실시간 최저가 비교",
                    "이름·전화번호 입력 제로 (PII-Free 안심 구조)",
                    "0.1초 만에 뇌경색 보장 공백 자가진단"
                ],
                "cta_subtext": "✨ 스팸 전화 0건 • 지금 조회하고 내 뇌혈관 보장 범위 완벽 체크"
            }
        ]
    },
    5: {
        "topic_id": 5,
        "theme_code": "acquaintance_insurance",
        "theme_name": "아는 사람 부탁으로 가입한 보험 손익 분석",
        "official_keyword": "보험 리밸런스",
        "slides": [
            {
                "page": 1,
                "badge": "📋 약관 기반 팩트체크",
                "title": "아는 사람 부탁으로 가입한 보험\n내 증권의 실제 보장 범위 점검",
                "subtitle": "지인 권유로 가입했던 종합보험, 과연 나에게 꼭 필요한 보장 위주로 설계되었을까요?",
                "bullets": [
                    "만기 시 돌려받는 돈 없는 불필요한 적립보험료 포함 여부 확인",
                    "나이가 들수록 보험료가 인상되는 갱신형 특약 비중 체크",
                    "암·뇌·심장 3대 질환의 실제 진단비 보장 범위 확인"
                ],
                "cta_button": "👉 지인 보험 약관 팩트 확인하기 (1/5) >",
                "image_prompt": (
                    "photographed from 2.5 meters away on Apple iPhone 15 Pro, "
                    "clear medium waist-up upper body shot showing head, masculine neck, broad natural shoulders, white oxford cotton shirt, arms, and torso down to the waistline, "
                    "subtle headroom occupying upper 5% of frame, "
                    "solo 1person male, sitting naturally and upright on a modern wooden chair in a contemporary cafe lounge, perfectly centered in frame, "
                    "perfectly upright head posture with zero tilt, head held straight and level, "
                    "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, "
                    "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear focus across entire frame, visible fine skin pores and sharp fabric textures, "
                    "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, symmetrical upright head angle, "
                    "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into the camera lens at horizontal eye level, symmetrical eyes, natural relaxed eyelids, "
                    "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
                    "composed calm trustworthy civilian expression, ready to speak with authentic eye contact, "
                    "an exceptionally handsome and charming 33-year-old Korean male professional (top-tier Korean drama male lead actor look, striking youthful attractive look in his early 30s), "
                    "strictly no glasses, bare clean face with clear smooth healthy skin, authentic handsome Korean male facial features, sharp masculine chiseled jawline, warm charismatic dark eyes, "
                    "stylish trendy Korean parted perm hairstyle (soft wavy side-parted comma hair with natural textured fringe, thick rich jet-black healthy hair, strictly ZERO grey hair, strictly NO white hair), "
                    "wearing a crisp tailored modern white oxford cotton shirt, sophisticated high-end Korean civilian smart casual look, "
                    "looking directly into camera lens with composed trustworthy closed-mouth expression (lips firmly closed together, strictly zero teeth showing), "
                    "modern K-drama handsome relatable lead look, "
                    "contemporary bright modern Scandinavian cafe lounge with warm wooden interior and soft natural daylight through window, tack sharp f/11 focus, "
                    "natural bright crisp daylight lighting, highly realistic 8k resolution, authentic Korean civilian documentary look, master quality"
                ),
                "negative_prompt": (
                    "ugly, average face, round face, chubby face, plain face, bloated, asymmetrical face, "
                    "extreme close-up, tight face shot, headshot portrait, cropped torso, cropped chest, cropped waist, big face, zoomed in face, "
                    "rolled back eyes, rolled eyes, upturned eyes, whites of eyes only, misaligned pupils, crossed eyes, strabismus, lazy eye, dilated pupils, deformed pupils, asymmetrical eyes, weird eyes, creepy eyes, blind eyes, blank stare, "
                    "cropped forehead, cropped head, head touching frame top, cut off head, "
                    "grey hair, white hair, greying temples, salt and pepper hair, elderly, old man, aged, wrinkled, sagging skin, old person, 50s, 60s, senior citizen, "
                    "old fashioned haircut, slicked back hair, middle part ahjussi hair, "
                    "puffy hair, frizzy hair, wide hair silhouette, mushroom hair, bird nest hair, frizzy curls, expanded hair, messy hair, overly curly hair, perm hair, unkempt hair, "
                    "arrogant pose, smug look, cocky smile, boastful expression, aggressive posture, awkward stiff pose, robotic posture, "
                    "showing teeth, open mouth, teeth, grinning, smiling with open mouth, smiling with teeth, parted lips, tooth, dental, toothy smile, big smile, mouth open, laughing with teeth, screaming, "
                    "glasses, spectacles, eyewear, sunglasses, rimless glasses, "
                    "chinese style, mainland chinese facial features, douyin aesthetic, heavy square jaw, broad flat nose, round wide face, "
                    "looking down, face obstructed, phone blocking face, phone covering mouth, "
                    "tilted head, sideways glance, looking away from camera, angled face, side profile, "
                    "heavy bokeh, blurry background, shallow depth of field, f/1.4 blur, cinematic bokeh blur, out of focus background, "
                    "distorted hands, extra fingers, deformed face, unnatural plastic skin, cartoon, anime, illustration, 3d render, watermark"
                )
            },
            {
                "page": 2,
                "badge": "📊 증권 정밀 팩트체크",
                "title": "매달 15만원 내는데 보장은 텅텅?\n지인 보험 증권에서 꼭 확인할 3가지",
                "subtitle": "거절하기 어려워 가입했던 종합보험, 불필요한 비용이 숨어있는지 확인해보세요.",
                "bullets": [
                    "불필요한 적립보험료: 만기 환급금 없이 사업비로 소진되는 적립금 비중 점검",
                    "3·5년 갱신형 특약: 나이가 들수록 보험료가 눈덩이처럼 인상되는 구조인지 확인",
                    "협소한 보장 범위: 뇌혈관·허혈성이 아닌 뇌출혈·급성심근경색 위주 설계인지 점검"
                ],
                "cta_button": "👉 다음 장: 0.1초 보장 자가진단 (2/5) >",
                "image_prompt": (
                    "masterpiece, best quality, ultra-photorealistic portrait, "
                    "photographed from 2.0 meters away on Apple iPhone 15 Pro, "
                    "clear medium waist-up shot showing head, upper torso in white shirt, arms holding an insurance policy paper document on cafe table, torso down to waistline, "
                    "subtle headroom occupying upper 5% of frame, "
                    "solo 1person male, the exact same exceptionally handsome and charming 33-year-old Korean male professional from slide 1 (top-tier Korean drama male lead actor look), "
                    "strictly no glasses, bare clean face with clear smooth healthy skin, authentic handsome Korean male facial features, sharp masculine chiseled jawline, "
                    "strictly clean-shaven, completely hairless smooth skin on chin and upper lip, strictly zero facial hair, strictly no beard, strictly no mustache, strictly no goatee, strictly no stubble, "
                    "the exact same stylish natural soft wavy side-parted comma hairstyle with textured fringe bangs covering part of forehead, thick rich jet-black healthy hair, strictly ZERO grey hair, strictly NO white hair, "
                    "wearing the exact same crisp tailored modern white oxford cotton shirt, sophisticated high-end Korean civilian smart casual look, "
                    "sitting at a Scandinavian wooden table in the contemporary cafe lounge, looking down at his old insurance policy document showing a realistic thoughtful and serious expression (약관을 진지하게 점검하는 표정), furrowed brow, lips firmly closed together, strictly zero open mouth, strictly no visible teeth, "
                    "soft natural daylight through cafe window, warm Scandinavian wooden cafe interior, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and fabric textures, vivid authentic Korean cafe realism"
                ),
                "negative_prompt": "ugly, average face, round face, chubby face, plain face, bloated, asymmetrical face, close-up, extreme close-up, cropped face, cropped head, zoomed-in face, female, woman, two people, crowd, open mouth, parted lips, visible teeth, showing teeth, laughing, smiling, happy, grinning, cartoon, anime, 3d render, illustration, deformed hands, extra fingers, blurry, low quality, glasses, suit, tie, jacket, beard, mustache, goatee, stubble, facial hair, whiskers, 5 o'clock shadow, slicked back, combed back, pompadour, forehead fully exposed all-back hair, undercut, bald, messy hair"
            },
            {
                "page": 3,
                "badge": "💡 0.1초 안심 자가진단",
                "title": "전화번호 없이 생년월일만 체크!\n종합건강 보장 구조 0.1초 즉시 계산",
                "subtitle": "이름·전화번호 일체 수집 없는 100% PII-Free 익명 진단",
                "bullets": [
                    "생년월일(19821003)과 남성 선택 시 0.1초 즉시 계산",
                    "일반암 3,000만·유사암 600만 맞춤형 원클릭 세팅",
                    "스팸 영업 전화 0건: 연락처 수집 없는 완벽한 익명 진단"
                ],
                "cta_button": "👉 다음 장: 34개 보험사 최저가 순위표 보기 (3/5) >",
                "use_direct_asset": True,
                "asset_image": "brands/insurance/assets/acquaintance_slide3_condition.png"
            },
            {
                "page": 4,
                "badge": "📊 대한민국 34개사 전수 공개",
                "title": "스팸 전화 0건! 34개 보험사\n종합건강 최저가 39,700원 실시간 순위표",
                "subtitle": "특정사 편파 추천 없이 금융감독원 공시 기준 실제 가격을 실시간 공개합니다.",
                "bullets": [
                    "동일 종합보장 기준 최저가 1위(39,700원) 투명 공개",
                    "스팸 영업 전화 0건: 조회 즉시 빗발치는 가입 권유 전화 원천 차단",
                    "금융위원회/금융감독원 공시 요율에 기반한 투명한 정보 제공"
                ],
                "cta_button": "👉 다음 장: 합리적 관리 방법 확인하기 (4/5) >",
                "use_direct_asset": True,
                "asset_image": "brands/insurance/assets/acquaintance_slide4_result.png"
            },
            {
                "page": 5,
                "badge": "찬반 토론 & 1분 진단 CTA",
                "title": "지인 권유 보험, 그대로 유지 vs 불필요 특약 부분 삭제?",
                "subtitle": "개인정보 입력 없이 1분 만에 내 증권의 객관적인 보장 상태를 확인해보세요",
                "bullets": [
                    "전화번호 입력 없이 34개 보험사 객관적 보장 비교",
                    "좋은 특약은 유지하고 불필요한 적립보험료만 골라서 정리",
                    "👉 지금 네이버 검색창에 '보험 리밸런스'를 검색해보세요!"
                ],
                "cta_button": "👉 네이버에 '보험 리밸런스' 검색하기 >",
                "debate_badge": "⚡ 지인 보험 현실 토론",
                "debate_question": "지인에게 가입한 보험, 원형 그대로 유지 vs 불필요 특약만 부분 삭제?",
                "debate_opt1_title": "✂️ 불필요 특약만 부분 삭제",
                "debate_opt1_sub": "좋은 주계약은 살리고 적립금·갱신형만 골라 다이어트",
                "debate_opt1_rate": "89% (대세)",
                "debate_opt2_title": "🛡️ 기존 계약 그대로 유지",
                "debate_opt2_sub": "보장 내용 변경 없이 만기까지 현 상태 유지",
                "debate_opt2_rate": "11%",
                "benefit_items": [
                    "34개 보험사 동일 보장 실시간 최저가 비교",
                    "이름·전화번호 입력 제로 (PII-Free 안심 구조)",
                    "0.1초 만에 불필요 적립금 & 중복 특약 자가진단"
                ],
                "cta_subtext": "✨ 스팸 전화 0건 • 지금 조회하고 내 증권 객관적 보장 분석하기"
            }
        ]
    },
    6: {
        "topic_id": 6,
        "theme_code": "child_to_adult",
        "theme_name": "어린이·어른이 100세 만기 리모델링",
        "official_keyword": "보험 리밸런스",
        "slides": [
            {
                "page": 1,
                "badge": "👶 어른이 보험 팩트체크",
                "title": "어릴 때 부모님이 들어준 100세 보험\n성인이 된 지금 보장 범위 충분할까요?",
                "subtitle": "소아 특약은 줄이고 성인 3대 질환을 비갱신형으로 알뜰하게 리모델링하세요.",
                "bullets": [
                    "소아 전용 특약(골절·스쿨존 등) 만기 및 불필요 담보 점검",
                    "성인 3대 질환(암·뇌혈관·허혈성) 진단비 보장 공백 확인",
                    "34개 보험사 비갱신형 어른이 플랜 실시간 1초 비교"
                ],
                "cta_button": "👉 어른이 보험 리모델링 팩트 보기 (1/5) >",
                "image_prompt": (
                    "photographed from 1.4 meters directly in front on Apple iPhone 15 Pro, "
                    "clear medium bust shot, showing head, elegant neck, natural shoulders, chest, and upper torso, "
                    "solo 1person female, sitting upright on a stylish modern lounge sofa, perfectly centered in frame, "
                    "perfectly upright head posture with zero tilt, subtle headroom occupying upper 5% of frame, "
                    "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, "
                    "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and sharp clothing fabric textures, "
                    "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, symmetrical upright head angle, "
                    "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into the camera lens at horizontal eye level, symmetrical eyes, natural relaxed eyelids, "
                    "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
                    "composed calm trustworthy civilian expression, ready to speak with authentic eye contact, "
                    "a gorgeous and charming 30-year-old Korean young woman, perfect 8-head-high golden ratio tall fit model proportions, "
                    "strictly no glasses, bare clean face with clear glowing fair skin, authentic beautiful Korean female facial features, attractive gentle brown eyes, "
                    "neat and stylish natural soft wavy hairstyle, "
                    "wearing a stylish, neat, and chic modern Korean smart-casual daily outfit, clean contemporary civilian fashion, "
                    "looking directly into camera lens with composed gentle closed-mouth expression (lips firmly closed together, strictly zero teeth showing), "
                    "modern K-drama relatable civilian look, "
                    "bright modern Scandinavian sunlit apartment living room with cozy wooden interior and lush indoor green plants, "
                    "warm soft natural morning window daylight streaming in, casting realistic gentle shadows, "
                    "crystal clear edge-to-edge deep focus across the entire living room, vivid authentic Korean indoor realism, zero yellow tint, "
                    "natural bright crisp daylight lighting, highly realistic 8k resolution, authentic Korean civilian documentary look, master quality"
                ),
                "negative_prompt": (
                    "extreme close-up, tight face shot, headshot portrait, cropped torso, cropped chest, cropped waist, big face, zoomed in face, "
                    "rolled back eyes, rolled eyes, upturned eyes, whites of eyes only, misaligned pupils, crossed eyes, strabismus, lazy eye, dilated pupils, deformed pupils, asymmetrical eyes, weird eyes, creepy eyes, blind eyes, blank stare, "
                    "cropped forehead, cropped head, head touching frame top, cut off head, "
                    "grey hair, white hair, greying temples, salt and pepper hair, elderly, old man, aged, wrinkled, sagging skin, old person, 50s, 60s, senior citizen, "
                    "old fashioned haircut, slicked back hair, middle part ahjussi hair, "
                    "puffy hair, frizzy hair, wide hair silhouette, mushroom hair, bird nest hair, frizzy curls, expanded hair, messy hair, overly curly hair, perm hair, unkempt hair, "
                    "arrogant pose, smug look, cocky smile, boastful expression, aggressive posture, awkward stiff pose, robotic posture, "
                    "showing teeth, open mouth, teeth, grinning, smiling with open mouth, smiling with teeth, parted lips, tooth, dental, toothy smile, big smile, mouth open, laughing with teeth, screaming, "
                    "glasses, spectacles, eyewear, sunglasses, rimless glasses, "
                    "chinese style, mainland chinese facial features, douyin aesthetic, heavy square jaw, broad flat nose, round wide face, "
                    "looking down, face obstructed, phone blocking face, phone covering mouth, "
                    "tilted head, sideways glance, looking away from camera, angled face, side profile, "
                    "heavy bokeh, blurry background, shallow depth of field, f/1.4 blur, cinematic bokeh blur, out of focus background, "
                    "distorted hands, extra fingers, deformed face, unnatural plastic skin, cartoon, anime, illustration, 3d render, watermark"
                )
            },
            {
                "page": 2,
                "badge": "💻 스마트 증권 정밀 분석",
                "title": "어릴 때 든 100세 보험 그대로 두면?\n성인 3대 질환 진단비가 턱없이 부족합니다",
                "subtitle": "입원일당·소아 골절 대신 암·뇌혈관·심장 집중 보장으로 비갱신 다이어트",
                "bullets": [
                    "과거 가입된 100세 보험: 소아 특약 비중이 높아 성인 주요 질환 한도 부족",
                    "30세 이전 '어른이 플랜': 일반 성인보험 대비 넓은 보장 범위와 저렴한 보험료",
                    "무해지·비갱신 리밸런스: 기존 좋은 주계약은 살리고 불필요 특약만 골라 알뜰 정리"
                ],
                "cta_button": "👉 다음 장: 100세 전환 체크리스트 (2/5) >",
                "image_prompt": (
                    "masterpiece, best quality, ultra-photorealistic portrait, "
                    "photographed from 2.5 meters away on Apple iPhone 15 Pro, "
                    "clear medium waist-up shot showing head, upper torso, arms working on a slim laptop and tablet on modern wooden desk, torso down to waistline, "
                    "subtle headroom occupying upper 5% of frame, "
                    "solo 1person female, the exact same gorgeous and charming 30-year-old Korean young woman from slide 1, "
                    "perfect 8-head-high golden ratio tall fit model proportions, "
                    "strictly no glasses, bare clean face with clear glowing fair skin, authentic beautiful Korean female facial features, attractive gentle brown eyes, "
                    "the exact same neat and stylish natural soft wavy hairstyle, "
                    "wearing the exact same stylish, neat, and chic modern Korean smart-casual daily outfit, "
                    "seated at a clean minimalist wooden home office desk, looking at the tablet and laptop screen with a smart, focused, and attentive expression (노트북 화면의 보장 분석을 진지하게 점검하는 표정), lips firmly closed together, strictly zero open mouth, strictly no visible teeth, "
                    "bright crisp natural morning window daylight streaming into a stylish modern Korean home study room with minimalist bookshelf and green indoor plant, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and fabric textures, vivid authentic Korean home realism"
                ),
                "negative_prompt": (
                    "extreme close-up, tight face shot, headshot portrait, cropped torso, cropped chest, cropped waist, big face, zoomed in face, "
                    "ugly, average face, round face, chubby face, plain face, bloated, asymmetrical face, male, man, two people, crowd, "
                    "open mouth, parted lips, visible teeth, showing teeth, laughing, smiling, happy, grinning, "
                    "cartoon, anime, 3d render, illustration, deformed hands, extra fingers, blurry, low quality, glasses"
                )
            },
            {
                "page": 3,
                "badge": "💡 0.1초 안심 자가진단",
                "title": "전화번호 없이 생년월일만 체크!\n어른이 3대 진단비 0.1초 즉시 계산",
                "subtitle": "소아 특약 다이어트 + 성인 3대 진단비(암·뇌·심) 비갱신형 최적화 설계",
                "bullets": [
                    "생년월일(19960515)과 성별 선택 시 0.1초 즉시 계산",
                    "암 5천·뇌혈관 2천·허혈성 2천만원 맞춤형 원클릭 세팅",
                    "스팸 영업 전화 0건: 연락처 수집 없는 완벽한 익명 진단"
                ],
                "cta_button": "👉 다음 장: 34개사 어른이 보험 순위표 보기 (3/5) >",
                "use_direct_asset": True,
                "asset_image": "brands/insurance/assets/slide3_silbi_condition.png"
            },
            {
                "page": 4,
                "badge": "📊 대한민국 34개사 전수 공개",
                "title": "스팸 전화 0건! 34개 보험사\n어른이 비갱신 최저가 34,200원 순위표",
                "subtitle": "특정사 편파 추천 없이 금융감독원 공시 기준 실제 가격을 실시간 공개합니다.",
                "bullets": [
                    "동일 보장 기준 최저가 1위(34,200원) 투명 공개",
                    "스팸 영업 전화 0건: 조회 즉시 빗발치는 가입 권유 전화 원천 차단",
                    "금융감독원 공시 연동: 34개사 실제 요율을 0.1초 만에 최저가 순위 정렬"
                ],
                "cta_button": "👉 다음 장: 합리적 리모델링 팁 확인하기 (4/5) >",
                "use_direct_asset": True,
                "asset_image": "brands/insurance/assets/slide4_silbi_result.png"
            },
            {
                "page": 5,
                "badge": "찬반 토론 & 1분 진단 CTA",
                "title": "어릴 때 든 100세 보험, 그대로 유지 vs 비갱신형 어른이 리모델링?",
                "subtitle": "개인정보 입력 없이 1분 만에 내 증권의 객관적인 보장 상태를 확인해보세요",
                "bullets": [
                    "전화번호 입력 없이 34개 보험사 객관적 보장 비교",
                    "소아 특약은 줄이고 성인 3대 질환을 비갱신형으로 알뜰 보강",
                    "👉 지금 네이버 검색창에 '보험 리밸런스'를 검색해보세요!"
                ],
                "cta_button": "👉 네이버에 '보험 리밸런스' 검색하기 >",
                "debate_badge": "⚡ 어른이 보험 현실 토론",
                "debate_question": "어릴 때 부모님이 들어준 100세 보험, 원형 그대로 유지 vs 성인 보장으로 리모델링?",
                "debate_opt1_title": "✂️ 어른이 비갱신 리모델링",
                "debate_opt1_sub": "소아 특약 빼고 암·뇌·심 3대 질환을 비갱신으로 집중 보강",
                "debate_opt1_rate": "87% (대세)",
                "debate_opt2_title": "🛡️ 기존 100세 보험 유지",
                "debate_opt2_sub": "보장 내용 변경 없이 만기까지 현 상태 유지",
                "debate_opt2_rate": "13%",
                "benefit_items": [
                    "34개 보험사 어른이 플랜 실시간 최저가 비교",
                    "이름·전화번호 입력 제로 (PII-Free 안심 구조)",
                    "0.1초 만에 불필요 소아 특약 & 3대 진단비 자가진단"
                ],
                "cta_subtext": "✨ 스팸 전화 0건 • 지금 조회하고 내 증권 객관적 보장 분석하기"
            }
        ]
    },
    7: {
        "topic_id": 7,
        "theme_code": "duplicate_coverage_diet",
        "theme_name": "내 보험 정밀 비교 & 새는 보험료 다이어트",
        "official_keyword": "보험 리밸런스",
        "slides": [
            {
                "page": 1,
                "badge": "💰 증권 정밀 점검",
                "title": "여러 개 가입해도 1곳에서만 나오는\n'비례보상 특약' 점검하기",
                "subtitle": "실손의료비·운전자 벌금·배상책임 등 비례보상 약관의 실제 원리",
                "bullets": [
                    "중복 가입 시 실제 손해액만 분할 지급되는 비례보상 특약 구조",
                    "중복 지급(진단비/수술비) vs 비례 지급(실손/벌금) 완벽 구분",
                    "34개 보험사 통합 전산 기준 중복 특약 점검 방법"
                ],
                "cta_button": "👉 내 중복 특약 점검하기 (1/5) >",
                "image_prompt": (
                    "photographed from 2.0 meters away on Apple iPhone 15 Pro, "
                    "clear medium waist-up shot showing head, elegant neck, natural shoulders, chest, and torso down to waistline, "
                    "solo 1person female, standing upright with natural elegant posture in a modern Scandinavian living room, "
                    "subtle headroom occupying upper 5% of frame, "
                    "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, "
                    "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and sharp clothing fabric textures, "
                    "composed calm trustworthy civilian expression, ready to speak with authentic eye contact, "
                    "a poised and intelligent 37-year-old Korean woman (smart professional and homemaker), perfect 8-head-high golden ratio tall fit model proportions, "
                    "strictly no glasses, bare clean face with clear glowing fair skin, authentic beautiful Korean female facial features, attractive articulate eyes, "
                    "neat and stylish natural dark brown shoulder-length wavy hairstyle, "
                    "wearing a stylish, neat, and chic modern Korean smart-casual daily outfit, clean contemporary civilian fashion, "
                    "looking directly into camera lens with composed gentle closed-mouth expression (lips firmly closed together, strictly zero teeth showing), "
                    "modern K-drama relatable civilian look, "
                    "bright modern Scandinavian sunlit apartment living room with cozy wooden interior and lush indoor green plants, "
                    "warm soft natural morning window daylight streaming in, casting realistic gentle shadows, "
                    "crystal clear edge-to-edge deep focus across the entire living room, vivid authentic Korean indoor realism, zero yellow tint, "
                    "natural bright crisp daylight lighting, highly realistic 8k resolution, authentic Korean civilian documentary look, master quality"
                ),
                "negative_prompt": (
                    "extreme close-up, tight face shot, headshot portrait, cropped torso, cropped chest, cropped waist, big face, zoomed in face, "
                    "rolled back eyes, rolled eyes, upturned eyes, whites of eyes only, misaligned pupils, crossed eyes, strabismus, lazy eye, dilated pupils, deformed pupils, asymmetrical eyes, weird eyes, creepy eyes, blind eyes, blank stare, "
                    "cropped forehead, cut off head, "
                    "grey hair, white hair, greying temples, salt and pepper hair, elderly, old man, aged, wrinkled, sagging skin, old person, 50s, 60s, senior citizen, "
                    "old fashioned haircut, slicked back hair, middle part ahjussi hair, "
                    "puffy hair, frizzy hair, wide hair silhouette, mushroom hair, bird nest hair, frizzy curls, expanded hair, messy hair, overly curly hair, perm hair, unkempt hair, "
                    "arrogant pose, smug look, cocky smile, boastful expression, aggressive posture, awkward stiff pose, robotic posture, "
                    "showing teeth, open mouth, teeth, grinning, smiling with open mouth, smiling with teeth, parted lips, tooth, dental, toothy smile, big smile, mouth open, laughing with teeth, screaming, "
                    "glasses, spectacles, eyewear, sunglasses, rimless glasses, "
                    "chinese style, mainland chinese facial features, douyin aesthetic, heavy square jaw, broad flat nose, round wide face, "
                    "looking down, face obstructed, phone blocking face, phone covering mouth, "
                    "tilted head, sideways glance, looking away from camera, angled face, side profile, "
                    "heavy bokeh, blurry background, shallow depth of field, f/1.4 blur, cinematic bokeh blur, out of focus background, "
                    "distorted hands, extra fingers, deformed face, unnatural plastic skin, cartoon, anime, illustration, 3d render, watermark"
                )
            },
            {
                "page": 2,
                "badge": "🚨 이중 납입 팩트체크",
                "title": "매달 2곳에 꼬박꼬박 냈는데…\n보상은 딱 1곳에서만 나온다고요?",
                "subtitle": "실손의료비·운전자 벌금 등 중복 가입해도 실제 발생 비용 한도 내 분할 지급됩니다",
                "bullets": [
                    "실손의료비 이중 가입 낭비: 보험료는 2곳에 내도 보장은 실제 병원비 내 분할",
                    "운전자 벌금 비례보상 원리: 여러 개 가입해도 법원 확정 판결 금액 내 분할",
                    "불필요 중복 특약 삭제: 중복 비례특약만 정리해도 매달 5~10만원 즉시 절감"
                ],
                "cta_button": "👉 다음 장: 중복 특약 정리 솔루션 (2/5) >",
                "image_prompt": (
                    "masterpiece, best quality, ultra-photorealistic portrait, "
                    "photographed from 2.5 meters away on Apple iPhone 15 Pro, "
                    "clear medium waist-up shot showing head, upper torso, arms holding a smartphone while seated on modern living room sofa, torso down to waistline, "
                    "subtle headroom occupying upper 5% of frame, "
                    "solo 1person female, the exact same poised and intelligent 37-year-old Korean woman from slide 1, "
                    "perfect 8-head-high golden ratio tall fit model proportions, "
                    "strictly no glasses, bare clean face with clear glowing fair skin, authentic beautiful Korean female facial features, attractive articulate eyes, "
                    "the exact same neat and stylish natural dark brown shoulder-length wavy hairstyle, "
                    "wearing the exact same stylish, neat, and chic modern Korean smart-casual daily outfit, "
                    "seated comfortably on the neutral fabric living room sofa, looking at her smartphone displaying monthly banking payment notifications with a realistic surprised and thoughtful expression (자동이체 내역을 보며 아차 싶어 진지하게 점검하는 표정), lips firmly closed together, strictly zero open mouth, strictly no visible teeth, "
                    "warm soft natural morning window daylight streaming in, Scandinavian apartment living room background with lush indoor plants, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and fabric textures, vivid authentic Korean home realism"
                ),
                "negative_prompt": (
                    "extreme close-up, tight face shot, headshot portrait, cropped torso, cropped chest, cropped waist, big face, zoomed in face, "
                    "ugly, average face, round face, chubby face, plain face, bloated, asymmetrical face, male, man, two people, crowd, "
                    "open mouth, parted lips, visible teeth, showing teeth, laughing, smiling, happy, grinning, "
                    "cartoon, anime, 3d render, illustration, deformed hands, extra fingers, blurry, low quality, glasses"
                )
            },
            {
                "page": 3,
                "badge": "💡 0.1초 안심 자가진단",
                "title": "전화번호 없이 생년월일만 체크!\n수술·암·종합 3종 리밸런싱 진단",
                "subtitle": "수술/입원 + 암보험 + 종합건강 3개 보장 맞춤형 원클릭 선택",
                "bullets": [
                    "생년월일과 성별 선택 시 0.1초 즉시 계산",
                    "수술·입원 반복지급 + 암 진단비 1억 + 종합건강 빈틈없는 조립",
                    "스팸 영업 전화 0건: 연락처 수집 없는 완벽한 익명 진단"
                ],
                "cta_button": "👉 다음 장: 3개 보험 동시 리밸런싱 결과표 보기 (3/5) >",
                "use_direct_asset": True,
                "asset_image": "brands/insurance/assets/diet_slide3_condition.png"
            },
            {
                "page": 4,
                "badge": "📊 3개 보험 동시 리밸런싱",
                "title": "월 150,000원 ➔ 117,750원!\n보장은 그대로, 매달 -32,250원 다이어트",
                "subtitle": "암진단 4.2만 + 수술입원 1.9만 + 종합건강 3.8만원 실시간 비교",
                "bullets": [
                    "기존 15만원 ➔ 3개 전체 리밸런싱 시 매달 32,250원 절약",
                    "스팸 영업 전화 0건: 조회 즉시 빗발치는 가입 권유 전화 원천 차단",
                    "금융감독원 공시 연동: L생보·E손보·P생보 최저가 조합 실시간 산출"
                ],
                "cta_button": "👉 다음 장: 합리적 다이어트 방법 확인하기 (4/5) >",
                "use_direct_asset": True,
                "asset_image": "brands/insurance/assets/diet_slide4_result.png"
            },
            {
                "page": 5,
                "badge": "환급 & 다이어트 CTA",
                "title": "중복된 비례보상 특약, 부분 삭제 vs 종합 리모델링?",
                "subtitle": "개인정보 입력 없이 1분 만에 내 증권의 중복 특약 상태를 확인해보세요",
                "bullets": [
                    "34개 보험사 동일 보장 실시간 객관적 비교",
                    "전화 영업 0건 • 100% 안전 비대면 스마트 분석",
                    "👉 지금 네이버 검색창에 '보험 리밸런스'를 검색해보세요!"
                ],
                "cta_button": "👉 네이버에 '보험 리밸런스' 검색하기 >",
                "debate_badge": "⚡ 중복 특약 현실 토론",
                "debate_question": "중복된 비례보상 특약, 해당 특약만 부분 삭제 vs 최신 다이렉트 종합 리모델링?",
                "debate_opt1_title": "✂️ 중복 특약만 부분 삭제",
                "debate_opt1_sub": "기존 주계약 유지하고 중복된 운전자/배상책임만 쏙 빼기",
                "debate_opt1_rate": "74% (대세)",
                "debate_opt2_title": "🔄 최신 다이렉트 종합 재설계",
                "debate_opt2_sub": "군더더기 없는 최신 다이렉트 상품으로 깔끔하게 통합",
                "debate_opt2_rate": "26%",
                "benefit_items": [
                    "34개 보험사 실시간 객관적 비교",
                    "이름·전화번호 입력 제로 (PII-Free 안심 구조)",
                    "0.1초 만에 중복 비례보상 특약 자가진단"
                ],
                "cta_subtext": "✨ 스팸 전화 0건 • 지금 조회하고 내 증권 중복 특약 정밀 점검"
            }
        ]
    },
    8: {
        "topic_id": 8,
        "theme_code": "coverage_score_gap_diagnosis",
        "theme_name": "AI 보험료 역추정 비교 & 가성비 리모델링",
        "official_keyword": "보험 리밸런스",
        "slides": [
            {
                "page": 1,
                "badge": "🤖 AI 역추정 리모델링",
                "title": "매달 내는 보험료 역추정 분석!\n같은 가격에 보장 더 큰 보험 찾기",
                "subtitle": "내가 내는 보험료 금액을 기준으로 34개 보험사 상품을 0.1초 만에 비교합니다",
                "bullets": [
                    "동일 보험료 대비 3대 질병 진단비 및 수술비 최대 보장 역추정",
                    "불필요한 사업비·적립금 거품을 뺀 가성비 극대화 플랜",
                    "34개 전 보험사 다이렉트 공시 요율 실시간 1초 비교"
                ],
                "cta_button": "👉 AI 역추정 진단 팩트 보기 (1/5) >",
                "image_prompt": (
                    "photographed from 1.4 meters directly in front on Apple iPhone 15 Pro, "
                    "clear medium bust shot, showing head, elegant neck, natural shoulders, chest, and upper torso, "
                    "solo 1person female, sitting upright in a modern Scandinavian living room, perfectly centered in frame, "
                    "perfectly upright head posture with zero tilt, natural balanced headroom occupying upper 8% of frame, "
                    "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into camera lens at horizontal eye level, "
                    "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and sharp clothing fabric textures, "
                    "perfectly upright head posture, head held completely straight and level with zero tilt, strictly no head tilt, symmetrical upright head angle, "
                    "perfect centered dark irises and pupils, sharp crystal clear eye contact looking straight and directly into the camera lens at horizontal eye level, symmetrical eyes, natural relaxed eyelids, "
                    "gently and firmly closed mouth, natural lips completely closed together, mouth shut tight, strictly zero open mouth, strictly no parted lips, absolutely zero teeth showing, strictly no visible teeth, "
                    "composed calm trustworthy civilian expression, ready to speak with authentic eye contact, "
                    "a poised, elegant, and intelligent 39-year-old Korean woman (smart professional and homemaker), perfect 8-head-high golden ratio tall fit model proportions, "
                    "strictly no glasses, bare clean face with clear glowing healthy skin, authentic beautiful Korean female facial features, attractive reassuring brown eyes, "
                    "neat and stylish natural dark brown wavy hairstyle, "
                    "wearing a stylish, neat, and chic modern Korean smart-casual daily outfit, clean contemporary civilian fashion, "
                    "looking directly into camera lens with composed gentle closed-mouth expression (lips firmly closed together, strictly zero teeth showing), "
                    "modern K-drama relatable civilian look, "
                    "bright modern Scandinavian sunlit apartment living room with cozy wooden interior and lush indoor green plants, "
                    "warm soft natural morning window daylight streaming in, casting realistic gentle shadows, "
                    "crystal clear edge-to-edge deep focus across the entire living room, vivid authentic Korean indoor realism, zero yellow tint, "
                    "natural bright crisp daylight lighting, highly realistic 8k resolution, authentic Korean civilian documentary look, master quality"
                ),
                "negative_prompt": (
                    "extreme close-up, tight face shot, headshot portrait, cropped torso, cropped chest, cropped waist, big face, zoomed in face, "
                    "rolled back eyes, rolled eyes, upturned eyes, whites of eyes only, misaligned pupils, crossed eyes, strabismus, lazy eye, dilated pupils, deformed pupils, asymmetrical eyes, weird eyes, creepy eyes, blind eyes, blank stare, "
                    "cropped forehead, cropped head, head touching frame top, cut off head, "
                    "grey hair, white hair, greying temples, salt and pepper hair, elderly, old man, aged, wrinkled, sagging skin, old person, 50s, 60s, senior citizen, "
                    "old fashioned haircut, slicked back hair, middle part ahjussi hair, "
                    "puffy hair, frizzy hair, wide hair silhouette, mushroom hair, bird nest hair, frizzy curls, expanded hair, messy hair, overly curly hair, perm hair, unkempt hair, "
                    "arrogant pose, smug look, cocky smile, boastful expression, aggressive posture, awkward stiff pose, robotic posture, "
                    "showing teeth, open mouth, teeth, grinning, smiling with open mouth, smiling with teeth, parted lips, tooth, dental, toothy smile, big smile, mouth open, laughing with teeth, screaming, "
                    "glasses, spectacles, eyewear, sunglasses, rimless glasses, "
                    "chinese style, mainland chinese facial features, douyin aesthetic, heavy square jaw, broad flat nose, round wide face, "
                    "looking down, face obstructed, phone blocking face, phone covering mouth, "
                    "tilted head, sideways glance, looking away from camera, angled face, side profile, "
                    "heavy bokeh, blurry background, shallow depth of field, f/1.4 blur, cinematic bokeh blur, out of focus background, "
                    "distorted hands, extra fingers, deformed face, unnatural plastic skin, cartoon, anime, illustration, 3d render, watermark"
                )
            },
            {
                "page": 2,
                "badge": "📊 가성비 비교 팩트",
                "title": "동일한 10만원으로 가입 가능한\n34개사 보장 범위 격차",
                "subtitle": "회사별 손해율과 사업비 구조에 따라 동일 금액 대비 보장 한도가 최대 2배까지 차이 납니다",
                "bullets": [
                    "같은 10만원으로 일반암 3,000만 vs 6,000만 보장 차이 확인",
                    "뇌혈관·허혈성 진단비 포함 여부에 따른 가성비 격차 분석",
                    "34개 보험사 공시 데이터 기반 객관적 역추정 분석"
                ],
                "cta_button": "👉 AI 역추정 솔루션 (2/5) >",
                "image_prompt": (
                    "masterpiece, best quality, ultra-photorealistic portrait, "
                    "photographed from 2.0 meters away on Apple iPhone 15 Pro, "
                    "clear medium waist-up shot showing head, upper torso, arms holding a tablet PC showing policy comparison graph, torso down to waistline, "
                    "subtle headroom occupying upper 5% of frame, "
                    "solo 1person female, the exact same poised, elegant, and intelligent 39-year-old Korean woman from slide 1, "
                    "strictly no glasses, bare clean face with clear glowing healthy skin, authentic beautiful Korean female facial features, sharp elegant jawline, "
                    "neat and stylish natural dark brown wavy hairstyle, "
                    "wearing the exact same chic modern smart-casual daily outfit, "
                    "sitting at the Scandinavian living room table, looking at the tablet screen with a serious and attentive analytical expression (비교 그래프를 꼼꼼히 점검하는 표정), furrowed brow, lips firmly closed together, strictly zero open mouth, strictly no visible teeth, "
                    "bright morning natural window daylight, Scandinavian apartment living room background, "
                    "f/11 deep pan-focus, zero lens blur, tack sharp crystal clear edge-to-edge focus, visible fine skin pores and fabric textures"
                ),
                "negative_prompt": "ugly, average face, round face, chubby face, plain face, bloated, asymmetrical face, close-up, extreme close-up, cropped face, cropped head, zoomed-in face, male, man, two people, crowd, open mouth, parted lips, visible teeth, showing teeth, laughing, smiling, happy, grinning, cartoon, anime, 3d render, illustration, deformed hands, extra fingers, blurry, low quality, glasses"
            },
            {
                "page": 3,
                "badge": "💡 감액완납의 원리",
                "title": "'감액완납' 신청 시 추가 보험료 없이\n축소된 보장 만기까지 유지",
                "subtitle": "지금까지 적립된 해약환급금으로 남은 기간의 보험료를 일시불 정산 처리하는 원리",
                "bullets": [
                    "보장 금액은 비율에 따라 일부 축소되지만, 보장 기간은 만기까지 유지",
                    "신청 다음 달부터 추가 보험료 납입 의무 완전 면제",
                    "해약에 따른 일시적 손실을 막고 기존 질병 보장 방어막 사수"
                ],
                "cta_button": "👉 감액완납 가능 여부 확인 (3/5) >",
                "use_direct_asset": True,
                "asset_image": "brands/insurance/assets/slide3_silbi_condition.png"
            },
            {
                "page": 4,
                "badge": "📊 3대 합법 유지 제도",
                "title": "보험료 부담을 줄이는 3대 제도:\n감액완납 / 특약 부분삭제 / 납입유예",
                "subtitle": "가계 경제 상황에 맞추어 해지 없이 보장을 지키는 실전 제도",
                "bullets": [
                    "1. 감액완납: 보험료 추가 납입 중단 + 조정된 보장 평생 유지",
                    "2. 특약 부분삭제: 불필요한 특약만 골라 삭제하여 월 납입료 경감",
                    "3. 납입유예/감액: 일시적 소득 공백 시 일정 기간 납입 정지"
                ],
                "cta_button": "👉 내 보험 최적 대안 찾기 (4/5) >",
                "use_direct_asset": True,
                "asset_image": "brands/insurance/assets/slide4_silbi_result.png"
            },
            {
                "page": 5,
                "badge": "방어 & 진단 CTA",
                "title": "부담스러운 보험, 해지 버튼 누르기 전에\n먼저 객관적 유지가능 여부를 진단받으세요",
                "subtitle": "내 증권으로 감액완납 시 예상 보장 금액과 절약 효과를 1분 만에 시뮬레이션",
                "bullets": [
                    "해약 손실 없이 내 합법적 계약 권리를 지키는 스마트 리밸런스",
                    "34개 보험사 객관적 시뮬레이션 결과 비대면 확인",
                    "👉 지금 네이버 검색창에 '보험 리밸런스'를 검색해보세요!"
                ],
                "cta_button": "👉 네이버에 '보험 리밸런스' 검색하기 >",
                "debate_badge": "⚡ 보험 유지 현실 토론",
                "debate_question": "보험료가 부담될 때, 전체 해지 후 신규 가입 vs 감액완납/특약삭제로 핵심 보장 유지?",
                "debate_opt1_title": "🛡️ 감액완납/특약삭제로 유지",
                "debate_opt1_sub": "해약 손실 없이 기존 핵심 보장과 병력 불이익 방어",
                "debate_opt1_rate": "86% (대세)",
                "debate_opt2_title": "🔄 전체 해지 후 신규 가입",
                "debate_opt2_sub": "해지환급금 수령 후 최신 다이렉트 상품으로 신규 재가입",
                "debate_opt2_rate": "14%",
                "benefit_items": [
                    "34개 보험사 객관적 시뮬레이션 비교",
                    "이름·전화번호 입력 제로 (PII-Free 안심 구조)",
                    "0.1초 만에 감액완납 & 특약 부분삭제 가능 여부 자가진단"
                ],
                "cta_subtext": "✨ 스팸 전화 0건 • 지금 조회하고 내 증권 안전하게 지키기"
            }
        ]
    }
}


class InsuranceCardnewsScenarioDirector:
    """🛡️ 보험 리밸런스 8대 정예 주제 5장 카드뉴스 시나리오 총괄 디렉터"""

    def __init__(self):
        self.scenarios = copy.deepcopy(INSURANCE_8_CARDNEWS_SCENARIOS)

    def get_scenario(self, topic_id: int = 1) -> Dict[str, Any]:
        """주제 번호에 따른 5장 완결 시나리오 반환"""
        if topic_id not in self.scenarios:
            topic_id = 1
        return copy.deepcopy(self.scenarios[topic_id])

    def get_all_scenarios(self) -> Dict[int, Dict[str, Any]]:
        """전체 8개 주제 시나리오 맵 반환"""
        return copy.deepcopy(self.scenarios)

    def list_topic_summary(self) -> List[Dict[str, Any]]:
        """8대 주제 요약 목록 반환 (대시보드/스케줄러 연동)"""
        summaries = []
        for tid, s in sorted(self.scenarios.items()):
            summaries.append({
                "topic_id": tid,
                "theme_code": s.get("theme_code"),
                "theme_name": s.get("theme_name"),
                "cover_title": s["slides"][0]["title"] if s.get("slides") else "",
                "official_keyword": s.get("official_keyword", "보험 리밸런스")
            })
        return summaries
