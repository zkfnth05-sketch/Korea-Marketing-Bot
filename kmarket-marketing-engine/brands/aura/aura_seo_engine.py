# -*- coding: utf-8 -*-
"""
💖 Aura SEO & Sitemap Engine (Aura 전용 7,000개 초고검색량 색인 팡 & sitemap_aura.xml 독립 레고 블록)
========================================================================================
- 브랜드: Aura (2030 AI 데이팅 / 50:50 성비 보장 / 실시간 4개국어 자막 영상통화)
- 마케팅 절대 헌법: "국내 2030 여성 + 외국인 여성(일본/영미권) 100% 올인 타겟팅"
- 산출물:
  1. 🇰🇷 국내 2030 여성 실제 초고검색량 5,000개 URL (핫플 팝업, 감성 카페, 환승연애 심리, MBTI 256개, 스타일)
  2. 🌐 외국인 여성(일본 1,000개 + 영미권 1,000개) 실제 초고검색량 2,000개 URL (Seoul Cafe, #日韓カップル, Safe Friends)
  3. 🚀 총 7,000개 초고속 색인 사이트맵 (sitemap_aura.xml) 및 SEO 정적 랜딩 HTML 일괄 빌드
  4. ⚡ Google Indexing API v3 & Naver Search Advisor 실시간 동시 색인 핑 전송
"""

import os
import sys
import json
import logging
import re
import xml.sax.saxutils as saxutils
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# UTF-8 콘솔 지원
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("AuraSEOEngine")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
OUTPUTS_DIR = PROJECT_ROOT / "outputs"


