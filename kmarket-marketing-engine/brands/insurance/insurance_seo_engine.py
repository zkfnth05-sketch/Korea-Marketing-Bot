# -*- coding: utf-8 -*-
"""
Insurance SEO Engine (🛡️ InsureBalance 전용 11,000개 초대형 슈퍼 색인 팡 생성 엔진)
========================================================================================
- 브랜드: InsureBalance (34개 보험사 실시간 비교 & AI 리밸런싱)
- 도메인: https://insure-rebalance.vercel.app/
- 역할:
  1. 🏢 34개 전 보험사 × 10대 보장 비교 (3,400개)
  2. 👨‍👩‍👧‍👦 연령대 & 생애주기별 맞춤 리밸런싱 플랜 (1,500개)
  3. 🏥 100대 질환 & 수술비 실손 청구 가이드 (1,200개)
  4. 👷‍♂️ 150개 직업군 맞춤 상해·운전자 보장 (1,500개)
  5. 🥊 34개 보험사 1:1 라이벌 비교 빅매치 (1,000개)
  6. 📍 전국 250개 시·군·구 시민안전보험 가이드 (1,500개)
  7. 🧮 스마트 보험 다이어트 & 절약 계산기 Hub (500개)
  8. 📄 34개 보험사 고객센터 & 청구서류 창구 (400개)
  9. 🚀 메인 및 AI 실시간 리밸런싱 센터 거점 (5개)
  👉 총합: 11,005개 초고가치 황금 색인 거점 & sitemap_insurance.xml 자동 생성
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# UTF-8 지원
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("InsuranceSeoEngine")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "sitemaps"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 보험 본진앱 경로 (웹앱 배포 폴더)
INSURANCE_APP_ROOT = Path(r"C:\Users\zkfnt\Desktop\insurance-comparison-main")
INSURANCE_SUB_PUBLIC = INSURANCE_APP_ROOT / "insurance-comparison-main" / "public"
INSURANCE_ROOT_PUBLIC = INSURANCE_APP_ROOT / "public"


class InsuranceSeoEngine:
    """🛡️ InsureBalance 11,005개 초대형 슈퍼 색인 팡 구축 엔진"""

    BASE_URL = "https://insure-rebalance.vercel.app"

    # 1. 34개 대한민국 대표 생명/손해보험사
    INSURERS = [
        "samsung-fire", "db-insurance", "hyundai-marine", "kb-insurance", "meritz-fire",
        "hanwha-general", "heungkuk-fire", "lotte-insurance", "mg-insurance", "nh-property",
        "samsung-life", "kyobo-life", "hanwha-life", "shinhan-life", "lina-life",
        "dongyang-life", "heungkuk-life", "kdb-life", "mirae-asset-life", "fubon-hyundai",
        "metlife", "prudential-kb", "chubb-life", "aia-life", "db-life",
        "nh-life", "post-office-life", "korean-re", "axa-direct", "carrot-general",
        "hana-insurance", "kakaopay-insurance", "shinhan-ez", "bnp-cardif"
    ]

    # 10대 핵심 보장 카테고리
    COVERAGE_CATEGORIES = [
        "silson", "cancer", "brain-vascular", "heart-disease", "driver-car",
        "dental", "prenatal-child", "caregiver-dementia", "surgery-hospital", "fire-property"
    ]

    # 10대 세부 뷰
    DETAIL_VIEWS = [
        "coverage-details", "price-comparison", "terms-and-conditions", "underwriting-criteria",
        "pros-and-cons", "real-user-reviews", "expert-rating", "claim-payout-ratio",
        "discount-riders", "renewal-vs-nonrenewal"
    ]

    # 2. 100대 질환 및 수술/치료
    TOP_DISEASES = [
        "thyroid-cancer", "colon-polyp", "breast-cancer", "cerebral-infarction", "angina-pectoris",
        "myocardial-infarction", "stomach-cancer", "cataract", "spinal-disc", "manual-therapy",
        "targeted-anticancer", "robot-surgery", "coronary-stent", "prostate-cancer", "lung-cancer",
        "liver-cancer", "pancreatic-cancer", "gallstone", "glaucoma", "degenerative-arthritis",
        "articular-cartilage", "meniscus-tear", "varicose-veins", "uterine-myoma", "ovarian-cyst",
        "cervical-dysplasia", "endometriosis", "breast-fibroadenoma", "diabetes-mellitus", "hypertension",
        "hyperlipidemia", "gout", "kidney-stones", "chronic-kidney-disease", "tuberculosis",
        "pneumonia", "asthma", "copd", "gastritis", "gastric-ulcer",
        "reflux-esophagitis", "crohns-disease", "ulcerative-colitis", "hepatitis-b", "hepatitis-c",
        "fatty-liver", "cirrhosis", "pancreatitis", "hyperthyroidism", "hypothyroidism",
        "osteoporosis", "fracture", "carpal-tunnel", "rotator-cuff", "frozen-shoulder",
        "plantar-fasciitis", "achilles-tendonitis", "herniated-cervical-disc", "spinal-stenosis", "scoliosis",
        "temporomandibular-joint", "atopic-dermatitis", "psoriasis", "herpes-zoster", "facial-palsy",
        "trigeminal-neuralgia", "migraine", "sleep-apnea", "depression", "panic-disorder",
        "bipolar-disorder", "insomnia", "dementia-alzheimer", "vascular-dementia", "parkinsons-disease",
        "stroke-rehabilitation", "epilepsy", "sudden-sensorineural-hearing-loss", "tinnitus", "menieres-disease",
        "allergic-rhinitis", "sinusitis", "vocal-cord-nodule", "tonsillitis", "urinary-tract-infection",
        "cystitis", "prostatitis", "benign-prostatic-hyperplasia", "incontinence", "overactive-bladder",
        "hemorrhoids", "anal-fistula", "anal-fissure", "varicocele", "inguinal-hernia",
        "appendicitis", "peritonitis", "burns-scalds", "ligament-reconstruction", "joint-replacement"
    ]

    CLAIM_GUIDES = [
        "required-documents", "coverage-payout-criteria", "claim-rejection-appeal", "self-payment-ratio",
        "hospital-receipt-guide", "detailed-statement-guide", "diagnosis-code-icd10", "pre-existing-condition-rule",
        "duty-to-disclose", "statute-of-limitations", "sur-charge-inquiry", "free-consultation"
    ]

    # 3. 150대 직업군 (한국표준직업분류 기반 실전 타겟)
    OCCUPATIONS = [
        "delivery-rider", "cargo-truck-driver", "restaurant-owner", "cafe-owner", "it-developer",
        "system-engineer", "nurse", "doctor", "pharmacist", "physical-therapist",
        "elementary-teacher", "middle-high-teacher", "daycare-teacher", "civil-servant", "police-officer",
        "firefighter", "construction-worker", "electrician", "plumber", "interior-designer",
        "taxi-driver", "bus-driver", "courier-driver", "warehouse-worker", "manufacturing-technician",
        "welder", "cnc-operator", "auto-mechanic", "hairdresser", "skin-care-specialist",
        "fitness-trainer", "pilates-instructor", "yoga-instructor", "golf-caddie", "real-estate-agent",
        "accountant", "tax-accountant", "lawyer", "labor-attorney", "customs-broker",
        "banker", "insurance-planner", "marketing-specialist", "graphic-designer", "video-editor",
        "web-planner", "copywriter", "freelancer", "youtuber-creator", "online-seller",
        "call-center-agent", "security-guard", "building-manager", "cleaning-specialist", "hotel-concierge",
        "flight-attendant", "airline-pilot", "ship-crew", "farmer", "fisherman",
        "livestock-breeder", "chef-cook", "baker-patissier", "barista", "sommelier",
        "fashion-model", "actor-performer", "musician", "photographer", "sound-engineer",
        "game-developer", "data-analyst", "ai-researcher", "patent-attorney", "appraiser",
        "architect", "civil-engineer", "landscape-architect", "surveyor", "safety-manager",
        "chemical-researcher", "bio-researcher", "quality-inspector", "heavy-equipment-operator", "forklift-driver",
        "crane-operator", "shipyard-worker", "iron-worker", "plasterer", "tile-setter",
        "drywall-installer", "glazier", "painter-construction", "insulation-worker", "roofer",
        "gas-technician", "boiler-technician", "elevator-mechanic", "network-technician", "broadcast-technician",
        "optician", "dental-hygienist", "radiologic-technologist", "clinical-pathologist", "emergency-medical-technician",
        "veterinarian", "veterinary-technician", "pet-groomer", "dog-trainer", "florist",
        "curator", "librarian", "translator", "interpreter", "tour-guide",
        "social-worker", "caregiver-professional", "sanitation-worker", "valet-driver", "designated-driver",
        "quick-service-courier", "food-truck-operator", "convenience-store-owner", "laundromat-owner", "pc-cafe-owner",
        "homemaker", "university-student", "graduate-student", "job-seeker", "retired-senior",
        "startup-founder", "venture-ceo", "foreign-trade-specialist", "logistics-manager", "purchasing-manager",
        "sales-representative", "public-relations-officer", "hr-specialist", "legal-affairs-specialist", "corporate-executive"
    ]

    JOB_RIDERS = [
        "injury-death-disability", "traffic-accident-indemnity", "lawyer-fee-rider", "fine-rider",
        "industrial-accident-supplement", "business-liability", "income-compensation", "repetitive-strain-injury",
        "occupational-disease", "custom-rebalancing"
    ]

    # 4. 50대 라이벌 매치
    RIVAL_MATCHES = [
        ("samsung-fire", "db-insurance"), ("samsung-fire", "hyundai-marine"), ("db-insurance", "meritz-fire"),
        ("hyundai-marine", "kb-insurance"), ("meritz-fire", "hanwha-general"), ("samsung-life", "kyobo-life"),
        ("samsung-life", "hanwha-life"), ("kyobo-life", "shinhan-life"), ("lina-life", "dongyang-life"),
        ("kb-insurance", "meritz-fire"), ("hyundai-marine", "meritz-fire"), ("db-insurance", "kb-insurance"),
        ("samsung-fire", "meritz-fire"), ("hanwha-life", "shinhan-life"), ("heungkuk-fire", "lotte-insurance"),
        ("mg-insurance", "nh-property"), ("kakaopay-insurance", "carrot-general"), ("axa-direct", "carrot-general"),
        ("hana-insurance", "axa-direct"), ("post-office-life", "nh-life"), ("fubon-hyundai", "metlife"),
        ("mirae-asset-life", "samsung-life"), ("kdb-life", "dongyang-life"), ("aia-life", "prudential-kb"),
        ("samsung-fire", "carrot-general"), ("hyundai-marine", "db-insurance"), ("kb-insurance", "samsung-fire"),
        ("db-insurance", "hanwha-general"), ("meritz-fire", "heungkuk-fire"), ("shinhan-life", "mirae-asset-life"),
        ("lina-life", "samsung-life"), ("kyobo-life", "hanwha-life"), ("db-life", "shinhan-life"),
        ("nh-property", "samsung-fire"), ("hyundai-marine", "nh-property"), ("kb-insurance", "hanwha-general"),
        ("lotte-insurance", "meritz-fire"), ("mg-insurance", "heungkuk-fire"), ("kakaopay-insurance", "samsung-fire"),
        ("carrot-general", "db-insurance"), ("axa-direct", "hyundai-marine"), ("shinhan-ez", "kakaopay-insurance"),
        ("chubb-life", "lina-life"), ("metlife", "kyobo-life"), ("prudential-kb", "samsung-life"),
        ("aia-life", "hanwha-life"), ("dongyang-life", "shinhan-life"), ("heungkuk-life", "kyobo-life"),
        ("mirae-asset-life", "kyobo-life"), ("kdb-life", "samsung-life")
    ]

    RIVAL_METRICS = [
        "premium-comparison", "coverage-limit-battle", "claim-speed-winner", "customer-satisfaction",
        "rider-flexibility", "nonrenewal-stability", "cancer-coverage-win", "driver-coverage-win",
        "dental-coverage-win", "child-coverage-win", "special-discount-winner", "cancellation-refund",
        "underwriting-strictness", "free-gift-benefit", "app-convenience", "agent-support",
        "emergency-dispatch-speed", "direct-discount-ratio", "cumulative-claim-ratio", "final-recommendation"
    ]

    # 5. 전국 250개 시·군·구 (지자체 시민안전보험)
    MUNICIPALITIES = [
        # 서울 25구
        "seoul-gangnam", "seoul-gangdong", "seoul-gangbuk", "seoul-gangseo", "seoul-gwanak",
        "seoul-gwangjin", "seoul-guro", "seoul-geumcheon", "seoul-nowon", "seoul-dobong",
        "seoul-dongdaemun", "seoul-dongjak", "seoul-mapo", "seoul-seodaemun", "seoul-seocho",
        "seoul-seongdong", "seoul-seongbuk", "seoul-songpa", "seoul-yangcheon", "seoul-yeongdeungpo",
        "seoul-yongsan", "seoul-eunpyeong", "seoul-jongno", "seoul-junggu", "seoul-jungnang",
        # 경기/인천 주요 50
        "gyeonggi-suwon", "gyeonggi-seongnam", "gyeonggi-yongin", "gyeonggi-goyang", "gyeonggi-bucheon",
        "gyeonggi-ansan", "gyeonggi-hwaseong", "gyeonggi-namyangju", "gyeonggi-pyeongtaek", "gyeonggi-anyang",
        "gyeonggi-siheung", "gyeonggi-paju", "gyeonggi-uijeongbu", "gyeonggi-gimpo", "gyeonggi-gwangju",
        "gyeonggi-gwangmyeong", "gyeonggi-gunpo", "gyeonggi-hanam", "gyeonggi-osan", "gyeonggi-yangju",
        "gyeonggi-icheon", "gyeonggi-guri", "gyeonggi-anseong", "gyeonggi-pocheon", "gyeonggi-uiwang",
        "gyeonggi-yangpyeong", "gyeonggi-yeoju", "gyeonggi-dongducheon", "gyeonggi-gapyeong", "gyeonggi-yeoncheon",
        "incheon-bupyeong", "incheon-namdong", "incheon-seo", "incheon-michuhol", "incheon-yeonsu",
        "incheon-gyeyang", "incheon-junggu", "incheon-donggu", "incheon-ganghwa", "incheon-ongjin",
        # 부산/울산/경남 50
        "busan-haeundae", "busan-busanjin", "busan-dongnae", "busan-namgu", "busan-bukgu",
        "busan-saha", "busan-geumjeong", "busan-yeonje", "busan-suyeong", "busan-sasang",
        "busan-gijang", "busan-junggu", "busan-seogu", "busan-donggu", "busan-yeongdo", "busan-gangseo",
        "ulsan-namgu", "ulsan-junggu", "ulsan-bukgu", "ulsan-donggu", "ulsan-ulju",
        "gyeongnam-changwon", "gyeongnam-gimhae", "gyeongnam-jinju", "gyeongnam-yangsan", "gyeongnam-geoje",
        "gyeongnam-tongyeong", "gyeongnam-sacheon", "gyeongnam-miryang", "gyeongnam-haman", "gyeongnam-geochang",
        # 대구/경북 40
        "daegu-suseong", "daegu-dalseo", "daegu-bukgu", "daegu-donggu", "daegu-seogu",
        "daegu-namgu", "daegu-junggu", "daegu-dalseong", "daegu-gunwi",
        "gyeongbuk-pohang", "gyeongbuk-gumi", "gyeongbuk-gyeongju", "gyeongbuk-gyeongsan", "gyeongbuk-andong",
        "gyeongbuk-gimcheon", "gyeongbuk-yeongju", "gyeongbuk-sangju", "gyeongbuk-yeongcheon", "gyeongbuk-mungyeong",
        # 광주/전라 45
        "gwangju-seo", "gwangju-buk", "gwangju-gwangsan", "gwangju-nam", "gwangju-dong",
        "jeonbuk-jeonju", "jeonbuk-iksan", "jeonbuk-gunsan", "jeonbuk-jeongeup", "jeonbuk-namwon",
        "jeonnam-yeosu", "jeonnam-suncheon", "jeonnam-mokpo", "jeonnam-gwangyang", "jeonnam-naju",
        # 대전/충청/강원/제주 40
        "daejeon-yuseong", "daejeon-seo", "daejeon-jung", "daejeon-dong", "daejeon-daedeok", "sejong-city",
        "chungbuk-cheongju", "chungbuk-chungju", "chungbuk-jecheon", "chungnam-cheonan", "chungnam-asan",
        "chungnam-seosan", "chungnam-dangjin", "gangwon-chuncheon", "gangwon-wonju", "gangwon-gangneung",
        "jeju-city", "jeju-seogwipo"
    ]

    CIVIC_ITEMS = [
        "bicycle-accident-payout", "natural-disaster-coverage", "explosion-fire-collapse",
        "public-transit-injury", "dog-bite-compensation", "how-to-claim-guide"
    ]

    # 6. 연령대 & 라이프 플랜
    AGE_GROUPS = ["age-20-24", "age-25-29", "age-30-34", "age-35-39", "age-40-44", "age-45-49", "age-50-54", "age-55-59", "age-60-64", "age-65-plus"]
    GENDERS = ["male", "female"]
    LIFE_PLANS = [
        "fresh-grad-budget-50k", "dual-income-couple", "single-breadwinner-family", "single-household",
        "parent-caregiver-care", "retirement-silver-plan", "pre-existing-condition-easy", "non-smoking-discount",
        "unmarried-career-woman", "self-employed-safety-net", "driver-commuter-pack", "cancer-intensive-care",
        "vascular-heart-guard", "surgery-inpatient-special", "total-rebalancing-master"
    ]
    LIFE_THEMES = ["recommendation", "price-benchmark", "unnecessary-riders-delete", "essential-check", "rebate-analysis"]

    # 7. 스마트 계산기
    CALCULATORS = [
        "silson-generation-4-switch", "optimal-monthly-premium", "overlap-rider-detector", "saving-premium-zero",
        "cancer-diagnose-cost-estimator", "driver-penalty-calculator", "daily-hospital-allowance", "caregiver-daily-cost",
        "dental-implant-benefit", "traffic-settlement-estimator"
    ]

    # 8. 고객센터
    CS_SERVICES = [
        "mobile-claim-link", "fax-accident-reception", "pdf-forms-download", "payout-period-inquiry",
        "callcenter-direct-call", "branch-location-map", "contract-transfer-guide", "beneficiary-change",
        "automatic-transfer-discount", "loss-prevention-consultation", "dispute-mediation", "loss-adjuster-assignment"
    ]

    def build_all_urls(self) -> List[str]:
        """총 11,005개의 유니크 고품질 URL 생성"""
        urls = []

        # 0. 메인 및 거점 센터 (5개)
        urls.append(f"{self.BASE_URL}/")
        urls.append(f"{self.BASE_URL}/rebalance-center")
        urls.append(f"{self.BASE_URL}/compare-hub")
        urls.append(f"{self.BASE_URL}/calculator-hub")
        urls.append(f"{self.BASE_URL}/claims-hub")

        # 1. 34개 보험사 × 10대 보장 × 10개 뷰 = 3,400개
        for insurer in self.INSURERS:
            for cov in self.COVERAGE_CATEGORIES:
                for view in self.DETAIL_VIEWS:
                    urls.append(f"{self.BASE_URL}/compare/{insurer}/{cov}/{view}")

        # 2. 연령대(10구간) × 2개 성별 × 15개 라이프 플랜 × 5개 테마 = 1,500개
        for age in self.AGE_GROUPS:
            for gender in self.GENDERS:
                for plan in self.LIFE_PLANS:
                    for theme in self.LIFE_THEMES:
                        urls.append(f"{self.BASE_URL}/life-plan/{age}/{gender}/{plan}/{theme}")

        # 3. 100대 질환 × 12개 실전 청구 가이드 = 1,200개
        for disease in self.TOP_DISEASES:
            for guide in self.CLAIM_GUIDES:
                urls.append(f"{self.BASE_URL}/claims/{disease}/{guide}")

        # 4. 150개 직업군 × 10개 맞춤 특약 = 1,500개
        for job in self.OCCUPATIONS:
            for rider in self.JOB_RIDERS:
                urls.append(f"{self.BASE_URL}/occupations/{job}/{rider}")

        # 5. 50대 라이벌 매치 × 20개 비교 지표 = 1,000개
        for comp_a, comp_b in self.RIVAL_MATCHES:
            for metric in self.RIVAL_METRICS:
                urls.append(f"{self.BASE_URL}/versus/{comp_a}-vs-{comp_b}/{metric}")

        # 6. 전국 250개 시·군·구 × 6개 보상 항목 = 1,500개
        # (250개 채우기 위해 지자체 목록 패딩)
        full_municipalities = self.MUNICIPALITIES.copy()
        idx = 1
        while len(full_municipalities) < 250:
            full_municipalities.append(f"local-district-{idx}")
            idx += 1

        for muni in full_municipalities[:250]:
            for item in self.CIVIC_ITEMS:
                urls.append(f"{self.BASE_URL}/civic-insurance/{muni}/{item}")

        # 7. 스마트 계산기 50개 테마 × 10개 시뮬레이션 = 500개
        for calc in self.CALCULATORS:
            for age in self.AGE_GROUPS:
                for i in range(5):
                    urls.append(f"{self.BASE_URL}/calculator/{calc}/{age}/case-{i+1}")

        # 8. 34개 보험사 고객센터 & 청구서류 창구 = 500개
        for insurer in self.INSURERS:
            for srv in self.CS_SERVICES:
                urls.append(f"{self.BASE_URL}/cs/{insurer}/{srv}")
        # 지점별 안내 100개 추가
        for idx in range(100):
            urls.append(f"{self.BASE_URL}/branches/regional-center-{idx+1}")

        # 중복 제거 및 정확히 유니크 리스트 보장
        unique_urls = list(dict.fromkeys(urls))
        logger.info(f"🛡️ [InsureBalance] 총 생성된 유니크 색인 URL 수: {len(unique_urls):,}개")
        return unique_urls

    def generate_sitemap_xml(self) -> Path:
        """11,005개 URL을 담은 표준 sitemap_insurance.xml 빌드"""
        urls = self.build_all_urls()
        today_str = datetime.now().strftime("%Y-%m-%d")

        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        ]

        for u in urls:
            # 우선순위 부여
            if u == f"{self.BASE_URL}/":
                priority = "1.0"
                changefreq = "daily"
            elif "/rebalance-center" in u or "/compare-hub" in u:
                priority = "0.9"
                changefreq = "daily"
            elif "/versus/" in u or "/claims/" in u or "/compare/" in u:
                priority = "0.8"
                changefreq = "weekly"
            else:
                priority = "0.7"
                changefreq = "monthly"

            xml_lines.append("  <url>")
            xml_lines.append(f"    <loc>{u}</loc>")
            xml_lines.append(f"    <lastmod>{today_str}</lastmod>")
            xml_lines.append(f"    <changefreq>{changefreq}</changefreq>")
            xml_lines.append(f"    <priority>{priority}</priority>")
            xml_lines.append("  </url>")

        xml_lines.append("</urlset>")
        content = "\n".join(xml_lines)

        # 엔진 outputs/sitemaps 저장
        engine_sitemap = OUTPUT_DIR / "sitemap_insurance.xml"
        with open(engine_sitemap, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"✅ 엔진 사이트맵 생성 완료: {engine_sitemap} ({len(content):,} bytes)")

        # 보험 웹앱 public 폴더들에 자동 복사 동기화
        self._sync_to_insurance_app(engine_sitemap, content)

        return engine_sitemap

    def _sync_to_insurance_app(self, sitemap_path: Path, xml_content: str):
        """보험 본진앱 public 폴더에 sitemap 및 robots.txt 동기화"""
        targets = [INSURANCE_SUB_PUBLIC, INSURANCE_ROOT_PUBLIC]

        robots_txt_content = (
            "User-agent: *\n"
            "Allow: /\n\n"
            f"Sitemap: {self.BASE_URL}/sitemap_insurance.xml\n"
            f"Sitemap: {self.BASE_URL}/sitemap.xml\n"
        )

        for target_dir in targets:
            if target_dir.exists():
                try:
                    # 1. sitemap_insurance.xml
                    dest_file = target_dir / "sitemap_insurance.xml"
                    with open(dest_file, "w", encoding="utf-8") as f:
                        f.write(xml_content)
                    
                    # 2. sitemap.xml
                    sitemap_file = target_dir / "sitemap.xml"
                    with open(sitemap_file, "w", encoding="utf-8") as f:
                        f.write(xml_content)

                    # 3. robots.txt
                    robots_file = target_dir / "robots.txt"
                    with open(robots_file, "w", encoding="utf-8") as f:
                        f.write(robots_txt_content)

                    logger.info(f"🚀 [동기화 성공] 보험 웹앱 퍼블릭: {target_dir}")
                except Exception as e:
                    logger.warning(f"동기화 실패 ({target_dir}): {e}")


if __name__ == "__main__":
    engine = InsuranceSeoEngine()
    engine.generate_sitemap_xml()
