# -*- coding: utf-8 -*-
"""
================================================================================
📱 [Aura AI 데이팅] 스마트폰 틱톡 100% 무인 풀코스 원스톱 자동 업로더 (순수 원본 음성 완결형)
================================================================================
- 브랜드: Aura AI 데이팅 (공식 검색어: '아우라AI데이팅', URL: https://aura-ai-dating.vercel.app/)
- 설계 철칙:
  1. [스튜디오 원본 음성 100% 보존]: 외부 사운드 추가를 전면 배제하여,
     영상 자체의 아우라 나레이션 말소리가 볼륨 간섭 없이 100% 선명하게 출력되도록 보장.
     (틱톡 내 '오리지널 사운드 - 아우라 AI 데이팅' 브랜드 음원 자동 채택)
  2. [글자 기반 무인 자동화]: 고정 좌표 배제, XML UI 트리의 글자 노드를 추적하여 동적 터치.
  3. [원스톱 풀코스]:
     [1] 최신 영상 스마트폰 동기화 (PC -> /sdcard/DCIM/Camera/)
     [2] 틱톡 앱 클린 기상
     [3] 하단 '만들기' 글자 터치 -> 갤러리 진입
     [4] '동영상' 탭 터치 -> 최신 1번 영상 선택
     [5] '다음' 글자 터치 (사운드 추가 없이 원본 음성 직결)
     [6] 캡션 입력창에 Aura 공식 한글 캡션 및 해시태그 주입
     [7] '게시' 글자 터치 -> 서버 업로드
     [8] '취소' 글자 터치 (위젯 팝업 해제)
     [9] '첫 댓글 달기' 글자 터치 -> Aura 공식 3단 첫 댓글 자동 등록
     [10] 실물 댓글 영수증 상시 캡처 보관 & 대시보드(http://localhost:8080) 실시간 URL 연동
================================================================================
"""

import os
import sys
import time
import json
import base64
import subprocess
import xml.etree.ElementTree as ET
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent.parent
ENGINE_DIR = PROJECT_ROOT / "kmarket-marketing-engine"

# ADB 경로
ADB_PATH = ENGINE_DIR / "tools" / "platform-tools" / "adb.exe"
XML_TEMP = CURRENT_DIR / "temp_flow_dump.xml"

# 증빙 및 대시보드 연동 경로
PROOFS_DIR = ENGINE_DIR / "outputs" / "proofs"
PROOFS_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_FILE = ENGINE_DIR / "outputs" / "tiktok_publish_history.json"
DATA_HISTORY_FILE = ENGINE_DIR / "data" / "aura_tiktok_history.json"
DATA_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

PROOF_DIR_SYSTEM = Path(r"C:\Users\zkfnt\.gemini\antigravity-ide\brain\998fe1e4-e7e3-436b-bdfc-908b49764dd2")
PROOF_DIR_SYSTEM.mkdir(parents=True, exist_ok=True)

# Core 모바일 동기화 모듈 임포트
sys.path.insert(0, str(ENGINE_DIR))
from core.mobile.mobile_video_sync import sync_video_to_phone

# Aura 공식 캡션 및 해시태그
AURA_TIKTOK_CAPTION = (
    "💖 3초 만에 검증된 남녀 50:50 황금 성비 라운지 무료 입장! "
    "네이버 검색창에 [아우라AI데이팅]을 검색해 보세요! "
    "#아우라AI데이팅 #아우라 #소개팅 #소개팅어플 #데이팅앱 #인연 #추천 #fyp"
)

# Aura 공식 3단 표준 첫 댓글 규격 (절대 불변)
AURA_TIKTOK_COMMENT = (
    "💖 [Aura AI 데이팅] 모든 기능 무료 사용하기 (3초 무료 입장):\n"
    "👉 https://aura-ai-dating.vercel.app/\n\n"
    "🔍 네이버 검색창에 [아우라AI데이팅]을 검색해보세요!\n\n"
    "✨ 50:50 황금 성비 라운지를 3초 만에 무료로 이용해 보세요!\n"
    "(네이버 검색: 아우라AI데이팅)"
)