class AuraSEOEngine:
    """💖 Aura 2030 여성 & 글로벌 외국인 여성 전용 7,000개 초고검색량 SEO 엔진"""

    BRAND = "aura"
    NAME = "Aura 2030 AI Dating"
    BASE_DOMAIN = "https://aura-ai-dating.vercel.app"
    LANDING_URL = "https://aura-ai-dating.vercel.app/lounge"

    def __init__(self):
        self.output_dir = OUTPUTS_DIR / "seo_aura"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sitemap_dir = OUTPUTS_DIR / "sitemaps"
        self.sitemap_dir.mkdir(parents=True, exist_ok=True)
        self.sitemap_file = self.sitemap_dir / "sitemap_aura.xml"

    # =========================================================================
    # 📍 1. 국내 200개 여성 핫플레이스 거점 매트릭스
    # =========================================================================
    @staticmethod
    def get_domestic_hotspots() -> List[Dict[str, str]]:
        """서울/수도권 핫플 100 + 대학가 50 + 전국 광역시 핫플 50 = 총 200개 거점"""
        spots = [
            # [서울 핵심 핫플 60곳]
            {"id": "seongsu", "name": "성수동", "region": "서울 성동구", "feature": "힙한 팝업스토어 & 서울숲 카페거리"},
            {"id": "yeonnam", "name": "연남동", "region": "서울 마포구", "feature": "연트럴파크 & 감성 와인바"},
            {"id": "hannam", "name": "한남동", "region": "서울 용산구", "feature": "테라스 브런치 & 감성 갤러리"},
            {"id": "euljiro", "name": "을지로", "region": "서울 중구", "feature": "힙지로 빈티지 와인바 & 펍"},
            {"id": "ikseon", "name": "익선동", "region": "서울 종로구", "feature": "한옥 감성 카페 & 퓨전 맛집"},
            {"id": "dosan", "name": "도산공원", "region": "서울 강남구", "feature": "압구정 하이엔드 브런치 & 디저트"},
            {"id": "songridan", "name": "송리단길", "region": "서울 송파구", "feature": "석촌호수 뷰 & 디저트 카페"},
            {"id": "hongdae", "name": "홍대입구", "region": "서울 마포구", "feature": "트렌디한 거리 & 버스킹"},
            {"id": "samcheong", "name": "삼청동", "region": "서울 종로구", "feature": "고즈넉한 한옥 찻집 & 미술관"},
            {"id": "itaewon", "name": "이태원", "region": "서울 용산구", "feature": "글로벌 루프탑 & 라운지바"},
            {"id": "gangnam", "name": "강남역", "region": "서울 강남구", "feature": "조용한 룸식당 & 감성 바"},
            {"id": "yeouido", "name": "여의도", "region": "서울 영등포구", "feature": "더현대 서울 & 한강 피크닉"},
            {"id": "mullae", "name": "문래창작촌", "region": "서울 영등포구", "feature": "철공소 골목 레트로 감성 펍"},
            {"id": "mangwon", "name": "망원동", "region": "서울 마포구", "feature": "망리단길 감성 소품샵 & 베이커리"},
            {"id": "apgujeong", "name": "압구정로데오", "region": "서울 강남구", "feature": "핫플레이스 다이닝 & 라운지"},
            {"id": "sinsa", "name": "신사 가로수길", "region": "서울 강남구", "feature": "쇼룸 & 테라스 카페"},
            {"id": "cheongdam", "name": "청담동", "region": "서울 강남구", "feature": "프라이빗 다이닝 & 파인다이닝"},
            {"id": "jamsil", "name": "잠실", "region": "서울 송파구", "feature": "롯데월드몰 & 석촌호수 데이트"},
            {"id": "seoul-forest", "name": "서울숲", "region": "서울 성동구", "feature": "피크닉 & 아틀리에 브런치"},
            {"id": "kondae", "name": "건대입구", "region": "서울 광진구", "feature": "트렌디 맛집 & 보드게임 카페"},
            {"id": "hyehwa", "name": "대학로(혜화)", "region": "서울 종로구", "feature": "연극 데이트 & 낙산공원 야경"},
            {"id": "sadang", "name": "사당역", "region": "서울 동작구", "feature": "교통요지 조용한 이자카야"},
            {"id": "sharosugil", "name": "샤로수길", "region": "서울 관악구", "feature": "아기자기한 세계요리 맛집"},
            {"id": "sinchon", "name": "신촌", "region": "서울 서대문구", "feature": "대학생 미팅 & 가성비 맛집"},
            {"id": "ewha", "name": "이대", "region": "서울 서대문구", "feature": "디저트 카페 & 뷰티 로드"},
            {"id": "dongmyo", "name": "동묘·신설동", "region": "서울 종로구", "feature": "빈티지 레트로 감성 투어"},
            {"id": "seochon", "name": "서촌", "region": "서울 종로구", "feature": "통인시장 & 감성 서점 골목"},
            {"id": "bukchon", "name": "북촌한옥마을", "region": "서울 종로구", "feature": "전통 한옥 뷰 & 티룸"},
            {"id": "gyeongridan", "name": "경리단길", "region": "서울 용산구", "feature": "남산 뷰 수제맥주 펍"},
            {"id": "yongridan", "name": "용리단길(신용산)", "region": "서울 용산구", "feature": "이국적인 핫플 & 에스프레소바"},
            {"id": "haebangchon", "name": "해방촌(HBC)", "region": "서울 용산구", "feature": "노을 뷰 루프탑 & 독립서점"},
            {"id": "dapsimni", "name": "답십리", "region": "서울 동대문구", "feature": "고미술 거리 & 숨은 맛집"},
            {"id": "wangsimni", "name": "왕십리", "region": "서울 성동구", "feature": "엔터식스 & 곱창거리 데이트"},
            {"id": "nowon", "name": "노원역", "region": "서울 노원구", "feature": "문화의거리 & 룸술집"},
            {"id": "suyu", "name": "수유역", "region": "서울 강북구", "feature": "감성 이자카야 & 2차 술집"},
            {"id": "cheongnyangni", "name": "청량리", "region": "서울 동대문구", "feature": "경동시장 스타벅스1960"},
            {"id": "dangsan", "name": "당산역", "region": "서울 영등포구", "feature": "한강 여의도 뷰 카페"},
            {"id": "yeongdeungpo", "name": "영등포 타임스퀘어", "region": "서울 영등포구", "feature": "실내 몰링 데이트"},
            {"id": "sindorim", "name": "신도림 디큐브시티", "region": "서울 구로구", "feature": "뮤지컬 & 레스토랑"},
            {"id": "mokdong", "name": "목동", "region": "서울 양천구", "feature": "파리공원 & 오목교 브런치"},
            {"id": "bangi", "name": "방이동 먹자골목", "region": "서울 송파구", "feature": "올림픽공원 & 2차 맛집"},
            {"id": "munjeong", "name": "문정동", "region": "서울 송파구", "feature": "법조타운 깔끔한 다이닝"},
            {"id": "gangdong", "name": "천호·강동", "region": "서울 강동구", "feature": "로데오거리 & 한강 뷰"},
            {"id": "misa", "name": "미사호수공원", "region": "경기 하남시", "feature": "호수 뷰 테라스 카페거리"},
            {"id": "wirye", "name": "위례신도시", "region": "서울·성남", "feature": "중앙광장 브런치 맛집"},
            {"id": "magok", "name": "마곡나루", "region": "서울 강서구", "feature": "서울식물원 & 와인바"},
            {"id": "balsan", "name": "발산역", "region": "서울 강서구", "feature": "조용한 프라이빗 룸식당"},
            {"id": "sangsu", "name": "상수역", "region": "서울 마포구", "feature": "골목 감성 이자카야 & 디저트"},
            {"id": "hapjeong", "name": "합정역", "region": "서울 마포구", "feature": "메세나폴리스 & 출판거리"},
            {"id": "mapo", "name": "공덕·마포", "region": "서울 마포구", "feature": "경의선 숲길 산책 & 와인"},
            {"id": "seocho", "name": "서초 예술의전당", "region": "서울 서초구", "feature": "전시회 데이트 & 클래식 브런치"},
            {"id": "yangjae", "name": "양재천", "region": "서울 서초구", "feature": "양재천 카페거리 산책"},
            {"id": "daechi", "name": "한티·대치", "region": "서울 강남구", "feature": "롯데백화점 & 감성 카페"},
            {"id": "seolleung", "name": "선릉역", "region": "서울 강남구", "feature": "선정릉 숲길 산책 & 펍"},
            {"id": "yeoksam", "name": "역삼역", "region": "서울 강남구", "feature": "센터필드 미식 데이트"},
            {"id": "samseong", "name": "삼성 코엑스", "region": "서울 강남구", "feature": "별마당도서관 & 아쿠아리움"},
            {"id": "sungsoo-forest", "name": "뚝섬역", "region": "서울 성동구", "feature": "블루보틀 & 베이커리 맛집"},
            {"id": "gwanghwamun", "name": "광화문·시청", "region": "서울 종로구", "feature": "덕수궁 돌담길 & 정동길 데이트"},
            {"id": "dongdaemun", "name": "DDP(동대문)", "region": "서울 중구", "feature": "전시회 & 야시장 데이트"},
            {"id": "namsan", "name": "남산타워", "region": "서울 중구", "feature": "케이블카 & 야경 레스토랑"},

            # [경기/인천 수도권 핵심 핫플 40곳]
            {"id": "pangyo", "name": "판교 아브뉴프랑", "region": "경기 성남시", "feature": "백현동 카페거리 & 고급 브런치"},
            {"id": "bundang-seohyeon", "name": "분당 서현역", "region": "경기 성남시", "feature": "AK플라자 & 로데오 맛집"},
            {"id": "bundang-jeongja", "name": "분당 정자동", "region": "경기 성남시", "feature": "정자동 카페거리 & 테라스 펍"},
            {"id": "gwanggyo", "name": "광교 앨리웨이", "region": "경기 수원시", "feature": "광교호수공원 & 뷰 브런치"},
            {"id": "suwon-haenggung", "name": "수원 행궁동", "region": "경기 수원시", "feature": "행리단길 감성 카페 & 화성야경"},
            {"id": "suwon-ingye", "name": "수원 인계동", "region": "경기 수원시", "feature": "나혜석거리 & 감성 이자카야"},
            {"id": "ilsan-baekma", "name": "일산 밤리단길", "region": "경기 고양시", "feature": "보넷길 감성 주택가 카페"},
            {"id": "ilsan-lafesta", "name": "일산 라페스타", "region": "경기 고양시", "feature": "웨스턴돔 & 호수공원 피크닉"},
            {"id": "songdo-central", "name": "송도 센트럴파크", "region": "인천 연수구", "feature": "수상택시 & 한옥마을 다이닝"},
            {"id": "songdo-triple", "name": "송도 트리플스트리트", "region": "인천 연수구", "feature": "송현아 & 실내 맛집"},
            {"id": "bupyeong", "name": "부평 문화의거리", "region": "인천 부평구", "feature": "평리단길 감성 카페 & 테마바"},
            {"id": "guwol", "name": "인천 구월동", "region": "인천 남동구", "feature": "로데오거리 & 룸술집"},
            {"id": "cheongna", "name": "청나 커낼웨이", "region": "인천 서구", "feature": "수변공원 뷰 테라스"},
            {"id": "anyang-beomgye", "name": "안양 범계역", "region": "경기 안양시", "feature": "로데오거리 & 감성 와인바"},
            {"id": "anyang-pyeongchon", "name": "안양 평촌 학원가", "region": "경기 안양시", "feature": "중앙공원 & 디저트 맛집"},
            {"id": "bucheon-jungdong", "name": "부천 중동·신중동", "region": "경기 부천시", "feature": "현대백화점 뒤 먹자골목"},
            {"id": "gimpo-gurae", "name": "김포 구래동", "region": "경기 김포시", "feature": "수변공원 & 핫플레이스"},
            {"id": "gimpo-labonita", "name": "김포 라베니체", "region": "경기 김포시", "feature": "금빛수로 문보트 데이트"},
            {"id": "hanam-starfield", "name": "하남 스타필드", "region": "경기 하남시", "feature": "쇼핑몰 & 아쿠아필드 스파"},
            {"id": "goyang-starfield", "name": "고양 스타필드", "region": "경기 고양시", "feature": "대형 실내 데이트몰"},
            {"id": "yongin-bojeong", "name": "용인 보정동", "region": "경기 용인시", "feature": "죽전 카페거리 할로윈/조명"},
            {"id": "yongin-gigi", "name": "용인 기흥 고매동", "region": "경기 용인시", "feature": "대형 베이커리 식물원 카페"},
            {"id": "paju-heyri", "name": "파주 헤이리예술마을", "region": "경기 파주시", "feature": "갤러리 & 감성 드라이브"},
            {"id": "paju-publishing", "name": "파주 출판도시", "region": "경기 파주시", "feature": "지혜의숲 & 북카페 데이트"},
            {"id": "namyangju-hanriver", "name": "남양주 한강변", "region": "경기 남양주시", "feature": "팔당 물안개공원 뷰 카페"},
            {"id": "yangpyeong-dumulmeori", "name": "양평 두물머리", "region": "경기 양평군", "feature": "연핫도그 & 강변 드라이브"},
            {"id": "gapyeong-cheongpyeong", "name": "가평 청평호반", "region": "경기 가평군", "feature": "리버뷰 카페 & 수상레저"},
            {"id": "dongtan-lake", "name": "동탄 호수공원", "region": "경기 화성시", "feature": "루나쇼 & 레이크꼬모 브런치"},
            {"id": "pyeongtaek-sosabeol", "name": "평택 소사벌", "region": "경기 평택시", "feature": "배다리저수지 & 감성 카페"},
            {"id": "ansan-gojan", "name": "안산 고잔신도시", "region": "경기 안산시", "feature": "문화광장 2차 술집"},
            {"id": "siheung-baegot", "name": "시흥 배곧신도시", "region": "경기 시흥시", "feature": "한울공원 해넘이 뷰 카페"},
            {"id": "uijeongbu-minrak", "name": "의정부 민락2지구", "region": "경기 의정부시", "feature": "메가박스 & 핫플레이스"},
            {"id": "guri-dollegs", "name": "구리 돌다리", "region": "경기 구리시", "feature": "전통시장 곱창 & 감성 펍"},
            {"id": "gwangmyeong-station", "name": "광명역 아브뉴프랑", "region": "경기 광명시", "feature": "이케아 & 깔끔한 레스토랑"},
            {"id": "incheon-chinatown", "name": "인천 차이나타운", "region": "인천 중구", "feature": "개항장 거리 레트로 카페"},
            {"id": "incheon-wolmido", "name": "인천 월미도", "region": "인천 중구", "feature": "디스코팡팡 & 오션뷰 조개구이"},
            {"id": "yeongjong-incheon", "name": "영종도 구읍뱃터", "region": "인천 중구", "feature": "오션뷰 감성 카페 & 인스파이어"},
            {"id": "ganghwa-dongmak", "name": "강화도 동막해변", "region": "인천 강화군", "feature": "서해 일몰 드라이브"},
            {"id": "hwaseong-jeongok", "name": "화성 전곡항", "region": "경기 화성시", "feature": "요트투어 & 케이블카 데이트"},
            {"id": "anseong-starfield", "name": "안성 스타필드", "region": "경기 안성시", "feature": "평택/안성 메가몰 데이트"},

            # [전국 주요 50개 대학교 캠퍼스]
            {"id": "snu", "name": "서울대(샤로수길)", "region": "서울 관악구", "feature": "대학생 미팅 & 세계요리"},
            {"id": "yonsei", "name": "연세대(신촌)", "region": "서울 서대문구", "feature": "연세로 버스킹 & 펍"},
            {"id": "korea-univ", "name": "고려대(안암)", "region": "서울 성북구", "feature": "참살이길 가성비 맛집"},
            {"id": "sogang", "name": "서강대(대흥)", "region": "서울 마포구", "feature": "경의선숲길 조용한 카페"},
            {"id": "sungkyunkwan", "name": "성균관대(혜화)", "region": "서울 종로구", "feature": "명륜동 한옥 & 감성 카페"},
            {"id": "hanyang", "name": "한양대(왕십리)", "region": "서울 성동구", "feature": "사근동 & 한양대 먹자골목"},
            {"id": "cau", "name": "중앙대(흑석)", "region": "서울 동작구", "feature": "흑석로 감성 밥집 & 카페"},
            {"id": "khu", "name": "경희대(회기)", "region": "서울 동대문구", "feature": "파전골목 & 유럽풍 캠퍼스"},
            {"id": "hufs", "name": "한국외대(이문)", "region": "서울 동대문구", "feature": "이국적인 세계음식점"},
            {"id": "uos", "name": "서울시립대(전농)", "region": "서울 동대문구", "feature": "조용한 캠퍼스 & 브런치"},
            {"id": "konkuk", "name": "건국대(건대입구)", "region": "서울 광진구", "feature": "일감호 야경 & 맛의거리"},
            {"id": "dongguk", "name": "동국대(충무로)", "region": "서울 중구", "feature": "남산 산책길 & 감성 술집"},
            {"id": "hongik", "name": "홍익대(상수)", "region": "서울 마포구", "feature": "예술적 감성 거리 & 클럽/라운지"},
            {"id": "kookmin", "name": "국민대(정릉)", "region": "서울 성북구", "feature": "북한산 숲뷰 카페"},
            {"id": "soongsil", "name": "숭실대(상도)", "region": "서울 동작구", "feature": "고민거리 없는 가성비 맛집"},
            {"id": "sejong", "name": "세종대(어린이대공원)", "region": "서울 광진구", "feature": "어린이대공원 피크닉"},
            {"id": "dankook", "name": "단국대(죽전)", "region": "경기 용인시", "feature": "보정동 카페거리"},
            {"id": "ajou", "name": "아주대(원천)", "region": "경기 수원시", "feature": "아주대 삼거리 핫플레이스"},
            {"id": "inha", "name": "인하대(인하문화거리)", "region": "인천 미추홀구", "feature": "인하대 후문 가성비 와플/술집"},
            {"id": "gachon", "name": "가천대(복정)", "region": "경기 성남시", "feature": "가천관 & 분당선 데이트"},
            {"id": "ewha-univ", "name": "이화여대(신촌)", "region": "서울 서대문구", "feature": "ECC & 베이커리 투어"},
            {"id": "sookmyung", "name": "숙명여대(청파)", "region": "서울 용산구", "feature": "청파동 아기자기한 디저트"},
            {"id": "sungshin", "name": "성신여대(돈암)", "region": "서울 성북구", "feature": "로데오거리 & 소품샵"},
            {"id": "seoul-women", "name": "서울여대(공릉)", "region": "서울 노원구", "feature": "공리단길 기찻길 산책"},
            {"id": "dongduk", "name": "동덕여대(월곡)", "region": "서울 성북구", "feature": "월곡 오거리 감성 밥집"},
            {"id": "pusan-univ", "name": "부산대(장전)", "region": "부산 금정구", "feature": "부산대 앞 젊음의거리"},
            {"id": "knu", "name": "경북대(북문)", "region": "대구 북구", "feature": "경북대 북문 로데오"},
            {"id": "cnu", "name": "충남대(궁동)", "region": "대전 유성구", "feature": "궁동 로데오거리 펍"},
            {"id": "jnu", "name": "전남대(후문)", "region": "광주 북구", "feature": "전대후문 메가상권"},
            {"id": "jbnu", "name": "전북대(구정문)", "region": "전북 전주시", "feature": "전북대 덕진공원 연꽃"},
            {"id": "cbnu", "name": "충북대(중문)", "region": "충북 청주시", "feature": "충대 중문 활기찬 거리"},
            {"id": "kangwon-univ", "name": "강원대(후문)", "region": "강원 춘천시", "feature": "축제거리 & 닭갈비 데이트"},
            {"id": "jeju-univ", "name": "제주대(아라)", "region": "제주 제주시", "feature": "아라동 감성 카페"},
            {"id": "kaist", "name": "KAIST(어은동)", "region": "대전 유성구", "feature": "어은동 유등천 산책"},
            {"id": "postech", "name": "포항공대(효자동)", "region": "경북 포항시", "feature": "효자동 철길숲 데이트"},
            {"id": "pknu", "name": "부경대(대연)", "region": "부산 남구", "feature": "경성대·부경대 먹자골목"},
            {"id": "ynu", "name": "영남대(오렌지거리)", "region": "경북 경산시", "feature": "영대 오렌지골목"},
            {"id": "donga-univ", "name": "동아대(하단)", "region": "부산 사하구", "feature": "에덴공원 & 하단 오거리"},
            {"id": "kyungsung", "name": "경성대(대연)", "region": "부산 남구", "feature": "문화골목 & 소극장"},
            {"id": "chosun-univ", "name": "조선대(후문)", "region": "광주 동구", "feature": "장미원 & 동명동 카페거리"},
            {"id": "konyang-univ", "name": "건양대(관저)", "region": "대전 서구", "feature": "마치광장 버스킹"},
            {"id": "hanbat", "name": "한밭대(덕명)", "region": "대전 유성구", "feature": "수통골 등산로 브런치"},
            {"id": "catholic-univ", "name": "가톨릭대(역곡)", "region": "경기 부천시", "feature": "역곡 상상시장 데이트"},
            {"id": "myongji-univ", "name": "명지대(남가좌)", "region": "서울 서대문구", "feature": "명지대 앞 떡볶이&카페"},
            {"id": "sangmyung", "name": "상명대(평창)", "region": "서울 종로구", "feature": "부암동 자하문 카페거리"},
            {"id": "kwangwoon", "name": "광운대(월계)", "region": "서울 노원구", "feature": "광운대역 비마관 맛집"},
            {"id": "hansung", "name": "한성대(삼선)", "region": "서울 성북구", "feature": "성곽길 낙산 야경"},
            {"id": "incheon-univ", "name": "인천대(송도)", "region": "인천 연수구", "feature": "송도 솔찬공원 바다뷰"},
            {"id": "kyonggi-univ", "name": "경기대(연무)", "region": "경기 수원시", "feature": "광교산 입구 보리밥&카페"},
            {"id": "kpu", "name": "한국공학대(정왕)", "region": "경기 시흥시", "feature": "옥구공원 & 시화호 드라이브"},

            # [전국 광역시 핫플레이스 50곳]
            {"id": "busan-seomyeon", "name": "부산 서면", "region": "부산 부산진구", "feature": "쥬디스태화 & 핫한 술집"},
            {"id": "busan-jeonpo", "name": "부산 전포 카페거리", "region": "부산 부산진구", "feature": "감성 소품샵 & 디저트"},
            {"id": "busan-gwangan", "name": "부산 광안리", "region": "부산 수영구", "feature": "광안대교 드론쇼 & 오션뷰 와인바"},
            {"id": "busan-haeundae", "name": "부산 해운대", "region": "부산 해운대구", "feature": "해리단길 & 달맞이길 드라이브"},
            {"id": "busan-nampo", "name": "부산 남포동", "region": "부산 중구", "feature": "자갈치 & BIFF거리 씨앗호떡"},
            {"id": "busan-dongnae", "name": "부산 동래역", "region": "부산 동래구", "feature": "메가마트 뒤 2차 포차"},
            {"id": "busan-yeongdo", "name": "부산 영도 흰여울", "region": "부산 영도구", "feature": "흰여울문화마을 바다뷰 카페"},
            {"id": "busan-gijang", "name": "부산 기장 오시리아", "region": "부산 기장군", "feature": "롯데월드 & 아난티 힐튼 브런치"},
            {"id": "busan-songjeong", "name": "부산 송정해수욕장", "region": "부산 해운대구", "feature": "서핑 & 문토스트 야경"},
            {"id": "busan-centum", "name": "부산 센텀시티", "region": "부산 해운대구", "feature": "신세계 스파랜드 & 영화의전당"},
            {"id": "daegu-dongseongro", "name": "대구 동성로", "region": "대구 중구", "feature": "스파크랜드 & 반월당 핫플"},
            {"id": "daegu-gyodong", "name": "대구 교동", "region": "대구 중구", "feature": "레트로 감성 펍 & LP바"},
            {"id": "daegu-suseong", "name": "대구 수성못", "region": "대구 수성구", "feature": "수성못 유람선 & 루프탑 카페"},
            {"id": "daegu-apsan", "name": "대구 앞산 카페거리", "region": "대구 남구", "feature": "전망대 케이블카 & 브런치"},
            {"id": "daegu-kimkwangseok", "name": "대구 김광석거리", "region": "대구 중구", "feature": "벽화거리 & 어쿠스틱 버스킹"},
            {"id": "daejeon-dunsan", "name": "대전 둔산동", "region": "대전 서구", "feature": "갤러리아 타임월드 & 감성 바"},
            {"id": "daejeon-galma", "name": "대전 갈마동(갈리단길)", "region": "대전 서구", "feature": "감성 주택가 일식당 & 와인"},
            {"id": "daejeon-bongmyeong", "name": "대전 유성 봉명동", "region": "대전 유성구", "feature": "온천 족욕체험 & 매드블럭 펍"},
            {"id": "daejeon-eunhaeng", "name": "대전 은행동 으능정이", "region": "대전 중구", "feature": "성심당 본점 & 스카이로드"},
            {"id": "daejeon-soje", "name": "대전 소제동", "region": "대전 동구", "feature": "철도관사촌 레트로 카페"},
            {"id": "gwangju-sangmu", "name": "광주 상무지구", "region": "광주 서구", "feature": "시청 앞 번화가 & 라운지"},
            {"id": "gwangju-dongmyeong", "name": "광주 동명동(동리단길)", "region": "광주 동구", "feature": "ACC 국립아시아문화전당 & 카페"},
            {"id": "gwangju-cheomdan", "name": "광주 첨단 시리단길", "region": "광주 광산구", "feature": "포플레이 & 원더풀 첨단 맛집"},
            {"id": "gwangju-gusi", "name": "광주 구시청", "region": "광주 동구", "feature": "충장로 & 젊음의 포차"},
            {"id": "gwangju-suwan", "name": "광주 수완지구", "region": "광주 광산구", "feature": "호수공원 & 롯데아울렛"},
            {"id": "ulsan-samsan", "name": "울산 삼산동", "region": "울산 남구", "feature": "현대백화점 & 롯데관람차 뷰"},
            {"id": "ulsan-seongnam", "name": "울산 성남동 젊음의거리", "region": "울산 중구", "feature": "문화의거리 & 큐빅광장"},
            {"id": "ulsan-ilsan", "name": "울산 일산지(일산해수욕장)", "region": "울산 동구", "feature": "대왕암공원 출렁다리"},
            {"id": "changwon-sangnam", "name": "창원 상남동", "region": "경남 창원시", "feature": "분수광장 & 전국 최대 상권"},
            {"id": "changwon-gwisan", "name": "창원 귀산동", "region": "경남 창원시", "feature": "마창대교 뷰 푸드트럭 & 카페"},
            {"id": "changwon-yongho", "name": "창원 가로수길(용호동)", "region": "경남 창원시", "feature": "메타세콰이어 & 브런치"},
            {"id": "pohang-yeongildae", "name": "포항 영일대해수욕장", "region": "경북 포항시", "feature": "영일대 해상누각 & 조개구이"},
            {"id": "pohang-space-walk", "name": "포항 스페이스워크", "region": "경북 포항시", "feature": "환호공원 스카이워크 야경"},
            {"id": "cheonan-buldang", "name": "천안 신불당", "region": "충남 천안시", "feature": "신불당 카페거리 & 감성 이자카야"},
            {"id": "cheonan-dujeong", "name": "천안 두정동", "region": "충남 천안시", "feature": "먹자골목 & 24시간 핫플"},
            {"id": "cheongju-yullyang", "name": "청주 율량동", "region": "충북 청주시", "feature": "그랜드플라자 뒤 감성 펍"},
            {"id": "cheongju-seongan", "name": "청주 성안길", "region": "충북 청주시", "feature": "로데오거리 & 쫄쫄호떡"},
            {"id": "cheongju-dongnam", "name": "청주 동남지구", "region": "충북 청주시", "feature": "신흥 상권 핫플레이스"},
            {"id": "jeonju-gaekridan", "name": "전주 객리단길", "region": "전북 전주시", "feature": "다가동 감성 맛집 & 펍"},
            {"id": "jeonju-hanok", "name": "전주 한옥마을", "region": "전북 전주시", "feature": "한복대여 & 경기전 데이트"},
            {"id": "jeonju-shinsigaji", "name": "전주 신시가지", "region": "전북 전주시", "feature": "도청 앞 번화가 & 클럽/라운지"},
            {"id": "yeosu-romantic-pocha", "name": "여수 낭만포차", "region": "전남 여수시", "feature": "거북선대교 하멜등대 야경"},
            {"id": "yeosu-isunshin", "name": "여수 이순신광장", "region": "전남 여수시", "feature": "딸기모찌 & 해양공원 산책"},
            {"id": "suncheon-jorye", "name": "순천 조례동", "region": "전남 순천시", "feature": "순천 핫플레이스 상권"},
            {"id": "jeju-nohyeong", "name": "제주 노형동·연동", "region": "제주 제주시", "feature": "드림타워 & 누웨마루거리"},
            {"id": "jeju-aewol", "name": "제주 애월 한담해변", "region": "제주 제주시", "feature": "노을 카약 & 해변 카페거리"},
            {"id": "jeju-woljeong", "name": "제주 월정리·구좌", "region": "제주 제주시", "feature": "풍차 바다뷰 & 감성 소품샵"},
            {"id": "jeju-seogwipo", "name": "제주 서귀포 올레시장", "region": "제주 서귀포시", "feature": "이중섭거리 & 야시장 먹거리"},
            {"id": "chuncheon-gubongsan", "name": "춘천 구봉산 전망대", "region": "강원 춘천시", "feature": "스카이워크 & 산토리니 카페"},
            {"id": "gangneung-anjin", "name": "강릉 안목해변", "region": "강원 강릉시", "feature": "강릉 커피거리 & 오션뷰 데이트"}
        ]
        return spots

    # =========================================================================
    # 💬 2. 국내 20대 초고검색량 테마 (여성 실검 1위)
    # =========================================================================
    @staticmethod
    def get_domestic_themes() -> List[Dict[str, str]]:
        return [
            {"id": "popup-store", "title": "실시간 핫플 팝업스토어 & 예약 꿀팁", "tag": "팝업스토어"},
            {"id": "aesthetic-cafe", "title": "인스타 감성 인생샷 디저트 카페 리스트", "tag": "감성카페"},
            {"id": "terrace-brunch", "title": "주말 낮 여유로운 테라스 브런치 맛집", "tag": "브런치"},
            {"id": "mood-winebar", "title": "조용하고 분위기 좋은 2차 감성 와인바", "tag": "와인바"},
            {"id": "rainy-indoor", "title": "비 오는 날 로맨틱 실내 데이트 코스", "tag": "실내데이트"},
            {"id": "pasta-dining", "title": "소개팅 1차 분위기 보장 파스타 맛집", "tag": "소개팅맛집"},
            {"id": "private-room", "title": "서로에게 집중하는 프라이빗 룸식당", "tag": "룸식당"},
            {"id": "nightview-drive", "title": "야경 뷰가 예쁜 심야 드라이브 명소", "tag": "야경드라이브"},
            {"id": "first-talk-cheat", "title": "첫 만남 어색함 제로 100% 호감 대화법", "tag": "소개팅대화"},
            {"id": "kakaotalk-signal", "title": "남자가 반했을 때 카톡 답장 텀 & 호감 시그널", "tag": "카톡심리"},
            {"id": "reading-ignore", "title": "읽씹 안읽씹 남자 속마음과 자연스러운 대처법", "tag": "연애심리"},
            {"id": "dutch-manner", "title": "센스 있는 더치페이 매너 & 호감 표현법", "tag": "데이트매너"},
            {"id": "outfit-lookbook", "title": "2030 여친룩 꾸안꾸 소개팅 코디 룩북", "tag": "소개팅룩"},
            {"id": "perfume-ranking", "title": "남자들이 심쿵하는 20대 여자 인생 향수", "tag": "향수추천"},
            {"id": "ai-photo-snap", "title": "셀카 1장으로 청담동 스냅 화보 만들기", "tag": "AI인생화보"},
            {"id": "after-success", "title": "당일 귀가 후 100% 성사되는 애프터 멘트", "tag": "애프터신청"},
            {"id": "threefter-propose", "title": "삼프터 고백 타이밍 & 심쿵 시그널", "tag": "고백타이밍"},
            {"id": "afterwork-date", "title": "퇴근 후 직장인 평일 저녁 번개 데이트", "tag": "직장인데이트"},
            {"id": "exhibition-class", "title": "어색함 풀리는 전시회 & 원데이클래스", "tag": "이색데이트"},
            {"id": "balance-game", "title": "가치관 통하는 연애 밸런스게임 질문 모음", "tag": "밸런스게임"}
        ]

    # =========================================================================
    # 🔮 3. 16×16 MBTI 1:1 전수 궁합 (256개)
    # =========================================================================
    @staticmethod
    def get_mbti_list() -> List[str]:
        return ["ENFP", "ENFJ", "ENTP", "ENTJ", "ESFP", "ESFJ", "ESTP", "ESTJ",
                "INFP", "INFJ", "INTP", "INTJ", "ISFP", "ISFJ", "ISTP", "ISTJ"]

    # =========================================================================
    # 🇯🇵 4. 일본 여성 초고검색량 테마 (1,000개)
    # =========================================================================
    @staticmethod
    def get_japanese_themes() -> List[Dict[str, str]]:
        themes = []
        categories = [
            ("seoul-cafe", "ソウル カフェ 巡り おすすめ 2026", "弘大・聖水・延南のインスタ映えカフェ完全ガイド"),
            ("seongsu-shopping", "聖水(ソンス) 雑貨屋 & コスメ ショッピング", "今ソウルで一番ホットな聖水洞おすすめルート"),
            ("nikkan-couple", "日韓カップル 出会い方 & 安全なアプリ", "韓国語が話せなくても繋がるリアルタイム字幕マッチング"),
            ("korean-guy-signals", "韓国男子 恋愛心理 & LINE返信スピード", "韓国人男性が本気で好きな人に見せる脈ありサイン"),
            ("solo-female-travel", "ソウル 一人旅 女子 安全 ガイド", "女性一人でも安心！現地のカフェ友達・写真メイト募集"),
            ("hongdae-hotplace", "弘大(ホンデ) 夜遊び & おすすめバー", "現地女子が教える安全でおしゃれな弘大ナイトスポット"),
            ("korean-makeup", "韓国コスメ おすすめ & パーソナルカラー診断", "オリーブヤング人気コスメと韓国トレンドメイク"),
            ("k-drama-romance", "リアル韓国ドラマ体験 & 現地人との出会い", "字幕付きビデオ通話で憧れの韓国男子と会話するコツ"),
            ("hanriver-picnic", "漢江(ハンガン) ラーメン & ピクニック デート", "汝矣島・トゥクソムで楽しむ韓国女子旅ピクニック"),
            ("language-exchange", "韓国語 勉強 & 日韓言語交換 友達作り", "初心者でも安心！リアルタイム翻訳アプリAURA活用法")
        ]
        # 100개 주요 스팟/상황 × 10개 테마 = 1,000개
        for i in range(1, 101):
            for cat_id, cat_title, cat_desc in categories:
                themes.append({
                    "slug": f"ja-seoul-{cat_id}-spot{i:03d}",
                    "title": f"【2026最新】{cat_title} (Spot #{i})",
                    "desc": f"{cat_desc}。現地カフェ友達探しや安全な出会いはAURAで！",
                    "lang": "ja"
                })
        return themes[:1000]

    # =========================================================================
    # 🇺🇸 5. 영미권/글로벌 여성 초고검색량 테마 (1,000개)
    # =========================================================================
    @staticmethod
    def get_english_themes() -> List[Dict[str, str]]:
        themes = []
        categories = [
            ("solo-female-seoul", "Solo Female Travel in Seoul: Ultimate Safe Guide", "Safe neighborhoods, cafe mates, and photo spots in Seoul 2026"),
            ("aesthetic-cafes", "Best Aesthetic Cafes in Seongsu & Hongdae", "Top Instagrammable cafes verified by local Korean girls"),
            ("safe-local-friends", "How to Meet Verified Korean Friends Safely", "100% Real-time Translated live video chat with local locals"),
            ("k-dating-culture", "Korean Dating Culture: Rules & Texting Habits", "What guys mean by reply times and how K-Dating actually works"),
            ("language-school-lounge", "Ewha / Yonsei / SNU Expat Student Meetups", "Safe social lounge for international girls studying in Korea"),
            ("seoul-nightlife-safe", "Safe Nightlife & Rooftop Bars in Itaewon / Hongdae", "Solo-friendly bars and trusted meetups with zero creeps"),
            ("k-beauty-makeover", "K-Beauty Skincare Routine & Personal Color Analysis", "Top aesthetic clinics and makeup spots in Gangnam / Sinsa"),
            ("k-drama-romance", "Real K-Drama Style Romance Experience in Seoul", "Chat with sweet Korean locals with live Netflix-style subtitles"),
            ("han-river-cycling", "Han River Sunset Picnic & Instant Ramen Guide", "Where to rent bikes, mats, and meet friendly local picnic buddies"),
            ("travel-dating-apps", "Safest Dating & Social Apps for Foreign Girls in Korea", "Why AURA's 50:50 gender ratio & 500m jittering makes you safe")
        ]
        # 100개 주요 스팟/상황 × 10개 테마 = 1,000개
        for i in range(1, 101):
            for cat_id, cat_title, cat_desc in categories:
                themes.append({
                    "slug": f"en-seoul-{cat_id}-spot{i:03d}",
                    "title": f"[2026 Guide] {cat_title} (Spot #{i})",
                    "desc": f"{cat_desc}. Connect with sweet local friends safely on AURA!",
                    "lang": "en"
                })
        return themes[:1000]

    # =========================================================================
    # 🚀 6. 7,000개 초대형 SEO 팡 빌드 & sitemap_aura.xml 생성
    # =========================================================================
    def build_7000_sitemap_and_pages(self) -> Dict[str, Any]:
        """총 7,000개 초고검색량 URL 및 정적 랜딩 페이지, sitemap_aura.xml 생성"""
        logger.info("🎬 [AuraSEOEngine] 7,000개 여성 타겟 초고검색량 색인 팡 빌드 시작...")
        sitemap_urls = []

        # 0. 메인 & 라운지 & 기본 게이트웨이
        sitemap_urls.append(f"{self.BASE_DOMAIN}")
        sitemap_urls.append(f"{self.BASE_DOMAIN}/lounge")
        sitemap_urls.append(f"{self.BASE_DOMAIN}/mbti")
        sitemap_urls.append(f"{self.BASE_DOMAIN}/dating-tips")
        sitemap_urls.append(f"{self.BASE_DOMAIN}/hotplace")
        self._render_main_index()

        # ---------------------------------------------------------------------
        # 🇰🇷 [1] 국내 2030 여성 핫플 × 20대 테마 = 4,000개
        # ---------------------------------------------------------------------
        hotspots = self.get_domestic_hotspots()
        themes = self.get_domestic_themes()

        domestic_rendered = 0
        for spot in hotspots:
            for th in themes:
                slug = f"hotplace-{spot['id']}-{th['id']}"
                target_url = f"{self.BASE_DOMAIN}/hotplace/{spot['id']}/{th['id']}"
                sitemap_urls.append(target_url)

                title = f"{spot['name']} {th['title']} | {spot['feature']}"
                self._render_domestic_page(slug, title, spot, th, target_url)
                domestic_rendered += 1

        logger.info(f"✅ [1/5] 국내 핫플 ✕ 테마 4,000개 URL 생성 완료 (누적: {len(sitemap_urls)}개)")

        # ---------------------------------------------------------------------
        # 🔮 [2] 16 × 16 MBTI 1:1 전수 궁합 = 256개
        # ---------------------------------------------------------------------
        mbti_list = self.get_mbti_list()
        for m1 in mbti_list:
            for m2 in mbti_list:
                slug = f"mbti-{m1.lower()}-{m2.lower()}"
                target_url = f"{self.BASE_DOMAIN}/mbti/{m1.lower()}-{m2.lower()}"
                sitemap_urls.append(target_url)

                title = f"{m1} 여자 ✕ {m2} 남자 연애 궁합 & 카톡 티키타카 공략법"
                self._render_mbti_page(slug, title, m1, m2, target_url)

        logger.info(f"✅ [2/5] 16×16 MBTI 1:1 궁합 256개 URL 생성 완료 (누적: {len(sitemap_urls)}개)")

        # ---------------------------------------------------------------------
        # 📺 [3] 연애 예능 & 현실 심리 롱테일 = 400개
        # ---------------------------------------------------------------------
        psych_topics = [
            "환승연애 카톡 대화법 분석", "나는솔로 데이트 심리 공략", "하트시그널 미묘한 호감 시그널",
            "남자가 반했을 때 카톡 답장 텀", "회피형 남자 vs 불안형 여자 심리", "짝사랑 포기해야 할 때 신호",
            "소개팅에서 도망치고 싶을 때 탈출법", "연애 밸런스게임 질문 100선", "썸 탈 때 안읽씹 대처 가이드",
            "남녀 50대50 성비 깨끗한 데이팅앱 비교"
        ]
        for i in range(1, 41):
            for idx, p_title in enumerate(psych_topics):
                slug = f"psychology-topic-{idx+1:02d}-{i:02d}"
                target_url = f"{self.BASE_DOMAIN}/dating-tips/psychology/{idx+1:02d}-{i:02d}"
                sitemap_urls.append(target_url)
                title = f"2026 {p_title} (심층 분석 #{i})"
                self._render_psych_page(slug, title, p_title, target_url)

        logger.info(f"✅ [3/5] 연애 심리 & 예능 400개 URL 생성 완료 (누적: {len(sitemap_urls)}개)")

        # ---------------------------------------------------------------------
        # 👗 [4] 2030 스타일/뷰티/AI인생화보 = 344개
        # ---------------------------------------------------------------------
        style_topics = [
            "20대 여자 인기 향수 순위 1위", "소개팅 꾸안꾸 여친룩 원피스 코디", "퍼스널컬러 웜톤 쿨톤 인생 립 추천",
            "셀카 1장으로 청담동 스냅 화보 만들기", "소개팅 전날 붓기 빼는 꿀팁", "인스타 스토리 감성 사진 구도",
            "하객룩 깔끔한 단아 스타일", "여자가 좋아하는 남자 댄디룩 스타일"
        ]
        for i in range(1, 44):
            for idx, s_title in enumerate(style_topics):
                if len(sitemap_urls) >= 5005:  # 국내 5,000개 + 기본 5개 맞춤
                    break
                slug = f"style-topic-{idx+1:02d}-{i:02d}"
                target_url = f"{self.BASE_DOMAIN}/dating-tips/style/{idx+1:02d}-{i:02d}"
                sitemap_urls.append(target_url)
                title = f"2026 {s_title} (에디터 추천 #{i})"
                self._render_style_page(slug, title, s_title, target_url)

        logger.info(f"✅ [4/5] 스타일 & AI화보 344개 URL 생성 완료 (국내 5,005개 완료!)")

        # ---------------------------------------------------------------------
        # 🇯🇵 [5-1] 일본 여성 초고검색량 = 1,000개
        # ---------------------------------------------------------------------
        ja_themes = self.get_japanese_themes()
        for item in ja_themes:
            target_url = f"{self.BASE_DOMAIN}/ja/{item['slug']}"
            sitemap_urls.append(target_url)
            self._render_japanese_page(item["slug"], item["title"], item["desc"], target_url)

        logger.info(f"✅ [5/5-1] 일본 2030 여성 타겟 1,000개 URL 생성 완료 (누적: {len(sitemap_urls)}개)")

        # ---------------------------------------------------------------------
        # 🇺🇸 [5-2] 영미권/글로벌 여성 초고검색량 = 1,000개
        # ---------------------------------------------------------------------
        en_themes = self.get_english_themes()
        for item in en_themes:
            target_url = f"{self.BASE_DOMAIN}/en/{item['slug']}"
            sitemap_urls.append(target_url)
            self._render_english_page(item["slug"], item["title"], item["desc"], target_url)

        logger.info(f"🎉 [총 7,005개 URL 생성 완료! (국내 5,005개 + 글로벌 2,000개)]")

        # ---------------------------------------------------------------------
        # 🗺️ sitemap_aura.xml 파일 쓰기
        # ---------------------------------------------------------------------
        self._write_sitemap(self.sitemap_file, sitemap_urls)
        logger.info(f"📁 [Aura Sitemaps] '{self.sitemap_file}' 저장 완료 (총 {len(sitemap_urls)}개 URL)")

        # ---------------------------------------------------------------------
        # ⚡ 실시간 색인 핑 전송 (Google Indexing API + Naver Search Advisor)
        # ---------------------------------------------------------------------
        from brands.aura.aura_search_indexing_hub import AuraSearchIndexingHub
        hub = AuraSearchIndexingHub()
        ping_res = hub.ping_google_search_console(sitemap_urls[:20])
        naver_res = hub.ping_naver_search_advisor(sitemap_urls[:20])

        return {
            "success": True,
            "brand": "aura",
            "total_urls": len(sitemap_urls),
            "domestic_urls": 5005,
            "global_urls": 2000,
            "sitemap_path": str(self.sitemap_file),
            "output_html_dir": str(self.output_dir),
            "indexing_results": {
                "google": ping_res,
                "naver": naver_res
            },
            "message": f"💖 [Aura] 국내 5,005개 + 글로벌 2,000개 (총 {len(sitemap_urls):,}개) 초대형 사이트맵 및 SEO 페이지 빌드 완료!"
        }

    GOOGLE_SITE_VERIFICATION = "IHFjD1HlX9qQLUbwjrKPVdADPnoqgmEqBML05pV4STs"
    NAVER_SITE_VERIFICATION = "bdfdbb49416330fed9984611756191930df7697f"

    # =========================================================================
    # 📄 7. HTML 렌더러 (오픈그래프, Schema.org, 전환 CTA 배너 탑재)
    # =========================================================================
    def _render_main_index(self):
        """메인 루트 랜딩 (소유권 인증 태그 100% 탑재)"""
        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AURA (아우라) - 국내 최초 50:50 황금 성비 &amp; 실시간 자막 AI 데이팅 라운지</title>
    <meta name="description" content="남탕 어플 NO! 1:1 남녀 50:50 성비 보장, 4개국어 실시간 자막 통역 영상통화, 500m 안심 지터링 보안. 2030 프리미엄 AI 데이팅 라운지 AURA">
    <link rel="canonical" href="{self.BASE_DOMAIN}">
    <meta name="google-site-verification" content="{self.GOOGLE_SITE_VERIFICATION}">
    <meta property="og:title" content="AURA - 50:50 남녀 성비 &amp; 프리미엄 AI 소개팅">
    <meta property="og:description" content="남탕 없는 깨끗한 라운지! 실시간 자막 영상통화로 국내외 친구를 만나보세요.">
    <meta property="og:url" content="{self.BASE_DOMAIN}">
    <meta property="og:image" content="https://aura-ai-dating.vercel.app/og-image.png">
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "WebSite",
      "name": "Aura AI Dating",
      "url": "{self.BASE_DOMAIN}",
      "description": "50:50 Gender Ratio Premium AI Dating Lounge"
    }}
    </script>
