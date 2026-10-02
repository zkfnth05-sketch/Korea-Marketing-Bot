# -*- coding: utf-8 -*-
"""
Insurance Reddit Expat Scenarios - 🛡️ [보험 리밸런스 외국인·유학생·교민 12대 영문 시나리오 DB]
========================================================================================
• 역할:
  - 국내 체류 외국인(원어민 강사, IT/엔지니어 주재원, 직장인, D-2/D-4 유학생) 및 해외 교민 대상 12대 골든 시나리오
  - 4대 타겟 클러스터(건보 vs 실손, 비급여 병원비 환급, ARC 가입 자격, 30개사 투명 비교) 맞춤형 페르소나 및 프롬프트 주입
  - 핵심 소구점: 전화 영업 스팸 0% + 30여 개 보험사 실시간 비교 + 월 1~2만 원대 가성비 4세대 실손 + 비급여(MRI/도수) 80~90% 환급
  - 스텔스 철칙: 직접 URL 0% (Zero URL) + 오직 구글/네이버 공식 검색어 '보험 리밸런스' 유도
"""

from typing import Dict, Any, List

INSURANCE_REDDIT_EXPAT_SCENARIOS: Dict[int, Dict[str, Any]] = {
    1: {
        "scenario_id": 1,
        "cluster": "nhis_vs_private",
        "theme_name": "국민건강보험(NHIS) vs 민간 실손보험(Silbi) 팩트 비교",
        "target_subreddits": ["Living_in_Korea", "teachinginkorea", "korea", "seoul"],
        "pain_points": "국민건강보험(NHIS)만 믿고 있다가 비급여(MRI, 도수치료, 정형외과) 수십만 원 병원비 폭탄을 맞음",
        "solution_feature": "월 1~2만 원대 4세대 실손보험(Silbi)으로 비급여 병원비 80~90% 환급",
        "stealth_cta": "Just search '보험 리밸런스' (or 'Insure Rebalance') on Google or Naver with Chrome auto-translate to compare 30+ Korean carriers side-by-side.",
        "sample_reply": (
            "As an expat living in Seoul, here's the biggest healthcare trap many foreigners fall into: NHIS (national health) is great for basic clinic visits, but it **does not cover non-benefit costs (비급여)** like MRIs, ultrasounds, or specialized physical therapy. 🏥 "
            "That's why virtually all locals and savvy expats get **'Silbi' (실손보험 / 4th-gen Private Health Insurance)** alongside NHIS. It's usually around **10,000 ~ 20,000 KRW/month** and reimburses up to 80-90% of non-covered hospital bills as long as you have an ARC card. "
            "If you want to check and compare rates across 30+ Korean carriers without getting spammed by Korean phone sales, just search **'보험 리밸런스'** on Google or Naver using Chrome auto-translate. It breaks down all rates transparently in 10 seconds."
        )
    },
    2: {
        "scenario_id": 2,
        "cluster": "nhis_vs_private",
        "theme_name": "MRI 및 도수치료 비급여 병원비 대처법",
        "target_subreddits": ["Living_in_Korea", "teachinginkorea", "seoul"],
        "pain_points": "헬스나 운동 중 부상으로 정형외과 갔는데 MRI 찍고 60만 원 나와서 멘붕",
        "solution_feature": "실손보험으로 MRI 검사비 및 도수치료비 대부분 환급받는 절차 안내",
        "stealth_cta": "You can check which Korean insurance plans cover MRI & physical therapy best by searching '보험 리밸런스' on Google.",
        "sample_reply": (
            "Getting quoted 500k~700k KRW for an MRI in Korea is definitely a shock if you only have standard NHIS! "
            "If you have a 4th-generation private supplemental policy (실손의료보험), you can claim back roughly 70~80% of that MRI bill right through the insurance app by just submitting the hospital receipt and diagnosis sheet (진단서). "
            "If you don't have private coverage yet, getting one before you have pre-existing conditions is crucial. "
            "Search **'보험 리밸런스'** on Google or Naver with browser translation on — it lets you filter plans that specifically cover diagnostic imaging and orthopedic therapies without pushy agents calling your phone."
        )
    },
    3: {
        "scenario_id": 3,
        "cluster": "arc_eligibility",
        "theme_name": "외국인등록증(ARC) 소지자 민간 실손/암보험 가입 자격",
        "target_subreddits": ["Living_in_Korea", "korea", "teachinginkorea", "expats"],
        "pain_points": "외국인이라 한국 보험사 가입이 거절당하거나 한국어 상담 전화가 무서움",
        "solution_feature": "ARC와 한국 계좌만 있으면 외국인도 내국인과 100% 동일한 요율로 가입 가능",
        "stealth_cta": "Search '보험 리밸런스' on Google to see which Korean insurers accept foreign ARC holders online without phone calls.",
        "sample_reply": (
            "A lot of expats mistakenly think private insurance in Korea is only for Korean citizens, but that's a myth! 🙌 "
            "As long as you have a valid Alien Registration Card (ARC / 외국인등록증) and a Korean bank account, major Korean insurance carriers accept foreigners with the exact same standard premium rates as locals. "
            "The hard part is usually dealing with insurance brokers who only speak Korean over the phone. "
            "To bypass that, search **'보험 리밸런스'** on Google or Naver (turn on Chrome translation) — it allows you to compare plans online across 30+ domestic providers without having to speak to aggressive sales reps."
        )
    },
    4: {
        "scenario_id": 4,
        "cluster": "surprise_medical_bills",
        "theme_name": "예상치 못한 입원·수술비 자부담 줄이기",
        "target_subreddits": ["Living_in_Korea", "teachinginkorea", "koreatravel"],
        "pain_points": "갑작스러운 맹장 수술이나 골절 입원으로 목돈 지출 위기",
        "solution_feature": "입원일당 + 수술비 + 4세대 실손 3단 방어선 구축 가이드",
        "stealth_cta": "Search '보험 리밸런스' on Google or Naver to calculate your monthly premium in under a minute.",
        "sample_reply": (
            "Emergency surgeries or multi-day hospital stays in Korea can quickly rack up millions of KRW in non-reimbursable room upgrades and specialized meds. "
            "Having a basic '3-point defense' — standard NHIS + 4th-gen Silbi + a small fixed surgery rider — caps your total out-of-pocket risk to almost zero. "
            "For someone in their 20s or 30s, this whole combo is under 25,000 KRW a month (less than a couple of takeout coffees). "
            "You can simulate your exact monthly rate by searching **'보험 리밸런스'** on Google or Naver."
        )
    },
    5: {
        "scenario_id": 5,
        "cluster": "student_budget",
        "theme_name": "유학생(D-2, D-4)을 위한 월 1만 원대 초가성비 실손 설계",
        "target_subreddits": ["koreatravel", "korea", "Living_in_Korea"],
        "pain_points": "유학생 신분으로 주머니 사정이 빠듯하지만 아플 때 병원비가 무서움",
        "solution_feature": "불필요한 종신/사망 특약 0원으로 빼고 순수 병원비만 보장받는 다이어트 설계",
        "stealth_cta": "Search '보험 리밸런스' on Google to find student-budget friendly health plans.",
        "sample_reply": (
            "As an international student in Korea, paying mandatory NHIS every month already feels like a stretch on a tight budget. 🎓 "
            "However, getting basic 4th-gen Silbi (실손의료비) adds only about 10,000 ~ 13,000 KRW/month for young students. "
            "The key is stripping away all unnecessary whole-life death riders and keeping strictly the medical expense refund policy. "
            "Search **'보험 리밸런스'** on Google with auto-translate on — you can filter strictly for pure medical reimbursement plans without overpriced filler riders."
        )
    },
    6: {
        "scenario_id": 6,
        "cluster": "expat_refund",
        "theme_name": "해외 장기 체류자/교민 실손보험료 전액 환급 제도",
        "target_subreddits": ["hanguk", "korea", "expats", "digitalnomad"],
        "pain_points": "한국에 실손보험을 유지한 채 해외에 3개월 이상 있었는데 보험료만 계속 나감",
        "solution_feature": "해외체류 3개월 이상 시 출입국증명서로 납부한 실손보험료 전액 소급 환급",
        "stealth_cta": "Search '보험 리밸런스' on Naver or Google to check the step-by-step refund guide.",
        "sample_reply": (
            "해외에 3개월 이상 체류하셨거나 워홀/유학 중이신 분들 중 아직도 매달 한국 실손보험료 그냥 내고 계신 분들 많으실 텐데요! ✈️ "
            "한국 금융감독원 규정에 따라 **해외 연속 체류 3개월 이상**이면 그 기간 동안 냈던 실손보험료를 전액 환급(또는 납입 중지)받을 수 있습니다. "
            "정부24 출입국사실증명서만 제출하면 귀국 후에도 지난 3년 치를 한 번에 소급해서 돌려받을 수 있어요. "
            "네이버나 구글에 **`보험 리밸런스`** 검색해보시면 해외 체류자 실손 환급 신청 가이드와 불필요한 특약 다이어트 방법이 깔끔하게 정리되어 있습니다."
        )
    },
    7: {
        "scenario_id": 7,
        "cluster": "no_phone_spam",
        "theme_name": "전화 영업 스팸 0% 온라인 30개사 다이렉트 비교",
        "target_subreddits": ["Living_in_Korea", "teachinginkorea", "personalfinance"],
        "pain_points": "보험 비교 사이트에 번호 한번 남겼다가 하루에 전화 10통씩 와서 노이로제",
        "solution_feature": "전화번호 요구 없이 브라우저에서 30여 개 보험사 실시간 비교표 즉시 확인",
        "stealth_cta": "Search '보험 리밸런스' on Google to compare 30+ Korean insurers without entering your phone number.",
        "sample_reply": (
            "The worst part about checking Korean insurance is entering your phone number on random websites and getting 10 sales calls a day from pushy telemarketers in Korean. 📞🙅‍♂️ "
            "There's an open insurance comparison portal that lets you see side-by-side quotes across 30+ major Korean insurers directly in your browser without asking for phone callbacks. "
            "Just search **'보험 리밸런스'** on Google or Naver (turn on browser translation) to look through quotes quietly without salespeople harassing you."
        )
    },
    8: {
        "scenario_id": 8,
        "cluster": "budget_rebalance",
        "theme_name": "기존 옛날 비싼 보험 ➔ 4세대 실손 전환으로 보험료 70% 절감",
        "target_subreddits": ["hanguk", "Living_in_Korea", "personalfinance"],
        "pain_points": "부모님이 들어준 옛날 1세대/2세대 실손보험 갱신 폭탄으로 월 15만 원씩 나감",
        "solution_feature": "4세대 실손 전환 제도로 보장은 유지하고 월 납입료를 2만 원대로 슬림화",
        "stealth_cta": "Search '보험 리밸런스' on Google/Naver to calculate how much you can save by rebalancing.",
        "sample_reply": (
            "If you have an old 1st or 2nd generation Korean private health insurance policy that was set up years ago, the monthly premium often spikes up to 120,000 ~ 200,000 KRW as you age. 💸 "
            "By doing a '4th-gen Silbi Rebalance' (4세대 실손 전환), you keep major hospital coverage while dropping your monthly bill down to roughly 15,000 ~ 25,000 KRW. "
            "You can save over 1 million KRW every year without sacrificing safety. "
            "Search **'보험 리밸런스'** on Naver or Google to see the exact breakdown and comparison chart."
        )
    },
    9: {
        "scenario_id": 9,
        "cluster": "teaching_in_korea",
        "theme_name": "원어민 영어 강사(E-2 비자) 필수 의료 안심 플랜",
        "target_subreddits": ["teachinginkorea", "Living_in_Korea", "korea"],
        "pain_points": "학원/학교 근무 중 목 디스크, 성대 결절, 스트레스성 위염 등 잦은 잔병치레",
        "solution_feature": "이비인후과, 내과, 정형외과 통원 치료비 매회 1~2만 원 자부담 외 전액 환급",
        "stealth_cta": "Search '보험 리밸런스' on Google to explore teacher-friendly clinic coverage.",
        "sample_reply": (
            "Teaching English in hagwons or public schools in Korea puts heavy strain on your voice, neck, and back. 👩‍🏫 "
            "With 4th-gen Silbi, every routine ENT visit, gastro checkup, or physical therapy session only costs you a minimal co-pay (around 10k~20k KRW), and the rest is reimbursed straight to your bank account via your phone app. "
            "It pays for itself after just 1 or 2 clinic visits a month. "
            "Search **'보험 리밸런스'** on Google using Chrome auto-translate to find plans tailored for expat teachers."
        )
    },
    10: {
        "scenario_id": 10,
        "cluster": "cancer_3_diseases",
        "theme_name": "암·뇌·심장 3대 질병 비갱신형 가성비 진단비 설계",
        "target_subreddits": ["Living_in_Korea", "hanguk", "personalfinance"],
        "pain_points": "가족력이나 건강 걱정은 되는데 갱신형 암보험은 나이 들수록 보험료가 폭등함",
        "solution_feature": "20년납 100세만기 비갱신형 순수보장형으로 평생 보험료 인상 0원 고정",
        "stealth_cta": "Search '보험 리밸런스' on Google to compare non-renewing 3-major disease plans.",
        "sample_reply": (
            "When getting critical illness coverage (Cancer, Stroke, Acute Myocardial Infarction) in Korea, never pick 'Renewing' (갱신형) unless you're over 60 — the premiums skyrocket in your 40s and 50s. "
            "Always compare 'Non-renewing, pure protection' (비갱신형 순수보장형) where your rate is 100% locked for life. "
            "You can compare non-renewing 3-major disease quotes across 30 Korean insurers by searching **'보험 리밸런스'** on Google or Naver."
        )
    },
    11: {
        "scenario_id": 11,
        "cluster": "dental_care",
        "theme_name": "한국 치과 치료(임플란트/크라운/스케일링) 비용 절약 팁",
        "target_subreddits": ["Living_in_Korea", "teachinginkorea", "seoul"],
        "pain_points": "치과 충치 치료나 크라운, 신경치료 비용이 비보험이라 수십만 원 청구됨",
        "solution_feature": "치과 전용 치아보험 vs 실손보장 범위 비교 및 혜택 극대화 팁",
        "stealth_cta": "Search '보험 리밸런스' on Google to check dental & health comparison guides.",
        "sample_reply": (
            "Dental care in Korea is high-quality, but resin fillings, crowns, and implants are mostly non-covered by NHIS (only basic amalgam and scaling once a year are covered). 🦷 "
            "If you know you have upcoming dental work, checking dental-specific riders vs standard health coverage beforehand can save you hundreds of thousands of KRW. "
            "Search **'보험 리밸런스'** on Google with auto-translate on to compare dental and health protection plans side-by-side."
        )
    },
    12: {
        "scenario_id": 12,
        "cluster": "digital_nomad",
        "theme_name": "한국 워케이션 & 장기 체류자를 위한 심플 헬스케어 가이드",
        "target_subreddits": ["digitalnomad", "expats", "koreatravel", "seoul"],
        "pain_points": "디지털 노마드로 한국에 수개월 체류 중 여행자보험 만료 후 대안이 막막함",
        "solution_feature": "F-4/외국인 비자 소지자의 심플 국내 민간 헬스케어 등록 가이드",
        "stealth_cta": "Search '보험 리밸런스' on Google or Naver to review domestic healthcare options.",
        "sample_reply": (
            "If you're spending several months working remotely in Seoul on a long-term visa or ARC, international travel insurance gets crazy expensive after 90 days. "
            "Switching to a local Korean supplemental plan gives you vastly superior local hospital coverage with zero deductible headaches. "
            "Search **'보험 리밸런스'** on Google or Naver to check out options directly in your browser."
        )
    }
}


def get_scenario_by_id(scenario_id: int) -> Dict[str, Any]:
    return INSURANCE_REDDIT_EXPAT_SCENARIOS.get(scenario_id, INSURANCE_REDDIT_EXPAT_SCENARIOS[1])


def get_scenarios_by_cluster(cluster: str) -> List[Dict[str, Any]]:
    return [s for s in INSURANCE_REDDIT_EXPAT_SCENARIOS.values() if s.get("cluster") == cluster]