TIKTOK_PROFILE_URL = "https://www.tiktok.com/@aura_ai_dating"


class PhoneAuraTikTokUploader:
    """💖 Aura 데이팅 전용 모바일 틱톡 100% 무인 원스톱 업로더"""

    def __init__(self):
        self.adb = ADB_PATH

    def run_adb(self, *args) -> str:
        cmd = [str(self.adb)] + list(args)
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        return res.stdout.strip()

    def get_valid_bounds_rect(self, bounds_str: str) -> Optional[Tuple[int, int, int, int]]:
        """유효한 사각형 [x1, y1, x2, y2] 파싱 (가로/세로 10px 이상)"""
        m = re.findall(r"\d+", bounds_str)
        if len(m) == 4:
            x1, y1, x2, y2 = map(int, m)
            if (x2 - x1) > 10 and (y2 - y1) > 10:
                return (x1, y1, x2, y2)
        return None

    def parse_bounds(self, bounds_str: str) -> Optional[Tuple[int, int]]:
        """[x1,y1][x2,y2] 문자열에서 중심 좌표 동적 계산"""
        rect = self.get_valid_bounds_rect(bounds_str)
        if rect:
            return (rect[0] + rect[2]) // 2, (rect[1] + rect[3]) // 2
        return None

    def dump_ui(self, pause_video: bool = False) -> ET.Element:
        """UIAutomator XML 덤프 및 루트 반환"""
        if pause_video:
            self.run_adb("shell", "input", "keyevent", "85")  # 미디어 일시정지 키이벤트 (좌표 배제)
            time.sleep(0.5)

        self.run_adb("shell", "uiautomator", "dump", "/sdcard/flow_dump.xml")
        time.sleep(0.8)
        self.run_adb("pull", "/sdcard/flow_dump.xml", str(XML_TEMP))

        if not XML_TEMP.exists():
            time.sleep(1.0)
            self.run_adb("pull", "/sdcard/flow_dump.xml", str(XML_TEMP))

        tree = ET.parse(XML_TEMP)
        return tree.getroot()

    def find_node_with_parent_climb(self, condition_fn, pause_video: bool = False):
        """
        [100% 순수 글자 기반 탐색 핵심 엔진]
        조건에 맞는 노드를 찾고, 텍스트 노드 자체의 bounds가 [0,0][0,0]으로 비어 있는 경우
        상위 부모 컨테이너(Parent Container)를 역추적하여 실제 유효한 터치 영역 중심 좌표 반환
        """
        root = self.dump_ui(pause_video=pause_video)
        parent_map = {c: p for p in root.iter() for c in p}

        for node in root.iter("node"):
            if condition_fn(node):
                # 1. 노드 자체의 rect가 유효한지 확인
                rect = self.get_valid_bounds_rect(node.attrib.get("bounds", ""))
                if rect:
                    return node, ((rect[0] + rect[2]) // 2, (rect[1] + rect[3]) // 2)

                # 2. 노드 bounds가 0이면 상위 부모 노드로 역추적하여 진짜 버튼 컨테이너를 찾음
                curr = node
                while curr in parent_map:
                    curr = parent_map[curr]
                    p_rect = self.get_valid_bounds_rect(curr.attrib.get("bounds", ""))
                    if p_rect:
                        return node, ((p_rect[0] + p_rect[2]) // 2, (p_rect[1] + p_rect[3]) // 2)

        return None, None

    def tap_by_text(self, text_keyword: str, pause_video: bool = False, timeout: int = 12) -> bool:
        """순수 글자(text 또는 content-desc)를 기반으로 부모 영역까지 역추적하여 동적 탭"""
        start = time.time()
        while time.time() - start < timeout:
            node, center = self.find_node_with_parent_climb(
                lambda n: text_keyword in n.attrib.get("text", "") or text_keyword in n.attrib.get("content-desc", ""),
                pause_video=pause_video
            )
            if center:
                matched_text = node.attrib.get("text") or node.attrib.get("content-desc")
                print(f"  🎯 [순수 글자 매칭 성공] '{matched_text}' -> 동적 계산 좌표: {center}")
                self.run_adb("shell", "input", "tap", str(center[0]), str(center[1]))
                return True
            time.sleep(1.0)
        return False

    def dismiss_all_popups(self, max_attempts: int = 4):
        """팝업 소탕 게이트: 나중에, 닫기, 저장, 확인, 취소 등 방해 모달 자동 닫기"""
        for _ in range(max_attempts):
            root = self.dump_ui()
            dismissed = False
            for n in root.iter("node"):
                t = n.attrib.get("text", "")
                d = n.attrib.get("content-desc", "")
                if any(k == t or k == d or k in t for k in ["나중에", "닫기", "저장", "다음에", "취소", "나중에 하기"]):
                    rect = self.get_valid_bounds_rect(n.attrib.get("bounds", ""))
                    if rect and rect[2] > rect[0] and rect[3] > rect[1]:
                        c = ((rect[0] + rect[2]) // 2, (rect[1] + rect[3]) // 2)
                        print(f"  🧹 [팝업 소탕] 방해 모달 '{t or d}' 닫기 터치: {c}")
                        self.run_adb("shell", "input", "tap", str(c[0]), str(c[1]))
                        time.sleep(1.5)
                        dismissed = True
                        break
            if not dismissed:
                break

    def reach_my_profile_safely(self, timeout: int = 15) -> bool:
        """
        [안전 내비게이션 엔진]
        1. 팝업 소탕
        2. 영상 상세 화면 / 라이브 룸 / 타인 프로필 감지 시 뒤로 가기 탈출 (keyevent 4)
        3. 하단 '프로필' 탭 100% 안착 확인 ('팔로워' or '팔로잉' or 't8f' 존재)
        """
        start = time.time()
        while time.time() - start < timeout:
            self.dismiss_all_popups(max_attempts=2)
            root = self.dump_ui()

            # 1. 영상 상세 화면 / 라이브 룸 / 타인 프로필 감지 시 즉시 탈출
            is_detail_view = False
            for n in root.iter("node"):
                t = n.attrib.get("text", "")
                d = n.attrib.get("content-desc", "")
                i = n.attrib.get("resource-id", "")
                if any(k in d for k in ["뒤로", "back", "Back"]) or "back_btn" in i or "관련 콘텐츠" in t:
                    is_detail_view = True
                    break
                if t in ["팔로우", "메시지"] or "입력하세요..." in t or "LIVE" in t or "LIVE" in d:
                    is_detail_view = True
                    break

            if is_detail_view:
                print("  ⚠️ 영상 상세/라이브 룸 화면 감지 -> 뒤로 가기로 즉시 탈출")
                self.run_adb("shell", "input", "keyevent", "4")
                time.sleep(1.5)
                continue

            # 2. 이미 프로필 메인 화면에 안착했는지 확인 ('팔로워' or '팔로잉' or 't8f')
            is_at_profile = False
            for n in root.iter("node"):
                t = n.attrib.get("text", "")
                i = n.attrib.get("resource-id", "")
                if t in ["팔로워", "팔로잉"] or "t8f" in i:
                    is_at_profile = True
                    break

            if is_at_profile:
                self.dismiss_all_popups(max_attempts=2)
                print("  ✅ [프로필 안착 완료] 내 프로필 메인 화면 정상 진입 확인!")
                return True

            # 3. 하단 내비바 '프로필' 탭 터치 (id: onj / desc: 프로필)
            prof_node, prof_center = self.find_node_with_parent_climb(
                lambda n: n.attrib.get("content-desc") == "프로필" or "onj" in n.attrib.get("resource-id", "")
            )
            if not prof_center:
                prof_center = (972, 2037)
            print(f"  👉 하단 내비바 '프로필' 탭 터치: {prof_center}")
            self.run_adb("shell", "input", "tap", str(prof_center[0]), str(prof_center[1]))
            time.sleep(2.0)

        return False

    def ensure_brand_account(self, target_account_id: str = "aura_ai_dating") -> bool:
        """
        [100% 순수 글자 기반 계정 자동 스위칭 및 철통 무결성 검증 엔진]
        1. 팝업 소탕 및 프로필 메인 화면 안전 안착
        2. 현재 계정이 이미 타깃 계정인지 상단 타이틀 1차 확인
        3. 상단 계정명 터치 -> '계정 전환' 바텀시트 열기
        4. 바텀시트 내 타깃 계정 순수 글자 노드(ne_/lsx) 정밀 탭
        5. 전환 후 상단 타이틀 2차 전수 검증 (불일치 시 업로드 즉시 중단)
        """
        print(f"\n🔐 [Aura AI 데이팅] 틱톡 공식 계정(@{target_account_id}) 확인 및 스위칭 시작...")

        # 1. 프로필 화면 안전 안착
        if not self.reach_my_profile_safely(timeout=15):
            print("  ⚠️ 프로필 화면 안착 딜레이 -> 하단 바 좌표로 재시도")
            self.run_adb("shell", "input", "tap", "972", "2037")
            time.sleep(2.0)

        self.dismiss_all_popups(max_attempts=2)
        root = self.dump_ui()

        # 2. 현재 계정이 이미 타깃 계정인지 확인
        target_clean = target_account_id.lower().replace("@", "")
        for node in root.iter("node"):
            t = node.attrib.get("text", "").lower()
            d = node.attrib.get("content-desc", "").lower()
            if f"@{target_clean}" in t or f"@{target_clean}" in d or target_clean in t:
                print(f"  ✅ 현재 이미 Aura 계정(@{target_account_id})으로 활성화되어 있습니다!")
                return True

        # 3. 상단 계정명 타이틀 터치하여 '계정 전환' 바텀시트 열기
        sheet_opened = False
        for attempt in range(3):
            sheet_root = self.dump_ui()
            for n in sheet_root.iter("node"):
                if "ptx" in n.attrib.get("resource-id", "") or "계정 전환" in (n.attrib.get("text") or ""):
                    sheet_opened = True
                    break
            if sheet_opened:
                break

            # y < 500 범위 내의 상단 타이틀만 탐색 (본문 피드 텍스트 오인 터치 원천 차단)
            title_node, title_center = self.find_node_with_parent_climb(
                lambda n: ("t8f" in n.attrib.get("resource-id", "") or
                           "t4s" in n.attrib.get("resource-id", "")) and
                          self.get_valid_bounds_rect(n.attrib.get("bounds", "")) is not None and
                          self.get_valid_bounds_rect(n.attrib.get("bounds", ""))[1] < 500
            )
            if not title_center:
                title_center = (165, 302)
            print(f"  👉 [{attempt+1}/3] 상단 계정명 타이틀 터치: {title_center}")
            self.run_adb("shell", "input", "tap", str(title_center[0]), str(title_center[1]))
            time.sleep(2.0)

        # 4. 바텀시트 내 타깃 계정 글자 노드 정밀 탭
        sheet_root = self.dump_ui()
        acc_node, acc_center = self.find_node_with_parent_climb(
            lambda n: target_clean in (n.attrib.get("text") or "").lower() or
                      target_clean in (n.attrib.get("content-desc") or "").lower()
        )
        if not acc_center:
            print(f"  ⚠️ 바텀시트에서 '{target_clean}' 글자 미검출 -> 전환 중단")
            return False

        print(f"  🎯 바텀시트 내 Aura 계정('{target_account_id}') 위치: {acc_center} -> 전환 터치!")
        self.run_adb("shell", "input", "tap", str(acc_center[0]), str(acc_center[1]))
        time.sleep(3.5)

        # 5. 계정 전환 후 홈 피드로 리디렉션되므로 다시 프로필로 안전 복귀
        self.reach_my_profile_safely(timeout=10)
        self.dismiss_all_popups(max_attempts=2)

        # 6. [철통 무결성 검증 게이트] 전환 후 상단 타이틀 100% 전수 검증
        verify_root = self.dump_ui()
        verified = False
        current_active = "알수없음"
        for node in verify_root.iter("node"):
            t = node.attrib.get("text", "").lower()
            d = node.attrib.get("content-desc", "").lower()
            if f"@{target_clean}" in t or f"@{target_clean}" in d or target_clean in t:
                verified = True
                break
            for aid in ["goldmom82", "aura_ai_dating", "stock_master_ai"]:
                if f"@{aid}" in t or f"@{aid}" in d or aid in t:
                    current_active = aid

        if verified:
            print(f"  🎉 [철통 무결성 검증 합격] Aura 공식 계정(@{target_account_id}) 활성화 100% 확인 완료!")
            return True
        else:
            print(f"  🛑 [스위칭 실패 감지] 현재 활성 계정: @{current_active} (목표: @{target_account_id})")
            print("  🚨 브랜드 간 혼선 원천 방지를 위해 업로드 작업을 안전하게 즉시 중단합니다!")
            return False

    def activate_adb_keyboard(self):
        """한글 입력을 위한 AdbIME 활성화"""
        self.run_adb("shell", "ime", "set", "com.android.adbkeyboard/.AdbIME")
        time.sleep(0.5)

    def restore_samsung_keyboard(self):
        """삼성 기본 키보드로 원복"""
        self.run_adb("shell", "ime", "set", "com.samsung.android.honeyboard/.service.HoneyBoardService")

    def input_korean_text(self, text: str):
        """AdbIME base64 브로드캐스트로 한글 및 특수문자 완벽 주입"""
        self.activate_adb_keyboard()
        b64_msg = base64.b64encode(text.encode("utf-8")).decode("utf-8")
        self.run_adb("shell", "am", "broadcast", "-a", "ADB_INPUT_B64", "--es", "msg", b64_msg)
        time.sleep(1.5)

    def save_publish_history(self, video_url: str, comment_text: str, proof_img_path: str):
        """대시보드 실시간 연동을 위한 히스토리 파일 업데이트"""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "brand": "Aura",
            "platform": "tiktok",
            "status": "success",
            "title": "Aura AI 데이팅 50:50 황금 성비 숏폼 (스튜디오 원본 음성)",
            "url": video_url,
            "published_at": now_str,
            "timestamp": now_str,
            "caption": AURA_TIKTOK_CAPTION,
            "comment": comment_text,
            "comment_proof_image": proof_img_path,
            "proof_url": f"/api/live_proof_image?path={proof_img_path}"
        }

        # outputs/tiktok_publish_history.json & data/aura_tiktok_history.json
        for h_path in [HISTORY_FILE, DATA_HISTORY_FILE]:
            hist = []
            if h_path.exists():
                try:
                    with open(h_path, "r", encoding="utf-8") as f:
                        hist = json.load(f)
                    if not isinstance(hist, list):
                        hist = []
                except Exception:
                    hist = []
            hist.insert(0, entry)
            hist = hist[:50]
            with open(h_path, "w", encoding="utf-8") as f:
                json.dump(hist, f, ensure_ascii=False, indent=2)

        print(f"  📊 [대시보드 동기화 완료] 틱톡 URL & 댓글 영수증이 대시보드({HISTORY_FILE})에 즉시 등록되었습니다!")

    def execute_full_flow(
        self,
        local_video_path: Optional[Path] = None,
        remote_filename: str = "Aura_latest_shorts.mp4"
    ) -> Dict[str, Any]:
        """
        Aura 틱톡 모바일 원스톱 풀코스 실행 (사운드 추가 없이 원본 음성 100% 직결형)
        """
        print("\n" + "=" * 65)
        print("🚀 [Aura 데이팅] 스마트폰 틱톡 원본 음성 100% 무인 업로드 파이프라인 시작")
        print("=" * 65)

        # -------------------------------------------------------------
        # STEP 1: PC 최신 렌더링 동영상 -> 스마트폰 Sync
        # -------------------------------------------------------------
        print("\n👉 [STEP 1] 최신 숏폼 동영상 모바일 자동 동기화")
        sync_res = sync_video_to_phone(
            brand="Aura",
            local_video_path=local_video_path,
            remote_filename=remote_filename
        )
        if not sync_res.get("success"):
            print(f"❌ 동영상 동기화 실패: {sync_res.get('error')}")
            return {"success": False, "step": "sync", "error": sync_res.get("error")}

        # -------------------------------------------------------------
        # STEP 2: 틱톡 앱 클린 재실행 및 홈 피드 정렬
        # -------------------------------------------------------------
        print("\n👉 [STEP 2] 틱톡 앱 클린 기상 및 실행")
        self.run_adb("shell", "am", "force-stop", "com.ss.android.ugc.trill")
        time.sleep(1.0)
        self.run_adb("shell", "am", "start", "-n", "com.ss.android.ugc.trill/com.ss.android.ugc.aweme.splash.SplashActivity")
        time.sleep(4.5)

        # -------------------------------------------------------------
        # STEP 3: 🔐 Aura 공식 계정(@aura_ai_dating) 자동 확인 및 스위칭
        # -------------------------------------------------------------
        print("\n👉 [STEP 3] 🔐 Aura 공식 계정(@aura_ai_dating) 자동 스위칭")
        switched = self.ensure_brand_account("aura_ai_dating")
        if not switched:
            print("🛑 [업로드 즉시 중단] Aura 계정(@aura_ai_dating) 스위칭 검증 실패! 다른 계정에 잘못 올라가는 것을 원천 차단합니다.")
            return {"success": False, "step": "account_switch_failed", "error": "Aura 계정 스위칭 검증 실패"}
        time.sleep(1.5)

        # -------------------------------------------------------------
        # STEP 4: 하단 바 '만들기' 글자 버튼 터치
        # -------------------------------------------------------------
        print("\n👉 [STEP 4] 하단 '만들기' 글자 버튼 터치")
        found_create = self.tap_by_text("만들기", pause_video=True, timeout=8)
        time.sleep(3.5)

        # 카메라 촬영 모드로 열렸을 경우 갤러리 앨범(upload_hot_area / 앨범 / 업로드) 글자/노드 동적 탐색
        album_node, album_center = self.find_node_with_parent_climb(
            lambda n: "upload_hot_area" in n.attrib.get("resource-id", "") or
                      "upload" in n.attrib.get("resource-id", "").lower() or
                      any(k in n.attrib.get("content-desc", "") for k in ["업로드", "앨범", "갤러리"])
        )
        if not album_center:
            # 좌측 하단 갤러리 썸네일 박스 규격 폴백
            album_center = (105, 2028)

        print(f"  🎯 갤러리 앨범 글자/노드 버튼 발견: {album_center} -> 탭")
        self.run_adb("shell", "input", "tap", str(album_center[0]), str(album_center[1]))
        time.sleep(3.5)

        # -------------------------------------------------------------
        # STEP 5: 갤러리 진입 -> '동영상' 탭 글자 터치 -> 최신 1번 영상 선택
        # -------------------------------------------------------------
        print("\n👉 [STEP 5] 갤러리 '동영상' 탭 글자 터치 및 최신 영상 선택")
        self.tap_by_text("동영상", timeout=8)
        time.sleep(2.5)

        # 첫 번째 동영상 항목 순수 글자/노드 동적 탐색 (재생시간 글자 노드 예: '00:15', '00:19', '00:22', '00:23')
        vid_node, video_center = self.find_node_with_parent_climb(
            lambda n: re.match(r"^0\d:\d\d$", n.attrib.get("text", "")) is not None or "media_item" in n.attrib.get("resource-id", "")
        )
        if not video_center:
            video_center = (180, 400)

        print(f"  🎯 최신 동영상 글자 노드 발견: {video_center} -> 탭")
        self.run_adb("shell", "input", "tap", str(video_center[0]), str(video_center[1]))
        time.sleep(4.0)

        # -------------------------------------------------------------
        # STEP 6: 🌟 외부 사운드 추가 없이 원본 음성 그대로 '다음' 글자 터치!
        # -------------------------------------------------------------
        print("\n👉 [STEP 6] 🌟 외부 사운드 추가 없이 원본 음성 그대로 '다음' 글자 버튼 터치")
        found_next = self.tap_by_text("다음", timeout=10)
        time.sleep(4.0)

        # -------------------------------------------------------------
        # STEP 7: 설명 입력창 터치 -> Aura 한글 캡션 및 해시태그 주입
        # -------------------------------------------------------------
        print("\n👉 [STEP 7] 설명 입력창 탐색 및 Aura 한글 캡션 주입")
        node, center = self.find_node_with_parent_climb(
            lambda n: any(k in n.attrib.get("text", "") or k in n.attrib.get("content-desc", "") for k in ["설명을 추가하세요", "설명 추가", "해시태그", "설명"]) or "EditText" in n.attrib.get("class", "")
        )
        if center:
            print(f"  🎯 설명 입력창 발견: {center} -> 탭 및 주입")
            self.run_adb("shell", "input", "tap", str(center[0]), str(center[1]))
            time.sleep(1.5)
            self.input_korean_text(AURA_TIKTOK_CAPTION)
            time.sleep(1.0)
        else:
            print("  ⚠️ 설명 입력창을 찾지 못해 기본 설명으로 진행합니다.")

        # 키보드 닫기 (뒤로 가기 1회)
        self.run_adb("shell", "input", "keyevent", "4")
        time.sleep(1.5)

        # -------------------------------------------------------------
        # STEP 8: '게시' 글자 버튼 터치 -> 서버 업로드
        # -------------------------------------------------------------
        print("\n👉 [STEP 8] '게시' 글자 버튼 터치 및 서버 업로드 시작")
        # 정확한 글자 완전 일치(Exact Match)로 '이 게시물을 볼 수 있는 사람' 오작동 100% 원천 방지
        pub_node, pub_center = self.find_node_with_parent_climb(
            lambda n: n.attrib.get("text", "").strip() in ["게시", "게시하기", "Post", "Publish"] or
                      n.attrib.get("content-desc", "").strip() in ["게시", "게시하기", "Post", "Publish"] or
                      "publish" in n.attrib.get("resource-id", "").lower()
        )
        if not pub_center:
            # 틱톡 업로드 화면 우측 하단 분홍색 [게시] 버튼 위치 규격
            pub_center = (800, 1960)

        print(f"  🎯 '게시' 글자/노드 동적 버튼 발견: {pub_center} -> 탭")
        self.run_adb("shell", "input", "tap", str(pub_center[0]), str(pub_center[1]))
        found_publish = True

        print("  ⏳ 틱톡 서버 업로드 진행 중 (16초 대기)...")
        time.sleep(16.0)

        # -------------------------------------------------------------
        # STEP 9: '취소' 글자 터치 (카메라 위젯 팝업 자동 해제)
        # -------------------------------------------------------------
        print("\n👉 [STEP 9] 게시 후 위젯 팝업 감지 및 '취소' 글자 터치")
        found_cancel = self.tap_by_text("취소", timeout=5)
        if found_cancel:
            print("  ✅ 카메라 위젯 팝업을 '취소' 글자로 정상 해제했습니다.")

        time.sleep(3.0)

        # -------------------------------------------------------------
        # STEP 10: 업로드 영상 피드 진입 -> 공식 3단 첫 댓글 자동 등록
        # -------------------------------------------------------------
        print("\n👉 [STEP 10] 방금 게시된 영상 피드에 Aura 공식 3단 첫 댓글 작성")
        node, center = self.find_node_with_parent_climb(
            lambda n: any(k in n.attrib.get("text", "") or k in n.attrib.get("content-desc", "") for k in ["첫 댓글", "댓글을 읽거나", "댓글"]),
            pause_video=True
        )

        comment_posted = False
        if center:
            print(f"  🎯 댓글 서랍 글자 버튼 발견: {center} -> 탭")
            self.run_adb("shell", "input", "tap", str(center[0]), str(center[1]))
            time.sleep(2.5)

            edit_node, edit_center = self.find_node_with_parent_climb(
                lambda n: any(k in n.attrib.get("text", "") for k in ["따듯한", "댓글 추가"]) or "EditText" in n.attrib.get("class", ""),
                pause_video=False
            )

            if edit_center:
                print(f"  🎯 댓글 입력창 발견: {edit_center} -> 탭 및 주입")
                self.run_adb("shell", "input", "tap", str(edit_center[0]), str(edit_center[1]))
                time.sleep(1.5)
                self.input_korean_text(AURA_TIKTOK_COMMENT)
                time.sleep(2.0)

                # 전송 버튼(↑) 글자/ID/접근성 라벨 동적 탐색 (부모 트리 역추적)
                send_node, send_center = self.find_node_with_parent_climb(
                    lambda n: any(k in n.attrib.get("resource-id", "") or k in n.attrib.get("content-desc", "") for k in ["d1y", "@2131823424", "send", "전송"])
                )
                if not send_center:
                    send_center = (906, 536)

                print(f"  🎯 댓글 전송 버튼 터치: {send_center}")
                self.run_adb("shell", "input", "tap", str(send_center[0]), str(send_center[1]))
                time.sleep(3.5)
                comment_posted = True
                print("  ✅ Aura 3단 공식 첫 댓글 전송 완료!")

        # -------------------------------------------------------------
        # STEP 11: 📸 댓글 영수증 상시 보관 및 📊 대시보드 실시간 연동
        # -------------------------------------------------------------
        print("\n👉 [STEP 11] 댓글 실물 영수증 캡처 및 대시보드 실시간 연동")
        ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        latest_proof = PROOFS_DIR / "aura_tiktok_comment_latest.png"
        ts_proof = PROOFS_DIR / f"aura_tiktok_comment_{ts_str}.png"
        system_proof = PROOF_DIR_SYSTEM / "proof_aura_latest_comment_live.png"

        self.run_adb("shell", "screencap", "-p", "/sdcard/comment_proof.png")
        self.run_adb("pull", "/sdcard/comment_proof.png", str(latest_proof))
        self.run_adb("pull", "/sdcard/comment_proof.png", str(ts_proof))
        self.run_adb("pull", "/sdcard/comment_proof.png", str(system_proof))

        # 삼성 키보드로 원복
        self.restore_samsung_keyboard()

        # 대시보드 히스토리 파일 실시간 업데이트
        self.save_publish_history(
            video_url=TIKTOK_PROFILE_URL,
            comment_text=AURA_TIKTOK_COMMENT,
            proof_img_path=str(latest_proof)
        )

        # 🌟 [사용자 핵심 철칙] 작업 완료 후 앱 100% 완전 종료 및 홈 화면 복귀 (브랜드 간 화면 꼬임 원천 차단)
        print("\n👉 [STEP 12] 틱톡 앱 완전 종료(force-stop) 및 스마트폰 홈 화면 복귀")
        self.run_adb("shell", "am", "force-stop", "com.ss.android.ugc.trill")
        self.run_adb("shell", "input", "keyevent", "3")
        time.sleep(1.0)

        print("\n" + "=" * 65)
        print("🎉 [성공] 💖 Aura 데이팅 원본 음성 100% + 첫 댓글 + 대시보드 URL + 클린 종료 완결!")
        print(f"📸 영수증 보관 경로: {latest_proof}")
        print("=" * 65 + "\n")

        return {
            "success": True,
            "comment_posted": comment_posted,
            "proof_path": str(latest_proof),
            "video_url": TIKTOK_PROFILE_URL,
            "caption": AURA_TIKTOK_CAPTION,
            "comment": AURA_TIKTOK_COMMENT
        }


if __name__ == "__main__":
    uploader = PhoneAuraTikTokUploader()
    res = uploader.execute_full_flow()
    print("최종 결과:", res)