</head>
<body style="font-family:'Pretendard', sans-serif; background:#0F172A; color:#F8FAFC; padding:40px 20px; text-align:center;">
    <div style="max-width:680px; margin:0 auto; background:#1E293B; padding:40px 30px; border-radius:24px; border:1px solid #334155;">
        <span style="background:#FDF2F8; color:#DB2777; font-size:13px; font-weight:bold; padding:6px 16px; border-radius:30px;">💖 AURA OFFICIAL AI LOUNGE</span>
        <h1 style="font-size:26px; margin:20px 0 12px 0; color:#FFFFFF;">남녀 50:50 황금 성비 AI 데이팅 라운지</h1>
        <p style="color:#94A3B8; font-size:15px; line-height:1.6;">유령회원 없는 1:1 성비 보장 &amp; 4개국어 실시간 자막 영상통화</p>
        <div style="margin:30px 0;">
            <a href="{self.LANDING_URL}" style="display:inline-block; background:linear-gradient(135deg, #EC4899 0%, #DB2777 100%); color:#FFF; font-weight:bold; font-size:16px; padding:15px 36px; border-radius:40px; text-decoration:none; box-shadow:0 6px 20px rgba(236,72,153,0.35);">
                👉 AURA 라운지 입장하기
            </a>
        </div>
    </div>
</body>
</html>"""
        with open(self.output_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html)

    def _render_domestic_page(self, slug: str, title: str, spot: Dict[str, str], theme: Dict[str, str], url: str):
        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | AURA</title>
    <meta name="description" content="{spot['name']} {theme['title']} 완벽 가이드! {spot['feature']} 추천 및 취향 맞는 데이트 메이트 찾기">
    <link rel="canonical" href="{url}">
    <meta name="google-site-verification" content="{self.GOOGLE_SITE_VERIFICATION}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{spot['name']} {theme['title']} - 50:50 황금 성비 AI 데이팅 라운지 AURA">
    <meta property="og:url" content="{url}">
    <meta property="og:image" content="https://aura-ai-dating.vercel.app/og-image.png">
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "{title}",
      "description": "{spot['name']} {theme['title']} 실전 가이드",
      "url": "{url}",
      "publisher": {{"@type": "Organization", "name": "Aura AI Dating", "url": "https://aura-ai-dating.vercel.app"}}
    }}
    </script>
</head>
<body style="font-family:'Pretendard', sans-serif; background:#0F172A; color:#F8FAFC; padding:20px; line-height:1.7;">
    <div style="max-width:680px; margin:0 auto; background:#1E293B; padding:30px; border-radius:18px; border:1px solid #334155;">
        <span style="background:#FDF2F8; color:#DB2777; font-size:12px; font-weight:bold; padding:4px 12px; border-radius:20px;">💖 2030 핫플 ✕ {theme['tag']}</span>
        <h1 style="font-size:22px; margin:16px 0 12px 0; color:#FFFFFF;">{title}</h1>
        <p style="color:#94A3B8; font-size:14.5px;">📍 {spot['region']} {spot['name']} · {spot['feature']}</p>
        <div style="background:#0F172A; padding:20px; border-radius:12px; margin:20px 0; border:1px solid #334155;">
            <h3 style="color:#EC4899; margin-top:0;">✨ {spot['name']} {theme['title']} 핵심 포인트</h3>
            <p style="color:#CBD5E1; font-size:14px; margin:0;">
                {spot['name']}에서 즐기는 특별한 {theme['tag']} 코스! 분위기 좋은 공간에서 어색함 없이 자연스럽게 이어지는 설레는 시간을 경험해 보세요.
            </p>
        </div>
        <div style="background:linear-gradient(135deg, #FFF1F2 0%, #FDF2F8 100%); border-radius:16px; padding:24px; text-align:center; color:#4C0519; margin-top:30px;">
            <h3 style="margin:0 0 8px 0; color:#BE123C; font-size:17px;">💑 {spot['name']} 같이 갈 50:50 데이트 메이트 찾기</h3>
            <p style="font-size:13.5px; margin:0 0 16px 0;">남탕 어플 NO! 1:1 남녀 50:50 황금 성비 보장 & AI 매력 분석 라운지</p>
            <a href="{self.LANDING_URL}" style="display:inline-block; background:#DB2777; color:#FFF; font-weight:bold; padding:12px 28px; border-radius:30px; text-decoration:none;">AURA 프라이빗 라운지 둘러보기 👉</a>
        </div>
    </div>
</body>
</html>"""
        with open(self.output_dir / f"{slug}.html", "w", encoding="utf-8") as f:
            f.write(html)

    def _render_mbti_page(self, slug: str, title: str, m1: str, m2: str, url: str):
        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>{title} | AURA MBTI</title>
    <meta name="description" content="{m1} 여자와 {m2} 남자의 2026 실전 연애 궁합! 연락 스타일, 호감 시그널, 첫 만남 주의점">
    <link rel="canonical" href="{url}">
    <meta name="google-site-verification" content="{self.GOOGLE_SITE_VERIFICATION}">
</head>
<body style="font-family:'Pretendard', sans-serif; background:#0F172A; color:#F8FAFC; padding:20px;">
    <div style="max-width:680px; margin:0 auto; background:#1E293B; padding:30px; border-radius:18px;">
        <span style="background:#FDF2F8; color:#DB2777; font-size:12px; font-weight:bold; padding:4px 12px; border-radius:20px;">🔮 16×16 MBTI 연애 궁합</span>
        <h1 style="font-size:22px; margin:16px 0; color:#FFF;">{title}</h1>
        <p style="color:#94A3B8;">{m1} 성향과 {m2} 성향의 환상적인 케미스트리와 카톡 핑퐁 꿀팁을 확인하세요.</p>
        <div style="text-align:center; margin-top:30px; padding:20px; background:#FFF1F2; border-radius:14px; color:#BE123C;">
            <a href="{self.LANDING_URL}" style="background:#DB2777; color:#FFF; padding:10px 24px; border-radius:30px; text-decoration:none; font-weight:bold;">나랑 궁합 100% 맞는 사람 매칭하기 👉</a>
        </div>
    </div>
</body>
</html>"""
        with open(self.output_dir / f"{slug}.html", "w", encoding="utf-8") as f:
            f.write(html)

    def _render_psych_page(self, slug: str, title: str, topic: str, url: str):
        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>{title} | AURA 매거진</title>
    <link rel="canonical" href="{url}">
    <meta name="google-site-verification" content="{self.GOOGLE_SITE_VERIFICATION}">
</head>
<body style="font-family:sans-serif; background:#0F172A; color:#FFF; padding:20px;">
    <div style="max-width:680px; margin:0 auto; background:#1E293B; padding:25px; border-radius:16px;">
        <h1 style="font-size:20px; color:#EC4899;">{title}</h1>
        <p style="color:#94A3B8;">2030 리얼 연애 심리 분석 및 AI 카톡 분석 솔루션</p>
        <a href="{self.LANDING_URL}" style="display:inline-block; background:#DB2777; color:#FFF; padding:10px 20px; border-radius:20px; text-decoration:none; margin-top:15px;">AURA AI 카톡 분석 체험하기 👉</a>
    </div>
</body>
</html>"""
        with open(self.output_dir / f"{slug}.html", "w", encoding="utf-8") as f:
            f.write(html)

    def _render_style_page(self, slug: str, title: str, topic: str, url: str):
        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>{title} | AURA 스타일</title>
    <link rel="canonical" href="{url}">
    <meta name="google-site-verification" content="{self.GOOGLE_SITE_VERIFICATION}">
</head>
<body style="font-family:sans-serif; background:#0F172A; color:#FFF; padding:20px;">
    <div style="max-width:680px; margin:0 auto; background:#1E293B; padding:25px; border-radius:16px;">
        <h1 style="font-size:20px; color:#EC4899;">{title}</h1>
        <p style="color:#94A3B8;">청담동 스냅 무드 AI 인생 화보 및 2030 소개팅 코디 가이드</p>
        <a href="{self.LANDING_URL}" style="display:inline-block; background:#DB2777; color:#FFF; padding:10px 20px; border-radius:20px; text-decoration:none; margin-top:15px;">셀카 1장으로 AI 화보 만들기 👉</a>
    </div>
</body>
</html>"""
        with open(self.output_dir / f"{slug}.html", "w", encoding="utf-8") as f:
            f.write(html)

    def _render_japanese_page(self, slug: str, title: str, desc: str, url: str):
        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>{title} | AURA 韓国</title>
    <meta name="description" content="{desc}">
    <link rel="canonical" href="{url}">
    <meta name="google-site-verification" content="{self.GOOGLE_SITE_VERIFICATION}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:url" content="{url}">
</head>
<body style="font-family:'Pretendard', sans-serif; background:#0F172A; color:#F8FAFC; padding:20px; line-height:1.7;">
    <div style="max-width:680px; margin:0 auto; background:#1E293B; padding:30px; border-radius:18px; border:1px solid #334155;">
        <span style="background:#FDF2F8; color:#DB2777; font-size:12px; font-weight:bold; padding:4px 12px; border-radius:20px;">🇯🇵 日韓カップル & ソウル女子旅</span>
        <h1 style="font-size:21px; margin:16px 0 12px 0; color:#FFFFFF;">{title}</h1>
        <p style="color:#CBD5E1; font-size:14.5px;">{desc}</p>
        <div style="background:linear-gradient(135deg, #FFF1F2 0%, #FDF2F8 100%); border-radius:16px; padding:24px; text-align:center; color:#4C0519; margin-top:30px;">
            <h3 style="margin:0 0 8px 0; color:#BE123C; font-size:16px;">✨ 韓国語が話せなくても大丈夫！リアルタイム字幕ビデオ通話</h3>
            <p style="font-size:13px; margin:0 0 16px 0;">女性専用VIPフリーパス & 映画のような字幕で韓国人の友達と繋がるAURA</p>
            <a href="{self.LANDING_URL}" style="display:inline-block; background:#DB2777; color:#FFF; font-weight:bold; padding:12px 28px; border-radius:30px; text-decoration:none;">AURAを無料で体験する 👉</a>
        </div>
    </div>
</body>
</html>"""
        with open(self.output_dir / f"{slug}.html", "w", encoding="utf-8") as f:
            f.write(html)

    def _render_english_page(self, slug: str, title: str, desc: str, url: str):
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title} | AURA Seoul</title>
    <meta name="description" content="{desc}">
    <link rel="canonical" href="{url}">
    <meta name="google-site-verification" content="{self.GOOGLE_SITE_VERIFICATION}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:url" content="{url}">
</head>
<body style="font-family:'Pretendard', sans-serif; background:#0F172A; color:#F8FAFC; padding:20px; line-height:1.7;">
    <div style="max-width:680px; margin:0 auto; background:#1E293B; padding:30px; border-radius:18px; border:1px solid #334155;">
        <span style="background:#FDF2F8; color:#DB2777; font-size:12px; font-weight:bold; padding:4px 12px; border-radius:20px;">🇺🇸 Solo Female in Seoul & Verified Local Friends</span>
        <h1 style="font-size:21px; margin:16px 0 12px 0; color:#FFFFFF;">{title}</h1>
        <p style="color:#CBD5E1; font-size:14.5px;">{desc}</p>
        <div style="background:linear-gradient(135deg, #FFF1F2 0%, #FDF2F8 100%); border-radius:16px; padding:24px; text-align:center; color:#4C0519; margin-top:30px;">
            <h3 style="margin:0 0 8px 0; color:#BE123C; font-size:16px;">💕 The Safest Way for International Girls to Meet Local Friends</h3>
            <p style="font-size:13px; margin:0 0 16px 0;">100% Real-time AI translated video chat like Netflix subtitles with 500m jittered security.</p>
            <a href="{self.LANDING_URL}" style="display:inline-block; background:#DB2777; color:#FFF; font-weight:bold; padding:12px 28px; border-radius:30px; text-decoration:none;">Explore AURA Private Lounge 👉</a>
        </div>
    </div>
</body>
</html>"""
        with open(self.output_dir / f"{slug}.html", "w", encoding="utf-8") as f:
            f.write(html)

    # =========================================================================
    # 🗺️ 8. XML Sitemap 생성기
    # =========================================================================
    def _write_sitemap(self, path: Path, urls: List[str]):
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for u in urls:
            escaped_u = saxutils.escape(u)
            xml += f'  <url>\n    <loc>{escaped_u}</loc>\n    <changefreq>daily</changefreq>\n    <priority>0.9</priority>\n  </url>\n'
        xml += '</urlset>'
        with open(path, "w", encoding="utf-8") as f:
            f.write(xml)


if __name__ == "__main__":
    engine = AuraSEOEngine()
    result = engine.build_7000_sitemap_and_pages()
    print("\n" + "=" * 60)
    print(f"🎉 {result['message']}")
    print(f"  - 총 생성 URL: {result['total_urls']:,}개")
    print(f"  - 🇰🇷 국내 2030 여성 타겟: {result['domestic_urls']:,}개")
    print(f"  - 🌐 외국인 여성 글로벌 타겟: {result['global_urls']:,}개")
    print(f"  - 🗺️ 사이트맵 파일: {result['sitemap_path']}")
    print("=" * 60)
